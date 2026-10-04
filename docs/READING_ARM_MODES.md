# READING_ARM_MODES — how a spiral's amplitude is split among arm numbers, and how that changes with radius (S56, BUILD_III Phase P1)

**The lead's note (2026-10-04).** One Opus reader, briefed by BUILD_III §3e and forbidden the repository, wrote
everything below the rule; it is entered as written. **It is a check, not an input** (BUILD_III §5, Phase P1): the
law — the local swing window's split of the power among m = 2–6 — was ruled before this was read (D215) and is not
adjusted to it. What the comparison says is D215's, at the close.

---

## The reader's note

Nothing under the galaxygen repository was opened and no repository was changed.

**How things were read.** arXiv PDFs were fetched and converted with `pdftotext`; the reader read the text. Those
are tagged `verified`. Three sources were read only through the fetch tool's extraction of the HTML page (quotes
returned, not line-checked); they are tagged `verified-via-extract`.

**Conventions.** A_m = I_m/I_0 is the amplitude of the cos(mφ) term relative to the azimuthal mean at that radius,
unless stated. Rs, Rexp and h all mean disc exponential scale length. These are *amplitude* ratios; a power split
is their square (A3/A2 = 0.58 is a power ratio of 0.34).

### 1. Summary table (read numbers only)

| # | Quantity | Value | Sample, band, radial range | Definition | Source |
|---|---|---|---|---|---|
| 1 | A3/A2 by arm class | flocculent 0.58 ± 0.11; multiple-arm 0.48 ± 0.24; grand design 0.33 ± 0.19 | 46 S4G galaxies (13 F, 20 M, 13 G), 3.6 µm, deprojected, scans in 0.05 R25 steps, often to ~1.5 R25 | Ratio of F_m = sqrt[(ΣI sin mθ)² + (ΣI cos mθ)²]/ΣI, averaged over the spiral region; F_m = A_m/2 by the authors' note | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.3, https://arxiv.org/abs/1106.4840]` |
| 2 | A4/A2 | "about half ... in all cases" | same | same | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.3]` |
| 3 | Arm–interarm contrast by class | G 1.14 ± 0.44; M 0.81 ± 0.28; F 0.75 ± 0.35 mag | same, whole disc beyond any bar | 2.5 log[2 I_arm/(I_inter1 + I_inter2)] | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.2]` |
| 4 | Flocculent contrast by band | B 0.63 ± 0.24; I 0.34 ± 0.18; 3.6 µm 0.44 ± 0.13 mag | flocculents among 16 galaxies with earlier B/I data | as row 3 | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.2]` |
| 5 | m = 2 by bar type | SA 0.15 ± 0.042; SAB 0.26 ± 0.12; SB 0.34 ± 0.14 (F2 units; double for A2) | 10 SA, 18 SAB, 18 SB | called "in the arms" in the text; see note A | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.7]` |
| 6 | Mean A1 and A2 by arm class, inner | F: A1 0.28 ± 0.03, A2 0.21 ± 0.02 (50); M: 0.16 ± 0.01, 0.23 ± 0.02 (72); G: 0.12 ± 0.02, 0.48 ± 0.07 (26) | S4G, 3.6 µm, inclination ≤ 30°, T > −5, 167 galaxies; 1.5–2.5 Rs | mean of A_m/A_0 over the range; bars not removed | `[verified: Zaritsky et al. 2013, arXiv:1305.2940, Table 2, https://arxiv.org/abs/1305.2940]` |
| 7 | Same, outer | F: 0.35 ± 0.03, 0.19 ± 0.03; M: 0.22 ± 0.02, 0.20 ± 0.02; G: 0.21 ± 0.04, 0.37 ± 0.06 | same; 2.5–3.5 Rs | same | `[verified: Zaritsky et al. 2013, arXiv:1305.2940, Table 2]` |
| 8 | Same by bar class | none (95): A1 0.20/0.27, A2 0.20/0.20; weak (29): 0.22/0.25, 0.22/0.18; strong (43): 0.15/0.24, 0.40/0.30 (inner/outer) | same | same | `[verified: Zaritsky et al. 2013, arXiv:1305.2940, Table 3]` |
| 9 | Mean m = 2 amplitude per galaxy at 3.6 µm | N628 0.198; N1566 0.284; N2403 0.119; N2841 0.069; N3031 0.224; N3184 0.282; N3198 0.213; N3938 0.093; N4321 0.327; N4579 0.188; N5194 0.416; N6946 0.214; N7793 0.071 | 13 SINGS galaxies; range where a log spiral is traceable, "generally less than R25" | straight radial average of m = 2 over the axisymmetric disc + bulge | `[verified: Kendall, Clarke & Kennicutt 2015, arXiv:1411.5792, Table 2 and §2.1, https://arxiv.org/abs/1411.5792]` |
| 10 | Spectrum of weak-m = 2 galaxies | "no single dominant Fourier component and the power in modes m=1, 3 and 4 is similar to that in m=2" (optically flocculent, e.g. NGC 7793) | same; m = 1–4 only | qualitative, from per-galaxy plots | `[verified: Kendall, Clarke & Kennicutt 2015, arXiv:1411.5792, §2.1]` |
| 11 | Spiral A2 range | 0.15 < A2 < 0.6 | 18 face-on spirals, K′, beyond the bars, out to ~3 Rexp | A_m(R) from a least-squares fit on 24 azimuth bins per radius | `[verified: Rix & Zaritsky 1995, arXiv:astro-ph/9505111, §3.1.2, https://arxiv.org/abs/astro-ph/9505111]` |
| 12 | A4 against A2; high m | some two-armed spirals have ⟨A2⟩ > 2⟨A4⟩; the two strongest patterns have large m = 4; m > 4 small, A6 about 0.1 or less for nearly all (relation symbol lost in extraction) | same | same | `[verified: Rix & Zaritsky 1995, arXiv:astro-ph/9505111, §3.1.3]` |
| 13 | Three-armed cases | 3 of 18 (ESO-436, NGC 1376, NGC 7309) show significant m = 3 | same | visual plus A3 | `[verified: Rix & Zaritsky 1995, arXiv:astro-ph/9505111, §3.1.3]` |
| 14 | A1 at 2.5 Rexp | sample mean 0.14 (0.11 without the largest); weak at 1–2 Rexp, A1 > 0.2 beyond in "a sizable fraction" | same | error-corrected A1 | `[verified: Rix & Zaritsky 1995, arXiv:astro-ph/9505111, §3.1.1]` |
| 15 | Lopsided fraction | ⟨A1⟩ ≥ 0.2 in 16 of 60 (27 %); 14 of 43 (33 %) in the new sample; range 0.020–0.352 | 60 field spirals, I and K′, R > 1.5 Rexp | mean A1/A0 over the outer range | `[verified: Zaritsky & Rix 1997, arXiv:astro-ph/9608086, abstract and §2, https://arxiv.org/abs/astro-ph/9608086]` |
| 16 | ⟨A1⟩ statistics | mean 0.11; 34 % above the mean; 63 % above 0.05 | 149 OSUBGS galaxies, near-IR, inclination < 70°; 1.5–2.5 Rs | mean of a_1/Σ_0 over the range | `[verified: Bournaud et al. 2005, arXiv:astro-ph/0503314, §2.3, https://arxiv.org/abs/astro-ph/0503314]` |
| 17 | Which m are present | only m = 2: 34 of 86 (~40 %); m = 2 & 3: 24 (~28 %); m = 1 & 2: 11 (~13 %); only m = 3: 3; only m = 4: 2; only m = 1: 1. m = 2 present in ~87 %, m = 3 in ~38 %, m = 1 in ~20 % | 86 isolated Sb–Sc galaxies, SDSS i band, whole disc | which reconstructed m-term images match visible arms; a census, not amplitudes | `[verified: Durbala et al. 2009, arXiv:0905.2340, §4.8 and Table 8, https://arxiv.org/abs/0905.2340]` |
| 18 | Highest m needed | "fully reconstructed without including terms beyond m=6 and in most cases the first three terms suffice" | same | same | `[verified: Durbala et al. 2009, arXiv:0905.2340, §4.8]` |
| 19 | Radial order of m = 2 and 3 | in the 2 & 3 galaxies, "the two-armed pattern usually in the inner part of the galaxy and m=3 spiral arms in the outer part" | the 24 of 86 | same | `[verified: Durbala et al. 2009, arXiv:0905.2340, §4.8]` |
| 20 | Inner arm count of multiple-arm galaxies | 83 % have two inner arms; 2 % have four. Inner means within 0.5 R25 or twice the bar radius | 99 multiple-arm among 185 SBbc/SBc galaxies (73 F, 99 M, 12 G), blue images, visual | arm count | `[verified: Xu et al. 2023, arXiv:2304.10690, §4.1, https://arxiv.org/abs/2304.10690]` |
| 21 | Radius where m = 2 stops dominating | N6946: dominant only to 0.5 R25, beyond it m = 1, 3 (and 4 at 3.6 µm) are similar; N3938: m = 1 and 3 dominate "equally" after ~0.45 R25; N7793: m = 2 never dominant, m = 1 strongest beyond 0.6 R25; N1566: m = 2 not dominant until R > 0.2 R25 | individual SINGS galaxies, 3.6/4.5 µm and colour-corrected optical, m = 1–4 | relative amplitude per radius | `[verified: Kendall, Kennicutt & Clarke 2011, arXiv:1101.5764, §3.1.2, 3.1.8, 3.1.12, 3.1.13, https://arxiv.org/abs/1101.5764]` |
| 22 | NGC 4414 arm contrast | N "arm" 1.38 ± 0.04; S "arm" 1.13 ± 0.03 | K′; arm segments to 40″ (0.4 R25), continuous over 60° | ratio of arm brightness to the axisymmetric disc + bulge model | `[verified: Thornley 1996, arXiv:astro-ph/9607041, Table 2 and §4.1, https://arxiv.org/abs/astro-ph/9607041]` |
| 23 | Flocculent K′ contrasts | 1.1–1.4 in four flocculents, against 1.5–3.0 quoted for grand designs; structure only inside ~0.4 R25 | NGC 2403, 3521, 4414, 5055 | as row 22 | `[verified: Thornley 1996, arXiv:astro-ph/9607041, §4.2 and §5]` |
| 24 | NGC 4414 spiral m = 2 amplitude | 0.09 (dispersion 0.04), 5 segments, typed multi-armed | S4G 3.6 µm | mean over fitted log-spiral segments of the *maximum* A2 in each segment's range | `[verified: Díaz-García et al. 2019, arXiv:1908.04246, Table A.1, https://arxiv.org/abs/1908.04246]` |
| 25 | Same quantity, other galaxies | N5055 0.15; N7793 0.24; N628 0.40; N5457 0.47; N4321 0.64; N5194 0.87 | same | same | `[verified: Díaz-García et al. 2019, arXiv:1908.04246, Table A.1]` |
| 26 | Arm-class counts | 76 G, 157 M, 158 F of 391 | S4G 3.6 µm, Buta et al. 2015 classes | counts | `[verified: Díaz-García et al. 2019, arXiv:1908.04246, §2]` |
| 27 | Near-IR two-arm structure in flocculents | only ~15 % of 197 optically flocculent galaxies | 2MASS images, visual | fraction | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.1]` |
| 28 | Arm truncation radius | "usually lies between 0.5 and 0.7" of r25, with a large full range | 29 S4G spirals, 3.6 µm, 2D decomposition with explicit arms | mean end radius of the fitted arms | `[verified: Chugunov et al. 2024, arXiv:2311.01848, §6, https://arxiv.org/abs/2311.01848]` |
| 29 | Radius of peak arm contribution | "usually ... 1–2 disc radial scale lengths", falling to zero at centre and periphery | same | arm share of the azimuthally averaged profile | `[verified: Chugunov et al. 2024, arXiv:2311.01848, §6–7]` |
| 30 | Arm share of total light | usually 10–25 %, up to above 45 % | same | spiral-to-total at 3.6 µm | `[verified: Chugunov et al. 2024, arXiv:2311.01848, §7]` |
| 31 | Outer two-armed spirals in grand designs | N1566: from ~0.5 R25 to at least 1.4 R25; N4321: ~R25 to ~1.3 R25 | 3.6 µm, non-SB grand designs | visual plus the m = 2 profile | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.5]` |
| 32 | Radial trend of arm contrast | 18 galaxies rising, 12 falling; SB grand-design and multiple-arm fall; SA/SAB rise or stay flat; flocculent and late types rise | 46 S4G | slope of arm–interarm contrast beyond the bar | `[verified: Elmegreen et al. 2011, arXiv:1106.4840, §4.7 and Table 2]` |
| 33 | Arm-count demographics | 1/2/3/4/5+ arms = 5/64/18/6/7 % | SDSS, log M* ≥ 10.6, 0.03 < z < 0.085, visual votes; Hart et al. 2016 as quoted by Smith et al. 2026 | dominant visual arm count | `[verified-via-extract: Smith et al. 2026, arXiv:2606.14896, https://arxiv.org/abs/2606.14896]` |
| 34 | Arm-strength measure; outer behaviour | A_tot = sqrt(A2² + A3² + A4²); decomposition to m = 6 "because higher order modes are nearly negligible"; beyond the main spiral region the structure "transforms into feathery structures dominated by higher-frequency modes" | 211 CGS discs, BVRI, from the bar radius or 0.1 R90 out to R90 | A_m = I_m/I_0 | `[verified-via-extract: Yu et al. 2018, arXiv:1806.06591, §3.1–3.2, https://arxiv.org/abs/1806.06591]` |
| 35 | Leading/trailing m = 2 ratio | ~0.4–0.5 over most of the arms; contrast rises with radius, not monotonically | NGC 4062 (flocculent, H) and NGC 5248 (grand design, K′) | 2D log-spiral Fourier | `[verified-via-extract: Puerari et al. 2000, arXiv:astro-ph/0005345, https://arxiv.org/abs/astro-ph/0005345]` |

### 2. Per-source notes

- **Elmegreen et al. 2011.** Note A: Table 2's fifth column is headed "F2r arm ... average" but footnoted "arm
  peak". The §4.7 SA mean of 0.15 matches the *third* column (the reader's mean over the 10 SA rows: 0.153), not
  the fifth (0.09). The paper is internally ambiguous here. The reader's arithmetic on the fifth column by class,
  not stated by the authors: F 0.106 (13), M 0.124 (20), G 0.207 (13), so A2 ≈ 0.21, 0.25, 0.41. Only m = 2, 3, 4
  were measured. NGC 4414 is not in the sample. §4.5: multiple-arm galaxies "generally have an inner 2-arm
  symmetry" with narrow, irregular, asymmetric arms to the image edge.
- **Zaritsky et al. 2013.** Decomposed m = 1–4 but tabulates only A1 and A2. "the m = 1 amplitudes generally rise
  toward larger galactic radii independent of galaxy type." A2 above 0.4 is mostly strong bars, so the
  grand-design 0.48 mixes bar and spiral.
- **Kendall et al. 2011 and 2015.** Of 31 galaxies, 13 are non-grand-design in the near-IR ("without a
  predominating m=2 mode"). Amplitude "seems to follow the standard trend of increasing with radius" (NGC 3198)
  and "increases approximately linearly with radius" (NGC 2403). NGC 7793: "more power is predicted to be in the
  higher order Fourier components (m ≥ 4)" is stated as an expectation, not a measurement. Spiral lost after
  0.5 R25 in NGC 1566 and NGC 2403; NGC 628 traced beyond 0.9 R25.
- **Rix & Zaritsky 1995.** "nearly half of the galaxies exhibit spiral arms with an arm-inter arm contrast ... of
  about unity", where contrast = I_max/I_min − 1 in a model image built from m = 0, 2, 4, 6 only. Arms extend "over
  a factor of about two in radius"; "A2 is the dominant even Fourier amplitude".
- **Durbala et al. 2009.** Rows containing m = 4 sum to 9 of 86 (the reader's arithmetic). No m = 5 or 6 arms
  appear in the census.
- **Thornley 1996.** No Fourier analysis. NGC 4414 "remains the most flocculent of the sample"; its segments "do
  not appear to contribute to a regular two-arm spiral pattern". Disc scale length 0.3 ± 0.05 arcmin.
- **Díaz-García et al. 2019.** A2 only; no higher modes. The amplitude is a mean of per-segment maxima, so it runs
  well above Kendall's radial means.
- **D'Onghia 2015** `[verified: D'Onghia 2015, arXiv:1507.00724, §2–3, https://arxiv.org/abs/1507.00724]`. Theory
  and N-body only: arm number "is expected to increase with distance"; outer arms "will have lower strength";
  Milky Way prediction of two arms at ~4.5 kpc and 5–6 near the Sun. The paper measures nothing on real galaxies;
  its DiskMass check is "a visual inspection".
- **Dobbs & Baba 2014** `[verified: Dobbs & Baba 2014, arXiv:1407.5062, §2.2, https://arxiv.org/abs/1407.5062]`.
  States that arm number rising outward "agrees qualitatively with observations" and shows Fuchs & Möllenhoff's
  NGC 1288 profile as a figure; no numbers in the text.

### 3. What a model should reproduce (each statement can fail)

**(a) Spectrum shape in m**
1. **Grand design:** m = 2 is the largest term, with A3/A2 = 0.33 ± 0.19 and A4/A2 ≈ 0.5 (rows 1–2). Mean A2 is
   0.48 ± 0.07 at 1.5–2.5 Rs and 0.37 ± 0.06 at 2.5–3.5 Rs, bars included (rows 6–7). Fails if A3 ≥ A2 or A4 ≥ A2
   over the main disc.
2. **Multiple-arm:** A3/A2 = 0.48 ± 0.24, A4/A2 ≈ 0.5, mean A2 ≈ 0.23 inner and 0.20 outer. Fails if m = 2 is not
   the largest of m = 2–4 on average, or if A2 exceeds ~0.4.
3. **Flocculent:** A3/A2 = 0.58 ± 0.11 and A4/A2 ≈ 0.5 (rows 1–2), so the spectrum is *not* flat from m = 2 to 4 in
   the 13 S4G flocculents. Kendall says it *is* roughly flat over m = 1–4 for NGC 7793-like discs (row 10). Fails
   either way if any single m ≥ 3 exceeds m = 2 by a clear margin disc-wide.
4. **Flocculent level:** mean m = 2 amplitude 0.07–0.12 (Kendall: N7793, N2841, N2403) or ~0.2 (Zaritsky class
   mean). For NGC 4414, the segment-maximum A2 is 0.09 and K′ arm contrasts are 1.13–1.38. Fails if the template's
   m = 2 is ≳ 0.2 at 3.6 µm, or if it shows a coherent two-armed pattern beyond 0.4 R25.
5. **High-m tail:** A6 is about 0.1 or less for nearly all spirals (row 12); nothing above m = 6 is needed and
   three terms usually suffice (row 18). Fails if m = 5–6 carry more amplitude than m = 2–3 anywhere inside the
   bright disc. No source read gives measured A5 or A6 values by class.

**(b) Dominant m against radius**
6. Inside ~0.5 R25 the pattern is two-armed: 83 % of multiple-arm galaxies have two inner arms and 2 % have four
   (row 20). Fails if dominant m ≥ 3 inside 0.5 R25 in a non-flocculent disc.
7. Where a second mode appears it sits *outside* m = 2: Durbala's 24 of 86; NGC 6946 at 0.5 R25; NGC 3938 at
   ~0.45 R25 (rows 19, 21). Fails if the dominant m falls outward.
8. The modes that take over are m = 3 and m = 1, with m = 4 joining in NGC 6946. No read source shows m = 5 or 6
   dominant at any radius in stellar light. Fails if the model's outer disc is amplitude-dominated by m = 5–6
   inside R25.
9. Counter-case: non-barred grand designs keep two-armed spirals to 1.3–1.4 R25 (row 31). A rule that forces m
   upward in every disc fails on these.
10. m = 2 amplitude rises with radius in unbarred, flocculent and late-type discs, and falls beyond strong bars
    (row 32; Kendall). Fails if amplitude peaks at the centre of an unbarred disc.

**(c) Odd against even**
11. m = 1 is weak inside 1–2 Rs and grows outward in all types (rows 14, 7). Mean ⟨A1⟩ over 1.5–2.5 Rs is 0.11
    (149 galaxies) to 0.12–0.28 by arm class (167 galaxies).
12. In flocculents A1 exceeds A2: 0.28 against 0.21 inner, 0.35 against 0.19 outer (rows 6–7). A split over
    m = 2–6 only omits the largest observed term of a flocculent disc at 1.5–3.5 Rs.
13. m = 3 is 0.33–0.58 of m = 2 in amplitude by class, comparable to or above m = 4 (≈ 0.5) in flocculents. Fails
    if odd modes are suppressed against even ones in a multi-arm or flocculent disc.

**(d) Where arms end**
14. Fitted stellar arms truncate at 0.5–0.7 r25 on average and their contribution peaks at 1–2 scale lengths
    (rows 28–29). Fails if the arm contribution peaks beyond ~2 h or stays undiminished to r25.
15. Near-IR structure in flocculents is confined to ≲ 0.4 R25 (row 23); grand-design arms are detectable to
    ~1.5 R25 at 3.6 µm (row 31).

### 4. Conflicts between sources (not averaged)

- **Is a flocculent spectrum flat?** Elmegreen et al. 2011: m = 3 is 0.58 and m = 4 about 0.5 of m = 2. Kendall et
  al. 2015: m = 1, 3, 4 "similar to" m = 2. Different galaxies, and averaged over the spiral region against read
  off per-radius plots.
- **Flocculent A2 level.** Kendall 0.07–0.12; Zaritsky 0.21 ± 0.02; Elmegreen ~0.21 (the reader's arithmetic);
  Díaz-García 0.24 for NGC 7793 (segment maxima). For NGC 7793 alone: 0.071, 0.14 (2 × 0.07) and 0.24. Kendall
  attributes Elmegreen's higher averages to analysing out to larger radius.
- **Size of m = 1.** Bournaud mean 0.11; Rix & Zaritsky 0.14 at 2.5 Rexp; Zaritsky et al. 2013 means of 0.15–0.28
  by class over the same 1.5–2.5 Rs. S4G includes many late, low-mass systems.
- **Where arms end.** Chugunov 0.5–0.7 r25 (fitted truncation, 29 galaxies) against Elmegreen "often out to
  ~1.5 R25" (detectable contrast). Different definitions.
- **m = 4 against m = 2.** Elmegreen "about half in all cases"; Rix & Zaritsky find both ⟨A2⟩ > 2⟨A4⟩ and cases
  with large m = 4; Kendall finds m = 4 similar to m = 2 in outer NGC 6946.
- **NGC 4414's class.** Flocculent, "the most flocculent of the sample" in K′ (Thornley), against multi-armed in
  S4G (Díaz-García Table A.1).
- **Theory against observation on the outer disc.** D'Onghia predicts 5–6 arms at the solar radius; the observed
  outer takeover modes are m = 1 and m = 3.

### 5. What could not be read

- **Elmegreen, Elmegreen & Montenegro 1992** (ApJS 79, 37) and **Elmegreen & Elmegreen 1995** (ApJ 445, 591): ADS
  returned HTTP 405. The "inside ~0.5 R25" result is reported here only as Xu et al. 2023 cites it.
- **Thornley & Mundy 1997** (NGC 4414, ApJ 490, 682) and **Fuchs & Möllenhoff 1999** (NGC 1288 arm number against
  radius): ADS only; not read.
- **Yu et al. 2018 Table 1** (per-galaxy dominant mode): the PDF exceeds the fetch size limit and the HTML
  extraction lacked the table, so there is no tally of dominant m. **Yu & Ho 2020** not found on arXiv by title.
- **Díaz-García et al. 2019** on aanda.org and **Grosbøl et al. 2004** (A&A 423, 849): HTTP 403. The former was
  read from arXiv; the latter not at all.
- **Rix & Zaritsky 1995 and Zaritsky & Rix 1997:** the HTML conversion failed; PDF text was read, but Rix &
  Zaritsky's Table 2 and figures (per-galaxy A_m profiles) did not extract.
- **Salo et al. 2015, Díaz-García et al. 2016, Bittner et al. 2017, Athanassoula et al. 1987, Considère &
  Athanassoula 1988, Hart et al. 2016 (primary):** not fetched.
- **Not found anywhere read:** a per-class amplitude spectrum over m = 1–6, any measured A5 or A6, a quantified
  A3(R) or A4(R) profile, or a Fourier spectrum of NGC 4414 itself.
- `[recall — NOT READ]` Elmegreen et al. 1992 reported three-arm components confined between resonances in 18
  galaxies; radii and amplitudes not confirmed.
