"""The randomness layer's noise primitives (BUILD_III Phase R, item 2): the instrument for ``galaxy.layer.noise``.

Every number a docstring of that module calls "measured" is measured here, by a ``measure_*`` function, and
asserted with a tolerance that says what it allows for: a sampling error (stated with the count that sets it)
or a systematic the docstring names. No input is tuned to make a tolerance hold (B5).
"""

from __future__ import annotations

import ast
import functools
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from galaxy.layer import noise

ROOT = Path(__file__).resolve().parents[1]
MASK = 0xFFFFFFFF


# --- an independent hash: plain Python integers, masked by hand --------------------------------------------------


def ref_mix(x: int) -> int:
    x ^= x >> 16
    x = (x * 0x7FEB352D) & MASK
    x ^= x >> 15
    x = (x * 0x846CA68B) & MASK
    x ^= x >> 16
    return x


def ref_hash(seed: int, octave: int, *cell: int) -> int:
    h = ref_mix((seed ^ 0x9E3779B9) & MASK)
    h = ref_mix(h ^ octave)
    for i in cell:
        h = ref_mix(h ^ (i % (1 << 32)))  # two's complement: Python's % of a negative int is non-negative
    return h


def test_the_mixer_is_the_published_one_worked_by_hand():
    """`lowbias32` on 1, step by step: the constants and shifts are the README's, and the arithmetic wraps."""
    x = 1
    x ^= x >> 16  # 1
    x = (x * 0x7FEB352D) % 2**32  # 0x7FEB352D
    assert x == 0x7FEB352D
    x ^= x >> 15  # 0x7FEB352D ^ 0xFFD6
    assert x == 0x7FEB352D ^ 0xFFD6 == 0x7FEBCAFB
    x = (x * 0x846CA68B) % 2**32
    x ^= x >> 16
    assert noise._mix_int(1) == x == ref_mix(1)
    assert int(noise._mix(np.array([1], dtype=np.uint32))[0]) == x
    assert noise.MIX_SHIFTS == (16, 15, 16) and noise.MIX_MULTIPLIERS == (0x7FEB352D, 0x846CA68B)
    assert noise._mix_int(0) == 0, "0 is the mixer's fixed point: the reason the seed is salted"
    sample = noise._mix(np.arange(1 << 16, dtype=np.uint32))
    assert len(np.unique(sample)) == 1 << 16, "a permutation has no collisions"


def test_hash_matches_the_independent_implementation_on_thousands_of_inputs():
    rng = np.random.default_rng(55)
    checked = 0
    for _ in range(40):
        seed, octave = int(rng.integers(0, 2**32)), int(rng.integers(0, 2**32))
        cells = rng.integers(-(2**31), 2**31, size=(3, 100))
        cells[:, :6] = [[0, 1, -1, 2**31 - 1, -(2**31), 255]] * 3
        two = noise.lattice_hash(seed, octave, cells[0], cells[1])
        three = noise.lattice_hash(seed, octave, cells[0], cells[1], cells[2])
        assert two.dtype == np.uint32 and three.dtype == np.uint32
        for n in range(100):
            ix, iy, iz = (int(c) for c in cells[:, n])
            assert int(two[n]) == ref_hash(seed, octave, ix, iy)
            assert int(three[n]) == ref_hash(seed, octave, ix, iy, iz)
            checked += 2
    assert checked == 8000
    # The edge seeds, as scalars.
    for seed in (0, 1, 0x9E3779B9, MASK):
        for octave in (0, 31, MASK):
            assert int(noise.lattice_hash(seed, octave, -7, 3)) == ref_hash(seed, octave, -7, 3)
            assert int(noise.lattice_hash(seed, octave, -7, 3, -(2**31))) == ref_hash(seed, octave, -7, 3, -(2**31))


def test_negative_cells_are_twos_complement_and_every_integer_type_agrees():
    assert int(noise.lattice_hash(3, 0, -1, -(2**31))) == int(noise.lattice_hash(3, 0, np.uint32(MASK), np.uint32(2**31)))
    cells = np.array([-5, -1, 0, 1, 70000])
    want = noise.lattice_hash(9, 2, cells, cells[::-1])
    for kind in (np.int32, np.int64):
        assert np.array_equal(noise.lattice_hash(9, 2, cells.astype(kind), cells[::-1].astype(kind)), want)
    assert np.array_equal(noise.lattice_hash(9, 2, cells.astype(np.int64).astype(np.uint32), cells[::-1].astype(np.int64).astype(np.uint32)), want)
    assert noise.lattice_hash(9, 2, cells[:, None], cells[None, :]).shape == (5, 5)
    with pytest.raises(noise.NoiseError):
        noise.lattice_hash(9, 2, 2**32, 0)
    with pytest.raises(noise.NoiseError):
        noise.lattice_hash(9, 2, 0.5, 0)


def bit_frequencies(diff: np.ndarray) -> np.ndarray:
    """How often each of the 32 bits is set across an array of uint32."""
    return ((diff[:, None] >> np.arange(32, dtype=np.uint32)) & np.uint32(1)).mean(axis=0)


def measure_avalanche(samples: int = 4096) -> dict:
    """Flip one input bit; count which output bits flip. Per input: 32 bits x `samples` base inputs."""
    rng = np.random.default_rng(7)
    side = int(math.isqrt(samples))
    out = {}
    cells = rng.integers(-(2**31), 2**31, size=(3, samples))
    seed, octave = 20261004, 3
    base = noise.lattice_hash(seed, octave, *cells)
    for axis, name in enumerate(("ix", "iy", "iz")):
        freq = np.zeros((32, 32))
        for bit in range(32):
            flipped = cells.copy()
            flipped[axis] = ((flipped[axis] + 2**31) ^ (1 << bit)) - 2**31
            freq[bit] = bit_frequencies(base ^ noise.lattice_hash(seed, octave, *flipped))
        out[name] = freq
    # Seed and octave are per-call scalars: `side` values of each against `side` cells.
    few = cells[:, :side]
    for name in ("seed", "octave"):
        freq = np.zeros((32, 32))
        for value in rng.integers(0, 2**32, size=side):
            args = (int(value), octave) if name == "seed" else (seed, int(value))
            base_few = noise.lattice_hash(*args, *few)
            for bit in range(32):
                other = (int(value) ^ (1 << bit), octave) if name == "seed" else (seed, int(value) ^ (1 << bit))
                freq[bit] += bit_frequencies(base_few ^ noise.lattice_hash(*other, *few))
        out[name] = freq / side
    return out


def test_avalanche_flipping_one_input_bit_flips_half_the_output_bits():
    """Known: 16 of 32 bits, each with probability 1/2. Sampling error of one frequency over 4096 trials: 0.008.

    Tolerances: the mean number of flipped bits per input bit within 0.4 of 16 (one count's error is 0.044;
    the mixer's own bias is allowed for); each of the 5 x 32 x 32 frequencies within 0.05 of 0.5 (six
    standard errors: 5120 frequencies are read, so four is expected by chance).
    """
    for name, freq in measure_avalanche().items():
        flipped = freq.sum(axis=1)
        assert np.all(np.abs(flipped - 16.0) < 0.4), (name, flipped.min(), flipped.max())
        assert np.all(np.abs(freq - 0.5) < 0.05), (name, freq.min(), freq.max())


def test_lattice_value_is_the_same_number_in_both_precisions():
    h = np.random.default_rng(1).integers(0, 2**32, size=20000, dtype=np.uint32)
    v64, v32 = noise.lattice_value(h), noise.lattice_value(h, np.float32)
    assert v64.dtype == np.float64 and v32.dtype == np.float32
    assert np.array_equal(v64, v32.astype(np.float64)), "float32 and float64 agree to the bit"
    assert np.array_equal(v64 * 2.0**23, np.round(v64 * 2.0**23)), "multiples of 2^-23"
    assert float(noise.lattice_value(np.uint32(0))) == -1.0
    assert float(noise.lattice_value(np.uint32(MASK))) == 1.0 - 2.0**-23
    assert float(noise.lattice_value(np.uint32(0x80000000))) == 0.0
    assert float(noise.lattice_value(np.uint32(0xFF))) == -1.0, "the low 8 bits are not read"
    assert abs(v64.mean()) < 4.0 * math.sqrt(1 / 3 / 20000) and abs(v64.var() - 1 / 3) < 0.01


# --- determinism at a point --------------------------------------------------------------------------------------

PROBE = "import numpy as np; from galaxy.layer import noise as n; " "print(float(n.noise2(7, 0.3, -4.7, 2)).hex(), float(n.noise3(7, 0.3, -4.7, 12.25, 2)).hex(), " "float(n.fractal(7, [0.3, -4.7], 2.5, 5, base_frequency=0.75)).hex(), float(n.fractal(7, [0.3, -4.7, 1.5], 3.5, 4, base_frequency=0.75, dtype=np.float32)).hex(), " "int(n.lattice_hash(7, 2, -3, 11, 5)))"


def test_a_point_has_one_value_however_it_is_asked_for():
    rng = np.random.default_rng(2)
    p = rng.uniform(-50, 50, size=(3, 1000))
    for ft in (np.float64, np.float32):
        whole2 = noise.noise2(11, p[0], p[1], 4, ft)
        whole3 = noise.noise3(11, p[0], p[1], p[2], 4, ft)
        whole_f = noise.fractal(11, p.T, 2.5, 5, base_frequency=0.5, dtype=ft)
        assert whole2.dtype == ft and whole3.dtype == ft and whole_f.dtype == ft
        # Scalars, one at a time.
        for n in range(0, 1000, 97):
            assert noise.noise2(11, p[0, n], p[1, n], 4, ft) == whole2[n]
            assert noise.noise3(11, p[0, n], p[1, n], p[2, n], 4, ft) == whole3[n]
            assert noise.fractal(11, p[:, n], 2.5, 5, base_frequency=0.5, dtype=ft) == whole_f[n]
        # Any chunking, any order, any shape.
        for chunk in (1, 7, 333):
            parts = [noise.noise2(11, p[0, i : i + chunk], p[1, i : i + chunk], 4, ft) for i in range(0, 1000, chunk)]
            assert np.array_equal(np.concatenate(parts), whole2)
        order = rng.permutation(1000)
        assert np.array_equal(noise.noise3(11, p[0, order], p[1, order], p[2, order], 4, ft), whole3[order])
        assert np.array_equal(noise.fractal(11, p.T.reshape(10, 100, 3), 2.5, 5, base_frequency=0.5, dtype=ft), whole_f.reshape(10, 100))
        assert np.array_equal(noise.noise2(11, p[0, :5, None], p[1, None, :7], 4, ft), noise.noise2(11, *np.broadcast_arrays(p[0, :5, None], p[1, None, :7]), 4, ft))
    # The seed and the octave both matter.
    assert not np.array_equal(noise.noise2(11, p[0], p[1], 4), noise.noise2(12, p[0], p[1], 4))
    assert not np.array_equal(noise.noise2(11, p[0], p[1], 4), noise.noise2(11, p[0], p[1], 5))


def test_a_fresh_interpreter_under_another_hash_seed_returns_the_same_values():
    env = dict(os.environ, PYTHONHASHSEED="4242" if os.environ.get("PYTHONHASHSEED") != "4242" else "17", PYTHONPATH=str(ROOT / "model"))
    out = subprocess.run([sys.executable, "-c", PROBE], env=env, capture_output=True, text=True, check=True).stdout.split()
    want = [
        float(noise.noise2(7, 0.3, -4.7, 2)).hex(),
        float(noise.noise3(7, 0.3, -4.7, 12.25, 2)).hex(),
        float(noise.fractal(7, [0.3, -4.7], 2.5, 5, base_frequency=0.75)).hex(),
        float(noise.fractal(7, [0.3, -4.7, 1.5], 3.5, 4, base_frequency=0.75, dtype=np.float32)).hex(),
        str(int(noise.lattice_hash(7, 2, -3, 11, 5))),
    ]
    assert out == want


# --- one octave: mean, variance, continuity ----------------------------------------------------------------------


def measure_moments(points: int = 2**20, cells: int = 2**18) -> dict:
    rng = np.random.default_rng(1)
    out = {}
    for name, fn, dims in (("noise2", noise.noise2, 2), ("noise3", noise.noise3, 3)):
        g = fn(7, *rng.uniform(-2048.0, 2048.0, size=(dims, points)))
        out[name] = dict(mean=float(g.mean()), variance=float(g.var()), largest=float(np.abs(g).max()))
        corner = rng.integers(-30000, 30000, size=(dims, cells)).astype(float)
        fixed = {}
        for where in ((0.0, 0.0, 0.0), (0.5, 0.5, 0.5), (0.5, 0.0, 0.0), (0.3, 0.7, 0.1)):
            fixed[where[:dims]] = float(fn(7, *(corner[axis] + where[axis] for axis in range(dims))).var())
        out[name]["fixed"] = fixed
    return out


def test_one_octave_has_mean_zero_and_variance_one_at_every_point_of_the_cell():
    """Derived: variance 1 at every point (the division by sqrt(n / 3)); mean -2^-24 sqrt(3 / n), unmeasurable.

    2^20 points over 4096^2 cells are independent to good approximation: the mean's standard error is 1e-3 and
    the variance's 1.1e-3 (kurtosis 2.1 to 2.2). Tolerances are five standard errors. At a fixed position in
    the cell over 2^18 cells the variance's standard error is 0.0018 to 0.0026: tolerance 0.012.
    """
    for name, m in measure_moments().items():
        assert abs(m["mean"]) < 5.0e-3, (name, m)
        assert abs(m["variance"] - 1.0) < 6.0e-3, (name, m)
        assert m["largest"] <= (2.0 * math.sqrt(3.0) if name == "noise2" else 2.0 * math.sqrt(6.0)), (name, m)
        for where, variance in m["fixed"].items():
            assert abs(variance - 1.0) < 0.012, (name, where, variance)


def test_plain_value_noise_would_not_have_unit_variance_and_this_says_by_how_much():
    """The closed form the division rests on: the interpolated value's variance is n / 3."""
    rng = np.random.default_rng(3)
    corner = rng.integers(-30000, 30000, size=(2, 2**17)).astype(float)
    for tx, ty in ((0.0, 0.0), (0.5, 0.5), (0.25, 0.5)):
        sx, sy = (float(noise._fade(np.float64(t))) for t in (tx, ty))
        n = (1 - 2 * sx * (1 - sx)) * (1 - 2 * sy * (1 - sy))
        raw = noise.noise2(5, corner[0] + tx, corner[1] + ty) * math.sqrt(n / 3.0)
        assert raw.var() == pytest.approx(n / 3.0, rel=0.02), (tx, ty)
    assert (1 - 2 * 0.5 * 0.5) ** 2 / 3 == pytest.approx(1 / 12)


def test_value_and_first_derivative_are_continuous_across_cell_edges():
    """The quintic has zero slope and curvature at 0 and 1, so the noise meets a cell edge flat: s(e) ~ 10 e^3.

    Value: 2^-16 either side of an edge differs from the edge by ~ 10 * 2^-48 * a few: below 1e-12.
    Derivative across the edge: the one-sided quotients at h = 2^-10 are ~ 10 h^2 * a few ~ 5e-5: below 3e-4,
    where the same quotient in mid-cell is of order one. Derivative along the edge: the same either side.
    """
    rng = np.random.default_rng(4)
    edge = rng.integers(-100, 100, size=4000).astype(float)
    along = rng.uniform(-100, 100, size=4000)
    other = rng.uniform(-100, 100, size=4000)
    tiny, h = 2.0**-16, 2.0**-10
    fields = {
        "noise2 x": lambda d, a: noise.noise2(3, edge + d, along + a),
        "noise2 y": lambda d, a: noise.noise2(3, along + a, edge + d),
        "noise3 x": lambda d, a: noise.noise3(3, edge + d, along + a, other),
        "noise3 z": lambda d, a: noise.noise3(3, along + a, other, edge + d),
        "fractal x": lambda d, a: noise.fractal(3, np.stack([edge + d, along + a], axis=-1), 2.5, 3, base_frequency=1.0),
    }
    for name, f in fields.items():
        at = f(0.0, 0.0)
        # A three-octave sum's finest octave sees the step four times larger: 64 times the cube (measured 3e-12).
        flat = 1e-10 if name.startswith("fractal") else 1e-12
        assert np.max(np.abs(f(-tiny, 0.0) - at)) < flat, name
        assert np.max(np.abs(f(tiny, 0.0) - at)) < flat, name
        if name.startswith("fractal"):
            continue  # the next assertions are one octave's
        left, right = (at - f(-h, 0.0)) / h, (f(h, 0.0) - at) / h
        assert np.max(np.abs(left)) < 3e-4 and np.max(np.abs(right)) < 3e-4, (name, np.abs(left).max(), np.abs(right).max())
        mid = (f(0.5 + h, 0.0) - f(0.5 - h, 0.0)) / (2 * h)
        assert np.median(np.abs(mid)) > 0.3, (name, "mid-cell slope is of order one")
        tangent = [(f(d, h) - f(d, -h)) / (2 * h) for d in (-tiny, tiny)]
        assert np.max(np.abs(tangent[0] - tangent[1])) < 1e-9, name


# --- spectra ------------------------------------------------------------------------------------------------------


def grid(n: int, length: float = 1.0) -> np.ndarray:
    axis = (np.arange(n) + 0.5) * (length / n)
    return np.stack(np.meshgrid(axis, axis, indexing="ij"), axis=-1)


def power(field: np.ndarray, length: float):
    """The 2-D periodogram of a Hann-windowed square field: (kx, ky, power), k in cycles per unit length."""
    n = field.shape[0]
    window = np.hanning(n + 1)[:-1]
    spectrum = np.abs(np.fft.fft2((field - field.mean()) * window[:, None] * window[None, :])) ** 2
    k = np.fft.fftfreq(n, d=length / n)
    return np.broadcast_to(k[:, None], spectrum.shape), np.broadcast_to(k[None, :], spectrum.shape), spectrum


BAND = (4.0, 64.0)  # base_frequency to a quarter of the finest octave's (256)
BINS = 12


def fitted_slope(kx, ky, spectrum) -> tuple[float, float]:
    """(slope, rms residual in dex) of mean power in BINS logarithmic bins of |k| over BAND."""
    edges = np.geomspace(*BAND, BINS + 1)
    k = np.hypot(kx, ky).ravel()
    index = np.digitize(k, edges) - 1
    inside = (index >= 0) & (index < BINS)
    mean = np.bincount(index[inside], weights=spectrum.ravel()[inside], minlength=BINS) / np.bincount(index[inside], minlength=BINS)
    centre = np.sqrt(edges[:-1] * edges[1:])
    fit = np.polyfit(np.log10(centre), np.log10(mean), 1)
    return float(-fit[0]), float(np.std(np.log10(mean) - np.polyval(fit, np.log10(centre))))


def measure_slopes(ndim: int, slopes, seeds: int, lacunarity: float = 2.0, octaves: int = 7) -> dict:
    points = grid(512)
    out = {}
    for slope in slopes:
        stacked, singles = 0.0, []
        for seed in range(seeds):
            p = points if ndim == 2 else np.concatenate([points, np.full(points.shape[:-1] + (1,), 0.3 + seed)], axis=-1)
            kx, ky, spectrum = power(noise.fractal(seed, p, slope, octaves, base_frequency=4.0, lacunarity=lacunarity), 1.0)
            stacked = stacked + spectrum
            singles.append(fitted_slope(kx, ky, spectrum)[0])
        out[slope] = dict(zip(("slope", "ripple"), fitted_slope(kx, ky, stacked)), singles=singles)
    return out


def test_fractal_spectrum_has_the_slope_it_was_asked_for_in_two_dimensions():
    """Known: the slope asked for (derived: a_j^2 = L^(j (2 - slope)), the top octave carrying the missing ones).

    512^2 samples of the unit square, 7 octaves from 4 to 256 cells, band 4 to 64, 4 seeds stacked. Measured
    1.495, 2.497, 3.544 (twelve seeds: 1.527, 2.520, 3.544). One seed's fitted slope scatters by 0.08 to 0.10
    rms (the lowest bins hold 36 to 64 modes), so four stacked scatter by about 0.045; the tolerance, 0.15,
    is three of those. The ripple about the line (measured 0.04, 0.05, 0.08 dex) is asserted below 0.1 dex,
    and to grow with the slope: the staircase the docstring describes.
    """
    measured = measure_slopes(2, (1.5, 2.5, 3.5), 4)
    for slope, m in measured.items():
        assert abs(m["slope"] - slope) < 0.15, (slope, m)
        assert m["ripple"] < 0.1, (slope, m)
        assert all(abs(single - slope) < 0.35 for single in m["singles"]), (slope, m)
    assert measured[1.5]["ripple"] < measured[3.5]["ripple"]


def test_a_plane_through_a_three_dimensional_fractal_is_one_power_shallower():
    """Known: slope - 1 (derived in `fractal`: the plane's spectrum is the 3-D one integrated along k_z).

    As the 2-D test, 3 seeds stacked (each on its own plane). Measured 1.62 for 1.5 and 2.57 for 2.5; eight
    seeds measure 1.57 and 2.53. The plane is systematically steeper than slope - 1, by 0.03 to 0.07, for the
    reason `fractal` gives (the missing octaves above the finest one matter more to a plane than to the 3-D
    spectrum). The tolerance, 0.2, is that 0.07 plus three times the stacked sampling error, 0.045; the sign
    of the offset is asserted too, so that the tolerance is not read as agreement.
    """
    measured = measure_slopes(3, (2.5, 3.5), 3)
    for slope, m in measured.items():
        assert abs(m["slope"] - (slope - 1.0)) < 0.2, (slope, m)
    assert measured[2.5]["slope"] > 1.5, "steeper than the endless sum's slope, not shallower"
    assert measured[3.5]["slope"] - measured[2.5]["slope"] == pytest.approx(1.0, abs=0.15), "one more power asked, one more measured"


def measure_octave_spectrum(seeds: int = 2) -> dict:
    """One octave, 64 cells across, 16 samples per cell: where its variance lies, and along which directions."""
    cells = 64.0
    points = np.moveaxis(grid(1024, cells), -1, 0)
    stacked = 0.0
    for seed in range(seeds):
        kx, ky, spectrum = power(noise.noise2(seed, *points), cells)
        stacked = stacked + spectrum
    k = np.hypot(kx, ky)
    order = np.argsort(k, axis=None)
    cumulative = np.cumsum(stacked.ravel()[order]) / stacked.sum()

    def quantile(q):
        return float(k.ravel()[order][np.searchsorted(cumulative, q)])

    fourfold = np.cos(4.0 * np.arctan2(ky, kx))  # +1 along the lattice axes, -1 along the diagonals

    def axes_over_diagonals(lo, hi):
        band = (k >= lo) & (k < hi)
        return float(stacked[band & (fourfold > 0.7071)].mean() / stacked[band & (fourfold < -0.7071)].mean())

    plateau = stacked[(k > 0.03) & (k < 0.1)].mean()
    return dict(
        half=quantile(0.5),
        ninety=quantile(0.9),
        above_one=float(stacked[k >= 1.0].sum() / stacked.sum()),
        quarter_level=float(stacked[(k > 0.22) & (k < 0.28)].mean() / plateau),
        low=axes_over_diagonals(0.1, 0.5),
        middle=axes_over_diagonals(0.5, 1.0),
        high=axes_over_diagonals(1.0, 2.0),
    )


def test_one_octave_is_a_low_pass_and_its_lattice_signature_is_the_stated_one():
    """The numbers `noise2` states about its own spectrum: half the variance below 0.35 cycles per cell, 90 %
    below 0.63, 3.4 % above 1; 0.96 of the plateau at a quarter of a cycle; axes over diagonals 1.01, 0.83
    and 48 in the three bands. 2 x 4096 cells: the tolerances are a few per cent of each, wider on the
    ratio in the last band, which is a ratio of two small powers."""
    m = measure_octave_spectrum()
    assert m["half"] == pytest.approx(0.35, abs=0.03), m
    assert m["ninety"] == pytest.approx(0.63, abs=0.04), m
    assert m["above_one"] == pytest.approx(0.034, abs=0.01), m
    assert m["quarter_level"] == pytest.approx(0.96, abs=0.1), m  # still on the plateau at a quarter of a cycle per cell
    assert m["low"] == pytest.approx(1.0, abs=0.08), m  # isotropic where most of the variance is
    assert m["middle"] == pytest.approx(0.83, abs=0.1), m
    assert 25.0 < m["high"] < 100.0, m


def measure_variance(points: int = 2**17) -> dict:
    rng = np.random.default_rng(5)
    out = {}
    for ndim, slopes, counts in ((2, (1.0, 2.0, 3.0, 4.0), (1, 3, 6)), (3, (2.0, 4.0), (1, 4))):
        p = rng.uniform(-500.0, 500.0, size=(points, ndim))
        for slope in slopes:
            for octaves in counts:
                out[ndim, slope, octaves] = float(noise.fractal(11, p, slope, octaves, base_frequency=1.0).var())
    return out


def test_fractal_has_unit_variance_for_any_slope_and_octave_count():
    """Derived: 1 at every point (octave_weights' normaliser). 2^17 points over 1000 outer scales: the
    sample variance's standard error is 0.003 to 0.004; tolerance 0.02."""
    for key, variance in measure_variance().items():
        assert abs(variance - 1.0) < 0.02, (key, variance)


def test_octave_weights_are_the_derived_ones_and_fractal_is_their_sum():
    for ndim in (2, 3):
        for slope in (0.5, 1.5, float(ndim), 3.7):
            for lac in (2.0, math.sqrt(2.0), 3.0):
                for octaves in (1, 2, 7):
                    gain, top, norm = noise.octave_weights(slope, octaves, lac, ndim)
                    assert gain == pytest.approx(lac ** ((ndim - slope) / 2.0), rel=1e-14)
                    assert top == pytest.approx(1.0 / math.sqrt(1.0 - lac**-slope), rel=1e-14)
                    r = lac ** (ndim - slope)
                    body = (octaves - 1) if abs(r - 1.0) < 1e-12 else (r ** (octaves - 1) - 1.0) / (r - 1.0)
                    assert norm == pytest.approx(1.0 / math.sqrt(body + top**2 * r ** (octaves - 1)), rel=1e-12)
    # Two and three dimensions differ by sqrt(L) per octave for the same slope.
    assert noise.octave_weights(2.5, 5, 2.0, 3)[0] / noise.octave_weights(2.5, 5, 2.0, 2)[0] == pytest.approx(math.sqrt(2.0))
    assert noise.octave_weights(2.0, 4, 2.0, 2)[0] == 1.0 and noise.octave_weights(3.0, 4, 2.0, 3)[0] == 1.0

    # The sum, written out here from the single octaves.
    p = np.random.default_rng(6).uniform(-20, 20, size=(500, 3))
    for ndim, one in ((2, noise.noise2), (3, noise.noise3)):
        gain, top, norm = noise.octave_weights(2.2, 5, 2.0, ndim)
        total = sum((top if j == 4 else 1.0) * gain**j * one(13, *(p[:, a] * (0.75 * 2.0**j) for a in range(ndim)), octave=j) for j in range(5))
        got = noise.fractal(13, p[:, :ndim], 2.2, 5, base_frequency=0.75)
        assert np.max(np.abs(got - total * norm)) < 1e-13
    # Fewer octaves are the same coarse octaves: the first octave of a sum is octave 0 of the seed.
    assert np.allclose(noise.fractal(13, p[:, :2], 2.2, 1, base_frequency=0.75), noise.noise2(13, p[:, 0] * 0.75, p[:, 1] * 0.75, 0), rtol=0, atol=1e-14)


# --- shear --------------------------------------------------------------------------------------------------------


def test_shear_is_the_stated_map_and_a_sheared_field_is_the_field_at_sheared_coordinates():
    rng = np.random.default_rng(8)
    p = rng.uniform(-30, 30, size=(200, 3))
    for s in (0.0, 0.5, -1.25, 3.0):
        q = noise.shear(p, s)
        assert np.array_equal(q[:, 0], p[:, 0] - s * p[:, 1]) and np.array_equal(q[:, 1:], p[:, 1:])
        assert np.array_equal(noise.shear(p[:, :2], s), q[:, :2])
        assert np.array_equal(noise.noise2(4, *noise.shear(p[:, :2], s).T), noise.noise2(4, p[:, 0] - s * p[:, 1], p[:, 1]))
        assert np.array_equal(noise.shear(noise.shear(p, s), -s), p) or np.allclose(noise.shear(noise.shear(p, s), -s), p, atol=1e-12)
    assert noise.shear(p.astype(np.float32), 0.5, np.float32).dtype == np.float32
    original = p.copy()
    noise.shear(p, 2.0)
    assert np.array_equal(p, original), "the caller's array is not written"


def test_shear_anisotropy_is_the_ellipse_of_the_sheared_moment_tensor():
    """The closed form against an eigen-decomposition of S^T S done here."""
    assert noise.shear_anisotropy(0.0)[0] == 1.0 and math.isnan(noise.shear_anisotropy(0.0)[1])
    for s in (0.01, 0.5, 1.0, 2.0, 7.0, -0.5, -3.0):
        shear_matrix = np.array([[1.0, -s], [0.0, 1.0]])
        values, vectors = np.linalg.eigh(shear_matrix.T @ shear_matrix)
        ratio, tilt = noise.shear_anisotropy(s)
        assert ratio == pytest.approx(math.sqrt(values[1] / values[0]), rel=1e-12)
        assert ratio == pytest.approx(values[1], rel=1e-12), "the eigenvalues multiply to 1"
        major = math.atan2(vectors[1, 1], vectors[0, 1])
        assert math.sin(tilt - major) == pytest.approx(0.0, abs=1e-12), "the same axis, modulo pi"
        assert math.tan(2.0 * tilt) == pytest.approx(2.0 / s, rel=1e-12)
    assert math.degrees(noise.shear_anisotropy(1e-9)[1]) == pytest.approx(-45.0, abs=1e-6)
    assert math.degrees(noise.shear_anisotropy(1e9)[1]) == pytest.approx(-90.0, abs=1e-6)
    assert noise.shear_anisotropy(1.0)[0] == pytest.approx((3.0 + math.sqrt(5.0)) / 2.0)


def measure_anisotropy(strain: float, seeds: int = 2) -> tuple[float, float]:
    """(axis ratio, tilt in radians) of the measured spectrum's second-moment tensor: one octave, 64 cells
    across, 16 samples per cell (a shear of 2 puts power up to 2.4 times further out: 8 per cell aliases)."""
    cells = 64.0
    points = noise.shear(grid(1024, cells), strain)
    stacked = 0.0
    for seed in range(seeds):
        kx, ky, spectrum = power(noise.noise2(seed, points[..., 0], points[..., 1]), cells)
        stacked = stacked + spectrum
    xy = float((stacked * kx * ky).sum())
    moment = np.array([[float((stacked * kx * kx).sum()), xy], [xy, float((stacked * ky * ky).sum())]])
    values, vectors = np.linalg.eigh(moment)
    return math.sqrt(values[1] / values[0]), math.atan2(vectors[1, 1], vectors[0, 1])


def test_the_measured_spectrum_under_shear_has_the_derived_ellipse():
    """Known: shear_anisotropy(s): ratios 1.640, 2.618, 5.828, 2.618 and tilts -52.0, -58.3, -67.5, +58.3
    degrees for s = 0.5, 1, 2, -1. Measured: ratios low by 0.8, 1.0, 1.7 and 0.1 per cent, tilts off by 0.04,
    0.05, 0.05 and 0.6 degrees. 2 x 4096 cells: one seed's ratio scatters by 1 to 2 per cent and its tilt by
    half a degree to a degree; at s = 2 the sampling (16 per cell) still clips a little of the sheared
    spectrum, which lowers the ratio (at 8 per cell it reads 5.07). Tolerances: 4 per cent on the ratio, 1.5
    degrees on the tilt. Unsheared, the ratio is 1 to the sampling error (measured 1.013, asserted below
    1.05) and there is no axis."""
    assert measure_anisotropy(0.0)[0] < 1.05
    for s in (0.5, 1.0, 2.0, -1.0):
        want_ratio, want_tilt = noise.shear_anisotropy(s)
        ratio, tilt = measure_anisotropy(s)
        assert ratio == pytest.approx(want_ratio, rel=0.04), (s, ratio, want_ratio)
        off = math.degrees(math.asin(math.sin(tilt - want_tilt)))  # an axis: modulo pi
        assert abs(off) < 1.5, (s, math.degrees(tilt), math.degrees(want_tilt))


# --- the log-normal map --------------------------------------------------------------------------------------------

FIELD = dict(slope=2.5, base_frequency=1.0)  # on unit cells: octave j has 2^j lattice cells across a cell


def cells_quadrature(side: int, n: int) -> np.ndarray:
    """Quadrature points of a side x side grid of unit cells: (side * side, n * n, 2)."""
    return np.stack([noise.cell_quadrature(i, i + 1, j, j + 1, n) for j in range(side) for i in range(side)])


@functools.lru_cache(maxsize=None)
def field_on_cells(side: int, n: int, octaves: int) -> np.ndarray:
    return noise.fractal(21, cells_quadrature(side, n), octaves=octaves, **FIELD)


def measure_lognormal(sigma: float, n: int = noise.DEFAULT_QUADRATURE, octaves: int = 3, side: int = 16, dense: int = 64) -> dict:
    """The map's mean over each of side^2 unit cells: on the cell's n x n quadrature, and on a dense lattice.

    Three octaves put 4 finest lattice cells across a cell (n = 16 is then 4 points per finest cell: the rule
    of `cell_quadrature`); four octaves put 8 (2 points per finest cell: half the rule).
    """
    g_quadrature, g_dense = field_on_cells(side, n, octaves), field_on_cells(side, dense, octaves)
    normaliser = noise.lognormal_normaliser(g_quadrature, sigma)
    on = noise.lognormal_map(g_quadrature, sigma, normaliser[:, None]).mean(axis=-1)
    off = noise.lognormal_map(g_dense, sigma, normaliser[:, None]).mean(axis=-1)
    return dict(
        on_worst=float(np.abs(on - 1.0).max()),
        off_rms=float(np.sqrt(np.mean((off - 1.0) ** 2))),
        off_worst=float(np.abs(off - 1.0).max()),
        normaliser=(float(normaliser.min()), float(normaliser.max())),
        smallest=float(noise.lognormal_map(g_dense, sigma, normaliser[:, None]).min()),
    )


def test_cell_quadrature_is_the_midpoint_lattice():
    q = noise.cell_quadrature(2.0, 4.0, -1.0, 0.0, 4)
    assert q.shape == (16, 2)
    assert np.array_equal(q[:4, 0], [2.25, 2.75, 3.25, 3.75]) and np.array_equal(q[:4, 1], [-0.875] * 4)
    assert np.array_equal(q[4], [2.25, -0.625]), "point j * n + i: i along the first coordinate"
    assert noise.cell_quadrature(0, 1, 0, 1).shape == (noise.DEFAULT_QUADRATURE**2, 2)
    assert np.array_equal(noise.cell_quadrature(0, 1, 0, 1), noise.cell_quadrature(0, 1, 0, 1)), "fixed points"
    with pytest.raises(noise.NoiseError):
        noise.cell_quadrature(0, 1, 0, 1, 0)


def test_the_lognormal_map_has_quadrature_mean_one_in_every_cell_and_is_positive():
    """Known: 1, by construction, to rounding. 256 cells, three widths: |mean - 1| below 1e-12."""
    for sigma in (0.5, 1.0, 1.5, 3.0):
        for octaves in (3, 4):
            m = measure_lognormal(sigma, octaves=octaves)
            assert m["on_worst"] < 1e-12, (sigma, m)
            assert m["smallest"] > 0.0, (sigma, m)
    # Weighted: a cell whose measure grows along the first coordinate (an annulus sector's, say).
    q = cells_quadrature(4, 8)
    g = noise.fractal(21, q, octaves=3, **FIELD)
    weights = 1.0 + q[..., 0]
    normaliser = noise.lognormal_normaliser(g, 1.0, weights)
    mean = (weights * noise.lognormal_map(g, 1.0, normaliser[:, None])).sum(axis=-1) / weights.sum(axis=-1)
    assert np.max(np.abs(mean - 1.0)) < 1e-12
    assert np.allclose(noise.lognormal_normaliser(g, 1.0, np.ones(64)), noise.lognormal_normaliser(g, 1.0), rtol=1e-14)
    assert float(noise.lognormal_normaliser(np.zeros(9), 1.0)) == pytest.approx(math.exp(0.5)), "a constant field: the map is 1"
    assert float(noise.lognormal_map(0.0, 1.0, noise.lognormal_normaliser(np.zeros(9), 1.0))) == pytest.approx(1.0)
    with pytest.raises(noise.NoiseError):
        noise.lognormal_normaliser(g, 1.0, -weights)


def test_the_lognormal_map_away_from_the_quadrature_points_is_as_close_to_one_as_stated():
    """`lognormal_map`'s numbers: the mean over a 64 x 64 midpoint lattice per cell, 256 unit cells, under the
    normaliser of the n x n quadrature. Each bound is the docstring's measured worst case rounded up by a
    half or so: a bound on a deterministic number, not a fit. (A 128 x 128 lattice moves the worst case at
    sigma 1, n 16, four octaves from 0.02082 to 0.02084: 64 is dense enough.)"""
    # measured worst cases: 9.5e-4, 3.6e-3, 8.0e-3; 0.059; 4.2e-5; 0.021; 1.1e-3
    stated = {(0.5, 16, 3): 1.5e-3, (1.0, 16, 3): 5e-3, (1.5, 16, 3): 1.2e-2, (1.0, 8, 3): 8e-2, (1.0, 32, 3): 7e-5, (1.0, 16, 4): 3e-2, (1.0, 32, 4): 1.6e-3}
    for (sigma, n, octaves), bound in stated.items():
        m = measure_lognormal(sigma, n, octaves)
        assert m["off_worst"] < bound, (sigma, n, octaves, m)
        assert m["off_rms"] < m["off_worst"]
    worst = {n: measure_lognormal(1.0, n)["off_worst"] for n in (8, 16, 32)}
    assert worst[32] < worst[16] < worst[8], "more points, closer"
    assert measure_lognormal(1.0, 16, 4)["off_worst"] > 5.0 * worst[16], "half the rule's points is much worse"


def measure_population_mean(points: int = 2**18) -> dict:
    """The mean of exp(sigma g - sigma^2 / 2) with no normaliser, over points spread across 1000 outer scales."""
    g = noise.fractal(21, np.random.default_rng(1).uniform(-500.0, 500.0, size=(points, 2)), octaves=3, **FIELD)
    return {sigma: float(noise.lognormal_map(g, sigma).mean()) for sigma in (0.5, 1.0, 1.5)}


def test_without_a_normaliser_the_map_has_unit_mean_only_roughly():
    """Why the normaliser exists. exp(sigma g - sigma^2/2) has mean 1 for a Gaussian g; the octave sum's
    tails are lighter, so it falls short, more at larger sigma. Stated: 0.999, 0.987, 0.941. 2^18 points: the
    sampling error at sigma 1.5 is about 0.005; tolerances 0.01 to 0.02."""
    m = measure_population_mean()
    assert m[0.5] == pytest.approx(0.999, abs=0.01), m
    assert m[1.0] == pytest.approx(0.987, abs=0.015), m
    assert m[1.5] == pytest.approx(0.941, abs=0.02), m
    assert m[1.5] < m[1.0] < m[0.5] < 1.005


# --- float32 ------------------------------------------------------------------------------------------------------


def measure_float32_drift() -> dict:
    """float32 against float64 at positions that are not exact in float32, by the size of the coordinate."""
    rng = np.random.default_rng(9)
    out = {}
    for limit in (16.0, 1024.0, 10000.0):
        p = rng.uniform(-limit, limit, size=(3, 200000))
        out[limit] = (
            float(np.abs(noise.noise2(5, p[0], p[1], 1, np.float32) - noise.noise2(5, p[0], p[1], 1)).max()),
            float(np.abs(noise.noise3(5, p[0], p[1], p[2], 1, np.float32) - noise.noise3(5, p[0], p[1], p[2], 1)).max()),
        )
    return out


def test_float32_drifts_from_float64_with_the_size_of_the_coordinate_as_stated():
    """Not a defect of the construction: 24 bits of position. Stated (measured worst of 200 000 random
    positions, noise2 / noise3): 5.2e-6 / 6.0e-6 below 16, 3.5e-4 / 4.1e-4 below 1024, 5.0e-3 / 5.1e-3 below
    10 000. Bounds: twice those. It is also asserted to be that large: the float32 path at arbitrary
    positions is NOT within 1e-6 of float64, and the docstring says so."""
    drift = measure_float32_drift()
    for limit, bound in ((16.0, 1.2e-5), (1024.0, 8e-4), (10000.0, 1e-2)):
        assert max(drift[limit]) < bound, (limit, drift[limit])
        assert min(drift[limit]) > bound / 8.0, (limit, drift[limit])
    assert min(drift[10000.0]) > 100.0 * max(drift[16.0]), "it grows with the coordinate"


# --- the committed vectors ----------------------------------------------------------------------------------------


def load_vectors() -> dict:
    return json.loads(noise.VECTORS.read_text(encoding="utf-8"))


def differences(want, got, exact: bool, path: str = "") -> list[str]:
    """Where two vector documents differ: floats to the bit if `exact`, else to 1e-12 relative."""
    if isinstance(want, dict) and isinstance(got, dict):
        if list(want) != list(got):
            return [f"{path}: keys {list(want)} != {list(got)}"]
        exact_here = {"exact": True, "1e-12": False}.get(want.get("compare"), exact)
        return [d for key in want for d in differences(want[key], got[key], exact_here, f"{path}/{key}")]
    if isinstance(want, list) and isinstance(got, list):
        if len(want) != len(got):
            return [f"{path}: length {len(want)} != {len(got)}"]
        return [d for n, (a, b) in enumerate(zip(want, got)) for d in differences(a, b, exact, f"{path}[{n}]")]
    if isinstance(want, float) and isinstance(got, float) and not exact:
        return [] if abs(want - got) <= 1e-12 * max(1.0, abs(want)) else [f"{path}: {want!r} != {got!r}"]
    return [] if (type(want) is type(got) and want == got) else [f"{path}: {want!r} != {got!r}"]


def test_the_vectors_file_is_what_the_generator_writes_today():
    """A contract, not a cache: if the noise changes, this fails, and regenerating is a decision's act.

    Sections marked ``exact`` (integer arithmetic; +, -, *, /, sqrt, floor) are compared to the bit; the
    fractal and log-normal sections pass through pow and exp, which a C library need not round correctly,
    and are compared to 1e-12. The top level (version, constants) is exact.
    """
    text = noise.VECTORS.read_bytes().decode("utf-8")
    assert "\r" not in text and text.endswith("}\n")
    stored = json.loads(text)
    assert noise.render_vectors(stored) == text, "the file is in the generator's own layout"
    found = differences(stored, noise.build_vectors(), exact=True)
    assert not found, found[:10]


def test_the_vectors_cover_what_a_twin_must_match_and_their_inputs_are_exact_in_float32():
    v = load_vectors()
    assert v["version"] == noise.VECTORS_VERSION == 1
    assert v["hash"] == {"mixer": "lowbias32", "shifts": [16, 15, 16], "multipliers": [0x7FEB352D, 0x846CA68B], "seed_salt": 0x9E3779B9, "lattice_bits": 24}
    count = len(v["lattice_hash"]["rows"]) + len(v["noise2"]["rows"]) + len(v["noise3"]["rows"]) + len(v["shear"]["rows"])
    count += sum(len(c["rows"]) for c in v["fractal"]["cases"]) + sum(len(c["rows"]) for c in v["lognormal"]["cases"])
    assert count >= 600, count
    assert {c["slope"] for c in v["fractal"]["cases"] if c["ndim"] == 2} == {1.5, 3.0}, "fractal sums at two slopes"
    assert {c["ndim"] for c in v["fractal"]["cases"]} == {2, 3}

    def exact32(x) -> bool:
        return float(np.float32(x)) == float(x)

    hashed = v["lattice_hash"]["rows"]
    assert all(isinstance(value, int) for row in hashed for value in row if value is not None)
    assert any(row[4] is None for row in hashed) and any(row[4] is not None for row in hashed)
    assert any(min(row[2], row[3]) < 0 for row in hashed) and any(row[2] == -(2**31) for row in hashed) and any(row[2] == 2**31 - 1 for row in hashed)
    for row in hashed:
        cell = row[2:4] if row[4] is None else row[2:5]
        assert row[5] == ref_hash(row[0], row[1], *cell), row

    for name, dims in (("noise2", 2), ("noise3", 3)):
        rows = v[name]["rows"]
        positions = np.array([row[2 : 2 + dims] for row in rows])
        assert all(exact32(x) and x * 1024 == round(x * 1024) for x in positions.ravel()), name
        assert np.any(positions < 0) and np.any(np.abs(positions) > 4096), "negatives and large coordinates"
        on_lattice = np.all(positions == np.floor(positions), axis=1)
        centred = np.all(positions - np.floor(positions) == 0.5, axis=1)
        assert on_lattice.sum() >= 8 and centred.sum() >= 8, "lattice points and cell centres"
    for row in v["shear"]["rows"]:
        assert all(exact32(x) for x in row[2:5]) and exact32(row[3] - row[2] * row[4]), row
    for case in v["fractal"]["cases"]:
        top_frequency = case["base_frequency"] * case["lacunarity"] ** (case["octaves"] - 1)
        assert all(exact32(x) and exact32(x * top_frequency) for row in case["rows"] for x in row[: case["ndim"]])
        assert (case["gain"], case["top"], case["norm"]) == pytest.approx(noise.octave_weights(case["slope"], case["octaves"], case["lacunarity"], case["ndim"]), rel=1e-14)
    assert {c["sigma"] for c in v["lognormal"]["cases"]} == {0.5, 1.0, 1.5}


def measure_vectors_float32() -> dict:
    """The largest |float32 path - float64 reference| in each section of the vectors (log-normal: relative)."""
    v = load_vectors()
    worst = {}
    worst["noise2"] = max(abs(float(noise.noise2(s, x, y, o, np.float32)) - value) for s, o, x, y, value, _ in v["noise2"]["rows"])
    worst["noise3"] = max(abs(float(noise.noise3(s, x, y, z, o, np.float32)) - value) for s, o, x, y, z, value, _ in v["noise3"]["rows"])
    worst["shear"] = max(abs(float(noise.noise2(s, *noise.shear([x, y], strain, np.float32), o, np.float32)) - value) for s, o, strain, x, y, value, _ in v["shear"]["rows"])
    worst["fractal"] = 0.0
    for case in v["fractal"]["cases"]:
        kwargs = dict(base_frequency=case["base_frequency"], lacunarity=case["lacunarity"], dtype=np.float32)
        got = noise.fractal(case["seed"], [row[: case["ndim"]] for row in case["rows"]], case["slope"], case["octaves"], **kwargs)
        worst["fractal"] = max(worst["fractal"], float(np.abs(got - np.array([row[-2] for row in case["rows"]])).max()))
    worst["lognormal"] = 0.0
    for case in v["lognormal"]["cases"]:
        kwargs = dict(slope=case["slope"], octaves=case["octaves"], base_frequency=case["base_frequency"], lacunarity=case["lacunarity"], dtype=np.float32)
        g = noise.fractal(case["seed"], [row[:2] for row in case["rows"]], **kwargs)
        got = noise.lognormal_map(g, case["sigma"], case["normaliser"], np.float32)
        want = np.array([row[2] for row in case["rows"]])
        worst["lognormal"] = max(worst["lognormal"], float(np.abs(got / want - 1.0).max()))
    return worst


def test_the_float32_path_is_within_the_stated_bound_of_every_vector():
    """Known: FLOAT32_TOLERANCE = 1e-6. Measured worst per section: noise2 2.1e-7, noise3 2.4e-7, shear
    4.9e-7, fractal 5.5e-7, log-normal 2.6e-7 relative. The Phase V7 gate, 1e-5, has an order of magnitude
    over the bound. The stored float32 values are what the float32 path returns (the generator test checks
    them to the bit in the exact sections)."""
    assert load_vectors()["float32_tolerance"] == noise.FLOAT32_TOLERANCE == 1.0e-6
    worst = measure_vectors_float32()
    assert set(worst) == {"noise2", "noise3", "shear", "fractal", "lognormal"}
    for section, value in worst.items():
        assert 0.0 < value < noise.FLOAT32_TOLERANCE, (section, value)


def test_each_lognormal_vector_cell_has_quadrature_mean_one_under_its_stored_normaliser():
    for case in load_vectors()["lognormal"]["cases"]:
        field = dict(slope=case["slope"], octaves=case["octaves"], base_frequency=case["base_frequency"], lacunarity=case["lacunarity"])
        quadrature = noise.cell_quadrature(*case["cell"], case["n"])
        assert all(float(np.float32(x)) == float(x) for x in quadrature.ravel()), "the quadrature points are exact in float32"
        g = noise.fractal(case["seed"], quadrature, **field)
        assert float(noise.lognormal_map(g, case["sigma"], case["normaliser"]).mean()) == pytest.approx(1.0, abs=1e-12)
        assert case["normaliser"] == pytest.approx(float(noise.lognormal_normaliser(g, case["sigma"])), rel=1e-13)


# --- arguments ----------------------------------------------------------------------------------------------------


def test_arguments_outside_the_definition_are_refused():
    bad_calls = [
        lambda: noise.noise2(-1, 0.0, 0.0),
        lambda: noise.noise2(2**32, 0.0, 0.0),
        lambda: noise.noise2(1.5, 0.0, 0.0),
        lambda: noise.noise2(True, 0.0, 0.0),
        lambda: noise.noise2(1, 0.0, 0.0, octave=-1),
        lambda: noise.noise2(1, 0.0, 0.0, dtype=np.float16),
        lambda: noise.noise2(1, 2.0**31, 0.0),
        lambda: noise.noise2(1, float("nan"), 0.0),
        lambda: noise.noise3(1, 0.0, 0.0, float("inf")),
        lambda: noise.fractal(1, [0.0, 0.0], 2.5, 0, base_frequency=1.0),
        lambda: noise.fractal(1, [0.0, 0.0], 2.5, 33, base_frequency=1.0),
        lambda: noise.fractal(1, [0.0, 0.0], 0.0, 4, base_frequency=1.0),
        lambda: noise.fractal(1, [0.0, 0.0], 2.5, 4, base_frequency=0.0),
        lambda: noise.fractal(1, [0.0, 0.0], 2.5, 4, base_frequency=1.0, lacunarity=1.0),
        lambda: noise.fractal(1, [0.0, 0.0, 0.0, 0.0], 2.5, 4, base_frequency=1.0),
        lambda: noise.fractal(1, [1.0e9, 0.0], 2.5, 4, base_frequency=1.0),
        lambda: noise.shear([0.0], 1.0),
        lambda: noise.octave_weights(2.5, 4, 2.0, 4),
        lambda: noise.fold_seed(-1),
        lambda: noise.fold_seed(2**64),
    ]
    for n, call in enumerate(bad_calls):
        with pytest.raises(noise.NoiseError):
            call()
            pytest.fail(f"call {n} was accepted")
    assert issubclass(noise.NoiseError, ValueError)


def test_fold_seed_takes_a_project_seed_to_thirty_two_bits():
    from galaxy.core import seeds

    assert noise.fold_seed(0) == 0 and noise.fold_seed(MASK) == MASK
    assert noise.fold_seed(0x1234567800000000) == 0x12345678
    assert noise.fold_seed(0x12345678_9ABCDEF0) == 0x12345678 ^ 0x9ABCDEF0
    child = seeds.child(0, "texture", "gas_fluctuation")
    assert 0 <= noise.fold_seed(child) <= MASK
    assert noise.noise2(noise.fold_seed(child), 0.5, 0.5) == noise.noise2(noise.fold_seed(seeds.child(0, "texture", "gas_fluctuation")), 0.5, 0.5)


# --- where the layer stands in the repository --------------------------------------------------------------------


def imported_modules(path: Path) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = ("." * node.level) + (node.module or "")
            names.add(module)
            names.update(f"{module}.{alias.name}" for alias in node.names)
    return names


def test_the_noise_imports_only_numpy_and_the_standard_library():
    for name in imported_modules(ROOT / "model" / "galaxy" / "layer" / "noise.py"):
        top = name.split(".")[0]
        assert top == "numpy" or top in sys.stdlib_module_names, name
    assert imported_modules(ROOT / "model" / "galaxy" / "layer" / "__init__.py") <= {"__future__", "__future__.annotations"}


def test_nothing_in_the_stages_the_core_or_the_api_reads_the_layer_yet():
    """Phase R, item 2: the primitives have no reader in this branch. The first reader removes its package
    from this list in the decision that adds it."""
    package = ROOT / "model" / "galaxy"
    for folder in ("stages", "core", "api"):
        files = sorted((package / folder).rglob("*.py"))
        assert files, folder
        for path in files:
            for name in imported_modules(path):
                assert "layer" not in name.split("."), f"{path.relative_to(ROOT)} imports {name}"
