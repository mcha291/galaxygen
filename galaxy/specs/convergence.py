"""convergence: every acceptance scalar swept in N_R and N_t, independently (rule B7, D37).

An acceptance row reads one published scalar. If that scalar moves when the
grid is refined, the row is judging the grid and not the physics, and N_R or
N_t has become a physics parameter (D37, D46). This spec runs every model at
the default grid and at each point of a sweep, publishes the **drift** of every
row's value against the default, and judges the drift against the row's own
target width: a drift larger than the room the target gives is a row the grid
can move across its own verdict.

**Two axes, never one knob.** GALAXY_INPUTS.md §10 measured the cost exponent
at 0.13 in N_R against about 1 in N_t, so radial resolution is nearly free and
temporal resolution is where the model gets expensive. They are swept
*separately*: each axis is moved with every other axis at its default, so a
drift can be read as "this row depends on N_t" rather than "on the grid".

**Statuses**, per row and per model:

- ``converged``: every drift is inside the target's width.
- ``unconverged``: some drift exceeds it. Recorded in ``_UNCONVERGED`` with a
  debt and a prediction, exactly as ``spec.py`` records a miss (rule B5) — it
  still prints ``unconverged``; only the exit status distinguishes explained
  from unexplained, and a recorded row that starts converging is itself an
  error (rule B10).
- ``untestable``: the row has a zero-width target (debt #17), so no drift can be
  judged against it. The drift is published; the table has no verdict to give.
- ``vacuous``: the row reads exactly zero at every grid — the advanced model's
  thick-disc rows with no valley (debt #27). Nothing moved because there is
  nothing to move; saying "converged" would be a false green.
- ``not-yet-computable``: the model does not publish the field. The row is
  listed so that both models show all 24.

Statistical rows are swept at the default seed: a seeded scalar is a pure
function of its seed and the grid, so at a fixed seed it must not move either.
Qualitative rows are judged on the category: a verdict that flips with N_t is
unconverged whatever the width.

**Publish the number, not the verdict** (rule B6): every row's value at every
grid point is in the report, beside the verdict, so a reader can disagree with
the threshold from the same numbers.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from galaxy.core.fielddoc import IDENT, Kind
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.core.registry import Model, production
from galaxy.specs import Problem, utf8_stdout
from galaxy.specs.spec import QUANTITIES, Quantity, SpecError

STATUSES: tuple[str, ...] = ("converged", "unconverged", "untestable", "vacuous", "not-yet-computable")

# The sweep. Each axis is moved on its own — coarser and finer than the default
# — with every other axis at the default grid. Adding an axis is one entry here.
SWEEP: Mapping[str, tuple[int, ...]] = MappingProxyType({"n_R": (200, 800), "n_t": (1000, 4000)})
QUICK: Mapping[str, tuple[int, ...]] = MappingProxyType({"n_R": (800,), "n_t": (4000,)})


@dataclass(frozen=True, slots=True)
class Point:
    """One grid of the sweep: ``axis`` set to ``n``, everything else at the base grid."""

    axis: str
    n: int

    def spec(self, base: GridSpec = DEFAULT) -> GridSpec:
        return base.replace(**{self.axis: self.n})

    @property
    def label(self) -> str:
        return f"{self.axis}={self.n}"


def points(sweep: Mapping[str, Sequence[int]] = SWEEP) -> tuple[Point, ...]:
    return tuple(Point(axis, int(n)) for axis, ns in sweep.items() for n in ns)


@dataclass(frozen=True, slots=True)
class Drift:
    """One row's value at the default grid and at every point of the sweep."""

    n: int
    name: str
    field: str | None
    status: str
    reason: str
    default: float | str | None = None
    values: Mapping[str, float | str] = MappingProxyType({})  # point label -> value at that grid
    width: float | None = None  # the row's hi − lo; None for a qualitative row

    @property
    def drifts(self) -> dict[str, float]:
        """Signed ``value − default`` per point; empty for categories and unpublished rows."""
        if not isinstance(self.default, (int, float)):
            return {}
        return {label: float(v) - float(self.default) for label, v in self.values.items() if isinstance(v, (int, float))}

    @property
    def worst(self) -> float | None:
        """The largest absolute drift across the sweep, or None if there is none to take."""
        d = self.drifts
        if not d:
            return None
        return max(abs(x) for x in d.values())

    @property
    def worst_share(self) -> float | None:
        """``worst / width``: 1 is the whole target width. None when there is no width to divide by."""
        if self.worst is None or self.width is None or self.width <= 0.0:
            return None
        return self.worst / self.width


@dataclass(frozen=True, slots=True)
class Unconverged:
    """A row the grid is known to move across its width, with the reason on the record (rule B5)."""

    row: int
    debt: int  # entry in the calibration debt register, GALAXY_INPUTS.md §11
    since: str  # the session that measured it
    reason: str
    prediction: str  # what would converge it, stated so that it can fail (rule B4)
    model: str | None = None  # None: every model; else the one model this explanation belongs to (rule A7)

    def __post_init__(self) -> None:
        if self.model is not None and not IDENT.match(self.model):
            raise SpecError(f"row {self.row}: model {self.model!r} must be a model name or None")
        if self.row not in {q.n for q in QUANTITIES}:
            raise SpecError(f"recorded unconverged row {self.row} is not in the table")
        if self.debt < 1 or not self.since.startswith("S"):
            raise SpecError(f"row {self.row}: a recorded unconverged row needs a debt number and a session")
        if not self.reason.strip() or not self.prediction.strip():
            raise SpecError(f"row {self.row}: a recorded unconverged row needs a reason and a prediction")


# Rows the sweep is known to move past their width, per model. Empty at S10: the
# sweep found none (DECISIONS.md, S10). An entry here is the convergence
# analogue of ``spec.Miss`` and is judged the same way.
_UNCONVERGED: tuple[Unconverged, ...] = ()


def recorded(model: str) -> Mapping[int, Unconverged]:
    """The recorded unconverged rows that apply to ``model`` (rule A7)."""
    out: dict[int, Unconverged] = {}
    for u in _UNCONVERGED:
        if u.model is None or u.model == model:
            if u.row in out:
                raise SpecError(f"row {u.row} is recorded as unconverged twice for model {model!r}")
            out[u.row] = u
    return MappingProxyType(out)


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def judge(q: Quantity, default: Mapping[str, Any], runs: Mapping[str, Mapping[str, Any]], decls: Mapping[str, Any]) -> Drift:
    """One row against the default fields and the swept ones. Pure: no runner here."""
    nyc = "not-yet-computable"
    if q.field is None:
        return Drift(q.n, q.name, None, nyc, "no published scalar is named for this quantity yet")
    if q.field not in default:
        return Drift(q.n, q.name, q.field, nyc, f"field {q.field!r} is not published by this model")
    decl = decls[q.field]
    values = MappingProxyType({label: fields[q.field] for label, fields in runs.items()})
    base = default[q.field]

    if decl.kind is Kind.CATEGORY_SCALAR or q.mode == "qualitative":
        flips = {label: v for label, v in values.items() if v != base}
        if flips:
            where = ", ".join(f"{label} reads {v!r}" for label, v in flips.items())
            return Drift(q.n, q.name, q.field, "unconverged", f"category {base!r} at the default grid; {where}", base, values, None)
        return Drift(q.n, q.name, q.field, "converged", f"{base!r} at every grid", base, values, None)

    base_f = float(base)
    vals = {label: float(v) for label, v in values.items()}
    if not _finite(base_f) or not all(_finite(v) for v in vals.values()):
        bad = ", ".join(f"{label}={v!r}" for label, v in {"default": base_f, **vals}.items() if not _finite(v))
        return Drift(q.n, q.name, q.field, "unconverged", f"not a number somewhere in the sweep: {bad}", base_f, MappingProxyType(vals), q.width)
    d = Drift(q.n, q.name, q.field, "converged", "", base_f, MappingProxyType(vals), q.width)
    worst = d.worst or 0.0
    if base_f == 0.0 and all(v == 0.0 for v in vals.values()):
        return Drift(q.n, q.name, q.field, "vacuous", "reads exactly 0 at every grid: nothing to converge", base_f, MappingProxyType(vals), q.width)
    if not q.testable:
        return Drift(
            q.n, q.name, q.field, "untestable",
            f"largest drift {worst:.4g} against a zero-width target (debt #17): published, not judged",
            base_f, MappingProxyType(vals), q.width,
        )
    assert q.width is not None
    share = worst / q.width
    if worst > q.width:
        return Drift(q.n, q.name, q.field, "unconverged", f"largest drift {worst:.4g} exceeds the target width {q.width:.4g} ({share:.2f}×)", base_f, MappingProxyType(vals), q.width)
    return Drift(q.n, q.name, q.field, "converged", f"largest drift {worst:.4g} is {share:.1%} of the target width {q.width:.4g}", base_f, MappingProxyType(vals), q.width)


def sweep(
    model: Model,
    quantities: Sequence[Quantity] = QUANTITIES,
    grids: Mapping[str, Sequence[int]] = SWEEP,
    base: GridSpec = DEFAULT,
    inputs: Mapping[str, Any] | None = None,
    **run_kwargs: Any,
) -> list[Drift]:
    """Run ``model`` at ``base`` and at every point of ``grids``; judge every row.

    Only the closure above the rows' fields runs (``only=``, rule D4): the
    catalogue and the planets are never built to read a scale length.
    """
    from galaxy.run import run

    fields = tuple(q.field for q in quantities if q.field is not None)
    default = run(model, inputs, base, only=fields, **run_kwargs)
    runs = {p.label: run(model, inputs, p.spec(base), only=fields, **run_kwargs).fields for p in points(grids)}
    return [judge(q, default.fields, runs, default.decls) for q in quantities]


def sweep_models(models: Iterable[Model], **kwargs: Any) -> dict[str, list[Drift]]:
    return {m.name: sweep(m, **kwargs) for m in models}


def summary(drifts: Iterable[Drift]) -> dict[str, int]:
    counts = {s: 0 for s in STATUSES}
    for d in drifts:
        counts[d.status] += 1
    return counts


def unexplained(drifts: Iterable[Drift], model: str) -> tuple[Drift, ...]:
    known = recorded(model)
    return tuple(d for d in drifts if d.status == "unconverged" and d.n not in known)


def stale(drifts: Iterable[Drift], model: str) -> tuple[Drift, ...]:
    """Recorded unconverged rows that now converge: the explanation is spent (rule B10)."""
    known = recorded(model)
    return tuple(d for d in drifts if d.status == "converged" and d.n in known)


def problems(drifts: Iterable[Drift], model: str) -> list[Problem]:
    drifts = list(drifts)
    known = recorded(model)
    out = [
        Problem("convergence", "unconverged", f"row {d.n} ({d.name}) moves with the grid and is not recorded for model {model!r}: {d.reason}")
        for d in unexplained(drifts, model)
    ]
    out += [
        Problem(
            "convergence",
            "stale-unconverged",
            f"row {d.n} ({d.name}) is recorded as unconverged for model {model!r} since {known[d.n].since} (debt "
            f"#{known[d.n].debt}) but now converges: {d.reason}. Remove the entry or find out why.",
        )
        for d in stale(drifts, model)
    ]
    return out


def check(models: Iterable[Model], results: Mapping[str, list[Drift]] | None = None, **kwargs: Any) -> list[Problem]:
    models = list(models)
    if results is None:
        results = sweep_models(models, **kwargs)
    return [p for m in models for p in problems(results[m.name], m.name)]


def _fmt(v: float | str | None) -> str:
    if v is None:
        return "-"
    if isinstance(v, str):
        return v
    return f"{v:.6g}"


def report(
    models: Iterable[Model],
    results: Mapping[str, list[Drift]] | None = None,
    grids: Mapping[str, Sequence[int]] = SWEEP,
    base: GridSpec = DEFAULT,
    **kwargs: Any,
) -> str:
    models = list(models)
    if results is None:
        results = sweep_models(models, grids=grids, base=base, **kwargs)
    labels = [p.label for p in points(grids)]
    axes = "; ".join(f"{axis} in {tuple(ns)}" for axis, ns in grids.items())
    lines = ["convergence", f"  default grid n_R={base.n_R}, n_t={base.n_t}, n_z={base.n_z}; each axis swept alone: {axes}"]
    for m in models:
        drifts = results[m.name]
        s = summary(drifts)
        known = recorded(m.name)
        lines.append(
            f"  model {m.name}: {s['converged']} converged, {s['unconverged']} unconverged, {s['untestable']} untestable, "
            f"{s['vacuous']} vacuous, {s['not-yet-computable']} not-yet-computable of {len(drifts)}"
        )
        lines.append("    " + f"{'row':>3} {'status':<19} {'default':>12} " + " ".join(f"{label:>12}" for label in labels) + f" {'drift/width':>11}  quantity")
        for d in drifts:
            cells = " ".join(f"{_fmt(d.values.get(label)):>12}" for label in labels)
            share = "-" if d.worst_share is None else f"{d.worst_share:.3f}"
            tag = f" [recorded, debt #{known[d.n].debt}, since {known[d.n].since}]" if d.n in known and d.status == "unconverged" else ""
            lines.append(f"    {d.n:>3} {d.status:<19} {_fmt(d.default):>12} {cells} {share:>11}  {d.name}: {d.reason}{tag}")
        for p in problems(drifts, m.name):
            lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, _, _ = production()
    models = list(models)
    results = sweep_models(models)
    print(report(models, results))
    return 1 if check(models, results) else 0


if __name__ == "__main__":
    sys.exit(main())
