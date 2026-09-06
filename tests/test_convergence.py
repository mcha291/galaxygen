"""convergence: the sweep's arithmetic on synthetic rows, and the production models' verdicts (S10)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.fielddoc import Kind
from galaxy.core.registry import INPUTS
from galaxy.specs import convergence, spec
from galaxy.specs.spec import Quantity, SpecError
from helpers import TINY, decl, impls, model, stage

GRIDS = {"n_R": (16,), "n_t": (10,)}  # TINY is n_R=8, n_t=5: one finer point per axis


def scalar_stage(name, fn, kind=Kind.SCALAR, **kw):
    return stage("s", (decl(name, kind, **kw),), compute=lambda ctx: {name: fn(ctx)})


def row(name, lo, hi, mode="pointwise", n=1, **kw):
    return Quantity(n, f"probe {name}", "dimensionless", name, lo, hi, mode, "probe", "probe", **kw)


def swept(st, q):
    m = model("m", st)
    return convergence.sweep(m, quantities=(q,), grids=GRIDS, base=TINY, impls=impls(st), table=INPUTS)


def test_the_axes_are_swept_separately():
    """GALAXY_INPUTS.md §10: N_R and N_t are not one knob, so no point moves both."""
    pts = convergence.points(GRIDS)
    assert [p.label for p in pts] == ["n_R=16", "n_t=10"]
    assert pts[0].spec(TINY) == TINY.replace(n_R=16) and pts[1].spec(TINY) == TINY.replace(n_t=10)
    for p in convergence.points():
        changed = {k for k in ("n_R", "n_t", "n_z", "n_phi") if getattr(p.spec(), k) != getattr(convergence.DEFAULT, k)}
        assert changed == {p.axis}


def test_a_scalar_that_moves_with_the_grid_is_unconverged():
    st = scalar_stage("f", lambda ctx: float(ctx.grid.spec.n_R))
    (d,) = swept(st, row("f", 0.0, 1.0))
    assert d.status == "unconverged" and d.default == 8.0 and d.values == {"n_R=16": 16.0, "n_t=10": 8.0}
    assert d.drifts == {"n_R=16": 8.0, "n_t=10": 0.0} and d.worst == 8.0 and d.worst_share == 8.0
    assert [p.code for p in convergence.problems([d], "m")] == ["unconverged"]
    assert convergence.summary([d])["unconverged"] == 1


def test_a_drift_inside_the_width_is_converged():
    st = scalar_stage("f", lambda ctx: ctx.grid.spec.n_R / 1000.0)
    (d,) = swept(st, row("f", 0.0, 1.0))
    assert d.status == "converged" and d.worst == pytest.approx(0.008) and d.worst_share == pytest.approx(0.008)
    assert convergence.problems([d], "m") == []
    still = scalar_stage("f", lambda ctx: 0.5)
    (d,) = swept(still, row("f", 0.0, 1.0))
    assert d.status == "converged" and d.worst == 0.0


def test_a_zero_width_target_is_untestable_not_failed():
    """Debt #17: a target with no width cannot judge a drift; the drift is still published."""
    st = scalar_stage("f", lambda ctx: float(ctx.grid.spec.n_R))
    q = row("f", 0.5, 0.5)
    assert not q.testable and q.width == 0.0
    (d,) = swept(st, q)
    assert d.status == "untestable" and d.worst == 8.0 and d.worst_share is None
    assert "debt #17" in d.reason
    assert convergence.problems([d], "m") == []


def test_a_row_that_reads_zero_everywhere_is_vacuous():
    st = scalar_stage("f", lambda ctx: 0.0)
    (d,) = swept(st, row("f", 1.0, 2.0))
    assert d.status == "vacuous" and convergence.problems([d], "m") == []


def test_a_category_that_flips_with_the_grid_is_unconverged():
    st = scalar_stage("c", lambda ctx: "a" if ctx.grid.spec.n_R < 10 else "b", Kind.CATEGORY_SCALAR, categories=("a", "b"))
    (d,) = swept(st, row("c", None, None, "qualitative", expect="a"))
    assert d.status == "unconverged" and d.width is None and d.drifts == {} and "n_R=16 reads 'b'" in d.reason
    steady = scalar_stage("c", lambda ctx: "a", Kind.CATEGORY_SCALAR, categories=("a", "b"))
    (d,) = swept(steady, row("c", None, None, "qualitative", expect="a"))
    assert d.status == "converged" and d.worst is None


def test_a_number_that_is_not_a_number_is_unconverged():
    st = scalar_stage("f", lambda ctx: float("nan") if ctx.grid.spec.n_t > 5 else 1.0)
    (d,) = swept(st, row("f", 0.0, 2.0))
    assert d.status == "unconverged" and "not a number" in d.reason and "n_t=10" in d.reason


def test_an_unpublished_row_is_not_yet_computable():
    st = scalar_stage("g", lambda ctx: 1.0)
    (d,) = swept(st, row("f", 0.0, 1.0))
    assert d.status == "not-yet-computable" and d.values == {} and d.default is None
    (d,) = swept(st, Quantity(1, "undefined", "dimensionless", None, None, None, "pointwise", "x", "src"))
    assert d.status == "not-yet-computable"


def test_a_recorded_row_does_not_stop_the_run_and_a_stale_one_does(monkeypatch):
    """The convergence analogue of a recorded miss: explained is not the same as fixed (rules B5, B10)."""
    entry = convergence.Unconverged(row=1, debt=1, since="S10", reason="probe", prediction="probe", model="m")
    monkeypatch.setattr(convergence, "_UNCONVERGED", (entry,))
    assert convergence.recorded("m") == {1: entry} and convergence.recorded("other") == {}
    moving = scalar_stage("f", lambda ctx: float(ctx.grid.spec.n_R))
    (d,) = swept(moving, row("f", 0.0, 1.0))
    assert d.status == "unconverged" and convergence.problems([d], "m") == []
    assert [p.code for p in convergence.problems([d], "other")] == ["unconverged"]
    still = scalar_stage("f", lambda ctx: 0.5)
    (d,) = swept(still, row("f", 0.0, 1.0))
    assert [p.code for p in convergence.problems([d], "m")] == ["stale-unconverged"]
    with pytest.raises(SpecError):
        convergence.Unconverged(row=99, debt=1, since="S10", reason="r", prediction="p")
    with pytest.raises(SpecError):
        convergence.Unconverged(row=1, debt=1, since="S10", reason="r", prediction=" ")
    monkeypatch.setattr(convergence, "_UNCONVERGED", (entry, entry))
    with pytest.raises(SpecError):
        convergence.recorded("m")


# --- the production models --------------------------------------------------

STATUSES = {
    "simple": {"converged": 17, "unconverged": 0, "untestable": 1, "vacuous": 0, "not-yet-computable": 6},
    "advanced": {"converged": 13, "unconverged": 0, "untestable": 1, "vacuous": 5, "not-yet-computable": 5},
}


@pytest.fixture(scope="module")
def drifts(prod):
    """Both models swept once, at the sweep the spec runs (about five seconds together)."""
    return convergence.sweep_models(list(prod[0]))


def test_every_acceptance_scalar_converges_in_both_models(model, drifts):
    """S10's measurement: the grid moves no row by more than a tenth of its width (D37 held)."""
    d = drifts[model.name]
    assert len(d) == 24 and [x.n for x in d] == list(range(1, 25))
    assert convergence.summary(d) == STATUSES[model.name]
    assert convergence.problems(d, model.name) == []
    by_n = {x.n: x for x in d}
    assert by_n[20].status == "untestable"  # debt #17: the source quotes no uncertainty
    # The largest drift at S10 is row 3's 5.6% of its width, from N_t; a ratchet, downward only.
    worst = max(x.worst_share for x in d if x.worst_share is not None)
    assert worst < 0.1, worst
    if model.name == "advanced":
        assert {x.n for x in d if x.status == "vacuous"} == {5, 7, 8, 9, 11}  # no valley, no thick disc (debt #27)
        assert by_n[24].status == "converged" and by_n[24].default == "single"


def test_the_radial_axis_is_the_cheap_one(model, drifts):
    """GALAXY_INPUTS.md §10's reading, seen from the other side: N_R moves nothing more than N_t does.

    Measured at S10 on every converged row and pinned as a fact about this
    grid, not a law — a stage that interpolated a scalar off the radial grid
    would break it, which is what D37 exists to prevent.
    """
    for x in drifts[model.name]:
        if x.status != "converged" or not x.drifts:
            continue
        radial = max(abs(v) for k, v in x.drifts.items() if k.startswith("n_R"))
        temporal = max(abs(v) for k, v in x.drifts.items() if k.startswith("n_t"))
        assert radial <= temporal + 1e-12 or radial < 0.02 * (x.width or math.inf), (x.n, x.drifts)


def test_the_report_lists_every_row_for_every_model(prod, drifts):
    out = convergence.report(list(prod[0]), drifts)
    assert out.startswith("convergence")
    assert "each axis swept alone: n_R in (200, 800); n_t in (1000, 4000)" in out
    for m in prod[0]:
        assert f"model {m.name}:" in out
    assert out.count("Total gas mass (<30 kpc)") == 2 and "published, not judged" in out
    assert "FAIL" not in out
    assert convergence.check(list(prod[0]), drifts) == []


def test_quick_sweep_is_a_subset_of_the_full_one():
    for axis, ns in convergence.QUICK.items():
        assert set(ns) <= set(convergence.SWEEP[axis])
