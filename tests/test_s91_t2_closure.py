"""S91 (BUILD_V row 91, batch M3; T2 / #114): the points painted through the filter set - the closure T2's row names.

T2's row (docs/VIEWER_TASKS.md) asks that the census summed through a filter set equal the render's ``stars`` over the
same cells. The published answers close it as S48's identity does - per ring and over the disc, not per cell: the
render's three parts (``stars_young``, the cluster census's ages; the bright catalogue's part above ``l_min``; the
remainder ``stars_unresolved``) are expectations, exact per ring (``tests/test_v6_bright.py``,
``tests/test_v6b_points.py``), while the cluster census and the bright catalogue are realisations of them. Measured at
S91 on the Milky Way through rgb at 6500 K (``scratch_s91_t2/measure_closure.py`` in the builder's worktree), at the
grid threshold where the whole disc expects at most 3 x 10^4 bright stars (10^4.20 Lsun, 24 070 returned), with the
census's 12 989 clusters:

* clusters + bright + remainder over ``stars``: the disc 0.9959 / 0.9947 / 0.9910 (R / G / B); per ring (the 26 rings
  holding over 1 % of the brightest ring's light) 0.927-1.099; per level-0 cell p05-p95 0.77-1.26 (median 0.96-0.97),
  and over the 16 level-2 children of cell 261 (R 7.5-8.5 kpc) 0.88-1.01 per cell, 0.905 / 0.881 / 0.818 summed - that
  cell's ten clusters carry 0.18 of its expected young light. Not claimed per cell.
* the clusters alone over the young part: the disc 0.9398 / 0.9380 / 0.9327, per ring 0.66-1.45; bolometrically the
  census's light over the young part's 0.9318. Through the set over bolometric, 1.0086 / 1.0066 / 1.0010: the census's
  response is the young part's colour to 1 %, and its 6 % shortfall is the census's draw against its expectation (the
  clusters' light's seed-to-seed spread is 4.4 %, D210), not the filter path.
* the drawn path (``frontend/src/galaxy/GalaxyTab.tsx``, the region regime's "sampled" cluster points): before S91,
  ``lightColors`` (L_bol x the blackbody share at the light temperature, through /api/blackbody's table as
  ``colors.ts channelShare`` reads it) summed over the census is 1.8352 / 2.0703 / 2.4222 times its summed response over
  the white point's - ``tests/test_v4.py``'s 1.847 / 2.085 / 2.436 on the coarse grid; since S91 ``responseColors`` draws
  the response over the white point's, 1 by construction (``colors.test.ts``).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.stages import systems as sy

ROOT = Path(__file__).resolve().parents[1]
RGB = json.dumps(json.loads((ROOT / "frontend/src/galaxy/filters.json").read_text(encoding="utf-8"))["sets"]["rgb"]["curves"])
WHITE = 6500
BUDGET = 3.0e4  # the whole disc's expected bright stars at the threshold picked
DISC = {"r_min": "0", "r_max": "1000", "phi_min": "0", "phi_max": repr(2 * math.pi)}


def ask(service: Service, path: str, **q):
    r = service.handle(path, {k: [str(v)] for k, v in q.items()})
    assert r.status == 200, r.body[:400]
    return wire.decode(r.body)


def ring(a: np.ndarray) -> np.ndarray:
    return a.reshape(sy.CELL_RINGS, sy.CELL_SECTORS, -1).sum(axis=1)


@pytest.fixture(scope="module")
def parts():
    """Per level-0 cell and filter, Lsun: the render's stars, its remainder at l_min and its young part placed; the
    cluster census's summed response; the bright catalogue's at l_min. And the census's and the render's bolometric
    young light, and the census's own columns."""
    service = Service(cache=4)
    _, table = ask(service, "/api/bright", template="milky_way", table=1)
    k = next(j for j in range(table["threshold"].size) if table["expected"][:, j].sum() <= BUDGET)
    l_min = repr(float(table["threshold"][k]))
    rh, ra = ask(service, "/api/render", template="milky_way", filters=RGB, white=WHITE, level=0, l_min=l_min, **DISC)
    R = service.grid.R
    cell = np.asarray(ra["cell"])
    order = np.argsort(cell)
    assert np.array_equal(cell[order], np.arange(sy.CELL_COUNT))
    bounds = [sy.cell_bounds(R, int(c), 0) for c in cell]
    area = np.array([0.5 * (b["r_hi"] ** 2 - b["r_lo"] ** 2) * (b["phi_hi"] - b["phi_lo"]) for b in bounds]) * 1e6  # pc²
    weight = rh["ages"]["parts"]["young"]["weight"]
    young = np.asarray(ra["stars_young"], dtype=float) * np.asarray(ra[weight], dtype=float)[:, None]
    out = {name: (np.asarray(v, dtype=float) * area[:, None])[order]
           for name, v in (("stars", ra["stars"]), ("remainder", ra["stars_unresolved"]), ("young", young))}
    ch, ca = ask(service, "/api/clusters", template="milky_way", filters=RGB, white=WHITE, **DISC)
    response = np.asarray(ca["response"], dtype=float)
    out["clusters"] = np.zeros_like(out["stars"])
    np.add.at(out["clusters"], np.asarray(ca["cell"]), response)  # the census's cell column is the level-0 cell
    bh, ba = ask(service, "/api/bright", template="milky_way", cells=",".join(map(str, range(sy.CELL_COUNT))), l_min=l_min,
                 filters=RGB, white=WHITE)
    level = int(bh["cells"]["level"])  # the catalogue names its stars by their finest cell
    out["bright"] = np.zeros_like(out["stars"])
    np.add.at(out["bright"], np.asarray(ba["cell"]) // sy.children_per_cell(level),
              np.asarray(ba["response"], dtype=float).reshape(-1, response.shape[1]))
    bb = service.handle("/api/blackbody", {"filters": [RGB], "white": [str(WHITE)]}).json()
    return {**out, "young_light": float(rh["resolved"]["light"]["young"]), "census": ca, "white": ch["white"]["response"],
            "blackbody": bb}


def test_the_census_the_catalogue_and_the_remainder_close_on_the_render_s_stars_over_the_disc_and_per_ring(parts):
    """T2's closure as the published answers support it: per ring and over the disc, the realised points plus the
    remainder against ``stars`` (measured 0.9959 / 0.9947 / 0.9910 over the disc, 0.927-1.099 per lit ring). The
    bounds are the census's: the clusters hold about a quarter of the light and their summed light has a 4.4 %
    seed-to-seed spread over the disc, tens of per cent per ring (a ring's light rides on its few most massive
    clusters). Per cell nothing is claimed (p05-p95 0.77-1.26)."""
    points = parts["clusters"] + parts["bright"] + parts["remainder"]
    whole = points.sum(axis=0) / parts["stars"].sum(axis=0)
    assert np.all(np.abs(whole - 1.0) < 0.02), whole
    lit = ring(parts["stars"])[:, 1] > 0.01 * ring(parts["stars"])[:, 1].max()
    assert lit.sum() >= 24
    per_ring = ring(points)[lit] / ring(parts["stars"])[lit]
    assert np.all(np.abs(per_ring - 1.0) < 0.15), per_ring
    # the bright catalogue against its expected part, the render's stars less its young part and its remainder
    expected = parts["stars"] - parts["young"] - parts["remainder"]
    bright = parts["bright"].sum(axis=0) / expected.sum(axis=0)
    assert np.all(np.abs(bright - 1.0) < 0.03), bright  # measured 1.0027 / 1.0091 / 1.0148 (24 070 stars)


def test_the_clusters_summed_response_is_the_young_part_s_colour(parts):
    """The clusters alone against the render's young part (the census's ages): through the set the disc reads 0.9398 /
    0.9380 / 0.9327, bolometrically 0.9318 - so the response the region regime now draws is the young part's colour to
    1 % (1.0086 / 1.0066 / 1.0010), and the shortfall is the census's draw against its expectation, the same in every
    channel and in the bolometric light (the clusters' light's seed-to-seed spread is 4.4 %, D210)."""
    through = parts["clusters"].sum(axis=0) / parts["young"].sum(axis=0)
    bolometric = float(np.sum(parts["census"]["cluster_luminosity"])) / parts["young_light"]
    assert 0.85 < bolometric < 1.10, bolometric
    assert np.all(np.abs(through / bolometric - 1.0) < 0.02), through / bolometric


def test_the_region_regime_s_old_painting_was_the_census_s_factor_of_two(parts):
    """The drawn path before S91: ``lightColors`` - each cluster's L_bol times /api/blackbody's share at its light
    temperature over the white point's, read as ``colors.ts channelShare`` reads the table (log share linear in log T,
    clamped) - summed over the census, over the census's summed response over the white point's: 1.8352 / 2.0703 /
    2.4222 on the default grid (``tests/test_v4.py`` pins 1.847 / 2.085 / 2.436 on the coarse one). Since S91 the region
    regime draws ``responseColors``, the response over the white point's, whose ratio is 1 by construction
    (``frontend/src/galaxy/colors.test.ts``)."""
    bb = parts["blackbody"]
    logk = np.log10(np.asarray(bb["kelvin"], dtype=float))
    share = np.asarray(bb["share"], dtype=float)
    white = np.asarray(bb["white"]["response"], dtype=float)
    c = parts["census"]
    L = np.asarray(c["cluster_luminosity"], dtype=float)
    x = np.clip(np.log10(np.asarray(c["cluster_light_temperature"], dtype=float)), logk[0], logk[-1])
    i = np.clip(np.searchsorted(logk, x, side="right") - 1, 0, logk.size - 2)
    f = ((x - logk[i]) / (logk[i + 1] - logk[i]))[:, None]
    a, b = share[i], share[i + 1]
    pos = (a > 0) & (b > 0)
    s = np.where(pos, a * np.where(pos, b / np.where(pos, a, 1.0), 1.0) ** f, a + (b - a) * f)
    painted = (L[:, None] * s[:, :3] / white[:3]).sum(axis=0)
    own = (np.asarray(c["response"], dtype=float)[:, :3] / np.asarray(parts["white"], dtype=float)[:3]).sum(axis=0)
    assert np.asarray(parts["white"], dtype=float)[:3] == pytest.approx(white[:3], rel=1e-12)
    assert painted / own == pytest.approx([1.8352, 2.0703, 2.4222], rel=2e-2), painted / own
