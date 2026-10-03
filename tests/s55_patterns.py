"""S55's two pattern laws, frozen: the oracle Phase P1's single-mode regression is held to (S56, DECISIONS.md D215).

Until S56 the stellar pattern was one cosine of a drawn arm number and the gas's ridge a von Mises in that one
arm's phase (S51, D210). P1 replaces both with a law over several modes, and its gate says that **with one mode -
one m, phase 0, the amplifier's weight 1 on every ring - the stellar field is S55's exactly and the gas field is
S51's to 1e-9**. A gate of that kind needs the old field as numbers, and the old code is gone from the model the
day the new one lands. So the two classes' arithmetic is copied here, **verbatim from ``model/galaxy/stages/
pattern.py`` and ``gas_pattern.py`` at the tag ``s55``** (the lines that make the grid field: ``_terms``,
``contrast``, the von Mises, the mask's quadrature, the amplitude), and nothing here is ever edited to follow
the model.

What ties the copy to S55: ``tests/layer_reference_s55.json`` holds, under ``single_mode``, the digests of the two
fields **as S55's own classes made them** on the default galaxy's scalars - the published fields at the drawn
m = 4, and the same classes at m = 2 - captured before any of P1's model code moved. ``tests/test_modes.py``
recomputes them from this module and compares bit for bit, then holds the new law's single-mode field to these
arrays.
"""

from __future__ import annotations

import math

import numpy as np

PHASE_CELLS = 360
_THETA = -math.pi + (np.arange(PHASE_CELLS) + 0.5) * (2.0 * math.pi / PHASE_CELLS)
_ORDER = np.argsort(np.abs(_THETA), kind="stable")


def stellar_terms(R: np.ndarray, arm: float, bar: float, pitch_deg: float, bar_length: float):
    """S55's ``ArmPattern._terms``: per radius the arm weight, the bar weight, the arm phase; and the bar's angle."""
    R = np.maximum(np.asarray(R, dtype=float), 1e-3)
    bar_w = np.exp(-((R / max(bar_length, 1e-3)) ** 4))
    cot = 1.0 / math.tan(math.radians(min(max(pitch_deg, 1.0), 89.0)))
    phase = np.log(R) * cot
    bar_angle = float(math.log(max(bar_length, 1e-3)) * cot)
    return arm * (1.0 - bar_w), bar * bar_w, phase, bar_angle


def stellar_contrast(R, phi, arm: float, bar: float, m: float, pitch_deg: float, bar_length: float) -> np.ndarray:
    """S55's ``ArmPattern.contrast``: 1 + A (1 - w_bar) cos m(phi - ln R cot p) + B w_bar cos 2(phi - phi_bar)."""
    arm_w, bar_w, phase, bar_angle = stellar_terms(R, arm, bar, pitch_deg, bar_length)
    phi = np.asarray(phi, dtype=float)[None, :]
    arms = arm_w[:, None] * np.cos(m * (phi - phase[:, None]))
    bar_term = bar_w[:, None] * np.cos(2.0 * (phi - bar_angle))
    return 1.0 + arms + bar_term


def stellar_sector_means(R: float, edges, arm: float, bar: float, m: float, pitch_deg: float, bar_length: float) -> np.ndarray:
    """S55's ``ArmPattern.sector_means``."""
    arm_w, bar_w, phase, bar_angle = stellar_terms(np.array([R]), arm, bar, pitch_deg, bar_length)
    a, b = edges[:-1], edges[1:]

    def mean_cos(k: float, shift: float) -> np.ndarray:
        return (np.sin(k * (b - shift)) - np.sin(k * (a - shift))) / (k * (b - a))

    return 1.0 + arm_w[0] * mean_cos(m, float(phase[0])) + bar_w[0] * mean_cos(2.0, bar_angle)


def kappa_for_width(width: float) -> float:
    w = min(max(float(width), 1e-4), 1.0)
    return math.log(2.0) / (1.0 - math.cos(math.pi * w))


def von_mises(theta: np.ndarray, kappa: float) -> np.ndarray:
    return np.exp(kappa * np.cos(theta)) / float(np.i0(kappa))


def mask_means(theta_m: np.ndarray, kappa: float) -> tuple[np.ndarray, np.ndarray]:
    """S51's mask quadrature: v's mean over the fixed cells inside |theta| < theta_m, and over the rest."""
    v = von_mises(_THETA, kappa)[_ORDER]
    pairs = v[0::2] + v[1::2]
    cum = np.concatenate([[0.0], np.cumsum(pairs)])
    total = float(cum[-1])
    step = 2.0 * math.pi / PHASE_CELLS
    edges = np.arange(cum.size) * step
    theta_m = np.clip(np.asarray(theta_m, dtype=float), 0.5 * step, 0.5 * math.pi)
    inside = np.interp(theta_m, edges, cum)
    cells = 2.0 * theta_m / step
    return inside / cells, (total - inside) / (PHASE_CELLS - cells)


def mask_half_width(R: np.ndarray, m: float, pitch_deg: float, mask_width: float) -> np.ndarray:
    R = np.maximum(np.asarray(R, dtype=float), 1e-3)
    sin_p = math.sin(math.radians(min(max(pitch_deg, 1.0), 89.0)))
    return np.minimum(m * 0.5 * mask_width / (R * sin_p), 0.5 * math.pi)


def gas_amplitude(R: np.ndarray, ratio: float, m: float, pitch_deg: float, width: float, mask_width: float) -> np.ndarray:
    """S51's ``GasPattern.amplitude``: a(R) = (C - 1)/[(v_in - 1) - C (v_out - 1)], clipped."""
    kappa = kappa_for_width(width)
    v_in, v_out = mask_means(mask_half_width(R, m, pitch_deg, mask_width), kappa)
    a = (ratio - 1.0) / ((v_in - 1.0) - ratio * (v_out - 1.0))
    v0, vpi = float(von_mises(np.array(0.0), kappa)), float(von_mises(np.array(math.pi), kappa))
    return np.clip(a, -1.0 / (v0 - 1.0), 1.0 / (1.0 - vpi))


def gas_contrast(R, phi, ratio: float, bar: float, m: float, pitch_deg: float, bar_length: float,
                 width: float, mask_width: float) -> np.ndarray:
    """S51's ``GasPattern.contrast``: 1 + w_arm a (v - 1) + w_bar B cos 2(phi - phi_bar), v the von Mises in the
    arm's phase. (The stage divided a ring by its sampled mean only where that had left 1 by 1e-12 - nowhere on the
    default grid - so on that grid this is the published field.)"""
    arm_w, bar_w, phase, bar_angle = stellar_terms(R, 1.0, bar, pitch_deg, bar_length)
    ridge_w = arm_w * gas_amplitude(R, ratio, m, pitch_deg, width, mask_width)
    phi = np.asarray(phi, dtype=float)[None, :]
    v = von_mises(m * (phi - phase[:, None]), kappa_for_width(width))
    return 1.0 + ridge_w[:, None] * (v - 1.0) + bar_w[:, None] * np.cos(2.0 * (phi - bar_angle))
