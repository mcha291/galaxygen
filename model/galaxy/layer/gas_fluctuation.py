"""gas_fluctuation: the turbulent structure of the diffuse ISM between the clouds (S62, D221 part I; BUILD_III Phase L2).

**State of this module (S62, builder A, first hand-back).** The arithmetic below is built and tested: the octave sum
continuing L1's noise (item 1), the per-ring amplitude ladder with its unit-variance normaliser (item 2), the break's
octave index from the gas's published height, and the shear's strain from the published rotation curve (item 4).
**No stage is registered yet**: the log-normal width (item 3) needs the Mach number of the phase the field stands
for, and the model publishes no sound speed for the diffuse gas (the hand-back to the lead says what it publishes);
the per-cell normaliser (item 5), the published parameters, the evaluator and the vectors (item 6) wait on that
ruling.

**One noise** (D220 part II item 6; D221 item 1). L1's ``census_clustering`` field is ``noise.fractal(seed, (x, y)
in kpc, 1.53, 3, base_frequency = 1 / 0.19 kpc)`` on the seed ``fold(child(texture_seed, "census_clustering"))``:
octave j is ``noise2(seed, x f_j, y f_j, octave=j)`` with ``f_j = 2^j / 0.19 kpc``. This field's octave j is the
**same call with the same arguments**, for j = 0 .. 5 - lattice scales 190, 95, 47.5, 23.75, 11.875 and 5.9375 pc,
the finest the field's resolution - so its three coarse octaves are L1's values at every point, bit for bit
(:func:`octave_terms`; tested by rebuilding L1's sum from them). Only the amplitudes differ: L1's three octaves carry
L1's weights (the top factor on its third octave, its normaliser for three); this sum carries the ladder's.

**The ladder** (D221 item 2). In two dimensions an octave sum has the local spectrum P(k) ~ k^-s between octaves j-1
and j when ``a_j / a_(j-1) = L^((2 - s) / 2)`` (``noise.octave_weights`` derives it; L = 2). Here the step into
octave j uses the slope ``s_j = s`` (L1's 1.53) if octave j's lattice scale is at least pi h(R), and ``s + 1`` (the
slope change of one: Elmegreen, Kim & Staveley-Smith 2001; Elmegreen & Scalo 2004 section 2.1) if it is below - h the
ring's published gas scale height, pi Dutta et al. 2009's factor. With ``b`` the number of octaves whose scale is not
below pi h (the **break octave index**: 0 when pi h exceeds 190 pc, 6 when pi h is at most 5.9375 pc)::

    a_0 = 1,   a_j = a_(j-1) * L^((2 - s_j) / 2),   s_j = s for j < b,  s + 1 for j >= b
    a_(N-1) *= top = 1 / sqrt(1 - L^(-s_last)),      s_last = s if b >= N else s + 1

``top`` is ``octave_weights``' factor for the octaves beyond the finest, at the slope the finest octave continues.
**The normaliser** follows from the octaves' independence and unit variance at every point (``noise.noise2``): the
sum's variance is ``sum_j a_j^2`` at every point, so ``norm = 1 / sqrt(sum_j a_j^2)``, summed with ``math.fsum``. With
``b = N`` the ladder is ``octave_weights(s, N)`` and with ``b = 0`` it is ``octave_weights(s + 1, N)``, to rounding
(tested), and the variance is measured directly (tested).

**The strain** (D221 item 4). An isotropic field t old, read at ``noise.shear(positions, strain)`` with x along the
rotation and y outward: ``strain = (dOmega / dlnR) t``, ``t = min(1 / A, cap)``, A the Oort constant ``-R dOmega/dR
/ 2 = (v / R - dv/dR) / 2`` from the published rotation curve (``circular_velocity``, checkpoint 1's - the curve the
epicyclic frequency and the gas pattern read; the model publishes no Oort constant, so it is derived here). Since
``dOmega / dlnR = -2 A``, the strain is ``-2 A t``: exactly -2 wherever ``t = 1 / A`` (asserted by
:func:`shear_strain`), ``-2 A cap`` where the cap binds.
"""

from __future__ import annotations

import math

import numpy as np

from galaxy.layer import census_clustering as _l1
from galaxy.layer import noise as _noise

LACUNARITY = _l1.LACUNARITY  # one noise: L1's octaves halve, and so do these
SEED_PATH = _l1.SEED_PATH  # and on L1's path (D220 part II item 6)
KM_S_PER_KPC_IN_PER_MYR = 1.0 / 977.792221  # 1 km/s/kpc in 1/Myr [inferred: 1 kpc / (1 km/s) = 977.79 Myr]


def field_seed(texture_seed: int) -> int:
    """The noise's 32-bit seed: L1's, the same fold of the same child (D221 item 1)."""
    return _l1.field_seed(texture_seed)


def octave_scales_pc(scale_kpc: float, octaves: int) -> np.ndarray:
    """The octaves' lattice scales in pc: ``1000 scale / 2^j``."""
    return 1000.0 * float(scale_kpc) / LACUNARITY ** np.arange(int(octaves))


def break_octave(height_pc: float, scale_kpc: float, octaves: int, factor: float = math.pi) -> int:
    """The number of octaves whose lattice scale is not below ``factor * height_pc``: the break's octave index."""
    height_pc = float(height_pc)
    if not (math.isfinite(height_pc) and height_pc > 0.0):
        raise ValueError(f"the break needs a published, positive gas height; got {height_pc!r}")
    return int(np.sum(octave_scales_pc(scale_kpc, octaves) >= float(factor) * height_pc))


def ladder_weights(slope: float, change: float, octaves: int, break_index: int,
                   lacunarity: float = LACUNARITY) -> tuple[tuple[float, ...], float]:
    """``(amplitudes, norm)`` of the ladder: each octave's amplitude (the top factor folded into the last) and the
    unit-variance normaliser. The module docstring derives both."""
    octaves, break_index = int(octaves), int(break_index)
    if not 1 <= octaves <= 32 or not 0 <= break_index <= octaves:
        raise ValueError(f"octaves in 1..32 and a break index in 0..octaves; got {octaves}, {break_index}")
    slope, change, lacunarity = float(slope), float(change), float(lacunarity)
    if not (slope > 0.0 and change >= 0.0 and lacunarity > 1.0):
        raise ValueError(f"a positive slope, a non-negative change and a lacunarity above 1; got {slope}, {change}, {lacunarity}")
    amplitudes = [1.0]
    for j in range(1, octaves):
        s_j = slope if j < break_index else slope + change
        amplitudes.append(amplitudes[-1] * math.sqrt(lacunarity ** (2.0 - s_j)))
    s_last = slope if break_index >= octaves else slope + change
    amplitudes[-1] *= 1.0 / math.sqrt(1.0 - lacunarity**-s_last)
    norm = 1.0 / math.sqrt(math.fsum(a * a for a in amplitudes))
    return tuple(amplitudes), norm


def octave_terms(seed: int, positions, scale_kpc: float, octaves: int, dtype=np.float64) -> list[np.ndarray]:
    """The unit-variance octaves at ``positions`` (kpc, last axis 2): octave j is ``noise2`` at ``positions * f_j``,
    ``f_j`` stepped by repeated multiplication from ``1 / scale`` exactly as ``noise.fractal_coarsest`` steps it, so the
    coarse octaves are L1's values to the bit."""
    ft = np.dtype(dtype).type
    p = np.asarray(positions, dtype=ft)
    f, step = ft(1.0 / float(scale_kpc)), ft(LACUNARITY)
    terms = []
    for j in range(int(octaves)):
        terms.append(_noise.noise2(seed, p[..., 0] * f, p[..., 1] * f, octave=j, dtype=ft))
        f = ft(f * step)
    return terms


def gaussian_sum(seed: int, positions, scale_kpc: float, amplitudes, norm: float, strain: float = 0.0,
                 dtype=np.float64) -> np.ndarray:
    """The ladder's unit-variance Gaussian sum at ``positions`` (kpc), read at ``noise.shear(positions, strain)``:
    ``norm * sum_j a_j octave_j``, summed coarse to fine."""
    ft = np.dtype(dtype).type
    p = np.asarray(positions, dtype=ft)
    if strain != 0.0:
        p = _noise.shear(p, strain, ft)
    total = np.zeros(p.shape[:-1], dtype=ft)
    for a, term in zip(amplitudes, octave_terms(seed, p, scale_kpc, len(amplitudes), ft)):
        total = total + ft(a) * term
    return (total * ft(norm))[()]


def oort_a(R_kpc, v_kms) -> np.ndarray:
    """Oort's A in km/s/kpc from a rotation curve on its grid: ``(v / R - dv/dR) / 2`` (= ``-R dOmega/dR / 2``)."""
    R, v = np.asarray(R_kpc, dtype=float), np.asarray(v_kms, dtype=float)
    return 0.5 * (v / R - np.gradient(v, R))


def shear_strain(oort_a_kms_kpc, cap_myr: float) -> tuple[np.ndarray, np.ndarray]:
    """``(strain, t in Myr)``: ``t = min(1 / A, cap)`` and ``strain = (dOmega / dlnR) t = -2 A t``; where ``t = 1/A``
    the strain is -2 exactly (asserted to rounding)."""
    a = np.asarray(oort_a_kms_kpc, dtype=float) * KM_S_PER_KPC_IN_PER_MYR  # 1/Myr
    if np.any(~(a > 0.0)):
        raise ValueError("the shear time needs a positive Oort A on every ring")
    shear_time = 1.0 / a
    t = np.minimum(shear_time, float(cap_myr))
    strain = -2.0 * a * t
    uncapped = shear_time <= float(cap_myr)
    assert np.allclose(strain[uncapped], -2.0, rtol=0.0, atol=1e-12), "dOmega/dlnR = -2A: the strain is -2 at t = 1/A"
    return strain, t
