# READING_ARM_PIECES — a single arm as measured, and what a disc's thickness does to its force (S60, BUILD_III Phase P5)

**The lead's note (2026-10-05).** Two Opus readers, briefed by BUILD_III §3e and forbidden the repository, wrote
Parts A and B below; each is entered as returned, its headings one level down. Both read the papers' PDFs as
text they converted themselves (the fetch tool saved the files and returned none of their text), so `[verified]`
means read in that text; what only the fetch tool's summarising model showed is marked as such. One correction
to the lead's brief, the reader's: Savchenko et al. 2020 is 155 SDSS galaxies in gri; the 29 galaxies at 3.6 µm
are Chugunov et al. 2024.

**What the readings say that Phase P5's text did not foresee** (the lead's summary; the parts below are the record).
(1) *An arm in old starlight is broad*: FWHM about half a scale length (0.12 r25), growing with radius; in
azimuth 20°–70° at ordinary pitches. Young tracers are half that or less (maser arms σ = 0.34 kpc at the Sun).
The narrow bright arms of a picture are the young stars' and the gas's, not the stellar mass's. (2) *Counts and
lengths are measured for grand designs and multi-armed discs* (2.8 and 3.5 arms of 90° or more, plus 1.4 shorter
features; mean length 273° and 244°) *and not for flocculent ones*: no source read gives the number or the
lengths of a flocculent disc's pieces, and only about 15 % of them show any underlying two-armed pattern.
(3) *Not measured anywhere read*: where arms branch, what share start at a bar's end, how unequal a galaxy's arms
are in amplitude, a taper length. (4) *The thickness factor is settled for one case and not for the mapping*:
for stars in an exponential layer the midplane force on thin gas is reduced by exactly 1/(1 + k h); for a sech²
layer the exact form is printed and a fit is good to 1.4 %; which of them an observed scale height stands for
moves the factor between 0.39 and 0.57 at k h = 1. (5) *No source converts a stellar arm's amplitude to a forcing
with thickness, and none gives the gas's response to a narrow arm that corotates*: the simulations impose the
force.

---

## Part A — a single spiral arm as measured

## Reading P5 - a single spiral arm as measured in stellar discs (notes)

Read 2026-10-05, blind to the repository. Texts were read from the papers' PDFs converted locally (pdftotext; working
copies in `p5txt/`). Tags: [verified: ...] = passage read this session; [fetch-quote] = shown only by the fetch tool's
summarising model; [inferred: ...] = my arithmetic; [not read] = cited by a paper I read, the original not opened.

### 0. Nothing readable found (or only second-hand)

- Thornley 1996 (ApJ 469, L45), Thornley & Mundy 1997 (NGC 5055: ApJ 484, 202; NGC 4414: ApJ 490, 682): NOT READ. The
  ADS copies are image scans without a text layer; the publisher's pages sit behind a bot wall. Their numbers appear
  below only as quoted by Elmegreen et al. 1999 and Elmegreen et al. 2011.
- Elmegreen & Elmegreen 1982, 1984, 1987, 1995; Elmegreen, Elmegreen & Montenegro 1992: NOT READ (image scans). The 1995
  result is known to me only from a search summary of its abstract.
- Bifurcations / branches, and arms from the bar's ends versus from a ring: NO measured statistic in any text read.
- A length distribution of flocculent arm pieces, and the number of pieces in a flocculent disc: NOT measured in
  anything read. Only the azimuthal span of weak two-armed K' structure in four galaxies, and NGC 4414's catalogue rows.
- Davis & Hayes 2014 (SpArcFiRe, arXiv:1402.1910): the arXiv text read prints no distribution of arc number or arc
  length and no "fraction in the longest arcs"; one worked example only.
- Bittner et al. 2017: arm contrasts by class are a figure (Fig. 11) and t-tests; no class medians in the text.
- Arm width as a fraction of the arm-to-arm spacing: printed nowhere; inferable only from an azimuthal FWHM in degrees.
- Yu et al. 2018 (CGS VI): abstract only (PDF over the fetch limit). Yu & Ho 2020: not located on arXiv. Mosenkov et
  al. 2020 with arms: not identified. Smith et al. 2022: not read (Stuber et al. 2023, PHANGS CO morphology, read
  instead). Savchenko & Reshetnikov 2013: abstract only.
- A correction to the brief: Savchenko et al. 2020 (MNRAS 493, 390; arXiv:2001.09110) is 155 SDSS galaxies in g, r, i
  (optical), not 29. The 29-galaxy 3.6 um sample is Chugunov et al. 2024 (arXiv:2311.01848).

### 1. Arm width across the arm

#### 1a. Old starlight / optical continuum

Savchenko, Marchuk, Mosenkov & Grishunin 2020 - 155 face-on SDSS spirals, g r i, de-projected; arms traced by hand, cut
perpendicular to the ridge; each cut fitted (PSF-convolved) with a lopsided Gaussian I0 exp(-(r-rpeak)^2/w1^2) on the
inner side and w2 on the outer; "width" w = w1 + w2.
- Mean width (0.14 +/- 0.05) r25; in kpc 3.3 +/- 1.2 (grand design), 2.5 +/- 0.9 (multi-armed), 2.1 +/- 1.4
  (flocculent) [verified: Savchenko 2020, Sect. 4.3]. In r25 units by class: G 0.16 +/- 0.04, M 0.13 +/- 0.04,
  F 0.12 +/- 0.04 [verified: Fig. 16 legend].
- This w is the full 1/e width, 2*sqrt(2)*sigma for a symmetric Gaussian; a FWHM is 0.83 w [inferred from eq. 1;
  Chugunov 2025 Sect. 3.3 says the same, "nearly 17% smaller"]. So the mean is a FWHM of about 0.12 r25, and about
  2.7 / 2.1 / 1.7 kpc for G / M / F [inferred].
- Width against radius: 85.8% of galaxies have a positive slope a (kpc of width per kpc of radius) [verified: Sect.
  4.3; the abstract says 86%]. By class, r band: G 0.15 +/- 0.10, M 0.10 +/- 0.16, F 0.17 +/- 0.13 [verified: Fig. 17
  legend]. Extremes named: -0.30, -0.18, +0.78 [verified: Sect. 4.3]. Chugunov 2025 quotes the sample's median slope
  as 0.12 [verified as a quotation: Chugunov 2025, Sect. 3.3].
- Asymmetry A = (w2 - w1)/w2: mean 0.14 +/- 0.23, 75.3% of galaxies positive, i.e. the inner (concave) side is the
  steeper, the outer half-width about 16% larger; G 0.16 +/- 0.18, M 0.14 +/- 0.22, F 0.15 +/- 0.27, no difference
  between classes [verified: Sect. 3.3 eq. 2, Sect. 4.3, Fig. 18].
- Reduced chi2 of the asymmetric Gaussian 1.07 (r) to 1.13 (i) [verified: Sect. 4.1].
- Caveats printed: flocculents under-counted (5 of the 67 "stage 2" galaxies; galaxies with no traceable arm dropped);
  arms splitting into equal branches discarded; galaxies larger than 50 arcsec, PSF FWHM about 1.3-1.4 arcsec, a
  typical arm at the size limit 3.5 arcsec = 2.7 PSF widths; dust not corrected [verified: Sect. 2.1, 3.2, 3.3, 5.1].

Chugunov et al. 2024 - 29 S4G galaxies (grand design and multi-armed only, low inclination, picked by eye for
prominent arms), 3.6 um, 2-D decomposition with each arm its own component; width = FWHM of a radial slice at mid-arm.
- w = (0.53 +/- 0.04) h = (0.12 +/- 0.01) r25 on average, h the disc scale length [verified: Chugunov 2024, Sect.
  6.3, Fig. 12; abstract]. Per galaxy <w>/h runs 0.24 to 1.18 [verified: Table 4, col. 3].
- Arms widen outward: width at the beginning is 74% of the width at the end (Sect. 6.3); the conclusions say 73%
  [verified: both passages].
- Asymmetry (w_out - w_in)/w: mean -0.05, about 2/3 of galaxies negative, i.e. the INNER side slightly more extended
  [verified: Sect. 6.3, Fig. 13]. CONFLICT with Savchenko 2020 (+0.14, inner side steeper).
- Scatter of arm widths inside one galaxy sigma_w/<w>: 23% on average; 10% for two-armed galaxies, 37% for the others
  [verified: Sect. 6.3]. The model cannot represent the outer narrowing Honig & Reid found [verified: Sect. 6.3].

Chugunov, Marchuk & Savchenko 2025 (arXiv:2504.11642) - 19 S4G galaxies (13 multi-armed, 6 grand design, no
flocculents), 3.6 um corrected for non-stellar emission (a stellar-mass map), plus GALEX FUV; radial slices, Gaussian
fits; width = FWHM measured RADIALLY (perpendicular width = cos(pitch) times that, 0.94 at 20 deg) [verified: 2.1, 3.3].
- Width is linear in radius, w = w1 r + w0. Long arms (azimuthal length >= 180 deg), disc removed as the 0.1 quantile
  at each radius: median w1 = 0.30 (same for grand design and multi-armed), median zero-point share |w0|/w(r_avg) =
  19%, median w_avg/r_avg = 0.37 (G 0.36, M 0.39). Including short arms: w1 = 0.28, share 35% [verified: Sect. 3.3].
- Same arms with the decomposition disc removed instead: median w1 = 0.19, share 34%, w_avg/r_avg = 0.29 [verified:
  Sect. 3.3]. The measured width depends on how the disc is subtracted.
- FUV arms: w1 = 0.14, share 39% [verified: Sect. 3.3]. The young tracer is about half as wide.
- 88% (0.1-quantile disc) or 82% (decomposition disc) of all features widen outward [verified: Sect. 3.3]. Linear in
  radius fits slightly better than linear or exponential in azimuth (median chi2 8.8 vs 9.7 and 9.5); forcing constant
  width costs "a few percent" in chi2, forcing w0 = 0 only 1-2% [verified: Sect. 3.3, 4.1].
- Shape: Sersic index of the cross-arm profile (0.5 = Gaussian, 1 = exponential): median n = 0.67 (0.1-quantile disc)
  or 0.59 (decomposition disc), most arms 0.4 < n < 0.9. Skewness: "a large scatter around zero"; skewness and n
  together lower chi2 by only 2-3% [verified: Sect. 3.4, 4.1]. Ridge scatter rms sigma_r/w = 0.16 +/- 0.06 [3.1.2].

Marchuk et al. 2024 (arXiv:2402.08531) - M51 alone, 17 bands, ALL images degraded to 18 arcsec FWHM, same model.
- FWHM "around 1.5-2 kpc"; at 3.6 um 42.5 +/- 5.8 and 41.0 +/- 0.6 arcsec for the two arms; optical 46-48 arcsec; FUV
  40.5 and 44.0 arcsec; at original resolution "20% larger in the optical bands". Widest in the optical/NIR, a drop at
  8-24 um, a second peak in the FIR [verified: Marchuk 2024, Sect. 6.3.4, Table 4, conclusions (v)].
- No widening with radius in M51 (the widening parameter is 0 in every band and arm) [verified: Sect. 6.3.4].
  CONFLICT with Honig & Reid, whose M51 HII widths rise from 0.07 to 0.46 kpc.

Seigar & James 1998 (paper II, astro-ph/9803254) - 45 face-on spirals, K band; arms sheared straight in (theta, ln r)
and collapsed; width = FWHM of the cross-section in AZIMUTH.
- FWHM between 10 and 70 deg, "typical values in the range 20-40 deg"; error < 10% [verified: Seigar & James 1998,
  Sect. 4.1.2, referring to Table 1 col. 6]. As a fraction of a two-armed spacing of 180 deg: 0.11-0.22 [inferred].
  They call this narrower than the 60 deg of a sinusoidal two-armed wave [verified: Sect. 4.1.2].
- Cross-sections of strong arms asymmetric "at only the 5-10% level"; of the less strongly armed about 25% [verified:
  Sect. 4.1.2]. B-band arms are "much smaller" in FWHM than K-band arms and lead them by about 5 deg at small radii,
  tens of degrees at large radii [verified: Sect. 5; three galaxies with B images].
- CONFLICT (not reconciled): 20-40 deg in azimuth at a pitch of 15-20 deg is a radial width of 0.09-0.25 r [inferred:
  r * dtheta * tan(pitch)]; Chugunov 2025 measures 0.29-0.37 r radially.

#### 1b. Young tracers

Honig & Reid 2015 (ApJ 800, 53; arXiv:1412.1012) - HII regions in NGC 628, 1232, 3184, 5194; width = Gaussian 1-sigma
scatter of HII regions about a log-spiral fitted per segment (segments chosen 5-10 kpc long).
- Segment widths sigma in kpc @ mean radius in kpc [verified: Tables 2-5]:
  NGC 628 A: 0.14 @2.58, 0.34 @5.60, 0.42 @7.31; B: 0.27 @5.75, 0.46 @7.57, 0.87 @10.38, 0.59 @12.02.
  NGC 1232 A: 0.16 @3.33, 0.52 @5.01, 0.51 @5.98; B: 0.10 @2.63, 0.24 @3.49, 0.33 @5.46, 0.46 @7.64; C: 0.12 @4.38,
  0.27 @5.82; D: 0.16 @9.87; E: 0.24 @11.38, 0.14 @12.83; F: 0.65 @16.23.
  NGC 3184 A: 0.19 @1.43, 0.32 @2.79, 0.47 @3.91; B: 0.07 @1.09, 0.24 @2.57, 0.42 @3.95.
  NGC 5194 A: 0.07 @1.90, 0.18 @3.29, 0.26 @5.40, 0.31 @6.45, 0.23 @6.08; B: 0.14 @2.50, 0.20 @3.42, 0.28 @5.39,
  0.37 @6.70, 0.43 @7.11, 0.46 @7.05, 0.22 @9.72.
- sigma/R: 0.05-0.08 along NGC 628's arms; over all 38 segments median 0.055, range 0.01-0.13; a FWHM (2.355 sigma) is
  then about 0.13 R at the median [inferred from the rows].
- All major arms widen outward; the last segment narrows in NGC 628 B, NGC 1232 E, NGC 5194 A and B [verified: Sect.
  5.2]. No fitted slope is printed (trend lines in Fig. 10 only).
- "spiral arms often appear to be composed of segments of ~5 kpc length, which join to form kinks and abrupt changes
  in pitch angle and arm width" [verified: abstract].

Reid et al. 2019 (arXiv:1910.03357) - Milky Way, masers of high-mass star-forming regions with parallaxes; width =
Gaussian 1-sigma in the plane, averaged per arm segment.
- w(R) = 336 + 36 (R[kpc] - 8.15) pc [verified: Reid 2019, Sect. 3 text and Fig. 4 caption]. The arm fits themselves
  adopted dw/dR = 42 pc/kpc from Reid et al. 2014 [verified: Sect. 3]. sigma/R = 0.041 at R0; FWHM 0.79 kpc [inferred].

Silva-Villa & Cano Gomez 2022 (MNRAS 514, L22; arXiv:2205.00010) - NGC 5236 (M83), resolved upper-main-sequence stars,
the two main arms, boxes 1.3 x 0.3 kpc.
- Mean width 0.59 kpc (1-sigma method), 0.60 kpc (stellar-density method); slope against radius 0.04 +/- 0.02 and
  0.05 +/- 0.02 (two arms), fitted over R = 2.5-3.5 kpc only [verified: Sect. 3]. Widths were capped at 1.3 kpc each
  side by construction [verified: Sect. 2]. Kennicutt & Hodge 1982: perpendicular arm width in M51 from HII regions
  17 arcsec [not read; quoted in Marchuk 2024, Sect. 6.3.4].

### 2. Arm amplitude

Elmegreen et al. 2011 (ApJ 737, 32; arXiv:1106.4840) - 46 S4G galaxies, 3.6 um, de-projected azimuthal scans every
0.05 R25, point sources avoided; contrast A(r) = 2.5 log[2 I_arm/(I_ia1 + I_ia2)] in mag, averaged over the disc beyond
any bar; errors about 0.1 mag.
- Disc-averaged contrast: grand design 1.14 +/- 0.44, multiple arm 0.81 +/- 0.28, flocculent 0.75 +/- 0.35 mag
  [verified: Sect. 4.2]. As intensity ratios 2.9, 2.1, 2.0 [inferred].
- For the 16 galaxies also measured in B and I, at one matched radius each: all 0.93 +/- 0.32 (B), 0.81 +/- 0.49 (I),
  0.99 +/- 0.46 (3.6); multiple arm + grand design 1.04, 0.99, 1.17; flocculent 0.63 +/- 0.24 (B), 0.34 +/- 0.18 (I),
  0.44 +/- 0.13 (3.6) [verified: Sect. 4.2, referring to Table 3]. NOTE two flocculent values in one paper: 0.75
  (disc average, all F) and 0.44 (the subset, one radius).
- Fourier: the relative amplitude of an arm is twice their component F_m. Average F2 in the arms: SA 0.15 +/- 0.042,
  SAB 0.26 +/- 0.12, SB 0.34 +/- 0.14; contrast SA 0.69, SAB 0.94 +/- 0.33, SB 0.94 +/- 0.44 mag [verified: Sect.
  4.7]. m = 4 "about half" of m = 2 in all cases; F3/F2 = 0.58 +/- 0.11 (F), 0.48 +/- 0.24 (M), 0.33 +/- 0.19 (G)
  [verified: Sect. 4.3]. The two-fold symmetric image holds 80-85% of the light, the asymmetric part 15-20% [4.1].
- Radial run: "Some spirals peak at mid-radius while others continuously rise or fall"; early-type barred: contrast
  falls outward from the bar's end; late-type barred: constant or rising [verified: abstract, Sect. 5]. Arms measured
  "often out to ~1.5 R25" [verified: Sect. 4.2].
- NGC 4321: arm strength modulated by 50-100%, peaks near 0.25 and 0.45 R25 and near the arm ends [verified: 4.4].
- Sharp outer edges in NGC 4321, NGC 5194 (near 0.5 R25) and NGC 1566: the drop is roughly exponential, "about twice
  as steep as the local disk" [verified: Sect. 4.6].

Kendall, Clarke & Kennicutt 2015 (arXiv:1411.5792) - 13 SINGS galaxies with a traceable m = 2 spiral; m = 2 Fourier
amplitude relative to the axisymmetric (disc + bulge) light, averaged over the radii where a log spiral is traced.
- 3.6 um: NGC 628 0.198, 1566 0.284, 2403 0.119, 2841 0.069, 3031 0.224, 3184 0.282, 3198 0.213, 3938 0.093, 4321
  0.327, 4579 0.188, 5194 0.416, 6946 0.214, 7793 0.071 [verified: Table 2]. Median 0.213 [inferred]. Optical
  0.085-0.299 [verified: Table 2].
- Amplitude follows Elmegreen arm class and tidal forcing, weakly mass and rotation speed [verified: abstract, Sect.
  2.1.1-2.1.2]. Its literature summary: optical arm/interarm 20-100%, later "40 to 50 per cent" at most [Sect. 1].
- Kendall et al. 2011 (arXiv:1101.5764): a two-armed pattern in "approximately half" of 31 SINGS galaxies (13 are
  "non-grand design"); those have power in m = 1, 3, 4 similar to m = 2 [verified: Kendall 2011 abstract, Sect. 3;
  Kendall 2015 Sect. 2.1].

Diaz-Garcia et al. 2019 (A&A 631, A94; arXiv:1908.04246) - 391 S4G galaxies, 3.6 um; m = 2 amplitude A2 = I2/I0, the
maximum over each measured segment's radial range, averaged per galaxy [verified: Sect. 4.2, Table A.1 notes].
- By class, from my parse of 367 of the 391 rows of Table A.1: median A2 = 0.44 (G, n = 73), 0.31 (M, n = 152), 0.31
  (F, n = 141); 16th-84th percentiles 0.21-0.66, 0.20-0.46, 0.21-0.47 [inferred: own tabulation of the printed table;
  the paper prints no class means]. These flocculents are mostly late-type and barred (77%).
- Spiral amplitude correlates with bar strength in all three classes [verified: Sect. 7.2].

Fraction of light in arms
- r band, 67 galaxies with a full arm mask: arms-to-total 0.17 +/- 0.07; G 0.21 +/- 0.07, M 0.14 +/- 0.05, F 0.13 +/-
  0.04 (5 galaxies); up to 0.4-0.5 in some grand designs; largest in g, falling to i; rises with Hubble type for
  grand designs (r = 0.66) [verified: Savchenko 2020, Sect. 4.4, Fig. 19, conclusions (iv)].
- 3.6 um: S/T "between 10% and 25%" for most, above 45% in exceptional cases; per galaxy 0.08-0.46 [verified:
  Chugunov 2024, Sect. 6.1, Table 4]; median 0.21, mean 0.23 [inferred from Table 4's 29 values].
- M51 per arm: 0.16 and 0.14 at 3.6 um, 0.29 and 0.30 in FUV [verified: Marchuk 2024, Table 4]; in the azimuthal
  profile the arms hold 0.5-0.8 of the light on a plateau from 2 to 4 arcmin [verified: Sect. 6.3.3].

Along the arm and at its ends
- The arms' share of the azimuthally averaged profile peaks "at a distance of 1-2 disc radial scale lengths", goes
  to zero at the centre and outside; peak share / (S/T) mostly 1.5-2.5; the bump on the profile is 0.3-0.7 mag; arms
  end at r_end "usually between 0.5 and 0.7" r25 with a wide range; in almost all galaxies the arms are truncated
  inside the disc [verified: Chugunov 2024, Sect. 6.5, Fig. 17, 20, conclusions (vii)]. Arm radial scale over disc
  scale <h_s>/h: 0.09 to 7.58 per galaxy [verified: Table 4].
- The radial brightness profile along an arm is "far from exponential in many cases"; dropping the exponential term
  raises chi2 by only 1-3%, while sharp ends (no growth or cutoff zone) raise it by more than 10%; Gaussian and cubic
  tapers fit equally (0.5% apart). At least one brightness dip in 24% of arms (35% in grand designs, 20% in
  multi-armed, p = 0.21); adding dips lowers chi2 by 17-18% [verified: Chugunov 2025, Sect. 3.2, 4.1, 4.2].
- Arm strength (K band) rises at small radii, turns over and falls; of 16 galaxies with long strong arms 4 show clear
  modulation, 6 some [verified: Seigar & James 1998, Sect. 4.2]. PGC 2182's arms are roughly exponential in radius
  [verified: Savchenko 2020, Sect. 3.3].
- M51: arm radial scales at 3.6 um 53.6 and 122.2 arcsec, 0.76 and 1.72 of the disc's [verified: Marchuk 2024, Table 4].

### 3. Number, length, classes

Arm classes - the three-way grouping of the 1-12 scale is printed differently:
- F = 1-3, M = 4-9, G = 10-12 [verified: Elmegreen 2011, Sect. 3]. F = 1-4, M = 5-9, G = 10-12 [verified: Elmegreen
  et al. 1999, Sect. 2]. "arm class 1-4" patchy, "5-12" increasingly two-armed [verified: Kendall 2015, Sect. 2.1.1].
  F = AC1-AC3, M = AC4-AC9, G = AC12, classes 10 and 11 no longer used [verified: Savchenko 2020, Sect. 2.4].
  The original definitions (Elmegreen & Elmegreen 1982, 1987) were not read.

Class frequencies
- S4G, 3.6 um, 1114 classifiable spirals: 50% flocculent, 32% multi-arm, 18% grand design; against earlier B-band
  classes (317 galaxies) 60% unchanged, 28% moved F->M or M->G, 9% the other way; 7 galaxies F->G, 2 G->F [verified:
  Buta et al. 2015, Sect. 4.6.1; arXiv:1501.00454]. The sample is weighted to Scd-Sm [verified: summary point 8].
- Diaz-Garcia 2019 subsample of 391: 76 G, 157 M, 158 F; classes peak at T = 3 (G), 5 (M), 6 (F); bar fraction 71 +/-
  5.2% (G), 59 +/- 3.9% (M), 77 +/- 3.3% (F), 69 +/- 2.3% overall [verified: Sect. 2.4, 5.1].
- PHANGS, CO(2-1), 72 valid discs: 28 +/- 2% grand design (20), 15 +/- 3% multi-arm (11), 36 +/- 6% flocculent (26),
  7 +/- 2% smooth (5), 14% unclassified; of the 62 classified 32 / 18 / 42 / 8%. 75% (15 of 20) of grand designs are
  barred; 52% (15 of 29) of barred galaxies are grand design; grand designs and bars sit at the high-mass end;
  multi-armed is the least repeatable class (47% agreement with stellar-light classes; G 67%, F 100%) [verified:
  Stuber et al. 2023, Sect. 4.2, 5.1.1, 5.2; arXiv:2305.17172].
- Galaxy Zoo 2 arm NUMBER, about 18 000 SDSS spirals: two arms in 62.1 +/- 0.4% of the luminosity-limited sample,
  rising to 75 +/- 2% in the densest environments [verified: Hart et al. 2016, Sect. 4.2.1, 4.2.3; arXiv:1607.01019].
  Debiased shares for m = 1, 2, 3, 4, 5+: 0.05, 0.62, 0.20, 0.06, 0.06 [verified with caution: Table 2, garbled layout].
- K band, 45 galaxies, dominant Fourier mode: m = 1 and m = 2 each "about one-third", m = 4 "a quarter", m = 3 in 4 of
  45; m = 2 dominant in 7 of 12 with near neighbours against 7 of 33 without [verified: Seigar & James 1998, Sect.
  4.2.1, 4.4].
- What goes with class: flocculents have lower stellar mass and surface density (medians nearly a dex lower); M and G
  alike except bar properties and bulge-to-total [verified: Bittner et al. 2017, abstract, Sect. 3.2.2;
  arXiv:1706.09904]. G against M at fixed mass: more concentrated, earlier type, classical bulges (245 against 299
  galaxies) [verified: arXiv:2405.01516, abstract]. G are 15% of isolated against 25% of non-isolated galaxies
  [verified: Savchenko 2020, Sect. 5.2]. CNN on SDSS: rotation speed 218 +/- 86 (G) against 145 +/- 67 km/s (F), bar
  fraction about 0.3 in both [fetch-quote: Sarkar et al. 2023 abstract, arXiv:2205.08733] - far from S4G's 71-77%.

Number of arms and of pieces
- All grand designs in Savchenko's sample are two-armed; multi-armed and flocculent run from 2 to ">5", flocculents
  higher on average [verified: Savchenko 2020, Sect. 2.4, Fig. 3].
- 29 G and M galaxies at 3.6 um: 2 to 5 fitted arms each [verified: Chugunov 2024, Table 4, last column].
- 19 galaxies: 88 spiral features = 26 "spurs" (azimuthal length < 90 deg) + 62 arms, 35 of them >= 180 deg; 17 arms
  in the 6 grand designs, 45 in the 13 multi-armed [verified: Chugunov 2025, Sect. 3]. That is 2.8 and 3.5 arms per
  galaxy and 1.4 short features per galaxy [inferred].
- S4G logarithmic segments (each a stretch of constant pitch marked by eye on unsharp-masked 3.6 um images; a long
  arm is several segments [verified: Herrera-Endoqui et al. 2015, text on the spiral measurements, Fig. 7]):
  1.5% of galaxies have one, 18.9% two, 22.0% three, 26.9% four, 14.8% five, 15.9% more than five, at most nine
  [verified: Diaz-Garcia 2019, Sect. 2.4 footnote 1]. By class from my parse of Table A.1 (367 rows): mean 3.7,
  median 4 (G); mean 5.0, median 5 (M); mean 3.2, median 3 (F) [inferred]. These count what could be traced reliably,
  so the flocculent number is a floor, not a census.
- SpArcFiRe arcs against human judgement, 252 galaxies: 1617 arcs, 246 judged real arms (163 + 83), 1371 not (39 +
  1332); a reliable arc in 3028 of 6222 spirals [counts verified, sums inferred: Hart et al. 2017, arXiv:1708.04628].
- Milky Way: "a four-arm spiral, with some extra arm segments and spurs"; the Local arm "an isolated arm segment";
  segment-length-weighted mean pitch 10 deg for the four major arms [verified: Reid 2019, abstract, Sect. 3.3, 8.1].

Length
- Azimuthal length of arms (those >= 90 deg): mean 273 deg (sd 143) in grand designs, 244 deg (sd 131) in multi-armed,
  not significantly different; the three longest, > 540 deg, are in NGC 628 and NGC 1232, both multi-armed [verified:
  Chugunov 2025, Sect. 3].
- Total angle subtended by the m = 2 arms at 3.6 um, 13 SINGS galaxies: 1.56 to 8.33 rad [verified: Kendall 2015,
  Table 2]; median 4.49 rad = 257 deg, range 89-477 deg [inferred].
- Pieces: segments "of ~5 kpc length" (Honig & Reid 2015, abstract; fitted lengths 5-10 kpc, Sect. 3); "characteristic
  lengths of 5 to 8 kpc, often separated by kinks or gaps" [verified: Reid 2019, Sect. 3, describing Honig & Reid].
  35% of arms have a bend (47% in grand designs, 31% in multi-armed) [verified: Chugunov 2025, Sect. 3.1.2].
- Pitch varies along an arm: sd between a galaxy's segments 9.5 +/- 0.3 deg, up to 15-20 deg [verified: Diaz-Garcia
  2019, Sect. 5.2, conclusions]; relative variation along the radius 0.56 +/- 0.25 (G 0.47 +/- 0.24, M 0.65 +/- 0.24)
  [verified: Savchenko 2020, Sect. 4.2].

### 4. Where arms start and how they join

- Method statement only: arms are traced "from the inner galaxy region (the ends of a bar or where spirals begin to
  be visible beyond the main body of a bulge)" [verified: Savchenko 2020, Sect. 6].
- Inner two-arm symmetry lies inside about 0.5 R25 in most galaxies with density waves; in barred galaxies the two
  symmetric arms end at twice the bar radius; 173 galaxies [fetch-quote: search summary of the abstract of Elmegreen &
  Elmegreen 1995, ApJ 445, 591; paper not read].
- Multiple-arm galaxies "generally have an inner 2-arm symmetry", "branching to many long arms" [verified: Elmegreen
  2011, Sect. 4.5; Buta 2015, Sect. 4.6.1]. No radius of branching is printed.
- Inner rings or pseudorings: about 50% of S0/a-Sc, about 13% of Scd-Sm, about 1/3 of all spirals [verified: Buta
  2015, Sect. 3.6]. Whether the arms then leave the ring or the bar is not tabulated.
- Barred grand designs: "the inner arms continue smoothly to the outer galaxy"; unbarred grand designs (NGC 1566,
  4321, 5248): a second, disjoint, broader and smoother arm system from about 0.5 R25 out to 1.3-1.4 R25; none in
  multiple-arm or flocculent galaxies [verified: Elmegreen 2011, Sect. 4.5].
- In the K' flocculent sample NGC 4041 and NGC 7177 have "short two-arm structures close to the ends of their bars";
  NGC 6384's arms end outside its nuclear bar and do not reach the centre; NGC 6643's "connect smoothly to the central
  regions" [verified: Elmegreen et al. 1999, Sect. 3].
- Innermost HII-traced segments have mean radii 1.1-3.3 kpc [verified: Honig & Reid 2015, Tables 2-5]. In M51 the
  fitted start of the arms lies 0.5 kpc further in in the FIR than in the UV [verified: Marchuk 2024, Sect. 6.3.3].
- Bifurcations: Savchenko 2020 followed the brighter branch and discarded arms with equal branches or more than one
  split, noting splits mostly in M and F galaxies [verified: Sect. 3.2, 3.3]. No statistic anywhere.

### 5. Flocculent discs in the near-infrared

- "most optically flocculent galaxies are also flocculent in the mid-IR"; exceptions NGC 5055 and NGC 2841 (long
  smooth arms at 3.6 um; in NGC 2841 mainly a dust arm), perhaps NGC 7793; of 197 optically flocculent galaxies looked
  at in 2MASS "only ~15% have underlying weak 2-arm structure" [verified: Elmegreen 2011, abstract, Sect. 4.1].
- 14 flocculent and multiple-arm galaxies in K': "half show some symmetry", 4 prominently (NGC 3810, 4501, 6384,
  6643) [verified: Elmegreen, Chromey, Bissell & Corrado 1999, AJ 118, 2618, abstract, Sect. 3].
- Contrast: those four "typically are about 0.5 mag brighter than the interarm regions", intensity ratios 1.45-1.70,
  rising with radius to mid-disc; arm pieces of the other flocculents "approximately 0.5 mag or less"; Thornley's
  flocculents 1.13-1.38 (0.13-0.35 mag); K' grand designs 1.5-6.3 (0.44-2 mag); 0.5 mag is a 22% compression, 2 mag
  72% [verified: Elmegreen 1999, Sect. 5; the Thornley and grand-design numbers are that paper's quotations].
- Thornley 1996: two symmetric K' arms in NGC 5055, 2403, 3521, 4414, "arm compression only about 20% greater than
  the interarm" on average [verified as a quotation: Elmegreen 1999, Sect. 1; original not read]. NGC 5055:
  arm/interarm about 1.3 in K' against about 3 in CO [verified as a quotation: Elmegreen 1999, Sect. 4].
- Extent of the two-arm symmetry in R25 (Table 1): NGC 3810 0.74, 4041 0.24, 4501 0.64, 5949 0.27, 6207 0.26, 6384
  0.98, 6643 0.78, 7177 0.18; none in six galaxies [verified: Elmegreen 1999, Table 1]. The prose gives azimuthal
  spans of nearly 180 deg (NGC 3810), about 160 (4501), about 50 (6384), nearly 250 (6643), with radii 0.44, 0.46,
  0.35 R25 attributed to EE95 [verified: Sect. 3]. Table and prose radii differ (K' here, the earlier optical measure
  there); not reconciled.
- Pitch of those K' arms 10-20 deg (+/- 2): 14.9 and 20.0 (NGC 3810), 13.2 (4501), 14.8 and 11.3 (6384), 10.0, 15.7,
  11.6 (6643); a fragment at 58 deg in NGC 3810, "typical for spurs" [verified: Table 1, Sect. 3; the table's columns
  are scrambled in the converted text, the 58 deg is confirmed in prose].
- Flocculent pitch at 3.6 um by radius in disc scale lengths (0-1, 1-2, 2-3, 3-4, 4-5): 23.1, 18.4, 17.6, 19.2, 20.9
  deg; multi-armed 22.3, 20.7, 19.0, 21.1, 21.4; grand design 20.1, 15.5, 15.4, 15.5, 18.0 [verified: Diaz-Garcia
  2019, Table 4]. Flocculent pitch does not depend on Hubble type [verified: Sect. 5.2]. Optical: sample mean pitch
  14.8 +/- 5.3 deg with a second flocculent peak near 25 deg [verified: Savchenko 2020, Sect. 4.2].
- Segments are measured in every radial bin from 0 to 5 scale lengths in all classes; no radial confinement is stated.

NGC 4414
- Arm class F [verified: Buta 2015, Table 9]; but "M" in Diaz-Garcia 2019's Table A.1, whose class column is said to
  follow Buta 2015 [verified: Table A.1 row and column notes]. CONFLICT inside the S4G papers; the VizieR copy of
  Herrera-Endoqui's table says F [fetch-quote].
- Five logarithmic segments at 3.6 um, all quality 2 ("acceptable"), pitch in deg (inner-outer radius in arcsec):
  -30.5 (28.7-63.6), -34.2 (19.4-57.3), -28.1 (32.7-87.4), -44.0 (29.2-54.4), -7.6 (57.9-66.3) [fetch-quote, twice,
  two VizieR mirrors of J/A+A/582/A86 table3, identical. The five pitches reproduce exactly the verified Table A.1
  row below (mean, sd, median, inner mean), so the pitches are as good as verified; the radii are not cross-checked].
- Table A.1 row: N = 5, mean pitch 28.9 +/- 6.0, sd 13.4, median 30.5, inner 32.3 +/- 1.9, arc-weighted 31.4 (7.8),
  spiral torque 0.06 +/- 0.01, m = 2 amplitude A2 = 0.09 (0.04) [verified: Diaz-Garcia 2019, Table A.1]. A2 = 0.09 is
  below the 16th percentile of every class (about 0.21) [inferred].
- Azimuth spanned by each segment, ln(ro/ri)/tan(pitch): 77, 91, 105, 37, 58 deg; arc lengths (ro - ri)/sin(pitch):
  69, 67, 116, 36, 64 arcsec; all segments lie between 19 and 87 arcsec [inferred from the rows].

### 6. Arm-to-arm differences inside one galaxy

- Difference between the mean pitches of a galaxy's arms, relative to the mean: "about 20-25%", up to 100%; G 0.16 +/-
  0.12, M 0.27 +/- 0.25, F 0.21 +/- 0.21 [verified: Savchenko 2020, Sect. 4.2, Fig. 15].
- In 20 of 45 K-band galaxies the two arms have "very different" pitch at the same radius; 9 of those have strong
  m = 1 [verified: Seigar & James 1998, Sect. 4.1.1]. One SDSS example: 13.6 against 24.4 deg [verified: Davis & Hayes
  2014, results text].
- HII-traced whole-arm pitches: M51 13.4 +/- 0.6 against 8.3 +/- 0.3 deg; NGC 3184 19.6 +/- 0.6 and 20.2 +/- 0.8; NGC
  1232's six arms and fragments 9.7, 17.3, 18.4, 10.9, 16.7, 10.8 deg [verified: Honig & Reid 2015, Sect. 4; degree
  marks are lost in the converted text, the decimal places are read from context].
- M51 at 3.6 um: light 0.16 against 0.14 of the total (ratio 1.14), pitch 12.0 against 15.7 deg, width 42.5 against
  41.0 arcsec, radial scale 53.6 against 122.2 arcsec [verified: Marchuk 2024, Table 4].
- Mode content: F3/F2 0.33 (G), 0.48 (M), 0.58 (F); asymmetric (non-180-deg) light 15-20% [verified: Elmegreen 2011,
  Sect. 4.3, 4.1]; m = 1 dominant in a third of K-band discs [Seigar & James 1998, Sect. 4.2.1]. Lopsidedness at 3.6
  um (167 galaxies) grows with radius to 3.5 scale lengths and "stronger arm patterns occur in galaxies with less
  lopsidedness" [verified: Zaritsky et al. 2013, abstract; arXiv:1305.2940].
- Unequal lengths, and the ratio of the two arms' amplitudes: no statistic found. Repeats of well-known results:
  M51's unequal arms; the high incidence of lopsidedness; pitch differing arm to arm.

### What a model could adopt (numbers only)

CROSS-ARM PROFILE
- Shape: near-Gaussian, Sersic index 0.6-0.7 (0.4-0.9) (Chugunov 2025). Asymmetry small, sign disputed: +0.14 +/- 0.23
  inner side steeper (Savchenko 2020, optical); -0.05 (Chugunov 2024, 3.6 um); 5-10% (Seigar & James 1998, K).
- Width, old stars: FWHM 0.53 +/- 0.04 h = 0.12 +/- 0.01 r25 at mid-arm, 0.24-1.18 h per galaxy (Chugunov 2024);
  optical FWHM about 0.12 r25, 2.7 / 2.1 / 1.7 kpc for G / M / F (Savchenko 2020, converted from 1/e widths).
- Width against radius: linear; radial FWHM 0.30 r (0.19 r with the other disc subtraction), zero point 19-34% of the
  mid-arm width (Chugunov 2025); optical slope 0.10-0.17 kpc/kpc, positive in 86% (Savchenko 2020); start/end ratio
  0.74 (Chugunov 2024); in azimuth 20-40 deg FWHM (Seigar & James 1998). These disagree by up to a factor of two.
- Width, young tracers: sigma 0.34 kpc at 8.15 kpc, +36 pc/kpc (MW masers, Reid 2019); sigma 0.055 R median,
  0.01-0.13 (HII, Honig & Reid 2015); 0.59 kpc mean in M83 (Silva-Villa 2022); FUV radial FWHM 0.14 r (Chugunov
  2025). The last segment narrows in 4 of the 10 arms with two or more segments (Honig & Reid 2015).
- NOT measured: a sharp-edge parameter per arm; near-IR width of flocculent pieces; width over arm spacing.
AMPLITUDE
- Arm/interarm at 3.6 um, disc average: 1.14 +/- 0.44 (G), 0.81 +/- 0.28 (M), 0.75 +/- 0.35 mag (F); flocculent at
  one radius 0.44 +/- 0.13 mag (Elmegreen 2011). K' flocculent 0.5 mag or less, ratios 1.13-1.70 (Elmegreen 1999).
- m = 2 relative amplitude at 3.6 um: median 0.21, range 0.07-0.42 (Kendall 2015); maximum A2 over segments, medians
  0.44 / 0.31 / 0.31 for G / M / F (Diaz-Garcia 2019, my tabulation); NGC 4414 0.09.
- Light in arms: 3.6 um median 0.21, 0.08-0.46 (Chugunov 2024, G and M); r band 0.21 / 0.14 / 0.13 (Savchenko 2020).
- Along a piece: not exponential in general; share of the disc profile peaks at 1-2 h; ends tapered, not sharp (chi2
  +10% if sharp); dips in 24% of arms; outer end usually at 0.5-0.7 r25 (Chugunov 2024, 2025).
- NOT measured: taper lengths as printed numbers; amplitude along flocculent pieces.
NUMBER AND LENGTH OF PIECES
- Arms per galaxy: 2 in all grand designs (Savchenko 2020); 2.8 (G) and 3.5 (M) arms of >= 90 deg plus 1.4 shorter
  features (Chugunov 2025); arm number 2 in 62%, 3 in 20%, 4 in 6%, 5+ in 6%, 1 in 5% of SDSS spirals (Hart 2016).
- Constant-pitch segments per galaxy at 3.6 um: 3.7 (G), 5.0 (M), 3.2 (F, a floor); at most 9 (Diaz-Garcia 2019).
- Length: whole arms 273 +/- 143 deg (G), 244 +/- 131 deg (M) (Chugunov 2025); m = 2 pattern median 257 deg, 89-477
  (Kendall 2015); pieces 5-8 kpc between kinks (Honig & Reid 2015; Reid 2019); bends in 35% of arms (Chugunov 2025).
  Flocculent: weak two-armed K' structure spans 50-250 deg (Elmegreen 1999); NGC 4414's segments 37-105 deg each.
- NOT measured: a length distribution of flocculent pieces; the number of pieces in a flocculent disc.
WHERE THEY START
- Arms' share is zero at the centre, peaks at 1-2 h (Chugunov 2024). Inner two-armed part inside about 0.5 R25,
  ending at twice the bar radius in barred galaxies (Elmegreen & Elmegreen 1995, abstract at fetch level only).
  Inner rings in about 1/3 of spirals: 50% of S0/a-Sc, 13% of Scd-Sm (Buta 2015).
- NOT measured: fraction of arms starting at a bar's end against a ring; branch radii; branch frequency.
INEQUALITY WITHIN A GALAXY
- Pitch between arms: 16% (G), 27% (M), 21% (F) of the mean (Savchenko 2020). Width: 10% (two-armed), 37% (others)
  (Chugunov 2024). Light, M51: 1.14 to 1 (Marchuk 2024). F3/F2 = 0.33 / 0.48 / 0.58 for G / M / F (Elmegreen 2011).
- NOT measured: a distribution of the two arms' amplitude ratio or length ratio.
CLASS FREQUENCY AND WHAT PREDICTS IT
- 18% G, 32% M, 50% F at 3.6 um in S4G, late-type-heavy (Buta 2015); 32 / 18 / 42% plus 8% smooth in PHANGS CO
  (Stuber 2023). Flocculent: low mass, low surface density, late type (Bittner 2017). Grand design: bars (75% barred
  in PHANGS), near neighbours, dense environments (Seigar & James 1998; Hart 2016), classical bulges (2405.01516).
  About 15% of optical flocculents show a weak two-armed near-IR pattern (Elmegreen 2011). F = classes 1-3 or 1-4.

---

## Part B — the disc's thickness and the force of a spiral wave

## Reading notes P5 (b): finite thickness and the in-plane force of a spiral wave; gas response to a narrow arm

Blind to the repository. Read 2026-10-05 as PDF text (files saved by the fetch tool, converted with pdftotext; texts in
`p5txt_b/`). ADS scans (Toomre 1964, Romeo 1992, Shu+ 1973) carry an OCR layer: words reliable, symbols in equations
partly garbled - said where it matters. arXiv papers: equation numbers of the arXiv version. Tags: [verified: ...] read
in the PDF text this session; [fetch-quote] summarising model only; [inferred: ...] my algebra or arithmetic; [not read].

### 0. Items for which nothing readable was found
- Vandervoort 1970 (ApJ 161, 87): ADS scan timed out twice; Shu 1968 (the "J factor"). Both [not read], known only
  second-hand (Romeo 1992; Elmegreen 2011).
- Binney & Tremaine 2008 (section/equation on thickness or softened gravity): [not read]; no section number given here.
- Bertin & Lin 1996, Bertin 2014, Romeo 1994, Elmegreen 1987, Ghosh & Jog 2014/2015, Jog & Solomon 1984: [not read]
  (Romeo 1994 only via Romeo & Wiegert 2011; Elmegreen 1987 only via Kim+ 2002/2006/2007, Behrendt+ 2015).
- Kim, Kim & Ostriker 2014 (thick-disc spiral shocks): [not read]. Read instead: Kim & Ostriker 2002, 2006, 2007;
  C.-G. Kim+ 2010; Kim, Kim & Ostriker 2020; Kim & Kim 2014.
- Roberts 1969, Wada 2008, Dobbs & Bonnell 2008: [not read]; second-hand via Dobbs & Baba 2014, Baba+ 2015.
- Zibetti+ 2009, Querejeta+ 2015: [not read]. Salo+ 2015 (arXiv:1503.06550) read: decompositions only, no force
  calculation, no g(dr, h_z); that is in Laurikainen & Salo 2002 and Diaz-Garcia+ 2016 (section 4).
- No printed Gaussian-profile factor; no printed conversion from stellar arm amplitude to F with thickness; no printed
  gas-to-stellar contrast for corotating arms; Bizyaev & Mitronova's mean ratio only as [fetch-quote].

### 1. The reduction factor
Notation: plane wave Sigma_1 exp(ikx); a = k times the thickness symbol of each formula. Thin-disc reference:
Phi_0 = -(2 pi G Sigma_1/|k|) exp(ikx - |kz|) [verified: Wang+ 2010, arXiv:1004.5593 (MNRAS 407, 705), eq. 32;
Behrendt+ 2015, arXiv:1408.5902, eq. A1; Toomre 1964, ApJ 139, 1217, eq. 16 (OCR)]; force amplitude at z = 0 is
2 pi G Sigma_1 (Toomre eq. 17, OCR).
#### 1.1 General: midplane potential of a layer with normalised vertical profile h(z)
    Phi(k, z=0) = -(2 pi G Sigma(k)/|k|) * Integral_{-inf}^{inf} h(z') exp(-|k z'|) dz'
[verified: Kim & Ostriker 2007, arXiv:astro-ph/0701755, eq. 3, "the solution at z = 0", h(z) assumed not to vary with
time; same content in Wang+ 2010 eq. 33 (general z, kernel exp(-k|z-h|)) and Behrendt+ 2015 eqs. 1, 3, A3: "the total
potential at the mid-plane ... Phi_tot = Phi_0 F"]. So T_mid(k) = Integral h(z) exp(-|kz|) dz multiplies the POTENTIAL
AT z = 0, hence the in-plane force at z = 0. Limits: 1 as k -> 0; 2 h(0)/k as k -> inf (force of uniform density
rho(0)) [inferred]. Ghosh & Jog 2022 (arXiv:2111.10893, after eq. 9): the azimuthal force at the midplane carries the
identical factor, also in WKB [verified].
#### 1.2 Exponential profile exp(-|z|/H)/(2H)
    T_mid = 1/(1 + |k| H)
[verified: Kim & Ostriker 2007 eq. 4, Phi(k) = -2 pi G Sigma(k)/(|k|(1+|k|H)), "thick-disk gravity"; Behrendt+ 2015
eqs. 4-5; Kim & Ostriker 2006, arXiv:astro-ph/0603751, eq. 11, "exact for ... rho ~ exp(-z/H0) (e.g. Elmegreen 1987)";
Kim, Ostriker & Stone 2002, arXiv:astro-ph/0208414, sect. 3.2: dPhi_1/dx = 4 pi i sgn(k) G rho_1(0) H exp(-ikx)/(1+|k|H)
"at the disk midplane", "exact for an exponential density distribution ... asymptotically approaches the exact
solutions for arbitrary density profiles when |k|H -> 0 or inf"; their eq. 18: omega^2 = kappa^2 + (c_s^2 + v_A^2)k^2
- [|k|H/(1+|k|H)] 4 pi G rho_00, Sigma_0 = 2 rho_00 H.] Multiplies potential and force AT z = 0, exactly, for this
profile; H = exponential scale height = Sigma/(2 rho(0)). Limits 1 and 1/(kH).
Stated accuracy when used for other profiles: "largest fractional difference ... only ~15 %, which occurs at |k|H ~ 1"
(Kim+ 2002); "slightly underestimates the real potential for purely self-gravitating disks, but not more than 14 %"
(Kim & Ostriker 2007); F_exp underestimates F_sech2 "with a maximum error of 13.7 %" at lambda/z0 = 1.04 pi
(Behrendt+ 2015 sect. 2.1); midplane acceleration by direct integration over two-component equilibria: (1+kH)^-1 "too
low by ~12 % at kH ~ 1-10", "less than 15 % in all cases" (Elmegreen 2011, arXiv:1106.1580, sect. 2 and App. B,
eqs. B1-B2) [all verified]. All four: the approximation UNDERSTATES the midplane force.
[inferred: my integration gives 13.71 % at k z0 = 1.92, i.e. lambda/z0 = 1.042 pi.]
#### 1.3 Uniform slab between z = -h and +h
    F(alpha h) = (1 - exp(-alpha h))/(alpha h)
[verified: Toomre 1964 sect. III(e) "The Effect of a Finite Disk Thickness", eq. 33 (OCR prints "03)" after "02)"):
stars "only to be found between the planes z = +-h", disturbance density independent of z inside; "the disturbance
force, say, in the central plane, will in this case be just that of equation (17) multiplied by" F; "about a 26 per
cent reduction ... where the wavelength ... equals 5 times the thickness, 2h, and about a 14 per cent change when it
amounts to 10 times"; "might simply be thought of as a decrease in the effective surface mass density".]
[inferred check: alpha h = pi/5 gives 0.742, pi/10 gives 0.858.] Multiplies the force in the CENTRAL PLANE; h is the
HALF-thickness of a constant-density slab; limits 1 and 1/(kh). Same form: Ghosh & Jog 2018 (arXiv:1806.01439, eqs. 8,
18) and 2022 (eq. 9), "total thickness of 2h"; Elmegreen 2011 sect. 2; Romeo 1992 eq. 14 ("naively obtained") [verified].
Caution: Ghosh & Jog 2018 equate beta = k_crit h = 0.3 with "a disk thickness of 300 pc" and the thin disc's ~300 pc
scale height, i.e. they put an exponential scale height into the slab half-thickness [verified wording].
#### 1.4 Isothermal profile sech^2(z/z0)/(2 z0)
    F(k, hz) = 1 - (1/2) k hz [ H(k hz/4) - H(k hz/4 - 1/2) ],   H(alpha) = Integral_0^1 (1 - y^alpha)/(1 - y) dy
[verified: Wang+ 2010 eqs. 33-36 and App. C eq. C1 (Gradshteyn & Ryzhik 3.541, 8.370, 8.361-7); H the harmonic number;
profile sech^2(h/hz)/(2hz); defined at the midplane, eq. 34: Phi_k(z=0) = -(2 pi G Sigma_k exp(ikx)/|k|) F.]
    F_sech2(lambda, z0) = Integral exp(-(2 pi/lambda)|h|) sech^2(h/z0)/(2 z0) dh    (integrated numerically)
[verified: Behrendt+ 2015 eqs. 3, 6; their introduction says "no analytical solution".]
[inferred: with H(alpha) = psi(alpha+1) + gamma the Wang form is (a/2)[psi(a/4 + 1/2) - psi(a/4)] - 1, a = k z0; at
a = 1 it is pi/2 - 1 = 0.5708, reproduced by my numerical integral; small a: 1 - a ln2; large a: 1/a.]
Symbol: z0 = Sigma/(2 rho(0)); the exponential tail has scale z0/2. Printed approximations for this profile:
1/(1 + k z0) (low by <= 13.7 %) and the Cox & Gomez fit (1.9). No read source prints (1 - exp(-kh))/(kh) or an
exp(-kh/..) form for sech^2.
#### 1.5 Gaussian profile
No printed factor found. [inferred: T_mid = exp(k^2 s^2/2) erfc(k s/sqrt2) for exp(-z^2/2s^2)/(sqrt(2 pi) s); limits
1 and sqrt(2/pi)/(ks).] The profile and its scale equivalence are printed in Laurikainen & Salo 2002 (section 4).
#### 1.6 Layer-averaged factor (the layer acting on itself)
    F(k) = (1/(Sigma_0 Sigma_1)) Double-Integral rho_0(z) rho_1(z') exp(-k|z - z'|) dz dz'
[verified: J.-G. Kim, W.-T. Kim, Seo & Hong 2012, arXiv:1210.6207, eqs. 37-39, "generalized reduction factor of
self-gravity", "F = 1 + O(k H) in the long wavelength limit, regardless of density distributions"; eq. 41 the same
with the Jeans-mode part of rho_1.] Unbounded exponential disc, rho_0 ~ rho_1 ~ exp(-|z|/H):
    F_J^exp = 1/(1 + kH) - kH/(2 (1 + kH)^2)
[verified: same paper, footnote 1; the pdf text garbles the second term, restored form confirmed by my algebra:
(1/pi) Integral a/(a^2+u^2) (1+u^2)^-2 du = (2+a)/(2(1+a)^2).] The footnote continues: 1/(1+kH) "is in fact the exact
force correction term at the z = 0 plane (e.g., Kim & Ostriker 2007), while the former is the correction factor
averaged along the z-direction. Nevertheless, equation (44) [= 1/(1+kH)] matches the reduction factor for sech^2(z/H)
disks better than F_J^exp." Fig. 5 text: F_J for sech^2(z/H), with rho_1 ~ rho_0 or the eigenfunction, "both are
closely approximated by (1 + k_x H)^-1". [inferred: my double integral for sech^2 with rho_1 ~ rho_0, times (1 + k z0):
0.998, 0.989, 0.935, 0.828 at k z0 = 0.1, 0.3, 1, 3.]
#### 1.7 Spiral-structure usage (Vandervoort / Shu / Romeo), second-hand
    T = 1/(1 + |k| <z>)      against Toomre's   (1 - exp(-|k|<z>))/(|k|<z>)
[verified: Romeo 1992, MNRAS 256, 307, sect. 3, eqs. 13-14 (OCR; layout garbled, words clear): "the form of the
dispersion relation remains the same provided the unperturbed surface density is multiplied by a suitable reduction
factor"; "The most reliable and complete analysis is that performed by Vandervoort (1970b), which is local in the
galactic plane and global perpendicular to it. The reduction factor, found by solving an eigenvalue problem, has been
shown to be very well approximated by the simple expression" (13).] <z> = "the thickness-scale of the galactic disc":
the effective thickness-scale sigma/(2 rho_0), in the one-component case "twice the exponential thickness-scales"
[verified in words; eq. 5 itself OCR-garbled]; for sech^2(z/z0), <z> = z0 [inferred]. Two components:
T_i = 1/(1 + |k| z_eff,i), an "ansatz ... which for the moment can only be justified at an intuitive level", for
components "not strongly coupled"; it "matches the reduction factors derived by Shu (1968)" in the one-component and
equal-dispersion limits [verified: sect. 3.1, eq. 23]. Elmegreen 2011 sect. 2: "Vandervoort (1970) used (1 + kH)^-1
from a more detailed analysis. These two factors are similar, as is the J factor in Shu (1968, see Vandervoort 1970)";
Romeo "concluded that the correction factors cannot generally be applied independently to each component, but if the
vertical distributions are somewhat uncoupled, then that approximation should be all right" [verified].
Romeo & Wiegert 2011 (arXiv:1101.4519, eq. 8): T ~ 0.8 + 0.7 (sigma_z/sigma_R), 0.5 <~ sigma_z/sigma_R <~ 1, from
Romeo 1994 fig. 3 [verified] - a multiplier of Q at the most unstable wavelength, NOT a function of k, not a force factor.
#### 1.8 Perturber (thick stars) acting on responder (thin gas)
- Kim & Ostriker 2007 eq. 8 (two-component dispersion relation): gas term with 1/(1 + k H_g), stellar term with
  1/(1 + k H_s); "the density reduction factors of the gaseous and stellar components differ"; H_g = 170 pc,
  H_s = 330 pc. Elmegreen 2011 eq. 19: phi = -(2 pi G/k)[Sigma_g/(1 + k H_g) + Sigma_s/(1 + k H_s)] [both verified].
  One potential - each layer's midplane value, reduced by that layer's OWN thickness - acts on both components: the
  force of the stellar wave on the gas carries the STARS' factor 1/(1 + k H_s).
- Ghosh & Jog 2018 sect. 2.3.1 (stars of thickness 2 h_1, gas razor-thin): the stellar force terms carry delta_s
  (eq. 18, slab form with h_1), "an effective reduction in the corresponding surface density" [verified].
- No read source averages the stellar potential over a gas layer of finite thickness. [inferred, two exponentials,
  from 1.6 by partial fractions: T_cross = (h_s + h_g + k h_s h_g)/((h_s + h_g)(1 + k h_s)(1 + k h_g)); h_g -> 0 gives
  1/(1 + k h_s), h_g = h_s gives F_J^exp; at k h_s = 1: 0.500, 0.486, 0.444, 0.375 for h_g/h_s = 0, 0.2, 0.5, 1.]
- The local spiral-shock simulations use none of this: the arm potential is Phi_sp cos(2 pi x/L_x), no z-dependence,
  amplitude prescribed (Kim & Ostriker 2006 eq. 7; C.-G. Kim+ 2010, arXiv:1006.4691, eq. 6; Kim+ 2020,
  arXiv:2006.05614, eq. 9) [verified].
#### 1.9 Cox & Gomez 2002 (ApJS 142, 261; arXiv:astro-ph/0207635)
rho_A(r,z) = rho_0 exp(-(r - r0)/Rs) sech^2(z/H) (eq. 1); rho = rho_A cos(gamma) (2);
gamma = N [phi - phi_p(r0) - ln(r/r0)/tan(alpha)] (3); rho = rho_A Sum_n C_n cos(n gamma) (4);
    K_n = n N/(r sin alpha)  (5);   beta_n = K_n H (1 + 0.4 K_n H)  (6);   D_n = (1 + K_n H + 0.3 (K_n H)^2)/(1 + 0.3 K_n H)  (7)
    Phi(r,phi,z) = -4 pi G H rho_0 exp(-(r - r0)/Rs) Sum_n [C_n/(K_n D_n)] cos(n gamma) [sech(K_n z/beta_n)]^beta_n   (8)
[verified: eqs. 1-8 in the UTF-8 pdf text; the galpy documentation page for SpiralArmsPotential prints the same K_n,
B_n (= beta_n), D_n and C_n = [8/(3 pi), 1/2, 8/(15 pi)] [fetch-quote].] Origin (sect. 2): the potential of "an
infinite sinusoidally oscillating density pattern in a rectilinear coordinate system" was evaluated numerically and
"fitted ... versus phase (kx) and z with a simple functional form", then remapped onto the log spiral: D_n and beta_n
are FITS. The exact density of (8) has the dominant term rho_0 C_n (K_n H/D_n)((beta_n+1)/beta_n) cos(n gamma)
sech^(2+beta_n)(K_n z/beta_n) (eq. 10), differing from (4) by "much smaller than the uncertainty in how the true arms
should be represented"; valid for "K_n H small to moderate" [verified].
Arm profile of the three-term sum: "the density behaves approximately as a cosine squared in the arms but is separated
by a flat interarm region occupying half the volume. It has three terms in its sum, with C1 = 8/(3 pi), C2 = 1/2, and
C3 = 8/(15 pi)"; "its average density is zero" [verified]. [inferred: exactly the first three Fourier coefficients of
2 cos^2(gamma) on |gamma| < pi/2, zero elsewhere, mean 1/2 removed; truncated peak +1.519 (exact +1.5), interarm
-0.519 (-0.5); consistent with their "0.4 perturbation fraction implies ... 0.8 and 1.6".]
Reduction read off (8) [inferred: a thin sheet Sigma_n = 2 H rho_0 C_n has Phi = -4 pi G H rho_0 C_n/K_n, so harmonic
n carries 1/D_n at the midplane]:   T_CG(KH) = (1 + 0.3 KH)/(1 + KH + 0.3 (KH)^2),  limits 1 and 1/(KH).
[inferred: T_CG over my exact sech^2 midplane integral = 0.9992, 0.9971, 0.9902, 0.9860, 0.9901 at KH = 0.1, 0.3, 1,
3, 6 - the fit IS the sech^2(z/H) midplane factor to 1.4 %.] Their case: N = 2, alpha = 15 deg, H = 0.18 kpc (sech^2
thin disc of Dehnen & Binney 1998 Model 2), r = 8 kpc; [inferred: K_n H = 0.174, 0.348, 0.522 and 1/D_n = 0.889,
0.798, 0.721 for n = 1, 2, 3].
#### 1.10 Side by side (my arithmetic; a = k times each column's own symbol)
| a | exp mid 1/(1+a) | exp layer-avg | slab mid (1-e^-a)/a | sech^2 mid (exact) | sech^2 layer-avg | Cox-Gomez 1/D | Gauss mid |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.909 | 0.868 | 0.952 | 0.935 | 0.908 | 0.934 | 0.925 |
| 0.3 | 0.769 | 0.681 | 0.864 | 0.824 | 0.761 | 0.821 | 0.799 |
| 1   | 0.500 | 0.375 | 0.632 | 0.571 | 0.467 | 0.565 | 0.523 |
| 3   | 0.250 | 0.156 | 0.317 | 0.288 | 0.207 | 0.284 | 0.243 |
Symbols: H, H, half-thickness h, z0, z0, H (sech^2), sigma. In the first six the symbol equals Sigma/(2 rho(0)).
At equal VERTICAL DISPERSION <z^2> = 2 h_z^2 instead (Laurikainen & Salo 2002 eq. 11), midplane factors, a = k h_z:
| k h_z | exponential | sech (0.900 h_z) | sech^2 (z0 = 1.559 h_z) | Gaussian (1.414 h_z) | slab (h = 2.449 h_z) |
|---|---|---|---|---|---|
| 0.1 | 0.909 | 0.904 | 0.901 | 0.897 | 0.887 |
| 0.3 | 0.769 | 0.756 | 0.747 | 0.735 | 0.708 |
| 1   | 0.500 | 0.469 | 0.452 | 0.428 | 0.373 |
| 3   | 0.250 | 0.214 | 0.199 | 0.179 | 0.136 |
With the other observers' convention z0 = 2 h_z (same slope at large z): sech^2 midplane 0.876, 0.695, 0.386, 0.159.
The conflict in one line: for a fitted exponential h_z the sech^2 factor at k h_z = 1 is 0.39 (z0 = 2 h_z), 0.45
(equal dispersion) or 0.57 (z0 = h_z, equal Sigma and rho(0)), against 0.50 exponential. The scale mapping moves the
factor more than the functional form does.

### 2. Typical numbers for k h
- Kregel, van der Kruit & de Grijs 2002 (arXiv:astro-ph/0204154), I band, 34 edge-ons, L ~ exp(-R/h_R) exp(-z/h_z),
  h_z = 0.5 z0 (eq. 1): "the average flattening of the diameter-limited distribution is h_R/h_z = 8.5 +- 2.9 (1 sigma),
  while that of the volume corrected distribution is h_R/h_z = 7.3 +- 2.2"; "about 70 percent of spirals seem to have
  a flattening between 6 and 8"; scale height taken independent of radius [verified]. h_z/h_R = 0.137 (0.105-0.196)
  [inferred].
- By type, de Grijs 1998 as used by Diaz-Garcia+ 2016 (arXiv:1509.06743 v6, sect. 3.1.2): "h_R/h_z = 4 (1-5) if
  T <= 1, 5 (3-7) if T in [2,4] and 9 (5-12) if T >= 5"; Laurikainen & Salo 2002 sect. 5: 2.5 early, 4.5 late [verified].
- Bizyaev & Mitronova 2002 (arXiv:astro-ph/0207539), 2MASS, 153 flat galaxies, exp(-r/Re) sech^2(z/z0) (eq. 2, z0 the
  SECH^2 scale) [verified]; mean h/z0 ~ 4.8 [fetch-quote], i.e. h_R/h_z ~ 9.6 for h_z = z0/2 [inferred].
- Milky Way: thin disc vertical scalelength at R0 300 +- 50 pc, thick 900 +- 180 pc, thin-disc radial scalelength
  2.6 +- 0.5 kpc [verified: Bland-Hawthorn & Gerhard 2016, arXiv:1602.07702, summary list]; h_z/h_R = 0.115 [inferred].
  Adopted elsewhere: 330 pc (Kim & Ostriker 2007), 245 pc (Kim+ 2020), 180 pc sech^2 (Cox & Gomez 2002) [verified].
k h per harmonic [inferred: k = m/(R sin i) (Cox & Gomez eq. 5); k h = m (h_z/h_R)/((R/h_R) sin i); h_z/h_R = 0.137;
T = 1/(1 + k h_z)]. Cells are k h / T:
| R/h_R, pitch | m=2 | m=3 | m=4 | m=5 | m=6 |
|---|---|---|---|---|---|
| 2, 10 deg | 0.79 / 0.56 | 1.18 / 0.46 | 1.58 / 0.39 | 1.97 / 0.34 | 2.37 / 0.30 |
| 2, 20 deg | 0.40 / 0.71 | 0.60 / 0.63 | 0.80 / 0.56 | 1.00 / 0.50 | 1.20 / 0.45 |
| 2, 30 deg | 0.27 / 0.79 | 0.41 / 0.71 | 0.55 / 0.65 | 0.69 / 0.59 | 0.82 / 0.55 |
| 3, 10 deg | 0.53 / 0.66 | 0.79 / 0.56 | 1.05 / 0.49 | 1.32 / 0.43 | 1.58 / 0.39 |
| 3, 20 deg | 0.27 / 0.79 | 0.40 / 0.71 | 0.53 / 0.65 | 0.67 / 0.60 | 0.80 / 0.56 |
| 3, 30 deg | 0.18 / 0.85 | 0.27 / 0.79 | 0.37 / 0.73 | 0.46 / 0.69 | 0.55 / 0.65 |
k h is linear in h_z/h_R: times 0.73 for 0.10, times 1.46 for 0.20 (R = 2 h_R, 10 deg, m = 6: T = 0.37 and 0.22).
Milky Way, h = 0.3 kpc, R = 8 kpc, 15 deg: k h = 0.29, 0.43, 0.58, 0.87 and T = 0.78, 0.70, 0.63, 0.53 for m = 2, 3,
4, 6 [inferred]. T spans 0.85 (m = 2, open, outer) to 0.30 (m = 6, tight, inner); relative to m = 2 the m = 6
harmonic is weakened by a further factor 0.53-0.77. Not a small correction for m >= 4.

### 3. Gas response to a narrow or non-sinusoidal arm
#### 3.1 Why harmonics are added to the stellar forcing
Cox & Gomez 2002: to build "more complicated azimuthal arm structures"; the three-term case has "the desired flatter
interarm density and sharper peaks at the arms. The difference is moderated somewhat in the potential function, but
the flatter peaks (interarm) and sharper valleys of the arms are apparent". Motive: Rix & Rieke 1993, Rix & Zaritsky
1995 found "in galaxies with strong arms, the arm to interarm stellar density contrast was roughly a factor of two";
some two-armed spirals are "dominated by the fundamental sinusoidal component, implying very broad arms", but "in
cases with very strong arms there was a significant higher harmonic, implying narrower arms" [verified]. They give NO
gas-response result for the concentrated arm. Gomez & Cox 2002 (arXiv:astro-ph/0207634) ran "a sinusoidal profile in
phi"; on Martos+ 2002's narrower arms: "The full 3D hydrodynamical effects ... will require further investigation" [verified].
[inferred: in (8) the force of harmonic n relative to n = 1 is (C_n/C_1)(D_1/D_n): thin limit 0.589, 0.200 for n = 2,
3; with K_1 H = 0.174: 0.529, 0.162.]
#### 3.2 Nonlinear response even to a sinusoid (Shu, Milione & Roberts 1973, ApJ 183, 819; OCR text)
- Potential "in the central plane of the galactic disk ... given by the linear theory", axisymmetric part plus
  A(r) cos(chi) (eq. 1); isothermal gas, a = 8 km/s. "the response of a particular component of the galaxy to a given
  spiral field is roughly proportional to the inverse square of the relevant dispersive speed"; "the density response
  of the interstellar gas can be fully nonlinear even if the perturbation density of the disk stars amounts to only a
  few percent of the unperturbed value" [verified, sect. II].
- Slightly nonlinear regime (sect. III): nu = m(Omega_p - Omega)/kappa (9a); x = (k^2 + m^2/r^2) a^2/kappa^2 (9b);
  velocities expanded in powers of the scaled field strength f (eq. 12; proportional to F, definition OCR-garbled);
  first order alpha_11 = nu/(1 - nu^2 + x), beta_11 = 1/(1 - nu^2 + x) (16a); the coefficient of harmonic s is O(f^s)
  (after eq. 19); "resonant denominators": harmonic s diverges where nu^2 - x = n^-2, n = +-s (eq. 17) - n = +-1 the
  Lindblad resonances, the rest "ultraharmonic resonances"; the higher harmonic reinforces or interferes with the
  fundamental according to the side of the resonance; "For realistic amplitudes of the background forcing, f is of
  order unity so that the series (18) converges slowly, if at all" [verified].
- Numbers (their Galaxy model): "F = 5 percent, the value believed to be approximately present in the solar
  neighborhood (Yuan 1969) ... a factor 12:1 results for the total variation of the gas density", peak "~5 times
  larger than the average density", compression "confined to a very narrow spike"; F_cusp (onset of shocks) 3.7 and
  1.1 percent on two streamlines; at 0.5-0.9 percent the second harmonic already splits the flow near the n = 2
  resonance. Abstract: narrow compression zones when the Doppler-shifted phase velocity exceeds the effective acoustic
  speed, broad otherwise; ultraharmonic resonances "can introduce secondary compressions" [verified].
  So a sinusoidal force of a few per cent already gives a gas arm far narrower and of far higher contrast than the
  stellar arm; the gas profile is not a scaled copy of the forcing.
#### 3.3 Harmonics in the forcing (Chakrabarti, Laughlin & Shu 2003, ApJ 596, 220; arXiv:astro-ph/0306472)
Thin self-gravitating singular isothermal gas discs under a rigidly rotating spiral. Resonance of the n-th harmonic
response to an m-armed log spiral: (Omega_p - Omega)/kappa = +-(1/m) sqrt(n^-2 + x), x = m^2 c_g^2/(r^2 kappa^2
sin^2 i) (eqs. 25-26) [verified; exponent read from "1/n times the epicyclic frequency"]. With harmonic j in the
forcing "resonances are possible where mj replaces m"; the SYL planform "contains a full Fourier decomposition of
forcing harmonics above the fundamental" and "produces somewhat higher density contrasts and causes the growth of more
substructure" than the sinusoid at equal amplitude (LSYL2 shows incipient spurs, L2 stays smooth); long runs:
"spiral forcing amplitudes of 1.3-1.5 % maintain a steady-state response in the Q_g = 1.3 disks", 3.5 % smooth and
5 % spur-forming at Q_g = 2.48; branches near the 4:1 resonance; "self-gravity is crucial for the growth of
substructure via the higher-order resonances" [verified]. All for a pattern the gas streams through.
Dobbs & Baba 2014 (arXiv:1407.5062, sect. 3.5): "for warm gas and moderate forcing, a narrow shock is expected ahead of
the minimum of the potential ... If the gas is cold ... after"; shock forcing "around a few %" at 8 km/s [verified].
#### 3.4 The arm strength F and the stellar amplitude
    F = (2/sin i)|Phi_0|/(Omega_0^2 R_0^2)   [verified: Kim & Ostriker 2002, arXiv:astro-ph/0111398, eq. 9 (m = 2)]
    F = (m/sin i)|Phi_sp|/(R_0^2 Omega_0^2)  [verified: Kim & Ostriker 2006 eq. 10; C.-G. Kim+ 2010 eq. 7; Kim+ 2020 eq. 12]
    F = m|Phi_0|/(v_c^2 tan p)               [verified: Kim & Kim 2014, arXiv:1402.2291, eq. 5]
"the amplitude of the perturbed radial force 2 pi|Phi_0|/L_x as a fraction of the mean axisymmetric gravitational
force field (Roberts 1969)", L_x = 2 pi R_0 sin i/m. Adopted: F <= 3 % for razor-thin models (Kim & Ostriker 2006 on
their Paper I); 0, 0.1, 0.2 (Kim+ 2020); "We vary F from 5 to 20 %", M83 "F ~ 5-10 %" (Kim & Kim 2014); 5 % solar
neighbourhood (Shu+ 1973). CO arm-to-interarm ~5 in M51 (Shetty+ 2007) against ~20 in isothermal models (Kim & Kim
2014). Gomez & Cox 2002: stellar arm amplitude ~52 % of the disc at 8 kpc gives "a peak to valley potential difference
of about (30 km/s)^2", "consistent with" K-band arm/interarm 1.8-3 [all verified as quoted].
None derives F from a stellar surface-density amplitude or puts the stars' thickness into F.
[inferred: Phi_m = 2 pi G Sigma_m T(k)/k with k = m/(R sin i) gives F_m = (m/sin i) Phi_m/(R^2 Omega^2)
= 2 pi G Sigma_m T(k)/(R Omega^2); m and sin i cancel - the thin-disc force of a WKB wave is 2 pi G Sigma_m whatever k
(Toomre eq. 17). With X = kappa^2 R/(2 pi G Sigma_0), A_m = Sigma_m/Sigma_0: F_m = (kappa/Omega)^2 A_m T(k)/X, i.e.
2 A_m T/X for a flat rotation curve. Thickness enters only through T(k), which brings m and i back.]
#### 3.5 Arms that corotate with the material
- Wada, Baba & Saitoh 2011 (ApJ 735, 1; arXiv:1104.1287), live stellar disc: "The stellar spiral arms and the
  interstellar matter on average corotate in a galactic potential at any radii. Unlike the stream motions in the
  galactic shock, the interstellar matter flows into the local potential minima with irregular motions. The flows
  converge to form dense gas clouds/filaments near the bottom of the stellar spirals"; "from both sides"; relative
  speeds ~15 km/s or less, "comparable to the random motion of the gas"; stars smooth, gas "more spiky" [verified].
- Dobbs & Baba 2014 sect. 3.7: "there is no gas flow through the arms"; "For dynamic arms, a systematic offset is not
  expected between the density peak of the gas, and the stellar minimum"; "the gaseous arm remains until the stellar
  arm disperses" and may outlast it; "Gas can still clearly undergo shocks as it falls into the minimum of the
  potential, particularly if it has cooled"; "substructure due to resonances cannot occur"; regular spurs "less
  likely", branches possible [verified].
- Baba, Morokuma-Matsui & Egusa 2015 (arXiv:1505.02881): steady spirals - dust lanes downstream inside, upstream
  outside, a radial trend depending "on neither the strength nor the pitch angle"; dynamic spirals - "the dust lanes
  are along with stellar spiral arms", "no systematic radial dependence of the arm-gas offsets, since the gas motions
  follow large-scale colliding flows" [verified].
- Not in these three: any number or formula for the gas-to-stellar arm CONTRAST in corotating arms.

### 4. Observers' conversion from stellar light to force, with thickness
Laurikainen & Salo 2002 (arXiv:astro-ph/0209214), sect. 3, after Quillen+ 1994:
    Phi(x, y, z=0) = -G Double-Integral Sigma(x', y') g(x - x', y - y') dx' dy'  (2);   g(dr) = Integral rho_z(z) (dr^2 + z^2)^(-1/2) dz  (3)
rho_z normalised: exponential exp(-|z/h_z|)/(2 h_z) (4); sech^2(z/h_sech2)/(2 h_sech2) (5); sech (6); Gaussian (9);
uniform slab (10). "Usually ... h_sech2 is set equal to 2 h_z, to yield a same slope at large z"; scale factors
"chosen in a manner that yields the same vertical dispersion as the exponential model ... <z^2 rho_z>/<rho_z> =
2 h_z^2. In this case h_gauss/h_z = sqrt2, h_sech2/h_z = sqrt24/pi, h_sech/h_z = sqrt8/pi, h_uni/h_z = sqrt6" (11);
"the convolution function depends very little on the model used for the vertical mass distribution as long as models
with a same vertical dispersion are compared"; "The difference in g(dr) is significant only for dr < h_z" [verified].
Evaluated in the central plane per Fourier component m (Diaz-Garcia+ 2016 eq. 8) - the real-space twin of T_mid
[inferred: the planar Fourier transform of g is (2 pi/k) Integral rho_z exp(-k|z|) dz].
By m (NGC 1433, exponential profile, sect. 4.1): "For h_r/h_z = 2.5 about 75 % of the tangential force is due to the
m=2 density component, and with the inclusion of the m=4 component Q_b increases to 97 %"; "in the case of
h_r/h_z = 10, Q_b = 70 %, 90 %, 98 % of its maximum value, when including the density components up to m_max = 2, 4,
6"; "planar density variations correspond to force variations only if their planar scale significantly exceeds h_z:
smaller h_r/h_z thus suppresses the force variations corresponding to large m". At equal dispersion "a more centrally
peaked vertical profile yields a slightly larger Q_b": exponential against uniform 15 % at h_r/h_z = 2.5, against
isothermal "only 5 %"; the scatter of h_r/h_z "for Sc-galaxies induces an uncertainty of about 15 % in Q_b" [verified].
Diaz-Garcia+ 2016 sect. 3.1: nominal assumptions "(1) the mass-to-light ratio is constant, (2) the vertical profile
follows an exponential law, (3) the scale height is constant over radius, (4) the scale height is tied to the disk
scale length"; forces recomputed with the extreme h_z of each type bin (Fig. 1: 0.14, 0.20, 0.33 h_R); the 10-15 %
halo correction "is of the same order as the uncertainty associated with estimating the vertical scale height"
[verified]. These are bar torques; no per-m table for spiral harmonics was found.

### What a model could adopt
(i) Thick stellar perturber, force on thin gas at the midplane
- General: T_mid(k) = Integral t_*(z) exp(-|kz|) dz times the thin-disc potential -2 pi G Sigma_m/k (and the force at
  z = 0). [Kim & Ostriker 2007 eq. 3; Wang+ 2010 eqs. 33-34; Behrendt+ 2015 eqs. 1, 3; Toomre 1964 sect. III(e)]
- Exponential stars: T = 1/(1 + k h_*), exact [Kim & Ostriker 2007 eq. 4; Kim+ 2002 sect. 3.2; Kim & Ostriker 2006
  eq. 11]; it is the factor the two-component relations put on the stellar term the gas feels [Kim & Ostriker 2007
  eq. 8; Elmegreen 2011 eq. 19].
- sech^2(z/z0) stars: exact T = 1 - (k z0/2)[H(k z0/4) - H(k z0/4 - 1/2)] [Wang+ 2010 eq. 35]; fit
  T = (1 + 0.3 k z0)/(1 + k z0 + 0.3 (k z0)^2) [Cox & Gomez 2002 eq. 7; equals the exact form to 1.4 %, my arithmetic];
  1/(1 + k z0) is low by up to 13.7 % for this profile [Behrendt+ 2015].
- Per harmonic of a narrow arm: K_n = n N/(R sin alpha), factor 1/D_n(K_n H), cos^2-arm coefficients
  C_n = 8/(3 pi), 1/2, 8/(15 pi) [Cox & Gomez 2002 eqs. 4-8].
(ii) The same layer acting on itself
- Exponential, density-weighted over the layer: 1/(1 + kH) - kH/(2(1 + kH)^2) [J.-G. Kim+ 2012 footnote 1].
- sech^2 layer in its own mode: about 1/(1 + k z0), z0 = Sigma/(2 rho(0)) [Vandervoort 1970 via Romeo 1992 eq. 13 and
  Elmegreen 2011; J.-G. Kim+ 2012 Fig. 5; my integral: within 1 % to k z0 = 0.3, 6.5 % low at 1].
- Uniform slab of half-thickness h, central plane: (1 - exp(-kh))/(kh) [Toomre 1964 eq. 33].
Thickness
- h_R/h_z = 7.3 +- 2.2 (exponential h_z, I band, volume-corrected) [Kregel+ 2002]; by type 4 / 5 / 9 [de Grijs 1998
  via Diaz-Garcia+ 2016]; Milky Way thin disc 300 +- 50 pc, h_R 2.6 +- 0.5 kpc [Bland-Hawthorn & Gerhard 2016].
- Fitted exponential h_z onto sech^2: z0 = 2 h_z (equal outer slope; also Kregel's h_z = 0.5 z0) or z0 = 1.559 h_z
  (equal dispersion) [Laurikainen & Salo 2002 eq. 11].
- Size: T = 0.85 to 0.30 over m = 2-6, pitch 10-30 deg, R = 2-3 h_R at h_z/h_R = 0.137 (section 2, inferred).
NOT established by what was read
- A gas layer of finite thickness in a thicker stellar wave: no source; the two-exponential formula of 1.8 is mine.
- Which mapping of an observed h_z onto the profile is right: at k h_z = 1 it moves the factor between 0.39 and 0.57.
- Any printed formula from stellar arm amplitude to F with thickness: none; the relation in 3.4 is inferred. The
  spiral-shock simulations impose F (3-20 %) and a z-independent arm potential.
- The gas response to a narrow (multi-harmonic) forcing: no analytic result. Printed: the response to a sinusoid is
  already nonlinear, harmonic s at order f^s with resonant denominators [Shu+ 1973]; forcing harmonics raise contrast
  and substructure in simulations [Chakrabarti+ 2003]; Cox & Gomez give the potential, not the response. All for gas
  streaming through a steady pattern.
- Corotating arms: gas converges on the potential minimum from both sides, no systematic offset, no steady galactic
  shock [Wada+ 2011; Dobbs & Baba 2014; Baba+ 2015]; no contrast law or number found.
- Vandervoort 1970, Shu 1968, Binney & Tremaine 2008, Bertin & Lin 1996, Romeo 1994: not read; the first two are
  reported second-hand only.
