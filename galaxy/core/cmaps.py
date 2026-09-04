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
)

DIVERGING: frozenset[str] = frozenset({"coolwarm", "RdBu"})

_STOPS: dict[str, tuple[str, ...]] = {
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
