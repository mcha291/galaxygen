"""The advanced model: a stub until S9, differing from simple by one constant."""

from galaxy.core.registry import MODELS, Constant, Model
from galaxy.models.level0 import LEVEL0

ADVANCED = MODELS.register(
    Model(
        name="advanced",
        about=(
            "Stub of the advanced model (S9: multi-element chemistry, DTD, migration, "
            "outflows). Until S9 it maps the same slots as simple and differs by CANARY "
            "only. It exists so the registry, the model switch and cross-model field "
            "reconciliation are exercised from S0 rather than discovered broken at S9 "
            "(GALAXY_PLAN.md §1, rule B1). Every test that runs all models runs this one."
        ),
        stages=(("halo", "halo"), ("disc", "disc"), ("assembly", "assembly"), ("sfh", "sfh"), ("chemistry", "chemistry"), ("vertical", "vertical"), ("bar", "bar"), ("pattern", "pattern"), ("population", "population"), ("systems", "systems"), ("formation", "formation"), ("planets", "planets")),
        constants={
            **LEVEL0,
            "CANARY": Constant(
                2.0,
                "dimensionless",
                "The one constant the two models differ by. See models/simple.py.",
            ),
        },
    )
)
