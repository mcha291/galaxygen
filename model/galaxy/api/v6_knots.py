"""The HII regions as knots at whole-galaxy scale (S64, BUILD_III Phase V6; RULING_S64 R5-R6): API-side arithmetic on
the cluster census's published columns, no stage and no constant on the wire (rule D4; the pattern of ``/api/clusters``'
``response``).

Two answers, both on ``/api/clusters`` (one hook in ``_clusters``):

- **Each region's lines through the viewer's curves** (``line_response``, :func:`line_response`): per cluster, its HII
  region's Halpha (``hii_halpha_luminosity``) through each curve at the line's wavelength, plus every other line the
  field's HII layers carry (``/api/render``'s ``lines_hii``: Hbeta and the four forbidden lines), each at its own
  wavelength by the same ``spectra.line_response`` (air to vacuum as the curve asks): Hbeta as Halpha over the region's
  own Balmer decrement (``hii_balmer_decrement``, Case B at its electron temperature), each forbidden line as Halpha
  times its ``hii_*_ratio``. The knots carry the lines the field carries, no more, no fewer (:func:`knot_lines`).
- **The header ``knots``** (:func:`header`; D223's ``ages`` pattern): the light column, the size column (the
  Stromgren radius, R6), the naming cell, the level-0 cells' layout, and the rule by which a viewer that draws some
  knots scales the field's HII layers in each cell by the share of the cell's census it does not draw, so the screen
  carries the census where every knot is drawn and the field where none is, never both whole (R5).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.api import v6_tiles as _v6_tiles
from galaxy.stages import spectra as _spectra

COLUMN = "line_response"
LIGHT = "hii_halpha_luminosity"
SIZE = "hii_stromgren_radius"
CELL = "cell"
DECREMENT = "hii_balmer_decrement"
# The field's lines, as /api/render's HII layers carry them: halpha_hii, then lines_hii's (service.RENDER_LINES_HII).
FIELD_LINES = ("halpha", "hbeta", "oiii_5007", "nii_6583", "sii_6716", "sii_6731")

# The rule, in the words the clusters header and the render's two HII abouts share (RULING_S64 R5).
RULE = (
    "in a level-0 cell c, the field's HII layers (/api/render's halpha_hii and lines_hii) are scaled by 1 - D_c / K_c, "
    "D_c the Halpha of the knots a viewer draws in c, K_c the Halpha of every knot named by c (the clusters' cell "
    "column, /api/clusters' knots); 1 where K_c is 0; the screen then carries the census where every knot is drawn "
    "and the field where none is"
)
# The sentence each of /api/render's two HII abouts gains (S64): appended where the text ends, before the layer-off words.
HALPHA_WORDS = (
    ". A viewer that draws the regions as knots (/api/clusters' line_response) scales this layer by each cell's undrawn "
    "share: " + RULE + "."
)
LINES_WORDS = (
    ". Scaled with halpha_hii by the knots' undrawn share where a viewer draws them (/api/clusters' line_response "
    "carries the same lines): " + RULE + "."
)
CLOSURE = (
    "over any set of whole level-0 cells, the drawn knots' Halpha plus the scaled field's is the census's (sum of K_c) "
    "when every knot is drawn and the field's when none is, exactly; between, the field's undrawn share. The share is "
    "in [0, 1]: never negative, nothing clipped. The census against the field per cell (K_c / F_c) is the catalogue's "
    "check on the field (RENDER_PHYSICS section 7), not a target: its own heavy-tailed Poisson noise"
)
LINE_ABOUT = (
    "each cluster's HII region's light through each curve, Lsun: its Halpha (hii_halpha_luminosity) through the curve "
    "at the line's wavelength, plus each other line the field's HII layers carry, each at its own wavelength - Hbeta as "
    "the Halpha over the region's Balmer decrement, each forbidden line as the Halpha times its hii_*_ratio - by "
    "spectra.line_response, as /api/render's lines_hii is per ring (S64, V6). Beside response, the cluster's "
    "starlight. A viewer draws a region's light through line_response or the field's halpha_hii and lines_hii in "
    "that cell's undrawn share (the knots header's rule), never both whole. 0 where the region has no Halpha; NaN "
    "where it has light and a line's ratio is missing (B9)"
)


def field_lines(declared: Iterable[str]) -> list[str]:
    """The lines the field's HII layers carry for a model that declares ``declared``: Halpha with
    ``halpha_surface_brightness_hii``, then each of ``lines_hii``'s that the model publishes, in /api/render's order."""
    names = set(declared)
    if "halpha_surface_brightness_hii" not in names:
        return []
    return [n for n in FIELD_LINES if f"{n}_surface_brightness_hii" in names]


def _source(line: str) -> str:
    """The census column a knot's line is read from, beside its Halpha."""
    if line == "halpha":
        return LIGHT
    if line == "hbeta":
        return DECREMENT
    return f"hii_{line}_ratio"


def matched(lines: Sequence[str], columns: Iterable[str]) -> tuple[list[str], list[str]]:
    """The field's lines a knot can carry from ``columns`` (each needs Halpha and its own column), and those it cannot."""
    have = set(columns)
    ok = [n for n in lines if LIGHT in have and _source(n) in have]
    return ok, [n for n in lines if n not in ok]


def knot_lines(census: Mapping[str, Any], lines: Sequence[str]) -> dict[str, np.ndarray]:
    """Each knot's light in each of ``lines``, Lsun: Halpha as published; Hbeta the Halpha over the region's Balmer
    decrement; a forbidden line the Halpha times its ratio. 0 where the Halpha is 0 (no region light, whatever the
    ratio), NaN where there is light and the line's column is not a finite positive number (B9)."""
    halpha = np.asarray(census[LIGHT], dtype=float)
    lit = halpha > 0.0
    out: dict[str, np.ndarray] = {}
    for n in lines:
        if n == "halpha":
            value = halpha.copy()
        else:
            x = np.asarray(census[_source(n)], dtype=float)
            with np.errstate(divide="ignore", invalid="ignore"):
                value = halpha / x if n == "hbeta" else halpha * x
            bad = ~np.isfinite(value) | ((x <= 0.0) if n == "hbeta" else (x < 0.0))
            value = np.where(bad, np.nan, value)
        out[n] = np.where(lit, value, np.where(np.isnan(halpha), np.nan, 0.0))
    return out


def line_response(census: Mapping[str, Any], lines: Sequence[str], curves: Sequence[Any]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """``(N, filters)``, Lsun: each knot's lines through each curve, summed (the knot is one point), and each line's
    transmission per curve (the header's). The curves' shares are ``spectra.line_response``, the render's own."""
    shares = {n: _spectra.line_response(curves, _spectra.LINE_WAVELENGTHS[n]) for n in lines}
    per_line = knot_lines(census, lines)
    size = int(np.asarray(census[LIGHT]).size)
    total = np.zeros((size, len(curves)))
    for n in lines:
        total = total + per_line[n][:, None] * shares[n][None, :]
    return total, shares


def header(R: np.ndarray, lines: Sequence[str], unmatched: Sequence[str], shares: Mapping[str, np.ndarray] | None) -> dict[str, Any]:
    """The clusters answer's ``knots`` entry: what a knot is drawn from, the cells that name it, and the rule."""
    return {
        "light": LIGHT,
        "size": SIZE,
        "cell": CELL,
        "column": COLUMN,
        "lines": {
            n: {"wavelength": _spectra.LINE_WAVELENGTHS[n], "from": _source(n),
                **({"transmission": shares[n].tolist()} if shares is not None else {})}
            for n in lines
        },
        "unmatched": list(unmatched),
        "layout": _v6_tiles.layout(R),
        "rule": RULE,
        "closure": CLOSURE,
        "about": (
            "the HII regions as knots (S64, V6): each cluster's region a point of its own lines (line_response, with "
            "filters=), its light hii_halpha_luminosity; a point until its diameter, 2 x hii_stromgren_radius, fills a "
            "pixel, then a disc of that radius - the Stromgren sphere holds the line light (hii_halpha_emissivity is "
            "uniform over it); the wind bubble (bubble_radius) is the shell's own object, drawn by the region regime, "
            "not the knot. Named by its cell column: the level-0 cell whose census drew it, which K_c sums, even where "
            "its source offset places it in a neighbour (2.7 % of the Milky Way's knots). The cells are the layout's, "
            "systems.cell_edges; K_c is the sum of the cell's rows, so no per-cell sum rides the wire"
        ),
    }
