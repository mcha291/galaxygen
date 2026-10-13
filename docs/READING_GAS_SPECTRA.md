# READING_GAS_SPECTRA — the gas column density's power spectrum, its break at the disc's thickness, the log-normal width against the Mach number (for BUILD_III Phase L2)

**The lead's note (2026-10-13, entered at S62's open).** One Opus reader, briefed by BUILD_III §3e and forbidden the
repository, fetched 23 arXiv preprints, converted them to text and read the passages itself; what is below the rule is
its note as returned, its headings one level down. Journal volumes and pages in the tags come from the brief or from
search listings, not from the preprints (the reader says so). **What the reading says that the plan's text did not
foresee** (the lead's summary; D221 rules on it): (1) the disc's thickness is the spectrum's *break*, not its outer
scale — the 2-D column spectrum is a power law from the kpc scales down to the thickness and steeper by about one
below it, and no turnover is seen inside any disc; (2) whether the break exists at all is contested once the beam is
forward-modelled (Koch et al. 2020 against Elmegreen et al. 2001, Block et al. 2010, Combes et al. 2012); (3) the
large-scale slope runs from −1.0 to −2.7 by sample and estimator (THINGS' median −1.6); (4) the column-density width
is A ln(1 + b²M²) with A = 0.11, b = 1/3 in solenoidal MHD, three times wider under compressive forcing; (5) the two
briefed papers "Nandakumar & Dutta 2020 (THINGS two-slope fits)" and "Koch 2019 (M33 widths)" do not exist as
described.

---

## READING: gas column-density spectra and log-normal widths (S62, Phase L2, `gas_fluctuation`)

Reader: Opus reading agent, 2026-10-13. Read-only; nothing in the repository touched.
Method: arXiv PDFs fetched (`l2_spectra/pdf/`), converted to text with pypdf (`l2_spectra/txt/`), passages read and grepped by me. Every `[verified: ...]` number below was read on that text. Numbers I computed from read numbers are marked **(derived)**. Anything from memory is tagged `[recall - NOT READ]` and kept out of the table.

Bibliographic caveat: what was read is the arXiv preprint named in each tag (id, section, table). The journal volume/page numbers in the tags come from the brief or from search-result listings, not from the preprints, so treat those bibliographic fields as `[recall - NOT READ]` (the numbers quoted are unaffected). Preprint and journal versions may differ slightly.

Slope convention throughout this note: P(k) ~ k^alpha, **alpha negative**. Several sources write P ~ k^-beta or k^-alpha with a positive index; I have converted the sign. I did not change any magnitudes.

"2-D spectrum" means the azimuthally averaged power spectrum of a 2-D image (|FFT|^2 averaged in rings of |k|; this is what most extragalactic papers call a "1-D" spectrum, e.g. Koch 2020). "Strip 1-D spectrum" means the average of 1-D FFTs along image rows (Elmegreen et al. 2001); its slope is shallower by about 1 than the 2-D one (Elmegreen et al. 2001 Sect. 3.6; Elmegreen & Scalo 2004 Sect. 2.1).

---

### 1. Summary table

| # | Quantity | Value (central) | Range across sources | Source tags |
|---|---|---|---|---|
| 1a | 2-D slope of the gas column / HI intensity spectrum, **above** the disc thickness (large scales, ~0.3-16 kpc), spirals | alpha = -1.6 (half of THINGS between -1.9 and -1.5) | THINGS single fits -0.3 to -2.2 (mean -1.3, s.d. 0.5); NGC 5236 -1.23; NGC 6946 -0.96; NGC 1058 -1.0; Grisdale's THINGS re-fit -1.6 to -2.8 | Dutta+2013 Tab.2; Nandakumar & Dutta 2020 Sect.5; N&D 2023 abstract; Dutta+2009 abstract; Grisdale+2017 Sect.3.2.1 |
| 1b | Same, Local Group, resolved to ~10-50 pc, large-scale (>~100-500 pc) segment | HI: LMC ~-2.7 (2-D), M33 -2.4 | HI M33 -2.0 to -2.4 (Combes LS); single fits at ~170-200 pc beam: M31 -2.66, M33 -2.18; dust/FIR LS: LMC -0.78 to -2.15, M33 -0.9 to -1.6 | Block+2010 Sect.2.2 (quoting EKS01); Combes+2012 Tab.3; Koch+2020 Tab.3, Tab.1 |
| 1c | 2-D slope **below** the thickness (small scales) | HI: LMC ~-3.7, M33 -3.2 | HI M33 -3.2 to -3.6; NGC 1058 -2.5 +/- 0.6; Milky Way HI/CO/dust maps -2.8 to -3.2 (and -2.5 to -2.8); dust LMC -2.55 to -3.08, M33 -2.6 to -4.7 | Block+2010 Sect.2.2; Combes+2012 Tab.3; Dutta+2009; Elmegreen & Scalo 2004 Sect.2.1; Dutta+2013 abstract |
| 1d | Change of slope across the break | ~1 (steeper below) | 0.8 (M33 HI) to 1.5 (NGC 1058); dust 0.9-3.6; Kortgen sim. example 2.5 | EKS01 Sect.3.3; Block+2010 intro + Sect.2.2; Zhang+2012 Sect.4; Combes Tab.3; Kortgen+2021 Sect.3 |
| 2a | Break scale (as a length) | LMC HI: wavelength 80-100 pc (rising to ~150 pc at large radius) | LMC FIR dust "1/k ~ 100-200 pc"; M33 HI 110 pc (100-120), CO 103 pc, dust 93-390 pc (grows with beam); NGC 1058 1.5 kpc | EKS01 Sect.3.3, 3.5; Block+2010 abstract; Combes+2012 Tab.3; Dutta+2009 Sect.3 |
| 2b | Break-to-thickness relation | Dutta+2009: break at baseline U = D/(pi z_h), i.e. break length D/U = pi * z_h (1.5 kpc -> z_h = 490 +/- 90 pc) | EKS01: break wavelength ~ line-of-sight thickness (80-100 pc vs. quoted LMC scale heights 95-350 pc; models want a structured layer ~50 pc thick); Combes sims: break 63-650 pc against H_z = 2.35 sigma_z of 64-217 pc | Dutta+2009 Sect.3; EKS01 Sect.3.3, Sect.5; Combes+2012 Tab.4 |
| 2c | Whether a break is real at all | contested | No break once the PSF is forward-modelled (LMC, SMC, M31, M33 dust; M31/M33 HI and CO), except LMC 24 um (30 Dor, 190 pc); THINGS breaks coincide with the beam; simulated breaks "almost never" trace the scale height | Koch+2020 abstract, Sect.3.5, Tab.3; Grisdale+2017 Sect.3.2.1; Kortgen+2021 abstract, Sect.3 |
| 3a | Column-density log-normal width vs Mach number (simulations) | sigma^2_ln(Sigma/Sigma0) = A ln(1 + b^2 Ms^2), A = 0.11, b = 1/3 (solenoidal, isothermal MHD, Ms 0.4-8.8) | fits to clouds: Taurus b = 0.5, A = 0.16; IC 5146 b = 0.5, A = 0.12. Federrath 2010 at Ms ~ 5.5: sigma_ln Sigma = 0.46 (solenoidal), 1.51 (compressive) | Burkhart & Lazarian 2012 abstract, eq.3, Tab.1; Federrath+2010 Tab.3 |
| 3b | 3-D forcing parameter b | b ~ 1/3 solenoidal (3-D), ~1 compressive | measured 0.36 (sol.), 1.05 (comp.); ~1/2 for 2-D solenoidal; PNJ97 b ~ 0.5 | Federrath+2008 Sect.3, eq.4-5, Fig.3 |
| 3c | Measured extragalactic column-density PDF widths (dex = std of log10) | HI: M31 0.27 dex (0.19-0.23 in sub-regions, ~170 x 785 pc beam); M51 0.51 dex (~300 pc) | H2/CO: M51 0.64 dex (~300 pc); PAWS M51 I(CO) 0.44 dex (40-53 pc), environments 0.21-0.47; LMC CO 0.26-0.3; PHANGS molecular Sigma 16-84% FULL width 0.52-1.18 dex (45-120 pc) | Berkhuijsen & Fletcher 2015 Fig.1-2, Sect.3.1, 4; Hughes+2013 Tab.1; Sun+2018 Tab.4, Sect.5.1.2 |
| 4 | Outer scale (flattening at large scale) | none observed inside the disc; power laws run to the disc size | column power law to 11 kpc (NGC 5236; "energy input ~6 kpc" inferred from the velocity spectrum and a Jeans length); to 6 kpc (NGC 6946); to R/r25 ~ 1, and > 2 in NGC 6946 (THINGS, up to 15.8 kpc); NGC 1058 shallow law to 10 kpc | Nandakumar & Dutta 2020 Sect.5; N&D 2023 abstract; Dutta+2013 Sect.3; Dutta+2009 abstract |

---

### 2. Per-source notes

### 2.1 Elmegreen, Kim & Staveley-Smith 2001 (LMC HI)
`[verified: Elmegreen, Kim & Staveley-Smith 2001, ApJ 548, 749, arXiv:astro-ph/0010578, Sect.3.3, 3.5, 3.6, 4, 5, Fig.2, Fig.8, https://arxiv.org/abs/astro-ph/0010578]`
- Data: ATCA + Parkes HI of the LMC, 1' (15 pc) resolution, final maps 40'' (~10 pc); peak-T, integrated and single-channel maps (no difference among them).
- Estimator: mainly **strip 1-D spectra** (average of FFTs of image rows, 600 rows of 630 px); also one 2-D spectrum (Fig.8, central 6.3 x 6.3 kpc, 1 px = 10 pc), "slope of the 2D power spectrum exceeds the average slope of the 1D power spectrum by about 1".
- Result: strip 1-D slope steepens from -5/3 at low spatial frequency to -8/3 at high; "the steepening transition ... occurs at a wavelength of 80-100 pc" (Sect.3.3); break wavelength rises from ~80 pc at small radius to ~150 pc at large radius (Sect.3.5). Interpretation from Lazarian & Pogosyan 2000: 2-D spectra -8/3 (thin) and -11/3 (thick); 1-D shallower by 1.
- Thickness context quoted: cool-cloud scale height 95 pc, warm diffuse 350 pc (Wang & Helfand), HI scale height ~180 pc (Kim et al. 1999). The authors' fractal models want most structure in a thin layer "perhaps ~50 pc thick" (Sect.5).
- Width/Mach: their model exponentiates a 3-D k^-5/3 noise with zeta = (ln[1 + 0.5 M^2])^0.5 (inferred from Nordlund & Padoan 1999); best fits need "unrealistically large Mach numbers", so phase transitions are added (Sect.4, 5). rms of PS variation with position ~0.6 at kpc to ~0.25 at ~20 pc (abstract).
- Covers: one galaxy, HI only, 10-2000 pc.

### 2.2 Block, Puerari, Elmegreen & Bournaud 2010 (LMC Spitzer FIR)
`[verified: Block et al. 2010, ApJL 718, L1, arXiv:1006.2080, abstract, Sect.1, Sect.2.2, https://arxiv.org/abs/1006.2080]`
- Data: MIPS 24, 70, 160 um, deprojected (i = 35 deg), 2-D FFT averaged over |k|, 15 bins.
- Slopes (2-D): high k -3.08 +/- 0.13, -2.97 +/- 0.52, -2.55 +/- 0.34 (160, 70, 24 um); low k -2.15 +/- 0.48, -1.83 +/- 0.36, -0.78 +/- 0.19. Abstract summary: -1.6 low k, -2.9 high k.
- Break: "k^-1 ~ 100-200 pc" for all bands; at 160 um "approximately 1/k = 200 parsecs". **Convention not stated** (whether 1/k is a wavelength or wavelength/2pi).
- HI comparison (reading of EKS01): 2-D HI slope ~-3.7 at high and ~-2.7 at low spatial frequency, break at 1/k ~ 100 pc.
- Intro: "PS for integrated emission from turbulent gas has a slope that differs by 1" between 2-D and 3-D cases (Lazarian & Pogosyan 2000; Lazarian et al. 2001).
- Covers: dust emission (not column density), one galaxy, ~1.5 pc to kpc.

### 2.3 Combes et al. 2012 (M33, HERM33ES)
`[verified: Combes et al. 2012, A&A 539, A67, arXiv:1201.2558, Tab.1, Sect.3-4, Tab.3, Tab.4, https://arxiv.org/abs/1201.2558]`
- Data: HI 12'' (48 pc), CO(2-1) 12'' (48 pc, partial), Herschel/Spitzer 24-500 um (24-144 pc), deprojected (i = 56 deg); 2-D FFT, azimuthal average; two power laws with free break chosen by minimum summed chi^2.
- Table 3 (LS > 500 pc / ss < 500 pc / break pc): HI -2.4 / -3.2 / 110 (extremes -2.0 to -2.4 / -3.2 to -3.6 / 100-120); CO(2-1) -1.5 / -3.7 / 103; dust 24 um -0.9 / -2.6 / 93 ... 500 um -1.1 / -4.4 / 390. The HI fit is called "ambiguous ... the two slopes are close, and the determination less trustworthy".
- Break grows with beam (Appendix B tested); the authors say the 70 um break is larger "only because of the coarser" resolution.
- Simulations (Table 4): LS -0.8 to -2.3, ss -2.8 to -5.2, breaks 63-650 pc, gas scale heights H_z = 2.35 (<z^2> - <z>^2)^1/2 of 64-217 pc. Fiducial run: -1.3 / -3.8 / 63 pc, H_z = 120 pc.
- **Break-scale convention** (wavelength or 1/k) not stated explicitly; k is the conjugate of x in e^{-i k x}.

### 2.4 Dutta et al. 2008 (NGC 628), 2009a (NGC 1058), 2009 (dwarfs), 2013 (THINGS), Dutta & Bharadwaj 2013
- NGC 628: `[verified: Dutta et al. 2008, MNRAS 384, L34, arXiv:0711.1234, abstract, https://arxiv.org/abs/0711.1234]` visibility-based estimator; alpha = -1.6 +/- 0.2 over 800 pc - 8 kpc; upper limit on scale height 800 pc.
- NGC 1058: `[verified: Dutta, Begum, Bharadwaj & Chengalur 2009, MNRAS 397, L60, arXiv:0905.1450, abstract, Sect.3, Tab.1, https://arxiv.org/abs/0905.1450]` alpha = -1.0 +/- 0.2 for U = 1.0-6.5 klambda (1.5-10 kpc) and -2.5 +/- 0.6 for U = 6.5-16 klambda (0.6-1.5 kpc). Transition expected "at a baseline U = D/pi z_h"; length scale is D/U; break at 1.5 kpc -> z_h = 490 pc, +/- 90 pc from bin width. Resolution 13.6'' ~ 660 pc (quoted by Block+2010). Galaxy face-on (i 4-11 deg), D = 10 Mpc.
- Dwarfs: `[verified: Dutta et al. 2009, MNRAS 398, 887, arXiv:0905.1756, abstract, https://arxiv.org/abs/0905.1756]` 8 galaxies; slopes ~-1.5 (AND IV, NGC 628, UGC 4459, GR 8) to ~-2.6 (DDO 210, NGC 3741), read as 2-D vs 3-D; slope independent of channel width.
- THINGS: `[verified: Dutta, Begum, Bharadwaj & Chengalur 2013, New Astron. 19, 89, arXiv:1208.5386, abstract, Tab.2, Sect.3, https://arxiv.org/abs/1208.5386]` 18 spirals, visibility estimator of HI **intensity** (not deprojected column density); single power law per galaxy over ~1 decade, 0.3-16 kpc; alpha per galaxy from -0.3 +/- 0.2 (NGC 4736) to -2.2 +/- 0.1 (NGC 5457); "50% of the values in the range alpha = -1.9 to -1.5", mean -1.3, s.d. 0.5; no correlation with SFR, dynamical mass, HI mass, velocity dispersion. Abstract quotes Milky Way small-scale slopes -2.8 to -2.5 and calls them 3-D. Power law reaches R/r25 ~ 1 and > 2 in NGC 6946.
- Column-density amplitude: `[verified: Dutta & Bharadwaj 2013, MNRAS 436, L49, arXiv:1308.2680, eq.16-19, Tab.1, Tab.3, https://arxiv.org/abs/1308.2680]` six face-on (i <= 35 deg) THINGS spirals; k^2 P_NHI(k) = mean-square column fluctuation at length 2 pi/k; A_NHI at k = 1 kpc^-1 in (10^20 cm^-2)^2: NGC 628 1.4 (mean N_HI 3.6), NGC 3184 0.45 (4.3), NGC 5194 7.7 (4.9), NGC 5457 13.9 (6.4), NGC 5236 1.5 (27.7), NGC 6946 0.35 (5.3); alpha -1.3 to -2.1. **(derived)** rms/mean at 2 pi kpc: 0.33, 0.16, 0.57, 0.58, 0.04, 0.11.

### 2.5 Nandakumar & Dutta 2020 (NGC 5236) and 2023 (NGC 6946)
- `[verified: Nandakumar & Dutta 2020, MNRAS (arXiv:2006.04575v3), abstract, Sect.5, Tab.2, https://arxiv.org/abs/2006.04575]` VLA + GMRT, visibility moment estimator, HI **column density**; alpha = -1.23 +/- 0.06 over ~300 pc - 11 kpc; velocity -1.91 +/- 0.08 over 0.9-16 klambda. No steepening down to 300 pc, so "the scale height of NGC 5236 is less than this scale". "Energy input scale ~6 kpc": the velocity power law extends to 6 kpc and a Jeans scale ~4.5 kpc is estimated; this is an inference, not an observed flattening. Table 2 quotes thin-disc expectations from Federrath et al. (2009): column slope -0.78 +/- 0.06 (solenoidal), -1.44 +/- 0.23 (compressive) - read only as quoted here.
- `[verified: Nandakumar & Dutta 2023, MNRAS 526, 4690, arXiv:2310.02661, abstract, Sect.5, https://arxiv.org/abs/2310.02661]` NGC 6946; column density alpha = -0.96 +/- 0.05, velocity -1.81 +/- 0.07, from 6 kpc to 170 pc, "no transition or break"; driving scale "at least as large as 6 kpc". Notes Kortgen+2021: the break scale is "not the scale height of the disk but related to it".
- Note: the brief's "Nandakumar & Dutta 2020, THINGS HI, two-slope fits, break scales vs scale height" does not match what I found: the 2020 paper is one galaxy, single slope, no break.

### 2.6 Zhang, Hunter & Elmegreen 2012 (LITTLE THINGS dwarfs)
`[verified: Zhang, Hunter & Elmegreen 2012, ApJ 754, 29, arXiv:1205.3793, abstract, Sect.4, Tab.2, https://arxiv.org/abs/1205.3793]`
- 24 dIrr, 2-D spectra of HI channel and velocity-integrated maps, fits from 1.5 x beam to max scale (0.04-1.31 kpc min, 0.43-9.26 kpc max).
- Velocity-integrated 2-D index from -1.59 (IC 10) to -4.33 (CVnIdwA); channel indices shallower as channels narrow. Single power laws; no break fitted. Text: break slope change "~1" (LMC, Bournaud+2010 sims); beam-scale indices separate around a 200-300 pc beam and an index of -3, read as disc thickness. Low-luminosity dwarfs steeper (line-of-sight depth comparable to radial scale).

### 2.7 Koch et al. 2020 (LMC, SMC, M31, M33; dust, HI, CO)
`[verified: Koch et al. 2020, MNRAS 492, 2663, arXiv:1912.09459, abstract, Sect.3.2 eq.1-2, Tab.1, Tab.3, Sect.3.5, Sect.4, https://arxiv.org/abs/1912.09459]`
- Estimator: azimuthally averaged 2-D spectra ("1D" in their wording), P = A k^-beta + B (point-source term), optional smooth broken law, **PSF forward-modelled**, Tukey taper, MCMC.
- Dust surface density beta (alpha = -beta): LMC 2.18 +/- 0.05 (13 pc), SMC 2.47 +/- 0.15 (13 pc), M31 2.46 +/- 0.14 (167 pc), M33 1.11 +/- 0.14 (167 pc).
- Table 3, single power laws: HI M31 2.66 +/- 0.12 (201 pc), M33 2.18 +/- 0.10 (167 pc); CO 1.59 / 0.91; dust 2.44 / 1.11; total gas (two alpha_CO) 2.34 / 1.66 and 2.11 / 1.36. M33 HI at native 80 pc: 2.30 +/- 0.13, "consistent with Combes et al. (2012)".
- Breaks: only LMC MIPS 24 um prefers a broken law, at 190 pc, attributed to 30 Doradus; local 820 pc boxes show index variations but no breaks; "the spatial power spectrum does not constrain the disc scale height". Apparent breaks below ~3 FWHM are the PSF.

### 2.8 Grisdale et al. 2017 (simulations + THINGS)
`[verified: Grisdale, Agertz, Romeo, Renaud & Read 2017, MNRAS 466, 1093, arXiv:1608.08639, abstract, Sect.3.2.1-3.2.2, https://arxiv.org/abs/1608.08639]`
- Definition: <P(k)> ~ k^-alpha with k = 2 pi / l (l = wavelength), maps normalised by M_HI.
- THINGS (6 galaxies): single power laws "a few 100 pc up to ~10 kpc", exponents 1.6 <~ alpha <~ 2.8 (i.e. -1.6 to -2.8 in this note's sign); steepening below a few 100 pc "always coincide[s] with the resolution limit of THINGS".
- Simulations (4.6 pc AMR, MW/LMC/SMC, with feedback): "all measured HI spectra steepen on small scales, with a break around l_break ~ 100-200 pc ... [which] coincides with the thickness of the HI layer". Kinetic energy E(k) ~ k^-2 below the HI layer thickness.

### 2.9 Kortgen, Pingel & Killerby-Smith 2021 (simulations)
`[verified: Kortgen, Pingel & Killerby-Smith 2021, MNRAS, arXiv:2105.06286, abstract, Sect.3, Fig.3 caption, https://arxiv.org/abs/2105.06286]`
- Isolated galaxy simulations without stellar feedback; spectra per phase.
- Large-scale slopes "around -1 for all phases"; small-scale ~-3.2 (WNM, CNM), -2.67 to -3 (transition gas); example slope change |dgamma| ~ 2.5.
- WNM: scale height ~200-500 pc but break "around a kpc"; MOL: break ~100 pc constantly while scale height grows to ~300 pc. "The break scale almost never traces the disc scale height"; in cold gas it traces cloud sizes.

### 2.10 Burkhart & Lazarian 2012 (column-density variance - Mach number)
`[verified: Burkhart & Lazarian 2012, ApJL 755, L19, arXiv:1205.3792, abstract, eq.1-4, Tab.1, Sect.3, https://arxiv.org/abs/1205.3792]`
- Definition: zeta = ln(Sigma/Sigma0); sigma^2_zeta = A ln(1 + b^2 Ms^2) (eq.3); linear form sigma^2_(Sigma/Sigma0) = (b^2 Ms^2 + 1)^A - 1 (eq.4). With b fixed at 1/3, best fit **A = 0.11**.
- Simulations: isothermal ideal MHD, **solenoidal** driving at large scales, periodic box, 512^3 and 256^3; Ms,rms 0.4-8.8, MA 0.5-3.2 (Table 1); column maps along the box (line of sight = box size). Smoothing lowers sigma^2.
- Observational fits: Taurus b = 0.5, A = 0.16; IC 5146 b = 0.5, A = 0.12 (molecular clouds, Milky Way).
- Coverage: no galactic disc geometry. Yoon & Cho 2024 state BL12 is a case of few eddies along the line of sight, N <~ 2.5.

### 2.11 Federrath, Klessen & Schmidt 2008; Federrath et al. 2010
- `[verified: Federrath, Klessen & Schmidt 2008, ApJL 688, L79, arXiv:0808.0605, eq.2-5, Fig.3, https://arxiv.org/abs/0808.0605]` sigma_s = [ln(1 + b^2 M^2)]^1/2 for s = ln(rho/rho0) (eq.4, from PNJ97 under a log-normal); b = 1 + (1/D - 1) zeta (eq.5): b ~ 1/3 for 3-D solenoidal, ~1/2 for 2-D solenoidal, ~1 compressive. Measured b ~ 0.36 (solenoidal), ~1.05 (compressive). PNJ97 (MHD) b ~ 0.5; other hydro studies 0.26-0.37.
- `[verified: Federrath et al. 2010, A&A 512, A81, arXiv:0905.1060, Tab.1, Tab.3, Sect.3.5, https://arxiv.org/abs/0905.1060]` RMS Mach ~5.5. Volume: sigma_s 1.32 +/- 0.06 (sol.), 3.04 +/- 0.24 (comp.). Column: sigma_eta (eta = ln Sigma/<Sigma>) 0.46 +/- 0.06 (sol.), 1.51 +/- 0.28 (comp.); "column density dispersions become smaller" because fluctuations average along the line of sight. **(derived)** sigma^2_eta / sigma^2_s = 0.12 (sol.), 0.25 (comp.).

### 2.12 Yoon & Cho 2024 (2-D vs 3-D variance)
`[verified: Yoon & Cho 2024, arXiv:2406.17022, abstract, Sect.1, eq.2-3, eq.14-15, https://arxiv.org/abs/2406.17022]`
- sigma^2_(Sigma/Sigma0) / sigma^2_(rho/rho0) = R (Brunt factor) and R ~ 1/N, N = number of independent eddies along the line of sight (~ L/L_f); holds for elongated (L_los != L_perp) geometry when written in N. Linear (not logarithmic) variances. The m-dependent prefactor of eq.14-15 did not extract cleanly from the PDF text, so I do not quote it.

### 2.13 Measured column-density PDFs in galaxies
- `[verified: Berkhuijsen & Fletcher 2015, MNRAS 448, 2469, arXiv:1501.07769, Sect.2, eq.1-2, Fig.1, Fig.2, Sect.3.1, Sect.4, https://arxiv.org/abs/1501.07769]` sigma = std of **log10**. M31 (i = 77.5 deg; maps at 45'' = 170 x 785 pc; independent points above 2 rms): HI disp = 0.27 (0 < R < 13.6 kpc), inner 0.23 +/- 0.01, bright ring 0.19 +/- 0.01; H2 0.41; Halpha 0.34. M51 (i = 20 deg; 8'' = 295 x 315 pc; R < 3'): HI 0.51, H2 0.64, Halpha 0.59. Whole-region PDFs include radial gradients (low-density excess). sigma falls with line-of-sight length L as L^(-0.76 +/- 0.06) (abstract). **(derived)** in natural log: M31 HI 0.44-0.62, M51 HI 1.17, M51 H2 1.47.
- `[verified: Hughes et al. 2013, ApJ 779, 44, arXiv:1304.1219, eq.3, Tab.1, Sect.4.1, Sect.6, https://arxiv.org/abs/1304.1219]` CO only (PAWS, 40 pc; 53 pc combined cube). Fit P(s) = c0 exp[-(log s - log s0)^2 / 2x^2]; x quoted in dex. I(CO) whole field x = 0.44; environments 0.21 (bar) to 0.47 (ring, A1I); interarm "up" 0.25, "down" 0.22; M51 at lower resolution 0.53; LMC 0.26 (also "x = 0.3"). Quotes PNJ97 as x^2 ~ ln(1 + 0.25 M^2).
- `[verified: Sun et al. 2018, ApJ 860, 172, arXiv:1805.00937, Tab.4, Sect.5.1.2, https://arxiv.org/abs/1805.00937]` molecular Sigma (CO) on CO-detected sightlines, mass-weighted; **full** 16-84% width of the disc distribution "typically 0.55-1.10 dex"; Table 4 values 0.52 (NGC 5068, 45 pc) to 1.18 (Antennae, 120 pc); M31 0.65-0.68, M33 0.73-0.76, M51 0.77-0.84. **(derived)** half-width (~1 sigma if log-normal) 0.26-0.59 dex.
- `[verified: Corbelli, Elmegreen, Braine & Thilker 2018, A&A 617, A125, arXiv:1807.00166, abstract, Sect.3.2, https://arxiv.org/abs/1807.00166]` M33 at ~50 pc: total-gas PDFs log-normal with width decreasing outward while the HI dispersion stays flat, read as a falling Mach number (order unity) as warm HI takes over. **No numerical widths in the text** (only in figures, not read).

### 2.14 Elmegreen & Scalo 2004 (review): 2-D vs 3-D slopes
`[verified: Elmegreen & Scalo 2004, ARA&A 42, 211, arXiv:astro-ph/0404451, Sect.2.1 (pp.5-6, 9), https://arxiv.org/abs/astro-ph/0404451]`
- Convention E(k) dk = P(k) d^D k. Kolmogorov 3-D P ~ k^-11/3; 2-D k^-8/3; 1-D k^-5/3.
- Milky Way HI, HI absorption, CO, IRAS 100 um 2-D maps: slopes -2.8 to -3.2; same for SMC/LMC HI.
- "the power spectrum of projected emission from a slab that is thinner than the inverse wave number is shallower than the 3D density spectrum by one (Goldman 2000, Lazarian et al. 2001)".
- **So, as read:** for a 3-D density spectrum k^-beta, the 2-D projected map shows **k^-beta at scales smaller than the thickness** and **k^-(beta-1) at scales larger than the thickness**. This is the reverse of the brief's guess ("-beta above the thickness, -(beta-1) below"). Every observational source (EKS01, Block, Combes, Dutta 2009, Zhang) agrees: steeper below the break, shallower above.

---

### 3. Conflicts, side by side (not reconciled)

**C1. Does the break exist and does it mark the thickness?**

| Says yes | Says no / not shown |
|---|---|
| EKS01: LMC HI break at 80-100 pc wavelength, growing with radius (flaring) | Koch+2020: with PSF forward-modelled, LMC/SMC/M31/M33 dust and M31/M33 HI, CO single power laws; the only break (LMC 24 um, 190 pc) is 30 Dor |
| Block+2010: LMC FIR break 1/k ~ 100-200 pc | Grisdale+2017: THINGS breaks coincide with the beam |
| Combes+2012: M33 breaks 93-390 pc (HI 110 pc, called ambiguous) | Kortgen+2021 (no-feedback sims): break "almost never" traces the scale height; WNM break ~1 kpc vs h 200-500 pc |
| Dutta+2009: NGC 1058 break 1.5 kpc -> z_h 490 pc | Dutta+2013 (18 THINGS), N&D 2020 (to 300 pc), N&D 2023 (to 170 pc), Zhang+2012 (24 dwarfs): single power laws |
| Grisdale+2017 sims with feedback: break 100-200 pc = HI layer thickness | Koch+2020: M33 HI at native 80 pc gives 2.30 single slope, "consistent with Combes" |

**C2. Break length vs thickness (the factor).** Dutta+2009: break length = pi z_h (z_h = scale height). EKS01: break wavelength ~ line-of-sight thickness (80-100 pc), compared with scale heights of 95-350 pc and a structured layer ~50 pc. Combes+2012 sims: break / H_z (H_z = 2.35 sigma_z) from 0.5 (run4: 63/120) to 3 (run3: 650/217) **(derived ratios)**. Block+2010 and Combes+2012 do not say whether their "scale" is 1/k or 2pi/k; Grisdale+2017 states k = 2pi/l.

**C3. Large-scale slope magnitude.** THINGS intensity spectra (visibility estimator, ~0.3-16 kpc): mostly -1.5 to -1.9, mean -1.3. Grisdale's image-based re-fit of THINGS: -1.6 to -2.8. Local Group image spectra at 13-200 pc: HI -2.2 to -2.7 (M31, M33, LMC). Column-density visibility spectra: -0.96 (NGC 6946), -1.23 (NGC 5236). Kortgen sims: ~-1.

**C4. M33 HI:** Combes LS -2.4 / ss -3.2 with break 110 pc (48 pc beam, no PSF model) vs Koch 2.18 single at 167 pc, 2.30 at 80 pc (PSF modelled, lowest-k bins excluded).

**C5. Width-Mach coefficients:** BL12 A = 0.11 with b = 1/3 (solenoidal sims) vs A = 0.12-0.16 with b = 0.5 (Taurus, IC 5146 fits); Federrath 2010 column sigma_ln 0.46 vs 1.51 at the same Mach 5.5 (forcing). PNJ97 coefficient: b ~ 0.5 (as quoted by Federrath 2008 and by Hughes 2013, x^2 ~ ln(1 + 0.25 M^2)) vs EKS01's 0.5 M^2 inside the log (b ~ 0.71) inferred from Nordlund & Padoan 1999.

**C6. Measured widths:** HI M31 0.19-0.27 dex at ~170 x 785 pc vs M51 0.51 dex at ~300 pc; molecular 0.21-0.64 dex (various) vs PHANGS full 16-84% widths 0.52-1.18 dex. The resolutions, masks (above 2-3 rms, CO-detected only) and the inclusion of radial gradients all differ.

---

### 4. What could not be read

- **Padoan, Nordlund & Jones 1997** (MNRAS 288, 145): not fetched; its coefficient is only known through Federrath+2008 and Hughes+2013 (secondary).
- **Koch et al. 2019 (M33 column-density PDFs/widths)**: not found under that description; Corbelli+2018 used instead, and it gives widths only in figures (not read numerically).
- **Sun et al. 2020 (PHANGS)**: not read; Sun+2018 used.
- **Schneider et al. (Galactic PDFs)**: not read (extragalactic widths were found).
- **Dutta et al. 2009b** (the simulation that gives U = D/(pi z_h)): not read; the relation is quoted from the NGC 1058 letter.
- **Lazarian & Pogosyan 2000, Goldman 2000, Padoan et al. 2001 (LMC SCF thickness 130-280 pc), Szotkowski et al. 2019, Bournaud et al. 2010, Federrath et al. 2009**: not read directly; only as cited inside the sources above.
- **Nandakumar & Dutta 2020 as described in the brief** (THINGS, two-slope fits, breaks vs scale height): no such paper found; the 2020 paper found is NGC 5236 only.
- Corbelli+2018 and EKS01 figure values; Grisdale's per-galaxy slopes (figure legends only, galaxy labels not attached in the extracted text).
- Yoon & Cho 2024 eq.14-15 prefactor (garbled in extraction).

---

### 5. Recommendation (named alternatives; the lead rules)

**(1) Spectral slope (2-D, above the thickness, i.e. for the octaves larger than the disc's thickness).**
- A model could adopt **alpha = -1.6** (Dutta+2013 THINGS, Tab.2: half the sample -1.9 to -1.5; also NGC 628 -1.6 in Dutta+2008 and Dutta & Bharadwaj 2013; Block+2010 abstract -1.6 for LMC dust) - spirals at kpc scales, HI intensity.
- or **alpha = -1.2** (Nandakumar & Dutta 2020: NGC 5236 HI column density -1.23 over 0.3-11 kpc; NGC 6946 -0.96) - the only true column-density spectra, single galaxies.
- or **alpha = -2.4** (Combes+2012 M33 HI LS; Block+2010 citing EKS01 LMC HI 2-D ~-2.7; Koch+2020 M31/M33 HI -2.66/-2.18) - Local Group, resolved to tens of pc.
- or a per-galaxy draw from the THINGS distribution (mean -1.3, s.d. 0.5, Dutta+2013).

**Below the thickness**, a model could adopt **alpha_small = alpha - 1** (EKS01, Block+2010 intro, Zhang+2012, Elmegreen & Scalo 2004: "shallower ... by one" above the thickness), or the measured small-scale values directly, **alpha_small = -3.2** (M33 HI, Combes+2012) / **-2.8 to -3.2** (Milky Way maps, Elmegreen & Scalo 2004), or **-2.5** (NGC 1058, Dutta+2009). Note again: steeper at small scale, not the other way.

**(2) Break at the disc thickness.**
- A model could put the break at **lambda_break = pi * h** (Dutta+2009, U = D/(pi z_h), h the gas scale height), or at **lambda_break ~ thickness ~ h to 2h** (EKS01, LMC: 80-100 pc wavelength vs scale height ~95-180 pc; Grisdale+2017 sims: 100-200 pc = HI layer thickness), or at **lambda_break = 1/k ~ 100-200 pc fixed** (Block+2010; Combes+2012 HI 110 pc).
- or **no break** (Koch+2020: none once the PSF is modelled; Kortgen+2021: break almost never tracks the scale height; THINGS and N&D 2020/2023 single laws to 170-300 pc) - one slope through all octaves.
- The model's octaves (190, 95, 47.5 pc, then finer) straddle the LMC/M33 break values (80-200 pc) and fall well below the NGC 1058 one (1.5 kpc); which of these the per-ring h produces depends on the factor chosen above.

**(3) Log-normal width vs Mach number (column density).**
- A model could adopt **sigma^2_ln Sigma = 0.11 ln(1 + Ms^2/9)** (Burkhart & Lazarian 2012, A = 0.11, b = 1/3, solenoidal MHD, Ms 0.4-8.8). **(derived)** sigma_ln = 0.11 at Ms = 1, 0.28 at Ms = 3, 0.52 at Ms = 10.
- or **A = 0.16, b = 0.5** (BL12's Taurus fit) or **A = 0.12, b = 0.5** (IC 5146). **(derived)** A = 0.16, b = 0.5, Ms = 10: sigma_ln = 0.72.
- or the 3-D relation **sigma_s^2 = ln(1 + b^2 M^2)** (Federrath+2008; b = 1/3 to 1) reduced by the line-of-sight averaging **sigma^2_2D / sigma^2_3D ~ 1/N** (Yoon & Cho 2024), with N the number of eddies through the layer - this ties the width to the scale height the model already has; or reduced by the measured ratio 0.12-0.25 (Federrath+2010 Tab.1/Tab.3, derived).
- or calibrate to measured galaxy widths instead of a Mach law: **HI 0.19-0.27 dex** (M31, Berkhuijsen & Fletcher 2015) to **0.51 dex** (M51), **molecular ~0.3-0.6 dex** (Hughes+2013 x 0.21-0.47; Sun+2018 half-widths 0.26-0.59, derived). Caution: these include beam smoothing (~50-800 pc), masks and radial gradients, and they are per-galaxy, not per-cell.

**(4) Outer scale.**
- A model could adopt **no flattening inside the disc** (Dutta+2013: power laws to R/r25 ~ 1-2, up to 15.8 kpc; N&D 2020: column power law to 11 kpc; Dutta+2009: to 10 kpc), which for the L2 field (finer than the 190 pc octave) means the outer scale lies outside its band and need not be modelled;
- or **L_out ~ 6 kpc** (Nandakumar & Dutta 2020: "energy input scale" from the velocity spectrum's extent and a Jeans scale ~4.5 kpc; N&D 2023: "at least as large as 6 kpc") - an inference, not a measured turnover of the column spectrum.
