"""gas_fluctuation: the turbulent structure of the diffuse ISM between the clouds (S62, D221 part I as the lead amended
it; BUILD_III Phase L2).

A layer stage on ``texture_seed``: a log-normal map of a six-octave sum of lattice noise in the plane, steepening by
one power below the gas layer's thickness, read sheared by the disc's rotation, with unit mean in every level-0 cell.
It multiplies nothing yet: the render's and the viewer's diffuse dust and gas read it in V7 (S65). With the layer off
it realises nothing - its published numbers are NaN, the rows kept - and its map is 1.

**One noise** (D220 part II item 6; D221 item 1). L1's ``census_clustering`` field is ``noise.fractal(seed, (x, y)
in kpc, 1.53, 3, base_frequency = 1 / 0.19 kpc)`` on the seed ``fold(child(texture_seed, "census_clustering"))``:
octave j is ``noise2(seed, x f_j, y f_j, octave=j)`` with ``f_j = 2^j / 0.19 kpc``. This field's octave j is the
**same call with the same arguments**, for j = 0 .. 5 - lattice scales 190, 95, 47.5, 23.75, 11.875 and 5.9375 pc,
the finest the field's resolution - so its three coarse octaves are L1's values at every point, bit for bit
(:func:`octave_terms`; tested by rebuilding L1's sum from them). Only the amplitudes differ: L1's three octaves carry
L1's weights (the top factor on its third octave, its normaliser for three); this sum carries the ladder's. **The two
maps share the coarse octaves' values before the shear**: the clouds' map is L1's own evaluation, unsheared; this one
reads the same noise at sheared positions, so the two differ at the coarse scales by the shear alone.

**The ladder** (D221 item 2, the mapping as the lead amended it). In two dimensions an octave sum has the local
spectrum P(k) ~ k^-s between octaves j-1 and j when ``a_j / a_(j-1) = L^((2 - s) / 2)`` (``noise.octave_weights``
derives it; L = 2). The step into octave j uses ``s_j = s`` (L1's 1.53) if the wavelength octave j carries is not
below the break, and ``s + 1`` if it is - the slope change of one (Elmegreen, Kim & Staveley-Smith 2001; Elmegreen &
Scalo 2004 section 2.1) at the wavelength ``pi h(R)`` (Dutta et al. 2009), h the ring's published gas scale height.
**Which wavelength an octave carries**: value noise is flat up to about a quarter cycle per lattice cell
(``noise.noise2``: 0.96 of its low-wavenumber level there, half its variance below 0.35 cycles per cell), so octave j
lays the spectrum's level near ``4 l_j`` (:data:`OCTAVE_WAVELENGTH`) and takes the steep gain when ``4 l_j < pi h``.
With ``b`` the number of octaves for which ``4 l_j >= pi h`` (the **break octave index**: 0 when pi h exceeds 760 pc,
6 when it is at most 23.75 pc)::

    a_0 = 1,   a_j = a_(j-1) * L^((2 - s_j) / 2),   s_j = s for j < b,  s + 1 for j >= b
    a_(N-1) *= top = 1 / sqrt(1 - L^(-s_last)),      s_last = s if b >= N else s + 1

``top`` is ``octave_weights``' factor for the octaves beyond the finest, at the slope the finest octave continues.
*Measured, the two mappings* (S62, the default galaxy's heights, 4 kpc patches at 2.9 pc, two seeds, a continuous
broken law fitted by ``specs/spectrum.py``): the literal one (``l_j < pi h``, as D221 item 2 was first written) put
the fitted break at 355, 379, 407, 515 and 443 pc at R = 1, 3, 5, 8.2 and 12 kpc against pi h 81, 121, 180, 355 and
990 pc, the slope above it -0.82 to +0.60 (the coarsest octave's roll-off, not s): beyond 5.3 kpc no octave at s
carried a wavelength above pi h. This one (``4 l_j < pi h``) fits -1.72 / -2.60 with the break at 57 pc (R 1),
-1.43 / -2.45 at 157 (R 3), -1.50 / -2.40 at 179 (R 5) and -1.62 / -2.50 at 266 (R 8.2): within an octave of pi h.
Beyond ring 11 (pi h above 760 pc) the whole band lies below pi h and the field is the steep slope alone (R 12: -2.51),
declared. *The steep slope is scalloped by octave* (S62's review, finding 8): the local slope per octave band below
the break reads -2.8 to -3.05 mid-band and about -2.17 in the transition octave, and the single fits (-2.46 / -2.51 /
-2.51 on rings 8, 11, 13) average them - value noise's octave structure, inside the gate's definition, which a shader
matching the vectors inherits. **Past the gas disc's last published height** (h is NaN past the stellar edge: rings 25-31 on the default
galaxy) a ring keeps the last finite ring's ladder - "the field beyond the gas disc's last published height keeps that
height's ladder" (the lead's ruling 3); nothing is placed there.

**The sum's normaliser** follows from the octaves' independence and unit variance at every point (``noise.noise2``):
its variance is ``sum_j a_j^2`` everywhere, so ``norm = 1 / sqrt(sum_j a_j^2)`` (``math.fsum``). With ``b = N`` the
ladder is ``octave_weights(s, N)`` and with ``b = 0`` ``octave_weights(s + 1, N)``, to rounding (tested), and the
variance is measured directly (tested).

**The width** (D221 item 3 as ruled): ``sigma^2 = A ln(1 + b^2 M^2)``, A = 0.11, b = 1/3 (Burkhart & Lazarian 2012),
at ``M = sigma_g / c_s``: sigma_g the model's one turbulent dispersion of the cold gas (6 km/s, the one the
star-formation threshold and the gas pattern read), c_s the isothermal sound speed of the cold neutral medium,
``sqrt(k T / mu m_H)`` at its column-weighted median temperature (70 K, Heiles & Troland 2003) with ``mu = 1.27``
(:data:`ATOMIC_MEAN_WEIGHT`): 0.675 km/s, M = 8.90, sigma = 0.501 on every ring (both numbers are constants of the
model, so the ring's value is the galaxy's). The measured galaxy HI widths, 0.19-0.51 dex (0.44-1.17 in ln;
Berkhuijsen & Fletcher 2015, beam-smoothed, with their gradients), are the disclosed check beside it.

**The shear** (D221 item 4). An isotropic field t old: ``strain = (dOmega / dlnR) t``, ``t = min(1 / A, cap)``, A
the Oort constant ``(v / R - dv/dR) / 2`` from the published rotation curve (``circular_velocity``, checkpoint 1's -
the curve the epicyclic frequency and the gas pattern read; the model publishes no Oort constant, so it is derived
here) at the ring's middle radius. Since ``dOmega / dlnR = -2 A`` the strain is ``-2 A t``: exactly -2 wherever
``t = 1 / A`` (asserted by :func:`shear_strain`), ``-2 A cap`` where the cap binds (outside 1.9 kpc on the default
galaxy). **Its polar form**: ``noise.shear`` maps ``x' = x - s y`` with x along the rotation and y outward; on the
disc the field is read at ``(R, phi - Theta(R))`` with ``dTheta / dlnR = s`` - in each point's own frame
``R dphi' = R dphi - s dR``, which is that shear exactly, at every azimuth - and ``Theta(R) = twist_r + s_r
ln(R / R_r)``, R_r the ring's inner edge and ``twist_r`` the integral of the strain over ln R from the grid's first
radius to it (published per ring), so the read positions are continuous across ring edges. One Cartesian
``noise.shear`` would shear along a single direction of the plane, the rotation's only on one line through the centre.
**The sense** (S62's review, finding 1; D221): x is along the rotation, and the disc turns towards *decreasing* phi
(``pattern.rotation_sense``, read off the arms' winding: their azimuth grows outward, so they trail). The strain and
the twist are angles in the disc's own sense - **negative strain = trailing, in the disc's own sense** - and the read
in phi is ``phi - sense (twist_r + s_r ln(R / R_r))`` with ``sense = rotation_sense(pitch_angle)`` (-1): a structure
at one read angle has ``phi = const + sense s ln R``, its azimuth growing outward as the arms' does. (The first build
read ``phi - Theta`` without the sense - a shear for a disc turning towards +phi - and its filaments led: the
autocorrelation's major axis in (+phi, outward) read (-0.90, +0.44) on ring 8; the reviewer's measurement.)
*The anisotropy by another estimator* (S62's review, finding 7): the axis ratio ``noise.shear_anisotropy`` derives is
the zero-lag curvature's, which the gate reads from the gradient covariance (5.52 / 2.73 / 2.18 against 5.83 / 2.72 /
2.17 on rings 1, 8, 11); the autocorrelation's half-maximum contour reads 4.91 / 2.36 / 1.91, 12-16 % low - value
noise's square-lattice anisotropy and the pixels' resolution of the minor axis at large lags, not a defect.

**Unit mean per cell** (D221 item 5): each level-0 cell's normaliser is ``noise.lognormal_normaliser`` of the field
over the cell's quadrature lattice - L1's table lattice (two points per 47.5 pc along the ring's width and along the
sector's outer arc, the ``cell`` table's density: the lead's ruling 4, for the cost), each point weighted by R - so
the map's weighted mean over that lattice is 1 to rounding in every cell, and every ring total of what it will
multiply is kept. Its error at other points, measured against a lattice four times denser (eight points per
47.5 pc) on ten cells (rings 0, 1, 8 twice and 20, two seeds): rms 9.7e-3, worst 1.83e-2 (ring 0); one point per
47.5 pc reads 7.8e-2 at worst and one and a half 3e-2 on the inner rings, so two is the sparsest within 2e-2.
**Cost** - S62 (D221): measured 4.6-5.1 s cold for the cell table (5 258 240 lattice points times six octaves of
float64 value noise; the noise alone 5.5 s in float64, 3.4 s in float32); the budget of 3 s was the lead's
estimate, and the lead accepted the measured cost for this lattice (register debt #163: a shared or float32
lattice is V7's, where the shader evaluates the same noise). The whole run, cold, the default galaxy, layer on, on a
machine running another session's tests: 43.8 and 45.6 s before the stage, 52.6 and 57.4 s with it; layer off 3.3
and 3.7 s (the stage realises nothing then); ``python -m galaxy.specs``' performance table, as loaded, the stage
6.7 s cold in ``azimuthal`` and 7.1 s in ``basic``. ``region: whole disc`` does not run it (5.3 s before, 6.0 after).

**What a shader reads** (D221 item 6): the seed; per ring (the table ``ring``, the 32 level-0 rings) the break index,
the Mach number, sigma, the strain, the twist and the sum's normaliser; per cell the normaliser; the disc's sense
(``rotation_sense`` of the published ``pitch_angle``); and the model's constants. The octave amplitudes are ``ladder_weights(s, 1, 6, b)``, products of two gains and ``top``: committed in
``vectors.json`` for every b. :meth:`GasFluctuationField.evaluate` is the reference evaluator.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import census_clustering as _l1
from galaxy.layer import compose as _compose
from galaxy.layer import noise as _noise

LACUNARITY = _l1.LACUNARITY  # one noise: L1's octaves halve, and so do these
SEED_PATH = _l1.SEED_PATH  # and on L1's path (D220 part II item 6)
KM_S_PER_KPC_IN_PER_MYR = 1.0 / 977.792221  # 1 km/s/kpc in 1/Myr [inferred: 1 kpc / (1 km/s) = 977.79 Myr]
TWO_PI = 2.0 * math.pi
# The wavelength an octave of value noise carries, in its lattice cells: flat up to a quarter cycle per cell
# (noise.noise2's measured spectrum), so octave j lays the spectrum's level near 4 l_j (the lead's ruling 2, S62).
OCTAVE_WAVELENGTH = 4.0
# The mean mass per particle of neutral atomic gas in proton masses, for the cold neutral medium's sound speed:
# 1.27 for He/H = 0.1 by number, (1 + 4 x 0.1) / (1 + 0.1) [inferred]; Heiles & Troland 2003 adopt 1.4 (sect. 6.2).
ATOMIC_MEAN_WEIGHT = 1.27
# The constants of the model the field is made of, by role (G1's ruling 2b; galaxy/models/level0.py).
CONSTANTS: Mapping[str, str] = {
    "scale": "CENSUS_CLUSTERING_SCALE",
    "slope": "CENSUS_CLUSTERING_SPECTRAL_SLOPE",
    "octaves": "GAS_FLUCTUATION_OCTAVES",
    "change": "GAS_FLUCTUATION_SLOPE_CHANGE",
    "break_factor": "GAS_FLUCTUATION_BREAK_FACTOR",
    "width_a": "GAS_FLUCTUATION_WIDTH_A",
    "width_b": "GAS_FLUCTUATION_WIDTH_B",
    "temperature": "CNM_TEMPERATURE",
    "dispersion": "GAS_DISPERSION",
    "cap": "GAS_FLUCTUATION_SHEAR_CAP",
}


def field_seed(texture_seed: int) -> int:
    """The noise's 32-bit seed: L1's, the same fold of the same child (D221 item 1)."""
    return _l1.field_seed(texture_seed)


def octave_scales_pc(scale_kpc: float, octaves: int) -> np.ndarray:
    """The octaves' lattice scales in pc: ``1000 scale / 2^j``."""
    return 1000.0 * float(scale_kpc) / LACUNARITY ** np.arange(int(octaves))


def break_octave(height_pc: float, scale_kpc: float, octaves: int, factor: float = math.pi,
                 wavelength: float = OCTAVE_WAVELENGTH) -> int:
    """The break's octave index: how many octaves carry a wavelength, ``wavelength`` lattice cells, not below
    ``factor * height_pc``. ``wavelength = 1`` is the literal mapping D221 item 2 was first written with."""
    height_pc = float(height_pc)
    if not (math.isfinite(height_pc) and height_pc > 0.0):
        raise ValueError(f"the break needs a published, positive gas height; got {height_pc!r}")
    return int(np.sum(float(wavelength) * octave_scales_pc(scale_kpc, octaves) >= float(factor) * height_pc))


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


def disc_sense(pitch_deg: float) -> float:
    """The disc's sense of rotation in phi (``pattern.rotation_sense``: -1, towards decreasing phi), which turns the
    strain's angles (the disc's own sense) into phi's; -1 for a pitch that is not finite, as the arm pieces take it."""
    from galaxy.stages.pattern import rotation_sense

    pitch_deg = float(pitch_deg)
    return float(rotation_sense(pitch_deg)) if math.isfinite(pitch_deg) else -1.0


# --- the per-ring parameters and the field ------------------------------------------------------------------------

def ring_heights(edges: np.ndarray, R: np.ndarray, height_pc: np.ndarray) -> np.ndarray:
    """The gas height at each ring's middle radius (pc), the last finite ring's carried outward where the height is not
    published (the lead's ruling 3) and the first finite ring's inward if the innermost are not."""
    mid = 0.5 * (edges[:-1] + edges[1:])
    h = np.interp(mid, np.asarray(R, dtype=float), np.asarray(height_pc, dtype=float))
    finite = np.isfinite(h) & (h > 0.0)
    if not finite.any():
        raise ValueError("the gas fluctuation field needs a published gas height on at least one ring")
    index = np.where(finite, np.arange(h.size), -1)
    index = np.maximum.accumulate(index)
    index = np.where(index < 0, int(np.argmax(finite)), index)
    return h[index]


def ring_parameters(R, height_pc, v_kms, constants: Mapping[str, Any], pitch_deg: float) -> dict[str, Any]:
    """Per level-0 ring: the break index, the Mach number, sigma, the shear time, the strain, the twist at the ring's
    inner edge and the octave sum's normaliser - every number but the seed a shader needs (the module docstring) - and
    the disc's sense from ``pitch_deg`` (``sense``, one number). The strain and the twist are in the disc's own sense."""
    from galaxy.stages.clouds import sound_speed
    from galaxy.stages.systems import cell_edges

    c = constants
    R = np.asarray(R, dtype=float)
    edges, _ = cell_edges(R)
    mid = 0.5 * (edges[:-1] + edges[1:])
    octaves, scale = int(c[CONSTANTS["octaves"]]), float(c[CONSTANTS["scale"]])
    h = ring_heights(edges, R, height_pc)
    breaks = np.array([break_octave(x, scale, octaves, float(c[CONSTANTS["break_factor"]])) for x in h])
    c_s = sound_speed(float(c[CONSTANTS["temperature"]]), ATOMIC_MEAN_WEIGHT)
    mach = float(c[CONSTANTS["dispersion"]]) / c_s
    a_w, b_w = float(c[CONSTANTS["width_a"]]), float(c[CONSTANTS["width_b"]])
    sigma = math.sqrt(a_w * math.log1p(b_w * b_w * mach * mach))
    strain, t = shear_strain(np.interp(mid, R, oort_a(R, v_kms)), float(c[CONSTANTS["cap"]]))
    twist = np.concatenate([[0.0], np.cumsum(strain * np.log(edges[1:] / edges[:-1]))[:-1]])
    slope, change = float(c[CONSTANTS["slope"]]), float(c[CONSTANTS["change"]])
    norms = np.array([ladder_weights(slope, change, octaves, int(b))[1] for b in breaks])
    n = breaks.size
    return {"edges": edges, "height": h, "break_octave": breaks.astype(float), "mach": np.full(n, mach),
            "sigma": np.full(n, sigma), "shear_time": t, "strain": strain, "twist": twist, "norm": norms,
            "sense": disc_sense(pitch_deg)}


@dataclass(frozen=True)
class GasFluctuationField:
    """The field: its seed, the model's numbers and the published per-ring parameters. ``evaluate`` is the map."""

    seed: int
    scale: float  # kpc, the coarsest lattice cell (L1's)
    slope: float  # the gain's slope above the break (L1's)
    change: float  # the slope change below it
    octaves: int
    edges: np.ndarray  # the 33 ring edges, kpc
    break_octave: np.ndarray  # per ring, int
    sigma: np.ndarray  # per ring
    strain: np.ndarray  # per ring
    twist: np.ndarray  # per ring, rad at the ring's inner edge, in the disc's own sense
    sense: float  # the disc's rotation in phi (pattern.rotation_sense, -1): turns the strain's angles into phi's
    cell_normaliser: np.ndarray | None = None  # per level-0 cell; None before the table is made

    def amplitudes(self) -> np.ndarray:
        """The ladder's amplitudes times its normaliser for every break index: a (octaves + 1, octaves) table."""
        rows = []
        for b in range(self.octaves + 1):
            amps, norm = ladder_weights(self.slope, self.change, self.octaves, b)
            rows.append([a * norm for a in amps])
        return np.array(rows)

    def ring_of(self, R: np.ndarray) -> np.ndarray:
        """Each radius's level-0 ring, the first and last rings holding everything inside and beyond them."""
        return np.clip(np.searchsorted(self.edges, np.asarray(R, dtype=float), side="right") - 1, 0, self.edges.size - 2)

    def read_positions(self, x, y, ring, dtype=np.float64) -> tuple[np.ndarray, np.ndarray]:
        """The sheared positions the noise is read at: ``(R, phi - Theta(R))`` (the module docstring's polar shear),
        Theta from ``ring``'s strain and twist turned into phi by the disc's sense; R below the first ring's inner edge
        reads the twist there. In the working precision, in this order: ``R = hypot(x, y)``, ``theta = sense * (twist
        + strain * log(max(R, R_0) / R_r))``, ``phi = atan2(y, x) - theta``, ``(R cos phi, R sin phi)``."""
        ft = np.dtype(dtype).type
        x, y = np.broadcast_arrays(np.asarray(x, dtype=ft), np.asarray(y, dtype=ft))
        ring = np.broadcast_to(np.asarray(ring), x.shape)
        R = np.hypot(x, y)
        inner = self.edges.astype(ft)[ring]
        theta = ft(self.sense) * (self.twist.astype(ft)[ring] + self.strain.astype(ft)[ring] * np.log(np.maximum(R, ft(self.edges[0])) / inner))
        phi = np.arctan2(y, x) - theta
        return R * np.cos(phi), R * np.sin(phi)

    def gaussian(self, x, y, ring=None, dtype=np.float64) -> np.ndarray:
        """The unit-variance sum at (x, y) kpc, read sheared, with each point's own ring's ladder - or, given ``ring``,
        that ring's ladder and shear at every point (a flat patch read with one ring's numbers, as the gate does)."""
        x, y = np.broadcast_arrays(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
        ring = self.ring_of(np.hypot(x, y)) if ring is None else np.broadcast_to(np.asarray(ring, dtype=int), x.shape)
        return self._sum(*self.read_positions(x, y, ring, dtype), self.amplitudes()[self.break_octave[ring]], dtype)

    def gaussian_polar(self, R, phi, ring: int) -> np.ndarray:
        """:meth:`gaussian` at ``(R, phi)`` with one ring's numbers: the same read positions without the round trip
        through (x, y) (the cell table's path; equal to :meth:`gaussian` to rounding, tested)."""
        R, phi = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(phi, dtype=float))
        theta = self.sense * (self.twist[ring] + self.strain[ring] * np.log(np.maximum(R, self.edges[0]) / self.edges[ring]))
        phi = phi - theta
        return self._sum(R * np.cos(phi), R * np.sin(phi), self.amplitudes()[self.break_octave[ring]])

    def _sum(self, xs: np.ndarray, ys: np.ndarray, weights: np.ndarray, dtype=np.float64) -> np.ndarray:
        """``sum_j w_j octave_j`` at read positions, coarse to fine; ``weights`` (amplitude times the ring's
        normaliser) per point (..., octaves) or one row; the frequency stepped as ``noise.fractal`` steps it."""
        ft = np.dtype(dtype).type
        weights = np.asarray(weights).astype(ft)
        total = np.zeros(np.shape(xs), dtype=ft)
        f, step = ft(1.0 / self.scale), ft(LACUNARITY)
        for j in range(self.octaves):
            total = total + weights[..., j] * _noise.noise2(self.seed, xs * f, ys * f, octave=j, dtype=ft)
            f = ft(f * step)
        return total

    def evaluate(self, x, y, dtype=np.float64) -> np.ndarray:
        """The map at face-on positions (kpc): ``normaliser_cell exp(sigma_r g - sigma_r^2 / 2)``, the cell and ring
        the point's own. Unit mean over every level-0 cell's quadrature lattice. ``dtype`` float32 is what a shader
        computes (the cell and ring found in float64, as a shader is handed them)."""
        from galaxy.stages.systems import CELL_SECTORS

        if self.cell_normaliser is None:
            raise ValueError("the field's cell normalisers are not made yet")
        ft = np.dtype(dtype).type
        x, y = np.broadcast_arrays(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
        ring = self.ring_of(np.hypot(x, y))
        sector = np.clip(np.floor(np.mod(np.arctan2(y, x), TWO_PI) / (TWO_PI / CELL_SECTORS)).astype(int), 0, CELL_SECTORS - 1)
        sigma = self.sigma.astype(ft)[ring]
        g = self.gaussian(x, y, ring, dtype)
        return self.cell_normaliser.astype(ft)[ring * CELL_SECTORS + sector] * np.exp(sigma * g - ft(0.5) * sigma * sigma)

    def cell_lattice(self, ring: int, sector: int, points: int, l1_finest: float) -> np.ndarray:
        """A level-0 cell's quadrature lattice, (n, 2) in (R, phi): L1's table lattice rule (``ClusteringField.lattice``)
        - ``points`` per L1 finest lattice cell along the ring's width and along the sector's outer arc."""
        from galaxy.stages.systems import CELL_SECTORS

        lo, hi = float(self.edges[ring]), float(self.edges[ring + 1])
        width = TWO_PI / CELL_SECTORS
        n_r = max(1, math.ceil(points * (hi - lo) * l1_finest))
        n_phi = max(1, math.ceil(points * hi * width * l1_finest))
        return _noise.cell_quadrature(lo, hi, sector * width, (sector + 1) * width, (n_r, n_phi))

    def cell_normalisers(self, points: int, l1_finest: float) -> np.ndarray:
        """Every level-0 cell's ``noise.lognormal_normaliser`` on its lattice, R-weighted, ring-major (1 024)."""
        from galaxy.stages.systems import CELL_RINGS, CELL_SECTORS

        out = np.empty(CELL_RINGS * CELL_SECTORS)
        for r in range(CELL_RINGS):
            q = np.stack([self.cell_lattice(r, s, points, l1_finest) for s in range(CELL_SECTORS)])  # (sectors, n, 2)
            g = self.gaussian_polar(q[..., 0], q[..., 1], r)
            out[r * CELL_SECTORS:(r + 1) * CELL_SECTORS] = _noise.lognormal_normaliser(g, float(self.sigma[r]), q[..., 0])
        return out


def field_of(seed: int, parameters: Mapping[str, np.ndarray], constants: Mapping[str, Any],
             cell_normaliser: np.ndarray | None = None) -> GasFluctuationField:
    """The field from its seed, its per-ring parameters (:func:`ring_parameters`, or a run's published columns with
    ``edges`` and ``sense``) and the model's constants."""
    c = constants
    return GasFluctuationField(
        int(seed), float(c[CONSTANTS["scale"]]), float(c[CONSTANTS["slope"]]), float(c[CONSTANTS["change"]]),
        int(c[CONSTANTS["octaves"]]), np.asarray(parameters["edges"], dtype=float),
        np.asarray(parameters["break_octave"]).astype(int), np.asarray(parameters["sigma"], dtype=float),
        np.asarray(parameters["strain"], dtype=float), np.asarray(parameters["twist"], dtype=float),
        float(parameters["sense"]), None if cell_normaliser is None else np.asarray(cell_normaliser, dtype=float),
    )


def l1_finest_frequency(constants: Mapping[str, Any]) -> float:
    """L1's finest lattice frequency (cells per kpc), whose lattice the cell normalisers are taken on."""
    return LACUNARITY ** (int(constants[_l1.CONSTANTS["octaves"]]) - 1) / float(constants[_l1.CONSTANTS["scale"]])


# --- the stage ------------------------------------------------------------------------------------------------------

_STANDS_IN_FOR = (
    "The turbulent structure of the diffuse ISM between the clouds - where inside a cell the diffuse gas and its dust "
    "lie denser or thinner, from the kiloparsec scales down to a few parsecs - which the model does not compute (a "
    "turbulent, magnetised, self-gravitating disc would: RESEARCH_AREAS section 1). Not the clouds, the clusters or "
    "the HII regions (the census's), and nothing the arms, the bar or the profile already give."
)
_CONSERVES = (
    "Every ring total and every level-0 cell's total of what it will multiply - the diffuse gas and the diffuse dust "
    "the render and the viewer draw (V7): the map has unit mean, R-weighted, over every cell's quadrature lattice to "
    "rounding (measured 1e-15). It does not keep where within a cell the dust and gas lie, and it keeps the cell's "
    "mean exactly on that lattice only: at other points the mean is off by the lattice's error - 9.7e-3 rms, 1.83e-2 "
    "at worst, at two points per 47.5 pc against a lattice four times denser (ten cells, two seeds). It shares the noise's coarse octaves with the clouds' "
    "clustering field before the shear and differs from it by the shear alone at those scales - the clouds' map "
    "is L1's own evaluation and is unsheared; this one is read at (R, phi - Theta(R)) with dTheta/dlnR the disc's sense (-1) times the ring's "
    "strain, which is noise.shear in each point's own frame, x along the rotation (the disc's sense, so the "
    "structures trail as the arms do). It moves no cloud."
)
_STATISTIC = (
    "The 2-D column spectrum P(k) ~ k^-1.53 above the break (the clustering field's slope; the sources' THINGS median "
    "-1.6, half the sample -1.9 to -1.5 [verified: Dutta et al. 2013, NewA 19, 89, Table 2; docs/READING_GAS_SPECTRA.md "
    "2.4]; the Local Group's -2.2 to -2.7) and steeper by one below pi h [verified: Elmegreen & Scalo 2004, ARA&A 42, "
    "211, sect. 2.1; Elmegreen, Kim & Staveley-Smith 2001, ApJ 548, 749, sect. 3.3; Dutta et al. 2009, MNRAS 397, L60; "
    "READING_GAS_SPECTRA.md 2.1, 2.4, 2.14]; the log-normal width sigma^2 = 0.11 ln(1 + M^2/9) [verified: Burkhart & "
    "Lazarian 2012, ApJL 755, L19, eq. 3, Table 1; READING_GAS_SPECTRA.md 2.10] at M = 6 km/s over the cold neutral "
    "medium's 0.675 km/s (70 K [verified: Heiles & Troland 2003, ApJ 586, 1067, Table 2]); the shear's strain over "
    "t = min(1/A, 30 Myr) [verified: Jeffreson & Kruijssen 2018, MNRAS 476, 3688, eq. 23; Meidt et al. 2015, sect. "
    "6.2; Chevance et al. 2020, sect. 5.2; docs/READING_SPURS.md 4a-4c]. Measured on the field: see "
    "tests/test_gas_fluctuation.py (D221)."
)


def _decl(name: str, label: str, unit: str, kind: Kind, about: str, **extra: Any) -> FieldDecl:
    return FieldDecl(
        name=name, label=label, unit=unit, kind=kind, meaningful_zero=True, provenance="synthetic",
        about=about + " NaN with the randomness layer off: no field is realised then (D164; D215's ruling 5).",
        stands_in_for=_STANDS_IN_FOR, conserves=_CONSERVES, statistic=_STATISTIC, **extra,
    )


_RING = " One row a level-0 ring, innermost first; read by a shader with the seed (S62, D221 item 6)."
GAS_FLUCTUATION_SEED = _decl(
    "gas_fluctuation_seed", "Gas fluctuation field's seed", "dimensionless", Kind.SCALAR,
    "The 32-bit seed of the gas fluctuation field: the clustering field's own, folded once from the layer's seed on "
    "the one noise's path, so the two fields share their coarse octaves. With the per-ring parameters and the model's "
    "numbers it makes the field evaluable anywhere. **Not shown by the viewer** (rule D4): a key, no quantity.",
)
GAS_FLUCTUATION_BREAK = _decl(
    "gas_fluctuation_break_octave", "Gas fluctuation: octaves above the break", "count", Kind.TABLE_COLUMN,
    "How many of the field's octaves carry a wavelength (four lattice cells) not below pi times the ring's gas scale "
    "height, whose gain is the shallow slope's; the finer ones take the steep slope's. Past the last published height "
    "the last finite ring's." + _RING, of="ring",
)
GAS_FLUCTUATION_MACH = _decl(
    "gas_fluctuation_mach", "Gas fluctuation: Mach number", "dimensionless", Kind.TABLE_COLUMN,
    "The diffuse gas's sonic Mach number the field's width is read at: the cold gas's turbulent dispersion over the "
    "isothermal sound speed of the cold neutral medium at its median temperature." + _RING, of="ring",
)
GAS_FLUCTUATION_SIGMA = _decl(
    "gas_fluctuation_sigma", "Gas fluctuation: log-normal width", "dimensionless", Kind.TABLE_COLUMN,
    "The width of the map's logarithm: the column-density variance's relation to the Mach number, from simulated "
    "solenoidal MHD turbulence." + _RING, of="ring",
)
GAS_FLUCTUATION_STRAIN = _decl(
    "gas_fluctuation_strain", "Gas fluctuation: shear strain", "dimensionless", Kind.TABLE_COLUMN,
    "How far the disc's differential rotation has sheared the field: dOmega/dlnR times the shear time, capped where "
    "feedback ends a cloud first; -2 where the shear time is not capped. In the disc's own sense: negative strain = "
    "trailing, in the disc's own sense - the azimuth along the rotation, which turns towards decreasing azimuth "
    "(read off the arms' winding), so the field's structures trail as the arms do." + _RING, of="ring",
)
GAS_FLUCTUATION_TWIST = _decl(
    "gas_fluctuation_twist", "Gas fluctuation: twist at the ring's inner edge", "rad", Kind.TABLE_COLUMN,
    "The angle the field is read back by at the ring's inner edge, in the disc's own sense (along the rotation; "
    "the azimuth's is minus it, the disc turning towards decreasing azimuth): the strain integrated over ln R from "
    "the grid's first radius, so that the sheared read positions are continuous across rings." + _RING, of="ring",
)
GAS_FLUCTUATION_NORM = _decl(
    "gas_fluctuation_norm", "Gas fluctuation: octave sum's normaliser", "dimensionless", Kind.TABLE_COLUMN,
    "One over the root of the sum of the ring's octave amplitudes squared: what makes the octave sum's variance 1 at "
    "every point." + _RING, of="ring",
)
GAS_FLUCTUATION_CELL_NORMALISER = _decl(
    "gas_fluctuation_cell_normaliser", "Gas fluctuation: cell normaliser", "dimensionless", Kind.TABLE_COLUMN,
    "Each level-0 cell's normaliser of the gas fluctuation map: one over the map's area-weighted mean on the cell's "
    "quadrature lattice, so that the map multiplied by it has unit mean in the cell and moves no gas or dust between "
    "cells (one row a cell, ring by ring, sector by sector). Not shown by the viewer, which will multiply its own "
    "evaluation of the same noise by it in V7 (S62, D221).", of="cell",
    # S62 (D221): taken on L1's table lattice, two points per 47.5 pc - 4.6-5.1 s cold, accepted by the lead over its
    # 3 s estimate (sparser lattices miss 2e-2 on the inner rings); debt #163.
)
RING_COLUMNS = (GAS_FLUCTUATION_BREAK, GAS_FLUCTUATION_MACH, GAS_FLUCTUATION_SIGMA, GAS_FLUCTUATION_STRAIN,
                GAS_FLUCTUATION_TWIST, GAS_FLUCTUATION_NORM)
PUBLISHES = (GAS_FLUCTUATION_SEED, *RING_COLUMNS, GAS_FLUCTUATION_CELL_NORMALISER)
RING_KEYS = {"gas_fluctuation_break_octave": "break_octave", "gas_fluctuation_mach": "mach",
              "gas_fluctuation_sigma": "sigma", "gas_fluctuation_strain": "strain",
              "gas_fluctuation_twist": "twist", "gas_fluctuation_norm": "norm"}


def evaluate(source: Any, constants: Mapping[str, Any], R: np.ndarray, x, y) -> np.ndarray:
    """The reference evaluator: the map at face-on positions (x, y) kpc of a run (``source``: its fields, or a stage's
    view), on the run's grid radii ``R``, through ``compose.gas_fluctuation`` - and 1 everywhere with the layer off
    (the field's neutral: it multiplies nothing then)."""
    field = _compose.gas_fluctuation(source, constants, R)
    if field is None:
        return np.ones(np.broadcast_shapes(np.shape(x), np.shape(y)))
    return field.evaluate(x, y)


def compute_gas_fluctuation(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants

    def draw() -> dict[str, Any]:
        params = ring_parameters(ctx.grid.R, ctx.fields["gas_scale_height"], ctx.fields["circular_velocity"], c,
                                 float(ctx.fields["pitch_angle"]))
        field = field_of(field_seed(int(ctx.seeds["texture_seed"])), params, c)
        normaliser = field.cell_normalisers(int(c[_l1.TABLE_POINTS]), l1_finest_frequency(c))
        return {"gas_fluctuation_seed": float(field.seed), **{n: params[k] for n, k in RING_KEYS.items()},
                "gas_fluctuation_cell_normaliser": normaliser}

    def neutral() -> dict[str, Any]:
        from galaxy.stages.systems import CELL_COUNT, CELL_RINGS

        return {"gas_fluctuation_seed": float("nan"), **{n: np.full(CELL_RINGS, np.nan) for n in RING_KEYS},
                "gas_fluctuation_cell_normaliser": np.full(CELL_COUNT, np.nan)}

    return _compose.realise(ctx.fields, draw, neutral)


GAS_FLUCTUATION = IMPLEMENTATIONS.register(
    Stage(
        id="gas_fluctuation", slot="gas_fluctuation", checkpoint=5,
        about=(
            "The randomness layer's turbulent structure of the diffuse gas between the clouds: a log-normal field of "
            "lattice noise in the plane, the clustering field's noise continued six octaves down to 6 pc on the "
            "layer's own seed, steepening below the gas layer's thickness, as wide as the cold gas's Mach number "
            "makes it and sheared by the disc's rotation, with unit mean in every cell. Synthetic: it multiplies "
            "nothing yet (the render's and the viewer's diffuse dust and gas will, in V7), moves no total, and with "
            "the layer off realises nothing."
        ),
        compute=compute_gas_fluctuation,
        layer_stage=True,
        reads_seeds=("texture_seed",),
        reads_constants=(*CONSTANTS.values(), _l1.CONSTANTS["octaves"], _l1.TABLE_POINTS),
        requires=("gas_scale_height", "circular_velocity", "pitch_angle"),  # the pitch: the disc's sense (finding 1)
        publishes=PUBLISHES,
    )
)


# --- the committed test vectors (D221 item 6; S55's convention, ``noise.build_vectors``) ------------------------------

VECTORS_SECTION = "gas_fluctuation"  # this field's section of ``layer/vectors.json``, beside the noise's own
VECTOR_CELLS = ((1, 3), (8, 0))  # (ring, sector) of the two cells whose normalisers the vectors carry
_F32 = np.float32


def _f32(value) -> float:
    return float(_F32(value))


def default_vector_inputs() -> dict[str, Any]:
    """The vectors' inputs, from the default galaxy run with the layer on: the field's seed, the model's numbers and the
    ring table - every float rounded to float32, so a float32 program is given exactly these inputs."""
    from galaxy.core.registry import production
    from galaxy.models import DEFAULT
    from galaxy.run import run
    from galaxy.stages.systems import cell_edges

    models, _, _ = production()
    model = models.get(DEFAULT) if isinstance(DEFAULT, str) else DEFAULT
    names = (GAS_FLUCTUATION_SEED.name, *RING_KEYS, "pitch_angle")
    out = run(model, only=names)
    c = {k: v.value for k, v in model.constants.items()}
    f = out.fields
    return {
        "seed": int(f[GAS_FLUCTUATION_SEED.name]), "scale": _f32(c[CONSTANTS["scale"]]),
        "slope": float(c[CONSTANTS["slope"]]), "change": float(c[CONSTANTS["change"]]),
        "octaves": int(c[CONSTANTS["octaves"]]), "lacunarity": LACUNARITY,
        "table_points": int(c[_l1.TABLE_POINTS]), "l1_finest_frequency": _f32(l1_finest_frequency(c)),
        "edges": [_f32(e) for e in cell_edges(out.grid.R)[0]],
        "break_octave": [int(b) for b in f["gas_fluctuation_break_octave"]],
        "sigma": [_f32(v) for v in f["gas_fluctuation_sigma"]],
        "strain": [_f32(v) for v in f["gas_fluctuation_strain"]],
        "twist": [_f32(v) for v in f["gas_fluctuation_twist"]],
        "sense": disc_sense(f["pitch_angle"]),
    }


def vector_field(inputs: Mapping[str, Any], cell_normaliser: np.ndarray | None = None) -> GasFluctuationField:
    """The field the vectors' inputs define."""
    return GasFluctuationField(
        int(inputs["seed"]), float(inputs["scale"]), float(inputs["slope"]), float(inputs["change"]),
        int(inputs["octaves"]), np.asarray(inputs["edges"], dtype=float), np.asarray(inputs["break_octave"], dtype=int),
        np.asarray(inputs["sigma"], dtype=float), np.asarray(inputs["strain"], dtype=float),
        np.asarray(inputs["twist"], dtype=float), float(inputs["sense"]), cell_normaliser,
    )


def build_vectors(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """This field's section of the vectors: the amplitudes for every break index, the sum ``g`` at points across the
    disc (float64 and float32), two cells' normalisers on their lattice and the map at points inside them. Positions
    are multiples of 1/1024 kpc (exact in float32). Compared to 1e-12 (``log``, ``atan2``, ``cos``, ``exp`` need not
    round correctly in a C library); a float32 value is compared to its float64 one by the tolerance measured here."""
    from galaxy.stages.systems import CELL_COUNT, CELL_SECTORS

    field = vector_field(inputs)
    draw = _noise._counter(62)
    points = [[_noise._dyadic(draw, 24), _noise._dyadic(draw, 24)] for _ in range(48)]
    points += [[_noise._dyadic(draw, 2), _noise._dyadic(draw, 2)] for _ in range(8)]  # the inner disc
    xy = np.array(points)
    ring = field.ring_of(np.hypot(xy[:, 0], xy[:, 1]))
    g64, g32 = field.gaussian(xy[:, 0], xy[:, 1]), field.gaussian(xy[:, 0], xy[:, 1], dtype=_F32)
    sums = [[x, y, int(r), float(a), float(b)] for (x, y), r, a, b in zip(points, ring, g64, g32)]
    normaliser = np.ones(CELL_COUNT)
    cells = []
    for r, s in VECTOR_CELLS:
        q = field.cell_lattice(r, s, int(inputs["table_points"]), float(inputs["l1_finest_frequency"]))
        value = float(_noise.lognormal_normaliser(field.gaussian_polar(q[:, 0], q[:, 1], r), float(field.sigma[r]), q[:, 0]))
        normaliser[r * CELL_SECTORS + s] = value
        cells.append({"ring": r, "sector": s, "lattice": list(q.shape), "normaliser": value})
    field = vector_field(inputs, normaliser)
    rows = []
    for r, s in VECTOR_CELLS:
        lo, hi = field.edges[r], field.edges[r + 1]
        width = TWO_PI / CELL_SECTORS
        for _ in range(8):
            rad = lo + (draw() % 1024 + 0.5) / 1024.0 * (hi - lo)
            phi = (s + (draw() % 1024 + 0.5) / 1024.0) * width
            x, y = _f32(rad * math.cos(phi)), _f32(rad * math.sin(phi))
            rows.append([x, y, r, s, float(field.evaluate(x, y)), float(field.evaluate(x, y, dtype=_F32))])
    amplitudes = field.amplitudes()
    return {
        "compare": "1e-12",
        "about": ("galaxy.layer.gas_fluctuation (S62, D221): g = sum_j w[b_r][j] noise2(seed, X f_j, Y f_j, octave=j), "
                  "f_j = 2^j / scale, (X, Y) = R (cos, sin)(atan2(y, x) - sense (twist_r + strain_r log(max(R, edges[0]) / "
                  "edges[r]))), sense the disc's rotation in phi (-1); the map = normaliser_cell exp(sigma_r g - sigma_r^2 / 2); w[b] = amplitude times the "
                  "ladder's normaliser for break index b; *_f32 the float32 path"),
        "inputs": dict(inputs),
        "weights": [[float(w) for w in row] for row in amplitudes],
        "sums": {"columns": ["x", "y", "ring", "g", "g_f32"], "rows": sums},
        "cells": cells,
        "maps": {"columns": ["x", "y", "ring", "sector", "value", "value_f32"], "rows": rows},
    }


def write_vectors(inputs: Mapping[str, Any] | None = None) -> Any:
    """Write this field's section into ``layer/vectors.json`` beside the noise's (a decision's act, as the noise's):
    ``uv run python -c "from galaxy.layer import gas_fluctuation as g; g.write_vectors()"``."""
    import json

    path = _noise.VECTORS
    document = json.loads(path.read_text(encoding="utf-8"))
    document[VECTORS_SECTION] = build_vectors(default_vector_inputs() if inputs is None else inputs)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_noise.render_vectors(document))
    return path

