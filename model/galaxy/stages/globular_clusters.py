"""Globular clusters: the bound clusters that survive the whole history (checkpoint 5, S34, BUILD_II Phase 5).

**The mechanism, and the check** (the brief's ruling (a)). S33 made every star in a cluster and let
Lada & Lada 2003's 7% of them emerge bound: ``clusters.bound_mass()``, published as
``bound_cluster_mass_total``, 2.79 × 10⁹ M☉ at the default — 72 times what Boylan-Kolchin 2018's
M_GC = η M_halo says a Milky Way halo holds in globular clusters (debt #97). What removes the rest is
dissolution, and that is what this phase builds: **the system's mass is the bound mass times the fraction
of it that survives to today**, and η is the check the product is held to, never an input to it.

**The survival** is Lamers et al. 2005's analytic disruption, read at its own solar-neighbourhood
calibration: a cluster of initial mass M_i loses mass at dM/dt = −M/t_dis with t_dis = t₀ (M/M☉)^γ, so
μ(t) = M(t)/M_i = {μ_ev^γ − γ t / t₀ (M☉/M_i)^γ}^(1/γ), and it is gone when the bracket reaches zero
(their eq. 6). ``μ_ev`` — what stellar evolution alone leaves — is the model's own instantaneous return
(1 − R), because the bound mass it multiplies is already net of that return; the source's μ_ev(t) is a
fit to one isochrone set and the named alternative. The clusters are born with the mass function the
review of young massive clusters gives Milky-Way-type spirals — a power law of index −2 with a Schechter
scale (Portegies Zwart, McKee & Gieles 2010 §2.4.2) — from the lower mass Lamers et al. suppose for the
same law (§5), and they form at the model's own rate: each step's clusters are as old as that step's
stars, and the survival is the mass-weighted average over the whole history. The mass function had
cancelled out of S33's integral because its bound fraction is mass-independent (D182); dissolution is
not, so the function enters here and nowhere else — the cluster census keeps the clouds' slopes (#96).

**What the survival assumes**, stated because #97 closes on it: one disruption time-scale for every
cluster ever formed, the one Lamers et al. measure for open clusters within 600 pc of the Sun, which
includes the encounters with molecular clouds of a gas-rich thin disc; the N-body value for the tidal
field alone is five times longer (their abstract), and a globular cluster that spent its life in the halo
felt less of the disc than an open cluster does. That is the named alternative; it reads the survival six
times higher. The universal model Portegies Zwart et al. set beside it (80-90% of clusters destroyed per
decade of age, whatever their mass; §4.4.2) is the other.

**What the survivors are** (measured at S34, pinned by the tests). The integral counts every bound cluster
alive today, whatever its age, because ruling (a) defines the system as the bound mass times its survival
over the history and no source read gives the age at which a survivor becomes a globular. At the default
**53% of the surviving mass is older than 1 Gyr and 0.7% older than 10 Gyr**: a cluster of 10⁴ M☉ is gone
in 1.3 Gyr and one of 10⁵ in 5.4, so the old end holds only the Schechter tail, and the system is mostly
open clusters. Its agreement with the halo relation (0.26 dex) is therefore carried by the young
survivors. The clusters older than 10 Gyr alone read 5 × 10⁵ M☉ at this calibration (−1.87 dex against the
relation) and 4.7 × 10⁷ at the N-body one (+0.09 dex) — the numbers S34's report gives the orchestrator to
rule on, neither built.

**The residual** (ruling (b)). Boylan-Kolchin's scatter at fixed halo mass is real and intrinsic, so under
GALAXY_INPUTS.md §4b the mean is derived and the residual drawn — a lognormal of his width on
``world_seed``, which binds at checkpoint 1 (the nucleus reads it first) and is not moved. The system mass
published is the drawn one; the mean is the survival fraction times the bound mass, both published.

**The metal-poor share** (ruling (c)) is η_b/η from the same source: the metal-poor clusters are the
accreted ones, so the share is that ratio when the merger list accreted any stars (``halo_stellar_mass``
> 0) and zero when it accreted none. The source measures both ratios on galaxies that all accreted, so it
says nothing about how the share scales with the accreted mass, and no scaling is invented here.

**Why the bound mass is recomputed rather than read.** ``bound_cluster_mass_total`` is published by a
stage that materialises the whole cloud and cluster census to publish it; the statistical row this phase
adds (row 32) is judged on an ensemble of 41 runs, and reading the field would build both censuses 41
times per model for an integral that depends on neither (rule D4, debt #24's reasoning). The stage calls
the same function on the same history with the same constant, and a test asserts the two are equal.

**Provenance.** Two stages, as the nucleus was split from the halo (D55, rule A10): ``cluster_survival``
publishes what the inputs determine — the survival fraction and the metal-poor share — and stays derived;
``globular_clusters`` reads ``world_seed`` and publishes the drawn mass and the count, seeded.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.clusters import bound_mass
from galaxy.stages.stellar_halo import formed_per_step

# The mass mesh the survival integral runs on: log-spaced from the lower mass to this many Schechter
# scales, where exp(-M/M*) is e^-100 and the law carries nothing; a fixed count, so the integral's cost
# and truncation are known in advance (rule A1). Numerical, not physical: no source is cited for it.
MASS_SPAN_SCALES = 100.0
MASS_POINTS = 1201


def mass_mesh(m_min: float, m_scale: float) -> np.ndarray:
    return np.geomspace(m_min, MASS_SPAN_SCALES * m_scale, MASS_POINTS)


def remaining_fraction(age_myr: np.ndarray, mass: np.ndarray, t0_myr: float, index: float, mu_ev: float) -> np.ndarray:
    """μ = M(t)/M_i = {μ_ev^γ − γ t / t₀ (M☉/M_i)^γ}^(1/γ), zero once the bracket is spent (Lamers et al. 2005,
    eq. 6). Broadcasts ``age_myr`` against ``mass``."""
    bracket = mu_ev**index - index * np.asarray(age_myr, dtype=float) / (t0_myr * np.asarray(mass, dtype=float) ** index)
    return np.where(bracket > 0.0, np.maximum(bracket, 0.0) ** (1.0 / index), 0.0)


def disruption_time(mass: float, t0_myr: float, index: float, mu_ev: float) -> float:
    """The age in Myr at which a cluster of initial mass ``mass`` is gone: μ_ev^γ t₀ M^γ / γ."""
    return mu_ev**index * t0_myr * mass**index / index


def survival_fraction(
    per_step: np.ndarray, age_myr: np.ndarray, constants: Mapping[str, float], mu_ev: float
) -> float:
    """The fraction of the bound cluster mass (net of stellar return) still in clusters today: the mass
    function's mass-weighted μ/μ_ev, averaged over the history by the mass each step formed."""
    c = constants
    M = mass_mesh(float(c["CLUSTER_MASS_MIN"]), float(c["CLUSTER_MASS_FUNCTION_SCALE"]))
    lnM = np.log(M)
    # Mass per unit ln M under dN/dM = A M^-beta exp(-M/M*): M^2 dN/dM.
    weight = M ** (2.0 - float(c["CLUSTER_MASS_FUNCTION_INDEX"])) * np.exp(-M / float(c["CLUSTER_MASS_FUNCTION_SCALE"]))
    w = np.asarray(per_step, dtype=float)
    keep = w > 0.0
    if not np.any(keep):
        return 0.0
    mu = remaining_fraction(np.asarray(age_myr, dtype=float)[keep, None], M[None, :],
                            float(c["CLUSTER_DISRUPTION_T0"]), float(c["CLUSTER_DISRUPTION_INDEX"]), mu_ev)
    left = np.trapezoid(weight[None, :] * mu, lnM, axis=1)  # per step, per unit of the law's normalisation
    born = np.trapezoid(weight, lnM) * mu_ev
    return float(np.sum(w[keep] * left) / (np.sum(w[keep]) * born))


def metal_poor_fraction(halo_stellar_mass: float, constants: Mapping[str, float]) -> float:
    """η_b/η when the history accreted any stars, zero when it accreted none."""
    c = constants
    if halo_stellar_mass <= 0.0:
        return 0.0
    return float(c["GC_METAL_POOR_HALO_MASS_RATIO"]) / float(c["GC_HALO_MASS_RATIO"])


GC_SURVIVAL_FRACTION = FieldDecl(
    name="gc_survival_fraction", label="Bound cluster mass surviving to today", unit="dimensionless",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The share of the mass that emerged in bound clusters, over the whole history, still in clusters "
        "today: Lamers et al. 2005's disruption at their solar-neighbourhood calibration, a cluster's "
        "life growing as its mass to the 0.62, applied to clusters born with the young-cluster mass "
        "function of Milky-Way-type spirals at the ages the model's own history gives them. Every cluster "
        "is given the disruption time of an open cluster near the Sun, gas clouds and all; the N-body "
        "tidal field alone gives five times longer and would read this six times higher. The surprise is "
        "how young the survivors are: every bound cluster alive today is counted, and at this calibration "
        "about half of the surviving mass is under a gigayear old and under 1% is older than 10 Gyr, so the "
        "sum lands near the halo relation on open clusters, not on globulars."
    ),
)

GC_METAL_POOR_FRACTION = FieldDecl(
    name="gc_metal_poor_fraction", label="Metal-poor share of the globular clusters", unit="dimensionless",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Boylan-Kolchin 2018's metal-poor (blue) clusters' share of the halo relation over all clusters' "
        "— both measured, both linear in halo mass. The metal-poor clusters are the accreted ones, so the "
        "share applies when the merger list accreted any stars and is zero when it accreted none; how it "
        "scales with the accreted mass the source does not say, and the model does not guess."
    ),
)

GC_SYSTEM_MASS = FieldDecl(
    name="gc_system_mass", label="Globular cluster system mass", unit="Msun", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "Acceptance row 32, statistical. The mass that emerged bound from every cluster the history made "
        "times the fraction that survives dissolution — derived — times a lognormal residual at "
        "Boylan-Kolchin 2018's scatter at fixed halo mass, drawn: the mean relation is his, not the answer. "
        "The halo-mass relation is the check the mean is held to, not how it is made. The mean lands 0.26 "
        "dex above that relation at the default, inside its 0.28 dex scatter, and 0.46 dex above the "
        "Harris catalogue's clusters at the mass-to-light ratio measured for metal-poor globulars. It is "
        "every bound cluster that survives, whatever its age — no source read gives the age at which a "
        "survivor counts as a globular — and about half of it is under a gigayear old."
    ),
)

GC_COUNT_ESTIMATE = FieldDecl(
    name="gc_count_estimate", label="Globular clusters (estimate)", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The system mass over the mean present-day cluster mass Boylan-Kolchin 2018 assumes after Harris et "
        "al. 2017 — an estimate from a second number, which is why the acceptance row judges the mass and "
        "not this. The Harris catalogue lists 157."
    ),
)


def compute_survival(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    per_step = formed_per_step(ctx.fields["stars_formed_history"], ctx.grid.R)
    age = (ctx.grid.spec.t_max - ctx.grid.t) * 1.0e3  # Myr
    mu_ev = 1.0 - float(c["RETURN_FRACTION"])
    return {
        "gc_survival_fraction": survival_fraction(per_step, age, c, mu_ev),
        "gc_metal_poor_fraction": metal_poor_fraction(float(ctx.fields["halo_stellar_mass"]), c),
    }


def compute_globulars(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    bound = bound_mass(ctx.fields["stars_formed_history"], ctx.grid.R, float(c["CLUSTER_BOUND_FRACTION"]))
    mean = float(ctx.fields["gc_survival_fraction"]) * bound
    # Lognormal, so the width is in dex and the median is the mean relation (D109): the statistical row
    # is judged on the same number at any width.
    dex = ctx.rng("world_seed", "residual").normal(0.0, float(c["GC_SYSTEM_SCATTER"]))
    mass = mean * math.pow(10.0, float(dex))
    return {"gc_system_mass": mass, "gc_count_estimate": mass / float(c["GC_MEAN_MASS"])}


CLUSTER_SURVIVAL = IMPLEMENTATIONS.register(
    Stage(
        id="cluster_survival", slot="cluster_survival", checkpoint=5,
        about=(
            "How much of the mass that emerged in bound clusters survives dissolution to today, over the "
            "whole history, and the metal-poor share of what survives: what the inputs determine about the "
            "globular clusters, before any draw."
        ),
        compute=compute_survival,
        reads_constants=(
            "RETURN_FRACTION", "CLUSTER_DISRUPTION_T0", "CLUSTER_DISRUPTION_INDEX", "CLUSTER_MASS_FUNCTION_INDEX",
            "CLUSTER_MASS_FUNCTION_SCALE", "CLUSTER_MASS_MIN", "GC_HALO_MASS_RATIO", "GC_METAL_POOR_HALO_MASS_RATIO",
        ),
        requires=("stars_formed_history", "halo_stellar_mass"),
        publishes=(GC_SURVIVAL_FRACTION, GC_METAL_POOR_FRACTION),
    )
)

GLOBULAR_CLUSTERS = IMPLEMENTATIONS.register(
    Stage(
        id="globular_clusters", slot="globular_clusters", checkpoint=5,
        about=(
            "The globular cluster system: the bound clusters' mass times the fraction that survives, with a "
            "seeded residual at the scatter the halo relation shows, and the count that mass implies."
        ),
        compute=compute_globulars,
        reads_seeds=("world_seed",),
        reads_constants=("CLUSTER_BOUND_FRACTION", "GC_SYSTEM_SCATTER", "GC_MEAN_MASS"),
        requires=("stars_formed_history", "gc_survival_fraction"),
        publishes=(GC_SYSTEM_MASS, GC_COUNT_ESTIMATE),
    )
)
