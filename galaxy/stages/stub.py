"""The stub stage: the only stage at S0. It computes no physics.

It exists because the gates must be falsifiable. A model with no stages passes
"acyclic", "preflight" and "reproducible" vacuously; one stage that reads one
constant and publishes one field gives every spec something real to check, and
lets the two registered models produce distinguishable output.

S1 deletes this module, moves CANARY into the first real stage, and updates
both model declarations. Nothing else refers to it by name except the tests
that guard the canary.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage

CANARY = FieldDecl(
    name="canary",
    label="Canary",
    unit="dimensionless",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("greys"),
    meaningful_zero=False,
    provenance="derived",
    about=(
        "Equals the model constant CANARY at every radius. Exists so that two registered "
        "models produce distinguishable output before any physics does; tests/test_models.py "
        "asserts they differ. Delete at S1 and move CANARY into the first real stage."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    return {"canary": np.full(ctx.grid.shape(("R",)), float(ctx.constants["CANARY"]))}


STUB = IMPLEMENTATIONS.register(
    Stage(
        id="stub",
        slot="stub",
        checkpoint=1,
        about=(
            "Placeholder occupying checkpoint 1 until S1 ships halo & disc. Reads one "
            "constant, publishes one field, reads no inputs and no seeds."
        ),
        compute=compute,
        reads_constants=("CANARY",),
        publishes=(CANARY,),
    )
)
