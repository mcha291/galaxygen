"""Systems: the star catalogue, headless (checkpoint 5).

**Nothing here rejects a sample it could have inverted** (rule B8). Every
positional draw is an inverse-CDF lookup against a density the model already
published: the radial mass distribution, the sech² vertical profile, the star
formation history at a radius. A rejection sampler would have been easier to
write and would have thrown away most of its draws, and its cost would have
depended on how peaked the galaxy happened to be.

**Per-region determinism, and how it is obtained.** The galaxy is divided into a
fixed grid of cells in (R, φ). A star's identity is ``(cell, index)``, and every
one of its properties comes from ``rng(systems_seed, "cell", cell, property)``
drawn at position ``index`` in that stream. Two consequences fall out, and they
are what the gate is about:

- **Order independence.** Nothing is drawn from a shared stream, so generating a
  region alone gives exactly what generating it inside a full sweep gives.
- **A smaller sample is a *prefix* of a larger one.** Each property has its own
  stream, so asking for 10 stars from a cell gives the first 10 of the 1000 that
  a full materialisation would give — which is what makes the clickable sample of
  GALAXY_PLAN.md §4 stable while the LOD ladder materialises more underneath it.

That second property is the reason each property gets its own stream rather than
one stream per star. With a single stream, drawing radius-then-age for 10 stars
would leave it at a different position than for 1000, and the prefix would break.

**What the catalogue does not have.** It is axisymmetric. S4 published a pitch
angle and an arm multiplicity but no non-axisymmetric density, so there is
nothing here to wind stars into arms — recorded as debt #23 rather than faked
with a modulation nothing in the model justifies.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.chemistry import age_bin_edges, migration_width, transport_columns
from galaxy.stages.disc import PC_PER_KPC
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
CATALOGUE_SAMPLE = 20_000  # the clickable sample of GALAXY_PLAN.md §4, order 10^4-10^5

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
    """

    counts: tuple[tuple[int, int], ...] = ()

    @classmethod
    def of(cls, columns: Mapping[str, Any], counts: Sequence[tuple[int, int]] = ()) -> "Catalogue":
        made = cls(columns)
        made.counts = tuple((int(c), int(n)) for c, n in counts)
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


def cell_bounds(R: np.ndarray, cell: int) -> dict[str, float]:
    """The (R, φ) footprint of one cell, for a caller that has to draw it."""
    rings, sectors = cell_edges(R)
    ring, sector = divmod(int(cell), CELL_SECTORS)
    return {
        "r_lo": float(rings[ring]), "r_hi": float(rings[ring + 1]),
        "phi_lo": float(sectors[sector]), "phi_hi": float(sectors[sector + 1]),
    }


def cells_in(
    R: np.ndarray, r_lo: float, r_hi: float, phi_lo: float = 0.0, phi_hi: float = 2.0 * math.pi
) -> tuple[int, ...]:
    """Every cell whose footprint meets the window. φ wraps; the window may cross zero.

    A window narrower than a cell still selects the cell containing it, so a
    query never comes back empty because it was too small to straddle an edge.
    """
    rings, sectors = cell_edges(R)
    if r_hi < r_lo:
        r_lo, r_hi = r_hi, r_lo
    span = min(max(phi_hi - phi_lo, 0.0), 2.0 * math.pi)
    start = phi_lo % (2.0 * math.pi)
    windows = [(start, start + span)]
    if start + span > 2.0 * math.pi:  # the window crosses φ = 0 and is two intervals
        windows = [(start, 2.0 * math.pi), (0.0, start + span - 2.0 * math.pi)]

    def meets(lo: float, hi: float, a: float, b: float) -> bool:
        return lo < b and a < hi or (a == b and lo <= a <= hi) or (lo == hi and a <= lo <= b)

    want_rings = [i for i in range(CELL_RINGS) if meets(rings[i], rings[i + 1], r_lo, r_hi)]
    want_sectors = [
        j for j in range(CELL_SECTORS)
        if any(meets(sectors[j], sectors[j + 1], a, b) for a, b in windows)
    ]
    return tuple(i * CELL_SECTORS + j for i in want_rings for j in want_sectors)


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


def cell_counts(
    sigma_star: np.ndarray,
    R: np.ndarray,
    seed: int,
    n_stars: int,
    cells: Sequence[int] | None = None,
) -> tuple[tuple[int, int], ...]:
    """``(cell, count)`` for every cell that realises a star, in cell order.

    Split out of :func:`materialise` because a star's *identity* is ``(cell,
    index)`` (D60) and more than one caller needs it: a later stage keying its own
    draws on a star, and an API mapping a row of a region query back to the star it
    came from. Recomputing the layout somewhere else would be a second definition
    of which star is which, and the two would diverge silently.

    It is cheap — one ``Generator`` per cell for the rounding, no property streams —
    so knowing the layout costs a fraction of drawing the stars themselves.
    """
    share = cell_shares(sigma_star, R)
    wanted = range(CELL_COUNT) if cells is None else cells
    out: list[tuple[int, int]] = []
    for cell in wanted:
        ring = int(cell) // CELL_SECTORS
        expected = n_stars * share[ring] / CELL_SECTORS
        base = int(expected)
        frac = expected - base
        # The fractional part is a seeded Bernoulli rather than a rounding rule,
        # which would bias the disc's outskirts away entirely.
        count = base + int(_seeds.rng(seed, "cell", int(cell), "count").random() < frac)
        if count:
            out.append((int(cell), count))
    return tuple(out)


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


def materialise(
    fields: Mapping[str, Any],
    R: np.ndarray,
    t: np.ndarray,
    seed: int,
    n_stars: int,
    cells: Sequence[int] | None = None,
    *,
    migration: float,
) -> Catalogue:
    """Generate ``n_stars`` across the whole galaxy, or only within ``cells``.

    Passing a subset of cells returns exactly the stars those cells would have in
    a full sweep — that is the per-region determinism the gate is about.

    ``migration`` is the ``migration_efficiency`` input and is keyword-only and required
    on purpose: it is the one argument here that is not a published field, and a default
    of zero would have made a caller that forgot it silently produce the unmigrated
    catalogue of debt #31 — the defect this signature exists to make unreachable (rule B13).
    """
    _, edges = cell_masses(fields["stellar_surface_density"], R)

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
    ring_index = np.array([int(np.argmin(np.abs(R - r))) for r in ring_radius])

    counts = cell_counts(fields["stellar_surface_density"], R, seed, n_stars, cells)
    columns: dict[str, list[np.ndarray]] = {}

    h_thin = float(fields["thin_disc_scale_height"]) / PC_PER_KPC
    h_thick = float(fields["thick_disc_scale_height"]) / PC_PER_KPC or h_thin
    feh = fields["feh_history"]
    # The thin/thick criterion over (birth radius, birth time), published by the vertical
    # stage that owns it. Until S19 this stage rebuilt it from the merger time and the
    # [α/Fe] valley, which in the advanced model was a second definition of "thick" that
    # disagreed with the one every thick-disc row is read from (rule A9).
    thick_at_birth = np.asarray(fields["birth_population"], dtype=np.int64) == POPULATIONS.index("thick")
    # Every cell ring, whichever cells were asked for. Narrowing it to the rings a region
    # query touches was tried and reverted: the arrival law is a matrix product over the
    # rings, and BLAS sums a 1-column product in a different order than a 32-column one, so
    # a region came back with a star one bit from the sweep's. Per-region determinism is
    # this stage's whole contract (D60), and arithmetic that depends on what was asked for
    # is the one thing it cannot have. Affordable because the kernel is read by column now.
    churn = Churn(R, t, fields["sfr_surface_density_history"], ring_index, migration)

    for cell, count in counts:
        ring, sector = divmod(int(cell), CELL_SECTORS)

        def draw(name: str, k: int = count) -> np.ndarray:
            return _seeds.rng(seed, "cell", int(cell), name).random(k)

        lo, hi = edges[ring], edges[ring + 1]
        inside = (R >= lo) & (R <= hi)
        weight = np.where(inside, fields["stellar_surface_density"] * R, 0.0)
        radius = invert_cdf(draw("radius"), R, weight)

        azimuth = (sector + draw("azimuth")) * (2.0 * math.pi / CELL_SECTORS)

        # When a star was born, of the stars that are *here now*: the migration kernel's
        # arrival law rather than the local birth rate, which would be the answer for a
        # disc whose stars never moved. Taken once per ring, as the birth-time CDF always
        # was — building one per star would cost 10^6 cumulative sums for a resolution
        # finer than a ring is wide.
        born = invert_cdf(draw("age"), t, churn.arrive[:, ring])
        cols = np.clip(np.searchsorted(t, born), 0, len(t) - 1)
        birth_radius = churn.birth_radius(draw("birth_radius"), ring, cols)
        rows = np.clip(np.searchsorted(R, birth_radius), 0, len(R) - 1)

        # Population and abundance are both read at the birth place, because both are
        # decided there: a star born before the merger is thick wherever it drifted to,
        # and its [Fe/H] is the gas it formed from (rule B8 — neither is drawn).
        is_thick = thick_at_birth[rows, cols]
        metallicity = feh[rows, cols]

        height = sech2_height(draw("height"), np.where(is_thick, h_thick, h_thin))

        columns.setdefault("star_radius", []).append(radius)
        columns.setdefault("star_azimuth", []).append(azimuth)
        columns.setdefault("star_height", []).append(height)
        columns.setdefault("star_age", []).append(t[-1] - born)
        columns.setdefault("star_birth_radius", []).append(birth_radius)
        columns.setdefault("star_metallicity", []).append(metallicity)
        columns.setdefault("star_mass", []).append(imf_sample(draw("mass")))
        columns.setdefault("star_population", []).append(is_thick.astype(np.int64))

    if not columns:
        empty = np.zeros(0)
        return Catalogue.of({
            n: (empty.astype(np.int64) if n == "star_population" else empty)
            for n in ("star_radius", "star_azimuth", "star_height", "star_age",
                      "star_birth_radius", "star_metallicity", "star_mass", "star_population")
        }, counts)
    return Catalogue.of({name: np.concatenate(parts) for name, parts in columns.items()}, counts)


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


def compute_population(ctx: Context) -> Mapping[str, Any]:
    mean_mass = imf_mean_mass()
    return {
        "mean_stellar_mass": mean_mass,
        "star_count_total": float(ctx.fields["stellar_mass_total"]) / mean_mass,
    }


POPULATION = IMPLEMENTATIONS.register(
    Stage(
        id="population", slot="population", checkpoint=5,
        about="IMF integrals: the mean stellar mass and how many stars the galaxy has. No draws (D55).",
        compute=compute_population,
        requires=("stellar_mass_total",),
        publishes=(MEAN_STELLAR_MASS, STAR_COUNT_TOTAL),
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
                       "Uniform within the star's sector. The catalogue is axisymmetric because "
                       "the model's density is: S4 published arm parameters but no arms (debt #23).")
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
STAR_MASS = _column("star_mass", "Stellar mass", "Msun",
                    "Kroupa by inverse CDF. The steep high-mass slope means almost every star in "
                    "the sample is smaller than the Sun.", ramp=Ramp("inferno", scale="log"))

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
        "from the requested size by the per-cell rounding, which is a seeded Bernoulli on the "
        "fractional part rather than a rounding rule that would bias the disc's outskirts away. "
        "**Not shown by the viewer** (debt #69, ruled at S22): it is a galaxy scalar of the stage "
        "that publishes the object columns, which `scalarsAt` excludes so the client cannot "
        "materialise a galaxy to print one number (rule D4). Nothing is lost — the region "
        "response's own cell census carries the count, which is where the viewer reads it."
    ),
)


def compute_systems(ctx: Context) -> Mapping[str, Any]:
    catalogue = materialise(
        ctx.fields, ctx.grid.R, ctx.grid.t, int(ctx.seeds["systems_seed"]), CATALOGUE_SAMPLE,
        migration=float(ctx.inputs["migration_efficiency"]),
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
        reads_seeds=("systems_seed",),
        reads_inputs=("migration_efficiency",),
        requires=(
            "stellar_surface_density", "thin_disc_scale_height", "thick_disc_scale_height",
            "birth_population", "sfr_surface_density_history", "feh_history",
        ),
        publishes=(
            STAR_RADIUS, STAR_AZIMUTH, STAR_HEIGHT, STAR_AGE, STAR_BIRTH_RADIUS,
            STAR_METALLICITY, STAR_MASS, STAR_POPULATION, CATALOGUE_SIZE,
        ),
    )
)
