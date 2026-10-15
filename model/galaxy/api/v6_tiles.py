"""S64 (V6, RULING_S64 R8; T28): the bright stars by tiles, their expected-count table, and the render's remainder alone.

Three answers the star-first view is built from, each keyed by cell and threshold and never by a window the viewer
chose (D222 ruling 14), so each is the same bytes every time it is asked and can be computed ahead (BUILD_IV W2):

- **The tile form of /api/bright** (``cells=<level-0 ids>&l_min=``): every disc star above ``l_min`` in each named
  level-0 cell (a *tile*: its 64 finest cells), ``l_min`` snapped up to the luminosity function's 0.05 dex grid
  (``bright.LOG_L_GRID``) so a tile at a threshold is one answer. The route's cap applies to the request's expected
  count, never to the disc.
- **The expected-count table** (``table=1``): per level-0 cell, the luminosity function's expected count above each
  grid threshold - what the viewer picks its one threshold per frame from, with a sum and a comparison (D5).
- **The remainder alone** (``/api/render?only=remainder&l_min=``): the two per-ring arrays the field's light under
  ``l_min`` is exactly, placed by two (R, phi) weights the whole render already carries - so a new threshold asks
  9.6 kB, not the render (T28).

Each runs what the request it stands beside runs and no more (rule D4): the tile and the table what ``_bright`` runs
(the galaxy's tables, ``Service._bright_galaxy``), the remainder the stellar part of ``/api/render?l_min=``.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import numpy as np

from galaxy.api import wire
from galaxy.layer import compose as _compose
from galaxy.stages import bright as _bright
from galaxy.stages import spectra as _spectra
from galaxy.stages import systems as _catalogue

if TYPE_CHECKING:  # the service imports this module; it is handed in, never imported here at run time
    from galaxy.api.service import Query, Response, Service

# The level a tile is: a level-0 cell, 32 rings by 32 sectors (systems.CELL_RINGS x CELL_SECTORS).
TILE_LEVEL = 0
# How far below a grid threshold an asked l_min may sit and still be that threshold, dex: a wire guard, not physics
# (rule A8). A client that writes a grid value in decimal, or reads it back from a float32 table, lands within a few
# 1e-8 dex of it; 1e-6 dex is 2.3e-6 of the luminosity, far inside the grid's 0.05 dex step, so no other value snaps
# to a threshold it is not at.
SNAP_TOLERANCE_DEX = 1e-6
# The grid the tile form snaps to, as the headers state it.
GRID = {
    "log_l_first": float(_bright.LOG_L_GRID[0]),
    "log_l_step": float(round(_bright.LOG_L_GRID[1] - _bright.LOG_L_GRID[0], 12)),
    "count": int(_bright.LOG_L_GRID.size),
    "snap": f"up: the smallest grid threshold at or above l_min, within {SNAP_TOLERANCE_DEX:g} dex",
}
# The rule the table's header states and the viewer applies (D5: a sum and a comparison, nothing else).
TABLE_RULE = (
    "pick the smallest grid threshold at which the sum over the tiles in view is at most the point budget; ask each "
    "tile at that threshold (cells=<ids>&l_min=<threshold>) and the field's remainder at the same one "
    "(/api/render?only=remainder&l_min=<threshold>)"
)
# The parameters the tile form refuses: a tile is named by its id, not by a window or a count.
TILE_REFUSES = ("n", "view", "r_min", "r_max", "phi_min", "phi_max")
# What the remainder's two per-ring arrays are called: the remainder's two age parts, as /api/render's l_min= splits it.
REMAINDER_PARTS = {"middle": "stars_unresolved_middle", "old": "stars_unresolved_old"}


def snap_up(l_min: float) -> tuple[int, float]:
    """(k, L): the grid threshold ``LOG_L_GRID[k]`` a tile is asked at for ``l_min`` (L☉), and its luminosity - the
    smallest at or above ``l_min`` (below the grid's faint end, the faint end). Past the grid's last, a 400."""
    from galaxy.api.service import BadRequest

    x = math.log10(float(l_min))
    k = int(np.searchsorted(_bright.LOG_L_GRID, x - SNAP_TOLERANCE_DEX, side="left"))
    if k >= _bright.LOG_L_GRID.size:
        raise BadRequest(
            f"l_min={l_min:g} is above the luminosity function's last threshold, 10^{_bright.LOG_L_GRID[-1]:g} Lsun: "
            "no disc star is that bright"
        )
    return k, float(10.0 ** _bright.LOG_L_GRID[k])


def tiles_of(raw: str) -> list[int]:
    """cells=: level-0 cell ids, comma-separated, each once, in ascending order (the answer's order); a 400 if not."""
    from galaxy.api.service import BadRequest

    try:
        ids = [int(p) for p in raw.split(",") if p.strip() != ""]
    except ValueError:
        raise BadRequest(f"cells={raw!r} is not a comma-separated list of level-0 cell ids") from None
    if not ids:
        raise BadRequest("cells= names no cell: give level-0 cell ids, 0.." + str(_catalogue.CELL_COUNT - 1))
    bad = [c for c in ids if not 0 <= c < _catalogue.CELL_COUNT]
    if bad:
        raise BadRequest(f"cells={bad[:5]} are not level-0 cell ids (0..{_catalogue.CELL_COUNT - 1})")
    if len(set(ids)) != len(ids):
        raise BadRequest("cells= names a cell twice: a tile is asked once, so no star is sent twice")
    return sorted(ids)


def finest_of(tiles: list[int]) -> np.ndarray:
    """The finest (level-MAX_LEVEL) cells of each tile, tile by tile, ascending: ``systems.child_id``'s numbering."""
    n = _catalogue.children_per_cell(_catalogue.MAX_LEVEL)
    return (np.asarray(tiles, dtype=np.int64)[:, None] * n + np.arange(n, dtype=np.int64)[None, :]).ravel()


def layout(R: np.ndarray) -> dict[str, Any]:
    """The level-0 cells as the catalogues cut them (``systems.cell_edges``): what the viewer resolves its footprint to."""
    rings, sectors = _catalogue.cell_edges(R)
    return {
        "level": TILE_LEVEL, "rings": _catalogue.CELL_RINGS, "sectors": _catalogue.CELL_SECTORS,
        "id": "ring * sectors + sector",
        "ring_edges": [float(v) for v in rings], "sector_edges": [float(v) for v in sectors],
        "about": "a level-0 cell is the annulus sector between two ring edges (kpc) and two sector edges (radians, "
                 "phi from 0 to 2 pi); systems.cell_edges, the one definition every census is cut by",
    }


def bright(service: Service, q: Query) -> Response:
    """/api/bright's tile form (``cells=``) or its expected-count table (``table=1``): the galaxy as ``_bright``
    makes it - the same model, inputs, layer and cache key, so the tiles and the window form share the cell cache."""
    from galaxy.api.service import BRIGHT_SLOT, BadRequest, _inputs_json, _object_filters, _stage_for

    is_table = q.one("table") is not None
    precision = q.one("precision", "f8")
    if precision not in ("f8", "f4"):
        raise BadRequest(f"precision={precision!r} is not f8 or f4")
    if is_table:
        if q.one("table") != "1":
            raise BadRequest(f"table={q.one('table')!r}: give table=1 for the expected-count table")
        for name in ("cells", *TILE_REFUSES, "l_min", "filters", "white"):
            if q.one(name) is not None:
                raise BadRequest(f"table=1 takes no {name}=: it is every level-0 cell's expected count at every grid threshold")
    else:
        for name in TILE_REFUSES:
            if q.one(name) is not None:
                raise BadRequest(
                    f"cells= takes no {name}=: a tile is a level-0 cell named by its id at a grid threshold (l_min=); "
                    "the window form is r_min..phi_max with n= or l_min="
                )
        if q.one("l_min") is None:
            raise BadRequest("cells= needs l_min= (Lsun): a tile is answered at one threshold of the 0.05 dex grid")
        tiles = tiles_of(q.one("cells") or "")
        l_min = q.number("l_min", 0.0)
        if not l_min > 0.0:
            raise BadRequest(f"l_min={l_min!r} is not a positive luminosity")
        k, used = snap_up(l_min)
        curves, white = _object_filters(q)

    model = service._model(q)
    stage = _stage_for(model, BRIGHT_SLOT, service.impls)
    inputs = service._overrides(model, q)
    layer = service._layer(q)
    out, ran = service.compute(model, inputs, service._reads(model, stage), layer)
    seed = int(out.inputs[stage.reads_seeds[0]])
    # The key _bright makes, the same words: one galaxy and one cell cache for the tiles and the window form (tested).
    key = repr(("bright", model.name, service.grid.spec, sorted(_inputs_json(out.inputs).items()), seed, _compose.setting(out.fields)))
    galaxy, scalars = service._bright_galaxy(key, out, model)
    base = {"model": model.name, "inputs": _inputs_json(out.inputs), "layer": _compose.setting(out.fields), "seed": seed}
    if is_table:
        return _table(service, galaxy, base, precision, ran)

    finest = finest_of(tiles)
    expected = float(galaxy.at_threshold(finest, k).sum())
    if expected > _service_cap():
        raise BadRequest(
            f"cells= at l_min={used:g} holds {expected:.0f} expected stars, more than {_service_cap()}: raise l_min "
            "or ask fewer cells at once (the table, table=1, gives each cell's count at every threshold)"
        )
    rows = service.bright.fetch(key, galaxy, seed, finest, used)
    columns = [d.name for d in stage.publishes if d.kind.domain == "object"] + ["cell", "rank"]
    lum = np.asarray(rows["bright_star_luminosity"], dtype=float)
    header = {
        **base,
        # No echo of the l_min asked: the bytes depend on (tile, grid threshold) alone, however l_min was written.
        "tile": {"cells": tiles, "level": TILE_LEVEL, "l_min_used": used, "grid": GRID},
        "cells": {"count": int(finest.size), "level": _catalogue.MAX_LEVEL,
                  "of": _catalogue.CELL_COUNT * _catalogue.children_per_cell(_catalogue.MAX_LEVEL)},
        "threshold": {"l_min": used, "complete": True, "prefix": _bright.PREFIX,
                      "why": "every disc star above l_min in the tiles is in the body, grouped by finest cell "
                             "(ascending) and brightest first within each"},
        # The luminosity function's count and light above the grid threshold over the tiles' finest cells - exactly
        # the table's columns for these cells (bright.BrightGalaxy.curves at the threshold).
        "count": {"returned": int(lum.size), "expected": expected},
        "light": {"returned": float(lum.sum()), "expected": float(galaxy.curves(finest, "light")[:, k].sum())},
        "columns": columns,
        "scalars": scalars,
        # No ``stages``: what a request ran depends on what the service already held, and a tile at a threshold is
        # the same bytes every time (the response's own ``stages`` still carries it, rule D4's instrument).
    }
    arrays = [(c, np.asarray(rows[c])) for c in columns]
    if curves is not None:
        from galaxy.api.service import _object_response_header

        anchors = _spectra.object_nu_l_nu(_bright.magnitudes(rows))
        arrays.append(("response", _spectra.object_response(anchors, np.asarray(rows["bright_star_temperature"], dtype=float), curves)))
        header.update(_object_response_header(curves, white, "bright_star_temperature"))
    return _respond(header, arrays, precision, ran)


def _service_cap() -> int:
    from galaxy.api.service import MAX_BRIGHTEST

    return MAX_BRIGHTEST


def _respond(header: dict[str, Any], arrays: list[tuple[str, np.ndarray]], precision: str, ran: tuple[str, ...]) -> Response:
    from galaxy.api.service import Response

    if precision == "f4":
        arrays = [(c, a.astype(np.float32) if a.dtype == np.float64 else a) for c, a in arrays]
    return Response(200, wire.MEDIA, wire.encode(header, arrays), ran)


def table_of(galaxy: Any) -> np.ndarray:
    """(CELL_COUNT, K): each level-0 cell's expected count above each grid threshold - its 64 finest cells' sum of
    ``BrightGalaxy.curves`` (each finest cell's area x its two parts' stars per pc² above the threshold x their
    azimuthal weights), summed over a cell's eight finest sectors first."""
    n = 1 << _catalogue.MAX_LEVEL
    sector_weights = galaxy.weights.reshape(2, galaxy.weights.shape[1], _catalogue.CELL_SECTORS, n).sum(axis=3)  # (2, 256, 32)
    per_sub = np.einsum("s,psj,psk->sjk", galaxy.area, sector_weights, galaxy.count_cell)  # (256 sub-rings, 32, K)
    return per_sub.reshape(_catalogue.CELL_RINGS, n, _catalogue.CELL_SECTORS, -1).sum(axis=1).reshape(_catalogue.CELL_COUNT, -1)


def _table(service: Service, galaxy: Any, base: dict[str, Any], precision: str, ran: tuple[str, ...]) -> Response:
    grid = _bright.LOG_L_GRID
    header = {
        **base,
        "table": {
            "rule": TABLE_RULE,
            "axes": {"expected": ["cell", "threshold"], "threshold": ["threshold"], "log_l": ["threshold"]},
            "about": "expected[cell, k]: the luminosity function's expected number of disc stars older than the cluster "
                     "window above threshold[k] (Lsun) in level-0 cell `cell` - the sum over its 64 finest cells of what "
                     "/api/bright's tile form and its header's count.expected read at that grid threshold "
                     "(bright.BrightGalaxy.curves). Non-increasing along k. The tile's realised count is Poisson about "
                     "it. threshold and log_l are float64 at any precision, so a threshold read back is the grid's value",
            "grid": GRID,
        },
        "cells": layout(service.grid.R),
    }
    arrays = [("log_l", np.asarray(grid, dtype=np.float64)), ("threshold", 10.0 ** np.asarray(grid, dtype=np.float64))]
    expected = table_of(galaxy)
    if precision == "f4":
        expected = expected.astype(np.float32)
    return _respond(header, [*arrays, ("expected", expected)], "f8", ran)


def remainder(service: Service, q: Query) -> Response:
    """/api/render?only=remainder&l_min=: the field's light under ``l_min`` as two per-ring arrays, the remainder's two
    age parts through the curves (``Service._unresolved``'s parts, one ``bright.resolve``), which the whole render's
    own placing weights turn into ``stars_unresolved`` exactly:

        stars_unresolved(R, phi, f) = stars_unresolved_middle(R, f) * <middle's weight>(R, phi)
                                      + stars_unresolved_old(R, f) * stars_placement(R, phi)

    the middle's weight being ``stars_middle_placement`` where the model publishes sfr_modulation and
    ``stars_placement`` where it does not (bright.part_weights; the whole render's ``ages`` names both). Runs the
    stellar part of an ``l_min=`` render and no more (rule D4): the stars' fields, the history, the contrast."""
    from galaxy.api.service import (
        EVEN_ROUND_THE_RING, RENDER_MIDDLE_PLACEMENT, RENDER_STARS, RENDER_STARS_PLACEMENT, BadRequest, NotFound,
        _inputs_json, _parse_filters, _white_point,
    )

    if q.one("only") != "remainder":
        raise BadRequest(f"only={q.one('only')!r}: the one part /api/render answers alone is only=remainder")
    for name in ("level", "r_min", "r_max", "phi_min", "phi_max"):
        if q.one(name) is not None:
            raise BadRequest(f"only=remainder takes no {name}=: its arrays are per ring over the whole grid")
    if q.one("l_min") is None:
        raise BadRequest("only=remainder needs l_min= (Lsun): the remainder is the light under a threshold")
    l_min = q.number("l_min", 0.0)
    if not l_min > 0.0:
        raise BadRequest(f"l_min={l_min!r} is not a positive luminosity")
    model = service._model(q)
    curves = _parse_filters(q)
    precision = q.one("precision", "f8")
    if precision not in ("f8", "f4"):
        raise BadRequest(f"precision={precision!r} is not f8 or f4")
    white = _white_point(q, curves)
    declared = service._declared(model)
    missing = [n for n in (*RENDER_STARS, "stars_formed_history", "feh_history") if n not in declared]
    if missing:
        raise NotFound(f"model {model.name!r} does not publish {missing}, which the remainder is decomposed from")
    wanted = [*RENDER_STARS, *(n for n in ("pattern_density_contrast", *_bright.RESOLVE_READS) if n in declared)]
    inputs = service._overrides(model, q)
    out, ran = service.compute(model, inputs, wanted, service._layer(q))
    f = out.fields
    R = out.grid.R
    sed = np.stack([np.asarray(f[f"disc_sed_{b.lower()}"], dtype=float) for b in _spectra.SED_BANDS], axis=-1)
    per_ring = _spectra.stellar_response(sed, f["disc_light_temperature"], curves)
    contrast = _compose.published(f, "pattern_density_contrast")
    # The full render's own entry and closure (the same method, so the same words and the same numbers), and its two
    # parts as it forms them: one decomposition, each part through the curves at the ring's colour temperature.
    parts: dict[str, np.ndarray] = {}
    _, entry, resolved = service._unresolved(model, f, R, curves, per_ring, contrast, l_min, parts)
    middle_by = RENDER_MIDDLE_PLACEMENT if _compose.published(f, "sfr_modulation") is not None else RENDER_STARS_PLACEMENT
    weight = {"middle": middle_by, "old": RENDER_STARS_PLACEMENT}
    R_axis = out.grid.axes["R"]
    header = {
        "model": model.name,
        "inputs": _inputs_json(out.inputs),
        "layer": _compose.setting(out.fields),
        "set": q.one("set"),
        "filters": [c.json() for c in curves],
        "only": "remainder",
        "window": {"R": {"first": 0, "n": int(R.size), "lo": R_axis.lo, "width": R_axis.width}},
        "axes": {name: ["R", "filter"] for name in REMAINDER_PARTS.values()},
        "remainder": {
            "component": "stars_unresolved",
            "rule": "stars_unresolved(R, phi, filter) = " + " + ".join(
                f"{REMAINDER_PARTS[p]}(R, filter) * {weight[p]}(R, phi)" for p in REMAINDER_PARTS),
            "parts": {p: {"array": REMAINDER_PARTS[p], "weight": weight[p]} for p in REMAINDER_PARTS},
            "weights": "the whole render's (R, phi) arrays of these names - /api/render with the same query and no "
                       "only= carries them, its header's ages naming each (S63, D223) - so a new l_min asks these two "
                       "arrays and not the render (T28). Exact: the full l_min= render's stars_unresolved is this sum "
                       "to rounding (tests/test_v6_bright.py: 1e-12)",
            "about": entry["about"] + _compose.words(f, "", EVEN_ROUND_THE_RING),
        },
        "white": white,
        "resolved": resolved,
        "stages": list(ran),
    }
    arrays = [(REMAINDER_PARTS[p], parts[p]) for p in REMAINDER_PARTS]
    return _respond(header, arrays, precision, ran)
