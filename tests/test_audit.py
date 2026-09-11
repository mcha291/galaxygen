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

import math

import numpy as np
import pytest

from galaxy.core.fielddoc import Kind
from galaxy.core.registry import Constant, MergerEvent, Model
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages import sfh
from galaxy.stages.chemistry import age_bin_edges, migration_width, transport
from galaxy.stages.disc import PC_PER_KPC
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
    from galaxy.core.registry import INPUTS

    K, z_f = simple.constants["CONCENTRATION_NORM"].value, INPUTS["halo_assembly_z"].default  # 2.5 until S15
    c_vir = K * (1.0 + z_f)
    c200 = c200_from_cvir(c_vir)
    assert c_vir == pytest.approx(10.91, abs=0.01) and c200 == pytest.approx(8.24, abs=0.05)  # 14.35 and 10.9 until S15
    # The conversion is a property of the profile, checked by inverting it (rule B3).
    assert mu(c200) / c200**3 == pytest.approx((200.0 / 101.0) * mu(c_vir) / c_vir**3, rel=1e-9)
    f = run(simple, only=KIN).fields
    assert f["halo_concentration_virial"] == pytest.approx(c_vir) and f["halo_concentration"] == pytest.approx(c200, abs=0.05)
    # Row 3 read 256.2 unconverted; converted it read 242.7 - through the 245-251 window and out the
    # other side - until S14 contracted the halo around the disc (270.8, high, debt #6); since S15 the
    # epoch's default is the LCDM median and the row reads 260.1, still high (D117).
    # S18: inside at 250.96, on the merger's radial kick and the basis-free solver, not on anything named here (D124).
    # S20: out again at 251.03, by 0.03, when the kick's constant was re-derived from a cited dispersion (D128).
    assert f["v_tangential_sun"] == pytest.approx(251.03, abs=0.5) and Q[3].hi < f["v_tangential_sun"] < Q[3].hi + 0.1  # 250.96 and in until S20; 251.3 and out until S18; 252.9 until S17
    # ...and the cited z_f = 2-3 spans 12 km/s on row 3 (236.4-249.2 until S14); the row wants 1.3-1.4 since S17 (1.1-1.2 at S16, 0.7-1.0 at S14-S15).
    lo, hi = (run(simple, {"halo_assembly_z": z}, only=KIN).fields["v_tangential_sun"] for z in (2.0, 3.0))
    assert lo == pytest.approx(255.8, abs=0.5) and hi == pytest.approx(268.3, abs=0.5)  # 256.0 and 268.4 until S18; 257.6 and 269.9 until S17
    assert 11.0 < hi - lo < 14.0


# --- debts #17 and #41: what the row 20 target is, and what it counts ----------


def test_debt_17_the_zero_width_rows_say_no_testable_target():
    """The source quotes no uncertainty [verified: arXiv:1511.08877, abstract and §4.2]; the table says so."""
    for n in (20, 21):
        assert Q[n].lo == Q[n].hi and Q[n].width == 0.0 and not Q[n].testable
    assert all(q.testable for q in spec.QUANTITIES if q.n not in (20, 21))
    # Row 14 was on this list too until S17. The debt's own remedy is "a citation with an
    # uncertainty, entered before the row is next judged", and for the bulge's dispersion the
    # same source does give one — "the rms is σ_rms,b ≈ 113 km/s, to ≈3 km/s" (BHG16 §4.3) — so
    # the row now has a target of 110-116 that it fails honestly. Rows 20 and 21 still have none.
    assert Q[14].width == 6.0 and Q[14].testable
    d = decl("hydrogen_mass_30kpc", Kind.SCALAR, unit="Msun")
    r = spec.evaluate(Q[20], {"hydrogen_mass_30kpc": 8.0e9 * (1 + 1e-9)}, {"hydrogen_mass_30kpc": d}, "m")
    assert r.status == "fail" and "no testable target" in r.reason and "debt #17" in r.reason
    # Row 20 stays a recorded miss on any reading (rule B5): under debt #17 since S18 put the number at the
    # target (8.09e9 against 8.0, D124); under #47 from S16, when the tail was built, and #18 before that.
    assert 20 in spec.MISSES and spec.MISSES[20].debt == 17 and 20 in spec.MISSES_ADVANCED


def test_debt_41_row_20_compares_total_gas_with_a_hydrogen_mass(model):
    """The target is HI + H₂ — hydrogen; the gas field is every retained baryon not in a star, helium included.

    Since S13 the row reads hydrogen_mass_30kpc = (1 − Y) × gas_mass_30kpc (debt #41).
    """
    f = run(model, only=("gas_mass_30kpc", "hydrogen_mass_30kpc", "stellar_mass_total", "baryon_mass_total")).fields
    Y = model.constants["HELIUM_MASS_FRACTION"].value
    assert Y == 0.27 and Q[20].field == "hydrogen_mass_30kpc"
    assert f["gas_mass_30kpc"] + f["stellar_mass_total"] <= f["baryon_mass_total"] * 1.0001
    assert f["gas_mass_30kpc"] == pytest.approx(1.108e10, rel=0.02)  # 8.26e9 until S18's derived threshold; 8.55e9 until S17; 5.71e9 until S16
    assert f["hydrogen_mass_30kpc"] == pytest.approx(f["gas_mass_30kpc"] * (1.0 - Y))
    # The miss as the table read it until S13 (total gas against a hydrogen target): 0.29 short until S16, then
    # 7% *over*, 3% over at S17 - and 38% over since S18, while the hydrogen is 1% over: the derived threshold
    # put the hydrogen at the target (D124). Like for like is the only reading, and it was the only one that moved.
    assert 1.0 - f["gas_mass_30kpc"] / 8.0e9 == pytest.approx(-0.38, abs=0.01)  # -0.03 until S18; -0.07 until S17
    assert 1.0 - f["hydrogen_mass_30kpc"] / 8.0e9 == pytest.approx(-0.01, abs=0.01)  # 0.25 until S18; 0.22 until S17; 0.48 until S16


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
    # S18 halved it again: the derived threshold rises with kappa inside (47 Msun/pc2 at 2 kpc, 590 at the
    # first cell), so the centre holds a gas reservoir it never had and the same metals sit in far more gas:
    # the simple peak 0.46 -> 0.25, the advanced 1.39 -> 0.70, super-solar out to 1.9 kpc rather than 2.66 (D124).
    assert s["max"] == pytest.approx(0.25, abs=0.05) and s["out_to"] == 0.0
    assert a["max"] == pytest.approx(0.70, abs=0.05) and a["out_to"] == pytest.approx(1.91, abs=0.15)  # 1.39 / 2.66 until S18; 1.36 / 2.5 until S14
    assert a["at_4"] == pytest.approx(0.25, abs=0.03)  # just outside row 22's 4-12 kpc fit range; unmoved
    # The one fitted constant does not reach the centre: it moves the level at R₀, not the peak or the tilt.
    cold, hot = centre(advanced, WIND_SPEED=800.0), centre(advanced, WIND_SPEED=1300.0)
    assert cold["sun"] - hot["sun"] > 0.3
    assert abs(cold["max"] - hot["max"]) < 0.35
    assert abs(cold["gradient"] - hot["gradient"]) < 0.005


# --- debt #27: the register's prediction, run ----------------------------------

CHEM = ("metallicity_gradient", "alpha_sequence")


def test_debt_27s_prediction_ran_a_fast_inner_disc_opens_a_valley_and_closes_row_22_doing_it(advanced):
    # With the default merger list, n = 3 at τ₀ = 1 opened the valley from S13 - when Sagittarius
    # stopped delivering a tenth of the budget beside Gaia-Enceladus (debt #29) - until S17 closed
    # it again (the spheroid takes 13% of the budget out of the disc before it accretes, D121), and
    # **S18 reopened it, wider**: with the derived threshold a fast inner disc (τ₀ = 1) opens a
    # valley at n = 2 *and* n = 3 (dips 0.57 and 0.64, the split at 0.39), and at τ₀ = 7 neither
    # does. The threshold holds the inner disc's gas high and the second infall then restarts the
    # sequence from a diluted start - which is debt #27's own mechanism. Recorded rather than
    # tuned: S20 owns the valley, and the row-6 cost is on the record too, 700 pc at those settings (D124).
    for n, tau, expect in ((2.0, 7.0, "single"), (2.0, 1.0, "bimodal_wide"), (3.0, 7.0, "single"), (3.0, 1.0, "bimodal_wide")):
        f = run(advanced, {"inside_out_index": n, "infall_timescale": tau}, only=CHEM).fields
        assert f["alpha_sequence"] == expect, (n, tau)
        if expect == "single":
            assert f["alpha_dip_depth"] == 0.0
        else:
            assert 0.55 < f["alpha_dip_depth"] < 0.66 and f["alpha_split"] == pytest.approx(0.39, abs=0.02)
    # With Gaia-Enceladus alone, a fast inner disc does open it — and the gradient doubles.
    for inputs in (
        {"inside_out_index": 3.0, "infall_timescale": 7.0, "mergers": one_merger(0.2)},
        {"inside_out_index": 3.0, "infall_timescale": 1.0, "mergers": one_merger(0.5)},
    ):
        f = run(advanced, inputs, only=CHEM).fields
        assert f["alpha_sequence"] == "bimodal_wide", inputs
        # 0.56-0.64 since S18 (0.55-0.62 at S17, 0.55-0.66 at S16); the split 0.41 at τ₀ = 7 and 0.39 at 1.
        assert 0.54 < f["alpha_dip_depth"] < 0.70 and f["alpha_split"] == pytest.approx(0.40, abs=0.02)
        assert f["high_alpha_feh_span"] > 1.0
        assert f["metallicity_gradient"] < -0.10  # row 22's window is [-0.069, -0.049]; -0.111 / -0.108 since S18 (below -0.12 until then)
    # The same small merger with n = 1 stays single: the index is what opens it.
    f = run(advanced, {"inside_out_index": 1.0, "infall_timescale": 7.0, "mergers": one_merger(0.2)}, only=CHEM).fields
    assert f["alpha_sequence"] == "single"


def test_the_thick_disc_a_valley_would_find_is_the_simple_models_compact_one(advanced):
    """What rows 5, 7-11 read the moment the split selects something: recorded so the next session knows the shape."""
    inputs = {"inside_out_index": 3.0, "infall_timescale": 7.0, "mergers": one_merger(0.2)}
    f = run(advanced, inputs, only=("thick_thin_surface_density_ratio",)).fields
    assert f["thick_disc_stellar_mass"] == pytest.approx(5.07e9, rel=0.05) and inside(11, f["thick_disc_stellar_mass"])  # 5.09e9 until S20; 4.92e9 until S18; 5.95e9 until S17; 6.6e9 until S16
    assert f["thick_disc_scale_length"] == pytest.approx(0.60, abs=0.05) and not inside(5, f["thick_disc_scale_length"])  # 0.64 until S20 (the smaller kick); 0.66 until S18
    assert f["thick_disc_scale_height"] == pytest.approx(1069.0, abs=30.0) and inside(7, f["thick_disc_scale_height"])  # 1379 until S20 (the kick re-derived, D128); 1398 until S18; 1202 until S17; 1113 until S16
    assert f["thick_thin_surface_density_ratio"] == pytest.approx(0.0014, abs=0.001)  # row 9: 0.0032 until S20; 0.0096 until S18 - the threshold holds the reservoir here too
    assert f["thin_disc_scale_height"] == pytest.approx(452.0, abs=15.0) and not inside(6, f["thin_disc_scale_height"])  # 512 until S20; 552 until S18; 478 until S17; 443 until S16


# --- debt #28: the flattening, measured in both models -------------------------

GRADS = ("metallicity_gradient_old", "metallicity_gradient_young")


def test_debt_28_migration_flattens_the_old_population_from_a_steeper_start_in_both_models(model):
    still = run(model, {"migration_efficiency": 0.0}, only=GRADS).fields
    moved = run(model, only=GRADS).fields
    # S13 (a physical Sagittarius, debt #29) flattened the unmigrated old gradient from -0.105 / -0.129;
    # S16's tail steepened it again, -0.084 -> -0.089 and -0.106 -> -0.114 (the outer gas is fresh),
    # and S17's spheroid steepened it once more, -> -0.102 and -0.127: a disc that accretes 13%
    # less enriches its middle faster while the tail keeps the outside fresh.
    # S18's derived threshold doubled the unmigrated old gradient, -0.102 -> -0.228 and -0.127 -> -0.254: the
    # oldest stars formed where the early gas first crossed a threshold that is 26 Msun/pc2 at 4 kpc and 11
    # at R0, so the old population's birth radii are compressed inward and its abundance falls faster out.
    old0, young0 = {"simple": (-0.228, -0.017), "advanced": (-0.254, -0.060)}[model.name]
    assert still["metallicity_gradient_old"] == pytest.approx(old0, abs=0.004)
    assert still["metallicity_gradient_young"] == pytest.approx(young0, abs=0.004)
    # The kernel takes the old gradient down by a factor 11-33 now (6-16 until S18; 5-14 until S17); the
    # young/old ratio came down with it, 2.5 in both models (3.0 and 3.5 until S18).
    assert 10.0 < still["metallicity_gradient_old"] / moved["metallicity_gradient_old"] < 35.0
    assert moved["metallicity_gradient_young"] / moved["metallicity_gradient_old"] == pytest.approx(2.52, abs=0.3)  # 3.27 until S18


# --- debt #42: row 6 at the edge in both models, for opposite reasons ----------

HEIGHTS = ("thin_disc_scale_height", "thick_disc_scale_height")


def test_debt_42_row_6_is_at_the_edge_of_its_window_in_both_models(simple, advanced):
    s = run(simple, only=HEIGHTS).fields
    a = run(advanced, only=HEIGHTS).fields
    # 327 against a floor of 250 and a ceiling of 350 (321 at S17): the simple model's row 6 moved off the
    # floor at S17 and is now near the other edge instead (275 at S16, 255 before it). Both
    # moves are the same mechanism from opposite ends - Σ(R₀) falls, h_z = σ²/2πGΣ rises - and
    # the row has been inside for four sessions while sitting nowhere near the middle (debt #42).
    assert Q[6].lo + 60.0 <= s["thin_disc_scale_height"] <= Q[6].hi - 20.0
    # 356 against a ceiling of 350: a recorded miss since S13 (373 until S20 re-derived the kick; 439 until S18's
    # threshold held more gas at R₀; 384 until S17; 358 until S16). The simple row 7 reads 962, inside, since S20 (1279 until then).
    assert Q[6].hi + 3.0 < a["thin_disc_scale_height"] <= Q[6].hi + 10.0
    assert inside(7, s["thick_disc_scale_height"]) and s["thick_disc_scale_height"] == pytest.approx(962.0, abs=10.0)
    # SECULAR_HEATING was set from the 10 Gyr end of the AVR (D54); 20 and 30 km/s fail the two models at opposite
    # ends (228 / 451 in the simple model, 252 / 483 in the advanced), which is why S20 left it at 25 (D128).
    low_s = run(with_constant(simple, "SECULAR_HEATING", 20.0), only=HEIGHTS).fields["thin_disc_scale_height"]
    high_s = run(with_constant(simple, "SECULAR_HEATING", 30.0), only=HEIGHTS).fields["thin_disc_scale_height"]
    high_a = run(with_constant(advanced, "SECULAR_HEATING", 30.0), only=HEIGHTS).fields["thin_disc_scale_height"]
    assert low_s < Q[6].lo and high_s > Q[6].hi and high_a > Q[6].hi
    # MERGER_HEATING calibrates row 7 in the simple model and row 6 in the advanced one, where the heated stars are thin.
    # S18 read 60 km/s landing both (row 7 at 751, the advanced row 6 at 346); S20 did not set it there - it derived the
    # constant from the thick disc's observed dispersion net of the secular heating (88.8, D128), which lands row 7 and
    # leaves the advanced row 6 at 356, the heated old population counted as thin (debt #27). The old default, 120, and
    # the two ends of S10's sweep are kept as measurements. The simple row 6 barely reads the kick (329.5 / 324.6).
    for k, row7, row6 in ((60.0, 751.0, 346.0), (120.0, 1279.0, 373.0), (180.0, 2148.0, 429.0)):  # 775/375 and 2199/544 until S18; 668/326 and 1889/482 until S17
        hot_s = run(with_constant(simple, "MERGER_HEATING", k), only=HEIGHTS).fields
        hot_a = run(with_constant(advanced, "MERGER_HEATING", k), only=HEIGHTS).fields
        assert hot_s["thick_disc_scale_height"] == pytest.approx(row7, rel=0.02)
        assert hot_s["thin_disc_scale_height"] == pytest.approx(327.0, abs=3.0)  # 321.5 until S18; 275.4 until S17; 254.6 until S16 - the radial kick moves it a little now
        assert hot_a["thin_disc_scale_height"] == pytest.approx(row6, rel=0.02)
        assert hot_a["thick_disc_scale_height"] == 0.0
    assert inside(7, run(with_constant(simple, "MERGER_HEATING", 60.0), only=HEIGHTS).fields["thick_disc_scale_height"])
    assert inside(6, run(with_constant(advanced, "MERGER_HEATING", 60.0), only=HEIGHTS).fields["thin_disc_scale_height"])


THICK_SIGMA_W = 35.0  # km/s, the thick disc's vertical dispersion [recall: Bensby, Feltzing & Lundstrom 2003]


def test_debt_42_the_merger_kick_is_the_observed_dispersion_net_of_the_secular_heating(simple):
    """S20 (D128): MERGER_HEATING = sqrt(35^2 - <sigma_sec^2 + sigma_0^2>_thick) / 0.25 = 88.8, reproduced here.

    The constant had been 120, 'scaled so the merger leaves the pre-existing disc at about 30 km/s',
    as if the kick were the whole dispersion; the assembly stage composes it in quadrature with the
    secular heating and the birth dispersion, which read 27.06 km/s over the thick population at R0.
    """
    o = run(simple, only=("thick_disc_dispersion", "stars_formed_history", "last_major_merger_time"))
    R, t = o.grid.R, o.grid.t
    at = int(np.argmin(np.abs(R - R_SUN)))
    thick = t < o.fields["last_major_merger_time"]
    weights = o.fields["stars_formed_history"][at] * thick
    kick_now = simple.constants["MERGER_HEATING"].value * 0.25
    secular2 = o.fields["disc_heating"] ** 2 - np.where(thick, kick_now**2, 0.0)
    secular = math.sqrt(np.average(secular2, weights=weights))
    assert secular == pytest.approx(27.06, abs=0.2)
    derived = math.sqrt(THICK_SIGMA_W**2 - secular**2) / 0.25
    # 88.815: the fixed point, because the thick population's weights at R0 move a little with the kick
    # (88.5 on the 120 km/s run's weights derives 88.82 on its own); the constant is set at the fixed point.
    assert derived == pytest.approx(simple.constants["MERGER_HEATING"].value, abs=0.1)
    assert o.fields["thick_disc_dispersion"] == pytest.approx(THICK_SIGMA_W, abs=0.1)  # 40.4 until S20


# --- debt #45: the constant that does nothing carries row 22 --------------------

STRUCT = (
    "stellar_mass_total", "sfr", "v_tangential_sun", "thin_disc_scale_length", "gas_mass_30kpc",
    "metallicity_gradient", "thick_disc_scale_length", "thick_disc_stellar_mass",
)


def test_debt_45_the_infall_scale_ratio_trades_the_structure_rows_against_the_gas_rows(model):
    by = {r: run(with_constant(model, "GAS_DISC_SCALE_RATIO", r), only=STRUCT).fields for r in (0.8, 1.0, 1.25, 1.5)}
    # Upstream is shared, so rows 1-4 and 20 read the same in both models.
    assert by[0.8]["thin_disc_scale_length"] == pytest.approx(1.94, abs=0.05)  # 2.00 until S18
    assert by[1.5]["thin_disc_scale_length"] == pytest.approx(3.69, abs=0.05) and not inside(4, by[1.5]["thin_disc_scale_length"])  # 3.67 until S18
    assert by[1.5]["gas_mass_30kpc"] == pytest.approx(1.226e10, rel=0.02)  # 9.76e9 until S18's threshold; 1.02e10 until S17's spheroid; 9.17e9 until S16
    assert by[1.5]["v_tangential_sun"] == pytest.approx(235.7, abs=0.5) and by[1.5]["sfr"] == pytest.approx(2.45, abs=0.05)  # 236.1/2.56 until S18; 235.2/2.94 until S17; 241.5/2.67 until S16
    grads = [by[r]["metallicity_gradient"] for r in (0.8, 1.0, 1.25, 1.5)]
    assert grads[0] < grads[1] < grads[2] < grads[3]
    if model.name == "simple":
        # At 1.25 the merger's thick disc reads 1.45 kpc (1.64 until S18; 1.77 at S16, 1.84 and inside before it), not
        # row 5 and not row 11 (7.5e9); at 1.5 it reads 1.69, *under* row 5 now (2.16 and inside until S18) — the derived
        # threshold truncates the pre-merger disc whatever the infall's extent — and rows 3, 4 and 22 are gone.
        assert by[1.25]["thick_disc_scale_length"] == pytest.approx(1.39, abs=0.03) and not inside(5, by[1.25]["thick_disc_scale_length"])  # 1.45 until S20 (the kick re-derived)
        assert inside(11, by[1.25]["thick_disc_stellar_mass"]) and inside(11, by[1.5]["thick_disc_stellar_mass"])  # 7.5e9 and 5.8e9: row 11 lands on this lever now (1.09e10 at 1.25 until S18), row 5 does not
        assert by[1.5]["thick_disc_scale_length"] == pytest.approx(1.65, abs=0.03) and not inside(5, by[1.5]["thick_disc_scale_length"])  # 1.69 until S20 (the kick re-derived)
        assert not inside(4, by[1.5]["thin_disc_scale_length"]) and not inside(3, by[1.5]["v_tangential_sun"])
        assert grads == pytest.approx([-0.103, -0.034, -0.016, -0.011], abs=0.003)  # [-0.065, -0.030, -0.022, -0.019] until S18; [-0.052, -0.026, -0.019, -0.017] until S17
    else:
        # Row 22 passed within a tenth of 1.0 until S17 and over a quarter of the range at S17 (1.0 and 1.25 inside);
        # since S18 **no setting of the ratio reads it**: 1.0 is out by 0.0008 (-0.0698, the recorded miss under
        # debt #47) and 1.25 out by 0.002 the other way (-0.0468). The window sits between them, and the constant
        # that multiplies nothing at 1.0 is not the lever that would land it (D124).
        assert grads == pytest.approx([-0.147, -0.070, -0.047, -0.038], abs=0.003)  # [-0.106, -0.064, -0.051, -0.046] until S18; [-0.092, -0.059, -0.048, -0.044] until S17
        assert not any(inside(22, g) for g in grads)
        assert grads[1] < Q[22].lo < Q[22].hi < grads[2]


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
    # S12 discharged #35, #37 and #40 (D104); S13 discharged #29, #30, #38 and #41 (D106-D109);
    # S14 discharged #6 and opened #46 (D113); S15 discharged #12 (D117); S16 discharged #18 and
    # opened #47 (D119); S17 opened #48 and discharged neither - #17 only for row 14 and #39 only
    # for its second half, which is why the discharged count did not move (D121, D122). S18
    # opened #49 and discharged none (32 / 17); S19 discharged #31 and opened #50, so the open
    # count stands still while the discharged one moves - both halves have to be read (D126).
    # S21 ran twice on two sealed branches and S22 ported both lists (D99): aim (a) opened #51
    # and #52 (D130), aim (b) #65-#73 (D144-D149), and neither discharged anything, so the port
    # alone reads 43 / 18. The gap #53-#64 is aim (a)'s unused reservation and #74-#78 is aim
    # (b)'s (D116) - a missing number inside those blocks is the plan working, not a lost item.
    assert progress.debt_counts(text) == (43, 18)  # 34 / 18 ported from (a) alone, 32 / 18 at S20
    for item in (
        "6. ~~Adiabatic contraction",
        "31. ~~**The catalogue does not migrate.**~~ **DISCHARGED by S19**",
        "50. **The model moves stars twice",
        "46. **The contraction's strength is a simulation calibration",
        "29. ~~**The Sagittarius default",
        "34. **The acceptance table reads nothing inside 4 kpc",
        "38. ~~**A statistical row tests overlap",
        "41. ~~**Acceptance row 20 compares total gas with a hydrogen mass",
        "42. **Row 6 passes at the edge",
        "43. **`NET_YIELD` and `WIND_SPEED` are each fitted",
        "44. **Row 2 cannot see past `KS_NORM`",
        "45. **`GAS_DISC_SCALE_RATIO` multiplies nothing",
        "48. **The M_• residual's width is the classical one",
        "51. **The spec judges every statistical row on one fixed sample",
        "52. **Row 14 is two large errors of opposite sign",
        "65. **Rule D4's instrument cannot see the work the routes do outside the runner",
        "67. **The catalogue is priced against the variable it is not a function of",
        "70. **The bimodality detector's mode test is a test on a peak's density",
        "73. **The number S20 recorded for `disc_radial_spread` is not on the screen as a number",
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
    """KS_NORM is (2.5 +/- 0.7) x 10^-4 and deliberately unfitted. Until S16 its 1-sigma swing was 2.5x row 2's miss.

    Then the tail (S16, D119) took the row to 2.08 with +1 sigma at 1.98, past the window; then
    the spheroid (S17, D121) took 13% of the budget out of the disc and the row landed at 1.82.
    **The row now sits inside its window and the KS_NORM band straddles it**: -1 sigma reads 1.97,
    outside, and +1 sigma 1.73, inside. So the debt's original claim - that the row's verdict is
    KS_NORM's to make - is true again, in the one direction that matters, and this is what a
    passing row 2 is worth. Read alongside the row's own note in spec.py, which says the miss was
    removed without debt #47's mechanism being built.
    """
    lo, mid, hi = (scalar(simple, "sfr", KS_NORM=k) for k in (1.8e-4, 2.5e-4, 3.2e-4))
    # **S18 (D124): the band collapsed.** With Kennicutt's threshold derived, the disc is threshold-regulated
    # everywhere inside 12 kpc - the gas sits just under Sigma_crit and the rate is whatever the infall
    # supplies - so the normalisation of the law no longer reaches the rate at all: 1.764 / 1.755 / 1.755
    # across the +/-1 sigma band, where S17 read 1.97 / 1.82 / 1.73. Row 2 is now a prediction of the infall
    # and the threshold alone, inside its window, and the debt's claim is false in the direction that matters.
    assert hi <= mid <= lo and lo - hi < 0.02  # 0.24 wide until S18
    assert mid == pytest.approx(1.755, abs=0.02) and hi == pytest.approx(1.755, abs=0.02) and lo == pytest.approx(1.764, abs=0.02)  # 1.82 / 1.73 / 1.97 until S17
    assert Q[2].lo < hi and lo < Q[2].hi
    # ...while the gas mass still reads the normalisation: the gas the law leaves is set by how fast it consumes.
    gas_lo, gas_hi = (scalar(simple, "gas_mass_30kpc", KS_NORM=k) for k in (1.8e-4, 3.2e-4))
    assert gas_lo > 1.14e10 > 1.10e10 > gas_hi > 1.04e10  # 8.7e9 > ... > 7.2e9 until S18; 9.0e9 > ... > 7.5e9 until S17


def test_debt_43_the_two_solar_calibrations_and_their_levers(simple, advanced):
    """NET_YIELD and WIND_SPEED each make the gas at R0 solar on a star formation history that
    misses rows 2 and 20 (debt #18). The levers, so the re-fit is one line when #18 closes."""
    assert abs(feh_at_sun(simple)) < 0.03 and abs(feh_at_sun(advanced)) < 0.02
    wind = feh_at_sun(advanced, WIND_SPEED=1.1 * advanced.constants["WIND_SPEED"].value) - feh_at_sun(advanced)  # +10%
    yld = feh_at_sun(simple, NET_YIELD=1.1 * simple.constants["NET_YIELD"].value) - feh_at_sun(simple)  # +10%
    assert wind == pytest.approx(-0.060, abs=0.01)  # -0.064 until S18's refit (982 -> 860 km/s)
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

    # S18 halved the centre's iron (debt #26: 1.39 -> 0.70 dex in the advanced model, 0.46 -> 0.25 in the simple),
    # so the occurrence inside a kiloparsec fell 0.36 -> 0.25 and the metal-rich share of the catalogue 0.01 -> 0.005.
    assert inner(out["simple"]) < 0.05 < 0.2 < inner(out["advanced"]) < 0.3
    # S19 re-pinned the two catalogue numbers, and the direction is the finding. With the
    # catalogue migrating, the stars at any radius are drawn from the whole disc rather than
    # from the ring they sit in, so the local age-metallicity relation stops dominating and
    # the two models' abundance distributions converge: the metal-rich share 0.005 -> 0.0031
    # and the giant-fraction contrast 1.58x -> 1.25x. The centre's iron still reaches the
    # planets -- that is the occurrence assertion above, unmoved -- but the *sample* is a
    # weaker instrument for it than it was, because a metal-rich star born at 1 kpc is now
    # spread over the disc instead of counted where it formed (D126).
    assert rich(out["simple"]) < 0.001 and 0.002 < rich(out["advanced"]) < 0.005  # 0.003-0.008 until S19
    ratio = out["advanced"].fields["giant_fraction_sample"] / out["simple"].fields["giant_fraction_sample"]
    assert ratio > 1.2, ratio  # > 1.3 until S19; 1.247 now, 1.576 before


# --- S20: the valley's mechanisms, probed by substituting the first infall's law (D114, D128) ---

VALLEY = ("alpha_sequence", "alpha_dip_depth", "alpha_split", "thin_disc_scale_height")
THICK = ("thick_disc_scale_length", "thick_disc_stellar_mass", "thick_thin_surface_density_ratio", "sfr")


def dynamical_time_at(z: float, model) -> float:
    """0.1/H(z) in Gyr, the halo's dynamical time at its assembly epoch, from the model's own constants."""
    H0 = model.constants["H0"].value / 0.9778  # km/s/kpc -> 1/Gyr
    om = model.constants["OMEGA_M"].value
    return 0.1 / (H0 * math.sqrt(om * (1.0 + z) ** 3 + 1.0 - om))


FIRST_INFALL = sfh.first_infall  # the built law, captured before any test substitutes it


def constant_law(tau_first: float):
    def law(t, tau, span):
        return FIRST_INFALL(t, np.full_like(tau, tau_first), span)
    return law


def test_debt_49s_prediction_ran_the_first_infall_on_the_halos_dynamical_time_and_failed(simple, advanced, monkeypatch):
    """Debt #49 predicted row 5 lands at any merger share with rows 9 and 11 moving together; it does not (D128).

    The first infall's timescale is the halo's dynamical time at z_f = 1.66 - 0.55 Gyr, derived
    from constants the model has (1 Gyr, the two-infall framework's, reads the same). Row 5 lands
    only where row 11 is far out, and where row 11 lands (share 0.8) rows 5 and 9 are out: the
    pre-committed reading is that the star formation law at high redshift is what is wrong.
    """
    t_dyn = dynamical_time_at(1.66, simple)
    assert t_dyn == pytest.approx(0.55, abs=0.02)
    monkeypatch.setattr(sfh, "first_infall", constant_law(t_dyn))
    at = {g: run(simple, {"mergers": (MergerEvent(3.8, 0.25, g, "probe"), MergerEvent(8.8, 0.02, 0.01, "probe"))}, only=THICK).fields
          for g in (0.3, 0.5, 0.65, 0.8)}
    assert at[0.5]["thick_disc_scale_length"] == pytest.approx(1.95, abs=0.05) and inside(5, at[0.5]["thick_disc_scale_length"])
    assert at[0.5]["thick_disc_stellar_mass"] == pytest.approx(1.67e10, rel=0.05) and at[0.5]["thick_thin_surface_density_ratio"] > 0.4
    assert inside(11, at[0.8]["thick_disc_stellar_mass"]) and not inside(5, at[0.8]["thick_disc_scale_length"]) and at[0.8]["thick_thin_surface_density_ratio"] < 0.05
    assert not any(inside(5, f["thick_disc_scale_length"]) and inside(11, f["thick_disc_stellar_mass"]) for f in at.values())
    assert at[0.5]["sfr"] == pytest.approx(1.27, abs=0.05)  # row 2 out too: the early gas is spent before today
    # In the advanced model it opens no valley - the dip is 0.15 at N_t 1000, 2000 and 4000 - and row 6 goes to 594 (710 on the 120 km/s kick).
    f = run(advanced, only=VALLEY).fields
    assert f["alpha_sequence"] == "single" and f["alpha_dip_depth"] == pytest.approx(0.151, abs=0.02)
    assert f["thin_disc_scale_height"] == pytest.approx(594.0, abs=15.0)


def test_debt_27_every_valley_the_detector_has_found_is_the_plateau_spike(advanced):
    """The alpha-rich 'mode' at tau_0 = 1, n = 2 is the stars formed before any Ia iron: +0.45 exactly, 5% of the mass.

    Recomputed from the published histories the way chemistry_dtd builds the R0 distribution (the
    backward weights, D126): the split sits at 0.39, above the alpha-rich sequence itself, the mass
    above it is a twentieth, and it is all in the top two bins. That is not a thick disc (D128).
    """
    o = run(advanced, {"infall_timescale": 1.0, "inside_out_index": 2.0}, only=VALLEY + ("alpha_fe_history", "sfr_surface_density_history"))
    f = o.fields
    assert f["alpha_sequence"] == "bimodal_wide" and f["alpha_split"] == pytest.approx(0.39, abs=0.02)
    R, t = o.grid.R, o.grid.t
    dt = o.grid.spec.t_max / o.grid.spec.n_t
    formed = PC_PER_KPC * f["sfr_surface_density_history"] * dt * (2.0 * math.pi * R * o.grid["R"].width * PC_PER_KPC**2)[:, None]
    afe = np.nan_to_num(f["alpha_fe_history"], nan=0.0)
    edges, age = age_bin_edges(o.grid.spec.t_max), o.grid.spec.t_max - t
    at_sun = int(np.argmin(np.abs(R - R_SUN)))
    w = np.zeros_like(formed)
    for b in range(edges.size - 1):
        in_bin = (age >= edges[b]) & (age < edges[b + 1])
        if in_bin.any():
            K = transport(R, float(migration_width(0.5 * (edges[b] + edges[b + 1]), o.inputs["migration_efficiency"])))
            w[:, in_bin] = formed[:, in_bin] * K[:, at_sun][:, None]
    hist, _ = np.histogram(afe, bins=np.arange(-0.3, 0.71, 0.02), weights=w)
    share = hist / hist.sum()
    above = share[35:]  # bins from +0.40 up; the split is at 0.39
    assert 0.06 < above.sum() < 0.13  # 0.10
    plateau = share[36:38].sum()  # +0.42 to +0.46: where the first stars of every ring sit, before any Ia iron
    assert plateau > 0.7 * above.sum() and share[38:].sum() == 0.0  # 0.079 of 0.102, and nothing above +0.46
    assert share[27:35].max() < 0.5 * plateau  # +0.24 to +0.40 is a plain, not a mode: no bin holds 3.3% of the mass (+0.20-0.24 is the thin mode's shoulder)


def test_debt_27_the_halos_own_accretion_history_as_the_first_infall_makes_no_thick_disc(simple, advanced, monkeypatch):
    """Wechsler et al. 2002's M(a) = M0 exp(-2 a_c (1/a - 1)) at the model's own a_c = 1/(1 + z_f), as the first infall's rate.

    Fully determined by z_f, and dead by the number: 29% of the halo's mass is in place by z_f, so
    almost nothing has arrived by the merger, the thick disc is 1.5e9 (row 11 out low, row 5 0.98)
    and the star formation rate today doubles (row 2 3.03). In the advanced model no valley (D128).
    """
    H0 = simple.constants["H0"].value / 0.9778
    om = simple.constants["OMEGA_M"].value
    ol = 1.0 - om

    def law(t, tau, span):
        a_grid = np.linspace(1e-4, 1.0, 20000)
        t_of_a = 2.0 / (3.0 * H0 * math.sqrt(ol)) * np.arcsinh(np.sqrt(ol / om) * a_grid**1.5)
        a = np.interp(t, t_of_a, a_grid)
        a_c = 1.0 / (1.0 + 1.66)
        rate = 2.0 * a_c / a**2 * np.exp(-2.0 * a_c * (1.0 / a - 1.0)) * a * H0 * np.sqrt(om / a**3 + ol)
        rate = rate / np.trapezoid(rate, t)
        return np.broadcast_to(rate[None, :], (tau.size, t.size))

    monkeypatch.setattr(sfh, "first_infall", law)
    s = run(simple, only=THICK).fields
    assert s["thick_disc_stellar_mass"] == pytest.approx(1.5e9, rel=0.1) and not inside(11, s["thick_disc_stellar_mass"])
    assert s["thick_disc_scale_length"] == pytest.approx(0.98, abs=0.05) and s["sfr"] == pytest.approx(3.03, abs=0.1)
    a = run(advanced, only=VALLEY).fields
    assert a["alpha_sequence"] == "single" and a["alpha_dip_depth"] == 0.0


# --- S21, run b: the instruments and the viewer (AUDIT_S21B.md) ---------------
#
# Aim (b)'s findings, pinned so the audit's citations point inside the repository
# (rule B14). Nothing here is a target: each is a measurement of an instrument,
# and where an instrument was found to be measuring the wrong thing the finding
# is the number, not the repair (rule B6).


def test_s21b_the_d4_report_is_what_actually_ran():
    """Rule D4, counted at the stages instead of read off the response (rule B3).

    Every other D4 assertion in the suite reads ``Response.stages``, which is the
    service's own account of itself. This one replaces each registered stage's
    ``compute`` with a counting wrapper and compares. It also counts the two pieces
    of physics the routes run *outside* the runner, which no ``stages`` tuple is
    obliged to mention and none does — debt #65.
    """
    from dataclasses import replace

    from galaxy.api.service import Service
    from galaxy.core.grids import GridSpec
    from galaxy.core.registry import production
    from galaxy.stages import planets as planets_mod
    from galaxy.stages import systems as systems_mod

    small = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
    calls: dict[str, int] = {}

    def counted(stage):
        def wrapper(ctx, _inner=stage.compute, _id=stage.id):
            calls[_id] = calls.get(_id, 0) + 1
            return _inner(ctx)

        return replace(stage, compute=wrapper)

    _, impls, _ = production()
    wrapped = {st.id: counted(st) for st in impls}
    outside: dict[str, int] = {}
    real_materialise, real_one_system = systems_mod.materialise, planets_mod.one_system

    def spy(name, fn):
        def wrapper(*a, **kw):
            outside[name] = outside.get(name, 0) + 1
            return fn(*a, **kw)

        return wrapper

    import galaxy.api.service as service_mod

    service_mod._catalogue.materialise = spy("systems.materialise", real_materialise)
    service_mod._planets.one_system = spy("planets.one_system", real_one_system)
    try:
        for route, query in (
            ("/api", ""), ("/api/version", ""), ("/api/stages", ""), ("/api/fields", ""), ("/api/inputs", ""),
            ("/api/arrays", "fields=halo_virial_mass"),
            ("/api/arrays", "fields=stellar_surface_density"),
            ("/api/region", "r_min=7&r_max=9&phi_min=0&phi_max=0.4"),
            ("/api/system", "cell=30&index=0"),
        ):
            calls.clear()
            outside.clear()
            response = Service(grid=small, impls=wrapped).handle(route, query)
            assert response.status == 200, (route, query, response.status)
            assert sorted(calls) == sorted(response.stages), (route, sorted(calls), response.stages)
            assert all(n == 1 for n in calls.values()), (route, calls)
            if route in ("/api", "/api/version", "/api/stages", "/api/fields", "/api/inputs"):
                assert calls == {} and outside == {}, f"{route} ran {calls or outside} (rule D4)"
            if route == "/api/region":
                # Debt #65: the costliest thing this route does is not in the tuple.
                assert outside == {"systems.materialise": 1}
                assert "systems.materialise" not in response.stages
            if route == "/api/system":
                assert outside == {"systems.materialise": 1, "planets.one_system": 1}
    finally:
        service_mod._catalogue.materialise = real_materialise
        service_mod._planets.one_system = real_one_system


def test_s21b_the_catalogue_is_priced_per_cell_not_per_star(simple):
    """Debt #67: the per-star line every record since S11 quotes is fitted to a curve.

    The cells that realise a star saturate, so seconds is a straight line in cells
    and a curve in stars. Pinned as the two R² values and the collapse of the
    marginal per-star cost across the range, both far outside any tolerance the
    machine's noise needs — debt #68 is the same fact seen from the flaky test.
    """
    from galaxy.specs import performance

    cost = performance.catalogue_cost(simple, n_stars=500, samples=(2_000, 8_000, 32_000))
    cells = cost["cells per sample"]
    stars = [s[1] for s in cost["samples"]]
    secs = [s[2] for s in cost["samples"]]

    # The saturation: 64x the stars buys about 2.3x the cells.
    assert stars[-1] / stars[0] > 50.0
    assert 1.8 < cells[-1] / cells[0] < 3.0, cells

    # The curvature, as the marginal cost between consecutive sizes.
    marginal = [(secs[i + 1] - secs[i]) / (stars[i + 1] - stars[i]) for i in range(len(secs) - 1)]
    assert marginal[0] > 3.0 * marginal[-1], marginal

    # And the fit that is conditioned. R² ~0.94-0.99 against ~0.4-0.7 in this repo;
    # the gate is the ordering, which cannot survive the saturation going away.
    assert cost["per_cell_us"] > 0.0 and cost["per_cell_r2"] > cost["per_star_r2"]
    assert 150.0 < cost["per_cell_us"] < 1500.0, cost["per_cell_us"]  # 420-535 us here


def test_s21b_the_detector_cannot_see_a_thick_mode_at_row_9s_share():
    """Debt #70: `MODE_MIN_SHARE` is a test on a peak's density, not on a mode's share.

    A mode of share s and dispersion σ is kept only if s·erf(0.05/(σ√2)) ≥ 0.10, so
    the Milky Way's own thick disc — row 9 asks for 8-16% of the local surface
    density, and the observed α-rich sequence is about 0.04 dex wide — sits inside
    the blind spot. Computed from the exact Gaussian mass per bin, not sampled
    (rule B8). The threshold is stated, never moved (rule B5).
    """
    from galaxy.stages.chemistry_dtd import (
        ALPHA_HIST,
        MODE_MIN_SHARE,
        PEAK_SEPARATION,
        bimodality,
    )

    lo, hi, width = ALPHA_HIST
    edges = np.arange(lo, hi + width / 2, width)
    centres = 0.5 * (edges[1:] + edges[:-1])
    feh = np.linspace(-1.0, 0.3, centres.size)  # wide enough that a found valley reads wide

    def mass(mu: float, sigma: float) -> np.ndarray:
        cdf = 0.5 * (1.0 + np.vectorize(math.erf)((edges - mu) / (sigma * math.sqrt(2.0))))
        m = np.diff(cdf)
        return m / m.sum()

    def two_modes(share: float, sigma_thick: float) -> np.ndarray:
        return (1.0 - share) * mass(0.05, 0.03) + share * mass(0.30, sigma_thick)

    # The α-rich maximum is found, and then rejected by the window: 0.0929 of the
    # mass inside ±0.05 dex against a threshold of 0.1000.
    hist = two_modes(0.12, 0.04)
    half = max(1, int(round(0.5 * PEAK_SEPARATION / width)))
    maxima = [i for i in range(hist.size) if hist[i] > 0.0
              and (i == 0 or hist[i] >= hist[i - 1]) and (i == hist.size - 1 or hist[i] > hist[i + 1])]
    assert [round(float(centres[i]), 2) for i in maxima] == [0.05, 0.29], maxima
    share_in_window = float(hist[maxima[1] - half : maxima[1] + half + 1].sum() / hist.sum())
    assert share_in_window == pytest.approx(0.0929, abs=0.0005) and share_in_window < MODE_MIN_SHARE

    assert bimodality(centres, feh, two_modes(0.12, 0.04))[0] == "single"
    assert bimodality(centres, feh, two_modes(0.12, 0.03))[0].startswith("bimodal")
    # Ten per cent or less is invisible at any width a galaxy could have.
    assert all(bimodality(centres, feh, two_modes(0.10, s))[0] == "single" for s in (0.02, 0.03, 0.04))
    # The closed form, against the detector itself.
    for share, sigma in ((0.12, 0.04), (0.12, 0.03), (0.15, 0.04), (0.20, 0.06), (0.20, 0.08)):
        predicted = share * math.erf(0.05 / (sigma * math.sqrt(2.0))) >= MODE_MIN_SHARE
        assert (bimodality(centres, feh, two_modes(share, sigma))[0] != "single") == predicted, (share, sigma)


def test_s21b_four_published_scalars_reach_no_surface_of_the_viewer(model):
    """Debt #69: §5d's "the viewer shows every published field" is short by four.

    `view.js` picks from declarations alone, so this is answerable without a
    browser: a grid field is a picture, an object field a column of the region
    response, and a galaxy scalar a number — unless its stage publishes object
    columns, which is rule D4 keeping the client from materialising a galaxy to
    print one number. Those are the four.
    """
    from galaxy.api.service import Service

    fields = Service().handle("/api/fields", f"model={model.name}").json()["fields"]
    catalogue_stages = {f["stage"] for f in fields if f["domain"] == "object"}
    lost = [f["name"] for f in fields
            if f["domain"] == "galaxy" and f["stage"] in catalogue_stages]
    assert sorted(lost) == [
        "catalogue_size", "giant_fraction_sample", "mean_planets_per_star", "planet_count_sample",
    ], lost
    # The one that costs nothing: the region response's own census carries the count.
    assert "catalogue_size" in lost
    # Everything else does reach a surface, and every picture has its ramp (rule A9).
    reachable = [f for f in fields if f["name"] not in lost]
    assert len(reachable) == len(fields) - 4
    assert all(f["ramp"] is not None for f in reachable if f["domain"] in ("grid", "object"))


def test_s21b_s20s_two_numbers_reach_the_viewer(simple):
    """S20's two moved numbers, read back through the API the viewer reads (BRIEF.md)."""
    from galaxy.api.service import Service

    svc = Service()
    fields = svc.handle("/api/fields", "model=simple").json()["fields"]
    by_name = {f["name"]: f for f in fields}

    # The thick disc's dispersion: a galaxy scalar of a stage that publishes no
    # object columns, so the viewer prints it.
    catalogue_stages = {f["stage"] for f in fields if f["domain"] == "object"}
    decl = by_name["thick_disc_dispersion"]
    assert decl["domain"] == "galaxy" and decl["stage"] not in catalogue_stages
    header, _ = svc.handle("/api/arrays", "model=simple&fields=thick_disc_dispersion").frame()
    assert header["scalars"]["thick_disc_dispersion"] == pytest.approx(35.0, abs=0.1)  # 40.4 until S20

    # The radial spread: a grid field on (R, t) with a ramp, so the viewer draws it
    # as an image — the number S20 recorded is the maximum over t and is not on the
    # screen as a number (debt #73).
    decl = by_name["disc_radial_spread"]
    assert decl["domain"] == "grid" and decl["axes"] == ["R", "t"] and decl["ramp"] is not None
    header, arrays = svc.handle("/api/arrays", "model=simple&fields=disc_radial_spread").frame()
    spread = np.asarray(arrays["disc_radial_spread"])
    axis = header["grid"]["axes"]["R"]
    R = np.linspace(axis["lo"], axis["hi"], axis["n"])
    at_sun = spread[int(np.argmin(abs(R - R_SUN)))].max()
    at_two = spread[int(np.argmin(abs(R - 2.0)))].max()
    assert at_sun == pytest.approx(1.09, abs=0.02)  # 1.47 until S20
    assert at_two == pytest.approx(0.22, abs=0.02)  # 0.30 until S20
