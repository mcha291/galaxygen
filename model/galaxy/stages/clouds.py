"""Molecular clouds: the ISM's molecular gas as a census of objects (checkpoint 5, S32, BUILD_II Phase 8).

The galaxy scale and the nebula scale are six orders of magnitude apart, so the model does not
make pillars or filaments. It makes a **catalogue of clouds**, each carrying the parameter vector
from which a renderer synthesises the interior on demand (RENDER_PHYSICS.md §5a): mass, size,
Mach number, the direction its embedded source sits in, the direction its density runs, its age
and state, its abundances. Clouds are an **object class beside stars** — ``FieldDecl(kind=COLUMN,
of="cloud")`` — drawn per cell by the same cell-and-index machinery, so that a region's clouds are
a sweep's clouds (D60). They are a **census, not a sample**: every cloud above the smallest mass
the function is drawn from exists, and a region query filters rather than resizes.

**The rulings (S32, made before any number was read, rule D113), each a level-0 constant with its
source in the about line; nothing here is recalled (rule B9).**

- *Mass function* — Rice et al. 2016's truncated power law, dN/dM ∝ M^γ up to M₀, with the inner
  Galaxy's (γ −1.6, M₀ 10⁷) inside the solar radius and the outer Galaxy's (−2.2, 1.5 × 10⁶) outside;
  drawn from a smallest mass of 10⁴ M☉ that no source fixed ``[inferred]``. **All of the ISM's
  molecular gas is in clouds**: each cell's expected cloud count is its molecular mass over the
  law's mean cloud mass, so the mass in clouds integrates back to the ISM's molecular mass
  (RENDER_PHYSICS §7's redistribution rule for clouds) — the diffuse fraction is zero by
  construction, and Rice et al.'s finding that catalogued clouds hold 25% of the Milky Way's H₂ is
  what that construction stands against (debt #94).
- *Size* — a constant surface density, Heyer et al. 2009's 42 M☉ pc⁻²: R = √(M/πΣ).
- *Velocity dispersion* — Heyer et al. 2009's eq. 10, σ_v = (πGΣ/5)^½ R^½, the virial relation at
  that surface density; the Mach number is σ_v over the sound speed of 10 K molecular gas.
- *Density PDF* — the renderer's log-normal width is σ_s² = ln(1 + b²ℳ²) (Federrath et al.); b is
  published as a scalar, and σ_s per cloud as a column so the renderer computes nothing (D5, A9).
- *Age and state* — a steady population: age uniform over the 26 Myr lifetime Kawamura et al. 2009's
  three phases sum to, the state the phase the age falls in: **embedded** (no massive star formation,
  6 Myr), **blown open** (HII regions, 13 Myr), **dispersing** (HII regions and exposed clusters,
  7 Myr). No *remnant* state: a dispersed cloud is not molecular gas, and no source gave the phase a
  duration (debt #95).
- *What no source gives* — the offset of the embedded source from the cloud's centre and the
  direction and steepness of the cloud's density gradient are seeded draws with the distribution
  stated and tagged ``[inferred]``: the source uniformly inside the cloud's volume, the gradient's
  direction uniform and its steepness uniform on [0, 1]. So is the cloud's height, a sech² layer at
  half the thin disc's scale height (debt #95).
- *Where* — radius inverted from Σ_H₂ within the cell's ring, azimuth from the pattern's density
  contrast within the sector exactly as a star's is (gas follows the pattern in both models);
  abundances read off the gas at the cloud's radius.

**Which cloud is which.** A cloud is named ``(cell, index)`` as a star is, on the same cell grid;
its stream is ``(systems_seed, "cloud", cell, …)``, so rerolling the systems seed rerolls the clouds
with the stars (one checkpoint, one seed) and nothing earlier. Every table this stage builds covers
every ring and sector whatever a request asked for (D60).
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
from galaxy.stages.pattern import ArmPattern
from galaxy.stages.systems import (
    CELL_COUNT,
    CELL_RINGS,
    CELL_SECTORS,
    Catalogue,
    cell_edges,
    invert_cdf,
    sech2_height,
)

CLOUD_STATES: tuple[str, ...] = ("embedded", "blown_open", "dispersing")

# Boltzmann's constant over the proton mass, in (km/s)^2 per kelvin: the sound speed squared of
# gas at temperature T and mean particle mass mu is K_OVER_MH * T / mu. SI 2019 exact k and the
# CODATA proton mass [recall: 1.380649e-23 J/K, 1.67262e-27 kg].
K_OVER_MH = 1.380649e-23 / 1.67262192e-27 / 1.0e6  # (km/s)^2 / K
G_PC = 4.300917270e-3  # G in pc (km/s)^2 / Msun: the model's G (kpc units) times 1000


# --- the mass function ---------------------------------------------------------------------------


def mass_function_mean(slope: float, m_min: float, m_max: float) -> float:
    """⟨M⟩ of dN/dM ∝ M^slope on [m_min, m_max]: ∫M^(slope+1) over ∫M^slope, both in closed form."""
    a, b = slope + 1.0, slope + 2.0
    number = (m_max**a - m_min**a) / a
    mass = (m_max**b - m_min**b) / b if b != 0.0 else math.log(m_max / m_min)
    return mass / number


def mass_function_sample(u: np.ndarray, slope: float, m_min: float, m_max: float) -> np.ndarray:
    """Masses by inverse CDF of the truncated power law — counted, never rejected (rule B8)."""
    a = slope + 1.0
    lo, hi = m_min**a, m_max**a
    return (lo + np.asarray(u, dtype=float) * (hi - lo)) ** (1.0 / a)


def cloud_radius_pc(mass: np.ndarray, surface_density: float) -> np.ndarray:
    """R = √(M / πΣ) in pc for a cloud of constant surface density Σ (M☉ pc⁻²)."""
    return np.sqrt(np.asarray(mass, dtype=float) / (math.pi * surface_density))


def velocity_dispersion(radius_pc: np.ndarray, surface_density: float) -> np.ndarray:
    """Heyer et al. 2009 eq. 10: σ_v = (πGΣ/5)^½ R^½, in km/s for R in pc and Σ in M☉ pc⁻²."""
    return np.sqrt(math.pi * G_PC * surface_density / 5.0) * np.sqrt(np.asarray(radius_pc, dtype=float))


def sound_speed(temperature: float, mean_weight: float) -> float:
    """Isothermal sound speed √(kT/μ m_H) in km/s."""
    return math.sqrt(K_OVER_MH * temperature / mean_weight)


def state_of(age_myr: np.ndarray, phases: Sequence[float]) -> np.ndarray:
    """The phase index an age falls in, the phases' durations in order (Kawamura et al. 2009)."""
    edges = np.cumsum(np.asarray(phases, dtype=float))
    return np.clip(np.searchsorted(edges, np.asarray(age_myr, dtype=float), side="right"), 0, len(phases) - 1).astype(np.int64)


# --- the census ------------------------------------------------------------------------------------


def ring_molecular_mass(sigma_h2: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Molecular mass per cell ring, M☉: Σ_H₂ (M☉ pc⁻²) integrated over each ring's annulus."""
    edges, _ = cell_edges(R)
    weight = np.asarray(sigma_h2, dtype=float) * PC_PER_KPC**2 * 2.0 * math.pi * R
    return np.array([
        float(np.trapezoid(np.where((R >= edges[i]) & (R <= edges[i + 1]), weight, 0.0), R))
        for i in range(CELL_RINGS)
    ])


def law_for(radius_kpc: float, c: Mapping[str, float]) -> tuple[float, float, float]:
    """(slope, m_min, m_max) of the mass function that applies at a radius: inner or outer Galaxy."""
    if radius_kpc < float(c["R_SUN"]):
        return float(c["GMC_MASS_SLOPE_INNER"]), float(c["GMC_MASS_MIN"]), float(c["GMC_MASS_TRUNCATION_INNER"])
    return float(c["GMC_MASS_SLOPE_OUTER"]), float(c["GMC_MASS_MIN"]), float(c["GMC_MASS_TRUNCATION_OUTER"])


def expected_counts(fields: Mapping[str, Any], R: np.ndarray, constants: Mapping[str, float]) -> np.ndarray:
    """The expected number of clouds in every cell, (rings, sectors): the cell's molecular mass over
    the law's mean cloud mass at the ring's radius. A population integral, whatever a request asked for."""
    rings, sectors = cell_edges(R)
    ring_mass = ring_molecular_mass(fields["gas_molecular_surface_density"], R)
    pattern = ArmPattern.from_fields(fields)
    weights = (
        np.ones((CELL_RINGS, CELL_SECTORS))
        if pattern is None or pattern.flat
        else np.array([pattern.sector_means(0.5 * (rings[i] + rings[i + 1]), sectors) for i in range(CELL_RINGS)])
    )
    mean = np.array([mass_function_mean(*law_for(0.5 * (rings[i] + rings[i + 1]), constants)) for i in range(CELL_RINGS)])
    return ring_mass[:, None] / mean[:, None] / CELL_SECTORS * np.maximum(weights, 0.0)


def cloud_counts(expected: np.ndarray, seed: int, cells: Sequence[int] | None = None) -> tuple[tuple[int, int], ...]:
    """``(cell, count)`` for every cell that realises a cloud: a Poisson draw on the cell's own stream.

    A census has a physical number, so the count is Poisson in the expectation rather than a share of a
    requested sample; one stream per cell, so a cell drawn alone is the cell drawn in any set (D60).
    """
    wanted = range(CELL_COUNT) if cells is None else cells
    out: list[tuple[int, int]] = []
    for cell in wanted:
        ring, sector = divmod(int(cell), CELL_SECTORS)
        lam = float(expected[ring, sector])
        count = int(_seeds.rng(seed, "cloud", int(cell), "count").poisson(lam)) if lam > 0.0 else 0
        if count:
            out.append((int(cell), count))
    return tuple(out)


CLOUD_COLUMNS: tuple[str, ...] = (
    "cloud_radius", "cloud_azimuth", "cloud_height", "cloud_mass", "cloud_size",
    "cloud_velocity_dispersion", "cloud_mach_number", "cloud_density_pdf_width",
    "cloud_age", "cloud_source_offset", "cloud_source_angle", "cloud_density_gradient",
    "cloud_gradient_angle", "cloud_metallicity", "cloud_alpha",
)


def materialise_clouds(
    fields: Mapping[str, Any],
    R: np.ndarray,
    seed: int,
    constants: Mapping[str, float],
    cells: Sequence[int] | None = None,
) -> Catalogue:
    """The clouds of ``cells`` (every cell when None), exactly the clouds a full sweep would give (D60)."""
    c = constants
    rings, sectors = cell_edges(R)
    expected = expected_counts(fields, R, c)
    counts = cloud_counts(expected, seed, cells)
    pattern = ArmPattern.from_fields(fields)
    sigma = float(c["GMC_SURFACE_DENSITY"])
    c_s = sound_speed(float(c["MOLECULAR_GAS_TEMPERATURE"]), float(c["MOLECULAR_MEAN_WEIGHT"]))
    b = float(c["TURBULENCE_FORCING_B"])
    phases = (float(c["GMC_PHASE_EMBEDDED"]), float(c["GMC_PHASE_BLOWN_OPEN"]), float(c["GMC_PHASE_DISPERSING"]))
    lifetime = sum(phases)
    h_cloud = 0.5 * float(fields["thin_disc_scale_height"]) / PC_PER_KPC  # kpc, half the thin disc's [inferred]
    sigma_h2 = np.asarray(fields["gas_molecular_surface_density"], dtype=float)
    feh_gas = np.asarray(fields["feh_gas"], dtype=float)
    alpha_gas = np.asarray(fields["alpha_fe_gas"], dtype=float)
    width = 2.0 * math.pi / CELL_SECTORS

    columns: dict[str, list[np.ndarray]] = {}
    states: list[np.ndarray] = []
    for cell, count in counts:
        ring, sector = divmod(int(cell), CELL_SECTORS)

        def draw(name: str, k: int = count) -> np.ndarray:
            return _seeds.rng(seed, "cloud", int(cell), name).random(k)

        lo, hi = rings[ring], rings[ring + 1]
        weight = np.where((R >= lo) & (R <= hi), sigma_h2 * R, 0.0)
        radius = invert_cdf(draw("radius"), R, weight) if weight.sum() > 0.0 else np.full(count, 0.5 * (lo + hi))
        if pattern is None or pattern.flat:
            azimuth = (sector + draw("azimuth")) * width
        else:
            azimuth = pattern.azimuths(draw("azimuth"), radius, sector * width, (sector + 1) * width)
        slope, m_min, m_max = law_for(0.5 * (lo + hi), c)
        mass = mass_function_sample(draw("mass"), slope, m_min, m_max)
        size = cloud_radius_pc(mass, sigma)
        disp = velocity_dispersion(size, sigma)
        mach = disp / c_s
        age = draw("age") * lifetime
        columns.setdefault("cloud_radius", []).append(radius)
        columns.setdefault("cloud_azimuth", []).append(azimuth)
        columns.setdefault("cloud_height", []).append(sech2_height(draw("height"), h_cloud))
        columns.setdefault("cloud_mass", []).append(mass)
        columns.setdefault("cloud_size", []).append(size)
        columns.setdefault("cloud_velocity_dispersion", []).append(disp)
        columns.setdefault("cloud_mach_number", []).append(mach)
        columns.setdefault("cloud_density_pdf_width", []).append(np.sqrt(np.log1p(b * b * mach * mach)))
        columns.setdefault("cloud_age", []).append(age)
        columns.setdefault("cloud_source_offset", []).append(size * np.cbrt(draw("source_offset")))
        columns.setdefault("cloud_source_angle", []).append(2.0 * math.pi * draw("source_angle"))
        columns.setdefault("cloud_density_gradient", []).append(draw("gradient"))
        columns.setdefault("cloud_gradient_angle", []).append(2.0 * math.pi * draw("gradient_angle"))
        columns.setdefault("cloud_metallicity", []).append(np.interp(radius, R, feh_gas))
        columns.setdefault("cloud_alpha", []).append(np.interp(radius, R, alpha_gas))
        states.append(state_of(age, phases))

    if not columns:
        empty = np.zeros(0)
        return Catalogue.of({n: empty for n in CLOUD_COLUMNS} | {"cloud_state": empty.astype(np.int64)}, counts)
    out: dict[str, Any] = {name: np.concatenate(parts) for name, parts in columns.items()}
    out["cloud_state"] = np.concatenate(states)
    return Catalogue.of(out, counts)


# --- declarations ----------------------------------------------------------------------------------


def _column(name: str, label: str, unit: str, about: str, ramp: Ramp = Ramp("viridis")) -> FieldDecl:
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="cloud",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about)


CLOUD_RADIUS = _column("cloud_radius", "Galactocentric radius", "kpc",
                       "Drawn by inverting the molecular surface density within the cloud's cell ring, as a "
                       "star's radius inverts the stellar one: the census traces the ISM's molecular gas exactly.")
CLOUD_AZIMUTH = _column("cloud_azimuth", "Azimuth", "rad",
                        "Drawn from the bar and arm density contrast at the cloud's radius, inside its sector, so "
                        "clouds crowd into the arms as the gas does; the same rule in both models.")
CLOUD_HEIGHT = _column("cloud_height", "Height above the plane", "kpc",
                       "A sech² layer at half the thin disc's scale height, a stated guess: no source for the "
                       "molecular layer's thickness was read (debt #95).")
CLOUD_MASS = _column("cloud_mass", "Cloud mass", "Msun",
                     "Inverse of the truncated power-law mass function that applies at the cloud's radius: the "
                     "inner Galaxy's slope and truncation inside the solar radius, the outer's beyond it (Rice et "
                     "al. 2016), from a smallest mass no source fixed. The census's total mass integrates back to "
                     "the ISM's molecular mass, to within the Poisson noise of the count.",
                     ramp=Ramp("magma", scale="log"))
CLOUD_SIZE = _column("cloud_size", "Cloud radius", "pc",
                     "√(M/πΣ) at one surface density for every cloud, Heyer et al. 2009's median; a renderer "
                     "reads mass over this for the mean density.", ramp=Ramp("viridis", scale="log"))
CLOUD_DISPERSION = _column("cloud_velocity_dispersion", "Velocity dispersion σ_v", "km/s",
                           "Heyer et al. 2009's size-linewidth relation at the cloud's surface density and "
                           "radius: the virial dispersion of a cloud that size.")
CLOUD_MACH = _column("cloud_mach_number", "Mach number", "dimensionless",
                     "σ_v over the sound speed of 10 K molecular gas. It sets the width of the log-normal density "
                     "distribution the renderer synthesises the interior from: mean density alone is fog.")
CLOUD_PDF_WIDTH = _column("cloud_density_pdf_width", "Density PDF width σ_s", "dimensionless",
                          "√ln(1 + b²ℳ²): the standard deviation of ln(ρ/ρ̄) in a turbulent cloud, from the Mach "
                          "number and the published forcing parameter, so the renderer computes nothing (D5).")
CLOUD_AGE = _column("cloud_age", "Cloud age", "Myr",
                    "Uniform over the lifetime the three sourced phases sum to — a steady population, in which "
                    "a field shows regions at every stage side by side.")
CLOUD_STATE = FieldDecl(
    name="cloud_state", label="Cloud state", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="cloud", categories=CLOUD_STATES, ramp=Palette(("#3a3f8f", "#e07b39", "#f2d16b")), provenance="seeded",
    about=(
        "Which of Kawamura et al. 2009's phases the cloud's age falls in: embedded (no massive star "
        "formation yet), blown open (HII regions inside it), dispersing (HII regions and exposed young "
        "clusters). A dispersed remnant is not molecular gas and has no sourced duration, so it is not a state."
    ),
)
CLOUD_SOURCE_OFFSET = _column("cloud_source_offset", "Embedded source offset", "pc",
                              "How far from the cloud's centre its embedded cluster sits, drawn uniformly over "
                              "the cloud's volume: pillars are the shadows of clumps that survived the ionization "
                              "front eating the cloud from one side, so this is what makes them point one way. No "
                              "source gives the distribution (debt #95).")
CLOUD_SOURCE_ANGLE = _column("cloud_source_angle", "Embedded source direction", "rad",
                             "The direction from the cloud's centre to its embedded source, in the plane, uniform.")
CLOUD_GRADIENT = _column("cloud_density_gradient", "Density gradient", "dimensionless",
                         "How steeply the cloud's density runs across it, 0 flat to 1 the whole contrast over one "
                         "radius, drawn uniform: bubbles sit off-centre because they expand into a gradient. No "
                         "source gives the distribution (debt #95).")
CLOUD_GRADIENT_ANGLE = _column("cloud_gradient_angle", "Density gradient direction", "rad",
                               "The direction the density increases in, in the plane, uniform.")
CLOUD_METALLICITY = _column("cloud_metallicity", "[Fe/H]", "dex",
                            "The present-day gas iron abundance at the cloud's radius: what the stars it makes "
                            "are born with, and what sets its dust.", ramp=Ramp("plasma"))
CLOUD_ALPHA = _column("cloud_alpha", "[α/Fe]", "dex",
                      "The present-day gas α-to-iron ratio at the cloud's radius, for the oxygen its lines need.",
                      ramp=Ramp("plasma"))

CLOUD_COUNT_TOTAL = FieldDecl(
    name="cloud_count_total", label="Clouds in the galaxy", unit="count", kind=Kind.SCALAR, meaningful_zero=True,
    provenance="seeded",
    about=(
        "The expected number of clouds, summed over every cell: each cell's molecular mass over the mass "
        "function's mean cloud mass at its radius. A population integral, not the count of a draw; the "
        "census realises it to within Poisson noise."
    ),
)
CLOUD_MASS_TOTAL = FieldDecl(
    name="cloud_mass_total", label="Molecular mass in clouds", unit="Msun", kind=Kind.SCALAR, meaningful_zero=True,
    provenance="seeded",
    about=(
        "The mass the realised census holds. It is the ISM's molecular mass to within the Poisson noise of "
        "the count, because every cell's expected count is its molecular mass over the mean cloud mass: a "
        "redistribution, not a new reservoir. The whole molecular gas is in clouds by construction, which is "
        "the construction debt #94 names."
    ),
)
CLOUD_FORCING = FieldDecl(
    name="cloud_forcing_parameter", label="Turbulence forcing parameter b", unit="dimensionless", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The b in σ_s² = ln(1 + b²ℳ²), a level-0 constant published as a scalar because the renderer that "
        "synthesises a cloud's interior reads it and the API serves no constants (D180's rule)."
    ),
)
CLOUD_LIFETIME = FieldDecl(
    name="cloud_lifetime", label="Cloud lifetime", unit="Myr", kind=Kind.SCALAR, meaningful_zero=True,
    provenance="seeded",
    about="The sum of the three sourced phases, 26 Myr: the span a cloud's age is drawn over.",
)


def compute_clouds(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    catalogue = materialise_clouds(ctx.fields, R, int(ctx.seeds["systems_seed"]), c)
    expected = expected_counts(ctx.fields, R, c)
    return {
        **catalogue,
        "cloud_count_total": float(expected.sum()),
        "cloud_mass_total": float(np.sum(catalogue["cloud_mass"])),
        "cloud_forcing_parameter": float(c["TURBULENCE_FORCING_B"]),
        "cloud_lifetime": float(c["GMC_PHASE_EMBEDDED"]) + float(c["GMC_PHASE_BLOWN_OPEN"]) + float(c["GMC_PHASE_DISPERSING"]),
    }


CLOUDS = IMPLEMENTATIONS.register(
    Stage(
        id="clouds", slot="clouds", checkpoint=5,
        about=(
            "The molecular-cloud census: every cloud the ISM's molecular gas makes, drawn per cell on the "
            "star catalogue's grid with the parameter vector a renderer synthesises the interior from."
        ),
        compute=compute_clouds,
        reads_seeds=("systems_seed",),
        reads_constants=(
            "R_SUN", "GMC_MASS_SLOPE_INNER", "GMC_MASS_TRUNCATION_INNER", "GMC_MASS_SLOPE_OUTER",
            "GMC_MASS_TRUNCATION_OUTER", "GMC_MASS_MIN", "GMC_SURFACE_DENSITY", "MOLECULAR_GAS_TEMPERATURE",
            "MOLECULAR_MEAN_WEIGHT", "TURBULENCE_FORCING_B", "GMC_PHASE_EMBEDDED", "GMC_PHASE_BLOWN_OPEN",
            "GMC_PHASE_DISPERSING",
        ),
        requires=(
            "gas_molecular_surface_density", "thin_disc_scale_height", "feh_gas", "alpha_fe_gas",
            "arm_contrast", "bar_contrast", "arm_multiplicity", "pitch_angle", "bar_half_length",
        ),
        publishes=(
            CLOUD_RADIUS, CLOUD_AZIMUTH, CLOUD_HEIGHT, CLOUD_MASS, CLOUD_SIZE, CLOUD_DISPERSION, CLOUD_MACH,
            CLOUD_PDF_WIDTH, CLOUD_AGE, CLOUD_STATE, CLOUD_SOURCE_OFFSET, CLOUD_SOURCE_ANGLE, CLOUD_GRADIENT,
            CLOUD_GRADIENT_ANGLE, CLOUD_METALLICITY, CLOUD_ALPHA,
            CLOUD_COUNT_TOTAL, CLOUD_MASS_TOTAL, CLOUD_FORCING, CLOUD_LIFETIME,
        ),
    )
)
