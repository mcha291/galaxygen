"""The bright end of the disc, complete: every disc star above a luminosity (checkpoint 5, S48, D200).

The star catalogue (``systems.py``) is a *number* sample, about one star in 10⁵ of the galaxy, so the
brightest of it are the brightest of the sample, not of the galaxy. This module is the other half: a
catalogue that holds **every** disc star above a luminosity threshold, drawn from the population's
luminosity function rather than from the sample, so that what it holds plus the field's light under it
is the disc's light, exactly.

**The luminosity function** (:func:`luminosity_function`). Per isochrone, the number of stars per solar
mass formed brighter than each threshold ``L_k`` (``LOG_L_GRID``), the bolometric light they carry and
their light in each of the table's eight bands. Integrated **along the isochrone's own points**, which
are dense where the evolved phases are: the field's own quadrature (``photometry.segments``, S49 D204) -
between consecutive living points the IMF's number in the mass interval (analytic) is spread uniformly in
log L between the two ends, so the count above a threshold is continuous and monotone in it; the light and
the band fluxes of the part above it are integrated on the same segment with each quantity's logarithm
linear in the segment's parameter (log L for the light, −0.4 M for a band), exactly
(``photometry.log_linear_integral``). The stars lighter than an isochrone's first point are read at it.
Dead stars contribute nothing. So each isochrone's light and band totals (the values for L → 0) **are**
the field's tables (``photometry.population_light``), by construction: one budget, which the stars carry
(rule A9). Until S49 the field integrated on a fixed log-spaced mass grid that aliased the giant branch,
and these tables were renormalised to it per isochrone (factors 0.55 to 7.1 bolometric, 0.25 to 12 in K;
D202, debt #126); the field now integrates along the points, and the renormalisation is gone.

**The ordered process** (:func:`materialise_bright`, the stage ``bright_stars``). The unit is the finest
cell of the hierarchy (level ``MAX_LEVEL``, 65 536 of them). In a cell the expected number of stars above
L is Λ(L): the cell's area times the mass formed on each isochrone, averaged over the cell's radial span,
times ``count_above``, times the cell's azimuthal weight — the pattern's density contrast for stars older
than ``systems.YOUNG_STAR_AGE`` and, where the model publishes it, ``sfr_modulation`` for the younger ones.
The cell's stars are a Poisson process in luminosity, ordered: star i has Γ_i = E_0 + … + E_i (unit
exponentials by inverse CDF from the cell's own stream), and Γ_i fixes its **threshold interval** - the pair
of grid thresholds its luminosity lies between, from Λ at the thresholds - so the stars above any grid
threshold are exactly those with Γ_i < Λ(threshold): a higher grid threshold is a prefix in Γ order, the
count above it is Poisson with mean Λ, and a cell's stars do not depend on which other cells were asked for
(D60). **Within its interval** (D203) the star's age part, isochrone and segment are drawn by their exact star
counts in the interval, and its luminosity uniformly in log L across the segment's overlap with the
interval, so every linear quantity of the realised stars - count, bolometric light, each band - has the
budget's expectation; until D203 the luminosity was Λ⁻¹(Γ_i) read log-linearly across the interval and the
segment chosen by its density there, which under-drew the hot segments where an isochrone's count is not
log-linear inside an interval (B 0.83 of the budget above 10⁴ L☉). The cost: the prefix is exact at the
grid's thresholds (every 0.05 dex), not inside an interval; a threshold inside one is served by drawing to
the interval's lower threshold and keeping the stars above it, so every star above it is still there. Each
star's age, mass, phase, magnitudes and place come from its own streams by inverse CDFs (rule B8). Stars younger than the cluster census's window (its blown-open and
dispersing phases, 20 Myr) are the census's, not this catalogue's; the bulge is not covered and stays in
the field.

**The decomposition** (:func:`isochrone_weights`, :func:`mass_on_isochrones`). The light stage reads
each history step's light as a per-isochrone table pushed through ``on_fine_ages``,
``cumulative_over_age`` and ``steps_over``, all linear in the table; pushing the identity through them
gives the weight each step puts on each isochrone age, so the mass formed on every (age, metallicity)
isochrone is a matrix product, and ``mass @ light_per_mass`` is ``disc_surface_brightness`` to rounding
(``tests/test_bright.py``). An age window is applied in step space: a step that straddles a boundary is
split into its parts, each part's weights computed over its own sub-interval and scaled by its share of
the step, so the parts sum to the step exactly.

**The field's remainder** (:func:`resolve`, S48's wiring). The same decomposition in three age parts
(:func:`part_masses`: the cluster census's, the catalogue's 20–100 Myr part, the older) and the same tables read
at a threshold by the same rule (:func:`above_at`) split each ring's light into what the cluster points carry,
what the bright catalogue carries and what neither does, which ``/api/render`` serves with ``l_min=`` beside the
stars, each part placed around its ring by the weight the catalogue gives it (:func:`part_weights`). The three are
the total exactly, per ring and band.
"""

from __future__ import annotations

import functools
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.cmaps import BLACKBODY_KELVIN
from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.grids import Axis
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.pattern import PATTERN_READS, invert_azimuths
from galaxy.stages.systems import (
    CELL_COUNT,
    CELL_SECTORS,
    MAX_LEVEL,
    YOUNG_STAR_AGE,
    Catalogue,
    Modulation,
    cell_edges,
    children_per_cell,
    sech2_height,
)
from galaxy.stages.vertical import POPULATIONS
from galaxy.stages.photometry import (
    BANDS,
    EXTRA,
    band_nu_l_nu,
    cumulative_over_age,
    Segments,
    isochrones,
    log_linear_integral,
    nearest_metallicity,
    on_fine_ages,
    population_light,
    segments,
    steps_over,
)

# Luminosity thresholds, log10 L/L☉ bolometric, every 0.05 dex from 0.1 L☉ to 4 × 10⁶ L☉: past the
# brightest point of the youngest isochrone the catalogue covers.
LOG_L_GRID = np.linspace(-1.0, 6.6, 153)


def _above(log_l: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(a, b): per segment (rows) and threshold (columns), the sub-interval of s ∈ [0, 1] on which
    log L(s) > x. Empty intervals have a == b. A segment flat in L is all above or all below."""
    y0, y1 = log_l[:, 0:1], log_l[:, 1:2]
    d = y1 - y0
    flat = d == 0.0
    s = np.clip((x[None, :] - y0) / np.where(flat, 1.0, d), 0.0, 1.0)
    rising = d > 0.0
    a = np.where(rising, s, 0.0)
    b = np.where(rising, 1.0, np.where(flat, 0.0, s))
    above_flat = y0 > x[None, :]
    a = np.where(flat, 0.0, a)
    b = np.where(flat, np.where(above_flat, 1.0, 0.0), b)
    return a, b


@dataclass(frozen=True)
class BrightTables:
    """Per isochrone ``(n_age, n_mh)`` and threshold ``LOG_L_GRID``: what lies above each threshold, per M☉ formed.

    ``count_above``, ``light_above`` and ``band_above`` are non-increasing in L. ``count_total``,
    ``light_total`` and ``band_total`` are every living star's (L → 0, below the grid's faint end too): the
    light and band totals are the field's ``light_per_mass`` and ``band_flux``, one quadrature (S49, D204).
    """

    log_l: np.ndarray  # (K,)
    count_above: np.ndarray  # (n_age, n_mh, K) stars per M☉ formed with L > L_k
    light_above: np.ndarray  # (n_age, n_mh, K) L☉ per M☉ formed from those stars
    band_above: np.ndarray  # (n_age, n_mh, K, 8) Σ 10^(−0.4 M_band) per M☉ formed from those stars
    count_total: np.ndarray  # (n_age, n_mh)
    light_total: np.ndarray  # (n_age, n_mh)
    band_total: np.ndarray  # (n_age, n_mh, 8)


@functools.cache
def luminosity_function() -> BrightTables:
    """The per-isochrone tables of what lies above each threshold: see the module docstring."""
    tab = isochrones()
    x = LOG_L_GRID
    shape = (tab.log_ages.size, tab.mhs.size)
    count = np.zeros((*shape, x.size))
    light = np.zeros((*shape, x.size))
    bands = np.zeros((*shape, x.size, len(BANDS)))
    count_total = np.zeros(shape)
    totals = np.zeros((*shape, 1 + len(BANDS)))
    for (age, mh) in tab.tracks:
        seg = segments(age, mh)
        above_n, above_q, totals[age, mh] = _above_sums(seg, x)
        count[age, mh] = above_n
        count_total[age, mh] = float(seg.number.sum())
        light[age, mh] = above_q[:, 0]
        bands[age, mh] = above_q[:, 1:]
    return BrightTables(x, count, light, bands, count_total, totals[..., 0], totals[..., 1:])


def _above_sums(seg: Segments, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(count (K,), quantities (K, 9), totals (9,)) of one isochrone above each threshold ``x``; the nine
    quantities are the light and the eight band fluxes. A segment wholly above a threshold adds its whole
    integral (a suffix sum over the segments sorted by their faint end); only the thresholds a segment
    straddles are integrated in part (:func:`_above`'s reading, done sparsely: a segment spans a few)."""
    y0, y1 = seg.log_l[:, 0], seg.log_l[:, 1]
    lo, hi, d = np.minimum(y0, y1), np.maximum(y0, y1), y1 - y0
    g0 = np.concatenate([y0[:, None], seg.neg_mag[:, 0, :]], axis=1)  # log10 of each quantity at s = 0
    g1 = np.concatenate([y1[:, None], seg.neg_mag[:, 1, :]], axis=1)
    full = seg.number[:, None] * log_linear_integral(g0, g1, 0.0, 1.0)  # (n, 9)
    order = np.argsort(lo, kind="stable")
    suffix_n = np.concatenate([np.cumsum(seg.number[order][::-1])[::-1], [0.0]])
    suffix_q = np.concatenate([np.cumsum(full[order][::-1], axis=0)[::-1], np.zeros((1, full.shape[1]))])
    start = np.searchsorted(lo[order], x, side="right")  # the first segment whose faint end is not above x
    count, quant = suffix_n[start].copy(), suffix_q[start].copy()
    # The straddled thresholds: lo <= x_k < hi (none for a segment flat in L).
    first = np.searchsorted(x, lo, side="left")
    many = np.maximum(np.searchsorted(x, hi, side="left") - first, 0)
    j = np.repeat(np.arange(lo.size), many)
    k = first[j] + np.arange(j.size) - np.repeat(np.cumsum(many) - many, many)
    s = (x[k] - y0[j]) / d[j]
    rising = d[j] > 0.0
    a, b = np.where(rising, s, 0.0), np.where(rising, 1.0, s)
    np.add.at(count, k, seg.number[j] * (b - a))
    np.add.at(quant, k, seg.number[j, None] * log_linear_integral(g0[j], g1[j], a[:, None], b[:, None]))
    return count, quant, full.sum(axis=0)


# --- the decomposition: the mass formed on each isochrone ---------------------------------------------


@functools.cache
def _identity_cumulative() -> np.ndarray:
    """(1, n_fine, n_age): the identity per-isochrone table through ``on_fine_ages`` and
    ``cumulative_over_age``, one metallicity row (every row of it would be the same)."""
    n_age = isochrones().log_ages.size
    eye = np.eye(n_age)[:, None, :]  # (n_age, 1, n_age): isochrone a's table is 1 at a, 0 elsewhere
    return cumulative_over_age(on_fine_ages(eye))


def _step_ages(t_max: float, n_t: int) -> tuple[np.ndarray, float]:
    """Each step's youngest age (Gyr) and the step's width, as the light stage takes them."""
    t = Axis("t", "Gyr", int(n_t), 0.0, float(t_max)).centres
    dt = float(t_max) / float(n_t)
    return float(t_max) - (t + 0.5 * dt), dt


@functools.lru_cache(maxsize=16)
def isochrone_weights(t_max: float, n_t: int, age_min_gyr: float = 0.0, age_max_gyr: float = math.inf) -> np.ndarray:
    """(n_t, n_age): the weight each history step puts on each isochrone age, per unit mass formed.

    The identity table pushed through the light stage's own functions, so for any per-isochrone table
    ``q`` (n_age, n_mh) ``steps_over``'s reading of it at metallicity ``z`` is ``weights @ q[:, z]`` to
    rounding. With an age window [``age_min_gyr``, ``age_max_gyr``) only the part of each step inside it
    counts: a straddling step's weights are computed over the sub-interval inside and scaled by its share
    of the step, so the windows of a partition sum to the whole exactly.
    """
    lo, dt = _step_ages(t_max, n_t)
    hi = lo + dt
    table = _identity_cumulative()
    floor = isochrones().mhs[0]  # the one row's metallicity: steps_over reads it at index 0
    feh = np.full(lo.size, floor)
    if age_min_gyr <= 0.0 and not math.isfinite(age_max_gyr):
        return steps_over(table, lo, hi, feh)
    a = np.clip(lo, age_min_gyr, age_max_gyr)
    b = np.clip(hi, age_min_gyr, age_max_gyr)
    share = (b - a) / dt
    whole = share >= 1.0
    out = np.zeros((lo.size, table.shape[-1]))
    if whole.any():
        out[whole] = steps_over(table, lo[whole], hi[whole], feh[whole])
    part = (share > 0.0) & ~whole
    if part.any():
        out[part] = steps_over(table, a[part], b[part], feh[part]) * share[part, None]
    return out


def mass_on_isochrones(
    formed: np.ndarray,
    feh_history: np.ndarray,
    t_max: float,
    n_t: int,
    *,
    age_min_gyr: float = 0.0,
    age_max_gyr: float = math.inf,
) -> np.ndarray:
    """(n_R, n_age, n_mh): M☉ formed per pc² on each isochrone, of the stars whose age is in the window.

    ``formed`` is the mass formed per step (M☉/pc², axes (R, t)); each step's mass goes to the
    isochrone ages by :func:`isochrone_weights` and to the metallicity ``steps_over`` reads its
    ``feh_history`` at (:func:`photometry.nearest_metallicity`, the same rule).
    """
    formed = np.asarray(formed, dtype=float)
    w = isochrone_weights(float(t_max), int(n_t), float(age_min_gyr), float(age_max_gyr))  # (n_t, n_age)
    mh = nearest_metallicity(feh_history)  # (n_R, n_t)
    n_mh = isochrones().mhs.size
    out = np.zeros((formed.shape[0], w.shape[1], n_mh))
    for z in range(n_mh):
        on = mh == z
        if on.any():
            out[:, :, z] = np.where(on, formed, 0.0) @ w
    return out


# The three age parts every decomposition here uses, in this order: the cluster census's (younger than its window),
# the bright catalogue's young part (the window to ``YOUNG_STAR_AGE``, placed by sfr_modulation where the model
# publishes it) and its old part (older, placed by the pattern's contrast).
AGE_PARTS: tuple[str, ...] = ("young", "middle", "old")


def part_masses(fields: Mapping[str, Any], t_max: float, n_t: int, constants: Mapping[str, Any]) -> np.ndarray:
    """(3, n_R, n_age, n_mh): M☉ formed per pc² on each isochrone in each of ``AGE_PARTS``, from the history the light
    stage reads (``stars_formed_history`` over 1 − R, ``feh_history``). The windows split steps in step space, so the
    three sum to :func:`mass_on_isochrones` of the whole history; the few 1e-16 negatives the fine-age reading leaves
    are clipped. One copy: the bright catalogue's tables and ``/api/render``'s unresolved remainder both read it."""
    formed = np.asarray(fields["stars_formed_history"], dtype=float) / (1.0 - float(constants["RETURN_FRACTION"]))
    feh = fields["feh_history"]
    cut = cluster_window(constants)
    parts = [
        mass_on_isochrones(formed, feh, t_max, n_t, age_max_gyr=cut),
        mass_on_isochrones(formed, feh, t_max, n_t, age_min_gyr=cut, age_max_gyr=YOUNG_STAR_AGE),
        mass_on_isochrones(formed, feh, t_max, n_t, age_min_gyr=YOUNG_STAR_AGE),
    ]
    return np.maximum(np.stack(parts), 0.0)


def part_weights(contrast: np.ndarray, modulation: np.ndarray | None) -> np.ndarray:
    """(2, n_rings, n_sectors): the azimuthal weights of the ``middle`` and ``old`` parts around each ring. The old
    part follows the pattern's density ``contrast``; the middle part follows ``modulation`` (where stars form today)
    normalised to its ring mean, so each ring keeps its light, or the contrast where the model publishes none. Floored
    at zero. One rule for the bright catalogue's finest cells and for the render's grid cells."""
    contrast = np.asarray(contrast, dtype=float)
    if modulation is None:
        young = contrast
    else:
        young = np.asarray(modulation, dtype=float)
        mean = young.mean(axis=1, keepdims=True)
        young = np.where(mean > 0.0, young / np.where(mean > 0.0, mean, 1.0), 1.0)
    return np.maximum(np.stack([young, contrast]), 0.0)


def above_at(mass: np.ndarray, table: np.ndarray, log_l: float) -> np.ndarray:
    """``(..., *q)``: what lies above 10^``log_l`` L☉ of the stars formed on the isochrones (``mass``,
    ``(..., n_age, n_mh)`` M☉) by a per-isochrone table above each threshold (``table``, ``(n_age, n_mh, K, *q)`` per
    M☉ formed: a :class:`BrightTables` member). The summed curve read between the thresholds by the rule the
    catalogue's expected counts are (:func:`_bracket`, :func:`_between`); exact at a grid threshold."""
    k, frac = _bracket(log_l)
    k = int(k)
    m = np.asarray(mass, dtype=float)
    m = m.reshape(*m.shape[:-2], -1)
    t = np.asarray(table, dtype=float)
    t = t.reshape(-1, *t.shape[2:])
    return _between(np.tensordot(m, t[:, k], axes=1), np.tensordot(m, t[:, k + 1], axes=1), float(frac))


# What :func:`resolve` reads of the bright stage's inputs: the history it decomposes, and where stars form today
# (optional) for the middle part's weight. /api/render reads these with l_min= (rule D4: no more of the stage).
RESOLVE_READS: tuple[str, ...] = ("stars_formed_history", "feh_history", "sfr_modulation")


@dataclass(frozen=True)
class Resolved:
    """The disc's light per ring split at a luminosity (S48's wiring, D200 (4)): what the cluster census carries
    (``young``, every star younger than its window), what the bright catalogue carries (its two parts' stars above the
    threshold) and what neither does (``unresolved_middle``, ``unresolved_old``: the field's remainder, each part
    placed around the ring by its own weight). All from one decomposition and one set of tables, so
    unresolved + young + bright is the total exactly; the bright parts are what the catalogue's stars carry, the
    luminosity function's totals being the field's own tables (one quadrature, S49 D204)."""

    log_l: float  # log10 of the threshold applied, L☉ (the requested one, raised to the grid's faint end)
    anchors: dict[str, np.ndarray]  # (n_R, 8): λL_λ at the table's eight bands, L☉/pc²
    light: dict[str, np.ndarray]  # (n_R,): bolometric, L☉/pc²


def resolve(fields: Mapping[str, Any], t_max: float, n_t: int, constants: Mapping[str, Any], l_min: float) -> Resolved:
    """Split the disc's light at ``l_min`` L☉: see :class:`Resolved`. Anchors ``total``, ``young``, ``bright_middle``,
    ``bright_old``, ``unresolved_middle``, ``unresolved_old``; light ``total``, ``young``, ``bright``, ``unresolved``. The threshold is read on ``LOG_L_GRID`` by :func:`above_at` (the catalogue's rule), per ring and
    part."""
    tables = luminosity_function()
    pop = population_light()
    masses = part_masses(fields, t_max, n_t, constants)  # (3, n_R, n_age, n_mh)
    log_l = math.log10(max(float(l_min), 10.0 ** LOG_L_GRID[0]))
    flat = masses.reshape(*masses.shape[:2], -1)
    bands = flat @ pop.band_flux.reshape(-1, len(BANDS))  # (3, n_R, 8): every living star of each part
    light = flat @ pop.light_per_mass.ravel()  # (3, n_R)
    bright_bands = above_at(masses[1:], tables.band_above, log_l)  # (2, n_R, 8): what lies above l_min
    bright_light = above_at(masses[1:], tables.light_above, log_l)  # (2, n_R)

    def anchors(flux: np.ndarray) -> np.ndarray:
        return np.stack([band_nu_l_nu(flux[..., k], b) for k, b in enumerate(BANDS)], axis=-1)

    return Resolved(
        log_l=log_l,
        anchors={
            "total": anchors(bands.sum(axis=0)),
            "young": anchors(bands[0]),
            "bright_middle": anchors(bright_bands[0]),
            "bright_old": anchors(bright_bands[1]),
            "unresolved_middle": anchors(bands[1] - bright_bands[0]),
            "unresolved_old": anchors(bands[2] - bright_bands[1]),
        },
        light={
            "total": light.sum(axis=0),
            "young": light[0],
            "bright": bright_light.sum(axis=0),
            "unresolved": (light[1:] - bright_light).sum(axis=0),
        },
    )


# --- the ordered process: every disc star above a threshold, per finest cell ---------------------------

DEFAULT_SELECTION = 3162  # the default run's selection: the viewer's default N (10^3.5 stars)
# What /api/bright's header says of its prefix (D203): exact at the grid's thresholds, a request inside an
# interval drawn to the interval's lower threshold and cut at its own luminosity.
PREFIX = "by interval: a higher grid threshold (every 0.05 dex) keeps a prefix of each cell's Gamma order"
BISECTION_STEPS = 60  # halvings of the one 0.05-dex interval that brackets a count: below a float's step
MAX_PASSES = 8  # threshold-lowering passes when a realisation falls short of n (A1: bounded)
RADIUS_STEPS = 8  # intervals a star's radius is inverted over across its cell's span
AZIMUTH_STEPS = 24  # and its azimuth (as the catalogue's)
CELL_SAMPLES = 8  # radii a cell's mass on the isochrones is averaged at, area-weighted
# PARSEC's evolutionary-phase labels 0-8, in order [recall: the CMD output documentation, as massive_stars
# reads labels 0 and 1]: the table's own vocabulary, every label the committed isochrones carry.
PHASES: tuple[str, ...] = (
    "pre_main_sequence", "main_sequence", "subgiant", "red_giant", "core_helium_burning",
    "blue_loop", "red_loop", "early_agb", "thermally_pulsing_agb",
)
STREAMS: tuple[str, ...] = ("population", "age", "segment", "luminosity", "radius", "azimuth", "height")


def cluster_window(constants: Mapping[str, Any]) -> float:
    """Gyr: the ages the cluster census holds (its clouds' blown-open and dispersing phases), which the
    bright catalogue leaves to it so that no star is counted twice."""
    return (float(constants["GMC_PHASE_BLOWN_OPEN"]) + float(constants["GMC_PHASE_DISPERSING"])) / 1000.0


def _bracket(log_l: float | np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(k, frac): the threshold interval [x_k, x_k+1] holding each log L and the way across it; below the
    grid the first point, above it the last interval's end."""
    x = LOG_L_GRID
    v = np.clip(np.asarray(log_l, dtype=float), x[0], x[-1])
    k = np.clip(np.searchsorted(x, v, side="right") - 1, 0, x.size - 2)
    return k, (v - x[k]) / (x[k + 1] - x[k])


def _between(a: np.ndarray, b: np.ndarray, frac: np.ndarray) -> np.ndarray:
    """A non-increasing curve read between two thresholds: log-linear in L where both ends hold something,
    linear to zero across the last occupied interval, zero past it: the expected count between thresholds."""
    a, b, frac = np.broadcast_arrays(np.asarray(a, dtype=float), np.asarray(b, dtype=float), np.asarray(frac, dtype=float))
    both = (a > 0.0) & (b > 0.0)
    safe_a, safe_b = np.where(both, a, 1.0), np.where(both, b, 1.0)
    logged = np.exp(np.log(safe_a) + frac * (np.log(safe_b) - np.log(safe_a)))
    return np.where(both, logged, np.where(a > 0.0, a * (1.0 - frac), 0.0))


class BrightGalaxy:
    """Everything one galaxy's bright catalogue reads, tabulated once over every finest cell (D60: no table
    depends on which cells a request names).

    Two age parts, each with its own azimuthal weight: ``0`` from the cluster window to
    ``YOUNG_STAR_AGE`` (placed by ``sfr_modulation`` where the model publishes it, by the contrast where it
    does not) and ``1`` older (by the contrast). A finest cell is one of 256 rings by 256 sectors.
    """

    def __init__(self, fields: Mapping[str, Any], R: np.ndarray, t: np.ndarray, t_max: float, n_t: int,
                 constants: Mapping[str, Any]) -> None:
        tables = luminosity_function()
        self.R, self.t, self.t_max = np.asarray(R, dtype=float), np.asarray(t, dtype=float), float(t_max)
        n_iso = tables.count_above.shape[0] * tables.count_above.shape[1]
        self.n_mh = tables.count_above.shape[1]
        K = LOG_L_GRID.size
        self.cut = cluster_window(constants)
        # The two parts older than the cluster window, in step space (part_masses: the young part is the census's).
        mass_R = part_masses(fields, t_max, n_t, constants)[1:].reshape(2, self.R.size, n_iso)  # M☉/pc² per isochrone
        self.windows = np.log10(np.array([[self.cut, YOUNG_STAR_AGE], [YOUNG_STAR_AGE, self.t_max]]) * 1e9)
        count = tables.count_above.reshape(n_iso, K)
        self.count_R = mass_R @ count  # (2, n_R, K): stars per pc² above each threshold
        # The finest cells: 2^MAX_LEVEL sub-rings and sub-sectors of every level-0 cell, cut as cell_bounds cuts.
        n = 1 << MAX_LEVEL
        rings32, sectors32 = cell_edges(self.R)
        frac = np.arange(n + 1) / n
        r_edges = rings32[:-1, None] + (rings32[1:] - rings32[:-1])[:, None] * frac[None, :]
        p_edges = sectors32[:-1, None] + (sectors32[1:] - sectors32[:-1])[:, None] * frac[None, :]
        self.ring_lo, self.ring_hi = r_edges[:, :-1].ravel(), r_edges[:, 1:].ravel()
        self.sector_lo, self.sector_hi = p_edges[:, :-1].ravel(), p_edges[:, 1:].ravel()
        # Each cell's mean over its radial span: the per-radius tables read linearly at CELL_SAMPLES
        # midpoints, weighted by radius (area). One matrix, so every table is averaged the same way.
        u = (np.arange(CELL_SAMPLES) + 0.5) / CELL_SAMPLES
        radii = self.ring_lo[:, None] + (self.ring_hi - self.ring_lo)[:, None] * u[None, :]
        average = np.zeros((self.ring_lo.size, self.R.size))
        weight = radii / radii.sum(axis=1, keepdims=True)
        i0 = np.clip(np.searchsorted(self.R, radii) - 1, 0, self.R.size - 2)
        w1 = np.clip((radii - self.R[i0]) / (self.R[i0 + 1] - self.R[i0]), 0.0, 1.0)
        rows = np.repeat(np.arange(self.ring_lo.size), CELL_SAMPLES)
        np.add.at(average, (rows, i0.ravel()), (weight * (1.0 - w1)).ravel())
        np.add.at(average, (rows, i0.ravel() + 1), (weight * w1).ravel())
        self.mass_cell = np.einsum("cr,prx->pcx", average, mass_R)  # (2, 256, n_iso) M☉/pc²
        self.count_cell = self.mass_cell @ count  # (2, 256, K)
        self.light_cell = self.mass_cell @ tables.light_above.reshape(n_iso, K)
        self.count_iso = count  # (n_iso, K)
        dphi = 2.0 * math.pi / (CELL_SECTORS * n)
        self.area = 0.5 * (self.ring_hi**2 - self.ring_lo**2) * dphi * PC_PER_KPC**2  # pc² per cell, by ring
        # The azimuthal weights per (ring, sector): the contrast averaged over the cell at its middle radius,
        # and the modulation normalised to its ring mean (as the catalogue's young stars read it).
        edges = np.concatenate([self.sector_lo, self.sector_hi[-1:]])
        middle = 0.5 * (self.ring_lo + self.ring_hi)
        # Both weights come from compose (S55, D214): no pattern and no modulation with the layer off, and then
        # every sector of a ring holds the same share - each ring's expected count is what it was (I2).
        self.pattern = _compose.stellar_pattern(fields, self.R)
        flat = self.pattern is None or self.pattern.flat
        contrast = np.ones((middle.size, edges.size - 1)) if flat else np.array([self.pattern.sector_means(float(r), edges) for r in middle])
        table = _compose.placement_weight(fields, "sfr_modulation")
        # S59 (D218, the gate's follow-up, item 1): the modulation's rows are read at the point's own winding
        # coordinate, by the winding of the pattern compose has just given - the reader the star sample uses.
        self.modulation = None if table is None else Modulation(table, self.R, self.pattern)
        young = None if self.modulation is None else np.array([self.modulation.sector_means(float(r), edges) for r in middle])
        self.weights = part_weights(contrast, young)  # (2, 256, 256)
        # What the height reads: the thin/thick criterion over (radius, birth time), the two scale heights.
        self.thick = np.asarray(fields["birth_population"], dtype=np.int64) == POPULATIONS.index("thick")
        self.h_thin = float(fields["thin_disc_scale_height"]) / PC_PER_KPC
        self.h_thick = float(fields["thick_disc_scale_height"]) / PC_PER_KPC or self.h_thin

    # --- where a finest cell is ---

    @staticmethod
    def locate(cells: Sequence[int] | np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(ring, sector) of each finest cell among the 256 x 256, from its level-MAX_LEVEL id."""
        cells = np.asarray(cells, dtype=np.int64)
        n = 1 << MAX_LEVEL
        parent, q = np.divmod(cells, children_per_cell(MAX_LEVEL))
        ring32, sector32 = np.divmod(parent, CELL_SECTORS)
        a, b = np.divmod(q, n)
        return ring32 * n + a, sector32 * n + b

    # --- the expected counts and light ---

    def curves(self, cells: Sequence[int] | np.ndarray, table: str = "count") -> np.ndarray:
        """(n_cells, K): each cell's expected number of stars above each threshold (``table="count"``), or
        their light (``"light"``)."""
        ring, sector = self.locate(cells)
        tab = {"count": self.count_cell, "light": self.light_cell}[table]
        return self.area[ring, None] * (
            tab[0, ring] * self.weights[0, ring, sector][:, None] + tab[1, ring] * self.weights[1, ring, sector][:, None]
        )

    def at_threshold(self, cells: Sequence[int] | np.ndarray, k: int) -> np.ndarray:
        """Each cell's expected number of stars above the grid threshold ``LOG_L_GRID[k]``, exactly as
        :meth:`curves` holds it: what Γ is compared with at a grid threshold (D203)."""
        ring, sector = self.locate(cells)
        j = int(k)
        return self.area[ring] * (self.count_cell[0, ring, j] * self.weights[0, ring, sector] + self.count_cell[1, ring, j] * self.weights[1, ring, sector])

    def expected(self, cells: Sequence[int] | np.ndarray, log_l: float, table: str = "count") -> np.ndarray:
        """Each cell's curve read at one log L, between the thresholds as :func:`_between` reads it."""
        ring, sector = self.locate(cells)
        k, frac = _bracket(log_l)
        tab = {"count": self.count_cell, "light": self.light_cell}[table]

        def at(j: int) -> np.ndarray:
            return self.area[ring] * (tab[0, ring, j] * self.weights[0, ring, sector] + tab[1, ring, j] * self.weights[1, ring, sector])

        return _between(at(int(k)), at(int(k) + 1), float(frac))

    def threshold(self, cells: Sequence[int] | np.ndarray, target: float) -> float:
        """log L at which the expected count over ``cells`` is ``target``, by bisection on the monotone count
        (rule A1: a fixed number of halvings); the grid's faint end if even that holds fewer."""
        cells = np.asarray(cells, dtype=np.int64)
        x = LOG_L_GRID
        ring, sector = self.locate(cells)
        # The summed curve at the thresholds brackets the answer; the bisection runs inside that one interval.
        w = [np.bincount(ring, weights=self.weights[p, ring, sector], minlength=self.area.size) for p in (0, 1)]
        total = (self.area[:, None] * (self.count_cell[0] * w[0][:, None] + self.count_cell[1] * w[1][:, None])).sum(axis=0)
        if total[0] <= target:
            return float(x[0])
        k = min(int(np.flatnonzero(total > target)[-1]), x.size - 2)
        a = self.area[ring] * (self.count_cell[0, ring, k] * self.weights[0, ring, sector] + self.count_cell[1, ring, k] * self.weights[1, ring, sector])
        b = self.area[ring] * (self.count_cell[0, ring, k + 1] * self.weights[0, ring, sector] + self.count_cell[1, ring, k + 1] * self.weights[1, ring, sector])
        lo, hi = 0.0, 1.0
        for _ in range(BISECTION_STEPS):
            mid = 0.5 * (lo + hi)
            if float(_between(a, b, mid).sum()) > target:
                lo = mid
            else:
                hi = mid
        return float(x[k] + lo * (x[k + 1] - x[k]))


def _gammas(seed: int, cell: int, ceiling: float) -> np.ndarray:
    """Γ_0 < Γ_1 < … below ``ceiling``: the running sum of unit exponentials, each the inverse CDF of one
    uniform of the cell's own stream (rule B8). Drawn in a block sized to hold them with room; a block that
    does not reach the ceiling is drawn again twice as long from the same stream, whose prefix is the same."""
    size = int(ceiling + 5.0 * math.sqrt(ceiling) + 8.0)
    while True:
        u = _seeds.rng(seed, "bright", int(cell), "gamma").random(size)
        gamma = np.cumsum(-np.log1p(-u))
        if gamma[-1] >= ceiling:
            return gamma[gamma < ceiling]
        size *= 2


def interval_of(l_min: float) -> int:
    """The threshold interval holding ``l_min`` (L☉): the index k of the grid threshold at or below it, the one
    the catalogue draws to before cutting at ``l_min`` itself (D203: the prefix is exact at grid thresholds)."""
    k, _ = _bracket(math.log10(max(float(l_min), 10.0 ** LOG_L_GRID[0])))
    return int(k)


def draw_bright(galaxy: BrightGalaxy, seed: int, cells: Sequence[int], k: int) -> Catalogue:
    """Every disc star older than the cluster window above the grid threshold ``LOG_L_GRID[k]`` in the finest
    ``cells``, in each cell's Γ order (``rank`` 0, 1, …): the stars with Γ_i below the cell's expected count at
    that threshold, exactly. Γ_i fixes the star's interval — the pair of grid thresholds its luminosity lies
    between, by the cell's expected count at the thresholds — and the order between intervals; within its
    interval the star's part, isochrone and segment are drawn by their exact counts in the interval and its
    luminosity uniformly in log L across the segment's overlap with it (D203). Besides the declared columns each
    row carries ``cell``, ``rank`` and ``gamma`` (what a cache cuts a prefix by)."""
    cells = [int(c) for c in cells]
    ceilings = galaxy.at_threshold(cells, int(k)) if cells else np.zeros(0)
    drawn = [(c, _gammas(seed, c, float(lam))) if lam > 0.0 else (c, np.zeros(0)) for c, lam in zip(cells, ceilings)]
    drawn = [(c, g) for c, g in drawn if g.size]
    counts = tuple((c, int(g.size)) for c, g in drawn)
    if not drawn:
        return Catalogue.of(_empty(), ())
    cell = np.concatenate([np.full(g.size, c, dtype=np.int64) for c, g in drawn])
    rank = np.concatenate([np.arange(g.size, dtype=np.int64) for _, g in drawn])
    gamma = np.concatenate([g for _, g in drawn])
    curves = galaxy.curves([c for c, _ in drawn])
    # The interval: the last threshold whose expected count is at least Γ (the curve is non-increasing).
    interval = np.concatenate([
        np.clip((curves[j][None, :] >= g[:, None]).sum(axis=1) - 1, 0, LOG_L_GRID.size - 2) for j, (_, g) in enumerate(drawn)
    ])
    u = {name: np.concatenate([_seeds.rng(seed, "bright", c, name).random(g.size) for c, g in drawn]) for name in STREAMS}
    out = _properties(galaxy, cell, interval, u)
    out.update({"cell": cell, "rank": rank, "gamma": gamma})
    return Catalogue.of(out, counts)


def cut_bright(drawn: Catalogue, galaxy: BrightGalaxy, l_min: float) -> Catalogue:
    """The stars of a :func:`draw_bright` catalogue (each cell's rows in Γ order, drawn to a grid threshold at or
    below ``l_min``'s interval) brighter than ``l_min``: in each cell the Γ prefix of ``l_min``'s interval, then
    those of its stars above ``l_min`` itself, brightest first within each cell. Every disc star above ``l_min``
    in the cells is in it."""
    if not drawn.counts:
        return Catalogue.of(_empty(), ())
    k = interval_of(l_min)
    cell_ids = [c for c, _ in drawn.counts]
    ceiling = np.repeat(galaxy.at_threshold(cell_ids, k), [n for _, n in drawn.counts])
    position = np.repeat(np.arange(len(cell_ids)), [n for _, n in drawn.counts])
    lum = np.asarray(drawn["bright_star_luminosity"], dtype=float)
    keep = np.flatnonzero((np.asarray(drawn["gamma"]) < ceiling) & (lum > float(l_min)))
    keep = keep[np.lexsort((-lum[keep], position[keep]))]
    held = np.bincount(position[keep], minlength=len(cell_ids))
    counts = tuple((c, int(n)) for c, n in zip(cell_ids, held) if n)
    return Catalogue.of({name: np.asarray(col)[keep] for name, col in drawn.items()}, counts)


def materialise_bright(galaxy: BrightGalaxy, seed: int, cells: Sequence[int], l_min: float) -> Catalogue:
    """Every disc star above ``l_min`` (L☉) older than the cluster window, in the finest ``cells``: drawn to the
    grid threshold of ``l_min``'s interval and cut at ``l_min`` (:func:`draw_bright`, :func:`cut_bright`). Rows are
    grouped by cell in the order asked, brightest first within each; ``rank`` is the star's place in its cell's Γ
    order, which a lower threshold does not change."""
    return cut_bright(draw_bright(galaxy, seed, cells, interval_of(l_min)), galaxy, l_min)


def _empty() -> dict[str, np.ndarray]:
    e = np.zeros(0)
    cols = {d.name: (e.astype(np.int64) if d.kind is Kind.CATEGORY_COLUMN else e) for d in COLUMNS}
    return cols | {"cell": e.astype(np.int64), "rank": e.astype(np.int64), "gamma": e}


def on_isochrone(iso: int, k: np.ndarray, u_segment: np.ndarray, u_luminosity: np.ndarray, n_mh: int) -> dict[str, np.ndarray]:
    """Stars of one isochrone in threshold intervals ``k``: each star's segment by the segments' exact counts in its
    interval (an inverse CDF), its log L uniform across that segment's overlap with the interval, and its initial
    mass, log T_eff, eight magnitudes and phase read at that point of the segment (D203). ``fallback`` marks a star
    whose isochrone holds no star in its interval to the tables' rounding (it is put at the interval's middle on the
    segment nearest it)."""
    seg = segments(*divmod(int(iso), n_mh))
    y0, y1 = seg.log_l[:, 0], seg.log_l[:, 1]
    d = y1 - y0
    lo_k, hi_k = LOG_L_GRID[k], LOG_L_GRID[k + 1]
    a0, b0 = _above(seg.log_l, lo_k)
    a1, b1 = _above(seg.log_l, hi_k)
    count = (seg.number[:, None] * np.maximum((b0 - a0) - (b1 - a1), 0.0)).T  # (n, n_seg): each segment's stars in the interval
    cdf = np.cumsum(count, axis=1)
    fallback = cdf[:, -1] <= 0.0
    j = np.clip((cdf < u_segment[:, None] * cdf[:, -1:]).sum(axis=1), 0, d.size - 1)
    if fallback.any():
        middle = 0.5 * (lo_k + hi_k)[fallback]
        gap = np.abs(np.clip(middle[:, None], np.minimum(y0, y1), np.maximum(y0, y1)) - middle[:, None])
        j[fallback] = np.argmin(gap, axis=1)
    flat = d[j] == 0.0
    lo = np.maximum(np.minimum(y0[j], y1[j]), lo_k)
    hi = np.minimum(np.maximum(y0[j], y1[j]), hi_k)
    hi = np.maximum(hi, lo)
    log_l = np.where(flat, y0[j], lo + u_luminosity * (hi - lo))
    s = np.clip(np.where(flat, 0.5, (log_l - y0[j]) / np.where(flat, 1.0, d[j])), 0.0, 1.0)
    log_l = np.where(fallback, y0[j] + s * d[j], log_l)
    neg = seg.neg_mag[j, 0] + s[:, None] * (seg.neg_mag[j, 1] - seg.neg_mag[j, 0])
    return {
        "log_l": log_l,
        "mass": seg.mass[j, 0] + s * (seg.mass[j, 1] - seg.mass[j, 0]),
        "log_teff": seg.log_teff[j, 0] + s * (seg.log_teff[j, 1] - seg.log_teff[j, 0]),
        "mags": -2.5 * neg,
        "label": np.where(s < 0.5, seg.label[j, 0], seg.label[j, 1]),
        "fallback": fallback,
    }


def _properties(galaxy: BrightGalaxy, cell: np.ndarray, k: np.ndarray, u: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Each star's isochrone, age, luminosity, place on the isochrone and place in its cell, given its interval."""
    tab = isochrones()
    ring, sector = galaxy.locate(cell)
    n_star = k.size

    # Which part and which isochrone: ∝ the part's azimuthal weight times the mass on each isochrone times the
    # stars it puts in this threshold interval - exact counts, the same partition the interval's count is.
    in_bin = galaxy.count_cell[:, ring, k] - galaxy.count_cell[:, ring, k + 1]  # (2, n)
    w = galaxy.weights[:, ring, sector] * np.maximum(in_bin, 0.0)
    total = w.sum(axis=0)
    p_young = np.where(total > 0.0, w[0] / np.where(total > 0.0, total, 1.0), 0.0)
    up = u["population"]
    part = (up >= p_young).astype(np.int64)
    rest = np.where(part == 0, up / np.where(p_young > 0.0, p_young, 1.0), (up - p_young) / np.where(p_young < 1.0, 1.0 - p_young, 1.0))
    rest = np.clip(rest, 0.0, 1.0)
    iso = np.zeros(n_star, dtype=np.int64)
    for s in range(0, n_star, 8192):
        sl = slice(s, s + 8192)
        dn = (galaxy.count_iso[:, k[sl]] - galaxy.count_iso[:, k[sl] + 1]).T  # (m, n_iso)
        weight = np.maximum(galaxy.mass_cell[part[sl], ring[sl]] * dn, 0.0)
        cdf = np.cumsum(weight, axis=1)
        iso[sl] = np.clip((cdf < rest[sl, None] * cdf[:, -1:]).sum(axis=1), 0, weight.shape[1] - 1)
    age_i, mh_i = np.divmod(iso, galaxy.n_mh)

    # The age within what the isochrone stands for: uniform in log age over the half-steps either side of it,
    # inside the part's window [inferred: the light stage's weights are linear in log age between isochrones].
    half = 0.5 * float(tab.log_ages[1] - tab.log_ages[0])
    centre = tab.log_ages[age_i]
    w_lo, w_hi = galaxy.windows[part, 0], galaxy.windows[part, 1]
    lo = np.maximum(centre - half, w_lo)
    hi = np.minimum(centre + half, w_hi)
    empty = hi < lo
    lo = np.where(empty, np.clip(centre, w_lo, w_hi), lo)
    hi = np.where(empty, lo, hi)
    age = 10.0 ** (lo + u["age"] * (hi - lo)) / 1e9

    # Where on the isochrone, and so the star's luminosity: its segment by exact counts in the interval, its
    # log L uniform across the segment's overlap with the interval (on_isochrone, D203).
    log_l = np.empty(n_star)
    mass = np.empty(n_star)
    log_teff = np.empty(n_star)
    mags = np.empty((n_star, len(BANDS)))
    label = np.empty(n_star)
    for g in np.unique(iso):
        sel = np.flatnonzero(iso == g)
        placed = on_isochrone(int(g), k[sel], u["segment"][sel], u["luminosity"][sel], galaxy.n_mh)
        log_l[sel], mass[sel], log_teff[sel] = placed["log_l"], placed["mass"], placed["log_teff"]
        mags[sel], label[sel] = placed["mags"], placed["label"]

    # Radius: the cell's span, by inverting the surface density of the star's own part and threshold interval
    # (linear between grid radii) times R. Azimuth: the cell's span, by the part's azimuthal law at that radius.
    R = galaxy.R
    lo_r, hi_r = galaxy.ring_lo[ring], galaxy.ring_hi[ring]
    grid = np.linspace(0.0, 1.0, RADIUS_STEPS + 1)
    rr = lo_r[:, None] + (hi_r - lo_r)[:, None] * grid[None, :]
    i0 = np.clip(np.searchsorted(R, rr) - 1, 0, R.size - 2)
    w1 = np.clip((rr - R[i0]) / (R[i0 + 1] - R[i0]), 0.0, 1.0)
    p, kk = part[:, None], k[:, None]
    dens = galaxy.count_R[p, i0, kk] - galaxy.count_R[p, i0, kk + 1]
    dens1 = galaxy.count_R[p, i0 + 1, kk] - galaxy.count_R[p, i0 + 1, kk + 1]
    radial = np.maximum(dens * (1.0 - w1) + dens1 * w1, 0.0) * rr
    radius = lo_r + invert_azimuths(u["radius"], grid, radial) * (hi_r - lo_r)

    lo_p, hi_p = galaxy.sector_lo[sector], galaxy.sector_hi[sector]
    agrid = np.linspace(0.0, 1.0, AZIMUTH_STEPS + 1)
    phis = lo_p[:, None] + (hi_p - lo_p)[:, None] * agrid[None, :]
    pattern = galaxy.pattern
    law = np.ones_like(phis) if pattern is None or pattern.flat else pattern.contrast_at(radius[:, None], phis)
    if galaxy.modulation is not None and (part == 0).any():
        young = part == 0
        law[young] = galaxy.modulation.at_points(radius[young], phis[young])
    azimuth = lo_p + invert_azimuths(u["azimuth"], agrid, law) * (hi_p - lo_p)

    # Height: the sech² profile at the scale height of the population born at this radius and birth time
    # (birth_population read where the star is now: the bright catalogue draws no birth radius).
    t = galaxy.t
    col = np.clip(np.searchsorted(t, galaxy.t_max - age), 0, t.size - 1)
    row = np.clip(np.searchsorted(R, radius), 0, R.size - 1)
    thick = galaxy.thick[row, col]
    height = sech2_height(u["height"], np.where(thick, galaxy.h_thick, galaxy.h_thin))

    out = {
        "bright_star_radius": radius,
        "bright_star_azimuth": azimuth,
        "bright_star_height": height,
        "bright_star_age": age,
        "bright_star_metallicity": tab.mhs[mh_i],
        "bright_star_mass": mass,
        "bright_star_luminosity": 10.0**log_l,
        "bright_star_temperature": 10.0**log_teff,
        "bright_star_phase": label.astype(np.int64),
    }
    for b, band in enumerate(BANDS):
        out[f"bright_star_magnitude_{band.lower()}"] = mags[:, b]
    return out


def magnitudes(cat: Mapping[str, np.ndarray]) -> np.ndarray:
    """``(n, 8)``: each star's eight absolute magnitudes in the table's band order, what ``spectra.object_nu_l_nu``
    turns into its anchors for ``/api/bright``'s ``response`` (S48's wiring)."""
    return np.stack([np.asarray(cat[f"bright_star_magnitude_{b.lower()}"], dtype=float) for b in BANDS], axis=-1)


def in_frustum(view: np.ndarray, radius: np.ndarray, azimuth: np.ndarray, height: np.ndarray) -> np.ndarray:
    """Which points lie inside a view-projection matrix's frustum, in the viewer's frame (y up, phi from +x
    towards -z: frontend/src/galaxy/positions.ts) - the test /api/region's brightest mode applies."""
    r = np.asarray(radius, dtype=float)
    phi = np.asarray(azimuth, dtype=float)
    p = np.stack([r * np.cos(phi), np.asarray(height, dtype=float), -r * np.sin(phi), np.ones_like(r)])
    clip = view @ p
    w = clip[3]
    return (w > 0) & (np.abs(clip[0]) <= w) & (np.abs(clip[1]) <= w) & (np.abs(clip[2]) <= w)


def _rows(cat: Mapping[str, np.ndarray], keep: np.ndarray) -> Catalogue:
    return Catalogue.of({name: np.asarray(col)[keep] for name, col in cat.items()})


def select_brightest(
    galaxy: BrightGalaxy,
    seed: int,
    cells: Sequence[int],
    n: int,
    *,
    view: np.ndarray | None = None,
    fetch: Callable[[Sequence[int], float], Catalogue] | None = None,
    pool_max: float = math.inf,
) -> tuple[Catalogue, dict[str, Any]]:
    """The ``n`` brightest disc stars in ``cells`` (inside ``view``'s frustum when one is given), brightest
    first, with what the selection is complete above.

    The threshold is found by bisection on the expected count over the cells; the stars above it are
    materialised (``fetch``, a cache's, or :func:`materialise_bright`) and cut to the frustum. If fewer than
    ``n`` are inside, the expected count aimed at is raised - by the shortfall's ratio with a margin, at least
    doubled when a view hides most of the window - and the threshold lowered, at most ``MAX_PASSES`` times,
    never past the grid's faint end and never above ``pool_max`` expected stars. ``l_min`` is then the
    faintest returned star's luminosity and every disc star older than the cluster window brighter than it
    in the cells (and frustum) is in the body; ``complete`` is false when the search stopped short of ``n``.
    """
    fetch = fetch or (lambda wanted, l: materialise_bright(galaxy, seed, wanted, l))
    cells = np.asarray(list(cells), dtype=np.int64)
    # Aim three standard deviations of the Poisson count past n, so one pass usually suffices.
    target = float(n) + 3.0 * math.sqrt(n) + 3.0
    why = ""
    complete = False
    for passes in range(1, MAX_PASSES + 1):
        x = galaxy.threshold(cells, target)
        pool = fetch(cells, 10.0**x)
        lum = np.asarray(pool["bright_star_luminosity"], dtype=float)
        inside = np.arange(lum.size)
        if view is not None and lum.size:
            inside = inside[in_frustum(view, pool["bright_star_radius"], pool["bright_star_azimuth"], pool["bright_star_height"])]
        order = inside[np.argsort(-lum[inside], kind="stable")]
        found = int(order.size)
        if found >= n:
            order, complete = order[:n], True
            break
        expected = float(galaxy.expected(cells, x).sum())
        if x <= LOG_L_GRID[0]:
            why = f"fewer than n={n}: the luminosity function's faint end ({10.0 ** LOG_L_GRID[0]:g} Lsun) holds {found}"
            break
        if expected >= pool_max:
            why = f"fewer than n={n}: {found} inside at {expected:.0f} expected in the cells, the most one request materialises"
            break
        if passes == MAX_PASSES:
            why = f"fewer than n={n}: {found} inside after {MAX_PASSES} passes"
            break
        ratio = n / max(found, 1)
        grow = ratio * (1.0 + 4.0 / math.sqrt(n)) + 4.0 / n
        target = min(pool_max, max(expected, target) * (2.0 if view is not None and ratio > 1.5 else 1.0) * grow)
    chosen = _rows(pool, order)
    l_min = float(chosen["bright_star_luminosity"][-1]) if complete and chosen.size else 10.0**x
    return chosen, {"l_min": l_min, "complete": complete, "why": why or "the n brightest: every star above l_min is in the body",
                    "passes": passes, "pool": int(lum.size)}


# --- declarations -------------------------------------------------------------------------------------


def _column(name: str, label: str, unit: str, about: str, ramp: Ramp, zero: bool = True) -> FieldDecl:
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="bright_star", ramp=ramp,
                     meaningful_zero=zero, provenance="seeded", about=about)


BRIGHT_RADIUS = _column(
    "bright_star_radius", "Galactocentric radius", "kpc",
    "Inside the star's finest cell, by inverting the surface density of stars of its own luminosity and age "
    "part across the cell's radial span, times R.", Ramp("viridis"))
BRIGHT_AZIMUTH = _column(
    "bright_star_azimuth", "Azimuth", "rad",
    "Inside the star's finest cell, by inverting the arm and bar density contrast at its radius; where the "
    "model publishes where stars form today, a star younger than about one arm crossing follows that instead, "
    "as the sampled catalogue's young stars do.", Ramp("viridis"))
BRIGHT_HEIGHT = _column(
    "bright_star_height", "Height above the plane", "kpc",
    "Inverted from the sech² profile at the scale height of the population (thin or thick) born at the "
    "star's radius at its birth time - read where the star is now, since this catalogue draws no birth radius.",
    Ramp("viridis"))
BRIGHT_AGE = _column(
    "bright_star_age", "Age", "Gyr",
    "Uniform in log age across the half-steps either side of the isochrone the star was drawn on, inside its "
    "age part. Never younger than the cluster census's window: those stars are the clusters'.", Ramp("magma"))
BRIGHT_METALLICITY = _column(
    "bright_star_metallicity", "[M/H]", "dex",
    "The metallicity of the isochrone the star was drawn on: the light stage's nearest isochrone to the [Fe/H] "
    "of the history step that formed it, where its stars are now.", Ramp("RdBu", lo=-2.0, hi=0.5), zero=False)
BRIGHT_MASS = _column(
    "bright_star_mass", "Initial mass", "Msun",
    "Read along the isochrone at the star's point: the segment chosen by its exact count of stars in the "
    "star's luminosity interval, the point by the star's luminosity on it.", Ramp("inferno", scale="log"))
BRIGHT_LUMINOSITY = _column(
    "bright_star_luminosity", "Luminosity", "Lsun",
    "Bolometric, from the luminosity function: the star's place in its cell's ordered Poisson process fixes the "
    "0.05-dex interval of luminosity it lies in, and within it the luminosity is uniform in log L across the "
    "isochrone segment its exact count there chose, so every disc star brighter than any threshold is in the "
    "catalogue and a higher grid threshold keeps a prefix of it. A point painted by this through a "
    "blackbody's share at the star's temperature is 4-15% too bright through optical filters (D201, debt #114: a star "
    "is nearly a blackbody, a cluster is not); /api/bright with filters= serves the star's own band light through the "
    "viewer's curves (S48), which the viewer draws by once its star-first mode is built.", Ramp("inferno", scale="log"))
BRIGHT_TEMPERATURE = _column(
    "bright_star_temperature", "Effective temperature", "K",
    "The isochrone's at the star's initial mass, read along the same segment as its mass.",
    Ramp("blackbody", scale="log", lo=BLACKBODY_KELVIN[0], hi=BLACKBODY_KELVIN[1]))


def _magnitude_column(band: str) -> FieldDecl:
    return _column(
        f"bright_star_magnitude_{band.lower()}", f"Absolute {band} magnitude M_{band}", "mag",
        f"The isochrone's {band}-band absolute magnitude (Vega) at the star's point on its segment, where its "
        "luminosity is the star's own. Intrinsic. With the other seven "
        "it is what /api/bright's response (filters=, S48) puts through the viewer's curves.",
        Ramp("inferno", lo=-10.0, hi=5.0), zero=False)


BRIGHT_MAGNITUDES = tuple(_magnitude_column(b) for b in BANDS)
BRIGHT_PHASE = FieldDecl(
    name="bright_star_phase", label="Evolutionary phase", unit="dimensionless", kind=Kind.CATEGORY_COLUMN,
    of="bright_star", categories=PHASES, provenance="seeded",
    ramp=Palette(("#7a7a7a", "#6fa8ff", "#9fd3c7", "#e8894c", "#f2d16b", "#4cc9f0", "#d1495b", "#b5179e", "#7209b7")),
    about=(
        "PARSEC's phase label at the nearer end of the isochrone segment the star sits on: the table's own "
        "vocabulary, from the main sequence to the thermally pulsing AGB."
    ),
)
COLUMNS: tuple[FieldDecl, ...] = (
    BRIGHT_RADIUS, BRIGHT_AZIMUTH, BRIGHT_HEIGHT, BRIGHT_AGE, BRIGHT_METALLICITY, BRIGHT_MASS,
    BRIGHT_LUMINOSITY, BRIGHT_TEMPERATURE, *BRIGHT_MAGNITUDES, BRIGHT_PHASE,
)

BRIGHT_LIMIT = FieldDecl(
    name="bright_star_limit", label="Bright catalogue's default limit", unit="Lsun", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The luminosity of the faintest star of the default selection - the disc's brightest few thousand, the "
        "viewer's default count: every disc star brighter than this and older than the cluster census's window "
        "is in it. **Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the "
        "stage that publishes the bright-star columns, which `scalarsAt` excludes; `/api/arrays` serves it, and "
        "the `/api/bright` header carries it under `scalars`."
    ),
)
BRIGHT_COUNT_1E3 = FieldDecl(
    name="bright_star_count_1e3", label="Disc stars above a thousand Suns", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The expected number of disc stars brighter than 10³ L☉ and older than the cluster census's window: the "
        "luminosity function summed over every finest cell, a count rather than a sample. Seeded only because "
        "its stage is (D55). **Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy "
        "scalar of the stage that publishes the bright-star columns, which `scalarsAt` excludes; `/api/arrays` "
        "serves it, and the `/api/bright` header carries it under `scalars`."
    ),
)

READS = (
    "stars_formed_history", "feh_history", "birth_population", "thin_disc_scale_height", "thick_disc_scale_height",
    *PATTERN_READS,  # S56 (D215): the stellar pattern's modes and their phases, not an arm number
)


def all_cells() -> np.ndarray:
    """Every finest cell's id, in order."""
    return np.arange(CELL_COUNT * children_per_cell(MAX_LEVEL), dtype=np.int64)


def galaxy_of(ctx: Context) -> BrightGalaxy:
    spec = ctx.grid.spec
    return BrightGalaxy(ctx.fields, ctx.grid.R, ctx.grid.t, float(spec.t_max), int(spec.n_t), ctx.constants)


def scalars(galaxy: BrightGalaxy, limit: float) -> dict[str, float]:
    """The stage's two galaxy scalars, from the default selection's limit and the luminosity function."""
    return {"bright_star_limit": float(limit), "bright_star_count_1e3": float(galaxy.expected(all_cells(), 3.0).sum())}


def compute_bright(ctx: Context) -> Mapping[str, Any]:
    galaxy = galaxy_of(ctx)
    chosen, info = select_brightest(galaxy, int(ctx.seeds["systems_seed"]), all_cells(), DEFAULT_SELECTION)
    return {**{d.name: chosen[d.name] for d in COLUMNS}, **scalars(galaxy, info["l_min"])}


BRIGHT_STARS = IMPLEMENTATIONS.register(
    Stage(
        id="bright_stars", slot="bright_stars", checkpoint=5,
        about=(
            "Every disc star above a luminosity, complete: per finest cell an ordered Poisson process in "
            "luminosity on the population's luminosity function, so a higher threshold keeps a prefix and a "
            "region's stars are a sweep's. Publishes the disc's brightest few thousand; /api/bright serves any "
            "threshold or count. Stars younger than the cluster census's window are the census's, and the bulge "
            "is not covered: it stays in the field."
        ),
        compute=compute_bright,
        placement_reader=True,  # S55 (D214, I4): a census, placed by the stellar pattern and the modulation
        reads_seeds=("systems_seed",),
        reads_constants=("RETURN_FRACTION", "GMC_PHASE_BLOWN_OPEN", "GMC_PHASE_DISPERSING"),
        requires=READS,
        requires_optional=("sfr_modulation",),
        publishes=(*COLUMNS, BRIGHT_LIMIT, BRIGHT_COUNT_1E3),
    )
)
