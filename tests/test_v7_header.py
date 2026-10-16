"""The render header's V7 entries (S66, BUILD_III Phase V7; DECISIONS.md D226, RULING_S66 R4-R6): what the viewer's
march evaluates, each map read once per ray as a thin screen at the midplane, every number the model's.

- ``gas_fluctuation``: the gas fluctuation field's seed, form, ring table, ladder weights and cell normalisers - the
  run's published fields to the bit;
- ``census_clustering``: the clustering field's form and the k-octave maps' cell means, k = 1, 2, 3, on the field's
  table lattice - k = 3 the published ``census_clustering_cell_mean`` to the bit, the others the same arithmetic on
  ``ClusteringField.maps``;
- ``spurs`` and ``dust_placement_unspurred``: composed through the model's own ``Spurs.compose_cells`` they give
  ``dust_placement`` to 1e-12 per cell; on a template without spurs the two placements are the same bits;
- ``ages.middle_kept``: the middle part split at the octaves' survival ages, the three kept arrays and the rest summing
  to ``stars_middle`` per ring and filter to 1e-12.

With the layer off the three entries' values are null (the keys kept) and the arrays are what they are with no layer
(I5: the same arrays either way): the unspurred placement is the neutral placement, the kept parts the same bits.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import v7_layer
from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.layer import census_clustering as l1
from galaxy.layer import gas_fluctuation as gf
from galaxy.layer import noise
from galaxy.stages import bright as br
from galaxy.stages import spectra
from galaxy.stages.spurs import Spurs
from galaxy.stages.systems import CELL_SECTORS, cell_edges

ROOT = Path(__file__).resolve().parents[1]
FILTERS = json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))
TEMPLATES = ("milky_way", "ngc_4414")


@pytest.fixture(scope="module")
def api() -> Service:
    return Service(cache=4)


def render(api: Service, template: str, layer: str = "on", name: str = "rgb") -> tuple[dict, dict]:
    got = api.handle("/api/render", {"template": [template], "layer": [layer],
                                     "filters": [json.dumps(FILTERS["sets"][name]["curves"])]})
    assert got.status == 200, got.body[:300]
    return wire.decode(got.body)


def published(api: Service, template: str, *names: str) -> dict:
    got = api.handle("/api/arrays", {"template": [template], "fields": [",".join(names)]})
    assert got.status == 200, got.body[:300]
    header, arrays = wire.decode(got.body)
    return {**header["scalars"], **arrays}


def constants(api: Service) -> dict:
    """The default model's constants (a template moves inputs, not constants)."""
    from galaxy.core.registry import production
    from galaxy.models import DEFAULT

    models, _, _ = production()
    model = models.get(DEFAULT) if isinstance(DEFAULT, str) else DEFAULT
    return {k: c.value for k, c in model.constants.items()}


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_gas_fluctuation_entry_is_the_run_s_published_field(api, template):
    """Seed, ring table and cell normalisers are the published fields' bits; the weights are the field's ladder for
    every break index; the edges the level-0 rings'; with the layer off every value but the form's numbers is null."""
    header, _ = render(api, template)
    g = header["gas_fluctuation"]
    names = [d.name for d in gf.PUBLISHES]
    f = published(api, template, *names)
    assert g["seed"] == int(f["gas_fluctuation_seed"])
    for key, name in (("break_octave", "gas_fluctuation_break_octave"), ("sigma", "gas_fluctuation_sigma"),
                      ("strain", "gas_fluctuation_strain"), ("twist", "gas_fluctuation_twist"), ("norm", "gas_fluctuation_norm")):
        assert np.array_equal(np.array(g["ring"][key], dtype=float), np.asarray(f[name], dtype=float)), key
    assert np.array_equal(np.array(g["cell_normaliser"]), np.asarray(f["gas_fluctuation_cell_normaliser"], dtype=float))
    assert np.array_equal(np.array(g["edges"]), cell_edges(api.grid.R)[0]) and len(g["edges"]) == 33
    c = constants(api)
    field = gf.field_of(g["seed"], {**{k: np.array(v) for k, v in g["ring"].items()}, "edges": np.array(g["edges"]),
                                    "sense": g["sense"]}, c)
    assert np.array_equal(np.array(g["weights"]), field.amplitudes()) and np.shape(g["weights"]) == (7, 6)
    assert g["sense"] == -1.0 and (g["scale"], g["octaves"], g["lacunarity"]) == (0.19, 6, 2.0)
    assert "thin screen at the ray's crossing of the midplane" in g["rule"] and "D226" in g["rule"]
    off, arrays = render(api, template, "off")
    assert {k for k, v in off["gas_fluctuation"].items() if v is not None} == {"scale", "slope", "change", "octaves", "lacunarity", "rule"}
    assert set(off["gas_fluctuation"]) == set(g)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_clustering_entry_carries_the_k_octave_cell_means(api, template):
    """cell_mean['3'] is the published census_clustering_cell_mean to the bit (the same lattice and arithmetic); '2' and
    '1' are the truncated maps' R-weighted means on the same lattice, recomputed here on 12 cells from
    ClusteringField.maps to 1e-12, and plateau well under 1 (#162); the octave ages are the bright catalogue's."""
    header, _ = render(api, template)
    e = header["census_clustering"]
    f = published(api, template, "census_clustering_seed", "census_clustering_cell_mean")
    assert e["seed"] == int(f["census_clustering_seed"])
    assert np.array_equal(np.array(e["cell_mean"]["3"]), np.asarray(f["census_clustering_cell_mean"], dtype=float))
    c = constants(api)
    field = l1.ClusteringField.of(e["seed"], c)
    assert (e["gain"], e["top"], e["norm"]) == tuple(field.weights())
    rings, sectors = cell_edges(api.grid.R)
    for cell in (0, 37, 130, 300, 333, 512, 640, 700, 800, 900, 1000, 1023):
        r, s = divmod(cell, CELL_SECTORS)
        r_mid, phi_mid = field.lattice(rings[r], rings[r + 1], sectors[s], sectors[s + 1], e["table_points"])
        q = noise.cell_quadrature(rings[r], rings[r + 1], sectors[s], sectors[s + 1], (r_mid.size, phi_mid.size))
        maps = field.maps(q[:, 0] * np.cos(q[:, 1]), q[:, 0] * np.sin(q[:, 1]), (1, 2, 3))
        for k, m in zip((1, 2, 3), maps):
            want = np.sum(q[:, 0] * m) / np.sum(q[:, 0])
            assert abs(e["cell_mean"][str(k)][cell] - want) <= 1e-12 * want, (cell, k)
    assert 0.2 < np.median(e["cell_mean"]["1"]) < np.median(e["cell_mean"]["2"]) < np.median(e["cell_mean"]["3"])
    survival = br.octave_survival(field.octave_scales_pc(), c[br.AGE_AMPLITUDE], c[br.AGE_INDEX])
    assert e["octave_ages_myr"] == pytest.approx(survival.tolist(), rel=0.0, abs=0.0)
    assert e["octave_ages_myr"] == pytest.approx([40.71, 31.18, 23.87], abs=0.01)
    off, _ = render(api, template, "off")
    assert off["census_clustering"]["seed"] is None and off["census_clustering"]["cell_mean"] is None
    assert off["census_clustering"]["octave_ages_myr"] == e["octave_ages_myr"]


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_unspurred_placement_composed_with_the_spurs_is_the_dust_s(api, template):
    """dust_placement_unspurred composed through the model's own Spurs.compose_cells with the header's table and its
    share gives dust_placement to 1e-12 per cell; the share is the spurs' ring mean on the render's rings exactly.
    The Milky Way lays spurs (48 at S66), NGC 4414 none: there the two placements are the same bits and the share 0."""
    header, arrays = render(api, template)
    sp, placement = header["spurs"], header["placement"]
    assert placement["dust_unspurred"] == "dust_placement_unspurred" and header["axes"]["dust_placement_unspurred"] == ["R", "phi"]
    rows = {k: np.array(v, dtype=float) for k, v in sp["rows"].items()}
    R, edges = api.grid.R, api.grid.axes["phi"].edges
    unspurred, placed = arrays["dust_placement_unspurred"], arrays["dust_placement"]
    assert unspurred.shape == placed.shape == (R.size, edges.size - 1)
    if template == "ngc_4414":
        assert rows["radius"].size == 0 and not any(sp["share"])
        assert np.array_equal(unspurred, placed)
    else:
        assert rows["radius"].size == 48
        spurs = Spurs(rows["radius"], rows["azimuth"], rows["contrast"], rows["pitch"], rows["length"], rows["width"],
                      rows["fall"], turn=sp["turn"])
        assert np.array_equal(np.array(sp["share"]), spurs.ring_mean(R))
        composed = np.maximum(spurs.compose_cells(R, edges, unspurred), 0.0)
        assert np.max(np.abs(composed - placed)) <= 1e-12
        touched = np.array(sp["share"]) > 0.0
        assert touched.sum() > 10 and np.max(np.abs(unspurred[touched] - placed[touched])) > 0.05  # the spurs move it
        assert np.array_equal(unspurred[~touched], placed[~touched])
    assert sp["reach"] == 9.0 and sp["fwhm_per_sigma"] == pytest.approx(2.0 * math.sqrt(2.0 * math.log(2.0)), rel=0, abs=0)
    assert set(sp["constants"]) == {"SPUR_PITCH", "SPUR_LENGTH", "SPUR_WIDTH", "SPUR_FALL"}
    off, off_arrays = render(api, template, "off")
    assert off["placement"]["dust_unspurred"] == "dust_placement_unspurred"
    assert np.array_equal(off_arrays["dust_placement_unspurred"], off_arrays["dust_placement"])
    assert np.all(off_arrays["dust_placement_unspurred"] == 1.0)
    assert all(off["spurs"][k] is None for k in ("rows", "turn", "share"))


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_middle_part_s_kept_windows_sum_to_it(api, template):
    """stars_middle_kept3/2/1 and the rest (stars_middle less the three) are the middle part's windows [20, 23.9),
    [23.9, 31.2), [31.2, 40.7) and [40.7, 100) Myr, each bright.window_anchors' light through the curves scaled by one
    closure factor per ring and filter: the four sum to stars_middle to 1e-12 through every set, each is
    non-negative, and they are recomputed here to 1e-12. Placed by the middle part's weight. Layer off: the same bits
    (the ages are the history's and the constants'), the maps 1."""
    c = constants(api)
    for name in ("rgb", "sho", "hoo"):
        header, arrays = render(api, template, name=name)
        kept = header["ages"]["middle_kept"]
        assert kept["weight"] == header["ages"]["parts"]["middle"]["weight"] == "stars_middle_placement"
        middle = arrays["stars_middle"]
        parts = [arrays[kept["arrays"][k]] for k in ("3", "2", "1")]
        rest = middle - sum(parts)
        assert all(np.all(p >= 0.0) for p in parts) and np.all(rest >= -1e-12 * np.maximum(middle, 1e-300))
        lit = middle > 0.0
        assert np.max(np.abs((sum(parts) + rest)[lit] / middle[lit] - 1.0)) < 1e-12
        windows = [kept["ages_gyr"][k] for k in ("3", "2", "1", "rest")]
        ages = np.array(kept["octave_ages_myr"]) / 1000.0
        assert windows == [[0.02, ages[2]], [ages[2], ages[1]], [ages[1], ages[0]], [ages[0], 0.1]]
        names = ("stars_formed_history", "feh_history", "disc_light_temperature")
        f = published(api, template, *names)
        spec = api.grid.spec
        anchors = br.window_anchors(f, spec.t_max, spec.n_t, c, [tuple(w) for w in windows])
        middle_anchor = br.part_anchors(f, spec.t_max, spec.n_t, c)[1]
        on = middle_anchor > 0.0
        assert np.max(np.abs(anchors.sum(axis=0)[on] / middle_anchor[on] - 1.0)) < 1e-12  # the windows partition it
        curves = spectra.parse_curves(FILTERS["sets"][name]["curves"])
        raw = np.stack([spectra.stellar_response(a, f["disc_light_temperature"], curves) for a in anchors])
        total = raw.sum(axis=0)
        ok = (total > 0.0) & lit
        factor = np.where(ok, middle / np.where(ok, total, 1.0), 1.0)
        for k, p in zip(range(3), parts):
            assert np.allclose(p, raw[k] * factor, rtol=1e-12, atol=0.0)
        assert kept["closure"]["factor"] == pytest.approx(np.max(np.abs(factor - 1.0), axis=0).tolist(), rel=1e-9)
    on_header, on = render(api, template)
    off_header, off = render(api, template, "off")
    assert off_header["ages"]["middle_kept"]["arrays"] == on_header["ages"]["middle_kept"]["arrays"]
    for name in on_header["ages"]["middle_kept"]["arrays"].values():
        assert np.array_equal(off[name], on[name]), name


def test_the_new_arrays_are_named_and_shaped(api):
    """The four arrays S66 adds, with their axes: the unspurred placement on the (R, phi) grid, the kept parts per ring
    and filter. That no array sent before moves is measured against 3794fc3's bodies on eight requests (RULING_S66 R10;
    recorded in D226) and, layer off, held by test_layer's S55 reference (layer_reference.ADDED_AT_S66)."""
    header, arrays = render(api, "milky_way")
    new = {"dust_placement_unspurred", *v7_layer.MIDDLE_KEPT.values()}
    assert new <= set(arrays)
    assert all(header["axes"][n] == (["R", "phi"] if n == "dust_placement_unspurred" else ["R", "filter"]) for n in new)
