"""The winding in seeded segments, and the templates' two measured pins (S59, BUILD_III Phase P4; DECISIONS.md D218).

Until S59 every arm mode wound at one pitch: χ = φ − ln R · cot p. A conditional gate ruled the rest (D218, items
1-7), an independent review read the first build, and a follow-up to the gate changed four things (items 1-7 of
"A follow-up to the gate"). This file holds the build to both:

- **the draw** (items 1-2): a segment's azimuthal extent and its pitch's unit normal deviate, on its own stream of
  the texture seed, the extent drawn again outside the sample's range and never clipped, the deviate untruncated;
- **the residual relative to the pitch** (the follow-up, item 2): a segment's pitch is p (1 + 0.56 z) - the
  standard deviation 0.56 of the disc's own pitch - in place of p + δ with δ of 10 degrees whatever the pitch;
- **the winding by hand**, from the published rows and nothing of the model's modules: the knots, Φ at every grid
  ring, a reversed segment, the bar's angle at the anchor, the published stellar field's arms, the Sun's azimuth;
- **the predictions** of the gate (B4) and of its follow-up (item 2), read before they were judged and recorded
  with the as-built numbers;
- **the gate** on the 360 galaxies of its three legs (the suite's 240 and the drawn-pitch unbarred family);
- **the young stars' reader** (the review's blocker; the follow-up's item 1, and the gate's ruling on what that
  remedy left inside a bar): the star formation law applied at a point to the gas pattern's point function, ring
  by ring, held against the law by hand, the published table at the cells, and the two readers it replaced;
- **the two disclosed checks**: Reid et al. 2019's arms against the composed field (``tests/reid2019.py``), read
  against its two nulls and judged by no verdict, and NGC 4414's five measured segments against the drawn spread;
- **the pins**: a pin may be a measured number, held to the range of what it replaces; ``sun_bar_angle`` places
  the Sun and moves nothing else; ``pitch_angle`` replaces the draw and the draw is published beside it.

**How the winding is published** (the builder's design, stated): the layer stage ``arm_phases`` publishes the raw
draws as two columns of a small table, ``arm_segment`` - 256 rows outward from the anchor and 768 inward,
each row on its own stream - and nothing of the law: the extent, and a **unit normal** that holds no pitch (a
table column, ``Kind.TABLE_COLUMN``, domain ``table``: the rows are published whole and read whole, and are no
catalogue - the lead's ruling on the contract); the ``bar`` stage publishes the anchor's radius and the spread of
a segment's pitch relative to the disc's (the constant 0.56, published so every reader builds the same winding
from published numbers); and every reader builds ``pattern.Winding`` from those and the published
``pitch_angle``. Φ is linear in ln R between the knots, so a point reads it exactly at its own radius, and the
grid plays no part in it.

**The row counts grew with the form** (64 and 192 until the follow-up). A segment spans Δβ |tan p_seg| in ln R:
with the residual relative to the pitch a disc at the pitch's floor of 1 degree lays a segment every fiftieth of
an e-fold, 89 outward of the Milky Way's anchor to the grid's edge and 424 inward to the radius floor, where the
first build's rows, sized at a residual of 10 degrees whatever the pitch, reached with 6 and 30. The suite's own
pattern seed 22 draws that pitch. The rows the first build laid keep their streams, and their extents their bits.
"""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pytest

import reid2019
from galaxy import templates
from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import TABLES, FieldDecl, Kind
from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, Input, RegistryError
from galaxy.layer import arm_phases as ap
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import RunError, run
from galaxy.stages import gas_pattern as gm
from galaxy.stages import pattern as pt
from galaxy.stages import sfh, systems

SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
PATTERN = ("pattern_density_contrast", "gas_density_contrast", "star_formation_gas_contrast", *pt.PATTERN_READS, *gm.GAS_PATTERN_READS,
           "bar_present", "pitch_angle_drawn", "sun_azimuth", "arm_saturation", "arm_contrast")
# What the young stars' reader and the law it is held against read.
READER = ("sfr_modulation", "star_formation_gas_contrast", "gas_surface_density", "sf_threshold_surface_density", *pt.PATTERN_READS, *gm.GAS_PATTERN_READS)
# The ruling's numbers, written here; the model's constants are held to them.
MEDIAN_HAND, LOG_SCATTER_HAND, LOW_HAND, HIGH_HAND, RELATIVE_HAND = 60.0, 0.35, 20.0, 180.0, 0.56
OUT_ROWS, IN_ROWS = 256, 768
# NGC 4414's five measured segments: pitch in degrees and radial range in arcsec, S4G 3.6 micron, deprojected
# [verified: Herrera-Endoqui et al. 2015, A&A 582, A86, Table 3 at VizieR J/A+A/582/A86/table3;
# docs/READING_ARM_SEGMENTS.md A1.4]. Their ranges overlap - pieces of different arms - so nothing positional is
# pinned of them (D218 item 6): a disclosed check of the drawn segments' spread.
NGC_4414_SEGMENTS = ((-30.5, 28.7, 63.6), (-34.2, 19.4, 57.3), (-28.1, 32.7, 87.4), (-44.0, 29.2, 54.4), (-7.6, 57.9, 66.3))
_RUNS: dict[object, object] = {}
_ROWS: dict[int, tuple[np.ndarray, np.ndarray]] = {}


def the_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def inputs_of(template: str, **more) -> dict:
    return {**templates.overrides(templates.TEMPLATES[template]), **more}


def drawn_pitch(template: str, **more) -> dict:
    """The template's inputs with its pitch pin taken off - its other pins kept: the galaxy at the pitch its law draws."""
    return {k: v for k, v in inputs_of(template, **more).items() if k != "pitch_angle"}


def template_run(prod, template: str, **more):
    key = (template, tuple(sorted(more.items())))
    if key not in _RUNS:
        _RUNS[key] = run(the_model(prod), inputs_of(template, **more), only=PATTERN)
    return _RUNS[key]


def drawn_rows(prod, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """(extents in radians, unit normal deviates) of texture seed ``seed``, row by row on the rows' own streams -
    what ``arm_phases`` publishes (held to the published rows in the draw's test), without a run."""
    if seed not in _ROWS:
        numbers = tuple(float(constants(the_model(prod))[k]) for k in ap.SEGMENT_CONSTANTS)
        rows = [ap.draw_segment(_seeds.rng(seed, "arm_phases", "segment", way, j), *numbers) for way, j in ap.segment_streams()]
        _ROWS[seed] = (np.array([r[0] for r in rows]), np.array([r[1] for r in rows]))
    return _ROWS[seed]


def hand_knots(F) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(ln R at the knots, Φ at the knots, each segment's pitch in degrees), inside out, from the published rows,
    the published pitch, the published relative spread and the published anchor: this file's arithmetic, a loop,
    no function of the model's. A segment's pitch is p + (s p) z."""
    extent, deviate = np.asarray(F["arm_segment_extent"], dtype=float), np.asarray(F["arm_segment_pitch_deviate"], dtype=float)
    pitch, anchor, spread = float(F["pitch_angle"]), float(F["arm_winding_anchor_radius"]), float(F["arm_segment_pitch_scatter"])
    x0 = math.log(anchor)
    p0 = x0 / math.tan(math.radians(pitch))
    xs, ps, pitches = [x0], [p0], []
    for j in range(OUT_ROWS):  # outward from the anchor
        p = pitch + (spread * pitch) * deviate[j]
        t = math.tan(math.radians(p))
        xs.append(xs[-1] + extent[j] * abs(t))
        ps.append(ps[-1] + extent[j] * (1.0 if t > 0.0 else -1.0 if t < 0.0 else 0.0))
        pitches.append(p)
    inward_x, inward_p, inward_pitch = [], [], []
    x, ph = x0, p0
    for j in range(IN_ROWS):  # inward from the anchor
        p = pitch + (spread * pitch) * deviate[OUT_ROWS + j]
        t = math.tan(math.radians(p))
        x -= extent[OUT_ROWS + j] * abs(t)
        ph -= extent[OUT_ROWS + j] * (1.0 if t > 0.0 else -1.0 if t < 0.0 else 0.0)
        inward_x.append(x)
        inward_p.append(ph)
        inward_pitch.append(p)
    return np.array(inward_x[::-1] + xs), np.array(inward_p[::-1] + ps), np.array(inward_pitch[::-1] + pitches)


def hand_phase(knots: np.ndarray, phases: np.ndarray, R: float) -> float:
    """Φ at one radius: the segment the radius lies in, and the straight line in ln R across it."""
    x = math.log(R)
    k = int(np.searchsorted(knots, x, side="right")) - 1
    return float(phases[k] + (phases[k + 1] - phases[k]) * (x - knots[k]) / (knots[k + 1] - knots[k]))


# --- the constants and the declarations ----------------------------------------------------------------------------


def test_the_constants_are_the_ruling_s_and_the_segments_declare_what_they_are(prod):
    """D218 item 2 and the follow-up's item 2. The extent's four numbers are the reader's arithmetic on Honig &
    Reid's 38 rows. The spread of a segment's pitch is **relative**: 0.56 of the disc's own pitch, Savchenko et
    al. 2020's measured variation along an arm, in place of the absolute 10 degrees the first build drew - and
    the constant says the absolute form was built first and withdrawn, and why."""
    m = the_model(prod)
    c = constants(m)
    held = {"ARM_SEGMENT_EXTENT_MEDIAN": MEDIAN_HAND, "ARM_SEGMENT_EXTENT_LOG_SCATTER": LOG_SCATTER_HAND, "ARM_SEGMENT_EXTENT_MIN": LOW_HAND,
            "ARM_SEGMENT_EXTENT_MAX": HIGH_HAND}
    assert {k: c[k] for k in held} == held and tuple(held) == ap.SEGMENT_CONSTANTS == ap.ARM_PHASES.reads_constants
    for k in held:
        about = " ".join(m.constants[k].about.split())
        assert "Honig & Reid 2015" in about and "38 printed rows" in about and "[verified:" in about, k
    assert "The reader's arithmetic on Honig & Reid 2015's 38 printed rows".lower() in " ".join(m.constants["ARM_SEGMENT_EXTENT_MEDIAN"].about.split()).replace("**", "").lower()
    # The spread: the relative form, with its tag; the absolute constant is gone, and no stage of the layer reads a spread.
    assert "ARM_SEGMENT_PITCH_SCATTER" not in c and c["ARM_SEGMENT_PITCH_RELATIVE_SCATTER"] == RELATIVE_HAND
    spread = m.constants["ARM_SEGMENT_PITCH_RELATIVE_SCATTER"]
    about = " ".join(spread.about.split())
    assert spread.unit == "dimensionless" and "untruncated" in about
    assert "[verified: Savchenko, Marchuk, Mosenkov & Grishunin 2020, MNRAS 493, 390, arXiv:2001.09110; docs/READING_ARM_SEGMENTS.md A1.1: \"sd of local pitch over mean 0.56 +- 0.25\", 155 galaxies]" in about
    assert "The absolute form was built first and withdrawn at the gate's follow-up" in about.replace("**", "") and "net leading" in about and "D218" in about
    assert "ARM_SEGMENT_PITCH_RELATIVE_SCATTER" in pt.BAR.reads_constants and "ARM_SEGMENT_PITCH_RELATIVE_SCATTER" not in ap.ARM_PHASES.reads_constants
    scatter = pt.ARM_SEGMENT_PITCH_SCATTER
    assert (scatter.name, scatter.unit, scatter.provenance, scatter.kind) == ("arm_segment_pitch_scatter", "dimensionless", "derived", Kind.SCALAR)
    assert scatter in pt.BAR.publishes and "0.56" in scatter.about and "net leading" in scatter.about
    assert (pt.SEGMENTS_OUTWARD, pt.SEGMENTS_INWARD) == (OUT_ROWS, IN_ROWS) and ap.MAX_EXTENT_DRAWS == 16
    for decl in ap.ARM_SEGMENTS:
        assert decl.provenance == "synthetic" and decl.of == "arm_segment"
        # A table's column, not a catalogue's: read whole by the model's own stages, drawn by nothing.
        assert decl.kind is Kind.TABLE_COLUMN and decl.kind.domain == "table" and decl.ramp is None
        assert "not shown by the viewer" in decl.about and "Not drawn by the viewer" not in decl.about
        assert "kinks of real spiral arms" in decl.stands_in_for and "common rings for every arm" in decl.stands_in_for
        assert "Every ring's mean and every mode's amplitude" in decl.conserves and "the gas law's strength" in decl.conserves
        assert "untruncated" in decl.statistic and "38 printed rows" in decl.statistic and "0.56 +- 0.25 over 155 galaxies" in decl.statistic
        assert "Savchenko" in decl.statistic and "withdrawn" in decl.statistic
    # The rows hold no pitch: an extent in radians and a unit normal, by name and by unit.
    assert [(d.name, d.unit) for d in ap.ARM_SEGMENTS] == [("arm_segment_extent", "rad"), ("arm_segment_pitch_deviate", "dimensionless")]
    assert [d.name for d in ap.ARM_SEGMENTS] == list(pt.SEGMENT_FIELDS) and ap.ARM_PHASES.reads_seeds == ("texture_seed",)
    assert pt.WINDING_FIELDS == ("arm_winding_anchor_radius", "arm_segment_pitch_scatter", *pt.SEGMENT_FIELDS)
    assert set(pt.WINDING_FIELDS) <= set(pt.PATTERN_READS) and set(pt.WINDING_FIELDS) <= set(gm.GAS_PATTERN_READS)
    # The censuses that build the young stars' reader declare what its winding reads: the pattern's own tuple.
    for stage in ("systems", "bright_stars"):
        assert {"pitch_angle", *pt.WINDING_FIELDS} <= set(prod[1].get(stage).requires), stage
    assert ap.segment_streams()[:2] == (("out", 0), ("out", 1)) and ap.segment_streams()[OUT_ROWS] == ("in", 0) and len(ap.segment_streams()) == OUT_ROWS + IN_ROWS


def test_the_draw_is_redrawn_outside_the_sample_s_range_and_never_clipped(prod):
    """D218 item 2: the extent "log-normal with median 60° and σ_ln 0.35, redrawn outside 20°–180°"; the residual
    "independent per segment, untruncated". The redraw has a fixed count (rule A1): at most 16 extents a segment,
    and the stage raises if all sixteen fall outside (4e-45 a segment) - it does not clip.
    **Counted**: over 100 texture seeds' 102 400 rows, 167 extents were drawn again (0.16 %) and no segment needed
    more than two draws. The deviate is drawn first, so it does not depend on the redraws. Each row is its own
    stream - ("segment", "out", j) and ("segment", "in", j), j = 0 at the anchor - so the published rows are these
    draws whatever the grid, and a row does not move when more rows are laid.

    **The unit normal rows are the first build's residual rows, the same draw** (the follow-up's item 2: "keep
    the same streams so the extent rows keep their bits"). The first build drew ``normal(0, 10)`` first on each
    stream; this one draws ``normal()``, the same deviate of the same generator, so: ten times a row is the old
    residual **bit for bit on every row**; the row is the old residual over ten bit for bit on 87.7 % of rows
    (8 984 of ten texture seeds' 10 240) and one unit in the last place off on the rest (a division's
    rounding); and the extent that follows is the same bits, on every row - read here on the rows whose first
    extent stood (10 217; the other 23 redrew it, as they did before). The 768 rows a texture seed lays that
    the first build did not are new streams."""
    numbers = tuple(float(constants(the_model(prod))[k]) for k in ap.SEGMENT_CONSTANTS)
    assert len(numbers) == 4
    rows, redraws, most, extents, deviates = 0, 0, 0, [], []
    for seed in range(100):
        for way, j in ap.segment_streams():
            extent, deviate, attempts = ap.draw_segment(_seeds.rng(seed, "arm_phases", "segment", way, j), *numbers)
            rows, redraws, most = rows + 1, redraws + attempts - 1, max(most, attempts)
            extents.append(math.degrees(extent))
            deviates.append(deviate)
    extents, deviates = np.array(extents), np.array(deviates)
    assert (rows, redraws, most) == (102400, 167, 2)
    assert LOW_HAND <= extents.min() and extents.max() <= HIGH_HAND
    assert float(np.median(extents)) == pytest.approx(60.0, abs=0.6) and float(np.std(np.log(extents))) == pytest.approx(0.35, abs=0.01)
    assert (float(deviates.mean()), float(deviates.std())) == pytest.approx((0.0, 1.0), abs=0.01)
    assert deviates.min() < -3.5 and deviates.max() > 3.5  # untruncated: beyond 3.5 sigma both ways
    # The reversed share of the rows is the normal's tail under -1/0.56, at every pitch the tangent does not wrap.
    tail = 0.5 * math.erfc((1.0 / RELATIVE_HAND) / math.sqrt(2.0))
    assert tail == pytest.approx(0.03707, abs=1e-5) and float((deviates < -1.0 / RELATIVE_HAND).mean()) == pytest.approx(tail, abs=0.002)
    # A generator that always draws outside the range exhausts the count and raises.
    class Stuck:
        def normal(self, *args):
            return 100.0

    with pytest.raises(ArithmeticError, match="16 times running"):
        ap.draw_segment(Stuck(), *numbers)
    # The same draw as the absolute form's, row by row: its residual was normal(0, 10) on the same stream, first.
    same, exact, within_one = 0, 0, 0
    for seed in range(10):
        for way, j in ap.segment_streams():
            extent, deviate, _ = ap.draw_segment(_seeds.rng(seed, "arm_phases", "segment", way, j), *numbers)
            old = _seeds.rng(seed, "arm_phases", "segment", way, j)
            residual = float(old.normal(0.0, 10.0))
            first_extent = MEDIAN_HAND * math.exp(LOG_SCATTER_HAND * float(old.normal()))
            assert residual == 10.0 * deviate, (seed, way, j)
            if LOW_HAND <= first_extent <= HIGH_HAND:
                assert math.radians(first_extent) == extent, (seed, way, j)
                same += 1
            exact += residual / 10.0 == deviate
            within_one += abs(residual / 10.0 - deviate) <= math.ulp(deviate)
    assert (same, exact, within_one) == (10217, 8984, 10240)  # 23 of the 10 240 rows redrew their extent; 87.7 % exact
    # The published rows are these draws: the default galaxy on two grids.
    for grid in (None, SMALL):
        o = run(the_model(prod), {"texture_seed": 3}, grid, only=pt.SEGMENT_FIELDS)
        want = drawn_rows(prod, 3)
        assert np.asarray(o.fields["arm_segment_extent"]).tolist() == want[0].tolist()
        assert np.asarray(o.fields["arm_segment_pitch_deviate"]).tolist() == want[1].tolist()
    off = run(the_model(prod), {"texture_seed": 3}, SMALL, only=pt.WINDING_FIELDS, layer=False)
    assert np.asarray(off.fields["arm_segment_extent"]).size == 0 and np.asarray(off.fields["arm_segment_pitch_deviate"]).size == 0
    assert float(off.fields["arm_segment_pitch_scatter"]) == RELATIVE_HAND  # a law's number: the same with the layer off
    assert pt.Winding.from_fields({**dict(off.fields), "pitch_angle": 13.5}) is None  # no segment: the plain winding


# --- by hand ---------------------------------------------------------------------------------------------------------


def test_the_winding_by_hand_on_a_seed_with_a_reversed_segment(prod):
    """D218 items 1-3, from the **published** numbers with this file's arithmetic: the Milky Way template at
    texture seed 7, whose winding holds a reversed segment inside the solar circle.

    Φ(R_A) = ln R_A · cot p at the anchor (the bar's half-length, 5.2097 kpc; p = 13.538°) - the bar's angle,
    6.85498 rad, exactly as it was. From there each segment of pitch p (1 + 0.56 z) spans Δβ |tan p_seg| in ln R
    and turns the phase by Δβ, outward - back, where the pitch is negative. As read, the segments over 3-12 kpc:

        R kpc             pitch°    (the first ends at the anchor; the third is reversed)
        2.902 - 5.210     27.77
        5.210 - 6.499     11.44
        6.499 - 7.529     −7.02
        7.529 - 8.806     11.12
        8.806 - 11.142     8.18
        11.142 - 12.369    5.49

    (With the absolute residual of the first build the same rows read 32.31, 10.78, −13.58, 10.35, 6.48, 2.92:
    the same deviates, 10° apiece in place of 7.58°.) Φ is the straight line in ln R across each segment:
    continuous at every knot, its slope cot(p_seg) jumping there and nowhere else. The module's Φ is the hand's
    at every grid ring to 1e-12; across the reversed segment Φ falls as R grows. Past the bar's body the
    published stellar field is 1 + Σ A_m cos(m (φ − Φ) − θ_m) with the hand's Φ; the two-armed mode's crest at
    R = a lies on the bar's axis; and the Sun stands 30° behind the bar's near end in the sense of rotation - at
    a larger azimuth, since the disc turns towards smaller ones."""
    o = template_run(prod, "milky_way", texture_seed=7)
    F, R, phi = o.fields, o.grid.R, o.grid.phi
    pitch, anchor, a = float(F["pitch_angle"]), float(F["arm_winding_anchor_radius"]), float(F["bar_half_length"])
    assert (pitch, anchor) == pytest.approx((13.5378, 5.2097), abs=5e-5) and anchor == a
    assert float(F["arm_segment_pitch_scatter"]) == RELATIVE_HAND and RELATIVE_HAND * pitch == pytest.approx(7.581, abs=1e-3)
    knots, phases, pitches = hand_knots(F)
    assert knots.size == OUT_ROWS + IN_ROWS + 1 and np.all(np.diff(knots) >= 0.0)
    bar_angle = math.log(a) / math.tan(math.radians(pitch))
    assert phases[IN_ROWS] == bar_angle == pytest.approx(6.85498, abs=1e-5)
    radii = np.exp(knots)
    on = (radii[1:] > 3.0) & (radii[:-1] < 12.0)
    assert np.round(radii[:-1][on], 3).tolist() == [2.902, 5.21, 6.499, 7.529, 8.806, 11.142]
    assert np.round(pitches[on], 2).tolist() == [27.77, 11.44, -7.02, 11.12, 8.18, 5.49]
    # The same rows under the absolute form the first build drew: p + 10 z.
    absolute = pitch + 10.0 * (pitches[on] - pitch) / (RELATIVE_HAND * pitch)
    assert np.round(absolute, 2).tolist() == [32.31, 10.78, -13.58, 10.35, 6.48, 2.92]
    # The module's winding is the hand's: its knots, and Φ on every grid ring.
    w = compose.stellar_pattern(F, R).winding
    assert np.allclose(w.knots, knots, rtol=0.0, atol=1e-12) and np.allclose(w.phases, phases, rtol=0.0, atol=1e-12)
    by_hand = np.array([hand_phase(knots, phases, float(r)) for r in R])
    assert float(np.abs(w.phase(R) - by_hand).max()) < 1e-12
    # Continuous at every knot, by both neighbours' lines; the slope is the segment's cotangent and jumps at the knots.
    k = IN_ROWS + 1  # the knot at 6.499 kpc, the first past the anchor, where the pitch turns from 11.44° to −7.02°
    assert math.exp(knots[k]) == pytest.approx(6.499, abs=5e-4)
    left = phases[k - 1] + (knots[k] - knots[k - 1]) / math.tan(math.radians(pitches[k - 1]))
    right = phases[k + 1] - (knots[k + 1] - knots[k]) / math.tan(math.radians(pitches[k]))
    assert abs(left - phases[k]) < 1e-12 and abs(right - phases[k]) < 1e-12
    inside = (np.log(R) > knots[k]) & (np.log(R) < knots[k + 1])
    assert int(inside.sum()) == 13 and np.all(np.diff(by_hand[inside]) < 0.0)  # the reversed segment: Φ falls outward
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


# --- the predictions (B4), the follow-up's predictions, and the gate ------------------------------------------------


def test_the_gate_s_predictions_as_measured(prod):
    """D218's predictions (B4), read before the build was judged; nothing was changed to make one hold. Re-read
    here on the residual relative to the pitch (the follow-up's item 2), the first build's readings beside them.

    "Milky Way: about 5–6 segments over 3–12 kpc, ~9 % reversed and ~9 % under 2.7°". **As built**, over 100
    texture seeds of the template: 6.54 segments over 3-12 kpc on average (6.39 on the absolute form; median 6:
    held; the default seeds themselves lay 8 - twelve on the absolute form); of the segments that cross the
    grid, **3.83 % reversed and 6.48 % under 2.7°** - the absolute form read 9.30 % and 8.76 %, as predicted of
    it; the relative form's reversed tail is the normal's under −1/0.56, 3.7 %, and the prediction was of the
    form that was withdrawn. "The bar's angle, the body, the lanes ...
    bit-identical": the bar's angle is ln a · cot p to the bit, the anchor's phase. "The m = 2 crest at R = a on
    the bar's axis on every seed": held (the gate, below). "The Reid check a miss by 2–4 widths": the verdict is
    withdrawn (the check's own test). ``ngc_4414`` at 28.9°: "ε × 1.96 and f × 0.51 on every ring" - **as built
    both ε and f are × 0.5121**, sin 14.33°/sin 28.9°: ε = a/(κ R sin p) falls as the pitch opens, as f does; the
    prediction's 1.96 is the inverse of the factor (the gate's follow-up, item 5: "my '×1.96' was a slip")."""
    model = the_model(prod)
    o = template_run(prod, "milky_way")
    pitch, anchor = float(o.fields["pitch_angle"]), float(o.fields["arm_winding_anchor_radius"])
    R = o.grid.R
    counts, pitches = [], []
    for seed in range(100):
        w = pt.Winding(pitch, RELATIVE_HAND, anchor, *drawn_rows(prod, seed))
        inner, outer, segment_pitch, _ = w.segments(float(R[0]), float(R[-1]))
        counts.append(int(((outer > 3.0) & (inner < 12.0)).sum()))
        pitches.extend(segment_pitch.tolist())
    pitches = np.array(pitches)
    # The first of them is the template's own winding, as its run publishes it.
    published = pt.Winding.from_fields(o.fields)
    assert np.array_equal(published.knots, pt.Winding(pitch, RELATIVE_HAND, anchor, *drawn_rows(prod, 0)).knots)
    read = (counts[0], float(np.mean(counts)), float(np.median(counts)), 100.0 * float((pitches < 0.0).mean()), 100.0 * float((np.abs(pitches) < 2.7).mean()))
    assert read == pytest.approx((8, 6.54, 6.0, 3.83, 6.48), abs=0.006), read
    # NGC 4414: the gas law's two numbers at the pinned pitch against the drawn one's.
    pinned = template_run(prod, "ngc_4414")
    drawn = run(model, drawn_pitch("ngc_4414"), only=PATTERN)
    R = pinned.grid.R
    a, b = (compose.gas_pattern(o.fields, R, constants(model)) for o in (pinned, drawn))
    factor = math.sin(math.radians(float(drawn.fields["pitch_angle"]))) / math.sin(math.radians(28.9))
    assert factor == pytest.approx(0.5121, abs=1e-4) and 1.0 / factor == pytest.approx(1.953, abs=1e-3)
    assert np.allclose(a.epsilon() / b.epsilon(), factor, rtol=1e-13, atol=0.0)
    fa, fb = a.forcing_amplitudes(), b.forcing_amplitudes()
    assert np.allclose(fa[fb != 0.0] / fb[fb != 0.0], factor, rtol=1e-13, atol=0.0)


def test_the_follow_up_s_predictions_as_measured(prod):
    """The follow-up to the gate, item 2, changed the form of the residual "on a source, not on the look", and
    predicted what the relative form would read. **Read before they were judged; nothing was changed to make one
    hold.** Over 1000 texture seeds (0-999), the Milky Way template's anchor (5.2097 kpc), the arms' net turn
    taken from 3 to 12 kpc, Φ(12) − Φ(3), at each pitch - the independent review's measurement, which read on the
    absolute form a median turn of 264° at 13.5° (10-90 %: 132-378) against the law's 330°, and 2 %, 14 % and 34 %
    of seeds net leading at 10°, 5° and 2°.

    1. *"The reversed fraction is then 3.7 % at every pitch"* (P(z < −1/0.56) = 3.707 %). Over the 1 024 000 rows:
       3.729 % - **held of the rows**. Of the segments that cross 3-12 kpc: 3.72 % at 1°, 3.71 % at 2°, 3.58 % at
       5°, 3.43 % at 10°, 3.59 % at 13.54°, 3.43 % at 28.9° - held. **Not held above about 35°**: a segment's
       pitch past 90° is a line's inclination read back the other way, so the phase recedes there too: 7.33 % at
       45° and 23.32 % at 60°, the pin's upper bound. The pitch law draws nothing there (mean 14°, scatter 6°).
    2. *"Net-leading windings vanish at any pitch above ~1°"*. **Held from 1° to 13.54°: none of 1000 seeds** at
       1°, 2°, 5°, 10° or 13.54° (the absolute form: 34 %, 14 %, 2 % at 2°, 5°, 10°). **Not held at the open end**:
       7 of 1000 at 28.9° - ``ngc_4414``'s pinned pitch, where only three or four segments span 3-12 kpc and the
       spread is 16° - 38 at 45° and 149 at 60°. Recorded, not tuned: the residual is untruncated and no mean
       winding rate is enforced.
    3. *"The median net turn over 3–12 kpc within about 10 % of the law's 330° at 13.5°"*: **311.8°, 5.5 % under
       the law's 329.9° - held** (10-90 %: 212-412°). At the other pitches the median is 0.911-0.963 of the law.
    4. *"The median |Δψ| there ≈ 7° against Honig & Reid's 9.7°, a predicted small miss"*: **7.22° - as
       predicted, a miss of the measured 9.7° by a quarter.**
    5. *"The Milky Way default seeds being the most extreme of 1000 is a fact about one realisation"*: on the
       relative form the template's default texture seed turns **511.7° from 3 to 12 kpc, the 987th of 1000**
       (the 999th on the absolute form, 695°), and lays **8 segments** there where the median is 6 (ranks
       764-907: 93 seeds lay more). Still an outlier in its turn; nothing is re-seeded."""
    o = template_run(prod, "milky_way")
    pitch, anchor = float(o.fields["pitch_angle"]), float(o.fields["arm_winding_anchor_radius"])
    assert (pitch, anchor) == pytest.approx((13.5378, 5.2097), abs=5e-5)
    seeds = 1000
    deviates = np.concatenate([drawn_rows(prod, seed)[1] for seed in range(seeds)])
    tail = 0.5 * math.erfc((1.0 / RELATIVE_HAND) / math.sqrt(2.0))
    assert deviates.size == 1024000 and 100.0 * tail == pytest.approx(3.707, abs=5e-4)
    assert 100.0 * float((deviates < -1.0 / RELATIVE_HAND).mean()) == pytest.approx(3.729, abs=5e-4)

    def read(at: float):
        turns, counts, reversed_, steps = [], [], [], []
        for seed in range(seeds):
            w = pt.Winding(at, RELATIVE_HAND, anchor, *drawn_rows(prod, seed))
            turns.append(math.degrees(float(np.diff(w.phase(np.array([3.0, 12.0])))[0])))
            _, _, segment_pitch, _ = w.segments(3.0, 12.0)
            counts.append(segment_pitch.size)
            reversed_.extend((np.tan(np.radians(segment_pitch)) < 0.0).tolist())
            steps.extend(np.abs(np.diff(segment_pitch)).tolist())
        return np.array(turns), np.array(counts), np.array(reversed_), np.array(steps)

    # pitch: (the law's turn, the median turn, net-leading seeds of 1000, reversed % of the segments over 3-12 kpc)
    as_read = {1.0: (4550.5, 4147.1, 0, 3.72), 2.0: (2274.5, 2071.4, 0, 3.71), 5.0: (907.9, 837.9, 0, 3.58), 10.0: (450.5, 422.5, 0, 3.43),
               pitch: (329.9, 311.8, 0, 3.59), 28.9: (143.9, 134.9, 7, 3.43), 45.0: (79.4, 76.5, 38, 7.33), 60.0: (45.9, 43.9, 149, 23.32)}
    for at, (law_turn, median_turn, leading, reversed_pct) in as_read.items():
        turns, counts, reversed_, steps = read(at)
        law = math.degrees(math.log(12.0 / 3.0) / math.tan(math.radians(at)))
        got = (law, float(np.median(turns)), int((turns < 0.0).sum()), 100.0 * float(reversed_.mean()))
        assert got == pytest.approx((law_turn, median_turn, leading, reversed_pct), abs=0.06), (at, got)
        assert 0.90 < got[1] / law < 0.97, (at, got)  # the median winds 3-10 % short of the law at every pitch
        if at == pitch:
            # Prediction 3 (within about 10 % of the law: held), 4 (about 7 degrees: as predicted) and 5 (the rank).
            assert abs(got[1] / law - 1.0) < 0.10 and np.percentile(turns, [10, 90]).tolist() == pytest.approx([212.4, 411.9], abs=0.6)
            assert float(np.median(steps)) == pytest.approx(7.22, abs=0.006) and (float(counts.mean()), float(np.median(counts))) == pytest.approx((6.431, 6.0), abs=1e-3)
            assert turns[0] == pytest.approx(511.68, abs=0.01) and int((turns < turns[0]).sum()) + 1 == 987
            assert int(counts[0]) == 8 and (int((counts < 8).sum()) + 1, int((counts <= 8).sum())) == (764, 907)
    # Predictions 1 and 2, as worded: held where the tangent does not wrap, not above.
    assert all(abs(as_read[at][3] - 3.707) < 0.3 for at in (1.0, 2.0, 5.0, 10.0, pitch, 28.9)) and as_read[45.0][3] > 7.0
    assert all(as_read[at][2] == 0 for at in (1.0, 2.0, 5.0, 10.0, pitch)) and as_read[28.9][2] == 7


LEGS = ("milky_way", "ngc_4414", "ngc_4414 drawn")
# The scalars that are not numbers, as ruled: an unbarred galaxy's bar (D217 item 3, D164) and the Sun's azimuth
# without a bar or without the pin (D218 item 5). A barred, pinned galaxy has none.
UNBARRED_NAN = {"bar_half_length", "bar_axis_ratio", "bar_boxiness", "bar_profile_index", "bar_contrast", "bar_mass_share",
                "bar_corotation_radius", "bar_pattern_speed", "sun_azimuth"}
STEP = 1e-6  # in ln R: how far inside and outside a knot the winding is read for its continuity


def knot_jumps(w, knots: np.ndarray, phases: np.ndarray, pitches: np.ndarray, lo: float, hi: float) -> tuple[float, int, int]:
    """(the worst departure over its tolerance, the knots read, the knots skipped) for the knots between the radii
    ``lo`` and ``hi``: **the module's Φ a step inside and a step outside each knot, against the knot's own Φ
    carried a step along each neighbouring segment's own slope** - cot of the segment's pitch, the hand's. A jump
    of Φ at a knot would show whole; a wrong slope on either side would show as the step times the error. A knot
    whose neighbour is shorter than two steps is skipped (and counted). The tolerance is 1e-12 and the rounding of
    the radius itself, 1e-14 of the slope: the gate's "continuous to 1e-12" wherever the slope is under 100, and
    the slope's own rounding beside a nearly circular segment (the worst read on the 360: 5e-11 beside a slope
    of 34 000, a segment of 0.002 degrees of pitch)."""
    worst, read, skipped = 0.0, 0, 0
    for k in range(1, knots.size - 1):
        if not math.log(lo) < knots[k] < math.log(hi):
            continue
        if min(knots[k] - knots[k - 1], knots[k + 1] - knots[k]) < 2.0 * STEP:
            skipped += 1
            continue
        below, above = 1.0 / math.tan(math.radians(pitches[k - 1])), 1.0 / math.tan(math.radians(pitches[k]))
        inside, at, outside = (float(v) for v in w.phase(np.exp(np.array([knots[k] - STEP, knots[k], knots[k] + STEP]))))
        # (At the knot itself the radius is e^x read back through a logarithm: a rounding of x to either side, on
        # the steeper neighbour's slope - 3e4 beside a segment of 0.002 degrees of pitch.)
        for got, want, slope in ((inside, phases[k] - STEP * below, below), (outside, phases[k] + STEP * above, above), (at, phases[k], max(abs(below), abs(above)))):
            worst = max(worst, abs(got - want) / (1e-12 + 1e-14 * abs(slope)))
        read += 1
    return worst, read, skipped


def test_gate_on_the_three_legs_of_the_suite_s_galaxies(prod):
    """"Every ring mean 1 (stellar 1e-12 on cells, gas 1e-13) on the 240 seeds and both templates; every
    ``arm_mode_amplitude_m`` bit-identical layer on and off; Φ continuous to 1e-12 at each kink; φ_bar = Φ(a) to
    rounding on every barred seed; the point function and the grid agree; the segment statistics re-measured on
    the 240 seeds ... read as checks of the draw, with the sub-grid segments (d ln R under one ring step) counted".
    The follow-up to the gate: "with the relative residual the gate range becomes 2–8 % reversed over the 240 and
    over the pitch law's population, re-measured and read" (item 4), and "the drawn-pitch unbarred family
    (``ngc_4414``'s inputs with the pitch pin off, 60 × 2 seeds) becomes the third leg of the gate sweeps" (item
    6): with ``ngc_4414`` pinned at 28.9° the suite had lost its tightly wound unbarred galaxies.

    **Three legs, 60 pattern seeds × 2 texture seeds each**: the Milky Way template (barred, the pitch drawn:
    1.0°-24.3°), ``ngc_4414`` (unbarred, pinned at 28.9°) and ``ngc_4414`` with its pitch pin taken off (unbarred,
    the pitch drawn: 1.0°-24.1°). On every one of the 360: nothing raises; the stellar ring means are 1 to 1e-12
    and the gas's to 2e-13; the stellar field is positive and the gas's is not negative (its exact zeros
    counted); no bit of an amplitude moves with the layer; Φ is continuous at every knot on the grid, read a step
    inside and a step outside by the neighbours' own slopes; the published stellar field past the bar's body is
    the arm modes on this file's own winding, at the cells' centres, and the published gas field on sampled
    rings is the point function averaged over each cell by quadrature; and no field holds a NaN but the ruled
    ones. The reviewer found two of the first build's assertions here vacuous (a table interpolated at its own
    knots; the grid rebuilt by the grid's own methods): both are replaced by the above.

    **As read.** Ring means: stellar 1.6e-15, gas 1.0e-13 at worst. The amplitudes: no bit moves. Φ(a) − φ_bar: 0,
    exactly. Φ across 11 580 knots on the grid: within 0.48 of the tolerance at worst, none skipped. The stellar
    field against the hand's point function: 1.3e-12 (the rounding of Φ, which runs to thousands of radians at a
    pitch of 1°). The gas field against the quadrature: 8.6e-6. No NaN but an unbarred galaxy's bar and Sun.
    **The reversed fraction**, of the segments that cross the grid. The gate's range, as ruled: **the suite's 240
    pooled 2.80 % (186 of 6 638); the three legs pooled 3.03 % (362 of 11 940); the pitch law's population - the
    default inputs' 60 pattern seeds at ten texture seeds - 3.81 % (972 of 25 511). Inside 2–8 % on all three.**
    Leg by leg: the Milky Way's 3.66 % and the drawn-pitch leg's 3.32 %, inside; **``ngc_4414``'s pinned leg 0 %,
    outside** - and there the explanation the first build gave for both legs is the true one: at one pinned pitch
    the leg's 120 galaxies are two windings, the suite's two texture seeds', 13 segments each, and neither holds
    a row under −1/0.56. (On the absolute form the Milky Way's leg read 17.4 %, and that was not the two texture
    seeds, as the first build's comment had it: a galaxy drawn at a low pitch reversed far more, 10° of residual
    on 2° of pitch. On the relative form the fraction is 3.7 % at every pitch the tangent does not wrap.)
    **The extent's median** 59.9°, 64.8° and 59.1° (inside 50°–80°). **The median |Δψ|** between neighbours:
    12.1° on the pinned leg (0.56 × 28.9° × √2 × 0.674 = 15.4° expected of many rows; two windings here) and
    **3.3° and 3.1° on the two drawn-pitch legs, outside the first gate's 7°–13°**: the step is the spread's,
    0.56 of each galaxy's own pitch, and a leg's segments are mostly its tightly wound galaxies' (a disc at 1°
    lays fourteen times the segments of one at 14°). At 13.5° it is 7.2° (the follow-up's own prediction, read
    in its test). **Segments holding no grid ring**: 1 445 of 5 078, 180 of 1 560 and 1 542 of 5 302.
    **The third leg's extremes** (and the first's beside them): the lowest pitch 1.0° on both drawn legs
    (pattern seed 22, the draw's floor; the highest 24.1° and 24.3°); the gas's contrast nowhere negative and
    nowhere exactly zero - its least value 2.3e-21 (2.6e-23 on the pinned leg, 2.1e-3 on the Milky Way's) - and
    its largest 10.91 (8.22 on the Milky Way's leg, 4.35 on the pinned one); **9
    galaxies of the third leg with a ring on its convergence floor**, 7 of the Milky Way's, none of the pinned."""
    model = the_model(prod)
    c = constants(model)
    read: dict[str, dict[str, list]] = {leg: {"extent": [], "reversed": [], "step": [], "sub": [], "pitch": [], "gas": [], "zeros": [], "floor": [], "knots": [], "skipped": []} for leg in LEGS}
    worst = {"stars": 0.0, "gas": 0.0, "bar": 0.0, "knot": 0.0, "field": 0.0, "cells": 0.0}
    for leg in LEGS:
        got = read[leg]
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                more = dict(pattern_seed=pattern_seed, texture_seed=texture_seed)
                given = drawn_pitch("ngc_4414", **more) if leg == "ngc_4414 drawn" else inputs_of(leg, **more)
                o = run(model, given, only=PATTERN)
                F, R, phi, edges = o.fields, o.grid.R, o.grid.phi, o.grid["phi"].edges
                label = (leg, pattern_seed, texture_seed)
                stars, gas = np.asarray(F["pattern_density_contrast"]), np.asarray(F["gas_density_contrast"])
                worst["stars"] = max(worst["stars"], float(np.abs(stars.mean(axis=1) - 1.0).max()))
                worst["gas"] = max(worst["gas"], float(np.abs(gas.sum(axis=1) / gas.shape[1] - 1.0).max()))
                assert stars.min() > 0.0 and gas.min() >= 0.0, label
                got["gas"].append((float(gas.min()), float(gas.max())))
                got["zeros"].append(int((gas == 0.0).sum()))
                # No NaN but the ruled ones: every array whole, and the scalars that are not numbers the ruled set.
                nan = {n for n, v in F.items() if not isinstance(v, str) and np.isnan(np.asarray(v, dtype=float)).any()}
                assert nan == (set() if leg == "milky_way" else UNBARRED_NAN), (label, sorted(nan))
                sp, gp = compose.stellar_pattern(F, R), compose.gas_pattern(F, R, c)
                off = run(model, given, only=pt.AMPLITUDE_FIELDS, layer=False).fields
                assert all(np.asarray(off[k]).tobytes() == np.asarray(F[k]).tobytes() for k in pt.AMPLITUDE_FIELDS), label
                # The winding, by hand from the published rows: the module's knots are the hand's, and Φ is
                # continuous across every knot on the grid, by the segments' own slopes.
                w = sp.winding
                knots, phases, pitches = hand_knots(F)
                assert np.allclose(w.knots, knots, rtol=0.0, atol=1e-11) and np.allclose(w.phases, phases, rtol=0.0, atol=1e-10), label
                jump, on_grid, skipped = knot_jumps(w, knots, phases, pitches, float(R[0]), float(R[-1]))
                worst["knot"] = max(worst["knot"], jump)
                got["knots"].append(on_grid)
                got["skipped"].append(skipped)
                # The published stellar field against the point function, evaluated independently: past the
                # bar's body it is the arm modes at the cells' centres, on the hand's winding.
                a = float(F["bar_half_length"])
                past = R > 1.01 * a if leg == "milky_way" else np.ones(R.size, dtype=bool)
                by_hand = np.interp(np.log(R[past]), knots, phases)
                arms = np.ones((int(past.sum()), phi.size))
                for m in (2, 3, 4, 5, 6):
                    arms += np.asarray(F[f"arm_mode_amplitude_{m}"])[past, None] * np.cos(m * (phi[None, :] - by_hand[:, None]) - float(F[f"arm_mode_phase_{m}"]))
                worst["field"] = max(worst["field"], float(np.abs(stars[past] - arms).max()))
                # The published gas field against the gas's point function: on every fortieth ring, the point
                # function averaged over each grid cell by a midpoint rule of 64 samples - not the exact integral
                # the stage publishes, so the two agree to the rule's error.
                rings = np.arange(5, R.size, 40)
                samples = (edges[:-1, None] + (edges[1:] - edges[:-1])[:, None] * ((np.arange(64) + 0.5) / 64.0)[None, :]).ravel()
                point = gp.contrast_at(R[rings][:, None], samples[None, :]).reshape(rings.size, phi.size, 64).mean(axis=2)
                worst["cells"] = max(worst["cells"], float(np.abs(point - gas[rings]).max()))
                if leg == "milky_way":
                    worst["bar"] = max(worst["bar"], abs(float(w.phase(np.array([a]))[0]) - sp.bar_angle))
                    assert float(F[pt.phase_field(2)]) == 0.0 and w.anchor_phase == sp.bar_angle, label
                inner, outer, pitch, extent = w.segments(float(R[0]), float(R[-1]))
                got["extent"].extend(np.degrees(extent).tolist())
                got["reversed"].extend((np.tan(np.radians(pitch)) < 0.0).tolist())
                got["step"].extend(np.abs(np.diff(pitch)).tolist())
                got["sub"].append(sum(1 for lo, hi in zip(inner, outer) if not ((R >= lo) & (R < hi)).any()))
                got["pitch"].append(float(F["pitch_angle"]))
                d = gp.diagnostics
                got["floor"].append(int((d.floor > 1e-10).sum()) if d is not None else 0)
    record, least = {}, {}
    for leg in LEGS:
        got = read[leg]
        extent, reversed_ = np.array(got["extent"]), np.array(got["reversed"])
        gas = np.array(got["gas"])
        least[leg] = float(gas[:, 0].min())
        record[leg] = (extent.size, round(float(np.median(extent)), 2), round(100.0 * float(reversed_.mean()), 2), round(float(np.median(got["step"])), 2),
                       sum(got["sub"]), round(min(got["pitch"]), 3), round(max(got["pitch"]), 3), round(float(gas[:, 1].max()), 3),
                       sum(got["zeros"]), sum(1 for n in got["floor"] if n), sum(got["knots"]), sum(got["skipped"]))
    suite = np.array(read["milky_way"]["reversed"] + read["ngc_4414"]["reversed"])
    pooled = np.array(sum((read[leg]["reversed"] for leg in LEGS), []))
    # ... and the pitch law's population: the default inputs' 60 pattern seeds at ten texture seeds.
    population = []
    for pattern_seed in range(60):
        o = run(model, {"pattern_seed": pattern_seed}, only=("pitch_angle", "arm_winding_anchor_radius"))
        for texture_seed in range(10):
            w = pt.Winding(float(o.fields["pitch_angle"]), RELATIVE_HAND, float(o.fields["arm_winding_anchor_radius"]), *drawn_rows(prod, texture_seed))
            population.extend((np.tan(np.radians(w.segments(float(o.grid.R[0]), float(o.grid.R[-1]))[2])) < 0.0).tolist())
    population = np.array(population)
    counts = (suite.size, int(suite.sum()), pooled.size, int(pooled.sum()), population.size, int(population.sum()))
    assert worst["stars"] < 1e-12 and worst["gas"] < 2e-13 and worst["bar"] == 0.0, worst
    # Φ across the knots (0.48 of its tolerance at worst); the stellar field against the hand's point function, to the
    # rounding of Φ itself, which is thousands of radians at a pitch of 1 degree (1.3e-12 at worst); the gas field
    # against the quadrature (8.6e-6 at worst: the midpoint rule's own error).
    assert worst["knot"] < 1.0 and worst["field"] < 1e-11 and worst["cells"] < 5e-5, worst
    # (segments on the grid, the extent's median°, reversed %, median |Δψ|°, segments holding no ring, the lowest and
    #  highest pitch°, the gas's largest value, its exact zeros, galaxies with a ring on its convergence floor,
    #  knots read for continuity, knots skipped as shorter than two steps)
    assert record == {
        "milky_way": (5078, 59.94, 3.66, 3.34, 1445, 1.0, 24.333, 8.223, 0, 7, 4958, 0),
        "ngc_4414": (1560, 64.8, 0.0, 12.1, 180, 28.9, 28.9, 4.347, 0, 0, 1440, 0),
        "ngc_4414 drawn": (5302, 59.09, 3.32, 3.11, 1542, 1.0, 24.096, 10.91, 0, 9, 5182, 0),
    }, record
    # The gas is nowhere negative and nowhere exactly zero: its least value on each leg.
    # (2e-23 is the response's own trough on a tightly forced ring, far above the smallest double: not an underflow.)
    assert all(v > 0.0 for v in least.values()) and least == pytest.approx({"milky_way": 2.1246e-3, "ngc_4414": 2.624e-23, "ngc_4414 drawn": 2.287e-21}, rel=2e-3, abs=0.0), least
    for leg in LEGS:
        assert 50.0 <= record[leg][1] <= 80.0, leg  # the extent's median, on every leg
    # The gate's 2-8 % reversed: over the suite's 240, over the three legs, and over the pitch law's population.
    assert counts == (6638, 186, 11940, 362, 25511, 972), counts
    assert [round(100.0 * float(x.mean()), 2) for x in (suite, pooled, population)] == [2.8, 3.03, 3.81]
    assert all(2.0 <= 100.0 * float(x.mean()) <= 8.0 for x in (suite, pooled, population))
    # ... and leg by leg it holds on the two legs whose pitch is drawn; the pinned leg reads none, of two windings.
    assert 2.0 <= record["milky_way"][2] <= 8.0 and 2.0 <= record["ngc_4414 drawn"][2] <= 8.0 and record["ngc_4414"][2] == 0.0


# --- the young stars' reader (the gate's ruling on the review's blocker: the law at a point) -----------------------

FINE = (np.arange(2880) + 0.5) * (2.0 * math.pi / 2880)  # the azimuths a ring's profile is read on, an eighth of a degree apart
ROUND = (np.arange(46080) + 0.5) * (2.0 * math.pi / 46080)  # the azimuths this file takes a ring's mean over: sixteen times the reader's
CELL_CENTRES = -math.pi + (np.arange(gm.CELLS) + 0.5) * (2.0 * math.pi / gm.CELLS)  # where the pattern holds a ring's profile


def hand_read(table: np.ndarray, R: np.ndarray, phase, r: float, phi: np.ndarray) -> np.ndarray:
    """**A superseded reader**, kept to say what was replaced: the grid table ``sfr_modulation`` at radius ``r``
    and azimuths ``phi`` - the two grid rings the radius lies between, each ring's row read at
    φ − (Φ(r) − Φ(R_ring)), linearly and periodically between the cells' centres, and the two blended linearly
    in R. ``phase`` is Φ, a function of one radius: the winding's gives the wound table read (the first follow-up
    to the gate), and a Φ that is 0 everywhere the read at fixed φ (S27's)."""
    i = max(0, min(int(np.searchsorted(R, r, side="right")) - 1, R.size - 2))
    share = min(max((r - R[i]) / (R[i + 1] - R[i]), 0.0), 1.0)
    centres = (np.arange(table.shape[1]) + 0.5) * (2.0 * math.pi / table.shape[1])

    def row(k: int) -> np.ndarray:
        return np.interp(np.mod(phi - (phase(r) - phase(float(R[k]))), 2.0 * math.pi), centres, table[k], period=2.0 * math.pi)

    return (1.0 - share) * row(i) + share * row(i + 1)


def misplaced(reader: np.ndarray, law: np.ndarray) -> np.ndarray:
    """The reviewer's statistic, per radius: half the integrated absolute difference between two azimuthal
    profiles, each normalised to a mean of 1 - the share of the ring's young stars the one puts at azimuths
    where the other does not."""
    a, b = reader / reader.mean(axis=1, keepdims=True), law / law.mean(axis=1, keepdims=True)
    return 0.5 * np.abs(a - b).mean(axis=1)


class HandLaw:
    """The star formation law at a point, by this file's arithmetic, from published numbers and the gas
    pattern's solved rings: for a point at radius r between the grid rings i and j,

        M(r, φ) = (1 − a) m_i + a m_j,   m_k = Ψ_k(g_k(r, φ)) / ⟨Ψ_k(g_k(r, ·))⟩,
        g_k(r, φ) = (1 − τ_k) s_k(φ − Φ(r)) + τ_k L_k(φ − φ_bar),   τ_k = exp(−(R_k/a_bar)⁴),
        Ψ_k(g) = (Σ_k g)ⁿ · ½ (1 + tanh((Σ_k g − Σ_crit,k) / (w Σ_crit,k))).

    Φ is the winding laid by hand from the published rows (``hand_knots``); φ_bar = ln a_bar · cot p; s_k is the
    gas response's solved profile on ring k (the solver's output, which the pattern holds on its cells' centres
    in χ - not a published field) and L_k the footprint-uniform profile on the same cells in the bar's frame
    (``gas_pattern.footprint_profiles``, the template's own function), each read linearly and periodically
    between the cells' centres; Σ_k and Σ_crit,k are ring k's published gas column and threshold, n the law's
    index and w the switch's width; ⟨·⟩ is the mean over 46 080 azimuths round the ring, the arms where the
    winding puts them at r. An unbarred galaxy has no τ and no L."""

    def __init__(self, F, R, gp, c):
        self.R, self.gp = R, gp
        self.knots, self.phases, _ = hand_knots(F)
        self.gas, self.threshold = np.asarray(F["gas_surface_density"]), np.asarray(F["sf_threshold_surface_density"])
        self.index = float(c["KS_INDEX"])
        self.a, pitch = float(F["bar_half_length"]), float(F["pitch_angle"])
        self.barred = math.isfinite(self.a)
        if self.barred:
            self.bar_angle = math.log(self.a) / math.tan(math.radians(pitch))
            self.footprint = gm.footprint_profiles(R, self.a, float(F["bar_axis_ratio"]), float(F["bar_boxiness"]), float(c["BAR_GAS_RATIO"]))

    def ring(self, k: int, r: float, phi: np.ndarray) -> np.ndarray:
        """Ψ_k(g_k(r, φ)): ring k's law at the point's coordinates, not yet over its mean."""
        chi = phi - hand_phase(self.knots, self.phases, r)
        g = np.interp(chi, CELL_CENTRES, self.gp.profiles[k], period=2.0 * math.pi)
        if self.barred:
            taper = math.exp(-((self.R[k] / self.a) ** 4))
            g = (1.0 - taper) * g + taper * np.interp(phi - self.bar_angle, CELL_CENTRES, self.footprint[k], period=2.0 * math.pi)
        column = self.gas[k] * np.maximum(g, 0.0)
        return column**self.index * 0.5 * (1.0 + np.tanh((column - self.threshold[k]) / (sfh.THRESHOLD_WIDTH * self.threshold[k])))

    def at(self, r: float, phi: np.ndarray) -> np.ndarray:
        R = self.R
        i = max(0, min(int(np.searchsorted(R, r, side="right")) - 1, R.size - 2))
        share = min(max((r - R[i]) / (R[i + 1] - R[i]), 0.0), 1.0)
        out = np.zeros(phi.shape)
        for k, weight in ((i, 1.0 - share), (i + 1, share)):
            mean = float(self.ring(k, r, ROUND).mean())
            out += weight * (self.ring(k, r, phi) / mean if mean > 0.0 else 1.0)
        return out


def reader_run(prod, **more):
    """A Milky Way template's run with what the reader reads, the two pattern objects, and the model's reader."""
    model = the_model(prod)
    c = constants(model)
    o = run(model, inputs_of("milky_way", **more), only=READER)
    F, R = o.fields, o.grid.R
    return o, compose.stellar_pattern(F, R), compose.gas_pattern(F, R, c), systems.young_reader(F, R, c), c


def test_the_young_stars_reader_is_the_star_formation_law_at_a_point(prod):
    """The gate's ruling on the review's blocker (D218): "(b), the exact point reader ... a stored grid is not a
    field's definition; a reader that interpolates a table between rings is reading the grid, and no
    interpolation of one row can serve two frames at once — the arms turn with the winding, the footprint stays
    in the bar's ... the young stars' placement weight at a point is that law applied to that point function,
    and the grid table of ``sfr_modulation`` becomes ... the same function at the cells (published, read by the
    viewer, read by no census)."

    **The reader** (``systems.Modulation``, built by ``systems.young_reader`` for the star sample and the bright
    catalogue alike) applies the law ring by ring, where its inputs exist - a ring's gas column and threshold
    are on the rings only, and nothing of them is interpolated - to each ring's own contrast as the point sees
    it (the ring's arm profile at the point's χ, its footprint in the bar's frame), each over its own mean round
    the ring there, and blends the two rings linearly in R as the pattern does. ``HandLaw`` above is the same
    law by this file's arithmetic.

    **The gate's three statements, as read.**

    1. *"At every grid cell the point reader equals the published ``sfr_modulation`` to rounding."* **Not to
       rounding, and it cannot be while the table is what it is.** The table is the law at each cell's *mean*
       contrast (``star_formation_gas_contrast`` is a cell mean of the gas's point function, so that a ring keeps
       its gas on any grid), over the mean of the cells; the reader at a cell's centre is the law at the
       *centre's* contrast, over the ring's mean of the law; and the law is not linear. What does hold to
       rounding: the reader's law is the stage's own arithmetic (the reader's law on the published cell-mean
       contrast, over its mean, is the table bit for bit), and the reader at a grid ring is the law of the
       pattern's own point function there. What is left is the cell mean: on the Milky Way template the largest
       difference at a cell's centre is 1.20 (a cell the footprint's edge crosses, at 2.5 kpc, where the table
       reads the law at the cell's mean of two levels), and as a ring's misplaced weight 0.59 % at worst, 0.03 %
       on average; on the rings whose contrast only turns with the winding (past the bar's body, or filled by it)
       0.015 % at worst (0.005 in the modulation). To meet "to rounding" the table would have to be made
       from the reader's function - ``sfh_azimuthal`` evaluating the law on the gas pattern's point function
       (and reading the pattern object and its constants) in place of the published cell-mean field. Not done:
       reported.
    2. *"Past the bar's reach it agrees with the wound table read to the 0.29 % already measured."* **Held**:
       the wound table read misplaces 0.10 % against the reader at worst on the default seeds, 0.18 % at pattern
       seed 3, 0.02 % at pattern seed 22 (the fixed-φ read: 3.6 %, 14.3 %, 45.1 %).
    3. *"Inside, the misplaced weight against the law is recorded as 0 by construction and the two superseded
       readers' numbers ... are kept in the record as what was replaced."* The reader against ``HandLaw`` on
       every ring gap inside the bar's half-length: under 0.01 % (the two quadratures' difference). **The
       superseded readers there**, worst gap, fixed-φ table / wound table: default seeds **7.7 % / 13.4 %**,
       pattern seed 3 (pitch 9.1°) **24.4 % / 17.2 %**, pattern seed 22 (pitch 1.0°) **37.2 % / 70.6 %**. (As
       first measured, against the law of the blended contrast with the column and threshold interpolated
       between rings - the reference this ruling replaced: 8.3 / 15.0 %, 24.8 / 17.5 %, 38 / 71 %.)

    **One measure.** The reader's mean round a ring is 1 at every radius, to its normaliser's quadrature (two
    equal steps to each of the pattern's cells: under 5e-4 against this file's rule sixteen times finer on gaps
    inside the bar, under 5e-5 past it). A sector's mean is the point function's integral over the sector - a
    Gauss rule on every piece between the contrast's kinks, two points where the contrast is the arm profile's
    alone and six where a bar's footprint is in it - and against a midpoint rule of a million samples round
    the ring it is right to 3e-6 of the sector's mean at worst, for the star sample's 32 sectors and the bright
    catalogue's 256 alike, inside the bar and out (a midpoint rule of two samples a cell, tried first, left
    2 % of a finest sector's mean at the footprint's edge); the sectors that tile a ring average to 1 to the
    normaliser's 7e-5. Azimuths drawn by the inverse CDF follow the point function. **The expected
    young count of every ring is the arrival law's, unchanged**: the census spreads a ring's young share over
    its sectors by the sector means over their mean, so the ring's total is the share times 1.

    **With the layer off** no reader is built and no number moves. A model that publishes a modulation cannot
    be placed without the model's constants, and says so; a flat gas pattern is the law of a uniform ring."""
    model = the_model(prod)
    superseded = {}
    for label, more, pins in (("default seeds", {}, ((0.10, 3.59), (7.73, 13.40))), ("pattern seed 3", {"pattern_seed": 3}, ((0.18, 14.29), (24.42, 17.24))),
                              ("pattern seed 22", {"pattern_seed": 22}, ((0.02, 45.12), (37.21, 70.64)))):
        o, sp, gp, reader, c = reader_run(prod, **more)
        F, R, phi, edges = o.fields, o.grid.R, o.grid.phi, o.grid["phi"].edges
        table = np.asarray(F["sfr_modulation"])
        a = float(F["bar_half_length"])
        law = HandLaw(F, R, gp, c)
        # The reader reads the model's own law: its arithmetic on the published cell-mean contrast is the table's.
        rings = np.arange(R.size)
        cells = reader._law(rings, np.asarray(F["star_formation_gas_contrast"]))
        assert np.array_equal(cells / cells.mean(axis=1, keepdims=True), table), label
        # ... and at a grid ring it is the law of the pattern's own point function there, over its mean round the ring.
        at_centres = reader.at(R, phi)
        point = reader._law(rings, gp.star_formation_contrast_at(R[:, None], phi[None, :]))
        assert np.array_equal(gp.ring_star_formation_contrast_at(rings, R, np.broadcast_to(phi[None, :], (R.size, phi.size))), gp.star_formation_contrast_at(R[:, None], phi[None, :])), label
        ratio = point / at_centres  # the ring's mean, one number round the ring
        assert float(np.abs(ratio / ratio[:, :1] - 1.0).max()) < 1e-12, label
        # 1. At the grid cells against the published table: the cell mean's difference, as read.
        body = gp.ring_turns_with_the_winding(rings)  # the rings past the bar's body, or filled by it: a contrast that only turns
        apart = np.abs(at_centres - table)
        weight = 100.0 * misplaced(at_centres, table)
        k, j = np.unravel_index(int(np.argmax(apart)), apart.shape)
        got = (float(apart.max()), float(R[k]), float(weight.max()), float(weight.mean()), float(weight[body].max()), float(apart[body].max()))
        if label == "default seeds":
            assert got == pytest.approx((1.201, 2.5125, 0.586, 0.029, 0.015, 0.0045), abs=2e-3), got
            assert not body[k] and int(body.sum()) == 359  # 41 rings hold a footprint that does not fill them
        assert weight.max() < 1.2 and weight[body].max() < 0.05, (label, got)
        # 2 and 3. Between the rings: the reader against the law by hand, and the two superseded readers against it.
        knots, phases = law.knots, law.phases
        mids = 0.5 * (R[:-1] + R[1:])
        now = reader.at(mids, FINE)
        live = now.max(axis=1) > 1.0 + 1e-9  # the gaps that form stars unevenly
        inside, past = np.flatnonzero(live & (mids < a)), np.flatnonzero(live & (mids > a))
        by_hand = np.array([law.at(float(mids[i]), FINE) for i in inside])
        assert 100.0 * float(misplaced(now[inside], by_hand).max()) < 0.01, label
        some = past[:: max(1, past.size // 12)]
        assert 100.0 * float(misplaced(now[some], np.array([law.at(float(mids[i]), FINE) for i in some])).max()) < 0.01, label
        wound = np.array([hand_read(table, R, lambda x: hand_phase(knots, phases, x), float(r), FINE) for r in mids])
        fixed = np.array([hand_read(table, R, lambda x: 0.0, float(r), FINE) for r in mids])
        old_wound, old_fixed = 100.0 * misplaced(wound, now), 100.0 * misplaced(fixed, now)
        superseded[label] = ((float(old_wound[past].max()), float(old_fixed[past].max())), (float(old_fixed[inside].max()), float(old_wound[inside].max())))
        assert superseded[label][0] == pytest.approx(pins[0], abs=0.02) and superseded[label][1] == pytest.approx(pins[1], abs=0.02), (label, superseded[label])
        assert superseded[label][0][0] < 0.29, label  # the gate's second statement
        # The reader's mean round a ring is 1 at every radius: against this file's finer rule.
        means = np.array([float(reader.at(np.array([r]), ROUND).mean()) for r in mids[inside[::6]]])
        outer = np.array([float(reader.at(np.array([r]), ROUND).mean()) for r in mids[past[::20]]])
        assert float(np.abs(means - 1.0).max()) < 5e-4 and float(np.abs(outer - 1.0).max()) < 5e-5, (label, float(np.abs(means - 1.0).max()), float(np.abs(outer - 1.0).max()))
    # One measure, on the default seeds' reader (the loop's last is pattern seed 22: take the default again).
    o, sp, gp, reader, c = reader_run(prod)
    F, R = o.fields, o.grid.R
    a = float(F["bar_half_length"])
    rings32, sectors32 = systems.cell_edges(R)
    finest = np.linspace(0.0, 2.0 * math.pi, 257)
    assert systems.RING_SAMPLES_PER_CELL == 2 and sectors32.size == 33
    assert {bar: nodes.size for bar, (nodes, _) in systems.GAUSS.items()} == {False: 2, True: 6}
    worst = {}
    for name, edges, count in (("level-0", sectors32, 32768), ("finest", finest, 4096)):
        for where, radii in (("bar", (1.5, 2.7, 3.6, 4.4)), ("disc", (6.0, 8.0, 12.0))):
            read = []
            for r in radii:
                means = reader.sector_means(r, edges)
                # ... against a midpoint rule of 2^20 samples round the ring (2e-5 of a pattern cell apart).
                samples = edges[:-1, None] + (edges[1:] - edges[:-1])[:, None] * ((np.arange(count) + 0.5) / count)[None, :]
                finer = np.concatenate([reader.at(np.array([r]), part.ravel()).reshape(part.shape).mean(axis=1) for part in np.array_split(samples, 16)])
                read.append((float(np.abs(means - finer).max()), float(np.abs(means / finer - 1.0).max()), abs(float(means.mean()) - 1.0)))
                assert np.array_equal(means, reader.sector_means_at(np.array([1.0, r, 9.9]), edges)[1])  # a row is the same in any company
            worst[(name, where)] = tuple(max(x[k] for x in read) for k in range(3))
    # (the largest error of a sector's mean, the largest relative one, the tiling's mean less 1): as read, and bounded.
    read = {k: tuple(float(f"{x:.1e}") for x in v) for k, v in worst.items()}
    assert read == {("level-0", "bar"): (7.7e-08, 7.7e-07, 6.7e-05), ("level-0", "disc"): (3.2e-08, 5.9e-07, 4.2e-06),
                    ("finest", "bar"): (3.1e-07, 1.5e-06, 6.7e-05), ("finest", "disc"): (4.4e-07, 2.7e-06, 4.2e-06)}, read
    assert all(v[0] < 1e-5 and v[1] < 1e-5 and v[2] < 5e-4 for v in worst.values()), worst
    # The azimuth draws follow the point function: the inverse CDF on a sector's 25 samples.
    for r in (2.7, 8.0):
        lo, hi = float(sectors32[10]), float(sectors32[11])
        u = np.random.default_rng(59).random(100000)
        drawn = reader.azimuths(u, np.full(u.size, r), lo, hi)
        assert drawn.min() >= lo and drawn.max() <= hi
        grid = np.linspace(lo, hi, 25)
        density = reader.at(np.array([r]), grid)[0]
        cdf = np.concatenate([[0.0], np.cumsum(0.5 * (density[1:] + density[:-1]))])
        assert float(np.abs(np.array([(drawn <= g).mean() for g in grid]) - cdf / cdf[-1]).max()) < 0.006, r
    some = np.array([2.7, 5.25, 8.0])
    assert np.array_equal(reader.at(some, grid), reader.at_points(some, np.broadcast_to(grid[None, :], (some.size, grid.size))))
    with pytest.raises(ValueError, match="its own row of azimuths"):
        reader.at_points(some, grid)
    # The expected young count of every ring is the arrival law's: the census's young share of a sector, weighted by
    # the sector's stars, sums to the ring's share. (A synthetic arrival law: every step alike.)
    t = o.grid.t
    arrive = np.ones((t.size, systems.CELL_RINGS))
    young = systems.YoungStars(reader, sp, arrive, t, rings32, sectors32)
    stars = np.array([sp.sector_means(float(r), sectors32) for r in 0.5 * (rings32[:-1] + rings32[1:])])
    assert young.p.shape == (32, 32) and young.p.max() < 1.0 and float(np.abs((young.p * stars).mean(axis=1) / young.share - 1.0).max()) < 1e-12
    # ... and the bright catalogue's expected total is the same with the layer on and off: I1, within four units.
    on = run(model, inputs_of("milky_way"), only=("bright_star_count_1e3",))
    off = run(model, inputs_of("milky_way"), only=("bright_star_count_1e3",), layer=False)
    total_on, total_off = float(on.fields["bright_star_count_1e3"]), float(off.fields["bright_star_count_1e3"])
    units = abs(total_on - total_off) / float(np.spacing(max(total_on, total_off)))
    assert units <= 4.0 and units == 0.0, (total_on, total_off, units)
    # With the layer off no reader is built; with it on the model's constants are required; a flat pattern reads 1.
    dark = run(model, inputs_of("milky_way"), only=READER, layer=False)
    assert systems.young_reader(dark.fields, R, c) is None and systems.young_reader(dark.fields, R, None) is None
    with pytest.raises(TypeError, match="pass constants="):
        systems.young_reader(F, R, None)
    with pytest.raises(TypeError, match="pass constants="):
        systems.materialise(run(model, inputs_of("milky_way"), SMALL, only=systems.SYSTEMS.requires + systems.SYSTEMS.requires_optional).fields,
                            SMALL.build().R, SMALL.build().t, 0, 500, migration=3.6)
    # The reviewer's second pass (D218): a gas pattern that cannot be built - one of its constants or fields missing -
    # raised nothing and read 1 everywhere. It raises, naming what is missing; the law's index missing raises too.
    for lost in ("G", "GAS_DISPERSION"):
        with pytest.raises(KeyError, match=f"cannot be built here: missing {lost}"):
            systems.young_reader(F, R, {k: v for k, v in c.items() if k != lost})
    with pytest.raises(KeyError, match="KS_INDEX"):
        systems.young_reader(F, R, {k: v for k, v in c.items() if k != "KS_INDEX"})
    flat = systems.Modulation(None, R, F["gas_surface_density"], F["sf_threshold_surface_density"], float(c["KS_INDEX"]))
    assert np.all(flat.at(some, grid) == 1.0) and np.all(flat.sector_means(8.0, sectors32) == 1.0)
    # The stages that build the reader declare what it reads; the table is asked for by name only.
    for stage in ("systems", "bright_stars"):
        st = prod[1].get(stage)
        assert {*gm.GAS_PATTERN_READS, "gas_surface_density", "sf_threshold_surface_density"} <= set(st.requires), stage
        assert {*gm.GAS_PATTERN_CONSTANTS, "KS_INDEX"} <= set(st.reads_constants) and st.requires_optional == ("sfr_modulation",), stage


# --- the two disclosed checks ---------------------------------------------------------------------------------------


def test_disclosed_check_the_milky_way_s_measured_arms_against_the_composed_field(prod):
    """D218 item 5 (not a spec row: I3): the radial distance from each of Reid et al. 2019's arm loci to the nearest
    crest of the composed stellar field, in measured arm widths; the median over the five arms.
    ``tests/reid2019.py`` holds the table and says exactly how the five arms are taken.

    **The statistic is kept and nothing is judged by "1 width"** (the follow-up to the gate, item 3: "judged only
    as a percentile of its null ... The miss/hit verdict is dropped"). **At 1 width the check passes by chance in
    a large share of cases: it has no power to tell this representation from the Milky Way's arms; that the
    representation cannot show the measured arms stands on the probe (four arms are not one winding), not on this
    statistic.** Stated and pinned:

    (i) **As built** (the template's default seeds, the relative residual): **1.535 widths**. Per arm:
        Norma–Outer 0.42, Scutum–Centaurus 0.87, Sagittarius–Carina 2.27, Perseus 1.61, Local 1.54 (all points
        pooled: 1.23). The first build's 1.92, on the absolute residual, was read on the 999th winding of 1000.
    (ii) **The Sun-rotation null**: the same field, the Sun placed at each of 360 azimuths a degree apart.
        Median 1.011 widths, 5-95 %: 0.578-1.900; **49.4 % of the rotations read at or under 1 width**. The
        as-built value is the null's 81st percentile.
    (iii) **The texture-seed null**: 60 texture seeds, the Sun where the model puts it. Median 1.591 widths,
        range 0.474-2.721; **8 of 60 (13.3 %) at or under 1 width**. The as-built value is its 38th percentile.
    (iv) **The unsegmented winding**, the same field's modes on ln R · cot p: 0.647 widths - the 2nd percentile of
        its own rotation null (median 1.354, 5-95 %: 0.726-2.128; 18.9 % at or under 1 width). A low reading by
        the chance of one azimuth, as the as-built is an ordinary one.

    Nothing is tuned to the check - not the Sun's azimuth, not the anchor, not the residual."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    sp = compose.stellar_pattern(F, R)
    sense = pt.rotation_sense(float(F["pitch_angle"]))
    sun = float(F["sun_azimuth"])
    per_arm, median, pooled = reid2019.check(sp, sun, sense)
    assert list(per_arm) == ["Norma-Outer", "Sct-Cen", "Sgr-Car", "Perseus", "Local"]
    assert [per_arm[k] for k in per_arm] == pytest.approx([0.423, 0.869, 2.265, 1.614, 1.535], abs=2e-3)
    assert (median, pooled) == pytest.approx((1.535, 1.231), abs=2e-3)
    # (ii) the Sun-rotation null: entry 0 is the Sun where the model puts it.
    null = reid2019.rotation_null(sp, sun, sense)
    assert null.shape == (360,) and float(null[0]) == pytest.approx(median, abs=1e-9)
    assert (float(np.median(null)), float(np.percentile(null, 5)), float(np.percentile(null, 95))) == pytest.approx((1.011, 0.578, 1.900), abs=2e-3)
    assert int((null <= 1.0).sum()) == 178 and 100.0 * float((null < median).mean()) == pytest.approx(81.1, abs=0.05)
    # (iii) the texture-seed null: other realisations of the arms, the Sun where the model puts it in each.
    model = the_model(prod)
    seeds = []
    for texture_seed in range(60):
        other = run(model, inputs_of("milky_way", texture_seed=texture_seed), only=(*pt.PATTERN_READS, "sun_azimuth"))
        seeds.append(reid2019.check(compose.stellar_pattern(other.fields, R), float(other.fields["sun_azimuth"]), sense)[1])
    seeds = np.array(seeds)
    assert float(seeds[0]) == median and float(other.fields["sun_azimuth"]) == sun  # the Sun does not move with the texture seed
    assert (float(np.median(seeds)), float(seeds.min()), float(seeds.max())) == pytest.approx((1.591, 0.474, 2.721), abs=2e-3)
    assert int((seeds <= 1.0).sum()) == 8 and int((seeds < median).sum()) == 23
    # (iv) the unsegmented winding, with its own null.
    plain = pt.ArmPattern(sp.R, sp.amplitudes, sp.phases, sp.bar, sp.pitch_deg, sp.bar_length, sp.axis_ratio, sp.boxiness, sp.index, sp.share, sp.surface_density)
    unsegmented = reid2019.check(plain, sun, sense)[1]
    plain_null = reid2019.rotation_null(plain, sun, sense)
    assert plain.winding is None and unsegmented == pytest.approx(0.646, abs=2e-3) and float(plain_null[0]) == pytest.approx(unsegmented, abs=1e-9)
    assert (float(np.median(plain_null)), float(np.percentile(plain_null, 5)), float(np.percentile(plain_null, 95))) == pytest.approx((1.354, 0.726, 2.128), abs=2e-3)
    assert int((plain_null <= 1.0).sum()) == 68 and int((plain_null < unsegmented).sum()) == 8
    # No verdict: the statistic at or under one width is what half the rotations read.
    assert 0.4 < float((null <= 1.0).mean()) < 0.6
    # The table as entered: seven rows, R0 8.15 kpc, the width law; a locus passes through its kink.
    assert len(reid2019.TABLE2) == 7 and reid2019.R0 == 8.15 and float(reid2019.width_kpc(8.15)) == 0.336
    beta, radius = reid2019.locus(reid2019.TABLE2[5])  # Perseus
    assert (beta[0], beta[-1], beta.size) == (-23.0, 115.0, 139) and float(radius[beta == 40.0][0]) == 8.87
    assert float(radius[0]) == pytest.approx(8.87 * math.exp(math.radians(63.0) * math.tan(math.radians(10.3))), rel=1e-12)


def test_disclosed_check_ngc_4414_s_measured_segments_and_its_pinned_pitch(prod):
    """D218 item 6. "``pitch_angle`` = 28.9° replaces the draw (a measured mean, as ``bar_present`` is); the law's
    own value 14.3° is published beside it and its miss recorded (2.4σ of the 6° draw: a finding against the pitch
    law)." The five measured segments' mean is 28.88° and their standard deviation 13.35°, this file's arithmetic
    on the five rows; **the drawn spread is 0.56 of the pinned pitch, 16.2°** (the follow-up's "16° at 28.9°";
    as realised on the segments that cross the template's grid over 100 texture seeds, below), so the
    galaxy's own segments scatter 0.82 times as widely as the draw - read, not tuned. (On the absolute form the
    draw was 10° and the measured segments scattered 1.3 times as widely.) Every other draw of the pattern stage
    keeps its stream and its value under the pin."""
    measured = np.array([abs(row[0]) for row in NGC_4414_SEGMENTS])
    assert float(measured.mean()) == pytest.approx(28.88, abs=5e-3) and float(measured.std(ddof=1)) == pytest.approx(13.35, abs=5e-3)
    assert float(measured.std(ddof=1) / math.sqrt(5)) == pytest.approx(5.97, abs=5e-3)
    pinned = template_run(prod, "ngc_4414")
    model = the_model(prod)
    drawn = run(model, drawn_pitch("ngc_4414"), only=PATTERN)
    assert pinned.inputs["pitch_angle"] == 28.9 and "pitch_angle" not in drawn.inputs
    assert float(pinned.fields["pitch_angle"]) == 28.9 and float(pinned.fields["pitch_angle_drawn"]) == float(drawn.fields["pitch_angle"]) == float(drawn.fields["pitch_angle_drawn"])
    law = float(pinned.fields["pitch_angle_drawn"])
    scatter = float(constants(model)["PITCH_SCATTER"])
    assert law == pytest.approx(14.330, abs=1e-3) and (28.9 - law) / scatter == pytest.approx(2.43, abs=0.01)
    # The rows hold no pitch: the pin moves none of them, and nothing else the pattern stage draws.
    for name in ("arm_contrast", *pt.AMPLITUDE_FIELDS, *pt.PHASE_FIELDS, *pt.WINDING_FIELDS, "arm_saturation"):
        assert np.asarray(pinned.fields[name]).tobytes() == np.asarray(drawn.fields[name]).tobytes(), name
    assert math.isnan(float(pinned.fields["sun_azimuth"])) and math.isnan(float(pinned.fields["bar_half_length"]))
    anchor = float(pinned.fields["arm_winding_anchor_radius"])
    assert anchor == pytest.approx(3.5101, abs=1e-4)  # where its bar would end
    spread = RELATIVE_HAND * 28.9
    R = pinned.grid.R
    residuals = []
    for seed in range(100):
        residuals.extend((pt.Winding(28.9, RELATIVE_HAND, anchor, *drawn_rows(prod, seed)).segments(float(R[0]), float(R[-1]))[2] - 28.9).tolist())
    assert spread == pytest.approx(16.18, abs=5e-3) and float(np.std(residuals)) == pytest.approx(16.2, abs=0.5), float(np.std(residuals))
    assert float(measured.std(ddof=1)) / spread == pytest.approx(0.825, abs=1e-3)


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


def test_a_numeric_pin_is_held_to_the_range_of_the_draw_it_replaces(prod):
    """The follow-up to the gate, item 7: "a numeric pin is held to the range of the draw it replaces (pitch
    1–60°, the Sun's angle 0–360°), refused otherwise, at ``run()`` as at the API." The reviewer: "a numeric pin
    had no range" - a pitch pin of −5° ran, and the law's cotangent (which holds the pitch inside 1-89°) and the
    segments (which did not) read two pitches.

    **The range is the registry's**: a pin that is a measured number declares lo and hi - the pitch's the bounds
    the draw is clipped to, both ends allowed; the Sun's angle one turn, 0 allowed and 360 not - and a class pin
    declares none. ``run()`` refuses a value outside it; so does a template's validation; the API refuses any
    pin as a request parameter, whatever its value. **And the winding itself refuses a pitch the law would read
    as another**: built from a pitch outside 1-89°, it raises - so the law and the segments read one pitch."""
    model = the_model(prod)
    pitch, sun, bar = INPUTS["pitch_angle"], INPUTS["sun_bar_angle"], INPUTS["bar_present"]
    assert (pitch.lo, pitch.hi, pitch.hi_open, pitch.range_text) == (1.0, 60.0, False, "1 to 60")
    assert (sun.lo, sun.hi, sun.hi_open, sun.range_text) == (0.0, 360.0, True, "0 up to, not including, 360")
    assert (bar.lo, bar.hi, bar.has_range) == (None, None, False) and bar.admits(True)
    assert "1 to 60 degrees" in pitch.about and "0 up to, not including, 360 degrees" in sun.about
    # The pitch's range is the draw's own: the bounds compute_pattern clips the drawn pitch to.
    drawn = [float(run(model, {"pattern_seed": s}, SMALL, only=("pitch_angle",)).fields["pitch_angle"]) for s in range(60)]
    assert min(drawn) >= pitch.lo and max(drawn) <= pitch.hi
    only = ("pitch_angle", "sun_azimuth")
    for good in (1.0, 13.5, 60.0):
        assert float(run(model, {"pitch_angle": good}, SMALL, only=only).fields["pitch_angle"]) == good
    for bad in (-5.0, 0.0, 0.999, 60.001, 89.0, 90.0, 1e9):
        with pytest.raises(RunError, match=r"pin 'pitch_angle' is held to the range of what it replaces, 1 to 60 deg; got"):
            run(model, {"pitch_angle": bad}, SMALL, only=only)
    for good in (0.0, 30.0, 359.999):
        assert math.isfinite(float(run(model, {"sun_bar_angle": good}, SMALL, only=only).fields["sun_azimuth"]))
    for bad in (-0.001, -30.0, 360.0, 390.0):
        with pytest.raises(RunError, match=r"pin 'sun_bar_angle' is held to the range of what it replaces, 0 up to, not including, 360 deg; got"):
            run(model, {"sun_bar_angle": bad}, SMALL, only=only)
    # A template is held to it when it is validated.
    ngc = templates.TEMPLATES["ngc_4414"]
    ngc.validate()
    for name, value in (("pitch_angle", 61.0), ("pitch_angle", 0.5)):
        pins = tuple(templates.Pin(p.name, value, p.source) if p.name == name else p for p in ngc.pins)
        with pytest.raises(templates.TemplateError, match="held to the range of what it replaces, 1 to 60 deg"):
            dataclasses.replace(ngc, pins=pins).validate()
    mw = templates.TEMPLATES["milky_way"]
    pins = tuple(templates.Pin(p.name, 360.0, p.source) if p.name == "sun_bar_angle" else p for p in mw.pins)
    with pytest.raises(templates.TemplateError, match="0 up to, not including, 360 deg"):
        dataclasses.replace(mw, pins=pins).validate()
    # The API refuses a pin as a request parameter, in range or out of it.
    api = Service(grid=SMALL)
    for query in ("fields=pitch_angle&pitch_angle=-5", "fields=pitch_angle&pitch_angle=20", "fields=sun_azimuth&sun_bar_angle=400"):
        got = api.handle("/api/arrays", query)
        assert got.status == 400 and "is a template's pin, not an input a request may set" in got.json()["error"], query
    # The registry: a measured number declares its range; a class declares none; only a numeric pin's is half-open.
    with pytest.raises(RegistryError, match="held to the range of what it replaces - lo and hi are required"):
        Input("some_pin", "A pin", "pin", "about", unit="deg", default=None)
    with pytest.raises(RegistryError, match="a pin has no default and no range"):
        Input("some_pin", "A pin", "pin", "about", default=None, lo=0.0, hi=1.0)
    with pytest.raises(RegistryError, match="only a numeric pin's range may leave its upper end out"):
        Input("some_pin", "A pin", "pin", "about", default=None, hi_open=True)
    number = Input("some_pin", "A pin", "pin", "about", unit="deg", default=None, lo=2.0, hi=5.0)
    assert number.admits(2.0) and number.admits(5.0) and not number.admits(5.1) and not number.admits(1.9)
    # The law and the winding cannot read two pitches: a winding is not built at a pitch the law's cotangent would move.
    rows = drawn_rows(prod, 0)
    assert pt.PITCH_RANGE == (1.0, 89.0) and pt.law_cot(0.5) == pt.law_cot(1.0) and pt.law_cot(95.0) == pt.law_cot(89.0)
    for bad in (-5.0, 0.5, 89.5, 120.0, float("nan")):
        with pytest.raises(ValueError, match="the law and the segments would read two pitches"):
            pt.Winding(bad, RELATIVE_HAND, 5.0, *rows)
    for good in (1.0, 60.0, 89.0):
        w = pt.Winding(good, RELATIVE_HAND, 5.0, *rows)
        assert w.anchor_phase == math.log(5.0) * pt.law_cot(good) and w.pitch_deg == good


def test_the_winding_s_door_says_what_it_cannot_build_and_its_refusal_cannot_overflow(prod):
    """Two things the reviewer listed. **``Winding.from_fields`` no longer returns None in silence**: None means
    one of two states the fields themselves say - the layer laid no row (the plain winding), or the disc's pitch
    is not a number (an unresolved pattern, flat: there is nothing to wind) - and anything else raises: a missing
    field, an anchor or a spread that is not a number. **The message of a winding asked past its rows cannot
    itself fail**: a nearly radial segment carries the last knot past what a float holds as a radius, and the
    first build's message took its exponential (an OverflowError in place of the refusal)."""
    o = template_run(prod, "milky_way")
    fields = {name: o.fields[name] for name in (*pt.WINDING_FIELDS, "pitch_angle")}
    w = pt.Winding.from_fields(fields)
    assert isinstance(w, pt.Winding) and (w.pitch_deg, w.scatter, w.anchor) == (float(fields["pitch_angle"]), RELATIVE_HAND, float(fields["arm_winding_anchor_radius"]))
    assert pt.Winding.from_fields({**fields, "arm_segment_extent": np.zeros(0), "arm_segment_pitch_deviate": np.zeros(0)}) is None  # the layer off
    assert pt.Winding.from_fields({**fields, "pitch_angle": float("nan")}) is None  # an unresolved pattern
    for name in fields:
        with pytest.raises(ValueError, match=f"missing: {name}"):
            pt.Winding.from_fields({k: v for k, v in fields.items() if k != name})
    for name in ("arm_winding_anchor_radius", "arm_segment_pitch_scatter"):
        for bad in (float("nan"), float("inf"), -1.0):
            with pytest.raises(ValueError, match="a finite relative spread of the segments' pitch and a positive anchor radius"):
                pt.Winding.from_fields({**fields, name: bad})
    with pytest.raises(ValueError, match="a winding holds 1024 segment rows"):
        pt.Winding.from_fields({**fields, "arm_segment_extent": np.asarray(fields["arm_segment_extent"])[:256]})
    # Asked past its rows it raises, with the reach in kiloparsecs.
    extent, deviate = drawn_rows(prod, 0)
    with pytest.raises(ArithmeticError, match=r"768 inward and 256 outward segments reach \S+ kpc and were asked at 1e\+40-1e\+40 kpc"):
        w.phase(np.array([1.0e40]))
    # A segment that is radial to rounding (its pitch 90 degrees: z = 5/0.56 at a pitch of 15) has a tangent past
    # 1e15, so the last knot lies at ln R past 1e15, which no float holds as a radius. With inward rows too short
    # to reach 1 kpc, a radius asked there is refused - and the refusal speaks (the first build's raised an
    # OverflowError from its own message here).
    radial, short = deviate.copy(), extent.copy()
    radial[0] = (90.0 / 15.0 - 1.0) / RELATIVE_HAND
    short[OUT_ROWS:] = 1e-9
    steep = pt.Winding(15.0, RELATIVE_HAND, 5.0, short, radial)
    assert steep.knots[-1] > 1e15 and np.all(np.isfinite(steep.knots)) and math.exp(steep.knots[0]) > 4.99
    with pytest.raises(OverflowError):
        math.exp(steep.knots[-1])
    with pytest.raises(ArithmeticError, match=r"segments reach 5-e\^\d\.\d+e\+\d+ kpc and were asked at 1-1 kpc"):
        steep.phase(np.array([1.0]))
    inner, outer, _, _ = steep.segments(1.0, 30.0)
    assert np.isinf(outer[-1]) and np.all(np.isfinite(inner))  # a knot past any radius is infinitely far, and says so
    assert math.isfinite(float(steep.phase(np.array([20.0]))[0]))  # ... and Φ inside the radial segment is a number


# --- the table: published whole, read whole, and no catalogue -------------------------------------------------------


def _viewer_rules(fields):
    """``interface/view.js``'s three declaration-only rules, as the viewer reads them off ``/api/fields``: the
    stages that publish objects (``catalogueStages``), the scalars it asks for at a checkpoint (``scalarsAt``:
    every galaxy scalar there but a catalogue stage's) and whether there is a sample to draw (``hasCatalogue``)."""
    catalogue_stages = {f["stage"] for f in fields if f["domain"] == "object"}

    def scalars_at(n: int) -> set[str]:
        return {f["name"] for f in fields if f["checkpoint"] == n and f["domain"] == "galaxy" and f["stage"] not in catalogue_stages}

    def has_catalogue(n: int) -> bool:
        return any(f["domain"] == "object" and f["checkpoint"] <= n for f in fields)

    return catalogue_stages, scalars_at, has_catalogue


def test_the_segments_are_a_table_and_the_catalogue_rule_sees_no_catalogue_before_the_stars(model):
    """The lead's ruling on the contract (S59, after the build): the segment rows are a small table published whole
    with the run, not a catalogue, and their kind is one the viewer's catalogue rule does not see. While they were
    declared an object class's columns, ``arm_phases`` read as a catalogue stage: the viewer stopped asking for its
    five phases (rule D4's exclusion, meant for a stage whose scalar would materialise a galaxy's sample) and took
    checkpoint 3 for one with a sample to draw. Read here from the API's own listing, as the viewer's rule reads
    it, for every registered model: no catalogue at checkpoints 3 and 4, the first at 5 as before S59, and the
    five phases among what a viewer asks for at checkpoint 3."""
    fields = Service(grid=SMALL).handle("/api/fields", f"model={model.name}").json()["fields"]
    by_name = {f["name"]: f for f in fields}
    table = [f for f in fields if f["domain"] == "table"]
    assert [f["name"] for f in table] == list(pt.SEGMENT_FIELDS) and {f["of"] for f in table} == set(TABLES) == {"arm_segment"}
    for f in table:
        assert (f["kind"], f["stage"], f["checkpoint"], f["axes"], f["ramp"], f["categorical"]) == ("table_column", "arm_phases", 3, [], None, False), f["name"]
        assert "not shown by the viewer" in f["about"] and f["provenance"] == "synthetic", f["name"]
    assert {f["domain"] for f in fields} == {"grid", "galaxy", "object", "table"}
    assert not [f["name"] for f in fields if f["domain"] == "object" and f["of"] == "arm_segment"]
    catalogue_stages, scalars_at, has_catalogue = _viewer_rules(fields)
    assert "arm_phases" not in catalogue_stages
    assert not has_catalogue(3) and not has_catalogue(4) and has_catalogue(5)
    assert min(f["checkpoint"] for f in fields if f["domain"] == "object") == 5
    phases = set(pt.PHASE_FIELDS)
    assert phases == {f"arm_mode_phase_{m}" for m in (2, 3, 4, 5, 6)} and {by_name[n]["checkpoint"] for n in phases} == {3}
    assert phases <= scalars_at(3)
    # ... and they do not carry the sentence a catalogue stage's scalar carries: they are shown.
    assert not [n for n in phases if "Not shown by the viewer" in by_name[n]["about"]]


def test_the_api_serves_the_table_whole_and_no_census_route_carries_it(prod):
    """What ``/api/arrays`` does with a table column, stated: **it serves it**, whole, as one array of the table's
    rows - the published draws, to the bit - beside the scalars and grid fields asked with it; ``precision=f4``
    narrows it as it narrows any array, ``t_samples`` does not touch it (it has no axes), and with the layer off
    it is an array of no rows. No other route knows it: the census and region routes pick ``domain == "object"``
    columns of their own stages."""
    api = Service(grid=SMALL)
    ask = "fields=arm_segment_extent,arm_segment_pitch_deviate,arm_winding_anchor_radius,arm_mode_phase_3&texture_seed=3"
    got = api.handle("/api/arrays", ask)
    assert got.status == 200
    head, arrays = got.frame()
    o = run(the_model(prod), {"texture_seed": 3}, SMALL, only=(*pt.SEGMENT_FIELDS, "arm_winding_anchor_radius"))
    assert set(arrays) == set(pt.SEGMENT_FIELDS) and set(head["scalars"]) == {"arm_winding_anchor_radius", "arm_mode_phase_3"}
    for name in pt.SEGMENT_FIELDS:
        assert arrays[name].dtype == np.float64 and arrays[name].shape == (OUT_ROWS + IN_ROWS,), name
        assert arrays[name].tobytes() == np.asarray(o.fields[name]).tobytes(), name
        assert o.decls[name].kind is Kind.TABLE_COLUMN
    assert "arm_phases" in head["stages"] and not {"systems", "clouds", "clusters"} & set(head["stages"])
    _, narrow = api.handle("/api/arrays", ask + "&precision=f4&t_samples=8").frame()
    for name in pt.SEGMENT_FIELDS:
        assert narrow[name].dtype == np.float32 and np.array_equal(narrow[name], arrays[name].astype(np.float32)), name
    head_off, off = api.handle("/api/arrays", ask + "&layer=off").frame()
    assert all(off[name].shape == (0,) for name in pt.SEGMENT_FIELDS) and head_off["scalars"]["arm_mode_phase_3"] is None
    window = "r_min=7&r_max=9&phi_min=0&phi_max=0.4"
    for path, query in (("/api/region", window), ("/api/clouds", window), ("/api/clusters", window), ("/api/remnants", window),
                        ("/api/bright", window + "&n=50")):
        r = api.handle(path, query)
        assert r.status == 200, (path, r.body[:200])
        header, rows = wire.decode(r.body)
        assert header["columns"] and not [c for c in (*header["columns"], *rows) if c.startswith("arm_segment")], path


def test_a_table_is_declared_from_a_closed_list_and_takes_no_ramp():
    """The declaration's own refusals, on the segments' table: a name off the closed list, a ramp, an object
    class's kind with the table's name (``tests/test_fielddoc.py`` holds the kind's rules in full)."""
    from galaxy.core.fielddoc import OBJECTS, DeclarationError, Ramp

    assert "arm_segment" not in OBJECTS and TABLES == ("arm_segment",)
    base = dict(name="x", label="x", unit="rad", about="a probe")
    assert FieldDecl(kind=Kind.TABLE_COLUMN, of="arm_segment", **base).kind.domain == "table"
    for bad in (dict(kind=Kind.TABLE_COLUMN, of="star"), dict(kind=Kind.TABLE_COLUMN, of="arm_segment", ramp=Ramp("viridis")),
                dict(kind=Kind.COLUMN, of="arm_segment", ramp=Ramp("viridis"))):
        with pytest.raises(DeclarationError):
            FieldDecl(**base, **bad)
