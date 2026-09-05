"""convergence: N_R, N_t and N_z swept one at a time; a drift wider than the target is a problem.

The production sweep is the record (``python -m galaxy.specs``); here it runs at
half size, and the detector is checked on a stage built to drift (rule B3).
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.fielddoc import Kind
from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS
from galaxy.specs import convergence
from galaxy.specs.spec import QUANTITIES
from helpers import decl, impls, model, stage

SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
HALF = {"n_R": (24, 48), "n_t": (32, 64), "n_z": (4, 8)}


def test_a_scalar_that_moves_with_the_grid_is_caught():
    """Row 1 (total stellar mass, 4-6e10) published as a function of N_R alone."""
    s = stage("s", (decl("stellar_mass_total", Kind.SCALAR, unit="Msun"),),
              compute=lambda ctx: {"stellar_mass_total": 5e10 + 1e9 * ctx.grid.spec.n_R})
    rep = convergence.sweep(model("m", s), HALF, SMALL, impls=impls(s), table=INPUTS)
    by_axis = {d.axis: d for d in rep.drifts if d.row == 1}
    assert by_axis["n_R"].status == "drifts" and by_axis["n_R"].drift == pytest.approx(2.4e10)
    assert by_axis["n_t"].status == "ok" and by_axis["n_z"].status == "ok"
    assert [p.code for p in rep.problems] == ["drift"]
    steady = stage("s", (decl("stellar_mass_total", Kind.SCALAR, unit="Msun"),),
                   compute=lambda ctx: {"stellar_mass_total": 5e10})
    assert convergence.sweep(model("m", steady), HALF, SMALL, impls=impls(steady), table=INPUTS).ok


def test_a_zero_width_target_is_untestable_not_failed():
    """Debt #17: row 20's target has no width, so no drift can be judged against it."""
    s = stage("s", (decl("gas_mass_30kpc", Kind.SCALAR, unit="Msun"),),
              compute=lambda ctx: {"gas_mass_30kpc": 8e9 + 1e7 * ctx.grid.spec.n_t})
    rep = convergence.sweep(model("m", s), HALF, SMALL, impls=impls(s), table=INPUTS)
    assert {d.status for d in rep.drifts} == {"untestable"} and rep.ok


def test_a_category_that_changes_is_a_drift():
    s = stage("s", (decl("alpha_sequence", Kind.CATEGORY_SCALAR, categories=("single", "bimodal_narrow", "bimodal_wide"), ramp=None),),
              compute=lambda ctx: {"alpha_sequence": "single" if ctx.grid.spec.n_t > 32 else "bimodal_wide"})
    rep = convergence.sweep(model("m", s), HALF, SMALL, impls=impls(s), table=INPUTS)
    by_axis = {d.axis: d for d in rep.drifts}
    assert by_axis["n_t"].status == "drifts" and by_axis["n_R"].status == "ok"


def test_the_production_scalars_hold_under_a_half_sweep(model):
    """The record is the full sweep; this is the same instrument at half size, per model."""
    rep = convergence.sweep(model, convergence.QUICK)
    assert rep.ok, rep.problems
    rows = {d.row for d in rep.drifts}
    assert {1, 2, 3, 4, 22, 23} <= rows
    if model.name == "advanced":
        assert 24 in rows
    assert all(d.status == "statistical" for d in rep.drifts if d.row in (16, 17))
    assert all(d.status == "untestable" for d in rep.drifts if d.row == 20)
    assert not any(d.status == "drifts" for d in rep.drifts)


def test_every_axis_is_swept_alone():
    """N_R and N_t are not one knob (GALAXY_INPUTS.md §10): each sweep holds the others at the default."""
    assert set(convergence.SWEEPS) == {"n_R", "n_t", "n_z"}
    for axis, sizes in convergence.SWEEPS.items():
        assert getattr(GridSpec(), axis) in sizes and len(sizes) >= 3
    assert all(q.mode in ("pointwise", "statistical", "qualitative") for q in QUANTITIES)


def test_report_runs(prod):
    out = convergence.report(list(prod[0]), convergence.QUICK)
    assert "convergence" in out and "model advanced" in out and "untestable" in out
