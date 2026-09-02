"""The canary guards: the second model must stay a real, distinguishable second model.

GALAXY_PLAN.md §1: the stub differs by one constant so the registry, the model
switch and cross-model reconciliation are exercised from S0. These tests are
what makes that exercise falsifiable. S9 rewrites ``test_models_differ_by_exactly_one_constant``
when the advanced model gets its own stage map; nothing before S9 should touch it.
"""

from __future__ import annotations

import numpy as np

from galaxy.run import run
from helpers import TINY


def test_two_models_registered(prod):
    models = list(prod[0])
    assert [m.name for m in models] == ["simple", "advanced"]


def test_models_differ_by_exactly_one_constant(prod):
    simple, advanced = prod[0].get("simple"), prod[0].get("advanced")
    assert simple.stage_map == advanced.stage_map
    assert set(simple.constants) == set(advanced.constants)
    differing = [k for k in simple.constants if simple.constants[k].value != advanced.constants[k].value]
    assert differing == ["CANARY"]
    assert simple.constants["CANARY"].unit == advanced.constants["CANARY"].unit


def test_model_switch_is_observable(prod):
    outs = {m.name: run(m, grid=TINY) for m in prod[0]}
    assert set(outs["simple"].fields) == set(outs["advanced"].fields)
    assert not np.array_equal(outs["simple"].fields["canary"], outs["advanced"].fields["canary"])


def test_canary_equals_its_own_constant(model):
    # A stage that hardcoded the constant instead of reading ctx.constants fails here for one model.
    out = run(model, grid=TINY)
    assert np.all(out.fields["canary"] == model.constants["CANARY"].value)
    assert out.decls["canary"].unit == "dimensionless"
