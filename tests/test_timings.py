"""tools/timings.py: the cold column says when it carries the interpreter's first seeded draw (debt #37, S12)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from timings import ENDPOINTS, table

TOOL = Path(__file__).resolve().parents[1] / "tools" / "timings.py"


def test_a_metadata_route_does_not_pay_the_first_draw_and_the_table_says_which_do():
    index = next(i for i, e in enumerate(ENDPOINTS) if e.route == "/api" and not e.query)
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--one", str(index)],
        capture_output=True, text=True, check=True, cwd=str(TOOL.parents[1]),
    )
    row = json.loads(proc.stdout.splitlines()[-1])
    assert row["stages"] == [] and row["first_draw_in_cold"] is False
    assert row["probe_s"] > 1e-3  # the probe paid the one-off, so the route's cold number never held it
    text = table([row, {**row, "name": "drawn", "first_draw_in_cold": True, "probe_s": 2e-5}])
    assert "drawn*" in text and "first seeded draw" in text and "debt #37" in text
    assert f"{row['name']} " in text  # the unmarked row keeps its name
