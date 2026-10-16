"""The layer in the march on the frame's pixels (S66, BUILD_III Phase V7; DECISIONS.md D226, RULING_S66 R2b, R5d): what
the viewer's march multiplies (read once per ray at its midplane crossing: face-on, the pixel itself), evaluated with the model's own reference evaluators on a face-on frame's
pixel lattice, ring by level-0 ring.

The maps' unit mean holds per level-0 cell on the model's quadrature lattice (gas_fluctuation's normalisers, the
clustering field's table lattice); on a frame's pixels it holds only to the lattice's sampling, so each statement here
is a **sampling tolerance**, declared with the number measured when it was written:

- R2b, the dust's column: per level-0 ring inside the dust's disc, sum(place m) / sum(place) - 1, ``place`` the
  placement the march reads at the pixel - the unspurred placement read bilinearly, times one less the spurs' ring
  mean, plus the spurs' sum at the pixel (stages/spurs.Spurs.at; the Milky Way's 48 rows, none on NGC 4414) - and ``m``
  the gas fluctuation map (gas_fluctuation.GasFluctuationField.evaluate), within 1.5e-2.
- R5d, the clustered light: per level-0 ring, the young part's light (its ring light times dust_placement, read
  bilinearly as the march reads its texture) times m_3 / cell_mean_3 over the same without; each of the middle part's
  kept shares (times stars_middle_placement) times m_k / cell_mean_k, every one within 5e-2 (R5d as amended; the
  maps census_clustering.ClusteringField.maps, the means the render header's census_clustering.cell_mean).
- the 3-octave map's pixel mean per level-0 cell over the header's cell mean (the lattice's sanity).

The lattice: square pixels of a 1024-pixel frame face-on, 39 pc on the Milky Way (its 40 kpc frame) and 28 pc on NGC
4414 (the probe's, REPORT_PROBE D), pixel centres at (k + 1/2) times the pixel from the centre, x = R cos phi and
y = R sin phi with phi the render grid's azimuth. The march itself reads at half that resolution; the frame's own gate
is the picture test's (e2e/settings.ts DUST_COLUMN_TOLERANCE).
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
PIXEL_KPC = {"milky_way": 0.039, "ngc_4414": 0.028}
DUST_COLUMN = 1.5e-2  # R2b
CLUSTERED_LIGHT = 5e-2  # R5d as amended: every clustered part, young and kept
G = 1  # the rgb set's G channel: the light's weight in a ring (the maps do not depend on the channel)


def _constants() -> dict:
    from galaxy.core.registry import production
    from galaxy.models import DEFAULT

    models, _, _ = production()
    model = models.get(DEFAULT) if isinstance(DEFAULT, str) else DEFAULT
    return {k: c.value for k, c in model.constants.items()}


@pytest.fixture(scope="module")
def frames() -> dict:
    """Per template: the render (layer on, rgb), the reference evaluators from its header, and the pixel lattice."""
    api = Service(cache=2)
    C = _constants()
    out = {}
    for template, pixel in PIXEL_KPC.items():
        got = api.handle("/api/render", {"template": [template], "filters": [json.dumps(FILTERS["sets"]["rgb"]["curves"])]})
        assert got.status == 200, got.body[:300]
        header, arrays = wire.decode(got.body)
        win = header["window"]["R"]
        R = win["lo"] + (np.arange(win["n"]) + 0.5) * win["width"]
        g = header["gas_fluctuation"]
        params = {"edges": np.asarray(g["edges"], float), "sense": float(g["sense"]),
                  **{k: np.asarray(g["ring"][k], float) for k in ("break_octave", "sigma", "strain", "twist")}}
        gas = gf.field_of(int(g["seed"]), params, C, np.asarray(g["cell_normaliser"], float))
        rows = header["spurs"]["rows"]
        spurs = Spurs(rows["radius"], rows["azimuth"], rows["contrast"], rows["pitch"], rows["length"], rows["width"],
                      rows["fall"], float(header["spurs"]["turn"])) if rows and rows["radius"] else None
        clustering = ClusteringField.of(header["census_clustering"]["seed"], C)
        edges = gas.edges
        n = int(math.ceil(edges[-1] / pixel))
        ax = (np.arange(-n, n) + 0.5) * pixel
        X, Y = np.meshgrid(ax, ax)
        r = np.hypot(X, Y)
        keep = (r >= edges[0]) & (r < edges[-1])
        x, y, r = X[keep], Y[keep], r[keep]
        phi = np.mod(np.arctan2(y, x), 2 * np.pi)
        ring = gas.ring_of(r)
        sector = np.clip(np.floor(phi / (2 * np.pi / CELL_SECTORS)).astype(int), 0, CELL_SECTORS - 1)
        out[template] = {"header": header, "arrays": arrays, "R": R, "gas": gas, "spurs": spurs, "clustering": clustering,
                         "x": x, "y": y, "r": r, "phi": phi, "ring": ring, "cell": ring * CELL_SECTORS + sector}
    return out


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


@pytest.mark.parametrize("template", list(PIXEL_KPC))
def test_the_dust_s_column_per_level_0_ring_is_kept_by_the_gas_map_on_the_frame_s_pixels(frames, template):
    """R2b, a sampling tolerance of 1.5e-2. Written at: Milky Way worst 1.22e-2 (rms 3.5e-3), NGC 4414 worst 6.3e-3
    (rms 2.0e-3) - the probe's 1.2e-2 / 6.3e-3 with the cell-mean placement, the spurs per pixel moving them little."""
    f = frames[template]
    a, R = f["arrays"], f["R"]
    shape = (R.size, -1)
    share = np.asarray(f["header"]["spurs"]["share"], float)
    place = bilinear(np.asarray(a["dust_placement_unspurred"], float).reshape(shape), R, f["r"], f["phi"])
    if f["spurs"] is not None:
        place = (1.0 - np.interp(f["r"], R, share)) * place + f["spurs"].at(f["r"], f["phi"])
    else:  # no spurs: the unspurred placement is the placement to the bit (builder A's closure)
        assert np.array_equal(np.asarray(a["dust_placement_unspurred"]), np.asarray(a["dust_placement"]))
    m = f["gas"].evaluate(f["x"], f["y"])
    h = np.asarray(a["dust_height"], float)
    disc = float(R[np.flatnonzero(np.isfinite(h) & (h > 0))[-1]])
    dusty = np.arange(32)[f["gas"].edges[1:] <= disc]
    dev = per_ring(f["ring"], place, m, dusty)
    print(f"{template}: dust column per level-0 ring (place m / place - 1), {dusty.size} rings, {f['x'].size} px: "
          f"worst {np.abs(dev).max():.3e} (ring {dusty[np.abs(dev).argmax()]}), rms {np.sqrt(np.mean(dev ** 2)):.3e}")
    assert np.all(np.abs(dev) < DUST_COLUMN), dev


def light_per_ring(f: dict) -> dict:
    """Per share the march clusters - the young part (its ring light times dust_placement) and the middle part's kept
    shares (times its weight, stars_middle_placement), each read bilinearly as the march reads its clump texture - the
    light per level-0 ring with its k-octave map over its cell mean, over the same without, minus 1: (worst, rms)."""
    a, h, R = f["arrays"], f["header"], f["R"]
    phi_n = np.asarray(a["dust_placement"]).size // R.size
    means = {int(k): np.asarray(v, float) for k, v in h["census_clustering"]["cell_mean"].items()}
    maps = dict(zip((1, 2, 3), f["clustering"].maps(f["x"], f["y"], (1, 2, 3))))
    ratio = {k: maps[k] / means[k][f["cell"]] for k in (1, 2, 3)}
    kept = h["ages"]["middle_kept"]
    middle_weight = np.asarray(a[kept["weight"]], float).reshape(R.size, phi_n)
    parts = {"young": (np.asarray(a["stars_young"], float).reshape(R.size, -1)[:, G], np.asarray(a["dust_placement"], float).reshape(R.size, phi_n), 3)}
    for k in (3, 2, 1):
        parts[f"kept{k}"] = (np.asarray(a[kept["arrays"][str(k)]], float).reshape(R.size, -1)[:, G], middle_weight, k)
    worst = {}
    for name, (light, weight, k) in parts.items():
        w = bilinear(light[:, None] * weight, R, f["r"], f["phi"])
        lit = np.flatnonzero(np.bincount(f["ring"], w, 32) > 0)
        dev = per_ring(f["ring"], w, ratio[k], lit)
        worst[name] = (float(np.abs(dev).max()), float(np.sqrt(np.mean(dev ** 2))))
    return worst


@pytest.mark.parametrize("template", list(PIXEL_KPC))
def test_every_clustered_part_s_light_per_level_0_ring_is_kept_by_its_map(frames, template):
    """R5d as amended on builder B's measurement: one sampling tolerance, 5e-2, for every part the march clusters - the
    young light (times m_3 / cell_mean_3) and each of the middle part's kept shares (times m_k / cell_mean_k). Written
    at, worst per level-0 ring (rms): Milky Way young 4.42e-2 (1.39e-2), kept 3 4.28e-2 (1.27e-2), kept 2 3.70e-2
    (1.04e-2), kept 1 3.93e-2 (8.4e-3); NGC 4414 young 3.38e-2 (8.4e-3), kept 3 3.89e-2 (9.6e-3), kept 2 3.78e-2
    (1.22e-2), kept 1 3.59e-2 (1.11e-2). One class: the placement weight's alignment with one draw of the map inside a
    level-0 cell (the bare map over its cell mean holds per ring to 3e-3 for k = 1, 2). The 2e-2 first ruled for the
    kept shares came from the probe's one number, kept 1 alone on the Milky Way (1.4e-2; 1.34e-2 here with the
    placement alone). Debt #176 carries the numbers."""
    worst = light_per_ring(frames[template])
    print(f"{template}: light per level-0 ring with the map over without - 1 (worst, rms): "
          + ", ".join(f"{n} {w:.2e} / {s:.2e}" for n, (w, s) in worst.items()))
    assert all(w < CLUSTERED_LIGHT for w, _ in worst.values()), worst


@pytest.mark.parametrize("template", list(PIXEL_KPC))
def test_the_3_octave_map_s_pixel_mean_per_cell_is_near_the_header_s_cell_mean(frames, template):
    """The lattice's sanity: the 3-octave map's mean over each level-0 cell's pixels over the header's cell mean (the
    published census_clustering_cell_mean, on the field's table lattice). Each cell's pixel count is in the hundreds
    to the thousands, so the per-cell scatter is the map's own (sigma 1.75), not a bias. Written at: per ring worst
    1.60e-2 (Milky Way), 7.7e-3 (NGC 4414); per cell rms 3.6e-2 / 1.9e-2. Held under 6e-2, the probe's 5.0e-2 worst on
    its own 4-point lattice."""
    f = frames[template]
    mean3 = np.asarray(f["header"]["census_clustering"]["cell_mean"]["3"], float)
    m3 = f["clustering"].maps(f["x"], f["y"], (3,))[0]
    count = np.bincount(f["cell"], None, 1024)
    seen = count > 0
    cell = np.bincount(f["cell"], m3, 1024)[seen] / count[seen] / mean3[seen] - 1.0
    ring = np.bincount(f["ring"], m3 / mean3[f["cell"]], 32) / np.bincount(f["ring"], None, 32) - 1.0
    print(f"{template}: 3-octave map's pixel mean over the cell mean - 1: per cell rms {np.sqrt(np.mean(cell ** 2)):.3e} "
          f"worst {np.abs(cell).max():.3e}; per ring worst {np.abs(ring).max():.3e}")
    assert np.abs(ring).max() < 6e-2
