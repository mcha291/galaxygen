"""S48 (D200): the bright-end-complete star catalogue.

The luminosity function per isochrone (stars, light and band flux above each threshold, integrated along the
isochrone's own points and renormalised to the field's tables) and the mass-on-isochrones decomposition, gated
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
from galaxy.stages.photometry import BANDS, band_nu_l_nu, imf_weights, isochrones, population_light


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
    pop = population_light()
    assert np.all(np.diff(tables.count_above, axis=-1) <= 0.0)
    assert np.all(np.diff(tables.light_above, axis=-1) <= 0.0)
    assert np.all(np.diff(tables.band_above, axis=-2) <= 0.0)
    assert np.all(tables.count_above[..., 0] <= tables.count_total)
    # The totals (L -> 0) are the field's own tables after the renormalisation, to 1e-12.
    from galaxy.stages.bright import _log_linear_integral, segments

    for (a, z) in [(0, 9), (14, 0), (22, 9), (32, 8), (35, 2), (35, 10)]:
        seg = segments(a, z)
        own = float((seg.number * _log_linear_integral(seg.log_l[:, 0], seg.log_l[:, 1], 0.0, 1.0)).sum())
        assert own * tables.light_factor[a, z] == pytest.approx(pop.light_per_mass[a, z], rel=1e-12)
        for k in range(len(BANDS)):
            g0, g1 = seg.neg_mag[:, 0, k], seg.neg_mag[:, 1, k]
            own = float((seg.number * _log_linear_integral(g0, g1, 0.0, 1.0)).sum())
            assert own * tables.band_factor[a, z, k] == pytest.approx(pop.band_flux[a, z, k], rel=1e-12)
    # Above the brightest point of every isochrone there is nothing.
    assert np.all(tables.count_above[..., -1] == 0.0) and np.all(tables.light_above[..., -1] == 0.0)


# --- (d) the renormalisation factors, pinned: they measure the field's mass grid ----------------------


def test_the_renormalisation_factors_are_pinned(tables):
    """The factor each isochrone's total takes to become the field's (population_light's trapezoid on a fixed
    log-spaced mass grid). Far from 1 on the old isochrones: the fixed grid puts one or two points on a red-giant
    branch a hundredth of a solar mass wide and on an AGB a thousandth wide, so the field's light per mass is
    off by up to a factor of seven either way, isochrone by isochrone - the integration along the isochrone's
    own points agrees with a 50-times-subdivided trapezoid to 0.1% (S48's check). Flagged, not hidden (D200)."""
    light = tables.light_factor
    # S48 (D200): bolometric 0.550 / 0.994 / 7.09 (min / median / max over the 396 isochrones), 171 beyond 10%.
    assert light.min() == pytest.approx(0.5497, abs=2e-3)
    assert np.median(light) == pytest.approx(0.9940, abs=2e-3)
    assert light.max() == pytest.approx(7.094, abs=1e-2)
    assert int((np.abs(light - 1.0) > 0.1).sum()) == 171
    k = tables.band_factor
    # S48 (D200): V 0.585 / 0.991 / 2.21; K 0.255 / 0.854 / 11.97.
    assert (k[..., 2].min(), k[..., 2].max()) == pytest.approx((0.5845, 2.207), abs=2e-3)
    assert (k[..., 7].min(), k[..., 7].max()) == pytest.approx((0.2549, 11.97), abs=2e-2)
    # The young isochrones (4-16 Myr), whose light is the main sequence's, are resolved by both: within 4%.
    assert np.all(np.abs(light[:9] - 1.0) < 0.04)


def test_the_luminosity_function_s_own_totals_are_a_fine_quadrature_s():
    """The independent check behind the pins: the isochrone's own L(m) (log L linear in mass, the field's
    reading) on a grid of every isochrone point with each interval cut in fifty agrees with the segments'
    total to 0.15%, where the field's 1500-point grid misses by a factor."""
    tab = isochrones()
    for (a, z) in [(35, 9), (32, 8), (22, 9)]:
        m, log_l, _ = tab.track(a, z)
        pieces = [np.geomspace(0.08, m[0], 200)] + [np.linspace(m[i], m[i + 1], 51) for i in range(m.size - 1) if m[i + 1] > m[i]]
        fine = np.unique(np.concatenate(pieces))
        quad = np.trapezoid(imf_weights(fine) * 10.0 ** np.interp(fine, m, log_l), fine) / br._imf_mass_formed()
        seg = br.segments(a, z)
        own = float((seg.number * br._log_linear_integral(seg.log_l[:, 0], seg.log_l[:, 1], 0.0, 1.0)).sum())
        assert own == pytest.approx(quad, rel=1.5e-3), (a, z)


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
        total += float(br._imf_number(np.array(lo), np.array(hi)))
    return total / br._imf_mass_formed()


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
    assert F["bright_star_limit"] == pytest.approx(33910.75, rel=1e-6)
    assert F["bright_star_count_1e3"] == pytest.approx(3.348738e6, rel=1e-6)
    assert np.all(np.asarray(F["bright_star_age"]) >= _cluster_window(models) * (1.0 - 1e-12))
    for d in br.COLUMNS:
        assert np.all(np.isfinite(np.asarray(F[d.name], dtype=float))), d.name
    assert set(np.unique(F["bright_star_phase"])) <= set(range(len(br.PHASES)))


def test_a_higher_threshold_keeps_a_prefix_cell_by_cell(galaxy, seed, default):
    """The stars above 2 l_min are the first of those above l_min in every cell, every column the same."""
    cells = _window(default.grid.R)
    low = br.materialise_bright(galaxy, seed, cells, 2000.0)
    high = br.materialise_bright(galaxy, seed, cells, 4000.0)
    assert 0 < high.size < low.size
    starts = {}
    offset = 0
    for c, n in low.counts:
        starts[c] = (offset, n)
        offset += n
    offset = 0
    for c, n in high.counts:
        first, held = starts[c]
        assert n <= held
        for name in high:
            assert np.array_equal(np.asarray(high[name])[offset:offset + n], np.asarray(low[name])[first:first + n]), (c, name)
        offset += n
    assert np.all(np.asarray(high["bright_star_luminosity"]) > 4000.0)
    assert int((np.asarray(low["bright_star_luminosity"]) > 4000.0).sum()) == high.size


def test_counts_over_the_whole_disc_are_poisson_about_the_expected_count(galaxy, seed):
    cells = br.all_cells()
    L = np.asarray(br.materialise_bright(galaxy, seed, cells, 2.0e4)["bright_star_luminosity"])
    for threshold in (2.0e4, 3.0e4, 5.0e4):
        lam = float(galaxy.expected(cells, np.log10(threshold)).sum())
        found = int((L > threshold).sum())
        assert abs(found - lam) < 4.0 * np.sqrt(lam), (threshold, found, lam)


def test_the_light_above_a_thousand_suns_is_what_the_luminosity_function_carries(galaxy, seed, default):
    """Σ L of the stars above 10^3 Lsun in a window against the luminosity function's own light there, within 4σ
    of the realised spread (σ² = Σ L², a compound Poisson sum). The field's budget above the same threshold - the
    tables renormalised to the field's - is 26% more in this window: the renormalisation's measure of the field's
    mass grid on the giant branch, pinned and flagged (D200), not a property of the stars."""
    cells = _window(default.grid.R)
    L = np.asarray(br.materialise_bright(galaxy, seed, cells, 1.0e3)["bright_star_luminosity"])
    own = float(galaxy.expected(cells, 3.0, "light_own").sum())
    assert abs(L.sum() - own) < 4.0 * np.sqrt((L**2).sum())
    assert float(galaxy.expected(cells, 3.0, "light").sum()) / own == pytest.approx(1.262, abs=0.005)  # S48 (D200)


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
    assert h["light"]["returned"] == pytest.approx(h["light"]["expected_own"], rel=0.1)
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
