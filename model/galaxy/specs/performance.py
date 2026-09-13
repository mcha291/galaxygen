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
asked for is what this table exists to show. Since S11 the catalogue is also
timed at several sample sizes and a straight line fitted through them, so the
fixed cost and the marginal cost per star are told apart (``SAMPLES``); a
two-point difference between the whole galaxy and a nine-cell window sits at
one stars-per-cell ratio and is ill-conditioned — it returned a negative cost
per star at S10 (session-10-beta, D96).

**The one-off** (S11, from session-10-beta D97): the first seeded draw of a
fresh interpreter costs milliseconds and every later one microseconds, and a
per-stage profile bills that to whichever stage draws first — which is why that
stage's cold column is hundreds of times its warm one. Which stage that is, the
table now derives from the widest cold/warm ratio rather than naming: it was
``pattern`` in both models until S17 put a seeded stage (``nucleus``) at
checkpoint 1, and the literal was stale the same day (rule B13). It is
measured in its own interpreter (``--one-off``) and published beside the table
rather than paid before the loop, which would tidy the table and destroy the
evidence (rule B6). ``tools/timings.py`` carries the same term, unlabelled (debt #37).
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

ROOT = Path(__file__).resolve().parents[3]
SAMPLE = 20_000  # the published catalogue size (D61)
SAMPLES: tuple[int, ...] = (500, 2_000, 5_000, 10_000, 20_000, 40_000)  # the sizes both fits run over
# Widened at S21b from (5k, 10k, 20k, 40k). Over that range the cells that realise a
# star only run 630 to 817 of 1024, so the per-cell line was extrapolated to zero cells
# from a fifth of its span and read a negative fixed cost. 500 and 2,000 stars cost
# 0.35 s more per model and carry the cell count down to 349, which conditions both
# fits (D115's own lesson: fit over a range wide enough to condition the slope).


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


def catalogue_cost(model: Model, n_stars: int = SAMPLE, samples: tuple[int, ...] = SAMPLES) -> dict[str, Any]:
    """Seconds to materialise 1, 9 and every cell, the layout alone, and the fit against the sample size.

    ``samples`` (plus ``n_stars``) are the sizes the whole catalogue is timed at. Two
    straight lines are fitted through them and both are published with their R²
    (S21b, debt #67): against stars realised, which gives ``per_star_us`` and
    ``fixed_s`` — the pair every record since S11 quotes — and against the cells that
    realise a star, which gives ``per_cell_us``. The second is the conditioned one.
    The cells saturate as the sample grows, so seconds is very nearly a straight line
    in cells (R² ≈ 0.97) and a curve in stars (R² ≈ 0.67); the per-star line is fitted
    through that curve, its residuals keep their sign, and its "fixed" part is not
    fixed — it is the price of however many cells the sample lights up.
    """
    import numpy as np

    from galaxy.run import run
    from galaxy.stages import systems

    stage = next(st for st in production()[1] if st.slot == "systems")
    out = run(model, only=stage.requires)
    R, t = out.grid.R, out.grid.t
    seed = int(out.inputs["systems_seed"])
    churn = float(out.inputs["migration_efficiency"])
    timings: dict[str, float] = {}
    start = time.perf_counter()
    systems.cell_counts(out.fields["stellar_surface_density"], R, seed, n_stars, None)
    timings["layout"] = time.perf_counter() - start
    for label, cells in (("one cell", [300]), ("nine cells", list(range(300, 309))), ("every cell", None)):
        start = time.perf_counter()
        cat = systems.materialise(out.fields, R, t, seed, n_stars, cells, migration=churn)
        timings[label] = time.perf_counter() - start
        timings[label + " (stars)"] = float(cat.size)
    sweep: list[list[float]] = []
    realised_cells: list[float] = []
    for n in sorted({*samples, n_stars}):
        start = time.perf_counter()
        cat = systems.materialise(out.fields, R, t, seed, n, None, migration=churn)
        sweep.append([float(n), float(cat.size), time.perf_counter() - start])
        realised_cells.append(float(len(systems.cell_counts(out.fields["stellar_surface_density"], R, seed, n, None))))
    stars = np.array([s[1] for s in sweep])
    secs = np.array([s[2] for s in sweep])
    cells = np.array(realised_cells)
    timings["samples"] = sweep  # [asked, realised, seconds] per size
    timings["cells per sample"] = realised_cells  # the cells that realise a star, per size
    # Both fits, published side by side (S21b). The per-star line is kept because
    # every record since S11 quotes it and a comparison needs it; the per-cell line
    # is the one that is conditioned, and R² says which by how much rather than
    # asserting it (rule B6).
    for prefix, x in (("per_star", stars), ("per_cell", cells)):
        slope, intercept = np.polyfit(x, secs, 1)
        resid = secs - (slope * x + intercept)
        spread = float(((secs - secs.mean()) ** 2).sum())
        timings[prefix + "_us"] = 1e6 * float(slope)
        timings[prefix + "_fixed_s"] = float(intercept)
        timings[prefix + "_r2"] = 1.0 - float((resid**2).sum()) / spread if spread > 0.0 else float("nan")
    timings["fixed_s"] = timings["per_star_fixed_s"]  # the name every record since S11 uses
    timings["cells"] = float(systems.CELL_COUNT)
    timings["cells realised"] = float(len(systems.cell_counts(out.fields["stellar_surface_density"], R, seed, n_stars, None)))
    return timings


def one_off() -> dict[str, float]:
    """The first seeded draw of this interpreter, then the second. Run in a fresh process."""
    from galaxy.core import seeds

    start = time.perf_counter()
    seeds.rng(0, "one-off").random(1)
    first = time.perf_counter() - start
    start = time.perf_counter()
    seeds.rng(1, "one-off").random(1)
    then = time.perf_counter() - start
    return {"first_s": first, "then_s": then}


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
    """One fresh interpreter per model (rule B2), and one more for the process-wide one-off."""
    proc = subprocess.run(
        [sys.executable, "-m", "galaxy.specs.performance", "--one-off"],
        capture_output=True, text=True, cwd=str(ROOT), check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"measuring the one-off failed:\n{proc.stderr[-2000:]}")
    shared = json.loads(proc.stdout.splitlines()[-1])
    rows = []
    for m in models:
        proc = subprocess.run(
            [sys.executable, "-m", "galaxy.specs.performance", "--one", m.name],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"profiling {m.name} failed:\n{proc.stderr[-2000:]}")
        rows.append({**json.loads(proc.stdout.splitlines()[-1]), "one_off": shared})
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
        if "per_star_us" in cat:
            sizes = " ".join(f"{int(s[0]) / 1000:g}k:{s[2]:.4f}s" for s in cat["samples"])
            r2 = cat.get("per_star_r2")
            fit = f" (R2 {r2:.2f})" if r2 is not None else ""
            lines.append(f"    catalogue against sample size: {sizes} -> {cat['per_star_us']:.2f} us per star, "
                         f"{1e3 * cat['fixed_s']:.1f} ms fixed{fit}; layout {1e3 * cat['layout']:.1f} ms over all "
                         f"{int(cat['cells'])} cells, {int(cat['cells realised'])} of them realise a star")
        if "per_cell_us" in cat:
            # The conditioned price (S21b, debt #67). The cells that realise a star
            # saturate — 349 of 1024 at 500 stars, 829 at 80,000 — so seconds is a
            # straight line in cells and a curve in stars, and the per-star line above
            # is a straight line through that curve. Both are published, with the R² of
            # each, because the number is the publication and the verdict is the
            # reader's (rule B6).
            lines.append(f"    the conditioned price: {cat['per_cell_us']:.1f} us per cell realised, "
                         f"{1e3 * cat['per_cell_fixed_s']:.1f} ms fixed (R2 {cat['per_cell_r2']:.2f}); "
                         f"cells per sample {[int(c) for c in cat.get('cells per sample', [])]}")
        one = r.get("one_off")
        if one:
            ratio = one["first_s"] / one["then_s"] if one["then_s"] > 0 else float("inf")
            # Which stage carries it is derived from the profile, not remembered: the widest
            # cold/warm ratio is the stage that paid the one-off. Naming it in a literal
            # was wrong within one session of being written — S17 put a seeded stage at
            # checkpoint 1 and the note still said `pattern` (rule B13, debt #37).
            billed = max(r["cold"], key=lambda s: r["cold"][s] / max(r["warm"][s], 1e-9))
            lines.append(f"    one-off, first seeded draw: {1e3 * one['first_s']:.2f} ms then {1e3 * one['then_s']:.3f} ms "
                         f"({ratio:.0f}x) — billed by this table to the first stage that draws ({billed}); debt #37")
    return "\n".join(lines)


def report(models: Iterable[Model]) -> str:
    return table(profile_cold(models))


def main() -> int:
    utf8_stdout()
    if len(sys.argv) > 2 and sys.argv[1] == "--one":
        print(json.dumps(measure(sys.argv[2])))
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "--one-off":
        print(json.dumps(one_off()))
        return 0
    models, _, _ = production()
    print(report(list(models)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
