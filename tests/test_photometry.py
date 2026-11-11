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
    # S93 (#113 / #171): re-pinned on the lookup along equivalent points - at an age between two isochrones the
    # star is read on the isochrone built point by point between them, not at its initial mass on each; was
    # 1.04704773, 1.08539546, 2.03570423 and 5823.96159307, 5832.87121235, 5729.52982438 (the table unchanged).
    assert L == pytest.approx([1.0416919899, 1.0850674864, 2.0248682039], rel=1e-8)  # old table: 1.04704773, 1.08539546, 2.03570423
    assert T == pytest.approx([5819.2982012888, 5832.6463136627, 5744.9645328922], rel=1e-10)  # old table: 5823.96..., 5832.87..., 5729.53...
    tab, pop = isochrones(), population_light()
    solar = int(np.abs(tab.mhs).argmin())
    # old table: 801.433898, 0.147498719 (the same on both tables, S28). # S49 (D204, #126): the light integrated along the isochrone's points; was those
    assert pop.light_per_mass[[0, -1], solar] == pytest.approx([8.04037928e02, 2.26344953e-01], rel=1e-8)


def test_the_bands_are_the_tables_eight_and_the_sun_is_near_willmers():
    """The Sun's V magnitude off the isochrones against Willmer 2018's observed 4.81 (level0)."""
    assert BANDS == ("U", "B", "V", "R", "I", "J", "H", "K")
    sun = lookup_columns(np.array([1.0]), np.array([4.57]), np.array([0.0]), ("B", "V", "K", "mbol", "mass_now", "label"))
    print({k: float(v[0]) for k, v in sun.items()})
    # S93 (#113 / #171): re-pinned on the lookup along equivalent points (4.57 Gyr lies between two isochrones); was
    # 4.7727 (S28: 4.77269, 0.037 brighter than Willmer's Sun), now 0.029 brighter.
    assert sun["V"][0] == pytest.approx(4.7809, abs=5e-4)
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


# --- S49 (D204, debt #126): the population's light along the isochrone's own points, checked by a path that is not it


GATE_ISOCHRONES = [(a, z) for a in (0, 5, 10, 15, 20, 25, 30, 35) for z in (0, 5, 9)]  # 4 Myr-12.6 Gyr; [M/H] -2.19, -0.94, +0.05


def _brute(a: int, z: int, flat: bool) -> np.ndarray:
    """(light, V, K, bolometric) per M☉ formed on isochrone (a, z), by the trapezoid in mass the field used until S49
    - φ(m) times each quantity read along the track by ``_along`` (log L and the magnitudes linear in initial mass) -
    on a fine grid inside each interval between consecutive points (every interval cut so that no quantity changes
    by more than 0.002 dex across a cut, and at least 256 times; each interval read alone, so a repeated mass is a
    jump between its two points), and below the first point on 4 000 log-spaced masses at its values. The mass formed
    is the same trapezoid of φ m on 400 000 log-spaced masses. ``flat`` holds φ inside each interval at its mean over
    the interval (that trapezoid of φ divided by the width): where the segments put the interval's stars. No segment
    code, no analytic IMF."""
    from galaxy.stages.photometry import EXTRA, _along, imf_weights
    from galaxy.stages.systems import IMF_MAX, IMF_MIN

    tab = isochrones()
    m, log_l, _ = tab.track(a, z)
    g = np.column_stack([log_l, -0.4 * tab.extra[(a, z)][:, [EXTRA.index(c) for c in ("V", "K", "mbol")]]])
    below = np.geomspace(IMF_MIN, m[0], 4000)
    total = np.trapezoid(imf_weights(below), below) * 10.0 ** g[0]
    jump = np.abs(np.diff(g, axis=0)).max(axis=1)
    for i in np.flatnonzero(np.diff(m) > 0.0):
        mm = np.linspace(m[i], m[i + 1], max(int(np.ceil(jump[i] / 0.002)), 256) + 1)
        q = np.column_stack([_along((m[i : i + 2], g[i : i + 2, k], g[i : i + 2, k]), mm)[0] for k in range(g.shape[1])])
        phi = imf_weights(mm)
        if flat:
            phi = np.full(mm.size, np.trapezoid(phi, mm) / (m[i + 1] - m[i]))
        total = total + np.trapezoid(phi[:, None] * 10.0**q, mm, axis=0)
    every = np.geomspace(IMF_MIN, IMF_MAX, 400_000)
    return total / np.trapezoid(imf_weights(every) * every, every)


def test_the_population_light_against_a_brute_force_integral():
    """B3: the light per mass formed (bolometric, V, K and CMD's own bolometric magnitude's) of 24 isochrones, 4 Myr to
    12.6 Gyr at three metallicities, against :func:`_brute`. Two readings. With φ held at its mean inside each
    interval - where the segments put the interval's stars - the agreement measures the quadrature itself: S49
    (D204) 6.3e-8 worst. With φ(m) itself the difference is the segments' reading, the IMF's number in an interval
    spread uniformly along it, against φ falling across an interval: S49 1.13e-3 worst (the light of the 4 Myr
    isochrone at [M/H] -0.94, whose upper main sequence has points 10-25 % apart in mass), median 4e-4; D204's
    1e-3 is missed there and recorded, not loosened. The fixed-grid trapezoid this replaced missed by up to a
    factor of seven (D202)."""
    pop = population_light()
    k_v, k_k = BANDS.index("V"), BANDS.index("K")
    worst_flat = worst_phi = 0.0
    for (a, z) in GATE_ISOCHRONES:
        ours = np.array([pop.light_per_mass[a, z], pop.band_flux[a, z, k_v], pop.band_flux[a, z, k_k], pop.bolometric_flux[a, z]])
        worst_flat = max(worst_flat, float(np.abs(ours / _brute(a, z, True) - 1.0).max()))
        worst_phi = max(worst_phi, float(np.abs(ours / _brute(a, z, False) - 1.0).max()))
    print(f"worst relative difference: phi at its interval mean {worst_flat:.3e}, phi(m) {worst_phi:.5e}")
    assert worst_flat < 1e-6
    assert worst_phi == pytest.approx(PHI_WORST, abs=2e-5)


PHI_WORST = 1.13e-3  # S49 (D204): the gate's worst against the trapezoid with φ(m), on the 4 Myr [M/H] -0.94 isochrone


# --- S93 (#113 / #171): the lookup along equivalent points -----------------------------------------------------


def test_at_a_table_age_the_lookup_reads_the_isochrone_itself():
    """At an isochrone's own age the isochrone built between it and its neighbour is itself (f = 0 on the union of
    their equivalent points, each piecewise linear in xi between its own points), so a star reads the track in
    initial mass as ``_along`` does - the reading before S93 at the table's ages. Below the giant branch, where no
    two points share a mass."""
    from galaxy.stages.photometry import _along

    tab = isochrones()
    for a in (3, 12, 20, 28, 34):
        for z in (1, 6, 10):
            m, _, _ = tab.track(a, z)
            label = tab.extra[(a, z)][:, -1]
            top = m[np.flatnonzero(label >= 3)[0] - 1]
            mass = np.linspace(m[0], top, 257)[1:-1]
            age = np.full(mass.size, 10.0 ** tab.log_ages[a] / 1e9)
            L, T = lookup(mass, age, np.full(mass.size, float(tab.mhs[z])))
            log_l, log_t = _along(tab.track(a, z), mass)
            assert np.log10(L) == pytest.approx(log_l, abs=1e-9)
            assert np.log10(T) == pytest.approx(log_t, abs=1e-9)


def test_the_imf_s_stars_through_the_lookup_carry_the_population_s_light():
    """#171's cause, measured where it lives: 10^6 stars drawn from the IMF (``systems.imf_sample``, seeded) at one age
    between two isochrones, through ``lookup``, summed over the mass formed (the IMF's mean mass a star), against the
    population's light per mass formed at that age (``population_at``, the isochrones' own integrals blended in log
    age). Before S93 the lookup read both isochrones at the star's initial mass and dropped the short evolved phases:
    0.43-0.49 at 5.6-11 Gyr, 0.50-0.52 at 2.8 Gyr, 0.74-0.78 at 1.1 Gyr, 0.80-0.88 at 355 Myr (measured at S93 on 2 x
    10^6 draws). Along equivalent points (S93): 0.947-1.043 over these 21 cases at these 10^6 draws (0.952-1.019 over
    27 at 2 x 10^6), the Monte Carlo spread a few per cent (the light of an old population rides on its few hundred AGB stars)."""
    from galaxy.stages.photometry import population_at
    from galaxy.stages.systems import imf_mean_mass, imf_sample

    tab = isochrones()
    m = imf_sample(np.random.default_rng(171).random(1_000_000))
    worst = []
    for log_age in (6.75, 7.55, 8.55, 9.05, 9.45, 9.75, 10.05):
        for z in (2, 6, 10):
            age = np.full(m.size, 10.0**log_age / 1e9)
            feh = np.full(m.size, float(tab.mhs[z]))
            L, _ = lookup(m, age, feh)
            ref, _ = population_at(age[:1], feh[:1])
            worst.append(float(np.nansum(L) / (m.size * imf_mean_mass()) / ref[0]))
    assert np.all(np.abs(np.asarray(worst) - 1.0) < 0.07), worst
