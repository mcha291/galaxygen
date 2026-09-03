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
    "V_SUN_PECULIAR": Constant(
        12.24,
        "km/s",
        "The Sun's own tangential motion relative to the local standard of rest [recall: "
        "Schönrich, Binney & Dehnen 2010]. Acceptance row 3 measures the Sun's velocity in the "
        "Galactic rest frame, from the proper motion of Sgr A*, so it is v_c(R₀) plus this — not "
        "the circular speed. Leaving it out would understate row 3 by four times its error bar.",
    ),
}
