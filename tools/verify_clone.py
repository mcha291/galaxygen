"""Rule C2: verify a session by cloning the remote into a clean directory and testing there.

The working copy is exactly the path immune to the defect this catches: a file
written but never ``git add``ed passes every test there and is absent for the
next session. So the checks run in a fresh clone, and the working copy is only
asked whether it has anything uncommitted or untracked.

Fixed steps, not an exploration:

 1. working copy: ``git status --porcelain`` is empty
 2. working copy: ``git ls-files --others --exclude-standard`` is empty
 3. ``git clone --branch REF URL DIR``
 4. clone: ``uv run python tools/bootstrap.py``
 5. clone: ``uv run pytest``
 6. clone: ``uv run python -m galaxy.specs``

    uv run python tools/verify_clone.py [--ref main] [--url URL] [--dir DIR] [--skip-worktree-checks]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sh(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def step(n: int, title: str, args: list[str], cwd: Path, expect_empty: bool = False) -> bool:
    r = sh(args, cwd)
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    ok = r.returncode == 0 and (not expect_empty or not out)
    print(f"[{n}] {'ok  ' if ok else 'FAIL'} {title}")
    if not ok or (out and not expect_empty and n >= 5):
        for line in (out.splitlines()[-40:] if out else []):
            print("      " + line)
        for line in (err.splitlines()[-20:] if err else []):
            print("      ! " + line)
    return ok


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", default="main")
    ap.add_argument("--url", default=None, help="remote URL (default: origin of this checkout)")
    ap.add_argument("--dir", default=None, help="clone target (default: a fresh temp dir)")
    ap.add_argument("--skip-worktree-checks", action="store_true")
    a = ap.parse_args(argv)

    url = a.url or sh(["git", "remote", "get-url", "origin"], ROOT).stdout.strip()
    if not url:
        print("no remote URL; pass --url", file=sys.stderr)
        return 2
    target = Path(a.dir) if a.dir else Path(tempfile.mkdtemp(prefix="galaxygen-verify-"))
    clone = target / "clone"

    ok = True
    if not a.skip_worktree_checks:
        ok &= step(1, "git status --porcelain is empty", ["git", "status", "--porcelain"], ROOT, expect_empty=True)
        ok &= step(2, "no untracked files", ["git", "ls-files", "--others", "--exclude-standard"], ROOT, expect_empty=True)
    else:
        print("[1] skip  worktree checks\n[2] skip  worktree checks")
    ok &= step(3, f"clone {url}@{a.ref} -> {clone}", ["git", "clone", "--quiet", "--branch", a.ref, url, str(clone)], target)
    if not clone.exists():
        return 1
    head = sh(["git", "rev-parse", "--short", "HEAD"], clone).stdout.strip()
    print(f"      HEAD {head}")
    ok &= step(4, "bootstrap", ["uv", "run", "python", "tools/bootstrap.py"], clone)
    ok &= step(5, "pytest", ["uv", "run", "pytest"], clone)
    ok &= step(6, "python -m galaxy.specs", ["uv", "run", "python", "-m", "galaxy.specs"], clone)
    print("verify_clone:", "OK" if ok else "FAIL", f"({head} at {clone})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
