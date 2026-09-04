"""performance: the profile is per stage, sums to the run, and the catalogue is priced per cell.

Timings are not asserted — a number in CI is a reading of the runner — but the
shape of the instrument is: every stage of the model's order appears once, the
warm and cold profiles cover the same stages, and the catalogue cost is
measured at one, nine and every cell.
"""

from __future__ import annotations

from galaxy.specs import graph, performance


def test_the_profile_covers_every_stage_in_order(model, prod):
    prof = performance.profile(model)
    g = graph.analyse(model, prod[1], prod[2])
    assert list(prof) == [s.id for s in g.order]
    assert all(v >= 0.0 for v in prof.values()) and sum(prof.values()) > 0.0


def test_the_catalogue_is_priced_per_cell(model):
    cost = performance.catalogue_cost(model, n_stars=2000)
    assert {"layout", "one cell", "nine cells", "every cell"} <= set(cost)
    assert cost["one cell (stars)"] <= cost["nine cells (stars)"] <= cost["every cell (stars)"]
    assert cost["every cell (stars)"] > 0.9 * 2000


def test_the_table_reads_a_measurement():
    rows = [{
        "model": "m", "import_s": 0.01,
        "cold": {"a": 0.5, "b": 0.5}, "warm": {"a": 0.4, "b": 0.4},
        "catalogue": {"layout": 0.01, "one cell": 0.001, "one cell (stars)": 20.0, "nine cells": 0.002,
                      "nine cells (stars)": 200.0, "every cell": 0.1, "every cell (stars)": 20000.0},
    }]
    out = performance.table(rows)
    assert "model m: 1.000 s cold" in out and "50.0%" in out and "every cell 0.1000 s (20000)" in out
