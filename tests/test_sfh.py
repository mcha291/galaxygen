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
    # Row 2 is inside since S17 took the spheroid's 13% out of the budget the disc accretes:
    # 1.82, from 2.08 with S16's tail (debt #47), 1.89 at S13, 1.97 while Sagittarius delivered
    # a tenth of the budget (debt #29, until S13), 1.14 before the merger-delivered second infall.
    assert 1.46 <= f["sfr"] <= 1.84
    assert f["sfr"] == pytest.approx(1.755, abs=0.06)  # 1.82 until S18's derived threshold held more gas at R0
    # Row 20 is at its zero-width target since S18 (1% over): 25% low at S17, 22% at S16, 48% with no extended component (debt #18, until S16).
    assert f["gas_mass_30kpc"] == pytest.approx(1.108e10, rel=0.05)  # 8.26e9 until S18; 8.55e9 until S17; 5.71e9 until S16
    assert f["hydrogen_mass_30kpc"] == pytest.approx(0.73 * f["gas_mass_30kpc"])
    assert 0.15 < f["gas_mass_30kpc"] / f["baryon_mass_total"] < 0.22  # 0.10-0.18 until S18 (0.141); 0.189 now


def test_star_formation_is_suppressed_below_the_threshold(model):
    """The threshold leaves an extended gas disc outside a truncated stellar one."""
    o = out(model)
    R, gas, psi = o.grid.R, o.fields["gas_surface_density"], o.fields["sfr_surface_density"]
    crit = o.fields["sf_threshold_surface_density"]  # the constant 5 until S18; Kennicutt's, by radius, since
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
    # 3% at S3, 4.6% at S17 (2.484 vs 2.605), 6.3% since S18 (2.441): the derived threshold holds more
    # gas inside R0 than outside, so the stars it leaves are a little more compact than the infall.
    assert abs(fitted / from_spin - 1.0) < 0.08, (fitted, from_spin)


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


def test_row_3_misses_high_once_the_halo_contracts(model):
    """The history of this row is the history of four wrong explanations (spec.MISSES[3]).

    S1 blamed the gas profile and predicted 246.4. S2 gave the gas a profile and got
    237.2, which was the stellar disc broadening at the same time. S3 corrected that and
    the miss returned to 256, high - and every audit blamed the compact disc. S13 did the
    conversion debt #12 named: the c_vir normalisation had been used as c200, and with
    c200 = 10.9 instead of 14.35 the row read 242.7, low - and named the halo's
    contraction as "several km/s", the lever that would close it. S14 modelled the
    contraction and it is 28 km/s at R0 (Gnedin et al. 2004's invariant; 38 for
    Blumenthal's): the row read 270.8, high by 20, and the epoch it wants is 0.7-1.0,
    below the cited 2-3. The magnitude was recalled, not measured (rule B4). S15 found the
    default epoch had been validated against measurements of the contracted halo and derived
    it from the LCDM median instead (2.5 -> 1.66, c200 10.9 -> 8.2): the row reads 260.1, high
    by 9, and its prediction names the bulge and the extended component (D117). S16 built the
    extended component and the row read 252.9; S17 built the spheroid, and the bulge was worth
    1.6 km/s and not the 5-8 D110's probe measured on the uncontracted halo - so the row read
    251.3, a quarter of a km/s outside, and the prediction that was left was the bar (D121).
    S18 read it inside at 250.96, by 0.04, and not on the bar: the merger's radial kick carries a
    fifth of the disc's stars outward across R0 (-0.2 km/s on the built model, -0.4 alone) and the
    basis-free velocity solver reads the S17 profile 0.09 lower than the exponential basis did
    (251.17); the derived threshold moves it not at all (D124). The bar's prediction stands unread.
    """
    o = out(model)
    v = o.fields["v_tangential_sun"]
    assert 245.0 <= v <= 251.0 and v > 250.5  # inside since S18, at the edge; 251.3 and outside until then
    assert v == pytest.approx(250.96, abs=0.3)  # 251.3 until S18 (251.17 on this solver); 252.9 until S17; 260.1 until S16; 270.8 until S15
    assert o.fields["halo_concentration"] == pytest.approx(8.24, abs=0.05)  # 10.9 until S15
    assert o.fields["halo_circular_velocity_sun"] - o.fields["halo_circular_velocity_sun_initial"] == pytest.approx(43.9, abs=0.5)  # 44.0 until S17; 42.8 until S15


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
    # 7.1 km/s since S17: the checkpoint-1 preview still has every baryon in one exponential, the
    # tail took 7.6% of it beyond 12 kpc (D119) and the spheroid 13% of it inside 2.5 kpc (D121).
    # 5.5 at S16, under 3 before it.
    assert 3.0 < abs(resolved - one_component) < 9.0


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
    # Since S17 row 1 is the disc's stars *plus* the spheroid, because the row's target is rows
    # 10 + 11 + 12 and includes the bulge; the surface density is the disc's alone, so the
    # difference is exactly the spheroid and this is what asserts it (D121).
    assert surface_to_mass(o.fields["stellar_surface_density"], R) == pytest.approx(
        o.fields["stellar_mass_total"] - o.fields["bulge_stellar_mass"]
    )


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


def test_the_tail_is_accreted_and_what_it_moved(model):
    """S16 (D119): the high-j tail joins the infall and the budget still closes.

    Row 20's hydrogen 4.17e9 -> 6.24e9, row 3 260.1 -> 252.9, row 4 unmoved at 2.49 (the check that
    the component is high enough in angular momentum, debt #18), row 2 1.89 -> 2.08 (debt #44).

    S17 (D121) took the other end of the same distribution out of the budget as the spheroid, so
    what accretes is the budget *minus the spheroid* and the numbers moved with it: hydrogen to
    6.03e9, row 3 to 251.3, row 2 to 1.82, row 4 still unmoved.
    """
    o = out(model)
    f, R = o.fields, o.grid.R
    total = np.trapezoid(f["infall_rate_history"], o.grid.t, axis=1)  # everything that arrived, per radius
    from galaxy.stages.sfh import surface_to_mass

    accreted = f["baryon_mass_total"] - f["bulge_stellar_mass"]
    assert surface_to_mass(total, R) == pytest.approx(accreted, rel=0.01)
    assert np.all(total[(R > 14.0) & (R < 24.0)] > 0.5)  # the tail is there: nothing accreted beyond 14 kpc until S16; it ends near 25
    # S18 derived the threshold and built the kick: hydrogen to 8.09e9, row 3 to 250.96, row 4 to 2.44,
    # row 2 to 1.755, row 1 to 4.75e10 (the disc makes fewer stars out of the same budget).
    assert f["hydrogen_mass_30kpc"] == pytest.approx(8.09e9, rel=0.01)  # 6.03e9 until S18; 6.24e9 until S17; 4.17e9 until S16
    assert f["v_tangential_sun"] == pytest.approx(250.96, abs=0.5)  # 251.3 until S18; 252.9 until S17; 260.1 until S16
    assert f["thin_disc_scale_length"] == pytest.approx(2.44, abs=0.02)  # 2.48 until S18, unmoved since S13
    assert f["sfr"] == pytest.approx(1.755, abs=0.03)  # 1.82 until S18; 2.08 until S17; 1.89 until S16
    assert f["stellar_mass_total"] == pytest.approx(4.75e10, rel=0.01)  # 5.03e10 until S18; 5.00e10 until S17; 5.29e10 until S16
    assert float(np.interp(20.0, R, f["gas_surface_density"])) == pytest.approx(3.33, abs=0.2)  # 3.75 until S18 (the threshold there is 3.9, so a little now forms stars); 0.6 until S16


def test_the_threshold_is_kennicutts_off_the_epicyclic_frequency(model):
    """S18 (D124, debt #47): Sigma_crit = alpha kappa sigma_g / 3.36 G, no longer the constant 5.

    11.5 Msun/pc2 at R0, 26 at 4 kpc, 4 at 20; the gas sits just under it inside 12 kpc, so the
    gas at R0 reads 10.8 against the observed 10-13 (6.3 until S18) and row 20's hydrogen 8.09e9
    against 8.0 (6.03e9 until S18). The cost is row 9 (0.135 -> 0.051), which debt #47 pre-committed
    to reading as the thick disc's fault, and it is recorded there.
    """
    from galaxy.stages.sfh import SFH, toomre_threshold

    assert "TOOMRE_ALPHA" in SFH.reads_constants and "GAS_DISPERSION" in SFH.reads_constants
    assert "SF_THRESHOLD" not in model.constants
    o = out(model)
    R, f = o.grid.R, o.fields
    crit = f["sf_threshold_surface_density"]
    G = float(model.constants["G"].value)
    assert np.allclose(crit, toomre_threshold(f["epicyclic_frequency"], 0.69, 6.0, G))
    assert float(np.interp(R_SUN, R, crit)) == pytest.approx(11.5, abs=0.2)
    assert float(np.interp(4.0, R, crit)) == pytest.approx(26.4, abs=0.5)
    assert float(np.interp(20.0, R, crit)) == pytest.approx(3.9, abs=0.2)
    gas = f["gas_surface_density"]
    inside = (R > 3.0) & (R < 12.0)
    assert np.all(gas[inside] < crit[inside]) and np.all(gas[inside] > 0.6 * crit[inside])  # regulated: held just under
    assert float(np.interp(R_SUN, R, gas)) == pytest.approx(10.8, abs=0.2)  # 6.3 until S18
    assert f["hydrogen_mass_30kpc"] == pytest.approx(8.09e9, rel=0.01)  # 6.03e9 until S18
    assert f["sfr"] == pytest.approx(1.755, abs=0.02)  # 1.82 until S18: still inside 1.46-1.84
    # what it holds inside: more gas than the Milky Way has there (the bar's job, debt #21), on the record
    assert float(np.interp(4.0, R, gas)) == pytest.approx(22.8, abs=0.5) and float(np.interp(2.0, R, gas)) == pytest.approx(33.0, abs=0.7)


def test_the_stars_formed_history_is_the_birth_history_moved_by_the_kick(model):
    """S18: sfh publishes where each step's stars are now; the vertical stage sorts that (rule A9)."""
    from galaxy.stages.disc import PC_PER_KPC
    from galaxy.stages.sfh import radial_transport, surface_to_mass

    o = out(model)
    R, t, f = o.grid.R, o.grid.t, o.fields
    dt = o.grid.spec.t_max / o.grid.spec.n_t
    ret = float(model.constants["RETURN_FRACTION"].value)
    born = (1.0 - ret) * PC_PER_KPC * f["sfr_surface_density_history"] * dt
    now = f["stars_formed_history"]
    assert np.array_equal(now.sum(axis=1), f["stellar_surface_density"])
    after = t > f["last_major_merger_time"]
    assert np.array_equal(now[:, after], born[:, after])           # untouched: born after the kick
    assert not np.allclose(now[:, ~after], born[:, ~after])        # moved: born before it
    area = 2.0 * np.pi * R * o.grid["R"].width
    assert float((now * area[:, None]).sum()) == pytest.approx(float((born * area[:, None]).sum()), rel=1e-12)
    # no major merger: the identity, exactly
    free = run(model, {"mergers": ()}, only=("stars_formed_history",))
    fb = (1.0 - ret) * PC_PER_KPC * free.fields["sfr_surface_density_history"] * dt
    assert np.array_equal(free.fields["stars_formed_history"], fb)
    # the pure function: a zero spread is the identity, a constant spread conserves ring mass
    assert np.array_equal(radial_transport(born, np.zeros_like(born), R, o.grid["R"].width), born)
    moved = radial_transport(born[:, :3], np.full((R.size, 3), 1.0), R, o.grid["R"].width)
    assert (moved * area[:, None]).sum() == pytest.approx((born[:, :3] * area[:, None]).sum(), rel=1e-12)
