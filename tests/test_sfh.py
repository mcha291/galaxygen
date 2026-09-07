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
from galaxy.core.registry import MergerEvent
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
    assert 4.0e10 <= f["stellar_mass_total"] <= 6.0e10          # row 1 passes
    # Row 2 overshoots: the second episode decays too slowly (debt #18). It read 1.97 while
    # Sagittarius delivered a tenth of the budget (debt #29, until S13).
    assert f["sfr"] == pytest.approx(1.89, abs=0.06)
    # Row 20 misses low by 29%, 48% like for like (debt #41): no extended accretion channel (debt #18).
    assert f["gas_mass_30kpc"] == pytest.approx(5.71e9, rel=0.05)
    assert f["hydrogen_mass_30kpc"] == pytest.approx(0.73 * f["gas_mass_30kpc"])
    assert 0.05 < f["gas_mass_30kpc"] / f["baryon_mass_total"] < 0.12


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


def test_the_two_disc_scale_lengths_agree(model):
    """Debt #13, discharged at S3.

    lambda_d predicts the disc scale length from angular momentum; the star
    formation history builds one. They are independent routes to the same
    observable and they must land on the same number, or one mechanism is wrong.
    """
    o = out(model)
    fitted, from_spin = o.fields["thin_disc_scale_length"], o.fields["disc_scale_length_spin"]
    assert abs(fitted / from_spin - 1.0) < 0.06, (fitted, from_spin)


def test_the_gas_disc_is_more_extended_than_the_stars(model):
    o = out(model)
    R = o.grid.R
    R_star = o.fields["thin_disc_scale_length"]
    R_gas = fit_scale_length(o.fields["gas_surface_density"], R, 1.0, 30.0)
    assert R_gas > R_star
    # Star formation is what makes it so: the gas arrives with the stars' own scale
    # length and the threshold protects what is left outside. The ratio lands in the
    # observed HI-to-optical 1.5-2, which is the check that the infall extent is right.
    assert 1.5 <= R_gas / R_star <= 2.1


def test_inside_out_growth_is_actually_inside_out(model):
    """The outer disc must still be forming stars after the inner disc has stopped."""
    o = out(model)
    R, psi_hist = o.grid.R, o.fields["sfr_surface_density_history"]
    inner = int(np.argmin(np.abs(R - 3.0)))
    outer = int(np.argmin(np.abs(R - 12.0)))
    peak_inner = o.grid.t[int(np.argmax(psi_hist[inner]))]
    peak_outer = o.grid.t[int(np.argmax(psi_hist[outer]))]
    assert peak_outer > peak_inner


def test_row_3_misses_low_once_the_concentration_is_converted(model):
    """The history of this row is the history of three wrong explanations (spec.MISSES[3]).

    S1 blamed the gas profile and predicted 246.4. S2 gave the gas a profile and got
    237.2, which was the stellar disc broadening at the same time. S3 corrected that and
    the miss returned to 256, high - and every audit blamed the compact disc. S13 did the
    conversion debt #12 named: the c_vir normalisation had been used as c200, and with
    c200 = 10.9 instead of 14.35 the row reads 242.7, low. An extended component would
    lower it further; what is missing inside R0 is the bulge (debt #11).
    """
    o = out(model)
    v = o.fields["v_tangential_sun"]
    assert v < 245.0
    assert v == pytest.approx(242.7, abs=1.0)
    assert o.fields["halo_concentration"] == pytest.approx(10.9, abs=0.05)


def test_the_resolved_curve_supersedes_the_checkpoint_one_one(model):
    o = out(model)
    R = o.grid.R
    resolved = float(np.interp(R_SUN, R, o.fields["circular_velocity_resolved"]))
    assert resolved == pytest.approx(o.fields["v_circular_sun"], rel=3e-3)
    assert o.fields["v_tangential_sun"] == pytest.approx(o.fields["v_circular_sun"] + 12.24)
    # Now that the infall carries the disc's own scale length, splitting the baryons
    # into stars and gas barely moves v_c at R0 - which is itself the result behind
    # debt #18: the split was never what row 3 needed, an extended component is.
    one_component = float(np.interp(R_SUN, R, o.fields["circular_velocity"]))
    assert abs(resolved - one_component) < 3.0


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


def test_the_second_infall_is_the_merger(model):
    """Ruling 11: the merger delivers the gas, so removing it removes the second episode."""
    o = out(model)
    assert o.fields["second_infall_share"] == pytest.approx(0.505, abs=0.01)  # 0.5 Gaia-Enceladus + 0.01 of the rest, Sagittarius (S13)
    free = run(model, {"mergers": ()})
    assert free.fields["second_infall_share"] == 0.0
    assert free.fields["major_merger_count"] == 0.0
    # Without the late delivery the present-day rate collapses: that is the mechanism.
    assert free.fields["sfr"] < 0.7 * o.fields["sfr"]


def test_the_merger_gas_arrives_at_its_own_epoch_and_the_grid_no_longer_sees_a_step(model):
    """Debt #30, fixed at S13: sfh accretes merger_delivery instead of a step at the last major merger.

    The register's prediction was that feeding the delivery windows in would remove rows 1
    and 10's non-monotone movement with N_t (5.2876, 5.2762, 5.2817 x 1e10 at 1000, 2000,
    4000). It did: monotone, and a spread of 0.007%.
    """
    from galaxy.stages.sfh import SFH

    assert "merger_delivery" in SFH.requires and "last_major_merger_time" not in SFH.requires
    ms = [float(run(model, grid=GridSpec(n_t=n), only=("stellar_mass_total",)).fields["stellar_mass_total"])
          for n in (1000, 2000, 4000)]
    assert ms[0] >= ms[1] >= ms[2] or ms[0] <= ms[1] <= ms[2]
    assert (max(ms) - min(ms)) / ms[1] < 5e-4
    # Sagittarius' gas arrives around 8.8 Gyr now, not with Gaia-Enceladus at 3.8: the infall with
    # the event minus without it peaks after 8.8 (the budget is fixed, so read the positive part).
    ge = (MergerEvent(3.8, 0.25, 0.5, "probe"),)
    a = run(model, only=("infall_rate_history",))
    b = run(model, {"mergers": ge}, only=("infall_rate_history",))
    extra = np.maximum((a.fields["infall_rate_history"] - b.fields["infall_rate_history"]).sum(axis=0), 0.0)
    assert 8.5 < a.grid.t[int(np.argmax(extra))] < 10.5
