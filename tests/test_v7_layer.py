"""The layer in the march on the frame's pixels (S66, BUILD_III Phase V7; DECISIONS.md D226, RULING_S66 R2b, R5d; review
M3 and N1): what the viewer's march multiplies (read once per ray at its midplane crossing: face-on, the pixel itself),
evaluated with the model's own reference evaluators on the capture's own pixel lattice, ring by level-0 ring.

The maps' unit mean holds per level-0 cell on the model's quadrature lattice (gas_fluctuation's normalisers, the
clustering field's table lattice); on a frame's pixels the march point-samples the map, one value per pixel with no
footprint average, so a ring's mean on the pixels departs from 1 by one draw of a log-normal's sample mean (N1). Each
per-ring statement is that draw's bound, **derived, not chosen**:

    s_r = sqrt((exp(v) - 1) / N_eff),   N_eff = N_r / g^2,   pinned |mean_r - 1| <= 3 s_r

for every ring, template and lattice offset. N_r is the ring's pixels in the frame, v the map's log variance and g its
grain in pixels: the finest octave's lattice cell over the pixel, at least 1 (two pixels inside one cell of the
finest octave are one draw of it). The gas fluctuation map: v = sigma_r^2 sum_j w_j^2 (the ring's own width, the ladder's
weights for its break index: GasFluctuationField.amplitudes, unit variance), finest octave scale / 2^5 = 5.9 pc - under
every pixel here, so g = 1. The clustering field's k-octave map (k = 3 the young light's, k = 3, 2, 1 the middle part's
kept shares): v = sigma^2 norm^2 sum_(j < k) a_j^2 (noise.fractal_coarsest: a truncated sum keeps its octaves' share of
the unit variance, top on the last octave only when k = octaves), finest octave scale / 2^(k - 1) = 47.5, 95, 190 pc,
so g = 1.22, 2.43, 4.86 on the Milky Way's pixel and 1.62, 3.24, 6.49 on NGC 4414's. The weights the means carry
(the placement) are not in N_r: the bound is the unweighted one.

- R2b, the dust's column: per level-0 ring inside the dust's disc, sum(place m) / sum(place) - 1, ``place`` the
  placement the march reads at the pixel - the unspurred placement read bilinearly, times one less the spurs' ring
  mean, plus the spurs' sum at the pixel (stages/spurs.Spurs.at; the Milky Way's 48 rows, none on NGC 4414) - and ``m``
  the gas fluctuation map (gas_fluctuation.GasFluctuationField.evaluate); and over the whole frame within 3e-3 (the
  picture test's DUST_COLUMN_TOLERANCE).
- R5d, the clustered light: per level-0 ring, the young part's light (its ring light times dust_placement, read
  bilinearly as the march reads its texture) times m_3 / cell_mean_3 over the same without; each of the middle part's
  kept shares (times stars_middle_placement) times m_k / cell_mean_k (the maps census_clustering.ClusteringField.maps,
  the means /api/layer's census_clustering.cell_mean - the render header's until S73).
- the 3-octave map's pixel mean per level-0 cell over the header's cell mean (the lattice's sanity).

The lattice: the `<template>-field` capture's own (frontend/e2e/captures.json): `viewport` square pixels over twice the
camera's radius_kpc - 2 x 20 / 1024 = 39.0625 pc on the Milky Way, 2 x 15 / 1024 = 29.297 pc on NGC 4414 - centred,
pixel centres at (k + 1/2 + o) times the pixel from the centre (k = -512..511 the frame, continued to the last ring), at the
16 offsets o = 0, 1/4, 1/2, 3/4 in x and in y (a turn of the picture by a multiple of 90 degrees maps the set onto
itself), face-on; x = R cos phi and y = R sin phi with phi the render grid's azimuth. Both are evaluated face-on: the NGC 4414 frame's own inclination
(55 degrees) is not evaluated here. The march itself reads its textures at half that resolution; the frame's own gate
is the picture test's (e2e/settings.ts DUST_COLUMN_TOLERANCE).

MEASURED when written (S66 fix pass; the worst |mean_r - 1| / s_r over the 16 offsets, its ring and offset, and the
largest |mean_r - 1| on any ring): the dust's column, Milky Way 2.93 on ring 2 at (1/4, 1/4) (-1.64e-2 against s_r
5.59e-3), largest 3.13e-2 (ring 0, s_r 1.21e-2); NGC 4414 2.33 on ring 0 at (1/2, 1/2) (-2.12e-2, s_r 9.09e-3); the whole
frame within 3.9e-4 and 9.2e-4. The young light, Milky Way 2.35 on ring 25 (largest 9.32e-2), NGC 4414 0.79 (4.30e-2);
kept 3 2.24 (6.86e-2) and 1.53 (5.73e-2); kept 2 1.26 (4.65e-2) and 1.51 (3.91e-2); kept 1 0.53 (4.53e-2) and 1.30
(3.65e-2). The review's numbers (019c0d8's test lattice and the capture's): the dust's column on ring 0 1.25e-2 on a
39.000 pc lattice, 1.81e-2 on the capture's pixel, 2.54e-2 a quarter pixel off; the young light 7.6e-2 to 9.3e-2.

Two parts make the per-ring departure, both one draw of the map in the ring's cells. The point sampling of a
log-normal at the pixel scale, with no footprint average (review N1): on the Milky Way's ring 2 the unweighted pixel
mean departs -9.3e-3 at the capture's pixel and 1e-5 at a quarter of it. And the placement's alignment with the map
inside a cell (builder B's class): weighted by the placement, ring 2 still departs -8.0e-3 at a quarter pixel and
ring 0 -1.5e-2 (unweighted -3.2e-3) - which a finer lattice does not remove. The bound counts N_r, not the weight's
effective number (1 402 of ring 0's 1 946 pixels, 3 209 of ring 2's 9 146), so it is the stricter of the two. The
lattice is continued past the frame's edge so that every ring is whole: a ring the frame cuts (beyond 20 kpc on the
Milky Way) is a partial cell's mean, which no sampling bound describes - ring 22 on the frame alone departed -5e-3 to
-7.6e-3 at every offset and -6.1e-3 at a quarter pixel.

Debt #176 carries the numbers; its mend for the sampling part is a footprint average of the map over the pixel.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.layer import gas_fluctuation as gf
from galaxy.layer.census_clustering import ClusteringField
from galaxy.stages.spurs import Spurs
from galaxy.stages.systems import CELL_SECTORS

ROOT = Path(__file__).resolve().parents[1]
FILTERS = json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))
CAPTURES = json.loads((ROOT / "frontend" / "e2e" / "captures.json").read_text(encoding="utf-8"))["captures"]
TEMPLATES = ("milky_way", "ngc_4414")
OFFSETS = tuple((ox, oy) for ox in (0.0, 0.25, 0.5, 0.75) for oy in (0.0, 0.25, 0.5, 0.75))
DRAWS = 3.0  # the pin: |mean_r - 1| <= 3 s_r, s_r the derived one-draw scatter
WHOLE_FRAME = 3e-3  # the dust's column over the whole frame: the picture test's DUST_COLUMN_TOLERANCE
G = 1  # the rgb set's G channel: the light's weight in a ring (the maps do not depend on the channel)


def _constants() -> dict:
    from galaxy.core.registry import production
    from galaxy.models import DEFAULT

    models, _, _ = production()
    model = models.get(DEFAULT) if isinstance(DEFAULT, str) else DEFAULT
    return {k: c.value for k, c in model.constants.items()}


def capture(template: str) -> tuple[float, int]:
    """The `<template>-field` capture's pixel (kpc) and its pixels across: twice the camera's radius over the viewport."""
    c = next(c for c in CAPTURES if c["name"] == f"{template}-field")
    return 2.0 * float(c["camera"]["radius_kpc"]) / int(c["viewport"]), int(c["viewport"])


def bilinear(table: np.ndarray, R: np.ndarray, r: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """The march's LinearFilter read of an (R, phi) texture: texel centres, R clamped to the edge, phi wrapped."""
    n_r, n_p = table.shape
    u = np.clip((r - R[0]) / (R[1] - R[0]), 0, n_r - 1)
    v = phi / (2 * np.pi / n_p) - 0.5
    i0 = np.floor(u).astype(int)
    i1 = np.minimum(i0 + 1, n_r - 1)
    fu = u - i0
    j0 = np.floor(v).astype(int)
    fv = v - j0
    j1 = (j0 + 1) % n_p
    j0 = j0 % n_p
    return (1 - fu) * ((1 - fv) * table[i0, j0] + fv * table[i0, j1]) + fu * ((1 - fv) * table[i1, j0] + fv * table[i1, j1])


def per_ring(ring: np.ndarray, weight: np.ndarray, modulated: np.ndarray, rings: np.ndarray) -> np.ndarray:
    """sum(weight modulated) / sum(weight) - 1 over each of ``rings``' pixels."""
    w0 = np.bincount(ring, weight, 32)
    w1 = np.bincount(ring, weight * modulated, 32)
    return w1[rings] / w0[rings] - 1.0


def one_draw(log_variance: np.ndarray | float, grain: float, pixels: np.ndarray) -> np.ndarray:
    """The derived scatter of a log-normal map's mean over a ring's point samples: sqrt((e^v - 1) g^2 / N_r)."""
    return np.sqrt(np.expm1(log_variance) * max(1.0, grain) ** 2 / pixels)


def lattice(f: dict, ox: float, oy: float) -> dict:
    """The capture's pixel centres at offset (ox, oy) pixels, continued past the frame's edge so that every level-0
    ring is whole: positions, rings and cells."""
    pixel, edges = f["pixel"], f["gas"].edges
    k = np.arange(-math.ceil(edges[-1] / pixel) - 1, math.ceil(edges[-1] / pixel) + 1)  # past the frame: every ring whole
    X, Y = np.meshgrid((k + 0.5 + ox) * pixel, (k + 0.5 + oy) * pixel)
    r = np.hypot(X, Y)
    keep = (r >= edges[0]) & (r < edges[-1])
    x, y, r = X[keep], Y[keep], r[keep]
    phi = np.mod(np.arctan2(y, x), 2 * np.pi)
    ring = f["gas"].ring_of(r)
    sector = np.clip(np.floor(phi / (2 * np.pi / CELL_SECTORS)).astype(int), 0, CELL_SECTORS - 1)
    return {"x": x, "y": y, "r": r, "phi": phi, "ring": ring, "cell": ring * CELL_SECTORS + sector,
            "pixels": np.bincount(ring, None, 32)}


@pytest.fixture(scope="module")
def frames() -> dict:
    """Per template: the render (layer on, rgb), the reference evaluators from its header, the capture's pixel, and
    each map's log variance and grain (the module docstring's derivation)."""
    api = Service(cache=2)
    C = _constants()
    out = {}
    for template in TEMPLATES:
        got = api.handle("/api/render", {"template": [template], "filters": [json.dumps(FILTERS["sets"]["rgb"]["curves"])]})
        assert got.status == 200, got.body[:300]
        header, arrays = wire.decode(got.body)
        win = header["window"]["R"]
        R = win["lo"] + (np.arange(win["n"]) + 0.5) * win["width"]
        # The layer's tables: /api/layer's since S73 (#199), the render header's until then - the same entries.
        layer = api.handle("/api/layer", {"template": [template]})
        assert layer.status == 200, layer.body[:300]
        tables = layer.json()
        g = tables["gas_fluctuation"]
        params = {"edges": np.asarray(g["edges"], float), "sense": float(g["sense"]),
                  **{k: np.asarray(g["ring"][k], float) for k in ("break_octave", "sigma", "strain", "twist")}}
        gas = gf.field_of(int(g["seed"]), params, C, np.asarray(g["cell_normaliser"], float))
        rows = tables["spurs"]["rows"]
        spurs = Spurs(rows["radius"], rows["azimuth"], rows["contrast"], rows["pitch"], rows["length"], rows["width"],
                      rows["fall"], float(tables["spurs"]["turn"])) if rows and rows["radius"] else None
        clustering = ClusteringField.of(tables["census_clustering"]["seed"], C)
        pixel, _ = capture(template)
        weights = gas.amplitudes()
        gas_v = gas.sigma ** 2 * np.sum(weights[gas.break_octave.astype(int)] ** 2, axis=1)
        gas_grain = gas.scale / 2 ** (gas.octaves - 1) / pixel  # every ladder row weights every octave
        gain, top, norm = clustering.weights()
        a2 = gain ** (2 * np.arange(clustering.octaves))
        a2[-1] *= top ** 2
        clump_v = {k: clustering.sigma ** 2 * norm ** 2 * float(a2[:k].sum()) for k in (1, 2, 3)}
        clump_grain = {k: clustering.scale / 2 ** (k - 1) / pixel for k in (1, 2, 3)}
        out[template] = {"header": header, "tables": tables, "arrays": arrays, "R": R, "gas": gas, "spurs": spurs, "clustering": clustering,
                         "pixel": pixel, "gas_v": gas_v, "gas_grain": gas_grain, "clump_v": clump_v,
                         "clump_grain": clump_grain}
    return out


def dust_column(f: dict, p: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """R2b at one offset: (rings, departure per ring, one-draw scatter per ring, the whole frame's departure)."""
    a, R = f["arrays"], f["R"]
    share = np.asarray(f["tables"]["spurs"]["share"], float)
    place = bilinear(np.asarray(a["dust_placement_unspurred"], float).reshape(R.size, -1), R, p["r"], p["phi"])
    if f["spurs"] is not None:
        place = (1.0 - np.interp(p["r"], R, share)) * place + f["spurs"].at(p["r"], p["phi"])
    else:  # no spurs: the unspurred placement is the placement to the bit (builder A's closure)
        assert np.array_equal(np.asarray(a["dust_placement_unspurred"]), np.asarray(a["dust_placement"]))
    m = f["gas"].evaluate(p["x"], p["y"])
    h = np.asarray(a["dust_height"], float)
    disc = float(R[np.flatnonzero(np.isfinite(h) & (h > 0))[-1]])
    dusty = np.arange(32)[(f["gas"].edges[1:] <= disc) & (p["pixels"] > 0)]
    inside = np.isin(p["ring"], dusty)
    whole = float(np.sum(place[inside] * m[inside]) / np.sum(place[inside]) - 1.0)
    dev = per_ring(p["ring"], place, m, dusty)
    return dusty, dev, one_draw(f["gas_v"][dusty], f["gas_grain"], p["pixels"][dusty]), whole


def clustered_light(f: dict, p: dict) -> dict:
    """R5d at one offset: per part the march clusters - the young part (its ring light times dust_placement) and the
    middle part's kept shares (times its weight, stars_middle_placement), each read bilinearly as the march reads its
    clump texture - (rings, departure per ring with its k-octave map over its cell mean, one-draw scatter per ring)."""
    a, h, R = f["arrays"], f["header"], f["R"]
    phi_n = np.asarray(a["dust_placement"]).size // R.size
    means = {int(k): np.asarray(v, float) for k, v in f["tables"]["census_clustering"]["cell_mean"].items()}
    maps = dict(zip((1, 2, 3), f["clustering"].maps(p["x"], p["y"], (1, 2, 3))))
    kept = h["ages"]["middle_kept"]
    middle_weight = np.asarray(a[kept["weight"]], float).reshape(R.size, phi_n)
    parts = {"young": (np.asarray(a["stars_young"], float).reshape(R.size, -1)[:, G],
                       np.asarray(a["dust_placement"], float).reshape(R.size, phi_n), 3)}
    for k in (3, 2, 1):
        parts[f"kept{k}"] = (np.asarray(a[kept["arrays"][str(k)]], float).reshape(R.size, -1)[:, G], middle_weight, k)
    out = {}
    for name, (light, weight, k) in parts.items():
        w = bilinear(light[:, None] * weight, R, p["r"], p["phi"])
        lit = np.flatnonzero(np.bincount(p["ring"], w, 32) > 0)
        dev = per_ring(p["ring"], w, maps[k] / means[k][p["cell"]], lit)
        out[name] = (lit, dev, one_draw(f["clump_v"][k], f["clump_grain"][k], p["pixels"][lit]))
    return out


@pytest.fixture(scope="module")
def sweeps(frames) -> dict:
    """Every offset's departures, per template: the dust's column and the clustered parts."""
    out = {}
    for template, f in frames.items():
        rows = []
        for ox, oy in OFFSETS:
            p = lattice(f, ox, oy)
            rows.append(((ox, oy), dust_column(f, p), clustered_light(f, p)))
        out[template] = rows
    return out


def worst(entries) -> tuple[float, int, tuple, float, float]:
    """Over (offset, rings, departure, scatter) entries: the largest |departure| / scatter, its ring, its offset, and
    the departure and scatter there."""
    best = (-1.0, -1, (0, 0), 0.0, 0.0)
    for off, rings, dev, s in entries:
        ratio = np.abs(dev) / s
        i = int(np.argmax(ratio))
        if ratio[i] > best[0]:
            best = (float(ratio[i]), int(rings[i]), off, float(dev[i]), float(s[i]))
    return best


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_dust_s_column_per_level_0_ring_is_kept_by_the_gas_map_within_its_one_draw_bound(sweeps, template):
    """R2b on the capture's lattice at 16 offsets: every dusty ring within 3 s_r (the module docstring), and the whole
    frame within 3e-3. The measured numbers are the module docstring's MEASURED."""
    rows = sweeps[template]
    ratio, ring, off, dev, s = worst((o, d[0], d[1], d[2]) for o, d, _ in rows)
    raw = max(float(np.abs(d[1]).max()) for _, d, _ in rows)
    whole = max(abs(d[3]) for _, d, _ in rows)
    print(f"{template}: dust column, worst |dev| / s_r {ratio:.3f} on ring {ring} at offset {off} "
          f"(dev {dev:+.3e}, s_r {s:.3e}); worst |dev| any ring {raw:.3e}; whole frame worst {whole:.3e}")
    assert ratio <= DRAWS, (ring, off, dev, s)
    assert whole < WHOLE_FRAME


@pytest.mark.parametrize("template", TEMPLATES)
def test_every_clustered_part_s_light_per_level_0_ring_is_kept_by_its_map_within_its_one_draw_bound(sweeps, template):
    """R5d on the capture's lattice at 16 offsets: the young light (times m_3 / cell_mean_3) and each of the middle
    part's kept shares (times m_k / cell_mean_k), every lit ring within 3 s_r of its k-octave map (the module
    docstring). The measured numbers are the module docstring's MEASURED."""
    rows = sweeps[template]
    failed = []
    for name in ("young", "kept3", "kept2", "kept1"):
        ratio, ring, off, dev, s = worst((o, *c[name]) for o, _, c in rows)
        raw = max(float(np.abs(c[name][1]).max()) for _, _, c in rows)
        print(f"{template}: {name}, worst |dev| / s_r {ratio:.3f} on ring {ring} at offset {off} "
              f"(dev {dev:+.3e}, s_r {s:.3e}); worst |dev| any ring {raw:.3e}")
        if ratio > DRAWS:
            failed.append((name, ring, off, dev, s))
    assert not failed, failed


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_3_octave_map_s_pixel_mean_per_cell_is_near_the_header_s_cell_mean(frames, template):
    """The lattice's sanity: the 3-octave map's mean over each level-0 cell's pixels over the header's cell mean (the
    published census_clustering_cell_mean, on the field's table lattice), on the capture's lattice at offset 0. Each
    cell's pixel count is in the hundreds to the thousands, so the per-cell scatter is the map's own (sigma 1.75), not a
    bias. Written at: per ring worst 1.87e-2 (Milky Way), 1.09e-2 (NGC 4414); per cell rms 3.8e-2 / 2.3e-2.
    Held under 6e-2, the probe's 5.0e-2 worst on its own 4-point lattice."""
    f = frames[template]
    p = lattice(f, 0.0, 0.0)
    mean3 = np.asarray(f["tables"]["census_clustering"]["cell_mean"]["3"], float)
    m3 = f["clustering"].maps(p["x"], p["y"], (3,))[0]
    count = np.bincount(p["cell"], None, 1024)
    seen = count > 0
    cell = np.bincount(p["cell"], m3, 1024)[seen] / count[seen] / mean3[seen] - 1.0
    ring = np.bincount(p["ring"], m3 / mean3[p["cell"]], 32)[p["pixels"] > 0] / p["pixels"][p["pixels"] > 0] - 1.0
    print(f"{template}: 3-octave map's pixel mean over the cell mean - 1: per cell rms {np.sqrt(np.mean(cell ** 2)):.3e} "
          f"worst {np.abs(cell).max():.3e}; per ring worst {np.abs(ring).max():.3e}")
    assert np.abs(ring).max() < 6e-2
