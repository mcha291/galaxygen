"""S64 (BUILD_III Phase V6; RULING_S64 R1-R2): the clouds as extinction at whole-galaxy scale, the API side.

R1: ``/api/clouds`` carries ``cloud_dust_extinction_v``, each cloud's face-on mean A_V from its own dust - its mass
times the ring's dust-to-gas ratio times the ring's A_V per unit dust column, both at its birth radius, over
``pi cloud_size^2`` (``cloud_size`` is the radius, ``sqrt(M / pi Sigma_GMC)``) - derived in the API from published
fields, no stage and no constant on the wire. R2: ``/api/render`` carries ``dust_diffuse_share``, the share of each
ring's dust that is diffuse once the ring's realised clouds hold theirs, summed off the ring-first draw's streams,
with the header entry ``clouds``. Gate (i): per level-0 cell ring, the share times the ring's dust plus the clouds'
dust from the MATERIALISED census (the independent path) is the ring's published dust to 1e-12, both templates,
layer on and off; the render runs no stage more than it did. Every check here recomputes from published fields and
the census's rows with this file's own arithmetic, never the module's.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

import layer_reference
from galaxy.api import v6_clouds, wire
from galaxy.api.service import Service
from galaxy.stages import clouds as _clouds

ROOT = Path(__file__).resolve().parents[1]
RGB = json.dumps(json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))["sets"]["rgb"]["curves"])
RINGS, SECTORS = 32, 32
CASES = [(t, layer) for t in ("milky_way", "ngc_4414") for layer in ("on", "off")]
# The render's stages at 01c4d4e, before the share (tools/timings.py "render: whole, rgb", a fresh process): the
# clouds stage is among them because the nebular line is redistributed from the census (checkpoint 5) - the share
# adds none.
RENDER_STAGES = ["halo", "census_clustering", "disc", "assembly", "bar", "pattern", "arm_pieces", "gas_pattern",
                 "stellar_pattern", "sfh_azimuthal", "chemistry_dtd", "gas_spurs", "light", "spurs", "vertical_alpha",
                 "ism", "dust", "clouds", "gas_fluctuation", "cloud_texture", "clusters", "nebular"]
# S66 (D226 R6; the review's M1): the render runs gas_fluctuation on every request - its header carries the field's
# cell normalisers - and with the layer off the stage returns its neutral (the route may not branch on the layer, I5).
# The disc's realised clouds' share of its dust and the first three rings' expected shares (S64's probe, measured;
# recorded in D224, not targets: the realised share is the census's draw, the expected the ring's molecular fraction).
CLOUDS_SHARE_DISC = {"milky_way": 0.4899973, "ngc_4414": 0.6327142}
EXPECTED_FIRST_THREE = {"milky_way": (0.8264951, 0.7385616, 0.6628994), "ngc_4414": (0.7907958, 0.6709560, 0.5524492)}


@pytest.fixture(scope="module")
def service():
    return Service()


_held: dict = {}


def get(service, path, **q):
    key = (path, tuple(sorted(q.items())))
    if key not in _held:
        r = service.handle(path, {k: [str(v)] for k, v in q.items()})
        assert r.status == 200, r.body[:400]
        _held[key] = (*wire.decode(r.body), r)
    return _held[key]


def fields(service, template, layer, names):
    return get(service, "/api/arrays", template=template, layer=layer, fields=",".join(names))[1]


def ring_edges(R):
    return np.linspace(R[0], R[-1], RINGS + 1)


def ring_integral(sigma, R):
    """Each level-0 ring's mass, Msun: sigma (Msun/pc2) * 2 pi R over the ring's grid points (both edges held), by
    the trapezoid on the whole grid - this file's own arithmetic."""
    e = ring_edges(R)
    out = np.zeros(RINGS)
    for i in range(RINGS):
        w = np.where((R >= e[i]) & (R <= e[i + 1]), sigma * 2.0 * math.pi * R * 1.0e6, 0.0)
        out[i] = float(np.sum(0.5 * (w[1:] + w[:-1]) * np.diff(R)))
    return out


@pytest.mark.parametrize("template,layer", CASES)
def test_gate_i_the_rings_dust_is_the_diffuse_share_plus_the_realised_clouds(service, template, layer):
    R = service.grid.R
    h, a, _ = get(service, "/api/render", template=template, layer=layer, filters=RGB)
    share = np.asarray(a["dust_diffuse_share"], dtype=float)
    assert h["axes"]["dust_diffuse_share"] == ["R"] and share.shape == R.shape
    f = fields(service, template, layer, ["dust_surface_density", "dust_to_gas_ratio"])
    dust = ring_integral(np.asarray(f["dust_surface_density"]), R)
    hc, c, _ = get(service, "/api/clouds", template=template, layer=layer)
    ring = np.asarray(c["cell"]) // SECTORS
    clouds_dust = np.bincount(ring, weights=c["cloud_mass"] * np.interp(c["cloud_birth_radius"], R, f["dust_to_gas_ratio"]), minlength=RINGS)
    e = ring_edges(R)
    for i in range(RINGS):
        # The grid rings the cell ring holds all carry its share (the last edge in the last ring).
        here = (R >= e[i]) & ((R < e[i + 1]) | (i == RINGS - 1))
        assert np.ptp(share[here]) == 0.0, i
        s = float(share[here][0])
        if dust[i] > 0.0:
            assert abs(s * dust[i] + clouds_dust[i] - dust[i]) <= 1e-12 * dust[i], (i, s, dust[i], clouds_dust[i])
        else:
            assert s == 1.0 and clouds_dust[i] == 0.0
    # The header's rings say the same, and the disc's realised clouds' share is the probe's.
    rings = h["clouds"]["rings"]
    assert np.allclose(rings["dust_mass"], dust, rtol=1e-12, atol=0.0)
    assert np.allclose(rings["cloud_dust_mass"], clouds_dust, rtol=1e-12, atol=0.0)
    assert rings["clouds_share_disc"] == pytest.approx(clouds_dust.sum() / dust.sum(), rel=1e-12)
    assert rings["clouds_share_disc"] == pytest.approx(CLOUDS_SHARE_DISC[template], rel=1e-6)
    # The share is floored at 0 (B9) and the rings where the floor acted are listed: none, on either template.
    assert rings["floored"] == []
    assert v6_clouds.floored(np.array([1.0, 2.0, 0.0]), np.array([1.5, 1.0, 0.3])) == [{"ring": 0, "excess_dust_mass": 0.5}]
    assert v6_clouds.ring_share(np.array([1.0, 2.0, 0.0]), np.array([1.5, 1.0, 0.3])).tolist() == [0.0, 0.5, 1.0]
    # The expected share is recorded, not used: the ring's molecular dust over its dust (its molecular fraction).
    g = fields(service, template, layer, ["gas_molecular_surface_density", "dust_to_gas_ratio"])
    expected = ring_integral(np.asarray(g["gas_molecular_surface_density"]) * g["dust_to_gas_ratio"], R)
    lit = dust > 0
    assert np.allclose(np.asarray(rings["expected_clouds_share"])[lit], expected[lit] / dust[lit], rtol=1e-12, atol=0.0)
    assert tuple(rings["expected_clouds_share"][:3]) == pytest.approx(EXPECTED_FIRST_THREE[template], rel=1e-6)


@pytest.mark.parametrize("template,layer", CASES)
def test_r1_the_clouds_dust_column_is_its_formula_on_published_fields(service, template, layer):
    R = service.grid.R
    h, c, _ = get(service, "/api/clouds", template=template, layer=layer)
    # S70 (D234): was the last column - Audit V F-4-3 appends the clouds' shape after it (test_s70_* below).
    assert h["columns"][-3:] == ["cloud_dust_extinction_v", "cloud_axis_ratio", "cloud_angle"]
    assert [x["name"] for x in h["arrays"]][-5:] == ["cloud_dust_extinction_v", "cloud_axis_ratio", "cloud_angle", "cell", "index"]
    f = fields(service, template, layer, ["dust_to_gas_ratio", "dust_extinction_v", "dust_surface_density"])
    sd = np.asarray(f["dust_surface_density"])
    per_dust = np.where(sd > 0, np.asarray(f["dust_extinction_v"]) / np.where(sd > 0, sd, 1.0), 0.0)
    b = np.asarray(c["cloud_birth_radius"])
    mine = c["cloud_mass"] * np.interp(b, R, f["dust_to_gas_ratio"]) * np.interp(b, R, per_dust) / (math.pi * c["cloud_size"] ** 2)
    assert np.allclose(c["cloud_dust_extinction_v"], mine, rtol=1e-12, atol=0.0)
    assert np.all(c["cloud_dust_extinction_v"] >= 0.0)
    # The column's A_V x area is the cloud's dust times the ring's A_V per unit dust: what a raster conserves.
    about = h["clouds"]["derived"]["cloud_dust_extinction_v"]
    assert about["unit"] == "mag" and "cloud_extinction_v" in about["about"] and "#167" in about["about"]
    assert "cloud_birth_radius" in about["fields"]


def test_r4_the_clouds_route_sends_float32_on_request(service):
    _, c8, r8 = get(service, "/api/clouds")
    _, c4, r4 = get(service, "/api/clouds", precision="f4")
    assert c4["cloud_dust_extinction_v"].dtype == np.float32 and c4["cell"].dtype == c8["cell"].dtype
    assert np.array_equal(c4["cloud_dust_extinction_v"], c8["cloud_dust_extinction_v"].astype(np.float32))
    assert len(r4.body) < 0.62 * len(r8.body)
    assert service.handle("/api/clouds", {"precision": ["f2"]}).status == 400


def test_c_the_share_runs_no_stage_more_and_materialises_no_census(monkeypatch):
    fresh = Service()
    r = fresh.handle("/api/render", {"filters": [RGB]})
    assert r.status == 200 and list(r.stages) == RENDER_STAGES
    # The share itself reads the ring streams alone: with the census's materialiser refused, it still answers.
    f = fresh.handle("/api/arrays", {"fields": [",".join(v6_clouds.SHARE_FIELDS)]})
    _, a = wire.decode(f.body)
    from galaxy.models import DEFAULT, MODELS
    model = MODELS.get(DEFAULT)
    constants = {k: c.value for k, c in model.constants.items()}

    def refused(*args, **kwargs):
        raise AssertionError("the share materialised a census")

    monkeypatch.setattr(_clouds, "materialise_clouds", refused)
    share, rings = v6_clouds.diffuse_share(a, fresh.grid.R, 0, constants)
    header, arrays = wire.decode(r.body)
    assert np.array_equal(share, arrays["dust_diffuse_share"])
    assert rings["clouds_share_disc"] == pytest.approx(CLOUDS_SHARE_DISC["milky_way"], rel=1e-6)


@pytest.mark.parametrize("template", ["milky_way", "ngc_4414"])
def test_d_the_share_is_the_same_layer_on_and_off_and_a_share(service, template):
    _, on, _ = get(service, "/api/render", template=template, layer="on", filters=RGB)
    _, off, _ = get(service, "/api/render", template=template, layer="off", filters=RGB)
    assert np.array_equal(on["dust_diffuse_share"], off["dust_diffuse_share"])
    s = on["dust_diffuse_share"]
    assert np.all((s >= 0.0) & (s <= 1.0)) and s.min() < 0.5 and s.max() == 1.0
    # The dust_extinction component is unchanged by the share: the viewer multiplies.
    _, a = get(service, "/api/arrays", template=template, layer="on", fields="dust_extinction_v")[:2]
    assert on["dust_extinction"].shape[0] == a["dust_extinction_v"].shape[0]


def test_e_the_header_states_the_rule_and_ships_the_array(service):
    h, a, _ = get(service, "/api/render", template="milky_way", layer="on", filters=RGB)
    entry = h["clouds"]
    assert entry["array"] == "dust_diffuse_share" and "dust_diffuse_share" in a
    assert entry["rule"] == "diffuse depth(R, phi) = depth(R) x dust_placement(R, phi) x dust_diffuse_share(R)"
    assert entry["route"] == "/api/clouds" and entry["column"] == "cloud_dust_extinction_v"
    assert entry["layers"]["diffuse"] == "dust" and entry["layers"]["clouds"] == "halpha_hii"
    assert entry["layers"]["clouds_scale_height"] == h["layers"]["halpha_hii"]
    assert "1e-12" in entry["closure"] and "not used" in entry["rings"]["about"]
    assert h["components"]["dust_extinction"]["fields"] == ["dust_extinction_v"]
    # At level=k a cell's mean of its rings' shares, as the dust's height is.
    hl, al, _ = get(service, "/api/render", filters=RGB, level=1, r_min=7, r_max=9, phi_min=0, phi_max=0.4)
    assert hl["axes"]["dust_diffuse_share"] == ["cell"] and al["dust_diffuse_share"].shape == al["cell"].shape
    assert np.all((al["dust_diffuse_share"] > 0.0) & (al["dust_diffuse_share"] <= 1.0))


def test_f_the_s55_digest_reports_the_new_keys_added(service):
    q = {"layer": ["off"], "filters": [layer_reference.curves()]}
    got = layer_reference.route_digest(service, "/api/render", q)
    # S64's key, then S66's four arrays and three header entries (layer_reference.ADDED_ARRAYS_AT_S66, ADDED_AT_S66).
    assert "dust_diffuse_share" in got["added"] and got["added"][-1] == layer_reference.ADDED_AT_S66[-1]
    got = layer_reference.route_digest(service, "/api/clouds", {"layer": ["off"]})
    # S70 (D234): was ["cloud_dust_extinction_v"] - and the clouds' shape (Audit V F-4-3, layer_reference.ADDED_AT_S70).
    assert got["added"] == ["cloud_dust_extinction_v", "cloud_axis_ratio", "cloud_angle"]
    assert not {"cloud_dust_extinction_v", "cloud_axis_ratio", "cloud_angle"} & {x[0] for x in got["arrays"]}


# --- S70 (Audit V F-4-3, D233/D234): each cloud's face-on shape, published --------------------------------------------
# The viewer drew each cloud as an ellipse along the gas fluctuation field's shear from S67 (D230 R2), by a formula it
# applied itself to the render header's strain; since S70 /api/clouds publishes the two numbers. Checked here twice
# with this file's own arithmetic: against the header's rule on the render header's own entry, and against the
# field's read map itself (its rotation by theta(R), from the header's twist and strain) by finite differences.


def ring_by_edges(edges, radius):
    """The level-0 ring of each radius: the last edge not above it, held to the first and last rings."""
    n = len(edges) - 1
    return np.array([max(0, min(n - 1, int(np.sum(np.asarray(edges[1:-1]) <= r)))) for r in radius])


@pytest.mark.parametrize("template", ["milky_way", "ngc_4414"])
def test_s70_the_clouds_shape_is_the_rule_on_the_render_headers_published_strain(service, template):
    h, _, _ = get(service, "/api/render", template=template, layer="on", filters=RGB)
    gas = h["gas_fluctuation"]
    edges, strain, sense = np.asarray(gas["edges"]), np.asarray(gas["ring"]["strain"]), float(gas["sense"])
    hc, c, _ = get(service, "/api/clouds", template=template, layer="on")
    k = sense * strain[ring_by_edges(edges, c["cloud_radius"])]
    lam = (2.0 + k * k + np.abs(k) * np.sqrt(k * k + 4.0)) / 2.0
    assert np.array_equal(c["cloud_axis_ratio"], lam)
    assert np.allclose(c["cloud_angle"], np.arctan2(lam - 1.0, k), rtol=0.0, atol=4e-16)
    assert np.all(c["cloud_axis_ratio"] >= 1.0) and np.ptp(c["cloud_axis_ratio"]) > 0.0
    # every term of the rule is published: the header names them and the render header carries each
    for name in ("cloud_axis_ratio", "cloud_angle"):
        about = hc["clouds"]["derived"][name]
        assert about["fields"] == ["cloud_radius", "gas_fluctuation.edges", "gas_fluctuation.ring.strain", "gas_fluctuation.sense"]
        assert "atan2(cloud_axis_ratio - 1, k)" in about["rule"] and "SYNTHETIC (rule A10)" in about["about"]
    assert hc["clouds"]["derived"]["cloud_angle"]["unit"] == "rad"


@pytest.mark.parametrize("template", ["milky_way", "ngc_4414"])
def test_s70_the_clouds_shape_is_the_image_of_a_round_feature_under_the_fields_read(service, template):
    """The closure: the field is read at its point rotated by -theta(R), theta = sense (twist_r + strain_r ln(max(R,
    edges[0]) / edges_r)) (the header's rule). Its Jacobian J by central differences maps a small circle of the field to
    the ellipse {p : p^T J^T J p = 1} in the disc - axis ratio sqrt(l_max / l_min) of J^T J, long axis along its small
    eigenvector - which is the published shape, at every 40th cloud away from a ring edge."""
    h, _, _ = get(service, "/api/render", template=template, layer="on", filters=RGB)
    gas = h["gas_fluctuation"]
    edges, strain, twist, sense = (np.asarray(gas["edges"]), np.asarray(gas["ring"]["strain"]),
                                   np.asarray(gas["ring"]["twist"]), float(gas["sense"]))
    _, c, _ = get(service, "/api/clouds", template=template, layer="on")
    checked = 0
    for i in range(0, len(c["cloud_radius"]), 40):
        R0, phi0 = float(c["cloud_radius"][i]), float(c["cloud_azimuth"][i])
        r = int(ring_by_edges(edges, [R0])[0])
        if not (edges[r] + 1e-4 < R0 < edges[r + 1] - 1e-4):
            continue  # the differences would straddle a ring edge, where the read map's strain steps

        def read(x, y, r=r):
            R = math.hypot(x, y)
            th = sense * (twist[r] + strain[r] * math.log(max(R, edges[0]) / edges[r]))
            return (x * math.cos(th) + y * math.sin(th), y * math.cos(th) - x * math.sin(th))

        x, y, d = R0 * math.cos(phi0), R0 * math.sin(phi0), 1e-6
        fx, bx, fy, by = read(x + d, y), read(x - d, y), read(x, y + d), read(x, y - d)
        J = np.array([[(fx[0] - bx[0]) / (2 * d), (fy[0] - by[0]) / (2 * d)], [(fx[1] - bx[1]) / (2 * d), (fy[1] - by[1]) / (2 * d)]])
        m = J.T @ J
        lo, hi = np.linalg.eigvalsh(m)
        assert math.sqrt(hi / lo) == pytest.approx(float(c["cloud_axis_ratio"][i]), rel=1e-6), i
        long = math.atan2(lo - m[0, 0], m[0, 1])  # (M - l_min) v = 0, v = (m01, l_min - m00)
        assert abs(math.sin(phi0 + float(c["cloud_angle"][i]) - long)) < 1e-6, i
        checked += 1
    assert checked > 100


@pytest.mark.parametrize("template", ["milky_way", "ngc_4414"])
def test_s70_the_clouds_are_round_with_the_layer_off_and_float32_on_request(service, template):
    _, off, _ = get(service, "/api/clouds", template=template, layer="off")
    assert np.all(off["cloud_axis_ratio"] == 1.0) and np.all(off["cloud_angle"] == 0.0)
    h, _, _ = get(service, "/api/render", template=template, layer="off", filters=RGB)
    assert h["gas_fluctuation"]["seed"] is None and h["gas_fluctuation"]["ring"] is None  # no field published, no shear
    _, c8, _ = get(service, "/api/clouds", template=template, layer="on")
    _, c4, _ = get(service, "/api/clouds", template=template, layer="on", precision="f4")
    for name in ("cloud_axis_ratio", "cloud_angle"):
        assert c4[name].dtype == np.float32 and np.array_equal(c4[name], c8[name].astype(np.float32)), name
