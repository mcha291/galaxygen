"""performance: the profile per stage, both models, cold in a fresh process (rules B2, B6).

What is published, per model:

- **Per-stage seconds, cold and warm.** The runner records what each stage cost
  it (``Outputs.seconds``). This module runs a model once in a *fresh
  interpreter* and then once more in the same one, so the first column is what
  a first request pays and the second is what a cache would be reading (rule
  B2, D67). One subprocess per model, as ``tools/timings.py`` does per endpoint:
  nothing is measured twice in one process.
- **The per-cell catalogue cost D61 left open.** The systems stage builds eight
  seeded streams for every one of its 32 × 32 cells on every run, whether or
  not anything asks for that cell's stars, and D61 priced one ``Generator``
  construction at about 22 µs. Debt #24 discharged the spec ensemble's version
  of the problem (``only=``) and left this one to S10. Here the stage is timed
  at as many stars as there are cells and at the published sample, so the cost
  splits into a per-cell part and a per-star part by arithmetic; and the
  construction of every stream the stage *would* build if every cell realised a
  star is timed on its own, as the stage constructs them, which is the ceiling
  of the per-cell part rather than a recollection of it.

**Publish the number, not the verdict** (rule B6). Nothing here passes or fails
on a timing; the one problem this spec can raise is a profile that could not be
taken. Whether the numbers are acceptable is a judgement someone can disagree
with from the same table.

    uv run python -m galaxy.specs.performance            # the tables
    uv run python -m galaxy.specs.performance --json     # the same numbers as JSON
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections.abc import Iterable, Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any

from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.core.registry import Model, production
from galaxy.specs import Problem, utf8_stdout

ROOT = Path(__file__).resolve().parents[2]

# The streams the systems stage constructs per cell: one for the count in the
# layout, seven for the properties of the stars the cell realises (D60, D61).
CELL_STREAMS: tuple[str, ...] = ("count", "radius", "azimuth", "population", "height", "age", "age_thin", "mass")


def _timed_run(model: Model, grid: GridSpec) -> tuple[Any, float]:
    from galaxy.run import run

    start = time.perf_counter()
    out = run(model, grid=grid)
    return out, time.perf_counter() - start


def catalogue_cost(out: Any, seed: int = 0) -> dict[str, float]:
    """The systems stage's cost split into what every cell pays and what every star pays.

    Timed in this process on the fields ``out`` already holds, so the stage's
    inputs are not rebuilt: the layout alone (one stream per cell), the stage at
    as many stars as cells (the cells the mass shares let realise a star build
    their streams and draw almost nothing), the stage at the published sample,
    and the construction of every stream the stage would build if every cell
    realised a star. The split is arithmetic on the two stage timings; the
    construction time is the ceiling of the per-cell part and says what numpy's
    ``Generator`` alone would cost (D61).
    """
    from galaxy.core import seeds
    from galaxy.stages import systems

    R, t, fields = out.grid.R, out.grid.t, out.fields
    n_cells, sample = systems.CELL_COUNT, systems.CATALOGUE_SAMPLE

    def best(fn, repeats: int = 3) -> float:
        b = float("inf")
        for _ in range(repeats):
            start = time.perf_counter()
            fn()
            b = min(b, time.perf_counter() - start)
        return b

    layout_s = best(lambda: systems.cell_counts(fields["stellar_surface_density"], R, seed, sample))
    one_per_cell_s = best(lambda: systems.materialise(fields, R, t, seed, n_cells))
    sample_s = best(lambda: systems.materialise(fields, R, t, seed, sample))
    streams_s = best(lambda: [seeds.rng(seed, "cell", c, name) for c in range(n_cells) for name in CELL_STREAMS])

    realised = len(systems.cell_counts(fields["stellar_surface_density"], R, seed, sample))
    realised_few = len(systems.cell_counts(fields["stellar_surface_density"], R, seed, n_cells))
    per_star_s = max(sample_s - one_per_cell_s, 0.0) / max(sample - n_cells, 1)
    per_cell_s = max(one_per_cell_s - per_star_s * n_cells, 0.0) / n_cells
    return {
        "cells": float(n_cells),
        "cells_realised_at_sample": float(realised),
        "cells_realised_at_one_per_cell": float(realised_few),
        "streams_per_cell": float(len(CELL_STREAMS)),
        "sample_stars": float(sample),
        "layout_s": layout_s,
        "one_star_per_cell_s": one_per_cell_s,
        "sample_s": sample_s,
        "stage_s": float(out.seconds.get("systems", float("nan"))),
        "streams_s": streams_s,
        "stream_us": 1e6 * streams_s / (n_cells * len(CELL_STREAMS)),
        "per_cell_us": 1e6 * per_cell_s,
        "per_star_us": 1e6 * per_star_s,
        "per_cell_share_at_sample": (per_cell_s * n_cells) / sample_s if sample_s > 0.0 else float("nan"),
        "streams_ceiling_share_of_stage": streams_s / sample_s if sample_s > 0.0 else float("nan"),
    }


def profile(model: Model, grid: GridSpec = DEFAULT, import_s: float = 0.0) -> dict[str, Any]:
    """Every stage of ``model`` timed twice in this process: first run, then again.

    Run this under a fresh interpreter for the first column to mean "cold";
    :func:`profiles` does that and passes what the imports cost it. The
    catalogue split is measured on the warm run's fields, and it is a warm
    measurement by construction: it prices the stage's arithmetic, not the
    allocator's first touch.
    """
    cold, cold_total = _timed_run(model, grid)
    warm, warm_total = _timed_run(model, grid)
    stages = [
        {
            "id": sid,
            "checkpoint": next(st.checkpoint for st in _stages(model) if st.id == sid),
            "cold_s": cold.seconds[sid],
            "warm_s": warm.seconds[sid],
        }
        for sid in cold.ran
    ]
    return {
        "model": model.name,
        "grid": asdict(grid),
        "import_s": import_s,
        "cold_total_s": cold_total,
        "warm_total_s": warm_total,
        "stages": stages,
        "catalogue": catalogue_cost(warm),
    }


def _stages(model: Model):
    _, impls, _ = production()
    return [impls.get(impl_id) for _, impl_id in model.stages]


# What the fresh interpreter runs: the clock starts before anything of this
# package is imported, so the import column is what a cold process pays for
# numpy, the registries and the stages, and not for the last module alone.
CHILD = """
import json, sys, time
started = time.perf_counter()
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.specs import performance, utf8_stdout
import galaxy.run
models, _, _ = production()
import_s = time.perf_counter() - started
utf8_stdout()
print(json.dumps(performance.profile(models.get(sys.argv[1]), GridSpec(**json.loads(sys.argv[2])), import_s)))
"""


def profiles(models: Iterable[Model], grid: GridSpec = DEFAULT) -> tuple[list[dict[str, Any]], list[Problem]]:
    """One fresh interpreter per model (rule B2). A profile that fails is a problem, not a number."""
    rows: list[dict[str, Any]] = []
    problems: list[Problem] = []
    for m in models:
        proc = subprocess.run(
            [sys.executable, "-c", CHILD, m.name, json.dumps(asdict(grid))],
            capture_output=True, text=True, cwd=str(ROOT), check=False, encoding="utf-8", errors="replace",
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            problems.append(Problem(m.name, "profile-failed", f"the fresh process exited {proc.returncode}: {proc.stderr.strip()[-400:]}"))
            continue
        rows.append(json.loads(proc.stdout.splitlines()[-1]))
    return rows, problems


def table(rows: Iterable[Mapping[str, Any]]) -> str:
    lines: list[str] = []
    for r in rows:
        g = r["grid"]
        lines.append(f"  model {r['model']}: grid n_R={g['n_R']}, n_t={g['n_t']}, n_z={g['n_z']}; import {r['import_s']:.3f} s (paid once per process)")
        head = f"    {'stage':<16} {'cp':>2} {'cold s':>9} {'warm s':>9} {'c/w':>6} {'cold %':>7}"
        lines.append(head)
        lines.append("    " + "-" * (len(head) - 4))
        total = r["cold_total_s"]
        for st in r["stages"]:
            ratio = st["cold_s"] / st["warm_s"] if st["warm_s"] > 0.0 else float("inf")
            lines.append(f"    {st['id']:<16} {st['checkpoint']:>2} {st['cold_s']:>9.4f} {st['warm_s']:>9.4f} {ratio:>6.2f} {100.0 * st['cold_s'] / total:>6.1f}%")
        ratio = r["cold_total_s"] / r["warm_total_s"] if r["warm_total_s"] > 0.0 else float("inf")
        lines.append(f"    {'whole model':<16} {'':>2} {r['cold_total_s']:>9.4f} {r['warm_total_s']:>9.4f} {ratio:>6.2f} {'100.0%':>7}")
        c = r["catalogue"]
        lines.append(
            f"    catalogue (D61): {int(c['cells'])} cells x {int(c['streams_per_cell'])} streams; stage {c['stage_s']:.4f} s at "
            f"{int(c['sample_stars'])} stars ({int(c['cells_realised_at_sample'])} cells realised)"
        )
        lines.append(
            f"      layout {c['layout_s']:.4f} s; {int(c['cells'])} stars {c['one_star_per_cell_s']:.4f} s ({int(c['cells_realised_at_one_per_cell'])} cells); "
            f"sample {c['sample_s']:.4f} s -> per cell {c['per_cell_us']:.0f} us, per star {c['per_star_us']:.1f} us; "
            f"per-cell share at the sample {c['per_cell_share_at_sample']:.0%}"
        )
        lines.append(
            f"      every stream of every cell constructed alone: {c['streams_s']:.4f} s ({c['stream_us']:.1f} us each), "
            f"{c['streams_ceiling_share_of_stage']:.0%} of the stage: the ceiling of the per-cell part"
        )
    return "\n".join(lines)


def check(models: Iterable[Model], rows: list[dict[str, Any]] | None = None, problems: list[Problem] | None = None, grid: GridSpec = DEFAULT) -> list[Problem]:
    if rows is None or problems is None:
        rows, problems = profiles(models, grid)
    return list(problems)


def report(models: Iterable[Model], rows: list[dict[str, Any]] | None = None, problems: list[Problem] | None = None, grid: GridSpec = DEFAULT) -> str:
    models = list(models)
    if rows is None or problems is None:
        rows, problems = profiles(models, grid)
    lines = ["performance (cold = first run in a fresh process, warm = the second in the same one)"]
    lines.append(table(rows))
    for p in problems:
        lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Per-stage profile of every model, cold in a fresh process (rule B2).")
    parser.add_argument("--json", action="store_true", help="print the measurements as JSON")
    args = parser.parse_args()
    utf8_stdout()
    models, _, _ = production()
    rows, problems = profiles(list(models))
    if args.json:
        print(json.dumps({"profiles": rows, "problems": [str(p) for p in problems]}, indent=2))
    else:
        print(report(list(models), rows, problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
