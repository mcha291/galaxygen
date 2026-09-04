"""convergence: does an acceptance number move when the grid moves?

The grid is not physics. Every number in ``spec.py`` is quoted against a
measurement of the Milky Way, and a number that changes when N_t doubles is
reporting the discretisation as well as the model — so the acceptance table
cannot be read at all until the drift is known and published.

**One knob at a time.** N_R, N_t and N_z are swept *independently*, each against
the default grid, never together. This is not tidiness: GALAXY_INPUTS.md §10
measured the cost exponent at 0.13 in N_R against ~1 in N_t, so they are not
interchangeable quality knobs and a single "resolution" dial would hide which one
a number is sensitive to ``[verified: GALAXY_INPUTS.md §10]``. The seed of this
module is ``tests/test_sfh.py::test_scalars_do_not_move_with_grid_resolution``,
which moved N_R and N_t together and so could not have told them apart.

N_z is swept too, though the S10 brief names only the other two. It is the third
grid axis, the vertical stage's scale heights are rows 6 and 7 of the acceptance
table, and an audit that leaves an axis out is the same defect in a different
place.

**The judgement.** Each row's drift is the largest absolute change from the
default grid's value across that knob's sweep. It is judged against the width of
the row's own acceptance interval, ``hi - lo``: a number that moves further under
a change of resolution than the observation it is checked against is allowed to
move is not measuring what the row claims. Rows whose target has zero width
(20, 21 — debt #17) have no width to judge against and are reported as
``no-target-width`` with the drift published anyway (rule B6: publish the number,
not the verdict). Qualitative rows are judged on whether the category changed.

**What is swept and what is not.** The statistical rows (13, 14, 16, 17, 18) are
judged in ``spec.py`` against an ensemble over seeds; here they are swept as the
single seed-0 draw, because "does this galaxy's pattern speed move with the grid"
is the convergence question and "is the ensemble consistent with the observation"
is not. Fields the model does not publish are skipped, exactly as they are
not-yet-computable there. Only the dependency closure above the acceptance
fields is run (``only=``, rule D4) — the catalogue does not participate.

**Recorded drifts** (:func:`recorded`). Rule B5 applies here as it does to the
acceptance table: a row known to drift, with a reason and a prediction, is
registered rather than tolerated silently or judged away. A registered drift
still prints as ``drifts``; it just does not stop the run. An unregistered drift
does, and so does a registered one that has stopped drifting, because the
recorded explanation is then stale (rule B10).
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from galaxy.core.fielddoc import IDENT
from galaxy.core.grids import GridSpec
from galaxy.core.registry import Model, production
from galaxy.specs import Problem, utf8_stdout
from galaxy.specs.spec import QUANTITIES, Quantity, SpecError

DEFAULT_GRID = GridSpec()

STATUSES: tuple[str, ...] = ("converged", "drifts", "no-target-width")


@dataclass(frozen=True, slots=True)
class Knob:
    """One grid axis, the values it is swept over, and a control point (rule B3).

    ``control`` is a deliberately too-coarse value for this axis, measured
    alongside the sweep so that the report says whether the criterion is capable
    of firing at all. A sweep in which nothing drifts is either a converged model
    or a broken instrument, and those two look identical from the sweep alone —
    ``scaling.py`` answers the same objection by timing the naive convolution it
    exists to rule out. ``control_fires`` is what the control did when it was
    measured; a change in either direction is a problem, so the finding that N_z
    moves *nothing* (not one acceptance row, even at ``n_z = 1``) is machine-
    checked rather than asserted in prose.
    """

    name: str  # a GridSpec field: n_R, n_t or n_z
    points: tuple[int, ...]
    control: int
    control_fires: bool
    about: str

    def __post_init__(self) -> None:
        if not hasattr(DEFAULT_GRID, self.name):
            raise SpecError(f"knob {self.name!r} is not a GridSpec field")
        default = getattr(DEFAULT_GRID, self.name)
        if default in self.points:
            raise SpecError(f"knob {self.name!r}: the default {default} is the baseline, not a sweep point")
        if len(self.points) < 2:
            raise SpecError(f"knob {self.name!r}: a sweep needs at least a coarser and a finer point")
        if self.control >= min(self.points):
            raise SpecError(f"knob {self.name!r}: the control must be coarser than every sweep point")
        if not self.about.strip():
            raise SpecError(f"knob {self.name!r}: a knob says what refining it is expected to buy")

    def specs(self) -> tuple[tuple[int, GridSpec], ...]:
        """``(value, grid)`` for each sweep point, this knob moved and nothing else."""
        return tuple((n, DEFAULT_GRID.replace(**{self.name: n})) for n in self.points)

    def control_spec(self) -> GridSpec:
        return DEFAULT_GRID.replace(**{self.name: self.control})


KNOBS: tuple[Knob, ...] = (
    Knob("n_R", (200, 800), 8, True, "radial annuli; the cost exponent here is 0.13, so refining is nearly free"),
    Knob("n_t", (1000, 4000), 8, True, "timesteps; the cost exponent here is ~1, and this is where the model gets expensive"),
    Knob("n_z", (30, 120), 1, False, "vertical samples of the (R, z) potential; no acceptance row is measured on it (S10)"),
)


@dataclass(frozen=True, slots=True)
class Recorded:
    """A drift that is known, explained and on the record (rule B5)."""

    row: int
    knob: str
    debt: int
    since: str
    reason: str
    prediction: str  # what would change it, stated so it can fail (rule B4)
    model: str | None = None  # None: every model; else the one it belongs to (rule A7)

    def __post_init__(self) -> None:
        if self.model is not None and not IDENT.match(self.model):
            raise SpecError(f"row {self.row}: model {self.model!r} must be a model name or None")
        if self.row not in {q.n for q in QUANTITIES}:
            raise SpecError(f"recorded drift names row {self.row}, which is not in the acceptance table")
        if self.knob not in {k.name for k in KNOBS}:
            raise SpecError(f"row {self.row}: knob {self.knob!r} is not swept")
        if self.debt < 1 or not self.since.startswith("S"):
            raise SpecError(f"row {self.row}: a recorded drift needs a debt number and a session")
        if not self.reason.strip() or not self.prediction.strip():
            raise SpecError(f"row {self.row}: a recorded drift needs a reason and a prediction")


_RECORDED: tuple[Recorded, ...] = ()


def recorded(model: str) -> Mapping[tuple[int, str], Recorded]:
    """The recorded drifts that apply to ``model``: the shared ones and its own (rule A7)."""
    out: dict[tuple[int, str], Recorded] = {}
    for d in _RECORDED:
        if d.model is None or d.model == model:
            key = (d.row, d.knob)
            if key in out:
                raise SpecError(f"row {d.row} knob {d.knob} is recorded twice for model {model!r}")
            out[key] = d
    return MappingProxyType(out)


@dataclass(frozen=True, slots=True)
class Drift:
    """One acceptance row swept over one knob, in one model."""

    row: int
    name: str
    model: str
    knob: str
    baseline: float | str
    points: tuple[tuple[int, float | str], ...]
    drift: float | None  # absolute, largest over the sweep; None for a category
    width: float | None  # the acceptance interval's width; None where the row has no interval
    status: str

    @property
    def relative(self) -> float | None:
        """The drift as a fraction of the default value, where that means anything."""
        if self.drift is None or not isinstance(self.baseline, float) or self.baseline == 0.0:
            return None
        return self.drift / abs(self.baseline)

    @property
    def margin(self) -> float | None:
        """The drift in units of the target's width — the number the verdict is read off.

        Published because the verdict alone hides how much room there was: a row
        at 0.001 widths and a row at 0.9 widths both print ``converged`` and are
        not the same finding (rule B6).
        """
        if self.drift is None or not self.width:
            return None
        return self.drift / self.width


@dataclass(frozen=True, slots=True)
class Control:
    """What one knob did at a deliberately too-coarse value (rule B3)."""

    model: str
    knob: str
    value: int
    fired: tuple[int, ...]  # acceptance rows whose drift exceeded their target's width
    expected: bool  # whether the criterion fired when this was measured

    @property
    def ok(self) -> bool:
        return bool(self.fired) == self.expected


@dataclass(frozen=True, slots=True)
class Audit:
    """One model's whole convergence result: the sweep and its controls."""

    model: str
    drifts: tuple[Drift, ...]
    controls: tuple[Control, ...]


def swept_fields(quantities: Iterable[Quantity] = QUANTITIES) -> tuple[str, ...]:
    """Every acceptance row's field, in table order, once each."""
    seen: dict[str, None] = {}
    for q in quantities:
        if q.field is not None:
            seen.setdefault(q.field, None)
    return tuple(seen)


def _value(fields: Mapping[str, Any], q: Quantity) -> float | str | None:
    assert q.field is not None
    if q.field not in fields:
        return None
    raw = fields[q.field]
    return raw if q.mode == "qualitative" else float(raw)


def _judge(
    q: Quantity,
    model: str,
    knob: str,
    baseline: float | str,
    points: Sequence[tuple[int, float | str]],
) -> Drift:
    if q.mode == "qualitative":
        changed = any(v != baseline for _, v in points)
        return Drift(q.n, q.name, model, knob, baseline, tuple(points), None, None, "drifts" if changed else "converged")
    assert isinstance(baseline, float)
    drift = max((abs(float(v) - baseline) for _, v in points), default=0.0)
    width = None if q.lo is None or q.hi is None else q.hi - q.lo
    if width is None or width == 0.0:
        status = "no-target-width"
    else:
        status = "drifts" if drift > width else "converged"
    return Drift(q.n, q.name, model, knob, baseline, tuple(points), drift, width, status)


def sweep(
    model: Model,
    knobs: Iterable[Knob] = KNOBS,
    quantities: Iterable[Quantity] = QUANTITIES,
    **run_kwargs: Any,
) -> Audit:
    """Every acceptance row of ``model``, swept over every knob independently."""
    from galaxy.run import run as _run

    quantities = [q for q in quantities if q.field is not None]
    wanted = swept_fields(quantities)

    def values(spec: GridSpec) -> Mapping[str, Any]:
        return _run(model, grid=spec, only=wanted, **run_kwargs).fields

    def judged(knob: str, base: Mapping[str, Any], runs: Sequence[tuple[int, Mapping[str, Any]]]) -> list[Drift]:
        out: list[Drift] = []
        for q in quantities:
            baseline = _value(base, q)
            if baseline is None:
                continue  # not published by this model: not-yet-computable there, unswept here
            points = [(n, _value(f, q)) for n, f in runs]
            if any(v is None for _, v in points):
                continue
            out.append(_judge(q, model.name, knob, baseline, [(n, v) for n, v in points if v is not None]))
        return out

    base = values(DEFAULT_GRID)
    drifts: list[Drift] = []
    controls: list[Control] = []
    for knob in knobs:
        drifts += judged(knob.name, base, [(n, values(g)) for n, g in knob.specs()])
        fired = [d.row for d in judged(knob.name, base, [(knob.control, values(knob.control_spec()))])
                 if d.status == "drifts"]
        controls.append(Control(model.name, knob.name, knob.control, tuple(fired), knob.control_fires))
    return Audit(model.name, tuple(drifts), tuple(controls))


def sweep_models(models: Iterable[Model], **kwargs: Any) -> dict[str, Audit]:
    return {m.name: sweep(m, **kwargs) for m in models}


def unrecorded(audit: Audit) -> tuple[Drift, ...]:
    known = recorded(audit.model)
    return tuple(d for d in audit.drifts if d.status == "drifts" and (d.row, d.knob) not in known)


def stale(audit: Audit) -> tuple[Drift, ...]:
    """A recorded drift that has converged: the explanation is spent (rule B10)."""
    known = recorded(audit.model)
    return tuple(d for d in audit.drifts if d.status == "converged" and (d.row, d.knob) in known)


def problems(audit: Audit) -> list[Problem]:
    model = audit.model
    known = recorded(model)
    out = [
        Problem(
            model,
            "convergence",
            f"row {d.row} ({d.name}) moves by {d.drift:.6g} when {d.knob} is swept, more than its "
            f"target's width {d.width:.6g}, and is not a recorded drift",
        )
        for d in unrecorded(audit)
    ]
    out += [
        Problem(
            model,
            "stale-drift",
            f"row {d.row} ({d.name}) is recorded as drifting in {d.knob} since "
            f"{known[(d.row, d.knob)].since} (debt #{known[(d.row, d.knob)].debt}) but now converges "
            f"({d.drift:.6g} within {d.width:.6g}). Remove the entry or find out why.",
        )
        for d in stale(audit)
    ]
    out += [
        Problem(
            model,
            "control",
            f"the control at {c.knob} = {c.value} "
            + (
                f"fired on rows {list(c.fired)}, and was measured not to fire: N_{c.knob[2:]} has "
                f"acquired an acceptance row that can see it, which is a finding, not a pass"
                if c.fired
                else f"fired on nothing, so the criterion cannot be shown to fire in {c.knob} at all "
                f"and a converged sweep is indistinguishable from a broken instrument (rule B3)"
            ),
        )
        for c in audit.controls
        if not c.ok
    ]
    return out


def check(
    models: Iterable[Model],
    results: Mapping[str, Audit] | None = None,
    **kwargs: Any,
) -> list[Problem]:
    """Every convergence problem across ``models``. Empty means the gate holds.

    ``results`` is the sweep if it has already been run: a sweep is twenty
    galaxies and is not worth building twice.
    """
    if results is None:
        results = sweep_models(models, **kwargs)
    return [p for a in results.values() for p in problems(a)]


def _cell(v: float | str) -> str:
    return f"{v:.6g}" if isinstance(v, float) else str(v)


def report(
    models: Iterable[Model],
    results: Mapping[str, Audit] | None = None,
    knobs: Iterable[Knob] = KNOBS,
    **kwargs: Any,
) -> str:
    models = list(models)
    knobs = list(knobs)
    if results is None:
        results = sweep_models(models, knobs=knobs, **kwargs)
    lines = ["convergence"]
    for k in knobs:
        lines.append(
            f"  knob {k.name}: {getattr(DEFAULT_GRID, k.name)} (default) against {list(k.points)}, "
            f"control {k.control} — {k.about}"
        )
    for m in models:
        audit = results[m.name]
        drifts = audit.drifts
        known = recorded(m.name)
        counts = {s: sum(1 for d in drifts if d.status == s) for s in STATUSES}
        worst = max((d.margin for d in drifts if d.margin is not None), default=0.0)
        lines.append(
            f"  model {m.name}: {counts['converged']} converged, {counts['drifts']} drift, "
            f"{counts['no-target-width']} with no target width, of {len(drifts)} row-knob pairs; "
            f"worst margin {worst:.4g} of a target width"
        )
        for d in drifts:
            points = " ".join(f"{n}:{_cell(v)}" for n, v in d.points)
            if d.drift is None:
                measure = "category unchanged" if d.status == "converged" else "category changed"
            else:
                rel = "" if d.relative is None else f" ({d.relative:.2%} of the value)"
                against = "no width" if d.width in (None, 0.0) else f"{d.margin:.4g} of width {d.width:.6g}"
                measure = f"drift {d.drift:.6g}{rel}, {against}"
            tag = ""
            if (d.row, d.knob) in known and d.status == "drifts":
                r = known[(d.row, d.knob)]
                tag = f" [recorded drift, debt #{r.debt}, since {r.since}]"
            lines.append(
                f"    {d.row:>2} {d.knob:<4} {d.status:<16} {d.name}: default {_cell(d.baseline)}, "
                f"{points}; {measure}{tag}"
            )
        for c in audit.controls:
            verdict = f"fires on rows {list(c.fired)}" if c.fired else "fires on nothing"
            lines.append(
                f"    control {c.knob} = {c.value}: {verdict} "
                f"({'as measured' if c.ok else 'NOT as measured'})"
            )
        for p in problems(audit):
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
