# READING_CLUSTERING — how young clusters and clouds are clustered, and how it fades (for BUILD_III Phase L1)

**The lead's note (2026-10-05).** One Opus reader, briefed by BUILD_III §3e and forbidden the repository, wrote
what is below the rule; it is entered as returned, its headings one level down. It was run while S59's closing
suite ran, and is entered on S60's branch so that it is not lost: **Phase L1 runs one session later than the plan
first had it** (the owner's ruling of 2026-10-05, D219: the arms become a census of pieces first). The reader
converted seventeen arXiv PDFs to text and read the passages itself (`[V]`); three sources it reached only through
the fetch tool's summarising model (`[FQ]`), which invented a number once — abstract-level trust.

**What the reading says that the plan's text did not foresee** (the lead's summary; the part below is the record).
(1) *There is no one slope and no one fading age*: the same galaxy reads −0.39 to −1.1 depending on the fit range,
the age cut and a single or a broken law; the randomisation age is 40, 40–60, 50–100 or about 100 Myr by source.
(2) *Every amplitude contains the galaxy's own large-scale structure*: the random catalogues are uniform in the
instrument's footprint, and no spiral has its clusters' correlation measured against a smooth or an arm-modulated
disc — which is the quantity a field of unit mean per cell multiplying an arm pattern would need. (3) *Clouds are
less clustered than young clusters* (about −0.2 against about −0.5), massive clouds as much; clusters leave their
clouds in 2–6 Myr. (4) *No kinematic dispersal is measured anywhere read*: every velocity is a size over an age.
Phase L1's gate ("the census's measured correlation function returns the sourced slope over the sourced range")
can be met only on the finished census, measured as the sources measure it.

---

## Reading notes L1: clustering of young star clusters and GMCs in nearby discs, and its fading with age

Read 2026-10-05, blind to the repository. Sources: arXiv PDFs fetched this session and read as text
(pdftotext); a few pages reached only through the fetch tool's summarising model.

Tags. [V: place] = verified: I read that passage myself this session in the arXiv PDF text of the source
named in the item. [FQ: place] = fetch-quote: the fetch tool's model returned it as a quotation from the
arXiv HTML; I did NOT see the text (that model invented a D2 range for Menon 2021 once, caught against the
PDF) - abstract-level trust. [inferred: ...] = my arithmetic on verified numbers. [not read] = cited only.
Journal volume/page as shown by a search result or the PDF header; "(ref from memory)" where not.

Convention in every source: 1 + omega(theta) = A theta^alpha, alpha < 0, D2 = alpha + 2 (D2 = 2 is
unclustered). LS = Landy-Szalay estimator. "Uniform random" = Poisson points filling the instrument
footprint. That is not a smooth disc: every amplitude and every large-scale slope below contains the
galaxy's own large-scale structure unless stated otherwise.

### Nothing readable found (or only partly)
- Efremov 1995 (AJ 110, 2757), the 80 / 250 / 600 pc ladder, and Elmegreen & Efremov 1996 (ApJ 466, 802):
  [not read] (ADS refused the fetch). The 80 pc association size, "300 pc to 1 kpc" complexes and the
  size-duration relation were read only as restated in Efremov & Elmegreen 1998.
- GMC two-point correlation in the LMC: nothing read. M 51/PAWS only through Grasha 2019.
- Over the fetch size limit, so [FQ] only: Gouliermis 2018 review (PASP 130, 072001; arXiv:1806.11541);
  He et al. 2026 (PHANGS-ALMA, arXiv:2604.07450). Shashank et al. 2025 (UVIT, arXiv:2412.00872, A&A
  accepted) exists: abstract only, [FQ]. Bastian et al. on M 33 (2007): [not read].
- No kinematic measurement of field stars or clusters dispersing from their birth sites was found. Every
  km/s number below is a size/age ratio, a crossing-time argument or a model fit; each is marked.
- Per-galaxy correlation lengths R0 of Grasha 2017a are in its Fig. 10 only (not tabulated).

### 1. Two-point correlation of young star clusters

#### 1.1 Grasha et al. 2015, ApJ 815, 93 (arXiv:1511.02233) - NGC 628
- What: angular, not deprojected ("nearly face-on"), LS, uniform random 100x the sample with chip-gap
  masks; 8 log bins, 0.16"-200" = 4.8 pc - 9.6 kpc; d = 9.9 Mpc; two WFC3 pointings [V: sect. 4].
  Classes: 1 symmetric, 2 asymmetric (both taken as bound), 3 multi-peak (taken as associations), 0 not
  inspected [V: sect. 5.1, Table 1 note]. Ages/masses least reliable below ~5000 Msun [V: sect. 3].
- Table 1 [V]: A1, alpha1 | break | A2, alpha2. A = 1+omega at 1" [inferred: fit form eq. 4, and 2017a].
  - Class 1 (N=420): 2.24(3), -0.14(3), single law
  - Class 2 (432): 5.31(3), -0.82(10) | 3.3" | 2.76(2), -0.17(2)
  - Class 3 (412): 8.17(7), -1.51(13) | 1.2" | 3.4(2), -0.37(5)
  - Class 1,2,3 (1264): 3.91(19), -0.65(9) | 3.3" | 2.29(2), -0.18(2)
  - Class 0 (384): 3.44(5), -0.20(2), single
- 3.3" = 158 pc; class 3 breaks at 58 pc [V: sect. 5.1, 5.1.1]. "Weighted mean" slope ~ -0.8 below the
  break, ~ -0.18 above [V: abstract, sect. 5.1]. The break moves between 2" and 14" (96-672 pc) as the
  number of bins goes from 5 to 20 [V: sect. 5.1.2]; read by the authors as the disc's line-of-sight
  thickness, quoted 0.25 kpc, "a factor of two different" [V: sect. 6].
- Mass: "little effect" [V: abstract]; split at log M = 3.6 [V: sect. 5.3].

#### 1.2 Grasha et al. 2017a, ApJ 840, 113 (arXiv:1704.06321) - six LEGUS galaxies
- Sample [V: Table 1]: NGC 7793 (3.44 Mpc, i 47.4), NGC 3738 (4.90, Im), NGC 6503 (5.27, i 70.2),
  NGC 3344 (7.0), NGC 628 (9.9), NGC 1566 (13.2). 3685 objects = 2323 compact (class 1,2) + 1362
  associations (class 3), M_V < -6 [V: sect. 7]. No mass cut (tested, not needed) [V: sect. 4].
- What: angular LS, uniform random; deprojected only for i > 40 deg (7793, 3738, 6503) [V: sect. 4,
  Fig. 5 caption]. Fitted up to R0, where 1+omega = 1 [V: sect. 5.1].
- Table 3 [V], classes 1,2,3, all ages, theta in arcsec:
  - NGC 7793 (350): 14.0(6), -1.16(5), single        - NGC 3738 (281): 3.27(3), -0.394(12), single
  - NGC 6503 (298): 3.97(19), -0.46(6), single       - NGC 1566 (1101): 6.06(6), -0.492(13), single
  - NGC 3344 (391): 4.7(3), -1.68(13) | 1.3" | 3.37(13), -0.42(3)   (1.3" = 44 pc [inferred: 33.9 pc/"])
  - NGC 628 (1264): 4.81(5), -0.75(4) | 3.3" | 2.39(5), -0.16(2)
  Inner slope across the six: -0.39 to -1.68, median -0.62 [inferred: from Table 3].
- Table 4 [V], pair-weighted average of the six, R in pc: A1, alpha1 | break (pc) | A2, alpha2.
  - All ages. Class 1: 62(2), -0.86(2) | 59 | 3.2(3), -0.14(3). Class 2: 63(3), -0.73(7) | 112 | 4.8(3),
    -0.18(3). Class 3: 463(40), -1.13(7) | 112 | 6.6(4), -0.23(7). Class 1,2: 25(4), -0.58(4) | 93 |
    3.6(2), -0.15(2). Class 1,2,3: 69(5), -0.77(7) | 112 | 4.0(3), -0.17(4).
  - Age <= 40 Myr. Class 1: 52(10), -0.66(14) | 128 | 6.4(3), -0.23(3). Class 2: 119(15), -0.83(3) | 112 |
    8.1(5), -0.26(2). Class 3: 565(18), -1.15(13) | 112 | 7.3(4), -0.232(16). Class 1,2: 39(2), -0.60(3) |
    186 | 3.51(13), -0.139(19). Class 1,2,3: 115(6), -0.85(3) | 112 | 5.6(3), -0.21(2).
  - Age > 40 Myr, single law. Class 1: 2.45(14), -0.13(2). Class 2: 3.98(10), -0.160(18). Class 3: 3.3(3),
    -0.161(14). Class 1,2: 2.90(13), -0.130(18). Class 1,2,3: 2.61(15), -0.164(6).
- What Table 4 implies for classes 1,2,3 [inferred: A R^alpha; the two branches meet at 112 pc]:
  <= 40 Myr: 1+omega = 16 at 10 pc, 2.1 at 112 pc, 1.3 at 1 kpc, reaching 1 near 3.6 kpc;
  > 40 Myr: 1.8 at 10 pc, 1.2 at 100 pc, reaching 1 near 350 pc.
- The paper disagrees with itself; not reconciled here: the text gives a global slope -0.83 and class
  slopes -0.85 / -0.57 / -0.18 / -1.12 [V: sect. 5.4, 6]; Table 4 gives -0.77 and -0.73 / -0.58 / -0.86 /
  -1.13; the summary prints "ages less than 40 Myr" for the table's > 40 Myr slopes [V: sect. 7].
- Amplitude at a fixed scale rises with host luminosity (lowest NGC 3738; highest NGC 1566, possibly a
  distance artefact); R0 larger in bigger, higher-SFR galaxies, no trend with Sigma_SFR [V: sect. 5.3, 6].

#### 1.3 Menon et al. 2021, MNRAS (ref from memory: 507, 5542; arXiv:2108.04387) - twelve LEGUS galaxies
- What: LS; every galaxy deprojected; uniform Poisson random in the HST footprint, ACS chip gaps masked;
  20 log bins over 10-5000 pc; classes 1+2+3 together [V: sect. 2.2.4, 3.1, 3.2, 4.1]; M_V < -6 and
  4-band detection [FQ: sect. 2.2.4]. Models chosen by AIC: S single law, PW two laws with break beta,
  PF law times exp(-theta/theta_c) [V: Table 2 notes].
- Table 2, young (T < 10 Myr) [V]: model, alpha1 (, alpha2, beta):
  0628 PW -1.1(0.14), -0.3(0.02), 3.9" | 1313 S -0.6(0.03) | 1566 S -0.5(0.02) | 3344 PW -1.4, -0.5, 2.2" |
  3627 S -0.4(0.04) | 3738 PF -0.1 | 4449 PW -0.5, -2.4, 74" | 5194 S -0.4(0.01) | 5253 PF -0.6 |
  5457 PW -0.6, -0.2, 14" | 6503 PW -0.6, -0.2, 28" | 7793 PW -1.5, -0.3, 5.8".
- Table 3 [V: raw text order]: D2 of the young clusters, l_corr (largest hierarchical scale, pc):
  0628: 0.9(0.14), 190 (+70 -40) | 1313: 1.4, > 960 | 1566: 1.5, > 1730 | 3344: 0.6, 110 (+100 -30) |
  3627: 1.6, > 2020 | 3738: 1.9, none | 4449: 1.5, < 1440 | 5194: 1.6, > 2700 | 5253: 1.4, < 410 |
  5457: 1.4, 450 (+160 -200) | 6503: 1.4, 845 (+407 -244) | 7793: 0.5, 101 (+30 -25).
  Model-S values are lower limits set by the footprint; PF values upper estimates [V: Table 3 notes].
- D2 "in the general range 0.5-1.6" without NGC 3738 [V: sect. 4.4.2], "0.5-1.9" [V: summary iii];
  median 1.4 [inferred: twelve values]. l_corr "from ~100 pc to scales beyond ~2.5 kpc" [V: summary
  iii]; the text also says "upwards of 3000 pc in NGC 5194" against the table's > 2700 [V: sect. 4.4.1].
- l_corr against stellar mass r=0.65 (p=0.03), SFR_UV 0.56 (0.07), Sigma_SFR 0.69 (0.02), R25 0.17 (0.62),
  Toomre length 0.75 (0.01) [V: sect. 4.4.1]. Beyond the break: "not entirely Poissonian" [V: sect. 4.2.3].

#### 1.4 Turner et al. 2022, MNRAS 516, 4612 (arXiv:2209.02872) - eleven PHANGS galaxies
- Sample [V: Table 1]: 9.84-19.57 Mpc; 6248 clusters (classes 1,2,3), 8336 GMCs; clusters below
  10^3-10^4 Msun not seen [V: sect. 4.4]. Angular LS, not deprojected (i <~ 60 deg, "minimal impact"),
  uniform random within the HST-ALMA overlap [V: sect. 3.2]. One power law over a per-galaxy range
  marked only in Fig. 10 [V: Table 4 caption] - the fit range in pc is not printed.
- Table 4 [V]: slope alpha, then amplitude = 1+omega at 300 pc.
  | NGC | all | <=10 Myr | >10 Myr | GMCs | amp all | amp <=10 | amp >10 | amp GMC |
  | 0628 | -0.28(2) | -0.39(5) | -0.20(3) | -0.24(4) | 2.20 | 2.46 | 1.86 | 2.15 |
  | 1365 | -0.41(3) | -0.66(9) | -0.33(2) | -0.47(11) | 5.75 | 9.98 | 5.04 | 4.97 |
  | 1433 | -0.38(2) | -0.55(2) | -0.28(17) | -0.82(14) | 2.86 | 4.43 | 1.44 | 7.96 |
  | 1559 | -0.32(2) | -0.49(3) | -0.22(2) | -0.22(2) | 3.51 | 3.77 | 3.05 | 1.88 |
  | 1566 | -0.44(2) | -0.73(5) | -0.36(2) | -0.26(3) | 3.64 | 5.52 | 2.92 | 2.19 |
  | 1792 | -0.36(6) | -0.51(5) | -0.32(6) | -0.49(6) | 3.29 | 3.43 | 2.78 | 2.27 |
  | 3351 | -0.73(10) | -0.84(15) | -0.29(11) | -0.76(2) | 3.12 | 3.85 | 1.61 | 1.83 |
  | 3627 | -0.38(1) | -0.47(3) | -0.38(2) | -0.08(2) | 2.84 | 3.28 | 2.73 | 1.60 |
  | 4535 | -0.41(4) | -0.73(6) | -0.25(3) | -0.23(2) | 1.90 | 2.89 | 1.52 | 1.90 |
  | 4548 | -0.34(3) | -0.50(4) | -0.24(2) | -0.16(4) | 2.33 | 2.99 | 1.89 | 2.44 |
  | 4571 | -0.11(3) | -0.14(8) | -0.28(11) | -0.59(11) | 1.36 | 1.23 | 2.26 | 2.67 |
- Medians [inferred: from Table 4]: slope all -0.38; <=10 Myr -0.51 (range -0.14 to -0.84); >10 Myr -0.28
  (-0.20 to -0.38); GMCs -0.26 (-0.08 to -0.82). Amplitude at 300 pc: 3.4, 2.3, 2.2 respectively.
- Correlation lengths (1+omega = 1) "equal for both populations", several kpc [V: sect. 4.4].

#### 1.5 Lapeer et al. 2026, AAS journal, accepted 2026-01-15 (arXiv:2601.11434, FEAST) - JWST + HST
- NGC 628 (9.84 Mpc), NGC 4449 (4), M 51 (7.5), M 83 (4.7); emerging (IR-detected) plus optical clusters;
  LS; only NGC 4449 deprojected; complete to ~10^3 Msun [V: sect. 2, 3.1, 3.2].
- Tables 3-4 [V: raw column order; alpha1 + 2 = D2 checked row by row]. D2 (alpha1) in age bins
  (0,10], (10,100], (100,300] Myr:
  NGC 628: 1.24 (-0.761), 1.82 (-0.18), 1.80 (-0.205); youngest bin breaks at 218 pc
  M 51: 1.51 (-0.49), 1.68 (-0.315), 1.86 (-0.14)        M 83: 1.45 (-0.546), 1.62 (-0.376), 1.75 (-0.248)
  NGC 4449: 1.27 (-0.728), 1.60 (-0.401), 1.53 (-0.47)
  The "only good estimate of l_corr" is NGC 628, 210-300 pc [V: sect. 4.4.2].

#### 1.6 Older measurements
- Zhang, Fall & Whitmore 2001 (ApJ, ref from memory 561, 727; astro-ph/0105174), Antennae (a merger),
  19.2 Mpc: xi(r) itself is fitted, after subtracting the correlation of a 3 kpc-smoothed map; power law
  to ~8" = 0.74 kpc (uncorrected ~15" = 1.4 kpc); indices -0.83 (R, <~5 Myr), -1.06 (B1, 3-16 Myr), -0.89
  (B2, 16-160 Myr); candidate young massive stars -0.41 [V: sect. 3, 4].
- Scheepmaker et al. 2009, A&A 494, 81 (arXiv:0812.1417), M 51 at 8.4 Mpc, 1580 clusters: surface-density
  autocorrelation, "arbitrary" absolute scaling, no random catalogue; fitted over 4" < r < 50" (160 pc -
  2 kpc). Samples 1 (<10 Myr) and 2: ~ -0.4. Sample 3 (log age >= 7.5): ~ -0.8 with Geneva isochrones,
  ~ -0.4 with Padova. Sample 1 limited to log M > 3.7: -0.8 or -0.7 [V: sect. 5.3].
- Shashank et al. 2025, star-forming clumps (not clusters), four spirals, UVIT: hierarchy up to a maximum
  scale of 0.5-3.1 kpc, smallest in NGC 7793 [FQ: abstract only].

#### 1.7 Conflicts, side by side (young clusters, same galaxy)
- NGC 628: -0.65(9) below 158 pc, all ages (1.1) | -0.75(4) below 158 pc (1.2) | -1.1(0.14) below 190 pc,
  D2 0.9 (1.3) | -0.39(5), one law (1.4) | -0.76 below 218 pc, D2 1.24 (1.5), whose authors say the 0.9
  "may have been biased due to incompleteness" [V: Lapeer sect. 4.4.1].
- NGC 7793: -1.16(5), one law (1.2) | -0.35(2) over 40-800 pc in the ALMA field (3.1) | -1.5 below 101 pc
  then -0.3 (1.3).
- NGC 1566: -0.492(13) at 13.2 Mpc (1.2) | -0.5(0.02) at 17.7 Mpc (1.3) | -0.73(5) for <= 10 Myr, -0.44 all,
  at 17.69 Mpc (1.4). Gouliermis 2017 adopts 10 Mpc for the same galaxy.
- M 51, < 10 Myr: -0.40(5), class 1,2 only (2) | -0.4(0.01) (1.3) | -0.49 (1.5) | ~ -0.4, or -0.8 mass-limited.
- Universal D2 or not: Scheepmaker and Lapeer argue for a common value (1.2-1.6; ~1.3); Menon and Grasha
  2017a find galaxy-to-galaxy variation "well beyond" the errors.

### 2. Change with cluster age

- NGC 628 (1.1): transition begins at 20 Myr, non-clustered distribution "in place by ages of 40 Myr";
  the 40 Myr boundary carries the catalogue's age uncertainty, 40 (+20 -10) Myr; class 3 "only minimally
  affected" by the age cut [V: sect. 3, 5.2, 6].
- Six galaxies (1.2): "more homogeneously distributed after ~40-60 Myr and on scales larger than a few
  hundred parsecs" [V: abstract]; "older than 20-60 Myr" [V: sect. 5.2]. Table 4: inner slope -0.85 ->
  -0.164; 1+omega at 10 pc 16 -> 1.8 [inferred]. Class 1,2 older than 40 Myr are flat down to ~10 pc;
  class 3 older than 40 Myr are absent within 100 pc of each other [V: sect. 5.4]. Strongest age effect
  in NGC 3738, strong in NGC 628 and 1566, "only a slight change" in NGC 7793, 6503, 3344 [V: sect. 5.2].
  "Primarily governed by age", not mass [V: sect. 7]; class 1 less clustered than class 3 even below
  40 Myr [V: sect. 6].
- M 51 (Grasha et al. 2019, MNRAS 483, 4707, arXiv:1812.06109; class 1,2 only; 7.66 Mpc), Table 2 [V],
  whole galaxy: N, A, alpha (the separation unit behind A is not stated in the caption):
  all 2862: 5.4(0.5), -0.21(0.03) | <= 10 Myr 1031: 23(3), -0.40(0.05) | 10-50 Myr 548: 13(2), -0.34(0.05) |
  50-100 Myr 439: 2.7(0.2), -0.12(0.04) | > 100 Myr 844: 2.1(0.2), -0.07(0.03) |
  R_gc <= 4 kpc 1308: 4.5(0.8), -0.23(0.04) | > 4 kpc 1554: 14.9(0.9), -0.32(0.02).
  "Randomization timescale" 50-100 Myr; "consistent with a randomized distribution after 100 Myr"
  [V: sect. 4.2.1, Fig. 10 caption]. Inner-galaxy clusters sit in smaller complexes [V: abstract].
- M 51 (1.3), four bins: alpha1 = -0.55 (< 2 Myr), -0.38 (2-10), -0.28 (10-100, with exponential
  fall-off), ~ -0.05 (> 100 Myr; only the disc's radial profile left); "similar qualitative behaviour" in
  NGC 1313, 1566, 0628 [V: sect. 4.3, Fig. 3 legend]. Old (> 10 Myr) clusters are model PF in all nine
  galaxies that have enough, alpha1 from -0.0 to -0.4 [V: Table 2]. Convergence to the smooth-disc
  residual "in ~100 Myr" [V: abstract]; the time "will also depend on the host galaxy" [V: sect. 4.3].
- PHANGS (1.4): only <= 10 against > 10 Myr (medians -0.51, -0.28); reversed in NGC 4571 alone; "No
  significant differences ... if the age threshold is lowered to 5 Myr" [V: sect. 4.4, fn. 2].
- FEAST (1.5): two-bin reading "randomization timescale of order ~10 Myr"; three-bin reading, (10,100]
  Myr "still exhibit some degree of hierarchical structure", "effectively random after ~100 Myr"; NGC 628
  random by ~10 Myr; NGC 4449 (dwarf, little shear) keeps structure past ~100 Myr [V: abstract, sect. 4, 5].
- Conflict, not reconciled: 40 Myr (1.1) | 40-60 or 20-60 Myr (1.2) | 50-100 Myr (M 51, Grasha 2019) |
  ~100 Myr (Menon) | ~10 or ~100 Myr by binning (FEAST) | "dissipates within 10 to 50 Myr" for clumps
  (Shashank [FQ: abstract only]). Scheepmaker's old sample is STEEPER than the young one with one
  isochrone set, while lower in amplitude.

#### Age difference against separation
- LMC (Efremov & Elmegreen 1998, MNRAS 299, 588, astro-ph/9805259; Bica et al. clusters, d = 45 kpc,
  S = 0.01-1 deg): log dt(yr) = 7.48 + 0.33 log S(deg) for 1-100 Myr (5509 pairs, r = 0.88); slope 0.38
  for 10-100 Myr, 0.42 for 1-1000 Myr; dt(Myr) ~ 3.3 S(pc)^0.33 over 15-780 pc; 1-10 Myr not significant
  [V: sect. 2, eqs. 1-4]. Cepheids (older than 27 Myr, most ~100 Myr): no relation, "consistent with
  noise" [V: sect. 1, 3].
- Eight galaxies (Grasha et al. 2017b, ApJ 842, 25, arXiv:1705.06281; classes 1,2,3, ages < 300 Myr, no
  mass cut, deprojected): dt = A1 R^alpha up to R_max, flat beyond. Table 2 [V]:
  | galaxy | A1 | alpha | max dt (Myr) | R_max (pc) | R_max/dt (km/s) | shear v_S (km/s) |
  | NGC 7793 | 4.0(0.3) | 0.47(0.06) | 48(19) | 203(30) | 4.0(1.1) | 2.0 |
  | NGC 1313 | 16(1) | 0.26(0.08) | 85(26) | 585(183) | 6.1(1.4) | 2.4 |
  | NGC 3738 | 9.0(0.5) | 0.24(0.04) | 45(9) | 869(152) | 15(2) | 5.0 |
  | NGC 6503 | 1.7(0.3) | 0.6(0.2) | 62(21) | 275(104) | 5.7(2.5) | 1.9 |
  | NGC 3344 | 1.0(0.2) | 0.6(0.2) | 41(14) | 338(131) | 8.5(3.1) | 3.7 |
  | NGC 5194 | 6.8(1.0) | 0.36(0.07) | 83(20) | 947(231) | 13(3) | 5.5 |
  | NGC 628 | 7.4(0.6) | 0.33(0.07) | 66(18) | 788(179) | 13(4) | 6.9 |
  | NGC 1566 | 2.3(0.2) | 0.41(0.14) | 30(9) | 508(179) | 20(7) | 10 |
  Medians [inferred]: alpha 0.385, R_max 547 pc, max dt 55 Myr, velocity 10.8 km/s. Stated: power
  0.25-0.6, R_max ~200 pc to ~1 kpc, dt 20-100 Myr [V: abstract, sect. 3.1]. Velocity correlates with
  R25 (r = 0.98) and SFR (0.86); velocity/v_S independent of R_max [FQ: sect. 3.3]. Dropping clusters
  under 10 Myr flattens the relation; 300 Myr samples are flatter than 100 Myr ones [V: sect. 3.4].
  Milky Way pairs: power 0.40 +- 0.08 [V: sect. 1]. The velocity is a size/age ratio, not a drift.

### 3. Giant molecular clouds; clusters against clouds

#### 3.1 GMC autocorrelation
- NGC 7793 (Grasha et al. 2018, MNRAS, ref from memory 481, 1016; arXiv:1808.02496; ALMA CO(2-1) at
  15 pc; LS, uniform random in the ALMA footprint; fits over 40-800 pc where 1+omega > 1), Table 2 [V]:
  clusters all 293: 8.3(0.2), -0.35(0.02) | clusters >= 1000 Msun and <= 10 Myr, 54: 20(3), -0.45(0.06) |
  GMCs all 534: 3.2(0.2), -0.18(0.02) | GMCs >= 3.3e4 Msun, 259: 5.2(0.2), -0.25(0.02) |
  GMCs >= 1e5 Msun, 85: 18.6(1.4), -0.44(0.03). (The abstract prints +-0.03 and +-0.04 on rows 1 and 3.)
- M 51 PAWS field (Grasha 2019), fits over 100-3000 pc, Table 2 [V]: clusters 1268: 4.1(0.8), -0.19(0.05) |
  <= 10 Myr 536: 8(1), -0.28(0.04) | and > 5e3 Msun 330: 10(1), -0.31(0.04) | and > 3e4 Msun 72: 43(15),
  -0.46(0.13) | GMCs 1507: 2.3(0.2), -0.09(0.03) | > 5e5 Msun 1070: 2.5(0.3), -0.11(0.04) | > 3e6 Msun
  338: 8.4(1.0), -0.27(0.04) | > 5e6 Msun 169: 20(3), -0.35(0.05). GMC correlation length "5000 pc",
  the clusters' in the same field "a few hundred parsec"; the GMCs resemble clusters older than 100 Myr
  [V: sect. 4.2.2].
- PHANGS (1.4; CPROPS clouds at 1", median radius 60.5 pc [V: sect. 3.1], completeness 4.7e5 Msun [FQ]):
  slopes in the table above; "closer to randomly distributed" than young clusters in most galaxies; the
  turn-down below ~2 R_GMC is the cloud finder merging neighbours [V: sect. 4.4]. Not split by mass.
- M 33 (Peltonen et al. 2023, MNRAS, doi stad1430; arXiv:2305.03618; 444 GMCs at 35 pc, 1214 clusters
  with CMD ages; deprojected; LS against 100 random EXPONENTIAL-DISC catalogues, fitted scale lengths
  1.6 / 3.2 / 5.8 / 2.5 kpc for youngest / medium / oldest clusters / GMCs): GMCs anticorrelated below
  50 pc (the finder's minimum peak spacing), uncorrelated beyond 100 pc; cutting at 3.6e4 Msun "has very
  little effect"; clusters <= 10 Myr and medium-aged are correlated only below ~100 pc, the oldest at no
  scale [V: sect. 3.1-3.2]. No power law is fitted.
- 40 PHANGS-ALMA galaxies (He, Leroy, Rosolowsky et al. 2026; 8984 GMCs, common 150 pc resolution,
  deprojected, LS): against a flat random, peak 1+omega ~ 2.3 and median index -0.25 over the trusted
  500-1000 pc (quartiles -0.1 to -0.5), flat below ~500 pc; against a control following the kpc-scale CO
  intensity, peak 1.3 and index ~0 [FQ: abstract, 2PCF section].
- Conflict: massive clouds more clustered in NGC 7793 and M 51; a mass cut changes nothing in M 33 ("We
  see this effect with the clusters but not with the GMCs" [V: Peltonen sect. 3.2]).
- Conflict of normalisation: exponential-disc randoms leave M 33's young clusters correlated only below
  ~100 pc; uniform randoms leave NGC 7793, M 51 and PHANGS clusters correlated to ~1000 pc (Peltonen's
  own comparison [V: sect. 3.2]); He 2026 shows the same for clouds [FQ].

#### 3.2 Clusters against clouds
- NGC 7793 [V: Grasha 2018 sect. 4.1, Table 1]: median age 2(1) Myr within 1 R_GMC (13 clusters), 2(1) at
  1-2 R_GMC (31), 3(2) at 2-3 (25), 7(1) unassociated (224), 6(1) all (293); every cluster still inside a
  GMC is younger than 11 Myr. Nearest-GMC distance 53+-5 pc all, 41+-4 (< 10 Myr), 66+-5 (> 10 Myr);
  older clusters as random. Departure in 2-3 Myr. Distance/age for the 69 within 3 R_GMC: 6.2+-0.9 km/s,
  described as mostly the cloud's erosion speed "with a component of dynamical motions".
- M 51 [V: Grasha 2019 abstract, sect. 4.1, Fig. 6 caption]: median age 4 (+1 -2) Myr within 1 R_GMC (129
  clusters), 6 (+2 -1) at 1-2, 30 (+7 -10) at 2-3, 50 (+20 -10) unassociated, 30+-6 all. "After 6 Myr,
  the majority of the star clusters lose association." Nearest-GMC distance 66+-2 pc inside 2.7 kpc
  (59+-2 young, 74+-4 old), 132+-6 pc outside (118+-9, 143+-7). Same distance/age construction: 9.5 km/s.
- PHANGS [V: Turner Table 2, sect. 4.2, 4.5]: ensemble median age 1 Myr within 1 R_GMC (232 clusters), 4
  at 1-2 (666), 5 at 2-3 (1041), 46 unassociated (2526), 19 all; per galaxy the 2-3 R_GMC median is
  4-6 Myr: "after 4-6 Myr the star clusters are no longer associated with any gas clouds". Median
  nearest-GMC separation 1.8" (NGC 1559) to 4.9" (NGC 4571), ~170 to ~350 pc [inferred: Table 1
  distances]. Cross-correlation functions "prove to be difficult to interpret"; no fit is given.
- M 33 [V: Peltonen abstract, sect. 3.1, 3.3, 5]: nearest CO peak at a median 90 pc (IQR 60) for clusters
  <= 10 Myr, 100 pc (IQR 80) medium, 120 pc (IQR 100-120) old = the random value. Cross-correlation
  present for <= 10 Myr over 40-158 pc, gone by ~18 Myr and beyond ~200 pc; 4-6 Myr inside the parent
  cloud; GMC lifetime 11-15 Myr. 200 pc / 18 Myr = 10 km/s, "should be seen as an upper limit"; a mock
  drift MODEL matched to the cluster autocorrelation gives a 2D dispersion of 5-10 km/s. M 31: no
  significant cluster-cloud correlation at any age.
- Conflict: unassociated clusters' median age 7 Myr (NGC 7793), 50 Myr (M 51), 5-136 Myr across PHANGS
  [V: Turner sect. 4.2]: it follows the catalogue's age mix, it is not a departure time.

### 4. Sizes of associations and complexes against age

- OB associations: "measured characteristic size ... ~80 pc" (attributed to Lucke & Hodge 1970; Efremov,
  Ivanov & Nikolov 1987); with dt = 3.3 S^0.33 their star formation lasts ~14 Myr; star complexes "300 pc
  to 1 kpc" take ~30 Myr; schematic durations 0.1, 1, 3, 10, 30 Myr for clumps, T Tauri associations, OB
  subgroups, OB associations, star complexes [V: Efremov & Elmegreen 1998 sect. 4 items 3-4, Fig. 8
  text]. "80-100 pc" associations and "0.5-1 kpc" complexes in the Galaxy, M 31, M 33, LMC
  [FQ: Gouliermis 2018 sect. 2.1, 2.3, citing Efremov 1989].
- Size-duration: crossing time t(Myr) ~ 0.7 S(pc)^0.5 from sigma = 0.7 S^0.5 km/s (Milky Way clouds); star
  formation lasts ~2.5 crossing times; the measured cluster relation is shallower, 0.33-0.42
  [V: Efremov & Elmegreen 1998 eqs. 6-7, sect. 4]. Square-root form: ~1.75 S^0.5 Myr [inferred: 2.5 x 0.7].
- Measured, PHANGS associations (Larson et al. 2023, MNRAS 523, 6061, arXiv:2212.11425; NGC 3351 at 10 Mpc,
  NGC 1566 at 18 Mpc; watershed on star maps smoothed to 8, 16, 32, 64 pc) [V: Tables 5-6, sect. 5]:
  median log(age/yr), NUV-selected: NGC 3351 6.6 (8 pc), 6.6 (16), 6.7 (32), 6.9 (64); NGC 1566 6.6 (16),
  6.7 (32), 6.85 (64). V-selected: 6.7, 6.7, 6.85, 6.9 and 6.78, 6.85, 6.9. Median effective radius
  12.4 pc (quartiles 10-15) at the 16 pc level, 26 pc (22-32) at the 32 pc level (NGC 3351). So 4 -> 8 Myr
  for a factor 4-8 in scale: age ~ size^0.3 to 0.5 [inferred], over 8-64 pc only.
- Young-star complexes (kernel-density contours; the size scale follows the kernel). NGC 6503: 244
  structures, sizes (2 r_eff) centred on 120 pc, sigma 40 pc, at an 80 pc kernel, ~70 pc at a 40 pc
  kernel, largest over 1 kpc [V: Gouliermis et al. 2015, MNRAS (ref from memory 452, 3508),
  arXiv:1506.03928, sect. 3.3]. NGC 1566: 890 structures, peak 125+-13 pc at a 67 pc kernel, smallest
  ~30 pc, power-law tail; 50-65 % of young stars and ~90 % of young clusters lie inside
  [V: Gouliermis et al. 2017, MNRAS (ref from memory 468, 509), arXiv:1702.06006, abstract, Fig. 7].

### 5. Field (non-cluster) young stars

- NGC 6503 (Gouliermis 2015; ring galaxy, 5.3 Mpc; blue main-sequence stars; surface-density
  autocorrelation; slope fitted for scales <= 20", ~0.5 kpc [inferred: 26 pc/"]), Table 4 [V]: eight
  equal-number (1600-star) magnitude bins: upper age limit (Myr), slope, median MST edge (pc):
  32: -0.693(4), 36.4 | 40: -0.470(7), 47.6 | 50: -0.321(9), 48.7 | 63: -0.289(11), 52.4 |
  71: -0.232(12), 56.4 | 89: -0.233(15), 60.0 | 100: -0.225(16), 59.8 | 112: -0.204(31), 76.0.
  Whole blue sample -0.30 (D2 1.7) over ~20 pc - 2.5 kpc; red (old) stars -0.05 (D2 1.95). "Changes
  significantly ... within the first ~60 Myr", then ~ -0.2 "almost unchanged ... up to ~110 Myr"
  [V: abstract, sect. 4.2, 4.3.1]. The ages are upper limits of magnitude bins: each bin also holds
  younger stars, so a faint bin's residual slope may be theirs.
- NGC 1566 (Gouliermis 2017): bright stars outside the complexes are ~10 Myr older than those inside,
  "a possible minimum timeframe" to leave - or formed in place, "we cannot rule out" [V: sect. 4.3, 5].
  Complex dispersions 0.3-1.7 km/s are derived from mass and size, not measured [V: sect. 3.2].
- SMC (Gieles, Bastian & Ercolano 2008, MNRAS 391, L93, arXiv:0809.2295; MCPS stars in colour-magnitude
  boxes; TPCF and Q): indistinguishable from the background SMC distribution at 75 Myr; matched to a
  crossing time R/sigma with R ~ 2 kpc and field-star sigma = 30 km/s (Evans & Howarth) - an argument; a
  few-km/s drift out of dissolving clusters would need ~1 Gyr, "much longer" [V: abstract, sect. 4].
- LMC (Bastian et al. 2009, MNRAS 392, 868, arXiv:0810.3190; twelve boxes, mean ages 9-1008 Myr; pair
  separations normalised to a centrally concentrated power-law reference, index 0.3): slope and zero
  point flat by 175+-25 Myr (Q: 168+-30); born with 2D fractal dimension ~1.8; crossing time 135-180 Myr
  from sigma ~ 22 km/s and R = 3-4 kpc - an argument; cluster "infant mortality" has "a negligible
  influence" [V: abstract, sect. 5.2, 5.3, 6].
- Dwarfs (Bastian et al. 2011, MNRAS 412, 1539, arXiv:1010.1837; blue helium-burning stars, HST/ACS):
  t_evo ~100 Myr (NGC 2366; "90 Myr" in the discussion), 150 Myr (IC 2574), 225 Myr (Holmberg II,
  NGC 784), 325+-50 Myr (NGC 4068), 350+-75 Myr (DDO 165); all lower limits; no trend with galaxy size
  [V: sect. 5.1-5.6, 6].
- M 31: young stellar structure survives "at least 300 Myr" [FQ: Gouliermis 2018 sect. 3.1.3; V as a
  citation in Grasha 2019 sect. 4.2.1]. LMC Cepheids carry no age-separation relation (sect. 2); the
  authors suggest single stars drift more than clusters. Antennae candidate young stars: index -0.41.
- Velocities offered as arguments, none measured for field stars: "10 km/s can travel 100 pc within
  10 Myr, making a 50 Myr timescale ... entirely reasonable" [V: Grasha 2017a sect. 6]; < 10 km/s gives
  100 and 300 pc at 10 and 30 Myr [V: Scheepmaker sect. 5.3]; 5 km/s gives ~500 pc in 100 Myr [V: Zhang
  sect. 5.3]; Milky Way open clusters, log age < 7.8: sigma 10.6 km/s [V: as cited, Peltonen sect. 5].

### What a model could adopt

All against a UNIFORM random in the footprint unless marked; none has a smooth disc divided out.
1. Young clusters (<= 10 Myr), one law over ~100 pc to a few kpc: -0.5, D2 ~ 1.5 (median -0.51, range
   -0.14 to -0.84, 11 PHANGS galaxies [inferred from Turner T4]; M 51 -0.40(5); Menon's single-law
   spirals -0.4 to -0.6). Where a break is fitted: inner -0.8 (-0.85(3) below 112 pc, six-galaxy
   average <= 40 Myr, Grasha 2017a T4; per galaxy -0.4 to -1.7), outer -0.2 (-0.14 to -0.26).
2. Break / largest hierarchical scale: 100-200 pc where fitted (112 pc average; 158 pc NGC 628; 101-845 pc
   in Menon T3), but four of Menon's nine spirals show none out to 0.96-2.7 kpc. Age-separation
   turnover: median ~550 pc, 203-947 pc (8 galaxies). Grows with stellar mass, Sigma_SFR, Toomre length.
3. Amplitude: 1+omega(300 pc) = 3.4 (<= 10 Myr), 2.3 (> 10 Myr) (PHANGS medians [inferred]; ranges 1.2-10,
   1.4-5.0); six-galaxy <= 40 Myr: 16 at 10 pc, 2.1 at 112 pc, 1.3 at 1 kpc [inferred]. Rises with host
   luminosity. By class below ~100 pc: associations -1.13(7), compact clusters -0.58(4). Cluster mass:
   little effect (NGC 628, six galaxies); steeper for massive young clusters in two CO fields (-0.45).
4. Age decay, the one four-bin series (M 51, Grasha 2019 T2): slope -0.40, -0.34, -0.12, -0.07 and
   amplitude 23, 13, 2.7, 2.1 for <= 10, 10-50, 50-100, > 100 Myr. Three-bin D2 in four galaxies (FEAST):
   1.24-1.51 -> 1.60-1.82 -> 1.53-1.86 for (0,10], (10,100], (100,300] Myr.
5. Gone by: ~40 Myr (NGC 628; six-galaxy cut) to ~100 Myr (M 51, Menon, FEAST); ~10 Myr in one reading of
   NGC 628; not by 100 Myr in the dwarf NGC 4449. The residual slope, -0.1 to -0.2, is the disc's profile.
6. Age difference against separation: dt ~ R^0.4 (median 0.385, range 0.24-0.6, 8 galaxies; LMC 0.33-0.42,
   3.3 Myr at 1 pc), flat beyond R_max where dt ~ 55 Myr (30-85).
7. Clouds: slope about -0.2 (NGC 7793 -0.18(2) over 40-800 pc; M 51 -0.09(3) over 100-3000 pc; PHANGS
   median -0.26, range -0.08 to -0.82; 40-galaxy median -0.25 over 500-1000 pc [FQ]); amplitude at 300 pc
   ~2.2; flat below ~2 cloud radii / ~500 pc (cloud finding, resolution). Against a control following the
   kpc-scale CO map: excess 1.3, slope ~0 [FQ]. Massive clouds: -0.44(3) above 1e5 Msun (NGC 7793),
   -0.35(5) above 5e6 Msun (M 51), matching the young clusters there; not seen in M 33.
8. Clusters leave clouds: median age 1-4 Myr inside one cloud radius, 4-6 Myr at 2-3 radii (PHANGS, M 51),
   2-3 Myr (NGC 7793), 4-6 Myr (M 33); no cluster-cloud correlation after ~18 Myr or beyond ~200 pc
   (M 33). Young clusters lie 40-120 pc from the nearest cloud centre; M 33: 90 pc against 120 pc random.
9. Association size against age: 80 pc <-> ~10-14 Myr, 300 pc - 1 kpc <-> ~30 Myr (Efremov & Elmegreen
   1998, schematic on dt = 3.3 S^0.33). Measured only over 8-64 pc: median age 4 -> 8 Myr (Larson).
10. Field young stars, the one direct series (NGC 6503): slope -0.69 (to 32 Myr), -0.47 (40), -0.32 (50),
    -0.29 (63), then ~ -0.22 from 71 to 112 Myr. Whole-galaxy erasure: 75 Myr (SMC), 175 Myr (LMC),
    100-350 Myr as lower limits (six dwarfs), >= 300 Myr (M 31 [FQ]).
NOT measured in anything read:
- Cluster or cloud correlation normalised to a smooth (exponential or arm-modulated) disc in a spiral,
  except M 33's exponential randoms (no slope fitted) and He 2026's CO-following control [FQ]; nor the
  correlation inside against outside spiral arms, or along against across an arm.
- A randomisation age against cluster mass or boundness (classes only, and only above/below 40 Myr).
- Any drift velocity from kinematics: every km/s value is a size/age ratio, a crossing-time argument, or
  the M 33 mock-drift fit (5-10 km/s). One structure's size followed with age past ~10 Myr. Not printed:
  the fit range in pc of Turner's Table 4 slopes; the separation unit of A in Grasha 2018/2019 tables.
