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
  stellar bar's, B its ``bar_contrast``. The taper multiplies a (v − 1) and the bar's term is added
  outside the ridge: neither is ranked (D215, gate ruling 9).
- **The stellar pattern the ridge follows.** ψ(R, φ) = Σ_m u_m(R) cos(m χ − θ_m), χ = φ − ln R · cot p:
  the stellar arm modes at unit amplitude **before the bar's taper**, u_m = A_m(R) / (A w_arm(R)) with
  A_m the published mode amplitudes, A the published ``arm_contrast`` and θ_m the layer's phases.
  (The plan writes ψ = (c − 1)/A; outside the bar's reach that is this ψ, and inside it S51's form
  keeps the taper and the bar outside the ridge, which is the only reading under which one mode is
  S51's field.)
- **The ridge by rank** (D215, gate ruling 7, the second turn). On each ring the gas takes S51's
  ridge values in the order of the stellar pattern:

      v(R, φ) = V(q) / z,    V(q) = e^{κ cos πq} / I₀(κ),

  q(R, φ) the **fraction of the ring on which ψ exceeds ψ(R, φ)** - the measure of the superlevel
  set, 0 on ψ's highest crest and 1 in its deepest trough. For one mode ψ = cos θ, the set is
  |θ′| < |θ|, q = |θ|/π and v is S51's von Mises e^{κ cos θ}/I₀(κ) - through the same code, with no
  one-mode case. Every ring carries S51's histogram of ridge values whatever its modes and phases:
  what the stellar pattern decides is where round the ring each value sits. So the crest is the
  form's (gate ruling 10): v lies in [e^{−κ}, e^{κ}]/I₀(κ), and outside the bar's reach the gas lies
  in [1 − a(½, C), 1 + a(½, C)(e^κ/I₀ − 1)], 0.53 to 3.07 at the defaults, on every ring and every
  seed. Nothing is clipped, capped or floored after composition to obtain it.

  *Retired at the second turn:* v = e^{κψ} over its ring mean, the first reading of "the gas follows
  any pattern". ψ at unit power reaches 2.2 where five modes' crests meet, and e^{κψ} is calibrated
  on a cosine of reach 1: the crest at R₀ was 11 times the ring's mean (S51's: 3.07) - knots, not
  ridges, whatever the scaling. The exponential of a sum of modes is forbidden.

  A rank map is not a local law: a point's gas depends on its whole ring's ψ, and on a ring with
  several modes the ridge's width is not the measured one (a tall crest takes a wide ridge, a low
  one none). It is P1's instrument, and P2's shock retires it.
- **No offset** (D210 ruling 3): the ridge's crest is the stellar pattern's crest. The
  density-wave law, Δφ = (Ω − Ω_p) t with the shock on the inner edge inside corotation, is the
  named alternative; the model publishes no spiral pattern speed to sign it with.
- **The width** (D210 ruling 4) is a fixed fraction of one mode's arm-to-arm period:
  κ = ln 2 / (1 − cos πW) is the von Mises's exact half-maximum relation, so for one mode
  v(±πW) = v(0)/2 and the full width at half maximum is W of the period.
- **The amplitude** (D210 ruling 5) is derived from the measured ratio of means with the source's
  own mask: g is affine in v, so C = [1 + a(v̄_in − 1)]/[1 + a(v̄_out − 1)] inverts to
  a = (C − 1)/[(v̄_in − 1) − C (v̄_out − 1)], clipped so the ridge is nowhere negative.
  **The mask** is the part of the ring where ψ is highest, as large a share of the ring as the
  source's mask covers - q < s(R): a mask of full width W_m perpendicular to an arm covers the
  share m W_m / (2π R sin p) of a ring with m arms, capped at a half, and with several modes m is
  the ring's power-weighted arm number m_eff(R) = Σ_m m A_m² / Σ_m A_m² (the lead's reading, D215:
  it is m for one mode and does not know the phases). Since every ring has S51's histogram, v̄_in
  and v̄_out depend on the share alone: they are S51's own sums at the half-width πs.
- **The fade follows the forcing amplitude** (D215, gate ruling 8). The ratio of means the ring is
  set to is C(R) = 1 + (C − 1) ρ(R), ρ(R) = min(1, (Σ_m u_m(R)²)^{1/2}): the ring's stellar arm
  amplitude in units of A, the taper excluded (it already multiplies a (v − 1)) and the saturation
  included (a saturated ring forces less). One fully amplified mode has ρ = 1 and C(R) = C; where
  the disc amplifies little the ratio falls to 1 with it, continuously - nothing shocks on nothing -
  and a ring that carries no mode has v = 1, a = 0 and no mask. (The first turn's rule set C on
  every ring that carried any mode, so the amplitude grew as the pattern faded.) The ratio
  following the gain - the quadratic response - is the named alternative; P2's solver measures
  the exponent.
- **The contrast C** is ``gas_arm_contrast``, published by the derived ``bar`` stage: the
  non-grand-design class's ratio to the grand designs' by the two-fold pattern's amplification
  weight, as the stellar amplitude's mean is (D175). **No residual is drawn** (D210 as amended,
  debt #131): the source's spread is over arm segments and radial bins, not galaxies.

**How q is computed, each count known in advance (A1).** One period of the ring's pattern - 2π over
the greatest common divisor of the arm numbers the ring carries - is cut into ``PHASE_CELLS`` cells.
ψ, ψ′ and ψ″ are read at the cells' edges; ψ's inflections and then its extrema are bracketed on
those cells (an extremum pair inside one cell is parted by the inflection between them) and refined;
the extrema join the edges as nodes, so between two nodes ψ is monotone and a level crosses it at
most once. For a point, the crossings of ψ − ψ(point) are bracketed by sign on the nodes and each
is refined: Newton from an inverse-Hermite start, kept inside its bracket, at most ``NEWTON_STEPS``
evaluations, a root accepted when the next iterate's error is bounded under ``CROSSING_TOLERANCE``
(1e-12 in χ) by the step and the series' second derivative; what is not accepted by then is
bisected ``BISECTION_STEPS`` times. The point's own crossing is the point. The measure of the
superlevel set is the sum of the falling crossings less the rising ones (plus the period where the
period's first node is inside), so q is the measure itself and no rank of cells: a linearly
interpolated rank of the cells is 1e-5 off at one mode. A crossing within about 1e-5 of an extremum
is determined only to ψ's own rounding over its slope there, which no step count mends.

**The mask's means** are S51's: midpoint sums of V over the fixed cells of q, taken from the crest
outward, the one the share cuts counted by the fraction of it inside; z is V's mean over the same
cells (1 to rounding). Against the integral v̄_in is off by 2e-7 of itself at the cap and 7e-5 at a
half-width of 0.5: S51's quadrature, reproduced and not refined.

**The sector means** come from the ridge's Fourier series at the radius: V(q(χ)) sampled at
``HARMONIC_SAMPLES`` points over one period, each harmonic's sector mean a sine or cosine
difference. For one mode the ridge is analytic and the series' dropped tail is under 1e-15. With
several modes V(q(χ)) is continuous but has corners where ψ passes a level at which the superlevel
set gains or loses a piece, so the series falls off slowly and ``HARMONIC_SAMPLES`` = 1024 gives
the sector means to one or two parts in 10³ of the ring's mean (1.1e-3 at worst over thirty-two
sectors for the Milky Way template and 1.9e-3 for ``ngc_4414``; pinned in ``tests/test_modes.py``);
they still average to 1 round the ring exactly, which is what keeps a ring's expected count.

**The grid field** is the ridge sampled at the model's φ cells. One mode's ridge is analytic and its
sampled ring mean is 1 to rounding on the default grid; several modes' is not smooth, and its
sampled mean leaves 1 by up to about one part in 10³. The stage divides a ring by its sampled mean wherever
that has left 1 by more than ``RING_MEAN_TOLERANCE`` (as it has since S51 for a coarse φ grid), so
every ring keeps its gas; the sampled field can therefore pass the form's bound by that factor.

**Why its own stage, and why seeded.** It reads no seed of its own and draws nothing; it reads the
pattern's amplitudes, pitch and bar, which carry seeded draws, and the layer's phases, so
``graph`` labels its one field seeded through those requirements (D55: a stage that reads a
seeded or a synthetic field publishes seeded fields).
"""

from __future__ import annotations

import functools
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
    effective_arm_number,
    invert_azimuths,
)

PHASE_CELLS = 360  # the fixed cells over one period of the ring's pattern: the brackets, and the mask's sums (A1)
NEWTON_STEPS = 6  # evaluations a crossing's refinement may take before it is bisected instead
BISECTION_STEPS = 40  # a cell is at most 1 degree wide: 40 halvings leave 1.6e-14 rad
CROSSING_TOLERANCE = 1e-12  # rad of χ: what a refined crossing is bounded to
HARMONIC_SAMPLES = 1024  # the FFT that gives the ridge's Fourier coefficients for the sector means
HARMONIC_FLOOR = 1e-15  # harmonics under this (of the ring's mean) are dropped (FFT rounding ~1e-16)
WORK_CELLS = 1 << 22  # points × nodes per block of the crossing search: bounds the working arrays, no number

RING_MEAN_TOLERANCE = 1e-12  # a sampled ring mean further from 1 than this is renormalised (the φ grid's sampling)

# What the gas's pattern is built from, and so what every stage that places by it requires (S56, D215): the
# ratio of means, the arm amplitude the modes are scaled by, and the stellar pattern's own reads - the modes
# and their phases, never ``arm_multiplicity``.
GAS_PATTERN_READS: tuple[str, ...] = ("gas_arm_contrast", "arm_contrast", *PATTERN_READS)
GAS_PATTERN_CONSTANTS: tuple[str, ...] = ("GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH")

_CELLS = -math.pi + (np.arange(PHASE_CELLS) + 0.5) * (2.0 * math.pi / PHASE_CELLS)  # cell centres over (−π, π)
_ORDER = np.argsort(np.abs(_CELLS), kind="stable")  # from the crest outward: the falling order of V
_BITS = 1 << np.arange(len(ARM_MODES))
_M = np.asarray(ARM_MODES, dtype=float)


def kappa_for_width(width: float) -> float:
    """The concentration whose one-mode ridge has a full width at half maximum of ``width`` of the period.

    v(θ)/v(0) = e^{κ(cos θ − 1)} = 1/2 at θ = πW, so κ = ln 2 / (1 − cos πW): exact for a von
    Mises, no Gaussian limit taken. 4.977 at W = 0.17.
    """
    w = min(max(float(width), 1e-4), 1.0)
    return math.log(2.0) / (1.0 - math.cos(math.pi * w))


@functools.lru_cache(maxsize=16)
def _bessel_i0(kappa: float) -> float:
    return float(np.i0(kappa))


def ridge_value(q: np.ndarray, kappa: float) -> np.ndarray:
    """V(q) = e^{κ cos πq}/I₀(κ): S51's ridge value at rank q, e^κ/I₀ on the crest (q = 0) and e^{−κ}/I₀ in the
    trough (q = 1). Its mean over q is 1."""
    return np.exp(kappa * np.cos(math.pi * np.asarray(q, dtype=float))) / _bessel_i0(kappa)


def pattern_period(present: int) -> int:
    """The greatest common divisor of the arm numbers a ring carries (``present``: bit k for mode k of
    ARM_MODES): the ring's pattern repeats that many times round it. 1 for a ring that carries none."""
    out = 0
    for k, m in enumerate(ARM_MODES):
        if present >> k & 1:
            out = math.gcd(out, m)
    return out or 1


@functools.lru_cache(maxsize=16)
def _mask_table(kappa: float) -> tuple[np.ndarray, float]:
    """Sums of V over the fixed cells of q from the crest outward - S51's cells: q = |θ|/π at the centres of
    PHASE_CELLS cells of θ - for every whole number of cells; and V's mean over them, z."""
    v = ridge_value(np.abs(_CELLS) / math.pi, kappa)[_ORDER]
    cum = np.concatenate([[0.0], np.cumsum(v)])
    return cum, float(cum[-1]) / PHASE_CELLS


def mask_means(share: np.ndarray, kappa: float) -> tuple[np.ndarray, np.ndarray]:
    """(v̄_in, v̄_out): the ridge's mean over the share of the ring where q < ``share``, and over the rest - on
    the fixed cells of q, the one the share cuts counted by the fraction of it inside, both over z. S51's sums:
    the share is its mask's half-width over π."""
    cum, z = _mask_table(kappa)
    cells = np.asarray(share, dtype=float) * PHASE_CELLS
    inside = np.interp(cells, np.arange(cum.size), cum)
    return inside / cells / z, (cum[-1] - inside) / (PHASE_CELLS - cells) / z


@functools.lru_cache(maxsize=8)
def _edge_table(period: int) -> tuple[np.ndarray, np.ndarray]:
    """cos(m x_k) and sin(m x_k) for every mode at the lower edges x_k of the PHASE_CELLS cells of one period of
    a pattern that repeats ``period`` times round the ring: (modes, cells) each."""
    x = (-math.pi + np.arange(PHASE_CELLS) * (2.0 * math.pi / PHASE_CELLS)) / period
    return np.cos(_M[:, None] * x[None, :]), np.sin(_M[:, None] * x[None, :])


def _harmonics(chi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """cos(m χ) and sin(m χ) for every mode, (modes, points) each, by the angle-addition recurrence from one
    cosine and one sine."""
    c1, s1 = np.cos(chi), np.sin(chi)
    two = 2.0 * c1
    cos_m, sin_m = np.empty((len(ARM_MODES), chi.size)), np.empty((len(ARM_MODES), chi.size))
    c_before, s_before, c, s = np.ones_like(c1), np.zeros_like(s1), c1, s1
    for m in range(2, ARM_MODES[-1] + 1):
        c, c_before = two * c - c_before, c
        s, s_before = two * s - s_before, s
        if m in ARM_MODES:
            cos_m[ARM_MODES.index(m)], sin_m[ARM_MODES.index(m)] = c, s
    return cos_m, sin_m


def _series(a: np.ndarray, b: np.ndarray, chi: np.ndarray, order: int) -> tuple[np.ndarray, np.ndarray]:
    """(f, f′) at each point for f the ``order``-th derivative of ψ = Σ_m a_m cos mχ + b_m sin mχ; ``a`` and
    ``b`` are (modes, points)."""
    c, s = _harmonics(chi)
    even, odd = a * c + b * s, b * c - a * s
    if order == 0:
        return even.sum(axis=0), _M @ odd
    if order == 1:
        return _M @ odd, -(_M**2) @ even
    return -(_M**2) @ even, -(_M**3) @ odd


def _start(lo, hi, f_lo, f_hi, s_lo, s_hi, rising) -> np.ndarray:
    """Where to start a bracketed root from: the inverse cubic Hermite through both ends (their values and
    slopes); where an end is too flat for it - an extremum of ψ is a node - the root of the parabola through
    both ends with the flatter end's slope; failing those the secant point, and the middle."""
    width, rise = hi - lo, f_hi - f_lo
    with np.errstate(divide="ignore", invalid="ignore"):
        chord = rise / width
        t = -f_lo / rise
        hermite = (lo * (2.0 * t**3 - 3.0 * t**2 + 1.0) + hi * (3.0 * t**2 - 2.0 * t**3)
                   + rise * ((t**3 - 2.0 * t**2 + t) / s_lo + (t**3 - t**2) / s_hi))
        steep = (s_lo * chord > 0.0) & (s_hi * chord > 0.0) & (np.abs(s_lo) >= 0.2 * np.abs(chord)) & (np.abs(s_hi) >= 0.2 * np.abs(chord))
        sign = np.where(rising, 1.0, -1.0)
        c_lo = (rise - s_lo * width) / width**2
        from_lo = lo - 2.0 * f_lo / (s_lo + sign * np.sqrt(s_lo**2 - 4.0 * c_lo * f_lo))
        c_hi = (s_hi * width - rise) / width**2
        from_hi = hi - 2.0 * f_hi / (s_hi + sign * np.sqrt(s_hi**2 - 4.0 * c_hi * f_hi))
        x = np.where(steep, hermite, np.where(np.abs(s_lo) <= np.abs(s_hi), from_lo, from_hi))
        inside = np.isfinite(x) & (x > lo) & (x < hi)
        x = np.where(inside, x, lo + t * width)
    inside = np.isfinite(x) & (x >= lo) & (x <= hi)
    return np.where(inside, x, 0.5 * (lo + hi))


def _refine(a, b, lo, hi, x, target, order, bound, rising) -> np.ndarray:
    """The root of ψ's ``order``-th derivative less ``target`` in each bracket [lo, hi], on which it is monotone
    (``rising``: negative at lo), to CROSSING_TOLERANCE.

    Newton from ``x``, kept inside the bracket (a step that leaves it is replaced by the bracket's middle), for
    at most NEWTON_STEPS evaluations. A root is accepted when the *next* iterate's error is bounded: with
    η = |f/f′| at the iterate and M ≥ |f″| on the bracket (``bound``: Σ_m m^(order+2) u_m), M η ≤ |f′|/4 puts the
    root within 2η and the next iterate within 2 M η²/|f′| of it. What is not accepted by then is bisected
    BISECTION_STEPS times, which leaves the bracket's width over 2^40. Every count is fixed in advance (A1).
    """
    out = np.empty(x.size)
    idx = np.arange(x.size)
    lo, hi, x = lo.copy(), hi.copy(), x.copy()
    target = np.broadcast_to(np.asarray(target, dtype=float), x.shape).copy()
    for _ in range(NEWTON_STEPS):
        if not idx.size:
            return out
        f, slope = _series(a, b, x, order)
        f = f - target
        above = f > 0.0
        upper = above == rising
        hi, lo = np.where(upper, x, hi), np.where(upper, lo, x)
        with np.errstate(divide="ignore", invalid="ignore"):
            step = f / slope
            eta, steepness = np.abs(step), np.abs(slope)
            new = x - step
            inside = np.isfinite(new) & (new > lo) & (new < hi)
            done = (inside & (bound * eta <= 0.25 * steepness) & (2.0 * bound * eta * eta <= CROSSING_TOLERANCE * steepness)) | (f == 0.0)
        new = np.where(f == 0.0, x, np.where(inside, new, 0.5 * (lo + hi)))
        out[idx[done]] = new[done]
        keep = ~done
        idx, a, b, lo, hi, x = idx[keep], a[:, keep], b[:, keep], lo[keep], hi[keep], new[keep]
        target, bound, rising = target[keep], bound[keep], rising[keep]
    for _ in range(BISECTION_STEPS if idx.size else 0):
        x = 0.5 * (lo + hi)
        f = _series(a, b, x, order)[0] - target
        upper = (f > 0.0) == rising
        hi, lo = np.where(upper, x, hi), np.where(upper, lo, x)
    out[idx] = 0.5 * (lo + hi)
    return out


@dataclass(frozen=True, slots=True, eq=False)
class _Rings:
    """The nodes of a batch of rings that share one pattern period: per ring the cells' edges over one period
    with ψ's extrema among them, in order, so that ψ is monotone between two nodes; ψ and ψ′ at each."""

    period: int             # the pattern repeats this many times round the ring
    a: np.ndarray           # (modes, rings): u_m cos θ_m
    b: np.ndarray           # (modes, rings): u_m sin θ_m
    bound: np.ndarray       # (rings,): Σ m² u_m ≥ |ψ″|
    nodes: np.ndarray       # (rings, nodes): χ, ascending, the first at −π/period and the last one period on
    values: np.ndarray      # (rings, nodes): ψ
    slopes: np.ndarray      # (rings, nodes): ψ′ (0 at an extremum)

    @property
    def span(self) -> float:
        return 2.0 * math.pi / self.period

    @property
    def origin(self) -> float:
        return -math.pi / self.period

    @classmethod
    def of(cls, a: np.ndarray, b: np.ndarray, period: int) -> "_Rings":
        n = a.shape[1]
        cos_k, sin_k = _edge_table(period)
        span, origin = 2.0 * math.pi / period, -math.pi / period
        h = span / PHASE_CELLS
        reach = np.abs(a) + np.abs(b)  # ≥ u_m
        psi = a.T @ cos_k + b.T @ sin_k                                       # (rings, cells) at the lower edges
        d1 = (a * _M[:, None]).T @ -sin_k + (b * _M[:, None]).T @ cos_k
        d2 = -((a * _M[:, None] ** 2).T @ cos_k + (b * _M[:, None] ** 2).T @ sin_k)
        after = lambda f: np.roll(f, -1, axis=1)  # noqa: E731  (the cell's upper edge: the period closes)

        # ψ's inflections, bracketed by ψ″'s sign at the edges: at most one is kept per cell.
        up2 = d2 > 0.0
        r, k = np.nonzero(up2 != after(up2))
        inflection = np.full((n, PHASE_CELLS), np.nan)
        slope_there = np.zeros((n, PHASE_CELLS))
        if r.size:
            lo = origin + k * h
            f_lo, f_hi = d2[r, k], after(d2)[r, k]
            with np.errstate(divide="ignore", invalid="ignore"):
                x = lo - f_lo / (f_hi - f_lo) * h
            x = np.where(np.isfinite(x), x, lo + 0.5 * h)
            t = _refine(a[:, r], b[:, r], lo, lo + h, x, 0.0, 2, (reach * _M[:, None] ** 4).sum(axis=0)[r], f_hi > f_lo)
            inflection[r, k] = t
            slope_there[r, k] = _series(a[:, r], b[:, r], t, 1)[0]

        # ψ's extrema, bracketed by ψ′'s sign: on a cell, or on its two parts where an inflection cuts it.
        cut = np.isfinite(inflection)
        up1, up1_after, up_cut = d1 > 0.0, after(d1 > 0.0), slope_there > 0.0
        edges = origin + np.arange(PHASE_CELLS) * h
        parts = []
        for where, x_lo, x_hi, f_lo, f_hi in (
            (~cut & (up1 != up1_after), edges[None, :], edges[None, :] + h, d1, after(d1)),
            (cut & (up1 != up_cut), edges[None, :], inflection, d1, slope_there),
            (cut & (up_cut != up1_after), inflection, edges[None, :] + h, slope_there, after(d1)),
        ):
            r, k = np.nonzero(where)
            pick = lambda f: np.broadcast_to(f, (n, PHASE_CELLS))[r, k]  # noqa: E731
            parts.append((r, k, pick(x_lo), pick(x_hi), pick(f_lo), pick(f_hi)))
        r, k, lo, hi, f_lo, f_hi = (np.concatenate(p) for p in zip(*parts))
        with np.errstate(divide="ignore", invalid="ignore"):
            x = lo - f_lo / (f_hi - f_lo) * (hi - lo)
        x = np.where(np.isfinite(x) & (x >= lo) & (x <= hi), x, 0.5 * (lo + hi))
        extremum = _refine(a[:, r], b[:, r], lo, hi, x, 0.0, 1, (reach * _M[:, None] ** 3).sum(axis=0)[r], f_hi > f_lo)
        level = _series(a[:, r], b[:, r], extremum, 0)[0]

        # The nodes: the cells' edges and the extrema, in order. An extremum in cell k comes after edge k and
        # after the ring's earlier extrema; a ring with fewer extrema than the widest repeats its last edge.
        count = np.bincount(r, minlength=n)
        width = PHASE_CELLS + 1 + int(count.max(initial=0))
        nodes = np.full((n, width), origin + span)
        values = np.repeat(psi[:, :1], width, axis=1)
        slopes = np.repeat(d1[:, :1], width, axis=1)
        order = np.lexsort((extremum, r))
        r, k, extremum, level = r[order], k[order], extremum[order], level[order]
        rank = np.arange(r.size) - (np.cumsum(count) - count)[r]
        earlier = np.zeros((n, PHASE_CELLS + 1), dtype=np.int64)
        np.add.at(earlier, (r, k + 1), 1)
        slot = np.arange(PHASE_CELLS + 1)[None, :] + np.cumsum(earlier, axis=1)
        closed = lambda f: np.concatenate([f, f[:, :1]], axis=1)  # noqa: E731  (the last edge is the first, a period on)
        np.put_along_axis(nodes, slot, np.broadcast_to(origin + np.arange(PHASE_CELLS + 1) * h, slot.shape), axis=1)
        np.put_along_axis(values, slot, closed(psi), axis=1)
        np.put_along_axis(slopes, slot, closed(d1), axis=1)
        nodes[r, k + 1 + rank], values[r, k + 1 + rank], slopes[r, k + 1 + rank] = extremum, level, 0.0
        return cls(period, a, b, (reach * _M[:, None] ** 2).sum(axis=0), nodes, values, slopes)

    def fraction(self, ring: np.ndarray, chi: np.ndarray) -> np.ndarray:
        """q at the points ``chi`` (rows, k), each row on the ring ``ring`` (rows,) names: the fraction of the
        ring on which ψ exceeds its value at the point - the measure of the superlevel set over the period."""
        ring = np.asarray(ring, dtype=np.int64)
        rows, k = chi.shape
        span, origin = self.span, self.origin
        at = origin + np.mod(chi - origin, span)  # the point inside the period the nodes cover
        level = _series(np.repeat(self.a[:, ring], k, axis=1), np.repeat(self.b[:, ring], k, axis=1), at.ravel(), 0)[0].reshape(rows, k)
        out = np.empty((rows, k))
        width = self.nodes.shape[1]
        columns = max(1, min(k, WORK_CELLS // width))
        block = max(1, WORK_CELLS // (width * columns))
        for first in range(0, rows, block):
            for left in range(0, k, columns):
                rr = ring[first:first + block]
                L, here = level[first:first + block, left:left + columns], at[first:first + block, left:left + columns]
                above = self.values[rr][:, None, :] > L[:, :, None]            # (rows, points, nodes)
                bi, ji, ki = np.nonzero(above[:, :, 1:] != above[:, :, :-1])   # one crossing per change of sign
                r = rr[bi]
                lo, hi = self.nodes[r, ki], self.nodes[r, ki + 1]
                rising = above[bi, ji, ki + 1]
                point, target = here[bi, ji], L[bi, ji]
                own = (point >= lo) & (point <= hi)  # the point's own crossing is the point
                root = point.copy()
                solve = ~own
                if solve.any():
                    r, lo, hi, ki_, target, up = r[solve], lo[solve], hi[solve], ki[solve], target[solve], rising[solve]
                    f_lo, f_hi = self.values[r, ki_] - target, self.values[r, ki_ + 1] - target
                    x = _start(lo, hi, f_lo, f_hi, self.slopes[r, ki_], self.slopes[r, ki_ + 1], up)
                    root[solve] = _refine(self.a[:, r], self.b[:, r], lo, hi, x, target, 0, self.bound[r], up)
                shape = L.shape
                # Falling crossings close a stretch of the superlevel set and rising ones open one; the period's
                # first node is inside it where ψ there is above the level.
                measure = np.bincount(bi * shape[1] + ji, weights=np.where(rising, -root, root), minlength=shape[0] * shape[1])
                measure = measure.reshape(shape) + span * above[:, :, 0]
                out[first:first + block, left:left + columns] = np.clip(measure / span, 0.0, 1.0)
        return out


GAS_DENSITY_CONTRAST = FieldDecl(
    name="gas_density_contrast", label="Gas density contrast Σ_gas(R, φ)/Σ_gas(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=4.0), meaningful_zero=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the ridge's law applied to where the arms are - and 1 everywhere
    # with the randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "Σ_gas(R, φ)/Σ_gas(R): mean 1 round every ring, so every radial gas profile is unchanged. "
        "A narrow ridge on the crests of the stellar pattern, whatever that pattern is. On each ring the "
        "gas takes one arm's ridge values - a von Mises profile whose full width at half maximum is a "
        "fixed fraction of the arm-to-arm period, half the stellar arm's as in the one galaxy measured "
        "both ways - in the order of the stellar arm modes' sum: the highest value where that sum is "
        "highest on the ring, the lowest where it is lowest, each point ranked by the fraction of its "
        "ring that stands higher. For one mode that is the von Mises ridge in that arm's phase; with "
        "several, the tallest stellar crest carries the widest ridge and a low one little or none. So "
        "every ring has the same spread of values, and outside the bar the gas stays between 0.53 and "
        "3.07 of its ring's mean at the defaults whatever the modes and their phases. It sits on the "
        "stellar crest with no offset. The density-wave offset "
        "law, Δφ = (Ω − Ω_p)·t with the shock inside the arm inside corotation, is the named "
        "alternative and is not adopted: the model publishes no spiral pattern speed to sign it "
        "with, and the evidence for co-rotating arms reads zero mean offset with scatter; no "
        "offset field is published for it. Inside the bar the term is the stellar bar's own. The "
        "ridge's amplitude is derived from the measured ratio of means (gas_arm_contrast) over "
        "the part of the ring where the stellar modes' sum is highest, as large a share of the ring "
        "as the source's own arm mask covers - a fixed width perpendicular to an arm, for the ring's "
        "power-weighted number of arms, at most half the ring. The ratio fades with the forcing: it is "
        "the measured one where the stellar arms have their full amplitude, and falls to 1 in step with "
        "that amplitude where the disc amplifies little, so where a ring carries no mode there is no "
        "ridge. A rank on the ring, not a local law: a point's gas depends on its whole ring. The gas's "
        "response to the stellar pattern: it reads no gas column. A composed "
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
    linearly in R (held at the end values beyond the grid). A point's rank is then the measure of ψ's
    superlevel set on the ring at the point's own radius, from that ring's fixed cells and the refined
    crossings; nothing is read off a stored (R, φ) table.
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

    def effective_arm_number(self, R: np.ndarray, unit: np.ndarray | None = None) -> np.ndarray:
        """m_eff(R) = Σ_m m u_m² / Σ_m u_m² (the taper and the arm amplitude cancel): the ring's
        power-weighted arm number; NaN on a ring with no mode. The pattern stage's one function
        (:func:`galaxy.stages.pattern.effective_arm_number`), on the unit amplitudes at ``R``. (``unit``: the
        amplitudes at ``R``, where the caller already holds them.)"""
        return effective_arm_number(self.unit_at(R) if unit is None else unit)

    def mask_share(self, R: np.ndarray, unit: np.ndarray | None = None) -> np.ndarray:
        """The share of the ring the source's arm mask covers: m_eff W_m / (2π R sin p), at most a half and
        at least one quadrature cell; NaN on a ring with no mode (no mask is formed)."""
        R = np.maximum(np.asarray(R, dtype=float), 1e-3)
        sin_p = math.sin(math.radians(min(max(self.pitch_deg, 1.0), 89.0)))
        # S51's half-width in the ridge's phase, θ_m = m (W_m/2)/(R sin p) clamped at π/2, over π.
        theta_m = np.minimum(self.effective_arm_number(R, unit) * 0.5 * self.mask_width / (R * sin_p), 0.5 * math.pi)
        return np.clip(theta_m, 0.5 * (2.0 * math.pi / PHASE_CELLS), 0.5 * math.pi) / math.pi

    def forcing(self, R: np.ndarray, unit: np.ndarray | None = None) -> np.ndarray:
        """ρ(R) = min(1, (Σ_m u_m²)^½): the ring's stellar arm amplitude in units of the arm amplitude A, the
        bar's taper excluded and the saturation included (D215, gate ruling 8). 1 for one fully amplified mode."""
        return np.minimum(1.0, np.sqrt(((self.unit_at(R) if unit is None else unit) ** 2).sum(axis=0)))

    def ratio_at(self, R: np.ndarray, unit: np.ndarray | None = None) -> np.ndarray:
        """C(R) = 1 + (C − 1) ρ(R): the ratio of means the ring is set to - the published one where the stellar
        arms have their full amplitude, 1 where the ring carries no mode."""
        return 1.0 + (self.ratio - 1.0) * self.forcing(R, unit)

    def extremes(self) -> tuple[float, float]:
        """(v at the crest, v in the trough): V(0)/z and V(1)/z, e^{±κ}/I₀(κ) to rounding."""
        kappa = self.kappa
        _, z = _mask_table(kappa)
        return float(ridge_value(0.0, kappa)) / z, float(ridge_value(1.0, kappa)) / z

    def amplitude(self, R: np.ndarray, unit: np.ndarray | None = None) -> np.ndarray:
        """a(R) = (C(R) − 1)/[(v̄_in − 1) − C(R) (v̄_out − 1)] at the ring's mask share, clipped so the ridge is
        nowhere negative; 0 on a ring that carries no mode."""
        R = np.asarray(R, dtype=float)
        unit = self.unit_at(R) if unit is None else unit
        share = self.mask_share(R, unit)
        carries = np.isfinite(share)
        v_in, v_out = mask_means(np.where(carries, share, 0.5), self.kappa)
        C = self.ratio_at(R, unit)
        crest, trough = self.extremes()
        a = (C - 1.0) / ((v_in - 1.0) - C * (v_out - 1.0))
        return np.where(carries, np.clip(a, -1.0 / (crest - 1.0), 1.0 / (1.0 - trough)), 0.0)

    def _rings(self, unit: np.ndarray) -> list[tuple[np.ndarray, _Rings]]:
        """The rings that carry a mode, by the period of their pattern: (their indices among ``unit``'s columns,
        their nodes)."""
        present = (unit > 0.0).T.astype(np.int64) @ _BITS
        periods = np.array([pattern_period(int(code)) for code in present])
        cos_t, sin_t = (np.asarray([f(t) for t in self.phases])[:, None] for f in (math.cos, math.sin))
        out = []
        for period in np.unique(periods[present > 0]):
            rows = np.nonzero((periods == period) & (present > 0))[0]
            out.append((rows, _Rings.of(unit[:, rows] * cos_t, unit[:, rows] * sin_t, int(period))))
        return out

    def rank(self, R: np.ndarray, chi: np.ndarray, unit: np.ndarray | None = None) -> np.ndarray:
        """q at the points χ (rows, k) of the rings at ``R`` (rows,): the fraction of each point's ring on which
        ψ exceeds its value at the point. NaN on a ring that carries no mode (ψ is 0 there: no rank)."""
        R, chi = np.asarray(R, dtype=float), np.asarray(chi, dtype=float)
        q = np.full(chi.shape, np.nan)
        for rows, rings in self._rings(self.unit_at(R) if unit is None else unit):
            q[rows] = rings.fraction(np.arange(rows.size), chi[rows])
        return q

    def ridge(self, R: np.ndarray, chi: np.ndarray, unit: np.ndarray | None = None) -> np.ndarray:
        """v = V(q)/z at the points χ (rows, k) of the rings at ``R`` (rows,); 1 on a ring with no mode."""
        q = self.rank(R, chi, unit)
        _, z = _mask_table(self.kappa)
        return np.where(np.isfinite(q), ridge_value(np.where(np.isfinite(q), q, 0.0), self.kappa) / z, 1.0)

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ_gas(R, φ)/Σ_gas(R) on the (R, φ) grid: the law at each cell's centre (mean 1 round the ring over
        the ring itself; a grid's sampled mean is the stage's to hold)."""
        R = np.asarray(R, dtype=float)
        unit = self.unit_at(R)
        a = self.amplitude(R, unit)
        taper, phase, bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)
        phi = np.asarray(phi, dtype=float)[None, :]
        v = self.ridge(R, phi - phase[:, None], unit)
        ridge_w, bar_w = (1.0 - taper) * a, self.bar * taper
        return 1.0 + ridge_w[:, None] * (v - 1.0) + bar_w[:, None] * np.cos(2.0 * (phi - bar_angle))

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise. Each distinct
        radius is one ring: its nodes are found once, and each of its points is ranked on them."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        shape = np.broadcast_shapes(R.shape, phi.shape)
        R_b, phi_b = np.broadcast_to(R, shape).ravel(), np.broadcast_to(phi, shape).ravel()
        radii, back, counts = np.unique(R_b, return_inverse=True, return_counts=True)
        taper, phase, bar_angle = bar_terms(R_b, self.pitch_deg, self.bar_length)
        chi = phi_b - phase
        v = np.empty(R_b.size)
        if np.all(counts == counts[0]):  # the same number of points on every ring: one row a ring
            order = np.argsort(back, kind="stable")
            v[order] = self.ridge(radii, chi[order].reshape(radii.size, -1)).ravel()
        else:  # a row a point; the rings are still found once
            unit = self.unit_at(radii)
            q = np.full(R_b.size, np.nan)
            for rows, rings in self._rings(unit):
                index = np.full(radii.size, -1)
                index[rows] = np.arange(rows.size)
                on = index[back] >= 0
                q[on] = rings.fraction(index[back][on], chi[on, None])[:, 0]
            _, z = _mask_table(self.kappa)
            v = np.where(np.isfinite(q), ridge_value(np.where(np.isfinite(q), q, 0.0), self.kappa) / z, 1.0)
        out = 1.0 + (1.0 - taper) * self.amplitude(R_b) * (v - 1.0) + self.bar * taper * np.cos(2.0 * (phi_b - bar_angle))
        return out.reshape(shape)

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` at one radius, by the ridge's Fourier series
        at that radius: V(q(χ)) at HARMONIC_SAMPLES points of one period, each harmonic's sector mean a sine or
        cosine difference. They average to 1 round the ring exactly. For one mode the series' dropped tail is
        under 1e-15; with several the ridge has corners and the means are good to about 1e-3 of the ring's mean
        (the module's docstring)."""
        radius = np.array([float(R)])
        unit = self.unit_at(radius)
        a = float(self.amplitude(radius)[0])
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
        if present and a != 0.0:
            # v(χ) = c_0 + 2 Σ_n Re(c_n e^{i n period χ}) on one period of the ring's pattern, by FFT.
            period = pattern_period(present)
            chi = np.arange(HARMONIC_SAMPLES) * (2.0 * math.pi / period / HARMONIC_SAMPLES)
            c = np.fft.rfft(self.ridge(radius, chi[None, :])[0]) / HARMONIC_SAMPLES
            c = c[1:HARMONIC_SAMPLES // 2] / c[0].real
            kept = np.nonzero(np.abs(c) >= HARMONIC_FLOOR)[0]
            if kept.size:
                c = c[: int(kept[-1]) + 1]
                k = period * np.arange(1, c.size + 1, dtype=float)
                shift = float(phase[0])
                ridge = 2.0 * (c.real[:, None] * mean_cos(k, shift) - c.imag[:, None] * mean_sin(k, shift)).sum(axis=0)
        bar = mean_cos(np.array([2.0]), bar_angle)[0]
        return 1.0 + (1.0 - taper[0]) * a * ridge + self.bar * taper[0] * bar

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
        # Every ring keeps its gas on any grid. The ridge's mean is 1 over the ring; sampled at the grid's cell
        # centres it is 1 to rounding only where the ridge is analytic and resolved (one mode on the default 360
        # cells; 6e-4 off on 36 cells with one four-armed mode, its ninth harmonic). A ring of several modes is
        # ranked, its ridge has corners, and its sampled mean leaves 1 by a few parts in 10^4. A ring whose
        # sampled mean has left 1 is divided by it; one that has not is untouched.
        mean = made.mean(axis=1, keepdims=True)
        aliased = np.abs(mean - 1.0) > RING_MEAN_TOLERANCE
        return np.where(aliased, made / np.where(aliased, mean, 1.0), made)

    return {"gas_density_contrast": _compose.field(ctx.fields, GAS_DENSITY_CONTRAST, cells, ridge)}


GAS_PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="gas_pattern", slot="gas_pattern", checkpoint=3,
        about=(
            "The gas's own arm pattern: a narrow ridge on the crests of the stellar pattern, whatever its "
            "modes - one arm's ridge values laid round each ring in the order of the stellar modes' sum - "
            "its width a fixed fraction of one mode's arm-to-arm period and its amplitude set by the "
            "derived ratio of means inside an arm mask, fading with the stellar arms' amplitude (D210 as "
            "amended; D215). Reads the stellar pattern's modes and phases and "
            "no gas column: the gas's response, stated as a shape. It draws nothing; "
            "its field is seeded through the pattern's drawn pitch and amplitudes and the layer's phases."
        ),
        compute=compute_gas_pattern,
        reads_constants=GAS_PATTERN_CONSTANTS,
        requires=GAS_PATTERN_READS,
        publishes=(GAS_DENSITY_CONTRAST,),
    )
)
