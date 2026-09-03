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


def test_rows_without_a_field_yet():
    assert {q.n for q in spec.QUANTITIES if q.field is None} == {24}  # S2 filled row 23
    assert Q[24].mode == "qualitative"


def test_the_rows_the_model_can_reach_report_a_verdict(model):
    """S1 and S2 publish rows 1, 2, 3, 4, 19, 20, 22, 23; the rest must admit they cannot."""
    results = spec.run(model)
    assert len(results) == 24
    by_n = {r.n: r for r in results}
    assert {n for n, r in by_n.items() if r.status != "not-yet-computable"} == {1, 2, 3, 4, 19, 20, 22, 23}
    assert spec.summary(results) == {"pass": 3, "fail": 5, "not-yet-computable": 16}
    assert "no published scalar" in by_n[24].reason


def test_every_failure_is_recorded_and_the_run_is_clean(model):
    """Five rows miss and every one names a debt and a prediction (rules B4, B5)."""
    results = spec.run(model)
    failed = {r.n for r in results if r.status == "fail"}
    assert failed == {2, 3, 20, 22, 23}
    assert spec.unexplained(results) == () and spec.stale(results) == ()
    assert spec.problems(results) == []
    # Two causes hold five rows: debt #18 (no extended accretion) and #15 (the tilt).
    assert {spec.MISSES[n].debt for n in failed} == {15, 18}


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
    for row, m in spec.MISSES.items():
        assert m.row == row and m.debt >= 1 and m.since.startswith("S")
        assert m.reason.strip() and m.prediction.strip()
    with pytest.raises(spec.SpecError):
        spec.Miss(row=99, debt=1, since="S1", reason="r", prediction="p")
    with pytest.raises(spec.SpecError):
        spec.Miss(row=1, debt=0, since="S1", reason="r", prediction="p")
    with pytest.raises(spec.SpecError):
        spec.Miss(row=1, debt=1, since="S1", reason="r", prediction=" ")


def test_report_runs(prod):
    out = spec.report(list(prod[0]))
    assert "spec" in out and "16 not-yet-computable of 24" in out
    assert "recorded miss, debt #18, since S1" in out   # row 3, three sessions old
    assert "recorded miss, debt #15, since S2" in out


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
