"""The separation (S55, BUILD_III Phase R; DECISIONS.md D214): the physics model beside the randomness layer.

Phase R is a behaviour-preserving restructure. What this file holds, in the order BUILD_III section 1d states it:

- **Behaviour preserved.** With the layer on, every field of both models on the production grid and every array of
  every input route's body is bit-identical to the reference captured at S54's state, before any of Phase R's
  model code moved (``tests/layer_reference.py``, ``tests/layer_reference_s54.json``).
- **I1.** With the layer off the model runs, and every field without a phi axis and every scalar that is not a
  census statistic is bit-identical to the layer-on run. The census statistics are a closed list, here.
- **I2.** A census's expected count per ring is the same with the layer on or off; only placements differ.
- **I3.** The acceptance table and the templates' checks are judged on the layer-off run, and no row names a
  synthetic or a composed field.
- **I4.** No physics stage requires a composed or a synthetic field: the graph refuses one that is not a declared
  placement reader, a composing stage or a layer stage, and ``compose`` refuses it again at run time.
- **I5 (the API's half).** Every route that takes inputs takes ``layer=off``; on and off never share a cache entry;
  any other value is a 400; the header echoes the setting.
- **The oracle.** Layer-off ``azimuthal`` equals layer-off ``basic`` on every field they share.
- **Appendix B applied.** The four cloud columns are the layer's, synthetic, the bits they were with the layer on and
  zero with it off; ``texture_seed`` is the fifth seed and no stage reads it yet.
- **One reader of the switch.** No module of the model but ``galaxy/layer/compose.py`` branches on the setting, and
  none calls ``.from_fields(``.

A *composed* field is identified in data: it has a phi axis (``FieldDecl.composed``). There is no list of them here.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import layer_reference
from galaxy import templates
from galaxy.api import wire
from galaxy.api.service import RESERVED, ROUTES, Service
from galaxy.core.fielddoc import PROVENANCE, SYNTHETIC_DECLARATIONS, DeclarationError, FieldDecl, Kind, Ramp
from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, production, seeds
from galaxy.core.stage import Fields, LayerError, UndeclaredAccess
from galaxy.layer import cloud_texture, compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import RunError, run
from galaxy.specs import graph, spec
from galaxy.specs import templates as checks
from galaxy.stages import bright as br
from galaxy.stages import bubbles as bb
from galaxy.stages import clouds as cl
from galaxy.stages import systems as sy
from helpers import decl, impls, model, stage

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "model" / "galaxy"
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
MODELS = ("azimuthal", "basic")

# --- the closed list (D214 section 1, "I1 as tested") -------------------------------------------------------------
# A census statistic is a scalar or a radial field computed from realised objects. These, and no other field without
# a phi axis outside the catalogues' own columns, differ between the layer-on and the layer-off run; a field outside
# this list that moves fails test_i1. Each line names the census whose objects it is computed from.
CENSUS_STATISTICS = {
    # the star sample (systems): how many stars the seeded rounding realised
    "catalogue_size",
    # the sample's planets (planets): counts and shares over the sample's stars
    "planet_count_sample", "mean_planets_per_star", "giant_fraction_sample",
    # the bright catalogue: the luminosity its default selection's few thousand brightest stars are complete above
    "bright_star_limit",
    # the cloud census: the mass its realised clouds hold
    "cloud_mass_total",
    # the HII-region census (nebular): the regions' leaked share, the luminosity function's fitted slope (row 35), the
    # [N II]/Halpha gradient (row 37) and the four forbidden lines' ring light, each a sum over the regions in a ring
    "dig_halpha_fraction", "hii_luminosity_function_slope", "nii_halpha_gradient_hii",
    "oiii_5007_surface_brightness_hii", "nii_6583_surface_brightness_hii", "sii_6716_surface_brightness_hii",
    "sii_6731_surface_brightness_hii",
    # the bubble and remnant censuses: the hot phase's filling per ring, a sum over the realised bubbles
    "hot_phase_porosity",
}
# The object classes a placement moves: every column of these is a catalogue's, not a statistic.
PLACED_OBJECTS = {"star", "planet", "bright_star", "cloud", "cluster"}
# And the one census no pattern places (bubbles.remnant_expected shares a ring evenly among its sectors).
UNPLACED_OBJECTS = {"remnant"}


def same(a, b) -> bool:
    """Bit for bit: arrays by dtype, shape and bytes (NaN equal to NaN), scalars and labels by value."""
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    a, b = np.asarray(a), np.asarray(b)
    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()


def constants(m) -> dict[str, float]:
    return {k: c.value for k, c in m.constants.items()}


def answer(response) -> tuple[dict, list[tuple[str, str, tuple, bytes]]]:
    """A response as what it says: its header less ``stages`` (what a request ran depends on what the service
    already held, not on what was asked) and every array's name, dtype, shape and bytes, in the body's order."""
    assert response.ok, response.status
    header, arrays = wire.decode(response.body)
    return ({k: v for k, v in header.items() if k != "stages"},
            [(n, a.dtype.str, a.shape, a.tobytes()) for n, a in arrays.items()])


@pytest.fixture(scope="module")
def reference():
    return layer_reference.load()


@pytest.fixture(scope="module")
def runs(prod):
    """Both models, the layer on and off, every stage, on the production grid: {(model, layer): Outputs}."""
    models = prod[0]
    return {(name, layer): run(models.get(name), layer=layer) for name in MODELS for layer in (True, False)}


@pytest.fixture(scope="module")
def small(prod):
    models = prod[0]
    return {(name, layer): run(models.get(name), grid=SMALL, layer=layer) for name in MODELS for layer in (True, False)}


# --- behaviour preserved: the layer on is S54 ----------------------------------------------------------------------


@pytest.mark.parametrize("name", MODELS)
def test_layer_on_every_field_is_the_s54_reference_bit_for_bit(runs, reference, name):
    """D214: "with the layer on, every published number, every catalogue row ... is bit-identical to S54's". The
    reference is sha256 of every field's bytes, captured before the model moved; nothing is re-pinned here, ever."""
    held = reference["fields"][name]
    now = {n: layer_reference.value_digest(v) for n, v in runs[name, True].fields.items()}
    assert not set(held) - set(now), sorted(set(held) - set(now))  # no field was lost
    moved = [n for n in held if now[n] != held[n]]
    assert moved == [], moved
    # What Phase R adds, and only this: the cloud-interior noise's three scalars (D214 section 5).
    assert set(now) - set(held) == set(layer_reference.ADDED_SCALARS)


def test_layer_on_a_template_s_fields_are_the_reference_too(prod, reference):
    """``ngc_4414`` gained the fifth seed (4414); no stage reads it, so the template's galaxy is the one it was."""
    out = run(prod[0].get("azimuthal"), templates.overrides(templates.TEMPLATES["ngc_4414"]))
    assert out.inputs["texture_seed"] == 4414
    held = reference["fields"]["azimuthal@ngc_4414"]
    moved = [n for n in held if layer_reference.value_digest(out.fields[n]) != held[n]]
    assert moved == [], moved


def test_layer_on_every_route_s_arrays_and_header_are_the_s54_reference(reference):
    """Every input route, a window and the whole disc, both models and a template: each array of the body is the
    reference's bytes in the reference's order, and the header is the reference's once the fields Phase R adds are
    taken out (``layer_reference.normalise``: the fifth seed among the inputs, the ``layer`` echo, the three cloud
    scalars, and ``stages``). The body's own hash is not compared: those additions change it by construction."""
    made = layer_reference.routes_digest()
    assert set(made) == set(reference["routes"])
    for label, got in made.items():
        held = reference["routes"][label]
        assert got["status"] == held["status"] == 200, label
        assert got["arrays"] == held["arrays"], (label, [a[0] for a, b in zip(got["arrays"], held["arrays"]) if a != b])
        assert got["header"] == held["header"], label


def test_the_cloud_route_sends_its_columns_in_the_order_it_always_did(prod):
    """The four texture columns changed publisher, not place: /api/clouds' columns are ``clouds.WIRE_COLUMNS``, which
    is the clouds stage's object columns with the layer's four where they stood, and nothing else."""
    _, impls_, _ = prod
    own = [d.name for d in impls_.get("clouds").publishes if d.kind.domain == "object"]
    layers = [d.name for d in impls_.get("cloud_texture").publishes if d.kind.domain == "object"]
    assert tuple(layers) == cl.TEXTURE_COLUMNS
    assert set(cl.WIRE_COLUMNS) == set(own) | set(layers) and len(cl.WIRE_COLUMNS) == len(own) + len(layers)
    assert [n for n in cl.WIRE_COLUMNS if n in own] == own  # the stage's own, in its own order
    header, arrays = Service(grid=SMALL).handle("/api/clouds", "r_min=7&r_max=9&phi_min=0&phi_max=0.6").frame()
    assert header["columns"] == list(cl.WIRE_COLUMNS) and list(arrays) == [*cl.WIRE_COLUMNS, "cell", "index"]


# --- I1: the layer off moves no law, no radial field and no total -------------------------------------------------


@pytest.mark.parametrize("name", MODELS)
def test_i1_layer_off_moves_only_placements_and_the_listed_census_statistics(runs, name):
    on, off = runs[name, True], runs[name, False]
    assert set(on.fields) == set(off.fields) and on.order == off.order  # the same model ran, every stage of it
    composed = [n for n, d in on.decls.items() if d.composed]
    assert composed and all("phi" in on.decls[n].axes for n in composed)
    for n in composed:  # the neutral value: exactly 1 everywhere, not 1 to rounding
        assert np.all(np.asarray(off.fields[n]) == 1.0), n
        assert not np.all(np.asarray(on.fields[n]) == 1.0), n  # and the layer on does place

    moved_statistics = set()
    for n, d in on.decls.items():
        if d.composed:
            continue
        if d.kind.domain == "object":
            # A catalogue's column: a placement moves it, unless no pattern places that census at all.
            if d.of in UNPLACED_OBJECTS:
                assert same(on.fields[n], off.fields[n]), n
            else:
                assert d.of in PLACED_OBJECTS, (n, d.of)
            continue
        if not same(on.fields[n], off.fields[n]):
            moved_statistics.add(n)
    # Every other field - every radial field, every history, every scalar - is the bit it was, but for the list.
    assert moved_statistics <= CENSUS_STATISTICS, sorted(moved_statistics - CENSUS_STATISTICS)
    # And the list is not padded: each entry does move on the production grid at the default seeds.
    assert moved_statistics == CENSUS_STATISTICS, sorted(CENSUS_STATISTICS - moved_statistics)


@pytest.mark.parametrize("name", MODELS)
def test_i1_every_scalar_of_the_pattern_stages_is_unchanged(runs, prod, name):
    """D214 section 1: "every scalar the bar, pattern and gas_pattern stages publish ... is unchanged: those are
    laws and measured scatters, and they are still drawn. What is switched off is where the arms are\""""
    on, off = runs[name, True], runs[name, False]
    _, impls_, _ = prod
    scalars = [d.name for sid in ("bar", "pattern", "gas_pattern") for d in impls_.get(sid).publishes if d.kind.domain == "galaxy"]
    assert len(scalars) == 14 and {"arm_multiplicity", "pitch_angle", "arm_contrast", "bar_contrast", "gas_arm_contrast",
                                   "bar_pattern_speed"} <= set(scalars)
    for n in scalars:
        assert on.fields[n] == off.fields[n], n


def test_i1_the_layer_off_run_is_reproducible_and_its_determinism_is_a_spec(prod):
    from galaxy.specs import determinism

    models, impls_, table = prod
    assert set(determinism.LAYERS) == {True, False}
    for m in models:
        assert determinism.check_reproducible(m, impls_, table, layer=False) == []
    text = determinism.report([models.get(DEFAULT_MODEL)], impls_, table)
    assert f"model {DEFAULT_MODEL}, layer on: reproducible OK" in text
    assert f"model {DEFAULT_MODEL}, layer off: reproducible OK" in text
    assert f"model {DEFAULT_MODEL}, layer off: reproducible across processes" in text and "FAIL" not in text


# --- I2: a census's expected count per ring does not know the layer ------------------------------------------------


def ring_expectations(out, m) -> dict[str, np.ndarray]:
    """What each census's draw is given, summed round each ring: the number of objects a ring expects."""
    F, R, c = out.fields, out.grid.R, constants(m)
    spec_ = out.grid.spec
    weights = sy._sector_weights(R, compose.stellar_pattern(F))
    stars = sy.CATALOGUE_SAMPLE * sy.cell_shares(F["stellar_surface_density"], R)[:, None] / sy.CELL_SECTORS * np.maximum(weights, 0.0)
    galaxy = br.BrightGalaxy(F, R, out.grid.t, float(spec_.t_max), int(spec_.n_t), c)
    ring, _ = galaxy.locate(br.all_cells())
    rings = int(ring.max()) + 1
    return {
        "stars": stars.sum(axis=1),
        "clouds": cl.expected_counts(F, R, c).sum(axis=1),
        "remnants": bb.remnant_expected(F, R, c).sum(axis=1),
        **{f"bright stars above 10^{x:g} Lsun": np.bincount(ring, weights=galaxy.expected(br.all_cells(), x), minlength=rings)
           for x in (3.0, 4.5)},
    }


@pytest.mark.parametrize("name", MODELS)
def test_i2_each_census_expects_the_same_count_in_every_ring(runs, prod, name):
    """"A census's expected counts per ring are identical with the layer on or off; only placements differ": the
    number handed to the draw, summed round the ring, to 1e-12 of itself - the placement weights average to 1."""
    m = prod[0].get(name)
    on, off = ring_expectations(runs[name, True], m), ring_expectations(runs[name, False], m)
    assert set(on) == set(off)
    for census in on:
        a, b = on[census], off[census]
        assert a.shape == b.shape and np.all(np.isfinite(a)) and a.sum() > 0, census
        assert np.allclose(a, b, rtol=1e-12, atol=0.0), (census, float(np.max(np.abs(a - b) / np.where(b > 0, b, 1.0))))
    # The clusters are their clouds' (one per cloud past its embedded phase): no count of their own to expect.
    # And the realised counts differ by the draw alone: prediction (d), the cloud count within 3% of 16 822.
    n_on, n_off = len(runs[name, True].fields["cloud_radius"]), len(runs[name, False].fields["cloud_radius"])
    assert n_on == 16822 and abs(n_off / 16822 - 1.0) < 0.03, (n_on, n_off)


def test_i2_holds_on_another_galaxy(prod):
    m = prod[0].get(DEFAULT_MODEL)
    given = {**templates.overrides(templates.TEMPLATES["ngc_4414"]), "systems_seed": 3}
    on = ring_expectations(run(m, given, SMALL, layer=True), m)
    off = ring_expectations(run(m, given, SMALL, layer=False), m)
    for census in on:
        assert np.allclose(on[census], off[census], rtol=1e-12, atol=0.0), census


# --- I3: the table is judged with the layer off --------------------------------------------------------------------


def test_i3_every_judging_run_is_layer_off(prod, monkeypatch):
    """``spec.run``, the ensemble, the sweeps and the convergence sweep all pass ``layer=False`` to the runner, and
    none takes a ``layer=`` of its own."""
    import galaxy.run as runner
    from galaxy.specs import convergence

    seen: list[bool] = []
    real = runner.run

    def recording(*args, **kwargs):
        seen.append(kwargs.get("layer", True))
        return real(*args, **kwargs)

    monkeypatch.setattr(runner, "run", recording)
    m = prod[0].get(DEFAULT_MODEL)
    spec.run(m, grid=SMALL)
    spec.ensemble(m, n=2, grid=SMALL)
    spec.sweeps(m, grid=SMALL)
    convergence.sweep(m, {"n_R": (24, 48)}, SMALL)
    assert len(seen) > 12 and not any(seen)
    assert spec.judged({}) == {"layer": False}
    for call in (lambda: spec.run(m, layer=True), lambda: spec.ensemble(m, n=1, layer=True),
                 lambda: spec.judged({"layer": False})):
        with pytest.raises(spec.SpecError, match="layer-off"):
            call()
    assert "judged on the layer-off run" in spec.report([m], {m.name: spec.run(m, grid=SMALL)})


def test_i3_no_row_and_no_check_names_a_synthetic_or_a_composed_field(prod):
    models, impls_, _ = prod
    for m in models:
        declared = {d.name: d for _, sid in m.stages for d in impls_.get(sid).publishes}
        named = [(q.n, f) for q in spec.QUANTITIES for f in (q.field, q.sweep.abscissa if q.sweep else None) if f]
        assert len(named) > 30
        for n, f in named:
            if f in declared:
                assert not declared[f].composed and declared[f].provenance != "synthetic", (n, f)
        for template in templates.TEMPLATES.values():
            for check in template.checks:
                if check.field in declared:
                    assert not declared[check.field].composed and declared[check.field].provenance != "synthetic", check.name
    assert checks.JUDGED_LAYER is False and compose.SETTINGS[checks.JUDGED_SETTING] is False


def test_i3_rows_35_and_37_read_the_layer_off_census(runs):
    """The two rows that read a census (BUILD_III section 1d: they "moved with S51's redraw; under I3 they stop
    moving with placement"). Read once layer-off and pinned here; every other row's field is the same number on and
    off (it is no census statistic: test_i1). Row 35 stays inside KEH89's [-2.5, -1.5]; row 37 stays a miss (#117)."""
    for name in MODELS:
        on, off = runs[name, True].fields, runs[name, False].fields
        # S55 (D214): was -1.98926 (the layer-on census), read layer-off
        assert float(off["hii_luminosity_function_slope"]) == pytest.approx(-2.08124, abs=1e-5)
        # S55 (D214): was -0.105511 (the layer-on census), read layer-off
        assert float(off["nii_halpha_gradient_hii"]) == pytest.approx(-0.102973, abs=1e-6)
        assert float(on["hii_luminosity_function_slope"]) == pytest.approx(-1.98926, abs=1e-5)
        assert float(on["nii_halpha_gradient_hii"]) == pytest.approx(-0.105511, abs=1e-6)
        # D214's prediction (b): row 37 within 0.005 dex/kpc of -0.1055, and still outside [-0.045, -0.005].
        assert abs(float(off["nii_halpha_gradient_hii"]) + 0.1055) < 0.005
        for q in spec.QUANTITIES:
            if q.field in on and q.n not in (spec.ROW_HII_LF_SLOPE, spec.ROW_NII_HALPHA_GRADIENT):
                assert same(on[q.field], off[q.field]), (q.n, q.field)
    q35 = next(q for q in spec.QUANTITIES if q.n == spec.ROW_HII_LF_SLOPE)
    q37 = next(q for q in spec.QUANTITIES if q.n == spec.ROW_NII_HALPHA_GRADIENT)
    assert q35.lo <= -2.08124 <= q35.hi and not q37.lo <= -0.102973 <= q37.hi
    assert spec.ROW_NII_HALPHA_GRADIENT in spec.MISSES and spec.ROW_HII_LF_SLOPE not in spec.MISSES


# --- I4: no physics stage reads the layer --------------------------------------------------------------------------

SYNTHETIC = dict(provenance="synthetic", stands_in_for="a physics", conserves="a total", statistic="none read (#95)")


def test_i4_the_production_graphs_declare_their_readers(prod):
    """The closed set, read from the stages' own declarations. ``nebular`` and ``bubbles`` inherit the clusters'
    objects and require neither a composed nor a synthetic field, so they are not readers; ``planets`` rebuilds
    the star catalogue's layout from the stellar pattern, so it is."""
    models, impls_, table = prod
    assert graph.check(models, impls_, table) == []
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert set(g.placement_readers) == {"systems", "bright_stars", "clouds", "clusters", "planets"}
        assert g.layer_stages == ("cloud_texture",)
        expected = {"pattern", "gas_pattern"} | ({"sfh_azimuthal"} if m.name == "azimuthal" else set())
        assert set(g.composing_stages) == expected
        # What the declarations are for: every stage that requires a composed or a synthetic field is one of them.
        decl_of = {d.name: d for st in g.order for d in st.publishes}
        for st in g.order:
            reads = [n for n in st.requires + st.requires_optional if n in decl_of]
            if any(decl_of[n].composed or decl_of[n].provenance == "synthetic" for n in reads):
                assert st.may_place, st.id
        assert not impls_.get("sfh").may_place  # the base of the composing extension has no such right
        report = graph.report([m], impls_, table)
        assert "placement readers: bright_stars, clouds, systems, planets, clusters" in report
        assert "layer stages: cloud_texture" in report and "input unread by ruling: texture_seed" in report


def test_i4_the_graph_refuses_a_physics_stage_that_requires_a_composed_field():
    contrast = decl("contrast", axes=("R", "phi"))
    assert contrast.composed and not decl("profile").composed
    composer = stage("composer", (contrast,))
    physics = stage("physics", ("g",), requires=("contrast",))
    m = model("m", composer, physics)
    problems = graph.check([m], impls(composer, physics), INPUTS)
    assert [p.code for p in problems] == ["layer-reader"]
    assert "'physics'" in problems[0].detail and "'contrast'" in problems[0].detail and "invariant I4" in problems[0].detail
    # An optional requirement is a requirement.
    optional = decl("contrast", axes=("R", "phi"), optional=True)
    po, optional_reader = stage("composer", (optional,)), stage("physics", ("g",), requires_optional=("contrast",))
    assert [p.code for p in graph.check([model("m", po, optional_reader)], impls(po, optional_reader), INPUTS)] == ["layer-reader"]
    # A declared placement reader may, and so may a stage that composes a field of its own from it.
    reader = stage("physics", ("g",), requires=("contrast",), placement_reader=True)
    assert graph.check([model("m", composer, reader)], impls(composer, reader), INPUTS) == []
    second = stage("physics", (decl("g", axes=("R", "phi")),), requires=("contrast",))
    assert second.composes and graph.check([model("m", composer, second)], impls(composer, second), INPUTS) == []


def test_i4_the_graph_refuses_a_physics_stage_that_requires_a_synthetic_field():
    texture = decl("texture", **SYNTHETIC)
    realiser = stage("realiser", (texture,), compute=cloud_texture.compute_cloud_texture, layer_stage=True)
    physics = stage("physics", (decl("g", provenance="seeded"),), requires=("texture",))
    problems = graph.check([model("m", realiser, physics)], impls(realiser, physics), INPUTS)
    assert [p.code for p in problems] == ["layer-reader"] and "synthetic" in problems[0].detail
    reader = stage("physics", (decl("g", provenance="seeded"),), requires=("texture",), placement_reader=True)
    assert graph.check([model("m", realiser, reader)], impls(realiser, reader), INPUTS) == []
    # A reader of a synthetic field is seeded, not synthetic and not derived (D55, one provenance per stage).
    derived = stage("physics", ("g",), requires=("texture",), placement_reader=True)
    assert [p.code for p in graph.check([model("m", realiser, derived)], impls(realiser, derived), INPUTS)] == ["provenance"]


def test_i4_only_a_layer_stage_publishes_synthetic_and_it_lives_under_the_layer():
    texture = decl("texture", **SYNTHETIC)
    # A stage outside galaxy/layer/ that publishes a synthetic field: its provenance does not compute.
    outside = stage("outside", (texture,))
    assert [p.code for p in graph.check([model("m", outside)], impls(outside), INPUTS)] == ["provenance"]
    # One that declares itself a layer stage without living there.
    claims = stage("claims", (texture,), layer_stage=True)
    assert claims.home == "helpers"
    assert [p.code for p in graph.check([model("m", claims)], impls(claims), INPUTS)] == ["layer-stage"]
    # One that lives there and does not say so.
    silent = stage("silent", ("f",), compute=cloud_texture.compute_cloud_texture)
    assert silent.home == "galaxy.layer.cloud_texture"
    assert [p.code for p in graph.check([model("m", silent)], impls(silent), INPUTS)] == ["layer-stage"]
    # A layer stage publishes synthetic fields, all of them, whatever it reads.
    mixed = stage("mixed", (texture, decl("plain")), compute=cloud_texture.compute_cloud_texture, layer_stage=True)
    assert [p.code for p in graph.check([model("m", mixed)], impls(mixed), INPUTS)] == ["provenance"]
    whole = stage("whole", (texture,), compute=cloud_texture.compute_cloud_texture, layer_stage=True,
                  reads_seeds=("systems_seed",), checkpoint=5)
    g = graph.analyse(model("m", whole), impls(whole), INPUTS)
    assert g.ok and g.provenance == {"texture": "synthetic"} and g.layer_stages == ("whole",)


@pytest.mark.parametrize("stage_id, field", [("clusters", "cloud_source_offset"), ("systems", "sfr_modulation"),
                                             ("bright_stars", "sfr_modulation")])
def test_i4_a_production_census_without_its_declaration_fails_the_graph(prod, stage_id, field):
    models, impls_, table = prod
    m = models.get("azimuthal")
    undeclared = {st.id: st for st in impls_}
    undeclared[stage_id] = replace(impls_.get(stage_id), placement_reader=False)
    problems = graph.check([m], undeclared, table)
    assert problems and {p.code for p in problems} == {"layer-reader"}
    assert any(f"'{stage_id}'" in p.detail and f"'{field}'" in p.detail for p in problems)


def test_i4_compose_refuses_a_stage_that_is_not_a_reader_at_run_time(prod):
    """The graph sees requirements; a pattern object is rebuilt from scalars, which it cannot see. So the stage's
    own view of the fields says whether it may ask, and ``compose`` refuses one that may not."""
    models, impls_, table = prod
    m = models.get(DEFAULT_MODEL)
    for stage_id in ("clouds", "planets"):  # neither requires a composed field: only compose can catch them
        undeclared = {st.id: st for st in impls_}
        undeclared[stage_id] = replace(impls_.get(stage_id), placement_reader=False)
        assert graph.check([m], undeclared, table) == []
        with pytest.raises(UndeclaredAccess, match="placement reader"):
            run(m, grid=SMALL, impls=undeclared, only=[d.name for d in impls_.get(stage_id).publishes][:1])


# --- I5: the API's half of the switch ------------------------------------------------------------------------------

INPUT_ROUTES = ("/api/arrays", "/api/region", "/api/system", "/api/clouds", "/api/clusters", "/api/remnants",
                "/api/bright", "/api/render")
SECTOR = "r_min=7&r_max=9&phi_min=0&phi_max=0.6"
B_V = json.dumps([{"name": b, "shape": "gaussian", "centre": c, "fwhm": 900.0} for b, c in (("B", 4400.0), ("V", 5500.0))])
QUERIES = {
    "/api/arrays": {"fields": ["pattern_density_contrast,stellar_mass_total"]},
    "/api/region": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/system": {"cell": ["300"], "index": ["0"]},
    "/api/clouds": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/clusters": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/remnants": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/bright": {"n": ["400"]},
    "/api/render": {"filters": [B_V]},
}


def test_i5_every_route_that_takes_inputs_takes_the_switch():
    """The routes with ``layer`` among their parameters are exactly those that take inputs (they take ``template``),
    and ``layer`` is reserved, so it is never read as an input."""
    takes = {r.path for r in ROUTES if "layer" in r.params}
    assert takes == {r.path for r in ROUTES if "template" in r.params} == set(INPUT_ROUTES) == set(QUERIES)
    assert "layer" in RESERVED and "layer" not in INPUTS
    index = Service(grid=SMALL).handle("/api").json()
    assert "layer=off" in index["layer"] and "400" in index["layer"]


@pytest.mark.parametrize("path", INPUT_ROUTES)
def test_i5_the_header_echoes_the_setting_and_a_bad_value_is_a_400(path):
    svc = Service(grid=SMALL)
    q = QUERIES[path]
    plain = svc.handle(path, q)
    on = svc.handle(path, {**q, "layer": ["on"]})
    off = svc.handle(path, {**q, "layer": ["off"]})
    assert plain.ok and on.ok and off.ok, (plain.status, on.status, off.status)
    # Absent and on are one request: the same header and the same arrays, byte for byte.
    assert answer(plain) == answer(on) and svc.handle(path, q).body == on.body
    assert answer(on)[0]["layer"] == "on" and answer(off)[0]["layer"] == "off"
    for bad in ("0", "false", "OFF", ""):
        refused = svc.handle(path, {**q, "layer": [bad]})
        assert refused.status == 400 and "layer=" in refused.json()["error"], bad
    assert svc.handle(path, {**q, "layer": ["on", "off"]}).status == 400  # given twice


def test_i5_on_and_off_never_share_a_cache_entry():
    svc = Service(grid=SMALL, cache=4)
    fields = {"fields": ["pattern_density_contrast,gas_density_contrast,sfr_modulation"]}
    on = svc.handle("/api/arrays", fields).frame()[1]
    off = svc.handle("/api/arrays", {**fields, "layer": ["off"]}).frame()[1]
    again = svc.handle("/api/arrays", fields).frame()[1]
    assert len(svc._cache) == 2  # one galaxy, two settings: two entries
    for name in on:
        assert np.all(off[name] == 1.0) and not np.all(on[name] == 1.0) and same(on[name], again[name]), name
    # The census caches too: a window's clouds asked for on, off, on again.
    first = svc.handle("/api/clouds", SECTOR)
    without = svc.handle("/api/clouds", SECTOR + "&layer=off")
    assert answer(svc.handle("/api/clouds", SECTOR)) == answer(first)
    assert answer(svc.handle("/api/clouds", SECTOR + "&layer=off")) == answer(without)
    a, b = first.frame()[1], without.frame()[1]
    assert not same(a["cloud_azimuth"], b["cloud_azimuth"])
    for route, column in (("/api/region", "star_azimuth"), ("/api/clusters", "cluster_azimuth")):
        got_on, got_off = svc.handle(route, SECTOR), svc.handle(route, SECTOR + "&layer=off")
        assert not same(got_on.frame()[1][column], got_off.frame()[1][column]), route
        assert answer(svc.handle(route, SECTOR)) == answer(got_on), route
    bright_on, bright_off = svc.handle("/api/bright", "n=300"), svc.handle("/api/bright", "n=300&layer=off")
    assert not same(bright_on.frame()[1]["bright_star_azimuth"], bright_off.frame()[1]["bright_star_azimuth"])
    assert answer(svc.handle("/api/bright", "n=300")) == answer(bright_on)


def test_i5_what_layer_off_serves():
    """The contract the viewer builds against: the composed fields 1, the cloud texture columns 0, the cloud
    interior's three scalars in the header either way, the render's frame placed evenly round each ring."""
    svc = Service(grid=SMALL)
    on_h, on = svc.handle("/api/clouds", SECTOR).frame()
    off_h, off = svc.handle("/api/clouds", SECTOR + "&layer=off").frame()
    interior = {"cloud_interior_octaves": 4.0, "cloud_interior_lacunarity": 2.0, "cloud_interior_gain": 0.5}
    for header in (on_h, off_h):
        assert {k: header["scalars"][k] for k in interior} == interior
        assert header["columns"] == list(cl.WIRE_COLUMNS)
    assert len(off["cloud_radius"]) > 20
    for name in cl.TEXTURE_COLUMNS:
        assert np.all(off[name] == 0.0) and np.any(on[name] != 0.0), name
    # The render: every component placed round a ring is the ring's own value in every cell, and the dust's
    # placement is 1.
    header, arrays = svc.handle("/api/render", {"filters": [B_V], "layer": ["off"]}).frame()
    assert header["layer"] == "off" and np.all(arrays["dust_placement"] == 1.0)
    for name in ("stars", "halpha_hii", "dust_scattered"):
        assert np.all(arrays[name] == arrays[name][:, :1, :]), name
    lit = svc.handle("/api/render", {"filters": [B_V]}).frame()[1]
    assert not np.all(lit["stars"] == lit["stars"][:, :1, :])
    # Each ring keeps its light: the frame's total through each filter is the layer-on frame's to rounding.
    total_off = checks.frame_total(header, arrays)
    total_on = checks.frame_total(svc.handle("/api/render", {"filters": [B_V]}).frame()[0], lit)
    assert np.allclose(total_off, total_on, rtol=1e-12)


def test_i5_the_metadata_names_the_fourth_kind_and_the_fifth_seed(model):
    svc = Service(grid=SMALL)
    fields = svc.handle("/api/fields", f"model={model.name}").json()["fields"]
    assert {f["provenance"] for f in fields} == set(PROVENANCE) == {"derived", "seeded", "synthetic"}
    synthetic = [f for f in fields if f["provenance"] == "synthetic"]
    assert {f["name"] for f in synthetic} == {*cl.TEXTURE_COLUMNS, *layer_reference.ADDED_SCALARS}
    for f in fields:
        if f["provenance"] == "synthetic":
            assert all(isinstance(f[k], str) and f[k].strip() for k in SYNTHETIC_DECLARATIONS), f["name"]
            assert f["stage"] == "cloud_texture" and re.search(r"none read \(#(95|110)\)", f["statistic"]), f["name"]
        else:
            assert not set(SYNTHETIC_DECLARATIONS) & set(f), f["name"]
    seeds_ = svc.handle("/api/inputs", f"model={model.name}").json()["seeds"]
    assert [s["name"] for s in seeds_] == [s.name for s in seeds()] and len(seeds_) == 5
    texture = next(s for s in seeds_ if s["name"] == "texture_seed")
    assert texture["default"] == 0 and texture["checkpoint"] == 3 and "P1" in texture["about"]
    published = {t["name"]: t["inputs"]["seeds"]["texture_seed"] for t in svc.handle("/api/templates").json()["templates"]}
    assert published == {"milky_way": 0, "ngc_4414": 4414}
    stages = svc.handle("/api/stages", f"model={model.name}").json()
    assert "cloud_texture" in stages["order"] and stages["order"].index("clouds") < stages["order"].index("cloud_texture") < stages["order"].index("clusters")


# --- the oracle (BUILD_III Phase R, item 5) ------------------------------------------------------------------------


def test_the_oracle_layer_off_azimuthal_is_layer_off_basic(runs):
    """``basic`` is the model without star formation that follows the arms. With the layer off the arms are nowhere,
    so the two are one galaxy: every field they share is bit-identical - every radial field, every history, every
    scalar and every column of every catalogue - and the one field only ``azimuthal`` has is 1 everywhere."""
    a, b = runs["azimuthal", False], runs["basic", False]
    assert set(a.fields) - set(b.fields) == {"sfr_modulation"} and not set(b.fields) - set(a.fields)
    assert np.all(np.asarray(a.fields["sfr_modulation"]) == 1.0)
    differ = [n for n in b.fields if not same(a.fields[n], b.fields[n])]
    assert differ == [], differ
    columns = [n for n, d in b.decls.items() if d.kind.domain == "object"]
    assert len(columns) > 100 and len(b.fields) == 334


def test_the_oracle_against_layer_on_basic_holds_outside_the_censuses(runs):
    """The second comparison D214 names: layer-off ``azimuthal`` against layer-on ``basic``, the fields without a phi
    axis. It holds on every radial field, history and scalar that is not a census statistic - 218 fields, bit for
    bit. It does not hold on the catalogues' columns or the census statistics, and cannot: layer-on ``basic`` places
    its censuses by the pattern. Those are exactly the fields I1 lets move, in ``basic`` itself (test_i1)."""
    a, b = runs["azimuthal", False], runs["basic", True]
    differ = {n for n, d in b.decls.items() if not d.composed and not same(a.fields[n], b.fields[n])}
    statistics = {n for n in differ if b.decls[n].kind.domain != "object"}
    assert statistics == CENSUS_STATISTICS
    assert {b.decls[n].of for n in differ - statistics} == PLACED_OBJECTS
    held = [n for n, d in b.decls.items() if not d.composed and n not in differ]
    assert len(held) == 218 and all(b.decls[n].of in (None, *UNPLACED_OBJECTS) for n in held)


def test_the_oracle_holds_layer_off_on_a_small_grid_and_another_seed(prod):
    models = prod[0]
    given = {"systems_seed": 5, "pattern_seed": 2, "halo_mass": 8e11}
    a = run(models.get("azimuthal"), given, SMALL, layer=False)
    b = run(models.get("basic"), given, SMALL, layer=False)
    assert [n for n in b.fields if not same(a.fields[n], b.fields[n])] == []


# --- Appendix B applied: the four cloud columns, the cloud interior's noise ----------------------------------------


@pytest.mark.parametrize("name", MODELS)
def test_the_cloud_texture_columns_are_the_bits_they_were(runs, reference, prod, name):
    """Layer on: the stage's four columns are the reference's (the ``clouds`` stage published them at S54), and are
    what a census materialised whole carries. The draws kept their seed, their stream paths and their values."""
    on = runs[name, True]
    for column in cl.TEXTURE_COLUMNS:
        assert layer_reference.value_digest(on.fields[column]) == reference["fields"][name][column], column
        assert on.decls[column].provenance == "synthetic" and on.decls[column].of == "cloud"
    m = prod[0].get(name)
    census = cl.materialise_clouds(on.fields, on.grid.R, int(on.inputs["systems_seed"]), constants(m))
    for column in cl.WIRE_COLUMNS:
        assert same(census[column], on.fields[column]), column
    own = cl.materialise_clouds(on.fields, on.grid.R, int(on.inputs["systems_seed"]), constants(m), texture=False)
    assert not set(cl.TEXTURE_COLUMNS) & set(own) and census.counts == own.counts
    # The offset lies inside its cloud, the gradient in [0, 1], the angles on the circle: the draws' own laws.
    offset, size = np.asarray(on.fields["cloud_source_offset"]), np.asarray(on.fields["cloud_size"])
    assert np.all((offset >= 0) & (offset <= size)) and np.all(np.asarray(on.fields["cloud_density_gradient"]) < 1.0)


@pytest.mark.parametrize("name", MODELS)
def test_the_cloud_texture_is_neutral_with_the_layer_off(runs, name):
    """No offset, no gradient, angles 0 - and a cluster then stands at its cloud's centre, exactly."""
    off = runs[name, False]
    n = len(off.fields["cloud_radius"])
    assert n > 16000
    for column in cl.TEXTURE_COLUMNS:
        value = np.asarray(off.fields[column])
        assert value.shape == (n,) and value.dtype == np.float64 and np.all(value == 0.0), column
    hosts = np.asarray(off.fields["cloud_cluster_index"]) >= 0
    assert hosts.sum() == len(off.fields["cluster_radius"]) > 12000
    assert same(off.fields["cluster_radius"], np.asarray(off.fields["cloud_radius"])[hosts])
    assert same(off.fields["cluster_azimuth"], np.asarray(off.fields["cloud_azimuth"])[hosts])
    assert same(off.fields["cluster_height"], np.asarray(off.fields["cloud_height"])[hosts])
    on = runs[name, True]
    hosts_on = np.asarray(on.fields["cloud_cluster_index"]) >= 0
    assert not same(on.fields["cluster_radius"], np.asarray(on.fields["cloud_radius"])[hosts_on])


def test_the_cloud_interior_s_noise_is_published_as_the_viewer_holds_it(runs):
    """D214 section 5, rule D5 as amended: the viewer may evaluate a function the model publishes and holds no
    parameter of its own, so the octave count, lacunarity and gain it uses today are the layer's scalars - read from
    the viewer's own source here, so the two cannot drift before the viewer reads the model's."""
    for key, out in runs.items():
        got = {n: out.fields[n] for n in layer_reference.ADDED_SCALARS}
        assert got == {"cloud_interior_octaves": 4.0, "cloud_interior_lacunarity": 2.0, "cloud_interior_gain": 0.5}, key
        assert got == cloud_texture.interior_scalars()
        for n in got:
            d = out.decls[n]
            assert d.provenance == "synthetic" and "#110" in d.statistic and "Not shown by the viewer" in d.about
    source = (ROOT / "frontend" / "src" / "galaxy" / "region.ts").read_text(encoding="utf-8")
    # Since builder D (S55) the viewer holds none of the three: it evaluates the interior with what the clouds'
    # header publishes, and keeps one measured normaliser with the parameter set it was measured for. The guard
    # therefore runs the other way round: the viewer names no octave count of its own, and the set its measured
    # constant belongs to is the layer's.
    assert "export const OCTAVES" not in source
    m = re.search(r"measuredFor: \{ octaves: (\d+), lacunarity: ([\d.]+), gain: ([\d.]+) \}", source)
    assert m, "region.ts no longer records which parameters its measured normaliser belongs to"
    assert (float(m[1]), float(m[2]), float(m[3])) == (
        cloud_texture.INTERIOR_OCTAVES, cloud_texture.INTERIOR_LACUNARITY, cloud_texture.INTERIOR_GAIN)


def test_a_synthetic_field_declares_what_it_stands_in_for_what_it_conserves_and_its_statistic():
    base = dict(name="f", label="f", unit="dimensionless", kind=Kind.FIELD, axes=("R",), ramp=Ramp("greys"), about="a test field")
    ok = FieldDecl(**base, **SYNTHETIC)
    assert ok.provenance == "synthetic" and ok.contract()[-3:] == ("a physics", "a total", "none read (#95)")
    for missing in SYNTHETIC_DECLARATIONS:
        with pytest.raises(DeclarationError, match="a synthetic field declares"):
            FieldDecl(**base, **{**SYNTHETIC, missing: "  "})
    for kind in ("derived", "seeded"):
        FieldDecl(**base, provenance=kind)
        for given in SYNTHETIC_DECLARATIONS:
            with pytest.raises(DeclarationError, match="synthetic field's declarations"):
                FieldDecl(**base, provenance=kind, **{given: "said anyway"})
    # "none read" is a debt and names it; a cited statistic needs no debt.
    for unsourced in ("none read", "None read: no source", "none read (debt ninety-five)"):
        with pytest.raises(DeclarationError, match="names it"):
            FieldDecl(**base, **{**SYNTHETIC, "statistic": unsourced})
    FieldDecl(**base, **{**SYNTHETIC, "statistic": "a power spectrum of slope -2.7 [verified: a source]"})
    assert FieldDecl(**base, **{**SYNTHETIC, "statistic": "none read (#110)"}).statistic.endswith("(#110)")
    with pytest.raises(DeclarationError, match="provenance"):
        FieldDecl(**base, provenance="composed")


def test_texture_seed_is_the_fifth_seed_and_no_stage_reads_it_yet(prod):
    """D214 section 3. **This test fails the day a stage reads ``texture_seed``** (BUILD_III phase P1's mode phases):
    remove ``graph.UNREAD_BY_RULING["texture_seed"]`` then, and this test's first half with it - the seed binds at
    its reader's checkpoint like every other, and the graph's one named exception is spent."""
    models, impls_, table = prod
    assert [s.name for s in seeds()] == ["world_seed", "pattern_seed", "systems_seed", "planets_seed", "texture_seed"]
    assert dict(graph.UNREAD_BY_RULING).keys() == {"texture_seed"}
    readers = sorted(st.id for st in impls_ if "texture_seed" in st.reads_seeds)
    assert readers == [], f"{readers} read texture_seed: remove graph.UNREAD_BY_RULING['texture_seed'] (D214 section 3)"
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert g.input_checkpoint["texture_seed"] is None and g.unread_by_ruling == ("texture_seed",)
        assert g.unbound_inputs == ()  # every other input is read
    # Accepted by a run, on every route, and moving nothing: rerolling it is the same galaxy.
    m = models.get(DEFAULT_MODEL)
    a, b = run(m, {"texture_seed": 0}, SMALL), run(m, {"texture_seed": 987654321}, SMALL)
    assert b.inputs["texture_seed"] == 987654321 and [n for n in a.fields if not same(a.fields[n], b.fields[n])] == []
    header = Service(grid=SMALL).handle("/api/clouds", SECTOR + "&texture_seed=12").frame()[0]
    assert header["inputs"]["texture_seed"] == 12
    # A seed nobody may leave unread without a ruling: the exception is by name.
    unread = stage("s", ("f",))
    g = graph.analyse(model("m", unread), impls(unread), INPUTS)
    assert "world_seed" in g.unbound_inputs and "texture_seed" not in g.unbound_inputs


# --- one reader of the switch (rule B13) ---------------------------------------------------------------------------


def model_sources() -> list[Path]:
    files = sorted(PACKAGE.rglob("*.py"))
    assert len(files) > 50
    return files


def test_compose_is_the_only_caller_of_from_fields():
    """A pattern object is obtained from ``compose`` or not at all: ``.from_fields(`` appears in the model only where
    it is defined (the two pattern classes) and where compose calls it."""
    calls: dict[str, int] = {}
    for path in model_sources():
        text = path.read_text(encoding="utf-8")
        found = len(re.findall(r"\.from_fields\(", text))
        if found:
            calls[path.relative_to(PACKAGE).as_posix()] = found
    assert set(calls) == {"layer/compose.py"}, calls
    assert calls["layer/compose.py"] == 3  # the stellar pattern, the gas pattern, and the docstring that says so
    defined = [p.relative_to(PACKAGE).as_posix() for p in model_sources() if "def from_fields(" in p.read_text(encoding="utf-8")]
    assert defined == ["stages/gas_pattern.py", "stages/pattern.py"]


def names_the_switch(node: ast.AST) -> bool:
    return any((isinstance(n, ast.Name) and n.id == "layer") or (isinstance(n, ast.Attribute) and n.attr == "layer")
               for n in ast.walk(node))


def test_nothing_but_compose_branches_on_the_layer():
    """The runner, the stages' context, the service and the specs carry the setting - they pass it, store it and
    echo it. None of them decides anything by it: no ``if``, conditional expression, ``while``, ``assert``,
    comparison, boolean operation, ``not`` or comprehension filter outside ``galaxy/layer/compose.py`` reads a name
    or an attribute called ``layer``."""
    offenders: list[str] = []
    for path in model_sources():
        if path == PACKAGE / "layer" / "compose.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            tests: list[ast.AST] = []
            if isinstance(node, (ast.If, ast.IfExp, ast.While, ast.Assert)):
                tests.append(node.test)
            elif isinstance(node, (ast.Compare, ast.BoolOp)):
                tests.append(node)
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                tests.append(node)
            elif isinstance(node, ast.comprehension):
                tests.extend(node.ifs)
            elif isinstance(node, ast.Match):
                tests.append(node.subject)
            if any(names_the_switch(t) for t in tests):
                offenders.append(f"{path.relative_to(PACKAGE).as_posix()}:{node.lineno if hasattr(node, 'lineno') else '?'}")
    assert offenders == [], offenders
    # compose itself does: the instrument sees a branch where there is one.
    tree = ast.parse((PACKAGE / "layer" / "compose.py").read_text(encoding="utf-8"))
    assert any(isinstance(n, (ast.If, ast.IfExp)) for n in ast.walk(tree))


def test_fields_carry_the_setting_and_compose_refuses_a_mapping_that_does_not(small, prod):
    """How the switch travels: run -> each stage's Context -> the run's fields -> whatever materialises from them.
    A catalogue cannot be materialised with the layer's placements from a run without them, or the reverse, because
    there is no argument to pass: the fields say which run they are."""
    on, off = small[DEFAULT_MODEL, True], small[DEFAULT_MODEL, False]
    assert isinstance(on.fields, Fields) and (on.layer, on.fields.layer, off.layer, off.fields.layer) == (True, True, False, False)
    assert compose.setting(on.fields) == "on" and compose.setting(off.fields) == "off"
    m = prod[0].get(DEFAULT_MODEL)
    c = constants(m)
    assert compose.stellar_pattern(on.fields) is not None and compose.stellar_pattern(off.fields) is None
    assert compose.gas_pattern(on.fields, c) is not None and compose.gas_pattern(off.fields, c) is None
    assert compose.placement_weight(on.fields, "sfr_modulation") is not None
    assert compose.placement_weight(off.fields, "sfr_modulation") is None
    assert np.all(compose.published(off.fields, "sfr_modulation") == 1.0)
    assert compose.published(off.fields, "no_such_field") is None
    # A census drawn from each run's fields is that run's census, with no word from the caller.
    seed = int(on.inputs["systems_seed"])
    for out in (on, off):
        census = cl.materialise_clouds(out.fields, out.grid.R, seed, c)
        for column in cl.WIRE_COLUMNS:
            assert same(census[column], out.fields[column]), (out.layer, column)
    # A plain dict of the same fields says nothing, and is refused rather than assumed.
    bare = dict(off.fields)
    for call in (lambda: compose.stellar_pattern(bare), lambda: compose.gas_pattern(bare, c),
                 lambda: compose.placement_weight(bare, "sfr_modulation"), lambda: compose.published(bare, "sfr_modulation"),
                 lambda: cl.materialise_clouds(bare, off.grid.R, seed, c),
                 lambda: sy.materialise(bare, off.grid.R, off.grid.t, seed, 2000, migration=3.6)):
        with pytest.raises(LayerError, match="does not say whether the randomness layer is on"):
            call()
    assert same(cl.materialise_clouds(Fields(bare, layer=False), off.grid.R, seed, c)["cloud_azimuth"], off.fields["cloud_azimuth"])


def test_a_run_is_not_resumed_under_the_other_setting(small, prod):
    m = prod[0].get(DEFAULT_MODEL)
    part = run(m, grid=SMALL, only=("pattern_density_contrast",), layer=False)
    with pytest.raises(RunError, match="layer off"):
        run(m, grid=SMALL, resume=part, layer=True)
    whole = run(m, grid=SMALL, resume=part, layer=False)
    assert whole.layer is False and whole.ran and "pattern" not in whole.ran
    assert [n for n in whole.fields if not same(whole.fields[n], small[DEFAULT_MODEL, False].fields[n])] == []


# --- the templates' checks, read layer-off -------------------------------------------------------------------------


def test_the_template_checks_layer_off_are_the_numbers_d213_recorded():
    """The five checks of ``ngc_4414`` on the production grid, read layer-off as the rows are (I3). The four field
    checks are radial and are the bits they were; the colour reads the face-on render, whose frame sums each ring
    round the ring, and moved in its thirteenth decimal (0.6355279197563419 layer-on). No verdict changed."""
    results = {r.name: r for r in checks.evaluate(["ngc_4414"])["ngc_4414"]}
    assert {n: r.status for n, r in results.items()} == dict.fromkeys(results, "fail") and len(results) == 5
    assert results["curve_shape"].value == 0.6532426864889841
    assert results["star_formation_rate"].value == 0.6528663372411139
    assert results["hydrogen_mass"].value == 4803633219.748805
    assert results["absolute_magnitude_k"].value == -23.270507283088264
    assert results["colour_b_v_face_on"].value == pytest.approx(0.6355279197563419, abs=1e-11)
