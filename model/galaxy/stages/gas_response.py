"""The steady response of isothermal gas to a spiral potential on a ring: the smooth branch (S57, D216, gate G2).

No stage: a numerical module. It solves one ordinary differential equation on a ring, for many rings at
once, and reads the solution at a point. Nothing here knows a galaxy; the stage that calls it hands it a
forcing and a number per ring.

**The law** (D216 item 5; the reading's `docs/READING_GAS_SHOCK.md` C1.1 and C3). On a ring, with χ the
pattern coordinate (period 2π round the ring) and s(χ) = Σ_gas/Σ_gas,mean, the steady flow with no shock obeys

    d/dχ [ (ε² − μ²/s²) · d ln s/dχ ] = s − 1 − g(χ)

- g(χ) is the forcing, any periodic function; the model's is g = Σ_m f_m cos(mχ − θ_m), zero in the mean,
  with f_m = m A_m/(X sin p) (``forcing_amplitudes``).
- ε = a/(κ R sin p) (``epsilon``): the sound speed over the epicyclic frequency times the arm-normal length.
- μ = (Ω_p − Ω)/κ is the frame's flow through the pattern. For one mode m, Shu, Milione & Roberts 1973's
  variables are ν = mμ, x = m²ε², η = mχ, and the equation is theirs, [(x − ν²/s²)(ln s)′]′ = s − 1 − f cos η
  (D216 item 10): the continuity equation s w = −ν put into the normal equation, with the parallel
  equation dv/dη = s − 1 - uniform potential vorticity.
- **The model uses μ = 0 only** (D216 item 1: every arm mode turns with the gas). Then ε² (ln s)″ = s − 1 − g
  is the Euler-Lagrange equation of J[φ] = ∫ [ε² φ′²/2 + e^φ − (1 + g) φ] dχ, φ = ln s: strictly convex and
  coercive on periodic functions, so the solution exists, is unique, is positive, and its mean is 1 + ḡ.
  The general μ is here so that the same code path can be certified against a published number (Sormani
  et al. 2017's no-shock threshold; ``tests/test_gas_response.py``).
- **No shocked branch** (forbidden this session; it is P3's). For μ ≠ 0 the smooth branch exists only while
  the flow stays on one side of the sound speed on every cell: ε² − μ²/s² keeps the sign it has at s = 1
  (base-subsonic, ε > |μ|: s > |μ|/ε everywhere). Its loss is detected and raised, never returned.

**The discretisation.** (ε² − μ²/s²) φ′ is the derivative of H(φ) = ε² φ + μ² e^{−2φ}/2, so the equation is
H(φ)″ = e^φ − 1 − g. On ``cells`` periodic cells of width h = 2π/cells, centred at χ_k = −π + (k + ½) h, a
flux lives on each cell face,

    Φ_{k+½} = [H(φ_{k+1}) − H(φ_k)] / h² = [ε² d_k + ½ μ² e^{−2φ_k} expm1(−2 d_k)] / h²,   d_k = φ_{k+1} − φ_k,

and a cell's equation is r_k = s_k − 1 − g_k − (Φ_{k+½} − Φ_{k−½}) = 0: second order, and conservative. The
same number Φ_{k+½} leaves cell k and enters cell k + 1, so the sum of the cells' equations is
Σ (s_k − 1 − g_k) = Σ r_k whatever φ is: **the ring's mean is 1 + ḡ by the equation, with no division and no
renormalisation anywhere in this module**; what is left is the residual's own sum, and convergence asks for
it (below). At the no-shock threshold φ has a corner where the flow touches the sound speed but H is smooth,
which is why the differences are taken in H.

**Newton, each count fixed in advance (rule A1; D216 item 7).** The unknown is φ = ln s, so s > 0 with
nothing clipped. A step solves the cyclic tridiagonal system A δ = −r, A_kk = s_k + 2H′_k/h²,
A_k,k±1 = −H′_k±1/h², H′ = ε² − μ²/s², and moves φ ← φ + t δ, t = 1, ½, ¼, …: at μ = 0 the step is halved
while J does not fall; at μ ≠ 0 while the residual's max norm does not fall. J's fall is summed term by term
from the step (``_functional_fall``), because the difference of two rounded J's is noise on the last steps.
At most ``MAX_NEWTON_STEPS`` steps and ``MAX_HALVINGS`` halvings of any one step.

**When a ring has converged** (D216, gate G3 item 2). A cell is converged when

    |r_k| ≤ max(``RESIDUAL_TOLERANCE``, F_k),   F_k = 2 (ε²/h²) (½ ulp(φ_{k−1}) + ulp(φ_k) + ½ ulp(φ_{k+1})),

φ = ln s, the neighbours periodic, ulp(φ) the spacing of doubles at |φ|; a ring is converged when every cell
is and |Σ_k r_k| < ``SUM_TOLERANCE`` × cells - the second is the ring's mean, held ten times inside the gate's
1e-12. (At μ ≠ 0, once every cell is inside its bound, where the residual sits on its rounding floor, a step
is also taken if it keeps it there and the sum falls: the sum may still be owed a step.) **A ring that has
not converged within the counts raises ``ConvergenceError``**: at μ = 0 the solution exists, so the failure is
the solver's. There is no fallback and no linear substitute.

*Why F_k: a theorem about the rounded exact solution, not a loosened number.* The residual's terms are not of
order 1: the flux's difference is (ε²/h²)(φ_{k+1} − 2φ_k + φ_{k−1}), three numbers each of size ε²|φ|/h² -
5e4 |φ| at ε = 1 and 1440 cells - whose sum is of order 1. φ is a double. Take the discrete equation's exact
solution and round each φ_k to the nearest double: each moves by at most ½ ulp(φ_k), and the residual of
that best possible array, in exact arithmetic, is as large as (ε²/h²)(½ ulp(φ_{k−1}) + ulp(φ_k) + ½ ulp(φ_{k+1})).
No array of doubles can be asked for less; the factor 2 covers the rounding of the residual's own arithmetic.
At 1440 cells F is 1e-12 for ε = 0.072 and |φ| < 8, where the absolute tolerance governs as it always did;
it passes 1e-10 where ε is of order 1 and the trough deep - at ε = 1, |φ| in [4, 8) gives 9.3e-11 and
[8, 16) 1.9e-10 - which is a tightly wound galaxy's inner rings (a pitch under about 2.7 degrees). There an
absolute 1e-10 lay under the rounding of doubles: Newton converged quadratically to within an ulp of the
exact discrete solution, sat at 1.0-1.4e-10, and the ring was solved and still raised (S57's first build;
5 and 15 of 300 pattern seeds for the two templates). ``Diagnostics.floor`` records each ring's max_k F_k,
and :func:`rounding_floor` gives F_k for any profile, so that a caller can hold the profile it was returned,
its logarithm taken again, to |r_k| ≤ max(1e-10, F_k + 4u ε²/h²), u = 2⁻⁵³ (the logarithm's own rounding).

**The linear system** is solved for all rings together by cyclic reduction: the odd cells are eliminated
from the even cells' equations, which leaves a cyclic tridiagonal system on half the cells; 1440 = 2⁵ · 45
halves five times, and the 45 cells left are solved by Thomas's elimination with the Sherman-Morrison
correction for the cyclic corner, a loop over cells whose every operation runs across the rings. No dense
matrix is formed. At μ = 0 the matrix is symmetric, positive definite and diagonally dominant, and so is
every reduced one; no pivoting is needed.

**Reproducible, and independent of the batch.** Every operation on a ring's cells is an elementwise numpy
operation or a sum along the ring's own cells; a ring that has converged is dropped from the working arrays
and a ring's halvings are its own. So a ring takes the same arithmetic alone as in any batch at any
position, and the same inputs give the same bits (tested, not assumed: numpy's exp is vectorised).

**The step at μ ≠ 0 is taken in H, and held on the base flow's side.** As the forcing nears the no-shock
threshold φ grows a corner where the flow touches the sound speed while H stays smooth; a Newton step added
to φ then overshoots at any useful length (measured: from the solution at f = 0.7199 of Sormani's case to
f = 0.7200 a step in φ had to be cut to 1/128 and gained 0.1 % of the residual). So the same Newton step is
applied to H: H ← H + t H′ δ, and φ is read back from H on the base flow's branch. With φ_c = ln(|μ|/ε) the
sonic value and ψ = φ − φ_c, H = ε² (φ_c + ½ + K(ψ)), K(ψ) = ψ + expm1(−2ψ)/2 ≥ 0, zero on the sonic line,
one universal function; ψ > 0 is subsonic, ψ < 0 supersonic. ``_branch_step`` finds the step in φ that
moves K by the linear amount: Newton on a convex function from the side it converges from monotonically,
``INVERSE_STEPS`` steps. A trial that would put any cell on or past the sonic line (K + t δK ≤ 0) is not a
state of the smooth branch: it is refused and halved like a residual that did not fall. At μ = 0, H = ε² φ
and the step is the plain one in φ: one code path, one linear system, one residual. (For base-subsonic flow
the equation in H is −H″ + S(H) = 1 + g with S increasing and concave and the Jacobian an M-matrix: Newton's
iterates in H rise monotonically to the solution from below once one of them is under it - the reason the
step holds up to the threshold.)

**Losing the smooth branch (μ ≠ 0).** A ring that has not converged within the counts, and whose last step
was refused at the sonic line at any length, raises ``SmoothBranchLost``; one that ran out of counts without
touching the line raises ``ConvergenceError``. Past the threshold the discrete equations have no solution
with every cell on the base's side: the iterates run up against the line with the residual stalled. It is a
detection, not a proof - no smooth solution was reached from this start within the counts, with the sonic
line in the way - and it is certified where it is used: Sormani et al. 2017's base-subsonic threshold,
found by continuation to the published digits, the bracket closed to 3e-9 in f, the last smooth solves
taking up to 41 of the 120 steps. **The base-supersonic branch (|μ| > ε) runs through the same code and is
not certified**: its linear limit is tested, but its Jacobian is indefinite (the linear response has
resonances at n² (ν² − x) = 1), Newton slows near its threshold and may run out of counts there with either
error. Shu, Milione & Roberts's base-supersonic cusps belong to P3's certification with the shocked branch.

**Reading a point** (D216 item 9). ``interpolate`` is linear in χ between cell centres, periodic: a convex
blend of two cells, so never under the profile's least cell, and its mean round the ring is the cells' mean.
``sector_mean`` is that interpolant's exact mean over any interval of χ. Measured at 1440 cells on the two
hard rings and pinned in ``tests/test_gas_response.py``: midway between centres the interpolant is off the
profile by 1.96e-4 and 1.54e-4 of the ring's mean at worst (h²/8 · max|s″|; up to 1.3e-3 of the local s),
twice the 1e-4 the gate expected, and the solver's own discretisation error is 3.2e-5 and 2.7e-5, falling
four-fold per doubling of the cells.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

CELLS = 1440  # the fixed periodic cells round a ring (D216 item 7, "1440, as probed"): 2^5 x 45, a quarter degree

# A1: every count is fixed in advance. Measured in S57 at 1440 cells (``tests/test_gas_response.py`` pins
# them). From s = 1 at μ = 0: 3-8 steps on ordinary rings; 7 on the two hard cases (five modes, trough 0.0073;
# total forcing 2.1 at ε = 0.072, trough 0.0010); 8 at most over 400 random five-mode rings of total forcing
# 2.1 (troughs down to 1.6e-10); 11 for one mode of forcing 2.1 at m = 1 (trough 1e-82). No step was halved:
# from s = 1 Newton in ln s comes down on the solution. From a start that is far (another ring's solution,
# e^{8 cos 3χ}, e^{−30(1 + cos 5χ)}): 16 steps at most, 3 halvings of one step at most. At μ ≠ 0, within 1e-6
# of Sormani's no-shock threshold: 41 steps at most, 5 halvings of one step (75 and 6 at 2880 cells). The
# gate's own probe saw 34 steps on its hardest ring. 120 is three times the most seen at 1440 cells and
# fifteen times the model's own rings; 2^-30 of a Newton step is shorter than any step a later one could use.
MAX_NEWTON_STEPS = 120
MAX_HALVINGS = 30

# The discrete equation's residual on every cell (D216, the gate): held under this number, or under the cell's
# rounding floor F_k where that is the larger (gate G3 item 2; the module's docstring). The residual's own terms
# are of size ε²|φ|/h², not of order 1: only their sum is.
RESIDUAL_TOLERANCE = 1e-10
SUM_TOLERANCE = 1e-13  # |Σ_k r_k| / cells: the ring's mean of s against 1 + ḡ, ten times inside the gate's 1e-12

INVERSE_STEPS = 8  # Newton steps of ``_branch_step`` (μ ≠ 0 only); measured: 4 reach rounding on both branches
_DIRECT = 6  # cyclic reduction halves an even cell count while at least this many cells are left (so >= 3 after)


class GasResponseError(RuntimeError):
    """A ring's steady response was not found. ``ring`` is its row in the call's batch."""

    def __init__(self, message: str, ring: int, residual: float, steps: int) -> None:
        super().__init__(message)
        self.ring = int(ring)
        self.residual = float(residual)
        self.steps = int(steps)


class ConvergenceError(GasResponseError):
    """A ring did not converge within ``MAX_NEWTON_STEPS`` steps or ``MAX_HALVINGS`` halvings of one step.

    At flow = 0 the solution exists and is unique, so this is the solver's failure, never the ring's
    (D216 item 7): a build failure, with no fallback.
    """


class SmoothBranchLost(GasResponseError):
    """At flow ≠ 0 a ring did not converge within the counts and its last step was refused at the sonic line.

    ``cells`` holds the indices of the cells that the last refused trial put on or past the sound speed:
    where the flow first touches it. The shocked branch that takes over is not built here (D216 item 10).
    """

    def __init__(self, message: str, ring: int, residual: float, steps: int, cells: np.ndarray) -> None:
        super().__init__(message, ring, residual, steps)
        self.cells = np.asarray(cells, dtype=int)


@dataclass(frozen=True)
class Diagnostics:
    """What Newton did, ring by ring (each array is shaped (rings,))."""

    steps: np.ndarray  # Newton steps taken
    halvings: np.ndarray  # halvings, summed over the ring's steps
    deepest: np.ndarray  # the most halvings any one of the ring's steps took
    residual: np.ndarray  # max_k |r_k| of the returned profile (dimensionless)
    residual_sum: np.ndarray  # Σ_k r_k of the returned profile: cells × (mean s − 1 − mean g), to rounding
    floor: np.ndarray  # max_k F_k of the returned profile: the ring's rounding floor (gate G3 item 2), dimensionless

    @property
    def worst_steps(self) -> int:
        return int(self.steps.max()) if self.steps.size else 0

    @property
    def worst_halvings(self) -> int:
        return int(self.deepest.max()) if self.deepest.size else 0

    @property
    def worst_residual(self) -> float:
        return float(self.residual.max()) if self.residual.size else 0.0


# --------------------------------------------------------------------------------------------------------------
# The law's small helpers
# --------------------------------------------------------------------------------------------------------------


def cell_centres(cells: int = CELLS) -> np.ndarray:
    """The cells' centres χ_k = −π + (k + ½)·2π/cells, in radians of the pattern coordinate; shaped (cells,)."""
    return -math.pi + (np.arange(cells) + 0.5) * (2.0 * math.pi / cells)


def forcing_amplitudes(arm_numbers, amplitudes, x, sin_pitch) -> np.ndarray:
    """f_m = m A_m / (X sin p): each mode's forcing in Shu, Milione & Roberts's variable (dimensionless).

    ``arm_numbers`` m, shaped (modes,); ``amplitudes`` A_m, the mode's cosine amplitude as a fraction of
    the surface density X is made from, shaped (rings, modes) or (modes,); ``x`` the arm-number law's
    X = κ²R/(2πGΣ), dimensionless, shaped (rings,) or a scalar; ``sin_pitch`` sin p, dimensionless, a scalar
    or (rings,). Returns (rings, modes) - or (modes,) for one ring's amplitudes with a scalar X and sin p.
    No factor is added and nothing is scaled (D216 item 5).
    """
    m = np.asarray(arm_numbers, dtype=float)
    a = np.asarray(amplitudes, dtype=float)
    scale = np.asarray(x, dtype=float) * np.asarray(sin_pitch, dtype=float)
    return m * a / scale[..., None]


def epsilon(sound_speed, kappa, radius, sin_pitch) -> np.ndarray:
    """ε = a / (κ R sin p), dimensionless: the sound speed over κ times the arm-normal length R sin p.

    ``sound_speed`` a in km/s; ``kappa`` the epicyclic frequency in km/s/kpc; ``radius`` R in kpc;
    ``sin_pitch`` sin p. Any shapes that broadcast. For one mode m, Shu, Milione & Roberts's x is m² ε².
    """
    return np.asarray(sound_speed, dtype=float) / (
        np.asarray(kappa, dtype=float) * np.asarray(radius, dtype=float) * np.asarray(sin_pitch, dtype=float)
    )


def forcing(arm_numbers, amplitudes, phases, cells: int = CELLS) -> np.ndarray:
    """g(χ_k) = Σ_m f_m cos(m χ_k − θ_m) on the cells' centres (dimensionless); shaped (rings, cells).

    ``arm_numbers`` m, shaped (modes,); ``amplitudes`` f_m (``forcing_amplitudes``), shaped (rings, modes);
    ``phases`` θ_m in radians, shaped (rings, modes) or (modes,). The modes are summed in the order given.
    A cosine of a whole number of periods sums to zero over the equal cells, so g's mean is zero to rounding.
    """
    m = np.asarray(arm_numbers, dtype=float)
    f = np.atleast_2d(np.asarray(amplitudes, dtype=float))
    theta = np.broadcast_to(np.asarray(phases, dtype=float), f.shape)
    chi = cell_centres(cells)
    g = np.zeros((f.shape[0], cells))
    for j in range(m.size):  # a fixed, short loop over the modes: no (rings, modes, cells) array
        g += f[:, j, None] * np.cos(m[j] * chi[None, :] - theta[:, j, None])
    return g


# --------------------------------------------------------------------------------------------------------------
# The discrete equation
# --------------------------------------------------------------------------------------------------------------


def _to_next(a: np.ndarray) -> np.ndarray:
    """a_{k+1} − a_k, cyclic in k: a difference on the face k + ½."""
    d = np.empty_like(a)
    np.subtract(a[:, 1:], a[:, :-1], out=d[:, :-1])
    np.subtract(a[:, 0], a[:, -1], out=d[:, -1])
    return d


def _state(phi: np.ndarray, g: np.ndarray, eps2: np.ndarray, mu2: np.ndarray, moving: bool):
    """s = e^φ and the residual r_k = s_k − 1 − g_k − (Φ_{k+½} − Φ_{k−½}); every array (rings, cells) or (rings, 1)."""
    inv_h2 = (phi.shape[1] / (2.0 * math.pi)) ** 2
    s = np.exp(phi)
    d = _to_next(phi)  # d_k = φ_{k+1} − φ_k, on the face k + ½
    flux = eps2 * d
    if moving:
        flux += 0.5 * mu2 * np.exp(-2.0 * phi) * np.expm1(-2.0 * d)
    flux *= inv_h2
    r = s - 1.0
    r -= g
    r[:, 1:] -= flux[:, 1:] - flux[:, :-1]  # the face k + ½ less the face k − ½: the one number, both cells
    r[:, 0] -= flux[:, 0] - flux[:, -1]
    return s, r


def _branch_step(psi, slope, linear, k_trial, subsonic) -> np.ndarray:
    """The step Δ in φ that moves H by the linear step's amount, on the base flow's branch (μ ≠ 0).

    K(ψ + Δ) − K(ψ) = K′(ψ) Δ + e^{−2ψ} K(Δ), so Δ solves K′(ψ) (Δ − ℓ) + e^{−2ψ} K(Δ) = 0 with ℓ the
    step Newton would add to φ (``linear``), K′(ψ) = ``slope`` and ``k_trial`` = K(ψ) + K′(ψ) ℓ > 0 the
    value aimed at. Written in the increment, a small step keeps its relative accuracy, so the last Newton
    steps are limited by φ's own rounding and nothing else. Newton on a convex function from the far side
    of the root, from which it converges monotonically: the nearer of the linear step (when it stays on
    the branch) and the bound ψ ≤ √k + k (subsonic, where K ≤ ψ²) or ψ ≥ −½ ln(1 + 2k + 2√k) (supersonic,
    where K ≥ ψ²). ``INVERSE_STEPS`` steps. A target so near the sonic line that the start rounds onto it
    comes back non-finite or off the branch, and the caller refuses it.
    """
    root = np.sqrt(k_trial)
    bound = np.where(subsonic, root + k_trial, -0.5 * np.log1p(2.0 * k_trial + 2.0 * root)) - psi
    nearer = np.where(subsonic, np.minimum(linear, bound), np.maximum(linear, bound))
    step = np.where(np.where(subsonic, psi + linear > 0.0, psi + linear < 0.0), nearer, bound)
    decay = 1.0 - slope  # e^{−2ψ}
    for _ in range(INVERSE_STEPS):
        value = slope * (step - linear) + decay * (step + 0.5 * np.expm1(-2.0 * step))
        step = step + value / np.expm1(-2.0 * (psi + step))  # K′(ψ + Δ) = −expm1(−2(ψ + Δ))
    return step


def _functional_fall(phi, s, g, eps2, delta, t) -> np.ndarray:
    """[J(φ + tδ) − J(φ)] / h at μ = 0, summed term by term so that a small step's fall is not lost in rounding."""
    inv_h2 = (phi.shape[1] / (2.0 * math.pi)) ** 2
    d = _to_next(phi)
    dd = t * _to_next(delta)
    step = t * delta
    terms = (0.5 * inv_h2) * eps2 * dd * (2.0 * d + dd) + s * np.expm1(step) - (1.0 + g) * step
    return terms.sum(axis=1)


def _thomas_cyclic(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> np.ndarray:
    """Solve a_k x_{k−1} + b_k x_k + c_k x_{k+1} = d_k, cyclic in k, for every ring; arrays (rings, n), n ≥ 3.

    Thomas's elimination on the matrix without its two corners, twice (the right-hand side and the
    corner's vector), and the Sherman-Morrison correction. The loop is over the cells; each operation
    runs across the rings.
    """
    n = b.shape[1]
    gamma = -b[:, 0]
    diagonal = b.copy()
    diagonal[:, 0] = b[:, 0] - gamma
    diagonal[:, n - 1] = b[:, n - 1] - c[:, n - 1] * a[:, 0] / gamma
    y = d.copy()
    z = np.zeros_like(d)
    z[:, 0] = gamma
    z[:, n - 1] = c[:, n - 1]
    upper = np.empty_like(b)
    pivot = diagonal[:, 0]
    upper[:, 0] = c[:, 0] / pivot
    y[:, 0] = y[:, 0] / pivot
    z[:, 0] = z[:, 0] / pivot
    for k in range(1, n):
        pivot = diagonal[:, k] - a[:, k] * upper[:, k - 1]
        upper[:, k] = c[:, k] / pivot
        y[:, k] = (y[:, k] - a[:, k] * y[:, k - 1]) / pivot
        z[:, k] = (z[:, k] - a[:, k] * z[:, k - 1]) / pivot
    for k in range(n - 2, -1, -1):
        y[:, k] = y[:, k] - upper[:, k] * y[:, k + 1]
        z[:, k] = z[:, k] - upper[:, k] * z[:, k + 1]
    last = a[:, 0] / gamma
    factor = (y[:, 0] + last * y[:, n - 1]) / (1.0 + z[:, 0] + last * z[:, n - 1])
    return y - factor[:, None] * z


def _solve_cyclic(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> np.ndarray:
    """The same system by cyclic reduction: halve the cells while their count is even, then ``_thomas_cyclic``.

    An odd cell j's equation gives x_j from its two even neighbours; put into the even cells' equations
    it leaves a cyclic tridiagonal system on the even cells alone. The depth is the number of twos in the
    cell count (five for 1440), known in advance.
    """
    n = b.shape[1]
    a, c = np.broadcast_to(a, b.shape), np.broadcast_to(c, b.shape)  # an off-diagonal may be one number per ring
    if n % 2 or n < _DIRECT:
        return _thomas_cyclic(a, b, c, d)
    a_even, b_even, c_even, d_even = a[:, 0::2], b[:, 0::2], c[:, 0::2], d[:, 0::2]
    a_odd, b_odd, c_odd, d_odd = a[:, 1::2], b[:, 1::2], c[:, 1::2], d[:, 1::2]
    # the even cell 2j has the odd cell 2j − 1 (odd index j − 1) on its left and 2j + 1 (odd index j) on its right
    left = a_even / np.roll(b_odd, 1, axis=1)
    right = c_even / b_odd
    x_even = _solve_cyclic(
        -left * np.roll(a_odd, 1, axis=1),
        b_even - left * np.roll(c_odd, 1, axis=1) - right * a_odd,
        -right * c_odd,
        d_even - left * np.roll(d_odd, 1, axis=1) - right * d_odd,
    )
    x = np.empty_like(d)
    x[:, 0::2] = x_even
    x[:, 1::2] = (d_odd - a_odd * x_even - c_odd * np.roll(x_even, -1, axis=1)) / b_odd
    return x


def _rows(a: np.ndarray, index: np.ndarray) -> np.ndarray:
    """a[index] for a sorted index without repeats; when that is every row, a itself (read, never written through)."""
    return a if index.size == a.shape[0] else a[index]


def _floor(phi: np.ndarray, eps2: np.ndarray) -> np.ndarray:
    """F_k = 2 (ε²/h²)(½ ulp(φ_{k−1}) + ulp(φ_k) + ½ ulp(φ_{k+1})), cyclic in k: each cell's rounding floor.

    ``phi`` (rings, cells), ``eps2`` (rings, 1). The residual of the exact discrete solution rounded to doubles
    is this large without the 2; the 2 covers the residual's own arithmetic (gate G3 item 2)."""
    inv_h2 = (phi.shape[1] / (2.0 * math.pi)) ** 2
    ulp = np.spacing(np.abs(phi))
    return (2.0 * inv_h2) * eps2 * (0.5 * np.roll(ulp, 1, axis=1) + ulp + 0.5 * np.roll(ulp, -1, axis=1))


def _measure(r: np.ndarray, phi: np.ndarray, eps2: np.ndarray):
    """A residual's max norm, its sum, whether the ring has converged, and whether every cell is inside its
    bound; each shaped (rings,).

    A cell is inside its bound when |r_k| ≤ max(RESIDUAL_TOLERANCE, F_k) (``_floor``); the ring has converged
    when every cell is and |Σ_k r_k| < SUM_TOLERANCE × cells (gate G3 item 2).

    The cells' floors are computed only for the rings they can decide. A ring whose largest residual is under
    the absolute tolerance is inside whatever its floors are. One whose largest residual is over both the
    tolerance and the ring's ceiling 2 (ε²/h²) · 2 ulp(max_k |φ_k|) - which no cell's F_k exceeds, the spacing
    of doubles never falling as the magnitude grows - has a cell outside its bound. Only what lies between has
    its F_k computed: the same answer for every ring as computing all of them, at a fraction of the cost."""
    size = np.abs(r)
    norm = size.max(axis=1)
    total = r.sum(axis=1)
    inside = norm <= RESIDUAL_TOLERANCE
    inv_h2 = (phi.shape[1] / (2.0 * math.pi)) ** 2
    ceiling = (2.0 * inv_h2) * eps2[:, 0] * (2.0 * np.spacing(np.abs(phi).max(axis=1)))
    near = np.flatnonzero(~inside & (norm <= ceiling))
    if near.size:
        inside[near] = (size[near] <= np.maximum(RESIDUAL_TOLERANCE, _floor(phi[near], eps2[near]))).all(axis=1)
    return norm, total, inside & (np.abs(total) < SUM_TOLERANCE * r.shape[1]), inside


def _newton(g, eps2, mu2, phi, max_steps: int, max_halvings: int, moving: bool):
    """Newton with step halving on one class of rings (all at rest in the frame, or all moving).

    Returns s, the diagnostics, which rings converged and, for the moving class, the cells at which each
    ring's last step was refused at the sonic line (none where it was not).
    """
    rings, n = g.shape
    inv_h2 = (n / (2.0 * math.pi)) ** 2
    steps = np.zeros(rings, dtype=int)
    halvings = np.zeros(rings, dtype=int)
    deepest = np.zeros(rings, dtype=int)
    stuck = np.zeros(rings, dtype=bool)  # a ring whose step could not be taken within the halvings: it raises
    refused = np.zeros((rings, n), dtype=bool)
    if moving:
        sonic = 0.5 * np.log(mu2 / eps2)  # φ_c = ln(|μ|/ε), shaped (rings, 1)
        subsonic = eps2 > mu2
    s, r = _state(phi, g, eps2, mu2, moving)
    for step in range(max_steps + 1):
        norm, total, converged, _ = _measure(r, phi, eps2)
        active = np.flatnonzero(~converged & ~stuck)
        if active.size == 0 or step == max_steps:
            break
        # the working arrays hold the rings still iterating, and nothing of the others
        phi_a, s_a, r_a, g_a, eps2_a, mu2_a = (_rows(a, active) for a in (phi, s, r, g, eps2, mu2))
        if moving:
            sonic_a, subsonic_a = sonic[active], subsonic[active]
            psi = phi_a - sonic_a
            slope = -np.expm1(-2.0 * psi)  # K′(ψ) = 1 − e^{−2ψ} = H′/ε²
            k_a = psi - 0.5 * slope  # K(ψ) = (H − H_sonic)/ε²
            stiff = eps2_a * slope * inv_h2  # H′/h² on the cells
            below, above = -np.roll(stiff, 1, axis=1), -np.roll(stiff, -1, axis=1)
            refused[active] = False
        else:
            stiff = eps2_a * inv_h2  # one number per ring
            below = above = -stiff
        delta = _solve_cyclic(below, s_a + 2.0 * stiff, above, -r_a)
        t = np.ones(active.size)
        pending = np.arange(active.size)
        for halving in range(max_halvings + 1):
            rows = pending
            if moving:  # the step is taken in H and read back on the base flow's branch
                linear = t[rows, None] * delta[rows]
                k_trial = k_a[rows] + slope[rows] * linear
                crossed = ~(k_trial > 0.0)  # the target on or past the sonic line (a not-a-number counts)
                reach = np.flatnonzero(~crossed.any(axis=1))
                sub = rows[reach]
                with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
                    trial = phi_a[sub] + _branch_step(psi[sub], slope[sub], linear[reach], k_trial[reach],
                                                      subsonic_a[sub])
                    side = trial - sonic_a[sub]
                    crossed[reach] = ~np.where(subsonic_a[sub], side > 0.0, side < 0.0)  # ... or there to rounding
                kept = ~crossed[reach].any(axis=1)
                inside = np.zeros(rows.size, dtype=bool)
                inside[reach[kept]] = True
                out = rows[~inside]
                refused[active[out]] = crossed[~inside]
                trial = trial[kept]
                rows = rows[inside]
            else:
                out = rows[:0]
                trial = _rows(phi_a, rows) + t[rows, None] * _rows(delta, rows)
            trial_s, trial_r = _state(trial, _rows(g_a, rows), _rows(eps2_a, rows), _rows(mu2_a, rows), moving)
            if moving:
                # "inside": every cell of the trial under max(RESIDUAL_TOLERANCE, F_k), the cell's own rule (G3 item 2)
                trial_norm, trial_total, _, trial_inside = _measure(trial_r, trial, _rows(eps2_a, rows))
                falls = (trial_norm < norm[active[rows]]) | (
                    trial_inside & (np.abs(trial_total) < np.abs(total[active[rows]]))
                )
            else:
                falls = _functional_fall(_rows(phi_a, rows), _rows(s_a, rows), _rows(g_a, rows),
                                         _rows(eps2_a, rows), _rows(delta, rows), t[rows, None]) < 0.0
            taken = active[rows[falls]]
            phi[taken], s[taken], r[taken] = trial[falls], trial_s[falls], trial_r[falls]
            deepest[taken] = np.maximum(deepest[taken], halving)
            halvings[taken] += halving
            pending = np.sort(np.concatenate((out, rows[~falls])))
            if pending.size == 0 or halving == max_halvings:
                break
            t[pending] *= 0.5
        steps[active] += 1
        if pending.size:  # the ring stays where it was and iterates no more, whatever the others do
            stuck[active[pending]] = True
            halvings[active[pending]] += max_halvings
            deepest[active[pending]] = max_halvings
    norm, total, converged, _ = _measure(r, phi, eps2)
    return s, Diagnostics(steps, halvings, deepest, norm, total, _floor(phi, eps2).max(axis=1)), converged, refused


def solve(
    forcing,  # the law's own word; the module's function of the same name builds it
    eps,
    flow=0.0,
    *,
    start=None,
    max_steps: int = MAX_NEWTON_STEPS,
    max_halvings: int = MAX_HALVINGS,
) -> tuple[np.ndarray, Diagnostics]:
    """The smooth steady response s(χ_k) of every ring to its forcing; returns ``(s, diagnostics)``.

    ``forcing`` g on the cells' centres, shaped (rings, cells), dimensionless, the sum of 1 + g over a ring
    positive (a zero mean in the model); ``eps`` ε > 0, shaped (rings,) or a scalar; ``flow`` μ = (Ω_p − Ω)/κ,
    a scalar or (rings,), 0 in the model (for one mode m in Shu, Milione & Roberts's variables on the cells
    as η: eps = √x, flow = ν). ``start`` an optional first guess of s, positive, shaped (rings, cells) - a
    continuation in the forcing starts each solve from the last; without it Newton starts from s = 1.
    ``max_steps`` and ``max_halvings`` are the fixed counts (A1); the model leaves them alone.

    Returns s shaped (rings, cells), positive, with Σ_k (s_k − 1 − g_k) = Σ_k r_k (``Diagnostics.residual_sum``)
    by the discrete equation, and a ``Diagnostics``. The cell count is the forcing's own (the model's is
    ``CELLS``).

    Raises, for the first ring (lowest row) that has not met both tolerances within the counts,
    ``SmoothBranchLost`` if its flow ≠ 0 and its last step was refused at the sound speed, and
    ``ConvergenceError`` otherwise; ``ValueError`` for inputs that pose no problem (shapes, a non-positive
    ε, a sonic base flow |μ| = ε, a ring whose 1 + g does not sum above zero, a start that is not positive
    or not on the base flow's side of the sound speed).
    """
    g = np.array(forcing, dtype=float, order="C")
    if g.ndim != 2 or g.shape[1] < 3:
        raise ValueError(f"forcing must be shaped (rings, cells) with at least 3 cells, not {g.shape}")
    rings, n = g.shape
    eps_r = np.array(np.broadcast_to(np.asarray(eps, dtype=float), (rings,)))
    mu_r = np.array(np.broadcast_to(np.asarray(flow, dtype=float), (rings,)))
    if not (np.all(np.isfinite(g)) and np.all(np.isfinite(eps_r)) and np.all(np.isfinite(mu_r))):
        raise ValueError("forcing, eps and flow must be finite")
    if np.any(eps_r <= 0.0):
        raise ValueError("eps must be positive on every ring")
    if np.any(np.abs(mu_r) == eps_r):
        raise ValueError("a base flow at the sound speed (|flow| = eps) has no smooth branch to follow")
    if np.any((1.0 + g).sum(axis=1) <= 0.0):
        raise ValueError("1 + forcing must sum above zero round every ring: the ring's mean of s is that sum")
    if start is None:
        phi = np.zeros_like(g)
    else:
        first = np.asarray(start, dtype=float)
        if first.shape != g.shape or not np.all(first > 0.0) or not np.all(np.isfinite(first)):
            raise ValueError("start must be positive, finite and shaped like the forcing")
        phi = np.log(first)
    eps2 = (eps_r * eps_r)[:, None]
    mu2 = (mu_r * mu_r)[:, None]
    through = mu_r != 0.0  # the rings the frame moves through: only they have a sonic line
    if np.any((eps2[through] - mu2[through] * np.exp(-2.0 * phi[through])) * (eps2[through] - mu2[through]) <= 0.0):
        raise ValueError("start must lie on the base flow's side of the sound speed on every cell")

    s = np.empty_like(g)
    steps = np.zeros(rings, dtype=int)
    halvings = np.zeros(rings, dtype=int)
    deepest = np.zeros(rings, dtype=int)
    norms = np.zeros(rings)
    sums = np.zeros(rings)
    floors = np.zeros(rings)
    converged = np.zeros(rings, dtype=bool)
    refused = np.zeros((rings, n), dtype=bool)
    # the rings at rest in the frame (the functional's halving, the step in φ) and the rings moving through it
    # (the residual's, the step in H) are iterated apart; a ring's arithmetic does not know the other class exists
    for moving in (False, True):
        rows = np.flatnonzero((mu_r != 0.0) == moving)
        if rows.size == 0:
            continue
        s_c, diag_c, converged_c, refused_c = _newton(
            g[rows], eps2[rows], mu2[rows], phi[rows], int(max_steps), int(max_halvings), moving
        )
        s[rows] = s_c
        steps[rows], halvings[rows], deepest[rows] = diag_c.steps, diag_c.halvings, diag_c.deepest
        norms[rows], sums[rows], floors[rows] = diag_c.residual, diag_c.residual_sum, diag_c.floor
        converged[rows], refused[rows] = converged_c, refused_c

    for ring in np.flatnonzero(~converged)[:1]:  # the first ring that failed, in the batch's order
        off = np.flatnonzero(refused[ring])
        if off.size:
            raise SmoothBranchLost(
                f"ring {ring}: the smooth branch is lost - not converged (residual {norms[ring]:.3e}) after "
                f"{steps[ring]} steps, the last refused at the sound speed on {off.size} cell(s), first cell {off[0]}",
                ring, norms[ring], steps[ring], off,
            )
        raise ConvergenceError(
            f"ring {ring}: Newton did not converge - residual {norms[ring]:.3e} (sum {sums[ring]:.3e}; the ring's "
            f"rounding floor {floors[ring]:.3e}) after {steps[ring]} steps (at most {max_steps}) and "
            f"{deepest[ring]} halvings of one step (at most {max_halvings})",
            ring, norms[ring], steps[ring],
        )
    return s, Diagnostics(steps, halvings, deepest, norms, sums, floors)


def residual(density, forcing, eps, flow=0.0) -> np.ndarray:
    """The discrete equation's residual r_k = s_k − 1 − g_k − (Φ_{k+½} − Φ_{k−½}) of a profile; (rings, cells).

    ``density`` s > 0 and ``forcing`` g shaped (rings, cells); ``eps`` and ``flow`` scalars or (rings,).
    Dimensionless. This is the number ``solve`` holds, cell by cell, under max(``RESIDUAL_TOLERANCE``, F_k)
    (:func:`rounding_floor`) - with ln s as it iterated it; here the logarithm of ``density`` is taken again,
    which can move a cell's residual by 4u ε²/h², u = 2⁻⁵³, on top.
    """
    s = np.asarray(density, dtype=float)
    g = np.asarray(forcing, dtype=float)
    eps_r = np.broadcast_to(np.asarray(eps, dtype=float), (s.shape[0],))
    mu_r = np.broadcast_to(np.asarray(flow, dtype=float), (s.shape[0],))
    eps2, mu2, phi = (eps_r * eps_r)[:, None], (mu_r * mu_r)[:, None], np.log(s)
    r = np.empty_like(phi)
    for moving in (False, True):  # as ``solve`` does: the two classes apart
        rows = np.flatnonzero((mu_r != 0.0) == moving)
        if rows.size:
            r[rows] = _state(phi[rows], g[rows], eps2[rows], mu2[rows], moving)[1]
    return r


def rounding_floor(density, eps) -> np.ndarray:
    """F_k = 2 (ε²/h²)(½ ulp(φ_{k−1}) + ulp(φ_k) + ½ ulp(φ_{k+1})), φ = ln s: each cell's rounding floor; (rings, cells).

    ``density`` s > 0 shaped (rings, cells); ``eps`` a scalar or (rings,). The bound ``solve`` holds a cell's
    residual under where it exceeds ``RESIDUAL_TOLERANCE`` (gate G3 item 2; the module's docstring): the residual
    of the exact discrete solution, rounded to doubles, is this large without the 2. Dimensionless.
    """
    s = np.asarray(density, dtype=float)
    eps_r = np.broadcast_to(np.asarray(eps, dtype=float), (s.shape[0],))
    return _floor(np.log(s), (eps_r * eps_r)[:, None])


def functional(density, forcing, eps) -> np.ndarray:
    """J = Σ_k h [ε² ((φ_{k+1} − φ_k)/h)²/2 + e^{φ_k} − (1 + g_k) φ_k], φ = ln s, on the cells; shaped (rings,).

    The μ = 0 equation is its stationary point, and it is strictly convex, so the solution is its one
    minimum. ``density`` s > 0 and ``forcing`` g shaped (rings, cells); ``eps`` a scalar or (rings,).
    Dimensionless (radians of χ times terms of order 1). The halving inside ``solve`` uses this sum's
    difference taken term by term (``_functional_fall``), not two calls of this function.
    """
    s = np.asarray(density, dtype=float)
    g = np.asarray(forcing, dtype=float)
    eps_r = np.broadcast_to(np.asarray(eps, dtype=float), (s.shape[0],))
    h = 2.0 * math.pi / s.shape[1]
    phi = np.log(s)
    d = np.roll(phi, -1, axis=1) - phi
    return h * ((0.5 / (h * h)) * (eps_r * eps_r)[:, None] * d * d + s - (1.0 + g) * phi).sum(axis=1)


# --------------------------------------------------------------------------------------------------------------
# Reading a point (D216 item 9)
# --------------------------------------------------------------------------------------------------------------


def bracket(chi, cells: int = CELLS):
    """The two cells a χ lies between and its place between them: ``(lower, upper, weight, wraps)``.

    ``chi`` in radians, any shape, any value (the ring is periodic). ``lower`` and ``upper`` are cell
    indices (upper is lower + 1, cyclic), ``weight`` in [0, 1] is the fraction of the way from the lower
    cell's centre to the upper's, and ``wraps`` counts whole turns from the first cell's centre (for
    ``sector_mean``). The interpolant is (1 − weight) · profile[lower] + weight · profile[upper].
    """
    u = (np.asarray(chi, dtype=float) + math.pi) * (cells / (2.0 * math.pi)) - 0.5
    whole = np.floor(u)
    weight = u - whole
    index = whole.astype(np.int64)
    lower = np.mod(index, cells)
    return lower, np.mod(lower + 1, cells), weight, (index - lower) // cells


def _gather(profile: np.ndarray, index: np.ndarray) -> np.ndarray:
    """profile[index] for a profile (cells,), or ring by ring for a profile (rings, cells) and index (rings, ...)."""
    if profile.ndim == 1:
        return profile[index]
    if profile.ndim != 2 or index.ndim < 1 or index.shape[0] != profile.shape[0]:
        raise ValueError("a profile shaped (rings, cells) is read at χ shaped (rings, ...): one row of χ per ring")
    rows = np.arange(profile.shape[0]).reshape((-1,) + (1,) * (index.ndim - 1))
    return profile[rows, index]


def interpolate(profile, chi) -> np.ndarray:
    """A profile at any χ: linear in χ between the cells' centres, periodic. Returns χ's shape.

    ``profile`` on the cells' centres, shaped (cells,) with ``chi`` of any shape, or (rings, cells) with
    ``chi`` shaped (rings, ...), a ring's row read by that ring's χ. ``chi`` in radians, any value. The
    result is the lesser of the two cells plus a non-negative share of their difference, so it is never
    under the profile's least cell, and nothing is clipped to make it so.
    """
    p = np.asarray(profile, dtype=float)
    x = np.asarray(chi, dtype=float)
    lower, upper, weight, _ = bracket(x, p.shape[-1])
    below, above = _gather(p, lower), _gather(p, upper)
    rising = above >= below
    return np.where(rising, below, above) + np.where(rising, weight, 1.0 - weight) * np.abs(above - below)


def sector_mean(profile, lo, hi) -> np.ndarray:
    """The exact mean of ``interpolate(profile, ·)`` over each interval [lo, hi] of χ. Returns lo's shape.

    ``profile`` shaped (cells,) with ``lo``, ``hi`` of any one shape, or (rings, cells) with them shaped
    (rings, ...). Radians; hi ≥ lo, of any width (an interval longer than 2π goes round more than once)
    and anywhere (it wraps). An interval of no width returns the interpolant there. The pieces are
    integrated as they are - the part of the first cell, the whole cells between, the part of the last -
    and divided by the interval's own width hi − lo, so sectors that tile the ring average, weighted by
    their widths, to the profile's mean to rounding: a shared edge is one number to both its sectors. An
    edge's place in its cell is known to the rounding of χ, about 1e-13 of a cell, so an interval narrower
    than 1e-3 of a cell keeps fewer than ten figures.
    """
    p = np.asarray(profile, dtype=float)
    a = np.asarray(lo, dtype=float)
    b = np.asarray(hi, dtype=float)
    if a.shape != b.shape:
        raise ValueError("lo and hi must have one shape")
    if np.any(b < a):
        raise ValueError("an interval runs from lo to hi with hi >= lo")
    cells = p.shape[-1]
    following = np.roll(p, -1, axis=-1)
    segments = 0.5 * (p + following)  # the interpolant's integral from centre k to centre k + 1, in cells
    cumulative = np.cumsum(segments, axis=-1) - segments  # ... from centre 0 to centre k
    turn = cumulative[..., -1] + segments[..., -1]  # ... over the whole ring
    k_a, next_a, w_a, wraps_a = bracket(a, cells)
    k_b, next_b, w_b, wraps_b = bracket(b, cells)
    p_a, slope_a = _gather(p, k_a), _gather(following, k_a) - _gather(p, k_a)
    p_b, slope_b = _gather(p, k_b), _gather(following, k_b) - _gather(p, k_b)
    same = (k_a == k_b) & (wraps_a == wraps_b)
    inside = (w_b - w_a) * (p_a + 0.5 * (w_b + w_a) * slope_a)  # both ends between the same two centres
    tail = (1.0 - w_a) * (p_a + 0.5 * (1.0 + w_a) * slope_a)  # from lo to the next centre
    head = w_b * (p_b + 0.5 * w_b * slope_b)  # from hi's lower centre to hi
    turns = turn if p.ndim == 1 else turn.reshape((-1,) + (1,) * (a.ndim - 1))
    # the whole segments between: from centre k_a + 1 to centre k_b, counted with the turns between them
    wrapped = next_a < k_a  # lo's next centre is the first cell of the following turn
    between = (wraps_b - wraps_a - wrapped) * turns + (_gather(cumulative, k_b) - _gather(cumulative, next_a))
    integral = np.where(same, inside, tail + between + head)
    width = (b - a) * (cells / (2.0 * math.pi))
    positive = width > 0.0
    return np.where(positive, integral / np.where(positive, width, 1.0), interpolate(p, a))
