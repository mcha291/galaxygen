"""determinism: per model and per region, and the golden pins."""

from __future__ import annotations

import numpy as np

from galaxy.core.registry import INPUTS
from galaxy.specs import determinism
from helpers import TINY, decl, impls, model, stage


def test_production_models_are_reproducible(model, prod):
    assert determinism.check_reproducible(model, prod[1], prod[2]) == []


def test_region_and_golden_hold():
    assert determinism.check_region() == []
    assert determinism.check_golden() == []


def test_full_check_and_report(prod):
    assert determinism.check(*prod) == []
    rep = determinism.report(*prod)
    assert "OK" in rep and "FAIL" not in rep


def test_unseeded_global_rng_is_caught():
    s = stage("s", ("f",), compute=lambda ctx: {"f": np.random.random(ctx.grid.shape(("R",)))})
    probs = determinism.check_reproducible(model("m", s), impls(s), INPUTS, TINY)
    assert [p.code for p in probs] == ["irreproducible"]


def test_seeded_stage_passes_and_nan_is_equal_to_nan():
    s = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("world_seed",), compute=lambda ctx: {"f": ctx.rng("world_seed").random(ctx.grid.shape(("R",)))})
    assert determinism.check_reproducible(model("m", s), impls(s), INPUTS, TINY) == []
    n = stage("n", ("f",), compute=lambda ctx: {"f": np.full(ctx.grid.shape(("R",)), np.nan)})
    assert determinism.check_reproducible(model("m", n), impls(n), INPUTS, TINY) == []
