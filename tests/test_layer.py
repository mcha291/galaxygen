"""The separation (S55, BUILD_III Phase R; DECISIONS.md D214): the physics model beside the randomness layer.

Phase R is a behaviour-preserving restructure. What this file holds, in the order BUILD_III section 1d states it:

- **The reference.** With the layer off, every field of both models at both templates' inputs on the production
  grid, and every array of every input route's body, is bit-identical to S55's layer-off run, captured before any of
  Phase P1's model code moved (``tests/layer_reference.py``, ``tests/layer_reference_s55.json``) - but for a closed,
  named list (``LAYER_OFF_EXCEPTIONS``). Until S56 the reference was S54's with the layer **on** (Phase R was
  behaviour-preserving); it is retired, because from P1 the layer-on galaxy changes by design (D215).
- **I1.** With the layer off the model runs, and every field not declared composed - every scalar, every history,
  every radial field, a phi-axis field too - is bit-identical to the layer-on run, except the census statistics, a
  closed list here, each entry naming the census it is computed from. Every composed field is its declared neutral.
- **I2.** A census's expected count per ring is the same with the layer on or off, to 1e-12. Until L1 the realised
  counts, and every total summed over realised objects, differ by re-draw noise.
- **I3.** The acceptance table and the templates' checks are judged on the layer-off run, and no row names a
  synthetic or a composed field.
- **I4.** No physics stage requires a composed or a synthetic field: the graph refuses one that is not a declared
  placement reader, a composing stage or a layer stage, and ``compose`` refuses it again at run time. Placement
  also reaches physics through the realised catalogues: the stages that bin realised objects are a closed list.
- **I5 (the API's half).** Every route that takes inputs takes ``layer=off``; on and off never share a cache entry;
  any other value is a 400; the header echoes the setting.
- **The oracle.** Layer-off ``azimuthal`` equals layer-off ``basic`` on every field they share.
- **Appendix B applied.** The four cloud columns are the layer's, synthetic, drawn on the streams they always were
  with the layer on and zero with it off; ``texture_seed`` is the fifth seed, and since S56 the arm modes' phases
  read it: rerolling it moves the arms and what is placed by them, and no law (BUILD_III section 1c rule 1).
- **One reader of the switch.** No module of the model but ``galaxy/layer/compose.py`` branches on the setting, none
  calls ``.from_fields(``, and none constructs a pattern object by its class.

**As amended at gate G1 (D214, ruling by Fable).** A *composed* field is one that declares itself so, with its
neutral value (``FieldDecl(composed=True, neutral=...)``): nothing here, and nothing in the model, reads the axes.
The invariants are stated on *expected* totals: a census draws each cell's count at an expectation that carries the
placement weight, so with the layer off its realised objects are another draw. **No per-object on/off assertion is
made, and none should be added** (gate G1, Q6): with different realised counts the objects of the two runs do not
correspond.
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
from galaxy.core import seeds as _seeds
from galaxy.layer import cloud_texture, compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import RunError, run
from galaxy.specs import graph, spec
from galaxy.specs import templates as checks
from galaxy.stages import bright as br
from galaxy.stages import bubbles as bb
from galaxy.stages import clouds as cl
from galaxy.stages import pattern as pt
from galaxy.stages import systems as sy
from helpers import decl, impls, model, stage

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "model" / "galaxy"
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
MODELS = ("azimuthal", "basic")

# --- the closed list (BUILD_III section 1d, I1 as amended at gate G1; D214 change 12) ------------------------------
# A census statistic is a scalar or a radial field computed from realised objects. These fourteen - the measured
# fourteen, nine scalars and five radial fields - and no other field outside the catalogues' own columns and the
# declared composed fields, differ between the layer-on and the layer-off run; a field outside this list that moves
# fails test_i1. Each entry names (the stage that publishes it, the census whose realised objects it is computed
# from, and where: the function that computes it). After L1's ring-first draw the list is empty.
CENSUS_STATISTICS = {
    "catalogue_size": ("systems", "the star sample",
                       "systems.compute_systems: the rows that systems.cell_counts' seeded rounding realised"),
    "planet_count_sample": ("planets", "the star sample's planets",
                            "planets.compute_planets: the planets drawn for the sample's stars, counted"),
    "mean_planets_per_star": ("planets", "the star sample's planets",
                              "planets.compute_planets: the planets per star, averaged over the sample's stars"),
    "giant_fraction_sample": ("planets", "the star sample's planets",
                              "planets.compute_planets: the share of the sample's stars with a giant"),
    "bright_star_limit": ("bright_stars", "the bright catalogue",
                          "bright.select_brightest, through bright.scalars: the luminosity the default selection's "
                          "brightest few thousand realised stars are complete above"),
    "cloud_mass_total": ("clouds", "the cloud census",
                         "clouds.compute_clouds: the realised clouds' cloud_mass, summed"),
    "dig_halpha_fraction": ("nebular", "the HII-region census",
                            "nebular.leaked_fraction: the regions' leaked share, a sum over the realised clusters"),
    "hii_luminosity_function_slope": ("nebular", "the HII-region census",
                                      "nebular.luminosity_function_slope: a fit to the realised regions' "
                                      "hii_halpha_luminosity (acceptance row 35)"),
    "nii_halpha_gradient_hii": ("nebular", "the HII-region census",
                                "nebular.nii_halpha_gradient, over the [N II] ring light below (acceptance row 37)"),
    **{f"{line}_surface_brightness_hii": ("nebular", "the HII-region census",
                                          "nebular.compute_nebular: the ring's Halpha times nebular.ring_ratios - the "
                                          "regions' line ratio weighted by their Halpha, binned by cluster_radius")
       for line in ("oiii_5007", "nii_6583", "sii_6716", "sii_6731")},
    "hot_phase_porosity": ("bubbles", "the clusters' bubbles (with the remnants, which no placement moves)",
                           "bubbles.hot_phase_porosity: the realised bubbles' volumes, binned by cluster_radius"),
}
assert len(CENSUS_STATISTICS) == 14  # nine scalars, five radial fields: the fourteen measured at S55, minus nothing
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


# --- the reference: the layer off is S55's layer off --------------------------------------------------------------

# The fields of a layer-off run that are not S55's bits, by name: **a closed list** (D215, the lead's reading 3).
# `arm_multiplicity` was the drawn arm number (4 for both templates) and is the derived dominant one - the mode
# carrying the most mass-weighted power: 3 for the Milky Way, 2 for ngc_4414. Nothing else of S55 moved.
LAYER_OFF_EXCEPTIONS = {"arm_multiplicity": {"milky_way": (4.0, 3.0), "ngc_4414": (4.0, 2.0)}}
# And the fields P1 adds, which S55 did not publish: the law's five amplitudes and its saturation, radial and the
# same on and off; the layer's five phases, not numbers with the layer off.
ADDED_AT_S56 = {*pt.AMPLITUDE_FIELDS, "arm_saturation", *pt.PHASE_FIELDS}


@pytest.mark.parametrize("template", layer_reference.TEMPLATES)
@pytest.mark.parametrize("name", MODELS)
def test_layer_off_every_field_is_the_s55_reference_bit_for_bit_but_the_named_list(runs, reference, prod, name, template):
    """D215: "every field that exists in both is bit-identical layer-off, except a closed, named list". The reference
    is sha256 of every field's bytes of S55's layer-off run, captured before P1's model code moved; nothing is
    re-pinned here - a field that moves joins the named list by a decision, or the phase stops (BUILD_III 3d)."""
    out = runs[name, False] if template == "milky_way" else run(prod[0].get(name), layer_reference.template_inputs(template), layer=False)
    held = reference["fields"][layer_reference.label(name, template)]
    now = {n: layer_reference.value_digest(v) for n, v in out.fields.items()}
    assert not set(held) - set(now), sorted(set(held) - set(now))  # no field was lost
    moved = {n for n in held if now[n] != held[n]}
    assert moved == set(LAYER_OFF_EXCEPTIONS), sorted(moved ^ set(LAYER_OFF_EXCEPTIONS))
    for n, by_template in LAYER_OFF_EXCEPTIONS.items():
        was, is_now = by_template[template]
        assert held[n] == layer_reference.value_digest(was) and out.fields[n] == is_now, (n, template)
    assert set(now) - set(held) == ADDED_AT_S56 and len(held) == (332 if name == "azimuthal" else 331)
    for n in pt.PHASE_FIELDS:
        assert np.isnan(out.fields[n]), n
    if template == "ngc_4414":
        assert out.inputs["texture_seed"] == 4414


def test_layer_off_every_route_s_arrays_and_header_are_the_s55_reference(reference):
    """Every input route asked with ``layer=off``, a window and the whole disc, both models and a template: each
    array of the body is the reference's bytes in the reference's order, and the header is the reference's less
    ``stages`` (what a request ran depends on what the service already held). A census placed by no pattern is the
    census S55 placed by no pattern, object for object."""
    made = layer_reference.routes_digest()
    assert set(made) == set(reference["routes"]) and len(made) == 42
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
    """I1 as amended at gate G1, walked from the declarations: a field is composed because it says so, and what it
    says is the value it must be with the layer off. Nothing here reads an axis."""
    on, off = runs[name, True], runs[name, False]
    assert set(on.fields) == set(off.fields) and on.order == off.order  # the same model ran, every stage of it
    composed = {n: d for n, d in on.decls.items() if d.composed}
    assert set(composed) == {"pattern_density_contrast", "gas_density_contrast"} | ({"sfr_modulation"} if name == "azimuthal" else set())
    for n, d in composed.items():
        # Exactly its declared neutral everywhere with the layer off - the number, not that number to rounding -
        # and not everywhere its neutral with the layer on: the layer does place.
        assert isinstance(d.neutral, float) and d.neutral == 1.0, n
        assert np.all(np.asarray(off.fields[n]) == d.neutral), n
        assert not np.all(np.asarray(on.fields[n]) == d.neutral), n

    moved_statistics = set()
    for n, d in on.decls.items():
        if d.composed:
            continue
        # Every field that does not declare itself composed is held to bit-identity, whatever its axes: a field
        # over phi tabulated in a pattern's own frame (P2, P3) will be physics, and is not exempt.
        if d.kind.domain == "object":
            # A catalogue's own columns. A census that no pattern places is the same census, bit for bit. One that
            # a pattern places is another draw with the layer off - other counts per cell, so other objects - and
            # **no per-object on/off assertion is made, here or anywhere** (gate G1, Q6: "with different realised
            # counts the objects do not correspond"). What is asserted of those censuses is I2 (the expected counts
            # per ring) and the statistics computed from them, below.
            if d.of in UNPLACED_OBJECTS:
                assert same(on.fields[n], off.fields[n]), n
            else:
                assert d.of in PLACED_OBJECTS, (n, d.of)
            continue
        if d.provenance == "synthetic":
            # S56 (D215, gate ruling 5): a synthetic scalar is a realisation - a number with the layer on, and not
            # one with it off ("an unrealised quantity is NaN ... 0 would claim a draw that was not made"). The five
            # arm modes' phases are the only ones; the layer's other fields are a census's columns, above.
            assert n in pt.PHASE_FIELDS and d.kind.domain == "galaxy", n
            assert np.isnan(off.fields[n]) and 0.0 <= on.fields[n] < 2.0 * np.pi, n
            continue
        if not same(on.fields[n], off.fields[n]):
            moved_statistics.add(n)
    # Every other field - every radial field, every history, every scalar - is the bit it was, but for the list.
    assert moved_statistics <= set(CENSUS_STATISTICS), sorted(moved_statistics - set(CENSUS_STATISTICS))
    # And the list is not padded: each entry does move on the production grid at the default seeds.
    assert moved_statistics == set(CENSUS_STATISTICS), sorted(set(CENSUS_STATISTICS) - moved_statistics)
    # Each entry says which stage publishes it, and that stage is where the model publishes it.
    producer = {d.name: sid for sid in on.order for d in production()[1].get(sid).publishes}
    for n, (stage_id, census, where) in CENSUS_STATISTICS.items():
        assert producer[n] == stage_id and census and where.startswith(("systems.", "planets.", "bright.", "clouds.", "nebular.", "bubbles.")), n
        assert on.decls[n].kind.domain in ("galaxy", "grid") and on.decls[n].axes in ((), ("R",)), n
    assert sum(1 for n in CENSUS_STATISTICS if on.decls[n].kind.domain == "galaxy") == 9


def test_i1_holds_an_undeclared_phi_field_to_bit_identity_and_a_declared_one_to_its_neutral(prod):
    """The case the axes rule got wrong (gate G1, F12): a phi-axis field that is physics - tabulated in a pattern's
    own frame, P2's and P3's - is not composed, and is the same bits with the layer on or off; and a composed field
    need not be 1 when the layer is off: it is whatever its declaration says."""
    def physics(ctx):
        return {"frame_field": np.cos(ctx.grid.phi)[None, :] * (1.0 + ctx.grid.R)[:, None]}

    def composing(ctx):
        cells = (ctx.grid.R.size, ctx.grid.phi.size)
        return {"placed_field": compose.field(ctx.fields, PLACED, cells, lambda: 2.0 + np.sin(ctx.grid.phi)[None, :] * np.ones(cells))}

    PLACED = decl("placed_field", axes=("R", "phi"), composed=True, neutral=2.0)
    frame = decl("frame_field", axes=("R", "phi"))
    assert not frame.composed and frame.neutral is None and PLACED.composed and PLACED.neutral == 2.0
    a, b = stage("frame", (frame,), compute=physics), stage("placing", (PLACED,), compute=composing)
    assert not a.composes and not a.may_place and b.composes
    m, table = model("m", a, b), production()[2]
    on = run(m, grid=SMALL, impls=impls(a, b), table=table, layer=True)
    off = run(m, grid=SMALL, impls=impls(a, b), table=table, layer=False)
    assert same(on.fields["frame_field"], off.fields["frame_field"]) and np.ptp(on.fields["frame_field"]) > 0
    assert np.all(off.fields["placed_field"] == 2.0) and not np.all(on.fields["placed_field"] == 2.0)
    # A stage cannot compose a field that does not declare it: compose refuses, layer on or off (the stage is given
    # a census's standing here so that it is the declaration compose refuses, not the stage).
    undeclared = stage("frame", (frame,), placement_reader=True,
                       compute=lambda ctx: {"frame_field": compose.field(ctx.fields, frame, (1,), lambda: np.ones(1))})
    for layer in (True, False):
        with pytest.raises(LayerError, match="not declared composed"):
            run(model("m", undeclared), grid=SMALL, impls=impls(undeclared), table=table, layer=layer)


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
    # S56 (D215, gate ruling 5): and the law of several modes - the five amplitudes and the saturation, radial
    # fields of the pattern stage - is the same bits: "with the layer off the texture_seed stream is never drawn,
    # and the five amplitudes, arm_multiplicity and arm_saturation are bit-identical".
    radial = [d.name for d in impls_.get("pattern").publishes if d.axes == ("R",)]
    assert radial == [*pt.AMPLITUDE_FIELDS, "arm_saturation"]
    for n in radial:
        assert same(on.fields[n], off.fields[n]) and np.all(np.isfinite(on.fields[n])), n


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
    weights = sy._sector_weights(R, compose.stellar_pattern(F, R))
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
    # S56 (D215): was n_on == 16822 - S51's census, placed by one four-armed ridge; placed by five modes' ridge it
    # is another draw. The layer-off census is S55's own (16 754), and the two still differ by the draw alone.
    assert n_on == 16765 and n_off == 16754 and abs(n_off / 16822 - 1.0) < 0.03 and abs(n_on / n_off - 1.0) < 0.03, (n_on, n_off)


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
        # The layer-on census's readings, for the record and not judged (I3). S56 (D215): were -1.98926 and
        # -0.105511 on S51's census; the census placed by five modes is another draw.
        assert float(on["hii_luminosity_function_slope"]) == pytest.approx(-2.07374, abs=1e-5)
        assert float(on["nii_halpha_gradient_hii"]) == pytest.approx(-0.105544, abs=1e-6)
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
        assert g.layer_stages == ("arm_phases", "cloud_texture")  # S56 (D215): was the cloud texture alone
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
        # S56 (D215): was "layer stages: cloud_texture" and a line "input unread by ruling: texture_seed".
        assert "layer stages: arm_phases, cloud_texture" in report and "unread by ruling" not in report
        assert "texture_seed@3" in report and "inputs unbound: 0" in report


def binning_stages(g) -> set[str]:
    """The physics stages a placement reaches through the realised catalogues, read from the graph: a stage that is
    neither a placement reader, a composing stage nor a layer stage, and requires a catalogue column a placement
    reader or a layer stage publishes - or a field of a stage that does."""
    carried = {d.name for st in g.order if st.placement_reader or st.layer_stage for d in st.publishes
               if d.kind.domain == "object" or d.provenance == "synthetic"}
    found: set[str] = set()
    for st in g.order:
        if not st.may_place and any(n in carried for n in st.requires + st.requires_optional):
            found.add(st.id)
            carried |= set(st.published_names)
    return found


# The physics stages that bin realised objects (I4 as amended at gate G1, change 7): **a closed list**. Each reads
# `cluster_radius`, which carries the layer's synthetic source offset, and bins by it - `nebular` the regions' line
# ratios per ring (nebular.ring_ratios), `bubbles` the bubbles' volumes per ring (bubbles.hot_phase_porosity). What
# they publish from that is in CENSUS_STATISTICS. A third stage appearing here fails the test below: from L1 what
# they bin per ring does not depend on placement, and until then no new physics may be built on a placed catalogue.
BINNING_STAGES = {"nebular", "bubbles"}


def test_i4_the_stages_that_bin_realised_objects_are_a_closed_list(prod):
    """Placement reaches physics through the realised catalogues, and the graph's field check cannot see it: a
    cluster's radius is a seeded column of a placement reader. So the transitive case is held by name, derived from
    the code: who requires a placed catalogue's column without being a reader."""
    models, impls_, table = prod
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert binning_stages(g) == BINNING_STAGES, sorted(binning_stages(g) ^ BINNING_STAGES)
        stages = {st.id: st for st in g.order}
        clusters = stages["clusters"]
        # The column that carries the offset: a placement reader's, drawn from the layer's synthetic columns.
        assert clusters.placement_reader and "cluster_radius" in clusters.published_names
        assert {"cloud_source_offset", "cloud_source_angle"} <= set(clusters.requires)
        assert g.provenance["cloud_source_offset"] == "synthetic" and g.provenance["cluster_radius"] == "seeded"
        readers = {st.id for st in g.order if "cluster_radius" in st.requires + st.requires_optional}
        assert readers == BINNING_STAGES
        for sid in BINNING_STAGES:
            st = stages[sid]
            assert not st.placement_reader and not st.composes and not st.layer_stage and not st.may_place, sid
            # No composed and no synthetic field among what it requires: the graph's own check passes it.
            for n in st.requires + st.requires_optional:
                d = next(d for s in g.order for d in s.publishes if d.name == n)
                assert not d.composed and d.provenance != "synthetic", (sid, n)
        # And what they publish from the binned objects is what the closed list of census statistics names.
        binned = {n for n, (sid, _, _) in CENSUS_STATISTICS.items() if sid in BINNING_STAGES}
        assert len(binned) == 8 and all(g.producer[n] in BINNING_STAGES for n in binned)
    # The derivation sees a third one: a physics stage that reads a cluster column is found.
    m = models.get(DEFAULT_MODEL)
    third = stage("ring_sums", (decl("cluster_ring_mass", provenance="seeded"),), requires=("cluster_radius", "cluster_mass"),
                  checkpoint=5)
    widened = {**{st.id: st for st in impls_}, "ring_sums": third}
    wider = replace(m, stages=(*m.stages, ("ring_sums", "ring_sums")))
    g = graph.analyse(wider, widened, table)
    assert g.ok and binning_stages(g) == BINNING_STAGES | {"ring_sums"}


def test_i4_the_graph_refuses_a_physics_stage_that_requires_a_composed_field():
    contrast = decl("contrast", axes=("R", "phi"), composed=True, neutral=1.0)
    assert contrast.composed and not decl("profile").composed
    # Declared, not read off the axes (gate G1, change 3): a phi-axis field that does not declare itself composed
    # is physics, and a physics stage may require it.
    in_frame = decl("in_frame", axes=("R", "phi"))
    tabulated, reads_it = stage("tabulated", (in_frame,)), stage("physics", ("g",), requires=("in_frame",))
    assert not in_frame.composed and not tabulated.composes
    assert graph.check([model("m", tabulated, reads_it)], impls(tabulated, reads_it), INPUTS) == []
    composer = stage("composer", (contrast,))
    physics = stage("physics", ("g",), requires=("contrast",))
    m = model("m", composer, physics)
    problems = graph.check([m], impls(composer, physics), INPUTS)
    assert [p.code for p in problems] == ["layer-reader"]
    assert "'physics'" in problems[0].detail and "'contrast'" in problems[0].detail and "invariant I4" in problems[0].detail
    # An optional requirement is a requirement.
    optional = decl("contrast", axes=("R", "phi"), optional=True, composed=True, neutral=1.0)
    po, optional_reader = stage("composer", (optional,)), stage("physics", ("g",), requires_optional=("contrast",))
    assert [p.code for p in graph.check([model("m", po, optional_reader)], impls(po, optional_reader), INPUTS)] == ["layer-reader"]
    # A declared placement reader may, and so may a stage that composes a field of its own from it.
    reader = stage("physics", ("g",), requires=("contrast",), placement_reader=True)
    assert graph.check([model("m", composer, reader)], impls(composer, reader), INPUTS) == []
    second = stage("physics", (decl("g", axes=("R", "phi"), composed=True, neutral=1.0),), requires=("contrast",))
    assert second.composes and graph.check([model("m", composer, second)], impls(composer, second), INPUTS) == []
    # Publishing a field over phi without declaring it composed lends no such right.
    undeclared = stage("physics", (decl("g", axes=("R", "phi")),), requires=("contrast",))
    assert not undeclared.composes
    assert [p.code for p in graph.check([model("m", composer, undeclared)], impls(composer, undeclared), INPUTS)] == ["layer-reader"]


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
    """A pattern object is rebuilt from published fields, not read as a composed field. So the stage's own view of
    the fields says whether it may ask, and ``compose`` refuses one that may not.

    S56 (D215): until S56 the graph could not see these two - a pattern was rebuilt from seeded scalars (the drawn
    arm number among them), so ``graph.check`` was empty and only ``compose`` caught them. A pattern is built from
    the layer's phases now, synthetic fields, so the graph refuses them too; the run-time refusal is unchanged and
    is still the one that stops the run (a layer-reader problem is reported, not fatal to building the graph)."""
    models, impls_, table = prod
    m = models.get(DEFAULT_MODEL)
    for stage_id in ("clouds", "planets"):
        undeclared = {st.id: st for st in impls_}
        undeclared[stage_id] = replace(impls_.get(stage_id), placement_reader=False)
        problems = graph.check([m], undeclared, table)
        assert {p.code for p in problems} == {"layer-reader"} and len(problems) == len(pt.PHASE_FIELDS)
        assert all(f"'{stage_id}'" in p.detail and "synthetic" in p.detail for p in problems)
        assert {n for n in pt.PHASE_FIELDS if any(f"'{n}'" in p.detail for p in problems)} == set(pt.PHASE_FIELDS)
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
    """The contract the viewer builds against: the composed fields at their neutral, the cloud texture columns 0, the
    cloud interior's three parameters in the header either way, the render's frame even round each ring."""
    svc = Service(grid=SMALL)
    on_h, on = svc.handle("/api/clouds", SECTOR).frame()
    off_h, off = svc.handle("/api/clouds", SECTOR + "&layer=off").frame()
    for header in (on_h, off_h):
        assert header["cloud_interior"] == {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
        assert not [k for k in header["scalars"] if "interior" in k]
        assert header["columns"] == list(cl.WIRE_COLUMNS)
    assert len(off["cloud_radius"]) > 20
    for name in cl.TEXTURE_COLUMNS:
        assert np.all(off[name] == 0.0) and np.any(on[name] != 0.0), name


# The render's components, by what each keeps ring by ring between the layer on and off (gate G1, change 10: "each
# ring keeps its light" is every component's claim, not the stars' alone). Measured at S55 on the small and the
# production grid through two filter sets: every component but one is the same ring total to 1.1e-14, the per-ring
# ones to the bit. The one is `lines_hii`, summed from the HII regions' four forbidden lines' ring light - the four
# radial fields CENSUS_STATISTICS names, a sum over realised regions - and it is a census statistic in the render
# too: up to a factor of six in a thinly populated ring on the production grid.
RENDER_PLACED = ("stars", "stars_unresolved", "halpha_hii", "dust_scattered", "dust_placement")  # (R, phi, ...)
RENDER_PER_RING = ("halpha_dig", "lines_dig", "dust_extinction", "dust_thermal", "dust_height")  # (R, ...)
RENDER_CENSUS_STATISTICS = ("lines_hii",)
WIDE = json.dumps([{"name": "optical", "shape": "box", "centre": 5500.0, "width": 4000.0},
                   {"name": "far_infrared", "shape": "box", "centre": 1.0e6, "width": 1.0e6}])


@pytest.mark.parametrize("curves", [B_V, WIDE], ids=["B and V", "optical and far infrared"])
def test_i5_every_component_of_the_render_keeps_its_ring_or_is_a_named_census_statistic(curves):
    svc = Service(grid=SMALL)
    q = {"filters": [curves], "l_min": ["1000"]}  # l_min: the unresolved remainder is a component too
    on_h, on = svc.handle("/api/render", q).frame()
    off_h, off = svc.handle("/api/render", {**q, "layer": ["off"]}).frame()
    assert (on_h["layer"], off_h["layer"]) == ("on", "off") and list(on) == list(off)
    # Every array of the response is in exactly one of the three groups: a new component must be placed in one.
    assert set(on) == {*RENDER_PLACED, *RENDER_PER_RING, *RENDER_CENSUS_STATISTICS}

    def rings(arrays, name):
        return np.asarray(arrays[name], dtype=float).sum(axis=1)

    for name in RENDER_PLACED:
        assert on_h["axes"][name][:2] == ["R", "phi"], name
        # Layer off: even round the ring - every cell holds its ring's own value. Layer on: it is placed.
        cell = off[name][:, :1]
        assert np.all(off[name] == cell) and not np.all(on[name] == on[name][:, :1]), name
        # And each ring keeps its total, to rounding: the placement averages to 1 round every ring.
        assert np.allclose(rings(on, name), rings(off, name), rtol=1e-12, atol=0.0), name
    assert np.all(off["dust_placement"] == 1.0)
    for name in RENDER_PER_RING:
        assert on_h["axes"][name][0] == "R" and "phi" not in on_h["axes"][name], name
        assert same(on[name], off[name]), name  # a ring's own value, the same bits either way
    for name in RENDER_CENSUS_STATISTICS:
        # Not conserved ring by ring, and said so: the regions the ring's line light is summed over are another
        # draw. Even round the ring all the same, and the Halpha it is built on (halpha_hii, above) is conserved.
        assert np.all(off[name] == off[name][:, :1]), name
        a, b = rings(on, name), rings(off, name)
        assert not np.allclose(a, b, rtol=1e-3, atol=0.0), name
        assert on_h["components"][name]["fields"][:4] == [f"{line}_surface_brightness_hii" for line in ("hbeta", "oiii_5007", "nii_6583", "sii_6716")]
        assert {f for f in on_h["components"][name]["fields"] if f in CENSUS_STATISTICS} == {
            f"{line}_surface_brightness_hii" for line in ("oiii_5007", "nii_6583", "sii_6716", "sii_6731")}
    # The frame: every conserving component's light, summed over the disc with the bulge, is the same to rounding.
    for name in ("stars", "stars_unresolved", "halpha_hii", "dust_scattered"):
        total_on = checks.frame_total(on_h, {**on, "stars": on[name]})
        total_off = checks.frame_total(off_h, {**off, "stars": off[name]})
        assert np.allclose(total_on, total_off, rtol=1e-12, atol=0.0), name
    # What the header says of a placement is true of this response (gate G1, change 11).
    for name in ("stars", "stars_unresolved", "halpha_hii", "lines_hii"):
        assert "layer is off" in off_h["components"][name]["about"] and "neutral value, 1" in off_h["components"][name]["about"], name
        assert "layer is off" not in on_h["components"][name]["about"], name
    placed = off_h["placement"]["arrays"]["dust_placement"]["about"]
    assert "layer is off" in placed and "layer is off" not in on_h["placement"]["arrays"]["dust_placement"]["about"]


def test_i5_the_metadata_names_the_fourth_kind_and_the_fifth_seed(model):
    svc = Service(grid=SMALL)
    fields = svc.handle("/api/fields", f"model={model.name}").json()["fields"]
    assert {f["provenance"] for f in fields} == set(PROVENANCE) == {"derived", "seeded", "synthetic"}
    synthetic = [f for f in fields if f["provenance"] == "synthetic"]
    # The four cloud columns and, since S56 (D215), the five arm modes' phases, and nothing else: the interior's three
    # numbers are constants, not fields (G1, change 4).
    assert {f["name"] for f in synthetic} == set(cl.TEXTURE_COLUMNS) | set(pt.PHASE_FIELDS)
    assert not [f["name"] for f in fields if "cloud_interior" in f["name"]]
    for f in fields:
        if f["provenance"] == "synthetic":
            assert all(isinstance(f[k], str) and f[k].strip() for k in SYNTHETIC_DECLARATIONS), f["name"]
            if f["name"] in pt.PHASE_FIELDS:
                # The first field on the layer's own seed. Its statistic is stated as what it is - a uniform phase
                # by the disc's symmetry, the absence of a measured preference - and claims no source.
                assert f["stage"] == "arm_phases" and f["kind"] == "scalar" and "texture seed" in f["about"], f["name"]
                assert "Uniform on the circle" in f["statistic"] and "[inferred]" in f["statistic"], f["name"]
                assert not re.search(r"none read", f["statistic"], re.IGNORECASE), f["name"]
                continue
            assert f["stage"] == "cloud_texture" and re.search(r"none read \(#95\)", f["statistic"]), f["name"]
            # Which seed, in each of the four (G1, change 6).
            assert "Drawn on `systems_seed`, the stream Phase R keeps; on `texture_seed` from L1." in f["about"], f["name"]
        else:
            assert not set(SYNTHETIC_DECLARATIONS) & set(f), f["name"]
    # A composed field says so, with its neutral value; no other entry carries either key (G1, change 3).
    composed = {f["name"]: f for f in fields if "composed" in f or "neutral" in f}
    assert set(composed) == {"pattern_density_contrast", "gas_density_contrast"} | ({"sfr_modulation"} if model.name == "azimuthal" else set())
    for name, f in composed.items():
        assert f["composed"] is True and f["neutral"] == 1.0 and f["provenance"] == "seeded", name
        assert "A composed field: with the randomness layer off it is 1 everywhere" in f["about"], name
        assert f["stage"] in ("pattern", "gas_pattern", "sfh_azimuthal")  # a composing stage lives in stages/, not layer/
    seeds_ = svc.handle("/api/inputs", f"model={model.name}").json()["seeds"]
    assert [s["name"] for s in seeds_] == [s.name for s in seeds()] and len(seeds_) == 5
    texture = next(s for s in seeds_ if s["name"] == "texture_seed")
    assert texture["default"] == 0 and texture["checkpoint"] == 3 and "P1" in texture["about"]
    published = {t["name"]: t["inputs"]["seeds"]["texture_seed"] for t in svc.handle("/api/templates").json()["templates"]}
    assert published == {"milky_way": 0, "ngc_4414": 4414}
    stages = svc.handle("/api/stages", f"model={model.name}").json()
    assert "cloud_texture" in stages["order"] and stages["order"].index("clouds") < stages["order"].index("cloud_texture") < stages["order"].index("clusters")
    assert stages["order"].index("arm_phases") < stages["order"].index("pattern")  # S56: the phases, then the field


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
    # 342: S54's 331 fields, name for name (334 while the interior's three numbers were scalars, before gate G1),
    # and S56's eleven (D215): five amplitudes, the saturation, five phases.
    assert len(columns) > 100 and len(b.fields) == 342


def test_the_oracle_against_layer_on_basic_holds_outside_the_censuses(runs):
    """The second comparison D214 names: layer-off ``azimuthal`` against layer-on ``basic``, the fields not declared
    composed. It holds on every radial field, history and scalar that is not a census statistic - 215 fields, bit
    for bit. It does not hold on the catalogues' columns or the census statistics, and cannot: layer-on ``basic``
    places its censuses by the pattern. Those are exactly the fields I1 lets move, in ``basic`` itself (test_i1) -
    I1's list again, and not an independent check (D214, the predictions as read)."""
    a, b = runs["azimuthal", False], runs["basic", True]
    differ = {n for n, d in b.decls.items() if not d.composed and not same(a.fields[n], b.fields[n])}
    # S56 (D215): the layer's five phases are numbers in the layer-on run and not in the layer-off one.
    phases = {n for n in differ if b.decls[n].provenance == "synthetic" and b.decls[n].kind.domain == "galaxy"}
    assert phases == set(pt.PHASE_FIELDS)
    statistics = {n for n in differ - phases if b.decls[n].kind.domain != "object"}
    assert statistics == set(CENSUS_STATISTICS)
    assert {b.decls[n].of for n in differ - statistics - phases} == PLACED_OBJECTS
    held = [n for n, d in b.decls.items() if not d.composed and n not in differ]
    # 221 = basic's 342 fields less its 2 composed ones, the 100 placed columns, the 14 census statistics and the
    # 5 phases (215 until S56, which added the law's five amplitudes and its saturation to what is held).
    assert len(held) == 221 and all(b.decls[n].of in (None, *UNPLACED_OBJECTS) for n in held)


def test_the_oracle_holds_layer_off_on_a_small_grid_and_another_seed(prod):
    models = prod[0]
    given = {"systems_seed": 5, "pattern_seed": 2, "halo_mass": 8e11}
    a = run(models.get("azimuthal"), given, SMALL, layer=False)
    b = run(models.get("basic"), given, SMALL, layer=False)
    assert [n for n in b.fields if not same(a.fields[n], b.fields[n])] == []


# --- Appendix B applied: the four cloud columns, the cloud interior's noise ----------------------------------------


@pytest.mark.parametrize("name", MODELS)
def test_the_cloud_texture_columns_are_drawn_on_the_streams_they_always_were(runs, prod, name):
    """Layer on: the stage's four columns are what a census materialised whole carries, and the draws keep their
    seed, their stream paths and their arithmetic - each cell's own stream ``(systems_seed, "cloud", cell, name)``.

    S56 (D215): until S56 this test held the four columns to S54's reference digest, bit for bit (Phase R moved the
    draws' publisher and no value). The layer-on census is another draw since P1 - the clouds follow five arm
    modes, so each cell holds another count - and a digest of it is no longer a statement; what Phase R promised
    of these columns is their streams, and that is read here directly."""
    on = runs[name, True]
    for column in cl.TEXTURE_COLUMNS:
        assert on.decls[column].provenance == "synthetic" and on.decls[column].of == "cloud"
    m = prod[0].get(name)
    seed = int(on.inputs["systems_seed"])
    counts = cl.cloud_counts(cl.expected_counts(on.fields, on.grid.R, constants(m)), seed)
    assert sum(k for _, k in counts) == len(on.fields["cloud_size"])
    start = 0
    for cell, k in counts[:40]:
        size = np.asarray(on.fields["cloud_size"])[start:start + k]
        want = {
            "cloud_source_offset": size * np.cbrt(_seeds.rng(seed, "cloud", cell, "source_offset").random(k)),
            "cloud_source_angle": 2.0 * np.pi * _seeds.rng(seed, "cloud", cell, "source_angle").random(k),
            "cloud_density_gradient": _seeds.rng(seed, "cloud", cell, "gradient").random(k),
            "cloud_gradient_angle": 2.0 * np.pi * _seeds.rng(seed, "cloud", cell, "gradient_angle").random(k),
        }
        for column, values in want.items():
            assert same(np.asarray(on.fields[column])[start:start + k], values), (cell, column)
        start += k
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


def test_the_offset_s_declaration_states_what_it_does_not_keep_and_the_numbers_are_the_model_s(runs):
    """Gate G1, change 5 (BUILD_III section 1c rule 2 as amended: "a declaration states what it does not keep, with
    the measured number"). The source's offset and direction place the cluster, and a cluster can leave its cloud's
    ring. The declaration's numbers are measured here on the production grid at the default inputs, the layer on -
    so the text cannot drift from the model. No clamp: nothing here changes a value."""
    on = runs[DEFAULT_MODEL, True]
    F, R = on.fields, on.grid.R
    offset_decl, angle_decl = on.decls["cloud_source_offset"], on.decls["cloud_source_angle"]
    text = offset_decl.conserves
    assert text == angle_decl.conserves and text.startswith("The cloud's mass and the cluster's mass: the column places, it does not weigh.")
    # S56 (D215): were "1 610 of 12 930 clusters (12.5 %, 43.7 % of the cluster mass)" and "157 in another cell ring",
    # measured on S51's census at S55; the layer-on census is another draw since P1 and the declaration was re-read.
    for phrase in ("at S56 the offset moves a cluster",
                   "by up to 249 pc in radius (its own length reaches 265 pc) against a 75 pc radial step",
                   "1 581 of 12 910 clusters (12.2 %, 41.9 % of the cluster mass)",
                   "144 in another cell ring", "`nebular` and `bubbles` bin from it", "#95; L1 decides"):
        assert phrase in text, phrase
    # The two gradient columns lean a cloud's density and place nothing outside it: they keep their declaration.
    for name in ("cloud_density_gradient", "cloud_gradient_angle"):
        assert on.decls[name].conserves.startswith("The cloud's mass and the census's count") and "249 pc" not in on.decls[name].conserves
    hosts = np.asarray(F["cloud_cluster_index"]) >= 0
    cloud_r, cluster_r = np.asarray(F["cloud_radius"])[hosts], np.asarray(F["cluster_radius"])
    mass = np.asarray(F["cluster_mass"])
    step = float(R[1] - R[0])
    assert step * 1000.0 == pytest.approx(75.0) and cluster_r.size == 12910  # S56 (D215): was 12930
    # "another radial ring": the grid ring whose centre is nearest, the cluster's against its cloud's.
    ring = lambda r: np.floor((r - R[0]) / step + 0.5).astype(int)  # noqa: E731
    moved = ring(cloud_r) != ring(cluster_r)
    assert int(moved.sum()) == 1581 and moved.mean() == pytest.approx(0.1225, abs=5e-4)  # S56 (D215): was 1610, 0.125
    # The share of the cluster mass that crosses: 0.41915, printed as 41.9 %. S56 (D215): was 0.43747 (43.7 %; the
    # gate's text carried the review's 43.8).
    assert mass[moved].sum() / mass.sum() == pytest.approx(0.4192, abs=5e-4)
    edges, _ = sy.cell_edges(R)
    # S56 (D215): was 157
    assert int((np.searchsorted(edges, cloud_r, side="right") != np.searchsorted(edges, cluster_r, side="right")).sum()) == 144
    # 249 pc is the largest radial displacement of a cluster from its cloud; the offset's own length reaches 265 pc
    # (it is not all radial), and it is the radial part that crosses rings. The gate's text said "the offset reaches
    # 249 pc"; the declaration says which of the two each number is (D214, the close).
    assert np.abs(cluster_r - cloud_r).max() * 1000.0 == pytest.approx(248.5, abs=0.1)
    assert np.asarray(F["cloud_source_offset"]).max() == pytest.approx(265.2, abs=0.1)


def test_the_cloud_interior_s_noise_is_three_constants_of_the_model(runs, prod):
    """D214 section 5 as ruled at gate G1 (change 4): "the three interior scalars are not synthetic. A constant 4, 2,
    0.5, the same on and off, is not 'a realisation from the layer's seed'. They are parameters of a synthetic
    function and are published as constants of the model ... not as fields of any stage". Three level-0 constants,
    declared by the layer's stage, carried by /api/clouds' header as ``cloud_interior`` - the one constant this API
    serves, by the gate's explicit exception (rule D5 as amended: a parameter of a function the viewer evaluates)."""
    models, impls_, _ = prod
    names = dict(cloud_texture.INTERIOR_CONSTANTS)
    assert names == {"octaves": "CLOUD_INTERIOR_OCTAVES", "lacunarity": "CLOUD_INTERIOR_LACUNARITY", "gain": "CLOUD_INTERIOR_GAIN"}
    for m in models:
        c = constants(m)
        assert cloud_texture.interior(c) == {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
        assert isinstance(cloud_texture.interior(c)["octaves"], int)
        for constant in names.values():
            about = m.constants[constant].about
            assert "The viewer's own choice, none read, #110" in about and "[verified: frontend/src/galaxy/region.ts at tag s54" in about
        # Declared by the layer's stage and by no other; not a field of any stage, in either run.
        readers = sorted(sid for _, sid in m.stages if set(names.values()) & set(impls_.get(sid).reads_constants))
        assert readers == ["cloud_texture"] and set(names.values()) <= set(impls_.get("cloud_texture").reads_constants)
    for out in runs.values():
        assert not [n for n in out.fields if "cloud_interior" in n]
    assert [d.name for d in impls_.get("cloud_texture").publishes] == list(cl.TEXTURE_COLUMNS)
    # A parameter set that is not a noise is refused where it is read.
    good = constants(models.get(DEFAULT_MODEL))
    for constant, bad in (("CLOUD_INTERIOR_OCTAVES", 0), ("CLOUD_INTERIOR_OCTAVES", 2.5), ("CLOUD_INTERIOR_LACUNARITY", 0.0),
                          ("CLOUD_INTERIOR_GAIN", float("nan"))):
        with pytest.raises(ValueError, match="cloud-interior noise"):
            cloud_texture.interior({**good, constant: bad})
    # The API: the exception is this one key of this one route, by the wire's names; no constant's name is served,
    # and no other response carries the key.
    svc = Service(grid=SMALL)
    for query in (SECTOR, SECTOR + "&layer=off", "model=basic&" + SECTOR):
        header = svc.handle("/api/clouds", query).frame()[0]
        assert header["cloud_interior"] == {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
        assert set(header["scalars"]) == {"cloud_count_total", "cloud_forcing_parameter", "cloud_lifetime", "cloud_extinction_v"}
        assert not re.search(r"CLOUD_INTERIOR", json.dumps(header))
    for path in INPUT_ROUTES:
        if path != "/api/clouds":
            assert "cloud_interior" not in svc.handle(path, QUERIES[path]).frame()[0], path
    for path in ("/api", "/api/fields", "/api/stages", "/api/inputs", "/api/templates"):
        text = svc.handle(path).body.decode("utf-8")
        assert "CLOUD_INTERIOR" not in text and '"constants"' not in text, path
    source = (ROOT / "frontend" / "src" / "galaxy" / "region.ts").read_text(encoding="utf-8")
    # Since builder D (S55) the viewer holds none of the three: it evaluates the interior with what the clouds'
    # header publishes, and keeps one measured normaliser with the parameter set it was measured for. The guard
    # therefore runs the other way round: the viewer names no octave count of its own, and the set its measured
    # constant belongs to is the layer's.
    assert "export const OCTAVES" not in source
    m = re.search(r"measuredFor: \{ octaves: (\d+), lacunarity: ([\d.]+), gain: ([\d.]+) \}", source)
    assert m, "region.ts no longer records which parameters its measured normaliser belongs to"
    interior = cloud_texture.interior(good)  # the model's constants: what the measured normaliser must belong to
    assert (float(m[1]), float(m[2]), float(m[3])) == (interior["octaves"], interior["lacunarity"], interior["gain"])


def test_a_synthetic_field_declares_what_it_stands_in_for_what_it_conserves_and_its_statistic():
    base = dict(name="f", label="f", unit="dimensionless", kind=Kind.FIELD, axes=("R",), ramp=Ramp("greys"), about="a test field")
    ok = FieldDecl(**base, **SYNTHETIC)
    assert ok.provenance == "synthetic" and ok.contract()[-5:-2] == ("a physics", "a total", "none read (#95)")
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


def test_a_composed_field_declares_itself_and_its_neutral_value():
    """Gate G1, change 3: composed is a declaration with its neutral value, the two refused apart, and nothing is
    read off the axes - a field over phi is not composed unless it says so, and a composed one need not be over phi."""
    over_phi = dict(name="f", label="f", unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"), ramp=Ramp("greys"), about="a test field")
    plain = FieldDecl(**over_phi)
    assert plain.composed is False and plain.neutral is None and plain.contract()[-2:] == (False, None)
    declared = FieldDecl(**over_phi, composed=True, neutral=1)
    assert declared.composed is True and declared.neutral == 1.0 and isinstance(declared.neutral, float)
    assert declared.contract()[-2:] == (True, 1.0) and declared.contract() != plain.contract()
    radial = FieldDecl(**{**over_phi, "axes": ("R",)}, composed=True, neutral=0.0)  # the axes say nothing either way
    assert radial.composed and radial.neutral == 0.0
    with pytest.raises(DeclarationError, match="a neutral value is a composed field's declaration"):
        FieldDecl(**over_phi, neutral=1.0)
    for missing in (None, float("nan"), float("inf"), True, "1"):
        with pytest.raises(DeclarationError, match="declares its neutral value"):
            FieldDecl(**over_phi, composed=True, neutral=missing)
    with pytest.raises(DeclarationError, match="composed is True or False"):
        FieldDecl(**over_phi, composed=1, neutral=1.0)
    # A composed field is a continuous grid field: a scalar or a column is not composed.
    with pytest.raises(DeclarationError, match="continuous grid field"):
        FieldDecl(name="s", label="s", unit="dimensionless", kind=Kind.SCALAR, about="a scalar", composed=True, neutral=1.0)
    # compose gives the declared neutral, and refuses a field that does not declare one.
    assert np.all(compose.neutral(declared, (2, 3)) == 1.0) and compose.neutral(radial, (4,)).tolist() == [0.0] * 4
    with pytest.raises(LayerError, match="not declared composed"):
        compose.neutral(plain, (2, 3))
    # No source in the model reads the axes to decide it: FieldDecl holds a field named composed, not a property.
    source = (PACKAGE / "core" / "fielddoc.py").read_text(encoding="utf-8")
    assert "composed: bool = False" in source and '"phi" in self.axes' not in source
    for path in model_sources():
        assert not re.search(r'["\']phi["\'] in \w+(\.\w+)*\.axes', path.read_text(encoding="utf-8")), path.name


def test_texture_seed_is_the_fifth_seed_and_the_arm_phases_read_it(prod):
    """D214 section 3 said: "this test fails the day a stage reads ``texture_seed`` (BUILD_III phase P1's mode
    phases): remove ``graph.UNREAD_BY_RULING["texture_seed"]`` then, and this test's first half with it". That day
    was S56 (D215): the layer's ``arm_phases`` stage reads it at the pattern's checkpoint, the seed binds there like
    every other, and the graph's one named exception is spent - the mapping is empty."""
    models, impls_, table = prod
    assert [s.name for s in seeds()] == ["world_seed", "pattern_seed", "systems_seed", "planets_seed", "texture_seed"]
    assert dict(graph.UNREAD_BY_RULING) == {}
    readers = sorted(st.id for st in impls_ if "texture_seed" in st.reads_seeds)
    assert readers == ["arm_phases"] and impls_.get("arm_phases").layer_stage and impls_.get("arm_phases").checkpoint == 3
    assert impls_.get("arm_phases").requires == () and impls_.get("arm_phases").reads_constants == ()
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert g.input_checkpoint["texture_seed"] == 3 == INPUTS["texture_seed"].checkpoint_hypothesis
        assert g.unread_by_ruling == () and g.unbound_inputs == ()  # every input is read
    header = Service(grid=SMALL).handle("/api/clouds", SECTOR + "&texture_seed=12").frame()[0]
    assert header["inputs"]["texture_seed"] == 12
    # A seed nobody may leave unread without a ruling: an unread one is reported, texture_seed among them now.
    unread = stage("s", ("f",))
    g = graph.analyse(model("m", unread), impls(unread), INPUTS)
    assert "world_seed" in g.unbound_inputs and "texture_seed" in g.unbound_inputs


def test_rerolling_texture_seed_moves_the_placements_and_no_law(prod):
    """BUILD_III section 1c rule 1: "rerolling it changes placements and texture and nothing else" - true of
    something for the first time at S56 (gate G1 noted that until P1 no field was on the layer's seed). Two runs of
    the whole model that differ in ``texture_seed`` alone:

    - the five phases differ, and with them the three composed fields and where every placed census's objects are;
    - **no law moves**: every radial field, every history and every scalar that is not a census statistic is the
      same bits - the amplitudes, the saturation, the pitch, the gas's ratio, every profile;
    - every census expects the same count in every ring, to 1e-12 (I2, between two realisations);
    - what does move outside the placements is the closed list of census statistics, and nothing else: the realised
      objects are another draw until L1, exactly as between the layer on and off."""
    m = prod[0].get(DEFAULT_MODEL)
    a, b = run(m, {"texture_seed": 0}, SMALL), run(m, {"texture_seed": 987654321}, SMALL)
    assert b.inputs["texture_seed"] == 987654321 and a.order == b.order and set(a.fields) == set(b.fields)
    # Two scalars are a census's *expected* total - the expected counts summed over every cell, each carrying its
    # sector's placement weight. The weights average to 1 round a ring to rounding, not to the bit, so the sum is
    # the same to 1e-12 (rule 2: "no expected count or expected total") and can differ in its last bit between
    # two realisations: measured 1 ulp here. (Between the layer on and off at the default seeds they happen to be
    # the same bits, which is what test_i1 sees.)
    expected_totals = {"cloud_count_total", "bright_star_count_1e3"}
    moved_statistics, placed = set(), set()
    for n, d in a.decls.items():
        equal = same(a.fields[n], b.fields[n])
        if n in expected_totals:
            assert float(a.fields[n]) == pytest.approx(float(b.fields[n]), rel=1e-12, abs=0.0), n
        elif n in pt.PHASE_FIELDS:
            assert d.provenance == "synthetic" and not equal, n
        elif d.composed:
            assert not equal, n
        elif d.kind.domain == "object":
            if d.of in UNPLACED_OBJECTS:
                assert equal, n
            elif not equal:
                placed.add(d.of)
        elif not equal:
            moved_statistics.add(n)
    assert moved_statistics <= set(CENSUS_STATISTICS), sorted(moved_statistics - set(CENSUS_STATISTICS))
    assert placed == PLACED_OBJECTS
    for n in (*pt.AMPLITUDE_FIELDS, "arm_saturation", "arm_multiplicity", "arm_contrast", "bar_contrast", "pitch_angle",
              "gas_arm_contrast", "bar_pattern_speed", "sfr_surface_density", "stellar_surface_density", "disc_luminosity"):
        assert same(a.fields[n], b.fields[n]), n
    expect_a, expect_b = ring_expectations(a, m), ring_expectations(b, m)
    for census in expect_a:
        assert np.allclose(expect_a[census], expect_b[census], rtol=1e-12, atol=0.0), census
    # Each composed field keeps every ring's mean under either realisation.
    for out in (a, b):
        for n in ("pattern_density_contrast", "gas_density_contrast", "sfr_modulation"):
            assert float(np.abs(np.asarray(out.fields[n]).mean(axis=1) - 1.0).max()) < 1e-12, n


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


def test_no_module_of_the_model_constructs_a_pattern_object_by_its_class():
    """Gate G1, change 8: ``.from_fields(`` is one door to a pattern object and the constructor is the other. Nothing
    in the model calls ``ArmPattern(`` or ``GasPattern(`` - read from the syntax tree, so a type annotation or a
    docstring is not a call.

    S56 (D215): until S56 the two pattern modules each called ``ArmPattern(`` once - the ``pattern`` stage built the
    stellar law from the numbers it had just drawn, and the gas law built a stellar law of unit amplitude to take
    its weights and phase from. Both are gone: the ``pattern`` stage hands its law to ``compose.stellar_pattern``,
    which reads the layer's phases and builds the object through ``from_fields``, and the gas law takes the taper
    and the phase from ``pattern.bar_terms``. So the second door is shut for the whole model: every pattern object
    comes through ``compose``."""
    calls: dict[str, dict[str, int]] = {}
    for path in model_sources():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            called = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
            if called in ("ArmPattern", "GasPattern"):
                where = calls.setdefault(path.relative_to(PACKAGE).as_posix(), {})
                where[called] = where.get(called, 0) + 1
    # S56 (D215): was {"stages/pattern.py": {"ArmPattern": 1}, "stages/gas_pattern.py": {"ArmPattern": 1}}.
    assert calls == {}, calls
    # The text agrees with the tree: the token appears in no module's code or comments either.
    for path in model_sources():
        name = path.relative_to(PACKAGE).as_posix()
        assert not re.search(r"\b(ArmPattern|GasPattern)\(", path.read_text(encoding="utf-8")), name
    # And the one door is compose's: the pattern stage asks it for its own composed field's pattern.
    source = (PACKAGE / "stages" / "pattern.py").read_text(encoding="utf-8")
    assert "_compose.stellar_pattern(" in source and "law=" in source


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
    R = on.grid.R
    assert compose.stellar_pattern(on.fields, R) is not None and compose.stellar_pattern(off.fields, R) is None
    assert compose.gas_pattern(on.fields, R, c) is not None and compose.gas_pattern(off.fields, R, c) is None
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
    for call in (lambda: compose.stellar_pattern(bare, R), lambda: compose.gas_pattern(bare, R, c),
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
