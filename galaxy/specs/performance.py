"""performance: the profile per stage, both models, cold in a fresh process, and the per-cell catalogue cost.

Rule B6: profile before optimising and publish the profile — the number, not
the verdict. Nothing here fails a run; what it publishes is where the time goes,
so that the next session optimises what is measured rather than what is
suspected (D84 found 1.5 s of a 2.5 s run in one intermediate this way).

**Cold** (rule B2) means the profile is taken in an interpreter that has done
nothing else: ``profile_cold`` runs this module in a subprocess per model, which
imports, builds the registry, and times every stage of one full default run
once. A second run in the same process is reported beside it as the warm
figure, so a stage whose cost is mostly a first-touch effect shows as a ratio.

**Per cell** (D61, debt #24's remainder): the catalogue is materialised for one
cell, nine cells and every cell at the published sample size, in one process,
and the cost per cell is published against the cost of the layout alone
(``cell_counts``). A per-cell cost that is paid whether or not the cell was
asked for is what this table exists to show.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from galaxy.core.registry import Model, production
from galaxy.specs import utf8_stdout

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = 20_000  # the published catalogue size (D61)


def profile(model: Model, **run_kwargs: Any) -> dict[str, float]:
    """Seconds per stage for one default run of ``model``, in this process, in execution order."""
    from galaxy.core.grids import DEFAULT
    from galaxy.core.stage import Context
    from galaxy.run import resolve_inputs
    from galaxy.specs import graph as _graph

    _, impls, table = production()
    g = _graph.build(model, impls, table)
    grid = DEFAULT.build()
    needed = {n for st in g.order for n in st.reads_inputs + st.reads_seeds}
    resolved = resolve_inputs(model, {}, table, needed)
    seeds = {n: v for n, v in resolved.items() if table[n].kind == "seed"}
    constants = {k: c.value for k, c in model.constants.items()}
    fields: dict[str, Any] = {}
    out: dict[str, float] = {}
    for stage in g.order:
        start = time.perf_counter()
        result = stage.compute(Context(stage, grid, resolved, seeds, constants, fields))
        out[stage.id] = time.perf_counter() - start
        fields.update(result)
    return out


def catalogue_cost(model: Model, n_stars: int = SAMPLE) -> dict[str, float]:
    """Seconds to materialise 1, 9 and every cell, and the layout alone, at ``n_stars``."""
    from galaxy.run import run
    from galaxy.stages import systems

    stage = next(st for st in production()[1] if st.slot == "systems")
    out = run(model, only=stage.requires)
    R, t = out.grid.R, out.grid.t
    seed = int(out.inputs["systems_seed"])
    timings: dict[str, float] = {}
    start = time.perf_counter()
    systems.cell_counts(out.fields["stellar_surface_density"], R, seed, n_stars, None)
    timings["layout"] = time.perf_counter() - start
    for label, cells in (("one cell", [300]), ("nine cells", list(range(300, 309))), ("every cell", None)):
        start = time.perf_counter()
        cat = systems.materialise(out.fields, R, t, seed, n_stars, cells)
        timings[label] = time.perf_counter() - start
        timings[label + " (stars)"] = float(cat.size)
    return timings


def measure(model_name: str) -> dict[str, Any]:
    """Cold then warm profile of one model, plus the catalogue cost. Run in a fresh process."""
    start = time.perf_counter()
    models, _, _ = production()
    imported = time.perf_counter() - start
    model = models.get(model_name)
    cold = profile(model)
    warm = profile(model)
    return {"model": model_name, "import_s": imported, "cold": cold, "warm": warm, "catalogue": catalogue_cost(model)}


def profile_cold(models: Iterable[Model]) -> list[dict[str, Any]]:
    """One fresh interpreter per model (rule B2)."""
    rows = []
    for m in models:
        proc = subprocess.run(
            [sys.executable, "-m", "galaxy.specs.performance", "--one", m.name],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"profiling {m.name} failed:\n{proc.stderr[-2000:]}")
        rows.append(json.loads(proc.stdout.splitlines()[-1]))
    return rows


def table(rows: list[dict[str, Any]]) -> str:
    lines = ["performance"]
    for r in rows:
        total_cold, total_warm = sum(r["cold"].values()), sum(r["warm"].values())
        lines.append(f"  model {r['model']}: {total_cold:.3f} s cold, {total_warm:.3f} s warm; import + registry {r['import_s']:.3f} s")
        lines.append(f"    {'stage':<16}{'cold s':>9}{'warm s':>9}{'share':>7}")
        for sid, c in r["cold"].items():
            w = r["warm"][sid]
            lines.append(f"    {sid:<16}{c:>9.4f}{w:>9.4f}{100 * c / total_cold:>6.1f}%")
        cat: Mapping[str, float] = r["catalogue"]
        lines.append(f"    catalogue at {SAMPLE:,} stars: layout {cat['layout']:.4f} s; "
                     f"one cell {cat['one cell']:.4f} s ({int(cat['one cell (stars)'])} stars), "
                     f"nine {cat['nine cells']:.4f} s ({int(cat['nine cells (stars)'])}), "
                     f"every cell {cat['every cell']:.4f} s ({int(cat['every cell (stars)'])})")
    return "\n".join(lines)


def report(models: Iterable[Model]) -> str:
    return table(profile_cold(models))


def main() -> int:
    utf8_stdout()
    if len(sys.argv) > 2 and sys.argv[1] == "--one":
        print(json.dumps(measure(sys.argv[2])))
        return 0
    models, _, _ = production()
    print(report(list(models)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
