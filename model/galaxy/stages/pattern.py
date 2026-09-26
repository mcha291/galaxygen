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
# The closed set an arm number is drawn from since S26 (D175): two to ARM_MULTIPLICITY_MAX. Until
# then a coin toss between 2 and 4. m = 1 is excluded (level0, ARM_MULTIPLICITY_MAX's about line).
ARM_MULTIPLICITIES: tuple[float, ...] = (2.0, 3.0, 4.0, 5.0, 6.0)
BAR_CONTRAST_CAP = 0.9  # a cosine bar above this empties its inter-bar sector (BAR_CONTRAST_LOG_SCATTER)


def swing_window(disc_dominance: float, shear: float, x_low: float, x_high: float) -> tuple[float, float, float]:
    """(X₂, m_lo, m_hi): Toomre's X for m = 2 in the Mestel form, and the arm numbers the disc amplifies.

    For a flat curve κ² = 2v²/R² and a disc whose own rotation is v_d² = 2πGΣR (Mestel), so
    X_m = κ²R/(2πGΣm) = 2/(m f_d) with f_d = v_d²/v² the disc's share of the rotation — the
    published ``disc_dominance``. Vigorous amplification for x_low < X/Γ < x_high therefore means
    X₂/(Γ x_high) ≤ m ≤ X₂/(Γ x_low), the review's 1/f_d ≲ m ≲ 2/f_d at Γ = 1 [verified:
    Sellwood & Masters 2022 §4.2.3.2]. The alternative is the local form with the exponential
    disc's own Σ(2.2 R_d), which reads X₂ = 2.7 at the defaults and prefers m = 3–4 there; it
    increases outward (D'Onghia 2015: two arms at 4.5 kpc, five or six at R₀), so it needs a
    radius chosen by hand, and the global form was chosen before either number was read (D175).
    """
    f_d = min(max(float(disc_dominance), 1e-6), 1.0)
    gamma = float(shear) if math.isfinite(shear) and shear > 0.0 else 1.0
    x2 = 2.0 / f_d
    return x2, x2 / (gamma * x_high), x2 / (gamma * x_low)


def swing_weight(m: float, m_lo: float, m_hi: float, x_high: float, x_dead: float, x_low: float, x_floor: float) -> float:
    """How strongly a disc amplifies an m-fold pattern, 0–1: 1 inside [m_lo, m_hi], falling
    log-linearly to 0 where X reaches x_dead (fewer arms than m_lo) or x_floor (more than m_hi)."""
    if m_lo <= m <= m_hi:
        return 1.0
    if m < m_lo:  # X above the vigorous range: dead at X = x_dead, i.e. at m_lo × x_high / x_dead
        m_dead = m_lo * x_high / x_dead
        return float(min(max(math.log(m / m_dead) / math.log(m_lo / m_dead), 0.0), 1.0)) if m > m_dead else 0.0
    m_dead = m_hi * x_low / x_floor  # X below the range: dead at X = x_floor
    return float(min(max(math.log(m_dead / m) / math.log(m_dead / m_hi), 0.0), 1.0)) if m < m_dead else 0.0


def contrast_amplitude(mag: float) -> float:
    """The cosine amplitude whose peak-to-trough ratio is an arm–interarm contrast of ``mag`` magnitudes."""
    c = 10.0 ** (0.4 * max(float(mag), 0.0))
    return (c - 1.0) / (c + 1.0)


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


SWING_X = _scalar(
    "swing_x", "Swing-amplification X for two arms", "dimensionless",
    "Toomre's X = κ²R/(2πGΣm) at m = 2 in the Mestel form, 2/disc_dominance (S26, D175): the "
    "first link of §4b's chain, disc dominance → the arms the disc can amplify. 3.3 at the "
    "defaults, against the vigorous range of 1–2 the level-0 window holds: a two-armed pattern "
    "is at the edge of what this disc amplifies, three arms are inside it.",
)

SWING_ARM_MIN = _scalar(
    "swing_arm_min", "Fewest arms the disc amplifies", "count",
    "swing_x over the shear rate times the window's upper edge: the m at which X/Γ leaves the vigorous range on the "
    "high side. Not an integer — the pattern stage draws the integer around it. 1.7 at the defaults; "
    "3.9 for a disc that holds 30% of its rotation at a shear of 0.87 (the flocculent regime).",
)

SWING_ARM_MAX = _scalar(
    "swing_arm_max", "Most arms the disc amplifies", "count",
    "swing_x over the shear rate times the window's lower edge: the m at which X/Γ leaves the range on the low side. 3.4 "
    "at the defaults, the review's 2/f_d [verified: Sellwood & Masters 2022 §4.2.3.2].",
)

ARM_CONTRAST_MEAN = _scalar(
    "arm_contrast_mean", "Mean arm amplitude the disc supports", "dimensionless",
    "The cosine amplitude of the arm–interarm contrast the disc's own dynamics predict before the "
    "residual is drawn: the flocculent class's arm–interarm contrast plus the two-fold pattern's "
    "amplification weight times the way to the grand-design class's, then 10^(0.4 mag) turned into (C−1)/(C+1). 0.48 "
    "at the defaults (the grand-design value, since m = 2 sits inside the vigorous range), falling "
    "to 0.33 for a halo-dominated disc. Derived, so it lives in the derived half (D55).",
)


def compute_bar(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    c = ctx.constants
    R_d = float(ctx.fields["disc_scale_length_spin"])
    at = SHEAR_RADIUS_IN_SCALE_LENGTHS * R_d
    total = np.asarray(ctx.fields["circular_velocity"])
    halo = np.asarray(ctx.fields["halo_circular_velocity"])
    v_total = float(np.interp(at, R, total))
    v_halo = float(np.interp(at, R, halo))
    dominance = 1.0 - (v_halo / v_total) ** 2 if v_total > 0.0 else 0.0
    shear = shear_rate(R, total, at)
    x2, m_lo, m_hi = swing_window(dominance, shear, float(c["SWING_X_LOW"]), float(c["SWING_X_HIGH"]))
    coherence = swing_weight(2.0, m_lo, m_hi, float(c["SWING_X_HIGH"]), float(c["SWING_X_DEAD"]), float(c["SWING_X_LOW"]), float(c["SWING_X_FLOOR"]))
    floc, grand = float(c["ARM_INTERARM_FLOCCULENT"]), float(c["ARM_INTERARM_GRAND_DESIGN"])
    return {
        "bar_half_length": float(c["BAR_LENGTH_RATIO"]) * R_d,
        "disc_dominance": dominance,
        "shear_rate": shear,
        "swing_x": x2,
        "swing_arm_min": m_lo,
        "swing_arm_max": m_hi,
        "arm_contrast_mean": contrast_amplitude(floc + (grand - floc) * coherence),
    }


BAR = IMPLEMENTATIONS.register(
    Stage(
        id="bar", slot="bar", checkpoint=3,
        about=(
            "The bar's size, the disc's shear, and what the disc can amplify — everything about the "
            "pattern that has no draw in it. Split from the seeded half so that row 15 stays "
            "reproducible (D55). Since S26 it publishes the swing-amplification window and the mean "
            "arm amplitude, derived from disc_dominance and shear_rate (D175)."
        ),
        compute=compute_bar,
        reads_constants=(
            "BAR_LENGTH_RATIO", "SWING_X_LOW", "SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_FLOOR",
            "ARM_INTERARM_GRAND_DESIGN", "ARM_INTERARM_FLOCCULENT",
        ),
        requires=("disc_scale_length_spin", "circular_velocity", "halo_circular_velocity"),
        publishes=(BAR_HALF_LENGTH, DISC_DOMINANCE, SHEAR, SWING_X, SWING_ARM_MIN, SWING_ARM_MAX, ARM_CONTRAST_MEAN),
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
    "Swing amplification sets a preferred m and real galaxies at similar X still differ, so §4b "
    "assigns this a seeded draw rather than an input. Since S26 the draw is weighted by what the "
    "disc amplifies — odds 1 for m between swing_arm_min and swing_arm_max, falling to 0 where X "
    "reaches the window's dead edge or its floor — over 2 to 6 (D175). At the "
    "defaults two or three arms carry 29% each, four 23%, five 13%, six 6%; a disc holding 30% of "
    "its rotation draws four to six, the flocculent regime. Until S26 a coin toss between 2 and 4.",
    provenance="seeded",
)


ARM_CONTRAST = _scalar(
    "arm_contrast", "Spiral arm amplitude A", "dimensionless",
    "Fractional density contrast of the arms, Σ(R, φ) = Σ(R)[1 + A cos m(φ − ln R / tan p)]. "
    "Since S26 the mean is derived (arm_contrast_mean, from the disc's own amplification) and the "
    "residual drawn on pattern_seed as the grand-design class's scatter in arm–interarm contrast "
    "(§4b verdict C, D175); until then an experimental input (D171, debt #23).",
    provenance="seeded",
)

BAR_CONTRAST = _scalar(
    "bar_contrast", "Bar amplitude", "dimensionless",
    "Fractional density contrast of the bar, an m = 2 term tapered off beyond the bar's "
    "half-length. Since S26 drawn log-normally on pattern_seed about the S4G barred sample's median "
    "with its 16th–84th-percentile width, capped at 0.9 (D175); until then an experimental input (D171).",
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

    # The arm number: the closed set, weighted by what this disc amplifies (D175). The odds are
    # a derived function of the window; the draw is the residual real galaxies show at one X.
    c = ctx.constants
    m_lo, m_hi = float(ctx.fields["swing_arm_min"]), float(ctx.fields["swing_arm_max"])
    x_high, x_dead, x_low, x_floor = (float(c[k]) for k in ("SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_LOW", "SWING_X_FLOOR"))
    choices = tuple(m for m in ARM_MULTIPLICITIES if m <= float(c["ARM_MULTIPLICITY_MAX"]))
    weights = np.array([swing_weight(m, m_lo, m_hi, x_high, x_dead, x_low, x_floor) for m in choices])
    if not weights.sum() > 0.0:  # nothing inside or near the window: the m nearest its centre
        weights = np.array([1.0 if i == int(np.argmin(np.abs(np.log(np.array(choices)) - 0.5 * (math.log(max(m_lo, 1e-9)) + math.log(max(m_hi, 1e-9)))))) else 0.0 for i in range(len(choices))])
    u = float(ctx.rng("pattern_seed", "arms").random())
    arms = float(choices[min(int(np.searchsorted(np.cumsum(weights) / weights.sum(), u, side="right")), len(choices) - 1)])
    pitch_angle = float(np.clip(pitch, 1.0, 60.0))
    # The amplitudes: derived means, seeded residuals (§4b verdict C). The arms' residual is drawn
    # in magnitudes of arm–interarm contrast about the derived mean; the bar's log-normally.
    floc, grand = float(c["ARM_INTERARM_FLOCCULENT"]), float(c["ARM_INTERARM_GRAND_DESIGN"])
    coherence = swing_weight(2.0, m_lo, m_hi, x_high, x_dead, x_low, x_floor)
    mag = floc + (grand - floc) * coherence + ctx.rng("pattern_seed", "arm_contrast").normal(0.0, float(c["ARM_INTERARM_SCATTER"]))
    arm_contrast = contrast_amplitude(mag)
    bar_contrast = min(
        math.exp(math.log(float(c["BAR_CONTRAST_MEDIAN"])) + ctx.rng("pattern_seed", "bar_contrast").normal(0.0, float(c["BAR_CONTRAST_LOG_SCATTER"]))),
        BAR_CONTRAST_CAP,
    )
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
        reads_constants=(
            "FAST_BAR_RATIO", "FAST_BAR_SCATTER",
            "PITCH_SHEAR_INTERCEPT", "PITCH_SHEAR_SLOPE", "PITCH_SCATTER",
            "SWING_X_LOW", "SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_FLOOR", "ARM_MULTIPLICITY_MAX",
            "ARM_INTERARM_GRAND_DESIGN", "ARM_INTERARM_FLOCCULENT", "ARM_INTERARM_SCATTER",
            "BAR_CONTRAST_MEDIAN", "BAR_CONTRAST_LOG_SCATTER",
        ),
        requires=("bar_half_length", "shear_rate", "circular_velocity", "swing_arm_min", "swing_arm_max"),
        publishes=(COROTATION, PATTERN_SPEED, PITCH_ANGLE, ARM_MULTIPLICITY, ARM_CONTRAST, BAR_CONTRAST, DENSITY_CONTRAST),
    )
)
