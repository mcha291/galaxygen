"""tools/goal_metrics.py: each metric returns a known value on a synthetic picture before it is trusted (rule B1).

Every picture here is an array built from a formula, so the answer is known before the tool is asked. The
pictures' own geometry (``plane``) is written here and not borrowed from the tool: a check that takes the tool's
path would pass whatever the tool did (B3). Each tolerance is stated with its cause; none was reached by tuning
the picture (B5). One PNG goes through Pillow, in ``tmp_path``.
"""

from __future__ import annotations

import functools
import json
import math
import subprocess
import sys
import tomllib
from pathlib import Path

import numpy as np
import pytest

import goal_metrics as gm

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "goal_metrics.py"
NO_SKY = (0.0, 0.0, 0.0)


# ------------------------------------------------------------------------------------------------------------
# The pictures
# ------------------------------------------------------------------------------------------------------------

def plane(shape, cx, cy, q=1.0, pa_deg=0.0):
    """Every pixel's radius (px) and azimuth in the plane of a disc seen with axis ratio q, long axis at pa_deg."""
    y, x = np.indices(shape, dtype=float)
    dx, dy = x - cx, y - cy
    t = math.radians(pa_deg)
    along = dx * math.cos(t) + dy * math.sin(t)
    across = (-dx * math.sin(t) + dy * math.cos(t)) / q
    return np.hypot(along, across), np.arctan2(across, along)


def grey(lum):
    return np.repeat(lum[..., None], 3, axis=2)


def power_law_field(n, beta, seed):
    """An isotropic Gaussian random field on n x n whose 2-D power spectrum is k^beta, unit rms."""
    white = np.random.default_rng(seed).standard_normal((n, n))
    k = np.hypot(np.fft.fftfreq(n)[:, None], np.fft.rfftfreq(n)[None, :])
    k[0, 0] = 1.0
    spectrum = np.fft.rfft2(white) * k ** (beta / 2.0)
    spectrum[0, 0] = 0.0
    field = np.fft.irfft2(spectrum, s=(n, n))
    return field / field.std()


def spots(shape, positions, heights, sigma):
    """A Gaussian of ``sigma`` px and the given peak height at each (x, y); sigma 0 is a single pixel."""
    out = np.zeros(shape)
    if sigma == 0:
        for (x, y), height in zip(positions, heights):
            out[int(round(y)), int(round(x))] += height
        return out
    reach = int(math.ceil(6 * sigma))                               # exp(-18): nothing is cut that matters
    for (px, py), height in zip(positions, heights):
        ya, yb = max(int(py) - reach, 0), min(int(py) + reach + 2, shape[0])
        xa, xb = max(int(px) - reach, 0), min(int(px) + reach + 2, shape[1])
        y, x = np.mgrid[ya:yb, xa:xb].astype(float)
        out[ya:yb, xa:xb] += height * np.exp(-((x - px) ** 2 + (y - py) ** 2) / (2 * sigma**2))
    return out


def _overlaps(n_in, factor):
    """The box average along one axis as a matrix: row k holds each input pixel's overlap with [k f, (k + 1) f) over f."""
    n_out = int(n_in / factor + 1e-9)
    k, i = np.arange(n_out)[:, None], np.arange(n_in)[None, :]
    return np.clip(np.minimum(i + 1, (k + 1) * factor) - np.maximum(i, k * factor), 0, None) / factor


def scattered(rng, count, r_lo, r_hi, cx, cy, apart):
    """``count`` positions with r in [r_lo, r_hi) about (cx, cy), no two within ``apart`` px."""
    found: list[tuple[float, float]] = []
    while len(found) < count:
        r, phi = rng.uniform(r_lo, r_hi), rng.uniform(0, 2 * math.pi)
        x, y = round(cx + r * math.cos(phi)), round(cy + r * math.sin(phi))
        if all(math.hypot(x - u, y - v) >= apart for u, v in found):
            found.append((x, y))
    return found


# ------------------------------------------------------------------------------------------------------------
# Pixel values and resampling
# ------------------------------------------------------------------------------------------------------------

def test_the_srgb_curve_is_the_standard_one_and_inverts():
    """Known: sRGB 0.5 is linear ((0.5 + 0.055)/1.055)^2.4 = 0.21404; the knee 0.04045 is 0.0031308."""
    assert gm.srgb_decode(0.5) == pytest.approx(0.214041, abs=1e-6)
    assert gm.srgb_decode(0.04045) == pytest.approx(0.0031308, abs=1e-7)
    assert gm.srgb_decode(np.array([0.0, 1.0])) == pytest.approx([0.0, 1.0])
    v = np.linspace(0, 1, 257)
    assert gm.srgb_encode(gm.srgb_decode(v)) == pytest.approx(v, abs=1e-12)


def test_area_averaging_is_exact_and_never_enlarges():
    """Known: output pixel k is sum_i overlap([k f, (k+1) f), [i, i+1)) x_i / f - written out here as a matrix.

    So the mean is kept when the factor divides the size, a factor of 2 is the 2 x 2 block mean, and a blob at
    x keeps its centroid at (x + 0.5)/f - 0.5: the mapping ``Geometry.scaled`` applies (0.01 px: a part-covered
    pixel's light goes to the output pixel's centre, which a smooth blob averages out).
    """
    rng = np.random.default_rng(11)
    image = rng.random((12, 18, 3))
    assert gm.resample_area(image, 1.5).shape == (8, 12, 3)
    assert gm.resample_area(image, 1.5).mean() == pytest.approx(image.mean(), rel=1e-12)
    assert gm.resample_area(image, 2.0) == pytest.approx(image.reshape(6, 2, 9, 2, 3).mean(axis=(1, 3)), abs=1e-12)
    assert gm.resample_area(image, 6.0) == pytest.approx(image.reshape(2, 6, 3, 6, 3).mean(axis=(1, 3)), abs=1e-12)
    assert gm.resample_area(image, 0.5).shape == image.shape and gm.resample_area(image, 1.0).shape == image.shape   # never up

    big = rng.random((40, 53))
    for factor in (2.5, 3.2, 1.25, 7.835):
        known = _overlaps(40, factor) @ big @ _overlaps(53, factor).T
        assert gm.resample_area(big, factor) == pytest.approx(known, abs=1e-12), factor
        assert gm.resample_area(big.astype(np.float32), factor) == pytest.approx(known, abs=1e-6)

    y, x = np.indices((90, 120), dtype=float)
    blob = np.exp(-((x - 61.3) ** 2 + (y - 40.8) ** 2) / (2 * 6.0**2))
    for factor in (2.5, 3.2, 1.25):
        out = gm.resample_area(blob, factor)
        v, u = np.indices(out.shape, dtype=float)
        g = gm.Geometry(61.3, 40.8, 0.7, 20.0, 12.0).scaled(factor)
        assert (u * out).sum() / out.sum() == pytest.approx(g.cx, abs=0.01)
        assert (v * out).sum() / out.sum() == pytest.approx(g.cy, abs=0.01)
        assert g.a == pytest.approx(12.0 / factor) and (g.q, g.pa_deg) == (0.7, 20.0)


def test_the_lattice_is_where_it_says_and_its_median_ignores_what_a_mean_follows():
    """Known: on a field whose value is 1000 row + column, a 3 x 3 lattice 4 px apart about (20, 30) reads the
    nine values at rows 16, 20, 24 and columns 26, 30, 34; at a corner the frame is reflected. The median of a
    flat field with a bright square under half the lattice is the flat field, where a Gaussian mean is not."""
    rows, cols = np.indices((50, 60))
    field = 1000.0 * rows + cols
    got = gm.lattice_values(field, np.array([20, 0]), np.array([30, 0]), 3, 4)
    assert got.shape == (2, 9)
    assert sorted(got[0]) == [1000.0 * r + c for r in (16, 20, 24) for c in (26, 30, 34)]
    assert sorted(got[1]) == sorted(1000.0 * r + c for r in (4, 0, 4) for c in (4, 0, 4))
    assert gm.lattice_values(field, np.array([], dtype=int), np.array([], dtype=int), 9, 3).shape == (0, 81)

    flat = np.ones((80, 80))
    flat[30:38, 30:38] = 50.0
    everywhere = np.indices((80, 80)).reshape(2, -1)
    assert np.median(gm.lattice_values(flat, *everywhere, 9, 3), axis=1) == pytest.approx(1.0)
    assert gm.gaussian_smooth(flat, 12.0).max() > 1.5                # the mean follows it
    assert gm.gaussian_smooth(np.ones((40, 60)), 7.0) == pytest.approx(1.0, abs=1e-12)   # normalised at the edge


# ------------------------------------------------------------------------------------------------------------
# Metric 1: the radial colour profile
# ------------------------------------------------------------------------------------------------------------

def _annulus(h, r1, r2):
    """The integral of exp(-r/h) r dr over [r1, r2]."""
    return h * h * ((1 + r1 / h) * math.exp(-r1 / h) - (1 + r2 / h) * math.exp(-r2 / h))


def test_an_exponential_disc_returns_its_colour_gradient():
    """Three exponential discs, one per channel, of scale lengths 50, 55, 60 px and peaks 1.0, 0.8, 0.6.

    Known: a ring's colour is -2.5 log10 of the ratio of the channels' annulus integrals, in closed form; the
    headline bands likewise (inner +0.3247, outer -0.1300, outer - inner -0.4547 mag in B-R).
    Tolerance 1e-4 mag from the second ring out: bilinear sampling of a curved profile is off by about
    h^-2 / 8 = 5e-5 of the value per channel, and the channels' errors nearly cancel in a ratio (measured 7e-6,
    and 6e-6 on the headline). The innermost ring holds the profile's cusp and is given 1e-3 (measured 3e-5).
    """
    a, scale, peak = 256.0, (50.0, 55.0, 60.0), (1.0, 0.8, 0.6)
    r, _ = plane((640, 640), 318.7, 321.4)
    image = np.stack([p * np.exp(-r / h) for p, h in zip(peak, scale)], axis=-1)
    result = gm.measure(image, gm.Geometry(318.7, 321.4, 1.0, 0.0, a), sky=NO_SKY)
    colour = result["metrics"]["radial_colour"]

    def known(lo, hi, channel):
        top, bottom = (peak[c] * _annulus(scale[c], lo * a, hi * a) for c in (channel, 0))
        return -2.5 * math.log10(top / bottom)

    edges = np.arange(gm.N_RINGS + 1) / gm.N_RINGS
    b_r = np.array([known(edges[k], edges[k + 1], 2) for k in range(gm.N_RINGS)])
    g_r = np.array([known(edges[k], edges[k + 1], 1) for k in range(gm.N_RINGS)])
    assert np.abs(colour["b_r"] - b_r)[1:].max() < 1e-4 and np.abs(colour["g_r"] - g_r)[1:].max() < 1e-4
    assert abs(colour["b_r"][0] - b_r[0]) < 1e-3
    assert b_r[-1] - b_r[0] < -0.8                                   # the picture does have a gradient to find

    head = result["headline"]
    inner, outer = known(*gm.COLOUR_INNER, 2), known(*gm.COLOUR_OUTER, 2)
    assert (inner, outer) == pytest.approx((0.3247, -0.1300), abs=1e-4)
    assert head["b_r_inner"] == pytest.approx(inner, abs=1e-4)
    assert head["b_r_outer"] == pytest.approx(outer, abs=1e-4)
    assert head["b_r_gradient"] == pytest.approx(outer - inner, abs=1e-4)
    assert head["g_r_gradient"] == pytest.approx(known(*gm.COLOUR_OUTER, 1) - known(*gm.COLOUR_INNER, 1), abs=1e-4)


# ------------------------------------------------------------------------------------------------------------
# Metrics 2 and 3: the Fourier amplitudes and the arm-interarm contrast
# ------------------------------------------------------------------------------------------------------------

def _pattern(shape, cx, cy, q, pa_deg, m, amplitude, phi0_deg, scale=80.0):
    r, phi = plane(shape, cx, cy, q, pa_deg)
    return np.exp(-r / scale) * (1 + amplitude * np.cos(m * (phi - math.radians(phi0_deg))))


@pytest.mark.parametrize("m, amplitude, phi0", [(2, 0.4, 25.0), (3, 0.3, 100.0), (7, 0.2, 10.0)])
@pytest.mark.parametrize("q, pa", [(1.0, 0.0), (0.5, 30.0)])
def test_a_cosine_pattern_returns_half_its_amplitude_at_its_m_face_on_and_inclined(m, amplitude, phi0, q, pa):
    """I(r, phi) = exp(-r/80) (1 + A cos(m (phi - phi0))), seen face-on and with q = 0.5 at 30 degrees.

    Known: sum_j (1 + A cos(m (phi_j - phi0))) exp(-i m phi_j) = N (A/2) exp(-i m phi0) on N even azimuths, and
    the same sum at any other m' <= 8 is 0; so A_m = A/2, every other A_m' = 0, and the crest is at phi0 modulo
    360/m. Tolerance: 0.2 % of A/2 on the headline and 1e-4 on the empty orders, for the bilinear reading of a
    pattern whose wavelength at r = 0.2 a is 46 px at m = 7 (23 px across the short axis when inclined), which
    lowers a crest by about (pi/23)^2 / 3 = 0.6 % there and a sixteenth of that at r = 0.8 a; 0.5 degrees on the
    phase. Measured: the worst of the six is m = 7 inclined, 0.10 % low, and 2e-5 on an empty order.
    """
    a, cx, cy = 256.0, 320.4, 318.9
    image = grey(_pattern((640, 640), cx, cy, q, pa, m, amplitude, phi0))
    result = gm.measure(image, gm.Geometry(cx, cy, q, pa, a), sky=NO_SKY)
    head, fourier = result["headline"], result["metrics"]["fourier"]

    assert head[f"A{m}"] == pytest.approx(amplitude / 2, rel=0.002)
    for other in range(1, gm.M_MAX + 1):
        if other != m:
            assert head[f"A{other}"] < 1e-4, other
    assert head["dominant_m"] == m and fourier["rings"] == 24       # the 24 rings of 0.2 <= r/a < 0.8
    pick = (fourier["r_over_a"] >= 0.2) & (fourier["r_over_a"] < 0.8)
    period = 360.0 / m
    offset = (fourier["phase_deg"][m - 1][pick] - phi0 + period / 2) % period - period / 2
    assert np.abs(offset).max() < 0.5


def test_the_wrong_axis_ratio_does_not_return_the_pattern():
    """The control (B4): the inclined m = 3 picture read as face-on must miss A/2 = 0.15 and gain an m = 2.

    Measured: A_3 = 0.114 and A_2 = 0.370. A test of the deprojection that passed here too would test nothing."""
    image = grey(_pattern((640, 640), 320.4, 318.9, 0.5, 30.0, 3, 0.3, 100.0))
    head = gm.measure(image, gm.Geometry(320.4, 318.9, 1.0, 30.0, 256.0), sky=NO_SKY)["headline"]
    assert abs(head["A3"] - 0.15) > 0.03 and head["A2"] > 0.05


def test_the_blue_contrast_is_its_closed_form_and_reads_the_blue_channel():
    """Red 1 + 0.1 cos(2 phi), green 1 + 0.2 cos(2 phi), blue 1 + 0.5 cos(2 phi), on one exponential disc.

    Known: for phi uniform, the p-th percentile of cos is cos(pi (1 - p)), so the 90th and 10th are
    +-cos(18 deg) = +-0.95106 and the contrast is (1 + A c)/(1 - A c): 2.8134 at A = 0.5. A pattern at m = 6 with
    A = 0.3 gives 1.7984. Tolerance 0.5 %: the percentile is read off 1024 sorted samples, and a pattern with m
    crests has them in equal groups of 2m, so the 90th and 10th are each placed to about 0.2-0.6 % of the
    azimuth. Measured 0.20 % low at m = 2 (face-on and inclined), 0.11 % low at m = 6; 0.22 % on the worst ring.
    """
    c = math.cos(math.radians(18.0))
    assert c == pytest.approx(math.cos(math.pi * (1 - 0.9)))
    for m, amplitude, q, pa in ((2, 0.5, 1.0, 0.0), (6, 0.3, 1.0, 0.0), (2, 0.5, 0.6, 140.0)):
        r, phi = plane((640, 640), 321.1, 319.3, q, pa)
        disc = np.exp(-r / 80.0)
        image = np.stack([disc * (1 + amp * np.cos(m * phi)) for amp in (0.1, 0.2, amplitude)], axis=-1)
        result = gm.measure(image, gm.Geometry(321.1, 319.3, q, pa, 256.0), sky=NO_SKY)
        known = (1 + amplitude * c) / (1 - amplitude * c)
        assert result["headline"]["arm_contrast"] == pytest.approx(known, rel=0.005), (m, q)
        per_ring = result["metrics"]["arm_contrast"]["contrast"]
        assert np.nanmax(np.abs(per_ring[8:32] / known - 1)) < 0.005
    assert (1 + 0.5 * c) / (1 - 0.5 * c) == pytest.approx(2.8134, abs=1e-4)
    assert (1 + 0.3 * c) / (1 - 0.3 * c) == pytest.approx(1.7984, abs=1e-4)
    # A pattern above m = 8 is cut before the percentiles are taken: the contrast is 1.
    r, phi = plane((640, 640), 321.1, 319.3)
    high = grey(np.exp(-r / 80.0) * (1 + 0.5 * np.cos(12 * phi)))
    assert gm.measure(high, gm.Geometry(321.1, 319.3, 1.0, 0.0, 256.0), sky=NO_SKY)["headline"]["arm_contrast"] == pytest.approx(1.0, abs=0.01)


def test_a_ring_that_leaves_the_frame_has_no_amplitude_and_says_so():
    """Known: with the centre 150 px from the frame's edge and a = 256, rings past r/a = 150/256 are cut.

    They carry NaN (null in the JSON), never zero (B9); the headline averages the complete rings only and
    counts them: ring centres from 0.2125 up to 0.5625, fifteen rings.
    """
    image = grey(_pattern((640, 640), 150.0, 320.0, 1.0, 0.0, 2, 0.4, 0.0))
    result = gm.measure(image, gm.Geometry(150.0, 320.0, 1.0, 0.0, 256.0), sky=NO_SKY)
    fourier = result["metrics"]["fourier"]
    cut = fourier["r_over_a"] > 150.0 / 256.0
    assert np.isnan(fourier["amplitude"][:, cut]).all() and np.isfinite(fourier["amplitude"][:, ~cut]).all()
    assert fourier["rings"] == 15 and result["metrics"]["arm_contrast"]["rings"] == 15
    assert result["headline"]["A2"] == pytest.approx(0.2, rel=0.01)
    as_json = gm.to_json(result)
    assert as_json["metrics"]["fourier"]["amplitude"][1][-1] is None
    json.dumps(as_json, allow_nan=False)                             # nothing unmeasured leaks out as NaN


# ------------------------------------------------------------------------------------------------------------
# Metric 4: the dark-lane covering fraction
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("period, width", [(16, 2), (8, 2), (20, 1)])
def test_dark_stripes_return_their_covering_fraction(period, width):
    """An exponential disc crossed by stripes ``width`` px wide every ``period`` px, each at 0.4 of the disc.

    Known: the stripes cover width/period of any region many periods across (0.125, 0.25, 0.05), and exactly the
    share of the annulus's pixels this test counts with its own mask. A stripe is at 0.4 of its surroundings,
    under the 0.75 line; the surroundings are not. Tolerance 0.002 against the test's own count (the two masks
    can differ by rounding on the ellipse's rim) and 0.004 against width/period (the annulus is finite).
    """
    q, pa, cx, cy, a = 0.7, 20.0, 322.3, 318.6, 256.0
    r, _ = plane((640, 640), cx, cy, q, pa)
    stripe = (np.indices((640, 640))[1] % period) < width
    image = grey(np.exp(-r / 100.0) * np.where(stripe, 0.4, 1.0))
    result = gm.measure(image, gm.Geometry(cx, cy, q, pa, a), sky=NO_SKY)
    annulus = (r / a >= gm.DISC_INNER) & (r / a < 1.0)
    counted = stripe[annulus].mean()
    assert result["headline"]["dark_fraction"] == pytest.approx(counted, abs=0.002)
    assert result["headline"]["dark_fraction"] == pytest.approx(width / period, abs=0.004)


def test_a_smooth_disc_a_bright_bar_and_black_gaps_hold_no_dark_lane():
    """Known: 0 on a smooth disc; 0 beside a bar ten times the disc; 0 in the black between narrow bright arms.

    The last two are why the local level is a median: against a Gaussian mean of sigma 0.05 a the bar's
    neighbours and the gaps both read as dark, and the same two pictures give 0.027 and 0.75 (asserted below, so
    the pictures are known to be ones a mean fails on). Tolerance 0.002 on the arms: a black pixel on the
    hollow side of an arm's curved edge has more than half its lattice on the arm (measured 0.0015).
    """
    geometry = gm.Geometry(320.0, 320.0, 1.0, 0.0, 256.0)
    r, phi = plane((640, 640), 320.0, 320.0)
    disc = np.exp(-r / 100.0)
    assert gm.measure(grey(disc), geometry, sky=NO_SKY)["headline"]["dark_fraction"] == 0.0

    y, x = np.indices((640, 640), dtype=float)
    bar = disc * (1 + 10.0 * np.exp(-(((x - 320) / 60.0) ** 2 + ((y - 320) / 8.0) ** 2) / 2))
    assert gm.measure(grey(bar), geometry, sky=NO_SKY)["headline"]["dark_fraction"] == 0.0

    arms = disc * (np.cos(phi - r / 40.0) ** 2 > 0.85)               # two arms a quarter of the azimuth wide, on black
    assert gm.measure(grey(arms), geometry, sky=NO_SKY)["headline"]["dark_fraction"] < 0.002

    annulus = (r / 256.0 >= gm.DISC_INNER) & (r / 256.0 < 1.0)
    for picture, by_the_mean in ((bar, 0.027), (arms, 0.75)):
        mean = gm.gaussian_smooth(picture, 0.05 * 256.0)
        assert (picture < 0.75 * mean)[annulus].mean() == pytest.approx(by_the_mean, rel=0.05)


# ------------------------------------------------------------------------------------------------------------
# Metric 5: the power-spectrum slope
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("beta, q, pa", [
    (0.0, 1.0, 0.0), (-1.0, 1.0, 0.0), (-2.0, 1.0, 0.0), (-3.0, 1.0, 0.0), (-1.0, 0.6, 50.0), (-3.0, 0.6, 50.0),
])
def test_a_power_law_field_returns_its_slope(beta, q, pa):
    """An exponential disc times (1 + 0.1 g), g a Gaussian random field of 2-D power k^beta.

    Known: the unsharp-masked picture is 0.1 g with its long waves removed, so the slope over 10-50 cycles per
    a is beta. Tolerance 0.1: ten bins over 0.7 dex, the first holding about 250 independent modes, scatter the
    fit by a few hundredths, and the window's leakage and the unsharp mask's last 1 % at 10 cycles add as much.
    Measured: face-on 0.001, -0.954, -2.024, -3.022; at q = 0.6 and 50 degrees -0.949 and -3.035.
    """
    cx, cy, a = 321.5, 318.5, 256.0
    r, _ = plane((640, 640), cx, cy, q, pa)
    image = grey(np.exp(-r / 100.0) * (1 + 0.1 * power_law_field(640, beta, seed=20 + int(-beta))))
    result = gm.measure(image, gm.Geometry(cx, cy, q, pa, a), sky=NO_SKY)
    assert result["headline"]["power_slope"] == pytest.approx(beta, abs=0.1)
    assert len(result["metrics"]["power_slope"]["kappa"]) == gm.SLOPE_BINS
    assert result["headline"]["unsharp_rms"] < 0.11                  # 0.1 g, less its long waves


@pytest.mark.parametrize("n, a", [(1280, 512.0), (1000, 400.0)])
def test_the_slope_survives_the_box_average(n, a):
    """The beta = -2 field drawn at a = 512 and a = 400 px, so averaged by 2 and by 1.5625 on the way in.

    Known: -2. Tolerance 0.1, the same. A box is not an ideal low-pass: it takes sinc^2 off the short end of the
    fit and folds some of the power past the new grid back in. Measured: -2.03 at a factor of 2 (as at a factor
    of 1), -2.06 at 1.5625; the module's docstring states the 0.03-0.04.
    """
    r, _ = plane((n, n), n / 2 + 0.5, n / 2 - 0.5)
    image = grey(np.exp(-r / (a / 2.56)) * (1 + 0.1 * power_law_field(n, -2.0, seed=3)))
    result = gm.measure(image, gm.Geometry(n / 2 + 0.5, n / 2 - 0.5, 1.0, 0.0, a), sky=NO_SKY)
    assert result["standard"]["factor"] == pytest.approx(a / 256.0) and result["standard"]["working_a_px"] == pytest.approx(256.0)
    assert result["headline"]["power_slope"] == pytest.approx(-2.0, abs=0.1)


def test_a_picture_too_small_for_the_fit_has_no_slope():
    """Known: at a = 90 px, 50 cycles per a is 1.8 px, past the grid's 2 px: None and a reason, not a number."""
    r, _ = plane((240, 240), 120.0, 120.0)
    image = grey(np.exp(-r / 40.0) * (1 + 0.1 * power_law_field(240, -2.0, seed=5)))
    result = gm.measure(image, gm.Geometry(120.0, 120.0, 1.0, 0.0, 90.0), sky=NO_SKY)
    assert result["standard"]["below_standard"] is True and result["standard"]["factor"] == 1.0
    assert result["standard"]["working_shape"] == [240, 240]         # used as it is, never enlarged
    assert math.isnan(result["headline"]["power_slope"]) and "Nyquist" in result["metrics"]["power_slope"]["reason"]
    assert gm.to_json(result)["headline"]["power_slope"] is None
    assert "—" in gm.table_row("small", result)


# ------------------------------------------------------------------------------------------------------------
# Metric 6: point sources
# ------------------------------------------------------------------------------------------------------------

def _starfield(noise=0.0, seed=3):
    """An exponential disc (q = 0.6, a = 256) with 40 single-pixel sources on it and 15 off it; returns the parts."""
    q, pa, cx, cy, a = 0.6, 35.0, 400.0, 330.0, 256.0
    shape = (660, 800)
    r, _ = plane(shape, cx, cy, q, pa)
    disc = np.exp(-r / 70.0)
    rng = np.random.default_rng(seed)
    if noise:
        disc = disc * (1 + noise * rng.standard_normal(shape))
    inside, outside = [], []
    while len(inside) < 40 or len(outside) < 15:
        x, y = int(rng.integers(8, shape[1] - 8)), int(rng.integers(8, shape[0] - 8))
        if any(math.hypot(x - u, y - v) < 8 for u, v in inside + outside):
            continue
        rho = r[y, x] / a
        if 0.2 <= rho < 0.95 and len(inside) < 40:
            inside.append((x, y))
        elif rho >= 1.1 and len(outside) < 15:
            outside.append((x, y))
    level = float(np.median(disc[(r / a >= 0.15) & (r / a < 1)]))
    heights = [3.0 * disc[y, x] for x, y in inside] + [level] * 15
    return disc, inside + outside, heights, gm.Geometry(cx, cy, q, pa, a)


@pytest.mark.parametrize("noise", [0.0, 0.01])
def test_planted_point_sources_are_counted_inside_and_outside(noise):
    """Known: 40 single pixels at three times the disc under them, 15 off the disc at the disc's median: 40 and 15.

    A single pixel of height H gives a residual of H (1/(2 pi 1.08) - 1/(2 pi 4.08)) = 0.108 H before the
    division, 0.2 or more after it: over the 0.05 floor everywhere. With 1 % noise the local robust sigma is
    about 0.002 and the floor still decides. Exact, no tolerance: the sources are 8 px or more apart.
    """
    disc, where, heights, geometry = _starfield(noise)
    result = gm.measure(grey(disc + spots(disc.shape, where, heights, 0)), geometry, sky=NO_SKY)
    assert (result["headline"]["points_inside"], result["headline"]["points_outside"]) == (40, 15)
    # The same field at twice the pixel count, each source a 2 x 2 block: the standard scale gives the same.
    double = np.kron(grey(disc + spots(disc.shape, where, heights, 0)), np.ones((2, 2, 1)))
    twice = gm.measure(double, gm.Geometry(2 * geometry.cx + 0.5, 2 * geometry.cy + 0.5, 0.6, 35.0, 512.0), sky=NO_SKY)
    assert (twice["headline"]["points_inside"], twice["headline"]["points_outside"]) == (40, 15)
    assert twice["standard"]["factor"] == 2.0


@pytest.mark.parametrize("noise", [0.0, 0.01])
def test_a_smooth_disc_holds_no_point_source(noise):
    """Known: 0 and 0, exactly: at 1 % noise the residual's scatter is 0.002 and nothing reaches the 0.05 floor."""
    disc, _, _, geometry = _starfield(noise, seed=8)
    sources = gm.measure(grey(disc), geometry, sky=NO_SKY)["metrics"]["point_sources"]
    assert (sources["inside"]["count"], sources["outside"]["count"]) == (0, 0)
    assert (sources["inside"]["count_above_floor"], sources["outside"]["count_above_floor"]) == (0, 0)


@pytest.mark.parametrize("seed", [6, 8])
def test_the_local_sigma_holds_back_ten_per_cent_noise(seed):
    """Known: 0 sources in pure noise. At 10 % the residual's scatter is 0.018, so about a hundred compact
    maxima clear the 0.05 floor inside the ellipse, and the five-sigma test is what refuses them.

    Not exact, and stated: the sigma is a MAD of 225 lattice values, good to about 7 %, and near the ellipse's
    rim the lattice reaches into quieter sky. Over seeds 1-8 the counts were 0 and 0 six times, 2 inside once
    (seed 6) and 1 outside once (seed 8): those two seeds are the ones run here. Tolerance: at most 2 a side.
    """
    disc, _, _, geometry = _starfield(0.1, seed=seed)
    sources = gm.measure(grey(disc), geometry, sky=NO_SKY)["metrics"]["point_sources"]
    assert sources["inside"]["count_above_floor"] > 50
    assert sources["inside"]["count"] <= 2 and sources["outside"]["count"] <= 2
    assert sources["inside"]["median_sigma"] == pytest.approx(0.018, rel=0.15)


def test_blobs_and_lines_are_not_point_sources():
    """Known: 0. Ten Gaussians of sigma 4 px at three times the disc are too wide for the 1-2 px residual; ten
    bright lines 40 px long have neighbours two pixels along them at the peak's own height, so fail compactness."""
    disc, where, heights, geometry = _starfield()
    blobs = spots(disc.shape, where[:10], heights[:10], 4.0)
    assert gm.measure(grey(disc + blobs), geometry, sky=NO_SKY)["headline"]["points_inside"] == 0
    lines = np.zeros_like(disc)
    for (x, y), height in zip(where[10:20], heights[10:20]):
        lines[y, x - 20 : x + 20] = height
    rng = np.random.default_rng(1)
    noisy = (disc + lines) * (1 + 0.01 * rng.standard_normal(disc.shape))
    assert gm.measure(grey(noisy), geometry, sky=NO_SKY)["headline"]["points_inside"] == 0


# ------------------------------------------------------------------------------------------------------------
# The outline
# ------------------------------------------------------------------------------------------------------------

def _inclined_disc(sky=0.0, noise=0.0, stars=0, seed=4):
    shape, cx, cy, q, pa, h = (700, 800), 412.3, 341.8, 0.55, 35.0, 45.0
    r, _ = plane(shape, cx, cy, q, pa)
    lum = np.exp(-r / h)
    rng = np.random.default_rng(seed)
    if stars:
        for _ in range(stars):
            lum[int(rng.integers(20, shape[0] - 20)), int(rng.integers(20, shape[1] - 20))] += 5.0
    image = np.stack([lum * 1.0, lum * 0.9, lum * 0.8], axis=-1) + sky
    if noise:
        image = image + noise * rng.standard_normal(image.shape)
    return image, (cx, cy, q, pa, h)


@pytest.mark.parametrize("sky, noise, stars", [(0.0, 0.0, 0), (0.05, 0.002, 0), (0.0, 0.0, 40)])
def test_the_outline_estimate_recovers_a_planted_ellipse(sky, noise, stars):
    """An exponential disc of scale length 45 px, q = 0.55, long axis at 35 degrees, centre (412.3, 341.8).

    Known: the isophote that holds a share f of an exponential disc's light is at x = r/h with
    1 - (1 + x) e^-x = f; at f = 0.9, x = 3.8897, so a = 175.0 px; q, the angle and the centre are the planted
    ones. Tolerances: centre 0.2 px, q 0.01, angle 0.2 degrees, a 1 % - the outline is found on a picture
    averaged to 512 px and smoothed by 1 % of its side, which moves the short axis of the isophote out by about
    1 px in 96 (measured: q 0.557 for 0.55, a 175.2). Held with a sky pedestal of 0.05 under noise of 0.002,
    where the sky comes back to 1e-4 and its noise as the box average leaves it.

    With 40 single pixels at five times the disc's peak scattered over the frame the centre holds and a does
    NOT, and should not: the stars are s = 200 / (2 pi h^2 q) = 2.9 % more light, the outline must hold 90 % of
    all of it, and the stars outside it leave the disc to supply up to 0.9 (1 + s) = 92.6 % of its own: a is
    between 175.0 and 191.2 px (measured 188.9, q 0.561, the angle 0.55 degrees off). The estimate follows a
    picture's light, stars included; that is a property recorded here, not a tolerance.
    """
    def radius_holding(share):
        x = 3.0
        for _ in range(50):
            x = x - (1 - (1 + x) * math.exp(-x) - share) / (x * math.exp(-x))    # Newton on the light share
        return x

    assert radius_holding(0.9) == pytest.approx(3.8897, abs=1e-4)
    image, (cx, cy, q, pa, h) = _inclined_disc(sky, noise, stars)
    estimate = gm.estimate_outline(image)
    g = estimate["geometry"]
    assert math.hypot(g.cx - cx, g.cy - cy) < 0.2
    assert estimate["sky"] == pytest.approx([sky] * 3, abs=1e-4)
    if stars:
        more = stars * 5.0 / (2 * math.pi * h * h * q)
        assert more == pytest.approx(0.0286, abs=1e-4)
        assert 1.03 * radius_holding(0.9) * h < g.a < 1.005 * radius_holding(0.9 * (1 + more)) * h
        assert g.q == pytest.approx(q, abs=0.015) and g.pa_deg == pytest.approx(pa, abs=1.0)
    else:
        assert g.q == pytest.approx(q, abs=0.01)
        assert g.pa_deg == pytest.approx(pa, abs=0.2)
        assert g.a == pytest.approx(radius_holding(0.9) * h, rel=0.01)
    if noise:
        # White noise through the box average: each axis keeps sqrt(mean sum w^2) of it, w the overlaps.
        keep = math.prod(
            math.sqrt((_overlaps(n, estimate["work_factor"]) ** 2).sum(axis=1).mean()) for n in image.shape[:2]
        )
        assert estimate["sky_noise"] == pytest.approx(noise * math.sqrt(sum(w * w for w in gm.LUMA)) * keep, rel=0.05)

    if sky or stars:
        return
    # measure() uses and reports the same estimate, and says where the geometry came from.
    result = gm.measure(image)
    assert result["geometry"]["source"].startswith("estimated") and result["geometry"]["used"]["a"] == pytest.approx(g.a)
    assert result["sky"]["subtracted"] == pytest.approx([sky] * 3, abs=1e-3)
    given = gm.measure(image, gm.Geometry(cx, cy, q, pa, 170.0))
    assert given["geometry"]["source"] == "given" and given["geometry"]["estimated"]["a"] == pytest.approx(g.a)


def test_a_face_on_disc_is_round_and_a_black_picture_is_refused():
    r, _ = plane((600, 600), 300.0, 300.0)
    g = gm.estimate_outline(grey(np.exp(-r / 40.0)))["geometry"]
    assert g.q > 0.98 and g.a == pytest.approx(3.8897 * 40.0, rel=0.03)
    with pytest.raises(ValueError, match="no light"):
        gm.measure(np.zeros((64, 64, 3)))
    with pytest.raises(ValueError, match="H x W x 3"):
        gm.measure(np.zeros((64, 64)))


# ------------------------------------------------------------------------------------------------------------
# Comparability: the same picture at twice the pixel count
# ------------------------------------------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def _scene(n=800):
    """A picture with something for every metric: a colour gradient, two arms, lanes, texture and 30 sources.

    Built once and shared: no test writes into it.
    """
    cx, cy, q, pa = 402.3, 396.6, 0.7, 25.0
    r, phi = plane((n, n), cx, cy, q, pa)
    arm = np.cos(2 * (phi - np.log(np.maximum(r, 1.0) / 40.0) / math.tan(math.radians(20.0))))
    lanes = 1 - 0.6 * sum(np.exp(-((r - radius) ** 2) / (2 * 1.5**2)) for radius in range(60, 320, 20))
    texture = 1 + 0.15 * power_law_field(n, -2.0, seed=17)
    rng = np.random.default_rng(23)
    where = scattered(rng, 30, 70.0, 280.0, 0.0, 0.0, 12.0)
    t = math.radians(pa)
    placed = [(cx + x * math.cos(t) - q * y * math.sin(t), cy + x * math.sin(t) + q * y * math.cos(t)) for x, y in where]
    channels = []
    for peak, scale, amplitude in ((1.0, 70.0, 0.15), (0.8, 78.0, 0.25), (0.6, 86.0, 0.4)):
        disc = peak * np.exp(-r / scale)
        heights = [4.0 * peak * math.exp(-math.hypot(x, y) / scale) for x, y in where]
        channels.append(disc * (1 + amplitude * arm) * lanes * texture + spots((n, n), placed, heights, 0.8))
    scene = np.stack(channels, axis=-1)
    scene.setflags(write=False)
    return scene


def _fourier_enlarge(image):
    """The same picture on twice the pixels by zero-padding its spectrum: an ideal enlargement, not a box."""
    n = image.shape[0]
    spectrum = np.fft.fftshift(np.fft.fft2(image, axes=(0, 1)), axes=(0, 1))
    padded = np.zeros((2 * n, 2 * n, image.shape[2]), dtype=complex)
    padded[n // 2 : n // 2 + n, n // 2 : n // 2 + n] = spectrum
    return 4.0 * np.fft.ifft2(np.fft.ifftshift(padded, axes=(0, 1)), axes=(0, 1)).real


def test_twice_the_pixels_gives_the_same_headlines():
    """One scene at 800 px and, enlarged through its Fourier transform, at 1600 px; geometry estimated on each.

    The enlargement is not the inverse of the tool's box average (the one picture is averaged by 1.05, the other
    by 2.11), so this is the comparability claim and not an identity. Known: every headline is a property of
    the picture, so the two agree. Tolerance, and what was measured:
      the outline's a doubles to 0.2 % (0.01 %), q to 0.002 (0.0001), the angle to 0.1 degree (0.01);
      colours 0.002 mag (0.0001); each A_m 0.001 (0.0002); the contrast 0.5 % (0.05 %);
      the dark fraction 0.005 (0.0001: a lane's edge pixels sit near the 0.75 line);
      the slope 0.08 (0.038: -1.719 and -1.681, the two box averages differing as the docstring says they do);
      the unsharp rms 3 % (1.6 %); the counts equal (28 inside and 2 outside, both times).
    """
    small = _scene()
    large = _fourier_enlarge(small)
    one, two = gm.measure(small), gm.measure(large)
    assert one["standard"]["below_standard"] is False and one["standard"]["factor"] == pytest.approx(1.054, abs=0.01)
    assert two["standard"]["factor"] == pytest.approx(2 * one["standard"]["factor"], rel=0.002)
    a, b = one["headline"], two["headline"]
    assert b["a_px"] == pytest.approx(2 * a["a_px"], rel=0.002)
    assert b["axis_ratio"] == pytest.approx(a["axis_ratio"], abs=0.002)
    assert b["position_angle_deg"] == pytest.approx(a["position_angle_deg"], abs=0.1)
    for key in ("b_r_inner", "b_r_outer", "b_r_gradient", "g_r_inner", "g_r_outer", "g_r_gradient"):
        assert b[key] == pytest.approx(a[key], abs=0.002), key
    for m in range(1, gm.M_MAX + 1):
        assert b[f"A{m}"] == pytest.approx(a[f"A{m}"], abs=0.001), m
    assert b["dominant_m"] == a["dominant_m"] == 2
    assert b["arm_contrast"] == pytest.approx(a["arm_contrast"], rel=0.005)
    assert b["dark_fraction"] == pytest.approx(a["dark_fraction"], abs=0.005)
    assert b["power_slope"] == pytest.approx(a["power_slope"], abs=0.08)
    assert b["unsharp_rms"] == pytest.approx(a["unsharp_rms"], rel=0.03)
    assert (b["points_inside"], b["points_outside"]) == (a["points_inside"], a["points_outside"])
    # The scene is not empty of what is being compared.
    assert a["b_r_gradient"] < -0.1 and a["A2"] > 0.05 and a["arm_contrast"] > 1.5 and a["dark_fraction"] > 0.05
    assert a["points_inside"] >= 20 and -2.6 < a["power_slope"] < -1.4


def test_the_polar_metrics_hold_below_the_standard_scale():
    """Known: the colour gradient and A_2 of one formula drawn at a = 256 and at a = 128 are the same numbers.

    The smaller picture is not enlarged; its polar grid is read between coarser pixels. Tolerances 0.001 mag and
    0.1 % of the amplitude (measured 1e-5 mag apart; A_2 = 0.19999 and 0.19997 for a known 0.2).
    """
    out = {}
    for a in (256.0, 128.0):
        n = int(2.5 * a)
        r, phi = plane((n, n), n / 2 + 0.3, n / 2 - 0.4)
        arm = 1 + 0.4 * np.cos(2 * phi)
        image = np.stack([p * np.exp(-r / (h * a)) * arm for p, h in ((1.0, 0.20), (0.8, 0.22), (0.6, 0.24))], axis=-1)
        out[a] = gm.measure(image, gm.Geometry(n / 2 + 0.3, n / 2 - 0.4, 1.0, 0.0, a), sky=NO_SKY)
    assert out[128.0]["standard"]["below_standard"] is True and out[256.0]["standard"]["below_standard"] is False
    assert out[128.0]["headline"]["b_r_gradient"] == pytest.approx(out[256.0]["headline"]["b_r_gradient"], abs=0.001)
    assert out[128.0]["headline"]["A2"] == pytest.approx(0.2, rel=0.001)
    assert out[256.0]["headline"]["A2"] == pytest.approx(0.2, rel=0.001)


# ------------------------------------------------------------------------------------------------------------
# The file, the command line, the table
# ------------------------------------------------------------------------------------------------------------

def test_a_png_goes_through_the_command_line_and_the_table_row_fits_its_header(tmp_path, capsys):
    """The scene written as an 8-bit sRGB PNG and read back by the tool, against the same scene in memory.

    Known: the command line adds nothing to ``measure`` on the array ``load_image`` returns (equal to the
    JSON's six figures), and the row has the header's columns. Against the scene before it was rounded to 8 bits
    the headlines agree only to the rounding, which is not small in a faint outer disc (at r = 0.8 a one step
    of 1/255 is 4 % of the value) and also moves the estimated outline by 0.5 %: 0.01 mag in the colours
    (measured 0.004), 0.005 in each A_m (0.003 at m = 6), 1.5 % in the contrast (0.7 %), 0.06 in the slope (0.03).
    """
    from PIL import Image

    scene = _scene()
    scene = scene / scene.max()
    png = tmp_path / "scene.png"
    Image.fromarray(np.rint(255 * gm.srgb_encode(scene)).astype(np.uint8)).save(png)
    loaded = gm.load_image(png)
    assert loaded.shape == scene.shape and loaded.dtype == np.float32
    assert np.abs(gm.srgb_encode(loaded) - gm.srgb_encode(scene)).max() <= 0.5 / 255 + 1e-6
    assert gm.load_image(png, encoded=True).max() == pytest.approx(1.0)

    out = tmp_path / "scene.json"
    assert gm.main([str(png), "--json", str(out), "--table", "--table-header", "--name", "scene"]) == 0
    header, rule, row = capsys.readouterr().out.strip().splitlines()
    assert header.count("|") == rule.count("|") == row.count("|") == len(gm.COLUMNS) + 3
    assert row.startswith("| scene | linear |")
    assert b"\r" not in out.read_bytes()

    result = json.loads(out.read_text(encoding="utf-8"))
    same = gm.to_json(gm.measure(loaded))
    assert result["headline"] == same["headline"] and result["metrics"]["fourier"] == same["metrics"]["fourier"]
    memory = gm.measure(scene)["headline"]
    for key in ("b_r_inner", "b_r_outer", "b_r_gradient"):
        assert result["headline"][key] == pytest.approx(memory[key], abs=0.01), key
    for m in range(1, gm.M_MAX + 1):
        assert result["headline"][f"A{m}"] == pytest.approx(memory[f"A{m}"], abs=0.005)
    assert result["headline"]["arm_contrast"] == pytest.approx(memory["arm_contrast"], rel=0.015)
    assert result["headline"]["power_slope"] == pytest.approx(memory["power_slope"], abs=0.06)
    assert result["headline"]["dark_fraction"] == pytest.approx(memory["dark_fraction"], abs=0.005)
    assert (result["headline"]["points_inside"], result["headline"]["points_outside"]) == (memory["points_inside"], memory["points_outside"])
    assert result["image"] == {"height": 800, "width": 800, "values": "linear", "path": "scene.png"}
    assert result["geometry"]["source"].startswith("estimated")
    # Every metric's definition travels with its numbers.
    assert set(result["metrics"]) == {"radial_colour", "fourier", "arm_contrast", "dark_fraction", "power_slope", "point_sources"}
    assert set(result["metrics"]) | {"pixel_value", "coordinates", "geometry", "standard_scale"} == set(result["definitions"])
    assert "not photometry" in result["note"] and "not photometry" in result["definitions"]["pixel_value"]

    # Given geometry is used and named; --encoded is labelled and is a different measurement; with no --table
    # the summary is printed.
    assert gm.main([str(png), "--json", str(out), "--encoded", "--axis-ratio", "1", "--radius", "300"]) == 0
    text = capsys.readouterr().out
    assert text.startswith("scene.png: 800 x 800 px, encoded values") and "6 point sources" in text
    assert "geometry (given: axis ratio, radius; the rest estimated)" in text
    encoded = json.loads(out.read_text(encoding="utf-8"))
    assert encoded["geometry"]["source"] == "given: axis ratio, radius; the rest estimated"
    assert encoded["geometry"]["used"]["q"] == 1.0 and encoded["geometry"]["used"]["a"] == 300.0
    assert encoded["geometry"]["estimated"]["q"] < 0.9
    assert encoded["image"]["values"] == "encoded"
    assert abs(encoded["headline"]["b_r_gradient"]) < abs(result["headline"]["b_r_gradient"])   # the curve compresses it

    # A black picture has no outline: a message and a failing exit, not a table row of nothing.
    black = tmp_path / "black.png"
    Image.fromarray(np.zeros((40, 40, 3), dtype=np.uint8)).save(black)
    assert gm.main([str(black), "--table"]) == 1
    streams = capsys.readouterr()
    assert streams.out == "" and "no light" in streams.err


def test_the_tool_runs_as_a_script_and_prints_utf8():
    """The header has a minus sign, a delta and a degree sign; a cp1252 console must not stop it."""
    proc = subprocess.run([sys.executable, str(TOOL), "--table-header"], capture_output=True, check=True, cwd=str(ROOT))
    lines = proc.stdout.decode("utf-8").splitlines()
    assert lines[0] == gm.table_header().splitlines()[0] and "Δ(B−R)" in lines[0] and "PA°" in lines[0]
    assert subprocess.run([sys.executable, str(TOOL)], capture_output=True, cwd=str(ROOT)).returncode == 2


def test_the_docstring_states_the_numbers_the_module_holds():
    """A definition that is written in two places drifts (B13): the docstring's numbers are the constants."""
    doc = " ".join(gm.__doc__.split())
    stated = [
        f"at most {gm.GEOM_WORK} px", f"{gm.GEOM_BORDER * 100:.0f} % of the shorter side", f"sigma {gm.GEOM_SMOOTH * 100:.0f} % of the longer side",
        f"hold {gm.GEOM_LIGHT * 100:.0f} % of the smoothed light", f"is {gm.STANDARD_A} px", f"a/{gm.STANDARD_A}",
        f"{gm.POLAR_N_R} radii", f"{gm.POLAR_N_PHI} azimuths", f"{gm.N_RINGS} rings of width a/{gm.N_RINGS}",
        f"{gm.LUMA[0]} R + {gm.LUMA[1]} G + {gm.LUMA[2]} B", f"m = 1..{gm.M_MAX}", f"m <= {gm.M_MAX}",
        f"{gm.COLOUR_INNER[0]} <= r/a < {gm.COLOUR_INNER[1]}", f"{gm.COLOUR_OUTER[0]} <= r/a < {gm.COLOUR_OUTER[1]}",
        f"{gm.PATTERN_RANGE[0]} <= r/a < {gm.PATTERN_RANGE[1]}",
        f"{gm.CONTRAST_PERCENTILES[1]:.0f}th percentile over its {gm.CONTRAST_PERCENTILES[0]:.0f}th",
        f"{gm.DARK_LATTICE} x {gm.DARK_LATTICE} lattice of pixels {gm.DARK_SPACING * 256:.0f}a/256 apart",
        f"{gm.DISC_INNER} <= r/a < 1", f"t = {gm.DARK_T}",
        f"sigma {gm.BACKGROUND_SIGMA} a", f"{gm.SLOPE_BINS} logarithmic bins", f"between {gm.SLOPE_KAPPA[0]:.0f} and {gm.SLOPE_KAPPA[1]:.0f} cycles",
        f"smoothed at {gm.POINT_SIGMAS[0]:.0f} px less the same at {gm.POINT_SIGMAS[1]:.0f} px", f"plus {gm.POINT_SOFT:.2f} of",
        f"stands {gm.POINT_K:.0f} robust sigmas", f"by {gm.POINT_K:.0f} x 1.4826 MAD", f"floor of {gm.POINT_FLOOR}",
        f"{gm.POINT_LATTICE} x {gm.POINT_LATTICE} lattice of pixels {gm.POINT_SPACING} px apart", "under half the peak",
    ]
    missing = [s for s in stated if s not in doc]
    assert not missing, missing
    assert gm.POINT_COMPACT == 0.5 and gm.POLAR_N_R == 8 * gm.N_RINGS
    # Each band ends on a ring's edge, as the docstring says.
    for edge in (*gm.COLOUR_INNER, *gm.COLOUR_OUTER, *gm.PATTERN_RANGE, gm.DISC_INNER):
        assert (edge * gm.N_RINGS) == pytest.approx(round(edge * gm.N_RINGS), abs=1e-9), edge


def test_pillow_is_a_development_tool_and_the_model_never_imports_it():
    """BUILD_III section 7, ruling 10: Pillow in the dev group only; nothing under model/galaxy/ imports it."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["dependencies"] == ["numpy>=2.3,<3"]
    assert any(d.lower().startswith("pillow") for d in project["dependency-groups"]["dev"])

    skip = {".claude", "node_modules", ".venv", "__pycache__"}
    sources = [p for p in (ROOT / "model").rglob("*.py") if not skip & set(p.relative_to(ROOT).parts)]
    assert len(sources) > 20
    for path in sources:
        for line in path.read_text(encoding="utf-8").splitlines():
            words = line.split("#")[0].split()
            if words[:1] in (["import"], ["from"]):
                assert not any(w.split(".")[0].rstrip(",") in ("PIL", "goal_metrics") for w in words[1:]), f"{path}: {line.strip()}"
