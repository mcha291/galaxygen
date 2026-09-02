"""Regenerate the status-board summary in GALAXY_PLAN.md from the board itself.

Everything on the summary lines is derived, so none of it can drift:

- the progress bar and "N / M sessions" from the ☐ ◐ ☑ column of the board
  (two cells per session: ☑ ``██``, ◐ ``█░``, ☐ ``░░``)
- "repo initialised" from whether S0 has started
- "Next: S<n>" from the first row that is not ☑
- the debt counts from the calibration debt register in GALAXY_INPUTS.md §11
  (struck-through items are discharged)

tests/test_progress.py asserts the committed file equals its own regeneration,
so a board edited by hand without running this is a red test, not a quiet lie.

    uv run python tools/progress.py          # rewrite GALAXY_PLAN.md if needed
    uv run python tools/progress.py --check  # exit 1 if it would change
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "GALAXY_PLAN.md"
INPUTS = ROOT / "GALAXY_INPUTS.md"

ROW = re.compile(r"^\| (☐|◐|☑) \| (\d+) \| ")
BAR = re.compile(r"^`([░█]+)` \*\*(\d+) / (\d+) sessions\*\* · repo initialised: (yes|no)$")
NEXT = re.compile(r"^(\*\*Next:\*\* S)(\d+)(\b.*)$")
DEBTS = re.compile(r"^(\*\*Open debts:\*\* )(\d+)( \(`GALAXY_INPUTS\.md` §11\)\. \*\*Discharged:\*\* )(\d+)(\.)$")
REGISTER_HEAD = "**Calibration debt register**"
ITEM = re.compile(r"^(\d+)\. (~~)?")
CELLS = {"☐": "░░", "◐": "█░", "☑": "██"}


class BoardError(ValueError):
    """The board or the register is not in the shape this tool expects."""


def read(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def board_rows(plan: str) -> list[tuple[str, int]]:
    rows = [(m.group(1), int(m.group(2))) for line in plan.splitlines() if (m := ROW.match(line))]
    if not rows:
        raise BoardError("no status-board rows found in GALAXY_PLAN.md")
    return rows


def debt_counts(inputs: str) -> tuple[int, int]:
    """(open, discharged) from the register; struck-through items are discharged."""
    lines = inputs.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith(REGISTER_HEAD))
    except StopIteration:
        raise BoardError(f"{REGISTER_HEAD!r} not found in GALAXY_INPUTS.md") from None
    total = struck = 0
    for line in lines[start + 1 :]:
        if line.strip() == "---":
            break
        if m := ITEM.match(line):
            total += 1
            struck += bool(m.group(2))
    if total == 0:
        raise BoardError("the debt register has no numbered items")
    return total - struck, struck


def render(plan: str, inputs: str) -> str:
    rows = board_rows(plan)
    closed = sum(1 for s, _ in rows if s == "☑")
    bar = "".join(CELLS[s] for s, _ in rows)
    initialised = "yes" if any(n == 0 and s != "☐" for s, n in rows) else "no"
    remaining = [n for s, n in rows if s != "☑"]
    open_debts, discharged = debt_counts(inputs)

    out: list[str] = []
    seen = {"bar": 0, "next": 0, "debts": 0}
    for line in plan.split("\n"):
        if BAR.match(line):
            seen["bar"] += 1
            line = f"`{bar}` **{closed} / {len(rows)} sessions** · repo initialised: {initialised}"
        elif (m := NEXT.match(line)) and remaining:
            seen["next"] += 1
            line = f"{m.group(1)}{remaining[0]}{m.group(3)}"
        elif m := DEBTS.match(line):
            seen["debts"] += 1
            line = f"{m.group(1)}{open_debts}{m.group(3)}{discharged}{m.group(5)}"
        out.append(line)
    for key, count in seen.items():
        if count != 1 and not (key == "next" and not remaining):
            raise BoardError(f"expected exactly one {key} line in GALAXY_PLAN.md, found {count}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Regenerate the GALAXY_PLAN.md status-board summary.")
    ap.add_argument("--check", action="store_true", help="exit 1 if the board would change; write nothing")
    a = ap.parse_args(argv)
    plan = read(PLAN)
    new = render(plan, read(INPUTS))
    rows = board_rows(new)
    closed = sum(1 for s, _ in rows if s == "☑")
    changed = new != plan
    if a.check:
        print(f"progress: {closed}/{len(rows)} closed; board {'is STALE' if changed else 'agrees'}")
        return 1 if changed else 0
    if changed:
        write(PLAN, new)
    print(f"progress: {closed}/{len(rows)} closed; GALAXY_PLAN.md {'updated' if changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
