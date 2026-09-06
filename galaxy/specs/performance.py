"""performance: the profile per stage, cold, for both models, and the per-cell catalogue cost (S10).

    uv run python -m galaxy.specs.performance          # the tables, to paste into DECISIONS.md
    uv run python -m galaxy.specs.performance --json

**Why a fresh process per model** (rule B2). A cache turns a measurement into a
reading of the cache, and here the caches are the interpreter's own: imported
modules, numpy's allocator, a galaxy already resolved. ``tools/timings.py`` and
``tools/scaling.py`` are the pattern — each model is profiled in its own
interpreter, first run, and the same process then runs every stage a second
time so the table can say what a warm one costs and by how much the cold one
was really cold.

**How a stage is isolated.** The runner resumes: ``run(model, only=(one of the
stage's fields,), resume=previous)`` executes exactly that stage on top of the
outputs of the ones before it, and ``Outputs.ran`` says so. The number is the
stage's, not the pipeline's.

**The per-cell cost** (D61). The catalogue stage builds every one of its
``CELL_RINGS × CELL_SECTORS`` cells on every run, whether or not anything asks
for that cell's stars, and D61 priced that at eight ``Generator`` constructions
a cell without ever measuring what a region query actually pays. Measured here:
the whole sample, the cell layout alone, one cell, and the nine-cell sector
``tools/timings.py`` asks the API for, beside the cost of one ``Generator``.

**Publish the number, not the verdict** (rule B6). Nothing here fails on a
timing. What the spec *does* check is structural: every stage of every model
appears in its profile, in that model's order, with a time — a stage nobody
profiled is the omission rule B2 exists to prevent.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from galaxy.core.grids import GridSpec
from galaxy.core.registry import Input, Model, Registry, production
from galaxy.core.stage import Stage
from galaxy.specs import Problem, utf8_stdout

ROOT = Path(__file__).resolve().parents[2]
SECTOR = (7.0, 9.0, 0.0, 0.4)  # the "one sector" region timings.py asks the API for: 9 of 1024 cells
RNG_SAMPLES = 2000


def _nbytes(value: Any) -> int:
    if isinstance(value, np.ndarray):
        return int(value.nbytes)
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    return 8


def profile(model_name: str, grid: GridSpec | None = None) -> dict[str, Any]:
    """Every stage of ``model_name`` timed alone, cold then warm. Run this in a fresh process."""
    start = time.perf_counter()
    from galaxy.run import run
    from galaxy.specs import graph as _graph

    models, impls, table = production()
    imported = time.perf_counter() - start
    model = models.get(model_name)
    order = _graph.build(model, impls, table).order

    def pass_once() -> tuple[list[dict[str, Any]], Any]:
        prev = None
        rows: list[dict[str, Any]] = []
        for st in order:
            probe = st.published_names[0]
            t0 = time.perf_counter()
            out = run(model, grid=grid, only=(probe,), resume=prev, impls=impls, table=table)
            seconds = time.perf_counter() - t0
            if out.ran != (st.id,):
                raise RuntimeError(f"profiling {st.id!r} ran {out.ran}, not the stage alone")
            rows.append({
                "stage": st.id,
                "slot": st.slot,
                "checkpoint": st.checkpoint,
                "seconds": seconds,
                "bytes": sum(_nbytes(out.fields[n]) for n in st.published_names),
                "fields": len(st.published_names),
            })
            prev = out
        return rows, prev

    cold, out = pass_once()
    warm, _ = pass_once()
    for c, w in zip(cold, warm):
        c["warm_s"] = w["seconds"]
    total = sum(r["seconds"] for r in cold)
    for r in cold:
        r["share"] = r["seconds"] / total if total > 0 else 0.0
    return {
        "model": model_name,
        "grid": repr(out.grid.spec),
        "import_s": imported,
        "total_s": total,
        "warm_total_s": sum(r["seconds"] for r in warm),
        "stages": cold,
        "catalogue": catalogue_cost(out),
    }


def catalogue_cost(out: Any) -> dict[str, Any]:
    """D61's open question: what a cell costs, and what a region query pays instead of the whole."""
    from galaxy.core import seeds
    from galaxy.stages import systems

    fields, R, t = out.fields, out.grid.R, out.grid.t
    seed = int(out.inputs["systems_seed"])
    n = systems.CATALOGUE_SAMPLE

    t0 = time.perf_counter()
    counts = systems.cell_counts(fields["stellar_surface_density"], R, seed, n)
    layout_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    whole = systems.materialise(fields, R, t, seed, n)
    whole_s = time.perf_counter() - t0

    cells = systems.cells_in(R, *SECTOR)
    t0 = time.perf_counter()
    sector = systems.materialise(fields, R, t, seed, n, cells)
    sector_s = time.perf_counter() - t0

    one = (counts[len(counts) // 2][0],)
    t0 = time.perf_counter()
    single = systems.materialise(fields, R, t, seed, n, one)
    one_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    for i in range(RNG_SAMPLES):
        seeds.rng(seed, "cell", i, "probe")
    rng_us = 1e6 * (time.perf_counter() - t0) / RNG_SAMPLES

    realised = len(counts)
    return {
        "cells": systems.CELL_COUNT,
        "cells_realised": realised,
        "stars": int(whole.size),
        "layout_s": layout_s,
        "whole_s": whole_s,
        "per_cell_us": 1e6 * whole_s / realised if realised else float("nan"),
        "per_star_us": 1e6 * whole_s / whole.size if whole.size else float("nan"),
        "sector_cells": len(cells),
        "sector_stars": int(sector.size),
        "sector_s": sector_s,
        "one_cell_stars": int(single.size),
        "one_cell_s": one_s,
        "rng_us": rng_us,
        # D61's estimate: eight constructions a cell, on every cell, on every run.
        "rng_floor_s": 8.0 * rng_us * 1e-6 * realised,
    }


def run_all(models: Iterable[str] = ("simple", "advanced")) -> list[dict[str, Any]]:
    """One fresh interpreter per model. Nothing is measured twice in one process."""
    out: list[dict[str, Any]] = []
    for name in models:
        proc = subprocess.run(
            [sys.executable, "-m", "galaxy.specs.performance", "--one", name],
            capture_output=True, text=True, cwd=str(ROOT), check=False, encoding="utf-8",
        )
        if proc.returncode != 0:
            raise SystemExit(f"profiling {name} failed:\n{proc.stderr}")
        out.append(json.loads(proc.stdout.splitlines()[-1]))
    return out


def check(
    models: Iterable[Model],
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
    profiles: Sequence[Mapping[str, Any]],
) -> list[Problem]:
    """Structural only: every stage of every model has a time, in that model's order."""
    from galaxy.specs import graph as _graph

    by_model = {p["model"]: p for p in profiles}
    out: list[Problem] = []
    for m in models:
        p = by_model.get(m.name)
        if p is None:
            out.append(Problem(m.name, "unprofiled", "no profile for this model"))
            continue
        want = [st.id for st in _graph.build(m, impls, table).order]
        got = [r["stage"] for r in p["stages"]]
        if got != want:
            out.append(Problem(m.name, "unprofiled", f"profiled {got}, the model's order is {want}"))
        for r in p["stages"]:
            if not r["seconds"] > 0.0:
                out.append(Problem(m.name, "unprofiled", f"stage {r['stage']!r} has no positive time"))
    return out


def table(profiles: Sequence[Mapping[str, Any]]) -> str:
    lines: list[str] = []
    for p in profiles:
        head = f"{p['model'] + ' stage':<22} {'cold s':>8} {'warm s':>8} {'c/w':>6} {'share':>6} {'bytes':>12}  cp"
        lines += [head, "-" * len(head)]
        for r in p["stages"]:
            ratio = r["seconds"] / r["warm_s"] if r["warm_s"] > 0 else float("inf")
            lines.append(
                f"{r['stage']:<22} {r['seconds']:>8.4f} {r['warm_s']:>8.4f} {ratio:>6.2f} "
                f"{100 * r['share']:>5.1f}% {r['bytes']:>12,}  {r['checkpoint']}"
            )
        lines.append(
            f"{'total':<22} {p['total_s']:>8.4f} {p['warm_total_s']:>8.4f} "
            f"{p['total_s'] / p['warm_total_s'] if p['warm_total_s'] > 0 else float('inf'):>6.2f}"
        )
        lines.append(f"import + registry {p['import_s']:.3f} s, paid once per process and excluded")
        c = p["catalogue"]
        lines.append(
            f"catalogue (D61): {c['cells_realised']} of {c['cells']} cells realise {c['stars']:,} stars in "
            f"{c['whole_s']:.4f} s = {c['per_cell_us']:.0f} us/cell, {c['per_star_us']:.1f} us/star; "
            f"layout alone {c['layout_s']:.4f} s"
        )
        lines.append(
            f"  one cell ({c['one_cell_stars']} stars) {1e3 * c['one_cell_s']:.2f} ms; sector of "
            f"{c['sector_cells']} cells ({c['sector_stars']} stars) {1e3 * c['sector_s']:.2f} ms; "
            f"a Generator {c['rng_us']:.1f} us, so 8/cell over every cell is {c['rng_floor_s']:.4f} s "
            f"= {100 * c['rng_floor_s'] / c['whole_s']:.0f}% of the whole"
        )
        lines.append("")
    return "\n".join(lines).rstrip()


def report(profiles: Sequence[Mapping[str, Any]]) -> str:
    return "performance\n" + "\n".join("  " + line if line else "" for line in table(profiles).splitlines())


def main() -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Per-stage cold profile for every model (rules B2, B6).")
    parser.add_argument("--json", action="store_true", help="print the measurements as JSON")
    parser.add_argument("--one", help=argparse.SUPPRESS)  # the subprocess entry point
    args = parser.parse_args()
    if args.one is not None:
        print(json.dumps(profile(args.one)))
        return 0
    models, impls, table_ = production()
    profiles = run_all(m.name for m in models)
    print(json.dumps(profiles, indent=2) if args.json else report(profiles))
    bad = check(models, impls, table_, profiles)
    for p in bad:
        print(f"  FAIL {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
