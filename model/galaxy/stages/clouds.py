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
  direction and steepness of the cloud's density gradient are draws with the distribution
  stated and tagged ``[inferred]``: the source uniformly inside the cloud's volume, the gradient's
  direction uniform and its steepness uniform on [0, 1]. **Since S55 (D214, BUILD_III Appendix B) these
  four are the randomness layer's**: synthetic, published by its stage ``cloud_texture``
  (``galaxy/layer/cloud_texture.py``), drawn on the same streams as before and zero with the layer off;
  a census materialised here carries them through ``galaxy.layer.compose``. The cloud's height, a sech²
  layer at half the thin disc's scale height, stays this stage's seeded draw (debt #95).
- *Where* — radius inverted from Σ_H₂ within the cell's ring; each cell's expected count, and each
  cloud's azimuth inside its sector, from the gas's own density contrast (``gas_pattern``,
  ``GasPattern``, S51, D210) — a narrow ridge on the stellar arm's crest, not the stars' broader
  arm, in both models — by the same sector means and inverse CDF a star's azimuth uses; abundances
  read off the gas at the cloud's radius. The contrast averages to 1 round every ring, so a ring's
  expected count is what it was: the clouds move round the ring, not in number.

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
from galaxy.layer import compose as _compose
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.dust import SOLAR_MASS_G
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
# The states whose cloud holds a star cluster (S33, BUILD_II Phase 11, ruling (d)): past the embedded
# phase, the two in which Kawamura et al. 2009 see HII regions, so massive stars have formed.
CLUSTER_HOSTING_STATES: tuple[str, ...] = ("blown_open", "dispersing")

# Boltzmann's constant over the proton mass, in (km/s)^2 per kelvin: the sound speed squared of
# gas at temperature T and mean particle mass mu is K_OVER_MH * T / mu. SI 2019 exact k and the
# CODATA proton mass [verified: CODATA 2018, k = 1.380649e-23 J/K exact (SI 2019) and
# m_p = 1.67262192e-27 kg, read at S43].
K_OVER_MH = 1.380649e-23 / 1.67262192e-27 / 1.0e6  # (km/s)^2 / K
G_PC = 4.300917270e-3  # G in pc (km/s)^2 / Msun: the model's G (kpc units) times 1000
# The clouds' layer: a sech² at this share of the thin disc's scale height, a stated guess with no
# source (debt #95) [inferred]. Named at S39 so the render's HII layer reads this one number (A9).
CLOUD_LAYER_SHARE = 0.5


def cloud_layer_height(thin_disc_scale_height_pc: float) -> float:
    """The clouds' sech² scale height, kpc, from the thin disc's (pc)."""
    return CLOUD_LAYER_SHARE * float(thin_disc_scale_height_pc) / PC_PER_KPC


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


def cluster_indices(state: np.ndarray) -> np.ndarray:
    """Per cloud of one cell, in the cell's order: the index its cluster has among the cell's clusters,
    or -1 where the cloud holds none. A cell's clusters are its hosting clouds' in the same order (S33)."""
    hosts = np.isin(np.asarray(state), [CLOUD_STATES.index(s) for s in CLUSTER_HOSTING_STATES])
    return np.where(hosts, np.cumsum(hosts) - 1, -1).astype(float)


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
    the law's mean cloud mass at the ring's radius, shared among the ring's sectors by the gas's own
    contrast averaged over each (S51, D210). A population integral, whatever a request asked for."""
    rings, sectors = cell_edges(R)
    ring_mass = ring_molecular_mass(fields["gas_molecular_surface_density"], R)
    # The gas's pattern, from compose (S55, D214): none with the layer off, and every sector of a ring then
    # expects the same number of clouds. The ring's *expected* total is the same either way (invariant I2); the
    # realised clouds are each cell's own Poisson draw at its own expectation, so they are another draw (until L1).
    pattern = _compose.gas_pattern(fields, constants)
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
# The four columns the randomness layer realises and its stage ``cloud_texture`` publishes (S55, D214 section 5;
# BUILD_III Appendix B): where a cloud's embedded source sits and how its density leans. Until S55 this stage
# drew and published them as seeded; the draws - their seed, their streams, their values - are unchanged, and
# live in ``galaxy/layer/cloud_texture.py``. A census materialised here still carries them (the cluster census
# and ``/api/clouds`` read whole clouds), obtained through ``galaxy.layer.compose``.
TEXTURE_COLUMNS: tuple[str, ...] = (
    "cloud_source_offset", "cloud_source_angle", "cloud_density_gradient", "cloud_gradient_angle",
)
# Every column of a cloud on the wire, in the order ``/api/clouds`` has always sent them: this stage's own with the
# layer's four where they stood before S55, so a response's columns did not move when their publisher did.
WIRE_COLUMNS: tuple[str, ...] = (
    "cloud_radius", "cloud_azimuth", "cloud_height", "cloud_mass", "cloud_size", "cloud_velocity_dispersion",
    "cloud_mach_number", "cloud_density_pdf_width", "cloud_age", "cloud_state", "cloud_source_offset",
    "cloud_source_angle", "cloud_density_gradient", "cloud_gradient_angle", "cloud_metallicity", "cloud_alpha",
    "cloud_cluster_index",
)

# The dust's V-band extinction cross-section per hydrogen atom, cm^2/H: the grain table's own V row
# (Draine 2003, R_V 3.1; spectra.GRAIN_TABLE, D189), the one number that turns a column density
# into magnitudes, A_V = 1.086 N_H C_ext(V). Read here so the census publishes each cloud's A_V (S40, V3).
MAG_PER_OPTICAL_DEPTH = 2.5 / math.log(10.0)  # 1.0857: a definition
PROTON_MASS_G = 1.67262192e-24
CM_PER_PC_ = 3.0856775814913673e18


def _grain_v_extinction() -> float:
    """C_ext(V)/H from the grain table (spectra.GRAIN_V_EXTINCTION), imported at call time: spectra is the
    render side and clouds the census; neither imports the other at module load."""
    from galaxy.stages.spectra import GRAIN_V_EXTINCTION

    return float(GRAIN_V_EXTINCTION)


def central_extinction_v(mass_msun: np.ndarray, radius_pc: np.ndarray, mass_per_h: float, c_ext_v: float) -> np.ndarray:
    """A_V (mag) face-on through the centre of a uniform sphere of this mass and radius: the column
    N_H = 2 r rho / (mu m_H) with rho = 3 M / (4 pi r^3), times 1.086 C_ext(V). Uniform, so a mean-density
    figure: the log-normal interior a renderer synthesises around it keeps the same mean column
    (RENDER_PHYSICS section 6) [inferred: the geometry]."""
    r_cm = np.asarray(radius_pc, dtype=float) * CM_PER_PC_
    with np.errstate(divide="ignore", invalid="ignore"):
        n_h = 3.0 * np.asarray(mass_msun, dtype=float) * SOLAR_MASS_G / (2.0 * math.pi * r_cm**2 * mass_per_h * PROTON_MASS_G)
    return MAG_PER_OPTICAL_DEPTH * c_ext_v * np.where(np.isfinite(n_h), n_h, 0.0)


def materialise_clouds(
    fields: Mapping[str, Any],
    R: np.ndarray,
    seed: int,
    constants: Mapping[str, float],
    cells: Sequence[int] | None = None,
    *,
    texture: bool = True,
) -> Catalogue:
    """The clouds of ``cells`` (every cell when None), exactly the clouds a full sweep would give (D60).

    ``texture`` says whether the census carries the randomness layer's four columns (``TEXTURE_COLUMNS``): a
    whole cloud does, which is what the cluster census and the API read; the ``clouds`` stage publishes its own
    columns only and passes False, the layer's stage publishing the four (S55, D214 section 5)."""
    c = constants
    rings, sectors = cell_edges(R)
    expected = expected_counts(fields, R, c)
    counts = cloud_counts(expected, seed, cells)
    pattern = _compose.gas_pattern(fields, c)  # the gas's own ridge places the clouds (S51, D210); none, layer off
    sigma = float(c["GMC_SURFACE_DENSITY"])
    c_s = sound_speed(float(c["MOLECULAR_GAS_TEMPERATURE"]), float(c["MOLECULAR_MEAN_WEIGHT"]))
    b = float(c["TURBULENCE_FORCING_B"])
    phases = (float(c["GMC_PHASE_EMBEDDED"]), float(c["GMC_PHASE_BLOWN_OPEN"]), float(c["GMC_PHASE_DISPERSING"]))
    lifetime = sum(phases)
    h_cloud = cloud_layer_height(fields["thin_disc_scale_height"])  # kpc, half the thin disc's [inferred]
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
        columns.setdefault("cloud_metallicity", []).append(np.interp(radius, R, feh_gas))
        columns.setdefault("cloud_alpha", []).append(np.interp(radius, R, alpha_gas))
        states.append(state_of(age, phases))
        columns.setdefault("cloud_cluster_index", []).append(cluster_indices(states[-1]))

    own = tuple(n for n in CLOUD_COLUMNS if n not in TEXTURE_COLUMNS)
    if not columns:
        empty = np.zeros(0)
        out: dict[str, Any] = {n: empty for n in own} | {"cloud_cluster_index": empty, "cloud_state": empty.astype(np.int64)}
    else:
        out = {name: np.concatenate(parts) for name, parts in columns.items()}
        out["cloud_state"] = np.concatenate(states)
    if texture:
        # The layer's four columns for these cells (S55): the same streams as ever with the layer on, zero with
        # it off. compose decides which, from the run the fields belong to.
        out.update(_compose.cloud_texture(fields, seed, counts, out["cloud_size"]))
    return Catalogue.of(out, counts)


# --- declarations ----------------------------------------------------------------------------------


# S41 (V4, D191): the cloud columns the viewer does not read, each with why - the object-class twin of the
# sentence a catalogue stage's scalars carry under rule D4 (debt #69). A column reaches the picture through what
# it sets, or nothing in a filter's image can see it; tests/test_v4.py holds the inventory and asserts the sentence.
NOT_DRAWN_WHY: dict[str, str] = {
    "cloud_velocity_dispersion": "it reaches the picture as the log-normal width it sets (`cloud_density_pdf_width`); "
                                 "a linewidth itself needs a spectral resolution the render has not.",
    "cloud_mach_number": "it reaches the picture as `cloud_density_pdf_width`, the width the interior is synthesised "
                         "at; the number is not a look.",
    "cloud_age": "an age has no look of its own; it is drawn through what it sets - the cloud's state, whether it "
                 "holds a cluster, and that cluster's light, region and bubble.",
    "cloud_state": "the state is drawn through what it sets: a cloud past its embedded phase holds a cluster "
                   "(`cloud_cluster_index`), whose cavity, HII sphere and point of light the viewer draws; the "
                   "category itself is not a look.",
    # cloud_source_offset and cloud_source_angle: with their declarations, galaxy/layer/cloud_texture.py (S55).
    "cloud_metallicity": "no line comes from molecular gas in the render; the abundance reaches the picture through "
                         "the cluster's light (the isochrones at its [Fe/H]) and its HII region's emissivity at the "
                         "temperature the oxygen sets.",
    "cloud_alpha": "as the iron abundance: through the HII region's oxygen, its temperature and so its emissivity, "
                   "and through the forbidden lines when a photoionization grid publishes them.",
}


def _not_drawn(name: str) -> str:
    why = NOT_DRAWN_WHY.get(name)
    return f" **Not drawn by the viewer** (D191): {why}" if why else ""


def _column(name: str, label: str, unit: str, about: str, ramp: Ramp = Ramp("viridis")) -> FieldDecl:
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="cloud",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about + _not_drawn(name))


CLOUD_RADIUS = _column("cloud_radius", "Galactocentric radius", "kpc",
                       "Drawn by inverting the molecular surface density within the cloud's cell ring, as a "
                       "star's radius inverts the stellar one: the census traces the ISM's molecular gas exactly.")
CLOUD_AZIMUTH = _column("cloud_azimuth", "Azimuth", "rad",
                        "Drawn from the gas's own density contrast at the cloud's radius, inside its sector — a "
                        "narrow ridge on the stellar arm's crest, and the stellar bar's term inside the bar — so "
                        "clouds crowd onto the arms' spines as the gas does, and each sector's share of clouds "
                        "follows the same contrast; the same rule in both models.")
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
        + _not_drawn("cloud_state")
    ),
)
# The embedded source's offset and direction and the density gradient's steepness and direction were declared
# here until S55; they are the randomness layer's (BUILD_III Appendix B) and are declared, drawn and published in
# galaxy/layer/cloud_texture.py, synthetic, each with what it stands in for, what it conserves and its statistic.
CLOUD_METALLICITY = _column("cloud_metallicity", "[Fe/H]", "dex",
                            "The present-day gas iron abundance at the cloud's radius: what the stars it makes "
                            "are born with, and what sets its dust.", ramp=Ramp("plasma"))
CLOUD_ALPHA = _column("cloud_alpha", "[α/Fe]", "dex",
                      "The present-day gas α-to-iron ratio at the cloud's radius, for the oxygen its lines need.",
                      ramp=Ramp("plasma"))

CLOUD_EXTINCTION_V = FieldDecl(
    name="cloud_extinction_v", label="A cloud's central extinction A_V", unit="mag", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The V-band extinction face-on through a cloud's centre: the column of a uniform sphere at the census's "
        "one surface density (Heyer et al. 2009's 42 solar masses per square parsec, so it is the same for "
        "every cloud - a scalar, not a column), 1.4 proton masses per hydrogen, times the grain table's V "
        "cross-section per hydrogen (Draine 2003, the dust stage's own table): 3.0 mag. What a renderer darkens "
        "a cloud by before it makes the interior log-normal at the published width, which keeps the mean column "
        "(RENDER_PHYSICS section 6); a cloud's centre is opaque at the pillars' scale, not at the disc's. "
        "**Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage that "
        "publishes the cloud columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the `/api/clouds` "
        "header carries it under `scalars`."
    ),
)
CLOUD_CLUSTER_INDEX = _column("cloud_cluster_index", "Its cluster's index", "dimensionless",
                              "Which star cluster of the cloud's own cell the cloud holds, by that cluster's index "
                              "in the cell (the cluster census names a cluster by cell and index, as stars are "
                              "named), or -1 for none: a cloud holds one cluster once it is past its embedded "
                              "phase, when its HII regions say massive stars have formed.",
                              ramp=Ramp("viridis", lo=-1.0))

CLOUD_COUNT_TOTAL = FieldDecl(
    name="cloud_count_total", label="Clouds in the galaxy", unit="count", kind=Kind.SCALAR, meaningful_zero=True,
    provenance="seeded",
    about=(
        "The expected number of clouds, summed over every cell: each cell's molecular mass over the mass "
        "function's mean cloud mass at its radius. A population integral, not the count of a draw; the "
        "census realises it to within Poisson noise. "
        "**Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage that publishes the cloud columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the `/api/clouds` header carries the count, b and the lifetime under `scalars`."
    ),
)
CLOUD_MASS_TOTAL = FieldDecl(
    name="cloud_mass_total", label="Molecular mass in clouds", unit="Msun", kind=Kind.SCALAR, meaningful_zero=True,
    provenance="seeded",
    about=(
        "The mass the realised census holds. It is the ISM's molecular mass to within the Poisson noise of "
        "the count, because every cell's expected count is its molecular mass over the mean cloud mass: a "
        "redistribution, not a new reservoir. The whole molecular gas is in clouds by construction, which is "
        "the construction debt #94 names. "
        "**Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage that publishes the cloud columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the `/api/clouds` header carries the count, b and the lifetime under `scalars`."
    ),
)
CLOUD_FORCING = FieldDecl(
    name="cloud_forcing_parameter", label="Turbulence forcing parameter b", unit="dimensionless", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The b in σ_s² = ln(1 + b²ℳ²), a level-0 constant published as a scalar because the renderer that "
        "synthesises a cloud's interior reads it and the API serves no constants (D180's rule). "
        "**Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage that publishes the cloud columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the `/api/clouds` header carries the count, b and the lifetime under `scalars`."
    ),
)
CLOUD_LIFETIME = FieldDecl(
    name="cloud_lifetime", label="Cloud lifetime", unit="Myr", kind=Kind.SCALAR, meaningful_zero=True,
    provenance="seeded",
    about=(
        "The sum of the three sourced phases, 26 Myr: the span a cloud's age is drawn over. "
        "**Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage that publishes the cloud columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the `/api/clouds` header carries the count, b and the lifetime under `scalars`."
    ),
)


def compute_clouds(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    # The stage's own columns: the layer's four are cloud_texture's to publish (S55, D214 section 5).
    catalogue = materialise_clouds(ctx.fields, R, int(ctx.seeds["systems_seed"]), c, texture=False)
    expected = expected_counts(ctx.fields, R, c)
    return {
        **catalogue,
        "cloud_count_total": float(expected.sum()),
        "cloud_mass_total": float(np.sum(catalogue["cloud_mass"])),
        "cloud_forcing_parameter": float(c["TURBULENCE_FORCING_B"]),
        "cloud_lifetime": float(c["GMC_PHASE_EMBEDDED"]) + float(c["GMC_PHASE_BLOWN_OPEN"]) + float(c["GMC_PHASE_DISPERSING"]),
        # S40 (V3): one A_V for every cloud, the census fixing one surface density; the centre column of a
        # uniform sphere is 3/2 of the mean, so mass and radius cancel to Sigma alone.
        "cloud_extinction_v": float(central_extinction_v(
            np.array([1.0e5]), np.array([cloud_radius_pc(np.array([1.0e5]), float(c["GMC_SURFACE_DENSITY"]))[0]]),
            float(c["HII_MASS_PER_HYDROGEN"]), _grain_v_extinction(),
        )[0]),
    }


CLOUDS = IMPLEMENTATIONS.register(
    Stage(
        id="clouds", slot="clouds", checkpoint=5,
        about=(
            "The molecular-cloud census: every cloud the ISM's molecular gas makes, drawn per cell on the "
            "star catalogue's grid with the parameter vector a renderer synthesises the interior from."
        ),
        compute=compute_clouds,
        placement_reader=True,  # S55 (D214, I4): a census, placed round each ring by the gas's own pattern
        reads_seeds=("systems_seed",),
        reads_constants=(
            "HII_MASS_PER_HYDROGEN",  # S40: the cloud's column density per hydrogen, for its A_V
            "R_SUN", "GMC_MASS_SLOPE_INNER", "GMC_MASS_TRUNCATION_INNER", "GMC_MASS_SLOPE_OUTER",
            "GMC_MASS_TRUNCATION_OUTER", "GMC_MASS_MIN", "GMC_SURFACE_DENSITY", "MOLECULAR_GAS_TEMPERATURE",
            "MOLECULAR_MEAN_WEIGHT", "TURBULENCE_FORCING_B", "GMC_PHASE_EMBEDDED", "GMC_PHASE_BLOWN_OPEN",
            "GMC_PHASE_DISPERSING",
            "GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH",  # S51 (D210): the gas's own ridge places the clouds
        ),
        requires=(
            "gas_molecular_surface_density", "thin_disc_scale_height", "feh_gas", "alpha_fe_gas",
            "gas_arm_contrast", "bar_contrast", "arm_multiplicity", "pitch_angle", "bar_half_length",
        ),
        publishes=(
            CLOUD_RADIUS, CLOUD_AZIMUTH, CLOUD_HEIGHT, CLOUD_MASS, CLOUD_SIZE, CLOUD_DISPERSION, CLOUD_MACH,
            CLOUD_PDF_WIDTH, CLOUD_AGE, CLOUD_STATE, CLOUD_METALLICITY, CLOUD_ALPHA, CLOUD_CLUSTER_INDEX,
            CLOUD_COUNT_TOTAL, CLOUD_MASS_TOTAL, CLOUD_FORCING, CLOUD_LIFETIME, CLOUD_EXTINCTION_V,
        ),
    )
)
