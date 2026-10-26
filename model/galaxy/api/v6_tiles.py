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

**S65 (V6b, RULING_S65 R1-R4): the zoomed-in point layer.** ``level=k`` (0-3) names the tiles at level k: a level-k
tile's rows are its finest cells' rows - the level-0 tile's rows restricted to them, row for row, the catalogue being
one at every level (D200, R2) - and ``table=1&cells=<ids>&level=k`` is the expected-count table for the cells asked
(each the sum of its finest cells' columns, the level-0 table's quadrature; never the whole level-3 table). A tile whose
level-0 ring holds more stars above the threshold than the ring-first draw may hold (``ring_cap``, #159) is refused
before any draw. Without ``level=`` every answer is S64's, byte for byte.

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

# The level a tile is unless level= names another (S65, V6b): a level-0 cell, 32 rings by 32 sectors
# (systems.CELL_RINGS x CELL_SECTORS).
TILE_LEVEL = 0
# ring_cap(): the most expected stars above a tile's threshold in one level-0 ring that a tile request draws (S65, V6b,
# RULING_S65 R4; debt #159). The ring-first draw (bright.draw_ring, D220) holds every star of a ring above the threshold at once -
# its Gamma, its eight uniform streams, its interval, part, sub-ring, rest, sector and cell, and the (N, 16) split CDF
# it reads - measured at 309-310 bytes a star (tracemalloc peak, one ring at R = 8 kpc, 1.9e5 / 9.6e5 / 2.9e6 stars,
# both templates; 0.21 us a star), so this is 1.5 GB and about a second. It is the service's guard on the stars one
# request materialises (service.MAX_STARS, /api/region's stars=), not a new number: MAX_BRIGHT_POOL (5e5) would
# refuse the default point budget's own thresholds at 0.25 kpc (224 Lsun: the ring at R = 8 kpc holds 9.6e5) and
# at 62 pc (71 Lsun: 2.9e6).
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
# The same rule for the cells asked at a level (S65, V6b, R1): the table served for the cells in view, never whole.
CELLS_TABLE_RULE = (
    "pick the smallest grid threshold at which the sum over the level-k cells in view, each cell's count weighted by "
    "the share of the stars' layer (/api/render's header layers.stars, sech2(z / 2h) / 4h) inside the frustum's height "
    "range, averaged over 3 x 3 points across the cell, is at most the point budget; ask at that threshold each cell "
    "expecting at least one star in view, its weighted count at least 1 (cells=<ids>&level=<k>&l_min=<threshold>), the "
    "skipped cells' weighted counts summed and stated as the rule's loss, and the field's remainder at the same "
    "threshold (/api/render?only=remainder&l_min=<threshold>)"
)
# How a level-k cell is cut from the level-0 layout (systems.cell_bounds, the one definition; D190's naming): what the
# viewer resolves its footprint to at level k, from the level-0 edges and this rule alone.
CHILDREN = (
    "a level-k cell's id is c 4^k + a 2^k + b: the a-th of 2^k equal sub-rings (in R) by the b-th of 2^k equal "
    "sub-sectors (in phi) of level-0 cell c, row-major (systems.cell_bounds); level 3 is the finest"
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


def tiles_of(raw: str, level: int = TILE_LEVEL) -> list[int]:
    """cells=: level-``level`` cell ids, comma-separated, each once, in ascending order (the answer's order); a 400
    if not."""
    from galaxy.api.service import BadRequest

    count = _catalogue.CELL_COUNT * _catalogue.children_per_cell(level)
    try:
        ids = [int(p) for p in raw.split(",") if p.strip() != ""]
    except ValueError:
        raise BadRequest(f"cells={raw!r} is not a comma-separated list of level-{level} cell ids") from None
    if not ids:
        raise BadRequest(f"cells= names no cell: give level-{level} cell ids, 0.." + str(count - 1))
    bad = [c for c in ids if not 0 <= c < count]
    if bad:
        raise BadRequest(f"cells={bad[:5]} are not level-{level} cell ids (0..{count - 1})")
    if len(set(ids)) != len(ids):
        raise BadRequest("cells= names a cell twice: a tile is asked once, so no star is sent twice")
    return sorted(ids)


def finest_of(tiles: list[int], level: int = TILE_LEVEL) -> np.ndarray:
    """The finest (level-MAX_LEVEL) cells of each level-``level`` tile, tile by tile, each tile's ascending:
    ``systems.child_id``'s numbering, a level-k cell being the a-th of 2^k sub-rings by the b-th of 2^k sub-sectors of
    its level-0 cell (q = a 2^k + b, ``systems.cell_bounds``), so its finest cells are the 2^(3-k) x 2^(3-k) block of
    finest sub-rings a 2^(3-k) .. and sub-sectors b 2^(3-k) .. of that level-0 cell. At level 0, the tile's 64."""
    k, top = int(level), _catalogue.MAX_LEVEL
    parent, q = np.divmod(np.asarray(tiles, dtype=np.int64), _catalogue.children_per_cell(k))
    a, b = np.divmod(q, 1 << k)
    per = 1 << (top - k)
    i = np.arange(per, dtype=np.int64)
    sub_ring = a[:, None, None] * per + i[None, :, None]
    sub_sector = b[:, None, None] * per + i[None, None, :]
    return (parent[:, None, None] * _catalogue.children_per_cell(top) + sub_ring * (1 << top) + sub_sector).ravel()


def tile_of(finest: np.ndarray, level: int) -> np.ndarray:
    """The level-``level`` cell each finest (level-MAX_LEVEL) cell stands in: :func:`finest_of`'s inverse."""
    k, top = int(level), _catalogue.MAX_LEVEL
    parent, q = np.divmod(np.asarray(finest, dtype=np.int64), _catalogue.children_per_cell(top))
    a, b = np.divmod(q, 1 << top)
    shift = top - k
    return parent * _catalogue.children_per_cell(k) + (a >> shift) * (1 << k) + (b >> shift)


def level_of(q: Query) -> int:
    """level=: the hierarchy level the tiles are named at, 0 (the default, S64's form) to systems.MAX_LEVEL."""
    from galaxy.api.service import _level

    return _level(q)


def ring_guard(galaxy: Any, finest: np.ndarray, used: float) -> None:
    """A 400 before any draw when a ring the tiles stand in holds more expected stars above the threshold than the
    ring-first draw may hold at once (:func:`ring_cap`; debt #159)."""
    from galaxy.api.service import BadRequest

    cap = ring_cap()
    k = _bright.interval_of(used)
    rings = np.unique(galaxy.ring_of(finest))
    counts = galaxy.ring_curve[rings, k]
    worst = int(np.argmax(counts))
    if float(counts[worst]) > cap:
        raise BadRequest(
            f"the cells asked at l_min={used:g} stand in level-0 ring {int(rings[worst])}, which holds {float(counts[worst]):.0f} "
            f"expected stars above it; the ring-first draw (D220) holds a ring's stars whole, about 310 bytes each, and "
            f"refuses a ring past {cap} (debt #159: a cell-local draw below a ring-level prefix is the mend). "
            "Raise l_min (the table, table=1, gives each cell's count at every threshold)"
        )


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
    level = level_of(q)
    if is_table:
        if q.one("table") != "1":
            raise BadRequest(f"table={q.one('table')!r}: give table=1 for the expected-count table")
        for name in (*TILE_REFUSES, "l_min", "filters", "white"):
            if q.one(name) is not None:
                raise BadRequest(f"table=1 takes no {name}=: it is the expected count at every grid threshold, of every "
                                 "level-0 cell or of the cells= named")
        # S65 (V6b, R1): the cells asked, at their level; without cells= the whole level-0 table as S64 served it.
        asked = None if q.one("cells") is None else tiles_of(q.one("cells") or "", level)
        if asked is None and level != TILE_LEVEL:
            raise BadRequest(f"table=1&level={level} needs cells=: the whole table is level 0's; name the level-{level} "
                             "cells in view")
    else:
        for name in TILE_REFUSES:
            if q.one(name) is not None:
                raise BadRequest(
                    f"cells= takes no {name}=: a tile is a level-0 cell named by its id at a grid threshold (l_min=); "
                    "the window form is r_min..phi_max with n= or l_min="
                )
        if q.one("l_min") is None:
            raise BadRequest("cells= needs l_min= (Lsun): a tile is answered at one threshold of the 0.05 dex grid")
        tiles = tiles_of(q.one("cells") or "", level)
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
        if asked is not None:
            return _cells_table(service, galaxy, base, precision, ran, asked, level)
        return _table(service, galaxy, base, precision, ran)

    finest = finest_of(tiles, level)
    expected = float(galaxy.at_threshold(finest, k).sum())
    if expected > _service_cap():
        raise BadRequest(
            f"cells= at l_min={used:g} holds {expected:.0f} expected stars, more than {_service_cap()}: raise l_min "
            "or ask fewer cells at once (the table, table=1, gives each cell's count at every threshold)"
        )
    ring_guard(galaxy, finest, used)
    rows = service.bright.fetch(key, galaxy, seed, finest, used)
    columns = [d.name for d in stage.publishes if d.kind.domain == "object"] + ["cell", "rank"]
    lum = np.asarray(rows["bright_star_luminosity"], dtype=float)
    header = {
        **base,
        # No echo of the l_min asked: the bytes depend on (tile, grid threshold) alone, however l_min was written.
        "tile": {"cells": tiles, "level": level, "l_min_used": used, "grid": GRID},
        "cells": {"count": int(finest.size), "level": _catalogue.MAX_LEVEL,
                  "of": _catalogue.CELL_COUNT * _catalogue.children_per_cell(_catalogue.MAX_LEVEL)},
        "threshold": {"l_min": used, "complete": True, "prefix": _bright.PREFIX,
                      "why": "every disc star above l_min in the tiles is in the body, grouped by finest cell "
                             "(ascending) and brightest first within each" if level == TILE_LEVEL else
                             f"every disc star above l_min in the level-{level} tiles is in the body, grouped by tile "
                             "(ascending), by finest cell (ascending) within each tile and brightest first within each "
                             "cell: each tile's rows are its finest cells' rows in the level-0 tile it stands in"},
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


def ring_cap() -> int:
    """The ring-first draw's bound, the service's MAX_STARS (the comment at TILE_LEVEL says why that number)."""
    from galaxy.api.service import MAX_STARS

    return MAX_STARS


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


def cells_table_of(galaxy: Any, cells: list[int], level: int) -> np.ndarray:
    """(len(cells), K): each level-``level`` cell's expected count above each grid threshold - the sum over its finest
    cells of ``BrightGalaxy.curves``, the same quadrature the level-0 table sums (no other)."""
    per = _catalogue.children_per_cell(_catalogue.MAX_LEVEL - int(level))
    return galaxy.curves(finest_of(cells, level)).reshape(len(cells), per, -1).sum(axis=1)


def _cells_table(service: Service, galaxy: Any, base: dict[str, Any], precision: str, ran: tuple[str, ...],
                 cells: list[int], level: int) -> Response:
    grid = _bright.LOG_L_GRID
    header = {
        **base,
        "table": {
            "rule": CELLS_TABLE_RULE,
            "axes": {"expected": ["cell", "threshold"], "threshold": ["threshold"], "log_l": ["threshold"]},
            "level": level,
            "cells": cells,
            "about": f"expected[i, k]: the luminosity function's expected number of disc stars older than the cluster "
                     f"window above threshold[k] (Lsun) in the level-{level} cell cells[i] (ascending) - the sum over its "
                     f"{_catalogue.children_per_cell(_catalogue.MAX_LEVEL - level)} finest cells of what the tile form's "
                     "count.expected reads (bright.BrightGalaxy.curves), so a level-k cell's row is its children's rows "
                     "summed and the level-0 table's row is its level-k cells' summed. Non-increasing along k",
            "grid": GRID,
        },
        "cells": {**layout(service.grid.R), "children": CHILDREN},
    }
    arrays = [("log_l", np.asarray(grid, dtype=np.float64)), ("threshold", 10.0 ** np.asarray(grid, dtype=np.float64))]
    expected = cells_table_of(galaxy, cells, level)
    if precision == "f4":
        expected = expected.astype(np.float32)
    return _respond(header, [*arrays, ("expected", expected)], "f8", ran)


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
        "stages": list(out.needs),
    }
    arrays = [(REMAINDER_PARTS[p], parts[p]) for p in REMAINDER_PARTS]
    return _respond(header, arrays, precision, ran)
