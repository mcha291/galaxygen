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

**A stage may extend another implementation of its slot** (``extends``, S27): it
publishes everything the base publishes, under the base's own declarations,
*computed by the base's own compute in the base's own restricted view*, and then
its own fields on top (:class:`Extension`). The base's fields therefore cannot
see anything the extension reads beyond the base's declarations, and ``graph``
derives their provenance from the base's reads alone. That is what lets a second
implementation of a slot read a seeded field for one field of its own without
making every history it shares with the first a false *seeded* (rule A10, D55).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np

from . import seeds as _seeds
from .fielddoc import CONST_IDENT, IDENT, FieldDecl

# The stage grouping hypothesis of GALAXY_PLAN.md §3. Index + 1 is the
# checkpoint number a stage declares; graph.py checks the hypothesis.
CHECKPOINTS: tuple[str, ...] = (
    "Halo & disc",
    "Assembly",
    "Pattern",  # ahead of star formation since S25 (D174): the arms shape where stars form
    "Star formation & chemistry",
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


class LayerError(RuntimeError):
    """A mapping of fields does not say whether the randomness layer is on, or two that must agree do not."""


class Fields(dict):
    """A run's published fields, carrying the run's setting of the randomness layer (S55, D214 section 1).

    ``layer`` is what the run was asked for (``run(..., layer=...)``). It travels with the fields because a
    catalogue is materialised from a mapping of fields long after the run that made them - by a later stage,
    by the API for one window - and what it places by must be the run's: a catalogue with the layer's
    placements drawn from a run without them would be a galaxy no request generates. ``galaxy.layer.compose``
    is the one reader (rule B13); nothing here or in the runner branches on it. A plain ``dict`` of fields does
    not carry it and ``compose`` refuses one.
    """

    __slots__ = ("layer",)

    def __init__(self, data: Mapping[str, Any] | Iterable[tuple[str, Any]] = (), *, layer: bool) -> None:
        super().__init__(data)
        self.layer = bool(layer)


class FieldView(Restricted):
    """A stage's restricted view of the fields, carrying the run's layer setting and whether this stage may
    place by it: ``galaxy.layer.compose`` reads both, so a stage that hands ``ctx.fields`` to a materialiser
    hands the setting with it, and a stage that is neither a placement reader, a composing stage nor a layer
    stage is refused a composed weight (invariant I4, checked in the graph and again here at run time)."""

    __slots__ = ("layer", "placement")

    def __init__(self, data: Mapping[str, Any], stage: Stage, layer: bool) -> None:
        super().__init__(data, stage.requires, "field", stage.id, stage.requires_optional)
        self.layer = bool(layer)
        self.placement = stage.may_place


class Context:
    """What a stage sees while computing. Built by the runner, one per stage."""

    __slots__ = ("grid", "inputs", "seeds", "constants", "fields", "stage", "layer")

    def __init__(
        self,
        stage: Stage,
        grid: Any,
        inputs: Mapping[str, Any],
        seeds: Mapping[str, int],
        constants: Mapping[str, Any],
        fields: Mapping[str, Any],
        *,
        layer: bool = True,
    ) -> None:
        self.stage = stage
        self.grid = grid
        # Whether the run composes the randomness layer (S55, D214): carried, never read here. A stage does not
        # read it either - it asks galaxy.layer.compose, which answers with the neutral value when it is off.
        self.layer = bool(layer)
        self.inputs = Restricted(inputs, stage.reads_inputs, "input", stage.id)
        self.seeds = Restricted(seeds, stage.reads_seeds, "seed", stage.id)
        self.constants = Restricted(constants, stage.reads_constants, "constant", stage.id)
        self.fields = FieldView(fields, stage, self.layer)

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
    extends: Stage | None = None  # the implementation whose fields this one republishes (S27)
    # S55 (D214): the two declarations the graph holds invariant I4 with.
    # A *layer stage* lives under galaxy/layer/ and publishes synthetic fields, all of them (D55 kept: one
    # provenance per stage), and no other stage publishes one.
    layer_stage: bool = False
    # A *placement reader* is a census stage allowed to consume a composed placement weight or a synthetic
    # field. Any other stage that requires one fails the graph, unless it composes (publishes a field declared
    # composed) or is a layer stage itself.
    placement_reader: bool = False

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
        for attr in ("layer_stage", "placement_reader"):
            if not isinstance(getattr(self, attr), bool):
                raise StageError(f"stage {self.id}: {attr} is True or False, got {getattr(self, attr)!r}")
        if self.extends is not None:
            self._check_extension(self.extends)

    def _check_extension(self, base: Stage) -> None:
        """An extension reads at least what its base reads, publishes the base's declarations
        themselves, and computes them through the base (rule B13: not by convention)."""
        if not isinstance(base, Stage):
            raise StageError(f"stage {self.id}: extends must be a Stage, got {base!r}")
        if base.slot != self.slot:
            raise StageError(f"stage {self.id}: extends {base.id!r}, which implements slot {base.slot!r}, not {self.slot!r}")
        mine = {id(d) for d in self.publishes}
        lost = [d.name for d in base.publishes if id(d) not in mine]
        if lost:
            raise StageError(f"stage {self.id}: extends {base.id!r} but does not republish its declarations {lost}")
        for attr in ("reads_inputs", "reads_seeds", "reads_constants", "requires", "requires_optional"):
            missing = set(getattr(base, attr)) - set(getattr(self, attr))
            if missing:
                raise StageError(f"stage {self.id}: extends {base.id!r} but does not declare its {attr} {sorted(missing)}")

    def validate_registration(self) -> None:
        """What must hold for an implementation production runs, checked when it is registered.

        An extension's compute must be :class:`Extension` of its base, so the base's fields are
        computed by the base in the base's own view. Checked at registration rather than at
        construction so that an instrument may wrap or substitute a compute on an unregistered copy
        — ``replace(stage, compute=...)`` with ``run(impls=...)`` is how a mechanism is probed with
        the repository unchanged (D114) and how rule D4 is counted at the stages (S21 b) — without
        weakening the guarantee for anything a model runs.
        """
        base = self.extends
        if base is not None and (not isinstance(self.compute, Extension) or self.compute.base is not base):
            raise StageError(
                f"stage {self.id}: extends {base.id!r}, so its compute must be Extension({base.id}, ...) — "
                "the base's fields are computed by the base, in the base's own view"
            )

    @property
    def published_names(self) -> tuple[str, ...]:
        return tuple(p.name for p in self.publishes)

    @property
    def composes(self) -> bool:
        """A *composing stage*: it publishes a field declared composed (``FieldDecl(composed=True, neutral=...)``),
        a law applied to a realisation. It stays in ``stages/`` - its law is physics, and under ``layer/`` its
        fields would be synthetic, which they are not (D214, gate G1 changes 3 and 4)."""
        return any(p.composed for p in self.publishes)

    @property
    def may_place(self) -> bool:
        """Whether this stage may consume a composed weight or a synthetic field (invariant I4)."""
        return self.placement_reader or self.layer_stage or self.composes

    @property
    def home(self) -> str:
        """The module this stage's compute is written in: an extension's is its own half's. What says whether a
        stage lives under ``galaxy/layer/`` (D214 section 2)."""
        compute = getattr(self.compute, "own", self.compute)
        return str(getattr(compute, "__module__", "") or "")

    @property
    def checkpoint_name(self) -> str:
        return CHECKPOINTS[self.checkpoint - 1]


class Extension:
    """The compute of a stage that extends another (``Stage.extends``).

    Runs the base's own compute in a :class:`Context` restricted to the base's own
    declarations — nested inside the extension's, so it can reach nothing the base did
    not declare — then ``own(ctx, base_fields)`` for the extension's fields, which may
    read the base's results. The base's fields are returned unchanged: what the second
    implementation adds cannot alter what it shares with the first.
    """

    __slots__ = ("base", "own")

    def __init__(self, base: Stage, own: Callable[[Context, Mapping[str, Any]], Mapping[str, Any]]) -> None:
        self.base = base
        self.own = own

    def __call__(self, ctx: Context) -> Mapping[str, Any]:
        # The base's own view: its own reads, and its own standing with the layer (a base that neither places
        # nor composes cannot reach a composed weight through an extension that does).
        inner = Context(self.base, ctx.grid, ctx.inputs, ctx.seeds, ctx.constants, ctx.fields, layer=ctx.layer)
        shared = dict(self.base.compute(inner))
        extra = dict(self.own(ctx, MappingProxyType(shared)))
        clash = sorted(set(extra) & set(shared))
        if clash:
            raise StageError(f"stage {ctx.stage.id!r} republished {clash}, which its base {self.base.id!r} computes")
        return {**shared, **extra}


def extend(
    base: Stage,
    *,
    id: str,
    about: str,
    own: Callable[[Context, Mapping[str, Any]], Mapping[str, Any]],
    checkpoint: int | None = None,
    reads_inputs: tuple[str, ...] = (),
    reads_seeds: tuple[str, ...] = (),
    reads_constants: tuple[str, ...] = (),
    requires: tuple[str, ...] = (),
    requires_optional: tuple[str, ...] = (),
    publishes: tuple[FieldDecl, ...] = (),
    placement_reader: bool = False,
) -> Stage:
    """A second implementation of ``base``'s slot: the base's reads and fields, plus these."""

    def union(a: tuple[str, ...], b: tuple[str, ...]) -> tuple[str, ...]:
        return a + tuple(n for n in b if n not in a)

    return Stage(
        id=id,
        slot=base.slot,
        checkpoint=base.checkpoint if checkpoint is None else checkpoint,
        about=about,
        compute=Extension(base, own),
        reads_inputs=union(base.reads_inputs, reads_inputs),
        reads_seeds=union(base.reads_seeds, reads_seeds),
        reads_constants=union(base.reads_constants, reads_constants),
        requires=union(base.requires, requires),
        requires_optional=union(base.requires_optional, requires_optional),
        publishes=base.publishes + tuple(publishes),
        extends=base,
        placement_reader=placement_reader,
    )
