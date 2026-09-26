"""Mechanical feedback: every young cluster's wind- and supernova-blown bubble, the supernova remnants as a census
of objects, and the hot phase they make together (checkpoint 5, S36, BUILD_II Phase 10).

Radiation does not evacuate a cavity; winds and supernovae do. This stage publishes what a renderer needs to draw
the hollow: per cluster (``of="cluster"``, columns beside the HII region's, RENDER_PHYSICS §5b) the bubble's
radius, its shell's velocity, density, thickness and Hα per unit volume (§4: a renderer integrates it along the
ray and the rim limb-brightens by itself), the interior's pressure and temperature; per supernova remnant
(``of="remnant"``, a new object class) the same for the blast wave; and the ratio of their summed volumes to the
gas layer's, ring by ring. The single star's own bubble is a column of the catalogue (``star_bubble_radius``,
``systems.py``). The solutions are in ``feedback.py`` with every sentence they were read from.

**The rulings (S36's brief, D113), and what was chosen inside them.**

- *(a) The cluster's bubble is Weaver et al. 1977's energy-conserving solution*, R = 0.76 (L/ρ₀)^⅕ t^⅗, which
  assumes a constant L. A cluster's power is not constant — its O stars die and its supernovae begin — so the
  L it is evaluated at is **the energy injected so far over the age**, (E_wind(t) + E_SN(t)) / t: for a constant
  power exactly Weaver's, and otherwise the similarity solution at the mean power, since the energy-conserving
  radius depends on the energy deposited, R ∝ (E t²/ρ)^⅕ ``[inferred]``. The wind's energy is the IMF integral
  the cluster's own wind column is read from (``photometry.population_wind``), integrated over the ages the
  cluster has lived through (the light stage's cumulative machinery), so over its first 4 Myr — read at the
  youngest isochrone, as the wind column is — the bubble is Weaver's at ``cluster_wind_luminosity`` itself.
  The supernovae are the stars born above the core-collapse limit that the isochrones hold dead at the
  cluster's age, each giving the sourced energy.
- *(b) The ambient density* is the HII region's rms density (S35's ``hii_electron_density``) times 1.4 m_H: the
  bubble expands into the region its cluster ionized. For a single star, the gas's midplane density at its
  radius (``ism``'s P/σ², the volume average over every phase), because stars and clouds are placed
  independently and a star found inside a cloud would be a coincidence of two draws.
- *The phase*: **wind-driven** until the first core collapse the isochrones can date — the youngest isochrone's
  age, 4 Myr: stars heavier than its heaviest living mass (64 M☉ at solar [Fe/H]) die before it, when the table
  cannot say, and are placed at it, the latest they could be — **supernova-driven** while its stars above the
  limit are still dying, and **fading** after the last, when nothing drives it. The census's clusters are 0–20
  Myr old and the last core collapse is at 36 Myr, so none fades at the defaults.
- *The shell* is Weaver's isothermal shock, n_s = n₀(V² + C₀²)/C_s² (their eq. 67), with the ionized gas's
  sound speed on both sides, and its column n₀R/3 (eq. 66) sets its thickness. **Its Hα is photon-limited**: the
  shell's Case B recombinations at the region's temperature if the cluster's trapped photons can keep it
  ionized, else the fraction they can ``[inferred]`` — the same photons as the HII region's Hα (S35), placed in
  the shell rather than filling the sphere: a renderer draws the one or the other, never both.
- *The stall*: Weaver et al. find the H II region's pressure stops the shell once its velocity has fallen to
  about 10 km/s, where their thin-shell treatment also fails (p. 389, p. 392), and give no formula for where.
  Eliminating t between their radius and velocity at the ionized gas's sound speed gives the radius for a
  constant power, R = a^{5/2}(L/ρ₀)^{1/2}(0.6/C)^{3/2}; a bubble past it is **stalled** there, its state the
  solution's at that moment, at the power that drives it now — so a stalled bubble's radius follows its mean
  power, which the supernovae raise at 4 Myr and which then declines slowly ``[inferred]``. At the defaults
  almost every cluster's bubble has stalled. A single star's bubble, in the far thinner midplane gas, is not
  stalled here.
- *(c) Supernova remnants* are a census per cell, as the clouds are: the expected count is the supernova rate
  surface density (Phase 6's two) times the cell's area times the time a remnant stays visible, Frail, Goss &
  Whiteoak 1994's mean radio lifetime of 60 000 years (a lower bound in its source). Cioffi et al. 1988's merger
  age was the alternative read and computed first: in the model's midplane densities it is 1.2 Myr at the Sun
  and hundreds of Myr in the outer disc, where the pressure prescription underestimates the density, and it
  counted 39 700 remnants up to 5 kpc across — a census set by the one density the model holds least well.
  Poisson on the cell's own stream, so a cell drawn alone is its slice of the sweep (D60). Each remnant: its
  radius in the ring by the rate's density, its azimuth uniform in the sector (the rates are axisymmetric: the
  core collapses do not crowd into the arms here), its height from a sech² layer of the gas's own thickness
  (h = Σ/4ρ₀ ``[inferred]``), its age uniform over its lifetime (a steady population), its kind by the two rates'
  ratio at its radius, Sedov–Taylor until t_PDS and the pressure-driven snowplow after. The census counts every
  supernova, those inside a cluster's superbubble too: 65% of core collapses are of stars that die before
  the census's oldest cluster, 20 Myr (the Kroupa stars above the 11.7 M☉ the isochrones hold alive then, of
  those above 8.5), so the remnants of those are also energy in a superbubble (debt).
- *A Sedov-phase remnant's shell is adiabatic*: its emission is collisional and out of equilibrium, which Case B
  does not describe, so its Hα is NaN, not zero (rule B9). A radiative remnant's shell emits the Case B Hα of
  **one recombination for every hydrogen atom its shock sweeps up**, at the sourced shell temperature — the
  atom is ionized in the shock and recombines once as it cools ``[inferred]`` — spread over the shell's volume
  and bounded by the whole shell kept ionized. Case B of the whole compressed shell alone made the median
  radiative remnant as bright in Hα as a giant HII region (1.8 × 10³⁸ erg/s; 1.3 × 10³⁶ as built): the cooled
  shell does not stay ionized. The
  forbidden lines that make remnants read as remnants ([S II]/Hα) are Phase 9's grid's, when it arrives.
- *The hot phase*: per ring, the summed volumes of the clusters' bubbles and the remnants over the gas layer's
  volume, the layer's full thickness Σ/ρ₀ ("half-thickness H ≡ Σ/(2ρ0)", Ostriker & Shetty 2011 eq. 26
  ``[verified: arXiv:1102.1446, §5]``). A porosity, not a filling factor: overlapping bubbles are counted twice.

**Which remnant is which.** A remnant is named ``(cell, index)`` on the catalogue's cell grid; its stream is
``(systems_seed, "remnant", cell, …)``, so rerolling the systems seed rerolls it with the stars, clouds and
clusters, and no existing draw moves. The cluster columns read no seed: each is a function of its cluster's
and region's columns, so a region's bubbles are the sweep's by construction. The stage reads seeded columns,
so everything it publishes is seeded (D55).
"""

from __future__ import annotations

import functools
import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages import feedback as fb
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.dust import CM_PER_PC
from galaxy.stages.massive_stars import SECONDS_PER_YEAR, SOLAR_LUMINOSITY
from galaxy.stages.nebular import PROTON_MASS, alpha_b, case_b_halpha, halpha_per_recombination
from galaxy.stages.photometry import cumulative_over_age, isochrones, on_fine_ages, population_wind, steps_over
from galaxy.stages.remnants import _heaviest_alive, death_age
from galaxy.stages.supernovae import imf_stars_above
from galaxy.stages.systems import CELL_COUNT, CELL_RINGS, CELL_SECTORS, Catalogue, cell_edges, invert_cdf, sech2_height

BUBBLE_PHASES: tuple[str, ...] = ("wind", "supernova", "fading")
BUBBLE_STATES: tuple[str, ...] = ("expanding", "stalled")
REMNANT_PHASES: tuple[str, ...] = ("sedov", "radiative")
REMNANT_KINDS: tuple[str, ...] = ("core_collapse", "type_ia")

CLUSTER_READS: tuple[str, ...] = (
    "cluster_radius", "cluster_mass", "cluster_age", "cluster_metallicity", "cluster_ionizing_photons", "cluster_wind_luminosity",
)
REGION_READS: tuple[str, ...] = ("hii_electron_density", "hii_temperature")
# What the remnant census reads: the rates, the gas it expands into, the metallicity factor.
REMNANT_READS: tuple[str, ...] = ("core_collapse_rate", "type_ia_rate", "gas_midplane_density", "gas_surface_density", "feh_gas")

BUBBLE_COLUMNS: tuple[str, ...] = (
    "bubble_radius", "bubble_shell_velocity", "bubble_shell_density", "bubble_shell_thickness", "bubble_interior_pressure",
    "bubble_interior_temperature", "bubble_shell_emissivity", "bubble_mechanical_luminosity",
)
REMNANT_COLUMNS: tuple[str, ...] = (
    "remnant_radius", "remnant_azimuth", "remnant_height", "remnant_size", "remnant_age", "remnant_shell_velocity",
    "remnant_ambient_density", "remnant_shell_density", "remnant_shell_thickness", "remnant_shell_emissivity",
)

MSUN_PC3 = fb.MSUN_PER_PC3_IN_G_PER_CM3  # g/cm³ per M☉/pc³
ERG_PER_E51 = 1.0e51


# --- the cluster's energy ------------------------------------------------------------------------------


@functools.cache
def _wind_energy_table() -> np.ndarray:
    """(n_mh, n_fine, 1): ∫₀^τ L_wind dτ' per unit mass formed, L☉ yr / M☉ — the wind column's integrand."""
    return cumulative_over_age(on_fine_ages(population_wind()[..., None]))


def mean_wind_per_mass(age_myr: np.ndarray, feh: np.ndarray) -> np.ndarray:
    """The wind's power averaged over a burst's first ``age_myr``, L☉ per M☉ formed; 0 at age 0."""
    age = np.atleast_1d(np.asarray(age_myr, dtype=float))
    return steps_over(_wind_energy_table(), np.zeros(age.shape), age / 1000.0, np.asarray(feh, dtype=float))[..., 0]


def first_supernova_age() -> float:
    """Myr: the youngest isochrone's age, the first at which the table holds a star dead."""
    return float(10.0 ** isochrones().log_ages[0] / 1.0e6)


def heaviest_living(age_myr: np.ndarray, feh: np.ndarray) -> np.ndarray:
    """The heaviest initial mass the isochrones hold alive at this age and [Fe/H] (M☉), linear in log age —
    the reading ``remnants.death_age`` inverts; the youngest isochrone's below its age."""
    tab = isochrones()
    top = _heaviest_alive()
    age = np.asarray(age_myr, dtype=float)
    mh = np.abs(np.asarray(feh, dtype=float)[:, None] - tab.mhs[None, :]).argmin(axis=1)
    log_age = np.log10(np.maximum(age, 1.0e-6) * 1.0e6)
    out = np.empty(age.shape)
    for z in np.unique(mh):
        sel = mh == z
        out[sel] = np.interp(log_age[sel], tab.log_ages, top[z])
    return out


def supernovae_per_mass(age_myr: np.ndarray, feh: np.ndarray, m_min: float) -> np.ndarray:
    """Core collapses so far per M☉ formed: the Kroupa stars born above ``m_min`` and above the heaviest mass
    still alive; none before the table first holds a star dead."""
    age = np.asarray(age_myr, dtype=float)
    if not age.size:
        return np.zeros(0)
    cut = np.maximum(heaviest_living(age, feh), m_min)
    per = np.array([imf_stars_above(float(m)) for m in cut]) if cut.size else np.zeros(0)
    return np.where(age >= first_supernova_age(), per, 0.0)


def phase_of(age_myr: np.ndarray, feh: np.ndarray, m_min: float) -> np.ndarray:
    """The bubble's phase index: wind before the first core collapse, supernova while stars above the limit
    are still dying, fading after the last."""
    age = np.asarray(age_myr, dtype=float)
    last = death_age(np.full(age.shape, m_min), np.asarray(feh, dtype=float)) * 1000.0  # Myr
    return np.where(age < first_supernova_age(), 0, np.where(age < last, 1, 2)).astype(np.int64)


def materialise_bubbles(clusters: Catalogue, regions: Catalogue, constants: Mapping[str, float]) -> Catalogue:
    """The bubble of every cluster of ``clusters`` (a ``materialise_clusters`` catalogue) in its HII region, the
    rows of ``regions`` (``nebular.materialise_nebular``'s) in the same order. No draw (D60)."""
    c = constants
    mass = np.asarray(clusters["cluster_mass"], dtype=float)
    if not mass.size:
        empty = np.zeros(0)
        return Catalogue.of(
            {n: empty for n in BUBBLE_COLUMNS} | {"bubble_phase": empty.astype(np.int64), "bubble_stalled": empty.astype(np.int64)},
            clusters.counts,
        )
    age = np.asarray(clusters["cluster_age"], dtype=float)  # Myr
    feh = np.asarray(clusters["cluster_metallicity"], dtype=float)
    q = np.asarray(clusters["cluster_ionizing_photons"], dtype=float)
    n0 = np.asarray(regions["hii_electron_density"], dtype=float)
    t_e = np.asarray(regions["hii_temperature"], dtype=float)
    m_min = float(c["CORE_COLLAPSE_MIN_MASS"])

    t_s = age * 1.0e6 * SECONDS_PER_YEAR
    wind = np.where(age > 0.0, mean_wind_per_mass(age, feh) * mass,
                    np.asarray(clusters["cluster_wind_luminosity"], dtype=float)) * SOLAR_LUMINOSITY  # erg/s
    energy_sn = float(c["SUPERNOVA_ENERGY_51"]) * ERG_PER_E51 * supernovae_per_mass(age, feh, m_min) * mass  # erg
    with np.errstate(divide="ignore", invalid="ignore"):
        power = wind + np.where(t_s > 0.0, energy_sn / np.where(t_s > 0.0, t_s, 1.0), 0.0)
    rho = float(c["HII_MASS_PER_HYDROGEN"]) * PROTON_MASS * n0
    sound = float(c["SHELL_SOUND_SPEED"])
    # Expanding while the similarity solution's shell outruns the region's sound speed; stalled after, its
    # state the solution's at the moment it stalled, at the power it is driven by now (Weaver p. 389).
    free = fb.weaver_radius(power, rho, t_s)
    stall = fb.weaver_stall_radius(power, rho, sound)
    stalled = free > stall
    t_at = np.where(stalled, 0.6 * stall / (sound * fb.CM_PER_KM), t_s)
    radius_cm = np.where(stalled, stall, free)
    velocity = np.where(stalled, 0.0, fb.weaver_velocity(radius_cm, t_at))
    n_shell = fb.isothermal_shell_density(n0, np.where(stalled, sound, velocity), sound, sound)
    radius = radius_cm / CM_PER_PC
    thickness = fb.shell_thickness(radius, n0, n_shell)
    volume = fb.shell_volume(radius_cm, thickness * CM_PER_PC)  # cm³
    trapped = (1.0 - float(c["HII_ESCAPE_FRACTION"])) * q
    with np.errstate(divide="ignore", invalid="ignore"):
        full = alpha_b(t_e) * n_shell**2 * volume  # recombinations/s of a fully ionized shell
        ionized = np.where(full > 0.0, np.minimum(1.0, trapped / np.where(full > 0.0, full, 1.0)), np.nan)
    out = {
        "bubble_radius": radius,
        "bubble_shell_velocity": velocity,
        "bubble_shell_density": n_shell,
        "bubble_shell_thickness": thickness,
        "bubble_interior_pressure": fb.weaver_pressure(power, rho, t_at),
        "bubble_interior_temperature": fb.weaver_temperature(power, n0, t_at / SECONDS_PER_YEAR),
        "bubble_shell_emissivity": ionized * n_shell**2 * case_b_halpha(t_e),
        "bubble_mechanical_luminosity": power / SOLAR_LUMINOSITY,
        "bubble_phase": phase_of(age, feh, m_min),
        "bubble_stalled": stalled.astype(np.int64),
    }
    return Catalogue.of(out, clusters.counts)


# --- the remnant census ----------------------------------------------------------------------------------


class Ambient:
    """The ISM a remnant expands into, on the radial grid: hydrogen density, metallicity factor, the rates and
    the visible lifetime, and the remnants per unit area they make."""

    def __init__(self, fields: Mapping[str, Any], R: np.ndarray, c: Mapping[str, float]) -> None:
        self.R = R
        self.rho = np.asarray(fields["gas_midplane_density"], dtype=float)  # M☉/pc³
        self.n0 = self.rho * MSUN_PC3 / (float(c["HII_MASS_PER_HYDROGEN"]) * PROTON_MASS)
        self.zeta = 10.0 ** np.asarray(fields["feh_gas"], dtype=float)
        self.sigma = np.asarray(fields["gas_surface_density"], dtype=float)
        self.cc = np.maximum(np.asarray(fields["core_collapse_rate"], dtype=float), 0.0)
        self.ia = np.maximum(np.asarray(fields["type_ia_rate"], dtype=float), 0.0)
        # Visible for a fixed time wherever there is gas to sweep; no gas, no remnant.
        self.lifetime = np.where(self.n0 > 0.0, float(c["REMNANT_VISIBLE_LIFETIME"]), 0.0)  # yr
        self.density = (self.cc + self.ia) * self.lifetime  # remnants per kpc²

    def at(self, name: str, radius: np.ndarray) -> np.ndarray:
        return np.interp(radius, self.R, getattr(self, name))


def remnant_expected(fields: Mapping[str, Any], R: np.ndarray, constants: Mapping[str, float]) -> np.ndarray:
    """The expected number of remnants in every cell, (rings, sectors): the rate surface density times the
    lifetime, integrated over the ring's annulus and shared by its sectors. A population integral."""
    amb = Ambient(fields, R, constants)
    edges, _ = cell_edges(R)
    weight = amb.density * 2.0 * math.pi * R
    ring = np.array([
        float(np.trapezoid(np.where((R >= edges[i]) & (R <= edges[i + 1]), weight, 0.0), R)) for i in range(CELL_RINGS)
    ])
    return np.repeat(ring[:, None] / CELL_SECTORS, CELL_SECTORS, axis=1)


def remnant_counts(expected: np.ndarray, seed: int, cells: Sequence[int] | None = None) -> tuple[tuple[int, int], ...]:
    """``(cell, count)`` for every cell that realises a remnant: Poisson on the cell's own stream (D60)."""
    out: list[tuple[int, int]] = []
    for cell in (range(CELL_COUNT) if cells is None else cells):
        ring, sector = divmod(int(cell), CELL_SECTORS)
        lam = float(expected[ring, sector])
        count = int(_seeds.rng(seed, "remnant", int(cell), "count").poisson(lam)) if lam > 0.0 else 0
        if count:
            out.append((int(cell), count))
    return tuple(out)


def materialise_remnants(
    fields: Mapping[str, Any], R: np.ndarray, seed: int, constants: Mapping[str, float], cells: Sequence[int] | None = None,
) -> Catalogue:
    """The remnants of ``cells`` (every cell when None), exactly those a full sweep gives (D60)."""
    c = constants
    amb = Ambient(fields, R, c)
    rings, _ = cell_edges(R)
    counts = remnant_counts(remnant_expected(fields, R, c), seed, cells)
    width = 2.0 * math.pi / CELL_SECTORS
    e51 = float(c["SUPERNOVA_ENERGY_51"])
    columns: dict[str, list[np.ndarray]] = {}
    for cell, count in counts:
        ring, sector = divmod(int(cell), CELL_SECTORS)

        def draw(name: str, k: int = count) -> np.ndarray:
            return _seeds.rng(seed, "remnant", int(cell), name).random(k)

        lo, hi = rings[ring], rings[ring + 1]
        weight = np.where((R >= lo) & (R <= hi), amb.density * R, 0.0)
        radius = invert_cdf(draw("radius"), R, weight) if weight.sum() > 0.0 else np.full(count, 0.5 * (lo + hi))
        n0 = amb.at("n0", radius)
        with np.errstate(divide="ignore", invalid="ignore"):
            scale = np.where(amb.at("rho", radius) > 0.0, amb.at("sigma", radius) / (4.0 * amb.at("rho", radius)), 0.0)  # pc
        cc, ia = amb.at("cc", radius), amb.at("ia", radius)
        kind = np.where(draw("kind") * (cc + ia) < cc, 0, 1).astype(np.int64)
        columns.setdefault("remnant_radius", []).append(radius)
        columns.setdefault("remnant_azimuth", []).append((sector + draw("azimuth")) * width)
        columns.setdefault("remnant_height", []).append(sech2_height(draw("height"), scale / PC_PER_KPC))
        columns.setdefault("remnant_age", []).append(draw("age") * amb.at("lifetime", radius))
        columns.setdefault("remnant_ambient_density", []).append(n0)
        columns.setdefault("remnant_kind", []).append(kind)
        columns.setdefault("remnant_zeta", []).append(amb.at("zeta", radius))
    if not columns:
        empty = np.zeros(0)
        return Catalogue.of(
            {n: empty for n in REMNANT_COLUMNS} | {"remnant_phase": empty.astype(np.int64), "remnant_kind": empty.astype(np.int64)},
            counts,
        )
    out = {name: np.concatenate(parts) for name, parts in columns.items()}
    out.update(blast_wave(out.pop("remnant_age"), out["remnant_ambient_density"], out.pop("remnant_zeta"), e51, c))
    return Catalogue.of({n: out[n] for n in (*REMNANT_COLUMNS, "remnant_phase", "remnant_kind")}, counts)


def blast_wave(age_yr: np.ndarray, n0: np.ndarray, zeta: np.ndarray, e51: float, c: Mapping[str, float]) -> dict[str, np.ndarray]:
    """A remnant's size, shell and phase at its age: Sedov–Taylor before t_PDS, the snowplow after."""
    rho = float(c["HII_MASS_PER_HYDROGEN"]) * PROTON_MASS * n0  # g/cm³
    t_pds = fb.pds_time(e51, n0, zeta, float(c["PDS_TIME_COEFFICIENT"]))
    radiative = age_yr >= t_pds
    t_s = age_yr * SECONDS_PER_YEAR
    with np.errstate(divide="ignore", invalid="ignore"):
        sedov = fb.sedov_radius(e51 * ERG_PER_E51, rho, t_s, float(c["SEDOV_XI"])) / CM_PER_PC
        sedov_v = 0.4 * sedov * CM_PER_PC / np.where(t_s > 0.0, t_s, np.nan) / fb.CM_PER_KM
        clock = np.where(radiative, fb.snowplow(age_yr, t_pds), 1.0)
        pds = fb.pds_radius(e51, n0, zeta, float(c["PDS_RADIUS_COEFFICIENT"])) * clock**0.3
        pds_v = fb.pds_velocity(e51, n0, zeta, float(c["PDS_VELOCITY_COEFFICIENT"])) * clock**-0.7
    size = np.where(radiative, pds, sedov)
    velocity = np.where(radiative, pds_v, sedov_v)
    # The adiabatic shock's jump for gamma = 5/3, (gamma + 1)/(gamma - 1) = 4 [inferred: Rankine-Hugoniot];
    # a radiative shell, the isothermal jump into the ambient's own velocity dispersion.
    n_shell = np.where(
        radiative,
        fb.isothermal_shell_density(n0, velocity, float(c["H2_GAS_DISPERSION"]), float(c["SHELL_SOUND_SPEED"])),
        4.0 * n0,
    )
    thickness = fb.shell_thickness(size, n0, n_shell)
    volume = fb.shell_volume(size * CM_PER_PC, thickness * CM_PER_PC)  # cm³
    # A radiative shell's Hα: every hydrogen atom the shock sweeps up recombines once as it cools through the
    # shell's temperature [inferred], bounded by the Case B emission of the whole shell kept ionized.
    t_shell = np.full(n0.shape, float(c["REMNANT_SHELL_TEMPERATURE"]))
    swept = 4.0 * math.pi * (size * CM_PER_PC) ** 2 * n0 * velocity * fb.CM_PER_KM  # H atoms/s through the shock
    with np.errstate(divide="ignore", invalid="ignore"):
        case_b = n_shell**2 * case_b_halpha(t_shell)
        cap = swept * halpha_per_recombination(t_shell) / np.where(volume > 0.0, volume, np.nan)
    return {
        "remnant_age": age_yr,
        "remnant_size": size,
        "remnant_shell_velocity": velocity,
        "remnant_shell_density": n_shell,
        "remnant_shell_thickness": thickness,
        "remnant_shell_emissivity": np.where(radiative, np.fmin(case_b, cap), np.nan),
        "remnant_phase": radiative.astype(np.int64),
    }


# --- the hot phase ---------------------------------------------------------------------------------------


def hot_phase_porosity(
    fields: Mapping[str, Any], R: np.ndarray, cluster_radius: np.ndarray, bubble_radius: np.ndarray,
    remnant_radius: np.ndarray, remnant_size: np.ndarray,
) -> np.ndarray:
    """Per cell ring, on the radial grid: the clusters' bubbles' and the remnants' summed volume over the gas
    layer's, the layer's full thickness Σ/ρ₀. NaN where the ring holds no gas layer."""
    edges, _ = cell_edges(R)
    sigma = np.asarray(fields["gas_surface_density"], dtype=float)
    rho = np.asarray(fields["gas_midplane_density"], dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        thickness = np.where(rho > 0.0, sigma / np.where(rho > 0.0, rho, 1.0), 0.0)  # pc
    layer = thickness * 2.0 * math.pi * R * PC_PER_KPC**2  # pc³ per kpc of radius
    ring_volume = np.array([
        float(np.trapezoid(np.where((R >= edges[i]) & (R <= edges[i + 1]), layer, 0.0), R)) for i in range(CELL_RINGS)
    ])
    held = np.zeros(CELL_RINGS)
    for where, size in ((cluster_radius, bubble_radius), (remnant_radius, remnant_size)):
        where = np.asarray(where, dtype=float)
        vol = 4.0 / 3.0 * math.pi * np.nan_to_num(np.asarray(size, dtype=float)) ** 3
        ring = np.clip(np.searchsorted(edges, where, side="right") - 1, 0, CELL_RINGS - 1)
        held += np.bincount(ring, weights=vol, minlength=CELL_RINGS)
    with np.errstate(divide="ignore", invalid="ignore"):
        per_ring = np.where(ring_volume > 0.0, held / np.where(ring_volume > 0.0, ring_volume, 1.0), np.nan)
    at = np.clip(np.searchsorted(edges, R, side="right") - 1, 0, CELL_RINGS - 1)
    return per_ring[at]


# --- declarations ----------------------------------------------------------------------------------------


def _bubble(name: str, label: str, unit: str, about: str, ramp: Ramp = Ramp("viridis", scale="log")) -> FieldDecl:
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="cluster",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about)


def _remnant(name: str, label: str, unit: str, about: str, ramp: Ramp = Ramp("viridis", scale="log")) -> FieldDecl:
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="remnant",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about)


_D4 = (" **Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage that "
       "publishes the bubble and remnant columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the "
       "`/api/remnants` header carries it under `scalars`.")

BUBBLE_RADIUS = _bubble("bubble_radius", "Bubble radius", "pc",
                        "Weaver et al. 1977's energy-conserving bubble, R = 0.76 (L/ρ₀)^⅕ t^⅗, at the cluster's age, in "
                        "its HII region's rms density, L the wind's and supernovae's energy so far over the age — "
                        "the cluster's own wind power over its first 4 Myr — until the shell has slowed to the "
                        "ionized gas's sound speed, where Weaver et al. find the region's pressure stalls it, and "
                        "the bubble keeps the radius it stalled at. Radiative losses are not in it. A bubble larger "
                        "than its cloud has blown out of it, which the uniform medium the solution assumes cannot say.")
BUBBLE_VELOCITY = _bubble("bubble_shell_velocity", "Shell expansion velocity", "km/s",
                          "dR/dt of the same solution, (3/5) R/t (Weaver et al.'s eq. 52), falling as t^−⅖, while it "
                          "expands; zero once stalled. What a line profile's splitting would show.", ramp=Ramp("viridis"))
BUBBLE_SHELL_DENSITY = _bubble("bubble_shell_density", "Shell density", "1/cm3",
                               "The swept-up shell's hydrogen density behind an isothermal shock, n₀(V² + C²)/C² "
                               "(Weaver et al.'s eq. 67) with the ionized gas's 10 km/s sound speed on both sides; "
                               "twice the region's once stalled, where the shock has weakened to a sound wave.",
                               ramp=Ramp("magma", scale="log"))
BUBBLE_SHELL_THICKNESS = _bubble("bubble_shell_thickness", "Shell thickness", "pc",
                                 "The shell's column, n₀R/3 (the swept-up gas, Weaver et al.'s eq. 66), over its "
                                 "density: the width of the rim a renderer draws.")
BUBBLE_PRESSURE = _bubble("bubble_interior_pressure", "Interior pressure P/k", "dimensionless",
                          "In cm⁻³ K, as the midplane pressure is declared: the hot interior's uniform pressure "
                          "(Weaver et al.'s eq. 22). Compared with the disc's midplane pressure it says how "
                          "over-pressured, and so how far from stalling, a bubble is.", ramp=Ramp("inferno", scale="log"))
BUBBLE_TEMPERATURE = _bubble("bubble_interior_temperature", "Interior temperature", "K",
                             "At the centre, where thermal conduction into the shell sets it (Weaver et al.'s eq. 37): "
                             "about 10⁶ K, the X-ray-emitting gas; it falls to the shell's at the rim.",
                             ramp=Ramp("inferno", scale="log"))
BUBBLE_EMISSIVITY = _bubble("bubble_shell_emissivity", "Shell Hα volume emissivity", "erg/s/cm3",
                            "Case B Hα per unit volume of the shell at the region's temperature, where the cluster's "
                            "trapped photons keep it ionized, and the fraction they can where they cannot "
                            "(averaged over the shell). Volumetric (RENDER_PHYSICS §4): integrated along a ray the "
                            "rim limb-brightens. The same photons as the HII region's Hα, placed in the shell: a "
                            "renderer draws the shell or the filled region, not both.",
                            ramp=Ramp("magma", scale="log"))
BUBBLE_POWER = _bubble("bubble_mechanical_luminosity", "Mean mechanical luminosity", "Lsun",
                       "The energy the cluster's winds and supernovae have injected, over its age: the L the bubble "
                       "is evaluated at. Over the first 4 Myr the cluster's wind power; after, its supernovae "
                       "dominate by an order of magnitude.", ramp=Ramp("inferno", scale="log"))
BUBBLE_PHASE = FieldDecl(
    name="bubble_phase", label="Bubble driven by", unit="dimensionless", kind=Kind.CATEGORY_COLUMN, of="cluster",
    categories=BUBBLE_PHASES, ramp=Palette(("#6fd3ff", "#e07b39", "#5a5a5a")), provenance="seeded",
    about=(
        "Wind: younger than the first core collapse the isochrones can date, 4 Myr. Supernova: while its stars "
        "above the core-collapse limit are still dying. Fading: after the last, when nothing drives it — none at "
        "the defaults, whose clusters are at most 20 Myr old."
    ),
)

BUBBLE_STALLED = FieldDecl(
    name="bubble_stalled", label="Bubble expanding or stalled", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="cluster", categories=BUBBLE_STATES, ramp=Palette(("#f2d16b", "#3b6fb6")), provenance="seeded",
    about=(
        "Stalled once the similarity solution's shell would be slower than the ionized gas's sound speed: Weaver "
        "et al. 1977 find the H II region's pressure stalls the shell when its velocity falls to about 10 km/s, "
        "and their thin-shell treatment fails there. A stalled bubble keeps the radius at which it stalled, at "
        "the power that drives it now, its shell at rest and its interior the solution's at that moment."
    ),
)

REMNANT_RADIUS = _remnant("remnant_radius", "Galactocentric radius", "kpc",
                          "Drawn in its cell's ring by the supernova rate times the remnant lifetime at each radius, "
                          "so the census traces where remnants are, not only where supernovae go off.",
                          ramp=Ramp("viridis"))
REMNANT_AZIMUTH = _remnant("remnant_azimuth", "Azimuth", "rad",
                           "Uniform in its sector: the rates are axisymmetric, so the remnants of core collapses do "
                           "not crowd into the arms as the young stars do.", ramp=Ramp("viridis"))
REMNANT_HEIGHT = _remnant("remnant_height", "Height above the plane", "kpc",
                          "A sech² layer as thick as the gas's own, the surface density over four times the midplane "
                          "density: a stated guess, as no source for the supernovae's vertical distribution was read.",
                          ramp=Ramp("viridis"))
REMNANT_SIZE = _remnant("remnant_size", "Remnant radius", "pc",
                        "The blast wave's radius: Sedov–Taylor, ξ₀(E t²/ρ₀)^⅕ with ξ₀ = 1.15 for γ = 5/3 and 10⁵¹ erg, "
                        "until the shell turns radiative at Cioffi et al. 1988's t_PDS; then their pressure-driven "
                        "snowplow, growing as roughly t^0.3. In the midplane density at its radius.")
REMNANT_AGE = _remnant("remnant_age", "Remnant age", "yr",
                       "Uniform over the 60 000 years Frail et al. 1994 read as radio remnants' mean lifetime from "
                       "their young pulsars: a steady population, remnants at every stage side by side. A lower "
                       "bound in its source; the remnants are still expanding faster than the ISM's turbulence when "
                       "the census stops counting them.")
REMNANT_VELOCITY = _remnant("remnant_shell_velocity", "Shock velocity", "km/s",
                            "(2/5) R/t in the Sedov phase, the snowplow's own law after: thousands of km/s young, "
                            "under a hundred at the end of the census's count.")
REMNANT_AMBIENT = _remnant("remnant_ambient_density", "Ambient hydrogen density", "1/cm3",
                           "The gas's midplane density at its radius over 1.4 proton masses: what it swept up.",
                           ramp=Ramp("magma", scale="log"))
REMNANT_SHELL_DENSITY = _remnant("remnant_shell_density", "Shell density", "1/cm3",
                                 "Four times the ambient behind the adiabatic Sedov shock; behind the radiative shock "
                                 "the isothermal jump into the ambient's velocity dispersion, as a wind bubble's shell.",
                                 ramp=Ramp("magma", scale="log"))
REMNANT_SHELL_THICKNESS = _remnant("remnant_shell_thickness", "Shell thickness", "pc",
                                   "The swept-up column n₀R/3 over the shell's density: R/12 in the Sedov phase.")
REMNANT_EMISSIVITY = _remnant("remnant_shell_emissivity", "Shell Hα volume emissivity", "erg/s/cm3",
                              "A radiative shell's Hα per unit volume: one Case B recombination at its sourced 10⁴ K "
                              "for every hydrogen atom the shock sweeps up, spread over the shell, never more than "
                              "the whole shell kept ionized would give — a stated construction, not a shock model. "
                              "NaN in the Sedov phase: the adiabatic shell's emission is collisional and out of "
                              "equilibrium, which Case B does not describe. [S II]/Hα, what makes a remnant read as "
                              "one, awaits the photoionization grid.",
                              ramp=Ramp("magma", scale="log"))
REMNANT_PHASE = FieldDecl(
    name="remnant_phase", label="Remnant phase", unit="dimensionless", kind=Kind.CATEGORY_COLUMN, of="remnant",
    categories=REMNANT_PHASES, ramp=Palette(("#6fd3ff", "#e07b39")), provenance="seeded",
    about="Sedov: the adiabatic blast wave, before its shell cools. Radiative: the pressure-driven snowplow after.",
)
REMNANT_KIND = FieldDecl(
    name="remnant_kind", label="Supernova type", unit="dimensionless", kind=Kind.CATEGORY_COLUMN, of="remnant",
    categories=REMNANT_KINDS, ramp=Palette(("#e07b39", "#9b6cff")), provenance="seeded",
    about=(
        "Core collapse or type Ia, drawn by the two rates' ratio at its radius. The same energy for both; a "
        "type Ia's older progenitor is not placed differently, so the two differ only in number here."
    ),
)

HOT_PHASE_POROSITY = FieldDecl(
    name="hot_phase_porosity", label="Hot-phase porosity Q(R)", unit="dimensionless", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True, provenance="seeded",
    about=(
        "The clusters' bubbles' and the remnants' summed volume in each cell ring, over the gas layer's volume "
        "there (its full thickness the surface density over the midplane density, Ostriker & Shetty 2011): "
        "the same mechanism scaled up to the galaxy's hot phase, from Phase 6's rates and the census. A "
        "porosity, not a filling factor — overlaps count twice and it can exceed 1 — and an upper bound, since "
        "the bubbles are the energy-conserving solution's. Ferrière 2001 reviews local hot-gas filling "
        "factors from McKee & Ostriker's ~70% to ~20% once magnetic pressure is included."
    ),
)
REMNANT_COUNT_TOTAL = FieldDecl(
    name="remnant_count_total", label="Supernova remnants in the galaxy", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The expected number of visible remnants, summed over every cell: the supernova rate times the 60 000 "
        "years Frail et al. 1994 read as a radio remnant's mean lifetime, integrated over the disc. A population "
        "integral, not the count of a draw. Ball et al. 2023 make the same product for the Galaxy, 1000 to 2700, "
        "against the 300 to 400 found." + _D4
    ),
)


def compute_bubbles(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    f = ctx.fields
    clusters = Catalogue.of({n: f[n] for n in CLUSTER_READS})
    regions = Catalogue.of({n: f[n] for n in REGION_READS})
    bubbles = materialise_bubbles(clusters, regions, c)
    remnants = materialise_remnants(f, R, int(ctx.seeds["systems_seed"]), c)
    return {
        **bubbles,
        **remnants,
        "hot_phase_porosity": hot_phase_porosity(
            f, R, clusters["cluster_radius"], bubbles["bubble_radius"], remnants["remnant_radius"], remnants["remnant_size"],
        ),
        "remnant_count_total": float(remnant_expected(f, R, c).sum()),
    }


BUBBLES = IMPLEMENTATIONS.register(
    Stage(
        id="bubbles", slot="bubbles", checkpoint=5,
        about=(
            "Mechanical feedback: every young cluster's wind- and supernova-blown bubble as columns beside its HII "
            "region, the supernova remnants as a census of objects per cell, and the hot phase their volumes "
            "make ring by ring — the hollows the nebulae are drawn around."
        ),
        compute=compute_bubbles,
        reads_seeds=("systems_seed",),
        reads_constants=(
            "HII_MASS_PER_HYDROGEN", "HII_ESCAPE_FRACTION", "CORE_COLLAPSE_MIN_MASS", "H2_GAS_DISPERSION",
            "SUPERNOVA_ENERGY_51", "SEDOV_XI", "PDS_TIME_COEFFICIENT", "PDS_RADIUS_COEFFICIENT", "PDS_VELOCITY_COEFFICIENT",
            "REMNANT_VISIBLE_LIFETIME", "SHELL_SOUND_SPEED", "REMNANT_SHELL_TEMPERATURE",
        ),
        requires=(*CLUSTER_READS, *REGION_READS, *REMNANT_READS),
        publishes=(
            BUBBLE_RADIUS, BUBBLE_VELOCITY, BUBBLE_SHELL_DENSITY, BUBBLE_SHELL_THICKNESS, BUBBLE_PRESSURE,
            BUBBLE_TEMPERATURE, BUBBLE_EMISSIVITY, BUBBLE_POWER, BUBBLE_PHASE, BUBBLE_STALLED,
            REMNANT_RADIUS, REMNANT_AZIMUTH, REMNANT_HEIGHT, REMNANT_SIZE, REMNANT_AGE, REMNANT_VELOCITY,
            REMNANT_AMBIENT, REMNANT_SHELL_DENSITY, REMNANT_SHELL_THICKNESS, REMNANT_EMISSIVITY, REMNANT_PHASE,
            REMNANT_KIND, HOT_PHASE_POROSITY, REMNANT_COUNT_TOTAL,
        ),
    )
)
