"""The advanced model: the simple model's stages where they are right, its own where they differ.

Two slots are remapped (S9): ``chemistry`` to ``chemistry_dtd`` and ``vertical``
to ``vertical_alpha``. Everything upstream — halo, disc, assembly, the star
formation history — is shared code, so the two models agree bit-for-bit up to
the point where the physics genuinely differs, and ``tests/test_models.py``
asserts exactly that boundary.

The constants below are the advanced model's own: only its stages read them, and
preflight fails a model that declares a constant nothing reads (D29). Each is a
Level 0 constant under GALAXY_INPUTS.md §2 — yields, the SNIa delay-time
distribution, the outflow loading — and none is a property of *this* galaxy,
which is why they are not inputs however §8 tabulates them (rule A4).
"""

from galaxy.core.registry import MODELS, Constant, Model
from galaxy.models.level0 import LEVEL0

ADVANCED = MODELS.register(
    Model(
        name="advanced",
        about=(
            "Multi-element chemistry with a type Ia delay-time distribution, metal-loaded "
            "outflows set by the local escape velocity, mass-conserving radial migration, and a "
            "thin/thick split read off the [α/Fe] plane rather than off the merger list. Shares "
            "every other stage with the simple model."
        ),
        stages=(("halo", "halo"), ("disc", "disc"), ("assembly", "assembly"), ("sfh", "sfh"), ("chemistry", "chemistry_dtd"), ("vertical", "vertical_alpha"), ("bar", "bar"), ("pattern", "pattern"), ("population", "population"), ("systems", "systems"), ("formation", "formation"), ("planets", "planets")),
        constants={
            **LEVEL0,
            "SOLAR_IRON": Constant(
                1.29e-3,
                "dimensionless",
                "Solar iron mass fraction, the zero point of [Fe/H] when iron is tracked as iron "
                "[recall: Asplund et al. 2009, A(Fe) = 7.50].",
            ),
            "SOLAR_OXYGEN": Constant(
                5.73e-3,
                "dimensionless",
                "Solar oxygen mass fraction, the zero point of [O/H]; oxygen stands for the α "
                "elements here because it carries most of their mass [recall: Asplund et al. "
                "2009, A(O) = 8.69]. Also converts the oxygen yield to a total metal yield: "
                "core-collapse ejecta are taken to carry metals in solar proportion to their "
                "oxygen, which gives y_Z = 0.037 against the 0.03-0.04 usually quoted [recall].",
            ),
            "Y_O_CC": Constant(
                0.015,
                "dimensionless",
                "Oxygen returned by core-collapse supernovae per unit mass of stars formed, for a "
                "Kroupa IMF [recall: Weinberg, Andrews & Freudenburg 2017 adopt 0.015]. Prompt: "
                "returned in the timestep that formed the stars.",
            ),
            "Y_FE_CC": Constant(
                1.2e-3,
                "dimensionless",
                "Iron from core-collapse supernovae per unit mass formed [recall: WAF17 adopt "
                "0.0012]. With Y_O_CC it fixes the plateau: [O/Fe] = log10(12.5 / 4.44) = +0.45 "
                "before any Ia iron has arrived.",
            ),
            "Y_FE_IA": Constant(
                1.7e-3,
                "dimensionless",
                "Iron from type Ia supernovae per unit mass formed, integrated over the whole "
                "delay-time distribution [recall: WAF17 adopt 0.0017]. Larger than the "
                "core-collapse iron, which is why [α/Fe] ends near solar: at late times the gas "
                "has iron from both sources and oxygen from one.",
            ),
            "DTD_INDEX": Constant(
                1.1,
                "dimensionless",
                "Power-law index of the type Ia delay-time distribution, DTD ∝ τ^-1.1 [recall: "
                "Maoz & Mannucci 2012; Maoz, Mannucci & Nelemans 2014]. A steeper law puts more "
                "of the iron early and shortens the α-rich era.",
            ),
            "DTD_MIN_DELAY": Constant(
                0.15,
                "Gyr",
                "Shortest delay before a stellar generation's first type Ia supernovae "
                "[recall: WAF17 adopt 0.15 Gyr; the white-dwarf formation time alone allows "
                "0.04]. The distribution is normalised between here and the age of the universe.",
            ),
            "WIND_INDEX": Constant(
                2.0,
                "dimensionless",
                "How the wind's metal loading falls with escape velocity: 2 is an energy-driven "
                "wind, 1 a momentum-driven one [recall: Murray, Quataert & Thompson 2005]. "
                "Chosen, not fitted, and the tilt it gives the gradient is a prediction.",
            ),
            "WIND_SPEED": Constant(
                993.0,
                "km/s",
                "The escape velocity at which half of a generation's fresh metals leave the disc. "
                "**The one fitted constant of the advanced chemistry**: set so the present-day "
                "gas at R₀ is solar, the same calibration NET_YIELD carried for the simple model "
                "(debt #16, rule B10). Fitted at S9 to 1010 against a potential built on an "
                "unconverted concentration; refitted at S13 to 987 once the halo converts c_vir to "
                "c₂₀₀ (debt #12) and Sagittarius delivers a physical share (debt #29); refitted at "
                "S14 to 1028 once the halo contracts around the disc (debt #6) and the escape velocity "
                "at R₀ rises 562 → 585 km/s; refitted at S15 to 999 once the epoch's default is the "
                "ΛCDM median (z_f 2.5 → 1.66, debt #12) and v_esc(R₀) falls 585 → 569, inside the "
                "observed 530–580; refitted at S16 to 993 once the high-j tail exists (debt #18) and "
                "the gas at R₀ read −0.004 dex — each time the mechanism fixed, the constant "
                "re-examined (rule B10, debt #43). Row 3 still overshoots by 2 km/s at this potential, "
                "so the value is fitted against a known miss and will move again when the bulge "
                "arrives. Everything the value implies elsewhere — the loss fraction at every other "
                "radius, the gradient tilt — is then a prediction.",
            ),
            "IA_METAL_TO_IRON": Constant(
                2.0,
                "dimensionless",
                "Total metal mass a type Ia ejects per unit iron mass: the ejecta are iron-peak "
                "throughout, about twice the iron by mass [recall]. Until S12 this was a bare 2.0 in "
                "chemistry_dtd (debt #33); it sets the advanced model's total-Z zero point, which reads "
                "1.24 Z☉ where [Fe/H] = 0 and is still debt #33's question. No stage reads Z yet.",
            ),
        },
    )
)
