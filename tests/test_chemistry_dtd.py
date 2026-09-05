"""The advanced chemistry: what the delay, the wind and the conservative migration each do.

Three predictions from earlier sessions are run here rather than honoured
(rule B4): debt #15's that outflows steepen the gradient (they do — row 22
closes), debt #9's that α-bimodality might appear without a merger (it does not
appear with one either), and S2's that if row 22 steepens and row 23 does not
then migration is too strong (it is — debt #28).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import Constant, MergerEvent, Model
from galaxy.run import run
from galaxy.stages import chemistry_dtd as C
from galaxy.stages.chemistry import gradient
from galaxy.stages.vertical_alpha import VERTICAL_ALPHA, alpha_mask

R_SUN = 8.2
CHEM = ("metallicity_gradient", "alpha_sequence")  # the closure above these is halo..chemistry_dtd


@pytest.fixture(scope="module")
def advanced(prod):
    return prod[0].get("advanced")


@pytest.fixture(scope="module")
def default(advanced):
    return run(advanced, only=CHEM)


def out(model, **inputs):
    return run(model, inputs or None, only=CHEM)


def with_constant(model, name, value):
    c = dict(model.constants)
    c[name] = Constant(value, c[name].unit, "probe")
    return Model(name="probe", about="probe", stages=model.stages, constants=c)


# --- the delay-time distribution --------------------------------------------


def test_the_delay_kernel_resolution_is_fixed_whatever_the_grid():
    """GALAXY_INPUTS.md §10: bin the DTD at a fixed K, or the cost is quadratic in N_t."""
    for n_t in (250, 2000, 16000):
        delays, weights = C.dtd_bins(0.15, 13.8, 1.1)
        assert delays.size == weights.size == C.DTD_BINS
        assert weights.sum() == pytest.approx(1.0)
        assert 0.15 < delays[0] < delays[-1] < 13.8
        # A burst at t = 0 explodes its whole Ia budget within the run, whatever dt is.
        psi = np.zeros((3, n_t))
        psi[:, 0] = 1.0
        ia = C.snia_rate(psi, 13.8 / n_t, delays, weights)
        assert ia[:, 0].max() == 0.0 and ia.sum(axis=1) == pytest.approx(np.ones(3))


def test_the_plateau_is_the_core_collapse_yield_ratio(advanced, default):
    c = advanced.constants
    plateau = math.log10((c["Y_O_CC"].value / c["Y_FE_CC"].value) / (c["SOLAR_OXYGEN"].value / c["SOLAR_IRON"].value))
    assert plateau == pytest.approx(0.45, abs=0.01)
    afe = default.fields["alpha_fe_history"]
    assert np.nanmax(afe) == pytest.approx(plateau, abs=0.005)
    # ...and the present-day gas at R₀ has come down to near solar, once the Ia iron is in.
    at_sun = int(np.argmin(np.abs(default.grid.R - R_SUN)))
    assert -0.05 < default.fields["alpha_fe_gas"][at_sun] < 0.15


def test_iron_lags_oxygen_so_the_iron_gradient_is_the_steeper(default):
    """The outer disc is younger and has received less of its delayed iron."""
    R = default.grid.R
    feh, oh = default.fields["feh_gas"], default.fields["feh_gas"] + default.fields["alpha_fe_gas"]
    assert gradient(feh, R) < gradient(oh, R) - 0.01
    assert gradient(oh, R) == pytest.approx(-0.037, abs=0.005)


# --- the wind ---------------------------------------------------------------


def test_the_escape_velocity_at_the_sun_is_where_it_is_measured(default):
    """Derived from the model's own potential; the measured local value is 530-580 km/s [recall]."""
    v = float(np.interp(R_SUN, default.grid.R, default.fields["escape_velocity"]))
    assert 528.0 <= v <= 590.0
    assert np.all(np.diff(default.fields["escape_velocity"][default.grid.R > 1.0]) < 0.0)


def test_the_wind_takes_the_share_the_effective_yield_was_hiding(default):
    """NET_YIELD is a third of the nucleosynthetic yield; here the third is a result (debt #16)."""
    f = float(np.interp(R_SUN, default.grid.R, default.fields["metal_escape_fraction"]))
    assert 0.65 <= f <= 0.85
    # ...and it rises outward, which is the whole mechanism of the tilt.
    f_in, f_out = (float(np.interp(r, default.grid.R, default.fields["metal_escape_fraction"])) for r in (4.0, 12.0))
    assert f_in < f < f_out


def test_debt_15s_prediction_holds_and_row_22_closes(default):
    """Outflows were predicted to steepen the present-day gradient towards -0.06. They do."""
    assert -0.069 <= default.fields["metallicity_gradient"] <= -0.049


def test_the_tilt_is_the_wind_s_radial_dependence(advanced, default):
    """Turn the dependence off (WIND_INDEX = 0: the same loss everywhere) and the tilt goes."""
    flat = run(with_constant(advanced, "WIND_INDEX", 0.0), only=CHEM)
    assert flat.fields["metallicity_gradient"] > default.fields["metallicity_gradient"] + 0.01
    # With no radial dependence what is left is the infall tilt plus the delayed iron's.
    assert flat.fields["metallicity_gradient"] == pytest.approx(-0.043, abs=0.006)


def test_the_solar_calibration_is_one_constant(advanced, default):
    at_sun = int(np.argmin(np.abs(default.grid.R - R_SUN)))
    assert abs(default.fields["feh_gas"][at_sun]) < 0.02
    hotter = run(with_constant(advanced, "WIND_SPEED", 1100.0), only=CHEM)
    assert hotter.fields["feh_gas"][at_sun] < default.fields["feh_gas"][at_sun] - 0.03


# --- migration --------------------------------------------------------------


def test_transport_conserves_what_it_moves():
    R = np.linspace(0.05, 30.0, 400)
    K = C.transport(R, 3.0)
    assert K.sum(axis=1) == pytest.approx(np.ones(R.size))
    m = np.exp(-R / 2.5)
    assert (K.T @ m).sum() == pytest.approx(m.sum())
    assert np.array_equal(C.transport(R, 0.0), np.eye(R.size))


def test_the_solar_neighbourhood_has_a_spread_and_migration_makes_it(advanced, default):
    """GALAXY_INPUTS.md §8: without migration the local distribution is far too narrow."""
    still = out(advanced, migration_efficiency=0.0)
    assert default.fields["feh_spread_sun"] > still.fields["feh_spread_sun"]
    assert 0.2 < default.fields["feh_spread_sun"] < 0.4  # observed ~0.2 dex [recall]


def test_s2s_prediction_fired_migration_is_too_strong_once_the_tilt_is_right(advanced, default):
    """Row 22 steepened and row 23 did not, so migration_efficiency is wrong too (debt #28)."""
    young, old = default.fields["metallicity_gradient_young"], default.fields["metallicity_gradient_old"]
    assert young / old == pytest.approx(3.1, abs=0.3)  # observed 1.75
    narrower = out(advanced, migration_efficiency=2.5)
    assert -0.05 <= narrower.fields["metallicity_gradient_old"] <= -0.03  # row 23 would pass
    assert narrower.fields["metallicity_gradient_young"] / narrower.fields["metallicity_gradient_old"] == pytest.approx(1.6, abs=0.2)


# --- row 24 and the split -----------------------------------------------------


def test_there_is_no_valley_and_the_answer_is_nan_not_zero(default):
    assert default.fields["alpha_sequence"] == "single"
    assert default.fields["alpha_dip_depth"] == 0.0
    assert math.isnan(default.fields["alpha_split"])  # rule B9: no valley is not a valley at zero


def test_the_experiments_that_looked_for_a_valley(advanced):
    """Debt #27's evidence: the accretion inputs do not reach two modes, with or without a merger."""
    free = out(advanced, mergers=())
    assert free.fields["alpha_sequence"] == "single"  # debt #9, from a criterion that never named the merger
    fast = out(advanced, infall_timescale=1.0, mergers=(MergerEvent(3.8, 0.25, 0.2, "probe"),))
    assert fast.fields["alpha_sequence"] == "single"
    assert 0.25 < fast.fields["alpha_dip_depth"] < C.DIP_DEPTH  # the closest any input vector comes


def test_bimodality_is_read_off_a_histogram_that_can_say_two():
    """The detector itself, on a distribution that is bimodal and one that is not."""
    rng = np.random.default_rng(0)
    a = np.concatenate([rng.normal(0.02, 0.03, 8000), rng.normal(0.28, 0.04, 2000)])
    feh = np.concatenate([rng.normal(0.0, 0.15, 8000), rng.normal(-0.4, 0.25, 2000)])
    w = np.ones(a.size)
    category, split, depth, span = C.bimodality(a, feh, w)
    assert category == "bimodal_wide" and 0.1 < split < 0.2 and depth > 0.8 and span > 0.5
    category, split, depth, _ = C.bimodality(rng.normal(0.2, 0.05, 10000), feh, w)
    assert category == "single" and math.isnan(split) and depth < C.DIP_DEPTH


def test_the_split_criterion_never_names_the_merger():
    assert "last_major_merger_time" not in VERTICAL_ALPHA.requires
    afe = np.array([[0.4, 0.2, np.nan, 0.05]])
    assert not alpha_mask(afe, float("nan")).any()
    assert alpha_mask(afe, 0.15).tolist() == [[True, True, True, False]]  # the first, metal-free stars are thick


def test_the_populations_still_add_up_with_a_chemical_split(advanced):
    o = run(advanced, only=("thick_thin_surface_density_ratio",))
    total = o.fields["thin_disc_stellar_mass"] + o.fields["thick_disc_stellar_mass"]
    assert total == pytest.approx(o.fields["stellar_mass_total"], rel=0.02)


def test_the_advanced_gradient_converges(advanced):
    grads = [
        run(advanced, grid=GridSpec(n_R=nr, n_t=nt, n_z=6), only=CHEM).fields["metallicity_gradient"]
        for nr, nt in ((200, 1000), (400, 2000), (400, 4000))
    ]
    assert (max(grads) - min(grads)) / abs(np.mean(grads)) < 0.02, grads


# --- S10, the calibration audit (rule B10) ------------------------------------


def test_the_winds_effective_yield_and_the_fitted_one_agree_to_ten_percent(prod):
    """Debt #16 was discharged on this claim at S9; S10 puts a number on it.

    The simple model fits ``NET_YIELD`` so that the solar neighbourhood comes out
    at [Fe/H] = 0 with no outflows. The advanced model instead takes
    nucleosynthetic yields and loses metals to a wind, and the effective yield at
    R₀ is then whatever falls out. The two are arrived at by routes that share no
    constant, so agreeing at all is the content of the discharge — and how well
    they agree is a number nobody had.
    """
    models, _, _ = prod
    advanced, simple = models.get("advanced"), models.get("simple")
    c = advanced.constants
    y_z = (float(c["Y_O_CC"].value) * float(c["SOLAR_METALLICITY"].value) / float(c["SOLAR_OXYGEN"].value)
           + 2.0 * float(c["Y_FE_IA"].value))
    assert y_z == pytest.approx(0.0406, abs=0.0005)  # against the 0.03-0.04 usually quoted

    o = run(advanced, only=("metal_escape_fraction",))
    i = int(np.argmin(abs(o.grid.R - float(c["R_SUN"].value))))
    escaped = float(o.fields["metal_escape_fraction"][i])
    assert escaped == pytest.approx(0.7532, abs=0.001)

    effective = y_z * (1.0 - escaped)
    fitted = float(simple.constants["NET_YIELD"].value)
    assert effective == pytest.approx(0.01001, abs=0.0002)
    assert fitted / effective == pytest.approx(1.10, abs=0.03)


def test_the_centres_iron_is_the_wind_and_not_the_grid(prod):
    """Debt #26's trap, checked: a convergence sweep sees the inner rings move.

    It moves them by ±0.04 dex and never by the dex that separates +1.5 from the
    +0.5 real bulges reach, and the simple model's centre sits at +0.62 on every
    grid. The excess is the massless wind, not the discretisation.
    """
    models, _, _ = prod
    peaks = {}
    for name in ("simple", "advanced"):
        got = [
            float(np.nanmax(run(models.get(name), grid=GridSpec(n_t=n), only=("feh_gas",)).fields["feh_gas"]))
            for n in (500, 1000, 2000, 4000, 8000)
        ]
        peaks[name] = got
        assert max(got) - min(got) < 0.10, (name, got)
    assert min(peaks["advanced"]) > 1.4 and max(peaks["simple"]) < 0.7


def test_no_acceptance_row_reads_the_disc_inside_four_kiloparsecs(prod):
    """So debt #26's +1.5 dex centre is invisible to the whole table (S10)."""
    from galaxy.stages.chemistry import GRADIENT_FIT_RANGE

    assert GRADIENT_FIT_RANGE[0] == 4.0
    models, _, _ = prod
    advanced = models.get("advanced")
    o = run(advanced, only=("feh_gas", "metallicity_gradient"))
    R, feh = o.grid.R, o.fields["feh_gas"]
    assert float(np.nanmax(feh)) == pytest.approx(float(feh[0]), abs=1e-9)  # the peak is the innermost ring

    # Clipping the inner disc to a sane value moves no acceptance scalar, which is
    # the sense in which the table cannot see it.
    fit = (R >= GRADIENT_FIT_RANGE[0]) & (R <= GRADIENT_FIT_RANGE[1])
    assert not fit[R < 4.0].any()
    assert float(np.nanmax(feh[fit])) < 0.5


def test_the_midplane_escape_velocity_is_half_a_cell_above_the_midplane(prod):
    """S10: the field says midplane and the value is at z = z_max / (2·n_z).

    ``halo_potential`` is the only field on the z axis and this is its only
    consumer, which reads column 0 — the first cell *centre*, not the plane. So a
    grid knob moves a published field, and the amount it moves it by is not
    documented anywhere. It is small because the NFW potential is nearly flat
    near r = 0, which is the reason to record the number rather than assume it.
    """
    models, _, _ = prod
    advanced = models.get("advanced")
    at = {}
    for n_z in (15, 60, 960):
        o = run(advanced, grid=GridSpec(n_z=n_z), only=("escape_velocity",))
        assert o.grid.z[0] == pytest.approx(5.0 / (2 * n_z))
        at[n_z] = float(o.fields["escape_velocity"][0])
    assert at[960] - at[15] == pytest.approx(1.03, abs=0.15)  # km/s, the innermost annulus
    assert abs(at[960] / at[15] - 1.0) < 0.002


def test_a_coarse_time_grid_manufactures_the_valley_debt_27_is_looking_for(prod):
    """A warning for whoever chases debt #27: check the grid before believing a verdict."""
    models, _, _ = prod
    advanced = models.get("advanced")
    assert run(advanced, only=("alpha_sequence",)).fields["alpha_sequence"] == "single"
    coarse = run(advanced, grid=GridSpec(n_t=8), only=("alpha_sequence",))
    assert coarse.fields["alpha_sequence"] != "single"
