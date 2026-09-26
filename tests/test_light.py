"""The disc's unresolved light (RENDER_PLAN R3): the population integral and the fields it publishes."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.photometry import (
    BANDS,
    EXTRA,
    blackbody_linear,
    correlated_temperature,
    isochrones,
    population_at,
    population_light,
)
from galaxy.stages.sfh import fit_scale_length

SMALL = GridSpec(n_R=64, n_t=128, n_z=8, n_phi=36)


def test_a_population_fades_and_reddens_as_it_ages():
    tab, pop = isochrones(), population_light()
    solar = int(np.abs(tab.mhs).argmin())
    light = pop.light_per_mass[:, solar]
    assert light[0] > 100 * light[-1]  # 4 Myr against 10 Gyr
    assert np.all(np.diff(light[::5]) < 0)
    young, old = correlated_temperature(pop.colour[[0, -1], solar])
    assert young > 15000 > 6000 > old


def test_an_old_population_has_the_light_per_mass_of_one():
    """A 10 Gyr solar population emits a few tenths of a solar luminosity per solar mass formed."""
    light, _ = population_at(np.array([10.0]), np.array([0.0]))
    assert 0.1 < light[0] < 0.4


def test_the_colour_temperature_of_a_blackbody_is_its_temperature():
    for kelvin in (3000.0, 5800.0, 12000.0):
        assert correlated_temperature(blackbody_linear(np.array([kelvin])))[0] == pytest.approx(kelvin, rel=0.02)
    assert np.isnan(correlated_temperature(np.zeros((1, 3)))[0])


@pytest.fixture(scope="module")
def outputs():
    models, impls, table = production()
    return {m.name: run(m, None, SMALL, impls=impls, table=table, only=("disc_surface_brightness", "disc_light_temperature", "disc_luminosity")) for m in models}


def test_the_disc_luminosity_is_its_surface_brightness_integrated(outputs):
    for out in outputs.values():
        R = out.grid.R
        brightness = np.asarray(out.fields["disc_surface_brightness"])
        assert np.all(brightness >= 0.0) and brightness.max() > 0.0
        total = float(np.trapezoid(brightness * 2.0 * np.pi * R * PC_PER_KPC**2, R))
        assert out.fields["disc_luminosity"] == pytest.approx(total)
        # A Milky Way disc, bolometric and dust-free: a few 10^10 L☉.
        assert 1e10 < out.fields["disc_luminosity"] < 2e11


def test_the_disc_light_is_a_stellar_colour(outputs):
    for out in outputs.values():
        brightness = np.asarray(out.fields["disc_surface_brightness"])
        temperature = np.asarray(out.fields["disc_light_temperature"])
        lit = brightness > 1e-3 * brightness.max()
        assert np.all((temperature[lit] > 3000.0) & (temperature[lit] < 20000.0))


# --- S28 (BUILD_II Phase 3): the bands, the colour, the mass-to-light ratio, the ionizing photons ---

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
PHOTOMETRIC = (
    *(f"absolute_magnitude_{b.lower()}" for b in BANDS), "colour_b_v", "mass_to_light_v", "bolometric_correction_v",
    "disc_surface_brightness_v", "photometric_scale_length", "ionizing_photon_rate", "ionizing_photon_rate_total",
)
BOLOMETRIC_TOLERANCE = 5e-5  # measured at S28: 1.65e-5 at this grid, 1.58e-5 at the default (CMD prints M_bol to 0.001)


@pytest.fixture(scope="module")
def photometric():
    models, impls, table = production()
    wanted = PHOTOMETRIC + ("disc_luminosity", "bulge_luminosity", "stellar_mass_total", "disc_scale_length_spin", "sfr")
    return {m.name: run(m, None, COARSE, impls=impls, table=table, only=wanted) for m in models}


def solar_bolometric_magnitude() -> float:
    """The M_bol of one L☉ in the table's own M_bol column: CMD's M_bol = M_bol,☉ − 2.5 log L, read back."""
    tab = isochrones()
    zero = np.concatenate([tab.extra[k][:, EXTRA.index("mbol")] + 2.5 * tab.tracks[k][1] for k in tab.tracks])
    assert np.ptp(zero) < 0.01  # printed to three decimals
    return float(np.median(zero))


def test_the_bands_reproduce_the_bolometric_light_with_the_stated_correction(photometric):
    """The gate: M_V plus the published BC_V is the bolometric light the disc and bulge carry.

    Two routes to one number - the bolometric sum of L along each isochrone, and the band route,
    each point's M_bol integrated like a band and published as a correction to M_V. They agree to
    the rounding of CMD's three-decimal M_bol."""
    m_sun = solar_bolometric_magnitude()
    assert m_sun == pytest.approx(4.77, abs=0.001)
    for out in photometric.values():
        f = out.fields
        m_bol = f["absolute_magnitude_v"] + f["bolometric_correction_v"]
        from_bands = 10.0 ** (-0.4 * (m_bol - m_sun))
        assert from_bands == pytest.approx(f["disc_luminosity"] + f["bulge_luminosity"], rel=BOLOMETRIC_TOLERANCE)
        assert -1.5 < f["bolometric_correction_v"] < 0.0  # a population's light is redder than V


def test_the_colour_and_the_mass_to_light_ratio_are_the_magnitudes(photometric):
    for out in photometric.values():
        f = out.fields
        assert f["colour_b_v"] == f["absolute_magnitude_b"] - f["absolute_magnitude_v"]
        L_v = 10.0 ** (-0.4 * (f["absolute_magnitude_v"] - 4.81))
        assert f["mass_to_light_v"] == pytest.approx(f["stellar_mass_total"] / L_v)
        # A disc galaxy's light gets brighter to the red from B onward.
        mags = [f[f"absolute_magnitude_{b.lower()}"] for b in BANDS[1:]]
        assert all(np.diff(mags) < 0.0), mags


def test_the_v_surface_brightness_is_the_disc_part_of_the_v_light(photometric):
    for out in photometric.values():
        f, R = out.fields, out.grid.R
        sigma_v = np.asarray(f["disc_surface_brightness_v"])
        disc_v = float(np.trapezoid(sigma_v * 2.0 * np.pi * R * PC_PER_KPC**2, R))
        total_v = 10.0 ** (-0.4 * (f["absolute_magnitude_v"] - 4.81))
        assert 0.8 * total_v < disc_v < total_v  # the rest is the bulge's (S28: 10.6%)
        R_d = float(f["disc_scale_length_spin"])
        assert f["photometric_scale_length"] == fit_scale_length(sigma_v, R, 1.0, 3.0 * R_d)


def test_the_ionizing_photons_are_todays_star_formation_times_the_yield(photometric):
    for out in photometric.values():
        f, R = out.fields, out.grid.R
        rate = np.asarray(f["ionizing_photon_rate"])
        assert np.all(rate >= 0.0)
        assert f["ionizing_photon_rate_total"] == pytest.approx(float(np.trapezoid(rate * 2.0 * np.pi * R, R)))
        per_sfr = f["ionizing_photon_rate_total"] / f["sfr"]
        print(f"Q per Msun/yr: {per_sfr:.4g}")
        assert 5e52 < per_sfr < 5e53


def test_every_photometric_field_reads_the_same_in_both_models(photometric):
    """The light is radial: the azimuthal model's modulation moves no radial field (S27), so none of these."""
    basic, azimuthal = photometric["basic"].fields, photometric["azimuthal"].fields
    for name in PHOTOMETRIC:
        assert np.array_equal(np.asarray(basic[name]), np.asarray(azimuthal[name])), name
