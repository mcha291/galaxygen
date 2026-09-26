"""The young star-cluster census (S33, BUILD_II Phase 11): an object class beside stars and clouds.

Every number a ruling rests on was read from its source at S33 and entered in level0 with the sentence
quoted; the tests here check the arithmetic the census is built from, that each cluster is the cluster
of one cloud in the same cell (the cloud's ``cloud_cluster_index``), per-region determinism (D60), that
both models draw the same clusters, the sums over the IMF against the light stage's integral, and the
Phase 5 hook. Pinned as measurements, never as targets (rule B5).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages import clouds as cl
from galaxy.stages import clusters as cu
from galaxy.stages import photometry as ph

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {m.name: m for m in ms}


@pytest.fixture(scope="module")
def default(models):
    o = run(models["basic"])
    return o, {k: v.value for k, v in models["basic"].constants.items()}


@pytest.fixture(scope="module")
def coarse(models):
    o = run(models["basic"], grid=COARSE)
    return o, {k: v.value for k, v in models["basic"].constants.items()}


def _hosts(fields) -> np.ndarray:
    return np.asarray(fields["cloud_cluster_index"]) >= 0.0


def test_the_sourced_constants_and_their_arithmetic(coarse):
    """Lada & Lada 2003's 7% and 10 Myr, Portegies Zwart et al. 2010's 10^3 Msun/pc^3; the efficiency derived."""
    o, c = coarse
    assert "CLUSTER_FORMATION_EFFICIENCY" not in c  # derived since the first pass's ruling, not adopted
    assert c["CLUSTER_BOUND_FRACTION"] == 0.07
    assert c["CLUSTER_DISSOLUTION_AGE"] == 10.0
    assert c["CLUSTER_HALF_MASS_DENSITY"] == 1.0e3
    # eps = Sigma_SFR tau / Sigma_H2, capped at 1: 1 Msun/yr/kpc^2 (1e-6 per pc^2) for 26 Myr over 26 Msun/pc^2 is 1.
    R = np.array([1.0, 2.0])
    assert cu.cloud_lifetime(c) == 26.0
    eps = cu.efficiency(np.array([1.5, 1.5, 1.5]), np.array([1.0, 1.0]), np.array([26.0, 26.0]), R, 26.0)
    assert np.allclose(eps, 1.0)
    assert cu.efficiency(np.array([1.5]), np.array([0.1, 0.1]), np.array([26.0, 26.0]), R, 26.0)[0] == pytest.approx(0.1)
    assert cu.efficiency(np.array([1.5]), np.array([5.0, 5.0]), np.array([26.0, 26.0]), R, 26.0)[0] == 1.0  # the cap
    assert cu.efficiency(np.array([1.5]), np.array([5.0, 5.0]), np.array([0.0, 0.0]), R, 26.0)[0] == 0.0  # no gas
    # The published scalar is the molecular-mass-weighted efficiency, a population integral.
    F, RR = o.fields, o.grid.R
    assert o.fields["cluster_formation_efficiency"] == pytest.approx(
        cu.mean_efficiency(F["sfr_surface_density"], F["gas_molecular_surface_density"], RR, 26.0))
    # rho_hm = 3M/(8 pi r_hm^3): a cluster of 8 pi/3 x 10^3 Msun at 10^3 Msun/pc^3 has r_hm = 1 pc.
    assert cu.half_mass_radius(np.array([8.0 * math.pi / 3.0 * 1.0e3]), 1.0e3)[0] == pytest.approx(1.0)
    # The offset is exact in the plane: 100 pc outward from 8 kpc is 8.1 kpc at the same azimuth, and
    # 100 pc toward increasing azimuth leaves the radius at sqrt(8^2 + 0.1^2).
    r, phi = cu.offset_position(np.array([8.0, 8.0]), np.array([1.0, 1.0]), np.array([100.0, 100.0]), np.array([0.0, math.pi / 2]))
    assert r[0] == pytest.approx(8.1) and phi[0] == pytest.approx(1.0)
    assert r[1] == pytest.approx(math.hypot(8.0, 0.1)) and phi[1] == pytest.approx(1.0 + math.atan2(0.1, 8.0))


def test_one_cluster_per_cloud_past_its_embedded_phase_in_the_same_cell(coarse):
    """Ruling (d): a blown-open or dispersing cloud holds one cluster, which its cloud_cluster_index names
    within the cloud's own cell; the cluster sits at the cloud's source, one embedded phase younger."""
    o, c = coarse
    F, R = o.fields, o.grid.R
    seed = int(o.inputs["systems_seed"])
    clouds = cu.census_of_clouds(F, R, seed, c)
    clusters = cu.materialise_clusters(clouds, F, R, seed, c)
    # The stage publishes exactly what materialise gives from the published clouds.
    for name in (*cu.CLUSTER_COLUMNS, "cluster_bound"):
        assert np.array_equal(clusters[name], F[name]), name
    state = np.asarray(F["cloud_state"])
    index = np.asarray(F["cloud_cluster_index"])
    assert np.array_equal(index >= 0.0, state >= cl.CLOUD_STATES.index("blown_open"))
    assert tuple(cl.CLUSTER_HOSTING_STATES) == ("blown_open", "dispersing")
    # Every index resolves to a cluster of the same cell, and every cluster is named by exactly one cloud.
    per_cell = dict(clusters.counts)
    offset, row = 0, 0
    eps_all = cu.efficiency(np.asarray(F["cloud_radius"]), F["sfr_surface_density"], F["gas_molecular_surface_density"], R, 26.0)
    assert 0.0 < eps_all[_hosts(F)].min() and eps_all.max() < 1.0  # no cloud reaches the cap at S33
    for cell, count in clouds.counts:
        idx = index[offset:offset + count]
        named = idx[idx >= 0.0].astype(int)
        assert np.array_equal(named, np.arange(per_cell.get(cell, 0))), cell
        hosts = offset + np.flatnonzero(idx >= 0.0)
        k = named.size
        if k:
            got = slice(row, row + k)
            assert np.allclose(F["cluster_mass"][got], eps_all[hosts] * F["cloud_mass"][hosts])
            assert np.allclose(F["cluster_age"][got], F["cloud_age"][hosts] - c["GMC_PHASE_EMBEDDED"])
            assert np.array_equal(F["cluster_height"][got], F["cloud_height"][hosts])
            assert np.array_equal(F["cluster_metallicity"][got], F["cloud_metallicity"][hosts])
            # Inside its cloud: no farther from the cloud's centre than the cloud's radius.
            x0 = F["cloud_radius"][hosts] * np.cos(F["cloud_azimuth"][hosts])
            y0 = F["cloud_radius"][hosts] * np.sin(F["cloud_azimuth"][hosts])
            x1 = F["cluster_radius"][got] * np.cos(F["cluster_azimuth"][got])
            y1 = F["cluster_radius"][got] * np.sin(F["cluster_azimuth"][got])
            assert np.allclose(np.hypot(x1 - x0, y1 - y0) * 1000.0, F["cloud_source_offset"][hosts])
            assert np.all(np.hypot(x1 - x0, y1 - y0) * 1000.0 <= F["cloud_size"][hosts] + 1e-9)
        offset += count
        row += k
    assert row == len(F["cluster_mass"]) and offset == len(F["cloud_mass"])
    ages = np.asarray(F["cluster_age"])
    assert ages.min() >= 0.0 and ages.max() <= c["GMC_PHASE_BLOWN_OPEN"] + c["GMC_PHASE_DISPERSING"]
    assert np.allclose(F["cluster_half_mass_radius"], cu.half_mass_radius(F["cluster_mass"], c["CLUSTER_HALF_MASS_DENSITY"]))


def test_bound_unbound_dissolved(coarse):
    """Ruling (b): bound at Lada & Lada's 7%, by number and whatever the mass; the unbound dissolved past 10 Myr."""
    o, c = coarse
    F = o.fields
    bound, age = np.asarray(F["cluster_bound"]), np.asarray(F["cluster_age"])
    assert tuple(cu.CLUSTER_BOUND_STATES) == ("bound", "unbound", "dissolved")
    n = bound.size
    share = float(np.mean(bound == 0))
    assert abs(share - 0.07) < 5.0 * math.sqrt(0.07 * 0.93 / n), (share, n)
    unbound = bound != 0
    assert np.all((bound[unbound] == 2) == (age[unbound] >= c["CLUSTER_DISSOLUTION_AGE"]))


def test_per_region_determinism_and_both_models_agree(models, coarse):
    """D60 for clusters: cells drawn alone are the sweep's cells; the azimuthal model draws the same census;
    a new systems seed rerolls clusters with clouds, and the cloud columns never move with the cluster stream."""
    o, c = coarse
    F, R = o.fields, o.grid.R
    sweep = cu.materialise_clusters(cl.materialise_clouds(F, R, 0, c), F, R, 0, c)
    cells = [300, 301, 517, 640]
    part = cu.materialise_clusters(cl.materialise_clouds(F, R, 0, c, cells=cells), F, R, 0, c)
    assert [cell for cell, _ in part.counts] == [cell for cell in cells if cell in dict(sweep.counts)]
    off_part = 0
    for cell, count in part.counts:
        off = sum(k for cc, k in sweep.counts if cc < cell)
        for name in (*cu.CLUSTER_COLUMNS, "cluster_bound"):
            assert np.array_equal(part[name][off_part:off_part + count], sweep[name][off:off + count]), (cell, name)
        off_part += count
    assert off_part == part.size > 0
    a = run(models["azimuthal"], grid=COARSE).fields
    for name in (*cu.CLUSTER_COLUMNS, "cluster_bound", "cloud_cluster_index"):
        assert np.array_equal(a[name], F[name]), name
    assert a["bound_cluster_mass_total"] == F["bound_cluster_mass_total"]
    other = run(models["basic"], {"systems_seed": 3}, grid=COARSE).fields
    assert not np.array_equal(other["cluster_mass"], F["cluster_mass"])
    assert other["bound_cluster_mass_total"] == F["bound_cluster_mass_total"]  # a population integral


def test_the_sums_over_the_imf_are_the_light_stages_integral(default):
    """The gate's Q check, a closure since the efficiency is derived. The machinery: Q per unit mass formed of
    a burst, averaged over 0-20 Myr, is the light stage's integral over the same ages. The census: its total
    Q against the light stage's Q from stars younger than the oldest cluster, within three times the noise
    the census itself carries - its ages (a burst's Q is steep in age) and its masses (Poisson in clouds)."""
    o, c = default
    F, R = o.fields, o.grid.R
    span = c["GMC_PHASE_BLOWN_OPEN"] + c["GMC_PHASE_DISPERSING"]  # Myr: the oldest a cluster is
    ages = np.linspace(0.0, span, 20001)
    for feh in (-1.0, 0.0, 0.3):
        q, _ = cu.per_mass(ages, np.full(ages.size, feh))
        mean = float(np.trapezoid(q, ages) / span)
        light = float(ph.population_over(np.zeros(1), np.array([span / 1000.0]), np.array([[feh]]))["ionizing"][0, 0])
        assert mean == pytest.approx(light, rel=2e-3), feh
    # The same [Fe/H] on both sides: the clusters read their cloud's, the gas's at its radius, which is the
    # present step of the history the light stage reads.
    assert np.array_equal(F["feh_gas"], np.asarray(F["feh_history"])[:, -1])
    mass, feh, Q = (np.asarray(F[n]) for n in ("cluster_mass", "cluster_metallicity", "cluster_ionizing_photons"))
    qbar = ph.population_over(np.zeros(1), np.array([span / 1000.0]), feh[:, None])["ionizing"][:, 0]
    expected = float((mass * qbar).sum())
    q_solar, _ = cu.per_mass(ages, np.zeros(ages.size))
    age_noise = math.sqrt(float((mass**2).sum())) * float(np.std(q_solar)) / expected  # 0.043 at S33
    mass_noise = math.sqrt(float((mass**2).sum())) / float(mass.sum())  # 1/sqrt(N_eff), N_eff 898: 0.033
    assert abs(Q.sum() / expected - 1.0) < 3.0 * age_noise, (Q.sum() / expected, age_noise)
    sfr = np.asarray(F["sfr_surface_density"])
    feh_now = np.asarray(F["feh_history"])[:, -1]
    younger = ph.population_over(np.zeros(1), np.array([span / 1000.0]), feh_now[:, None])["ionizing"][:, 0] * span * 1e6
    light_young = float(np.trapezoid(sfr * younger * 2.0 * math.pi * R, R))
    assert light_young == pytest.approx(0.980 * F["ionizing_photon_rate_total"], rel=0.002)  # 98% of it is under 20 Myr
    ratio = Q.sum() / light_young
    tolerance = 3.0 * math.hypot(age_noise, mass_noise)  # 0.16 at S33
    assert abs(ratio - 1.0) < tolerance, (ratio, tolerance)
    # Measured at S33: 1.0088 - the clouds' mass 1.037 of the molecular gas (S32's Poisson excess), the
    # clusters' formation rate 1.029 of the SFR, 1.022 once each cluster's own [Fe/H] is read, and the
    # draw of the ages 0.987 of that: every factor inside its noise, none unexplained.
    assert ratio == pytest.approx(1.0088, abs=0.0005)
    sfr_total = float(np.trapezoid(sfr * 2.0 * math.pi * R, R))
    assert mass.sum() / (span * 1e6) / sfr_total == pytest.approx(1.029, abs=0.001)
    assert expected / light_young == pytest.approx(1.022, abs=0.001)
    # The efficiency the census used, against the sources it was chosen against (its about line).
    assert F["cluster_formation_efficiency"] == pytest.approx(0.02058, abs=0.0001)
    assert 0.005 < F["cluster_formation_efficiency"] < 0.08
    # The wind: positive, finite, the O and B stars' - a 1 Myr burst blows harder than a 19 Myr one.
    _, w = cu.per_mass(np.array([1.0, 19.0]), np.zeros(2))
    assert w[0] > w[1] >= 0.0
    W = np.asarray(F["cluster_wind_luminosity"])
    assert np.all(np.isfinite(W)) and np.all(W >= 0.0) and W.sum() == pytest.approx(5.466e6, rel=0.01)


def test_the_census_on_the_default_grid(default):
    """The numbers the report quotes, pinned as measured at S33 (rule B5)."""
    o, c = default
    F = o.fields
    mass = np.asarray(F["cluster_mass"])
    assert mass.size == 12860 == int(_hosts(F).sum())
    assert mass.min() == pytest.approx(9.289, rel=1e-3) and mass.max() == pytest.approx(2.652e5, rel=1e-3)
    assert np.median(mass) == pytest.approx(763.06, rel=1e-3) and mass.sum() == pytest.approx(3.613e7, rel=1e-3)
    bound = np.asarray(F["cluster_bound"])
    assert np.bincount(bound, minlength=3).tolist() == [901, 5951, 6008]
    # Portegies Zwart et al.'s Schechter mass for Milky Way-type spirals, 2e5: 4 clusters are above it,
    # holding 2.7% of the mass.
    assert int((mass > 2.0e5).sum()) == 4
    assert np.median(F["cluster_half_mass_radius"]) == pytest.approx(0.450, abs=0.002)


def test_the_phase_5_hook(default):
    """bound_cluster_mass_total: the whole history's locked stars times the bound fraction - every star formed in a
    cluster, as the derived efficiency makes them, so the efficiency does not enter it. At S33 it is 72 times
    Boylan-Kolchin 2018's eta M_halo, (3-4) x 10^-5 of 1.1e12 Msun: what S34's dissolution has to remove."""
    o, c = default
    F, R = o.fields, o.grid.R
    locked = float(np.trapezoid(np.asarray(F["stars_formed_history"]).sum(axis=1) * 1.0e6 * 2.0 * math.pi * R, R))
    assert F["bound_cluster_mass_total"] == pytest.approx(c["CLUSTER_BOUND_FRACTION"] * locked, rel=1e-12)
    assert F["bound_cluster_mass_total"] == pytest.approx(2.786e9, rel=1e-3)
    assert F["bound_cluster_mass_total"] / (3.5e-5 * F["halo_virial_mass"]) == pytest.approx(72.4, abs=0.1)


def test_the_clusters_route_is_the_stages_census_by_window_and_level():
    svc = Service()
    r0 = svc.handle("/api/clusters", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    r2 = svc.handle("/api/clusters", "r_min=7&r_max=9&phi_min=0&phi_max=0.4&level=2")
    assert r0.status == 200 and r2.status == 200
    h0, a0 = wire.decode(r0.body)
    h2, a2 = wire.decode(r2.body)
    # Neither the clusters stage nor the clouds stage runs for a window (D4): the cells are drawn here.
    assert "clusters" not in h0["stages"] and "clouds" not in h0["stages"]
    assert h0["clusters"]["materialised"] == len(a0["cluster_mass"]) > 0
    assert "cluster_bound" in h0["columns"] and "cluster_ionizing_photons" in h0["columns"]
    # The same rows the stage publishes for those cells, cell by cell.
    whole, _ = wire.decode(svc.handle("/api/arrays", "fields=cluster_mass,bound_cluster_mass_total,cluster_formation_efficiency").body)
    frame = wire.decode(svc.handle("/api/arrays", "fields=cluster_mass,cloud_cluster_index").body)[1]
    clouds = wire.decode(svc.handle("/api/clouds", "r_min=7&r_max=9&phi_min=0&phi_max=0.4").body)
    hosts = [(cell, int((clouds[1]["cloud_cluster_index"][o:o + n] >= 0).sum()))
             for cell, n, o in zip(clouds[0]["cells"]["ids"], clouds[0]["cells"]["counts"],
                                   np.cumsum([0] + clouds[0]["cells"]["counts"][:-1]))]
    assert [(c_, n) for c_, n in hosts if n] == list(zip(h0["cells"]["ids"], h0["cells"]["counts"]))
    assert set(np.round(a0["cluster_mass"], 6).tolist()) <= set(np.round(frame["cluster_mass"], 6).tolist())
    # The header carries the stage's scalar, the number /api/arrays serves.
    assert set(h0["scalars"]) == {"bound_cluster_mass_total", "cluster_formation_efficiency"}
    for name in h0["scalars"]:
        assert h0["scalars"][name] == pytest.approx(whole["scalars"][name])
    # A level filters, by the cluster's own position.
    assert h2["level"] == 2 and 0 < len(a2["cluster_mass"]) < len(a0["cluster_mass"])
    assert set(np.round(a2["cluster_mass"], 6).tolist()) <= set(np.round(a0["cluster_mass"], 6).tolist())
    again = svc.handle("/api/clusters", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    ha, aa = wire.decode(again.body)
    assert {k: v for k, v in ha.items() if k != "stages"} == {k: v for k, v in h0.items() if k != "stages"}
    assert all(np.array_equal(aa[k], a0[k], equal_nan=True) for k in a0)
    assert svc.handle("/api/clusters", "level=4").status == 400
    fields = svc.handle("/api/fields", "").json()["fields"]
    for f in fields:
        if f["name"] in ("bound_cluster_mass_total", "cluster_formation_efficiency"):
            assert "Not shown by the viewer" in f["about"] and "rule D4" in f["about"]
