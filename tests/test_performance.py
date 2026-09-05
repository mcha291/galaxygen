"""performance: every stage profiled cold, the numbers published, no verdicts."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from galaxy.specs import performance as perf
from galaxy.specs.graph import build


@pytest.fixture(scope="module")
def profiles(prod):
    models, _, _ = prod
    return perf.measure(list(models))


# --- completeness is the only gate --------------------------------------------


def test_every_stage_of_every_model_is_profiled(profiles, prod):
    """Rule B13: a stage nobody measured is the omission rule B2 exists to prevent."""
    models, impls, table = prod
    for m in models:
        expected = [s.id for s in build(m, impls, table).order]
        assert [s.stage for s in profiles[m.name].stages] == expected


def test_an_unprofiled_stage_stops_the_run(profiles, prod):
    models, impls, table = prod
    m = next(iter(models))
    full = profiles[m.name]
    short = perf.Profile(full.model, full.import_s, full.overhead_s, full.stages[:-1], full.cells)
    assert [p.code for p in perf.problems(m, short, impls, table)] == ["unprofiled-stage"]
    assert perf.problems(m, full, impls, table) == []


def test_there_is_no_time_budget(profiles, prod):
    """Rule B6: this module publishes numbers. A slow model is not a failing one."""
    models, impls, table = prod
    m = next(iter(models))
    full = profiles[m.name]
    slow = perf.Profile(
        full.model, full.import_s, full.overhead_s,
        tuple(perf.StageCost(s.model, s.stage, s.slot, s.checkpoint, 1e3, 1e3) for s in full.stages),
        full.cells,
    )
    assert perf.problems(m, slow, impls, table) == []


def test_the_check_agrees_with_the_report(profiles, prod):
    models, impls, table = prod
    assert perf.check(list(models), profiles, impls, table) == []


# --- what was measured --------------------------------------------------------


def test_each_stage_ran_alone(profiles):
    """The number is the stage's, not the pipeline prefix's: profile() asserts ran == (id,)."""
    for p in profiles.values():
        assert len({s.stage for s in p.stages}) == len(p.stages)
        assert all(s.cold_s > 0 and s.warm_s > 0 for s in p.stages)


def test_the_runner_overhead_is_published_not_subtracted(profiles):
    for p in profiles.values():
        assert 0 < p.overhead_s < min(s.cold_s for s in p.stages)


def test_the_first_seeded_draw_is_measured_because_it_lands_on_a_stage(profiles):
    """S10: 8-9 ms of numpy bit-generator setup, billed by the table to whoever draws first."""
    for p in profiles.values():
        one = {o.name: o for o in p.one_offs}["first seeded draw"]
        assert one.ratio > 20, one
        assert "pattern" in one.lands_on
        pattern = {s.stage: s for s in p.stages}["pattern"]
        assert pattern.ratio > 10  # the table shows it, and the one-off line explains it
        assert one.first_s == pytest.approx(pattern.cold_s, rel=0.6)


def test_the_catalogue_cost_is_separated_the_way_debt_61_asks(profiles):
    for p in profiles.values():
        c = p.cells
        assert c is not None and c.cells == 1024
        # 90% of the catalogue does not depend on how many stars are asked for.
        _, stars, _, seconds = c.full
        assert 0 < c.per_star_us * stars * 1e-6 < 0.2 * seconds
        # The part D61 names — paid whether or not anything asks — is the layout.
        assert 0 < c.layout_share < 0.25
        assert c.setup_s + c.layout_s < c.fixed_s  # the rest is drawing in realised cells
        # A region query does not pay for the cells nobody asked about.
        assert c.region_share < 0.1 and c.region_cells == 9


def test_the_sample_sweep_spans_enough_to_fit_a_slope(profiles):
    """The two-point difference this replaced returned a negative cost per star."""
    for p in profiles.values():
        sizes = [n for n, *_ in p.cells.samples]
        assert max(sizes) >= 8 * min(sizes)
        assert p.cells.per_star_us > 0


# --- plumbing -----------------------------------------------------------------


def test_a_profile_survives_the_subprocess_boundary(profiles):
    for p in profiles.values():
        assert perf.Profile.from_json(json.loads(json.dumps(p.to_json()))) == p


def test_the_subprocess_entry_point_prints_one_json_profile():
    proc = subprocess.run(
        [sys.executable, "-m", "galaxy.specs.performance", "--one", "simple"],
        capture_output=True, text=True, cwd=str(perf.ROOT), check=True,
    )
    p = perf.Profile.from_json(json.loads(proc.stdout.splitlines()[-1]))
    assert p.model == "simple" and p.stages and p.cells is not None


def test_the_report_publishes_the_numbers(profiles, prod):
    models, impls, table = prod
    text = perf.report(list(models), profiles, impls, table)
    assert "performance" in text
    for m in models:
        assert f"model {m.name}:" in text
    assert "catalogue (D61)" in text
    assert "paid whether or not anything asks" in text
    assert "one-off, first seeded draw" in text
    assert "runner overhead" in text
