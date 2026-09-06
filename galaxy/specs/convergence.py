"""convergence: how far each acceptance number moves with the grid, knob by knob (S10).

The runner takes a :class:`~galaxy.core.grids.GridSpec` rather than reading
module constants so that this spec can exist (D6, D37). It runs every model at
the default grid and again with **one** knob changed at a time — ``n_R`` over
:data:`R_SWEEP`, ``n_t`` over :data:`T_SWEEP` — and reports, for every quantity
in the acceptance table, the largest distance any sweep point puts between that
quantity and its default-grid value. GALAXY_INPUTS.md §10 measured the cost
exponent at 0.13 in N_R against ~1 in N_t ``[verified: GALAXY_INPUTS.md §10,
citing bench2.py §3]``; the two are not one quality knob and are never swept as
one here.

**What passes.** A row's *width* is the length of its target interval. A number
that the grid alone can move by more than the width could pass on one grid and
fail on another, so the verdict would be a property of the discretisation and
not of the model (rule A6's "quality knob, not physics parameter", D37). A row
passes when every drift is at most the width; the qualitative row passes when
its category is the same at every point. Rows the model does not publish are
not-yet-computable, exactly as in ``spec``.

**What is measured, and what is not.** Every value is the model's own scalar at
the default seeds, one run per grid point, including the statistical rows: for
those the drift is that of a *single seeded realisation*, which is what the
ensemble is built from, and a seed is an argument rather than a source of
scatter under rule A10. Zero-width targets have no drift they could tolerate,
which is debt #17's complaint made mechanical; the table carries the source's
printed precision since S10 so no row is untestable by construction.

**Recorded drifts.** As in ``spec``, a failure nobody has explained stops the
run and a recorded one does not (rules B4, B5): :data:`_RECORDED` names the row,
its model, the debt it belongs to, the reason and a prediction that could kill
it. A recorded drift that has stopped failing is an error too — the explanation
is stale (rule B10).
"""

from __future__ import annotations

import math
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from galaxy.core.fielddoc import IDENT
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.core.registry import Model, production
from galaxy.specs import Problem, utf8_stdout
from galaxy.specs.spec import QUANTITIES, STATUSES, Quantity, SpecError

R_SWEEP: tuple[int, ...] = (100, 200, 800)
T_SWEEP: tuple[int, ...] = (500, 1000, 4000)
KNOBS: tuple[str, ...] = ("n_R", "n_t")

# Every scalar the table names. ``run(only=…)`` executes the closure above
# these and nothing else — the catalogue and the planets are not in it.
FIELDS: tuple[str, ...] = tuple(q.field for q in QUANTITIES if q.field is not None)


@dataclass(frozen=True, slots=True)
class Point:
    """One sweep point: which knob, its value, and what the quantity read there."""

    knob: str
    n: int
    value: float | str | None


@dataclass(frozen=True, slots=True)
class Drift:
    n: int
    name: str
    status: str
    reason: str
    default: float | str | None = None
    width: float | None = None
    drift: Mapping[str, float] = MappingProxyType({})  # knob -> max |value - default|
    points: tuple[Point, ...] = ()

    @property
    def worst(self) -> float:
        return max(self.drift.values(), default=0.0)


@dataclass(frozen=True, slots=True)
class Recorded:
    """A row the grid is known to move beyond its width, with the reason on the record (rule B5)."""

    row: int
    debt: int
    since: str
    reason: str
    prediction: str
    model: str | None = None

    def __post_init__(self) -> None:
        if self.model is not None and not IDENT.match(self.model):
            raise SpecError(f"row {self.row}: model {self.model!r} must be a model name or None")
        if self.row not in {q.n for q in QUANTITIES}:
            raise SpecError(f"recorded drift names row {self.row}, which is not in the table")
        if self.debt < 1 or not self.since.startswith("S"):
            raise SpecError(f"row {self.row}: a recorded drift needs a debt number and a session")
        if not self.reason.strip() or not self.prediction.strip():
            raise SpecError(f"row {self.row}: a recorded drift needs a reason and a prediction")


_RECORDED: tuple[Recorded, ...] = ()


def recorded(model: str) -> Mapping[int, Recorded]:
    out: dict[int, Recorded] = {}
    for r in _RECORDED:
        if r.model is None or r.model == model:
            if r.row in out:
                raise SpecError(f"row {r.row} is recorded as a drift twice for model {model!r}")
            out[r.row] = r
    return MappingProxyType(out)


def grids(
    base: GridSpec = DEFAULT, r_sweep: Sequence[int] = R_SWEEP, t_sweep: Sequence[int] = T_SWEEP
) -> tuple[tuple[str, int, GridSpec], ...]:
    """The sweep: one knob moved at a time, everything else at ``base``."""
    return tuple(("n_R", n, base.replace(n_R=n)) for n in r_sweep) + tuple(
        ("n_t", n, base.replace(n_t=n)) for n in t_sweep
    )


def sweep(
    model: Model,
    base: GridSpec = DEFAULT,
    r_sweep: Sequence[int] = R_SWEEP,
    t_sweep: Sequence[int] = T_SWEEP,
    **run_kwargs: Any,
) -> tuple[dict[str, Any], list[tuple[str, int, dict[str, Any]]]]:
    """The table's scalars at ``base`` and at every sweep point, for one model."""
    from galaxy.run import run

    def scalars(grid: GridSpec) -> dict[str, Any]:
        out = run(model, grid=grid, only=FIELDS, **run_kwargs)
        return {f: out.fields[f] for f in FIELDS if f in out.fields}

    return scalars(base), [(knob, n, scalars(g)) for knob, n, g in grids(base, r_sweep, t_sweep)]


def _fmt(v: float) -> str:
    return f"{v:.3g}"


def judge(q: Quantity, default: Mapping[str, Any], points: Sequence[tuple[str, int, Mapping[str, Any]]]) -> Drift:
    nyc = "not-yet-computable"
    if q.field is None:
        return Drift(q.n, q.name, nyc, "no published scalar is named for this quantity yet")
    if q.field not in default:
        return Drift(q.n, q.name, nyc, f"field {q.field!r} is not published by this model")
    base = default[q.field]
    if q.mode == "qualitative":
        pts = tuple(Point(k, n, p.get(q.field)) for k, n, p in points)
        moved = [pt for pt in pts if pt.value != base]
        if moved:
            where = ", ".join(f"{pt.knob}={pt.n} -> {pt.value!r}" for pt in moved)
            return Drift(q.n, q.name, "fail", f"{base!r} at the default grid; changes at {where}", base, None, MappingProxyType({}), pts)
        return Drift(q.n, q.name, "pass", f"{base!r} at every point", base, None, MappingProxyType({}), pts)
    assert q.lo is not None and q.hi is not None
    base_f = float(base)
    pts = tuple(Point(k, n, float(p[q.field])) for k, n, p in points if q.field in p)
    drift: dict[str, float] = {}
    for pt in pts:
        assert isinstance(pt.value, float)
        d = abs(pt.value - base_f) if math.isfinite(pt.value) and math.isfinite(base_f) else math.inf
        drift[pt.knob] = max(drift.get(pt.knob, 0.0), d)
    width = q.hi - q.lo
    worst = max(drift.values(), default=0.0)
    ok = worst <= width
    parts = []
    for knob in KNOBS:
        if knob in drift:
            share = "" if width <= 0.0 else f" ({100.0 * drift[knob] / width:.1f}% of width)"
            parts.append(f"{knob} {_fmt(drift[knob])}{share}")
    seed = " (single seed)" if q.mode == "statistical" else ""
    reason = f"{base_f:.6g}{seed}; drift " + ", ".join(parts) + f"; width {_fmt(width)}"
    return Drift(q.n, q.name, "pass" if ok else "fail", reason, base_f, width, MappingProxyType(drift), pts)


def evaluate(model: Model, **kwargs: Any) -> list[Drift]:
    default, points = sweep(model, **kwargs)
    return [judge(q, default, points) for q in QUANTITIES]


def evaluate_models(models: Iterable[Model], **kwargs: Any) -> dict[str, list[Drift]]:
    return {m.name: evaluate(m, **kwargs) for m in models}


def summary(drifts: Iterable[Drift]) -> dict[str, int]:
    counts = {s: 0 for s in STATUSES}
    for d in drifts:
        counts[d.status] += 1
    return counts


def unexplained(drifts: Iterable[Drift], model: str) -> tuple[Drift, ...]:
    known = recorded(model)
    return tuple(d for d in drifts if d.status == "fail" and d.n not in known)


def stale(drifts: Iterable[Drift], model: str) -> tuple[Drift, ...]:
    known = recorded(model)
    return tuple(d for d in drifts if d.status == "pass" and d.n in known)


def problems(drifts: Iterable[Drift], model: str) -> list[Problem]:
    drifts = list(drifts)
    known = recorded(model)
    out = [
        Problem(model, "drift", f"row {d.n} ({d.name}) moves more than its width with the grid and is not recorded: {d.reason}")
        for d in unexplained(drifts, model)
    ]
    out += [
        Problem(
            model,
            "stale-drift",
            f"row {d.n} ({d.name}) is recorded as a drift since {known[d.n].since} (debt #{known[d.n].debt}) "
            f"but now converges: {d.reason}. Remove the entry or find out why.",
        )
        for d in stale(drifts, model)
    ]
    return out


def report(
    models: Iterable[Model],
    results: Mapping[str, list[Drift]] | None = None,
    base: GridSpec = DEFAULT,
    r_sweep: Sequence[int] = R_SWEEP,
    t_sweep: Sequence[int] = T_SWEEP,
    **kwargs: Any,
) -> str:
    models = list(models)
    if results is None:
        results = evaluate_models(models, base=base, r_sweep=r_sweep, t_sweep=t_sweep, **kwargs)
    lines = ["convergence"]
    lines.append(
        f"  one knob at a time against n_R={base.n_R}, n_t={base.n_t}: "
        f"n_R {', '.join(str(n) for n in r_sweep)}; n_t {', '.join(str(n) for n in t_sweep)}"
    )
    for m in models:
        drifts = results[m.name]
        s = summary(drifts)
        known = recorded(m.name)
        rec = sum(1 for d in drifts if d.status == "fail" and d.n in known)
        head = f"  model {m.name}: {s['pass']} pass, {s['fail']} fail, {s['not-yet-computable']} not-yet-computable of {len(drifts)}"
        if rec:
            head += f" ({rec} of the failures recorded)"
        lines.append(head)
        for d in drifts:
            tag = ""
            if d.n in known and d.status == "fail":
                tag = f" [recorded drift, debt #{known[d.n].debt}, since {known[d.n].since}]"
            lines.append(f"    {d.n:>2} {d.status:<19} {d.name}: {d.reason}{tag}")
        for p in problems(drifts, m.name):
            lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, _, _ = production()
    models = list(models)
    results = evaluate_models(models)
    print(report(models, results))
    return 1 if any(problems(r, name) for name, r in results.items()) else 0


if __name__ == "__main__":
    sys.exit(main())
