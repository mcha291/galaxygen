"""The simple model: the first pass, built S1–S8."""

from galaxy.core.registry import MODELS, Constant, Model
from galaxy.models.level0 import LEVEL0

SIMPLE = MODELS.register(
    Model(
        name="simple",
        about=(
            "First-pass model (GALAXY_PLAN.md §2): shared halo, potential and disc; "
            "instantaneous recycling; single-element chemistry. At S1 it maps halo and disc."
        ),
        stages=(("halo", "halo"), ("disc", "disc"), ("sfh", "sfh")),
        constants={
            **LEVEL0,
            "CANARY": Constant(
                1.0,
                "dimensionless",
                "The one constant the two models differ by while the advanced model is still a "
                "stub. Read by the halo stage and published as the canary field, which is not "
                "physics; S9 deletes both when the advanced model gets a stage map of its own.",
            ),
        },
    )
)
