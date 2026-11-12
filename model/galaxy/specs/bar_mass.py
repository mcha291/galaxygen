"""bar_mass: a bar's non-axisymmetric mass on a face-on surface density, as Portail et al. 2017 measure the Milky
Way's (S99, debt #146; DECISIONS.md D268 ruling 8 and the gate's rulings 1-2 of S99).

An instrument (rule B1: built and tested on hand cases before the template's number is read through it). It reads a
face-on surface density Sigma(R, phi) on a polar grid and the bar's angle, and nothing of how the density was made.

**The quantity** (Portail, Gerhard, Wegg & Ness 2017, arXiv:1608.07954v3, Sect. 9.1 (ii), the PDF read
at S99 by the session's reader): "We first define a maximum axisymmetric model using the minor axis profile
and remove this maximum axisymmetric model from the original surface density map. By integrating the residuals for
radii inside 5.3 kpc and outside the bulge, we find a non-axisymmetric long bar mass of Mnon-axi = 0.46 +/- 0.03 x
10^10 Msun." So:

    M = integral of [Sigma(R, phi) - Sigma_minor(R)] dA over R < 5.3 kpc (cylindrical), outside the bulge,

**signed** (the page says "the residuals", not their positive part). ``Sigma_minor(R)`` is Sigma along the bar's
in-plane minor axis, both ends averaged, each end read as a sector of :data:`MINOR_AXIS_HALF_WINDOW_DEG` either side
of the axis (S98's measurer's reading, three one-degree cells an end; the page does not say how wide the axis is
read: ``[inferred]``). An axisymmetric component - the bulge - cancels from M exactly.

**The bulge's cut** (the gate's ruling 2, chosen before the template's number was read): the paper's own printed
bulge region, "the interior of an ellipse reaching 2.2 kpc along the bar major axis and 1.4 kpc along the
intermediate axis" (its Sect. 3) - :data:`BULGE_REGION`. The other reading, R >= 2 kpc (S98's, from Sect. 9.1's "the
edge of the bulge ... at 2 kpc"), is :data:`BULGE_CIRCLE`, measured beside and never used to choose.

**The region's area** is integrated exactly in R, at the 5.3 kpc edge and at the cut's boundary (read at
``SUBCELLS`` azimuths a cell), so the measure does not move by a ring's width with the grid. Sigma is a cell's value
over the whole cell.

Units: R in kpc, Sigma in Msun/pc^2, M in Msun. Read-only on a run: :func:`measure` takes a finished run's fields.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

# The target and its window: Portail et al. 2017, Sect. 9.1 (ii) and Table 2, "Non-axisymmetric long bar 0.46 +/- 0.03"
# (x 10^10 Msun; the error the variation models' systematic half-range) [verified: Portail, Gerhard, Wegg & Ness 2017,
# arXiv:1608.07954v3, Sect. 9.1 (ii) and Table 2, the PDF read at S99].
PORTAIL_NON_AXISYMMETRIC_MASS = 0.46e10
PORTAIL_NON_AXISYMMETRIC_ERROR = 0.03e10
# "for radii inside 5.3 kpc": a cylindrical radius in the face-on map (the bar "extends to 5.3 kpc from the centre",
# its Fig. 20) [verified: the same page].
PORTAIL_OUTER_RADIUS = 5.3
# The other numbers of Sect. 9.1 a pinned template is checked against, never fitted to: the major-to-minor axis
# surface density "a factor of about 4" at 2 kpc; "Both profiles cross at 6.3 kpc"; the bar outside the bulge "slightly
# less than half the mass of the disk in the same radial range" [verified: the same page].
PORTAIL_AXIS_RATIO_RADIUS = 2.0
PORTAIL_AXIS_RATIO = 4.0
PORTAIL_CROSSING = 6.3

# The sector an axis is read over, either side of it, in degrees [inferred]: S98's measurer's three one-degree cells
# an end (s98_M_bar.py); the paper does not say.
MINOR_AXIS_HALF_WINDOW_DEG = 1.5
# Azimuths a cell the cut's boundary is read at (the area is exact in R).
SUBCELLS = 16


@dataclass(frozen=True)
class Ellipse:
    """A bulge region in the bar's frame: the interior of an ellipse of semi-axes ``major`` along the bar and ``minor``
    along its in-plane minor axis, kpc."""

    major: float
    minor: float

    def boundary(self, psi: np.ndarray) -> np.ndarray:
        """kpc: the ellipse's radius at angle ``psi`` from the bar's major axis."""
        c, s = np.cos(psi), np.sin(psi)
        return 1.0 / np.sqrt((c / self.major) ** 2 + (s / self.minor) ** 2)


@dataclass(frozen=True)
class Circle:
    """A bulge region as a circle, R < ``radius`` kpc."""

    radius: float

    def boundary(self, psi: np.ndarray) -> np.ndarray:
        """kpc: the circle's radius, at every angle."""
        return np.full(np.shape(psi), float(self.radius))


# The gate's ruling 2: Portail et al. 2017's own bulge region, Sect. 3, "the interior of an ellipse reaching 2.2 kpc
# along the bar major axis and 1.4 kpc along the intermediate axis" [verified: the same paper, Sect. 3; the face-on footprint of its Table 2 box, +/-2.2 x +/-1.4 kpc].
BULGE_REGION = Ellipse(2.2, 1.4)
# The named alternative, measured beside and never used to choose: R >= 2 kpc (S98's reading of Sect. 9.1).
BULGE_CIRCLE = Circle(2.0)


def axis_profile(sigma: np.ndarray, phi: np.ndarray, direction: float, half_window_deg: float = MINOR_AXIS_HALF_WINDOW_DEG) -> np.ndarray:
    """(R,): Sigma along the axis at azimuth ``direction`` (rad), both ends (``direction`` and ``direction + pi``)
    averaged, each end the mean of the cells whose centres lie within ``half_window_deg`` of it - the nearest cell where
    the window holds none."""
    sigma = np.asarray(sigma, dtype=float)
    phi = np.asarray(phi, dtype=float)
    cols: list[int] = []
    for end in (direction, direction + math.pi):
        off = np.abs((phi - end + math.pi) % (2.0 * math.pi) - math.pi)
        near = np.flatnonzero(off <= math.radians(half_window_deg) + 1e-12)
        cols.extend(near.tolist() if near.size else [int(np.argmin(off))])
    return sigma[:, cols].mean(axis=1)


def region_area(R_edges: np.ndarray, phi_edges: np.ndarray, angle: float, outer: float, cut: Any) -> np.ndarray:
    """(R, phi) pc^2: each cell's area inside R < ``outer`` and outside the bulge region ``cut`` (in the bar's frame,
    the bar along ``angle``; ``cut`` None for no cut). Both regions are bounded by a radius at each azimuth, so the
    area is exact in R - each cell's ring taken from max(its inner edge, the cut's boundary) to min(its outer edge,
    ``outer``) - and the cut's boundary is read at ``SUBCELLS`` azimuths a cell (the midpoint rule; exact for a
    circle)."""
    R_edges, phi_edges = np.asarray(R_edges, dtype=float), np.asarray(phi_edges, dtype=float)
    lo, hi = R_edges[:-1, None, None], np.minimum(R_edges[1:], outer)[:, None, None]
    dphi = np.diff(phi_edges)
    u = (np.arange(SUBCELLS) + 0.5) / SUBCELLS
    psi = phi_edges[:-1, None] + dphi[:, None] * u[None, :] - angle          # (phi, k)
    edge = np.zeros(psi.shape) if cut is None else cut.boundary(psi)         # (phi, k) kpc
    start = np.minimum(np.maximum(lo, edge[None]), hi)                       # (R, phi, k)
    ring = np.where(hi > start, 0.5 * (hi * hi - start * start), 0.0)
    return ring.mean(axis=2) * dphi[None, :] * 1e6


def non_axisymmetric_mass(R_edges: np.ndarray, phi_edges: np.ndarray, sigma: np.ndarray, angle: float,
                          outer: float = PORTAIL_OUTER_RADIUS, cut: Any = BULGE_REGION,
                          half_window_deg: float = MINOR_AXIS_HALF_WINDOW_DEG) -> float:
    """Msun: the integral of Sigma - Sigma_minor(R), signed, over R < ``outer`` outside ``cut`` (Portail et al. 2017,
    Sect. 9.1 (ii)); ``angle`` the bar's major axis (rad), so its minor axis is ``angle + pi/2``."""
    phi = 0.5 * (np.asarray(phi_edges[1:]) + np.asarray(phi_edges[:-1]))
    minor = axis_profile(sigma, phi, angle + 0.5 * math.pi, half_window_deg)
    area = region_area(R_edges, phi_edges, angle, outer, cut)
    return float(((np.asarray(sigma, dtype=float) - minor[:, None]) * area).sum())


def axisymmetric_mass(R_edges: np.ndarray, phi_edges: np.ndarray, sigma: np.ndarray, angle: float,
                      outer: float = PORTAIL_OUTER_RADIUS, cut: Any = BULGE_REGION,
                      half_window_deg: float = MINOR_AXIS_HALF_WINDOW_DEG) -> float:
    """Msun: the maximum axisymmetric model's mass over the same region - Sigma_minor(R) integrated - the disc the
    paper's "slightly less than half the mass of the disk in the same radial range" sets the bar against."""
    phi = 0.5 * (np.asarray(phi_edges[1:]) + np.asarray(phi_edges[:-1]))
    minor = axis_profile(sigma, phi, angle + 0.5 * math.pi, half_window_deg)
    return float((minor[:, None] * region_area(R_edges, phi_edges, angle, outer, cut)).sum())


def axis_ratio(R: np.ndarray, phi: np.ndarray, sigma: np.ndarray, angle: float, at: float,
               half_window_deg: float = MINOR_AXIS_HALF_WINDOW_DEG) -> float:
    """Sigma along the major axis over Sigma along the minor axis at radius ``at`` (linear in R between rings)."""
    major = axis_profile(sigma, phi, angle, half_window_deg)
    minor = axis_profile(sigma, phi, angle + 0.5 * math.pi, half_window_deg)
    return float(np.interp(at, R, major) / np.interp(at, R, minor))


def crossing(R: np.ndarray, phi: np.ndarray, sigma: np.ndarray, angle: float, lo: float = 0.5, hi: float = 12.0,
             half_window_deg: float = MINOR_AXIS_HALF_WINDOW_DEG) -> float:
    """kpc: the first radius in [lo, hi] at which the major-axis profile falls below the minor-axis one, linear
    between the two rings that bracket it (NaN where it never does)."""
    d = axis_profile(sigma, phi, angle, half_window_deg) - axis_profile(sigma, phi, angle + 0.5 * math.pi, half_window_deg)
    R = np.asarray(R, dtype=float)
    for i in range(R.size - 1):
        if lo <= R[i] < hi and d[i] > 0.0 >= d[i + 1]:
            return float(R[i] + (R[i + 1] - R[i]) * d[i] / (d[i] - d[i + 1]))
    return float("nan")


def m2_angle(R: np.ndarray, phi: np.ndarray, sigma: np.ndarray, lo: float = 1.5, hi: float = 4.0) -> float:
    """rad in [0, pi): the m = 2 phase of Sigma over lo < R < hi, each ring weighted by its area - where the density's
    two-fold part points (S98's measurer's estimate of the bar's major axis; a check on the model's angle)."""
    R, phi = np.asarray(R, dtype=float), np.asarray(phi, dtype=float)
    sel = (R > lo) & (R < hi)
    z = (np.asarray(sigma, dtype=float)[sel] * np.exp(-2j * phi)[None, :]).sum(axis=1)
    return float((-np.angle((z * R[sel]).sum()) / 2.0) % math.pi)


def hernquist_projected(R: np.ndarray, mass: float, a: float) -> np.ndarray:
    """Msun/pc^2: a Hernquist sphere's projected surface density, R and a in kpc, Sigma(s) = M / (2 pi a^2 (1 - s^2)^2)
    [(2 + s^2) X(s) - 3], s = R/a, X = arcsech(s)/sqrt(1 - s^2) inside s = 1 and arcsec(s)/sqrt(s^2 - 1) outside,
    2M/(15 pi a^2) at s = 1 [recall: Hernquist 1990, ApJ 356, 359, eqs. 32-34; held against its own line-of-sight
    quadrature in tests/test_bar.py::test_the_hand_hernquist_projection_is_the_density_s_line_of_sight_integral].
    The model's bulge (``bulge_stellar_mass``, ``bulge_scale_radius``), axisymmetric: it cancels from the mass and
    enters only the axis ratio."""
    s = np.maximum(np.asarray(R, dtype=float) / a, 1e-9)
    x = np.ones_like(s)
    inner, outer = s < 1.0, s > 1.0
    x[inner] = np.arccosh(1.0 / s[inner]) / np.sqrt(1.0 - s[inner] ** 2)
    x[outer] = np.arccos(1.0 / s[outer]) / np.sqrt(s[outer] ** 2 - 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma = mass / (2.0 * math.pi * a * a * (1.0 - s * s) ** 2) * ((2.0 + s * s) * x - 3.0)
    sigma = np.where(inner | outer, sigma, 2.0 * mass / (15.0 * math.pi * a * a))
    return sigma / 1e6


# What :func:`measure` reads of a run (rule D4: a run restricted to these fields).
READS: tuple[str, ...] = (
    "stellar_surface_density", "pattern_density_contrast", "sfr_modulation", "sfr_surface_density_history",
    "bulge_stellar_mass", "bulge_scale_radius", "bar_half_length", "pitch_angle", "bar_contrast",
)


def stellar_density(out: Any) -> np.ndarray:
    """(R, phi) Msun/pc^2: the finished model's face-on stellar disc - ``stellar_surface_density`` (stars and
    remnants) placed round each ring as the model places its old stars, by the star sample's rule
    (``bright.part_weights``' old part on the pattern's density contrast, the render's ``stars_old_placement``, S91
    #160), which keeps each ring's mass. With the layer off every placing weight is 1 and the disc axisymmetric."""
    from galaxy.layer import compose
    from galaxy.stages import bright

    f, R = out.fields, out.grid.R
    stars = np.asarray(f["stellar_surface_density"], dtype=float)
    contrast = compose.published(f, "pattern_density_contrast")
    placed = np.ones((R.size, out.grid["phi"].n)) if contrast is None else np.maximum(np.asarray(contrast, dtype=float), 0.0)
    modulation = compose.published(f, "sfr_modulation")
    share = None
    if modulation is not None:
        share = (np.zeros(R.size) if compose.placement_weight(f, "sfr_modulation") is None else
                 bright.row_young_share(f, R, out.grid.t, R, migration=float(out.inputs["migration_efficiency"])))
    old = bright.part_weights(placed, modulation, share)[1]
    return stars[:, None] * old


def bar_angle(out: Any) -> float:
    """rad: the bar's major axis as the pattern stage lays the body (``pattern.bar_terms``' angle)."""
    from galaxy.stages import pattern

    f = out.fields
    return float(pattern.bar_terms(out.grid.R, float(f["pitch_angle"]), float(f["bar_half_length"]))[2])


def measure(out: Any) -> dict[str, float]:
    """The ruling's measure and its recorded companions on a finished run: ``mass`` (the bulge cut the ellipse, the
    gate's ruling 2), ``mass_circle`` (R >= 2 kpc, the named alternative), ``axis_ratio_2kpc`` (Sigma with the bulge,
    major over minor at 2 kpc), ``crossing`` (kpc), ``disc_share`` (the mass over the maximum axisymmetric disc's in
    the same region, the disc without the bulge), ``angle`` and ``m2_angle`` (deg, the model's and the density's)."""
    R, phi = out.grid.R, out.grid.phi
    R_edges, phi_edges = out.grid["R"].edges, out.grid["phi"].edges
    disc = stellar_density(out)
    f = out.fields
    bulge = hernquist_projected(R, float(f["bulge_stellar_mass"]), float(f["bulge_scale_radius"]))
    total = disc + bulge[:, None]
    angle = bar_angle(out)
    mass = non_axisymmetric_mass(R_edges, phi_edges, total, angle)
    return {
        "mass": mass,
        "mass_circle": non_axisymmetric_mass(R_edges, phi_edges, total, angle, cut=BULGE_CIRCLE),
        "mass_no_cut": non_axisymmetric_mass(R_edges, phi_edges, total, angle, cut=None),
        "axis_ratio_2kpc": axis_ratio(R, phi, total, angle, PORTAIL_AXIS_RATIO_RADIUS),
        "axis_ratio_2kpc_disc": axis_ratio(R, phi, disc, angle, PORTAIL_AXIS_RATIO_RADIUS),
        "crossing": crossing(R, phi, total, angle),
        "disc_share": mass / axisymmetric_mass(R_edges, phi_edges, disc, angle),
        "angle": math.degrees(angle) % 180.0,
        "m2_angle": math.degrees(m2_angle(R, phi, disc)),
    }
