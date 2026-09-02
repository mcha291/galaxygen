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
    assert {q.n for q in spec.QUANTITIES if q.field is None} == {23, 24}
    assert Q[24].mode == "qualitative"


def test_everything_not_yet_computable_at_s0(model):
    results = spec.run(model, grid=TINY)
    assert len(results) == 24
    assert {r.status for r in results} == {"not-yet-computable"}
    assert spec.summary(results) == {"pass": 0, "fail": 0, "not-yet-computable": 24}
    reasons = {r.n: r.reason for r in results}
    assert "not published" in reasons[1] and "no published scalar" in reasons[23]


def test_report_runs(prod):
    out = spec.report(list(prod[0]), grid=TINY)
    assert "spec" in out and "24 not-yet-computable of 24" in out


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
