"""Template bundles (S72, BUILD_IV Phase W2): the canonical key, the reader under the model's hash, the export's plan.

A bundle answers a request only when its canonical form is an entry's and the bundle was built from the serving
model's own bytes; then it runs nothing (D4) and sends the bytes the model sent (the export's --check asserts that
over a whole manifest; here a small hand-made bundle asserts it entry by entry). Everything else is computed.
"""

from __future__ import annotations

import json
import shutil
import threading
import urllib.parse
import urllib.request

import pytest

from export_template import GROUPS, filter_sets, plan, viewer_query
from galaxy.api import bundle
from galaxy.api import http as api_http
from galaxy.api.service import ROUTES, ApiError, Response, Service
from galaxy.api.version import MODEL, content_hash

RGB = filter_sets()["rgb"]
TEMPLATE = "milky_way"


# --- the canonical key ------------------------------------------------------------------------------------------------

def test_the_key_does_not_depend_on_the_order_or_the_form_of_the_query():
    a = bundle.canonical("/api/arrays", "template=milky_way&fields=a&layer=off")
    assert a == bundle.canonical("/api/arrays", "layer=off&fields=a&template=milky_way")
    assert a == bundle.canonical("/api/arrays/", {"fields": ["a"], "template": "milky_way", "layer": "off"})
    assert a == bundle.canonical("/api/arrays", "?fields=a&layer=off&template=milky_way")
    assert a == "/api/arrays?fields=a&layer=off&template=milky_way"
    assert bundle.key("/api/arrays", "fields=a&template=milky_way&layer=off") == bundle.key("/api/arrays", a.split("?", 1)[1])
    # Values are never defaulted or coerced: another spelling is another request, and a miss is computed.
    assert bundle.key("/api/arrays", "fields=a&white=6500") != bundle.key("/api/arrays", "fields=a&white=6500.0")
    assert bundle.key("/api/arrays", "fields=a") != bundle.key("/api/arrays", "fields=a&model=azimuthal")
    # The encoding is the canonical one whatever the request's was: '+' and %20 are both a space.
    assert bundle.canonical("/api/region", "about=a+b") == bundle.canonical("/api/region", "about=a%20b")


def test_layer_absent_is_layer_on_where_the_route_takes_the_switch_and_nowhere_else():
    assert bundle.canonical("/api/render", "white=6500") == bundle.canonical("/api/render", "white=6500&layer=on")
    assert bundle.canonical("/api/render", "white=6500&layer=off") != bundle.canonical("/api/render", "white=6500")
    assert bundle.canonical("/api/render", "layer=OFF").endswith("layer=OFF"), "any other value is left as given"
    layered = {r.path for r in ROUTES if "layer" in r.params}
    assert "/api/stages" not in layered and "/api/blackbody" not in layered
    assert bundle.canonical("/api/stages", "model=azimuthal") == "/api/stages?model=azimuthal"
    assert bundle.canonical("/api/blackbody", "white=6500") == "/api/blackbody?white=6500"


def test_filters_are_keyed_as_json_not_as_spelled():
    js = bundle.js_json(RGB)  # what the viewer's JSON.stringify sends
    assert " " not in js and js.startswith('[{"name":"R","shape":"gaussian","centre":6498.09')
    spaced = json.dumps(RGB)  # Python's spacing
    shuffled = json.dumps([dict(reversed(list(c.items()))) for c in RGB], indent=2)
    keys = {bundle.key("/api/render", {"filters": f, "white": "6500"}) for f in (js, spaced, shuffled)}
    assert len(keys) == 1
    assert bundle.canonical("/api/render", {"filters": "[not json"}).count("%5Bnot%20json") == 1


def test_numbers_are_written_as_a_browser_writes_them():
    cases = {7.0: "7", 1.1e12: "1100000000000", 0.0173: "0.0173", 1e-7: "1e-7", 1e-6: "0.000001", 1.5e16: "15000000000000000",
             1e21: "1e+21", 6.283185307179586: "6.283185307179586", 2238.7211385683404: "2238.7211385683404", 0: "0", -3.5: "-3.5",
             4414: "4414", 609546153006.4983: "609546153006.4983"}
    for value, written in cases.items():
        assert bundle.js_number(value) == written, value
    assert bundle.js_json([{"a": 1.0, "b": "x☉"}, None, True]) == '[{"a":1,"b":"x☉"},null,true]'
    assert bundle.js_value([1.0, 2]) == "1,2"


# --- a small bundle, exported and read back ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def service():
    return Service()


@pytest.fixture(scope="module")
def base(service):
    templates = {t["name"]: t for t in service.handle("/api/templates").json()["templates"]}
    t = templates[TEMPLATE]
    return viewer_query(t, service.handle("/api/inputs", {"model": t["model"]}).json(), "on")


@pytest.fixture(scope="module")
def small(service, base):
    """Six small entries in the viewer's spelling, layer absent (on): metadata, a one-stage array, the blackbody, a
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
    for (route, query), (_, _, r) in zip(small, answers):
        assert r.status == 200, (route, r.body[:200])
    manifest = bundle.write(root, TEMPLATE, "on", service.model_hash, answers)
    return root, manifest, {bundle.key(route, query): r for route, query, r in answers}


def test_a_bundle_answers_each_entry_byte_identical_and_runs_nothing(exported, small):
    root, manifest, live = exported
    served = Service(bundles=root)
    assert len(served.bundles) == len(small) == len(manifest["entries"])
    for route, query in small:
        got = served.handle(route, query)
        want = live[bundle.key(route, query)]
        assert got.source == "bundle" and got.stages == () and got.status == 200, route
        assert got.body == want.body and got.media == want.media, route
    # D4: a hit touched no stage and cached no galaxy, no cell and no bright cell (ruling 11: the caches are for misses).
    assert served._cache == {} and len(served.cells._cells) == 0 and len(served.bright._cells) == 0
    assert len(served._bright_galaxies) == 0


def test_layer_absent_and_layer_on_are_one_entry(exported, base):
    root, _, live = exported
    served = Service(bundles=root)
    query = base | {"fields": "halo_virial_mass"}
    on = served.handle("/api/arrays", query | {"layer": "on"})
    absent = served.handle("/api/arrays", query)
    assert on.source == absent.source == "bundle" and on.body == absent.body
    assert on.body == live[bundle.key("/api/arrays", query)].body
    off = served.handle("/api/arrays", query | {"layer": "off"})
    assert off.source == "model" and off.stages, "layer=off is another galaxy and no entry of this bundle"


def test_a_request_outside_the_bundle_is_computed(exported):
    root, _, _ = exported
    served = Service(bundles=root)
    got = served.handle("/api/arrays", {"template": TEMPLATE, "fields": "halo_virial_mass"})
    assert got.ok and got.source == "model" and got.stages == ("halo",)
    assert served.handle("/api/fields", {"model": "azimuthal"}).source == "model"
    assert served.handle("/api/nope").status == 404


def test_version_and_the_index_are_never_answered_from_a_bundle(service, tmp_path):
    fake = Response(200, "application/json", b'{"stale": true}')
    bundle.write(tmp_path, TEMPLATE, "on", service.model_hash, [("/api/version", {}, fake), ("/api", {}, fake)])
    served = Service(bundles=tmp_path)
    assert len(served.bundles) == 0, "listed in the manifest, never indexed"
    for route in ("/api/version", "/api"):
        got = served.handle(route)
        assert got.source == "model" and b"stale" not in got.body
    assert served.handle("/api/version").json()["model"]["hash"] == served.model_hash


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


def test_the_manifest_is_the_files(exported):
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
        assert bundle.key(e["route"], e["query"]) == e["key"]
        assert e["route"] + "?" + e["query"] == bundle.canonical(e["route"], e["query"])
    assert [e["stages"] for e in manifest["entries"] if e["route"] == "/api/stages"] == [[]]
    assert any(e["stages"] for e in manifest["entries"] if e["route"] == "/api/render")


def test_a_damaged_bundle_is_refused(exported, tmp_path):
    root, manifest, _ = exported
    copy = tmp_path / "bundles"
    shutil.copytree(root, copy)
    first = copy / TEMPLATE / "on" / bundle.ENTRIES / manifest["entries"][0]["key"]
    first.write_bytes(first.read_bytes() + b"x")
    with pytest.raises(bundle.BundleError, match="the manifest says"):
        Service(bundles=copy)


def test_the_server_says_where_an_answer_came_from_and_a_post_is_a_get(exported, small):
    root, _, live = exported
    server = api_http.make_server("127.0.0.1", 0, Service(bundles=root))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}"
    route, query = small[3]  # the blackbody, with the viewer's curves
    try:
        with urllib.request.urlopen(url + route + "?" + urllib.parse.urlencode(query)) as r:
            assert r.headers["X-Galaxy-Source"] == "bundle" and r.headers["X-Galaxy-Stages"] == ""
            assert r.headers["Cache-Control"] == "no-store"
            assert r.read() == live[bundle.key(route, query)].body
        body = urllib.parse.urlencode(query).encode("ascii")
        post = urllib.request.Request(url + route, data=body, method="POST",
                                      headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(post) as r:
            assert r.headers["X-Galaxy-Source"] == "bundle"
            assert r.read() == live[bundle.key(route, query)].body
        with urllib.request.urlopen(url + "/api/version") as r:
            assert r.headers["X-Galaxy-Source"] == "model"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_the_filters_spelling_does_not_move_the_answer(service):
    """The normalisation's claim, asked of the model: the viewer's compact curves and Python's spaced ones are answered
    with the same bytes, so one entry may serve both."""
    a = service.handle("/api/blackbody", {"white": "6500", "filters": bundle.js_json(RGB)})
    b = service.handle("/api/blackbody", {"white": "6500", "filters": json.dumps(RGB, indent=2)})
    assert a.ok and a.body == b.body


# --- the plan ---------------------------------------------------------------------------------------------------------

def test_the_plan_names_every_group_and_only_routes_that_exist(service, exported):
    entries = plan(TEMPLATE, "on", (0,), service)
    routes = {r.path for r in ROUTES}
    planned = {route for route, _ in entries}
    assert planned <= routes
    assert {"/api", "/api/stages", "/api/fields", "/api/inputs", "/api/templates", "/api/blackbody", "/api/arrays",
            "/api/render", "/api/clouds", "/api/clusters", "/api/remnants", "/api/region", "/api/bright"} == planned
    assert "/api/version" not in planned
    keys = [bundle.key(r, q) for r, q in entries]
    assert len(keys) == len(set(keys)), "no request planned twice"
    sets = filter_sets()
    tiles = [q for r, q in entries if r == "/api/bright" and "cells" in q]
    assert len(tiles) == 1024 * len(sets) and all("level" not in q for q in tiles)
    assert len({q["l_min"] for q in tiles}) == 1
    renders = [q for r, q in entries if r == "/api/render"]
    assert sum("only" not in q for q in renders) == len(sets) and sum(q.get("only") == "remainder" for q in renders) == len(sets)
    assert all(q["template"] == TEMPLATE and "layer" not in q for r, q in entries if "template" in q)
    off = plan(TEMPLATE, "off", (0,), service, only=("census",))
    assert all(q["layer"] == "off" for _, q in off)
    assert [r for r, _ in plan(TEMPLATE, "on", (0,), service, only=("region",))] == []
    with pytest.raises(SystemExit):
        plan(TEMPLATE, "on", (0,), service, only=("pictures",))
    assert set(GROUPS) == {"metadata", "arrays", "render", "census", "bright", "region"}
