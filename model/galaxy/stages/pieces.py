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

**The window along it, W** (D219 item 1; the first follow-up's item 1; the second's items 2 and 3). 1 within the
extent 0 ≤ t ≤ T and 0 outside it, **and tapered linearly to zero over one width at a chain's two free ends** -
"the taper is a chain's two ends, over one width each; a chain is continuous through its kinks". So the taper is
the chain's, not the piece's: a point's distance to a free end is taken *along the chain*, through its kinks -
R (t + T_before) to the chain's start and R (T − t + T_after) to its end, T_before and T_after the lengths of the
chain's pieces before and after this one - and W = min(1, that distance over the width at the point's radius),
the lesser of the two ends'. An end of a piece at which another piece of its chain stands has no taper (the
window there is cut square across the piece, at t = 0 or T); **nor has an end joined to another chain** (the
second follow-up, item 2: "a drawn piece that meets another chain ends there, joined, without taper"; the table's
``arm_piece_join`` says which). The taper is a declared placeholder: no taper length is measured (a debt).

**The field** (D219 item 4). c(R, φ) = 1 + [bar's body] + a(R) Σ_j (E_j(R, φ) − ⟨E_j⟩(R)): every piece within
reach of the radius, each less its own mean round the ring there, so **the ring's mean is 1 exactly** at every
radius and nothing is divided. ⟨E_j⟩(R) is the exact integral round the ring (:func:`gauss_linear`: on each
stretch of the window that is linear in the azimuth, a Gaussian times a line - by the error function, or by an
eight-point Gauss rule where the stretch is under half a dispersion's worth of argument, each exact to rounding).
a(R) is the pieces' one amplitude on the ring:

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

**Which pieces a radius reads.** A piece's Gaussian is not cut off: a ring a few widths inside or outside a
nearly circular piece's radius holds its flank. A radius reads every piece whose window comes within
:data:`REACH` dispersions of it - |d'| ≥ (distance in ln R past the piece's nearer end)/c_p wherever the window is
open, so the test is exact - and a piece further off, under e^{−40.5} of its height, is not summed. The pieces
are summed in the table's order, one after another, so a point reads the same bits in any batch.

**On the grid as exact cell means** (rule 5; D216). :meth:`ArmPattern.contrast_at` is the point function. The
published field holds the mean of the same function over each of the grid's φ cells on each ring - each
piece's integral over the cell by the same closed forms as its ring mean, so a ring's cells average to 1 to
rounding on any grid - with the body's exact cell means as before.

**On the solver's cells** (the second follow-up, item 1): a ring's profile of the pieces on the gas solver's
cells' centres is what the gas's forcing is transformed from (``gas_pattern``), and the realised ring variance
and its split by arm number - the **disclosed check** of D219 item 4, published for m = 2 … 6 beside the law's
A_m², read, never tuned - are that profile's, by the same quadrature.

**What is not here.** The bar's body is ``pattern.BarBody``, unchanged. The gas's answer to the pieces is
``gas_pattern``'s, which asks this pattern for each ring's pieces. Nothing here draws: the census is the layer's.
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
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


# --------------------------------------------------------------------------------------------------------------
# The census as read: the table's rows, their chains, and which of them cross a radius
# --------------------------------------------------------------------------------------------------------------


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
                for f in own:
                    if f % n != e % n and abs(ends[f][0] - ends[e][0]) < JOINED and abs(math.remainder(ends[f][1] - ends[e][1], TWO_PI)) < JOINED:
                        partner[e] = f
                        break
        closed = np.concatenate([self.join == JOIN_INNER, self.join == JOIN_OUTER])  # an end that meets another chain
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


def window(t: np.ndarray, length: np.ndarray, before: np.ndarray, after: np.ndarray, taper: np.ndarray) -> np.ndarray:
    """W(t): a piece's window along itself (the module's docstring) - 1 within 0 ≤ t ≤ T and 0 outside, tapered
    linearly over ``taper`` (one width, in the plane's unit: w/R) from the chain's free ends, which lie ``before``
    the piece's start and ``after`` its end along the chain (infinite: no free end that side, no taper)."""
    with np.errstate(invalid="ignore", over="ignore"):
        inside = np.minimum(1.0, np.minimum((t + before) / taper, (length - t + after) / taper))
        return np.where((t >= 0.0) & (t <= length), np.maximum(inside, 0.0), 0.0)


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
    "little - so the amplitude changes smoothly with radius but where two chains join. Shown here on "
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
        "laid there, at least the arm number the law counts wherever the ring has a budget. A ring with a "
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
COMPOSED: tuple[FieldDecl, ...] = (DENSITY_CONTRAST, ARM_PIECE_AMPLITUDE, ARM_PIECE_SATURATION, ARM_CHAIN_COUNT, ARM_RING_POWER, *ARM_MODE_POWERS)


# --------------------------------------------------------------------------------------------------------------
# The pattern
# --------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class Laid:
    """What the arms are made of at each of a batch of radii (n,): the ring's numbers and the pieces within reach.
    ``slots`` (n, S) are indices into the census's padded arrays (the pad's where fewer are in reach), in the
    table's order; ``x`` (n, S) is ln(R/R_s) per slot; ``mean`` (n, S) each piece's exact mean round the ring
    (0 in an empty slot)."""

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
        return width, sum_slots(np.nan_to_num(weight, nan=0.0))

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
        reach, and each one's exact mean round the ring (the module's docstring)."""
        R = np.asarray(R, dtype=float)
        p = self.pieces
        n, census = R.size, p.count
        if not self.R.size or not census:
            none = np.zeros(n)
            return Laid(R, self.law_width_at(R) if self.R.size else none, none, none, none, np.ones(n), np.ones(n),
                        np.full((n, 1), census, dtype=np.int64), np.zeros((n, 1), dtype=bool), np.zeros((n, 1)), np.zeros((n, 1)))
        width, count = self.ring_state(R)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            sigma_design = design_dispersion(R, width, self.pitch_deg)
            amplitude = budget_amplitude(self._budget_at(R), count, np.nan_to_num(sigma_design, nan=np.inf, posinf=np.inf))
            x = np.log(R)
            sigma = width / FWHM_PER_SIGMA / R  # ς: the dispersion across, in the plane's unit
            # Which pieces are within reach: |d'| >= (the distance in ln R past the piece's nearer end)/|cos p|
            # wherever the piece's window is open.
            from_start = x[:, None] - p.x_start[None, :census]
            past = np.maximum(np.maximum(from_start - (p.x_end - p.x_start)[None, :census], -from_start), 0.0)
            # (A ring with no amplitude - no budget, no count - holds no arm whatever is near it: nothing is read.)
            reach = (past <= REACH * sigma[:, None] * p.cos_abs[None, :census]) & ((R > 0.0) & (amplitude > 0.0))[:, None] & (p.extent > 0.0)[None, :]
        rows, columns = np.nonzero(reach)
        held = reach.sum(axis=1)
        slots = np.full((n, max(int(held.max(initial=0)), 1)), census, dtype=np.int64)
        slots[rows, np.arange(rows.size) - (np.cumsum(held) - held)[rows]] = columns
        live = slots < census
        ok = (R > 0.0) & np.isfinite(sigma) & (sigma > 0.0)
        inv = np.where(ok, 1.0 / (math.sqrt(2.0) * np.where(ok, sigma, 1.0)), 1.0)
        taper = np.where(ok, width / np.where(ok, R, 1.0), 1.0)
        relative = np.where(live, np.where(ok, x, 0.0)[:, None] - p.x_start[slots], 0.0)
        mean = np.zeros(slots.shape)
        at = np.nonzero(live)
        mean[at] = self._integral(slots[at], relative[at], inv[at[0]], taper[at[0]], None) / TWO_PI
        room = 1.0 - self.depth_at(R)
        deep = sum_slots(mean)
        with np.errstate(over="ignore", invalid="ignore"):
            cut = amplitude * deep > room
            effective = np.where(cut, room / np.where(cut, deep, 1.0) * CUT_IN_DOUBLES, amplitude)
        return Laid(R, width, count, amplitude, effective, inv, taper, slots, live, relative, mean)

    def _integral(self, slots: np.ndarray, x: np.ndarray, inv: np.ndarray, taper: np.ndarray, upto: np.ndarray | None) -> np.ndarray:
        """∫ E_j dψ from the piece's image's lower end, ψ = Δβ/2 − π, up to ψ = ``upto`` (m, k) - or, with None,
        over the whole turn, shaped (m,) - for each of m (radius, piece) pairs: ``slots`` the pieces, ``x``
        ln(R/R_s), ``inv`` and ``taper`` the radius' 1/(√2 ς) and w/R. Exact: W is linear in ψ on three stretches
        - up to where the rise from the chain's start is over (or meets the fall), the flat part, the fall to the
        chain's end - and each is :func:`gauss_linear`'s."""
        p = self.pieces
        whole = upto is None
        sin_abs, cos_abs = p.sin_abs[slots][:, None], p.cos_abs[slots][:, None]
        length, before, after = p.length[slots][:, None], p.before[slots][:, None], p.after[slots][:, None]
        low = (p.middle[slots] - math.pi)[:, None]
        high = low + TWO_PI
        x, width, inverse = x[:, None], taper[:, None], inv[:, None]
        top = high if whole else np.minimum(upto, high)
        with np.errstate(invalid="ignore", over="ignore", divide="ignore"):
            rise_ends, fall_starts = width - before, length + after - width
            meet = 0.5 * (length + after - before)
            flat = rise_ends <= fall_starts
            knots = (np.zeros(length.shape), np.clip(np.where(flat, rise_ends, meet), 0.0, length),
                     np.clip(np.where(flat, fall_starts, meet), 0.0, length), length)
            heights = [window(t, length, before, after, width) for t in knots]
            angles = [(t - x * sin_abs) / cos_abs for t in knots]
            total = np.zeros(top.shape)
            for k in range(3):
                span = angles[k + 1] - angles[k]
                has = span > 0.0
                slope = np.where(has, (heights[k + 1] - heights[k]) / np.where(has, span, 1.0), 0.0)
                lo, hi = np.clip(angles[k], low, top), np.clip(angles[k + 1], low, top)
                total = total + gauss_linear(lo, hi, heights[k] + slope * (lo - angles[k]), slope, x * cos_abs, sin_abs, inverse)
        return total[:, 0] if whole else total

    def _piece(self, laid: Laid, k: int, phi: np.ndarray) -> np.ndarray:
        """E of the pieces in slot ``k`` of each radius of ``laid`` at that row's azimuths ``phi`` (n, m): the
        window along times the Gaussian across; 0 in an empty slot (whose row is not computed)."""
        p = self.pieces
        out = np.zeros(phi.shape)
        rows = np.flatnonzero(laid.live[:, k])
        if rows.size:
            slot = laid.slots[rows, k, None]
            psi = p.unwrapped(slot, phi[rows])
            x = laid.x[rows, k, None]
            sin_abs, cos_abs = p.sin_abs[slot], p.cos_abs[slot]
            across = (x * cos_abs - psi * sin_abs) * laid.inv[rows, None]
            along = window(x * sin_abs + psi * cos_abs, p.length[slot], p.before[slot], p.after[slot], laid.taper[rows, None])
            out[rows] = along * np.exp(-across * across)
        return out

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
            for k in range(laid.slots.shape[1]):
                total = total + (self._piece(laid, k, angles) - laid.mean[:, k, None])
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
        p = self.pieces
        span = (edges[1:] - edges[:-1])[None, :]
        for part in self._batches(R.size, 32 * edges.size):
            laid = self.laid(R[part])
            at = np.nonzero(laid.live)
            slot = laid.slots[at]
            middle, mean, sense = p.middle[slot][:, None], laid.mean[at][:, None], p.sense[slot][:, None]
            turns, within = np.divmod(sense * (edges[None, :] - p.phi_start[slot][:, None]) - middle + math.pi, TWO_PI)
            upto = turns * (TWO_PI * mean) + self._integral(slot, laid.x[at], laid.inv[at[0]], laid.taper[at[0]], middle - math.pi + within)
            cells = np.zeros((*laid.slots.shape, edges.size - 1))
            cells[at] = sense * (upto[:, 1:] - upto[:, :-1]) / span - mean
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
        """Each piece's own ridge on the solver's cells' centres, ring by ring, for the gas's forcing: yields
        ``(rows, |sin p_j| (n, S), a E_j (n, S, CELLS))`` for stretches ``rows`` of ``R`` - the ridge at the
        stars' own amplitude on the ring, the cut in it, its mean not taken out (the forcing's transform drops
        it); 0 in an empty slot."""
        R = np.asarray(R, dtype=float)
        centres = _cells.cell_centres(CELLS)
        if self.flat or not self.pieces.count or not self.budget.any():
            return
        step = max(1, _BATCH // (4 * CELLS))
        for start in range(0, R.size, step):
            rows = slice(start, start + step)
            laid = self.laid(R[rows])
            angles = np.broadcast_to(centres[None, :], (laid.R.size, CELLS))
            ridges = np.stack([self._piece(laid, k, angles) for k in range(laid.slots.shape[1])], axis=1)
            yield rows, self.pieces.sin_abs[laid.slots], laid.effective[:, None, None] * ridges

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

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8)."""
        grid = np.linspace(lo, hi, steps + 1)
        return invert_azimuths(u, grid, self.contrast(radius, grid))


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
                power, by_mode = shape.ring_power(R)
                made.update({
                    DENSITY_CONTRAST.name: shape.published(R, ctx.grid.phi, ctx.grid["phi"].edges),
                    ARM_PIECE_AMPLITUDE.name: shape.amplitude_at(R),
                    ARM_PIECE_SATURATION.name: shape.saturation(R),
                    ARM_CHAIN_COUNT.name: shape.pieces.chains_crossing(R).astype(float),
                    ARM_RING_POWER.name: power,
                    **{name: by_mode[k] for k, name in enumerate(MODE_POWER_FIELDS)},
                })
        return made[decl.name]

    return {
        decl.name: _compose.field(ctx.fields, decl, cells if decl is DENSITY_CONTRAST else (R.size,), lambda decl=decl: compose(decl))
        for decl in COMPOSED
    }


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
            "means over the grid's cells, the amplitude and its cut on each ring, how many chains cross each "
            "ring, and - to be read beside the law - the arm power each ring actually carries and its split "
            "among two to six arms. It draws nothing: its fields are seeded through the pattern's drawn pitch "
            "and amplitudes and the layer's pieces, and with the layer off they are their neutral values and "
            "no arm is placed (D219)."
        ),
        compute=compute_stellar_pattern,
        requires=PATTERN_READS,
        publishes=COMPOSED,
    )
)
