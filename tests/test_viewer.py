"""The viewer: rule D1 as state, rule A9 as colour, rule D5 as what is absent.

The viewer is written as pure modules plus a thin DOM shell, and the reason is
this file. D1's four statements are claims about *state* — where a page load
lands, whether a confirmed control is disabled, what a reopen discards, what a
lock does and does not protect — and state can be asserted. Demonstrated on a
screen, they would be checked by looking, which is rule B3's failure.

Node runs the logic tests (``tests/js/``) against the *live* declarations: the
fixture is dumped from the API rather than written by hand, so a registry change
that the viewer would get wrong fails here instead of in a browser.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from galaxy.api.service import MEDIA_TYPES, Service, routes
from galaxy.api.version import CLIENT
from galaxy.core.cmaps import CMAPS, COLORMAPS, DIVERGING, CmapError, UnknownCmap, cmap
from galaxy.core.grids import GridSpec
from galaxy.stages import systems

ROOT = Path(__file__).resolve().parents[1]
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
NODE = shutil.which("node")


def service(**kw):
    return Service(grid=SMALL, **kw)


# --- the cmap stops, which are what makes rule A9 reachable from a browser ----


def test_every_cmap_in_the_vocabulary_has_usable_stops():
    assert set(COLORMAPS) == set(CMAPS)
    for name, c in COLORMAPS.items():
        assert len(c.stops) >= 2, name
        assert all(re.fullmatch(r"#[0-9a-f]{6}", s) for s in c.stops), name
        assert c.diverging == (name in DIVERGING)
    # A diverging map needs a middle stop or its neutral point is half a stop out.
    for name in DIVERGING:
        assert len(COLORMAPS[name].stops) % 2 == 1
        assert cmap(name).midpoint == COLORMAPS[name].stops[len(COLORMAPS[name].stops) // 2]
    assert cmap("viridis").midpoint is None
    with pytest.raises(UnknownCmap, match="closed cmap vocabulary"):
        cmap("jet")


def test_a_cmap_the_vocabulary_names_but_does_not_define_is_refused():
    """The failure this prevents is a field declaring a ramp nothing can draw."""
    from galaxy.core import cmaps

    saved = dict(cmaps._STOPS)
    try:
        cmaps._STOPS.pop("viridis")
        with pytest.raises(CmapError, match="no stops"):
            cmaps._validate()
        cmaps._STOPS.update(saved)
        cmaps._STOPS["coolwarm"] = cmaps._STOPS["coolwarm"][:-1]  # an even count
        with pytest.raises(CmapError, match="no middle one"):
            cmaps._validate()
    finally:
        cmaps._STOPS.clear()
        cmaps._STOPS.update(saved)
    assert cmaps._validate() == COLORMAPS


def test_the_api_publishes_the_stops_behind_every_ramp_it_publishes(model):
    payload = service().handle("/api/fields", {"model": [model.name]}).json()
    assert set(payload["cmaps"]) == set(CMAPS)
    for name, entry in payload["cmaps"].items():
        assert entry["stops"] == list(COLORMAPS[name].stops)
        assert entry["diverging"] == COLORMAPS[name].diverging
    used = {f["ramp"]["cmap"] for f in payload["fields"] if f["ramp"] and f["ramp"]["kind"] == "ramp"}
    assert used and used <= set(payload["cmaps"]), "a field names a ramp the viewer cannot draw"
    assert set(payload["scales"]) >= {f["ramp"]["scale"] for f in payload["fields"] if f["ramp"] and "scale" in f["ramp"]}


# --- rule A9 and rule D5, as things the client does not contain ---------------


def client_sources() -> list[Path]:
    return sorted(p for p in CLIENT.rglob("*.js") if p.is_file())


def test_the_viewer_holds_no_colour_of_its_own():
    """Rule A9. Every colour the viewer draws data with arrives from a declaration.

    Scanned over the client's JavaScript, which is where value becomes colour.
    Chrome — the page's own background, borders, text — is CSS, and a theme is
    not an opinion about a field.
    """
    for path in client_sources():
        source = path.read_text(encoding="utf-8")
        hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", strip_js(source))
        assert not hexes, f"{path.name} carries colour literals {hexes}; ramps come from /api/fields"
        for name in CMAPS:
            assert not re.search(rf"[\"']{re.escape(name)}[\"']", strip_js(source)), (
                f"{path.name} names the cmap {name!r}; the declaration names it and the API defines it"
            )


def test_the_viewer_persists_nothing():
    """Rule D5, and the other half of "a page load lands on stage one" (D1)."""
    forbidden = ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "caches.open")
    for path in client_sources():
        source = strip_js(path.read_text(encoding="utf-8"))
        for api in forbidden:
            assert api not in source, f"{path.name} uses {api}; the viewer persists no generated object"


def strip_js(source: str) -> str:
    """Source with comments and string literals removed — imported from the D2 gate."""
    from test_api import strip_js as strip

    return strip(source)


# --- the static route ---------------------------------------------------------


def test_the_viewer_is_served_from_its_own_directory_and_nowhere_else():
    s = service()
    assert s.handle("/").status == 200
    assert s.handle("/").media.startswith("text/html")
    assert s.handle("/transport.js").media.startswith("text/javascript")
    assert s.handle("/").stages == (), "serving a file runs no stage"
    # Every attempt to leave the directory is answered the same way: it is not there.
    for escape in ("/../../etc/passwd", "/../version.py", "/etc/passwd", "//etc/passwd", "/./../service.py"):
        assert s.handle(escape).status == 404, escape
    assert s.handle("/nothing.js").status == 404
    assert s.handle("/index.html").body == (CLIENT / "index.html").read_bytes()


def test_only_declared_media_types_are_served(tmp_path):
    (CLIENT / "probe.txt").write_bytes(b"not a type the viewer serves")
    try:
        assert service().handle("/probe.txt").status == 404
        assert ".txt" not in MEDIA_TYPES
    finally:
        (CLIENT / "probe.txt").unlink()


def test_the_viewer_route_is_in_the_route_table_and_the_timings():
    from timings import ENDPOINTS

    assert "/" in {r.path for r in routes()}
    assert "/" in {e.route for e in ENDPOINTS}


def test_the_page_asks_only_for_files_that_exist():
    """A stale import is a blank page and a console message nobody is watching."""
    html = (CLIENT / "index.html").read_text(encoding="utf-8")
    referenced = set(re.findall(r'(?:src|href)="([^"]+)"', html))
    for ref in referenced:
        if ref.startswith(("http", "//", "#", "data:")):
            raise AssertionError(f"index.html reaches outside the viewer for {ref}")
        assert (CLIENT / ref.lstrip("/")).is_file(), f"index.html references {ref}, which is not there"
    for path in client_sources():
        for imported in re.findall(r'from\s+"([^"]+)"', path.read_text(encoding="utf-8")):
            if imported.startswith("node:"):
                continue
            assert (path.parent / imported).resolve().is_file(), f"{path.name} imports {imported}"


# --- the viewer walking the checkpoints, against a live server ----------------

DRIVER = """
import {{ catalogue, confirm, initial, query, reopen, seedsAt, setValue, withPreview }}
  from "{client}/flow.js";
import {{ discScale }} from "{client}/field.js";
import {{ makeRamp }} from "{client}/ramp.js";
import {{ nearest, project }} from "{client}/stars.js";
import {{ arrays, fields, inputs, region, stages }} from "{client}/transport.js";
import * as view from "{client}/view.js";

const origin = "{origin}";
const meta = await fields({{ origin }});
const byName = Object.fromEntries(meta.fields.map((f) => [f.name, f]));
let state = initial(catalogue(await stages({{ origin }}), await inputs({{ origin }})));
const ran = {{}};

// Walk the checkpoints the way the viewer does: draw what is published here,
// confirm, move on. Nothing is asked for that this checkpoint has not made.
for (const cp of state.cat.checkpoints) {{
  const names = view.wanted(meta.fields, cp.n, view.defaultField(meta.fields, cp.n));
  if (names.length) {{
    const frame = await arrays(names, query(state), {{ origin }});
    ran[cp.n] = frame.stages;
    state = withPreview(state, cp.n, frame.header.fields.length);
  }} else {{
    ran[cp.n] = [];
  }}
  state = confirm(state);
}}

// The clickable sample, at the checkpoint that publishes it.
const got = await region({{ r_min: 0, r_max: 30 }}, {{ ...query(state), stars: 5000 }}, {{ origin }});
const size = 400;
const scale = discScale(size, meta.grid.axes.R.hi);
const points = project(got.arrays, scale, size);
const half = size / 2;
let outside = 0;
for (let i = 0; i < points.n; i += 1) {{
  if (Math.hypot(points.sx[i] - half, points.sy[i] - half) > half + 0.5) outside += 1;
}}
const hit = nearest(points.sx[7], points.sy[7], points, 3);

// A field drawn end to end: values in, colour out, from the published stops.
const decl = byName.stellar_surface_density;
const frame = await arrays([decl.name], query(state), {{ origin }});
const ramp = makeRamp(decl, meta.cmaps, frame.arrays[decl.name]);

// Reopening discards, even after all that.
const reopened = reopen(state, 2);

console.log(JSON.stringify({{
  ran,
  columns: Object.keys(got.arrays).sort(),
  stars: got.header.stars.materialised,
  outside,
  hit,
  radius: [...got.arrays.star_radius.slice(0, 3)],
  population: Number(got.arrays.star_population[0]),
  colorAtPeak: ramp.color(ramp.hi),
  colorOfNothing: ramp.color(null),
  rampCmap: ramp.cmap,
  previewsAfterReopen: Object.keys(reopened.previews),
  confirmedAfterReopen: reopened.confirmed,
  seedsAtPattern: seedsAt(state, 4),
  refusedConfirmed: (() => {{ try {{ setValue(reopened, "halo_mass", 1e12); return null; }} catch (e) {{ return e.name; }} }})(),
}}));
"""


@pytest.mark.skipif(NODE is None, reason="node is not installed; the viewer's data path is unchecked here")
def test_the_viewer_walks_the_checkpoints_against_a_live_server(tmp_path):
    """The whole path, in the client's own modules: declarations in, pixels' worth of data out.

    What this adds over the unit tests is the join: that the fields a checkpoint
    publishes can be asked for and drawn, that the region endpoint's columns are
    the ones ``stars.js`` reads, and — the part rule D4 cares about — that the
    viewer asking for checkpoint one's fields does not run the whole pipeline.
    """
    import threading
    import urllib.request

    from galaxy.api import http as api_http

    server = api_http.make_server("127.0.0.1", 0, service())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    driver = tmp_path / "walk.mjs"
    driver.write_text(
        DRIVER.format(client=CLIENT.as_uri(), origin=f"http://{host}:{port}"), encoding="utf-8"
    )
    try:
        proc = subprocess.run([NODE, str(driver)], capture_output=True, text=True, timeout=300)
        assert proc.returncode == 0, proc.stderr[-4000:]
        got = json.loads(proc.stdout)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    # Rule D4, from the client's side: drawing checkpoint one does not build a galaxy.
    assert got["ran"]["1"] and "systems" not in got["ran"]["1"] and "chemistry" not in got["ran"]["1"]
    # Checkpoint 6 draws where giants are possible, which is derived from the
    # chemistry — and stops there. Neither materialiser runs anywhere in the walk:
    # a sample is what a region query is for (D73).
    assert got["ran"]["6"] == ["formation"]
    ran = {stage for got_ran in got["ran"].values() for stage in got_ran}
    assert not ran & {"systems", "planets"}, "drawing a checkpoint materialised a catalogue"

    # The sample, drawn where the disc is.
    assert got["stars"] > 0
    assert got["columns"] == sorted(d.name for d in systems.SYSTEMS.publishes if d.kind.domain == "object")
    assert got["outside"] == 0, "a star was projected outside the grid's own radius"
    assert got["hit"] == 7, "a click on a star selects that star"
    assert all(0 <= r <= 30 for r in got["radius"])
    assert got["population"] in (0, 1)

    # Colour, from the declaration and the published stops.
    from galaxy.core.cmaps import COLORMAPS

    assert got["colorOfNothing"] == [0, 0, 0, 0]
    assert got["colorAtPeak"][:3] == list(
        int(COLORMAPS[got["rampCmap"]].stops[-1][i : i + 2], 16) for i in (1, 3, 5)
    )

    # Rule D1 survives the round trip.
    assert got["previewsAfterReopen"] == ["1"]
    assert got["confirmedAfterReopen"] == 1
    assert got["refusedConfirmed"] == "FlowError"
    assert "pattern_seed" in got["seedsAtPattern"]


# --- the logic, run in node ---------------------------------------------------


@pytest.mark.skipif(NODE is None, reason="node is not installed; the viewer's logic is unchecked here")
def test_the_viewer_logic_holds(tmp_path):
    """``node --test`` over tests/js, against declarations dumped from the API."""
    s = service()
    fixture = tmp_path / "catalogue.json"
    fixture.write_text(
        json.dumps({
            "stages": s.handle("/api/stages").json(),
            "inputs": s.handle("/api/inputs").json(),
            "fields": s.handle("/api/fields").json(),
        }),
        encoding="utf-8",
    )
    files = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "tests" / "js").glob("*.test.mjs"))
    assert files, "no node tests found; an empty run must not look like a passing one"
    proc = subprocess.run(
        [NODE, "--test", *files],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
        env={**os.environ, "GALAXY_FIXTURE": str(fixture)},
    )
    assert proc.returncode == 0, proc.stdout[-4000:] + proc.stderr[-2000:]
    assert "# fail 0" in proc.stdout and "# pass 0\n" not in proc.stdout, proc.stdout[-2000:]


def test_the_screenshot_tool_can_find_a_browser_or_says_which_it_wanted():
    """A development instrument, not a gate: CI has no browser and does not need one."""
    import shot

    browser = shot.find_browser()
    if browser is None:
        pytest.skip("no chromium here; tools/shot.py reports that rather than failing obscurely")
    assert browser.is_file()
    proc = subprocess.run(
        [__import__("sys").executable, str(ROOT / "tools" / "shot.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0 and proc.stdout.strip() == str(browser)
