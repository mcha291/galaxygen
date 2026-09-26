"""The stellar halo: the debris of the satellites the merger list says were accreted (checkpoint 4, S34,
BUILD_II Phase 5).

**What it is made of** (the brief's ruling (d)). The halo's stars are the accreted satellites' stars,
summed over ``mergers[]`` with the mass ratios and times the model already has; nothing here makes a
satellite an object (BUILD_II Phase 5 cut satellites, and this stage needs only their debris). No
stripped fraction is applied, because none was read: **each satellite's whole stellar mass is taken to
end in the halo**, Sagittarius's included although it is still being disrupted.

**How a mass ratio becomes a stellar mass** ``[inferred]``. A ``MergerEvent``'s mass ratio is the
satellite's mass over the host's; the model has no halo mass history, so the host's mass at the event is
read from what it has — the disc stars formed before the event, net of what they returned — and the
satellite is taken to hold the same fraction of its mass in stars as the host did then, so the ratio
applies to the stars as to the whole. The spheroid is not in that sum: the model gives it no formation
time (``halo.py``), so it cannot say whether it existed at the event. The alternative reading — the ratio
times a halo mass, times a stellar-to-halo relation for dwarfs, whose stellar fractions are far below a
Milky Way's ``[recall]`` — needs a halo mass history and a sourced relation the model has neither of, and is not
built; it is the direction the stellar halo's recorded miss points (row 33, debt #99).

**Its shape** is the oblate broken power law BHG16 §6.1.1 summarise from the star counts, normalised to
the mass: the inner slope, outer slope, break radius and flattening are each a level-0 constant with the
sentence it was read from. Published as the density in the plane, where the model's radial mesh lives.

**Derived, not seeded**, which is why it is not a field of the globular-cluster stage that reads
``world_seed``: provenance is per stage (D55), and rule A10 forbids labelling a function of the inputs
seeded.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS, MergerEvent
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC


def formed_per_step(stars_formed_history: np.ndarray, R: np.ndarray) -> np.ndarray:
    """The stellar mass locked at each step, net of what it returned, M☉: ∫ Σ 2πR dR over the disc."""
    locked = np.asarray(stars_formed_history, dtype=float) * PC_PER_KPC**2  # M☉ per kpc² per step
    return np.trapezoid(locked * 2.0 * math.pi * R[:, None], R, axis=0)


def satellite_stellar_masses(events: Sequence[MergerEvent], per_step: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Each event's stellar mass, M☉: its mass ratio times the host's disc stars formed strictly before it."""
    return np.array([e.mass_ratio * float(per_step[t < e.time].sum()) for e in events], dtype=float)


def broken_power_law_norm(mass: float, inner: float, outer: float, break_radius: float, flattening: float) -> float:
    """ρ_b in M☉/kpc³ such that the oblate broken power law ρ = ρ_b (m/r_b)^α, α the inner slope inside the
    break and the outer beyond, m² = R² + z²/q², holds ``mass``. Exact: M = 4π q ρ_b r_b³ [1/(3+α_in) −
    1/(3+α_out)], finite for α_in > −3 and α_out < −3."""
    if not (inner > -3.0 and outer < -3.0):
        raise ValueError("the broken power law holds a finite mass only for an inner slope above -3 and an outer below")
    shape = 1.0 / (3.0 + inner) - 1.0 / (3.0 + outer)
    return mass / (4.0 * math.pi * flattening * break_radius**3 * shape)


def midplane_density(R: np.ndarray, mass: float, inner: float, outer: float, break_radius: float, flattening: float) -> np.ndarray:
    """The broken power law in the plane (z = 0, so m = R), M☉/pc³."""
    rho_b = broken_power_law_norm(mass, inner, outer, break_radius, flattening)
    x = np.asarray(R, dtype=float) / break_radius
    return rho_b * np.where(x < 1.0, x**inner, x**outer) / PC_PER_KPC**3


HALO_STELLAR_MASS = FieldDecl(
    name="halo_stellar_mass", label="Stellar halo mass", unit="Msun", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Acceptance row 33. The stars of every satellite the merger list accreted, whole: each event's mass "
        "ratio times the disc stars the host had formed before it, the satellite taken to hold as large a "
        "share of its mass in stars as the host did. No stripped fraction is applied because none was read, "
        "and the spheroid is left out of the host's mass because the model gives it no formation time. Zero "
        "for an empty merger list, which is a legitimate galaxy. The surprise is how much the one major "
        "merger carries: a quarter of the host's early disc, which is more than the whole observed halo."
    ),
)

HALO_STELLAR_DENSITY = FieldDecl(
    name="halo_stellar_density", label="Stellar halo density in the plane", unit="Msun/pc3", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    about=(
        "The oblate broken power law Bland-Hawthorn & Gerhard 2016 summarise from the halo's star counts, "
        "its slope steepening beyond a break radius, flattened toward the plane, and normalised to the "
        "stellar halo mass; read at z = 0, where the radial mesh lies. A smooth average: the substructure "
        "that holds a large share of the real halo's stars is not in it, and neither is the tidal "
        "truncation the source reads beyond 100 kpc."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R, t = ctx.grid.R, ctx.grid.t
    per_step = formed_per_step(ctx.fields["stars_formed_history"], R)
    mass = float(satellite_stellar_masses(list(ctx.inputs["mergers"]), per_step, t).sum())
    density = midplane_density(
        R, mass, float(c["STELLAR_HALO_INNER_SLOPE"]), float(c["STELLAR_HALO_OUTER_SLOPE"]),
        float(c["STELLAR_HALO_BREAK_RADIUS"]), float(c["STELLAR_HALO_FLATTENING"]),
    )
    return {"halo_stellar_mass": mass, "halo_stellar_density": density}


STELLAR_HALO = IMPLEMENTATIONS.register(
    Stage(
        id="stellar_halo", slot="stellar_halo", checkpoint=4,
        about=(
            "The stellar halo as the debris of the accreted satellites: the merger list's mass ratios and "
            "times turned into stellar masses against the disc the host had built, summed whole, and spread "
            "in the broken power law the halo's star counts show."
        ),
        compute=compute,
        reads_inputs=("mergers",),
        reads_constants=(
            "STELLAR_HALO_INNER_SLOPE", "STELLAR_HALO_OUTER_SLOPE", "STELLAR_HALO_BREAK_RADIUS", "STELLAR_HALO_FLATTENING",
        ),
        requires=("stars_formed_history",),
        publishes=(HALO_STELLAR_MASS, HALO_STELLAR_DENSITY),
    )
)
