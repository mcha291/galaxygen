"""The winding in seeded segments, and the templates' two measured pins (S59, BUILD_III Phase P4; DECISIONS.md D218).

Until S59 every arm mode wound at one pitch: χ = φ − ln R · cot p. A conditional gate ruled the rest (D218, items
1-7), and this file holds the build to it:

- **the draw** (items 1-2): a segment's azimuthal extent and its pitch's residual, on its own stream of the texture
  seed, the extent drawn again outside the sample's range and never clipped, the residual untruncated;
- **the winding by hand**, from the published rows and nothing of the model's modules: the knots, Φ at every grid
  ring, a reversed segment, the bar's angle at the anchor, the published stellar field's arms, the Sun's azimuth;
- **the predictions** (B4), read before they were judged and recorded with the as-built numbers;
- **the gate** on the 240 galaxies the suite draws;
- **the two disclosed checks**: Reid et al. 2019's arms against the composed field (``tests/reid2019.py``), and NGC
  4414's five measured segments against the drawn spread;
- **the pins**: a pin may be a measured number; ``sun_bar_angle`` places the Sun and moves nothing else;
  ``pitch_angle`` replaces the draw and the draw is published beside it.

**How the winding is published** (the builder's design, stated): the layer stage ``arm_phases`` publishes the raw
draws as two columns of a small object class, ``arm_segment`` - 64 rows outward from the anchor and 192 inward,
each row on its own stream - and nothing of the law; the ``bar`` stage publishes the anchor's radius; and every
reader builds ``pattern.Winding`` from those and the published ``pitch_angle``. Φ is linear in ln R between the
knots, so a point reads it exactly at its own radius, and the grid plays no part in it.

**Read on 2026-10-05** (the production grid). The Milky Way template at its default seeds lays 12 segments over
3-12 kpc; over 100 texture seeds 6.39 on average, 9.30 % of them reversed and 8.76 % under 2.7 degrees, the extent's
median 59.8 degrees and the median change of pitch between neighbours 9.6 degrees; a fifth of the segments on the
grid (20.2 %) hold no ring. The Reid check reads 1.92 widths (a miss; 0.65 with the unsegmented winding).
``ngc_4414`` at its pinned 28.9 degrees: ε and f both × 0.5121 on every ring.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import reid2019
from galaxy import templates
from galaxy.api.service import Service
from galaxy.core import seeds as _seeds
from galaxy.core.grids import GridSpec
from galaxy.layer import arm_phases as ap
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import RunError, run
from galaxy.stages import gas_pattern as gm
from galaxy.stages import pattern as pt

SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
PATTERN = ("pattern_density_contrast", "gas_density_contrast", "star_formation_gas_contrast", *pt.PATTERN_READS, *gm.GAS_PATTERN_READS,
           "bar_present", "pitch_angle_drawn", "sun_azimuth", "arm_saturation", "arm_contrast")
# The ruling's numbers, written here; the model's constants are held to them.
MEDIAN_HAND, LOG_SCATTER_HAND, LOW_HAND, HIGH_HAND, RESIDUAL_HAND = 60.0, 0.35, 20.0, 180.0, 10.0
OUT_ROWS, IN_ROWS = 64, 192
# NGC 4414's five measured segments: pitch in degrees and radial range in arcsec, S4G 3.6 micron, deprojected
# [verified: Herrera-Endoqui et al. 2015, A&A 582, A86, Table 3 at VizieR J/A+A/582/A86/table3;
# docs/READING_ARM_SEGMENTS.md A1.4]. Their ranges overlap - pieces of different arms - so nothing positional is
# pinned of them (D218 item 6): a disclosed check of the drawn segments' spread.
NGC_4414_SEGMENTS = ((-30.5, 28.7, 63.6), (-34.2, 19.4, 57.3), (-28.1, 32.7, 87.4), (-44.0, 29.2, 54.4), (-7.6, 57.9, 66.3))
_RUNS: dict[object, object] = {}


def the_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def inputs_of(template: str, **more) -> dict:
    return {**templates.overrides(templates.TEMPLATES[template]), **more}


def template_run(prod, template: str, **more):
    key = (template, tuple(sorted(more.items())))
    if key not in _RUNS:
        _RUNS[key] = run(the_model(prod), inputs_of(template, **more), only=PATTERN)
    return _RUNS[key]


def hand_knots(F) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(ln R at the knots, Φ at the knots, each segment's pitch in degrees), inside out, from the published rows,
    the published pitch and the published anchor: this file's arithmetic, a loop, no function of the model's."""
    extent, residual = np.asarray(F["arm_segment_extent"], dtype=float), np.asarray(F["arm_segment_pitch_residual"], dtype=float)
    pitch, anchor = float(F["pitch_angle"]), float(F["arm_winding_anchor_radius"])
    x0 = math.log(anchor)
    p0 = x0 / math.tan(math.radians(pitch))
    xs, ps, pitches = [x0], [p0], []
    for j in range(OUT_ROWS):  # outward from the anchor
        p = pitch + residual[j]
        t = math.tan(math.radians(p))
        xs.append(xs[-1] + extent[j] * abs(t))
        ps.append(ps[-1] + extent[j] * (1.0 if t > 0.0 else -1.0 if t < 0.0 else 0.0))
        pitches.append(p)
    x, ph = x0, p0
    for j in range(IN_ROWS):  # inward from the anchor
        p = pitch + residual[OUT_ROWS + j]
        t = math.tan(math.radians(p))
        x -= extent[OUT_ROWS + j] * abs(t)
        ph -= extent[OUT_ROWS + j] * (1.0 if t > 0.0 else -1.0 if t < 0.0 else 0.0)
        xs.insert(0, x)
        ps.insert(0, ph)
        pitches.insert(0, p)
    return np.array(xs), np.array(ps), np.array(pitches)


def hand_phase(knots: np.ndarray, phases: np.ndarray, R: float) -> float:
    """Φ at one radius: the segment the radius lies in, and the straight line in ln R across it."""
    x = math.log(R)
    k = int(np.searchsorted(knots, x, side="right")) - 1
    return float(phases[k] + (phases[k + 1] - phases[k]) * (x - knots[k]) / (knots[k + 1] - knots[k]))


# --- the constants and the declarations ----------------------------------------------------------------------------


def test_the_constants_are_the_ruling_s_and_the_segments_declare_what_they_are(prod):
    m = the_model(prod)
    c = constants(m)
    held = {"ARM_SEGMENT_EXTENT_MEDIAN": MEDIAN_HAND, "ARM_SEGMENT_EXTENT_LOG_SCATTER": LOG_SCATTER_HAND, "ARM_SEGMENT_EXTENT_MIN": LOW_HAND,
            "ARM_SEGMENT_EXTENT_MAX": HIGH_HAND, "ARM_SEGMENT_PITCH_SCATTER": RESIDUAL_HAND}
    assert {k: c[k] for k in held} == held and tuple(held) == ap.SEGMENT_CONSTANTS
    for k in held:
        about = " ".join(m.constants[k].about.split())
        assert "Honig & Reid 2015" in about and "38 printed rows" in about and "[verified:" in about, k
    for k in ("ARM_SEGMENT_EXTENT_MEDIAN", "ARM_SEGMENT_PITCH_SCATTER"):
        assert "The reader's arithmetic on Honig & Reid 2015's 38 printed rows".lower() in " ".join(m.constants[k].about.split()).replace("**", "").lower(), k
    scatter = " ".join(m.constants["ARM_SEGMENT_PITCH_SCATTER"].about.split())
    assert "9.5 +/- 0.3 deg" in scatter and "Diaz-Garcia" in scatter and "untruncated" in scatter
    assert (pt.SEGMENTS_OUTWARD, pt.SEGMENTS_INWARD) == (OUT_ROWS, IN_ROWS) and ap.MAX_EXTENT_DRAWS == 16
    for decl in ap.ARM_SEGMENTS:
        assert decl.provenance == "synthetic" and decl.of == "arm_segment" and decl.kind.domain == "object"
        assert "kinks of real spiral arms" in decl.stands_in_for and "common rings for every arm" in decl.stands_in_for
        assert "Every ring's mean and every mode's amplitude" in decl.conserves and "the gas law's strength" in decl.conserves
        assert "untruncated" in decl.statistic and "38 printed rows" in decl.statistic and "9.5 +/- 0.3" in decl.statistic
    assert [d.name for d in ap.ARM_SEGMENTS] == list(pt.SEGMENT_FIELDS) and ap.ARM_PHASES.reads_seeds == ("texture_seed",)
    assert set(pt.WINDING_FIELDS) <= set(pt.PATTERN_READS) and set(pt.WINDING_FIELDS) <= set(gm.GAS_PATTERN_READS)
    assert ap.segment_streams()[:2] == (("out", 0), ("out", 1)) and ap.segment_streams()[OUT_ROWS] == ("in", 0) and len(ap.segment_streams()) == OUT_ROWS + IN_ROWS


def test_the_draw_is_redrawn_outside_the_sample_s_range_and_never_clipped(prod):
    """D218 item 2: the extent "log-normal with median 60° and σ_ln 0.35, redrawn outside 20°–180°"; the residual
    "normal with sd 10°, independent per segment, untruncated". The redraw has a fixed count (rule A1): at most 16
    extents a segment, and the stage raises if all sixteen fall outside (4e-45 a segment) - it does not clip.
    **Counted**: over 100 texture seeds' 25 600 rows, 39 extents were drawn again (0.15 %) and no segment needed
    more than two draws. The residual is drawn first, so it does not depend on the redraws. Each row is its own
    stream - ("segment", "out", j) and ("segment", "in", j), j = 0 at the anchor - so the published rows are these
    draws whatever the grid, and a row does not move when more rows are laid."""
    numbers = tuple(float(constants(the_model(prod))[k]) for k in ap.SEGMENT_CONSTANTS)
    rows, redraws, most, extents, residuals = 0, 0, 0, [], []
    for seed in range(100):
        for way, j in ap.segment_streams():
            extent, residual, attempts = ap.draw_segment(_seeds.rng(seed, "arm_phases", "segment", way, j), *numbers)
            rows, redraws, most = rows + 1, redraws + attempts - 1, max(most, attempts)
            extents.append(math.degrees(extent))
            residuals.append(residual)
    extents, residuals = np.array(extents), np.array(residuals)
    assert (rows, redraws, most) == (25600, 39, 2)
    assert LOW_HAND <= extents.min() and extents.max() <= HIGH_HAND
    assert float(np.median(extents)) == pytest.approx(60.0, abs=0.6) and float(np.std(np.log(extents))) == pytest.approx(0.35, abs=0.01)
    assert (float(residuals.mean()), float(residuals.std())) == pytest.approx((0.0, 10.0), abs=0.15)
    assert residuals.min() < -35.0 and residuals.max() > 35.0  # untruncated: beyond 3.5 sigma both ways
    # A generator that always draws outside the range exhausts the count and raises.
    class Stuck:
        def normal(self, *args):
            return 100.0

    with pytest.raises(ArithmeticError, match="16 times running"):
        ap.draw_segment(Stuck(), *numbers)
    # The published rows are these draws: the default galaxy on two grids.
    for grid in (None, SMALL):
        o = run(the_model(prod), {"texture_seed": 3}, grid, only=pt.SEGMENT_FIELDS)
        want = [ap.draw_segment(_seeds.rng(3, "arm_phases", "segment", way, j), *numbers) for way, j in ap.segment_streams()]
        assert np.asarray(o.fields["arm_segment_extent"]).tolist() == [w[0] for w in want]
        assert np.asarray(o.fields["arm_segment_pitch_residual"]).tolist() == [w[1] for w in want]
    off = run(the_model(prod), {"texture_seed": 3}, SMALL, only=(*pt.SEGMENT_FIELDS, "arm_winding_anchor_radius"), layer=False)
    assert np.asarray(off.fields["arm_segment_extent"]).size == 0 and np.asarray(off.fields["arm_segment_pitch_residual"]).size == 0
    assert pt.Winding.from_fields({**dict(off.fields), "pitch_angle": 13.5}) is None  # no segment: the plain winding


# --- by hand ---------------------------------------------------------------------------------------------------------


def test_the_winding_by_hand_on_a_seed_with_a_reversed_segment(prod):
    """D218 items 1-3, from the **published** numbers with this file's arithmetic: the Milky Way template at
    texture seed 7, whose winding holds a reversed segment across the solar circle.

    Φ(R_A) = ln R_A · cot p at the anchor (the bar's half-length, 5.2097 kpc; p = 13.538°) - the bar's angle,
    6.85498 rad, exactly as it was. From there each segment of pitch p + δ spans Δβ |tan(p + δ)| in ln R and turns
    the phase by Δβ, outward - back, where the pitch is negative. As read, the segments over 3-12 kpc:

        R kpc             pitch°    (the first ends at the anchor; the third is reversed)
        2.580 - 5.210     32.31
        5.210 - 6.414     10.78
        6.414 - 8.558    −13.58
        8.558 - 9.899     10.35
        9.899 - 11.919     6.48
        11.919 - 12.599    2.92

    Φ is the straight line in ln R across each segment: continuous at every knot, its slope cot(p + δ) jumping
    there and nowhere else. The module's Φ is the hand's at every grid ring to 1e-12; across the reversed segment
    Φ falls as R grows. Past the bar's body the published stellar field is 1 + Σ A_m cos(m (φ − Φ) − θ_m) with
    the hand's Φ; the two-armed mode's crest at R = a lies on the bar's axis; and the Sun stands 30° behind the
    bar's near end in the sense of rotation - at a larger azimuth, since the disc turns towards smaller ones."""
    o = template_run(prod, "milky_way", texture_seed=7)
    F, R, phi = o.fields, o.grid.R, o.grid.phi
    pitch, anchor, a = float(F["pitch_angle"]), float(F["arm_winding_anchor_radius"]), float(F["bar_half_length"])
    assert (pitch, anchor) == pytest.approx((13.5378, 5.2097), abs=5e-5) and anchor == a
    knots, phases, pitches = hand_knots(F)
    assert knots.size == OUT_ROWS + IN_ROWS + 1 and np.all(np.diff(knots) >= 0.0)
    bar_angle = math.log(a) / math.tan(math.radians(pitch))
    assert phases[IN_ROWS] == bar_angle == pytest.approx(6.85498, abs=1e-5)
    radii = np.exp(knots)
    on = (radii[1:] > 3.0) & (radii[:-1] < 12.0)
    assert np.round(radii[:-1][on], 3).tolist() == [2.58, 5.21, 6.414, 8.558, 9.899, 11.919]
    assert np.round(pitches[on], 2).tolist() == [32.31, 10.78, -13.58, 10.35, 6.48, 2.92]
    # The module's winding is the hand's: its knots, and Φ on every grid ring.
    w = compose.stellar_pattern(F, R).winding
    assert np.allclose(w.knots, knots, rtol=0.0, atol=1e-12) and np.allclose(w.phases, phases, rtol=0.0, atol=1e-12)
    by_hand = np.array([hand_phase(knots, phases, float(r)) for r in R])
    assert float(np.abs(w.phase(R) - by_hand).max()) < 1e-12
    # Continuous at every knot, by both neighbours' lines; the slope is the segment's cotangent and jumps at the knots.
    k = IN_ROWS + 1  # the knot at 6.414 kpc, the first past the anchor, where the pitch turns from 10.78° to −13.58°
    assert math.exp(knots[k]) == pytest.approx(6.414, abs=5e-4)
    left = phases[k - 1] + (knots[k] - knots[k - 1]) / math.tan(math.radians(pitches[k - 1]))
    right = phases[k + 1] - (knots[k + 1] - knots[k]) / math.tan(math.radians(pitches[k]))
    assert abs(left - phases[k]) < 1e-12 and abs(right - phases[k]) < 1e-12
    inside = (np.log(R) > knots[k]) & (np.log(R) < knots[k + 1])
    assert int(inside.sum()) == 28 and np.all(np.diff(by_hand[inside]) < 0.0)  # the reversed segment: Φ falls outward
    slope = np.diff(by_hand[inside]) / np.diff(np.log(R[inside]))
    assert np.allclose(slope, 1.0 / math.tan(math.radians(pitches[k])), rtol=1e-9, atol=0.0)
    # Φ(a) is the bar's angle, so the two-armed crest at the bar's end is on the bar's axis.
    assert hand_phase(knots, phases, a) == pytest.approx(bar_angle, abs=1e-13) and float(F[pt.phase_field(2)]) == 0.0
    # The published stellar field past the body: the arm modes on the hand's winding.
    past = R > 1.01 * a
    arms = np.ones((int(past.sum()), phi.size))
    for m in (2, 3, 4, 5, 6):
        arms += np.asarray(F[f"arm_mode_amplitude_{m}"])[past, None] * np.cos(m * (phi[None, :] - by_hand[past, None]) - float(F[f"arm_mode_phase_{m}"]))
    assert float(np.abs(np.asarray(F["pattern_density_contrast"])[past] - arms).max()) < 1e-12
    # The same seed with the unsegmented winding is another field (the segments are in it) with the same ring means.
    plain = 1.0 + sum(np.asarray(F[f"arm_mode_amplitude_{m}"])[past, None] * np.cos(m * (phi[None, :] - np.log(R[past])[:, None] / math.tan(math.radians(pitch))) - float(F[f"arm_mode_phase_{m}"])) for m in (2, 3, 4, 5, 6))
    assert float(np.abs(arms - plain).max()) > 0.1 and float(np.abs(arms.mean(axis=1) - 1.0).max()) < 1e-12
    # The Sun: φ_sun = φ_bar − sense · 30°, the disc turning towards decreasing φ (sense −1), wrapped into one turn.
    assert pt.rotation_sense(pitch) == gm.rotation_sense(pitch) == -1.0
    sun = (bar_angle + math.radians(30.0)) % (2.0 * math.pi)
    assert float(F["sun_azimuth"]) == pytest.approx(sun, abs=1e-13) == pytest.approx(1.09539, abs=1e-5)
    # ... so the bar's near end is at β = +30°, β measured from the Sun in the sense of rotation.
    beta = -1.0 * (bar_angle - float(F["sun_azimuth"]))
    assert math.degrees(beta % (2.0 * math.pi)) == pytest.approx(30.0, abs=1e-9)


# --- the predictions (B4) and the gate ---------------------------------------------------------------------------------


def test_the_gate_s_predictions_as_measured(prod):
    """D218's predictions, read before the build was judged; nothing was changed to make one hold.

    "Milky Way: about 5–6 segments over 3–12 kpc, ~9 % reversed and ~9 % under 2.7°". **As built**, over 100
    texture seeds of the template: 6.39 segments over 3-12 kpc on average (median 6: held; the default seeds
    themselves lay 12, four of them nearly circular), 9.30 % reversed and 8.76 % under 2.7° (held). "The bar's
    angle, the body, the lanes ... bit-identical": the bar's angle is ln a · cot p to the bit, the anchor's phase.
    "The m = 2 crest at R = a on the bar's axis on every seed": held (the gate, below). "The Reid check a miss by
    2–4 widths": 1.92 widths - a miss, just under the predicted range (below). ``ngc_4414`` at 28.9°: "ε × 1.96 and
    f × 0.51 on every ring" - **as built both ε and f are × 0.5121**, sin 14.33°/sin 28.9°: ε = a/(κ R sin p) falls
    as the pitch opens, as f does; the prediction's 1.96 is the inverse of the factor (it is what f/ε² gains).
    Recorded as worded and as read."""
    model = the_model(prod)
    counts, pitches = [], []
    for seed in range(100):
        o = run(model, inputs_of("milky_way", texture_seed=seed), only=(*pt.WINDING_FIELDS, "pitch_angle"))
        w = pt.Winding.from_fields(o.fields)
        inner, outer, pitch, _ = w.segments(float(o.grid.R[0]), float(o.grid.R[-1]))
        counts.append(int(((outer > 3.0) & (inner < 12.0)).sum()))
        pitches.extend(pitch.tolist())
    pitches = np.array(pitches)
    assert counts[0] == 12 and float(np.mean(counts)) == pytest.approx(6.39, abs=0.005) and float(np.median(counts)) == 6.0
    assert 100.0 * float((pitches < 0.0).mean()) == pytest.approx(9.30, abs=0.01)
    assert 100.0 * float((np.abs(pitches) < 2.7).mean()) == pytest.approx(8.76, abs=0.01)
    # NGC 4414: the gas law's two numbers at the pinned pitch against the drawn one's.
    pinned = template_run(prod, "ngc_4414")
    given = {k: v for k, v in inputs_of("ngc_4414").items() if k != "pitch_angle"}
    drawn = run(model, given, only=PATTERN)
    R = pinned.grid.R
    a, b = (compose.gas_pattern(o.fields, R, constants(model)) for o in (pinned, drawn))
    factor = math.sin(math.radians(float(drawn.fields["pitch_angle"]))) / math.sin(math.radians(28.9))
    assert factor == pytest.approx(0.5121, abs=1e-4) and 1.0 / factor == pytest.approx(1.953, abs=1e-3)
    assert np.allclose(a.epsilon() / b.epsilon(), factor, rtol=1e-13, atol=0.0)
    fa, fb = a.forcing_amplitudes(), b.forcing_amplitudes()
    assert np.allclose(fa[fb != 0.0] / fb[fb != 0.0], factor, rtol=1e-13, atol=0.0)


def test_gate_on_the_suite_s_galaxies(prod):
    """"Every ring mean 1 (stellar 1e-12 on cells, gas 1e-13) on the 240 seeds and both templates; every
    ``arm_mode_amplitude_m`` bit-identical layer on and off; Φ continuous to 1e-12 at each kink; φ_bar = Φ(a) to
    rounding on every barred seed; the point function and the grid agree; the segment statistics re-measured on
    the 240 seeds — extent median inside 50°–80°, reversed fraction 5–12 %, median |Δψ| 7°–13° — read as checks of
    the draw, with the sub-grid segments (d ln R under one ring step) counted".

    **As read.** Ring means: stellar 1.6e-15, gas 1.0e-13 at worst (the solver's own sum, as S57-S58 pin it: under
    2e-13). The amplitudes: no bit moves. Φ(a) − φ_bar: 0, exactly. The published fields are the pattern objects'
    own, rebuilt from the published numbers, to the bit. **The segment statistics, on the segments that cross the
    grid**: the Milky Way's 120 galaxies - 3 442 segments, extent median 58.5°, 17.4 % reversed, median |Δψ| 8.8°,
    18.7 % holding no ring; ``ngc_4414``'s 120 - 1 440 segments, 67.6°, none reversed (its pitch is pinned at
    28.9°), 7.5°, 8.3 % holding no ring. **The reversed fraction is outside 5–12 % on both, and it is the suite
    that is the wrong sample, not the draw**: the suite holds two texture seeds, so two sequences of rows, read
    at sixty pitches (the pattern seeds'; a galaxy drawn at a low pitch reverses more) or at one pinned pitch.
    Pooled, 598 of 4 882: 12.2 %. The draw itself is read on 100 texture seeds in the predictions' test: 9.30 %."""
    model = the_model(prod)
    read: dict[str, dict[str, list]] = {t: {"extent": [], "pitch": [], "step": [], "sub": []} for t in ("milky_way", "ngc_4414")}
    worst = {"stars": 0.0, "gas": 0.0, "bar": 0.0}
    for template in read:
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                given = inputs_of(template, pattern_seed=pattern_seed, texture_seed=texture_seed)
                o = run(model, given, only=PATTERN)
                F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
                label = (template, pattern_seed, texture_seed)
                stars, gas = np.asarray(F["pattern_density_contrast"]), np.asarray(F["gas_density_contrast"])
                worst["stars"] = max(worst["stars"], float(np.abs(stars.mean(axis=1) - 1.0).max()))
                worst["gas"] = max(worst["gas"], float(np.abs(gas.sum(axis=1) / gas.shape[1] - 1.0).max()))
                assert stars.min() > 0.0 and gas.min() > 0.0, label
                sp, gp = compose.stellar_pattern(F, R), compose.gas_pattern(F, R, constants(model))
                assert sp.published(R, o.grid.phi, edges).tobytes() == stars.tobytes(), label
                assert gp.cell_means(R, edges).tobytes() == gas.tobytes(), label
                off = run(model, given, only=pt.AMPLITUDE_FIELDS, layer=False).fields
                assert all(np.asarray(off[k]).tobytes() == np.asarray(F[k]).tobytes() for k in pt.AMPLITUDE_FIELDS), label
                w = sp.winding
                assert np.interp(w.knots, w.knots, w.phases).tobytes() == w.phases.tobytes(), label
                if template == "milky_way":
                    a = float(F["bar_half_length"])
                    worst["bar"] = max(worst["bar"], abs(float(w.phase(np.array([a]))[0]) - sp.bar_angle))
                    assert float(F[pt.phase_field(2)]) == 0.0 and w.anchor_phase == sp.bar_angle, label
                inner, outer, pitch, extent = w.segments(float(R[0]), float(R[-1]))
                got = read[template]
                got["extent"].extend(np.degrees(extent).tolist())
                got["pitch"].extend(pitch.tolist())
                got["step"].extend(np.abs(np.diff(pitch)).tolist())
                got["sub"].append(sum(1 for lo, hi in zip(inner, outer) if not ((R >= lo) & (R < hi)).any()))
    assert worst["stars"] < 1e-12 and worst["gas"] < 2e-13 and worst["bar"] == 0.0
    for template, (n, median, reversed_pct, step, sub) in (("milky_way", (3442, 58.46, 17.37, 8.83, 644)), ("ngc_4414", (1440, 67.56, 0.0, 7.47, 120))):
        got = read[template]
        extent, pitch = np.array(got["extent"]), np.array(got["pitch"])
        assert extent.size == n and float(np.median(extent)) == pytest.approx(median, abs=0.01), template
        assert 50.0 <= float(np.median(extent)) <= 80.0 and 7.0 <= float(np.median(got["step"])) <= 13.0, template
        assert 100.0 * float((pitch < 0.0).mean()) == pytest.approx(reversed_pct, abs=0.01), template
        assert float(np.median(got["step"])) == pytest.approx(step, abs=0.01) and sum(got["sub"]) == sub, template
    pooled = np.array(read["milky_way"]["pitch"] + read["ngc_4414"]["pitch"])
    assert pooled.size == 4882 and int((pooled < 0.0).sum()) == 598  # 12.2 %: outside 5-12 %, the suite's two texture seeds


# --- the two disclosed checks ---------------------------------------------------------------------------------------


def test_disclosed_check_the_milky_way_s_measured_arms_against_the_composed_field(prod):
    """D218 item 5 (not a spec row: I3): the radial distance from each of Reid et al. 2019's arm loci to the nearest
    crest of the composed stellar field, in measured arm widths; the median over the five arms, judged against 1
    width. ``tests/reid2019.py`` holds the table and says exactly how the five arms are taken.

    **Predicted before the build: a miss by 2–4 widths. As read: 1.92 widths - a miss** (over 1), a little under
    the predicted range. Per arm: Norma–Outer 1.15, Scutum–Centaurus 0.49, Sagittarius–Carina 2.58, Perseus 1.92,
    Local 1.96 (all points pooled: 1.38). The same field with the unsegmented winding reads 0.65, inside a width:
    a sum of five modes puts a crest every kiloparsec or so along an azimuth, so a locus is seldom far from one -
    the statistic measures how dense the crests are, not whether the arms are the Milky Way's. **This
    representation cannot show the Milky Way's measured arms** (D218; #138's conflict): nothing is tuned to the
    check - not the Sun's azimuth, not the anchor, not the residual."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    sp = compose.stellar_pattern(F, R)
    sense = pt.rotation_sense(float(F["pitch_angle"]))
    per_arm, median, pooled = reid2019.check(sp, float(F["sun_azimuth"]), sense)
    assert list(per_arm) == ["Norma-Outer", "Sct-Cen", "Sgr-Car", "Perseus", "Local"]
    assert [per_arm[k] for k in per_arm] == pytest.approx([1.151, 0.494, 2.584, 1.920, 1.957], abs=2e-3)
    assert (median, pooled) == pytest.approx((1.920, 1.378), abs=2e-3)
    assert median > 1.0 and not 2.0 <= median <= 4.0  # a miss; and the prediction's range is itself missed, from below
    plain = pt.ArmPattern(sp.R, sp.amplitudes, sp.phases, sp.bar, sp.pitch_deg, sp.bar_length, sp.axis_ratio, sp.boxiness, sp.index, sp.share, sp.surface_density)
    assert plain.winding is None and reid2019.check(plain, float(F["sun_azimuth"]), sense)[1] == pytest.approx(0.646, abs=2e-3)
    # The table as entered: seven rows, R0 8.15 kpc, the width law; a locus passes through its kink.
    assert len(reid2019.TABLE2) == 7 and reid2019.R0 == 8.15 and float(reid2019.width_kpc(8.15)) == 0.336
    beta, radius = reid2019.locus(reid2019.TABLE2[5])  # Perseus
    assert (beta[0], beta[-1], beta.size) == (-23.0, 115.0, 139) and float(radius[beta == 40.0][0]) == 8.87
    assert float(radius[0]) == pytest.approx(8.87 * math.exp(math.radians(63.0) * math.tan(math.radians(10.3))), rel=1e-12)


def test_disclosed_check_ngc_4414_s_measured_segments_and_its_pinned_pitch(prod):
    """D218 item 6. "``pitch_angle`` = 28.9° replaces the draw (a measured mean, as ``bar_present`` is); the law's
    own value 14.3° is published beside it and its miss recorded (2.4σ of the 6° draw: a finding against the pitch
    law)." The five measured segments' mean is 28.88° and their standard deviation 13.35°, this file's arithmetic
    on the five rows; **the drawn spread is 10°** (the constant; 9.8° as realised on the segments that cross the
    template's grid over 100 texture seeds), so the galaxy's own segments scatter 1.3 times as widely as the draw -
    read, not tuned. Every other draw of the pattern stage keeps its stream and its value under the pin."""
    measured = np.array([abs(row[0]) for row in NGC_4414_SEGMENTS])
    assert float(measured.mean()) == pytest.approx(28.88, abs=5e-3) and float(measured.std(ddof=1)) == pytest.approx(13.35, abs=5e-3)
    assert float(measured.std(ddof=1) / math.sqrt(5)) == pytest.approx(5.97, abs=5e-3)
    pinned = template_run(prod, "ngc_4414")
    model = the_model(prod)
    drawn = run(model, {k: v for k, v in inputs_of("ngc_4414").items() if k != "pitch_angle"}, only=PATTERN)
    assert pinned.inputs["pitch_angle"] == 28.9 and "pitch_angle" not in drawn.inputs
    assert float(pinned.fields["pitch_angle"]) == 28.9 and float(pinned.fields["pitch_angle_drawn"]) == float(drawn.fields["pitch_angle"]) == float(drawn.fields["pitch_angle_drawn"])
    law = float(pinned.fields["pitch_angle_drawn"])
    scatter = float(constants(model)["PITCH_SCATTER"])
    assert law == pytest.approx(14.330, abs=1e-3) and (28.9 - law) / scatter == pytest.approx(2.43, abs=0.01)
    for name in ("arm_contrast", *pt.AMPLITUDE_FIELDS, *pt.PHASE_FIELDS, *pt.SEGMENT_FIELDS, "arm_winding_anchor_radius", "arm_saturation"):
        assert np.asarray(pinned.fields[name]).tobytes() == np.asarray(drawn.fields[name]).tobytes(), name
    assert math.isnan(float(pinned.fields["sun_azimuth"])) and math.isnan(float(pinned.fields["bar_half_length"]))
    assert float(pinned.fields["arm_winding_anchor_radius"]) == pytest.approx(3.5101, abs=1e-4)  # where its bar would end
    residuals = []
    for seed in range(100):
        o = run(model, inputs_of("ngc_4414", texture_seed=seed), only=(*pt.WINDING_FIELDS, "pitch_angle"))
        residuals.extend((pt.Winding.from_fields(o.fields).segments(float(o.grid.R[0]), float(o.grid.R[-1]))[2] - 28.9).tolist())
    assert float(np.std(residuals)) == pytest.approx(9.8, abs=0.3) and float(measured.std(ddof=1)) / RESIDUAL_HAND == pytest.approx(1.335, abs=1e-3)


# --- the pins ---------------------------------------------------------------------------------------------------------


def test_a_pin_may_be_a_measured_number_and_the_sun_moves_nothing_else(prod):
    """D218 items 5-6 on D217's mechanism: a pin with a unit is a finite number; one without is a class. Neither is
    offered to a request; a run made with a pin is not resumed without it. ``sun_bar_angle`` gives ``sun_azimuth``
    and moves no other field; without it, or without a bar, the Sun's azimuth is not a number."""
    model = the_model(prod)
    only = ("sun_azimuth", "pitch_angle", "pitch_angle_drawn", "bar_half_length", "pattern_density_contrast", "gas_density_contrast")
    bare = run(model, None, SMALL, only=only)
    sun = run(model, {"sun_bar_angle": 30.0}, SMALL, only=only)
    assert math.isnan(float(bare.fields["sun_azimuth"])) and math.isfinite(float(sun.fields["sun_azimuth"]))
    for name in only[1:]:
        assert np.asarray(bare.fields[name]).tobytes() == np.asarray(sun.fields[name]).tobytes(), name
    assert math.isnan(float(run(model, {"sun_bar_angle": 30.0, "bar_present": False}, SMALL, only=only).fields["sun_azimuth"]))
    other = run(model, {"sun_bar_angle": 28.0}, SMALL, only=only)
    assert float(other.fields["sun_azimuth"]) - float(sun.fields["sun_azimuth"]) == pytest.approx(math.radians(-2.0), abs=1e-12)
    pitched = run(model, {"pitch_angle": 20.0}, SMALL, only=only)
    assert float(pitched.fields["pitch_angle"]) == 20.0 and float(pitched.fields["pitch_angle_drawn"]) == float(bare.fields["pitch_angle"])
    for bad in (True, "30", float("nan"), float("inf")):
        with pytest.raises(RunError, match="finite number in deg"):
            run(model, {"sun_bar_angle": bad}, SMALL, only=only)
    with pytest.raises(RunError, match="True or False"):
        run(model, {"bar_present": 1.0}, SMALL, only=only)
    with pytest.raises(RunError, match="cannot resume: (pin|input) 'pitch_angle'"):
        run(model, {}, SMALL, resume=pitched, only=only)
    api = Service(grid=SMALL)
    for query in ("fields=sun_azimuth&sun_bar_angle=30", "fields=pitch_angle&pitch_angle=20", "fields=pitch_angle&template=ngc_4414&pitch_angle=20"):
        got = api.handle("/api/arrays", query)
        assert got.status == 400 and "is a template's pin, not an input a request may set" in got.json()["error"], query
    listed = api.handle("/api/inputs").json()
    assert not {"pitch_angle", "sun_bar_angle"} & {i["name"] for kind in ("controls", "seeds", "events") for i in listed[kind]}
    head = api.handle("/api/arrays", "fields=sun_azimuth,pitch_angle,pitch_angle_drawn&template=milky_way").frame()[0]
    assert head["inputs"]["sun_bar_angle"] == 30.0 and head["scalars"]["sun_azimuth"] is not None
    head = api.handle("/api/arrays", "fields=sun_azimuth,pitch_angle,pitch_angle_drawn&template=ngc_4414").frame()[0]
    assert head["inputs"]["pitch_angle"] == 28.9 and head["scalars"]["pitch_angle"] == 28.9 and head["scalars"]["sun_azimuth"] is None
