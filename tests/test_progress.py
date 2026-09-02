"""tools/progress.py: the board summary equals its own regeneration."""

from __future__ import annotations

import pytest

import progress

MINI_PLAN = """# Plan

## Status

`░░░░░░` **0 / 3 sessions** · repo initialised: no

| | S | Session | Model | Tag | Closed |
|---|---|---|---|---|---|
| ☑ | 0 | Init | Fable | s00 | 2026-09-02 |
| ◐ | 1 | Halo | Opus | — | — |
| ☐ | 2 | SFH | Opus | — | — |

**Next:** S0. Its prompt is here.

**Open debts:** 9 (`GALAXY_INPUTS.md` §11). **Discharged:** 0.

---
body
"""

MINI_INPUTS = """## 11. Rulings

**Calibration debt register**

1. ~~Discharged thing.~~ **DISCHARGED**
2. Open thing
   continued on a second line.
3. Another open thing.

---
"""


def test_committed_board_agrees_with_itself():
    plan = progress.read(progress.PLAN)
    assert progress.render(plan, progress.read(progress.INPUTS)) == plan


def test_render_synthetic():
    out = progress.render(MINI_PLAN, MINI_INPUTS)
    assert "`███░░░` **1 / 3 sessions** · repo initialised: yes" in out
    assert "**Next:** S1. Its prompt is here." in out
    assert "**Open debts:** 2 (`GALAXY_INPUTS.md` §11). **Discharged:** 1." in out
    assert out.endswith("body\n")
    assert progress.render(out, MINI_INPUTS) == out  # idempotent


def test_all_closed_keeps_next_line():
    plan = MINI_PLAN.replace("| ◐ | 1", "| ☑ | 1").replace("| ☐ | 2", "| ☑ | 2")
    out = progress.render(plan, MINI_INPUTS)
    assert "`██████` **3 / 3 sessions**" in out
    assert "**Next:** S0. Its prompt is here." in out


def test_debt_counts():
    assert progress.debt_counts(MINI_INPUTS) == (2, 1)
    with pytest.raises(progress.BoardError):
        progress.debt_counts("nothing here")


def test_board_errors():
    with pytest.raises(progress.BoardError):
        progress.render("no rows here", MINI_INPUTS)
    with pytest.raises(progress.BoardError):
        progress.render(MINI_PLAN.replace("`░░░░░░` **0 / 3 sessions** · repo initialised: no\n", ""), MINI_INPUTS)


def test_check_and_rewrite_modes(tmp_path, monkeypatch):
    plan = tmp_path / "PLAN.md"
    inputs = tmp_path / "INPUTS.md"
    progress.write(plan, MINI_PLAN)
    progress.write(inputs, MINI_INPUTS)
    monkeypatch.setattr(progress, "PLAN", plan)
    monkeypatch.setattr(progress, "INPUTS", inputs)
    assert progress.main(["--check"]) == 1  # MINI_PLAN's bar is stale on purpose
    assert progress.read(plan) == MINI_PLAN  # --check writes nothing
    assert progress.main([]) == 0
    assert progress.main(["--check"]) == 0
    assert "**1 / 3 sessions**" in progress.read(plan)
