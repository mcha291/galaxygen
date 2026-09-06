"""performance: the runner's clock, the in-process profile, the fresh-process one, the catalogue split (S10).

The seconds themselves are readings of this machine and are not asserted; what
is asserted is that the instrument reports what ran, that the split is the
arithmetic it claims, and that a profile which cannot be taken is a problem
rather than a missing row (rule B9).
"""

from __future__ import annotations

import math

import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.specs import performance
from galaxy.stages import systems
from helpers import TINY, model

SMALL = GridSpec(n_R=64, n_t=50, n_z=6, n_phi=12)


def test_the_runner_records_seconds_for_exactly_what_it_ran(model):
    out = run(model, grid=TINY)
    assert set(out.seconds) == set(out.ran) == set(out.order)
    assert all(s > 0.0 for s in out.seconds.values())
    part = run(model, grid=TINY, only=("bar_pattern_speed",))
    assert set(part.seconds) == set(part.ran) and "systems" not in part.seconds
    rest = run(model, grid=TINY, only=("star_radius",), resume=part)
    assert set(rest.seconds) == set(rest.ran) and not set(rest.seconds) & set(part.seconds)


def test_the_profile_reads_the_runners_clock(prod):
    simple = prod[0].get("simple")
    p = performance.profile(simple, SMALL)
    assert p["model"] == "simple" and p["grid"] == {"n_R": 64, "n_t": 50, "n_z": 6, "n_phi": 12, "R_max": 30.0, "t_max": 13.8, "z_max": 5.0}
    ids = [st["id"] for st in p["stages"]]
    assert ids == list(run(simple, grid=SMALL).ran)
    assert all(st["cold_s"] > 0.0 and st["warm_s"] > 0.0 for st in p["stages"])
    assert sum(st["cold_s"] for st in p["stages"]) <= p["cold_total_s"]
    assert {st["checkpoint"] for st in p["stages"]} == {1, 2, 3, 4, 5, 6}


def test_the_catalogue_cost_is_split_by_arithmetic(prod):
    """D61's open question: what every cell pays and what every star pays, as numbers."""
    out = run(prod[0].get("simple"), grid=SMALL)
    c = performance.catalogue_cost(out)
    assert c["cells"] == systems.CELL_COUNT == 1024 and c["streams_per_cell"] == len(performance.CELL_STREAMS) == 8
    assert c["sample_stars"] == systems.CATALOGUE_SAMPLE
    assert 0 < c["cells_realised_at_sample"] <= c["cells"]
    for key in ("layout_s", "one_star_per_cell_s", "sample_s", "streams_s", "stream_us", "stage_s"):
        assert c[key] > 0.0, key
    assert c["per_cell_us"] >= 0.0 and c["per_star_us"] >= 0.0
    # The split is the arithmetic it says it is.
    per_star_s = max(c["sample_s"] - c["one_star_per_cell_s"], 0.0) / (c["sample_stars"] - c["cells"])
    assert c["per_star_us"] == pytest.approx(1e6 * per_star_s)
    assert c["per_cell_us"] == pytest.approx(1e6 * max(c["one_star_per_cell_s"] - per_star_s * c["cells"], 0.0) / c["cells"])
    assert 0.0 <= c["per_cell_share_at_sample"] <= 1.0
    assert 0.0 < c["streams_ceiling_share_of_stage"] < 5.0 and 0 < c["cells_realised_at_one_per_cell"] <= c["cells"]
    # The layout is one stream per cell, so it costs less than the eight-per-cell construction.
    assert c["layout_s"] < c["streams_s"] * 2.0


def test_profiles_are_taken_in_a_fresh_process_and_reported(prod):
    simple = prod[0].get("simple")
    rows, problems = performance.profiles([simple], SMALL)
    assert problems == [] and len(rows) == 1 and rows[0]["model"] == "simple"
    assert rows[0]["grid"]["n_R"] == 64 and rows[0]["import_s"] > 0.01  # the registries and numpy, in a fresh process
    assert [st["id"] for st in rows[0]["stages"]] == list(run(simple, grid=SMALL).ran)
    text = performance.report([simple], rows, problems)
    assert text.startswith("performance") and "model simple: grid n_R=64" in text
    assert "whole model" in text and "catalogue (D61)" in text and "FAIL" not in text
    assert performance.check([simple], rows, problems) == []


def test_a_profile_that_cannot_be_taken_is_a_problem():
    rows, problems = performance.profiles([model("nope")], TINY)
    assert rows == [] and [p.code for p in problems] == ["profile-failed"] and problems[0].scope == "nope"
    assert "FAIL" in performance.report([model("nope")], rows, problems)
