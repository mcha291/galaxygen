"""Supernova rates and the galactic habitable zone (BUILD_II Phase 6, S30).

Pins the two sourced constants, the two conservation checks the gate names — the core-collapse
rate is SFR times the IMF integral exactly, the Ia history counts the events the chemistry's
iron convolution implies — and rows 30-31, whose numbers are read from ``spec`` (renumbering is
spec's one line).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages import supernovae as sn
from galaxy.stages import systems
from galaxy.stages.chemistry_dtd import dtd_bins, snia_rate

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
RATES = (
    "core_collapse_rate", "core_collapse_rate_total", "type_ia_rate", "type_ia_rate_total",
    "core_collapse_per_mass_formed", "type_ia_per_mass_formed", "core_collapse_rate_history",
    "type_ia_rate_history", "sfr", "sfr_surface_density", "sfr_surface_density_history",
)


@pytest.fixture(scope="module")
def coarse(prod):
    models, _, _ = prod
    return {m.name: run(m, grid=COARSE, only=RATES) for m in models}


# --- the sources (read at S30, rule B9) -------------------------------------------------------


def test_the_two_constants_are_the_numbers_the_sources_print(prod):
    """Smartt 2009 §4.4: m_min = 8.5 +1 -1.5 Msun (not the plan's recalled 8); Maoz & Graur 2017
    eq. 2: 0.7 Msun of iron per Ia. Both models share them (level 0)."""
    for m in prod[0]:
        assert m.constants["CORE_COLLAPSE_MIN_MASS"].value == 8.5
        assert m.constants["IA_IRON_MASS"].value == 0.7
        assert "section 4.4" in m.constants["CORE_COLLAPSE_MIN_MASS"].about
        assert "eq. 2" in m.constants["IA_IRON_MASS"].about


# --- core collapse: SFR x the IMF integral -----------------------------------------------------


def _kroupa_numeric(m_lo: float, n: int = 400_001) -> float:
    """Stars above ``m_lo`` per solar mass formed, by quadrature on a log grid: a second path (B3)."""
    k = systems.IMF_BREAK ** (systems.IMF_LOW_SLOPE - systems.IMF_HIGH_SLOPE)

    def xi(m):
        return np.where(m < systems.IMF_BREAK, m**systems.IMF_LOW_SLOPE, k * m**systems.IMF_HIGH_SLOPE)

    def quad(f, lo, hi):  # each piece on its own log grid, so the kink at the break is a node
        if hi <= lo:
            return 0.0
        m = np.geomspace(lo, hi, n)
        return float(np.trapezoid(f(m), m))

    lo_b, hi_b = (systems.IMF_MIN, systems.IMF_BREAK), (systems.IMF_BREAK, systems.IMF_MAX)
    mass = quad(lambda m: xi(m) * m, *lo_b) + quad(lambda m: xi(m) * m, *hi_b)
    number = quad(xi, max(m_lo, lo_b[0]), lo_b[1]) + quad(xi, max(m_lo, hi_b[0]), hi_b[1])
    return number / mass


def test_stars_above_the_limit_is_the_imf_integral():
    """The analytic count against quadrature, and against the population stage's own mean mass.

    Measured at S30: 0.0100316 per Msun above 8.5 Msun — Maoz & Graur 2017's 'about one CC SN for
    every 100 Msun of stars formed' (0.010 +/- 0.002 for a Kroupa IMF, their section I) — and
    0.0108744 above 8, the plan's recalled limit."""
    assert sn.imf_stars_above(8.5) == pytest.approx(_kroupa_numeric(8.5), rel=1e-6)
    assert sn.imf_stars_above(0.3) == pytest.approx(_kroupa_numeric(0.3), rel=1e-6)  # across the break
    assert sn.imf_stars_above(systems.IMF_MIN) * systems.imf_mean_mass() == pytest.approx(1.0, rel=1e-12)
    assert sn.imf_stars_above(8.5) == pytest.approx(0.0100316, abs=5e-8)
    assert sn.imf_stars_above(8.0) == pytest.approx(0.0108744, abs=5e-8)
    assert sn.imf_stars_above(9.0) / sn.imf_stars_above(8.5) == pytest.approx(0.92663, abs=5e-5)  # Heger's 9: -7.3%
    assert sn.imf_stars_above(systems.IMF_MAX) == 0.0


def test_the_core_collapse_rate_is_sfr_times_the_imf_integral(model, coarse):
    f = coarse[model.name].fields
    per = _kroupa_numeric(8.5)
    assert float(f["core_collapse_per_mass_formed"]) == pytest.approx(per, rel=1e-6)
    assert np.allclose(f["core_collapse_rate"], float(f["core_collapse_per_mass_formed"]) * f["sfr_surface_density"], rtol=1e-14, atol=0)
    # Integrated exactly as the SFR is, so the total is SFR x the integral to rounding.
    assert float(f["core_collapse_rate_total"]) == pytest.approx(float(f["sfr"]) * per, rel=1e-6)
    assert float(f["core_collapse_rate_total"]) == pytest.approx(
        float(f["sfr"]) * float(f["core_collapse_per_mass_formed"]), rel=1e-13)
    assert np.allclose(f["core_collapse_rate_history"], per * f["sfr_surface_density_history"], rtol=1e-6, atol=0)


# --- type Ia: the chemistry's own convolution, counted ---------------------------------------


def test_the_ia_rate_is_the_chemistrys_convolution_divided_by_the_iron_per_event(model, coarse):
    """One convolution (rule B13): the stage's history is the chemistry's DTD applied to the same
    history, times the Ia iron yield over the iron one event makes — bit for bit."""
    out = coarse[model.name]
    f, g, c = out.fields, out.grid, model.constants
    delays, weights = dtd_bins(c["DTD_MIN_DELAY"].value, g.spec.t_max, c["DTD_INDEX"].value)
    ia = snia_rate(np.asarray(f["sfr_surface_density_history"]), g.spec.t_max / g.spec.n_t, delays, weights)
    per_ia = c["Y_FE_IA"].value / c["IA_IRON_MASS"].value
    assert float(f["type_ia_per_mass_formed"]) == per_ia
    assert np.array_equal(np.asarray(f["type_ia_rate_history"]), per_ia * ia)
    assert np.array_equal(np.asarray(f["type_ia_rate"]), np.asarray(f["type_ia_rate_history"])[:, -1])
    assert float(f["type_ia_rate_total"]) == pytest.approx(sn.ring_integral(np.asarray(f["type_ia_rate"]), g.R), rel=1e-14)


def test_the_ia_history_counts_the_events_the_iron_implies(model, coarse):
    """The gate's second check: every Ia the history holds, integrated over area and time, against
    the events per unit mass formed times the mass each step formed times the analytic power law's
    share of its delays that have elapsed by today.

    The binned convolution rounds each delay to whole steps (at least one), so the two differ by
    the discretisation. Measured at S30: -6.20e-5 on this grid, +3.28e-6 on the default one."""
    out = coarse[model.name]
    f, g, c = out.fields, out.grid, model.constants
    R, t = g.R, g.t
    dt = g.spec.t_max / g.spec.n_t
    area = 2.0 * math.pi * R * g["R"].width
    events = float((np.asarray(f["type_ia_rate_history"]) * area[:, None]).sum() * dt * sn.YR_PER_GYR)
    t_min, p, T = c["DTD_MIN_DELAY"].value, 1.0 - c["DTD_INDEX"].value, g.spec.t_max
    elapsed = (np.clip(T - t, t_min, T) ** p - t_min**p) / (T**p - t_min**p)
    formed = (np.asarray(f["sfr_surface_density_history"]) * area[:, None]).sum(axis=0) * dt * sn.YR_PER_GYR
    expected = float(f["type_ia_per_mass_formed"]) * float((formed * elapsed).sum())
    assert events / expected - 1.0 == pytest.approx(-6.20e-5, abs=5e-7)
    assert abs(events / expected - 1.0) < 1e-4


# --- rows 30-31 -------------------------------------------------------------------------------


def test_the_rows_are_adams_et_al_s_intervals_converted_to_per_year():
    """3.2 +7.3 -2.6 and 1.4 +1.4 -0.8 per century (Adams et al. 2013 §III.5), nothing chosen."""
    cc, ia = (next(q for q in spec.QUANTITIES if q.n == n) for n in (spec.ROW_CORE_COLLAPSE_RATE, spec.ROW_TYPE_IA_RATE))
    assert (cc.field, cc.unit, cc.mode) == ("core_collapse_rate_total", "1/yr", "pointwise")
    assert (ia.field, ia.unit, ia.mode) == ("type_ia_rate_total", "1/yr", "pointwise")
    assert (cc.lo, cc.hi) == pytest.approx(((3.2 - 2.6) / 100, (3.2 + 7.3) / 100), abs=1e-15)
    assert (ia.lo, ia.hi) == pytest.approx(((1.4 - 0.8) / 100, (1.4 + 1.4) / 100), abs=1e-15)
    for q in (cc, ia):
        assert q.testable and "Adams et al. 2013" in q.source
        assert "3.2 +7.3 -2.6 per century" in q.note and "1.4 +1.4 -0.8 per century" in q.note


def test_both_rates_pass_and_read_the_same_in_both_models(judged):
    """Measured at S30 (default grid): core collapse 0.0176069 /yr (1.761 per century), type Ia
    0.00653320 /yr (0.653 per century, 0.053 above the window's lower edge) in both models."""
    for results in judged.values():
        r = {x.n: x for x in results}
        cc, ia = r[spec.ROW_CORE_COLLAPSE_RATE], r[spec.ROW_TYPE_IA_RATE]
        assert cc.status == "pass" and cc.value == pytest.approx(0.0176069237, rel=1e-8)
        assert ia.status == "pass" and ia.value == pytest.approx(0.0065332015, rel=1e-8)
    # Every row equal across the two models is test_sfh_azimuthal's; these two, bit for bit.
    for n in (spec.ROW_CORE_COLLAPSE_RATE, spec.ROW_TYPE_IA_RATE):
        b, a = (next(x for x in judged[name] if x.n == n) for name in ("basic", "azimuthal"))
        assert a.value == b.value
