"""spectrum: the two-dimensional power spectrum of a field on a flat square patch (S62, D221 part I items 8-9).

An instrument (rule B1: built and tested before the thing it certifies - the gas fluctuation field, whose gate
reads its slopes and its break). It reads a field sampled on a regular square grid and nothing of how the field was
made, so it measures any field.

**The convention.** ``k = 2 pi / wavelength`` (an angular wavenumber: radians per unit of the grid's spacing; a
patch sampled in pc gives k in rad/pc, and the wavelength of a bin is ``2 pi / k``). ``P(k)`` is the power
spectral density per unit area of k-space, normalised so that the sum of ``P`` over every mode times the area of one
mode, ``(2 pi / (n d))^2``, is the variance of the windowed field (Parseval) - the "P(k) per unit volume of
wavenumber in d dimensions" of ``noise.octave_weights``. **A power law is written** ``P(k) ~ k^alpha`` **with alpha
negative for a field with more power at large scales**: a field drawn by ``noise.fractal`` with ``slope = s`` has
``alpha = -s``, and the sources' "P(k) ~ k^-1.6" (Dutta et al. 2013) is ``alpha = -1.6``. A slope "above a break"
in scale is the one at **low k** here; the fits name their slopes by k.

**The estimate** (:func:`power_spectrum`): the field's mean is removed, it is multiplied by a separable Hann window
(``w(i) = sin^2(pi (i + 1/2) / n)`` per axis) and the periodogram ``|FFT|^2 d^2 / (4 pi^2 n^2 <w^2>)`` is taken, so
that a white field of variance v reads ``P = v d^2 / (4 pi^2)`` at every k. The window guards against the patch's
edges, since no field of the model is periodic on a patch: a box window's transform falls as k^-1 in amplitude, so
the edges' discontinuity leaks power as k^-2 into the higher wavenumbers [inferred]. Measured on ``noise.fractal``
fields (512^2, three seeds) it matters less than that suggests: asked 2.53, the bare periodogram reads -2.66 to -2.71
over 4-64 cycles against the window's -2.41 to -2.60, and asked 3.5 it reads 0.03 to 0.11 shallower over 16-128
cycles - no systematic flattening at the gas's slopes, so the window is the conventional guard, not a correction
this field needs. It costs resolution at the lowest wavenumbers (it convolves the spectrum with a kernel about two
modes wide), so a fit starts a few modes above the patch's fundamental.

**The azimuthal average** (:func:`azimuthal_average`): the modes are binned in ``|k|`` on logarithmic bins from the
patch's fundamental ``2 pi / (n d)`` to its Nyquist wavenumber ``pi / d``; a bin's ``k`` is the geometric mean of
its modes' ``|k|`` and its power the arithmetic mean of their ``P``; empty bins are dropped. The zero mode is never
counted.

**The fits** are unweighted least squares on ``log10 P`` against ``log10 k`` over the bins whose ``k`` lies in a
range: :func:`fit_power_law` one line, :func:`fit_broken` a **continuous** broken line (two slopes meeting at the
break, ``log10 P = a + alpha_low (x - x_b)`` below ``x_b = log10 k_b`` and ``a + alpha_high (x - x_b)`` above),
the break chosen by the least total squared error on a fine grid of trial breaks (:data:`BREAK_TRIALS`) between the
range's third bin and its third-last, ``a``, ``alpha_low`` and ``alpha_high`` by linear least squares at each trial.
Continuity is the sources' form (Elmegreen, Kim & Staveley-Smith 2001's "two power laws ... meeting at" the
thickness, as read in ``READING_GAS_SPECTRA.md`` 2.1); it needs no bin edge at the break.

**Cost.** One FFT of the patch and a ``bincount``: a 1376^2 patch (4 kpc at 2.9 pc) in under a second.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

DEFAULT_BINS = 40  # logarithmic bins of |k| from the fundamental to Nyquist
BREAK_TRIALS = 400  # trial breaks between the range's third bin and its third-last
MIN_SIDE_BINS = 3  # each branch of a broken fit holds at least this many bins


class SpectrumError(ValueError):
    """An argument outside what the instrument measures."""


@dataclass(frozen=True)
class Spectrum:
    """An azimuthally averaged spectrum: per bin ``k`` (rad per length unit), ``power`` and the number of ``modes``."""

    k: np.ndarray
    power: np.ndarray
    modes: np.ndarray

    @property
    def wavelength(self) -> np.ndarray:
        return 2.0 * math.pi / self.k


@dataclass(frozen=True)
class PowerLaw:
    """``P = 10^intercept k^alpha`` over ``[k_lo, k_hi]``: alpha, its standard error, the rms residual (dex), bins."""

    alpha: float
    intercept: float
    stderr: float
    rms: float
    bins: int


@dataclass(frozen=True)
class BrokenLaw:
    """Two slopes meeting at ``k_break``: ``alpha_low`` below it in k (large scales), ``alpha_high`` above."""

    alpha_low: float
    alpha_high: float
    k_break: float
    rms: float
    bins_low: int
    bins_high: int

    @property
    def wavelength_break(self) -> float:
        return 2.0 * math.pi / self.k_break


def hann(n: int) -> np.ndarray:
    """The periodic-free Hann taper of length n: ``sin^2(pi (i + 1/2) / n)``, positive at every sample."""
    return np.sin(math.pi * (np.arange(n) + 0.5) / n) ** 2


def power_spectrum(field, spacing: float, window: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(kx, ky, P)`` of an n x n field sampled at ``spacing``: the module's normalisation, the zero mode included."""
    f = np.asarray(field, dtype=np.float64)
    if f.ndim != 2 or f.shape[0] != f.shape[1] or f.shape[0] < 8:
        raise SpectrumError(f"the field must be a square n x n array with n >= 8, got shape {f.shape}")
    spacing = float(spacing)
    if not (math.isfinite(spacing) and spacing > 0.0):
        raise SpectrumError(f"spacing must be positive, got {spacing}")
    if not np.all(np.isfinite(f)):
        raise SpectrumError("the field must be finite")
    n = f.shape[0]
    f = f - f.mean()
    w2 = 1.0
    if window:
        w = hann(n)
        f = f * np.outer(w, w)
        w2 = float(np.mean(w * w)) ** 2  # <w(i)^2 w(j)^2> for the separable window
    amplitude = np.fft.fft2(f)
    power = (amplitude.real**2 + amplitude.imag**2) * spacing**2 / (4.0 * math.pi**2 * n * n * w2)
    k = 2.0 * math.pi * np.fft.fftfreq(n, d=spacing)
    return k[None, :] * np.ones((n, 1)), k[:, None] * np.ones((1, n)), power


def azimuthal_average(kx, ky, power, spacing: float, bins: int = DEFAULT_BINS) -> Spectrum:
    """The module's log-binned azimuthal average; the zero mode and empty bins dropped."""
    kx, ky, power = (np.asarray(a, dtype=np.float64) for a in (kx, ky, power))
    n = power.shape[0]
    kmag = np.hypot(kx, ky).ravel()
    p = power.ravel()
    k_min, k_max = 2.0 * math.pi / (n * spacing), math.pi / spacing
    edges = np.geomspace(k_min, k_max, int(bins) + 1)
    keep = (kmag >= k_min) & (kmag <= k_max)
    index = np.clip(np.searchsorted(edges, kmag[keep], side="right") - 1, 0, int(bins) - 1)
    modes = np.bincount(index, minlength=int(bins))
    log_k = np.bincount(index, weights=np.log(kmag[keep]), minlength=int(bins))
    total = np.bincount(index, weights=p[keep], minlength=int(bins))
    filled = modes > 0
    return Spectrum(np.exp(log_k[filled] / modes[filled]), total[filled] / modes[filled], modes[filled])


def measure(field, spacing: float, bins: int = DEFAULT_BINS, window: bool = True) -> Spectrum:
    """The azimuthally averaged spectrum of a square patch: :func:`power_spectrum` then :func:`azimuthal_average`."""
    kx, ky, power = power_spectrum(field, spacing, window)
    return azimuthal_average(kx, ky, power, spacing, bins)


def stack(spectra) -> Spectrum:
    """The mean of several spectra on the same bins: realisations measured as one (each weighs the same)."""
    spectra = list(spectra)
    first = spectra[0]
    for other in spectra[1:]:
        if other.k.shape != first.k.shape or not np.allclose(other.k, first.k, rtol=1e-12):
            raise SpectrumError("spectra stack only on the same bins")
    power = np.mean([sp.power for sp in spectra], axis=0)
    return Spectrum(first.k, power, np.sum([sp.modes for sp in spectra], axis=0))


def _select(spectrum: Spectrum, k_lo: float, k_hi: float) -> tuple[np.ndarray, np.ndarray]:
    use = (spectrum.k >= k_lo) & (spectrum.k <= k_hi) & (spectrum.power > 0.0)
    return np.log10(spectrum.k[use]), np.log10(spectrum.power[use])


def fit_power_law(spectrum: Spectrum, k_lo: float, k_hi: float) -> PowerLaw:
    """One power law over the bins with ``k_lo <= k <= k_hi`` (at least three)."""
    x, y = _select(spectrum, k_lo, k_hi)
    if x.size < 3:
        raise SpectrumError(f"a power law needs three bins in [{k_lo}, {k_hi}], found {x.size}")
    design = np.stack([np.ones_like(x), x], axis=1)
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ coef
    dof = max(x.size - 2, 1)
    stderr = math.sqrt(float(resid @ resid) / dof / float(((x - x.mean()) ** 2).sum()))
    return PowerLaw(float(coef[1]), float(coef[0]), stderr, float(np.sqrt(np.mean(resid**2))), int(x.size))


def fit_broken(spectrum: Spectrum, k_lo: float, k_hi: float, trials: int = BREAK_TRIALS) -> BrokenLaw:
    """A continuous broken power law over ``[k_lo, k_hi]``, the break by the least total squared error."""
    x, y = _select(spectrum, k_lo, k_hi)
    if x.size < 2 * MIN_SIDE_BINS:
        raise SpectrumError(f"a broken law needs {2 * MIN_SIDE_BINS} bins in [{k_lo}, {k_hi}], found {x.size}")
    best = None
    for xb in np.linspace(x[MIN_SIDE_BINS - 1], x[-MIN_SIDE_BINS], int(trials)):
        below = np.minimum(x - xb, 0.0)
        above = np.maximum(x - xb, 0.0)
        design = np.stack([np.ones_like(x), below, above], axis=1)
        coef, *_ = np.linalg.lstsq(design, y, rcond=None)
        err = float(((y - design @ coef) ** 2).sum())
        if best is None or err < best[0]:
            best = (err, xb, coef)
    err, xb, coef = best
    return BrokenLaw(float(coef[1]), float(coef[2]), float(10.0**xb), math.sqrt(err / x.size),
                     int((x < xb).sum()), int((x >= xb).sum()))


def gaussian_field(n: int, spacing: float, power_of_k, seed: int) -> np.ndarray:
    """A periodic Gaussian random field on an n x n grid whose spectrum is ``power_of_k(|k|)`` (up to a constant).

    The instrument's own anchor (its tests): white complex Gaussian amplitudes times ``sqrt(P(|k|))``, the inverse
    FFT's real part, the zero mode removed. Its spectrum is exactly ``P`` in expectation, at every k, so a fit to it
    has a known answer."""
    rng = np.random.default_rng(int(seed))
    k = 2.0 * math.pi * np.fft.fftfreq(int(n), d=float(spacing))
    kmag = np.hypot(k[None, :], k[:, None])
    amp = np.zeros_like(kmag)
    nonzero = kmag > 0.0
    amp[nonzero] = np.sqrt(power_of_k(kmag[nonzero]))
    white = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    field = np.fft.ifft2(white * amp).real
    return field / field.std()
