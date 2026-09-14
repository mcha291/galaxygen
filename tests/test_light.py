"""The disc's unresolved light (RENDER_PLAN R3): the population integral and the fields it publishes."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.photometry import blackbody_linear, correlated_temperature, isochrones, population_at, population_light

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
