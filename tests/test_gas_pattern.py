"""The gas's own arm pattern: since S57 the gas's steady response to the stellar arms (BUILD_III Phase P2; D216).

From S51 to S56 this file held a ridge to its form: a von Mises of a measured width, its amplitude solved from a
measured ratio of means, since S56 laid round each ring by rank. Gate G2 of S57 retired the ridge for a law -
``ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(mχ − θ_m)`` on every ring, solved by ``gas_response`` (the instrument;
``tests/test_gas_response.py`` certifies it) - and this file holds the model to that law and to nothing of the
ridge. What is tested, in the gate's order:

- **the gate**, on every ring of both templates and of the 240 seeded galaxies the suite draws: the discrete
  residual as gate G3 words it (under 1e-10 or under the cell's rounding floor, the returned profile re-logged
  too), the ring's mean on the solver's cells with no division, positivity and the bound w_bar (1 − B), the
  published field's ring mean, Newton's counts, finiteness, the sector means, the saturation's bound;
- **the law re-derived by hand** on three rings from the published fields, with a dense Newton and a spectral
  derivative written here, and the published cell means with the bar's composition; and again on the suite's most
  saturated seed (gate G3 item 3: the forcing's amplitude carries the saturation);
- **the published field is the law's exact mean over each grid cell's extent in azimuth, at the ring's own
  radius** (G3 item 4; not over R: points between rings are blended in R): ring means 1 to 1e-13 on any φ grid
  with nothing divided, and its error against the exact solution's cell means with the h² law;
- **the two interpolation errors** of the point function, in χ and in R, pinned as measured (G3 item 5);
- **the predictions** of D216, read before they are judged (B4), with the as-built numbers;
- **the disclosed check** (not an acceptance row; invariant I3 stands): the ratio of means in the source's mask
  against PHANGS's 2.73 within 1.37-5.79, and the crest's width against 0.17 - layer on, both templates.

**Read on 2026-10-04, the Milky Way template at its default seeds** (165 rings carry a mode; `ngc_4414`: 133):
Newton 8 steps at most and one halving (9 and none); the residual 5.3e-12 (9.0e-12), the rounding floor 1.3e-11
(1.9e-11) - the absolute tolerance governs; the ring mean on the solver's cells off 1 by 8.8e-14 (9.6e-14); the
published field's ring mean off 1 by 7.1e-14 (9.7e-14) on the default grid and 1e-14 on a 36-, 108- or 500-cell
one, with nothing divided; s between 4.5e-11 and 5.70 (1.8e-17 and 4.73), both extremes deep inside the bar where
the arm's weight is under 1 %; the published field between 0.0199 and 3.092 (0.0143 and 2.688), its margin over
w_bar (1 − B) 2.0e-5 (7.7e-6). At R₀ the crest is 2.74 and the trough 0.025 (S56's ridge: 3.06 and 0.534): the
gas between the arms is nearly emptied where the modes' forcing sums past 1, as the gate predicted.

**What the first build found, and what gate G3 ruled** (D216). (i) Tightly wound galaxies raised: at a drawn
pitch under about 2.7 degrees ε is of order 1 and the forcing's sum 60-80, the residual's rounding floor passes
the absolute 1e-10, and two of the 240 seeded galaxies (``ngc_4414`` at pattern seed 33) - 20 of 600 over a sweep
of 300 pattern seeds a template - were solved and still raised. Since G3 a cell is converged under 1e-10 **or
under its rounding floor**; all 240 and all 600 converge, and the regime is published as the law gives it.
**One of the 238 that converged before moved its bits** (``ngc_4414`` at pattern seed 1, texture seed 1: one ring
at 0.49 kpc stops at 8 Newton steps where the absolute tolerance took 10; the profile moves by 1.8e-15 of itself
and the published field not at all) and three of the sweep's 580: reported to the gate, which had asked for none
and accepted the four at its follow-up - each by at most 2.0e-15 of the profile, the old acceptance having been
a chance landing inside the floor (the bound is asserted on the suite's galaxy against the first build's rule).
(ii) The interpolation in χ reads 3.5e-4 outside the bar's reach and 1.2e-3 inside it (3.0e-4 of the point
field), not the 2.0e-4 of the instrument's two hard rings: 1440 cells stand, pinned per quantity. (iii) The
offset is zero for a lone mode, exactly; with several modes, within one solver cell (0.25 degrees) on the Milky
Way template and up to about a degree on ``ngc_4414`` - the mode-by-mode weighting, measured, not ruled, and of
no one sign; no offset is put in and none is published. (iv) The published field is cell means in azimuth, not
centre samples: ring totals hold on every grid. (v) The solver's shortcut in evaluating the criterion (the
cells' floors only where they can decide a ring) is held to the rule as written, bit for bit.

**Since S58 (BUILD_III Phase P3; D217) the galaxies this file reads are other galaxies, and its pins are re-read on
them** - each with ``# S58 (D217): was <old>`` beside it. Three things moved them. (a) *The two-armed mode's phase
is the bar's in a barred galaxy* (θ₂ = 0, item 9): on the Milky Way template every ring that carries the two-armed
mode - inside about 6.5 kpc - holds another sum of the same five forcings, so s there is another profile (its range
6.2e-14 to 6.23, where it was 4.5e-11 to 5.70), and from R₀ out it is the ring it was (the crest 2.797, the ratio of
means 2.571). (b) *The bar's term is the lane field* (items 6-8): g = w_arm s + w_bar L, L re-derived by hand in
``tests/test_bar.py``; the published field runs from 0.0184 to 6.66, a lane's crest at 2.06 kpc, and is never under
w_bar min L (to the rounding of a cell's mean). (c) *``ngc_4414`` is pinned unbarred* (items 2-3): no taper and no
lanes, its arm modes untapered to the centre; its response on its own seeds is the one it was - the disclosed
check reads 1.881 and 0.512 as D217 predicted - but its published field is that response alone, innermost rings and
all (4.6e-18 to 4.73), and on other pattern seeds its inner rings saturate. The S57 text above is the record of
that session's gates and is left as read then.

**Since S59 (BUILD_III Phase P4; D218) two more things move this file's pins, each re-read with ``# S59 (D218): was
<old>`` beside it.** (a) *The arms' common winding is laid in seeded segments* (items 1-4): χ = φ − Φ(R), Φ built from
the layer's published segment rows; **geometry only** - the law's ε and f keep the disc's own ``pitch_angle`` - so on
every ring s(χ) is the profile it was, and what is in χ did not move (the solver's residuals, floors and counts, the
extremes of s, the crests' separation, the disclosed check's two measurements, the interpolation errors). What
moved, layer on, is where a ring's profile lies among the grid's cells: the published field's cell means (in the
third or fourth figure where the ring is the response alone), and inside a bar's reach its blend with the lanes,
whose angle did not move (the largest published value 6.68 where it was 6.66; the margin over w_bar min L −1.8e-14
where it was −2.1e-15, a rounding the lanes always carried). This file's hand derivations wind by ``hand_winding``,
from the published rows. (b) *``ngc_4414`` pins its measured pitch, 28.9 degrees* (item 6), layer on and off: ε and f
are both × 0.5121 on every ring of the template (sin 14.33° / sin 28.9°), its response is gentler (the crest 3.16
where it was 4.73; the disclosed check's median ratio 1.406 where it was 1.881, still inside 1.37-5.79 by 0.036,
21 of its 53 rings under; the width 0.550), and **every pattern seed of that template's inputs is at that one
pitch** - so the suite's 120 ``ngc_4414`` galaxies no longer reach the tightly wound regime, and the three of them
that gate G3's record names are read as what they were, with the pitch's pin taken off (``drawn_pitch``).
"""

from __future__ import annotations

import ast
import collections
import functools
import math
import re
from pathlib import Path

import numpy as np
import pytest

import gas_check
from galaxy import templates
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import gas_pattern as gm
from galaxy.stages import gas_response as gr
from galaxy.stages import pattern as pt
from galaxy.stages.gas_pattern import GAS_PATTERN, GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS, GasPattern
from galaxy.stages.pattern import BAR, PATTERN

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
TEMPLATES = ("milky_way", "ngc_4414")
R_SUN = 8.122
G_HAND = 4.30091727e-6  # kpc (km/s)^2 / Msun, written here; the model's constant is held to it
SOUND_SPEED_HAND = 6.0  # km/s, written here; the model's GAS_DISPERSION is held to it
# The disclosed check's two numbers are no constants of the model since gate G3 (item 7): they live in
# tests/gas_check.py with their sources. PHANGS's median mask width, and the measured gas arm's width over its period.
MASK_WIDTH = gas_check.GAS_ARM_MASK_WIDTH
WIDTH_TARGET = gas_check.GAS_ARM_WIDTH
RATIO_TARGET, RATIO_LOW, RATIO_HIGH = 2.73, 1.37, 5.79  # PHANGS's grand designs: the mean and its 16th-84th percentiles
PATTERN_FIELDS = ("gas_density_contrast", "pattern_density_contrast", "gas_arm_contrast", "arm_pattern_speed",
                  "circular_velocity", "arm_saturation", *GAS_PATTERN_READS)
ROUNDING = 2.0**-53  # u: half a unit in the last place of 1
_RUNS: dict[object, object] = {}


def out(model):
    """The default run, once per model per session (the whole pipeline is a few seconds)."""
    if model.name not in _RUNS:
        _RUNS[model.name] = run(model)
    return _RUNS[model.name]


def template_run(prod, template: str):
    """A template's pattern fields alone on the production grid (rule D4), once per session."""
    key = ("template", template)
    if key not in _RUNS:
        _RUNS[key] = run(prod[0].get(DEFAULT_MODEL), templates.overrides(templates.TEMPLATES[template]), only=PATTERN_FIELDS)
    return _RUNS[key]


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def shape_of(model, o) -> GasPattern:
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert gp is not None and not gp.flat
    return gp


def row(o, R: float) -> int:
    return int(np.argmin(np.abs(o.grid.R - R)))


def drawn_pitch(template: str, **more) -> dict:
    """A template's inputs with its pitch as the law draws it: the template's other pins kept, its measured-pitch
    pin taken off (S59, D218 item 6: ``ngc_4414`` pins ``pitch_angle`` at 28.9 degrees, so every pattern seed of
    that template's inputs is at that one pitch since - and the tightly wound galaxies this file read on them
    until S59, pattern seeds 33 and 1 at 1.78 and 2.06 degrees, are this disc with the pin off, the galaxies they
    were). ``more`` overrides, as the suite's seeds do."""
    given = templates.overrides(templates.TEMPLATES[template])
    return {**{k: v for k, v in given.items() if k != "pitch_angle"}, **more}


SEGMENTS_OUTWARD_HAND = 64  # S59 (D218): the winding's rows laid outward from the anchor, first; the rest run inward


def hand_winding(F, R) -> np.ndarray:
    """Φ(R), the arms' common winding, from the **published** numbers with this file's arithmetic and no function of
    the model's (S59, D218 items 1-2). Until S59 it was ln R · cot p. Since then the layer lays segments: a row's
    pitch is ``pitch_angle`` plus its residual; across it ln R advances by its extent times |tan| of that pitch and
    the phase by its extent times the pitch's sign; the first 64 rows run outward from the anchor, the rest inward;
    at the anchor Φ = ln R_A · cot p - the bar's angle, where there is a bar; and Φ is the straight line in ln R
    between the segments' ends. With the layer off there are no rows, and Φ is ln R · cot p as it always was.
    **Geometry only** (item 4): the law's ε and f read ``pitch_angle`` itself, not a segment's pitch."""
    R = np.asarray(R, dtype=float)
    pitch, anchor = float(F["pitch_angle"]), float(F["arm_winding_anchor_radius"])
    extent, residual = np.asarray(F["arm_segment_extent"], dtype=float), np.asarray(F["arm_segment_pitch_residual"], dtype=float)
    cot = 1.0 / math.tan(math.radians(pitch))
    if extent.size == 0:
        return np.log(R) * cot
    x0 = math.log(anchor)
    p0 = x0 * cot
    tangent = np.tan(np.radians(pitch + residual))
    knots, phases = [x0], [p0]
    # Each side's spans are summed from the anchor and the sum laid from the anchor's own values - the order the
    # model sums them in, so this winding is the model's to the last bit and the tolerances below stay at rounding.
    # (tests/test_segments.py holds the model's winding to a loop of another order, to 1e-12.)
    span = turn = 0.0
    for j in range(SEGMENTS_OUTWARD_HAND):  # outward from the anchor
        span += extent[j] * abs(tangent[j])
        turn += extent[j] * (1.0 if tangent[j] > 0.0 else -1.0 if tangent[j] < 0.0 else 0.0)
        knots.append(x0 + span)
        phases.append(p0 + turn)
    span = turn = 0.0
    for j in range(SEGMENTS_OUTWARD_HAND, extent.size):  # inward from the anchor
        span += extent[j] * abs(tangent[j])
        turn += extent[j] * (1.0 if tangent[j] > 0.0 else -1.0 if tangent[j] < 0.0 else 0.0)
        knots.insert(0, x0 - span)
        phases.insert(0, p0 - turn)
    x = np.log(R)
    assert knots[0] < x.min() and x.max() < knots[-1] and np.all(np.diff(knots) >= 0.0)
    return np.interp(x, knots, phases)  # the straight line in ln R between the segments' ends


LANES_HAND = (0.4, 3.0, 1.15, 0.10, 2.6, 0.10)  # the footprint's q and c; κ·a, r_ring/a, the ratio, the width / a (D217)


def synthetic(unit: np.ndarray, phases=(0.0,) * 5, arm: float = 0.4, pitch: float = 13.5,
              bar_length: float = float("nan"), R: np.ndarray | None = None, lanes: tuple = LANES_HAND) -> GasPattern:
    """A pattern on a made-up disc: a flat curve of 220 km/s (κ = √2 v/R) and an exponential disc of 50 M☉/pc² at
    8 kpc with a 2.6 kpc scale length. Built directly: it does not pass through the switch. **Unbarred unless a
    half-length is given** (S58, D217: a half-length that is not a number is no bar and no taper; until S58 the
    helper gave every pattern a bar's taper and a bar amplitude of 0, a bar the model no longer has)."""
    R = DEFAULT.build().R if R is None else R
    kappa = math.sqrt(2.0) * 220.0 / R
    sigma = 50.0 * np.exp(-(R - 8.0) / 2.6)
    return GasPattern(R, unit, phases, arm, pitch, bar_length, kappa, sigma, G_HAND, SOUND_SPEED_HAND, *lanes)


def lane_floor(gp: GasPattern, R: np.ndarray) -> np.ndarray:
    """w_bar · min L on each ring of ``R`` (grid radii): the bound the gas is never under (D217 item 6; until S58
    w_bar (1 − B), the cosine bar's own trough). 0 on every ring of an unbarred pattern."""
    if not gp.barred:
        return np.zeros(np.shape(R))
    return pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[0] * gp.lanes.min(axis=1)


def one_mode(m: int = 4, strength: float = 1.0, **more) -> GasPattern:
    R = DEFAULT.build().R
    unit = np.zeros((len(pt.ARM_MODES), R.size))
    unit[pt.ARM_MODES.index(m)] = strength
    return synthetic(unit, **more)


def hand_newton(forcing: np.ndarray, eps: float) -> tuple[np.ndarray, int]:
    """The discrete equation ε² (φ_{k+1} − 2φ_k + φ_{k−1})/h² = e^{φ_k} − 1 − g_k on the ring's cells, solved here by
    a dense Newton in φ = ln s from s = 1 - a full matrix and numpy's general solver, the step halved while the
    convex functional J does not fall. Nothing of ``gas_response`` or ``gas_pattern``."""
    n = forcing.size
    h = 2.0 * math.pi / n
    stiffness = (eps / h) ** 2
    laplacian = 2.0 * np.eye(n) - np.roll(np.eye(n), 1, axis=0) - np.roll(np.eye(n), -1, axis=0)

    def functional(phi: np.ndarray) -> float:
        d = np.roll(phi, -1) - phi
        return float((0.5 * stiffness * d * d + np.exp(phi) - (1.0 + forcing) * phi).sum())

    phi = np.zeros(n)
    for step in range(60):
        s = np.exp(phi)
        residual = s - 1.0 - forcing + stiffness * (laplacian @ phi)
        if float(np.abs(residual).max()) < 1e-11:
            return s, step
        delta = np.linalg.solve(np.diag(s) + stiffness * laplacian, -residual)
        t, before = 1.0, functional(phi)
        while functional(phi + t * delta) > before and t > 1e-6:
            t *= 0.5
        phi = phi + t * delta
    raise AssertionError("the hand Newton did not converge in 60 steps")


def footprint_share(radius: float, a: float, q: float = 0.4, c: float = 3.0) -> float:
    """The share of a ring's 1440 cells whose centres lie inside the bar's body's footprint, m ≤ 1 with
    m = ((|x|/a)^c + (|y|/(q a))^c)^{1/c}: this file's arithmetic (S58, D217 item 8: the lanes' base is
    1/(1 + 1.6 × this))."""
    psi = -math.pi + (np.arange(1440) + 0.5) * (2.0 * math.pi / 1440)
    x, y = radius * np.cos(psi), radius * np.sin(psi)
    return float((((np.abs(x) / a) ** c + (np.abs(y) / (q * a)) ** c) ** (1.0 / c) <= 1.0).mean())


def hand_cell_means(profile: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """The mean, over each interval [lo_j, hi_j] of χ, of the periodic piecewise-linear function through ``profile``
    on the ring's cell centres χ_k = −π + (k + ½) 2π/n: the trapezoid rule on the function's own breakpoints, which
    is its exact integral. This file's arithmetic - no function of ``gas_response`` or ``gas_pattern``."""
    n = profile.size
    h = 2.0 * math.pi / n
    centres = -math.pi + (np.arange(-n, 2 * n) + 0.5) * h  # three turns of the ring
    values = np.tile(profile, 3)
    means = []
    for a, b in zip(lo, hi):
        turn = math.floor((a + math.pi) / (2.0 * math.pi))
        a0, b0 = a - 2.0 * math.pi * turn, b - 2.0 * math.pi * turn
        nodes = np.concatenate([[a0], centres[(centres > a0) & (centres < b0)], [b0]])
        height = np.interp(nodes, centres, values)
        means.append(float((0.5 * (height[1:] + height[:-1]) * np.diff(nodes)).sum()) / (b0 - a0))
    return np.array(means)


# --- a redistribution, not a source ----------------------------------------------------------------------------


def test_the_gas_contrast_averages_to_one_around_every_ring(model):
    """Positive, finite, and mean 1 round every ring of the published field - with nothing divided: each value is
    the law's mean over its cell, and a ring's cells tile the ring."""
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    assert g.shape == (o.grid.R.size, o.grid.phi.size)
    assert np.all(g > 0.0) and np.all(np.isfinite(g))
    assert float(np.abs(g.sum(axis=1) / g.shape[1] - 1.0).max()) < 1e-13
    assert not np.all(g == 1.0)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_published_field_is_the_law_s_mean_over_each_cell_and_is_never_divided(prod, template):
    """Gate G3 item 4 (it rewords D216 items 9 and 11 i): "the published (R, φ) field is the law's mean over each
    grid cell - the interpolant integrated exactly - so its ring mean is 1 to rounding on every grid with no
    division (pin 1e-13) ... ``contrast_at``, ``response_at`` and the censuses keep the point function". As built
    and as the gate's follow-up accepted it, the cell is the grid cell's extent in azimuth at the ring's own
    radius: the exact mean over φ there, not a mean over R (a point between two rings is blended in R).

    The published field is ``GasPattern.cell_means`` on the grid's own φ edges, bit for bit, and each of its rows
    is ``sector_means`` at that ring's radius, bit for bit: no step stands between the law and the field, a
    division least of all. **Measured: the ring mean is off 1 by 7.1e-14 (the Milky Way template) and 9.7e-14
    (``ngc_4414``) on the default grid - the solver's own ring mean, which it holds to 1e-13 - and by 1e-14 and
    2e-15 on grids of 36, 108, 500 and 720 φ cells.** (The first build published the point function at the cells'
    centres: 7e-14 on 360 cells, which divide the solver's 1440, but 2e-6 on 108 and 1.3e-3 on 36 - the response's
    harmonics aliased - and three small-grid tests had been re-pinned to that. They are back at 1e-12.)
    A cell's mean is not its centre's value: the two differ by up to 1.7e-3 of the ring's mean (on the flank of a
    crest, where the profile curves); and it is never under w_bar min L (S58, D217: until then w_bar (1 − B))."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R, phi, edges = o.grid.R, o.grid.phi, o.grid["phi"].edges
    g = np.asarray(o.fields["gas_density_contrast"])
    gp = shape_of(model, o)
    assert g.tobytes() == gp.cell_means(R, edges).tobytes()
    for i in (3, 60, 106, 133, 160, 399):
        assert g[i].tobytes() == gp.sector_means(float(R[i]), edges).tobytes(), i
    assert float(np.abs(g.sum(axis=1) / g.shape[1] - 1.0).max()) < 1e-13
    # S58 (D217 item 6): was `g >= taper (1 - B)`, the cosine bar's trough. The bound is w_bar min L - to the rounding
    # of a cell's mean where the lane field sits on its base across a whole cell - and 0 for `ngc_4414`.
    # S59 (D218): was `> -1e-14`, the Milky Way reading -2.1e-15. The lanes' own cell means sit up to 8.9e-14 under
    # their base (an exact mean taken as a difference of running sums; no winding in it, the same bits as before),
    # and until S59 the response's part of the cell covered that wherever it happened. The segments turn each
    # ring's response, and at 2.44 kpc a trough of it (1.3e-13) now lies on such a cell: -1.8e-14. Held to the
    # bound the suite's gate already holds the 240 galaxies to (-2e-13); the two parts are held apart, each at its
    # own rounding, in tests/test_bar.py.
    assert float((g - lane_floor(gp, R)[:, None]).min()) > -2e-13 and g.min() > 0.0
    # Against the point function at the cells' centres: another number, by the profile's curvature across a cell.
    # S58 (D217): were 1.718e-3 and 1.716e-3. The Milky Way's lanes are narrow - half a kiloparsec across, a few
    # cells of this grid inside 3 kpc - so a cell's mean and its centre differ by 1.2 % of the ring's mean there;
    # `ngc_4414`, unbarred, shows its innermost rings untapered, where the response swings hardest.
    # S59 (D218): were 1.198e-2 and 6.261e-3 - the Milky Way's on a ring the winding's segments have turned, inside
    # the bar's reach (3.79 kpc); `ngc_4414`'s at its pinned pitch of 28.9 degrees, the law's ε and f both 0.51 of
    # what they were, so a gentler response (1.01 kpc).
    point = gp.contrast(R, phi)
    assert float(np.abs(g - point).max()) == pytest.approx({"milky_way": 1.217e-2, "ngc_4414": 4.803e-3}[template], rel=0.02)
    # 360 divides 1440, so the response's centre samples average to 1 to rounding - but the lanes are laid in the
    # bar's frame, whose angle is no multiple of a cell, and their centre samples do not (S58: was < 5e-13 for both).
    sampled = float(np.abs(point.sum(axis=1) / point.shape[1] - 1.0).max())
    assert sampled < 5e-13 if template == "ngc_4414" else sampled == pytest.approx(9.82e-6, rel=0.02)
    # The module holds no tolerance to renormalise by, and its source does not divide a field by a mean. S58 (D217
    # item 8): the lanes' template is weighed by its own quadrature on the ring's cells - `ring_quadrature`, the one
    # division, a template's normalisation - and that is the only use of it.
    assert not hasattr(gm, "RING_MEAN_TOLERANCE")
    source = Path(gm.__file__).read_text(encoding="utf-8")
    assert ".mean(" not in source and source.count("ring_quadrature(") == 3  # its definition, the footprint's share, the weight
    # Any φ grid: the ring keeps its gas to rounding, and the centre samples do not.
    given = templates.overrides(templates.TEMPLATES[template])
    # S58 (D217): the 36-cell centre samples read 1.257e-3 and 1.056e-3; with the lanes, and with `ngc_4414`'s
    # inner rings untapered, 2.53e-2 and 7.26e-3 - the cells' means are 1 to 5e-14 as before.
    # S59 (D218): were 2.529e-2 and 7.263e-3 - the centre samples of rings the segments have turned (the Milky
    # Way), and of a gentler response at the pinned pitch (`ngc_4414`). The cells' means: 1 to 5e-14, as before.
    for n_phi, sampled in ((36, {"milky_way": 3.018e-2, "ngc_4414": 1.931e-3}[template]), (108, None), (500, None)):
        coarse = run(model, given, GridSpec(n_R=48, n_t=64, n_z=8, n_phi=n_phi), only=GAS_PATTERN_READS + ("gas_density_contrast",))
        small = np.asarray(coarse.fields["gas_density_contrast"])
        assert small.shape[1] == n_phi and np.all(small > 0.0)
        assert float(np.abs(small.sum(axis=1) / n_phi - 1.0).max()) < 1e-13, n_phi  # measured 1.2e-14 and 2e-15
        if sampled is not None:  # what the centre samples read on this grid: the first build's field
            centre = compose.gas_pattern(coarse.fields, coarse.grid.R, constants(model)).contrast(coarse.grid.R, coarse.grid.phi)
            assert float(np.abs(centre.sum(axis=1) / n_phi - 1.0).max()) == pytest.approx(sampled, rel=0.02)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_cell_averaged_field_against_the_exact_solution_s_cell_means(prod, template):
    """Gate G3 item 4: "re-measure and pin the averaged field's error against the exact solution's cell means".
    The reference is the same equation solved on finer cells - 2880 and 5760 - and averaged over the same grid
    cells. **The h² law**: the error of a cell mean at n solver cells is c/n² (the solver's second-order error and
    the linear interpolant's, both; a cell's mean feels them averaged over the grid cell, so it is smaller than the
    point function's error at a midpoint), so against the 5760-cell reference the 1440-cell means are off by
    c (1 − 1/16)/1440² and the 2880-cell ones by c (1/4 − 1/16)/1440²: **their ratio is 5, and it reads 5.00**.
    The 1440-cell error against the exact solution is then 16/15 of the first.

    **As measured (the Milky Way template; ``ngc_4414``): of the published field 2.8e-4 (9.1e-4) at worst, at
    5.1 kpc (1.1 kpc); of s itself 1.2e-3 (9.1e-4), at 1.6 kpc deep inside the bar where the arm's weight is under
    1 % (``ngc_4414`` has no bar since S58, so its s is its field), and 3.0e-4 (6.1e-5) beyond 6 kpc.** The cell
    count is the ruling's (G3 item 5) and is not touched. (Until S58: 2.1e-4 (2.1e-4), 9.2e-4 (9.1e-4), 2.5e-4
    (6.1e-5).)

    **S59 (D218), as measured now: of the published field 2.8e-4 (6.6e-4) at worst, at 5.3 kpc (0.71 kpc); of s
    itself 1.2e-3 (6.6e-4); 2.9e-4 (2.7e-5) beyond 6 kpc.** The Milky Way's rings are the profiles they were, each
    read over the grid's cells at another phase - the winding's segments' - so the errors of its cells' means move
    in the third figure. ``ngc_4414`` is at its pinned pitch, 28.9 degrees: ε and f are 0.51 of what they were, the
    response gentler, its error smaller. The h² law reads 5.00 on both, as before."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R, edges = o.grid.R, o.grid["phi"].edges
    gp = shape_of(model, o)
    carries = gp.carries
    f, eps = gp.forcing_amplitudes()[carries], gp.epsilon()[carries]
    # S59 (D218): was `pt.bar_terms(R, gp.pitch_deg, gp.bar_length)` - a grid cell's extent in χ is its φ edges
    # less the winding in seeded segments at the ring (the pattern's own, which is this file's from the published
    # rows to 1e-12), where it was ln R · cot p.
    taper, phase, _ = pt.bar_terms(R, gp.pitch_deg, gp.bar_length, gp.winding)
    assert float(np.abs(phase - hand_winding(o.fields, R)).max()) < 1e-12
    lo, hi = edges[None, :-1] - phase[carries, None], edges[None, 1:] - phase[carries, None]
    means = {gr.CELLS: gr.sector_mean(gp.profiles[carries], lo, hi)}
    for cells in (2880, 5760):
        fine, _ = gr.solve(gr.forcing(pt.ARM_MODES, f, np.asarray(gp.phases), cells), eps)
        means[cells] = gr.sector_mean(fine, lo, hi)
    weight = (1.0 - taper[carries])[:, None]
    at_1440, at_2880 = np.abs(means[1440] - means[5760]), np.abs(means[2880] - means[5760])
    got = (float(at_1440.max()), float((at_1440 * weight).max()), float(at_1440[R[carries] > 6.0].max()))
    # S58 (D217): were (9.207e-4, 2.105e-4, 2.458e-4) and (9.144e-4, 2.101e-4, 6.122e-5). The Milky Way's two-armed
    # mode sits on the bar's axis now (θ₂ = 0, item 9), another sum of the same modes on every ring that carries it;
    # `ngc_4414`'s response is the one it was, and unbarred its arm weight is 1 on every ring, so the weighted error
    # is the unweighted one, at 1.09 kpc.
    # S59 (D218): were (1.1786e-3, 2.760e-4, 2.950e-4) and (9.144e-4, 9.144e-4, 6.122e-5): the cells are read at the
    # segments' phase (the Milky Way: the same profiles, the third figure moves; read at one pitch's phase they are
    # 1.1786e-3, 2.760e-4, 2.950e-4 still), and `ngc_4414`'s response is the one of its pinned pitch (at 0.71 kpc).
    want = {"milky_way": (1.1786e-3, 2.765e-4, 2.899e-4), "ngc_4414": (6.582e-4, 6.582e-4, 2.729e-5)}[template]
    assert got == pytest.approx(want, rel=0.01), got
    assert float(at_1440.max() / at_2880.max()) == pytest.approx(5.0, abs=0.03)
    assert float((at_1440 * weight).max() / (at_2880 * weight).max()) == pytest.approx(5.0, abs=0.03)
    # The published field's own arm part is those 1440-cell means: its error is the weighted one above.
    published = np.asarray(o.fields["gas_density_contrast"])[carries]
    # S58 (D217): the bar's part of the cell is the lanes' exact mean (it was the cosine's own integral), which no
    # solver cell count touches; an unbarred galaxy has none.
    exact = weight * means[5760]
    if gp.barred:
        angle = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[2]
        exact = exact + taper[carries, None] * gr.sector_mean(gp.lanes[carries], np.broadcast_to(edges[None, :-1] - angle, lo.shape),
                                                              np.broadcast_to(edges[None, 1:] - angle, lo.shape))
    assert float(np.abs(published - exact).max()) == pytest.approx(want[1], rel=0.01)


def test_the_sector_means_are_the_exact_means_of_the_point_function(model):
    """Twelve sectors at five radii: their mean is the ring's, 1, to rounding; and each sector's mean is the
    dense average of ``contrast_at`` over it to the dense average's own error (a midpoint rule on a piecewise
    linear function: 4000 points a sector) - the series of S56 was good to 1e-3 on a ranked ridge; this is the
    interpolant's own integral. Also between two grid rings, where a point blends two profiles."""
    o = out(model)
    gp = shape_of(model, o)
    R = o.grid.R
    edges = np.linspace(0.0, 2.0 * np.pi, 13)
    worst = 0.0
    for radius in (1.0, 3.0, 6.0, 10.0, float(0.3 * R[120] + 0.7 * R[121])):
        means = gp.sector_means(radius, edges)
        assert float(means.mean()) == pytest.approx(1.0, abs=1e-12)
        dense = []
        for a, b in zip(edges[:-1], edges[1:]):
            phi = a + (np.arange(4000) + 0.5) * (b - a) / 4000
            dense.append(float(gp.contrast_at(np.full_like(phi, radius), phi).mean()))
        worst = max(worst, float(np.abs(means - np.array(dense)).max()))
        assert means.max() > 1.0 > means.min()  # the arms are resolved: not a flat ring
        # and the many-radii form the stage publishes with is this one, at any radius
        assert gp.cell_means(np.array([radius]), edges)[0].tobytes() == means.tobytes()
    assert worst < 2e-7  # measured 4e-8: the midpoint rule's, not the means'
    # Thirty-two sectors, unequal ones, and a ring past the last mode and the bar: every sector exactly 1.
    uneven = np.concatenate([[0.0], np.sort(np.random.default_rng(5).uniform(0.0, 2.0 * np.pi, 31)), [2.0 * np.pi]])
    means = gp.sector_means(8.0, uneven)
    assert float((means * np.diff(uneven)).sum() / (2.0 * np.pi)) == pytest.approx(1.0, abs=1e-12)
    assert np.all(gp.sector_means(20.0, edges) == 1.0) and np.all(gp.cell_means(np.array([20.0, 25.0]), edges) == 1.0)


# --- the gate ----------------------------------------------------------------------------------------------------


def gate(gp: GasPattern, edges: np.ndarray) -> dict[str, float]:
    """The gate's numbers for one pattern (D216, "the gate (every ring, every seed, both templates)"), with its
    residual item as gate G3 words it (item 2): "on every cell |r_k| ≤ max(1e-10, F_k), F_k recorded per ring as
    its rounding floor; |Σr_k|/cells < 1e-13; the returned s re-logged satisfies the same with F_k + 4u·ε²/h²".

    The solver's own residual and floor are its report's (per ring: the largest of each; the cell-by-cell rule is
    the solver's convergence itself). The re-logged statement is asserted here on every cell of every ring, from
    the profile the pattern holds, with ``gas_response.residual`` and ``gas_response.rounding_floor``. Everything
    else is recomputed from the profiles."""
    R = gp.R
    s, carries, d = gp.profiles, gp.carries, gp.diagnostics
    f, eps = gp.forcing_amplitudes(), gp.epsilon()
    forcing = gr.forcing(pt.ARM_MODES, f[carries], np.asarray(gp.phases))
    relogged = np.abs(gr.residual(s[carries], forcing, eps[carries]))
    floor = gr.rounding_floor(s[carries], eps[carries])
    inv_h2 = (gr.CELLS / (2.0 * math.pi)) ** 2
    # The reviewer's note (D216): the criterion itself implies only max(1e-10, F_k) + F_k/2 + 4u ε²/h² for the
    # re-logged profile; the gate's tighter wording holds because accepted residuals sit under half their floor
    # (0.95 of this bound at worst over 842 galaxies). If it ever fails, the bound is what to re-read, not the solver.
    assert np.all(relogged <= np.maximum(1e-10, floor + 4.0 * ROUNDING * (eps[carries] ** 2)[:, None] * inv_h2))
    assert np.all(d.residual <= np.maximum(1e-10, d.floor))
    # The floor of ln s as the solver held it and of the logarithm taken again: the same spacing of doubles, but
    # where a cell's ln s sits on a power of two (a factor 2 there, on that cell).
    assert np.all((floor.max(axis=1) <= 2.0 * d.floor) & (d.floor <= 2.0 * floor.max(axis=1)))
    assert np.all(s[~carries] == 1.0)  # a ring with no mode has s = 1
    floor_g = lane_floor(gp, R)  # S58 (D217 item 6): w_bar min L, where it was w_bar (1 − B)
    field = gp.cell_means(R, edges)  # what the stage publishes
    assert np.all(np.isfinite(s)) and np.all(np.isfinite(field))
    return {
        "residual": float(d.worst_residual), "relogged": float(relogged.max()), "floor": float(d.floor.max()),
        "over": float((d.residual / np.maximum(1e-10, d.floor)).max()),  # the residual over what it is held under
        "on_floor": float((d.floor > 1e-10).sum()),  # rings whose floor, not the tolerance, is the bound
        "sum": float(np.abs(d.residual_sum).max() / gr.CELLS),
        "mean": float(np.abs(s.sum(axis=1) / s.shape[1] - 1.0).max()),
        "min_s": float(s.min()), "max_s": float(s.max()),
        "margin": float((field - floor_g[:, None]).min()),  # min g − w_bar min L, ring by ring
        "ring_mean": float(np.abs(field.sum(axis=1) / field.shape[1] - 1.0).max()),
        "steps": float(d.worst_steps), "halvings": float(d.worst_halvings),
        "max_g": float(field.max()), "min_g": float(field.min()),
    }


@pytest.mark.parametrize("template", TEMPLATES)
def test_gate_every_ring_of_both_templates(prod, template):
    """The gate at each template's own seeds, on every ring, with the numbers as read (the module docstring)."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    gp = shape_of(model, o)
    got = gate(gp, o.grid["phi"].edges)
    want = {
        # S58 (D217): were min_s=4.50e-11, max_s=5.6975, min_g=0.019943, max_g=3.092221 (the Milky Way: θ₂ = 0 is
        # another sum of the modes on the inner rings, and the published field carries the lanes, 6.66 at 2.06 kpc)
        # and min_g=0.014257, max_g=2.688408 (`ngc_4414`: unbarred, its field is its response, the innermost rings'
        # 4.6e-18 and 4.73 no longer under a taper; s itself is unmoved).
        # S59 (D218): the Milky Way's were min_g=0.018394, max_g=6.664030 - s is the profile it was on every ring
        # (min_s, max_s, the counts and the floor unmoved); the segments turn the rings, so the published cells are
        # read elsewhere on them, a lane's crest and an arm's meeting at another angle (6.68 at 2.06 kpc).
        # `ngc_4414`'s were steps=9, min_s=1.81e-17, max_s=4.7322, min_g=4.578e-18, max_g=4.727844, floor=1.933e-11:
        # at its pinned pitch, 28.9 degrees, ε and f are both 0.5121 of what they were at the drawn 14.33, and the
        # response is another: its crest stands at 3.16 where it stood at 4.73, one Newton step fewer; unbarred,
        # its field is its response (the smallest cell 3.9e-16 at 0.71 kpc).
        "milky_way": dict(rings=165, steps=8, halvings=1, min_s=6.157e-14, max_s=6.2295, min_g=0.018402, max_g=6.678598, floor=1.279e-11),
        "ngc_4414": dict(rings=133, steps=8, halvings=0, min_s=1.556e-15, max_s=3.1580, min_g=3.946e-16, max_g=3.156717, floor=5.069e-12),
    }[template]
    assert int(gp.carries.sum()) == want["rings"]
    # The residual: at these pitches (13.5 and - pinned since S59 - 28.9 degrees) every ring's floor is far under
    # 1e-10 and the absolute tolerance governs, as it did before G3. Measured 5.8e-12 and 5.3e-12, re-logged the same.
    assert got["floor"] == pytest.approx(want["floor"], rel=0.01) and got["on_floor"] == 0
    assert got["residual"] < gr.RESIDUAL_TOLERANCE == 1e-10 and got["relogged"] < 1e-10
    assert got["sum"] < gr.SUM_TOLERANCE == 1e-13
    assert got["mean"] < 1e-12                                       # measured 9.7e-14 and 9.2e-14, nothing divided
    # nothing clipped: the law's own positivity. S58 (D217 item 6): the bound is w_bar min L, held to the rounding of
    # a cell's mean (the Milky Way reads −2.1e-15 where the lane field sits on its base across a cell); was `>= 0.0`.
    # S59 (D218): was `> -1e-14`. The Milky Way reads −1.8e-14: the lanes' own cell means lie up to 8.9e-14 under
    # their base (no winding in them: unmoved), and a trough of the turned response now sits on such a cell
    # (the published field's test, above, and tests/test_bar.py). Held to the suite's bound, −2e-13.
    assert got["min_s"] > 0.0 and got["margin"] > -2e-13
    assert got["ring_mean"] < 1e-13                                  # measured 7.1e-14 and 9.3e-14: the cell means
    assert (got["steps"], got["halvings"]) == (want["steps"], want["halvings"])
    assert got["steps"] <= gr.MAX_NEWTON_STEPS == 120 and got["halvings"] <= gr.MAX_HALVINGS == 30
    assert got["min_s"] == pytest.approx(want["min_s"], rel=0.02) and got["max_s"] == pytest.approx(want["max_s"], abs=2e-4)
    # S57 (D216 G3): were (0.019924, 3.09294) and (0.014249, 2.68897), the point function at the cells' centres.
    assert got["max_g"] == pytest.approx(want["max_g"], abs=2e-5) and got["min_g"] == pytest.approx(want["min_g"], rel=2e-3)
    # The bound of D216 item 12 as S58 leaves it, [w_bar min L, max(max s, max L)]: the margin over the floor is
    # rounding where the arm's weight is nothing. S58 (D217): was `0.0 < margin < 3e-5 and max_g <= max_s` - the
    # cosine bar never passed the response's crest; the lanes do (7.06 on the lane field against 6.23).
    assert got["margin"] < 3e-5 and got["max_g"] <= max(got["max_s"], float(gp.lanes.max()) if gp.barred else 0.0)
    # The declared ramp's top is the viewer's display range, not a cap on the field: nothing clips to it. S58
    # (D217): until S58 both templates stayed under it at their own seeds (3.09 and 2.69); the Milky Way's lanes
    # (6.66) and `ngc_4414`'s untapered inner rings (4.73) pass it now, as strong seeds always did.
    # S59 (D218 item 6): was `np.any(... > 4.0)` for both. The Milky Way's lanes still pass it (6.68); `ngc_4414` at
    # its pinned pitch does not (3.157 at most, at 0.56 kpc) - a gentler response, and nothing clipped it there.
    assert gm.GAS_DENSITY_CONTRAST.ramp.hi == 4.0
    assert bool(np.any(np.asarray(o.fields["gas_density_contrast"]) > 4.0)) == (template == "milky_way")


def test_gate_every_ring_on_every_seed_the_suite_draws(prod):
    """The gate on the suite's seeds - sixty pattern seeds by two texture seeds for each template's inputs, the 240
    galaxies the stellar positivity test draws (``tests/test_modes.py``): on every ring the residual item as gate
    G3 words it (``gate``, above); the ring's mean 1 to 1e-12 on the solver's cells with no division; min s > 0 and
    min g ≥ w_bar min L with nothing clipped (S58, D217 item 6: until then w_bar (1 − B)); the published field's
    ring mean within its pinned 2e-13; Newton's counts under the solver's maxima; finite everywhere; the sector
    means averaging to 1; and the stellar amplitudes the forcing is made of inside the saturation's bound,
    Σ_m A_m ≤ 1 − b with b the bar's body's depth (S58, item 5: until then B·taper), on every ring (G3 item 3).

    **Since S58 (D217) these are other galaxies, and the numbers below are re-read on them.** The Milky Way's
    inputs: the two-armed mode on the bar's axis (θ₂ = 0), the lanes in the bar's reach, the saturation on the
    body's depth. ``ngc_4414``'s: unbarred by its pin - no taper, so its arm modes run to the centre, its inner
    rings saturate and its published field is its response alone, innermost rings and all. **All 240 still meet
    the gate; none raises.** What S57 read, kept below where it is the record of gate G3, was read on the galaxies
    of that day.

    **All 240 meet it.** The first build's two failures - ``ngc_4414`` at pattern seed 33, either texture seed, a
    drawn pitch of 1.78 degrees: ε = a/(κR sin p) about 1 on the inner rings, the forcing's sum 60-80, the
    residual stalled at 1.0-1.3e-10 against an absolute 1e-10 for 120 steps - **now converge in 10 steps at most**:
    their worst ring's rounding floor is 3.38e-10 and its residual 1.31e-10 and 1.24e-10, 0.48 and 0.49 of what
    it is held under; 50 and 48 of their 133 rings have a floor above 1e-10. Seventeen of the 240 galaxies have
    such a ring (249 rings in all), every one at a drawn pitch under 7.7 degrees.

    **One galaxy that converged before G3 is not the bits it was**: ``ngc_4414`` at pattern seed 1, texture seed 1
    (pitch 2.06 degrees). Its ring at 0.49 kpc (arm weight 3.7e-4) took 10 Newton steps under the absolute
    tolerance - the last two wandering on the rounding floor until one landed at 9.5e-11 - and takes 8 now,
    stopping at 1.19e-10 under a floor of 2.5e-10. The two profiles differ by 1.8e-15 of themselves; the
    published field, the point function and the sector means of that galaxy are bit for bit what they were.

    **The record across the criterion change, accepted at gate G3's follow-up (D216)** - "my bit-identical
    assertion was too strong where the old acceptance was itself a chance landing inside the floor". Over 842
    galaxies - this suite's 240, the two templates, and a sweep of 300 pattern seeds a template at the template's
    own texture seed (the sweep is outside this test): **816 bit-identical; 22 that raised now converge (2 of the
    suite's, 5 and 15 of the sweep's); 4 moved** - this one and three of the sweep's (Milky Way pattern seeds 152
    and 279, ``ngc_4414`` 227) - **each by at most 2.0e-15 of the profile, on inner rings (0.26-0.79 kpc) whose
    arm weight is 5.2e-4 at most; one published cell moved, by 5.55e-17 (Milky Way pattern seed 279)**. The bound
    is asserted for the suite's galaxy, against the first build's rule made again, in
    ``test_the_suite_galaxy_whose_bits_moved_with_the_criterion_moved_by_rounding``. The sweep as it reads now: no
    galaxy raises; the worst floor 5.8e-10 and 9.7e-10, the worst residual over its bound 0.49; s from 3.9e-41 to
    14.0 and from 2.7e-79 to 14.8.

    **Since S59 (D218) half of these are other galaxies again, and the numbers below are re-read.** (a) *The winding
    is laid in seeded segments*: each ring's response is the profile it was - the law's ε and f read the disc's own
    pitch, so no residual, floor, step count or extreme of s moved on the Milky Way's 120 - and only where it lies
    among the grid's cells did (the published field's extremes, its margin). (b) *``ngc_4414`` pins its measured
    pitch, 28.9 degrees* (item 6): **all 120 of that template's suite galaxies are at that one pitch**, where they
    were at sixty drawn ones (1.0 to 24.1 degrees, the median 11.9). Their ε and f are sin p_drawn / sin 28.9° of
    what they were; none has a ring on its rounding floor; and on its saturated inner rings a galaxy's forcing no
    longer depends on the pattern seed (the saturated amplitudes are the gain's split alone, and the pitch is one
    number), so galaxies of one texture seed share those rings to rounding - pattern seeds 1 and 33 at texture
    seed 1 read the same largest crest, 3.9156. **The tightly wound regime of an unbarred disc has
    left the suite** with those sixty pitches: the two galaxies that raised at the first build and the one whose
    bits moved with the criterion are read below as what they were - that disc with its pitch as the law draws it,
    the pitch's pin taken off (``drawn_pitch``) - and their numbers are S58's to every figure pinned. The 240 as
    they are now: all meet the gate, none raises."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    edges = np.linspace(0.0, 2.0 * np.pi, 33)
    worst: dict[str, float] = {}
    held: dict[tuple[str, int, int], dict[str, float]] = {}
    on_floor: dict[tuple[str, int, int], float] = {}
    saturated_most = 0.0
    sides, mid_most = np.zeros(4, dtype=int), 0
    for template in TEMPLATES:
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                given = {**templates.overrides(templates.TEMPLATES[template]), "pattern_seed": pattern_seed, "texture_seed": texture_seed}
                o = run(model, given, only=GAS_PATTERN_READS)
                gp = compose.gas_pattern(o.fields, o.grid.R, c)
                assert gp is not None and not gp.flat
                label = (template, pattern_seed, texture_seed)
                got = gate(gp, o.grid["phi"].edges)  # raises nowhere: every ring of every galaxy converges
                held[label] = got
                assert got["over"] <= 1.0 and got["sum"] < 1e-13, label
                assert got["mean"] < 1e-12, label
                # S58 (D217): the margin was `>= 0.0` over w_bar (1 − B), a cosine's own integral. Over w_bar min L it
                # holds to the rounding of a cell's mean of the lane field (6.2e-14 under at worst over the 240).
                assert got["min_s"] > 0.0 and got["margin"] > -2e-13, label
                assert got["ring_mean"] < 2e-13, label
                assert got["steps"] <= gr.MAX_NEWTON_STEPS and got["halvings"] <= gr.MAX_HALVINGS, label
                if got["on_floor"]:
                    on_floor[label] = float(o.fields["pitch_angle"])
                for radius in (3.0, 8.0):
                    assert float(gp.sector_means(radius, edges).mean()) == pytest.approx(1.0, abs=1e-12), label
                # The stellar amplitudes the forcing is made of, as published: inside the saturation's bound.
                # S58 (D217 item 5): the bound was 1 − B·taper; it is 1 − b, b the body's depth (0 with no bar).
                depth = compose.stellar_pattern(o.fields, o.grid.R).depth
                assert gp.barred == (template == "milky_way") == bool(depth.any()), label
                total = np.sum([np.asarray(o.fields[n], dtype=float) for n in pt.AMPLITUDE_FIELDS], axis=0)
                excess = float((total - (1.0 - depth)).max())
                assert excess <= 1e-12, label
                saturated_most = max(saturated_most, excess)
                # Where the gas's tallest crest sits against the stellar sum's, in solver cells, signed (the
                # offset's test, below): counted where the two are the same arm's crest (within 20 cells).
                apart = crest_separation(gp)[gp.carries]
                same = np.abs(apart) <= 20
                sides += np.array([(apart[same] < 0).sum(), (apart[same] == 0).sum(), (apart[same] > 0).sum(), (~same).sum()])
                mid = same & (o.grid.R[gp.carries] >= 6.0) & (o.grid.R[gp.carries] <= 10.0)
                mid_most = max(mid_most, int(np.abs(apart[mid]).max(initial=0)))
                for key, value in got.items():
                    worst[key] = min(worst.get(key, value), value) if key in ("min_s", "margin", "min_g") else max(worst.get(key, value), value)
    assert len(held) == 240
    # S59 (D218 item 6): the three galaxies of gate G3's record were `held[("ngc_4414", 33, 0)]`, `(33, 1)` and
    # `(1, 1)` - the suite's own. The template pins its pitch since, so on the suite those labels are galaxies at
    # 28.9 degrees (no ring on its floor, residuals of 5-6e-12); the record's galaxies are that disc with the
    # pitch's pin off, at their drawn 1.78 and 2.06 degrees, and they are read as such - every pin below unmoved.
    drawn: dict[tuple[str, int, int], dict[str, float]] = {}
    drawn_at: dict[tuple[str, int, int], float] = {}
    for label in (("ngc_4414", 33, 0), ("ngc_4414", 33, 1), ("ngc_4414", 1, 1)):
        assert held[label]["on_floor"] == 0 and held[label]["residual"] < 1e-11 and label not in on_floor, label
        o = run(model, drawn_pitch(label[0], pattern_seed=label[1], texture_seed=label[2]), only=GAS_PATTERN_READS)
        gp = compose.gas_pattern(o.fields, o.grid.R, c)
        assert gp is not None and not gp.flat and not gp.barred, label
        drawn[label], drawn_at[label] = gate(gp, o.grid["phi"].edges), float(o.fields["pitch_angle"])
        assert drawn[label]["over"] <= 1.0 and drawn[label]["sum"] < 1e-13 and drawn[label]["min_s"] > 0.0 and drawn[label]["margin"] > -2e-13, label
    # The two that raised at the first build, as they converge now (their floors and residuals, as read).
    # S58 (D217): were floor 3.384e-10, residuals 1.305e-10 and 1.238e-10, 10 steps, 48 and 50 rings on their
    # floor - `ngc_4414` with a bar. Unbarred: 3.067e-10, 1.371e-10 and 1.299e-10, 9 steps, 45 and 42 rings.
    for label, residual, rings in ((("ngc_4414", 33, 0), 1.3705e-10, 45), (("ngc_4414", 33, 1), 1.2989e-10, 42)):
        got = drawn[label]
        assert got["floor"] == pytest.approx(3.0673e-10, rel=0.01) and got["residual"] == pytest.approx(residual, rel=0.01), label
        assert got["steps"] == 9 and got["residual"] > 1e-10 and 0.4 < got["over"] < 0.5, label
        assert drawn_at[label] == pytest.approx(1.780, abs=2e-3) and got["on_floor"] == rings, label
    # The one whose bits moved with the criterion at S57 (the docstring): `ngc_4414` at pattern seed 1, texture
    # seed 1. S58 (D217): was residual 1.186e-10 under a floor of 2.516e-10, 9 steps; unbarred it is another
    # galaxy - 9.673e-11 under 2.280e-10, 9 steps - and the two rules solve it to the same bytes
    # (``test_the_suite_galaxy_whose_bits_moved_with_the_criterion_moved_by_rounding``).
    moved = drawn[("ngc_4414", 1, 1)]
    assert moved["residual"] == pytest.approx(9.673e-11, rel=0.01) and moved["floor"] == pytest.approx(2.280e-10, rel=0.01) and moved["steps"] == 9
    assert drawn_at[("ngc_4414", 1, 1)] == pytest.approx(2.065, abs=2e-3)
    # The worst seen over the 240, recorded: Newton's counts (the maxima are 120 and 30); the largest floor and the
    # residual nearest its bound - under half of it everywhere, since the bound carries a factor 2 for the
    # residual's own arithmetic; the ring mean 1.0e-13 on the solver's cells; the published ring mean; s from
    # 7.7e-36 to 15.88; the published field from 2.6e-23 to 8.58 (S59; 2.3e-21 to 10.91 until then); its margin
    # over w_bar min L.
    # S57 (D216 G3): was `5e-11 < worst residual < 1e-10` over the 238 - a pin that sat on the rounding floor it
    # is now judged against. The residual over its bound is the robust reading.
    # S58 (D217): were steps (11, 2), floor 3.384e-10, residual 1.305e-10, s from 2.4e-44 to 14.39.
    # S59 (D218 item 6): were floor 3.0673e-10 and residual 1.3705e-10 - `ngc_4414` at pattern seed 33, a drawn pitch
    # of 1.78 degrees, which is on the suite no longer (read above with its pitch drawn). The worst of the 240 as
    # they are: the Milky Way's inputs at pattern seed 33 (2.02 degrees), 2.165e-10 and 8.656e-11.
    assert (worst["steps"], worst["halvings"]) == (10, 2)
    assert worst["floor"] == pytest.approx(2.1650e-10, rel=0.01) and 0.45 < worst["over"] < 0.5
    assert worst["residual"] == pytest.approx(8.6558e-11, rel=0.01) and worst["relogged"] < 5e-10
    assert worst["mean"] < 2e-13 and worst["ring_mean"] < 2e-13 and worst["sum"] < 1e-13
    assert 0.0 < worst["min_s"] < 1e-34 and worst["max_s"] == pytest.approx(15.88, abs=0.02)
    # S57 (D216 G3, the reviewer's second pass): the second build had loosened these two to `> 1e-3` and `abs=0.03`;
    # re-read on the cell-averaged field: 0.0016862 (ngc_4414, pattern seed 55) and 6.77163 (Milky Way, seed 40).
    # S58 (D217): were 1.6862e-3 and 6.7716. **`ngc_4414`'s inputs, unbarred, publish their innermost rings as the
    # response leaves them**: 2.27e-21 of the ring's mean at the lowest (pattern seed 5) and 10.91 at the highest
    # (pattern seed 1, a pitch of 2.06 degrees) - the razor-thin forcing's known excess on tightly wound inner rings
    # (#142), which a bar's taper used to hide. Positive on every seed; nothing clipped. The margin over w_bar min L
    # is the rounding of a cell's mean at its lowest (−6.2e-14, the Milky Way's inputs at pattern seed 52).
    # S59 (D218): were min_g 2.269e-21 and max_g 10.907, both `ngc_4414`'s at drawn pitches of 2-8 degrees. At its
    # pinned 28.9 degrees that template's lowest cell is 2.64e-23 (pattern seed 12, texture seed 1) and no cell of
    # its 120 galaxies is as high as the Milky Way's inputs' highest: 8.582, at pattern seed 33 (a drawn pitch of
    # 2.02 degrees). The margin: −6.4e-14 (pattern seed 6, texture seed 1; was −6.2e-14 at seed 52) - the lanes' own
    # cell means, which the segments do not touch, under another trough of the response.
    assert -2e-13 < worst["margin"] < 0.0 and worst["min_g"] == pytest.approx(2.639e-23, rel=0.02) and worst["max_g"] == pytest.approx(8.582, abs=2e-3)
    assert worst["min_g"] > 0.0
    # Which galaxies have a ring whose floor is the bound: seven, at the lowest drawn pitches.
    # S58 (D217): were seventeen under 7.7 degrees, at most 50 rings; `ngc_4414` at pattern seed 28 left the list
    # and the Milky Way's inputs at pattern seed 52 joined it.
    # S59 (D218 item 6): were sixteen, at most 45 rings, nine of them `ngc_4414`'s inputs at pattern seeds 1, 18, 33,
    # 40 and 52 - every one of that template's galaxies is at 28.9 degrees now, and none has such a ring. The
    # Milky Way's seven stand as they were (pattern seeds 1, 33, 40 and 52; at most 26 rings).
    assert len(on_floor) == 7 and max(on_floor.values()) < 5.8 and worst["on_floor"] == 26
    assert {k[:2] for k in on_floor} == {("milky_way", 1), ("milky_way", 33), ("milky_way", 40), ("milky_way", 52)}
    # The saturation's bound is met with equality on a saturated ring, to rounding (the excess is rounding's).
    assert -1e-15 < saturated_most <= 1e-12
    # The offset's sign over the 240 (gate G3's follow-up): the gas's tallest crest against the stellar sum's is
    # at the smaller χ on 12 008 rings, on the same cell on 9 280 and at the larger χ on 13 738 - both sides - and
    # on 734 rings the tallest gas crest is another arm's. Over 6-10 kpc the two are never more than 4 solver cells
    # (1 degree) apart on any of the 240: the field's about says "within about a degree ... over the mid disc, to
    # either side". S58 (D217): were 11 697 / 11 012 / 12 298 / 753 with the two-armed phase a draw in every galaxy
    # and a bar's taper on `ngc_4414`'s saturation.
    # S59 (D218 item 6): were 12 008 / 9 280 / 13 738 / 734. The separation is the solver's own (in χ: the segments do
    # not enter it), so the Milky Way's 120 count as they did; `ngc_4414`'s 120, each at 28.9 degrees, are other
    # rings: 12 218 / 7 510 / 15 270 / 762, still both sides, still at most 4 cells over 6-10 kpc.
    print(f"crest separation over the 240: smaller chi {sides[0]}, same cell {sides[1]}, larger chi {sides[2]}, another arm's {sides[3]}; "
          f"6-10 kpc at most {mid_most} cells")
    assert sides.tolist() == [12218, 7510, 15270, 762] and mid_most == 4


def test_a_ring_the_solver_cannot_converge_raises_and_nothing_catches_it(prod, monkeypatch):
    """D216 item 7: "a ring that fails to converge within the counts is a build failure (raise) ... there is no
    fallback and no linear substitute". Since gate G3 the galaxies that raised at the first build converge, so the
    failure is forced as the instrument's own test forces it - the solver is given fewer Newton steps than a ring
    needs - and it is shown to come through every door uncaught: the pattern's profiles, a point, a sector, the
    cell means, the stage and the whole run."""
    model = prod[0].get(DEFAULT_MODEL)
    # S59 (D218 item 6): was `{**overrides(ngc_4414), "pattern_seed": 33}`. The template pins its measured pitch
    # since, so that galaxy - the tightly wound one, its pitch the law's draw - is this disc with the pitch's pin
    # off; pinned, pattern seed 33 is at 28.9 degrees like every other, with no ring on its rounding floor.
    given = drawn_pitch("ngc_4414", pattern_seed=33)
    o = run(model, given, only=GAS_PATTERN_READS)
    assert float(o.fields["pitch_angle"]) == pytest.approx(1.780, abs=2e-3) and "pitch_angle" not in o.inputs
    # With the steps it needs (10 at most) this galaxy - the pattern seed that raised before G3 - is solved, its
    # worst ring on a rounding floor above the absolute tolerance.
    gm.forget_solutions()
    solved = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert 5 < solved.diagnostics.worst_steps <= 10 and solved.profiles.min() > 0.0 and solved.diagnostics.floor.max() > 1e-10
    full = np.asarray(run(model, given, only=("gas_density_contrast",)).fields["gas_density_contrast"])
    assert np.all(np.isfinite(full)) and full.min() > 0.0
    # Refused its steps, it raises - and nothing between the solver and the caller catches it.
    gm.forget_solutions()  # the cache must not hand back the solution just made
    monkeypatch.setattr(gr, "solve", functools.partial(gr.solve, max_steps=4))
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert not gp.flat
    with pytest.raises(gr.ConvergenceError, match="Newton did not converge") as failure:
        gp.profiles
    assert failure.value.steps == 4 and failure.value.residual > 1e-10
    for call in (lambda: gp.contrast_at(np.array([8.0]), np.array([1.0])),
                 lambda: gp.sector_means(8.0, np.linspace(0.0, 2.0 * np.pi, 5)),
                 lambda: gp.cell_means(o.grid.R, o.grid["phi"].edges),
                 lambda: run(model, given, only=("gas_density_contrast",)),
                 lambda: run(model, only=("gas_density_contrast",))):  # the default galaxy needs 8 steps: it raises too
        with pytest.raises(gr.ConvergenceError):
            call()
    assert len(gm._SOLUTIONS) == 0  # a failure is not kept
    # With the layer off there is no pattern to solve, and the galaxy runs whatever the solver is given.
    off = run(model, given, only=("gas_density_contrast",), layer=False)
    assert np.all(np.asarray(off.fields["gas_density_contrast"]) == 1.0)
    monkeypatch.undo()
    gm.forget_solutions()


# --- the law, re-derived by hand ---------------------------------------------------------------------------------


def test_the_law_rederived_by_hand_on_three_rings(prod):
    """D216's law on three rings of the default galaxy, independent of the modules: f_m and ε are computed here
    from the **published** ``epicyclic_frequency``, ``disc_surface_density``, pitch, amplitudes, phases and the
    bar's taper with this file's arithmetic - no function of ``pattern``, ``gas_pattern`` or ``gas_response`` -
    and the model's ring is held to the equation by two roads the module does not take: a dense Newton on the
    same cells (agreement to rounding), and the differential equation itself through a spectral derivative (to
    the cells' second-order error).

        R kpc     Ω       κ       X         ε         f_2 … f_6 (the untapered forcing)             1 − taper
        4.0125    59.942  91.930  4.26101   0.069486  0.23897 0.59227 0.78969 0.98712 1.04999   0.29664
        7.9875    30.895  41.442  7.92860   0.077433  0       0.25498 0.45908 0.57385 0.68861   0.99602
        10.0125   23.905  30.879  12.00573  0.082903  0       0       0.23099 0.45286 0.56434   1.00000

    X(7.99 kpc) = 7.93 is D215's hand anchor, and Ω and κ there are the probe's 30.9 and 41.4. At every ring the
    **published field** is held to the composition written out here: the mean over each grid cell's azimuth, on the ring, of
    g = w_arm s + w_bar L - the hand's ring integrated over the cell by the trapezoid rule on its own breakpoints,
    and the lane field L the same way in the bar's frame (gate G3 item 4; S58, D217 item 6: until S58 the bar's
    term was 1 + B cos 2(φ − φ_bar), by its own integral; L is re-derived by hand in ``tests/test_bar.py``). At
    4 kpc, inside the bar's reach, the bar's term carries 0.70 of the weight. **S59 (D218 items 1, 4): the cell's
    extent in χ is its φ edges less Φ(R), the winding in seeded segments** - laid here by hand from the published
    segment rows, the published pitch and the published anchor (``hand_winding``) - where until S59 it was
    ln R · cot p; ε and f keep the published ``pitch_angle`` ("geometry only"), so the table above is unmoved to
    every figure, and the bar's angle is ln a · cot p as it was. The spectral residual of the
    differential equation reads 6.8e-4, 9.1e-5 and 3.8e-5 on the three rings: the cells' second-order error
    (S58: the first was 4.8e-4 - at 4 kpc the two-armed mode is on the bar's axis now, θ₂ = 0, another sum of the
    same five forcings; the outer two rings carry no two-armed mode and are the rings they were)."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    assert c["G"] == pytest.approx(G_HAND, rel=1e-9) and c["GAS_DISPERSION"] == SOUND_SPEED_HAND
    o = template_run(prod, "milky_way")
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    assert edges[0] == 0.0 and edges[-1] == pytest.approx(2.0 * math.pi, rel=1e-15) and edges.size == 361
    kappa, sigma, v = (np.asarray(F[k], dtype=float) for k in ("epicyclic_frequency", "disc_surface_density", "circular_velocity"))
    assert o.decls["disc_surface_density"].unit == "Msun/pc2" and o.decls["epicyclic_frequency"].unit == "km/s/kpc"
    pitch = math.radians(float(F["pitch_angle"]))
    a_bar, B = float(F["bar_half_length"]), float(F["bar_contrast"])
    theta = [float(F[n]) for n in pt.PHASE_FIELDS]
    published = np.asarray(F["gas_density_contrast"])
    gp = shape_of(model, o)
    n = gr.CELLS
    assert n == 1440
    h = 2.0 * math.pi / n
    chi = -math.pi + (np.arange(n) + 0.5) * h
    for radius, omega_want, kappa_want, x_want, eps_want, f_want, weight_want, ode_want in (
        (4.0125, 59.942, 91.930, 4.26101, 0.069486, (0.23897, 0.59227, 0.78969, 0.98712, 1.04999), 0.29664, 6.83e-4),  # S58 (D217): was 4.85e-4
        (7.9875, 30.895, 41.442, 7.92860, 0.077433, (0.0, 0.25498, 0.45908, 0.57385, 0.68861), 0.99602, 9.1e-5),
        (10.0125, 23.905, 30.879, 12.00573, 0.082903, (0.0, 0.0, 0.23099, 0.45286, 0.56434), 1.00000, 3.8e-5),
    ):
        i = int(np.argmin(np.abs(R - radius)))
        Ri = float(R[i])
        assert Ri == pytest.approx(radius, abs=1e-9)
        # The frame: the arms turn at the disc's own angular speed, published as a statement (and read by nothing).
        assert float(np.asarray(F["arm_pattern_speed"])[i]) == float(v[i]) / Ri == pytest.approx(omega_want, abs=1e-3)
        x = float(kappa[i]) ** 2 * Ri / (2.0 * math.pi * G_HAND * float(sigma[i]) * 1.0e6)  # Σ per pc² → per kpc²
        eps = SOUND_SPEED_HAND / (float(kappa[i]) * Ri * math.sin(pitch))
        taper = math.exp(-((Ri / a_bar) ** 4))
        untapered = [float(np.asarray(F[pt.amplitude_field(m)])[i]) / (1.0 - taper) for m in (2, 3, 4, 5, 6)]
        f = [m * a / (x * math.sin(pitch)) for m, a in zip((2, 3, 4, 5, 6), untapered)]
        assert float(kappa[i]) == pytest.approx(kappa_want, abs=1e-3) and x == pytest.approx(x_want, abs=2e-5), radius
        assert eps == pytest.approx(eps_want, abs=2e-6) and 1.0 - taper == pytest.approx(weight_want, abs=2e-5), radius
        assert f == pytest.approx(f_want, abs=2e-5), radius
        # The module's own f and ε are these (its arithmetic goes through the unit amplitudes: equal to rounding).
        assert gp.forcing_amplitudes()[i].tolist() == pytest.approx(f, rel=1e-12, abs=1e-15)
        assert float(gp.epsilon()[i]) == pytest.approx(eps, rel=1e-13)
        forcing = sum(f_m * np.cos(m * chi - t) for m, f_m, t in zip((2, 3, 4, 5, 6), f, theta))
        # Road one: the dense Newton on the same cells (measured: 1e-13, 1e-14 and 7e-15 apart).
        by_hand, steps = hand_newton(forcing, eps)
        model_ring = gp.profiles[i]
        assert steps <= 12 and float(np.abs(model_ring - by_hand).max()) < 1e-9, (radius, steps, float(np.abs(model_ring - by_hand).max()))
        assert float(np.abs(model_ring / by_hand - 1.0).max()) < 1e-8, radius  # in the trough too, where s is 1e-6
        assert abs(float(model_ring.sum()) / n - 1.0) < 1e-12 and model_ring.min() > 0.0
        # Road two: the differential equation, ε² (ln s)″ = s − 1 − g, the second derivative taken spectrally. What
        # is left is the cells' second-order error, ε² h²/12 max|(ln s)⁗|: pinned as read.
        log_s = np.log(model_ring)
        k = np.fft.rfftfreq(n, d=1.0 / n)
        second = np.fft.irfft(-(k**2) * np.fft.rfft(log_s), n=n)
        ode = eps**2 * second - (model_ring - 1.0 - forcing)
        assert float(np.abs(ode).max()) == pytest.approx(ode_want, rel=0.03), (radius, float(np.abs(ode).max()))
        # The published field, at the grid's own cells: the hand's ring averaged over each cell's χ - the cell's φ
        # edges less the winding at the ring's radius - weighed by 1 − taper, and the bar's own term, averaged over
        # the same cell, by the taper. S57 (D216 G3): was the hand's ring read at each cell's centre.
        # S59 (D218 items 1, 4): was `winding = ln R / tan(pitch)`. The ring is turned by the winding in seeded
        # segments, laid here by hand from the published rows; ε and f above keep the disc's own pitch, and the
        # bar's angle is ln a · cot p as it was (the winding is anchored on it).
        winding, bar_angle = float(hand_winding(F, np.array([Ri]))[0]), math.log(a_bar) / math.tan(pitch)
        lo, hi = edges[:-1], edges[1:]
        ring = hand_cell_means(by_hand, lo - winding, hi - winding)
        # S58 (D217 item 6): was `bar = the cosine's own integral; composed = (1 − taper) ring + taper (1 + B bar)`.
        lanes = hand_cell_means(gp.lanes[i], lo - bar_angle, hi - bar_angle)
        composed = (1.0 - taper) * ring + taper * lanes
        assert float(np.abs(published[i] - composed).max()) < 1e-11, (radius, float(np.abs(published[i] - composed).max()))
        assert published[i].min() >= taper * float(gp.lanes[i].min()) - 1e-14 and abs(float(published[i].sum()) / 360.0 - 1.0) < 1e-13
        assert abs(float(lanes.mean()) - 1.0) < 1e-13 and float(gp.lanes[i].min()) == pytest.approx(1.0 / (1.0 + 1.6 * footprint_share(Ri, a_bar)), abs=1e-12)
    # Inside the bar's reach the two terms are both there: at 4 kpc the bar carries 0.70 of the weight.
    # S57 (D216 G3): was (2.0112, 0.5010), the centre samples. S58 (D217): was (2.0108, 0.5010) with the cosine bar;
    # with the lanes - a base of 0.674 on this ring and a lane of 6.87 - and θ₂ = 0, (4.869, 0.4738).
    # S59 (D218): was (4.869, 0.4738) - the response on this ring is turned by the winding's segments, and its crest
    # meets the lane's at another angle: (4.990, 0.4738).
    i = row(o, 4.0125)
    assert float(published[i].max()) == pytest.approx(4.990, abs=2e-3) and float(published[i].min()) == pytest.approx(0.4738, abs=1e-3)


def test_the_forcing_carries_the_saturation_by_hand_on_the_most_saturated_seed(prod):
    """Gate G3 item 3: "A_m is the stellar field's actual cosine amplitude on the ring (published over (1 − taper)),
    the saturation in it, because the gas answers the stars that exist" - the forcing is the saturated one, as
    built. The hand test it owes, on the suite's most saturated pattern seed and from the published fields alone.

    **The most saturated suite seed is ``ngc_4414`` at pattern seed 28, its smallest saturation 0.572.** Over the
    suite's seeds (sixty pattern seeds, each template's inputs) none is smaller (the Milky Way template's is 0.643,
    at the same seed). Its arm amplitude draws 0.786; 124 of its rings are saturated, from the innermost to 9.3 kpc.
    Two of them are read: the most saturated ring of all (4.91 kpc) and the most saturated one at or beyond 6.5 kpc
    (6.56 kpc). On each: the published amplitudes sum to 1 to rounding - that is what saturated means in an
    unbarred galaxy, whose bar's depth is 0 and whose taper is 0 on every ring; f_m = m A_m(published)/(X sin p),
    by this file's arithmetic, is the stage's forcing to 1e-15; and this file's dense Newton on that forcing is the
    stage's profile to 1e-10. The unsaturated amplitude A √gain would force 1/0.57 times harder: it is not what the
    stage uses.

    **S58 (D217 item 3): the galaxy is unbarred** (``ngc_4414``'s pin). Until S58 it had a bar: its smallest
    saturation read 0.574, at 5.36 kpc under a taper of 4e-3, 83 of its rings were saturated (3.1 to 9.3 kpc - the
    taper kept the inner rings' modes small), a saturated ring's amplitudes summed to 1 − B·taper with B = 0.410,
    and the forcing took the taper back out. With no bar the modes run to the centre at their whole amplitude and
    saturate there too. A saturated ring of a *barred* galaxy - the amplitudes summing to 1 less the body's depth -
    is read by hand in ``tests/test_bar.py``.

    **S59 (D218 item 6): the galaxy is at the template's pinned pitch, 28.9 degrees** - not the 7.615 degrees this
    pattern seed draws. The saturation is the amplitudes' law and reads no pitch: the seed, its 0.572, its 124
    rings and the two rings read are the ones they were. The forcing and ε go as 1/sin p, so each is 0.2742 of
    what it was (sin 7.615° / sin 28.9°), and the response is a gentler one: at 4.91 kpc Σf 1.604, ε 0.0398, s
    from 0.069 to 2.36; at 6.56 kpc Σf 1.222, ε 0.0456, s from 0.162 to 2.13. What is tested holds as it did: the
    published pitch gives the stage's f and ε by this file's arithmetic, and the saturation is in them."""
    model = prod[0].get(DEFAULT_MODEL)
    lowest = min(
        (float(np.min(run(model, {**templates.overrides(templates.TEMPLATES[t]), "pattern_seed": seed, "texture_seed": 0},
                          only=("arm_saturation",)).fields["arm_saturation"])), t, seed)
        for t in TEMPLATES for seed in range(60))
    # S58 (D217): was 0.5744 (the same seed, with a bar's taper on its inner rings).
    assert lowest[1:] == ("ngc_4414", 28) and lowest[0] == pytest.approx(0.5720, abs=2e-4)
    given = {**templates.overrides(templates.TEMPLATES["ngc_4414"]), "pattern_seed": 28, "texture_seed": 0}
    o = run(model, given, only=PATTERN_FIELDS + ("bar_contrast",))
    F, R = o.fields, o.grid.R
    gp = shape_of(model, o)
    saturation = np.asarray(F["arm_saturation"], dtype=float)
    kappa, sigma = (np.asarray(F[k], dtype=float) for k in ("epicyclic_frequency", "disc_surface_density"))
    pitch = math.radians(float(F["pitch_angle"]))
    A = float(F["arm_contrast"])
    # S59 (D218 item 6): was (7.615, 0.7859) - the pitch is the template's pin; the draw is published beside it.
    assert (math.degrees(pitch), A) == pytest.approx((28.9, 0.7859), abs=2e-3)
    assert float(run(model, given, only=("pitch_angle_drawn",)).fields["pitch_angle_drawn"]) == pytest.approx(7.615, abs=2e-3)
    # S58 (D217): was `B == 0.4101` and a taper exp(−(R/a)⁴) on every ring; the draw is made and not published.
    assert math.isnan(float(F["bar_half_length"])) and math.isnan(float(F["bar_contrast"])) and not gp.barred
    theta = [float(F[n]) for n in pt.PHASE_FIELDS]
    # S58 (D217): was 83 rings, 3.1125 to 9.2625 kpc.
    assert int((saturation < 1.0).sum()) == 124 and (R[saturation < 1.0].min(), R[saturation < 1.0].max()) == pytest.approx((0.0375, 9.2625), abs=1e-6)
    most = int(np.argmin(saturation))
    far = np.flatnonzero(R >= 6.5)
    outside = int(far[np.argmin(saturation[far])])
    n = gr.CELLS
    chi = -math.pi + (np.arange(n) + 0.5) * (2.0 * math.pi / n)
    read = {}
    for i in (most, outside):
        Ri = float(R[i])
        published = [float(np.asarray(F[pt.amplitude_field(m)])[i]) for m in (2, 3, 4, 5, 6)]
        # Saturated: the modes' amplitudes add up to 1 exactly - to rounding (no bar: nothing is taken off the 1).
        assert saturation[i] < 1.0 and sum(published) == pytest.approx(1.0, rel=4e-16, abs=0.0), Ri
        x = float(kappa[i]) ** 2 * Ri / (2.0 * math.pi * G_HAND * float(sigma[i]) * 1.0e6)
        eps = SOUND_SPEED_HAND / (float(kappa[i]) * Ri * math.sin(pitch))
        f = [m * a / (x * math.sin(pitch)) for m, a in zip((2, 3, 4, 5, 6), published)]
        stage = gp.forcing_amplitudes()[i]
        assert stage.tolist() == pytest.approx(f, rel=1e-15, abs=0.0), (Ri, (stage / np.array(f) - 1.0).tolist())
        assert float(gp.epsilon()[i]) == pytest.approx(eps, rel=1e-15)
        forcing = sum(f_m * np.cos(m * chi - t) for m, f_m, t in zip((2, 3, 4, 5, 6), f, theta))
        by_hand, steps = hand_newton(forcing, eps)
        ring = gp.profiles[i]
        assert float(np.abs(ring - by_hand).max()) < 1e-10 and float(np.abs(ring / by_hand - 1.0).max()) < 1e-8, Ri
        read[i] = (Ri, float(saturation[i]), sum(f), eps, float(ring.max()), float(ring.min()), steps)
        # The unsaturated amplitude, A √gain (the saturation taken back out), is another forcing by 1/saturation.
        carried = np.array(f) > 0.0
        unsaturated = np.array(f)[carried] / float(saturation[i])
        assert carried.sum() >= 3 and float(np.abs(stage[carried] / unsaturated - 1.0).max()) == pytest.approx(1.0 - float(saturation[i]), rel=1e-12)
    # The two rings, as read: R, the saturation; the forcing's sum, ε, the crest and the trough of s.
    # 4.91 kpc: 0.572; Σf 5.85, ε 0.145, s from 4.4e-5 to 5.13. 6.56 kpc: 0.613; Σf 4.46, ε 0.166, s from 9.1e-3 to
    # 4.21. S58 (D217): were 5.36 kpc (0.574; 5.44, 0.151, 4.3e-4 to 4.83) and 6.79 kpc (0.636; 4.31, 0.169, 9.0e-3
    # to 4.12) - the rings a tapered galaxy saturated most.
    # S59 (D218 item 6): were (5.850, 0.1451, 5.130, 4.38e-5) and (4.456, 0.1664, 4.205, 9.14e-3), at the drawn
    # pitch of 7.615 degrees; Σf and ε are sin 7.615°/sin 28.9° = 0.2742 of those at the pinned 28.9.
    assert math.sin(math.radians(7.615)) / math.sin(math.radians(28.9)) == pytest.approx(0.2742, abs=1e-4)
    assert read[most][:2] == pytest.approx((4.9125, 0.5720), abs=2e-4)
    assert read[most][2:6] == pytest.approx((1.6041, 0.03979, 2.3649, 6.936e-2), rel=2e-3)
    assert read[outside][:2] == pytest.approx((6.5625, 0.6132), abs=2e-4)
    assert read[outside][2:6] == pytest.approx((1.2219, 0.04563, 2.1300, 0.16190), rel=2e-3)


def test_one_weak_mode_is_the_linear_response_and_a_lone_mode_has_no_offset():
    """Two anchors on a made-up disc, with the arithmetic written here. A weak mode's response is the linear one,
    s − 1 = f/(1 + m² ε²) cos(mχ − θ) - so f and ε reach the solver as the law writes them, sign and phase
    included. And **the offset is zero for a lone mode, exactly, by the equation's symmetry** (D210 ruling 3, D216
    item 12; gate G3 item 7): one mode's response is even about the mode's crest at any amplitude."""
    R = DEFAULT.build().R
    i = int(np.argmin(np.abs(R - 8.0)))
    m, theta, arm, pitch = 4, 0.7, 0.4, 13.5
    weak = one_mode(m, strength=0.01, phases=(0.0, 0.0, theta, 0.0, 0.0), arm=arm, pitch=pitch)
    kappa, sigma = math.sqrt(2.0) * 220.0 / R[i], 50.0 * math.exp(-(R[i] - 8.0) / 2.6)
    sin_p = math.sin(math.radians(pitch))
    x = kappa**2 * R[i] / (2.0 * math.pi * G_HAND * sigma * 1.0e6)
    f = m * arm * 0.01 / (x * sin_p)
    eps = SOUND_SPEED_HAND / (kappa * R[i] * sin_p)
    assert (float(weak.forcing_amplitudes()[i, 2]), float(weak.epsilon()[i])) == pytest.approx((f, eps), rel=1e-12)
    chi = gr.cell_centres()
    linear = f / (1.0 + m * m * eps * eps) * np.cos(m * chi - theta)
    departure = float(np.abs(weak.profiles[i] - 1.0 - linear).max())
    # f = 0.0077 here; what is left of the linear response is second order in it (measured 2.4e-5: about f²/2).
    assert f == pytest.approx(0.00768, abs=1e-5) and departure < f * f
    # Symmetry about the crest, at full strength: phase 0 puts a crest of the four on the edge between cells 719
    # and 720 (χ = 0), and the response is even about it.
    strong = one_mode(m, strength=1.0, arm=arm, pitch=pitch)
    s = strong.profiles[i]
    assert float(s.max()) > 1.5 and int(np.argmax(s)) in (0, 1439, 359, 360, 719, 720, 1079, 1080)
    assert float(np.abs(s[:720][::-1] - s[720:]).max()) < 1e-10
    assert s[719] == pytest.approx(float(s.max()), rel=1e-12) and s[720] == pytest.approx(float(s.max()), rel=1e-12)
    # And where the crests are: at χ = θ/m (and every quarter turn from it) for a phase θ, to the cell.
    turned = one_mode(m, strength=1.0, phases=(0.0, 0.0, theta, 0.0, 0.0), arm=arm, pitch=pitch).profiles[i]
    away = (float(chi[int(np.argmax(turned))]) - theta / m) % (2.0 * math.pi / m)
    assert min(away, 2.0 * math.pi / m - away) <= 2.0 * math.pi / gr.CELLS


def crest_separation(gp: GasPattern) -> np.ndarray:
    """Per grid ring, in solver cells: the cell of the tallest crest of s minus the cell of the tallest crest of
    the stellar modes' sum, wrapped to (−720, 720]. Positive: the gas's crest at the larger χ. 0 on a ring that
    carries no mode (both are flat)."""
    d = (gp.profiles.argmax(axis=1) - gp.stellar_sum().argmax(axis=1)) % gr.CELLS
    return np.where(d > gr.CELLS // 2, d - gr.CELLS, d)


@pytest.mark.parametrize("template", TEMPLATES)
def test_with_several_modes_the_two_crests_are_cells_apart_as_read(prod, template):
    """D216's prediction "offset 0 on every ring", as the record is worded since gate G3's follow-up: "zero for a
    lone mode, exactly; with several modes, within one solver cell (0.25 deg) on the Milky Way template and up to
    about a degree on ngc_4414 - the mode-by-mode weighting, measured, not ruled; no offset is put in and none is
    published". Read here on the solver's own cells, ring by ring: the cell of the tallest crest of s minus the
    cell of the tallest crest of the stellar modes' sum, **signed** - positive is the gas's crest at the larger χ.

    **The Milky Way template (as read since S58, θ₂ = 0): within one solver cell on 50 of 53 rings over 6-10 kpc
    (three read two cells, half a degree) and on 103 of the 165 rings that carry a mode; 53 rings read two cells
    and two read three; and on two (12.1 and 12.2 kpc, where the six-armed mode is all but alone and six nearly
    equal crests stand) the gas's tallest crest is another arm's. ``ngc_4414``: up to 5 cells (1.25 degrees) over
    6-10 kpc and 7 at most over the disc; within one cell on 37 of its 133 rings.** (Until S58, with the
    two-armed mode's phase a draw: within one cell on 53 of 53 and on 161 of 165, two rings at two cells.)

    **The sign: both sides of the stellar crest, in both templates.** Milky Way, 6-10 kpc: +1 cell on 49 rings,
    +2 on 3 and the same cell on 1 - one side over that band - but over the disc −2 or −1 on 12 rings (every one
    inside 0.9 kpc), 0 on 30, +1 on 66, +2 on 53, +3 on 2. ``ngc_4414``, 6-10 kpc: −5 to +1 (27 rings at the smaller χ, 20 on the same cell,
    6 at the larger); over the disc −7 to +7, 95 rings at the smaller χ, 22 the same, 16 at the larger. So the
    separation is no displacement to one side of the arm: its sign turns with radius and with the galaxy, as the
    modes' weights do. (Over the suite's 240 seeded galaxies the two sides are met about equally: the gate's test
    on every seed counts them.)

    **S59 (D218).** The separation is read on the solver's own cells, in χ, and the winding's segments turn the gas
    and the stars of a ring together: the Milky Way's counts are the ones above, to the ring. **``ngc_4414`` is read
    at its pinned pitch, 28.9 degrees (item 6), and is another response** - ε and f both 0.51 of what they were:
    over 6-10 kpc still −5 to +1 (26 rings at the smaller χ, 17 on the same cell, 10 at the larger); over the disc
    −10 to +1 among the rings within ten cells - 101 at the smaller χ, 17 the same, 10 at the larger - within one
    cell on 29 of its 133; and **on five of its six innermost rings (0.11-0.41 kpc) the two crests are 11 to 17
    cells apart (2.75 to 4.25 degrees)**, all at the smaller χ - the rings outside them read −5 to −10 inside
    6 kpc, and these run the same way on inward, past the ten-cell line this count draws. Until S59 (the drawn
    14.33 degrees): 6-10 kpc −5 to +1 (27 / 20 / 6), the disc −7 to +7 (95 / 22 / 16), within one cell on 37, none
    past ten cells. Both sides still, over the disc."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R = o.grid.R
    gp = shape_of(model, o)
    signed = crest_separation(gp)
    carries = np.flatnonzero(gp.carries)
    band = collections.Counter(int(signed[i]) for i in carries if 6.0 <= R[i] <= 10.0)
    same_arm = collections.Counter(int(signed[i]) for i in carries if abs(signed[i]) <= 10)
    want = {
        # S58 (D217 item 9): was band={0: 5, 1: 48}, disc={-1: 41, 0: 59, 1: 61, 2: 2}, within_one=161, most=(1, 2).
        # With the two-armed mode on the bar's axis the modes' sum is another on every ring that carries it (inside
        # about 6.5 kpc): the gas's tallest crest is two cells from the stars' on 53 rings and three on 2, and on
        # the smaller-χ side only inside 0.9 kpc. `ngc_4414`, whose phases are the draws they were, is unmoved.
        "milky_way": dict(band={0: 1, 1: 49, 2: 3}, disc={-2: 5, -1: 7, 0: 30, 1: 66, 2: 53, 3: 2}, other_arm=2, within_one=103, most=(2, 3)),
        # S59 (D218 item 6): `ngc_4414`'s were band={-5: 2, -4: 4, -3: 2, -2: 13, -1: 6, 0: 20, 1: 6}, other_arm=0,
        # within_one=37, most=(5, 7), disc={-7: 28, -6: 19, -5: 14, -4: 7, -3: 4, -2: 16, -1: 7, 0: 22, 1: 8, 2: 1,
        # 3: 4, 4: 1, 5: 1, 7: 1} - at the drawn pitch; these are the response at the pinned 28.9 degrees. Its five
        # rings past ten cells (`other_arm`, by this count's line) are 11-17 cells apart, at 0.11-0.41 kpc.
        "ngc_4414": dict(band={-5: 2, -4: 6, -3: 3, -2: 13, -1: 2, 0: 17, 1: 10}, other_arm=5, within_one=29, most=(5, 10),
                         disc={-10: 3, -9: 34, -8: 17, -7: 11, -6: 6, -5: 6, -4: 6, -3: 3, -2: 13, -1: 2, 0: 17, 1: 10}),
    }[template]
    print(f"{template}: signed separation in solver cells, 6-10 kpc {dict(sorted(band.items()))}; the disc {dict(sorted(same_arm.items()))}")
    assert dict(band) == want["band"] and sum(band.values()) == 53
    assert dict(same_arm) == want["disc"] and carries.size - sum(same_arm.values()) == want["other_arm"]
    assert sum(n for d, n in same_arm.items() if abs(d) <= 1) == want["within_one"]
    assert (max(abs(d) for d in band), max(abs(d) for d in same_arm)) == want["most"]
    # both sides of the stellar crest over the disc, in both templates
    assert min(same_arm) < 0 < max(same_arm)
    # the Milky Way's inner disc sits on the other side from its mid disc
    if template == "milky_way":
        assert all(R[i] < 0.9 for i in carries if signed[i] < 0) and min(band) == 0  # S58 (D217): was `R[i] < 6.0 ... == -1`


# --- the interpolation of the point function, in χ and in R (D216 item 9; gate G3 item 5) -----------------------


def midpoint_error(s: np.ndarray) -> np.ndarray:
    """Per ring, how far the linear interpolant is from the profile midway between two cell centres: the profile
    there by its own trigonometric series (a half-cell shift of its Fourier coefficients - the response is smooth
    and its spectrum has fallen to rounding well under the cells' Nyquist number, which the caller checks)."""
    n = s.shape[1]
    spectrum = np.fft.rfft(s, axis=1)
    k = np.arange(spectrum.shape[1])
    midway = np.fft.irfft(spectrum * np.exp(1j * math.pi * k / n)[None, :], n=n, axis=1)
    return np.abs(0.5 * (s + np.roll(s, -1, axis=1)) - midway).max(axis=1)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_interpolation_errors_are_pinned_as_measured(prod, template):
    """Gate G3 item 5: "1440 cells stand. Pinned as measured: s 3.5e-4 beyond 6 kpc, 1.2e-3 inside the bar's
    reach (≤ 1.2e-5 of the field there as the gate read it; 1.45e-5 for `ngc_4414` as measured below), the point field 3.0e-4, the R-interpolation 5.7e-4 / 7.9e-4."

    **In χ, at the cells' midpoints** (the worst place for the point function: h²/8 · max|s″|). The instrument's
    two hard rings read 1.96e-4 and 1.54e-4. The model's rings, per quantity: **s beyond 6 kpc 3.5e-4 at worst for
    the Milky Way template (9.2e-5 for ``ngc_4414``); s inside the bar's reach 1.2e-3 (1.2e-3)** - where the
    untapered forcing sums to 4-6 and the crest stands at 4-5.7 - **which on that ring is 9.4e-6 (1.4e-5) of the
    field, the arm's weight there being under 1.2 %; the point field 3.0e-4 (2.9e-4) at worst over every ring.**
    (The published field is cell means, whose error is smaller: the test of the cell-averaged field, above.)

    **In R, midway between two grid rings**, against a ring solved there with the law's inputs linear in R
    between the two rings (the amplitudes as ``ArmPattern`` reads them, κ and Σ alike): the blend of the two
    neighbours at the same χ is off by 5.7e-4 (7.9e-4) of the point field at worst, its median 8e-5 (1.7e-4);
    on s itself by 0.22 (0.30), on the innermost pair, where ε falls by a third between two rings and the arm's
    weight is 1e-7. The worst pairs are where a mode enters or leaves between two rings."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R = o.grid.R
    gp = shape_of(model, o)
    s, carries = gp.profiles, gp.carries
    taper = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[0]
    # In χ.
    spectrum = np.abs(np.fft.rfft(s, axis=1)) / s.shape[1]
    assert float(spectrum[:, 480:].max()) < 1e-13  # resolved: nothing left above two thirds of the Nyquist number
    error = midpoint_error(s)
    worst = int(np.argmax(error))
    # S58 (D217): were (1.240e-3, 2.963e-4, 3.486e-4, 9.37e-6) and (1.210e-3, 2.886e-4, 9.232e-5, 1.45e-5). The
    # Milky Way's inner rings are another sum of the modes (θ₂ = 0): s 1.58e-3 at worst (1.76 kpc, the arm's weight
    # 1.3 %), 3.8e-4 of the point field. `ngc_4414` is unbarred: the arm's weight is 1 on every ring, so its field's
    # error is its s's own, 1.2e-3 at 1.16 kpc - no longer hidden under a taper.
    # S59 (D218 item 6): `ngc_4414`'s were (1.210e-3, 1.210e-3, 9.232e-5, 1.210e-3), at the drawn pitch; at the pinned
    # 28.9 degrees its response is gentler and its interpolant closer: 8.9e-4 at worst, at 0.79 kpc. The Milky Way's
    # are the solver's own, in χ: unmoved by the winding's segments.
    want = {"milky_way": (1.5756e-3, 3.809e-4, 4.134e-4, 2.051e-5), "ngc_4414": (8.903e-4, 8.903e-4, 4.359e-5, 8.903e-4)}[template]
    got = (float(error.max()), float((error * (1.0 - taper)).max()), float(error[R > 6.0].max()), float(error[worst] * (1.0 - taper[worst])))
    assert got == pytest.approx(want, rel=0.01), got
    # the worst ring of s: deep inside the bar's reach, where there is a bar (S58: was `< 0.012` for both)
    assert R[worst] < 2.0 and (1.0 - taper[worst] < 0.014 if gp.barred else taper[worst] == 0.0)
    # The interpolant the pattern reads is that linear one: at a midpoint, the mean of the two cells.
    chi = gr.cell_centres() + math.pi / gr.CELLS
    i = int(np.argmax(error * (1.0 - taper)))
    assert np.allclose(gp.response_at(R[i], chi), 0.5 * (s[i] + np.roll(s[i], -1)), rtol=0.0, atol=1e-12)
    # In R.
    pairs = np.flatnonzero(carries[:-1] | carries[1:])
    mid = 0.5 * (R[pairs] + R[pairs + 1])
    unit = np.stack([np.interp(mid, R, u) for u in gp.unit])
    kappa, sigma = np.interp(mid, R, gp.epicyclic), np.interp(mid, R, gp.surface_density)
    f = gr.forcing_amplitudes(pt.ARM_MODES, (gp.arm * unit).T, pt.local_swing_x(mid, kappa, sigma, gp.gravity), gp.sin_pitch)
    solved, _ = gr.solve(gr.forcing(pt.ARM_MODES, f, np.asarray(gp.phases)), gr.epsilon(gp.sound_speed, kappa, mid, gp.sin_pitch))
    weight = 1.0 - pt.bar_terms(mid, gp.pitch_deg, gp.bar_length)[0]
    apart = np.abs(solved - 0.5 * (s[pairs] + s[pairs + 1])).max(axis=1)
    # S58 (D217): were (0.2208, 5.709e-4, 8.45e-5, 6.45) and (0.2966, 7.933e-4, 1.69e-4, 9.525). **`ngc_4414`,
    # unbarred, shows the innermost pair of rings as it is**: between 0.04 and 0.11 kpc ε falls by a third and a
    # point midway reads the blend 0.30 of the ring's mean away from a ring solved there - what a bar's taper had
    # weighed by 1e-7 (the median over its pairs 3.1e-4). The Milky Way's worst pair of s is the same innermost
    # one, 0.32 with θ₂ = 0, under its taper; of its point field 5.8e-4, at 6.45 kpc as before.
    # S59 (D218 item 6): `ngc_4414`'s were (0.2966, 0.2966, 3.055e-4, 0.075); at its pinned pitch the innermost pair
    # reads 0.325 and the median over its pairs 1.0e-4.
    want = {"milky_way": (0.3238, 5.823e-4, 8.59e-5, 6.45), "ngc_4414": (0.3254, 0.3254, 1.031e-4, 0.075)}[template]
    got = (float(apart.max()), float((apart * weight).max()), float(np.median(apart * weight)), float(mid[int(np.argmax(apart * weight))]))
    assert got == pytest.approx(want, rel=0.02), got
    # And what a point between two rings reads is that blend, at its own χ: the point function at the mid radius.
    j = int(np.argmax(apart * weight))
    centres = gr.cell_centres()
    assert np.allclose(gp.response_at(mid[j], centres), 0.5 * (s[pairs[j]] + s[pairs[j] + 1]), rtol=0.0, atol=1e-12)


# --- the predictions, read before they are judged (B4) -----------------------------------------------------------


def test_the_gate_s_predictions_as_measured(prod):
    """D216's predictions for the default galaxy, read on the built model before they were judged. The probe that
    made them forced with the *tapered* amplitudes; the ruling forces with the untapered ones and composes with the
    bar afterwards (item 8), so "outside the bar's reach these are the ruling's" (Fable).

        R kpc     predicted: crest / trough / ratio     as built, s: crest / trough / ratio     published g: crest / trough
        4.0125    1.91 / 0.37  / 1.57                   4.346 / 6.2e-10 / 4.572                 4.990 / 0.474
        5.9625    3.02 / 0.007 / 2.69                   3.552 / 3.0e-5 / 3.384                  3.092 / 0.180
        7.9875    2.79 / 0.018 / 2.56                   2.797 / 0.0171 / 2.571                  2.788 / 0.0211
        10.0125   2.09 / 0.18  / 2.04                   2.090 / 0.1819 / 2.037                  2.089 / 0.1820
        10.9875   1.77 / 0.38  / 1.89                   1.765 / 0.3845 / 1.886                  1.764 / 0.3847
        12.0375   1.20 / 0.81  / 1.28                   1.198 / 0.8114 / 1.281                  1.198 / 0.8117

    (The published g is the cells' means since gate G3: its crest reads a few 1e-4 under the point function's and
    its trough as much over.) **Held** at 10, 11 and 12 kpc, to the figures given. **Held at R₀ to the taper's
    share**: the taper is 0.0040 at 7.99 kpc, the untapered forcing 0.4 % stronger, and the crest and the ratio
    stand 0.3-0.4 % above the probe's (the trough 5 % under: 0.0171 against 0.018). **Not held inside the bar's
    reach, as foreseen**: at 4 and 6 kpc s answers the untapered forcing (its sum 3.7 and 2.8, against the probe's
    1.1 and 2.3) and is far stronger than the probe's; the published field there is s at 0.30 and 0.82 of the
    weight with the bar's own term. Nothing was changed to make a number hold.

    **S58 (D217).** The two rings inside the bar's reach are other rings since S58: the two-armed mode sits on the
    bar's axis (θ₂ = 0, item 9), so s is another sum of the same forcings there (until S58: 4.170 / 4.5e-7 / 3.811
    and 3.480 / 2.5e-4 / 3.208), and the published field blends it with the lanes, not with the stellar bar's
    cosine (2.011 / 0.501 and 3.009 / 0.128). From R₀ out no two-armed mode is carried and s is the ring it was;
    the published trough at R₀ reads 0.0211 where the cosine bar's last 0.4 % of weight left 0.0220.

    **S59 (D218).** s on every ring is the profile it was - the predictions are of s, and each verdict above
    stands to the figure. The published g is s's mean over the grid's cells, and the winding's segments turn each
    ring among them: its crest and trough move in the fourth figure where the ring is the response alone (until
    S59: 2.7870 / 0.0211 at R₀, 2.0888 / 0.1823 at 10 kpc), and at 4 kpc, inside the bar's reach, the response's
    crest meets the lane's at another angle (4.869 until S59).

    Also read: "interarm nearly empty where the forcing's sum exceeds 1 (6-8 kpc)" - held, the trough of s
    4.2e-5 to 0.017 there (2.9e-4 until S58); "Newton at most 8 steps here" - held, 8; "34 on ``ngc_4414``" - the probe's own Newton;
    the instrument takes 9."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, "milky_way")
    R = o.grid.R
    g = np.asarray(o.fields["gas_density_contrast"])
    gp = shape_of(model, o)
    s, ratio = gp.profiles, gp.arm_ratio(MASK_WIDTH)
    f_sum = gp.forcing_amplitudes().sum(axis=1)
    table = (
        # R, predicted (crest, trough, ratio), as built s (crest, trough, ratio), published g (crest, trough), held
        # S57 (D216 G3): the published g were (2.0112, 0.5010), (3.0096, 0.1282), (2.7874, 0.0220), (2.0892, 0.1822),
        # (1.7646, 0.3845), (1.1982, 0.8116) - the point function at the cells' centres; they are the cells' means.
        # S58 (D217): the first two rows were (4.1701, 4.48e-7, 3.8106), (2.0108, 0.5010) and (3.4796, 2.54e-4,
        # 3.2080), (3.0088, 0.1282); the third's published g (2.7868, 0.0220).
        # S59 (D218): the published g were (4.8691, 0.4738), (3.0918, 0.1798), (2.7870, 0.0211), (2.0888, 0.1823),
        # (1.7642, 0.3847), (1.1981, 0.8117) - the cells' means of rings the segments have since turned; s is unmoved.
        (4.0125, (1.91, 0.37, 1.57), (4.3456, 6.23e-10, 4.5718), (4.9899, 0.4738), False),
        (5.9625, (3.02, 0.007, 2.69), (3.5520, 2.98e-5, 3.3837), (3.0919, 0.1798), False),
        (7.9875, (2.79, 0.018, 2.56), (2.7967, 0.0171, 2.5705), (2.7879, 0.0211), True),
        (10.0125, (2.09, 0.18, 2.04), (2.0896, 0.1819, 2.0375), (2.0885, 0.1820), True),
        (10.9875, (1.77, 0.38, 1.89), (1.7648, 0.3845, 1.8857), (1.7643, 0.3847), True),
        (12.0375, (1.20, 0.81, 1.28), (1.1984, 0.8114, 1.2812), (1.1981, 0.8117), True),
    )
    for radius, predicted, built, composed, held in table:
        i = row(o, radius)
        assert float(R[i]) == pytest.approx(radius, abs=1e-9)
        got = (float(s[i].max()), float(s[i].min()), float(ratio[i]))
        assert got[0] == pytest.approx(built[0], abs=2e-3) and got[2] == pytest.approx(built[2], abs=2e-3), radius
        assert got[1] == pytest.approx(built[1], rel=0.03), radius
        assert (float(g[i].max()), float(g[i].min())) == pytest.approx(composed, abs=2e-4), radius
        # Against the prediction: the crest and the ratio within 0.5 % and the trough within 0.006 where it held.
        near = abs(got[0] / predicted[0] - 1.0) < 5e-3 and abs(got[2] / predicted[2] - 1.0) < 5e-3 and abs(got[1] - predicted[1]) < 6e-3
        assert near == held, (radius, got, predicted)
    # The forcing's sum at the six rings: the untapered one (the probe's tapered sums were 1.08, 2.28, 1.97, 1.25, 0.88, 0.25).
    sums = [float(f_sum[row(o, radius)]) for radius, *_ in table]
    assert sums == pytest.approx([3.659, 2.781, 1.976, 1.249, 0.884, 0.247], abs=3e-3)
    # The gaps between the arms, 6 to 8 kpc: nearly emptied, on every ring.
    band = (R >= 6.0) & (R <= 8.0)
    assert np.all(f_sum[band] > 1.0) and float(s[band].min(axis=1).max()) < 0.02 and float(s[band].min()) == pytest.approx(4.24e-5, rel=0.03)  # S58 (D217): was 2.93e-4
    assert gp.diagnostics.worst_steps == 8


# --- the disclosed check: NOT an acceptance row (I3 stands) ------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
def test_disclosed_check_the_ratio_of_means_and_the_width(prod, template):
    """**A disclosed check, not an acceptance row** (D216, the gate's follow-up: "row 38 is not an acceptance row;
    the number 38 is not taken; I3 stands as tested"). Layer on, each template at its default seeds, per ring over
    6-10 kpc. **Disclosed** (D113): the probe printed 2.56 at R₀ and 2.0-2.8 over 6-10 kpc before the check was
    defined, so it cannot be a blind test. The definitions are the gates', fixed before the numbers they judge.

    *The ratio of means*: the mean of s inside the source's arm mask - the share m_eff W/(2π R sin p) of the ring,
    at most a half, where the stellar modes' sum is highest (S56's mask) - over its mean outside, against PHANGS's
    2.73 within its 16th-84th percentiles 1.37-5.79. **The verdict, in gate G3's words (item 7): "a hit, disclosed
    (D113): Milky Way median 2.571, 53 of 53 rings inside 1.37-5.79; ``ngc_4414`` median 1.881 inside, seven of
    its 53 rings (the outer ones) below the 16th percentile, recorded".** Those seven are 9.49 to 9.94 kpc, where
    its arms fade, down to 1.076. Nothing was tuned to land it.

    *The width*, as gate G3 fixed its definition (item 6): "the FWHM of the ring's tallest crest of s as a fraction
    of the period 2π/m of the mode of largest forcing m·A_m - the mode the gas answers most strongly - not a
    tie-break on amplitude", the half level midway between the ring's trough and crest, against the measured 0.17.
    **As read: the Milky Way template 0.466 at the median, 0.428 to 0.481 (0.423 until S58); ``ngc_4414`` 0.512,
    0.479 to 0.526 - a miss on every ring, by 2.52 to 2.83 times and by 2.82 to 3.09 times** (G3 recorded "2.5-3.0× on every ring":
    two and a half to three times, as rounded, on both). Its two named suspects (D216, "Honesty"): the steady pressure-balanced
    response in place of the simulations' converging infall, and the razor-thin forcing of the five- and six-armed
    modes.

    **The other two readings, printed beside it and not the check** (G3: "the build's first reading (0.311) was
    the kindest and is replaced"). The first build read the period of the mode of *largest amplitude*; on 52 of
    the Milky Way's 53 rings (32 of ``ngc_4414``'s) the top amplitude is a tie between arm numbers - the gain is
    whole for each - and it took the lower one, as the probe had: 0.311 at the median, 0.211 to 0.481 (0.422, 0.262
    to 0.508), a miss by 1.2 to 2.8 times. Taking the higher tied arm number: 0.466, 0.352 to 0.481 (0.506, 0.437
    to 0.525). A miss on every ring under every reading.

    **S59 (D218): ``ngc_4414`` is read at its pinned pitch, 28.9 degrees; the Milky Way's check is unmoved to the
    figure** (both measurements are the solver's own, in χ: the winding's segments do not enter them). The gate
    predicted, before the build (D218, "Its predictions"): "ε × 1.96 and f × 0.51 on every ring; the ratio of means
    over 6–10 kpc falls from 1.881 to about 1.4–1.5 and most of its 53 rings fall under PHANGS's 1.37 — 'the
    disclosed check becomes a miss there (recorded, not tuned)'; the width stays near 0.5 of the dominant period".

    **As read** (nothing tuned). *The ratio*: **median 1.406** (1.047 to 1.656) - inside the predicted 1.4-1.5 -
    with **21 of its 53 rings under 1.37** (8.44 to 9.94 kpc, the outer ones, contiguous; they were seven, from
    9.49 kpc) and 32 inside 1.37-5.79. "Most of its 53 rings" is not what is read: 21 is two fifths. **The
    verdict, by this test's own rule - the band's median against PHANGS's 16th-84th percentiles: not a miss. The
    median, 1.406, is inside 1.37-5.79, by 0.036; a hit, disclosed, and a marginal one**, where the gate foresaw a
    miss. Recorded as it reads (by a count of rings it would read the same way: 32 of 53 inside). *The width*:
    **0.550 at the median, 0.494 to 0.606 - wider than the 0.512 it was, not "near 0.5"; a miss on every ring by
    2.91 to 3.57 times** the measured 0.17 (2.82 to 3.09 at the drawn pitch). The other two readings: 0.453 (0.294
    to 0.545) and 0.543 (0.490 to 0.582). And both ε and f are × 0.5121 on every ring, not ε × 1.96
    (``tests/test_segments.py`` holds it; 1.96 is the factor's inverse)."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    assert "GAS_ARM_MASK_WIDTH" not in c and "GAS_ARM_WIDTH" not in c  # the model reads neither: tests/gas_check.py
    assert (MASK_WIDTH, WIDTH_TARGET) == (1.5, 0.17)
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    assert float(F["gas_arm_contrast"]) == pytest.approx(RATIO_TARGET, abs=1e-12)  # the target, and no stage's input
    gp = shape_of(model, o)
    band = (R >= 6.0) & (R <= 10.0) & gp.carries
    ratio, width = gp.arm_ratio(MASK_WIDTH)[band], gp.arm_width()[band]
    # The arm numbers the three readings take on every ring, from the published amplitudes, by this file's arithmetic.
    modes = np.arange(2.0, 7.0)
    amplitudes = np.stack([np.asarray(F[n], dtype=float) for n in pt.AMPLITUDE_FIELDS])
    by_forcing = modes[np.argmax(modes[:, None] * amplitudes, axis=0)]
    lower_tied = modes[np.argmax(amplitudes, axis=0)]
    higher_tied = modes[len(modes) - 1 - np.argmax(amplitudes[::-1], axis=0)]
    tied = int(((amplitudes == amplitudes.max(axis=0)).sum(axis=0) > 1)[band].sum())
    assert np.array_equal(gp.strongest_forcing()[band], by_forcing[band])
    # One measurement - the crest's width in radians - read against three periods.
    readings = {"largest forcing (the check)": width,
                "largest amplitude, the lower arm number on a tie (the first build's)": gp.arm_width(lower_tied)[band],
                "largest amplitude, the higher arm number on a tie": gp.arm_width(higher_tied)[band]}
    assert np.allclose(readings["largest amplitude, the higher arm number on a tie"] / higher_tied[band], width / by_forcing[band], rtol=1e-12)
    for name, values in readings.items():
        print(f"{template}: width by the {name}: median {np.median(values):.3f}, {values.min():.3f} to {values.max():.3f}, "
              f"{values.min() / WIDTH_TARGET:.2f} to {values.max() / WIDTH_TARGET:.2f} times the measured {WIDTH_TARGET}")
    want = {
        # S58 (D217 item 9): the Milky Way's were ratio=(2.5705, 2.0523, 3.1921), width=(0.4660, 0.4229, 0.4807),
        # lower=(0.3107, 0.2114, 0.4807), higher=(0.4660, 0.3524, 0.4807): the medians are the ones they were; the
        # extremes are the band's innermost rings, which still carry a little two-armed power, its phase now the
        # bar's. `ngc_4414`'s are unmoved, as D217 predicted ("unchanged to three figures (1.881 and 0.512)").
        "milky_way": dict(rings=53, ratio=(2.5705, 2.0523, 3.3459), inside=53, tied=52,
                          width=(0.4660, 0.4282, 0.4807), lower=(0.3107, 0.2141, 0.4807), higher=(0.4660, 0.3568, 0.4807)),
        # S59 (D218 item 6): `ngc_4414`'s were ratio=(1.8814, 1.0762, 2.8299), inside=46, width=(0.5120, 0.4790,
        # 0.5260), lower=(0.4218, 0.2620, 0.5083), higher=(0.5061, 0.4366, 0.5253), below from 9.4875 kpc - read at the
        # drawn pitch of 14.33 degrees. At the pinned 28.9 (ε and f both × 0.5121) the gate predicted a median of
        # "about 1.4–1.5" with "most of its 53 rings" under 1.37: read 1.4065, with 21 of 53 under, from 8.4375 kpc.
        "ngc_4414": dict(rings=53, ratio=(1.4065, 1.0468, 1.6564), inside=32, tied=32, below_from=8.4375,
                         width=(0.5496, 0.4939, 0.6062), lower=(0.4532, 0.2940, 0.5448), higher=(0.5428, 0.4900, 0.5822)),
    }[template]
    assert int(band.sum()) == want["rings"] and tied == want["tied"]
    assert (float(np.median(ratio)), float(ratio.min()), float(ratio.max())) == pytest.approx(want["ratio"], abs=2e-3)
    # S57 (D216 G3 item 6): the check's width was (0.3107, 0.2114, 0.4807) and (0.4218, 0.2620, 0.5083) - the reading
    # by the largest amplitude, the lower arm number on a tie, which is kept below as the record of the first build.
    for values, key in zip(readings.values(), ("width", "lower", "higher")):
        assert (float(np.median(values)), float(values.min()), float(values.max())) == pytest.approx(want[key], abs=2e-3), key
    # The verdicts, as read: the median ratio inside PHANGS's percentiles (a hit, disclosed) ...
    # S59 (D218): the rule is the one it was, and `ngc_4414` at its pinned pitch still meets it - by 0.036, where
    # the gate predicted "the disclosed check becomes a miss there". Recorded as read: a hit on the median, 21 of
    # its 53 rings under the 16th percentile (they were 7), fewer than the "most" predicted. Nothing is tuned.
    assert RATIO_LOW <= float(np.median(ratio)) <= RATIO_HIGH
    assert int(((ratio >= RATIO_LOW) & (ratio <= RATIO_HIGH)).sum()) == want["inside"] and np.all(ratio <= RATIO_HIGH)
    below = R[band][ratio < RATIO_LOW]
    # S59 (D218): was `below.min() == 9.4875` - the seven outer rings; at the pinned pitch the 21 outer ones.
    assert below.size == want["rings"] - want["inside"] and (below.size == 0 or (below.min() == pytest.approx(want.get("below_from"), abs=1e-6) and below.max() == pytest.approx(9.9375, abs=1e-6)))
    if template == "ngc_4414":
        assert float(np.median(ratio)) - RATIO_LOW == pytest.approx(0.036, abs=2e-3) and 1.4 <= float(np.median(ratio)) <= 1.5  # the predicted range, held
        assert below.size == 21 and below.size < want["rings"] / 2 and np.all(np.diff(np.flatnonzero(ratio < RATIO_LOW)) == 1)  # "most": not held
    # ... and the width a miss on every ring, under every reading: wider than the measured arm - by 2.5 to 3.1 times
    # as the check reads it.
    for values in readings.values():
        assert np.all(values > WIDTH_TARGET)
    # S59 (D218 item 6): was `... < 3.1` for both. `ngc_4414` at its pinned pitch is wider still - 2.91 to 3.57 times
    # the measured width (it was 2.82 to 3.09), a median of 0.550 where the gate predicted "near 0.5".
    assert 2.45 < float(width.min()) / WIDTH_TARGET and float(width.max()) / WIDTH_TARGET < {"milky_way": 3.1, "ngc_4414": 3.6}[template]
    assert template == "milky_way" or float(width.max()) / WIDTH_TARGET > 3.1

    # The two measurements, re-made here on one ring by this file's arithmetic (a sort and a walk), from the
    # published amplitudes and phases: the module's helpers are these.
    i = row(o, 8.0)
    amplitudes = amplitudes[:, i]
    phases = np.array([float(F[n]) for n in pt.PHASE_FIELDS])
    chi = -math.pi + (np.arange(1440) + 0.5) * (2.0 * math.pi / 1440)
    psi = (amplitudes[:, None] * np.cos(modes[:, None] * chi[None, :] - phases[:, None])).sum(axis=0)
    m_eff = float((modes * amplitudes**2).sum() / (amplitudes**2).sum())
    share = min(0.5, m_eff * MASK_WIDTH / (2.0 * math.pi * float(R[i]) * math.sin(math.radians(float(F["pitch_angle"])))))
    s = gp.profiles[i]
    order = np.argsort(-psi, kind="stable")
    inside = int(round(share * s.size))
    by_hand = float(s[order[:inside]].mean() / s[order[inside:]].mean())
    assert float(gp.arm_ratio(MASK_WIDTH)[i]) == pytest.approx(by_hand, rel=2e-3)  # a whole cell at the cut, against a share of it
    half = 0.5 * (float(s.max()) + float(s.min()))
    top = int(np.argmax(s))
    ahead = next(k for k in range(1, s.size) if s[(top + k) % s.size] <= half)
    behind = next(k for k in range(1, s.size) if s[(top - k) % s.size] <= half)
    strongest = float(modes[int(np.argmax(modes * amplitudes))])  # the mode of largest forcing m·A_m
    cells = (ahead + behind - 1) * (2.0 * math.pi / s.size) / (2.0 * math.pi / strongest)
    assert float(gp.arm_width()[i]) == pytest.approx(cells, abs=1.5 * strongest / s.size)  # whole cells against the crossing


def test_the_check_s_measurements_on_shapes_whose_answers_are_known():
    """The two measuring functions on profiles written here. A cosine's full width at half maximum is half its
    period; a ring that is 3 on a quarter of its cells and 1/3 elsewhere has a ratio of means of 9 in a mask of a
    quarter laid on its high part, and 1 in a mask laid by an order that knows nothing of it; the mask's share is
    m W/(2π R sin p), at most a half."""
    chi = gr.cell_centres()
    for m in (2, 3, 6):
        assert gm.crest_width(1.0 + 0.3 * np.cos(m * chi)) == pytest.approx(0.5 * 2.0 * math.pi / m, rel=1e-4)
    assert gm.crest_width(np.exp(4.0 * np.cos(2 * chi - 1.0))) == pytest.approx(2.0 * math.acos(1.0 + math.log(0.5 * (1.0 + math.exp(-8.0))) / 4.0) / 2.0, rel=1e-4)
    assert math.isnan(gm.crest_width(np.ones(1440)))
    step = np.where(np.abs(chi) < 0.25 * math.pi, 3.0, 1.0 / 3.0)
    assert gm.ratio_of_means(step, np.cos(chi), 0.25) == pytest.approx(9.0, rel=1e-12)
    assert gm.ratio_of_means(step, np.cos(chi), 0.5) == pytest.approx((0.5 * 3.0 + 0.5 / 3.0) / (1.0 / 3.0), rel=1e-12)
    assert gm.ratio_of_means(step, np.cos(8 * chi), 0.5) == pytest.approx(1.0, abs=1e-12)
    # The cell the share cuts is counted by the fraction of it inside: continuous in the share.
    ramp = np.linspace(2.0, 0.0, 1440)
    a, b = gm.ratio_of_means(ramp, ramp, 0.25), gm.ratio_of_means(ramp, ramp, 0.25 + 1e-7)
    assert a != b and abs(a - b) < 1e-5
    share = gm.mask_share(np.array([4.0, 4.0, np.nan]), np.array([8.0, 2.0, 8.0]), 0.25, 1.5)
    assert share[0] == pytest.approx(4.0 * 1.5 / (2.0 * math.pi * 8.0 * 0.25)) and share[1] == 0.5 and math.isnan(share[2])
    # The width's mode is the one of largest forcing m·A_m: with equal amplitudes that is the highest arm number.
    R = DEFAULT.build().R
    unit = np.zeros((5, R.size))
    unit[1:4] = 1.0 / math.sqrt(3.0)  # three, four and five arms at one amplitude: a tie the amplitude cannot break
    assert np.all(synthetic(unit).strongest_forcing() == 5.0)
    unit[1] = 0.9  # m·A: 3 × 0.9 = 2.7 against 5 × 0.577 = 2.89 - still five; at 0.97, 2.91: three
    assert np.all(synthetic(unit).strongest_forcing() == 5.0)
    unit[1] = 0.97
    assert np.all(synthetic(unit).strongest_forcing() == 3.0)


def test_nothing_of_the_ridge_builds_the_field(prod):
    """D216 item 11 (iv): "nothing replaces the amplitude: s is the field; ``gas_arm_contrast`` and S56's mask
    survive only as [the check's] target and definition; ``GAS_ARM_WIDTH`` only as the width miss's target". And
    gate G3 item 7: "the two retired constants leave the model's registry and live in ``tests/`` with their
    sources: a stage may not declare reads it does not make." The model declares neither constant and no stage
    names one; the pattern is built from the law's two constants; no stage requires the ratio; and the retired
    machinery is gone from the module."""
    models, impls_, _ = prod
    model = models.get(DEFAULT_MODEL)
    # S58 (D217 items 7-8): was `== ("G", "GAS_DISPERSION")`. The law's two constants, and the lanes' four: the
    # arcs' curvature, the nuclear ring's radius, the gas inside the footprint over the gas outside, and the lane's
    # width - a declared placeholder. Each is read (`lane_profiles`), so each is declared.
    assert GAS_PATTERN_CONSTANTS == ("G", "GAS_DISPERSION", "BAR_LANE_CURVATURE", "NUCLEAR_RING_RATIO", "BAR_GAS_RATIO", "BAR_LANE_WIDTH")
    assert gm.LANE_CONSTANTS == GAS_PATTERN_CONSTANTS[2:] and not hasattr(gm, "GAS_CHECK_CONSTANTS")
    assert GAS_PATTERN.reads_constants == GAS_PATTERN_CONSTANTS and "gas_arm_contrast" not in GAS_PATTERN_READS
    retired = ("GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH")
    for m in models:
        assert not set(retired) & set(m.constants), m.name
        assert {"GAS_ARM_CONTRAST_GRAND_DESIGN", "GAS_ARM_CONTRAST_OTHER", "G", "GAS_DISPERSION"} <= set(m.constants)
        readers = [sid for _, sid in m.stages if "gas_arm_contrast" in impls_.get(sid).requires + impls_.get(sid).requires_optional]
        assert readers == [], readers
        declaring = sorted(sid for _, sid in m.stages if set(retired) & set(impls_.get(sid).reads_constants))
        assert declaring == [], declaring
        # ... and every stage that places by the gas declares the two the law does read.
        for sid in ("gas_pattern", "clouds", "cloud_texture", "clusters"):
            assert set(GAS_PATTERN_CONSTANTS) <= set(impls_.get(sid).reads_constants), sid
    # They live in tests/, with the values the model held and their sources.
    assert (gas_check.GAS_ARM_WIDTH, gas_check.GAS_ARM_MASK_WIDTH) == (0.17, 1.5)
    assert "[verified: Egusa et al. 2017, MNRAS 465, 460, arXiv:1610.06642" in gas_check.GAS_ARM_WIDTH_SOURCE
    assert "[verified: Querejeta et al. 2021, A&A 656, A133, arXiv:2109.04491" in gas_check.GAS_ARM_MASK_WIDTH_SOURCE
    # The pattern from fields and the law's two constants alone is the pattern the stage published: the same bits.
    o = template_run(prod, "milky_way")
    R, edges = o.grid.R, o.grid["phi"].edges
    c = constants(model)
    lean = compose.gas_pattern(o.fields, R, {k: c[k] for k in GAS_PATTERN_CONSTANTS})
    assert lean.cell_means(R, edges).tobytes() == np.asarray(o.fields["gas_density_contrast"]).tobytes()
    fields = {n: o.fields[n] for n in GAS_PATTERN_READS}
    assert GasPattern.from_fields(fields, R, {k: c[k] for k in GAS_PATTERN_CONSTANTS}).cell_means(R, edges).tobytes() == lean.cell_means(R, edges).tobytes()
    assert GasPattern.from_fields(fields, R, {"G": c["G"]}) is None  # a constant the law reads is missing: no pattern
    # No module of the model names either retired constant in its code (docstrings and comments apart).
    package = Path(gm.__file__).resolve().parents[1]
    named = []
    for path in sorted(package.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                      if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)) and n.body
                      and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings]
        named += [(path.name, name) for name in retired for text in strings if name in text]
        if path.name == Path(gm.__file__).name and path.parent.name == "stages":
            own_tree, own_strings = tree, strings
    assert named == [], named  # not as a key, not in a declaration, not in an about line: the registry does not know them
    assert not any("gas_arm_contrast" in text or "arm_multiplicity" in text or "arm_pattern_speed" in text for text in own_strings)
    for name in ("_Rings", "ridge_value", "kappa_for_width", "mask_means", "pattern_period", "PHASE_CELLS",
                 "HARMONIC_SAMPLES", "RING_MEAN_TOLERANCE", "NEWTON_STEPS", "BISECTION_STEPS"):
        assert not hasattr(gm, name), name
    for name in ("rank", "ridge", "amplitude", "ratio_at", "forcing", "extremes", "ratio", "width", "mask_width"):
        assert not hasattr(GasPattern, name), name
    # Forbidden forms (D216), held by what the code does, read from the syntax tree: nothing is clipped and no error
    # is caught (so no fallback on a ring that did not converge).
    assert [n.attr for n in ast.walk(own_tree) if isinstance(n, ast.Attribute) and n.attr == "clip"] == []
    assert not any(isinstance(n, (ast.Try, ast.ExceptHandler)) for n in ast.walk(own_tree))
    # And nothing reads the frame's field: the flow is 0 by construction, not a difference of two speeds. The one
    # call of the solver hands it the constant 0 as the flow.
    for m in models:
        readers = [sid for _, sid in m.stages if "arm_pattern_speed" in impls_.get(sid).requires + impls_.get(sid).requires_optional]
        assert readers == [] and "arm_pattern_speed" in impls_.get("bar").published_names
    solves = [n for n in ast.walk(own_tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "solve"]
    assert len(solves) == 1 and isinstance(solves[0].args[2], ast.Constant) and solves[0].args[2].value == 0.0 and not solves[0].keywords


def test_the_frame_is_published_as_a_statement(model):
    """``arm_pattern_speed`` = v_c/R on every ring, a derived radial field of the ``bar`` stage whose about line
    says what it is: a statement of the frame, not a measurement (the gate's two conditions)."""
    o = out(model)
    speed = np.asarray(o.fields["arm_pattern_speed"])
    assert speed.tobytes() == (np.asarray(o.fields["circular_velocity"]) / o.grid.R).tobytes()
    d = o.decls["arm_pattern_speed"]
    assert d.unit == "km/s/kpc" and d.axes == ("R",) and d.provenance == "derived" and not d.composed
    assert "A statement of the frame, not a measurement" in d.about and "Nothing computes anything from this field" in d.about
    assert d.name in {x.name for x in BAR.publishes}
    assert float(speed[row(o, 7.9875)]) == pytest.approx(30.90, abs=0.01)  # the probe's table: Ω(7.99 kpc) = 30.9
    # The same with the layer off: a law's field.
    off = run(model, layer=False, only=("arm_pattern_speed",))
    assert np.asarray(off.fields["arm_pattern_speed"]).tobytes() == speed.tobytes()


# --- seeded through the pattern; the ratio a derived target ---------------------------------------------------


def test_the_field_moves_with_the_pattern_seed_and_not_the_world_seed(model):
    """The field is seeded through the pattern's drawn pitch, amplitudes and bar and the layer's phases (graph
    labels it so, D55); the stage itself reads no seed and draws nothing (D210 as amended)."""
    a = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    b = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    c = run(model, {"pattern_seed": 8}, grid=COARSE).fields
    w = run(model, {"pattern_seed": 7, "world_seed": 12345}, grid=COARSE).fields
    t = run(model, {"pattern_seed": 7, "texture_seed": 9}, grid=COARSE, only=("gas_density_contrast",)).fields
    assert np.array_equal(a["gas_density_contrast"], b["gas_density_contrast"])
    assert not np.array_equal(a["gas_density_contrast"], c["gas_density_contrast"])
    assert np.array_equal(a["gas_density_contrast"], w["gas_density_contrast"])
    assert not np.array_equal(a["gas_density_contrast"], t["gas_density_contrast"])  # S56: the phases are the layer's
    assert GAS_PATTERN.reads_seeds == ()
    # S58 (D217 follow-up): was ["seeded"] - the stage's second field, the contrast the star formation law reads.
    assert [d.provenance for d in GAS_PATTERN.publishes] == ["seeded", "seeded"]
    # It moves as the gas's own contrast does; at these defaults (a barred galaxy) the two are not one field.
    name = "star_formation_gas_contrast"
    assert np.array_equal(a[name], b[name]) and np.array_equal(a[name], w[name]) and not np.array_equal(a[name], c[name])
    assert not np.array_equal(a[name], a["gas_density_contrast"])


def test_the_ratio_is_the_derived_class_mean_and_no_draw(model):
    """The check's target is the bar stage's: 2.73 at the defaults (m = 2 inside the swing window, coherence 1),
    and the same under every pattern seed — no residual, since the source's spread is over segments and bins, not
    galaxies (#131)."""
    assert float(out(model).fields["gas_arm_contrast"]) == pytest.approx(2.73, abs=1e-12)
    values = {run(model, {"pattern_seed": s}, grid=COARSE).fields["gas_arm_contrast"] for s in range(6)}
    assert len(values) == 1
    about = out(model).decls["gas_arm_contrast"].about
    assert "the target of a disclosed check" in about and "No stage reads it" in about


# --- one function at points and on the grid ------------------------------------------------------------------


def test_the_point_function_is_one_function_and_the_published_field_is_its_cell_means(model):
    o = out(model)
    gp = shape_of(model, o)
    R, phi, edges = o.grid.R, o.grid.phi, o.grid["phi"].edges
    on_mesh = gp.contrast(R, phi)
    # S57 (D216 G3): was `on_mesh.tobytes() == published` - the first build published these samples. The published
    # field is the cells' means; the point function at a cell's centre is within 1.7e-3 of its cell's mean.
    published = np.asarray(o.fields["gas_density_contrast"])
    assert published.tobytes() == gp.cell_means(R, edges).tobytes() and published.tobytes() != on_mesh.tobytes()
    # S58 (D217): was 1.718e-3; the lanes are a few cells wide inside 3 kpc, and a cell's mean is 1.2e-2 from its centre.
    # S59 (D218): was 1.198e-2 - on a ring the winding's segments have turned, inside the bar's reach (3.79 kpc).
    assert float(np.abs(published - on_mesh).max()) == pytest.approx(1.217e-2, rel=0.02)
    idx = np.array([5, 77, 190, 399]), np.array([0, 91, 180, 359])
    assert np.array_equal(gp.contrast_at(R[idx[0]], phi[idx[1]]), on_mesh[idx])
    assert np.array_equal(gp.contrast_at(R[:, None], phi[None, :]), on_mesh)
    # Points that share a radius unevenly: each is the single point's value.
    radii = np.concatenate([np.full(7, R[100]), np.full(3, R[150])])
    azimuths = np.linspace(0.3, 5.9, 10)
    alone = np.array([gp.contrast_at(np.array([r]), np.array([p]))[0] for r, p in zip(radii, azimuths)])
    assert np.array_equal(gp.contrast_at(radii, azimuths), alone)
    # A cell's mean is the dense average of the point function over the cell (the same measure, G3 item 4).
    i, j = 106, 200
    dense = edges[j] + (np.arange(2000) + 0.5) * (edges[j + 1] - edges[j]) / 2000
    assert float(gp.contrast_at(np.full_like(dense, R[i]), dense).mean()) == pytest.approx(float(published[i, j]), abs=1e-7)


def test_a_point_reads_its_two_rings_at_its_own_winding_phase(model):
    """D216 item 9. At a grid radius a point reads that ring's profile by the instrument's own interpolant, bit
    for bit; between two rings it reads both **at its own χ** - the winding at the point's radius, not at either
    ring's - and blends them linearly in R; beyond the grid it holds the end ring; the taper and the bar's term
    are taken at the point's own radius (since S58 the bar's term is the lane field, read from the two rings at the
    point's own angle from the bar, as s is read at its own winding phase; D217 item 6)."""
    o = out(model)
    gp = shape_of(model, o)
    R = o.grid.R
    s = gp.profiles
    chi = np.random.default_rng(11).uniform(-9.0, 9.0, 500)  # the test's own points, any turn of the ring
    for i in (40, 106, 133, 160):
        assert gp.response_at(R[i], chi).tobytes() == gr.interpolate(s[i], chi).tobytes()
    assert not s.flags.writeable
    k, share = 106, 0.3
    radius = float((1.0 - share) * R[k] + share * R[k + 1])
    got = gp.response_at(radius, chi)
    lower, upper = gr.interpolate(s[k], chi), gr.interpolate(s[k + 1], chi)
    assert np.allclose(got, (1.0 - share) * lower + share * upper, rtol=1e-13, atol=0.0)
    assert np.all(got >= np.minimum(lower, upper) * (1.0 - 1e-15)) and np.all(got <= np.maximum(lower, upper) * (1.0 + 1e-15))
    # The whole contrast at that point, written out: its own taper, its own winding phase, its own bar term.
    phi = chi + 3.0
    # S59 (D218): "its own winding phase" is the winding in seeded segments at the point's own radius - was
    # `pt.bar_terms(np.array([radius]), gp.pitch_deg, gp.bar_length)`, ln R · cot p. The pattern's own, to hold
    # 1e-13 of the value; this file's, from the published rows, is it to 1e-12. The taper and the bar's angle read
    # nothing of the segments.
    taper, phase, bar_angle = pt.bar_terms(np.array([radius]), gp.pitch_deg, gp.bar_length, gp.winding)
    plain = pt.bar_terms(np.array([radius]), gp.pitch_deg, gp.bar_length)
    assert abs(phase[0] - float(hand_winding(o.fields, np.array([radius]))[0])) < 1e-12 and (taper[0], bar_angle) == (plain[0][0], plain[2])
    assert gp.winding is not None and abs(phase[0] - plain[1][0]) > 1e-3  # the segments are in it
    # S58 (D217 item 6): the bar's term was `1 + B cos 2(φ − φ_bar)`; it is the two rings' lane profiles at φ − φ_bar.
    lanes = (1.0 - share) * gr.interpolate(gp.lanes[k], phi - bar_angle) + share * gr.interpolate(gp.lanes[k + 1], phi - bar_angle)
    assert np.allclose(gp.lanes_at(radius, phi - bar_angle), lanes, rtol=1e-13, atol=0.0) and gp.barred
    by_hand = (1.0 - taper[0]) * gp.response_at(radius, phi - phase[0]) + taper[0] * lanes
    assert np.allclose(gp.contrast_at(np.full_like(phi, radius), phi), by_hand, rtol=1e-13, atol=0.0)
    # ... and deep inside the bar, where the lanes carry nearly all the weight: the same composition.
    k_in, deep = 26, float(0.6 * R[26] + 0.4 * R[27])
    t_in, w_in, _ = pt.bar_terms(np.array([deep]), gp.pitch_deg, gp.bar_length, gp.winding)  # S59 (D218): the segments' winding
    assert abs(w_in[0] - float(hand_winding(o.fields, np.array([deep]))[0])) < 1e-12
    inner = (1.0 - t_in[0]) * gp.response_at(deep, phi - w_in[0]) + t_in[0] * (0.6 * gr.interpolate(gp.lanes[k_in], phi - bar_angle) + 0.4 * gr.interpolate(gp.lanes[k_in + 1], phi - bar_angle))
    assert np.allclose(gp.contrast_at(np.full_like(phi, deep), phi), inner, rtol=1e-12, atol=0.0) and t_in[0] > 0.97
    # Beyond the grid: the end rings, held.
    assert gp.response_at(0.0, chi).tobytes() == gr.interpolate(s[0], chi).tobytes()
    assert gp.response_at(99.0, chi).tobytes() == gr.interpolate(s[-1], chi).tobytes()
    # A point's mean round its ring is 1 at any radius: both blends are convex blends of mean-1 profiles.
    dense = (np.arange(14400) + 0.5) * (2.0 * math.pi / 14400)
    for radius in (2.03, 6.511, 8.3, 11.99):
        ring = gp.contrast_at(np.full_like(dense, radius), dense)
        assert float(ring.mean()) == pytest.approx(1.0, abs=1e-12) and ring.min() > 0.0


def test_azimuths_fall_inside_the_sector_and_follow_the_arms(model):
    gp = shape_of(model, out(model))
    u = np.random.default_rng(0).random(20000)
    radius = np.full(u.size, 8.0)
    phi = gp.azimuths(u, radius, 0.0, 2.0 * np.pi, steps=720)
    assert np.all((phi >= 0.0) & (phi <= 2.0 * np.pi))
    # Drawn by the contrast, the clouds sit where it is high: their mean contrast is the ring's mean square, well
    # above 1 — to sampling noise, about 0.5 %.
    ring = np.linspace(0.0, 2.0 * np.pi, 36000, endpoint=False)
    mean_square = float((gp.contrast_at(np.full_like(ring, 8.0), ring) ** 2).mean())
    # S57 (D216): was 1.253 at 12 kpc, the ranked ridge of the six-armed mode alone at half the arm amplitude. The
    # response there is weak (1.021: the crest 1.20); read at 8 kpc instead, where the arms are whole.
    assert mean_square == pytest.approx(1.358, abs=0.005)
    assert float(gp.contrast_at(radius, phi).mean()) == pytest.approx(mean_square, rel=0.02)


def test_the_default_field_s_range_and_its_mean_square(model):
    """The default galaxy's published field as read: its range; at R₀ the crest and the trough; and ⟨g²⟩ - the
    factor a process quadratic in the gas gains from the arms - at R₀ and by gas mass over the disc."""
    o = out(model)
    F, R = o.fields, o.grid.R
    g = np.asarray(F["gas_density_contrast"])
    # S57 (D216): was (0.5336, 3.0688), the ranked ridge's form; the response empties the gaps between the arms.
    # S57 (D216 G3): was (0.01992, 3.09294), the centre samples; the cells' means read (0.01994, 3.09222).
    # S58 (D217): was (0.019943, 3.092221). The largest value is a lane's, at 2.06 kpc; the smallest is where it was
    # (7.69 kpc), a little lower since the bar's last 0.3 % of weight there is the lanes' 1 and not the cosine's.
    # S59 (D218): was (0.018394, 6.664030). The same two places - the lowest cell at 7.69 kpc, the highest a lane's
    # at 2.06 kpc - on rings the winding's segments have turned among the grid's cells.
    assert (float(g.min()), float(g.max())) == pytest.approx((0.018402, 6.678598), abs=2e-5)
    i = row(o, R_SUN)
    # S57 (D216): was crest 3.0592, trough 0.5340 at R0. S57 (D216 G3): was (2.7403, 0.02534) on the centre samples.
    # S58 (D217): was (2.73964, 0.025373) - the cosine bar's 0.33 % of weight at R0 put 0.0007 into the trough.
    # S59 (D218): was (2.73970, 0.024689) - the ring at R0 is the curve it was, its cells' means read at another phase.
    assert (float(g[i].max()), float(g[i].min())) == pytest.approx((2.73884, 0.024605), abs=2e-5)
    # S57 (D216): was 1.603 at R0 and 1.194 by gas mass. S57 (D216 G3): was 1.3443 and 1.1157 on the centre samples.
    assert float((g[i] ** 2).mean()) == pytest.approx(1.34398, abs=2e-5)  # S59: 1.343975, to the pin's tolerance the number it was
    weight = np.asarray(F["gas_surface_density"]) * R
    # S58 (D217): was 1.11562. The lanes: inside the bar the gas is thinned to four tenths of the ring's mean off two
    # narrow lanes at seven times it, so a process quadratic in the gas gains there - 1.312 over the disc by gas mass.
    # S59 (D218): was 1.31200. Inside the bar's reach the turned response meets the lanes at other angles, and the
    # mean square of their sum moves with it: 1.31031.
    assert float(((g**2).mean(axis=1) * weight).sum() / weight.sum()) == pytest.approx(1.31031, abs=2e-5)


# --- what the stage reads, where it sits ---------------------------------------------------------------------


def test_the_stage_reads_no_gas_and_sits_at_checkpoint_three():
    assert GAS_PATTERN.checkpoint == 3 == PATTERN.checkpoint
    # No gas column and no gas ratio: nothing it requires is a gas field.
    assert [n for n in GAS_PATTERN.requires if "gas" in n] == []
    # S57 (D216): was ("gas_arm_contrast", "arm_contrast", *PATTERN_READS). The response reads the stellar modes,
    # their phases, the arm amplitude the taper is taken back out with, and checkpoint 1's disc - and no arm number.
    # S58 (D217 items 6-8): was ("arm_contrast", *PATTERN_READS, ...). Of the bar the gas reads the half-length and
    # the body's footprint (its axis ratio and boxiness) - the lanes are deterministic given the bar - and no longer
    # the stellar bar's amplitude; of the stellar body's own numbers (its share, its profile's exponent) nothing.
    # S59 (D218 items 1, 4): the winding's three fields - the radius it is anchored at and the layer's two segment
    # columns: the geometry of χ, which the response is turned by, and nothing of ε or f.
    assert pt.WINDING_FIELDS == ("arm_winding_anchor_radius", "arm_segment_extent", "arm_segment_pitch_residual")
    assert GAS_PATTERN.requires == GAS_PATTERN_READS == (
        "arm_contrast", "pitch_angle", "bar_half_length", "bar_axis_ratio", "bar_boxiness",
        *pt.AMPLITUDE_FIELDS, *pt.PHASE_FIELDS, "epicyclic_frequency", "disc_surface_density",
        "arm_winding_anchor_radius", "arm_segment_extent", "arm_segment_pitch_residual")  # S59 (D218)
    assert not {"bar_contrast", "bar_mass_share", "bar_profile_index"} & set(GAS_PATTERN_READS) and set(GAS_PATTERN_READS) - set(pt.PATTERN_READS) == {"arm_contrast", "epicyclic_frequency"}
    assert "arm_multiplicity" not in GAS_PATTERN.requires
    assert set(pt.AMPLITUDE_FIELDS) | set(pt.PHASE_FIELDS) <= set(GAS_PATTERN.requires)
    assert GAS_PATTERN.reads_seeds == ()
    # S58 (D217 follow-up): was {"gas_density_contrast"} - beside it the contrast as the star formation law reads
    # it, the lanes' excess spread evenly over the bar's footprint ("the lanes' one unsourced number (the width)
    # must not drive a census"). Its about says what it is and why, and names no constant (rule D5).
    assert [d.name for d in GAS_PATTERN.publishes] == ["gas_density_contrast", "star_formation_gas_contrast"]
    second = GAS_PATTERN.publishes[1]
    assert second.composed and second.neutral == 1.0 and second.axes == ("R", "phi") and second.provenance == "seeded"
    assert "Star formation therefore follows the bar's footprint, not the lanes" in second.about
    assert "a declared placeholder that no source gave" in second.about and "The dust and the cloud census keep the lanes" in second.about
    assert "A composed field: with the randomness layer off it is 1 everywhere" in second.about
    assert not re.search(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b", second.about + GAS_PATTERN.about)
    about = GAS_PATTERN.publishes[0].about
    assert "the mean over its azimuthal cell" in about and "the offset is zero for a lone mode" in about
    assert "at the ring's own radius" in about and "within about a degree of each other over the mid disc, to either side" in about
    # S58 (D217): what the bar's reach holds, and what of it is not sourced.
    assert "two narrow lanes on the bar's leading side" in about and "its width is a declared placeholder that no source gave" in about
    assert "An unbarred galaxy has no lanes" in about and "the stellar bar's own two-fold term" not in about


def test_both_models_run_the_gas_pattern_after_the_pattern(model):
    slots = [slot for slot, _ in model.stages]
    assert dict(model.stages)["gas_pattern"] == "gas_pattern"
    assert slots.index("gas_pattern") == slots.index("pattern") + 1


def test_a_flat_pattern_publishes_ones_and_a_ring_with_no_mode_is_one():
    """S58 (D217): the pattern holds no bar amplitude; "no bar" is a half-length that is not a number (an unbarred
    galaxy: no taper, no lanes), and a bar is its half-length with the lanes' numbers. Until S58 the cases read
    ``bar=0.0`` for no bar and ``bar=0.3`` for the stellar bar's cosine term."""
    nan = float("nan")
    assert one_mode(4, pitch=nan).flat                     # a pitch the mesh could not resolve
    assert one_mode(4, phases=(nan,) * 5).flat             # the layer did not realise the phases
    assert one_mode(4, strength=0.0).flat                  # no mode and no bar
    assert one_mode(4, arm=0.0).flat                       # no arm amplitude and no bar
    assert not one_mode(4).flat and not one_mode(4).barred  # an unbarred galaxy's arms
    assert not one_mode(4, strength=0.0, bar_length=5.2097).flat  # the bar's lanes alone
    assert one_mode(4, bar_length=5.2097, lanes=()).flat   # a bar, and none of the lanes' numbers: unresolved
    assert one_mode(4, bar_length=float("inf")).flat
    # A ring that carries no mode: s = 1 exactly, the solver is not asked, and the field there is the lanes' own.
    grid = DEFAULT.build()
    R, phi, edges = grid.R, grid.phi, grid["phi"].edges
    unit = np.zeros((5, R.size))
    wound = (R >= 3.0) & (R < 10.0)
    unit[2, wound] = 1.0
    gp = synthetic(unit, bar_length=5.2097)
    assert gp.barred and np.array_equal(gp.carries, wound) and np.all(gp.profiles[~wound] == 1.0)
    assert gp.diagnostics.steps.size == int(wound.sum())
    field = gp.contrast(R, phi)
    taper, _, bar_angle = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)
    L = gp.lanes
    assert np.all(L[R >= 5.2097] == 1.0) and L[R < 3.0].max() > 5.0
    inner, beyond = R < 3.0, R >= 10.0
    lanes_at_centres = gr.interpolate(L, np.broadcast_to(phi[None, :] - bar_angle, (R.size, phi.size)))
    assert np.allclose(field[inner], (1.0 - taper[inner, None]) + taper[inner, None] * lanes_at_centres[inner], rtol=1e-14, atol=0.0)
    assert np.all(np.abs(field[beyond] - 1.0) < 1e-15)
    # ... and its cell means there are the lanes' own, averaged over each cell: 1 at 10 kpc and beyond.
    means = gp.cell_means(R, edges)
    cells = gr.sector_mean(L, np.broadcast_to(edges[None, :-1] - bar_angle, (R.size, phi.size)), np.broadcast_to(edges[None, 1:] - bar_angle, (R.size, phi.size)))
    assert np.allclose(means[inner], (1.0 - taper[inner, None]) + taper[inner, None] * cells[inner], rtol=1e-14, atol=0.0)
    assert np.all(np.abs(means[beyond] - 1.0) < 1e-15) and float(np.abs(means.sum(axis=1) / means.shape[1] - 1.0).max()) < 1e-13
    assert np.all(np.isnan(gp.arm_ratio(1.5)[~wound])) and np.all(np.isnan(gp.arm_width()[~wound]))
    bar_only = one_mode(4, strength=0.0, bar_length=5.2097)
    assert bar_only.diagnostics is None and np.all(bar_only.profiles == 1.0)
    alone = bar_only.cell_means(R, edges)
    assert float(np.abs(alone.sum(axis=1) / alone.shape[1] - 1.0).max()) < 1e-13 and alone.max() > 5.0 and alone.min() > 0.38
    # The unbarred pattern of the same modes: its response alone, on every ring - no taper, no lanes.
    free = synthetic(unit)
    assert not free.barred and free.profiles.tobytes() == gp.profiles.tobytes()
    winding = pt.bar_terms(R, free.pitch_deg, free.bar_length)[1]
    assert np.all(pt.bar_terms(R, free.pitch_deg, free.bar_length)[0] == 0.0)
    assert free.cell_means(R, edges)[wound].tobytes() == gr.sector_mean(free.profiles[wound], edges[None, :-1] - winding[wound, None], edges[None, 1:] - winding[wound, None]).tobytes()
    assert np.all(free.cell_means(R, edges)[~wound] == 1.0) and np.all(free.contrast(R, phi)[~wound] == 1.0)
    assert free.sector_means(20.0, edges).shape == (edges.size - 1,) and np.all(free.sector_means(20.0, edges) == 1.0)
    with pytest.raises(ValueError, match="5 modes"):
        synthetic(unit[:3])
    with pytest.raises(ValueError, match="epicyclic frequency and surface density"):
        GasPattern(R, unit, (0.0,) * 5, 0.4, 13.5, 5.2, np.ones(3), np.ones(R.size), G_HAND, SOUND_SPEED_HAND)
    # Fields that hold no pattern give none.
    assert GasPattern.from_fields({"bar_contrast": 0.3}, R, {"G": G_HAND, "GAS_DISPERSION": 6.0}) is None


def test_the_two_weights_sum_to_one_or_the_composition_is_refused():
    """D216 item 8: "w_arm + w_bar = 1 asserted". (1 − t) + t is 1 in doubles to one unit in the last place; a
    taper that is not a number or outside [0, 1] is refused, not composed."""
    taper = np.concatenate([[0.0, 1.0, 0.5, 1e-300, 1.0 - 1e-16], np.random.default_rng(2).random(1000)])
    w_arm, w_bar = gm.blend_weights(taper)
    assert np.array_equal(w_bar, taper) and np.array_equal(w_arm, 1.0 - taper)
    assert float(np.abs(w_arm + w_bar - 1.0).max()) <= np.finfo(float).eps
    for bad in (np.array([0.2, np.nan]), np.array([1.5]), np.array([-0.1])):
        with pytest.raises(ArithmeticError, match="do not sum to 1"):
            gm.blend_weights(bad)


def test_one_solve_per_pattern_and_the_cache_changes_no_bit(prod):
    """The pattern solves its rings once, the first time a profile is asked for. Several stages of a run build the
    same pattern, so the last few solutions are kept under a digest of what was solved; a solution from the cache
    is the one a fresh solve makes, bit for bit - with the cache, without it, and ring by ring alone."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, "milky_way")
    c = constants(model)
    R, phi, edges = o.grid.R, o.grid.phi, o.grid["phi"].edges
    gm.forget_solutions()
    first = compose.gas_pattern(o.fields, R, c)
    cold = first.profiles
    assert len(gm._SOLUTIONS) == 1 and first.profiles is cold  # kept on the object: no second solve, no second look-up
    second = compose.gas_pattern(o.fields, R, c)
    assert second.profiles.tobytes() == cold.tobytes() and len(gm._SOLUTIONS) == 1
    assert second.contrast(R, phi).tobytes() == first.contrast(R, phi).tobytes()
    assert second.cell_means(R, edges).tobytes() == first.cell_means(R, edges).tobytes()
    # Without the cache, and one ring at a time: the same bits (the solver gives a ring the same arithmetic alone
    # as in any batch).
    f, eps, carries = first.forcing_amplitudes(), first.epsilon(), first.carries
    fresh, diagnostics = gm.respond(f[carries], first.phases, eps[carries], cache=False)
    assert fresh.tobytes() == cold[carries].tobytes() and len(gm._SOLUTIONS) == 1
    assert np.array_equal(diagnostics.steps, first.diagnostics.steps) and np.array_equal(diagnostics.floor, first.diagnostics.floor)
    for i in np.flatnonzero(carries)[[0, 37, 90, -1]]:
        alone, _ = gm.respond(f[i:i + 1], first.phases, eps[i:i + 1], cache=False)
        assert alone[0].tobytes() == cold[i].tobytes()
    # The cache is bounded, and another pattern does not get this one's rings.
    for seed in range(1, gm.SOLUTIONS_KEPT + 3):
        other = run(model, {"texture_seed": seed}, only=GAS_PATTERN_READS)
        assert compose.gas_pattern(other.fields, R, c).profiles.tobytes() != cold.tobytes()
    assert len(gm._SOLUTIONS) == gm.SOLUTIONS_KEPT == 4
    again = compose.gas_pattern(o.fields, R, c)
    assert again.profiles.tobytes() == cold.tobytes()
    gm.forget_solutions()
    assert len(gm._SOLUTIONS) == 0


DIAGNOSTICS = ("steps", "halvings", "deepest", "residual", "residual_sum", "floor")


@pytest.mark.parametrize("which", ["milky_way", "ngc_4414", "ngc_4414 at pattern seed 33"])
def test_the_criterion_s_shortcut_changes_no_bit_of_the_model_s_rings(prod, monkeypatch, which):
    """Gate G3's follow-up (D216): the solver computes the cells' rounding floors only for the rings they can decide
    (``gas_response._measure``); the rule is per cell on every ring. On the two templates' rings, and on the
    tightly wound galaxy that raised before G3 (``ngc_4414`` at pattern seed 33 and the template's own texture
    seed, where the floor and not the absolute tolerance is the bound on 48 of its 133 rings - 52 until S58, when
    the galaxy had a bar: unbarred, its inner rings saturate and their forcing is another), the solver
    with its shortcut and the solver made to compute every cell's floor at every step (its private keyword
    ``_every_floor``, the tests' alone) return the same bytes: profiles, Newton's counts, residuals, sums, floors.
    The instrument's own cases are held the same way in ``tests/test_gas_response.py``.

    S59 (D218 item 6): the tightly wound galaxy is ``ngc_4414``'s disc at pattern seed 33 **with its pitch as the
    law draws it** (1.78 degrees: the template's pitch pin taken off, ``drawn_pitch``); the template itself is
    read at its pinned 28.9 degrees, where no ring's floor is the bound, as none was at the drawn 14.33."""
    model = prod[0].get(DEFAULT_MODEL)
    if which in TEMPLATES:
        o = template_run(prod, which)
    else:
        # S59 (D218 item 6): was the template's inputs at pattern seed 33 - at 28.9 degrees since the template pins
        # its pitch (no ring on its floor). The tightly wound galaxy is the same disc with the pitch's pin off.
        o = run(model, drawn_pitch("ngc_4414", pattern_seed=33), only=GAS_PATTERN_READS)
        assert float(o.fields["pitch_angle"]) == pytest.approx(1.780, abs=2e-3)
    gp = shape_of(model, o)
    f, eps, carries = gp.forcing_amplitudes(), gp.epsilon(), gp.carries
    shortcut, d = gm.respond(f[carries], gp.phases, eps[carries], cache=False)
    monkeypatch.setattr(gr, "solve", functools.partial(gr.solve, _every_floor=True))
    written, e = gm.respond(f[carries], gp.phases, eps[carries], cache=False)
    monkeypatch.undo()
    assert written.tobytes() == shortcut.tobytes() == gp.profiles[carries].tobytes()
    for name in DIAGNOSTICS:
        assert getattr(e, name).tobytes() == getattr(d, name).tobytes(), name
    on_floor = int((d.floor > gr.RESIDUAL_TOLERANCE).sum())
    assert (int(carries.sum()), on_floor) == {"milky_way": (165, 0), "ngc_4414": (133, 0), "ngc_4414 at pattern seed 33": (133, 48)}[which]  # S58 (D217): the last was (133, 52)


def test_the_suite_galaxy_whose_bits_moved_with_the_criterion_moved_by_rounding(prod, monkeypatch):
    """The record of gate G3's follow-up (D216), with its bound asserted and no profile stored. Across the criterion
    change 816 of 842 galaxies were bit-identical, 22 that raised converge and 4 moved (the gate test's docstring);
    of the suite's 240 the one that moved was ``ngc_4414`` at pattern seed 1, texture seed 1. The first build's rule
    is made again here - max_k |r_k| under the absolute 1e-10 and no rounding floor, by handing the criterion a
    floor of zero (the rule then reads |r_k| ≤ 1e-10 where the first build read <: the same but at equality) - and
    the galaxy solved both ways.

    **As S57 read it**: one ring differed, at 0.49 kpc, where the arm's weight was 3.7e-4; the first build took 10
    Newton steps there and stopped at 9.46e-11, the solver took 8 and stopped at 1.19e-10 under a floor of
    2.52e-10; the two profiles were within 1.8e-15 of each other, cell by cell.

    **Since S58 (D217) that galaxy is another**: ``ngc_4414`` is pinned unbarred, so its arm modes are untapered
    and its inner rings saturate - 124 of its rings carry another forcing than S57's - and the chance landing
    inside the rounding floor that S57 recorded is gone with the ring it happened on. **On today's galaxy the two
    rules give the same bytes on every ring**: its worst residual is 9.67e-11, under the absolute tolerance, on a
    floor of 2.28e-10 (19 of its 133 rings have a floor above 1e-10). The bound stays asserted: any ring the two
    rules solve differently differs by under 2.5e-15 of its profile.

    **S59 (D218 item 6)**: "today's galaxy" is that disc with its pitch as the law draws it, 2.06 degrees - the
    template pins 28.9 since, and on the suite this label is a galaxy with no ring near its floor."""
    model = prod[0].get(DEFAULT_MODEL)
    # S59 (D218 item 6): was `{**overrides(ngc_4414), "pattern_seed": 1, "texture_seed": 1}` - the galaxy of this
    # record is that disc at its drawn pitch, 2.06 degrees; the template pins 28.9 since, so the pitch's pin is
    # taken off. The solver's numbers below are in χ and read nothing of the winding's segments: unmoved.
    given = drawn_pitch("ngc_4414", pattern_seed=1, texture_seed=1)
    o = run(model, given, only=GAS_PATTERN_READS)
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert not gp.barred and float(o.fields["pitch_angle"]) == pytest.approx(2.065, abs=2e-3)
    f, eps, carries = gp.forcing_amplitudes(), gp.epsilon(), gp.carries
    now, d = gm.respond(f[carries], gp.phases, eps[carries], cache=False)
    assert now.tobytes() == gp.profiles[carries].tobytes()
    monkeypatch.setattr(gr, "_floor", lambda phi, eps2: np.zeros_like(phi))  # no floor: the absolute tolerance alone
    before, b = gm.respond(f[carries], gp.phases, eps[carries], cache=False)
    monkeypatch.undo()
    assert np.all(b.residual <= 1e-10) and np.all(b.floor == 0.0)  # the first build's acceptance, on every ring
    differs = np.flatnonzero((before != now).any(axis=1))
    # S58 (D217): was `differs.size == 1` - the ring at 0.4875 kpc (ε 0.821, arm weight 3.72e-4; 10 steps against 8,
    # residuals 9.461e-11 against 1.186e-10 under a floor of 2.516e-10; 1.78e-15 apart).
    assert differs.size == 0 and before.tobytes() == now.tobytes() and np.array_equal(b.steps, d.steps)
    for k in differs:  # the bound, kept for the day a ring lands inside its floor again
        assert 0.0 < float(np.abs(now[k] / before[k] - 1.0).max()) <= 2.5e-15
    assert float(d.residual.max()) == pytest.approx(9.673e-11, rel=0.01) and float(d.floor.max()) == pytest.approx(2.280e-10, rel=0.01)
    assert int((d.floor > gr.RESIDUAL_TOLERANCE).sum()) == 19 and d.worst_steps == 9
