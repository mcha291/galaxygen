"""The runner: order, restricted access, publish validation, input resolution."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.fielddoc import Kind
from galaxy.core.registry import INPUTS, Input
from galaxy.core.stage import OptionalFieldAccess, UndeclaredAccess
from galaxy.run import MissingInput, PublishError, RunError, run
from galaxy.specs.graph import GraphError
from helpers import TINY, decl, impls, model, stage


def go(m, *stages, inputs=None, grid=TINY, only=None):
    return run(m, inputs, grid, impls=impls(*stages), table=INPUTS, only=only)


def test_production_runs(model):
    out = run(model, grid=TINY)
    assert out.fields["canary"].shape == (8,)
    assert out.order == (
        "halo", "assembly", "disc", "sfh", "chemistry", "vertical",
        "bar", "population", "pattern", "systems", "formation", "planets",
    )
    assert {"halo_mass", "world_seed"} <= set(out.inputs)
    assert set(out.inputs) == set(INPUTS)  # S3 set the last default, so every input resolves


def chain():
    a = stage("a", ("fa",), reads_inputs=("halo_mass",), compute=lambda ctx: {"fa": np.full(ctx.grid.shape(("R",)), ctx.inputs["halo_mass"] / 1e12)})
    b = stage("b", ("fb",), requires=("fa",), compute=lambda ctx: {"fb": ctx.fields["fa"] * 2})
    c = stage("c", ("fc",), requires=("fb",), reads_constants=("K",), compute=lambda ctx: {"fc": ctx.fields["fb"] + ctx.constants["K"]})
    return a, b, c


def test_synthetic_chain_and_override():
    a, b, c = chain()
    m = model("m", c, a, b, constants={"K": 1.0})
    out = go(m, a, b, c)
    assert out.order == ("a", "b", "c")
    assert np.allclose(out.fields["fc"], 1.1 * 2 + 1)
    out2 = go(m, a, b, c, inputs={"halo_mass": 2e12})
    assert np.allclose(out2.fields["fc"], 5.0)


def test_undeclared_access_raises():
    s = stage("s", ("f",), compute=lambda ctx: {"f": np.ones(8) * ctx.inputs["halo_mass"]})
    with pytest.raises(UndeclaredAccess):
        go(model("m", s), s)
    s = stage("s", ("f",), compute=lambda ctx: {"f": np.ones(8) * ctx.constants["K"]})
    with pytest.raises(UndeclaredAccess):
        go(model("m", s, constants={"K": 1.0}), s)
    p = stage("p", ("fa",))
    s = stage("s", ("f",), compute=lambda ctx: {"f": ctx.fields["fa"]})
    with pytest.raises(UndeclaredAccess):
        go(model("m", p, s), p, s)


def test_publish_must_match_declaration():
    s = stage("s", ("f",), compute=lambda ctx: {"f": np.ones(8), "extra": 1})
    with pytest.raises(PublishError, match="undeclared"):
        go(model("m", s), s)
    s = stage("s", ("f",), compute=lambda ctx: {})
    with pytest.raises(PublishError, match="did not publish"):
        go(model("m", s), s)
    s = stage("s", ("f",), compute=lambda ctx: [1, 2])
    with pytest.raises(PublishError, match="mapping"):
        go(model("m", s), s)


def test_shape_is_checked_including_axis_order():
    d = decl("f", axes=("R", "t"))
    s = stage("s", (d,), compute=lambda ctx: {"f": np.ones((5, 8))})  # (t, R): transposed
    with pytest.raises(PublishError, match="shape"):
        go(model("m", s), s)
    s = stage("s", (d,), compute=lambda ctx: {"f": np.ones((8, 5))})
    assert go(model("m", s), s).fields["f"].shape == (8, 5)
    s = stage("s", ("f",), compute=lambda ctx: {"f": np.ones(8, dtype=int)})
    with pytest.raises(PublishError, match="floating"):
        go(model("m", s), s)


def test_scalar_is_checked():
    d = decl("f", Kind.SCALAR)
    for bad in (np.ones(3), True, "x"):
        s = stage("s", (d,), compute=lambda ctx, b=bad: {"f": b})
        with pytest.raises(PublishError):
            go(model("m", s), s)
    s = stage("s", (d,), compute=lambda ctx: {"f": 3})
    out = go(model("m", s), s)
    assert out.fields["f"] == 3.0 and isinstance(out.fields["f"], float)


def test_category_codes_are_checked():
    d = decl("f", Kind.CATEGORY_FIELD)
    s = stage("s", (d,), compute=lambda ctx: {"f": np.zeros(8)})  # floats
    with pytest.raises(PublishError, match="integer"):
        go(model("m", s), s)
    s = stage("s", (d,), compute=lambda ctx: {"f": np.full(8, 5)})
    with pytest.raises(PublishError, match="codes"):
        go(model("m", s), s)
    s = stage("s", (d,), compute=lambda ctx: {"f": np.array([0, 1] * 4)})
    assert go(model("m", s), s).fields["f"].max() == 1
    ds = decl("g", Kind.CATEGORY_SCALAR)
    s = stage("s", (ds,), compute=lambda ctx: {"g": "z"})
    with pytest.raises(PublishError):
        go(model("m", s), s)
    s = stage("s", (ds,), compute=lambda ctx: {"g": "b"})
    assert go(model("m", s), s).fields["g"] == "b"


def test_columns_share_a_length_per_object_class():
    d1, d2 = decl("m1", Kind.COLUMN), decl("m2", Kind.COLUMN)
    s = stage("s", (d1, d2), compute=lambda ctx: {"m1": np.ones(3), "m2": np.ones(4)})
    with pytest.raises(PublishError, match="length"):
        go(model("m", s), s)
    s = stage("s", (d1,), compute=lambda ctx: {"m1": np.ones((3, 2))})
    with pytest.raises(PublishError, match="1-D"):
        go(model("m", s), s)
    d3 = decl("m3", Kind.COLUMN, of="planet")
    s = stage("s", (d1, d3), compute=lambda ctx: {"m1": np.ones(3), "m3": np.ones(9)})
    assert go(model("m", s), s).fields["m3"].shape == (9,)
    dc = decl("c1", Kind.CATEGORY_COLUMN)
    s = stage("s", (dc,), compute=lambda ctx: {"c1": np.array([0, 1, 7])})
    with pytest.raises(PublishError, match="codes"):
        go(model("m", s), s)


def test_unset_input_is_an_error_only_when_read():
    """Rule B9: refuse to invent a number, but only when a stage actually wants one.

    Every production input has a default since S3, so this is exercised against a
    synthetic table — the behaviour still has to hold for the next input added.
    """
    owed = Input("owed", "Owed", "control", "no default yet", unit="kpc", default_owner="S9")
    table = {**INPUTS, "owed": owed}
    s = stage("s", ("f",), reads_inputs=("owed",), compute=lambda ctx: {"f": np.full(8, ctx.inputs["owed"])})
    m = model("m", s)
    with pytest.raises(MissingInput, match="S9"):
        run(m, None, TINY, impls=impls(s), table=table)
    got = run(m, {"owed": 2.5}, TINY, impls=impls(s), table=table)
    assert np.all(got.fields["f"] == 2.5)
    t = stage("t", ("f",))
    assert run(model("m", t), None, TINY, impls=impls(t), table=table).fields["f"].shape == (8,)


def test_unknown_override_and_input_subset():
    s = stage("s", ("f",))
    with pytest.raises(RunError):
        go(model("m", s), s, inputs={"nope": 1})
    r = stage("r", ("f",), reads_inputs=("disc_spin",), compute=lambda ctx: {"f": np.full(8, ctx.inputs["disc_spin"])})
    with pytest.raises(GraphError):
        go(model("m", r, inputs=("halo_mass",)), r)


def test_optional_field_absence_is_handled_or_impossible():
    producer = stage("p", (decl("opt", optional=True),))
    reader = stage("r", ("g",), requires_optional=("opt",), compute=lambda ctx: {"g": np.full(8, 2.0 if ctx.fields.has("opt") else 1.0)})
    with_it = go(model("with_it", producer, reader), producer, reader)
    without = go(model("without", reader), reader)
    assert np.all(with_it.fields["g"] == 2.0) and np.all(without.fields["g"] == 1.0)
    careless = stage("c", ("g",), requires_optional=("opt",), compute=lambda ctx: {"g": ctx.fields["opt"] * 2})
    with pytest.raises(OptionalFieldAccess):
        go(model("m", producer, careless), producer, careless)


def test_seeded_stage_reproducible_and_seed_sensitive():
    s = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("world_seed",), compute=lambda ctx: {"f": ctx.rng("world_seed").random(8)})
    m = model("m", s)
    a, b = go(m, s), go(m, s)
    assert np.array_equal(a.fields["f"], b.fields["f"])
    c = go(m, s, inputs={"world_seed": 1})
    assert not np.array_equal(a.fields["f"], c.fields["f"])


def test_cycle_is_refused_before_running():
    a = stage("a", ("fa",), requires=("fb",))
    b = stage("b", ("fb",), requires=("fa",))
    with pytest.raises(GraphError, match="cycle"):
        go(model("m", a, b), a, b)


# --- partial runs: rule D4's arithmetic ---------------------------------------


def same(a, b) -> bool:
    """Bit-identical, with NaN equal to NaN — TINY's coarse axes make some scalars NaN."""
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    return bool(np.array_equal(a, b, equal_nan=bool(np.issubdtype(a.dtype, np.floating))))


def test_only_runs_the_closure_and_nothing_else():
    a, b, c = chain()
    m = model("m", c, a, b, constants={"K": 1.0})
    assert go(m, a, b, c, only=("fb",)).ran == ("a", "b")
    assert go(m, a, b, c, only=("fa",)).ran == ("a",)
    assert go(m, a, b, c, only=("fa", "fc")).ran == ("a", "b", "c")
    # A field this model does not publish contributes nothing; it is not an error.
    empty = go(m, a, b, c, only=("nothing_publishes_this",))
    assert empty.ran == () and empty.fields == {}


def test_a_partial_run_agrees_with_the_full_run(model):
    """Running fewer stages must not move the ones that run (rule B3: assert it)."""
    wanted = ("bar_pattern_speed", "bar_corotation_radius")
    full = run(model, grid=TINY)
    part = run(model, grid=TINY, only=wanted)
    assert set(part.ran) < set(full.ran), "the closure above the bar is not the whole pipeline"
    assert "systems" not in part.ran and "population" not in part.ran
    for name, value in part.fields.items():
        assert same(value, full.fields[name]), name
    assert set(wanted) <= set(part.fields)


def test_resume_runs_only_what_is_missing_and_gets_the_same_galaxy(model):
    full = run(model, grid=TINY)
    first = run(model, grid=TINY, only=("bar_pattern_speed",))
    second = run(model, grid=TINY, only=("star_radius",), resume=first)
    assert not set(second.ran) & set(first.ran), "resume re-ran a stage that was already done"
    assert set(second.order) == set(first.ran) | set(second.ran)
    for name, value in second.fields.items():
        assert same(value, full.fields[name]), name


def test_resume_refuses_a_galaxy_it_did_not_compute(model):
    first = run(model, grid=TINY, only=("bar_pattern_speed",))
    with pytest.raises(RunError, match="input"):
        run(model, {"halo_mass": 2e12}, TINY, only=("star_radius",), resume=first)
    with pytest.raises(RunError, match="grid"):
        run(model, None, TINY.replace(n_R=9), only=("star_radius",), resume=first)
    other = model.__class__(
        name="other", about=model.about, stages=model.stages, constants=dict(model.constants)
    )
    with pytest.raises(RunError, match="model"):
        run(other, None, TINY, only=("star_radius",), resume=first)


def test_a_pruned_stage_does_not_owe_its_inputs():
    """An UNSET input is only an error on a path that actually runs (rule B9)."""
    owed = Input("owed", "Owed", "control", "no default", unit="dimensionless", default_owner="S6")
    table = {**INPUTS, "owed": owed}
    needs = stage("needs", ("f",), reads_inputs=("owed",), compute=lambda ctx: {"f": np.full(8, ctx.inputs["owed"])})
    other = stage("other", ("g",))
    m = model("m", needs, other)
    with pytest.raises(MissingInput):
        run(m, None, TINY, impls=impls(needs, other), table=table)
    out = run(m, None, TINY, impls=impls(needs, other), table=table, only=("g",))
    assert out.ran == ("other",) and "owed" not in out.inputs
