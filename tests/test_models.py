"""The two models: where they share code, where they differ, and that the difference is real.

S0 kept the advanced model a stub differing by one constant so the registry and
the model switch were exercised from the start. S9 ended that: the advanced model
maps two slots to implementations of its own, and these tests assert the boundary
rather than a canary — everything upstream of chemistry is bit-identical, and
what differs downstream is physics the simple model cannot produce.
"""

from __future__ import annotations

import numpy as np

from galaxy.models.level0 import LEVEL0
from galaxy.run import run
from galaxy.specs import graph, spec
from helpers import TINY

ADVANCED_SLOTS = {"chemistry": "chemistry_dtd", "vertical": "vertical_alpha"}


def test_two_models_registered(prod):
    models = list(prod[0])
    assert [m.name for m in models] == ["simple", "advanced"]


def test_the_advanced_model_remaps_exactly_two_slots(prod):
    simple, advanced = prod[0].get("simple"), prod[0].get("advanced")
    assert set(simple.stage_map) == set(advanced.stage_map)
    differing = {s for s in simple.stage_map if simple.stage_map[s] != advanced.stage_map[s]}
    assert differing == set(ADVANCED_SLOTS)
    assert {s: advanced.stage_map[s] for s in differing} == ADVANCED_SLOTS


def test_shared_constants_are_shared_and_own_ones_are_read(prod):
    """No canary: every constant a model has is Level 0 or read by one of its own stages."""
    simple, advanced = prod[0].get("simple"), prod[0].get("advanced")
    for name, c in LEVEL0.items():
        assert simple.constants[name] is c and advanced.constants[name] is c
    assert set(simple.constants) - set(LEVEL0) == {"NET_YIELD"}
    own = set(advanced.constants) - set(LEVEL0)
    assert "NET_YIELD" not in own and "CANARY" not in own | set(simple.constants)
    read = {c for st in graph.analyse(advanced, prod[1], prod[2]).stages.values() for c in st.reads_constants}
    assert own <= read


def test_the_models_agree_upstream_of_chemistry_and_differ_below(prod):
    """The boundary, asserted: bit-identical shared stages, a real difference after them."""
    simple, advanced = prod[0].get("simple"), prod[0].get("advanced")
    a, b = run(simple, grid=TINY), run(advanced, grid=TINY)
    g = graph.analyse(simple, prod[1], prod[2])
    below = {"chemistry", "vertical"}
    grew = True
    while grew:  # everything that reads, transitively, from the remapped slots
        grew = False
        for st in g.stages.values():
            if st.id not in below and any(g.producer.get(n) in below for n in st.requires + st.requires_optional):
                below.add(st.id)
                grew = True
    downstream = {n for n, sid in g.producer.items() if sid in below}
    for name in set(a.fields) - downstream:
        assert np.array_equal(np.asarray(a.fields[name]), np.asarray(b.fields[name]), equal_nan=True), name
    assert "feh_history" in downstream and "halo_potential" not in downstream
    assert not np.array_equal(a.fields["feh_history"], b.fields["feh_history"], equal_nan=True)


def test_the_advanced_model_publishes_what_the_simple_one_cannot(prod, judged):
    simple, advanced = prod[0].get("simple"), prod[0].get("advanced")
    a, b = run(simple, grid=TINY, only=("alpha_sequence", "feh_gas")), run(advanced, grid=TINY, only=("alpha_sequence", "feh_gas"))
    assert "alpha_fe_history" not in a.fields and "alpha_fe_history" in b.fields
    assert b.decls["alpha_fe_history"].optional and b.decls["feh_history"].contract() == a.decls["feh_history"].contract()
    # Row 24 is a verdict in one model and an admission in the other (rule B3).
    row24 = {name: next(r for r in results if r.n == 24) for name, results in judged.items()}
    assert row24["simple"].status == "not-yet-computable"
    assert row24["advanced"].status in ("pass", "fail")
    assert row24["advanced"].value in b.decls["alpha_sequence"].categories
