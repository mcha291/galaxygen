"""The star formation history: the gas/star split, and what it did to row 3.

S1 predicted (spec.MISSES[3]) that giving the gas its own profile would lower
the solar tangential velocity by about 5 km/s, into row 3's window. S2 ran the
mechanism. The prediction is tested here as a prediction — it is allowed to
fail, and it does.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.stages.sfh import fit_scale_length, surface_to_mass

R_SUN = 8.2


def out(model, **inputs):
    return run(model, inputs or None)


def test_the_baryons_are_conserved(model):
    """Every baryon the halo handed over is a star, or gas, or has not fallen in yet."""
    o = out(model)
    f = o.fields
    accounted = f["stellar_mass_total"] + f["gas_mass_30kpc"]
    assert accounted <= f["baryon_mass_total"] * 1.0001
    # The infall is exponential and 13.8 Gyr is many e-folding times at small R,
    # so almost all of it has arrived; what is left out is the outer disc's tail.
    assert accounted / f["baryon_mass_total"] > 0.95


def test_the_split_is_computed_not_assumed(model):
    o = out(model)
    f = o.fields
    assert 4.0e10 <= f["stellar_mass_total"] <= 6.0e10          # row 1
    assert 1.46 <= f["sfr"] <= 1.84                              # row 2
    assert f["gas_mass_30kpc"] == pytest.approx(8.0e9, rel=0.15)  # row 20, 6% out
    assert 0.10 < f["gas_mass_30kpc"] / f["baryon_mass_total"] < 0.20


def test_star_formation_is_suppressed_below_the_threshold(model):
    """The threshold leaves an extended gas disc outside a truncated stellar one."""
    o = out(model)
    R, gas, psi = o.grid.R, o.fields["gas_surface_density"], o.fields["sfr_surface_density"]
    crit = 5.0
    # Suppressed, not switched: the cutoff is smooth by numerical necessity (D46),
    # so the right check is against the rate the unsuppressed law would give, not zero.
    deep = gas < 0.5 * crit
    unsuppressed = 2.5e-4 * np.maximum(gas, 0.0) ** 1.4
    assert np.all(psi[deep] < 0.05 * unsuppressed[deep] + 1e-30)
    assert np.all(psi[deep] < 1e-2 * psi.max())
    assert np.any(psi > 0.0)
    assert gas[R > R[np.argmax(psi)]].sum() > 0.0


def test_the_star_formation_rate_converges(model):
    """A hard threshold made this number grid-alignment noise; the smooth one does not.

    This is the check that found the defect (rules B1, B7): the gas mass and the
    gradient converged all along, and only the SFR wandered — between 1.47 and
    1.79 with no trend in either N_R or N_t.
    """
    rates = [
        run(model, grid=GridSpec(n_R=nr, n_t=nt, n_z=6)).fields["sfr"]
        for nr, nt in ((200, 1000), (400, 2000), (800, 2000), (400, 4000))
    ]
    spread = (max(rates) - min(rates)) / np.mean(rates)
    assert spread < 0.01, f"SFR spread {spread:.3f} across the grid sweep: {rates}"


def test_the_gas_disc_is_more_extended_than_the_stars(model):
    o = out(model)
    R = o.grid.R
    R_star = o.fields["thin_disc_scale_length"]
    R_gas = fit_scale_length(o.fields["gas_surface_density"], R, 1.0, 30.0)
    assert R_gas > R_star
    # Recorded, not asserted to be right: the ratio comes out near 2.9 against an
    # observed HI-to-optical 1.5-2 (debt #13). Bound it loosely so a change is loud.
    assert 2.0 < R_gas / R_star < 4.0


def test_inside_out_growth_is_actually_inside_out(model):
    """The outer disc must still be forming stars after the inner disc has stopped."""
    o = out(model)
    R, psi_hist = o.grid.R, o.fields["sfr_surface_density_history"]
    inner = int(np.argmin(np.abs(R - 3.0)))
    outer = int(np.argmin(np.abs(R - 12.0)))
    peak_inner = o.grid.t[int(np.argmax(psi_hist[inner]))]
    peak_outer = o.grid.t[int(np.argmax(psi_hist[outer]))]
    assert peak_outer > peak_inner


def test_S1s_prediction_about_row_3_was_directionally_right_and_numerically_wrong(model):
    """spec.MISSES[3], written at S1, said the split would bring v_tan to about 246.4."""
    o = out(model)
    v = o.fields["v_tangential_sun"]
    assert v < 256.09          # S1's value: the direction was right
    assert not 245.0 <= v <= 251.0  # and it overshot the window rather than landing in it
    assert v == pytest.approx(237.2, abs=1.0)
    # The overshoot is the stellar disc broadening at the same time (debt #13).
    assert o.fields["thin_disc_scale_length"] > o.fields["disc_scale_length_spin"]


def test_the_resolved_curve_supersedes_the_checkpoint_one_one(model):
    o = out(model)
    R = o.grid.R
    resolved = float(np.interp(R_SUN, R, o.fields["circular_velocity_resolved"]))
    assert resolved == pytest.approx(o.fields["v_circular_sun"], rel=3e-3)
    assert o.fields["v_tangential_sun"] == pytest.approx(o.fields["v_circular_sun"] + 12.24)
    # It is a different number from the one-component curve, which is the point.
    assert abs(resolved - float(np.interp(R_SUN, R, o.fields["circular_velocity"]))) > 5.0


def test_scalars_do_not_move_with_grid_resolution(model):
    """An acceptance number that moved with N_R would make the S10 sweep meaningless (D37)."""
    coarse = run(model, grid=GridSpec(n_R=200, n_t=1000, n_z=6))
    fine = run(model, grid=GridSpec(n_R=400, n_t=2000, n_z=6))
    for name in ("stellar_mass_total", "sfr", "gas_mass_30kpc", "v_tangential_sun"):
        assert coarse.fields[name] == pytest.approx(fine.fields[name], rel=0.05), name


def test_surface_densities_integrate_to_their_masses(model):
    o = out(model)
    R = o.grid.R
    assert surface_to_mass(o.fields["gas_surface_density"], R) == pytest.approx(o.fields["gas_mass_30kpc"])
    assert surface_to_mass(o.fields["stellar_surface_density"], R) == pytest.approx(o.fields["stellar_mass_total"])
