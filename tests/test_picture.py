"""The React viewer's picture test (T12, BUILD_III Phase 0), from the side that needs no browser.

The pictures are taken by ``frontend/e2e/picture.spec.ts`` on headless Chromium through Playwright and
compared with the committed files: the frames in ``frontend/e2e/frames/`` and, since S54 (D213 ruling 7),
each template's thumbnail in ``frontend/public/templates/``, which the app's switcher serves. That run is a
development instrument (BUILD_III section 7, rulings 6 and 10; the precedent is ``tools/shot.py``): nothing
in this suite depends on a browser being installed, and CI has none. What is checked here is what can be
checked without one: the capture list is well formed and holds each template in both modes and once as a
thumbnail, every capture has its picture at the stated size where the list says it is, the record beside
the frames describes those very files, the list's cameras and filter sets are the templates' own, and
Playwright stays a development tool of the frontend - not a dependency of the viewer, not imported by it,
and unknown to the model.

The picture run itself is one test, skipped unless ``GALAXYGEN_PICTURE=1``::

    GALAXYGEN_PICTURE=1 uv run pytest tests/test_picture.py
    npm --prefix frontend run picture           # the same run, directly
    npm --prefix frontend run picture:update    # rewrite the frames and frames.json

The frames are display captures, never acceptance rows (C6, D113).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
E2E = FRONTEND / "e2e"
FRAMES = E2E / "frames"
THUMBNAILS = FRONTEND / "public" / "templates"  # where the app serves a template's thumbnail from

TEMPLATE = re.compile(r"[a-z0-9]+(_[a-z0-9]+)*")  # src/workflow/templates.ts NAME: a path segment of its thumbnail
NAME = re.compile(r"[a-z0-9]+(_[a-z0-9]+)*(-[a-z0-9]+)+")  # <template>-<what the picture is>
ENTRY_KEYS = {"name", "template", "camera", "mode", "filters", "viewport", "file"}
OPTIONAL_KEYS = {"pending"}
CAMERA_KEYS = {"inclination_deg", "azimuth_deg", "radius_kpc", "fov_deg"}
MODES = {"field", "stars"}  # the spec's MODE_BUTTON: the Rendering buttons "field" and "star-first"
THUMBNAIL = "thumbnail"  # a thumbnail's capture is named <template>-thumbnail
PLAYWRIGHT = "@playwright/test"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def captures() -> list[dict]:
    return load(E2E / "captures.json")["captures"]


def taken() -> list[dict]:
    """The captures whose picture exists: all of them, but those still marked pending."""
    return [c for c in captures() if "pending" not in c]


def filter_sets() -> dict:
    """The viewer's filter sets: the stand-ins and the named instruments (src/galaxy/filters.ts FILTER_SETS)."""
    galaxy = FRONTEND / "src" / "galaxy"
    return {**load(galaxy / "filters.json")["sets"], **load(galaxy / "instruments.json")["sets"]}


def is_thumbnail(c: dict) -> bool:
    return c["file"].startswith("public/")


def png_size(path: Path) -> tuple[int, int]:
    """A PNG's width and height from its header: the signature, then the IHDR chunk."""
    head = path.read_bytes()[:24]
    assert head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR", f"{path.name} is not a PNG"
    return struct.unpack(">II", head[16:24])


# --- the capture list ---------------------------------------------------------


def test_the_capture_list_is_well_formed():
    listed = load(E2E / "captures.json")
    assert set(listed) == {"about", "fields", "captures"}
    # Every key an entry may carry is explained in the file itself.
    assert set(listed["fields"]) == ENTRY_KEYS | OPTIONAL_KEYS
    sets = filter_sets()
    names = [c.get("name") for c in listed["captures"]]
    assert len(names) == len(set(names)) and names, f"capture names repeat or are missing: {names}"
    files = [c.get("file") for c in listed["captures"]]
    assert len(files) == len(set(files)), f"two captures write one file: {files}"
    for c in listed["captures"]:
        assert ENTRY_KEYS <= set(c) <= ENTRY_KEYS | OPTIONAL_KEYS, f"{c.get('name')}: keys {sorted(c)}"
        # Since S54 every capture names a template (D213 ruling 7): the test chooses it in the viewer's switcher.
        assert isinstance(c["template"], str) and TEMPLATE.fullmatch(c["template"]), f"{c['name']}: template {c['template']!r}"
        assert isinstance(c["name"], str) and NAME.fullmatch(c["name"]), f"{c['name']!r} is not a capture's name"
        assert c["name"].startswith(c["template"] + "-"), f"{c['name']} does not begin with its template, {c['template']}"
        camera = c["camera"]
        assert set(camera) == CAMERA_KEYS, f"{c['name']}: camera keys {sorted(camera)}"
        assert all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in camera.values()), c["name"]
        assert 0 <= camera["inclination_deg"] <= 90, f"{c['name']}: inclination from face-on (0) to edge-on (90)"
        assert 0 <= camera["azimuth_deg"] < 360, c["name"]
        assert camera["radius_kpc"] > 0, c["name"]
        assert 0 < camera["fov_deg"] < 180, f"{c['name']}: a lens is a field of view between 0 and 180 degrees"
        assert c["mode"] in MODES, f"{c['name']}: mode {c['mode']!r}"
        assert c["filters"] in sets, f"{c['name']}: {c['filters']!r} is not one of the viewer's filter sets"
        assert isinstance(c["viewport"], int) and not isinstance(c["viewport"], bool) and 128 <= c["viewport"] <= 2048, c["name"]
        # Where the picture is committed: a frame under its capture's name, or the template's thumbnail where the
        # app serves it from.
        if c["name"] == f"{c['template']}-{THUMBNAIL}":
            assert c["file"] == f"public/templates/{c['template']}.png", f"{c['name']}: {c['file']}"
        else:
            assert c["file"] == f"e2e/frames/{c['name']}.png", f"{c['name']}: {c['file']}"
        if "pending" in c:
            assert isinstance(c["pending"], str) and c["pending"].strip(), c["name"]


def test_the_list_holds_each_template_in_both_modes_and_once_as_a_thumbnail():
    """D213 ruling 7: each template at its own camera, lens and filter set in both modes, and its thumbnail."""
    by_template: dict[str, list[dict]] = {}
    for c in captures():
        by_template.setdefault(c["template"], []).append(c)
    assert {"milky_way", "ngc_4414"} <= set(by_template), f"the list's templates: {sorted(by_template)}"
    for template, listed in by_template.items():
        frames = [c for c in listed if not is_thumbnail(c)]
        thumbnails = [c for c in listed if is_thumbnail(c)]
        assert sorted(c["mode"] for c in frames) == sorted(MODES), f"{template}: frames in modes {[c['mode'] for c in frames]}"
        assert len(thumbnails) == 1, f"{template}: {len(thumbnails)} thumbnails"
        # One template is one camera, one lens and one filter set, whatever the picture's mode and size.
        assert all(c["camera"] == listed[0]["camera"] and c["filters"] == listed[0]["filters"] for c in listed), template
        # A thumbnail is a small render of its own, not a frame scaled down (ruling 7).
        assert thumbnails[0]["viewport"] < min(c["viewport"] for c in frames), template
    # D213 ruling 5, as the list states it: the Milky Way face-on through the 45 degree lens and rgb; NGC 4414 at
    # 55 degrees through a 5 degree lens and the Hubble broadband set.
    milky_way, ngc = by_template["milky_way"][0], by_template["ngc_4414"][0]
    assert (milky_way["camera"]["inclination_deg"], milky_way["camera"]["fov_deg"], milky_way["filters"]) == (0, 45, "rgb")
    assert (ngc["camera"]["inclination_deg"], ngc["camera"]["fov_deg"], ngc["filters"]) == (55, 5, "wfc3")


def test_the_app_serves_a_thumbnail_from_where_the_list_writes_it():
    """The switcher's <img> asks for templates/<name>.png under the app's base: Vite serves public/ from there."""
    source = (FRONTEND / "src" / "workflow" / "templates.ts").read_text(encoding="utf-8")
    assert "return `${base}templates/${name}.png`;" in source, "thumbnailOf no longer serves public/templates/<name>.png"
    for c in taken():
        if is_thumbnail(c):
            assert (THUMBNAILS / f"{c['template']}.png").is_file(), f"{c['name']}: the app would ask for a thumbnail that is not there"


def served_templates() -> dict[str, dict] | None:
    """What this checkout's API answers on `/api/templates`, by name; None where it has no such route (a 404:
    the model before S54's templates). Metadata: no stage runs (rule D4)."""
    from galaxy.api.service import Service

    answer = Service().handle("/api/templates")
    if answer.status == 404:
        return None
    assert answer.status == 200, answer.body[:300]
    return {t["name"]: t for t in json.loads(answer.body)["templates"]}


def test_a_capture_is_pending_only_while_the_api_serves_no_templates():
    """The `pending` mark is for a template the API cannot serve yet (S54: the viewer was built beside the
    model). Once the API serves its templates the mark is refused: the picture is taken, or the list is wrong."""
    marked = [c["name"] for c in captures() if "pending" in c]
    if served_templates() is not None:
        assert not marked, f"/api/templates answers and these captures are still pending: {marked}. Run npm --prefix frontend run picture:update and remove the marks"
    # The default template's pictures never wait: its inputs are the published defaults (D213 ruling 1).
    assert not [name for name in marked if name.startswith("milky_way-")], marked


def test_the_lists_cameras_and_filters_are_the_templates_own():
    """The list states each template's camera, lens and filter set so a picture says what it is of; the source is
    `/api/templates` (the spec holds the two together in the browser, this test without one). Skipped while the
    API has no such route."""
    served = served_templates()
    if served is None:
        pytest.skip("this checkout's API has no /api/templates yet (S54, builder A's)")
    for c in captures():
        assert c["template"] in served, f"{c['name']}: no template {c['template']} among {sorted(served)}"
        template = served[c["template"]]
        assert template["camera"] == c["camera"], f"{c['name']}: the template's camera is {template['camera']}"
        assert template["filters"] == c["filters"], f"{c['name']}: the template's filter set is {template['filters']}"
    # And every template has its pictures: a template added to the model without a thumbnail fails here.
    assert set(served) == {c["template"] for c in captures()}, "a template has no captures in frontend/e2e/captures.json"


# --- the committed frames -------------------------------------------------------


def test_every_capture_has_a_picture_of_the_stated_size_and_no_picture_is_unlisted():
    for c in captures():
        picture = FRONTEND / c["file"]
        if "pending" in c:
            assert not picture.exists(), f"{c['name']} is marked pending and {c['file']} exists: remove the mark"
            continue
        assert picture.is_file(), f"{picture.relative_to(ROOT)} is missing: npm --prefix frontend run picture:update"
        assert png_size(picture) == (c["viewport"], c["viewport"]), f"{picture.name} is {png_size(picture)}"
    listed = {(FRONTEND / c["file"]).resolve() for c in taken()}
    for folder in (FRAMES, THUMBNAILS):
        stray = sorted(p.name for p in folder.iterdir() if p.resolve() not in listed)
        assert not stray, f"{folder.relative_to(ROOT)} holds files no capture in captures.json writes: {stray}"


def test_the_frames_can_be_committed_and_the_run_output_cannot():
    """The frames are tracked files; a failed comparison's actual, expected and diff are not."""
    frames = [f"frontend/{c['file']}" for c in captures()]
    kept = subprocess.run(["git", "check-ignore", *frames, "frontend/e2e/frames.json"], cwd=ROOT, capture_output=True, text=True)
    assert kept.returncode == 1 and not kept.stdout.strip(), f"ignored by git: {kept.stdout}"
    output = subprocess.run(["git", "check-ignore", "frontend/e2e/.output/x.png"], cwd=ROOT, capture_output=True, text=True)
    assert output.returncode == 0, "frontend/e2e/.output is not ignored: a failed run would leave files to commit"


def test_the_record_beside_the_frames_describes_these_files():
    """frames.json is written with the frames: each one's size, bytes and hash, and the renderer that drew it."""
    record = load(E2E / "frames.json")
    listed = taken()
    assert list(record["frames"]) == [c["name"] for c in listed], "frames.json and captures.json list different captures"
    for c in listed:
        entry = record["frames"][c["name"]]
        assert entry["file"] == c["file"] and entry["template"] == c["template"], c["name"]
        raw = (FRONTEND / entry["file"]).read_bytes()
        assert (entry["width"], entry["height"]) == (c["viewport"], c["viewport"])
        assert entry["bytes"] == len(raw), f"{c['name']}: the frame is not the one frames.json was written with"
        assert entry["sha256"] == hashlib.sha256(raw).hexdigest(), f"{c['name']}: the frame is not the one frames.json was written with"
        # Committed frames belong to a renderer: WebGL's UNMASKED_RENDERER string, and the browser's version.
        assert isinstance(entry["renderer"], str) and entry["renderer"].strip(), c["name"]
        assert re.fullmatch(r"chromium \d+(\.\d+)+", entry["browser"]), entry["browser"]
    package = load(FRONTEND / "package.json")
    assert record["playwright"] == package["devDependencies"][PLAYWRIGHT], "the frames were written by another Playwright"
    # The tolerance the frames were written under is the one the spec compares with.
    settings = (E2E / "settings.ts").read_text(encoding="utf-8")
    stated = re.search(r"TOLERANCE = \{ threshold: ([\d.]+), maxDiffPixelRatio: ([\d.]+) \}", settings)
    assert stated, "e2e/settings.ts no longer states TOLERANCE on one line"
    assert record["tolerance"] == {"threshold": float(stated[1]), "maxDiffPixelRatio": float(stated[2])}
    assert 0 < record["tolerance"]["threshold"] <= 0.05 and 0 < record["tolerance"]["maxDiffPixelRatio"] <= 0.01


# --- Playwright is a development tool, and only the frontend's ---------------------


def test_playwright_is_a_dev_dependency_pinned_to_one_version():
    """Ruling 10: development-only. Pinned exactly, because a Playwright version names one Chromium build."""
    package = load(FRONTEND / "package.json")
    assert not [name for name in package["dependencies"] if "playwright" in name.lower()]
    assert re.fullmatch(r"\d+\.\d+\.\d+", package["devDependencies"][PLAYWRIGHT]), "pin @playwright/test to an exact version"
    lock = load(FRONTEND / "package-lock.json")["packages"]
    assert PLAYWRIGHT not in lock[""].get("dependencies", {})
    assert lock[""]["devDependencies"][PLAYWRIGHT] == package["devDependencies"][PLAYWRIGHT]
    installed = {name: entry for name, entry in lock.items() if "playwright" in name.lower()}
    assert f"node_modules/{PLAYWRIGHT}" in installed
    for name, entry in installed.items():
        assert entry.get("dev") is True, f"{name} is installed for production"
    for script in ("picture", "picture:update"):
        assert "playwright test" in package["scripts"][script]
    assert "--update-snapshots" in package["scripts"]["picture:update"] and "--update-snapshots" not in package["scripts"]["picture"]


def sources(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in suffixes and "node_modules" not in p.parts)


def test_nothing_the_viewer_ships_knows_of_playwright():
    """The viewer's sources neither import it nor name it: the hook on `window` is the whole of the contact."""
    files = sources(FRONTEND / "src", (".ts", ".tsx", ".js", ".mjs", ".json", ".css", ".html"))
    assert len(files) > 50, "frontend/src was not found where it was"
    named = [str(p.relative_to(ROOT)) for p in files if "playwright" in p.read_text(encoding="utf-8").lower()]
    assert not named, f"the viewer's sources name Playwright: {named}"
    # And vitest does not pick the specs up, nor Playwright the unit tests: the two runners are told apart by name.
    assert 'include: ["src/**/*.test.ts"]' in (FRONTEND / "vite.config.ts").read_text(encoding="utf-8")
    specs = sorted(p.name for p in E2E.glob("*.ts") if p.name.endswith((".spec.ts", ".test.ts")))
    assert specs and all(name.endswith(".spec.ts") for name in specs), specs


def test_the_model_does_not_reference_playwright():
    """BUILD_III Phase 0: neither development tool is imported by model/galaxy/."""
    files = sources(ROOT / "model" / "galaxy", (".py", ".json", ".toml", ".txt", ".md"))
    assert len(files) > 50, "model/galaxy was not found where it was"
    named = [str(p.relative_to(ROOT)) for p in files if "playwright" in p.read_text(encoding="utf-8", errors="replace").lower()]
    assert not named, f"the model names Playwright: {named}"
    assert "playwright" not in (ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()


# --- the picture run, only when asked for -------------------------------------------


@pytest.mark.skipif(
    os.environ.get("GALAXYGEN_PICTURE") != "1",
    reason="the picture test needs headless Chromium (a development tool): set GALAXYGEN_PICTURE=1 to run "
    "`npm --prefix frontend run picture` from here, or run that command directly",
)
def test_the_viewer_draws_the_committed_frames():
    """The real run: build the viewer, serve it on port 8019, capture each camera and compare with its frame."""
    npm = shutil.which("npm")
    assert npm, "GALAXYGEN_PICTURE=1 but npm is not on PATH"
    proc = subprocess.run([npm, "--prefix", "frontend", "run", "picture"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1500)
    assert proc.returncode == 0, proc.stdout[-6000:] + proc.stderr[-2000:]
    assert f"{len(taken())} passed" in proc.stdout, proc.stdout[-2000:]
