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
    # S1 set halo_assembly_z; S2 set inside_out_index and migration_efficiency; S3 set
    # mergers. S10's audit lowered the bound to what it had been for six sessions: zero.
    assert len(unset) == 0


def test_control_ranges_never_decrease():
    missing = [i.name for i in controls() if not i.has_range]
    # S0: none set. S1 set the four checkpoint-1 controls, S2 the three
    # checkpoint-3 ones. Every control now has a range. Ratchet downward only.
    assert len(missing) == 0


def test_defaults_are_the_milky_way():
    assert INPUTS["halo_mass"].default == 1.1e12
    # Ruling 8 says 0.0144, inferred against R_vir = 255 kpc. S1 re-derived it against this
    # model's own R₂₀₀ = 212.9 kpc, which is what MMW98's relation takes (DECISIONS.md D30).
    assert INPUTS["disc_spin"].default == 0.0173
    assert INPUTS["halo_assembly_z"].default == 1.66  # 2.5 until S15: the ΛCDM median for the default mass (D117)
    assert INPUTS["baryon_retention"].default == 0.35
    assert INPUTS["infall_timescale"].default == 7.0
    assert INPUTS["inside_out_index"].default == 1.0
    assert INPUTS["migration_efficiency"].default == 3.6
    # S2: a radial dispersion has a length; dimensionless was provisional (D45).
    assert INPUTS["migration_efficiency"].unit == "kpc"
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
    assert {"halo", "disc", "sfh", "chemistry"} <= set(impls.names())
    assert table is INPUTS
    again = production()
    assert again[0] is models and again[1] is impls


def test_the_epochs_default_is_the_lcdm_median():
    """S15 (D117): z_f's default is derived, not the midpoint of a cited range.

    The c_vir normalisation K is a dark-matter-only calibration, so the concentration it
    gives is the halo's before it contracted around the disc (S14); the Milky Way's measured
    10-18 are fits to the halo after, so they could not set the default. What can is the
    LCDM concentration-mass relation at z = 0 for the default mass [verified: Dutton & Maccio
    2014, log10 c200 = 0.905 - 0.101 log10(M200 / 10^12 h^-1 Msun), Planck, 0.11 dex scatter],
    converted to c_vir at Delta_vir and read back through K: the epoch of the median halo of
    this mass. The scatter spans 1.08-2.41 and the old 2.5 lies outside it.
    """
    import math

    from galaxy.models.level0 import LEVEL0
    from galaxy.stages.halo import concentration_at, virial_overdensity

    h, K = LEVEL0["H0"].value / 0.1, LEVEL0["CONCENTRATION_NORM"].value
    dvir = virial_overdensity(LEVEL0["OMEGA_M"].value)

    def epoch(dex: float) -> float:
        c200 = 10.0 ** (0.905 - 0.101 * math.log10(INPUTS["halo_mass"].default * h / 1e12) + dex)
        return concentration_at(dvir, c200, 200.0) / K - 1.0

    assert epoch(0.0) == pytest.approx(INPUTS["halo_assembly_z"].default, abs=0.005)
    assert epoch(-0.11) == pytest.approx(1.08, abs=0.01) and epoch(+0.11) == pytest.approx(2.41, abs=0.01)
    assert not epoch(-0.11) <= 2.5 <= epoch(+0.11)
    assert INPUTS["halo_assembly_z"].lo <= epoch(-0.11) and epoch(+0.11) <= INPUTS["halo_assembly_z"].hi
