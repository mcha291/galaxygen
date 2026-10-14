"""The spectrum instrument (galaxy.specs.spectrum; S62, D221 part I items 8-9): built and tested before the gas
fluctuation field it certifies (rule B1). Every expectation here is computable without the instrument: a white
field's flat level, the slope ``noise.fractal`` was asked for (``octave_weights``' docstring derives it), and a
Gaussian field drawn with an exact broken spectrum."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.layer import noise
from galaxy.specs import spectrum as sp

N = 512
TWO_PI = 2.0 * math.pi


def unit_square(n: int = N) -> np.ndarray:
    x = (np.arange(n) + 0.5) / n
    return np.stack(np.meshgrid(x, x, indexing="xy"), axis=-1)


def broken_law(k_break: float, alpha_low: float, alpha_high: float):
    return lambda k: np.where(k < k_break, (k / k_break) ** alpha_low, (k / k_break) ** alpha_high)


def test_the_normalisation_is_parseval_s():
    """Known: the sum of P over the modes times one mode's area is the windowed field's variance (the module's
    normalisation), and a white field of variance v reads P = v d^2 / (4 pi^2) on average over its modes."""
    field = 2.0 * np.random.default_rng(3).standard_normal((N, N))
    spacing = 0.5
    kx, ky, power = sp.power_spectrum(field, spacing)
    w = sp.hann(N)
    windowed = (field - field.mean()) * np.outer(w, w)
    variance = float(np.mean(windowed**2)) / float(np.mean(w * w)) ** 2
    assert power.sum() * (TWO_PI / (N * spacing)) ** 2 == pytest.approx(variance, rel=1e-12)
    s = sp.measure(field, spacing)
    level = float((s.power * s.modes).sum() / s.modes.sum()) * 4.0 * math.pi**2 / spacing**2
    assert level == pytest.approx(4.0, rel=0.03)  # measured 4.04, 4.04, 4.01 on three seeds


def test_white_noise_reads_flat():
    """Known: alpha = 0. Measured -0.027 +- 0.024 over the 34 bins above the third (one seed)."""
    s = sp.measure(np.random.default_rng(1).standard_normal((N, N)), 1.0 / N)
    fit = sp.fit_power_law(s, s.k[2], s.k[-1])
    assert abs(fit.alpha) < 0.08, fit


@pytest.mark.parametrize("slope", [1.53, 2.53])
def test_a_fractal_reads_minus_the_slope_it_was_asked_for(slope):
    """Known: alpha = -slope over the fractal's band (``noise.fractal``: base frequency to a quarter of the finest
    octave's; 7 octaves from 4 to 256 cells on the unit square, band 4 to 64 cycles), four seeds stacked.
    Measured -1.511 and -2.499 (single seeds -1.42 to -1.60 and -2.37 to -2.60)."""
    pts = unit_square()
    spectra = [sp.measure(noise.fractal(seed, pts, slope, 7, base_frequency=4.0), 1.0 / N) for seed in range(4)]
    fit = sp.fit_power_law(sp.stack(spectra), TWO_PI * 4, TWO_PI * 64)
    assert fit.alpha == pytest.approx(-slope, abs=0.1), fit


@pytest.mark.parametrize("alpha_low, alpha_high", [(-1.53, -2.53), (-2.5, -1.0)])
def test_a_broken_spectrum_returns_both_slopes_and_its_break(alpha_low, alpha_high):
    """Known: a periodic Gaussian field drawn with an exact continuous broken law (``gaussian_field``), the break at
    20 cycles across the patch, two seeds stacked, fitted over 3 to 200 cycles. Measured: -1.557 / -2.497 with the
    break at 0.93 of the true one; -2.597 / -0.990 at 0.99. The break is asserted within an octave (D221 item 8's
    tolerance), the slopes within 0.15."""
    k_break = TWO_PI * 20
    law = broken_law(k_break, alpha_low, alpha_high)
    spectra = [sp.measure(sp.gaussian_field(N, 1.0 / N, law, seed), 1.0 / N) for seed in range(2)]
    fit = sp.fit_broken(sp.stack(spectra), TWO_PI * 3, TWO_PI * 200)
    assert fit.alpha_low == pytest.approx(alpha_low, abs=0.15), fit
    assert fit.alpha_high == pytest.approx(alpha_high, abs=0.15), fit
    assert 0.5 < fit.k_break / k_break < 2.0, fit
    assert fit.wavelength_break == pytest.approx(TWO_PI / fit.k_break)


def test_the_instrument_refuses_what_it_does_not_measure():
    with pytest.raises(sp.SpectrumError):
        sp.measure(np.zeros((8, 9)), 1.0)
    with pytest.raises(sp.SpectrumError):
        sp.measure(np.zeros((8, 8)), 0.0)
    s = sp.measure(np.random.default_rng(0).standard_normal((64, 64)), 1.0)
    with pytest.raises(sp.SpectrumError):
        sp.fit_power_law(s, s.k[0], s.k[1])
