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
from galaxy.stages.disc import PC_PER_KPC

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
POPULATIONS: tuple[str, ...] = ("thin", "thick")

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


def sech2_height(u: np.ndarray, scale: np.ndarray | float) -> np.ndarray:
    """Inverse CDF of the self-gravitating sheet: ρ ∝ sech²(z/2h), so z = 2h artanh(2u−1)."""
    return 2.0 * np.asarray(scale) * np.arctanh(np.clip(2.0 * np.asarray(u) - 1.0, -0.999999, 0.999999))


class Catalogue(dict):
    """A materialised set of stars: name -> column. A plain mapping, deliberately."""

    @property
    def size(self) -> int:
        return len(next(iter(self.values()))) if self else 0


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


def materialise(
    fields: Mapping[str, Any],
    R: np.ndarray,
    t: np.ndarray,
    seed: int,
    n_stars: int,
    cells: Sequence[int] | None = None,
) -> Catalogue:
    """Generate ``n_stars`` across the whole galaxy, or only within ``cells``.

    Passing a subset of cells returns exactly the stars those cells would have in
    a full sweep — that is the per-region determinism the gate is about.
    """
    ring_mass, edges = cell_masses(fields["stellar_surface_density"], R)
    total = ring_mass.sum()
    share = ring_mass / total if total > 0.0 else np.zeros_like(ring_mass)

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

    wanted = range(CELL_COUNT) if cells is None else cells
    columns: dict[str, list[np.ndarray]] = {}

    sigma_thin = fields["thin_disc_surface_density"]
    sigma_thick = fields["thick_disc_surface_density"]
    h_thin = float(fields["thin_disc_scale_height"]) / PC_PER_KPC
    h_thick = float(fields["thick_disc_scale_height"]) / PC_PER_KPC or h_thin
    psi = fields["sfr_surface_density_history"]
    feh = fields["feh_history"]
    onset = float(fields["last_major_merger_time"])

    for cell in wanted:
        ring, sector = divmod(int(cell), CELL_SECTORS)
        expected = n_stars * share[ring] / CELL_SECTORS
        base = int(expected)
        frac = expected - base
        count = base + int(_seeds.rng(seed, "cell", int(cell), "count").random() < frac)
        if count == 0:
            continue

        def draw(name: str, k: int = count) -> np.ndarray:
            return _seeds.rng(seed, "cell", int(cell), name).random(k)

        lo, hi = edges[ring], edges[ring + 1]
        inside = (R >= lo) & (R <= hi)
        weight = np.where(inside, fields["stellar_surface_density"] * R, 0.0)
        radius = invert_cdf(draw("radius"), R, weight)

        azimuth = (sector + draw("azimuth")) * (2.0 * math.pi / CELL_SECTORS)

        # Per star, not per cell: the thick fraction varies across a ring's width.
        thin_here = np.interp(radius, R, sigma_thin)
        thick_here = np.interp(radius, R, sigma_thick)
        both = thin_here + thick_here
        p_thick = np.where(both > 0.0, thick_here / np.where(both > 0.0, both, 1.0), 0.0)
        is_thick = draw("population") < p_thick

        height = sech2_height(draw("height"), np.where(is_thick, h_thick, h_thin))

        # The birth-time CDF is taken once per ring rather than per star: building a
        # separate CDF for every star would cost 10^6 cumulative sums for a resolution
        # finer than a ring is wide.
        index = int(np.argmin(np.abs(R - ring_radius[ring])))
        window = (t < onset) if onset > 0.0 else np.ones_like(t, dtype=bool)
        born_thick = invert_cdf(draw("age"), t, np.where(window, psi[index], 0.0))
        born_thin = invert_cdf(draw("age_thin"), t, np.where(~window, psi[index], 0.0))
        born = np.where(is_thick, born_thick, born_thin)

        rows = np.clip(np.searchsorted(R, radius), 0, len(R) - 1)
        cols = np.clip(np.searchsorted(t, born), 0, len(t) - 1)
        metallicity = feh[rows, cols]

        columns.setdefault("star_radius", []).append(radius)
        columns.setdefault("star_azimuth", []).append(azimuth)
        columns.setdefault("star_height", []).append(height)
        columns.setdefault("star_age", []).append(t[-1] - born)
        columns.setdefault("star_metallicity", []).append(metallicity)
        columns.setdefault("star_mass", []).append(imf_sample(draw("mass")))
        columns.setdefault("star_population", []).append(is_thick.astype(np.int64))

    if not columns:
        empty = np.zeros(0)
        return Catalogue({
            n: (empty.astype(np.int64) if n == "star_population" else empty)
            for n in ("star_radius", "star_azimuth", "star_height", "star_age",
                      "star_metallicity", "star_mass", "star_population")
        })
    return Catalogue({name: np.concatenate(parts) for name, parts in columns.items()})


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
STAR_METALLICITY = _column("star_metallicity", "[Fe/H]", "dex",
                           "Looked up at the star's radius and birth time, not drawn: given when "
                           "and where it formed, its abundance is already decided (rule B8).",
                           ramp=Ramp("RdBu", lo=-2.0, hi=0.5))
STAR_MASS = _column("star_mass", "Stellar mass", "Msun",
                    "Kroupa by inverse CDF. The steep high-mass slope means almost every star in "
                    "the sample is smaller than the Sun.", ramp=Ramp("inferno", scale="log"))

STAR_POPULATION = FieldDecl(
    name="star_population", label="Population", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="star", categories=POPULATIONS, ramp=Palette(("#4c9be8", "#e8894c")),
    provenance="seeded",
    about="Thin or thick, drawn against the local surface-density ratio the vertical stage published.",
)

CATALOGUE_SIZE = FieldDecl(
    name="catalogue_size", label="Stars in the catalogue", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "How many of GALAXY_PLAN.md §4's clickable sample were actually materialised. It differs "
        "from the requested size by the per-cell rounding, which is a seeded Bernoulli on the "
        "fractional part rather than a rounding rule that would bias the disc's outskirts away."
    ),
)


def compute_systems(ctx: Context) -> Mapping[str, Any]:
    catalogue = materialise(
        ctx.fields, ctx.grid.R, ctx.grid.t, int(ctx.seeds["systems_seed"]), CATALOGUE_SAMPLE
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
        requires=(
            "stellar_surface_density", "thin_disc_surface_density", "thick_disc_surface_density",
            "thin_disc_scale_height", "thick_disc_scale_height",
            "sfr_surface_density_history", "feh_history", "last_major_merger_time",
        ),
        publishes=(
            STAR_RADIUS, STAR_AZIMUTH, STAR_HEIGHT, STAR_AGE, STAR_METALLICITY,
            STAR_MASS, STAR_POPULATION, CATALOGUE_SIZE,
        ),
    )
)
