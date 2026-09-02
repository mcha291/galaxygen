"""Builders for synthetic stages and models, so specs can be tested on graphs that fail."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.grids import GridSpec
from galaxy.core.registry import Constant, Model
from galaxy.core.stage import Context, Stage

TINY = GridSpec(n_R=8, n_t=5, n_z=4, n_phi=6)


def decl(name: str, kind: Kind | str = Kind.FIELD, **kw: Any) -> FieldDecl:
    base: dict[str, Any] = dict(label=name, unit="dimensionless", kind=kind, about=f"test field {name}")
    try:
        kind = Kind(kind)
    except ValueError:
        base.update(kw)
        return FieldDecl(name=name, **base)  # let FieldDecl raise DeclarationError
    if kind.domain == "grid":
        base["axes"] = ("R",)
    if kind.domain == "object":
        base["of"] = "star"
    if kind.categorical:
        base["categories"] = ("a", "b")
        if kind.domain != "galaxy":
            base["ramp"] = Palette(("#000000", "#ffffff"))
    elif kind.domain != "galaxy":
        base["ramp"] = Ramp("greys")
    base.update(kw)
    return FieldDecl(name=name, **base)


def default_value(d: FieldDecl, ctx: Context) -> Any:
    k = d.kind
    if k.domain == "grid":
        shape = ctx.grid.shape(d.axes)
        return np.zeros(shape, dtype=int) if k.categorical else np.ones(shape)
    if k.domain == "galaxy":
        return d.categories[0] if k.categorical else 1.0
    return np.zeros(3, dtype=int) if k.categorical else np.ones(3)


def stage(
    id: str,
    publishes: tuple[str | FieldDecl, ...] = (),
    compute: Callable[[Context], Mapping[str, Any]] | None = None,
    slot: str | None = None,
    checkpoint: int = 1,
    **kw: Any,
) -> Stage:
    pubs = tuple(decl(p) if isinstance(p, str) else p for p in publishes)
    if compute is None:

        def compute(ctx: Context, _pubs: tuple[FieldDecl, ...] = pubs) -> Mapping[str, Any]:
            return {d.name: default_value(d, ctx) for d in _pubs}

    return Stage(
        id=id,
        slot=slot or id,
        checkpoint=checkpoint,
        about=f"test stage {id}",
        compute=compute,
        publishes=pubs,
        **kw,
    )


def model(
    name: str,
    *stages: Stage,
    constants: Mapping[str, float] | None = None,
    inputs: tuple[str, ...] | None = None,
) -> Model:
    return Model(
        name=name,
        about=f"test model {name}",
        stages=tuple((s.slot, s.id) for s in stages),
        constants={k: Constant(v, "dimensionless", f"test constant {k}") for k, v in (constants or {}).items()},
        inputs=inputs,
    )


def impls(*stages: Stage) -> dict[str, Stage]:
    return {s.id: s for s in stages}
