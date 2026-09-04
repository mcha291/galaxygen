"""convergence: N_R, N_t and N_z swept independently, per model, for every acceptance scalar.

GALAXY_INPUTS.md §10 measured the model's cost exponent at 0.13 in N_R against
~1 in N_t: the two are not one quality knob and must not share one, so this
sweep moves each axis of the grid on its own and holds the others at the
default. N_z is swept too, because the advanced chemistry reads the halo
potential off the first z-row as its midplane value (D89).

For every acceptance quantity a model publishes, the value is taken at each
grid and the **drift** is the largest departure from the default-grid value. A
pointwise row's tolerance is the width of its own target: a scalar that moves
by more than the error bar it is judged against makes the grid a physics
parameter, which is the defect the sweep exists to find (D37, D46). A
zero-width target has no tolerance to judge against and is reported as
untestable rather than failed (debt #17). A qualitative row drifts if its
category changes at all. Statistical rows are seeded draws and are reported at
the default seed without a verdict.

Publish the numbers, not the verdict (rule B6): the report carries every value
at every grid, and ``check`` is the one place a drift becomes a problem.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.core.registry import Model, production
from galaxy.specs import Problem, utf8_stdout
from galaxy.specs.spec import QUANTITIES, Quantity

# Each axis halved and doubled about the default, the others held there.
SWEEPS: Mapping[str, tuple[int, ...]] = {
    "n_R": (200, 400, 800),
    "n_t": (1000, 2000, 4000),
    "n_z": (30, 60, 120),
}
QUICK: Mapping[str, tuple[int, ...]] = {"n_R": (200, 400), "n_t": (1000, 2000), "n_z": (30, 60)}


@dataclass(frozen=True, slots=True)
class Drift:
    model: str
    row: int
    name: str
    axis: str
    values: Mapping[int, float | str]  # grid size -> value
    default: float | str
    drift: float  # largest |value - default| over the sweep; 1.0 for a category that changed
    tolerance: float | None  # the target's width; None when there is none to judge against
    status: str  # "ok" | "drifts" | "untestable" | "statistical"

    @property
    def problem(self) -> bool:
        return self.status == "drifts"


@dataclass
class Report:
    drifts: list[Drift] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def problems(self) -> list[Problem]:
        return [
            Problem(
                d.model, "drift",
                f"row {d.row} ({d.name}) moves by {d.drift:.4g} across {d.axis} = {dict(d.values)}; "
                f"the target is {d.tolerance:.4g} wide",
            )
            for d in self.drifts if d.problem
        ]

    @property
    def ok(self) -> bool:
        return not self.problems


def _judge(q: Quantity, default: float | str, values: Mapping[int, float | str]) -> tuple[float, float | None, str]:
    if q.mode == "statistical":
        drift = max((abs(float(v) - float(default)) for v in values.values()), default=0.0)
        return drift, None, "statistical"
    if q.mode == "qualitative":
        drift = 0.0 if all(v == default for v in values.values()) else 1.0
        return drift, 0.0, "drifts" if drift else "ok"
    assert q.lo is not None and q.hi is not None
    drift = max(abs(float(v) - float(default)) for v in values.values())
    if any(not math.isfinite(float(v)) for v in values.values()) or not math.isfinite(float(default)):
        return float("nan"), None, "untestable"
    width = q.hi - q.lo
    if width <= 0.0:
        return drift, None, "untestable"  # debt #17: nothing to judge the drift against
    return drift, width, "drifts" if drift > width else "ok"


def sweep(
    model: Model,
    sweeps: Mapping[str, Sequence[int]] = SWEEPS,
    base: GridSpec = DEFAULT,
    **run_kwargs: object,
) -> Report:
    """Every published acceptance scalar of ``model`` at every grid of every sweep."""
    from galaxy.run import run

    rep = Report()
    fields = tuple(q.field for q in QUANTITIES if q.field is not None)
    at_default = run(model, grid=base, only=fields, **run_kwargs)
    published = [q for q in QUANTITIES if q.field in at_default.fields]
    skipped = [q.n for q in QUANTITIES if q.field not in at_default.fields]
    if skipped:
        rep.notes.append(f"model {model.name}: rows {skipped} not published, not swept")
    for axis, sizes in sweeps.items():
        outs = {}
        for n in sizes:
            spec = base if n == getattr(base, axis) else base.replace(**{axis: n})
            outs[n] = at_default if spec == base else run(model, grid=spec, only=fields, **run_kwargs)
        for q in published:
            assert q.field is not None
            values = {n: outs[n].fields[q.field] for n in sizes}
            default = at_default.fields[q.field]
            drift, tolerance, status = _judge(q, default, values)
            rep.drifts.append(Drift(model.name, q.n, q.name, axis, values, default, drift, tolerance, status))
    return rep


def check(models: Iterable[Model], sweeps: Mapping[str, Sequence[int]] = SWEEPS, **kw: object) -> list[Problem]:
    out: list[Problem] = []
    for m in models:
        out.extend(sweep(m, sweeps, **kw).problems)
    return out


def _fmt(v: float | str) -> str:
    return v if isinstance(v, str) else f"{v:.6g}"


def report(models: Iterable[Model], sweeps: Mapping[str, Sequence[int]] = SWEEPS, **kw: object) -> str:
    lines = ["convergence"]
    for m in models:
        rep = sweep(m, sweeps, **kw)
        counts = {s: sum(1 for d in rep.drifts if d.status == s) for s in ("ok", "drifts", "untestable", "statistical")}
        lines.append(f"  model {m.name}: {counts['ok']} ok, {counts['drifts']} drift, {counts['untestable']} untestable, {counts['statistical']} statistical (row x axis)")
        for axis in sweeps:
            lines.append(f"    {axis} = {list(sweeps[axis])}")
            for d in rep.drifts:
                if d.axis != axis:
                    continue
                vals = ", ".join(_fmt(v) for v in d.values.values())
                tol = "" if d.tolerance is None else f" of {d.tolerance:.4g}"
                lines.append(f"      {d.row:>2} {d.status:<11} {d.name}: [{vals}]  drift {d.drift:.3g}{tol}")
        for n in rep.notes:
            lines.append(f"    note: {n}")
        for p in rep.problems:
            lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, _, _ = production()
    models = list(models)
    quick = "--quick" in sys.argv[1:]
    print(report(models, QUICK if quick else SWEEPS))
    return 1 if check(models, QUICK if quick else SWEEPS) else 0


if __name__ == "__main__":
    sys.exit(main())
