"""performance: every stage timed alone, in order, and the catalogue's per-cell cost measured (rules B2, B6).

The numbers are the spec's to publish, not the suite's to assert: a timing in CI
is a reading of the runner. What is asserted is the mechanics — that a stage is
isolated, that no stage goes unprofiled, that the structural check sees a gap —
and, once, that a fresh process really does produce a profile.
"""

from __future__ import annotations

import pytest

from galaxy.core.grids import GridSpec
from galaxy.specs import graph
from galaxy.specs import performance as P

SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)


@pytest.fixture(scope="module")
def profiles(prod):
    """In-process, on a small grid: the mechanics, not the cold numbers."""
    return [P.profile(m.name, grid=SMALL) for m in prod[0]]


def test_every_stage_is_timed_alone_in_the_models_order(prod, profiles):
    models, impls, table = prod
    for m, p in zip(models, profiles):
        assert p["model"] == m.name and p["import_s"] > 0
        order = [st.id for st in graph.build(m, impls, table).order]
        assert [r["stage"] for r in p["stages"]] == order
        assert all(r["seconds"] > 0 and r["warm_s"] > 0 and r["bytes"] > 0 and r["fields"] > 0 for r in p["stages"])
        assert sum(r["share"] for r in p["stages"]) == pytest.approx(1.0)
        assert p["total_s"] == pytest.approx(sum(r["seconds"] for r in p["stages"]))
        assert p["warm_total_s"] > 0
    assert P.check(models, impls, table, profiles) == []
    # The two models share every stage except chemistry and vertical (S9).
    simple, advanced = ({r["stage"] for r in p["stages"]} for p in profiles)
    assert simple ^ advanced == {"chemistry", "vertical", "chemistry_dtd", "vertical_alpha"}


def test_an_unprofiled_stage_is_a_problem(prod, profiles):
    models, impls, table = prod
    first = profiles[0]
    short = [dict(first, stages=first["stages"][1:])] + profiles[1:]
    assert [p.code for p in P.check(models, impls, table, short)] == ["unprofiled"]
    zero = [dict(first, stages=[dict(first["stages"][0], seconds=0.0)] + first["stages"][1:])] + profiles[1:]
    assert [p.code for p in P.check(models, impls, table, zero)] == ["unprofiled"]
    missing = P.check(models, impls, table, profiles[1:])
    assert [(p.scope, p.code) for p in missing] == [(first["model"], "unprofiled")]


def test_the_catalogue_cost_is_measured_per_cell(profiles):
    """D61 priced a cell at eight Generator constructions and never measured it. Now it is measured."""
    for p in profiles:
        c = p["catalogue"]
        assert 0 < c["cells_realised"] <= c["cells"] == 1024
        assert c["stars"] > 0 and c["whole_s"] > 0 and c["layout_s"] > 0
        assert c["per_cell_us"] > 0 and c["per_star_us"] > 0 and c["rng_us"] > 0 and c["rng_floor_s"] > 0
        # A region pays for its own cells, not the galaxy's (rule D4 at the catalogue's level).
        assert c["sector_cells"] == 9 and 0 < c["sector_stars"] < c["stars"] and c["sector_s"] < c["whole_s"]
        assert 0 < c["one_cell_stars"] <= c["stars"] and c["one_cell_s"] < c["whole_s"]


def test_the_tables_render(profiles):
    text = P.table(profiles)
    assert "simple stage" in text and "advanced stage" in text and "catalogue (D61)" in text
    assert text.count("import + registry") == 2
    assert P.report(profiles).startswith("performance\n  simple stage")


def test_a_fresh_process_profiles_a_model():
    """The spec's own path (rule B2): one interpreter, first run, nothing warm."""
    rows = P.run_all(("simple",))
    assert len(rows) == 1 and rows[0]["model"] == "simple" and rows[0]["import_s"] > 0
    assert len(rows[0]["stages"]) == 12 and rows[0]["catalogue"]["cells"] == 1024
