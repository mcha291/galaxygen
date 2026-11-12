"""The bar's non-axisymmetric mass, Portail et al. 2017's measure (S99, debt #146; DECISIONS.md D268 ruling 8).

``galaxy.specs.bar_mass`` is an instrument (rule B1), so it is held first on hand cases whose answer is written here
by hand: an axisymmetric disc gives 0 under every cut; a disc of one two-fold cosine, Sigma0 (1 + A cos 2 psi), gives
Sigma0 A (1 + cos 2 psi) above its minor axis, whose integral is Sigma0 A pi R_out^2 with no cut, less Sigma0 A pi
(2^2) for the circle R < 2 kpc, and less 2 Sigma0 A pi a^2 b / (a + b) for the ellipse of semi-axes a along the bar
and b across it (the integral of cos^2 psi over an ellipse is pi a^2 b / (a + b): the boundary r(psi)^2 =
1 / (cos^2/a^2 + sin^2/b^2) integrated against cos^2 psi / 2); the axis ratio of that disc is (1 + A)/(1 - A) and
the profiles cross where A changes sign.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.specs import bar_mass as bm

N_R, N_PHI, R_MAX = 400, 360, 30.0
R_EDGES = np.linspace(0.0, R_MAX, N_R + 1)
PHI_EDGES = np.linspace(0.0, 2.0 * math.pi, N_PHI + 1)
R = 0.5 * (R_EDGES[1:] + R_EDGES[:-1])
PHI = 0.5 * (PHI_EDGES[1:] + PHI_EDGES[:-1])
THETA = math.radians(22.5)  # the bar's angle: its minor axis, 112.5 deg, on a cell's centre
KPC2 = 1e6  # pc^2 a kpc^2


def cosine_disc(sigma0: float, amplitude) -> np.ndarray:
    a = np.broadcast_to(np.asarray(amplitude, dtype=float), R.shape)
    return sigma0 * (1.0 + a[:, None] * np.cos(2.0 * (PHI[None, :] - THETA)))


def test_the_constants_are_the_rulings():
    """The target, its window and the region as the gate ruled them (S99 rulings 1-2; Portail et al. 2017)."""
    assert (bm.PORTAIL_NON_AXISYMMETRIC_MASS, bm.PORTAIL_NON_AXISYMMETRIC_ERROR, bm.PORTAIL_OUTER_RADIUS) == (0.46e10, 0.03e10, 5.3)
    assert (bm.BULGE_REGION.major, bm.BULGE_REGION.minor, bm.BULGE_CIRCLE.radius) == (2.2, 1.4, 2.0)
    assert (bm.PORTAIL_AXIS_RATIO_RADIUS, bm.PORTAIL_AXIS_RATIO, bm.PORTAIL_CROSSING) == (2.0, 4.0, 6.3)


def test_the_region_s_area_by_hand():
    """No cut: pi 5.3^2 exactly (a ring is taken to 5.3 kpc); the circle's pi 2^2 taken out exactly; the ellipse's
    pi a b to the midpoint rule's reading of its boundary."""
    full = bm.region_area(R_EDGES, PHI_EDGES, THETA, 5.3, None).sum() / KPC2
    assert full == pytest.approx(math.pi * 5.3**2, rel=1e-12)
    circle = bm.region_area(R_EDGES, PHI_EDGES, THETA, 5.3, bm.BULGE_CIRCLE).sum() / KPC2
    assert circle == pytest.approx(math.pi * (5.3**2 - 2.0**2), rel=1e-12)
    ellipse = bm.region_area(R_EDGES, PHI_EDGES, THETA, 5.3, bm.BULGE_REGION).sum() / KPC2
    assert ellipse == pytest.approx(math.pi * (5.3**2 - 2.2 * 1.4), rel=1e-9)
    # on a coarse grid too: the area does not move with the rings' width
    coarse = bm.region_area(np.linspace(0.0, 30.0, 41), np.linspace(0.0, 2.0 * math.pi, 37), THETA, 5.3, bm.BULGE_REGION)
    assert coarse.sum() / KPC2 == pytest.approx(math.pi * (5.3**2 - 2.2 * 1.4), rel=1e-6)


@pytest.mark.parametrize("cut", [None, bm.BULGE_REGION, bm.BULGE_CIRCLE])
def test_an_axisymmetric_disc_has_no_non_axisymmetric_mass(cut):
    """An exponential disc plus a bulge-like cusp, round every ring: 0 to rounding, under every cut and any angle."""
    sigma = np.broadcast_to((800.0 * np.exp(-R / 2.6) + 50.0 / (R + 0.1))[:, None], (N_R, N_PHI))
    for angle in (THETA, 1.0, 2.9):
        assert abs(bm.non_axisymmetric_mass(R_EDGES, PHI_EDGES, sigma, angle, cut=cut)) < 1e-3  # Msun, of ~1e10


def test_one_cosine_by_hand():
    """Sigma0 (1 + A cos 2 psi): the residual Sigma0 A (1 + cos 2 psi) integrated by hand (the module's docstring)."""
    s0, A = 300.0, 0.4
    sigma = cosine_disc(s0, A)
    a, b = bm.BULGE_REGION.major, bm.BULGE_REGION.minor
    hand = {
        None: s0 * A * math.pi * 5.3**2,
        bm.BULGE_CIRCLE: s0 * A * math.pi * (5.3**2 - 2.0**2),
        bm.BULGE_REGION: s0 * A * (math.pi * 5.3**2 - 2.0 * math.pi * a * a * b / (a + b)),
    }
    for cut, value in hand.items():
        got = bm.non_axisymmetric_mass(R_EDGES, PHI_EDGES, sigma, THETA, cut=cut, half_window_deg=0.0)
        assert got / KPC2 == pytest.approx(value, rel=1e-3), cut
    # the default window (+/- 1.5 deg, three cells an end) reads the minor axis a little above its value: the mass
    # falls by A (1 - mean cos 2 delta) Sigma0 x area - under 1e-3 of it
    wide = bm.non_axisymmetric_mass(R_EDGES, PHI_EDGES, sigma, THETA)
    assert wide / KPC2 == pytest.approx(hand[bm.BULGE_REGION], rel=2e-3)
    # an axisymmetric part added cancels (the bulge): the same number
    bulge = bm.hernquist_projected(R, 8e9, 0.36)
    assert bm.non_axisymmetric_mass(R_EDGES, PHI_EDGES, sigma + bulge[:, None], THETA) == pytest.approx(wide, rel=1e-12)
    # the disc's share: the residual over the maximum axisymmetric disc Sigma0 (1 - A) over the same region
    disc = bm.axisymmetric_mass(R_EDGES, PHI_EDGES, sigma, THETA, half_window_deg=0.0) / KPC2
    assert disc == pytest.approx(s0 * (1.0 - A) * math.pi * (5.3**2 - a * b), rel=2e-4)


def test_the_axis_ratio_the_crossing_and_the_angle_by_hand():
    """(1 + A)/(1 - A) at 2 kpc; a cosine whose A = 0.05 (R0 - R) changes sign at R0 = 6.3 kpc crosses there; the
    m = 2 phase is the bar's angle."""
    s0 = 100.0
    sigma = cosine_disc(s0, 0.5)
    assert bm.axis_ratio(R, PHI, sigma, THETA, 2.0, half_window_deg=0.0) == pytest.approx(1.5 / 0.5, rel=1e-12)
    sloped = cosine_disc(s0, 0.05 * (6.3 - R))
    assert bm.crossing(R, PHI, sloped, THETA, half_window_deg=0.0) == pytest.approx(6.3, abs=1e-9)
    assert math.isnan(bm.crossing(R, PHI, cosine_disc(s0, 0.5), THETA))
    assert bm.m2_angle(R, PHI, sigma) == pytest.approx(THETA, abs=1e-9)


def test_the_bulge_s_projection_is_its_line_of_sight_integral():
    """The Hernquist projection against the density M a / (2 pi r (r + a)^3) integrated along the line of sight."""
    mass, a = 1.0e10, 0.36
    for radius in (0.05, 0.36, 1.0, 3.0):
        z = np.concatenate([[0.0], np.geomspace(1e-6, 400.0, 200001)])
        r = np.sqrt(radius * radius + z * z)
        rho = mass * a / (2.0 * math.pi * r * (r + a) ** 3)
        column = 2.0 * float((0.5 * (rho[1:] + rho[:-1]) * np.diff(z)).sum()) / 1e6
        assert float(bm.hernquist_projected(np.array([radius]), mass, a)[0]) == pytest.approx(column, rel=1e-4)
