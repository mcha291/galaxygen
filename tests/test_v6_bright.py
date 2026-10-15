"""S64 (BUILD_III Phase V6; RULING_S64 R8, T28): the bright stars by tiles, the expected-count table, the remainder alone.

R8 (a): ``/api/bright?cells=<level-0 ids>&l_min=`` - each tile's stars above l_min snapped up to the 0.05 dex grid,
the same bytes every time; the 2e5 cap on the request. (b) ``/api/bright?table=1`` - every level-0 cell's expected count
above every grid threshold. (c) ``/api/render?only=remainder&l_min=`` - two per-ring arrays the remainder is exactly,
placed by the whole render's own weights. Gate (iii): the tiles' union over a footprint is the window answer row for
row; one l_min per frame keeps S48's identity as it is; the remainder alone is the full render's stars_unresolved to
1e-12. Both templates, layer on and off where it bears. Every check recomputes with this file's own arithmetic.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import MAX_BRIGHTEST, Service
from galaxy.stages import bright as br
from galaxy.stages import systems as sy

ROOT = Path(__file__).resolve().parents[1]
GAL = ROOT / "frontend" / "src" / "galaxy"
SETS = {**json.loads((GAL / "filters.json").read_text(encoding="utf-8"))["sets"],
        **json.loads((GAL / "instruments.json").read_text(encoding="utf-8"))["sets"]}
TEMPLATES = ("milky_way", "ngc_4414")
K_1E3, K_3E3, K_1E4 = 80, 90, 100  # LOG_L_GRID's 10^3, 10^3.5, 10^4 Lsun
# The probe's 10^6-over-the-disc depth, 2251 Lsun (REPORT §1D), snaps up to 10^3.40 = 2511.89 Lsun.
DEPTH = 2251.0
# Ten tiles and three thresholds for the table against the realised counts (default galaxy, milky_way template),
# measured at S64: the realised counts' z = (n - expected) / sqrt(expected) lay in -1.64..+2.68 over the thirty
# (one tile, 900, holds 0.01 expected stars at 10^3 and none realised).
POISSON_TILES = (261, 262, 100, 500, 700, 33, 4, 900, 288, 400)
# The tiles' expected light above 10^4 Lsun over the disc (the finest cells' 8-midpoint radial rule, bright.BrightGalaxy)
# against bright.resolve's light above it (the trapezoid on the render's R grid): two quadratures of one luminosity
# function, measured at S64 at 2.64e-5 (milky_way, 10^3.35); a bound, not a target.
QUADRATURES_MISS = 1e-4


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


def window_of(tiles: list[int], R: np.ndarray) -> dict:
    """The (R, phi) window that is exactly the tiles' union: a block of whole rings by whole sectors."""
    rings, sectors = sy.cell_edges(R)
    i = sorted({t // 32 for t in tiles})
    j = [t % 32 for t in tiles]
    lo = j[0] if not (0 in j and 31 in j) else max(s for s in j if s > 16)
    span = len(set(j))
    return {"r_min": repr(float(rings[i[0]])), "r_max": repr(float(rings[i[-1] + 1])),
            "phi_min": repr(float(sectors[lo])), "phi_max": repr(float(sectors[lo]) + span * 2.0 * math.pi / 32)}


# --- (a) the tiles' union is the window answer row for row ------------------------------------------------------------

@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("tiles", [[259, 260, 261, 291, 292, 293], [415, 384]], ids=["block", "across-phi-0"])
def test_the_tiles_union_is_the_window_answer_row_for_row(service, template, tiles):
    used = grid_l(K_1E3)
    th, ta, _ = ask(service, "/api/bright", template=template, cells=",".join(map(str, tiles)), l_min=repr(used))
    key_tile = next(reversed(service._bright_galaxies))
    wh, wa, _ = ask(service, "/api/bright", template=template, l_min=repr(used), **window_of(tiles, service.grid.R))
    # one galaxy and one cell cache for both forms: _bright's key, made the same way
    assert next(reversed(service._bright_galaxies)) == key_tile
    assert wh["cells"]["count"] == th["cells"]["count"] == 64 * len(tiles)
    assert th["tile"]["l_min_used"] == wh["threshold"]["l_min"] == used and th["tile"]["cells"] == sorted(tiles)
    assert th["columns"] == wh["columns"] and th["count"]["returned"] == wh["count"]["returned"] > 100
    a, b = by_cell_rank(ta), by_cell_rank(wa)
    for name in wh["columns"]:
        assert a[name].tobytes() == b[name].tobytes(), name
    # the tile body is grouped by finest cell ascending, brightest first within each
    cell, lum = np.asarray(ta["cell"]), np.asarray(ta["bright_star_luminosity"])
    assert np.all(np.diff(cell) >= 0) and np.all(np.diff(lum)[np.diff(cell) == 0] <= 0)
    assert np.isin(cell // 64, tiles).all()
    for part in ("count", "light"):
        assert th[part]["expected"] == pytest.approx(wh[part]["expected"], rel=1e-12)


# --- (b) a tile at a threshold is the same bytes every time -----------------------------------------------------------

def test_a_tile_at_a_threshold_is_the_same_bytes_every_time(service):
    q = {"template": "milky_way", "cells": "261", "l_min": repr(DEPTH), "precision": "f4", "filters": curves("rgb"), "white": 6500}
    first = ask(service, "/api/bright", **q)[2].body
    assert ask(service, "/api/bright", **q)[2].body == first
    # held deeper by a lower threshold's request, the cache cuts the same prefix: still the same bytes
    ask(service, "/api/bright", template="milky_way", cells="261", l_min=repr(grid_l(K_1E3 - 10)))
    assert ask(service, "/api/bright", **q)[2].body == first
    header, arrays = wire.decode(first)
    # the header has no timing field, and no `stages` (what ran depends on what the service held)
    assert "stages" not in header and not any("time" in k or "seconds" in k for k in header)
    assert header["tile"]["l_min_asked"] == DEPTH and header["tile"]["l_min_used"] == pytest.approx(10**3.4, rel=1e-12)
    assert header["tile"]["grid"]["log_l_step"] == 0.05 and arrays["response"].shape == (arrays["cell"].size, 3)
    # another l_min that snaps to the same grid value: the same rows (only l_min_asked differs)
    other, rows, _ = ask(service, "/api/bright", **{**q, "l_min": repr(header["tile"]["l_min_used"] * (1 - 1e-7))})
    assert other["tile"]["l_min_used"] == header["tile"]["l_min_used"]
    assert all(rows[k].tobytes() == arrays[k].tobytes() for k in arrays)


# --- (c) what the tile form, the table and the remainder refuse -------------------------------------------------------

def test_the_refusals(service):
    b = "/api/bright"
    assert "needs l_min" in refused(service, b, cells="261")
    for extra in ({"n": 10}, {"view": ",".join(["1"] * 16)}, {"r_min": 7}, {"phi_max": 1}):
        assert "takes no" in refused(service, b, cells="261", l_min=1000, **extra)
    for bad in ("1024", "-1", "x", "", "3,3"):
        refused(service, b, cells=bad, l_min=1000)
    assert "last threshold" in refused(service, b, cells="261", l_min=1e7)
    assert "positive" in refused(service, b, cells="261", l_min=0)
    every = ",".join(map(str, range(sy.CELL_COUNT)))
    message = refused(service, b, cells=every, l_min=1.0)
    assert str(MAX_BRIGHTEST) in message and "expected stars" in message
    assert "table=1" in refused(service, b, table=2)
    for extra in ({"cells": "261"}, {"l_min": 1000}, {"n": 10}, {"filters": curves("rgb")}):
        refused(service, b, table=1, **extra)
    r = "/api/render"
    assert "needs l_min" in refused(service, r, only="remainder", filters=curves("rgb"))
    assert "only=remainder" in refused(service, r, only="stars", filters=curves("rgb"), l_min=1000)
    assert "takes no level" in refused(service, r, only="remainder", filters=curves("rgb"), l_min=1000, level=1)


# --- (R8b) the expected-count table ----------------------------------------------------------------------------------

def test_the_table_is_each_tile_s_expected_count_at_every_grid_threshold(service):
    h, t, r = ask(service, "/api/bright", template="milky_way", table=1)
    assert t["expected"].shape == (sy.CELL_COUNT, br.LOG_L_GRID.size) and t["expected"].dtype == np.float64
    assert t["log_l"].tobytes() == br.LOG_L_GRID.tobytes() and np.array_equal(t["threshold"], 10.0 ** br.LOG_L_GRID)
    assert "smallest grid threshold" in h["table"]["rule"] and "point budget" in h["table"]["rule"]
    rings, sectors = sy.cell_edges(service.grid.R)
    assert h["cells"]["ring_edges"] == rings.tolist() and h["cells"]["sector_edges"] == sectors.tolist()
    assert np.all(np.diff(t["expected"], axis=1) <= 0.0)
    # f4 for the viewer: the counts only; the thresholds stay float64 so a threshold read back is the grid's value
    _, t4, r4 = ask(service, "/api/bright", template="milky_way", table=1, precision="f4")
    assert t4["expected"].dtype == np.float32 and t4["threshold"].tobytes() == t["threshold"].tobytes()
    assert len(r4.body) < 0.6 * len(r.body)
    # The table against this file's own quadrature, one cell, one threshold, at 1e-9: each finest cell's area times
    # each part's stars per pc² above the threshold (its mass on every isochrone times the count table) times its weight.
    galaxy = service._bright_galaxies[next(reversed(service._bright_galaxies))][0]
    count = br.luminosity_function().count_above.reshape(-1, br.LOG_L_GRID.size)
    for cell, k in ((261, 87), (100, K_3E3)):
        i, j = divmod(cell, 32)
        own = 0.0
        for a in range(8):
            for b in range(8):
                for p in range(2):
                    stars_per_pc2 = float(np.dot(galaxy.mass_cell[p, 8 * i + a], count[:, k]))
                    own += galaxy.area[8 * i + a] * galaxy.weights[p, 8 * i + a, 8 * j + b] * stars_per_pc2
        assert t["expected"][cell, k] == pytest.approx(own, rel=1e-9)
    # every ring's tiles sum to its ring's own expected curve (I2's expectation, D220)
    rings_sum = t["expected"].reshape(32, 32, -1).sum(axis=1)
    lit = galaxy.ring_curve > 0
    assert np.max(np.abs(rings_sum[lit] / galaxy.ring_curve[lit] - 1.0)) < 1e-13
    # the table's column is each tile's count.expected, and the realised count is Poisson about it
    z = []
    for k in (K_1E3, K_3E3, K_1E4):
        for cell in POISSON_TILES:
            th, _, _ = ask(service, "/api/bright", template="milky_way", cells=cell, l_min=repr(float(t["threshold"][k])))
            lam = t["expected"][cell, k]
            assert th["count"]["expected"] == pytest.approx(lam, rel=1e-12)
            z.append((th["count"]["returned"] - lam) / math.sqrt(max(lam, 1e-300)))
    assert np.max(np.abs(z)) < 4.0 and abs(float(np.mean(z))) < 4.0 / math.sqrt(len(z))


# --- (R8c) the remainder alone ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("template,layer", [("milky_way", "on"), ("ngc_4414", "on"), ("milky_way", "off")])
@pytest.mark.parametrize("filters", ["rgb", "wfc3"])
def test_the_remainder_alone_placed_by_the_render_s_weights_is_stars_unresolved(service, template, layer, filters):
    q = {"template": template, "layer": layer, "filters": curves(filters), "white": 6500, "l_min": repr(DEPTH)}
    fh, fa, _ = ask(service, "/api/render", **q)
    rh, ra, r = ask(service, "/api/render", only="remainder", **q)
    assert set(ra) == {"stars_unresolved_middle", "stars_unresolved_old"} and rh["only"] == "remainder"
    parts = rh["remainder"]["parts"]
    # the weights it names are the ones the whole render's ages names for the same parts
    assert {p: parts[p]["weight"] for p in parts} == {p: fh["ages"]["parts"][p]["weight"] for p in ("middle", "old")}
    placed = sum(ra[parts[p]["array"]][:, None, :] * fa[parts[p]["weight"]][..., None] for p in ("middle", "old"))
    want = fa["stars_unresolved"]
    assert np.max(np.abs(placed - want)) <= 1e-12 * np.max(np.abs(want))
    assert rh["resolved"] == fh["resolved"] and rh["axes"]["stars_unresolved_middle"] == ["R", "filter"]
    assert rh["layer"] == fh["layer"] and ra["stars_unresolved_old"].shape == (service.grid.R.size, 3)
    if layer == "off":  # the physics alone: every placing weight even round its ring
        assert all(np.allclose(fa[parts[p]["weight"]], 1.0, rtol=0, atol=1e-12) for p in parts)
    _, _, small = ask(service, "/api/render", only="remainder", precision="f4", **q)
    assert len(small.body) < 32_000


def test_the_remainder_runs_no_stage_the_l_min_render_does_not():
    """Rule D4, from a fresh service each: what the remainder alone runs is inside what the full l_min render runs,
    and none of the gas's, dust's or census's stages."""
    q = {"filters": [curves("rgb")], "l_min": ["1000"]}
    alone = Service().handle("/api/render", {**q, "only": ["remainder"]})
    full = Service().handle("/api/render", q)
    assert alone.ok and full.ok
    assert set(alone.stages) <= set(full.stages)
    assert not {"ism", "dust", "clouds", "clusters", "nebular"} & set(alone.stages)


# --- (d) one l_min per frame keeps S48's identity ---------------------------------------------------------------------

@pytest.mark.parametrize("template", TEMPLATES)
def test_one_threshold_per_frame_keeps_s48_s_identity(service, template):
    """The frame asks its tiles and its remainder at one grid threshold: the remainder is resolved at exactly the
    tiles' l_min_used (the same float), and there S48's identity holds as it is - unresolved + young + bright is the
    stars' light, per ring and band (test_bright, 1e-9) and over the disc (1e-12, test_render's method). The tiles'
    expected light over the disc and the identity's bright part are one luminosity function on two quadratures."""
    th, _, _ = ask(service, "/api/bright", template=template, cells="261", l_min=repr(DEPTH))
    used = th["tile"]["l_min_used"]
    rh, _, _ = ask(service, "/api/render", template=template, only="remainder", filters=curves("rgb"), l_min=repr(used))
    assert rh["resolved"]["l_min"] == used == rh["resolved"]["requested"]
    light = rh["resolved"]["light"]
    assert light["unresolved"] + light["young"] + light["bright"] == pytest.approx(light["total"], rel=1e-12)
    # over the disc at 10^4 Lsun (under the cap): the window form's expected light against the identity's bright part
    wh, _, _ = ask(service, "/api/bright", template=template, l_min=repr(grid_l(K_1E4)))
    rh4, _, _ = ask(service, "/api/render", template=template, only="remainder", filters=curves("rgb"), l_min=repr(grid_l(K_1E4)))
    assert abs(wh["light"]["expected"] / rh4["resolved"]["light"]["bright"] - 1.0) < QUADRATURES_MISS


# --- (e) layer on and off: the same stars at the same threshold -------------------------------------------------------

def test_with_the_layer_off_a_ring_s_tiles_hold_the_same_stars(service):
    ring = ",".join(str(8 * 32 + s) for s in range(32))
    got = {}
    for layer in ("on", "off"):
        h, a, _ = ask(service, "/api/bright", template="milky_way", layer=layer, cells=ring, l_min=repr(grid_l(K_3E3)))
        _, t, _ = ask(service, "/api/bright", template="milky_way", layer=layer, table=1)
        got[layer] = (h, a, t["expected"])
    (h0, a0, t0), (h1, a1, t1) = got["on"], got["off"]
    assert h0["layer"] != h1["layer"] and h0["tile"]["l_min_used"] == h1["tile"]["l_min_used"]
    assert h0["count"]["returned"] == h1["count"]["returned"] > 1000
    for name in ("bright_star_luminosity", "bright_star_age"):
        assert np.sort(a0[name]).tobytes() == np.sort(a1[name]).tobytes(), name
    per_tile = [np.bincount(np.asarray(a["cell"]) // 64 - 8 * 32, minlength=32) for a in (a0, a1)]
    assert not np.array_equal(*per_tile)  # the layer places them round the ring
    on_ring, off_ring = (t.reshape(32, 32, -1).sum(axis=1) for t in (t0, t1))
    lit = on_ring > 0
    assert np.max(np.abs(off_ring[lit] / on_ring[lit] - 1.0)) < 1e-13
