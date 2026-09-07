"""The calibration audit (rule B10): every constant fitted while a mechanism was missing, re-examined (S10).

Ported to main at S11 from the two blind runs of the gamma pair (session-10-gamma,
session-10-gamme-run-2); the debt numbers are main's (GALAXY_INPUTS.md §11 #41-#45).

S9 gave the advanced model outflows, a delay-time distribution and a chemical
thin/thick split. This file re-runs the constants and the predictions that were
calibrated or made before those mechanisms existed, and pins what it found.
Nothing here is fixed — rule B10 says a constant fitted against a missing
mechanism has no claim on its value, not which value to give it — and every
finding is on the register (GALAXY_INPUTS.md §11) with a prediction that could
kill it (rule B4). The numbers are pinned loosely, as measurements to spot a
regression by, never as targets.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.fielddoc import Kind
from galaxy.core.registry import Constant, MergerEvent, Model
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages.halo import mu
from helpers import decl

R_SUN = 8.2
Q = {q.n: q for q in spec.QUANTITIES}


@pytest.fixture(scope="module")
def simple(prod):
    return prod[0].get("simple")


@pytest.fixture(scope="module")
def advanced(prod):
    return prod[0].get("advanced")


def with_constant(model, name, value):
    c = dict(model.constants)
    c[name] = Constant(value, c[name].unit, "probe")
    return Model(name="probe", about="probe", stages=model.stages, constants=c)


def one_merger(gas_fraction: float) -> tuple[MergerEvent, ...]:
    return (MergerEvent(3.8, 0.25, gas_fraction, "probe: Gaia-Enceladus alone"),)


def inside(n: int, value: float) -> bool:
    return Q[n].lo <= value <= Q[n].hi


# --- debt #12: the concentration is quoted at the wrong overdensity -----------

KIN = ("v_tangential_sun", "halo_concentration", "v_circular_sun")


def c200_from_cvir(c_vir: float, delta_vir: float = 101.0) -> float:
    """The c₂₀₀ of the NFW halo whose concentration at ``delta_vir`` ρ_crit is ``c_vir``.

    The mean density inside x scale radii goes as μ(x)/x³, so the two satisfy
    μ(c₂₀₀)/c₂₀₀³ = (200/Δ_vir) μ(c_vir)/c_vir³; bisected, μ(x)/x³ being monotone.
    """
    target = (200.0 / delta_vir) * mu(c_vir) / c_vir**3
    lo, hi = 1.0, c_vir
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mu(mid) / mid**3 > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def test_debt_12_the_concentration_is_converted_and_row_3_reads_low(simple):
    """K = 4.1 normalises c_vir; until S13 it was applied to c₂₀₀ unconverted (debt #12).

    Δ_vir ≈ 101 ρ_crit for Ω_M = 0.3 [recall: Bryan & Norman 1998] against the model's
    200: the same halo is less concentrated at R₂₀₀ than at R_vir. The halo stage converts
    since S13; this pins what the conversion is worth and where it leaves row 3.
    """
    K, z_f = simple.constants["CONCENTRATION_NORM"].value, 2.5
    c_vir = K * (1.0 + z_f)
    c200 = c200_from_cvir(c_vir)
    assert c_vir == pytest.approx(14.35) and c200 == pytest.approx(10.9, abs=0.05)
    # The conversion is a property of the profile, checked by inverting it (rule B3).
    assert mu(c200) / c200**3 == pytest.approx((200.0 / 101.0) * mu(c_vir) / c_vir**3, rel=1e-9)
    f = run(simple, only=KIN).fields
    assert f["halo_concentration_virial"] == pytest.approx(c_vir) and f["halo_concentration"] == pytest.approx(c200, abs=0.05)
    # Row 3 read 256.2 unconverted; converted it reads 242.7 - through the 245-251 window and out the other side.
    assert f["v_tangential_sun"] == pytest.approx(242.7, abs=0.5) and f["v_tangential_sun"] < Q[3].lo
    # ...and the cited z_f = 2-3 spans 13 km/s on row 3; the row wants 2.7-3.1, the top of the range.
    lo, hi = (run(simple, {"halo_assembly_z": z}, only=KIN).fields["v_tangential_sun"] for z in (2.0, 3.0))
    assert lo == pytest.approx(236.4, abs=0.5) and hi == pytest.approx(249.2, abs=0.5)
    assert 12.0 < hi - lo < 14.0


# --- debts #17 and #41: what the row 20 target is, and what it counts ----------


def test_debt_17_the_zero_width_rows_say_no_testable_target():
    """The source quotes no uncertainty [verified: arXiv:1511.08877, abstract and §4.2]; the table says so."""
    for n in (14, 20, 21):
        assert Q[n].lo == Q[n].hi and Q[n].width == 0.0 and not Q[n].testable
    assert all(q.testable for q in spec.QUANTITIES if q.n not in (14, 20, 21))
    # Row 14 was exempt while a statistical row passed on its interval's reach; since S13 it
    # passes on its median, which no float meets at zero width either (debts #17, #38).
    d = decl("hydrogen_mass_30kpc", Kind.SCALAR, unit="Msun")
    r = spec.evaluate(Q[20], {"hydrogen_mass_30kpc": 8.0e9 * (1 + 1e-9)}, {"hydrogen_mass_30kpc": d}, "m")
    assert r.status == "fail" and "no testable target" in r.reason and "debt #17" in r.reason
    # Row 20 stays a recorded miss under debt #18: the model is low on any reading (rule B5).
    assert 20 in spec.MISSES and spec.MISSES[20].debt == 18 and 20 in spec.MISSES_ADVANCED


def test_debt_41_row_20_compares_total_gas_with_a_hydrogen_mass(model):
    """The target is HI + H₂ — hydrogen; the gas field is every retained baryon not in a star, helium included.

    Since S13 the row reads hydrogen_mass_30kpc = (1 − Y) × gas_mass_30kpc (debt #41).
    """
    f = run(model, only=("gas_mass_30kpc", "hydrogen_mass_30kpc", "stellar_mass_total", "baryon_mass_total")).fields
    Y = model.constants["HELIUM_MASS_FRACTION"].value
    assert Y == 0.27 and Q[20].field == "hydrogen_mass_30kpc"
    assert f["gas_mass_30kpc"] + f["stellar_mass_total"] <= f["baryon_mass_total"] * 1.0001
    assert f["gas_mass_30kpc"] == pytest.approx(5.71e9, rel=0.02)
    assert f["hydrogen_mass_30kpc"] == pytest.approx(f["gas_mass_30kpc"] * (1.0 - Y))
    assert 1.0 - f["gas_mass_30kpc"] / 8.0e9 == pytest.approx(0.29, abs=0.01)  # the miss as the table read it until S13
    assert 1.0 - f["hydrogen_mass_30kpc"] / 8.0e9 == pytest.approx(0.48, abs=0.01)  # like for like, which the table reads now


# --- debt #26: the super-solar centre ------------------------------------------


def centre(model, **consts):
    m = model
    for k, v in consts.items():
        m = with_constant(m, k, v)
    o = run(m, only=("metallicity_gradient",))
    R, feh = o.grid.R, o.fields["feh_gas"]
    over = R[np.isfinite(feh) & (feh > 0.5)]
    return {
        "max": float(np.nanmax(feh)),
        "out_to": float(over.max()) if over.size else 0.0,
        "sun": float(np.interp(R_SUN, R, feh)),
        "at_4": float(np.interp(4.0, R, feh)),
        "gradient": o.fields["metallicity_gradient"],
    }


def test_debt_26_the_centre_is_the_missing_mass_loss_not_the_fitted_constant(simple, advanced):
    s, a = centre(simple), centre(advanced)
    # S13 moved the centre down: Sagittarius no longer delivers a tenth of the budget early, and
    # WIND_SPEED was refitted to the converted potential. The simple model's gas no longer reaches +0.5 at all.
    assert s["max"] == pytest.approx(0.46, abs=0.05) and s["out_to"] == 0.0
    assert a["max"] == pytest.approx(1.36, abs=0.05) and a["out_to"] == pytest.approx(2.5, abs=0.15)
    assert a["at_4"] == pytest.approx(0.25, abs=0.03)  # just outside row 22's 4-12 kpc fit range
    # The one fitted constant does not reach the centre: it moves the level at R₀, not the peak or the tilt.
    cold, hot = centre(advanced, WIND_SPEED=800.0), centre(advanced, WIND_SPEED=1300.0)
    assert cold["sun"] - hot["sun"] > 0.3
    assert abs(cold["max"] - hot["max"]) < 0.35
    assert abs(cold["gradient"] - hot["gradient"]) < 0.005


# --- debt #27: the register's prediction, run ----------------------------------

CHEM = ("metallicity_gradient", "alpha_sequence")


def test_debt_27s_prediction_ran_a_fast_inner_disc_opens_a_valley_and_closes_row_22_doing_it(advanced):
    # With the default merger list, n = 2 at either τ₀ and n = 3 at τ₀ = 7 stay single. n = 3 at τ₀ = 1
    # opens the valley since S13, when Sagittarius stopped delivering a tenth of the budget beside
    # Gaia-Enceladus (debt #29): that gas was what kept the fast inner disc's track single.
    for n, tau in ((2.0, 7.0), (2.0, 1.0), (3.0, 7.0)):
        f = run(advanced, {"inside_out_index": n, "infall_timescale": tau}, only=CHEM).fields
        assert f["alpha_sequence"] == "single" and f["alpha_dip_depth"] == 0.0, (n, tau)
    f = run(advanced, {"inside_out_index": 3.0, "infall_timescale": 1.0}, only=CHEM).fields
    assert f["alpha_sequence"] == "bimodal_wide" and f["alpha_dip_depth"] > 0.55
    # With Gaia-Enceladus alone, a fast inner disc does open it — and the gradient doubles.
    for inputs in (
        {"inside_out_index": 3.0, "infall_timescale": 7.0, "mergers": one_merger(0.2)},
        {"inside_out_index": 3.0, "infall_timescale": 1.0, "mergers": one_merger(0.5)},
    ):
        f = run(advanced, inputs, only=CHEM).fields
        assert f["alpha_sequence"] == "bimodal_wide", inputs
        assert 0.55 < f["alpha_dip_depth"] < 0.70 and f["alpha_split"] == pytest.approx(0.40, abs=0.02)
        assert f["high_alpha_feh_span"] > 1.0
        assert f["metallicity_gradient"] < -0.12  # row 22's window is [-0.069, -0.049]
    # The same small merger with n = 1 stays single: the index is what opens it.
    f = run(advanced, {"inside_out_index": 1.0, "infall_timescale": 7.0, "mergers": one_merger(0.2)}, only=CHEM).fields
    assert f["alpha_sequence"] == "single"


def test_the_thick_disc_a_valley_would_find_is_the_simple_models_compact_one(advanced):
    """What rows 5, 7-11 read the moment the split selects something: recorded so the next session knows the shape."""
    inputs = {"inside_out_index": 3.0, "infall_timescale": 7.0, "mergers": one_merger(0.2)}
    f = run(advanced, inputs, only=("thick_thin_surface_density_ratio",)).fields
    assert f["thick_disc_stellar_mass"] == pytest.approx(6.6e9, rel=0.05) and inside(11, f["thick_disc_stellar_mass"])
    assert f["thick_disc_scale_length"] == pytest.approx(0.71, abs=0.05) and not inside(5, f["thick_disc_scale_length"])
    assert f["thick_disc_scale_height"] == pytest.approx(1113.0, abs=30.0) and not inside(7, f["thick_disc_scale_height"])
    assert f["thick_thin_surface_density_ratio"] == pytest.approx(0.011, abs=0.002)  # row 9: an order of magnitude low
    assert f["thin_disc_scale_height"] == pytest.approx(443.0, abs=15.0) and not inside(6, f["thin_disc_scale_height"])


# --- debt #28: the flattening, measured in both models -------------------------

GRADS = ("metallicity_gradient_old", "metallicity_gradient_young")


def test_debt_28_migration_flattens_the_old_population_from_a_steeper_start_in_both_models(model):
    still = run(model, {"migration_efficiency": 0.0}, only=GRADS).fields
    moved = run(model, only=GRADS).fields
    # S13 (a physical Sagittarius, debt #29) flattened the unmigrated old gradient from -0.105 / -0.129.
    old0, young0 = {"simple": (-0.084, -0.020), "advanced": (-0.106, -0.062)}[model.name]
    assert still["metallicity_gradient_old"] == pytest.approx(old0, abs=0.004)
    assert still["metallicity_gradient_young"] == pytest.approx(young0, abs=0.004)
    # The kernel takes the old gradient down by a factor 5-13; the young/old ratio lands at 3.0-3.3 in both.
    assert 5.0 < still["metallicity_gradient_old"] / moved["metallicity_gradient_old"] < 14.0
    assert moved["metallicity_gradient_young"] / moved["metallicity_gradient_old"] == pytest.approx(3.15, abs=0.2)


# --- debt #42: row 6 at the edge in both models, for opposite reasons ----------

HEIGHTS = ("thin_disc_scale_height", "thick_disc_scale_height")


def test_debt_42_row_6_is_at_the_edge_of_its_window_in_both_models(simple, advanced):
    s = run(simple, only=HEIGHTS).fields
    a = run(advanced, only=HEIGHTS).fields
    assert Q[6].lo <= s["thin_disc_scale_height"] <= Q[6].lo + 5.0  # 255 against a floor of 250
    # 358 against a ceiling of 350: a recorded miss since S13 (326 while Sagittarius delivered young gas).
    assert Q[6].hi < a["thin_disc_scale_height"] <= Q[6].hi + 15.0
    # SECULAR_HEATING was set from the 10 Gyr end of the AVR (D54); 20 and 30 km/s fail the two models at opposite ends.
    low_s = run(with_constant(simple, "SECULAR_HEATING", 20.0), only=HEIGHTS).fields["thin_disc_scale_height"]
    high_a = run(with_constant(advanced, "SECULAR_HEATING", 30.0), only=HEIGHTS).fields["thin_disc_scale_height"]
    assert low_s < Q[6].lo and high_a > Q[6].hi
    # MERGER_HEATING calibrates row 7 in the simple model and row 6 in the advanced one, where the heated stars are thin.
    for k, row7, row6 in ((60.0, 619.0, 303.0), (180.0, 1747.0, 451.0)):
        hot_s = run(with_constant(simple, "MERGER_HEATING", k), only=HEIGHTS).fields
        hot_a = run(with_constant(advanced, "MERGER_HEATING", k), only=HEIGHTS).fields
        assert hot_s["thick_disc_scale_height"] == pytest.approx(row7, rel=0.02)
        assert hot_s["thin_disc_scale_height"] == pytest.approx(254.6, abs=1.0)
        assert hot_a["thin_disc_scale_height"] == pytest.approx(row6, rel=0.02)
        assert hot_a["thick_disc_scale_height"] == 0.0


# --- debt #45: the constant that does nothing carries row 22 --------------------

STRUCT = (
    "stellar_mass_total", "sfr", "v_tangential_sun", "thin_disc_scale_length", "gas_mass_30kpc",
    "metallicity_gradient", "thick_disc_scale_length", "thick_disc_stellar_mass",
)


def test_debt_45_the_infall_scale_ratio_trades_the_structure_rows_against_the_gas_rows(model):
    by = {r: run(with_constant(model, "GAS_DISC_SCALE_RATIO", r), only=STRUCT).fields for r in (0.8, 1.0, 1.25, 1.5)}
    # Upstream is shared, so rows 1-4 and 20 read the same in both models.
    assert by[0.8]["thin_disc_scale_length"] == pytest.approx(2.00, abs=0.05)
    assert by[1.5]["thin_disc_scale_length"] == pytest.approx(3.68, abs=0.05) and not inside(4, by[1.5]["thin_disc_scale_length"])
    assert by[1.5]["gas_mass_30kpc"] == pytest.approx(9.17e9, rel=0.02)
    assert by[1.5]["v_tangential_sun"] == pytest.approx(222.7, abs=0.5) and by[1.5]["sfr"] == pytest.approx(2.67, abs=0.05)
    grads = [by[r]["metallicity_gradient"] for r in (0.8, 1.0, 1.25, 1.5)]
    assert grads[0] < grads[1] < grads[2] < grads[3]
    if model.name == "simple":
        # At 1.25 the merger's thick disc reaches row 5 (1.84 kpc) and not row 11 (1.19e10); at 1.5 it
        # overshoots row 5 (2.22) — and rows 3, 4 and 22 are gone. (Until S13, with Sagittarius' extra
        # pre-merger gas, 1.5 reached rows 5 and 11 together.)
        assert inside(5, by[1.25]["thick_disc_scale_length"]) and not inside(11, by[1.25]["thick_disc_stellar_mass"])
        assert not inside(5, by[1.5]["thick_disc_scale_length"])
        assert not inside(3, by[1.5]["v_tangential_sun"])
        assert grads == pytest.approx([-0.047, -0.024, -0.017, -0.016], abs=0.003)
    else:
        # Row 22 passes only within a tenth of 1.0: -0.086 at 0.8, -0.047 at 1.25.
        assert grads == pytest.approx([-0.086, -0.057, -0.047, -0.043], abs=0.003)
        assert not inside(22, grads[0]) and inside(22, grads[1]) and not inside(22, grads[2])


# --- debt #21: row 15 is the constant --------------------------------------------


def test_row_15_is_the_bar_constant_times_the_scale_length(model):
    f = run(model, only=("bar_half_length",)).fields
    ratio = model.constants["BAR_LENGTH_RATIO"].value
    assert f["bar_half_length"] == pytest.approx(ratio * f["thin_disc_scale_length"], rel=1e-12)
    assert ratio == 2.0 and inside(15, f["bar_half_length"])
    # A scale length outside 2.4-2.6 kpc takes row 15 out of its window: a check on R_d, not on the bar.
    assert Q[15].lo / ratio == pytest.approx(2.4) and Q[15].hi / ratio == pytest.approx(2.6)


# --- the register moved with the findings ----------------------------------------


def test_the_register_carries_the_s10_findings():
    import progress  # tools/, on sys.path via conftest

    text = progress.read(progress.INPUTS)
    # main's #29-#33 (its own two runs), beta's #34-#40, the gamma pair's #41-#45 (S11, D99);
    # S12 discharged #35, #37 and #40 (D104); S13 discharged #29, #30, #38 and #41 (D106-D109).
    assert progress.debt_counts(text) == (31, 14)
    for item in (
        "29. ~~**The Sagittarius default",
        "34. **The acceptance table reads nothing inside 4 kpc",
        "38. ~~**A statistical row tests overlap",
        "41. ~~**Acceptance row 20 compares total gas with a hydrogen mass",
        "42. **Row 6 passes at the edge",
        "43. **`NET_YIELD` and `WIND_SPEED` are each fitted",
        "44. **Row 2 cannot see past `KS_NORM`",
        "45. **`GAS_DISC_SCALE_RATIO` multiplies nothing",
    ):
        assert item in text, item


# --- gamma's probes (session-10-gamma, tests/test_calibration.py), ported at S11 -----


def with_constants(model, **values):
    m = model
    for k, v in values.items():
        m = with_constant(m, k, v)
    return m


def scalar(model, name, inputs=None, **consts):
    m = with_constants(model, **consts) if consts else model
    return float(run(m, inputs, only=(name,)).fields[name])


def feh_at_sun(model, **consts):
    o = run(with_constants(model, **consts) if consts else model, only=("feh_gas",))
    return float(o.fields["feh_gas"][int(np.argmin(np.abs(o.grid.R - R_SUN)))])


def test_debt_44_row_2_cannot_see_past_ks_norms_own_uncertainty(simple):
    """KS_NORM is (2.5 +/- 0.7) x 10^-4 and deliberately unfitted. Its 1-sigma swing is 2.5x row 2's miss."""
    lo, mid, hi = (scalar(simple, "sfr", KS_NORM=k) for k in (1.8e-4, 2.5e-4, 3.2e-4))
    assert hi < mid < lo  # a higher normalisation locks gas up sooner and leaves less to form stars now
    assert mid == pytest.approx(1.89, abs=0.02) and hi == pytest.approx(1.77, abs=0.03)
    assert hi < Q[2].hi  # at +1 sigma the row passes outright since S13 (it was 0.007 short before)
    assert lo - hi > 2.0 * (mid - Q[2].hi)
    # ...and rows 2 and 20 pull it opposite ways, which is what makes the pair evidence for debt #18.
    gas_lo, gas_hi = (scalar(simple, "gas_mass_30kpc", KS_NORM=k) for k in (1.8e-4, 3.2e-4))
    assert gas_lo > 6.5e9 > 5.5e9 > gas_hi


def test_debt_43_the_two_solar_calibrations_and_their_levers(simple, advanced):
    """NET_YIELD and WIND_SPEED each make the gas at R0 solar on a star formation history that
    misses rows 2 and 20 (debt #18). The levers, so the re-fit is one line when #18 closes."""
    assert abs(feh_at_sun(simple)) < 0.03 and abs(feh_at_sun(advanced)) < 0.02
    wind = feh_at_sun(advanced, WIND_SPEED=1.1 * advanced.constants["WIND_SPEED"].value) - feh_at_sun(advanced)  # +10%
    yld = feh_at_sun(simple, NET_YIELD=1.1 * simple.constants["NET_YIELD"].value) - feh_at_sun(simple)  # +10%
    assert wind == pytest.approx(-0.064, abs=0.01)
    assert yld == pytest.approx(0.041, abs=0.01)


def test_debt_26_the_iron_at_the_centre_reaches_the_planets(prod):
    """[Fe/H] = +1.5 inside half a kiloparsec is not clipped (rule B9), so it reaches occurrence."""
    out = {m.name: run(m) for m in prod[0]}
    for o in out.values():
        assert o.fields["giant_occurrence_sun"] == pytest.approx(0.05, abs=0.002)  # the fit at [Fe/H]=0 holds
    R = out["advanced"].grid.R

    def inner(o):
        return float(np.nanmean(o.fields["giant_occurrence"][R < 1.0]))

    def rich(o):
        return float(np.mean(o.fields["star_metallicity"] > 0.5))

    assert inner(out["simple"]) < 0.1 < 0.3 < inner(out["advanced"])
    assert rich(out["simple"]) < 0.001 and rich(out["advanced"]) > 0.008
    assert out["advanced"].fields["giant_fraction_sample"] > 1.3 * out["simple"].fields["giant_fraction_sample"]
