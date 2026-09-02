"""The input table (rules A2, A5, A10), constants, models and the registries."""

from __future__ import annotations

import pytest

from galaxy.core.registry import (
    INPUT_CEILING,
    INPUTS,
    UNSET,
    Constant,
    DuplicateRegistration,
    Input,
    Model,
    Registry,
    RegistryError,
    controls,
    production,
    seeds,
)

PLAN_INPUTS = {
    # GALAXY_PLAN.md §8: the seven, plus four seeds and mergers[].
    "halo_mass",
    "disc_spin",
    "halo_assembly_z",
    "baryon_retention",
    "infall_timescale",
    "inside_out_index",
    "migration_efficiency",
    "mergers",
    "world_seed",
    "pattern_seed",
    "systems_seed",
    "planets_seed",
}


def test_input_vector_is_closed():
    assert set(INPUTS) == PLAN_INPUTS
    assert len(controls()) == 7 <= INPUT_CEILING
    assert len(seeds()) == 4
    assert [i.name for i in INPUTS.values() if i.kind == "events"] == ["mergers"]


def test_every_input_carries_a_checkpoint_hypothesis():
    for i in INPUTS.values():
        assert i.checkpoint_hypothesis is not None, i.name


def test_unset_defaults_are_owed_and_never_increase():
    unset = [i for i in INPUTS.values() if i.unset]
    for i in unset:
        assert i.default_owner and i.default_owner.startswith("S"), i.name
    # S0: halo_assembly_z (S1), inside_out_index (S2), migration_efficiency (S2), mergers (S3).
    # Sessions lower this bound as they discharge defaults; nothing may raise it.
    assert len(unset) <= 4


def test_control_ranges_never_decrease():
    missing = [i.name for i in controls() if not i.has_range]
    assert len(missing) <= 7  # S0: none set yet. Ratchet downward only.


def test_defaults_are_the_milky_way():
    assert INPUTS["halo_mass"].default == 1.1e12
    assert INPUTS["disc_spin"].default == 0.0144
    assert INPUTS["baryon_retention"].default == 0.35
    assert INPUTS["infall_timescale"].default == 7.0
    assert all(i.default == 0 for i in seeds())


def test_input_validation():
    ok = dict(label="L", about="A")
    with pytest.raises(RegistryError):
        Input("x", kind="control", default=1.0, **ok)  # no unit
    with pytest.raises(RegistryError):
        Input("x", kind="seed", unit="kpc", default=0, **ok)
    with pytest.raises(RegistryError):
        Input("x", kind="seed", **ok)  # seeds need an int default
    with pytest.raises(RegistryError):
        Input("x", kind="control", unit="kpc", **ok)  # UNSET without owner
    with pytest.raises(RegistryError):
        Input("x", kind="control", unit="kpc", default=1.0, default_owner="S1", **ok)
    with pytest.raises(RegistryError):
        Input("x", kind="control", unit="kpc", default=1.0, lo=2.0, hi=1.0, **ok)
    with pytest.raises(RegistryError):
        Input("x", kind="knob", unit="kpc", default=1.0, **ok)
    with pytest.raises(RegistryError):
        Input("x", kind="control", unit="kpc", default=1.0, checkpoint_hypothesis=9, **ok)
    with pytest.raises(RegistryError):
        Input("x", kind="control", unit="kpc", default="big", **ok)
    with pytest.raises(RegistryError):
        Input("X", kind="control", unit="kpc", default=1.0, **ok)
    i = Input("x", kind="control", unit="kpc", default_owner="S1", lo=0.0, hi=1.0, **ok)
    assert i.unset and i.has_range and i.default is UNSET


def test_constant_validation():
    with pytest.raises(RegistryError):
        Constant(1.0, "furlong", "x")
    with pytest.raises(RegistryError):
        Constant(True, "kpc", "x")  # type: ignore[arg-type]
    with pytest.raises(RegistryError):
        Constant(1.0, "kpc", "")
    assert Constant(2, "kpc", "ok").value == 2


def test_model_validation():
    c = {"K": Constant(1.0, "kpc", "k")}
    with pytest.raises(RegistryError):
        Model("m", "about", (("halo", "a"), ("halo", "b")), c)
    with pytest.raises(RegistryError):
        Model("m", "about", (("halo", "a"),), {"K": 1.0})  # type: ignore[dict-item]
    with pytest.raises(RegistryError):
        Model("m", "about", (("halo", "a"),), {"k": Constant(1.0, "kpc", "k")})  # not UPPER_SNAKE
    with pytest.raises(RegistryError):
        Model("m", " ", (("halo", "a"),), c)
    with pytest.raises(RegistryError):
        Model("Model", "about", (("halo", "a"),), c)
    m = Model("m", "about", (("halo", "a"), ("disc", "b")), c)
    assert m.stage_map == {"halo": "a", "disc": "b"}
    assert m.input_names(INPUTS) == tuple(INPUTS)
    assert Model("m", "about", (), c, inputs=("halo_mass",)).input_names(INPUTS) == ("halo_mass",)
    with pytest.raises(TypeError):
        m.constants["X"] = c["K"]  # type: ignore[index]  read-only


def test_registry_refuses_duplicates():
    r: Registry[str] = Registry("thing", lambda x: x)
    r.register("a")
    with pytest.raises(DuplicateRegistration):
        r.register("a")
    assert "a" in r and "b" not in r
    assert r.get("a") == "a" and r.names() == ("a",) and len(r) == 1
    with pytest.raises(KeyError):
        r.get("b")


def test_production_is_loaded_and_idempotent(prod):
    models, impls, table = prod
    assert set(models.names()) >= {"simple", "advanced"}
    assert "stub" in impls
    assert table is INPUTS
    again = production()
    assert again[0] is models and again[1] is impls
