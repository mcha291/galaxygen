"""Systems: the star catalogue, headless (checkpoint 5).

**Nothing here rejects a sample it could have inverted** (rule B8). Every
positional draw is an inverse-CDF lookup against a density the model already
published: the radial mass distribution, the sech² vertical profile, the star
formation history at a radius. A rejection sampler would have been easier to
write and would have thrown away most of its draws, and its cost would have
depended on how peaked the galaxy happened to be.

**Per-region determinism, and how it is obtained.** The galaxy is divided into a
fixed grid of cells in (R, φ). A star's name is ``(cell, index)``. Since S61 (D220
part I) the sample is drawn **ring first**: a level-0 ring's count is one seeded
rounding of the ring's expectation on ``rng(systems_seed, "star", ring, "count")``,
every property of its stars is one array on ``rng(systems_seed, "star", ring,
property)`` - a star is element ``i`` of its ring's draw - and the layer only
allocates each star to a sector (at its own ``sector`` uniform) and an azimuth in
it; ``index`` is its rank among its ring's stars in that cell, in ring order. A
cell drawn alone draws its ring's count and uniforms whole and derives every
column for its own rows only. (Until S61 every cell drew its own count and its
own streams ``rng(systems_seed, "cell", cell, property)``, so the layer's
weights changed which stars existed.) Two consequences fall out, and they are
what the gate is about:

- **Order independence.** Nothing is drawn from a shared stream, so generating a
  region alone gives exactly what generating it inside a full sweep gives.
- **A smaller sample is a *prefix* of a larger one.** Each property has its own
  stream, so a ring's first stars at a smaller sample are its first stars at a
  larger one and land in the same cells, and a cell's rows at the smaller sample
  are the first of its rows at the larger — which is what makes the clickable
  sample of GALAXY_PLAN.md §4 stable while the LOD ladder materialises more
  underneath it.

That second property is the reason each property gets its own stream rather than
one stream per star. With a single stream, drawing radius-then-age for 10 stars
would leave it at a different position than for 1000, and the prefix would break.

**Arms and bar.** Azimuth is drawn from the pattern stage's density contrast
(``pattern.ArmPattern``): a sector's star count follows the contrast averaged over
that sector at the ring's radius, and a star's azimuth inside its sector inverts
the contrast at its own radius. The contrast averages to 1 around every ring, so
the radial distribution — and every radial row — is what it was. Its amplitudes
are derived means with seeded residuals since S26 (D175).

**Young stars in the azimuthal model** (S27). Where the model publishes
``sfr_modulation`` — where around each ring today's stars form — a star younger than
:data:`YOUNG_STAR_AGE` takes its azimuth from that instead, and a cell's share of young
stars follows the sector's modulation over its contrast (:class:`YoungStars`). The cell
counts are still the contrast's, so a star's name is the same whichever model drew it.
Since S59 (D218) the young stars' reader is not that table but the law it tabulates,
applied at the star's own point to the gas pattern's point function (:class:`Modulation`):
a table between two rings cannot serve the arms' frame and the bar's at once.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.cmaps import BLACKBODY_KELVIN
from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.chemistry import age_bin_edges, migration_width, transport_columns
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.feedback import star_bubble_radius
from galaxy.stages import gas_response as _cells  # the pattern's fixed cells round a ring: what the quadratures are counted in
from galaxy.stages.gas_pattern import CELLS as GAS_CELLS
from galaxy.stages.gas_pattern import GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS
from galaxy.stages.pattern import PATTERN_READS, invert_azimuths, ring_bracket, sector_grid
from galaxy.stages.pieces import ArmPattern
from galaxy.stages.sfh import star_formation_rate
from galaxy.stages.massive_stars import WR_CATEGORIES, ionizing_photons, wind_luminosity, wolf_rayet
from galaxy.stages.photometry import lookup as photometry
from galaxy.stages.photometry import lookup_columns
from galaxy.stages.remnants import REMNANT_CATEGORIES, classify as remnants_of
from galaxy.stages.vertical import POPULATIONS

# The cell grid is the unit of regional materialisation, and its size is a real
# trade-off measured at S5: every cell costs eight Generator constructions (~22 us
# each) on every run, whether or not anything asks for its stars, while a coarser
# grid makes a small region query materialise more stars than it needs and discard
# them. 32 x 32 puts the per-run cost at about 0.2 s for a 0.94 kpc by 11.25 degree
# cell. See debt #24 for the structural fix.
CELL_RINGS = 32
CELL_SECTORS = 32
CELL_COUNT = CELL_RINGS * CELL_SECTORS
# The cell hierarchy (S32, BUILD_II Phase 8, RENDER_PHYSICS section 5c): a level-k cell is one of 4^k
# children of a level-0 cell, 2^k sub-rings by 2^k sub-sectors, with its own seeded stream. Three
# levels deep: at level 3 a child at R0 is about 15 pc by 0.05 rad, 64 times the sample density.
MAX_LEVEL = 3


def children_per_cell(level: int) -> int:
    return 4 ** int(level)


def child_id(cell: int, level: int, q: int) -> int:
    """The id of child ``q`` (row-major over sub-rings then sub-sectors) of level-0 ``cell`` at ``level``."""
    return int(cell) * children_per_cell(level) + int(q)


def parent_of(cell_id: int, level: int) -> tuple[int, int]:
    """(level-0 cell, child index q) of a cell id at ``level``; at level 0 the id itself and 0."""
    n = children_per_cell(level)
    return int(cell_id) // n, int(cell_id) % n


def canonical_cell(level: int, cell_id: int) -> int:
    """One integer naming a cell at any level without collisions across levels: the level-0 ids
    come first, then every level-1 id, and so on. What the planets stage keys a star's draws on."""
    return int(cell_id) + sum(CELL_COUNT * children_per_cell(j) for j in range(int(level)))
CATALOGUE_SAMPLE = 20_000  # the clickable sample of GALAXY_PLAN.md §4, order 10^4-10^5

# Younger than this, a star is placed by where stars form today (``sfr_modulation``, published
# only by the azimuthal model) rather than by where the mass is (the density contrast). The number
# is the arm's lifetime, not a crossing time (S57, D216 item 12): the arms turn with the disc, so
# nothing crosses them, and a star stays in the arm it formed in until the arm itself dissolves -
# swing-amplified arms live 100-160 Myr [verified: Grand, Kawata & Cropper 2012, arXiv:1112.0019;
# Baba, Saitoh & Wada 2013, arXiv:1211.5401; docs/READING_GAS_SHOCK.md Part B rows A1, A3]. The
# value is the one BUILD_II.md Phase 2 stated without a source (as "about one arm crossing", gas
# mixing azimuthally on ~100 Myr), kept and re-sourced; it sits at the short end of the range. It is
# a cut, not a law: nothing in the model says how fast a young population leaves its arm, and a
# decaying weight would be a second constant with no source either.
YOUNG_STAR_AGE = 0.1  # Gyr

# The young stars' reader's two quadratures (S59, D218; rule A1: fixed counts). The star formation law's mean
# round a ring has no closed form (its switch is a hyperbolic tangent), so the reader's normaliser is the mean of
# equal steps round the ring, this many to each of the pattern's cells - 2880 in all; measured against a rule 32
# times finer on every ring inside the Milky Way template's bar at random alignments: 3e-4 of the mean at worst
# (1.2e-3 at one step a cell, 8e-5 at four, 2e-5 at eight). It is part of the reader's definition - the same
# number wherever the function is read - and what it leaves of a ring's mean the censuses divide out. A sector's
# mean, which sets a cell's expected count, is the function's integral: a Gauss rule on every piece of the sector
# on which the gas's contrast is linear (below).
RING_SAMPLES_PER_CELL = 2
# Gauss-Legendre points on each piece of a sector: two where the contrast is the arm profile's alone, which is
# smooth from cell to cell (1e-6 of a sector's mean against a rule of a million points round the ring), and six
# where a bar's footprint is in it - its edge is a ramp one cell wide on which the law's switch turns over, and
# two points leave 1e-2 of a finest sector's mean there, three 1e-3, four 2e-4, six 2e-6 (the reference's own).
GAUSS = {False: np.polynomial.legendre.leggauss(2), True: np.polynomial.legendre.leggauss(6)}  # (nodes, weights) on [-1, 1]
MEAN_CHUNK = 128  # rings whose mean is taken at once: a bound on memory (128 x 2880 doubles a temporary), not a count of work
# How many stars one placing call takes at once (S60, the cost): never a value's concern - a star's azimuth is the
# star's own - but the cost's: the pattern's exact ring means are made on arrays of (stars x chains) rows, and past a
# few thousand radii they leave the processor's cache and run at memory speed. Measured on 100 000 radii x 25
# azimuths: 17 241 radii a batch 6.9 s, 2 758 a batch 5.5 s, 1 379 a batch 6.1 s (the per-cell regime before S60,
# ~1 000 radii a call, 5.5 s). One cell's stars used to be one call; this is a few cells' worth.
PLACE_CHUNK = 4096
# What the young stars' reader reads beside the stellar pattern (S59, D218): the gas pattern's own reads, and the
# two ring fields and the index the star formation law is applied with.
YOUNG_READS: tuple[str, ...] = ("gas_surface_density", "sf_threshold_surface_density")
YOUNG_CONSTANTS: tuple[str, ...] = (*GAS_PATTERN_CONSTANTS, "KS_INDEX")

# Kroupa IMF: dN/dm proportional to m^-1.3 below the break and m^-2.3 above it
# [recall: Kroupa 2001]. GALAXY_INPUTS.md §2 makes the IMF a Level 0 constant.
IMF_MIN, IMF_BREAK, IMF_MAX = 0.08, 0.5, 150.0
IMF_LOW_SLOPE, IMF_HIGH_SLOPE = -1.3, -2.3


def _powerlaw_segment(lo: float, hi: float, slope: float) -> float:
    """∫ m^slope dm over [lo, hi]."""
    p = slope + 1.0
    return (hi**p - lo**p) / p


def imf_mean_mass() -> float:
    """Mass-weighted mean of the Kroupa IMF — what turns a stellar mass into a star count."""
    k_high = IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE)
    number = _powerlaw_segment(IMF_MIN, IMF_BREAK, IMF_LOW_SLOPE) + k_high * _powerlaw_segment(
        IMF_BREAK, IMF_MAX, IMF_HIGH_SLOPE
    )
    mass = _powerlaw_segment(IMF_MIN, IMF_BREAK, IMF_LOW_SLOPE + 1.0) + k_high * _powerlaw_segment(
        IMF_BREAK, IMF_MAX, IMF_HIGH_SLOPE + 1.0
    )
    return mass / number


def imf_sample(u: np.ndarray) -> np.ndarray:
    """Kroupa masses by inverse CDF — counted, not rejected (rule B8)."""
    k_high = IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE)
    n_low = _powerlaw_segment(IMF_MIN, IMF_BREAK, IMF_LOW_SLOPE)
    n_high = k_high * _powerlaw_segment(IMF_BREAK, IMF_MAX, IMF_HIGH_SLOPE)
    split = n_low / (n_low + n_high)

    def invert(frac: np.ndarray, lo: float, hi: float, slope: float) -> np.ndarray:
        p = slope + 1.0
        return (lo**p + frac * (hi**p - lo**p)) ** (1.0 / p)

    low = invert(np.clip(u / split, 0.0, 1.0), IMF_MIN, IMF_BREAK, IMF_LOW_SLOPE)
    high = invert(np.clip((u - split) / (1.0 - split), 0.0, 1.0), IMF_BREAK, IMF_MAX, IMF_HIGH_SLOPE)
    return np.where(u < split, low, high)


def invert_cdf(u: np.ndarray, x: np.ndarray, weight: np.ndarray) -> np.ndarray:
    """Draw from a tabulated density by inverting its CDF. Exact, vectorised, no rejection."""
    cdf = np.cumsum(weight)
    total = cdf[-1]
    if total <= 0.0:
        return np.full_like(np.asarray(u, dtype=float), x[0])
    return np.interp(np.asarray(u, dtype=float), cdf / total, x)


def invert_columns(u: np.ndarray, x: np.ndarray, cdf: np.ndarray, column: np.ndarray) -> np.ndarray:
    """:func:`invert_cdf` where each draw reads its own column of a shared table.

    ``cdf`` is ``(len(x), n_columns)``, already cumulative and normalised down each column, and
    ``column`` says which one each draw inverts. The search is a binary one across the draws at
    once — ``log2(len(x))`` passes over an array as long as the draws — rather than a comparison
    against the whole table, which would put ``len(x)`` work on every star and move the
    catalogue's cost onto the sample size (D24: the per-cell cost is what this design keeps
    fixed). Still an inversion, never a rejection (rule B8).
    """
    u = np.asarray(u, dtype=float)
    lo = np.zeros(u.size, dtype=np.intp)
    hi = np.full(u.size, len(x) - 1, dtype=np.intp)
    while True:
        mid = (lo + hi) // 2
        if not np.any(mid > lo) and not np.any(mid < hi):
            break
        below = cdf[mid, column] < u
        lo = np.where(below, np.minimum(mid + 1, hi), lo)
        hi = np.where(below, hi, mid)
    below = np.maximum(hi - 1, 0)
    c_hi, c_lo = cdf[hi, column], cdf[below, column]
    span = np.where(c_hi > c_lo, c_hi - c_lo, 1.0)
    return x[below] + np.clip((u - c_lo) / span, 0.0, 1.0) * (x[hi] - x[below])


def sech2_height(u: np.ndarray, scale: np.ndarray | float) -> np.ndarray:
    """Inverse CDF of the self-gravitating sheet: ρ ∝ sech²(z/2h), so z = 2h artanh(2u−1)."""
    return 2.0 * np.asarray(scale) * np.arctanh(np.clip(2.0 * np.asarray(u) - 1.0, -0.999999, 0.999999))


class Catalogue(dict):
    """A materialised set of stars: name -> column. A plain mapping, deliberately.

    ``counts`` carries the ``(cell, count)`` layout the rows were built from, which
    is how a row is named: row *r* is star ``index`` of ``cell``. Identity is not a
    column — it has no unit, no ramp and nothing to draw — so it travels beside the
    columns rather than inside them.

    ``ring_layout`` (S61, D220 part I) is where a census drawn ring-first put each row in its draw: the
    star sample's :class:`StarLayout`, the cloud census's ``clouds.RingLayout`` - each row's ring (or a
    level's sub-ring) and its place ``i`` in the ring's arrays, which a later draw keyed on the object
    (the planets, the clusters, the layer's texture) is indexed by. None on a catalogue assembled from
    pieces (the service's cell cache) or drawn otherwise. Not a column, for the same reason as ``counts``.
    """

    counts: tuple[tuple[int, int], ...] = ()
    ring_layout: Any = None

    @classmethod
    def of(cls, columns: Mapping[str, Any], counts: Sequence[tuple[int, int]] = (), ring_layout: Any = None) -> "Catalogue":
        made = cls(columns)
        made.counts = tuple((int(c), int(n)) for c, n in counts)
        made.ring_layout = ring_layout
        return made

    @property
    def size(self) -> int:
        return len(next(iter(self.values()))) if self else 0

    def star(self, row: int) -> tuple[int, int]:
        """The ``(cell, index)`` of one row — the name a system is opened by (§12)."""
        return star_at(self.counts, row)


def cell_edges(R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Ring edges in R and sector edges in φ: the footprint of every cell.

    The rings are the ones :func:`cell_masses` cuts, stated once here so that a
    caller asking "which cells cover this window" cannot answer it with a second,
    subtly different definition (rule A9 applied to geometry).
    """
    return np.linspace(R[0], R[-1], CELL_RINGS + 1), np.linspace(0.0, 2.0 * math.pi, CELL_SECTORS + 1)


def cell_bounds(R: np.ndarray, cell: int, level: int = 0) -> dict[str, float]:
    """The (R, phi) footprint of one cell - at ``level`` k, of one of a level-0 cell's 4^k children
    (2^k sub-rings by 2^k sub-sectors, row-major) - for a caller that has to draw it."""
    rings, sectors = cell_edges(R)
    parent, q = parent_of(cell, level)
    ring, sector = divmod(int(parent), CELL_SECTORS)
    n = 1 << int(level)
    a, b = divmod(int(q), n)
    r_lo, r_hi = rings[ring], rings[ring + 1]
    p_lo, p_hi = sectors[sector], sectors[sector + 1]
    return {
        "r_lo": float(r_lo + (r_hi - r_lo) * a / n), "r_hi": float(r_lo + (r_hi - r_lo) * (a + 1) / n),
        "phi_lo": float(p_lo + (p_hi - p_lo) * b / n), "phi_hi": float(p_lo + (p_hi - p_lo) * (b + 1) / n),
    }


def cells_in(
    R: np.ndarray, r_lo: float, r_hi: float, phi_lo: float = 0.0, phi_hi: float = 2.0 * math.pi, level: int = 0
) -> tuple[int, ...]:
    """Every cell whose footprint meets the window - at ``level`` k, every child (S32). phi wraps;
    the window may cross zero.

    A window narrower than a cell still selects the cell containing it, so a
    query never comes back empty because it was too small to straddle an edge.
    """
    rings, sectors = cell_edges(R)
    if r_hi < r_lo:
        r_lo, r_hi = r_hi, r_lo
    span = min(max(phi_hi - phi_lo, 0.0), 2.0 * math.pi)
    start = phi_lo % (2.0 * math.pi)
    windows = [(start, start + span)]
    if start + span > 2.0 * math.pi:  # the window crosses phi = 0 and is two intervals
        windows = [(start, 2.0 * math.pi), (0.0, start + span - 2.0 * math.pi)]

    def meets(lo: float, hi: float, a: float, b: float) -> bool:
        return lo < b and a < hi or (a == b and lo <= a <= hi) or (lo == hi and a <= lo <= b)

    want_rings = [i for i in range(CELL_RINGS) if meets(rings[i], rings[i + 1], r_lo, r_hi)]
    want_sectors = [
        j for j in range(CELL_SECTORS)
        if any(meets(sectors[j], sectors[j + 1], a, b) for a, b in windows)
    ]
    parents = tuple(i * CELL_SECTORS + j for i in want_rings for j in want_sectors)
    if not level:
        return parents
    out: list[int] = []
    for parent in parents:
        for q in range(children_per_cell(level)):
            cid = child_id(parent, level, q)
            bounds = cell_bounds(R, cid, level)
            if meets(bounds["r_lo"], bounds["r_hi"], r_lo, r_hi) and any(
                meets(bounds["phi_lo"], bounds["phi_hi"], a, b) for a, b in windows
            ):
                out.append(cid)
    return tuple(out)


def cell_masses(sigma_star: np.ndarray, R: np.ndarray, rings: int = CELL_RINGS) -> tuple[np.ndarray, np.ndarray]:
    """Mass per radial ring and the ring edges. The count is computed, never sampled."""
    edges = np.linspace(R[0], R[-1], rings + 1)  # cell_edges(R)[0] when rings is CELL_RINGS
    weight = sigma_star * PC_PER_KPC**2 * 2.0 * math.pi * R
    per_ring = np.array([
        float(np.trapezoid(np.where((R >= edges[i]) & (R <= edges[i + 1]), weight, 0.0), R))
        for i in range(rings)
    ])
    return per_ring, edges


def cell_shares(sigma_star: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Each ring's share of the stellar mass — what decides how many stars a cell gets."""
    ring_mass, _ = cell_masses(sigma_star, R)
    total = ring_mass.sum()
    return ring_mass / total if total > 0.0 else np.zeros_like(ring_mass)


def _sector_weights(R: np.ndarray, pattern: ArmPattern | None) -> np.ndarray:
    """Each ring's sector weights from the arm and bar contrast at the ring's middle; they
    average to 1, so a ring's total is unchanged. None or zero amplitudes: every sector alike."""
    rings, sectors = cell_edges(R)
    if pattern is None or pattern.flat:
        return np.ones((CELL_RINGS, CELL_SECTORS))
    return np.array([pattern.sector_means(0.5 * (rings[i] + rings[i + 1]), sectors) for i in range(CELL_RINGS)])


def cell_expected(
    sigma_star: np.ndarray, R: np.ndarray, n_stars: int, cell: int, pattern: ArmPattern | None = None
) -> float:
    """The expected number of stars in a level-0 cell at sample size ``n_stars``: the ring's share of
    the stellar mass, over the sectors, times the sector's contrast weight. A float; the realised
    count is how many of its ring's stars the allocation gives it (:func:`cell_counts`; S61, D220), and
    a child below level 0 draws its extra stars against this expectation (S32)."""
    share = cell_shares(sigma_star, R)
    weights = _sector_weights(R, pattern)
    ring, sector = divmod(int(cell), CELL_SECTORS)
    return float(n_stars * share[ring] / CELL_SECTORS * max(float(weights[ring, sector]), 0.0))


def star_at(counts: Sequence[tuple[int, int]], row: int) -> tuple[int, int]:
    """The ``(cell, index)`` of row ``row`` of a catalogue built from ``counts``."""
    seen = 0
    for cell, count in counts:
        if row < seen + count:
            return cell, row - seen
        seen += count
    raise IndexError(f"row {row} is past the {seen} stars these cells realise")


class Churn:
    """Where the stars now at each ring were born — the chemistry's migration kernel, backwards.

    The chemistry moves a star's abundance from where it formed to where it is now with a
    Gaussian of width ``migration_efficiency √(age / 8 Gyr)``, evaluated in age bins. Read
    forwards that says where a ring's stars went; the catalogue needs the opposite — given a
    star here now, where and when was it born — and that is not the kernel alone but the
    kernel weighted by how much mass each ring had to send (rule B8, and see
    ``chemistry.transport``). Both are precomputed once per materialisation: one kernel per
    age bin, and one arrival law per cell ring, so the cost does not scale with the stars.
    """

    __slots__ = ("R", "t", "arrive", "_born", "_cdf", "_bin", "_rings")

    def __init__(self, R: np.ndarray, t: np.ndarray, psi: np.ndarray, rings: np.ndarray, migration: float):
        """``rings`` are the grid indices of every cell ring — all of them, always: see the
        note at the call site for why this must not depend on which cells were asked for."""
        self.R, self.t = R, t
        # Mass born per ring per step, up to the constant factors that normalise away: the
        # ring's area is the part that does not, and dropping it would weight a birth radius
        # by surface density where the chemistry weights it by mass.
        self._born = np.asarray(psi, dtype=float) * R[:, None]
        self._rings = np.asarray(rings, dtype=int)
        edges = age_bin_edges(float(t[-1]))
        age = float(t[-1]) - t
        self._bin = np.clip(np.searchsorted(edges, age, side="right") - 1, 0, edges.size - 2)
        widths = migration_width(0.5 * (edges[1:] + edges[:-1]), migration)
        # K[bin][birth ring, cell ring]: only the cell rings are ever asked about, which is
        # what makes this 32 columns rather than a second grid-sized field.
        kcol = np.stack([transport_columns(R, float(w), self._rings) for w in widths])
        # The arrival law, per step: how much of what was born at each step is here now.
        # Per step and not per bin, because it is what a star's *age* is drawn from and the
        # bins are half a gigayear wide.
        self.arrive = np.zeros((t.size, self._rings.size))
        # Where it was born, per age bin: the kernel is a bin-level object — one width for
        # the whole bin — so the birth-radius distribution is read at that resolution too,
        # and the birth mass is summed over the bin to match it. Cumulative and normalised
        # here, once, so that drawing a star's birth radius is a search and not a sum.
        self._cdf = np.zeros((R.size, widths.size, self._rings.size))
        for b in range(widths.size):
            step = self._bin == b
            if not step.any():
                continue
            self.arrive[step] = self._born[:, step].T @ kcol[b]
            weight = self._born[:, step].sum(axis=1)[:, None] * kcol[b]
            cum = np.cumsum(weight, axis=0)
            total = cum[-1]
            self._cdf[:, b, :] = cum / np.where(total > 0.0, total, 1.0)

    def birth_radius(self, u: np.ndarray, ring: int, cols: np.ndarray) -> np.ndarray:
        """Birth radii for stars of one cell ring, each drawn from its own age bin's weights."""
        cdf = self._cdf[:, :, ring]
        drawn = invert_columns(u, self.R, cdf, self._bin[cols])
        # An age bin nothing was born in: the star stays where it is rather than being placed
        # at radius zero. ``ring`` numbers the cell rings, so the grid radius it stands for is
        # ``_rings[ring]`` — not ``R[ring]``, which is a different disc.
        empty = cdf[-1, self._bin[cols]] <= 0.0
        return np.where(empty, self.R[self._rings[ring]], drawn)


class Modulation:
    """Where stars form today around a ring, at a point: the young stars' reader (S27; exact since S59; on the gas
    pattern's one point function since S60).

    **The star formation law applied to the gas pattern's point function** (S59, D218, the gate's ruling on the
    reader: "a stored grid is not a field's definition; a reader that interpolates a table between rings is
    reading the grid"). The published ``sfr_modulation`` is the same law at the grid's cells: the viewer reads it,
    and no census does.

    The law is not linear, and what it reads beside the contrast - the ring's gas column and its threshold -
    exists on the grid rings and nowhere between them. So it is **applied with each bracketing grid ring's
    inputs to the one contrast the point has, and blended in R** (the second follow-up to D219's gate, item 3, in
    its own words): "The young stars' reader applies each bracketing grid ring's law to the gas pattern's point
    function at the point,

        M(r, φ) = (1 − a) Ψ_i(g(r, φ)) / ⟨Ψ_i(g(r, ·))⟩ + a Ψ_j(g(r, φ)) / ⟨Ψ_j(g(r, ·))⟩,

    the point function using the mid-gap rings of item 6; nothing ring-only is interpolated." Here i and j are the
    grid rings the radius r lies between and a its place between them (``pattern.ring_bracket``); g is the gas
    pattern's star-formation contrast at the point (``GasPattern.star_formation_contrast_at``: the response
    carried from the two *solved* rings the radius lies between - a mid-gap ring where the gap holds one - and
    the bar's footprint in the bar's frame); Ψ_k is the law ``sfh_azimuthal`` applies -
    ``sfh.star_formation_rate`` on Σ_gas,k · g with ring k's threshold and the law's index, the switch per point;
    and ⟨·⟩ is the mean round the ring at the point's own radius. Each ring's term is so a redistribution at
    every radius - its mean round the ring is 1 wherever it is read - and M's is 1. Not the column, not the
    threshold, not the normaliser is interpolated. A ring that forms nothing anywhere reads 1, as the published
    field does. At a grid radius M is that ring's own law of the pattern's contrast there.

    (From S59 to the second pass of S60 the reader applied each grid ring's law to *that ring's own* contrast as
    the point saw it, so its two terms were laws of two different contrasts and the pattern's own blend - and,
    since S60's third pass, its mid-gap rings - never reached the young stars.)

    **The mean round the ring is a quadrature** (the law's switch is a hyperbolic tangent; there is no closed
    form): :data:`RING_SAMPLES_PER_CELL` equal steps to each of the pattern's cells round the ring, of the point
    function at the point's own radius. It is the reader's normaliser by definition, one number per ring's law
    wherever the function is read; its accuracy against a rule 32 times finer is pinned in
    ``tests/test_pieces.py``. Where the contrast is one number round the ring (``GasPattern.uniform_at``: no
    solved ring the radius reads is forced, the footprint uniform) the mean is the law of that number, and is not
    sampled.

    **One point function behind every entry point.** :meth:`at` and :meth:`at_points` are it; :meth:`azimuths`
    is its inverse CDF; :meth:`sector_means_at` is its integral over a sector: between two neighbouring breaks
    (``GasPattern.star_formation_kinks``) each piece takes a Gauss rule. Sectors that tile a ring average to the
    ring's mean of the function: 1 to the normaliser's accuracy.

    ``pattern`` is the gas pattern of the same run, from ``compose.gas_pattern``; None, or a flat one (a pitch
    the mesh could not resolve), is no pattern at all: the law of a uniform ring, 1 everywhere. ``gas`` and
    ``threshold`` are the published ``gas_surface_density`` and ``sf_threshold_surface_density`` on the grid
    radii ``R``, and ``index`` the law's.
    """

    __slots__ = ("pattern", "R", "gas", "threshold", "index")

    def __init__(self, pattern: Any, R: np.ndarray, gas: np.ndarray, threshold: np.ndarray, index: float) -> None:
        self.pattern = None if pattern is None or pattern.flat else pattern
        self.R = np.asarray(R, dtype=float)
        self.gas = np.asarray(gas, dtype=float)
        self.threshold = np.asarray(threshold, dtype=float)
        self.index = float(index)
        if self.gas.shape != self.R.shape or self.threshold.shape != self.R.shape:
            raise ValueError(f"the law reads the gas column and the threshold on the {self.R.size} grid radii; got {self.gas.shape} and {self.threshold.shape}")

    def _law(self, ring: np.ndarray, contrast: np.ndarray) -> np.ndarray:
        """Ψ_ring on a contrast shaped (rings, k): ``sfh_azimuthal``'s own arithmetic, the law's normalisation
        left at 1 (it divides out)."""
        return star_formation_rate(self.gas[ring][:, None] * np.maximum(contrast, 0.0), 1.0, self.index, self.threshold[ring][:, None])

    def _means(self, r: np.ndarray, lower: np.ndarray, upper: np.ndarray, per_cell: int = RING_SAMPLES_PER_CELL) -> tuple[np.ndarray, np.ndarray]:
        """(⟨Ψ_lower(g(r, ·))⟩, ⟨Ψ_upper(g(r, ·))⟩) for each radius: the two grid rings' laws of the pattern's
        point function round the ring at the radius itself - ``per_cell`` equal steps to each of the pattern's
        cells, a fixed number of radii at a time; one sample where the contrast is one number round the ring."""
        low, high = np.empty(r.shape), np.empty(r.shape)
        even = self.pattern.uniform_at(r)
        if even.any():
            level = self.pattern.star_formation_contrast_at(r[even, None], np.zeros((1, 1)))
            low[even], high[even] = self._law(lower[even], level)[:, 0], self._law(upper[even], level)[:, 0]
        rows = np.flatnonzero(~even)
        steps = GAS_CELLS * int(per_cell)
        phi = -math.pi + (np.arange(steps) + 0.5) * (2.0 * math.pi / steps)
        for start in range(0, rows.size, MEAN_CHUNK):
            part = rows[start:start + MEAN_CHUNK]
            contrast = self.pattern.star_formation_contrast_at(r[part, None], phi[None, :])
            low[part], high[part] = self._law(lower[part], contrast).mean(axis=1), self._law(upper[part], contrast).mean(axis=1)
        return low, high

    def at_points(self, r: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The modulation at each radius ``r`` (n,) and that row's own azimuths ``phi`` (n, k): the point
        function (S48: a bright star inverts its own row inside its own cell)."""
        r = np.atleast_1d(np.asarray(r, dtype=float))
        phi = np.asarray(phi, dtype=float)
        if phi.ndim != 2 or phi.shape[0] != r.size:
            raise ValueError(f"each of the {r.size} radii reads its own row of azimuths; got azimuths shaped {phi.shape}")
        if self.pattern is None:
            return np.ones(phi.shape)
        lower, upper, share = ring_bracket(self.R, r)
        contrast = self.pattern.star_formation_contrast_at(r[:, None], phi)
        mean_low, mean_high = self._means(r, lower, upper)

        def term(ring: np.ndarray, mean: np.ndarray) -> np.ndarray:
            forms = mean > 0.0
            return np.where(forms[:, None], self._law(ring, contrast) / np.where(forms, mean, 1.0)[:, None], 1.0)

        return term(lower, mean_low) * (1.0 - share)[:, None] + term(upper, mean_high) * share[:, None]

    def at(self, r: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The modulation at each radius ``r`` (one row each) and every azimuth ``phi``: :meth:`at_points` on
        the mesh."""
        r = np.atleast_1d(np.asarray(r, dtype=float))
        phi = np.asarray(phi, dtype=float)
        return self.at_points(r, np.broadcast_to(phi[None, :], (r.size, phi.size)))

    def sector_means_at(self, r: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """The modulation averaged over each sector between ``edges`` (ascending, spanning a turn at most) at
        each radius of ``r``, shaped (radii, sectors): the point function's integral over the sector, over the
        sector's width. The integral is taken piece by piece between the sectors' edges and the breaks
        ``GasPattern.star_formation_kinks`` gives - the cells' centres of the arm profile, the anchors of the map
        that carries it, and inside a bar's body the footprint's cells - with a Gauss rule on each piece
        (:data:`GAUSS`: two points, and six where a bar's footprint is in the contrast); the count is the
        geometry's (rule A1). Measured in ``tests/test_pieces.py`` against a fine rule round the ring. A row is
        the same numbers whichever radii are asked with it."""
        r = np.atleast_1d(np.asarray(r, dtype=float))
        edges = np.asarray(edges, dtype=float)
        width = np.diff(edges)
        if self.pattern is None:
            return np.ones((r.size, width.size))
        plain = self.pattern.footprint_uniform_at(r)  # no ring read here holds a footprint that is not uniform
        out = np.empty((r.size, width.size))
        for rows, bar in ((np.flatnonzero(plain), False), (np.flatnonzero(~plain), True)):
            if rows.size:
                out[rows] = self._sector_integrals(r[rows], edges, bar) / width[None, :]
        return out

    def _sector_integrals(self, r: np.ndarray, edges: np.ndarray, bar: bool) -> np.ndarray:
        """∫ M(r, φ) dφ over each sector between ``edges``, for each radius: a Gauss rule on every piece between
        neighbouring breaks - the sectors' edges and the contrast's kinks, each kink taken at its turn inside the
        sectors' span."""
        span_lo, span_hi = edges[0], edges[-1]
        kinks = self.pattern.star_formation_kinks(r, bar)
        kinks = np.minimum(span_lo + np.mod(kinks - span_lo, 2.0 * math.pi), span_hi)
        breaks = np.concatenate([np.broadcast_to(edges[None, :], (r.size, edges.size)), kinks], axis=1)
        order = np.argsort(breaks, axis=1, kind="stable")  # an edge before a kink that falls on it
        breaks = np.take_along_axis(breaks, order, axis=1)
        place = np.empty_like(order)
        np.put_along_axis(place, order, np.broadcast_to(np.arange(order.shape[1])[None, :], order.shape), axis=1)
        half, middle = 0.5 * (breaks[:, 1:] - breaks[:, :-1]), 0.5 * (breaks[:, 1:] + breaks[:, :-1])
        pieces = half.shape[1]
        nodes, weights = GAUSS[bool(bar)]
        values = self.at_points(r, np.concatenate([middle + node * half for node in nodes], axis=1))
        weighed = sum(weight * values[:, k * pieces:(k + 1) * pieces] for k, weight in enumerate(weights))
        running = np.concatenate([np.zeros((r.size, 1)), np.cumsum(half * weighed, axis=1)], axis=1)
        at_edges = place[:, : edges.size]
        return np.take_along_axis(running, at_edges[:, 1:], axis=1) - np.take_along_axis(running, at_edges[:, :-1], axis=1)

    def sector_means(self, r: float, edges: np.ndarray) -> np.ndarray:
        """The modulation averaged over each sector between ``edges`` at one radius: :meth:`sector_means_at`'s row."""
        return self.sector_means_at(np.array([float(r)]), edges)[0]

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: np.ndarray | float, hi: np.ndarray | float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the modulation at each star's own radius (rule B8). ``lo`` and
        ``hi`` are one sector's, or since S60 one sector a star (stars,) - :func:`sector_grid` - the stars of
        many cells placed in one call, each as its own cell's call placed it."""
        grid = sector_grid(lo, hi, steps)
        if grid.ndim == 1:
            return invert_azimuths(u, grid, self.at(radius, grid))
        return invert_azimuths(u, grid, self.at_points(radius, grid))


def young_reader(fields: Mapping[str, Any], R: np.ndarray, constants: Mapping[str, Any] | None) -> Modulation | None:
    """The young stars' reader of a run's fields, or None where the stars are placed by no modulation: the layer
    off, or a model that publishes none (``basic``). Whether the model publishes one is asked of ``compose``, as
    a census asks for any placement weight; **the table's values are not read** - the reader is the law the
    table holds at the cells, applied to the gas pattern compose gives (S59, D218).

    ``constants`` are the model's: the gas pattern's (its sound speed, G, the lanes' numbers) and the law's
    index. A catalogue of a model that publishes a modulation cannot be placed without them, and says so - with
    none given, and with one of the gas pattern's missing (a pattern that is there and flat is the law of a
    uniform ring, 1 everywhere; a pattern that cannot be built is an error, never 1)."""
    if _compose.placement_weight(fields, "sfr_modulation") is None:
        return None
    if constants is None:
        raise TypeError(
            "this model publishes sfr_modulation: its young stars are placed by the star formation law at a point, "
            "which reads the model's constants (the gas pattern's and KS_INDEX) - pass constants="
        )
    pattern = _compose.gas_pattern(fields, R, constants)
    if pattern is None:
        # A reader that cannot be built raises; it never falls back to another, or to 1 (D218, the third follow-up).
        missing = [n for n in GAS_PATTERN_READS if n not in fields] + [k for k in GAS_PATTERN_CONSTANTS if k not in constants]
        raise KeyError(
            "this model publishes sfr_modulation, and its young stars are placed by the star formation law on the gas "
            f"pattern, which cannot be built here: missing {', '.join(missing) or 'nothing it names'}"
        )
    return Modulation(pattern, R, fields["gas_surface_density"], fields["sf_threshold_surface_density"], float(constants["KS_INDEX"]))


class YoungStars:
    """The azimuthal model's split of each cell into young stars and the rest (S27). Since S61 the split is the
    allocation's (:class:`Placement`): a star's age is its ring's (or sub-ring's) draw and its sector follows from
    it; until S61 ``age_weights`` tilted each cell's age law toward its young share instead.

    A cell's expected star count stays the density contrast's — the stellar mass is where the
    contrast puts it. (Until S61 its realised count was too, and a star's name ``(cell, index)``
    did not depend on which model drew the layout; drawn ring-first, a ring's stars are the same
    in both models and the young ones are allocated by the modulation, so a star keeps its
    identity in the ring's draw and may stand in another cell.) What moves is *which* of a
    cell's stars are young. A ring whose arrival law holds a share
    ``y`` of stars younger than :data:`YOUNG_STAR_AGE` gives each of its sectors a young share
    ``y · m̄ / c̄`` — the sector's mean modulation over its mean contrast — so the ring's young
    stars are spread over its sectors as the modulation is, the ring's total young share is
    still ``y``, and the older stars take up the difference: the total stays the contrast.
    Every table here covers every ring and sector, whatever a request asked for (D60).
    """

    __slots__ = ("modulation", "young_step", "born_after", "share", "p")  # S61: young_step is read by nothing but the split

    def __init__(
        self,
        modulation: Modulation,
        pattern: ArmPattern | None,
        arrive: np.ndarray,
        t: np.ndarray,
        rings: np.ndarray,
        sectors: np.ndarray,
    ) -> None:
        self.modulation = modulation
        self.young_step = (t[-1] - t) < YOUNG_STAR_AGE
        first = int(np.argmax(self.young_step)) if self.young_step.any() else t.size
        # invert_cdf gives step k's weight to the interval ending at t[k], so a star born after
        # t[first - 1] was drawn from the young steps' weights, and it is young by that token.
        self.born_after = float(t[first - 1]) if first > 0 else -math.inf
        total = arrive.sum(axis=0)
        young = arrive[self.young_step].sum(axis=0)
        self.share = np.where(total > 0.0, young / np.where(total > 0.0, total, 1.0), 0.0)
        mids = 0.5 * (rings[:-1] + rings[1:])
        mod = modulation.sector_means_at(mids, sectors)
        ring_mean = mod.mean(axis=1, keepdims=True)
        mod = np.where(ring_mean > 0.0, mod / np.where(ring_mean > 0.0, ring_mean, 1.0), 1.0)
        con = (
            np.ones_like(mod)
            if pattern is None or pattern.flat
            else np.array([pattern.sector_means(float(r), sectors) for r in mids])
        )
        ratio = np.where(con > 0.0, mod / np.where(con > 0.0, con, 1.0), 1.0)
        self.p = np.clip(self.share[:, None] * ratio, 0.0, 1.0)

    def is_young(self, born: np.ndarray) -> np.ndarray:
        return born > self.born_after


# --- the ring-first draw (S61, D220 part I) ----------------------------------

# The per-star streams of a ring's draw, each an array of the ring's count (D220 item 1). The names are the ones the
# cells' streams had until S61; ``sector`` (the allocation's uniform) and ``count`` (the ring's seeded rounding) are
# the ring's own.
STAR_STREAMS: tuple[str, ...] = ("radius", "age", "azimuth", "birth_radius", "height", "mass")


def star_stream(seed: int, ring: int, name: str, level: int = 0) -> np.random.Generator:
    """The stream ``name`` of one level-0 ring's draw of the star sample, ``(seed, "star", ring, name)`` (S61, D220
    item 1). A star's identity in the draw is ``(ring, i)``: it is element ``i`` of every array drawn on these
    streams. ``level`` k names the hierarchy's sub-ring streams, ``(seed, "star", "level", k, sub_ring, name)``: a
    level-k child's own stars are its sub-ring's draw, allocated among the sub-ring's children (S61, D220 item 8)."""
    if not level:
        return _seeds.rng(seed, "star", int(ring), name)
    return _seeds.rng(seed, "star", "level", int(level), int(ring), name)


def ring_star_expected(sigma_star: np.ndarray, R: np.ndarray, n_stars: int) -> np.ndarray:
    """The expected number of the sample's stars in every level-0 ring, (rings,): ``n_stars`` times the ring's share of
    the stellar mass. No placement enters it, so it is the same number with the layer on or off; it is the sum of the
    ring's cell expectations (:func:`cell_expected`) to rounding (invariant I2; measured at S61, see
    ``tests/test_layer.py``). A ring's count is its seeded rounding (:func:`ring_star_count`)."""
    return float(n_stars) * cell_shares(sigma_star, R)


def ring_star_count(seed: int, ring: int, expected: float, level: int = 0) -> int:
    """A ring's star count: the expectation's whole part plus one seeded Bernoulli on its fractional part, drawn on
    the ring's stream ``(seed, "star", ring, "count")`` - the census's own rule (rather than a rounding rule, which
    would bias the disc's outskirts away), applied once per ring since S61 (D220 item 1) and once per cell before.
    At ``level`` k, ``ring`` is a sub-ring and the stream its own, ``(seed, "star", "level", k, sub_ring, "count")``."""
    base = int(expected)
    return base + int(star_stream(seed, ring, "count", level).random() < expected - base)


def sub_ring_expected(sigma_star: np.ndarray, R: np.ndarray, n_stars: int, level: int) -> np.ndarray:
    """The expected number of a level-k sub-ring's own stars, per level-0 ring (rings,) - the same for each of the
    ring's 2^k sub-rings: ``2^k (1 − 4^−k) n_stars share`` (S61, D220 item 8). Each of the sub-ring's 32·2^k children
    holds a level-k sample 4^k times as dense as level 0's, of which its parent's stars supply 4^−k: summed round the
    sub-ring that is ``2^k (1 − 4^−k)`` times the ring's level-0 expectation. No placement enters it."""
    k = int(level)
    return float(1 << k) * (1.0 - 4.0 ** -k) * ring_star_expected(sigma_star, R, n_stars)


@dataclass(frozen=True)
class StarLayout:
    """Where the ring-first draw put the rows of a star catalogue (S61, D220 items 1-2).

    ``counts`` is the catalogue's ``(cell, count)`` layout - the cells in the order asked, those that realise no star
    left out - and row by row ``level``, ``ring`` and ``index`` are the star's identity in its draw: a level-0 star is
    element ``index`` of its ``ring``'s arrays (:func:`star_stream`); below level 0 a child's own star is ``(level,
    sub-ring, index in the sub-ring's draw)``. ``sizes`` holds each drawn ring's count, the length of its arrays -
    keyed by the level-0 ring, and by ``(level, sub-ring)`` below. A row's name stays ``(cell, index in the cell)``
    (D190); this is what a draw keyed on the star - its planets - is indexed by, so that draw does not depend on where
    the layer put it."""

    counts: tuple[tuple[int, int], ...]
    level: np.ndarray
    ring: np.ndarray
    index: np.ndarray
    sizes: Mapping[Any, int]

    def take(self, keep: np.ndarray, counts: Sequence[tuple[int, int]]) -> "StarLayout":
        """The layout of the rows ``keep`` selects, laid out as ``counts``."""
        return StarLayout(tuple((int(c), int(n)) for c, n in counts), self.level[keep], self.ring[keep], self.index[keep], self.sizes)


def star_layout_of(catalogue: Catalogue) -> StarLayout:
    """The :class:`StarLayout` a star catalogue drawn by :func:`materialise` carries (``Catalogue.ring_layout``)."""
    layout = getattr(catalogue, "ring_layout", None)
    if not isinstance(layout, StarLayout):
        raise ValueError("this catalogue carries no star layout: materialise it with systems.materialise")
    return layout


def select(catalogue: Catalogue, keep: np.ndarray, counts: Sequence[tuple[int, int]], drop: Sequence[str] = ()) -> Catalogue:
    """The rows ``keep`` of a star catalogue, laid out as ``counts``, its columns but ``drop``, and its
    :class:`StarLayout` taken with them - what a caller that narrows a catalogue (``/api/system`` below level 0)
    hands on, so the rows it keeps are still named in their draw."""
    layout = getattr(catalogue, "ring_layout", None)
    columns = {n: np.asarray(v)[keep] for n, v in catalogue.items() if n not in drop}
    return Catalogue.of(columns, counts, layout.take(keep, counts) if isinstance(layout, StarLayout) else None)


class Placement:
    """What places a run's stars round their rings, made once a materialisation and over every ring and sector
    whatever a request asked for (D60): the stellar pattern from compose, the churn's arrival law, the young stars'
    split and the sector weights each part is allocated by (S61, D220 item 2).

    *The allocation.* A star's sector is the inverse of its ring's cumulative sector weights at its own ``sector``
    uniform (``clouds.allocate``). With no modulation the weights are the pattern's sector means (``_sector_weights``,
    clipped at 0), or none - every sector alike - with the layer off. Where the model publishes ``sfr_modulation``
    and the layer is on, the weights are the two the catalogue has read per cell since S27 (:class:`YoungStars`),
    taken apart: a star younger than :data:`YOUNG_STAR_AGE` by its age - drawn from the ring's arrival law, the same
    on and off - is allocated by the sector's contrast times its young share, ``c̄ p``, and an older one by
    ``c̄ (1 − p)``. A sector so expects the young and the old stars it expected when each cell tilted its own age law
    (until S61): ``p`` is the young share ``y m̄ / c̄``, so the young weights are ``y m̄`` and sum round the ring to the
    ring's young share wherever no sector's share is clipped at 0 or 1, and the cell's total is the contrast's. The
    layer assigns the sector - and the azimuth within it - and nothing else (item 4)."""

    __slots__ = ("pattern", "churn", "young", "edges", "ring_index", "contrast", "old", "fresh", "t")

    def __init__(self, fields: Mapping[str, Any], R: np.ndarray, t: np.ndarray, *, migration: float,
                 constants: Mapping[str, Any] | None) -> None:
        _, edges = cell_masses(fields["stellar_surface_density"], R)
        self.edges, self.t = edges, t
        # The radius that stands for a ring, computed from the density field rather than
        # from the stars a cell happens to realise. Using the realised mean would make a
        # cell's ages depend on how many stars were asked for, which silently broke the
        # prefix property until a test caught it.
        weights = fields["stellar_surface_density"] * R
        ring_radius = np.array([
            float(np.average(R, weights=np.where((R >= edges[i]) & (R <= edges[i + 1]), weights, 0.0)))
            if np.any((R >= edges[i]) & (R <= edges[i + 1]) & (weights > 0.0))
            else 0.5 * (edges[i] + edges[i + 1])
            for i in range(CELL_RINGS)
        ])
        self.ring_index = np.array([int(np.argmin(np.abs(R - r))) for r in ring_radius])
        # The pattern the catalogue places by, from compose (S55, D214): none with the layer off, and then every
        # sector of a ring is alike and a star's azimuth is uniform in its sector - the arithmetic of no pattern.
        self.pattern = _compose.stellar_pattern(fields, R)
        # Every cell ring, whichever cells were asked for. Narrowing it to the rings a region
        # query touches was tried and reverted: the arrival law is a matrix product over the
        # rings, and BLAS sums a 1-column product in a different order than a 32-column one, so
        # a region came back with a star one bit from the sweep's. Per-region determinism is
        # this stage's whole contract (D60), and arithmetic that depends on what was asked for
        # is the one thing it cannot have. Affordable because the kernel is read by column now.
        self.churn = Churn(R, t, fields["sfr_surface_density_history"], self.ring_index, migration)
        # Where stars form today, when the model publishes it (the azimuthal model, S27): read
        # optionally, so the same stage draws both models' catalogues, and tabulated over every
        # ring and sector for the same reason the arrival law is (D60). A composed weight, so it comes from
        # compose (S55): none with the layer off, and the catalogue is drawn as a model without the field draws it.
        # Since S59 (D218, the gate's ruling) the young stars' reader is not the table: it is the star formation law
        # applied to the gas pattern's point function, ring by ring (:class:`Modulation`). The table says only that
        # the model has such a law.
        reader = young_reader(fields, R, constants)
        self.young = None if reader is None else YoungStars(reader, self.pattern, self.churn.arrive, t, edges, cell_edges(R)[1])
        flat = self.pattern is None or self.pattern.flat
        self.contrast = None if flat else np.maximum(_sector_weights(R, self.pattern), 0.0)
        if self.young is None:
            self.old = self.fresh = self.contrast
        else:
            c = np.ones((CELL_RINGS, CELL_SECTORS)) if self.contrast is None else self.contrast
            self.fresh, self.old = c * self.young.p, c * (1.0 - self.young.p)

    def born(self, u_age: np.ndarray, ring: int) -> np.ndarray:
        """Birth times at ``u_age`` from the ring's arrival law: of the stars *here now*, the migration kernel's law
        rather than the local birth rate. The same law on and off since S61 (the layer no longer tilts a cell's)."""
        return invert_cdf(u_age, self.t, self.churn.arrive[:, int(ring)])

    def sectors(self, ring: int, u_sector: np.ndarray, born: np.ndarray | None) -> np.ndarray:
        """Each of a ring's stars' sector (D220 item 2). ``born`` (every star of the ring's) is read only where the
        young stars are allocated apart."""
        if self.young is None:
            return self.allocate(u_sector, born, None if self.old is None else self.old[ring], None)
        return self.allocate(u_sector, born, self.old[ring], self.fresh[ring])

    def allocate(self, u_sector: np.ndarray, born: np.ndarray | None, old: np.ndarray | None,
                 fresh: np.ndarray | None) -> np.ndarray:
        """Each star's place among ``len(old)`` sectors (``CELL_SECTORS`` when the weights are None): the old stars by
        ``old``, the young ones (born after :data:`YOUNG_STAR_AGE` ago, read where the model publishes a modulation) by
        ``fresh``."""
        from galaxy.stages.clouds import allocate  # one allocation law for every census; clouds imports this module

        if self.young is None:
            return allocate(u_sector, old)
        assert born is not None and old is not None and fresh is not None
        young = self.young.is_young(born)
        out = np.empty(u_sector.size, dtype=np.int64)
        out[young] = _allocate_among(u_sector[young], fresh)
        out[~young] = _allocate_among(u_sector[~young], old)
        return out

    def sub_ring_weights(self, level: int, sub_ring: int) -> tuple[np.ndarray | None, np.ndarray | None]:
        """``(old, fresh)``: the parts' weights on a level-k sub-ring's 32·2^k children (D220 item 8) - the rule of
        level 0 evaluated on the children at the sub-ring's middle radius: the pattern's exact sector means ``c̄`` over
        the children's sub-sectors and, where the model publishes a modulation, the modulation's ``m̄`` normalised to
        its mean round the sub-ring and the ring's young share ``y``: ``c̄ (1 − p)`` and ``c̄ p`` with ``p = clip(y m̄ /
        c̄)``. ``(None, None)`` where every child of the sub-ring weighs the same (the layer off)."""
        n = 1 << int(level)
        r, a = divmod(int(sub_ring), n)
        lo, hi = float(self.edges[r]), float(self.edges[r + 1])
        mid = lo + (hi - lo) * (a + 0.5) / n
        edges = np.linspace(0.0, 2.0 * math.pi, CELL_SECTORS * n + 1)
        con = None if self.pattern is None or self.pattern.flat else np.asarray(self.pattern.sector_means(mid, edges), dtype=float)
        if self.young is None:
            return (None if con is None else np.maximum(con, 0.0)), None
        mod = np.asarray(self.young.modulation.sector_means_at(np.array([mid]), edges)[0], dtype=float)
        mean = float(mod.mean())
        mod = mod / mean if mean > 0.0 else np.ones_like(mod)
        c = np.ones_like(mod) if con is None else con
        ratio = np.where(c > 0.0, mod / np.where(c > 0.0, c, 1.0), 1.0)
        p = np.clip(float(self.young.share[r]) * ratio, 0.0, 1.0)
        c = np.maximum(c, 0.0)
        return c * (1.0 - p), c * p


def _allocate_among(u: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """``clouds.allocate``'s law over ``len(weights)`` sectors (it is fixed at a level-0 ring's 32): the inverse of the
    cumulative weights at each uniform, uniform where they sum to nothing."""
    u = np.asarray(u, dtype=float)
    k = int(np.asarray(weights).size)
    if not float(np.sum(weights)) > 0.0:
        return np.minimum((u * k).astype(np.int64), k - 1)
    cdf = np.cumsum(np.asarray(weights, dtype=float))
    return np.minimum(np.searchsorted(cdf / cdf[-1], u, side="right"), k - 1).astype(np.int64)


def _layout(place: Placement, sigma_star: np.ndarray, R: np.ndarray, seed: int, n_stars: int,
            cells: Sequence[int]) -> tuple[StarLayout, dict[int, dict[str, np.ndarray]]]:
    """The level-0 layout of ``cells`` and the uniforms drawn to make it, per touched ring (D220 items 1-3): each ring
    the cells lie in has its count and its ``sector`` uniforms drawn whole (and its ``age`` uniforms, where the young
    stars are allocated apart), and each cell's rows are the ring's stars allocated to it, in ring order."""
    expected = ring_star_expected(sigma_star, R, n_stars)
    wanted = [int(c) for c in cells]
    drawn: dict[int, dict[str, np.ndarray]] = {}
    sector: dict[int, np.ndarray] = {}
    for r in dict.fromkeys(c // CELL_SECTORS for c in wanted):
        n = ring_star_count(seed, r, float(expected[r]))
        here = {"sector": star_stream(seed, r, "sector").random(n)}
        born = None
        if place.young is not None:
            here["age"] = star_stream(seed, r, "age").random(n)
            born = place.born(here["age"], r)
        drawn[r] = here
        sector[r] = place.sectors(r, here["sector"], born)
    counts: list[tuple[int, int]] = []
    ring: list[np.ndarray] = []
    index: list[np.ndarray] = []
    for cell in wanted:
        r, s = divmod(cell, CELL_SECTORS)
        rows = np.flatnonzero(sector[r] == s)
        if rows.size:
            counts.append((cell, int(rows.size)))
            ring.append(np.full(rows.size, r, dtype=np.int64))
            index.append(rows.astype(np.int64))
    join = lambda parts: np.concatenate(parts) if parts else np.zeros(0, dtype=np.int64)  # noqa: E731
    ring_ = join(ring)
    return StarLayout(tuple(counts), np.zeros(ring_.size, dtype=np.int64), ring_, join(index),
                      {r: v["sector"].size for r, v in drawn.items()}), drawn


def star_layout(fields: Mapping[str, Any], R: np.ndarray, t: np.ndarray, seed: int, n_stars: int,
                cells: Sequence[int] | None = None, *, migration: float, constants: Mapping[str, Any] | None = None) -> StarLayout:
    """The level-0 :class:`StarLayout` of ``cells`` (every cell when None) - which star of which ring each row is,
    and the ``(cell, count)`` layout that names the rows - without materialising a star (S61, D220).

    Split out of :func:`materialise` because a star's *identity* is ``(cell, index)`` (D60) and more than one caller
    needs it: a later stage keying its own draws on a star (the planets), and an API mapping a row back to the star it
    came from. Recomputing the layout somewhere else would be a second definition of which star is which. It reads
    what the allocation reads: the arrival law and the young stars' reader where the model publishes a modulation."""
    place = Placement(fields, R, t, migration=migration, constants=constants)
    return _layout(place, fields["stellar_surface_density"], R, seed, n_stars, range(CELL_COUNT) if cells is None else cells)[0]


def cell_counts(fields: Mapping[str, Any], R: np.ndarray, t: np.ndarray, seed: int, n_stars: int,
                cells: Sequence[int] | None = None, *, migration: float, constants: Mapping[str, Any] | None = None) -> tuple[tuple[int, int], ...]:
    """``(cell, count)`` for every cell that realises a star, in the order asked: :func:`star_layout`'s counts. Since
    S61 (D220) a cell's count is how many of its ring's stars the allocation gives it, no longer a draw of its own."""
    return star_layout(fields, R, t, seed, n_stars, cells, migration=migration, constants=constants).counts


def materialise(
    fields: Mapping[str, Any],
    R: np.ndarray,
    t: np.ndarray,
    seed: int,
    n_stars: int,
    cells: Sequence[int] | None = None,
    *,
    migration: float,
    level: int = 0,
    constants: Mapping[str, Any] | None = None,
) -> Catalogue:
    """Generate ``n_stars`` across the whole galaxy, or only within ``cells``.

    Passing a subset of cells returns exactly the stars those cells would have in
    a full sweep — that is the per-region determinism the gate is about.

    ``migration`` is the ``migration_efficiency`` input and is keyword-only and required
    on purpose: it is the one argument here that is not a published field, and a default
    of zero would have made a caller that forgot it silently produce the unmigrated
    catalogue of debt #31 — the defect this signature exists to make unreachable (rule B13).

    ``constants`` (S59, D218) are the model's constants, which the young stars' reader needs
    where the model publishes ``sfr_modulation`` and the layer is on: the gas pattern's and the
    star formation law's index (:data:`YOUNG_CONSTANTS`). A catalogue that needs them and is not
    given them raises - it is never drawn by another reader instead; a model that publishes no
    modulation, and any run with the layer off, needs none.

    ``level`` (S32, BUILD_II Phase 8) names the cell hierarchy's depth: at level 0 ``cells``
    are the grid's cells and the catalogue is the sample as always; at level k they are
    child ids (:func:`child_id`), and each child holds **its parent's stars that fall inside
    it** — the same rows, in the parent's order, still named by the parent's cell and index —
    **plus** extra stars from the child's own stream, drawn at the parent's density read at
    the child (uniform over the child's footprint), so that a level-k child holds about as
    many stars as its whole parent did: the sample is 4^k times denser. The union property
    (a parent's stars are its children's) and the prefix property (a smaller sample is a
    subset of a larger one, within a cell at any level) follow by construction and are
    asserted in ``tests/test_hierarchy.py``. Below level 0 the catalogue carries three more
    columns, ``level``, ``cell`` and ``index`` — each row's canonical name, which is what a
    system is opened by: an inherited star's is its parent's, an extra star's is its child's.

    **Ring first** (S61, D220 part I). At level 0 a cell's stars are its ring's draw: the ring's
    count one seeded rounding of its expectation (:func:`ring_star_count`), every per-star uniform
    an array on the ring's stream (:func:`star_stream`), each star's sector the inverse of its
    part's sector weights at its own ``sector`` uniform (:class:`Placement`), its radius, age and
    the rest as before at its own uniforms, its azimuth in the sector by the pattern's point
    function (the young stars' by the star formation law at the point). A cell drawn alone draws
    its ring's count and uniforms whole, keeps the rows allocated to it, and derives every column
    for those rows alone. The catalogue carries its :class:`StarLayout` (``ring_layout``).
    A star's radius inverts its ring's density on the grid's nodes, and the inversion can put it
    up to one node (75 pc on the production grid) past the ring's inner edge, in the next ring's
    footprint while its name is its own cell's (pre-existing; debt #158, measured at S61).

    *Below level 0 the unit is the whole sub-ring* (D220 item 8; the lead's ruling (a) at S61). A
    level-k child's own stars are its sub-ring's draw: the sub-ring's count the seeded rounding of
    2^k (1 − 4^−k) n share (:func:`sub_ring_expected`) on ``(seed, "star", "level", k, sub_ring,
    "count")``, every per-star uniform an array on the sub-ring's stream, each star's child the
    inverse of its part's weights on the sub-ring's 32·2^k children (``Placement.sub_ring_weights``:
    level 0's rule evaluated on the children), its radius and azimuth uniform over the child's
    footprint as since S32. So the sub-ring's realised totals are the same on and off. *The cost,
    accepted as measured:* a child query draws its sub-ring whole - about 1.3 million stars at
    level 3 near R0 at the route's largest sample (5 000 000) - which prices a level-3 child there
    at about 2.2 times the cell draws' (~69 ms against 32, layer off); at n ≤ 10^6 every level
    stays under 2 times, and with the layer on far under (the run's placement tables dominate).
    """
    if not 0 <= level <= MAX_LEVEL:
        raise ValueError(f"level={level} is outside 0..{MAX_LEVEL}")
    # What places the stars round their rings, over every ring and sector (D60): the pattern, the churn's arrival
    # law, the young stars' split and each part's sector weights (S61, D220 item 2).
    placement = Placement(fields, R, t, migration=migration, constants=constants)
    edges, pattern, churn, young = placement.edges, placement.pattern, placement.churn, placement.young
    sigma_star = fields["stellar_surface_density"]
    parents = list(range(CELL_COUNT)) if cells is None or level else [int(c) for c in cells]
    if cells is not None and level:
        parents = sorted({parent_of(int(c), level)[0] for c in cells})
    # S61 (D220 items 1-3): the level-0 stars of the asked cells, drawn ring-first - each ring's count and its
    # uniform arrays whole, the rows allocated to the asked cells kept, every derived column for those rows alone.
    layout, drawn = _layout(placement, sigma_star, R, seed, n_stars, parents)
    counts = layout.counts

    h_thin = float(fields["thin_disc_scale_height"]) / PC_PER_KPC
    h_thick = float(fields["thick_disc_scale_height"]) / PC_PER_KPC or h_thin
    feh = fields["feh_history"]
    # The thin/thick criterion over (birth radius, birth time), published by the vertical
    # stage that owns it. Until S19 this stage rebuilt it from the merger time and the
    # [α/Fe] valley, which in the advanced model was a second definition of "thick" that
    # disagreed with the one every thick-disc row is read from (rule A9).
    thick_at_birth = np.asarray(fields["birth_population"], dtype=np.int64) == POPULATIONS.index("thick")
    # [α/Fe] at birth, read at the same place as [Fe/H].
    alpha = np.asarray(fields["alpha_fe_history"], dtype=float)
    width = 2.0 * math.pi / CELL_SECTORS

    def rows_for(cell: int, count: int, draw: Callable[[str], np.ndarray], footprint: dict[str, float] | None) -> dict[str, np.ndarray]:
        """One cell's (or one child's extra) stars: every column but the looked-up ones.

        ``draw(name)`` is the stream for this set of ``count`` stars; ``footprint`` is None at
        level 0 (radius from the ring's density, azimuth from the contrast in the sector) and a
        child's bounds below it (the parent's density read at the child: uniform over it).
        """
        ring, sector = divmod(int(cell), CELL_SECTORS)
        lo, hi = edges[ring], edges[ring + 1]
        if footprint is None:
            inside = (R >= lo) & (R <= hi)
            weight = np.where(inside, fields["stellar_surface_density"] * R, 0.0)
            radius = invert_cdf(draw("radius"), R, weight)
            phi_lo, phi_hi = sector * width, (sector + 1) * width
        else:
            r_lo, r_hi = footprint["r_lo"], footprint["r_hi"]
            radius = np.sqrt(r_lo * r_lo + draw("radius") * (r_hi * r_hi - r_lo * r_lo))
            phi_lo, phi_hi = footprint["phi_lo"], footprint["phi_hi"]

        # When a star was born, of the stars that are *here now*: the migration kernel's
        # arrival law rather than the local birth rate, which would be the answer for a
        # disc whose stars never moved. Taken once per ring, as the birth-time CDF always
        # was — building one per star would cost 10^6 cumulative sums for a resolution
        # finer than a ring is wide. Since S61 (D220 items 2 and 8) a star's age - a child's own star's too - is drawn
        # from its ring's law, the same on and off, and the young stars' share of a sector is the allocation's
        # (Placement); until S61 each cell tilted the law toward or away from its young steps (YoungStars).
        arrival = churn.arrive[:, ring]
        born = invert_cdf(draw("age"), t, arrival)

        # Where around the ring: the density contrast at the star's own radius, inside its
        # sector; in the azimuthal model a star younger than an arm crossing follows where
        # stars form today instead. Every property has its own stream, so drawing the age
        # first changes no number. A child below level 0 is uniform over its footprint.
        # S60 (D219, the cost): the stars of every cell of the request are placed in one call after the loop
        # (``place``), each star by its own radius and sector exactly as its cell's own call placed it - the
        # pattern's arithmetic is the point's own - so the exact ring means are made in a few large groups
        # rather than once a cell. ``pending`` carries what the placement reads.
        u_azimuth = draw("azimuth")
        uniform = footprint is not None or pattern is None or pattern.flat
        azimuth = phi_lo + u_azimuth * (phi_hi - phi_lo) if uniform else np.empty(count)
        fresh = young.is_young(born) if young is not None and footprint is None else None
        pending = None if uniform and fresh is None else (u_azimuth, radius, phi_lo, phi_hi, uniform, fresh)

        cols = np.clip(np.searchsorted(t, born), 0, len(t) - 1)
        birth_radius = churn.birth_radius(draw("birth_radius"), ring, cols)
        rows = np.clip(np.searchsorted(R, birth_radius), 0, len(R) - 1)

        # Population and abundance are both read at the birth place, because both are
        # decided there: a star born before the merger is thick wherever it drifted to,
        # and its [Fe/H] is the gas it formed from (rule B8 — neither is drawn).
        is_thick = thick_at_birth[rows, cols]
        metallicity = feh[rows, cols]
        height = sech2_height(draw("height"), np.where(is_thick, h_thick, h_thin))
        return {
            "star_radius": radius,
            "star_azimuth": azimuth,
            "star_height": height,
            "star_age": t[-1] - born,
            "star_birth_radius": birth_radius,
            "star_metallicity": metallicity,
            "star_alpha": alpha[rows, cols],
            "star_mass": imf_sample(draw("mass")),
            "star_population": is_thick.astype(np.int64),
        }, pending

    def place(made: Sequence[tuple[dict[str, np.ndarray], tuple | None]]) -> None:
        """Fill ``star_azimuth`` of every cell's rows ``made`` whose placement is pending: the old stars by the
        pattern's contrast at each star's own radius inside its own sector, the young ones (born after an arm
        crossing) by the star formation law at the point (:class:`Modulation`) - every cell's stars in one
        call, :data:`PLACE_CHUNK` stars at a time, the rows a cell's own call would have placed in one
        group skipped where another places them."""
        pending = [(rows["star_azimuth"], *p) for rows, p in made if p is not None]
        if not pending:
            return
        counts_ = [a.size for a, *_ in pending]
        u = np.concatenate([p[1] for p in pending])
        radius = np.concatenate([p[2] for p in pending])
        lo = np.concatenate([np.full(n, p[3]) for n, p in zip(counts_, pending)])
        hi = np.concatenate([np.full(n, p[4]) for n, p in zip(counts_, pending)])
        by_pattern = np.concatenate([np.full(n, not p[5], dtype=bool) for n, p in zip(counts_, pending)])
        fresh = np.concatenate([np.zeros(n, dtype=bool) if p[6] is None else p[6] for n, p in zip(counts_, pending)])
        azimuth = np.concatenate([p[0] for p in pending])
        for who, placer in ((by_pattern & ~fresh, pattern.azimuths if pattern is not None else None),
                            (fresh, young.modulation.azimuths if young is not None else None)):
            rows = np.flatnonzero(who)
            for start in range(0, rows.size, PLACE_CHUNK):
                at = rows[start : start + PLACE_CHUNK]
                azimuth[at] = placer(u[at], radius[at], lo[at], hi[at])
        offset = 0
        for target, n in zip((p[0] for p in pending), counts_):
            target[:] = azimuth[offset : offset + n]
            offset += n

    # The rows' uniforms (D220 items 1 and 3): each touched ring's arrays on its streams, read at each row's place
    # ``i`` in the ring. A Generator's draws are a sequence, so the first ``max(i) + 1`` of a ring's array are the
    # whole array's: the values are the ring's whatever else was asked, and nothing past the last asked row is drawn.
    u_rows: dict[str, np.ndarray] = {}
    for name in STAR_STREAMS:
        values = np.zeros(layout.index.size)
        for r, already in drawn.items():
            here = layout.ring == r
            if not here.any():
                continue
            arr = already.get(name)
            if arr is None:
                arr = star_stream(seed, r, name).random(int(layout.index[here].max()) + 1)
            values[here] = arr[layout.index[here]]
        u_rows[name] = values
    starts = np.cumsum([0] + [n for _, n in counts])

    def cell_rows(k: int) -> Callable[[str], np.ndarray]:
        rows = slice(int(starts[k]), int(starts[k + 1]))
        return lambda name: u_rows[name][rows]

    columns: dict[str, list[np.ndarray]] = {}
    made = [rows_for(cell, count, cell_rows(k), None) for k, (cell, count) in enumerate(counts)]
    place(made)
    if level == 0:
        for rows, _ in made:
            for name, values in rows.items():
                columns.setdefault(name, []).append(values)
        out_counts: tuple[tuple[int, int], ...] = counts
        out_layout = layout
    else:
        # Below level 0: each requested child inherits its parent's stars that fall inside it, then adds its own -
        # its sub-ring's stars allocated to it (S61, D220 item 8, the lead's ruling (a)). A level-k sub-ring is drawn
        # whole, as a level-0 ring is: its count the seeded rounding of 2^k (1 − 4^−k) n share on its stream, every
        # per-star uniform an array on it, each star's child the inverse of its part's weights on the sub-ring's
        # 32·2^k children at its own ``sector`` uniform; within the child its radius and azimuth are uniform over the
        # footprint, as since S32. A child's own star is named (level, child, rank in the child) on the wire and is
        # (level, sub-ring, i) in its draw.
        made = {cell: m for (cell, _), m in zip(counts, made)}
        parent_slice = {cell: slice(int(starts[k]), int(starts[k + 1])) for k, (cell, _) in enumerate(counts)}
        side = 1 << level
        expected_sub = sub_ring_expected(sigma_star, R, n_stars, level)
        asked = [int(c) for c in (cells if cells is not None else range(CELL_COUNT * children_per_cell(level)))]

        def place_of(child: int) -> tuple[int, int, int, int]:
            """(parent, q, sub-ring, child's place among the sub-ring's children)."""
            parent, q = parent_of(child, level)
            ring_, sector_ = divmod(parent, CELL_SECTORS)
            a_, b_ = divmod(q, side)
            return parent, q, ring_ * side + a_, sector_ * side + b_

        drawn_sub: dict[int, dict[str, np.ndarray]] = {}
        alloc_sub: dict[int, np.ndarray] = {}
        for sr in dict.fromkeys(place_of(c)[2] for c in asked):
            ring_ = sr // side
            n_sub = ring_star_count(seed, sr, float(expected_sub[ring_]), level)
            here = {"sector": star_stream(seed, sr, "sector", level).random(n_sub)}
            born_sub = None
            if young is not None:
                here["age"] = star_stream(seed, sr, "age", level).random(n_sub)
                born_sub = placement.born(here["age"], ring_)
            old_w, fresh_w = placement.sub_ring_weights(level, sr)
            alloc_sub[sr] = placement.allocate(here["sector"], born_sub,
                                               np.ones(CELL_SECTORS * side) if old_w is None else old_w,
                                               np.ones(CELL_SECTORS * side) if fresh_w is None else fresh_w) \
                if young is not None else _allocate_among(here["sector"], np.ones(CELL_SECTORS * side) if old_w is None else old_w)
            drawn_sub[sr] = here
        own_rows = {c: np.flatnonzero(alloc_sub[place_of(c)[2]] == place_of(c)[3]) for c in dict.fromkeys(asked)}
        # The children's own stars' uniforms: each sub-ring's arrays, up to its last asked row (a Generator's draws are
        # a sequence), read at each row's place.
        need = {}
        for c, rows_ in own_rows.items():
            if rows_.size:
                sr = place_of(c)[2]
                need[sr] = max(need.get(sr, 0), int(rows_.max()) + 1)
        u_sub = {sr: {name: drawn_sub[sr][name] if name in drawn_sub[sr] else star_stream(seed, sr, name, level).random(m)
                      for name in STAR_STREAMS} for sr, m in need.items()}
        lv: list[np.ndarray] = []
        rg: list[np.ndarray] = []
        ix: list[np.ndarray] = []
        parent_rows = {cell: rows for cell, (rows, _) in made.items()}
        realised: list[tuple[int, int]] = []
        for child in asked:
            parent, q, sr, _ = place_of(child)
            bounds = cell_bounds(R, child, level)
            rows = parent_rows.get(parent)
            if rows is None:
                inherited: dict[str, np.ndarray] = {}
                n_in = 0
            else:
                inside = _within(rows["star_radius"], rows["star_azimuth"], bounds, R, parent, level, q)
                inherited = {name: values[inside] for name, values in rows.items()}
                n_in = int(inside.sum())
                inherited["level"] = np.zeros(n_in, dtype=np.int64)
                inherited["cell"] = np.full(n_in, parent, dtype=np.int64)
                inherited["index"] = np.flatnonzero(inside).astype(np.int64)
                lv.append(np.zeros(n_in, dtype=np.int64))
                rg.append(layout.ring[parent_slice[parent]][inside])
                ix.append(layout.index[parent_slice[parent]][inside])
            mine_ = own_rows[child]
            n_extra = int(mine_.size)
            extra = rows_for(parent, n_extra, lambda name, sr_=sr, at=mine_: u_sub[sr_][name][at], bounds)[0] if n_extra else {}
            if n_extra:
                extra["level"] = np.full(n_extra, level, dtype=np.int64)
                extra["cell"] = np.full(n_extra, child, dtype=np.int64)
                extra["index"] = np.arange(n_extra, dtype=np.int64)
                lv.append(np.full(n_extra, level, dtype=np.int64))
                rg.append(np.full(n_extra, sr, dtype=np.int64))
                ix.append(mine_.astype(np.int64))
            total = n_in + n_extra
            if not total:
                continue
            for name in (*inherited.keys(), *(k for k in extra.keys() if k not in inherited)):
                parts = [d[name] for d in (inherited, extra) if name in d and len(d[name])]
                columns.setdefault(name, []).append(np.concatenate(parts) if parts else np.zeros(0))
            realised.append((child, total))
        out_counts = tuple(realised)
        join = lambda parts: np.concatenate(parts) if parts else np.zeros(0, dtype=np.int64)  # noqa: E731
        out_layout = StarLayout(out_counts, join(lv), join(rg), join(ix),
                                {**layout.sizes, **{(level, sr): v["sector"].size for sr, v in drawn_sub.items()}})

    if not columns:
        empty = np.zeros(0)
        blank = {
            n: (empty.astype(np.int64) if n == "star_population" else empty)
            for n in ("star_radius", "star_azimuth", "star_height", "star_age",
                      "star_birth_radius", "star_metallicity", "star_alpha", "star_mass", "star_population",
                      "star_luminosity", "star_temperature", "star_magnitude_v", "star_ionizing_photons",
                      "star_wind_luminosity", "star_remnant_mass", "star_bubble_radius")
        } | {"star_wolf_rayet": empty.astype(np.int64), "star_remnant": empty.astype(np.int64)}
        if level:
            blank |= {n: empty.astype(np.int64) for n in ("level", "cell", "index")}
        return Catalogue.of(blank, out_counts, out_layout)
    out = {name: np.concatenate(parts) for name, parts in columns.items()}
    # What each star emits, looked up rather than drawn: given its mass, age and abundance
    # the isochrones have already decided (rule B8). Per star, so a region's rows are the
    # sweep's rows (D60).
    out["star_luminosity"], out["star_temperature"] = photometry(out["star_mass"], out["star_age"], out["star_metallicity"])
    # S28 (BUILD_II Phase 3): the rest of what the same point of the table says, and what the
    # massive stars do with it - each a function of columns already here, so looked up rather
    # than drawn, per star, for the same reason (D60).
    more = lookup_columns(out["star_mass"], out["star_age"], out["star_metallicity"], ("V", "mass_now", "label"))
    L, T = out["star_luminosity"], out["star_temperature"]
    out["star_magnitude_v"] = more["V"]
    out["star_ionizing_photons"] = ionizing_photons(L, T)
    out["star_wind_luminosity"] = wind_luminosity(L, T, more["mass_now"], 10.0 ** out["star_metallicity"])
    out["star_wolf_rayet"] = wolf_rayet(out["star_mass"], L, T, more["label"])
    # S29 (BUILD_II Phase 4): what a dead star is. Dead is the NaN the lookup above already put
    # in its luminosity; the class and the remnant's mass follow from its initial mass, and a
    # planetary nebula from how long ago the same table says it died - per star, as above (D60).
    out["star_remnant"], out["star_remnant_mass"] = remnants_of(out["star_mass"], out["star_age"], out["star_metallicity"], L)
    # S36 (BUILD_II Phase 10): the bubble its wind has blown, from its own columns and the gas's midplane
    # density at its radius - per star, as above (D60); a column added, none moved.
    out["star_bubble_radius"] = star_bubble_radius(
        out["star_wind_luminosity"], out["star_age"], np.interp(out["star_radius"], R, np.asarray(fields["gas_midplane_density"], dtype=float))
    )
    return Catalogue.of(out, out_counts, out_layout)


def _within(radius: np.ndarray, azimuth: np.ndarray, bounds: Mapping[str, float], R: np.ndarray, parent: int, level: int, q: int) -> np.ndarray:
    """Which of a parent's stars fall in child ``q``: by the sub-ring and sub-sector index of each
    star's position, so that every star lands in exactly one child and the children partition the
    parent (a boundary star goes to the higher child, the last child closed)."""
    n = 1 << level  # children per side
    rings, sectors = cell_edges(R)
    ring, sector = divmod(int(parent), CELL_SECTORS)
    r_lo, r_hi = rings[ring], rings[ring + 1]
    p_lo, p_hi = sectors[sector], sectors[sector + 1]
    a = np.clip(np.floor((np.asarray(radius) - r_lo) / (r_hi - r_lo) * n).astype(int), 0, n - 1)
    b = np.clip(np.floor((np.mod(np.asarray(azimuth), 2.0 * math.pi) - p_lo) / (p_hi - p_lo) * n).astype(int), 0, n - 1)
    return (a * n + b) == int(q)


# --- derived half -------------------------------------------------------------

MEAN_STELLAR_MASS = FieldDecl(
    name="mean_stellar_mass", label="Mean stellar mass", unit="Msun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Mass-weighted mean of the Kroupa IMF, integrated analytically rather than sampled — "
        "there is nothing random about the mean of a known distribution (rule B8). It is what "
        "turns a stellar mass into a star count."
    ),
)

STAR_COUNT_TOTAL = FieldDecl(
    name="star_count_total", label="Stars in the galaxy", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "M_star divided by the mean stellar mass: about 1.5 × 10¹¹. The catalogue materialises a "
        "vanishing fraction of them, which is the whole reason GALAXY_PLAN.md §4 renders the "
        "field as an image and only a sample as objects."
    ),
)


REMNANT_MASS_FRACTION = FieldDecl(
    name="remnant_mass_fraction", label="Mass fraction in stellar remnants", unit="dimensionless",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Of the mass in stars and their remnants, the share in white dwarfs, neutron stars and black "
        "holes: every step of the formation history, and the bulge, times what a Kroupa population "
        "leaves per unit mass formed at that age and [Fe/H] along the PARSEC isochrones - the stars "
        "still alive at their present mass, and every dead one's remnant (Cummings et al. 2018's "
        "initial-final mass relation for the white dwarfs; 1.33 and 7.8 M☉ for the neutron stars and "
        "black holes, the measured Galactic means). A population integral, not a count of the sample. "
        "The isochrones return more of the mass formed than the star formation law's instantaneous "
        "return fraction does, so stars and remnants together come to less than the stellar mass the "
        "model publishes; this is a share of the former."
    ),
)

PLANETARY_NEBULA_COUNT = FieldDecl(
    name="planetary_nebula_count", label="Planetary nebulae", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "How many planetary nebulae the galaxy holds today: the rate at which stars that will become "
        "white dwarfs are dying, from the same population integral, times the 27 000 years a nebula "
        "stays visible (Badenes, Maoz & Ciardullo 2015). The sample of 2 × 10⁴ stars almost never "
        "catches one. Stars older than 12.6 Gyr, where the isochrones end, die no more and make none."
    ),
)


def compute_population(ctx: Context) -> Mapping[str, Any]:
    from galaxy.stages.light import bulge_abundance
    from galaxy.stages.remnants import budget

    mean_mass = imf_mean_mass()
    R, t = ctx.grid.R, ctx.grid.t
    ret = float(ctx.constants["RETURN_FRACTION"])
    locked = np.asarray(ctx.fields["stars_formed_history"], dtype=float)
    # S29 (BUILD_II Phase 4): what the locked mass is made of, integrated as the light is.
    mass = budget(
        locked, ctx.fields["feh_history"], R, t, float(ctx.grid.spec.t_max), ret,
        float(ctx.fields["bulge_stellar_mass"]), float(t[-1] - t[0]),
        bulge_abundance(R, locked / (1.0 - ret), ctx.fields["feh_history"], float(ctx.fields["bulge_scale_radius"])),
    )
    return {
        "mean_stellar_mass": mean_mass,
        "star_count_total": float(ctx.fields["stellar_mass_total"]) / mean_mass,
        "remnant_mass_fraction": mass.remnant_fraction,
        "planetary_nebula_count": mass.planetary_nebulae,
    }


POPULATION = IMPLEMENTATIONS.register(
    Stage(
        id="population", slot="population", checkpoint=5,
        about=(
            "IMF integrals: the mean stellar mass, how many stars the galaxy has, what share of its "
            "stellar mass is in remnants and how many planetary nebulae it holds. No draws (D55)."
        ),
        compute=compute_population,
        reads_constants=("RETURN_FRACTION",),
        requires=(
            "stellar_mass_total", "stars_formed_history", "feh_history", "bulge_stellar_mass", "bulge_scale_radius",
        ),
        publishes=(MEAN_STELLAR_MASS, STAR_COUNT_TOTAL, REMNANT_MASS_FRACTION, PLANETARY_NEBULA_COUNT),
    )
)


# --- seeded half --------------------------------------------------------------

def _column(name, label, unit, about, ramp=Ramp("viridis")):
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="star",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about)


STAR_RADIUS = _column("star_radius", "Galactocentric radius", "kpc",
                      "Drawn by inverting the radial mass distribution the model published, so the "
                      "sample traces the disc exactly rather than approximately.")
STAR_AZIMUTH = _column("star_azimuth", "Azimuth", "rad",
                       "Drawn from the bar and arm density contrast at the star's radius, so stars "
                       "crowd into the arms and the bar. Where the model publishes where stars form "
                       "today (sfr_modulation, the azimuthal model), a star younger than about one arm "
                       "crossing, 100 Myr, is placed by that instead, and the young stars crowd into "
                       "the arms more tightly than the old ones.")
STAR_HEIGHT = _column("star_height", "Height above the plane", "kpc",
                      "Inverted from the sech² profile at the star's own population's scale height, "
                      "so the thick disc is genuinely thicker rather than tagged as such.")
STAR_AGE = _column("star_age", "Age", "Gyr",
                   "Drawn from the star formation history at its radius, restricted to its "
                   "population's era — so an old thick-disc star and a young thin-disc one come "
                   "from the same machinery.", ramp=Ramp("magma"))
STAR_BIRTH_RADIUS = _column(
    "star_birth_radius", "Birth radius", "kpc",
    "Where the star formed, drawn backwards through the chemistry's migration kernel from where "
    "it is now — so its abundance is read off the gas it was actually made from. The difference "
    "from star_radius is the churning, and it is what debt #31 said the catalogue was missing.")
STAR_METALLICITY = _column("star_metallicity", "[Fe/H]", "dex",
                           "Looked up at the star's *birth* radius and birth time, not drawn: given "
                           "when and where it formed, its abundance is already decided (rule B8).",
                           ramp=Ramp("RdBu", lo=-2.0, hi=0.5))
STAR_ALPHA = _column("star_alpha", "[α/Fe]", "dex",
                     "Looked up at the star's birth radius and birth time from alpha_fe_history, exactly "
                     "as [Fe/H] is, so a star born on the core-collapse plateau is α-enhanced wherever it "
                     "drifted to. Painted by it, the catalogue splits into the α-rich and α-poor sequences "
                     "the vertical stage divides thick from thin by (D169).",
                     ramp=Ramp("viridis", scale="linear", lo=-0.1, hi=0.5))
STAR_MASS = _column("star_mass", "Stellar mass", "Msun",
                    "Kroupa by inverse CDF. The steep high-mass slope means almost every star in "
                    "the sample is smaller than the Sun.", ramp=Ramp("inferno", scale="log"))

STAR_LUMINOSITY = _column(
    "star_luminosity", "Luminosity", "Lsun",
    "Bolometric, from the PARSEC isochrones at the star's initial mass, age and [Fe/H] "
    "(galaxy/stages/photometry.py, RENDER_PLAN M2). NaN for a star that has died: the table "
    "carries no remnants, and a white dwarf's thousandth of a solar luminosity is not "
    "invented. Ages past 12.6 Gyr are read at 12.6 Gyr, where the table ends.",
    ramp=Ramp("inferno", scale="log"))
STAR_TEMPERATURE = _column(
    "star_temperature", "Effective temperature", "K",
    "From the same isochrone lookup as the luminosity. Its ramp is the blackbody colour of "
    "the temperature itself (galaxy/core/cmaps.py), which is what makes a photometric render "
    "a published quantity rather than a palette: most stars are M dwarfs, so a correct "
    "galaxy is overwhelmingly red and its blue stars are young and few.",
    ramp=Ramp("blackbody", scale="log", lo=BLACKBODY_KELVIN[0], hi=BLACKBODY_KELVIN[1]))

STAR_MAGNITUDE_V = FieldDecl(
    name="star_magnitude_v", label="Absolute V magnitude M_V", unit="mag", kind=Kind.COLUMN, of="star",
    ramp=Ramp("inferno", lo=-8.0, hi=15.0), meaningful_zero=False, provenance="seeded",
    about=(
        "The star's absolute V magnitude, Vega system, from the same point of the PARSEC table as its "
        "luminosity and temperature (the table's own bolometric corrections). What a V-band image of "
        "the sample would weight each star by: an M dwarf is 10-15, the Sun 4.8, a red giant 0 to -3 "
        "and an O star -4 to -6. NaN for a star that has died. Intrinsic, before any dust."
    ),
)
STAR_IONIZING_PHOTONS = _column(
    "star_ionizing_photons", "Hydrogen-ionizing photon rate Q(H⁰)", "1/s",
    "Photons above 13.6 eV per second: the star's surface area, L / σT_eff⁴, times the photon flux "
    "per unit area of a model atmosphere at its temperature, tabulated for O and early-B dwarfs by "
    "Sternberg, Hoffmann & Pauldrach 2003. Outside that table's 32-51 kK the blackbody carries the "
    "temperature dependence, joined to the table at its end. Brutally steep: an O5 dwarf emits ~3 "
    "× 10⁴⁹, a B0 ~1 × 10⁴⁸, and the Sun's is negligible, so a handful of the sample's stars carry "
    "all of it. NaN for a star that has died.",
    ramp=Ramp("magma", scale="log", lo=1e40, hi=1e50))
STAR_WIND_LUMINOSITY = _column(
    "star_wind_luminosity", "Wind mechanical luminosity", "Lsun",
    "½ Ṁ v_∞² of the star's line-driven wind: Ṁ from Vink, de Koter & Lamers 2001's recipe at its "
    "luminosity, temperature, present mass and 10^[Fe/H] as Z/Z☉, v_∞ its fixed multiple of the "
    "escape velocity on either side of the bistability jump. The escape velocity is Newtonian: the "
    "source's Eddington reduction needs an opacity it cites and this model has not read, so v_∞ is "
    "high by (1 − Γ_e)^(−1/2). NaN outside the recipe's 12.5-50 kK, which is almost every star.",
    ramp=Ramp("inferno", scale="log"))
STAR_WOLF_RAYET = FieldDecl(
    name="star_wolf_rayet", label="Wolf-Rayet (proxy)", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="star", categories=WR_CATEGORIES, ramp=Palette(("#5a5a5a", "#6fd3ff")), provenance="seeded",
    about=(
        "A stated proxy, not a classification: the isochrones do not name Wolf-Rayet stars, so a star "
        "is flagged when it is past the main sequence, was born at 25 M☉ or more, is hotter than 30 kK "
        "and brighter than 1.5 × 10⁵ L☉ - the lowest initial mass, temperature and luminosity Crowther "
        "2007 quotes for WR stars at solar metallicity. What makes a WR star, a hydrogen-stripped "
        "surface under a dense wind, the table cannot see. They live a few hundred thousand years, so "
        "a sample of 2 × 10⁴ usually holds none."
    ),
)

STAR_REMNANT = FieldDecl(
    name="star_remnant", label="Remnant", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="star", categories=REMNANT_CATEGORIES,
    ramp=Palette(("#5a5a5a", "#d8e4ff", "#9b6cff", "#111111", "#4cf0b0")), provenance="seeded",
    about=(
        "What a star that has died is, looked up rather than drawn: a star is dead where the PARSEC "
        "isochrones no longer hold it (its luminosity is NaN), and then a white dwarf below 8.5 M☉ of "
        "initial mass (the lowest observed core-collapse progenitor, Smartt 2009), a neutron star up to "
        "25 M☉ and a black hole above it (Heger et al. 2003) - solar-metallicity boundaries applied at "
        "every [Fe/H]. A white dwarf's progenitor that left the AGB less than 27 000 years ago "
        "(Badenes, Maoz & Ciardullo 2015) is a planetary nebula instead. A living star is none."
    ),
)
STAR_REMNANT_MASS = _column(
    "star_remnant_mass", "Remnant mass", "Msun",
    "The mass of a dead star's remnant: a white dwarf's from its initial mass by Cummings et al. "
    "2018's initial-final mass relation, fitted with the same PARSEC isochrones the catalogue reads "
    "(0.55 M☉ from a 0.8 M☉ star, 1.23 from an 8 M☉ one); a neutron star 1.33 M☉ and a black hole 7.8, "
    "the measured means of the Galaxy's double neutron stars and X-ray-binary black holes. A black "
    "hole's mass certainly depends on its metallicity; no fit for that has been read, so it does not "
    "here. NaN for a living star, which has no remnant.",
    ramp=Ramp("cividis", scale="log"))

STAR_BUBBLE_RADIUS = _column(
    "star_bubble_radius", "Wind bubble radius", "pc",
    "The bubble the star's own wind has blown: Weaver et al. 1977's energy-conserving solution, R = 0.76 "
    "(L_w / ρ₀)^⅕ t^⅗, at its wind power held for its whole age, in the gas's midplane density at its "
    "radius. Why that density and not its cloud's: the catalogue places a star by the disc's densities "
    "and the cloud census places clouds by the molecular gas's, independently, so a star found inside a "
    "cloud would be a coincidence of two draws, not a birthplace. The midplane density is the volume "
    "average over every phase, low for an O star still in its natal cloud, so these bubbles are large. "
    "NaN wherever the wind is (outside the recipe's 12.5-50 kK: almost every star). Not stalled, as a "
    "cluster's is: in the thin midplane gas a single O star's shell stays faster than the ionized gas's "
    "sound speed out to tens of parsecs. A star's own bubble inside a cluster's is not distinguished from it.",
    ramp=Ramp("viridis", scale="log"))

STAR_POPULATION = FieldDecl(
    name="star_population", label="Population", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="star", categories=POPULATIONS, ramp=Palette(("#4c9be8", "#e8894c")),
    provenance="seeded",
    about=(
        "Thin or thick, read off birth_population at the star's own birth place — the vertical "
        "stage's criterion, applied to where and when this star formed. It is not drawn: given a "
        "birth time the answer is already decided. Migrants make the catalogue's thick fraction "
        "at R₀ larger than thick_thin_surface_density_ratio, which is the same population moved "
        "by the other of the model's two transports (debt #50)."
    ),
)

CATALOGUE_SIZE = FieldDecl(
    name="catalogue_size", label="Stars in the catalogue", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "How many of GALAXY_PLAN.md §4's clickable sample were actually materialised. It differs "
        "from the requested size by the per-ring rounding (per cell until S61), which is a seeded Bernoulli on the "
        "fractional part rather than a rounding rule that would bias the disc's outskirts away - the same "
        "number with the layer on or off, since the layer places a ring's stars and never draws them (D220). "
        "**Not shown by the viewer** (debt #69, ruled at S22): it is a galaxy scalar of the stage "
        "that publishes the object columns, which `scalarsAt` excludes so the client cannot "
        "materialise a galaxy to print one number (rule D4). Nothing is lost — the region "
        "response's own cell census carries the count, which is where the viewer reads it."
    ),
)


def compute_systems(ctx: Context) -> Mapping[str, Any]:
    catalogue = materialise(
        ctx.fields, ctx.grid.R, ctx.grid.t, int(ctx.seeds["systems_seed"]), CATALOGUE_SAMPLE,
        migration=float(ctx.inputs["migration_efficiency"]), constants=ctx.constants,
    )
    return {**catalogue, "catalogue_size": float(catalogue.size)}


SYSTEMS = IMPLEMENTATIONS.register(
    Stage(
        id="systems", slot="systems", checkpoint=5,
        about=(
            "The materialised star catalogue: a stable, seeded sample of the galaxy's stars, "
            "drawn by inverting densities the model already published."
        ),
        compute=compute_systems,
        placement_reader=True,  # S55 (D214, I4): a census, placed by the stellar pattern and the modulation
        reads_seeds=("systems_seed",),
        reads_inputs=("migration_efficiency",),
        # S59 (D218): what the young stars' reader applies the star formation law with - the gas pattern's
        # constants and the law's index. Read only where the model publishes a modulation and the layer is on.
        reads_constants=YOUNG_CONSTANTS,
        requires=tuple(dict.fromkeys((
            "stellar_surface_density", "thin_disc_scale_height", "thick_disc_scale_height",
            "birth_population", "sfr_surface_density_history", "feh_history", "alpha_fe_history",
            *PATTERN_READS,  # S56 (D215): the stellar pattern's modes and their phases, not an arm number
            "gas_midplane_density",  # S36: what a star's wind bubble expands into
            # S59 (D218): the young stars' reader - the gas pattern's own reads (it is built from compose, as the
            # clouds' is) and the ring's gas column and threshold, which the law is applied with ring by ring.
            *GAS_PATTERN_READS, *YOUNG_READS,
        ))),
        # Where stars form today: the azimuthal model's own field, absent in basic (S27). Since S59 the census
        # asks only whether the model publishes it - the reader is the law itself, not the table.
        requires_optional=("sfr_modulation",),
        publishes=(
            STAR_RADIUS, STAR_AZIMUTH, STAR_HEIGHT, STAR_AGE, STAR_BIRTH_RADIUS,
            STAR_METALLICITY, STAR_ALPHA, STAR_MASS, STAR_LUMINOSITY, STAR_TEMPERATURE, STAR_POPULATION, CATALOGUE_SIZE,
            STAR_MAGNITUDE_V, STAR_IONIZING_PHOTONS, STAR_WIND_LUMINOSITY, STAR_WOLF_RAYET,
            STAR_REMNANT, STAR_REMNANT_MASS, STAR_BUBBLE_RADIUS,
        ),
    )
)
