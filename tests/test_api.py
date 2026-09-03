"""The API: what it publishes, what it refuses, and how much of the pipeline it runs.

The rule this file exists for is D4 — no endpoint runs more of the pipeline than
its answer requires — and the way it is checked matters as much as that it is.
A timing cannot check it (rule B2: the second call is fast whatever the first
one did), so every response carries the stages it ran and the assertions read
that. Where a route claims to touch no stage at all, the runner is removed from
its path entirely and the route is called again: a check that only observes
"it did not run one this time" is a check on the run, not on the route.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import threading
import urllib.request
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import http as api_http
from galaxy.api import wire
from galaxy.api.service import MAX_STARS, RESERVED, Response, Service, routes
from galaxy.api.version import CLIENT, content_hash
from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, production
from galaxy.stages import systems

ROOT = Path(__file__).resolve().parents[1]
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
METADATA = ("/api", "/api/version", "/api/stages", "/api/fields", "/api/inputs")


def service(**kw):
    """A cold service: no galaxy computed, nothing cached (rule B2)."""
    return Service(grid=SMALL, **kw)


@pytest.fixture
def api():
    return service()


# --- rule D2: one fetch, asserted in CI ---------------------------------------

NETWORK = re.compile(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)\s*[(<]")
SKIP = {".git", "node_modules", ".venv", "__pycache__"}


def strip_js(source: str) -> str:
    """Source with comments and string literals removed, so a mention is not a call."""
    out: list[str] = []
    i, n = 0, len(source)
    while i < n:
        two = source[i : i + 2]
        if two == "//":
            i = source.find("\n", i)
            if i < 0:
                break
        elif two == "/*":
            end = source.find("*/", i + 2)
            i = n if end < 0 else end + 2
        elif source[i] in "\"'`":
            quote, i = source[i], i + 1
            while i < n and source[i] != quote:
                i += 2 if source[i] == "\\" else 1
            i += 1
        else:
            out.append(source[i])
            i += 1
    return "".join(out)


def js_files() -> list[Path]:
    return [p for p in ROOT.rglob("*.js") if not SKIP & set(p.parts)]


def test_exactly_one_fetch_in_the_client_transport():
    """Rule D2. Instrumentation that must be remembered in N places is forgotten in one."""
    files = js_files()
    transport = CLIENT / "transport.js"
    assert transport in files, "the transport S7 imports must exist for this gate to mean anything"
    calls = NETWORK.findall(strip_js(transport.read_text(encoding="utf-8")))
    assert len(calls) == 1 and calls[0].startswith("fetch"), f"transport.js makes {calls}"
    for path in files:
        if path == transport:
            continue
        raw = path.read_text(encoding="utf-8")
        assert "fetch(" not in raw, f"{path.relative_to(ROOT)} names fetch(; the transport holds the only one"
        assert not NETWORK.search(strip_js(raw)), f"{path.relative_to(ROOT)} opens its own connection (rule D2)"


# --- rule D3: a content hash of the viewer's own bytes ------------------------


def test_the_hash_changes_when_the_bytes_change(tmp_path):
    (tmp_path / "a.js").write_text("one", encoding="utf-8")
    first = content_hash(tmp_path)["hash"]
    (tmp_path / "a.js").write_text("two", encoding="utf-8")
    assert content_hash(tmp_path)["hash"] != first, "a changed byte must change the hash"
    (tmp_path / "a.js").write_text("one", encoding="utf-8")
    assert content_hash(tmp_path)["hash"] == first, "content, not mtime: rewriting the same bytes is not news"
    (tmp_path / "a.js").rename(tmp_path / "b.js")
    assert content_hash(tmp_path)["hash"] != first, "the path is part of what is served"
    (tmp_path / "b.js").rename(tmp_path / "a.js")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.js").write_text("", encoding="utf-8")
    assert content_hash(tmp_path)["count"] == 2, "an empty file is still a file that is served"


def test_version_publishes_the_client_hash_and_its_files(api):
    payload = api.handle("/api/version").json()
    assert payload["viewer"] == content_hash(CLIENT)
    assert [f["path"] for f in payload["viewer"]["files"]] == ["package.json", "transport.js"]
    assert payload["wire"] == wire.FORMAT
    assert payload["api"]["count"] >= 5 and "files" not in payload["api"]


# --- rule D4: no endpoint runs more of the pipeline than its answer requires ---


def test_metadata_endpoints_run_no_stages():
    for route in METADATA:
        response = service().handle(route)  # cold every time: a warm one proves nothing
        assert response.status == 200, route
        assert response.stages == (), f"{route} ran {response.stages}"


def test_metadata_endpoints_have_no_runner_in_their_path(monkeypatch):
    """The stronger form: not "it did not run a stage", but "it could not have"."""

    def refuse(*a, **kw):
        raise AssertionError("a metadata endpoint reached the runner (rule D4)")

    monkeypatch.setattr("galaxy.api.service._run", refuse)
    for route in METADATA:
        assert service().handle(route).status == 200, route


def test_arrays_runs_the_closure_above_the_field_and_no_more(model):
    early = service().handle("/api/arrays", {"model": [model.name], "fields": ["halo_virial_mass"]})
    assert early.status == 200
    assert "systems" not in early.stages and "chemistry" not in early.stages
    late = service().handle("/api/arrays", {"model": [model.name], "fields": ["catalogue_size"]})
    assert set(early.stages) < set(late.stages), "the whole pipeline is not the closure above one halo field"


def test_a_region_query_does_not_build_the_galaxy_wide_catalogue(model):
    """The defect D4 names, in the one place it would actually be committed."""
    response = service().handle(
        "/api/region", {"model": [model.name], "r_min": ["7"], "r_max": ["9"], "phi_max": ["0.2"]}
    )
    assert response.status == 200
    assert "systems" not in response.stages, "the region endpoint ran the stage it exists to avoid"
    assert "population" not in response.stages, "nothing in a region query needs the IMF integrals"
    header, arrays = response.frame()
    assert header["cells"]["count"] < header["cells"]["of"] / 8
    assert 0 < header["stars"]["materialised"] < header["stars"]["requested"]


def test_a_second_question_runs_only_the_difference(api):
    """The cache is of work, not of answers: what has not run is not in it."""
    first = api.handle("/api/arrays", "fields=halo_virial_mass")
    second = api.handle("/api/arrays", "fields=catalogue_size")
    assert not set(first.stages) & set(second.stages)
    third = api.handle("/api/arrays", "fields=halo_virial_mass")
    assert third.stages == (), "an answer already computed should cost no stage"
    assert third.frame()[0]["scalars"] == first.frame()[0]["scalars"]
    # A different input vector is a different galaxy and shares nothing.
    other = api.handle("/api/arrays", "fields=halo_virial_mass&halo_mass=9e11")
    assert other.stages == first.stages
    assert other.frame()[0]["scalars"] != first.frame()[0]["scalars"]


# --- what the arrays are ------------------------------------------------------


def test_the_frame_round_trips_and_the_payload_is_aligned(api, model):
    response = api.handle(
        "/api/arrays", {"model": [model.name], "fields": ["stellar_surface_density,stellar_mass_total"]}
    )
    header, arrays = response.frame()
    assert header["format"] == wire.FORMAT and header["endian"] == "little"
    length = int.from_bytes(response.body[4:8], "little")
    assert (8 + length) % wire.ALIGN == 0, "a misaligned payload cannot be read as a typed array"
    from galaxy.run import run

    out = run(model, None, SMALL, only=("stellar_surface_density", "stellar_mass_total"))
    assert np.array_equal(arrays["stellar_surface_density"], out.fields["stellar_surface_density"])
    assert header["scalars"]["stellar_mass_total"] == float(out.fields["stellar_mass_total"])
    assert header["grid"]["axes"]["R"]["n"] == SMALL.n_R
    assert set(header["inputs"]) == set(out.inputs)


def test_a_scalar_with_no_value_is_published_as_null_not_as_a_number():
    """Rule B9. A 6-annulus grid cannot fit a scale length; ``null`` says so, 0.0 would not."""
    coarse = Service(grid=GridSpec(n_R=6, n_t=8, n_z=4, n_phi=6))
    header, _ = coarse.handle("/api/arrays", "fields=thin_disc_scale_length").frame()
    value = header["scalars"]["thin_disc_scale_length"]
    assert value is None or math.isfinite(value)
    assert "NaN" not in json.dumps(header), "NaN is not JSON and a browser will not parse it"


def test_the_catalogue_columns_are_what_the_stage_declares(api, model):
    response = api.handle("/api/region", "r_min=6&r_max=10&phi_max=0.6")
    header, arrays = response.frame()
    declared = [d.name for d in systems.SYSTEMS.publishes if d.kind.domain == "object"]
    assert header["columns"] == declared
    assert set(arrays) == set(declared)
    assert arrays["star_population"].dtype == np.int64, "a category is an integer code, not a float"
    lengths = {len(a) for a in arrays.values()}
    assert lengths == {header["stars"]["materialised"]}


def test_a_region_is_exactly_what_the_full_sweep_puts_there(api):
    """Rule B3: check the region against the whole catalogue, not against itself."""
    from galaxy.run import run

    models, impls, table = production()
    out = run(models.get("simple"), None, SMALL, only=systems.SYSTEMS.requires)
    R, t = out.grid.R, out.grid.t
    whole = systems.materialise(out.fields, R, t, 0, 5000)

    header, arrays = api.handle("/api/region", "r_min=7&r_max=9&phi_min=0&phi_max=0.4&stars=5000").frame()
    cells = tuple(header["cells"]["ids"])
    rings, sectors = systems.cell_edges(R)
    got = set(arrays["star_radius"].tolist())
    assert got and got <= set(whole["star_radius"].tolist()), "the region returned a star the sweep does not have"

    # The other direction needs care about where a star *is* versus which cell it
    # belongs to. Identity is (cell, index); the radius comes from inverting the
    # ring's CDF, which is flat outside the ring and so can place a star up to one
    # R-spacing beyond its own ring's edge. Azimuth carries no such slack — it is
    # (sector + u) x width exactly. So the containment is asserted on radii deeper
    # than one grid spacing inside the window, where no star can be ambiguous.
    margin = out.grid["R"].width
    ring_ids = sorted({c // systems.CELL_SECTORS for c in cells})
    sector_ids = sorted({c % systems.CELL_SECTORS for c in cells})
    interior = (
        (whole["star_radius"] > rings[ring_ids[0]] + margin)
        & (whole["star_radius"] < rings[ring_ids[-1] + 1] - margin)
        & (whole["star_azimuth"] >= sectors[sector_ids[0]])
        & (whole["star_azimuth"] <= sectors[sector_ids[-1] + 1])
    )
    assert interior.sum() > 0, "the window caught nothing; the check would be vacuous"
    assert set(whole["star_radius"][interior].tolist()) <= got


def test_a_bigger_sample_contains_the_smaller_one(api):
    """D60's prefix property, through the endpoint the LOD ladder will climb."""
    window = "r_min=7&r_max=9&phi_min=0&phi_max=0.4&"
    small = api.handle("/api/region", window + "stars=5000").frame()[1]["star_radius"]
    large = api.handle("/api/region", window + "stars=50000").frame()[1]["star_radius"]
    assert len(large) > len(small)
    assert set(small.tolist()) <= set(large.tolist())


# --- what the metadata says ---------------------------------------------------


def test_field_declarations_carry_the_one_rendering_opinion(api, model):
    payload = api.handle("/api/fields", {"model": [model.name]}).json()
    declared = {d.name: d for st in production()[1] for d in st.publishes}
    assert payload["fields"], "no fields published"
    for entry in payload["fields"]:
        decl = declared[entry["name"]]
        assert entry["label"] == decl.label and entry["unit"] == decl.unit
        assert entry["about"] == decl.about and entry["provenance"] == decl.provenance
        if entry["domain"] in ("grid", "object"):
            assert entry["ramp"] is not None, f"{entry['name']} reaches the viewer without a ramp (rule A9)"
        if entry["categorical"]:
            assert entry["ramp"]["kind"] == "palette"
            assert len(entry["ramp"]["colors"]) == len(entry["categories"])
    assert payload["grid"]["axes"]["t"]["hi"] == SMALL.t_max


def test_stages_and_checkpoints_are_the_graph(api, model):
    payload = api.handle("/api/stages", {"model": [model.name]}).json()
    from galaxy.specs import graph

    g = graph.analyse(model, production()[1], INPUTS)
    assert payload["order"] == [s.id for s in g.order]
    listed = [s for cp in payload["checkpoints"] for s in cp["stages"]]
    assert sorted(listed) == sorted(payload["order"]), "a stage belongs to exactly one checkpoint"
    assert [cp["n"] for cp in payload["checkpoints"]] == [1, 2, 3, 4, 5, 6]


def test_inputs_publishes_every_default_and_every_range(api, model):
    payload = api.handle("/api/inputs", {"model": [model.name]}).json()
    assert len(payload["controls"]) == 7 and len(payload["seeds"]) == 4
    for control in payload["controls"]:
        assert control["default"] is not None, f"{control['name']} has no default (rule A5)"
        assert control["lo"] is not None and control["hi"] < math.inf
        assert control["unit"] and control["about"]
    assert all(isinstance(s["default"], int) for s in payload["seeds"])
    events = payload["events"][0]
    assert events["name"] == "mergers" and len(events["default"]) == 2
    assert {"time", "mass_ratio", "gas_fraction", "about"} == set(events["default"][0])


def test_the_api_publishes_no_model_internals(api):
    """Rule D5: declarations, numbers and ramps. Not the constants they were computed from."""
    from galaxy.models.level0 import LEVEL0

    text = b"".join(api.handle(route).body for route in METADATA).decode("utf-8")
    for name in LEVEL0:
        assert not re.search(rf"\b{name}\b", text), f"constant {name} is published; the viewer must not see it"
    assert '"constants"' not in text and "reads_constants" not in text
    # CANARY is named in the canary field's own ``about``, which is a declaration
    # and is published on purpose (rule A8); its value is not.
    assert '"CANARY"' not in text


# --- what it refuses ----------------------------------------------------------


def test_a_control_outside_its_published_range_is_refused(api):
    bad = api.handle("/api/arrays", "fields=halo_virial_mass&halo_mass=1e15")
    assert bad.status == 400 and "range" in bad.json()["error"]
    assert bad.stages == (), "a rejected request must not have run anything"
    assert api.handle("/api/arrays", "fields=halo_virial_mass&halo_mass=big").status == 400
    assert api.handle("/api/arrays", "fields=halo_virial_mass&not_an_input=1").status == 404
    assert api.handle("/api/arrays", "fields=not_a_field").status == 404
    assert api.handle("/api/arrays", "").status == 400
    assert api.handle("/api/nope").status == 404
    assert api.handle("/api/stages", "model=nope").status == 404
    assert api.handle("/api/region", f"stars={MAX_STARS + 1}").status == 400
    assert api.handle("/api/region", "stars=0").status == 400


def test_the_event_list_is_settable_and_validated(api):
    ok = api.handle("/api/arrays", 'fields=last_major_merger_time&mergers=[{"time":5,"mass_ratio":0.3,"gas_fraction":0.4}]')
    assert ok.status == 200
    assert ok.frame()[0]["scalars"]["last_major_merger_time"] == 5.0
    empty = api.handle("/api/arrays", "fields=last_major_merger_time&mergers=[]")
    assert empty.status == 200 and empty.frame()[0]["scalars"]["last_major_merger_time"] == 0.0
    assert api.handle("/api/arrays", "fields=last_major_merger_time&mergers=notjson").status == 400
    assert api.handle("/api/arrays", 'fields=last_major_merger_time&mergers=[{"time":5}]').status == 400
    assert api.handle("/api/arrays", 'fields=last_major_merger_time&mergers=[{"time":5,"mass_ratio":9,"gas_fraction":0.4}]').status == 400


def test_reserved_parameters_cannot_shadow_an_input():
    assert not RESERVED & set(INPUTS), "a reserved parameter would make that input unreachable"
    assert {"model", "fields", "stars"} <= RESERVED


# --- over the socket ----------------------------------------------------------


def test_the_server_answers_and_says_what_it_ran():
    server = api_http.make_server("127.0.0.1", 0, service())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        with urllib.request.urlopen(base + "/api/version") as r:
            assert r.status == 200
            assert r.headers["Cache-Control"] == "no-store"
            assert r.headers["X-Galaxy-Stages"] == ""
            assert json.loads(r.read())["viewer"]["hash"] == content_hash(CLIENT)["hash"]
        with urllib.request.urlopen(base + "/api/arrays?fields=halo_virial_mass") as r:
            assert r.headers["Content-Type"] == wire.MEDIA
            ran = r.headers["X-Galaxy-Stages"].split(",")
            header, _ = wire.decode(r.read())
            assert header["stages"] == ran == ["halo"]
        with pytest.raises(urllib.error.HTTPError) as bad:
            urllib.request.urlopen(base + "/api/nope")
        assert bad.value.status == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


NODE = shutil.which("node")

DRIVER = """
import {{ version, arrays, region, codes }} from "{module}";
const origin = "{origin}";
const v = await version({{ origin }});
const a = await arrays(["stellar_surface_density", "stellar_mass_total"], {{}}, {{ origin }});
const r = await region({{ r_min: 7, r_max: 9, phi_max: 0.4 }}, {{ stars: 5000 }}, {{ origin }});
let refused = null;
try {{
  await arrays(["not_a_field"], {{}}, {{ origin }});
}} catch (e) {{
  refused = [e.status, e.body.error];
}}
console.log(JSON.stringify({{
  viewer: v.viewer.hash,
  stages: a.stages,
  header_stages: a.header.stages,
  profile: Array.from(a.arrays.stellar_surface_density.slice(0, 4)),
  length: a.arrays.stellar_surface_density.length,
  scalar: a.header.scalars.stellar_mass_total,
  stars: r.header.stars.materialised,
  radii: Array.from(r.arrays.star_radius.slice(0, 4)),
  populations: Array.from(codes(r.arrays.star_population).slice(0, 8)),
  refused,
}}));
"""


@pytest.mark.skipif(NODE is None, reason="node is not installed; nothing here can run the browser's path")
def test_the_transport_decodes_what_the_server_sends(tmp_path):
    """Rule B3: the JS decoder is checked by running it, not by a Python twin of it.

    Alignment, endianness, BigInt category codes and the error path are all
    things a reimplementation would get right by construction and the real
    client could still get wrong.
    """
    server = api_http.make_server("127.0.0.1", 0, service())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    origin = f"http://{host}:{port}"
    driver = tmp_path / "drive.mjs"
    driver.write_text(
        DRIVER.format(module=(CLIENT / "transport.js").as_uri(), origin=origin), encoding="utf-8"
    )
    try:
        proc = subprocess.run([NODE, str(driver)], capture_output=True, text=True, timeout=180)
        assert proc.returncode == 0, proc.stderr
        got = json.loads(proc.stdout)

        api = service()
        header, arrays = api.handle("/api/arrays", "fields=stellar_surface_density,stellar_mass_total").frame()
        stars_header, stars = api.handle("/api/region", "r_min=7&r_max=9&phi_max=0.4&stars=5000").frame()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert got["viewer"] == content_hash(CLIENT)["hash"]
    assert got["stages"] == got["header_stages"] == header["stages"]
    assert got["length"] == SMALL.n_R
    assert got["profile"] == arrays["stellar_surface_density"][:4].tolist()
    assert got["scalar"] == header["scalars"]["stellar_mass_total"]
    assert got["stars"] == stars_header["stars"]["materialised"]
    assert got["radii"] == stars["star_radius"][:4].tolist()
    assert got["populations"] == stars["star_population"][:8].tolist()
    assert got["refused"][0] == 404 and "not_a_field" in got["refused"][1]


def test_every_route_has_a_published_timing():
    """Rule B2 is only kept if a new endpoint cannot quietly go unmeasured (B13)."""
    from timings import ENDPOINTS

    measured = {e.route for e in ENDPOINTS}
    assert {r.path for r in routes()} <= measured, "a route with no cold timing"


def test_the_route_table_is_what_the_index_publishes(api):
    listed = api.handle("/api").json()["routes"]
    assert [r["path"] for r in listed] == [r.path for r in routes()]
    assert all(r["about"] for r in listed)


def test_a_response_says_whether_it_is_ok():
    assert Response(200, "application/json", b"{}").ok
    assert not Response(404, "application/json", b"{}").ok
