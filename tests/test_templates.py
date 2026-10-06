"""The templates (S54, BUILD_III Phase T; DECISIONS.md D213): two named galaxies as data, the fit, the checks.

**The gates.** ``milky_way`` is the registry's defaults exactly, and a run of it is bit-identical to a run
with no inputs given - asserted on every published array, not on a hash of a few. ``template=milky_way``
and no template (D213 ruling 2, as the gate rewords it at S58, D217): the same bytes on every field; the
inputs carry the pin, so a second cache entry whose header differs by that word. An input in the query
overrides the template's; an unknown template is a 404 that names the registered ones. ``/api/templates``
is metadata and runs no stage (rule D4).

**The fit (D213 as amended at the gate).** The free set is a rule, in the template's data: a control is free
only if a target measures what it controls, and ``ngc_4414`` names four with the target beside each. The
other three are not stated at all, so they are the registry's defaults object for object, the tool never
passes them to the model, and nothing admits a control by weight. The committed values are where
``tools/fit_template.py``'s search stops - a point on a plateau resolved to the model's own steps, not a
minimum to the printed precision - and the three model numbers committed beside them are what the model
gives there. Where the search stops is what is tested, not a zero gradient: the three targets carry steps in
``halo_mass`` and ``disc_spin`` (debt #133; ``test_the_model_s_targets_are_stepped...`` pins it), so a
derivative at the committed point reads a tooth. One further cycle of the search from the committed values
finds nothing lower. A free control left on a bound is labelled ``bound`` with its finding (debt #132). The
whole search re-run from the registry's defaults (forty seconds) is opt-in: ``GALAXYGEN_REFIT=1``.

**The checks.** Each is defined as D213's table words it and on the reading's window. Each was read once,
blind, on the first fit (fit A, withdrawn): that reading is data beside the check, and every verdict on the
fit that stands is ``disclosed``, never blind. The verdicts are ``python -m galaxy.specs``'s to print, and
nothing here pins the model's number for one on the fit that stands (the ledger of recorded misses is the
lead's).
"""

from __future__ import annotations

import inspect
import json
import math
import os
import re
from pathlib import Path

import numpy as np
import pytest

import fit_template
from galaxy import templates
from galaxy.api import wire
from galaxy.api.service import RESERVED, Service, routes
from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, MergerEvent, controls, seeds
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.models.level0 import LEVEL0
from galaxy.run import run
from galaxy.specs import Problem
from galaxy.specs import templates as checks
from galaxy.stages import spectra

ROOT = Path(__file__).resolve().parents[1]
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
MILKY_WAY = templates.TEMPLATES["milky_way"]
NGC_4414 = templates.TEMPLATES["ngc_4414"]
# The routes that take inputs: every one whose handler lays a request's inputs over the registry's.
INPUT_ROUTES = ("/api/arrays", "/api/region", "/api/system", "/api/clouds", "/api/clusters", "/api/remnants",
                "/api/bright", "/api/render")
SECTOR = "r_min=7&r_max=9&phi_min=0&phi_max=0.4"
B_V = json.dumps([{"name": b, "shape": "gaussian", "centre": c, "fwhm": 900.0} for b, c in (("B", 4400.0), ("V", 5500.0))])
# S60 (D219 items 3 and 8): each template holds three pins. The Milky Way's third is its measured arms - the rows of
# Reid et al. 2019's Table 2 the template pins, the four major arms (Norma and the Outer arm as two chains) and the
# Local arm - and NGC 4414's its observed arm class, a name.
MW_ARMS = tuple(row for row in templates.REID_2019_TABLE2 if row[0] in templates.MILKY_WAY_PINNED_ARMS)
MW_PINS = {"bar_present": True, "sun_bar_angle": 30.0, "arm_pieces": MW_ARMS}
NGC_PINS = {"bar_present": False, "pitch_angle": 28.9, "arm_class": "flocculent"}
assert len(MW_ARMS) == 6 and [row[0] for row in MW_ARMS] == ["Norma", "Sct-Cen", "Sgr-Car", "Local", "Perseus", "Outer"]


def text(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def same(a, b) -> bool:
    """Bit for bit: arrays by dtype, shape and every element (NaN equal to NaN), scalars and labels by value."""
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a, b = np.asarray(a), np.asarray(b)
        if a.dtype != b.dtype or a.shape != b.shape:
            return False
        return a.tobytes() == b.tobytes()
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (math.isnan(a) and math.isnan(b))
    return a == b


# --- the registry of two ---------------------------------------------------------------------


def test_two_templates_are_registered_and_the_default_leads():
    assert templates.names() == ("milky_way", "ngc_4414")
    assert templates.DEFAULT == "milky_way" and templates.get("milky_way") is MILKY_WAY
    with pytest.raises(KeyError, match="registered"):
        templates.get("andromeda")
    for t in templates.TEMPLATES.values():
        t.validate()
        # S58 (D217 item 2): was `t.pins == ()` - each template pins the one measured fact of its structure there
        # is a pin for, the observed bar class (the tests of the pin are below).
        # S59 (D218 items 5-6): was ["bar_present"] for both - the Milky Way also pins where the Sun is (the bar's angle
        # to the Sun-centre line), NGC 4414 its measured mean pitch: each a number with its source.
        # S60 (D219 items 3 and 8): was two each - the Milky Way also pins its measured arms (a table), NGC 4414 its
        # observed arm class (a name).
        assert t.model == DEFAULT_MODEL and [p.name for p in t.pins] == (
            ["bar_present", "sun_bar_angle", "arm_pieces"] if t.name == "milky_way" else ["bar_present", "pitch_angle", "arm_class"]
        )
    assert (MILKY_WAY.filters, NGC_4414.filters) == ("rgb", "wfc3")


def test_milky_way_overrides_nothing_and_resolves_to_the_registry_s_defaults():
    """Ruling 1: its inputs are resolved from the registry when asked for, so it cannot drift from the defaults.

    S58 (D217 item 2): the template states one thing the registry does not - its pin, the observed bar class - and
    nothing else: no control, no seed, no event list. Until S58 its overrides were empty and its resolved inputs
    the registry's whole table; they are the pin, and the table's controls, seeds and event list with the pin."""
    # S59 (D218 item 5): was {"bar_present": True}; S58 (D217): was {}
    # S60 (D219 item 8): was {"bar_present": True, "sun_bar_angle": 30.0} - the measured arms join them (MW_PINS).
    assert templates.overrides(MILKY_WAY) == MW_PINS == templates.pinned(MILKY_WAY)
    assert not MILKY_WAY.controls and not MILKY_WAY.seeds and MILKY_WAY.mergers is None
    assert MILKY_WAY.fit is None and MILKY_WAY.checks == ()
    resolved = templates.resolve(MILKY_WAY)
    # S59 (D218): was `== list(INPUTS)` - a pin the template does not state (the pitch) is not among its inputs.
    # S60 (D219): nor the arm class, which the Milky Way does not state either (the model derives it from the bar).
    assert list(resolved) == [n for n in INPUTS if n not in ("pitch_angle", "arm_class")]
    for name, inp in INPUTS.items():
        if name in ("pitch_angle", "arm_class"):
            continue
        if inp.kind == "pin":
            # a pin has no default: the template's is the only one (S59: was `is True` - one of the two is a number)
            assert resolved[name] == MW_PINS[name] and inp.default is None, name
        else:
            assert resolved[name] is inp.default, name  # the registry's own object, not a copy of its value


def test_a_pin_is_a_measured_fact_with_its_source_and_replaces_nothing_but_the_verdict():
    """D217 item 2: "a template-only field ``bar_present`` (true/false, the observed class with its source) that
    replaces the derived presence when given ... ``milky_way`` pins barred, ``ngc_4414`` pins unbarred. This is a
    measured fact entering as template structure, not a fit: no parameter is set to a number." """
    from dataclasses import replace

    mw, ngc = MILKY_WAY.pins[0], NGC_4414.pins[0]
    assert (mw.name, mw.value, ngc.name, ngc.value) == ("bar_present", True, "bar_present", False)
    assert "Bland-Hawthorn & Gerhard 2016" in mw.source and "rows 15-17" in mw.source and "[verified:" in mw.source
    assert "READING_NGC_4414.md, row 16" in ngc.source and "RC3 SA" in ngc.source and "S4G fits no bar component" in ngc.source
    assert "D217 item 2" in mw.source and "D217 item 2" in ngc.source
    reading = " ".join(text("READING_NGC_4414.md").split())
    assert "NGC 4414 has no bar" in reading and "S4G fits none" in reading and "SA(rs)c? (RC3)" in reading
    # S59 (D218 item 6): was {"bar_present": False} alone - the measured mean pitch joins it.
    # S60 (D219 item 3): and the observed arm class, flocculent - a name, which the model derives of no disc.
    assert templates.pinned(NGC_4414) == NGC_PINS and templates.overrides(NGC_4414)["bar_present"] is False
    # It is an input of its own kind: no control, no seed; not a number of the template (it carries its own source),
    # so it is no path of `numbers` and no free control of a fit.
    assert INPUTS["bar_present"].kind == "pin" and "bar_present" not in {c.name for c in controls()} | {x.name for x in seeds()}
    assert not any("bar_present" in path for path in templates.numbers(NGC_4414)) and "bar_present" not in NGC_4414.fit.free
    assert "pinned unbarred, as observed" in NGC_4414.about and "the Milky Way is barred" in MILKY_WAY.about
    # Refused: a value that is not a class, a pin without a tagged source, a name the registry does not hold as a
    # pin, the same input pinned twice.
    # S60 (D219 items 3 and 8): was `Pin("bar_present", "yes", ...)` refused when built - a text is a named class's
    # value now, so a value of no shape at all is what the builder refuses, and "yes" for a class of two is the
    # template's to refuse (below).
    with pytest.raises(templates.TemplateError, match="True or False"):
        templates.Pin("bar_present", None, "[inferred] x")  # type: ignore[arg-type]
    with pytest.raises(templates.TemplateError, match="a class, True or False"):
        replace(NGC_4414, pins=(templates.Pin("bar_present", "yes", "[inferred] x"),)).validate()
    # S59 (D218 items 5-6): was `Pin("bar_present", 1, ...)` refused when built - a pin may now be a measured number,
    # and which it is, is the registry's: a class given a number, or a number given a class, is refused by the
    # template that states it.
    with pytest.raises(templates.TemplateError, match="a class, True or False"):
        replace(NGC_4414, pins=(templates.Pin("bar_present", 1, "[inferred] x"),)).validate()
    with pytest.raises(templates.TemplateError, match="a measured number in deg"):
        replace(NGC_4414, pins=(templates.Pin("pitch_angle", True, "[inferred] x"),)).validate()
    with pytest.raises(templates.TemplateError, match="finite number"):
        templates.Pin("pitch_angle", float("nan"), "[inferred] x")
    # S60 (D219 items 3 and 8): the two new shapes are held to the registry's declaration by the template that
    # states them - a name outside the closed list of classes, a row of the wrong length, a cell of the wrong
    # type, a table whose rows the declaration's own check faults - and a table of measured arms is placed by the
    # Sun, so a template that pins one without the Sun's angle and a bar is refused.
    with pytest.raises(templates.TemplateError, match="is one of \\['grand_design', 'multi_armed', 'flocculent'\\]"):
        replace(NGC_4414, pins=(*NGC_4414.pins[:2], templates.Pin("arm_class", "ringed", "[inferred] x"))).validate()
    with pytest.raises(templates.TemplateError, match="a row holds"):
        replace(MILKY_WAY, pins=(*MILKY_WAY.pins[:2], templates.Pin("arm_pieces", (("Local", 1.0),), "[inferred] x"))).validate()
    with pytest.raises(templates.TemplateError, match="column arm is a name"):
        replace(MILKY_WAY, pins=(*MILKY_WAY.pins[:2], templates.Pin("arm_pieces", ((4.0, -8.0, 34.0, 9.0, 8.26, 11.4, 11.4),), "[inferred] x"))).validate()
    with pytest.raises(templates.TemplateError, match="named twice"):
        replace(MILKY_WAY, pins=(*MILKY_WAY.pins[:2], templates.Pin("arm_pieces", (MW_ARMS[0], MW_ARMS[0]), "[inferred] x"))).validate()
    with pytest.raises(templates.TemplateError, match="placed by the Sun's azimuth"):
        replace(MILKY_WAY, pins=(MILKY_WAY.pins[0], MILKY_WAY.pins[2])).validate()
    with pytest.raises(templates.TemplateError, match="placed by the Sun's azimuth"):
        replace(MILKY_WAY, pins=(replace(MILKY_WAY.pins[0], value=False), *MILKY_WAY.pins[1:])).validate()
    # A list of lists given to the builder is the same table, as tuples.
    assert templates.Pin("arm_pieces", [list(row) for row in MW_ARMS], "[inferred] x").value == MW_ARMS  # type: ignore[arg-type]
    with pytest.raises(templates.TemplateError, match="rows of a measured table"):
        templates.Pin("arm_pieces", (), "[inferred] x")
    with pytest.raises(templates.TemplateError, match="carries no tag"):
        templates.Pin("bar_present", True, "the galaxy's bar")
    with pytest.raises(templates.TemplateError, match="not a registered pin"):
        replace(NGC_4414, pins=(templates.Pin("halo_mass", True, "[inferred] x"),)).validate()
    with pytest.raises(templates.TemplateError, match="each input pinned once"):
        replace(NGC_4414, pins=(ngc, ngc))
    with pytest.raises(templates.TemplateError, match="each input pinned once"):
        replace(NGC_4414, pins=({"name": "bar_present", "value": False},))
    # A one-field flip restores the barred picture with nothing else changed (D217, the owner's part): the template
    # with its pin flipped is the same inputs but for the pin.
    flipped = replace(NGC_4414, pins=(replace(ngc, value=True), *NGC_4414.pins[1:]))
    flipped.validate()
    assert {k: v for k, v in templates.resolve(flipped).items() if k != "bar_present"} == {k: v for k, v in templates.resolve(NGC_4414).items() if k != "bar_present"}


def test_a_run_of_milky_way_is_bit_identical_to_a_run_with_no_inputs(prod):
    """The gate (BUILD_III Phase T): every published field of the whole pipeline on the production grid."""
    model = prod[0].get(MILKY_WAY.model)
    bare = run(model)
    named = run(model, templates.resolve(MILKY_WAY))
    # S58 (D217 item 2): was `named.inputs == bare.inputs`. The template pins the Milky Way barred; the bare run
    # pins nothing and derives - barred, at the defaults - so the two differ by the pin among their inputs and
    # **by no bit of any field**, which is the gate, below.
    # S59 (D218 item 5): was {**bare.inputs, "bar_present": True} - and where the Sun is, which moves one field:
    # ``sun_azimuth``, a number for the template and not one for the bare run. Every other field: no bit.
    # S60 (D219 item 8): and the measured arms. **With the layer on the template is no longer the bare default
    # galaxy**: its arms are pinned where Reid et al. 2019 measured them, so the layer's census of pieces, the
    # fields composed from it (the stellar pattern's, the gas's answer, the azimuthal modulation) and every census
    # a pattern places - its columns and the statistics computed from the realised objects - are another
    # realisation. **Every law is the same bits**: nothing the bar and the pattern stages publish, nothing of
    # checkpoints 1 and 2, nothing downstream that reads no pattern (the remnants, the dust, the light) moves. With
    # the layer off the two are still bit-identical but for the Sun's azimuth, and that is the run the acceptance
    # table is judged on (below).
    assert named.inputs == {**bare.inputs, **MW_PINS} and "bar_present" not in bare.inputs and named.order == bare.order
    assert math.isnan(float(bare.fields["sun_azimuth"])) and float(named.fields["sun_azimuth"]) == pytest.approx(1.09539, abs=2e-5)
    assert bare.fields["bar_present"] == named.fields["bar_present"] == "yes"
    assert set(named.fields) == set(bare.fields) and len(bare.fields) > 300
    differ = {name for name, value in bare.fields.items() if not same(value, named.fields[name])}
    assert "sun_azimuth" in differ
    producer = {d.name: sid for sid in named.order for d in prod[1].get(sid).publishes}
    placed = {"star", "planet", "bright_star", "cloud", "cluster"}  # the object classes a pattern places (tests/test_layer.py)
    censuses = {"systems", "planets", "bright_stars", "clouds", "nebular", "bubbles"}  # the stages that count them
    moved_laws, moved_statistics = set(), set()
    for name in differ - {"sun_azimuth"}:
        d = named.decls[name]
        if d.kind.domain == "table":
            assert d.of == "arm_piece" and producer[name] == "arm_pieces", name  # the layer's census of pieces
        elif d.composed:
            assert producer[name] in ("stellar_pattern", "gas_pattern", "sfh_azimuthal"), name  # what reads the pieces
        elif d.kind.domain == "object":
            assert d.of in placed, name  # a placed census is another draw; the remnants (unplaced) are the same bits
        elif producer[name] in censuses and d.axes in ((), ("R",)):
            moved_statistics.add(name)  # a statistic of a placed census's realised objects
        else:
            moved_laws.add(name)
    assert moved_laws == set(), sorted(moved_laws)  # no law, no checkpoint-1 or -2 field, nothing that reads no pattern
    # The whole table and every composed field moved - the pinned arms are placed - and every column of every
    # placed census; the statistics that moved are a subset of the fourteen tests/test_layer.py lists (the rest
    # land on the same bits by rounding, as a census statistic may).
    assert {n for n, d in named.decls.items() if d.kind.domain == "table" or d.composed} <= differ
    assert {n for n, d in named.decls.items() if d.kind.domain == "object" and d.of in placed} <= differ
    assert {n for n, d in named.decls.items() if d.kind.domain == "object" and d.of not in placed}.isdisjoint(differ)
    assert moved_statistics <= {
        "catalogue_size", "planet_count_sample", "mean_planets_per_star", "giant_fraction_sample", "bright_star_limit",
        "cloud_mass_total", "dig_halpha_fraction", "hii_luminosity_function_slope", "nii_halpha_gradient_hii",
        "oiii_5007_surface_brightness_hii", "nii_6583_surface_brightness_hii", "sii_6716_surface_brightness_hii",
        "sii_6731_surface_brightness_hii", "hot_phase_porosity",
        # the two expected totals, which the layer moves by rounding alone (I1: within four units in the last place)
        "cloud_count_total", "bright_star_count_1e3",
    }, sorted(moved_statistics)
    for name in ("cloud_count_total", "bright_star_count_1e3"):
        a, b = float(bare.fields[name]), float(named.fields[name])
        assert abs(a - b) <= 4.0 * float(np.spacing(max(abs(a), abs(b)))), (name, a, b)
    arrays = sum(isinstance(v, np.ndarray) for v in bare.fields.values())
    assert arrays > 150  # the comparison is on arrays, not on a handful of scalars
    # ... and with the layer off, the run the acceptance table is judged on: bit-identical but for the Sun.
    off, named_off = run(model, layer=False), run(model, templates.resolve(MILKY_WAY), layer=False)
    for name, value in off.fields.items():
        assert name == "sun_azimuth" or same(value, named_off.fields[name]), f"{name} differs between the template and the bare run, layer off"
    assert float(named_off.fields["sun_azimuth"]) == float(named.fields["sun_azimuth"])  # a law's number: the layer does not move it
    # The pinned arms are in the layer-on census and nowhere with the layer off: six rows of the table say so.
    assert int(np.asarray(named.fields["arm_piece_pinned"]).sum()) >= len(MW_ARMS) and not np.asarray(bare.fields["arm_piece_pinned"]).any()
    assert np.asarray(named_off.fields["arm_piece_pinned"]).shape == (0,)


FREE = {"halo_mass": "curve_peak", "disc_spin": "disc_scale_length", "halo_assembly_z": "curve_peak",
        "baryon_retention": "stellar_mass"}
HELD = ("infall_timescale", "inside_out_index", "migration_efficiency")


def test_ngc_4414_states_the_controls_its_targets_measure_and_invents_nothing():
    """D213 as amended, ruling 1: a control is free only if a fit target measures what it controls; every other
    control stays at the registry's default and does not move. Ruling 4: no merger, every seed 4414."""
    assert dict(NGC_4414.fit.free) == FREE and set(NGC_4414.controls) == set(FREE)
    assert set(FREE) | set(HELD) == {c.name for c in controls()}
    assert set(FREE.values()) == {t.name for t in NGC_4414.fit.targets}  # each target measures something
    assert dict(NGC_4414.fit.measures) == {
        "halo_mass": "the peak", "disc_spin": "the scale length",
        "halo_assembly_z": "the peak at a given disc, through the concentration",
        "baryon_retention": "the stellar mass at a given halo",
    }
    for c in controls():
        if c.name in FREE:
            assert c.lo <= NGC_4414.controls[c.name] <= c.hi, c.name
    # The held controls are not stated, so they are the registry's own defaults, exactly, and cannot have moved.
    resolved = templates.resolve(NGC_4414)
    given = templates.overrides(NGC_4414)
    for name in HELD:
        assert name not in NGC_4414.controls and name not in given and name not in NGC_4414.sources
        assert resolved[name] is INPUTS[name].default and resolved[name] == INPUTS[name].default, name
    assert (resolved["infall_timescale"], resolved["inside_out_index"], resolved["migration_efficiency"]) == (7.0, 1.0, 3.6)
    assert dict(NGC_4414.seeds) == {s.name: 4414 for s in seeds()}  # a new seed in the registry fails here
    assert NGC_4414.mergers == ()
    # S59 (D218): the Sun is the Milky Way's. S60 (D219 item 8): and so are the measured arms.
    assert set(resolved) == set(INPUTS) - {"sun_bar_angle", "arm_pieces"} and resolved["mergers"] == ()
    # S58 (D217 item 2): the pin joins what the template states - a measured class, not a control.
    # S59 (D218 item 6): and the measured mean pitch. S60 (D219 item 3): and the observed arm class.
    assert set(given) == set(FREE) | {s.name for s in seeds()} | {"mergers", *NGC_PINS} and {n: given[n] for n in NGC_PINS} == NGC_PINS
    assert (NGC_4414.camera.inclination_deg, NGC_4414.camera.azimuth_deg, NGC_4414.camera.fov_deg) == (55.0, 0.0, 5.0)
    assert (MILKY_WAY.camera.inclination_deg, MILKY_WAY.camera.azimuth_deg, MILKY_WAY.camera.radius_kpc,
            MILKY_WAY.camera.fov_deg) == (0.0, 270.0, 20.0, 45.0)
    assert (NGC_4414.instrument.distance_mpc, NGC_4414.instrument.pixel_scale_arcsec) == (17.7, None)
    assert (MILKY_WAY.instrument.distance_mpc, MILKY_WAY.instrument.pixel_scale_arcsec) == (None, None)
    # The frame holds the disc: the 3.6 micron isophote the source's tag names, 153.5 arcsec at 17.7 Mpc.
    assert 153.5 * 17.7e3 * math.radians(1.0 / 3600.0) < NGC_4414.camera.radius_kpc


def test_a_bound_is_labelled_and_its_finding_written_out():
    """Ruling 3: a value on a bound is a finding, not a fit. It is labelled in the template's data with the
    finding in the ruling's words and its debt; no bound value is rounded or nudged inside."""
    table = {c.name: c for c in controls()}
    on_bound = {n for n, v in NGC_4414.controls.items() if v in (table[n].lo, table[n].hi)}
    assert on_bound == set(NGC_4414.fit.bounds) == {"halo_assembly_z"}
    assert NGC_4414.controls["halo_assembly_z"] == table["halo_assembly_z"].lo == 0.5  # the bound itself, exactly
    finding = NGC_4414.fit.bounds["halo_assembly_z"]
    ruled = ("the model cannot lower its inner peak enough for this disc inside the range; the concentration "
             "floor, or the concentration–mass relation, is the debt")
    assert finding.startswith(ruled) and "debt #132" in finding and "[verified: DECISIONS.md D213" in finding
    assert ruled in " ".join(text("DECISIONS.md").split())  # the ruling's own sentence, whatever its line breaks
    # No published range moved: the registry's are the ones the ruling quotes.
    assert [(c.name, c.lo, c.hi) for c in controls()] == [
        ("halo_mass", 1e11, 1e13), ("disc_spin", 0.005, 0.05), ("halo_assembly_z", 0.5, 5.0),
        ("baryon_retention", 0.05, 0.5), ("infall_timescale", 1.0, 14.0), ("inside_out_index", 0.0, 3.0),
        ("migration_efficiency", 0.0, 8.0)]


def test_a_template_is_refused_what_the_registry_does_not_hold():
    from dataclasses import replace

    with pytest.raises(templates.TemplateError, match="not a registered control"):
        replace(NGC_4414, controls={"bar_strength": 1.0}).validate()
    with pytest.raises(templates.TemplateError, match="outside"):
        replace(NGC_4414, controls={**NGC_4414.controls, "disc_spin": 0.5}).validate()
    # S55 (D214 section 3): the example was texture_seed, which the registry did not hold until the randomness
    # layer's seed joined it - and which this template now states (4414). A seed nobody registered is still refused.
    with pytest.raises(templates.TemplateError, match="not a registered seed"):
        replace(NGC_4414, seeds={"glitter_seed": 1}).validate()
    assert NGC_4414.seeds["texture_seed"] == 4414 and "texture_seed" not in MILKY_WAY.seeds
    assert templates.resolve(MILKY_WAY)["texture_seed"] == 0  # the default template: the registry's own
    with pytest.raises(templates.TemplateError, match="no source"):
        replace(NGC_4414, sources={}).validate()
    with pytest.raises(templates.TemplateError, match="carries no tag"):
        replace(NGC_4414, sources={**NGC_4414.sources, "camera.fov_deg": "a long lens"}).validate()
    with pytest.raises(templates.TemplateError, match="they are not checks"):
        replace(NGC_4414, checks=(replace(NGC_4414.checks[1], field="stellar_mass_total", first_reading=None),)).validate()


def test_a_fit_cannot_move_a_control_no_target_measures():
    """The free set is the stated set. A template that states a held control - at its default or anywhere else -
    is refused; so is a free control with no target, a bound without its label and a label without its bound."""
    from dataclasses import replace

    fit = NGC_4414.fit
    moved = {**NGC_4414.controls, "infall_timescale": 1.0}
    with pytest.raises(templates.TemplateError, match="stays at the registry's default"):
        replace(NGC_4414, controls=moved, sources={**NGC_4414.sources, "inputs.controls.infall_timescale": "[inferred] x"}).validate()
    at_default = {**NGC_4414.controls, "migration_efficiency": 3.6}
    with pytest.raises(templates.TemplateError, match="stays at the registry's default"):
        replace(NGC_4414, controls=at_default, sources={**NGC_4414.sources, "inputs.controls.migration_efficiency": "[inferred] x"}).validate()
    with pytest.raises(templates.TemplateError, match="not one of the fit's targets"):
        replace(fit, free={**fit.free, "infall_timescale": "star_formation_rate"}, measures={**fit.measures, "infall_timescale": "x"})
    with pytest.raises(templates.TemplateError, match="none is admitted any other way"):
        replace(fit, free={}, measures={}, bounds={})
    with pytest.raises(templates.TemplateError, match="says how its target measures it"):
        replace(fit, measures={})
    with pytest.raises(templates.TemplateError, match="only a free control can stand on a bound"):
        replace(fit, bounds={**fit.bounds, "infall_timescale": "x"})
    with pytest.raises(templates.TemplateError, match="a value on a bound is a finding"):
        replace(NGC_4414, fit=replace(fit, bounds={})).validate()
    with pytest.raises(templates.TemplateError, match="a value on a bound is a finding"):
        replace(NGC_4414, fit=replace(fit, bounds={**fit.bounds, "disc_spin": "x"})).validate()


# --- every number carries its tag (rule B14) ---------------------------------------------------


def test_every_number_of_ngc_4414_has_a_tag_and_the_tag_s_citation_exists():
    reading = text("READING_NGC_4414.md")
    decisions = text("DECISIONS.md")
    assert "### D213." in decisions
    paths = templates.numbers(NGC_4414)
    assert len(paths) == 4 + len(seeds()) + 1 + 4 + 1  # the free controls, seeds, the merger list, the camera, the distance
    tagged = {path: NGC_4414.sources[path] for path in paths}
    tagged |= {f"fit.targets.{t.name}": t.source for t in NGC_4414.fit.targets}
    tagged |= {f"checks.{c.name}": c.source for c in NGC_4414.checks}
    for path, source in tagged.items():
        assert any(tag in source for tag in templates.TAGS), path
        for cited in re.findall(r"tests/test_templates\.py::(\w+)", source):
            assert callable(globals().get(cited)), f"{path} cites a test that is not here: {cited}"
    # A read number names the reading and one of its source keys; a display choice says it is one.
    keys = {"camera.inclination_deg": "W04", "instrument.distance_mpc": "F01", "camera.radius_kpc": "S4G",
            "fit.targets.curve_peak": "P16", "fit.targets.disc_scale_length": "S4G", "fit.targets.stellar_mass": "z0MGS",
            "checks.curve_shape": "P16", "checks.star_formation_rate": "z0MGS", "checks.hydrogen_mass": "H03",
            "checks.absolute_magnitude_k": "2MRS", "checks.colour_b_v_face_on": "RC3"}
    for path, key in keys.items():
        assert "READING_NGC_4414.md" in tagged[path] and key in tagged[path], path
        assert re.search(rf"\*\*{re.escape(key)}\b|{re.escape(key)}/", reading), f"{key} is not a source key of the reading"
    for path in ("camera.azimuth_deg", "camera.radius_kpc", "camera.fov_deg", *(f"inputs.seeds.{s.name}" for s in seeds())):
        assert "[inferred]" in tagged[path], path
    for name in FREE:
        fitted = tagged[f"inputs.controls.{name}"]
        assert "fitted 2026-10-0" in fitted and "tools/fit_template.py ngc_4414" in fitted and "[verified:" in fitted
        assert "a target measures it" in fitted and "plateau" in fitted and "not a minimum to the printed precision" in fitted
    assert not any(f"inputs.controls.{name}" in tagged for name in HELD)  # a held control states no number of its own
    assert "no merger of NGC 4414 was read" in tagged["inputs.mergers"]
    # What was not read is None and carries no source to dress it as a number (rule B9).
    assert "instrument.pixel_scale_arcsec" not in NGC_4414.sources
    # The numbers the tags quote are the reading's own.
    for quoted in ("V_max = 237 ± 10, V_flat = 185 ± 10", "h_r = 19.22″", "log M* = 10.65 ± 0.10", "i = 55 ± 2",
                   "μ_Z = 31.24, D_Z = 17.70 Mpc", "(B−V)_T⁰ = 0.77", "153.5″"):
        assert quoted in reading, quoted


# --- template= on the routes that take inputs --------------------------------------------------


def test_every_route_that_takes_inputs_takes_a_template():
    assert "template" in RESERVED and "template" not in INPUTS
    by_path = {r.path: r for r in routes()}
    for path in INPUT_ROUTES:
        assert "template" in by_path[path].params, path
    # ... and those are all of them: a route that names a model and is not metadata lays inputs over it.
    metadata = {"/api/stages", "/api/fields", "/api/inputs"}
    assert {r.path for r in routes() if "model" in r.params} - metadata == set(INPUT_ROUTES)
    source = inspect.getsource(Service)
    for path in INPUT_ROUTES:
        handler = getattr(Service, "_" + by_path[path].handler)
        assert "self._overrides(model, q)" in inspect.getsource(handler), path
    assert source.count("self._overrides(model, q)") == len(INPUT_ROUTES)


@pytest.mark.parametrize("route, query", [
    ("/api/arrays", "fields=stellar_surface_density,stellar_mass_total"),
    ("/api/clouds", SECTOR),
    ("/api/region", SECTOR),
])
@pytest.mark.parametrize("layer", ["", "&layer=off"], ids=["layer on", "layer off"])
def test_naming_the_default_template_is_naming_none(route, query, layer):
    """Ruling 2 (D213) was "one point in input space - one cache entry, the same bytes". **As the gate rewords it at
    S58 (D217 item 2 and its follow-up): "the same bytes on every field; the inputs carry the pin, so a second
    cache entry whose header differs by that word".** The default template pins the Milky Way barred; a request
    that names no template pins nothing and the model derives - barred, at the defaults. So the two requests hold
    the same arrays and the same scalars, bit for bit, and their headers differ in one word: the template's request
    carries the pin among its inputs. They are two cache entries, and naming the template runs the stages again.

    **S60 (D219 item 8): that holds with the layer off, and with the layer on for what reads no pattern.** The
    template pins the Milky Way's measured arms, which the layer places; so with the layer on a census route's
    window holds other objects - other counts per cell, other rows - and its header's counts differ with them, while
    a field no pattern composes or places (the disc's surface density, its stellar mass) is the same bytes either
    way. The inputs carry the three pins; the arms' rows are JSON like any input."""
    api = Service(grid=SMALL)
    bare = api.handle(route, query + layer)  # cold: it runs the closure
    named = api.handle(route, query + layer + "&template=milky_way")
    again = api.handle(route, query + layer)
    assert bare.status == named.status == again.status == 200
    # S58 (D217): was `named.stages == ()` and one cache entry.
    assert bare.stages and named.stages == bare.stages and again.stages == ()
    assert len(api._cache) == 2
    warm = api.handle(route, query + layer + "&template=milky_way")
    assert warm.stages == () and len(api._cache) == 2 and again.body == api.handle(route, query + layer).body  # warm against warm
    bare_head, bare_arrays = bare.frame()
    named_head, named_arrays = named.frame()
    # S58 (D217): was `bare inputs == named inputs` and `named.body == bare.body`.
    # S59 (D218): the second pin. S60 (D219 item 8): the third, the measured arms, whose rows come back as lists.
    assert named_head["inputs"] == {**bare_head["inputs"], **MW_PINS, "arm_pieces": [list(row) for row in MW_ARMS]}
    assert "bar_present" not in bare_head["inputs"]
    assert list(named_arrays) == list(bare_arrays)
    differing = {k for k in set(bare_head) | set(named_head) if bare_head.get(k) != named_head.get(k)}
    if layer or route == "/api/arrays":
        # The same bytes on every field, the header the same but for the inputs.
        assert differing == {"inputs"}
        for name, array in bare_arrays.items():
            assert same(array, named_arrays[name]), name
    else:
        # The pinned arms are placed: the window's objects are another draw, every column of them, and the header
        # counts them - the cells' counts, the arrays' shapes, the census's materialised number. A scalar that
        # rides in the header is an expected total, which the layer moves by rounding alone (within four units in
        # the last place, as tests/test_layer.py holds it).
        assert {"inputs", "arrays", "cells"} <= differing <= {"inputs", "arrays", "cells", "clouds", "stars", "scalars"}, differing
        assert bare_head["cells"]["ids"] == named_head["cells"]["ids"] and bare_head["cells"]["counts"] != named_head["cells"]["counts"]
        for name, array in bare_arrays.items():
            assert not same(array, named_arrays[name]), name
        for name, value in bare_head.get("scalars", {}).items():
            other = named_head["scalars"][name]
            if value != other:
                assert name == "cloud_count_total" and abs(value - other) <= 4.0 * float(np.spacing(max(abs(value), abs(other)))), name
    # ... and cold against cold, on a second service: the same bytes as the first named request's.
    cold = Service(grid=SMALL).handle(route, "template=milky_way&" + query + layer)
    assert cold.stages == bare.stages and cold.body == named.body


def test_a_pin_is_given_by_a_template_and_by_no_query_parameter():
    """D217 item 2: "a template-only field". The API takes a pin from ``template=`` alone: naming one as an input
    is a 400 that says so, whatever its value, with a template or without; ``/api/inputs`` does not offer it; and
    ``/api/templates`` publishes each template's pins with their sources."""
    api = Service(grid=SMALL)
    for query in ("fields=bar_present&bar_present=false", "fields=bar_present&bar_present=true", "fields=bar_present&bar_present=0",
                  "fields=bar_present&template=ngc_4414&bar_present=true"):
        got = api.handle("/api/arrays", query)
        assert got.status == 400 and got.stages == () and "is a template's pin, not an input a request may set" in got.json()["error"], query
    listed = api.handle("/api/inputs").json()
    assert set(listed) == {"model", "ceiling", "controls", "seeds", "events"}
    assert "bar_present" not in [i["name"] for kind in ("controls", "seeds", "events") for i in listed[kind]]
    assert len(listed["controls"]) == 7 and len(listed["seeds"]) == 5 and len(listed["events"]) == 1
    # What the three ways of asking say: no template derives (barred at the defaults); each template states its class.
    wanted = "fields=bar_present,bar_formation_time,bar_half_length"
    bare, mw, ngc = (api.handle("/api/arrays", wanted + extra).frame()[0] for extra in ("", "&template=milky_way", "&template=ngc_4414"))
    assert (bare["scalars"]["bar_present"], mw["scalars"]["bar_present"], ngc["scalars"]["bar_present"]) == ("yes", "yes", "no")
    assert "bar_present" not in bare["inputs"] and mw["inputs"]["bar_present"] is True and ngc["inputs"]["bar_present"] is False
    assert bare["scalars"]["bar_half_length"] == mw["scalars"]["bar_half_length"] and ngc["scalars"]["bar_half_length"] is None
    assert ngc["scalars"]["bar_formation_time"] == pytest.approx(0.905, abs=0.01)  # published beside the pin
    # "Edit galaxy" from a template keeps its pin: the query moves a control, the template still says the class.
    edited = api.handle("/api/arrays", wanted + "&template=ngc_4414&halo_mass=2e12").frame()[0]
    assert edited["inputs"]["bar_present"] is False and edited["scalars"]["bar_present"] == "no"
    # The same controls, seeds and event list with no template are the disc the model derives a bar for.
    spelled = "&".join(f"{n}={v!r}" for n, v in {**NGC_4414.controls, **NGC_4414.seeds}.items()) + "&mergers=[]"
    unpinned = api.handle("/api/arrays", wanted + "&" + spelled).frame()[0]
    assert "bar_present" not in unpinned["inputs"] and unpinned["scalars"]["bar_present"] == "yes"
    assert unpinned["scalars"]["bar_formation_time"] == ngc["scalars"]["bar_formation_time"]


def test_a_template_s_inputs_are_the_base_and_the_query_overrides_them():
    api = Service(grid=SMALL)
    base = api.handle("/api/arrays", "fields=stellar_mass_total&template=ngc_4414")
    assert base.status == 200
    published = next(t for t in api.handle("/api/templates").json()["templates"] if t["name"] == "ngc_4414")["inputs"]
    got = base.frame()[0]["inputs"]
    assert {n: got[n] for n in published["controls"]} == published["controls"]
    assert {n: got[n] for n in published["seeds"]} == published["seeds"] and got["mergers"] == []
    # "Edit galaxy" starts from the template and moves a control: the control is the query's, the rest the template's.
    moved = api.handle("/api/arrays", "fields=stellar_mass_total&template=ngc_4414&halo_mass=2e12&world_seed=7").frame()[0]
    assert moved["inputs"]["halo_mass"] == 2e12 and moved["inputs"]["world_seed"] == 7
    assert {n: v for n, v in moved["inputs"].items() if n not in ("halo_mass", "world_seed")} == {
        n: v for n, v in got.items() if n not in ("halo_mass", "world_seed")}
    assert moved["scalars"]["stellar_mass_total"] != base.frame()[0]["scalars"]["stellar_mass_total"]
    event = '[{"time":5,"mass_ratio":0.3,"gas_fraction":0.4}]'
    merged = api.handle("/api/arrays", f"fields=last_major_merger_time&template=ngc_4414&mergers={event}").frame()[0]
    assert merged["scalars"]["last_major_merger_time"] == 5.0
    assert api.handle("/api/arrays", "fields=last_major_merger_time&template=ngc_4414").frame()[0]["scalars"][
        "last_major_merger_time"] == 0.0  # the template's list is empty: no merger, not the Milky Way's two
    # The same inputs spelled out beside the template are the same point: the same cache entry. S58 (D217 item 2):
    # was "spelled out with no template" - without the template the pin is not given, and that is another galaxy
    # (the model derives a bar for this disc): another point, another entry, the same stellar mass.
    api = Service(grid=SMALL)
    first = api.handle("/api/arrays", "fields=stellar_mass_total&template=ngc_4414")
    spelled = "&".join(f"{n}={v!r}" for n, v in {**NGC_4414.controls, **NGC_4414.seeds}.items()) + "&mergers=[]"
    second = api.handle("/api/arrays", "fields=stellar_mass_total&template=ngc_4414&" + spelled)
    assert first.stages and second.stages == () and len(api._cache) == 1
    third = api.handle("/api/arrays", "fields=stellar_mass_total&" + spelled)
    assert third.stages and len(api._cache) == 2
    assert third.frame()[0]["scalars"] == first.frame()[0]["scalars"] and "bar_present" not in third.frame()[0]["inputs"]
    # A range is still enforced on what the query gives, and the model= parameter still chooses the model.
    assert api.handle("/api/arrays", "fields=stellar_mass_total&template=ngc_4414&disc_spin=0.5").status == 400
    other = next(n for n in api.models.names() if n != NGC_4414.model)
    assert api.handle("/api/arrays", f"fields=stellar_mass_total&template=ngc_4414&model={other}").frame()[0]["model"] == other
    assert first.frame()[0]["model"] == NGC_4414.model


@pytest.mark.parametrize("route", INPUT_ROUTES)
def test_an_unknown_template_is_a_404_that_names_the_registered_ones(route):
    got = Service(grid=SMALL).handle(route, "template=andromeda&fields=stellar_mass_total&cell=0&index=0&n=10&filters=" + B_V)
    assert got.status == 404 and got.stages == ()
    assert got.json()["error"] == "no template 'andromeda'; registered: ['milky_way', 'ngc_4414']"


def test_a_template_given_twice_is_refused():
    assert Service(grid=SMALL).handle("/api/arrays", "fields=sfr&template=milky_way&template=ngc_4414").status == 400


# --- /api/templates: metadata ----------------------------------------------------------------

TEMPLATE_KEYS = {"name", "label", "about", "model", "inputs", "camera", "filters", "instrument", "pins", "fit", "checks", "sources"}
TARGET_KEYS = {"name", "label", "field", "unit", "value", "half_window", "window", "source", "model", "residual"}
FIT_KEYS = {"targets", "controls", "objective", "objective_value", "tool", "method", "date", "evaluations"}
CHECK_KEYS = {"name", "label", "unit", "window", "quantity", "mismatch", "source", "standing", "standing_about", "first_reading"}
CONTROL_KEYS = {"name", "default", "fitted", "lo", "hi", "free", "measured_by", "measures", "bound", "finding"}
FIRST_READING_KEYS = {"fit", "value", "verdict", "standing", "source"}


def test_the_templates_route_runs_no_stage_and_cannot(monkeypatch):
    """Rule D4, both forms: it ran nothing, and there is no runner in its path to run."""
    cold = Service(grid=SMALL).handle("/api/templates")
    assert cold.status == 200 and cold.stages == ()

    def refuse(*a, **kw):
        raise AssertionError("a metadata endpoint reached the runner (rule D4)")

    monkeypatch.setattr("galaxy.api.service._run", refuse)
    api = Service(grid=SMALL)
    assert api.handle("/api/templates").body == cold.body and api._cache == {}
    listed = {r["path"]: r for r in api.handle("/api").json()["routes"]}
    assert listed["/api/templates"]["params"] == []


def test_the_templates_route_has_the_stated_shape():
    api = Service(grid=SMALL)
    payload = api.handle("/api/templates").json()
    assert set(payload) == {"default", "templates"} and payload["default"] == "milky_way"
    assert [t["name"] for t in payload["templates"]] == ["milky_way", "ngc_4414"]
    registry = api.handle("/api/inputs").json()
    viewer_sets = set(json.loads((ROOT / "frontend/src/galaxy/filters.json").read_text(encoding="utf-8"))["sets"])
    viewer_sets |= set(json.loads((ROOT / "frontend/src/galaxy/instruments.json").read_text(encoding="utf-8"))["sets"])
    for t in payload["templates"]:
        assert set(t) == TEMPLATE_KEYS, t["name"]
        assert t["model"] in api.models and t["label"] and t["about"]
        # The inputs, fully resolved, in the shapes /api/inputs uses.
        assert set(t["inputs"]) == {"controls", "seeds", "mergers"}
        # (S58: a pin is not among the inputs' three shapes - /api/inputs offers none - and travels under "pins".)
        assert list(t["inputs"]["controls"]) == [c["name"] for c in registry["controls"]]
        assert list(t["inputs"]["seeds"]) == [s["name"] for s in registry["seeds"]]
        assert all(isinstance(v, float) for v in t["inputs"]["controls"].values())
        assert all(isinstance(v, int) for v in t["inputs"]["seeds"].values())
        for event in t["inputs"]["mergers"]:
            assert set(event) == {"time", "mass_ratio", "gas_fraction", "about"}
        assert list(t["camera"]) == ["inclination_deg", "azimuth_deg", "radius_kpc", "fov_deg"]
        assert all(isinstance(v, float) for v in t["camera"].values())
        assert t["filters"] in viewer_sets, "a template names a filter set the viewer holds"
        # S58 (D217 item 2): was `t["pins"] == []`.
        assert list(t["instrument"]) == ["distance_mpc", "pixel_scale_arcsec"]
        # S59 (D218 items 5-6): was one pin each; the second is a measured number.
        # S59 (D218): was {"name", "value", "source"} - a pin carries its input's label and unit (null for a class).
        # S60 (D219 items 3 and 8): was two pins each - a third: a named class carries ``classes``, the closed list
        # it is one of; a table's value is its columns, each a name and a unit, and its rows.
        assert [set(p) for p in t["pins"][:2]] == [{"name", "label", "unit", "value", "source"}] * 2 and t["pins"][0]["name"] == "bar_present"
        assert t["pins"][0]["unit"] is None and t["pins"][1]["unit"] == "deg" and all(p["label"] == INPUTS[p["name"]].label for p in t["pins"])
        assert (t["pins"][1]["name"], t["pins"][1]["value"]) == (("sun_bar_angle", 30.0) if t["name"] == "milky_way" else ("pitch_angle", 28.9))
        assert "[verified:" in t["pins"][1]["source"] and "D218" in t["pins"][1]["source"]
        assert t["pins"][0]["value"] is (t["name"] == "milky_way") and "[verified:" in t["pins"][0]["source"]
        third = t["pins"][2]
        assert third["unit"] is None and "[verified:" in third["source"] and "D219" in third["source"]
        if t["name"] == "milky_way":
            assert set(third) == {"name", "label", "unit", "value", "source"} and third["name"] == "arm_pieces"
            assert third["value"] == {
                "columns": [{"name": n, "unit": u} for n, u in INPUTS["arm_pieces"].columns],
                "rows": [list(row) for row in MW_ARMS],
            }
            assert [c["name"] for c in third["value"]["columns"]] == ["arm", "beta_from", "beta_to", "beta_kink", "radius_kink", "pitch_below", "pitch_above"]
            assert [c["unit"] for c in third["value"]["columns"]] == [None, "deg", "deg", "deg", "kpc", "deg", "deg"]
        else:
            assert set(third) == {"name", "label", "unit", "value", "source", "classes"} and (third["name"], third["value"]) == ("arm_class", "flocculent")
            assert third["classes"] == ["grand_design", "multi_armed", "flocculent"] == list(INPUTS["arm_class"].classes)
    mw, ngc = payload["templates"]
    assert mw["inputs"]["controls"] == {c["name"]: c["default"] for c in registry["controls"]}
    assert mw["inputs"]["seeds"] == {s["name"]: s["default"] for s in registry["seeds"]}
    assert mw["inputs"]["mergers"] == registry["events"][0]["default"]
    assert mw["fit"] is None and mw["checks"] == [] and mw["instrument"] == {"distance_mpc": None, "pixel_scale_arcsec": None}
    assert mw["camera"] == {"inclination_deg": 0.0, "azimuth_deg": 270.0, "radius_kpc": 20.0, "fov_deg": 45.0}
    assert ngc["inputs"]["mergers"] == [] and set(ngc["inputs"]["seeds"].values()) == {4414}
    assert ngc["camera"] == {"inclination_deg": 55.0, "azimuth_deg": 0.0, "radius_kpc": NGC_4414.camera.radius_kpc, "fov_deg": 5.0}
    assert ngc["instrument"] == {"distance_mpc": 17.7, "pixel_scale_arcsec": None}
    fit = ngc["fit"]
    assert set(fit) == FIT_KEYS and [t["name"] for t in fit["targets"]] == ["curve_peak", "disc_scale_length", "stellar_mass"]
    for target in fit["targets"]:
        assert set(target) == TARGET_KEYS
        lo, hi = target["window"]
        assert target["half_window"] == pytest.approx((hi - lo) / 2.0)
        assert target["residual"] == pytest.approx((target["model"] - target["value"]) / target["half_window"], rel=1e-12)
    assert [c["name"] for c in fit["controls"]] == list(ngc["inputs"]["controls"])
    for c, r in zip(fit["controls"], registry["controls"]):
        assert set(c) == CONTROL_KEYS
        assert (c["default"], c["lo"], c["hi"]) == (r["default"], r["lo"], r["hi"])
        assert c["fitted"] == ngc["inputs"]["controls"][c["name"]] and c["lo"] <= c["fitted"] <= c["hi"]
        # Free with the target that measures it, or held at the registry's default; a bound is flagged with its finding.
        assert c["free"] == (c["name"] in FREE) and c["measured_by"] == FREE.get(c["name"])
        assert (c["measures"] is not None) == c["free"]
        assert c["free"] or c["fitted"] == c["default"]
        assert c["bound"] == (c["fitted"] in (c["lo"], c["hi"])) == (c["finding"] is not None)
    assert [c["name"] for c in fit["controls"] if c["bound"]] == ["halo_assembly_z"]
    assert "debt #132" in next(c["finding"] for c in fit["controls"] if c["bound"])
    assert isinstance(fit["objective"], str) and "half-window" in fit["objective"] and "0.001" in fit["objective"]
    assert fit["tool"] == "tools/fit_template.py ngc_4414" and (ROOT / "tools" / "fit_template.py").is_file()
    # The checks: the windows only. No model number of the template as it stands rides with one - those verdicts
    # are the specs' report - but its standing does, and the record of its first reading on the withdrawn fit.
    assert [c["name"] for c in ngc["checks"]] == ["curve_shape", "star_formation_rate", "hydrogen_mass",
                                                 "absolute_magnitude_k", "colour_b_v_face_on"]
    for c in ngc["checks"]:
        assert set(c) == CHECK_KEYS and len(c["window"]) == 2 and c["window"][0] < c["window"][1]
        assert c["standing"] == "disclosed" and "fit A" in c["standing_about"] and "never blind" in c["standing_about"]
        first = c["first_reading"]
        assert set(first) == FIRST_READING_KEYS and (first["fit"], first["standing"]) == ("fit A", "blind")
        assert first["verdict"] == ("pass" if c["window"][0] <= first["value"] <= c["window"][1] else "fail")
    assert set(ngc["sources"]) == set(templates.numbers(NGC_4414))
    # The route's about states the shape: every key of a template, of a fit and of a check is named in it.
    about = next(r.about for r in routes() if r.path == "/api/templates")
    for key in (TEMPLATE_KEYS | FIT_KEYS | CHECK_KEYS | TARGET_KEYS | CONTROL_KEYS | FIRST_READING_KEYS
                | {"default", "templates", "controls", "seeds", "mergers"}):
        assert re.search(rf"\b{key}\b", about), f"the route's about does not name {key}"
    assert "Runs no stage" in about


def test_the_templates_route_publishes_no_model_internals():
    """Rule D5: no constant's name, whatever a source string quotes."""
    body = Service(grid=SMALL).handle("/api/templates").body.decode("utf-8")
    for name in LEVEL0:
        assert not re.search(rf"\b{name}\b", body), f"constant {name} is published"


def test_the_route_has_a_timing_row_and_a_templated_request_has_one():
    from timings import ENDPOINTS

    assert any(e.route == "/api/templates" and not e.query for e in ENDPOINTS)
    assert any("template=ngc_4414" in e.query for e in ENDPOINTS)


# --- the fit ---------------------------------------------------------------------------------


def test_the_objective_is_d213_s():
    """Squared residuals in half-windows, plus 1e-3 times the free controls' squared departures in units of each
    one's range: a tie-breaker among the free controls and nothing else (D213 as amended, ruling 1)."""
    assert NGC_4414.fit.tiebreak == 1e-3
    p = fit_template.Problem(NGC_4414, SMALL)
    # The free set is the template's, in the registry's order; the rest are held and are not the search's.
    assert [c.name for c in p.controls] == list(FREE) == [c.name for c in controls() if c.name in FREE]
    assert [c.name for c in p.held] == list(HELD) and p.weight == 1e-3
    # The fit holds the template's seeds and its merger list.
    # S58 (D217 follow-up): was {**NGC_4414.seeds, "mergers": ()} - and its pins: the tool ran a template without
    # them. No target's field is downstream of the bar (the fields below), so no target's number and no fit moves.
    # S59 (D218 item 6): was without the pitch. S60 (D219 item 3): and without the arm class.
    assert p.fixed == {**NGC_4414.seeds, "mergers": (), **NGC_PINS}
    assert p.fixed == {k: v for k, v in templates.overrides(NGC_4414).items() if k not in NGC_4414.controls}
    assert p.fields == ("circular_velocity", "thin_disc_scale_length", "stellar_mass_total")
    # A departure is counted in the control's own linear range, whatever coordinate the search moves in.
    values = {c.name: c.default for c in controls()} | {"disc_spin": 0.0173 + 0.0045, "halo_mass": 1.1e12 + 9.9e11}
    s = p.s_of(values)
    assert s.shape == (4,)
    assert p.departures(s) == pytest.approx([0.1, 0.1, 0, 0], abs=1e-12)
    assert p.departures(p.s0) == pytest.approx(np.zeros(4), abs=1e-15)
    r = np.array([0.5, -2.0, 1.0])
    assert p.parts(r, s) == pytest.approx((0.25 + 4.0 + 1.0, 1e-3 * 0.02))
    assert p.objective(r, s) == pytest.approx(5.25002)
    assert p.values(s) == pytest.approx({n: values[n] for n in FREE}, rel=1e-12)
    # The search's coordinates: the logarithm where a range starts above zero - all four of the free ones.
    assert p.log.all()
    assert p.values(np.zeros(4)) == {c.name: c.lo for c in controls() if c.name in FREE}
    assert p.values(np.ones(4)) == {c.name: c.hi for c in controls() if c.name in FREE}
    assert p.s_of({c.name: math.sqrt(c.lo * c.hi) for c in controls() if c.name in FREE}) == pytest.approx(np.full(4, 0.5))
    step = 1e-6
    slopes = (p.departures(p.s0 + step) - p.departures(p.s0 - step)) / (2 * step)
    assert p.departure_slopes(p.s0) == pytest.approx(slopes, rel=1e-8)
    # A residual is counted in half-windows of the reader's window, about the reader's value.
    peak, length, mass = NGC_4414.fit.targets
    assert (peak.value, peak.window, peak.half_window) == (237.0, (222.0, 247.0), 12.5)
    assert (length.value, length.window) == (1.649, (1.5, 1.9)) and length.half_window == pytest.approx(0.2)
    assert mass.value == pytest.approx(10**10.65) and mass.window == (3.4e10, 5.9e10) and mass.half_window == 1.25e10
    assert peak.residual_of(249.5) == 1.0 and peak.holds(247.0) and not peak.holds(247.01)
    assert (peak.inside_kpc, peak.statistic, peak.field) == (20.6, "curve_peak", "circular_velocity")
    # The words say what the last term is, and no more.
    assert "breaks ties among the free controls and does nothing else" in NGC_4414.fit.objective
    assert "the four free controls" in NGC_4414.fit.objective and "keeps a control" not in NGC_4414.fit.objective


def test_the_tool_moves_the_free_controls_and_never_passes_a_held_one():
    """The model is handed the template's seeds, its merger list, its pins (S58, D217) and the four free controls:
    a held control is not among the inputs of any evaluation, so it is the registry's default by construction."""
    from dataclasses import replace

    p = fit_template.Problem(NGC_4414, SMALL)
    seen = []
    real = p._run

    def spy(model, inputs, *a, **kw):
        seen.append(dict(inputs))
        return real(model, inputs, *a, **kw)

    p._run = spy
    J, probes = p.jacobian(p.s0.copy(), p.residuals_of(p.model_numbers(p.s0)), 0.02)
    assert J.shape == (3, 4) and len(probes) == 8 and len(seen) == 9
    for inputs in seen:
        # S58 (D217 follow-up): was without "bar_present" - a template's run carries its pin, the tool's too.
        # S59 (D218 item 6): was without "pitch_angle". S60 (D219 item 3): was without "arm_class".
        assert set(inputs) == set(FREE) | {s.name for s in seeds()} | {"mergers", *NGC_PINS} and inputs["bar_present"] is False
        assert not set(inputs) & set(HELD)
    # No argument of the tool admits a control: the free set is read from the template's data and nowhere else.
    assert set(inspect.signature(fit_template.fit).parameters) == {"template", "grid", "start", "iterations"}
    assert set(inspect.signature(fit_template.Problem.__init__).parameters) == {"self", "template", "grid"}
    source = inspect.getsource(fit_template.main)
    assert source.count("add_argument") == 2 and '"--check"' in source
    # A template that names fewer free controls is fitted in fewer; one that names a stranger is refused.
    fewer = replace(NGC_4414, fit=replace(NGC_4414.fit, free={"disc_spin": "disc_scale_length"},
                                          measures={"disc_spin": "the scale length"}, bounds={}))
    assert [c.name for c in fit_template.Problem(fewer, SMALL).controls] == ["disc_spin"]
    stranger = replace(NGC_4414, fit=replace(NGC_4414.fit, free={"bar_strength": "curve_peak"},
                                             measures={"bar_strength": "x"}, bounds={}))
    with pytest.raises(SystemExit, match="not controls of its model"):
        fit_template.Problem(stranger, SMALL)


def test_the_search_s_counts_are_fixed_in_advance():
    assert (fit_template.ITERATIONS, fit_template.FD_STEPS, fit_template.DAMPING) == (24, (4e-2, 2e-2, 1e-2), (0.0, 0.1, 1.0, 10.0))
    assert NGC_4414.fit.evaluations == 1 + 24 * (2 * 4 + 4) == 289
    assert NGC_4414.fit.method == fit_template.METHOD  # the template states the method the tool states
    assert NGC_4414.fit.date == "2026-10-04"
    # Ruling 4: what the search leaves is a point on a plateau resolved to the step, and the words say so.
    for words in (NGC_4414.fit.method, NGC_4414.fit.objective):
        assert "plateau" in words and "not a minimum to the printed precision" in words and "0.01 half-windows" in words
    assert "a few 1e-4 of a range in the controls" in NGC_4414.fit.method


def test_a_bounded_step_stays_inside_the_ranges_and_solves_the_free_controls():
    normal = np.array([[4.0, 1.0, 0.0], [1.0, 3.0, 0.0], [0.0, 0.0, 2.0]])
    rhs = np.array([1.0, -6.0, 0.4])
    s = np.array([0.5, 0.2, 0.5])
    plain = np.linalg.solve(normal, rhs)
    assert s[1] + plain[1] < 0.0 and s[0] + plain[0] > 1.0  # the unbounded step carries two controls out of range
    step = fit_template.bounded_step(normal, rhs, s, 0.0)
    assert s[1] + step[1] == 0.0 and np.all((s + step >= 0.0) & (s + step <= 1.0))
    # The second reaches its bound first and is held there; the first, solved again with it held, stays inside
    # its range - a clipped step would have pinned it on its bound too.
    assert step[0] == pytest.approx((rhs[0] - normal[0, 1] * step[1]) / normal[0, 0]) and s[0] + step[0] == pytest.approx(0.8)
    assert step[2] == pytest.approx(0.2)
    inside = np.array([0.4, 0.3, 0.2])
    assert fit_template.bounded_step(normal, inside, s, 0.0) == pytest.approx(np.linalg.solve(normal, inside))
    damped = fit_template.bounded_step(normal, inside, s, 10.0)
    assert np.all(np.abs(damped) < np.abs(np.linalg.solve(normal, inside)))
    # A control standing on its bound with the step pointing outwards does not move, and the rest are solved.
    on_bound = fit_template.bounded_step(normal, rhs, np.array([0.5, 0.0, 0.5]), 0.0)
    assert on_bound[1] == 0.0 and on_bound[0] == pytest.approx(0.25)


def test_the_committed_fit_is_where_the_search_stops_and_reproduces_its_numbers():
    """The committed controls on the production grid: the model's three numbers there are the committed ones,
    and one more cycle of the search from them - the targets differenced at each of the three widths, twelve
    damped trial steps, 37 model evaluations - finds nothing lower. A point on a plateau resolved to the
    model's steps, which is all the search claims."""
    here = fit_template.at(NGC_4414)
    assert here.evaluations == 1
    assert here.controls == pytest.approx(dict(NGC_4414.controls), rel=1e-12) and set(here.controls) == set(FREE)
    for target in NGC_4414.fit.targets:
        assert here.model[target.name] == pytest.approx(target.model, rel=1e-9), target.name
        assert here.residuals[target.name] == pytest.approx(target.residual, rel=1e-7, abs=1e-9), target.name
        assert target.residual == pytest.approx(target.residual_of(target.model), rel=1e-12)
        assert target.holds(target.model)  # S54: every target inside its window, none on its value
    assert here.objective == pytest.approx(NGC_4414.fit.objective_value, rel=1e-9)
    assert here.objective == pytest.approx(here.misfit + here.tiebreak) and here.tiebreak == pytest.approx(1.73e-4, rel=5e-3)
    assert f"{NGC_4414.fit.objective_value:.4f}" in NGC_4414.fit.objective  # the words carry the number
    cycle = fit_template.fit(NGC_4414, start=templates.resolve(NGC_4414), iterations=len(fit_template.FD_STEPS))
    assert cycle.evaluations == 1 + 3 * (2 * 4 + 4)
    assert cycle.objective == here.objective and cycle.controls == here.controls
    assert cycle.history == (here.objective,) * 3
    # The held controls did not move by any amount: the galaxy the fit was read on has the registry's own.
    resolved = templates.resolve(NGC_4414)
    assert all(resolved[name] is INPUTS[name].default for name in HELD)


@pytest.mark.skipif(os.environ.get("GALAXYGEN_REFIT") != "1", reason="the whole search is forty seconds: GALAXYGEN_REFIT=1 runs it")
def test_the_fit_re_run_from_the_defaults_lands_on_the_committed_values():
    """The whole search again (289 model evaluations): deterministic, so the same answer."""
    result = fit_template.fit(NGC_4414)
    assert result.evaluations == NGC_4414.fit.evaluations
    assert result.controls == pytest.approx(dict(NGC_4414.controls), rel=1e-9)
    assert result.objective == pytest.approx(NGC_4414.fit.objective_value, rel=1e-9)
    assert result.history[-1] == result.history[-3]  # it had stopped moving before the last cycle ended
    text_out = fit_template.tables(NGC_4414, result)
    for word in ("residuals", "controls", "half-window", "moved / range", "objective"):
        assert word in text_out


def test_the_tool_prints_the_two_tables_for_the_committed_fit():
    """The residuals table and the controls table: each free control with the target that measures it, each held
    one as held, the bound labelled with its finding beside it, and the plateau stated."""
    here = fit_template.at(NGC_4414)
    out = fit_template.tables(NGC_4414, here)
    lines = out.splitlines()
    assert "residuals" in out and "moved / range" in out and "half-window" in out
    assert sum(line.endswith("  inside") for line in lines) == 3 and "OUTSIDE" not in out
    assert sum("held at the registry's default" in line for line in lines) == 3
    for name in HELD:
        row = next(line for line in lines if line.strip().startswith(name))
        assert row.endswith("held at the registry's default") and "+0.00000" in row and "bound" not in row
    for name, target in FREE.items():
        row = next(line for line in lines if line.strip().startswith(name))
        assert "free: " in row and NGC_4414.fit.measures[name] in row
        assert ("bound; free:" in row) == (name == "halo_assembly_z")
    finding = next(line for line in lines if line.strip().startswith("bound: "))
    assert "halo_assembly_z = 0.5 is the lower bound of its range, a finding and not a fit" in finding
    assert "the model cannot lower its inner peak enough for this disc inside the range" in finding and "debt #132" in finding
    assert "a point on a plateau" in out and "not a minimum to the printed precision" in out
    assert f"objective {NGC_4414.fit.objective_value:.6f}" in out
    paste = fit_template.literals(NGC_4414, here)
    assert all(f'"{name}": ' in paste for name in FREE) and not any(f'"{name}": ' in paste for name in HELD)
    assert repr(NGC_4414.fit.targets[0].model)[:12] in paste


def test_the_model_s_targets_are_stepped_in_halo_mass_and_disc_spin():
    """Debt #133, the finding the search's differencing widths answer (S54): along disc_spin, from the registry's defaults
    with this template's seeds and no merger, the stellar mass falls smoothly by about 6.7e5 Msun per 2.5e-4 of
    the range, and at one place between two such points it falls by 1.7e8 - a step of 0.014 half-windows. A
    derivative taken across it reads the step, not the trend, and what the fit leaves is a point on a plateau
    resolved to this step, not a minimum (D213 as amended, ruling 4)."""
    p = fit_template.Problem(NGC_4414)
    table = {c.name: c for c in controls()}
    spin = table["disc_spin"]
    mass = []
    for k in range(-6, 3):
        values = {c.name: c.default for c in controls()} | {"disc_spin": spin.default + k * 2.5e-4 * (spin.hi - spin.lo)}
        mass.append(p.model_numbers(p.s_of(values))[2])
    drops = -np.diff(mass)
    assert np.median(drops) == pytest.approx(6.7e5, rel=0.05)
    assert drops.max() == pytest.approx(1.71e8, rel=0.05) and drops.max() > 100 * np.median(drops)
    assert drops.max() / NGC_4414.fit.targets[2].half_window == pytest.approx(0.0137, abs=5e-4)


# --- the checks' definitions -----------------------------------------------------------------


def test_the_shape_number_on_a_curve_of_known_ratio():
    """S = mean speed from 20.6 kpc to the grid's edge over the maximum inside 20.6 kpc."""
    R = (np.arange(400) + 0.5) * 0.075
    speed = np.where(R < 20.6, 200.0, 150.0)
    speed[40] = 250.0  # the peak, at 3.04 kpc
    assert templates.curve_peak(speed, R, 20.6) == 250.0
    assert templates.curve_shape(speed, R, 20.6) == pytest.approx(0.6, rel=1e-15)
    # A faster ring beyond 20.6 kpc is not the peak: it raises the outer mean, never the denominator.
    speed[390] = 400.0
    assert templates.curve_peak(speed, R, 20.6) == 250.0
    assert templates.curve_shape(speed, R, 20.6) == pytest.approx((150.0 * 124 + 400.0) / 125 / 250.0)
    assert int((R >= 20.6).sum()) == 125 and R[R >= 20.6][0] == pytest.approx(20.6625)
    # A flat curve is S = 1, and one that falls by a fifth is inside the window.
    assert templates.curve_shape(np.full(400, 220.0), R, 20.6) == 1.0
    shape = next(c for c in NGC_4414.checks if c.name == "curve_shape")
    assert shape.holds(templates.curve_shape(np.where(R < 20.6, 237.0, 185.0), R, 20.6)) and not shape.holds(1.0)
    assert templates.measure("curve_shape", speed, R, 20.6) == templates.curve_shape(speed, R, 20.6)
    assert templates.measure("scalar", np.float64(3.5)) == 3.5
    with pytest.raises(templates.TemplateError):
        templates.measure("face_on_colour", speed, R, 20.6)


def test_each_check_names_a_published_field_in_its_unit(prod):
    """The hydrogen field named exists, and so does every other; a scalar check is in its field's own unit."""
    models, impls, _ = prod
    model = models.get(NGC_4414.model)
    declared = {d.name: d for sid in model.stage_map.values() for d in impls.get(sid).publishes}
    by_name = {c.name: c for c in NGC_4414.checks}
    assert by_name["hydrogen_mass"].field == "hydrogen_mass_30kpc" and "hydrogen_mass_30kpc" in declared
    assert {c.field for c in NGC_4414.checks} == {"circular_velocity", "sfr", "hydrogen_mass_30kpc", "absolute_magnitude_k", None}
    for c in NGC_4414.checks:
        if c.field is None:
            assert c.statistic == "face_on_colour"
            continue
        assert c.field in declared, c.name
        if c.statistic == "scalar":
            assert declared[c.field].unit == c.unit and declared[c.field].kind.domain == "galaxy", c.name
    for t in NGC_4414.fit.targets:
        assert t.field in declared and (t.statistic != "scalar" or declared[t.field].unit == t.unit), t.name
    assert declared["circular_velocity"].unit == "km/s" and declared["circular_velocity"].axes == ("R",)
    # The fit never sees a check: no check reads a field the fit is given, but the curve, by another statistic.
    fitted = {(t.field, t.statistic) for t in NGC_4414.fit.targets}
    assert not fitted & {(c.field, c.statistic) for c in NGC_4414.checks}


def _reading_windows() -> dict[int, tuple[float, float]]:
    """The summary table's windows, by row number: the bold ``[lo, hi]`` of the "Window at 17.7 Mpc" column."""
    powers = {"×10¹⁰": 1e10, "×10⁹": 1e9}
    out: dict[int, tuple[float, float]] = {}
    for line in text("READING_NGC_4414.md").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 7 or not cells[1].isdigit():
            continue
        found = re.search(r"\*\*\[([^\],]+), ([^\]]+)\]\s*(×10\S+)?", cells[5])
        if found:
            scale = powers.get(found.group(3) or "", 1.0)
            out[int(cells[1])] = tuple(float(v.replace("−", "-")) * scale for v in found.group(1, 2))
    return out


def test_each_window_is_the_reading_s():
    """Every window the template states is a row of READING_NGC_4414.md's summary table, fixed before any model
    output for this galaxy existed (D113); none is widened here."""
    rows = _reading_windows()
    assert len(rows) >= 13
    targets = {t.name: t for t in NGC_4414.fit.targets}
    by_name = {c.name: c for c in NGC_4414.checks}
    assert targets["curve_peak"].window == rows[4] == (222.0, 247.0)
    assert targets["disc_scale_length"].window == rows[7] == (1.5, 1.9)
    assert targets["stellar_mass"].window == pytest.approx(rows[8]) and rows[8] == pytest.approx((3.4e10, 5.9e10))
    assert by_name["curve_shape"].window == rows[6] == (0.71, 0.86)
    assert by_name["star_formation_rate"].window == rows[11] == (1.8, 4.7)
    assert by_name["absolute_magnitude_k"].window == rows[12] == (-24.62, -24.12)
    assert by_name["colour_b_v_face_on"].window == rows[14] == (0.72, 0.82)
    # Hydrogen is the atomic and the molecular windows summed edge to edge (the reading's W-G: "range [7.4, 14.7]").
    assert by_name["hydrogen_mass"].window == pytest.approx((rows[9][0] + rows[10][0], rows[9][1] + rows[10][1]))
    assert by_name["hydrogen_mass"].window == (7.4e9, 14.7e9)
    assert "Total hydrogen (W-F + W-G centres): 4.46 + 6.03 = 10.5e9, range [7.4, 14.7]" in text("READING_NGC_4414.md")
    # 20.6 kpc is the inner disc's edge, 240 arcsec at 17.7 Mpc.
    assert 240.0 * 17.7e3 * math.radians(1.0 / 3600.0) == pytest.approx(templates.NGC_4414_INNER_DISC_KPC, abs=0.01)
    for name in (*targets, *by_name):
        assert {**targets, **by_name}[name].inside_kpc in (None, 20.6)


def test_the_checks_are_d213_s_table_word_for_word():
    """Label, window, the model's quantity and what still differs: the ruling's own row for each check."""
    decision = text("DECISIONS.md").split("### D213.")[1]
    rows = [[c.strip().replace("`", "") for c in line.strip().strip("|").split("|")]
            for line in decision.splitlines() if line.strip().startswith("| ") and "---" not in line]
    # The ruling's table is the four-column one whose rows open with a check's label; the entry's later tables
    # (the fits' controls, the readings) are other tables, some of them four columns wide too.
    labels = {c.label for c in NGC_4414.checks}
    table = {r[0]: r for r in rows if len(r) == 4 and r[0] in labels}
    assert len(table) == 5 and len(NGC_4414.checks) == 5
    for check in NGC_4414.checks:
        label, window, quantity, mismatch = table[check.label]
        assert check.quantity == quantity and check.mismatch == mismatch, check.name
        lo, hi = (float(v.replace("−", "-")) for v in re.match(r"\[([^,]+), ([^\]]+)\]", window).groups())
        scale = 1e9 if "10⁹" in window else 1.0
        assert check.window == pytest.approx((lo * scale, hi * scale)), check.name
    # ... and the three targets are the ruling's, with its fields and windows.
    ruling = decision.replace("`", "")
    for words in ("max circular_velocity inside 20.6 kpc, 237 ± 10 km/s [222, 247]", "thin_disc_scale_length, 1.649 kpc [1.5, 1.9]",
                  "stellar_mass_total, 10^10.65 M☉\n   [3.4, 5.9] × 10¹⁰"):
        assert words in ruling, words


# --- both templates run ----------------------------------------------------------------------


@pytest.mark.parametrize("name", templates.names())
def test_a_template_runs_end_to_end_on_a_small_grid(prod, name):
    """Every stage of the template's model, on its inputs: NGC 4414's list of no mergers and its seeds included."""
    template = templates.get(name)
    model = prod[0].get(template.model)
    out = run(model, templates.resolve(template), SMALL)
    assert out.ran == out.order and len(out.ran) == len(model.stages)
    assert out.inputs == templates.resolve(template)
    for field in ("stellar_mass_total", "sfr", "hydrogen_mass_30kpc", "absolute_magnitude_k", "thin_disc_scale_length"):
        assert np.isfinite(out.fields[field]) and field in out.decls, field
    assert np.all(np.isfinite(out.fields["circular_velocity"])) and out.fields["catalogue_size"] > 0
    if template.mergers == ():
        assert out.fields["last_major_merger_time"] == 0.0


@pytest.mark.parametrize("route, query", [
    ("/api/region", SECTOR),
    ("/api/system", "cell=300&index=0"),
    ("/api/clouds", SECTOR),
    ("/api/clusters", SECTOR),
    ("/api/remnants", SECTOR),
    ("/api/bright", SECTOR + "&n=50"),
    ("/api/render", "filters=" + B_V),
])
def test_every_route_answers_for_ngc_4414(route, query):
    api = Service(grid=SMALL)
    got = api.handle(route, "template=ngc_4414&" + query)
    assert got.status == 200, got.body[:300]
    header, _ = wire.decode(got.body)
    assert header["inputs"]["mergers"] == [] and header["inputs"]["world_seed"] == 4414
    assert header["inputs"]["halo_mass"] == NGC_4414.controls["halo_mass"]


# --- the checks' report ------------------------------------------------------------------------


def test_the_checks_are_judged_on_the_template_s_own_run():
    """On a small grid, for speed: five results for NGC 4414, none for the Milky Way, each a number against its window."""
    api = Service(grid=SMALL)
    results = checks.evaluate(service=api)
    assert list(results) == ["milky_way", "ngc_4414"] and results["milky_way"] == []
    judged = results["ngc_4414"]
    assert [r.name for r in judged] == [c.name for c in NGC_4414.checks]
    for r, c in zip(judged, NGC_4414.checks):
        assert r.status in ("pass", "fail") and math.isfinite(r.value)
        assert (r.status == "pass") == c.holds(r.value)
        assert f"{r.value:.6g}" in r.reason and ("not in" in r.reason) == (r.status == "fail")
        assert r.standing == "disclosed" and r.first is c.first_reading  # the standing and fit A's reading ride along
    # Each number is the template's own galaxy's, read as the definition says - and, since S55 (D214, invariant
    # I3), on the layer-off run, as the acceptance rows are: the four field checks are the same bits either way,
    # and the frame's colour moves in its fourteenth decimal with the placement (so the render below is asked off).
    assert checks.JUDGED_LAYER is False and checks.JUDGED_SETTING == "off"
    out, _ = api.compute(api.models.get(NGC_4414.model), templates.overrides(NGC_4414),
                         ("circular_velocity", "sfr", "hydrogen_mass_30kpc", "absolute_magnitude_k"), layer=False)
    by_name = {r.name: r.value for r in judged}
    assert by_name["curve_shape"] == templates.curve_shape(out.fields["circular_velocity"], out.grid.R, 20.6)
    assert by_name["star_formation_rate"] == out.fields["sfr"]
    assert by_name["hydrogen_mass"] == out.fields["hydrogen_mass_30kpc"]
    assert by_name["absolute_magnitude_k"] == out.fields["absolute_magnitude_k"]
    # The colour is the frame's through its dust, not its stars' alone. (Which way the dust moves it is the
    # galaxy's: reddening against scattered light. On this grid this template's frame is bluer through its dust.)
    got = api.handle("/api/render", {"template": ["ngc_4414"], "layer": ["off"], "filters": [json.dumps(
        [spectra.band_curve(b).json() for b in checks.FACE_ON_BANDS])]})
    header, arrays = got.frame()
    assert by_name["colour_b_v_face_on"] == checks.face_on_colour(header, arrays)
    bare = checks.frame_total(header, arrays)
    assert by_name["colour_b_v_face_on"] != float(checks.band_magnitude(bare[0], "B") - checks.band_magnitude(bare[1], "V"))


def test_the_colour_check_s_computation_is_the_render_gate_s_record():
    """One computation, two readers: on the default galaxy it is tests/test_render.py's pinned face-on frame."""
    import test_render

    assert test_render.face_on is checks.face_on and test_render.frame_total is checks.frame_total
    assert test_render.band_magnitude is checks.band_magnitude and test_render.cell_areas is checks.cell_areas
    value, why = checks._frame_colour(MILKY_WAY, Service())
    assert why == "" and value == pytest.approx(test_render.FACE_ON_B_V[DEFAULT_MODEL], abs=2e-6)


def _result(name: str, status: str, value: float = 1.0) -> checks.Result:
    return checks.Result("ngc_4414", name, name, status, f"{value} somewhere", value)


def test_a_check_s_miss_is_recorded_or_it_fails_the_run():
    """The acceptance table's convention (spec.MISSES): an unrecorded miss fails the run, a recorded one does not
    and still prints fail, and a recorded miss that starts passing fails it."""
    results = {"milky_way": [], "ngc_4414": [_result("curve_shape", "fail"), _result("hydrogen_mass", "pass"),
                                             _result("colour_b_v_face_on", "not-yet-computable")]}
    unrecorded = checks.problems(results, {})
    assert [p.code for p in unrecorded] == ["template-check"] and isinstance(unrecorded[0], Problem)
    assert "curve_shape" in unrecorded[0].detail and "not a recorded miss" in unrecorded[0].detail
    miss = checks.CheckMiss(debt=132, since="S54", reason="the halo holds the curve flat")
    assert checks.problems(results, {"ngc_4414": {"curve_shape": miss}}) == []
    stale = checks.problems(results, {"ngc_4414": {"curve_shape": miss, "hydrogen_mass": miss}})
    assert [p.code for p in stale] == ["stale-check-miss"] and "now passes" in stale[0].detail and "#132" in stale[0].detail
    unknown = checks.problems(results, {"ngc_4414": {"curve_shape": miss, "bar_length": miss}, "andromeda": {}})
    assert sorted(p.code for p in unknown) == ["unknown-check-miss", "unknown-check-miss"]
    with pytest.raises(ValueError):
        checks.CheckMiss(debt=0, since="S54", reason="x")
    with pytest.raises(ValueError):
        checks.CheckMiss(debt=132, since="S54", reason=" ")
    # The report: its own table, headed so nobody reads it as acceptance rows.
    report = checks.report(results, {"ngc_4414": {"curve_shape": miss}})
    lines = report.splitlines()
    assert lines[0] == "template checks" and "NOT acceptance rows" in lines[1] and "never counted in it" in lines[2]
    assert "template milky_way (Milky Way): states no checks" in report
    assert "template ngc_4414 (NGC 4414), model azimuthal: 1 pass, 1 fail, 1 not-yet-computable of 3 checks (1 of the failures recorded as misses)" in report
    assert "[recorded miss, debt #132, since S54]" in report and "FAIL" not in report
    assert "FAIL [ngc_4414] template-check" in checks.report(results, {})
    assert checks.summary(results["ngc_4414"]) == {"pass": 1, "fail": 1, "not-yet-computable": 1}


def test_every_verdict_on_the_fit_that_stands_is_disclosed_and_fit_a_s_reading_is_kept():
    """D213 as amended, ruling 2: the five were read once, blind, on fit A; the refit was decided after four of
    them were read, so no verdict on it is blind. Fit A's values and verdicts stay as data beside the checks,
    and they are the decision record's own table."""
    decision = text("DECISIONS.md").split("### D213.")[1]
    assert "**The first reading: fit A" in decision and "All five checks on fit B are **disclosed**" in decision
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in decision.splitlines() if line.startswith("| ")]
    recorded = {r[0]: r for r in rows if len(r) == 5 and r[3].startswith(("miss", "pass"))}
    assert len(recorded) == 5
    names = {"curve_shape": "Curve shape S", "star_formation_rate": "Star formation rate", "hydrogen_mass": "Hydrogen",
             "absolute_magnitude_k": "M_K", "colour_b_v_face_on": "B − V, face-on through dust"}
    for check in NGC_4414.checks:
        assert check.standing == "disclosed"
        assert "decided after four of the five checks had been read on fit A" in check.standing_about
        first = check.first_reading
        assert (first.fit, first.standing) == ("fit A", "blind") and "DECISIONS.md D213" in first.source
        row = recorded[names[check.name]]
        scale = 1e9 if check.name == "hydrogen_mass" else 1.0
        digits = 2 if check.name in ("hydrogen_mass", "absolute_magnitude_k") else 3
        assert round(first.value / scale, digits) == float(row[2].replace("−", "-")), check.name
        assert first.verdict == ("pass" if row[3].startswith("pass") else "fail") == ("pass" if check.holds(first.value) else "fail")
    assert [c.first_reading.verdict for c in NGC_4414.checks] == ["fail", "fail", "fail", "fail", "pass"]
    # The data refuses a check that was read once and calls its next verdict blind, and a verdict that is not its value's.
    from dataclasses import replace

    with pytest.raises(templates.TemplateError, match="disclosed on any later fit"):
        replace(NGC_4414.checks[0], standing="blind", standing_about="")
    with pytest.raises(templates.TemplateError, match="says why"):
        replace(NGC_4414.checks[0], standing_about="")
    with pytest.raises(templates.TemplateError, match="not its value against the window"):
        replace(NGC_4414.checks[0], first_reading=replace(NGC_4414.checks[0].first_reading, verdict="pass"))
    # The report prints the word in each row, and fit A's reading beside the new one.
    judged = [checks.judge(NGC_4414, c, c.window[0] - 1.0) for c in NGC_4414.checks]
    report = checks.report({"ngc_4414": judged}, {})
    assert "A verdict marked disclosed" in report and "it is not" in report and "blind. That first reading" in report
    for c in NGC_4414.checks:
        row = next(line for line in report.splitlines() if line.strip().startswith(c.name + " "))
        assert " disclosed " in row and " blind " not in row.split("first reading")[0]
        assert f"first reading (fit A, blind): {c.first_reading.value:.6g}, {c.first_reading.verdict}" in row


def test_the_ledger_names_only_checks_a_template_states():
    for name, entries in checks.CHECK_MISSES.items():
        stated = {c.name for c in templates.get(name).checks}
        assert set(entries) <= stated, name
        assert all(isinstance(m, checks.CheckMiss) for m in entries.values())


def test_the_specs_print_the_checks_after_the_acceptance_table_and_never_among_its_rows():
    from galaxy.specs import __main__ as entry
    from galaxy.specs import spec

    source = inspect.getsource(entry.main)
    assert source.index("spec.report(") < source.index("templates.report(") < source.index("convergence.report(")
    assert "bad |= bool(templates.problems(template_results))" in source
    assert len(spec.QUANTITIES) == 37  # the checks added no row
    assert not {c.name for c in NGC_4414.checks} & {q.name for q in spec.QUANTITIES}
