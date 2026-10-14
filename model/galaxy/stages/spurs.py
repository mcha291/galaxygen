"""The gas spurs (feathers) composed into the gas's contrast (checkpoint 4; S62, BUILD_III Phase L2; DECISIONS.md D221
item 7 as the lead amended it at S62).

The layer lays the spurs (``galaxy/layer/spurs.py``: the table ``gas_spur``, one row a spur - where its foot stands on
its chain's gas ridge, the ridge's contrast there and the spur's shape). This module is the composing side: the
spurs' field, exact at any point and exactly integrable round any ring, and the stage that publishes the gas's
contrast with them, ``gas_density_contrast`` - moved here from ``gas_pattern`` at S62, because the spurs' spacing
reads the ring's gas column, which the default model publishes after the gas pattern (``sfh_azimuthal`` reads the
pattern's star-formation contrast): the ruling's item 2.

**A spur** (the ruling's item 6). In the log-polar plane of the arm pieces (``pieces.py``: x = ln R, ψ the azimuth
from the spur's foot in the disc's trailing sense, both in the plane's unit, radians) a spur is the straight line
from its foot along (sin p, cos p), p = ``SPUR_PITCH`` from the circle - a short arc of a logarithmic spiral of that
pitch, trailing, which runs outward from the ridge on the arm's outer side - of plane length T = L / R_f, L the
spur's length and R_f its foot's radius: over 240 pc it departs from the plane's straight segment by under a parsec
at the Sun's radius (a declared look; the table's length is the arc's at the foot's radius). With

    d' = Δx cos p − ψ sin p   (across),     t = Δx sin p + ψ cos p   (along; 0 at the foot, T at the tip),

Δx = ln(R/R_f), the spur's excess is

    E = A exp(−λ t) exp(−d'²/2ς²)                 on 0 ≤ t ≤ T,
    E = A exp(−(d'² + t²)/2ς²)                    for t < 0     (a round cap at the foot),
    E = (A/F) exp(−(d'² + (t − T)²)/2ς²)          for t > T     (a round cap at the tip),

ς = σ/R with σ the width's dispersion (FWHM ``SPUR_WIDTH``) and R the point's own radius, as a piece's is; λ =
ln F / T, F = ``SPUR_FALL``; A the ridge's crest contrast at the foot (the table's ``gas_spur_contrast``): "the
foot's peak equal to the ridge's crest contrast there", falling by F to the tip. E is continuous everywhere: the
caps meet the middle at t = 0 and t = T in value and in their distance. A point sees the image of the spur within
half a turn of its middle, ψ ∈ [T cos p/2 − π, T cos p/2 + π).

**Which spurs a radius reads** (``pieces.REACH``'s rule): a spur whose nearest point to the ring - the gap in ln R
past its foot or its tip, times the radius - lies more than :data:`REACH` dispersions off is not read there, at
the point function and at the ring's integrals alike: it is under e^{-40.5} of its height on that ring.

**Round a ring, in closed form.** At a fixed radius the three stretches - t < 0, 0 ≤ t ≤ T, t > T - are intervals in
ψ, cut at ψ₀ = −Δx tan p (t = 0) and ψ₁ = (T − Δx sin p)/cos p (t = T); on each the excess is e^(a quadratic in ψ), integrated by the
error function (the stretches' method, ``pieces.Stretches``; the complementary function where both ends lie in one
tail). The integral is taken over the spur's support on the ring, ψ ∈ [−REACH ς, T cos p + REACH ς], beyond which
the excess is under e^{-40.5} of its height; so a ring's cells' integrals telescope to the ring's whole integral to
rounding.

**The composition** (the ruling's item 4): g' = (1 − ⟨S⟩(R)) g + S, g the gas pattern's contrast (the response
and the bar's lanes), S the spurs' sum and ⟨S⟩(R) its exact mean round the ring at the point's radius. The ring's
mean of g' is exactly (1 − ⟨S⟩) + ⟨S⟩ = 1 and g' is positive wherever g is, while ⟨S⟩ < 1. **What it does not
keep:** the spurs' excess is taken from the whole ring in proportion to g - the interarm floor's share of the ring's
gas falls by ⟨S⟩, as the ridge's does - not from the floor alone. Layer off, and on a ring no spur reaches, g' is
g to the bit.

**Who reads it.** ``GasPattern.contrast_at`` and its exact cell and sector means (the clouds, their texture, the
clusters, and this stage's published field, which places the render's dust and HII regions) - **not** the
star-formation contrast, which keeps neither the lanes nor the spurs (the ruling's item 5).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.gas_pattern import GAS_DENSITY_CONTRAST, GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS
from galaxy.stages.pieces import FWHM_PER_SIGMA, REACH, TWO_PI

# The table's columns (``layer/spurs.py`` declares them), in their order; what every stage that composes the spurs
# into the gas pattern requires.
SPUR_FIELDS: tuple[str, ...] = (
    "gas_spur_chain", "gas_spur_arc", "gas_spur_radius", "gas_spur_azimuth", "gas_spur_spacing",
    "gas_spur_jeans_length", "gas_spur_peak_surface_density", "gas_spur_contrast",
    "gas_spur_pitch", "gas_spur_length", "gas_spur_width", "gas_spur_fall",
)
# What the gas pattern reads of the table to compose the spurs (the walk's own record - the spacing, λ_J and Σ_peak,
# the arc length, the chain - is the gate's and builds nothing).
SPUR_READS: tuple[str, ...] = SPUR_FIELDS
_POINT_BATCH = 4_000_000  # (point, spur) pairs one pass of the point function holds: a bound on memory, never a value

_ERF = np.frompyfunc(math.erf, 1, 1)
_ERFC = np.frompyfunc(math.erfc, 1, 1)


def _gauss_difference(u_lo: np.ndarray, u_hi: np.ndarray) -> np.ndarray:
    """erf(u_hi) − erf(u_lo), element by element (the C library's, so an element is the same bits in any batch): by
    the complementary function where both ends lie in one tail, where the difference of two values near ±1 would
    be rounding."""
    out = np.zeros(u_lo.shape)
    if not u_lo.size:
        return out
    upper = u_lo >= 0.0
    lower = u_hi <= 0.0
    mid = ~(upper | lower)
    if upper.any():
        out[upper] = (_ERFC(u_lo[upper]) - _ERFC(u_hi[upper])).astype(float)
    if lower.any():
        out[lower] = (_ERFC(-u_hi[lower]) - _ERFC(-u_lo[lower])).astype(float)
    if mid.any():
        out[mid] = (_ERF(u_hi[mid]) - _ERF(u_lo[mid])).astype(float)
    return out


def gaussian_integral(lo: np.ndarray, hi: np.ndarray, a: np.ndarray, mu: np.ndarray, log_peak: np.ndarray) -> np.ndarray:
    """∫_lo^hi exp(log_peak − a (ψ − μ)²) dψ, element by element; 0 where hi ≤ lo. a > 0."""
    lo, hi, a, mu, log_peak = np.broadcast_arrays(*(np.asarray(v, dtype=float) for v in (lo, hi, a, mu, log_peak)))
    out = np.zeros(lo.shape)
    open_ = hi > lo
    if open_.any():
        root = np.sqrt(a[open_])
        diff = _gauss_difference(root * (lo[open_] - mu[open_]), root * (hi[open_] - mu[open_]))
        out[open_] = np.exp(log_peak[open_]) * (0.5 * math.sqrt(math.pi) / root) * diff
    return out


@dataclass(frozen=True, slots=True, eq=False)
class Spurs:
    """The spurs of a run's table, as every reader builds them (rule A9): one entry a spur, in the table's order.

    ``radius`` (kpc) and ``azimuth`` (rad) its foot; ``amplitude`` A, the ridge's contrast there; ``pitch_deg``,
    ``length`` (kpc), ``width`` (kpc, FWHM) and ``fall`` its shape; ``turn`` the disc's trailing sense (+1 where an
    arm's azimuth grows outward), the sense ψ is taken in. Built by ``GasPattern.from_fields`` and by tests."""

    radius: np.ndarray
    azimuth: np.ndarray
    amplitude: np.ndarray
    pitch_deg: np.ndarray
    length: np.ndarray
    width: np.ndarray
    fall: np.ndarray
    turn: float
    x: np.ndarray = field(init=False, repr=False)        # ln R_f
    sin: np.ndarray = field(init=False, repr=False)
    cos: np.ndarray = field(init=False, repr=False)
    span: np.ndarray = field(init=False, repr=False)     # T = L / R_f, the plane length
    decay: np.ndarray = field(init=False, repr=False)    # λ = ln F / T
    sigma: np.ndarray = field(init=False, repr=False)    # σ, kpc
    reach_x: np.ndarray = field(init=False, repr=False)  # T sin p: the tip's Δx

    def __post_init__(self) -> None:
        names = ("radius", "azimuth", "amplitude", "pitch_deg", "length", "width", "fall")
        for name in names:
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float).reshape(-1))
        n = self.radius.size
        if any(getattr(self, name).shape != (n,) for name in names):
            raise ValueError("the columns of the spurs' table share one length")
        if n and not (np.all(self.radius > 0.0) and np.all(np.isfinite(self.azimuth)) and np.all(self.amplitude >= 0.0)
                      and np.all((self.pitch_deg > 0.0) & (self.pitch_deg < 90.0)) and np.all(self.length > 0.0)
                      and np.all(self.width > 0.0) and np.all(self.fall >= 1.0)):
            raise ValueError("a spur has a positive foot radius, an azimuth, a contrast not under 0, a pitch inside 0-90 "
                             "degrees, a positive length and width and a fall not under 1")
        pitch = np.radians(self.pitch_deg)
        span = self.length / self.radius
        if n and not np.all(span * np.cos(pitch) < math.pi):
            raise ValueError("a spur longer than half its ring in azimuth: its foot stands too near the centre")
        for name, value in (("x", np.log(self.radius)), ("sin", np.sin(pitch)), ("cos", np.cos(pitch)), ("span", span),
                            ("decay", np.log(self.fall) / span), ("sigma", self.width / FWHM_PER_SIGMA), ("reach_x", span * np.sin(pitch))):
            value.setflags(write=False)
            object.__setattr__(self, name, value)

    @property
    def count(self) -> int:
        return int(self.radius.size)

    # --- which spurs a radius reads ----------------------------------------------------------------------

    def reads(self, R: np.ndarray) -> np.ndarray:
        """(…R, spurs) bool: the spurs read at each radius - those whose nearest point to the ring lies within
        :data:`REACH` dispersions: R times the gap in ln R past the foot or the tip."""
        x = np.log(np.asarray(R, dtype=float))[..., None]
        gap = np.maximum(np.maximum(self.x - x, x - (self.x + self.reach_x)), 0.0)
        return np.asarray(R, dtype=float)[..., None] * gap <= REACH * self.sigma

    # --- the point function ------------------------------------------------------------------------------

    def _psi(self, phi: np.ndarray, j: np.ndarray) -> np.ndarray:
        """ψ of spur ``j`` at azimuths ``phi``: in the trailing sense from its foot, within half a turn of its middle."""
        middle = 0.5 * self.span[j] * self.cos[j]
        return middle + np.mod(self.turn * (phi - self.azimuth[j]) - middle + math.pi, TWO_PI) - math.pi

    def excess(self, R: np.ndarray, phi: np.ndarray, j: np.ndarray) -> np.ndarray:
        """E of spur ``j`` at points (R, φ), the three broadcast against each other."""
        R, phi, j = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(phi, dtype=float), np.asarray(j, dtype=np.int64))
        dx = np.log(R) - self.x[j]
        psi = self._psi(phi, j)
        s, c, T = self.sin[j], self.cos[j], self.span[j]
        across = dx * c - psi * s
        along = dx * s + psi * c
        inv2 = 0.5 * (R / self.sigma[j]) ** 2  # 1 / 2ς²
        before = along < 0.0
        after = along > T
        gap = np.where(before, along, np.where(after, along - T, 0.0))
        height = np.where(before, 1.0, np.where(after, 1.0 / self.fall[j], np.exp(-self.decay[j] * np.clip(along, 0.0, T))))
        return self.amplitude[j] * height * np.exp(-(across * across + gap * gap) * inv2)

    def at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """S, the spurs' sum at points (``R``, ``phi`` broadcast against each other): every spur the point's radius
        reads, added in the table's order."""
        R, phi = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(phi, dtype=float))
        out = np.zeros(R.shape)
        if not self.count:
            return out
        flat_R, flat_phi, flat = R.reshape(-1), phi.reshape(-1), out.reshape(-1)
        step = max(1, _POINT_BATCH // self.count)
        for start in range(0, flat_R.size, step):
            r, p = flat_R[start:start + step], flat_phi[start:start + step]
            near = self.reads(r)
            if not near.any():
                continue
            total = np.zeros(r.size)
            for j in np.flatnonzero(near.any(axis=0)):  # the table's order: the same bits in any batch
                on = near[:, j]
                total[on] = total[on] + self.excess(r[on], p[on], j)
            flat[start:start + step] = total
        return out

    # --- round a ring -------------------------------------------------------------------------------------

    def _support(self, R: np.ndarray, j: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(lo, hi): the spur's support in ψ on the ring at R, inside its window."""
        middle = 0.5 * self.span[j] * self.cos[j]
        reach = REACH * self.sigma[j] / R
        lo = np.maximum(-reach, middle - math.pi)
        hi = np.minimum(self.span[j] * self.cos[j] + reach, middle + math.pi)
        return lo, hi

    def _integral(self, R: np.ndarray, j: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
        """∫_lo^hi E dψ on the ring at R for spur ``j`` (the arguments broadcast): the three stretches in closed form."""
        R, j, lo, hi = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(j, dtype=np.int64), np.asarray(lo, dtype=float), np.asarray(hi, dtype=float))
        dx = np.log(R) - self.x[j]
        s, c, T, lam, A = self.sin[j], self.cos[j], self.span[j], self.decay[j], self.amplitude[j]
        inv2 = 0.5 * (R / self.sigma[j]) ** 2
        psi0 = -dx * s / c          # t = 0
        psi1 = (T - dx * s) / c     # t = T
        # The foot's cap: A exp(−(Δx² + ψ²)/2ς²), ψ < ψ₀.
        cap0 = gaussian_integral(lo, np.minimum(hi, psi0), inv2, 0.0, np.log(A) - dx * dx * inv2)
        # The middle: A exp(−λ t − d'²/2ς²) = exp(log A + C + b ψ − a ψ²).
        a = inv2 * s * s
        b = 2.0 * inv2 * dx * c * s - lam * c
        C = -lam * dx * s - inv2 * dx * dx * c * c
        mid = gaussian_integral(np.maximum(lo, psi0), np.minimum(hi, psi1), a, b / (2.0 * a), np.log(A) + C + b * b / (4.0 * a))
        # The tip's cap: (A/F) exp(−((Δx − T sin p)² + (ψ − T cos p)²)/2ς²), ψ > ψ₁.
        tip_dx = dx - T * s
        cap1 = gaussian_integral(np.maximum(lo, psi1), hi, inv2, T * c, np.log(A) - np.log(self.fall[j]) - tip_dx * tip_dx * inv2)
        with np.errstate(divide="ignore"):
            return np.where(A > 0.0, cap0 + mid + cap1, 0.0)

    def ring_mean(self, R: np.ndarray) -> np.ndarray:
        """⟨S⟩ at each radius of ``R`` (any shape): the spurs' exact integral round the ring over 2π."""
        R = np.asarray(R, dtype=float)
        out = np.zeros(R.shape)
        if not self.count or not R.size:
            return out
        radii, inverse = np.unique(R.reshape(-1), return_inverse=True)
        mean = np.zeros(radii.size)
        near = self.reads(radii)
        for j in np.flatnonzero(near.any(axis=0)):
            on = near[:, j]
            lo, hi = self._support(radii[on], j)
            mean[on] = mean[on] + self._integral(radii[on], j, lo, hi)
        return (mean / TWO_PI)[inverse].reshape(R.shape)

    def cell_integrals(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """∫ S dφ over each azimuthal cell between ``edges`` (ascending, radians) at each radius of ``R``, shaped
        (R, cells): each spur's antiderivative in ψ at the edges, continued periodically, differenced - so a ring's
        cells add up to its whole integral (2π ⟨S⟩) to rounding, and nothing is divided."""
        R = np.asarray(R, dtype=float).reshape(-1)
        edges = np.asarray(edges, dtype=float)
        out = np.zeros((R.size, edges.size - 1))
        if not self.count or not R.size:
            return out
        near = self.reads(R)
        for j in np.flatnonzero(near.any(axis=0)):
            rows = np.flatnonzero(near[:, j])
            r = R[rows][:, None]
            lo, hi = self._support(r, j)
            whole = self._integral(r, j, lo, hi)
            middle = 0.5 * self.span[j] * self.cos[j]
            psi = np.broadcast_to(self.turn * (edges[None, :] - self.azimuth[j]), (rows.size, edges.size))
            turns = np.floor((psi - (middle - math.pi)) / TWO_PI)
            q = psi - TWO_PI * turns  # inside the window
            inside = (q > lo) & (q < hi)
            partial = np.where(q >= hi, whole, 0.0)
            if inside.any():
                r_in = np.broadcast_to(r, q.shape)[inside]
                lo_in = np.broadcast_to(lo, q.shape)[inside]
                partial[inside] = self._integral(r_in, j, lo_in, q[inside])
            running = turns * whole + partial
            out[rows] = out[rows] + self.turn * (running[:, 1:] - running[:, :-1])
        return out

    # --- the composition ------------------------------------------------------------------------------------

    def compose_at(self, R: np.ndarray, phi: np.ndarray, contrast: np.ndarray) -> np.ndarray:
        """g' = (1 − ⟨S⟩(R)) g + S at points, ``contrast`` g there (broadcast as ``R`` and ``phi``): g itself, to the
        bit, at a radius no spur reaches."""
        R, phi, contrast = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(phi, dtype=float), np.asarray(contrast, dtype=float))
        mean = self.ring_mean(R)
        touched = mean > 0.0
        if not touched.any():
            return np.array(contrast, dtype=float)
        out = np.array(contrast, dtype=float)
        out[touched] = (1.0 - mean[touched]) * contrast[touched] + self.at(R[touched], phi[touched])
        return out

    def compose_cells(self, R: np.ndarray, edges: np.ndarray, means: np.ndarray) -> np.ndarray:
        """The exact cell means of g', ``means`` g's cell means between ``edges`` at each radius of ``R``: (1 − ⟨S⟩)
        g's mean plus S's - the ring's cells average to 1 to rounding wherever g's do. g's own, to the bit, on a ring
        no spur reaches."""
        R = np.asarray(R, dtype=float).reshape(-1)
        edges = np.asarray(edges, dtype=float)
        mean = self.ring_mean(R)
        out = np.array(means, dtype=float)
        touched = mean > 0.0
        if touched.any():
            width = edges[1:] - edges[:-1]
            out[touched] = (1.0 - mean[touched])[:, None] * out[touched] + self.cell_integrals(R[touched], edges) / width[None, :]
        return out


def compute_spurs(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    cells = (R.size, ctx.grid.phi.size)

    def make() -> np.ndarray:
        # The gas pattern with the spurs the layer laid (compose reads the table through this stage's view), and its
        # exact mean over each of the grid's φ cells on each grid ring - the field gas_pattern published until S62.
        shape = _compose.gas_pattern(ctx.fields, R, ctx.constants)
        if shape is None or shape.flat:
            return _compose.neutral(GAS_DENSITY_CONTRAST, cells)
        return shape.cell_means(R, ctx.grid["phi"].edges)

    return {GAS_DENSITY_CONTRAST.name: _compose.field(ctx.fields, GAS_DENSITY_CONTRAST, cells, make)}


SPURS = IMPLEMENTATIONS.register(
    Stage(
        id="spurs", slot="spurs", checkpoint=4,
        about=(
            "The gas's density contrast with its spurs: the gas pattern's steady response to the arms and the bar's "
            "lanes, and on it the feathers the layer laid off each arm chain's gas ridge - each a short trailing "
            "streak of gas at a steep pitch on the ridge's outer side, as dense at its foot as the ridge there and "
            "fading to a seventh of that at its tip - their excess taken from the whole ring in proportion to its "
            "gas, so every ring keeps its gas exactly. It publishes the gas contrast the dust, the HII regions, the "
            "clouds and the clusters are placed by (the star formation law reads the pattern's other contrast, "
            "without lanes or spurs). It stands after the star formation history because the spurs' spacing reads "
            "the ring's gas column; it draws nothing."
        ),
        compute=compute_spurs,
        reads_constants=GAS_PATTERN_CONSTANTS,
        requires=(*GAS_PATTERN_READS, *SPUR_READS),
        publishes=(GAS_DENSITY_CONTRAST,),
    )
)
