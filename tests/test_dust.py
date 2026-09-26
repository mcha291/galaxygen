"""Dust that radiates (BUILD_II Phase 7, S31): the grain model's constants, the slab, the heating
balance and the gate RENDER_PHYSICS §7 names — the starlight the dust absorbs equals the infrared it
emits, per radius and in total, read from two published fields and two published scalars.

The balance is closed by construction (the temperature is solved from the absorbed power), so what
it tests is that the published infrared — the emission spectrum a renderer draws, integrated by
quadrature — carries the same power as the closed form the temperature was solved with: a change to
either side alone breaks it. What it cannot catch, a unit error common to both, the temperature's
range and the grain model's own V opacity against the ISM's coefficient catch instead (the class of
defect D163's factor of 162 was).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.stages import dust
from galaxy.stages.disc import PC_PER_KPC

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
FIELDS = (
    "dust_scattering_optical_depth", "dust_colour_excess_b_v", "dust_scattering_asymmetry",
    "dust_absorbed_surface_brightness", "dust_temperature", "dust_infrared_surface_brightness",
    "dust_absorbed_luminosity", "dust_infrared_luminosity", "radiation_field_g0", "pah_fraction",
    "disc_surface_brightness", "disc_luminosity", "dust_surface_density", "dust_extinction_v",
    "sfr_surface_density", "feh_gas",
)
# The gate's tolerances, measured at S31: the per-radius balance closes to 1.41e-12 on this grid and
# 1.46e-12 on the default one (worst at the grid's outer edge, where the dust is at 1.5 K and the
# quadrature's long-wavelength end is felt), 1e-15 inside the disc; the totals to 2.2e-15 and 2.0e-15.
BALANCE_PER_RADIUS = 1e-11
BALANCE_TOTAL = 1e-13


@pytest.fixture(scope="module")
def coarse(prod):
    models, _, _ = prod
    return {m.name: run(m, grid=COARSE, only=FIELDS) for m in models}


def _c(model, name):
    return model.constants[name].value


# --- the sources (ruling (a), read at S31, rule B9) --------------------------------------------


def test_the_grain_model_constants_are_the_rows_the_table_prints(prod):
    """Draine's kext_albedo_WD_MW_3.1_60_D03.all: the V filter row (0.547 um) 0.6774 / 0.5383 /
    4.868E-22; the 0.151356 um row 0.4068 / 1.193E-21; the MIPS 3 row (155.9 um) K_abs 1.643E+01.
    Planck 2013 XI Table 3's whole-sky beta 1.62; Kennicutt & Evans 2012's log C_FUV 43.35; the Habing
    field's 1.6e-3; Remy-Ruyer et al. 2015's eq. 5 and its normalisation. Both models share them."""
    for m in prod[0]:
        assert _c(m, "DUST_R_V") == 3.1
        assert (_c(m, "DUST_ALBEDO_V"), _c(m, "DUST_SCATTERING_G")) == (0.6774, 0.5383)
        assert _c(m, "DUST_EXTINCTION_RATIO_FUV") == 1.193e-21 / 4.868e-22
        assert _c(m, "DUST_ALBEDO_FUV") == 0.4068
        assert (_c(m, "DUST_OPACITY_REFERENCE"), _c(m, "DUST_OPACITY_WAVELENGTH")) == (16.43, 155.9)
        assert _c(m, "DUST_EMISSIVITY_INDEX") == 1.62
        assert _c(m, "FUV_LUMINOSITY_PER_SFR") == 10.0**43.35 / 3.828e33
        assert _c(m, "HABING_FLUX") == 1.6e-3
        assert (_c(m, "PAH_FRACTION_GALACTIC"), _c(m, "PAH_METALLICITY_INTERCEPT"), _c(m, "PAH_METALLICITY_SLOPE")) == (
            0.0457, -11.0, 1.30)
        assert (_c(m, "OXYGEN_ABUNDANCE_SOLAR"), _c(m, "PAH_METALLICITY_MAX")) == (8.69, 1.20)
        for name in ("DUST_ALBEDO_V", "DUST_SCATTERING_G", "DUST_OPACITY_REFERENCE"):
            assert "kext_albedo_WD_MW_3.1_60_D03.all" in m.constants[name].about
        assert "Table 3" in m.constants["DUST_EMISSIVITY_INDEX"].about
        assert "eq. 5" in m.constants["PAH_METALLICITY_SLOPE"].about


def test_the_grain_models_v_opacity_is_the_ism_coefficient_within_three_per_cent(prod):
    """The ISM's A_V per unit dust mass (from Bohlin et al.'s N_H/A_V, D163) against the grain model's
    own: C_ext(V)/H over the dust mass per H, 4.868E-22 / 1.398E-26 cm^2/g (the table's V filter row
    and header), as magnitudes per Msun/pc^2. Two routes to one number that D163's factor of 162 and
    its 1.38 would each have failed. Measured at S31: 7.8956 against 7.71, 2.4% apart."""
    grains = 4.868e-22 / 1.398e-26 * dust.GRAMS_PER_MSUN / dust.CM_PER_PC**2 * dust.MAGNITUDES_PER_OPTICAL_DEPTH
    for m in prod[0]:
        ism = _c(m, "DUST_EXTINCTION_COEFFICIENT")
        assert grains == pytest.approx(7.8956, abs=5e-4)
        assert grains / ism - 1.0 == pytest.approx(0.02407, abs=5e-5)
        assert abs(grains / ism - 1.0) < 0.03


# --- the slab and the modified blackbody, against their defining integrals (rule B3) -----------


def _mu_quadrature(f, n=400_001):
    """int_0^1 f(mu) dmu as int f mu dln(mu) on a log grid from 1e-14: both integrands here are bounded
    at mu -> 0, so the piece below is under 1e-14."""
    mu = np.geomspace(1e-14, 1.0, n)
    return float(np.trapezoid(f(mu) * mu, np.log(mu)))


@pytest.mark.parametrize("tau", [1e-6, 1e-4, 9.99e-4, 1.001e-3, 0.05, 0.3, 1.0, 3.0, 30.0])
def test_the_slab_keeps_the_light_its_defining_integral_says(tau):
    """1 - P_esc against its defining integral, (1/tau) int_0^1 mu (y - 1 + e^-y) dmu with y = tau/mu (the
    same integral as 1 - (1/tau) int mu (1 - e^-y) dmu, written without the cancellation), both sides of
    the series' switch."""

    def kept(mu):
        y = tau / mu
        return mu * np.where(y < 1e-3, y * y / 2.0 - y**3 / 6.0 + y**4 / 24.0, np.expm1(-y) + y)

    direct = _mu_quadrature(kept) / tau
    assert float(dust.slab_absorbed_fraction(np.array([tau]))[0]) == pytest.approx(direct, rel=2e-6, abs=1e-12)


def test_the_slab_limits():
    thick = dust.slab_absorbed_fraction(np.array([200.0]))[0]
    assert thick == pytest.approx(1.0 - 1.0 / 400.0, rel=1e-12)  # escapes 1/(2 tau), both faces
    assert dust.slab_absorbed_fraction(np.array([0.0]))[0] == 0.0
    grid = np.geomspace(1e-9, 1e3, 2001)
    kept = dust.slab_absorbed_fraction(grid)
    assert np.all(np.diff(kept) > 0.0) and np.all((kept > 0.0) & (kept < 1.0))


@pytest.mark.parametrize("tau", [1e-3, 0.2, 1.4, 12.0])
def test_the_midplane_flux_is_its_defining_integral(tau):
    """4 pi J at the midplane: (emitted / tau) int_0^1 (1 - exp(-tau / 2mu)) dmu."""
    direct = _mu_quadrature(lambda mu: -np.expm1(-0.5 * tau / mu)) / tau
    assert float(dust.slab_midplane_flux(np.array([1.0]), np.array([tau]))[0]) == pytest.approx(direct, rel=2e-6)
    assert dust.slab_midplane_flux(np.array([1.0]), np.array([0.0]))[0] == 0.0


@pytest.mark.parametrize("beta", [1.62, 2.0])
def test_the_temperature_inverts_the_spectrums_own_power(beta):
    """The closed form (Gamma, zeta) against the spectrum integrated by quadrature, and the inversion."""
    k0, lam0 = 16.43, 155.9
    T = np.array([3.0, 10.0, 19.5, 40.0, 60.0])
    quad = dust.emitted_per_mass(T, k0, lam0, beta)
    closed = dust.emitted_power_coefficient(k0, lam0, beta) * T ** (4.0 + beta)
    assert np.allclose(quad / closed, 1.0, rtol=1e-12, atol=0.0)
    assert np.allclose(dust.dust_temperature(closed, k0, lam0, beta), T, rtol=1e-13, atol=0.0)
    assert dust.dust_temperature(np.array([0.0]), k0, lam0, beta)[0] == 0.0


def test_zeta_against_its_series():
    for s in (4.5, 5.62, 6.0):
        direct = sum(k ** (-s) for k in range(1, 200_000)) + 200_000 ** (1 - s) / (s - 1)
        assert dust._zeta(s) == pytest.approx(direct, rel=1e-13)
    assert dust._zeta(6.0) == pytest.approx(math.pi**6 / 945.0, rel=1e-14)


# --- THE GATE (RENDER_PHYSICS §7): absorbed = emitted, per radius and in total -----------------


def test_the_energy_balance_closes_per_radius_and_in_total(model, coarse):
    f = coarse[model.name].fields
    R = coarse[model.name].grid.R
    absorbed = np.asarray(f["dust_absorbed_surface_brightness"])
    emitted = np.asarray(f["dust_infrared_surface_brightness"])
    heated = absorbed > 0.0
    assert heated.sum() == R.size  # the grid's every ring has light and dust on the default Milky Way
    worst = float(np.max(np.abs(emitted[heated] / absorbed[heated] - 1.0)))
    assert worst < BALANCE_PER_RADIUS, worst
    assert np.all(emitted[~heated] == 0.0)
    total = float(f["dust_infrared_luminosity"]) / float(f["dust_absorbed_luminosity"]) - 1.0
    assert abs(total) < BALANCE_TOTAL, total
    # Each total is its surface brightness over the disc, taken independently here.
    area = 2.0 * math.pi * R * PC_PER_KPC**2
    assert float(f["dust_absorbed_luminosity"]) == pytest.approx(float(np.trapezoid(absorbed * area, R)), rel=1e-14)
    assert float(f["dust_infrared_luminosity"]) == pytest.approx(float(np.trapezoid(emitted * area, R)), rel=1e-14)


def test_the_absorbed_light_is_the_slabs_share_of_the_starlight(model, coarse):
    f = coarse[model.name].fields
    light = np.asarray(f["disc_surface_brightness"])
    tau_abs = (1.0 - _c(model, "DUST_ALBEDO_V")) * np.asarray(f["dust_extinction_v"]) / (2.5 * math.log10(math.e))
    assert np.allclose(np.asarray(f["dust_absorbed_surface_brightness"]), light * dust.slab_absorbed_fraction(tau_abs), rtol=1e-12, atol=0.0)  # tau rounded differently: 1.8e-13
    assert np.all(np.asarray(f["dust_absorbed_surface_brightness"]) <= light)


def test_the_dust_is_between_10_and_60_k_wherever_the_disc_has_dust(model, coarse):
    """A sanity bound, not a target. The dust disc ends at 23.7 kpc, where the gas's metals fall away
    and the dust surface density drops five orders of magnitude within a few hundred parsecs; beyond
    it the few grains left sit in the disc's last starlight at 1.5-9 K (the CMB, which would hold them
    at 2.7 K, is not modelled). 'Has dust' is therefore above 1e-5 of the peak surface density."""
    f = coarse[model.name].fields
    T = np.asarray(f["dust_temperature"])
    sigma = np.asarray(f["dust_surface_density"])
    disc = sigma > 1e-5 * sigma.max()
    assert disc.sum() > 0.75 * sigma.size
    assert np.all(np.isfinite(T[disc])) and np.all((T[disc] > 10.0) & (T[disc] < 60.0))
    assert np.all(np.isfinite(T))  # every ring is lit on this grid: no NaN


def test_the_temperature_profile_and_the_infrared_share(model, coarse):
    """Measured at S31 on this grid (default grid in brackets): T = 17.955 (17.968) K at 2 kpc, 20.414
    (20.411) at 5, 19.543 (19.539) at 8.2, 16.621 (16.604) at 12, 16.485 (16.485) at 16; L_IR = 1.6185e10
    (1.6223e10) Lsun, 0.3311 (0.3314) of the disc's intrinsic bolometric light and 0.3020 (0.3023) of disc
    and bulge together. Planck's whole-sky 19.7 K (sigma 1.4 K) is a sky average from the Sun, read to
    source beta before any row was ruled; it is a comparison, not a target (D113)."""
    out = coarse[model.name]
    f, R = out.fields, out.grid.R
    T = np.asarray(f["dust_temperature"])
    for r, want in ((2.0, 17.955), (5.0, 20.414), (8.2, 19.543), (12.0, 16.621), (16.0, 16.485)):
        assert float(np.interp(r, R, T)) == pytest.approx(want, abs=2e-3)
    L = float(f["dust_infrared_luminosity"])
    assert L == pytest.approx(1.6185e10, rel=2e-4)
    assert L / float(f["disc_luminosity"]) == pytest.approx(0.3311, abs=2e-4)


# --- scattering, the field G0 and the PAHs -----------------------------------------------------


def test_the_scattering_fields_are_the_grain_models_share_of_the_extinction(model, coarse):
    f = coarse[model.name].fields
    a_v = np.asarray(f["dust_extinction_v"])
    tau_v = a_v / (2.5 * math.log10(math.e))
    assert np.allclose(f["dust_scattering_optical_depth"], _c(model, "DUST_ALBEDO_V") * tau_v, rtol=1e-15, atol=0.0)
    assert np.allclose(f["dust_colour_excess_b_v"], a_v / 3.1, rtol=1e-15, atol=0.0)
    assert float(f["dust_scattering_asymmetry"]) == _c(model, "DUST_SCATTERING_G")
    # dust_extinction_v is ism's, unchanged (D167): the coefficient times the dust.
    assert np.allclose(a_v, np.asarray(f["dust_surface_density"]) * _c(model, "DUST_EXTINCTION_COEFFICIENT"), rtol=1e-15, atol=0.0)


def test_g0_is_the_star_formations_far_ultraviolet_at_the_midplane(model, coarse):
    """Measured at S31: G0 = 2.63 at 8.2 kpc on this grid (2.64 default), against the local field's 1.7
    in Habing units (Draine 1978 via Wolfire et al. 2003) - a comparison, not a target; 0.056 at 0.5
    kpc, where the far-ultraviolet's absorption depth is 50."""
    out = coarse[model.name]
    f, R = out.fields, out.grid.R
    g0 = np.asarray(f["radiation_field_g0"])
    fuv = np.asarray(f["sfr_surface_density"]) * _c(model, "FUV_LUMINOSITY_PER_SFR") / 1e6 * math.log(13.6 / 6.0)
    tau = (1.0 - _c(model, "DUST_ALBEDO_FUV")) * _c(model, "DUST_EXTINCTION_RATIO_FUV") * np.asarray(f["dust_extinction_v"]) / (
        2.5 * math.log10(math.e))
    assert np.allclose(g0, dust.slab_midplane_flux(fuv, tau) * dust.FLUX_PER_LSUN_PC2 / 1.6e-3, rtol=1e-14, atol=0.0)
    assert float(np.interp(8.2, R, g0)) == pytest.approx(2.632, abs=2e-3)
    assert np.all(g0 >= 0.0) and np.all(np.isfinite(g0))


def test_the_pah_fraction_follows_the_gas_abundance_and_stops_at_the_fits_edge(model, coarse):
    """Remy-Ruyer et al. 2015 eq. 5 read on [Fe/H] + 8.69, held above 1.2 Z_sun. Measured at S31: 11.48%
    in the inner disc (held), 9.10% at 8.2 kpc on this grid (the gas is solar there to 0.002 dex; the
    relation gives 9.06% at solar, twice Draine & Li's Milky Way 4.58%), 1.35% at 16 kpc."""
    out = coarse[model.name]
    f, R = out.fields, out.grid.R
    q = np.asarray(f["pah_fraction"])
    cap = 0.0457 * 10.0 ** (-11.0 + 1.30 * (8.69 + math.log10(1.2)))
    assert q.max() == pytest.approx(cap, rel=1e-14) and cap == pytest.approx(0.11478, abs=5e-6)
    assert 0.0457 * 10.0 ** (-11.0 + 1.30 * 8.69) == pytest.approx(0.090556, abs=5e-6)
    feh = np.asarray(f["feh_gas"])
    free = feh < math.log10(1.2)
    assert np.allclose(q[free], 0.0457 * 10.0 ** (-11.0 + 1.30 * (8.69 + feh[free])), rtol=1e-13, atol=0.0)
    assert np.all(q[~free] == cap)
    assert float(np.interp(8.2, R, q)) == pytest.approx(0.0910, abs=2e-4)
    assert float(np.interp(16.0, R, q)) == pytest.approx(0.01347, abs=5e-5)


def test_both_models_publish_the_same_dust(coarse):
    """The dust reads shared fields only, so the azimuthal model's is basic's bit for bit."""
    for name in FIELDS:
        assert np.array_equal(np.asarray(coarse["basic"].fields[name]), np.asarray(coarse["azimuthal"].fields[name]), equal_nan=True), name
