"""The gas fluctuation field (galaxy.layer.gas_fluctuation; S62, D221 part I). The arithmetic built at the first
hand-back: one noise with L1's, the amplitude ladder and its normaliser, the break's octave index, the shear's strain.
The stage, the width, the per-cell normaliser, the vectors and the gate's spectra wait on the lead's ruling (the
module docstring says why)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.layer import census_clustering as l1
from galaxy.layer import gas_fluctuation as gf
from galaxy.layer import noise
from galaxy.models import level0

SCALE = 0.19
L1_OCTAVES, L1_SLOPE = 3, 1.53
OCTAVES = 6


def constant(name: str) -> float:
    return float(level0.LEVEL0[name].value)


def test_l1_s_numbers_are_the_model_s():
    assert constant("CENSUS_CLUSTERING_SCALE") == SCALE
    assert constant("CENSUS_CLUSTERING_OCTAVES") == L1_OCTAVES
    assert constant("CENSUS_CLUSTERING_SPECTRAL_SLOPE") == L1_SLOPE


@pytest.mark.parametrize("dtype", [np.float64, np.float32])
def test_the_three_coarse_octaves_are_l1_s_values_to_the_bit(dtype):
    """D221 item 1: the same lattice, the same seed path, the same values. L1's octave sum rebuilt from this field's
    octave terms with L1's own weights is ``noise.fractal``'s, bit for bit, at points across the disc."""
    seed = gf.field_seed(20261014)
    assert seed == l1.field_seed(20261014)
    rng = np.random.default_rng(62)
    pts = rng.uniform(-20.0, 20.0, size=(4096, 2))
    terms = gf.octave_terms(seed, pts, SCALE, OCTAVES, dtype)
    ft = np.dtype(dtype).type
    gain, top, norm = noise.octave_weights(L1_SLOPE, L1_OCTAVES, 2.0, 2)
    a, total = ft(1.0), np.zeros(len(pts), dtype=ft)
    for j in range(L1_OCTAVES):
        if j == L1_OCTAVES - 1:
            a = ft(a * ft(top))
        total = total + a * terms[j]
        a = ft(a * ft(gain))
    expected = noise.fractal(seed, pts, L1_SLOPE, L1_OCTAVES, base_frequency=1.0 / SCALE, dtype=dtype)
    assert np.array_equal(total * ft(norm), expected)


@pytest.mark.parametrize("slope", [1.53, 2.53])
def test_the_ladder_without_a_change_is_octave_weights(slope):
    """A ladder whose every step has one slope is ``noise.octave_weights``' sum: break index N at s, 0 at s + 1."""
    for break_index, s in ((OCTAVES, slope), (0, slope - 1.0)):
        if s <= 0.0:
            continue
        amps, norm = gf.ladder_weights(s, 1.0, OCTAVES, break_index)
        gain, top, ref_norm = noise.octave_weights(slope, OCTAVES, 2.0, 2)
        expected = [gain**j for j in range(OCTAVES)]
        expected[-1] *= top
        assert np.allclose(amps, expected, rtol=1e-14, atol=0.0)
        assert norm == pytest.approx(ref_norm, rel=1e-14)


def test_the_ladder_s_gains_change_by_one_power_at_the_break():
    """Steps above the break at L^((2 - s)/2), below at L^((2 - s - 1)/2): their ratio is L^-1/2 (one power in P)."""
    amps, _ = gf.ladder_weights(L1_SLOPE, 1.0, OCTAVES, 2)
    steps = [amps[j] / amps[j - 1] for j in range(1, OCTAVES - 1)]
    assert steps[0] == pytest.approx(2.0 ** ((2.0 - L1_SLOPE) / 2.0), rel=1e-14)
    for step in steps[1:]:
        assert step == pytest.approx(2.0 ** ((2.0 - L1_SLOPE - 1.0) / 2.0), rel=1e-14)


@pytest.mark.parametrize("break_index", [0, 2, 4, 6])
def test_the_ladder_s_sum_has_unit_variance_measured(break_index):
    """The normaliser derived (``norm^2 sum a_j^2 = 1`` at every point) against a direct measurement: 2^17 points
    spread over a 200 kpc square, about a thousand coarsest cells across. Measured 0.9939, 1.0069, 1.0011, 0.9990
    (standard error about 0.004); asserted within 0.015."""
    amps, norm = gf.ladder_weights(L1_SLOPE, 1.0, OCTAVES, break_index)
    assert norm**2 * math.fsum(a * a for a in amps) == pytest.approx(1.0, rel=1e-14)
    pts = np.random.default_rng(break_index).uniform(-100.0, 100.0, size=(2**17, 2))
    g = gf.gaussian_sum(7, pts, SCALE, amps, norm)
    assert g.var() == pytest.approx(1.0, abs=0.015)
    assert abs(g.mean()) < 0.015


def test_the_break_octave_counts_the_octaves_whose_wavelength_is_not_below_pi_h():
    """Scales 190, 95, 47.5, 23.75, 11.875, 5.9375 pc; each carries the wavelength 4 l_j (the lead's ruling 2) and the
    index is how many of those are not below pi h. The literal mapping (``wavelength=1``) is kept as the comparison
    the module docstring measures."""
    scales = gf.octave_scales_pc(SCALE, OCTAVES)
    assert np.allclose(scales, [190.0, 95.0, 47.5, 23.75, 11.875, 5.9375])
    assert gf.OCTAVE_WAVELENGTH == 4.0
    assert gf.break_octave(355.0 / math.pi, SCALE, OCTAVES) == 2  # R_SUN on the default galaxy: pi h 355 pc
    assert gf.break_octave(81.0 / math.pi, SCALE, OCTAVES) == 4  # R = 1 kpc: pi h 81 pc
    assert gf.break_octave(990.0 / math.pi, SCALE, OCTAVES) == 0  # R = 12 kpc: the whole band below pi h
    assert gf.break_octave(380.0 / math.pi, SCALE, OCTAVES) == 2  # a wavelength equal to pi h is not below it
    assert gf.break_octave(355.0 / math.pi, SCALE, OCTAVES, wavelength=1.0) == 0  # the literal mapping
    assert gf.break_octave(81.0 / math.pi, SCALE, OCTAVES, wavelength=1.0) == 2
    assert gf.break_octave(1.0, SCALE, OCTAVES) == 6
    with pytest.raises(ValueError):
        gf.break_octave(float("nan"), SCALE, OCTAVES)


def test_the_strain_is_minus_two_where_the_shear_time_is_not_capped():
    """dOmega/dlnR = -2A: on a flat curve A = Omega / 2, so 1/A = 2R/v; the strain is -2 below the cap and -2 A cap
    above it. Also the identity on a curve that is not flat, numerically."""
    R = np.linspace(0.5, 20.0, 400)
    v = 220.0 * np.ones_like(R)
    a = gf.oort_a(R, v)
    assert np.allclose(a, 0.5 * v / R, rtol=1e-12)
    strain, t = gf.shear_strain(a, 30.0)
    short = 1.0 / (a * gf.KM_S_PER_KPC_IN_PER_MYR) <= 30.0
    assert short.any() and (~short).any()
    assert np.allclose(strain[short], -2.0, atol=1e-12)
    assert np.allclose(strain[~short], -2.0 * a[~short] * gf.KM_S_PER_KPC_IN_PER_MYR * 30.0, rtol=1e-12)
    assert np.all(strain >= -2.0 - 1e-12) and np.all(strain < 0.0)
    v = 250.0 * np.tanh(R / 2.5)
    omega = v / R
    domega_dlnr = np.gradient(omega, np.log(R))
    inner = slice(5, -5)
    assert np.allclose(domega_dlnr[inner], -2.0 * gf.oort_a(R, v)[inner], rtol=2e-3)
