"""S36 (BUILD_II Phase 10): mechanical feedback. Weaver et al. 1977's bubble and the Sedov-Taylor blast wave against
hand-computed points; the stall; the cluster columns as functions of their cluster and region; the remnant census's
per-region determinism and its redistribution of the rates (RENDER_PHYSICS §7); the star column; the routes."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages import bubbles as bb
from galaxy.stages import feedback as fb
from galaxy.stages import systems as sy
from galaxy.stages.dust import CM_PER_PC
from galaxy.stages.massive_stars import BOLTZMANN, SECONDS_PER_YEAR, SOLAR_LUMINOSITY
from galaxy.stages.nebular import PROTON_MASS, halpha_per_recombination
from galaxy.stages.systems import Catalogue

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
MYR = 1.0e6 * SECONDS_PER_YEAR
RHO_1 = 1.4 * PROTON_MASS  # g/cm³ of one hydrogen atom per cm³ (Kim & Ostriker 2015's 1.4 m_H)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {n: ms.get(n) for n in ms.names()}


@pytest.fixture(scope="module")
def constants(models):
    return {k: v.value for k, v in models["basic"].constants.items()}


@pytest.fixture(scope="module")
def default(models):
    return run(models["basic"])


@pytest.fixture(scope="module")
def coarse(models):
    return run(models["basic"], grid=COARSE)


def test_weaver_at_a_hand_computed_point():
    """L_w = 1e36 erg/s into n_0 = 1 cm^-3 for 1 Myr. By hand: (250/308pi)^(1/5) = 0.76287; (L/rho)^(1/5) with
    rho = 1.4 m_H = 2.3417e-24 g/cm3 is (4.2705e59)^(1/5) = 8.4352e11; t^(3/5) = (3.15576e13 s)^(3/5) = 1.2574e8;
    R = 0.76287 * 8.4352e11 * 1.2574e8 = 8.0911e19 cm = 26.22 pc. Weaver's eq. 51 reads 27 pc (their mu is not
    stated; the paper's 27 matches mu ~ 1.2), eq. 52 16 km/s against (3/5) R/t = 15.38."""
    a = (250.0 / (308.0 * math.pi)) ** 0.2
    assert a == pytest.approx(0.76287, abs=5e-6)
    assert fb.WEAVER_RADIUS == a
    by_hand = 0.76287 * (1.0e36 / 2.3417e-24) ** 0.2 * (3.15576e13) ** 0.6 / 3.0856775814913673e18
    r = fb.weaver_radius(np.array([1.0e36]), np.array([RHO_1]), np.array([MYR]))[0] / CM_PER_PC
    assert r == pytest.approx(by_hand, rel=1e-5)
    assert r == pytest.approx(26.22, abs=0.01)
    assert r == pytest.approx(27.0, rel=0.03)  # eq. 51, to its two figures and the unstated mu
    v = fb.weaver_velocity(np.array([r * CM_PER_PC]), np.array([MYR]))[0]
    assert v == pytest.approx(0.6 * r * CM_PER_PC / MYR / 1.0e5)
    assert v == pytest.approx(16.0, rel=0.04)  # eq. 52
    # eq. 22's coefficient is the interior energy (5/11) L t spread over (3/2) the volume: (5/11) / (2 pi a^3)
    assert fb.WEAVER_PRESSURE == pytest.approx(5.0 / 11.0 / (2.0 * math.pi * a**3), rel=1e-12)
    p = fb.weaver_pressure(np.array([1.0e36]), np.array([RHO_1]), np.array([MYR]))[0] * BOLTZMANN  # erg/cm3
    energy = 5.0 / 11.0 * 1.0e36 * MYR
    assert p == pytest.approx(energy / (1.5 * 4.0 / 3.0 * math.pi * (r * CM_PER_PC) ** 3), rel=1e-9)  # eq. 17
    # eq. 37 at L_36 = n_0 = t_6 = 1, the centre
    assert fb.weaver_temperature(np.array([1.0e36]), np.array([1.0]), np.array([1.0e6]))[0] == pytest.approx(2.07e6)


def test_the_stall_is_where_the_shell_slows_to_the_sound_speed():
    """R_stall = a^(5/2) (L/rho)^(1/2) (0.6/C)^(3/2): at the age the free solution reaches it, its velocity is C."""
    L, rho, c = np.array([1.0e36, 3.0e38]), np.array([RHO_1, 200.0 * RHO_1]), 10.0
    stall = fb.weaver_stall_radius(L, rho, c)
    t = 0.6 * stall / (c * 1.0e5)
    assert fb.weaver_radius(L, rho, t) == pytest.approx(stall, rel=1e-12)
    assert fb.weaver_velocity(stall, t) == pytest.approx([c, c], rel=1e-12)
    # at n_0 = 1 and 1e36 erg/s: 26.22 pc at 1 Myr and 15.4 km/s, so it stalls later, further out
    assert stall[0] / CM_PER_PC > 26.22 and t[0] > MYR


def test_sedov_taylor_and_the_snowplow_at_hand_computed_points(constants):
    """E = 1e51 erg into n_0 = 1 for 1000 yr: 1.15167 (1e51 (3.15576e10 s)^2 / 2.3417e-24)^(1/5) = 1.5384e19 cm
    = 4.986 pc, Kim & Ostriker 2015's eq. 3 (5.0 pc E51^(1/5) n0^(-1/5) t3^(2/5)) to 0.3%. At t_PDS = 1.33e4 yr the
    Sedov radius, 14.04 pc, meets Cioffi's r_PDS = 14.0; after it the snowplow grows as (4t/3t_PDS - 1/3)^(3/10)."""
    c = constants
    by_hand = 1.15167 * (1.0e51 * (3.15576e10) ** 2 / 2.3417e-24) ** 0.2 / 3.0856775814913673e18
    r = fb.sedov_radius(1.0e51, np.array([RHO_1]), np.array([1.0e3 * SECONDS_PER_YEAR]), float(c["SEDOV_XI"]))[0] / CM_PER_PC
    assert r == pytest.approx(by_hand, rel=1e-5)
    assert r == pytest.approx(4.986, abs=0.001)
    assert r == pytest.approx(5.0, rel=0.005)  # K&O eq. 3's two figures
    one = np.array([1.0])
    t_pds = fb.pds_time(1.0, one, one, float(c["PDS_TIME_COEFFICIENT"]))[0]
    assert t_pds == pytest.approx(1.33e4)
    assert fb.pds_radius(1.0, one, one, float(c["PDS_RADIUS_COEFFICIENT"]))[0] == pytest.approx(14.0)
    assert fb.pds_velocity(1.0, one, one, float(c["PDS_VELOCITY_COEFFICIENT"]))[0] == pytest.approx(413.0)
    at_pds = fb.sedov_radius(1.0e51, np.array([RHO_1]), np.array([t_pds * SECONDS_PER_YEAR]), float(c["SEDOV_XI"]))[0] / CM_PER_PC
    assert at_pds == pytest.approx(14.04, abs=0.01)
    assert at_pds == pytest.approx(14.0, rel=0.005)  # the phases join to half a percent
    assert fb.snowplow(np.array([t_pds]), np.array([t_pds]))[0] == pytest.approx(1.0)
    # blast_wave: continuous across t_PDS, and the phase flips there
    ages = np.array([0.999, 1.001]) * t_pds
    w = bb.blast_wave(ages, one.repeat(2), one.repeat(2), 1.0, c)
    assert list(w["remnant_phase"]) == [0, 1]
    assert w["remnant_size"][1] == pytest.approx(w["remnant_size"][0], rel=0.01)
    assert w["remnant_shell_density"][0] == pytest.approx(4.0)  # the adiabatic jump
    assert np.isnan(w["remnant_shell_emissivity"][0]) and w["remnant_shell_emissivity"][1] > 0.0


def test_a_clusters_bubble_is_a_function_of_its_cluster_and_region(default, constants):
    """Over its first 4 Myr a cluster's mean power is its own wind column; past that the supernovae join; stalled
    shells are at rest at the stall radius, expanding ones faster than the sound speed; the shell's Hα never uses
    more photons than the region traps."""
    F, c = default.fields, constants
    age = np.asarray(F["cluster_age"], dtype=float)
    power = np.asarray(F["bubble_mechanical_luminosity"], dtype=float)
    wind = np.asarray(F["cluster_wind_luminosity"], dtype=float)
    first = bb.first_supernova_age()
    assert first == pytest.approx(10.0**6.6 / 1.0e6)  # the youngest isochrone, 3.98 Myr
    young = age < first
    assert young.sum() == 2568
    assert power[young] == pytest.approx(wind[young], rel=1e-9)
    assert np.all(power[~young] > wind[~young])
    phase = np.asarray(F["bubble_phase"])
    assert np.array_equal(phase == 0, young) and not np.any(phase == 2)  # no cluster outlives its last core collapse
    n0 = np.asarray(F["hii_electron_density"], dtype=float)
    rho = float(c["HII_MASS_PER_HYDROGEN"]) * PROTON_MASS * n0
    L = power * SOLAR_LUMINOSITY
    free = fb.weaver_radius(L, rho, age * MYR) / CM_PER_PC
    stall = fb.weaver_stall_radius(L, rho, float(c["SHELL_SOUND_SPEED"])) / CM_PER_PC
    stalled = np.asarray(F["bubble_stalled"]) == 1
    radius = np.asarray(F["bubble_radius"], dtype=float)
    assert np.array_equal(stalled, free > stall)
    assert radius[stalled] == pytest.approx(stall[stalled], rel=1e-12)
    assert radius[~stalled] == pytest.approx(free[~stalled], rel=1e-12)
    v = np.asarray(F["bubble_shell_velocity"], dtype=float)
    assert np.all(v[stalled] == 0.0) and np.all(v[~stalled] >= 10.0 * (1 - 1e-12))
    # the photon limit: the shell's Hα at most the trapped photons' Case B Hα
    t_e = np.asarray(F["hii_temperature"], dtype=float)
    shell = fb.shell_volume(radius * CM_PER_PC, np.asarray(F["bubble_shell_thickness"]) * CM_PER_PC)
    l_shell = np.asarray(F["bubble_shell_emissivity"]) * shell
    trapped = (1.0 - float(c["HII_ESCAPE_FRACTION"])) * np.asarray(F["cluster_ionizing_photons"]) * halpha_per_recombination(t_e)
    assert np.all(l_shell <= trapped * (1.0 + 1e-9))
    # and the regions' Hα is the same photons: every shell that can hold them all emits the region's Hα
    region = np.asarray(F["hii_halpha_luminosity"], dtype=float) * SOLAR_LUMINOSITY
    full = l_shell >= trapped * (1.0 - 1e-9)
    assert full.mean() > 0.9
    assert l_shell[full] == pytest.approx(region[full], rel=1e-9)


def test_the_default_numbers(default):
    """Measured at S36 on the default grid; a pin that moves says why in its commit."""
    F = default.fields
    radius = np.asarray(F["bubble_radius"], dtype=float)
    assert radius.size == 12860
    assert float(np.median(radius)) == pytest.approx(8.963, rel=0.01)
    assert int(np.asarray(F["bubble_stalled"]).sum()) == 12521
    # a stalled bubble's interior sits at the region's thermal pressure, 2 n T: the stall rule, read from the
    # velocity, finds the pressure balance it stands for
    p_region = 2.0 * np.asarray(F["hii_electron_density"]) * np.asarray(F["hii_temperature"])
    stalled = np.asarray(F["bubble_stalled"]) == 1
    ratio = np.asarray(F["bubble_interior_pressure"])[stalled] / p_region[stalled]
    assert float(np.median(ratio)) == pytest.approx(1.0, abs=0.25)
    hosts = np.flatnonzero(np.asarray(F["cloud_cluster_index"]) >= 0)
    assert float(np.mean(radius > np.asarray(F["cloud_size"])[hosts])) == pytest.approx(0.205, abs=0.01)
    assert float(np.mean(radius > np.asarray(F["hii_stromgren_radius"]))) > 0.99
    assert np.asarray(F["remnant_size"]).size == 1464
    assert float(F["remnant_count_total"]) == pytest.approx(1448.41, rel=1e-4)
    kind = np.asarray(F["remnant_kind"])
    assert (int((kind == 0).sum()), int((kind == 1).sum())) == (1071, 393)
    R = default.grid.R
    i = int(np.argmin(abs(R - 8.2)))
    assert float(F["hot_phase_porosity"][i]) == pytest.approx(0.0334, abs=0.001)
    n_mid = float(F["gas_midplane_density"][i]) * fb.MSUN_PER_PC3_IN_G_PER_CM3 / RHO_1
    assert n_mid == pytest.approx(0.688, abs=0.002)


def test_the_midplane_density_is_the_pressure_over_the_dispersion_squared(default, constants):
    F = default.fields
    rho = np.asarray(F["gas_midplane_pressure"]) * BOLTZMANN / (float(constants["H2_GAS_DISPERSION"]) * 1.0e5) ** 2
    assert np.asarray(F["gas_midplane_density"]) * fb.MSUN_PER_PC3_IN_G_PER_CM3 == pytest.approx(rho, rel=1e-12)


def test_the_remnant_census_redistributes_the_rates(default, constants):
    """RENDER_PHYSICS §7: the census integrates back to (core collapse + Ia rate) x lifetime x area, the kinds to
    their rates' shares, within Poisson noise; the ring integrals lose only the trapezoid's edge intervals."""
    F, c, R = default.fields, constants, default.grid.R
    rate = np.asarray(F["core_collapse_rate"]) + np.asarray(F["type_ia_rate"])
    lifetime = float(c["REMNANT_VISIBLE_LIFETIME"])
    whole = float(np.trapezoid(rate * lifetime * 2.0 * math.pi * R, R))
    assert whole == pytest.approx((float(F["core_collapse_rate_total"]) + float(F["type_ia_rate_total"])) * lifetime, rel=1e-9)
    expected = float(F["remnant_count_total"])
    assert expected == pytest.approx(whole, rel=0.02)
    n = np.asarray(F["remnant_size"]).size
    assert abs(n - expected) < 3.0 * math.sqrt(expected)
    cc_share = float(F["core_collapse_rate_total"]) / (float(F["core_collapse_rate_total"]) + float(F["type_ia_rate_total"]))
    cc = int((np.asarray(F["remnant_kind"]) == 0).sum())
    assert abs(cc - cc_share * n) < 3.0 * math.sqrt(n * cc_share * (1 - cc_share))
    # ages uniform over the lifetime, the phase Sedov exactly before t_PDS
    age = np.asarray(F["remnant_age"])
    assert 0.0 <= age.min() and age.max() <= lifetime
    assert abs(float(np.mean(age)) / lifetime - 0.5) < 3.0 / math.sqrt(12.0 * n)
    n0 = np.asarray(F["remnant_ambient_density"])
    t_pds = fb.pds_time(float(c["SUPERNOVA_ENERGY_51"]), n0, 10.0 ** np.interp(F["remnant_radius"], R, F["feh_gas"]),
                        float(c["PDS_TIME_COEFFICIENT"]))
    assert np.array_equal(np.asarray(F["remnant_phase"]) == 1, age >= t_pds)
    # the radiative shells' Halpha is one recombination per swept atom, never above the ionized shell's
    rad = np.asarray(F["remnant_phase"]) == 1
    assert np.all(np.isnan(np.asarray(F["remnant_shell_emissivity"])[~rad]))
    assert np.all(np.asarray(F["remnant_shell_emissivity"])[rad] > 0.0)


def test_the_remnant_census_is_per_region_deterministic(coarse, constants, models):
    """D60: a cell drawn alone is the sweep's slice; a set of cells is the cells in any order; both models draw the
    same remnants (the rates do not see the azimuthal modulation)."""
    F, R, c = coarse.fields, coarse.grid.R, constants
    seed = int(coarse.inputs["systems_seed"])
    whole = bb.materialise_remnants(F, R, seed, c)
    runs = dict(whole.counts)
    offsets = {}
    o = 0
    for cell, count in whole.counts:
        offsets[cell] = o
        o += count
    picked = [cell for cell, _ in whole.counts][::97][:8]
    alone = bb.materialise_remnants(F, R, seed, c, picked[::-1])
    for cell in picked:
        one = bb.materialise_remnants(F, R, seed, c, (cell,))
        for name in (*bb.REMNANT_COLUMNS, "remnant_phase", "remnant_kind"):
            got = np.asarray(one[name])
            want = np.asarray(whole[name])[offsets[cell]:offsets[cell] + runs[cell]]
            assert np.array_equal(got, want, equal_nan=True), (cell, name)
    assert dict(alone.counts) == {cell: runs[cell] for cell in picked}
    other = run(models["azimuthal"], grid=COARSE).fields
    for name in (*bb.REMNANT_COLUMNS, *bb.BUBBLE_COLUMNS, "remnant_phase", "remnant_kind", "bubble_phase", "bubble_stalled"):
        assert np.array_equal(np.asarray(F[name]), np.asarray(other[name]), equal_nan=True), name


def test_the_star_column_and_the_catalogues_other_columns(coarse):
    """star_bubble_radius is eq. 21 at the star's own wind and age in the midplane density at its radius, NaN
    where the wind is; a region's star has the sweep's value, at every level of the hierarchy."""
    F, R, t = coarse.fields, coarse.grid.R, coarse.grid.t
    cat = sy.materialise(F, R, t, 3, 200_000, migration=float(coarse.inputs["migration_efficiency"]))
    wind = np.asarray(cat["star_wind_luminosity"], dtype=float)
    got = np.asarray(cat["star_bubble_radius"], dtype=float)
    assert np.array_equal(np.isnan(got), np.isnan(wind))
    ok = np.isfinite(wind)
    assert ok.sum() > 0
    rho = np.interp(cat["star_radius"][ok], R, F["gas_midplane_density"]) * fb.MSUN_PER_PC3_IN_G_PER_CM3
    want = fb.weaver_radius(wind[ok] * SOLAR_LUMINOSITY, rho, cat["star_age"][ok] * 1.0e9 * SECONDS_PER_YEAR) / CM_PER_PC
    assert got[ok] == pytest.approx(want, rel=1e-12)
    cell = int(cat.counts[len(cat.counts) // 2][0])
    kids = [sy.child_id(cell, 1, q) for q in range(4)]
    parent = sy.materialise(F, R, t, 3, 200_000, cells=[cell], migration=float(coarse.inputs["migration_efficiency"]))
    child = sy.materialise(F, R, t, 3, 200_000, cells=kids, migration=float(coarse.inputs["migration_efficiency"]), level=1)
    inherited = np.asarray(child["level"]) == 0
    idx = np.asarray(child["index"])[inherited]
    assert np.array_equal(np.asarray(child["star_bubble_radius"])[inherited], np.asarray(parent["star_bubble_radius"])[idx], equal_nan=True)


def test_the_hot_phase_is_the_volumes_over_the_layer(default):
    F, R = default.fields, default.grid.R
    edges, _ = sy.cell_edges(R)
    q = np.asarray(F["hot_phase_porosity"], dtype=float)
    ring = 10
    inside = (R >= edges[ring]) & (R <= edges[ring + 1])
    sigma, rho = np.asarray(F["gas_surface_density"]), np.asarray(F["gas_midplane_density"])
    layer = float(np.trapezoid(np.where(inside, sigma / rho * 2.0 * math.pi * R, 0.0), R)) * 1.0e6  # pc3
    vol = 0.0
    for where, size in ((F["cluster_radius"], F["bubble_radius"]), (F["remnant_radius"], F["remnant_size"])):
        where, size = np.asarray(where), np.asarray(size)
        sel = (where >= edges[ring]) & (where < edges[ring + 1])
        vol += float(np.sum(4.0 / 3.0 * math.pi * size[sel] ** 3))
    at = int(np.flatnonzero((R >= edges[ring]) & (R < edges[ring + 1]))[0])
    assert q[at] == pytest.approx(vol / layer, rel=1e-9)
    assert np.all(q[np.isfinite(q)] >= 0.0)


def test_the_routes():
    """/api/remnants is the stage's census by window and level, and runs nothing that makes clusters or stars (D4);
    /api/clusters carries the bubble columns, equal to the stage's."""
    svc = Service()
    r0 = svc.handle("/api/remnants", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    assert r0.status == 200
    h0, a0 = wire.decode(r0.body)
    assert not set(h0["stages"]) & {"systems", "clouds", "clusters", "nebular", "bubbles"}
    assert h0["remnants"]["materialised"] == a0["remnant_size"].size > 0
    assert h0["scalars"]["remnant_count_total"] == pytest.approx(1448.41, rel=1e-4)
    for name in (*bb.REMNANT_COLUMNS, "remnant_phase", "remnant_kind"):
        assert name in h0["columns"], name
    whole, arrays = wire.decode(svc.handle("/api/arrays", "fields=remnant_radius,remnant_azimuth,remnant_size").body)
    got = set(zip(a0["remnant_radius"].tolist(), a0["remnant_size"].tolist()))
    rings, sectors = sy.cell_edges(svc.grid.R)
    want = set()
    for rr, phi, s in zip(arrays["remnant_radius"], arrays["remnant_azimuth"], arrays["remnant_size"]):
        ring = min(int(np.searchsorted(rings, rr, side="right") - 1), sy.CELL_RINGS - 1)
        sector = min(int(phi // (2.0 * math.pi / sy.CELL_SECTORS)), sy.CELL_SECTORS - 1)
        if ring * sy.CELL_SECTORS + sector in set(h0["cells"]["ids"]):
            want.add((float(rr), float(s)))
    assert got == want
    r2 = svc.handle("/api/remnants", "r_min=7&r_max=9&phi_min=0&phi_max=0.4&level=2")
    h2, a2 = wire.decode(r2.body)
    assert a2["remnant_size"].size == h2["remnants"]["materialised"] <= a0["remnant_size"].size
    assert svc.handle("/api/remnants", "level=4").status == 400
    rc = svc.handle("/api/clusters", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    hc, ac = wire.decode(rc.body)
    for name in (*bb.BUBBLE_COLUMNS, "bubble_phase", "bubble_stalled"):
        assert name in hc["columns"] and ac[name].shape == ac["cluster_mass"].shape, name
    assert not any(n.startswith("remnant_") for n in hc["columns"])
    full, fa = wire.decode(svc.handle("/api/arrays", "fields=cluster_mass,bubble_radius").body)
    lookup = dict(zip(fa["cluster_mass"].tolist(), fa["bubble_radius"].tolist()))
    assert all(lookup[m] == b for m, b in zip(ac["cluster_mass"].tolist(), ac["bubble_radius"].tolist()))
