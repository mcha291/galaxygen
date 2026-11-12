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

from galaxy import templates
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
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


# --- the pin (S99 ruling 4): the template's amplitude replaces the draw, the draw keeps its stream -------------------

MW_PATTERN = ("bar_contrast", "bar_mass_share", "pitch_angle", "pitch_angle_drawn", "arm_contrast", "bar_corotation_radius",
              "bar_pattern_speed", "arm_saturation", "arm_power_budget", "pattern_density_contrast")
# The draw on pattern_seed 0 (the registry's) and on 4414 (NGC 4414's, its bar pin taken off), as the stage drew them
# before the pin existed [tests/layer_reference_s93.json, bar_contrast, recorded at S93].
DRAWN_DEFAULT, DRAWN_4414 = 0.28926359920045497, 0.32104666953110067


def unpinned(name: str, *off: str) -> dict:
    """A template's inputs with the named pins taken off."""
    return {k: v for k, v in templates.overrides(templates.TEMPLATES[name]).items() if k not in off}


def test_the_pin_replaces_the_draw_and_every_other_galaxy_keeps_it_bit_for_bit(prod):
    """The pin is ``pitch_angle``'s mechanism (S59, D218 item 6), copied: declared as a numeric pin held to the range
    of the draw it replaces, read by the stage with ``.get`` from a template's inputs alone, and the draw still made on
    its stream - so a galaxy no template pins draws the number it drew, bit for bit, and the template's other seeded
    numbers (the drawn pitch, the arms' amplitude, the fast-bar ratio) are the bits they were."""
    model = prod[0].get(DEFAULT_MODEL)
    bare = run(model, only=MW_PATTERN, layer=False)
    assert float(bare.fields["bar_contrast"]) == DRAWN_DEFAULT
    ngc = run(model, unpinned("ngc_4414", "bar_present"), only=MW_PATTERN, layer=False)
    assert ngc.fields["bar_present"] == "yes" and float(ngc.fields["bar_contrast"]) == DRAWN_4414
    drawn = run(model, unpinned("milky_way", "bar_contrast"), only=MW_PATTERN, layer=False)
    pinned = run(model, templates.resolve(templates.MILKY_WAY), only=MW_PATTERN, layer=False)
    assert float(drawn.fields["bar_contrast"]) == DRAWN_DEFAULT
    assert float(pinned.fields["bar_contrast"]) == templates.pinned(templates.MILKY_WAY)["bar_contrast"]
    for name in ("pitch_angle", "pitch_angle_drawn", "arm_contrast", "bar_corotation_radius", "bar_pattern_speed"):
        assert float(pinned.fields[name]) == float(drawn.fields[name]), name
    # refused outside the draw's range, by a run
    with pytest.raises(Exception, match="bar_contrast"):
        run(model, {**unpinned("milky_way"), "bar_contrast": 0.95}, only=("bar_contrast",), layer=False)


def test_pinned_at_the_drawn_value_nothing_moves(prod):
    """S99 step 2: the template with its amplitude pinned to the value the draw gives is the template with the draw,
    bit for bit, on every published field of the whole pipeline, the layer on."""
    model = prod[0].get(DEFAULT_MODEL)
    drawn = run(model, unpinned("milky_way", "bar_contrast"))
    again = run(model, {**unpinned("milky_way", "bar_contrast"), "bar_contrast": DRAWN_DEFAULT})
    assert set(drawn.fields) == set(again.fields) and len(drawn.fields) > 300
    differ = [n for n, v in drawn.fields.items() if not same(v, again.fields[n])]
    assert differ == []


def same(a, b) -> bool:
    """Bit for bit: arrays by dtype, shape and bytes; scalars by value, NaN equal to NaN."""
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a, b = np.asarray(a), np.asarray(b)
        return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (math.isnan(a) and math.isnan(b))
    return a == b


# --- the value (S99 ruling 5): derived, then held to the source's own error -----------------------------------------


def test_the_milky_way_template_holds_the_galaxy_s_non_axisymmetric_mass(prod):
    """**Judged** (the source's error, not ours): the template's measure inside Portail et al. 2017's 0.46 +/- 0.03 x
    10^10 Msun, the bulge cut their own ellipse. The amplitude is ``tools/derive_bar_contrast.py``'s root, 0.686196,
    stored to four figures; the measure is linear in it, (0.080 + 0.554 B) x 10^10 over the draw's whole range 0-0.9
    (S99's scan: 0.0802 at 0, 0.5783 at 0.9 - the 0.080 at B = 0 is the arm pieces' two-fold part inside 5.3 kpc).

    **Recorded as measured beside it, never judged** (S99, the template at 0.6862, the layer on; before the pin, at the
    draw's 0.2893, in brackets): the named alternative cut R >= 2 kpc 0.4485 (0.2354) x 10^10; no cut 0.7171 (0.3486);
    Sigma along the major axis over the minor at 2 kpc, the bulge in, 3.166 (1.595) - the paper's "a factor of about
    4"; the disc alone 3.738 (1.688); the axis profiles cross at 6.954 kpc (6.954: beyond the body) against the paper's
    6.3; the residual over the maximum axisymmetric disc of the same region 0.328 (0.144) against "slightly less than
    half"."""
    pinned = templates.pinned(templates.MILKY_WAY)["bar_contrast"]
    assert pinned == 0.6862 == float(f"{pinned:.4g}")
    model = prod[0].get(DEFAULT_MODEL)
    out = run(model, templates.resolve(templates.MILKY_WAY), only=bm.READS)
    assert float(out.fields["bar_contrast"]) == pinned
    m = bm.measure(out)
    assert abs(m["mass"] - bm.PORTAIL_NON_AXISYMMETRIC_MASS) <= bm.PORTAIL_NON_AXISYMMETRIC_ERROR  # JUDGED
    assert m["mass"] == pytest.approx(0.46000e10, abs=0.00005e10)  # as measured: 0.460002
    assert (m["mass_circle"], m["mass_no_cut"]) == pytest.approx((0.44854e10, 0.71707e10), abs=0.00005e10)
    assert (m["axis_ratio_2kpc"], m["axis_ratio_2kpc_disc"], m["crossing"], m["disc_share"]) == pytest.approx(
        (3.1661, 3.7376, 6.9538, 0.32758), abs=1e-4)
    # with the layer off the face-on disc is round every ring (the contrast's neutral 1): nothing to measure
    off = bm.measure(run(model, templates.resolve(templates.MILKY_WAY), only=bm.READS, layer=False))
    assert abs(off["mass"]) < 1.0 and off["axis_ratio_2kpc"] == 1.0


@pytest.mark.skipif(not __import__("os").environ.get("GALAXYGEN_REDERIVE"), reason="the root-find re-run (about 3 min) is opt-in: GALAXYGEN_REDERIVE=1")
def test_the_committed_amplitude_is_where_the_root_find_lands():
    """tools/derive_bar_contrast.py from its bracket: monotone over the scan, the root to four figures the pin."""
    import derive_bar_contrast as tool

    root, seen = tool.derive(say=lambda *_: None)
    assert tool.four_figures(root) == templates.pinned(templates.MILKY_WAY)["bar_contrast"]
    assert root == pytest.approx(0.686196, abs=2e-6)
