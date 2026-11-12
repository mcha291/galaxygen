# READING_GAS_SHOCK — the steady spiral shock, pattern speeds, and where the gas ridge sits (S57, BUILD_III Phase P2)

**The lead's note (2026-10-04).** Two Opus readers, briefed by BUILD_III §3e and forbidden the repository, wrote
what is below the rules; each part is entered as written. Part A is the shock's equations and the published
profiles a solver can be checked against; Part B is pattern speeds and the gas ridge's place and width. Gate G2
rules on them before anything is built (D216).

**Part C (added when S57 resumed, 2026-10-04).** Part A arrived as the earlier session paused and was entered
then. The resuming session, told that reader 1 had been cut off, put the same question to a fresh reader, also
blind to the repository, before it saw that Part A had landed: Part C is that reader's note as returned, its
headings one level down and its section labels changed from A to C. **The two readings are independent and
agree** on the system of equations, the regularity condition at the sonic point, the isothermal jump, and Kim,
Kim & Kim 2014's Table 1 to the digit. They differ in what each could open: Part A's reader read Roberts 1969
and Shu, Milione & Roberts 1973 as page images (rows B to F of its table); Part C's reader could not open the
scans and read Lee & Shu 2012, Lee 2014 and the simulation papers on co-rotating arms instead, and states the
two closures of the steady state exactly at corotation (C3).

---

## Part B — pattern speeds, and where the gas ridge sits (reader 2)

**Method and caveats.** Everything was read through the fetch tool (arXiv abstract pages, ar5iv HTML), blind to
the repository. The tool passes each page through a small model, so quotations are as relayed by it. Each number
below was on a fetched page, but anything load-bearing deserves a second look at the stated location. Long
reviews were truncated by the tool (§B5).

**Sign conventions differ between papers** and are stated per row. Inside corotation (CR) the gas overtakes the
pattern, so "upstream" is the trailing/concave side (smaller azimuth) and "downstream" is the leading side.

### B1. Summary tables (read statements only)

#### Pattern speeds

| # | Statement | Value | System | Source |
|---|---|---|---|---|
| A1 | Arms are transient; Ω_p falls with radius, "almost equal to the rotation curve" | arm lifetime ≈ 120 Myr (one arm, t = 1.73–1.85 Gyr); no Ω_p(R) values are printed - "almost equal to the rotation curve" (about 26 km/s/kpc at 8 kpc), not "~10 at 8 kpc" (*re-read at Audit V (S70)*) | N-body, pure stellar disc 3×10¹⁰ M☉, 3×10⁶ particles, static halo | `[verified: Grand, Kawata & Cropper 2012a, arXiv:1112.0019, abstract and pattern-speed section, https://ar5iv.labs.arxiv.org/html/1112.0019]` |
| A2 | Same with a bar: Ω_p(R) similar to stellar rotation, "slightly faster"; no offset between SF tracers across the arm | qualitative | N-body/SPH barred disc | `[verified: Grand, Kawata & Cropper 2012b, arXiv:1202.6387, abstract, https://arxiv.org/abs/1202.6387]` |
| A3 | "every single position in the arm can be regarded as the co-rotation point"; Ω_p decreases with radius like galactic rotation | no lifetime in Myr or rotation periods is printed: "the short-lived spiral arms can recurrently develop over many rotational periods" (abstract); the "0.3–0.5 rotation periods (~100–160 Myr at R = 2R_sd)" that stood here is the reader's (*re-read at Audit V (S70)*); max amplitude at pitch ~30° | N-body, 3×10⁸ particles, disc 3.2×10¹⁰ M☉, rigid NFW halo, no bar | `[verified: Baba, Saitoh & Wada 2013, ApJ 763, 46, arXiv:1211.5401, abstract, §3, §6, https://ar5iv.labs.arxiv.org/html/1211.5401]` |
| A4 | "The stellar spiral arms and the interstellar matter on average corotate in a galactic potential at any radii"; arm densities change on ~100 Myr | gas–arm relative Mach ~2 (against ~10–40 in rigid-potential models) | N-body/SPH, 3×10⁶ N-body + 10⁶ SPH particles | `[verified: Wada, Baba & Saitoh 2011, ApJ 735, 1, arXiv:1104.1287, abstract and body, https://ar5iv.labs.arxiv.org/html/1104.1287]` |
| A5 | Recurrent spirals are "the super-position of a few transient spiral modes"; each has greatest amplitude at its CR and extends "roughly as far as the Lindblad resonances" | each mode lasts 5–10 rotations at its CR | N-body, low-mass discs | `[verified: Sellwood & Carlberg 2014, arXiv:1403.1135, abstract and §2.5, https://ar5iv.labs.arxiv.org/html/1403.1135]` |
| A6 | "apparently shearing patterns are simply the result of the superposition of multiple separate modes"; a shearing ridge follows when lower-frequency modes peak at larger radii | m ~ R_CR κ²/(4πGΣ) (their eq. 9) | same | `[verified: Sellwood & Carlberg 2014, arXiv:1403.1135, §4.1 and footnote 4]` |
| A7 | Several transient patterns coexist, but "at any given time the disk favors patterns of certain pattern speeds" | three m = 2 patterns: ~20–30, ~40–43, > 50 km/s/kpc; the slow one persists most of 10 Gyr, fast ones ≲ 2 Gyr | N-body/SPH, 10⁶ particles per component | `[verified: Roškar et al. 2012, MNRAS 426, 2089, arXiv:1110.4413, abstract and §3, https://ar5iv.labs.arxiv.org/html/1110.4413]` |
| A8 | Bar + three spiral patterns with distinct speeds; slow two-armed patterns end at or inside their CR; the three-armed one spans its m = 3 ILR to OLR | bar ~40 km/s/kpc, CR ~6 kpc, OLR ~9 kpc; inner m = 2 0.030→0.022; outer m = 2 0.015; m = 3 0.023 Myr⁻¹ | N-body hybrid disc | `[verified: Quillen et al. 2011, arXiv:1010.5745, Table 1 and text, https://ar5iv.labs.arxiv.org/html/1010.5745]` |
| A9 | Non-linear coupling between bar and spiral, or spiral and spiral, "with a very sharp selection of the frequencies"; can outweigh swing amplification beyond the bar's CR | qualitative | 2-D N-body, m = 0–4 | `[verified: Masset & Tagger 1997, A&A 322, 442, arXiv:astro-ph/9902125, abstract, https://arxiv.org/abs/astro-ph/9902125]` |
| A10 | "evidence for non-linear coupling among m=1, 2, 3 and 4 density waves" | qualitative | Tree-SPH discs | `[verified: Minchev et al. 2012, arXiv:1203.2621, abstract, https://arxiv.org/abs/1203.2621]` |
| A11 | Diversity in cosmological discs: kinematic waves (Ω_p = Ω − κ/m, tidal case), manifold spirals (fixed Ω_p ~55 km/s/kpc out to the bar's OLR), dynamic co-rotating spirals, overlapping modes; one galaxy changes type | co-rotating arms grow and decay on ~100 Myr; a large-scale wave survives ≲ 1 Gyr | Auriga Superstars, ~10⁸ star particles per disc | `[verified: Grand et al. 2026, arXiv:2602.15108, abstract and results, https://ar5iv.labs.arxiv.org/html/2602.15108]` |
| A12 | Radial Tremaine–Weinberg: 1–3 piecewise-constant speeds per galaxy, inner faster; "In no case do we find that pattern speed is a smoothly decreasing function of radius" | M101: 47 ± 10 (to 6.7 kpc), 18 ± 1 (to 13.8 kpc), 5 ± 3. IC 342: 38 ± 7 (to 5.7 kpc), 11 ± 6. NGC 3344: 44 ± 4 to 6.8 kpc. NGC 3938: 53 ± 9.2 inside 3.4 kpc then 7.7 ± 1.6, or a single 6.6 ± 2.1 (km/s/kpc) | HI + CO cubes, 4 galaxies | `[verified: Meidt, Rand & Merrifield 2009, ApJ 702, 277, arXiv:0907.3443, §3–4, https://ar5iv.labs.arxiv.org/html/0907.3443]` |
| A13 | Transitions sit at resonance overlaps: M101 inner OLR ≈ outer pattern's inner 4:1 at ~7 kpc; IC 342's outer pattern starts near its ILR (or inner 4:1) | as stated | same | `[verified: Meidt, Rand & Merrifield 2009, arXiv:0907.3443, §3.2, §3.3]` |
| A14 | M51: speeds inside 4 kpc "both ending at corotation" | 90 (+20/−27) to 2.1 kpc; 50 (+9/−11) to 4.1 kpc; tentative 23 (+6/−7) for 4–5.3 kpc; conventional global value 38 km/s/kpc | CO, D = 9.5 Mpc, i = 24° | `[verified: Meidt et al. 2008, arXiv:0807.1902, abstract and results, https://ar5iv.labs.arxiv.org/html/0807.1902]` |
| A15 | NGC 1068: pattern speed "varies rapidly with radius", lifetime "very short" | qualitative | CO, generalised TW | `[verified: Merrifield, Rand & Meidt 2006, MNRAS 366, L17, arXiv:astro-ph/0511069, abstract, https://arxiv.org/abs/astro-ph/0511069]` |
| A16 | NGC 1365 HI pattern: Ω_p ≈ 1/r, like the material speed; no CR or Lindblad resonances found | Ω_p = 2.87 (± 0.61) × 10² km/s ÷ r; winding time ~500 Myr | HI | `[verified: Speights & Westpfahl 2011, ApJ 736, 70, arXiv:1105.2572, abstract and Tables 2, 4, https://ar5iv.labs.arxiv.org/html/1105.2572]` |
| A17 | M81: Ω_p "more similar to the material speed than ... a rigidly rotating pattern", "no clear indications of unique corotation or Lindblad resonances" | qualitative (four HI data sets agree) | HI | `[verified: Speights & Westpfahl 2012, ApJ 752, 52, arXiv:1205.0304, abstract, https://arxiv.org/abs/1205.0304]` |
| A18 | Caveat on A12–A17: "in general, applying TW to observations of gas will not recover the true pattern speed" | — | hydro simulations with a known bar speed | `[verified: Borodina et al. 2023, arXiv:2306.17780, abstract, https://arxiv.org/abs/2306.17780]` |
| A19 | Six nearby galaxies each hold at least two independent spiral patterns in resonance coupling | new coupling form: OLR_in = OUHR_out and OUHR_in = CR_out (two galaxies) | literature CR measurements, flat curve | `[verified: Marchuk 2024, A&A 686, L14, arXiv:2405.14483, abstract, https://arxiv.org/abs/2405.14483]` |
| A20 | Milky Way bar and spiral "dynamically decoupled" | bar Ω_b ≃ 50–60 km/s/kpc, R_CR ≃ 3.5–4.5 kpc; spiral Ω_sp ≃ 25 ± 2 (range 17–28), R_CR,sp = (1.06 ± 0.08) R₀ | review of methods | `[verified: Gerhard 2011, arXiv:1003.2489, abstract and body, https://ar5iv.labs.arxiv.org/html/1003.2489]` |
| A21 | Milky Way, one speed for three arms | 28.2 ± 2.1 km/s/kpc "with no difference between the arms"; R_c = 8.51 ± 0.64 kpc | open clusters < 50 Myr, Gaia DR2 | `[verified: Dias et al. 2019, arXiv:1905.08133, abstract, https://arxiv.org/abs/1905.08133]` |
| A22 | Milky Way, a different speed per arm, following the rotation curve | Scutum 46.85 ± 1.73 (R = 6.02 kpc), Sagittarius 26.52 ± 2.03 (7.10), Local 31.85 ± 0.77 (8.69), Perseus 21.25 ± 2.16 (10.88) km/s/kpc | 264 young open clusters, Gaia EDR3 | `[verified: Castro-Ginard et al. 2021, A&A 652, A162, arXiv:2105.04590, abstract and Table 2, https://ar5iv.labs.arxiv.org/html/2105.04590]` |
| A23 | Milky Way red-giant ⟨v_R⟩ fit assumes its speed | 12 km/s/kpc (assumed, not measured); pitch ~12°; arm/interarm ± 10 % at R₀ | — | `[verified: Eilers et al. 2020, arXiv:2003.01132, abstract, https://arxiv.org/abs/2003.01132]` |
| A24 | UGC 3825: young-star offsets fit "a pattern speed that varies little with radius" | qualitative | one grand-design galaxy | `[verified: Peterken et al. 2019, arXiv:1809.08048, abstract, https://arxiv.org/abs/1809.08048]` |

#### Offsets

| # | Value and sign | Tracer pair, convention | Sample | Source |
|---|---|---|---|---|
| B1 | "typically a few degrees"; fitted as Δφ(r) = (Ω(r) − Ω_p)·t with t = 1–4 Myr; R_cor/R_s ≃ 2.7 ± 0.2; Ω_p from 11 ± 1.0 to 42 ± 2 km/s/kpc; four galaxies problematic | Δφ = φ_24µm − φ_HI; > 0 inside CR | 14 galaxies, to ~0.8 R25 | `[verified: Tamburro et al. 2008, AJ 136, 2872, arXiv:0810.2391, eqs. 1, 8, Table 2, https://ar5iv.labs.arxiv.org/html/0810.2391]` |
| B2 | "In none of the resulting tracer cross-correlations ... do we find systematic angular offsets"; typically < 5°, no positive-to-negative trend; could not reproduce B1 | HI, CO, 24 µm, FUV, 3.6 µm cross-correlations | 12 galaxies | `[verified: Foyle et al. 2011, ApJ 735, 101, arXiv:1105.5141, abstract and results, https://ar5iv.labs.arxiv.org/html/1105.5141]` |
| B3 | Clear offsets in 5 of 13, none in 2 (both barred), ambiguous in 5. θ = 0.586 (Ω − Ω_P)(t_SF/10⁷ yr). Ω_P / t_SF: NGC 628 16 ± 3 / 28.2 ± 3.1; NGC 4254 10 ± 3 / 12.4 ± 1.3; NGC 4303 24 ± 29 / 10.8 ± 5.7; NGC 5194 40 ± 4 / 13.8 ± 0.7; NGC 5457 72 ± 37 / 4.0 ± 1.3 | CO against Hα arms | 13 galaxies | `[verified: Egusa et al. 2009, ApJ 697, 1870, arXiv:0904.3121, tables, https://ar5iv.labs.arxiv.org/html/0904.3121]` |
| B4 | M51: CO→Hα 5–30°, mostly positive, substantial scatter; HI→Hα mostly zero; HI is mostly photodissociated gas downstream of CO, which reconciles B1 with B2 | positive = SF downstream of gas | M51, arm 1 | `[verified: Louie, Koda & Egusa 2013, ApJ 763, 94, arXiv:1301.2601, abstract and results, https://ar5iv.labs.arxiv.org/html/1301.2601]` |
| B5 | M51 gas arm against stellar-mass arm: inner arm 2 moves from about −45° to ~0° with radius, fitting a galactic shock with R_CR = 168″; inner arm 1 has no systematic trend; outer arms scatter about zero | offset = az(gas) − az(star) | M51, two arms | `[verified: Egusa et al. 2017, MNRAS 465, 460, arXiv:1610.06642, abstract and Fig. 7 discussion, https://ar5iv.labs.arxiv.org/html/1610.06642]` |
| B6 | CO→Hα: mean 230 pc, median 220 pc, range −400 to +740 pc; median scatter ~1 kpc. **4/24 (17 %) positive with a declining trend (a single density wave); 10/24 (42 %) positive without a trend; 10/24 (42 %) not significantly positive** | positive = Hα ahead of CO in rotation; ~100 pc resolution | 24 PHANGS galaxies with clear arms | `[verified: Querejeta et al. 2025, arXiv:2509.01668, abstract and results, https://ar5iv.labs.arxiv.org/html/2509.01668]` |
| B7 | Ω_p and R_CR for the four: NGC 1385 26.1 ± 13.8, 4.8 kpc; NGC 1566 25.0 ± 4.8, 7.6 kpc; NGC 2283 28.2 ± 7.0; NGC 4303 34.8 ± 20.1, 5.9 kpc | from the offset trend | 4 galaxies | `[verified: Querejeta et al. 2025, arXiv:2509.01668]` |
| B8 | Pitch angle falls from red to blue; relative to I band: R −0.5 ± 0.1°, V −0.7 ± 0.1°, B −1.1 ± 0.2°, NUV −1.6 ± 0.5°, FUV −2.2 ± 0.6° | pitch per band | CGS, 50–71 images | `[verified: Yu & Ho 2018, arXiv:1810.08979, abstract and results, https://ar5iv.labs.arxiv.org/html/1810.08979]` |
| B9 | Opposite sign to B8: B and 3.6 µm pitch smaller than 8.0 µm "in all cases" | pitch per band | Pour-Imani 2016; Miller 2019 | `[verified: Pour-Imani et al. 2016, ApJL 827, L2, arXiv:1608.00969, abstract; Miller et al. 2019, ApJ 874, 177, arXiv:1907.09390, abstract]` |
| B10 | Colour (age) gradients across arms match density-wave predictions in 10 of 13 galaxies | azimuthal colour gradients | 13 SA/SAB galaxies | `[verified: Martínez-García et al. 2009, ApJ 694, 512, arXiv:0812.3647, abstract, https://arxiv.org/abs/0812.3647]` |
| B11 | Cluster age gradient across arms: NGC 1566 significant; M51a none; NGC 628 none | LEGUS clusters | 3 galaxies | `[verified: Shabani et al. 2018, arXiv:1805.05643, abstract, https://arxiv.org/abs/1805.05643]` |
| B12 | NGC 4321: "No significant offsets are found, favouring instead a mechanism where the pattern speed has a radial dependence" | 787 UV sources | 1 galaxy | `[verified: Ferreras et al. 2012, MNRAS 424, 1636, arXiv:1204.1974, abstract, https://arxiv.org/abs/1204.1974]` |
| B13 | M81: "no evidence of star formation propagation across the spiral arm" | resolved SFHs of 20 regions | 1 galaxy | `[verified: Choi et al. 2015, ApJ 810, 9, arXiv:1507.07000, abstract, https://arxiv.org/abs/1507.07000]` |
| B15 | Milky Way: gas tracers share tangency longitudes; old stars displaced by 1.3°–5.8° near Scutum–Centaurus | tangency longitudes | Milky Way | `[verified: Hou & Han 2015, arXiv:1508.04263, abstract, https://arxiv.org/abs/1508.04263]` |
| B17 | Theory, rigid wave: Θ = m(θ_shock − θ_min), Θ < 0 upstream. "At small radii, the shock occurs almost at the potential minimum, but as the radius increases and the shock becomes weaker, it moves upstream toward the potential maximum" (Θ → −π towards CR). Base-subsonic zone bounded by R sin i (Ω − Ω_P) = ± a; no solutions between 11 and 12.5 kpc in the standard model; "difficult to predict without performing a full calculation" | standard model: m = 2, sin i = 0.1, Ω_P = 13 km/s/kpc, a = 8 km/s, F₀ = 0.05 at 8.5 kpc, v₀ = 220 km/s, CR ≈ 17 kpc | semi-analytic + hydro | `[verified: Gittins & Clarke 2004, MNRAS 349, 909, arXiv:astro-ph/0312562, abstract, §3.1, §4.1, Table 1, https://ar5iv.labs.arxiv.org/html/astro-ph/0312562]` |
| B19 | Steady rigid spirals: offset depends on radius "regardless of the strength and pitch angle of the spiral and the model of the ISM". **Dynamic spirals: "no systematic radial dependence of the arm-gas offsets"** | steady: Ω_p ≃ 23 km/s/kpc, CR ~10 kpc, pitch 10° and 20°, F = 2–5 %; dynamic: N-body/SPH | simulations | `[verified: Baba, Morokuma-Matsui & Egusa 2015, arXiv:1505.02881, abstract and §3, https://ar5iv.labs.arxiv.org/html/1505.02881]` |
| B20 | Local rigid arm: shock front at x/L_x ≈ −0.02 (−0.05 for the other field strength), potential minimum at x = 0; self-gravity moves it downstream | Ω_p = Ω₀/2, sin i = 0.1, c_s = 7 km/s, L_x = 3.1 kpc, F = 1–6 % | local MHD | `[verified: Kim & Ostriker 2002, ApJ 570, 132, arXiv:astro-ph/0111398, §2.2 and results, https://ar5iv.labs.arxiv.org/html/astro-ph/0111398]` |
| B21 | Time-evolving multi-armed potential: "instead of passing through the spiral arms, gas generally falls into a developing potential minimum"; "Particles enter the minimum from both sides"; dense gas "strongly coincides with the potential minimum"; "no fixed pattern speed or co-rotation radius" | potential from N-body, dominant m between 2 and 8; 27 million SPH particles | simulation | `[verified: Dobbs & Bonnell 2008, MNRAS 385, 1893, arXiv:0801.3562, abstract and §3.2, https://arxiv.org/html/0801.3562]` |
| B22 | Clusters < ~30 Myr sit on the stellar arms "without a clear spatial offset between gas spiral arms and distribution of young stars" | live disc | simulation | `[verified: Wada, Baba & Saitoh 2011, arXiv:1104.1287, abstract]` |
| B23 | Age patterns: a steady wave gives a monotonic age increase across the arm; a flocculent disc gives similar ages within a segment and no trend across | clusters of ~2–130 Myr | 4 simulations | `[verified: Dobbs & Pringle 2010, arXiv:1007.1399, §3–7, https://ar5iv.labs.arxiv.org/html/1007.1399]` |

#### Widths

| # | Value | Definition | System | Source |
|---|---|---|---|---|
| C1 | Gas arms ≃ 30° FWHM (inner), ≃ 5° (outer); stellar arms ≃ 60° (inner), ≃ 30° (outer) | FWHM in azimuth | M51 | `[verified: Egusa et al. 2017, arXiv:1610.06642]` |
| C2 | Scutum 0.17 ± 0.02 kpc at 5.0 kpc; Sagittarius 0.26 ± 0.02 at 6.6; Local 0.33 ± 0.01 at 8.4; Perseus 0.38 ± 0.01 at 9.9; Outer 0.63 ± 0.18 at 13.0 | intrinsic scatter of high-mass star-forming regions perpendicular to the fitted spiral | Milky Way, 103 maser parallaxes | `[verified: Reid et al. 2014, ApJ 783, 130, arXiv:1401.5377, Table 2, https://ar5iv.labs.arxiv.org/html/1401.5377]` |
| C3 | w(R) = 336 + 36 (R[kpc] − 8.15) pc | Gaussian 1σ intrinsic width | Milky Way, ~200 maser parallaxes | `[verified: Reid et al. 2019, arXiv:1910.03357, Fig. 4 and text, https://ar5iv.labs.arxiv.org/html/1910.03357]` |
| C4 | Width grows with radius in all major arms, as in the Milky Way | scatter of HII regions about the fitted spiral | NGC 628, 1232, 3184, 5194 | `[verified: Honig & Reid 2015, ApJ 800, 53, arXiv:1412.1012, abstract, https://arxiv.org/abs/1412.1012]` |

### B2. Per-source notes

- **Egusa 2017's wording.** With azimuth increasing along rotation, negative az(gas) − az(star) places the gas
  behind the stellar peak, the upstream side inside CR. Baba 2015 uses the opposite sign. The physical statement
  both share: under a galactic shock the gas arm moves from downstream to upstream of the stellar arm with
  increasing radius inside CR.
- **C1 as a fraction of the arm period** (the reader's arithmetic, two arms, period 180°): gas FWHM ≈ 1/6 inner and
  ≈ 1/36 outer; stellar ≈ 1/3 inner and 1/6 outer.
- **C2 and C3 trace star formation, not gas**: the scatter of masers in high-mass star-forming regions, an upper
  proxy for the dense ridge's width. Their slope is the only fitted width–radius relation found.
- **Gittins & Clarke's subsonic zone** (the reader's arithmetic on B17): for a flat curve the bound gives
  |1 − R/R_CR| < a/(v₀ sin i) = 8/(220 × 0.1) ≈ 0.36 — a wide band around CR with no shock, narrowing as the
  pitch angle grows.
- **Meidt 2009** fits piecewise-constant speeds in radial bins, which biases it against finding a smooth decline.
- **Speights & Westpfahl** use HI; Borodina 2023 shows TW on gas generally fails. "Ω_p ≈ Ω" from HI is therefore
  weak evidence for material stellar arms.
- **Sellwood & Carlberg 2014**: the lifetime (5–10 rotations at CR) is for a mode; the ~100–160 Myr lifetimes of A1
  and A3 are for a visible arm. The two are not directly comparable.
- **Querejeta 2025** measures gas against star formation, not gas against the stellar arm.
- **Dias 2019 and Castro-Ginard 2021** use the same method on Gaia data and reach opposite conclusions.

### B3. What a model could adopt (the frame's speed on a ring)

**R1. Ω_frame(R) = Ω(R) for every mode (material arms).** For: A1–A4, A22, A16–A17 (weak), B2, B12, B13, B21, B22,
and the 42 % of B6 with no positive offset. Against: A5–A8 (the same simulations decompose into discrete modes),
A12, A21, A24, B3, B5 arm 2, B10, B15, and the 17 % + 42 % of B6 with positive offsets. *Predicts:* no flow through
the arm, so no galactic shock; gas converges on the potential minimum from both sides at Mach ~2; the ridge sits
on the stellar crest with zero mean offset at all radii. *Fails if* a ring-averaged offset is systematically
non-zero with a radial trend.

**R2. One rigid Ω_p per mode m, with CR where that mode's amplitude peaks, acting only between its Lindblad
resonances.** For: A5–A8, A12–A14, A10, B10. Against: needs a global peak radius per mode; A22; B2; nothing read
says how the gas responds to several superposed frames on one ring. *Predicts, per mode:* a shock only where
R sin i |Ω − Ω_p| > a; the phase offset near 0 well inside CR, sliding upstream towards −π as CR is approached; a
shock-free band around CR; the sense reversed outside. *The reader's inference:* if mode power is set ring by ring
by local swing amplification, taking the peak radius as the ring itself collapses R2 into R1; Sellwood &
Carlberg's own remark (A6) says the superposed ridge then shears at about Ω(R).

**R3. A few global rigid patterns chained by resonance overlap.** For: A9, A12–A14, A19, A8. *Predicts* a saw-tooth
of offsets in radius.

**R4. One global Ω_p with CR at a fixed disc radius.** For: B1 (R_cor ≃ 2.7 ± 0.2 R_s), A20–A21, A24, B7. Against:
A12–A14, A22, B2. *Fails* for the 83 % of B6 without that trend.

**R5. A kinematic wave, Ω_p = Ω − κ/m.** Found only for a tidally driven case (A11).

**Several modes on one ring.** No source read gives a rule. Either superpose per-mode responses, each in its own
frame, so the gas response is not steady in any frame; or treat the composite ridge as moving at about Ω(R),
which is R1. The literature treats these as two descriptions of the same simulations (A6); the gas offset is the
discriminator (B19).

### B4. Conflicts between sources (reported, not averaged)

1. **Simulations, material arms or modes.** Grand 2012a,b, Baba 2013 and Wada 2011: Ω_p(R) ≈ Ω(R). Sellwood &
   Carlberg 2014 and Roškar 2012: a few modes with fixed Ω_p. Grand 2026 finds both, in different galaxies and at
   different times.
2. **External galaxies.** Meidt 2008/2009: piecewise-constant speeds, never a smooth decline. Speights & Westpfahl
   and Merrifield 2006: speeds varying like the material speed. Borodina 2023 touches both camps.
3. **Milky Way.** Dias 2019: one speed, 28.2 ± 2.1. Castro-Ginard 2021: a speed per arm, 46.85 to 21.25, following
   the rotation curve. Gerhard 2011: 25 ± 2. Eilers 2020 assumes 12.
4. **HI to 24 µm offsets.** Tamburro 2008 finds ordered offsets in 14 galaxies; Foyle 2011 finds none in 12 and
   cannot reproduce Tamburro; Louie 2013 attributes the difference to HI being a dissociation product.
5. **Pitch angle by band.** Yu & Ho 2018: blue tighter than red. Pour-Imani 2016 and Miller 2019: the reverse.
6. **Age gradients.** Present in NGC 1566, in 10 of 13 galaxies (Martínez-García) and UGC 3825; absent in M51a,
   NGC 628, M81 and NGC 4321.
7. **M51 itself.** Its two arms behave differently (Egusa 2017).

### B5. What could not be read

- **Dobbs & Baba 2014** (arXiv:1407.5062): truncated after §2.3.1; §3 (gas) and §4 unread. **Sellwood & Masters
  2022**: truncated before §5–§7. **Bland-Hawthorn & Gerhard 2016**: truncated in §4.2.
- Tables and figures not reached: Kim & Ostriker 2002 Table 1 (arm width); Honig & Reid 2015's fitted slopes;
  Egusa 2017 Fig. 7's values; a Sellwood & Carlberg mode table.
- Abstract only: Kawata et al. 2014, Minchev 2012, Sellwood 2011, Baba et al. 2017.
- Not attempted or not found: Grand et al. 2013, Tagger et al. 1987, Kim & Ostriker 2006, Wada 2008, Schinnerer
  et al. 2017.
- `[recall — NOT READ]` The Tagger 1987 coupling condition is usually stated as bar CR ≈ spiral ILR.
- `[recall — NOT READ]` The classical placement of dust lanes on the concave edge of trailing arms inside CR.
- **No closed-form formula** for the shock's offset against radius, sound speed and distance from CR was found:
  Gittins & Clarke say it needs the full calculation. The only closed forms read are the star-formation tracer's
  drift Δφ = (Ω − Ω_p)·t and the subsonic zone's bound R sin i (Ω − Ω_P) = ± a.
- **No measured gas-ridge width against distance from CR** was found.

---

## Part A — the steady one-dimensional isothermal flow through a spiral potential (reader 1)

*Entered by the lead from the reader's report as it arrived at the session's pause; the equations, the table and
the statements are the reader's, the wording shortened in places.* Blind to the model. **How things were read:**
Roberts 1969 and Shu, Milione & Roberts 1973 as page images in the ADS scan viewer, by eye; Gittins & Clarke 2004,
Kim, Kim & Kim 2014, Sormani et al. 2017, Kim & Ostriker 2002 and Kim & Kim 2014 as arXiv/ar5iv HTML with each
equation's LaTeX extracted. All treat a razor-thin isothermal gas forced by an imposed, rigidly rotating
potential; the first five have no gas self-gravity and no magnetic field.

Source keys: **R69** `[verified: Roberts 1969, ApJ 158, 123, https://ui.adsabs.harvard.edu/scan/manifest/1969ApJ...158..123R]`;
**SMR** `[verified: Shu, Milione & Roberts 1973, ApJ 183, 819, https://ui.adsabs.harvard.edu/scan/manifest/1973ApJ...183..819S]`;
**GC** `[verified: Gittins & Clarke 2004, MNRAS 349, 909, https://ar5iv.labs.arxiv.org/html/astro-ph/0312562]`;
**KKK** `[verified: Kim, Kim & Kim 2014, ApJ 789, 68, https://arxiv.org/html/1405.5874v1]`;
**S17** `[verified: Sormani et al. 2017, MNRAS, https://ar5iv.labs.arxiv.org/html/1707.00301]`;
**KO02** `[verified: Kim & Ostriker 2002, ApJ 570, 132, https://ar5iv.labs.arxiv.org/html/astro-ph/0111398]`;
**KK14** `[verified: Kim & Kim 2014, MNRAS 440, 208, https://arxiv.org/html/1402.2291]`.

### A1. The equations

**SMR's lowest-order form (SMR §II–III, eqs. 1–12, pp. 820–823)**, m arms, one sinusoidal forcing:
- (S1–S3) 𝔙 = 𝔙₀(ϖ) + A(ϖ) cos χ, χ = Φ(ϖ) − mφ, φ = θ − Ω_p t; η = −χ + π; tan i = −m/(kϖ), k = Φ′ negative for
  trailing arms. **η = 0 is the potential minimum**; one arm-to-arm passage is Δη = 2π for any m.
- (S4) F = (k² + m²ϖ⁻²)^{1/2} A / (ϖΩ²): the maximum spiral force over ϖΩ².
- (S7a) (σ₀+σ₁)(u_η0+u_η1) = σ₀ u_η0
- (S7b) ∂u_η1/∂η = U (u_η0+u_η1)(2u_ξ1 − FϖΩ sin η) / [(u_η0+u_η1)² − a²]
- (S7c) ∂u_ξ1/∂η = −V u_η1/(u_η0+u_η1)
- (S8) u_η0 = ϖ(Ω−Ω_p) sin i; u_ξ0 = ϖ(Ω−Ω_p) cos i; U = (sin i/m) ϖΩ; V = (sin i/m) ϖκ²/2Ω
- (S9) ν ≡ m(Ω_p−Ω)/κ = −u_η0/(2UV)^{1/2}; x ≡ a²/2UV
- (S10) u ≡ u_η1/(2UV)^{1/2}; v ≡ u_ξ1/V
- (S11) ∂u/∂η = (u−ν)(v − f sin η)/[(u−ν)² − x]; ∂v/∂η = u/(ν−u)
- (S12) f ≡ FϖΩ/2V = (Ω/κ)²(mF/sin i)

Three parameters (ν, x, f). Density from (S7a): σ/σ₀ = −ν/(u−ν). The constants may be held fixed along a
streamline "as long as F is not large in comparison with sin i"; single-valuedness is periodicity in η with period
2π. GC's Appendix A reproduces S7–S11 identically.

**The local Cartesian form (KKK §II–III, eqs. 1, 4, 5, 8–13)**, the most convenient for a general periodic Φ: x the
distance perpendicular to the arm, L = 2πR sin i/m, Φ_s = Φ₀ cos(2πx/L), the minimum at x = L/2.
- (K1) u_c = R(Ω−Ω_p) sin i; q ≡ −dlnΩ/dlnR; (K5) ℱ ≡ (m/sin i)(Φ₀/R²Ω²); (K8) Σ₀ u_T0 = Σ_c u_c
- (K10) u_T0 dv₀/dx = −(κ²/2Ω) u₀, u₀ = u_T0 − u_c, κ² = (4−2q)Ω²
- (K11) (u_T0 − c_s²/u_T0) du_T0/dx = 2Ωv₀ + RΩ²ℱ sin(2πx/L); the last term is −dΦ_s/dx.
Substituting η = 2πx/L − π maps K10–K11 onto S7b–c (the reader's check). S17's eqs. 13–14 are the same system
with κ = 2Ω. **Roberts 1969's original form** (R69 §II c–d, eqs. 5–22) is the same physics with small curvature
terms χ₁,₂,₃ kept in his numerics; F there is "the amplitude of the perturbation force as a fraction of the mean
axisymmetric gravitational field".

### A2. Constructing the periodic solution with a shock

1. **Singular points:** u = ν, ν − √x, ν + √x are u_η = 0, −a, +a; the third is the sonic point where the gas goes
   subsonic → supersonic after the shock (GC App. A).
2. **Regularity there:** v(η_SP) = f sin η_SP with u = ν + √x. Series start with α ≡ √x: u = (α+ν) + A_SP(η−η_SP),
   v = f sin η_SP − (1+ν/α)(η−η_SP), A_SP = (½)^{1/2}[−(1+ν/α) − f cos η_SP]^{1/2} (SMR App. eqs. A6–A7).
3. **Existence at the sonic point:** −1 + |ν|/α − f cos η_SP > 0; cos η_SP > 0 for |ν| > α (an upper cutoff on f)
   and < 0 for |ν| < α (a lower cutoff) (SMR eq. A10).
4. **Regularised variables (no series needed):** u = ν + √x + ũ, v = f sin η + ṽ, w̃ = ũ²; then
   ∂w̃/∂η = 2(√x ± √w̃)ṽ/(2√x ± √w̃), ∂ṽ/∂η = −1 − f cos η − ν/(√x ± √w̃), + on the supersonic branch, − on the
   subsonic; start at w̃ = ṽ = 0 (GC App. A).
5. **The jump:** isothermal, u_sup·u_post = a², v continuous; the density ratio is M₁² (SMR eq. A8; KKK eqs. 20–21).
6. **Closure:** integrate from η_SP forward (supersonic) and backward (subsonic); the shock is where the
   post-shock branch crosses the subsonic branch at equal v; η_SP is adjusted until the period is 2π (GC App. A;
   SMR App. p. 840). KKK iterate the sonic point "until all the jump conditions are met within tolerance
   (typically ∼10⁻⁵)".
7. **Method:** no source gives a step count. SMR: "Four-place accuracy is easily achieved". GC: in the
   base-subsonic region the window of η_SP that yields a shock "can have a width of less than π/1000".
8. **No shock:** integrate from η = 0 to 180° with v(0) = 0 and choose u(0) so that v(180°) = 0 (this uses a
   single cosine's symmetry). The linear limit: u_η1 = f(2UV)^{1/2} α₁₁ cos η, u_ξ1 = fVβ₁₁ sin η,
   α₁₁ = ν(1−ν²+x)⁻¹, β₁₁ = (1−ν²+x)⁻¹ (SMR eqs. 16a, 18–19).
9. **Threshold:** as f rises the smooth solution forms a cusp on the sonic line, at η = 0 (base-supersonic) or
   ±180° (base-subsonic); F_cusp is the upper limit of smooth flow and the lower limit of shocked flow.
10. **Ultraharmonic resonances:** the series diverges where ν² − x = n⁻²; n = ±1 are the pressure-shifted Lindblad
    resonances. Near n = −2 there are two shocks and a two-parameter search; GC: single-shock solutions are
    "difficult or impossible to find for F ≳ 0.1 and sin i ≳ 0.2".

### A3. Checkable published cases

| # | Source and case | Parameters | Numbers to reproduce | Precision |
|---|---|---|---|---|
| A | **KKK Table 1** (no self-gravity, no field, one cosine) | q = 1, m = 2, sin i = 0.1, Ω_p/Ω = 0.5, c_s/(RΩ) = 0.027; minimum at x/L = 0.5 | ℱ = 0.03: x_sp/L 0.458, x_sh/L 0.402, μ 5.67. ℱ = 0.05: 0.507, 0.431, 11.6. ℱ = 0.10: 0.615, 0.495, 34.5. ℱ = 0.20: 0.699, 0.560, 97.3. Σ₀(x_sp)/Σ_c = u_c/c_s = 1.86 | tabulated, 3 figures |
| B | SMR Figs. 1, 2, 4, ϖ = 10 kpc | Ω 24.7, κ 31.0 km/s/kpc, i 6.7°, u_η0 13.0, u_ξ0 111.2, U 14.4, V 11.3 km/s; Ω_p 13.5; a = 8 km/s; m = 2 | F_cusp = 0.97 %, cusp at η = 0. F = 5 %: shock at η = 334° (−26°), "a factor 12:1" total density variation, peak "∼5 times" the average | labels exact; from the figures, pre-shock u_η ≈ 26.5 and post-shock ≈ 2.4 km/s (± 0.3), peak σ/σ₀ ≈ 5.2–5.3 |
| C | SMR Figs. 5–6, ϖ = 14 kpc (base-subsonic) | Ω 15.5, κ 15.0, i 8.4°, u_η0 4.1, U 15.9, V 7.5; a = 8 | F_cusp = 3.7 %, cusp at η = ±180° (the potential maximum). F = 5 %: shock at −122°. F = 7 %: −86°. The density peaks near η ≈ 0, not at the shock | labels exact; peaks ≈ 1.25 (2 %), 1.45 (3.7 %), 1.6 (5 %), 1.9 (7 %), ± 0.05 |
| D | SMR Figs. 7–8, ϖ = 11 kpc (the n = −2 resonance) | Ω 21.9, κ 25.6, i 7.0°, u_η0 11.2; a = 8 | F_cusp = 1.1 % with two cusps at η = ±54°. F = 3 %: one shock at −55°, peak σ/σ₀ ≈ 3.0 | labels exact |
| E | R69 Figs. 3 and 5 | tan i = 1/7, Ω_p = 12.5, F = 5 %, ϖ = 10 kpc, a = 10 km/s | enters the shock at "about 31 km sec⁻¹", leaves at "about 3.2", "density contrast across the shock is about 9.6" | captions, 2 figures |
| F | R69 Fig. 8 and Table 1 | tan i = 1/7, (K/2Ω)² = 0.4, w′⊥0 = 0.049, a′ = 0.034 | F (%) → σ(2)/σ(1), M₁: 7.5 → 9.2, 3.0; 5.0 → 6.2, 2.5; 2.0 → 2.4, 1.6; 1.04 → 1.4, 1.2. No solution below about 1.04 % | tabulated |
| G | S17 Figs. 1–2 (κ = 2Ω) | L = 1, units F_y = Ω = 1 | c_s = 0.7: Φ_c = 0.07297 | stated in the text |
| I | KO02 Table 1 (**with** self-gravity) | c_s = 7 km/s, Ω_p = Ω₀/2, sin i = 0.1 | F 1 / 2 / 3 %: Σ_max/Σ₀ = 2.36 / 3.91 / 6.49, width W/L_x = 0.16 / 0.06 / 0.05 | tabulated; not like for like with a pure hydrodynamic solver |

Derived from row A by the reader: shock phase relative to the minimum −35.3°, −24.8°, −1.8°, +21.6°; peak Σ/Σ_c
just behind the shock 4.4, 6.3, 10.9, 18.3. In SMR's variables row A is ν = −0.707, x = 0.146, f = 10ℱ, and row B
ν = −0.721, x = 0.197, f = 0.546 at F = 5 %: near neighbours, and their shock phases (−24.8° and −26°) agree.
Row B's width (read from Fig. 4, ± 5°): σ falls to half its peak about 26° after the shock, 0.07 of a period.

### A4. Scalings

- **With F:** the jump and the peak grow steeply (row A: μ rises 17-fold for a 6.7-fold rise in ℱ); the shock
  and the sonic point move downstream as F grows; "weaker spirals will form shocks further upstream" (GC §5.1).
- **With a:** at 10 kpc with a = 30 km/s the flow is entirely subsonic and at F = 5 % "differs little from the
  behavior predicted by the linear theory" (SMR Fig. 3).
- **Width:** "When u_η0 > a … the zone of high gas compression is very narrow. When u_η0 ≲ a … broad" (SMR §VII).
- **Offset inside corotation:** upstream of the minimum (the inner side of a trailing arm) for moderate F, moving
  toward the potential maximum (Θ → −π) as corotation is approached and the shock weakens (GC §3.1.2; SMR §IVb).
- **Outside corotation:** not computed by SMR; solutions follow from u_η → −u_η, u_ξ → −u_ξ, η → −η (SMR fn. 4).
- **Near corotation, and for a perpendicular Mach number under 1:** the base-subsonic band is bounded by
  R sin i (Ω−Ω_p) = ± a (12.5–15.3 kpc in SMR's model). At small F the flow is entirely subsonic and smooth; the
  cusp forms at the potential *maximum*; the peak density "is not reached immediately after the shock, but is
  attained subsequently by a smooth compression occurring at subsonic speeds", the zone "fairly broad … not unlike
  that produced by an extrapolation of the linear theory" (SMR §IVb, row C). These solutions "are not easy to
  find". **Exactly at Ω_p = Ω no source read gives a nonlinear solution**: S7c is singular at u_η = 0. What the
  sources give is the linear limit — *(reconstructed by the reader from S7a, S9, S16a)* σ₁/σ₀ ≈ f cos η/(1 − ν² + x),
  which at ν = 0 is f cos η/(1 + x): finite, symmetric, centred on the potential minimum, with no flow across the
  arm. KK14: the peak "is smaller near the respective CR"; "conventional wisdom is that spiral shocks are absent
  in the CR region where M⊥ = 0".
- **Lindblad resonances:** the linear response diverges at ν² − x = 1.

### A5. A potential that is a sum of several modes

**No source read integrates the 1-D steady equations with a multi-mode or non-sinusoidal forcing**: all impose
one cosine; in SMR the second harmonic arises only in the response. Every formulation is written in a frame
rotating at one Ω_p in which the potential is time-independent, so **a steady solution needs a common pattern
speed for all modes** (the reader's inference; no source states it as a theorem). *What carries over
(reconstructed, in no source):* K10–K11 hold for any periodic Φ_s(x) with −dΦ_s/dx in place of the sine; the
fundamental period is that of the lowest common harmonic; the sonic-point condition becomes 2Ωv₀ = dΦ_s/dx. *What
does not:* the even/odd shortcut for smooth solutions, and the guarantee of a single shock — each extra forcing
harmonic adds its own resonances.

### A6. Conflicts between sources

1. R69 finds a finite lower limit of the shock (σ(2)/σ(1) = 1.4 at F ≈ 1.04 %); SMR a continuous family whose
   critical solution is a cusp of zero strength. Different parameters; R69 keeps the curvature terms.
2. GC's Appendix labels the forward branch "subsonic"; SMR, KKK and GC's own period say the reverse: a slip.
3. The shock's offset: −30°, −72°, −26°, and from about 0 to −π with radius (GC); KKK's row A turns positive at
   ℱ = 20 %. Not contradictory once F and the Mach number are stated, but "upstream of the minimum" is not general.
4. "No shock compression at corotation" (GC §5) against weak shocks crossing corotation in KK14's 2-D runs.

### A7. What could not be read

R69 pp. 132–133 and 136–144; Shu et al. 1972; Woodward 1975; Wada & Koda 2004; Dobbs & Bonnell 2006; Kim &
Ostriker 2006; Lee & Shu 2012 and Chakrabarti et al. 2003 (through a summariser only: kept out of the table);
Binney & Tremaine and Shu's textbook (not online); GC's and KKK's figure curves.

### A8. The reader's recommendation

**Integrate** SMR's two-equation system (equivalently KKK's K10–K11) in GC's regularised variables, started at the
sonic point, forward on the supersonic branch and backward on the subsonic; find the shock where the post-shock
branch meets the subsonic branch at equal v; close the period by a bisection on the sonic point's phase alone —
one fixed-step integration per trial and a fixed number of bisection steps. Below the cusp, the linear closed
form or SMR's symmetric shooting. **Check first against row A (KKK Table 1)**, the only tabulated, pure
hydrodynamic, dimensionless case; then row B, row C (base-subsonic: the regime the gate asks about) and row G.
**Open for the gate:** the multi-mode extension has no published check (its only anchors are the single-mode
limit and the per-mode linear response); exact corotation needs a ruling (the sources supply only the linear
limit there); the base-subsonic search window can be narrower than π/1000.

---

## Part C — the same question read a second time: equations, sonic point, jump, a profile to check against, and the corotating case (a third reader)

Reading done only by web search and web fetch; nothing local was opened, no code was run. The fetch tool returns
a small model's transcription of an HTML page and refuses long quotes, so "as printed" below means "as transcribed
from ar5iv / arxiv.org HTML", read at least twice where load-bearing (stated per item). **Roberts 1969 and Shu,
Milione & Roberts 1973 were NOT read** (scans; see C5): every equation below comes from later restatements, and the
original symbol names w_perp0, w_par0 were not seen on any fetched page.

Source keys (the URL each tag refers to):

- S1 = Kim, Kim & Kim 2014, ApJ 789, 68, arXiv:1405.5874 — https://ar5iv.labs.arxiv.org/html/1405.5874 and
  https://arxiv.org/html/1405.5874 (title and authors confirmed on both)
- S2 = Gittins & Clarke 2004, MNRAS 349, 909, arXiv:astro-ph/0312562 — https://ar5iv.labs.arxiv.org/html/astro-ph/0312562
  (title/authors/journal confirmed at https://arxiv.org/abs/astro-ph/0312562)
- S3 = Lee & Shu 2012, ApJ 756, 45, arXiv:1207.0875 — https://ar5iv.labs.arxiv.org/html/1207.0875
- S4 = Lee 2014, arXiv:1407.5215 — https://arxiv.org/html/1407.5215
- S5 = Kim & Ostriker 2002, ApJ 570, 132, arXiv:astro-ph/0111398 — https://ar5iv.labs.arxiv.org/html/astro-ph/0111398
- S6 = Sormani, Sobacchi, Shore, Tress & Klessen 2017, arXiv:1707.00301 — https://ar5iv.labs.arxiv.org/html/1707.00301
  and https://arxiv.org/html/1707.00301
- S7 = Dobbs & Baba 2014, PASA 31, 35, arXiv:1407.5062 — https://ned.ipac.caltech.edu/level5/March15/Dobbs/Dobbs3.html
- S8 = Wada, Baba & Saitoh 2011, ApJ 735, 1, arXiv:1104.1287 — https://arxiv.org/html/1104.1287
- S9 = Baba, Morokuma-Matsui & Egusa 2015, PASJ 67, L4, arXiv:1505.02881 — https://ar5iv.labs.arxiv.org/html/1505.02881
- S10 = Baba et al. 2016, MNRAS 460, 2472, arXiv:1604.06879 — https://ar5iv.labs.arxiv.org/html/1604.06879
- S11 = Dobbs & Bonnell 2008, MNRAS 385, 1893, arXiv:0801.3562 — https://arxiv.org/html/0801.3562
- S12 = Bovy, "Dynamics and Astrophysics of Galaxies", ch. 20.1 —
  https://galaxiesbook.org/chapters/IV-04.-Internal-Evolution-in-Galaxies_1-The-(in)stability-of-disks.html
- S13 = Kim & Kim 2014, MNRAS 440, 208, arXiv:1402.2291 — https://ar5iv.labs.arxiv.org/html/1402.2291
- S14 = Wada & Koda 2004, arXiv:astro-ph/0308203 — https://arxiv.org/html/astro-ph/0308203
- S15 = Yanez, Norman, Martos & Hayes 2008, arXiv:0710.1331 — https://ar5iv.labs.arxiv.org/html/0710.1331
- S16 = Martinez-Garcia, Gonzalez-Lopezlira & Gomez 2009, arXiv:0911.0161 — https://ar5iv.labs.arxiv.org/html/0911.0161

### C1 Summary tables

#### C1.1 The equations (three restatements; all isothermal unless said, no self-gravity, no field, tightly wound)

| Item | S1 (local Cartesian x normal, y along arm) | S2 (spiral coords eta, xi; dimensionless) | S3 (eta, xi; dimensionless) |
|---|---|---|---|
| Coordinates | x perp. to arm, y parallel; frame at R rotating at Omega_p; L = 2 pi R sin i / m | `d eta = -k dR + m d theta`; `d xi = -m dR/R - k R d theta`; k = -m/(R tan i) | `eta = m phi - Phi(varpi)` (29); `d eta = m(cot i d varpi/varpi + d phi)` (30); `d xi = m(d varpi/varpi + cot i d phi)` (31) |
| Unperturbed flow | `u_c = R(Omega - Omega_p) sin i`; `v_c = R(Omega - Omega_p) - q Omega x` | `u_eta0 = R0(Omega - Omega_P) sin i`; `u_xi0 = R0(Omega - Omega_P) cos i` | `nu = -u_eta0/(2UV)^(1/2) = m(Omega_p - Omega)/kappa` (42) |
| Potential | `Phi_s = Phi_0 cos(2 pi x/L)`; minimum at x = L/2 | `V_S = A cos(chi)`, chi = Phi(R) - m(theta - Omega_P t); eta = -chi + pi so eta = 0 is the minimum | `V_* = -A(varpi) cos[m phi - Phi(varpi)]` (7); minimum at eta = 0 |
| Forcing F | `F = (m/sin i) Phi_0/(R^2 Omega^2)` | `F = m A/(v^2 sin i)`, v = circular speed | `F = abs(k_varpi) A/(varpi Omega^2)` (8); `f = (Omega/kappa)^2 (m F/sin i)` (9) |
| Continuity | `Sigma_0 u_T0 = Sigma_c u_c` (8) | (implied; sigma follows from u) | `(1 + sigma)(-nu + u) = -nu` (53) |
| Normal eq. | `(u_T0 - c_s^2/u_T0) du_T0/dx = 2 Omega v_0 + R Omega^2 F sin(2 pi x/L)` (11) | `du/d eta = (u - nu)(v - f sin eta)/((u - nu)^2 - x)` | `du/d eta = (-nu + u)(v - alpha d phi/d eta - f sin eta)/((-nu + u)^2 - xhat)` (51) |
| Parallel eq. | `u_T0 dv_0/dx = -(kappa^2/(2 Omega)) u_0` (10), u_0 = u_T0 - u_c | `dv/d eta = u/(nu - u)` | `dv/d eta = u/(nu - u)` (52) |
| Scalings | a = c_s/(R Omega); kappa^2 = (4 - 2q) Omega^2 | `u = u_eta1/sqrt(2UV)`, `v = u_xi1/V`, `f = F R0 Omega/(2V)`, `nu = -u_eta0/sqrt(2UV)`, `x = a^2/(2UV)` | same u, v; `U = varpi Omega sin i/m`, `V = varpi kappa^2 sin i/(2 Omega m)` (36-37); `x_t0 = v_t0^2/(2UV)` (43) |

Tags: column S1 [verified: Kim, Kim & Kim 2014, arXiv:1405.5874, Sec. 2-3, eqs. 8-11, S1; eq. 11 and the F
definition read four times across two hosts, identical]. Column S2 [verified: Gittins & Clarke 2004,
astro-ph/0312562, Sec. 2 and App. A, S2; ODEs, f, nu, x read three times on one host, identical]. Column S3
[verified: Lee & Shu 2012, arXiv:1207.0875, eqs. 7-9, 29-31, 36-37, 42-43, 51-53, S3; eqs. 51-53 read twice,
identical]. The unmagnetised, non-self-gravitating, isothermal limit of S3 is alpha = 0, x_A0 = 0, xhat = x
(S3 itself is logatropic: xhat = x_t0/(1+sigma) + x_A0 (1+sigma); see C4).

The three are the same system [the reader's derivation, by substituting d/dx = (m/(R sin i)) d/d eta and
eta = 2 pi x/L - pi into S1's eqs. 10-11; it reproduces S2's f = F R Omega/(2V) and S3's eq. 9 exactly]. In one
notation, with `w = u - nu` (total normal speed in units of sqrt(2UV) = kappa R sin i/m), `s = Sigma/Sigma_0`:

    (w - x/w) dw/d eta = v - f sin eta        dv/d eta = -1 - nu/w = s - 1        s w = -nu
    nu = m(Omega_p - Omega)/kappa    x = (m a/(kappa R sin i))^2 = (k a/kappa)^2    f = (Omega/kappa)^2 m F/sin i

Period 2 pi in eta; eta = 0 the potential minimum; inside corotation nu < 0 and gas moves towards +eta. The second
equation is the statement that potential vorticity is uniform (S1 prints `xi_0 = kappa^2/(2 Omega Sigma_c)`, "constant
everywhere") [verified: S1, Sec. 3; S5 eq. 10 prints the same relation as `q = 2 - (2 - q_0) Sigma/Sigma_0`].

Approximations as stated: local (abs(x), abs(y) << R), tightly wound (sin i << 1), isothermal, razor-thin, no
self-gravity, no field, steady in the pattern frame, variation only normal to the arm [verified: S1 Sec. 2; S3
Sec. 2 ("first-order asymptotic expansion in sin i")]. Periodicity: "u_0 and v_0 are periodic at x/L = 0 and 1"
(S1); period 2 pi in eta (S2, S3).

**F as a fraction of what.** S5: "amplitude of the perturbed radial force 2 pi abs(Phi_0)/L_x as a fraction of the
mean axisymmetric gravitational force", `F = (2/sin i) abs(Phi_0)/(Omega_0^2 R_0^2)` (m = 2) [verified: Kim &
Ostriker 2002, astro-ph/0111398, Sec. 2, S5]. S2: "ratio of the amplitude of the perturbation force to the
axisymmetric force". S3: fraction "of the axisymmetric gravitational acceleration", typical 5 to 10 %.

**F from a stellar surface-density contrast.** No source read states it. S3 says A(varpi) is "given ... from stellar
density-wave theory". The WKB Poisson relation `Phi_1 = -2 pi G Sigma_1/abs(k)` is printed [verified: Bovy, S12,
eq. 20.15, read twice]. Composition [the reader's derivation]: `F = abs(k) A/(R Omega^2) = 2 pi G Sigma_*1/(R Omega^2)`,
razor-thin, one Fourier mode; a finite-thickness reduction is not in any source read.

#### C1.2 Sonic point and jump

| Item | Statement | Tag |
|---|---|---|
| Sonic condition | `u_T0 = c_s` (S1); `u = nu + sqrt(x)` i.e. u_eta = a (S2); `(-nu + u)^2 - xhat = 0` (S3 eq. 56) | verified S1, S2, S3 |
| Singularity | the denominator of the normal equation vanishes; a smooth passage needs the numerator to vanish too | verified S2, S3 ("both the numerator and denominator to be zero") |
| Regularity | `v(eta_SP) = f sin eta_SP` (S2); `beta_0 = -(F/2) sin(2 pi x_sp/L)` (S1 eq. 15), the same thing | verified S2, S1 (twice) |
| Slope at the sonic point | S1: `u_T0/(R Omega) = a + alpha_1 d eta + ...`, `v_0/(R Omega) = beta_0 + beta_1 d eta + ...`, `d eta = (x - x_sp)/R`; `alpha_1 = [beta_1 + (F/sin i) cos(2 pi x_sp/L)]^(1/2)` (16); `beta_1 = (u_c - c_s)/c_s` (17) | verified S1, read three times, two hosts |
| Jump | `Delta(u_T0 Sigma_0) = 0` (20a); `Delta((c_s^2 + u_T0^2) Sigma_0) = 0` (20b); `Delta(v_0) = 0` (20c); hence `u_T0(s+) u_T0(s-) = c_s^2` (21); `mu = Sigma(s+)/Sigma(s-)` (22) | verified S1 |
| Jump (S2) | `u_sup * u_shock = a^2` | verified S2 |
| No-shock regime | "In the limit of small F, the solutions reach the first-order response, which is sinusoidal in u and v" | verified S2 |
| Shock threshold | Shu et al. 1973: "even a very weak spiral forcing (F > 0.9%) for their model parameters results in shocks" | verified S1 (S1's report of SMR73; SMR73 itself not read) |
| Shock threshold | "For c_s = 8 km/s, the forcing required to produce a shock is around a few %" | verified S7, Sec. 3.5 |
| Shock threshold, exact | `Phi_c = 0.07297` for L = 1, c_s = 0.7 in units F_y = Omega = 1 (base flow u_0x = 1/2, subsonic) | verified S6, Sec. 3.2.1, two hosts |

S1's eqs. 16-17 are printed without m, q or kappa. They are the m = 2, q = 1 case of [the reader's derivation]
`alpha_1^2 = beta_1 + (m F/(2 sin i)) cos(2 pi x_sp/L)`, `beta_1 = (kappa^2/(2 Omega^2))(u_c - c_s)/c_s`; in the
unified variables `(dw/d eta)^2 = (1/2)(-1 - nu/sqrt(x) - f cos eta_sp)` at w = sqrt(x). The positive root is the
subsonic-to-supersonic passage downstream of the shock.

#### C1.3 Published profiles with parameters

| Source | Parameters | Printed numbers | Use |
|---|---|---|---|
| S1 Table 1 | q = 1, m = 2, sin i = 0.1, Omega_p/Omega = 0.5, c_s/(R Omega) = 0.027, potential minimum at x/L = 0.5 | F = 0.03: x_sp/L 0.458, x_sh/L 0.402, mu 5.67; F = 0.05: 0.507, 0.431, 11.6; F = 0.10: 0.615, 0.495, 34.5; F = 0.20: 0.699, 0.560, 97.3 | exact check (table) |
| S1 text | same | `Sigma_0(x_sp)/Sigma_c = u_c/c_s = 1.86` | exact check (text) |
| S6 | L = 1, c_s = 0.7, F_y = Omega = 1, `Phi = Phi_0 cos(2 pi x/L)` | Phi_c = 0.07297: smooth solution first touches the sound speed; shock first appears at x = 0 (the potential maximum) | exact check of the no-shock threshold (text) |
| S5 text | F = 3 %, c_s = 7 km/s, Omega_p = Omega_0/2, sin i = 0.1, R_0 = 10 kpc, Omega_0 = 26 km/s/kpc, L_x = 3.1 kpc; self-gravitating AND magnetised | Q_0 = 2.0, beta_0 = 10: Sigma_max/Sigma_0 ~ 2.5, shock at x/L_x ~ -0.02, thickness ~ 0.03; Q_0 = 1.5, beta_0 = 1: ~ 3.8, ~ -0.05, ~ 0.02 | band only |
| S4 | varpi = 2 kpc, i = 21 deg, Omega_p = 40, Omega = 127, kappa = 186 km/s/kpc, v_t0 = 10 km/s; nu = -0.933, f = 0.2, x_t0 = 0.022, x_A0 = 0.02, F ~ 8 %; logatropic, magnetised | Sigma_peak/Sigma_0 ~ 13; arm width (eta_mp - eta_sh) ~ 10 % or less of 2.25 kpc | band only |
| S3 | varpi = 5 kpc (M81), Omega/kappa = 0.666, tan i = 0.249, F = 11.5 %, alpha = 0.35, nu = -0.666, x_t0 = 0.1, x_A0 = 0.1; logatropic, magnetised, self-gravitating | arm FWHM ~ 12 % of the arm spacing, ~ 480 pc | band only |
| S2 standard model | m = 2, sin i = 0.1, Omega_P = 13 km/s/kpc, a = 8 km/s, F_0 = 0.05 at R_0 = 8.5 kpc, v_0 = 220 km/s | none printed; offset Theta = eta_shock runs from ~0 near 5 kpc towards -pi near 11 kpc (figure read-off) | qualitative |

Tags: S1 [verified: Kim, Kim & Kim 2014, arXiv:1405.5874, Table 1 "Properties of Equilibrium Spiral Shocks" and
Sec. 3 text, S1; covers one ring, one pattern speed, four forcings, unmagnetised, non-self-gravitating; the table
was read four times on two hosts with identical digits]. Quantities: x_sp = sonic point, x_sh = shock front,
mu = post-shock over pre-shock surface density; x runs 0 to L in the flow direction (u_c > 0). S6 [verified:
Sormani et al. 2017, arXiv:1707.00301, Sec. 3.2.1, S6; one parameter set]. S5 [verified: Kim & Ostriker 2002,
Sec. 3, S5; two models, values printed with "approximately"; x from -L_x/2 to L_x/2, minimum at x = 0]. S4
[verified: Lee 2014, arXiv:1407.5215, Table 2 and text near Fig. 6, S4; single read]. S3 [verified: Lee & Shu
2012, Table 2 and text near Fig. 4, S3]. S2 [verified: Gittins & Clarke 2004, Table of the standard model and
Fig. 12 description, S2; parameters partly confirmed by S16, which reuses m = 2, sin i = 0.1, Omega_p = 13,
a = 8, F = 0.05].

S1's benchmark in the unified variables [the reader's arithmetic from the verified table; not printed anywhere]:
nu = -1/sqrt(2) = -0.70711; f = 10 F; x = 200 a^2 = 0.1458 for a = 0.027, or 0.1450 for a = 7/260 (see C4, item 8).

| F | f | eta_sp (rad) | eta_sh (rad) | mu | pre-shock Mach sqrt(mu) | Sigma(s-)/Sigma_c | Sigma(s+)/Sigma_c | (x_sp - x_sh)/L |
|---|---|---|---|---|---|---|---|---|
| 0.03 | 0.3 | -0.264 | -0.616 | 5.67 | 2.38 | 0.78 | 4.4 | 0.056 |
| 0.05 | 0.5 | +0.044 | -0.434 | 11.6 | 3.41 | 0.55 | 6.3 | 0.076 |
| 0.10 | 1.0 | +0.723 | -0.031 | 34.5 | 5.87 | 0.32 | 10.9 | 0.120 |
| 0.20 | 2.0 | +1.250 | +0.377 | 97.3 | 9.86 | 0.19 | 18.3 | 0.139 |

Only columns F and mu are printed; eta = 2 pi (x/L - 0.5); the densities use Sigma u_T0 = Sigma_c u_c with
u_c/c_s = 1.857 and the isothermal jump (mu = Mach^2); normal speeds before/after are c_s sqrt(mu) and c_s/sqrt(mu).
A consistency check the reader made by hand: alpha_1^2 from eq. 16 is positive at every tabulated x_sp
(0.57, 0.36, 0.11, 0.23), as a transonic passage requires.

#### C1.4 The corotating case (Omega_p = Omega on the ring)

| Source | What is derived or measured | Tag |
|---|---|---|
| S7 Sec. 3.7 | "gas effectively falls in to the minimum of the potential, from both sides of the spiral arm"; "a systematic offset is not expected"; "the gaseous arm remains until the stellar arm disperses"; gas "can still clearly undergo shocks as it falls into the minimum" | verified S7 (review; no equation, no number) |
| S8 | no galactic shock; gas converges to "near the bottom of the stellar spirals"; relative speed ~15 km/s or less; Mach ~2 against ~10-40 in the rigid-pattern run; arm density changes over ~100 Myr | verified S8 (N-body/SPH, 10 pc softening, multiphase, self-gravity, feedback; single read) |
| S9 | dynamic arms: arm-gas offset "no clear radial dependence"; steady arms: a systematic trend with radius | verified S9 (offset = gas azimuth relative to the potential minimum) |
| S10 | dynamic arm: "V_R ~ 0" in the arm with tangential streaming "typically ~10 km/s"; steady arm: radial streaming and a sudden change at the shock | verified S10 (ASURA-2 SPH, 10 pc softening, multiphase) |
| S11 | active N-body potential: gas "accumulate[s] in the potential minima"; densest gas coincides with the minimum; no pattern speed defined | verified S11 (SPH, isothermal 100 K and 1e4 K phases, no self-gravity) |
| S2 | the band round corotation where u_eta0 < a ("base-subsonic"): "a broad density peak at eta = 0", shock weak or absent | verified S2 |
| S12 | linear WKB fluid response: `u_R1 = -omega k Phi_1/(kappa^2 - omega^2 + c_s^2 k^2)` (20.35), `Sigma_1 = (k Sigma_0/omega) u_R1` (20.17), general-m dispersion relation with (omega - m Omega) (20.45) | verified S12 (20.35 read once, 20.17 and 20.45 once; printed for m = 0) |
| S5 eq. 10 | potential-vorticity conservation fixes the local shear: `q = 2 - (2 - q_0) Sigma/Sigma_0` | verified S5, read twice |

No source read gives a steady profile or a density contrast for the corotating case, and none addresses
uniqueness. The simulation papers reject steadiness outright (S8, S11).

### C2 Per-source notes

**S1, Kim, Kim & Kim 2014** (covers: the whole of items 1-4 for one ring; nothing on corotation). The cleanest
restatement and the only tabulated solution found. Momentum equation as printed:
`dv/dt + v_T . grad v = -c_s^2 grad ln Sigma + q Omega u yhat - 2 Omega x v - grad Phi_s`, v = (u, v) the induced
velocity, v_T = v + v_c. Steady equations 8-11 as in C1.1; eq. 9 before combination:
`u_T0 du_0/dx = -(c_s^2/Sigma_0) dSigma_0/dx + 2 Omega v_0 - dPhi_s/dx`. Method, quoted: "We first choose x_sp
arbitrarily for given F and then integrate equations (10) and (11) starting from x_sp in both forward and backward
directions ... We determine x_sh from equation (20c), and check the jump condition for the perpendicular velocity
... If equation (21) is not satisfied within tolerance (typically ~1e-5), we ... repeat the calculation by changing
x_sp iteratively". Parameters: "q = 1, m = 2, sin i = 0.1, Omega_p/Omega = 0.5, F = 3-10%, c_s/(R Omega) = 0.027
(c_s/7 km/s)(Omega/26 km/s/kpc)^-1 (R/10 kpc)^-1". Fig. 1 shows profiles for F = 3, 5, 10 % with the sonic point
marked; the sonic point lies downstream of the shock ("The gas should be accelerated downstream and pass through
the sonic point"). Further coefficients as transcribed once, not cross-checked, not to be coded from this note:
`alpha_2 = alpha_1^2/(6a) - u_c/(R Omega)/(6 a^2) + 2 beta_0/(3 alpha_1 sin^2 i)`, `beta_2 = -(1 + beta_1) alpha_1/(2a)`.

**S2, Gittins & Clarke 2004** (covers: items 1-3 in the Roberts/SMR73 spiral coordinates, a radial sequence of
solutions, the base-subsonic band; no printed solution numbers). Dimensional equations as transcribed:
`d u_eta1/d eta = U (u_eta0 + u_eta1)[2 u_xi1 - F R_0 Omega sin eta]/[(u_eta0 + u_eta1)^2 - a^2]`,
`d u_xi1/d eta = -V u_eta1/(u_eta0 + u_eta1)`, `U = (sin i/m) R_0 Omega`, `V = (sin i/m) R_0 kappa^2/(2 Omega)`.
Appendix A removes the singularity with `u = nu + sqrt(x) + utilde`, `v = f sin eta + vtilde`, `wtilde = utilde^2`:
`d wtilde/d eta = 2 (sqrt(x) +/- sqrt(wtilde)) vtilde/(2 sqrt(x) +/- sqrt(wtilde))`,
`d vtilde/d eta = -1 - f cos eta - nu/(sqrt(x) +/- sqrt(wtilde))`, the sign choosing the supersonic or subsonic
branch (single read; consistent with the reader's slope formula in C1.2). Algorithm: guess eta_SP; integrate forward
along the subsonic branch and backward along the supersonic branch; map the supersonic branch through
`u_sup u_shock = a^2`; the shock is where that mapped branch crosses the subsonic one in the (v, u) plane; adjust
eta_SP until the solution is 2 pi periodic. Definitions: base-supersonic is `u_eta0 > a`, base-subsonic `u_eta0 < a`,
the latter "either side of the corotation radius". Shock formation: "If the strength F of the perturbation is
gradually increased, starting from an entirely subsonic solution, then at some point ... u_eta will pass the sound
speed a. Any solution must now contain a sonic point". Several shocks: "Many solutions show secondary peaks in the
density ... especially near the ultraharmonic resonances ... If a secondary peak crosses the sonic line, a second
shock will occur"; no solutions were found between 11 and 12.5 kpc in the standard model, and "solutions are
difficult or impossible to find for F >~ 0.1 and sin i >~ 0.2". Offset `Theta = m(theta_shock - theta_min) = eta_shock`:
near the minimum at small radii, moving upstream towards the potential maximum with radius. Rotation curve
`v(R) = v_max sqrt[F_b eps_b R exp(-eps_b R) + 1 - exp(-eps_d R)]`, `A(R) = A_0 R exp(-eps_s R)`, 1/eps_d = 1.5 kpc,
1/eps_s = 10 kpc, F_b = 0.

**S3, Lee & Shu 2012; S4, Lee 2014** (cover: the equations in Shu's own later notation with self-gravity and field
added; one equilibrium each; logatropic, so not a digit check for an isothermal solver). Pressure
`Pi = Sigma_0 v_t0^2 ln(Sigma/Sigma_0)`, signal speed `v_t^2 = v_t0^2 (Sigma_0/Sigma)`. Sonic-point slope, eq. 58, as
transcribed once: `du/d eta = [-u_mp/y_mp - alpha phi'' - f cos eta_mp]^(1/2)/[2 + x_t0/(nu y_mp) - x_A0 nu/y_mp^3]^(1/2)`.
Integration starts at the magnetosonic point by Taylor expansion and proceeds both ways; self-gravity is added by
iteration with a relaxation parameter. "Solutions with multiple magnetosonic points and shocks are also possible,
but their study is beyond the scope of this paper"; "we deliberately stay away from corotation". S4's Table 2 is
internally consistent with the definitions [the reader's arithmetic: 2(40 - 127)/186 = -0.935 against nu = -0.933;
U = 45.5, V = 48.8 km/s give v_t0^2/(2UV) = 0.0225 against x_t0 = 0.022; f = 0.2 gives F = 7.7 %].

**S5, Kim & Ostriker 2002** (covers: local frame, F definition, PV relation, two approximate profiles with
self-gravity and field). Background `v_0 = [R_0(Omega_0 - Omega_p) - q_0 Omega_0 x](sin i xhat + cos i yhat)`;
`Phi_ext = Phi_0 cos(2 pi x/L_x)` with Phi_0 < 0. Profiles are found by time-dependent relaxation, raising F slowly
(about five orbits), not by shooting. PV: `xi = abs(curl v_T + 2 Omega_0)/Sigma`, giving eq. 10 and
`Q = Q_0 (Sigma/Sigma_0)^(-1/2)`; shear reverses where Sigma/Sigma_0 > 2 for q_0 = 1. Weak forcing: "the shock
disappears, leaving quite symmetric density configurations". Non-self-gravitating counterparts are drawn dashed in
Figs. 2a, 3a with no numbers printed. No steady 1D solution exists below Q_sp ~ 0.8, 0.5, 0.4 (no field, beta = 10,
beta = 1) [verified: abstract via search listing and S5].

**S6, Sormani et al. 2017** (covers: a no-shear toy of the same system; the threshold to four digits). Equations
`dv/dt + (v.grad)v = -grad P/rho - grad Phi - 2 Omega x v + F`, steady form in units F_y = Omega = 1:
`u_0y' = -2 + 1/u_0x` (13), `u_0x' = (2 u_0y - Phi')/(u_0x - c_s^2/u_0x)` (14); uniform solution u_0x = 1/2,
u_0y = 0; "If c_s > 1/2, the Phi_0 = 0 solution is subsonic". "For Phi_0 < Phi_c the solution does not contain a
shock"; above it "the solution must contain a shock", which first appears at x = 0, the maximum of Phi. A value
Phi_c ~ 0.0148 for c_s = 0.3 was returned by one fetch and reported absent by a second: unverified, not used.
Mapping to the unified variables [the reader's derivation]: kappa^2/(2 Omega) -> 2 Omega (kappa = 2 Omega),
u_c = 1/2, k = 2 pi/L, so nu = -pi/2 = -1.5708, x = (pi c_s)^2 = 4.836, f = pi^2 Phi_0, hence f_c = 0.7202; their
x = 0 is eta = +/- pi.

**S7, Dobbs & Baba 2014** (covers: review statements on items 2, 3, 5). Shock position: "For warm gas and moderate
forcing, a narrow shock is expected ahead of the minimum of the potential. If the gas is cold however, a very
narrow shock is expected after the minimum". Ultraharmonic: "Gas undergoes a secondary compression ... at the
ultraharmonic resonance (n = 2)", arms bifurcate for F >= 5 %. Resonance equation 38 as transcribed:
`kappa = m(Omega - Omega_p)/n` (see C4, item 9).

**S13, Kim & Kim 2014** (covers: global isothermal runs, c_s = 10 km/s, pitch 20 deg, F = 5, 10, 20 %). Shocks are
"weak" at corotation; quasi-steady shocks need `M_perp/sin p <~ 20 + 100 F`; the shock moves upstream as M_perp
rises; branches at the 4:1 resonance. Single read. **S14**: "If the spiral potential is too weak (e.g. amplitude
... less than a few % of the axisymmetric one), shocks do not appear". **S15**: reports SMR73's ultraharmonic
resonances as points where "the amplitude became infinite", with "a secondary compression"; its own runs show two
pairs of shocks near the first ultraharmonic resonance. **S16**: reuses S2's parameters, prints no solution numbers.

### C3 What a solver should integrate

**Recommendation.** Integrate the unified system of C1.1 in (w, v) with the three numbers (nu, x, f) per ring, by
S1's procedure: place the sonic point at a trial eta_sp, start with w = sqrt(x), v = f sin eta_sp and the positive
slope of C1.2, integrate downstream on the supersonic branch and upstream on the subsonic branch, wrap by 2 pi,
find the shock where v is continuous and require w(s-) w(s+) = x there; iterate eta_sp. S2's change of variables is
the alternative way through the singular point. It predicts: one shock per period, upstream of the minimum for weak
forcing and downstream for strong; S1's Table 1 to three figures for (nu, x) = (-0.7071, 0.1450 or 0.1458) and
f = 0.3, 0.5, 1, 2. Shown wrong by: any tabulated x_sp/L, x_sh/L off by more than 0.001 or mu off by more than the
last printed digit under both values of x; a density at the sonic point other than -nu/sqrt(x); potential vorticity
not uniform.

**Branch for no shock.** If w stays on one side of sqrt(x) over the whole period the solution is smooth and periodic
and is found as a boundary-value problem, not by shooting from a sonic point (there is none). The small-f limit is
[the reader's derivation from the verified ODEs] `sigma = f cos eta/(1 - nu^2 + x)`, `v = f sin eta/(1 - nu^2 + x)`,
`u = nu f cos eta/(1 - nu^2 + x)`, i.e. `Sigma_1/Sigma_0 = k^2 A cos eta/(kappa^2 - m^2 (Omega - Omega_p)^2 + k^2 a^2)`,
which agrees with the composition of S12's eqs. 20.17 and 20.35. It predicts: a density maximum at the minimum when
1 - nu^2 + x > 0, a response that diverges at nu^2 = 1 + x, and harmonic n of the forcing resonant at
n^2 (nu^2 - x) = 1 (the ultraharmonic condition in these variables, the reader's). Exact check: S6's threshold,
(nu, x) = (-1.5708, 4.836), the smooth solution first reaching w = sqrt(x) at f = 0.7202, at eta = +/- pi. Shown
wrong by: a threshold off in the fourth digit, or first contact elsewhere than the potential maximum.

**The ring at corotation.** At nu = 0 the mass flux is zero, w = 0, and the normal equation reduces to
`x d ln s/d eta = v - f sin eta` with v free: any s(eta) is steady if v balances it, so the steady state is not
unique [the reader's derivation; no source addresses it]. Two closures, named:
(a) uniform potential vorticity, the nu -> 0 limit of the Roberts family, `dv/d eta = s - 1`, giving
`x d^2 ln s/d eta^2 = s - 1 - f cos eta`, periodic, mean of s equal to 1 automatically; linear amplitude f/(1 + x),
i.e. `Sigma_1/Sigma_0 = k^2 A/(kappa^2 + k^2 a^2)`. It predicts a symmetric arm centred on the minimum, no offset,
V_R = 0 in the arm with tangential streaming of amplitude v, as S7, S9 and S10 describe.
(b) hydrostatic, v = 0: `s proportional to exp((f/x) cos eta)`, linear amplitude f/x = A/a^2; closure (a) is smaller
by x/(1 + x) in the linear regime (0.13 at x = 0.145). It would hold only if the Coriolis term were absent.
Shown wrong by: a measured arm-interarm contrast in the simulations of S8-S11 (none prints one for cold-free
isothermal gas), or a ruling that swing-amplified arms last too briefly (~100 Myr, S8) for either steady state.
A third alternative is to keep nu small but non-zero from the arm's own pattern speed and use the smooth branch.

**Several modes at once** [the reader's note; no source]: the sources force with one sinusoid. A sum over m keeps a
steady one-dimensional problem only if every mode shares the pattern speed and pitch, the forcing becoming a sum of
harmonics over the period of the lowest common pattern; otherwise the response is time-dependent.

### C4 Conflicts between sources

1. **F by sin i or tan i.** S1, S2, S5 use `m Phi_0/(R^2 Omega^2 sin i)`; S3 uses `abs(k_varpi) A/(varpi Omega^2)`
   with k_varpi = m cot i/varpi from its eq. 30, larger by 1/cos i (0.5 % at sin i = 0.1, 3 % at tan i = 0.249).
2. **Phase and sign of the potential.** Minimum at x = L/2 with Phi_0 > 0 (S1); at x = 0 with Phi_0 < 0 (S5); at
   eta = 0 via eta = -chi + pi (S2) or V = -A cos eta (S3); S6 puts the maximum at x = 0. Forcing sign follows.
3. **Equation of state.** Isothermal in S1, S2, S5, S6; logatropic in S3, S4. Their profiles are not comparable.
4. **Shock threshold.** 0.9 % (SMR73 as reported by S1, "for their model parameters"), "a few %" at c_s = 8 km/s
   (S7), "less than a few %" gives none (S14). Different parameters; no source gives the threshold as a formula.
5. **Shock position.** S7: ahead of the minimum for warm gas, after it for cold. S1: upstream for F <= 0.10,
   downstream at 0.20, at fixed sound speed. S2: upstream, increasingly so with radius. Same sign of trend, three
   different control variables; not reconciled by any source.
6. **Kim, Kim & Kim 2015 (arXiv:1506.07178), Table 1.** Same parameters as S1. ar5iv does not carry the table;
   arxiv.org/html returned three mutually inconsistent sets (mu = 2.18; 2.45 and 4.48; 2.45 and 6.28 for F = 5 and
   10 %), none equal to S1's 11.6 and 34.5, with a pre-shock density of exactly 1.000 that mass conservation
   forbids. Treated as mis-transcription; not used; a human should open that table.
7. **Transcription disagreements.** S2's U once as `sin i/(m R_0 Omega)` (dimensionally impossible) and once as
   `(sin i/m) R_0 Omega`; the latter matches S3. S3's eq. 43 once as x_t0 and once as x_t0^2; S4's numbers fix it
   as `x_t0 = v_t0^2/(2UV)`. One fetch of S3 said gas moves to decreasing eta; the equations and S2 ("moving
   outward in eta") say increasing eta inside corotation.
8. **S1's sound speed.** 0.027 gives u_c/c_s = 1.852; the printed 1.86 matches 7/260 = 0.02692 (1.857). A solver
   should try both.
9. **S7 eq. 38** reads `kappa = m(Omega - Omega_p)/n`; the ultraharmonic condition as usually written is
   `m(Omega - Omega_p) = kappa/n` [recall — NOT READ]; S7's sentence says "or vice versa". S2 places an
   ultraharmonic resonance at 13 kpc; for a flat 220 km/s curve and Omega_p = 13 the reader's arithmetic puts
   n = 2 at 10.9 kpc and n = 3 at 12.9 kpc, so S2's is probably n = 3, or its rotation curve differs.

### C5 What could not be read

- **Roberts 1969 (ApJ 158, 123)** and **Shu, Milione & Roberts 1973 (ApJ 183, 819)**: ADS abstract pages returned
  HTTP 405; the scan manifest was empty; the ADS PDFs timed out or came back as unparsed binary. Not read at all.
  The original symbols [recall — NOT READ]: w_perp0 = R(Omega - Omega_p) sin i, w_par0 = R(Omega - Omega_p) cos i,
  equations in eta with the same structure as S2's. SMR73's table of cases, its "effective acoustic speed"
  criterion for narrow or broad compression (seen only in a search-listing abstract) and its 0.9 % are unread.
- **Shu 2016, ARA&A 54, 667**: paywalled. **Woodward 1975; Lubow, Balbus & Cowie 1986; Balbus 1988; Binney &
  Tremaine sec. 6.2-6.3; Chakrabarti, Laughlin & Shu 2003; Baba et al. 2017; Kim & Ostriker 2006**: not attempted
  or not reachable; nothing from them is used.
- **Kim, Kim & Kim 2015, Table 1** (C4 item 6). **All arXiv PDFs**: the fetch tool cannot parse them; only HTML
  renderings were read. **Figures**: none seen; every figure statement is the paper's own text.
- A search listing attributed "3-4 %" for the shock threshold to SMR73; the page it came from was not identified
  (Elmegreen's arXiv:1101.3109 was fetched and does not contain it). Not used.
- Not found anywhere: a steady corotating gas profile; F in terms of a stellar surface-density contrast; a
  threshold formula in (nu, x, f); pre- and post-shock densities printed for an isothermal, unmagnetised solution
  (C1.3's are derived from mu).

---

## Part D — S87 (BUILD_V M1): how fast a young population's arm contrast fades (debt #81), and a dynamic arm's gas width (debt #144), re-read here

**The lead's note (2026-11-03).** No web access this session. Debts #81 and #144 each named a reading for S87; this
is a re-reading of Parts A-C above and of READING_CLUSTERING.md and READING_GAS_PATTERN.md. Nothing was fetched; the
arithmetic is the lead's `[inferred]`.

**D1. #81 — the age at which a population's arm-interarm contrast has decayed to the old disc's.** The entry's kill
condition, read from observation. What the readers hold, closest first:
- *Simulations, the young stars on the arm:* clusters younger than ~30 Myr sit on the stellar arms "without a clear
  spatial offset" in a live disc (B22, Wada, Baba & Saitoh 2011); the arm's density changes on ~100 Myr (A4) and an
  arm lives ~120 Myr (A1, Grand, Kawata & Cropper 2012) — the 0.1 Gyr the cut is sourced to since S57 (#81's re-ruling).
  (Wada, Baba & Saitoh 2011 read at S95, reader R.)
- *Observations, ages across arms:* cluster age bins <10, 10-50 and 50-200 Myr against the arm in three LEGUS
  galaxies — an age gradient in NGC 1566, none in M51a or NGC 628 (B11, Shabani et al. 2018); colour (age) gradients
  across arms in 10 of 13 galaxies (B10, Martinez-Garcia et al. 2009); no propagation across the arm in M81's 20
  regions (B13). Each is a *place* by age (an offset or a gradient), not an arm-interarm *contrast* by age.
  (Shabani et al. 2018 and Martinez-Garcia et al. 2009, arXiv:0812.3647, read at S95, reader R.)
- *The nearest measured fading:* the young clusters' **clustering** decays with age — "more homogeneously distributed
  after ~40-60 Myr" (six LEGUS galaxies), a "randomization timescale" of 50-100 Myr and "consistent with a randomized
  distribution after 100 Myr" in M51 (Grasha et al. 2017, 2019; READING_CLUSTERING.md section 2; read at S95,
  reader R). That is the fade
  of a hierarchy of clumps the model draws on its own (`census_clustering`, #162's), not of the arm's contrast.
- **No reader prints the age at which a population's arm-interarm contrast has decayed to the old disc's**, so the
  0.1 Gyr cut stays a cut with two simulations' arm lifetime behind it; the observed fades the readers do hold
  (clustering at 40-100 Myr) bracket it and are not its statistic. The owner's reading: an arm-interarm contrast (or
  an azimuthal Fourier amplitude) per age bin of resolved young populations — LEGUS or PHANGS-HST cluster catalogues
  binned by age against an arm mask, the form Shabani et al. 2018's bins come closest to.

**D2. #144 — a dynamic (co-rotating) arm's gas ridge width over the arm spacing.** C1.4 above stands: the simulations
of co-rotating arms (S7 Dobbs & Baba 2014 section 3.7; S8 Wada et al. 2011; S10; S11) print that gas falls into the
minimum from both sides, at Mach ~2, and that the arm density changes over ~100 Myr — **no ridge width** (read at
S95, reader R: the infall from both sides is Dobbs & Baba's §3.7, Mach ~2 and ~100 Myr Wada et al. 2011's). The widths
the readers hold are a steady shock's (Kim & Ostriker 2002 W/L_x 0.05-0.16 [KO02's W: the full width at
(Σ_max + Σ_min)/2, half way between peak and trough, of a rigid-pattern shock's 1-D stationary solution, its peak over
the mean - not a FWHM, not over the median (S98, F-98B-1)]; Kim, Kim & Ostriker 2010's 3D arm at 10 %
of the arm-to-arm distance, both rigid patterns), one galaxy's measured gas arm (Egusa et al. 2017, M51 inner 0.17; read at S95, reader R),
a maser arm's 1 sigma (Reid et al. 2019) and PHANGS's ridge masks (Querejeta et al. 2024, 500-1000 pc top-hat; Reading
D of READING_GAS_PATTERN.md). None is a co-rotating arm's gas width, so #144's second closer is not met by anything in
the repository and its first is #141's (permanent at S86). The owner's reading: the gas surface-density profile
across an arm in a live-disc simulation with gas (Baba et al. 2015's dynamic models, Wada et al. 2011's Fig. 4 or 9),
as FWHM over the arm spacing.

## Part S96 — an arm's contrast by stellar age (debt #81) and a live disc's gas across an arm (debt #144) (2026-11-12, read at the reading session; reader A)

**The reader's note.** S96's reader A fetched the two sources below in this session (its note `s96_A.md` in the
session's scratchpad). `[verified: source, place]` marks what it quoted from a fetched page; `[inferred]` its own
inference. The register carries the gate's ruling on each entry (D265).

### S96.1 #81 — Peterken et al. 2019: one galaxy's arm contrast by age

- **Source.** Peterken et al. 2019, MNRAS (doi 10.1093/mnras/stz2204), arXiv:1908.05013 — the abstract page and the PDF
  (its text taken by `pdftotext -layout`). Found by a web search for arm contrast by stellar age.
- **Sample.** One galaxy: "MCG+07-28-064 (MaNGA plate-IFU 8332-12701)", z = 0.028, "a mass of 10^9.78 M_sun" (NSA), a
  grand design with a bar, chosen "as a example galaxy to test our population analysis techniques".
- **Method.** Starlight SSP fits per spaxel; time-slice images "smoothed to 0.3 dex in age"; spiral and disc masks from
  Galaxy Zoo:3D (≥ 40 % / < 20 % of users); Eq. 1, S(r,t) = (f_s − f_d)/f_d, its median over radius the contrast S(t).
- **What it prints:** "A clear trend with age is also apparent in the spiral arm contrast. In the oldest stars the arms
  are not detected, while at intermediate ages there appears to be about a 75% enhancement of stellar density in the
  arms, which rises in stars younger than 10^8 years toward the Hα contrast." And: the bar's young-star offset "is only
  seen in stars younger than 0.1 Gyr because they have not had time to mix around their orbits" `[verified: Peterken et
  al. 2019, text (PDF)]`.
- **What it says against the model** `[inferred]`: the one observed time-slice places the young excess over the stellar
  arm below 10⁸ yr — the model's 0.1 Gyr — at a 0.3 dex age resolution that cannot tell a step from a decay; no decay
  curve is printed. Separately (not #81's question; one galaxy): the *oldest* stars show no arm, where the model gives
  every star older than 0.1 Gyr the density contrast.
- **Not read.** Fig. 2 (the ages at which each regime begins, as numbers); a sample-wide time-slicing follow-up (the paper
  announces it as future work; not searched).

### S96.2 #144 — Baba et al. 2015: offsets, no width

- **Source.** Baba, Morokuma-Matsui & Egusa 2015, PASJ 67, L4, arXiv:1505.02881 (ar5iv; found by a web search for Baba
  2015's dynamic arms). Asked for any width or profile number, the fetch answered **"No."**: the paper measures the
  angular offset of dense gas from the stellar potential minimum (Sect. 3.1, Fig. 2: "the radial distributions of the
  offset angle of the dense gas relative to the spiral potential"; Sect. 3.2: offsets "show no clear radial dependence
  in dynamic spiral models"), not a width or a contrast `[verified: Baba et al. 2015, Sects. 3.1–3.2]`.
- **Wada, Baba & Saitoh 2011** (arXiv:1104.1287) was not re-fetched: Part D above (D2) records that it prints infall at
  Mach ~2 and no width.
- **Not searched.** Other live-disc simulations (e.g. Dobbs & Bonnell, Pettitt).

## Part S98 — a shock's profile with its definitions, a live disc's gas, how dark and how wide a real lane is, and the model's ridge across the arm (2026-11-12, BUILD_VI row 98; reader B and the measurer)

**The note.** S98's reader B fetched each source below in this session (ar5iv HTML through a summarising fetch, which
would not quote long sentences — numbers were asked for cell by cell; one PDF by `pdftotext -layout`); its note is
`s98_B.md` in the session's scratchpad. The measurer's first pass, item 2 (`s98_M.md`), read the model's gas ridge
across the arm. `[verified: source, place]` marks a quotation from a page fetched in S98; `[inferred]` the reader's own
arithmetic or reading; "by eye" a figure read off its image. The register (#144, #129) carries the gate's ruling
(D267). Nothing here moved a constant, a pin or a model byte.

### S98.1 #144 — Kim & Ostriker 2002: the setting, Table 1, and what its columns are

- **Source.** Kim & Ostriker, "Formation and Fragmentation of Gaseous Spurs in Spiral Galaxies", arXiv:astro-ph/0111398
  ("Accepted for publication in ApJ"; DOI 10.1086/339352; the ApJ 570, 132 volume and page NOT printed on the abs page,
  not checked) — ar5iv HTML, three fetches.
- **The setting**, Sect. II.2: "Omega_p = Omega_0/2 and pitch angle sin i = 0.1"; "cs = 7 km s-1"; "R0 = 10 kpc"; "Lx =
  pi R0 sin i = 3.1 kpc"; "Omega0 = 26 km s-1 kpc-1"; F (eq. 9) = (2/sin i)(|Φ_0|/Ω_0² R_0²), "the amplitude of the
  perturbed radial force" relative to the mean axisymmetric force; "In the absence of external potential perturbation,
  our model disks have uniform surface density Sigma_0" — the mean `[verified: KO02, Sect. II.2]`. A shearing box,
  isothermal, self-gravitating, magnetised or not; a **RIGID pattern** (Ω_p = Ω_0/2: the gas flows through the arm at
  R(Ω − Ω_p)) — the steady-shock case, not the co-rotating one.
- **What the columns are**, Sect. IV: "The peak surface density Sigma_max and local Qsp of the 1D, stationary solution
  are listed, respectively, in columns (5) and (6), while column (7) gives the arm width determined at
  Sigma=(Sigma_max+Sigma_min)/2." The table's note: "W is the arm width at Sigma = 1/2 (Sigma_max + Sigma_min)."
  `[verified: KO02, Sect. IV, Table 1 note]` So **W is the full width at the MID level between peak and trough (not at
  half the peak), of the 1-D stationary shock profile (before spurs), in units of Lx, the arm-to-arm distance**; column
  (5), Σ_max/Σ_0, is **peak over the MEAN**; Σ_min has no column.
- **Table 1**, "Parameters of Nonaxisymmetric Simulations" `[verified: KO02, Table 1, cell by cell, one read on one
  host; F printed as 1, 2, 3 = per cent by the text's "F=3%", the header's unit not seen]`:

| Model | β0 | Q0 | F | Σmax/Σ0 | Qsp | W/Lx | ly/Lx | ly/W | Ky,max |
|---|---|---|---|---|---|---|---|---|---|
| H1 | ∞ | 1.7 | 1 | 2.36 | 1.11 | 0.16 | 0.67 | 4.2 | 0.21 |
| H2 | ∞ | 2.1 | 2 | 3.91 | 1.06 | 0.06 | ... | ... | ... |
| H3 | ∞ | 2.3 | 3 | 6.49 | 0.90 | 0.05 | ... | ... | ... |
| MS1 | 10 | 1.6 | 1 | 2.77 | 0.96 | 0.11 | 0.67 | 6.1 | 0.16 |
| MS2 | 10 | 1.8 | 2 | 4.91 | 0.81 | 0.07 | 0.22 | 3.1 | 0.31 |
| MS3 | 10 | 2.0 | 3 | 5.59 | 0.85 | 0.06 | 0.25 | 4.2 | 0.27 |
| ME1 | 1 | 1.2 | 1 | 2.11 | 0.83 | 0.16 | 0.20 | 1.3 | 0.54 |
| ME2 | 1 | 1.4 | 2 | 2.45 | 0.89 | 0.16 | 0.22 | 1.4 | 0.49 |
| ME3 | 1 | 1.5 | 3 | 2.84 | 0.89 | 0.16 | 0.22 | 1.4 | 0.45 |
| ME4 | 1 | 1.6 | 3 | 2.72 | 0.97 | 0.16 | 0.25 | 1.6 | 0.45 |

- **Peak over trough**, Sect. IV.1 (a partial quote): H2 and H3 have "a realistic arm-interarm contrast in surface
  density of Sigma_max/Sigma_min=6.2 and 11.5"; Sect. IV.3: in ME1-ME4 "the maximum to minimum density ratios are
  smaller than 6" `[verified: KO02, Sects. IV.1, IV.3]`.
- **F-98B-1 (stale text / a definition; wording, not a wrong number; the reader: high).** Part D (D2) above lists KO02's
  "W/L_x 0.05-0.16" among the widths the readers hold (register #144's S87 paragraph names KO02's width among them,
  without the range), beside the model's "FWHM 0.37 of the arm spacing" and its crest over the ring's median. **The range is right; the statistics are unlike**: KO02's W is
  the width at the mid level between peak and trough (close to a FWHM about the trough for a peaked profile with a deep
  trough `[inferred]`), and its peak is over the mean, not the median. Any comparison must recompute the model's width
  at (max + min)/2 and its crest over the mean. Applied at S98: the definition added in brackets where D2 quotes the
  range, and in the register.
- Every KO02 row is a rigid-pattern (Ω_p = Ω/2) shock at R0 = 10 kpc, F = 1-3 %: ruleset (ii)'s source, never a
  co-rotating arm's. In parsecs, 0.05-0.16 Lx is 155-500 pc `[inferred: × 3.1 kpc]`.

### S98.2 #144 — Wada, Baba & Saitoh 2011: no number; one figure, by eye

- **Source.** Wada, Baba & Saitoh 2011, "Interplay between Stellar Spirals and the ISM in Galactic Disks",
  arXiv:1104.1287 — ar5iv HTML (three fetches) and Fig. 4's image (ar5iv's figure4.png, viewed directly by the reader);
  the journal not on the ar5iv page, not checked.
- **Printed.** No number for a gas arm / inter-arm contrast, peak over mean, compression ratio or arm width anywhere in
  the text (the fetch, asked, answered none). Gas velocity relative to the stellar arms "should be ~15 km s-1 or
  smaller"; median Mach ~2 in the live model against "M ~10-40" in the rigid one (Sect. III.2); "there are four arms at
  R=8.6 kpc" (t = 1.441 Gyr); ASURA N-body/SPH, 10 pc softening, a multiphase ISM; stellar scale length 4.3 kpc, gas
  8.6 kpc (Table 1); R_CR = 14 kpc. On Fig. 4: "Total gas density, on the other hand, is more spiky."; "Each peak
  corresponds to a high density clouds or internal substructures of them."; "It is clear that high density peaks of
  the gas tend to be associated with stellar arms." The gas structure "is not steady" `[verified: WBS11, text]`.
- **"Density contrast" is NOT DEFINED in the paper** (asked: no formula, no surface against volume, no radial bin).
  Fig. 4's caption: "Azimuth distributions of stellar (red) and total gas (blue) density contrasts at R=4.3, 8.6 and
  12.9 kpc at t=1.441 Gyr."
- **Fig. 4, BY EYE** (the reader's read-off of the image, not printed; the y axis labelled "Density Contrast", −1 to
  about 2.8, **the gas curve clipped at the top in every panel**): at R = 8.6 kpc the stellar curve has broad bumps
  peaking about +0.7 to +1.4 near 65, 170, 255-265 and 325° (four arms, ~90° apart); the gas is a forest of narrow
  spikes, each about 2-5° wide (about 0.3-0.75 kpc of arc at 8.6 kpc), many reaching the clip (> 2.8), troughs about
  −0.5 to −0.9; the spikes cluster within about 10-20° of each stellar bump (0.11-0.22 of the 90° arm spacing along
  the ring), but spikes also stand between arms (near 10-30 and 120-130°). If "contrast" is ρ/⟨ρ⟩ − 1 `[inferred —
  undefined in the paper]`, the gas peaks exceed 3.8 × the azimuthal mean and the troughs are 0.1-0.5 ×. No single gas
  ridge with a width is drawn: the arm's gas is several clouds, not a profile.
- **Verdict for #144.** No profile printed; the only usable thing is a figure read by eye, of one snapshot, with an
  undefined ordinate and a clipped curve — not a source for a number under rule D1 `[inferred]`.

### S98.3 #144 — Dobbs & Baba 2014 section 3.7: qualitative

- **Source.** Dobbs & Baba 2014, "Dawes Review 4: Spiral Structures in Disc Galaxies", PASA, arXiv:1407.5062 — ar5iv
  HTML, characters 0-200 000 (200 000 to the end, the references area, NOT read).
- **Sect. 3.7, "Gas flow in dynamic spiral arms"**: "Thus the gas, stars and spiral arms will have the same angular
  velocities and there is no gas flow through the arms."; "gas effectively falls in to the minimum of the potential,
  from both sides of the spiral arm."; "For dynamic arms, a systematic offset is not expected between the density peak
  of the gas, and the stellar minimum."; "Gas can still clearly undergo shocks as it falls into the minimum of the
  potential, particularly if it has cooled."; "the gaseous arm remains until the stellar arm disperses"; "spurs are not
  typically seen in simulations" `[verified: DB14, Sect. 3.7]`. **No gas density, contrast or arm width for dynamic arms
  is printed in 3.7** (asked twice; the only numbers are cloud masses, "a few 10^5 Msun compared to a few 10^6 Msun",
  arms against no arms).
- The density-wave against dynamic comparison is qualitative only (Sect. 3.5, Roberts 1969: "for warm gas and moderate
  forcing, a narrow shock is expected ahead of the minimum of the potential"; Sect. 3.5.2 "Typically the gas density
  peaks after, or coincident with the minimum of the potential"; Sect. 3.6, tidal arms, "the gas will flow through the
  arms and experience a spiral shock"). For the steady shock DB14 reports Shu et al. 1972 `[secondary: as the review
  reports it; not opened]`: a steady two-phase shock with "density enhancements (of around 10 and 40)" for the two
  phases and "a width of the shocked region of 50 pc". Sect. 4.7: Dobbs et al. 2011's "only a factor of ~2 increase
  with spiral arms compared to without" — the quantity not named in the sentence (context: star formation), not a gas
  profile. Dust: Sect. 1.1 "dark dust lanes alongside spiral arms" (Sandage 1961; Lynds 1970), no number.
- **So**: with S96's Baba et al. 2015 (offsets only), three of the dynamic-arm sources named so far print no profile.
  Ruleset (i) — keep the co-rotating frame with a sourced profile — is NOT SOURCED; ruleset (ii) — a shock where an arm
  has a pattern speed — is sourced (KO02) only in a frame the model does not have, and taking it re-opens D216: the
  owner's (D267).

### S98.4 How dark and how wide a dust lane is in a face-on spiral's optical image

How found (reader B): web searches (M51 dust lane extinction A_V width pc HST; Thornley & Mundy 1997 NGC 4414 dust
lanes; Elmegreen 1980 dust lanes; Holwerda 2005 arm inter-arm), then the papers' own pages.

- **Schinnerer, Weiss, Aalto & Scoville 2010**, "Multi-Transition Study of M51's Molecular Gas Spiral Arms",
  arXiv:1007.0692 — ar5iv HTML, one fetch (the journal not checked). "D=8.4 Mpc with 1'' ~ 40.7 pc" (Sect. I). **Width**:
  "The widths of the dust lanes visible in the HST V band image range from about 0.5'' to 2''" (Sect. V) = **20-81 pc**
  `[inferred: the reader's arithmetic at 40.7 pc per arcsec]`; "enhanced extinction is present across the full width of
  the gas spiral arms of ~ 7''" (~285 pc `[inferred]`); "the extincting material can not have a larger vertical extent
  than a dust lane is wide" — a gas scale height under 20-80 pc. These are M51's INNER arms (the CO field). **Darkness,
  as a column**: "The derived extinction is about AV~12-18" (Sect. V), from N(H2) = 1.87e21 A_V (Nakai & Kuno 1995)
  applied to the CO-derived N(H2) (2.3-3.3)e22 cm⁻²; the abstract "AV about 15 - 30 mag"; HII regions A_V ~3.0
  `[verified: Schinnerer et al. 2010, Sects. I, V, abstract]`. That is the FULL column through the disc from the gas,
  NOT the dimming of the starlight seen (stars in front of the dust are not dimmed); no surface brightness or lane over
  surroundings ratio printed (asked; none).
- **Rix & Rieke 1993**, "M51 Stripped To Its Bones", arXiv:astro-ph/9304006 (submitted to ApJ, the PDF says) — the PDF,
  text by `pdftotext -layout`. Abstract: "From modeling the color changes across the main dust lanes in M51, we find the
  optical depths to be ~0.5 in the K-band." Sect. 3.2: "optical depths in the dust lanes at K are about 0.5,
  corresponding to tau_V ~ 4"; "the dust lanes are optically thin at K, semi-transparent at J and I, and optically
  thick at B,V and R"; the dust's scale height relative to the stars' "is found to range from 0.25 to 0.6, decreasing
  with radius"; "in all cases the dust in the lanes appear to be more vertically extended than inferred from global
  edge-on estimates, zeta = 0.2". Fig. 8's caption: a lane at ~25″, τ_K ~0.4 "(corresponding to tau_V ~ 3.5) with a
  scale height of 60% of the star's"; a lane in a dominant arm at R ~90″, the dust's height "only ~ 35% of the star's",
  τ_K = 0.4-1, "corresponding to tau_V = 3.5 - 9". Sect. 3.2 cites Elmegreen 1980, "the optical depths in the lanes can
  be large, tau_V ~ 10" (secondary) `[verified: Rix & Rieke 1993, abstract, Sect. 3.2, Fig. 8]`.
  **Table 1 (p. 25), the OBSERVED colour change between the lane's centre and "the surrounding innerarm regions"**, mag,
  Lane 86 / Lane 45: J−K 0.21 / 0.13, I−K 0.50 / 0.38, R−K 0.64 / 0.53, **V−K 0.79 / 0.58**, **B−K 1.01 / 0.69** (each ±
  0.04) `[verified: Rix & Rieke 1993, Table 1]` (the labels as printed; Fig. 7 places the two lanes at ~25″ and ~90″ —
  which label is which was not read). **The arithmetic, marked** `[inferred: the reader's, not printed]`: K is
  attenuated "only by ~10%" (Sect. 3.2), ≤ 0.11 mag, so the lane's V deficit against the adjacent arm is about 0.58-0.79
  mag plus ≤ 0.11, i.e. **0.6-0.9 mag in V, a transmission of about 0.44-0.58 of the surroundings**; in B about 0.7-1.1
  mag (0.36-0.52). Caveat: a lane-centre colour at ground resolution (images 1.8″ per pixel rebinned; high-resolution J
  / K 0.6″ per pixel with 1.2″ seeing; ~40 pc per arcsec), so the lane averaged over ~50-100 pc. **Width: not printed**
  (Fig. 7, the cut, not seen).
- **Keel & White 2001**, "Seeing Galaxies though Thick and Thin. IV. The Superimposed Spiral Galaxies of NGC 3314",
  arXiv:astro-ph/0106056 (AJ, "in press, September 2001" per the page) — ar5iv HTML, two fetches. NGC 3314A, a
  foreground Sc, HST B and I (F814W), "a scale of 172 pc/arcsecond". The one source found that measures a lane's
  darkness against its OWN galaxy's light (the face-on image's case) apart from the backlit case, Sect. V: "Histograms
  of the relative I intensity showed the backlit dust to have many pixels with values as low as 0.3, while the
  non-backlit dust lanes have no values below 0.75, as predicted for a thin dust lane." "Comparable covering fractions
  are reached at, for example, 0.4 for the backlit case and 0.65 for the non-backlit areas." The relative intensity is
  the I image over "a median-filtered image with a 5.0'' window" (= 0.86 kpc `[inferred]`); "the changes in B-I at
  transmission 0.75 are 0.08 and 0.20 magnitude for the backlit and non-backlit regions"; "most of the dust must be
  well-concentrated to the disk midplane." `[verified: Keel & White 2001, Sect. V]` Backlit (an occultation, not a face-on
  image's look): Fig. 8's caption, "The darkest areas in (e) have a B transmission near 0.40" (R ~3.7 kpc); Sect. III.2,
  "Spiral arms can include dust clouds on 15-pc scales with optical depths up to tau_B=1 at any radius within the disk";
  the conclusions, "dusty arms can include regions of high opacity A_B>1"; the inter-arm rises "by about Delta A_B=0.12
  per kpc" (Sect. III.1 says ~0.25 mag/kpc; the paper does not reconcile them). **Width not printed** (no width column
  in Table 2; Fig. 11 draws the lanes "with the proper radius and width" but prints none). Lanes at R 1.7-3.8 kpc.
  For a face-on image `[inferred]`: a lane in its own galaxy's light dims I to no less than 0.75 of the 0.86 kpc running
  median (one Sc); in V deeper (the B−I change says the lane reddens), not printed.
- **Holwerda et al.** (counts of distant galaxies), arXiv:astro-ph/0508261 (proceedings; the authors not on the page):
  32 HST/WFPC2 fields; opacity shows "a strong radial relation in the arms and a much flatter profile in the rest of
  the disk", values in a figure only, binned in 0.25 R₂₅ annuli `[verified: Holwerda et al., text]`. **No lane-scale
  number** (arm masks over annuli). Domingue, Keel & White 2000 and White, Keel & Conselice 1996 surfaced only in a
  search summary — NOT READ, kept out.
- **Elmegreen 1980** (ApJS 43, 37, per a search listing) — **UNREACHABLE** (the ADS abstract returned HTTP 405; the full
  scan's redirect not followed). Its "tau_V ~ 10" is known here only as Rix & Rieke 1993 report it.
- **Thornley & Mundy 1997** (ApJ 490, 682), NGC 4414 — a search snippet only (Hα, CO, HI against near-infrared
  armlets); NOT fetched; no dust number expected from it `[inferred from the abstract's scope]`. **Unread.**
- **Against the model** `[inferred: the reader's]`: the model's stars' transmission at the gas crest, 0.82-0.95 of the
  ring median's (S97), is LIGHTER than M51's lanes (0.44-0.58 in V) and comparable to or lighter than NGC 3314A's I-band
  floor (0.75); the observed lanes are 20-80 pc wide, a few render cells, where the model's ridge is kpc-wide. Even
  KO02's narrowest shocked arm (0.05 Lx, ~155 pc at mid level) is 2-8 times wider than M51's lanes: a sourced lane would
  be a thin feature at the ridge (the shock front or the clouds), not the gas ridge's FWHM — #129's width check (0.17 of
  the spacing, Egusa et al.) and a dust lane's width are different statistics and are not to be merged.

### S98.5 The model's gas ridge across the arm (the measurer, first pass item 2)

**Method** (`s98_M.md` section 2; logs `s98_M_ridge_milky_way.log`, `s98_M_ridge_ngc_4414.log`; the field S96's saved
`/api/render` grid `dust_placement_unspurred` — `gas_density_contrast`'s cell means without the spurs, 75 pc × 1°, 0-30
kpc; no server, no new model run): per ring row, crests = local maxima with prominence ≥ 0.15 × the row's range; the
trough = the mean of the minima between a crest and its two neighbours; the FWHM along the ring at (crest + trough)/2
(also at (crest + inter-arm median)/2); the arm spacing along the ring = the mean arc gap to the two neighbouring
crests; ACROSS = along × sin(the tracked pitch, crest by crest over ±6 rows). FWHM / spacing is pitch-free. The
inter-arm median = the row's cells outside every crest's FWHM. A ring's number = the median over its crests, then the
median over the five rows R0 − 150 pc to R0 + 150 pc, [min..max over rows].

| template | R kpc | crests | crest / ring median | crest / inter-arm median | pitch (tracked) ° | FWHM across pc | spacing across pc | FWHM / spacing (trough base) | (inter-arm-median base) |
|---|---|---|---|---|---|---|---|---|---|
| milky_way | 4 (bar lanes) | 2 | 6.33 [5.81..6.87] | 6.34 [5.83..6.88] | 55.7 | 520 [515..528] | (two lanes 180° apart: not a spacing) | — | — |
| milky_way | 6 | 3 | 1.30 [1.21..1.46] | 1.61 [1.44..1.91] | 25.0 [21.5..32.9] | 2256 [1590..3347] | 4965 [3423..6732] | 0.47 [0.34..0.52] | 0.38 [0.26..0.47] |
| milky_way | 8 | 4 | 1.31 [1.29..1.33] | 1.50 [1.48..1.52] | 15.6 [15.4..19.0] | 1210 [1167..1337] | 3435 [3169..4178] | 0.35 [0.33..0.43] | 0.28 [0.26..0.37] |
| milky_way | 10 | 4 | 1.25 [1.24..1.28] | 1.43 [1.40..1.46] | 18.9 [16.2..19.6] | 1679 [1495..1819] | 5238 [4328..5768] | 0.36 [0.32..0.40] | 0.35 [0.30..0.37] |
| ngc_4414 | 4 | 5 | 1.53 [1.49..1.66] | 1.82 [1.80..1.85] | 31.7 [30.9..33.7] | 1082 [1003..1090] | 3103 [3045..3406] | 0.29 [0.27..0.33] | 0.27 [0.26..0.33] |
| ngc_4414 | 6 | 5 | 1.54 [1.53..1.55] | 1.66 [1.64..1.68] | 32.8 [27.0..42.7] | 1269 [1223..1372] | 4520 [4055..4841] | 0.29 [0.29..0.31] | 0.27 [0.26..0.29] |
| ngc_4414 | 8 | 4 | 1.38 [1.37..1.40] | 1.60 [1.58..1.68] | 48.6 [26.0..53.5] | 2048 [1966..2159] | 9320 [4951..9901] | 0.37 [0.36..0.39] | 0.33 [0.33..0.37] |
| ngc_4414 | 10 | 0 | the pattern is flat (1.0000 everywhere at R 10.01); it fades from a range of 0.53 at 9.0 kpc to 0.05 at 9.94 and is absent from 10.0 kpc out | | | | | | |

- **The method's check**: the bar lanes at 4 kpc read FWHM 510-531 pc against `BAR_LANE_WIDTH` 0.10 a = 0.5 kpc.
- **Caveats, as the measurer gives them.** The per-crest scatter is large (`milky_way` 8 kpc: FWHM / spacing 0.29-0.38,
  crest / ring median 1.21-1.55; 10 kpc: one crest 58.6° long with a tracked pitch of 69° — a merged double, kept in the
  median). The pc columns inherit the tracked pitch's error (±20 % on `milky_way` at 8-10 kpc, worse at 6 kpc and on
  `ngc_4414` at 8 kpc); the FWHM / spacing column does not. NGC 4414's flocculent pattern's direction is poorly defined.
- **Against #144's / #129's pinned reading** (FWHM 0.37 of the arm spacing on `milky_way`, 0.39 on `ngc_4414`): the
  measurer's 0.35-0.47 on `milky_way` (6-10 kpc) and 0.29-0.37 on `ngc_4414` (4-8 kpc) are the same order; how the
  pinned number was measured was not read, so the definitions may differ (the half level, the baseline). The crest over
  the ring median here (1.25-1.54 at 6-10 kpc) is below S97's "1.5-2.0" because S97 took each ring's single largest
  cell; this is the median crest. The crests here are over the ring's and the inter-arm median, not KO02's mean
  (F-98B-1): the columns are set beside KO02's range, not ruled against it.

### S98.6 Not read or unreachable

Elmegreen 1980 (unreachable); Thornley & Mundy 1997's full text; Domingue, Keel & White 2000 and White, Keel &
Conselice 1996 / 2000 (search summaries only); Pettitt et al. 2015 and Dobbs & Bonnell 2008 (live-disc gas; not
fetched); KO02's table read once on one host and ApJ 570, 132 not confirmed on a page; Rix & Rieke's Fig. 7 (the lane
cuts, which would give a width) not seen; DB14's characters 200 000 to the end not read; Shu et al. 1972 (only as DB14
reports it).
