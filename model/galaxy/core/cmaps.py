"""The colour stops behind the closed cmap vocabulary (rule A9).

A field declaration names a ramp — a cmap, a scale, optional bounds — and that
declaration is the *only* opinion about how the field is drawn. But naming
``viridis`` is only half an answer: something has to know what viridis is, and
if that something is the viewer then every client reimplements it and they
disagree. So the stops live here, beside the closed vocabulary they belong to,
and the API publishes them. A viewer holds no colour of its own; a test asserts
it (``tests/test_viewer.py``).

Stops are anchors, not a 256-entry table: the client interpolates linearly in
sRGB between them. Nine or ten anchors is what the shape of these maps needs —
they were designed to be perceptually smooth, so linear interpolation between
evenly spaced samples does not reintroduce a band the map was built to avoid
``[inferred]``. The values are the standard samples of matplotlib's maps and
ColorBrewer's ``[recall: matplotlib viridis/magma/inferno/plasma/cividis and
coolwarm; ColorBrewer Greys-9 and RdBu-11]``, which is a recall tag and not a
verified one: nothing in this repository can check them against their source.
What *is* checked here is every property the renderer depends on.

**A diverging map has an odd number of stops**, so its middle anchor is its
neutral point. That is what makes ``meaningful_zero`` drawable: a field whose
zero means something is drawn with zero at the middle stop, and a field whose
zero does not is not. A diverging map with an even count has no defined middle
and would put the neutral colour half a stop off, silently.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

_HEX = re.compile(r"^#[0-9a-f]{6}$")


class UnknownCmap(ValueError):
    """A ramp named a cmap outside the closed vocabulary."""


class CmapError(ValueError):
    """A cmap definition violates the contract this module guarantees."""


# The closed set. Extending it is a deliberate edit here, with stops and a
# DECISIONS.md entry — never a side effect of declaring a field.
CMAPS: tuple[str, ...] = (
    "viridis",
    "magma",
    "inferno",
    "plasma",
    "cividis",
    "greys",
    "coolwarm",  # diverging
    "RdBu",  # diverging
    "blackbody",  # a physical colour, not a data ramp: see blackbody_hex
)

DIVERGING: frozenset[str] = frozenset({"coolwarm", "RdBu"})

# The blackbody map's span. A ramp naming it must declare exactly these bounds on a log
# scale, because its stops are the colours of these temperatures and nothing else.
BLACKBODY_KELVIN: tuple[float, float] = (2000.0, 40000.0)
_BLACKBODY_STOPS = 17


def _lobe(lam: float, mu: float, below: float, above: float) -> float:
    s = below if lam < mu else above
    return math.exp(-0.5 * ((lam - mu) / s) ** 2)


def blackbody_rgb(kelvin: float) -> tuple[float, float, float]:
    """The **linear** sRGB colour of a blackbody, brightest channel at 1: chromaticity only.

    Computed, not recalled: Planck's law integrated against the CIE 1931 2° colour
    matching functions in Wyman, Sloan and Shirley's multi-lobe fit, then XYZ to linear
    sRGB (D65) ``[recall: Wyman, Sloan & Shirley 2013, JCGT 2(2); IEC 61966-2-1]``. A
    colour outside the sRGB gamut is clipped at zero before normalising, which
    desaturates the hottest and coolest ends a little. What a star is as *bright* is its
    luminosity, published separately; this is only what colour it is.
    """
    x = y = z = 0.0
    for lam in range(380, 781, 5):  # nm
        planck = lam**-5.0 / math.expm1(1.438777e7 / (lam * kelvin))
        x += planck * (1.056 * _lobe(lam, 599.8, 37.9, 31.0) + 0.362 * _lobe(lam, 442.0, 16.0, 26.7)
                       - 0.065 * _lobe(lam, 501.1, 20.4, 26.2))
        y += planck * (0.821 * _lobe(lam, 568.8, 46.9, 40.5) + 0.286 * _lobe(lam, 530.9, 16.3, 31.1))
        z += planck * (1.217 * _lobe(lam, 437.0, 11.8, 36.0) + 0.681 * _lobe(lam, 459.0, 26.0, 13.8))
    rgb = (
        max(0.0, 3.2406 * x - 1.5372 * y - 0.4986 * z),
        max(0.0, -0.9689 * x + 1.8758 * y + 0.0415 * z),
        max(0.0, 0.0557 * x - 0.2040 * y + 1.0570 * z),
    )
    top = max(rgb)
    return (rgb[0] / top, rgb[1] / top, rgb[2] / top)


def blackbody_hex(kelvin: float) -> str:
    """:func:`blackbody_rgb` through the sRGB transfer curve, as a stop."""

    def encode(c: float) -> int:
        s = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
        return round(255 * min(1.0, max(0.0, s)))

    return "#" + "".join(f"{encode(c):02x}" for c in blackbody_rgb(kelvin))


def _blackbody_stops() -> tuple[str, ...]:
    lo, hi = (math.log10(k) for k in BLACKBODY_KELVIN)
    return tuple(blackbody_hex(10 ** (lo + (hi - lo) * i / (_BLACKBODY_STOPS - 1))) for i in range(_BLACKBODY_STOPS))


_STOPS: dict[str, tuple[str, ...]] = {
    # Evenly spaced in log T across BLACKBODY_KELVIN, so a log ramp over those bounds
    # lands each temperature on its own colour.
    "blackbody": _blackbody_stops(),
    "viridis": (
        "#440154", "#482878", "#3e4989", "#31688e", "#26828e",
        "#1f9e89", "#35b779", "#6ece58", "#b5de2b", "#fde725",
    ),
    "magma": (
        "#000004", "#180f3d", "#440f76", "#721f81", "#9e2f7f",
        "#cd4071", "#f1605d", "#fd9668", "#feca8d", "#fcfdbf",
    ),
    "inferno": (
        "#000004", "#1b0c41", "#4a0c6b", "#781c6d", "#a52c60",
        "#cf4446", "#ed6925", "#fb9b06", "#f7d13d", "#fcffa4",
    ),
    "plasma": (
        "#0d0887", "#46039f", "#7201a8", "#9c179e", "#bd3786",
        "#d8576b", "#ed7953", "#fb9f3a", "#fdca26", "#f0f921",
    ),
    "cividis": (
        "#00224e", "#123570", "#3b496c", "#575d6d", "#707173",
        "#8a8678", "#a59c74", "#c3b369", "#e1cc55", "#fee838",
    ),
    "greys": (
        "#ffffff", "#f0f0f0", "#d9d9d9", "#bdbdbd", "#969696",
        "#737373", "#525252", "#252525", "#000000",
    ),
    "coolwarm": (
        "#3b4cc0", "#6788ee", "#9abbff", "#c9d7f0", "#dddddd",
        "#f2cbb7", "#f7ac8e", "#e88568", "#b40426",
    ),
    "RdBu": (
        "#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7", "#f7f7f7",
        "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061",
    ),
}


@dataclass(frozen=True, slots=True)
class Cmap:
    name: str
    stops: tuple[str, ...]
    diverging: bool

    @property
    def midpoint(self) -> str | None:
        """The neutral colour of a diverging map; ``None`` where there is no such thing."""
        return self.stops[len(self.stops) // 2] if self.diverging else None


def _validate() -> Mapping[str, Cmap]:
    out: dict[str, Cmap] = {}
    for name in CMAPS:
        stops = _STOPS.get(name)
        if not stops:
            raise CmapError(f"cmap {name!r} is in the vocabulary with no stops")
        if len(stops) < 2:
            raise CmapError(f"cmap {name!r} needs at least two stops to interpolate between")
        bad = [s for s in stops if not _HEX.match(s)]
        if bad:
            raise CmapError(f"cmap {name!r}: stops must be lowercase #rrggbb, got {bad}")
        if name in DIVERGING and len(stops) % 2 == 0:
            raise CmapError(f"diverging cmap {name!r} has {len(stops)} stops and so no middle one")
        out[name] = Cmap(name, tuple(stops), name in DIVERGING)
    extra = set(_STOPS) - set(CMAPS)
    if extra:
        raise CmapError(f"stops defined for {sorted(extra)}, which are not in the vocabulary")
    unknown = DIVERGING - set(CMAPS)
    if unknown:
        raise CmapError(f"{sorted(unknown)} marked diverging but not in the vocabulary")
    return MappingProxyType(out)


COLORMAPS: Mapping[str, Cmap] = _validate()


def cmap(name: str) -> Cmap:
    """Resolve a cmap name or raise :class:`UnknownCmap` naming the vocabulary."""
    try:
        return COLORMAPS[name]
    except (KeyError, TypeError):
        raise UnknownCmap(
            f"{name!r} is not in the closed cmap vocabulary (galaxy/core/cmaps.py). "
            f"Known: {sorted(COLORMAPS)}"
        ) from None
