"""The gas fluctuation field (galaxy.layer.gas_fluctuation; S62, D221 part I as the lead amended it): its arithmetic
(one noise with L1's, the ladder and its normaliser, the break's index, the strain), the stage, the evaluator, the
vectors and the gate (D221 item 8: (a) spectra, (b) width, (c) anisotropy, (d) unit mean per cell; (e) and (f) are
held here and in test_layer / test_clustering_gate), every measured number beside its prediction."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.registry import production
from galaxy.layer import census_clustering as l1
from galaxy.layer import compose
from galaxy.layer import gas_fluctuation as gf
from galaxy.layer import noise
from galaxy.models import DEFAULT, level0
from galaxy.run import run

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


# --- the stage, the evaluator and the gate (D221 item 8 as the lead amended it) ------------------------------------

FIELD_NAMES = (gf.GAS_FLUCTUATION_SEED.name, *gf.RING_KEYS, gf.GAS_FLUCTUATION_CELL_NORMALISER.name)
TWO_PI = 2.0 * math.pi


@pytest.fixture(scope="module")
def default_run():
    """The default galaxy, layer on and off, restricted to the field and what it reads."""
    models, _, _ = production()
    model = models.get(DEFAULT) if isinstance(DEFAULT, str) else DEFAULT
    names = (*FIELD_NAMES, "gas_scale_height", "circular_velocity", "pitch_angle")
    constants = {k: v.value for k, v in model.constants.items()}
    return {layer: run(model, only=names, layer=layer) for layer in (True, False)}, constants


@pytest.fixture(scope="module")
def field(default_run):
    runs, constants = default_run
    return compose.gas_fluctuation(runs[True].fields, constants, runs[True].grid.R)


# The default galaxy's rings as the stage publishes them (S62, D221; measured): the break index, the strain.
BREAKS = [4, 4, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1] + [0] * 20
STRAINS = {0: -2.0, 1: -2.0, 2: -1.808, 8: -1.043, 11: -0.793, 31: -0.231}


def test_the_stage_publishes_its_ring_table_and_is_neutral_layer_off(default_run, field):
    """Ruling 1: M = 6 km/s over the CNM's 0.675 km/s (70 K, mu 1.27) = 8.90, sigma 0.501 on every ring; the break
    table under ruling 2 (rings 25-31 hold ring 24's, ruling 3); the strain -2 on the two rings the cap does not
    bind; NaN with the layer off, every row kept; the evaluator 1 with the layer off."""
    runs, constants = default_run
    on, off = runs[True].fields, runs[False].fields
    assert np.asarray(on["gas_fluctuation_break_octave"]).tolist() == BREAKS
    assert np.allclose(on["gas_fluctuation_mach"], 8.8953, atol=1e-4)
    assert np.allclose(on["gas_fluctuation_sigma"], 0.50097, atol=1e-5)
    strain = np.asarray(on["gas_fluctuation_strain"])
    for ring, value in STRAINS.items():
        assert strain[ring] == pytest.approx(value, abs=1e-3), ring
    assert on[gf.GAS_FLUCTUATION_SEED.name] == gf.field_seed(int(runs[True].inputs["texture_seed"]))
    for name in FIELD_NAMES:
        assert np.all(np.isnan(np.asarray(off[name], dtype=float))), name
        assert np.shape(off[name]) == np.shape(on[name]), name
    assert compose.gas_fluctuation(off, constants, runs[False].grid.R) is None
    x = np.array([8.2, 1.0, -3.0])
    assert np.array_equal(gf.evaluate(off, constants, runs[False].grid.R, x, x), np.ones(3))
    assert np.all(gf.evaluate(on, constants, runs[True].grid.R, x, x) > 0.0)


def test_the_polar_read_is_the_cartesian_read_to_rounding(field):
    """``gaussian_polar`` (the cell table's path) and ``gaussian`` (the evaluator's) read the same positions."""
    rng = np.random.default_rng(5)
    R, phi = rng.uniform(7.6, 8.4, 2000), rng.uniform(0.0, TWO_PI, 2000)
    a = field.gaussian_polar(R, phi, 8)
    b = field.gaussian(R * np.cos(phi), R * np.sin(phi), 8)
    assert np.allclose(a, b, rtol=0.0, atol=1e-9)


def test_d_unit_mean_in_every_cell_on_its_lattice(default_run, field):
    """Gate (d): the map times the published cell normaliser has R-weighted mean 1 over every level-0 cell's lattice
    (L1's table lattice), to 1e-12. Measured: worst |mean - 1| 4.4e-16 over the 1 024 cells."""
    from galaxy.stages.systems import CELL_RINGS, CELL_SECTORS

    _, constants = default_run
    points, f1 = int(constants["CENSUS_CLUSTERING_TABLE_POINTS"]), gf.l1_finest_frequency(constants)
    worst = 0.0
    for r in range(CELL_RINGS):
        q = np.stack([field.cell_lattice(r, s, points, f1) for s in range(CELL_SECTORS)])
        g = field.gaussian_polar(q[..., 0], q[..., 1], r)
        sigma = field.sigma[r]
        norm = field.cell_normaliser[r * CELL_SECTORS:(r + 1) * CELL_SECTORS, None]
        m = norm * np.exp(sigma * g - 0.5 * sigma * sigma)
        mean = (m * q[..., 0]).sum(axis=-1) / q[..., 0].sum(axis=-1)
        worst = max(worst, float(np.max(np.abs(mean - 1.0))))
    assert worst < 1e-12, worst


@pytest.mark.parametrize("ring", [1, 8, 11])
def test_b_the_map_s_width_is_the_relation_s(field, ring):
    """Gate (b): the variance of ln(map) over 200 000 points spread uniformly in area over the ring equals
    sigma^2 = 0.11 ln(1 + M^2 / 9) = 0.2510 within 10 %. Measured: ring 1 0.2446, ring 8 0.2467, ring 11 0.2462 (2.5, 1.7, 1.9 % low)
    (the cell normalisers' own spread is in it: ln(normaliser) has variance 0.0028 over the 1 024 cells, 0.80-1.27)."""
    rng = np.random.default_rng(ring)
    lo, hi = field.edges[ring], field.edges[ring + 1]
    R = np.sqrt(rng.uniform(lo * lo, hi * hi, 200_000))
    phi = rng.uniform(0.0, TWO_PI, R.size)
    values = field.evaluate(R * np.cos(phi), R * np.sin(phi))
    expected = 0.11 * math.log1p((8.8953152 / 3.0) ** 2)
    assert expected == pytest.approx(field.sigma[ring] ** 2, rel=1e-6)
    measured = float(np.log(values).var())
    print(f"ring {ring}: var ln(map) {measured:.4f} against {expected:.4f}")
    assert measured == pytest.approx(expected, rel=0.10)


def local_gradient_moment(field, ring: int, half: float = 0.2, n: int = 800, along_sense: float | None = None) -> np.ndarray:
    """The covariance of the field's gradient in each point's own frame (x along the rotation, y outward) on a patch
    about (R_ring, 0): the autocorrelation's curvature at zero lag, the tensor ``noise.shear_anisotropy`` derives.
    ``along_sense`` +1 takes x along +phi instead (the review's frame, finding 1); by default x is along the rotation,
    the field's own ``sense`` times +phi."""
    R0 = 0.5 * (field.edges[ring] + field.edges[ring + 1])
    step = 2.0 * half / n
    u = (np.arange(n) + 0.5) * step - half
    X, Y = np.meshgrid(R0 + u, u, indexing="xy")
    g = field.gaussian(X, Y, ring)
    gy, gx = np.gradient(g, step)
    phi = np.arctan2(Y, X)
    sense = field.sense if along_sense is None else along_sense
    along = sense * (-np.sin(phi) * gx + np.cos(phi) * gy)  # d/d(R phi) times the sense: along the rotation
    out = np.cos(phi) * gx + np.sin(phi) * gy  # d/dR
    return np.array([[np.mean(along * along), np.mean(along * out)], [np.mean(along * out), np.mean(out * out)]])


@pytest.mark.parametrize("ring", [1, 8, 11])
def test_c_the_anisotropy_is_the_ring_s_own_strain_s(field, ring):
    """Gate (c): the gradient covariance's axis ratio sqrt(l+/l-) and its major axis against ``shear_anisotropy`` at
    the ring's strain: 5.83 at -2 (ring 1), 2.72 at -1.043 (ring 8), 2.17 at -0.793 (ring 11). In the disc's own
    frame, x along the rotation (towards -phi): self-consistent and blind to the sense, which the test after this one
    holds (S62's review, finding 1). Measured (a 0.4 kpc patch at 0.5 pc): 5.516, 2.734, 2.176; the major axis 65.9, 58.0, 55.3 degrees against 67.5, 58.8, 55.8
    (5.589, 2.709, 2.182 and 66.2, 58.3, 55.1 before the sense was mended: the same noise read at mirrored positions)."""
    moment = local_gradient_moment(field, ring)
    values, vectors = np.linalg.eigh(moment)
    ratio = math.sqrt(values[1] / values[0])
    tilt = math.atan2(vectors[1, 1], vectors[0, 1])
    want_ratio, want_tilt = noise.shear_anisotropy(float(field.strain[ring]))
    turn = (tilt - want_tilt + math.pi / 2) % math.pi - math.pi / 2
    print(f"ring {ring}: ratio {ratio:.3f} against {want_ratio:.3f}, tilt {math.degrees(tilt):.1f} against {math.degrees(want_tilt):.1f}")
    assert ratio == pytest.approx(want_ratio, rel=0.10)
    assert abs(math.degrees(turn)) < 3.0


@pytest.mark.parametrize("ring", [1, 8, 11])
def test_the_field_s_structures_trail_as_the_arms_do(default_run, field, ring):
    """S62's review, finding 1: the elongation's sense follows the arms' winding. The disc turns towards
    ``rotation_sense`` (read off the arms' winding: their azimuth grows outward, so they trail and the disc turns
    towards -phi), and material further out lags, so a sheared structure's azimuth moves *against* the rotation going
    outward: d(phi)/dR has the sign of ``-rotation_sense`` - the arms' own. The autocorrelation's major axis (its
    zero-lag curvature: the gradient covariance's minor eigenvector) in (along +phi, outward) must therefore have
    components of product sign ``-rotation_sense``, derived here, not written in. Measured after the fix (rings 1, 8,
    11): (+0.91, +0.41), (+0.85, +0.53), (+0.82, +0.57) - 24.3, 31.9 and 34.8 degrees off +phi (the shear's 22.5,
    31.2 and 34.2 from the rotation's direction, mirrored into +phi); the first build read (-0.93, +0.37), (-0.90, +0.44), (-0.78, +0.62) by the
    autocorrelation's half-maximum in the same frame (the review's), the structures leading."""
    from galaxy.stages.pattern import rotation_sense

    runs, _ = default_run
    sense = rotation_sense(float(runs[True].fields["pitch_angle"]))
    assert field.sense == sense
    moment = local_gradient_moment(field, ring, along_sense=1.0)
    values, vectors = np.linalg.eigh(moment)
    major = vectors[:, 0] * math.copysign(1.0, vectors[1, 0])  # the structures' long axis, pointing outward
    print(f"ring {ring}: the long axis in (+phi, outward) ({major[0]:+.2f}, {major[1]:+.2f}); rotation_sense {sense:+.0f}")
    assert math.copysign(1.0, major[0] * major[1]) == -sense
    assert abs(major[0]) > 0.2  # an axis well off the radial, so the sign is the shear's and not the noise's


def patch_spectra(ring_break: int, R: float, seeds: int = 3) -> list:
    """The ring's unsheared octave sum on a flat 4 x 4 kpc patch at 2.9 pc (1376^2), one spectrum per seed (100 on)."""
    from galaxy.specs import spectrum as sp

    n, side = 1376, 4.0
    d = side / n
    x = (np.arange(n) + 0.5) * d
    pts = np.stack(np.meshgrid(x, x, indexing="xy"), axis=-1) + [R, 0.0]
    amps, norm = gf.ladder_weights(L1_SLOPE, 1.0, OCTAVES, ring_break)
    return [sp.measure(gf.gaussian_sum(100 + s, pts, SCALE, amps, norm), d * 1000.0) for s in range(seeds)]


def patch_spectrum(ring_break: int, R: float, seeds: int = 3):
    """:func:`patch_spectra` stacked."""
    from galaxy.specs import spectrum as sp

    return sp.stack(patch_spectra(ring_break, R, seeds))


def k_of(wavelength_pc: float) -> float:
    return TWO_PI / wavelength_pc


# Gate (a), the rings as the lead ruled them: ring 1, the R_SUN ring (8) and ring 11 hold an octave above the break;
# beyond ring 12 the whole band lies below pi h. (mid radius kpc, the published height there pc, break index.)
SPECTRUM_RINGS = {1: (1.44, 28.0, 4), 8: (7.99, 107.6, 2), 11: (10.79, 213.9, 1), 13: (12.66, 340.4, 0)}


def test_a_ring_1_reads_both_slopes_and_the_break_at_pi_h():
    """Gate (a), ring 1 (pi h 88 pc, four octaves above the break): a continuous broken law fitted over 600-23.75 pc
    (the coarsest octave's plateau ends near 4 x 190 pc; the finest carries 23.75 pc) reads -1.53 +- 0.15 above and
    -2.53 +- 0.15 below, the break within an octave of pi h. Measured (three seeds): -1.543 / -2.435, the break at 77 pc against 88."""
    from galaxy.specs import spectrum as sp

    R, h, b = SPECTRUM_RINGS[1]
    assert gf.break_octave(h, SCALE, OCTAVES) == b
    fit = sp.fit_broken(patch_spectrum(b, R), k_of(600.0), k_of(23.75))
    print(f"ring 1: {fit.alpha_low:.3f} / {fit.alpha_high:.3f}, break {fit.wavelength_break:.0f} pc against {math.pi * h:.0f}")
    assert fit.alpha_low == pytest.approx(-L1_SLOPE, abs=0.15)
    assert fit.alpha_high == pytest.approx(-L1_SLOPE - 1.0, abs=0.15)
    assert 0.5 < fit.wavelength_break / (math.pi * h) < 2.0


@pytest.mark.parametrize("ring", [8, 11, 13])
def test_a_below_the_break_the_slope_is_the_steep_one(ring):
    """Gate (a): below pi h (ring 8: 338 pc, ring 11: 672, ring 13: 1069 - from 380 pc down where pi h is larger, the
    first wavelength the octave sum is a power law at) to 23.75 pc, one power law, -2.53 +- 0.15. Ring 13 is the
    ruling's "one slope" ring (the whole band below pi h). Measured (three seeds): -2.451 +- 0.032, -2.502 +- 0.025, -2.488 +- 0.025."""
    from galaxy.specs import spectrum as sp

    R, h, b = SPECTRUM_RINGS[ring]
    assert gf.break_octave(h, SCALE, OCTAVES) == b
    fit = sp.fit_power_law(patch_spectrum(b, R), max(2.0 / h, k_of(380.0)), k_of(23.75))
    print(f"ring {ring}: {fit.alpha:.3f} +- {fit.stderr:.3f}")
    assert fit.alpha == pytest.approx(-L1_SLOPE - 1.0, abs=0.15)


# Ring 8's seeds (S62's review, finding 2): the band above its break, 600-338 pc, holds three log bins and one seed's
# slope there scatters by 0.97 (100 seeds: mean -1.226, s.e. 0.097); stacks of ten seeds read -0.84 to -1.79 (sd
# 0.27; the first ten, 100-109, -1.548, inside the band), stacks of thirty -1.05 to -1.47 (sd 0.17), all hundred
# -1.259 +- 0.112. The miss is about two standard deviations of a thirty-seed stack, not more: of the three disjoint
# thirty-seed stacks one (seeds 160-189, -1.472) would read inside -1.53 +- 0.15, of the ten ten-seed stacks one
# (100-109). The seeds here are the reviewer's thirty, 100-129 (-1.234), fixed, so the strict xfail is deterministic;
# each seed costs 2.3-2.6 s (under another session's suite), 67 s for the two tests below, computed once.
RING_8_SEEDS = 30


@pytest.fixture(scope="module")
def ring_8_spectra():
    R, h, b = SPECTRUM_RINGS[8]
    return patch_spectra(b, R, RING_8_SEEDS)


@pytest.mark.xfail(strict=True, reason=(
    "a disclosed miss, D221: -1.23 +- 0.06 over 600-338 pc against -1.53 +- 0.15, too shallow by 0.3 - the coarsest "
    "octave's plateau at 760 pc (the band above pi h = 338 pc runs only to 4 x 190 pc, and by D221 item 1 the field's "
    "coarse end is L1's 190 pc; the cell's unit mean removes the larger scales anyway, #161); the test's three seeds "
    "read -1.97 by noise. Thirty seeds (100-129) here: -1.234 +- 0.059; a hundred -1.259 +- 0.112, one seed's mean "
    "-1.226 +- 0.097 (S62's review, finding 2, re-measured)."))
def test_a_ring_8_reads_the_shallow_slope_above_the_break(ring_8_spectra):
    from galaxy.specs import spectrum as sp

    R, h, b = SPECTRUM_RINGS[8]
    fit = sp.fit_power_law(sp.stack(ring_8_spectra), k_of(600.0), 2.0 / h)
    print(f"ring 8 above the break, {RING_8_SEEDS} seeds: {fit.alpha:.3f} +- {fit.stderr:.3f}")
    assert fit.alpha == pytest.approx(-L1_SLOPE, abs=0.15)


def test_a_ring_8_s_break_is_within_an_octave_of_pi_h(ring_8_spectra):
    """Gate (a), ring 8 judged on its break (D221's ruling; S62's review, finding 2): a continuous broken law over
    760-23.75 pc (the coarsest octave's plateau down to the finest octave) on thirty seeds puts the break within an
    octave of pi h = 338 pc. Measured: 341 pc (-0.930 / -2.451) on seeds 100-129; every ten-seed stack of seeds 100-199
    reads 212-353 pc, every thirty 286-341, all hundred 295. (Over 600-23.75 pc, as ring 1 is fitted, the band above
    holds too few bins and three seeds put it at 147 pc: the review's reading.)"""
    from galaxy.specs import spectrum as sp

    R, h, b = SPECTRUM_RINGS[8]
    fit = sp.fit_broken(sp.stack(ring_8_spectra), k_of(760.0), k_of(23.75))
    print(f"ring 8, {RING_8_SEEDS} seeds: {fit.alpha_low:.3f} / {fit.alpha_high:.3f}, break {fit.wavelength_break:.0f} pc "
          f"against {math.pi * h:.0f}")
    assert 0.5 < fit.wavelength_break / (math.pi * h) < 2.0


def test_a_ring_11_has_no_band_above_its_break():
    """Ring 11 (pi h 672 pc) has one octave above the break by the mapping (4 x 190 = 760 >= 672), but no wavelength
    band between the octave sum's top (760 pc) and pi h wide enough to fit: a fifth of an octave. Stated, measured
    only below (the test above)."""
    R, h, b = SPECTRUM_RINGS[11]
    assert b == 1 and math.log2(4.0 * 190.0 / (math.pi * h)) < 0.25


# --- the committed vectors (D221 item 6) -----------------------------------------------------------------------------


def stored_section() -> dict:
    import json

    return json.loads(noise.VECTORS.read_text(encoding="utf-8"))[gf.VECTORS_SECTION]


def close(want, got, path: str = "") -> list[str]:
    """Where two documents differ: ints and strings exactly, floats to 1e-12 relative."""
    if isinstance(want, dict):
        if list(want) != list(got):
            return [f"{path}: keys"]
        return [d for k in want for d in close(want[k], got[k], f"{path}/{k}")]
    if isinstance(want, list):
        if len(want) != len(got):
            return [f"{path}: length"]
        return [d for n, (a, b) in enumerate(zip(want, got)) for d in close(a, b, f"{path}[{n}]")]
    if isinstance(want, float):
        return [] if abs(want - float(got)) <= 1e-12 * max(1.0, abs(want)) else [f"{path}: {want!r} != {got!r}"]
    return [] if want == got else [f"{path}: {want!r} != {got!r}"]


def test_the_vectors_are_what_the_evaluator_computes_from_their_inputs():
    """The section of ``layer/vectors.json`` rebuilt from its own stored inputs (the seed, the model's numbers, the
    ring table, float32-exact) is the stored section to 1e-12: the evaluator reproduces every vector. Regenerating
    from the model is a decision's act (``gas_fluctuation.write_vectors``)."""
    stored = stored_section()
    found = close(stored, gf.build_vectors(stored["inputs"]))
    assert not found, found[:10]


def test_the_vectors_cover_what_a_twin_must_match():
    """56 sums across the disc (8 inside 2 kpc), two cells' normalisers and 16 map values in them, the weights for
    every break index 0-6, inputs exact in float32 (the disc's sense among them). The float32 path against float64,
    measured: the sum within 1.98e-3 out to 26 kpc and 6.4e-5 inside 3 kpc (single precision's lattice coordinates,
    noise.py's docstring: up to 5e-3 at 10 000 cells), the map within 5.1e-4 relative. (Before the sense was mended,
    S62's review finding 1, the same points read the noise at mirrored positions: 1.44e-3, 2.7e-4 and 3.5e-4; the
    bounds were 2e-3, 5e-4 and 5e-4, now 3e-3, 5e-4 and 1e-3 - the same precision's spread over other lattice points.)"""
    v = stored_section()
    inputs = v["inputs"]
    for key in ("scale", "l1_finest_frequency", "sense"):
        assert float(np.float32(inputs[key])) == inputs[key], key
    for key in ("edges", "sigma", "strain", "twist"):
        assert all(float(np.float32(x)) == x for x in inputs[key]), key
    assert len(v["weights"]) == OCTAVES + 1 and all(len(row) == OCTAVES for row in v["weights"])
    sums = np.array(v["sums"]["rows"])
    maps = np.array(v["maps"]["rows"])
    assert len(sums) == 56 and len(maps) == 16 and len(v["cells"]) == 2
    assert all(float(np.float32(x)) == x and x * 1024 == round(x * 1024) for x in sums[:, :2].ravel())
    radius = np.hypot(sums[:, 0], sums[:, 1])
    assert np.max(np.abs(sums[:, 3] - sums[:, 4])) < 3e-3
    assert np.max(np.abs(sums[radius < 3.0, 3] - sums[radius < 3.0, 4])) < 5e-4
    assert np.max(np.abs(maps[:, 5] / maps[:, 4] - 1.0)) < 1e-3


def test_e_nothing_reads_the_field_yet_so_l1_and_the_censuses_are_untouched():
    """Gate (e): the field multiplies nothing in this pass (V7 reads it), so no stage requires any of its fields and the
    clustering field's stage reads nothing of it: L1's map and every census are the branch's before the stage, by
    construction. Measured at S62 against the branch before the stage (18a6520): every field of the default galaxy's
    layer-on and layer-off runs but the eight new ones (777 digests) and the layer-on clouds' and clusters' 31
    materialised columns, bit for bit; tests/test_clustering_gate.py green. **Against the branch before the stage,
    not against main**: 18a6520 already carries the spurs, which move every cloud, cluster, HII-region and bubble
    column through the gas contrast (57 fields on the default galaxy, 62 on milky_way, layer on; S62's review, finding
    5) - L1's map itself (``census_clustering_seed``, ``census_clustering_cell_mean``) is main's to the bit. After the
    shear's sense was mended (finding 1) the same digests on default and milky_way, layer on and off, moved only this
    field's ``gas_fluctuation_cell_normaliser``."""
    _, impls_, _ = production()
    ours = set(FIELD_NAMES)
    for stage in impls_:
        assert not ours & set(stage.requires + stage.requires_optional), stage.id
    assert {d.name for d in impls_.get("gas_fluctuation").publishes} == ours
    assert impls_.get("gas_fluctuation").requires == ("gas_scale_height", "circular_velocity", "pitch_angle")  # the sense: S62 review, finding 1
