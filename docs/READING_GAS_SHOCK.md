# READING_GAS_SHOCK — the steady spiral shock, pattern speeds, and where the gas ridge sits (S57, BUILD_III Phase P2)

**The lead's note (2026-10-04).** Two Opus readers, briefed by BUILD_III §3e and forbidden the repository, wrote
what is below the rules; each part is entered as written. Part A is the shock's equations and the published
profiles a solver can be checked against; Part B is pattern speeds and the gas ridge's place and width. Gate G2
rules on them before anything is built (D216).

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
| A1 | Arms are transient; Ω_p falls with radius, "almost equal to the rotation curve" | arm lifetime ≈ 120 Myr (one arm, t = 1.73–1.85 Gyr); Ω_p ~30–40 km/s/kpc inner to ~10 at 8 kpc | N-body, pure stellar disc 3×10¹⁰ M☉, 3×10⁶ particles, static halo | `[verified: Grand, Kawata & Cropper 2012a, arXiv:1112.0019, abstract and pattern-speed section, https://ar5iv.labs.arxiv.org/html/1112.0019]` |
| A2 | Same with a bar: Ω_p(R) similar to stellar rotation, "slightly faster"; no offset between SF tracers across the arm | qualitative | N-body/SPH barred disc | `[verified: Grand, Kawata & Cropper 2012b, arXiv:1202.6387, abstract, https://arxiv.org/abs/1202.6387]` |
| A3 | "every single position in the arm can be regarded as the co-rotation point"; Ω_p decreases with radius like galactic rotation | arm lifetime ≈ 0.3–0.5 rotation periods (~100–160 Myr at R = 2R_sd); max amplitude at pitch ~30° | N-body, 3×10⁸ particles, disc 3.2×10¹⁰ M☉, rigid NFW halo, no bar | `[verified: Baba, Saitoh & Wada 2013, ApJ 763, 46, arXiv:1211.5401, abstract, §3, §6, https://ar5iv.labs.arxiv.org/html/1211.5401]` |
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
