"""The advanced model: a stub until S9, differing from simple by one constant."""

from galaxy.core.registry import MODELS, Constant, Model

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
        stages=(("stub", "stub"),),
        constants={
            "CANARY": Constant(
                2.0,
                "dimensionless",
                "The one constant the two models differ by at S0. See models/simple.py.",
            ),
        },
    )
)
