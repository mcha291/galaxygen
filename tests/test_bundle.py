"""Template bundles (S72, BUILD_IV Phase W2): the key, the reader under the model's hash, the export's plan.

A bundle answers a request only when the request means what an entry's means and the bundle was built from the
serving model's own bytes; then it runs nothing (D4) and sends the bytes the model sent (the export's --check asserts
that over whole manifests; here a small hand-made bundle asserts it entry by entry). Everything else is computed. The
plan is checked against the requests a real viewer made (tests/fixtures/s72_viewer_requests.json), string for string,
because a body echoes some parameters as given.
"""

from __future__ import annotations

import json
import shutil
import threading
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from export_template import GROUPS, filter_sets, pick_threshold, plan, viewer_query
from galaxy.api import bundle
from galaxy.api import http as api_http
from galaxy.api import wire
from galaxy.api.service import ROUTES, ApiError, Response, Service
from galaxy.api.version import MODEL, content_hash
from galaxy.core.grids import DEFAULT, GridSpec

RGB = filter_sets()["rgb"]
TEMPLATE = "milky_way"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "s72_viewer_requests.json"


@pytest.fixture(scope="module")
def service():
    return Service()


def _template(service, name=TEMPLATE):
    return {t["name"]: t for t in service.handle("/api/templates").json()["templates"]}[name]


@pytest.fixture(scope="module")
def base(service):
    t = _template(service)
    return viewer_query(t, service.handle("/api/inputs", {"model": t["model"]}).json(), "on")


# --- the viewer's spelling ------------------------------------------------------------------------------------------

def test_numbers_and_queries_are_written_as_a_browser_writes_them():
    cases = {7.0: "7", 1.1e12: "1100000000000", 0.0173: "0.0173", 1e-7: "1e-7", 1e-6: "0.000001", 1.5e16: "15000000000000000",
             1e21: "1e+21", 0: "0", -3.5: "-3.5", 4414: "4414",
             # The probe's log (S72): the viewer's own strings.
             6.283185307179586: "6.283185307179586", 609546153006.4983: "609546153006.4983",
             0.014191065730401048: "0.014191065730401048", 35481.33892335753: "35481.33892335753",
             25118.86431509577: "25118.86431509577", 1258.9254117941662: "1258.9254117941662"}
    for value, written in cases.items():
        assert bundle.js_number(value) == written, value
    assert bundle.js_json([{"a": 1.0, "b": "x☉"}, None, True]) == '[{"a":1,"b":"x☉"},null,true]'
    assert bundle.js_value([1.0, 2]) == "1,2"
    assert bundle.js_query({"a": "x y~*-._/", "b": 2.0}) == "a=x+y%7E*-._%2F&b=2"
    assert bundle.js_query({"m": "10⁸ M☉"}) == "m=10%E2%81%B8+M%E2%98%89"


# --- the key: the request's meaning ---------------------------------------------------------------------------------

def test_the_key_is_what_the_service_reads_not_how_it_is_spelled(service, base):
    k = bundle.key(service, "/api/arrays", base | {"fields": "halo_virial_mass"})
    assert k is not None
    assert k == bundle.key(service, "/api/arrays", dict(reversed(list((base | {"fields": "halo_virial_mass"}).items()))))
    assert k == bundle.key(service, "/api/arrays/", bundle.js_query(base | {"fields": "halo_virial_mass"}))
    assert k == bundle.key(service, "/api/arrays", base | {"infall_timescale": "7.0", "fields": "halo_virial_mass"})
    assert k != bundle.key(service, "/api/arrays", base | {"infall_timescale": "7.5", "fields": "halo_virial_mass"})
    assert k != bundle.key(service, "/api/arrays", {"fields": "halo_virial_mass"}), "no template: no pin, another galaxy"
    # A raw parameter is its string: the body echoes a window's bounds as given.
    w = {"r_min": "0", "r_max": "30", "phi_min": "0", "phi_max": "6.283185307179586", "level": "0"}
    assert bundle.key(service, "/api/remnants", base | w) != bundle.key(service, "/api/remnants", base | w | {"r_min": "0.0"})
    # A request the service refuses has no key, and is computed: it answers with its own error.
    assert bundle.key(service, "/api/arrays", base | {"halo_mass": "nope", "fields": "x"}) is None
    assert bundle.key(service, "/api/arrays", base | {"no_such_input": "1", "fields": "x"}) is None
    assert bundle.key(service, "/api/arrays", base | {"layer": "OFF", "fields": "x"}) is None
    assert bundle.key(service, "/api/version", {}) is None and bundle.key(service, "/api", {}) is None


def test_layer_absent_is_layer_on_and_off_is_another_galaxy(service, base):
    q = base | {"fields": "halo_virial_mass"}
    assert bundle.key(service, "/api/arrays", q) == bundle.key(service, "/api/arrays", q | {"layer": "on"})
    assert bundle.key(service, "/api/arrays", q) != bundle.key(service, "/api/arrays", q | {"layer": "off"})


def test_filters_are_keyed_as_json_not_as_spelled(service):
    js = bundle.js_json(RGB)
    assert " " not in js and js.startswith('[{"name":"R","shape":"gaussian","centre":6498.09')
    shuffled = json.dumps([dict(reversed(list(c.items()))) for c in RGB], indent=2)
    keys = {bundle.key(service, "/api/blackbody", {"white": "6500", "filters": f}) for f in (js, json.dumps(RGB), shuffled)}
    assert len(keys) == 1 and None not in keys
    a = service.handle("/api/blackbody", {"white": "6500", "filters": js})
    b = service.handle("/api/blackbody", {"white": "6500", "filters": shuffled})
    assert a.ok and a.body == b.body, "the model answers the spellings alike, so one entry may serve them"


def test_a_body_is_a_function_of_the_request_not_of_the_cache():
    """S72 (R3): the header's stages is the closure the answer needs; what ran is X-Galaxy-Stages (D4) alone."""
    api = Service()
    cold = api.handle("/api/arrays", {"fields": "halo_virial_mass,stellar_surface_density"})
    warm = api.handle("/api/arrays", {"fields": "halo_virial_mass,stellar_surface_density"})
    assert cold.ok and cold.stages and warm.stages == ()
    assert cold.body == warm.body
    assert wire.decode(cold.body)[0]["stages"] == list(cold.stages)


# --- a small bundle, exported and read back ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def small(base):
    """Small entries in the viewer's spelling, layer absent (on): metadata, a one-stage array, the blackbody, a
    nine-cell region window, one bright tile at a high threshold and a small render window."""
    js = bundle.js_json(RGB)
    sector = {"r_min": "7", "r_max": "9", "phi_min": "0", "phi_max": "0.4"}
    return [
        ("/api/stages", {"model": "azimuthal"}),
        ("/api/templates", {}),
        ("/api/arrays", base | {"fields": "halo_virial_mass"}),
        ("/api/blackbody", {"white": "6500", "filters": js}),
        ("/api/region", base | sector),
        ("/api/bright", base | {"cells": "261", "l_min": "100000", "filters": js, "white": "6500", "precision": "f4"}),
        ("/api/render", base | {"white": "6500", "precision": "f4", "filters": js} | sector | {"level": "1"}),
    ]


@pytest.fixture(scope="module")
def exported(service, small, tmp_path_factory):
    root = tmp_path_factory.mktemp("bundles")
    answers = [(route, query, service.handle(route, query)) for route, query in small]
    for route, _, r in answers:
        assert r.status == 200, (route, r.body[:200])
    manifest = bundle.write(root, TEMPLATE, "on", service, answers)
    return root, manifest, {bundle.key(service, route, query): r for route, query, r in answers}


def test_a_bundle_answers_each_entry_byte_identical_and_runs_nothing(exported, small):
    root, manifest, live = exported
    served = Service(bundles=root)
    assert len(served.bundles) == len(small) == len(manifest["entries"])
    for route, query in small:
        got = served.handle(route, query)
        want = live[bundle.key(served, route, query)]
        assert got.source == "bundle" and got.stages == () and got.status == 200, route
        assert got.body == want.body and got.media == want.media, route
    # D4: a hit touched no stage and cached no galaxy, no cell and no bright cell (ruling 11: the caches are for misses).
    assert served._cache == {} and len(served.cells._cells) == 0 and len(served.bright._cells) == 0
    assert len(served._bright_galaxies) == 0


def test_another_spelling_of_an_entry_hits_and_is_the_bytes_the_model_gives_it(exported, service):
    root, _, _ = exported
    served = Service(bundles=root)
    base = dict(_entry(exported, "/api/arrays"))
    # Reordered, numbers spelled otherwise, the layer named: the same overrides, the same answer.
    respelled = dict(reversed(list(base.items()))) | {"halo_mass": "1.1e12", "infall_timescale": "7.0", "layer": "on"}
    got = served.handle("/api/arrays", respelled)
    assert got.source == "bundle" and got.body == service.handle("/api/arrays", respelled).body
    off = served.handle("/api/arrays", base | {"layer": "off"})
    assert off.source == "model" and off.ok
    # The template's overrides alone are other overrides (the defaults not restated): computed, not served.
    assert served.handle("/api/arrays", {"template": TEMPLATE, "fields": "halo_virial_mass"}).source == "model"


def _entry(exported, route):
    from urllib.parse import parse_qsl

    _, manifest, _ = exported
    return parse_qsl(next(e["query"] for e in manifest["entries"] if e["route"] == route), keep_blank_values=True)


def test_a_request_outside_the_bundle_is_computed(exported):
    root, _, _ = exported
    served = Service(bundles=root)
    got = served.handle("/api/arrays", {"fields": "halo_virial_mass"})
    assert got.ok and got.source == "model" and got.stages == ("halo",)
    assert served.handle("/api/fields", {"model": "azimuthal"}).source == "model"
    assert served.handle("/api/arrays", {"template": TEMPLATE, "halo_mass": "nope", "fields": "halo_virial_mass"}).status == 400
    assert served.handle("/api/nope").status == 404


def test_version_and_the_index_are_never_written_or_answered_from_a_bundle(service, exported, tmp_path):
    fake = Response(200, "application/json", b'{"stale": true}')
    for route in ("/api/version", "/api"):
        with pytest.raises(bundle.BundleError, match="has no key"):
            bundle.write(tmp_path, TEMPLATE, "on", service, [(route, {}, fake)])
    root, _, _ = exported
    served = Service(bundles=root)
    for route in ("/api/version", "/api"):
        assert served.handle(route).source == "model"
    assert served.handle("/api/version").json()["model"]["hash"] == served.model_hash == content_hash(MODEL)["hash"]


def test_a_bundle_from_another_model_is_refused_naming_both_hashes(exported, tmp_path):
    root, manifest, _ = exported
    copy = tmp_path / "bundles"
    shutil.copytree(root, copy)
    path = copy / TEMPLATE / "on" / bundle.MANIFEST
    stale = "0" * 32
    path.write_text(json.dumps(manifest | {"model_hash": stale}, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    with pytest.raises(bundle.BundleMismatch) as refused:
        Service(bundles=copy)
    message = str(refused.value)
    assert stale in message and manifest["model_hash"] in message and str(path.parent) in message
    assert not isinstance(refused.value, ApiError), "a startup failure, not a request's 4xx"


def test_a_bundle_built_on_another_grid_is_refused_naming_the_grid(exported):
    """Q3 (S72): the same model bytes on another mesh compute other answers; the manifest's grid and models are
    checked after its hash."""
    root, manifest, _ = exported
    other = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
    assert manifest["grid"] == repr(DEFAULT) and manifest["grid"] != repr(other)
    assert manifest["models"] == list(Service().models.names())
    with pytest.raises(bundle.BundleMismatch) as refused:
        Service(grid=other, bundles=root)
    assert "grid" in str(refused.value) and repr(other) in str(refused.value) and manifest["grid"] in str(refused.value)


def test_the_manifest_is_the_files(exported, service):
    root, manifest, _ = exported
    path = root / TEMPLATE / "on" / bundle.MANIFEST
    raw = path.read_bytes()
    assert b"\r" not in raw and json.loads(raw) == manifest
    assert manifest["format"] == bundle.FORMAT and manifest["layer"] == "on" and manifest["template"] == TEMPLATE
    assert manifest["model_hash"] == content_hash(MODEL)["hash"]
    files = sorted(p.name for p in (path.parent / bundle.ENTRIES).iterdir())
    assert files == sorted(e["key"] for e in manifest["entries"])
    for e in manifest["entries"]:
        assert (path.parent / bundle.ENTRIES / e["key"]).stat().st_size == e["bytes"]
        assert bundle.key(service, e["route"], e["query"]) == e["key"], "the recorded query is the request"
    assert [e["stages"] for e in manifest["entries"] if e["route"] == "/api/stages"] == [[]]


def test_a_damaged_bundle_is_refused(exported, tmp_path):
    root, manifest, _ = exported
    copy = tmp_path / "bundles"
    shutil.copytree(root, copy)
    first = copy / TEMPLATE / "on" / bundle.ENTRIES / manifest["entries"][0]["key"]
    first.write_bytes(first.read_bytes() + b"x")
    with pytest.raises(bundle.BundleError, match="the manifest says"):
        Service(bundles=copy)


def test_the_server_says_where_an_answer_came_from_and_a_post_is_a_get(exported, small, service):
    root, _, live = exported
    server = api_http.make_server("127.0.0.1", 0, Service(bundles=root))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}"
    route, query = small[3]  # the blackbody, with the viewer's curves
    want = live[bundle.key(service, route, query)].body
    try:
        with urllib.request.urlopen(url + route + "?" + bundle.js_query(query)) as r:
            assert r.headers["X-Galaxy-Source"] == "bundle" and r.headers["X-Galaxy-Stages"] == ""
            assert r.headers["Cache-Control"] == "no-store"
            assert r.read() == want
        post = urllib.request.Request(url + route, data=bundle.js_query(query).encode("ascii"), method="POST",
                                      headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(post) as r:
            assert r.headers["X-Galaxy-Source"] == "bundle" and r.read() == want
        with urllib.request.urlopen(url + "/api/version") as r:
            assert r.headers["X-Galaxy-Source"] == "model"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


# --- the plan, against what the viewer sent -------------------------------------------------------------------------

def _logged() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _sent(doc: dict, r: dict) -> str:
    rest = r["rest"]
    for name, curves in filter_sets().items():
        rest = rest.replace(f"filters=<set:{name}>", "filters=" + bundle.js_query({"": bundle.js_json(curves)})[1:])
    return rest if r["galaxy"] is None else doc["prefixes"][r["galaxy"]] + ("&" + rest if rest else "")


def test_the_plan_is_what_the_viewer_sends_string_for_string(service, exported):
    """Every galaxy-scale request the probe's walk logged is in the plan of its galaxy, byte for byte, and the
    landing thresholds are the viewer's pick from the table (MW 10^4.55, NGC 10^4.40 as the walk logged them)."""
    doc = _logged()
    assert FIXTURE.stat().st_size < 100_000 and len(doc["requests"]) > 30
    picks = {}
    for galaxy in ("milky_way/on", "ngc_4414/on"):  # the table is computed for the pick; the off layer asks the same
        template = galaxy.split("/")[0]
        t = _template(service, template)
        q = viewer_query(t, service.handle("/api/inputs", {"model": t["model"]}).json(), "on")
        picks[template] = pick_threshold(service.handle("/api/bright", q | {"table": "1", "precision": "f4"}).frame())
    assert bundle.js_number(picks["milky_way"]) == "35481.33892335753"
    assert bundle.js_number(picks["ngc_4414"]) == "25118.86431509577"
    planned: dict[str, set[str]] = {}
    for galaxy in doc["prefixes"]:
        template, layer = galaxy.split("/")
        entries = plan(template, layer, service, l_min=picks[template])
        planned[galaxy] = {route + "?" + bundle.js_query(query) for route, query in entries}
        assert planned[galaxy] and len(planned[galaxy]) == len(entries), "no request planned twice"
        prefix = doc["prefixes"][galaxy]
        inputs = [q for q in planned[galaxy] if "template=" in q]
        assert all(q.split("?", 1)[1].startswith(prefix + "&") for q in inputs), galaxy
    anywhere = set().union(*planned.values())
    for r in doc["requests"]:
        sent = r["path"] + "?" + _sent(doc, r)
        pool = anywhere if r["galaxy"] is None else planned[r["galaxy"]]
        assert sent in pool, sent[:300]


def test_the_plan_names_every_group_and_only_routes_that_exist(service):
    entries = plan(TEMPLATE, "on", service, l_min=35481.33892335753)
    planned = {route for route, _ in entries}
    assert planned <= {r.path for r in ROUTES} and not planned & bundle.NEVER
    assert planned == {"/api/stages", "/api/fields", "/api/inputs", "/api/templates", "/api/blackbody", "/api/arrays",
                       "/api/render", "/api/clouds", "/api/clusters", "/api/remnants", "/api/region", "/api/bright"}
    keys = [bundle.key(service, r, q) for r, q in entries]
    assert None not in keys and len(keys) == len(set(keys)), "every entry has a key, and no two share one"
    sets = filter_sets()
    tiles = [q for r, q in entries if r == "/api/bright" and "cells" in q]
    assert len(tiles) == len(sets) and all(q["cells"].split(",") == [str(c) for c in range(1024)] for q in tiles)
    renders = [q for r, q in entries if r == "/api/render"]
    assert sum("only" not in q for q in renders) == len(sets) == sum(q.get("only") == "remainder" for q in renders)
    arrays = [q["fields"] for r, q in entries if r == "/api/arrays"]
    assert "bulge_scale_radius" in arrays and "disc_surface_density,disc_radial_spread,merger_delivery,disc_heating," \
        "halo_potential,halo_potential_midplane" in arrays and len(arrays) > 10
    off = plan(TEMPLATE, "off", service, only=("arrays", "census"))
    assert all(q["layer"] == "off" for _, q in off) and [q["fields"] for r, q in off if r == "/api/arrays"] == ["bulge_scale_radius"]
    with pytest.raises(SystemExit):
        plan(TEMPLATE, "on", service, only=("pictures",))
    assert set(GROUPS) == {"metadata", "arrays", "render", "census", "bright"}
