"""The randomness layer's noise primitives: a lattice noise a shader can reproduce.

Everything here is a pure function of a position, a 32-bit seed and a few numbers (BUILD_III section 1c, rule 5:
no stored grid is a field's definition). Nothing reads this module yet; the realisation stages and a GLSL twin
will, so each step is written as the exact sequence of operations a GLSL ES 3.00 program performs.

The pieces, in the order a caller composes them::

    lattice_hash     seed, octave, integer cell  ->  uint32          (32-bit integer arithmetic only)
    lattice_value    uint32  ->  a float in [-1, 1) on a 2^-23 grid   (exact in float32 and float64)
    noise2, noise3   one octave: value noise, quintic fade, unit variance at every point
    octave_weights   the per-octave gain, the top octave's factor and the unit-variance normaliser for a slope
    fractal          octaves summed to P(k) ~ k^-slope, unit variance at every point
    shear            x' = x - s y: a sheared field is the unsheared field at sheared coordinates
    shear_anisotropy the axis ratio and tilt that shear gives the power spectrum
    cell_quadrature, lognormal_normaliser, lognormal_map
                     a log-normal map whose quadrature mean is exactly 1 in every cell

**The noise is value noise, not gradient noise.** The trade: gradient noise is band-limited from below (each
octave is a band-pass, and less of its power lies along the lattice axes), while value noise costs one hash per
corner and nothing else, has lattice values that are exact in float32, and has a closed-form variance at every
point. The reasons for value noise here: (a) the GLSL twin must match committed vectors, and fewer float
operations leave fewer places to diverge; (b) a gradient noise is exactly zero at every lattice point, and with
lacunarity 2 the lattice points of the first octave are lattice points of every octave, so an octave sum would be
pinned to zero on a regular grid; (c) value noise's variance at a point is known in closed form, so it can be
divided out (below), which gradient noise's cannot be without a division by zero at the lattice points. What
value noise costs is stated as measured numbers in :func:`noise2` and :func:`fractal`: each octave is a
low-pass, not a band-pass, so an octave sum's spectrum ripples about its power law, and the little power an
octave has above one cycle per cell lies along the lattice axes.

**Unit variance at every point, not on average.** Plain value noise has variance 1/3 at a lattice point and 1/12
at a 2-D cell centre (1/24 in 3-D): its contrast is printed with the lattice. Each octave is therefore divided
by its own standard deviation at that point, which is a closed form of the fade weights (:func:`noise2`). The
result has variance 1 everywhere, so an octave sum has variance exactly the sum of its squared amplitudes
everywhere, and the unit-variance normaliser of :func:`fractal` is derived, not fitted.

**Float precision.** Every float function takes ``dtype``: ``np.float64`` (the reference) or ``np.float32``
(the same operations in single precision: what a shader computes). Measured over the committed vectors
(``vectors.json``, whose positions, frequencies and strains are exact in float32), the float32 path differs
from the float64 path by at most 2.1e-7 on noise2, 2.4e-7 on noise3, 4.9e-7 on the sheared cases, 5.5e-7 on
the fractal sums and 2.6e-7 (relative) on the log-normal map; ``FLOAT32_TOLERANCE`` (1e-6) is the bound the
test holds them to, an order of magnitude inside Phase V7's 1e-5.

That holds while the lattice coordinate (position times frequency) is exact in float32. When it is not (a
position or a frequency that is not a short binary fraction) it is rounded to 24 bits before the cell is
found, and the noise's slope, a few per lattice cell, turns that into a difference from float64 that grows
with the coordinate. Measured over 200 000 random positions, noise2 and noise3 alike: 6e-6 at coordinates
below 16, 4e-4 below 1024, 5e-3 below 10 000 (``tests/test_layer_noise.py``). So the construction is within
1e-6 of float64 on exact inputs and is not on arbitrary ones, and the reason is single precision's
resolution, not the construction: a shader has the same 24 bits, and at a coordinate of 10 000 they resolve
a thousandth of a cell. A caller who needs 1e-5 against float64 keeps lattice coordinates small: positions
relative to a nearby origin that is a whole number of the coarsest lattice cells.

**Cost** (S55's machine, numpy 2.5, best of seven, while another session's test suite was running: an upper
bound; nothing here is optimised beyond plain vectorisation). One octave over a million points: noise2 0.15 s
in float64 and 0.09 s in float32; noise3 0.25 s and 0.18 s. A six-octave 2-D sum over a 512 x 512 grid: 0.22 s
and 0.14 s.

**Regenerating the vectors** is a deliberate act a decision must record: ``uv run python -m galaxy.layer.noise
write-vectors``. The test recomputes every vector and fails if the file would change.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# The avalanche finaliser: "lowbias32", a two-round xorshift-multiply permutation of the 32-bit integers found by
# search for low avalanche bias [verified: C. Wellons, hash-prospector README, function `lowbias32`, "exact bias:
# 0.17353355999581582", https://github.com/skeeto/hash-prospector (README.md fetched and read 2026-10-04)]:
#     x ^= x >> 16;  x *= 0x7feb352d;  x ^= x >> 15;  x *= 0x846ca68b;  x ^= x >> 16;
MIX_SHIFTS = (16, 15, 16)
MIX_MULTIPLIERS = (0x7FEB352D, 0x846CA68B)

# Xored into the seed before its first mix. The mixer maps 0 to 0, so without a salt seed 0 and octave 0 would
# start every chain from 0. The value is floor(2^32 / golden ratio) [recall: the constant of Knuth's
# multiplicative hashing]; nothing depends on which odd constant it is.
SEED_SALT = 0x9E3779B9

MASK32 = 0xFFFFFFFF
LATTICE_BITS = 24  # the top 24 bits of a hash make the lattice value: a float32 mantissa holds exactly 24
LATTICE_LIMIT = 2.0**31  # |position * frequency| must stay below this: the cell index is a GLSL `int`
SQRT3 = math.sqrt(3.0)  # one over the standard deviation of a value uniform in [-1, 1)

DEFAULT_QUADRATURE = 16  # points per axis of a cell's midpoint lattice (see cell_quadrature)

FLOAT32_TOLERANCE = 1.0e-6  # the float32 path against float64 over the vectors (measured: module docstring)
VECTORS_VERSION = 1
VECTORS = Path(__file__).resolve().parent / "vectors.json"

_FLOAT_TYPES = (np.float64, np.float32)


class NoiseError(ValueError):
    """An argument outside what the noise is defined for."""


def _float_type(dtype) -> type:
    ft = np.dtype(dtype).type
    if ft not in _FLOAT_TYPES:
        raise NoiseError(f"dtype must be float64 or float32, got {np.dtype(dtype).name}")
    return ft


def _uint(value, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise NoiseError(f"{what} must be an int, got {type(value).__name__}")
    if not 0 <= int(value) <= MASK32:
        raise NoiseError(f"{what} must lie in [0, 2^32), got {value}")
    return int(value)


def fold_seed(seed: int) -> int:
    """A 32-bit seed from one of the project's 64-bit seeds: the low half xor the high half.

    ``galaxy.core.seeds.child`` returns 64 bits; the noise takes 32 so that a shader's ``uint`` holds it. The
    fold is done once per field, by the model, which publishes the 32-bit result; it is never done per point.
    """
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise NoiseError(f"seed must be an int, got {type(seed).__name__}")
    seed = int(seed)
    if not 0 <= seed < 2**64:
        raise NoiseError(f"seed must lie in [0, 2^64), got {seed}")
    return (seed ^ (seed >> 32)) & MASK32


# --- the hash: 32-bit integer arithmetic only ---------------------------------------------------------------------


def _mix_int(h: int) -> int:
    """`lowbias32` on one Python int (the per-call key; the per-point path is `_mix`)."""
    h ^= h >> MIX_SHIFTS[0]
    h = (h * MIX_MULTIPLIERS[0]) & MASK32
    h ^= h >> MIX_SHIFTS[1]
    h = (h * MIX_MULTIPLIERS[1]) & MASK32
    h ^= h >> MIX_SHIFTS[2]
    return h


def _mix(h: np.ndarray) -> np.ndarray:
    """`lowbias32` on a uint32 array of at least one dimension, in place. Multiplication wraps modulo 2^32."""
    h ^= h >> np.uint32(MIX_SHIFTS[0])
    h *= np.uint32(MIX_MULTIPLIERS[0])
    h ^= h >> np.uint32(MIX_SHIFTS[1])
    h *= np.uint32(MIX_MULTIPLIERS[1])
    h ^= h >> np.uint32(MIX_SHIFTS[2])
    return h


def _key(seed: int, octave: int) -> np.uint32:
    """The first two steps of the chain, which do not depend on the point."""
    return np.uint32(_mix_int(_mix_int(_uint(seed, "seed") ^ SEED_SALT) ^ _uint(octave, "octave")))


def _absorb(h, u: np.ndarray) -> np.ndarray:
    """One step of the chain: a new array, mix32(h xor u)."""
    return _mix(np.bitwise_xor(h, u))


def _as_uint32(i) -> np.ndarray:
    """Integers to uint32 by two's complement: i mod 2^32, so -1 -> 0xFFFFFFFF (GLSL's ``uint(int)``)."""
    i = np.asarray(i)
    if i.dtype == np.uint32:
        return i
    if i.dtype.kind not in "iu":
        raise NoiseError(f"lattice coordinates must be integers, got {i.dtype.name}")
    if i.size and (int(i.min()) < -(2**31) or int(i.max()) > MASK32):
        raise NoiseError("a lattice coordinate must fit 32 bits")
    return i.astype(np.int64).astype(np.uint32)


def lattice_hash(seed: int, octave: int, ix, iy, iz=None) -> np.ndarray:
    """The uint32 of one lattice point: seed, octave and two or three integer coordinates, no float anywhere.

    With ``mix32`` the `lowbias32` finaliser (``MIX_SHIFTS``, ``MIX_MULTIPLIERS``), ``^`` xor and every
    quantity a 32-bit unsigned integer::

        h = mix32(seed ^ SEED_SALT)
        h = mix32(h ^ octave)
        h = mix32(h ^ uint(ix))
        h = mix32(h ^ uint(iy))
        h = mix32(h ^ uint(iz))        # three coordinates only

    ``uint(i)`` is two's complement: i mod 2^32, so -1 is 0xFFFFFFFF and -2^31 is 0x80000000; coordinates lie
    in [-2^31, 2^31). That is what GLSL's ``uint(int)`` constructor does [recall: GLSL ES 3.00 section 5.4.1,
    the conversion between int and uint preserves the bit pattern]. ``mix32`` is a bijection, so for a fixed
    seed, octave and the other coordinates the map from one coordinate to the hash is a bijection too: no two
    cells along a lattice line share a hash. The two-coordinate hash is the three-coordinate chain stopped
    one step early; a 2-D and a 3-D field that must differ take different seeds.

    ``seed`` and ``octave`` are ints in [0, 2^32); the coordinates are integer arrays, broadcast together
    (a uint32 array is taken as already converted).
    """
    key = _key(seed, octave)
    coords = [np.atleast_1d(_as_uint32(c)) for c in ((ix, iy) if iz is None else (ix, iy, iz))]
    coords = np.broadcast_arrays(*coords)
    h = key
    for u in coords:
        h = _absorb(h, u)
    shape = np.broadcast_shapes(*(np.shape(c) for c in ((ix, iy) if iz is None else (ix, iy, iz))))
    return h.reshape(shape)


def lattice_value(h, dtype=np.float64) -> np.ndarray:
    """A hash to a lattice value in [-1, 1): ``(h >> 8) * 2^-23 - 1``.

    The top 24 bits are an integer below 2^24, which float32 holds exactly; scaling by a power of two and
    subtracting 1 are exact too, so float32 and float64 agree to the bit. The values are the 2^24 multiples of
    2^-23 from -1 to 1 - 2^-23, each equally likely for a uniform hash: mean -2^-24 (not 0: the grid has no
    point at +1), variance (1 - 2^-48) / 3 [inferred: the variance of a discrete uniform on N = 2^24 points of
    spacing d is (N^2 - 1) d^2 / 12].
    """
    ft = _float_type(dtype)
    h = np.asarray(h, dtype=np.uint32)
    return (h >> np.uint32(32 - LATTICE_BITS)).astype(ft) * ft(2.0 ** -(LATTICE_BITS - 1)) - ft(1.0)


# --- one octave ----------------------------------------------------------------------------------------------------


def _fade(t: np.ndarray) -> np.ndarray:
    """The quintic 6 t^5 - 15 t^4 + 10 t^3 as ``t*t*t*(t*(t*6 - 15) + 10)``: zero slope and curvature at 0 and 1."""
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _cell(coordinate: np.ndarray):
    """A coordinate to its cell: (uint32 index, fade weight, variance factor 1 - 2 s (1 - s))."""
    if not np.all(np.abs(coordinate) < LATTICE_LIMIT):  # also refuses NaN
        raise NoiseError("a lattice coordinate (position times frequency) must be finite and below 2^31 in size")
    base = np.floor(coordinate)
    s = _fade(coordinate - base)  # the fraction is exact: base and coordinate share a binade or base is smaller
    return base.astype(np.int64).astype(np.uint32), s, 1.0 - 2.0 * s * (1.0 - s)


def _prepare(ft, *coordinates):
    arrays = np.broadcast_arrays(*(np.asarray(c, dtype=ft) for c in coordinates))
    return arrays[0].shape, [np.ascontiguousarray(a).reshape(-1) for a in arrays]


def noise2(seed: int, x, y, octave: int = 0, dtype=np.float64) -> np.ndarray:
    """One octave of 2-D value noise on the unit lattice: mean 0, variance 1 at every point.

    For a point (x, y), with ``i = floor(x)``, ``t = x - i`` and the fade ``s = t*t*t*(t*(t*6 - 15) + 10)`` on
    each axis, and ``v(i, j) = lattice_value(lattice_hash(seed, octave, i, j))``::

        a = v(i, j)     + sx * (v(i+1, j)   - v(i, j))
        b = v(i, j+1)   + sx * (v(i+1, j+1) - v(i, j+1))
        r = a + sy * (b - a)
        n = (1 - 2*sx*(1 - sx)) * (1 - 2*sy*(1 - sy))
        noise = r * (sqrt(3) / sqrt(n))

    in that order, in the working precision. ``i + 1`` wraps modulo 2^32 like every other integer here.

    **Why the division.** ``r`` is a weighted sum of four independent values of variance 1/3, with weights
    (1 - sx, sx) x (1 - sy, sy), so its variance is n / 3 with n the product over the axes of (1 - s)^2 + s^2 =
    1 - 2 s (1 - s): 1/3 at a lattice point, 1/12 at a cell centre. Dividing by sqrt(n / 3) makes the variance
    1 at every point [inferred: independence of the four hashes], to the 2^-48 of :func:`lattice_value`. The
    mean is -2^-24 sqrt(3 / n), between -1.0e-7 and -2.1e-7. n and its first derivative are continuous across
    cell edges (s' = 0 there), so the noise stays continuous with a continuous first derivative; its
    derivative across an edge is zero.

    **Measured** (``tests/test_layer_noise.py``, 2^20 points over 4096^2 cells): mean -7e-5 (standard error
    1e-3), variance 0.9991 (1e-3); the variance at fixed positions in the cell, over 2^18 cells each
    (standard error 0.002): a lattice point 1.0002, the centre 0.9981, an edge midpoint 1.0040, the point
    (0.3, 0.7) 0.9988. The values are bounded: |noise| <= 2 sqrt(3) in 2-D (the cell centre, four equal
    corners). The marginal is not Gaussian: uniform on [-sqrt 3, sqrt 3) at a lattice point, closer to a bell
    at the centre (kurtosis 2.1 over the cell against a Gaussian's 3); an octave sum is closer still.

    **Its spectrum** (measured: 64 cells across, 16 samples per cell, a Hann window, two seeds) is a
    low-pass: flat to a quarter of a cycle per cell (0.96 of its low-wavenumber level there), half the
    variance below 0.35 cycles per cell, 90 % below 0.63, 3.4 % above 1. It is isotropic where the variance
    is (power along the lattice axes over power along the diagonals: 1.01 between 0.1 and 0.5 cycles per
    cell, 0.83 between 0.5 and 1) and not above one cycle per cell, where the axes carry 48 times the
    diagonals' power: value noise's lattice signature, confined to that 3.4 %.

    ``seed`` and ``octave`` are ints in [0, 2^32). ``x`` and ``y`` broadcast; |x|, |y| < 2^31.
    """
    ft = _float_type(dtype)
    key = _key(seed, octave)
    shape, (x, y) = _prepare(ft, x, y)
    ux, sx, nx = _cell(x)
    uy, sy, ny = _cell(y)
    one = np.uint32(1)
    h0, h1 = _absorb(key, ux), _absorb(key, ux + one)
    uy1 = uy + one
    v00, v10 = lattice_value(_absorb(h0, uy), ft), lattice_value(_absorb(h1, uy), ft)
    v01, v11 = lattice_value(_absorb(h0, uy1), ft), lattice_value(_absorb(h1, uy1), ft)
    a = v00 + sx * (v10 - v00)
    b = v01 + sx * (v11 - v01)
    r = a + sy * (b - a)
    return (r * (ft(SQRT3) / np.sqrt(nx * ny))).reshape(shape)[()]


def noise3(seed: int, x, y, z, octave: int = 0, dtype=np.float64) -> np.ndarray:
    """One octave of 3-D value noise on the unit lattice: mean 0, variance 1 at every point.

    As :func:`noise2` with a third axis: the eight corners ``v(i, j, k)`` are interpolated along x, then y,
    then z, and the result is multiplied by ``sqrt(3) / sqrt(nx * ny * nz)``::

        a00 = v(i,j,k)     + sx * (v(i+1,j,k)     - v(i,j,k))
        a10 = v(i,j+1,k)   + sx * (v(i+1,j+1,k)   - v(i,j+1,k))
        a01 = v(i,j,k+1)   + sx * (v(i+1,j,k+1)   - v(i,j,k+1))
        a11 = v(i,j+1,k+1) + sx * (v(i+1,j+1,k+1) - v(i,j+1,k+1))
        b0 = a00 + sy * (a10 - a00);  b1 = a01 + sy * (a11 - a01)
        r = b0 + sz * (b1 - b0)
        noise = r * (sqrt(3) / sqrt((nx * ny) * nz))

    Unnormalised, the variance would run from 1/3 at a lattice point to 1/24 at a cell centre; normalised it is
    1 everywhere, by the same argument. Measured (2^20 points): mean 1.2e-3 (standard error 1e-3), variance
    0.9991 (1e-3); at a lattice point 0.9997, the centre 0.9959, an edge midpoint 0.9984, the point
    (0.3, 0.7, 0.1) 1.0020 (0.002 to 0.003). |noise| <= 2 sqrt(6).

    A plane z = constant of this field is not :func:`noise2`: the hash chain has one more step.
    """
    ft = _float_type(dtype)
    key = _key(seed, octave)
    shape, (x, y, z) = _prepare(ft, x, y, z)
    ux, sx, nx = _cell(x)
    uy, sy, ny = _cell(y)
    uz, sz, nz = _cell(z)
    one = np.uint32(1)
    uy1, uz1 = uy + one, uz + one
    h0, h1 = _absorb(key, ux), _absorb(key, ux + one)
    h00, h10, h01, h11 = _absorb(h0, uy), _absorb(h1, uy), _absorb(h0, uy1), _absorb(h1, uy1)

    def along_x(low, high, uk):
        v_low, v_high = lattice_value(_absorb(low, uk), ft), lattice_value(_absorb(high, uk), ft)
        return v_low + sx * (v_high - v_low)

    a00, a10 = along_x(h00, h10, uz), along_x(h01, h11, uz)
    a01, a11 = along_x(h00, h10, uz1), along_x(h01, h11, uz1)
    b0 = a00 + sy * (a10 - a00)
    b1 = a01 + sy * (a11 - a01)
    r = b0 + sz * (b1 - b0)
    return (r * (ft(SQRT3) / np.sqrt((nx * ny) * nz))).reshape(shape)[()]


# --- octaves to a spectral slope ---------------------------------------------------------------------------------


def octave_weights(slope: float, octaves: int, lacunarity: float = 2.0, ndim: int = 2) -> tuple[float, float, float]:
    """The numbers that shape an octave sum to a spectral slope: ``(gain, top, norm)``.

    **The gain.** Octave j is the unit-lattice noise evaluated at ``f_j x`` with ``f_j = f_0 L^j`` (L the
    lacunarity), times an amplitude ``a_j``. If the unit-lattice noise has power spectrum ``P_1(q)`` per unit
    volume of wavenumber in d dimensions (integrating to its variance, 1), the octave's is
    ``a_j^2 f_j^-d P_1(k / f_j)``: stretching a field by f in d dimensions spreads the same variance over a
    volume of k-space f^d times larger. The sum of independent octaves has::

        P(k) = sum_j  a_j^2 f_j^-d  P_1(k / f_j)

    and ``P(L k) = L^-slope P(k)`` term by term, for any ``P_1``, when ``a_(j+1)^2 L^-d = L^-slope a_j^2``::

        a_j^2 = L^(j (d - slope))            gain = a_(j+1) / a_j = L^((d - slope) / 2)

        2-D:  gain = L^(1 - slope/2)         3-D:  gain = L^((3 - slope) / 2)

    So the same slope needs amplitudes that differ by sqrt(L) per octave between two and three dimensions
    [inferred].

    **The top octave.** The term-by-term relation is exact for an endless sum. Value noise is a low-pass:
    ``P_1`` is flat below about a quarter of a cycle per cell, so every octave lays a flat floor
    ``a_j^2 f_j^-d = f_0^-d L^(-j slope)`` under all the wavenumbers below its own. The octaves above the
    last one, N - 1, are missing, and their floors with them: a geometric series, ``L^-slope / (1 - L^-slope)``
    times the last octave's own floor. The last octave therefore carries them: its amplitude is multiplied by::

        top = 1 / sqrt(1 - L^-slope)

    which restores the endless sum's spectrum at every wavenumber below the last octave's roll-off [inferred;
    it needs slope > 0, which is required]. Without it a shallow slope measures too steep: 1.60 for 1.5,
    against 1.53 with it, over the band and the twelve seeds of :func:`fractal`'s measurement [recall: S55,
    builder A's probe before the factor was added; the suite measures only the corrected sum]. The floor is
    the d-dimensional spectrum's; a plane through a 3-D sum is not fully restored (:func:`fractal`).

    **The normaliser.** Each octave has variance 1 at every point (:func:`noise2`) and the octaves are
    independent (the octave index is hashed), so the sum's variance is, at every point, with
    ``r = L^(d - slope)``::

        sum_(j < N-1) r^j  +  top^2 r^(N-1)

    ``norm`` is one over its square root. The first part is ``(r^(N-1) - 1) / (r - 1)``, or N - 1 when r = 1;
    it is summed term by term here, which the closed form equals and which does not cancel near r = 1.

    A model publishes ``gain``, ``top`` and ``norm``; a shader reads them and computes no power.
    """
    if isinstance(octaves, bool) or not isinstance(octaves, (int, np.integer)) or not 1 <= octaves <= 32:
        raise NoiseError(f"octaves must be an int in [1, 32], got {octaves!r}")
    if ndim not in (2, 3):
        raise NoiseError(f"ndim must be 2 or 3, got {ndim!r}")
    slope, lacunarity = float(slope), float(lacunarity)
    if not (math.isfinite(slope) and slope > 0.0):
        raise NoiseError(f"slope must be positive and finite, got {slope}")
    if not (math.isfinite(lacunarity) and lacunarity > 1.0):
        raise NoiseError(f"lacunarity must exceed 1, got {lacunarity}")
    ratio = lacunarity ** (ndim - slope)
    top_squared = 1.0 / (1.0 - lacunarity**-slope)
    last = int(octaves) - 1
    total = math.fsum([ratio**j for j in range(last)] + [top_squared * ratio**last])
    return math.sqrt(ratio), math.sqrt(top_squared), 1.0 / math.sqrt(total)


def fractal(seed: int, positions, slope: float, octaves: int, *, base_frequency: float, lacunarity: float = 2.0, dtype=np.float64) -> np.ndarray:
    """Octaves of value noise summed to a power spectrum P(k) ~ k^-slope, with unit variance at every point.

    ``positions`` has a last axis of length 2 or 3, which chooses :func:`noise2` or :func:`noise3`.
    ``octaves`` is fixed by the caller (rule A1: the step count is known in advance). In the working
    precision, with ``gain``, ``top`` and ``norm`` from :func:`octave_weights` for that dimension::

        f = base_frequency;  a = 1;  total = 0
        for j in 0 .. octaves - 1:
            if j == octaves - 1:  a = a * top
            total = total + a * noise(seed, positions * f, octave = j)
            f = f * lacunarity;  a = a * gain
        return total * norm

    ``base_frequency`` is lattice cells per unit length of the coarsest octave: its inverse is the outer
    scale. **The band** the slope holds over runs from ``base_frequency`` to a quarter of the finest octave's
    frequency: below it the spectrum is flat (white: cells of the coarsest lattice are independent), above it
    the finest octave rolls off and the spectrum falls steeply. A caller who needs the slope up to a
    wavenumber k gives octaves up to 4 k.

    **Measured slopes** (``tests/test_layer_noise.py``, ``measure_slopes``: 2-D, 512^2 samples of a unit
    square, 7 octaves from 4 to 256 cells across, a Hann window, the power averaged in 12 logarithmic bins of
    wavenumber over the band 4 to 64, a straight line fitted to log power against log wavenumber). Asked
    1.5, 2.5, 3.5: four seeds stacked (what the suite runs) measure 1.495, 2.497, 3.544; twelve measure
    1.527, 2.520, 3.544. One seed alone scatters by 0.08 to 0.10 rms (the lowest bins hold a few dozen modes).

    **The ripple.** The power is not a smooth power law. It ripples about the fitted line with the period of
    the lacunarity, because each octave is a plateau and a roll-off and a steep sum is a staircase of them:
    0.03, 0.04 and 0.06 dex rms at those slopes (twelve seeds; four measure 0.04, 0.05, 0.08, sampling noise
    included). A lacunarity of sqrt 2 with 13 octaves over the same band measures 0.03 at slope 3.5 (four
    seeds): the caller's choice, at twice the cost. Gradient noise would ripple less: a prototype on this
    hash measured about 0.6 of the value noise's ripple at lacunarity 2, and no steepening at the top of the
    band [recall: S55, builder A's probe, not kept]. That is the price of the choice in the module docstring.

    **A plane through a 3-D sum** has a 2-D spectrum one power shallower, ``slope - 1`` [inferred: the
    octave's 2-D spectrum in the plane is its 3-D one integrated along the third wavenumber, which leaves
    ``a_j^2 f_j^-2`` times a function of k / f_j, and a_j^2 f_j^-2 is f_j^-(slope - 1) up to a constant].
    Measured the same way, eight seeds: asked 2.5 and 3.5 in 3-D, expected 1.5 and 2.5 in the plane, measured
    1.57 and 2.53 (three seeds, the suite's: 1.62 and 2.57; one seed scatters by 0.08). The plane is steeper
    than slope - 1 by 0.03 to 0.07, more at shallow slopes: the plane's spectrum at one wavenumber gathers
    every k_z, those above the finest octave included, and ``top`` restores the missing octaves' floor in the
    3-D spectrum only, where it falls as L^-slope per octave; in the plane it falls as L^-(slope - 1)
    [inferred]. A caller who needs the plane's slope to the top of the band gives two octaves beyond it.

    **Variance**, over 2^17 points spread across 1000 outer scales: between 0.998 and 1.004 for slopes 1 to 4
    and 1, 3 and 6 octaves in 2-D and slopes 2 and 4, 1 and 4 octaves in 3-D (standard error 0.003 to 0.004;
    it is 1 in expectation at every point). One picture that spans only a few outer scales does not show it:
    a steep sum's variance is mostly in its coarsest octave, and 4 x 4 of that octave's cells are 16 samples.
    """
    ft = _float_type(dtype)
    p = np.asarray(positions, dtype=ft)
    if p.ndim < 1 or p.shape[-1] not in (2, 3):
        raise NoiseError(f"positions must have a last axis of length 2 or 3, got shape {p.shape}")
    base_frequency = float(base_frequency)
    if not (math.isfinite(base_frequency) and base_frequency > 0.0):
        raise NoiseError(f"base_frequency must be positive, got {base_frequency}")
    ndim = p.shape[-1]
    gain, top, norm = octave_weights(slope, octaves, lacunarity, ndim)
    one_octave = noise2 if ndim == 2 else noise3
    f, a, step, gain = ft(base_frequency), ft(1.0), ft(lacunarity), ft(gain)
    total = np.zeros(p.shape[:-1], dtype=ft)
    for j in range(int(octaves)):
        if j == int(octaves) - 1:
            a = ft(a * ft(top))
        total = total + a * one_octave(seed, *(p[..., axis] * f for axis in range(ndim)), octave=j, dtype=ft)
        f, a = ft(f * step), ft(a * gain)
    return (total * ft(norm))[()]


# --- shear --------------------------------------------------------------------------------------------------------


def shear(positions, strain: float, dtype=np.float64) -> np.ndarray:
    """Positions mapped by the plane shear ``x' = x - strain * y``, ``y' = y`` (a third coordinate is kept).

    A sheared field is the unsheared field evaluated at sheared coordinates:
    ``fractal(seed, shear(positions, s), ...)``. The map has unit determinant, so it moves no area and changes
    no mean or variance.

    Pure geometry: which axis is which is the caller's. *Example* [inferred]: take x along the direction of
    rotation and y radially outward at a point of a disc whose angular speed falls outward. Material further
    out lags, so a pattern that was isotropic a time t ago is now the isotropic pattern read at
    ``x + |dOmega/dlnR| t y``: ``strain = (dOmega/dlnR) t``, negative, and the crests trail.
    """
    ft = _float_type(dtype)
    p = np.array(positions, dtype=ft)
    if p.ndim < 1 or p.shape[-1] not in (2, 3):
        raise NoiseError(f"positions must have a last axis of length 2 or 3, got shape {p.shape}")
    p[..., 0] = p[..., 0] - ft(strain) * p[..., 1]
    return p


def shear_anisotropy(strain: float) -> tuple[float, float]:
    """What a shear does to an isotropic 2-D power spectrum: ``(axis_ratio, tilt)`` of its anisotropy ellipse.

    Write the shear as r' = S r with S = [[1, -s], [0, 1]]. The sheared field g'(r) = g(S r) has the spectrum
    ``P'(k) = P(S^-T k)`` (det S = 1), that is ``P'(kx, ky) = P(kx, ky + s kx)``. The spectrum's second-moment
    tensor, M_ab = integral of P k_a k_b (equally the covariance of the field's gradient), is m times the
    identity for an isotropic field and becomes::

        M' = m S^T S = m [[1, -s], [-s, 1 + s^2]]

    whose eigenvalues are ``1 + s^2/2 +- |s| sqrt(1 + s^2/4)``, with product 1. The anisotropy ellipse is the
    ellipse of M': its semi-axes are the rms wavenumbers along its principal directions, so::

        axis_ratio = sqrt(l+ / l-) = l+ = 1 + s^2/2 + |s| sqrt(1 + s^2/4)
        tilt       = atan2(-2 s, -s^2) / 2          (the major axis, from the kx axis; an axis: modulo pi)

    The tilt is -45 degrees for a vanishing positive strain and turns to -90 degrees as it grows; structures
    in real space are elongated at right angles to it, at ``atan2(2 s, s^2) / 2`` from the x axis (45 degrees
    turning to 0: along x). For ``strain == 0`` the ratio is 1 and the tilt is returned as nan (no axis)
    [inferred].
    """
    s = float(strain)
    if s == 0.0:
        return 1.0, math.nan
    return 1.0 + 0.5 * s * s + abs(s) * math.sqrt(1.0 + 0.25 * s * s), 0.5 * math.atan2(-2.0 * s, -s * s)


# --- the unit-mean log-normal map, normalised per cell ------------------------------------------------------------


def cell_quadrature(u0: float, u1: float, v0: float, v1: float, n: int = DEFAULT_QUADRATURE) -> np.ndarray:
    """The n x n midpoint lattice of the rectangle [u0, u1] x [v0, v1]: an (n*n, 2) float64 array.

    Point ``j * n + i`` is ``(u0 + (i + 1/2)(u1 - u0)/n, v0 + (j + 1/2)(v1 - v0)/n)``. The two coordinates are
    the caller's (x and y, or R and phi); the caller maps them to the positions the noise is evaluated at, and
    weights the points if the cell's measure is not uniform in them (see :func:`lognormal_normaliser`).

    **Choosing n**: at least four points per cell of the finest octave's lattice along each axis,
    ``n >= 4 * extent * finest_frequency``. The default 16 serves a cell that holds up to 4 finest lattice
    cells across; what that buys, and what half of it costs, is measured in :func:`lognormal_map`. n is fixed
    per field by the model and published with it: the normaliser is defined on these points and no others.
    """
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 1:
        raise NoiseError(f"n must be a positive int, got {n!r}")
    mid = (np.arange(int(n), dtype=np.float64) + 0.5) / int(n)
    u = float(u0) + mid * (float(u1) - float(u0))
    v = float(v0) + mid * (float(v1) - float(v0))
    return np.stack([np.tile(u, int(n)), np.repeat(v, int(n))], axis=-1)


def lognormal_normaliser(g_quadrature, sigma: float, weights=None) -> np.ndarray:
    """The per-cell normaliser of the log-normal map: one over the quadrature mean of ``exp(sigma g - sigma^2/2)``.

    ``g_quadrature`` holds a unit-variance field at a cell's quadrature points along its last axis (any
    leading axes are cells: one normaliser each). ``weights`` (same last axis, non-negative, default equal)
    are the points' shares of the cell's measure, for a cell whose conserved total is not uniform in the two
    coordinates; they are normalised to sum to 1.

    ``exp(sigma g - sigma^2/2)`` has mean 1 only in expectation, and only for a Gaussian g: over many cells
    of a three-octave sum it measures 0.999, 0.987 and 0.941 at sigma 0.5, 1 and 1.5 (the sum's tails are
    lighter than a Gaussian's). The layer's second rule needs the mean to be 1 in every cell, so that the map
    redistributes inside the cell and changes no total. With this normaliser the weighted mean of
    :func:`lognormal_map` over the same quadrature points is 1 to rounding, by construction. It is a number
    the model publishes per cell; a shader reads it from a table and never recomputes it. It is not near 1
    when the cell is no larger than the field's outer scale (one coarse lattice cell is then one sample):
    over 256 such cells at sigma 1 it ran from 0.29 to 5.1. Always float64: it is the model's.
    """
    g = np.asarray(g_quadrature, dtype=np.float64)
    sigma = float(sigma)
    e = np.exp(sigma * g - 0.5 * sigma * sigma)
    if weights is None:
        mean = e.mean(axis=-1)
    else:
        w = np.broadcast_to(np.asarray(weights, dtype=np.float64), g.shape)
        if np.any(w < 0.0) or not np.all(w.sum(axis=-1) > 0.0):
            raise NoiseError("weights must be non-negative with a positive sum in every cell")
        mean = (w * e).sum(axis=-1) / w.sum(axis=-1)
    return 1.0 / mean


def lognormal_map(g, sigma: float, normaliser=1.0, dtype=np.float64) -> np.ndarray:
    """The normalised log-normal map at any points of a cell: ``normaliser * exp(sigma * g - sigma^2 / 2)``.

    Positive everywhere. Its mean over the cell's quadrature points is 1 to rounding (measured: 7e-16; the
    contract is 1e-12) when ``normaliser`` is that cell's (:func:`lognormal_normaliser`).

    **At other points the mean is only close to 1.** Measured for the default n = 16 on 256 unit cells of a
    2-D sum with slope 2.5, base frequency 1 and three octaves (4 finest lattice cells across a cell: the
    limit of the rule in :func:`cell_quadrature`), as the mean over a 64 x 64 midpoint lattice of each cell
    (``tests/test_layer_noise.py``)::

        sigma 0.5   |mean - 1|  rms 3.2e-4   worst 9.5e-4
        sigma 1.0               rms 8.4e-4   worst 3.6e-3
        sigma 1.5               rms 1.6e-3   worst 8.0e-3

    At sigma 1, n = 32 (eight points per finest lattice cell) brings the worst case to 4.2e-5, and n = 8 (two)
    takes it to 0.059. A fourth octave under n = 16 (two points per finest cell again) measures 0.021; under
    n = 32, 1.1e-3. So a total summed over the quadrature points is conserved exactly, and one summed any
    other way is conserved to these numbers.

    In float32 the exponential's relative error is that of ``sigma * g``: the map is compared relatively.
    """
    ft = _float_type(dtype)
    g = np.asarray(g, dtype=ft)
    sigma = ft(sigma)
    return (np.asarray(normaliser, dtype=ft) * np.exp(sigma * g - ft(0.5) * sigma * sigma))[()]


# --- the committed test vectors -----------------------------------------------------------------------------------


def _counter(tag: int):
    """A stream of 32-bit integers for choosing the vectors' inputs: the mixer on a counter. No numpy stream."""
    state = [(_mix_int(tag ^ SEED_SALT) + 1) & MASK32]

    def draw() -> int:
        state[0] = (state[0] + 0x6D2B79F5) & MASK32
        return _mix_int(state[0])

    return draw


def _dyadic(draw, span: int) -> float:
    """A multiple of 1/1024 in [-span, span): exact in float32 while span <= 8192."""
    return (draw() % (2048 * span) - 1024 * span) / 1024.0


def _f32(value) -> float:
    return float(np.float32(value))


def build_vectors() -> dict:
    """The test vectors as a document. Not run at import; ``write_vectors`` commits it, the test recomputes it.

    Every position is a multiple of 1/1024 and every frequency and strain a power of two or a small dyadic
    number, so a float32 program is given exactly these inputs. ``value`` is the float64 reference and
    ``value_f32`` what the float32 path returns. Sections marked ``exact`` contain only integer arithmetic and
    correctly rounded float operations (+, -, *, /, sqrt, floor) and are compared to the bit; the others pass
    through ``pow`` or ``exp``, which a C library need not round correctly, and are compared to 1e-12.
    """
    seeds = (0, 1, SEED_SALT, MASK32, 20261004, 0x00C0FFEE)

    draw = _counter(1)
    edge = (0, 1, -1, 2, -2, 255, -256, 2**31 - 1, -(2**31), 65536, -65537)
    rows = []
    for n in range(160):
        seed = seeds[n % len(seeds)] if n < 96 else draw()
        octave = (0, 1, 2, 5, 31, 7)[(n // 6) % 6] if n < 96 else draw() % 32
        ix = edge[n % len(edge)] if n < 66 else draw() - 2**31
        iy = edge[(n // len(edge)) % len(edge)] if n < 66 else draw() - 2**31
        iz = None if n % 2 == 0 else (edge[(n // 3) % len(edge)] if n < 66 else draw() - 2**31)
        rows.append([seed, octave, ix, iy, iz, int(lattice_hash(seed, octave, ix, iy, iz))])
    hash_section = {"columns": ["seed", "octave", "ix", "iy", "iz", "hash"], "compare": "exact", "rows": rows}

    def positions(tag: int, count: int, dims: int) -> list[list[float]]:
        draw = _counter(tag)
        fixed = [0.0, 1.0, -1.0, 0.5, -0.5, 2.5, -3.5, 7.0, -8.0, 0.25, 1023.0 / 1024.0, -1.0 / 1024.0]
        out = [[fixed[(n + axis * (1 + n // len(fixed))) % len(fixed)] for axis in range(dims)] for n in range(2 * len(fixed))]
        out += [[float(draw() % 64 - 32) for _ in range(dims)] for _ in range(8)]  # lattice points
        out += [[float(draw() % 64 - 32) + 0.5 for _ in range(dims)] for _ in range(8)]  # cell centres
        out += [[_dyadic(draw, 8192) for _ in range(dims)] for _ in range(24)]  # large: up to 8192
        out += [[_dyadic(draw, 8) for _ in range(dims)] for _ in range(count - len(out))]
        return out

    rows = []
    for n, (x, y) in enumerate(positions(2, 120, 2)):
        seed, octave = seeds[n % len(seeds)], (0, 1, 3, 7)[(n // 5) % 4]
        rows.append([seed, octave, x, y, float(noise2(seed, x, y, octave)), _f32(noise2(seed, x, y, octave, np.float32))])
    noise2_section = {"columns": ["seed", "octave", "x", "y", "value", "value_f32"], "compare": "exact", "rows": rows}

    rows = []
    for n, (x, y, z) in enumerate(positions(3, 120, 3)):
        seed, octave = seeds[n % len(seeds)], (0, 1, 3, 7)[(n // 5) % 4]
        rows.append([seed, octave, x, y, z, float(noise3(seed, x, y, z, octave)), _f32(noise3(seed, x, y, z, octave, np.float32))])
    noise3_section = {"columns": ["seed", "octave", "x", "y", "z", "value", "value_f32"], "compare": "exact", "rows": rows}

    fractal_cases = []
    draw = _counter(4)
    for ndim, octaves, base_frequency, count in ((2, 6, 0.25, 40), (3, 4, 0.5, 20)):
        for slope in (1.5, 3.0) if ndim == 2 else (2.5, 3.5):
            seed = seeds[len(fractal_cases) + 1]
            gain, top, norm = octave_weights(slope, octaves, 2.0, ndim)
            pts = [[_dyadic(draw, 64) for _ in range(ndim)] for _ in range(count)]
            kwargs = dict(base_frequency=base_frequency, lacunarity=2.0)
            rows = [[*p, float(fractal(seed, p, slope, octaves, **kwargs)), _f32(fractal(seed, p, slope, octaves, dtype=np.float32, **kwargs))] for p in pts]
            columns = ["x", "y", "value", "value_f32"] if ndim == 2 else ["x", "y", "z", "value", "value_f32"]
            fractal_cases.append({"seed": seed, "ndim": ndim, "slope": slope, "octaves": octaves, "lacunarity": 2.0, "base_frequency": base_frequency, "gain": gain, "top": top, "norm": norm, "columns": columns, "rows": rows})
    fractal_section = {"compare": "1e-12", "cases": fractal_cases}

    rows = []
    draw = _counter(5)
    for n in range(48):
        seed, octave, strain = seeds[n % len(seeds)], n % 3, (0.5, -1.25, 2.0, -0.125)[n % 4]
        x, y = _dyadic(draw, 16), _dyadic(draw, 16)
        value = [float(noise2(seed, *shear([x, y], strain, ft), octave, ft)) for ft in _FLOAT_TYPES]
        rows.append([seed, octave, strain, x, y, value[0], _f32(value[1])])
    shear_section = {"columns": ["seed", "octave", "strain", "x", "y", "value", "value_f32"], "compare": "exact", "about": "noise2 at (x - strain * y, y)", "rows": rows}

    lognormal_cases = []
    draw = _counter(6)
    field = dict(slope=2.5, octaves=3, base_frequency=1.0, lacunarity=2.0)
    for n, sigma in enumerate((0.5, 1.0, 1.5, 1.0, 0.5, 1.5, 1.0, 1.0)):
        seed, n_quad = seeds[n % len(seeds)], 4
        u0, v0 = float(draw() % 32 - 16), float(draw() % 32 - 16)
        quadrature = cell_quadrature(u0, u0 + 1.0, v0, v0 + 1.0, n_quad)
        normaliser = float(lognormal_normaliser(fractal(seed, quadrature, **field), sigma))
        pts = [[u0 + (draw() % 1024) / 1024.0, v0 + (draw() % 1024) / 1024.0] for _ in range(8)]
        rows = []
        for p in pts:
            value = [float(lognormal_map(fractal(seed, p, dtype=ft, **field), sigma, normaliser, ft)) for ft in _FLOAT_TYPES]
            rows.append([*p, value[0], _f32(value[1])])
        gain, top, norm = octave_weights(field["slope"], field["octaves"], field["lacunarity"], 2)
        lognormal_cases.append({"seed": seed, **field, "gain": gain, "top": top, "norm": norm, "sigma": sigma, "cell": [u0, u0 + 1.0, v0, v0 + 1.0], "n": n_quad, "normaliser": normaliser, "columns": ["x", "y", "value", "value_f32"], "rows": rows})
    lognormal_section = {"compare": "1e-12", "about": "normaliser * exp(sigma * fractal - sigma^2 / 2); the normaliser is the cell's, over its n x n midpoint lattice; value_f32 is compared relatively", "cases": lognormal_cases}

    return {
        "version": VECTORS_VERSION,
        "about": "galaxy.layer.noise: committed test vectors. Regenerating is a decision's act: uv run python -m galaxy.layer.noise write-vectors",
        "hash": {"mixer": "lowbias32", "shifts": list(MIX_SHIFTS), "multipliers": list(MIX_MULTIPLIERS), "seed_salt": SEED_SALT, "lattice_bits": LATTICE_BITS},
        "float32_tolerance": FLOAT32_TOLERANCE,
        "lattice_hash": hash_section,
        "noise2": noise2_section,
        "noise3": noise3_section,
        "fractal": fractal_section,
        "shear": shear_section,
        "lognormal": lognormal_section,
    }


def render_vectors(document: dict) -> str:
    """The document as text: one row per line, floats in Python's shortest round-trip form, LF line ends."""

    def render(node, depth: int) -> str:
        pad = " " * (depth + 1)
        if isinstance(node, dict):
            items = [f"{pad}{json.dumps(key)}: {render(value, depth + 1)}" for key, value in node.items()]
            return "{\n" + ",\n".join(items) + "\n" + " " * depth + "}"
        if isinstance(node, list) and node and isinstance(node[0], (list, dict)):
            return "[\n" + ",\n".join(pad + render(item, depth + 1) for item in node) + "\n" + " " * depth + "]"
        return json.dumps(node)

    return render(document, 0) + "\n"


def write_vectors(path: Path = VECTORS) -> Path:
    """Write the vectors file. A deliberate act: the decision that changes the noise records the regeneration."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_vectors(build_vectors()))
    return path


if __name__ == "__main__":
    if sys.argv[1:] != ["write-vectors"]:
        raise SystemExit("usage: python -m galaxy.layer.noise write-vectors")
    print(write_vectors())
