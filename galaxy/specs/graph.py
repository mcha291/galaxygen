"""graph: the dependency structure of one model, checked per model (rule A6).

Nodes are stages; an edge runs from the stage that publishes a field to every
stage that requires it. The graph must be acyclic per model, and the execution
order the runner uses is the topological order computed here, so what is
audited is what runs.

Beyond acyclicity this module checks three things the plan makes load-bearing:

- **Checkpoint order.** A stage may only require fields from stages at the same
  or an earlier checkpoint; otherwise confirming a checkpoint would not lock its
  prefix (rule D1).
- **Checkpoint hypotheses.** GALAXY_PLAN.md §3 assigns each input and seed to a
  checkpoint. The *derived* checkpoint of an input is the earliest checkpoint of
  any stage that reads it. Where both exist and differ, the hypothesis is dead
  (rule B4). Inputs no stage reads yet are reported as unbound, not failed.
- **Provenance** (rule A10). A field is seeded if its stage reads a seed or
  requires a seeded field; otherwise it is derived. The declaration must agree.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from galaxy.core.registry import Input, Model, Registry, production
from galaxy.core.stage import Stage
from galaxy.specs import Problem, utf8_stdout


class GraphError(ValueError):
    """The graph cannot be built: a cycle, an unknown implementation, or a missing producer."""


@dataclass
class Graph:
    model: Model
    stages: dict[str, Stage]  # implementation id -> Stage, for every slot of the model
    producer: dict[str, str]  # field name -> implementation id
    order: tuple[Stage, ...]  # execution order; empty if a cycle prevents one
    input_checkpoint: dict[str, int | None]  # input/seed name -> derived checkpoint, None if unbound
    provenance: dict[str, str]  # field name -> computed provenance
    problems: list[Problem] = field(default_factory=list)

    @property
    def unbound_inputs(self) -> tuple[str, ...]:
        return tuple(n for n, c in self.input_checkpoint.items() if c is None)

    @property
    def ok(self) -> bool:
        return not self.problems


def resolve_stages(
    model: Model, impls: Registry[Stage] | Mapping[str, Stage]
) -> tuple[dict[str, Stage], list[Problem]]:
    """Map every slot of ``model`` to its implementation, recording what fails to resolve."""
    problems: list[Problem] = []
    stages: dict[str, Stage] = {}
    for slot, impl_id in model.stages:
        if impl_id not in impls:
            problems.append(Problem(model.name, "unknown-implementation", f"slot {slot!r} -> {impl_id!r} is not registered"))
            continue
        stage = impls[impl_id] if isinstance(impls, Mapping) else impls.get(impl_id)
        if stage.slot != slot:
            problems.append(
                Problem(model.name, "slot-mismatch", f"slot {slot!r} maps to {impl_id!r}, which implements slot {stage.slot!r}")
            )
            continue
        stages[impl_id] = stage
    return stages, problems


def analyse(
    model: Model,
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
) -> Graph:
    """Build the graph and collect every problem. Never raises."""
    stages, problems = resolve_stages(model, impls)

    producer: dict[str, str] = {}
    for sid, st in stages.items():
        for name in st.published_names:
            if name in producer:
                problems.append(Problem(model.name, "duplicate-field", f"{name!r} published by both {producer[name]!r} and {sid!r}"))
            else:
                producer[name] = sid

    # Edges: producer -> consumer. Optional requires create edges too (order matters
    # when the field is present); a missing optional producer is fine.
    deps: dict[str, set[str]] = {sid: set() for sid in stages}
    for sid, st in stages.items():
        for name in st.requires:
            if name in producer:
                deps[sid].add(producer[name])
            else:
                problems.append(Problem(model.name, "missing-producer", f"stage {sid!r} requires {name!r}, which no stage of this model publishes"))
        for name in st.requires_optional:
            if name in producer:
                deps[sid].add(producer[name])

    # Kahn's algorithm with a deterministic tie-break.
    remaining = {sid: set(d) for sid, d in deps.items()}
    order: list[Stage] = []
    while remaining:
        ready = sorted((sid for sid, d in remaining.items() if not d), key=lambda s: (stages[s].checkpoint, s))
        if not ready:
            cyc = sorted(remaining)
            problems.append(Problem(model.name, "cycle", f"stages {cyc} depend on each other"))
            order = []
            break
        for sid in ready:
            order.append(stages[sid])
            del remaining[sid]
            for d in remaining.values():
                d.discard(sid)

    # Checkpoint order: a required field must come from the same or an earlier checkpoint.
    for sid, st in stages.items():
        for name in st.requires + st.requires_optional:
            p = producer.get(name)
            if p is not None and stages[p].checkpoint > st.checkpoint:
                problems.append(
                    Problem(
                        model.name,
                        "checkpoint-order",
                        f"stage {sid!r} (checkpoint {st.checkpoint}) requires {name!r} from {p!r} (checkpoint {stages[p].checkpoint})",
                    )
                )

    # Provenance (rule A10), computed along the order.
    provenance: dict[str, str] = {}
    for st in order:
        seeded = bool(st.reads_seeds) or any(
            provenance.get(n) == "seeded" for n in st.requires + st.requires_optional
        )
        computed = "seeded" if seeded else "derived"
        for decl in st.publishes:
            provenance[decl.name] = computed
            if decl.provenance != computed:
                problems.append(
                    Problem(
                        model.name,
                        "provenance",
                        f"field {decl.name!r} is declared {decl.provenance} but computed {computed} in stage {st.id!r}",
                    )
                )

    # Input and seed checkpoints: derived from readers, compared to the hypothesis.
    accepted = set(model.input_names(table))
    input_checkpoint: dict[str, int | None] = {}
    for name, inp in table.items():
        if name not in accepted:
            continue
        readers = [
            st for st in stages.values() if name in (st.reads_seeds if inp.kind == "seed" else st.reads_inputs)
        ]
        derived = min((st.checkpoint for st in readers), default=None)
        input_checkpoint[name] = derived
        if derived is not None and inp.checkpoint_hypothesis is not None and derived != inp.checkpoint_hypothesis:
            problems.append(
                Problem(
                    model.name,
                    "hypothesis",
                    f"{inp.kind} {name!r}: GALAXY_PLAN.md §3 puts it at checkpoint {inp.checkpoint_hypothesis}, "
                    f"but it is first read at checkpoint {derived} by {sorted(st.id for st in readers if st.checkpoint == derived)}",
                )
            )
    for st in stages.values():
        for name in st.reads_inputs + st.reads_seeds:
            if name not in accepted:
                problems.append(Problem(model.name, "unknown-input", f"stage {st.id!r} reads {name!r}, which model {model.name!r} does not accept"))

    return Graph(model, stages, producer, tuple(order), input_checkpoint, provenance, problems)


def build(
    model: Model,
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
) -> Graph:
    """The graph for the runner. Raises :class:`GraphError` on anything that prevents execution."""
    g = analyse(model, impls, table)
    fatal = [p for p in g.problems if p.code in ("cycle", "unknown-implementation", "slot-mismatch", "missing-producer", "duplicate-field", "unknown-input")]
    if fatal:
        raise GraphError("; ".join(str(p) for p in fatal))
    return g


def check(
    models: Iterable[Model],
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
) -> list[Problem]:
    """Every graph problem across ``models``. Empty means the gate holds."""
    out: list[Problem] = []
    for m in models:
        out.extend(analyse(m, impls, table).problems)
    return out


def report(
    models: Iterable[Model],
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
) -> str:
    lines: list[str] = ["graph"]
    for m in models:
        g = analyse(m, impls, table)
        lines.append(f"  model {m.name}: {'OK' if g.ok else f'{len(g.problems)} problem(s)'}")
        lines.append("    order: " + (" -> ".join(f"{s.id}@{s.checkpoint}" for s in g.order) or "(none)"))
        for name, sid in sorted(g.producer.items()):
            lines.append(f"    field {name}: {sid}, {g.provenance.get(name, '?')}")
        bound = {n: c for n, c in g.input_checkpoint.items() if c is not None}
        lines.append("    inputs bound: " + (", ".join(f"{n}@{c}" for n, c in sorted(bound.items())) or "(none)"))
        lines.append(f"    inputs unbound: {len(g.unbound_inputs)} " + (", ".join(g.unbound_inputs) if g.unbound_inputs else ""))
        for p in g.problems:
            lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, impls, table = production()
    print(report(models, impls, table))
    return 1 if check(models, impls, table) else 0


if __name__ == "__main__":
    sys.exit(main())
