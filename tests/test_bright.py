"""S48 (D200): the bright-end-complete star catalogue.

The luminosity function per isochrone (stars, light and band flux above each threshold, integrated along the
isochrone's own points - the field's own quadrature since S49, D204) and the mass-on-isochrones decomposition, gated
against the light stage it must reproduce; then the ordered Poisson process per finest cell (complete above any
threshold, a prefix as it drops, per-region), the stage bright_stars and /api/bright.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.api.service import Service
from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import bright as br
from galaxy.stages.systems import MAX_LEVEL, cells_in
from galaxy.stages.photometry import (
    BANDS, band_nu_l_nu, imf_mass_formed, imf_number, isochrones, log_linear_integral, population_light, segments,
)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {n: ms.get(n) for n in ms.names()}


# The default model's run, as far as these gates read it: the light stage's fields, everything the bright stage
# reads (and the azimuthal model's modulation), and the bright stage itself.
WANTED = (
    "disc_surface_brightness", *(f"disc_sed_{b.lower()}" for b in BANDS), *br.READS, "sfr_modulation",
    *(d.name for d in br.COLUMNS), "bright_star_limit", "bright_star_count_1e3",
)


@pytest.fixture(scope="module")
def default(models):
    return run(models[DEFAULT_MODEL], only=WANTED)


@pytest.fixture(scope="module")
def tables():
    return br.luminosity_function()


def _formed(out, model):
    return np.asarray(out.fields["stars_formed_history"], dtype=float) / (1.0 - float(model.constants["RETURN_FRACTION"].value))


# --- (a) the decomposition reproduces the light stage --------------------------------------------------


def test_mass_on_isochrones_reproduces_the_light_stage_ring_by_ring(default, models):
    """Σ over (age, [M/H]) of the mass formed on each isochrone times the field's light per mass formed is the
    light stage's disc_surface_brightness at every ring, and each band's sum its disc_sed_<band>, to 1e-9."""
    spec = default.grid.spec
    M = br.mass_on_isochrones(_formed(default, models[DEFAULT_MODEL]), default.fields["feh_history"], spec.t_max, spec.n_t)
    pop = population_light()
    want = np.asarray(default.fields["disc_surface_brightness"], dtype=float)
    got = np.einsum("raz,az->r", M, pop.light_per_mass)
    assert np.all(want > 0.0)
    assert np.max(np.abs(got - want) / want) < 1e-9
    for k, band in enumerate(BANDS):
        want = np.asarray(default.fields[f"disc_sed_{band.lower()}"], dtype=float)
        got = band_nu_l_nu(np.einsum("raz,az->r", M, pop.band_flux[..., k]), band)
        assert np.max(np.abs(got - want) / want) < 1e-9, band


def test_the_weights_are_steps_over_s_reading_of_any_table():
    """For a table that is not the light, the weights still give steps_over's reading to rounding."""
    from galaxy.stages.photometry import cumulative_over_age, on_fine_ages, steps_over

    rng = np.random.default_rng(3)
    tab = isochrones()
    q = rng.random((tab.log_ages.size, tab.mhs.size, 1))
    t_max, n_t = 13.8, 400
    lo, dt = br._step_ages(t_max, n_t)
    feh = np.full(n_t, 0.0)
    want = steps_over(cumulative_over_age(on_fine_ages(q)), lo, lo + dt, feh)[:, 0]
    z = int(br.nearest_metallicity(np.array([0.0]))[0])
    got = br.isochrone_weights(t_max, n_t) @ q[:, z, 0]
    assert np.max(np.abs(got - want) / np.abs(want)) < 1e-12


# --- (b) an age window is split in step space ---------------------------------------------------------


def test_young_and_old_sum_to_the_whole_exactly(default, models):
    """The window at the cluster census's 20 Myr: a step straddling it is split by sub-interval, so the young
    part plus the old part is the whole to 1e-12 (and the same at the 100 Myr arm-crossing split)."""
    spec = default.grid.spec
    formed, feh = _formed(default, models[DEFAULT_MODEL]), default.fields["feh_history"]
    whole = br.mass_on_isochrones(formed, feh, spec.t_max, spec.n_t)
    for cut in (0.020, 0.1):
        young = br.mass_on_isochrones(formed, feh, spec.t_max, spec.n_t, age_max_gyr=cut)
        old = br.mass_on_isochrones(formed, feh, spec.t_max, spec.n_t, age_min_gyr=cut)
        assert np.max(np.abs(young + old - whole)) <= 1e-12 * np.max(whole), cut
        assert young.sum() > 0.0 and old.sum() > 0.0
    # The old part puts nothing on the isochrones younger than 10^7.3 yr but what the fine age grid's linear
    # reading of the cumulative integral smears across the cut: a millionth of it.
    old = br.mass_on_isochrones(formed, feh, spec.t_max, spec.n_t, age_min_gyr=0.020)
    assert abs(old[:, :7].sum()) < 1e-6 * old.sum()


# --- (c) the tables: monotone, and the totals the field's ---------------------------------------------


def test_the_tables_are_monotone_and_their_totals_are_the_field_s(tables):
    """One budget (rule A9; S49, D204): the luminosity function's totals - every living star's light and band
    flux per M☉ formed - are population_light's tables to 1e-12 on all 396 isochrones, because both are the one
    quadrature along the isochrone's points (photometry.segments). Until S49 they were renormalised per isochrone to
    the field's trapezoid on a fixed mass grid, by factors of 0.55 to 7.09 bolometric and 0.25 to 11.97 in K (D202)."""
    pop = population_light()
    assert np.all(np.diff(tables.count_above, axis=-1) <= 0.0)
    assert np.all(np.diff(tables.light_above, axis=-1) <= 0.0)
    assert np.all(np.diff(tables.band_above, axis=-2) <= 0.0)
    assert np.all(tables.count_above[..., 0] <= tables.count_total)
    assert np.all(tables.light_above[..., 0] <= tables.light_total * (1.0 + 1e-12))
    assert np.max(np.abs(tables.light_total / pop.light_per_mass - 1.0)) < 1e-12
    assert np.max(np.abs(tables.band_total / pop.band_flux - 1.0)) < 1e-12
    # And by hand on a few, from the segments themselves.
    for (a, z) in [(0, 9), (14, 0), (22, 9), (32, 8), (35, 2), (35, 10)]:
        seg = segments(a, z)
        own = float((seg.number * log_linear_integral(seg.log_l[:, 0], seg.log_l[:, 1], 0.0, 1.0)).sum())
        assert own == pytest.approx(pop.light_per_mass[a, z], rel=1e-12)
        for k in range(len(BANDS)):
            g0, g1 = seg.neg_mag[:, 0, k], seg.neg_mag[:, 1, k]
            own = float((seg.number * log_linear_integral(g0, g1, 0.0, 1.0)).sum())
            assert own == pytest.approx(pop.band_flux[a, z, k], rel=1e-12)
    # Above the brightest point of every isochrone there is nothing.
    assert np.all(tables.count_above[..., -1] == 0.0) and np.all(tables.light_above[..., -1] == 0.0)


# --- (e) the counts, by hand ---------------------------------------------------------------------------


def _by_hand(a: int, z: int, log_threshold: float) -> float:
    """Stars per M☉ formed brighter than the threshold on isochrone (a, z), from its own points: walk the track,
    find each mass interval on which log L (linear in mass between points) is above the threshold, and take the
    IMF's number on it analytically - linear in mass where the luminosity function spreads uniformly in log L."""
    m, log_l, _ = isochrones().track(a, z)
    total = 0.0
    for i in range(m.size - 1):
        m0, m1, y0, y1 = m[i], m[i + 1], log_l[i], log_l[i + 1]
        if m1 <= m0 or (y0 <= log_threshold and y1 <= log_threshold):
            continue
        if y0 > log_threshold and y1 > log_threshold:
            lo, hi = m0, m1
        else:
            cross = m0 + (log_threshold - y0) / (y1 - y0) * (m1 - m0)
            lo, hi = (cross, m1) if y1 > y0 else (m0, cross)
        total += float(imf_number(np.array(lo), np.array(hi)))
    return total / imf_mass_formed()


def test_count_above_on_the_oldest_solar_isochrone_against_a_hand_count(tables):
    """12.6 Gyr (log age 10.1, the table's oldest, nearest 12 Gyr) at [M/H] +0.05 (nearest solar): S48 (D200)
    counts 228.7 stars above 10^2 L☉ and 19.99 above 10^3 per 10^6 M☉ formed; the hand count from the
    isochrone's points (229 and 20.0) agrees to 0.5%."""
    a, z = 35, 9
    assert isochrones().log_ages[a] == pytest.approx(10.1) and isochrones().mhs[z] == pytest.approx(0.05)
    for log_threshold, pinned in ((2.0, 228.69), (3.0, 19.989)):
        k = int(np.argmin(np.abs(tables.log_l - log_threshold)))
        assert tables.log_l[k] == pytest.approx(log_threshold)
        per_million = tables.count_above[a, z, k] * 1e6
        assert per_million == pytest.approx(pinned, rel=1e-3)
        assert per_million == pytest.approx(_by_hand(a, z, log_threshold) * 1e6, rel=5e-3)


# --- commit 2: the ordered process, the stage and the route -------------------------------------------


@pytest.fixture(scope="module")
def galaxy(default, models):
    spec = default.grid.spec
    constants = {k: c.value for k, c in models[DEFAULT_MODEL].constants.items()}
    return br.BrightGalaxy(default.fields, default.grid.R, default.grid.t, spec.t_max, spec.n_t, constants)


@pytest.fixture(scope="module")
def seed(default):
    return int(default.inputs["systems_seed"])


@pytest.fixture(scope="module")
def api():
    return Service()


def _window(R, r_lo=7.0, r_hi=9.0, phi_lo=0.0, phi_hi=0.4):
    return np.asarray(cells_in(R, r_lo, r_hi, phi_lo, phi_hi, level=MAX_LEVEL), dtype=np.int64)


def _cluster_window(models):
    return br.cluster_window({k: c.value for k, c in models[DEFAULT_MODEL].constants.items()})


def test_the_stage_publishes_the_default_selection_and_its_two_scalars(default, models):
    F = default.fields
    L = np.asarray(F["bright_star_luminosity"])
    assert L.size == br.DEFAULT_SELECTION == 3162
    assert np.all(np.diff(L) <= 0.0)  # brightest first
    assert F["bright_star_limit"] == L[-1] == L.min()
    # S48 (D200): every disc star above 3.39e4 Lsun older than 20 Myr is in the default selection; the galaxy holds
    # 3.35e6 such stars above 10^3 Lsun (and 3.5e7 above 10^2, 6.4e4 above 10^4, 3e-4 expected above 10^5).
    # S48 (D203): the within-interval draw - 33 910.75 until then; the same 3162 stars by Gamma, the luminosity of
    # each now uniform across its segment's overlap with its interval. The expected count is the tables' (unmoved).
    # S51 (D210): the 20-100 Myr stars' cell weights follow sfr_modulation, which now reads the gas's own ridge, so
    # the cells' Gamma draws and the 3162nd star move; the expected count is still the tables'.
    # S56 (D215): the cells' weights follow five arm modes' contrast and the modulation of their gas ridge, so the
    # cells' Gamma draws and the 3162nd star move again; the expected count is still the tables'.
    # S57 (D216): the modulation reads the gas's steady response to the arm modes, so the young stars' cell weights,
    # the cells' Gamma draws and the 3162nd star move again; the expected count is still the tables'.
    # S58 (D217): the gas inside the bar's reach lies on the bar's lanes and the two-armed mode on the bar's axis, so
    # the modulation, the young stars' cell weights, the cells' Gamma draws and the 3162nd star move again; the
    # expected count is still the tables'.
    # S58 (D217 follow-up): star formation follows the bar's footprint, not the lanes (the gate: "the lanes' one
    # unsourced number (the width) must not drive a census"), so the modulation inside the bar's reach, the young
    # stars' cell weights there, the cells' Gamma draws and the 3162nd star move once more; the expected count
    # is still the tables'.
    # S59 (D218): the arms' winding is laid in seeded segments, so on each ring the stellar pattern and the
    # modulation are turned: the cells' weights, their Gamma draws and the 3162nd star move again (-1.0 %); the
    # expected count is still the tables', to the bit.
    assert F["bright_star_limit"] == pytest.approx(34348.365, rel=1e-6)  # S59 (D218): was 34697.372; S58 (D217 follow-up): was 34617.696; S58 (D217): was 34635.740; S57 (D216): was 34549.483; S56 (D215): was 33787.518; S51 (D210): was 33960.12
    assert F["bright_star_count_1e3"] == pytest.approx(3.348738e6, rel=1e-6)
    assert np.all(np.asarray(F["bright_star_age"]) >= _cluster_window(models) * (1.0 - 1e-12))
    for d in br.COLUMNS:
        assert np.all(np.isfinite(np.asarray(F[d.name], dtype=float))), d.name
    assert set(np.unique(F["bright_star_phase"])) <= set(range(len(br.PHASES)))


def test_a_higher_grid_threshold_keeps_a_prefix_cell_by_cell(galaxy, seed, default):
    """At grid thresholds (D203) the stars above the higher are, in every cell, the first of its Gamma order -
    ranks 0..m-1 - and they are the lower set's stars of those ranks, every column the same; the lower set holds
    no other star above the higher threshold. Rows within a cell come brightest first."""
    cells = _window(default.grid.R)
    k_low, k_high = br.interval_of(10.0 ** 3.3), br.interval_of(10.0 ** 3.6)
    l_low, l_high = 10.0 ** br.LOG_L_GRID[k_low], 10.0 ** br.LOG_L_GRID[k_high]
    low = br.materialise_bright(galaxy, seed, cells, l_low)
    high = br.materialise_bright(galaxy, seed, cells, l_high)
    assert 0 < high.size < low.size

    def by_name(cat):
        return {(int(c), int(r)): i for i, (c, r) in enumerate(zip(cat["cell"], cat["rank"]))}

    names_low, names_high = by_name(low), by_name(high)
    offset = 0
    for c, n in high.counts:
        assert sorted(int(r) for r in high["rank"][offset:offset + n]) == list(range(n)), c  # a Gamma prefix
        assert np.all(np.diff(high["bright_star_luminosity"][offset:offset + n]) <= 0.0)  # brightest first
        offset += n
    for name, i in names_high.items():
        j = names_low[name]
        for col in high:
            assert np.asarray(high[col])[i] == np.asarray(low[col])[j], (name, col)
    above = {name for name, j in names_low.items() if low["bright_star_luminosity"][j] > l_high}
    assert above == set(names_high)


def test_counts_over_the_whole_disc_are_poisson_about_the_expected_count(galaxy, seed):
    cells = br.all_cells()
    L = np.asarray(br.materialise_bright(galaxy, seed, cells, 2.0e4)["bright_star_luminosity"])
    for threshold in (2.0e4, 3.0e4, 5.0e4):
        lam = float(galaxy.expected(cells, np.log10(threshold)).sum())
        found = int((L > threshold).sum())
        assert abs(found - lam) < 4.0 * np.sqrt(lam), (threshold, found, lam)


def test_the_light_above_a_thousand_suns_is_what_the_luminosity_function_carries(galaxy, seed, default):
    """Σ L of the stars above 10^3 Lsun in a window against the luminosity function's light there, within 4σ of the
    realised spread (σ² = Σ L², a compound Poisson sum). One budget since S49 (D204): until then the field's budget
    here, the tables renormalised to the field's fixed mass grid, was 1.262 times the stars' own (debt #126)."""
    cells = _window(default.grid.R)
    L = np.asarray(br.materialise_bright(galaxy, seed, cells, 1.0e3)["bright_star_luminosity"])
    budget = float(galaxy.expected(cells, 3.0, "light").sum())
    assert abs(L.sum() - budget) < 4.0 * np.sqrt((L**2).sum())


def test_young_bright_stars_follow_where_stars_form_today(galaxy, seed, default):
    """In the azimuthal default the stars between the cluster window and 100 Myr are placed by sfr_modulation:
    the modulation at their positions sits far above the older stars' (S48: mean ln 0.50 against -0.46, the
    basic model's two parts both at -0.46)."""
    from galaxy.stages.systems import Modulation

    assert "sfr_modulation" in default.fields  # the default model publishes it (D197)
    cells = _window(default.grid.R, 6.0, 10.0, 0.0, 2.0 * np.pi)
    cat = br.materialise_bright(galaxy, seed, cells, 5.0e3)
    age = np.asarray(cat["bright_star_age"])
    m = Modulation(default.fields["sfr_modulation"], default.grid.R).at_points(cat["bright_star_radius"], np.asarray(cat["bright_star_azimuth"])[:, None])[:, 0]
    ln = np.log(np.maximum(m, 1e-12))
    young, old = age < 0.1, age >= 0.1
    assert young.sum() > 1000 and old.sum() > 1000
    gap = ln[young].mean() - ln[old].mean()
    error = np.hypot(ln[young].std() / np.sqrt(young.sum()), ln[old].std() / np.sqrt(old.sum()))
    assert gap > 0.5 and gap > 20.0 * error


def test_a_window_alone_is_the_same_cells_inside_a_whole_disc_call():
    """Per-region determinism (D60): a window's stars, asked alone of a fresh service, are the rows the whole disc
    holds in the same cells, named by (cell, rank), every column equal."""
    query = "l_min=20000"
    alone = Service().handle("/api/bright", "r_min=7&r_max=9&phi_min=0&phi_max=0.4&" + query)
    whole = Service().handle("/api/bright", query)
    assert alone.ok and whole.ok
    (ha, a), (hw, w) = alone.frame(), whole.frame()
    assert ha["columns"] == hw["columns"]
    name_w = {(int(c), int(r)): i for i, (c, r) in enumerate(zip(w["cell"], w["rank"]))}
    cells = set(int(c) for c in _window(Service().grid.R))
    inside = [i for (c, _), i in name_w.items() if c in cells]
    assert len(inside) == a["cell"].size > 0
    for j, (c, r) in enumerate(zip(a["cell"], a["rank"])):
        i = name_w[(int(c), int(r))]
        for col in ha["columns"]:
            assert a[col][j] == w[col][i], col


def test_the_n_brightest_are_complete_above_the_header_s_threshold(api, default, models):
    import time

    start = time.perf_counter()
    r = api.handle("/api/bright", "n=3162")
    cold = time.perf_counter() - start
    assert r.ok
    h, a = r.frame()
    L = a["bright_star_luminosity"]
    assert h["threshold"]["complete"] is True and h["count"]["returned"] == L.size == 3162
    assert np.all(np.diff(L) <= 0.0) and np.all(L >= h["threshold"]["l_min"]) and L[-1] == h["threshold"]["l_min"]
    # The route's whole-disc selection is the stage's default selection, and its scalars the stage's.
    assert np.array_equal(L, np.asarray(default.fields["bright_star_luminosity"]))
    assert h["scalars"] == {"bright_star_limit": default.fields["bright_star_limit"], "bright_star_count_1e3": default.fields["bright_star_count_1e3"]}
    assert np.all(a["bright_star_age"] >= _cluster_window(models) * (1.0 - 1e-12))
    for name in h["columns"]:
        assert np.all(np.isfinite(np.asarray(a[name], dtype=float))), name
    # The light: the stars carry what the luminosity function says (they are 3162 of an expected ~3250 there).
    assert h["light"]["returned"] == pytest.approx(float(L.sum()))
    assert h["light"]["returned"] == pytest.approx(h["light"]["expected"], rel=0.1)
    assert "expected_own" not in h["light"]  # one budget since S49 (D204)
    # A metadata-free route: what the stage reads ran, not the stage (rule D4).
    assert "bright_star" not in " ".join(h["stages"]) and "bright_stars" not in r.stages
    # S48 (D200): about 4.5 s cold for the whole disc on the owner's machine (the pipeline it reads, then 65 536
    # cells' first draws), 0.7 s warm; a loose class, not a benchmark.
    assert cold < 60.0
    start = time.perf_counter()
    assert api.handle("/api/bright", "n=3162").ok
    assert time.perf_counter() - start < 10.0


def _box_view(x_lo, x_hi, y_lo, y_hi, z_lo, z_hi):
    """A view-projection matrix whose frustum is an axis-aligned box in the viewer's frame, column-major."""
    m = np.zeros((4, 4))
    for row, (lo, hi) in enumerate(((x_lo, x_hi), (y_lo, y_hi), (z_lo, z_hi))):
        m[row, row] = 2.0 / (hi - lo)
        m[row, 3] = -(hi + lo) / (hi - lo)
    m[3, 3] = 1.0
    return ",".join(repr(float(v)) for v in m.flatten(order="F")), m


def test_with_a_view_the_n_brightest_inside_the_frustum(api):
    text, m = _box_view(7.0, 9.0, -1.0, 1.0, -1.0, 1.0)
    base = "r_min=6&r_max=10&phi_min=-0.5&phi_max=0.5&view=" + text
    r = api.handle("/api/bright", base + "&n=500")
    assert r.ok
    h, a = r.frame()
    assert h["view"] is True and h["threshold"]["complete"] is True and a["cell"].size == 500
    assert np.all(br.in_frustum(m, a["bright_star_radius"], a["bright_star_azimuth"], a["bright_star_height"]))
    # The same frustum cut at the header's l_min holds exactly these stars: complete above it.
    again = api.handle("/api/bright", base + f"&l_min={h['threshold']['l_min'] * (1.0 - 1e-12)!r}")
    assert again.ok
    _, b = again.frame()
    assert sorted(zip(b["cell"].tolist(), b["rank"].tolist())) == sorted(zip(a["cell"].tolist(), a["rank"].tolist()))


def test_the_route_refuses_what_it_cannot_answer(api):
    for query, says in (
        ("", "exactly one of n="),
        ("n=5&l_min=3000", "exactly one of n="),
        ("n=0", "outside 1..200000"),
        ("n=200001", "outside 1..200000"),
        ("l_min=-1", "positive luminosity"),
        ("l_min=1000", "expected stars in this window, more than 200000"),
        ("n=10&precision=f2", "precision"),
        ("n=10&view=1,2,3", "view="),
    ):
        r = api.handle("/api/bright", query)
        assert r.status == 400, query
        assert says in r.json()["error"], (query, r.json())
    # the count a refused l_min would hold is said
    assert "3348738" in api.handle("/api/bright", "l_min=1000").json()["error"]


# --- S48's wiring (D200 (5), D201): each star's band light through the viewer's curves -----------------------------


def _rgb_curves() -> list:
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "frontend" / "src" / "galaxy" / "filters.json"
    return json.loads(path.read_text(encoding="utf-8"))["sets"]["rgb"]["curves"]


def _with_filters(query: str, curves: list, **extra) -> str:
    import json
    from urllib.parse import urlencode

    return query + "&" + urlencode({"filters": json.dumps(curves), **extra})


def test_with_filters_each_star_carries_its_band_light_through_the_curves(api):
    """filters= adds ``response`` (stars x filters, Lsun): spectra.object_response on the star's eight magnitudes and
    its temperature. Against the exact field machinery (stellar_response) on the same floored anchors, 200 stars: within
    0.01 mag (D201 measured 2.8e-6 over 2 000 isochrone points). Without filters the body is the one it was, byte for
    byte; f4 sends the response as float32 too."""
    from galaxy.api import wire
    from galaxy.stages import spectra

    query = "r_min=7&r_max=9&phi_min=0&phi_max=0.4&n=1000"
    assert api.handle("/api/bright", query).ok  # warm, so the bodies below name the same stages run (none)
    curves = _rgb_curves()
    got = api.handle("/api/bright", _with_filters(query, curves, white=6500))
    assert got.ok
    h, a = got.frame()
    assert a["response"].shape == (1000, 3) and np.all(a["response"] > 0.0)
    assert [c["name"] for c in h["filters"]] == ["R", "V", "B"] and h["response"]["unit"] == "Lsun"
    assert h["response"]["temperature"] == "bright_star_temperature" and h["white"]["kelvin"] == 6500.0
    parsed = spectra.parse_curves(curves)
    anchors = spectra.object_nu_l_nu(br.magnitudes(a))
    pick = np.linspace(0, 999, 200).round().astype(int)
    floored = np.maximum(anchors[pick], spectra.ANCHOR_FLOOR * anchors[pick].max(axis=1, keepdims=True))
    exact = spectra.stellar_response(floored, a["bright_star_temperature"][pick], parsed)
    assert np.max(np.abs(2.5 * np.log10(a["response"][pick] / exact))) < 0.01
    # A star's response is its light where the filters see it: through R, V and B together less than its bolometric.
    assert np.all(a["response"].sum(axis=1) < a["bright_star_luminosity"])
    plain = api.handle("/api/bright", query)
    stripped = {k: v for k, v in h.items() if k not in ("filters", "white", "response")}
    assert plain.body == wire.encode(stripped, [(k, v) for k, v in a.items() if k != "response"])
    _, f4 = api.handle("/api/bright", _with_filters(query + "&precision=f4", curves)).frame()
    assert f4["response"].dtype == np.float32 and np.array_equal(f4["response"], a["response"].astype(np.float32))


def test_the_bright_route_refuses_bad_filters(api):
    for query, says in (
        ("n=10&white=6500", "white= is a blackbody's response"),
        ("n=10&filters=rgb", "must be a JSON list"),
        ("n=10&filters=%5B%5D", "1 to 8 curves"),
        (_with_filters("n=10", _rgb_curves(), white=10), "white=10.0 is outside 1000..100000 K"),
    ):
        r = api.handle("/api/bright", query)
        assert r.status == 400 and says in r.json()["error"], (query, r.json())
        assert r.stages == ()


# --- S48's wiring: points and field add up (D200 (4)) ----------------------------------------------------------------


def _constants(models) -> dict:
    return {k: c.value for k, c in models[DEFAULT_MODEL].constants.items()}


@pytest.mark.parametrize("l_min", [1e2, 1e3, 1e4])
def test_unresolved_young_and_bright_are_the_stars_per_ring_and_band(default, models, l_min):
    """The identity the single counting rests on: per ring and band, the field's remainder plus the young population
    (the cluster census's ages) plus the old stars above l_min (the bright catalogue's, the field's budget) is the
    light stage's own disc_sed_<band>, and the bolometric parts its disc_surface_brightness - to 1e-9 (S48: 1e-13).
    One decomposition (bright.part_masses) and one set of tables; a threshold on the grid is read exactly."""
    spec = default.grid.spec
    res = br.resolve(default.fields, spec.t_max, spec.n_t, _constants(models), l_min)
    a = res.anchors
    assert res.log_l == pytest.approx(np.log10(l_min), abs=1e-12)
    parts = a["unresolved_middle"] + a["unresolved_old"] + a["young"] + a["bright_middle"] + a["bright_old"]
    for k, band in enumerate(BANDS):
        want = np.asarray(default.fields[f"disc_sed_{band.lower()}"], dtype=float)
        assert np.all(want > 0.0)
        assert np.max(np.abs(parts[:, k] / want - 1.0)) < 1e-9, band
        assert np.max(np.abs(a["total"][:, k] / want - 1.0)) < 1e-9, band
        for name, value in a.items():
            assert np.all(value[:, k] >= 0.0), (name, band)
    light = res.light
    want = np.asarray(default.fields["disc_surface_brightness"], dtype=float)
    assert np.max(np.abs((light["unresolved"] + light["young"] + light["bright"]) / want - 1.0)) < 1e-9
    assert np.max(np.abs(light["total"] / want - 1.0)) < 1e-9


def _area(default) -> np.ndarray:
    from galaxy.stages.disc import PC_PER_KPC

    return 2.0 * np.pi * default.grid.R * PC_PER_KPC**2


def _band_light(anchors: np.ndarray, curves: list) -> np.ndarray:
    """Through curves that are the table's own bands (the rgb set: R, V, B), a band-consistent join returns each
    band's light: the anchor's mean L_lambda times the curve's area. Linear, so a sum of objects' responses is the
    response of their summed anchors."""
    from galaxy.stages import spectra

    parsed = spectra.parse_curves(curves)
    idx = [BANDS.index(c.name) for c in parsed]
    area = np.array([np.trapezoid(c.at(c.grid()), c.grid()) for c in parsed])
    return np.asarray(anchors)[..., idx] / spectra.SED_WAVELENGTHS[idx] * area


@pytest.fixture(scope="module")
def through_rgb(api):
    """The whole disc's bright stars above 10^4 Lsun (64 492 of an expected 64 233, under the route's cap) and its
    cluster census, each through the rgb set."""
    bright = api.handle("/api/bright", _with_filters("l_min=10000", _rgb_curves()))
    clusters = api.handle("/api/clusters", _with_filters("level=0", _rgb_curves()))
    assert bright.ok and clusters.ok
    return bright.frame(), clusters.frame()


def _expected_bright(galaxy, table: np.ndarray, log_l: float) -> np.ndarray:
    """What the luminosity function puts above 10^log_l over the whole disc, from ``table`` (a per-isochrone member):
    every finest cell's area x its parts' azimuthal weights x the mass on each isochrone, summed."""
    tables = br.luminosity_function()
    mass = np.einsum("r,pr,prx->px", galaxy.area, galaxy.weights.sum(axis=2), galaxy.mass_cell)
    return br.above_at(mass.reshape(2, *tables.count_above.shape[:2]), table, log_l).sum(axis=0)


# S48's wiring, measured: the whole disc's bright stars above 10^4 Lsun through rgb (R, V, B) against the expectation
# from their own budget. Until D203 the bolometric light held (z = +0.08) and the band light did not (0.977 / 0.915 /
# 0.826, z = -3.9 / -14 / -26); S48 (D203): the within-interval draw - 1.0033 / 1.0044 / 1.0041, z = +0.54 / +0.66 / +0.51.
# S51 (D210): the young stars' cells follow the gas's own ridge through sfr_modulation - another realisation of
# the same budget.
# S56 (D215): the cells' weights follow five arm modes - another realisation again, inside the 4-sigma gate below.
# S57 (D216): the young stars' cells follow the gas's steady response through sfr_modulation - another realisation
# again, inside the same gate.
# S58 (D217): the young stars' cells follow the lanes inside the bar's reach and the bar-tied two-armed mode -
# another realisation again, inside the same gate.
# S58 (D217 follow-up): the young stars inside the bar's reach follow the bar's footprint and not its lanes -
# another realisation, inside the same gate.
# S59 (D218): every cell's weight follows the arms on a winding laid in seeded segments - another realisation,
# inside the same gate.
BRIGHT_RGB_OVER_OWN = (0.99811, 0.99982, 1.00218)  # S59 (D218): was (1.00161, 1.00226, 1.00268); S58 (D217 follow-up): was (1.00235, 1.00392, 1.00461); S58 (D217): was (1.00198, 1.00322, 1.00488); S57 (D216): was (1.00149, 1.00552, 1.01059); S56 (D215): was (1.00065, 1.00380, 1.00503); S51 (D210): was (1.00325, 1.00435, 1.00412)


def test_the_bright_stars_light_is_their_budget_and_their_band_light_is_pinned(galaxy, through_rgb):
    """(b) the realisation. The catalogue's stars above 10^4 Lsun, summed over the whole disc, against what the
    luminosity function's budget (light_above, band_above) expects there: the bolometric light within 4
    sigma of the realised spread (sigma^2 = sum L^2, a compound Poisson sum), and the light through rgb, pinned (the
    4-sigma gate is the test below). Until D203 the band light was short by 2 / 8 / 17 % in R / V / B: the segment was
    picked by its stars per dex at an L read log-linearly across the interval, which under-drew the hot segments
    where an isochrone's count is not log-linear inside an interval; since D203 the segment is drawn by its exact
    count in the interval and L uniformly across its overlap. Until S49 the field's budget was 0.8-0.9 % above the
    stars' own here (debt #126); one budget since (D204)."""
    (h, a), _ = through_rgb
    L = a["bright_star_luminosity"]
    own = float(_expected_bright(galaxy, br.luminosity_function().light_above, 4.0))
    assert L.size == h["count"]["returned"] and abs(L.size - h["count"]["expected"]) < 4.0 * np.sqrt(h["count"]["expected"])
    assert abs(L.sum() - own) < 4.0 * np.sqrt((L**2).sum())
    tables = br.luminosity_function()
    anchors = band_nu_l_nu_all(_expected_bright(galaxy, tables.band_above, 4.0))
    expected = _band_light(anchors, _rgb_curves())
    got = a["response"].sum(axis=0)
    assert got / expected == pytest.approx(BRIGHT_RGB_OVER_OWN, abs=1e-4)


def test_the_bright_stars_band_light_is_their_budget_within_4_sigma(galaxy, through_rgb):
    """D203's gate (a strict xfail at S48's wiring): above 10^4 Lsun over the whole disc, the realised light in each
    of the table's eight bands and through each rgb filter within 4 sigma of the budget. S48 (D203): the eight
    bands U..K at 1.0044 / 1.0042 / 1.0043 / 1.0033 / 1.0002 / 0.9971 / 0.9970 / 0.9978 (z = +0.55 / +0.51 / +0.66 /
    +0.55 / +0.03 / -0.52 / -0.53 / -0.40), until then 0.84 / 0.83 / 0.92 / 0.98 / 1.02 / 1.04 / 1.04 / 1.03."""
    (_, a), _ = through_rgb
    tables = br.luminosity_function()
    expected = _band_light(band_nu_l_nu_all(_expected_bright(galaxy, tables.band_above, 4.0)), _rgb_curves())
    z = (a["response"].sum(axis=0) - expected) / np.sqrt((a["response"] ** 2).sum(axis=0))
    assert np.all(np.abs(z) < 4.0), z
    flux = 10.0 ** (-0.4 * br.magnitudes(a))
    budget = _expected_bright(galaxy, tables.band_above, 4.0)
    z = (flux.sum(axis=0) - budget) / np.sqrt((flux**2).sum(axis=0))
    assert np.all(np.abs(z) < 4.0), z


def test_the_bolometric_light_at_ten_to_the_three_and_a_half_is_the_budget(galaxy, seed, default):
    """D203's second gate: at 10^3.5 Lsun, where the old draw was 1.2 % low (z = -8 over the whole disc), the stars'
    light within 4 sigma of what the luminosity function's budget puts there - here over the 6-10 kpc annulus
    (the whole disc holds 6.5e5 such stars; S48 (D203) measured it at 1.0007, z = +0.44), and each band too."""
    cells = _window(default.grid.R, 6.0, 10.0, 0.0, 2.0 * np.pi)
    cat = br.materialise_bright(galaxy, seed, cells, 10.0 ** 3.5)
    L = np.asarray(cat["bright_star_luminosity"])
    own = float(galaxy.expected(cells, 3.5, "light").sum())
    assert L.size > 1e5 and abs(L.sum() - own) < 4.0 * np.sqrt((L**2).sum())
    tables = br.luminosity_function()
    ring, sector = galaxy.locate(cells)
    mass = np.einsum("c,pc,pcx->px", galaxy.area[ring], galaxy.weights[:, ring, sector], galaxy.mass_cell[:, ring])
    budget = br.above_at(mass.reshape(2, *tables.count_above.shape[:2]), tables.band_above, 3.5).sum(axis=0)
    flux = 10.0 ** (-0.4 * br.magnitudes(cat))
    z = (flux.sum(axis=0) - budget) / np.sqrt((flux**2).sum(axis=0))
    assert np.all(np.abs(z) < 4.0), z


def test_one_isochrone_drawn_alone_carries_its_band_budget():
    """The case D203 was found by: log age 7.6, [M/H] +0.05, 3e5 stars above 10^2 Lsun, each interval by the
    isochrone's own counts and each star placed by bright.on_isochrone. Until D203: B 0.72, K 1.11 of its budget;
    S48 (D203): U..K 1.0016 / 1.0017 / 0.9988 / 0.9954 / 0.991 / 0.986 / 0.984 / 0.984, every band within 1.1 sigma,
    the bolometric 0.997, and no star without a segment in its interval."""
    tables = br.luminosity_function()
    a, z = 10, 9
    assert isochrones().log_ages[a] == pytest.approx(7.6) and isochrones().mhs[z] == pytest.approx(0.05)
    k0 = int(np.argmin(np.abs(tables.log_l - 2.0)))
    dn = tables.count_above[a, z, k0:-1] - tables.count_above[a, z, k0 + 1:]
    rng = np.random.default_rng(7)
    n = 300_000
    k = np.clip(k0 + np.searchsorted(np.cumsum(dn) / dn.sum(), rng.random(n), side="right"), k0, tables.log_l.size - 2)
    placed = br.on_isochrone(a * isochrones().mhs.size + z, k, rng.random(n), rng.random(n), isochrones().mhs.size)
    assert not placed["fallback"].any()
    assert np.all((placed["log_l"] >= tables.log_l[k]) & (placed["log_l"] <= tables.log_l[k + 1]))
    flux = 10.0 ** (-0.4 * placed["mags"])
    per_star = tables.band_above[a, z, k0] / tables.count_above[a, z, k0]
    zs = (flux.sum(axis=0) - per_star * n) / np.sqrt((flux**2).sum(axis=0))
    assert np.all(np.abs(zs) < 4.0), zs
    ratio = flux.sum(axis=0) / (per_star * n)
    assert ratio[BANDS.index("B")] == pytest.approx(1.0017, abs=2e-4) and ratio[BANDS.index("K")] == pytest.approx(0.9840, abs=2e-4)


# S48's wiring, measured: the cluster census's light through rgb (R, V, B) and bolometric, whole disc, against the
# young population's (ages under the census's window) from the same decomposition. S33 measured the census's ionizing
# photons at 1.0088 of the young population's.
# S51 (D210): the clouds, and so the clusters, sit in the gas's own ridge - a different Poisson realisation of the
# same expected census (whole-disc cluster light +3.2 %, its seed-to-seed spread 4.4 %).
# S56 (D215): the gas's ridge follows five arm modes at their own phases - another Poisson realisation again.
# S57 (D216): the clouds are placed by the gas's steady response to the arm modes - another Poisson realisation again
# (whole-disc cluster light -1.0 %).
# S58 (D217): the clouds inside the bar's reach are placed by the bar's lanes, and the two-armed mode sits on the
# bar's axis - another Poisson realisation again (whole-disc cluster light +0.7 %).
# S59 (D218): the gas's response is turned round each ring by a winding laid in seeded segments, so the clouds fall
# in other cells - another Poisson realisation again (whole-disc cluster light +5.0 %: three clusters of
# 1.9-2.6e5 Msun under 4 Myr old are new to the census and are its three brightest; the clusters' light's own
# noise, sqrt(sum L^2) / sum L, is 4.8 %, and the young population it is read against has not moved).
CLUSTERS_RGB_OVER_YOUNG = (0.99372, 1.00109, 1.01543)  # S59 (D218): was (0.96011, 0.96524, 0.97627); S58 (D217): was (0.96043, 0.96399, 0.97313); S57 (D216): was (0.96603, 0.96950, 0.97826); S56 (D215): was (1.02504, 1.02748, 1.03528); S51 (D210): was (0.98508, 0.99003, 1.00087); S49 (D204, #126): the light integrated along the isochrone's points; was (0.98482, 0.98957, 1.00026)
CLUSTERS_LIGHT_OVER_YOUNG = 1.03547  # S59 (D218): was 0.98645; S58 (D217): was 0.97957; S57 (D216): was 0.98920; S56 (D215): was 1.04343; S51 (D210): was 1.01128


def test_the_cluster_census_carries_the_young_light(default, models, through_rgb):
    """(b) the single counting's other half: the census's clusters (one per cloud past its embedded phase, ages 0-20 Myr)
    summed over the whole disc, through rgb and bolometric, against the young part of the decomposition the field's
    remainder is cut by. Within 1.5 % in every filter and 1.1 % bolometric until S51; 3.6 % and 4.4 % since (D210: the
    clouds on the gas's ridge, another draw of the same census; the clusters' light moved +3.2 %, its seed-to-seed
    spread 4.4 %); 3.4 % and 1.1 % under at S56 (D215: the ridge on five arm modes, another draw again; the
    clusters' light moved -5.2 %); 4.0 % and 2.0 % under since S57 (D216: the clouds on the gas's steady response,
    another draw again; the clusters' light moved -1.0 %); from 0.6 % under to 1.5 % over and 3.5 % over since S59
    (D218: the winding in seeded segments, another draw again; the clusters' light moved +5.0 %): the clusters
    carry the young light, so the remainder that leaves it out counts no star twice and drops none. A realisation (the
    census is a Poisson draw of clouds), seeded, so pinned tight."""
    _, (hc, ac) = through_rgb
    spec = default.grid.spec
    res = br.resolve(default.fields, spec.t_max, spec.n_t, _constants(models), 1e4)
    area = _area(default)
    young = np.trapezoid(res.anchors["young"] * area[:, None], default.grid.R, axis=0)
    ratio = ac["response"].sum(axis=0) / _band_light(young, _rgb_curves())
    assert ratio == pytest.approx(CLUSTERS_RGB_OVER_YOUNG, abs=2e-4)
    assert np.all(np.abs(ratio - 1.0) < 0.1)
    light = ac["cluster_luminosity"].sum() / float(np.trapezoid(res.light["young"] * area, default.grid.R))
    assert light == pytest.approx(CLUSTERS_LIGHT_OVER_YOUNG, abs=2e-4)


def band_nu_l_nu_all(flux: np.ndarray) -> np.ndarray:
    """The eight band sums as lambda L_lambda anchors, L☉."""
    return np.array([float(band_nu_l_nu(np.asarray(flux)[k], b)) for k, b in enumerate(BANDS)])
