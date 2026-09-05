"""spec: 24 quantities as data; the evaluator; everything not-yet-computable at S0."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.fielddoc import Kind
from galaxy.specs import spec
from helpers import TINY, decl

Q = {q.n: q for q in spec.QUANTITIES}


def test_24_quantities():
    assert len(spec.QUANTITIES) == 24
    assert [q.n for q in spec.QUANTITIES] == list(range(1, 25))
    names = [q.name for q in spec.QUANTITIES]
    assert len(set(names)) == 24
    fields = [q.field for q in spec.QUANTITIES if q.field]
    assert len(set(fields)) == len(fields)
    assert all(q.source and q.stated for q in spec.QUANTITIES)


def test_statistical_rows_are_debt_8():
    assert {q.n for q in spec.QUANTITIES if q.mode == "statistical"} == {13, 14, 16, 17, 18}


def test_every_row_names_a_field():
    assert all(q.field is not None for q in spec.QUANTITIES)  # S9 filled row 24
    assert Q[24].mode == "qualitative" and Q[24].expect == "bimodal_wide"


REACHED = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17, 19, 20, 22, 23}
VERDICTS = {"simple": REACHED, "advanced": REACHED | {24}}
SUMMARY = {
    "simple": {"pass": 11, "fail": 7, "not-yet-computable": 6},
    "advanced": {"pass": 8, "fail": 11, "not-yet-computable": 5},
}
FAILED = {"simple": {2, 3, 5, 11, 20, 22, 23}, "advanced": {2, 3, 5, 7, 8, 9, 10, 11, 20, 23, 24}}
DEBTS = {"simple": {15, 18, 19}, "advanced": {18, 27, 28}}


def test_the_rows_the_model_can_reach_report_a_verdict(model, judged):
    """Everything the model reaches; the rest must admit they cannot."""
    results = judged[model.name]
    assert len(results) == 24
    by_n = {r.n: r for r in results}
    assert {n for n, r in by_n.items() if r.status != "not-yet-computable"} == VERDICTS[model.name]
    assert spec.summary(results) == SUMMARY[model.name]
    if model.name == "simple":
        assert "not published by model" in by_n[24].reason  # one abundance, no α–Fe plane (rule B3)


def test_every_failure_is_recorded_and_the_run_is_clean(model, judged):
    """Every miss names a debt and a prediction, per model (rules A7, B4, B5)."""
    results = judged[model.name]
    failed = {r.n for r in results if r.status == "fail"}
    assert failed == FAILED[model.name]
    assert spec.unexplained(results, model.name) == () and spec.stale(results, model.name) == ()
    assert spec.problems(results, model.name) == []
    # Simple: #18 (no extended accretion), #15 (the tilt), #19 (the thick disc's
    # shape). Advanced: #18 again, #27 (no [α/Fe] valley, so no thick disc), #28
    # (migration too strong once the tilt is right).
    assert {spec.misses(model.name)[n].debt for n in failed} == DEBTS[model.name]


def test_a_miss_belongs_to_one_model_or_to_all():
    """Row 22 is a simple-model miss the advanced model closes; row 3 misses in both."""
    assert 22 in spec.MISSES and 22 not in spec.MISSES_ADVANCED
    assert 24 in spec.MISSES_ADVANCED and 24 not in spec.MISSES
    assert spec.MISSES[3] is spec.MISSES_ADVANCED[3] and spec.MISSES[3].model is None
    assert {m.model for m in spec._MISSES_ADVANCED} == {"advanced"}


def test_an_unexplained_failure_stops_the_run():
    q = Q[1]
    d = scalar("stellar_mass_total")
    bad = [spec.evaluate(q, {"stellar_mass_total": 9e10}, {"stellar_mass_total": d}, "m")]
    assert len(spec.unexplained(bad)) == 1
    assert [p.code for p in spec.problems(bad)] == ["acceptance"]


def test_a_recorded_miss_that_starts_passing_is_itself_a_problem():
    q = Q[3]
    d = scalar("v_tangential_sun", "km/s")
    good = [spec.evaluate(q, {"v_tangential_sun": 248.0}, {"v_tangential_sun": d}, "m")]
    assert good[0].status == "pass" and len(spec.stale(good)) == 1
    assert [p.code for p in spec.problems(good)] == ["stale-miss"]


def test_recorded_misses_are_well_formed():
    for row, m in list(spec.MISSES.items()) + list(spec.MISSES_ADVANCED.items()):
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
    assert "spec" in out and "6 not-yet-computable of 24" in out and "5 not-yet-computable of 24" in out
    assert "recorded miss, debt #18, since S1" in out   # row 3, eight sessions old
    assert "recorded miss, debt #19, since S3" in out
    assert "recorded miss, debt #15, since S2" in out
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
    d = scalar("gas_mass_30kpc")
    assert spec.evaluate(q, {"gas_mass_30kpc": 8.0e9}, {"gas_mass_30kpc": d}, "m").status == "pass"
    r = spec.evaluate(q, {"gas_mass_30kpc": 8.0e9 * (1 + 1e-9)}, {"gas_mass_30kpc": d}, "m")
    assert r.status == "fail" and "zero-width" in r.reason


def test_the_table_says_which_rows_have_no_testable_target():
    """Debt #17: the second of the two fixes it names, the first needing a source S10 has not got."""
    assert {q.n for q in spec.untestable()} == {20, 21}
    assert all(Q[n].lo == Q[n].hi and Q[n].mode == "pointwise" for n in (20, 21))
    # Row 14 quotes no uncertainty either and is testable, because it is judged
    # against an ensemble whose spread does the work.
    assert Q[14].lo == Q[14].hi and Q[14].mode == "statistical" and Q[14].testable
    assert all(q.testable for q in spec.QUANTITIES if q.n not in (20, 21))


def test_a_new_zero_width_row_cannot_be_added_silently():
    """Rule B13: the defect is only recorded because rows 20 and 21 say so in their notes."""
    ok = dict(n=1, name="x", unit="Msun", field="f", mode="pointwise", stated="8", source="s")
    with pytest.raises(spec.SpecError):
        spec.Quantity(lo=8.0, hi=8.0, **ok)
    assert not spec.Quantity(lo=8.0, hi=8.0, note="no uncertainty quoted", **ok).testable
    assert spec.Quantity(lo=7.0, hi=9.0, **ok).testable


def test_the_report_names_the_table_defect(prod, judged):
    out = spec.report(list(prod[0]), judged)
    assert "table: rows 20, 21 have zero-width targets" in out
    assert "a defect in the table, not in a model (debt #17)" in out
    # It fails nothing: the rows still evaluate and still print their number.
    assert "5.79503e+09" in out


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
    point = Q[14]  # 113 km/s, no error: the ensemble spread does the work
    dp = scalar("bulge_velocity_dispersion", "km/s")
    r = spec.evaluate(point, {"bulge_velocity_dispersion": 100.0}, {"bulge_velocity_dispersion": dp}, "m", {"bulge_velocity_dispersion": np.linspace(100, 120, 40)})
    assert r.status == "pass"


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
