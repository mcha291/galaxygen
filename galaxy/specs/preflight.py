"""preflight: declarations reconcile within a model and across models (rule A8).

Per model:

- every slot resolves to a registered implementation of that slot
- every input, seed and constant a stage reads is declared and exists
- every constant a model declares is read by some stage (no dead constants)
- every strictly required field is published earlier in that model
- a field declared optional is only ever read through ``requires_optional``
- a field read through ``requires_optional`` is actually optional somewhere

Across models:

- the same field name carries the same contract everywhere (``FieldDecl.contract``)
- a field published by some models and not all is declared optional

Orphans, by scanning ``galaxy.stages`` modules:

- every ``Stage`` found is registered and used by at least one model
- every ``FieldDecl`` found is published by a registered stage

Preflight also reports, without failing, the debts the registry carries:
inputs whose default is UNSET and controls without a range. The S10 audit
expects both to be zero.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from galaxy.core.fielddoc import FieldDecl
from galaxy.core.registry import INPUT_CEILING, Input, Model, Registry, controls, production
from galaxy.core.stage import Stage
from galaxy.specs import Problem, utf8_stdout
from galaxy.specs.graph import resolve_stages

SCAN_PACKAGES: tuple[str, ...] = ("galaxy.stages",)


@dataclass
class Report:
    problems: list[Problem] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def scan_declarations(packages: Iterable[str]) -> tuple[list[Stage], list[FieldDecl]]:
    """Every Stage and FieldDecl bound at module level in ``packages`` (recursively)."""
    stages: dict[int, Stage] = {}
    decls: dict[int, FieldDecl] = {}

    def collect(value: object) -> None:
        if isinstance(value, Stage):
            stages[id(value)] = value
            for d in value.publishes:
                decls[id(d)] = d
        elif isinstance(value, FieldDecl):
            decls[id(value)] = value
        elif isinstance(value, (tuple, list)):
            for v in value:
                collect(v)

    for pkg_name in packages:
        pkg = importlib.import_module(pkg_name)
        modules = [pkg]
        if hasattr(pkg, "__path__"):
            for info in pkgutil.walk_packages(pkg.__path__, prefix=pkg_name + "."):
                modules.append(importlib.import_module(info.name))
        for mod in modules:
            for value in vars(mod).values():
                collect(value)
    return list(stages.values()), list(decls.values())


def _impl(impls: Registry[Stage] | Mapping[str, Stage], impl_id: str) -> Stage:
    return impls[impl_id] if isinstance(impls, Mapping) else impls.get(impl_id)


def check(
    models: Iterable[Model],
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
    *,
    scan: Iterable[str] | None = SCAN_PACKAGES,
) -> Report:
    models = list(models)
    rep = Report()
    P = rep.problems.append

    # Which models publish which field, and with which declaration.
    published_in: dict[str, dict[str, FieldDecl]] = {}  # field -> {model -> decl}
    resolved: dict[str, dict[str, Stage]] = {}
    seed_names = {n for n, i in table.items() if i.kind == "seed"}

    for m in models:
        stages, probs = resolve_stages(m, impls)
        rep.problems.extend(probs)
        resolved[m.name] = stages
        accepted = set(m.input_names(table))
        unknown_accepted = accepted - set(table)
        if unknown_accepted:
            P(Problem(m.name, "unknown-input", f"model accepts {sorted(unknown_accepted)}, which are not in the input table"))

        read_constants: set[str] = set()
        for sid, st in stages.items():
            for name in st.reads_inputs:
                if name not in accepted:
                    P(Problem(m.name, "unknown-input", f"stage {sid!r} reads input {name!r}, not accepted by this model"))
                elif name in seed_names:
                    P(Problem(m.name, "seed-as-input", f"stage {sid!r} lists seed {name!r} in reads_inputs; seeds go in reads_seeds"))
            for name in st.reads_seeds:
                if name not in seed_names or name not in accepted:
                    P(Problem(m.name, "unknown-seed", f"stage {sid!r} reads seed {name!r}, which is not an accepted seed"))
            for name in st.reads_constants:
                if name not in m.constants:
                    P(Problem(m.name, "unknown-constant", f"stage {sid!r} reads constant {name!r}, which model {m.name!r} does not declare"))
                read_constants.add(name)
            for decl in st.publishes:
                published_in.setdefault(decl.name, {})[m.name] = decl
        dead = set(m.constants) - read_constants
        for name in sorted(dead):
            P(Problem(m.name, "dead-constant", f"constant {name!r} is declared but no stage reads it"))

    # Field reads, judged against every declaration anywhere.
    all_decls: dict[str, list[FieldDecl]] = {}
    for name, by_model in published_in.items():
        all_decls[name] = list(by_model.values())
    # An optional field is one some model lacks. A stage may still require it
    # strictly if every model that maps the stage publishes it: the advanced
    # model's own stages read the advanced model's own fields, and asking them to
    # handle an absence that cannot happen in any model they run in would be a
    # false declaration (S9, D86). What is refused is a *shared* stage requiring a
    # field that is absent in one of the models it is shared with.
    maps_stage: dict[str, set[str]] = {}
    for m in models:
        for sid in resolved[m.name]:
            maps_stage.setdefault(sid, set()).add(m.name)
    for m in models:
        stages = resolved[m.name]
        here = {n for n, by in published_in.items() if m.name in by}
        for sid, st in stages.items():
            for name in st.requires:
                decls = all_decls.get(name)
                if not decls:
                    P(Problem(m.name, "missing-required", f"stage {sid!r} requires {name!r}, which no model publishes"))
                elif name not in here:
                    P(Problem(m.name, "missing-required", f"stage {sid!r} requires {name!r}, which model {m.name!r} does not publish"))
                elif any(d.optional for d in decls) and not maps_stage[sid] <= set(published_in[name]):
                    absent = sorted(maps_stage[sid] - set(published_in[name]))
                    P(Problem(m.name, "optional-read-strict", f"stage {sid!r} requires optional field {name!r}, which {absent} map it without; move it to requires_optional"))
            for name in st.requires_optional:
                decls = all_decls.get(name)
                if not decls:
                    P(Problem(m.name, "optional-unpublished", f"stage {sid!r} optionally reads {name!r}, which no model publishes"))
                elif not any(d.optional for d in decls):
                    P(Problem(m.name, "optional-read-of-required", f"stage {sid!r} reads {name!r} as optional, but it is declared non-optional everywhere"))

    # Cross-model reconciliation.
    model_names = [m.name for m in models]
    for name, by_model in sorted(published_in.items()):
        contracts = {d.contract() for d in by_model.values()}
        if len(contracts) > 1:
            P(Problem("*", "contract-mismatch", f"field {name!r} is declared differently across models {sorted(by_model)}"))
        missing = [mn for mn in model_names if mn not in by_model]
        if missing and not all(d.optional for d in by_model.values()):
            P(Problem("*", "undeclared-optional", f"field {name!r} is published by {sorted(by_model)} but not by {missing}; declare it optional"))
        if not missing and len(model_names) > 1 and all(d.optional for d in by_model.values()):
            rep.notes.append(f"field {name!r} is declared optional but every model publishes it")

    # Orphans.
    if scan:
        found_stages, found_decls = scan_declarations(scan)
        used = {impl_id for m in models for _, impl_id in m.stages}
        for st in found_stages:
            if st.id not in impls:
                P(Problem("*", "orphan-stage", f"stage {st.id!r} is defined but not registered"))
            elif _impl(impls, st.id) is not st:
                P(Problem("*", "orphan-stage", f"stage {st.id!r} is defined but a different object is registered under that id"))
            elif st.id not in used:
                P(Problem("*", "orphan-stage", f"stage {st.id!r} is registered but no model uses it"))
        attached = {id(d) for impl_id in used if impl_id in impls for d in _impl(impls, impl_id).publishes}
        for d in found_decls:
            if id(d) not in attached:
                P(Problem("*", "orphan-declaration", f"field {d.name!r} is declared but no stage of any model publishes it"))

    # The input table itself.
    n_controls = len(controls(table))
    if n_controls > INPUT_CEILING:
        P(Problem("*", "ceiling", f"{n_controls} controls exceed the ceiling of {INPUT_CEILING}"))
    unset = [i.name for i in table.values() if i.unset]
    noranges = [i.name for i in controls(table) if not i.has_range]
    rep.notes.append(f"controls: {n_controls} of {INPUT_CEILING}")
    rep.notes.append(f"inputs with UNSET default: {len(unset)}" + (f" ({', '.join(f'{n}<-{table[n].default_owner}' for n in unset)})" if unset else ""))
    rep.notes.append(f"controls without a range: {len(noranges)}" + (f" ({', '.join(noranges)})" if noranges else ""))
    return rep


def report(
    models: Iterable[Model],
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
) -> str:
    models = list(models)
    rep = check(models, impls, table)
    lines = ["preflight", f"  models: {', '.join(m.name for m in models)}"]
    lines.append("  " + ("OK" if rep.ok else f"{len(rep.problems)} problem(s)"))
    for p in rep.problems:
        lines.append(f"    FAIL {p}")
    for n in rep.notes:
        lines.append(f"    note: {n}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, impls, table = production()
    print(report(models, impls, table))
    return 0 if check(models, impls, table).ok else 1


if __name__ == "__main__":
    sys.exit(main())
