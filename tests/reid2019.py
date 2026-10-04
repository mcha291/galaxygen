"""Reid et al. 2019's maser-fitted spiral arms of the Milky Way, and the disclosed check D218 defines on them.

**Not a pin and not a spec row** (D218 item 5; invariant I3): "Reid 2019 is not pinned; its Table 2 as read defines
a disclosed check: for each of the four major arms and the Local arm, over its β range, the radial distance from
R(β) to the nearest crest of the composed stellar field (layer on, the template's default seeds), in units of the
measured width w(R) = 336 + 36(R − 8.15) pc; the statistic is the median over the five arms' loci, judged against 1
width. Predicted before the build: a miss by 2–4 widths."

**The table**, verbatim from ``docs/READING_ARM_SEGMENTS.md`` A1.3 [verified: Reid et al. 2019, ApJ 885, 131 =
arXiv:1910.03357, Table 2 and note, https://arxiv.org/pdf/1910.03357; all seven rows, two reads of the PDF text
agree digit for digit]. The form: ln(R/R_kink) = −(β − β_kink) tan ψ, ψ = ψ_< for β ≤ β_kink and ψ_> for β > β_kink;
β the Galactocentric azimuth, 0 towards the Sun, increasing in the direction of Galactic rotation; R0 = 8.15 kpc.
The uncertainties the table prints are not entered: the check reads the loci, not their errors.

**The five arms, exactly as taken here.** The ruling's "four major arms" are the source's own (§3.2): Norma–Outer,
Scutum–Centaurus(–OSC), Sagittarius–Carina and Perseus. Table 2 has no row for the Outer–Scutum–Centaurus arm; it
has a row for Norma and a row for the Outer arm, which the source reads as one arm, so **the Norma row's and the
Outer row's loci are counted together as one arm's**. With the Local arm (the source's "isolated arm segment")
that is five. The 3-kpc arm's row is entered and not used (the source: "may not be true spiral arms"). Each row is
sampled every degree over its printed β range, the ends included.

**The statistic, exactly.** For each locus point: the radial distance to the nearest crest of the composed stellar
contrast along the point's own azimuth - a crest being a local maximum in R of the pattern's point function there,
found on radial samples 0.005 kpc apart - over the measured width at the point's radius. Per arm, the median over
its points; the statistic is the median of the five arms' medians. (The median over all the points pooled is
returned beside it.) Nothing here places an arm, and nothing is tuned to it.

**The verdict is withdrawn; the statistic is read against its nulls** (D218, the follow-up to the gate, item 3:
"judged only as a percentile of its null ... The miss/hit verdict is dropped"). The independent review rotated the
Sun through 360 azimuths on the same field and found the statistic at or under one width in a large share of
the rotations: a sum of five modes lays a crest every kiloparsec or so along any azimuth, so a locus is seldom
far from one wherever the Sun stands. :func:`rotation_null` is that null - the same field, the Sun placed at each
of 360 azimuths a degree apart - and the test beside this file holds a second, the texture seed's (other
realisations of the arms, the Sun where the model puts it). At 1 width the check passes by chance in a large
share of cases: it has no power to tell this representation from the Milky Way's arms; that the representation
cannot show the measured arms stands on the probe (four arms are not one winding), not on this statistic.
"""

from __future__ import annotations

import math

import numpy as np

R0 = 8.15  # kpc, the table's own
# (arm, β from, β to, β_kink, R_kink kpc, ψ_< deg, ψ_> deg): Table 2 as printed, the uncertainties left out.
TABLE2: tuple[tuple[str, float, float, float, float, float, float], ...] = (
    ("3-kpc(N)", 15.0, 18.0, 15.0, 3.52, -4.2, -4.2),
    ("Norma", 5.0, 54.0, 18.0, 4.46, -1.0, 19.5),
    ("Sct-Cen", 0.0, 104.0, 23.0, 4.91, 14.1, 12.1),
    ("Sgr-Car", 2.0, 97.0, 24.0, 6.04, 17.1, 1.0),
    ("Local", -8.0, 34.0, 9.0, 8.26, 11.4, 11.4),
    ("Perseus", -23.0, 115.0, 40.0, 8.87, 10.3, 8.7),
    ("Outer", -16.0, 71.0, 18.0, 12.24, 3.0, 9.4),
)
# The five arms of the check, each the rows whose loci are counted as its own.
ARMS: dict[str, tuple[str, ...]] = {
    "Norma-Outer": ("Norma", "Outer"), "Sct-Cen": ("Sct-Cen",), "Sgr-Car": ("Sgr-Car",), "Perseus": ("Perseus",),
    "Local": ("Local",),
}
RADIAL_STEP = 0.005  # kpc: the samples a crest is found on
RADIAL_RANGE = (0.5, 20.0)  # kpc


def width_kpc(R: np.ndarray) -> np.ndarray:
    """The measured arm width at radius R, kpc: w(R) = 336 + 36 (R − 8.15) pc."""
    return (336.0 + 36.0 * (np.asarray(R, dtype=float) - R0)) / 1000.0


def locus(row: tuple[str, float, float, float, float, float, float]) -> tuple[np.ndarray, np.ndarray]:
    """(β in degrees, R in kpc) along one row's arm, every degree over its β range."""
    _, lo, hi, kink, r_kink, below, above = row
    beta = np.arange(lo, hi + 0.5, 1.0)
    psi = np.where(beta <= kink, below, above)
    return beta, r_kink * np.exp(-np.radians(beta - kink) * np.tan(np.radians(psi)))


def nearest_crest(pattern, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """The radial distance, kpc, from each point (R, φ) to the nearest crest of ``pattern``'s contrast along the
    point's own azimuth: local maxima in R of ``pattern.contrast_at`` on samples :data:`RADIAL_STEP` apart."""
    r = np.arange(RADIAL_RANGE[0], RADIAL_RANGE[1] + 0.5 * RADIAL_STEP, RADIAL_STEP)
    out = np.empty(R.size)
    for k in range(R.size):
        v = np.asarray(pattern.contrast_at(r, np.full(r.size, phi[k])))
        crest = np.flatnonzero((v[1:-1] > v[:-2]) & (v[1:-1] >= v[2:])) + 1
        out[k] = float(np.abs(r[crest] - R[k]).min()) if crest.size else math.inf
    return out


def check(pattern, sun_azimuth: float, sense: float) -> tuple[dict[str, float], float, float]:
    """(each arm's median distance in widths, the median of the five, the median over all points pooled).

    ``sun_azimuth`` is the model's published one and ``sense`` the disc's sense of rotation in φ: a locus point at
    β stands at φ = φ_sun + sense · β."""
    rows = {row[0]: row for row in TABLE2}
    per_arm, pooled = {}, []
    for arm, names in ARMS.items():
        parts = []
        for name in names:
            beta, R = locus(rows[name])
            parts.append(nearest_crest(pattern, R, sun_azimuth + sense * np.radians(beta)) / width_kpc(R))
        distances = np.concatenate(parts)
        per_arm[arm] = float(np.median(distances))
        pooled.append(distances)
    return per_arm, float(np.median(list(per_arm.values()))), float(np.median(np.concatenate(pooled)))


ROTATIONS = 360  # the Sun-rotation null's azimuths, a degree apart: the loci are sampled every degree, so every
# rotation reads the same 360 azimuths of the field


def crests(pattern, phi: np.ndarray) -> list[np.ndarray]:
    """The radii, kpc, of the crests of ``pattern``'s contrast along each azimuth of ``phi``: :func:`nearest_crest`'s
    own definition and samples (local maxima in R, :data:`RADIAL_STEP` apart), every azimuth at once."""
    r = np.arange(RADIAL_RANGE[0], RADIAL_RANGE[1] + 0.5 * RADIAL_STEP, RADIAL_STEP)
    v = np.asarray(pattern.contrast_at(r[:, None], np.asarray(phi, dtype=float)[None, :]))
    peak = (v[1:-1] > v[:-2]) & (v[1:-1] >= v[2:])
    return [r[1:-1][peak[:, j]] for j in range(v.shape[1])]


def rotation_null(pattern, sun_azimuth: float, sense: float) -> np.ndarray:
    """The statistic of :func:`check` with the Sun placed at each of :data:`ROTATIONS` azimuths round the same
    field: entry k is the median over the five arms with the Sun at φ_sun + sense · k°, so entry 0 is the Sun
    where the model puts it (:func:`check`'s own median, to the rounding of an azimuth). The field is not
    touched: only where the measured loci are laid on it. A locus point at β then stands at
    φ_sun + sense · (β + k)°, one of the 360 azimuths whose crests are found once."""
    rows = {row[0]: row for row in TABLE2}
    lines = crests(pattern, sun_azimuth + sense * np.radians(np.arange(ROTATIONS)))
    loci = {arm: [locus(rows[name]) for name in names] for arm, names in ARMS.items()}
    out = np.empty(ROTATIONS)
    for k in range(ROTATIONS):
        medians = []
        for parts in loci.values():
            distances = []
            for beta, R in parts:
                at = np.mod(np.rint(beta).astype(np.int64) + k, ROTATIONS)
                near = np.array([np.abs(lines[j] - radius).min() if lines[j].size else math.inf for j, radius in zip(at, R)])
                distances.append(near / width_kpc(R))
            medians.append(float(np.median(np.concatenate(distances))))
        out[k] = float(np.median(medians))
    return out
