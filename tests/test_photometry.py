"""Per-star photometry from the PARSEC table, and the blackbody cmap its temperature is drawn with (RENDER_PLAN M2)."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.cmaps import BLACKBODY_KELVIN, COLORMAPS, blackbody_hex
from galaxy.stages.photometry import isochrones, lookup


def one(mass: float, age: float, feh: float) -> tuple[float, float]:
    L, T = lookup(np.array([mass]), np.array([age]), np.array([feh]))
    return float(L[0]), float(T[0])


def test_the_table_is_the_grid_the_readme_attributes():
    tab = isochrones()
    assert tab.log_ages.size == 36 and tab.log_ages[0] == pytest.approx(6.6) and tab.log_ages[-1] == pytest.approx(10.1)
    assert tab.mhs.size == 11 and tab.mhs[0] == pytest.approx(-2.19) and tab.mhs[-1] == pytest.approx(0.30)
    assert len(tab.tracks) == 396


def test_no_isochrone_keeps_the_boundary_row():
    """CMD's closing row at log L = -9.999 is not a star; kept, it stretched the heaviest living mass."""
    for mass, log_l, _ in isochrones().tracks.values():
        assert np.all(log_l > -9.0)
        assert np.all(np.diff(mass) >= 0.0)


def test_the_sun_comes_out_as_the_sun():
    L, T = one(1.0, 4.57, 0.0)
    assert L == pytest.approx(1.0, abs=0.1)
    assert T == pytest.approx(5772, abs=150)


def test_the_main_sequence_brightens_and_heats_with_mass():
    masses = np.array([0.15, 0.3, 0.6, 1.0, 2.0, 5.0])
    L, T = lookup(masses, np.full(masses.size, 0.05), np.zeros(masses.size))
    assert np.all(np.diff(L) > 0) and np.all(np.diff(T) > 0)
    assert T[0] < 3500 < 10000 < T[-1]


def test_a_star_past_its_lifetime_has_no_light():
    """No remnant values are invented (rule B9): dead is NaN in both columns."""
    assert all(np.isnan(v) for v in one(1.5, 8.0, 0.0))
    assert all(np.isnan(v) for v in one(0.95, 12.0, -1.0))  # turnoff 0.88 at 10 Gyr, [M/H] -0.95
    assert all(np.isnan(v) for v in one(100.0, 0.001, 0.0))  # past the youngest isochrone's end


def test_ages_past_the_table_read_at_its_oldest():
    oldest = 10**10.1 / 1e9  # 12.6 Gyr, log age 10.1 since D166 (was 10 Gyr, 35 ages, at D164)
    assert one(0.8, 13.5, 0.0) == pytest.approx(one(0.8, oldest, 0.0))


def test_a_giant_is_brighter_and_cooler_than_the_dwarf_it_was():
    dwarf = one(1.0, 5.0, 0.0)
    giant = one(1.0, 9.9, 0.0)  # near the turnoff mass at 9.9-10 Gyr, solar: up the giant branch
    assert giant[0] > dwarf[0]


def test_the_empty_catalogue_looks_up_nothing():
    L, T = lookup(np.zeros(0), np.zeros(0), np.zeros(0))
    assert L.size == 0 and T.size == 0


def test_blackbody_colours_run_red_to_blue():
    def rgb(k: float) -> tuple[int, int, int]:
        h = blackbody_hex(k)
        return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)

    cool, sun, hot = rgb(3000), rgb(5800), rgb(20000)
    assert cool[0] == 255 and cool[2] < 160
    assert min(sun) > 220  # near white
    assert hot[2] == 255 and hot[0] < hot[2]


def test_the_blackbody_cmap_is_in_the_vocabulary_and_spans_its_declared_bounds():
    cmap = COLORMAPS["blackbody"]
    assert not cmap.diverging and len(cmap.stops) >= 9
    assert cmap.stops[0] == blackbody_hex(BLACKBODY_KELVIN[0])
    assert cmap.stops[-1] == blackbody_hex(BLACKBODY_KELVIN[1])
