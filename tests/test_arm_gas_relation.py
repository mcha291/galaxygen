"""The arms' molecular gas by the measured relation (S102, batch Q lane L; register #234 ruleset (ii); HELD for the owner).

Querejeta et al. 2024 (A&A 687, A293, arXiv:2405.05364), Table 4, nominal, individual spiral segments:
log10 C_mol = 1.83 log10 C_star + 0.16, each C a ratio of means - the mean in the arm footprint over the mean in the
rest of the ring (Sect. 2.7). The gas pattern sets g_mol = c^gamma / <c^gamma>_ring on every ring, c the stellar arm
pieces' field over its ring mean, gamma one exponent per galaxy solved so that the mean over the galaxy's arm rings of
the molecular ratio of means meets the relation at the stars' own (``gas_pattern.relation_exponent``). The atomic gas
keeps D216's steady response (#130); the bar's lanes are unchanged.

Judged here: the law by hand (a two-level ring, gamma analytic), the relation met on both templates, ring means 1,
the no-arms guard and the bracket's refusal, determinism. Disclosed (records, not judged): the per-ring ratio against
the relation, the crest's width against the stars', the placed field's row statistics, the star-formation contrast
against Table 4's SFR row. Production grid, as test_gas_pattern's pinned check.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import gas_check
from galaxy import templates
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import gas_pattern as gm
from galaxy.stages.gas_pattern import GAS_PATTERN_READS

TEMPLATES = ("milky_way", "ngc_4414")
SLOPE, INTERCEPT = 1.83, 0.16  # Querejeta et al. 2024, Table 4, nominal, individual segments: written here, the model's held to them
SFR_SLOPE, SFR_INTERCEPT = 2.89, 0.15  # the same table, Sigma_star - Sigma_SFR, nominal, individual segments (a record's ask only)
FIELDS = ("gas_density_contrast", "star_formation_gas_contrast", "atomic_gas_density_contrast", *GAS_PATTERN_READS)
_RUNS: dict = {}


def template_run(prod, template: str):
    if template not in _RUNS:
        _RUNS[template] = run(prod[0].get(DEFAULT_MODEL), templates.overrides(templates.TEMPLATES[template]), only=FIELDS)
    return _RUNS[template]


def pattern(prod, template: str) -> gm.GasPattern:
    o = template_run(prod, template)
    c = {k: v.value for k, v in prod[0].get(DEFAULT_MODEL).constants.items()}
    gp = compose.gas_pattern(o.fields, o.grid.R, c)
    assert gp is not None and not gp.flat and gp.relation is not None
    return gp


# --- the law by hand -------------------------------------------------------------------------------------------


def two_level(a: float, b: float, cells: int, top: int) -> tuple[np.ndarray, np.ndarray, float]:
    """A ring holding ``a`` on its first ``top`` cells and ``b`` on the rest, over its own mean; the mask the top cells."""
    c = np.full(cells, b)
    c[:top] = a
    c = c / c.mean()
    return c, c - 1.0, top / cells


@pytest.mark.parametrize("a, b, top", [(1.6, 0.9, 360), (1.3, 0.95, 288), (2.2, 0.7, 100)])
def test_the_exponent_by_hand_on_a_two_level_ring(a, b, top):
    """On a ring of two levels whose mask is exactly the upper one, the ratio of means of c^gamma is (a/b)^gamma, so the
    relation asks gamma = slope + intercept / log10(a/b): the root-find meets it to the bracket's last halving."""
    c, psi, share = two_level(a, b, gm.CELLS, top)
    gamma, met = gm.relation_exponent(c[None, :], psi[None, :], np.array([share]), SLOPE, INTERCEPT)
    assert met and gamma == pytest.approx(SLOPE + INTERCEPT / math.log10(a / b), abs=1e-10)
    g = c**gamma / gm.ring_quadrature(c**gamma)
    assert abs(gm.ring_quadrature(g) - 1.0) <= 1e-14
    assert math.log10(gm.ratio_of_means(g, psi, share)) == pytest.approx(INTERCEPT + SLOPE * math.log10(a / b), abs=1e-9)


def test_two_rings_meet_the_relation_on_their_mean():
    """Two rings: gamma meets the relation between the means of their ratios (not ring by ring) - the definition."""
    (c1, p1, s1), (c2, p2, s2) = two_level(1.6, 0.9, gm.CELLS, 360), two_level(1.2, 0.97, gm.CELLS, 360)
    gamma, met = gm.relation_exponent(np.stack([c1, c2]), np.stack([p1, p2]), np.array([s1, s2]), SLOPE, INTERCEPT)
    assert met
    stellar = 0.5 * (1.6 / 0.9 + 1.2 / 0.97)
    gas = 0.5 * ((1.6 / 0.9) ** gamma + (1.2 / 0.97) ** gamma)
    assert math.log10(gas) == pytest.approx(INTERCEPT + SLOPE * math.log10(stellar), abs=1e-9)


def test_no_arms_and_the_bracket():
    """A flat ring, or none, has no arms: (NaN, met). A field below zero is no density. A non-finite ratio fails the
    bisection's invariant and raises."""
    flat = np.ones((1, gm.CELLS))
    gamma, met = gm.relation_exponent(flat, flat - 1.0, np.array([0.25]), SLOPE, INTERCEPT)
    assert math.isnan(gamma) and met
    gamma, met = gm.relation_exponent(np.ones((0, gm.CELLS)), np.ones((0, gm.CELLS)), np.zeros(0), SLOPE, INTERCEPT)
    assert math.isnan(gamma) and met
    c, psi, share = two_level(1.6, 0.9, gm.CELLS, 360)
    with pytest.raises(ValueError, match="finite positive ratio"):
        gm.relation_exponent(np.where(np.arange(c.size) == 0, np.inf, c)[None, :], psi[None, :], np.array([share]), SLOPE, INTERCEPT)
    c, psi, share = two_level(1.6, -0.1, gm.CELLS, 360)
    with pytest.raises(ArithmeticError):
        gm.relation_exponent(c[None, :], psi[None, :], np.array([share]), SLOPE, INTERCEPT)


# Where the hold begins on a two-level ring: (a/b)^12 = 10^intercept (a/b)^slope, so a/b = 10^(intercept / (12 - slope)).
HOLD_RATIO = 10.0 ** (INTERCEPT / (12.0 - SLOPE))  # 1.0369


@pytest.mark.parametrize("a", [1.01, HOLD_RATIO * (1.0 - 1e-6)])
def test_a_weak_ring_holds_the_exponent_and_declares_the_shortfall(a):
    """The gate's ruling 2: a stellar ratio under the hold's threshold gives gamma = the bracket's top, met False, ring
    mean 1, and a molecular ratio under the relation's ask - no raise."""
    c, psi, share = two_level(a, 1.0, gm.CELLS, 360)
    gamma, met = gm.relation_exponent(c[None, :], psi[None, :], np.array([share]), SLOPE, INTERCEPT)
    assert gamma == gm.EXPONENT_BRACKET[1] and not met
    g = c**gamma / gm.ring_quadrature(c**gamma)
    assert abs(gm.ring_quadrature(g) - 1.0) <= 1e-14
    assert gm.ratio_of_means(g, psi, share) < 10.0 ** (INTERCEPT + SLOPE * math.log10(a))


@pytest.mark.parametrize("a", [HOLD_RATIO * (1.0 + 1e-6), 1.04])
def test_just_above_the_threshold_the_relation_solves(a):
    c, psi, share = two_level(a, 1.0, gm.CELLS, 360)
    gamma, met = gm.relation_exponent(c[None, :], psi[None, :], np.array([share]), SLOPE, INTERCEPT)
    assert met and gamma < gm.EXPONENT_BRACKET[1]
    assert gamma == pytest.approx(SLOPE + INTERCEPT / math.log10(a), abs=1e-9)


def test_the_constants_are_the_tables_and_the_mask_is_the_check_s(prod):
    c = prod[0].get(DEFAULT_MODEL).constants
    assert c["ARM_GAS_RELATION_SLOPE"].value == SLOPE and c["ARM_GAS_RELATION_INTERCEPT"].value == INTERCEPT
    assert c["ARM_GAS_RELATION_MASK_WIDTH"].value == gas_check.GAS_ARM_MASK_WIDTH
    assert set(gm.RELATION_CONSTANTS) <= set(gm.GAS_PATTERN_CONSTANTS)


# --- on the templates -----------------------------------------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_relation_is_met_and_every_ring_keeps_its_gas(prod, template):
    """The galaxy's molecular ratio of means over its arm rings meets Table 4 at its stars' own to 1e-6 in log; every
    published contrast averages to 1 round every ring to 1e-12; the atomic gas keeps the steady response."""
    gp = pattern(prod, template)
    rel = gp.arm_relation_ratios()
    gamma = gp.arm_gas_exponent
    assert 1.0 < gamma < 12.0 and rel["rings"].size >= 20 and gp.arm_relation_met and rel["met"]
    assert abs(math.log10(rel["molecular"]) - (INTERCEPT + SLOPE * math.log10(rel["stellar"]))) <= 1e-6
    o = template_run(prod, template)
    for name in ("gas_density_contrast", "star_formation_gas_contrast", "atomic_gas_density_contrast"):
        field = np.asarray(o.fields[name], dtype=float)
        assert np.abs(field.mean(axis=1) - 1.0).max() <= 1e-12, name
    # The molecular profiles are the relation's on every solved ring; the atomic pattern is the solver's.
    psi = gp.arms_field()
    on = gp.carries
    power = (1.0 + psi[on]) ** gamma
    assert np.array_equal(gp.profiles[on], power / gm.ring_quadrature(power)[:, None])
    atomic = gp.atomic(prod[0].get(DEFAULT_MODEL).constants["HI_DISPERSION_RATIO"].value)
    assert atomic.relation is None and math.isnan(atomic.arm_gas_exponent) and atomic.diagnostics is not None
    assert gp.diagnostics is None


def test_the_exponent_is_the_same_bits_afresh(prod):
    """Determinism: the same inputs, the caches emptied, give gamma and the profiles to the bit."""
    first = pattern(prod, "milky_way")
    gamma, profiles = first.arm_gas_exponent, first.profiles.copy()
    gm.forget_solutions()
    second = pattern(prod, "milky_way")
    assert second is not first
    assert second.arm_gas_exponent == gamma and np.array_equal(second.profiles, profiles)


def test_a_pattern_without_arms_takes_no_molecular_contrast(prod):
    """The layer off composes no pattern; a pattern whose arm rings are taken away (the taper over every ring)
    has gamma NaN and its molecular gas 1 round every ring."""
    gp = pattern(prod, "ngc_4414")
    psi = np.zeros_like(gp.stellar_sum())
    rings, _ = gp.arm_rings(psi)
    assert not rings.any() and math.isnan(gp._exponent(psi)[0]) and gp._exponent(psi)[1]
    profiles, carries = gp._relation_profiles(gp.arms_field(), math.nan)
    assert np.all(profiles == 1.0) and not carries.any()


# --- disclosed records (not judged) ----------------------------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
def test_disclosed_records(prod, template, record_property):
    """Records only: the per-ring ratio over the relation's ask; the crest's FWHM across the arm over the stars' (the
    S101 scout's power probe 0.64-0.79; Egusa et al. 2017's M51 inner arms 0.5, a check); the placed molecular field's
    row p90 / median and max / median, 5-9 kpc; the star-formation contrast's ratio of means over Table 4's SFR row."""
    gp = pattern(prod, template)
    rel = gp.arm_relation_ratios()
    ask = 10.0 ** (INTERCEPT + SLOPE * np.log10(rel["ring_stellar"]))
    over = rel["ring_molecular"] / ask
    R = gp.R
    idx = rel["rings"]
    stellar = 1.0 + gp.arms_field()
    widths = np.array([gm.crest_width(gp.profiles[i]) / gm.crest_width(stellar[i]) for i in idx])
    o = template_run(prod, template)
    edges = o.grid["phi"].edges
    placed = np.asarray(gp.unspurred_cell_means(R, edges))
    rows = (R >= 5.0) & (R <= 9.0)
    med = np.median(placed[rows], axis=1)
    sf = np.asarray(o.fields["star_formation_gas_contrast"], dtype=float)
    # The star-formation contrast on the arm rings, on the grid's phi cells, ordered by the stars' cell means.
    count = np.asarray(gp.design_count, dtype=float)
    share = gm.mask_share(np.where(count > 0, count, np.nan), R, gp.sin_pitch, gas_check.GAS_ARM_MASK_WIDTH)
    stars_cells = gp.stars.arms_at(R[:, None], (0.5 * (edges[1:] + edges[:-1]))[None, :])
    sf_ratio = np.array([gm.ratio_of_means(sf[i], stars_cells[i], float(share[i])) for i in idx])
    sfr_ask = 10.0 ** (SFR_INTERCEPT + SFR_SLOPE * np.log10(rel["ring_stellar"]))
    records = {
        "gamma": gp.arm_gas_exponent, "arm_rings": int(idx.size),
        "stellar": rel["stellar"], "molecular": rel["molecular"],
        "ring_over_ask_median_min_max": [float(np.median(over)), float(over.min()), float(over.max())],
        "fwhm_over_stellar_median_min_max": [float(np.nanmedian(widths)), float(np.nanmin(widths)), float(np.nanmax(widths))],
        "p90_over_median": float(np.median(np.percentile(placed[rows], 90, axis=1) / med)),
        "max_over_median": float(np.median(placed[rows].max(axis=1) / med)),
        "sf_ratio_over_sfr_ask_median": float(np.median(sf_ratio / sfr_ask)),
    }
    for k, v in records.items():
        record_property(k, v)
    print(template, records)
    assert np.all(np.isfinite(over)) and np.isfinite(records["p90_over_median"])
