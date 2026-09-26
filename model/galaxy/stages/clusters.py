"""Star clusters: the young clusters the molecular clouds make, as a census of objects (checkpoint 5, S33,
BUILD_II Phase 11).

Clusters are an **object class beside stars and clouds** — ``FieldDecl(kind=COLUMN, of="cluster")`` —
not a label on stars (RENDER_PHYSICS.md §5b). They are drawn from the cloud census, cell by cell,
so that a region's clusters are a sweep's clusters (D60), and a cluster is named ``(cell, index)`` on
the same grid as a star and a cloud.

**The rulings (S33's brief, D113, and the orchestrator's rulings on the first pass), each sourced
number a level-0 constant with the sentence it was read from quoted in its line; nothing here is
recalled (rule B9).**

- *One cluster per cloud past its embedded phase* (ruling (d)): a cloud in Kawamura et al. 2009's
  blown-open or dispersing state holds one, and the cloud census says which by ``cloud_cluster_index``.
- *Its mass is derived, not adopted* (rule A3, D117): the efficiency per cloud is the local molecular
  depletion time inverted over one cloud lifetime, ε(R) = Σ_SFR(R) τ_cloud / Σ_H₂(R), read at the
  cloud's radius, capped at 1, and the cluster's mass is ε times the cloud's. ε here is M★/M_gas, not
  Murray 2011's M★/(M_GMC + M★): the census's cloud masses *are* the molecular gas (S32's
  redistribution rule), and ε(R) is defined so that the clusters form stars exactly as fast as the
  model's own star formation rate does — every star in a cluster — just as the clouds hold exactly the
  ISM's molecular mass. The sourced values it is read against, chosen against as defaults, are in
  ``cluster_formation_efficiency``'s about line: Murray's 0.08, his "typical" 0.02 and Galactic
  average 0.005, and Lada & Lada's 1–5%. The model's own galaxy-wide value is 0.0198.
- *No cap by the mass function* (ruling (a)): the cluster mass function Portegies Zwart, McKee &
  Gieles 2010 give is a Schechter function, which has no upper end, and its M★ is a scale, not a cut;
  the census inherits the clouds' slopes, and the test says how far that is from the review's −2.
- *Age* (accepted by the orchestrator on the first pass): the cluster forms when its cloud leaves the
  embedded phase — the phase the source defines by the absence of massive star formation — so its age
  is the cloud's less that phase's duration: 0 to 20 Myr. A cluster as old as its cloud would have made
  its O stars in a phase defined by having none, and the census would hold no cluster younger than
  6 Myr, the ones that make most of the ionizing photons.
- *Bound* (ruling (b)): a seeded draw at Lada & Lada 2003's fraction of embedded clusters that
  survive to Pleiades age, independent of mass; an unbound cluster older than the age by which the
  same review says the unbound have dispersed is *dissolved* — its stars are still there and still
  counted, but it is no longer a cluster.
- *Half-mass radius* (ruling (c)): the constant half-mass density Portegies Zwart, McKee & Gieles
  2010 read for clusters younger than 10 Myr, r_hm = (3M / 8πρ_hm)^⅓; the constant radius they and
  Larsen 2004 read for older clusters is the named alternative.
- *Where*: at the cloud's embedded source — the cloud's centre plus its source offset, in the plane,
  the angle measured from the outward radial direction toward increasing azimuth ``[inferred]``: the
  cloud census states no reference direction — and at the cloud's height and gas abundance.
- *What it emits*: **the sums over the members the IMF gives it**, integrated rather than sampled
  (rule B8): Q(H⁰) and the wind's power per unit mass formed at the cluster's age and [Fe/H], read
  off the same isochrone integrals the light stage uses (``photometry``), times the cluster's mass.

**The Phase 5 hook.** ``bound_cluster_mass_total`` is a population integral over the whole history:
the stars formed, net of what they return, times the bound fraction — every star taken to form in a
cluster ``[inferred]``: Lada & Lada 2003 put 70-90% of the stars formed in GMCs in embedded clusters.
No dissolution after emergence is applied; that is S34's, where Boylan-Kolchin 2018's η checks it.

**Which cluster is which.** Its stream is ``(systems_seed, "cluster", cell, …)``, so rerolling the
systems seed rerolls it with the stars and clouds, and no cloud number moves with it.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.clouds import cloud_counts, expected_counts
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.photometry import per_mass_at, population_light, population_wind
from galaxy.stages.systems import Catalogue

CLUSTER_BOUND_STATES: tuple[str, ...] = ("bound", "unbound", "dissolved")

CLUSTER_COLUMNS: tuple[str, ...] = (
    "cluster_radius", "cluster_azimuth", "cluster_height", "cluster_mass", "cluster_half_mass_radius",
    "cluster_age", "cluster_metallicity", "cluster_ionizing_photons", "cluster_wind_luminosity",
)
# What the census reads of each cloud: its place, mass, age, abundance, source and which cluster it holds.
CLOUD_READS: tuple[str, ...] = (
    "cloud_radius", "cloud_azimuth", "cloud_height", "cloud_mass", "cloud_age", "cloud_source_offset",
    "cloud_source_angle", "cloud_metallicity", "cloud_cluster_index",
)


def cloud_lifetime(constants: Mapping[str, float]) -> float:
    """τ_cloud in Myr: the three sourced phases' sum, the span a cloud's age is drawn over."""
    c = constants
    return float(c["GMC_PHASE_EMBEDDED"]) + float(c["GMC_PHASE_BLOWN_OPEN"]) + float(c["GMC_PHASE_DISPERSING"])


def efficiency(radius: np.ndarray, sigma_sfr: np.ndarray, sigma_h2: np.ndarray, R: np.ndarray, lifetime_myr: float) -> np.ndarray:
    """ε = min(Σ_SFR τ_cloud / Σ_H₂, 1) at ``radius`` (kpc): the fraction of a cloud's molecular mass that
    one cloud lifetime of the local star formation rate turns into stars. Σ_SFR in M☉/yr/kpc², Σ_H₂ in
    M☉/pc²; zero where there is no molecular gas (no cloud is drawn there)."""
    sfr = np.interp(radius, R, np.asarray(sigma_sfr, dtype=float)) / PC_PER_KPC**2  # M☉/yr/pc²
    h2 = np.interp(radius, R, np.asarray(sigma_h2, dtype=float))
    with np.errstate(divide="ignore", invalid="ignore"):
        eps = np.where(h2 > 0.0, sfr * lifetime_myr * 1.0e6 / np.where(h2 > 0.0, h2, 1.0), 0.0)
    return np.minimum(eps, 1.0)


def mean_efficiency(sigma_sfr: np.ndarray, sigma_h2: np.ndarray, R: np.ndarray, lifetime_myr: float) -> float:
    """The molecular-mass-weighted ε over the disc, a population integral: ∫ ε Σ_H₂ 2πR dR / ∫ Σ_H₂ 2πR dR."""
    h2 = np.asarray(sigma_h2, dtype=float)
    eps = efficiency(R, sigma_sfr, h2, R, lifetime_myr)
    mass = float(np.trapezoid(h2 * R, R))
    return float(np.trapezoid(eps * h2 * R, R)) / mass if mass > 0.0 else 0.0


def half_mass_radius(mass: np.ndarray, density: float) -> np.ndarray:
    """r_hm in pc at half-mass density ρ_hm ≡ 3M/(8π r_hm³) (Portegies Zwart et al. 2010, Fig. 9)."""
    return np.cbrt(3.0 * np.asarray(mass, dtype=float) / (8.0 * math.pi * density))


def offset_position(radius: np.ndarray, azimuth: np.ndarray, offset_pc: np.ndarray, angle: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(R, φ) of a point ``offset_pc`` from (radius, azimuth) in the plane, at ``angle`` from the outward
    radial direction toward increasing φ. Exact, not a small-offset expansion."""
    d = np.asarray(offset_pc, dtype=float) / PC_PER_KPC
    x = np.asarray(radius, dtype=float) + d * np.cos(angle)
    y = d * np.sin(angle)
    return np.hypot(x, y), np.mod(np.asarray(azimuth, dtype=float) + np.arctan2(y, x), 2.0 * math.pi)


def per_mass(age_myr: np.ndarray, feh: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(Q in photons/s, wind power in L☉) per M☉ formed, for single bursts of these ages and [Fe/H]."""
    age = np.asarray(age_myr, dtype=float) / 1000.0
    return per_mass_at(population_light().ionizing_per_mass, age, feh), per_mass_at(population_wind(), age, feh)


def materialise_clusters(
    clouds: Catalogue, fields: Mapping[str, Any], R: np.ndarray, seed: int, constants: Mapping[str, float]
) -> Catalogue:
    """The clusters of a cloud census's cells: one per cloud whose ``cloud_cluster_index`` names one, in
    the cells' order and the clouds' order within each, so a cell drawn alone is the cell in any set (D60).
    ``counts`` lists the cells that hold a cluster, in the order the census listed them. ``fields`` gives
    the star formation rate and molecular surface densities the efficiency is read from."""
    c = constants
    lifetime = cloud_lifetime(c)
    embedded = float(c["GMC_PHASE_EMBEDDED"])
    bound_fraction = float(c["CLUSTER_BOUND_FRACTION"])
    dissolution = float(c["CLUSTER_DISSOLUTION_AGE"])
    density = float(c["CLUSTER_HALF_MASS_DENSITY"])
    index = np.asarray(clouds["cloud_cluster_index"], dtype=float)
    pick: list[np.ndarray] = []
    counts: list[tuple[int, int]] = []
    bound: list[np.ndarray] = []
    offset = 0
    for cell, count in clouds.counts:
        rows = offset + np.flatnonzero(index[offset:offset + count] >= 0.0)
        offset += count
        if not rows.size:
            continue
        pick.append(rows)
        counts.append((int(cell), int(rows.size)))
        bound.append(_seeds.rng(seed, "cluster", int(cell), "bound").random(rows.size) < bound_fraction)
    if not pick:
        empty = np.zeros(0)
        return Catalogue.of({n: empty for n in CLUSTER_COLUMNS} | {"cluster_bound": empty.astype(np.int64)}, ())
    rows = np.concatenate(pick)

    def cloud(name: str) -> np.ndarray:
        return np.asarray(clouds[name], dtype=float)[rows]

    eps = efficiency(cloud("cloud_radius"), fields["sfr_surface_density"], fields["gas_molecular_surface_density"], R, lifetime)
    mass = eps * cloud("cloud_mass")
    age = np.maximum(cloud("cloud_age") - embedded, 0.0)
    feh = cloud("cloud_metallicity")
    radius, azimuth = offset_position(cloud("cloud_radius"), cloud("cloud_azimuth"), cloud("cloud_source_offset"), cloud("cloud_source_angle"))
    q, wind = per_mass(age, feh)
    is_bound = np.concatenate(bound)
    state = np.where(is_bound, 0, np.where(age < dissolution, 1, 2)).astype(np.int64)
    out = {
        "cluster_radius": radius,
        "cluster_azimuth": azimuth,
        "cluster_height": cloud("cloud_height"),
        "cluster_mass": mass,
        "cluster_half_mass_radius": half_mass_radius(mass, density),
        "cluster_age": age,
        "cluster_metallicity": feh,
        "cluster_ionizing_photons": mass * q,
        "cluster_wind_luminosity": mass * wind,
        "cluster_bound": state,
    }
    return Catalogue.of(out, counts)


def census_of_clouds(fields: Mapping[str, Any], R: np.ndarray, seed: int, constants: Mapping[str, float]) -> Catalogue:
    """The published cloud columns with the ``(cell, count)`` layout they were drawn in: the counts are
    the census's own Poisson draws, redrawn (they are cheap), so the stage need not draw a cloud twice."""
    counts = cloud_counts(expected_counts(fields, R, constants), seed)
    return Catalogue.of({name: fields[name] for name in CLOUD_READS}, counts)


def bound_mass(stars_formed_history: np.ndarray, R: np.ndarray, bound_fraction: float) -> float:
    """The stars formed over the whole history, net of what they return, times the bound fraction, M☉."""
    locked = np.asarray(stars_formed_history, dtype=float).sum(axis=1) * PC_PER_KPC**2  # M☉ per kpc²
    return float(bound_fraction * np.trapezoid(locked * 2.0 * math.pi * R, R))


# --- declarations ----------------------------------------------------------------------------------


def _column(name: str, label: str, unit: str, about: str, ramp: Ramp = Ramp("viridis")) -> FieldDecl:
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="cluster",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about)


CLUSTER_RADIUS = _column("cluster_radius", "Galactocentric radius", "kpc",
                         "Where its cloud's embedded source sits: the cloud's centre plus the source's offset, "
                         "so a cluster lies inside the cloud that made it, where the ionization front starts.")
CLUSTER_AZIMUTH = _column("cluster_azimuth", "Azimuth", "rad",
                          "The embedded source's azimuth. The source's direction is read from the outward radial "
                          "direction toward increasing azimuth, a convention the cloud census does not state.")
CLUSTER_HEIGHT = _column("cluster_height", "Height above the plane", "kpc",
                         "Its cloud's height: the offset is taken in the plane.")
CLUSTER_MASS = _column("cluster_mass", "Cluster mass", "Msun",
                       "Stellar mass formed: the cloud's mass times the efficiency derived where it sits — one "
                       "cloud lifetime of the local star formation rate over the local molecular gas — so the "
                       "clusters form stars exactly as fast as the galaxy does, every star in a cluster. The "
                       "clusters inherit the cloud mass function's slopes rather than the −2 of the review's "
                       "cluster function, and nothing caps them: that function has a scale, not an end.",
                       ramp=Ramp("magma", scale="log"))
CLUSTER_HALF_MASS_RADIUS = _column("cluster_half_mass_radius", "Half-mass radius", "pc",
                                   "(3M / 8πρ)^⅓ at the one half-mass density young clusters are read to form at "
                                   "(Portegies Zwart, McKee & Gieles 2010); a constant radius of a few parsecs, their "
                                   "reading for older clusters and Larsen 2004's, is the alternative. The unbound are "
                                   "given the radius they formed with, not the one they expand to.",
                                   ramp=Ramp("viridis", scale="log"))
CLUSTER_AGE = _column("cluster_age", "Cluster age", "Myr",
                      "Its cloud's age less the embedded phase. Kawamura et al. 2009 define that phase by the "
                      "absence of massive star formation, so a cluster as old as its cloud would have made its O "
                      "stars in a phase defined by having none: a cluster is born when its HII regions appear, "
                      "and the census holds every cluster from 0 to 20 Myr old.")
CLUSTER_BOUND = FieldDecl(
    name="cluster_bound", label="Bound", unit="dimensionless", kind=Kind.CATEGORY_COLUMN, of="cluster",
    categories=CLUSTER_BOUND_STATES, ramp=Palette(("#f2d16b", "#e07b39", "#5a5a5a")), provenance="seeded",
    about=(
        "Bound, a seeded draw at the fraction of embedded clusters Lada & Lada 2003 find surviving to the "
        "Pleiades' age, whatever the mass; otherwise unbound and expanding, and dissolved — an association "
        "in the field, its stars still counted — once older than the age by which the same review finds "
        "the unbound gone."
    ),
)
CLUSTER_METALLICITY = _column("cluster_metallicity", "[Fe/H]", "dex",
                              "Its cloud's: the present-day gas iron abundance at the cloud's radius, which the "
                              "stars are born with.", ramp=Ramp("plasma"))
CLUSTER_IONIZING = _column("cluster_ionizing_photons", "Hydrogen-ionizing photon rate Q(H⁰)", "1/s",
                           "The sum over its members, integrated rather than sampled: Q per unit mass formed of a "
                           "burst at the cluster's age and [Fe/H], summed over the IMF along the same isochrones "
                           "and calibration the light stage integrates, times the mass. Falls by orders of "
                           "magnitude between 3 and 10 Myr as the O stars die; the first 4 Myr are read at the "
                           "youngest isochrone, which cannot see stars above 64 M☉.",
                           ramp=Ramp("magma", scale="log", lo=1e44, hi=1e53))
CLUSTER_WIND = _column("cluster_wind_luminosity", "Wind mechanical luminosity", "Lsun",
                       "½ Ṁ v_∞² summed over the IMF the same way: Vink, de Koter & Lamers 2001's line-driven "
                       "winds at each living member's luminosity, temperature and present mass, at the "
                       "isochrone's metallicity, times the mass. Only the O and B stars the recipe covers blow; "
                       "no supernova energy is in it.", ramp=Ramp("inferno", scale="log"))

BOUND_CLUSTER_MASS_TOTAL = FieldDecl(
    name="bound_cluster_mass_total", label="Mass in clusters that emerge bound", unit="Msun", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "A population integral over the whole history, not a sum over the census: the stars formed "
        "everywhere, net of what they return, times the fraction of clusters Lada & Lada 2003 find "
        "emerging bound, every star taken to form in a cluster, as the census's own efficiency makes "
        "them. **Survival after emergence is not applied**: this is the mass that could become old "
        "clusters before any of them dissolves, which is the next phase's to apply, and the globular "
        "clusters' share of the halo mass is the check it will be held to. "
        "**Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage "
        "that publishes the cluster columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the "
        "`/api/clusters` header carries it under `scalars`."
    ),
)

CLUSTER_FORMATION_EFFICIENCY_DECL = FieldDecl(
    name="cluster_formation_efficiency", label="Star formation efficiency per cloud", unit="dimensionless",
    kind=Kind.SCALAR, meaningful_zero=True, provenance="seeded",
    about=(
        "The fraction of a cloud's molecular mass its cluster takes, averaged over the disc by molecular "
        "mass: today's star formation rate times one cloud lifetime over the molecular gas, ring by ring "
        "and capped at 1. Derived, so the clusters form stars as fast as the model does; M★/M_gas, not "
        "Murray's M★/(M_GMC + M★), because the census's clouds are the molecular gas itself. The sourced "
        "values it is read against, each chosen against as the default: Murray 2011's 0.08, 'a lower "
        "limit to the fraction of gas in a massive Milky Way GMC that will be converted into stars' "
        "[verified: arXiv:1007.3270, section 6], the ionizing-luminosity-weighted mean of the most active "
        "clouds; the same paper's 'typical estimates are more like 0.02' [verified: section 3] and "
        "'Galactic average ~ 0.005' [verified: abstract]; and Lada & Lada 2003's 'global SFEs estimated "
        "for entire GMCs which are typically only 1-5 %' [verified: astro-ph/0301540, section 5.2]. "
        "**Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage "
        "that publishes the cluster columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the "
        "`/api/clusters` header carries it under `scalars`."
    ),
)


def compute_clusters(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    seed = int(ctx.seeds["systems_seed"])
    clusters = materialise_clusters(census_of_clouds(ctx.fields, R, seed, c), ctx.fields, R, seed, c)
    return {
        **clusters,
        "cluster_formation_efficiency": mean_efficiency(
            ctx.fields["sfr_surface_density"], ctx.fields["gas_molecular_surface_density"], R, cloud_lifetime(c)
        ),
        "bound_cluster_mass_total": bound_mass(ctx.fields["stars_formed_history"], R, float(c["CLUSTER_BOUND_FRACTION"])),
    }


CLUSTERS = IMPLEMENTATIONS.register(
    Stage(
        id="clusters", slot="clusters", checkpoint=5,
        about=(
            "The young star clusters: one in every cloud that has made massive stars, drawn per cell from "
            "the cloud census with the parameter vector a renderer draws a cluster from, and what its "
            "members emit summed over the IMF."
        ),
        compute=compute_clusters,
        reads_seeds=("systems_seed",),
        reads_constants=(
            "R_SUN", "GMC_MASS_SLOPE_INNER", "GMC_MASS_TRUNCATION_INNER", "GMC_MASS_SLOPE_OUTER",
            "GMC_MASS_TRUNCATION_OUTER", "GMC_MASS_MIN", "GMC_PHASE_EMBEDDED", "GMC_PHASE_BLOWN_OPEN",
            "GMC_PHASE_DISPERSING", "CLUSTER_BOUND_FRACTION", "CLUSTER_DISSOLUTION_AGE", "CLUSTER_HALF_MASS_DENSITY",
        ),
        requires=(
            *CLOUD_READS, "gas_molecular_surface_density", "arm_contrast", "bar_contrast", "arm_multiplicity",
            "pitch_angle", "bar_half_length", "stars_formed_history", "sfr_surface_density",
        ),
        publishes=(
            CLUSTER_RADIUS, CLUSTER_AZIMUTH, CLUSTER_HEIGHT, CLUSTER_MASS, CLUSTER_HALF_MASS_RADIUS, CLUSTER_AGE,
            CLUSTER_BOUND, CLUSTER_METALLICITY, CLUSTER_IONIZING, CLUSTER_WIND, BOUND_CLUSTER_MASS_TOTAL,
            CLUSTER_FORMATION_EFFICIENCY_DECL,
        ),
    )
)
