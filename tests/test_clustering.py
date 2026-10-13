"""The two-point correlation instrument (``galaxy.specs.clustering``, S61, D220) held before it certifies a census
(rule B1): the pair counts against brute force, Poisson points, an analytic clustered field, a control drawn from
the data's own law, and the fits' arithmetic."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.specs import clustering as C


def _brute(a: np.ndarray, b: np.ndarray | None, edges: np.ndarray) -> np.ndarray:
    if b is None:
        i, j = np.triu_indices(a.shape[0], k=1)
        s = np.hypot(*(a[i] - a[j]).T)
    else:
        s = np.hypot(*(a[:, None, :] - b[None, :, :]).reshape(-1, 2).T)
    return np.histogram(s, bins=edges)[0]


def test_pair_counts_are_the_brute_force_counts():
    """The grid hash counts every pair closer than the largest edge once, auto and cross, in every bin: against
    every pair's separation computed directly, on points spread over many grid cells."""
    rng = np.random.default_rng(7)
    a = rng.uniform(-12000.0, 12000.0, (900, 2))
    b = rng.uniform(-12000.0, 12000.0, (700, 2))
    a[:60] = a[0] + rng.normal(0.0, 50.0, (60, 2))  # a tight group, so the small bins are populated
    assert np.array_equal(C.pair_counts(a), _brute(a, None, C.EDGES_PC))
    assert np.array_equal(C.pair_counts(a, b), _brute(a, b, C.EDGES_PC))


def test_poisson_points_in_an_annulus_are_unclustered():
    """Points uniform in area in an annulus, against randoms uniform in the same annulus: 1 + omega = 1 within four
    times its Poisson error in every bin, sigma^2 = 1/DD_expected + 1/RR (DD_expected = the normalised RR times the
    data's pairs), and the fitted slope within four of its standard errors of 0."""
    fp = C.Annulus(2000.0, 15000.0)
    data = fp.sample(5000, np.random.default_rng(11))
    comp = C.Comparison.uniform(fp, 25000, seed=12)
    corr = C.landy_szalay(data, comp)
    dd_expected = corr.rr / comp.rr_pairs * (corr.n_data * (corr.n_data - 1) / 2.0)
    sigma = np.sqrt(1.0 / dd_expected + 1.0 / corr.rr)
    assert np.all(np.abs(corr.one_plus_omega - 1.0) < 4.0 * sigma), (corr.one_plus_omega - 1.0) / sigma
    law = C.fit_power_law(corr)
    assert abs(law.alpha) < 4.0 * law.alpha_error, law
    assert corr.dropped == 0 and corr.n_random == 25000


def test_a_field_of_gaussian_clumps_returns_its_analytic_correlation():
    """The anchor: clumps at uniform random centres (number density n_c), each with Poisson(m) members displaced
    from its centre by an isotropic 2-D Gaussian of width sigma (a Thomas process).

    Derivation. The density of pairs at separation r is n^2 g(r). Pairs from different clumps are uncorrelated
    (Poisson centres): they give n^2. Pairs within one clump: a clump of N members holds N(N-1) ordered pairs, with
    E[N(N-1)] = m^2 for N ~ Poisson(m), and the separation of two members is the difference of two independent
    Gaussian displacements, a 2-D Gaussian of variance 2 sigma^2 per axis, density
    h(r) = exp(-r^2 / (4 sigma^2)) / (4 pi sigma^2). So the ordered-pair density is n_c m^2 h(r), and with n = n_c m,
    g(r) = 1 + n_c m^2 h(r) / (n_c m)^2 = 1 + exp(-r^2 / (4 sigma^2)) / (4 pi sigma^2 n_c).
    A bin holds the pair-weighted mean of g over the annulus [a, b]; integrating r exp(-r^2/4sigma^2) gives
    <g - 1> = (exp(-a^2/4sigma^2) - exp(-b^2/4sigma^2)) / (pi n_c (b^2 - a^2)), which is what is compared.
    The centres fill a square padded by ten sigma round the footprint, so the field is stationary inside it; the
    integral constraint (the mean density estimated from the data) shifts 1 + omega by about 1/(n_c A) = 0.0025.

    The noise: (i) the clumps' own pair numbers vary, relative cv = sqrt(Var N(N-1)) / (m^2 sqrt(N_c)) with
    Var N(N-1) = 4 m^3 + 2 m^2 for a Poisson N; (ii) the Poisson error of DD; (iii) the pairs between clumps come
    from a Poisson number of centre pairs in the bin, N_cc = N_c^2 / 2 times the bin's share of the footprint's
    area, relative error 1/sqrt(N_cc). Bins where the prediction exceeds three of those sigmas are compared, each
    within four. Measured before this test was written (three seeds, scratch): the same agreement in every bin
    with signal; without term (iii) the bins at 300-600 pc departed by up to 30 of the other two sigmas in one
    seed - the noise model, not the estimator.
    """
    sigma_pc, n_c, m, side, pad = 100.0, 1.0e-6, 20.0, 20000.0, 1000.0
    rng = np.random.default_rng(0)
    width = side + 2.0 * pad
    centres = rng.uniform(-width / 2, width / 2, (rng.poisson(n_c * width * width), 2))
    k = rng.poisson(m, centres.shape[0])
    points = np.repeat(centres, k, axis=0) + rng.normal(0.0, sigma_pc, (int(k.sum()), 2))
    fp = C.Square(0.0, 0.0, side)
    corr = C.against_uniform(points, fp, multiple=10.0, seed=100)
    a, b = C.EDGES_PC[:-1], C.EDGES_PC[1:]
    predicted = (np.exp(-a**2 / (4 * sigma_pc**2)) - np.exp(-b**2 / (4 * sigma_pc**2))) / (math.pi * n_c * (b**2 - a**2))
    n_clumps = n_c * side * side
    cv = math.sqrt(4 * m**3 + 2 * m**2) / (m * m * math.sqrt(n_clumps))
    centre_pairs = n_clumps**2 / 2.0 * math.pi * (b**2 - a**2) / (side * side)
    sigma = np.sqrt((predicted * cv) ** 2 + (1.0 + predicted) ** 2 / np.maximum(corr.dd, 1) + 1.0 / centre_pairs)
    signal = predicted > 3.0 * sigma
    assert signal.sum() >= 8, signal  # 30 pc to about 350 pc
    z = (corr.one_plus_omega - 1.0 - predicted) / sigma
    assert np.all(np.abs(z[signal]) < 4.0), z[signal]


def _exponential_disc(n: int, scale_pc: float, fp: C.Annulus, rng: np.random.Generator) -> np.ndarray:
    out = np.zeros((0, 2))
    while out.shape[0] < n:
        r = rng.gamma(2.0, scale_pc, 4 * n)  # surface density exp(-R/h): R exp(-R/h) in R
        r = r[(r >= fp.r_in_pc) & (r <= fp.r_out_pc)]
        p = rng.uniform(0.0, 2.0 * math.pi, r.size)
        out = np.vstack([out, np.column_stack([r * np.cos(p), r * np.sin(p)])])
    return out[:n]


def test_the_control_divides_out_the_law_the_data_were_drawn_from():
    """Data from an exponential disc, against a control drawn from the same disc (five times as many): 1 within four
    Poisson errors in every bin and a slope within noise of 0. Against uniform randoms the same data are not 1: the
    disc's profile is in the sources' convention. For a smooth surface density S in a footprint of area A, at
    separations small beside its scale the pairs are DD/RR -> A int S^2 dA / (int S dA)^2, a plateau (3.178 for this
    disc, by quadrature) that bends down only as (r/h)^2: so the bins to 300 pc read it within four Poisson errors.
    (The test first asserted a steep slope against uniform randoms; the measurement, -0.03 over 100-2000 pc with
    amplitude 3.1, showed a smooth profile raises the amplitude and barely tilts the slope - the expectation was
    wrong, not the estimator.)"""
    fp = C.Annulus(1000.0, 15000.0)
    rng = np.random.default_rng(21)
    data = _exponential_disc(5000, 3000.0, fp, rng)
    control = _exponential_disc(25000, 3000.0, fp, rng)
    corr = C.against_control(data, control, fp)
    dd_expected = corr.rr / (corr.n_random * (corr.n_random - 1) / 2.0) * (corr.n_data * (corr.n_data - 1) / 2.0)
    sigma = np.sqrt(1.0 / dd_expected + 1.0 / corr.rr)
    assert np.all(np.abs(corr.one_plus_omega - 1.0) < 4.0 * sigma), (corr.one_plus_omega - 1.0) / sigma
    law = C.fit_power_law(corr)
    assert abs(law.alpha) < 4.0 * law.alpha_error, law
    uniform = C.against_uniform(data, fp, multiple=5.0, seed=22)
    radius = np.linspace(fp.r_in_pc, fp.r_out_pc, 200001)
    surface = np.exp(-radius / 3000.0)
    plateau = fp.area_pc2 * np.trapezoid(surface**2 * radius, radius) * 2 * math.pi / (
        np.trapezoid(surface * radius, radius) * 2 * math.pi) ** 2
    small = uniform.r <= 300.0
    error = uniform.poisson_error
    assert np.all(np.abs(uniform.one_plus_omega[small] - plateau) < 4.0 * error[small]), (uniform.one_plus_omega, plateau)


def _synthetic(values: np.ndarray) -> C.Correlation:
    n = values.size
    ones = np.ones(n, dtype=np.int64)
    return C.Correlation(C.EDGES_PC, values, ones, ones, ones, 10, 10, 0, "synthetic", 0.0)


def test_the_fits_recover_an_exact_law():
    """The fit's arithmetic on bins that hold an exact law (the anchor above pins the estimator; this pins the fit,
    so the rejection-sampled power-law field the brief offered as a fourth test is not needed): one law recovered to
    rounding over each named range, and a broken law's break, both slopes and both amplitudes."""
    r = C.centres()
    for lo, hi in C.FIT_RANGES_PC.values():
        law = C.fit_power_law(_synthetic(3.4 * (r / 300.0) ** -0.5), lo, hi)
        assert law.alpha == pytest.approx(-0.5, abs=1e-12)
        assert law.amplitude == pytest.approx(3.4, rel=1e-12)
        assert law.scatter_dex < 1e-12
    k = 9  # the break at EDGES_PC[9], 297 pc
    values = np.where(np.arange(r.size) < k, 2.0 * (r / 300.0) ** -0.8, 2.0 * (r / 300.0) ** -0.2)
    broken = C.fit_broken(_synthetic(values), 30.0, 5000.0)
    assert broken is not None and broken.break_pc == pytest.approx(C.EDGES_PC[k])
    assert broken.inner.alpha == pytest.approx(-0.8, abs=1e-12) and broken.outer.alpha == pytest.approx(-0.2, abs=1e-12)
    assert broken.inner.amplitude == pytest.approx(2.0) and broken.outer.amplitude == pytest.approx(2.0)


def test_the_bins_and_footprints():
    """Twenty logarithmic bins from 30 pc to 5 kpc, geometric centres; randoms uniform in area inside each footprint."""
    assert C.EDGES_PC.size == 21 and C.EDGES_PC[0] == pytest.approx(30.0) and C.EDGES_PC[-1] == pytest.approx(5000.0)
    assert np.allclose(np.diff(np.log(C.EDGES_PC)), math.log(5000.0 / 30.0) / 20)
    fp = C.Annulus(4000.0, 12000.0)
    pts = fp.sample(200000, np.random.default_rng(3))
    assert fp.contains(pts).all()
    r = np.hypot(*pts.T)
    # Uniform in area: the share inside radius x is (x^2 - R_in^2) / (R_out^2 - R_in^2).
    assert np.mean(r < 8000.0) == pytest.approx((8000.0**2 - 4000.0**2) / (12000.0**2 - 4000.0**2), abs=5e-3)
    sq = C.solar_pointing(8.2)
    assert sq.contains(sq.sample(1000, np.random.default_rng(4))).all() and sq.area_pc2 == pytest.approx(3.6e7)
