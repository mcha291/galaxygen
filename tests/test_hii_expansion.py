"""S102 (batch Q, #232; docs/READING_HII_SIZES.md): an HII region's size once it has outgrown its natal clump. The
D-type front (Hosokawa & Inutsuka 2006 as Bisbas et al. 2015 eq. 13), its stagnation radius (Bisbas eq. 17), the
cloud's turbulence as pressure (Tremblin et al. 2014 eqs. 8 and 16), the cap at the cloud, and photon balance at the
new radius. The law by hand, its limits, its closure; then the model's numbers, DISCLOSED (not judged: the S101
reader printed the model's numbers under this law before it was built)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import nebular as nb
from galaxy.stages.clouds import sound_speed
from galaxy.stages.massive_stars import SECONDS_PER_YEAR, SOLAR_LUMINOSITY
from galaxy.stages.systems import Catalogue

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)  # tests/test_nebular.py's coarse grid
PC = nb.CM_PER_PC
KMS = 1.0e5
MYR = 1.0e6 * SECONDS_PER_YEAR


@pytest.fixture(scope="module")
def constants():
    ms, _, _ = production()
    return {k: v.value for k, v in ms.get(DEFAULT_MODEL).constants.items()}


@pytest.fixture(scope="module")
def coarse():
    ms, _, _ = production()
    return run(ms.get(DEFAULT_MODEL), grid=COARSE)


def test_the_law_by_hand_at_two_points():
    """R_D = R_St (1 + (7/4) sqrt(4/3) c_i t / R_St)^(4/7); R_STAG = R_St (8/3)^(2/3) (c_i/c_0)^(4/3);
    c_0eff = sqrt(c_s^2 + sigma^2/3). Written out by hand for R_St = 1 pc, c_i = 10 km/s."""
    ci_t_pc = 10.0 * KMS * 1.0 * MYR / PC  # c_i t at 1 Myr: 10.227 pc
    assert ci_t_pc == pytest.approx(10.227, abs=1e-3)
    for t_myr, want in ((1.0, 5.7979), (5.0, 14.234)):
        by_hand = (1.0 + 1.75 * math.sqrt(4.0 / 3.0) * ci_t_pc * t_myr) ** (4.0 / 7.0)
        got = nb.d_type_radius(np.array([PC]), 10.0 * KMS, np.array([t_myr * MYR]))[0] / PC
        assert got == pytest.approx(by_hand, rel=1e-12) and got == pytest.approx(want, rel=1e-3)
    # stagnation at c_0 = 1 km/s: (8/3)^(2/3) 10^(4/3) = 1.9230 x 21.544 = 41.43 pc
    assert nb.stagnation_radius(np.array([PC]), 10.0, np.array([1.0]))[0] / PC == pytest.approx(41.43, rel=1e-3)
    assert nb.stagnation_radius(np.array([PC]), 10.0, np.array([10.0]))[0] / PC == pytest.approx((8.0 / 3.0) ** (2.0 / 3.0), rel=1e-12)
    # the cloud's effective sound speed: 10 K molecular gas (0.19 km/s, Bergin & Tafalla's 0.2) with sigma = 3 km/s
    c_s = sound_speed(10.0, 2.33)
    assert c_s == pytest.approx(0.189, abs=1e-3)
    # the gate's ruling 1 (S102): Tremblin's sigma^2/3 is a third of a 3-D variance; the cloud's sigma_v is 1-D, so
    # c_0^2 = c_s^2 + sigma_v^2 (was + sigma_v^2/3 in the lane's first commit)
    assert nb.effective_sound_speed(c_s, np.array([3.0]))[0] == pytest.approx(math.sqrt(c_s**2 + 9.0), rel=1e-12)
    assert nb.effective_sound_speed(c_s, np.array([0.0]))[0] == c_s
    # photon balance: n = n_St (R_St/R)^(3/2), so n^2 R^3 is conserved
    n = nb.expanded_density(np.array([100.0]), np.array([1.0]), np.array([4.0]))[0]
    assert n == pytest.approx(12.5) and n**2 * 4.0**3 == pytest.approx(100.0**2 * 1.0)


def test_the_limits_and_monotonic_in_age():
    """t -> 0 gives R_St exactly; t -> infinity passes any stagnation radius; the radius never falls with age."""
    r_st = np.array([0.3, 1.0, 7.0]) * PC
    assert np.array_equal(nb.d_type_radius(r_st, 10.0 * KMS, np.zeros(3)), r_st)
    assert np.array_equal(nb.d_type_radius(np.zeros(1), 10.0 * KMS, np.array([MYR])), np.zeros(1))
    t = np.linspace(0.0, 20.0, 401) * MYR
    r = nb.d_type_radius(np.full_like(t, PC), 10.0 * KMS, t)
    assert np.all(np.diff(r) > 0.0)
    assert nb.d_type_radius(np.array([PC]), 10.0 * KMS, np.array([1.0e4 * MYR]))[0] > nb.stagnation_radius(np.array([PC]), 10.0, np.array([0.5]))[0]


def _synthetic(constants, ages, masses, sigmas, size=30.0, q=1.0e48):
    k = len(ages)
    clusters = Catalogue.of({
        "cluster_ionizing_photons": np.broadcast_to(np.asarray(q, dtype=float), (k,)).copy(), "cluster_metallicity": np.zeros(k),
        "cluster_age": np.asarray(ages, dtype=float), "cluster_birth_radius": np.full(k, 8.0),
    }, ((0, k),))
    clouds = Catalogue.of({
        "cloud_mass": np.asarray(masses, dtype=float), "cloud_size": np.full(k, size), "cloud_density_pdf_width": np.full(k, 1.0),
        "cloud_alpha": np.zeros(k), "cloud_cluster_index": np.arange(k, dtype=float),
        "cloud_velocity_dispersion": np.asarray(sigmas, dtype=float),
    }, ((0, k),))
    return clusters, clouds, nb.materialise_nebular(clusters, clouds, constants)


def test_each_limit_and_the_cap_on_a_synthetic_census(constants):
    """Q = 1e48 /s in 30 pc clouds: three of 1e5 Msun (R_St 2.3 pc) at age 0 (the Stromgren sphere, 'expansion'),
    0.5 Myr (expanding), 3.9 Myr at sigma 5 km/s (stagnated inside the cloud, R_STAG ~ 11 pc); one of 1e4 Msun
    (R_St ~ 11 pc) at 3.9 Myr and sigma 0.5 km/s (capped at the cloud); one of 1e3 Msun too thin to hold its Stromgren
    sphere (R_St ~ 50 pc): leaking as before, its radius the cloud's, its density the clump's. S104 (#235): the ages
    were 1000 Myr (and the capped cloud 1e5 Msun), past the rate's fall, where the peak rate now drives the shell;
    under 3.98 Myr the model's rate is its peak, so these regions are S102's law exactly, the shell the radius."""
    _, _, reg = _synthetic(constants, [0.0, 0.5, 3.9, 3.9, 0.0], [1e5, 1e5, 1e5, 1e4, 1e3], [5.0, 5.0, 5.0, 0.5, 5.0])
    assert np.array_equal(np.asarray(reg["hii_shell_radius"]), np.asarray(reg["hii_radius"]))
    rs, r = np.asarray(reg["hii_stromgren_radius"]), np.asarray(reg["hii_radius"])
    lim = np.asarray(reg["hii_radius_limit"]).tolist()
    assert lim == [0, 0, 1, 2, 2]
    assert r[0] == rs[0] and rs[1] < r[1] < 30.0
    c_i = float(constants["SHELL_SOUND_SPEED"])
    c_0 = nb.effective_sound_speed(sound_speed(float(constants["MOLECULAR_GAS_TEMPERATURE"]), float(constants["MOLECULAR_MEAN_WEIGHT"])), np.array([5.0]))
    assert r[2] == pytest.approx(rs[2] * (8.0 / 3.0) ** (2.0 / 3.0) * (c_i / c_0[0]) ** (4.0 / 3.0), rel=1e-12)
    assert r[2] < 30.0 and r[3:] == pytest.approx([30.0, 30.0], rel=1e-14) and r[4] == rs[4]
    assert np.asarray(reg["hii_density_bounded"]).tolist() == [0, 0, 0, 0, 1]
    n = np.asarray(reg["hii_electron_density"])
    assert n[0] > n[1] > n[2] > n[3]
    assert n[4] == pytest.approx(n[0] * 1.0e-2, rel=1e-12)  # the clump's rms, mass 100x less in the same size
    # the Halpha is the same whatever the size: the photons kept are the same
    L = np.asarray(reg["hii_halpha_luminosity"])
    assert np.array_equal(L[:4], np.full(4, L[0]))
    # and the leaking region's photons are today's rule's: (r_cloud / R_St)^3 of them
    assert L[4] < L[0]


def test_the_peak_rate_off_the_models_own_table():
    """S104 (#235): Q_peak / Q_now off population_light().ionizing_per_mass, read as the clusters stage reads it. The
    peak is exact (the reading is linear between isochrones): it equals a dense sampling of [0, age]; it is today's
    rate, ratio exactly 1, for the table's first 4 Myr (the youngest isochrone's); it never falls with age; and the
    rate falls far by 20 Myr (S104 measured 20-140x over the census)."""
    from galaxy.stages import photometry as ph

    table = ph.population_light().ionizing_per_mass
    ages = np.array([0.0, 1.0, 3.9, 4.5, 6.0, 8.0, 12.0, 20.0])
    for feh in (-0.5, 0.0, 0.3):
        f = np.full(ages.size, feh)
        ratio = nb.peak_rate_ratio(ages, f)
        assert np.array_equal(ratio[:3], np.ones(3))
        assert np.all(ratio >= 1.0) and np.all(np.diff(ratio) >= 0.0) and ratio[-1] > 20.0
        grid = ages[:, None] * np.linspace(0.0, 1.0, 2001)[None, :]
        sampled = ph.per_mass_at(table, grid / 1000.0, np.full(grid.shape, feh)).max(axis=1)
        assert np.allclose(ph.peak_per_mass_at(table, ages / 1000.0, f), sampled, rtol=1e-12)


def test_a_region_grown_at_its_peak_rate(constants):
    """S104 (#235), by hand: a cluster of 10 Myr whose rate has fallen by Q_peak/Q_now = k. Its shell is S102's law
    grown from the Stromgren sphere of the peak rate; the gas inside sits at n_i = n_rms (R_St,peak / R_shell)^1.5;
    today's photons ionize it to R_ion = R_shell k^(-1/3), where photon balance closes with today's kept photons;
    R_ion lies between the natal Stromgren sphere of today's rate and the shell; the Halpha is today's photons', the
    same as a region of the same Q at age 0; and a 2 Myr region (k = 1) is S102's region exactly."""
    q = 1.0e48
    _, _, reg = _synthetic(constants, [10.0, 0.0, 2.0], [1e6, 1e6, 1e6], [5.0, 5.0, 5.0], size=60.0, q=q)
    k = float(nb.peak_rate_ratio(np.array([10.0]), np.zeros(1))[0])
    assert k > 5.0
    t_e = np.asarray(reg["hii_temperature"], dtype=float)
    alpha = float(nb.alpha_b(t_e[:1])[0])
    clump = math.exp(1.0)
    n_rms = math.sqrt(clump) * float(nb.mean_hydrogen_density(np.array([1e6]), np.array([60.0]), float(constants["HII_MASS_PER_HYDROGEN"]))[0])
    kept = (1.0 - float(constants["HII_ESCAPE_FRACTION"])) * q
    r_st_peak = (3.0 * kept * k / (4.0 * math.pi * alpha * n_rms**2)) ** (1.0 / 3.0)
    c_i = float(constants["SHELL_SOUND_SPEED"]) * KMS
    c_0 = float(nb.effective_sound_speed(sound_speed(float(constants["MOLECULAR_GAS_TEMPERATURE"]), float(constants["MOLECULAR_MEAN_WEIGHT"])), np.array([5.0]))[0]) * KMS
    r_d = r_st_peak * (1.0 + 1.75 * math.sqrt(4.0 / 3.0) * c_i * 10.0 * MYR / r_st_peak) ** (4.0 / 7.0)
    r_stag = r_st_peak * (8.0 / 3.0) ** (2.0 / 3.0) * (c_i / c_0) ** (4.0 / 3.0)
    shell = min(r_d, r_stag, 60.0 * PC)
    assert shell < 60.0 * PC  # this region is not capped: the law alone sets it
    got_shell = float(np.asarray(reg["hii_shell_radius"])[0]) * PC
    r_ion = float(np.asarray(reg["hii_radius"])[0]) * PC
    n_i = float(np.asarray(reg["hii_electron_density"])[0])
    assert got_shell == pytest.approx(shell, rel=1e-12)
    assert n_i == pytest.approx(n_rms * (r_st_peak / shell) ** 1.5, rel=1e-12)
    assert r_ion == pytest.approx(shell * k ** (-1.0 / 3.0), rel=1e-12) and r_ion < got_shell
    assert alpha * n_i**2 * 4.0 / 3.0 * math.pi * r_ion**3 == pytest.approx(kept, rel=1e-12)  # balance with today's Q
    assert r_ion > float(np.asarray(reg["hii_stromgren_radius"])[0]) * PC
    L = np.asarray(reg["hii_halpha_luminosity"])
    assert np.array_equal(L, np.full(3, L[1]))
    # the young region: shell = radius = S102's min(R_D, R_STAG) from today's R_St
    r_st = float(np.asarray(reg["hii_stromgren_radius"])[2]) * PC
    s102 = min(float(nb.d_type_radius(np.array([r_st]), c_i, np.array([2.0 * MYR]))[0]), float(nb.stagnation_radius(np.array([r_st]), c_i, np.array([c_0]))[0]))
    assert float(np.asarray(reg["hii_radius"])[2]) * PC == pytest.approx(s102, rel=1e-14)
    assert np.asarray(reg["hii_radius"])[2] == np.asarray(reg["hii_shell_radius"])[2]


def test_photon_balance_closes_and_the_halpha_is_unchanged(constants, coarse):
    """On the default model's census: every non-leaking region's recombinations at its new radius and density are
    the photons it keeps, alpha_B n_e^2 (4/3) pi R^3 = (1 - f_esc) Q; its Halpha is those photons' (unchanged by the
    size: the closure R2 asks); the emissivity times the new volume is the Halpha; the Stromgren radius is
    R_St and the new radius never below it."""
    F = coarse.fields
    q = np.asarray(F["cluster_ionizing_photons"], dtype=float)
    leak = np.asarray(F["hii_density_bounded"]) == 1
    t_e = np.asarray(F["hii_temperature"], dtype=float)
    n = np.asarray(F["hii_electron_density"], dtype=float)
    r = np.asarray(F["hii_radius"], dtype=float) * PC
    rs = np.asarray(F["hii_stromgren_radius"], dtype=float) * PC
    kept = (1.0 - float(constants["HII_ESCAPE_FRACTION"])) * q
    ok = ~leak & (q > 0)
    assert ok.sum() > 1000
    rec = nb.alpha_b(t_e) * n**2 * 4.0 / 3.0 * math.pi * r**3
    assert np.allclose(rec[ok], kept[ok], rtol=1e-9)
    L = np.asarray(F["hii_halpha_luminosity"], dtype=float) * SOLAR_LUMINOSITY
    assert np.allclose(L[ok], (kept * nb.halpha_per_recombination(t_e))[ok], rtol=1e-12)
    em = np.asarray(F["hii_halpha_emissivity"], dtype=float)
    assert np.allclose((em * 4.0 / 3.0 * math.pi * r**3)[ok], L[ok], rtol=1e-9)
    # R_STAG < R_St would need c_0 above ~16 km/s ((8/3)^(2/3) (c_i/c_0)^(4/3) < 1): no cloud of the census has it
    assert np.all(r >= rs)
    cloud = np.asarray(F["cloud_size"], dtype=float)[np.flatnonzero(np.asarray(F["cloud_cluster_index"]) >= 0)] * PC
    assert np.all(r <= cloud * (1.0 + 1e-12))
    # S104 (#235): today's ionized sphere lies inside the shell the peak rate drove, the shell inside the cloud, and the
    # shell is the radius wherever today's rate is the peak (the table's first 4 Myr)
    shell = np.asarray(F["hii_shell_radius"], dtype=float) * PC
    assert np.all(r <= shell) and np.all(shell <= cloud * (1.0 + 1e-12))
    young = nb.peak_rate_ratio(np.asarray(F["cluster_age"], dtype=float), np.asarray(F["cluster_metallicity"], dtype=float)) == 1.0
    assert young.sum() > 100 and np.array_equal(r[young], shell[young]) and np.all(r[~young & ~leak] < shell[~young & ~leak])


@pytest.fixture(scope="module")
def default():
    ms, _, _ = production()
    return run(ms.get(DEFAULT_MODEL))


def test_the_default_regions_under_the_law_disclosed(default):
    """DISCLOSED, as measured at S102 on the default grid (milky_way, the default galaxy); not judged (the S101 reader
    printed the model's numbers under this law first). Before (main 8db2cee): radius median / p99 / max 0.770 / 7.67 /
    25.7 pc (the Stromgren sphere), n_e median 153.7 cm^-3, log U median -2.831, 7 regions wider than 19.5 pc radius
    holding 6.0 % of the census's Halpha, no log U on the grid's -4 floor. S104 (#235, batch R) re-pinned the region's
    numbers, the shell driven at the cluster's peak rate and today's sphere inside it; batch Q's (S102) in comments."""
    F = default.fields
    r = np.asarray(F["hii_radius"], dtype=float)
    L = np.asarray(F["hii_halpha_luminosity"], dtype=float)
    assert [float(np.median(r)), float(np.percentile(r, 99)), float(r.max())] == pytest.approx([5.4746, 26.310, 52.889], rel=2e-3)  # S102: 10.992 / 36.36 / 70.57; S102 first commit (sigma^2/3): 11.900 / 39.72 / 70.57
    shell = np.asarray(F["hii_shell_radius"], dtype=float)
    assert [float(np.median(shell)), float(np.percentile(shell, 99)), float(shell.max())] == pytest.approx([12.560, 60.776, 109.95], rel=2e-3)  # S104: new
    assert float(np.median(np.asarray(F["hii_stromgren_radius"]))) == pytest.approx(0.770, abs=0.01)  # unchanged
    assert float(np.median(np.asarray(F["hii_electron_density"]))) == pytest.approx(9.416, rel=0.01)  # S102: 3.196; first commit: 2.305
    assert float(np.median(np.asarray(F["hii_ionization_parameter"]))) == pytest.approx(-3.244, abs=0.01)  # S102: -3.426; first commit: -3.457
    lim = np.asarray(F["hii_radius_limit"])
    # which limit binds the shell, by count: expansion / stagnation / cloud; by Halpha 0.704 / 0.042 / 0.254 (S102 0.704 /
    # 0.073 / 0.223; first commit 0.763 / 0.013 / 0.224). R_STAG scales with the peak rate's R_St, so the cloud binds first.
    assert [float((lim == k).mean()) for k in range(3)] == pytest.approx([0.2246, 0.0413, 0.7342], abs=2e-3)  # S102: 0.2308 / 0.3209 / 0.4483; first commit: 0.3353 / 0.1278 / 0.5370
    assert [float(L[lim == k].sum() / L.sum()) for k in range(3)] == pytest.approx([0.704, 0.042, 0.254], abs=5e-3)
    wide = r > 19.5  # half the frame's 39 pc pixel
    assert int(wide.sum()) == 431 and float(L[wide].sum() / L.sum()) == pytest.approx(0.448, abs=2e-3)  # S102: 1482, 0.490; first commit: 1956, 0.511
    # low U reads the grid's floor (clamped, as FSPS clamps; recorded, not mended): 4.5 % of the regions (S102: 8.5 %), 0.003 % of the light
    floor = np.asarray(F["hii_ionization_parameter"]) <= -4.0
    assert float(floor.mean()) == pytest.approx(0.0448, abs=2e-3) and float(L[floor].sum() / L.sum()) < 1e-3  # S102: 0.0850
    # S104: the Halpha is batch Q's (fccecee) bit for bit (every region, compared at S104) - its sum as measured there,
    # Lsun, to the summation order's last bit
    assert float(L.sum()) == pytest.approx(41518643.58704805, rel=1e-14)
    # the gate's ruling 4 (S102): the bubbles read the natal density (hii_natal_density), so they are main's bit for
    # bit - median 9.575 pc, 97.42 % stalled (the first commit, reading the expanded density: 86.69 pc, 81.19 %)
    assert float(np.median(np.asarray(F["bubble_radius"]))) == pytest.approx(9.575127483783945, rel=1e-12)
    assert float(np.mean(np.asarray(F["bubble_stalled"]) == 1)) == pytest.approx(0.9742456568119475, rel=1e-12)
    rs = np.asarray(F["hii_stromgren_radius"], dtype=float)
    n_st = np.asarray(F["hii_natal_density"], dtype=float)
    bounded = np.asarray(F["hii_density_bounded"]) == 0
    assert np.allclose(np.asarray(F["hii_electron_density"])[bounded], (n_st * (rs / r) ** 1.5)[bounded], rtol=1e-12)
