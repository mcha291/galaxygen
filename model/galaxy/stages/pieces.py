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
  where its inner end stands, its pitch, how far round the disc it runs, the chain it belongs to.
- **The composed field** is made here, by :class:`ArmPattern`: the pieces' sum, exact at any point.

**A piece** (D219 item 1) is a ridge on its own logarithmic locus: from its start (R_s, φ_s) it runs outward
to R_s exp(Δβ |tan p|), its azimuth advancing by Δβ in the trailing sense where p > 0 and the other way where
p < 0 (a reversed piece, as measured arms have) - linear in ln R between its two ends, so no cotangent is
taken and a piece of nearly no pitch is a short radial step that carries its whole Δβ of azimuth. Across it the
profile is a Gaussian of full width at half maximum FWHM(R), the published width law. **On a ring** a piece of
pitch p is so a Gaussian in azimuth of dispersion σ_φ = σ / (R |sin p|), σ = FWHM / (2 √(2 ln 2)) - the
ruling's own arithmetic - **made periodic**: the wrapped normal Σ_k exp(−(δ + 2πk)² / 2σ_φ²), which is the
Gaussian wherever the piece is narrower than its ring and the only form that is a function on the ring where
it is not (a nearly circular piece, or any piece near the centre, is wider than its ring: it then spreads
round the whole ring and adds no contrast). Its mean round the ring is σ_φ/√(2π) exactly and its Fourier
amplitudes are c_m = (2σ_φ/√(2π)) e^{−m²σ_φ²/2}, so every statement below is exact. Along it the piece is
flat, **tapered linearly to zero over one width at each end** - a declared placeholder, no taper length being
measured (a debt): τ = min(1, s/w(R_s), (L − s)/w(R_e)), s the arc length from the start, read where the locus
crosses the ring. The taper is each piece's own, as ruled: where two pieces of a chain join, both are at zero.

**The field** (item 4). c(R, φ) = 1 + [bar's body] + a(R) Σ_j τ_j(R) (W(φ − φ_j(R); σ_φ,j(R)) − σ_φ,j/√(2π)):
the pieces crossing the radius, each less its own mean round the ring, so **the ring's mean is 1 exactly** at
every radius and nothing is divided. a(R) is the pieces' one amplitude on the ring:

- *The budget, in expectation.* B(R) = √(budget / (N v)), v = Σ_m c_m(σ_d)²/2 the variance round the ring of
  one piece of unit amplitude at the disc's own pitch, σ_d = σ/(R sin p), and N the count the budget is divided
  among: the law's n(R), or - in a galaxy with pinned pieces - the number of chains crossing the ring (the
  lead's reading (b) of the ruling). For N pieces at independent uniform azimuths the expected variance is
  N v B², so the expectation equals the budget by construction; the realised variance is published beside it
  and is never divided by. For a narrow piece v is the ruling's σ_φ/(2√π) − σ_φ²/(2π); the exact periodic form
  is used because that expression turns negative past σ_φ = √π, which the inner rings of every disc reach.
  Where a designed piece is so much wider than its ring that v is under the smallest normal double, no
  amplitude spends the budget: B = 0, and the ring is counted.
- *Positivity by the saturation alone.* The pieces' sum is nowhere under −a Σ_j τ_j d_j, d_j = σ_φ,j/√(2π) −
  W(π; σ_φ,j) the depth of a piece's own trough under its mean (its mean itself, σ_φ,j/√(2π), for a piece
  narrower than its ring: the ruling's "the arms' mean excess ≤ 1 − b"). So a = min(B, (1 − b(R)) / Σ_j τ_j d_j),
  b the depth of the bar's body under the ring's mean: the field is non-negative at every point, **the cut is
  taken at the point's own radius**, nothing is clipped, floored or renormalised, and the cut is published on
  the grid's rings and counted.

Between the grid's rings the budget (with the bar's taper taken back out, and put back at the point's own
radius), the count and the width are read linearly - the width law is linear in R, so that is the law itself -
and B is made from them at the point's own radius. B itself is not read between rings: toward the centre it
grows as e^{σ_d²/2}, and a line between two rings' values would be neither ring's law. On the grid's rings it
is published (``arm_piece_amplitude``).

**Exact at a point, and on the grid as exact cell means** (rule 5; D216). :meth:`ArmPattern.contrast_at` is the
point function. The published field holds the mean of the same function over each of the grid's φ cells on
each ring - the Fourier series integrated term by term, 128 harmonics, more than any piece the width law
allows needs (σ_φ ≥ 0.082 at any radius and pitch) - with the body's exact cell means as before, so a ring's
cells average to 1 to rounding on any grid. (Until S60 the arm modes were published at the cells' centres.)

The split of a ring's power by arm number survives as a **disclosed check** (item 4): the composed field's own
m-fold Fourier power is published for m = 2 … 6 beside the law's A_m², read, never tuned.

**What is not here.** The bar's body is ``pattern.BarBody``, unchanged. The gas's answer to the pieces is
``gas_pattern``'s, which asks this pattern for each ring's pieces. Nothing here draws: the census is the layer's.
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
from galaxy.stages import gas_response as _cells
from galaxy.stages.pattern import (
    ARM_MODES,
    CELLS,
    PATTERN_READS,
    PIECE_FIELDS,
    BarBody,
    bar_terms,
    invert_azimuths,
    ring_bracket,
    rotation_sense,
)

TWO_PI = 2.0 * math.pi
SQRT_TWO_PI = math.sqrt(TWO_PI)
FWHM_PER_SIGMA = 2.0 * math.sqrt(2.0 * math.log(2.0))  # a Gaussian's full width at half maximum over its dispersion
# The harmonics a ring's arm field is held in where it is integrated or transformed: more than any piece needs.
# The width law keeps a piece's azimuthal dispersion over 0.082 rad at every radius and pitch (σ/R ≥ 0.53 × 0.73 /
# (2 × 2.355) scale lengths per scale length), where harmonic 128 stands e^-55 under the first.
HARMONICS = 128
_M = np.arange(1, HARMONICS + 1, dtype=float)
# A harmonic of a ring's series under this share of the ring's largest is not summed (and none after the last
# that is over it): a term that far under the largest moves no bit of a sum but by rounding.
HARMONIC_FLOOR = 1e-18
# Where the wrapped normal's two forms change over, by the piece's dispersion on the ring (rad). Up to NARROW the
# two nearest images hold it to e^-54; up to WIDE the five nearest; past it six Fourier terms. All three are the
# same function to a part in 1e16 at the changes; which is used is decided element by element, by the dispersion
# alone, so a point reads the same bits in any batch.
NARROW, WIDE = 0.6, 1.5
WIDE_TERMS = 6
# The designed azimuthal dispersion past which a ring carries no arm: √π, where D219's ring variance of a piece,
# σ/(2√π) − σ²/(2π), reaches 0 (``budget_amplitude``). A piece of that dispersion is 239 degrees wide at half
# maximum on its ring.
WIDEST = math.sqrt(math.pi)
MODE_POWER_FIELDS: tuple[str, ...] = tuple(f"arm_mode_power_{m}" for m in ARM_MODES)


# --------------------------------------------------------------------------------------------------------------
# A piece on a ring: the wrapped normal
# --------------------------------------------------------------------------------------------------------------


def harmonic_amplitudes(sigma: np.ndarray) -> np.ndarray:
    """c_m(σ) = (2σ/√(2π)) e^{−m²σ²/2} for m = 1 … :data:`HARMONICS`, shaped (…σ's shape, HARMONICS): the cosine
    amplitudes of a wrapped normal of dispersion σ (rad) and unit height less its mean,
    W(δ; σ) − σ/√(2π) = Σ_m c_m cos(m δ)."""
    s = np.asarray(sigma, dtype=float)[..., None]
    return (2.0 / SQRT_TWO_PI) * s * np.exp(-0.5 * (_M * s) ** 2)


def harmonics_summed(real: np.ndarray, imaginary: np.ndarray) -> np.ndarray:
    """How many harmonics of each ring's series are summed, per ring: up to the last whose amplitude is over
    :data:`HARMONIC_FLOOR` of the ring's largest (0 for a ring that holds none). ``real`` and ``imaginary`` are
    (rings, HARMONICS). A ring's count is its own, so a ring's sum is the same bits alone as in any batch, and
    no ring pays for harmonics only another needs."""
    size = np.sqrt(real**2 + imaginary**2)
    matters = size > HARMONIC_FLOOR * size.max(axis=1, keepdims=True)
    return np.where(matters.any(axis=1), HARMONICS - np.argmax(matters[:, ::-1], axis=1), 0)


def ring_variance(sigma: np.ndarray) -> np.ndarray:
    """v(σ) = Σ_m c_m(σ)²/2 = (σ²/π) Σ_{m≥1} e^{−m²σ²}: the variance round a ring of one piece of unit amplitude and
    azimuthal dispersion σ. For a piece narrower than its ring it is the Gaussian's σ/(2√π) − σ²/(2π) (D219's
    "ring variance"); for one wider it falls as e^{−σ²}, where the Gaussian's expression is negative.

    Evaluated element by element, by σ alone: up to :data:`WIDE` by the sum's other form,
    σ/(2√π) (1 + 2 Σ_{k=1..3} e^{−(πk/σ)²}) − σ²/(2π) (Poisson's summation: the Gaussian's value and the images'
    corrections, to e^-70); past it by the first six terms of the sum itself (to e^-81)."""
    sigma = np.asarray(sigma, dtype=float)
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        images = np.zeros(sigma.shape)
        for k in (1, 2, 3):
            images += np.exp(-((math.pi * k / sigma) ** 2))
        out = np.asarray(sigma / (2.0 * math.sqrt(math.pi)) * (1.0 + 2.0 * images) - sigma * sigma / TWO_PI)
        wide = sigma > WIDE
        if wide.any():
            sw = sigma[wide]
            series = np.zeros(sw.shape)
            for m in range(1, WIDE_TERMS + 1):
                series += np.exp(-((m * sw) ** 2))
            out[wide] = np.where(np.isfinite(sw), sw * sw / math.pi * series, 0.0)
    return out


def deviation(delta: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """W(δ; σ) − σ/√(2π): a piece's profile round its ring less its mean, at azimuth δ from its crest (rad), for an
    azimuthal dispersion σ (rad, positive). ``delta`` and ``sigma`` broadcast against each other.

    W is the wrapped normal Σ_k exp(−(δ + 2πk)²/2σ²), of unit height where σ is small. Its mean round the ring is
    σ/√(2π) exactly, so this function's is 0. Evaluated by the images nearest δ where σ ≤ :data:`WIDE` and by its
    Fourier series past it (the module's constants say to what)."""
    delta, sigma = np.broadcast_arrays(np.asarray(delta, dtype=float), np.asarray(sigma, dtype=float))
    d = np.abs(delta - TWO_PI * np.rint(delta / TWO_PI))  # |δ| brought into [0, π]
    inv = 0.5 / (sigma * sigma)
    out = np.exp(-(d * d) * inv) + np.exp(-((TWO_PI - d) ** 2) * inv)
    mid = sigma > NARROW
    if mid.any():
        dm, im = d[mid], inv[mid]
        out[mid] += np.exp(-((TWO_PI + dm) ** 2) * im) + np.exp(-((2.0 * TWO_PI - dm) ** 2) * im) + np.exp(-((2.0 * TWO_PI + dm) ** 2) * im)
    out -= sigma / SQRT_TWO_PI
    wide = sigma > WIDE
    if wide.any():
        dw, sw = d[wide], sigma[wide]
        series = np.zeros(dw.shape)
        for m in range(1, WIDE_TERMS + 1):
            series += np.exp(-0.5 * (m * sw) ** 2) * np.cos(m * dw)
        out[wide] = (2.0 / SQRT_TWO_PI) * sw * series
    return out


def depth(sigma: np.ndarray) -> np.ndarray:
    """d(σ) = σ/√(2π) − W(π; σ) ≥ 0: how far a piece's trough - opposite its crest - lies under its mean round the
    ring, per unit amplitude. :func:`deviation`'s own arithmetic at δ = π, so the saturation's bound is the point
    function's own least value. σ/√(2π) for a narrow piece, falling to 0 for one that fills its ring."""
    sigma = np.asarray(sigma, dtype=float)
    return -deviation(np.full(sigma.shape, math.pi), sigma)


def budget_amplitude(budget: np.ndarray, count: np.ndarray, sigma_design: np.ndarray) -> np.ndarray:
    """B = √(budget / (N v(σ_d))) per ring: the one amplitude at which N pieces of the designed azimuthal dispersion
    σ_d, at independent uniform azimuths, make the budget's variance round the ring in expectation (D219 item 4).

    0 where the ring has no budget or no count - and **where the designed piece is no ridge on its ring**,
    σ_d ≥ :data:`WIDEST` = √π: there the ruling's own expression for a piece's ring variance, σ_d/(2√π) − σ_d²/(2π),
    is no longer positive, and the exact periodic one falls as e^{−σ_d²} - a height that made the budget's
    variance there would grow without bound toward the centre and lend any piece a little more open than the
    disc's pitch a contrast far beyond the budget. Such a ring carries no arm, and is counted (the builder's
    reading of a case D219 does not cover; the alternative built first, the exact form at every σ_d, put the
    innermost rings at the saturation and drove the gas's forcing past what the solver converges). Never a
    function of a realised power."""
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
    own pitch. Bounded by R/(X h) for every m and pitch, and regular at sin p = 0."""
    m = np.asarray(m, dtype=float)
    return m / (np.asarray(x, dtype=float) * (np.abs(np.asarray(sin_pitch, dtype=float)) + m * np.asarray(height_over_radius, dtype=float)))


# --------------------------------------------------------------------------------------------------------------
# The census as read: the table's rows, and which of them cross a radius
# --------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class Pieces:
    """The realised census of arm pieces, as every reader builds it from the published table (rule A9).

    One entry a piece, in the table's order: ``chain`` and ``order`` name it; ``start_radius`` (kpc) and
    ``start_azimuth`` (rad) are its inner end; ``pitch_deg`` its pitch; ``extent`` (rad) how far round the disc it
    runs; ``pinned`` whether a template stated it. ``turn`` is +1 where a piece of positive pitch gains azimuth
    outwards - the trailing sense, minus the disc's sense of rotation.

    A piece's locus is linear in ln R between its two ends: from x_s = ln R_s to x_e = x_s + Δβ |tan p|, the
    azimuth going from φ_s to φ_s + turn · sign(tan p) · Δβ. A piece with no radial reach (a pitch of exactly 0)
    crosses no ring and is left out of every sum.

    :meth:`slots` gives, for any radius, the pieces that cross it (x_s ≤ ln R < x_e), padded to the most that
    cross any radius: the count is the census's own (rule A1).
    """

    chain: np.ndarray
    order: np.ndarray
    start_radius: np.ndarray
    start_azimuth: np.ndarray
    pitch_deg: np.ndarray
    extent: np.ndarray
    pinned: np.ndarray
    turn: float
    x_start: np.ndarray = field(init=False, repr=False)   # (n + 1,): ln R at the inner end; the last entry is the pad's
    x_end: np.ndarray = field(init=False, repr=False)     # ln R at the outer end
    phi_start: np.ndarray = field(init=False, repr=False)
    phi_end: np.ndarray = field(init=False, repr=False)
    sin_abs: np.ndarray = field(init=False, repr=False)   # |sin p|
    breaks: np.ndarray = field(init=False, repr=False)    # the ln R at which the set of crossing pieces changes
    table: np.ndarray = field(init=False, repr=False)     # (len(breaks) + 1, most): piece indices, the pad's = n
    most: int = field(init=False)

    def __post_init__(self) -> None:
        columns = ("chain", "order", "start_radius", "start_azimuth", "pitch_deg", "extent", "pinned")
        for name in columns:
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float))
        n = self.chain.size
        if any(getattr(self, name).shape != (n,) for name in columns):
            raise ValueError("the columns of the arm pieces' table share one length")
        if n and not (np.all(np.isfinite(self.start_radius)) and np.all(self.start_radius > 0.0) and np.all(np.isfinite(self.start_azimuth))
                      and np.all(np.isfinite(self.pitch_deg)) and np.all(np.isfinite(self.extent)) and np.all(self.extent >= 0.0)):
            raise ValueError("an arm piece has a positive start radius, a start azimuth, a pitch and an extent that are numbers")
        tangent = np.tan(np.radians(self.pitch_deg))
        x_start = np.log(self.start_radius)
        with np.errstate(over="ignore"):
            x_end = x_start + self.extent * np.abs(tangent)
        phi_end = self.start_azimuth + self.turn * np.sign(tangent) * self.extent
        sin_abs = np.abs(np.sin(np.radians(self.pitch_deg)))
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
        # The pad: an entry no ring is crossed by, with numbers that keep every expression finite.
        pad = lambda a, value: np.concatenate([a, [value]])  # noqa: E731
        for name, value in (("x_start", pad(x_start, 0.0)), ("x_end", pad(x_end, 1.0)), ("phi_start", pad(self.start_azimuth, 0.0)),
                            ("phi_end", pad(phi_end, 0.0)), ("sin_abs", pad(sin_abs, 1.0)), ("breaks", breaks), ("table", table)):
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        object.__setattr__(self, "most", int(most))

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], turn: float) -> "Pieces":
        """The census of a run's published table (:data:`~galaxy.stages.pattern.PIECE_FIELDS`)."""
        return cls(*(np.asarray(fields[name], dtype=float) for name in PIECE_FIELDS), turn=turn)

    @property
    def count(self) -> int:
        return int(self.chain.size)

    def slots(self, R: np.ndarray) -> np.ndarray:
        """The pieces crossing each radius, shaped (…R's shape, max(most, 1)): indices into the padded arrays, the
        pad's index where fewer cross. A radius is crossed by a piece from its inner end up to, not including, its
        outer end."""
        with np.errstate(divide="ignore"):
            x = np.log(np.asarray(R, dtype=float))
        return self.table[np.searchsorted(self.breaks, x, side="right")]

    def chains_crossing(self, R: np.ndarray) -> np.ndarray:
        """How many chains have a piece crossing each radius, shaped as ``R``."""
        slots = self.slots(R)
        chain = np.concatenate([self.chain, [np.nan]])[slots]
        chain = np.sort(chain, axis=-1)  # the pad's NaN sorts last
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
        "point. A piece is laid on its ring by the sine of its pitch, so a nearly circular piece, and any "
        "piece close to the centre, spreads round its whole ring and adds no contrast there. "
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
    "round the ring at the disc's own pitch - so that as many pieces as the arm-number law counts, at "
    "independent places round the ring, make the budget's variance on average. The count is the law's arm "
    "number; in a galaxy with measured pieces it is the number of chains that cross the ring. Shown here on "
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
class ArmPattern:
    """The stellar pattern of arm pieces and the bar's body: everything the density contrast needs, read from
    published fields in one place (rule A9).

    c(R, φ) = 1 − β(R) + Σ_bar(R, φ)/Σ(R) + a(R) Σ_j τ_j(R) (W(φ − φ_j(R); σ_φ,j(R)) − σ_φ,j(R)/√(2π)) - the module's
    docstring has each term.

    **Evaluable at a point** (BUILD_III section 1c rule 5, D60): a piece's locus, its taper and its width on the
    ring are closed forms of the point's radius; the budget's amplitude and the width law are the published
    radial fields read linearly in R between the grid radii (held at the end values beyond them); the cut is
    taken at the point's own radius. **The bar's body** is :class:`~galaxy.stages.pattern.BarBody` at the
    normalisation the published ``bar_mass_share`` states, read as it has been since S58.

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
    _taper_start: np.ndarray = field(init=False, repr=False)  # (pieces + 1,): the radial length of a piece's taper at its start, kpc
    _taper_end: np.ndarray = field(init=False, repr=False)
    _r_start: np.ndarray = field(init=False, repr=False)
    _r_end: np.ndarray = field(init=False, repr=False)
    count: np.ndarray = field(init=False, repr=False)       # (R,): the count the budget is divided among, N
    _untapered: np.ndarray = field(init=False, repr=False)  # (R,): the budget with the bar's taper taken back out

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
        # A piece's taper, as a length in radius: one width of arc at each end is |sin p| widths of radius, the
        # width the law's at that end (D219 item 1).
        p = self.pieces
        with np.errstate(over="ignore"):
            r_start, r_end = np.exp(p.x_start), np.exp(p.x_end)
        widths = self.width if self.width.size else np.zeros(1)
        radii = self.R if self.R.size else np.zeros(1)
        for name, value in (("_r_start", r_start), ("_r_end", r_end),
                            ("_taper_start", p.sin_abs * np.interp(r_start, radii, widths)),
                            ("_taper_end", p.sin_abs * np.interp(r_end, radii, widths))):
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        # No perturbation to apply: no arm amplitude or no piece, and no body; or a pattern the grid could not
        # resolve (a mesh too coarse for the shear gives a NaN pitch), which stays axisymmetric. Decided once: the
        # censuses ask per cell.
        finite = (resolved and math.isfinite(self.pitch_deg) and bool(np.all(np.isfinite(self.budget)))
                  and bool(np.all(np.isfinite(self.design))) and bool(np.all(np.isfinite(self.width))))
        if finite and deviation_ is not None and not math.isfinite(bar_terms(self.R, self.pitch_deg, self.bar_length)[2]):
            finite = False  # a body with no angle to lie along
        # The count the budget is divided among (the lead's reading (b) of D219): the law's arm number - or, in a
        # galaxy with pinned pieces, the number of chains that cross the ring. Never a realised power.
        count = p.chains_crossing(self.R).astype(float) if p.pinned.any() else self.design
        # The budget with the bar's taper taken back out: what is read between two rings, so that the taper - the
        # one steep factor in it - is the point's own (the gas pattern has always taken it so). 0 where the taper
        # is whole.
        taper = bar_terms(self.R, self.pitch_deg if finite else 45.0, self.bar_length)[0] if self.R.size else np.zeros(0)
        with np.errstate(divide="ignore", invalid="ignore"):
            untapered = np.where(taper < 1.0, self.budget / np.where(taper < 1.0, (1.0 - taper) ** 2, 1.0), 0.0)
        for name, value in (("count", np.asarray(count, dtype=float)), ("_untapered", untapered)):
            value = np.array(value, dtype=float)
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        object.__setattr__(self, "flat", not finite or (not (self.budget.any() and p.most) and deviation_ is None))

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
        """b on the grid rings: 1 − min_φ of the body's contrast, what the saturation reads; 0 with no body."""
        return np.zeros(self.R.size) if self.body is None else self.body.depth(self.normalisation)

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

    # --- the pieces on a ring ---------------------------------------------------------------------------

    def width_at(self, R: np.ndarray) -> np.ndarray:
        """FWHM across a piece at ``R``, kpc: the published width law, linear between the grid radii."""
        return np.interp(np.asarray(R, dtype=float), self.R, self.width)

    def amplitude_at(self, R: np.ndarray) -> np.ndarray:
        """B at ``R``: the budget's amplitude, **made at the point's own radius** - √(budget / (N v(σ_d))) with the
        untapered budget and the count N read linearly between the grid radii (held at the end values beyond
        them), the bar's taper put back at the radius itself, and σ_d = σ(R)/(R sin p) the designed dispersion
        there. (B itself is not read between rings: toward the centre it grows as e^{σ_d²/2}, and a line between
        two rings' values would be neither ring's law.) At a grid radius it is the published
        ``arm_piece_amplitude``."""
        R = np.asarray(R, dtype=float)
        if not self.R.size:
            return np.zeros(R.shape)
        taper = bar_terms(R, self.pitch_deg, self.bar_length)[0]
        budget = np.interp(R, self.R, self._untapered) * (1.0 - taper) ** 2
        with np.errstate(divide="ignore", invalid="ignore"):
            sigma = design_dispersion(R, self.width_at(R), self.pitch_deg)
        return budget_amplitude(budget, np.interp(R, self.R, self.count), np.nan_to_num(sigma, nan=np.inf, posinf=np.inf))

    def ring_pieces(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """The pieces crossing each radius of ``R`` (any shape S), each array shaped (S, slots):
        ``(slots, taper, azimuth, sigma, sin_abs)`` - the pieces' indices (the pad's where fewer cross); τ, each
        piece's taper at the radius, 0 in a slot that holds none; φ_j, where its locus crosses the ring, rad;
        σ_φ,j = σ/(R |sin p_j|), its dispersion on the ring, rad (1 in an empty slot); and |sin p_j|."""
        R = np.asarray(R, dtype=float)
        p = self.pieces
        slots = p.slots(R)
        live, azimuth, sin_abs = p.geometry(R, slots)
        radius = R[..., None]
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            rise = (radius - self._r_start[slots]) / self._taper_start[slots]
            fall = (self._r_end[slots] - radius) / self._taper_end[slots]
            taper = np.where(live, np.minimum(1.0, np.maximum(0.0, np.minimum(rise, fall))), 0.0)
            sigma = np.where(live, (self.width_at(R) / FWHM_PER_SIGMA)[..., None] / (radius * sin_abs), 1.0)
        return slots, np.nan_to_num(taper, nan=0.0), azimuth, sigma, sin_abs

    def effective_amplitude(self, R: np.ndarray, taper: np.ndarray, sigma: np.ndarray) -> np.ndarray:
        """a(R) = min(B, (1 − b)/Σ_j τ_j d_j) at each radius: the budget's amplitude, cut where the pieces' troughs
        would reach under what the bar's body leaves of the mean (the module's docstring). ``taper`` and
        ``sigma`` are :meth:`ring_pieces`' for the same radii."""
        R = np.asarray(R, dtype=float)
        amplitude = self.amplitude_at(R)
        room = 1.0 - self.depth_at(R)
        deep = (taper * depth(sigma)).sum(axis=-1)
        with np.errstate(over="ignore", invalid="ignore"):
            cut = amplitude * deep > room
            return np.where(cut, room / np.where(cut, deep, 1.0), amplitude)

    def saturation(self, R: np.ndarray) -> np.ndarray:
        """a/B at each radius: the cut of the pieces' amplitude, 1 where it is not cut (and where there is none)."""
        R = np.asarray(R, dtype=float)
        _, taper, _, sigma, _ = self.ring_pieces(R)
        amplitude = self.amplitude_at(R)
        effective = self.effective_amplitude(R, taper, sigma)
        return np.where(amplitude > 0.0, effective / np.where(amplitude > 0.0, amplitude, 1.0), 1.0)

    def arms_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """a(R) Σ_j τ_j (W(φ − φ_j; σ_φ,j) − σ_φ,j/√(2π)) at points, ``R`` and ``phi`` broadcast against each other:
        the pieces alone, with no body and no 1. Its mean round a ring is 0."""
        R, phi = np.asarray(R, dtype=float), np.asarray(phi, dtype=float)
        # The pieces are found once per radius given, not once per point: a column of radii against rows of
        # azimuths reads each radius' pieces once. A point's value is its own radius' and azimuth's alone.
        rank = max(R.ndim, phi.ndim)
        R = R.reshape((1,) * (rank - R.ndim) + R.shape)
        phi = phi.reshape((1,) * (rank - phi.ndim) + phi.shape)
        _, taper, azimuth, sigma, _ = self.ring_pieces(R)
        weight = self.effective_amplitude(R, taper, sigma)[..., None] * taper
        total = (weight * deviation(phi[..., None] - azimuth, sigma)).sum(axis=-1)
        return np.array(np.broadcast_to(total, np.broadcast_shapes(R.shape, phi.shape)))

    def ring_harmonics(self, R: np.ndarray, scale: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
        """The Fourier coefficients of the pieces' sum round each ring of ``R`` (n,): ``(real, imaginary)``, each
        (n, HARMONICS), with Σ_j a τ_j (W_j − mean) = Σ_m (real_m cos mφ − imaginary_m sin mφ). ``scale``,
        shaped (n, slots, HARMONICS), multiplies each piece's m-th harmonic first (the gas's forcing factor)."""
        R = np.asarray(R, dtype=float)
        _, taper, azimuth, sigma, _ = self.ring_pieces(R)
        weight = self.effective_amplitude(R, taper, sigma)[:, None] * taper
        coefficient = weight[..., None] * harmonic_amplitudes(sigma)  # (n, slots, HARMONICS)
        if scale is not None:
            coefficient = coefficient * scale
        angle = azimuth[..., None] * _M
        return (coefficient * np.cos(angle)).sum(axis=1), -(coefficient * np.sin(angle)).sum(axis=1)

    def ring_power(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(the variance round each ring of the pieces' sum, the squared m-fold cosine amplitude for each of
        :data:`~galaxy.stages.pattern.ARM_MODES` shaped (modes, n)): the realised power, exactly, from the
        pieces' own Fourier coefficients."""
        real, imaginary = self.ring_harmonics(R)
        power = real**2 + imaginary**2
        return 0.5 * power.sum(axis=1), np.stack([power[:, m - 1] for m in ARM_MODES])

    def arm_cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """The pieces' sum averaged over each azimuthal cell between ``edges`` at each radius of ``R``, shaped
        (R, cells): the Fourier series integrated term by term - exact, and cells that tile a ring sum to 0."""
        R = np.asarray(R, dtype=float)
        edges = np.asarray(edges, dtype=float)
        real, imaginary = self.ring_harmonics(R)
        last = harmonics_summed(real, imaginary)
        primitive = np.zeros((R.size, edges.size))
        for k in range(int(last.max()) if last.size else 0):
            m = float(k + 1)
            rows = np.flatnonzero(last > k)
            primitive[rows] += (real[rows, k, None] * np.sin(m * edges)[None, :] + imaginary[rows, k, None] * np.cos(m * edges)[None, :]) / m
        return (primitive[:, 1:] - primitive[:, :-1]) / (edges[1:] - edges[:-1])[None, :]

    def ring_profile(self, R: np.ndarray, cells: int = CELLS) -> np.ndarray:
        """The pieces' sum on the centres of ``cells`` equal cells round each ring of ``R``, shaped (R, cells): the
        point function there (what the gas pattern lays its mask on)."""
        R = np.asarray(R, dtype=float)
        return self.arms_at(R[:, None], _cells.cell_centres(cells)[None, :])

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
        between ``edges`` - the pieces' series integrated term by term, the body's interpolant piece by piece. A
        ring's cells average to 1 to rounding on any grid, with nothing divided. (``phi``, the cells' centres,
        is not read: until S60 the arm modes were published there.)"""
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
