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

- *Stars.* The disc's published bolometric surface brightness at its published colour
  temperature, the shape a blackbody's: F_λ = Σ_L · πB_λ(T)/(σT⁴). A population is not a
  blackbody, and ``disc_light_temperature`` is a correlated colour temperature, not a
  temperature of anything (``light.py``); how far the first cut's colour and magnitudes sit
  from the eight-band table the same populations are integrated in is measured by
  ``tests/test_render.py`` and stated there. The table-based spectrum (the eight bands as an
  SED) or the population's own temperature mix is the second cut, owed.
- *Lines.* Each published line surface brightness times the curve's transmission at the
  line's wavelength: a line is narrower than any filter the viewer holds, so it is evaluated
  exactly rather than on a grid (§3). Only Hα is published per cell today (``nebular``);
  [O III], [S II] and [N II] wait on the photoionization grid (D184) and are listed as absent,
  not as zero (rule B9).
- *Dust.* Not a spectrum: occlusion. The published face-on A_V per cell (``ism``) and, where
  the model publishes it, E(B − V) (``dust``); no extinction curve is published, so no
  per-filter ratio is computed here.

Wavelengths are in ångströms throughout, in air for the lines.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.stages.massive_stars import BOLTZMANN, LIGHT_SPEED, PLANCK

# hc/k in Å·K: the second radiation constant, from the SI 2019 defining constants (exact).
_C2 = PLANCK * LIGHT_SPEED / BOLTZMANN * 1.0e8

# The span a curve may cover: RENDER_PHYSICS §3's shared continuum grid, 0.1–30 µm.
WAVELENGTH_MIN = 1_000.0
WAVELENGTH_MAX = 300_000.0
MAX_FILTERS = 8
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
# 10⁻¹⁹ of the peak) at 801, a box its width at 2001 log-spaced (a box may span the whole
# continuum grid), a sampled curve is resampled at 2001.
_GAUSSIAN_POINTS = 801
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


def stellar_response(surface_brightness: np.ndarray, kelvin: np.ndarray, curves: Sequence[Curve]) -> np.ndarray:
    """``(*shape, n_filters)``: the stellar component through each curve, L☉/pc² if the surface
    brightness is. Zero where there is no light; NaN where there is light with no temperature."""
    light = np.asarray(surface_brightness, dtype=float)
    share = blackbody_response(curves, kelvin)
    return np.where((light > 0.0)[..., None], light[..., None] * share, 0.0)
