"""Pattern: the bar and the spiral arms (checkpoint 3, ahead of star formation since S25).

Both stages read the checkpoint-1 curve (``circular_velocity``, the halo plus one
exponential) and the λ_d scale length, so the pattern is a consequence of the halo and
disc alone and the star-formation stages can read it (BUILD_II Phase 1, D174). Until
S25 they read ``sfh``'s resolved curve and fitted thin-disc scale length, which put
the pattern behind star formation and made azimuthal star formation impossible.

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
rerolling the pattern's stage invalidates what follows it and nothing earlier
(GALAXY_PLAN.md §3; since S25 that is checkpoints 4–6, D174).
The registry and the plan agree on ``pattern_seed``; §5 is the outlier
(DECISIONS.md D56).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
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
    "derived stage. Scaled from the disc's λ_d scale length (checkpoint 1) since S25, so that the "
    "pattern can precede star formation; until then from the thin disc's fitted stellar scale "
    "length, a star-formation result 6% shorter (D174, debt #80). The disc-dominance link "
    "GALAXY_INPUTS.md §4b describes is published beside it but not modelled (debt #21).",
)

DISC_DOMINANCE = _scalar(
    "disc_dominance", "Disc share of v_c² at 2.2 R_d", "dimensionless",
    "How much of the rotation the baryons provide where the disc's own curve peaks. §4b makes "
    "this the first link in the chain to the pattern speed; it is measured here and unused, so "
    "that the missing link is visible rather than silently absent. Read off the checkpoint-1 "
    "curve since S25, which holds every baryon in one exponential (D174).",
)

SHEAR = _scalar(
    "shear_rate", "Shear rate Γ", "dimensionless",
    "1 − dln v/dln R at 2.2 R_d. Zero is solid-body rotation and 1 is a flat curve, so a value "
    "near 1 means the disc is shearing as a flat-curve galaxy does. Off the checkpoint-1 curve "
    "since S25 (D174).",
)


def compute_bar(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    R_d = float(ctx.fields["disc_scale_length_spin"])
    at = SHEAR_RADIUS_IN_SCALE_LENGTHS * R_d
    total = np.asarray(ctx.fields["circular_velocity"])
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
        id="bar", slot="bar", checkpoint=3,
        about=(
            "The bar's size and the disc's shear — everything about the pattern that has no draw "
            "in it. Split from the seeded half so that row 15 stays reproducible (D55)."
        ),
        compute=compute_bar,
        reads_constants=("BAR_LENGTH_RATIO",),
        requires=("disc_scale_length_spin", "circular_velocity", "halo_circular_velocity"),
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


ARM_CONTRAST = _scalar(
    "arm_contrast", "Spiral arm amplitude A", "dimensionless",
    "Fractional density contrast of the arms, Σ(R, φ) = Σ(R)[1 + A cos m(φ − ln R / tan p)]. "
    "Experimental: taken from the arm_amplitude input while its value is explored (debt #23).",
    provenance="seeded",
)

BAR_CONTRAST = _scalar(
    "bar_contrast", "Bar amplitude", "dimensionless",
    "Fractional density contrast of the bar, an m = 2 term tapered off beyond the bar's "
    "half-length. Experimental: taken from the bar_amplitude input (debt #23).",
    provenance="seeded",
)

DENSITY_CONTRAST = FieldDecl(
    name="pattern_density_contrast", label="Bar and arm density contrast Σ(R, φ)/Σ(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=2.0), meaningful_zero=True, provenance="seeded",
    about=(
        "The non-axisymmetric factor the star catalogue samples azimuth from: 1 on average around "
        "every ring, so the radial profile and every radial row are unchanged. A logarithmic spiral "
        "of the drawn pitch angle and multiplicity outside the bar, a straight m = 2 bar inside it."
    ),
)


@dataclass(frozen=True, slots=True)
class ArmPattern:
    """Everything the density contrast needs, read from published fields in one place (rule A9)."""

    arm: float
    bar: float
    m: float
    pitch_deg: float
    bar_length: float

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any]) -> "ArmPattern | None":
        names = ("arm_contrast", "bar_contrast", "arm_multiplicity", "pitch_angle", "bar_half_length")
        if any(n not in fields for n in names):
            return None
        return cls(float(fields["arm_contrast"]), float(fields["bar_contrast"]), float(fields["arm_multiplicity"]),
                   float(fields["pitch_angle"]), float(fields["bar_half_length"]))

    @property
    def flat(self) -> bool:
        """No perturbation to apply: zero amplitudes, or a pattern the grid could not resolve
        (a mesh too coarse for the shear gives a NaN pitch and bar), which stays axisymmetric."""
        if not all(math.isfinite(v) for v in (self.arm, self.bar, self.m, self.pitch_deg, self.bar_length)):
            return True
        return self.arm == 0.0 and self.bar == 0.0

    def _terms(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Per radius: arm weight, bar weight, arm phase; and the bar's position angle."""
        R = np.maximum(np.asarray(R, dtype=float), 1e-3)
        # The bar gives way to the arms over its own half-length: a smooth taper, so the
        # density has no seam at the bar's end.
        bar_w = np.exp(-((R / max(self.bar_length, 1e-3)) ** 4))
        cot = 1.0 / math.tan(math.radians(min(max(self.pitch_deg, 1.0), 89.0)))
        phase = np.log(R) * cot
        # The bar lies along the arms' phase at its end, so each arm starts from a tip.
        bar_angle = float(math.log(max(self.bar_length, 1e-3)) * cot)
        return self.arm * (1.0 - bar_w), self.bar * bar_w, phase, bar_angle

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ(R, φ)/Σ(R) on the (R, φ) grid. Mean 1 around every ring for integer m."""
        arm_w, bar_w, phase, bar_angle = self._terms(R)
        phi = np.asarray(phi, dtype=float)[None, :]
        arms = arm_w[:, None] * np.cos(self.m * (phi - phase[:, None]))
        bar = bar_w[:, None] * np.cos(2.0 * (phi - bar_angle))
        return 1.0 + arms + bar

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` at one radius, analytically."""
        arm_w, bar_w, phase, bar_angle = self._terms(np.array([R]))
        a, b = edges[:-1], edges[1:]

        def mean_cos(m: float, shift: float) -> np.ndarray:
            return (np.sin(m * (b - shift)) - np.sin(m * (a - shift))) / (m * (b - a))

        return 1.0 + arm_w[0] * mean_cos(self.m, float(phase[0])) + bar_w[0] * mean_cos(2.0, bar_angle)

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8)."""
        grid = np.linspace(lo, hi, steps + 1)
        f = np.maximum(self.contrast(radius, grid), 0.0)  # (stars, steps + 1)
        seg = 0.5 * (f[:, 1:] + f[:, :-1])
        cdf = np.concatenate([np.zeros((len(radius), 1)), np.cumsum(seg, axis=1)], axis=1)
        total = np.where(cdf[:, -1] > 0.0, cdf[:, -1], 1.0)
        target = np.asarray(u, dtype=float) * total
        k = np.clip((cdf < target[:, None]).sum(axis=1) - 1, 0, steps - 1)
        rows = np.arange(len(radius))
        c0, c1 = cdf[rows, k], cdf[rows, k + 1]
        frac = np.where(c1 > c0, (target - c0) / np.where(c1 > c0, c1 - c0, 1.0), 0.0)
        return grid[k] + np.clip(frac, 0.0, 1.0) * (grid[1] - grid[0])


def compute_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    a_bar = float(ctx.fields["bar_half_length"])
    total = np.asarray(ctx.fields["circular_velocity"])

    ratio = ctx.rng("pattern_seed", "fast_bar").normal(
        float(ctx.constants["FAST_BAR_RATIO"]), float(ctx.constants["FAST_BAR_SCATTER"])
    )
    corotation = max(float(ratio), 0.1) * a_bar
    v_cr = float(np.interp(corotation, R, total))

    gamma = float(ctx.fields["shear_rate"])
    pitch_mean = float(ctx.constants["PITCH_SHEAR_INTERCEPT"]) + float(ctx.constants["PITCH_SHEAR_SLOPE"]) * (gamma - 1.0)
    pitch = ctx.rng("pattern_seed", "pitch").normal(pitch_mean, float(ctx.constants["PITCH_SCATTER"]))

    arms = ARM_MULTIPLICITIES[int(ctx.rng("pattern_seed", "arms").integers(len(ARM_MULTIPLICITIES)))]
    pitch_angle = float(np.clip(pitch, 1.0, 60.0))
    arm_contrast = float(ctx.inputs["arm_amplitude"])
    bar_contrast = float(ctx.inputs["bar_amplitude"])
    shape = ArmPattern(arm_contrast, bar_contrast, arms, pitch_angle, a_bar)

    return {
        "bar_corotation_radius": corotation,
        "bar_pattern_speed": v_cr / corotation if corotation > 0.0 else 0.0,
        "pitch_angle": pitch_angle,
        "arm_multiplicity": arms,
        "arm_contrast": arm_contrast,
        "bar_contrast": bar_contrast,
        "pattern_density_contrast": np.ones((R.size, ctx.grid.phi.size)) if shape.flat else shape.contrast(R, ctx.grid.phi),
    }


PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="pattern", slot="pattern", checkpoint=3,
        about=(
            "The pattern's kinematics and the arms: everything §4b assigns to a seeded draw. "
            "Reads pattern_seed, so rerolling it invalidates checkpoints 4, 5 and 6 and nothing "
            "earlier — star formation follows the pattern since S25 (D174)."
        ),
        compute=compute_pattern,
        reads_seeds=("pattern_seed",),
        reads_inputs=("arm_amplitude", "bar_amplitude"),
        reads_constants=(
            "FAST_BAR_RATIO", "FAST_BAR_SCATTER",
            "PITCH_SHEAR_INTERCEPT", "PITCH_SHEAR_SLOPE", "PITCH_SCATTER",
        ),
        requires=("bar_half_length", "shear_rate", "circular_velocity"),
        publishes=(COROTATION, PATTERN_SPEED, PITCH_ANGLE, ARM_MULTIPLICITY, ARM_CONTRAST, BAR_CONTRAST, DENSITY_CONTRAST),
    )
)
