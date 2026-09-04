"""Render a page of the viewer to a PNG, so visual work is not done blind.

    uv run python tools/shot.py                       # the viewer, to shot.png
    uv run python tools/shot.py --path /api/version --out version.png
    uv run python tools/shot.py --check               # just find a browser

GALAXY_PLAN.md §5b names S7 the largest quota risk in the build, "visual work
iterates blind". It does not have to: a headless browser renders the page the
same way a real one does, and the result is a file that can be looked at. This
is rule B1 — the instrument before the thing it certifies — applied to a picture.

It is a development tool, not a test. Nothing in the suite depends on a browser
being installed, and CI has none; what CI checks is the logic underneath the
pixels (tests/test_viewer.py), which is why that logic was kept out of the DOM.

The browser is whichever of these exists first: $GALAXY_CHROME, the Playwright
download directory ($PLAYWRIGHT_BROWSERS_PATH or /opt/pw-browsers), then chrome
or chromium on PATH.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BROWSERS = "/opt/pw-browsers"
CANDIDATES = ("chrome", "chromium", "chromium-browser", "google-chrome")


def find_browser() -> Path | None:
    named = os.environ.get("GALAXY_CHROME")
    if named and Path(named).is_file():
        return Path(named)
    root = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or DEFAULT_BROWSERS)
    if root.is_dir():
        # chromium-<build>/chrome-linux/chrome, and the headless shell beside it.
        found = sorted(root.glob("chromium-*/chrome-linux/chrome")) + sorted(root.glob("*/chrome-linux/chrome"))
        if found:
            return found[0]
    for name in CANDIDATES:
        which = shutil.which(name)
        if which:
            return Path(which)
    return None


def shoot(browser: Path, url: str, out: Path, width: int, height: int, budget_ms: int) -> None:
    subprocess.run(
        [
            str(browser), "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={width},{height}",
            f"--virtual-time-budget={budget_ms}",  # let the page finish its requests
            f"--screenshot={out}",
            url,
        ],
        check=True, capture_output=True, text=True, cwd=str(out.parent),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", default="/", help="path to render (default: the viewer)")
    parser.add_argument("--out", default="shot.png", help="where to write the PNG")
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--budget", type=int, default=25000, help="virtual milliseconds to let the page run")
    parser.add_argument("--check", action="store_true", help="report which browser would be used, and stop")
    args = parser.parse_args()

    browser = find_browser()
    if browser is None:
        print("no chromium found; set GALAXY_CHROME to one", file=sys.stderr)
        return 2
    if args.check:
        print(browser)
        return 0

    from galaxy.api.http import make_server
    from galaxy.api.service import Service

    server = make_server("127.0.0.1", 0, Service())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        shoot(browser, f"http://{host}:{port}{args.path}", out, args.width, args.height, args.budget)
    except subprocess.CalledProcessError as e:  # pragma: no cover - a browser that will not start
        print(e.stderr[-2000:], file=sys.stderr)
        return 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print(f"{out} ({out.stat().st_size:,} B) from {browser.name} at {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
