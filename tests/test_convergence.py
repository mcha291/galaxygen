"""convergence: one knob at a time, judged against each row's own target width."""

from __future__ import annotations

import dataclasses

import pytest

from galaxy.core.grids import GridSpec
from galaxy.specs import convergence as cv
from galaxy.specs.spec import QUANTITIES, SpecError

Q = {q.n: q for q in QUANTITIES}


@pytest.fixture(scope="module")
def audits(prod):
    models, _, _ = prod
    return cv.sweep_models(list(models))


# --- the sweep is a sweep -----------------------------------------------------


def test_each_knob_moves_exactly_one_field_of_the_grid():
    """The whole point of the module: N_R, N_t and N_z are never one knob (§10)."""
    for knob in cv.KNOBS:
        for _, spec in knob.specs() + ((knob.control, knob.control_spec()),):
            differ = [
                f.name
                for f in dataclasses.fields(GridSpec)
                if getattr(spec, f.name) != getattr(cv.DEFAULT_GRID, f.name)
            ]
            assert differ == [knob.name], (knob.name, differ)


def test_the_three_grid_axes_are_all_swept():
    assert {k.name for k in cv.KNOBS} == {"n_R", "n_t", "n_z"}


def test_a_knob_needs_two_points_and_a_coarser_control():
    with pytest.raises(SpecError):
        cv.Knob("n_R", (200, 800), 8, True, "")  # a knob says what refining it buys
    with pytest.raises(SpecError):
        cv.Knob("n_widgets", (1, 2), 0, True, "x")
    with pytest.raises(SpecError):
        cv.Knob("n_R", (200, 400), 8, True, "x")  # 400 is the default: it is the baseline
    with pytest.raises(SpecError):
        cv.Knob("n_R", (200,), 8, True, "x")  # one point is not a sweep
    with pytest.raises(SpecError):
        cv.Knob("n_R", (200, 800), 200, True, "x")  # the control must be coarser than the sweep


def test_every_published_acceptance_scalar_is_swept_over_every_knob(audits, prod):
    from galaxy.run import run

    models, _, _ = prod
    for m in models:
        published = {
            q.n for q in QUANTITIES if q.field is not None and q.field in run(m, grid=cv.DEFAULT_GRID).fields
        }
        for knob in cv.KNOBS:
            swept = {d.row for d in audits[m.name].drifts if d.knob == knob.name}
            assert swept == published, (m.name, knob.name, published ^ swept)


def test_a_row_the_model_does_not_publish_is_not_swept(audits):
    """Rows 12, 13, 14, 18 and 21 are not-yet-computable in spec, and unswept here."""
    for name in ("simple", "advanced"):
        assert {d.row for d in audits[name].drifts}.isdisjoint({12, 13, 14, 18, 21})
    assert 24 not in {d.row for d in audits["simple"].drifts}  # simple has no alpha_sequence


# --- the judgement ------------------------------------------------------------


def test_zero_width_targets_get_no_verdict_rather_than_a_false_one(audits):
    """Debt #17: rows 20 and 21 are quoted without an uncertainty, so there is no width."""
    for name in ("simple", "advanced"):
        zero = [d for d in audits[name].drifts if d.status == "no-target-width"]
        assert {d.row for d in zero} == {20}
        assert all(d.knob in {"n_R", "n_t", "n_z"} for d in zero)
        assert all(d.drift is not None for d in zero)  # the number is still published (rule B6)


def test_the_acceptance_table_is_converged_on_the_default_grid(audits):
    """The S10 result: no row moves by even a tenth of its target's width."""
    for name in ("simple", "advanced"):
        drifts = audits[name].drifts
        assert not [d for d in drifts if d.status == "drifts"]
        margins = [d.margin for d in drifts if d.margin is not None]
        assert max(margins) < 0.1, max(margins)


def test_the_criterion_can_fire_and_is_shown_to(audits):
    """Rule B3: a sweep where nothing drifts and a broken instrument look the same."""
    for name in ("simple", "advanced"):
        controls = {c.knob: c for c in audits[name].controls}
        assert controls["n_R"].fired and controls["n_t"].fired
        assert all(c.ok for c in audits[name].controls)
        # Row 3 is read at one radius, so it is the first thing a coarse radial grid loses.
        assert 3 in controls["n_R"].fired


def test_n_z_moves_no_acceptance_row_at_any_resolution(audits):
    """S10 finding: the z axis has one field on it and one consumer, which reads column 0.

    Nothing in the acceptance table is measured on the vertical grid — not even at
    ``n_z = 1``, where the single sample sits 2.5 kpc above the plane. The scale
    heights of rows 6 and 7 are computed analytically by the vertical stage, not
    fitted to a z profile.
    """
    for name in ("simple", "advanced"):
        controls = {c.knob: c for c in audits[name].controls}
        assert controls["n_z"].fired == ()
        z = [d for d in audits[name].drifts if d.knob == "n_z"]
        assert z and max(d.margin for d in z if d.margin is not None) < 1e-3


def test_a_category_row_is_judged_on_the_category(audits):
    row24 = [d for d in audits["advanced"].drifts if d.row == 24]
    assert len(row24) == len(cv.KNOBS)
    assert all(d.drift is None and d.width is None for d in row24)
    assert all(d.status == "converged" and d.baseline == "single" for d in row24)


# --- the register -------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Named:
    """``report`` asks a model only for its name; a whole model is not needed to render one."""

    name: str


def _audit(model: str, *drifts: cv.Drift) -> cv.Audit:
    controls = tuple(cv.Control(model, k.name, k.control, (1,) if k.control_fires else (), k.control_fires)
                     for k in cv.KNOBS)
    return cv.Audit(model, drifts, controls)


def _drift(row: int, knob: str, status: str) -> cv.Drift:
    q = Q[row]
    width = (q.hi or 0.0) - (q.lo or 0.0)
    return cv.Drift(row, q.name, "simple", knob, 1.0, ((1, 1.0),), 99.0 if status == "drifts" else 0.0, width, status)


def test_an_unrecorded_drift_stops_the_run():
    a = _audit("simple", _drift(1, "n_t", "drifts"))
    assert [p.code for p in cv.problems(a)] == ["convergence"]
    assert cv.unrecorded(a) == a.drifts


def test_a_recorded_drift_prints_but_does_not_stop_the_run(monkeypatch):
    rec = cv.Recorded(row=1, knob="n_t", debt=99, since="S10", reason="r", prediction="p")
    monkeypatch.setattr(cv, "_RECORDED", (rec,))
    a = _audit("simple", _drift(1, "n_t", "drifts"))
    assert cv.problems(a) == []
    assert "recorded drift, debt #99" in cv.report([_Named("simple")], {"simple": a})


def test_a_recorded_drift_that_has_converged_is_stale_and_stops_the_run(monkeypatch):
    """Rule B10: the explanation is spent and the register is lying."""
    rec = cv.Recorded(row=1, knob="n_t", debt=99, since="S10", reason="r", prediction="p")
    monkeypatch.setattr(cv, "_RECORDED", (rec,))
    a = _audit("simple", _drift(1, "n_t", "converged"))
    assert [p.code for p in cv.problems(a)] == ["stale-drift"]


def test_a_recorded_drift_belongs_to_one_model_or_to_all(monkeypatch):
    """Rule A7: the advanced model's findings are its own."""
    rec = cv.Recorded(row=1, knob="n_t", debt=99, since="S10", reason="r", prediction="p", model="advanced")
    monkeypatch.setattr(cv, "_RECORDED", (rec,))
    assert cv.recorded("advanced") and not cv.recorded("simple")
    assert cv.problems(_audit("advanced", _drift(1, "n_t", "drifts"))) == []
    assert [p.code for p in cv.problems(_audit("simple", _drift(1, "n_t", "drifts")))] == ["convergence"]


def test_a_recorded_drift_is_validated():
    ok = dict(row=1, knob="n_t", debt=1, since="S10", reason="r", prediction="p")
    with pytest.raises(SpecError):
        cv.Recorded(**{**ok, "row": 99})
    with pytest.raises(SpecError):
        cv.Recorded(**{**ok, "knob": "n_stars"})
    with pytest.raises(SpecError):
        cv.Recorded(**{**ok, "since": "10"})
    with pytest.raises(SpecError):
        cv.Recorded(**{**ok, "reason": " "})
    with pytest.raises(SpecError):
        cv.Recorded(**{**ok, "model": "Advanced"})


def test_a_control_that_stops_firing_stops_the_run():
    """The instrument losing its demonstration is a problem, not a pass (rule B3)."""
    a = cv.Audit("simple", (), (cv.Control("simple", "n_R", 8, (), True),))
    assert [p.code for p in cv.problems(a)] == ["control"]
    b = cv.Audit("simple", (), (cv.Control("simple", "n_z", 1, (7,), False),))
    assert [p.code for p in cv.problems(b)] == ["control"]


# --- the report ---------------------------------------------------------------


def test_the_report_publishes_the_number_not_the_verdict(audits, prod):
    """Rule B6: the drift, what fraction of the value it is, and the margin against width."""
    models, _, _ = prod
    text = cv.report(list(models), audits)
    assert "convergence" in text and "control n_z = 1" in text
    for name in ("simple", "advanced"):
        assert f"model {name}:" in text
    assert "of the value)" in text and "of width" in text
    assert "no-target-width" in text


def test_the_runner_agrees_with_the_report(audits, prod):
    models, _, _ = prod
    assert cv.check(list(models), audits) == []
