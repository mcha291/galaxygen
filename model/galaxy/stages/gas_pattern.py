"""The gas's own arm pattern (checkpoint 3, S51, D210 Phase 1).

The stellar pattern (``pattern``) is one cosine harmonic: an arm whose half-maximum is half
the arm-to-arm period, its amplitude Elmegreen et al. 2011's peak-to-trough contrast of the old
stars. The gas is not that. Measured the same way in the same galaxy, the gas ridge is half the
stellar arm's width (Egusa et al. 2017), and its arm-to-interarm contrast, measured as a ratio
of means inside the arm mask, is two to three where the stars' is a few tens of percent
(Querejeta et al. 2024). D210 rules a second pattern for the gas, read off the first:

- **The form** (ruling 2). g(R, φ) = 1 + w_arm(R) a(R) (v(θ) − 1) + w_bar(R) B cos 2(φ − φ_bar),
  θ = m (φ − ln R cot p), v(θ) = e^{κ cos θ}/I₀(κ) — a von Mises ridge, whose mean round the
  ring is 1 in closed form. The arm weight, bar weight, phase and bar angle are the stellar
  pattern's own, taken from ``ArmPattern._terms`` (not re-derived); the bar term is the stellar
  bar's, B its ``bar_contrast``.
- **No offset** (ruling 3): the ridge's crest is the stellar arm's crest. The density-wave law,
  Δφ = (Ω − Ω_p) t with the shock on the inner edge inside corotation, is the named alternative;
  the model publishes no spiral pattern speed to sign it with.
- **The width** (ruling 4) is a fixed fraction of the arm-to-arm period: κ = ln 2 / (1 − cos πW)
  is the von Mises's exact half-maximum relation, so v(±πW) = v(0)/2 and the full width at half
  maximum is W of the period.
- **The amplitude** (ruling 5) is derived from the measured ratio of means with the source's own
  mask: a mask of full width W_m perpendicular to the arm spans |θ| < θ_m = m (W_m/2)/(R sin p),
  clamped at π/2 (half the period); g is affine in v, so C = [1 + a(v̄_in − 1)]/[1 + a(v̄_out − 1)]
  inverts to a = (C − 1)/[(v̄_in − 1) − C (v̄_out − 1)]. a depends on R only through θ_m, so
  inside the clamp it is one number.
- **The contrast's mean** is derived as the stellar amplitude's is (D175): the non-grand-design
  class's ratio to the grand designs' by the two-fold pattern's amplification weight, its residual
  drawn log-normally on ``pattern_seed``.

**Quadratures, each a step count known in advance (A1).** The mask means v̄_in and v̄_out are
midpoint sums over a fixed grid of ``PHASE_CELLS`` cells in θ over one period, independent of
the model's φ grid, so a point evaluation needs no grid; at the clamp the mask's edges are cell
edges. The sector means are exact: v's Fourier series, e^{κ cos θ}/I₀(κ) = 1 + 2 Σ_n
[I_n(κ)/I₀(κ)] cos nθ, has coefficients computed once by a ``HARMONIC_SAMPLES``-point FFT, and
each harmonic's sector mean is a sine difference, as the stellar pattern's are.

**Why its own stage.** ``pattern`` publishes seeded fields and this stage draws one more residual
on the same seed; a separate stage keeps ``pattern``'s outputs (and every row that reads them)
exactly what they were, and gives the gas's response one declaration with one provenance (D55).
"""

from __future__ import annotations

import functools
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.pattern import ArmPattern, invert_azimuths, swing_weight

PHASE_CELLS = 360  # the mask's fixed midpoint quadrature over one period of θ (A1)
HARMONIC_SAMPLES = 1024  # the FFT that gives v's Fourier coefficients for the exact sector means
HARMONIC_FLOOR = 1e-15  # the series stops at the first coefficient under this (FFT rounding ~1e-16)

# The fixed θ grid: cell centres over one period, symmetric about the crest, so at the clamp
# (θ_m = π/2) the mask's edges fall on cell edges. Sorted by |θ| once, so v̄_in for any θ_m is a
# prefix sum over ± pairs of cells.
_THETA = -math.pi + (np.arange(PHASE_CELLS) + 0.5) * (2.0 * math.pi / PHASE_CELLS)
_ORDER = np.argsort(np.abs(_THETA), kind="stable")


def kappa_for_width(width: float) -> float:
    """The von Mises concentration whose full width at half maximum is ``width`` of the period.

    v(θ)/v(0) = e^{κ(cos θ − 1)} = 1/2 at θ = πW, so κ = ln 2 / (1 − cos πW): exact for a von
    Mises, no Gaussian limit taken. 4.977 at W = 0.17.
    """
    w = min(max(float(width), 1e-4), 1.0)
    return math.log(2.0) / (1.0 - math.cos(math.pi * w))


def von_mises(theta: np.ndarray, kappa: float) -> np.ndarray:
    """v(θ) = e^{κ cos θ}/I₀(κ): mean 1 over a period, crest e^κ/I₀(κ) at θ = 0."""
    return np.exp(kappa * np.cos(theta)) / float(np.i0(kappa))


@functools.lru_cache(maxsize=16)
def _harmonics(kappa: float) -> np.ndarray:
    """c_n = I_n(κ)/I₀(κ) for n = 1 … HARMONIC_SAMPLES/2 − 1: v = 1 + 2 Σ c_n cos nθ.

    By FFT of v on HARMONIC_SAMPLES points; the aliasing error is c_{N−n}, below 1e-300 at the
    defaults. c_n falls monotonically, so the series stops at the first coefficient under
    HARMONIC_FLOOR (the FFT's own rounding is ~1e-16): 23 terms at κ = 4.977, the dropped tail
    under 1e-15.
    """
    theta = np.arange(HARMONIC_SAMPLES) * (2.0 * math.pi / HARMONIC_SAMPLES)
    c = np.fft.rfft(von_mises(theta, kappa)).real / HARMONIC_SAMPLES
    c = c[1:HARMONIC_SAMPLES // 2]
    small = np.nonzero(np.abs(c) < HARMONIC_FLOOR)[0]
    return c[: int(small[0])] if small.size else c


@functools.lru_cache(maxsize=16)
def _mask_table(kappa: float) -> tuple[np.ndarray, float]:
    """Sums of v over the fixed θ cells inside |θ| < e_j for every cell edge e_j = j Δ (0 … π),
    the cells taken in ± pairs from the crest outward; and the sum over all of them."""
    v = von_mises(_THETA, kappa)[_ORDER]
    pairs = v[0::2] + v[1::2]  # _ORDER takes the cells by |θ|, each |θ| twice
    cum = np.concatenate([[0.0], np.cumsum(pairs)])
    return cum, float(cum[-1])


def mask_means(theta_m: np.ndarray, kappa: float) -> tuple[np.ndarray, np.ndarray]:
    """(v̄_in, v̄_out): v's mean over the fixed θ cells inside |θ| < θ_m, and over the rest.

    A midpoint sum on the fixed cells, the one pair the mask's edge cuts counted by the fraction
    of it inside (linear between cell edges), so v̄_in moves smoothly with θ_m and at the clamp —
    θ_m = π/2, a cell edge — is the plain midpoint sum. Against the integral, v̄_in is off by
    2e-7 of itself at the clamp, 7e-6 at θ_m = 1.07 (12 kpc at the defaults) and 7e-5 at 0.5.
    At least one cell's width is inside.
    """
    cum, total = _mask_table(kappa)
    step = 2.0 * math.pi / PHASE_CELLS
    edges = np.arange(cum.size) * step
    theta_m = np.clip(np.asarray(theta_m, dtype=float), 0.5 * step, 0.5 * math.pi)
    inside = np.interp(theta_m, edges, cum)
    cells = 2.0 * theta_m / step
    return inside / cells, (total - inside) / (PHASE_CELLS - cells)


def _scalar(name, label, unit, about):
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.SCALAR,
                     meaningful_zero=True, about=about, provenance="seeded")


GAS_ARM_CONTRAST = _scalar(
    "gas_arm_contrast", "Gas arm–interarm contrast (ratio of means)", "dimensionless",
    "The ratio the gas's arm pattern is set to: mean gas surface density inside an arm mask of the "
    "source's width over the mean outside it, on each ring — a ratio of means, not a peak-to-trough. "
    "Its mean runs from the non-grand-design spirals' molecular ratio to the grand designs' with the "
    "two-fold pattern's amplification weight, as the stellar amplitude's does; its residual is drawn "
    "log-normally on pattern_seed with the grand-design class's 16th–84th-percentile half-width. "
    "Those percentiles are over arm segments and radial bins, so the per-galaxy draw also carries "
    "the scatter within one galaxy [verified: Querejeta et al. 2024, A&A 687, A293, Table 1; "
    "docs/READING_GAS_PATTERN.md]. Where the drawn ratio would need the ridge's trough or crest "
    "below zero the amplitude is clipped and the ring's ratio falls short of this number.",
)

GAS_DENSITY_CONTRAST = FieldDecl(
    name="gas_density_contrast", label="Gas density contrast Σ_gas(R, φ)/Σ_gas(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=4.0), meaningful_zero=True, provenance="seeded",
    about=(
        "Σ_gas(R, φ)/Σ_gas(R): mean 1 round every ring, so every radial gas profile is unchanged. "
        "A von Mises ridge in the stellar arm's own phase, its full width at half maximum a fixed "
        "fraction of the arm-to-arm period, half the stellar arm's as in the one galaxy measured "
        "both ways, sitting on the stellar arm's crest with no offset. The density-wave offset "
        "law, Δφ = (Ω − Ω_p)·t with the shock inside the arm inside corotation, is the named "
        "alternative and is not adopted: the model publishes no spiral pattern speed to sign it "
        "with, and the evidence for co-rotating arms reads zero mean offset with scatter; no "
        "offset field is published for it. Inside the bar the term is the stellar bar's own. The "
        "ridge's amplitude is derived from the measured ratio of means (gas_arm_contrast) over "
        "the source's own arm mask, a fixed width perpendicular to the arm, at most half the "
        "period. The gas's response to the stellar pattern: it reads no gas column."
    ),
)


@dataclass(frozen=True, slots=True)
class GasPattern:
    """Everything the gas contrast needs, read from published fields in one place (rule A9).

    The interface is ``ArmPattern``'s (``flat``, ``contrast``, ``contrast_at``, ``sector_means``,
    ``azimuths``), so a stage that places by the stellar pattern can place by this one instead.
    """

    ratio: float          # C, the published gas_arm_contrast
    bar: float            # B, the stellar bar_contrast
    m: float
    pitch_deg: float
    bar_length: float
    width: float          # W, FWHM over the arm-to-arm period
    mask_width: float     # W_m, kpc, full width perpendicular to the arm

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], constants: Mapping[str, Any]) -> "GasPattern | None":
        names = ("gas_arm_contrast", "bar_contrast", "arm_multiplicity", "pitch_angle", "bar_half_length")
        consts = ("GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH")
        if any(n not in fields for n in names) or any(k not in constants for k in consts):
            return None
        return cls(float(fields["gas_arm_contrast"]), float(fields["bar_contrast"]),
                   float(fields["arm_multiplicity"]), float(fields["pitch_angle"]),
                   float(fields["bar_half_length"]),
                   float(constants["GAS_ARM_WIDTH"]), float(constants["GAS_ARM_MASK_WIDTH"]))

    @property
    def flat(self) -> bool:
        """No perturbation to apply: a pattern the grid could not resolve (NaN pitch or bar), or a
        ratio of 1 with no bar, which stays axisymmetric."""
        values = (self.ratio, self.bar, self.m, self.pitch_deg, self.bar_length, self.width, self.mask_width)
        if not all(math.isfinite(v) for v in values):
            return True
        return self.ratio == 1.0 and self.bar == 0.0

    @property
    def kappa(self) -> float:
        return kappa_for_width(self.width)

    @property
    def _stellar(self) -> ArmPattern:
        # Unit arm amplitude, so _terms returns the arm weight itself and the bar's B times its weight.
        return ArmPattern(1.0, self.bar, self.m, self.pitch_deg, self.bar_length)

    def mask_half_width(self, R: np.ndarray) -> np.ndarray:
        """θ_m = m (W_m/2)/(R sin p), clamped at π/2: the source's mask in the ridge's phase."""
        R = np.maximum(np.asarray(R, dtype=float), 1e-3)
        sin_p = math.sin(math.radians(min(max(self.pitch_deg, 1.0), 89.0)))
        return np.minimum(self.m * 0.5 * self.mask_width / (R * sin_p), 0.5 * math.pi)

    def amplitude(self, R: np.ndarray) -> np.ndarray:
        """a(R) = (C − 1)/[(v̄_in − 1) − C (v̄_out − 1)], clipped so the ridge is nowhere negative."""
        kappa = self.kappa
        v_in, v_out = mask_means(self.mask_half_width(R), kappa)
        C = self.ratio
        a = (C - 1.0) / ((v_in - 1.0) - C * (v_out - 1.0))
        v0, vpi = float(von_mises(np.array(0.0), kappa)), float(von_mises(np.array(math.pi), kappa))
        return np.clip(a, -1.0 / (v0 - 1.0), 1.0 / (1.0 - vpi))

    def _parts(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Per radius: the ridge's weight w_arm a, the bar's w_bar B, the arm phase; the bar angle."""
        arm_w, bar_w, phase, bar_angle = self._stellar._terms(R)
        return arm_w * self.amplitude(R), bar_w, phase, bar_angle

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ_gas(R, φ)/Σ_gas(R) on the (R, φ) grid. Mean 1 around every ring for integer m."""
        ridge_w, bar_w, phase, bar_angle = self._parts(R)
        phi = np.asarray(phi, dtype=float)[None, :]
        v = von_mises(self.m * (phi - phase[:, None]), self.kappa)
        return 1.0 + ridge_w[:, None] * (v - 1.0) + bar_w[:, None] * np.cos(2.0 * (phi - bar_angle))

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        shape = np.broadcast_shapes(R.shape, phi.shape)
        R_b, phi_b = np.broadcast_to(R, shape).ravel(), np.broadcast_to(phi, shape).ravel()
        ridge_w, bar_w, phase, bar_angle = self._parts(R_b)
        v = von_mises(self.m * (phi_b - phase), self.kappa)
        out = 1.0 + ridge_w * (v - 1.0) + bar_w * np.cos(2.0 * (phi_b - bar_angle))
        return out.reshape(shape)

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` at one radius — exactly, by v's
        Fourier series (each harmonic's sector mean is a sine difference); the error is the
        dropped coefficients', under 1e-15."""
        ridge_w, bar_w, phase, bar_angle = self._parts(np.array([R]))
        edges = np.asarray(edges, dtype=float)
        a, b = edges[:-1], edges[1:]

        def mean_cos(k: np.ndarray, shift: float) -> np.ndarray:  # k (H,) → (H, sectors)
            k = np.asarray(k, dtype=float)[:, None]
            return (np.sin(k * (b - shift)) - np.sin(k * (a - shift))) / (k * (b - a))

        c = _harmonics(self.kappa)
        n = np.arange(1, c.size + 1, dtype=float)
        ridge = 2.0 * (c[:, None] * mean_cos(n * self.m, float(phase[0]))).sum(axis=0) if c.size else 0.0
        bar = mean_cos(np.array([2.0]), bar_angle)[0]
        return 1.0 + ridge_w[0] * ridge + bar_w[0] * bar

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8)."""
        grid = np.linspace(lo, hi, steps + 1)
        return invert_azimuths(u, grid, self.contrast(radius, grid))


def compute_gas_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    c = ctx.constants
    # The mean ratio: the two classes joined by the two-fold pattern's amplification weight, exactly
    # as the bar stage weighs the stellar arm contrast (D175); the residual log-normal (D210 ruling 5).
    m_lo, m_hi = float(ctx.fields["swing_arm_min"]), float(ctx.fields["swing_arm_max"])
    x_high, x_dead, x_low, x_floor = (float(c[k]) for k in ("SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_LOW", "SWING_X_FLOOR"))
    coherence = swing_weight(2.0, m_lo, m_hi, x_high, x_dead, x_low, x_floor)
    other, grand = float(c["GAS_ARM_CONTRAST_OTHER"]), float(c["GAS_ARM_CONTRAST_GRAND_DESIGN"])
    mean = other + (grand - other) * coherence
    ratio = math.exp(math.log(mean) + ctx.rng("pattern_seed", "gas_contrast").normal(0.0, float(c["GAS_ARM_CONTRAST_LOG_SCATTER"])))

    shape = GasPattern.from_fields({**{k: ctx.fields[k] for k in ("bar_contrast", "arm_multiplicity", "pitch_angle", "bar_half_length")},
                                    "gas_arm_contrast": ratio}, c)
    flat = shape is None or shape.flat
    return {
        "gas_arm_contrast": ratio,
        "gas_density_contrast": np.ones((R.size, ctx.grid.phi.size)) if flat else shape.contrast(R, ctx.grid.phi),
    }


GAS_PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="gas_pattern", slot="gas_pattern", checkpoint=3,
        about=(
            "The gas's own arm pattern: a narrow ridge on the stellar arm's crest, its width a fixed "
            "fraction of the arm-to-arm period and its amplitude set by a measured ratio of means "
            "inside an arm mask, drawn on pattern_seed (D210). Reads the stellar pattern's numbers, "
            "not its amplitude, and no gas column: the gas's response, stated as a shape."
        ),
        compute=compute_gas_pattern,
        reads_seeds=("pattern_seed",),
        reads_constants=(
            "GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH",
            "GAS_ARM_CONTRAST_GRAND_DESIGN", "GAS_ARM_CONTRAST_OTHER", "GAS_ARM_CONTRAST_LOG_SCATTER",
            "SWING_X_LOW", "SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_FLOOR",
        ),
        requires=("bar_contrast", "arm_multiplicity", "pitch_angle", "bar_half_length", "swing_arm_min", "swing_arm_max"),
        publishes=(GAS_ARM_CONTRAST, GAS_DENSITY_CONTRAST),
    )
)
