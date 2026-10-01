"""S48 (D200): the bright-end-complete star catalogue.

Commit 1: the luminosity function per isochrone (stars, light and band flux above each threshold, integrated
along the isochrone's own points and renormalised to the field's tables) and the mass-on-isochrones
decomposition, gated against the light stage it must reproduce.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import bright as br
from galaxy.stages.photometry import BANDS, band_nu_l_nu, imf_weights, isochrones, population_light


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {n: ms.get(n) for n in ms.names()}


@pytest.fixture(scope="module")
def default(models):
    return run(models[DEFAULT_MODEL])


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
