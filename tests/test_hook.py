"""The pre-commit hook refuses token shapes (rule C2c), and is installed here."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "tools" / "hooks" / "pre-commit"

# Assembled at runtime so that this file never itself contains a token shape.
CLASSIC = "gh" + "p_" + "A" * 36
FINE_GRAINED = "github_" + "pat_" + "B" * 22 + "_" + "C" * 30


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    assert git("init", "-q", "-b", "main", cwd=tmp_path).returncode == 0
    for k, v in [
        ("user.email", "t@example.com"),
        ("user.name", "t"),
        ("commit.gpgsign", "false"),
        ("core.hooksPath", HOOK.parent.as_posix()),
    ]:
        git("config", k, v, cwd=tmp_path)
    return tmp_path


def commit(repo: Path, name: str, content: str) -> subprocess.CompletedProcess[str]:
    (repo / name).write_text(content, encoding="utf-8")
    git("add", name, cwd=repo)
    return git("commit", "-q", "-m", "x", cwd=repo)


def test_hook_is_a_posix_sh_script_with_lf():
    raw = HOOK.read_bytes()
    assert raw.startswith(b"#!/bin/sh\n")
    assert b"\r" not in raw


def test_refuses_classic_token(repo):
    r = commit(repo, "a.txt", f"token = {CLASSIC}\n")
    assert r.returncode != 0
    assert "C2c" in r.stderr


def test_refuses_fine_grained_token(repo):
    r = commit(repo, "a.txt", f"export T={FINE_GRAINED}\n")
    assert r.returncode != 0


def test_allows_bare_prefixes_in_prose(repo):
    # RULES.md and GALAXY_PLAN.md mention the prefixes; they must stay committable.
    r = commit(repo, "b.md", "the hook greps staged content for `ghp_` and `github_pat_`\n")
    assert r.returncode == 0, r.stderr


def test_allows_clean_commit(repo):
    assert commit(repo, "c.txt", "hello\n").returncode == 0


def test_token_in_second_commit_is_still_refused(repo):
    assert commit(repo, "c.txt", "hello\n").returncode == 0
    assert commit(repo, "c.txt", f"hello\n{CLASSIC}\n").returncode != 0
    # The refused change stays staged, uncommitted.
    assert git("log", "--oneline", cwd=repo).stdout.count("\n") == 1


@pytest.mark.skipif(bool(os.environ.get("CI")), reason="hooks are not installed in CI")
def test_hooks_path_is_configured_in_this_checkout():
    r = git("config", "core.hooksPath", cwd=ROOT)
    assert r.stdout.strip() == "tools/hooks", "run: uv run python tools/bootstrap.py"
