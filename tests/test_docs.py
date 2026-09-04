"""The session documents: caps, tags, and no bare [verified] labels (rules B14, C3, C4, C5)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SESSION_DOCS = ["DECISIONS.md", "LESSONS.md", "RESUMING.md", "BRIEF.md", "README.md", "MANUAL_TODO.md", "AUDIT_RUN1.md"]


def text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_resuming_is_capped_at_120_lines():
    lines = text("RESUMING.md").splitlines()
    assert len(lines) <= 120, f"RESUMING.md has {len(lines)} lines; rule C3 caps it at 120"


def test_brief_is_brief():
    # Rule C4 says ~40 lines; 60 is the enforced ceiling (DECISIONS.md).
    lines = text("BRIEF.md").splitlines()
    assert len(lines) <= 60, f"BRIEF.md has {len(lines)} lines"


def test_lessons_are_tagged_by_stage_type():
    body = text("LESSONS.md")
    header = next((line for line in body.splitlines() if line.startswith("Tags:")), None)
    assert header, "LESSONS.md must open with a 'Tags:' line listing the closed tag set"
    tags = set(re.findall(r"`([a-z]+)`", header))
    assert tags
    bullets = [line for line in body.splitlines() if line.startswith("- ")]
    assert bullets, "no lessons found"
    for line in bullets:
        m = re.match(r"^- ((?:\[[a-z]+\])+) ", line)
        assert m, f"untagged lesson: {line[:60]!r}"
        for tag in re.findall(r"\[([a-z]+)\]", m.group(1)):
            assert tag in tags, f"unknown tag {tag!r} in: {line[:60]!r}"


@pytest.mark.parametrize("name", SESSION_DOCS)
def test_no_bare_verified_labels(name):
    # Rule B14: [verified] needs a citation in the same document; a bare label is a false label.
    assert "[verified]" not in text(name), f"{name} carries a bare [verified] tag"


def test_decisions_are_numbered_sequentially():
    nums = [int(n) for n in re.findall(r"^### D(\d+)\.", text("DECISIONS.md"), flags=re.M)]
    assert nums == list(range(1, len(nums) + 1)) and nums, nums


def test_manual_todo_carries_a_row_for_every_closed_session():
    """Rule C2e: no session tags, so the queue is the only record that a tag is owed.

    The failure this prevents is the one that only shows up at the end, when the
    tags are applied in a batch and one session is quietly missing from it.
    """
    board = (ROOT / "GALAXY_PLAN.md").read_text(encoding="utf-8")
    closed = [int(n) for n in re.findall(r"^\| ☑ \| (\d+) \| ", board, flags=re.M)]
    assert closed, "no closed sessions on the board"
    todo = text("MANUAL_TODO.md")
    for n in closed:
        assert re.search(rf"^\| {n} \| `s{n:02d}` \|", todo, flags=re.M), (
            f"S{n} is ☑ on the board but has no tag row in MANUAL_TODO.md (rule C2e)"
        )


def test_every_queued_tag_has_a_command_to_run():
    todo = text("MANUAL_TODO.md")
    queued = re.findall(r"^\| \d+ \| `(s\d+)` \|.*\| \*\*queued\*\*", todo, flags=re.M)
    assert queued, "no queued tags; if every session is applied, say so here instead"
    for tag in queued:
        assert f"git tag -a {tag} " in todo, f"{tag} is queued but no command is given for it"
