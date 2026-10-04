"""The instrument for the gas's steady response (S57, D216 gate G2, item 10; rule B1: built before its user).

``galaxy.stages.gas_response`` solves, ring by ring, d/dχ[(ε² − μ²/s²) d ln s/dχ] = s − 1 − g on the smooth
branch. Nothing in the model calls it yet. What certifies it, each written so that it could fail:

(a) **Sormani et al. 2017's no-shock threshold** (the reading's Part A row G, Part C C1.3 and C2 "S6"). Their
    units F_y = Ω = 1, L = 1, κ = 2Ω, base flow u_x = 1/2, c_s = 0.7, Φ = Φ₀ cos 2πx; the mapping, re-derived
    here from their eqs. 13-14 (`u_y′ = −2 + 1/u_x`, `u_x′ = (2u_y − Φ′)/(u_x − c_s²/u_x)`): with η = 2πx − π,
    s = 1/(2u_x), w = π u_x and v = π u_y they are (w − x/w) w′ = v − f sin η, v′ = s − 1 with
    ν = −π/2, x = (π c_s)² = 4.836, f = π² Φ₀; their x = 0, the potential's maximum, is η = ±π. The published
    Φ_c = 0.07297 is f_c = 0.7202. **Measured at 1440 cells: f_c = 0.7202298** (Φ_c = 0.0729745), the bracket
    closed to 3e-9, first contact on the two cells either side of η = ±π; 0.7202510 at 720 cells, so second
    order, and Richardson's value 0.7202228 is Φ_c = 0.0729738, the published five figures.
(b) **The linear limit, by hand**: s − 1 = f cos η/(1 − ν² + x), and to second order
    + f² (x − 3ν²) cos 2η / [(1 − ν² + x)² (1 + 4(x − ν²))] (derived in the test's own comments).
(c) **The two hard rings against the differential equation**, with derivatives the module does not use (FFT),
    against uniform potential vorticity, and against a dense Newton written here.
(d) the mean identity; (e) J's minimum; (f) batches, bits, and the two errors; (g) the cell count;
(h) the cost. A second published threshold, Shu, Milione & Roberts 1973's base-subsonic ring at 14 kpc
(F_cusp = 3.7 %, the reading's Part A row C), is read as an extra: 3.65 %.

**Measured in S57 (this machine, numpy 2.5.2), pinned below.** Five modes m = 2..6,
f = (0.08, 0.37, 0.49, 0.62, 0.72), ε = 0.072: trough 0.00732, crest 3.0227, 7 Newton steps, no halving,
residual 4e-13. Total forcing 2.1 (f = (0.706, 0.126, 0.366, 0.102, 0.800)): trough 0.00100, crest 2.4395,
7 steps. The solver's discretisation error at 1440 cells 3.2e-5 and 2.7e-5 of the mean (falling 4.00-fold
per doubling); linear interpolation between centres adds 1.96e-4 and 1.54e-4 at the midpoints, h²/8 · max|s″|
to four figures - twice D216 item 9's expected 1e-4. 400 rings of 1440 cells: 0.5-0.7 s.
"""

from __future__ import annotations

import inspect
import math
import time
from decimal import Decimal, getcontext

import numpy as np
import pytest

from galaxy.stages import gas_response as gr

MODES = np.array([2, 3, 4, 5, 6])
EPS = 0.072
# the two hard rings (D216's probe: five modes at 6 kpc; a total forcing of 2.1 with a trough of 0.001)
FIVE = (np.array([[0.08, 0.37, 0.49, 0.62, 0.72]]), np.array([[2.625, 1.405, 1.356, 2.462, 2.914]]))
HEAVY = (np.array([[0.706, 0.126, 0.366, 0.102, 0.800]]), np.array([[2.111, 0.971, 6.179, 0.193, 0.447]]))
HARD = {"five modes": FIVE, "total 2.1": HEAVY}

SORMANI_NU = -math.pi / 2.0
SORMANI_X = (math.pi * 0.7) ** 2


# --------------------------------------------------------------------------------------------------------------
# tools the module does not have
# --------------------------------------------------------------------------------------------------------------


def spectral(values: np.ndarray, order: int) -> np.ndarray:
    """A periodic sample's derivative of the given order by FFT (order −1: the integral of its zero-mean part)."""
    n = values.size
    k = np.fft.rfftfreq(n, d=1.0 / n)
    weight = np.zeros(k.size, dtype=complex)
    if order < 0:
        weight[1:] = 1.0 / (1j * k[1:])
    else:
        weight = (1j * k) ** order
        if order % 2 and n % 2 == 0:
            weight[-1] = 0.0  # the Nyquist mode has no odd derivative on the sample
    return np.fft.irfft(np.fft.rfft(values) * weight, n)


def shifted(values: np.ndarray, shift: float) -> np.ndarray:
    """The sample's trigonometric interpolant at χ_k + shift: exact to rounding for a resolved profile."""
    n = values.size
    k = np.fft.rfftfreq(n, d=1.0 / n)
    c = np.fft.rfft(values) * np.exp(1j * k * shift)
    if n % 2 == 0:
        c[-1] = c[-1].real * math.cos(k[-1] * shift)
    return np.fft.irfft(c, n)


def hard(name: str, cells: int = gr.CELLS):
    f, theta = HARD[name]
    g = gr.forcing(MODES, f, theta, cells)
    s, diagnostics = gr.solve(g, EPS)
    return g, s, diagnostics


def threshold(nu: float, x: float, rise: float, cells: int = gr.CELLS, rises: int = 80, halvings: int = 24):
    """The largest f whose smooth solution exists: f rises in steps of ``rise`` from the last solution until
    the branch is lost, then the bracket is bisected ``halvings`` times. Every solve starts from the last
    smooth solution; the counts are fixed. Returns (f_lo, f_hi, s at f_lo, the most steps a smooth solve took).
    """
    cosine = np.cos(gr.cell_centres(cells))[None, :]
    eps = math.sqrt(x)
    f_lo, s_lo, f_hi, most = 0.0, np.ones((1, cells)), None, 0
    for _ in range(rises):
        try:
            s, diagnostics = gr.solve((f_lo + rise) * cosine, eps, nu, start=s_lo)
        except gr.SmoothBranchLost:
            f_hi = f_lo + rise
            break
        f_lo, s_lo, most = f_lo + rise, s, max(most, diagnostics.worst_steps)
    assert f_hi is not None, "the branch was never lost"
    for _ in range(halvings):
        f = 0.5 * (f_lo + f_hi)
        try:
            s, diagnostics = gr.solve(f * cosine, eps, nu, start=s_lo)
        except gr.SmoothBranchLost:
            f_hi = f
            continue
        f_lo, s_lo, most = f, s, max(most, diagnostics.worst_steps)
    return f_lo, f_hi, s_lo, most


# --------------------------------------------------------------------------------------------------------------
# the law's helpers
# --------------------------------------------------------------------------------------------------------------


def test_the_cells_and_the_laws_helpers():
    chi = gr.cell_centres()
    assert gr.CELLS == 1440 and chi.shape == (1440,)
    h = 2.0 * math.pi / 1440
    assert chi[0] == pytest.approx(-math.pi + 0.5 * h, abs=1e-15) and chi[-1] == pytest.approx(math.pi - 0.5 * h)
    assert np.allclose(np.diff(chi), h, rtol=0, atol=1e-14)
    assert np.allclose(gr.cell_centres(8), -math.pi + (np.arange(8) + 0.5) * math.pi / 4)

    # f_m = m A_m / (X sin p): by hand, m = 4, A = 0.1, X = 7.93 (D215's anchor at 7.99 kpc), sin p = 0.2341
    f = gr.forcing_amplitudes([2, 4], [[0.05, 0.1], [0.0, 0.2]], [7.93, 3.0], 0.2341)
    assert f.shape == (2, 2)
    assert f[0, 1] == pytest.approx(4 * 0.1 / (7.93 * 0.2341), rel=1e-15)
    assert f[0, 0] == pytest.approx(2 * 0.05 / (7.93 * 0.2341), rel=1e-15)
    assert f[1, 0] == 0.0 and f[1, 1] == pytest.approx(4 * 0.2 / (3.0 * 0.2341), rel=1e-15)
    assert gr.forcing_amplitudes([2, 4], [0.05, 0.1], 7.93, 0.2341).shape == (2,)  # one ring's modes stay (modes,)
    assert gr.forcing_amplitudes([2, 4], [0.05, 0.1], [7.93, 3.0, 2.0], [0.2, 0.2, 0.3]).shape == (3, 2)

    # ε = a / (κ R sin p): 6 km/s over 37 km/s/kpc × 8 kpc × 0.2341
    assert gr.epsilon(6.0, 37.0, 8.0, 0.2341) == pytest.approx(6.0 / (37.0 * 8.0 * 0.2341), rel=1e-15)
    assert gr.epsilon(6.0, np.array([37.0, 20.0]), np.array([8.0, 15.0]), 0.2341).shape == (2,)

    g = gr.forcing(MODES, *FIVE)
    by_hand = sum(FIVE[0][0, j] * np.cos(MODES[j] * chi - FIVE[1][0, j]) for j in range(5))
    assert g.shape == (1, 1440) and np.allclose(g[0], by_hand, rtol=0, atol=1e-15)
    assert abs(g.mean()) < 1e-16  # a whole number of periods over equal cells
    assert gr.forcing(MODES, np.vstack([FIVE[0], HEAVY[0]]), FIVE[1][0]).shape == (2, 1440)  # one phase set for all


# --------------------------------------------------------------------------------------------------------------
# (a) the published threshold
# --------------------------------------------------------------------------------------------------------------


def test_sormani_2017_no_shock_threshold():
    """f_c = 0.7202 ± 0.0001 at (ν, x) = (−1.5708, 4.836), first sonic contact at η = ±π (D216 item 10)."""
    assert SORMANI_NU == pytest.approx(-1.5708, abs=5e-5) and SORMANI_X == pytest.approx(4.836, abs=5e-4)
    f_lo, f_hi, s, most = threshold(SORMANI_NU, SORMANI_X, rise=0.05)
    print(f"Sormani threshold at 1440 cells: f_c in [{f_lo:.10f}, {f_hi:.10f}], Phi_c = {f_lo / math.pi**2:.7f}, "
          f"most steps of a smooth solve {most}")
    assert f_hi - f_lo < 1e-8
    assert abs(f_lo - 0.7202) < 1e-4  # the ruled criterion; π² × 0.07297 = 0.72018
    assert f_lo == pytest.approx(0.7202298, abs=2e-7)  # the measured value, pinned
    assert most <= 60  # 41 measured: Newton slows as the corner forms, and stays inside the counts

    # the flow is subsonic everywhere, and nearest the sound speed on the two cells either side of η = ±π
    sonic = abs(SORMANI_NU) / math.sqrt(SORMANI_X)
    assert sonic == pytest.approx(1.0 / 1.4, rel=1e-12)  # u_x = c_s: s = (1/2)/0.7
    margin = s[0] - sonic
    assert margin.min() > 0.0
    order = np.argsort(margin)
    assert set(order[:2].tolist()) == {0, gr.CELLS - 1}
    assert abs(abs(gr.cell_centres()[order[0]]) - math.pi) < 2.0 * math.pi / gr.CELLS
    assert margin[0] == pytest.approx(margin[-1], rel=1e-6)  # the solution is even about the minimum
    assert margin.min() < 1e-5  # ... and it has reached the line: the margin closes as (f_c − f)^½

    # just past it the branch is lost, from the solution just under it; well under it, it is a solution
    cosine = np.cos(gr.cell_centres())[None, :]
    with pytest.raises(gr.SmoothBranchLost) as lost:
        gr.solve(f_hi * cosine, math.sqrt(SORMANI_X), SORMANI_NU, start=s)
    assert set(lost.value.cells.tolist()) <= {0, 1, gr.CELLS - 2, gr.CELLS - 1} and lost.value.ring == 0

    # second order in the cells, and the published five figures in the limit
    f_720 = threshold(SORMANI_NU, SORMANI_X, rise=0.05, cells=720)[0]
    richardson = f_lo - (f_720 - f_lo) / 3.0
    print(f"at 720 cells {f_720:.10f}; Richardson {richardson:.7f}, Phi_c = {richardson / math.pi**2:.7f}")
    assert f_720 == pytest.approx(0.7202510, abs=2e-7)
    assert round(richardson / math.pi**2, 5) == 0.07297
    assert round(f_lo / math.pi**2, 5) == 0.07297


def test_shu_milione_roberts_base_subsonic_cusp_at_14_kpc():
    """An extra, not the gate's: SMR 1973 Figs. 5-6, F_cusp = 3.7 % with the cusp at η = ±180° (two figures).

    From their printed ϖ = 14 kpc, Ω = 15.5, κ = 15.0 km/s/kpc, i = 8.4°, Ω_p = 13.5, a = 8 km/s, m = 2 and
    their definitions ν = m(Ω_p − Ω)/κ, x = (m a/(κ ϖ sin i))², f = (Ω/κ)² m F / sin i. The prediction was
    written before the number was read: 3.7 ± 0.1 (the label's last figure and the inputs' rounding).
    Measured 3.65 %.
    """
    sin_i = math.sin(math.radians(8.4))
    nu = 2.0 * (13.5 - 15.5) / 15.0
    x = (2.0 * 8.0 / (15.0 * 14.0 * sin_i)) ** 2
    per_force = (15.5 / 15.0) ** 2 * 2.0 / sin_i
    f_lo, f_hi, s, _ = threshold(nu, x, rise=0.02, halvings=18)
    cusp = 100.0 * f_lo / per_force
    print(f"SMR 14 kpc: nu = {nu:.5f}, x = {x:.5f}, f_cusp = {f_lo:.6f}, F_cusp = {cusp:.4f} %")
    assert abs(cusp - 3.7) < 0.1
    assert cusp == pytest.approx(3.6525, abs=2e-3)
    nearest = int(np.argmin(s[0] - abs(nu) / math.sqrt(x)))
    assert nearest in (0, gr.CELLS - 1)


# --------------------------------------------------------------------------------------------------------------
# (b) the linear limit, by hand
# --------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("nu", "x"),
    [(0.0, SORMANI_X), (SORMANI_NU, SORMANI_X), (0.0, 0.145), (-0.72, 0.197)],
    ids=["at rest, Sormani's x", "Sormani's flow", "at rest, x = 0.145", "base-supersonic"],
)
def test_linear_limit_derived_by_hand(nu, x):
    """Small f: s − 1 = f cos η / (1 − ν² + x), and the departure is second order.

    By hand, from [(x − ν²/s²) φ′]′ = e^φ − 1 − f cos η with φ = f φ₁ + f² φ₂: H(φ) = xφ + ν² e^{−2φ}/2
    = const + (x − ν²) φ + ν² φ² + ..., so at order f, (x − ν²) φ₁″ = φ₁ − cos η: φ₁ = c cos η,
    c = 1/(1 − ν² + x). At order f², (x − ν²) φ₂″ + ν² (φ₁²)″ = φ₂ + φ₁²/2 with φ₁² = c² (1 + cos 2η)/2:
    φ₂ = −c²/4 − c² (2ν² + ¼) cos 2η / (1 + 4(x − ν²)), and s − 1 = φ + φ²/2 gives the second-order
    density c₂ cos 2η, c₂ = c² (x − 3ν²) / (1 + 4(x − ν²)), with no constant: the mean stays 1.

    The cells add their own share, first order in f: their second difference of cos η is −λ cos η,
    λ = (2 − 2 cos h)/h², so they answer f cos η / (1 + (x − ν²) λ), off the limit by f c² (x − ν²) h²/12.
    """
    eta = gr.cell_centres()
    h = 2.0 * math.pi / gr.CELLS
    c = 1.0 / (1.0 - nu * nu + x)
    c2 = c * c * (x - 3.0 * nu * nu) / (1.0 + 4.0 * (x - nu * nu))
    lam = (2.0 - 2.0 * math.cos(h)) / (h * h)
    departure, on_cells, beyond = {}, {}, {}
    for f in (1e-3, 1e-4):
        s, _ = gr.solve(f * np.cos(eta)[None, :], math.sqrt(x), nu)
        departure[f] = np.abs(s[0] - 1.0 - f * c * np.cos(eta)).max()
        cells_own = f * np.cos(eta) / (1.0 + (x - nu * nu) * lam)
        on_cells[f] = np.abs(s[0] - 1.0 - cells_own).max()
        beyond[f] = np.abs(s[0] - 1.0 - cells_own - f * f * c2 * np.cos(2.0 * eta)).max()
    share = c * c * abs(x - nu * nu) * h * h / 12.0  # the cells' first-order share, per unit f
    print(f"nu = {nu:.4f}, x = {x:.4f}: departure {departure[1e-3]:.4e} -> {departure[1e-4]:.4e} "
          f"(ratio {departure[1e-3] / departure[1e-4]:.2f}); on the cells' own limit {on_cells[1e-3]:.4e} -> "
          f"{on_cells[1e-4]:.4e} (ratio {on_cells[1e-3] / on_cells[1e-4]:.2f}); past second order "
          f"{beyond[1e-3]:.2e}, {beyond[1e-4]:.2e}")
    # the limit itself: at f = 1e-4 the response is the hand-derived one to a part in a thousand of its
    # amplitude (7e-4 on the base-supersonic ring, which sits by the n = 2 resonance 1 + 4(x − ν²) = 0), and
    # what departs is the second-order term and the cells' share, both by hand
    assert departure[1e-4] < 1e-3 * (1e-4 * abs(c))
    for f in (1e-3, 1e-4):
        assert departure[f] == pytest.approx(f * f * abs(c2) + f * share, rel=0.02)
    # second order: 100-fold from f = 1e-3 to 1e-4 once the cells' first-order share is taken out. Against the
    # continuous limit the fall is 78 to 100-fold at 1440 cells (measured 78.0, 88.2, 97.8, 100.2), and it is
    # the predicted one: D216 item 10's "100-fold" is the limit of fine cells.
    predicted = (1e-6 * abs(c2) + 1e-3 * share) / (1e-8 * abs(c2) + 1e-4 * share)
    assert departure[1e-3] / departure[1e-4] == pytest.approx(predicted, rel=0.01)
    assert on_cells[1e-3] / on_cells[1e-4] == pytest.approx(100.0, rel=0.01)
    # ... and the second-order term is the hand-derived one: what is left is third order
    assert beyond[1e-3] < 0.01 * 1e-6 * abs(c2)
    assert on_cells[1e-3] == pytest.approx(1e-6 * abs(c2), rel=0.01)


# --------------------------------------------------------------------------------------------------------------
# (c) the hard rings, checked without the module's own derivative
# --------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(("name", "trough", "crest"), [("five modes", 0.00732, 3.0227), ("total 2.1", 0.00100, 2.4395)])
def test_hard_rings_against_the_differential_equation(name, trough, crest):
    """ε² (ln s)″ = s − 1 − g by FFT, uniform potential vorticity, and a dense Newton written here.

    The tolerance is the discretisation's order, not a number chosen: the cells solve ε² D²φ = s − 1 − g with
    D²φ = φ″ + (h²/12) φ⁗ + O(h⁴), so on the returned profile ε² φ″ − (s − 1 − g) = −(h²/12) ε² φ⁗
    = −(h²/12)(s − g)″ to O(h⁴), and its integral ε² φ′ − (v − G) = −(h²/12)(s − g)′, with v′ = s − 1 the
    tangential velocity of uniform potential vorticity and G′ = g.
    """
    g, s, diagnostics = hard(name)
    f, theta = HARD[name]
    assert f.sum() == pytest.approx({"five modes": 2.28, "total 2.1": 2.1}[name], abs=1e-12)
    assert s.min() == pytest.approx(trough, abs=1e-5) and s.max() == pytest.approx(crest, abs=1e-4)
    assert diagnostics.worst_steps == 7 and diagnostics.worst_halvings == 0  # measured; the maxima are 120 and 30
    assert diagnostics.worst_residual < 1e-10

    h = 2.0 * math.pi / gr.CELLS
    chi = gr.cell_centres()
    phi = np.log(s[0])
    spectrum = np.abs(np.fft.rfft(phi))
    assert spectrum[-5:].max() < 1e-13 * spectrum[1:].max()  # ln s is resolved: the FFT's derivative is exact

    equation = EPS**2 * spectral(phi, 2) - (s[0] - 1.0 - g[0])
    leading = -(h * h / 12.0) * spectral(s[0] - g[0], 2)
    print(f"{name}: ODE residual by FFT {np.abs(equation).max():.4e}, the cells' truncation "
          f"{np.abs(leading).max():.4e}, remainder {np.abs(equation - leading).max():.3e}")
    assert np.abs(equation).max() < 1.01 * np.abs(leading).max()  # 1.2e-4: second order, and no more
    assert np.abs(equation - leading).max() < 1e-3 * np.abs(leading).max()  # what is left is fourth order

    # uniform potential vorticity, directly: v′ = s − 1 integrated, and the normal equation ε² (ln s)′ = v − ∫g
    v = spectral(s[0] - 1.0, -1)
    potential = sum(f[0, j] * np.sin(MODES[j] * chi - theta[0, j]) / MODES[j] for j in range(MODES.size))
    normal = EPS**2 * spectral(phi, 1) - (v - potential)
    leading = -(h * h / 12.0) * spectral(s[0] - g[0], 1)
    print(f"{name}: first integral {np.abs(normal).max():.4e}, truncation {np.abs(leading).max():.4e}")
    assert np.abs(normal).max() < 1.01 * np.abs(leading).max()  # 1.0e-5
    assert np.abs(normal - leading).max() < 1e-3 * np.abs(leading).max()

    # the oracle: a dense Newton on the same cells, with a matrix built here and LAPACK's solve
    n = gr.CELLS
    identity = np.eye(n)
    laplacian = (np.roll(identity, 1, axis=1) + np.roll(identity, -1, axis=1) - 2.0 * identity) / (h * h)
    dense = np.zeros(n)
    for _ in range(40):
        mismatch = EPS**2 * laplacian @ dense - np.exp(dense) + 1.0 + g[0]
        if np.abs(mismatch).max() < 1e-12:
            break
        dense = dense - np.linalg.solve(EPS**2 * laplacian - np.diag(np.exp(dense)), mismatch)
    assert np.abs(mismatch).max() < 1e-12
    print(f"{name}: against the dense Newton {np.abs(s[0] - np.exp(dense)).max():.2e}")
    assert np.abs(s[0] - np.exp(dense)).max() < 1e-9

    # the published residual is the module's own, and the diagnostics report it
    assert np.abs(gr.residual(s, g, EPS)).max() == diagnostics.residual[0]


# --------------------------------------------------------------------------------------------------------------
# (d) the mean, by the equation
# --------------------------------------------------------------------------------------------------------------


def test_the_ring_mean_is_one_by_the_equation():
    rng = np.random.default_rng(57)
    amplitudes = rng.uniform(0.0, 0.7, (50, 5))
    phases = rng.uniform(0.0, 2.0 * math.pi, (50, 5))
    eps = rng.uniform(0.05, 0.2, 50)
    g = gr.forcing(MODES, amplitudes, phases)
    s, diagnostics = gr.solve(g, eps)
    error = np.abs(s.mean(axis=1) - 1.0)
    print(f"50 random rings: mean error {error.max():.2e}, troughs {s.min():.2e}..{s.min(axis=1).max():.3f}, "
          f"steps {diagnostics.steps.min()}..{diagnostics.steps.max()}, residual {diagnostics.worst_residual:.1e}")
    assert error.max() < 1e-12
    assert s.min() > 0.0 and diagnostics.worst_residual < 1e-10
    assert diagnostics.worst_steps <= 10 and diagnostics.worst_halvings == 0
    for name in HARD:
        assert abs(hard(name)[1].mean() - 1.0) < 1e-12

    # it is the equation that sets it: a forcing whose mean is 0.1 has a ring mean of 1.1
    lifted, _ = gr.solve(g[:5] + 0.1, eps[:5])
    assert np.abs(lifted.mean(axis=1) - 1.1).max() < 1e-12
    # ... and the sum the diagnostics carry is that identity
    assert np.allclose(diagnostics.residual_sum, (s - 1.0 - g).sum(axis=1), rtol=0, atol=1e-11)

    # nothing in the module takes a mean or divides by one
    source = inspect.getsource(gr)
    for forbidden in (".mean(", "np.mean", "np.average", "np.clip", ".clip(", "np.maximum(s", "np.minimum(s"):
        assert forbidden not in source, forbidden


# --------------------------------------------------------------------------------------------------------------
# (e) the functional
# --------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", list(HARD))
def test_the_solution_is_the_functionals_minimum(name):
    g, s, _ = hard(name)
    j = gr.functional(s, g, EPS)[0]
    chi = gr.cell_centres()
    rng = np.random.default_rng(216)
    rises = []
    for k in range(10):  # ten fixed perturbations of ln s: smooth ones, large and small, and cell-to-cell noise
        if k < 6:
            wave = sum(rng.normal() * np.cos(m * chi - rng.uniform(0, 2 * math.pi)) for m in range(1, 9))
            perturbed = s * np.exp(10.0 ** (-k / 2.0) * wave / 8.0)
        else:
            perturbed = s * np.exp(10.0 ** (3 - k) * 1e-2 * rng.normal(size=chi.size))
        rises.append(gr.functional(perturbed, g, EPS)[0] - j)
    print(f"{name}: J = {j:.9f}; rises {min(rises):.3e} .. {max(rises):.3e}")
    assert min(rises) > 0.0

    # the halving's term-by-term difference is the same functional
    delta = 0.3 * np.cos(3.0 * chi)[None, :]
    fall = gr._functional_fall(np.log(s), s, g, np.array([[EPS**2]]), delta, np.array([[0.5]]))[0]
    assert fall * (2.0 * math.pi / gr.CELLS) == pytest.approx(gr.functional(s * np.exp(0.5 * delta), g, EPS)[0] - j, rel=1e-9)


# --------------------------------------------------------------------------------------------------------------
# (f) batches, bits, and the two errors
# --------------------------------------------------------------------------------------------------------------


def test_a_ring_does_not_know_its_batch():
    """Same inputs, same bits; and a ring's bits are its own, wherever and with whomever it is solved."""
    rng = np.random.default_rng(1973)
    amplitudes = rng.uniform(0.0, 0.7, (24, 5))
    amplitudes[5] = HEAVY[0][0]
    amplitudes[17] = 0.02 * amplitudes[17]  # a nearly linear ring: it stops iterating early
    g = gr.forcing(MODES, amplitudes, rng.uniform(0.0, 2.0 * math.pi, (24, 5)))
    eps = rng.uniform(0.05, 0.2, 24)
    flow = np.zeros(24)
    flow[[3, 11, 20]] = (-0.02, 0.3, 0.03)  # three rings the frame moves through (one base-supersonic)
    eps[11] = 0.1
    g[[3, 11, 20]] *= 0.05
    s, diagnostics = gr.solve(g, eps, flow)
    assert len(set(diagnostics.steps.tolist())) > 2  # the rings do stop at different steps

    again, diagnostics_again = gr.solve(g, eps, flow)
    assert np.array_equal(s, again) and np.array_equal(diagnostics.steps, diagnostics_again.steps)
    assert np.array_equal(diagnostics.residual, diagnostics_again.residual)

    for ring in range(24):  # alone
        alone, d = gr.solve(g[ring:ring + 1], eps[ring:ring + 1], flow[ring:ring + 1])
        assert np.array_equal(alone[0], s[ring]), ring
        assert d.steps[0] == diagnostics.steps[ring] and d.residual[0] == diagnostics.residual[ring]
        assert d.halvings[0] == diagnostics.halvings[ring] and d.residual_sum[0] == diagnostics.residual_sum[ring]
    order = rng.permutation(24)  # shuffled
    shuffled, _ = gr.solve(g[order], eps[order], flow[order])
    assert np.array_equal(shuffled, s[order])
    part = np.array([20, 2, 5, 11])  # a part of the batch
    assert np.array_equal(gr.solve(g[part], eps[part], flow[part])[0], s[part])
    # the moving rings are solutions of their own equation, on their own side of the sound speed
    assert np.abs(gr.residual(s, g, eps, flow)).max() < 1e-10
    assert np.all(s[11] < 0.3 / 0.1) and np.all(s[3] > 0.02 / eps[3])


def test_far_starts_reach_the_same_solution_through_the_halving():
    g, s, _ = hard("total 2.1")
    chi = gr.cell_centres()
    starts = {
        "the other hard ring": hard("five modes")[1],
        "e^(8 cos 3χ)": np.exp(8.0 * np.cos(3.0 * chi))[None, :],
        "e^(−30 (1 + cos 5χ))": np.exp(-30.0 * (1.0 + np.cos(5.0 * chi)))[None, :],
    }
    halved = 0
    for name, start in starts.items():
        other, diagnostics = gr.solve(g, EPS, start=start)
        print(f"from {name}: {diagnostics.steps[0]} steps, {diagnostics.halvings[0]} halvings "
              f"({diagnostics.deepest[0]} of one step), {np.abs(other - s).max():.2e} from the solution")
        assert np.abs(other - s).max() < 1e-10  # one solution: the functional is strictly convex
        assert diagnostics.worst_steps <= 30 and diagnostics.worst_halvings <= 8  # 13, 3 at most measured
        halved += int(diagnostics.halvings[0])
    assert halved > 0  # the halving was exercised: from above a full step would raise J


def test_a_ring_that_does_not_converge_raises():
    g_easy = gr.forcing([2], [[0.1]], [0.0])
    g = np.vstack([g_easy, hard("five modes")[0], g_easy])
    with pytest.raises(gr.ConvergenceError) as failure:
        gr.solve(g, EPS, max_steps=4)  # the easy rings take 4 steps, the hard one 7
    assert failure.value.ring == 1 and failure.value.steps == 4 and failure.value.residual > 1e-10
    assert isinstance(failure.value, gr.GasResponseError) and "ring 1" in str(failure.value)
    assert gr.solve(g, EPS, max_steps=7)[1].worst_steps == 7  # and with the steps it needs, it returns

    far = np.exp(-30.0 * (1.0 + np.cos(5.0 * gr.cell_centres())))[None, :]
    with pytest.raises(gr.ConvergenceError):
        gr.solve(g[1:2], EPS, start=far, max_halvings=0)  # a step that must be halved, and may not be
    with pytest.raises(gr.ConvergenceError):
        gr.solve(g[1:2], EPS, max_steps=0)


def test_the_loss_of_the_smooth_branch_is_raised_not_returned():
    cosine = np.cos(gr.cell_centres())[None, :]
    eps = math.sqrt(SORMANI_X)
    sonic = abs(SORMANI_NU) / eps
    under, diagnostics = gr.solve(0.70 * cosine, eps, SORMANI_NU)  # from s = 1, 3 % under the threshold
    assert under.min() > sonic and diagnostics.worst_residual < 1e-10
    assert abs(under.mean() - 1.0) < 1e-12
    for f in (0.75, 1.0):  # past it, from s = 1 and from the solution under it
        for start in (None, under):
            with pytest.raises(gr.SmoothBranchLost) as lost:
                gr.solve(f * cosine, eps, SORMANI_NU, start=start)
            assert lost.value.cells.size > 0 and lost.value.residual > 1e-10
            assert np.all(np.abs(np.abs(gr.cell_centres()[lost.value.cells]) - math.pi) < 0.3)  # at the maximum
    # in a batch the ring that lost its branch is named, and the rings at rest are untouched by it
    with pytest.raises(gr.SmoothBranchLost) as lost:
        gr.solve(np.vstack([0.5 * cosine, 0.75 * cosine]), eps, np.array([0.0, SORMANI_NU]))
    assert lost.value.ring == 1


def test_inputs_that_pose_no_problem_are_refused():
    g = gr.forcing([2], [[0.1]], [0.0])
    with pytest.raises(ValueError):
        gr.solve(g[0], EPS)  # one ring is still (1, cells)
    with pytest.raises(ValueError):
        gr.solve(g, 0.0)
    with pytest.raises(ValueError):
        gr.solve(g, EPS, EPS)  # a base flow at the sound speed
    with pytest.raises(ValueError):
        gr.solve(g - 1.0, EPS)  # 1 + g sums to nothing: no positive s has that mean
    with pytest.raises(ValueError):
        gr.solve(g, EPS, start=np.zeros_like(g))
    with pytest.raises(ValueError):
        gr.solve(g, 1.0, 0.5, start=np.full_like(g, 0.4))  # a start on the other side of the sound speed (0.5)
    with pytest.raises(ValueError):
        gr.solve(np.full_like(g, np.nan), EPS)


# --------------------------------------------------------------------------------------------------------------
# (g) the cell count, and reading a point
# --------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(("name", "solver", "between"), [("five modes", 3.22e-5, 1.959e-4), ("total 2.1", 2.69e-5, 1.536e-4)])
def test_convergence_with_the_cell_count_and_the_point_error(name, solver, between):
    """Second order: 4-fold per doubling. The 1440-cell errors, each on its own, pinned (D216 item 9).

    The common points are the 720 cells' centres; a finer profile is read there by its trigonometric
    interpolant, exact to rounding for these resolved profiles, so the differences are the solver's alone.
    """
    profiles = {cells: hard(name, cells)[1][0] for cells in (720, 1440, 2880)}

    def at_720_centres(cells):
        if cells == 720:
            return profiles[720]
        ratio = cells // 720  # a coarse centre is the fine face between fine cells ratio·k + ratio/2 − 1 and the next
        return shifted(profiles[cells], math.pi / cells)[ratio // 2 - 1 + ratio * np.arange(720)]

    common = {cells: at_720_centres(cells) for cells in profiles}
    coarse = np.abs(common[720] - common[1440]).max()
    fine = np.abs(common[1440] - common[2880]).max()
    estimate = 4.0 / 3.0 * fine  # Richardson: the 1440-cell solution's own error
    h = 2.0 * math.pi / gr.CELLS
    middle = gr.interpolate(profiles[1440], gr.cell_centres() + 0.5 * h)
    reading = np.abs(middle - shifted(profiles[1440], 0.5 * h))  # linear against the profile's own interpolant
    curvature = h * h / 8.0 * np.abs(spectral(profiles[1440], 2)).max()
    print(f"{name}: |s720 − s1440| = {coarse:.4e}, |s1440 − s2880| = {fine:.4e}, ratio {coarse / fine:.3f}; "
          f"solver error at 1440 = {estimate:.3e}; linear interpolation at the midpoints {reading.max():.4e} "
          f"(h²/8 max|s″| = {curvature:.4e}; {np.max(reading / middle):.2e} of the local s)")
    assert coarse / fine == pytest.approx(4.0, abs=0.05)
    assert estimate == pytest.approx(solver, rel=0.01)
    assert reading.max() == pytest.approx(between, rel=0.01)
    assert reading.max() == pytest.approx(curvature, rel=0.01)  # a chord's sag under a parabola
    assert reading.max() < 2.5e-4  # D216 item 9 expected about 1e-4: it is twice that (reported, not tuned)


def test_interpolation_is_linear_periodic_and_never_under_the_least_cell():
    _, s, _ = hard("five modes")
    profile = s[0]
    chi = gr.cell_centres()
    h = 2.0 * math.pi / gr.CELLS
    assert np.allclose(gr.interpolate(profile, chi), profile, rtol=1e-12, atol=0)  # the centres are the cells
    rng = np.random.default_rng(9)
    weight = rng.uniform(0.0, 1.0, gr.CELLS)
    blend = (1.0 - weight) * profile + weight * np.roll(profile, -1)
    assert np.allclose(gr.interpolate(profile, chi + weight * h), blend, rtol=1e-13, atol=0)
    anywhere = rng.uniform(-40.0, 40.0, 20000)
    values = gr.interpolate(profile, anywhere)
    assert values.min() >= profile.min() and values.max() <= profile.max() * (1 + 1e-15)
    assert np.allclose(values, gr.interpolate(profile, anywhere + 2.0 * math.pi), rtol=1e-10, atol=0)  # periodic
    assert np.allclose(values, gr.interpolate(profile, anywhere - 6.0 * math.pi), rtol=1e-10, atol=0)
    # across the seam at ±π the interpolant runs between the last cell and the first
    assert gr.interpolate(profile, math.pi) == pytest.approx(0.5 * (profile[-1] + profile[0]), rel=1e-12)
    assert gr.interpolate(profile, -math.pi) == pytest.approx(0.5 * (profile[-1] + profile[0]), rel=1e-12)

    # the pieces a caller indexes with itself
    lower, upper, share, _ = gr.bracket(anywhere)
    assert np.all((share >= 0.0) & (share <= 1.0)) and np.array_equal(upper, (lower + 1) % gr.CELLS)
    assert np.allclose((1.0 - share) * profile[lower] + share * profile[upper], values, rtol=1e-13, atol=0)

    # several rings, each read at its own χ
    rings = np.vstack([profile, hard("total 2.1")[1][0], np.ones(gr.CELLS)])
    points = rng.uniform(-math.pi, math.pi, (3, 7, 5))
    together = gr.interpolate(rings, points)
    assert together.shape == (3, 7, 5)
    for ring in range(3):
        assert np.array_equal(together[ring], gr.interpolate(rings[ring], points[ring]))
    assert np.all(together[2] == 1.0)
    with pytest.raises(ValueError):
        gr.interpolate(rings, points[:2])


def test_sector_means_are_the_interpolants_exact_means():
    _, s, _ = hard("five modes")
    profile = s[0]
    rng = np.random.default_rng(10)
    two_pi = 2.0 * math.pi

    # sectors that tile the ring average to the profile's mean - whatever their number and wherever they start
    for sectors, offset in ((32, 0.0), (32, 0.4321), (7, -2.0), (1440, 0.001), (1, 3.0), (2880, 0.0), (5, 100.0)):
        edges = offset + two_pi * np.arange(sectors + 1) / sectors
        means = gr.sector_mean(profile, edges[:-1], edges[1:])
        assert means.min() >= profile.min()
        assert abs(means.sum() / sectors - profile.mean()) < 5e-15 * profile.mean(), (sectors, offset)
    cuts = np.sort(rng.uniform(0.0, two_pi, 40))  # unequal sectors, weighted by their widths
    edges = np.concatenate([cuts, cuts[:1] + two_pi]) - 1.234
    means = gr.sector_mean(profile, edges[:-1], edges[1:])
    assert abs((means * np.diff(edges)).sum() / two_pi - profile.mean()) < 1e-14 * profile.mean()

    # against the interpolant itself, summed finely (midpoints: exact for a piecewise-linear function but for
    # the pieces a corner falls in)
    lo = rng.uniform(-10.0, 10.0, 30)
    hi = lo + rng.uniform(0.0, 1.0, 30) ** 3 * 9.0
    exact = gr.sector_mean(profile, lo, hi)
    samples = 200_000
    for k in range(30):
        points = lo[k] + (np.arange(samples) + 0.5) * (hi[k] - lo[k]) / samples
        assert exact[k] == pytest.approx(gr.interpolate(profile, points).mean(), rel=2e-9), (lo[k], hi[k])

    # an interval inside one piece is the interpolant at its middle; one of no width is the interpolant there
    h = two_pi / gr.CELLS
    a = gr.cell_centres()[100] + 0.2 * h
    assert gr.sector_mean(profile, a, a + 0.5 * h) == pytest.approx(gr.interpolate(profile, a + 0.25 * h), rel=1e-13)
    # a narrow one keeps what its ends' rounding leaves: they are known to 1e-13 of a cell, so 1e-3 of a cell
    # is good to 1e-10 (the integral is over the nominal width, which is what makes tiling sectors sum exactly)
    assert gr.sector_mean(profile, a, a + 1e-3 * h) == pytest.approx(gr.interpolate(profile, a + 5e-4 * h), rel=1e-8)
    assert gr.sector_mean(profile, a, a) == gr.interpolate(profile, a)
    # more than once round: the whole turns count
    assert gr.sector_mean(profile, -1.0, -1.0 + 3 * two_pi) == pytest.approx(profile.mean(), rel=1e-14)
    # a flat profile's mean is the profile, to the edges' rounding over the width (in cells)
    flat = gr.sector_mean(np.full(gr.CELLS, 2.5), lo, hi)
    assert np.all(np.abs(flat / 2.5 - 1.0) * (hi - lo) / h < 5e-12)
    with pytest.raises(ValueError):
        gr.sector_mean(profile, 1.0, 0.5)

    # several rings, each with its own sectors
    rings = np.vstack([profile, hard("total 2.1")[1][0]])
    edges = np.array([[0.3], [-1.1]]) + two_pi * np.arange(33) / 32
    together = gr.sector_mean(rings, edges[:, :-1], edges[:, 1:])
    assert together.shape == (2, 32)
    for ring in range(2):
        assert np.array_equal(together[ring], gr.sector_mean(rings[ring], edges[ring, :-1], edges[ring, 1:]))
    assert np.abs(together.mean(axis=1) - rings.mean(axis=1)).max() < 1e-14


# --------------------------------------------------------------------------------------------------------------
# the pieces
# --------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("n", [3, 4, 5, 6, 9, 12, 45, 48, 90, 720, 1440])
def test_the_cyclic_tridiagonal_solve_against_a_dense_one(n):
    rng = np.random.default_rng(n)
    rings = 4
    below, above = -rng.uniform(0.5, 2.0, (rings, n)), -rng.uniform(0.5, 2.0, (rings, n))
    diagonal = -(below + above) + rng.uniform(1e-3, 3.0, (rings, n))  # dominant, as the solver's matrices are
    right = rng.normal(size=(rings, n))
    x = gr._solve_cyclic(below, diagonal, above, right)
    direct = gr._thomas_cyclic(below, diagonal, above, right)
    for ring in range(rings):
        matrix = np.diag(diagonal[ring])
        for k in range(n):
            matrix[k, (k - 1) % n] += below[ring, k]
            matrix[k, (k + 1) % n] += above[ring, k]
        dense = np.linalg.solve(matrix, right[ring])
        assert np.allclose(x[ring], dense, rtol=1e-9, atol=1e-11)
        assert np.allclose(direct[ring], dense, rtol=1e-9, atol=1e-11)
    # one number per ring off the diagonal, as the rings at rest pass it
    constant = gr._solve_cyclic(below[:, :1], diagonal - below + below[:, :1], below[:, :1], right)
    again = gr._solve_cyclic(np.repeat(below[:, :1], n, axis=1), diagonal - below + below[:, :1],
                             np.repeat(below[:, :1], n, axis=1), right)
    assert np.array_equal(constant, again)


def test_the_step_taken_in_h_against_exact_arithmetic():
    """K(ψ + Δ) − K(ψ) = K′(ψ) ℓ on ψ's own branch, to rounding, against 50-digit arithmetic."""
    getcontext().prec = 50

    def k_of(p):
        return p + ((-2 * p).exp() - 1) / 2

    rng = np.random.default_rng(14)
    cases = []
    for sign in (1.0, -1.0):
        for _ in range(150):
            psi = sign * 10.0 ** rng.uniform(-8.0, 0.5)
            cases.append((psi, rng.choice([-1.0, 1.0]) * abs(psi) * 10.0 ** rng.uniform(-12.0, 0.8)))
    psi = np.array([c[0] for c in cases])[:, None]
    linear = np.array([c[1] for c in cases])[:, None]
    slope = -np.expm1(-2.0 * psi)
    target = (psi - 0.5 * slope) + slope * linear
    on_branch = target[:, 0] > 0.0
    assert 150 < on_branch.sum() < 300  # the rest aim past the sonic line: the solver refuses those before this
    step = gr._branch_step(psi[on_branch], slope[on_branch], linear[on_branch], target[on_branch], psi[on_branch] > 0.0)
    worst = 0.0
    for (p, ell), got in zip([c for c, keep in zip(cases, on_branch) if keep], step[:, 0]):
        p, ell = Decimal(p), Decimal(ell)
        aim = k_of(p) + (1 - (-2 * p).exp()) * ell
        q = (aim.sqrt() + aim) if p > 0 else -(1 + 2 * aim + 2 * aim.sqrt()).ln() / 2
        for _ in range(120):
            q = q - (k_of(q) - aim) / (1 - (-2 * q).exp())
        exact = float(q - p)
        assert (float(p) + got) * float(p) > 0.0  # the same branch
        worst = max(worst, abs(got - exact) / max(abs(float(q)), abs(exact)))
    print(f"the step in H: worst error {worst:.2e} of the larger of the step and the new ψ")
    assert worst < 1e-6  # near the line the error is absolute, 2e-16: of the order of φ's own rounding


# --------------------------------------------------------------------------------------------------------------
# (h) the cost
# --------------------------------------------------------------------------------------------------------------


def test_cost_of_four_hundred_rings():
    """Not asserted on the clock (rule B6: publish the number): 0.5-0.7 s here for 400 rings of 1440 cells."""
    rng = np.random.default_rng(400)
    radius = np.linspace(0.0, 1.0, 400)[:, None]
    envelope = np.exp(-(((radius - 0.45) / 0.3) ** 2))  # the forcing peaks mid-disc, as the probe's table does
    amplitudes = envelope * rng.uniform(0.2, 0.7, (400, 5))
    g = gr.forcing(MODES, amplitudes, rng.uniform(0.0, 2.0 * math.pi, (400, 5)))
    eps = rng.uniform(0.05, 0.2, 400)
    gr.solve(g[:2], eps[:2])  # warm
    started = time.perf_counter()
    s, diagnostics = gr.solve(g, eps)
    elapsed = time.perf_counter() - started
    print(f"400 rings x 1440 cells: {elapsed:.2f} s; total forcing up to {amplitudes.sum(axis=1).max():.2f}; "
          f"steps {diagnostics.steps.min()}..{diagnostics.steps.max()} (mean {diagnostics.steps.mean():.1f}), "
          f"halvings {diagnostics.worst_halvings}; residual {diagnostics.worst_residual:.1e}; "
          f"mean error {np.abs(s.mean(axis=1) - 1.0).max():.1e}; s {s.min():.2e}..{s.max():.2f}")
    assert s.shape == (400, 1440) and s.min() > 0.0
    assert diagnostics.worst_residual < 1e-10 and np.abs(s.mean(axis=1) - 1.0).max() < 1e-12
    assert diagnostics.worst_steps <= 12 and diagnostics.worst_halvings == 0  # the counts' maxima are 120 and 30
