"""performance: the profile is per stage, sums to the run, and the catalogue is priced per cell.

Timings are not asserted — a number in CI is a reading of the runner — but the
shape of the instrument is: every stage of the model's order appears once, the
warm and cold profiles cover the same stages, and the catalogue cost is
measured at one, nine and every cell.
"""

from __future__ import annotations

import json
import subprocess
import sys

from galaxy.specs import graph, performance


def test_the_profile_covers_every_stage_in_order(model, prod):
    prof = performance.profile(model)
    g = graph.analyse(model, prod[1], prod[2])
    assert list(prof) == [s.id for s in g.order]
    assert all(v >= 0.0 for v in prof.values()) and sum(prof.values()) > 0.0


def test_the_catalogue_is_priced_per_cell(model):
    """Per *cell*, which is what D61 asked and what the numbers say (S21b, debt #67, #68).

    Until S21b this asserted ``per_star_us > 0``, and D115 recorded it failing on a
    negative fitted slope under load. The slope is reproducible to about 9%; the fit's
    own standard error on it is 4-7x that, because the cells that realise a star
    saturate and a straight line in stars is fitted through a curve. The sign of a
    per-star slope is therefore not a fact this instrument can establish, and asserting
    it was a coin weighted by the machine. Both fits are published with their R2 and
    the assertion reads the conditioned one, which is a stronger check and not a
    looser one: if the per-star line ever explained more than the per-cell line, the
    saturation would have gone and this fails.
    """
    cost = performance.catalogue_cost(model, n_stars=2000)
    assert {"layout", "one cell", "nine cells", "every cell"} <= set(cost)
    assert cost["one cell (stars)"] <= cost["nine cells (stars)"] <= cost["every cell (stars)"]
    assert cost["every cell (stars)"] > 0.9 * 2000
    # D61's split (S11): a straight line through the sample sizes; most of the cost is fixed.
    sizes = [int(s[0]) for s in cost["samples"]]
    assert 2000 in sizes and max(sizes) >= 8 * min(sizes)
    # "The stars are the smaller part" — measured at the top of the range rather than
    # through the per-star fit, whose slope is an artefact of the saturation (debt #67):
    # doubling the sample adds a small fraction of what the catalogue already cost.
    top, below = cost["samples"][-1], cost["samples"][-2]
    marginal = (top[2] - below[2]) / (top[1] - below[1])
    assert marginal * top[1] < 0.5 * top[2], (marginal, top)
    assert 0 < cost["cells realised"] <= cost["cells"] == 1024
    # The conditioned fit: a cell costs a few hundred microseconds and the line through
    # the cells explains the timings the line through the stars cannot.
    cells = cost["cells per sample"]
    assert len(cells) == len(cost["samples"]) and cells == sorted(cells)
    assert cells[0] < cells[-1] <= cost["cells"], "the sample range must move the cell count"
    assert cost["per_cell_us"] > 0.0
    assert cost["per_cell_r2"] > cost["per_star_r2"], (cost["per_cell_r2"], cost["per_star_r2"])


def test_the_first_seeded_draw_is_measured_in_a_fresh_interpreter():
    """Debt #37: milliseconds the profile bills to whichever stage draws first (pattern)."""
    proc = subprocess.run(
        [sys.executable, "-m", "galaxy.specs.performance", "--one-off"],
        capture_output=True, text=True, cwd=str(performance.ROOT), check=True,
    )
    one = json.loads(proc.stdout.splitlines()[-1])
    assert one["first_s"] > 5.0 * one["then_s"] > 0.0


def test_the_table_reads_a_measurement():
    rows = [{
        "model": "m", "import_s": 0.01,
        "cold": {"a": 0.5, "b": 0.5}, "warm": {"a": 0.4, "b": 0.4},
        "catalogue": {"layout": 0.01, "one cell": 0.001, "one cell (stars)": 20.0, "nine cells": 0.002,
                      "nine cells (stars)": 200.0, "every cell": 0.1, "every cell (stars)": 20000.0},
    }]
    out = performance.table(rows)
    assert "model m: 1.000 s cold" in out and "50.0%" in out and "every cell 0.1000 s (20000)" in out
    assert "against sample size" not in out and "one-off" not in out  # tolerant of the old shape
    rows[0]["catalogue"].update({
        "samples": [[5000.0, 5000.0, 0.05], [20000.0, 20000.0, 0.08], [40000.0, 40000.0, 0.12]],
        "per_star_us": 2.0, "fixed_s": 0.04, "per_star_r2": 0.6, "cells": 1024.0, "cells realised": 516.0,
    })
    rows[0]["one_off"] = {"first_s": 0.009, "then_s": 0.00002}
    out = performance.table(rows)
    assert "2.00 us per star, 40.0 ms fixed (R2 0.60)" in out
    assert "516 of them realise a star" in out and "one-off, first seeded draw: 9.00 ms" in out
    assert "the conditioned price" not in out  # still tolerant: a row with only the old fit
    rows[0]["catalogue"].update({
        "per_cell_us": 420.0, "per_cell_fixed_s": 0.018, "per_cell_r2": 0.99,
        "cells per sample": [349.0, 630.0, 817.0],
    })
    out = performance.table(rows)
    assert "the conditioned price: 420.0 us per cell realised, 18.0 ms fixed (R2 0.99)" in out
    assert "cells per sample [349, 630, 817]" in out
