"""The simple model: the first pass, built S1–S8."""

from galaxy.core.registry import MODELS, Constant, Model
from galaxy.models.level0 import LEVEL0

SIMPLE = MODELS.register(
    Model(
        name="simple",
        about=(
            "First-pass model (GALAXY_PLAN.md §2): instantaneous recycling, one abundance, no "
            "outflows, migration as a kernel on a mean, and a thick disc defined by the last "
            "major merger. Every stage it maps is shared with the advanced model except "
            "chemistry and vertical, where the two genuinely differ (S9)."
        ),
        stages=(("halo", "halo"), ("disc", "disc"), ("assembly", "assembly"), ("sfh", "sfh"), ("chemistry", "chemistry"), ("vertical", "vertical"), ("bar", "bar"), ("pattern", "pattern"), ("population", "population"), ("systems", "systems"), ("formation", "formation"), ("planets", "planets")),
        constants={
            **LEVEL0,
            # Read by the simple chemistry only. The advanced model has no effective
            # yield: it has nucleosynthetic yields and a wind, and the effective yield
            # at R₀ is one of its results (debt #16).
    "NET_YIELD": Constant(
        0.011,
        "dimensionless",
        "**Effective** yield: metals surviving in the gas per unit mass locked into stars. The "
        "nucleosynthetic yield integrated over a Kroupa/Chabrier IMF is 0.03-0.04 for total "
        "metallicity [recall], and this is deliberately about a third of it. The simple model has "
        "no outflows — GALAXY_INPUTS.md §8 makes them an advanced-model axis — so metals that "
        "should leave the disc stay in it, and at the nucleosynthetic value the solar "
        "neighbourhood comes out at [Fe/H] = +0.50 rather than 0.00. The factor of three is the "
        "metal loss the model does not have, and it is debt #16: when S9 adds outflows this "
        "constant has no claim on its value and must be re-derived (rule B10). Calibrating it "
        "costs no acceptance row, because the gradient rows are exactly insensitive to it "
        "[verified: tests/test_chemistry.py::test_the_gradient_does_not_depend_on_the_yield].",
    ),
        },
    )
)
