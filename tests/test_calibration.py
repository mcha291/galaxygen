"""The calibration audit (rule B10), as tests: constants fitted while a mechanism was missing, re-examined.

Each test is a measurement with its number pinned loosely enough to survive a
different machine and tightly enough to notice the physics changing. What each
number *means* is in the register (GALAXY_INPUTS.md §11, debts #12, #18, #26
and #29–#31) and in DECISIONS.md; nothing here fixes anything — the brief said
record, and rule B12 keeps a conflict on the record rather than averaged.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.registry import Constant, Model
from galaxy.run import run
from galaxy.stages.halo import mu

R_SUN = 8.2


def with_constants(model, **values):
    c = dict(model.constants)
    for k, v in values.items():
        c[k] = Constant(v, c[k].unit, "probe")
    return Model(name="probe", about="probe", stages=model.stages, constants=c)


@pytest.fixture(scope="module")
def simple(prod):
    return prod[0].get("simple")


@pytest.fixture(scope="module")
def advanced(prod):
    return prod[0].get("advanced")


def scalar(model, name, inputs=None, **consts):
    m = with_constants(model, **consts) if consts else model
    return float(run(m, inputs, only=(name,)).fields[name])


# --- debt #12: the c_vir normalisation applied to c200 -------------------------


def bryan_norman(omega_m: float) -> float:
    """The virial overdensity in units of rho_crit at z = 0 [recall: Bryan & Norman 1998]."""
    x = omega_m - 1.0
    return 18.0 * math.pi**2 + 82.0 * x - 39.0 * x * x


def concentration_at(delta: float, c_ref: float, delta_ref: float) -> float:
    """Concentration of one NFW halo at overdensity ``delta``, given it at ``delta_ref``.

    ``Delta * c^3 / mu(c)`` is the halo's own invariant (its scale density in units of
    rho_crit), so the conversion is a root, not a fit.
    """
    target = delta_ref * c_ref**3 / mu(c_ref)
    lo, hi = 0.5, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if delta * mid**3 / mu(mid) < target else (lo, mid)
    return 0.5 * (lo + hi)


def test_debt_12_the_overdensity_conversion_is_worth_more_than_row_3s_whole_miss(simple):
    """c200 = 4.1(1+z_f) quotes a c_vir normalisation. Converted at Delta_vir ~ 101 it is 24% lower,
    and v_tan(R0) falls 13 km/s: past the target, from 5 km/s high to 2.4 km/s low."""
    dvir = bryan_norman(0.3)
    assert dvir == pytest.approx(101.1, abs=0.2)
    c_vir = 4.1 * (1.0 + 2.5)
    c200 = concentration_at(200.0, c_vir, dvir)
    assert c200 == pytest.approx(10.9, abs=0.1)
    assert concentration_at(dvir, c200, 200.0) == pytest.approx(c_vir, abs=1e-6)  # the root round-trips
    base = scalar(simple, "v_tangential_sun")
    converted = scalar(simple, "v_tangential_sun", CONCENTRATION_NORM=c200 / 3.5)
    assert base == pytest.approx(256.0, abs=0.5) and converted == pytest.approx(242.6, abs=1.0)
    assert base - converted > 251.0 - 245.0  # the conversion alone is worth more than the target's width
    # At z_f = 3 the converted concentration lands inside: the two halves of the debt are degenerate.
    c3 = concentration_at(200.0, 4.1 * 4.0, dvir)
    inside = scalar(simple, "v_tangential_sun", {"halo_assembly_z": 3.0}, CONCENTRATION_NORM=c3 / 4.0)
    assert 245.0 <= inside <= 251.0


# --- debt #29: row 2 against KS_NORM's own error bar ---------------------------


def test_debt_29_row_2_cannot_see_past_ks_norms_own_uncertainty(simple):
    """KS_NORM is (2.5 +/- 0.7) x 10^-4 and deliberately unfitted. Its 1-sigma swing is 2.5x row 2's miss."""
    lo, mid, hi = (scalar(simple, "sfr", KS_NORM=k) for k in (1.8e-4, 2.5e-4, 3.2e-4))
    assert hi < mid < lo  # a higher normalisation locks gas up sooner and leaves less to form stars now
    assert mid == pytest.approx(1.97, abs=0.02) and hi == pytest.approx(1.85, abs=0.03)
    assert lo - hi > 2.0 * (mid - 1.84)
    # ...and rows 2 and 20 pull it opposite ways, which is what makes the pair evidence for debt #18.
    gas_lo, gas_hi = (scalar(simple, "gas_mass_30kpc", KS_NORM=k) for k in (1.8e-4, 3.2e-4))
    assert gas_lo > 6.5e9 > 5.5e9 > gas_hi


# --- debt #18: the one constant kept for S10 to sweep ---------------------------


def test_debt_18_a_broader_single_infall_trades_rows_3_and_20_against_2_and_22(simple, advanced):
    """GAS_DISC_SCALE_RATIO at 1.2 buys rows 3 and 4 and most of row 20, and pays with rows 2 and 22."""
    F = ("sfr", "v_tangential_sun", "thin_disc_scale_length", "gas_mass_30kpc", "metallicity_gradient")

    def at(ratio):
        o = run(with_constants(simple, GAS_DISC_SCALE_RATIO=ratio), only=F)
        return {k: float(o.fields[k]) for k in F}

    base, broad = at(1.0), at(1.2)
    assert not 245.0 <= base["v_tangential_sun"] <= 251.0 and 245.0 <= broad["v_tangential_sun"] <= 251.0
    assert 2.1 <= broad["thin_disc_scale_length"] <= 3.1
    assert broad["gas_mass_30kpc"] > 1.2 * base["gas_mass_30kpc"]
    assert broad["sfr"] > base["sfr"] > 1.84  # row 2 gets worse
    assert broad["metallicity_gradient"] > base["metallicity_gradient"]  # flatter: row 22 gets worse
    assert scalar(advanced, "metallicity_gradient", GAS_DISC_SCALE_RATIO=1.2) > -0.049  # and reopens
    assert scalar(advanced, "metallicity_gradient", GAS_DISC_SCALE_RATIO=0.8) < -0.069  # or overshoots


# --- debt #30: the two solar calibrations ---------------------------------------


def feh_at_sun(model, **consts):
    o = run(with_constants(model, **consts) if consts else model, only=("feh_gas",))
    return float(o.fields["feh_gas"][int(np.argmin(np.abs(o.grid.R - R_SUN)))])


def test_debt_30_the_two_solar_calibrations_and_their_levers(simple, advanced):
    """NET_YIELD and WIND_SPEED each make the gas at R0 solar on a star formation history that
    misses rows 2 and 20 (debt #18). The levers, so the re-fit is one line when #18 closes."""
    assert abs(feh_at_sun(simple)) < 0.03 and abs(feh_at_sun(advanced)) < 0.02
    wind = feh_at_sun(advanced, WIND_SPEED=1111.0) - feh_at_sun(advanced)  # +10%
    yld = feh_at_sun(simple, NET_YIELD=0.0121) - feh_at_sun(simple)  # +10%
    assert wind == pytest.approx(-0.064, abs=0.01)
    assert yld == pytest.approx(0.041, abs=0.01)


# --- debt #31: the thin disc's thickness under two split criteria ----------------


def test_debt_31_secular_heating_passes_row_6_in_both_models_only_by_the_targets_width(simple, advanced):
    """S3 fitted 25 km/s to a merger-split thin disc. The chemical split finds no thick disc, so the
    advanced thin disc keeps the merger-heated stars: 326 pc against 253, 24 pc inside 350."""
    h = "thin_disc_scale_height"
    s, a = scalar(simple, h), scalar(advanced, h)
    assert 250.0 <= s <= 350.0 and 250.0 <= a <= 350.0 and a - s > 60.0
    assert scalar(advanced, h, MERGER_HEATING=0.0) == pytest.approx(274.0, abs=6.0)  # 52 pc is the merger's
    assert scalar(simple, h, MERGER_HEATING=0.0) == pytest.approx(s, abs=0.5)  # the simple split removed them
    # The same +5 km/s that leaves the simple model inside puts the advanced one 80 pc out.
    assert scalar(simple, h, SECULAR_HEATING=30.0) <= 350.0 < scalar(advanced, h, SECULAR_HEATING=30.0)


# --- debt #26: the centre, in the catalogue and the planets ---------------------


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
