"""Stage declarations and the restricted context (rule B13 applied to A8)."""

from __future__ import annotations

import pytest

from galaxy.core.stage import (
    CHECKPOINTS,
    Context,
    OptionalFieldAccess,
    Restricted,
    Stage,
    StageError,
    UndeclaredAccess,
)
from helpers import TINY, decl, stage


def test_stage_validation():
    with pytest.raises(StageError):
        stage("Stub")
    with pytest.raises(StageError):
        stage("s", checkpoint=0)
    with pytest.raises(StageError):
        stage("s", checkpoint=7)
    with pytest.raises(StageError):
        stage("s", checkpoint=True)  # type: ignore[arg-type]
    with pytest.raises(StageError):
        Stage(id="s", slot="s", checkpoint=1, about=" ", compute=lambda ctx: {})
    with pytest.raises(StageError):
        Stage(id="s", slot="s", checkpoint=1, about="a", compute=None)  # type: ignore[arg-type]
    with pytest.raises(StageError):
        stage("s", publishes=(decl("f"), decl("f")))
    with pytest.raises(StageError):
        stage("s", requires=("a",), requires_optional=("a",))
    with pytest.raises(StageError):
        stage("s", publishes=("f",), requires=("f",))
    with pytest.raises(StageError):
        stage("s", reads_constants=("canary",))  # constants are UPPER_SNAKE
    with pytest.raises(StageError):
        stage("s", reads_inputs=("HALO_MASS",))
    with pytest.raises(StageError):
        stage("s", requires=("a", "a"))
    with pytest.raises(StageError):
        stage("s", publishes=("f", "not a decl object"[0:0] or 3))  # type: ignore[arg-type]
    ok = stage("s", publishes=("f",), reads_constants=("K_ONE",), checkpoint=6)
    assert ok.published_names == ("f",)
    assert ok.checkpoint_name == "Planets"


def test_checkpoints_are_the_plan_hypothesis():
    assert len(CHECKPOINTS) == 6
    assert CHECKPOINTS[0] == "Halo & disc" and CHECKPOINTS[3] == "Pattern"


def test_restricted_view():
    r = Restricted({"a": 1, "b": 2, "o": 3}, ["a"], "field", "s", optional=["o", "p"])
    assert r["a"] == 1
    with pytest.raises(UndeclaredAccess):
        r["b"]
    with pytest.raises(UndeclaredAccess):
        r.get("b")
    with pytest.raises(UndeclaredAccess):
        r.has("b")
    with pytest.raises(OptionalFieldAccess):
        r["o"]
    assert r.get("o") == 3 and r.has("o")
    assert r.get("p") is None and not r.has("p")
    assert r.get("p", 7) == 7
    assert "a" in r and "o" in r and "b" not in r and "p" not in r and 3 not in r
    assert sorted(r) == ["a", "o"] and len(r) == 2


def test_context_exposes_only_declared_names():
    s = stage("s", reads_inputs=("halo_mass",), reads_seeds=("world_seed",), reads_constants=("K",), requires=("f",))
    ctx = Context(s, TINY.build(), {"halo_mass": 1.0, "disc_spin": 2.0}, {"world_seed": 0, "pattern_seed": 1}, {"K": 3.0, "J": 4.0}, {"f": 5, "g": 6})
    assert ctx.inputs["halo_mass"] == 1.0 and ctx.seeds["world_seed"] == 0
    assert ctx.constants["K"] == 3.0 and ctx.fields["f"] == 5
    for view, key in [(ctx.inputs, "disc_spin"), (ctx.seeds, "pattern_seed"), (ctx.constants, "J"), (ctx.fields, "g")]:
        with pytest.raises(UndeclaredAccess):
            view[key]
    assert ctx.grid.shape(("R",)) == (8,)


def test_context_rng_is_keyed_by_slot():
    s1 = stage("impl_a", slot="chem", reads_seeds=("world_seed",))
    s2 = stage("impl_b", slot="chem", reads_seeds=("world_seed",))
    s3 = stage("impl_c", slot="halo", reads_seeds=("world_seed",))
    g = TINY.build()
    ctxs = [Context(s, g, {}, {"world_seed": 9}, {}, {}) for s in (s1, s2, s3)]
    d = [c.rng("world_seed").random() for c in ctxs]
    assert d[0] == d[1]  # same slot, same seed: same stream, whichever implementation
    assert d[0] != d[2]  # different slot: independent stream
    assert ctxs[0].rng("world_seed", "sub", 1).random() != d[0]
    with pytest.raises(UndeclaredAccess):
        ctxs[0].rng("pattern_seed")
