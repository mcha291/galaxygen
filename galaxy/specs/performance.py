"""performance: what each stage of each model costs, measured cold, published raw.

**Publish the number, not the verdict** (rule B6). This module has no time budget
and no pass mark, because "fast enough" is a judgement someone can disagree with
from the same numbers and a threshold buried in an instrument is that judgement
made once and then forgotten. What it does assert is *completeness*: every stage
of every model appears in the profile. A stage nobody measured is exactly the
omission rule B2 exists to prevent, and ``tools/timings.py`` already holds that
line for API routes (rule B13).

**Cold, in a fresh process** (rule B2). One subprocess per model, and inside it
each stage is executed once from a run resumed at its own dependencies — so the
number is that stage's, not the pipeline prefix's, and it is the first execution
of that code in that interpreter. Each stage is then re-run from the same resume
point for a warm number; the ratio says whether the cold measurement was a warm
one in disguise. ``tools/timings.py`` and ``tools/scaling.py`` are the pattern.

**The runner's own overhead is measured and published, not subtracted.** Every
``run()`` rebuilds the dependency graph and resolves the inputs before executing
anything, and for the cheap stages that is a real fraction of the number. It is
measured by resuming with ``only=()`` — a run that executes nothing — and
reported on its own line. Subtracting it would be a correction someone would
have to trust; publishing it is one they can check.

**The per-cell catalogue cost** is D61's open question, and the reason this
module exists rather than another entry in ``tools/``. S5 chose 32 × 32 cells
because every cell costs a ``Generator`` construction that is paid on every run
whether or not anything asks for that cell's stars, and recorded that the
optimum depends on what the viewer asks for. Debt #24 fixed the spec ensemble's
version of that waste; the catalogue's own was left open. Here it is measured
three ways — the layout over every cell, the whole-galaxy catalogue, and the
nine-cell window ``tools/timings.py`` uses for a region query — so the fixed
per-cell cost and the marginal per-star cost can be told apart.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from galaxy.core.registry import Model, production
from galaxy.specs import Problem, utf8_stdout

ROOT = Path(__file__).resolve().parents[2]

# The window tools/timings.py calls "region: one sector" — nine cells of 1024.
REGION = (7.0, 9.0, 0.0, 0.4)


@dataclass(frozen=True, slots=True)
class StageCost:
    model: str
    stage: str
    slot: str
    checkpoint: int
    cold_s: float
    warm_s: float

    @property
    def ratio(self) -> float:
        return self.cold_s / self.warm_s if self.warm_s > 0 else float("inf")


@dataclass(frozen=True, slots=True)
class CellCost:
    """D61: what the catalogue costs per cell, and how much of it a region query pays.

    Two costs are mixed together in one materialisation and the decision D61 left
    open needs them apart:

    - a **fixed** cost that does not depend on how many stars are asked for, of
      which the *layout* — one ``Generator`` per cell in ``cell_counts``, for
      every cell of the grid whether or not it realises a star or anyone asks —
      is the part D61 is about;
    - a **marginal** cost per star.

    Layout is timed on its own. The split between fixed and marginal comes from
    materialising the same galaxy at several sample sizes and fitting a straight
    line, not from differencing the whole-galaxy and region materialisations:
    those two sit at almost the same stars-per-cell ratio, so that 2×2 is
    ill-conditioned and returns a *negative* cost per star from perfectly good
    timings ``[verified: measured at S10, before this was replaced]``. A slope
    over four sample sizes is the same idiom ``tools/scaling.py`` uses, and for
    the same reason: a difference of two points cannot see what a slope can.
    """

    cells: int  # the whole grid
    layout_s: float  # cell_counts over every cell of it
    setup_s: float  # materialise over no cells at all: the floor every materialisation pays
    # (stars asked for, stars realised, cells that realised one, seconds)
    samples: tuple[tuple[int, int, int, float], ...]
    default_sample: int  # the sample size the systems stage actually publishes
    region_cells: int
    region_realised: int
    region_s: float
    region_stars: int

    @property
    def full(self) -> tuple[int, int, int, float]:
        """The sample the systems stage itself draws."""
        return next(s for s in self.samples if s[0] == self.default_sample)

    @property
    def full_s(self) -> float:
        return self.full[3]

    @property
    def per_cell_layout_us(self) -> float:
        return 1e6 * self.layout_s / self.cells

    def _fit(self) -> tuple[float, float]:
        """(seconds per star, fixed seconds) by least squares over the sample sizes."""
        import numpy as np

        stars = np.array([s[1] for s in self.samples], dtype=float)
        secs = np.array([s[3] for s in self.samples], dtype=float)
        if stars.size < 2 or float(np.ptp(stars)) == 0.0:
            return float("nan"), float("nan")
        slope, intercept = np.polyfit(stars, secs, 1)
        return float(slope), float(intercept)

    @property
    def per_star_us(self) -> float:
        return 1e6 * self._fit()[0]

    @property
    def fixed_s(self) -> float:
        """What a materialisation costs before the first star: the intercept."""
        return self._fit()[1]

    @property
    def region_share(self) -> float:
        """What a nine-cell query costs as a fraction of the whole catalogue."""
        return self.region_s / self.full_s if self.full_s > 0 else float("nan")

    @property
    def layout_share(self) -> float:
        """The part D61 is about: cost paid for cells nothing asked for."""
        return self.layout_s / self.full_s if self.full_s > 0 else float("nan")


@dataclass(frozen=True, slots=True)
class OneOff:
    """A cost paid once per process, which a per-stage profile bills to whoever triggers it.

    The profile times each stage's first execution, so a cost that belongs to the
    interpreter rather than to any stage lands entirely on whichever stage runs
    into it first — and is then read as that stage being expensive. Measuring it
    on its own is the only way the table can be read correctly (rules B2, B6).
    """

    name: str
    first_s: float
    then_s: float
    lands_on: str
    about: str

    @property
    def ratio(self) -> float:
        return self.first_s / self.then_s if self.then_s > 0 else float("inf")


@dataclass(frozen=True, slots=True)
class Profile:
    model: str
    import_s: float
    overhead_s: float  # one run() that executes no stage: graph build plus input resolution
    stages: tuple[StageCost, ...]
    cells: CellCost | None  # None when the model has no catalogue stage
    one_offs: tuple[OneOff, ...] = ()

    @property
    def total_s(self) -> float:
        return sum(s.cold_s for s in self.stages)

    def share(self, stage: StageCost) -> float:
        return stage.cold_s / self.total_s if self.total_s > 0 else float("nan")

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        d["stages"] = [asdict(s) for s in self.stages]
        d["cells"] = asdict(self.cells) if self.cells else None
        d["one_offs"] = [asdict(o) for o in self.one_offs]
        return d

    @staticmethod
    def from_json(d: Mapping[str, Any]) -> Profile:
        cells = d["cells"]
        if cells:
            cells = {**cells, "samples": tuple(tuple(s) for s in cells["samples"])}
        return Profile(
            model=d["model"],
            import_s=d["import_s"],
            overhead_s=d["overhead_s"],
            stages=tuple(StageCost(**s) for s in d["stages"]),
            cells=CellCost(**cells) if cells else None,
            one_offs=tuple(OneOff(**o) for o in d.get("one_offs", ())),
        )


# --- measuring ----------------------------------------------------------------


SAMPLES: tuple[int, ...] = (5_000, 10_000, 20_000, 40_000)


def _cell_cost(fields: Mapping[str, Any], grid: Any, seed: int = 0) -> CellCost:
    """Time the catalogue, on a galaxy that is already built."""
    from galaxy.stages.systems import CATALOGUE_SAMPLE, CELL_COUNT, cell_counts, cells_in, materialise

    R, t = grid.R, grid.t
    sigma = fields["stellar_surface_density"]

    start = time.perf_counter()
    counts = cell_counts(sigma, R, seed, CATALOGUE_SAMPLE)
    layout_s = time.perf_counter() - start

    # Over no cells at all: the ring masses and ring radii every materialisation
    # builds before it draws anything, and the floor a one-cell query cannot go under.
    start = time.perf_counter()
    materialise(fields, R, t, seed, CATALOGUE_SAMPLE, cells=())
    setup_s = time.perf_counter() - start

    samples: list[tuple[int, int, int, float]] = []
    for n in sorted({*SAMPLES, CATALOGUE_SAMPLE}):
        start = time.perf_counter()
        cat = materialise(fields, R, t, seed, n)
        seconds = time.perf_counter() - start
        realised = len(cell_counts(sigma, R, seed, n))
        samples.append((n, int(cat.size), realised, seconds))

    cells = cells_in(R, *REGION)
    start = time.perf_counter()
    region = materialise(fields, R, t, seed, CATALOGUE_SAMPLE, cells=cells)
    region_s = time.perf_counter() - start

    assert sum(c for _, c in counts) == next(s[1] for s in samples if s[0] == CATALOGUE_SAMPLE)
    return CellCost(
        cells=CELL_COUNT,
        layout_s=layout_s,
        setup_s=setup_s,
        samples=tuple(samples),
        default_sample=CATALOGUE_SAMPLE,
        region_cells=len(cells),
        region_realised=len(cell_counts(sigma, R, seed, CATALOGUE_SAMPLE, cells)),
        region_s=region_s,
        region_stars=int(region.size),
    )


def profile(model_name: str) -> Profile:
    """Every stage of one model, timed once each. Run this under a fresh interpreter."""
    start = time.perf_counter()
    from galaxy.run import run
    from galaxy.specs import graph as _graph

    models, impls, table = production()
    import_s = time.perf_counter() - start

    model = models.get(model_name)
    g = _graph.build(model, impls, table)

    acc = run(model, only=())  # nothing to execute: the runner's own cost, once
    start = time.perf_counter()
    run(model, only=(), resume=acc)
    overhead_s = time.perf_counter() - start

    costs: list[StageCost] = []
    for stage in g.order:
        names = stage.published_names
        start = time.perf_counter()
        nxt = run(model, only=names, resume=acc)
        cold_s = time.perf_counter() - start
        start = time.perf_counter()
        run(model, only=names, resume=acc)  # same resume point, so this one is warm
        warm_s = time.perf_counter() - start
        assert nxt.ran == (stage.id,), f"resuming ran {nxt.ran}, not just {stage.id!r}"
        acc = nxt
        costs.append(StageCost(model_name, stage.id, stage.slot, stage.checkpoint, cold_s, warm_s))

    cells = None
    if "stellar_surface_density" in acc.fields and any(s.checkpoint == 5 for s in g.order):
        cells = _cell_cost(acc.fields, acc.grid)
    return Profile(model_name, import_s, overhead_s, tuple(costs), cells)


def one_offs() -> tuple[OneOff, ...]:
    """Process-wide first-call costs, timed in an interpreter that has run no stage.

    Measured here rather than inside :func:`profile`, because paying the cost
    before the stage loop would move it out of the table and leave nothing to
    explain why the table used to show it.
    """
    from galaxy.core import seeds
    from galaxy.specs import graph as _graph

    models, impls, table = production()
    lands: list[str] = []
    for m in models:
        first = next(
            (s.id for s in _graph.build(m, impls, table).order if s.reads_seeds),
            "(no stage draws)",
        )
        lands.append(f"{first} ({m.name})")

    start = time.perf_counter()
    seeds.rng(0, "one-off").random(1)
    first_s = time.perf_counter() - start
    start = time.perf_counter()
    seeds.rng(1, "one-off").random(1)
    then_s = time.perf_counter() - start
    return (
        OneOff(
            "first seeded draw",
            first_s,
            then_s,
            ", ".join(lands),
            "numpy's bit generator machinery, initialised by whichever stage draws first",
        ),
    )


def measure(models: Iterable[Model]) -> dict[str, Profile]:
    """One fresh interpreter per model. Nothing is measured in a process that ran a model."""
    proc = subprocess.run(
        [sys.executable, "-m", "galaxy.specs.performance", "--one-off"],
        capture_output=True, text=True, cwd=str(ROOT), check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"measuring the process one-offs failed:\n{proc.stderr}")
    shared = tuple(OneOff(**o) for o in json.loads(proc.stdout.splitlines()[-1]))

    out: dict[str, Profile] = {}
    for m in models:
        proc = subprocess.run(
            [sys.executable, "-m", "galaxy.specs.performance", "--one", m.name],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(f"profiling {m.name} failed:\n{proc.stderr}")
        p = Profile.from_json(json.loads(proc.stdout.splitlines()[-1]))
        out[m.name] = dataclasses.replace(p, one_offs=shared)
    return out


# --- judging: completeness only -----------------------------------------------


def problems(model: Model, prof: Profile, impls: Any, table: Any) -> list[Problem]:
    """A stage that is not in the profile. There is no time budget here (rule B6)."""
    from galaxy.specs import graph as _graph

    expected = tuple(s.id for s in _graph.build(model, impls, table).order)
    measured = tuple(s.stage for s in prof.stages)
    out: list[Problem] = []
    if measured != expected:
        missing = [s for s in expected if s not in measured]
        extra = [s for s in measured if s not in expected]
        detail = f"profile ran {list(measured)}, the graph orders {list(expected)}"
        if missing:
            detail = f"stages {missing} are in the model and not in the profile; " + detail
        if extra:
            detail = f"stages {extra} are in the profile and not in the model; " + detail
        out.append(Problem(model.name, "unprofiled-stage", detail))
    return out


def check(
    models: Iterable[Model],
    results: Mapping[str, Profile] | None = None,
    impls: Any = None,
    table: Any = None,
) -> list[Problem]:
    models = list(models)
    if impls is None or table is None:
        _, impls, table = production()
    if results is None:
        results = measure(models)
    return [p for m in models for p in problems(m, results[m.name], impls, table)]


# --- reporting ----------------------------------------------------------------


def report(
    models: Iterable[Model],
    results: Mapping[str, Profile] | None = None,
    impls: Any = None,
    table: Any = None,
) -> str:
    models = list(models)
    if impls is None or table is None:
        _, impls, table = production()
    if results is None:
        results = measure(models)
    lines = ["performance"]
    for m in models:
        p = results[m.name]
        lines.append(
            f"  model {m.name}: {p.total_s:.4f} s cold over {len(p.stages)} stages; "
            f"import + registry {p.import_s:.3f} s, runner overhead {1e3 * p.overhead_s:.2f} ms per call"
        )
        lines.append(f"    {'stage':<20} {'cp':>3} {'cold s':>9} {'warm s':>9} {'c/w':>6} {'share':>7}")
        for s in p.stages:
            lines.append(
                f"    {s.stage:<20} {s.checkpoint:>3} {s.cold_s:>9.4f} {s.warm_s:>9.4f} "
                f"{s.ratio:>6.2f} {p.share(s):>6.1%}"
            )
        if p.cells is not None:
            c = p.cells
            asked, stars, realised, seconds = c.full
            lines.append(
                f"    catalogue (D61): {seconds:.4f} s for {stars:,} stars in {realised} of {c.cells} "
                f"cells; {c.region_cells}-cell window {c.region_s:.4f} s for {c.region_stars:,} stars "
                f"({c.region_share:.1%} of the whole)"
            )
            sweep = " ".join(f"{n // 1000}k:{s:.4f}s" for n, _, _, s in c.samples)
            lines.append(
                f"    catalogue cost against sample size: {sweep} -> {c.per_star_us:.2f} us per star, "
                f"{1e3 * c.fixed_s:.1f} ms fixed ({1 - stars * c.per_star_us * 1e-6 / seconds:.0%} of the "
                f"catalogue at {asked // 1000}k does not depend on how many stars are asked for)"
            )
            lines.append(
                f"    of that fixed cost: {1e3 * c.setup_s:.1f} ms setup over no cells at all, "
                f"{1e3 * c.layout_s:.1f} ms laying out all {c.cells} cells "
                f"({c.per_cell_layout_us:.1f} us each, paid whether or not anything asks), "
                f"{1e3 * (c.fixed_s - c.setup_s - c.layout_s):.1f} ms drawing in the {realised} cells "
                f"that realise a star"
            )
        for o in p.one_offs:
            lines.append(
                f"    one-off, {o.name}: {1e3 * o.first_s:.2f} ms then {1e3 * o.then_s:.3f} ms "
                f"({o.ratio:.0f}x) — billed by this table to {o.lands_on}; {o.about}"
            )
        for problem in problems(m, p, impls, table):
            lines.append(f"    FAIL {problem}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Per-stage cold profile, both models (rules B2, B6).")
    parser.add_argument("--json", action="store_true", help="print the measurements as JSON")
    parser.add_argument("--one", help=argparse.SUPPRESS)  # the subprocess entry points
    parser.add_argument("--one-off", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.one is not None:
        print(json.dumps(profile(args.one).to_json()))
        return 0
    if args.one_off:
        print(json.dumps([asdict(o) for o in one_offs()]))
        return 0

    utf8_stdout()
    models, impls, table = production()
    models = list(models)
    results = measure(models)
    if args.json:
        print(json.dumps({n: p.to_json() for n, p in results.items()}, indent=2))
    else:
        print(report(models, results, impls, table))
    return 1 if check(models, results, impls, table) else 0


if __name__ == "__main__":
    sys.exit(main())
