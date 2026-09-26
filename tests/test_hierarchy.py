"""The cell hierarchy (S32, BUILD_II Phase 8, D181; RENDER_PHYSICS §5c).

A level-k cell is one of 4^k children of a level-0 cell with its own seeded stream. The
contract, asserted at every level: the same bounds and level twice give the same rows;
overlapping windows agree on the overlap; **a parent's stars are its children's** (the union
property) and a smaller sample is a subset of a larger one within a cell (the prefix property);
and the same star opened by either name has the same planets. This is the determinism contract
BUILD_II names as the one that can hold at one level and break at another.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.api.service import Service
from galaxy.api import wire
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages import systems as sy

STAR_COLS = ("star_radius", "star_azimuth", "star_height", "star_age", "star_birth_radius", "star_metallicity",
             "star_alpha", "star_mass", "star_population", "star_luminosity")
NAME = ("level", "cell", "index")
PARENT = 300  # ring 9, sector 12: inside R0, a few dozen stars at the default sample


@pytest.fixture(scope="module")
def fields():
    models, _, _ = production()
    basic = next(m for m in models if m.name == "basic")
    o = run(basic, only=tuple(sy.SYSTEMS.requires))
    return o.fields, o.grid.R, o.grid.t


def names(cat, mask=None):
    cols = [np.asarray(cat[n]) if mask is None else np.asarray(cat[n])[mask] for n in NAME]
    return set(zip(*(c.tolist() for c in cols)))


def test_ids_bounds_and_windows():
    R = np.linspace(0.05, 30.0, 400)
    assert sy.children_per_cell(0) == 1 and sy.children_per_cell(3) == 64
    for level in range(sy.MAX_LEVEL + 1):
        for q in range(sy.children_per_cell(level)):
            cid = sy.child_id(PARENT, level, q)
            assert sy.parent_of(cid, level) == (PARENT, q)
    parent = sy.cell_bounds(R, PARENT)
    kids = [sy.cell_bounds(R, sy.child_id(PARENT, 2, q), 2) for q in range(16)]
    # The children tile the parent exactly: 4 sub-rings by 4 sub-sectors of equal width.
    assert min(k["r_lo"] for k in kids) == parent["r_lo"] and max(k["r_hi"] for k in kids) == pytest.approx(parent["r_hi"])
    assert min(k["phi_lo"] for k in kids) == parent["phi_lo"] and max(k["phi_hi"] for k in kids) == pytest.approx(parent["phi_hi"])
    area = sum((k["r_hi"] ** 2 - k["r_lo"] ** 2) * (k["phi_hi"] - k["phi_lo"]) for k in kids)
    assert area == pytest.approx((parent["r_hi"] ** 2 - parent["r_lo"] ** 2) * (parent["phi_hi"] - parent["phi_lo"]))
    # A window meets 4^k times as many children as level-0 cells, up to the edges it cuts.
    assert len(sy.cells_in(R, 7.0, 9.0, 0.0, 0.4)) == 9
    assert len(sy.cells_in(R, 7.0, 9.0, 0.0, 0.4, level=1)) == 30
    assert len(sy.cells_in(R, 7.0, 9.0, 0.0, 0.4, level=2)) == 90
    # Canonical names never collide across levels.
    tops = [sy.canonical_cell(k, sy.CELL_COUNT * sy.children_per_cell(k) - 1) for k in range(sy.MAX_LEVEL + 1)]
    bottoms = [sy.canonical_cell(k, 0) for k in range(sy.MAX_LEVEL + 1)]
    assert all(tops[k] < bottoms[k + 1] for k in range(sy.MAX_LEVEL))


@pytest.mark.parametrize("level", [1, 2, 3])
def test_union_prefix_and_determinism_at_every_level(fields, level):
    F, R, t = fields
    parent = sy.materialise(F, R, t, 0, 20000, cells=[PARENT], migration=3.6)
    kids = [sy.child_id(PARENT, level, q) for q in range(sy.children_per_cell(level))]
    cat = sy.materialise(F, R, t, 0, 20000, cells=kids, migration=3.6, level=level)
    inherited = np.asarray(cat["level"]) == 0
    # Union: the parent's rows are exactly the children's inherited rows, column for column.
    assert names(cat, inherited) == {(0, PARENT, i) for i in range(parent.size)}
    order = np.argsort(np.asarray(cat["index"])[inherited])
    for n in STAR_COLS:
        assert np.array_equal(np.asarray(cat[n])[inherited][order], np.asarray(parent[n]), equal_nan=True), n
    # The children partition the parent: every inherited name once.
    assert int(inherited.sum()) == parent.size
    # Every row lies inside its child's footprint; the extras are 4^k − 1 times the parent's expectation.
    offset = 0
    for cid, n in cat.counts:
        b = sy.cell_bounds(R, cid, level)
        r = np.asarray(cat["star_radius"])[offset:offset + n]
        phi = np.mod(np.asarray(cat["star_azimuth"])[offset:offset + n], 2.0 * math.pi)
        assert np.all((r >= b["r_lo"] - 1e-9) & (r <= b["r_hi"] + 1e-9)) and np.all((phi >= b["phi_lo"] - 1e-9) & (phi <= b["phi_hi"] + 1e-9)), cid
        offset += n
    expected = sy.cell_expected(F["stellar_surface_density"], R, 20000, PARENT, sy.ArmPattern.from_fields(F))
    extras = int((~inherited).sum())
    assert extras == len(kids) * int(round(expected * (1.0 - 1.0 / len(kids))))
    # Determinism: a child alone is its slice of the whole set.
    q = 1
    alone = sy.materialise(F, R, t, 0, 20000, cells=[kids[q]], migration=3.6, level=level)
    off = sum(n for c, n in cat.counts if c < kids[q])
    n_alone = dict(cat.counts).get(kids[q], 0)
    assert alone.size == n_alone
    for n in STAR_COLS + NAME:
        assert np.array_equal(np.asarray(alone[n]), np.asarray(cat[n])[off:off + n_alone], equal_nan=True), n
    # Prefix: the child's rows at a smaller sample are a subset of its rows at a larger one, by name.
    small = sy.materialise(F, R, t, 0, 10000, cells=[kids[q]], migration=3.6, level=level)
    assert names(small) <= names(alone)
    # And the level-0 catalogue is untouched by the machinery: no name columns, the sample as always.
    assert "level" not in parent and parent.size == 22


def test_a_deeper_level_contains_its_parents_rows(fields):
    """Union across two steps: a level-1 child's rows are among its level-3 descendants' rows."""
    F, R, t = fields
    child1 = sy.child_id(PARENT, 1, 2)
    one = sy.materialise(F, R, t, 0, 20000, cells=[child1], migration=3.6, level=1)
    grand = [sy.child_id(PARENT, 3, q) for q in range(64)]
    three = sy.materialise(F, R, t, 0, 20000, cells=grand, migration=3.6, level=3)
    # The inherited rows of level 1 are the parent's rows in the child; at level 3 they are still there.
    inherited1 = names(one, np.asarray(one["level"]) == 0)
    assert inherited1 <= names(three, np.asarray(three["level"]) == 0)
    # Level-1 extras are not level-3 rows: each level has its own stream; the union property is about
    # the level-0 parent's stars (RENDER_PHYSICS §5c), and the plan says so.
    assert not (names(one, np.asarray(one["level"]) == 1) & names(three))


def test_the_api_serves_levels_and_opens_a_child_star():
    svc = Service()
    r0 = svc.handle("/api/region", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    r2 = svc.handle("/api/region", "r_min=7&r_max=9&phi_min=0&phi_max=0.4&level=2")
    assert r0.status == 200 and r2.status == 200
    h0, a0 = wire.decode(r0.body)
    h2, a2 = wire.decode(r2.body)
    assert h0["level"] == 0 and h2["level"] == 2 and h2["cells"]["of"] == sy.CELL_COUNT * 16
    assert set(("level", "cell", "index")) <= set(h2["columns"]) and "level" not in h0["columns"]
    # Every level-0 star of the window that lies in a child the window meets is among the level-2 rows
    # by name (the union property over the API; a level-0 cell's stars outside the window's children
    # belong to children the window did not ask for).
    R = np.linspace(0.05, 30.0, 400)
    wanted = set(h2["cells"]["ids"])
    theirs = set(zip(a2["level"].tolist(), a2["cell"].tolist(), a2["index"].tolist()))
    row = 0
    covered = 0
    for c, n in zip(h0["cells"]["ids"], h0["cells"]["counts"]):
        r = a0["star_radius"][row:row + n]
        phi = a0["star_azimuth"][row:row + n]
        for q in range(16):
            cid = sy.child_id(c, 2, q)
            if cid in wanted:
                inside = sy._within(r, phi, {}, R, c, 2, q)
                for i in np.flatnonzero(inside).tolist():
                    assert (0, c, i) in theirs, (c, i)
                    covered += 1
        row += n
    assert covered > 0
    assert h2["stars"]["materialised"] > 4 * h0["stars"]["materialised"]
    # An extra star opened by its child name has planets, and the same star opened twice is the same.
    extra = next(i for i, lv in enumerate(a2["level"].tolist()) if lv == 2)
    cell, index = int(a2["cell"][extra]), int(a2["index"][extra])
    s1 = svc.handle("/api/system", f"level=2&cell={cell}&index={index}")
    s2 = svc.handle("/api/system", f"level=2&cell={cell}&index={index}")
    assert s1.status == 200 and s1.body == s2.body
    hs, _ = wire.decode(s1.body)
    assert hs["level"] == 2 and hs["cell"] == cell and hs["star"]["star_radius"] == pytest.approx(float(a2["star_radius"][extra]))
    # An inherited star is opened by its level-0 name, and gets the planets it had at level 0.
    inh = next(i for i, lv in enumerate(a2["level"].tolist()) if lv == 0)
    p0 = svc.handle("/api/system", f"cell={int(a2['cell'][inh])}&index={int(a2['index'][inh])}")
    assert p0.status == 200
    # Refusals: brightest below level 0, a level past the deepest, a whole disc at level 3.
    assert svc.handle("/api/region", "level=1&brightest=10").status == 400
    assert svc.handle("/api/region", "level=4").status == 400
    assert svc.handle("/api/region", "level=3").status == 400


def test_the_clouds_route_is_a_census_that_levels_only_filter():
    svc = Service()
    r0 = svc.handle("/api/clouds", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    r2 = svc.handle("/api/clouds", "r_min=7&r_max=9&phi_min=0&phi_max=0.4&level=2")
    assert r0.status == 200 and r2.status == 200
    h0, a0 = wire.decode(r0.body)
    h2, a2 = wire.decode(r2.body)
    assert h0["level"] == 0 and h2["level"] == 2
    assert h0["clouds"]["materialised"] == len(a0["cloud_mass"]) and h2["clouds"]["materialised"] == len(a2["cloud_mass"])
    # The level-2 clouds are a subset of the level-0 cells' clouds (by mass, a continuous column).
    assert set(np.round(a2["cloud_mass"], 6).tolist()) <= set(np.round(a0["cloud_mass"], 6).tolist())
    assert 0 < len(a2["cloud_mass"]) < len(a0["cloud_mass"])
    # A census: no stars= parameter changes it; twice the same rows (the header's `stages` differs
    # between a cold and a cached call, as it does for the star route).
    again = svc.handle("/api/clouds", "r_min=7&r_max=9&phi_min=0&phi_max=0.4")
    ha, aa = wire.decode(again.body)
    assert {k: v for k, v in ha.items() if k != "stages"} == {k: v for k, v in h0.items() if k != "stages"}
    assert all(np.array_equal(aa[k], a0[k], equal_nan=True) for k in a0)
    assert "cloud_state" in h0["columns"] and "cloud_mach_number" in h0["columns"]
