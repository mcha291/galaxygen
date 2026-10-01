"""The bright end of the disc, complete: every disc star above a luminosity (checkpoint 5, S48, D200).

The star catalogue (``systems.py``) is a *number* sample, about one star in 10⁵ of the galaxy, so the
brightest of it are the brightest of the sample, not of the galaxy. This module is the other half: a
catalogue that holds **every** disc star above a luminosity threshold, drawn from the population's
luminosity function rather than from the sample, so that what it holds plus the field's light under it
is the disc's light, exactly.

**The luminosity function** (:func:`luminosity_function`). Per isochrone, the number of stars per solar
mass formed brighter than each threshold ``L_k`` (``LOG_L_GRID``), the bolometric light they carry and
their light in each of the table's eight bands. Integrated **along the isochrone's own points**, which
are dense where the evolved phases are: between consecutive living points the IMF's number in the mass
interval (analytic, ``_imf_number``) is spread uniformly in log L between the two ends, so the count
above a threshold is continuous and monotone in it; the light and the band fluxes of the part above it
are integrated on the same segment with each quantity's logarithm linear in the segment's parameter
(log L for the light, −0.4 M for a band), exactly. The stars lighter than an isochrone's first point
are read at it, as the field reads them. Dead stars contribute nothing. Each isochrone's light and band
totals (the values for L → 0) are then **renormalised to the field's own tables**
(``photometry.population_light``): the field's quadrature is the total, the luminosity function
distributes it, so the bright catalogue and the field share one budget. The count is not renormalised;
the field has no count to match.

**The decomposition** (:func:`isochrone_weights`, :func:`mass_on_isochrones`). The light stage reads
each history step's light as a per-isochrone table pushed through ``on_fine_ages``,
``cumulative_over_age`` and ``steps_over``, all linear in the table; pushing the identity through them
gives the weight each step puts on each isochrone age, so the mass formed on every (age, metallicity)
isochrone is a matrix product, and ``mass @ light_per_mass`` is ``disc_surface_brightness`` to rounding
(``tests/test_bright.py``). An age window is applied in step space: a step that straddles a boundary is
split into its parts, each part's weights computed over its own sub-interval and scaled by its share of
the step, so the parts sum to the step exactly.
"""

from __future__ import annotations

import functools
import math
from dataclasses import dataclass

import numpy as np

from galaxy.core.grids import Axis
from galaxy.stages.photometry import (
    BANDS,
    EXTRA,
    cumulative_over_age,
    isochrones,
    nearest_metallicity,
    on_fine_ages,
    population_light,
    steps_over,
)

# Luminosity thresholds, log10 L/L☉ bolometric, every 0.05 dex from 0.1 L☉ to 4 × 10⁶ L☉: past the
# brightest point of the youngest isochrone the catalogue covers.
LOG_L_GRID = np.linspace(-1.0, 6.6, 153)


# --- the IMF's number in a mass interval, analytic ---------------------------------------------------


def _imf_cumulative(m: np.ndarray) -> np.ndarray:
    """∫ φ dm from the IMF's lower end to ``m``, with φ ``photometry.imf_weights``' unnormalised Kroupa form."""
    from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE, IMF_MIN

    m = np.clip(np.asarray(m, dtype=float), IMF_MIN, None)
    p_lo, p_hi = IMF_LOW_SLOPE + 1.0, IMF_HIGH_SLOPE + 1.0
    k_high = IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE)
    below = (np.minimum(m, IMF_BREAK) ** p_lo - IMF_MIN**p_lo) / p_lo
    above = k_high * (np.maximum(m, IMF_BREAK) ** p_hi - IMF_BREAK**p_hi) / p_hi
    return below + above


def _imf_number(lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """∫ φ dm over [lo, hi]: the IMF's number in each mass interval, unnormalised."""
    return _imf_cumulative(hi) - _imf_cumulative(lo)


@functools.cache
def _imf_mass_formed() -> float:
    """∫ φ m dm over the whole IMF, analytic: what turns the unnormalised number into stars per M☉ formed."""
    from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE, IMF_MAX, IMF_MIN

    k_high = IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE)
    p_lo, p_hi = IMF_LOW_SLOPE + 2.0, IMF_HIGH_SLOPE + 2.0
    return float((IMF_BREAK**p_lo - IMF_MIN**p_lo) / p_lo + k_high * (IMF_MAX**p_hi - IMF_BREAK**p_hi) / p_hi)


# --- the segments of an isochrone ---------------------------------------------------------------------


@dataclass(frozen=True)
class Segments:
    """One isochrone as straight pieces between its consecutive living points.

    Each segment holds ``number`` stars per M☉ formed, spread uniformly in its parameter s ∈ [0, 1]
    (and so in log L, which is linear in s); every other column is linear in s between its ends.
    The first segment runs from the IMF's lower end to the isochrone's first point at that point's
    values: the stars the table does not reach, read at its lightest as the field reads them.
    """

    number: np.ndarray  # (n,) stars per M☉ formed
    log_l: np.ndarray  # (n, 2) log10 L/L☉ at the two ends
    mass: np.ndarray  # (n, 2) initial mass, M☉
    log_teff: np.ndarray  # (n, 2)
    neg_mag: np.ndarray  # (n, 2, 8): −0.4 M_band at the ends, so 10^this is the band flux
    label: np.ndarray  # (n, 2) PARSEC's phase label at the ends


@functools.cache
def segments(age: int, mh: int) -> Segments:
    """The segments of isochrone ``(age, mh)``: see :class:`Segments`."""
    from galaxy.stages.systems import IMF_MIN

    tab = isochrones()
    m, log_l, log_teff = tab.track(age, mh)
    cols = tab.extra[(age, mh)]
    mags = cols[:, [EXTRA.index(b) for b in BANDS]]
    label = cols[:, EXTRA.index("label")]
    # Prepend the IMF's lower end at the first point's values (a degenerate segment in L).
    m0 = np.concatenate([[min(IMF_MIN, m[0])], m])
    idx = np.concatenate([[0], np.arange(m.size)])
    lo, hi = idx[:-1], idx[1:]
    number = _imf_number(m0[:-1], m0[1:]) / _imf_mass_formed()
    return Segments(
        number=number,
        log_l=np.stack([log_l[lo], log_l[hi]], axis=1),
        mass=np.stack([m0[:-1], m0[1:]], axis=1),
        log_teff=np.stack([log_teff[lo], log_teff[hi]], axis=1),
        neg_mag=np.stack([-0.4 * mags[lo], -0.4 * mags[hi]], axis=1),
        label=np.stack([label[lo], label[hi]], axis=1),
    )


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


def _log_linear_integral(g0: np.ndarray, g1: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """∫_a^b 10^(g0 + s (g1 − g0)) ds, exactly, for g linear in s; zero where b <= a."""
    d = (g1 - g0) * math.log(10.0)
    width = np.maximum(b - a, 0.0)
    start = 10.0 ** (g0 + a * (g1 - g0))
    x = d * width
    small = np.abs(x) < 1e-9
    factor = np.where(small, width * (1.0 + 0.5 * x), np.expm1(np.where(small, 0.0, x)) / np.where(small, 1.0, d))
    return start * factor


@dataclass(frozen=True)
class BrightTables:
    """Per isochrone ``(n_age, n_mh)`` and threshold ``LOG_L_GRID``: what lies above each threshold, per M☉ formed.

    ``count_above``, ``light_above`` and ``band_above`` are non-increasing in L; ``light_above`` and
    ``band_above`` are renormalised so that their totals (L → 0, every living star) are the field's
    ``light_per_mass`` and ``band_flux``; ``light_factor`` and ``band_factor`` are the factors that took.
    ``count_total`` is every living star per M☉ formed (not renormalised).
    """

    log_l: np.ndarray  # (K,)
    count_above: np.ndarray  # (n_age, n_mh, K) stars per M☉ formed with L > L_k
    light_above: np.ndarray  # (n_age, n_mh, K) L☉ per M☉ formed from those stars
    band_above: np.ndarray  # (n_age, n_mh, K, 8) Σ 10^(−0.4 M_band) per M☉ formed from those stars
    count_total: np.ndarray  # (n_age, n_mh)
    light_factor: np.ndarray  # (n_age, n_mh): the field's total over the segments' own
    band_factor: np.ndarray  # (n_age, n_mh, 8)

    @property
    def light_above_own(self) -> np.ndarray:
        """``light_above`` before the renormalisation: the light the stars of ``count_above`` themselves carry."""
        return self.light_above / self.light_factor[..., None]


@functools.cache
def luminosity_function() -> BrightTables:
    """The per-isochrone tables of what lies above each threshold: see the module docstring."""
    tab = isochrones()
    pop = population_light()
    x = LOG_L_GRID
    shape = (tab.log_ages.size, tab.mhs.size)
    count = np.zeros((*shape, x.size))
    light = np.zeros((*shape, x.size))
    bands = np.zeros((*shape, x.size, len(BANDS)))
    count_total = np.zeros(shape)
    light_factor = np.ones(shape)
    band_factor = np.ones((*shape, len(BANDS)))
    for (age, mh) in tab.tracks:
        seg = segments(age, mh)
        n = seg.number[:, None]
        a, b = _above(seg.log_l, x)
        count[age, mh] = (n * (b - a)).sum(axis=0)
        raw_light = (n * _log_linear_integral(seg.log_l[:, 0:1], seg.log_l[:, 1:2], a, b)).sum(axis=0)
        total_light = float((seg.number * _log_linear_integral(seg.log_l[:, 0], seg.log_l[:, 1], 0.0, 1.0)).sum())
        light_factor[age, mh] = pop.light_per_mass[age, mh] / total_light
        light[age, mh] = raw_light * light_factor[age, mh]
        count_total[age, mh] = float(seg.number.sum())
        for k in range(len(BANDS)):
            g0, g1 = seg.neg_mag[:, 0, k], seg.neg_mag[:, 1, k]
            raw = (n * _log_linear_integral(g0[:, None], g1[:, None], a, b)).sum(axis=0)
            total = float((seg.number * _log_linear_integral(g0, g1, 0.0, 1.0)).sum())
            band_factor[age, mh, k] = pop.band_flux[age, mh, k] / total
            bands[age, mh, :, k] = raw * band_factor[age, mh, k]
    return BrightTables(x, count, light, bands, count_total, light_factor, band_factor)


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
