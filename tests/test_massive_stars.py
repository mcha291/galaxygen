"""Massive stars (BUILD_II Phase 3, S28): Q(H⁰) by ruling (a), the wind, the Wolf-Rayet proxy."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.stages import massive_stars as ms
from galaxy.stages.photometry import imf_weights, isochrones, population_light

SOLAR_RADIUS_CM = 6.957e10  # IAU 2015 nominal [recall]; only the transcription check reads it


# --- the tables: fetched, counted and checked by their own arithmetic (D175) ----------------


def test_the_tables_are_the_rows_that_were_read():
    """SHP03 Table 1 has 15 class V rows, O3-B0.5; MSH05 Table 4 has 12, O3-O9.5 (read at S28)."""
    assert [r[0] for r in ms.SHP03_CLASS_V] == [
        "O3", "O4", "O4.5", "O5", "O5.5", "O6", "O6.5", "O7", "O7.5", "O8", "O8.5", "O9", "O9.5", "B0", "B0.5"]
    assert [r[0] for r in ms.MSH05_CLASS_V] == [
        "O3", "O4", "O5", "O5.5", "O6", "O6.5", "O7", "O7.5", "O8", "O8.5", "O9", "O9.5"]
    assert ms.SHP03_TEFF[0] == 32060.0 and ms.SHP03_TEFF[-1] == 51230.0


@pytest.mark.parametrize("rows, cols", [
    (ms.SHP03_CLASS_V, (1, 3, 4, 6, 7)),  # T_eff, R, log L, log Q, log q
    (ms.MSH05_CLASS_V, (1, 4, 3, 7, 6)),
])
def test_every_row_obeys_its_own_arithmetic(rows, cols):
    """Q = q · 4πR² and L = 4πR²σT⁴ hold row by row to the printed precision: a transcription check.

    Measured at S28: every row within 0.010 dex in both, which is the rounding of numbers printed
    to two decimals of a log and three significant figures of a radius."""
    t, r, log_l, log_q_total, log_q = cols
    for row in rows:
        area = 4.0 * np.pi * (row[r] * SOLAR_RADIUS_CM) ** 2
        assert row[log_q] + np.log10(area) == pytest.approx(row[log_q_total], abs=0.012), row[0]
        L = area * ms.STEFAN_BOLTZMANN * row[t] ** 4 / ms.SOLAR_LUMINOSITY
        assert np.log10(L) == pytest.approx(row[log_l], abs=0.012), row[0]


def test_q_from_l_and_teff_reproduces_the_tables_own_q():
    """The per-star route, Q = q₀(T) L / σT⁴, gives each row's printed log Q_H back."""
    for row in ms.SHP03_CLASS_V:
        Q = ms.ionizing_photons(np.array([10.0 ** row[4]]), np.array([row[1]]))[0]
        assert np.log10(Q) == pytest.approx(row[6], abs=0.012), row[0]


# --- ruling (a) against its named alternative ---------------------------------------------------


def test_the_table_against_the_blackbody_for_an_o5_and_a_b0():
    """Ruling (a)'s comparison, pinned. At S28: O5 V 0.9225, B0 V 0.3583 (table / blackbody).

    The blackbody is close for a mid-O dwarf and nearly three times too bright for a B0: the
    atmosphere's Lyman edge bites harder as the star cools, which is why the ruling tabulates."""
    def ratio(sp: str) -> float:
        row = next(r for r in ms.SHP03_CLASS_V if r[0] == sp)
        L, T = np.array([10.0 ** row[4]]), np.array([row[1]])
        return float(ms.ionizing_photons(L, T)[0] / ms.ionizing_photons(L, T, "blackbody")[0])

    assert ratio("O5") == pytest.approx(0.9225, abs=5e-4)
    assert ratio("B0") == pytest.approx(0.3583, abs=5e-4)


def test_the_two_calibrations_agree_where_they_overlap():
    """SHP03 and MSH05 read at the same T_eff, over MSH05's span: SHP03 is lower everywhere.

    Two atmosphere codes; q₀(T) is the property they share, and this is how far apart they put
    it. Measured at S28: −0.049 dex at 44.9 kK (O3 V in MSH05) widening to −0.285 at 31.9 kK
    (O9.5 V) — a factor of 1.9 for a late-O dwarf. The ruling takes SHP03 because it alone
    reaches the early B stars; this is the size of the choice, stated rather than averaged (B12)."""
    t = np.linspace(ms.MSH05_TEFF[0], ms.MSH05_TEFF[-1], 50)
    diff = np.log10(ms.tabulated_q0(t, "shp03")) - np.log10(ms.tabulated_q0(t, "msh05"))
    assert np.all(diff < 0.0)
    assert diff[-1] == pytest.approx(-0.049, abs=0.002) and diff[0] == pytest.approx(-0.285, abs=0.002)


def test_outside_the_table_the_blackbody_carries_the_shape_joined_at_the_end():
    lo, hi = ms.SHP03_TEFF[0], ms.SHP03_TEFF[-1]
    for edge in (lo, hi):
        assert ms.tabulated_q0(np.array([edge * (1 - 1e-9)]))[0] == pytest.approx(ms.tabulated_q0(np.array([edge * (1 + 1e-9)]))[0], rel=1e-6)
    cool = ms.tabulated_q0(np.array([20000.0, 25000.0, 30000.0]))
    assert np.all(np.diff(cool) > 0)
    assert ms.tabulated_q0(np.array([5772.0]))[0] < 1e-6 * ms.tabulated_q0(np.array([lo]))[0]
    assert np.isnan(ms.ionizing_photons(np.array([np.nan]), np.array([np.nan]))[0])


def test_the_blackbody_integral_is_the_series_it_says():
    """Against a brute-force quadrature of π B_ν / hν above 13.598 eV, at three temperatures."""
    for T in (20000.0, 40000.0, 80000.0):
        nu0 = ms.HYDROGEN_EDGE / ms.PLANCK
        nu = np.linspace(nu0, nu0 * 40, 400001)
        x = ms.PLANCK * nu / (ms.BOLTZMANN * T)
        integrand = 2.0 * np.pi * nu**2 / ms.LIGHT_SPEED**2 / np.expm1(x)
        assert ms.blackbody_q0(np.array([T]))[0] == pytest.approx(np.trapezoid(integrand, nu), rel=1e-5)


# --- what the table cannot see ----------------------------------------------------------------


def test_the_unresolved_top_of_the_imf():
    """The share of a steady population's Q the table cannot see: an estimate, not a bound (S28).

    The youngest isochrone (10^6.6 yr = 3.98 Myr) ends at 63.8 M☉ at solar metallicity; the
    IMF runs to 150. Every star of 63.8-150 M☉ is read as dead at every age the table has, so
    the budget holds none of their photons. The estimate gives each the Q of the heaviest star
    the youngest isochrone holds (4.0e49/s) for 3.98 Myr: 0.489 of the total, the table's
    share 0.511. Its two errors have opposite signs [inferred] - a heavier star emits more than
    that, and it dies before 3.98 Myr (that is why the isochrone does not hold it) - and the
    table cannot say which wins. What it does say: about half of a star-forming galaxy's
    ionizing photons come from stars the table cannot see, so ionizing_photon_rate is a lower
    limit by up to a factor of two. Measured at solar metallicity."""
    tab = isochrones()
    solar = int(np.abs(tab.mhs).argmin())
    mass, log_l, log_teff = tab.track(0, solar)
    top = mass[-1]
    q_top = float(np.nanmax(ms.ionizing_photons(10.0**log_l[mass >= 0.95 * top], 10.0**log_teff[mass >= 0.95 * top])))
    m = np.geomspace(0.08, 150.0, 200001)
    phi = imf_weights(m)
    per_mass = np.trapezoid(phi * m, m)
    heavy = m > top
    missing = q_top * np.trapezoid(np.where(heavy, phi, 0.0), m) / per_mass * 10.0**tab.log_ages[0]  # photons/s · yr per M☉
    ages = 10.0 ** tab.log_ages
    pop = population_light()
    seen = float(np.trapezoid(pop.ionizing_per_mass[:, solar], ages) + ages[0] * pop.ionizing_per_mass[0, solar])
    fraction = missing / (seen + missing)
    print(f"top of the youngest isochrone {top:.1f} Msun, Q there {q_top:.3e}/s; unseen >= {fraction:.3f}")
    assert top == pytest.approx(63.8, abs=0.05)
    assert q_top == pytest.approx(4.006e49, rel=1e-3)
    assert fraction == pytest.approx(0.489, abs=0.001)


def test_how_much_of_a_populations_q_the_table_itself_covers():
    """Of a steady solar population's photons, the share from stars whose T_eff is inside the
    table's 32-51 kK, cooler, and hotter (the stripped post-main-sequence stars the blackbody
    extension carries). Measured at S28, printed and pinned."""
    from galaxy.stages.photometry import _IMF_MASSES, _along

    tab = isochrones()
    solar = int(np.abs(tab.mhs).argmin())
    m = _IMF_MASSES
    phi = imf_weights(m)
    ages = 10.0 ** tab.log_ages
    parts = np.zeros((ages.size, 3))
    for a in range(ages.size):
        track = tab.track(a, solar)
        alive = m <= track[0][-1]
        log_l, log_teff = _along(track, m)
        T = 10.0**log_teff
        Q = np.where(alive, np.nan_to_num(ms.ionizing_photons(10.0**log_l, T)), 0.0)
        for k, sel in enumerate((T < ms.SHP03_TEFF[0], (T >= ms.SHP03_TEFF[0]) & (T <= ms.SHP03_TEFF[-1]), T > ms.SHP03_TEFF[-1])):
            parts[a, k] = np.trapezoid(np.where(sel, phi * Q, 0.0), m)
    total = np.trapezoid(parts, ages, axis=0) + ages[0] * parts[0]
    share = total / total.sum()
    print(f"cooler {share[0]:.4f}, inside {share[1]:.4f}, hotter {share[2]:.4f}")
    assert share == pytest.approx(TABLE_COVERAGE, abs=5e-4)


TABLE_COVERAGE = (0.2177, 0.3283, 0.4540)  # S28: the table itself carries a third of the photons


# --- the wind ---------------------------------------------------------------------------------


def test_the_wind_recipe_at_its_reference_points():
    """Eqs. 24 and 25 at L = 10⁵, M = 30, Z = Z☉ and their own reference temperatures."""
    mdot, v = ms.wind(np.array([1e5, 1e5]), np.array([40000.0, 20000.0]), np.array([30.0, 30.0]), np.ones(2))
    assert np.log10(mdot[0]) == pytest.approx(-6.697 - 1.226 * np.log10(2.6 / 2.0), abs=1e-9)
    assert np.log10(mdot[1]) == pytest.approx(-6.688 - 1.601 * np.log10(1.3 / 2.0), abs=1e-9)
    # v_inf is the ratio times the Newtonian escape velocity at the star's own radius.
    R = np.sqrt(1e5 * ms.SOLAR_LUMINOSITY / (4 * np.pi * ms.STEFAN_BOLTZMANN * 40000.0**4))
    assert v[0] == pytest.approx(2.6 * np.sqrt(2 * ms.SOLAR_GM * 30.0 / R) / 1e5)


def test_the_jump_sits_where_eq_15_puts_it_and_the_recipe_stops_at_its_edges():
    assert ms.jump_temperature(np.array([1.0]))[0] == pytest.approx(1000 * (61.2 + 2.59 * -14.94))
    mdot, v = ms.wind(np.full(3, 1e5), np.array([12000.0, 51000.0, 30000.0]), np.full(3, 30.0), np.ones(3))
    assert np.isnan(mdot[0]) and np.isnan(mdot[1]) and np.isfinite(mdot[2])
    assert np.isnan(v[0]) and np.isnan(v[1])
    # Metal-poor winds are weaker, as 0.85 log Z says.
    def rate(z: float) -> float:
        return float(ms.wind(np.array([1e5]), np.array([40000.0]), np.array([30.0]), np.array([z]))[0][0])

    assert np.log10(rate(0.1)) == pytest.approx(np.log10(rate(1.0)) - 0.85)


def test_the_wind_power_is_half_mdot_v_squared():
    L, T, M = np.array([10**5.73]), np.array([46120.0]), np.array([56.6])
    mdot, v = ms.wind(L, T, M, np.ones(1))
    erg_s = 0.5 * mdot * ms.SOLAR_MASS / ms.SECONDS_PER_YEAR * (v * 1e5) ** 2
    assert ms.wind_luminosity(L, T, M, np.ones(1))[0] == pytest.approx(erg_s[0] / ms.SOLAR_LUMINOSITY)


# --- the Wolf-Rayet proxy ---------------------------------------------------------------------


def test_the_wolf_rayet_proxy_needs_all_four_conditions():
    base = dict(initial_mass=40.0, luminosity=3e5, teff=60000.0, phase=3)
    assert ms.wolf_rayet(**{k: np.array([v]) for k, v in base.items()})[0] == 1
    for key, bad in (("initial_mass", 20.0), ("luminosity", 1e5), ("teff", 25000.0), ("phase", 1)):
        args = {k: np.array([bad if k == key else v]) for k, v in base.items()}
        assert ms.wolf_rayet(**args)[0] == 0, key
    dead = ms.wolf_rayet(np.array([40.0]), np.array([np.nan]), np.array([np.nan]), np.array([-1]))
    assert dead[0] == 0


# --- the catalogue's columns ------------------------------------------------------------------


@pytest.fixture(scope="module")
def catalogues():
    from galaxy.core.grids import GridSpec
    from galaxy.core.registry import production
    from galaxy.run import run

    models, impls, table = production()
    wanted = ("star_mass", "star_age", "star_metallicity", "star_luminosity", "star_temperature",
              "star_magnitude_v", "star_ionizing_photons", "star_wind_luminosity", "star_wolf_rayet")
    return {m.name: run(m, None, GridSpec(n_R=120, n_t=400, n_z=6), impls=impls, table=table, only=wanted) for m in models}


def test_the_catalogue_columns_are_the_functions_of_its_own_columns(catalogues):
    """Looked up inside materialise from the star's own L, T_eff, mass, age and [Fe/H] (D60), never drawn."""
    from galaxy.stages.photometry import lookup_columns

    for out in catalogues.values():
        c = {k: np.asarray(v) for k, v in out.fields.items()}
        L, T = c["star_luminosity"], c["star_temperature"]
        alive = np.isfinite(L)
        assert np.array_equal(np.isfinite(c["star_magnitude_v"]), alive)
        assert np.array_equal(np.isfinite(c["star_ionizing_photons"]), alive)
        np.testing.assert_array_equal(c["star_ionizing_photons"], ms.ionizing_photons(L, T))
        more = lookup_columns(c["star_mass"], c["star_age"], c["star_metallicity"], ("V", "mass_now", "label"))
        np.testing.assert_array_equal(c["star_magnitude_v"], more["V"])
        np.testing.assert_array_equal(
            c["star_wind_luminosity"], ms.wind_luminosity(L, T, more["mass_now"], 10.0 ** c["star_metallicity"]))
        np.testing.assert_array_equal(c["star_wolf_rayet"], ms.wolf_rayet(c["star_mass"], L, T, more["label"]))
        # The wind is only where the recipe reaches: 12.5-50 kK, a small minority of a Kroupa sample.
        windy = np.isfinite(c["star_wind_luminosity"])
        assert np.all((T[windy] >= 12500.0) & (T[windy] <= 50000.0))
        assert windy.sum() < 0.01 * L.size
        print(f"alive {alive.sum()}, windy {windy.sum()}, Wolf-Rayet {c['star_wolf_rayet'].sum()}, "
              f"Q > 1e45: {(c['star_ionizing_photons'] > 1e45).sum()}, brightest M_V {np.nanmin(c['star_magnitude_v']):.2f}")
