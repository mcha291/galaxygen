# AUDIT_III — Session 37: the second build's own audit (BUILD_II, S25–S36)

Once, on Fable, after the build, as the project does (S10's two runs, S21's aim (a)); ruled in by the
reconciliation because B3 says the phases' own gates are checks on the phases. **Nothing here changes a
number in the model** (B3): a finding that would is a debt or a ruling for the owner, with the sentence that
decides it. Decision D186 records the aim, the method and the counts.

## 0. The aim, stated before any file was opened (D113), and how it read

1. Every constant that entered code S25–S36 with a citation (63 in `level0.py`, found by their "read at S2x/S3x"
   tags) and every module-level table (Case B, the two O-star tables, the wind coefficients, the IFMR, Weaver's
   and Sedov's coefficients, Draine's table) and rows 32–36's targets **re-read against the sentence the constant
   quotes**, by a read-only agent that did not write them (`scratchpad/audit3_reread.md`, 170 lines), each
   labelled MATCH / DIFFERS / ADOPTED-NOT-MEASURED / MISATTRIBUTED / UNREACHABLE. A DIFFERS is a finding; an
   adopted value presented as a measurement is the class S21's A-14 caught ("cited 35", measured 39 ± 4).
2. Every redistribution and balance the build asserted **re-derived at a mesh the build did not use**
   (`GridSpec(n_R=180, n_t=600, n_z=8)`), beside the default mesh's number (`tests/test_audit_iii.py`).
3. Every green row the build added (29, 30, 31, 35) **conditioned** (AUDIT_RUN2 §5): what makes it green, and does
   it survive the alternative named in its constant's about line (`scratchpad/audit3_greens.py`).
4. The two rows whose windows were chosen with the model's number known (32, #98; 34, #100) **re-read blind** by an
   agent forbidden the repository (`scratchpad/audit3_blind.md`).
5. The register's items #80–#103 **re-stated in one line each**: still-open / closable-now / wrongly-described.

Sources were read from primary text wherever it exists (arXiv LaTeX streamed, the CDS VI/64 FTP mirror, Draine's
table file, the Harris catalogue, the ADS scan page images for Weaver et al. 1977 and Kennicutt, Edgar & Hodge
1989); section and equation numbers were counted from the LaTeX where an about line cites one. The agents'
reports are quoted below as they were written; the verdicts are theirs, the findings (§6) are the session's.

## 1. The sources re-read (the agent's report, verbatim)

"MATCH" means the sentence was found where cited and the code value equals the source's (or its stated midpoint or
derivation, recomputed).

### 1.1 Star formation calibrations, photometry

| constant | code value | source value and sentence read | location | verdict |
|---|---|---|---|---|
| HALPHA_PER_SFR | 4.86e7 Lsun | Table 1: "H$\alpha$ & 0-3-10 & ergs s-1 & 41.27"; "\log SFR (Msun/yr) = \log L_x - \log C_x". 10^41.27 / 3.828e33 = **4.8644e7**; code is 4.86e7 (-0.09%). The equation is not in section 3.1 (3.1 is "Star Counting and CMD Analysis"); it is in section 3.8 "An Updated Compendium of Integrated SFR Calibrations", eq. 12. | KE12 arXiv:1204.3552, Table 1, sec. 3.8 eq. 12 | DIFFERS (rounded; section also misattributed) |
| FUV_LUMINOSITY_PER_SFR | 5848278836.385441 Lsun | Table 1 FUV "43.35", nu L_nu; 10^43.35/3.828e33 = 5848278836.385441 exactly. Eq. 12 confirmed by counting (3 in definitions + 4 gastracers + 2 resolvedstars + 2 composite + 1). IMF "Salpeter slope from 1-100 Msun and -1.3 for 0.1-1 Msun" (Kroupa & Weidner 2003, 2003ApJ...598.1076K). Hao et al. 2011: "monochromatic luminosity L(FUV)_obs = nu L_nu(1528 A)". | KE12 Table 1, eq. 12; Hao+11 arXiv:1108.2837 | MATCH |
| SOLAR_ABSOLUTE_MAGNITUDE_V | 4.81 mag | "Johnson\_V & 4.81 & 4.80 & 4.81 ..." in Table "Magnitudes of the Sun" (third table in the paper). | Willmer 2018 arXiv:1804.07788, Table 3 | MATCH |

### 1.2 Molecular clouds (S32)

| constant | code value | source value and sentence read | location | verdict |
|---|---|---|---|---|
| GMC_MASS_SLOPE_INNER | -1.6 | "it is best described by a truncating power law with power index gamma=-1.6+/-0.1 and truncation mass M_0 = (1.0 +/- 0.2) x 10^7 Msun" (inner Galaxy); same in the Cloud Mass Functions subsection. Alternative: Rosolowsky 2005 Table 1 "Inner MW & SRBY & VT & 190 & -1.53 +/- 0.07 & ... & 29. +/- 5.0" (M_0/1e5), eqs. 3-4 the truncated form, confirmed. | Rice+16 arXiv:1602.02791 sec. IV.4, abstract/conclusions | MATCH |
| GMC_SURFACE_DENSITY | 42 Msun/pc2 | "The corresponding median mass surface density of molecular hydrogen for this sample is 42 Msun/pc^2, which is significantly lower than the value derived by SRBY (median 206 Msun/pc^2)". Alternatives confirmed: Roman-Duval 2010 "median of 144 Msun pc-2", "M = (228+/-18) R^{2.36+/-0.04}". Note: 206 is Heyer's rescaling of Solomon's original 170 (R0 10 -> 8.5 kpc), and the 42 is H2 mass (the abstract also warns Sigma "could be larger" owing to envelope abundances). | Heyer+09 arXiv:0809.1397 abstract | MATCH |
| MOLECULAR_GAS_TEMPERATURE | 10 K | Sec. 1: dark clouds "have gas temperatures ~10-20 K"; 3.2.2: NH3 "gas temperatures of about 10 K"; 2.5: "sound speed is 0.2 km s-1 for 10 K gas"; Table 1 clouds "approx 10". Same intro: GMCs "contain embedded massive stars that heat the surrounding gas to temperatures > 20 K". | Bergin & Tafalla 2007 arXiv:0705.3765 | MATCH |
| TURBULENCE_FORCING_B | 0.4 | FKS08 eq. 4 "sigma_s=[ln(1+b^2 M^2)]^{1/2}"; Table 1 sol "0.36+/-0.03", comp "1.05+/-0.19". F10 sec. 3.6: "For zeta >~ 0.5 the b-parameter remains close to the value obtained for purely solenoidal forcing, i.e. b approx 0.3-0.4 in 3D"; eq. 19 confirmed (ar5iv numbering). 0.4 is the upper end of 0.3-0.4. | FKS08 arXiv:0808.0605; Federrath+10 arXiv:0905.1060 | MATCH |
| GMC_PHASE_EMBEDDED | 6 Myr | "By adopting the time scale of the youngest stellar clusters, 10 Myrs, we roughly estimate the timescales of Types I, II and III to be 6 Myrs, 13 Myrs and 7 Myrs ... lifetime of 20--30 Myrs". The count ratios are measured; the absolute clock is the adopted 10 Myr cluster age. Alternatives confirmed: Murray 2011 "17 plus or minus 4 Myr"; Chevance+20 "typically 10-30 Myr" (which also reports "a long inert phase without massive star formation traced by Halpha (75-90% of the cloud lifetime)", a very different embedded share from Kawamura's 6/26). | Kawamura+09 arXiv:0908.1168 abstract, sec. 4.2, Table 3 | MATCH |

### 1.3 Clusters, globular clusters, stellar halo (S33-S34)

| constant | code value | source value and sentence read | location | verdict |
|---|---|---|---|---|
| CLUSTER_BOUND_FRACTION | 0.07 | Abstract "Less than 4-7% of embedded clusters survive emergence ... Pleiades age"; 2.5 "only about 7% of all embedded clusters survive to Pleiades age. It is likely that only the most massive clusters in our catalog are candidates for long term survival. Roughly 7% ... in excess of 500 Msun". | Lada & Lada 2003 astro-ph/0301540 | MATCH |
| CLUSTER_DISSOLUTION_AGE | 10 Myr | 2.5 "do not survive ... for periods even as long as 10 Myr ... less than 10% survive longer than 10 Myr. Indeed, most clusters may dissolve well before they reach an age of 10 Myr". | same, sec. 2.5 | MATCH |
| CLUSTER_HALF_MASS_DENSITY | 1000 Msun/pc3 | 4.4.2: "For young clusters (<~10 Myr) there seems to be some positive correlation between mass and radius, roughly consistent with a density of 10^{3+/-1} Msun pc^-3"; Fig. 9 caption (9th figure, counted) "rho_hm = 3M/(8 pi r_hm^3)". Sec. 2.3 calls the same trend "tentatively" overplotted. Larsen 2004 sec. 6.3 alternative "revised to 4+/-1 pc (Whitmore et al. 1999)" confirmed. | PZMG10 arXiv:1002.1961 | MATCH |
| CLUSTER_MASS_FUNCTION_INDEX | 2.0 | 2.4.2: "is well represented by a Schechter (1976) distribution phi(M) = dN/dM = A M^-beta exp(-M/M*). Here beta simeq 2". | PZMG10 sec. 2.4.2 | MATCH |
| GC_HALO_MASS_RATIO | 3.5e-5 | "with eta=(3-4) x 10^-5 (hudson2014, harris2015, harris2017 ...)", listed under "I will assume the following". The **measurement behind it**, Harris, Blakeslee & Harris 2017 (arXiv:1701.04845): "The new calibration of the mean mass ratio eta_M = (2.9 +/- 0.2) x 10^-5 is significantly lower than in previous papers". 3.5e-5 sits 3 sigma above it. **arXiv id wrong**: the sentences are in Boylan-Kolchin 2017, MNRAS 472, 3120 = arXiv:1705.01548; arXiv:1711.00009 is Boylan-Kolchin's "Globular clusters and high-z luminosity functions" paper, which contains none of them. | BK17 arXiv:1705.01548 sec. 2 (iii) | ADOPTED (and id misattributed) |
| GC_METAL_POOR_HALO_MASS_RATIO | 2.25e-5 | "with eta_b approx (2-2.5) x 10^-5 (harris2015, harris2017)", same assumption list. Midpoint recomputed 2.25e-5; share 0.643; range 0.50-0.83 correct. The blue-GC ratio was not located in Harris 2015 (arXiv:1504.03199), whose global value is <log eta> = -4.47 +/- 0.07. | BK17 sec. 2 (iv) | ADOPTED (and id misattributed) |
| GC_SYSTEM_SCATTER | 0.28 dex | BK17 5.1: "Observationally, the scatter in the mass in globular clusters at fixed halo mass is approximately constant with sigma <~ 0.28 dex". Its origin, Harris+17: "<eta_M> = 2.9x10^-5, with a residual rms scatter +/- 0.28 dex" (an rms, not a bound). | BK17 arXiv:1705.01548 sec. 5.1 (not 1711.00009) | MISATTR (arXiv id) |
| GC_MEAN_MASS | 2.5e5 Msun | "I will assume <m(z=0)>=2.5x10^5 Msun (see harris2017)". Harris+17 gives mean GC masses that vary with host (e.g. "<M_GC> simeq 2.6 x 10^5", "2.8 x 10^5", "1.0 x 10^5", "2.3 x 10^5"). | BK17 sec. 2 (i) | ADOPTED (and id misattributed) |
| CLUSTER_DISRUPTION_T0 | 3.3 Myr | Table 5 bottom line "adopted & 3.3^{+1.4}_{-1.0}"; text 6.3: "we conclude that t0=3.3^{+1.5}_{-1.0} Myr" (text and table disagree on the upper error, +1.5 vs +1.4); "implies a total disruption time of a 10^4 Msun cluster of 1.3 +/- 0.5 Gyr"; abstract "a factor 5 shorter than derived from N-body simulations". A fit to the Kharchenko sample; "adopted" there is the combination of the Mmin=80 and 100 fits. | Lamers+05 astro-ph/0505558 sec. 6.3, Table | MATCH |
| CLUSTER_DISRUPTION_INDEX | 0.62 | Sec. 2: "with gamma simeq 0.6 for clusters in very different local environments"; eq. 1 "t_dis = t_0 (M_i/Msun)^{0.62}"; eq. 6 (6th equation) mu = {(mu_ev)^gamma - gamma t/t0 (Msun/M_i)^gamma}^{1/gamma}. | Lamers+05 sec. 2, eqs. 1, 6 | MATCH |
| CLUSTER_MASS_MIN | 100 Msun | Sec. 5: "Suppose that the CIMF is a power law with a slope -alpha=-2 ... in the range of Mmin < M_cl < Mmax, Mmin approx 10^2 Msun and Mmax approx 10^7 Msun". Sec. 6.2 estimates the Kharchenko sample's lower limit and fits at 80 and 100. | Lamers+05 sec. 5 | ADOPTED (disclosed) |
| STELLAR_HALO_INNER_SLOPE | -2.5 | "The inner power-law slope is encompassed by alpha_in = -2.5 +/- 0.3" (Halo = sec. 6, Stellar halo 6.1, 6.1.1). | BHG16 arXiv:1602.07702 | MATCH |

### 1.4 Supernovae and habitability (S30)

| constant | code value | source value and sentence read | location | verdict |
|---|---|---|---|---|
| CORE_COLLAPSE_MIN_MASS | 8.5 Msun | 4.4: "They find that the minimum stellar mass for a type II-P to form is m_min=8.5^{+1}_{-1.5} Msun" (the max-likelihood fit of Smartt et al. 2009 MNRAS, quoted in the review); 8.1 repeats it as "an observational estimate". Alternative: Heger+03 sec. III "it is assumed that stars below ~9 Msun ... end their lives as white dwarfs" and sec. IV.1 "Estimates range from 6 to 11 Msun" (the 9 is in sec. III, not IV.1). | Smartt 2009 arXiv:0908.0700 | MATCH |
| IA_IRON_MASS | 0.7 Msun | "The mean iron yield of a SN Ia ... is (e.g., Mazzali 2007, Howell 2009) y_Fe,Ia = 0.7 Msun, (eq. 2) as already assumed in Graur2011." Alternative Weinberg+17 "K_Fe,Ia = 0.77 Msun (based on the W70 model)", "m_Fe,Ia = 0.0017" confirmed. | Maoz & Graur 2017 arXiv:1703.04540 sec. 3 eq. 2 | ADOPTED (disclosed) |
| PLANET_PROBABILITY_SOLAR | 0.03 | 3.2.2: "Fischer & Valenti find that the probability of forming a gas giant planet is P(planet)=0.03x10^{2.0[Fe/H]}"; Santos+04 "constant (3%) at sub-solar metallicities". | Gowanlock+11 arXiv:1107.1286 | MATCH |
| PLANET_METALLICITY_INDEX | 2.0 | same equation. | same | MATCH |
| STERILIZATION_DISTANCE | 8 pc | "at a distance of <8 pc, a SNII will deplete the ozone" (Gehrels 2003, adopted: "We assume that the sterilization distance ... refers to an average SNII"). **Eq. 5 as printed: d_SN = 8 pc x sqrt(10^{-0.4(M_SN - M_std)})**, i.e. exponent -0.2. The about line and `habitable_zone.sterilization_distance` use 10^{-0.4(M - M_std)} with no square root. The "third read" was right. | Gowanlock+11 sec. 3.1.2, eq. 5 (5th equation, counted) | DIFFERS (formula) |
| STERILIZATION_MAGNITUDE | -17.505 mag | "M_std=-17.505, which is the absolute magnitude of the average SNII that we assume is just sufficient to sterilize life within 8 pc". | same | MATCH |
| IA_ABSOLUTE_MAGNITUDE | -19.34 mag | "based on 109 SNIa with a mean M_B of -19.34". "~5.7x" (Model 1) and "roughly 5.6x" (Model 4) more lethal confirmed. Consequence of the eq. 5 error: at the mean the Ia/II distance ratio is 2.33 by the printed equation, not 5.42, so the model's Ia sterilization volume is 12.6x too large. | same | MATCH (value; see DIFFERS above) |
| COMPLEX_LIFE_DELAY | 4.0 Gyr | 3.4.1: "Given that the age of the Earth is ~4.55 Gyr, we assume that the rise of animal life occurred ~4 Gyr after the planet's formation" (fossils ~600 Mya, molecular clock ~1 Gya). | same, sec. 3.4.1 | ADOPTED (disclosed) |
| OZONE_CONTINUITY | 1.55 Gyr | "Therefore, 1.55 Gyr of continuous ozone is required"; clock restarts: "we assume that the planet does not develop animal life until 1.55 Gyr of time elapses without interruption"; 3.4.2 draws ozone rebuild U[0.4, 2.25] Gyr plus animal re-evolution U[0, 1.55] Gyr. Footnote: "The ozone layer forms at 2.45 Gyr" -> 4.0-2.45 = 1.55. Internal inconsistency in the source: its "~2.3 Gya" gives 4.55-2.3 = 2.25 Gyr and would make it 1.75. | same, sec. 3.4.1 | ADOPTED |

### 1.5 Dust (S31)

| constant | code value | source value and sentence read | location | verdict |
|---|---|---|---|---|
| DUST_R_V | 3.1 | Header "Carbonaceous - Silicate Model for Interstellar Dust with R_V=3.1"; Draine 2003: "R_V approx 3.1 for the ``average'' extinction law for diffuse regions in the local Milky Way". | kext_albedo_WD_MW_3.1_60_D03.all; astro-ph/0304489 | MATCH |
| DUST_ALBEDO_V | 0.6774 | "5.47000E-01 0.6774 0.5383 4.868E-22 1.123E+04 0.53230 V filter" | same file | MATCH |
| DUST_SCATTERING_G | 0.5383 | same row, <cos> | same | MATCH |
| DUST_EXTINCTION_RATIO_FUV | 2.450698438783895 | "1.51356E-01 0.4068 0.6633 1.193E-21 ..."; 1.193e-21/4.868e-22 = 2.450698438783895 (exact); next point 1.54882E-01 gives 1.171e-21 -> 2.406; 0.151356 um is the grid point nearest 1528 A. | same | MATCH |
| DUST_ALBEDO_FUV | 0.4068 | same row | same | MATCH |
| DUST_OPACITY_REFERENCE | 16.43 cm2/g | "1.55900E+02 0.0000 -0.0005 2.298E-25 1.643E+01 0.40000 MIPS 3"; 100 um 4.095E+01, 245.471 um 6.412E+00, local slope 2.065; "1.653E+02 = M_gas/M_dust". | same | MATCH |
| DUST_OPACITY_WAVELENGTH | 155.9 um | same row | same | MATCH |
| DUST_EMISSIVITY_INDEX | 1.62 | Table 3 (tab:summary, 3rd table) "Whole sky & 100 & 19.7 & 1.4 & 1.62 & 0.10"; "|b| > 15 & 50 & 20.3 & 1.3 & 1.59 & 0.12". | Planck 2013 XI arXiv:1312.1300 | MATCH |
| HABING_FLUX | 1.6e-3 erg/cm2/s | Kaufman+99: "G_0 is in units of the ``Habing Field'', 1.6x10^-3 erg cm^-2 s^-1"; Wolfire+03: "4 pi J(R_0) = 2.7x10^-3 ... a factor of 1.7 higher than the integrated field of Habing 1968". | astro-ph/9907255; astro-ph/0207098 | MATCH |
| PAH_FRACTION_GALACTIC | 0.0457 | Footnote (sec. 3.2): "The Galactic PAH mass fraction is fpah_sun=4.57% from Zubko2004". | Remy-Ruyer+15 arXiv:1507.05432 | MATCH |
| PAH_METALLICITY_INTERCEPT | -11.0 | Eq. 5 (5th equation): "log(f_PAH) = (-11.0 +/- 0.3) + (1.30 +/- 0.04) x (12+log(O/H))", "with a dispersion of 0.35 dex around the relation with metallicity" (sec. 4.3). The "primarily driven by the sSFR, with a second order effect from metallicity" remark is in the concluding section, not 4.3. | same | MATCH |
| PAH_METALLICITY_SLOPE | 1.30 | same | same | MATCH |
| OXYGEN_ABUNDANCE_SOLAR | 8.69 | The sentence is a footnote in **sec. 1 (Introduction)**, not sec. 2, and prints "(O/H)_sun= 4.90x10^4" (typo for 10^-4). The Pilyugin & Thuan 2005 sentence is in sec. 2.1. Value confirmed at source: Asplund+09 "log epsilon_O = 8.69 +/- 0.05". | RR15 sec. 1 fn.; Asplund arXiv:0909.0948 | MISATTR (section) |
| PAH_METALLICITY_MAX | 1.2 | "The metallicities in the KINGFISH sample range from Z ~ 0.07 Zsun to 1.20 Zsun." | RR15 sec. 2.1 | MATCH |

### 1.6 Nebular (S35)

| constant | code value | source value and sentence read | location | verdict |
|---|---|---|---|---|
| HII_ESCAPE_FRACTION | 0.3 | IV.B: "In this model 30% of emitted Lyman continuum photons escape from each HII region, and propagate through the DIG isotropically"; "the result is remarkably similar globally". **The "between 30% and 60%" is not Zurita's variants**: it is in IV.C "Line ratio studies", about Hoopes & Walterbos 2003's modified spectra ("varying the modeled escape fraction between 30% and 60%, where a lower escape fraction implies a harder spectrum"). Oey+07 "The mean fraction f_WIM ... is 0.59+/-0.19" (109 galaxies) and "about 1/8th" confirmed. | Haffner+09 arXiv:0901.0941 | MISATTR (the 30-60% range) |
| DIG_TEMPERATURE | 8000 K | "Temperatures range from about 6000 K to 10 000 K" - in **sec. II.A** ("Basic characteristics of the WIM"), not sec. I. Midpoint 8000 recomputed. | Haffner+09 sec. II.A | MISATTR (section) |
| DIG_SCALE_HEIGHT | 1.4 kpc | "The large, 1000--1800 pc scale height, significantly larger than that of the neutral hydrogen layer" - sec. II.A, not I. Midpoint 1400 pc. | same | MISATTR (section) |
| HII_LF_MIN_LUMINOSITY | 1e37 (erg/s) | Scan p. 768, sec. III.b: "10^37 ergs s-1 in the LMC and M31, the LFs become significantly flatter; this may partly reflect incompleteness, but a turnover is expected near the transition between HII regions ionized by single stars and small associations"; "power laws provide good fits to the LFs (over the range where the data are complete)". Unit in the constants file is printed "[dimensionless]"; it is erg/s. | KEH89 ApJ 337, 761, ADS scan pp. 767-768 | MATCH (unit label wrong) |
| TE_METALLICITY_INTERCEPT | 9.29 | Eq. 5 (5th equation, counted): "12 + log(O/H)_{t^2=0} = (9.29 +/- 0.02) - (0.96 +/- 0.02) x (T_e(H+)/10^4 K)"; eq. 6 "(9.46 +/- 0.05) - (0.97 +/- 0.05)"; 225 regions, 460 radio regions. | arXiv:2601.13337 | MATCH |
| TE_METALLICITY_SLOPE | 0.96 | same | same | MATCH |
| TE_VALID_MIN | 6000 K | "valid over a T_e(H+) range between approximately 6000 K to 20000 K ... only one object in our sample lies beyond T_e ~ 16,000 K". | same | MATCH |
| TE_VALID_MAX | 20000 K | same | same | MATCH |
| NO_PRIMARY_LOG | -1.732 | Eq. 3 (3rd equation): "log(X/O) = log[10^a + 10^{[log(O/H)+b]}]" ... "for nitrogen a = -1.732, b = 2.19"; "a starting point for modelling, rather than being prescriptive"; stellar data 12+log(O/H) ~6.0-9.0. log N/O at 8.76 recomputed -0.968. | Nicholls+17 arXiv:1612.03546 | MATCH |
| NO_SECONDARY_LOG | 2.19 | same | same | MATCH |
| NITROGEN_ABUNDANCE_SOLAR | 7.83 | "log epsilon_N = 7.83 +/- 0.05"; Table 1 "N 7.83 +/- 0.05". | Asplund+09 | MATCH |
| SULPHUR_ABUNDANCE_SOLAR | 7.12 | "log epsilon_S = 7.12 +/- 0.03". | Asplund+09 | MATCH |

### 1.7 Bubbles and remnants (S36)

| constant | code value | source value and sentence read | location | verdict |
|---|---|---|---|---|
| SUPERNOVA_ENERGY_51 | 1.0 | KO15 sec. 3: "For our standard models, we fix the total energy of a single SN to be E_SN=10^51 erg"; sec. 1 "kinetic energy of ~10^51 erg"; Chen & Slane 3.4.1 "somewhat lower than the canonical value of 10^51 ergs" (their own fits give 1.3-3.4e50); Sarbadhicary 2.1.3 "log-normal distribution centered on 10^51 ergs". No source measures it. | arXiv:1410.1537; astro-ph/0108502; arXiv:1605.04923 | ADOPTED |
| SEDOV_XI | 1.15167 | "A detailed solution gives xi_0 = 1.15167 at the shock radius, when the specific heat ratio is gamma=5/3"; Reynolds 2.2 "R_s = 1.15 (E/rho)^{1/5} t^{2/5} ... presume a ratio of specific heats of 5/3". | KO15 sec. 2; arXiv:1708.05386 sec. 2.2 | MATCH |
| PDS_TIME_COEFFICIENT | 13300 yr | "t_PDS = 1.33x10^4 E51^{3/14} n0^{-4/7} zeta_m^{-5/14} yr" (after eq. 5, "(Cioffi et al. 1988)"); Leahy & Williams 3.1.2 "t_sf=3.61x10^4 ... we define t_PDS=t_sf/e" = 13280 yr. Telezhinsky eq. 1 "t_tr = 2.9x10^4 E51^{4/17} n_ISM^{-9/17} yr" confirmed. Cioffi 1988 itself not read (secondary quotes agree). | Chen & Slane 2001 sec. 3.4.2 | MATCH |
| PDS_RADIUS_COEFFICIENT | 14.0 pc | Eq. 3: "r_PDS=14.0 E51^{2/7} n0^{-3/7} zeta_m^{-1/7} pc, where zeta_m is the metallicity factor and is close to unity"; eq. 4 "r_s = r_PDS (4t/(3t_PDS) - 1/3)^{3/10}". Martizzi+15 2.1 "(Z/Zsun)^{-1/7}" confirmed. Sedov radius at t_PDS recomputed 14.036 pc (mu = 1.4). | same, eqs. 3-4 | MATCH |
| PDS_VELOCITY_COEFFICIENT | 413 km/s | Eq. 5 "v_s = v_PDS (...)^{-7/10}", "v_PDS = 413 n0^{1/7} zeta_m^{3/14} E51^{1/14} km s-1". | same, eq. 5 | MATCH |
| REMNANT_VISIBLE_LIFETIME | 6e4 yr | Sec. 4.1: "it follows that the mean lifetime of radio supernova remnants is > 60,000 years and not 20,000 years as Braun et al. (1989) concluded"; "Thus we can assume E51 ~ 1 ... The average density is approximately 0.2 cm-3"; conclusion "at least 60,000 years". Ball+23 sec. 1 and Sarbadhicary sec. 4 ("visibility times between 20-80 kyrs"), Leahy t_mrg formula with beta = 2, all confirmed. | Frail+94 astro-ph/9407031 (PDF text layer) | MATCH (lower bound, disclosed) |
| SHELL_SOUND_SPEED | 10 km/s | Scan p. 392: "For simplicity in the ensuing discussion, we shall assume that most of the gas in the shell is isothermal ... C_s = (kT/mu)^{1/2} can be C_I approx 1 km s-1 if the gas is HI or H2, or C_II approx 10 km s-1 if the gas is HII"; "T_II approx 8000 K". The same page, right column, computes for an HII region at 8000 K "C_II approx 10.5 km s-1". Eq. 67 "n_s = n_0(V_2^2 + C_0^2)/C_s^2", "valid only if C_0^2 + V_2^2 >> V_2 C_s" confirmed. | Weaver+77 ApJ 218, 377, p. 392 | ADOPTED (round 10 vs the page's 10.5) |
| REMNANT_SHELL_TEMPERATURE | 1e4 K | 2.3: "The temperature of the shell equals the ISM temperature: T_sh=T_ISM=10^4 K" (model assumption); KO15 "shell gas as zones with T<2x10^4 K". | Telezhinsky 2009 arXiv:0812.4604 | ADOPTED (disclosed) |

### 1.8 Module-level tables and coefficients

| item | code | source | verdict |
|---|---|---|---|
| nebular.py CASE_B_HBETA, CASE_B_HALPHA (8 T x 2) | as coded | Extracted from r1b0030..r1b0300.d, first NE=1.000E+02 block, E_NU=4 and E_NU=3, entry 2: 3000 K 3.265E-25/1.048E-24; 5000 2.199E-25/6.687E-25; 7500 1.579E-25/4.625E-25; 10000 1.235E-25/3.536E-25; 12500 1.014E-25/2.860E-25; 15000 8.600E-26/2.398E-25; 20000 6.579E-26/1.807E-25; 30000 4.440E-26/1.199E-25. All 16 identical. | MATCH |
| nebular.py ALPHA_B (7 T) | as coded | e1b.d end table a(dens,temp), per intrat.f "read(15,*) ((a(i,j),i=1,ndens),j=1,ntemp)"; at n_e = 1e2: 5000 4.522E-13, 7500 3.273E-13, 10000 2.585E-13, 12500 2.144E-13, 15000 1.836E-13, 20000 1.428E-13, 30000 9.911E-14. All 7 identical. The comment "no 3000 K row was read" is out of date: the file has 3000 K = 6.708E-13 (also 500 K 2.493E-12, 1000 K 1.512E-12). | MATCH |
| Case B derived | 0.452, 2.863 | 3.536e-25/2.585e-13 = 1.3679e-12 erg per recombination = 0.4520 Halpha photons (vacuum 6564.6 A); ratio 2.863. Kennicutt 1998 eq. 2 "7.9x10^-42 L(Halpha) = 1.08x10^-53 Q(H0)" -> 1.3671e-12 (0.06% off); "upper limit of 3% on the escape fraction" (Leitherer 1995) confirmed. | MATCH |
| feedback.py WEAVER_RADIUS, WEAVER_PRESSURE, WEAVER_TEMPERATURE | 0.76287, 0.16295, 2.07e6 | Scan p. 380 eqs. 20-22 as quoted, "the coefficient has changed from alpha = 0.88 to alpha = 0.76"; p. 382 eq. 37 "T = 2.07 x 10^6 L36^{8/35} n0^{2/35} t6^{-6/35}(1 - xi)^{2/5} K"; p. 387 eqs. 51-52 "27 n0^-1/5 L36^1/5 t6^3/5 pc", "16 ... km s-1"; p. 389 stall sentence as quoted (detailed model R_2 ~ t^0.58). Recomputed: (250/308pi)^0.2 = 0.762865; 7/(3850pi)^0.4 = 0.162950 = (5/11)/(2pi a^3). Eq. 51's 27 pc implies mu = 1.209 m_H; mu = 1.4 gives 26.22 pc. | MATCH |
| feedback.py Sedov, PDS | xi0, 14.0, 413, 1.33e4 | see section 7 | MATCH |
| massive_stars.py SHP03_CLASS_V (15 rows x 7 cols) | as coded | Table 1 "Parameters for OB stars of luminosity class V" diffed field-by-field against the LaTeX: identical. arXiv id astro-ph/0312232 in the code is correct (the brief's astro-ph/0301509 is Gammie+03's HARM paper). | MATCH |
| massive_stars.py MSH05_CLASS_V (12 rows x 7 cols) | as coded | Table 4 (tab_V_obs, 4th table) diffed: identical. | MATCH |
| massive_stars.py VINK_HOT, VINK_COOL, ratios, VINK_JUMP | as coded | Vink+01 (astro-ph/0101509) eq. 24: -6.697, 2.194, -1.313, -1.226, 0.933, -10.92, 0.85 "for 27 500 < Teff <= 50 000 K", ratio 2.6; eq. 25: -6.688, 2.210, -1.339, -1.601, 1.07, 0.85, "12 500 <= Teff <= 22 500 K", ratio 1.3; eq. 15 "61.2 + 2.59 log<rho>"; eq. 23 "-14.94 + 0.85 log(Z/Zsun) + 3.2 Gamma_e"; critical-range sentence verbatim. Eq. numbers counted (15, 23, 24, 25). Vink+00 (astro-ph/0008183): "For the determination of v_esc, the effective mass M_eff=M_*(1-Gamma_e) was used"; "Gamma_e = ... = 7.66 10^-5 sigma_e (L/Lsun)(M/Msun)^-1", sigma_e "taken as determined in Lamers & Leitherer 1993". | MATCH |
| massive_stars.py WR proxy | 25 Msun, 30 kK, 1.5e5 Lsun | Crowther 2007: "At Solar metallicity the minimum initial mass for a star to become a WR star is ~25 Msun"; "from 30 kK amongst WN10 subtypes"; "For Milky Way WC stars, inferred stellar luminosities are ~150,000 Lsun". | MATCH |
| remnants.py IFMR_PARSEC, IFMR_MIST | as coded | Cummings+18 (arXiv:1809.01673) sec. VI.2: all six segments and ranges identical. **New reading**: "this gives a set of three equations for both the PARSEC and MIST-based IFMR, which is our adopted IFMR and selected in bold" - the MIST-based set is the bold one, i.e. the paper's adopted IFMR is the MIST fit, the code's named alternative. (The code docstring records that two reads disagreed on this.) | MATCH (values); preference settled: MIST |
| remnants.py WHITE_DWARF_MAX_INITIAL_MASS | 8.5 | Smartt 2009 (see CORE_COLLAPSE_MIN_MASS). | MATCH |
| remnants.py BLACK_HOLE_MIN_INITIAL_MASS | 25 | Heger+03 sec. II.1: "Fryer (1999) has estimated that the helium core mass where black hole formation by fall back ensues is about 8 Msun (a <~25 Msun main sequence star) ... These numbers are uncertain". Fryer's estimate quoted, not Heger's measurement. | ADOPTED |
| remnants.py BH, NS masses, PN duration | 7.8, 1.33, 27 kyr | Ozel+10 "a narrow mass distribution at 7.8 +/- 1.2 Msun"; Ozel & Freire 2016 "M_0=1.33 Msun and sigma=0.09 Msun"; Badenes+15 "lifetimes of 27+/-6 kyr for the PNe produced by the older progenitors". | MATCH |

### 1.9 Acceptance rows 32-36 (spec.py)

| row | target in code | source read | verdict |
|---|---|---|---|
| 32 GC system mass | 0.9-1.9 x 1.716222334634886e7 Lsun | mwgc.dat Part II parsed: 157 rows, 156 with M_V,t (GLIMPSE02 blank); sum 10^(-0.4(M_V,t - 4.81)) = 17162223.34634886, identical to HARRIS_LUMINOSITY_V; x2 = 3.43e7. BHG16 6.1.2 "M/L_V=1.4+/-0.5 for metal-poor Galactic globular clusters (Kimmig2015)". Header "157 objects", "This revision: December 2010" confirmed. Minor: "A mean stellar mass of (1/3) M_sun and a mean mass to light ratio of M/L = 2 are assumed" and "not yet convincing" are in mwgc.ref (the bibliography), not mwgc.dat. | MATCH |
| 33 stellar halo mass | 4-7e8 | BHG16 6.1.2 "to obtain a rough estimate for the total stellar halo mass M_s=4-7x10^8 Msun. This is somewhat lower than the classical value based on Morrison1993"; Bell "~(3.7+/-1.2)x10^8". | MATCH |
| 34 ionizing rate | 1.7e53-5.3e53 | Chomiuk & Povich 3.1: "correcting for dust absorption and photon escape, they found N_c = (3.5 +/- 1.8) x 10^53 phot s-1"; McKee & Williams "(2.6 +/- 1.3) x 10^53". | MATCH |
| 35 HII LF slope | -2.5 to -1.5 | KEH89 abstract (scan p. 761): "In most galaxies the LF is well represented by a power-law function, with N(L) proportional to L^{-2+/-0.5}"; p. 767 eq. 1 "N(L) = A L^a dL" with "a = -2.3 +/- 0.2 for M31, -2.1 +/- 0.2 for M101, and -1.75 +/- 0.15 for the LMC"; faint-end sentence as in section 6. | MATCH |
| 36 PNLF cutoff | -4.47 | Ciardullo 2012 sec. 4: "By adopting the ``universal'' PNLF ... N(M) propto e^{0.307 M}{1 - e^{3(M* - M)}} the authors obtained a value of M* = -4.47"; "M* = -4.46 +/- 0.05 (standard deviation of the mean)". | MATCH |

### 1.10 Summary count (the 63 constants)

| verdict | count |
|---|---|
| MATCHES | 46 |
| DIFFERS | 2 |
| ADOPTED-NOT-MEASURED | 10 |
| MISATTRIBUTED | 5 |
| UNREACHABLE | 0 |

Module-level tables: every tabulated number re-read matches (Case B 16 + 7, SHP03 105 cells, MSH05 84 cells, Vink 13 coefficients, IFMR 12, Weaver 5, Draine 10). One module-level boundary is ADOPTED (Heger's 25 Msun is Fryer 1999's estimate). One reading is new (Cummings+18 adopts MIST). Rows 32-36 all MATCH. Not re-read: Weaver eq. 66 (p. 391); Byler+17 grid dimensions in the nebular docstring (only the abstract was read); Cioffi+88 and Habing 1968 originals (secondary quotes only).

### 1.11 Every non-MATCH item and the sentence that decides it

1. **STERILIZATION_DISTANCE - DIFFERS (the formula).** Gowanlock+11 eq. 5 as printed in the arXiv LaTeX: `d_{SN}=8~{\rm pc}\times\sqrt{10^{-0.4(M_{SN}-M_{std})}}`. `habitable_zone.sterilization_distance` computes `base_pc * 10.0 ** (-0.4 * (magnitude - m_std))` with no square root. At the mean M_B = -19.34 the Ia distance is 18.6 pc by the source, 43.4 pc in the model: the Ia sterilization volume is 12.6x too large. This settles the question the about line carried: the third read was right.
2. **HALPHA_PER_SFR - DIFFERS (rounding), section misattributed.** 10^41.27 / 3.828e33 = 4.8644e7; code 4.86e7 (-0.09%), while FUV_LUMINOSITY_PER_SFR is carried to full precision. The equation "log SFR = log L_x - log C_x" is in KE12 section 3.8 ("An Updated Compendium ..."), eq. 12, not section 3.1.
3. **GC_HALO_MASS_RATIO - ADOPTED (A-14 class).** BK17 lists "eta=(3-4) x 10^-5" under "I will assume the following". The measurement it cites, Harris, Blakeslee & Harris 2017: "The new calibration of the mean mass ratio eta_M = (2.9 +/- 0.2) x 10^-5". The midpoint 3.5e-5 is 3 sigma above it. The arXiv id is also wrong (see item 5).
4. **GC_METAL_POOR_HALO_MASS_RATIO - ADOPTED.** "with eta_b approx (2-2.5) x 10^-5 (harris2015, harris2017)", same assumption list. The blue-GC ratio was not located in Harris+15. The share 0.643 inherits item 3.
5. **GC_SYSTEM_SCATTER - MISATTRIBUTED (arXiv id).** The sentence "approximately constant with sigma <~ 0.28 dex" is in BK17 = arXiv:1705.01548 sec. 5.1. arXiv:1711.00009 is a different Boylan-Kolchin paper (GCs and high-z UV luminosity functions) and contains none of the four quoted sentences. The same wrong id is on GC_HALO_MASS_RATIO, GC_METAL_POOR_HALO_MASS_RATIO and GC_MEAN_MASS. Harris+17 states 0.28 as an rms ("with a residual rms scatter +/- 0.28 dex"), not an upper bound.
6. **GC_MEAN_MASS - ADOPTED.** "I will assume <m(z=0)>=2.5x10^5 Msun (see harris2017)". Harris+17 gives host-dependent means from 0.94e5 to 3.4e5.
7. **CLUSTER_MASS_MIN - ADOPTED (disclosed).** Lamers+05 sec. 5: "Suppose that the CIMF is a power law ... Mmin approx 10^2 Msun".
8. **IA_IRON_MASS - ADOPTED (disclosed).** Maoz & Graur: "(e.g., Mazzali 2007, Howell 2009) y_Fe,Ia=0.7 Msun, as already assumed in Graur2011."
9. **COMPLEX_LIFE_DELAY - ADOPTED (disclosed).** "we assume that the rise of animal life occurred ~4 Gyr after the planet's formation".
10. **OZONE_CONTINUITY - ADOPTED.** "Therefore, 1.55 Gyr of continuous ozone is required". It rests on the footnote's "ozone layer forms at 2.45 Gyr". The text's own "~2.3 Gya" would give 1.75 Gyr, an inconsistency inside the source.
11. **SUPERNOVA_ENERGY_51 - ADOPTED.** KO15: "For our standard models, we fix the total energy of a single SN to be E_SN=10^51 erg". Chen & Slane call it "the canonical value", and their own fits give 1.3-3.4e50.
12. **SHELL_SOUND_SPEED - ADOPTED.** Weaver p. 392: "For simplicity ... we shall assume ... C_II approx 10 km s-1 if the gas is HII". The same page computes "C_II approx 10.5 km s-1" for an 8000 K HII region, the temperature the about line cites.
13. **REMNANT_SHELL_TEMPERATURE - ADOPTED (disclosed).** Telezhinsky 2.3: "The temperature of the shell equals the ISM temperature: T_sh=T_ISM=10^4 K" (a model assumption).
14. **OXYGEN_ABUNDANCE_SOLAR - MISATTRIBUTED (section).** The "Throughout the paper, we assume (O/H)_sun= 4.90x10^4 [sic], i.e., 12+log(O/H)_sun= 8.69" footnote is in RR15 section 1, not section 2. The value is confirmed at Asplund+09.
15. **HII_ESCAPE_FRACTION - MISATTRIBUTED (the range).** The 30% is Zurita's NGC 157 model (Haffner IV.B). "varying the modeled escape fraction between 30% and 60%" is Hoopes & Walterbos 2003's line-ratio modelling in IV.C, not variants of Zurita's model.
16. **DIG_TEMPERATURE - MISATTRIBUTED (section).** "Temperatures range from about 6000 K to 10 000 K" is in Haffner section II.A ("Basic characteristics of the WIM"), not section I. The midpoint is correct.
17. **DIG_SCALE_HEIGHT - MISATTRIBUTED (section).** "The large, 1000--1800 pc scale height" is in section II.A, not I. The midpoint is correct.

Also found, outside the verdict count:
- HII_LF_MIN_LUMINOSITY is labelled "[dimensionless]" in the constants list; it is erg/s.
- The nebular.py comment "no 3000 K row was read" is out of date: e1b.d has alpha_B(3000 K, 1e2) = 6.708E-13.
- Lamers+05 gives t0's upper error as +1.5 in the text and +1.4 in the table.
- Cummings+18 marks the MIST-based IFMR as "our adopted IFMR" (bold). The code uses the PARSEC fit, citing the isochrones' consistency.
- The brief's arXiv ids for SHP03 (0301509) and the Cummings IFMR (0908.0700) are wrong in the brief only. The code carries the correct ones (astro-ph/0312232, 1809.01673).

## 2. The redistributions and balances, re-derived at a mesh the build did not use

Method: the basic model run at `GridSpec(n_R=180, n_t=600, n_z=8)` — neither the default nor the tests'
coarse (120, 400, 6) — and every identity the phases asserted computed again from the published fields by
`scratchpad/audit3_redist.py` (now `tests/test_audit_iii.py`), beside the default mesh's number. "What would
have to be true for them to differ" is stated per row `[verified: tests/test_audit_iii.py; audit3_redist.log]`.

| identity (decision) | default mesh | audit mesh | noise / bound | verdict |
|---|---|---|---|---|
| clouds: mass in clouds / molecular mass (D181) | 1.0374 | 1.0549 | census noise 0.035 (√Σm²/M) | holds: 1.1σ and 1.6σ. Would differ only if the expected count were not the molecular mass over the mean cloud mass ring by ring — it is, to 10⁻⁹ |
| clouds: expected / realised count | 0.99937 | 1.00112 | Poisson, 1.7 × 10⁴ | holds |
| clusters: mass formation rate / SFR (D182) | 1.0292 | 1.0313 | inherits the clouds' 1.037 | holds; the 3% is the clouds' Poisson excess, not the efficiency (ε is derived ring by ring) |
| clusters: ΣQ / light's Q(H⁰) total (D182) | 0.9887 | 0.9689 | census noise ~0.06 (N_eff ~600) | holds; would differ if Q per unit mass at the cluster's age were not the light stage's table — the same `per_mass_at` reads both |
| HII regions' Hα / the HII field's integral (D184) | 0.9901 | 0.9706 | 0.059 / 0.061 | holds; the same 3% as the clusters' photons (the regions are the clusters') |
| nebular: total field / `halpha_luminosity_nebular` | 1.0 | 1.0 | exact | identity |
| remnants: drawn against expected (D185) | +0.41σ | +0.97σ | Poisson | holds |
| remnants: expected / rate × lifetime | 1.0 | 1.0 | exact | identity |
| dust: worst emitted/absorbed − 1 per radius (D180) | 1.5 × 10⁻¹² | 1.4 × 10⁻¹² | quadrature | identity — and says nothing about how much is absorbed (#91) |
| dust: total emitted/absorbed − 1 | 2 × 10⁻¹⁵ | 2 × 10⁻¹⁵ | exact | identity |
| pattern: max |⟨contrast⟩_φ − 1| | 2 × 10⁻¹⁶ | 2 × 10⁻¹⁶ | exact | identity |
| gc: `bound_mass()` / `bound_cluster_mass_total` (D183) | 1.0 | 1.0 | exact | identity |
| hierarchy: union at levels 1, 2, 3 on cell 300 (D181) | holds (22 rows) | holds (20 rows) | exact | the parent's rows are its children's inherited rows, column for column, at a mesh whose cell 300 holds a different sample |

No redistribution moved outside its own noise at the new mesh. The three that read 0.97 at the audit mesh
(clusters' Q, HII Hα) are one number — the clusters realised at that seed hold 0.969 of Σ_Q — and inside 1σ.

## 3. The green rows added by the second build, conditioned (AUDIT_RUN2 §5)

| row | green on | the alternative in the constant's about | survives? | verdict |
|---|---|---|---|---|
| 29 Tully–Fisher slope (S28) | the sweep of `halo_mass` over five values; −7.914 against Sakai's −7.85 ± 0.71 | the zero point (−19.00 vs −19.70) is unjudged because dust moves it and the model's light is intrinsic (D177) | judged on the slope alone by ruling | conditioned at entry; the slope of a disc-dominated model at fixed M/L is close to a prediction, the nearest thing to an unconditioned green the build has |
| 30 core-collapse rate (S30) | 0.0176 yr⁻¹ in Adams et al.'s [0.006, 0.105] | `CORE_COLLAPSE_MIN_MASS` 8.5 (Smartt; Heger's 8 the alternative) | the window spans a factor 17.5; the SFR would have to fall to 0.60 or rise to 10.5 M☉/yr to leave it `[verified: audit3_greens.py]` | green says almost nothing; the rate is SFR × IMF and both are upstream |
| 31 type Ia rate (S30) | 0.00653 yr⁻¹ in [0.006, 0.028], 0.0005 above the floor | `Y_FE_IA` 0.0017 [recall] over `IA_IRON_MASS` 0.7 → 2.43 × 10⁻³ events per M☉, 1.87 × Maoz & Graur's measured 1.3 ± 0.1 × 10⁻³ | **no**: at the measured efficiency 0.0035 yr⁻¹, 0.35 per century, fails (#88) | green by a recalled yield; the one green row of the build that the named alternative kills |
| 35 HII-region LF slope (S35) | −2.008 in KEH89's −2.0 ± 0.5 | the slope is inherited from the cloud mass function at one efficiency (#96): inner −1.6 / outer −2.2 | yes: inner regions alone −1.76, outer alone −2.15, 0.1 / 0.3 dex bins −2.01 / −2.06, floor 10³⁶ → −1.75, 10³⁸ → −2.09 — every reading inside `[verified: audit3_greens.py]` | green by the clouds' slopes bracketing the observed one (Rice et al.'s two slopes straddle KEH89's −2); 2 166 of 12 860 regions are above the floor |

Two of the four greens are conditioned on a source's slope pair (35) or a window a factor 17 wide (30);
one (31) does not survive its own alternative; one (29) is a ruling's half of a two-part measurement.

## 4. The disclosed rows, re-read blind

A reading agent was given the sources and forbidden the repository (`scratchpad/audit3_blind.md`). It set:

- **Row 32 (GC system mass).** Window **[2.7, 4.0] × 10⁷ M☉**, centre 3.3 × 10⁷: the Harris 2010 Part II M_V,t sum
  (156 clusters, 1.716 × 10⁷ L☉ at M_V☉ = 4.81, recomputed independently and equal to the build's) at
  **M/L_V = 1.9 (1.6–2.2)** from Baumgardt, Sollima & Hilker 2020 §3.3, "average mass-to-light ratio of M/L_V =
  1.83 ± 0.03 … compared to M/L_V = 1.92 ± 0.05 … from the literature magnitudes" `[verified: arXiv:2009.09611,
  read blind]`, the 1.92 being the consistent pairing with Harris's literature magnitudes; Baumgardt & Hilker
  2018's dynamical masses (112 clusters, Σ = 3.23 × 10⁷; matched to Harris, M/L 2.07) corroborate. The blind
  reader **did not adopt Kimmig's 1.4 ± 0.5** — BHG16 quote it for metal-poor clusters, to turn halo star counts
  into mass — which is the ratio S34 chose (#98's disclosure) and which gives [1.54, 3.26] × 10⁷. **The model's
  7.13 × 10⁷ misses either window** (0.25 dex above the blind one's top against 0.47 dex above the built one's
  centre): the disclosure was honest and the miss stands; the window itself should be the blind one (A3-x).
- **Row 34 (Q(H⁰)).** The blind reader chose **McKee & Williams 1997, (2.6 ± 1.3) × 10⁵³, window [1.3, 3.9] ×
  10⁵³**, for reasons stated before any comparison: whole Galaxy, both Galaxy-wide tracers (thermal radio and
  COBE [N II]), its corrections stated (dust ~25%; the 1.37 Murray & Rahman borrow). S35 chose Bennett et al.
  1994's [1.7, 5.3] × 10⁵³ as the primary analysis and disclosed that the model's 1.65 × 10⁵³ was known and
  would pass McKee & Williams'. **Under the blind window the row passes**; under the built one it misses by
  3%. The blind reader also notes all five candidates overlap between 1.9 and 2.7 × 10⁵³ once rescaled to
  R₀ = 8.2 kpc, and Murray & Rahman's 3.2 × 10⁵³ has no uncertainty. The 0.71 of `halpha_sfr_ratio` (#100)
  is unaffected by which window is chosen: it is the isochrones' Q against Starburst99's, not against a galaxy.

Both rows: the built windows were chosen with the model's number known and said so; the blind windows
differ from both, one toward the model and one away. Neither is applied here (B3); A3-x asks the owner
to rule which windows rows 32 and 34 carry, with the recommendation that the blind ones do.

## 5. The register's second-build items, re-stated

One line each: still-open / closable-now / wrongly-described, with the sentence that decides it.

| # | one line | state |
|---|---|---|
| 80 | `BAR_LENGTH_RATIO` 2.0 is recall against an unstated R_d; the only sourced ratio that lands row 15 is BHG16's own 5.0/2.6 = 1.92 (S26) | still open; the owner's call (B5), not a reading |
| 81 | the 0.1 Gyr young-star cut has no source; needs a spiral pattern speed | still open |
| 82 | rows 25–28 n-y-c: BHG16 Table 2's magnitudes not stated extinction-corrected | still open; closable by Licquia+2015's errors or a dust-attenuated magnitude (Phase 7 gave A_V; V1–V3 could publish it) |
| 83 | v_esc without Γ_e in the wind recipe (10–20% high v_∞) | closable now: one constant σ_e with a citation |
| 84 | Q's calibration covers 0.33 of a steady population's Q; the youngest isochrone hides ~half | still open; **#100's 0.71 is this debt measured** (the model's Q per SFR is 0.71 of Starburst99's) — 84 and 100 are one mechanism |
| 85 | locked mass 0.836 of stars + remnants: R 0.30 vs 0.41 | still open; a mechanism in `sfh` |
| 86 | remnant masses and boundaries metallicity-independent | still open |
| 87 | row on Σ_WD(R₀) 4.9 ± 0.8 owed, read before ruling; model 4.757 pinned | **not enterable blind**: the pin is in the repo and the window is the source's own (no choice to make); enterable *disclosed* with a published scalar — a code change, so a ruling (A3-x) |
| 88 | row 31 rests on a recalled Ia yield 1.87× the measured efficiency | still open; §3 confirms the green dies at the measured value |
| 89 | the spheroid's Ia not in the rate | still open |
| 90 | the habitable zone's two readings of Gowanlock eq. 5 | still open |
| 91 | the dust slab is grey | still open; the remedy (eight bands) is one afternoon |
| 92 | the PAH fit applied per radius, 2× Draine & Li at R₀ | still open |
| 93 | row on T_d owed: Planck's 19.7 ± 1.4 K is a sky average, not a face-on T_d(R) | **wrongly-described as a row owed**: the source does not measure the model's quantity (D177's rule names no field) — record as not enterable, not carried as owed (A3-x) |
| 94 | all molecular gas in clouds, M_min 10⁴ unsourced | still open |
| 95 | cloud offset, gradient, height unsourced; no remnant state | still open |
| 96 | the cluster census inherits the cloud slopes | still open; §3 shows it is what makes row 35 green |
| 97 | bound mass 72× η M_halo before survival; survival built on the wrong population (S34) | still open; needs a globular age cut and a halo-orbit t₀ |
| 98 | row 32 misses Harris by 0.47 dex at Kimmig's M/L | still open; **the window is wrongly chosen** (§4): the blind M/L is 1.9, the miss 0.25 dex |
| 99 | row 33: stellar halo 3.0 × 10⁹ vs 4–7 × 10⁸ | still open; the lever is a stellar-to-halo relation for the satellites |
| 100 | row 34 misses Bennett by 3%; Q/SFR 0.71 of Starburst99 | **the window is wrongly chosen** (§4): under McKee & Williams the row passes; the 0.71 stands and is #84 |
| 101 | DIG 30% by construction vs Oey's 0.59 and Haffner's 1/8 | still open |
| 102 | remnants untied from their clusters; core collapses ignore the arms | still open; the remedy is stated |
| 103 | remnant count set by Frail's 60 kyr, read garbled; inferred shell physics | still open; the count moves 27× under the alternative |

Counts: 24 items; 20 still open as described; 2 closable now (83, and 87 once a scalar is published); 2 wrongly
described (93 as a row owed; and 84/100 as two debts). No item is discharged here (B3).

## 6. Findings, numbered for D186 and the register

Each names the decision it needs. None is applied here (B3).

- **A3-1 (defect, changes model output). `habitable_zone.sterilization_distance` drops a square root.** Gowanlock et
  al. 2011 eq. 5 as printed is d_SN = 8 pc × √(10^(−0.4(M_SN − M_std))), exponent −0.2; the code computes
  10^(−0.4 ΔM). At the mean type Ia magnitude the source gives 18.6 pc, the model 43.4 pc: **the Ia sterilization
  volume is 12.6× too large**, and the zone S30 published (deliberately unjudged, D179) is wrong by it. This settles
  #90's two readings: the third read was right. *Decision:* the next model-side change fixes the exponent, re-pins
  the zone's probes (the second reading's numbers — hazard at R₀ 0.20 per Gyr, the habitable count peaking at
  6.6 kpc — are what the model should then read, D179), and #90 closes on the reading and stays on Lineweaver.
  Registered as **#104**.
- **A3-2 (A-14's class). `GC_HALO_MASS_RATIO` 3.5 × 10⁻⁵ is an adopted value; the measurement behind it is
  (2.9 ± 0.2) × 10⁻⁵.** Boylan-Kolchin 2017 lists "η = (3–4) × 10⁻⁵" under "I will assume the following"; the
  paper he cites, Harris, Blakeslee & Harris 2017, measures "η_M = (2.9 ± 0.2) × 10⁻⁵ … significantly lower than
  in previous papers", with "a residual rms scatter ± 0.28 dex" (an rms, not a bound). At the measured η, η M_halo
  = 3.19 × 10⁷ and S34's mean 6.97 × 10⁷ sits **+0.34 dex above it — outside the 0.28 dex** that D183 said it was
  inside. So the GC closure fails on the measured relation as well as on the population (#97). `GC_METAL_POOR_
  HALO_MASS_RATIO` and `GC_MEAN_MASS` are adopted in the same list. *Decision:* the constants take the measured
  values with Harris et al. 2017 as the citation (η 2.9 × 10⁻⁵ ± 0.2; the scatter as an rms), D183's "inside the
  scatter" is corrected in the next decision, and the test that asserts the consistency check moves with the
  number in the comment. Registered as **#105**.
- **A3-3 (record). Five citations are misattributed and one is rounded.** All four Boylan-Kolchin constants cite
  arXiv:1711.00009, a different paper; the sentences are in arXiv:1705.01548 (MNRAS 472, 3120). `HII_ESCAPE_
  FRACTION`'s "between 30% and 60%" is Hoopes & Walterbos 2003's line-ratio modelling (Haffner §IV.C), not
  variants of Zurita's model. `DIG_TEMPERATURE` and `DIG_SCALE_HEIGHT` are Haffner §II.A, not §I. `OXYGEN_
  ABUNDANCE_SOLAR`'s footnote is Rémy-Ruyer §1, not §2. `HALPHA_PER_SFR` is 4.86 × 10⁷ against the exact
  4.8644 × 10⁷ (−0.09%) and the equation is KE12 §3.8 eq. 12, not §3.1. `HII_LF_MIN_LUMINOSITY` is labelled
  dimensionless; it is erg/s. The `nebular.py` comment "no 3000 K row was read" is out of date (α_B(3000 K) =
  6.708 × 10⁻¹³ is in the file). Lamers et al. give t₀'s upper error as +1.5 (text) and +1.4 (table). *Decision:*
  an about-line pass in the next session that touches `level0.py` (no number moves except the −0.09%, which is
  a rounding and moves nothing at the pinned precision). Registered as **#106**.
- **A3-4 (adopted, disclosed or not).** `SUPERNOVA_ENERGY_51` (every source "fixes" or calls canonical the 10⁵¹ erg;
  none measures it; Chen & Slane's fits give 1.3–3.4 × 10⁵⁰), `SHELL_SOUND_SPEED` (Weaver "assume … C_II ≈ 10";
  the same page computes 10.5 at 8000 K), `OZONE_CONTINUITY` (1.55 Gyr rests on a footnote's 2.45 Gyr; the text's
  own "~2.3 Gya" would give 1.75), `CLUSTER_MASS_MIN`, `IA_IRON_MASS`, `COMPLEX_LIFE_DELAY`, `REMNANT_SHELL_
  TEMPERATURE` (disclosed as assumptions in their abouts), and `remnants.py`'s 25 M☉ black-hole boundary (Fryer
  1999's estimate quoted by Heger et al., "these numbers are uncertain"). *Decision:* none moves; each about
  says "adopted" where it does not yet (part of #106); `SUPERNOVA_ENERGY_51` and `SHELL_SOUND_SPEED` are the two
  a source could still measure, and #103 already carries the remnant census's dependence on them.
- **A3-5 (reading settled). Cummings et al. 2018's adopted IFMR is the MIST-based fit** ("our adopted IFMR and
  selected in bold"); the code uses the PARSEC fit for consistency with its isochrones and records that two reads
  disagreed on which the paper preferred. The disagreement is over: the paper prefers MIST, the code chooses PARSEC
  for a stated reason. *Decision:* the docstring says so; no number moves (the fits differ by < 0.05 M☉ over the
  range, D178).
- **A3-6 (the greens).** Row 31 is the one green of the build that dies under its constant's own alternative
  (0.35 per century at Maoz & Graur's measured efficiency; #88). Row 30's window spans a factor 17.5. Row 35 is
  green because Rice et al.'s two cloud slopes straddle KEH89's −2 (#96). Row 29 is a ruling's half of a
  measurement. *Decision:* none; recorded in `test_s22_rulings`'s conditioning already, now with the numbers.
- **A3-7 (the blind windows).** Row 32's blind window is [2.7, 4.0] × 10⁷ at Baumgardt et al. 2020's measured
  M/L_V 1.9, not Kimmig's 1.4 ± 0.5 for metal-poor clusters; the model misses either (0.25 dex vs 0.47). Row 34's
  blind source is McKee & Williams 1997, [1.3, 3.9] × 10⁵³, under which the model passes; S35 chose Bennett 1994
  and disclosed it. *Decision (the owner's, B5):* whether rows 32 and 34 carry the blind windows. The
  recommendation is yes for both — the blind reader's reasons were stated before any comparison, and one moves
  toward the model and one away — with the row texts keeping the disclosure. The 0.71 of #100 stands either way.
- **A3-8 (rows owed).** #87's Σ_WD(R₀) row cannot be entered blind (the pin is in the repo and the window is the
  source's own); it can be entered *disclosed* once a scalar is published — a code change (a decision, not
  this session's). #93's T_d row cannot be entered at all: Planck's 19.7 ± 1.4 K is a sky average seen from the
  Sun, not the face-on T_d(R) the model publishes (D177: a source that does not measure the model's quantity
  names no field). #93 is re-described accordingly; #87 stays owed with its route stated.
- **A3-9 (one mechanism, two debts).** #84 (the Q calibration covers a third of a population's Q; the youngest
  isochrone hides stars above 64 M☉) and #100 (the model's Q per SFR is 0.71 of Starburst99's; row 34) are one
  mechanism measured twice. *Decision:* #100's remedy is #84's; the register says so in both.

**Counts.** 63 constants re-read: 46 match, 2 differ (one a formula, one a rounding), 10 adopted rather than
measured (5 of them disclosed as such), 5 misattributed, 0 unreachable; every module table matches (Case B 23
values, SHP03 105 cells, MSH05 84, Vink 13, IFMR 12, Weaver 5, Draine 10); rows 32–36's targets match. Thirteen
redistributions and balances hold at the audit mesh, none outside its noise. Four greens conditioned, one dies
under its alternative. Two blind windows differ from the built ones. Twenty-four register items re-stated: 20
still open as described, 2 closable now (#83; #87 with a published scalar), 2 wrongly described (#93; #84/#100 as
two). Three new debts (#104–#106). No number moved.
