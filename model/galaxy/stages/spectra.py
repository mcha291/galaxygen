"""The spectrum function and the filter integral (RENDER_PHYSICS §3a; BUILD_II V1, S38).

**Where the integral runs** (RENDER_PHYSICS §0's open ruling, settled at S38 as option (a),
D113 by the orchestrator): the viewer holds its filters as data and sends their curves with a
request; the model evaluates each emitting component's spectrum through each curve and
returns a response per cell per filter per component. The viewer multiplies those numbers
by its tone map and computes nothing else (rule D5), and there is still exactly one opinion
about what a component emits, held here beside the fields it reads (rule A9). No filter set
is held on this side: a request that names no curves gets no answer (§2a, "the viewer holds
the filters. The model holds no opinion about palette at all").

**What a response is.** For a component whose spectrum per unit area is F_λ, with
∫ F_λ dλ the component's published surface brightness, the response in a filter of
transmission S(λ) is ∫ F_λ S(λ) dλ — the energy the filter lets through, L☉/pc² for a
surface quantity. The transmission is the viewer's curve as sent, not renormalised: a
filter whose curve peaks at 1 passes a line at its peak whole.

**The components, first cut** (§2, components not colours; nothing is composited here):

- *Stars.* The population's own spectrum, from the eight bands the light stage integrates it in
  (the second cut, ruled at S38): per cell the eight points λL_λ at the bands' reference
  wavelengths (``disc_sed_u`` … ``disc_sed_k``), joined by power laws (L_λ linear in log–log)
  and continued outside U–K by a blackbody at the cell's colour temperature scaled to the end
  point [inferred: the join and the tails are stated choices, not a model atmosphere]. Through
  the table's own B and V this returns the table's magnitudes up to what the interpolation
  costs over a band's width, measured in ``tests/test_render.py``. The first cut — the
  bolometric light as one blackbody at the colour temperature — put twice the table's V light in
  V (M_V 0.71 mag bright, B − V +0.012) and is kept as ``blackbody_stellar_response``, the
  record the second is measured against.
- *Lines.* Each published line surface brightness times the curve's transmission at the
  line's wavelength: a line is narrower than any filter the viewer holds, so it is evaluated
  exactly rather than on a grid (§3). Only Hα is published per cell today (``nebular``);
  [O III], [S II] and [N II] wait on the photoionization grid (D184) and are listed as absent,
  not as zero (rule B9). Since S39 (V2) the line is two volumetric components: the HII
  regions' share placed around each ring by the pattern's contrast in the clouds' layer, and
  the diffuse gas's in its own published layer (``api/service.py``'s render).
- *Dust* (S39, BUILD_II V2; the orchestrator's ruling (a), D113). Three components from one
  grain model, the one the ``dust`` stage read its albedo, g and opacity from: Draine's
  tabulation of the Milky Way R_V = 3.1 model (``GRAIN_TABLE``, rows transcribed here).
  **Extinction** per filter is the transmission 10^(−0.4 A_V r) of the published face-on A_V,
  r = A_λ/A_V the table's own extinction cross-section per H (its fourth column, C_ext/H) at the
  filter's reference wavelength over the same column at the table's V row, 0.547 µm, whose
  4.868 × 10⁻²² cm² the dust stage's far-ultraviolet ratio is already divided by.
  **Scattering** per filter starts from the published V-band τ_sca scaled by the table's scattering
  cross section (albedo × C_ext) at the filter over the V row's; the light scattered is the stellar
  response times the share a mixed slab of that depth scatters in the dust stage's own convention
  (``scattered_share``: what the extinction removes less what the absorption keeps), not the
  ruling's optically thin τ_sca × the stars, which the disc's centre (τ_sca ≈ 30) makes thirty times
  the light there; its direction by a Henyey–Greenstein phase function at the published g
  (``disc_phase``). **Thermal** emission per filter is the
  published Σ_IR as a modified blackbody at the published T_d through the curve, its shape the
  dust stage's own emission spectrum at its emissivity index (``thermal_share``), normalised
  by the dust stage's own quadrature of it, so a curve holding the whole spectrum returns Σ_IR.

Wavelengths are in ångströms throughout, in air for the lines. The continuum grid runs from
0.1 µm to 1 mm since S39: RENDER_PHYSICS §3's 0.1–30 µm holds the stars and not the cold dust,
whose modified blackbody peaks near 130 µm at 20 K.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.stages import dust as _dust
from galaxy.stages.massive_stars import BOLTZMANN, LIGHT_SPEED, PLANCK
from galaxy.stages.photometry import BANDS, PASSBANDS

# hc/k in Å·K: the second radiation constant, from the SI 2019 defining constants (exact).
_C2 = PLANCK * LIGHT_SPEED / BOLTZMANN * 1.0e8

# The span a curve may cover: RENDER_PHYSICS §3's shared continuum grid, 0.1 µm, to 1 mm since S39 (the
# cold dust's modified blackbody; until S39 the grid stopped at 30 µm, 300 000 Å).
WAVELENGTH_MIN = 1_000.0
WAVELENGTH_MAX = 10_000_000.0
MAX_FILTERS = 8

# The stellar spectrum's anchors (S38's second cut): each of the table's eight bands at its reference
# wavelength, Å, read from SVO (photometry.PASSBANDS), in increasing wavelength.
SED_BANDS: tuple[str, ...] = BANDS
SED_WAVELENGTHS = np.array([PASSBANDS[b].reference for b in SED_BANDS])
# The corrections that make the joined spectrum's band means the table's (band_consistent).
SED_ITERATIONS = 12
SHAPES = ("gaussian", "box", "sampled")

# The lines a render can carry, by component name: wavelength in air, Å [recall: the standard
# air wavelengths of these transitions; not read from a source in this session]. Hα is the one
# published per cell; the rest are named so a request can be told they are absent rather than dark.
LINE_WAVELENGTHS: Mapping[str, float] = {
    "halpha": 6562.8,
    "hbeta": 4861.3,
    "oiii_5007": 5006.8,
    "sii_6716": 6716.4,
    "sii_6731": 6730.8,
    "nii_6583": 6583.5,
}

# Points per curve for the continuum integral: a Gaussian spans ±4 FWHM (its wings there are
# 10⁻¹⁹ of the peak) at 201 (a twenty-fifth of a FWHM apart: the trapezoid on a Gaussian times a
# smooth spectrum is exact to far below the magnitudes' thousandths; 801 until the band-consistent
# spectrum's twelve passes made it the route's cost), a box its width at 2001 log-spaced (a box may
# span the whole continuum grid), a sampled curve is resampled at 2001.
_GAUSSIAN_POINTS = 201
_GAUSSIAN_SPAN = 4.0
_BOX_POINTS = 2001
_SAMPLED_POINTS = 2001


class CurveError(ValueError):
    """A filter curve the integral cannot take."""


@dataclass(frozen=True)
class Curve:
    """One filter's transmission, as the viewer sent it."""

    name: str
    shape: str
    centre: float = math.nan  # Å; gaussian and box
    width: float = math.nan  # Å; the FWHM of a gaussian, the full width of a box
    wavelength: tuple[float, ...] = ()  # Å; sampled
    transmission: tuple[float, ...] = ()  # sampled

    def at(self, lam: np.ndarray) -> np.ndarray:
        """Transmission at wavelengths ``lam`` (Å): zero outside a box or a sampled curve."""
        lam = np.asarray(lam, dtype=float)
        if self.shape == "gaussian":
            return np.exp(-4.0 * math.log(2.0) * ((lam - self.centre) / self.width) ** 2)
        if self.shape == "box":
            return np.where(np.abs(lam - self.centre) <= 0.5 * self.width, 1.0, 0.0)
        return np.interp(lam, self.wavelength, self.transmission, left=0.0, right=0.0)

    def grid(self) -> np.ndarray:
        """The wavelengths (Å) the continuum integral is taken on."""
        if self.shape == "gaussian":
            lo = max(self.centre - _GAUSSIAN_SPAN * self.width, 0.5 * WAVELENGTH_MIN)
            return np.linspace(lo, self.centre + _GAUSSIAN_SPAN * self.width, _GAUSSIAN_POINTS)
        if self.shape == "box":
            return np.geomspace(self.centre - 0.5 * self.width, self.centre + 0.5 * self.width, _BOX_POINTS)
        # The sampled points themselves, and a fine grid between them, so neither a narrow feature
        # of the curve nor the blackbody's curvature between wide samples is lost.
        fine = np.linspace(self.wavelength[0], self.wavelength[-1], _SAMPLED_POINTS)
        return np.union1d(fine, np.asarray(self.wavelength))

    def reference(self) -> float:
        """The wavelength (Å) the dust's extinction curve is read at for this filter (S39): a Gaussian's
        or a box's centre, a sampled curve's transmission-weighted mean ∫λS dλ / ∫S dλ [inferred: the
        choice of reference; the two coincide for a symmetric curve]."""
        if self.shape != "sampled":
            return float(self.centre)
        lam = self.grid()
        s = self.at(lam)
        return float(np.trapezoid(lam * s, lam) / np.trapezoid(s, lam))

    def json(self) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "shape": self.shape}
        if self.shape == "sampled":
            out |= {"wavelength": list(self.wavelength), "transmission": list(self.transmission)}
        else:
            out |= {"centre": self.centre, ("fwhm" if self.shape == "gaussian" else "width"): self.width}
        return out


def _finite(value: Any, what: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise CurveError(f"{what} is not a number: {value!r}") from None
    if not math.isfinite(number):
        raise CurveError(f"{what} is not finite: {value!r}")
    return number


def parse_curves(raw: Any) -> tuple[Curve, ...]:
    """The viewer's filter set, as JSON decoded: a list of curves, each a Gaussian
    (``centre``, ``fwhm``), a box (``centre``, ``width``) or sampled (``wavelength``,
    ``transmission``), all in Å, each with a ``name``. Refused rather than guessed at."""
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_FILTERS:
        raise CurveError(f"a filter set is a list of 1 to {MAX_FILTERS} curves")
    curves: list[Curve] = []
    for k, entry in enumerate(raw):
        if not isinstance(entry, Mapping):
            raise CurveError(f"curve {k} is not an object")
        name = str(entry.get("name", f"f{k}"))
        shape = entry.get("shape")
        if shape not in SHAPES:
            raise CurveError(f"curve {name!r}: shape must be one of {list(SHAPES)}, got {shape!r}")
        allowed = {"name", "shape", "about"} | (
            {"centre", "fwhm"} if shape == "gaussian" else {"centre", "width"} if shape == "box" else {"wavelength", "transmission"}
        )
        unknown = set(entry) - allowed
        if unknown:
            raise CurveError(f"curve {name!r}: unknown keys {sorted(unknown)} for a {shape}")
        if shape == "sampled":
            lam, s = entry.get("wavelength"), entry.get("transmission")
            if not isinstance(lam, list) or not isinstance(s, list) or len(lam) != len(s) or len(lam) < 2:
                raise CurveError(f"curve {name!r}: wavelength and transmission are equal-length lists of at least 2")
            lam_v = tuple(_finite(v, f"{name} wavelength") for v in lam)
            s_v = tuple(_finite(v, f"{name} transmission") for v in s)
            if any(b <= a for a, b in zip(lam_v, lam_v[1:])):
                raise CurveError(f"curve {name!r}: wavelengths must increase")
            if any(v < 0.0 for v in s_v) or max(s_v) <= 0.0:
                raise CurveError(f"curve {name!r}: transmission must be non-negative and somewhere positive")
            if lam_v[0] < WAVELENGTH_MIN or lam_v[-1] > WAVELENGTH_MAX:
                raise CurveError(f"curve {name!r}: wavelengths must lie in {WAVELENGTH_MIN:g}-{WAVELENGTH_MAX:g} A")
            curves.append(Curve(name, shape, wavelength=lam_v, transmission=s_v))
            continue
        centre = _finite(entry.get("centre"), f"{name} centre")
        width = _finite(entry.get("fwhm" if shape == "gaussian" else "width"), f"{name} width")
        # A Gaussian's centre and a box's whole span must lie on the continuum grid.
        lo, hi = (centre, centre) if shape == "gaussian" else (centre - 0.5 * width, centre + 0.5 * width)
        if not (WAVELENGTH_MIN <= lo and hi <= WAVELENGTH_MAX) or width <= 0.0 or (shape == "gaussian" and width > centre):
            raise CurveError(
                f"curve {name!r}: centre must lie in {WAVELENGTH_MIN:g}-{WAVELENGTH_MAX:g} A, a box wholly, "
                "with a positive width, a Gaussian's FWHM no more than its centre"
            )
        curves.append(Curve(name, shape, centre=centre, width=width))
    return tuple(curves)


def planck_share(lam: np.ndarray, kelvin: np.ndarray) -> np.ndarray:
    """πB_λ(T)/(σT⁴) per Å, shape ``(*kelvin.shape, *lam.shape)``: a blackbody's spectrum per unit
    bolometric light, so that it integrates to 1 over all wavelengths. Zero where T is not positive."""
    lam = np.asarray(lam, dtype=float)
    t = np.asarray(kelvin, dtype=float)[..., None]
    ok = np.isfinite(t) & (t > 0.0)
    safe = np.where(ok, t, 1.0)
    x = _C2 / (lam * safe)
    with np.errstate(over="ignore"):
        shape = (15.0 / math.pi**4) * (_C2 / safe) ** 4 / lam**5 / np.expm1(np.minimum(x, 700.0))
    return np.where(ok, np.where(x < 700.0, shape, 0.0), np.nan)


def blackbody_response(curves: Sequence[Curve], kelvin: np.ndarray) -> np.ndarray:
    """``(*kelvin.shape, n_filters)``: the share of a blackbody's light each curve passes,
    ∫ πB_λ(T)/(σT⁴) S(λ) dλ. NaN where the temperature is (no light has no colour, rule B9)."""
    kelvin = np.asarray(kelvin, dtype=float)
    out = np.empty((*kelvin.shape, len(curves)))
    for k, curve in enumerate(curves):
        lam = curve.grid()
        out[..., k] = np.trapezoid(planck_share(lam, kelvin) * curve.at(lam), lam, axis=-1)
    return out


def line_response(curves: Sequence[Curve], wavelength: float) -> np.ndarray:
    """``(n_filters,)``: each curve's transmission at one line's wavelength (Å)."""
    return np.array([float(curve.at(np.array([wavelength]))[0]) for curve in curves])


def blackbody_stellar_response(surface_brightness: np.ndarray, kelvin: np.ndarray, curves: Sequence[Curve]) -> np.ndarray:
    """``(*shape, n_filters)``: S38's first cut, kept as the record the second is measured against — the
    bolometric surface brightness as one blackbody at the colour temperature, through each curve, L☉/pc²
    if the surface brightness is. Zero where there is no light; NaN where there is light with no
    temperature. It puts about twice the table's V light in V (tests/test_render.py)."""
    light = np.asarray(surface_brightness, dtype=float)
    share = blackbody_response(curves, kelvin)
    return np.where((light > 0.0)[..., None], light[..., None] * share, 0.0)


def sed_density(lam: np.ndarray, nu_l_nu: np.ndarray, kelvin: np.ndarray) -> np.ndarray:
    """L_λ per Å at wavelengths ``lam`` (Å), shape ``(*shape, *lam.shape)``, of the spectrum the eight
    band points ``nu_l_nu`` (``(*shape, 8)``, λL_λ at each band's reference wavelength, in the order of
    ``SED_WAVELENGTHS``) describe: a power law between neighbouring points (L_λ linear in log–log), and
    outside U–K a blackbody at ``kelvin`` scaled to the end point it meets [inferred: the stated join].
    Zero where the population has no light; NaN in a tail where it has light and no temperature."""
    lam = np.asarray(lam, dtype=float)
    points = np.asarray(nu_l_nu, dtype=float) / SED_WAVELENGTHS  # L_λ at the anchors
    lit = (points > 0.0).any(axis=-1)
    log_p = np.log(np.maximum(points, 1e-300))
    log_x = np.log(SED_WAVELENGTHS)
    x = np.log(np.clip(lam, SED_WAVELENGTHS[0], SED_WAVELENGTHS[-1]))
    k = np.clip(np.searchsorted(log_x, x, side="right") - 1, 0, log_x.size - 2)
    w = (x - log_x[k]) / (log_x[k + 1] - log_x[k])
    out = np.exp(log_p[..., k] * (1.0 - w) + log_p[..., k + 1] * w)
    t = np.asarray(kelvin, dtype=float)
    # The tails, evaluated only where a curve reaches past U or K.
    for side, end in ((lam < SED_WAVELENGTHS[0], 0), (lam > SED_WAVELENGTHS[-1], -1)):
        if side.any():
            anchor = SED_WAVELENGTHS[end : end + 1 if end == 0 else None]
            tail = points[..., end : end + 1 if end == 0 else None] * planck_share(lam[side], t) / planck_share(anchor, t)
            out[..., side] = tail
    return np.where(lit[..., None], out, 0.0)


def sed_response(nu_l_nu: np.ndarray, kelvin: np.ndarray, curves: Sequence[Curve]) -> np.ndarray:
    """``(*shape, n_filters)``: the eight-band spectrum (``sed_density``) through each curve, ∫ L_λ S dλ,
    in the unit λL_λ was given in (L☉/pc² for the disc's fields, L☉ for the bulge's)."""
    nu_l_nu = np.asarray(nu_l_nu, dtype=float)
    out = np.empty((*nu_l_nu.shape[:-1], len(curves)))
    for k, curve in enumerate(curves):
        lam = curve.grid()
        out[..., k] = np.trapezoid(sed_density(lam, nu_l_nu, kelvin) * curve.at(lam), lam, axis=-1)
    return out


def band_consistent(nu_l_nu: np.ndarray, kelvin: np.ndarray, iterations: int = SED_ITERATIONS) -> np.ndarray:
    """The anchor points, ``(*shape, 8)``, moved so that the joined spectrum's mean L_λ through each band's
    own curve (``band_curve``) is the band's published value, rather than its value at the band's reference
    wavelength: a spectrum peaked at B, read at B's centre, is brighter than its mean over B's 950 Å, and the
    point-anchored join read the table's B 0.076 mag faint (S38). A fixed number of multiplicative
    corrections, each band's point scaled by its target over its current mean (A1: a step count fixed in
    advance, its residual measured in tests/test_render.py)."""
    target = np.asarray(nu_l_nu, dtype=float) / SED_WAVELENGTHS
    curves = [band_curve(b) for b in SED_BANDS]
    norm = np.array([np.trapezoid(c.at(c.grid()), c.grid()) for c in curves])
    points = target.copy()
    for _ in range(iterations):
        mean = sed_response(points * SED_WAVELENGTHS, kelvin, curves) / norm
        points = np.where(mean > 0.0, points * target / np.where(mean > 0.0, mean, 1.0), points)
    return points * SED_WAVELENGTHS


def stellar_response(nu_l_nu: np.ndarray, kelvin: np.ndarray, curves: Sequence[Curve]) -> np.ndarray:
    """``(*shape, n_filters)``: the stellar component through each curve — the eight band points made
    band-consistent (``band_consistent``), joined (``sed_density``) and integrated (``sed_response``)."""
    return sed_response(band_consistent(nu_l_nu, kelvin), kelvin, curves)


def band_curve(band: str) -> Curve:
    """The table's own band as a curve: a Gaussian at its reference wavelength with its FWHM, both read
    from SVO (``photometry.PASSBANDS``); the Gaussian shape is [inferred]. What the render gate sends."""
    p = PASSBANDS[band]
    return Curve(band, "gaussian", centre=p.reference, width=p.fwhm)


# --- the dust (S39, BUILD_II V2) ------------------------------------------------------------------------

# Draine's tabulation of the Milky Way R_V = 3.1 grain model (Weingartner & Draine 2001 as renormalised by
# Draine 2003), kext_albedo_WD_MW_3.1_60_D03.all, the file the dust stage's albedo, g, far-ultraviolet ratio
# and opacity were read from at S31 [verified: https://www.astro.princeton.edu/~draine/dust/extcurvs/
# kext_albedo_WD_MW_3.1_60_D03.all, rows read at S39 as printed]. Columns kept, in the file's order:
# lambda (micron), albedo, <cos>, C_ext/H (cm^2 per H nucleon: the extinction column), K_abs (cm^2 per g of
# dust). The file runs from 1e4 micron down to 1e-4 in steps of 0.01 dex; kept here, in increasing
# wavelength, every row between 0.30 and 0.66 micron, one row per 0.05 dex from 0.1 to 3.5 micron elsewhere
# and per 0.1 dex beyond, the named filter rows among them, and the rows the dust stage's constants quote
# (0.151356, 0.547, 155.9 micron). Read through a summarising fetch, row by row; S31's lesson (a fetch misread
# four rows) is answered by the identity every row must satisfy, K_abs x M_dust/H = (1 - albedo) C_ext
# (the absorption cross-section two ways), asserted in tests/test_render.py, and by the rows the S31
# constants quote, asserted equal.
GRAIN_DUST_MASS_PER_H = 1.398e-26  # g of dust per H nucleon: the table's header (as quoted at S31, D180)
GRAIN_TABLE: tuple[tuple[float, float, float, float, float], ...] = (
    (0.100000, 0.2761, 0.6501, 2.083e-21, 1.078e05),
    (0.112202, 0.3302, 0.6636, 1.645e-21, 7.879e04),
    (0.125893, 0.3632, 0.6789, 1.420e-21, 6.468e04),
    (0.141254, 0.3863, 0.6766, 1.268e-21, 5.567e04),
    (0.151356, 0.4068, 0.6633, 1.193e-21, 5.061e04),
    (0.158489, 0.4262, 0.6550, 1.153e-21, 4.732e04),
    (0.177828, 0.4924, 0.6190, 1.120e-21, 4.064e04),
    (0.199526, 0.5212, 0.5774, 1.203e-21, 4.120e04),
    (0.217500, 0.5046, 0.5544, 1.308e-21, 4.633e04),  # "2175 A feature"
    (0.218776, 0.5060, 0.5531, 1.306e-21, 4.613e04),
    (0.223872, 0.5151, 0.5492, 1.281e-21, 4.443e04),
    (0.251189, 0.5762, 0.5428, 1.072e-21, 3.249e04),
    (0.281838, 0.6008, 0.5503, 9.452e-22, 2.698e04),
    (0.301995, 0.6108, 0.5571, 8.909e-22, 2.480e04),
    (0.309029, 0.6150, 0.5591, 8.732e-22, 2.404e04),
    (0.316228, 0.6195, 0.5610, 8.555e-22, 2.328e04),
    (0.323594, 0.6239, 0.5629, 8.383e-22, 2.255e04),
    (0.331131, 0.6283, 0.5647, 8.215e-22, 2.184e04),
    (0.338844, 0.6324, 0.5662, 8.051e-22, 2.117e04),
    (0.346737, 0.6362, 0.5676, 7.892e-22, 2.053e04),
    (0.350000, 0.6376, 0.5681, 7.828e-22, 2.029e04),  # "u (Stromgren) filter"
    (0.354814, 0.6396, 0.5687, 7.736e-22, 1.994e04),
    (0.355000, 0.6397, 0.5687, 7.733e-22, 1.993e04),  # "u (SDSS) filter"
    (0.363078, 0.6428, 0.5695, 7.583e-22, 1.937e04),
    (0.363500, 0.6430, 0.5696, 7.576e-22, 1.934e04),  # "U filter"
    (0.371535, 0.6459, 0.5700, 7.431e-22, 1.882e04),
    (0.380189, 0.6489, 0.5703, 7.279e-22, 1.828e04),
    (0.389045, 0.6518, 0.5702, 7.127e-22, 1.775e04),
    (0.398107, 0.6546, 0.5699, 6.973e-22, 1.723e04),
    (0.407380, 0.6573, 0.5693, 6.818e-22, 1.671e04),
    (0.410000, 0.6581, 0.5691, 6.775e-22, 1.657e04),  # "v (Stromgren) filter"
    (0.416869, 0.6601, 0.5685, 6.662e-22, 1.620e04),
    (0.426580, 0.6627, 0.5674, 6.505e-22, 1.569e04),
    (0.436516, 0.6653, 0.5661, 6.348e-22, 1.519e04),
    (0.440500, 0.6662, 0.5655, 6.286e-22, 1.501e04),  # "B filter"
    (0.446684, 0.6676, 0.5645, 6.192e-22, 1.472e04),
    (0.457088, 0.6697, 0.5626, 6.036e-22, 1.426e04),
    (0.467735, 0.6716, 0.5604, 5.882e-22, 1.382e04),
    (0.468500, 0.6717, 0.5602, 5.871e-22, 1.379e04),  # "g (SDSS) filter"
    (0.470000, 0.6719, 0.5599, 5.850e-22, 1.373e04),  # "b (Stromgren)"
    (0.478630, 0.6731, 0.5579, 5.729e-22, 1.339e04),
    (0.486100, 0.6740, 0.5561, 5.627e-22, 1.312e04),  # "H beta (4-2)"
    (0.489779, 0.6744, 0.5552, 5.577e-22, 1.299e04),
    (0.501187, 0.6754, 0.5522, 5.427e-22, 1.260e04),
    (0.512861, 0.6762, 0.5489, 5.277e-22, 1.222e04),
    (0.524807, 0.6768, 0.5454, 5.129e-22, 1.186e04),
    (0.537032, 0.6772, 0.5415, 4.983e-22, 1.150e04),
    (0.547000, 0.6774, 0.5383, 4.868e-22, 1.123e04),  # "V filter": the dust stage's albedo_V and g
    (0.549541, 0.6774, 0.5374, 4.839e-22, 1.116e04),
    (0.555000, 0.6774, 0.5355, 4.778e-22, 1.102e04),  # "y (Stromgren) filter"
    (0.562341, 0.6774, 0.5330, 4.697e-22, 1.084e04),
    (0.575440, 0.6772, 0.5283, 4.558e-22, 1.052e04),
    (0.588844, 0.6769, 0.5233, 4.421e-22, 1.022e04),
    (0.602560, 0.6763, 0.5181, 4.287e-22, 9.925e03),
    (0.616500, 0.6755, 0.5127, 4.155e-22, 9.645e03),  # "r (SDSS) filter"
    (0.616595, 0.6755, 0.5126, 4.155e-22, 9.643e03),
    (0.630958, 0.6745, 0.5069, 4.025e-22, 9.370e03),
    (0.641500, 0.6737, 0.5027, 3.933e-22, 9.179e03),  # "R_J filter"
    (0.645654, 0.6734, 0.5010, 3.898e-22, 9.105e03),
    (0.649200, 0.6731, 0.4996, 3.868e-22, 9.044e03),  # "R_C filter"
    (0.656200, 0.6725, 0.4967, 3.810e-22, 8.925e03),  # "H alpha (3-2)"
    (0.707946, 0.6672, 0.4754, 3.416e-22, 8.130e03),
    (0.794328, 0.6553, 0.4411, 2.878e-22, 7.095e03),
    (0.891251, 0.6393, 0.4043, 2.411e-22, 6.219e03),
    (1.00000, 0.6153, 0.3630, 2.021e-22, 5.560e03),
    (1.12202, 0.5945, 0.3192, 1.676e-22, 4.861e03),
    (1.25000, 0.5706, 0.2813, 1.417e-22, 4.352e03),  # "J filter"
    (1.25893, 0.5690, 0.2790, 1.402e-22, 4.321e03),
    (1.41254, 0.5503, 0.2451, 1.157e-22, 3.722e03),
    (1.58489, 0.5247, 0.2155, 9.606e-23, 3.265e03),
    (1.65000, 0.5151, 0.2054, 8.995e-23, 3.120e03),  # "H filter"
    (1.77828, 0.4963, 0.1864, 7.948e-23, 2.863e03),
    (1.99526, 0.4648, 0.1561, 6.543e-23, 2.505e03),
    (2.20000, 0.4358, 0.1288, 5.525e-23, 2.230e03),  # "K filter"
    (2.23872, 0.4304, 0.1237, 5.357e-23, 2.182e03),
    (2.51189, 0.3933, 0.0900, 4.356e-23, 1.890e03),
    (2.81838, 0.3539, 0.0560, 3.519e-23, 1.626e03),
    (3.16228, 0.3119, 0.0246, 2.829e-23, 1.392e03),
    (3.54813, 0.2686, -0.0017, 2.268e-23, 1.187e03),
    (3.98107, 0.2249, -0.0219, 1.818e-23, 1.008e03),
    (5.01187, 0.1428, -0.0461, 1.190e-23, 7.294e02),
    (6.30957, 0.0718, -0.0550, 9.090e-24, 6.034e02),
    (7.94328, 0.0186, -0.0515, 1.290e-23, 9.052e02),
    (8.91251, 0.0049, -0.0451, 3.157e-23, 2.247e03),
    (10.0000, 0.0030, -0.0354, 3.736e-23, 2.664e03),
    (11.2202, 0.0028, -0.0313, 2.444e-23, 1.743e03),
    (12.5893, 0.0028, -0.0293, 1.505e-23, 1.074e03),
    (15.8489, 0.0012, -0.0279, 1.286e-23, 9.185e02),
    (19.9526, 0.0005, -0.0229, 1.476e-23, 1.055e03),
    (25.1189, 0.0003, -0.0216, 9.952e-24, 7.115e02),
    (31.6228, 0.0002, -0.0203, 6.555e-24, 4.687e02),
    (39.8107, 0.0001, -0.0171, 4.186e-24, 2.993e02),
    (50.1187, 0.0001, -0.0103, 2.582e-24, 1.846e02),
    (63.0957, 0.0001, 0.0023, 1.568e-24, 1.121e02),
    (79.4328, 0.0000, 0.0081, 9.444e-25, 6.754e01),
    (100.000, 0.0000, 0.0048, 5.726e-25, 4.095e01),
    (155.900, 0.0000, -0.0005, 2.298e-25, 1.643e01),  # "MIPS 3": the dust stage's opacity reference
    (158.489, 0.0000, -0.0005, 2.216e-25, 1.585e01),
    (199.526, 0.0000, -0.0005, 1.369e-25, 9.791e00),
    (245.471, 0.0000, -0.0003, 8.966e-26, 6.412e00),
    (251.189, 0.0000, -0.0003, 8.533e-26, 6.102e00),
    (398.107, 0.0000, -0.0001, 3.493e-26, 2.498e00),
    (630.957, 0.0000, -0.0000, 1.343e-26, 9.605e-01),
    (1000.00, 0.0000, -0.0000, 6.174e-27, 4.416e-01),
)
_GRAIN = np.array(GRAIN_TABLE)
GRAIN_WAVELENGTHS = _GRAIN[:, 0] * 1.0e4  # Å
GRAIN_V_WAVELENGTH = 5470.0  # Å: the table's "V filter" row
_V_ROW = int(np.flatnonzero(GRAIN_WAVELENGTHS == GRAIN_V_WAVELENGTH)[0])
GRAIN_V_EXTINCTION = float(_GRAIN[_V_ROW, 3])  # cm² per H
GRAIN_V_ALBEDO = float(_GRAIN[_V_ROW, 1])


def _grain_log_log(lam: np.ndarray, column: int) -> np.ndarray:
    """A positive column of the grain table at wavelengths ``lam`` (Å), linear in log–log between rows,
    held at the end rows outside 0.1 µm – 1 mm."""
    x = np.log(np.clip(np.asarray(lam, dtype=float), GRAIN_WAVELENGTHS[0], GRAIN_WAVELENGTHS[-1]))
    return np.exp(np.interp(x, np.log(GRAIN_WAVELENGTHS), np.log(_GRAIN[:, column])))


def extinction_ratio(lam: np.ndarray) -> np.ndarray:
    """A_λ / A_V at wavelengths ``lam`` (Å): the table's C_ext/H there over its V row's. Extinction in
    magnitudes is 1.086 N_H C_ext, so the column density cancels and the ratio is the table's alone."""
    return _grain_log_log(lam, 3) / GRAIN_V_EXTINCTION


def albedo(lam: np.ndarray) -> np.ndarray:
    """The table's albedo at wavelengths ``lam`` (Å), linear in log λ between rows (it reaches zero in the
    far infrared, where a log–log join would not)."""
    x = np.log(np.clip(np.asarray(lam, dtype=float), GRAIN_WAVELENGTHS[0], GRAIN_WAVELENGTHS[-1]))
    return np.interp(x, np.log(GRAIN_WAVELENGTHS), _GRAIN[:, 1])


def filter_references(curves: Sequence[Curve]) -> np.ndarray:
    """``(n_filters,)``: each curve's reference wavelength (Å), where the grain table is read for it."""
    return np.array([c.reference() for c in curves])


def extinction_transmission(a_v: np.ndarray, curves: Sequence[Curve]) -> np.ndarray:
    """``(*a_v.shape, n_filters)``: 10^(−0.4 A_V r) per filter, the share of light a face-on column of the
    published A_V lets through at each filter's reference wavelength. 1 where there is no dust."""
    ratio = extinction_ratio(filter_references(curves))
    a_v = np.nan_to_num(np.asarray(a_v, dtype=float), nan=0.0)
    return 10.0 ** (-0.4 * a_v[..., None] * ratio)


def scattering_depth(tau_sca_v: np.ndarray, curves: Sequence[Curve]) -> np.ndarray:
    """``(*shape, n_filters)``: the published V-band scattering depth moved to each filter by the table's
    scattering cross-section, albedo × C_ext, there over the V row's."""
    lam = filter_references(curves)
    share = albedo(lam) * extinction_ratio(lam) / GRAIN_V_ALBEDO
    return np.nan_to_num(np.asarray(tau_sca_v, dtype=float), nan=0.0)[..., None] * share


def extinction_depth(a_v: np.ndarray, curves: Sequence[Curve]) -> np.ndarray:
    """``(*a_v.shape, n_filters)``: the face-on extinction optical depth per filter, A_V r / 1.0857 — the
    −ln of ``extinction_transmission``."""
    ratio = extinction_ratio(filter_references(curves))
    return _dust.optical_depth(np.nan_to_num(np.asarray(a_v, dtype=float), nan=0.0)[..., None] * ratio)


def scattered_share(tau_ext: np.ndarray, tau_sca: np.ndarray) -> np.ndarray:
    """The share of a uniform mixed slab's light its dust scatters, all directions together: what the slab's
    extinction removes, 1 − P_esc(τ_ext), less what its absorption keeps, 1 − P_esc(τ_ext − τ_sca) — the dust
    stage's own convention, in which a scattered photon is neither lost nor sent further (``dust.py``), so that
    the light a frame's extinction takes from a line of sight and the scattered light it adds back leave exactly
    the light the stage says escapes. Replaces, at S39, the ruling's optically thin τ_sca × the stars, which the
    frame measured at 12 times this over the whole galaxy: the disc's centre has τ_sca near 30, and a thin
    scatterer there scatters thirty times the light it holds (tests/test_render.py keeps it as the record)."""
    tau_ext = np.asarray(tau_ext, dtype=float)
    tau_abs = np.maximum(tau_ext - np.asarray(tau_sca, dtype=float), 0.0)
    return _dust.slab_absorbed_fraction(tau_ext) - _dust.slab_absorbed_fraction(tau_abs)


# The scattering phase function [verified: Bosschaart & Olofsson 2026, arXiv:2604.08379 (HTML), eq. 3,
# "In its single-component form, the HG phase function is defined as" HG(g, θ) = (1/4π)(1 − g²)/
# (1 − 2g cos θ + g²)^(3/2), normalised to one over the sphere; the form is Henyey & Greenstein 1941's].
PHASE_POINTS = 21  # the view's |cos i| from 0 (edge-on) to 1 (face-on), evenly spaced
_PHASE_AZIMUTHS = 720


def henyey_greenstein(g: float, cos_theta: np.ndarray) -> np.ndarray:
    """The Henyey–Greenstein phase function per steradian at scattering angle θ, asymmetry ``g``."""
    c = np.asarray(cos_theta, dtype=float)
    return (1.0 - g * g) / (4.0 * math.pi * (1.0 + g * g - 2.0 * g * c) ** 1.5)


def disc_phase(g: float, cos_view: np.ndarray) -> np.ndarray:
    """4π × the phase function averaged over light arriving in the disc's plane from every azimuth, seen
    along a direction at |cos i| = ``cos_view`` to the disc's axis: the factor that turns the scattered
    power per unit area (all directions) into what one view receives. Light arriving in the plane is the
    thin mixed slab's limit, where the grazing rays carry the most [inferred: the geometry]. Face-on every
    scattering angle is 90°, (1 − g²)/(1 + g²)^(3/2); averaged over the sphere of views the factor is 1,
    since scattering moves light and makes none."""
    mu = np.clip(np.asarray(cos_view, dtype=float), 0.0, 1.0)
    psi = (np.arange(_PHASE_AZIMUTHS) + 0.5) * (2.0 * math.pi / _PHASE_AZIMUTHS)
    cos_theta = np.sqrt(1.0 - mu**2)[..., None] * np.cos(psi)
    return 4.0 * math.pi * henyey_greenstein(g, cos_theta).mean(axis=-1)


def phase_table(g: float) -> dict[str, list[float]]:
    """``disc_phase`` at PHASE_POINTS evenly spaced |cos i|, for a viewer to read by its own view."""
    mu = np.linspace(0.0, 1.0, PHASE_POINTS)
    return {"cos_view": mu.tolist(), "factor": disc_phase(g, mu).tolist()}


def thermal_share(lam: np.ndarray, kelvin: np.ndarray, kappa_ref: float, wavelength_ref_um: float, beta: float,
                  power: np.ndarray | None = None) -> np.ndarray:
    """The dust's modified blackbody per Å per unit emitted power, ``(*kelvin.shape, *lam.shape)``: the dust
    stage's emission spectrum (``dust.emission_per_mass``, L_ν per gram) at wavelengths ``lam`` (Å), turned
    to L_λ and divided by the dust stage's own quadrature of it over 1 µm – 1 m (``dust.emitted_per_mass``),
    so that it integrates to one over that span exactly as Σ_IR was integrated. Zero where the dust absorbs
    nothing (no temperature). The opacity's normalisation cancels; its slope β does not."""
    lam = np.asarray(lam, dtype=float)
    t = np.asarray(kelvin, dtype=float)
    heated = np.isfinite(t) & (t > 0.0)
    safe = np.where(heated, t, 1.0)
    lam_cm = lam * 1.0e-8
    per_nu = _dust.emission_per_mass(lam / 1.0e4, safe, kappa_ref, wavelength_ref_um, beta)  # erg/s/Hz/g
    per_angstrom = per_nu * LIGHT_SPEED / lam_cm**2 * 1.0e-8  # erg/s/Å/g
    if power is None:
        power = _dust.emitted_per_mass(safe, kappa_ref, wavelength_ref_um, beta)  # erg/s/g
    return np.where(heated[..., None], per_angstrom / np.asarray(power)[..., None], 0.0)


def thermal_response(sigma_ir: np.ndarray, kelvin: np.ndarray, curves: Sequence[Curve], kappa_ref: float,
                     wavelength_ref_um: float, beta: float) -> np.ndarray:
    """``(*shape, n_filters)``: the published infrared surface brightness at the published temperature through
    each curve, Σ_IR ∫ φ_λ(T_d) S(λ) dλ, in Σ_IR's unit. Zero where the dust emits nothing."""
    sigma = np.nan_to_num(np.asarray(sigma_ir, dtype=float), nan=0.0)
    t = np.asarray(kelvin, dtype=float)
    power = _dust.emitted_per_mass(np.where(np.isfinite(t) & (t > 0.0), t, 1.0), kappa_ref, wavelength_ref_um, beta)
    out = np.empty((*sigma.shape, len(curves)))
    for k, curve in enumerate(curves):
        lam = curve.grid()
        share = np.trapezoid(thermal_share(lam, t, kappa_ref, wavelength_ref_um, beta, power) * curve.at(lam), lam, axis=-1)
        out[..., k] = np.where(sigma > 0.0, sigma * share, 0.0)
    return out
