"""The galactic habitable zone: built from sourced criteria and deliberately unjudged (checkpoint 6, S30).

BUILD_II Phase 6 and its ruling (b): the zone was in the original design as derivable from
metallicity plus the supernova rate (GALAXY_INPUTS.md §4b, verdict A) and was never built. It
is built here and **given no acceptance row**: nobody has measured the Galaxy's habitable zone,
so any target would be a model's number chosen with this model's answer already known (rules
B5, B9). Each field's about line says so, so that the absence reads as a decision and not as an
oversight, the way row 21's did for twenty-three sessions.

**Whose criteria.** The ruling named Lineweaver, Fenner & Gibson 2004 first and Gowanlock,
Patton & McConnell 2011 as the alternative. The first could not be read (a scanned preprint, no
text mirror; only its abstract), so every criterion is Gowanlock et al.'s as read at S30 —
level 0 carries each with its section. Three ingredients, each per birth radius and birth time:

- **Metals** — the probability that a star forms a giant planet, flat at 3% below solar
  metallicity and rising as 10^(2[Fe/H]) above it (their §3.2, after Fischer & Valenti 2005 and
  Santos et al. 2004), read off the gas the star formed from (``feh_history``). The source turns
  it into a habitable-planet probability with ratios that were not read, so the weight here is
  relative: its shape across the disc is the source's, its absolute scale is not claimed.
- **Supernovae** — a planet within 8 pc of an average type II supernova, or within the distance a
  type Ia's brighter peak reaches, loses its ozone (their §3.1.2, eq. 5). The model's supernova
  histories (``supernovae.py``) over the midplane of the stellar layer the catalogue places its
  stars in give the rate of such events at a point; a planet survives a window of time with the
  Poisson probability of none [inferred: the source tracks individual supernovae instead].
- **Time** — complex life arises about 4 Gyr after the planet forms and needs 1.55 Gyr of unbroken
  ozone before that (their §3.4.1, §3.4); the window is the last 1.55 Gyr before the rise
  [inferred placement]. A star formed less than 4 Gyr ago carries no weight yet. The source's
  clock *restarts* after a sterilization (read in paraphrase, one pass), so a planet can become
  habitable later; this model counts only the first window, a lower bound on theirs.

**Two readings the source left open, recorded rather than chosen.** Eq. 5 was read twice as
d = 8 pc × 10^(−0.4 ΔM) and is used as read; a third reading described the distance as scaling
with the square root of the flux ratio, which would be 10^(−0.2 ΔM). The two give different
zones (S30's report carries both), and picking the one whose answer looks familiar would be
choosing with the answer known.

**What it is not.** Stars are weighted where they were *born*: migration, which the chemistry
applies to abundances, is not applied to the hazard, so a star's supernova history is its birth
ring's (Lineweaver et al. and Gowanlock et al. both place stars without migrating them either
[recall for the former]). A host star must outlive the 4 Gyr; the IMF fraction that does not is a
constant across the disc and is not removed, which is one more reason the weight is relative.
The model's own giant occurrence (``formation``, derived from the solid budget of a disc) is a
different answer to the metals question and is not used: the ruling asks for the source's.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.supernovae import YR_PER_GYR

_UNJUDGED = (
    " Deliberately unjudged: no acceptance row reads it, because nobody has measured the Galaxy's "
    "habitable zone and a target invented now would be chosen with the model's answer known "
    "(BUILD_II Phase 6, rules B5 and B9)."
)


def planet_probability(feh: np.ndarray, p_solar: float, index: float) -> np.ndarray:
    """Gowanlock et al. 2011 §3.2: ``p_solar`` below solar [Fe/H], ``p_solar 10^(index [Fe/H])`` above.

    Gas with no metals yet ([Fe/H] = −inf or NaN) is sub-solar and reads the flat tail, as the
    source's rule says. Capped at one, which the source does not state and which only gas above
    [Fe/H] = +0.76 would reach [inferred].
    """
    feh = np.nan_to_num(np.asarray(feh, dtype=float), nan=-np.inf)
    with np.errstate(over="ignore"):
        rising = p_solar * 10.0 ** (index * np.maximum(feh, 0.0))
    return np.minimum(np.where(feh >= 0.0, rising, p_solar), 1.0)


def sterilization_distance(magnitude: float, base_pc: float, m_std: float) -> float:
    """Eq. 5 of Gowanlock et al. 2011: d = 8 pc × 10^(−0.4 (M − M_std)), in pc."""
    return base_pc * 10.0 ** (-0.4 * (magnitude - m_std))


def cumulative_at(cum_edges: np.ndarray, when: np.ndarray, dt: float) -> np.ndarray:
    """``cum_edges`` (R, n_t + 1) sampled at the step edges, read at times ``when`` (n,) by linear interpolation."""
    n_t = cum_edges.shape[1] - 1
    x = np.clip(np.asarray(when, dtype=float) / dt, 0.0, float(n_t))
    i0 = np.minimum(np.floor(x).astype(int), n_t - 1)
    frac = x - i0
    return cum_edges[:, i0] * (1.0 - frac) + cum_edges[:, i0 + 1] * frac


# --- declarations -------------------------------------------------------------

PLANET_METALLICITY_PROBABILITY = FieldDecl(
    name="planet_metallicity_probability", label="Giant-planet probability from metals",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "t"),
    ramp=Ramp("viridis", scale="log", lo=0.03, hi=1.0), meaningful_zero=True,
    about=(
        "The habitable zone's metals ingredient: the probability that a star born at (R, t) forms a "
        "giant planet, from the [Fe/H] of the gas it formed from — 3% at any sub-solar metallicity, "
        "10^(2[Fe/H]) times that above solar (Gowanlock et al. 2011 §3.2, after Fischer & Valenti "
        "2005 and Santos et al. 2004). Their conversion to a habitable-planet probability was not "
        "read, so this is the giant-planet criterion itself." + _UNJUDGED
    ),
)
STERILIZATION_RATE_HISTORY = FieldDecl(
    name="sterilization_rate_history", label="Sterilizing supernovae at a point", unit="1/yr",
    kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "The habitable zone's supernova ingredient: how often a planet in the midplane at (R, t) "
        "has a supernova close enough to strip its ozone — 8 pc for an average core collapse, 5.4 "
        "times that for a type Ia's brighter peak (Gowanlock et al. 2011 eq. 5) — from the model's "
        "two supernova histories spread through the stellar layer the catalogue places its stars "
        "in. Type Ia dominate wherever they are more than a hundred-and-sixtieth of the core "
        "collapses, since the volume goes as the cube of the distance." + _UNJUDGED
    ),
)
HABITABILITY_HISTORY = FieldDecl(
    name="habitability_history", label="Habitability weight by birth place and time",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("viridis", scale="log"),
    meaningful_zero=True,
    about=(
        "The three ingredients multiplied for a star born at (R, t): its giant-planet probability, "
        "the chance its planet saw no sterilizing supernova in the 1.55 Gyr before complex life "
        "arises at 4 Gyr (Gowanlock et al. 2011 §3.4; the window's placement is inferred), and zero "
        "if it formed less than 4 Gyr ago. Relative, not a probability of complex life: the "
        "source's habitable-planet scaling was not read." + _UNJUDGED
    ),
)
HABITABILITY = FieldDecl(
    name="habitability", label="Habitability weight per star, by birth radius", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("viridis", scale="log"), meaningful_zero=True,
    about=(
        "The mean habitability weight of the stars born at each radius, over the whole history: "
        "where a star is likeliest to host complex life by Gowanlock et al. 2011's criteria. The "
        "inner disc has the metals and the supernovae; the outer disc the safety, and below solar "
        "metallicity the source's criterion does not penalise it for its few metals. Stars younger "
        "than the time complex life takes count as zero. By birth radius — stars are not migrated "
        "here." + _UNJUDGED
    ),
)
HABITABLE_SURFACE_DENSITY = FieldDecl(
    name="habitable_surface_density", label="Habitability-weighted stars formed", unit="Msun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "Stellar mass formed at each birth radius times its habitability weight: where the "
        "habitable planets are by number rather than by chance per star. Relative in scale, as "
        "the weight is." + _UNJUDGED
    ),
)
HABITABLE_FRACTION = FieldDecl(
    name="habitable_fraction", label="Mean habitability weight of the disc's stars",
    unit="dimensionless", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Habitability-weighted mass over all the mass the disc formed. A giant-planet probability "
        "times a survival: Gowanlock et al. put the fraction of stars hosting a habitable planet at "
        "~1.2%, but by a scaling this model has not read, so the two are not comparable." + _UNJUDGED
    ),
)
HABITABLE_ZONE_PEAK_RADIUS = FieldDecl(
    name="habitable_zone_peak_radius", label="Where most habitable stars were born",
    unit="kpc", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The birth radius of the annulus holding the most habitability-weighted stars: the peak by "
        "number, not by chance per star, which in this model still rises at the grid's edge where "
        "almost nothing forms. Lineweaver et al. 2004's abstract puts their zone at 7-9 kpc; "
        "Gowanlock et al. 2011 find habitable planets most numerous in the inner Galaxy. Neither "
        "is a target." + _UNJUDGED
    ),
)
HABITABLE_ZONE_HALF_RADIUS = FieldDecl(
    name="habitable_zone_half_radius", label="Radius holding half the habitable stars",
    unit="kpc", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The birth radius inside which half the habitability-weighted stars formed — the statistic "
        "Gowanlock et al. 2011 §4.3 quote, half their habitable planets inside 4.1 and 4.4 kpc in "
        "their models 1 and 4. Theirs is not a target either." + _UNJUDGED
    ),
)


def compute_habitable_zone(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    t = ctx.grid.t
    t_max, n_t = ctx.grid.spec.t_max, ctx.grid.spec.n_t
    dt = t_max / n_t
    c = ctx.constants

    p_planet = planet_probability(
        ctx.fields["feh_history"], float(c["PLANET_PROBABILITY_SOLAR"]), float(c["PLANET_METALLICITY_INDEX"])
    )

    # Sterilization volumes (kpc^3) and the midplane density of a sech^2(z/2h) layer, which
    # integrates to 4h: the profile systems.py places its stars with, at the thin disc's height.
    base, m_std = float(c["STERILIZATION_DISTANCE"]), float(c["STERILIZATION_MAGNITUDE"])
    d_cc = base / PC_PER_KPC  # the average SN II sits at M_std by the source's definition
    d_ia = sterilization_distance(float(c["IA_ABSOLUTE_MAGNITUDE"]), base, m_std) / PC_PER_KPC
    h = float(ctx.fields["thin_disc_scale_height"]) / PC_PER_KPC
    volume = 4.0 / 3.0 * math.pi
    rate = (
        np.asarray(ctx.fields["core_collapse_rate_history"], dtype=float) * volume * d_cc**3
        + np.asarray(ctx.fields["type_ia_rate_history"], dtype=float) * volume * d_ia**3
    ) / (4.0 * h)  # sterilizing events per year at a point in the midplane

    # Expected sterilizations in the ozone window before life arises, for a star born at each step.
    cum = np.concatenate([np.zeros((R.size, 1)), np.cumsum(rate, axis=1) * dt * YR_PER_GYR], axis=1)
    delay, window = float(c["COMPLEX_LIFE_DELAY"]), float(c["OZONE_CONTINUITY"])
    arises = t + delay
    expected = cumulative_at(cum, arises, dt) - cumulative_at(cum, arises - window, dt)
    old_enough = arises <= t_max
    weight = np.where(old_enough[None, :], p_planet * np.exp(-expected), 0.0)

    formed = np.asarray(ctx.fields["sfr_surface_density_history"], dtype=float)  # Msun/yr/kpc2 per step
    formed_total = formed.sum(axis=1)
    weighted = (formed * weight).sum(axis=1)
    per_star = np.where(formed_total > 0.0, weighted / np.where(formed_total > 0.0, formed_total, 1.0), 0.0)
    # M☉/yr/kpc² × Gyr -> M☉/pc²: 10⁹ yr per Gyr over 10⁶ pc² per kpc².
    surface = weighted * dt * YR_PER_GYR / PC_PER_KPC**2

    annulus = surface * 2.0 * math.pi * R
    total = float(annulus.sum())
    formed_all = float((formed_total * R).sum())
    if total > 0.0:
        cum_r = np.cumsum(annulus) / total
        half = float(np.interp(0.5, cum_r, R))
        peak = float(R[int(np.argmax(annulus))])
    else:  # nothing habitable anywhere: no radius, not radius zero (rule B9)
        half = peak = float("nan")
    return {
        "planet_metallicity_probability": p_planet,
        "sterilization_rate_history": rate,
        "habitability_history": weight,
        "habitability": per_star,
        "habitable_surface_density": surface,
        "habitable_fraction": float((weighted * R).sum()) / formed_all if formed_all > 0.0 else float("nan"),
        "habitable_zone_peak_radius": peak,
        "habitable_zone_half_radius": half,
    }


HABITABLE_ZONE = IMPLEMENTATIONS.register(
    Stage(
        id="habitable_zone",
        slot="habitable_zone",
        checkpoint=6,
        about=(
            "The galactic habitable zone by Gowanlock et al. 2011's criteria — metals for planets, "
            "no ozone-stripping supernova in the window before complex life, time for it to arise — "
            "over every birth radius and time. Built and deliberately unjudged: no acceptance row "
            "names it, because no measurement exists to judge it against."
        ),
        compute=compute_habitable_zone,
        reads_constants=(
            "PLANET_PROBABILITY_SOLAR", "PLANET_METALLICITY_INDEX", "STERILIZATION_DISTANCE",
            "STERILIZATION_MAGNITUDE", "IA_ABSOLUTE_MAGNITUDE", "COMPLEX_LIFE_DELAY", "OZONE_CONTINUITY",
        ),
        requires=(
            "feh_history", "core_collapse_rate_history", "type_ia_rate_history",
            "sfr_surface_density_history", "thin_disc_scale_height",
        ),
        publishes=(
            PLANET_METALLICITY_PROBABILITY, STERILIZATION_RATE_HISTORY, HABITABILITY_HISTORY,
            HABITABILITY, HABITABLE_SURFACE_DENSITY, HABITABLE_FRACTION,
            HABITABLE_ZONE_PEAK_RADIUS, HABITABLE_ZONE_HALF_RADIUS,
        ),
    )
)
