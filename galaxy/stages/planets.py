"""Planets: protoplanetary discs, core accretion, and what a system is made of (checkpoint 6).

GALAXY_INPUTS.md §12 settles the shape of this stage before a line of it is
written, and three of its rulings are load-bearing here.

**The object half is chaotic, not merely scattered.** Identical initial conditions
give different systems, so the architecture is a seeded draw by construction and
its checks are statistical by nature rather than by concession. That is why the
stage splits in two, exactly as S5's did: ``formation`` publishes what the inputs
determine — where in the galaxy giants are possible, and when — and ``planets``
publishes the seeded systems themselves. A stage that reads a seed publishes
seeded fields (rule A10, enforced by ``graph.py``), so the split is what keeps the
occurrence fields honestly *derived*.

**Metallicity is inherited, and the coupling is not imposed.** §12 quotes
occurrence going as 10^(β[Fe/H]) with β ≈ 2, and it would have been easy to write
that law down. Nothing here does. Metallicity enters once, where it physically
acts — the solid mass a disc contains is its mass times its metal fraction — and
occurrence comes out as the probability that this solid budget clears the
critical core mass, which is a threshold on a log-normal and therefore a probit
in [Fe/H]. The slope is then a *measurement* of the model, published as
``giant_occurrence_index``, and it can disagree with the literature (rule A3: if
it can be derived, derive it; rule B11: a relation that fits can still be the
wrong relation).

**No integrator.** Spacing is the mutual-Hill criterion and mass is the isolation
mass, both closed-form. §12 forbids N-body outright: the moment one enters the
loop, rule A1 is gone and the cost model is void.

**Belts are not placed, they are what a giant prevented.** Given the giants, the
asteroid analogue lies between the 4:1 and 2:1 resonances of the innermost one
and the Kuiper analogue starts at the 3:2 of the outermost. Zero inputs, zero
seeds, and the Solar System's numbers fall out of it (``tests/test_planets.py``).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.special import normal_cdf
from galaxy.core.stage import Context, Stage
from galaxy.stages.systems import CATALOGUE_SAMPLE, CELL_SECTORS, cell_counts

# Conversions. A factor is a factual claim and carries a citation (units.py holds
# none for exactly that reason).
EARTH_MASSES_PER_SOLAR = 332946.0  # [recall: M☉/M⊕, IAU nominal values]
EARTH_RADII_PER_SOLAR = 109.076  # [recall: R☉/R⊕]
DAYS_PER_YEAR = 365.25
# Equilibrium temperature at 1 AU from a solar-luminosity star, for a disc that
# reprocesses starlight: T(a) = 278 K (L/L☉)^¼ (a/AU)^-½ [recall: the standard
# passive-disc scaling; it puts the Solar System's ice line near 2.7 AU].
DISC_TEMPERATURE_1AU = 278.0
# Main-sequence mass–luminosity, L ∝ M^3.5 [recall: the standard fit for
# 0.5-2 M☉; it is used here only through L^¼, which softens it to M^0.875].
LUMINOSITY_INDEX = 3.5
SLOTS = 8  # zones per system; §12's benchmark uses tens and the architecture is insensitive
# The mass the literature's occurrence numbers are quoted for. The galaxy's *mean*
# star is an M dwarf (0.59 M☉), and giant occurrence around one is far lower — so
# the scalars below are published at solar mass, where 5% and 25% mean something,
# while the fields are published for the mean star, which is what the galaxy has.
QUOTED_STAR_MASS = 1.0
ATMOSPHERES: tuple[str, ...] = ("none", "thin", "volatile", "hydrogen")
# Escape parameter above which a planet keeps a heavy atmosphere over Gyr:
# v_esc / v_thermal(CO₂ at T_eq). Ten rather than six because six retains an
# atmosphere on a Mercury analogue and ten does not [inferred; the Solar System
# check is tests/test_planets.py::test_the_solar_system_lands_in_the_right_classes].
ESCAPE_PARAMETER = 10.0
CO2_THERMAL_1AU = 0.412  # km/s, sqrt(3kT/μ) for CO₂ at 278 K [recall: kinetic theory]
EARTH_ESCAPE_VELOCITY = 11.186  # km/s [recall]
# Mean-motion resonances that clear a belt: the asteroid analogue is bounded by
# the 4:1 and 2:1 of the innermost giant, the Kuiper analogue starts at the 3:2 of
# the outermost. a_res = a_giant (q/p)^(2/3) — Kepler's third law, nothing more.
ASTEROID_RESONANCES = (4.0, 2.0)
KUIPER_RESONANCE = 2.0 / 3.0


def luminosity(star_mass: np.ndarray | float) -> np.ndarray:
    """Main-sequence luminosity in L☉ from mass in M☉."""
    return np.asarray(star_mass, dtype=float) ** LUMINOSITY_INDEX


def ice_line(star_mass: np.ndarray | float, ice_temperature: float) -> np.ndarray:
    """Where water condenses, in AU. Derived from the star, which is why occurrence depends on it."""
    return (DISC_TEMPERATURE_1AU / ice_temperature) ** 2 * np.sqrt(luminosity(star_mass))


def _solid_weight(inner: np.ndarray, outer: np.ndarray) -> np.ndarray:
    """∫2πr·Σ dr for Σ ∝ r^-3/2, up to the normalisation: proportional to √outer − √inner."""
    return np.sqrt(np.maximum(outer, 0.0)) - np.sqrt(np.maximum(inner, 0.0))


def solid_budget(
    star_mass: np.ndarray | float,
    feh: np.ndarray | float,
    disc_mass_fraction: float,
    solar_metallicity: float,
    efficiency: float,
    ice_temperature: float,
    ice_boost: float,
    inner_edge: float,
    outer_edge: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solid mass in M⊕: (total, beyond the ice line, ice-line radius) for a median disc.

    Metallicity enters here and nowhere else. Everything the model says about
    [Fe/H] is a consequence of this one multiplication.
    """
    mass = np.asarray(star_mass, dtype=float)
    z = solar_metallicity * 10.0 ** np.asarray(feh, dtype=float)
    total = disc_mass_fraction * mass * z * efficiency * EARTH_MASSES_PER_SOLAR
    r_ice = ice_line(mass, ice_temperature)
    r_ice = np.clip(r_ice, inner_edge, outer_edge)
    inner_w = _solid_weight(np.full_like(r_ice, inner_edge), r_ice)
    outer_w = ice_boost * _solid_weight(r_ice, np.full_like(r_ice, outer_edge))
    share = np.where(inner_w + outer_w > 0.0, outer_w / (inner_w + outer_w), 0.0)
    return total, total * share, r_ice


def giant_zone_share(star_mass: np.ndarray | float, constants: Mapping[str, float]) -> np.ndarray:
    """Share of a disc's solids held by its most massive zone beyond the ice line.

    It depends on the *star* and not on its metallicity: the zone edges are fixed
    and the ice line moves with luminosity alone, while metallicity scales every
    zone together. Splitting it out is what lets occurrence be evaluated on an
    800 000-cell history without building an 800 000 × 8 array of zones for it.
    """
    mass = np.atleast_1d(np.asarray(star_mass, dtype=float))
    inner, outer = constants["DISC_INNER_EDGE"], constants["DISC_OUTER_EDGE"]
    r_ice = np.clip(ice_line(mass, constants["ICE_LINE_TEMPERATURE"]), inner, outer)
    edges = zone_edges(inner, outer)
    zones = zone_solids(edges, r_ice, np.ones_like(mass), constants["ICE_BOOST"])
    beyond = np.sqrt(edges[:-1] * edges[1:])[None, :] > r_ice[:, None]
    share = np.max(np.where(beyond, zones, 0.0), axis=1)
    return share.reshape(np.shape(star_mass)) if np.shape(star_mass) else float(share[0])


def giant_probability(
    feh: np.ndarray | float,
    star_mass: np.ndarray | float,
    constants: Mapping[str, float],
) -> np.ndarray:
    """Probability that a star of this metallicity and mass hosts a giant.

    Not an occurrence law. A giant is a zone whose solids clear the critical core
    mass beyond the ice line, the disc mass is log-normal about its median, and so
    the chance is a normal CDF in log mass — a probit in [Fe/H], because the solid
    budget is proportional to 10^[Fe/H]. The steepness belongs to the disc-mass
    scatter and to nothing that was fitted.

    It reads the criterion off the same ``zone_solids`` the drawn systems are built
    from, rather than restating it: two definitions of what a giant is would drift,
    and ``giant_fraction_sample`` is published to catch exactly that (rule B3).
    """
    total, _, _ = solid_budget(
        star_mass, feh,
        constants["DISC_MASS_FRACTION"], constants["SOLAR_METALLICITY"],
        constants["PLANETESIMAL_EFFICIENCY"], constants["ICE_LINE_TEMPERATURE"],
        constants["ICE_BOOST"], constants["DISC_INNER_EDGE"], constants["DISC_OUTER_EDGE"],
    )
    best = total * giant_zone_share(star_mass, constants)
    critical = constants["CORE_CRITICAL_MASS"]
    scatter = constants["DISC_MASS_SCATTER"]
    with np.errstate(divide="ignore", invalid="ignore"):
        margin = np.log10(np.where(best > 0.0, best, np.nan) / critical) / scatter
    return np.where(np.isfinite(margin), normal_cdf(margin), 0.0)


# --- the derived half: where giants are possible, and when --------------------

GIANT_OCCURRENCE = FieldDecl(
    name="giant_occurrence", label="Giant-planet occurrence", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("plasma"), meaningful_zero=True,
    about=(
        "Fraction of present-day stars at this radius that host a giant planet, for a star of the "
        "galaxy's mean stellar mass. It is the metallicity gradient seen through core accretion: "
        "the inner disc is metal-rich and makes giants, the outer disc is not and does not. "
        "Nothing here is an occurrence law — this is the probability that a log-normal disc's "
        "solids clear the critical core mass (rule A3)."
    ),
)

GIANT_OCCURRENCE_HISTORY = FieldDecl(
    name="giant_occurrence_history", label="Giant occurrence by birth radius and time",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("plasma"),
    meaningful_zero=True,
    about=(
        "The same probability for a star born at this radius and time. This is what the whole "
        "chemistry stage was for: giant planets were impossible in the early disc and became "
        "possible as it enriched, and the front moves outward. GALAXY_INPUTS.md §12 calls it the "
        "payoff; acceptance rows 22 and 23 say the gradient it rests on is a third too shallow "
        "(debt #15), so the front's *position* inherits that error."
    ),
)

GIANT_OCCURRENCE_SUN = FieldDecl(
    name="giant_occurrence_sun", label="Giant occurrence at R₀", unit="dimensionless",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Occurrence for a **solar-mass** star at [Fe/H] = 0, which is what the observed ~5% is "
        "quoted for [recall: GALAXY_INPUTS.md §12, citing the Adibekyan review]. "
        "the stage's one fitted constant is calibrated to it, so this is a check that the "
        "calibration took, not independent evidence. The galaxy's mean star is an M dwarf and its occurrence "
        "is an order of magnitude lower — that is the giant_occurrence field, and it is a "
        "prediction."
    ),
)

GIANT_OCCURRENCE_RICH = FieldDecl(
    name="giant_occurrence_rich", label="Giant occurrence at [Fe/H] = +0.5",
    unit="dimensionless", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Occurrence for a metal-rich star, where the observed value is ~25%. This one *is* a "
        "prediction: the calibration fixed the level at [Fe/H] = 0 and the disc-mass scatter "
        "decides how fast it rises from there. See debt #25 — the two relations §12 cites cannot "
        "both hold, and this number says which one the mechanism agrees with."
    ),
)

GIANT_OCCURRENCE_INDEX = FieldDecl(
    name="giant_occurrence_index", label="Occurrence metallicity index β", unit="dimensionless",
    kind=Kind.SCALAR,
    about=(
        "d log₁₀(occurrence) / d[Fe/H] at solar metallicity, measured on the model rather than "
        "assumed. §12 quotes β ≈ 2 from Fischer & Valenti; the same section's endpoints (5% at 0, "
        "25% at +0.5) require β ≈ 1.4. They are different claims and this is the instrument that "
        "says which the mechanism reproduces (rule B11)."
    ),
)

ICE_LINE_SUN = FieldDecl(
    name="ice_line_sun", label="Ice line of a solar-mass star", unit="AU", kind=Kind.SCALAR,
    about=(
        "Where water condenses around a solar-mass star: 2.67 AU, from the star's luminosity and the "
        "condensation temperature of water alone. The Solar System's is usually quoted near 2.7 AU, which is "
        "the one number in this stage that can be checked against something everybody knows. A "
        "lighter star's ice line is closer in, and that is why occurrence depends on stellar mass."
    ),
)


def compute_formation(ctx: Context) -> Mapping[str, Any]:
    constants = {k: ctx.constants[k] for k in FORMATION_CONSTANTS}
    mean_mass = float(ctx.fields["mean_stellar_mass"])
    feh_now = ctx.fields["feh_stars_young"]
    history = ctx.fields["feh_history"]

    occurrence = giant_probability(feh_now, mean_mass, constants)
    occurrence_history = giant_probability(history, mean_mass, constants)

    # The scalars are the literature's comparison, so they take the literature's
    # star: solar mass. The same function draws both, so a scalar cannot drift
    # from the picture beside it.
    at_sun = float(giant_probability(0.0, QUOTED_STAR_MASS, constants))
    rich = float(giant_probability(0.5, QUOTED_STAR_MASS, constants))
    step = 0.05
    lo = float(giant_probability(-step, QUOTED_STAR_MASS, constants))
    hi = float(giant_probability(step, QUOTED_STAR_MASS, constants))
    index = (math.log10(hi) - math.log10(lo)) / (2.0 * step) if lo > 0.0 and hi > 0.0 else float("nan")
    return {
        "giant_occurrence": occurrence,
        "giant_occurrence_history": occurrence_history,
        "giant_occurrence_sun": at_sun,
        "giant_occurrence_rich": rich,
        "giant_occurrence_index": index,
        "ice_line_sun": float(ice_line(QUOTED_STAR_MASS, ctx.constants["ICE_LINE_TEMPERATURE"])),
    }


FORMATION_CONSTANTS = (
    "DISC_MASS_FRACTION", "DISC_MASS_SCATTER", "PLANETESIMAL_EFFICIENCY", "CORE_CRITICAL_MASS",
    "ICE_LINE_TEMPERATURE", "ICE_BOOST", "DISC_INNER_EDGE", "DISC_OUTER_EDGE", "SOLAR_METALLICITY",
)

FORMATION = IMPLEMENTATIONS.register(
    Stage(
        id="formation", slot="formation", checkpoint=6,
        about=(
            "Where and when giant planets are possible: core accretion applied to the metallicity "
            "the chemistry stage published. Derived — no seed, no draw (§12's field half)."
        ),
        compute=compute_formation,
        reads_constants=FORMATION_CONSTANTS,
        requires=("feh_stars_young", "feh_history", "mean_stellar_mass"),
        publishes=(
            GIANT_OCCURRENCE, GIANT_OCCURRENCE_HISTORY, GIANT_OCCURRENCE_SUN,
            GIANT_OCCURRENCE_RICH, GIANT_OCCURRENCE_INDEX, ICE_LINE_SUN,
        ),
    )
)


# --- the seeded half: the systems themselves ----------------------------------

# Mass–radius, in Earth units. Rocky worlds compress; volatile-rich ones do not;
# above roughly half a Saturn the radius stops growing because degeneracy takes
# over [recall: Chen & Kipping 2017; Weiss & Marcy 2014]. It is good to ~10% on
# Jupiter, which is a rendering-grade relation and is used for nothing else.
ROCKY_MAX = 2.0
GIANT_MIN = 130.0
ROCKY_INDEX, VOLATILE_INDEX, GIANT_INDEX = 0.28, 0.5, 0.05
# Tidal locking: inside this radius a planet's rotation is its orbit, for a
# solar-mass star at 4.5 Gyr [recall: the Kasting et al. 1993 locking-radius
# scaling, ~0.06 AU, weak in both mass and age].
LOCK_RADIUS_1MSUN = 0.06
VOLATILE_RICH, VOLATILE_POOR = 0.5, 0.001  # ice mass fraction inside and outside the ice line
# M⊕: the smallest body this model calls a planet. Mercury is 0.055 M⊕ and is one;
# Pluto is 0.0022 and is not [recall: the IAU's orbit-clearing criterion is what
# separates them, and it lands between these two by two orders of magnitude].
PLANET_MIN_MASS = 0.05


def planet_radius(mass: np.ndarray) -> np.ndarray:
    """Radius in R⊕ from mass in M⊕, over three regimes."""
    m = np.asarray(mass, dtype=float)
    rocky = np.power(np.maximum(m, 1e-9), ROCKY_INDEX)
    at_rocky = ROCKY_MAX**ROCKY_INDEX
    volatile = at_rocky * np.power(np.maximum(m, ROCKY_MAX) / ROCKY_MAX, VOLATILE_INDEX)
    at_giant = at_rocky * (GIANT_MIN / ROCKY_MAX) ** VOLATILE_INDEX
    giant = at_giant * np.power(np.maximum(m, GIANT_MIN) / GIANT_MIN, GIANT_INDEX)
    return np.where(m <= ROCKY_MAX, rocky, np.where(m <= GIANT_MIN, volatile, giant))


def equilibrium_temperature(insolation: np.ndarray) -> np.ndarray:
    """T_eq in K from insolation in S⊕, for zero albedo — S^¼ and nothing else."""
    return DISC_TEMPERATURE_1AU * np.power(np.maximum(np.asarray(insolation, dtype=float), 0.0), 0.25)


def escape_parameter(mass: np.ndarray, radius: np.ndarray, temperature: np.ndarray) -> np.ndarray:
    """Escape velocity over the thermal speed of CO₂: whether a heavy atmosphere stays."""
    v_escape = EARTH_ESCAPE_VELOCITY * np.sqrt(np.maximum(mass, 0.0) / np.maximum(radius, 1e-9))
    v_thermal = CO2_THERMAL_1AU * np.sqrt(np.maximum(temperature, 1.0) / DISC_TEMPERATURE_1AU)
    return v_escape / v_thermal


def classify(mass: np.ndarray, radius: np.ndarray, insolation: np.ndarray, icy: np.ndarray, giant: np.ndarray) -> np.ndarray:
    """Atmosphere class as a category code. Derived: nothing here is drawn."""
    lam = escape_parameter(mass, radius, equilibrium_temperature(insolation))
    code = np.zeros(np.shape(mass), dtype=np.int64)  # "none"
    code = np.where(lam >= ESCAPE_PARAMETER, 1, code)  # "thin"
    code = np.where(icy & (mass >= 0.5), 2, code)  # "volatile"
    return np.where(giant, 3, code)  # "hydrogen"


def orbital_period(axis: np.ndarray, star_mass: np.ndarray) -> np.ndarray:
    """Kepler's third law, in days."""
    return DAYS_PER_YEAR * np.power(np.maximum(axis, 0.0), 1.5) / np.sqrt(np.maximum(star_mass, 1e-6))


def belts(giant_axes: Sequence[float], outer_edge: float) -> tuple[dict[str, float], ...]:
    """The regions a system's giants prevented from accreting (§12: derived, not modelled).

    The asteroid analogue lies between the innermost giant's 4:1 and 2:1 mean-motion
    resonances, and the Kuiper analogue starts at the outermost giant's 3:2. Both
    are Kepler's third law applied to a period ratio: a_res = a (q/p)^(2/3).
    """
    axes = sorted(float(a) for a in giant_axes if np.isfinite(a))
    if not axes:
        return ()
    inner, outer = axes[0], axes[-1]
    found = [{
        "kind": "asteroid",
        "inner": inner * ASTEROID_RESONANCES[0] ** (-2.0 / 3.0),
        "outer": inner * ASTEROID_RESONANCES[1] ** (-2.0 / 3.0),
    }]
    kuiper_inner = outer * KUIPER_RESONANCE ** (-2.0 / 3.0)
    if kuiper_inner < outer_edge:
        found.append({"kind": "kuiper", "inner": kuiper_inner, "outer": outer_edge})
    return tuple(found)


def zone_edges(inner_edge: float, outer_edge: float) -> np.ndarray:
    """The SLOTS annuli, spaced geometrically — the disc's own logarithmic zones.

    Real systems are roughly geometric in radius, and so is the disc: a linear
    layout would put seven of eight zones inside 4 AU. Nothing is *placed* here;
    this is the partition the solid budget is divided over, and where a planet
    ends up inside its zone is a draw.
    """
    return np.geomspace(inner_edge, outer_edge, SLOTS + 1)


def zone_solids(
    edges: np.ndarray, r_ice: np.ndarray, budget: np.ndarray, ice_boost: float
) -> np.ndarray:
    """Solid mass in each annulus, for Σ ∝ r^-3/2 with the jump across the ice line.

    Mass-conserving by construction: the annuli partition the disc, so the planets
    that form in them cannot between them contain more solids than the disc had.
    """
    ice = np.asarray(r_ice, dtype=float)[:, None]
    lo = edges[None, :-1]
    hi = edges[None, 1:]
    dry = _solid_weight(np.minimum(lo, ice), np.minimum(hi, ice))
    icy = ice_boost * _solid_weight(np.maximum(lo, ice), np.maximum(hi, ice))
    weight = dry + icy
    total = weight.sum(axis=1, keepdims=True)
    return np.asarray(budget, dtype=float)[:, None] * np.divide(
        weight, total, out=np.zeros_like(weight), where=total > 0.0
    )


def architecture(
    star_mass: np.ndarray,
    feh: np.ndarray,
    residual: np.ndarray,
    jitter: np.ndarray,
    constants: Mapping[str, float],
) -> dict[str, np.ndarray]:
    """One system per star: the disc's solids partitioned into planets, then filtered.

    Three steps, all closed-form, because §12 forbids an integrator outright.

    1. **Partition.** Each geometric zone gets the solids it contains. A zone
       straddling the ice line gets both sides of the jump.
    2. **Runaway.** A zone beyond the ice line whose solids clear the critical core
       mass accretes the gas of the same zone — its solids divided by the metal
       fraction, which is where the disc's gas-to-dust ratio comes back in.
    3. **Filter.** Neighbours closer than HILL_SEPARATION mutual Hill radii cannot
       both survive, so they merge: one planet at the mass-weighted radius. This is
       §12's stability criterion used as a filter, which is what it is for.

    The isolation mass is deliberately *not* used to set planet masses. It is the
    mass of an embryo, ~0.02 M⊕ at 1 AU in this disc, and a planet is what a swarm
    of embryos becomes — using it directly builds a system of gravel.
    """
    n = len(star_mass)
    inner_edge = constants["DISC_INNER_EDGE"]
    outer_edge = constants["DISC_OUTER_EDGE"]
    boost = constants["ICE_BOOST"]
    critical = constants["CORE_CRITICAL_MASS"]
    metal = constants["SOLAR_METALLICITY"] * 10.0 ** np.asarray(feh, dtype=float)

    total, _, r_ice = solid_budget(
        star_mass, feh,
        constants["DISC_MASS_FRACTION"], constants["SOLAR_METALLICITY"],
        constants["PLANETESIMAL_EFFICIENCY"], constants["ICE_LINE_TEMPERATURE"],
        boost, inner_edge, outer_edge,
    )
    budget = total * 10.0 ** (constants["DISC_MASS_SCATTER"] * np.asarray(residual, dtype=float))

    edges = zone_edges(inner_edge, outer_edge)
    solids = zone_solids(edges, r_ice, budget, boost)
    # Where in its zone: geometric centre, jittered inside it. A zone is a wide
    # place and the model has no opinion about which part of it a planet occupies.
    centre = np.sqrt(edges[:-1] * edges[1:])[None, :]
    span = np.sqrt(edges[1:] / edges[:-1])[None, :]
    axis = centre * span ** (0.6 * (jitter - 0.5))

    icy = axis > np.asarray(r_ice, dtype=float)[:, None]
    runaway = icy & (solids >= critical)
    mass = np.where(runaway, solids / np.maximum(metal, 1e-6)[:, None], solids)
    alive = solids >= PLANET_MIN_MASS

    # The stability filter: one sweep outward, each zone compared against the last
    # planet that survived rather than against the slot beside it. Comparing
    # neighbouring *slots* leaves a few per cent of pairs crowded, because a merge
    # makes the surviving planet heavier and its Hill radius wider than the pair
    # that was already checked. Carrying the survivor forward is exact in one pass,
    # which keeps this bounded and cheap (rule A1).
    star_earths = np.asarray(star_mass, dtype=float) * EARTH_MASSES_PER_SOLAR
    separation = constants["HILL_SEPARATION"]
    rows = np.arange(n)
    last = np.zeros(n, dtype=int)
    for j in range(1, SLOTS):
        left_mass = mass[rows, last]
        left_axis = axis[rows, last]
        both = alive[rows, last] & alive[:, j]
        hill = 0.5 * (left_axis + axis[:, j]) * np.cbrt((left_mass + mass[:, j]) / (3.0 * star_earths))
        crowded = both & ((axis[:, j] - left_axis) < separation * hill)
        merged = left_mass + mass[:, j]
        weighted = np.where(
            merged > 0.0,
            (left_mass * left_axis + mass[:, j] * axis[:, j]) / np.maximum(merged, 1e-30),
            left_axis,
        )
        mass[rows, last] = np.where(crowded, merged, left_mass)
        axis[rows, last] = np.where(crowded, weighted, left_axis)
        runaway[rows, last] |= crowded & runaway[:, j]
        icy[rows, last] |= crowded & icy[:, j]
        alive[:, j] &= ~crowded
        last = np.where(alive[:, j], j, last)

    axis = np.where(alive, axis, np.nan)
    return {
        "axis": axis,
        "mass": np.where(alive, mass, 0.0),
        "giant": alive & runaway,
        "icy": alive & icy,
        "count": alive.sum(axis=1),
    }


def system_columns(
    star_mass: np.ndarray,
    feh: np.ndarray,
    age: np.ndarray,
    draws: Mapping[str, np.ndarray],
    constants: Mapping[str, float],
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Every published planet quantity for a block of stars, plus each star's planet count."""
    built = architecture(star_mass, feh, draws["disc"], draws["spacing"], constants)
    keep = np.isfinite(built["axis"])
    order = np.argsort(~keep, axis=1, kind="stable")  # planets first, gaps after, slot order kept
    rows = np.repeat(np.arange(len(star_mass))[:, None], SLOTS, axis=1)

    def flat(values: np.ndarray) -> np.ndarray:
        return np.take_along_axis(values, order, axis=1)[np.take_along_axis(keep, order, axis=1)]

    axis = flat(built["axis"])
    mass = flat(built["mass"])
    giant = flat(built["giant"])
    icy = flat(built["icy"])
    star = flat(rows)
    host_mass = np.asarray(star_mass, dtype=float)[star]
    host_age = np.asarray(age, dtype=float)[star]

    radius = planet_radius(mass)
    insolation = luminosity(host_mass) / np.maximum(axis, 1e-6) ** 2
    period = orbital_period(axis, host_mass)
    lock_radius = LOCK_RADIUS_1MSUN * np.cbrt(host_mass) * np.power(np.maximum(host_age, 0.01) / 4.5, 1.0 / 6.0)
    spun = 10.0 ** (0.3 * flat(draws["rotation"]))  # ~1 day, log-normal: accretion, then tides
    rotation = np.where(axis < lock_radius, period, spun)
    # Obliquity: giant impacts leave a terrestrial anywhere on the sphere; a giant
    # keeps the angular momentum it accreted with.
    u = flat(draws["obliquity"])
    obliquity = np.degrees(np.arccos(np.where(giant, 1.0 - 0.3 * u, 1.0 - 2.0 * u)))

    columns = {
        "planet_semi_major_axis": axis,
        "planet_mass": mass,
        "planet_radius": radius,
        "planet_insolation": insolation,
        "planet_orbital_period": period,
        "planet_rotation_period": rotation,
        "planet_obliquity": obliquity,
        "planet_volatile_fraction": np.where(icy, VOLATILE_RICH, VOLATILE_POOR),
        "planet_atmosphere": classify(mass, radius, insolation, icy, giant),
    }
    return columns, built["count"].astype(np.int64)


def draw_block(seed: int, cell: int, count: int) -> dict[str, np.ndarray]:
    """The seeded draws for one cell's stars: one stream per property, as S5 established.

    A star is ``(cell, index)`` (D60) and its planets are at ``index`` in every one
    of these streams, so a system is the same whether the cell was materialised
    alone or inside a sweep, and a smaller sample is a prefix of a larger one. The
    slot block is fixed width for the same reason: star *i* owns
    ``[i·SLOTS, (i+1)·SLOTS)`` whatever its neighbours turned out to be.
    """
    def stream(name: str) -> np.random.Generator:
        return _seeds.rng(seed, "cell", int(cell), name)

    return {
        "disc": stream("disc").standard_normal(count),
        "spacing": stream("spacing").random(count * SLOTS).reshape(count, SLOTS),
        "rotation": stream("rotation").standard_normal(count * SLOTS).reshape(count, SLOTS),
        "obliquity": stream("obliquity").random(count * SLOTS).reshape(count, SLOTS),
    }


def materialise(
    stars: Mapping[str, np.ndarray],
    counts: Sequence[tuple[int, int]],
    seed: int,
    constants: Mapping[str, float],
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Planets for a catalogue laid out as ``counts``, in the same row order as its stars.

    The *draws* are per cell, because that is what makes a star's system its own
    (D60). The *physics* is not: it runs once over every star in the sample. Doing
    it per cell instead cost 1.6 s of a 2.5 s model run — five hundred cells each
    paying numpy's per-call overhead on eight-star arrays — for arithmetic that
    vectorises perfectly across the whole sample. §12 says as much in its cost
    table: vectorise *across* systems, since a planets stage is many objects with
    few cells each.
    """
    total = sum(n for _, n in counts)
    if not total:
        empty = np.zeros(0)
        return (
            {n: (empty.astype(np.int64) if n == "planet_atmosphere" else empty) for n in PLANET_COLUMNS},
            np.zeros(0, dtype=np.int64),
        )
    draws = {
        "disc": np.empty(total),
        "spacing": np.empty((total, SLOTS)),
        "rotation": np.empty((total, SLOTS)),
        "obliquity": np.empty((total, SLOTS)),
    }
    at = 0
    for cell, count in counts:
        block = draw_block(seed, cell, count)
        for name, values in block.items():
            draws[name][at : at + count] = values
        at += count
    return system_columns(
        stars["star_mass"], stars["star_metallicity"], stars["star_age"], draws, constants
    )


def one_system(
    stars: Mapping[str, np.ndarray],
    index: int,
    cell: int,
    seed: int,
    constants: Mapping[str, float],
) -> tuple[dict[str, np.ndarray], tuple[dict[str, float], ...]]:
    """One star's planets and its belts — what opening a system costs, and no more.

    ``stars`` is that cell's catalogue; the draws are the cell's own streams, so the
    system is identical to the one a whole-galaxy materialisation would give it.
    """
    count = len(stars["star_mass"])
    columns, per_star = materialise(stars, ((cell, count),), seed, constants)
    start = int(np.sum(per_star[:index]))
    end = start + int(per_star[index])
    mine = {name: values[start:end] for name, values in columns.items()}
    giants = mine["planet_semi_major_axis"][mine["planet_atmosphere"] == ATMOSPHERES.index("hydrogen")]
    return mine, belts(giants, constants["DISC_OUTER_EDGE"])


def _column(name, label, unit, about, ramp=Ramp("viridis")):
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="planet",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about)


PLANET_SEMI_MAJOR_AXIS = _column(
    "planet_semi_major_axis", "Semi-major axis", "AU",
    "Where the chain put it: the inner edge, then each step the previous planet's own Hill radius "
    "times the stability separation. Closed-form, because §12 forbids an integrator.",
    ramp=Ramp("cividis", scale="log"),
)
PLANET_MASS = _column(
    "planet_mass", "Mass", "Mearth",
    "The isolation mass of its feeding zone — and, if that cleared the critical core beyond the "
    "ice line, the zone's gas as well, which is its solids divided by the metal fraction. Nothing "
    "about the mass is drawn; the disc it formed in is.",
    ramp=Ramp("inferno", scale="log"),
)
PLANET_RADIUS = _column(
    "planet_radius", "Radius", "Rearth",
    "From the mass through a three-regime relation good to about 10% on Jupiter. It exists so the "
    "atmosphere class can be decided by an escape velocity, and for drawing.",
    ramp=Ramp("magma", scale="log"),
)
PLANET_INSOLATION = _column(
    "planet_insolation", "Insolation", "Searth",
    "L/a² in Earth units, from the star's own mass. The habitable zone is not published as a "
    "category because where it lies is a claim about atmospheres this model does not make.",
    ramp=Ramp("plasma", scale="log"),
)
PLANET_ORBITAL_PERIOD = _column(
    "planet_orbital_period", "Orbital period", "day",
    "Kepler's third law about the host mass. Published because it is what a system view labels an "
    "orbit with, and because a locked planet's rotation is exactly this.",
    ramp=Ramp("cividis", scale="log"),
)
PLANET_ROTATION_PERIOD = _column(
    "planet_rotation_period", "Rotation period", "day",
    "Seeded from accretion — log-normal about a day — unless the planet is inside the tidal "
    "locking radius for its star's mass and age, in which case it is the orbital period. Half "
    "derived, half drawn, and which one depends on where it is.",
    ramp=Ramp("cividis", scale="log"),
)
PLANET_OBLIQUITY = _column(
    "planet_obliquity", "Obliquity", "deg",
    "Seeded: giant impacts leave a terrestrial's axis anywhere on the sphere, while a giant keeps "
    "the angular momentum it accreted with and stays within about 45°. This is the clearest case "
    "in the model of a quantity with no deterministic value to have scatter about (§12).",
    ramp=Ramp("coolwarm"),
)
PLANET_VOLATILE_FRACTION = _column(
    "planet_volatile_fraction", "Volatile fraction", "dimensionless",
    "Ice mass fraction: high for anything that formed beyond its star's ice line, negligible for "
    "anything inside it. The model tracks where a planet formed, not where it drifted to.",
)
PLANET_ATMOSPHERE = FieldDecl(
    name="planet_atmosphere", label="Atmosphere", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="planet", categories=ATMOSPHERES, ramp=Palette(("#3d4451", "#7bb0d8", "#63c48a", "#e8b04c")),
    provenance="seeded",
    about=(
        "Derived from what the planet is and where: hydrogen for a runaway giant, volatile for an "
        "ice-rich world, thin where the escape velocity beats the thermal speed of CO₂ at its "
        "equilibrium temperature, none where it does not. The threshold is set so that a Mercury "
        "analogue keeps nothing and a Mars analogue keeps a little."
    ),
)
STAR_PLANET_COUNT = FieldDecl(
    name="star_planet_count", label="Planets", unit="count", kind=Kind.COLUMN, of="star",
    ramp=Ramp("greys"), meaningful_zero=True, provenance="seeded",
    about=(
        "How many planets this star of the catalogue has. It is what joins the two object classes: "
        "the planet columns run in star order, so this column's running total says which planets "
        "are whose without an identifier field."
    ),
)

PLANET_COLUMNS: tuple[str, ...] = (
    "planet_semi_major_axis", "planet_mass", "planet_radius", "planet_insolation",
    "planet_orbital_period", "planet_rotation_period", "planet_obliquity",
    "planet_volatile_fraction", "planet_atmosphere",
)

PLANET_COUNT_SAMPLE = FieldDecl(
    name="planet_count_sample", label="Planets in the catalogue", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about="How many planets the published star sample turned out to have. A sample count, not a galaxy's.",
)
MEAN_PLANETS_PER_STAR = FieldDecl(
    name="mean_planets_per_star", label="Planets per star", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "Averaged over the sample. Kepler's occurrence for planets of any size is of order one per "
        "star [recall], so this is the number that says whether the solid budget is plausible at "
        "all — and it is one of the two things the stage's fitted constant moves."
    ),
)
GIANT_FRACTION_SAMPLE = FieldDecl(
    name="giant_fraction_sample", label="Stars with a giant", unit="dimensionless", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "Fraction of the sample's stars hosting at least one runaway giant. It is the *drawn* "
        "counterpart of giant_occurrence, which is computed: the two must agree, and a test says "
        "so — a sample that traces the wrong density is still internally consistent (rule B3)."
    ),
)


def compute_planets(ctx: Context) -> Mapping[str, Any]:
    constants = {k: ctx.constants[k] for k in PLANETS_CONSTANTS}
    counts = cell_counts(
        ctx.fields["stellar_surface_density"], ctx.grid.R,
        int(ctx.seeds["systems_seed"]), CATALOGUE_SAMPLE,
    )
    columns, per_star = materialise(ctx.fields, counts, int(ctx.seeds["planets_seed"]), constants)
    giants = np.zeros(len(per_star), dtype=bool)
    if len(columns["planet_mass"]):
        hydrogen = columns["planet_atmosphere"] == ATMOSPHERES.index("hydrogen")
        which = np.repeat(np.arange(len(per_star)), per_star)
        giants[np.unique(which[hydrogen])] = True
    return {
        **columns,
        "star_planet_count": per_star.astype(float),
        "planet_count_sample": float(len(columns["planet_mass"])),
        "mean_planets_per_star": float(per_star.mean()) if len(per_star) else 0.0,
        "giant_fraction_sample": float(giants.mean()) if len(giants) else 0.0,
    }


PLANETS_CONSTANTS = FORMATION_CONSTANTS + ("HILL_SEPARATION",)

PLANETS = IMPLEMENTATIONS.register(
    Stage(
        id="planets", slot="planets", checkpoint=6,
        about=(
            "The systems themselves: one Hill-separated chain of isolation masses per star of the "
            "catalogue, seeded by planets_seed. §12's object half, which is chaotic by construction."
        ),
        compute=compute_planets,
        reads_seeds=("planets_seed", "systems_seed"),
        reads_constants=PLANETS_CONSTANTS,
        requires=(
            "stellar_surface_density", "star_mass", "star_metallicity", "star_age",
        ),
        publishes=(
            PLANET_SEMI_MAJOR_AXIS, PLANET_MASS, PLANET_RADIUS, PLANET_INSOLATION,
            PLANET_ORBITAL_PERIOD, PLANET_ROTATION_PERIOD, PLANET_OBLIQUITY,
            PLANET_VOLATILE_FRACTION, PLANET_ATMOSPHERE, STAR_PLANET_COUNT,
            PLANET_COUNT_SAMPLE, MEAN_PLANETS_PER_STAR, GIANT_FRACTION_SAMPLE,
        ),
    )
)
