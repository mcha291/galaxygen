"""convergence: one knob at a time, the judge, the register, and what the grid moves at S10.

The full sweep is what ``python -m galaxy.specs`` runs; here each model is swept
at one point per knob, once per session, so the suite asserts the instrument's
own reading rather than re-measuring it in every test.
"""

from __future__ import annotations

import math

import pytest

from galaxy.core.grids import DEFAULT
from galaxy.specs import convergence as C
from galaxy.specs.spec import QUANTITIES, Quantity, SpecError

Q = {q.n: q for q in QUANTITIES}
QUICK = dict(r_sweep=(200,), t_sweep=(1000,))
REACHED = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17, 19, 20, 22, 23}
VERDICTS = {"simple": REACHED, "advanced": REACHED | {24}}


@pytest.fixture(scope="module")
def swept(prod):
    """Both models, one point per knob: the instrument's state at S10, built once."""
    return {m.name: C.evaluate(m, **QUICK) for m in prod[0]}


def test_the_sweep_moves_one_knob_at_a_time():
    """GALAXY_INPUTS.md §10: exponent 0.13 in N_R against ~1 in N_t. They are not one knob."""
    for knob, n, g in C.grids():
        changed = {k for k in ("n_R", "n_t", "n_z", "n_phi") if getattr(g, k) != getattr(DEFAULT, k)}
        assert changed == {knob} and getattr(g, knob) == n
    assert [k for k, _, _ in C.grids()] == ["n_R"] * len(C.R_SWEEP) + ["n_t"] * len(C.T_SWEEP)
    assert DEFAULT.n_R not in C.R_SWEEP and DEFAULT.n_t not in C.T_SWEEP
    assert set(C.KNOBS) == {"n_R", "n_t"}
    # Both directions of each knob: coarser says whether the default is converged, finer where it goes.
    assert min(C.R_SWEEP) < DEFAULT.n_R < max(C.R_SWEEP) and min(C.T_SWEEP) < DEFAULT.n_t < max(C.T_SWEEP)


def points(field, *values):
    return [("n_R", 100, {field: values[0]})] + [("n_t", 500, {field: v}) for v in values[1:]]


def test_the_judge():
    q = Q[3]  # 245-251 km/s: width 6
    d = C.judge(q, {"v_tangential_sun": 248.0}, points("v_tangential_sun", 250.0, 247.0, 246.5))
    assert d.status == "pass" and d.width == 6 and dict(d.drift) == {"n_R": 2.0, "n_t": 1.5} and d.worst == 2.0
    assert d.default == 248.0 and len(d.points) == 3 and "33.3% of width" in d.reason
    d = C.judge(q, {"v_tangential_sun": 248.0}, points("v_tangential_sun", 255.0, 247.0))
    assert d.status == "fail" and "n_R 7" in d.reason
    assert C.judge(q, {}, points("v_tangential_sun", 1.0)).status == "not-yet-computable"
    assert C.judge(Q[12], {}, []).status == "not-yet-computable"
    # A statistical row is judged on one seeded realisation, and says so.
    assert "single seed" in C.judge(Q[16], {"bar_pattern_speed": 43.0}, points("bar_pattern_speed", 43.5)).reason
    # NaN anywhere is an infinite drift, never a quiet pass (rule B9).
    assert C.judge(q, {"v_tangential_sun": 248.0}, points("v_tangential_sun", math.nan)).status == "fail"


def test_the_qualitative_row_and_a_zero_width_one():
    q = Q[24]
    assert C.judge(q, {"alpha_sequence": "single"}, points("alpha_sequence", "single", "single")).status == "pass"
    d = C.judge(q, {"alpha_sequence": "single"}, points("alpha_sequence", "bimodal_wide", "single"))
    assert d.status == "fail" and "n_R=100" in d.reason and d.width is None
    z = Quantity(99, "z", "km/s", "v_tangential_sun", 1.0, 1.0, "pointwise", "1", "s")
    assert C.judge(z, {"v_tangential_sun": 1.0}, points("v_tangential_sun", 1.0)).status == "pass"
    assert C.judge(z, {"v_tangential_sun": 1.0}, points("v_tangential_sun", 1.0 + 1e-12)).status == "fail"


def test_the_register_is_well_formed_and_judged_per_model(monkeypatch):
    with pytest.raises(SpecError):
        C.Recorded(row=99, debt=1, since="S10", reason="r", prediction="p")
    with pytest.raises(SpecError):
        C.Recorded(row=3, debt=0, since="S10", reason="r", prediction="p")
    with pytest.raises(SpecError):
        C.Recorded(row=3, debt=1, since="S10", reason="r", prediction=" ")
    with pytest.raises(SpecError):
        C.Recorded(row=3, debt=1, since="S10", reason="r", prediction="p", model="Not a model")
    r = C.Recorded(row=3, debt=18, since="S10", reason="r", prediction="p", model="simple")
    monkeypatch.setattr(C, "_RECORDED", (r,))
    q = Q[3]
    failing = [C.judge(q, {"v_tangential_sun": 248.0}, points("v_tangential_sun", 255.0))]
    passing = [C.judge(q, {"v_tangential_sun": 248.0}, points("v_tangential_sun", 249.0))]
    assert C.problems(failing, "simple") == [] and C.unexplained(failing, "simple") == ()
    assert [p.code for p in C.problems(failing, "advanced")] == ["drift"]
    assert [p.code for p in C.problems(passing, "simple")] == ["stale-drift"] and len(C.stale(passing, "simple")) == 1
    assert C.problems(passing, "advanced") == []
    monkeypatch.setattr(C, "_RECORDED", (r, r))
    with pytest.raises(SpecError):
        C.recorded("simple")


def test_every_row_the_model_reaches_converges_at_s10(model, swept):
    """S10's measurement: the grid moves no verdict. Halving either knob moves nothing past a tenth of its width."""
    drifts = swept[model.name]
    assert len(drifts) == 24
    by_n = {d.n: d for d in drifts}
    assert {n for n, d in by_n.items() if d.status != "not-yet-computable"} == VERDICTS[model.name]
    assert all(d.status == "pass" for d in drifts if d.status != "not-yet-computable")
    assert C.problems(drifts, model.name) == [] and C.stale(drifts, model.name) == ()
    assert max(d.worst / d.width for d in drifts if d.width) < 0.1
    assert by_n[19].worst == 0.0  # M200 is an input read back
    if model.name == "advanced":
        assert by_n[24].status == "pass" and "'single' at every point" in by_n[24].reason
        assert by_n[5].default == 0.0 and by_n[5].worst == 0.0  # no thick disc on any grid (debt #27)


def test_report_runs(prod, swept):
    out = C.report(list(prod[0]), swept, r_sweep=QUICK["r_sweep"], t_sweep=QUICK["t_sweep"])
    assert out.startswith("convergence") and "one knob at a time against n_R=400, n_t=2000: n_R 200; n_t 1000" in out
    assert "model simple: 18 pass, 0 fail, 6 not-yet-computable of 24" in out
    assert "model advanced: 19 pass, 0 fail, 5 not-yet-computable of 24" in out
