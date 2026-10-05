"""Reid et al. 2019's maser-fitted spiral arms of the Milky Way, and the disclosed checks defined on them.

**The table is the template's own data since S60** (D219 item 8: the four major arms and the Local arm are pinned):
``galaxy.templates.REID_2019_TABLE2``, verbatim from ``docs/READING_ARM_SEGMENTS.md`` A1.3 [verified: Reid et al.
2019, ApJ 885, 131 = arXiv:1910.03357, Table 2 and note]; this module reads it from there. The form:
ln(R/R_kink) = −(β − β_kink) tan ψ, ψ = ψ_< for β ≤ β_kink and ψ_> for β > β_kink; β the Galactocentric azimuth, 0
towards the Sun, increasing in the direction of Galactic rotation; R0 = 8.15 kpc.

**What is checked, and of what** (D219 item 8, which rewords P4's gate sentence): "the composed stellar crest lies
within 0.1 width of each pinned locus over its β range — by construction, asserted, not a test of the model; the
model is tested by the gas and young stars' crest against the maser loci within the masers' σ (0.34 kpc at R₀), a
disclosed check with its null stated". The stellar pieces are *on* the loci by construction; the gas and the young
stars are the model's answer to them, so their crests against the loci are a check. **Not a spec row** (I3).

**The five arms, exactly as taken here** (unchanged from S59's check). The source's four major arms are
Norma–Outer, Scutum–Centaurus(–OSC), Sagittarius–Carina and Perseus; Table 2 has a row for Norma and a row for the
Outer arm, which the source reads as one arm, so **the Norma row's and the Outer row's loci are counted together as
one arm's**. With the Local arm that is five. The 3-kpc arm's row is not used. Each row is sampled every degree
over its printed β range, the ends included.

**The statistic, exactly.** For each locus point: the radial distance to the nearest crest of a contrast along the
point's own azimuth - a crest being a local maximum in R of the contrast's point function there, found on radial
samples 0.005 kpc apart - over the masers' measured width at the point's radius, σ(R) = 336 + 36 (R − 8.15) pc.
Per arm, the median over its points; the statistic is the median of the five arms' medians (the median over all
the points pooled is returned beside it). **Read against its null** (D218's follow-up, item 3, kept): the same
field with the Sun placed at each of 360 azimuths a degree apart (:func:`rotation_null`) - a field with a crest
every kiloparsec or so along any azimuth is seldom far from a locus wherever the Sun stands.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np

from galaxy.templates import MILKY_WAY_PINNED_ARMS, REID_2019_R0, REID_2019_TABLE2

R0 = REID_2019_R0  # kpc, the table's own
TABLE2 = REID_2019_TABLE2
PINNED = MILKY_WAY_PINNED_ARMS
# The five arms of the check, each the rows whose loci are counted as its own.
ARMS: dict[str, tuple[str, ...]] = {
    "Norma-Outer": ("Norma", "Outer"), "Sct-Cen": ("Sct-Cen",), "Sgr-Car": ("Sgr-Car",), "Perseus": ("Perseus",),
    "Local": ("Local",),
}
RADIAL_STEP = 0.005  # kpc: the samples a crest is found on
RADIAL_RANGE = (0.5, 20.0)  # kpc
ROTATIONS = 360  # the Sun-rotation null's azimuths, a degree apart: the loci are sampled every degree

Contrast = Callable[[np.ndarray, np.ndarray], np.ndarray]  # (radii (n,), azimuths (k,)) -> values (n, k)


def width_kpc(R: np.ndarray) -> np.ndarray:
    """The masers' measured arm width (a Gaussian σ) at radius R, kpc: 336 + 36 (R − 8.15) pc."""
    return (336.0 + 36.0 * (np.asarray(R, dtype=float) - R0)) / 1000.0


def locus(row: tuple[str, float, float, float, float, float, float]) -> tuple[np.ndarray, np.ndarray]:
    """(β in degrees, R in kpc) along one row's arm, every degree over its β range."""
    _, lo, hi, kink, r_kink, below, above = row
    beta = np.arange(lo, hi + 0.5, 1.0)
    psi = np.where(beta <= kink, below, above)
    return beta, r_kink * np.exp(-np.radians(beta - kink) * np.tan(np.radians(psi)))


def crests(contrast: Contrast, phi: np.ndarray) -> list[np.ndarray]:
    """The radii, kpc, of the crests of ``contrast`` along each azimuth of ``phi``: local maxima in R on samples
    :data:`RADIAL_STEP` apart, every azimuth at once."""
    r = np.arange(RADIAL_RANGE[0], RADIAL_RANGE[1] + 0.5 * RADIAL_STEP, RADIAL_STEP)
    v = np.asarray(contrast(r, np.asarray(phi, dtype=float)))
    peak = (v[1:-1] > v[:-2]) & (v[1:-1] >= v[2:])
    return [r[1:-1][peak[:, j]] for j in range(v.shape[1])]


def rotation_null(contrast: Contrast, sun_azimuth: float, sense: float) -> tuple[np.ndarray, dict[str, float], float]:
    """(the statistic with the Sun at each of :data:`ROTATIONS` azimuths, each arm's median with the Sun where
    the model puts it, the pooled median there). Entry k of the first is the median over the five arms with the
    Sun at φ_sun + sense · k°, so entry 0 is the model's own Sun. The field is not touched: only where the
    measured loci are laid on it. A locus point at β then stands at φ_sun + sense · (β + k)°, one of the 360
    azimuths whose crests are found once."""
    rows = {row[0]: row for row in TABLE2}
    lines = crests(contrast, sun_azimuth + sense * np.radians(np.arange(ROTATIONS)))
    loci = {arm: [locus(rows[name]) for name in names] for arm, names in ARMS.items()}
    out = np.empty(ROTATIONS)
    per_arm: dict[str, float] = {}
    pooled = math.nan
    for k in range(ROTATIONS):
        medians, everything = {}, []
        for arm, parts in loci.items():
            distances = []
            for beta, R in parts:
                at = np.mod(np.rint(beta).astype(np.int64) + k, ROTATIONS)
                near = np.array([np.abs(lines[j] - radius).min() if lines[j].size else math.inf for j, radius in zip(at, R)])
                distances.append(near / width_kpc(R))
            medians[arm] = float(np.median(np.concatenate(distances)))
            everything.extend(distances)
        out[k] = float(np.median(list(medians.values())))
        if k == 0:
            per_arm, pooled = medians, float(np.median(np.concatenate(everything)))
    return out, per_arm, pooled
