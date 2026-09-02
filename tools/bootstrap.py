"""Per-clone setup. Every session is a fresh clone (rule C1), so this runs every session.

    uv run python tools/bootstrap.py

- points git at the tracked hooks (rule C2c: the pre-commit token check)
- confirms the environment imports

Idempotent. tests/test_hook.py asserts the hook path is set, so forgetting
this shows up as a red test rather than an unguarded commit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = "tools/hooks"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def main() -> int:
    git("config", "core.hooksPath", HOOKS)
    if git("config", "core.hooksPath") != HOOKS:
        print("bootstrap: failed to set core.hooksPath", file=sys.stderr)
        return 1
    import galaxy.core.registry  # noqa: F401

    print(f"bootstrap: core.hooksPath={HOOKS}; galaxy imports; ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
