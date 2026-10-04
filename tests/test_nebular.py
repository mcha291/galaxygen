"""S35 (BUILD_II Phase 9): the HII regions, the diffuse ionized gas and the galaxy's Hα as its ionizing photons
redistributed. Case B against the rows read from Storey & Hummer 1995; the Strömgren sphere against its
defining balance; the census against the field (RENDER_PHYSICS §7); determinism; the clusters route."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import nebular as nb
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.massive_stars import SOLAR_LUMINOSITY
from galaxy.stages.systems import Catalogue

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {n: ms.get(n) for n in ms.names()}


@pytest.fixture(scope="module")
def default(models):
    return run(models[DEFAULT_MODEL])


@pytest.fixture(scope="module")
def default_layer_off(models):
    """The default run with the randomness layer off: what the acceptance rows read since S55 (D214, invariant I3)."""
    return run(models[DEFAULT_MODEL], layer=False)


@pytest.fixture(scope="module")
def coarse(models):
    return run(models[DEFAULT_MODEL], grid=COARSE)


def test_case_b_reproduces_the_rows_read_from_storey_and_hummer():
    """The table is the source's rows (CDS VI/64, n_e = 1e2); the interpolation returns them exactly and gives
    Hα/Hβ = 2.863 at 1e4 K, 0.452 Hα photons per recombination (Kennicutt 1998 eq. 2: 1.08e-53 / 7.9e-42 =
    1.367e-12 erg per photon, to 0.2%)."""
    t = np.array([5000.0, 10000.0, 20000.0])
    assert nb.case_b_hbeta(t) == pytest.approx([2.199e-25, 1.235e-25, 6.579e-26])
    assert nb.case_b_halpha(t) == pytest.approx([6.687e-25, 3.536e-25, 1.807e-25])
    assert nb.alpha_b(t) == pytest.approx([4.522e-13, 2.585e-13, 1.428e-13])
    ratio = nb.case_b_halpha(t) / nb.case_b_hbeta(t)
    assert ratio == pytest.approx([3.041, 2.863, 2.747], abs=0.001)
    per_photon = nb.halpha_per_recombination(np.array([1.0e4]))[0]
    assert per_photon == pytest.approx(1.368e-12, rel=1e-3)
    assert per_photon == pytest.approx(1.08e-53 / 7.9e-42, rel=2.5e-3)  # Kennicutt 1998 eq. 2
    h_nu_halpha = 1.98645e-8 / 6564.7229  # erg, h c over the vacuum wavelength FSPS lists
    assert per_photon / h_nu_halpha == pytest.approx(0.452, abs=0.001)
    # monotone in T between the rows, clamped outside them
    fine = np.logspace(math.log10(3000.0), math.log10(30000.0), 200)
    assert np.all(np.diff(nb.case_b_halpha(fine)) < 0)
    assert nb.case_b_halpha(np.array([1000.0]))[0] == nb.case_b_halpha(np.array([3000.0]))[0]


def test_temperature_and_abundances_are_the_sources_relations():
    """T_e from 12+log(O/H) by the DESIRED eq. 5, clamped to 6000-20000 K; N/O by Nicholls eq. 3 (solar log N/O is
    -0.86, the relation gives -0.97 at the Galactic Concordance 8.76 and -1.0 at 8.69); S an alpha element."""
    ms, _, _ = production()
    c = {k: v.value for k, v in ms.get(DEFAULT_MODEL).constants.items()}
    assert nb.electron_temperature(np.array([8.69]), c)[0] == pytest.approx((9.29 - 8.69) / 0.96 * 1.0e4)  # 6250 K
    assert nb.electron_temperature(np.array([9.0, 7.0]), c) == pytest.approx([6000.0, 20000.0])
    o, n, s_ = nb.abundances(np.array([0.0, 0.07]), np.array([0.0, 0.0]), c)
    assert o == pytest.approx([8.69, 8.76])
    assert (n - o)[1] == pytest.approx(math.log10(10.0**-1.732 + 10.0 ** (8.76 - 12.0 + 2.19)), abs=1e-9)
    assert (n - o)[1] == pytest.approx(-0.97, abs=0.01)
    assert s_ == pytest.approx([7.12, 7.19])
    # metal-poor gas sits on the primary floor
    o2, n2, _ = nb.abundances(np.array([-2.5]), np.array([0.3]), c)
    assert (n2 - o2)[0] == pytest.approx(-1.732, abs=0.02)


def test_the_stromgren_sphere_is_its_own_balance_and_the_clumping_is_the_log_normals_second_moment():
    """Q = alpha_B <n^2> (4/3) pi R^3 inverted; <n^2>/<n>^2 = e^(sigma_s^2)."""
    q = np.array([1.0e49])
    n2 = np.array([1.0e4])
    alpha = np.array([2.585e-13])
    r = nb.stromgren_radius_cm(q, n2, alpha)
    assert alpha * n2 * 4.0 / 3.0 * math.pi * r**3 == pytest.approx(q)
    assert 1.0 < r[0] / nb.CM_PER_PC < 10.0  # a few parsecs for 1e49 photons/s in n = 100 gas (3.16 pc here)
    # the census's mean density of a uniform sphere: 1e5 Msun in 10 pc -> ~1e3 cm^-3 with 1.4 m_H per H
    n_mean = nb.mean_hydrogen_density(np.array([1.0e5]), np.array([10.0]), 1.4)[0]
    assert n_mean == pytest.approx(1.0e5 * nb.SOLAR_MASS_G / (1.4 * nb.PROTON_MASS) / (4 / 3 * math.pi * (10 * nb.CM_PER_PC) ** 3))
    assert 500.0 < n_mean < 1200.0


def test_the_luminosity_function_slope_recovers_a_known_power_law():
    rng = np.random.default_rng(3)
    # dN/dL ∝ L^-2 between 1e37 and 1e40: inverse-CDF sample
    u = rng.random(200_000)
    lo, hi = 1.0e37, 1.0e40
    l = 1.0 / (1.0 / lo - u * (1.0 / lo - 1.0 / hi))
    assert nb.luminosity_function_slope(l, 1.0e37) == pytest.approx(-2.0, abs=0.05)
    assert math.isnan(nb.luminosity_function_slope(np.array([1.0e38, 2.0e38]), 1.0e37))


def _catalogues(fields) -> tuple[Catalogue, Catalogue]:
    clusters = Catalogue.of({n: fields[n] for n in nb.CLUSTER_READS})
    clouds = Catalogue.of({n: fields[n] for n in nb.CLOUD_READS})
    return clusters, clouds


def test_every_region_is_a_function_of_its_cluster_and_cloud_and_the_census_matches_the_field(models, coarse):
    """RENDER_PHYSICS §7's catalogue-against-field: the regions' Hα integrates back to the HII surface brightness
    within the census's own noise plus the leak; the fraction that reaches the diffuse gas is the escape fraction
    when nothing leaks."""
    F = coarse.fields
    R = coarse.grid.R
    clusters, clouds = _catalogues(F)
    regions = nb.materialise_nebular(clusters, clouds, {k: v.value for k, v in models[DEFAULT_MODEL].constants.items()})
    for name in nb.HII_COLUMNS:
        assert np.array_equal(np.asarray(regions[name]), np.asarray(F[name]), equal_nan=True), name
    L = np.asarray(F["hii_halpha_luminosity"], dtype=float)
    assert L.size == np.asarray(F["cluster_mass"]).size
    assert np.all(np.isfinite(L)) and np.all(L >= 0.0)
    field = float(np.trapezoid(np.asarray(F["halpha_surface_brightness_hii"]) * 2.0 * math.pi * R, R)) * PC_PER_KPC**2
    noise = math.sqrt(float((L**2).sum())) / float(L.sum())
    leak = float(F["dig_halpha_fraction"]) - 0.30
    assert L.sum() / field == pytest.approx(1.0, abs=3.0 * noise + leak)
    # the redistribution: every photon makes Halpha somewhere
    total = float(np.trapezoid(np.asarray(F["halpha_surface_brightness_nebular"]) * 2.0 * math.pi * R, R)) * PC_PER_KPC**2
    assert total == pytest.approx(float(F["halpha_luminosity_nebular"]))
    assert np.all(np.asarray(F["halpha_surface_brightness_nebular"]) >= np.asarray(F["halpha_surface_brightness_hii"]))
    # shape parameters inside their definitions
    assert np.all((np.asarray(F["hii_temperature"]) >= 6000.0) & (np.asarray(F["hii_temperature"]) <= 20000.0))
    assert np.all(np.asarray(F["hii_clumping"]) >= 1.0)
    assert np.all(np.asarray(F["hii_balmer_decrement"]) >= 2.74) and np.all(np.asarray(F["hii_balmer_decrement"]) <= 3.05)
    r = np.asarray(F["hii_stromgren_radius"])
    assert np.all(r <= np.asarray(F["cloud_size"])[np.flatnonzero(np.asarray(F["cloud_cluster_index"]) >= 0)] + 1e-9)
    assert float(F["dig_scale_height"]) == pytest.approx(1.4)


def test_the_default_census_numbers(default, default_layer_off):
    """Measured at S35 on the default grid (D184); the pins that move say why in their commit."""
    F = default.fields
    judged = default_layer_off.fields  # the two acceptance rows below read the layer-off census (S55, D214)
    L = np.asarray(F["hii_halpha_luminosity"], dtype=float)
    # one region per cluster (S33); S51 (D210): was 12860 (the clouds on the gas's ridge)
    # S56 (D215): was 12930 (the ridge follows five arm modes: another draw of the census)
    assert L.size == 12829  # S57 (D216): was 12814 (the clouds placed by the gas's steady response: another draw)
    assert float(np.median(np.asarray(F["hii_stromgren_radius"]))) == pytest.approx(0.720, abs=0.01)
    assert float(np.median(np.asarray(F["hii_electron_density"]))) == pytest.approx(193.7, rel=0.01)
    assert float(np.median(np.asarray(F["hii_ionization_parameter"]))) == pytest.approx(-2.826, abs=0.01)
    # the metal-rich inner disc sits on the floor; S51 (D210): was 7779 (the clouds on the gas's ridge)
    # S57 (D216): was 7775 (another draw); S56 (D215): was 7792 (another draw)
    assert int((np.asarray(F["hii_temperature"]) <= 6000.0).sum()) == 7780
    assert int(np.asarray(F["hii_density_bounded"]).sum()) == 0  # no region outgrows its cloud
    assert float(F["dig_halpha_fraction"]) == pytest.approx(0.30)
    assert float(F["halpha_luminosity_nebular"]) == pytest.approx(6.0770e7, rel=1e-3)  # S49 (D204, #126): the light integrated along the isochrone's points; was 6.0523e7
    # The check that replaced the calibration (D166 -> D184): the model's photons per unit star formation are
    # 0.71 of Kennicutt & Evans 2012's Kroupa/Starburst99 steady state - the same 0.71 that puts row 34 3%
    # under Bennett et al. 1994's window (debt #100). A consistency check, not a validation.
    assert float(F["halpha_sfr_ratio"]) == pytest.approx(0.7124, abs=0.002)  # S49 (D204, #126): the light integrated along the isochrone's points; was 0.7095
    # Row 35 (KEH89 -2.0 +/- 0.5). S55 (D214): was -2.008 (abs 0.02; the layer-on census reads -1.9893), read layer-off
    assert float(judged["hii_luminosity_function_slope"]) == pytest.approx(-2.0812, abs=0.02)
    # Row 37, a recorded miss under #117 (D195): the blind window is [-0.045, -0.005] dex/kpc (Zhao et al. 2026);
    # the model's ratio falls outward at its N/H gradient's pace.
    # S51 (D210): was -0.1035 - the row reads the HII-region census, redrawn with the clouds on the gas's ridge
    # (-0.103687 -> -0.105511); the miss stands, 0.002 further out.
    # S55 (D214): was -0.1055, read layer-off (-0.105511 -> -0.102973: the census placed by no pattern); still a miss
    assert float(judged["nii_halpha_gradient_hii"]) == pytest.approx(-0.1030, abs=0.002)
    # The layer-on census, which the viewer draws: not judged, read for the record. S56 (D215): were -1.9893 and
    # -0.105511 ("keeps the numbers it had", held bit for bit to S54's reference until then); the census placed by
    # five arm modes is another draw.
    # S57 (D216): were -2.0608 and -0.102613; the census placed by the gas's steady response is another draw again
    # (D216 predicted "rows 35 and 37 may move with placement, layer on"; the judged, layer-off rows above did not).
    assert float(F["hii_luminosity_function_slope"]) == pytest.approx(-2.0698, abs=1e-3)
    assert float(F["nii_halpha_gradient_hii"]) == pytest.approx(-0.103890, abs=1e-5)


def test_both_models_agree_and_a_region_alone_is_its_slice(models, coarse):
    """The azimuthal model draws the same clusters (S33) so the same regions; per-region determinism (D60): the
    regions of one cell, materialised from that cell's clouds alone, are the sweep's rows for that cell."""
    from galaxy.stages import clouds as cl
    from galaxy.stages import clusters as cs

    F = coarse.fields
    other = run(models["azimuthal"], grid=COARSE).fields
    for name in nb.HII_COLUMNS:
        assert np.array_equal(np.asarray(F[name]), np.asarray(other[name]), equal_nan=True), name
    c = {k: v.value for k, v in models[DEFAULT_MODEL].constants.items()}
    R = coarse.grid.R
    seed = int(coarse.inputs["systems_seed"])
    clusters, clouds = _catalogues(F)
    whole = nb.materialise_nebular(clusters, clouds, c)
    # rebuild the census cell by cell for a few cells and compare with the whole's slices
    all_clouds = cl.materialise_clouds(F, R, seed, c)
    all_clusters = cs.materialise_clusters(all_clouds, F, R, seed, c)
    offset = 0
    checked = 0
    for cell, count in all_clusters.counts:
        if checked >= 5 and cell % 97:
            offset += count
            continue
        one_clouds = cl.materialise_clouds(F, R, seed, c, (cell,))
        one_clusters = cs.materialise_clusters(one_clouds, F, R, seed, c)
        one = nb.materialise_nebular(one_clusters, one_clouds, c)
        for name in nb.HII_COLUMNS:
            assert np.array_equal(np.asarray(one[name]), np.asarray(whole[name])[offset:offset + count], equal_nan=True), (cell, name)
        offset += count
        checked += 1
    assert checked >= 5


def test_the_clusters_route_carries_the_regions_and_the_scalars_fall_under_rule_d4():
    svc = Service()
    r = svc.handle("/api/clusters", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    assert r.status == 200
    header, arrays = wire.decode(r.body)
    for name in nb.HII_COLUMNS:
        assert name in header["columns"] and name in arrays, name
    assert "hii_density_bounded" in arrays
    assert arrays["hii_halpha_luminosity"].shape == arrays["cluster_mass"].shape
    # a level filters the regions with their clusters
    r2 = svc.handle("/api/clusters", "r_min=7&r_max=9&phi_min=0&phi_max=0.4&level=2")
    h2, a2 = wire.decode(r2.body)
    assert a2["hii_halpha_luminosity"].size == h2["clusters"]["materialised"] <= arrays["hii_halpha_luminosity"].size
    fields = svc.handle("/api/fields", f"model={DEFAULT_MODEL}").json()["fields"]
    by_name = {f["name"]: f for f in fields}
    for name in ("dig_scale_height", "halpha_luminosity_nebular", "dig_halpha_fraction", "halpha_sfr_ratio", "hii_luminosity_function_slope",
                 "nii_halpha_gradient_hii"):  # the sixth since S44 (row 37, D195)
        assert by_name[name]["domain"] == "galaxy" and "rule D4" in by_name[name]["about"], name
    for name in ("halpha_surface_brightness_hii", "halpha_surface_brightness_dig", "halpha_surface_brightness_nebular"):
        assert by_name[name]["domain"] == "grid" and by_name[name]["unit"] == "Lsun/pc2"
    assert by_name["hii_halpha_emissivity"]["unit"] == "erg/s/cm3" and by_name["hii_electron_density"]["unit"] == "1/cm3"


# --- S42: the forbidden lines off Byler et al. 2017's grid (the owner's word on D184, 2026-09-27) -------------


def test_the_line_table_is_the_fetched_grid_and_a_grid_point_reads_back_exactly():
    """tools/fetch_nebular.py's table: FSPS's PARSEC-ionized dust-free grid at the pinned commit, its three axes as
    the file gives them, six lines. At a grid point the reader returns the grid's own ratio; off the grid it clamps."""
    g = nb._line_grid()
    assert g["log_z"].tolist() == [-1.98, -1.5, -0.98, -0.58, -0.39, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2]
    assert np.allclose(10.0 ** g["log_age_yr"], [5e5, 1e6, 2e6, 3e6, 4e6, 5e6, 6e6, 7e6, 1e7, 2e7], rtol=1e-12)
    assert g["log_u"].tolist() == [-4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0]
    assert g["lines"].tolist() == ["hbeta", "oiii_5007", "halpha", "nii_6583", "sii_6716", "sii_6731"]
    with np.load(nb.LINE_TABLE) as a:
        assert str(a["source"]) == "cconroy20/fsps@bd187a0d07dac17b55c4dc7c60d83f63694c1b4e:nebular/ZAU_ND_prsc.lines"
    cube = g["log_lsun_per_photon"].astype(float)
    # Solar gas, 1 Myr, log U = -3: the grid's own [O III]/Halpha and [N II]/Halpha (the file's 0.992 x its Hb/Ha
    # and 0.396, read off it at S42).
    got = nb.grid_line_ratios(0.0, 6.0, -3.0)
    assert float(got["oiii_5007"]) == pytest.approx(10.0 ** (cube[8, 1, 2, 1] - cube[8, 1, 2, 2]), rel=1e-12)
    assert float(got["nii_6583"]) == pytest.approx(0.396, abs=5e-4)
    # Past every edge the corner's value; a NaN input is a NaN line, never a guess.
    corner = nb.grid_line_ratios(1.0, 8.0, 0.0)
    assert float(corner["sii_6731"]) == pytest.approx(10.0 ** (cube[-1, -1, -1, 5] - cube[-1, -1, -1, 2]), rel=1e-12)
    assert np.isnan(nb.grid_line_ratios(np.nan, 6.0, -3.0)["oiii_5007"])
    # Linear in log luminosity between grid points, as FSPS's add_nebular.f90 interpolates.
    mid = nb.grid_line_ratios(0.0, 6.0, -2.75)["oiii_5007"]
    ends = [10.0 ** (cube[8, 1, k, 1] - cube[8, 1, k, 2]) for k in (2, 3)]
    assert float(mid) == pytest.approx(math.sqrt(ends[0] * ends[1]), rel=1e-12)


def test_the_default_regions_on_the_grid_and_their_lines(models, default):
    """Where the default census's regions sit on the grid, and what it gives them. Recorded, not judged: no row
    reads these lines yet. On the grid's own solar oxygen (8.93, Anders & Grevesse; D195, #121) the inner disc's
    gas is richer than the grid's +0.2 dex edge for 3.0% of the regions, which read the edge; the youngest 2.6%
    read the 0.5 Myr floor; every log U is inside."""
    F = default.fields
    g = nb._line_grid()
    solar = float(models[DEFAULT_MODEL].constants["NEBULAR_GRID_OXYGEN_SOLAR"].value)
    assert solar == 8.93  # the grid's log Z = 0 (Byler et al. 2017 section 2.1.2; D195)
    log_z = np.asarray(F["hii_oxygen_abundance"]) - solar
    age = np.log10(np.asarray(F["cluster_age"]) * 1e6)
    log_u = np.asarray(F["hii_ionization_parameter"])
    # S44: was 0.2641 on the 8.69 scale; the grid's log Z = 0 is Anders & Grevesse's 8.93 (D195, #121)
    assert (log_z > g["log_z"][-1]).mean() == pytest.approx(0.0302, abs=1e-3) and not (log_z < g["log_z"][0]).any()
    assert (age < g["log_age_yr"][0]).mean() == pytest.approx(0.0257, abs=1e-3) and not (age > g["log_age_yr"][-1]).any()
    assert np.all((log_u >= g["log_u"][0]) & (log_u <= g["log_u"][-1]))
    w = np.asarray(F["hii_halpha_luminosity"])
    weighted = {n: float(np.sum(np.asarray(F[f"hii_{n}_ratio"]) * w) / w.sum()) for n in nb.FORBIDDEN}
    # S44: was 0.477 / 0.131 / 0.053 / 0.041 on the 8.69 scale; the grid's log Z = 0 is Anders & Grevesse's 8.93
    # (D195, #121)
    # S51 (D210): [O III] 0.752 -> 0.756, the Halpha weights another draw of the census (the clouds on the gas's ridge)
    # S56 (D215): [O III] 0.756 -> 0.749, another draw again (the gas's ridge follows five arm modes)
    assert weighted == pytest.approx({"oiii_5007": 0.749, "nii_6583": 0.082, "sii_6716": 0.053, "sii_6731": 0.041}, abs=2e-3)
    # The gradient the metallicity sets: [O III] rises outward, [N II] falls.
    R = default.grid.R
    ha = np.asarray(F["halpha_surface_brightness_hii"])
    at = {r: int(np.argmin(np.abs(R - r))) for r in (4.0, 12.0)}
    ratio = {n: {r: F[f"{n}_surface_brightness_hii"][i] / ha[i] for r, i in at.items()} for n in ("oiii_5007", "nii_6583")}
    # S44: the 4 kpc bound was 0.05 on the 8.69 scale (the ring reads 0.116 now, 0.989 at 12 kpc); the grid's
    # log Z = 0 is Anders & Grevesse's 8.93 (D195, #121). S51 (D210): the bound was 0.15; the 4 kpc grid ring reads
    # 0.359 (1.087 at 12 kpc): that 75 pc ring's ~80 regions are a new draw when the clouds moved onto the gas's ridge,
    # and a handful of bright ones carry its Halpha; the regions' own Halpha-weighted mean over 3.5-4.5 kpc was 0.335
    # and is 0.361, the neighbouring rings 0.17-0.60 before and after. One ring of a heavy-tailed census is a realisation; the gradient is what is asserted.
    assert ratio["oiii_5007"][4.0] < 0.4 < 0.5 < ratio["oiii_5007"][12.0]
    assert ratio["nii_6583"][4.0] > ratio["nii_6583"][12.0]
    # Hbeta is Halpha over the Case B decrement in both layers.
    t_dig = float(models[DEFAULT_MODEL].constants["DIG_TEMPERATURE"].value)
    dec = float(nb.case_b_halpha(np.array([t_dig]))[0] / nb.case_b_hbeta(np.array([t_dig]))[0])
    assert np.allclose(np.asarray(F["hbeta_surface_brightness_dig"]) * dec, F["halpha_surface_brightness_dig"], rtol=1e-12)
