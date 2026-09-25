"""Chemistry, the shared half: the gradient, the migration kernel, and the [Fe/H] declarations.

Until D170 this module was also a stage — the simple model's single-element chemistry
with instantaneous recycling, ``d(Sigma_gas Z)/dt = NET_YIELD (1 - R) Psi - Z (1 - R) Psi``
— and ``chemistry_dtd`` replaced it in the advanced model with multi-element yields and a
delay-time distribution (S9). With one model registered the stage is retired; what stays
here is what the delay-time chemistry and the catalogue still read: the gradient fit, the
age bins, the migration transport, and the [Fe/H] field declarations the chemistry publishes
under the same contract.

The two terms of that equation are still the whole story of a gradient. Enrichment goes as
the star formation rate; dilution goes as the *infall* rate. The inner disc finished
accreting long ago and has been enriching undiluted ever since; the outer disc is still
being rained on by primordial gas. That is where a negative gradient comes from, and it is
why the gradient is set by the inside-out index rather than by the yield — the yield moves
the whole curve up and down.

**Radial migration** applies to stars and not to gas. A star's birth radius is
where its metallicity was set; churning then moves it. Modelled as a Gaussian
in radius whose width grows with age, ``sigma(age) = migration_efficiency *
sqrt(age / 8 Gyr)``, convolved over the birth-radius distribution of each age
bin. So acceptance row 22 — the *present-day* gradient, measured from young
tracers — is untouched by migration, while row 23's old populations are flattened
by it. That contrast is the observable migration is there to reproduce.
"""

from __future__ import annotations

import numpy as np

from galaxy.stages.disc import PC_PER_KPC

GRADIENT_FIT_RANGE = (4.0, 12.0)  # kpc; where gradients are actually measured
MIGRATION_REFERENCE_AGE = 8.0  # Gyr, the age the migration width is quoted at
AGE_BIN = 0.5  # Gyr; 1.0 and 10.0 are bin edges, so the young/old selections are exact
YOUNG_MAX_AGE = 1.0  # Gyr
OLD_MIN_AGE = 10.0  # Gyr


def gradient(feh: np.ndarray, R: np.ndarray, weights: np.ndarray | None = None) -> float:
    """Weighted least-squares slope of [Fe/H] against R over the measured range."""
    lo, hi = GRADIENT_FIT_RANGE
    w = (R > lo) & (R < hi) & np.isfinite(feh)
    if weights is not None:
        w &= weights > 0.0
    if w.sum() < 3:
        return float("nan")
    ww = None if weights is None else weights[w]
    return float(np.polyfit(R[w], feh[w], 1, w=ww)[0])


def age_bin_edges(t_max: float) -> np.ndarray:
    """The age bins the migration kernel is evaluated in, shared so two stages cannot drift.

    ``chemistry_dtd`` moves each bin's stars with one kernel width and ``systems`` draws a
    star's birth radius from the same bin's weights; binned differently, the catalogue would
    carry a population the chemistry never described, which is the defect debt #31 named.
    """
    return np.arange(0.0, float(t_max) + AGE_BIN, AGE_BIN)


def migration_width(age: np.ndarray | float, efficiency: float) -> np.ndarray:
    """σ(age) = migration_efficiency · √(age / 8 Gyr) — the kernel's width, in one place.

    The rule is the model's, not this stage's: ``chemistry_dtd`` widens its transport by it
    and ``systems`` draws a star's birth radius with it, so it is written once here rather
    than three times consistently (rule A9).
    """
    return efficiency * np.sqrt(np.maximum(np.asarray(age, dtype=float), 0.0) / MIGRATION_REFERENCE_AGE)


def transport(R: np.ndarray, sigma: float) -> np.ndarray:
    """Row-normalised Gaussian kernel: fraction of ring i's stars now found in ring j.

    Normalised over the *destination*, so ``K[i]`` is where ring i's stars went and sums to
    one. Reading it backwards — which ring did the stars now at j come from — is therefore
    not ``K[:, j]`` but ``born[i] · K[i, j]`` — Bayes, weighted by how much mass each ring
    had to send. ``chemistry_dtd`` writes that product inline and ``systems`` draws a star's
    birth radius from it; a draw that used ``K[:, j]`` alone would put stars where nothing
    was born, and read a metallicity off gas that made no stars (rule B9).
    """
    if sigma <= 0.0:
        return np.eye(R.size)
    k = np.exp(-0.5 * ((R[None, :] - R[:, None]) / sigma) ** 2)
    return k / k.sum(axis=1, keepdims=True)


def transport_columns(R: np.ndarray, sigma: float, at: np.ndarray) -> np.ndarray:
    """``transport(R, sigma)[:, at]`` without building the square kernel.

    A caller that wants a few destinations should not pay for every pair. On a uniform grid
    the row normalisation — the sum of one Gaussian over the whole grid, seen from each ring
    — is a sliding window over a fixed profile, so it is a cumulative sum rather than a
    matrix row sum, and each column asked for is then linear in the grid. Same numbers as
    the square kernel's columns `[verified: tests/test_chemistry.py::
    test_the_columns_of_the_kernel_are_the_kernels_columns]`; it is what lets a one-cell
    region query not pay for the whole disc (rule D4).

    Falls back to the square kernel when the grid is not uniform, because the sliding-window
    argument is exactly the thing that stops being true then.
    """
    at = np.atleast_1d(np.asarray(at, dtype=int))
    n = R.size
    step = np.diff(R)
    if sigma <= 0.0 or n < 2 or not np.allclose(step, step[0]):
        return transport(R, sigma)[:, at]
    offsets = np.arange(-(n - 1), n) * float(step[0])
    g = np.exp(-0.5 * (offsets / sigma) ** 2)
    cumulative = np.cumsum(g)
    i = np.arange(n)
    upper = cumulative[2 * n - 2 - i]
    lower = np.where(i <= n - 2, cumulative[np.maximum(n - 2 - i, 0)], 0.0)
    rows = upper - lower
    return g[at[None, :] - i[:, None] + (n - 1)] / rows[:, None]


def migrate(profile: np.ndarray, weight: np.ndarray, R: np.ndarray, sigma: float) -> np.ndarray:
    """Mass-weighted Gaussian smoothing of a per-radius quantity (churning)."""
    if sigma <= 0.0:
        return profile
    kernel = np.exp(-0.5 * ((R[:, None] - R[None, :]) / sigma) ** 2)
    num = kernel @ (weight * profile)
    den = kernel @ weight
    return np.where(den > 0.0, num / np.where(den > 0.0, den, 1.0), np.nan)


