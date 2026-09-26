"""spec: 33 quantities as data (31 until S34, 29 until S30, 24 until S28); the evaluator; everything not-yet-computable at S0."""

from __future__ import annotations

import re

import numpy as np
import pytest

from galaxy.core.fielddoc import Kind
from galaxy.specs import spec
from helpers import TINY, decl

Q = {q.n: q for q in spec.QUANTITIES}


def test_33_quantities():  # test_31_quantities until S34
    """S28 (BUILD_II Phase 3) added rows 25-28 (BHG16 Table 2) and 29 (the Tully-Fisher slope); S30
    (Phase 6) the two supernova rates, numbered once in ``spec`` (``ROW_CORE_COLLAPSE_RATE``,
    ``ROW_TYPE_IA_RATE``) and read from there everywhere else; S34 (Phase 5) the globular cluster system
    and the stellar halo the same way (``ROW_GC_SYSTEM_MASS``, ``ROW_STELLAR_HALO_MASS``)."""
    assert len(spec.QUANTITIES) == 33  # 31 until S34
    assert [q.n for q in spec.QUANTITIES] == list(range(1, 34))
    assert (spec.ROW_CORE_COLLAPSE_RATE, spec.ROW_TYPE_IA_RATE) == (30, 31)
    assert (spec.ROW_GC_SYSTEM_MASS, spec.ROW_STELLAR_HALO_MASS) == (32, 33)
    names = [q.name for q in spec.QUANTITIES]
    assert len(set(names)) == 33  # 31 until S34
    fields = [q.field for q in spec.QUANTITIES if q.field]
    assert len(set(fields)) == len(fields)
    assert all(q.source and q.stated for q in spec.QUANTITIES)


def test_statistical_rows_are_debt_8():
    # S34: row 32, the globular cluster system, drawn on world_seed ({13, 14, 16, 17, 18} until S34).
    assert {q.n for q in spec.QUANTITIES if q.mode == "statistical"} == {13, 14, 16, 17, 18, 32}


def test_every_row_names_a_field_but_the_four_ruling_b_holds_back():
    """S9 filled row 24. S28's ruling (b): rows 25-28 judge the model's intrinsic light only if BHG16
    Table 2 says its magnitudes are extinction-corrected, and it does not, so they name no field."""
    assert [q.n for q in spec.QUANTITIES if q.field is None] == [25, 26, 27, 28]
    assert Q[24].mode == "qualitative" and Q[24].expect == "bimodal_wide"
    for n, field in ((25, "absolute_magnitude_b"), (26, "absolute_magnitude_v"), (27, "colour_b_v"), (28, "mass_to_light_v")):
        assert Q[n].note.startswith("Not judged (S28 ruling (b))") and f"published as {field}" in Q[n].note
        assert "does not say its magnitudes are extinction-corrected" in Q[n].note
        assert "without the uncertainties" in Q[n].note  # the source's own words for the zero width
        assert "inconsistencies between magnitude differences and colour indices" in Q[n].note  # its caveat
    assert (Q[25].lo, Q[26].lo, Q[27].lo, Q[28].lo) == (-20.70, -21.37, 0.73, 1.70)


REACHED = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23}  # 12-14 and 18 since S17
# One model since D170 (the former advanced physics); the tables keep its values.
VERDICTS = {"basic": REACHED | {21, 24, 29, spec.ROW_CORE_COLLAPSE_RATE, spec.ROW_TYPE_IA_RATE, spec.ROW_GC_SYSTEM_MASS, spec.ROW_STELLAR_HALO_MASS}}  # S34: rows 32 and 33  # S24: the ism stage publishes gas_h2_fraction, so row 21 is computable for the first time (debt #79)
SUMMARY = {
    "basic": {"pass": 10, "fail": 19, "not-yet-computable": 4},  # S34: rows 32 and 33 fail, recorded (#98, #99; 17 fail of 31 until S34)  # S30: both supernova rates pass (8 pass of 29 until S30)  # S28: row 29 passes; 25-28 are ruling (b)'s  # S25: row 15 left by 0.01 (#80); S20: row 3 left; S18: row 22 crossed its edge by 0.0008
}
FAILED = {
    "basic": {3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 18, 20, 21, 22, 23, 24, 32, 33},  # 32, 33 since S34
}
# S25: row 15 is #80's (the bar reads the lambda_d scale length now that the pattern precedes
# star formation). S20: row 3 is #11's again (the bar); row 6 stays #42's. S18: row 20 is #17's
# (at its zero-width target), row 22 is #47's.
DEBTS = {"basic": {2, 11, 17, 27, 28, 42, 47, 80, 98, 99}}  # 98, 99 since S34 (rows 32, 33)
# S27 (BUILD_II Phase 2): the azimuthal model is basic with the sfh slot swapped for one that adds
# an (R, phi) modulation and changes no radial field, and every row is radial or vertical, so its
# tables are basic's -- by reference, so that they cannot drift apart. test_sfh_azimuthal asserts
# the rows themselves are equal, number for number.
for _table in (VERDICTS, SUMMARY, FAILED, DEBTS):
    _table["azimuthal"] = _table["basic"]
# S24: row 21 fails at a zero-width target (0.11, no quoted uncertainty) — debt #17's defect,
# not the prescription's. It could not pass however well the physics were done.


def test_the_rows_the_model_can_reach_report_a_verdict(model, judged):
    """Everything the model reaches; the rest must admit they cannot."""
    results = judged[model.name]
    assert len(results) == len(spec.QUANTITIES) == 33  # 31 until S34
    by_n = {r.n: r for r in results}
    assert {n for n, r in by_n.items() if r.status != "not-yet-computable"} == VERDICTS[model.name]
    assert spec.summary(results) == SUMMARY[model.name]


def test_every_failure_is_recorded_and_the_run_is_clean(model, judged):
    """Every miss names a debt and a prediction (rules A7, B4, B5)."""
    results = judged[model.name]
    failed = {r.n for r in results if r.status == "fail"}
    assert failed == FAILED[model.name]
    assert spec.unexplained(results, model.name) == () and spec.stale(results, model.name) == ()
    assert spec.problems(results, model.name) == []
    # #18 (no extended accretion), #27 (no [α/Fe] valley, so no thick disc), #28
    # (migration too strong once the tilt is right).
    assert {spec.misses(model.name)[n].debt for n in failed} == DEBTS[model.name]


def test_the_ledger_is_one_since_d170():
    """One model, one ledger: every miss is in ``spec.MISSES`` and none belongs to a model that is not registered."""
    assert spec.MISSES[5].debt == 27 and spec.MISSES[7].debt == 27  # the valley's rows (D170 kept the advanced ledger)
    # Row 22: since S18 the inner gas under the derived threshold (debt #47), out by 0.0008.
    assert spec.MISSES[22].debt == 47
    assert spec.MISSES[24].debt == 27
    assert spec.MISSES[12].debt == 11 and spec.MISSES[12].model is None
    # Row 3 landed at S18, by 0.04, on the kick (D124) and left again at S20, by 0.03, when the kick's
    # constant was re-derived (D128): the bar's (debt #11).
    assert spec.MISSES[3].debt == 11 and spec.MISSES[3].model is None and spec.MISSES[3].since == "S20"
    assert {m.model for m in spec.MISSES.values()} <= {None, "basic"}
    assert spec.misses("basic") == dict(spec.MISSES)
    # S27: every recorded miss is unqualified, so the azimuthal model is judged against the same ledger.
    assert spec.misses("azimuthal") == dict(spec.MISSES)


def test_an_unexplained_failure_stops_the_run():
    q = Q[1]
    d = scalar("stellar_mass_total")
    bad = [spec.evaluate(q, {"stellar_mass_total": 9e10}, {"stellar_mass_total": d}, "m")]
    assert len(spec.unexplained(bad)) == 1
    assert [p.code for p in spec.problems(bad)] == ["acceptance"]


def test_a_recorded_miss_that_starts_passing_is_itself_a_problem():
    q = Q[9]  # row 3 was the example until S18, when it did exactly this and its entry went (D124)
    d = scalar("thick_thin_surface_density_ratio", "dimensionless")
    good = [spec.evaluate(q, {"thick_thin_surface_density_ratio": 0.12}, {"thick_thin_surface_density_ratio": d}, "m")]
    assert good[0].status == "pass" and len(spec.stale(good)) == 1
    assert [p.code for p in spec.problems(good)] == ["stale-miss"]


def test_recorded_misses_are_well_formed():
    for row, m in spec.MISSES.items():
        assert m.row == row and m.debt >= 1 and m.since.startswith("S")
        assert m.reason.strip() and m.prediction.strip()
    with pytest.raises(spec.SpecError):
        spec.Miss(row=99, debt=1, since="S1", reason="r", prediction="p")
    with pytest.raises(spec.SpecError):
        spec.Miss(row=1, debt=0, since="S1", reason="r", prediction="p")
    with pytest.raises(spec.SpecError):
        spec.Miss(row=1, debt=1, since="S1", reason="r", prediction=" ")
    with pytest.raises(spec.SpecError):
        spec.Miss(row=1, debt=1, since="S1", reason="r", prediction="p", model="Not A Model")


def test_report_runs(prod, judged):
    out = spec.report(list(prod[0]), judged)
    assert "spec" in out and "4 not-yet-computable of 33" in out  # of 31 until S34
    assert "recorded miss, debt #11, since S17" in out   # rows 12-14: the spheroid
    assert "recorded miss, debt #11, since S20" in out   # row 3: the bar again, out by 0.03 on the re-derived kick (D128)
    assert "recorded miss, debt #42, since S13" in out   # row 6: the heated old population counted as thin
    assert "recorded miss, debt #17, since S16" in out   # row 20: at its zero-width target
    assert "recorded miss, debt #47, since S18" in out   # row 22
    assert "recorded miss, debt #27, since S9" in out


def scalar(name, unit="Msun"):
    return decl(name, Kind.SCALAR, unit=unit)


def test_pointwise():
    q = Q[1]
    d = scalar("stellar_mass_total")
    assert spec.evaluate(q, {"stellar_mass_total": 5e10}, {"stellar_mass_total": d}, "m").status == "pass"
    r = spec.evaluate(q, {"stellar_mass_total": 7e10}, {"stellar_mass_total": d}, "m")
    assert r.status == "fail" and r.value == 7e10
    r = spec.evaluate(q, {"stellar_mass_total": 5e10}, {"stellar_mass_total": scalar("stellar_mass_total", "kpc")}, "m")
    assert r.status == "fail" and "unit mismatch" in r.reason
    r = spec.evaluate(q, {"stellar_mass_total": np.ones(3)}, {"stellar_mass_total": decl("stellar_mass_total", unit="Msun")}, "m")
    assert r.status == "fail" and "not a scalar" in r.reason


def test_zero_width_target_is_recorded_not_widened():
    q = Q[20]
    d = scalar("hydrogen_mass_30kpc")
    assert spec.evaluate(q, {"hydrogen_mass_30kpc": 8.0e9}, {"hydrogen_mass_30kpc": d}, "m").status == "pass"
    r = spec.evaluate(q, {"hydrogen_mass_30kpc": 8.0e9 * (1 + 1e-9)}, {"hydrogen_mass_30kpc": d}, "m")
    assert r.status == "fail" and "zero-width" in r.reason


def test_the_table_says_which_rows_have_no_testable_target():
    """Debt #17: the second of the two fixes it names, the first needing a source S10 has not got."""
    # Row 14 left at S17 (the source does quote an uncertainty); rows 25-28 joined at S28: BHG16
    # prints Table 2 "without the uncertainties" (section 2.2), and no width is invented (D100).
    assert {q.n for q in spec.untestable()} == {20, 21, 25, 26, 27, 28}
    assert all(Q[n].lo == Q[n].hi and Q[n].mode == "pointwise" for n in (20, 21, 25, 26, 27, 28))
    # Row 14 was on the list until S17, when the remedy debt #17 actually asks for arrived: the
    # source does quote an uncertainty for the bulge's dispersion, "to = 3 km/s" (BHG16 §4.3),
    # and it was entered rather than invented. Rows 20 and 21's sources still quote none.
    assert Q[14].lo == 110.0 and Q[14].hi == 116.0 and Q[14].mode == "statistical" and Q[14].testable
    assert all(q.testable for q in spec.QUANTITIES if q.n not in (20, 21, 25, 26, 27, 28))


def test_a_new_zero_width_row_cannot_be_added_silently():
    """Rule B13: the defect is only recorded because rows 20 and 21 say so in their notes."""
    ok = dict(n=1, name="x", unit="Msun", field="f", mode="pointwise", stated="8", source="s")
    with pytest.raises(spec.SpecError):
        spec.Quantity(lo=8.0, hi=8.0, **ok)
    assert not spec.Quantity(lo=8.0, hi=8.0, note="no uncertainty quoted", **ok).testable
    assert spec.Quantity(lo=7.0, hi=9.0, **ok).testable


def test_the_report_names_the_table_defect(prod, judged):
    out = spec.report(list(prod[0]), judged)
    assert "table: rows 20, 21, 25, 26, 27, 28 have zero-width targets" in out
    assert "a defect in the table, not in a model (debt #17)" in out
    # It fails nothing: the rows still evaluate and still print their number.
    assert re.search(r"8\.08\d*e\+09", out)  # row 20's hydrogen mass, printed (6.028e9 until S18; 6.243e9 until S17; 4.171e9 until S16)


def test_statistical():
    q = Q[16]  # bar pattern speed 34–52 km/s/kpc
    d = scalar("bar_pattern_speed", "km/s/kpc")
    fields = {"bar_pattern_speed": 43.0}
    decls = {"bar_pattern_speed": d}
    assert spec.evaluate(q, fields, decls, "m").status == "not-yet-computable"
    assert spec.evaluate(q, fields, decls, "m", {"bar_pattern_speed": [40.0] * 5}).status == "not-yet-computable"
    ok = spec.evaluate(q, fields, decls, "m", {"bar_pattern_speed": np.linspace(30, 40, 50)})
    assert ok.status == "pass" and ok.value == pytest.approx(35.0)
    bad = spec.evaluate(q, fields, decls, "m", {"bar_pattern_speed": np.linspace(60, 70, 50)})
    assert bad.status == "fail"
    # Row 14 carried the zero-width defect until S17 entered the source's own ±3 (debt #17).
    # Its median is judged like any other statistical row now, and a median outside the window
    # still fails: the row is testable, not lenient.
    point = Q[14]  # 113 ± 3 km/s since S17
    dp = scalar("bulge_velocity_dispersion", "km/s")
    ens = {"bulge_velocity_dispersion": np.linspace(100, 120, 50)}
    assert spec.evaluate(point, {"bulge_velocity_dispersion": 110.0}, {"bulge_velocity_dispersion": dp}, "m", ens).status == "pass"
    far = {"bulge_velocity_dispersion": np.linspace(120, 140, 50)}
    r = spec.evaluate(point, {"bulge_velocity_dispersion": 130.0}, {"bulge_velocity_dispersion": dp}, "m", far)
    assert r.status == "fail" and "no testable target" not in r.reason


def test_qualitative():
    q = spec.Quantity(99, "q", "dimensionless", "flag", None, None, "qualitative", "x", "src", expect="bimodal")
    d = decl("flag", Kind.CATEGORY_SCALAR, categories=("bimodal", "unimodal"))
    assert spec.evaluate(q, {"flag": "bimodal"}, {"flag": d}, "m").status == "pass"
    assert spec.evaluate(q, {"flag": "unimodal"}, {"flag": d}, "m").status == "fail"
    assert spec.evaluate(q, {"flag": 1.0}, {"flag": scalar("flag", "dimensionless")}, "m").status == "fail"


def test_quantity_validation():
    ok = dict(n=1, name="n", unit="kpc", field="f", lo=0.0, hi=1.0, mode="pointwise", stated="s", source="src")
    spec.Quantity(**ok)
    for bad in [
        dict(mode="vibes"),
        dict(unit="furlong"),
        dict(hi=None),
        dict(lo=2.0),
        dict(lo=None, hi=None),
        dict(mode="qualitative", lo=None, hi=None),  # field set but no expect
        dict(source=""),
        dict(field="Bad"),
    ]:
        with pytest.raises(spec.SpecError):
            spec.Quantity(**{**ok, **bad})
    spec.Quantity(**{**ok, "field": None, "lo": None, "hi": None})  # not yet defined: allowed


def test_the_ensemble_runs_only_the_stages_its_fields_need():
    """Debt #24: twenty runs of the whole pipeline for two scalars (rule D4)."""
    from galaxy.core.registry import INPUTS
    from helpers import impls, model, stage

    ran: list[str] = []

    def count(name):
        def compute(ctx, _n=name):
            ran.append(_n)
            return {_n: np.ones(ctx.grid.shape(("R",)))}

        return compute

    wanted = stage("wanted", (decl("f", Kind.SCALAR, provenance="seeded"),), reads_seeds=("world_seed",),
                   compute=lambda ctx: {"f": float(ctx.rng("world_seed").random())})
    costly = stage("costly", ("expensive",), compute=count("expensive"))
    m = model("m", wanted, costly)
    got = spec.ensemble(m, fields=("f",), n=3, impls=impls(wanted, costly), table=INPUTS, grid=TINY)
    assert len(got["f"]) == 3 and len(set(got["f"])) == 3, "the seeds did not move"
    assert ran == [], f"the ensemble ran {ran}, which no requested field needs"


# --- S10 run 2: the statistical machinery (debt #8's criterion) ----------------


def _stat(values, row=16):
    """Judge row ``row`` against a synthetic ensemble, the median standing in for the run."""
    q = Q[row]
    d = {q.field: scalar(q.field, q.unit)}
    return spec.evaluate(q, {q.field: float(np.median(values))}, d, "m", {q.field: list(values)})


def test_a_statistical_row_is_judged_on_its_median_not_on_its_reach():
    """S13 (debt #38): the S0 criterion passed a row when the ensemble's interval *intersected*
    the target, so a median well outside passed on spread alone and a noisier model was easier
    to pass. The verdict is the median's now; the interval is published beside it."""
    q = Q[16]  # target [34, 52]
    assert (q.lo, q.hi) == (34.0, 52.0)
    assert _stat(43.0 + np.linspace(-20, 20, spec.ENSEMBLE_MIN)).status == "pass"
    assert _stat(50.0 + np.linspace(-30, 30, spec.ENSEMBLE_MIN)).status == "pass"  # wide, but centred inside
    # 60 is 8 above the top of the target: it fails at every spread, however wide.
    assert _stat(60.0 + np.linspace(-5, 5, spec.ENSEMBLE_MIN)).status == "fail"
    assert _stat(60.0 + np.linspace(-20, 20, spec.ENSEMBLE_MIN)).status == "fail"
    assert _stat(100.0 + np.linspace(-60, 60, spec.ENSEMBLE_MIN)).status == "fail"
    assert "median" in _stat(43.0 + np.linspace(-20, 20, spec.ENSEMBLE_MIN)).reason


def test_the_ensemble_size_and_the_central_fraction_agree_since_s13():
    """S13 (debt #38): at n = 20 the 'central 95%' interval trimmed no whole draw, being pinned by
    the two most extreme values; n = 41 is the smallest ensemble at which it excludes one draw
    at each end, so the published interval is the fraction it is named after."""
    tail = (1.0 - spec.CENTRAL) / 2.0
    assert (spec.ENSEMBLE_MIN, spec.CENTRAL) == (41, 0.95)
    assert tail * (spec.ENSEMBLE_MIN - 1) == pytest.approx(1.0)
    assert tail * (spec.ENSEMBLE_MIN - 1) >= 1.0

    v = np.linspace(0.0, 1.0, spec.ENSEMBLE_MIN)
    lo, hi = np.percentile(v, [100 * tail, 100 * (1 - tail)])
    assert lo == pytest.approx(v[1]) and hi == pytest.approx(v[-2])  # one draw excluded at each end
    assert (hi - lo) / (v.max() - v.min()) == pytest.approx(0.95)


def test_the_ensemble_samples_the_diagonal_of_seed_space(prod):
    """S10 run 2: every member sets all four seeds to the same integer (debt #39)."""
    from galaxy.core.registry import INPUTS
    from galaxy.run import run

    models, _, _ = prod
    m = models.get("basic")
    seed_names = [n for n, i in INPUTS.items() if i.kind == "seed"]
    assert len(seed_names) == 4
    # Harmless today: no published quantity depends on more than one seed, so the
    # diagonal and the marginal agree. The test is what notices if that changes.
    alone = float(run(m, {"pattern_seed": 3}, only=("bar_pattern_speed",)).fields["bar_pattern_speed"])
    together = float(run(m, {n: 3 for n in seed_names}, only=("bar_pattern_speed",)).fields["bar_pattern_speed"])
    assert alone == together


def test_world_seed_is_live_and_every_declared_seed_is_bound(prod):
    """S10 run 2 found one of the four seeds inert (debt #39); S17's nucleus stage reads it.

    ``graph`` reported it as unbound rather than failing, which was deliberate — an input
    no stage reads yet is a gap, not an error — and what this test pinned was that
    ``spec.ensemble`` varied it anyway, so a quarter of the nominal seed dimension did
    nothing. The M_• residual is what ruling 10 always meant it for, and now that the
    spheroid exists to have a dispersion, it draws it. Debt #39's other half stands: the
    ensemble is still a diagonal, moving every seed together rather than one at a time.
    """
    from galaxy.run import run as _run
    from galaxy.specs.graph import build

    models, impls, table = prod
    for m in models:
        read = {s for st in build(m, impls, table).order for s in st.reads_seeds}
        assert read == {"world_seed", "pattern_seed", "systems_seed", "planets_seed"}
        assert build(m, impls, table).unbound_inputs == ()
        # And it moves something: rerolling it alone changes M_• and nothing upstream.
        a = _run(m, {"world_seed": 0}, only=("black_hole_mass", "bulge_velocity_dispersion"))
        b = _run(m, {"world_seed": 5}, only=("black_hole_mass", "bulge_velocity_dispersion"))
        assert a.fields["black_hole_mass"] != b.fields["black_hole_mass"]
        assert a.fields["bulge_velocity_dispersion"] == b.fields["bulge_velocity_dispersion"]


# --- S28: the sweep instrument (rule B1) and the rows it judges ---------------------------------


def test_a_sweep_row_is_well_formed():
    ok = dict(n=1, name="tf", unit="mag", field="absolute_magnitude_b", lo=-8.56, hi=-7.14, mode="sweep", stated="s", source="src")
    spec.Quantity(**ok, sweep=spec.Sweep("halo_mass", 5, "circular_velocity_resolved"))
    with pytest.raises(spec.SpecError):
        spec.Quantity(**ok)  # a sweep row without a Sweep
    with pytest.raises(spec.SpecError):
        spec.Quantity(**{**ok, "mode": "pointwise"}, sweep=spec.Sweep("halo_mass", 5, "circular_velocity_resolved"))
    with pytest.raises(spec.SpecError):
        spec.Sweep("halo_mass", 2, "circular_velocity_resolved")  # two points fit any slope exactly
    with pytest.raises(spec.SpecError):
        spec.Sweep("Halo", 5, "circular_velocity_resolved")


def test_the_sweep_judges_the_slope_and_only_the_slope():
    q = Q[29]
    d = {q.field: scalar(q.field, "mag")}
    x = np.linspace(2.2, 2.8, q.sweep.points)
    inside = spec.evaluate(q, {q.field: -21.0}, d, "m", swept={29: (x, -7.85 * (x - 2.5) - 19.70)})
    assert inside.status == "pass" and inside.value == pytest.approx(-7.85)
    shifted = spec.evaluate(q, {q.field: -21.0}, d, "m", swept={29: (x, -7.85 * (x - 2.5) - 15.0)})
    assert shifted.status == "pass", "the zero point is not judged (the dust and the width definitions move it)"
    steep = spec.evaluate(q, {q.field: -21.0}, d, "m", swept={29: (x, -10.0 * (x - 2.5) - 19.70)})
    assert steep.status == "fail"
    assert spec.evaluate(q, {q.field: -21.0}, d, "m").status == "not-yet-computable"
    assert spec.evaluate(q, {q.field: -21.0}, d, "m", swept={29: (x[:3], x[:3])}).status == "not-yet-computable"


def test_the_tully_fisher_row_is_sakais_slope_with_its_own_uncertainty():
    q = Q[29]
    assert q.mode == "sweep" and (q.lo, q.hi) == (-8.56, -7.14)  # -7.85 +/- 0.71
    assert q.sweep.input == "halo_mass" and q.sweep.abscissa == "circular_velocity_resolved"
    assert q.lo <= -7.27 <= q.hi  # Tully & Pierce 2000's slope, the named alternative, inside
    assert q.sweep.x(np.array([10.0, 158.1, 120.0])) == pytest.approx(np.log10(316.2))


def test_the_sweep_runs_the_whole_declared_range(prod):
    """The input is swept across the range it declares, not a range chosen to fit (S28)."""
    from galaxy.core.registry import INPUTS

    q = Q[29]
    values = q.sweep.values(INPUTS["halo_mass"].lo, INPUTS["halo_mass"].hi)
    assert values[0] == 1e11 and values[-1] == pytest.approx(1e13) and values.size == 9


def test_rows_1_to_24_are_where_s27_left_them(judged):
    """The gate: S28 added light and moved nothing it did not publish (D176's numbers)."""
    for results in judged.values():
        v = {r.n: r.value for r in results}
        assert v[15] == pytest.approx(5.20971, abs=5e-6)
        assert v[16] == pytest.approx(41.1036, abs=5e-5)
        assert v[17] == pytest.approx(6.08381, abs=5e-6)
        assert v[3] == pytest.approx(251.026, abs=5e-4)
        assert v[21] == pytest.approx(0.2001, abs=5e-5)


def test_the_tully_fisher_slope_as_the_sweep_reads_it(judged):
    """S28: -7.91436 in both models, inside Sakai et al.'s -7.85 +/- 0.71; the zero point (not
    judged) is -19.00 at log W = 2.5 against Sakai's -19.70 and Tully & Pierce's -20.11."""
    for results in judged.values():
        r = next(r for r in results if r.n == 29)
        assert r.status == "pass" and r.value == pytest.approx(-7.91436, abs=5e-5)
        zero = float(re.search(r"zero point at log W = 2\.5 (-?[0-9.]+)", r.reason).group(1))
        assert zero == pytest.approx(-19.00, abs=0.01)
