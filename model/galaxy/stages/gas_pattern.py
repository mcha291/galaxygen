"""The gas's own arm pattern (checkpoint 3; S51, D210 Phase 1; since S56 a response to any stellar pattern, D215).

The stellar pattern (``pattern``) is a sum of cosine modes: an arm whose half-maximum is half
the arm-to-arm period, its amplitude Elmegreen et al. 2011's peak-to-trough contrast of the old
stars. The gas is not that. Measured the same way in the same galaxy, the gas ridge is half the
stellar arm's width (Egusa et al. 2017), and its arm-to-interarm contrast, measured as a ratio
of means inside the arm mask, is two to three where the stars' is a few tens of percent
(Querejeta et al. 2024). D210 rules a second pattern for the gas, read off the first; D215
restates it so that it follows whatever the stellar pattern is.

- **The form** (D210 ruling 2). g(R, φ) = 1 + w_arm(R) a(R) (v(R, φ) − 1) + w_bar(R) B cos 2(φ − φ_bar).
  The arm weight w_arm = 1 − the bar's taper, the bar weight, the winding phase and the bar's angle
  are the stellar pattern's own (``pattern.bar_terms``, not re-derived); the bar term is the
  stellar bar's, B its ``bar_contrast``.
- **The ridge** (S56, D215). ψ(R, φ) = (c_arms − 1)/A: the stellar arm modes scaled to unit
  amplitude, A the published ``arm_contrast`` -

      ψ = Σ_m u_m(R) cos(m χ − θ_m),   u_m = A_m(R) / (A w_arm(R)),   χ = φ − ln R · cot p,

  with A_m the published mode amplitudes and θ_m the layer's phases. v = e^{κψ} over its mean
  round the ring. **With one fully amplified mode at phase 0, ψ = cos m χ and v is S51's von
  Mises e^{κ cos θ}/I₀(κ)**: the regression P1's gate holds to 1e-9. The ridge fades with ψ: where
  the disc amplifies little, u is small and v flattens toward 1; where a ring carries no mode,
  ψ = 0, the ridge is 1 and no mask is formed.

  *What "the stellar pattern scaled to unit amplitude" is read as.* The plan writes ψ = (c − 1)/A.
  Outside the bar's reach that is this ψ exactly. Inside it, c carries the bar's taper on the arms
  and the bar's own m = 2 term, and S51's form keeps both **outside** the exponential - the taper
  multiplies a (v − 1) and the bar's term is added - so ψ is the arm modes before the taper: the
  only reading under which one mode is S51's field. Putting the tapered arms and the bar inside the
  exponential differs from S51's field by tenths of the mean inside the bar.
- **No offset** (D210 ruling 3): the ridge's crest is the stellar pattern's crest. The
  density-wave law, Δφ = (Ω − Ω_p) t with the shock on the inner edge inside corotation, is the
  named alternative; the model publishes no spiral pattern speed to sign it with.
- **The width** (D210 ruling 4) is a fixed fraction of one mode's arm-to-arm period:
  κ = ln 2 / (1 − cos πW) is the von Mises's exact half-maximum relation, so for one mode
  v(±πW) = v(0)/2 and the full width at half maximum is W of the period. With several modes
  the same κ is applied to their sum.
- **The amplitude** (D210 ruling 5) is derived from the measured ratio of means with the source's
  own mask: g is affine in v, so C = [1 + a(v̄_in − 1)]/[1 + a(v̄_out − 1)] inverts to
  a = (C − 1)/[(v̄_in − 1) − C (v̄_out − 1)], clipped so the ridge is nowhere negative.
  **The mask** (S56, D215) is the cells of the ring where ψ exceeds the level that encloses the
  same share of the ring the source's mask did: a mask of full width W_m perpendicular to an arm
  covers the share m W_m / (2π R sin p) of a ring with m arms, capped at a half, and with several
  modes m is the ring's power-weighted arm number m_eff(R) = Σ_m m A_m² / Σ_m A_m² (the lead's
  reading, D215: it is m for one mode and does not know the phases). The rule sets the ratio of
  means on every ring that carries a pattern, however faint: a(R) grows as the ridge flattens.
- **The contrast C** is ``gas_arm_contrast``, published by the derived ``bar`` stage: the
  non-grand-design class's ratio to the grand designs' by the two-fold pattern's amplification
  weight, as the stellar amplitude's mean is (D175). **No residual is drawn** (D210 as amended,
  debt #131): the source's spread is over arm segments and radial bins, not galaxies.

**Quadratures, each a step count known in advance (A1).** The ring's mean of e^{κψ} and the mask
means are midpoint sums over ``PHASE_CELLS`` cells of χ across **one period of the ring's
pattern** - 2π over the greatest common divisor of the arm numbers the ring carries - centred on
χ = 0, independent of the model's φ grid, so a point evaluation needs no grid. The mask takes the
cells in falling order of ψ, the one the level cuts counted by the fraction of it inside. For one
mode at phase 0 the period is the arm-to-arm one and these are S51's cells and S51's sums (its
mask took them in ± pairs from the crest outward, which is the falling order of cos θ). The sector
means are exact to the series' dropped tail: the ridge's Fourier coefficients at the radius come
from a ``HARMONIC_SAMPLES``-point FFT over the same period, and each harmonic's sector mean is a
sine or cosine difference, as the stellar pattern's are.

**Why its own stage, and why seeded.** It reads no seed of its own and draws nothing; it reads the
pattern's amplitudes, pitch and bar, which carry seeded draws, and the layer's phases, so
``graph`` labels its one field seeded through those requirements (D55: a stage that reads a
seeded or a synthetic field publishes seeded fields).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.pattern import (
    AMPLITUDE_FIELDS,
    ARM_MODES,
    PATTERN_READS,
    PHASE_FIELDS,
    bar_terms,
    invert_azimuths,
)

PHASE_CELLS = 360  # the fixed midpoint quadrature over one period of the ring's pattern (A1)
HARMONIC_SAMPLES = 1024  # the FFT that gives the ridge's Fourier coefficients for the exact sector means
HARMONIC_FLOOR = 1e-15  # harmonics under this (of the ring's mean) are dropped (FFT rounding ~1e-16)
RING_BLOCK = 2048  # radii per block of the ring quadrature: bounds the working arrays, changes no number

RING_MEAN_TOLERANCE = 1e-12  # a sampled ring mean further from 1 than this is renormalised (a coarse phi grid)

# What the gas's pattern is built from, and so what every stage that places by it requires (S56, D215): the
# ratio of means, the arm amplitude the modes are scaled by, and the stellar pattern's own reads - the modes
# and their phases, never ``arm_multiplicity``.
GAS_PATTERN_READS: tuple[str, ...] = ("gas_arm_contrast", "arm_contrast", *PATTERN_READS)
GAS_PATTERN_CONSTANTS: tuple[str, ...] = ("GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH")

_CELLS = -math.pi + (np.arange(PHASE_CELLS) + 0.5) * (2.0 * math.pi / PHASE_CELLS)  # cell centres over (−π, π)
_BITS = 1 << np.arange(len(ARM_MODES))


def kappa_for_width(width: float) -> float:
    """The concentration whose one-mode ridge has a full width at half maximum of ``width`` of the period.

    v(θ)/v(0) = e^{κ(cos θ − 1)} = 1/2 at θ = πW, so κ = ln 2 / (1 − cos πW): exact for a von
    Mises, no Gaussian limit taken. 4.977 at W = 0.17.
    """
    w = min(max(float(width), 1e-4), 1.0)
    return math.log(2.0) / (1.0 - math.cos(math.pi * w))


def pattern_period(present: int) -> int:
    """The greatest common divisor of the arm numbers a ring carries (``present``: bit k for mode k of
    ARM_MODES): the ring's pattern repeats that many times round it. 1 for a ring that carries none."""
    out = 0
    for k, m in enumerate(ARM_MODES):
        if present >> k & 1:
            out = math.gcd(out, m)
    return out or 1


GAS_DENSITY_CONTRAST = FieldDecl(
    name="gas_density_contrast", label="Gas density contrast Σ_gas(R, φ)/Σ_gas(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=4.0), meaningful_zero=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the ridge's law applied to where the arms are - and 1 everywhere
    # with the randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "Σ_gas(R, φ)/Σ_gas(R): mean 1 round every ring, so every radial gas profile is unchanged. "
        "A narrow ridge on the crests of the stellar pattern, whatever that pattern is: the exponential "
        "of the stellar arm modes' sum at unit amplitude, over its mean round the ring - for one mode a "
        "von Mises ridge in that arm's phase, its full width at half maximum a fixed "
        "fraction of the arm-to-arm period, half the stellar arm's as in the one galaxy measured "
        "both ways; with several modes a ridge that is sharpest where their crests meet. It sits on the "
        "stellar crest with no offset, and it flattens where the stellar modes are weak: where a ring "
        "carries no mode there is no ridge. The density-wave offset "
        "law, Δφ = (Ω − Ω_p)·t with the shock inside the arm inside corotation, is the named "
        "alternative and is not adopted: the model publishes no spiral pattern speed to sign it "
        "with, and the evidence for co-rotating arms reads zero mean offset with scatter; no "
        "offset field is published for it. Inside the bar the term is the stellar bar's own. The "
        "ridge's amplitude is derived from the measured ratio of means (gas_arm_contrast) over "
        "the cells of the ring where the stellar modes' sum is highest, as large a share of the ring "
        "as the source's own arm mask covers - a fixed width perpendicular to an arm, for the ring's "
        "power-weighted number of arms, at most half the ring. The gas's response to the stellar "
        "pattern: it reads no gas column. A composed "
        "field: with the randomness layer off it is 1 everywhere - the ratio of means, the width "
        "and the mask are unchanged, and nothing says where the ridge is."
    ),
)


@dataclass(frozen=True, slots=True, eq=False)
class GasPattern:
    """Everything the gas contrast needs, read from published fields in one place (rule A9).

    The interface is ``ArmPattern``'s (``flat``, ``contrast``, ``contrast_at``, ``sector_means``,
    ``azimuths``), so a stage that places by the stellar pattern can place by this one instead.

    **Evaluable at a point**: the unit amplitudes u_m at an arbitrary radius are their values at the grid
    radii - the published amplitudes over the arm amplitude and the bar's taper there - interpolated
    linearly in R (held at the end values beyond the grid); the ring's mean, its mask and its amplitude
    a(R) are then computed at that radius by the fixed quadrature, not read off a table.
    """

    R: np.ndarray          # the grid radii the stellar amplitudes are published at
    unit: np.ndarray       # (modes, R): u_m = A_m / (A (1 − bar taper)), the arm modes at unit amplitude
    phases: tuple[float, ...]
    ratio: float           # C, the published gas_arm_contrast
    bar: float             # B, the stellar bar_contrast
    pitch_deg: float
    bar_length: float
    width: float           # W, FWHM of one mode's ridge over its arm-to-arm period
    mask_width: float      # W_m, kpc, full width perpendicular to an arm
    flat: bool = field(init=False)
    _tables: dict = field(init=False, repr=False, default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "R", np.asarray(self.R, dtype=float))
        object.__setattr__(self, "unit", np.asarray(self.unit, dtype=float))
        object.__setattr__(self, "phases", tuple(float(p) for p in self.phases))
        if self.unit.shape != (len(ARM_MODES), self.R.size) or len(self.phases) != len(ARM_MODES):
            raise ValueError(
                f"a gas pattern holds {len(ARM_MODES)} modes on its {self.R.size} radii; got unit amplitudes "
                f"{self.unit.shape} and {len(self.phases)} phases"
            )
        # No perturbation to apply: a pattern the grid could not resolve or the layer did not realise (a NaN
        # among its numbers), or no ridge (a ratio of 1, or no mode anywhere) and no bar.
        scalars = (self.ratio, self.bar, self.pitch_deg, self.bar_length, self.width, self.mask_width, *self.phases)
        finite = all(math.isfinite(v) for v in scalars) and bool(np.all(np.isfinite(self.unit)))
        no_ridge = self.ratio == 1.0 or not self.unit.any()
        object.__setattr__(self, "flat", not finite or (no_ridge and self.bar == 0.0))

    @staticmethod
    def unit_amplitudes(R: np.ndarray, amplitudes: np.ndarray, arm: float, pitch_deg: float, bar_length: float) -> np.ndarray:
        """u_m(R) = A_m(R) / (A (1 − bar taper)) at the grid radii: the published amplitudes with the arm
        amplitude and the bar's taper taken back out, so ψ = Σ u_m cos(…) is the arm modes at unit amplitude.
        Zero where the denominator is (no arm amplitude at all, or a radius where the taper is whole)."""
        taper, _, _ = bar_terms(R, pitch_deg, bar_length)
        scale = arm * (1.0 - taper)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(scale > 0.0, np.asarray(amplitudes, dtype=float) / np.where(scale > 0.0, scale, 1.0), 0.0)

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], R: np.ndarray, constants: Mapping[str, Any]) -> "GasPattern | None":
        """The gas pattern of a run's published fields on the run's grid radii ``R``, or None where the fields
        hold no pattern. It reads the modes; ``arm_multiplicity`` is not among what it reads (D215)."""
        if any(n not in fields for n in GAS_PATTERN_READS) or any(k not in constants for k in GAS_PATTERN_CONSTANTS):
            return None
        pitch, bar_length = float(fields["pitch_angle"]), float(fields["bar_half_length"])
        amplitudes = np.stack([np.asarray(fields[n], dtype=float) for n in AMPLITUDE_FIELDS])
        return cls(
            R, cls.unit_amplitudes(R, amplitudes, float(fields["arm_contrast"]), pitch, bar_length),
            tuple(float(fields[n]) for n in PHASE_FIELDS),
            float(fields["gas_arm_contrast"]), float(fields["bar_contrast"]), pitch, bar_length,
            float(constants["GAS_ARM_WIDTH"]), float(constants["GAS_ARM_MASK_WIDTH"]),
        )

    @property
    def kappa(self) -> float:
        return kappa_for_width(self.width)

    def unit_at(self, R: np.ndarray) -> np.ndarray:
        """(modes, …R's shape): each mode's unit amplitude at ``R``, linear in R between the grid radii."""
        R = np.asarray(R, dtype=float)
        return np.stack([np.interp(R, self.R, row) for row in self.unit])

    def effective_arm_number(self, R: np.ndarray) -> np.ndarray:
        """m_eff(R) = Σ_m m u_m² / Σ_m u_m² (the taper and the arm amplitude cancel): the ring's
        power-weighted arm number; NaN on a ring with no mode."""
        power = self.unit_at(R) ** 2
        total = power.sum(axis=0)
        m = np.asarray(ARM_MODES, dtype=float).reshape((-1,) + (1,) * (power.ndim - 1))
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(total > 0.0, (m * power).sum(axis=0) / np.where(total > 0.0, total, 1.0), np.nan)

    def mask_share(self, R: np.ndarray) -> np.ndarray:
        """The share of the ring the source's arm mask covers: m_eff W_m / (2π R sin p), at most a half and
        at least one quadrature cell; NaN on a ring with no mode (no mask is formed)."""
        R = np.maximum(np.asarray(R, dtype=float), 1e-3)
        sin_p = math.sin(math.radians(min(max(self.pitch_deg, 1.0), 89.0)))
        # S51's half-width in the ridge's phase, θ_m = m (W_m/2)/(R sin p) clamped at π/2, over π.
        theta_m = np.minimum(self.effective_arm_number(R) * 0.5 * self.mask_width / (R * sin_p), 0.5 * math.pi)
        return np.clip(theta_m, 0.5 * (2.0 * math.pi / PHASE_CELLS), 0.5 * math.pi) / math.pi

    def _table(self, period: int) -> np.ndarray:
        """cos(m χ_k − θ_m) for every mode on the fixed cells of one period of a pattern that repeats
        ``period`` times round the ring: (modes, PHASE_CELLS)."""
        table = self._tables.get(period)
        if table is None:
            chi = _CELLS / period
            table = np.stack([np.cos(float(m) * chi - theta) for m, theta in zip(ARM_MODES, self.phases)])
            self._tables[period] = table
        return table

    def _ring(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Per radius of ``R`` (n,): the unit amplitudes (modes, n), the ring mean of e^{κψ} (n,) and the
        ridge's amplitude a (n,). A radius that carries no mode has mean 1 and a = 0: the ridge is 1 there
        and no mask is formed."""
        R = np.asarray(R, dtype=float)
        unit = self.unit_at(R)
        n = R.size
        mean, amplitude = np.ones(n), np.zeros(n)
        present = (unit > 0.0).T.astype(np.int64) @ _BITS
        if self.ratio == 1.0 or not present.any():
            return unit, self._means(unit, present, mean), amplitude
        kappa, C = self.kappa, self.ratio
        inside_cells = self.mask_share(R) * PHASE_CELLS
        reach = np.abs(unit).sum(axis=0)  # Σ|u_m|: ψ lies within ±reach
        for code in np.unique(present[present > 0]):
            table = self._table(pattern_period(int(code)))
            rows = np.nonzero(present == code)[0]
            for start in range(0, rows.size, RING_BLOCK):
                at = rows[start:start + RING_BLOCK]
                v = np.exp(kappa * (unit[:, at].T @ table))  # (block, cells)
                total = v.sum(axis=1)
                z = total / PHASE_CELLS
                # The mask: the cells in falling order of ψ (v rises with ψ), the one the level cuts counted
                # by the fraction of it inside.
                cum = np.concatenate([np.zeros((at.size, 1)), np.cumsum(-np.sort(-v, axis=1), axis=1)], axis=1)
                cells = inside_cells[at]
                whole = np.minimum(np.floor(cells).astype(np.int64), PHASE_CELLS - 1)
                lo = np.take_along_axis(cum, whole[:, None], axis=1)[:, 0]
                hi = np.take_along_axis(cum, whole[:, None] + 1, axis=1)[:, 0]
                inside = lo + (cells - whole) * (hi - lo)
                v_in = inside / z / cells
                v_out = (total - inside) / z / (PHASE_CELLS - cells)
                denominator = (v_in - 1.0) - C * (v_out - 1.0)
                # Clipped so the ridge is nowhere negative: v lies within e^{±κ reach} over the mean.
                v_hi, v_lo = np.exp(kappa * reach[at]) / z, np.exp(-kappa * reach[at]) / z
                ok = (denominator > 0.0) & (v_hi > 1.0) & (v_lo < 1.0)
                with np.errstate(divide="ignore", invalid="ignore"):
                    a = np.where(ok, (C - 1.0) / np.where(ok, denominator, 1.0), 0.0)
                    a = np.where(ok, np.clip(a, -1.0 / np.where(ok, v_hi - 1.0, 1.0), 1.0 / np.where(ok, 1.0 - v_lo, 1.0)), 0.0)
                mean[at], amplitude[at] = z, a
        return unit, mean, amplitude

    def _means(self, unit: np.ndarray, present: np.ndarray, mean: np.ndarray) -> np.ndarray:
        """The ring means alone (a ratio of 1 needs no mask): e^{κψ} averaged over the fixed cells."""
        kappa = self.kappa
        for code in np.unique(present[present > 0]):
            table = self._table(pattern_period(int(code)))
            rows = np.nonzero(present == code)[0]
            for start in range(0, rows.size, RING_BLOCK):
                at = rows[start:start + RING_BLOCK]
                mean[at] = np.exp(kappa * (unit[:, at].T @ table)).mean(axis=1)
        return mean

    def amplitude(self, R: np.ndarray) -> np.ndarray:
        """a(R) = (C − 1)/[(v̄_in − 1) − C (v̄_out − 1)], clipped so the ridge is nowhere negative; 0 on a
        ring that carries no mode."""
        R = np.asarray(R, dtype=float)
        return self._ring(R.ravel())[2].reshape(R.shape)

    def _psi(self, unit: list[np.ndarray], chi: np.ndarray) -> np.ndarray | float:
        """ψ = Σ_m u_m cos(m χ − θ_m), the modes with no amplitude anywhere among ``unit`` left out."""
        total: np.ndarray | None = None
        for m, theta, u in zip(ARM_MODES, self.phases, unit):
            if not np.any(u):
                continue
            term = u * np.cos(float(m) * chi - theta)
            total = term if total is None else total + term
        return 0.0 if total is None else total

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ_gas(R, φ)/Σ_gas(R) on the (R, φ) grid. Mean 1 around every ring: every m is an integer."""
        R = np.asarray(R, dtype=float)
        unit, mean, a = self._ring(R)
        taper, phase, bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)
        phi = np.asarray(phi, dtype=float)[None, :]
        psi = self._psi([u[:, None] for u in unit], phi - phase[:, None])
        v = np.exp(self.kappa * psi) / mean[:, None]
        ridge_w, bar_w = (1.0 - taper) * a, self.bar * taper
        return 1.0 + ridge_w[:, None] * (v - 1.0) + bar_w[:, None] * np.cos(2.0 * (phi - bar_angle))

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise. The ring's
        mean and amplitude are computed once per distinct radius."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        shape = np.broadcast_shapes(R.shape, phi.shape)
        R_b, phi_b = np.broadcast_to(R, shape).ravel(), np.broadcast_to(phi, shape).ravel()
        radii, back = np.unique(R_b, return_inverse=True)
        unit, mean, a = self._ring(radii)
        unit, mean, a = unit[:, back], mean[back], a[back]
        taper, phase, bar_angle = bar_terms(R_b, self.pitch_deg, self.bar_length)
        v = np.exp(self.kappa * self._psi(list(unit), phi_b - phase)) / mean
        out = 1.0 + (1.0 - taper) * a * (v - 1.0) + self.bar * taper * np.cos(2.0 * (phi_b - bar_angle))
        return out.reshape(shape)

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` at one radius - exactly, by the ridge's
        Fourier series at that radius (each harmonic's sector mean is a sine or cosine difference); the
        error is the dropped coefficients', under 1e-15 of the ring's mean."""
        radius = np.array([float(R)])
        unit, _, a = self._ring(radius)
        taper, phase, bar_angle = bar_terms(radius, self.pitch_deg, self.bar_length)
        edges = np.asarray(edges, dtype=float)
        lo, hi = edges[:-1], edges[1:]

        def mean_cos(k: np.ndarray, shift: float) -> np.ndarray:  # k (H,) → (H, sectors)
            k = np.asarray(k, dtype=float)[:, None]
            return (np.sin(k * (hi - shift)) - np.sin(k * (lo - shift))) / (k * (hi - lo))

        def mean_sin(k: np.ndarray, shift: float) -> np.ndarray:
            k = np.asarray(k, dtype=float)[:, None]
            return -(np.cos(k * (hi - shift)) - np.cos(k * (lo - shift))) / (k * (hi - lo))

        ridge: np.ndarray | float = 0.0
        present = int((unit[:, 0] > 0.0).astype(np.int64) @ _BITS)
        if present and a[0] != 0.0:
            # v(χ) = c_0 + 2 Σ_n Re(c_n e^{i n period χ}) on one period of the ring's pattern, by FFT.
            period = pattern_period(present)
            chi = np.arange(HARMONIC_SAMPLES) * (2.0 * math.pi / period / HARMONIC_SAMPLES)
            c = np.fft.rfft(np.exp(self.kappa * self._psi(list(unit[:, 0]), chi))) / HARMONIC_SAMPLES
            c = (c[1:HARMONIC_SAMPLES // 2] / c[0].real)
            kept = np.nonzero(np.abs(c) >= HARMONIC_FLOOR)[0]
            if kept.size:
                c = c[: int(kept[-1]) + 1]
                k = period * np.arange(1, c.size + 1, dtype=float)
                shift = float(phase[0])
                ridge = 2.0 * (c.real[:, None] * mean_cos(k, shift) - c.imag[:, None] * mean_sin(k, shift)).sum(axis=0)
        bar = mean_cos(np.array([2.0]), bar_angle)[0]
        return 1.0 + (1.0 - taper[0]) * a[0] * ridge + self.bar * taper[0] * bar

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8)."""
        grid = np.linspace(lo, hi, steps + 1)
        return invert_azimuths(u, grid, self.contrast(radius, grid))


def compute_gas_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    # Everything is read, nothing drawn: the ratio is the bar stage's derived class mean (D210 as
    # amended), the shape the stellar pattern's modes and the layer's phases.
    # A composed field (S55, D214): with the layer off compose gives the neutral value the declaration states,
    # everywhere, and the ratio the bar stage derived is untouched. With it on, the pattern object comes from
    # compose too, and a pattern with nothing to place (unresolved, or a ratio of 1 with no bar) is the neutral.
    cells = (R.size, ctx.grid.phi.size)

    def ridge() -> np.ndarray:
        shape = _compose.gas_pattern(ctx.fields, R, ctx.constants)
        if shape is None or shape.flat:
            return _compose.neutral(GAS_DENSITY_CONTRAST, cells)
        made = shape.contrast(R, ctx.grid.phi)
        # Every ring keeps its gas on any grid. Sampled at cell centres, the ridge's harmonics alias where a sum
        # of the arm numbers' multiples equals the cell count: nothing on the default 360 cells, 6e-4 of the
        # ring's mean on 36 cells with one four-armed mode (its ninth harmonic). A ring whose sampled mean has
        # left 1 is divided by it; one that has not is untouched, so the default grid's field is the law's own.
        mean = made.mean(axis=1, keepdims=True)
        aliased = np.abs(mean - 1.0) > RING_MEAN_TOLERANCE
        return np.where(aliased, made / np.where(aliased, mean, 1.0), made)

    return {"gas_density_contrast": _compose.field(ctx.fields, GAS_DENSITY_CONTRAST, cells, ridge)}


GAS_PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="gas_pattern", slot="gas_pattern", checkpoint=3,
        about=(
            "The gas's own arm pattern: a narrow ridge on the crests of the stellar pattern, whatever its "
            "modes - the exponential of their sum at unit amplitude over its ring mean - its width a fixed "
            "fraction of one mode's arm-to-arm period and its amplitude set by the derived ratio of means "
            "inside an arm mask (D210 as amended; D215). Reads the stellar pattern's modes and phases and "
            "no gas column: the gas's response, stated as a shape. It draws nothing; "
            "its field is seeded through the pattern's drawn pitch and amplitudes and the layer's phases."
        ),
        compute=compute_gas_pattern,
        reads_constants=GAS_PATTERN_CONSTANTS,
        requires=GAS_PATTERN_READS,
        publishes=(GAS_DENSITY_CONTRAST,),
    )
)
