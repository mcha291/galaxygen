"""The runner: execute one model on one grid with one input vector.

Stages run in the order ``specs/graph.py`` computes, each inside a
:class:`~galaxy.core.stage.Context` that exposes only what the stage declared.
What a stage returns is validated against its declarations: exactly the declared
names, each with the shape and value class its kind implies. A stage cannot
publish an undeclared field, forget a declared one, or hand back an ``(t, R)``
array for an ``(R, t)`` declaration.

Inputs are resolved from overrides, then registry defaults. An input whose
default is UNSET is only an error if some stage of the model reads it (rule B9:
a number is never substituted for a missing one).

**Partial runs** (rule D4). ``only=`` names the fields a caller actually wants,
and the runner executes the dependency closure above them and nothing else —
``graph.Graph.needed_for``. ``resume=`` hands back an earlier ``Outputs`` for
the same model, inputs and grid, and the stages already in it are not run again.
Together they are what lets an API answer a question without building the whole
galaxy, and what lets the spec ensemble stop rebuilding a star catalogue to read
a pattern speed (debt #24). Neither changes any value: a stage is a pure
function of its declared reads, so running fewer of them cannot move the ones
that do run — asserted rather than argued, in ``tests/test_run.py``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.grids import DEFAULT, Grid, GridSpec
from galaxy.core.registry import Input, Model, Registry, production
from galaxy.core.stage import Context, Stage
from galaxy.specs import graph as _graph


class RunError(RuntimeError):
    """The run could not proceed."""


class MissingInput(RunError):
    """A stage reads an input with no default and no override."""


class PublishError(RunError):
    """A stage returned something other than what it declared."""


@dataclass
class Outputs:
    model: str
    grid: Grid
    inputs: dict[str, Any]
    fields: dict[str, Any]
    decls: dict[str, FieldDecl]
    order: tuple[str, ...]  # implementation ids whose fields are present, in execution order
    ran: tuple[str, ...] = ()  # what this call executed; differs from order under resume=


def resolve_inputs(
    model: Model,
    overrides: Mapping[str, Any],
    table: Mapping[str, Input],
    needed: set[str],
) -> dict[str, Any]:
    accepted = model.input_names(table)
    unknown = set(overrides) - set(accepted)
    if unknown:
        raise RunError(f"model {model.name!r} does not accept inputs {sorted(unknown)}")
    out: dict[str, Any] = {}
    for name in accepted:
        inp = table[name]
        if name in overrides:
            out[name] = overrides[name]
        elif not inp.unset:
            out[name] = inp.default
        elif name in needed:
            raise MissingInput(
                f"input {name!r} has no default (owed by {inp.default_owner}) and none was given; "
                f"rule B9 forbids substituting one"
            )
    return out


def _check_value(decl: FieldDecl, value: Any, grid: Grid, stage: Stage, column_lengths: dict[str, int]) -> Any:
    kind = decl.kind
    where = f"stage {stage.id!r} field {decl.name!r}"
    if kind.domain == "grid":
        arr = np.asarray(value)
        expected = grid.shape(decl.axes)
        if arr.shape != expected:
            raise PublishError(f"{where}: shape {arr.shape} does not match axes {decl.axes} -> {expected}")
        if kind.categorical:
            if not np.issubdtype(arr.dtype, np.integer):
                raise PublishError(f"{where}: categorical fields are integer category codes, got {arr.dtype}")
            if arr.size and (arr.min() < 0 or arr.max() >= len(decl.categories)):
                raise PublishError(f"{where}: category codes must lie in [0, {len(decl.categories)})")
        elif not np.issubdtype(arr.dtype, np.floating):
            raise PublishError(f"{where}: continuous fields are floating arrays, got {arr.dtype}")
        return arr
    if kind.domain == "galaxy":
        if kind.categorical:
            if value not in decl.categories:
                raise PublishError(f"{where}: {value!r} is not one of {decl.categories}")
            return value
        if isinstance(value, bool) or np.ndim(value) != 0 or not isinstance(value, (int, float, np.number)):
            raise PublishError(f"{where}: a scalar must be a single number, got {type(value).__name__}")
        return float(value)
    # object domain
    arr = np.asarray(value)
    if arr.ndim != 1:
        raise PublishError(f"{where}: columns are 1-D, got shape {arr.shape}")
    assert decl.of is not None
    n = column_lengths.setdefault(decl.of, arr.shape[0])
    if arr.shape[0] != n:
        raise PublishError(f"{where}: {decl.of} columns must share one length; {arr.shape[0]} != {n}")
    if kind.categorical:
        if not np.issubdtype(arr.dtype, np.integer):
            raise PublishError(f"{where}: categorical columns are integer category codes, got {arr.dtype}")
        if arr.size and (arr.min() < 0 or arr.max() >= len(decl.categories)):
            raise PublishError(f"{where}: category codes must lie in [0, {len(decl.categories)})")
    elif not np.issubdtype(arr.dtype, np.floating):
        raise PublishError(f"{where}: continuous columns are floating arrays, got {arr.dtype}")
    return arr


def _check_resumable(model: Model, g: Grid, resolved: Mapping[str, Any], resume: Outputs) -> None:
    """``resume`` must describe the same galaxy, or its fields are someone else's.

    Checked rather than documented: a resumed run that silently mixes two input
    vectors would publish a self-consistent galaxy that no input vector
    generates, and nothing downstream could detect it (rule B13).
    """
    if resume.model != model.name:
        raise RunError(f"cannot resume model {model.name!r} from an {resume.model!r} run")
    if resume.grid.spec != g.spec:
        raise RunError(f"cannot resume: grid {resume.grid.spec} is not {g.spec}")
    for name in set(resolved) & set(resume.inputs):
        if resolved[name] != resume.inputs[name]:
            raise RunError(
                f"cannot resume: input {name!r} was {resume.inputs[name]!r} and is now {resolved[name]!r}"
            )


def run(
    model: Model,
    inputs: Mapping[str, Any] | None = None,
    grid: GridSpec | Grid | None = None,
    *,
    impls: Registry[Stage] | Mapping[str, Stage] | None = None,
    table: Mapping[str, Input] | None = None,
    only: Iterable[str] | None = None,
    resume: Outputs | None = None,
) -> Outputs:
    """Execute ``model``. ``only`` restricts the work to what those fields need (rule D4)."""
    if impls is None or table is None:
        _, prod_impls, prod_table = production()
        impls = prod_impls if impls is None else impls
        table = prod_table if table is None else table
    spec = DEFAULT if grid is None else grid
    g = spec.build() if isinstance(spec, GridSpec) else spec

    graph = _graph.build(model, impls, table)
    plan = graph.order if only is None else graph.needed_for(only)
    # Inputs are owed by the stages that actually run: pruning a stage prunes
    # its inputs too, so a partial run cannot be stopped by an UNSET default
    # that nothing on its path reads.
    needed = {n for st in plan for n in st.reads_inputs + st.reads_seeds}
    resolved = resolve_inputs(model, dict(inputs or {}), table, needed)
    seeds = {n: v for n, v in resolved.items() if table[n].kind == "seed"}
    constants = {k: c.value for k, c in model.constants.items()}

    fields: dict[str, Any] = {}
    decls: dict[str, FieldDecl] = {}
    column_lengths: dict[str, int] = {}
    done: tuple[str, ...] = ()
    if resume is not None:
        _check_resumable(model, g, resolved, resume)
        fields.update(resume.fields)
        decls.update(resume.decls)
        for name, decl in decls.items():
            if decl.kind.domain == "object":
                assert decl.of is not None
                column_lengths[decl.of] = len(fields[name])
        done = resume.order
        plan = tuple(st for st in plan if st.id not in set(done))

    for stage in plan:
        ctx = Context(stage, g, resolved, seeds, constants, fields)
        result = stage.compute(ctx)
        if not isinstance(result, Mapping):
            raise PublishError(f"stage {stage.id!r} must return a mapping of field name -> value")
        declared = set(stage.published_names)
        got = set(result)
        if got - declared:
            raise PublishError(f"stage {stage.id!r} published undeclared fields {sorted(got - declared)} (rule A8)")
        if declared - got:
            raise PublishError(f"stage {stage.id!r} declared but did not publish {sorted(declared - got)}")
        for decl in stage.publishes:
            fields[decl.name] = _check_value(decl, result[decl.name], g, stage, column_lengths)
            decls[decl.name] = decl
    ran = tuple(s.id for s in plan)
    order = tuple(st.id for st in graph.order if st.id in set(done) | set(ran))
    return Outputs(model.name, g, resolved, fields, decls, order, ran)
