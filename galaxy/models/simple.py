"""The simple model: the first pass, built S1–S8."""

from galaxy.core.registry import MODELS, Constant, Model

SIMPLE = MODELS.register(
    Model(
        name="simple",
        about=(
            "First-pass model (GALAXY_PLAN.md §2): shared halo, potential and disc; "
            "instantaneous recycling; single-element chemistry. At S0 it maps one stub slot."
        ),
        stages=(("stub", "stub"),),
        constants={
            "CANARY": Constant(
                1.0,
                "dimensionless",
                "The one constant the two models differ by at S0. Read only by the stub "
                "stage; S1 moves it into the first real stage or replaces it with a real "
                "constant the two models legitimately differ on.",
            ),
        },
    )
)
