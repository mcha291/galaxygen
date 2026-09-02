"""Stage declarations and the restricted context a stage computes in.

A :class:`Stage` is an implementation of a *slot* (``halo``, ``chemistry``…).
A model maps slots to implementations; two models share a stage wherever the
implementation is identical (GALAXY_PLAN.md §2).

A stage declares everything it reads and everything it publishes. At run time it
receives a :class:`Context` whose mappings expose *only* the declared names and
raise :class:`UndeclaredAccess` for anything else. This is rule B13 applied to
rule A8: a stage cannot quietly depend on an input, constant or field it did not
declare, so the graph the specs audit is the graph that actually runs.

Optional fields (present in some models only) are declared in
``requires_optional`` and are reachable only through ``ctx.fields.get(name)`` or
``ctx.fields.has(name)``; ``ctx.fields[name]`` raises even when the field is
present. Handling absence is therefore not something a reader can forget.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from . import seeds as _seeds
from .fielddoc import CONST_IDENT, IDENT, FieldDecl

# The stage grouping hypothesis of GALAXY_PLAN.md §3. Index + 1 is the
# checkpoint number a stage declares; graph.py checks the hypothesis.
CHECKPOINTS: tuple[str, ...] = (
    "Halo & disc",
    "Assembly",
    "Star formation & chemistry",
    "Pattern",
    "Systems",
    "Planets",
)


class UndeclaredAccess(KeyError):
    """A stage read a name it did not declare."""


class OptionalFieldAccess(KeyError):
    """A stage subscripted an optional field; use ``.get()`` or ``.has()``."""


class StageError(ValueError):
    """A stage declaration violates the contract."""


class Restricted(Mapping[str, Any]):
    """Read-only view of ``data`` exposing only ``allowed`` names."""

    __slots__ = ("_data", "_allowed", "_optional", "_what", "_stage")

    def __init__(
        self,
        data: Mapping[str, Any],
        allowed: Iterable[str],
        what: str,
        stage: str,
        optional: Iterable[str] = (),
    ) -> None:
        self._data = data
        self._allowed = frozenset(allowed)
        self._optional = frozenset(optional)
        self._what = what
        self._stage = stage

    def _check(self, key: str) -> None:
        if key not in self._allowed and key not in self._optional:
            raise UndeclaredAccess(
                f"stage {self._stage!r} read {self._what} {key!r} without declaring it; "
                f"declared: {sorted(self._allowed | self._optional)}"
            )

    def __getitem__(self, key: str) -> Any:
        self._check(key)
        if key in self._optional:
            raise OptionalFieldAccess(
                f"stage {self._stage!r}: {key!r} is optional; use .get({key!r}) or .has({key!r})"
            )
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        self._check(key)
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        self._check(key)
        return key in self._data

    def __contains__(self, key: object) -> bool:
        return (
            isinstance(key, str)
            and (key in self._allowed or key in self._optional)
            and key in self._data
        )

    def __iter__(self) -> Iterator[str]:
        return (k for k in self._data if k in self._allowed or k in self._optional)

    def __len__(self) -> int:
        return sum(1 for _ in self)


class Context:
    """What a stage sees while computing. Built by the runner, one per stage."""

    __slots__ = ("grid", "inputs", "seeds", "constants", "fields", "stage")

    def __init__(
        self,
        stage: Stage,
        grid: Any,
        inputs: Mapping[str, Any],
        seeds: Mapping[str, int],
        constants: Mapping[str, Any],
        fields: Mapping[str, Any],
    ) -> None:
        self.stage = stage
        self.grid = grid
        self.inputs = Restricted(inputs, stage.reads_inputs, "input", stage.id)
        self.seeds = Restricted(seeds, stage.reads_seeds, "seed", stage.id)
        self.constants = Restricted(constants, stage.reads_constants, "constant", stage.id)
        self.fields = Restricted(fields, stage.requires, "field", stage.id, stage.requires_optional)

    def rng(self, seed_name: str, *path: _seeds.PathPart) -> np.random.Generator:
        """An independent stream for this stage under a declared seed.

        Keyed by slot, not implementation, so two implementations of one slot
        draw the same numbers at a fixed seed and differ only in what they do
        with them.
        """
        return _seeds.rng(self.seeds[seed_name], self.stage.slot, *path)


def _names(value: Iterable[str], what: str, stage: str, pattern: re.Pattern[str] = IDENT) -> tuple[str, ...]:
    out = tuple(value)
    for v in out:
        if not isinstance(v, str) or not pattern.match(v):
            raise StageError(f"stage {stage}: {what} entry {v!r} must match {pattern.pattern}")
    if len(set(out)) != len(out):
        raise StageError(f"stage {stage}: {what} has duplicates: {out}")
    return out


@dataclass(frozen=True, slots=True)
class Stage:
    id: str  # implementation id, unique across the registry
    slot: str  # the stage slot this implements
    checkpoint: int  # 1..len(CHECKPOINTS); the §3 hypothesis, checked by graph.py
    about: str
    compute: Callable[[Context], Mapping[str, Any]]
    reads_inputs: tuple[str, ...] = ()
    reads_seeds: tuple[str, ...] = ()
    reads_constants: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    requires_optional: tuple[str, ...] = ()
    publishes: tuple[FieldDecl, ...] = ()

    def __post_init__(self) -> None:
        for attr in ("id", "slot"):
            v = getattr(self, attr)
            if not isinstance(v, str) or not IDENT.match(v):
                raise StageError(f"stage {attr} {v!r} must match {IDENT.pattern}")
        if (
            not isinstance(self.checkpoint, int)
            or isinstance(self.checkpoint, bool)
            or not 1 <= self.checkpoint <= len(CHECKPOINTS)
        ):
            raise StageError(
                f"stage {self.id}: checkpoint must be 1..{len(CHECKPOINTS)}, got {self.checkpoint!r}"
            )
        if not isinstance(self.about, str) or not self.about.strip():
            raise StageError(f"stage {self.id}: an about line is required")
        if not callable(self.compute):
            raise StageError(f"stage {self.id}: compute must be callable")
        for attr in ("reads_inputs", "reads_seeds", "requires", "requires_optional"):
            object.__setattr__(self, attr, _names(getattr(self, attr), attr, self.id))
        object.__setattr__(
            self, "reads_constants", _names(self.reads_constants, "reads_constants", self.id, CONST_IDENT)
        )
        pubs = tuple(self.publishes)
        for p in pubs:
            if not isinstance(p, FieldDecl):
                raise StageError(f"stage {self.id}: publishes must be FieldDecl instances, got {p!r}")
        object.__setattr__(self, "publishes", pubs)
        names = [p.name for p in pubs]
        if len(set(names)) != len(names):
            raise StageError(f"stage {self.id}: publishes the same field twice: {names}")
        overlap = set(self.requires) & set(self.requires_optional)
        if overlap:
            raise StageError(f"stage {self.id}: {sorted(overlap)} in both requires and requires_optional")
        selfdep = set(names) & (set(self.requires) | set(self.requires_optional))
        if selfdep:
            raise StageError(f"stage {self.id}: requires what it publishes: {sorted(selfdep)}")

    @property
    def published_names(self) -> tuple[str, ...]:
        return tuple(p.name for p in self.publishes)

    @property
    def checkpoint_name(self) -> str:
        return CHECKPOINTS[self.checkpoint - 1]
