"""Level 0: physical constants, shared by every model.

GALAXY_INPUTS.md §2 — these are constants that happen to be uncertain, recorded
as calibration debt and never exposed as controls. Rule A4 disqualifies each:
they would exist whether or not this model did, and none is a property of *this*
galaxy.

They live in one module rather than in each model declaration because two copies
of a constant is exactly the duplicate rule A9 forbids: the one that loses is
dead, and the one that wins is a bug wearing the right name. A model takes this
mapping and adds only what it genuinely differs on.

Only constants some stage actually reads may appear here: preflight fails a
model that declares a constant no stage reads, so the cosmological parameters
that nothing has needed yet (Ω_M, Ω_Λ) are absent rather than declared dead.
"""

from __future__ import annotations

from galaxy.core.registry import Constant

LEVEL0: dict[str, Constant] = {
    "G": Constant(
        4.300917270e-6,
        "kpc.km2/s2/Msun",
        "Newton's constant in the model's own units, so G·M/R is a squared velocity with no "
        "conversion factor anywhere. It is the IAU nominal solar mass parameter GM☉ = "
        "1.32712440018 × 10²⁰ m³/s² divided by (1 kpc = 3.0856775814913673 × 10¹⁹ m) and by "
        "(1 km/s)²; GM☉ is used rather than G and M☉ separately because the product is known to "
        "ten digits and the factors to four [verified: tests/test_special.py::test_G_is_the_IAU_"
        "nominal_solar_mass_parameter reproduces this arithmetic].",
    ),
    "H0": Constant(
        0.07,
        "km/s/kpc",
        "Hubble constant, 70 km/s/Mpc, i.e. h = 0.7 [verified: GALAXY_INPUTS.md §2, citing BHG16 "
        "§1]. Read only to form ρ_crit = 3H₀²/8πG, which fixes R₂₀₀. The local-distance-ladder and "
        "CMB values differ by about 8%; that propagates to R₂₀₀ as 8% and to R_d through λ_d, and "
        "is not modelled.",
    ),
    "F_BARYON": Constant(
        0.152177,
        "dimensionless",
        "Cosmic baryon fraction Ω_b/Ω_M = (0.02237/0.7²)/0.3, combining Planck's Ω_b h² [recall: "
        "Planck 2018] with the h = 0.7 and Ω_M = 0.3 this project's Level 0 takes from BHG16 "
        "[verified: GALAXY_INPUTS.md §2]. Planck's own parameters give 0.1565, 3% higher; the "
        "mixture is inherited from Level 0 rather than chosen here, and the 3% goes straight into "
        "the baryon budget.",
    ),
    "CONCENTRATION_NORM": Constant(
        4.1,
        "dimensionless",
        "Normalisation of c₂₀₀ = K(1 + z_f), the concentration a halo freezes in at its assembly "
        "epoch (ruling 5). K = 4.1 is quoted for c_vir [recall: Wechsler et al. 2002]; c_vir and "
        "c₂₀₀ are defined at different overdensities and the conversion between them is folded "
        "into K rather than modelled, which is debt #12. The default z_f = 2.5 gives c₂₀₀ = 14.4, "
        "inside the 10–18 the Milky Way's own measurements span [verified: GALAXY_INPUTS.md §4b].",
    ),
    "R_SUN": Constant(
        8.2,
        "kpc",
        "Galactocentric radius of the Sun, R₀ = 8.2 ± 0.1 kpc [verified: GALAXY_INPUTS.md §7 row "
        "3's source BHG16]. Where every 'solar neighbourhood' quantity is evaluated.",
    ),
    "RETURN_FRACTION": Constant(
        0.30,
        "dimensionless",
        "Fraction of the mass formed into stars that a stellar generation gives straight back, "
        "under instantaneous recycling. Set by the IMF, which GALAXY_INPUTS.md §2 fixes as Level 0 "
        "(Kroupa/Chabrier; Salpeter is ruled out by the bulge dynamics) [verified: GALAXY_INPUTS.md "
        "§2]. 0.30 is the usual Kroupa/Chabrier value [recall]. Instantaneous recycling is the "
        "simple model's defining approximation; S9's DTD is what replaces it.",
    ),
    "KS_NORM": Constant(
        2.5e-4,
        "dimensionless",
        "Normalisation of the Kennicutt-Schmidt law, Sigma_SFR [Msun/yr/kpc2] = KS_NORM x "
        "(Sigma_gas [Msun/pc2])^KS_INDEX. (2.5 +/- 0.7) x 10^-4 as measured across disc and "
        "starburst galaxies [recall: Kennicutt 1998]. Dimensionless here because the vocabulary is "
        "closed and the law's units are carried by the formula, not the constant - flagged for the "
        "session that needs a compound SFR-surface-density unit. It is a *measured* normalisation "
        "and is deliberately not fitted: fitting it would make acceptance row 2 a check on the fit "
        "rather than on the model (GALAXY_INPUTS.md §4b).",
    ),
    "KS_INDEX": Constant(
        1.4,
        "dimensionless",
        "Exponent of the Kennicutt-Schmidt law, 1.4 +/- 0.15 [recall: Kennicutt 1998]. Level 0 by "
        "GALAXY_INPUTS.md §2, which names the K-S index and normalisation as constants.",
    ),
    "SF_THRESHOLD": Constant(
        5.0,
        "Msun/pc2",
        "Gas surface density below which star formation shuts off. Observed disc thresholds sit "
        "near 5-10 Msun/pc2 and are what truncate stellar discs while leaving HI far beyond them "
        "[recall: Kennicutt 1989; Martin & Kennicutt 2001]. Without it the outer gas would all turn "
        "into stars and the model would have no extended gas disc at all.",
    ),
    "GAS_DISC_SCALE_RATIO": Constant(
        1.0,
        "dimensionless",
        "Scale length of the *accreting* gas in units of the disc scale length lambda_d predicts. "
        "S2 set this to 1.5 from the observed HI-to-optical ratio, which was a mis-application it "
        "flagged itself: 1.5-2 is measured between *final* discs [recall: Broeils & Rhee 1997], "
        "not between the infall and the stars. S3 corrected it, and two independent arguments then "
        "agree on 1.0. MMW98 predicts the gas that forms the disc carries the halo's angular "
        "momentum distribution and so arrives with exactly the disc scale length; and running the "
        "model back from the *observed* final ratio picks 1.0-1.1, because star formation makes "
        "the surviving gas more extended than the gas that fell in. At 1.0 the model's fitted "
        "stellar scale length is 2.52 kpc against lambda_d's 2.605 - agreement to 3%, which "
        "discharges debt #13 [verified: tests/test_sfh.py::test_the_two_disc_scale_lengths_agree]. "
        "The constant is kept rather than deleted so that S10 can sweep it; at 1.0 it does nothing.",
    ),
    "MERGER_DURATION": Constant(
        0.5,
        "Gyr",
        "Time over which a merger delivers its gas, as a Gaussian width. Around half a Gyr for a "
        "major merger's crossing and settling [recall]. It is not cosmetic: delivering the gas "
        "instantaneously makes the star formation rate depend on the timestep, which is the same "
        "class of defect the star formation threshold had (D46).",
    ),
    "BIRTH_DISPERSION": Constant(
        8.0,
        "km/s",
        "Vertical velocity dispersion stars are born with, set by the turbulence of the gas they "
        "form from. Observed for the youngest disc stars [recall: ~6-10 km/s].",
    ),
    "SECULAR_HEATING": Constant(
        25.0,
        "km/s",
        "Vertical dispersion secular heating alone adds over 10 Gyr, from giant molecular clouds "
        "and spiral arms. The solar neighbourhood's age-velocity dispersion relation runs from "
        "about 20 km/s at 5 Gyr to 25-30 at 10 [recall], and S3 set this from the 10 Gyr end "
        "rather than from the 5 Gyr one, which was the first attempt and left the thin disc "
        "half the observed thickness. On its own this makes a gradient in sigma_z and no thick "
        "disc; a thick disc needs an event.",
    ),
    "SECULAR_HEATING_INDEX": Constant(
        0.5,
        "dimensionless",
        "Power of age in the secular age-velocity dispersion relation. Measured values run 0.3-0.5 "
        "[recall]; 0.5 is the random-walk value and the upper end of the observed range.",
    ),
    "MERGER_HEATING": Constant(
        120.0,
        "km/s",
        "Vertical dispersion a merger of mass ratio 1 would add to the stars already present; an "
        "event contributes this times its mass ratio. Scaled so the Milky Way's 1:4 merger leaves "
        "the pre-existing disc at about 30 km/s, which is what makes it thick rather than warm.",
    ),
    "BAR_LENGTH_RATIO": Constant(
        2.0,
        "dimensionless",
        "Bar half-length in units of the disc scale length. Bars in barred spirals run about "
        "1.5-2.5 R_d [recall]. GALAXY_INPUTS.md 4b describes the chain as disc dominance -> bar "
        "length -> pattern speed; only the second and third links are modelled here, because no "
        "relation between disc dominance and bar length is quoted anywhere in the project and "
        "inventing one would be rule A4's failure a level up. disc_dominance is published so the "
        "missing link can be checked rather than forgotten (debt #21).",
    ),
    "FAST_BAR_RATIO": Constant(
        1.2,
        "dimensionless",
        "Corotation radius in units of the bar half-length. Bars are observed to be 'fast', with "
        "R_CR/a_bar = 1.2 +/- 0.2 [verified: GALAXY_INPUTS.md 4b, citing BHG16 4.4].",
    ),
    "FAST_BAR_SCATTER": Constant(
        0.2,
        "dimensionless",
        "The +/- on FAST_BAR_RATIO, and it is *observed scatter* rather than measurement error - "
        "two galaxies with identical inputs credibly differ by this much. That is why it is a "
        "seeded draw and why acceptance rows 16 and 17 are statistical (GALAXY_INPUTS.md 4b, "
        "debt #8).",
    ),
    "PITCH_SHEAR_INTERCEPT": Constant(
        13.0,
        "deg",
        "Mean spiral pitch angle at shear rate 1, i.e. for a flat rotation curve. The Milky Way's "
        "arms are quoted near 12-13 degrees [recall]. Ruling 3 took PITCH_YU over PITCH_SEIGAR.",
    ),
    "PITCH_SHEAR_SLOPE": Constant(
        -8.0,
        "deg",
        "Degrees of pitch per unit shear rate: tighter arms where shear is stronger. Ruling 3 "
        "says the trend is weak, which is a claim S4 measured rather than assumed - the S-spread "
        "check reports how much of the pitch variance is trend and how much is draw.",
    ),
    "PITCH_SCATTER": Constant(
        6.0,
        "deg",
        "Dispersion of pitch angle about the shear trend. Large enough that ruling 3 calls pitch "
        "'effectively seeded rather than derived' [verified: GALAXY_INPUTS.md 5], which is exactly "
        "what the S-spread measurement checks.",
    ),
    "SOLAR_METALLICITY": Constant(
        0.0142,
        "dimensionless",
        "Present-day solar metallicity Z_sun, the zero point of [Fe/H] = log10(Z/Z_sun) [recall: "
        "Asplund et al. 2009].",
    ),
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
    "V_SUN_PECULIAR": Constant(
        12.24,
        "km/s",
        "The Sun's own tangential motion relative to the local standard of rest [recall: "
        "Schönrich, Binney & Dehnen 2010]. Acceptance row 3 measures the Sun's velocity in the "
        "Galactic rest frame, from the proper motion of Sgr A*, so it is v_c(R₀) plus this — not "
        "the circular speed. Leaving it out would understate row 3 by four times its error bar.",
    ),
}
