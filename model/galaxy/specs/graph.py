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
  A stage that extends another (``Stage.extends``, S27) republishes the base's
  fields at the base's provenance, because the base computes them in its own
  restricted view; only the extension's own fields see its extra reads.
  **Since S55 (D214) there is a fourth kind, and its unit is still the stage**
  (D55 kept): a *layer stage* - one that lives under ``galaxy/layer/`` and
  declares itself one - publishes synthetic fields, all of them, and no other
  stage publishes one. A stage that reads a synthetic field is seeded: its
  fields are functions of the inputs and a seed, and only the layer realises.
- **The randomness layer's readers** (invariant I4, S55). A *composed* field is a
  law applied to a realisation, and says so: ``FieldDecl(composed=True, neutral=...)``
  (gate G1: a declaration, never read off the axes - a phi-axis field tabulated in a
  pattern's own frame is physics and is not declared).
  A stage may require a composed or a synthetic field only if it is a declared
  *placement reader* (a census), a *composing stage* (it publishes a composed
  field itself) or a layer stage. Anything else is a physics stage reading a
  placement, and fails here. A base stage is judged on its own requirements, so
  an extension that composes does not lend its base the right.
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


# Where a layer stage lives (D214 section 2): the package its compute is written in.
LAYER_PACKAGE = "galaxy.layer"

# The inputs a ruling leaves without a reader, each with the ruling. Every other seed binds at its earliest
# reader's checkpoint, and one that no stage reads is reported unbound (``Graph.unbound_inputs``), which
# ``tests/test_spec.py`` holds empty. **Exactly one exception, named**: ``texture_seed`` feeds only fields the
# third build adds, and its first reader is P1's mode phases; no dummy reader is invented for it (rule A4).
# ``tests/test_layer.py`` fails the day a stage reads it - this entry is removed then.
UNREAD_BY_RULING: Mapping[str, str] = {
    "texture_seed": "DECISIONS.md D214 section 3: no stage reads it until BUILD_III phase P1",
}


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
        """The inputs no stage reads, less the one a ruling leaves unread (``UNREAD_BY_RULING``)."""
        return tuple(n for n, c in self.input_checkpoint.items() if c is None and n not in UNREAD_BY_RULING)

    @property
    def unread_by_ruling(self) -> tuple[str, ...]:
        """The inputs no stage reads because a ruling says none does yet."""
        return tuple(n for n, c in self.input_checkpoint.items() if c is None and n in UNREAD_BY_RULING)

    @property
    def placement_readers(self) -> tuple[str, ...]:
        """The census stages declared to consume a composed weight or a synthetic field, in execution order."""
        return tuple(st.id for st in self.order if st.placement_reader)

    @property
    def composing_stages(self) -> tuple[str, ...]:
        """The stages that publish a field declared composed, in execution order."""
        return tuple(st.id for st in self.order if st.composes)

    @property
    def layer_stages(self) -> tuple[str, ...]:
        """The randomness layer's realisation stages, in execution order."""
        return tuple(st.id for st in self.order if st.layer_stage)

    @property
    def ok(self) -> bool:
        return not self.problems

    def needed_for(self, fields: Iterable[str]) -> tuple[Stage, ...]:
        """The stages that must run to publish ``fields``, in execution order.

        This is rule D4's arithmetic: the transitive closure of the dependency
        edges above the requested fields, and nothing else. A name no stage of
        this model publishes contributes nothing — the caller asked for a field
        this model does not have, which is the same answer as an empty closure
        and is what leaves an acceptance row not-yet-computable rather than
        failing (``spec.evaluate``).

        Optional requirements are followed only when this model has a producer
        for them, which is exactly the rule the edges were built under.
        """
        wanted = {self.producer[n] for n in fields if n in self.producer}
        frontier = list(wanted)
        while frontier:
            sid = frontier.pop()
            for name in self.stages[sid].requires + self.stages[sid].requires_optional:
                dep = self.producer.get(name)
                if dep is not None and dep not in wanted:
                    wanted.add(dep)
                    frontier.append(dep)
        return tuple(st for st in self.order if st.id in wanted)


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


def stage_provenance(st: Stage, known: Mapping[str, str]) -> dict[str, str]:
    """The provenance each field of ``st`` computes to, given what its inputs computed to.

    Per stage (D55): a stage that reads a seed, or requires a seeded field, publishes seeded
    fields, all of them. The one refinement is an extension (``Stage.extends``, S27): the
    fields it republishes are computed by its base in the base's own restricted view, so they
    take the base's provenance, and only the extension's own fields see its extra reads.
    """
    if st.layer_stage:
        # S55 (D214 section 2): the layer's stage is the unit of the fourth kind. Whatever seed it draws on, what
        # it publishes is a realisation standing in for physics the model does not compute.
        out = {name: "synthetic" for name in st.published_names}
    else:
        # A synthetic field is a function of the inputs and a seed too, so its readers are seeded; only a layer
        # stage publishes synthetic.
        seeded = bool(st.reads_seeds) or any(
            known.get(n) in ("seeded", "synthetic") for n in st.requires + st.requires_optional
        )
        out = {name: ("seeded" if seeded else "derived") for name in st.published_names}
    if st.extends is not None:
        out.update(stage_provenance(st.extends, known))
    return out


def layer_problems(model: Model, stages: Mapping[str, Stage]) -> list[Problem]:
    """Invariant I4 and where a layer stage lives (S55, D214 sections 1 and 2).

    A stage that requires a field declared composed or a synthetic one is a placement reader, a composing
    stage or a layer stage, or it is a problem; a base is judged on its own requirements. A stage declares
    itself a layer stage exactly when its compute lives under ``galaxy/layer/``.
    """
    decl = {d.name: d for st in stages.values() for d in st.publishes}
    problems: list[Problem] = []

    def judge(st: Stage, sid: str) -> None:
        if not st.may_place:
            for name in st.requires + st.requires_optional:
                d = decl.get(name)
                if d is None or not (d.composed or d.provenance == "synthetic"):
                    continue
                what = "declared composed (a law applied to a realisation)" if d.composed else "synthetic"
                via = "" if st.id == sid else f" through its base {st.id!r}"
                problems.append(Problem(
                    model.name, "layer-reader",
                    f"stage {sid!r}{via} requires {name!r}, which is {what}, and is neither a placement reader, "
                    "a composing stage nor a layer stage: no physics stage reads the randomness layer (invariant I4)",
                ))
        if st.extends is not None:
            judge(st.extends, sid)

    for sid, st in stages.items():
        judge(st, sid)
        lives = st.home == LAYER_PACKAGE or st.home.startswith(LAYER_PACKAGE + ".")
        if st.layer_stage and not lives:
            problems.append(Problem(
                model.name, "layer-stage",
                f"stage {sid!r} declares itself a layer stage but its compute lives in {st.home or 'no module'!r}, "
                f"not under {LAYER_PACKAGE}",
            ))
        elif lives and not st.layer_stage:
            problems.append(Problem(
                model.name, "layer-stage",
                f"stage {sid!r} lives in {st.home!r} and does not declare itself a layer stage (layer_stage=True)",
            ))
    return problems


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
        computed_for = stage_provenance(st, provenance)
        for decl in st.publishes:
            computed = computed_for[decl.name]
            provenance[decl.name] = computed
            if decl.provenance != computed:
                problems.append(
                    Problem(
                        model.name,
                        "provenance",
                        f"field {decl.name!r} is declared {decl.provenance} but computed {computed} in stage {st.id!r}",
                    )
                )

    # The randomness layer's readers and its stages (invariant I4, S55).
    problems.extend(layer_problems(model, stages))

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
        for name in g.unread_by_ruling:
            lines.append(f"    input unread by ruling: {name} ({UNREAD_BY_RULING[name]})")
        lines.append("    layer stages: " + (", ".join(g.layer_stages) or "(none)"))
        lines.append("    composing stages: " + (", ".join(g.composing_stages) or "(none)"))
        lines.append("    placement readers: " + (", ".join(g.placement_readers) or "(none)"))
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
