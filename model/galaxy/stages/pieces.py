"""The stellar arms as a census of pieces: the law applied to the realisation (checkpoint 3; S60, BUILD_III Phase P5;
DECISIONS.md D219).

From S56 to S59 the stellar arms were five cosine modes with drawn phases on one winding. Set beside the goal
pictures that reads as many broad, equal, faint arms, holds no arm that could be pinned, and with S59's kinks on
common rings reads as ripples. The owner ruled the arms a **census of arm pieces** (D219), and a conditional gate
ruled what a piece, a chain, the class and the budget are. This module is the composing side:

- **The law** is the ``pattern`` stage's and the ``bar`` stage's, the same with the randomness layer on or off: each
  ring's *budget* of arm power ½ Σ_m A_m(R)² (``arm_power_budget``, the bar's taper and the saturation in it), the
  arm number the law counts there n(R) (``arm_design_count``), the disc's pitch, and the width of an arm across
  itself at every radius (``arm_piece_width``).
- **The realisation** is the layer's (``galaxy/layer/arm_pieces.py``): the table ``arm_piece``, one row a piece -
  where its inner end stands, its pitch, how far round the disc it runs, the chain it belongs to, and which of its
  ends meets another chain.
- **The composed field** is made here, by :class:`ArmPattern`: the pieces' sum, exact at any point.

**A piece, by its perpendicular distance** (the gate's second follow-up to D219, item 1, in its own words): "A
piece is a Gaussian in the perpendicular distance to its locus, within its extent, as D219 item 1 says: in
log-polar coordinates x = ln(R/R0), y = phi − phi0 the locus is the line through the origin along (sin p_j, cos
p_j); the perpendicular distance is d = R |x cos p_j − y sin p_j| and the position along it s = R (x sin p_j + y
cos p_j), both regular at p_j = 0 where the piece is an arc of its drawn extent at its radius; the width sigma is
the bounded law's at the point's R; a ring's profile of a piece is the Gaussian in d times the window in s on the
solver's cells, its ring mean and variance by the same quadrature, the forcing term by term as now. The wrapped
normal in azimuth was an approximation that holds only at moderate pitch and is retired; the near-circular pieces
are arcs, not rings."

As built. A piece starts at (R_s, φ_s) and runs outward; with x = ln(R/R_s), ψ the azimuth from its start *in
the piece's own sense* (the trailing sense for a positive pitch, the other for a negative one) and (s_p, c_p) =
(|sin p|, |cos p|), its locus is the straight line from the origin along (s_p, c_p), of length T = Δβ / c_p:

    d' = x c_p − ψ s_p   (across, signed),     t = x s_p + ψ c_p   (along, 0 at the start, T at the end),

both in the plane's own unit (radians); a point's distances in kpc are R |d'| and R t, R the point's own radius.
The piece is

    E(R, φ) = W(t) · exp(−d'² / 2ς²),     ς = σ(R)/R,   σ = FWHM(R) / (2 √(2 ln 2)),

FWHM the bounded width at the point's radius (:meth:`ArmPattern.width_at`). **The azimuth's turns**: a piece spans
at most half a turn of its own extent, and a point sees the image of the piece nearest to it - ψ is taken within
half a turn of the piece's own middle, ψ ∈ [Δβ/2 − π, Δβ/2 + π). Where the two images meet, opposite the piece's
middle, the piece is under e^{−π²/8ς²} of its height wherever its window is open (the algebra is in
:meth:`Pieces.unwrapped`'s docstring). A piece of pitch exactly 0 is an arc of its extent at its start's radius,
running in the trailing sense.

**The chain's locus** (the gate's third follow-up to D219, item 1, quoted whole in :meth:`ArmPattern._chains`).
Since the fourth pass a piece is not read alone: **a chain's excess at a point is the Gaussian of the point's
distance to the chain's polyline** in the log-polar plane - the perpendicular distance to the nearest piece where
the point's foot falls inside that piece, the distance to the nearest piece end otherwise - times the taper along
the chain at its free ends, read at the arc length to the point's foot. So a kink is rounded on the outside and
counted once on the inside, a joined end is a round cap of the piece's own width that sinks into the ridge it
meets, a free end tapers to nothing over one width (the taper is a declared placeholder: no taper length is
measured, a debt), and far from any kink it is the third pass's d exactly. The window W of the third pass - the
piece cut square across at a kink and at a join - is gone with the square edges it made. A point's distance to a
piece is taken with the piece at the image within half a turn of its middle and each end at its nearest image
(:meth:`ArmPattern._candidate`); a chain is its pieces' least.

**The field** (D219 item 4). c(R, φ) = 1 + [bar's body] + a(R) Σ_c (E_c(R, φ) − ⟨E_c⟩(R)): every chain with a
piece within reach of the radius, each less its own mean round the ring there, so **the ring's mean is 1
exactly** at every radius and nothing is divided. Where two chains meet they add: "a branch is two arms' material
in one place" (the third follow-up); the join's excess is bounded by nothing but the saturation. ⟨E_c⟩(R) is the
exact integral round the ring (:class:`Stretches`): the ring is cut into stretches of azimuth on each of which one
feature of the polyline - a piece's perpendicular or a piece's end - is the nearest, found by every azimuth at
which two features within reach are equidistant, and on each stretch the excess is a line (the taper) times a
Gaussian in the azimuth, :func:`gauss_linear`'s integrand - by the error function, or by an eight-point Gauss
rule where the stretch is under half a dispersion's worth of argument, each exact to rounding. a(R) is the
chains' one amplitude on the ring:

- *The count, continuous* (the second follow-up, item 3): "The count on a ring is the sum over crossing chains of
  their taper weights, so B and the bounded width are continuous in R and a lone tapering chain's amplitude goes
  to zero as the square root of its weight; the realised variance inside tapers falls a little under the budget
  and is recorded." N(R) = Σ_c min(1, s_c/w), s_c the distance along chain c from where its locus crosses the
  ring to its nearer free end (no free end: 1), w the width.
- *The width, bounded* (the first follow-up, item 3): "a piece's FWHM on a ring is min(the width law's, half the
  ring's crossing spacing π R sin p / N(R)), N the chains crossing" - a bound, not a target, never raised. With
  the count a sum of taper weights that themselves read the width, the two are one equation,
  w = min(law, π R sin p / N(w)); it has one solution, found in closed form (:meth:`ArmPattern.ring_state`):
  Σ_c min(w, s_c) = π R sin p, or the law's width where the chains' tapers together are shorter than that.
- *The budget, in expectation.* B(R) = √(budget / (N v)), v the variance round the ring of one designed piece of
  unit height: a full-height ridge at the disc's own pitch, a Gaussian in azimuth of dispersion σ_d = σ/(R sin p)
  seen within half a turn of its crest, v = (σ_d/2√π) erf(π/σ_d) − (σ_d²/2π) erf(π/√2σ_d)² (:func:`ring_variance`;
  the ruling's σ_d/(2√π) − σ_d²/(2π) while the ridge is narrower than its ring). For N such ridges at independent
  azimuths the expected variance is N v B²: the budget, by construction. The realised variance is published
  beside it and is never divided by. Where the designed ridge is no ridge on its ring, σ_d ≥ √π, no amplitude
  spends the budget (B = 0, counted): under the bound that takes a count under 1 - a lone chain inside its taper
  - close to the centre.
- *Positivity by the saturation alone.* E_j ≥ 0, so the pieces' sum is nowhere under −a Σ_j ⟨E_j⟩: D219's "the
  arms' mean excess ≤ 1 − b(R)". a = min(B, (1 − b(R)) / Σ_j ⟨E_j⟩), b the depth of the bar's body under the
  ring's mean: the field is non-negative at every point, **the cut is taken at the point's own radius**, nothing
  is clipped, floored or renormalised, and the cut is published on the grid's rings and counted. (In doubles the
  cut is taken four units in the last place under that ratio, :data:`CUT_IN_DOUBLES`, so that the rounded sum of
  the field's terms cannot land under nothing.)

Between the grid's rings the budget (with the bar's taper taken back out, and put back at the point's own
radius) and the width law are read linearly - the width law is linear in R, so that is the law itself - and the
count, the bounded width and B are made at the point's own radius.

**Which pieces a radius reads.** A chain's Gaussian is not cut off: a ring a few widths inside or outside a
nearly circular piece's radius holds its flank. A radius reads every piece whose nearest point comes within
:data:`REACH` dispersions of it - a piece's nearest point to a ring it does not cross is its nearer end, at the
distance in ln R past that end, so the test is exact - and a piece further off, under e^{−40.5} of its height, is
not read. The chains are summed in the table's order, one after another, so a point reads the same bits in any
batch.

**On the grid as exact cell means** (rule 5; D216). :meth:`ArmPattern.contrast_at` is the point function. The
published field holds the mean of the same function over each of the grid's φ cells on each ring - each
piece's integral over the cell by the same closed forms as its ring mean, so a ring's cells average to 1 to
rounding on any grid - with the body's exact cell means as before.

**On the solver's cells** (the second follow-up, item 1): a ring's profile of the chains on the gas solver's
cells' centres is what the gas's forcing is transformed from (``gas_pattern``) - each chain's ridge with the
pitch of its piece nearest the ring, "the forcing's pitch for a ring's term is the nearest piece's" - and the
realised ring variance and its split by arm number - the **disclosed check** of D219 item 4, published for m =
2 … 6 beside the law's A_m² by the ``arm_ring_power`` stage, read, never tuned - are that profile's, by the same
quadrature.

**What is not here.** The bar's body is ``pattern.BarBody``, unchanged. The gas's answer to the pieces is
``gas_pattern``'s, which asks this pattern for each ring's pieces. Nothing here draws: the census is the layer's.
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field, fields
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages import gas_response as _cells
from galaxy.stages.pattern import (
    ARM_MODES,
    CELLS,
    PATTERN_READS,
    PIECE_FIELDS,
    PIECE_JOINS,
    BarBody,
    bar_terms,
    invert_azimuths,
    ring_bracket,
    rotation_sense,
    sector_grid,
)

TWO_PI = 2.0 * math.pi
SQRT_PI = math.sqrt(math.pi)
FWHM_PER_SIGMA = 2.0 * math.sqrt(2.0 * math.log(2.0))  # a Gaussian's full width at half maximum over its dispersion
# How far from a piece's window, in dispersions across it, a radius still reads the piece: past it the piece is
# under e^-40.5 of its height - a quarter of a unit in the last place of 1 - and is not summed.
REACH = 9.0
# A stretch of a piece's window whose Gaussian argument changes by no more than this is integrated by the Gauss
# rule (exact to rounding there: the eight-point rule's error on e^{-u²} over half a unit of u is under 1e-19);
# a longer one by the error function, whose difference is then well conditioned.
SHORT_STRETCH = 0.5
_GAUSS_NODES, _GAUSS_WEIGHTS = np.polynomial.legendre.leggauss(8)
# The designed azimuthal dispersion past which a ring carries no arm: √π, where D219's ring variance of a piece,
# σ/(2√π) − σ²/(2π), reaches 0 (``budget_amplitude``). A piece of that dispersion is 239 degrees wide at half
# maximum on its ring.
WIDEST = math.sqrt(math.pi)
# Where the amplitude is cut, the cut is taken four units in the last place under (1 − b)/Σ⟨E_j⟩: at exactly that
# amplitude the field's least value is 0, and the doubles' own sum of 1, the body and the pieces - each rounded -
# could land a unit in the last place under it. The saturation, in the arithmetic it is made in; nothing of the
# field is clipped.
CUT_IN_DOUBLES = 1.0 - 4.0 * np.finfo(float).eps
JOINED = 1e-9  # two ends of pieces of one chain closer than this in ln R and in azimuth (rad) are one point: a kink
# ``arm_piece_join``'s values: which of a piece's ends meets another chain (the second follow-up, item 2).
JOIN_NONE, JOIN_INNER, JOIN_OUTER = PIECE_JOINS
MODE_POWER_FIELDS: tuple[str, ...] = tuple(f"arm_mode_power_{m}" for m in ARM_MODES)
# How many (radius, piece, azimuth) values one pass of a sum holds at once: a bound on memory, never on a value.
_BATCH = 2_000_000

_ERF = np.frompyfunc(math.erf, 1, 1)


def erf(x: np.ndarray) -> np.ndarray:
    """The error function, element by element: the C library's (``math.erf``), so an element is the same bits in
    any batch."""
    x = np.asarray(x, dtype=float)
    return _ERF(x).astype(float) if x.size else np.zeros(x.shape)


# --------------------------------------------------------------------------------------------------------------
# A Gaussian across, a line along: the one integral every mean of a piece is made of
# --------------------------------------------------------------------------------------------------------------


def gauss_linear(lo: np.ndarray, hi: np.ndarray, w_lo: np.ndarray, slope: np.ndarray, d0: np.ndarray, sin_abs: np.ndarray, inv: np.ndarray) -> np.ndarray:
    """∫_lo^hi (w_lo + slope (ψ − lo)) exp(−((ψ s_p − d0) inv)²) dψ, element by element (the arguments broadcast):
    a stretch of a piece's window, linear in the azimuth ψ, times its Gaussian across - d' = d0 − ψ s_p, and
    ``inv`` = 1/(√2 ς). 0 where hi ≤ lo.

    With u = (ψ s_p − d0) inv and κ = s_p inv: where the stretch is short in u (:data:`SHORT_STRETCH`), an
    eight-point Gauss rule, exact to rounding there and regular at s_p = 0 - where the Gaussian does not vary
    along the ring at all, the arc of a piece of no pitch; otherwise
    I0 = (√π/2κ)(erf u_hi − erf u_lo), I1 = ∫(ψ − lo)… = −(u_lo/κ) I0 − (e^{−u_hi²} − e^{−u_lo²})/(2κ²), and the
    integral is w_lo I0 + slope I1. Which is used is decided by the element's own numbers."""
    lo, hi, w_lo, slope, d0, sin_abs, inv = np.broadcast_arrays(*(np.asarray(v, dtype=float) for v in (lo, hi, w_lo, slope, d0, sin_abs, inv)))
    out = np.zeros(lo.shape)
    width = hi - lo
    kappa = sin_abs * inv
    with np.errstate(invalid="ignore", over="ignore"):
        open_ = width > 0.0
        short = open_ & (width * kappa <= SHORT_STRETCH)
        long_ = open_ & ~short
    if short.any():
        a, half, w0, sl, c, s, k = lo[short], 0.5 * width[short], w_lo[short], slope[short], d0[short], sin_abs[short], inv[short]
        total = np.zeros(a.shape)
        for node, weight in zip(_GAUSS_NODES, _GAUSS_WEIGHTS):
            step = half * (1.0 + node)
            total += weight * (w0 + sl * step) * np.exp(-(((a + step) * s - c) * k) ** 2)
        out[short] = half * total
    if long_.any():
        a, b, w0, sl, c, s, k = lo[long_], hi[long_], w_lo[long_], slope[long_], d0[long_], sin_abs[long_], inv[long_]
        kap = s * k
        u_lo, u_hi = (a * s - c) * k, (b * s - c) * k
        i0 = (0.5 * SQRT_PI / kap) * (erf(u_hi) - erf(u_lo))
        i1 = -(u_lo / kap) * i0 - (np.exp(-u_hi * u_hi) - np.exp(-u_lo * u_lo)) / (2.0 * kap * kap)
        out[long_] = w0 * i0 + sl * i1
    return out


def ring_variance(sigma: np.ndarray) -> np.ndarray:
    """v(σ) = (σ/2√π) erf(π/σ) − (σ²/2π) erf(π/(√2 σ))²: the variance round a ring of one designed piece of unit
    height - a Gaussian in azimuth of dispersion σ (rad) seen within half a turn of its crest (one image: the
    second follow-up's item 1 retired the wrapped normal). While the ridge is narrower than its ring it is the
    Gaussian's σ/(2√π) − σ²/(2π), D219's "ring variance"; it is positive at every σ and falls to nothing for a
    ridge that fills its ring."""
    shape = np.shape(sigma)
    s = np.atleast_1d(np.asarray(sigma, dtype=float))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        out = s / (2.0 * SQRT_PI) * erf(math.pi / s) - s * s / TWO_PI * erf(math.pi / (math.sqrt(2.0) * s)) ** 2
    return np.where(np.isfinite(s) & (s > 0.0), out, 0.0).reshape(shape)


def budget_amplitude(budget: np.ndarray, count: np.ndarray, sigma_design: np.ndarray) -> np.ndarray:
    """B = √(budget / (N v(σ_d))) per ring: the one amplitude at which N designed pieces of azimuthal dispersion
    σ_d, at independent uniform azimuths, make the budget's variance round the ring in expectation (D219 item 4).
    N is the ring's count - a sum of taper weights, any positive number (the second follow-up, item 3).

    0 where the ring has no budget or no count - and **where the designed piece is no ridge on its ring**,
    σ_d ≥ :data:`WIDEST` = √π: there the ruling's own expression for a piece's ring variance, σ_d/(2√π) − σ_d²/(2π),
    is no longer positive - a height that made the budget's variance there would grow without bound toward the
    centre. Such a ring carries no arm, and is counted (the first builder's reading of a case D219 does not
    cover; under the width's bound it takes a count under 1). Never a function of a realised power."""
    budget = np.asarray(budget, dtype=float)
    count = np.asarray(count, dtype=float)
    sigma_design = np.asarray(sigma_design, dtype=float)
    spends = (budget > 0.0) & (count > 0.0) & (sigma_design < WIDEST)
    v = ring_variance(np.where(spends, sigma_design, 1.0))
    return np.sqrt(np.where(spends, budget / np.where(spends, count * v, 1.0), 0.0))


def thickness_factor(m: np.ndarray, sin_pitch: np.ndarray, height_over_radius: np.ndarray) -> np.ndarray:
    """T = 1/(1 + k h) with k h = m (h/R)/|sin p|: how much of the razor-thin force of an arm's m-th harmonic
    reaches the gas at the midplane from stars in an exponential layer of scale height h - exact for that layer
    (D219 item 5; the constant ``ARM_LAYER_FLATTENING`` carries the source). ½ at k h = 1. Written so that a
    pitch of 0 is regular: T = |sin p| / (|sin p| + m h/R)."""
    s = np.abs(np.asarray(sin_pitch, dtype=float))
    return s / (s + np.asarray(m, dtype=float) * np.asarray(height_over_radius, dtype=float))


def forcing_factor(m: np.ndarray, x: np.ndarray, sin_pitch: np.ndarray, height_over_radius: np.ndarray) -> np.ndarray:
    """m / (X (|sin p| + m h/R)): what the m-th harmonic of a piece's excess is multiplied by to give the gas's
    forcing (D219 item 5) - the razor-thin m/(X sin p) of D216 times :func:`thickness_factor`, with the piece's
    own pitch. Bounded by R/(X h) for every m and pitch, and regular at sin p = 0. 0 at m = 0."""
    m = np.asarray(m, dtype=float)
    below = np.asarray(x, dtype=float) * (np.abs(np.asarray(sin_pitch, dtype=float)) + m * np.asarray(height_over_radius, dtype=float))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(m > 0.0, m / np.where(m > 0.0, below, 1.0), 0.0)


def sum_slots(values: np.ndarray) -> np.ndarray:
    """The sum along the last axis, one entry after another in the axis' own order: the same bits however many
    empty slots (zeros) pad the axis."""
    total = np.zeros(values.shape[:-1])
    for k in range(values.shape[-1]):
        total = total + values[..., k]
    return total


def run_argmin(key: np.ndarray, first: np.ndarray, last: np.ndarray) -> np.ndarray:
    """Per run - the contiguous slots along the last axis from a ``first`` to a ``last`` - True at the slot of the
    least ``key``, the earliest of equals; False elsewhere."""
    n, size = key.shape
    out = np.zeros(key.shape, dtype=bool)
    best, where = np.full(n, np.inf), np.zeros(n, dtype=np.int64)
    for k in range(size):
        better = first[:, k] | (key[:, k] < best)
        best, where = np.where(better, key[:, k], best), np.where(better, k, where)
        done = last[:, k]
        out[np.flatnonzero(done), where[done]] = True
    return out


def _roots(kind_i, al_i, be_i, kind_j, al_j, be_j) -> tuple[np.ndarray, np.ndarray]:
    """Where two features' squared distances are equal, as two roots in φ (NaN where there is none or only one):
    a perp's is (α + β φ)², a vertex's (φ − φ_v)² + Δx² (``al``, ``be`` are (α, β) or (φ_v, Δx) by ``kind``)."""
    nan = np.full(np.broadcast(al_i, al_j).shape, np.nan)
    both_perp, both_vertex = (kind_i == 0) & (kind_j == 0), (kind_i == 1) & (kind_j == 1)
    mixed = ~(both_perp | both_vertex)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        # Two perps: α_i + β_i φ = ±(α_j + β_j φ).
        diff, total = be_i - be_j, be_i + be_j
        r1 = np.where(both_perp & (diff != 0.0), (al_j - al_i) / np.where(diff != 0.0, diff, 1.0), nan)
        r2 = np.where(both_perp & (total != 0.0), -(al_i + al_j) / np.where(total != 0.0, total, 1.0), nan)
        # Two vertices: the bisector, (φ_i² + Δx_i²) − (φ_j² + Δx_j²) = 2 (φ_i − φ_j) φ.
        gap = al_i - al_j
        r1 = np.where(both_vertex & (gap != 0.0), (al_i * al_i + be_i * be_i - al_j * al_j - be_j * be_j) / np.where(gap != 0.0, 2.0 * gap, 1.0), r1)
        # A perp and a vertex: (α + β φ)² = (φ − φ_v)² + Δx², a quadratic in φ.
        perp_first = mixed & (kind_i == 0)
        al_p, be_p = np.where(perp_first, al_i, al_j), np.where(perp_first, be_i, be_j)
        al_v, be_v = np.where(perp_first, al_j, al_i), np.where(perp_first, be_j, be_i)
        a, b, c = be_p * be_p - 1.0, 2.0 * (al_p * be_p + al_v), al_p * al_p - al_v * al_v - be_v * be_v
        linear = mixed & (a == 0.0)
        disc = b * b - 4.0 * a * c
        has = mixed & (a != 0.0) & (disc >= 0.0)
        q = -0.5 * (b + np.copysign(np.sqrt(np.where(has, disc, 0.0)), b))
        q1 = np.where(has, q / np.where(a != 0.0, a, 1.0), nan)
        q2 = np.where(has & (q != 0.0), c / np.where(q != 0.0, q, 1.0), nan)
        r1 = np.where(mixed, np.where(linear & (b != 0.0), -c / np.where(b != 0.0, b, 1.0), q1), r1)
        r2 = np.where(mixed, q2, r2)
    return r1, r2


@dataclass(frozen=True, slots=True, eq=False)
class Stretches:
    """A batch of runs' rings cut into stretches of azimuth (M, K): on each stretch one feature of the chain's
    polyline - a piece's perpendicular (where the foot falls inside it) or a piece's end - is the nearest, and the
    chain's excess there is a line (the taper) times a Gaussian in the azimuth, :func:`gauss_linear`'s integrand.
    ``lo``, ``hi`` bound each stretch (NaN past the last); ``value`` is its integral (0 where the nearest feature
    is beyond :data:`REACH` dispersions on the whole stretch); ``w_lo``, ``slope``, ``d0``, ``scale`` the
    integrand's parameters on it and ``on`` whether it is integrated; ``w0`` each run's window start and ``inv``
    its 1/(√2 ς)."""

    w0: np.ndarray
    inv: np.ndarray
    groups: tuple  # per group of rows of one feature count: (rows, lo, hi, value, w_lo, slope, d0, scale, on)

    def whole(self) -> np.ndarray:
        """The integral over the turn, per run (M,): the stretches summed in their order."""
        out = np.zeros(self.w0.size)
        for rows, _, _, value, *_ in self.groups:
            out[rows] = sum_slots(value)
        return out

    def integral_to(self, upto: np.ndarray) -> np.ndarray:
        """The integral from each run's W0 up to the azimuths ``upto`` (M, k): whole turns counted."""
        out = np.zeros(upto.shape)
        turns, within = np.divmod(upto - self.w0[:, None], TWO_PI)
        phi = self.w0[:, None] + within
        whole = self.whole()
        for rows, lo, hi, value, w_lo, slope, d0, scale, on in self.groups:
            at = np.clip((lo[:, None, :] <= phi[rows][:, :, None]).sum(axis=2) - 1, 0, lo.shape[1] - 1)
            prefix = np.concatenate([np.zeros((rows.size, 1)), np.cumsum(value, axis=1)], axis=1)
            pick = lambda a: np.take_along_axis(a, at, axis=1)  # noqa: E731
            low = pick(lo)
            partial = np.where(pick(on), gauss_linear(low, np.maximum(phi[rows], low), pick(w_lo), pick(slope), pick(d0), pick(scale), self.inv[rows][:, None]), 0.0)
            out[rows] = turns[rows] * whole[rows][:, None] + np.take_along_axis(prefix, at, axis=1) + partial
        return out

    @classmethod
    def build(cls, p: "Pieces", pieces: np.ndarray, held: np.ndarray, x: np.ndarray, inv: np.ndarray, w: np.ndarray, w0: np.ndarray, rho: np.ndarray) -> "Stretches":
        """The decomposition for M runs: ``pieces`` (M, P) the run's pieces (``held`` where the slot holds one),
        ``x`` ln R, ``inv``, ``w`` one width in the plane's unit, ``w0`` the window start and ``rho`` the reach in
        the plane's unit, all (M,).

        **The features**, in the window [W0, W0 + 2π) of azimuth φ: for each piece its perpendicular on the
        stretch of φ where the foot falls inside it, at the image within half a turn of the piece's middle - d' =
        α + β φ, the arc length to the foot t = t_a + t_b φ - and its two ends, each at its nearest image - the
        distance² Δx² + (φ − φ_v)², the arc length the end's. A feature whose stretch wraps past the window's end
        is two images. Each has a **reach**, the part of its stretch where it is within ``rho``: beyond it the
        feature is under e^{−REACH²/2} wherever it is nearest and the stretch is not integrated.

        **The breakpoints**: the window's ends, every feature's stretch and reach ends, the taper's knots on each
        perpendicular (where the rise to full height ends, where the fall begins, where they meet), and every
        azimuth at which two features that are both within reach are equidistant (:func:`_roots`). Between two
        neighbouring breakpoints no two features cross, so the nearest at the middle is the nearest throughout;
        its taper's branch at the middle is its branch throughout."""
        M, P = pieces.shape
        W0 = w0[:, None]
        W1 = W0 + TWO_PI
        xj = x[:, None] - p.x_start[pieces]
        s, c, T = p.sin_abs[pieces], p.cos_abs[pieces], p.length[pieces]
        mid, phi0, sense = p.middle[pieces], p.phi_start[pieces], p.sense[pieces]
        before, after = p.before[pieces], p.after[pieces]
        x_end, phi_end = p.x_end[pieces], p.phi_end[pieces]
        rho2 = (rho * rho)[:, None]
        kinds, los, his, rlos, rhis, alives, als, bes, gss, gds, gcs, tas, tbs, befores, afters, lengths = ([] for _ in range(16))

        def add(kind, lo, hi, rlo, rhi, alive, al, be, gs, gd, gc, ta, tb):
            kinds.append(np.broadcast_to(kind, lo.shape)); los.append(lo); his.append(hi); rlos.append(rlo); rhis.append(rhi)
            alives.append(alive & (rhi >= rlo) & (hi > lo)); als.append(al); bes.append(be); gss.append(np.broadcast_to(gs, lo.shape))
            gds.append(gd); gcs.append(np.broadcast_to(gc, lo.shape)); tas.append(ta); tbs.append(tb)
            befores.append(before); afters.append(after); lengths.append(T)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            # The perpendicular: the foot inside, 0 ≤ t ≤ T, is a stretch of ψ (the piece's own frame).
            a = np.where(c > 0.0, -s * xj / np.where(c > 0.0, c, 1.0), np.where(xj >= 0.0, -np.inf, np.inf))
            b = np.where(c > 0.0, (T - s * xj) / np.where(c > 0.0, c, 1.0), np.where(xj >= 0.0, np.inf, -np.inf))
            lo_psi, hi_psi = np.maximum(a, mid - math.pi), np.minimum(b, mid + math.pi)
            opened = held & (hi_psi > lo_psi)
            e1, e2 = phi0 + sense * lo_psi, phi0 + sense * hi_psi
            lo_phi, hi_phi = np.minimum(e1, e2), np.maximum(e1, e2)
            n0 = np.where(opened, np.floor((lo_phi - W0) / TWO_PI), 0.0)
            lo_a, hi_raw = lo_phi - TWO_PI * n0, hi_phi - TWO_PI * n0
            for image, lo, hi, n in ((0, lo_a, np.minimum(hi_raw, W1), n0), (1, np.broadcast_to(W0, lo_a.shape), hi_raw - TWO_PI, n0 + 1.0)):
                alive = opened & ((hi_raw > W1) if image else np.ones(lo.shape, dtype=bool))
                beta = -s * sense
                alpha = xj * c + s * sense * (phi0 - TWO_PI * n)
                tb = c * sense
                ta = xj * s + c * sense * (TWO_PI * n - phi0)
                # Reach: |α + β φ| ≤ ρ.
                r_a, r_b = (-rho[:, None] - alpha) / np.where(beta != 0.0, beta, 1.0), (rho[:, None] - alpha) / np.where(beta != 0.0, beta, 1.0)
                r_lo = np.where(beta != 0.0, np.minimum(r_a, r_b), np.where(np.abs(alpha) <= rho[:, None], -np.inf, np.inf))
                r_hi = np.where(beta != 0.0, np.maximum(r_a, r_b), np.where(np.abs(alpha) <= rho[:, None], np.inf, -np.inf))
                add(0, lo, hi, np.maximum(r_lo, lo), np.minimum(r_hi, hi), alive, alpha, beta, np.abs(beta), -alpha * np.where(beta < 0.0, -1.0, 1.0), 1.0, ta, tb)
            # The two ends, each at its nearest image. **An end is nearest only beyond its own piece's foot** - a
            # point whose foot falls inside the piece is nearer the perpendicular - and beyond the foot of the
            # piece of its chain standing at it, so a kink's end lives in the kink's outside wedge alone: the
            # end's stretch is cut to those two half-lines (a pruning that changes nothing). A lone piece with
            # both ends free needs no end at all: its caps weigh nothing and no other feature of the run could
            # be taken for nearest there.
            lone = (held.sum(axis=1, keepdims=True) == 1) & (before == 0.0) & (after == 0.0)
            extent = 2.0 * mid

            def half_line(piece, psi_at, phi_img, over, bound):
                """The φ on which t of ``piece`` (ψ = ``psi_at`` + sense (φ − ``phi_img``)) is over or under
                ``bound``: (lo, hi) of a half-line."""
                live_l = piece >= 0
                l = np.where(live_l, piece, 0)
                x_l, s_l, c_l, sense_l = x[:, None] - p.x_start[l], p.sin_abs[l], p.cos_abs[l], p.sense[l]
                slope_l = c_l * sense_l
                offset = x_l * s_l + c_l * psi_at - slope_l * phi_img
                edge = (bound - offset) / np.where(slope_l != 0.0, slope_l, 1.0)
                rising = slope_l > 0.0
                flat_ok = np.where(over, offset > bound, offset < bound)
                lo_h = np.where(slope_l != 0.0, np.where(rising == over, edge, -np.inf), np.where(flat_ok, -np.inf, np.inf))
                hi_h = np.where(slope_l != 0.0, np.where(rising == over, np.inf, edge), np.where(flat_ok, np.inf, -np.inf))
                return np.where(live_l, lo_h, -np.inf), np.where(live_l, hi_h, np.inf)

            for which, dx, phi_v, arc in ((0, xj, phi0, np.zeros(T.shape)), (1, x[:, None] - x_end, phi_end, T)):
                placed = phi_v - TWO_PI * np.floor((phi_v - W0) / TWO_PI)
                half = np.sqrt(np.maximum(rho2 - dx * dx, 0.0))
                within = held & ~lone & (dx * dx <= rho2)
                gc = np.exp(-(dx * inv[:, None]) ** 2)
                link = (p.link_start if which == 0 else p.link_end)[pieces]
                link_at_end = (p.link_start_is_end if which == 0 else p.link_end_is_end)[pieces]
                for image in (0, 1):
                    if image == 0:
                        img, lo, hi, alive = placed, np.maximum(W0, placed - math.pi), np.minimum(W1, placed + math.pi), held
                    else:
                        low_side = placed - math.pi < W0
                        img = np.where(low_side, placed + TWO_PI, placed - TWO_PI)
                        lo = np.where(low_side, placed + math.pi, W0)
                        hi = np.where(low_side, W1, placed - math.pi)
                        alive = held & (low_side | (placed + math.pi > W1))
                    # Beyond its own piece's foot: t < 0 at a start, t > T at an end ...
                    own_lo, own_hi = half_line(pieces, (np.zeros(T.shape) if which == 0 else extent), img, which == 1, (np.zeros(T.shape) if which == 0 else T))
                    # ... and beyond the linked piece's: its end there (t > T) or its start (t < 0).
                    link_l = np.where(link >= 0, link, 0)
                    lnk_lo, lnk_hi = half_line(link, np.where(link_at_end, 2.0 * p.middle[link_l], 0.0), img, link_at_end, np.where(link_at_end, p.length[link_l], 0.0))
                    lo, hi = np.maximum(lo, np.maximum(own_lo, lnk_lo)), np.minimum(hi, np.minimum(own_hi, lnk_hi))
                    add(1, lo, hi, np.maximum(img - half, lo), np.minimum(img + half, hi), alive & within, img, dx, 1.0, img, gc, arc, np.zeros(T.shape))
        alive = np.concatenate(alives, axis=1)
        features = dict(kind=kinds, lo=los, hi=his, rlo=rlos, rhi=rhis, al=als, be=bes, gs=gss, gd=gds, gc=gcs, ta=tas, tb=tbs, bef=befores, aft=afters, length=lengths)
        features = {name: np.concatenate(parts, axis=1) for name, parts in features.items()}
        # The rows cut in groups of one count of live features, the live ones first in each row and the axis cut
        # to that count (a compaction: the same features, the same numbers, and no row pays for a fuller row's
        # pairs or stretches).
        count = alive.sum(axis=1)
        groups = []
        for size in np.unique(count):
            rows = np.flatnonzero(count == size)
            width = max(int(size), 1)
            # A group is cut so many rows at a time that its (rows, stretches, features) temporary stays inside
            # :data:`_ELEMENTS` - the stretches are at most the breakpoint columns, 4 + 3F + F(F − 1). A bound on
            # memory, never on a value: every number in a row is the row's own (S60, the cost).
            step = max(1, _ELEMENTS // ((4 + 3 * width + width * (width - 1)) * width))
            for start in range(0, rows.size, step):
                part = rows[start : start + step]
                order = np.argsort(~alive[part], axis=1, kind="stable")[:, :width]
                picked = {name: np.take_along_axis(v[part], order, axis=1) for name, v in features.items()}
                groups.append((part, *cls._cut(np.take_along_axis(alive[part], order, axis=1), picked, W0[part], W1[part], w[part], inv[part], rho2[part])))
        return cls(w0, inv, tuple(groups))

    @staticmethod
    def _cut(alive, f: dict, W0, W1, w, inv, rho2) -> tuple:
        """The stretches of a group of rows of one feature count: ``(lo, hi, value, w_lo, slope, d0, scale, on)``,
        each (rows, K)."""
        kind, lo, hi, rlo, rhi = f["kind"], f["lo"], f["hi"], f["rlo"], f["rhi"]
        al, be, gs, gd, gc, ta, tb, bef, aft, length = (f[n] for n in ("al", "be", "gs", "gd", "gc", "ta", "tb", "bef", "aft", "length"))
        F = kind.shape[1]
        # Breakpoints: the window's ends, the features' reach ends (a stretch's own end beyond every reach only
        # splits a stretch that is not integrated), the taper's knots, and the roots.
        parts = [W0, W1, np.where(alive, rlo, np.nan), np.where(alive, rhi, np.nan)]
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            wv = w[:, None]
            for knot in (wv - bef, length + aft - wv, 0.5 * (length + aft - bef)):
                phi_k = (knot - ta) / np.where(tb != 0.0, tb, 1.0)
                parts.append(np.where(alive & (kind == 0) & (tb != 0.0) & (phi_k >= rlo) & (phi_k <= rhi), phi_k, np.nan))
            ii, jj = np.triu_indices(F, 1)
            o_lo, o_hi = np.maximum(rlo[:, ii], rlo[:, jj]), np.minimum(rhi[:, ii], rhi[:, jj])
            pair = alive[:, ii] & alive[:, jj] & (o_hi >= o_lo)
            for r in _roots(kind[:, ii], al[:, ii], be[:, ii], kind[:, jj], al[:, jj], be[:, jj]):
                parts.append(np.where(pair & (r >= o_lo) & (r <= o_hi), r, np.nan))
        breaks = np.sort(np.concatenate(parts, axis=1), axis=1)
        breaks = breaks[:, : max(int(np.isfinite(breaks).sum(axis=1).max(initial=0)), 2)]  # (the finite ones sort first)
        b_lo, b_hi = breaks[:, :-1], breaks[:, 1:]
        valid = np.isfinite(b_hi) & (b_hi > b_lo)
        middle = 0.5 * (b_lo + b_hi)
        # The nearest feature at each stretch's middle.
        with np.errstate(invalid="ignore", over="ignore"):
            phi_c = middle[:, :, None]
            d2 = np.where(kind[:, None, :] == 0, (al[:, None, :] + be[:, None, :] * phi_c) ** 2, (phi_c - al[:, None, :]) ** 2 + be[:, None, :] ** 2)
            d2 = np.where(alive[:, None, :] & (phi_c >= lo[:, None, :]) & (phi_c <= hi[:, None, :]), d2, np.inf)
        nearest = d2.argmin(axis=2)
        at_row = np.arange(nearest.shape[0])[:, None]
        least = d2[at_row, np.arange(nearest.shape[1])[None, :], nearest]
        on = valid & (least <= rho2)
        pick = lambda v: v[at_row, nearest]  # noqa: E731  (``take_along_axis`` by plain indexing: the same elements)
        with np.errstate(invalid="ignore", over="ignore"):
            t_c = pick(ta) + pick(tb) * middle
            rise, fall = (pick(bef) + t_c) / w[:, None], (pick(aft) + pick(length) - t_c) / w[:, None]
            branch = np.argmin(np.stack([np.ones(rise.shape), rise, fall], axis=2), axis=2)
            height = np.minimum(1.0, np.minimum(rise, fall))
            slope = np.where(branch == 0, 0.0, np.where(branch == 1, pick(tb), -pick(tb)) / w[:, None])
            w_lo = pick(gc) * (height + slope * (b_lo - middle))
            slope = pick(gc) * slope
            d0, scale = pick(gd), pick(gs)
            value = np.where(on, gauss_linear(np.where(on, b_lo, 0.0), np.where(on, b_hi, 0.0), np.where(on, w_lo, 0.0), np.where(on, slope, 0.0),
                                              np.where(on, d0, 0.0), np.where(on, scale, 0.0), inv[:, None]), 0.0)
        held_stretch = np.isfinite(b_hi)  # (a stretch of no length keeps its place: ``integral_to`` counts by ``lo``)
        return np.where(held_stretch, b_lo, np.nan), np.where(held_stretch, b_hi, np.nan), value, w_lo, slope, d0, scale, on


# How many (radius, chain) rows one decomposition holds at once, and how many (row, stretch, feature) elements one
# group's cutting holds at once: bounds on memory, never on a value (S60: a row's numbers are the row's own). The
# cost of the exact mean is arithmetic volume on rows of ~100 elements, and it is paid at memory speed once the
# arrays leave the cache: on 36 584 rows at once 8192-row groups ran 1.7 s -> 1.1 s (46 MB -> 109 MB at the peak),
# but a catalogue placed a few thousand radii a call (systems.PLACE_CHUNK) is as fast with 2048-row groups and
# the smaller peak, so the bounds are kept small.
_ROWS = 2048
_ELEMENTS = 500_000
# :meth:`ArmPattern.laid` keeps its answer for a request of at most this many radii, the last this many requests.
_MEMO_RADII = 4096
_MEMO_KEPT = 8


# --------------------------------------------------------------------------------------------------------------
# The census as read: the table's rows, their chains, and which of them cross a radius
# --------------------------------------------------------------------------------------------------------------


def _met_at(point: tuple[float, float], own: int, x_start: np.ndarray, x_end: np.ndarray, phi_start: np.ndarray, phi_end: np.ndarray) -> tuple[int, float]:
    """(the piece whose locus a joined end stands on, the whole turns from that piece's line to the end's
    azimuth): the piece nearest the point (ln R, azimuth) in the log-polar plane, each tried at the image of its
    middle nearest the point and a turn either way, among those within :data:`JOINED` of it; (−1, 0) where none
    is - a table whose join flag names no meeting (a hand-built one), read as the chain's end before the sixth
    follow-up: its own line continued. ``own`` is the joined piece itself, never its own meeting."""
    px, py = point
    best, best_distance, turns = -1, JOINED, 0.0
    for q in range(x_start.size):
        if q == own:
            continue
        ax, ay, vx, vy = x_start[q], phi_start[q], x_end[q] - x_start[q], phi_end[q] - phi_start[q]
        if not (math.isfinite(vx) and math.isfinite(vy)):
            continue
        squared = vx * vx + vy * vy
        nearest = TWO_PI * round((py - (ay + 0.5 * vy)) / TWO_PI)
        for k in (-1.0, 0.0, 1.0):
            image = nearest + k * TWO_PI
            ox, oy = px - ax, py - image - ay
            t = min(max((ox * vx + oy * vy) / squared, 0.0), 1.0) if squared > 0.0 else 0.0
            distance = math.hypot(ox - t * vx, oy - t * vy)
            if distance < best_distance:
                best, best_distance, turns = q, distance, image
    return best, turns


@dataclass(frozen=True, slots=True, eq=False)
class Pieces:
    """The realised census of arm pieces, as every reader builds it from the published table (rule A9).

    One entry a piece, in the table's order: ``chain`` and ``order`` name it; ``start_radius`` (kpc) and
    ``start_azimuth`` (rad) are its inner end; ``pitch_deg`` its pitch; ``extent`` (rad) how far round the disc it
    runs; ``pinned`` whether a template stated it; ``join`` which of its ends meets another chain (0 none, 1 its
    inner end, 2 its outer end). ``turn`` is +1 where a piece of positive pitch gains azimuth outwards - the
    trailing sense, minus the disc's sense of rotation.

    **A piece in its own log-polar plane** (the module's docstring): x = ln(R/R_s) and ψ = ``sense`` · (φ − φ_s),
    ``sense`` = turn for a pitch ≥ 0 and −turn for a negative one; its locus the line from the origin along
    (|sin p|, |cos p|), of length ``length`` = Δβ/|cos p|, reaching x = Δβ |tan p|. A pitch past 90 degrees is the
    spiral of its supplement run the other way (the tangent's sign says which).

    **A chain** is the pieces of one number joined end to end: two ends of pieces of one chain at one point are a
    kink. ``before`` and ``after`` are, per piece, the length of the chain's pieces from the piece's start back
    to the chain's free end on that side, and from its end on to the other - infinite where the chain has no free
    end on that side, because its last end there is joined to another chain (``join``).

    :meth:`slots` gives, for any radius, the pieces whose locus crosses it (x_s ≤ ln R < x_e), padded to the most
    that cross any radius: the count is the census's own (rule A1). Every array below holds one entry more than
    the census, the pad's: an entry no ring is crossed by, with numbers that keep every expression finite.
    """

    chain: np.ndarray
    order: np.ndarray
    start_radius: np.ndarray
    start_azimuth: np.ndarray
    pitch_deg: np.ndarray
    extent: np.ndarray
    pinned: np.ndarray
    turn: float
    join: np.ndarray | None = None
    x_start: np.ndarray = field(init=False, repr=False)   # (n + 1,): ln R at the inner end
    x_end: np.ndarray = field(init=False, repr=False)     # ln R at the outer end
    phi_start: np.ndarray = field(init=False, repr=False)
    phi_end: np.ndarray = field(init=False, repr=False)   # the azimuth at the outer end, unwrapped from the start's
    sin_abs: np.ndarray = field(init=False, repr=False)   # |sin p|
    cos_abs: np.ndarray = field(init=False, repr=False)   # |cos p|
    sense: np.ndarray = field(init=False, repr=False)     # ±1: the way the piece's azimuth runs from its start
    length: np.ndarray = field(init=False, repr=False)    # T = Δβ/|cos p|: the locus' length in the log-polar plane
    middle: np.ndarray = field(init=False, repr=False)    # Δβ/2: the piece's own middle, in ψ
    before: np.ndarray = field(init=False, repr=False)    # the chain's length before the piece's start (inf: no free end)
    after: np.ndarray = field(init=False, repr=False)     # ... and after its end
    link_start: np.ndarray = field(init=False, repr=False)        # the piece of the chain standing at this one's start (−1 none)
    link_end: np.ndarray = field(init=False, repr=False)          # ... at its end
    link_start_is_end: np.ndarray = field(init=False, repr=False)  # whether it is that piece's end that stands there
    link_end_is_end: np.ndarray = field(init=False, repr=False)
    met_start: np.ndarray = field(init=False, repr=False)         # the piece a joined start met (−1 none)
    met_end: np.ndarray = field(init=False, repr=False)           # ... a joined end
    met_start_turns: np.ndarray = field(init=False, repr=False)   # whole turns (rad) from that piece's line to the end
    met_end_turns: np.ndarray = field(init=False, repr=False)
    chain_of: np.ndarray = field(init=False, repr=False)  # the chain's number, NaN for the pad
    breaks: np.ndarray = field(init=False, repr=False)    # the ln R at which the set of crossing pieces changes
    table: np.ndarray = field(init=False, repr=False)     # (len(breaks) + 1, most): piece indices, the pad's = n
    most: int = field(init=False)

    def __post_init__(self) -> None:
        columns = ("chain", "order", "start_radius", "start_azimuth", "pitch_deg", "extent", "pinned")
        for name in columns:
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float))
        n = self.chain.size
        object.__setattr__(self, "join", np.zeros(n) if self.join is None else np.asarray(self.join, dtype=float))
        if any(getattr(self, name).shape != (n,) for name in (*columns, "join")):
            raise ValueError("the columns of the arm pieces' table share one length")
        if n and not (np.all(np.isfinite(self.start_radius)) and np.all(self.start_radius > 0.0) and np.all(np.isfinite(self.start_azimuth))
                      and np.all(np.isfinite(self.pitch_deg)) and np.all(np.isfinite(self.extent)) and np.all(self.extent >= 0.0)
                      and np.all(np.isin(self.join, (JOIN_NONE, JOIN_INNER, JOIN_OUTER)))):
            raise ValueError("an arm piece has a positive start radius, a start azimuth, a pitch and an extent that are numbers, and a join that is 0, 1 or 2")
        pitch = np.radians(self.pitch_deg)
        tangent = np.tan(pitch)
        sin_abs, cos_abs = np.abs(np.sin(pitch)), np.abs(np.cos(pitch))
        sense = self.turn * np.where(tangent >= 0.0, 1.0, -1.0)
        x_start = np.log(self.start_radius)
        with np.errstate(over="ignore", divide="ignore"):
            x_end = x_start + self.extent * np.abs(tangent)
            length = self.extent / cos_abs
        phi_end = self.start_azimuth + sense * self.extent
        live = np.flatnonzero(x_end > x_start)  # a piece with no radial reach crosses no ring
        breaks = np.unique(np.concatenate([x_start[live], x_end[live]])) if live.size else np.zeros(0)
        breaks = breaks[np.isfinite(breaks)]
        # Between two neighbouring breaks the crossing set is one set: the pieces with x_s <= the lower break < x_e.
        lows = np.concatenate([[-np.inf], breaks])
        rows = [live[(x_start[live] <= lo) & (lo < x_end[live])] for lo in lows]
        most = max((r.size for r in rows), default=0)
        table = np.full((len(rows), max(most, 1)), n, dtype=np.int64)
        for i, r in enumerate(rows):
            table[i, : r.size] = r
        # A chain's lengths to its free ends. Two ends of pieces of one chain at one point are a kink, and the
        # chain runs through it; an end no other piece of the chain stands at is the chain's own - free, or
        # joined to another chain where the table says so (the second follow-up, item 2).
        ends = [(x_start[i], self.start_azimuth[i]) for i in range(n)] + [(x_end[i], phi_end[i]) for i in range(n)]  # entry i: start; n + i: end
        partner = np.full(2 * n, -1, dtype=np.int64)
        for chain in np.unique(self.chain):
            members = np.flatnonzero(self.chain == chain)
            own = [int(i) for i in members] + [n + int(i) for i in members]
            for e in own:
                # A kink is two ends at one point. Three or more - a piece shorter than JOINED between two others, a
                # table built so - would leave which two make the kink to the order the ends are listed in: the
                # laying stops there (the gate's sixth follow-up, item 5), a piece's own two ends counted.
                together = [f for f in own if abs(ends[f][0] - ends[e][0]) < JOINED and abs(math.remainder(ends[f][1] - ends[e][1], TWO_PI)) < JOINED]
                if len(together) >= 3:
                    raise ArithmeticError(
                        f"{len(together)} ends of chain {chain:g} stand within {JOINED:g} of one point (ln R {ends[e][0]:.12g}, "
                        f"azimuth {ends[e][1]:.12g} rad): a kink is two ends, and which two are joined cannot be told"
                    )
                for f in own:
                    if f % n != e % n and abs(ends[f][0] - ends[e][0]) < JOINED and abs(math.remainder(ends[f][1] - ends[e][1], TWO_PI)) < JOINED:
                        partner[e] = f
                        break
        closed = np.concatenate([self.join == JOIN_INNER, self.join == JOIN_OUTER])  # an end that meets another chain
        # The piece each joined end met, and the whole turns between the end's azimuth and that piece's own line
        # there (the gate's sixth follow-up, item 2: past its join a chain's anchor follows the chain it met).
        met = np.full(2 * n, -1, dtype=np.int64)
        met_turns = np.zeros(2 * n)
        for e in np.flatnonzero(closed):
            met[e], met_turns[e] = _met_at(ends[e], int(e % n), x_start, x_end, self.start_azimuth, phi_end)
        # The links: at each piece's start and end, the piece of its own chain that stands there (−1 none) and
        # whether it is that piece's end that does (else its start) - what a kink's rounding reads.
        link = np.where(partner >= 0, partner % n, -1)
        link_is_end = partner >= n
        beyond = np.zeros(2 * n)
        for e in range(2 * n):
            total, at = 0.0, e
            for _ in range(n + 1):  # a chain holds at most all the pieces (rule A1)
                if partner[at] < 0:
                    total = math.inf if closed[at] else total
                    break
                other = int(partner[at])
                total += float(length[other % n])
                at = other + n if other < n else other - n  # that piece's other end
            else:
                total = math.inf  # a chain that closes on itself has no free end
            beyond[e] = total
        pad = lambda a, value: np.concatenate([a, [value]])  # noqa: E731
        for name, value in (("x_start", pad(x_start, 0.0)), ("x_end", pad(x_end, 1.0)), ("phi_start", pad(self.start_azimuth, 0.0)),
                            ("phi_end", pad(phi_end, 0.0)), ("sin_abs", pad(sin_abs, 1.0)), ("cos_abs", pad(cos_abs, 1.0)),
                            ("sense", pad(sense, 1.0)), ("length", pad(length, 1.0)), ("middle", pad(0.5 * self.extent, 0.0)),
                            ("before", pad(beyond[:n], math.inf)), ("after", pad(beyond[n:], math.inf)),
                            ("link_start", np.concatenate([link[:n], [-1]])), ("link_end", np.concatenate([link[n:], [-1]])),
                            ("link_start_is_end", np.concatenate([link_is_end[:n], [False]])), ("link_end_is_end", np.concatenate([link_is_end[n:], [False]])),
                            ("met_start", np.concatenate([met[:n], [-1]])), ("met_end", np.concatenate([met[n:], [-1]])),
                            ("met_start_turns", pad(met_turns[:n], 0.0)), ("met_end_turns", pad(met_turns[n:], 0.0)),
                            ("chain_of", pad(self.chain, math.nan)), ("breaks", breaks), ("table", table)):
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        object.__setattr__(self, "most", int(most))

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], turn: float) -> "Pieces":
        """The census of a run's published table (:data:`~galaxy.stages.pattern.PIECE_FIELDS`)."""
        columns = [np.asarray(fields[name], dtype=float) for name in PIECE_FIELDS]
        return cls(*columns[:7], turn=turn, join=columns[7] if len(columns) > 7 else None)

    @property
    def count(self) -> int:
        return int(self.chain.size)

    @property
    def joins(self) -> int:
        """How many ends of pieces meet another chain: the realised number of joins of the galaxy."""
        return int((self.join != JOIN_NONE).sum())

    def slots(self, R: np.ndarray) -> np.ndarray:
        """The pieces whose locus crosses each radius, shaped (…R's shape, max(most, 1)): indices into the padded
        arrays, the pad's index where fewer cross. A radius is crossed by a piece from its inner end up to, not
        including, its outer end."""
        with np.errstate(divide="ignore"):
            x = np.log(np.asarray(R, dtype=float))
        return self.table[np.searchsorted(self.breaks, x, side="right")]

    def chains_crossing(self, R: np.ndarray) -> np.ndarray:
        """How many chains have a piece whose locus crosses each radius, shaped as ``R``: a whole number (what the
        births are counted on; the budget's count is :meth:`ArmPattern.count_at`)."""
        slots = self.slots(R)
        chain = np.sort(self.chain_of[slots], axis=-1)  # the pad's NaN sorts last
        fresh = np.concatenate([np.isfinite(chain[..., :1]), np.isfinite(chain[..., 1:]) & (chain[..., 1:] != chain[..., :-1])], axis=-1)
        return fresh.sum(axis=-1)

    def geometry(self, R: np.ndarray, slots: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(live, azimuth, |sin p|) of each slot's piece at each radius: whether the slot holds a piece, where the
        piece's locus stands at the radius - linear in ln R between its ends, and on the same line beyond them -
        and the sine of its pitch. ``R`` broadcasts against ``slots``' leading shape."""
        with np.errstate(divide="ignore"):
            x = np.log(np.asarray(R, dtype=float))[..., None]
        x0, x1 = self.x_start[slots], self.x_end[slots]
        live = slots < self.count
        with np.errstate(invalid="ignore"):
            # (A piece that runs to infinity is a spoke; an empty slot stands at azimuth 0 and weighs nothing.)
            share = np.where(live & np.isfinite(x1) & np.isfinite(x), (x - x0) / (x1 - x0), 0.0)
        azimuth = self.phi_start[slots] + share * (self.phi_end[slots] - self.phi_start[slots])
        return live, azimuth, self.sin_abs[slots]

    def along(self, slots: np.ndarray, x_to: np.ndarray) -> np.ndarray:
        """The azimuth at ln R = ``x_to`` of **the chain** of each slot's piece, followed along its polyline from
        that piece: outward through the pieces joined end to start while the target lies past a piece's end,
        inward through those joined start to end while it lies before a piece's start; where the chain ends, or
        turns back in radius (a measured arm that kinks back), the last piece's own line continued (the gas's
        carried map, D219 item 6: "along the pieces' loci" - since the fourth pass the chains'). **Past a join -
        a chain's end that met another chain - it follows the chain it met** (the gate's sixth follow-up, item 2:
        "the chain's material is there"), on that chain's polyline by the same rules. ``x_to`` broadcasts against
        ``slots``; an empty slot reads azimuth 0."""
        base, turns = self.along_parts(slots, x_to)
        return base + turns

    def along_parts(self, slots: np.ndarray, x_to: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """:meth:`along` as (the azimuth on the line of the piece it ends on, the whole turns from that line to the
        slot's own chain's unwrapping): two chains that read one piece read the first to the bit, whichever of
        them it is followed from - so the anchors of a chain and of the chain it joined coincide exactly past
        the join, and the turns are added only to a displacement."""
        slots, x_to = np.broadcast_arrays(np.asarray(slots), np.asarray(x_to, dtype=float))
        at = slots.copy()
        turns = np.zeros(at.shape)
        for _ in range(self.count + 1):
            x0, x1 = self.x_start[at], self.x_end[at]
            live = at < self.count
            out_next = self.link_end[at]
            outward = live & (x_to > x1) & (out_next >= 0) & ~self.link_end_is_end[at] & (self.x_end[np.maximum(out_next, 0)] > x1)
            in_next = self.link_start[at]
            inward = live & (x_to < x0) & (in_next >= 0) & self.link_start_is_end[at] & (self.x_start[np.maximum(in_next, 0)] < x0)
            # A joined end, where the target lies past it: onto the piece it met.
            met_out = live & ~outward & ~inward & (x_to > x1) & (self.met_end[at] >= 0)
            met_in = live & ~outward & ~inward & ~met_out & (x_to < x0) & (self.met_start[at] >= 0)
            step = np.where(outward, out_next, np.where(inward, in_next, np.where(met_out, self.met_end[at], np.where(met_in, self.met_start[at], at))))
            if np.array_equal(step, at):
                break
            # The table holds each start azimuth within one turn, so the piece stepped onto may be a whole turn off
            # the one stepped from at the point they share: the turns keep the chain's azimuth continuous.
            to_next = np.maximum(step, 0)
            turns = (turns + np.where(outward, TWO_PI * np.round((self.phi_end[at] - self.phi_start[to_next]) / TWO_PI), 0.0)
                     + np.where(inward, TWO_PI * np.round((self.phi_start[at] - self.phi_end[to_next]) / TWO_PI), 0.0)
                     + np.where(met_out, self.met_end_turns[at], 0.0) + np.where(met_in, self.met_start_turns[at], 0.0))
            at = step
        x0, x1 = self.x_start[at], self.x_end[at]
        with np.errstate(invalid="ignore", divide="ignore"):
            share = np.where((at < self.count) & np.isfinite(x1) & np.isfinite(x_to) & (x1 > x0), (x_to - x0) / np.where(x1 > x0, x1 - x0, 1.0), 0.0)
        return self.phi_start[at] + share * (self.phi_end[at] - self.phi_start[at]), turns

    def unwrapped(self, slots: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """ψ of each slot's piece at azimuths ``phi`` (broadcast against ``slots``): the azimuth from the piece's
        start in the piece's own sense, **within half a turn of the piece's middle**, ψ ∈ [Δβ/2 − π, Δβ/2 + π) -
        "a piece spans at most 180 degrees of its own extent; a point sees the image of the piece nearest to it".

        Where the two images meet (ψ = Δβ/2 ± π) and the window is open (0 ≤ t ≤ T), |d'| ≥ π/2: with
        t = x s_p + ψ c_p ≤ T = Δβ/c_p, d' = x c_p − ψ s_p ≤ (Δβ − ψ)/s_p ≤ −(π − Δβ/2) at ψ = Δβ/2 + π, and
        from t ≥ 0, d' ≥ −ψ/s_p ≥ π − Δβ/2 at ψ = Δβ/2 − π; Δβ ≤ π. So the piece's value there is under
        e^{−π²/8ς²}."""
        middle = self.middle[slots]
        return middle + np.mod(self.sense[slots] * (phi - self.phi_start[slots]) - middle + math.pi, TWO_PI) - math.pi


# --------------------------------------------------------------------------------------------------------------
# The declarations of the composing stage
# --------------------------------------------------------------------------------------------------------------

DENSITY_CONTRAST = FieldDecl(
    name="pattern_density_contrast", label="Bar and arm density contrast Σ(R, φ)/Σ(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=2.0), meaningful_zero=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the law applied to where the arms are - and 1 everywhere with the
    # randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "The non-axisymmetric factor the star catalogue samples azimuth from: 1 on average around "
        "every ring, so the radial profile and every radial row are unchanged. The arms are a census of arm "
        "pieces: each piece a ridge along its own logarithmic spiral, with its own pitch, a start and an end, "
        "broad across itself as old stellar arms are - about half a disc scale length - flat along itself and "
        "faded to nothing over one width at each end. A few long chains of pieces joined end to end make a "
        "grand design, two of them starting at the bar's two ends; single short pieces make a flocculent "
        "disc; where a template states measured arms, those pieces lie where they were measured. On a ring "
        "every piece that crosses it adds its ridge less the ridge's own mean round the ring, all with one "
        "amplitude, so the ring's mean is 1 exactly and nothing is divided. That amplitude is set by the "
        "arm-number law's budget for the ring - so that the variance the pieces make round the ring equals the "
        "law's arm power on average over the layer's draws, never ring by ring - and is cut where the pieces' "
        "troughs together with the bar's body would reach below nothing, so the field is nowhere negative and "
        "nothing is clipped. Inside the bar's half-length, the bar's body: a boxy, elongated component along "
        "the bar's axis whose surface density falls smoothly to nothing at its edge, its mass taken ring by "
        "ring from the ring's own stars against the checkpoint-1 total disc (no split into stars and gas and "
        "no bulge there: a declared approximation). Each value is the field's exact mean over its cell's "
        "extent in azimuth, on its ring; a census placing a star reads the same function at the star's own "
        "point. A piece is a ridge by the distance across itself, so a nearly circular piece is an arc of its "
        "own length at its own radius, and the rings a little inside and outside it hold its flanks. Where a "
        "drawn piece meets another chain it ends there, joined to it and not faded; no two chains cross. "
        "A composed field: with the randomness layer off it is 1 everywhere - the budget, the pitch, the width "
        "and the body's mass are still published, and nothing says where the arms are."
    ),
)


def _radial(name: str, label: str, unit: str, neutral: float, about: str, hi: float | None = None) -> FieldDecl:
    return FieldDecl(
        name=name, label=label, unit=unit, kind=Kind.FIELD, axes=("R",), ramp=Ramp("magma", lo=0.0, hi=hi),
        meaningful_zero=True, provenance="seeded", composed=True, neutral=neutral, about=about,
    )


ARM_PIECE_AMPLITUDE = _radial(
    "arm_piece_amplitude", "Amplitude of the arm pieces crossing a ring", "dimensionless", 0.0,
    "The one amplitude of the arm pieces on each ring, as the ring's budget of arm power sets it and before any "
    "cut: the height of a piece's ridge above nothing, in units of the ring's mean density. It is the root of "
    "the budget over the count the budget is divided among times the variance one piece of unit height makes "
    "round the ring at the disc's own pitch - so that as many pieces as the count, at independent places "
    "round the ring, make the budget's variance on average. The count is the chains that cross the ring, "
    "each weighed by how far along it the ring stands from its faded end - a chain just begun counts for "
    "little, and never under one in all on a ring any chain crosses, so a lone chain just born or just ending "
    "spends no more than one piece's share of the budget and its excess fades with its own weight - so the "
    "amplitude changes smoothly with radius but where two chains join. Shown here on "
    "the grid's rings; a reader of the arms makes it at its own radius from the budget, the count and the "
    "width, each taken linearly between the grid's radii. It grows without bound toward the centre, where a "
    "piece is wider than its ring and makes almost no variance at any height - a ridge that fills its ring "
    "is no arm, and the arms there carry next to none of the budget whatever this number reads. 0 where the "
    "ring has no budget, where no amplitude could spend it, and - a composed field - everywhere with the "
    "randomness layer off, when no arm is placed.",
)
ARM_PIECE_SATURATION = _radial(
    "arm_piece_saturation", "Cut of the arm pieces' amplitude on a ring", "dimensionless", 1.0,
    "The factor the pieces' amplitude is cut by on each ring so that the density stays non-negative: 1 where "
    "the troughs of the pieces crossing the ring, each as deep under the ring's mean as the piece's own mean "
    "excess, together with the depth of the bar's body leave something of the mean, and under 1 where they "
    "would not - the room the body leaves over the pieces' summed depths at the budget's amplitude. It depends "
    "on which pieces cross the ring and how wide each lies on it, never on a realised power; the field is kept "
    "non-negative by this cut alone, at every point, and nothing is clipped. Shown here on the grid's rings; a "
    "point between two rings takes the cut of its own radius. A ring where it is under 1 carries less arm "
    "power than its budget, and such rings are counted. 1 with the randomness layer off.",
    hi=1.0,
)
ARM_CHAIN_COUNT = FieldDecl(
    name="arm_chain_count", label="Chains of arm pieces crossing a ring", unit="count", kind=Kind.FIELD, axes=("R",),
    ramp=Ramp("viridis", lo=0.0), meaningful_zero=True, provenance="seeded", composed=True, neutral=0.0,
    about=(
        "How many chains of arm pieces cross each ring in this realisation: the whole number the layer's census "
        "laid there: at least the arm number the law counts wherever the ring has a budget and lies at or "
        "outside a bar's half-length, inside which no chain is born and only a measured arm reaches. A ring with a "
        "budget and no chain carries no arm, and is counted. 0 with the randomness layer off: no arm is placed."
    ),
)
ARM_RING_POWER = _radial(
    "arm_ring_power", "Realised arm power on a ring", "dimensionless", 0.0,
    "The variance round each ring of the arm pieces' part of the density contrast, as realised: what the "
    "pieces crossing the ring actually make, to be read beside the ring's budget of arm power. The two agree "
    "on average over the layer's draws where the pieces are as the budget assumes - the law's count of them, "
    "each at the disc's pitch and at full height - and differ ring by ring: more where more chains cross than "
    "the law counts or two pieces overlap, less at a piece's faded ends, where a piece lies nearly along its "
    "ring, and where the amplitude was cut. It is never used to rescale the field. 0 with the randomness layer "
    "off.",
)


def _mode_power(m: int) -> FieldDecl:
    return _radial(
        f"arm_mode_power_{m}", f"Realised {m}-fold power of the arms", "dimensionless", 0.0,
        f"The square of the {m}-fold Fourier amplitude, round each ring, of the arm pieces' part of the density "
        f"contrast as realised - to be read beside the square of the law's amplitude for {m} arms. A disclosed "
        "check of how the pieces split a ring's power among the arm numbers, read and never tuned: the law sets "
        "a ring's whole budget and how many pieces cross it, not this number. 0 with the randomness layer off.",
    )


ARM_MODE_POWERS: tuple[FieldDecl, ...] = tuple(_mode_power(m) for m in ARM_MODES)
# The composing stage's fields, and - since the fourth pass (the gate's fourth follow-up, C) - the disclosed
# check's, published by a stage of their own so that a run that does not ask for them does not pay for them.
COMPOSED: tuple[FieldDecl, ...] = (DENSITY_CONTRAST, ARM_PIECE_AMPLITUDE, ARM_PIECE_SATURATION, ARM_CHAIN_COUNT)
RING_POWER: tuple[FieldDecl, ...] = (ARM_RING_POWER, *ARM_MODE_POWERS)


# --------------------------------------------------------------------------------------------------------------
# The pattern
# --------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class Laid:
    """What the arms are made of at each of a batch of radii (n,): the ring's numbers and the pieces within reach.
    ``slots`` (n, S) are indices into the census's padded arrays (the pad's where fewer are in reach), in the
    table's order - so the slots of one chain's pieces are contiguous, **a run**; ``x`` (n, S) is ln(R/R_s) per
    slot. ``first`` and ``last`` (n, S) mark a run's first and last slot; ``lead`` marks the slot of the run's
    piece nearest the ring (the one whose locus crosses it, else the one whose end is nearest in ln R), whose
    pitch the chain's forcing takes on the ring; ``mean`` (n, S) holds **the chain's** exact mean round the ring
    at the run's last slot and 0 elsewhere."""

    R: np.ndarray
    width: np.ndarray      # FWHM across a piece, kpc: the bounded law's
    count: np.ndarray      # N: the sum of the crossing chains' taper weights
    amplitude: np.ndarray  # B: the budget's amplitude
    effective: np.ndarray  # a: B, cut where the pieces' means would leave less than nothing of the ring's mean
    inv: np.ndarray        # 1/(√2 ς), ς = σ/R
    taper: np.ndarray      # one width in the plane's unit, w/R
    slots: np.ndarray
    live: np.ndarray
    x: np.ndarray
    mean: np.ndarray
    first: np.ndarray
    last: np.ndarray
    lead: np.ndarray


@dataclass(frozen=True, slots=True, eq=False)
class ArmPattern:
    """The stellar pattern of arm pieces and the bar's body: everything the density contrast needs, read from
    published fields in one place (rule A9).

    c(R, φ) = 1 − β(R) + Σ_bar(R, φ)/Σ(R) + a(R) Σ_j (E_j(R, φ) − ⟨E_j⟩(R)) - the module's docstring has each term.

    **Evaluable at a point** (BUILD_III section 1c rule 5, D60): a piece's Gaussian across and its window along
    are closed forms of the point's position; its mean round the ring is a closed form of the point's radius;
    the budget and the width law are the published radial fields read linearly in R between the grid radii (held
    at the end values beyond them); the count, the bounded width, the amplitude and its cut are made at the
    point's own radius. **The bar's body** is :class:`~galaxy.stages.pattern.BarBody` at the normalisation the
    published ``bar_mass_share`` states, read as it has been since S58.

    **No bar** (D217 item 3): a bar amplitude and a half-length that are both NaN are an unbarred galaxy - no
    body, no taper - and not an unresolved pattern.

    Built through ``galaxy.layer.compose`` (the one reader of the layer's switch) and by tests.
    """

    R: np.ndarray            # the grid radii the law is published at
    budget: np.ndarray       # (R,): the published arm_power_budget, ½ Σ A_m²: the taper and the saturation in it
    design: np.ndarray       # (R,): the published arm_design_count, the law's arm number (0 where no arm power)
    width: np.ndarray        # (R,): the published arm_piece_width, FWHM across a piece, kpc
    pieces: Pieces           # the census, from the published table
    bar: float               # the published bar_contrast: NaN for an unbarred galaxy
    pitch_deg: float
    bar_length: float        # a, kpc: NaN for an unbarred galaxy
    axis_ratio: float = float("nan")    # q, the body's
    boxiness: float = float("nan")      # c
    index: float = float("nan")         # n, the profile's exponent
    share: float = float("nan")         # the published bar_mass_share: the body's normalisation, as a mass share
    surface_density: np.ndarray | None = None  # (R,): checkpoint 1's total disc Σ, M☉/pc², which the share is of
    flat: bool = field(init=False)
    barred: bool = field(init=False)
    body: BarBody | None = field(init=False, repr=False)
    normalisation: float = field(init=False)  # N, M☉/pc²: the body's surface density is N · body.unit
    _deviation: np.ndarray | None = field(init=False, repr=False)  # (R, CELLS): the body's contrast less 1
    _untapered: np.ndarray = field(init=False, repr=False)  # (R,): the budget with the bar's taper taken back out
    _depth: np.ndarray = field(init=False, repr=False)      # (R,): the body's depth under each grid ring's mean, made once
    _laid: dict = field(default_factory=dict, init=False, repr=False)  # :meth:`laid` by the radii asked (S60, the cost)

    def __post_init__(self) -> None:
        for name in ("R", "budget", "design", "width"):
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float))
        if self.budget.shape != self.R.shape or self.design.shape != self.R.shape or self.width.shape != self.R.shape:
            raise ValueError(
                f"a pattern holds the arms' budget, the law's arm number and the pieces' width on its {self.R.size} "
                f"radii; got {self.budget.shape}, {self.design.shape} and {self.width.shape}"
            )
        # The bar. Both of its numbers NaN: an unbarred galaxy (D217 item 3), which is a pattern like any other.
        # Both finite: a bar, whose body needs its shape, its share and the disc it is a share of. Anything else
        # - one of the two missing, a body that cannot be built - is a pattern the grid could not resolve.
        unbarred = math.isnan(self.bar) and math.isnan(self.bar_length)
        barred = math.isfinite(self.bar) and math.isfinite(self.bar_length)
        body: BarBody | None = None
        normalisation, deviation_ = 0.0, None
        resolved = unbarred
        if barred:
            shape = (self.axis_ratio, self.boxiness, self.index, self.share)
            if all(math.isfinite(v) for v in shape) and self.surface_density is not None and self.share >= 0.0:
                body = BarBody(self.R, self.surface_density, self.bar_length, self.axis_ratio, self.boxiness, self.index)
                normalisation = body.normalisation(self.share)
                resolved = True
                if normalisation > 0.0:
                    deviation_ = body.deviation(normalisation)
                    deviation_.setflags(write=False)
        object.__setattr__(self, "barred", barred and resolved)
        object.__setattr__(self, "body", body)
        object.__setattr__(self, "normalisation", normalisation)
        object.__setattr__(self, "_deviation", deviation_)
        depth_ = np.zeros(self.R.size) if body is None else np.array(body.depth(normalisation), dtype=float)
        depth_.setflags(write=False)
        object.__setattr__(self, "_depth", depth_)
        # No perturbation to apply: no arm amplitude or no piece, and no body; or a pattern the grid could not
        # resolve (a mesh too coarse for the shear gives a NaN pitch), which stays axisymmetric. Decided once: the
        # censuses ask per cell.
        finite = (resolved and math.isfinite(self.pitch_deg) and bool(np.all(np.isfinite(self.budget)))
                  and bool(np.all(np.isfinite(self.design))) and bool(np.all(np.isfinite(self.width))))
        if finite and deviation_ is not None and not math.isfinite(bar_terms(self.R, self.pitch_deg, self.bar_length)[2]):
            finite = False  # a body with no angle to lie along
        # The budget with the bar's taper taken back out: what is read between two rings, so that the taper - the
        # one steep factor in it - is the point's own (the gas pattern has always taken it so). 0 where the taper
        # is whole.
        taper = bar_terms(self.R, self.pitch_deg if finite else 45.0, self.bar_length)[0] if self.R.size else np.zeros(0)
        with np.errstate(divide="ignore", invalid="ignore"):
            untapered = np.array(np.where(taper < 1.0, self.budget / np.where(taper < 1.0, (1.0 - taper) ** 2, 1.0), 0.0), dtype=float)
        untapered.setflags(write=False)
        object.__setattr__(self, "_untapered", untapered)
        object.__setattr__(self, "flat", not finite or (not (self.budget.any() and self.pieces.count) and deviation_ is None))

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], R: np.ndarray) -> "ArmPattern | None":
        """The pattern of a run's published fields on the run's grid radii ``R``, or None where the fields
        hold no pattern. It reads the pieces, their width, the ring's budget and the law's arm number; neither
        ``arm_multiplicity`` nor a mode's amplitude is among what it reads (D215, D219)."""
        if any(n not in fields for n in PATTERN_READS):
            return None
        pitch = float(fields["pitch_angle"])
        turn = -rotation_sense(pitch) if math.isfinite(pitch) else 1.0
        return cls(
            R, np.asarray(fields["arm_power_budget"], dtype=float), np.asarray(fields["arm_design_count"], dtype=float),
            np.asarray(fields["arm_piece_width"], dtype=float), Pieces.from_fields(fields, turn),
            float(fields["bar_contrast"]), pitch, float(fields["bar_half_length"]),
            float(fields["bar_axis_ratio"]), float(fields["bar_boxiness"]), float(fields["bar_profile_index"]),
            float(fields["bar_mass_share"]), np.asarray(fields["disc_surface_density"], dtype=float),
        )

    # --- the bar's body ---------------------------------------------------------------------------------

    @property
    def bar_angle(self) -> float:
        """The bar's position angle, rad: the disc's winding phase at the bar's end. NaN for an unbarred galaxy."""
        return bar_terms(self.R, self.pitch_deg, self.bar_length)[2]

    @property
    def ring_share(self) -> np.ndarray:
        """β on the grid rings: the body's share of each ring's stars; 0 where there is no body."""
        return np.zeros(self.R.size) if self.body is None else self.body.ring_share(self.normalisation)

    @property
    def depth(self) -> np.ndarray:
        """b on the grid rings: 1 − min_φ of the body's contrast, what the saturation reads; 0 with no body.
        (Made once with the pattern: every point's cut reads it.)"""
        return self._depth

    def depth_at(self, R: np.ndarray) -> np.ndarray:
        """b at any radius: the two neighbouring grid rings' depths blended as :meth:`body_at` blends the rings'
        profiles - a bound on how far the blended body lies under the mean there (the least of a blend is not
        under the blend of the leasts)."""
        if self.body is None:
            return np.zeros(np.shape(R))
        lower, upper, share = ring_bracket(self.R, np.asarray(R, dtype=float))
        b = self.depth
        return (1.0 - share) * b[lower] + share * b[upper]

    def body_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray | float:
        """The body's contrast less 1 at points, ``R`` and ``phi`` broadcast against each other: each point
        reads its two neighbouring grid rings at its own φ − φ_bar - ``gas_response.interpolate``'s arithmetic
        on the two cells it lies between - and blends them linearly in R. 0.0 where there is no body."""
        deviation_ = self._deviation
        if deviation_ is None:
            return 0.0
        R, psi = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(phi, dtype=float) - self.bar_angle)
        lower, upper, share = ring_bracket(self.R, R)
        below, above, weight, _ = _cells.bracket(psi, CELLS)

        def read(ring: np.ndarray) -> np.ndarray:
            first, second = deviation_[ring, below], deviation_[ring, above]
            rising = second >= first
            return np.where(rising, first, second) + np.where(rising, weight, 1.0 - weight) * np.abs(second - first)

        return (1.0 - share) * read(lower) + share * read(upper)

    def body_cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray | float:
        """The body's contrast less 1 averaged over each azimuthal cell between ``edges`` at each radius of
        ``R``, shaped (R, cells): the exact mean of :meth:`body_at` over the cell - the two neighbouring
        rings' interpolants integrated piece by piece and blended as a point blends them. 0.0 with no body."""
        deviation_ = self._deviation
        if deviation_ is None:
            return 0.0
        R = np.asarray(R, dtype=float)
        edges = np.asarray(edges, dtype=float)
        angle = self.bar_angle
        lo = np.broadcast_to(edges[None, :-1] - angle, (R.size, edges.size - 1))
        hi = np.broadcast_to(edges[None, 1:] - angle, (R.size, edges.size - 1))
        lower, upper, share = ring_bracket(self.R, R)
        return ((1.0 - share)[:, None] * _cells.sector_mean(deviation_[lower], lo, hi)
                + share[:, None] * _cells.sector_mean(deviation_[upper], lo, hi))

    # --- a ring's numbers: the count, the width, the amplitude ---------------------------------------------

    @property
    def sin_pitch(self) -> float:
        """sin p of the disc's pitch, held inside 1-89 degrees as the bar's angle and the gas's response hold it."""
        return math.sin(math.radians(min(max(self.pitch_deg, 1.0), 89.0)))

    def law_width_at(self, R: np.ndarray) -> np.ndarray:
        """The width law's FWHM across a piece at ``R``, kpc: the published field, linear between the grid radii
        (which is the law itself)."""
        return np.interp(np.asarray(R, dtype=float), self.R, self.width)

    def ring_state(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(the width, the count) at each radius of ``R`` (n,): the bounded FWHM across a piece, kpc, and N, the
        sum over the chains whose locus crosses the ring of their taper weights.

        **One equation for the two** (the first follow-up's item 3 and the second's item 3 together). A chain's
        taper weight on a ring is min(1, s_c/w): s_c the distance along the chain, in kpc at the ring's radius,
        from where it crosses the ring to its nearer free end (:attr:`Pieces.before`, :attr:`Pieces.after`;
        infinite where it has none: weight 1), w the width - "free chain ends taper over one width". And
        w = min(the law's, π R sin p / N). So w = min(law, w_g) with w_g the one solution of

            Σ_c min(w_g, s_c) = π R sin p

        (the left side grows with w_g from 0, piece by piece linear, so it is solved exactly on the sorted s_c;
        where the chains' tapers together are shorter than π R sin p there is none and the law's width stands).
        With every crossing chain past its taper it is the first follow-up's π R sin p / n. Both are continuous
        in R wherever the chains crossing are the same chains. A chain that crosses a ring twice - a measured
        arm that kinks back - counts once, at its greater weight."""
        R = np.asarray(R, dtype=float)
        p = self.pieces
        law = self.law_width_at(R)
        slots = p.slots(R)
        live = slots < p.count
        size = slots.shape[1]
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            x = np.log(R)[:, None]
            x0, x1 = p.x_start[slots], p.x_end[slots]
            length = p.length[slots]
            t = np.where(live, (x - x0) / (x1 - x0) * length, 0.0)
            along = np.where(live, np.minimum(t + p.before[slots], length - t + p.after[slots]) * R[:, None], 0.0)
        chain = p.chain_of[slots]
        same = chain[:, :, None] == chain[:, None, :]  # (the pad's NaN is its own chain's to nobody)
        best = np.where(same, along[:, None, :], -np.inf).max(axis=2)
        first = same.argmax(axis=2) == np.arange(size)[None, :]
        s = np.where(live & first, best, 0.0)
        target = math.pi * R * self.sin_pitch
        ordered = np.sort(s, axis=1)
        finite = np.isfinite(ordered)
        running = np.cumsum(np.where(finite, ordered, 0.0), axis=1)
        zero = np.zeros((R.size, 1))
        under = np.concatenate([zero, running[:, :-1]], axis=1)   # the sum of the k least
        least = np.concatenate([zero, ordered[:, :-1]], axis=1)   # the k-th least (0 for k = 0)
        with np.errstate(invalid="ignore", over="ignore"):
            candidate = (target[:, None] - under) / (size - np.arange(size))[None, :]
            holds = np.isfinite(least) & (least <= candidate) & (candidate <= ordered)
        solved = holds.any(axis=1)
        bound = np.where(solved, np.take_along_axis(candidate, holds.argmax(axis=1)[:, None], axis=1)[:, 0], np.inf)
        width = np.minimum(law, bound)
        with np.errstate(divide="ignore", invalid="ignore"):
            weight = np.where(live & first, np.minimum(1.0, s / width[:, None]), 0.0)
        count = sum_slots(np.nan_to_num(weight, nan=0.0))
        # The gate's fourth follow-up, B: "On a ring crossed by any chain the count is N = max(1, sum of the taper
        # weights of the crossing chains), so B <= sqrt(budget/v) on every ring; a lone newborn or ending chain's
        # excess goes to zero linearly in its weight; N is continuous through 1." Where the weights sum under 1
        # the bound is then half the spacing of one piece, pi R sin p, and the weights are read at that width (their
        # sum is no larger there: the width grew); where they sum to 1 or more nothing changes, so N and the width
        # are continuous through 1.
        crossed = (live & first).any(axis=1)
        under = crossed & (count < 1.0)
        if under.any():
            width = np.where(under, np.minimum(law, target), width)
            with np.errstate(divide="ignore", invalid="ignore"):
                weight = np.where(live & first, np.minimum(1.0, s / width[:, None]), 0.0)
            count = np.where(under, np.maximum(1.0, sum_slots(np.nan_to_num(weight, nan=0.0))), count)
        return width, count

    def width_at(self, R: np.ndarray) -> np.ndarray:
        """FWHM across a piece on the ring at ``R``, kpc: **the width law's, bounded by half the ring's crossing
        spacing**, min(law, π R sin p / N(R)) (the gate's first follow-up, item 3). A bound, not a target, and
        never raised: the width law was measured on two-to-four-armed galaxies, where the spacing far exceeds
        the width, and width over arm spacing is measured nowhere; a ridge wider than half its spacing is not a
        crest of the law's arm number but the sum the modes already were - which the split of the first build's
        power by arm number showed. N is the count of :meth:`ring_state`, so the width is continuous in R."""
        R = np.asarray(R, dtype=float)
        return self.ring_state(R.reshape(-1))[0].reshape(R.shape)

    def count_at(self, R: np.ndarray) -> np.ndarray:
        """N at ``R``: the sum over the chains crossing the ring of their taper weights (:meth:`ring_state`) - what
        the ring's budget is divided among."""
        R = np.asarray(R, dtype=float)
        return self.ring_state(R.reshape(-1))[1].reshape(R.shape)

    def spacing_at(self, R: np.ndarray) -> np.ndarray:
        """The crossing spacing on the ring at ``R``, kpc, measured across the arms at the disc's pitch:
        2π R sin p / N. Infinite where nothing crosses."""
        R = np.asarray(R, dtype=float)
        count = self.count_at(R)
        with np.errstate(divide="ignore"):
            return np.where(count > 0.0, TWO_PI * R * self.sin_pitch / np.where(count > 0.0, count, 1.0), np.inf)

    def _budget_at(self, R: np.ndarray) -> np.ndarray:
        """The ring's budget at ``R``: the untapered budget read linearly between the grid radii (held at the end
        values beyond them), the bar's taper put back at the radius itself."""
        taper = bar_terms(R, self.pitch_deg, self.bar_length)[0]
        return np.interp(R, self.R, self._untapered) * (1.0 - taper) ** 2

    def design_dispersion_at(self, R: np.ndarray) -> np.ndarray:
        """σ_d at ``R``, rad: the azimuthal dispersion of the designed piece - the bounded width at the disc's own
        pitch (:func:`design_dispersion`)."""
        R = np.asarray(R, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            return design_dispersion(R, self.width_at(R), self.pitch_deg)

    def laid(self, R: np.ndarray) -> Laid:
        """Everything the arms' sum reads at each radius of ``R`` (n,): the ring's numbers, the pieces within
        reach, their runs by chain, and each chain's exact mean round the ring (the module's docstring).

        **A radius' row is the radius' own** (S60, the cost): a radius asked twice in one call is made once and
        its row copied (:func:`numpy.unique`), and a small request - at most :data:`_MEMO_RADII` radii, the grid's
        and the viewer's - is kept by its radii's bytes, the last :data:`_MEMO_KEPT` of them, so that the published
        field, the ring power, the gas's forcing and the saturation read one decomposition of the grid, not four.
        The arrays of a kept ``Laid`` are shared between callers and are read, never written."""
        R = np.asarray(R, dtype=float)
        key = R.tobytes() if R.ndim == 1 and R.size <= _MEMO_RADII else None
        if key is not None:
            held = self._laid.get(key)
            if held is not None:
                return held
        if R.ndim == 1 and R.size > 1 and not np.isnan(R).any():
            distinct, inverse = np.unique(R, return_inverse=True)
            if distinct.size < R.size:
                made = self._laid_distinct(distinct)
                out = Laid(*(getattr(made, f.name)[inverse] for f in fields(Laid)))
            else:
                out = self._laid_distinct(R)
        else:
            out = self._laid_distinct(R)
        if key is not None:
            while len(self._laid) >= _MEMO_KEPT:
                del self._laid[next(iter(self._laid))]
            self._laid[key] = out
        return out

    def _laid_distinct(self, R: np.ndarray) -> Laid:
        """:meth:`laid` made: every row computed, nothing looked up."""
        p = self.pieces
        n, census = R.size, p.count
        if not self.R.size or not census:
            none = np.zeros(n)
            empty = np.zeros((n, 1), dtype=bool)
            return Laid(R, self.law_width_at(R) if self.R.size else none, none, none, none, np.ones(n), np.ones(n),
                        np.full((n, 1), census, dtype=np.int64), empty, np.zeros((n, 1)), np.zeros((n, 1)), empty, empty, empty)
        width, count = self.ring_state(R)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            sigma_design = design_dispersion(R, width, self.pitch_deg)
            amplitude = budget_amplitude(self._budget_at(R), count, np.nan_to_num(sigma_design, nan=np.inf, posinf=np.inf))
            x = np.log(R)
            sigma = width / FWHM_PER_SIGMA / R  # ς: the dispersion across, in the plane's unit
            # Which pieces are within reach: a piece's nearest point to a ring it does not cross is its nearer
            # end, at the distance in ln R past that end (the module's docstring).
            from_start = x[:, None] - p.x_start[None, :census]
            past = np.maximum(np.maximum(from_start - (p.x_end - p.x_start)[None, :census], -from_start), 0.0)
            # (A ring with no amplitude - no budget, no count - holds no arm whatever is near it: nothing is read.)
            reach = (past <= REACH * sigma[:, None]) & ((R > 0.0) & (amplitude > 0.0))[:, None] & (p.extent > 0.0)[None, :]
        rows, columns = np.nonzero(reach)
        held = reach.sum(axis=1)
        slots = np.full((n, max(int(held.max(initial=0)), 1)), census, dtype=np.int64)
        slots[rows, np.arange(rows.size) - (np.cumsum(held) - held)[rows]] = columns
        live = slots < census
        ok = (R > 0.0) & np.isfinite(sigma) & (sigma > 0.0)
        inv = np.where(ok, 1.0 / (math.sqrt(2.0) * np.where(ok, sigma, 1.0)), 1.0)
        taper = np.where(ok, width / np.where(ok, R, 1.0), 1.0)
        relative = np.where(live, np.where(ok, x, 0.0)[:, None] - p.x_start[slots], 0.0)
        # The runs: the slots of one chain are contiguous (the table's order is by chain). The run's lead is the
        # piece whose locus crosses the ring, else the one whose end is nearest in ln R, the earlier of equals.
        chain = p.chain_of[slots]
        same = np.zeros(slots.shape, dtype=bool)
        same[:, 1:] = live[:, 1:] & live[:, :-1] & (chain[:, 1:] == chain[:, :-1])
        first = live & ~same
        last = np.zeros(slots.shape, dtype=bool)
        last[:, :-1] = live[:, :-1] & ~same[:, 1:]
        last[:, -1] = live[:, -1]
        crossing = live & (relative >= 0.0) & (relative < (p.x_end - p.x_start)[slots])
        nearness = np.full(slots.shape, np.inf)
        nearness[live] = np.where(crossing[live], -1.0, past[np.nonzero(live)[0], slots[live]])
        lead = run_argmin(nearness, first, last)
        mean = np.zeros(slots.shape)
        if live.any():
            mean[last] = self._chain_means(Laid(R, width, count, amplitude, amplitude, inv, taper, slots, live, relative, mean, first, last, lead))
        room = 1.0 - self.depth_at(R)
        deep = sum_slots(mean)
        with np.errstate(over="ignore", invalid="ignore"):
            cut = amplitude * deep > room
            effective = np.where(cut, room / np.where(cut, deep, 1.0) * CUT_IN_DOUBLES, amplitude)
        return Laid(R, width, count, amplitude, effective, inv, taper, slots, live, relative, mean, first, last, lead)

    # --- a chain at a point: the Gaussian of the distance to its polyline -------------------------------

    def _candidate(self, laid: Laid, k: int, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(the rows live in slot ``k``, the squared distance in the plane's unit, the chain's taper there) from
        the points ``phi`` (n, m) of each of those radii to **the piece** in slot ``k``, as a segment of its
        chain's polyline: the perpendicular distance where the point's foot falls inside the piece, the distance
        to the nearer end otherwise - each end seen at its nearest image, the piece at the image within half a
        turn of its middle - and the taper read at the arc length along the chain to that nearest point. The two
        arrays are (rows, m): only the live rows are made (S60, the cost; an empty slot is infinitely far and
        weighs nothing, which :meth:`_chains` holds without computing it)."""
        p = self.pieces
        m = phi.shape[1]
        rows = np.flatnonzero(laid.live[:, k])
        if not rows.size:
            return rows, np.zeros((0, m)), np.zeros((0, m))
        slot = laid.slots[rows, k, None]
        psi = p.unwrapped(slot, phi[rows])
        x = laid.x[rows, k, None]
        sin_abs, cos_abs, length = p.sin_abs[slot], p.cos_abs[slot], p.length[slot]
        before, after, extent = p.before[slot], p.after[slot], (2.0 * p.middle[slot])
        w = laid.taper[rows, None]
        with np.errstate(invalid="ignore", over="ignore"):
            t = x * sin_abs + psi * cos_abs
            across = x * cos_abs - psi * sin_abs
            inside = (t >= 0.0) & (t <= length)
            best = np.where(inside, across * across, np.inf)
            arc = np.where(inside, t, 0.0)
            # The two ends, each at its nearest image: the start at ψ = 0, the end at ψ = Δβ.
            for at_psi, at_t in ((0.0, 0.0), (extent, length)):
                dpsi = psi - at_psi
                dpsi = dpsi - TWO_PI * np.round(dpsi / TWO_PI)
                dx = x - at_t * sin_abs
                d = dx * dx + dpsi * dpsi
                nearer = d < best
                best = np.where(nearer, d, best)
                arc = np.where(nearer, at_t, arc)
            taper = np.minimum(1.0, np.minimum((before + arc) / w, (after + length - arc) / w))
        return rows, best, np.maximum(np.nan_to_num(taper, nan=0.0), 0.0)

    def _chains(self, laid: Laid, phi: np.ndarray) -> Iterator[tuple[int, np.ndarray]]:
        """For each run of ``laid`` (one chain within reach of a radius), the chain's excess E at the azimuths
        ``phi`` (n, m) of each radius: yields ``(k, E)`` with ``k`` the run's last slot, E (n, m) 0 on the rows the
        run is not live on. E = the taper at the foot times the Gaussian of the least squared distance over the
        chain's pieces within reach (:meth:`_candidate`).

        **The gate's third follow-up to D219, item 1, which this defines:** "A chain's excess at a point is the
        Gaussian of the point's distance to the chain's locus - the polyline of its pieces in the log-polar plane:
        the perpendicular distance to the nearest piece where the point's foot falls inside that piece, the
        distance to the nearest piece end otherwise - times the taper along the chain at its free ends; the width
        the bounded law's at the point's R. A kink is rounded on the outside and counted once on the inside; a
        joined end is a round cap of the piece's own width that sinks into the ridge it meets; far from any kink
        it is the third pass's d exactly. A ring's profile, mean, variance and forcing are the same quadrature as
        now; the forcing's pitch for a ring's term is the nearest piece's." Where two chains meet "they add: a
        branch is two arms' material in one place ... the join's local excess is read and recorded, bounded by
        nothing but the ring's saturation. Nothing physical is discontinuous there, so no square edge may remain
        anywhere: asserted by a continuity test across every kink and join on both templates."

        The arc length the taper reads is the arc length to the point's foot on the polyline (the lead's note);
        on the inside of a kink within one width of a free end the foot's arc length differs by piece and so the
        taper may - the continuity test across every kink of both templates found no such jump."""
        # Only the rows live in a slot are compared there, and only the rows whose run ends in a slot take the
        # exponential there (S60, the cost): a row's least distance, its weight and its excess are the row's own,
        # and an empty slot is infinitely far and weighs nothing - the same numbers as comparing every row.
        n, m = phi.shape
        best, weight = np.full((n, m), np.inf), np.zeros((n, m))
        inv2 = laid.inv * laid.inv
        for k in range(laid.slots.shape[1]):
            rows, d2, w = self._candidate(laid, k, phi)
            if rows.size:
                nearer = laid.first[rows, k][:, None] | (d2 < best[rows])
                best[rows] = np.where(nearer, d2, best[rows])
                weight[rows] = np.where(nearer, w, weight[rows])
            ends = np.flatnonzero(laid.last[:, k])
            if ends.size:
                value = np.zeros((n, m))
                with np.errstate(over="ignore", invalid="ignore"):
                    value[ends] = np.nan_to_num(weight[ends] * np.exp(-best[ends] * inv2[ends, None]), nan=0.0, posinf=0.0, neginf=0.0)
                yield k, value

    # --- a chain's exact mean round a ring: the ring cut into stretches on each of which one feature is nearest -----

    def _chain_means(self, laid: Laid, upto: np.ndarray | None = None) -> np.ndarray:
        """The exact integral round the ring of each chain's excess, over 2π - the mean - for every run of ``laid``,
        in the runs' order (row-major over ``laid.last``), shaped (M,); or, with ``upto`` (M, k) azimuths, the
        integral from each run's window start W0 up to each of them, shaped (M, k) (:class:`Stretches`)."""
        rows, ends = np.nonzero(laid.last)
        if upto is None:
            out = np.empty(rows.size)
        else:
            out = np.empty((rows.size, upto.shape[1]))
        # The runs decomposed in groups of one piece count, :data:`_ROWS` at a time (S60, the cost): a run's
        # features are its own pieces', so a group carries no padding for a longer run's slots - the same numbers.
        size = laid.slots.shape[1]
        starts = np.maximum.accumulate(np.where(laid.first, np.arange(size)[None, :], 0), axis=1)[rows, ends]
        length = ends - starts
        for count in np.unique(length):
            of = np.flatnonzero(length == count)
            for part in range(0, of.size, _ROWS):
                pick = of[part : part + _ROWS]
                stretches = self._stretches(laid, rows[pick], ends[pick])
                out[pick] = stretches.whole() / TWO_PI if upto is None else stretches.integral_to(upto[pick])
        return out

    def _stretches(self, laid: Laid, rows: np.ndarray, ends: np.ndarray) -> "Stretches":
        """The decomposition of each run's ring (``rows`` the radii, ``ends`` the runs' last slots) into stretches
        of azimuth on each of which one feature of the chain's polyline is nearest (the module's docstring)."""
        p = self.pieces
        size = laid.slots.shape[1]
        # The run's pieces, padded: slots from the run's first to its last.
        starts = np.maximum.accumulate(np.where(laid.first, np.arange(size)[None, :], 0), axis=1)[rows, ends]
        P = int((ends - starts).max(initial=-1)) + 1
        at = starts[:, None] + np.arange(P)[None, :]
        held = at <= ends[:, None]
        at = np.minimum(at, size - 1)
        pieces = np.where(held, laid.slots[rows[:, None], at], p.count)
        x = np.log(laid.R[rows])
        inv, w = laid.inv[rows], laid.taper[rows]
        # The window: a turn centred on the run's lead piece's locus at the ring (any centre would do).
        lead = pieces[np.arange(rows.size), (laid.lead[rows[:, None], at] & held).argmax(axis=1)]
        x0, x1 = p.x_start[lead], p.x_end[lead]
        with np.errstate(divide="ignore", invalid="ignore"):
            share = np.where(x1 > x0, np.clip((x - x0) / np.where(x1 > x0, x1 - x0, 1.0), 0.0, 1.0), 0.5)
        centre = p.phi_start[lead] + share * (p.phi_end[lead] - p.phi_start[lead])
        w0 = centre - math.pi
        return Stretches.build(p, pieces, held, x, inv, w, w0, REACH / (math.sqrt(2.0) * inv))

    def _batches(self, n: int, per_radius: int) -> Iterator[slice]:
        step = max(1, _BATCH // max(per_radius, 4 * max(self.pieces.count, 1)))
        for start in range(0, n, step):
            yield slice(start, start + step)

    def amplitude_at(self, R: np.ndarray) -> np.ndarray:
        """B at ``R``: the budget's amplitude, **made at the point's own radius** - √(budget / (N v(σ_d))), the
        budget, the count and the bounded width all the radius' own. At a grid radius it is the published
        ``arm_piece_amplitude``."""
        R = np.asarray(R, dtype=float)
        if not self.R.size or not self.pieces.count:
            return np.zeros(R.shape)
        flat = R.reshape(-1)
        width, count = self.ring_state(flat)
        with np.errstate(divide="ignore", invalid="ignore"):
            sigma = design_dispersion(flat, width, self.pitch_deg)
        return budget_amplitude(self._budget_at(flat), count, np.nan_to_num(sigma, nan=np.inf, posinf=np.inf)).reshape(R.shape)

    def effective_amplitude(self, R: np.ndarray) -> np.ndarray:
        """a(R) = min(B, (1 − b)/Σ_j ⟨E_j⟩) at each radius: the budget's amplitude, cut where the pieces' means
        together would leave less than nothing of what the bar's body leaves of the ring's mean."""
        R = np.asarray(R, dtype=float)
        flat = R.reshape(-1)
        out = np.empty(flat.size)
        for part in self._batches(flat.size, 1):
            out[part] = self.laid(flat[part]).effective
        return out.reshape(R.shape)

    def saturation(self, R: np.ndarray) -> np.ndarray:
        """a/B at each radius: the cut of the pieces' amplitude, 1 where it is not cut (and where there is none)."""
        R = np.asarray(R, dtype=float)
        amplitude, effective = self.amplitude_at(R), self.effective_amplitude(R)
        return np.where(amplitude > 0.0, effective / np.where(amplitude > 0.0, amplitude, 1.0), 1.0)

    def _rows(self, radii: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """a Σ_j (E_j − ⟨E_j⟩) at each radius of ``radii`` (n,) and that row's azimuths ``phi`` (n, k)."""
        out = np.zeros(phi.shape)
        if self.flat or not self.pieces.count or not self.budget.any():
            return out
        for part in self._batches(radii.size, phi.shape[1]):
            laid = self.laid(radii[part])
            angles = phi[part]
            total = np.zeros(angles.shape)
            for k, value in self._chains(laid, angles):
                # (The rows whose run ends in slot k alone: elsewhere the term is 0 − 0, and a sum that began at
                # +0 is unchanged by adding +0 - the same bits as adding the whole column.)
                ends = np.flatnonzero(laid.last[:, k])
                total[ends] = total[ends] + (value[ends] - laid.mean[ends, k, None])
            out[part] = laid.effective[:, None] * total
        return out

    def arms_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """a(R) Σ_j (E_j(R, φ) − ⟨E_j⟩(R)) at points, ``R`` and ``phi`` broadcast against each other: the pieces
        alone, with no body and no 1. Its mean round a ring is 0. A point's value is its own radius' and
        azimuth's alone: a column of radii against rows of azimuths only reads each radius' pieces once."""
        R, phi = np.asarray(R, dtype=float), np.asarray(phi, dtype=float)
        shape = np.broadcast_shapes(R.shape, phi.shape)
        rank = len(shape)
        aligned = R.reshape((1,) * (rank - R.ndim) + R.shape)
        if rank >= 1 and aligned.shape[-1] == 1 and shape[-1] > 1:
            radii = np.broadcast_to(aligned, shape[:-1] + (1,)).reshape(-1)
            return self._rows(radii, np.broadcast_to(phi, shape).reshape(radii.size, shape[-1])).reshape(shape)
        return self._rows(np.broadcast_to(R, shape).reshape(-1), np.broadcast_to(phi, shape).reshape(-1, 1)).reshape(shape)

    def arm_cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """The pieces' sum averaged over each azimuthal cell between ``edges`` at each radius of ``R``, shaped
        (R, cells): each piece's integral over the cell by :func:`gauss_linear`'s closed forms - the integral up
        to each edge, whole turns counted, and the cell the difference of two - less the piece's mean round the
        ring by the same forms. Exact, and cells that tile a ring sum to 0 to rounding."""
        R = np.asarray(R, dtype=float)
        edges = np.asarray(edges, dtype=float)
        out = np.zeros((R.size, edges.size - 1))
        if self.flat or not self.pieces.count or not self.budget.any():
            return out
        span = (edges[1:] - edges[:-1])[None, :]
        for part in self._batches(R.size, 32 * edges.size):
            laid = self.laid(R[part])
            at = np.nonzero(laid.last)
            cells = np.zeros((*laid.slots.shape, edges.size - 1))
            if at[0].size:
                upto = self._chain_means(laid, np.broadcast_to(edges[None, :], (at[0].size, edges.size)))
                cells[at] = (upto[:, 1:] - upto[:, :-1]) / span - laid.mean[at][:, None]
            total = np.zeros((laid.R.size, edges.size - 1))
            for k in range(cells.shape[1]):
                total = total + cells[:, k, :]
            out[part] = laid.effective[:, None] * total
        return out

    def ring_profile(self, R: np.ndarray, cells: int = CELLS) -> np.ndarray:
        """The pieces' sum on the centres of ``cells`` equal cells round each ring of ``R``, shaped (R, cells): the
        point function there - "a ring's profile ... on the solver's cells"."""
        R = np.asarray(R, dtype=float)
        return self.arms_at(R[:, None], _cells.cell_centres(cells)[None, :])

    def piece_profiles(self, R: np.ndarray) -> Iterator[tuple[slice, np.ndarray, np.ndarray]]:
        """Each chain's own ridge on the solver's cells' centres, ring by ring, for the gas's forcing: yields
        ``(rows, |sin p| (n, S), a E_c (n, S, CELLS))`` for stretches ``rows`` of ``R`` - the ridge at the stars'
        own amplitude on the ring, the cut in it, its mean not taken out (the forcing's transform drops it), held
        in the last slot of the chain's run with **the pitch of the run's lead piece** - the one whose locus
        crosses the ring, else the one whose end is nearest it - "the forcing's pitch for a ring's term is the
        nearest piece's" (the gate's third follow-up); 0 in every other slot."""
        R = np.asarray(R, dtype=float)
        centres = _cells.cell_centres(CELLS)
        if self.flat or not self.pieces.count or not self.budget.any():
            return
        p = self.pieces
        step = max(1, _BATCH // (4 * CELLS))
        for start in range(0, R.size, step):
            rows = slice(start, start + step)
            laid = self.laid(R[rows])
            angles = np.broadcast_to(centres[None, :], (laid.R.size, CELLS))
            ridges = np.zeros((*laid.slots.shape, CELLS))
            for k, value in self._chains(laid, angles):
                ridges[:, k, :] = value
            sines = np.zeros(laid.slots.shape)
            carried = np.zeros(laid.R.size)
            for k in range(laid.slots.shape[1]):
                carried = np.where(laid.lead[:, k], p.sin_abs[laid.slots[:, k]], carried)
                sines[:, k] = np.where(laid.last[:, k], carried, 0.0)
            yield rows, sines, laid.effective[:, None, None] * ridges

    def ring_power(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(the variance round each ring of the pieces' sum, the squared m-fold cosine amplitude for each of
        :data:`~galaxy.stages.pattern.ARM_MODES` shaped (modes, n)): the realised power **of the ring's profile
        on the solver's cells** - "its ring mean and variance by the same quadrature" - from that profile's
        transform."""
        R = np.asarray(R, dtype=float)
        spectrum = np.fft.rfft(self.ring_profile(R), axis=1) / CELLS
        power = (2.0 * np.abs(spectrum[:, 1:])) ** 2
        power[:, -1] *= 0.5  # the cells' last harmonic, CELLS/2, is a cosine alone: its amplitude is |c|, not 2|c|
        return 0.5 * power.sum(axis=1), np.stack([power[:, m - 1] for m in ARM_MODES])

    # --- the contrast -----------------------------------------------------------------------------------

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ(R, φ)/Σ(R) at the points of an (R, φ) mesh: the point function at each (R_i, φ_j), what a census
        inverts for an azimuth. Its mean round a ring is 1 over the ring itself."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        return self.contrast_at(R[:, None], phi[None, :])

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise (S48: each
        bright star inverts its own row of azimuths inside its own cell)."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        return 1.0 + self.arms_at(R, phi) + self.body_at(R, phi)

    def published(self, R: np.ndarray, phi: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """What the stage publishes on the grid: at each radius of ``R``, the field's exact mean over each cell
        between ``edges`` - each piece's closed-form integral, the body's interpolant piece by piece. A ring's
        cells average to 1 to rounding on any grid, with nothing divided. (``phi``, the cells' centres, is not
        read: until S60 the arm modes were published there.)"""
        R = np.asarray(R, dtype=float)
        return 1.0 + self.arm_cell_means(R, edges) + self.body_cell_means(R, edges)

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` at one radius, exactly: :meth:`published`'s
        arithmetic there. Sectors that tile the ring average to 1 to rounding."""
        radius = np.array([float(R)])
        body = self.body_cell_means(radius, edges)
        return 1.0 + self.arm_cell_means(radius, edges)[0] + (body if isinstance(body, float) else body[0])

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: np.ndarray | float, hi: np.ndarray | float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8).
        ``lo`` and ``hi`` are one sector's, or since S60 one sector a star (stars,) - :func:`sector_grid` - the
        stars of many cells placed in one call, each as its own cell's call placed it (the contrast at a point is
        the point's own)."""
        grid = sector_grid(lo, hi, steps)
        if grid.ndim == 1:
            return invert_azimuths(u, grid, self.contrast(radius, grid))
        return invert_azimuths(u, grid, self.contrast_at(np.asarray(radius, dtype=float)[:, None], grid))


def design_dispersion(R: np.ndarray, width: np.ndarray, pitch_deg: float) -> np.ndarray:
    """σ_d = σ/(R sin p): the azimuthal dispersion of a piece at the disc's own pitch on each ring, rad - what the
    budget's amplitude is set at (D219 item 4: "the width law at the disc's pitch"). The pitch is held inside 1-89
    degrees, as the bar's angle and the gas's response hold it."""
    sin_pitch = math.sin(math.radians(min(max(pitch_deg, 1.0), 89.0)))
    return (np.asarray(width, dtype=float) / FWHM_PER_SIGMA) / (np.asarray(R, dtype=float) * sin_pitch)


def compute_stellar_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    cells = (R.size, ctx.grid.phi.size)
    made: dict[str, np.ndarray] = {}

    def compose(decl: FieldDecl) -> np.ndarray:
        if not made:
            # The law applied to the realisation: the pattern object is compose's, built from the published law
            # and the layer's table. A pattern with nothing to place is the neutral.
            shape = _compose.stellar_pattern(ctx.fields, R)
            if shape is None or shape.flat:
                made.update({d.name: _compose.neutral(d, cells if d is DENSITY_CONTRAST else (R.size,)) for d in COMPOSED})
            else:
                made.update({
                    DENSITY_CONTRAST.name: shape.published(R, ctx.grid.phi, ctx.grid["phi"].edges),
                    ARM_PIECE_AMPLITUDE.name: shape.amplitude_at(R),
                    ARM_PIECE_SATURATION.name: shape.saturation(R),
                    ARM_CHAIN_COUNT.name: shape.pieces.chains_crossing(R).astype(float),
                })
        return made[decl.name]

    return {
        decl.name: _compose.field(ctx.fields, decl, cells if decl is DENSITY_CONTRAST else (R.size,), lambda decl=decl: compose(decl))
        for decl in COMPOSED
    }


def compute_arm_ring_power(ctx: Context) -> Mapping[str, Any]:
    """The disclosed check (D219 item 4): the realised arm power per ring and its split by arm number, from the
    same pattern the composing stage built - the ring's profile on the solver's cells transformed."""
    R = ctx.grid.R
    made: dict[str, np.ndarray] = {}

    def compose(decl: FieldDecl) -> np.ndarray:
        if not made:
            shape = _compose.stellar_pattern(ctx.fields, R)
            if shape is None or shape.flat:
                made.update({d.name: _compose.neutral(d, (R.size,)) for d in RING_POWER})
            else:
                power, by_mode = shape.ring_power(R)
                made.update({ARM_RING_POWER.name: power, **{name: by_mode[k] for k, name in enumerate(MODE_POWER_FIELDS)}})
        return made[decl.name]

    return {decl.name: _compose.field(ctx.fields, decl, (R.size,), lambda decl=decl: compose(decl)) for decl in RING_POWER}


STELLAR_PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="stellar_pattern", slot="stellar_pattern", checkpoint=3,
        about=(
            "The stellar arms and bar as a density contrast: the arm-number law applied to the randomness "
            "layer's census of arm pieces. On every ring the pieces that cross it each add a broad ridge less "
            "its own mean round the ring, all at one amplitude - the one at which the law's count of pieces "
            "would make the ring's budget of arm power on average - cut where their troughs would reach under "
            "what the bar's body leaves of the mean; so every ring keeps its stars, the field is nowhere "
            "negative and nothing is clipped or rescaled by what was realised. It publishes the field as exact "
            "means over the grid's cells, the amplitude and its cut on each ring, and how many chains cross each "
            "ring. It draws nothing: its fields are seeded through the pattern's drawn pitch "
            "and amplitudes and the layer's pieces, and with the layer off they are their neutral values and "
            "no arm is placed (D219)."
        ),
        compute=compute_stellar_pattern,
        requires=PATTERN_READS,
        publishes=COMPOSED,
    )
)

ARM_RING_POWER_STAGE = IMPLEMENTATIONS.register(
    Stage(
        id="arm_ring_power", slot="arm_ring_power", checkpoint=3,
        about=(
            "The disclosed check of the stellar arms, read beside the arm-number law and never used by any "
            "stage: the arm power each ring actually carries - the variance round the ring of the arm pieces' "
            "part of the density contrast, as composed - and its split among two to six arms, the square of "
            "each arm number's Fourier amplitude, to be set beside the law's budget and the square of the "
            "law's amplitude for that arm number. Made from the same composed pattern the stellar pattern "
            "stage built, on the gas solver's cells; a stage of its own so that a run that does not ask for "
            "the check does not pay for it. 0 with the randomness layer off (D219)."
        ),
        compute=compute_arm_ring_power,
        requires=(*PATTERN_READS, DENSITY_CONTRAST.name),
        publishes=RING_POWER,
    )
)
