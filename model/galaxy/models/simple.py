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
        stages=(
            ("halo", "halo"),
            ("disc", "disc"),
            ("nucleus", "nucleus"),
            ("assembly", "assembly"),
            ("sfh", "sfh"),
            ("chemistry", "chemistry"),
            ("vertical", "vertical"),
            ("bar", "bar"),
            ("pattern", "pattern"),
            ("population", "population"),
            ("systems", "systems"),
            ("formation", "formation"),
            ("planets", "planets"),
        ),
        constants={
            **LEVEL0,
            # Read by the simple chemistry only. The advanced model has no effective
            # yield: it has nucleosynthetic yields and a wind, and the effective yield
            # at R₀ is one of its results (debt #16).
    "NET_YIELD": Constant(
        0.01376,
        "dimensionless",
        "**Effective** yield: metals surviving in the gas per unit mass locked into stars. Refitted "
        "at S18 from 0.01184 (+16%), the largest move it has made: the star formation threshold is "
        "Kennicutt's derived one and holds 10.8 M☉/pc² of gas at R₀ where the constant held 6.3, so "
        "the same metals sit in more gas and the gas at R₀ read −0.065 dex (debt #43, D124). Refitted "
        "at S16 from 0.011, the first time since S3: the high-j tail took 7.6% of the budget out of "
        "the exponential and the gas at R₀ read −0.027 dex, so the value was re-set to solar by "
        "bisection (rule B10, debt #43, D119); refitted again at S17 from 0.0117 when the spheroid "
        "took another 13% out, though that moved the gas at R₀ only −0.005 dex and the constant "
        "1.2% — re-examined every time the budget moves, whether or not the move is material. The "
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
