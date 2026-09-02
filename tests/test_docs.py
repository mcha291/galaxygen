"""The session documents: caps, tags, and no bare [verified] labels (rules B14, C3, C4, C5)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SESSION_DOCS = ["DECISIONS.md", "LESSONS.md", "RESUMING.md", "BRIEF.md", "README.md"]


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
