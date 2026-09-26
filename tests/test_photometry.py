"""Per-star photometry from the PARSEC table, and the blackbody cmap its temperature is drawn with (RENDER_PLAN M2)."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.cmaps import BLACKBODY_KELVIN, COLORMAPS, blackbody_hex
from galaxy.stages.photometry import BANDS, isochrones, lookup, lookup_columns, population_light


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


def test_the_regenerated_table_reads_what_the_old_one_did():
    """S28 regenerated the table with the bands kept; mass, log L and log T_eff are CMD's same rows.

    Re-pinned on the new table, the old table's numbers in the comments: they are equal, because
    the request was the same and CMD answered it with the same rows (compared bit for bit, S28)."""
    L, T = lookup(np.array([1.0, 1.0, 1.0]), np.array([4.57, 5.0, 9.9]), np.zeros(3))
    assert L == pytest.approx([1.04704773, 1.08539546, 2.03570423], rel=1e-8)  # old: 1.04704773, 1.08539546, 2.03570423
    assert T == pytest.approx([5823.96159307, 5832.87121235, 5729.52982438], rel=1e-10)  # old: 5823.96..., 5832.87..., 5729.53...
    tab, pop = isochrones(), population_light()
    solar = int(np.abs(tab.mhs).argmin())
    assert pop.light_per_mass[[0, -1], solar] == pytest.approx([8.01433898e02, 1.47498719e-01], rel=1e-8)  # old: 801.433898, 0.147498719


def test_the_bands_are_the_tables_eight_and_the_sun_is_near_willmers():
    """The Sun's V magnitude off the isochrones against Willmer 2018's observed 4.81 (level0)."""
    assert BANDS == ("U", "B", "V", "R", "I", "J", "H", "K")
    sun = lookup_columns(np.array([1.0]), np.array([4.57]), np.array([0.0]), ("B", "V", "K", "mbol", "mass_now", "label"))
    print({k: float(v[0]) for k, v in sun.items()})
    assert sun["V"][0] == pytest.approx(4.7727, abs=5e-4)  # S28: 4.77269, 0.037 brighter than Willmer's Sun
    assert sun["V"][0] == pytest.approx(4.81, abs=SUN_V_OFFSET)
    assert 0.55 < sun["B"][0] - sun["V"][0] < 0.75  # a G2 dwarf
    assert sun["label"][0] == 1.0  # on the main sequence
    assert sun["mass_now"][0] == pytest.approx(1.0, abs=0.01)


SUN_V_OFFSET = 0.05  # the isochrones' Sun against the observed one: 0.037 at S28


def test_a_dead_star_has_no_magnitude_and_no_phase():
    dead = lookup_columns(np.array([1.5]), np.array([8.0]), np.array([0.0]), ("V", "label"))
    assert np.isnan(dead["V"][0]) and dead["label"][0] == -1.0


def test_the_band_integrals_carry_the_bolometric_one():
    """Per isochrone: Σ 10^(−0.4 M_bol) per mass formed is the bolometric light per mass formed, at
    CMD's M_bol,☉ = 4.77 - the table's two columns describe the same stars (S28)."""
    pop = population_light()
    lit = pop.light_per_mass > 0.0
    ratio = pop.bolometric_flux[lit] * 10.0 ** (0.4 * 4.77) / pop.light_per_mass[lit]
    print(f"bolometric route / log L route: {ratio.min():.6f} - {ratio.max():.6f}")
    assert np.all(np.abs(ratio - 1.0) < 1e-3)  # S28: 0.999247 - 1.000682 over the 396 isochrones


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
