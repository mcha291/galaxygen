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
    assert nb.effective_sound_speed(c_s, np.array([3.0]))[0] == pytest.approx(math.sqrt(c_s**2 + 3.0), rel=1e-12)
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
        "cluster_ionizing_photons": np.full(k, q), "cluster_metallicity": np.zeros(k),
        "cluster_age": np.asarray(ages, dtype=float), "cluster_birth_radius": np.full(k, 8.0),
    }, ((0, k),))
    clouds = Catalogue.of({
        "cloud_mass": np.asarray(masses, dtype=float), "cloud_size": np.full(k, size), "cloud_density_pdf_width": np.full(k, 1.0),
        "cloud_alpha": np.zeros(k), "cloud_cluster_index": np.arange(k, dtype=float),
        "cloud_velocity_dispersion": np.asarray(sigmas, dtype=float),
    }, ((0, k),))
    return clusters, clouds, nb.materialise_nebular(clusters, clouds, constants)


def test_each_limit_and_the_cap_on_a_synthetic_census(constants):
    """Q = 1e48 /s in 30 pc clouds: four of 1e5 Msun (R_St 2.3 pc) at age 0 (the Stromgren sphere, 'expansion'),
    0.5 Myr (expanding), 1000 Myr at sigma 5 km/s (stagnated inside the cloud, R_STAG ~ 23 pc), 1000 Myr at
    sigma 0.5 km/s (capped at the cloud); one of 1e3 Msun too thin to hold its Stromgren sphere (R_St ~ 50 pc):
    leaking as before, its radius the cloud's, its density the clump's."""
    _, _, reg = _synthetic(constants, [0.0, 0.5, 1000.0, 1000.0, 0.0], [1e5, 1e5, 1e5, 1e5, 1e3], [5.0, 5.0, 5.0, 0.5, 5.0])
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
    # R_STAG < R_St would need sigma_v above ~18 km/s ((8/3)^(2/3) (c_i/c_0)^(4/3) < 1): no cloud of the census has it
    assert np.all(r >= rs)
    cloud = np.asarray(F["cloud_size"], dtype=float)[np.flatnonzero(np.asarray(F["cloud_cluster_index"]) >= 0)] * PC
    assert np.all(r <= cloud * (1.0 + 1e-12))


@pytest.fixture(scope="module")
def default():
    ms, _, _ = production()
    return run(ms.get(DEFAULT_MODEL))


def test_the_default_regions_under_the_law_disclosed(default):
    """DISCLOSED, as measured at S102 on the default grid (milky_way, the default galaxy); not judged (the S101 reader
    printed the model's numbers under this law first). Before (main 8db2cee): radius median / p99 / max 0.770 / 7.67 /
    25.7 pc (the Stromgren sphere), n_e median 153.7 cm^-3, log U median -2.831, 7 regions wider than 19.5 pc radius
    holding 6.0 % of the census's Halpha, no log U on the grid's -4 floor."""
    F = default.fields
    r = np.asarray(F["hii_radius"], dtype=float)
    L = np.asarray(F["hii_halpha_luminosity"], dtype=float)
    assert [float(np.median(r)), float(np.percentile(r, 99)), float(r.max())] == pytest.approx([11.900, 39.72, 70.57], rel=2e-3)
    assert float(np.median(np.asarray(F["hii_stromgren_radius"]))) == pytest.approx(0.770, abs=0.01)  # unchanged
    assert float(np.median(np.asarray(F["hii_electron_density"]))) == pytest.approx(2.305, rel=0.01)
    assert float(np.median(np.asarray(F["hii_ionization_parameter"]))) == pytest.approx(-3.457, abs=0.01)
    lim = np.asarray(F["hii_radius_limit"])
    # which limit binds, by count: expansion / stagnation / cloud; by Halpha 0.763 / 0.013 / 0.224
    assert [float((lim == k).mean()) for k in range(3)] == pytest.approx([0.3353, 0.1278, 0.5370], abs=2e-3)
    assert [float(L[lim == k].sum() / L.sum()) for k in range(3)] == pytest.approx([0.763, 0.013, 0.224], abs=5e-3)
    wide = r > 19.5  # half the frame's 39 pc pixel
    assert int(wide.sum()) == 1956 and float(L[wide].sum() / L.sum()) == pytest.approx(0.511, abs=2e-3)
    # low U now reads the grid's floor (clamped, as FSPS clamps; reported, not mended): 10.6 % of the regions, 0.02 % of the light
    floor = np.asarray(F["hii_ionization_parameter"]) <= -4.0
    assert float(floor.mean()) == pytest.approx(0.1064, abs=2e-3) and float(L[floor].sum() / L.sum()) < 1e-3
    # the bubbles' ambient density is the region's (bubbles.py): their median radius was 9.58 pc, 97.4 % stalled
    assert float(np.median(np.asarray(F["bubble_radius"]))) == pytest.approx(86.69, rel=5e-3)
    assert float(np.mean(np.asarray(F["bubble_stalled"]) == 1)) == pytest.approx(0.8119, abs=3e-3)
