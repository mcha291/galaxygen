"""Pattern: the bar and the spiral arms (checkpoint 4). The first seeded stage.

Two stages, not one, and the reason is a limitation worth naming.
``graph.py`` derives provenance **per stage**: a stage that reads a seed
publishes seeded fields, all of them. But the bar's *length* has no draw in it
while its *pattern speed* does, and acceptance row 15 is pointwise where rows 16
and 17 are statistical — so declaring the length seeded would be a false label on
a reproducible number (rule A10 forbids exactly that vagueness). Splitting the
derived half from the seeded half gets both labels right with the machinery that
exists; making provenance per-field is the alternative, and it is a contract
change that belongs to the audit (DECISIONS.md D55).

**Where the draws come from.** GALAXY_INPUTS.md §4b assigns bar pattern speed and
arm multiplicity to seeded draws rather than to inputs: the residual is real and
nobody would ever choose it. The consequence, stated there and honoured here, is
that the affected acceptance rows become *statistical* — the model must reproduce
the Milky Way within an ensemble, not exactly.

**Which seed.** ``pattern_seed``. GALAXY_INPUTS.md §5 says the pitch dispersion
comes from ``world_seed``, and it cannot: rerolling the arms would then invalidate
every checkpoint from 1 onwards, when the whole point of per-stage seeds is that
rerolling stage 4 invalidates 5 and 6 and nothing earlier (GALAXY_PLAN.md §3).
The registry and the plan agree on ``pattern_seed``; §5 is the outlier
(DECISIONS.md D56).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage

SHEAR_RADIUS_IN_SCALE_LENGTHS = 2.2  # ruling 3: take the scaled form
ARM_MULTIPLICITIES: tuple[float, ...] = (2.0, 4.0)


def shear_rate(R: np.ndarray, v: np.ndarray, at: float) -> float:
    """Γ = 1 − (R/v)(dv/dR): 0 for solid body, 1 for a flat curve, 1.5 for Keplerian."""
    dv = float(np.gradient(v, R)[int(np.argmin(np.abs(R - at)))])
    v_at = float(np.interp(at, R, v))
    return 1.0 - (at / v_at) * dv if v_at > 0.0 else float("nan")


def _scalar(name, label, unit, about, provenance="derived"):
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.SCALAR,
                     meaningful_zero=True, about=about, provenance=provenance)


# --- derived half -------------------------------------------------------------

BAR_HALF_LENGTH = _scalar(
    "bar_half_length", "Bar half-length", "kpc",
    "Acceptance row 15, and pointwise rather than statistical — which is why it lives in the "
    "derived stage. Scaled from the disc's own scale length; the disc-dominance link "
    "GALAXY_INPUTS.md §4b describes is published beside it but not modelled (debt #21).",
)

DISC_DOMINANCE = _scalar(
    "disc_dominance", "Disc share of v_c² at 2.2 R_d", "dimensionless",
    "How much of the rotation the baryons provide where the disc's own curve peaks. §4b makes "
    "this the first link in the chain to the pattern speed; it is measured here and unused, so "
    "that the missing link is visible rather than silently absent.",
)

SHEAR = _scalar(
    "shear_rate", "Shear rate Γ", "dimensionless",
    "1 − dln v/dln R at 2.2 R_d. Zero is solid-body rotation and 1 is a flat curve, so a value "
    "near 1 means the disc is shearing as a flat-curve galaxy does.",
)


def compute_bar(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    R_d = float(ctx.fields["thin_disc_scale_length"])
    at = SHEAR_RADIUS_IN_SCALE_LENGTHS * R_d
    total = np.asarray(ctx.fields["circular_velocity_resolved"])
    halo = np.asarray(ctx.fields["halo_circular_velocity"])
    v_total = float(np.interp(at, R, total))
    v_halo = float(np.interp(at, R, halo))
    return {
        "bar_half_length": float(ctx.constants["BAR_LENGTH_RATIO"]) * R_d,
        "disc_dominance": 1.0 - (v_halo / v_total) ** 2 if v_total > 0.0 else 0.0,
        "shear_rate": shear_rate(R, total, at),
    }


BAR = IMPLEMENTATIONS.register(
    Stage(
        id="bar", slot="bar", checkpoint=4,
        about=(
            "The bar's size and the disc's shear — everything about the pattern that has no draw "
            "in it. Split from the seeded half so that row 15 stays reproducible (D55)."
        ),
        compute=compute_bar,
        reads_constants=("BAR_LENGTH_RATIO",),
        requires=("thin_disc_scale_length", "circular_velocity_resolved", "halo_circular_velocity"),
        publishes=(BAR_HALF_LENGTH, DISC_DOMINANCE, SHEAR),
    )
)


# --- seeded half --------------------------------------------------------------

COROTATION = _scalar(
    "bar_corotation_radius", "Bar corotation radius", "kpc",
    "Acceptance row 17, statistical. The fast-bar ratio R_CR/a_bar is 1.2 ± 0.2, and that ± is "
    "observed scatter between galaxies rather than measurement error — so it is drawn, and the "
    "row is judged against an ensemble (debt #8).",
    provenance="seeded",
)

PATTERN_SPEED = _scalar(
    "bar_pattern_speed", "Bar pattern speed Ω_b", "km/s/kpc",
    "Acceptance row 16, statistical. Not drawn directly: it is v_c at the corotation radius "
    "divided by that radius, which is a definition, so all of its scatter is inherited from the "
    "fast-bar draw. Two galaxies with identical inputs differ here, and that is the point.",
    provenance="seeded",
)

PITCH_ANGLE = _scalar(
    "pitch_angle", "Spiral arm pitch angle", "deg",
    "Mean from the shear trend, dispersion drawn (ruling 3, PITCH_YU). **Because the trend is "
    "weak the draw dominates**, so arm winding is not a consequence of the mass distribution and "
    "anything reading this inherits a random component — the flag ruling 3 asks for. It is also a "
    "live instance of rule B11: a relation that fits the validation table can still be the wrong "
    "relation.",
    provenance="seeded",
)

ARM_MULTIPLICITY = _scalar(
    "arm_multiplicity", "Number of spiral arms", "count",
    "Swing amplification sets a preferred m and real galaxies at similar shear still differ, so "
    "§4b assigns this a seeded draw rather than an input. Two arms or four; nobody would choose it.",
    provenance="seeded",
)


def compute_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    a_bar = float(ctx.fields["bar_half_length"])
    total = np.asarray(ctx.fields["circular_velocity_resolved"])

    ratio = ctx.rng("pattern_seed", "fast_bar").normal(
        float(ctx.constants["FAST_BAR_RATIO"]), float(ctx.constants["FAST_BAR_SCATTER"])
    )
    corotation = max(float(ratio), 0.1) * a_bar
    v_cr = float(np.interp(corotation, R, total))

    gamma = float(ctx.fields["shear_rate"])
    pitch_mean = float(ctx.constants["PITCH_SHEAR_INTERCEPT"]) + float(ctx.constants["PITCH_SHEAR_SLOPE"]) * (gamma - 1.0)
    pitch = ctx.rng("pattern_seed", "pitch").normal(pitch_mean, float(ctx.constants["PITCH_SCATTER"]))

    arms = ARM_MULTIPLICITIES[int(ctx.rng("pattern_seed", "arms").integers(len(ARM_MULTIPLICITIES)))]

    return {
        "bar_corotation_radius": corotation,
        "bar_pattern_speed": v_cr / corotation if corotation > 0.0 else 0.0,
        "pitch_angle": float(np.clip(pitch, 1.0, 60.0)),
        "arm_multiplicity": arms,
    }


PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="pattern", slot="pattern", checkpoint=4,
        about=(
            "The pattern's kinematics and the arms: everything §4b assigns to a seeded draw. "
            "Reads pattern_seed, so rerolling it invalidates checkpoints 5 and 6 and nothing "
            "earlier."
        ),
        compute=compute_pattern,
        reads_seeds=("pattern_seed",),
        reads_constants=(
            "FAST_BAR_RATIO", "FAST_BAR_SCATTER",
            "PITCH_SHEAR_INTERCEPT", "PITCH_SHEAR_SLOPE", "PITCH_SCATTER",
        ),
        requires=("bar_half_length", "shear_rate", "circular_velocity_resolved"),
        publishes=(COROTATION, PATTERN_SPEED, PITCH_ANGLE, ARM_MULTIPLICITY),
    )
)
