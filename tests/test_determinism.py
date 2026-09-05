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


# --- S10 run 2: the check runs twice in ONE process ---------------------------

_ACROSS_PROCESSES = """
import hashlib, json, sys
import numpy as np
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
models, _, _ = production()
o = run(models.get(sys.argv[1]), grid=GridSpec(n_R=64, n_t=128, n_z=8, n_phi=36))
out = {}
for name, v in sorted(o.fields.items()):
    a = np.asarray(v)
    out[name] = hashlib.blake2b(a.tobytes(), digest_size=8).hexdigest() if a.dtype != object else str(v)
print(json.dumps({"order": list(o.order), "fields": out}))
"""


def test_the_model_is_reproducible_across_processes_too(model):
    """S10 run 2, debt #35: ``check_reproducible`` compares two runs in one interpreter.

    Everything a process holds fixed — ``PYTHONHASHSEED``, set and dict iteration
    order, the allocator, module-level caches — is constant across that
    comparison, so a field that depended on any of them would pass it every time
    (rule B3: the check takes the one path immune to the defect). This runs the
    stronger form the spec does not, and the model meets it.
    """
    import json
    import os
    import subprocess
    import sys

    seen = []
    for hashseed in ("0", "1", "12345"):
        proc = subprocess.run(
            [sys.executable, "-c", _ACROSS_PROCESSES, model.name],
            capture_output=True, text=True, check=True,
            env={**os.environ, "PYTHONHASHSEED": hashseed},
        )
        seen.append(json.loads(proc.stdout.splitlines()[-1]))
    assert all(r["order"] == seen[0]["order"] for r in seen)
    differing = sorted({n for r in seen[1:] for n, v in r["fields"].items() if seen[0]["fields"].get(n) != v})
    assert differing == [], differing
    assert len(seen[0]["fields"]) >= 91
