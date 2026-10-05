# READING_ARM_SEGMENTS — pitch along an arm, and what a template can pin (S59, BUILD_III Phase P4)

**The lead's note (2026-10-05).** One Opus reader, briefed by BUILD_III §3e and forbidden the repository, wrote
what is below the rule; it is entered as returned, its headings one level down. It was run while S58's closing
suite ran, before this session's branch existed. Two things the reader flags itself: the segment-length and
pitch-change statistics of A1.1 are its hand arithmetic on Honig & Reid 2015's 38 printed rows (the rows are in
A2, so the arithmetic can be re-run), and the Milky Way's arm table is Reid et al. 2019's Table 2 read twice,
digit for digit.

**What the reading says that the plan's text did not foresee** (the lead's summary; the part below is the record).
(1) *Segments are per arm*: each arm is fitted on its own, with its own kinks; no source says kinks of different
arms share a radius, and arms of one galaxy differ in pitch by a few degrees. The model's arms are a sum of modes
that share one winding. (2) *The Milky Way's measured loci are seven separately fitted segments* covering about a
third of the disc on the Sun's side, four of them read as major arms, with pitches from −1° to 19.5°; later work
moves Perseus and argues for two inner arms. (3) *NGC 4414 has nothing positional to pin*: five segment pitches
(mean 29°) over stated radii, no azimuths.

---

## Part A — pitch along an arm, and what can be pinned (reader 1)

Read blind (web search and fetch only; no repository file opened; no code run). Every number below was read on a
fetched page unless it carries `[derived]` (my hand arithmetic on a verified table) or `[recall — NOT READ]`.
PDFs were read through a text rendering of the arXiv PDF (r.jina.ai) and, where it exists, the ar5iv HTML; "2 reads
agree" means two separate fetches gave the same digits. Full tags with URLs are in A2; tables carry the source key.

### A1 Summary tables

#### A1.1 Pitch along one arm; segment statistics

| Quantity (definition) | Value | n | Source key |
|---|---|---|---|
| Segment = stretch of one arm between breaks in HII density/scatter or apparent pitch change; log-spiral fit per segment | "∼5 kpc" (abstract); "roughly 5 to 10 kpc" (intro); quoted later as "5 to 8 kpc" by Reid+19 | 38 segments, 4 galaxies | HR15; R19 |
| Segment azimuthal extent, from the printed azimuth ranges `[derived]` | median 60°, quartiles 50°–80°, range 20°–180°, mean 67.8° | 38 | HR15 T2–T5 |
| Segment arc length R·Δβ/cos ψ from printed mean radius `[derived]` | median 5.9 kpc, quartiles 4.9–7.6, range 1.0–11.1 kpc | 38 | HR15 T2–T5 |
| Segment pitch, winding sense normalised `[derived]` | mean 15.0°, sd 9.9° (pooled, 4 galaxies); 3 of 38 segments reversed (−4.0°, −9.1°, −10.3°, all M 51) | 38 | HR15 T2–T5 |
| Pitch change at a join of adjacent segments, outer minus inner `[derived]` | signed mean −0.5°, rms 14.4°; \|Δψ\| median 9.7°, mean 11.5°, max 35.8° | 25 joins | HR15 T2–T5 |
| Sign of successive changes along one arm `[derived]` | 12 of 15 successive pairs reverse sign (iid draws predict 2/3; a random walk 1/2) | 15 | HR15 T2–T5 |
| Trend of segment pitch with radius | "no systematic trend with galactocentric distance" | 4 gal. | HR15 abstract |
| sd of \|φ\| among a galaxy's log segments (3.6 μm, visual tracing, fit of log r vs θ) | mean σ\|φ\| = 9.5° ± 0.3°; "varies on average by ∼10° between segments, but by up to ≳15−20°" | 391 gal. | DG19 |
| Segments per galaxy | 1: 1.5 %; 2: 18.9 %; 3: 22.0 %; 4: 26.9 %; 5: 14.8 %; >5: 15.9 % (max 9) | 391 | DG19 |
| \|φ\| against radius, statistically | "does not change with increasing radius ... for all types of spirals" | 391 | DG19 §6 |
| Variation along the two main arms: max deviation from mean ÷ mean (window Fourier, SDSS) | > 20 % in "about 2/3"; < 10 % in "∼1/10"; pitch falls outward in 32 of 50 (64 % ± 11 %) | 50 gal. | SR13 |
| Radial range traced | 0.74 ± 0.09 to 2.40 ± 0.25 inner-disc scale lengths | 50 | SR13 |
| Variation along an arm: sd of local pitch ÷ mean (local pitch in a window of 1/3 of the arm) | 0.56 ± 0.25 all; 0.47 ± 0.24 grand design; 0.65 ± 0.24 multi-armed; absolute σ(ψ) = 7.2° ± 3.3° | 155 gal. | S20 |
| Method scatter, 1D vs 2D Fourier | "consistent within a small scatter of 2°" | — | YH19 |
| 2DFFT error per galaxy | "2° to 4°"; variable pitch "more the exception than the rule" | — | D12 |

#### A1.2 Arm-to-arm differences inside one galaxy

| Quantity (definition) | Value | n | Source key |
|---|---|---|---|
| σ_gal: sd of a truncated normal from which each arm's (single-log-spiral) pitch is drawn about φ_gal | 11.0° ± 0.9° (posterior; one value common to all galaxies) | 129 gal., 247 arms | L21 |
| (max − min arm pitch) ÷ mean | 0.16 ± 0.12 grand design; 0.27 ± 0.25 multi-armed; "about 20-25%" | 155 gal. | S20 |
| Median pitch difference of the two longest arcs, by minimum arc length in pixels | 0 px: 14.5°; 50: 14.3°; 100: 10.7°; 150: 7.5°; 200: 5.6°; 250: 3.5°; 300: 2.6° | SDSS, GZ subset 29 250 | DH14 T1 |
| Whole-arm ("global") single-pitch fits to HII loci | NGC 628: 15.4 ± 0.5, 14.3 ± 0.2; NGC 3184: 19.6 ± 0.6, 20.2 ± 0.8; M 51: 13.4 ± 0.6, 8.3 ± 0.3; NGC 1232 A/B/C: 9.7 ± 0.5, 17.3 ± 0.4, 18.4 ± 0.5 (signs dropped) | 4 gal. | HR15 |
| Mean \|φ\| by arm number m = 2, 3, 4, 5+ (length-weighted arcs) | 18.6 ± 0.2, 19.2 ± 0.3, 19.2 ± 0.5, 19.4 ± 0.6°; sample 16th/84th pct 12.2°/26.1° | 6 222 gal. | H17 |
| Mean \|φ\| by T (all galaxies; number) | T 0–2: 15.9 ± 1.3 (19); 2–4: 17.8 ± 0.7 (80); 4–6: 19.7 ± 0.4 (159); 6–8: 21.2 ± 0.8 (97); 8–10: 21.3 ± 1.5 (36) | 391 | DG19 T2 |
| Mean \|φ\| by arm class, range over T bins | grand design 13.6–19.7°; multi-armed 19.8–28.4°; flocculent 18.7–20.8° | 391 | DG19 T2 |

#### A1.3 The Milky Way (Reid et al. 2019, Table 2, as printed; 2 reads agree digit for digit)

Form: `ln(R/R_kink) = −(β − β_kink) tan ψ`, ψ = ψ_< for β ≤ β_kink, ψ_> for β > β_kink. β = Galactocentric azimuth,
0 towards the Sun, increasing in the direction of Galactic rotation (so the first quadrant has β > 0). Positive ψ =
R falls as β grows (trailing). Width = intrinsic Gaussian 1σ at R_kink. Model assumes R0 = 8.15 kpc.

| Arm | N | ℓ tangency | β range (°) | β_kink (°) | R_kink (kpc) | ψ_< (°) | ψ_> (°) | Width (kpc) |
|---|---|---|---|---|---|---|---|---|
| 3-kpc(N) | 3 | 337.0 | 15 → 18 | 15 | 3.52 ± 0.26 | −4.2 ± 3.8 | −4.2 ± 3.8 | 0.18 ± 0.05 |
| Norma | 11 | 327.5 | 5 → 54 | 18 ± 4 | 4.46 ± 0.19 | −1.0 ± 3.3 | 19.5 ± 5.1 | 0.14 ± 0.10 |
| Sct-Cen | 36 | 306.1 | 0 → 104 | 23 | 4.91 ± 0.09 | 14.1 ± 1.7 | 12.1 ± 2.4 | 0.23 ± 0.05 |
| Sgr-Car | 35 | 285.6 | 2 → 97 | 24 ± 2 | 6.04 ± 0.09 | 17.1 ± 1.6 | 1.0 ± 2.1 | 0.27 ± 0.04 |
| Local | 28 | ... | −8 → 34 | 9 | 8.26 ± 0.05 | 11.4 ± 1.9 | 11.4 ± 1.9 | 0.31 ± 0.05 |
| Perseus | 41 | ... | −23 → 115 | 40 | 8.87 ± 0.13 | 10.3 ± 1.4 | 8.7 ± 2.7 | 0.35 ± 0.06 |
| Outer | 11 | ... | −16 → 71 | 18 | 12.24 ± 0.36 | 3.0 ± 4.4 | 9.4 ± 4.0 | 0.65 ± 0.16 |

Table note (read): β_kink without uncertainty was not solved for (set from a gap in sources); ψ_< = ψ_> means one
pitch was solved; β range is that of the parallax data; fourth-quadrant tangency priors 337°, 328°, 308°, 283° (±2°)
constrain the fits where parallaxes are few. No row exists for the Outer-Scutum-Centaurus arm or the far 3-kpc arm.
Width law: `w(R) = 336 + 36 (R[kpc] − 8.15) pc`. R0 = 8.15 ± 0.15 kpc, Θ0 = 236 ± 7 km/s.

| Other Milky Way numbers | Value | Source key |
|---|---|---|
| Arm number | "a four-arm spiral as traced by massive young stars"; two arms would need mean pitch "near 5°"; found "an average pitch angle of 10° for the major arms" | R19 §8.1 |
| Major arms | Norma–Outer, Scutum–Centaurus–OSC, Sagittarius–Carina, Perseus | R19 §3.2 |
| Local arm | "an isolated arm segment"; "has not linked up with other segments to form a 'true' arm" | R19 §3.3 |
| 3-kpc arms | "associated with the Galactic bar and may not be true spiral arms" | R19 |
| Perseus | weakens "and possibly die[s] out in the 3rd quadrant"; a stretch of "about 8 kpc" with little star formation in Q1 | R19 §3.2.4 |
| Perseus re-fit, R0 = 8.15 | two-segment: β_kink 40 (fixed), R_kink 9.29 ± 0.10, ψ_< 5.9 ± 1.2, ψ_> 10.6 ± 1.0, width 0.32 ± 0.04; one-segment (preferred): R 9.08 ± 0.08 at β = 40, ψ 8.7 ± 0.7, width 0.36 ± 0.06 | Hy26 T3 |
| 2014 single-pitch fits, R0 = 8.34 | Scutum β_ref 27.6, R 5.0 ± 0.1, ψ 19.8 ± 2.6; Sagittarius 25.6, 6.6 ± 0.1, 6.9 ± 1.6; Local 8.9, 8.4 ± 0.1, 12.8 ± 2.7; Perseus 14.2, 9.9 ± 0.1, 9.4 ± 1.4; Outer 18.6, 13.0 ± 0.3, 13.8 ± 3.3 | R14 T2 |
| Xu+ 2023, masers, R0 = 8.15 | Norma (Scutum merged in) N 53, β 0→120, R_ref 4.96 ± 0.02 at β_ref 13.07, ψ 15.0 ± 1.1; Sagittarius 24, 26→150, 6.02 ± 0.65 at 119.11, 1.3 ± 5.1; Carina 17, −5→20, 6.35 ± 0.11 at 9.93, 21.4 ± 4.6; Local 28, −10→40, 8.29 ± 0.08 at 8.95, 11.3 ± 1.9; Perseus 39, −10→160, 9.50 ± 0.09 at 18.78, 11.0 ± 1.1; Outer 12, −25→70, 12.05 ± 0.39 at 17.9, 3.6 ± 4.1 | X23 T2 |
| Xu+ 2023 morphology | two symmetric inner arms (Norma, Perseus) that bifurcate at 5.0–6.5 kpc into Centaurus and Sagittarius; outer "long, irregular arms" (Centaurus, Sagittarius, Carina, Outer, Local) | X23 |
| Long bar | angle to the line of sight "(28−33)°"; half-length 5.0 ± 0.2 kpc (two-component), 4.6 ± 0.3 kpc (thin bar alone); R0 = 8.3 kpc assumed | W15 abstract |
| Bulge (box/peanut) bar | φ_bp = 27° ± 2°; long bar φ_lb 28°–33°, R_lb = 5.0 ± 0.2 kpc; R0 = 8.2 ± 0.1 kpc | BHG16 |
| VERA R0 | 7.92 ± 0.16 (stat) ± 0.3 (sys) kpc; no arm fits of its own (plots R19's arms) | V20 |

#### A1.4 NGC 4414

| Quantity | Value | Source key |
|---|---|---|
| Classification, 3.6 μm | phase 1 SA(rl)bc; phase 2 SA(s)c / E3; mean SA(r͟s)b͟c / E3, ⟨T⟩ 4.5, bar family index 0.00 (no bar); arm class F; note "flocculent spiral; embedded low inclination case" | B15 (VizieR) |
| Optical arm class | "According to Elmegreen & Elmegreen (1987), NGC 4414 is a flocculent galaxy" (class number not read) | F05 |
| Log segments, 3.6 μm deprojected: pitch α (°), r_i–r_o (″), quality | sp1 −30.5, 28.7–63.6, 2; sp2 −34.2, 19.4–57.3, 2; sp3 −28.1, 32.7–87.4, 2; sp4 −44.0, 29.2–54.4, 2; sp5 −7.6, 57.9–66.3, 2 (2 reads agree) | HE15 T3 |
| Derived from those five | mean 28.88°, error of mean 5.97°, sd 13.35°, median 30.50°, inner 32.35 ± 1.85°, arc-weighted 31.44° (sd 7.78°); arithmetic re-done by hand: matches | DG19 Ta1 |
| Azimuth spanned per segment, ln(r_o/r_i)/tan\|α\| `[derived]` | 77°, 91°, 105°, 37°, 58° | HE15 T3 |
| K′ structure | ring/arm at radius 20″ (2 kpc); outer "arm" segments to north and south reach ∼40″ (0.4 R25), "continuous over ∼60° in azimuth"; no regular two-arm pattern; contrast N 1.38 ± 0.04, S 1.13 ± 0.03; "the most flocculent of the sample" | T96 |
| Inclination / PA | 55° (T96); 55°, 155° (So02, LEDA); 55°, 157° (Va02); kinematic 56 ± 4°, 155 ± 2°, photometric 56 ± 3°, 157 ± 3° (F05); 60°, 160° (RW04); HI 52.3 ± 1.5°, PA 155°→161°→155° inside 240″ (dB14) | as named |
| Distance | 19.2 Mpc (So02, Va02: ± 2); 19.1 (RW04); 17.8 (dB14) | as named |
| Magnetic pitch | "about zero in the northern disk, increasing to about 40°–45°"; mean about 20° | So02 |

### A2 Per-source notes (tags; what each covers)

- **HR15** `[verified: Honig & Reid 2015, ApJ 800, 53 = arXiv:1412.1012, Tables 1–5, abstract, §3, §5.2–5.3,
  https://arxiv.org/pdf/1412.1012 and https://ar5iv.labs.arxiv.org/html/1412.1012; covers all 38 segment rows, 2 reads
  agree]`. Model `R = R_ref exp(−(β − β_ref) tan ψ)`, β zero to north, increasing eastward; positions were NOT
  deprojected (galaxies "within about 30°" of face-on). Segment boundaries by three criteria: breaks in HII density or
  scatter, apparent pitch change, comparable sample sizes. Tabulated per segment: azimuth range, "mean radius" (fitted
  radius at the mean azimuth of the segment's HII regions), ψ, width. Distances 10.0, 21.0, 8.2, 9.4 Mpc (NGC 628,
  1232, 3184, 5194). Rows, as (range°, R kpc, ψ°): NGC 628 A (90→225, 2.58, −27.6), (225→310, 5.60, −9.4), (310→360,
  7.31, −18.1); B (50→125, 5.75, −15.2), (125→195, 7.57, −15.9), (195→255, 10.38, −11.0), (255→290, 12.02, −15.4).
  NGC 1232 A (−45→55, 3.33, −9.9), (45→150, 5.01, −8.9), (150→230, 5.98, −14.3); B (50→165, 2.63, −11.8), (165→250,
  3.49, −10.8), (250→315, 5.46, −26.6), (312→380, 7.64, −30.0); C (−80→−20, 4.38, −14.7), (−20→35, 5.82, −20.9);
  D (155→195, 9.87, −10.9); E (−85→−65, 11.38, −11.6), (−65→−40, 12.83, −22.0); F (95→130, 16.23, −10.8). NGC 3184
  A (0→180, 1.43, −22.8), (180→260, 2.79, −14.9), (260→320, 3.91, −22.7); B (−180→−130, 1.09, −5.4), (−30→45, 2.57,
  −26.9), (45→120, 3.95, −12.2). M 51 A (250→170, 1.90, +30.9), (165→80, 3.29, +15.0), (80→30, 5.40, +26.7),
  (30→−15, 6.45, −9.1), (−15→−40, 6.08, −4.0); B (65→−40, 2.50, +22.5), (−40→−90, 3.42, +1.2), (−90→−150, 5.39,
  +19.4), (−150→−200, 6.70, +8.6), (−200→−250, 7.11, −10.3), (−250→−305, 7.05, +19.2), (−305→−345, 9.72, +28.9).
  Sign: negative is the normal winding sense in the first three galaxies, positive in M 51 (traced the other way).
  Widths 0.07–0.87 kpc, growing outward. Continuity at joins is not stated and was not imposed in what I read: ranges
  overlap (NGC 1232 A: 55 vs 45) or leave gaps (M 51 A: 170 vs 165). `[derived]` check on NGC 628 arm A at β = 225°,
  taking the mean azimuth as the range midpoint: 4.78 kpc from the inner fit, 4.95 kpc from the outer, a 0.17 kpc
  step, about one arm width. Kinks and resonances: outer narrowing "could be attributed to reaching the radius of
  co-rotation"; "M 51's arm A co-rotates at a radius of ≈ 6 kpc while arm B co-rotates at a radius of ≈ 9 kpc", which
  the authors say "would argue against a single (global) pattern speed". Nothing says kinks of different arms share a
  radius. Simulations cited (D'Onghia+ 2013): segments form, swing-amplify, "then connect".
- **DG19** `[verified: Díaz-García, Salo, Knapen & Herrera-Endoqui 2019, A&A 631, A94 = arXiv:1908.04246, §3, §6,
  Table 2, https://ar5iv.labs.arxiv.org/html/1908.04246 and https://arxiv.org/pdf/1908.04246; covers σ|φ|, segment
  counts, T-bin means; 2 reads agree on σ|φ| and on 2.9° ± 0.14°]`. 391 S4G galaxies with i < 65°; segments are those
  of HE15 (quality 1–2 only). Arc length of a segment `s_i = |r'_i − r_i| sqrt(1 + tan²|φ_i|)/tan|φ_i|`; mean absolute
  difference between plain and arc-weighted means 2.9° ± 0.14°. φ is taken positive; mixed senses not analysed.
- **HE15** `[verified: Herrera-Endoqui, Díaz-García, Laurikainen & Salo 2015, A&A 582, A86 = arXiv:1509.05328, §
  on spirals, https://arxiv.org/pdf/1509.05328; Table 3 rows read at VizieR J/A+A/582/A86/table3,
  https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=J/A+A/582/A86/table3&-out.all&Name=NGC4414; covers the five
  NGC 4414 rows]`. Points marked by eye on unsharp-masked 3.6 μm images, fitted as a line in log r vs θ; stored per
  segment: α (sign = s or z winding), r_i, r_o (arcsec), quality (1 good, 2 acceptable). No azimuth is stored, no
  formal error. "pitch angle is not necessarily constant within a galaxy".
- **SR13** `[verified: Savchenko & Reshetnikov 2013, MNRAS 436, 1074 = arXiv:1309.4308, abstract and results,
  https://arxiv.org/html/1309.4308v1 and https://arxiv.org/pdf/1309.4308; covers the fractions and radial range; 2
  reads agree]`. 50 non-barred or weakly barred two-armed SDSS galaxies, i ≈ 40°–60°, Sa–Sc. Between-arm difference
  not quantified. Agreement with literature −0.2° ± 0.7°; g vs r −0.33° ± 0.16°.
- **S20** `[verified: Savchenko, Marchuk, Mosenkov & Grishunin 2020, MNRAS 493, 390 = arXiv:2001.09110, results,
  https://arxiv.org/pdf/2001.09110 and https://ar5iv.labs.arxiv.org/html/2001.09110; covers the variation statistics;
  2 reads agree]`. 155 face-on SDSS spirals (20 F, 100 M, 35 G). Whole-sample mean pitch 14.8° ± 5.3°. Flocculent
  variation 0.39 ± 0.10 from 5 galaxies (one read). Per-class mean pitches: reads disagree, not used.
- **L21** `[verified: Lingard et al. 2021, MNRAS 504, 3364 = arXiv:2105.04500, §2.3, §3.1,
  https://arxiv.org/pdf/2105.04500 and https://ar5iv.labs.arxiv.org/html/2105.04500; covers σ_gal; 2 reads agree]`.
  `φ_arm ~ TruncatedNormal(φ_gal, σ_gal, 0°, 90°)`; each arm one log spiral `r = A exp(θ tan φ)`; 68 two-arm, 19
  three-arm, 4 four-arm, 38 one-arm galaxies. Mean uncertainty on φ_gal for two-arm galaxies 7.9°. Authors call
  σ_gal "similar to that found by Kennicutt 1981 and Davis & Hayes 2014".
- **DH14** `[verified: Davis & Hayes 2014, ApJ 790, 87 = arXiv:1402.1910, Table 1,
  https://ar5iv.labs.arxiv.org/html/1402.1910 and https://arxiv.org/pdf/1402.1910; covers Table 1; end values agree in
  2 reads, the column alignment differs — see A4]`. An arc is a contiguous region of consistent orientation, fitted by
  a log spiral. Example: 13.6° vs 24.4° in one galaxy. Lengths are in pixels, not kpc.
- **H17** `[verified: Hart et al. 2017, MNRAS 472, 2263 = arXiv:1708.04628, https://arxiv.org/pdf/1708.04628; one
  read]`. `ψ_galaxy = Σ(L_n ψ_n)/L_total` over reliable arcs; mean 18.0°. No within-galaxy scatter printed.
- **D12** `[verified: Davis et al. 2012, ApJS 199, 33 = arXiv:1202.4780, https://arxiv.org/pdf/1202.4780; one read]`
  and **YH19** `[verified: Yu & Ho 2019, ApJ 871, 194 = arXiv:1812.06010, https://arxiv.org/pdf/1812.06010; one read;
  the 2° is YH19 quoting Yu+ 2018]`. 79 galaxies; scatter of pitch at fixed Hubble type "∼7°".
- **R19** `[verified: Reid et al. 2019, ApJ 885, 131 = arXiv:1910.03357, Table 2 and note, §3, §3.2.1–3.2.4, §3.3,
  §8.1, https://arxiv.org/pdf/1910.03357; covers all seven rows; 2 reads of the PDF text agree digit for digit; the
  Perseus row is confirmed by Hy26's Table 3, the Sgr-Car pitches and kink by a search extract of Kuhn+ 2021]`. About
  200 maser parallaxes. Arm fits remove > 3σ outliers found with a Lorentzian-like likelihood, then refit Gaussian.
  Norma: a "quasi-linear, spur-like structure" of pitch "≈ 20°" from "(X, Y) = (3, 2) kpc near the end of the bar";
  my evaluation of the table at β = 54° gives R = 3.57 kpc, (X, Y) = (2.89, 2.10) with X = R sin β, Y = R cos β
  `[derived]`, so that axis convention reproduces the text. Norma "wraps around the far side ... and becomes the Outer
  arm"; Sct-Cen passes G007.47+00.05 and returns as the OSC arm (not fitted). Sagittarius has "a 2-kpc long gap"
  centred at β ≈ 24°. Segments: Honig & Reid "found that arm segments have characteristic lengths of 5 to 8 kpc,
  often separated by kinks or gaps". Long bar drawn "after Wegg, Gerhard & Portail (2015)".
- **R14** `[verified: Reid et al. 2014, ApJ 783, 130 = arXiv:1401.5377, Table 2, https://arxiv.org/pdf/1401.5377 and
  https://ar5iv.labs.arxiv.org/html/1401.5377; 2 reads agree]`. β "increasing with Galactic longitude"; R0 = 8.34 ±
  0.16 kpc, Θ0 = 240 ± 8 km/s. β ranges: +3→101, −2→68, −8→27, −21→88, −6→56. N = 17, 18, 25, 24, 6.
- **Hy26** `[verified: Hyland, Reid et al. 2026, arXiv:2603.05896 (ApJ, doi 10.3847/1538-4357/ae64f5), Table 3,
  https://arxiv.org/html/2603.05896v1; 2 of 3 reads agree]`. Perseus in Q1 lies 0.5–1.0 kpc farther out than R19 put
  it; Perseus and Sagittarius cross on the far side near β ≈ 185°–224°, R ≈ 5.5–5.6 kpc (two models); a parent
  "Perseus-Sagittarius-Carina" arm is discussed.
- **X23** `[verified: Xu et al. 2023, ApJ 947, 54 = arXiv:2304.10690, Table 2, abstract, conclusions,
  https://arxiv.org/html/2304.10690 and https://arxiv.org/pdf/2304.10690; maser rows agree in 2 reads]`. 204 masers,
  23 807 O–B2 stars, 981 clusters younger than 20 Myr. Same spiral form and β convention as R19. O–B2 fits differ:
  Perseus ψ 1.9 ± 0.3 over β −30→40; Carina 17.5 ± 0.9; Local 10.0 ± 2.5; Outer −3.9 ± 0.5 and −1.1 ± 1.4.
- **Ho21** `[verified: Hou 2021, Front. Astron. Space Sci. 8, 671670, Table 1,
  https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2021.671670/full; one
  read, not in A1]`. "Kinked logarithmic spiral" with one or two kinks per arm; e.g. Local β_kink −2.0°, R_kink 8.46,
  ψ 4.4°/12.6°; Perseus 32.7°, 9.57, 3.9°/19.9°; Sgr-Car in two pieces; Norma 18.0°, 4.5, 1.3°/19.0°.
- **P21** `[verified: Poggio et al. 2021, A&A 651, A104 = arXiv:2103.01970, https://arxiv.org/pdf/2103.01970; one
  read]`. Upper-main-sequence overdensity maps (bandwidths 0.3 and 2 kpc). Local arm "at least 8 kpc" long, running
  ≥ 4 kpc into the third quadrant; Perseus steeper than R19 and geometry in Q3 "differs significantly" from R19.
- **V20** `[verified: VERA collaboration 2020, PASJ 72, 50 = arXiv:2002.03089, https://arxiv.org/pdf/2002.03089; one
  read]`. 99 sources; Ω_⊙ = 30.17 ± 0.27 ± 0.3 km/s/kpc.
- **W15** `[verified: Wegg, Gerhard & Portail 2015, MNRAS 450, 4050 = arXiv:1504.01401, abstract,
  https://ar5iv.labs.arxiv.org/html/1504.01401; 2 reads]`; best-fit α 28.4° (one component), 29.1°/30.0° (two).
  **BHG16** `[verified: Bland-Hawthorn & Gerhard 2016, ARA&A 54, 529 = arXiv:1602.07702, §4.2.1, §4.3,
  https://arxiv.org/pdf/1602.07702; one read plus a search extract]`; Ω_b ≈ 43 ± 9 km/s/kpc, R_CR 4.5–7.0 kpc.
- **NGC 4414**: **T96** `[verified: Thornley 1996, ApJ 469, L45 = arXiv:astro-ph/9607041, text and Tables 1–2,
  https://arxiv.org/pdf/astro-ph/9607041 and ar5iv; 2 reads agree]` — no pitch angle for any of its four galaxies.
  **TM97b** `[verified: Thornley & Mundy 1997, ApJ 490, 682, abstract only, https://iopscience.iop.org/article/
  10.1086/304907]` — NIR enhancements are old-star surface density; "stochastic processes are also important".
  **So02** `[verified: Soida et al. 2002, arXiv:astro-ph/0208180, Table 1, 2 reads]`; **Va02** `[verified: Vallejo,
  Braine & Baudry 2002, arXiv:astro-ph/0202391]` ("no bar and poorly defined spiral structure"; disc scale 2.5 kpc);
  **F05** `[verified: Fridman et al. 2005, arXiv:astro-ph/0409622]`; **RW04** `[verified: Rand & Wallin 2004,
  arXiv:astro-ph/0406426]` (no pattern speed could be claimed); **dB14** `[verified: de Blok et al. 2014,
  arXiv:1405.2160]` (D25 4.5′); **B15** `[verified: Buta et al. 2015, ApJS 217, 32, VizieR J/ApJS/217/32 table cvrhs,
  https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=J/ApJS/217/32&-out.all&Name=NGC%204414; one read]`. Each of
  these was one read except where said, and each covers only the NGC 4414 values quoted in A1.4.
- **Non-logarithmic form**: Ringermacher & Mead 2009 (MNRAS 397, 164 = arXiv:0908.0892). The search extract prints
  `r(φ) = A / log[B tan(φ/2N)]`; my fetch of the PDF garbled the formula, so it is not verified.

### A3 What a model could adopt

**Segment length.** Recommended: draw each segment's azimuthal extent from the HR15 distribution `[derived]`:
median 60°, quartiles 50°–80°, bounded 20°–180° (a lognormal of median 60° and σ_ln ≈ 0.35 reproduces the
quartiles). It predicts 3–5 segments on an arm that winds 180°–300°, matching DG19's mode of 3–4 segments per
galaxy, and arc lengths of median ≈ 6 kpc on a Milky-Way-sized disc. The five S4G segments of NGC 4414 span 37°–105°
`[derived]`, inside that range. Named alternatives: (B) constant arc length 5–8 kpc (R19's reading of HR15), which
makes inner segments span more azimuth than outer ones — HR15's NGC 3184 A (180° at 1.4 kpc) fits that, M 51 does
not; (C) segments defined in radius (r_i, r_o as in HE15), not read as a distribution. Shown wrong if: arms drawn
this way and re-measured as HE15 did give a segment count far from DG19's distribution.

**Pitch per segment and change at a kink.** Recommended: each segment's pitch an independent draw about the arm's
mean with sd ≈ 10° (HR15 pooled sd 9.9° `[derived]`; DG19 σ|φ| 9.5° ± 0.3° within a galaxy), which gives a change at
a join of rms ≈ 14° and median |Δψ| ≈ 10°, as HR15's 25 joins show (rms 14.4°, median 9.7°), signed mean zero, and
successive changes anticorrelated (12 of 15). Segments of zero or slightly reversed pitch must be allowed (3 of 38
in HR15; R19's Norma −1.0°, Sagittarius 1.0°). Named alternatives: (B) a random walk in pitch (Δψ iid): predicts sign
reversal in half of successive pairs and a spread growing along the arm — HR15 disfavours it, on 15 pairs only; (C)
relative variation, sd/mean = 0.56 ± 0.25 (S20), i.e. tighter arms vary less in degrees; (D) a smooth outward
decline (SR13's 64 %), against HR15 and DG19 who find no radial trend. Shown wrong if: σ|φ| re-measured on drawn
arms is not ≈ 9.5°, or the fraction with max-deviation/mean > 20 % is far from 2/3.

**Arm-to-arm.** Recommended: separate arm means a few degrees apart (HR15 global fits differ by 0.6°, 1.1°, 5.1° in
the two-armed cases; DH14's 2.6° for the longest arcs; S20's 16–27 % of ≈ 15°), with the 10° segment scatter on top.
Named alternative: L21's σ_gal = 11.0° ± 0.9° applied to whole arms — but that number absorbs along-arm variation
and tracing error of single-spiral fits (see A4).

**Milky Way pins (ready to enter).** Use A1.3's seven rows with `R(β) = R_kink exp(−(β − β_kink) tan ψ)`, R0 = 8.15
kpc, X = R sin β, Y = R cos β (Sun at β = 0). End radii over the data range `[derived]`: Norma 4.44 (β = 5) and 3.57
(54); Sct-Cen 5.43 (0) and 3.63 (104); Sgr-Car 6.80 (2) and 5.91 (97); Local 8.77 (−8) and 7.56 (34); Perseus 10.83
(−23) and 7.26 (115); Outer 12.63 (−16) and 10.50 (71); 3-kpc(N) 3.52–3.53. Pins are only measured inside each β
range (roughly a third of the disc on the Sun's side); beyond it R19 extrapolates with CO/HI tangencies and
kinematic distances. Enter Local as an isolated segment, the 3-kpc arm as bar-related, four major arms. Bar: long
bar 28°–33° from the Sun–centre line, near end at positive longitude (β > 0), half-length 5.0 ± 0.2 kpc; bulge bar
27° ± 2°. Named alternatives: Hy26's Perseus (one pitch 8.7° ± 0.7°, R = 9.08 at β = 40); X23's two inner arms with
bifurcations. Shown wrong if: Gaia young-star maps (P21) and further parallaxes keep moving Perseus and the third
quadrant away from R19 — already the case for Perseus in Q1 (Hy26).

**NGC 4414.** Can be pinned: no bar (family index 0.00); arm class F; inclination 52°–56° and PA 155°–160°; five
3.6 μm segments each with a pitch and a radial range (19.4″–87.4″; 1″ = 0.086 kpc at 17.8 Mpc `[derived]`), all of
one winding sense; a K′ ring at 20″ and two outer segments to north and south reaching ∼40″ over ∼60°. Cannot be
pinned: any locus. No source tabulates azimuths or positions of its arm pieces; HE15 stores radius ranges only, and
T96 gives sky directions ("north and south"), not deprojected azimuths. So the template can carry "unbarred,
flocculent, segment pitches −30.5, −34.2, −28.1, −44.0, −7.6° over the stated radii" and nothing positional beyond a
north/south pair near 0.4 R25. It predicts open (≈ 30°) short segments; shown wrong if another 3.6 μm or K′
measurement gives the ≈ 19°–21° typical of flocculents in DG19.

**Phase continuity and Fourier terms.** R19 and Ho21 write a kinked arm as one log spiral through (β_kink, R_kink)
with a different ψ each side, so position is continuous and only the slope d ln R/dβ jumps. HR15 fitted segments
independently; they meet to about an arm width in the one join I checked. No source read states the Fourier content
of a segmented arm; the statement that, for a mode m, a kink is a break in the slope of phase against ln R (not in
the phase) is my inference from that form. On resonances: HR15 ties outer narrowing to corotation and finds different
radii for M 51's two arms; no source read says kinks of different arms share a radius.

### A4 Conflicts between sources

1. Pitch against radius: SR13 (64 % fall outward) vs HR15 ("no systematic trend") vs DG19 (no change, statistically).
2. Arm-to-arm spread: L21's 11.0° vs S20's 16–27 % of ≈ 15° (≈ 2°–4°) vs DH14 (14.5° for all arcs, 2.6° for long ones).
3. NGC 4414 arm class: F in B15 and in HE15's Table 3, M in DG19's table a1 (read twice).
4. Segment length: "∼5 kpc" (HR15 abstract), "5 to 10 kpc" (HR15 text), "5 to 8 kpc" (R19 quoting HR15).
5. Milky Way: four arms (R19) vs two inner arms plus outer segments (X23); Scutum separate (R19) or part of Norma
   (X23); Sagittarius pitch 6.9° (R14), 1.0°/17.1° about a kink (R19), 1.3° and Carina 21.4° as separate arms (X23);
   Perseus R at β = 40°: 8.87 (R19) vs 9.08–9.29 (Hy26); Outer pitch 13.8° (R14) vs 3.0°/9.4° (R19) vs 3.6° (X23).
6. R0: 8.34 (R14), 8.15 (R19, X23, Hy26), 7.92 (V20), 8.2 (BHG16), 8.3 assumed (W15). β: "increasing with Galactic
   longitude" (R14) vs "in the direction of Galactic rotation" (R19) — the same sense, worded differently.
7. Transcription: my first fetch of R19's ar5iv page returned a Table 2 with other digits and a constant width; two
   later reads of that page found no table there. I discarded it. Hy26's ψ_< read once as 5.8 ± 0.7, twice as 5.9 ±
   1.2. DH14's Table 1 read once with 14.5° at the 50-pixel threshold, once at 0 pixels.

### A5 What could not be read

- R19 at IOP (refused, then bot wall) and its ar5iv HTML (no Table 2); ADS abstract pages (405, bot wall).
- A&A HTML pages (403): Kuhn+ 2021 on the Sagittarius high-pitch structure, the 2025 Cepheid spiral paper.
- Thornley & Mundy 1997a (ApJ 484, 202): not opened; 1997b: abstract only. Elmegreen & Elmegreen 1987's table
  (scan): the arm-class number for NGC 4414 not read. Elmegreen+ 1999 and Kendall+: not opened.
- Yu, Ho, Barth & Li 2018 (PDF came back empty) and Yu & Ho 2020: not read. D'Onghia+ 2013: empty. Kennicutt 1981,
  Hart+ 2018: not opened. "Chen et al. 2021" on Galaxy Builder: not found; the paper is Lingard et al. 2021.
- DG19's Table 2 by arm class row by row; the CDS ReadMe of its table a1; B15's own PDF row for NGC 4414.
- Ringermacher & Mead's formula (garbled); S20's per-class mean pitch (reads disagree).
