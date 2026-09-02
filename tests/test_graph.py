"""graph: acyclic per model, checkpoint order, hypotheses, provenance."""

from __future__ import annotations

import pytest

from galaxy.core.registry import INPUTS
from galaxy.specs import graph
from helpers import decl, impls, model, stage


def codes(problems):
    return sorted(p.code for p in problems)


def chk(m, *stages):
    return graph.check([m], impls(*stages), INPUTS)


def test_production_graphs_hold(prod):
    models, impls_, table = prod
    assert graph.check(models, impls_, table) == []
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert g.ok
        assert tuple(s.id for s in g.order) == ("halo", "disc")
        # Nothing at checkpoint 1 reads a seed, so every field is derived, not seeded (rule A10).
        assert set(g.provenance.values()) == {"derived"}
        # S1 binds the four checkpoint-1 controls and no others; graph.py checks each
        # against GALAXY_PLAN.md §3's hypothesis and none of them disagrees.
        assert {n for n, c in g.input_checkpoint.items() if c is not None} == {
            "halo_mass",
            "disc_spin",
            "halo_assembly_z",
            "baryon_retention",
        }
        assert all(c == 1 for c in g.input_checkpoint.values() if c is not None)
    assert "graph" in graph.report(models, impls_, table)


def test_cycle_detected_and_refused():
    a = stage("a", ("fa",), requires=("fb",))
    b = stage("b", ("fb",), requires=("fa",))
    m = model("m", a, b)
    assert "cycle" in codes(chk(m, a, b))
    with pytest.raises(graph.GraphError):
        graph.build(m, impls(a, b), INPUTS)


def test_order_is_topological_and_deterministic():
    a = stage("a", ("fa",))
    b = stage("b", ("fb",), requires=("fa",))
    c = stage("c", ("fc",), requires=("fb",))
    g = graph.build(model("m", c, a, b), impls(a, b, c), INPUTS)
    assert tuple(s.id for s in g.order) == ("a", "b", "c")
    x = stage("x", ("fx",), checkpoint=2)
    y = stage("y", ("fy",), checkpoint=1)
    g = graph.build(model("m", x, y), impls(x, y), INPUTS)
    assert tuple(s.id for s in g.order) == ("y", "x")
    assert g.producer == {"fx": "x", "fy": "y"}


def test_missing_producer_and_duplicate_field():
    b = stage("b", ("fb",), requires=("fa",))
    assert "missing-producer" in codes(chk(model("m", b), b))
    with pytest.raises(graph.GraphError):
        graph.build(model("m", b), impls(b), INPUTS)
    p1 = stage("p1", ("f",))
    p2 = stage("p2", ("f",))
    assert "duplicate-field" in codes(chk(model("m", p1, p2), p1, p2))


def test_unknown_implementation_and_slot_mismatch():
    from galaxy.core.registry import Model

    m = Model("m", "about", (("halo", "nope"),), {})
    assert "unknown-implementation" in codes(graph.check([m], {}, INPUTS))
    s = stage("impl", slot="chem")
    m = Model("m", "about", (("halo", "impl"),), {})
    assert "slot-mismatch" in codes(graph.check([m], impls(s), INPUTS))


def test_checkpoint_order():
    p = stage("p", ("f",), checkpoint=2)
    early = stage("c", ("g",), requires=("f",), checkpoint=1)
    assert "checkpoint-order" in codes(chk(model("m", p, early), p, early))
    same = stage("c", ("g",), requires=("f",), checkpoint=2)
    assert chk(model("m", p, same), p, same) == []
    opt = stage("c", ("g",), requires_optional=(decl("f", optional=True).name,), checkpoint=1)
    po = stage("p", (decl("f", optional=True),), checkpoint=2)
    assert "checkpoint-order" in codes(chk(model("m", po, opt), po, opt))


def test_hypothesis_checked_against_derived_checkpoint():
    late = stage("s", ("f",), reads_inputs=("halo_mass",), checkpoint=2)
    probs = chk(model("m", late), late)
    assert codes(probs) == ["hypothesis"]
    assert "checkpoint 1" in probs[0].detail and "checkpoint 2" in probs[0].detail
    ok = stage("s", ("f",), reads_inputs=("halo_mass",), checkpoint=1)
    g = graph.analyse(model("m", ok), impls(ok), INPUTS)
    assert g.ok and g.input_checkpoint["halo_mass"] == 1
    assert "halo_mass" not in g.unbound_inputs and "disc_spin" in g.unbound_inputs
    seeded = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("pattern_seed",), checkpoint=4)
    assert chk(model("m", seeded), seeded) == []
    seeded5 = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("pattern_seed",), checkpoint=5)
    assert codes(chk(model("m", seeded5), seeded5)) == ["hypothesis"]


def test_provenance_is_computed_and_compared():
    s = stage("s", ("f",), reads_seeds=("world_seed",))  # declared derived, computed seeded
    assert codes(chk(model("m", s), s)) == ["provenance"]
    s = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("world_seed",))
    assert chk(model("m", s), s) == []
    d = stage("d", ("g",), requires=("f",))  # downstream of seeded, declared derived
    assert codes(chk(model("m", s, d), s, d)) == ["provenance"]
    d = stage("d", (decl("g", provenance="seeded"),), requires=("f",))
    assert chk(model("m", s, d), s, d) == []
    s_opt = stage("s", (decl("f", provenance="seeded", optional=True),), reads_seeds=("world_seed",))
    d_opt = stage("d", ("g",), requires_optional=("f",))
    assert codes(chk(model("m", s_opt, d_opt), s_opt, d_opt)) == ["provenance"]
    claims = stage("s", (decl("f", provenance="seeded"),))  # declared seeded, reads no seed
    assert codes(chk(model("m", claims), claims)) == ["provenance"]


def test_unknown_input():
    s = stage("s", ("f",), reads_inputs=("nope",))
    assert "unknown-input" in codes(chk(model("m", s), s))
    r = stage("r", ("f",), reads_inputs=("disc_spin",))
    assert "unknown-input" in codes(chk(model("m", r, inputs=("halo_mass",)), r))
