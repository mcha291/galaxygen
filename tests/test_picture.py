"""The React viewer's picture test (T12, BUILD_III Phase 0), from the side that needs no browser.

The pictures are taken by ``frontend/e2e/picture.spec.ts`` on headless Chromium through Playwright and
compared with the committed frames in ``frontend/e2e/frames/``. That run is a development instrument
(BUILD_III section 7, rulings 6 and 10; the precedent is ``tools/shot.py``): nothing in this suite depends
on a browser being installed, and CI has none. What is checked here is what can be checked without one:
the capture list is well formed, every capture has its frame at the stated size and the record beside the
frames describes those very files, and Playwright stays a development tool of the frontend - not a
dependency of the viewer, not imported by it, and unknown to the model.

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

NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
ENTRY_KEYS = {"name", "template", "camera", "mode", "filters", "viewport"}
OPTIONAL_KEYS = {"placeholder"}
CAMERA_KEYS = {"inclination_deg", "azimuth_deg", "radius_kpc"}
MODES = {"field", "stars"}  # the spec's MODE_BUTTON: the Rendering buttons "field" and "star-first"
PLAYWRIGHT = "@playwright/test"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def captures() -> list[dict]:
    return load(E2E / "captures.json")["captures"]


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
    sets = load(FRONTEND / "src" / "galaxy" / "filters.json")["sets"]
    names = [c.get("name") for c in listed["captures"]]
    assert len(names) == len(set(names)) and names, f"capture names repeat or are missing: {names}"
    for c in listed["captures"]:
        assert ENTRY_KEYS <= set(c) <= ENTRY_KEYS | OPTIONAL_KEYS, f"{c.get('name')}: keys {sorted(c)}"
        assert isinstance(c["name"], str) and NAME.fullmatch(c["name"]), f"{c['name']!r} is not a frame's file name"
        # Room for Phase T: a template's name, or null for the default galaxy the viewer lands on.
        assert c["template"] is None or (isinstance(c["template"], str) and c["template"]), c["name"]
        camera = c["camera"]
        assert set(camera) == CAMERA_KEYS, f"{c['name']}: camera keys {sorted(camera)}"
        assert all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in camera.values()), c["name"]
        assert 0 <= camera["inclination_deg"] <= 90, f"{c['name']}: inclination from face-on (0) to edge-on (90)"
        assert 0 <= camera["azimuth_deg"] < 360, c["name"]
        assert camera["radius_kpc"] > 0, c["name"]
        assert c["mode"] in MODES, f"{c['name']}: mode {c['mode']!r}"
        assert c["filters"] in sets, f"{c['name']}: {c['filters']!r} is not a set of filters.json"
        assert isinstance(c["viewport"], int) and not isinstance(c["viewport"], bool) and 256 <= c["viewport"] <= 2048, c["name"]
        if "placeholder" in c:
            assert isinstance(c["placeholder"], str) and c["placeholder"].strip(), c["name"]


def test_the_list_holds_a_face_on_and_an_inclined_camera_in_both_modes():
    """Phase 0's list: the Milky Way goal's camera and NGC 4414's, each in the field and the star-first mode."""
    seen = {("face-on" if c["camera"]["inclination_deg"] == 0 else "inclined", c["mode"]) for c in captures() if c["template"] is None}
    assert seen == {(camera, mode) for camera in ("face-on", "inclined") for mode in MODES}


# --- the committed frames -------------------------------------------------------


def test_every_capture_has_a_frame_of_the_stated_size_and_no_frame_is_unlisted():
    names = {c["name"] for c in captures()}
    for c in captures():
        frame = FRAMES / f"{c['name']}.png"
        assert frame.is_file(), f"{frame.relative_to(ROOT)} is missing: npm --prefix frontend run picture:update"
        assert png_size(frame) == (c["viewport"], c["viewport"]), f"{frame.name} is {png_size(frame)}"
    stray = sorted(p.name for p in FRAMES.iterdir() if p.stem not in names or p.suffix != ".png")
    assert not stray, f"frames with no capture in captures.json: {stray}"


def test_the_frames_can_be_committed_and_the_run_output_cannot():
    """The frames are tracked files; a failed comparison's actual, expected and diff are not."""
    frames = [str((FRAMES / f"{c['name']}.png").relative_to(ROOT).as_posix()) for c in captures()]
    kept = subprocess.run(["git", "check-ignore", *frames, "frontend/e2e/frames.json"], cwd=ROOT, capture_output=True, text=True)
    assert kept.returncode == 1 and not kept.stdout.strip(), f"ignored by git: {kept.stdout}"
    output = subprocess.run(["git", "check-ignore", "frontend/e2e/.output/x.png"], cwd=ROOT, capture_output=True, text=True)
    assert output.returncode == 0, "frontend/e2e/.output is not ignored: a failed run would leave files to commit"


def test_the_record_beside_the_frames_describes_these_files():
    """frames.json is written with the frames: each one's size, bytes and hash, and the renderer that drew it."""
    record = load(E2E / "frames.json")
    listed = captures()
    assert list(record["frames"]) == [c["name"] for c in listed], "frames.json and captures.json list different captures"
    for c in listed:
        entry = record["frames"][c["name"]]
        raw = (E2E / entry["file"]).read_bytes()
        assert entry["file"] == f"frames/{c['name']}.png"
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
    assert f"{len(captures())} passed" in proc.stdout, proc.stdout[-2000:]
