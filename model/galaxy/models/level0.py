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
    "HALPHA_PER_SFR": Constant(  # read by light (RENDER_PLAN M4)
        4.86e7,
        "Lsun",
        "Intrinsic Hα luminosity, in L☉, per M☉/yr of star formation: Kennicutt & Evans 2012's "
        "calibration log SFR = log L(Hα) − 41.27 for a Kroupa IMF, with L(Hα) in erg/s, over "
        "L☉ = 3.828 × 10³³ erg/s [recall: Kennicutt & Evans 2012, ARA&A 50, 531, Table 1]. "
        "Intrinsic: before the dust the line is emitted through.",
    ),
    "SOLAR_ABSOLUTE_MAGNITUDE_V": Constant(  # read by light (S28, BUILD_II Phase 3)
        4.81,
        "mag",
        "The Sun's absolute magnitude in Johnson V, Vega system: 4.81 [verified: Willmer 2018, ApJS "
        "236, 47, Table 3 'Magnitudes of the Sun', Johnson_V Abs(Vega), read from arXiv:1804.07788 at "
        "S28]. It is what turns a V magnitude into V-band solar luminosities, for the mass-to-light "
        "ratio and the V surface brightness. The isochrones' own Sun (1 M☉, 4.57 Gyr, solar) reads "
        "4.773, 0.037 brighter, which is the named alternative and is not used: a solar luminosity "
        "is a unit, and the unit is the observed Sun's [verified: tests/test_photometry.py].",
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
    # --- molecular clouds: the population the ISM's molecular gas is drawn as (S32, BUILD_II Phase 8, D181) ---
    "GMC_MASS_SLOPE_INNER": Constant(
        -1.6,
        "dimensionless",
        "Slope of the giant-molecular-cloud mass function inside the solar circle, dN/dM proportional to "
        "M^gamma up to a truncation mass: gamma = -1.6 +/- 0.1 [verified: Rice et al. 2016, ApJ 822, 52, "
        "arXiv:1602.02791, abstract and section IV.4, read at S32 by a read-only agent]. The functional "
        "form is Rosolowsky 2005's eqs. 3-4 (PASP 117, 1403), whose inner-Milky-Way fit, -1.53 +/- 0.07 "
        "with a truncation near 3e6 [verified: its Table 1, read at S32], is the named alternative.",
    ),
    "GMC_MASS_TRUNCATION_INNER": Constant(
        1.0e7,
        "Msun",
        "Upper truncation of the inner Galaxy's cloud mass function, (1.0 +/- 0.2) x 10^7 [verified: Rice "
        "et al. 2016, abstract and section IV.4].",
    ),
    "GMC_MASS_SLOPE_OUTER": Constant(
        -2.2,
        "dimensionless",
        "Slope of the cloud mass function outside the solar circle, -2.2 +/- 0.1, a non-truncating power "
        "law in the source [verified: Rice et al. 2016, abstract and section IV.4]; Rosolowsky 2005's outer "
        "Milky Way -2.56 +/- 0.11 is the alternative. The inner/outer boundary is taken at the solar "
        "radius, the sources' 'inner' and 'outer Galaxy' [inferred].",
    ),
    "GMC_MASS_TRUNCATION_OUTER": Constant(
        1.5e6,
        "Msun",
        "The outer Galaxy's largest cloud mass, (1.5 +/- 0.5) x 10^6 [verified: Rice et al. 2016, abstract]; "
        "the source calls the law non-truncating and this is its upper end, used as the cut.",
    ),
    "GMC_MASS_MIN": Constant(
        1.0e4,
        "Msun",
        "The smallest cloud the catalogue draws. No completeness limit was read from the sources at S32, "
        "so this is the mass at which a 'giant' molecular cloud is conventionally said to begin "
        "[inferred]. With gamma near -1.6 the mass in clouds is set by the top of the function and moves "
        "6% for a factor of ten here; the count is set by this end and moves fourfold (debt #94).",
    ),
    "GMC_SURFACE_DENSITY": Constant(
        42.0,
        "Msun/pc2",
        "Mean mass surface density of a giant molecular cloud, from which its radius follows as "
        "sqrt(M / pi Sigma): 'the median mass surface density of molecular hydrogen for this sample is "
        "42 Msun/pc2' [verified: Heyer et al. 2009, ApJ 699, 1092, arXiv:0809.1397, abstract, read at "
        "S32]. The named alternatives are Roman-Duval et al. 2010's median 144 (ApJ 723, 492, section "
        "VI.3; their M = 228 R^2.36, eq. 13) and Solomon et al. 1987's 206, which Heyer et al. re-derive "
        "downward; three sourced values, the largest homogeneous re-analysis chosen (rule B12).",
    ),
    "MOLECULAR_GAS_TEMPERATURE": Constant(
        10.0,
        "K",
        "Kinetic temperature of molecular cloud gas, for the sound speed the Mach number is measured "
        "against: 'gas temperatures ~10-20 K' for dark clouds and 'about 10 K' for their dense cores "
        "[verified: Bergin & Tafalla 2007, ARA&A 45, 339, arXiv:0705.3765, sections 1, 2.2 and 3.2.2, "
        "read at S32]; the same review states the sound speed as 0.2 km/s at 10 K (section 2.5). 20 K, "
        "the warm end of the range, is the named alternative.",
    ),
    "MOLECULAR_MEAN_WEIGHT": Constant(
        2.33,
        "dimensionless",
        "Mean mass per particle of molecular gas in proton masses, H2 with helium at the solar ratio: "
        "1/(X/2 + Y/4) for X = 0.71, Y = 0.28 [inferred: arithmetic on the composition]. The sound speed is "
        "sqrt(k T / mu m_H): 0.19 km/s at 10 K, the review's 0.2.",
    ),
    "TURBULENCE_FORCING_B": Constant(
        0.4,
        "dimensionless",
        "The forcing parameter b in the width of a cloud's log-normal density distribution, sigma_s^2 = "
        "ln(1 + b^2 M^2) [verified: Federrath, Klessen & Schmidt 2008, ApJL 688, L79, eq. 4; Federrath et "
        "al. 2010, A&A 512, A81, eq. 19]: 'for zeta >~ 0.5 the b-parameter remains close to the value "
        "obtained for purely solenoidal forcing, i.e. b ~ 0.3-0.4 in 3D' [verified: Federrath et al. 2010, "
        "section 3.6, read at S32], the natural mixture. Purely solenoidal 0.36 +/- 0.03 and purely "
        "compressive 1.05 +/- 0.19 (FKS08 Table 1) are the named alternatives; published as a scalar "
        "because the renderer that synthesises a cloud's interior reads it (D180's rule).",
    ),
    "GMC_PHASE_EMBEDDED": Constant(
        6.0,
        "Myr",
        "How long a cloud shows no massive star formation (Kawamura et al. 2009's Type I): 6 Myr, of a "
        "20-30 Myr lifetime, 'rough' by the source's own word [verified: Kawamura et al. 2009, ApJS 184, 1, "
        "arXiv:0908.1168, Table 3 and section IV.2, read at S32]. Murray 2011's 17 +/- 4 Myr total (ApJ "
        "729, 133, abstract) and Chevance et al. 2020's 10-30 Myr (MNRAS 493, 2872, abstract) are the "
        "named alternatives for the whole lifetime; a fourth, dispersed 'remnant' state has no sourced "
        "duration and is not drawn (debt #95).",
    ),
    "GMC_PHASE_BLOWN_OPEN": Constant(
        13.0,
        "Myr",
        "How long a cloud carries HII regions but no exposed cluster (Kawamura et al. 2009's Type II): 13 "
        "Myr [verified: the same Table 3].",
    ),
    "GMC_PHASE_DISPERSING": Constant(
        7.0,
        "Myr",
        "How long a cloud carries HII regions and young clusters before it is gone (Kawamura et al. 2009's "
        "Type III): 7 Myr [verified: the same Table 3]. The three phases sum to 26 Myr, the lifetime a cloud's "
        "age is drawn over; Kruijssen et al. 2019 read 1.5 Myr for the overlap of clouds and HII regions in "
        "NGC 300 (Nature 569, 519, arXiv:1905.08801), the alternative reading of the last two phases.",
    ),
    # --- star clusters: one per cloud past its embedded phase (S33, BUILD_II Phase 11). Every number
    # below was read at S33 in its source's text (rule B9, D175); the sentence is quoted in the line. The
    # efficiency per cloud is derived, not a constant (the orchestrator's ruling on S33's first pass):
    # the sourced values it is read against are in the cluster_formation_efficiency scalar's about. ---
    "CLUSTER_BOUND_FRACTION": Constant(
        0.07,
        "dimensionless",
        "The chance a cluster emerges from its cloud bound: 'Less than 4-7% of embedded clusters survive "
        "emergence from molecular clouds to become bound clusters of Pleiades age' (abstract) and 'only "
        "about 7% of all embedded clusters survive to Pleiades age' (section 2.5) [verified: Lada & Lada "
        "2003, ARA&A 41, 57, astro-ph/0301540, read at S33]. The upper end of the range, by number and "
        "independent of mass; the same section's 'It is likely that only the most massive clusters in "
        "our catalog are candidates for long term survival' is the named alternative (a mass cut), not "
        "built: its 500 Msun is a sub-cloud embedded cluster's, below every cluster this census makes.",
    ),
    "CLUSTER_DISSOLUTION_AGE": Constant(
        10.0,
        "Myr",
        "The age by which an unbound cluster has dispersed: 'the vast majority of embedded clusters do "
        "not survive emergence from molecular clouds as identifiable systems for periods even as long as "
        "10 Myr ... less than 10% survive longer than 10 Myr. Indeed, most clusters may dissolve well "
        "before they reach an age of 10 Myr' [verified: Lada & Lada 2003, section 2.5, read at S33]. An "
        "upper bound in the source, used as the time.",
    ),
    "CLUSTER_HALF_MASS_DENSITY": Constant(
        1.0e3,
        "Msun/pc3",
        "The half-mass density rho_hm = 3M/(8 pi r_hm^3) young clusters form at: 'For young clusters "
        "(<~ 10 Myr) there seems to be some positive correlation between mass and radius, roughly "
        "consistent with a density of 10^(3+/-1) Msun pc^-3' [verified: Portegies Zwart, McKee & Gieles "
        "2010, ARA&A 48, 431, arXiv:1002.1961, section 4.4.2, and Fig. 9's caption for the definition, "
        "read at S33]. The named alternative is a constant radius, the same section's reading of "
        "clusters older than 10 Myr and Larsen 2004's 'most star clusters seem to have about the same "
        "size', a mean half-light radius of '4 +/- 1 pc' in the Antennae (astro-ph/0408201, section "
        "6.3, read at S33).",
    ),
    # --- swing amplification: the arm number and the arms' strength (S26, BUILD_II Phase 1b, D175) ---
    "SWING_X_LOW": Constant(
        1.0,
        "dimensionless",
        "Lower edge of the X range over which swing amplification is vigorous, for a flat rotation "
        "curve. X = kappa^2 R / (2 pi G Sigma m); 'in a disk with Gamma = 1 and Q = 1.2, the "
        "amplification factor may vary from less than 2 for X > 3 to greater than 100 for 1 < X < 2' "
        "[verified: Sellwood & Masters 2022, ARA&A 60, 73, section 4.2.3.2]. The peak sits at X = 1.5 "
        "[verified: D'Onghia 2015, ApJL 808, L8, citing Toomre 1981 and Athanassoula 1984]. The edges "
        "scale with the shear rate: the vigorous range is 0.5-1.5 at Gamma = 0.5 and 1.5-4 at 1.5 "
        "[verified: the same section], so the stage tests X/Gamma against these edges - exact at the "
        "lower edge for all three quoted shears, a third short at the upper edge for Gamma = 1.5 "
        "[inferred]. In the Mestel form X_m = 2/(m f_d), the same range reads 1/f_d <= m <= 2/f_d for "
        "the arm number, which the review states outright [verified: the same section].",
    ),
    "SWING_X_HIGH": Constant(
        2.0,
        "dimensionless",
        "Upper edge of the vigorous range, 'greater than 100 for 1 < X < 2' [verified: Sellwood & "
        "Masters 2022 section 4.2.3.2]. Between here and SWING_X_DEAD the pattern stage's odds for an "
        "arm number fall log-linearly to zero [inferred: the shape; the two edges are the source's].",
    ),
    "SWING_X_DEAD": Constant(
        3.0,
        "dimensionless",
        "Where amplification has stopped: 'less than 2 for X > 3' [verified: Sellwood & Masters 2022 "
        "section 4.2.3.2]. An arm number whose X sits here or beyond is not drawn.",
    ),
    "SWING_X_FLOOR": Constant(
        0.5,
        "dimensionless",
        "Below SWING_X_LOW the odds fall log-linearly to zero here. 0.5 is the lower edge of the "
        "vigorous range the source quotes for Gamma = 0.5 [verified: Sellwood & Masters 2022 section "
        "4.2.3.2]; using it as the floor at Gamma = 1 is the inference, since the source gives no "
        "lower cut-off for a flat curve [inferred]. It bounds how many arms a halo-dominated disc can "
        "carry: X_m < floor is a wavelength the disc cannot amplify at all.",
    ),
    "ARM_MULTIPLICITY_MAX": Constant(
        6.0,
        "count",
        "The most arms one pattern is allowed: beyond six a disc is flocculent and no single m "
        "describes it [inferred]. D'Onghia 2015 expects 'a total of 5-6 spiral arms, lower in "
        "strength, in the solar neighborhood' for the Milky Way [verified: D'Onghia 2015, ApJL 808, "
        "L8], so six is the multi-arm regime her own estimate reaches, not an invention. m = 1 is "
        "excluded: 'the overwhelming majority of spirals in galaxies have two- or three-fold rotational "
        "symmetry' [verified: Sellwood & Masters 2022, abstract].",
    ),
    "ARM_INTERARM_GRAND_DESIGN": Constant(
        1.14,
        "mag",
        "Arm-interarm contrast of grand-design spirals in the old stellar disc: 1.14 +/- 0.44 mag at "
        "3.6 micron, 13 galaxies, all Hubble types [verified: Elmegreen et al. 2011, ApJ 737, 32, "
        "section 4.2 and Table 2, the class means recomputed from the table's 46 rows in "
        "tests/test_s26_rulings.py]. The stage turns a contrast C = 10^(0.4 mag) into the cosine "
        "amplitude A = (C - 1)/(C + 1), because the pattern is one harmonic and its whole "
        "arm-interarm contrast is that amplitude. The alternative is the arms' m = 2 Fourier "
        "amplitude, 0.21 +/- 0.08 for the same 13 galaxies (Table 2): a real arm carries higher "
        "harmonics that a single cosine does not, so matching the Fourier amplitude would draw arms "
        "with a 0.4 mag contrast where 1.1 is observed. Chosen before the number was read (D175).",
    ),
    "ARM_INTERARM_FLOCCULENT": Constant(
        0.75,
        "mag",
        "Arm-interarm contrast of flocculent spirals in the old stellar disc: 0.75 +/- 0.35 mag at "
        "3.6 micron, 13 galaxies [verified: Elmegreen et al. 2011 section 4.2 and Table 2]. The "
        "16-galaxy multi-band subsample reads 0.44 +/- 0.13 for flocculents at 3.6 micron [verified: "
        "the same paper, Table 3]; the larger sample is used and the smaller is the named alternative. "
        "The arms' mean contrast runs from here to ARM_INTERARM_GRAND_DESIGN with the two-fold "
        "pattern's amplification weight - a halo-dominated disc, which cannot amplify m = 2, gets "
        "flocculent arms [inferred: the link; the two end points are the source's].",
    ),
    "ARM_INTERARM_SCATTER": Constant(
        0.44,
        "mag",
        "Dispersion of the arm-interarm contrast about its class mean, the grand-design class's 0.44 "
        "mag [verified: Elmegreen et al. 2011 section 4.2]; the multiple-arm class reads 0.28 and the "
        "flocculent 0.35. Drawn on pattern_seed as the residual a derived mean cannot carry "
        "(GALAXY_INPUTS.md 4b, verdict C).",
    ),
    "BAR_CONTRAST_MEDIAN": Constant(
        0.374,
        "dimensionless",
        "Median of the bar's maximum normalised m = 2 Fourier density amplitude, A_2^max, over the 587 "
        "barred S4G galaxies at 3.6 micron: median 0.374, mean 0.412, 16th-84th percentiles 0.214-0.609 "
        "[verified: Diaz-Garcia et al. 2016, A&A 587, A160, VizieR J/A+A/587/A160 tablea3.dat column "
        "A2, read and reduced on 2026-09-26 (D175)]. A pure cos 2phi bar has A_2 equal to its "
        "amplitude, so this is the bar_contrast like for like. The median rather than the mean because "
        "the distribution is skewed (maximum 1.3). Elmegreen et al. 2011's 13 grand designs read a "
        "peak m = 2 of 0.43 +/- 0.12 (Table 2), the named alternative. Not derived from the bar's "
        "length: the correlation is real ('long bars are typically strong', the same paper's abstract) "
        "but bar_half_length is a constant times R_d in this model, so it has no lever (debt #21).",
    ),
    "BAR_CONTRAST_LOG_SCATTER": Constant(
        0.52,
        "dimensionless",
        "Half the natural-log width of A_2^max's 16th-84th percentile range, ln(0.609/0.214)/2 "
        "[verified: the same VizieR table]. Drawn log-normally on pattern_seed and capped at 0.9, since "
        "an amplitude at 1 empties the inter-bar sector and a Fourier amplitude above 1 describes a "
        "peaked bar no single cosine can (the table's top 2% exceed 0.9).",
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

    # ---- The cold ISM (S24). Both prescriptions carry a second measured pair,
    # kept beside them and never averaged (rule B12).
    "H2_PRESSURE_LOG_NORM": Constant(
        4.54,
        "dimensionless",
        "log₁₀(P₀/k_B) in cm⁻³ K: the midplane pressure at which the ISM is equal parts HI and H₂ "
        "[recall: Blitz & Rosolowsky 2006, fourteen nearby galaxies, 4.54 ± 0.07]. **The measured "
        "alternative is 4.23** [recall: Leroy et al. 2008, larger sample, with a pressure estimate "
        "that adds the gas self-gravity this stage's form omits]. Kept beside it, never averaged "
        "(rule B12): the two belong to different pressure estimates, so mixing this norm with "
        "Leroy's index would be a third prescription nobody measured.",
    ),
    "H2_PRESSURE_INDEX": Constant(
        0.92,
        "dimensionless",
        "The exponent α in R_mol = (P/P₀)^α [recall: Blitz & Rosolowsky 2006, 0.92 ± 0.07]. **The "
        "measured alternative is 0.8** [recall: Leroy et al. 2008; Wong & Blitz 2002 also found "
        "0.8]. Belongs with H2_PRESSURE_LOG_NORM — change both or neither.",
    ),
    "H2_GAS_DISPERSION": Constant(
        8.0,
        "km/s",
        "The gas vertical velocity dispersion the pressure estimate assumes [recall: Blitz & "
        "Rosolowsky 2006]. **Leroy et al. 2008 adopt 11 km/s** for the composite ISM. This belongs "
        "to the prescription rather than to the model: it is not the model's own gas dispersion "
        "and must not be swapped for one, or the fitted P₀ no longer means what it was fitted as.",
    ),
    "DUST_TO_GAS_SOLAR": Constant(
        1.0 / 162.0,
        "dimensionless",
        "Dust-to-gas mass ratio at solar abundance: the reciprocal of (G/D)☉ = 162 [recall: Zubko "
        "et al. 2004, as adopted throughout Rémy-Ruyer et al. 2014]. **This number and "
        "DUST_TO_GAS_SLOPE are a matched pair and must not be changed separately**: Rémy-Ruyer "
        "imposed their fits to pass through Zubko's value, so the slope was measured *given* this "
        "normalisation. Relaxing that condition gives solar G/D anywhere from 90 to 240 - about "
        "60% either way - which is the real uncertainty on this constant and is larger than it "
        "looks.",
    ),
    "DUST_TO_GAS_SLOPE": Constant(
        1.6,
        "dimensionless",
        "D/G proportional to Z^1.6, the single power law [recall: Rémy-Ruyer et al. 2014, "
        "G/D ∝ (O/H)^-1.6 ± 0.3 for a Galactic X_CO; -2.0 ± 0.3 if X_CO scales as Z^-2]. **The "
        "alternative is a broken power law**, which the same paper finds reproduces the data best; "
        "De Vis et al. 2019 find a single law no worse on a larger late-type sample. A live "
        "disagreement, kept as one (rule B12). Its parameters *are* sourced - low-metallicity "
        "slope -3.1 (± 1.8 for a Galactic X_CO, ± 1.3 for X_CO ∝ Z^-2, the same central value "
        "either way), high-metallicity slope fixed to 1 following James et al. 2002 and Draine et "
        "al. 2007, transition at 12 + log(O/H) = 7.96 ± 0.47 - and they are recorded here rather "
        "than declared as constants, because **a ruleset is a stage implementation, not a constant "
        "beside the default**: preflight rejects a model carrying a constant no stage reads (D29), "
        "which is exactly what happened when they were first added. Adopting the broken law means "
        "a second ism implementation, as chemistry_dtd is to chemistry. Matched to "
        "DUST_TO_GAS_SOLAR - see there.",
    ),
    "DUST_EXTINCTION_COEFFICIENT": Constant(
        7.71,
        "dimensionless",
        "A_V in magnitudes per M☉/pc² of **dust**, applied to a gas column that **includes "
        "helium**. From N_H/A_V = 1.9 × 10²¹ cm⁻² mag⁻¹ [recall: Bohlin, Savage & Drake 1978], "
        "with 1 M☉/pc² of total gas carrying 1.248 × 10²⁰ nuclei cm⁻² if it were all hydrogen but "
        "only X = 1/1.38 = 0.725 of that in hydrogen once helium and metals are counted — giving "
        "0.0476 mag per M☉/pc² of gas, then divided by the dust-to-gas ratio 1/162 to express it "
        "per unit dust. **Both factors were wrong on first writing and each was caught by a "
        "different method**: the 162 by a sanity check against a known value (A_V at the Sun read "
        "0.003 mag, not ~0.5), the 1.38 by a reader noticing that gas_surface_density carries "
        "helium while this arithmetic did not. The helium belongs here and not in "
        "DUST_TO_GAS_SOLAR: Rémy-Ruyer define their gas mass as μ(M_HI + M_H₂) with "
        "μ = 1/(1 − Y − Z) = 1.38, so (G/D)☉ = 162 is already on a total-gas basis and correcting "
        "it there too would count helium twice. A_V at the Sun now reads 0.512 mag.",
    ),
    # --- S30 (BUILD_II Phase 6): supernova rates. Both read from their sources by a read-only
    # agent at S30, confirmed by a second fetch, and entered as printed (rule B9; D175).
    "CORE_COLLAPSE_MIN_MASS": Constant(
        8.5,
        "Msun",
        "The lowest initial mass that ends in a core-collapse supernova, m_min = 8.5 (+1, -1.5) "
        "Msun for a type II-P progenitor: a maximum-likelihood fit to the masses and upper limits "
        "of the progenitors in a volume-limited sample of nearby supernovae [verified: Smartt 2009, "
        "ARA&A 47, 63, section 4.4, arXiv:0908.0700, read at S30]. The named alternative is Heger "
        "et al. 2003, who adopt 9 Msun inside a debated 6-11 [verified: ApJ 591, 288, section "
        "IV.1, astro-ph/0212469, read at S30]; 9 lowers the rate by 7%. BUILD_II's 8 Msun was "
        "recall and is not the number the source prints. Every star from here to the IMF's upper "
        "end counts as one supernova: no source for which massive stars collapse without "
        "exploding has been read.",
    ),
    "IA_IRON_MASS": Constant(
        0.7,
        "Msun",
        "Iron ejected by one type Ia supernova, the mean yield Maoz & Graur adopt (citing Mazzali et "
        "al. 2007 and Howell et al. 2009) [verified: Maoz & Graur 2017, ApJ 848, 25, section III "
        "eq. 2, arXiv:1703.04540, read at S30]. It turns the chemistry's Ia iron into a number of "
        "events. The named alternative is Weinberg, Andrews & Freudenburg 2017's 0.77 Msun (the W70 "
        "model of Iwamoto et al. 1999), the value their Ia iron yield of 0.0017 per unit mass "
        "formed was built with [verified: ApJ 837, 183, section II.2, arXiv:1604.07435, read at "
        "S30]; it would lower the rate by 9%.",
    ),
    # --- S30: the galactic habitable zone's criteria (ruling (b): built, deliberately unjudged).
    # Lineweaver, Fenner & Gibson 2004 (Science 303, 59) was the ruling's first source and could
    # not be read: its astro-ph preprint is a scanned image and no text mirror was found. Only its
    # abstract was read (a zone between 7 and 9 kpc, of stars formed 8 to 4 Gyr ago), so its
    # criteria enter nothing here. Every criterion below is Gowanlock, Patton & McConnell 2011,
    # Astrobiology 11, 855 (arXiv:1107.1286), the ruling's named alternative, read at S30 section
    # by section; the one quoted fragment is the equation.
    "PLANET_PROBABILITY_SOLAR": Constant(
        0.03,
        "dimensionless",
        "The probability that a star of solar metallicity forms a giant planet, the metallicity "
        "criterion's normalisation: Gowanlock et al. 2011 section 3.2 adopt Fischer & Valenti "
        "2005's P(planet) = 0.03 x 10^(2.0[Fe/H]) above solar metallicity and Santos et al. "
        "2004's flat tail, a constant 3% below it [verified: arXiv:1107.1286 section 3.2, read at "
        "S30]. They scale it to a habitable-planet probability by Ida & Lin 2005's ratios and "
        "remove a habitable planet whose star also has a hot Jupiter; neither the ratios nor the "
        "hot-Jupiter fraction was read, so the model publishes the giant-planet criterion itself "
        "and says its weight is relative.",
    ),
    "PLANET_METALLICITY_INDEX": Constant(
        2.0,
        "dimensionless",
        "The exponent of the same relation, P proportional to 10^(2.0[Fe/H]) above solar "
        "metallicity [verified: arXiv:1107.1286 section 3.2, citing Fischer & Valenti 2005, read "
        "at S30]. No upper metallicity cut is stated there.",
    ),
    "STERILIZATION_DISTANCE": Constant(
        8.0,
        "pc",
        "How close an average type II supernova must be to strip a planet's ozone, 8 pc after "
        "Gehrels et al. 2003; a brighter event reaches further by eq. 5, d_SN = 8 pc x "
        "10^(-0.4(M_SN - M_std)) [verified: arXiv:1107.1286 section 3.1.2, eq. 5, read twice at "
        "S30]. A third read described the distance as scaling with the square root of the flux "
        "ratio, which would make the exponent -0.2; the equation is used as read and the "
        "question is carried, not settled from recall (rule B9).",
    ),
    "STERILIZATION_MAGNITUDE": Constant(
        -17.505,
        "mag",
        "M_std of the sterilization distance: the absolute magnitude of the average SN II, taken "
        "as just enough to sterilize at 8 pc [verified: arXiv:1107.1286 section 3.1.2, read at "
        "S30]. The source draws each SN II from Richardson et al. 2002's magnitude distribution; "
        "the model uses the average, so a core collapse reaches 8 pc.",
    ),
    "IA_ABSOLUTE_MAGNITUDE": Constant(
        -19.34,
        "mag",
        "The mean peak magnitude of a type Ia supernova in the sterilization distance: Wang et al. "
        "2006's mean M_B over 109 events, which the source draws its Ia magnitudes from "
        "[verified: arXiv:1107.1286 section 3.1, read at S30]. At the mean and by eq. 5 as read a "
        "type Ia sterilizes out to 5.4 times a type II's distance; the source, drawing both from "
        "their distributions, calls an Ia about 5.6-5.7 times more lethal. No dispersion is "
        "stated there.",
    ),
    "COMPLEX_LIFE_DELAY": Constant(
        4.0,
        "Gyr",
        "How long after its planet forms complex life arises: the source assumes animal life "
        "about 4 Gyr after formation, from the Earth's age of about 4.55 Gyr [verified: "
        "arXiv:1107.1286 section 3.4.1, read at S30]. A star formed less than this long ago "
        "carries no weight in the habitable zone.",
    ),
    "OZONE_CONTINUITY": Constant(
        1.55,
        "Gyr",
        "How long a planet's ozone must survive unbroken by a sterilizing supernova for complex "
        "life to arise: 1.55 Gyr before the rise of animal life [verified: arXiv:1107.1286 "
        "section 3.4, read at S30]. The source restarts the clock after a sterilization (read in "
        "paraphrase, one pass), so a planet can become habitable later; the model counts only the "
        "last 1.55 Gyr before the 4 Gyr rise, the first chance and a lower bound on the source's "
        "criterion [inferred].",
    ),
    # --- S31 (BUILD_II Phase 7): dust that radiates. Ruling (a): one grain model, the Milky Way
    # R_V = 3.1 carbonaceous-silicate model of Weingartner & Draine 2001 renormalised by Draine 2003,
    # read row by row from Draine's own tabulation of it, kext_albedo_WD_MW_3.1_60_D03.all
    # (https://www.astro.princeton.edu/~draine/dust/extcurvs/, calculated 2009), by a read-only agent
    # and again directly at S31; the agent's first pass misread four rows (it took 1.65 um for 0.165)
    # and the rows below are the file's as printed. Its header: M_dust per H nucleon 1.398E-26 g,
    # M_gas/M_dust 165.3 (He/H = 0.096). Every other R_V (the same model's 4.0 and 5.5 tables for
    # dense clouds; Fitzpatrick 1999's law) is the named alternative, never an average (B12).
    "DUST_R_V": Constant(
        3.1,
        "dimensionless",
        "The ratio of total to selective extinction, A_V / E(B-V): the grain model's, whose table is "
        "headed 'Carbonaceous - Silicate Model for Interstellar Dust with R_V=3.1', the value Draine "
        "2003 (ARA&A 41, 241) takes for 'the average extinction law for diffuse regions in the local "
        "Milky Way' [verified: Draine's table header and astro-ph/0304489, read at S31]. Dense clouds "
        "run to 5.5; the same model's R_V = 4.0 and 5.5 tables are the named alternatives.",
    ),
    "DUST_ALBEDO_V": Constant(
        0.6774,
        "dimensionless",
        "Scattering over extinction cross-section in V: the table's 'V filter' row, lambda = 0.547 um, "
        "albedo 0.6774 [verified: kext_albedo_WD_MW_3.1_60_D03.all, the V filter row, read at S31]. "
        "Two thirds of the V light dust removes from a ray is scattered, one third absorbed. "
        "BUILD_II's recalled 0.5-0.6 was low.",
    ),
    "DUST_SCATTERING_G": Constant(
        0.5383,
        "dimensionless",
        "The scattering asymmetry g = <cos theta> in V, the same row's <cos> column, 0.5383 "
        "[verified: kext_albedo_WD_MW_3.1_60_D03.all, the V filter row, read at S31]: forward-throwing. "
        "BUILD_II's recalled ~0.6 was high.",
    ),
    "DUST_EXTINCTION_RATIO_FUV": Constant(
        1.193e-21 / 4.868e-22,
        "dimensionless",
        "A_FUV / A_V = 2.451: the extinction cross-section per H at lambda = 0.151356 um, 1.193E-21 "
        "cm^2/H, over the V filter row's 4.868E-22 [verified: kext_albedo_WD_MW_3.1_60_D03.all, both "
        "rows, read at S31]. 0.151356 um is the table's point nearest 1528 A, where the far-ultraviolet "
        "calibration's nu L_nu is read [verified: Hao et al. 2011, ApJ 741, 124, arXiv:1108.2837, "
        "Kennicutt & Evans's FUV reference, read at S31]; the next point, 0.154882 um, gives 2.406.",
    ),
    "DUST_ALBEDO_FUV": Constant(
        0.4068,
        "dimensionless",
        "The albedo at the same far-ultraviolet point, lambda = 0.151356 um: 0.4068 [verified: "
        "kext_albedo_WD_MW_3.1_60_D03.all, read at S31]. Ultraviolet is absorbed, not scattered, in "
        "the larger share, unlike V.",
    ),
    "DUST_OPACITY_REFERENCE": Constant(
        16.43,
        "cm2/g",
        "Absorption cross-section per gram of dust at the far-infrared reference wavelength: K_abs = "
        "1.643E+01 cm^2/g on the table's 'MIPS 3' row, lambda = 155.9 um [verified: "
        "kext_albedo_WD_MW_3.1_60_D03.all, read at S31]. Chosen at 156 um because a 15-25 K modified "
        "blackbody's power peaks near there, so the emissivity index moves the temperature least; the "
        "same table gives 40.95 at 100 um and 6.412 at 245.5 um (a local slope of 2.07 between them). "
        "Per unit dust mass on the same total-gas basis as the dust-to-gas ratio: the table's "
        "M_gas/M_dust is 165.3 against the 162 the ISM stage adopts.",
    ),
    "DUST_OPACITY_WAVELENGTH": Constant(
        155.9,
        "um",
        "The wavelength the far-infrared opacity is quoted at: the table's 'MIPS 3' row, 1.55900E+02 um "
        "[verified: kext_albedo_WD_MW_3.1_60_D03.all, read at S31].",
    ),
    "DUST_EMISSIVITY_INDEX": Constant(
        1.62,
        "dimensionless",
        "beta of the modified blackbody, kappa_nu proportional to nu^beta: Planck's whole-sky mean "
        "<beta_obs> = 1.62, standard deviation 0.10, fitted with <T_obs> = 19.7 K (sigma 1.4 K) "
        "[verified: Planck Collaboration 2014, A&A 571, A11 ('Planck 2013 results. XI'), Table 3, "
        "arXiv:1312.1300, read at S31]; 1.59 +/- 0.12 above |b| = 15 deg. The named alternative is "
        "beta = 2, graphite's in Draine & Li 2007 (which the same Planck paper contrasts with its "
        "lower mean) and near the grain model's own 100-250 um slope of 2.07.",
    ),
    "FUV_LUMINOSITY_PER_SFR": Constant(
        10.0**43.35 / 3.828e33,
        "Lsun",
        "Far-ultraviolet nu L_nu, in Lsun, per Msun/yr of star formation: Kennicutt & Evans 2012's "
        "log SFR = log L_x - log C_x with log C_x = 43.35 for FUV, L_x in erg/s as nu L_nu, ages "
        "0-10-100 Myr, for a Kroupa & Weidner 2003 IMF (Salpeter 1-100 Msun, -1.3 below) [verified: "
        "arXiv:1204.3552, Table 1 and eq. 12, read at S31], nu L_nu at 1528 A [verified: Hao et al. "
        "2011, arXiv:1108.2837, read at S31], over Lsun = 3.828e33 erg/s. The same table "
        "gives the H-alpha constant's 41.27. 5.85e9 Lsun per Msun/yr.",
    ),
    "HABING_FLUX": Constant(
        1.6e-3,
        "erg/cm2/s",
        "Habing's 1968 estimate of the interstellar far-ultraviolet flux between 6 and 13.6 eV, the "
        "unit G0 = 1: 'G0 is in units of the \"Habing Field\", 1.6 x 10^-3 erg cm^-2 s^-1' [verified: "
        "Kaufman, Wolfire, Hollenbach & Luhman 1999, ApJ 527, 795, astro-ph/9907255, read at S31]. "
        "The local field measured by Draine 1978 is 4 pi J = 2.7 x 10^-3, 'a factor of 1.7 higher than "
        "the integrated field of Habing 1968' [verified: Wolfire et al. 2003, ApJ 587, 278, "
        "astro-ph/0207098, read at S31]: G0 = 1.7 at the Sun is the comparison, not a target.",
    ),
    # --- S31 ruling (c): the PAH fraction's metallicity dependence enters because a source for it was
    # read - Remy-Ruyer et al. 2015, A&A 582, A121 (arXiv:1507.05432), section 4.3, eq. 5, its
    # normalisation, abundance scale and sample read by the agent and again directly at S31. The
    # named alternative is a constant: Draine & Li 2007's Milky Way q_PAH = 4.58% (model MW3.1_60,
    # the grain model the dust constants above are read from) [verified: astro-ph/0608003, its model
    # tables, read at S31]. Draine et al. 2007 (ApJ 663, 866) measured the same trend in two bins,
    # 'The nine galaxies in our sample with A_O<8.1 have a median q_PAH=1.0%, whereas galaxies with
    # A_O>8.1 have a median q_PAH=3.55%' [verified: astro-ph/0703213, abstract, read at S31], on the
    # same Pilyugin & Thuan 2005 abundance scale; a relation is preferred to a step.
    "PAH_FRACTION_GALACTIC": Constant(
        0.0457,
        "dimensionless",
        "The Galactic PAH mass fraction the relation's f_PAH is normalised to: 'The Galactic PAH mass "
        "fraction is f_PAH,sun = 4.57% from Zubko et al. 2004' [verified: Remy-Ruyer et al. 2015, "
        "arXiv:1507.05432, section 3 footnote 13, read at S31]. Draine & Li 2007's Milky Way model has "
        "4.58%, the named alternative's constant.",
    ),
    "PAH_METALLICITY_INTERCEPT": Constant(
        -11.0,
        "dimensionless",
        "log(f_PAH) = (-11.0 +/- 0.3) + (1.30 +/- 0.04) x (12 + log(O/H)), 'with a dispersion of 0.35 "
        "dex around the relation with metallicity' [verified: Remy-Ruyer et al. 2015, arXiv:1507.05432, "
        "section 4.3, eq. 5, read at S31]: the intercept. Fitted across 109 galaxies (their dwarf and "
        "KINGFISH samples), not along any one galaxy's radius; the same section's sSFR relation, and "
        "their remark that the PAH fraction is 'primarily driven by the sSFR, with a second order effect "
        "from metallicity', are recorded, not used.",
    ),
    "PAH_METALLICITY_SLOPE": Constant(
        1.30,
        "dimensionless",
        "The same relation's slope, 1.30 +/- 0.04 per dex of 12 + log(O/H) [verified: arXiv:1507.05432, "
        "section 4.3, eq. 5, read at S31].",
    ),
    "OXYGEN_ABUNDANCE_SOLAR": Constant(
        8.69,
        "dex",
        "12 + log(O/H) of the Sun on the relation's own scale: 'Throughout the paper, we assume "
        "(O/H)sun = 4.90 x 10^-4, i.e., 12+log(O/H)sun = 8.69 (Asplund et al. 2009)', their abundances "
        "being Pilyugin & Thuan 2005's strong-line calibration [verified: arXiv:1507.05432, section 2, "
        "read at S31]. It places the gas's [Fe/H], oxygen taken to track iron as the ISM stage takes it, "
        "on the relation's absolute scale.",
    ),
    "PAH_METALLICITY_MAX": Constant(
        1.20,
        "dimensionless",
        "The most metal-rich galaxy the relation was fitted to, in Z/Z_sun: 'The metallicities in the "
        "KINGFISH sample range from Z ~ 0.07 Z_sun to 1.20 Z_sun' [verified: arXiv:1507.05432, section "
        "2, read at S31]. The relation is not extrapolated above it: the inner disc's gas reaches five "
        "times solar, where eq. 5 would give three quarters of the dust mass in PAHs.",
    ),
}
