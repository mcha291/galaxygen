"""S65 (BUILD_III Phase V6b; RULING_S65 R1-R4): the zoomed-in point layer - the bright catalogue at level-k tiles.

R1: ``/api/bright?cells=<level-k ids>&level=k&l_min=`` - each level-k cell's stars above l_min snapped up to the 0.05 dex
grid, the same bytes every time; ``table=1&cells=<ids>&level=k`` - the expected count of the cells asked at every grid
threshold; without ``level=`` both are S64's, byte for byte. R2: a level-k tile's rows are its finest cells' rows - the
level-0 tile's rows restricted to them, row for row - at every level, on both templates, layer on and off; the union over
a level-k footprint is the window answer. R3: at the tiles' threshold S48's identity holds as it is. R4: a tile whose
level-0 ring holds more stars above the threshold than the ring-first draw may hold is refused before any draw (#159).
Every check recomputes with this file's own arithmetic.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import v6_tiles as v6
from galaxy.api import wire
from galaxy.api.service import MAX_STARS, Service
from galaxy.stages import bright as br
from galaxy.stages import systems as sy

ROOT = Path(__file__).resolve().parents[1]
GAL = ROOT / "frontend" / "src" / "galaxy"
SETS = {**json.loads((GAL / "filters.json").read_text(encoding="utf-8"))["sets"],
        **json.loads((GAL / "instruments.json").read_text(encoding="utf-8"))["sets"]}
TEMPLATES = ("milky_way", "ngc_4414")
LEVELS = (1, 2, 3)
K_1E3, K_3E3 = 80, 90  # LOG_L_GRID's 10^3 and 10^3.5 Lsun
# The thresholds a level-k tile is asked at twice: 10^2.5, 10^2.2, 10^1.9 Lsun, near the default budget's own picks (R1)
SAME_BYTES_K = {1: 70, 2: 64, 3: 58}
TILE = 261  # a level-0 cell: ring 8 (R = 7.52-8.45 kpc on the Milky Way), sector 5 (phi 0.98-1.18)
# Ten (level-2 cell, threshold) pairs for the table against the realised counts (milky_way). Measured at S65: the
# realised counts' z = (n - expected) / sqrt(expected) lay in -1.50..+0.93 over the ten (expected 82-761); the bound is
# the S64 test's.
POISSON_PAIRS = ((4176, K_1E3), (4181, K_1E3), (4190, K_1E3), (4191, K_1E3), (1600, K_1E3),
                 (4176, K_3E3 - 4), (4183, K_3E3 - 4), (8000, K_3E3 - 4), (4100, K_3E3 - 4), (2900, K_3E3 - 4))


def curves(name: str) -> str:
    return json.dumps(SETS[name]["curves"])


@pytest.fixture(scope="module")
def service():
    return Service(cache=4)


def ask(service: Service, path: str, **q):
    r = service.handle(path, {k: [str(v)] for k, v in q.items()})
    assert r.status == 200, r.body[:400]
    return (*wire.decode(r.body), r)


def refused(service: Service, path: str, **q) -> str:
    r = service.handle(path, {k: [str(v)] for k, v in q.items()})
    assert r.status == 400, (q, r.status, r.body[:300])
    return r.json()["error"]


def by_cell_rank(arrays: dict) -> dict:
    order = np.lexsort((np.asarray(arrays["rank"]), np.asarray(arrays["cell"])))
    return {k: np.asarray(v)[order] for k, v in arrays.items()}


def grid_l(k: int) -> float:
    return float(10.0 ** br.LOG_L_GRID[k])


def children(tile: int, level: int) -> list[int]:
    return [sy.child_id(tile, level, q) for q in range(sy.children_per_cell(level))]


def level_id(sub_ring: int, sub_sector: int, level: int) -> int:
    """The level-k id of the cell at global sub-ring / sub-sector (each 32 x 2^k round the disc): D190's naming."""
    n = 1 << level
    return ((sub_ring // n) * sy.CELL_SECTORS + sub_sector // n) * n * n + (sub_ring % n) * n + sub_sector % n


def galaxy_of(service: Service):
    return service._bright_galaxies[next(reversed(service._bright_galaxies))][0]


# --- the naming: a level-k tile's finest cells, by systems.cell_bounds' own geometry ---------------------------------

@pytest.mark.parametrize("level", (0, *LEVELS))
def test_a_level_k_tile_s_finest_cells_are_the_finest_cells_inside_it(level):
    R = np.linspace(0.0, 30.0, 400)
    for tile in (0, TILE, sy.CELL_COUNT * sy.children_per_cell(level) - 1, 37 * sy.children_per_cell(level) + 3 % sy.children_per_cell(level)):
        fine = v6.finest_of([tile], level)
        assert fine.size == sy.children_per_cell(sy.MAX_LEVEL - level) and np.all(np.diff(fine) > 0)
        outer = sy.cell_bounds(R, tile, level)
        for c in fine:  # each lies inside the tile, and the tile's area is theirs summed
            b = sy.cell_bounds(R, int(c), sy.MAX_LEVEL)
            assert outer["r_lo"] - 1e-12 <= b["r_lo"] < b["r_hi"] <= outer["r_hi"] + 1e-12
            assert outer["phi_lo"] - 1e-12 <= b["phi_lo"] < b["phi_hi"] <= outer["phi_hi"] + 1e-12
        assert np.all(v6.tile_of(fine, level) == tile)
    if level == 0:  # S64's numbering: a tile's 64, in order
        assert v6.finest_of([TILE], 0).tolist() == list(range(TILE * 64, TILE * 64 + 64))
    # every finest cell stands in exactly one level-k tile
    every = np.arange(sy.CELL_COUNT * 64, dtype=np.int64)
    assert np.array_equal(np.sort(v6.finest_of(list(range(sy.CELL_COUNT * sy.children_per_cell(level))), level)), every)


# --- R1: without level= every answer is S64's ---------------------------------------------------------------------------

def test_level_0_is_s64_s_form_byte_for_byte(service):
    """level=0 and no level= are one answer, the tile's and the whole table's (S65's builder compared both against the
    S64 code itself before the change: five answers, the same sha256)."""
    q = {"template": "milky_way", "cells": "259,260,261", "l_min": "2251", "precision": "f4", "filters": curves("rgb"), "white": 6500}
    first = ask(service, "/api/bright", **q)[2].body
    assert ask(service, "/api/bright", level=0, **q)[2].body == first
    assert wire.decode(first)[0]["tile"]["level"] == 0
    whole = ask(service, "/api/bright", template="milky_way", table=1, precision="f4")[2].body
    assert ask(service, "/api/bright", template="milky_way", table=1, precision="f4", level=0)[2].body == whole


# --- R2: a level-k tile is the level-0 tile restricted, row for row ------------------------------------------------------

@pytest.mark.parametrize("template,layer", [("milky_way", "on"), ("ngc_4414", "on"), ("milky_way", "off"), ("ngc_4414", "off")])
def test_a_level_k_tile_is_the_level_0_tile_s_rows_restricted_to_it(service, template, layer):
    used = grid_l(K_1E3)
    base = {"template": template, "layer": layer, "l_min": repr(used), "filters": curves("rgb"), "white": 6500}
    h0, a0, _ = ask(service, "/api/bright", cells=TILE, **base)
    cell0 = np.asarray(a0["cell"])
    assert h0["count"]["returned"] > 300
    galaxy = galaxy_of(service)
    for level in LEVELS:
        kids = children(TILE, level)
        picks = [kids[0], kids[min(len(kids) // 2 + 1, len(kids) - 2)], kids[-1]]
        singles = []
        for c in picks:
            h, a, _ = ask(service, "/api/bright", cells=c, level=level, **base)
            fine = v6.finest_of([c], level)
            mask = np.isin(cell0, fine)
            assert h["tile"] == {**h0["tile"], "cells": [c], "level": level}
            assert h["cells"]["count"] == fine.size == 4 ** (sy.MAX_LEVEL - level)
            assert h["columns"] == h0["columns"] and set(a) == set(a0)
            for name in a0:  # the same rows in the same order: every column bytes-equal
                assert np.asarray(a[name]).tobytes() == np.asarray(a0[name])[mask].tobytes(), (level, c, name)
            assert np.all(v6.tile_of(np.asarray(a["cell"]), level) == c)
            assert h["count"]["expected"] == pytest.approx(float(galaxy.at_threshold(fine, K_1E3).sum()), rel=1e-12)
            singles.append(h["count"]["expected"])
        # several at once: grouped by tile ascending, each tile's rows a run, the same rows
        h, a, _ = ask(service, "/api/bright", cells=",".join(map(str, picks)), level=level, **base)
        runs = v6.tile_of(np.asarray(a["cell"]), level)
        assert np.all(np.diff(runs) >= 0) and h["tile"]["cells"] == sorted(picks)
        got, want = by_cell_rank(a), by_cell_rank({k: np.asarray(v)[np.isin(cell0, v6.finest_of(picks, level))] for k, v in a0.items()})
        assert all(got[k].tobytes() == want[k].tobytes() for k in a0)
        assert h["count"]["expected"] == pytest.approx(sum(singles), rel=1e-12)
        # every child of the tile at once is the level-0 tile, star for star (a census identical at every level)
        h, a, _ = ask(service, "/api/bright", cells=",".join(map(str, kids)), level=level, **base)
        assert h["count"]["returned"] == h0["count"]["returned"]
        got, want = by_cell_rank(a), by_cell_rank(a0)
        assert all(got[k].tobytes() == want[k].tobytes() for k in a0)
        for part in ("count", "light"):
            assert h[part]["expected"] == pytest.approx(h0[part]["expected"], rel=1e-12)


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("level", LEVELS)
def test_the_level_k_tiles_union_over_a_footprint_is_the_window_answer(service, template, level):
    """A 2 x 2 block of level-k cells across a ring edge and a sector edge (so across four level-0 tiles): the tiles'
    union is the window form's answer over the block's (R, phi) window, row for row."""
    n = 1 << level
    rings = (8 * n + n - 1, 9 * n)
    sectors = (5 * n + n - 1, 6 * n)
    ids = sorted(level_id(i, j, level) for i in rings for j in sectors)
    R = service.grid.R
    bs = [sy.cell_bounds(R, c, level) for c in ids]
    window = {"r_min": repr(min(b["r_lo"] for b in bs)), "r_max": repr(max(b["r_hi"] for b in bs)),
              "phi_min": repr(min(b["phi_lo"] for b in bs)), "phi_max": repr(max(b["phi_hi"] for b in bs))}
    assert sorted(sy.cells_in(R, *(float(window[k]) for k in ("r_min", "r_max", "phi_min", "phi_max")), level=level)) == ids
    used = grid_l(K_3E3 - 10 * (level - 1))
    th, ta, _ = ask(service, "/api/bright", template=template, cells=",".join(map(str, ids)), level=level, l_min=repr(used))
    wh, wa, _ = ask(service, "/api/bright", template=template, l_min=repr(used), **window)
    assert th["cells"]["count"] == wh["cells"]["count"] == 4 * 4 ** (sy.MAX_LEVEL - level)
    assert th["count"]["returned"] == wh["count"]["returned"] > 20
    a, b = by_cell_rank(ta), by_cell_rank(wa)
    assert all(a[name].tobytes() == b[name].tobytes() for name in wh["columns"])
    for part in ("count", "light"):
        assert th[part]["expected"] == pytest.approx(wh[part]["expected"], rel=1e-12)


@pytest.mark.parametrize("level", LEVELS)
def test_a_level_k_tile_at_a_threshold_is_the_same_bytes_every_time(service, level):
    tile = children(TILE, level)[1]
    q = {"template": "milky_way", "cells": tile, "level": level, "l_min": repr(grid_l(SAME_BYTES_K[level])), "precision": "f4",
         "filters": curves("rgb"), "white": 6500}
    first = ask(service, "/api/bright", **q)[2].body
    assert ask(service, "/api/bright", **q)[2].body == first
    # held deeper by a lower threshold's request (of the whole level-0 tile), the cache cuts the same prefix
    ask(service, "/api/bright", template="milky_way", cells=TILE, l_min=repr(grid_l(SAME_BYTES_K[level] - 2)))
    assert ask(service, "/api/bright", **q)[2].body == first
    header = wire.decode(first)[0]
    assert header["tile"]["level"] == level and "stages" not in header
    assert f"level-{level} tiles" in header["threshold"]["why"]


# --- R1: the table for the cells asked -----------------------------------------------------------------------------------

@pytest.mark.parametrize("template", TEMPLATES)
def test_the_table_for_the_cells_asked_is_their_finest_cells_summed(service, template):
    _, whole, _ = ask(service, "/api/bright", template=template, table=1)
    E0 = whole["expected"]
    K = br.LOG_L_GRID.size
    for level in LEVELS:
        ids = children(TILE, level) + children(TILE + 1, level)
        h, t, _ = ask(service, "/api/bright", template=template, table=1, cells=",".join(map(str, ids)), level=level)
        e = t["expected"]
        assert e.shape == (len(ids), K) and e.dtype == np.float64 and np.all(np.diff(e, axis=1) <= 0.0)
        assert h["table"]["cells"] == sorted(ids) and h["table"]["level"] == level
        assert "level-k cells in view" in h["table"]["rule"] and "point budget" in h["table"]["rule"]
        assert "sub-rings" in h["cells"]["children"] and h["cells"]["ring_edges"] == sy.cell_edges(service.grid.R)[0].tolist()
        assert t["threshold"].tobytes() == whole["threshold"].tobytes()
        # a level-k cell's row is the sum of its finest cells' rows (the level-3 table for those cells)
        fine = v6.finest_of(ids, level)
        _, t3, _ = ask(service, "/api/bright", template=template, table=1, cells=",".join(map(str, fine.tolist())), level=3)
        summed = t3["expected"][np.argsort(np.argsort(fine))].reshape(len(ids), -1, K).sum(axis=1)
        assert np.all(np.abs(e - summed) <= 1e-12 * np.abs(summed))
        # and the level-0 table's row is its level-k cells' rows summed: one quadrature at every level
        per0 = e.reshape(2, sy.children_per_cell(level), K).sum(axis=1)
        assert np.all(np.abs(per0 - E0[[TILE, TILE + 1]]) <= 1e-12 * np.abs(E0[[TILE, TILE + 1]]))
    # f4 for the viewer: the counts only
    _, t4, _ = ask(service, "/api/bright", template=template, table=1, cells=TILE * 4, level=1, precision="f4")
    assert t4["expected"].dtype == np.float32 and t4["threshold"].dtype == np.float64


def test_a_level_k_cell_s_realised_count_is_poisson_about_its_table_row(service):
    cells = sorted({c for c, _ in POISSON_PAIRS})
    _, t, _ = ask(service, "/api/bright", template="milky_way", table=1, cells=",".join(map(str, cells)), level=2)
    z = []
    for cell, k in POISSON_PAIRS:
        lam = float(t["expected"][cells.index(cell), k])
        th, _, _ = ask(service, "/api/bright", template="milky_way", cells=cell, level=2, l_min=repr(float(t["threshold"][k])))
        assert th["count"]["expected"] == pytest.approx(lam, rel=1e-12) and lam > 5.0
        z.append((th["count"]["returned"] - lam) / math.sqrt(lam))
    assert np.max(np.abs(z)) < 4.0


# --- R3: at the tiles' threshold S48's identity holds as it is ----------------------------------------------------------

def resolved_per_ring(service: Service, template: str, l_min: float):
    """bright.resolve on the template's own fields - what /api/render's l_min= decomposes (Service._unresolved)."""
    from galaxy.api.service import RENDER_STARS, Query

    q = Query({"template": [template]})
    model = service._model(q)
    declared = service._declared(model)
    wanted = [*RENDER_STARS, *(n for n in br.RESOLVE_READS if n in declared)]
    out, _ = service.compute(model, service._overrides(model, q), wanted, service._layer(q))
    spec = service.grid.spec
    constants = {k: c.value for k, c in model.constants.items()}
    return br.resolve(out.fields, float(spec.t_max), int(spec.n_t), constants, l_min)


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("level", (2, 3))
def test_the_render_at_level_k_resolves_at_the_tiles_threshold_and_closes_per_ring(service, template, level):
    """The frame's one threshold at level k: the per-cells table's pick for the cells in view at the default point budget,
    the tile's l_min_used, and the render's l_min at level k (cell means over the same cells) resolved at exactly that
    float. There S48's identity holds PER RING (S65 review, F3): unresolved + young + bright is the stars' light ring by
    ring to 1e-12, and the eight bands' anchors ring by ring and band (bright.resolve, the decomposition the render's
    l_min= runs; the reviewer measured 2.2e-16 and 4.4e-16). In each cell in view the bright part the remainder leaves -
    the middle and old parts placed by their own weights less stars_unresolved - is not negative."""
    ids = children(TILE, level)[:4]
    _, t, _ = ask(service, "/api/bright", template=template, table=1, cells=",".join(map(str, ids)), level=level)
    k = next(j for j in range(t["threshold"].size) if t["expected"][:, j].sum() <= 10**3.5)
    th, _, _ = ask(service, "/api/bright", template=template, cells=",".join(map(str, ids)), level=level, l_min=repr(float(t["threshold"][k])))
    used = th["tile"]["l_min_used"]
    assert used == float(t["threshold"][k])
    R = service.grid.R
    bs = [sy.cell_bounds(R, c, level) for c in ids]
    window = {"r_min": min(b["r_lo"] for b in bs), "r_max": max(b["r_hi"] for b in bs),
              "phi_min": min(b["phi_lo"] for b in bs), "phi_max": max(b["phi_hi"] for b in bs)}
    rh, ra, _ = ask(service, "/api/render", template=template, level=level, filters=curves("rgb"), white=6500, l_min=repr(used),
                    **{k_: repr(v) for k_, v in window.items()})
    assert rh["resolved"]["l_min"] == used == rh["resolved"]["requested"]
    res = resolved_per_ring(service, template, used)
    light = res.light
    total = np.asarray(light["total"], dtype=float)
    lit = total > 0
    assert lit.sum() > 100
    parts = np.asarray(light["unresolved"]) + np.asarray(light["young"]) + np.asarray(light["bright"])
    assert np.max(np.abs(parts[lit] / total[lit] - 1.0)) < 1e-12
    a = res.anchors
    anchored = a["unresolved_middle"] + a["unresolved_old"] + a["young"] + a["bright_middle"] + a["bright_old"]
    on = a["total"] > 0
    assert np.max(np.abs(anchored[on] / a["total"][on] - 1.0)) < 1e-12
    # and the render's whole-disc numbers are these rings' (the trapezoid in R the header states)
    assert rh["resolved"]["light"]["bright"] > 0
    placed = (np.asarray(ra["stars_middle"]) * np.asarray(ra["stars_middle_placement"])[:, None]
              + np.asarray(ra["stars_old"]) * np.asarray(ra["stars_placement"])[:, None])
    assert np.all(placed - np.asarray(ra["stars_unresolved"]) >= -1e-12 * placed)


# --- R4: the refusal before any draw ------------------------------------------------------------------------------------

def test_a_ring_past_the_draw_s_bound_is_refused_before_any_draw(service):
    """The probe's out-of-memory case: ngc_4414 at 1.1 Lsun at a 62 pc stand (the ring at R = 8 kpc holds 4.0e7 expected
    stars above 10^0.05 Lsun; the ring-first draw holds about 310 bytes a star). Refused in under a second once the
    galaxy's tables are held, naming the count, the bound and #159; the cache holds nothing new."""
    ask(service, "/api/bright", template="ngc_4414", table=1, cells=TILE, level=0)  # the galaxy's tables, held
    cells = ",".join(map(str, children(TILE, 3)[:2]))
    rows_before = service.bright._rows
    t0 = time.perf_counter()
    message = refused(service, "/api/bright", template="ngc_4414", cells=cells, level=3, l_min=1.1)
    assert time.perf_counter() - t0 < 1.0
    assert str(MAX_STARS) in message and "#159" in message and "expected stars" in message
    assert service.bright._rows == rows_before
    galaxy = galaxy_of(service)
    assert galaxy.ring_curve[8, br.interval_of(10**0.05)] > MAX_STARS
    # the default point budget's deepest stand on the Milky Way (62 pc, 10^1.85 Lsun) stays under it and is served
    ask(service, "/api/bright", template="milky_way", cells=children(TILE, 3)[0], level=3, l_min=repr(grid_l(57)))
    assert galaxy_of(service).ring_curve[:, 57].max() < MAX_STARS


def test_a_window_whose_ring_is_past_the_bound_is_refused_before_any_draw(service):
    """S65 review (F4): the window form (l_min=) draws the same ring-first way, so the same guard. One level-3 cell's window
    on ngc_4414 at 1.1 Lsun expects some 2e4 stars (under the 2e5 cap) while its ring holds 4.0e7 (a ~13 GB draw)."""
    ask(service, "/api/bright", template="ngc_4414", table=1, cells=TILE, level=0)  # the galaxy's tables, held
    b = sy.cell_bounds(service.grid.R, children(TILE, 3)[0], 3)
    window = {"r_min": repr(b["r_lo"]), "r_max": repr(b["r_hi"]), "phi_min": repr(b["phi_lo"]), "phi_max": repr(b["phi_hi"])}
    rows_before = service.bright._rows
    t0 = time.perf_counter()
    message = refused(service, "/api/bright", template="ngc_4414", l_min=1.1, **window)
    assert time.perf_counter() - t0 < 1.0
    ring = galaxy_of(service).ring_curve[8, br.interval_of(1.1)]
    assert ring > MAX_STARS and f"{ring:.0f}" in message and str(MAX_STARS) in message and "#159" in message
    assert service.bright._rows == rows_before


def test_the_refusals_at_a_level(service):
    b = "/api/bright"
    assert "outside 0..3" in refused(service, b, cells=TILE, level=4, l_min=1000)
    assert "outside 0..3" in refused(service, b, cells=TILE, level=-1, l_min=1000)
    top = sy.CELL_COUNT * 16
    assert "level-2 cell ids" in refused(service, b, cells=top, level=2, l_min=1000)
    assert "names a cell twice" in refused(service, b, cells=f"{TILE * 4},{TILE * 4}", level=1, l_min=1000)
    assert "needs cells=" in refused(service, b, table=1, level=2)
    assert "level-3 cell ids" in refused(service, b, table=1, cells=sy.CELL_COUNT * 64, level=3)
    assert "names tiles" in refused(service, b, l_min=1000, level=1, r_min=7, r_max=9, phi_min=0, phi_max=0.4)
    for extra in ({"n": 10}, {"l_min": 1000}, {"filters": curves("rgb")}, {"r_min": 7}):
        refused(service, b, table=1, cells=TILE, level=0, **extra)
