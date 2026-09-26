"""The galactic habitable zone (BUILD_II Phase 6, S30, ruling (b)): built from Gowanlock et al.
2011's criteria as read, and deliberately unjudged — no acceptance row may name it."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages import habitable_zone as hz

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
ZONE = tuple(d.name for d in hz.HABITABLE_ZONE.publishes)
READS = ZONE + (
    "feh_history", "core_collapse_rate_history", "type_ia_rate_history", "sfr_surface_density_history",
    "thin_disc_scale_height",
)


@pytest.fixture(scope="module")
def coarse(prod):
    models, _, _ = prod
    return {m.name: run(m, grid=COARSE, only=READS) for m in models}


# --- ruling (b): built, and unjudged on purpose ----------------------------------------------


def test_no_acceptance_row_names_the_habitable_zone():
    """BUILD_II: 'Do not give the habitable zone an acceptance target.' Nor any of its ingredients."""
    named = {q.field for q in spec.QUANTITIES} | {q.sweep.abscissa for q in spec.QUANTITIES if q.sweep}
    assert not named & set(ZONE)
    assert not any(name in q.note for q in spec.QUANTITIES for name in ZONE)


def test_every_zone_field_says_it_is_deliberately_unjudged_and_why():
    for d in hz.HABITABLE_ZONE.publishes:
        assert "Deliberately unjudged" in d.about, d.name
        assert "nobody has measured the Galaxy's habitable zone" in d.about, d.name
    assert "deliberately unjudged" in hz.HABITABLE_ZONE.about


def test_the_zone_is_in_both_models(prod):
    for m in prod[0]:
        assert ("habitable_zone", "habitable_zone") in m.stages


# --- the criteria, as read (Gowanlock et al. 2011) -------------------------------------------


def test_the_metals_criterion_is_flat_below_solar_and_rises_as_ten_to_the_two_feh_above():
    feh = np.array([-np.inf, np.nan, -2.0, -0.01, 0.0, 0.2, 0.5, 1.0])
    p = hz.planet_probability(feh, 0.03, 2.0)
    assert np.all(p[:4] == 0.03)  # no metals yet is sub-solar: the source's flat tail
    assert p[4] == pytest.approx(0.03) and p[5] == pytest.approx(0.03 * 10**0.4) and p[6] == pytest.approx(0.3)
    assert p[7] == 1.0  # capped [inferred]; the source states no cap and 0.03 x 10^2 = 3


def test_the_sterilization_distance_is_eq_5():
    """An average SN II sits at M_std and reaches 8 pc; a mean type Ia at -19.34 reaches further."""
    assert hz.sterilization_distance(-17.505, 8.0, -17.505) == 8.0
    ratio = hz.sterilization_distance(-19.34, 8.0, -17.505) / 8.0
    assert ratio == pytest.approx(10 ** (0.4 * 1.835))


def test_a_star_younger_than_the_complex_life_delay_carries_no_weight(model, coarse):
    out = coarse[model.name]
    f, t = out.fields, out.grid.t
    w = np.asarray(f["habitability_history"])
    young = t + model.constants["COMPLEX_LIFE_DELAY"].value > out.grid.spec.t_max
    assert young.any() and np.all(w[:, young] == 0.0)
    assert np.all(w <= np.asarray(f["planet_metallicity_probability"]) + 1e-15) and np.all(w >= 0.0)


def test_the_survival_is_the_poisson_chance_of_no_event_in_the_ozone_window(model, coarse):
    """A second path (B3): one ring, one birth step, the window summed step by step."""
    out = coarse[model.name]
    f, g, c = out.fields, out.grid, model.constants
    dt = g.spec.t_max / g.spec.n_t
    i, j = int(np.argmin(abs(g.R - 8.2))), 100  # born at 3.45 Gyr: life at 7.45, window from 5.9
    rate = np.asarray(f["sterilization_rate_history"])[i]
    lo, hi = g.t[j] + c["COMPLEX_LIFE_DELAY"].value - c["OZONE_CONTINUITY"].value, g.t[j] + c["COMPLEX_LIFE_DELAY"].value
    edges = np.arange(g.spec.n_t + 1) * dt
    overlap = np.clip(np.minimum(edges[1:], hi) - np.maximum(edges[:-1], lo), 0.0, None)
    expected = float((rate * overlap).sum() * 1e9)
    p = np.asarray(f["planet_metallicity_probability"])[i, j]
    assert np.asarray(f["habitability_history"])[i, j] == pytest.approx(p * math.exp(-expected), rel=1e-9)


def test_the_hazard_is_the_two_histories_through_the_stellar_layer(model, coarse):
    f, c = coarse[model.name].fields, model.constants
    d_cc = c["STERILIZATION_DISTANCE"].value / 1000.0
    d_ia = hz.sterilization_distance(c["IA_ABSOLUTE_MAGNITUDE"].value, c["STERILIZATION_DISTANCE"].value,
                                     c["STERILIZATION_MAGNITUDE"].value) / 1000.0
    h = float(f["thin_disc_scale_height"]) / 1000.0
    expect = (np.asarray(f["core_collapse_rate_history"]) * d_cc**3 + np.asarray(f["type_ia_rate_history"]) * d_ia**3) \
        * (4.0 / 3.0 * math.pi) / (4.0 * h)
    assert np.allclose(f["sterilization_rate_history"], expect, rtol=1e-12, atol=0.0)


def test_a_thin_disc_with_no_thickness_leaves_the_hazard_undefined(prod):
    """Determinism's grid (n_t = 8) builds a thin disc whose scale height reads zero: no layer to
    spread the supernovae through, so the hazard and everything it feeds is NaN, never a number
    divided by zero (rule B9) - and no warning is raised on the way."""
    import warnings

    from galaxy.specs.determinism import SMALL

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        f = run(prod[0].get("basic"), grid=SMALL, only=ZONE + ("thin_disc_scale_height",)).fields
    assert float(f["thin_disc_scale_height"]) == 0.0
    assert np.all(np.isnan(np.asarray(f["sterilization_rate_history"])))
    for name in ("habitable_fraction", "habitable_zone_peak_radius", "habitable_zone_half_radius"):
        assert math.isnan(float(f[name])), name
    assert np.all(np.asarray(f["planet_metallicity_probability"]) >= 0.03)  # the metals never needed it


# --- the zone's shape, pinned (S30) ----------------------------------------------------------


def test_the_zone_as_the_criteria_read_it(model, coarse):
    """Measured at S30 on this grid (the default grid reads 4.7269e-4, 10.84 and 12.159 kpc). By
    number the habitable stars were born around 11 kpc and half of them outside 12 kpc, where only
    5% of the disc's stars formed: at R0 a planet sees about 2 sterilizing supernovae per Gyr
    today, nearly all type Ia at 43 pc, so the inner disc's metals are outweighed by its hazard.
    The per-star weight still rises at the grid's edge, because below solar metallicity the
    source's criterion is flat."""
    out = coarse[model.name]
    f, R = out.fields, out.grid.R
    assert float(f["habitable_fraction"]) == pytest.approx(4.7514e-4, rel=1e-4)
    assert float(f["habitable_zone_peak_radius"]) == pytest.approx(10.875, abs=1e-9)
    assert float(f["habitable_zone_half_radius"]) == pytest.approx(12.0517, abs=1e-3)
    formed = np.asarray(f["sfr_surface_density_history"]).sum(axis=1) * R
    inside = float(formed[R <= float(f["habitable_zone_half_radius"])].sum() / formed.sum())
    assert inside == pytest.approx(0.95269, abs=5e-5)
    assert int(np.argmax(np.asarray(f["habitability"]))) == R.size - 1  # the edge, not an interior maximum
    i = int(np.argmin(abs(R - 8.2)))
    assert np.asarray(f["sterilization_rate_history"])[i, -1] * 1e9 == pytest.approx(2.0834, abs=5e-4)


def test_the_other_reading_of_eq_5_moves_the_zone_inward(prod, monkeypatch):
    """Kept visible, as D176 kept its discarded normalisation: with the distance scaling as the
    square root of the flux ratio, 10^(-0.2 dM), a type Ia sterilizes to 18.6 pc rather than 43.4,
    the hazard at R0 falls tenfold (0.203 per Gyr) and the zone moves in - half the habitable stars
    inside 6.44 kpc, the peak at 6.6. Measured at S30 on this grid. Not adopted: the equation was
    read twice as -0.4, and choosing the reading whose answer resembles Lineweaver et al.'s 7-9 kpc
    would be choosing with the answer known (candidate debt)."""
    monkeypatch.setattr(hz, "sterilization_distance", lambda mag, base, m_std: base * 10.0 ** (-0.2 * (mag - m_std)))
    out = run(prod[0].get("basic"), grid=COARSE, only=ZONE)
    f, R = out.fields, out.grid.R
    assert float(f["habitable_zone_half_radius"]) == pytest.approx(6.4414, abs=1e-3)
    assert float(f["habitable_zone_peak_radius"]) == pytest.approx(6.625, abs=1e-9)
    assert float(f["habitable_fraction"]) == pytest.approx(5.9613e-3, rel=1e-4)
    i = int(np.argmin(abs(R - 8.2)))
    assert np.asarray(f["sterilization_rate_history"])[i, -1] * 1e9 == pytest.approx(0.20278, abs=5e-5)
