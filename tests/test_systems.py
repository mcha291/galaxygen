"""The star catalogue: does it reproduce the galaxy it was drawn from, and is it stable?

The correctness tests here deliberately check the catalogue against the *fields*
rather than against itself (rule B3): a sample that traces the wrong density would
still be internally consistent.
"""

from __future__ import annotations

import math
import time

import numpy as np
import pytest

from galaxy.run import run
from galaxy.stages.systems import (
    CATALOGUE_SAMPLE,
    CELL_COUNT,
    IMF_MAX,
    IMF_MIN,
    imf_mean_mass,
    imf_sample,
    invert_cdf,
    materialise,
    sech2_height,
)

# One run per model for the whole module. Materialising stars is cheap; running the
# pipeline again for every test is not, and this file has a lot of tests.
_RUNS: dict[str, object] = {}


def out(model):
    if model.name not in _RUNS:
        _RUNS[model.name] = run(model)
    return _RUNS[model.name]


def stars(model, n, **kw):
    o = out(model)
    return materialise(o.fields, o.grid.R, o.grid.t, kw.pop("seed", 0), n, **kw)


# --- the primitives -----------------------------------------------------------


def test_inverse_cdf_reproduces_the_density_it_was_given():
    """The whole point of rule B8: invert, do not reject."""
    x = np.linspace(0.0, 10.0, 500)
    weight = np.exp(-x / 2.0) * x          # a peaked density with a known mean
    u = np.random.default_rng(0).random(200_000)
    drawn = invert_cdf(u, x, weight)
    expected = float(np.trapezoid(x * weight, x) / np.trapezoid(weight, x))
    assert drawn.mean() == pytest.approx(expected, rel=0.01)


def test_sech2_inversion_matches_the_profile():
    u = np.random.default_rng(0).random(200_000)
    z = sech2_height(u, 0.3)
    # For rho ∝ sech²(z/2h) the mean |z| is 2h ln 2.
    assert np.abs(z).mean() == pytest.approx(2.0 * 0.3 * math.log(2.0), rel=0.02)
    assert np.median(z) == pytest.approx(0.0, abs=0.01)


def test_imf_mean_matches_a_numerical_integral():
    """The mean of a known distribution is computed, never sampled (rule B8)."""
    m = np.linspace(IMF_MIN, IMF_MAX, 2_000_000)
    phi = np.where(m < 0.5, m**-1.3, 0.5 ** (-1.3 + 2.3) * m**-2.3)
    numeric = float(np.trapezoid(m * phi, m) / np.trapezoid(phi, m))
    assert imf_mean_mass() == pytest.approx(numeric, rel=1e-3)


def test_imf_samples_span_the_range_and_have_the_right_mean():
    u = np.random.default_rng(0).random(500_000)
    masses = imf_sample(u)
    assert masses.min() >= IMF_MIN and masses.max() <= IMF_MAX
    assert masses.mean() == pytest.approx(imf_mean_mass(), rel=0.05)
    assert np.median(masses) < 0.5      # a steep IMF: most stars are small


# --- per-region determinism, the gate ----------------------------------------


def test_a_region_is_the_same_alone_as_in_a_full_sweep(model):
    cells = [17, 400, 900]
    alone = stars(model, 100_000, seed=0, cells=cells)
    reversed_order = stars(model, 100_000, seed=0, cells=list(reversed(cells)))
    for name in alone:
        assert np.array_equal(np.sort(alone[name]), np.sort(reversed_order[name])), name
    one = stars(model, 100_000, seed=0, cells=[400])
    assert one.size > 0
    assert np.allclose(one["star_radius"], alone["star_radius"][np.isin(alone["star_radius"], one["star_radius"])])


def test_a_small_sample_is_a_prefix_of_a_large_one(model):
    """What makes GALAXY_PLAN.md §4's clickable sample stable while the LOD ladder fills in."""
    small = stars(model, 100_000, seed=0, cells=[400])
    large = stars(model, 1_000_000, seed=0, cells=[400])
    n = small.size
    assert 0 < n < large.size
    for name in small:
        assert np.array_equal(small[name], large[name][:n]), name


def test_the_seed_changes_the_catalogue(model):
    a = stars(model, 50_000, seed=0, cells=[400])
    b = stars(model, 50_000, seed=1, cells=[400])
    assert not np.array_equal(a["star_radius"], b["star_radius"])


def test_the_catalogue_generates_a_million_stars_in_time(model):
    """The gate. Published number: 1.47 s on the S5 machine (D59); the bound is loose
    because a test that fails on a busy runner teaches everyone to ignore it."""
    start = time.perf_counter()
    catalogue = stars(model, 1_000_000, seed=0)
    elapsed = time.perf_counter() - start
    assert catalogue.size == pytest.approx(1_000_000, rel=0.01)
    assert elapsed < 10.0, f"{elapsed:.2f} s for 10^6 stars"


# --- does it trace the galaxy? ------------------------------------------------


def test_the_sample_traces_the_published_surface_density(model):
    """Checked against the field, not against the sample's own histogram (rule B3)."""
    o = out(model)
    cat = stars(model, 120_000, seed=0)
    R, sigma = o.grid.R, o.fields["stellar_surface_density"]
    weight = sigma * R
    expected = float(np.trapezoid(weight * R, R) / np.trapezoid(weight, R))
    assert cat["star_radius"].mean() == pytest.approx(expected, rel=0.02)


def test_the_thick_fraction_matches_the_vertical_stage(model):
    o = out(model)
    cat = stars(model, 120_000, seed=0)
    published = o.fields["thick_disc_stellar_mass"] / o.fields["stellar_mass_total"]
    assert cat["star_population"].mean() == pytest.approx(published, abs=0.03)


def test_thick_stars_are_older_and_higher(model):
    cat = stars(model, 120_000, seed=0)
    thick = cat["star_population"] == 1
    assert cat["star_age"][thick].mean() > cat["star_age"][~thick].mean()
    assert np.abs(cat["star_height"][thick]).mean() > np.abs(cat["star_height"][~thick]).mean()


def test_metallicity_is_looked_up_not_drawn(model):
    """Given when and where a star formed, its abundance is already decided."""
    cat = stars(model, 120_000, seed=0)
    thick = cat["star_population"] == 1
    assert np.nanmean(cat["star_metallicity"][thick]) < np.nanmean(cat["star_metallicity"][~thick])
    assert np.nanmax(cat["star_metallicity"]) < 1.0


# --- what the stage publishes -------------------------------------------------


def test_the_published_catalogue_is_the_sample_size(model):
    o = out(model)
    assert o.fields["catalogue_size"] == pytest.approx(CATALOGUE_SAMPLE, rel=0.01)
    assert len(o.fields["star_radius"]) == int(o.fields["catalogue_size"])
    assert o.decls["star_population"].categories == ("thin", "thick")


def test_the_star_count_is_computed_from_the_imf(model):
    o = out(model)
    assert o.fields["mean_stellar_mass"] == pytest.approx(imf_mean_mass())
    assert o.fields["star_count_total"] == pytest.approx(
        o.fields["stellar_mass_total"] / imf_mean_mass()
    )
    assert 1e10 < o.fields["star_count_total"] < 1e12


def test_an_empty_region_is_empty_not_an_error(model):
    far = stars(model, 100, seed=0, cells=[CELL_COUNT - 1])
    assert far.size == 0
    assert set(far) == {"star_radius", "star_azimuth", "star_height", "star_age",
                        "star_metallicity", "star_mass", "star_population"}
