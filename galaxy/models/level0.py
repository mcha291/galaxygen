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
        "Normalisation of c_vir = K(1 + z_f), the concentration a halo freezes in at its assembly "
        "epoch (ruling 5). K = 4.1 is quoted for c_vir [recall: Wechsler et al. 2002], at the virial "
        "overdensity Δ_vir(Ω_M) ≈ 101 ρ_crit; since S13 the halo stage converts it through the NFW "
        "profile to the c₂₀₀ it is built with (debt #12). K is a dark-matter-only calibration "
        "(Ω_M = 0.3, σ₈ = 1.0), so the concentration it gives is the halo's before it contracted "
        "around the disc; the 10–18 the Milky Way's measurements span are fits to the halo after, "
        "and are read against halo_concentration_contracted since S15. At the default epoch, 1.66 — "
        "the ΛCDM median for the default mass, derived at S15 — c_vir = 10.92 and c₂₀₀ = 8.25 before "
        "the response, 15.5 after it, inside the span; at the old 2.5 the fit read 18.5, over.",
    ),
    "OMEGA_M": Constant(
        0.3,
        "dimensionless",
        "Matter density parameter, the Ω_M = 0.3 Level 0 takes from BHG16 and F_BARYON already "
        "assumes [verified: GALAXY_INPUTS.md §2]. Read to form the virial overdensity "
        "Δ_vir = 18π² + 82x − 39x², x = Ω_M − 1 [recall: Bryan & Norman 1998] — about 101 ρ_crit — "
        "at which the c_vir normalisation is quoted (debt #12, S13).",
    ),
    "CONTRACTION_A": Constant(
        0.85,
        "dimensionless",
        "Adiabatic contraction of the halo by the disc's baryons (debt #6, S14): the invariant "
        "conserved as a dark-matter shell moves inward is r M(r̄) with r̄ = A R₂₀₀ (r/R₂₀₀)^w, the "
        "orbit-averaged radius standing in for the radius itself. A = 0.85, w = 0.8 is the form "
        "fitted to hydrodynamic simulations [recall: Gnedin et al. 2004]; A = w = 1 is the "
        "circular-orbit invariant r M(r) [recall: Blumenthal et al. 1986], which over-contracts "
        "against every simulation since and is kept as the named alternative (rule B12), not "
        "averaged in. Chosen before the row was read, on the literature, so that the number could "
        "not choose the ruleset (rule B5). A later revision makes A and w depend on halo mass and "
        "epoch [recall: Gnedin et al. 2011] and is not adopted (debt #46).",
    ),
    "CONTRACTION_W": Constant(
        0.8,
        "dimensionless",
        "The exponent of the orbit-averaged radius in the contraction invariant; see CONTRACTION_A. "
        "w = 1 with A = 1 recovers the circular-orbit invariant.",
    ),
    "ANGULAR_MOMENTUM_MU": Constant(
        1.25,
        "dimensionless",
        "Shape of the halo's specific-angular-momentum distribution, M(< j) = M μ j/(j₀ + j) with "
        "j ≤ j₀/(μ − 1): the universal profile of ΛCDM haloes, whose μ − 1 has log-mean −0.6 and "
        "scatter 0.4 dex — median μ = 1.25, 90% of haloes between 1.06 and 2.0 [verified: Bullock et "
        "al. 2001, read at S16]. Read by the halo stage to derive the extended accretion component "
        "(debt #18, S16): the exponential disc MMW98 assume holds the distribution's low-j part, and "
        "what it does not hold beyond their outer crossing — the high-j tail, about 9% of the "
        "budget beyond 12 kpc at the default — is the gas the star formation threshold leaves as the "
        "outer HI disc. Since S17 the *low-j* excess inside the inner crossing is read off the same "
        "construction as the central spheroid (debt #11, D121), so one constant now sets both ends of "
        "the disc the exponential does not describe: at μ = 1.06 the spheroid is 1.46 × 10¹⁰ M☉ and "
        "at 1.40 it is 5.6 × 10⁹. The scatter in μ is not absorbed by any input (debt #47).",
    ),
    "R_SUN": Constant(
        8.2,
        "kpc",
        "Galactocentric radius of the Sun, R₀ = 8.2 ± 0.1 kpc [verified: GALAXY_INPUTS.md §7 row "
        "3's source BHG16]. Where every 'solar neighbourhood' quantity is evaluated.",
    ),
    "HELIUM_MASS_FRACTION": Constant(
        0.27,
        "dimensionless",
        "Helium mass fraction of the gas, Y. Primordial 0.245, solar 0.27, and the disc's "
        "interstellar gas sits near the solar value [recall]. Read to publish the gas's hydrogen "
        "mass, which is what acceptance row 20's HI + H₂ target counts (debt #41, S13); the metals' "
        "one to two percent is not taken out, the sfh stage being upstream of the chemistry.",
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
    "TOOMRE_ALPHA": Constant(
        0.69,
        "dimensionless",
        "Kennicutt's star formation threshold is the gas surface density at which a disc with "
        "velocity dispersion sigma_g is Toomre-unstable, Sigma_crit = alpha kappa sigma_g / 3.36 G, "
        "and alpha is the measured ratio of the observed threshold to the ideal one: 0.63 in the "
        "1989 sample, 0.69 +/- 0.2 in the larger one [recall: Kennicutt 1989; Martin & Kennicutt "
        "2001]. Derived from the rotation curve's epicyclic frequency since S18 (debt #47): 11 "
        "Msun/pc2 at R_0, 26 at 4 kpc, 4 at 20 kpc. Until then the threshold was the constant 5, "
        "the bottom of its cited 5-10, which held the gas at R_0 at 6.3 against the observed 10-13 "
        "(AUDIT_RUN2.md D-3). alpha and GAS_DISPERSION are one calibration: alpha was fitted with "
        "the dispersion assumed, so their product, 4.1 km/s, is what is measured (rule B10).",
    ),
    "GAS_DISPERSION": Constant(
        6.0,
        "km/s",
        "Velocity dispersion of the cold gas the threshold is evaluated at, the 6 km/s Kennicutt "
        "assumed everywhere when fitting alpha [recall: Kennicutt 1989]. The Milky Way's HI reads "
        "7-10 at R_0 and rises inward [recall], but alpha was calibrated with this value, so moving "
        "one without the other breaks the calibration (see TOOMRE_ALPHA). At 8 km/s the gas at R_0 "
        "reads 13.6 and row 9 falls to 0.025 (D119's probe): the pair is read as one number.",
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
    "MERGER_DURATION": Constant(  # read by assembly; its window reaches sfh since S13 (debt #30)
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
        88.8,
        "km/s",
        "Velocity dispersion a merger of mass ratio 1 would add to the stars already present; an "
        "event contributes this times its mass ratio. Set so that the Milky Way's 1:4 merger leaves "
        "the pre-existing disc at the thick disc's observed vertical dispersion, sigma_W = 35 km/s "
        "[recall: Bensby, Feltzing & Lundstrom 2003, (67, 38, 35) for the thick disc], **net of the "
        "heating the model already gives those stars**: the assembly stage composes the kick in "
        "quadrature with the secular heating and the birth dispersion, which together read 27.06 km/s "
        "over the thick population at R_0, so the kick is sqrt(35^2 - 27.06^2) = 22.2 km/s and the "
        "constant is 22.2/0.25 (S20, debt #42; a test reproduces the arithmetic). Until S20 it was "
        "120 - 'scaled so the merger leaves the pre-existing disc at about 30 km/s' - which counted "
        "the kick as if it were the whole dispersion, so the thick disc read 40.4 and row 7 1279 pc; "
        "it reads 960 now. Since S18 the same impulse is applied radially too (isotropic; an "
        "anisotropic kick has no cited number), and the epicyclic frequency turns it into a "
        "displacement of 1.09 kpc at R_0 (1.47 at 120; debt #19, D124). The re-derivation costs row 3, "
        "which S18 had landed on the kick by 0.04 and which reads 251.03 now (debt #11). "
        "**The named alternative, kept and not averaged (rule B12), is 112.3 km/s**: S21 (a) read the "
        "citation and the 35 is Bensby et al.'s Table 1 adopted characteristic value for a kinematic "
        "selection function, quoted without an uncertainty, while the measurement their Sect. 1 quotes "
        "for it is Soubiran, Bienayme & Siebert 2003's sigma_W = 39 +/- 4; net of the same 27.06 that "
        "gives sqrt(39^2 - 27.06^2)/0.25 = 112.3, at which row 7 reads 1193 (out) and row 3 250.97 "
        "(in) - the two rows trade across the source's own error bar and the window's top edge is "
        "sigma_W = 37.1. S22 kept 88.8: the arithmetic is S20's derivation and choosing between the "
        "two values with both rows' answers already known is the move rule B5 forbids in either "
        "direction. What S22 changed is that row 7's green says here, and in spec.py, what it stands "
        "on (AUDIT_II_A.md A-14, debt #42).",
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
    # --- the planets stage (S8, GALAXY_INPUTS.md §12) -------------------------
    "DISC_MASS_FRACTION": Constant(
        0.01,
        "dimensionless",
        "Protoplanetary disc mass as a fraction of the star's, at the moment planet formation "
        "starts [recall: surveys of Class II discs put the median near 1% of the stellar mass]. "
        "It is a median, not a value: the residual is DISC_MASS_SCATTER and is seeded, which is "
        "what makes occurrence a probability rather than a verdict.",
    ),
    "DISC_MASS_SCATTER": Constant(
        0.3,
        "dex",
        "Log-normal width of the disc-mass residual about that median [recall: GALAXY_INPUTS.md "
        "§12 quotes ~0.3 dex]. This constant does more work than its size suggests: giant "
        "occurrence is the probability that a log-normal disc clears the critical core mass, so "
        "the *slope* of occurrence against [Fe/H] is set by this width and not by any occurrence "
        "law. A narrower disc distribution makes a steeper metallicity dependence.",
    ),
    "PLANETESIMAL_EFFICIENCY": Constant(
        0.171,
        "dimensionless",
        "Share of a disc's solid mass that reaches planetesimals and then cores, rather than "
        "being lost to radial drift or accreted by the star [recall: the streaming-instability "
        "literature spans tens of percent]. **This absorbs GALAXY_INPUTS.md §12's separate "
        "'occurrence normalisation'**: in this formation model the two are the same number — a "
        "factor in front of the solid budget — and declaring both would be inventing a variable "
        "to justify a stage (rule A4). It is the one constant in the stage fitted to an "
        "observation: 0.171 puts giant occurrence at 5% for a solar-mass star at [Fe/H] = 0, "
        "which is where the Adibekyan review puts it [recall: GALAXY_INPUTS.md §12]. Everything "
        "else about occurrence — its slope, its stellar-mass dependence, its value anywhere else "
        "— is then a prediction, and debt #25 records what those predictions cost.",
    ),
    "CORE_CRITICAL_MASS": Constant(
        10.0,
        "Mearth",
        "Core mass above which a protoplanet's envelope can no longer stay in hydrostatic "
        "equilibrium and runaway gas accretion begins [recall: the classical core-accretion "
        "threshold, ~10 M⊕]. A giant is a core that reached this beyond the ice line before the "
        "disc dispersed; everything else stays a solid planet.",
    ),
    "ICE_LINE_TEMPERATURE": Constant(
        170.0,
        "K",
        "Disc temperature at which water condenses, which is where the solid surface density "
        "jumps [recall: ~170 K at protoplanetary disc pressures]. It is a temperature rather than "
        "a radius because the radius is derived from the star's own luminosity — a hotter star "
        "pushes its ice line out, which is why occurrence depends on stellar mass at all.",
    ),
    "ICE_BOOST": Constant(
        2.0,
        "dimensionless",
        "Factor by which the solid surface density rises across the ice line, once water is a "
        "solid [recall: Hayashi's minimum-mass solar nebula uses about 4; measurements of the "
        "condensable inventory support 2-4]. The low end is taken deliberately: the factor and "
        "PLANETESIMAL_EFFICIENCY are degenerate in the solid budget, and only one of them can be "
        "calibrated without the other becoming meaningless (rule B10).",
    ),
    "HILL_SEPARATION": Constant(
        10.0,
        "dimensionless",
        "Minimum spacing between neighbouring planets, in mutual Hill radii — the closed-form "
        "stability criterion GALAXY_INPUTS.md §12 requires in place of an integrator [recall: "
        "systems below about 10 mutual Hill radii are not long-term stable]. This is what sets "
        "the architecture: the chain is laid out from the inner edge with each step the previous "
        "planet's own Hill radius times this, so a massive planet clears a wide gap and a small "
        "one does not.",
    ),
    "DISC_INNER_EDGE": Constant(
        0.05,
        "AU",
        "Inner edge of the planet-forming region, where the disc is truncated by the star's "
        "magnetosphere [recall: co-rotation for a few-day rotation period]. Nothing forms inside "
        "it, so it is where the orbital chain starts.",
    ),
    "DISC_OUTER_EDGE": Constant(
        30.0,
        "AU",
        "Outer edge of the region where planet formation completes within the disc's lifetime "
        "[recall: beyond a few tens of AU growth times exceed disc lifetimes, which is why the "
        "Solar System's planets stop at Neptune and the Kuiper belt is unaccreted]. Solids "
        "beyond it are counted into the budget but never assembled.",
    ),
    "BLACK_HOLE_NORM": Constant(
        0.309e9,
        "Msun",
        "M_• at σ = 200 km/s in the M–σ relation ruling 10 takes, M_•/10⁹ M☉ = 0.309 (σ/200)^4.38 "
        "[verified: GALAXY_INPUTS.md §13, citing Ho 2014 eq. 2]. It is the relation for **classical "
        "bulges and ellipticals**, which is why the model publishes the classical share of its own "
        "spheroid beside it: pseudobulges show no significant correlation at all, so applying this "
        "to a pseudobulge-dominated galaxy is applying a relation that does not hold for the object "
        "(GALAXY_INPUTS.md §13). The Milky Way is such a galaxy and acceptance row 18 is expected to "
        "miss by ~0.75 dex because of it, which is a property of the source and not of the model.",
    ),
    "BLACK_HOLE_INDEX": Constant(
        4.38,
        "dimensionless",
        "Slope of the M–σ relation, the exponent in BLACK_HOLE_NORM's formula [verified: "
        "GALAXY_INPUTS.md §13, citing Ho 2014 eq. 2]. Steep enough that the row is a check on the "
        "velocity dispersion far more than on the normalisation: a 3% error in σ is 13% in M_•.",
    ),
    "BLACK_HOLE_SCATTER": Constant(
        0.28,
        "dimensionless",
        "Width of the seeded M_• residual, in dex of log₁₀ M_•, drawn about the M–σ mean (ruling 10; "
        "the residual is real and nobody would choose it, §4b). 0.28 dex is the intrinsic scatter "
        "**for classical bulges and ellipticals** [verified: GALAXY_INPUTS.md §13, citing Kormendy & "
        "Ho via Ho 2014]. Ruling 10 asks for this width to be interpolated by the classical share "
        "the model computes, towards the pseudobulge end; that end has no published number — "
        "Kormendy & Ho declined to fit pseudobulges at all and Ho & Kim 2014 say only 'a different "
        "zero point and much larger scatter' — so the interpolation is not done and this width, the "
        "narrow end, is used for a galaxy whose spheroid the model calls 83% pseudo. It therefore "
        "**understates** the spread, which is debt #48; it moves no verdict, because a statistical "
        "row is judged on its median (D109) and the median is the mean relation at any width.",
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
