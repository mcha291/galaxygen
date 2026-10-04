# READING_BAR — the bar's body and presence, its lanes, and the arms' relation to it (S58, BUILD_III Phase P3)

**The lead's note (2026-10-04).** Two Opus readers, briefed by BUILD_III §3e and forbidden the repository, wrote
what is below the rule; each part is entered as returned, its headings one level down to sit in this document.
Part A is the bar's light share, shape, profile and size, the bar fraction against disc properties, and the
stability criteria with what tests them. Part B is the gas and dust lanes, the gas inside the bar, the arms'
phase and strength against the bar, and how far a bar-driven two-armed response reaches (also the reading debt
#139 asked for, and the one #138's re-read at this phase's close will stand on). Both were run while S57's
closing suite ran, before this session's branch existed; neither reader saw the model or its numbers.

**What the readings say that the plan's text did not foresee** (the lead's summary; the parts below are the
record). (1) *No source gives a barred fraction as a function of a criterion's value, nor a galaxy-to-galaxy
scatter about a threshold* (A3): the plan's "presence derived from the sourced stability criterion; a seeded
residual only if a galaxy-to-galaxy scatter is read" has, as read, a criterion that is right for roughly three
galaxies in four and no scatter to draw. (2) *The bar's share is of the whole galaxy's light* (Bar/T ≈ 0.10),
and no 3.6 µm statistic was found. (3) *The lanes' curvature against bar strength is an envelope with a wide
spread*, and two fitted laws disagree in the sign of their axis-ratio term (B4). (4) *Whether bars are emptied
of gas off the lanes is disputed in numbers* (B4). (5) *The arms' link to the bar is measured only within about
1.5 bar radii*, by eye and unsigned for the phase.

---

## Part A — the bar's body and its presence (reader 1)

Reading done blind to the model, by web search and fetch only (2026-10-04). Every number below was read on a
fetched page unless tagged otherwise. The fetch tool passes pages through a small model; `×2` means two
separate fetches (or two sources) agreed, `×1` means a single fetch. Tags in the tables are written
`[verified: KEY, place, ×n]`; each KEY expands in A2 to author, year, journal, arXiv id and the fetched URL.

### A1 Summary tables

#### A1.1 Bar light or mass share

| Quantity (definition) | Value as printed | Sample, band | Tag |
|---|---|---|---|
| Bar/T, luminosity; T = whole galaxy (bulge + disc + bar); 2D fit, Sérsic bar | distribution "peak at ≈0.1" | 291 barred, b/a ≥ 0.9, M⋆ > 10¹⁰ M☉, z 0.02–0.07, SDSS i | [verified: G11, §3.1, ×2] |
| Bar/T, stellar mass, same fits | peak higher than in light; "up to about 40%" | same | [verified: G11, §3.1, ×2] |
| Bar/T median as quoted by a later paper | "median Bar/T∼0.10" (for G11) | same | [verified: K18, results, ×1] |
| Bar/T, luminosity, i band; disc+bar(+bulge) Sérsic fits; strong bars (p_bar ≥ 0.5) | "Bar/T∼0.14", same for disc-dominated and obvious-bulge, low and high mass | ∼3,500 fitted; 2,435 volume-limited, z < 0.06, i ≲ 60° | [verified: K18, results, ×2] |
| Bar/T, H-band light (= mass at one M/L); T = bulge + disc + bar | range "∼0.03 to ∼0.47"; six above 0.3; mean flat Sa–Sb, declines "by about 0.1" Sb→Sc | 143 spirals, M_B ≤ −19.3, i ≤ 70° (83 barred) | [verified: W09, §5.5, ×2] |
| Share of all stellar mass in the sample that is in bars (barred and unbarred galaxies together) | "∼10%" bars, ∼70% discs, ∼20% bulges | same sample S1 | [verified: W09, §5.2, ×2] |
| Share of stellar mass in bars, all massive galaxies including ellipticals | 4% bars (32% E, 36% discs, 25% classical bulges, 3% pseudo-bulges) | ∼1000 SDSS galaxies, M⋆ > 10¹⁰ M☉ | [verified: G09, abstract, ×1 + search snippet] |
| Effect of modelling the disc break on Bar/T at 3.6 µm | Bar/T falls "∼25%" in the median when the break is modelled | 144 S4G barred, b/a > 0.5 | [verified: K14, text; K15 repeats, ×2] |
| Milky Way: bulge-region stellar mass / total stellar mass | 0.3 ± 0.06; M_b⋆ = (1.4–1.7)×10¹⁰ M☉ | review | [verified: BHG16, §4.2.4, ×2] |
| Milky Way: bar + bulge stellar mass (long bar and b/p bulge together) | 1.88 ± 0.12 ×10¹⁰ M☉ (inner disc in bar region 1.29 ± 0.12 ×10¹⁰) | M2M models | [verified: P17, abstract, ×1] |

No S4G (3.6 µm, pipeline 4) Bar/T statistic was found on any page read: S15 defers statistics to a second paper.

#### A1.2 Shape, profile, size

| Quantity (definition) | Value as printed | Sample | Tag |
|---|---|---|---|
| Bar ellipticity ε = 1 − b/a of the 2D model component (face-on galaxies) | distribution "peaks at ≈0.6" | G11 sample | [verified: G11, §3.1, ×2] |
| Ellipse-fit vs 2D-fit ellipticity | ellipse fits "on average, 20% lower" | — | [verified: G11, §3.1, ×2] |
| Bar component axis ratio b/a (Sérsic component, strong bars; not stated as deprojected) | "b/a=0.31±0.12" median and 1σ scatter; range 0.1–0.6 | K18 sample | [verified: K18, results, ×2] |
| Deprojected ε at the isophote of maximum ellipticity, 3.6 µm | spirals: mean "ε ≈ 0.5", "nearly independent of T"; S0s "≈0.2" | 654 bars, i ≤ 65° | [verified: DG16, abstract + §5.3, ×2] |
| Same quantity in stacked bars | S0 "ε≈0.35"; spirals and irregulars "ε≈0.5" | 748 bars | [verified: DG16b, text, ×1] |
| Projected maximum ellipticity (ellipse fit, J+H+Ks) | typical 0.5; early (Sa–Sb) 0.54 ± 0.13; late (Sc–Sd) 0.48 ± 0.12 (1σ) | 151 spirals, i < 65°, D < 40 Mpc | [verified: MD07, Table 3, ×2] |
| Deprojected maximum ellipticity e_bar (ellipse fit, B and H) | range 0.25–0.80; 70% (B), 71% (H) within 0.50–0.75; 7% (B), 10% (H) within 0.25–0.40 | 136 spirals, i < 60° | [verified: MJ07, results, ×1] |
| Boxiness c of the generalised ellipse (|x|/a)^c + (|y|/b)^c = 1 | "peaks at c=3" | G11 sample | [verified: G11, §3.1, ×2] |
| Boxiness, 3.6 µm | every bar c > 2; no trend with host | 144 S4G | [verified: K15, results, ×2] |
| Bar Sérsic index n_bar along the bar | typical "≈0.7" (between Gaussian 0.5 and exponential 1) | G11 sample | [verified: G11, §3.1, ×2] |
| n_bar at 3.6 µm against bulge | B/T > 0.2: median ∼0.30 (flat); B/T = 0: median ∼0.85, range 0.25–1.4; flat defined n < 0.4, exponential n ≥ 0.8 | 144 S4G, i < 60° | [verified: K15, results, ×2] |
| Mass of the flat→exponential change | M₃.₆ ∼ −20 AB mag, M⋆ ∼ 10^10.2 M☉ | same | [verified: K15, results, ×2] |
| n_bar, SDSS | 0.92 ± 0.67 (disc-dominated / low mass); 0.40 ± 0.30 (obvious bulge / high mass), 1σ scatter | K18 | [verified: K18, results, ×2; subsample label differs between fetches] |
| S4G pipeline-4 bar function | `Σ(r) = Σ₀ [1 − (r/r_out)^(2−β)]^α` for r < r_out, else 0; fixed α = 2, β = 0; free: r_out, q_bar, PA | 863 of 2,277 fits have a bar | [verified: S15, §decomposition + Table 2, ×1] |
| CALIFA bar function | `I(r) = I₀ [1 − (r/a_bar)²]^(n_bar+0.5)`, r ≤ a_bar; n_bar fixed at 2 | 404 galaxies, g r i | [verified: MA17, §3, ×2] |
| Bar length / disc scale length (R-band, L_avg of two measures) | S0–Sab 1.29 ± 0.54 (abstract: "mean ∼1.4 h", range 0.5–2.5 h); Sc–Sd 0.57 ± 0.44 (abstract: 0.6 h, range 0.2–1.5 h) | 65 S0–Sb + 70 Sb–Sd | [verified: E05, abstract + Table 5, ×2 for abstract] |
| Bar length / R25 | S0–Sab 0.37 ± 0.13 (abstract ∼0.38); Sc–Sd 0.14 ± 0.07 | same | [verified: E05, abstract + Table 5] |
| Bar length, S4G, visual, deprojected | mean ∼2.5 kpc; S0–Sab ∼0.27 R25.5 and ∼1.25 h_R; ⟨r_bar/h_R⟩ ≥ 1 only for S0s and early spirals | DG16 | [verified: DG16, §5.2, ×1] |
| Bar size against scale length | `log a_vis = 0.04(±0.02) + 0.76(±0.06) log h` (kpc); Spearman 0.61 | 367 S4G barred spirals | [verified: E19, Table 3, ×1] |
| Bar semi-major axis / R25 (2MASS) | all 0.29 ± 0.17; early 0.43 ± 0.18; late 0.22 ± 0.11; 4.2 ± 2.9 kpc overall | MD07 | [verified: MD07, Table 3, ×2] |
| Upper bound | "no bar extends to a radius larger than ≈3 times the disc scale length" | G11 | [verified: G11, §3.1, ×1] |

#### A1.3 Bar fraction against disc properties

| Against | Fraction as printed | Sample, detection, limit | Tag |
|---|---|---|---|
| Stellar mass | peak "≈0.70 at log(M⋆/M☉)≈9.7", falling to both sides; whole sample 0.563 ± 0.019 (D ≤ 25 Mpc), 0.618 ± 0.020 (also log M⋆ ≥ 8.5) | S4G spirals; SB + SAB of Buta et al. via HE15; mean resolution 165 pc | [verified: E18, abstract + Table 2, ×2] |
| Stellar mass, fitted | `f_bar = 1/(1 + exp(−(α + β₁x + β₂x²)))`, x = log M⋆; α = −82.2 ± 22.1, β₁ = 17.1 ± 4.62, β₂ = −0.88 ± 0.24 | Sample 1 (659 galaxies) | [verified: E18, §3 + Table, ×2] |
| Colour, gas | flat over g−r ≈ 0.1–0.8 and log(M_HI/M⋆) ≈ −2.5 to 1; gas coefficient P = 0.55 | 556 with gas | [verified: E18, abstract + Table 4, ×2] |
| Hubble type (visual / ellipse / Fourier) | T∈[−3,0): 49.1 ± 4.6 / 40.5 / 43.1 %; [0,3): 69.8 ± 3.2 / 61.8 / 61.8; [3,5): 55.8 ± 3.6 / 48.9 / 46.8; [5,7]: 75.1 ± 2.4 / 60.2 / 50.8; T>7: 60.6 ± 2.2 / 37.1 / 25.5 (N = 116, 212, 190, 329, 498) | S4G, 1,345 discs, i ≤ 65° | [verified: DG16, Table 1, ×2] |
| Stellar mass (CALIFA) | 9.5–10: 74.6 ± 6.4 %; 10–10.5: 46.4 ± 8.6; 10.5–11: 72.0 ± 8.0; 11–11.5: 25.1 ± 22.1; overall 57% | 404 galaxies, volume-corrected; visual + fit (q_bar < 0.7) | [verified: MA17, Table 4, ×2] |
| All discs, SDSS visual | 29.4 ± 0.5 %; over half of red, bulge-dominated discs barred | 13,665 discs, 0.01 < z < 0.06, M_r < −19.38; Galaxy Zoo 2 vote majority | [verified: M11, abstract, ×2] |
| Gas (HI) | strong-bar fraction 22 ± 1 % (HI detected), 32 ± 1 % (undetected); log M⋆ > 10.2: 31 ± 2, < 10.2: 16 ± 1; g−r > 0.6: 33 ± 2, < 0.6: 16 ± 1; median f_HI 0.39 barred, 0.74 unbarred | 2,090 discs, z < 0.05, p_bar > 0.5; 1.3 kpc at z = 0.05 | [verified: M12, Table 1 + text, ×1] |
| Stellar mass, SDSS visual | ∼30 % overall (2,312 bars); ∼40 % at log M ∼ 9; minimum ∼24 % at ∼10.2; plateau 30 % above ∼11.4 | ∼14,000, g < 16, z 0.01–0.1; RC3-like strong bars | [verified: NA10, text, ×1] |
| Strong / weak, SDSS | 23.8 % strong, 6.5 % weak, 30.4 % total; rises with M⋆/M_halo, falls with HI fraction at fixed M⋆ (per-bin values in figures) | 10,674 late types, z 0.02–0.055, b/a > 0.6; strong = longer than ¼ of optical size | [verified: CS17, §2–3, ×1] |
| Redshift | ∼65 % locally → ∼20 % at z ∼ 0.84; strong bars ∼30 % → under 10 % | 2,157 COSMOS spirals | [verified: S08, abstract, ×1 + snippet] |
| NIR / optical | H: 60 %, B: 44 % (deprojected); 2MASS: 59 % (67 % with candidates) | OSUBSGS 136; 2MASS 151 | [verified: MJ07; MD07, ×1 / ×2] |
| Simulations | TNG100 55 % of 1,269 discs (A₂ > 0.15, M⋆ > 10^10.5); Illustris-1 8.9 % of 1,232; EAGLE ∼40 % (20 % strong A₂ > 0.4, 20 % weak 0.2–0.4) of 269; Auriga 60 % of 39 (A₂ ≥ 0.25) | — | [verified: Z20; Al17 ×2; F25, ×1] |

Why SDSS fractions are lower: bars with projected semi-major axis under twice the PSF FWHM go undetected; SDSS
FWHM ≈ 1.4″ at ⟨z⟩ ≈ 0.045 is ≈ 1.25 kpc; bar size falls with mass below a break at log M⋆ = 10.16, so small
bars in low-mass, blue, gas-rich discs are missed [verified: E18, abstract + §5, ×2].

#### A1.4 Stability criteria and what tests them

| Criterion | Formula and threshold as read | Probability or scatter given? | Tag |
|---|---|---|---|
| Ostriker & Peebles 1973 | `τ_OP = T_rot/|U|`; stable if τ_OP < 0.14 (as stated by a later paper) | none | [verified: Wo24, §IV.1, ×1 — original NOT READ] |
| Efstathiou, Lake & Negroponte 1982 | `ε = V_max / (G M_d / R_d)^(1/2)`; unstable if ε ≲ 1.1 (stars); gas discs ≲ 0.9 (Christodoulou et al. 1995) | none in the criterion | [verified: MMW98 eq. 35; A08; IV22 eq. 1; YS15; Ka25 eq. 1 — five sources agree; original NOT READ] |
| Mo, Mao & White 1998 | stable if `λ′ ≳ λ′_crit = √2 ε²_m,crit m_d f_c^(1/2) f_R^(−1) f_V^(−2)`, λ′ ≡ (j_d/m_d) λ; rough form "λ′ > m_d" | fraction of haloes with stable discs: "at most half" for m_d = 0.05, "about 90 percent" for m_d = 0.025 (j_d = m_d) | [verified: MMW98, eq. 37, §3.2–3.3, ×1 + a second paper's quotation of eq. 37] |
| Toomre Q | `Q ≡ σ_R κ / (3.36 G Σ) > 1` (axisymmetric stability) | — | [verified: Se14, §II.9; YS15, ×2] |
| Swing amplification X | `X ≡ κ² R / (2π G Σ m)`; large for 1 ≲ X ≲ 2 (F18) or 1 ≲ X ≲ 3 (Se14); gain ∼100 at X ≃ 2, Q ≃ 1.2, a few at Q ≃ 2 | — | [verified: F18 eq. 6; Se14 eqs 17–19, ×1 each] |
| Disc fraction and time (Fujii) | `f_d ≡ (V_c,d/V_c,tot)²` at R = 2.2 R_d; `t_b = (0.146 ± 0.079) exp[(1.38 ± 0.17)/f_d]` Gyr; formed when A₂,max > 0.2 and R_b > 1 kpc; N_d = 8M, Q₀ = 1.2 | fit errors only; "the scatter is large"; at one f_d, t_b = 0.27 Gyr (Q₀ = 0.5) against 8.8 Gyr (Q₀ = 2.0) | [verified: F18, eq. 11 + §3.3, ×2; BH23 eq. 7 agrees] |
| Disc fraction and time (Bland-Hawthorn) | `τ_bar/τ_H = exp[−13.9(f_disk − 0.250)]` (M_halo 5×10¹⁰), `exp[−14.1(f_disk − 0.310)]` (10¹¹), `exp[−13.0(f_disk − 0.328)]` (5×10¹¹ M☉); τ_H ≈ 13.78 Gyr; dividing line f_disk ≈ 0.3 | none stated; 21 dry + 4 gas models; f_gas = 0.1 slows onset by up to 50 % | [verified: BH23, eqs 1, 7–10, ×2] |
| Local + global dominance (EAGLE) | `f_disc ≡ V₅₀/(G M⋆/r₅₀)^(1/2)`, `f_dec ≡ V₅₀/V_max,halo`; strong bars: f_disc < 1 and f_dec > 0.95 | 45 % of discs with f_disc < 1.1 stay unbarred; pair finds 82 % of strong bars, 11 % of those selected unbarred; 77 % of unbarred found by f_disc > 0.95, f_dec < 1 | [verified: Al17, §4, ×2] |
| Q with central concentration C | boundary `Q²_min/4 + C²/2.89 = 1`; critical ELN value ∼1.0, critical τ_OP 0.14–0.24 | none | [verified: Wo24, eq. 17, ×1] |

Tests of ELN: TNG100 74 % of strong bars found unstable, 79 % of unbarred found stable (58 and 131 galaxies);
TNG50 72 % and 75 % (39 and 31) [verified: IV22, §4, ×1; abstract ∼75 % / ∼80 %]. SPARC: 71 % ± 12 % of barred
have ε ≤ 1.1, 81 % ± 3.6 % of unbarred have ε > 1.1 (14 barred, 118 unbarred, bulgeless); CALIFA 67 % ± 12 %
(15 barred) [verified: Ka25, ×2]. SPARC + LITTLE THINGS, 91 galaxies: wrong regime "in about 55% of the cases"
[verified: R23, §4, ×2]. Eight live-halo disc models with ε 0.79–1.0 all barred (seven reached A₂ ≃ 0.6)
[verified: YS15, ×1]. Counter-examples at ε = 0.89 (one stable hot disc) and ε = 1.19–1.22 (bars form)
[verified: A08, Figs 1–2, ×1].

### A2 Per-source notes

Each entry: full tag, what the citation covers, definitions.

- **G11** `[verified: Gadotti 2011, MNRAS 415, 3308, arXiv:1003.1719, §2–3.1, https://ar5iv.labs.arxiv.org/html/1003.1719]`.
  Covers ellipticity, boxiness, n_bar, the Bar/T peak and the 40 % ceiling; medians and σ sit in Fig. 1 and were
  not readable. Bar = Sérsic profile on a generalised ellipse; face-on sample, so shapes are near intrinsic.
- **G09** `[verified: Gadotti 2009, MNRAS 393, 1531, arXiv:0810.1953, abstract, https://arxiv.org/abs/0810.1953]`.
  Covers only the 4 % mass budget; the denominator includes ellipticals.
- **W09** `[verified: Weinzirl et al. 2009, ApJ 696, 411, arXiv:0807.0040, §3.3, §5.2, §5.5,
  https://ar5iv.labs.arxiv.org/html/0807.0040]`. Covers the Bar/T range and the 10 % mass share; no median or
  per-type mean in the text. Bar fraction by decomposition 58.0 ± 4.13 % (83 of 143). Bar Sérsic "mostly below
  unity".
- **K18** `[verified: Kruk et al. 2018, MNRAS 473, 4731, arXiv:1710.00093, results,
  https://ar5iv.labs.arxiv.org/html/1710.00093]`. Covers Bar/T, b/a, n_bar. Strong bars only; 1,246 disc + bar and
  2,215 disc + bar + bulge fits. Bar effective radius peaks at ∼0.5 of the disc's; "20-80%" of disc size.
- **K15** `[verified: Kim et al. 2015, ApJ 799, 99, arXiv:1411.4650, eqs 2, 4 and results,
  https://ar5iv.labs.arxiv.org/html/1411.4650]`. Covers the profile and boxiness; gives no Bar/T or axis-ratio
  statistic. Carries the Elmegreen & Elmegreen (1985) statement: flat bars in early types, exponential in late.
- **K14** `[verified: Kim et al. 2014, ApJ 782, 64, arXiv:1312.3384, https://arxiv.org/html/1312.3384]`. Covers the
  25 % Bar/T shift only.
- **S15** `[verified: Salo et al. 2015, ApJS 219, 4, arXiv:1503.06550, Table 2 and bar function,
  https://ar5iv.labs.arxiv.org/html/1503.06550]`. Covers the function and counts (BDbar 213, NDbar 184, Dbar 458,
  Zbar 8). No statistics. Bar length sometimes held fixed when GALFIT gave a wrong length.
- **DG16** `[verified: Díaz-García et al. 2016, A&A 587, A160, arXiv:1509.06743, Table 1, §4, §5.2–5.3,
  https://ar5iv.labs.arxiv.org/html/1509.06743]`. Covers Table 1 in full, mean ε, the scaled lengths in text.
  Length ratios: ⟨r_ε/r_vis⟩ = 0.97 (σ 0.18), ⟨r_A2/r_vis⟩ = 0.75 (σ 0.25), ⟨r_Qb/r_vis⟩ = 0.62 (σ 0.25). Bar
  fraction "drops for M⋆ ≲ 10^9.5–10 M☉". Table 3 not carried by the HTML.
- **DG16b** `[verified: Díaz-García, Salo & Laurikainen 2016, A&A, arXiv:1607.07317, text and Table 5,
  https://arxiv.org/html/1607.07317]`. Covers the stack statements: T < 5 bars flat, late-type exponential; only
  M⋆ ≥ 10¹⁰ M☉ show flat bars; stack A₂ maximum 0.23 (log M⋆ 8.5–9) and 0.41 (10.5–11). Single fetch.
- **HE15** `[verified: Herrera-Endoqui et al. 2015, A&A 582, A86, arXiv:1509.05328,
  https://ar5iv.labs.arxiv.org/html/1509.05328]`. Covers method only: 1,146 of 1,174 bars measured visually,
  deprojected; bars in 55 % of S0/a–Sc and 81 % of Scd–Sm. No aggregate ellipticity.
- **MJ07** `[verified: Marinova & Jogee 2007, ApJ 659, 1176, arXiv:astro-ph/0608039,
  https://ar5iv.labs.arxiv.org/html/astro-ph/0608039]`. Covers fractions and the ellipticity distribution; 68 % (B)
  and 76 % (H) of bars have a_bar ≤ 5 kpc; a_bar/R25 mostly 0.1–0.5.
- **MD07** `[verified: Menéndez-Delmestre et al. 2007, ApJ 657, 790, arXiv:astro-ph/0611540, Table 3,
  https://arxiv.org/html/astro-ph/0611540]`. Ellipticity is projected. Detection: ε_max > 0.2, Δε > 0.1, ΔPA > 10°.
- **E05** `[verified: Erwin 2005, MNRAS 364, 283, arXiv:astro-ph/0508590, abstract, Tables 2, 4, 5, 8,
  https://arxiv.org/abs/astro-ph/0508590 and https://ar5iv.labs.arxiv.org/html/astro-ph/0508590]`. a_ε (maximum
  ellipticity) is a lower limit, L_bar an upper; S0–Sb: a_ε/h = 1.27 ± 0.52, L_bar/h = 1.51 ± 0.56; bar size
  against h: r = 0.73–0.75 (n = 45). Simulated R_bar/h quoted from 0.6 to 3.6. Tables single fetch.
- **E18** `[verified: Erwin 2018, MNRAS 474, 5372, arXiv:1711.04867, abstract, Tables 2–4,
  https://ar5iv.labs.arxiv.org/html/1711.04867]`. Covers the frequency, the fit, the resolution argument. Bar size:
  slope 0.10 ± 0.03 below and 0.60 ± 0.08 above log M⋆ = 10.16; "considerable scatter" at fixed mass, no number.
- **E19** `[verified: Erwin 2019, MNRAS 489, 3553, arXiv:1908.08423, Tables 2–4, https://arxiv.org/html/1908.08423]`.
  No dependence of bar size on gas fraction (r = 0.08, P = 0.11) or on type once mass is held.
- **MA17** `[verified: Méndez-Abreu et al. 2017, A&A 598, A32, arXiv:1610.05324, Table 4,
  https://arxiv.org/html/1610.05324]`. Covers fraction per mass bin; no Bar/T aggregate.
- **M11** `[verified: Masters et al. 2011, MNRAS 411, 2026, arXiv:1003.0449, abstract, https://arxiv.org/abs/1003.0449]`.
- **M12** `[verified: Masters et al. 2012, MNRAS 424, 2180, arXiv:1205.5271, Table 1,
  https://ar5iv.labs.arxiv.org/html/1205.5271]`. Per-bin gas trend in figures only.
- **NA10** `[verified: Nair & Abraham 2010, ApJL 714, L260, arXiv:1004.0684, https://ar5iv.labs.arxiv.org/html/1004.0684]`.
- **S08** `[verified: Sheth et al. 2008, ApJ 675, 1141, arXiv:0710.4552, abstract, https://arxiv.org/abs/0710.4552]`.
- **CS17** `[verified: Cervantes Sodi 2017, ApJ 835, 80, arXiv:1611.04241, https://ar5iv.labs.arxiv.org/html/1611.04241]`.
  Halo mass from `M_halo = 2.54×10¹⁰ M☉ (r_d/kpc)(V_rot/100 km s⁻¹)²`; 1,471 with HI.
- **Z20** `[verified: Zhou et al. 2020, arXiv:2004.11620, https://ar5iv.labs.arxiv.org/html/2004.11620]`. Bars form
  where disc gas fraction is mostly below 0.4.
- **F25** `[verified: Fragkoudi et al. 2025, MNRAS, arXiv:2406.09453, https://arxiv.org/html/2406.09453]`. Barred
  galaxies are baryon-dominated within 5 kpc; unbarred stay dark-matter dominated and have higher Q; scatter
  noted, not quantified.
- **MMW98** `[verified: Mo, Mao & White 1998, MNRAS, arXiv:astro-ph/9707093, eqs 28, 35, 37, §3.2–3.3,
  https://ar5iv.labs.arxiv.org/html/astro-ph/9707093]`. `R_d = (1/√2)(j_d/m_d) λ r₂₀₀ f_c^(−1/2) f_R`.
- **A08** `[verified: Athanassoula 2008, MNRAS 390, L69, arXiv:0808.0016, https://arxiv.org/html/0808.0016]`. ELN ran
  2D discs in rigid haloes; the criterion ignores velocity dispersion and the halo's response.
- **YS15** `[verified: Yurin & Springel 2015, MNRAS 452, 2367, arXiv:1411.3729, https://ar5iv.labs.arxiv.org/html/1411.3729]`.
  With a bulge "only a subset of the systems develops bars"; they call 1.1 "a surprisingly robust indicator".
- **Al17** `[verified: Algorry et al. 2017, MNRAS, arXiv:1609.05909, §4, https://ar5iv.labs.arxiv.org/html/1609.05909]`.
  Parameters measured just before the bar grows (unbarred: at z = 0.5). l_bar/r₅₀ = 1.53 (+0.42, −0.41).
- **IV22** `[verified: Izquierdo-Villalba et al. 2022, MNRAS 514, 1006, arXiv:2203.07734,
  https://ar5iv.labs.arxiv.org/html/2203.07734]`. Bars A₂,max ≥ 0.3; M⋆ ≥ 10^10.4 M☉; D/T > 0.5. False positives are
  late-forming, bulge-heavy early, thick; false negatives are extended, high-spin, bars set off by a neighbour.
- **R23** `[verified: Romeo, Agertz & Renaud 2023, MNRAS 518, 1002, arXiv:2204.02695, eqs 9–10, §4,
  https://ar5iv.labs.arxiv.org/html/2204.02695]`. Writes ELN as `E ≲ 1` and `E² ≈ λ (j_d/j_h)/(M_d/M_h) ≲ 1`; bars from
  HyperLeda (43 % barred, 47 % not); mixing cannot be cured "by shifting the instability threshold". Own proxy
  `j_i σ̂_i/(G M_i) ≈ 1`, 1σ scatter ≈ 0.2 dex in ⟨Q_i⟩.
- **Ka25** `[verified: Kashfi et al. 2025, MNRAS 543, 518, arXiv:2509.02016, https://arxiv.org/html/2509.02016]`.
- **F18** `[verified: Fujii et al. 2018, MNRAS 477, 1451, arXiv:1712.00058, eqs 6, 9, 11, §3.3,
  https://ar5iv.labs.arxiv.org/html/1712.00058]`. Bars formed for f_d ≈ 0.35–0.60; none at f_d ∼ 0.06. Abstract: the
  epoch "exceeds a Hubble time when the disk-mass fraction is ∼0.35".
- **F19** `[verified: Fujii et al. 2019, MNRAS 482, 1983, arXiv:1807.10019, https://ar5iv.labs.arxiv.org/html/1807.10019]`.
  Carries no fit; only restates that larger f_d gives an earlier bar.
- **BH23** `[verified: Bland-Hawthorn et al. 2023, ApJ 947, arXiv:2303.05574, eqs 1, 7–10, App. A,
  https://ar5iv.labs.arxiv.org/html/2303.05574]`. τ_bar here is the e-folding time of A₂/A₀, not Fujii's threshold
  time. ELN "is not a reliable estimator"; ε ∝ f_disk^α, α < 0, coefficients in a figure only.
- **Wo24** `[verified: Worrakitpoonpon 2024, arXiv:2412.18098, §II–IV, https://arxiv.org/html/2412.18098]`. 24 models;
  stability needs both high Q_min and high concentration; either alone only slows the bar.
- **Se14** `[verified: Sellwood 2014, Rev. Mod. Phys. 86, 1, arXiv:1310.0403, §II.9, https://ar5iv.labs.arxiv.org/html/1310.0403]`.
- **BHG16** `[verified: Bland-Hawthorn & Gerhard 2016, ARA&A 54, 529, arXiv:1602.07702, §4.2.4,
  https://ar5iv.labs.arxiv.org/html/1602.07702]`. Total stellar mass ≈ 4.7–5.7 ×10¹⁰ M☉ (one fetch) or 5 ± 1 ×10¹⁰
  (the other); b/p bulge (b/a) ≈ 0.5 ± 0.05 seen from above, single fetch.
- **We15** `[verified: Wegg, Gerhard & Portail 2015, MNRAS 450, 4050, arXiv:1504.01401, abstract,
  https://arxiv.org/abs/1504.01401]`. Long bar half-length 5.0 ± 0.2 kpc, angle 28–33°, thin ∼180 pc and super-thin
  ∼45 pc components.
- **P17** `[verified: Portail et al. 2017, MNRAS, arXiv:1608.07954, abstract, https://arxiv.org/abs/1608.07954]`.
  Pattern speed 39.0 ± 3.5 km s⁻¹ kpc⁻¹, corotation 6.1 ± 0.5 kpc.

`[the reader's derivation]`, kept apart from the tables: (i) b/a = 1 − ε turns G11's peak into b/a ≈ 0.4 and the
ellipse-fit mean 0.5 into b/a ≈ 0.5; 0.5 × 1.2 = 0.6, so the two agree once G11's 20 % is applied. (ii) The
central Fujii fit reaches 13.8 Gyr at f_d = 1.38/ln(13.8/0.146) ≈ 0.30, and gives ≈ 7.5 Gyr at 0.35, 4.6 Gyr at
0.4, 2.3 Gyr at 0.5, 1.5 Gyr at 0.6. (iii) Erwin's fit peaks at x = β₁/(−2β₂) ≈ 9.7 with f ≈ 0.70, matching the
print; off-peak values are unsafe to evaluate, because β₂ printed to two figures moves the logit by ∼0.5.
(iv) From Ka25's SPARC counts, about 10 of 14 barred and about 22 of 118 unbarred have ε ≤ 1.1, so
P(bar | ε ≤ 1.1) ≈ 0.3 in that sample; the sample's bar fraction (14/132) is far below S4G's.

### A3 What a model could adopt

**Body, axis ratio.** Adopt b/a ≈ 0.4 (ε ≈ 0.6) for a 2D component (G11), with K18's 1σ scatter 0.12 as the only
printed spread. Alternatives: K18's b/a = 0.31 (strong bars only, so biased thin); ε ≈ 0.5 from ellipse fits
(DG16, MD07, MJ07), which G11 says runs 20 % low. Wrong if the ridge's own maximum-ellipticity isophote, measured
as the observers measure it, does not fall near 0.5 with most values in 0.50–0.75.

**Body, light share.** Adopt Bar/T ≈ 0.10 of total galaxy light for M⋆ > 10¹⁰ M☉ (G11), as a share of
bulge + disc + bar, not of the disc. Alternatives: 0.14 (K18, strong bars); W09's range 0.03–0.47. No source read
gives the share by mass bin, by type with numbers, or below 10¹⁰ M☉, and none at 3.6 µm. Wrong if the body's
share together with its axis ratio gives an m = 2 amplitude outside DG16b's stack maxima (0.23 to 0.41).

**Body, profile.** Adopt a Sérsic run along the bar with n_bar set by bulge prominence: ∼0.3 where B/T > 0.2,
∼0.85 where there is no bulge, changing near M⋆ ∼ 10^10.2 M☉ (K15); boxiness c ≈ 3 (G11), always above 2 (K15).
Alternatives: one index n ≈ 0.7 (G11); the S4G Ferrers form with α = 2, β = 0 (S15), which is a fitting choice,
not a measurement. Wrong if late-type bars in the model look flat, or early-type bars exponential.

**Body, size.** Check the half-length against h: 1.3–1.5 h in S0–Sab and ∼0.6 h in Sc–Sd (E05), ∼1.25 h_R in
S0–Sab (DG16), or log a = 0.04 + 0.76 log h (E19); nothing beyond ≈3 h (G11).

**Presence, criterion.** No source read gives the barred fraction as a function of a criterion's value, and none
gives a galaxy-to-galaxy scatter about a threshold. What is measured is classification error, and an empirical
frequency against mass. Three named options:

1. *ELN, ε ≤ 1.1, no draw.* Right for ∼72–75 % of bars and ∼75–81 % of unbarred discs in TNG and SPARC (IV22,
   Ka25), but R23 finds it wrong for ∼55 % of 91 galaxies and A08 and BH23 reject it. It predicts fewer bars in
   dark-matter-dominated, gas-rich dwarfs; E18's 0.56–0.70 over 10^8.5–10 M☉ argues against that.
2. *Disc fraction with a formation time, no draw.* f_d at 2.2 R_d, bar present if t_b(f_d) is shorter than the
   disc's age, with F18's coefficients; threshold f_d ≈ 0.30 (BH23) to 0.35 (F18). The printed errors are fit
   errors over simulations, and the Q dependence (0.27 against 8.8 Gyr) is a second parameter, so neither is a
   population scatter to draw from. Wrong if the model's bar fraction does not peak near 10^9.7 M☉ and fall on
   both sides, or if barred model discs are not baryon-dominated inside ∼2 R_d.
3. *The measured frequency.* E18's logistic in stellar mass as a probability. It is a draw from a measured
   frequency, not a residual about a derived criterion, so it meets the rule only if the rule is read that way.

A two-parameter form (Al17's f_disc with f_dec, or Wo24's Q with concentration) is the best-supported derived
criterion, tested in simulations only.

### A4 Conflicts between sources

- ELN against real galaxies: Ka25 finds 71 % / 81 % correct in SPARC; R23 finds ∼55 % in the wrong regime in
  SPARC + LITTLE THINGS. Different bar classifications (SPARC types against HyperLeda) and different M_d.
- Critical disc fraction: F18's abstract says ∼0.35; BH23 says ≈0.3, and F18's own central fit gives ≈0.30.
- Bar fraction against mass, colour, gas: rising with mass and redness, falling with gas in SDSS (M11, M12,
  CS17); peaked at 10^9.7 and flat in colour and gas in S4G (E18), who attributes the difference to resolution.
  NA10 shows a minimum at 10^10.2; MA17's bins are not monotonic.
- S0 bar ellipticity: ≈0.2 (DG16) against ≈0.35 (DG16b), same group, one year.
- Swing amplification range: 1 ≲ X ≲ 2 (F18) against 1 ≲ X ≲ 3 (Se14).
- Scaled bar length in early types: 0.38 R25 and 1.4 h (E05) against ∼0.27 R25.5 and ∼1.25 h_R (DG16).
- Milky Way long bar: one fetch of BHG16 returned a half-length of 3.5 kpc, an angle of 44° and component
  masses; a second fetch found none of these on the page, and We15 prints 5.0 ± 0.2 kpc and 28–33°. The first
  fetch's long-bar values are discarded as a mis-transcription.
- K18's n_bar subsamples: labelled by bulge class in one fetch, by mass in the other.

### A5 What could not be read

- Ostriker & Peebles 1973 and Efstathiou, Lake & Negroponte 1982: ADS returned HTTP 405; both known only through
  later papers. The "0.14 ± 0.02" appeared in a search snippet only `[recall — NOT READ]`.
- A&A pages for DG16 and HE15 returned HTTP 403; arXiv PDFs were not parsed. DG16's Table 3 (mean lengths per
  type in kpc, R25.5 and h_R; mean ε, Q_b, A₂) is not in the ar5iv page, and one fetch declined to copy tables.
- Medians and σ in G11's Fig. 1; per-bin fractions in E18, M12 and CS17 figures; BH23's ε–f_disk coefficients.
- Any S4G Bar/T statistic; Laurikainen et al. 2007 beyond its abstract; Gadotti 2008; Elmegreen & Elmegreen
  1985; Christodoulou et al. 1995; Toomre 1981; S08 beyond its abstract; BHG16 §4.3–4.4.
- Single-fetch items, not cross-checked: MJ07, NA10, M12, CS17, Z20, F25, A08, YS15, E19, DG16b, Wo24, E05 tables.

---

## Part B — the bar's lanes, its gas, and the arms' relation to the bar (reader 2)

Reading done by web search and web fetch only; nothing local was opened, no code run. Every number below was read
on a fetched page through the fetch tool's small model. "2×" means two fetches agreed (two reads of one HTML
rendering, or two renderings); "1×" means read once and not cross-checked. Table cells carry a short key such as
`[v:C09 §IV]`; each key expands to the full `[verified: …]` tag given once per source in B2. PDFs could not be
parsed by the tool (all PDF fetches failed), so every source is an HTML rendering (ar5iv, arxiv.org/html) or an
abstract page. Convention used throughout: "leading" = ahead of the bar's major axis in the sense of galactic
rotation; lanes lie inside the bar's corotation; a = bar semi-major axis; R_bar = bar radius as each paper defines
it; R_CR = corotation.

### B1 Summary tables

#### B1.1 Lanes

| Quantity | Value as printed | Definition, side, convention | Key, reads |
|---|---|---|---|
| Side of the lanes | "offset from the bar major axis towards its leading side" | shock loci, gas simulations; inside CR | `[v:A92 abstract]` 1× |
| Condition for offset lanes | x₂ and x₃ families "must not only exist but also cover a sufficient extent" | along the bar major axis | `[v:A92 abstract]` 1× |
| Lagrangian radius | r_L = (1.2 ± 0.2) a | needed for offset lanes of the observed shape | `[v:A92 abstract]` 1× |
| Shape vs strength | low axial ratio or low quadrupole: curved, "concave sides towards the bar major axis" | simulations | `[v:A92 abstract]` 1× |
| Gas outside the lanes | density "low, except for the centre and two narrow lanes" | simulations, no number | `[v:A92 abstract]` 1× |
| Curvature, observed (K02) | 0 to 20 °/kpc, error ±3 °/kpc, 9 galaxies | Δα = change of tangent angle per kpc along the lane, from just outside the circumnuclear region to near the bar end | `[v:K02 curvature section]` 1× |
| Curvature, observed (C09) | 0° to 111°, uncertainty ~15°, 55 galaxies, Q_b 0.089–0.730 | Δα = tangent-angle change per unit length × r(Q_b); dimensionless (degrees); constant-curvature stretch only | `[v:C09 §III–IV, Table 1]` 2× |
| Curvature vs Q_b, observed | no fit; an upper envelope: "strong bars cannot have curved dust lanes" | populated lower-left, empty upper-right of (Δα, Q_b) | `[v:C09 §IV, Fig. 1]` 2× |
| Curvature fit, SPH (C09) | Q_b − 0.087 (a/b) = (0.156 ± 0.020) − (0.119 ± 0.015) log₁₀Δα; ρ = 0.66 (0.58 with Q_b alone) | 238 simulated bars; a/b 1.5–4.5 | `[v:C09 §VI, eq. 3]` 2× |
| Curvature fit, grid hydro (KSK12) | Q_b + 0.10 ℛ = 0.87 − 0.37 log Δα | Δα as C09; ℛ = a/b here; a = 5 kpc, R_CR = 6 kpc, c_s = 10 km/s | `[v:KSK12 eq. 9–10]` 3× |
| Mean curvature × a, observed (SM15) | 0.12 to 2.37 (10 S⁴G galaxies, Q_b 0.09–0.63) | κ = \|y″\|/(1+y′²)^{3/2}, mean along the lane, × bar semi-major axis; from outside the nuclear ring to the kink where the arms begin | `[v:SM15 Table 1]` 1× |
| Curvature vs strength, fast/slow (SM15) | fast bars (1 < ℛ < 1.4): inverse relation; slow bars (ℛ > 1.4): constant; 1.90 (fast) vs 0.95 (slow) at lowest ellipticity | ℛ = R_CR/a here; no fitted equation printed; unit of the two numbers not stated by the read | `[v:SM15 abstract + results]` 2× (numbers 2×) |
| Lane offset from the bar axis | x_peak ≈ −2.5 kpc (early ridge) → ≈ −1 kpc (steady shock), model M30R25 | x = distance from the bar major axis of the density peak on the circle r = 1.5 kpc; bar along y; a = 5 kpc | `[v:KSK12 dust-lane section]` 1× (ar5iv) + 1× (definition) |
| Peak surface density in the lane | Σ_peak ~ 100 M⊙ pc⁻² against Σ₀ = 10 M⊙ pc⁻² initial | at r = 1.5 kpc, at the shock's strongest phase (t ~ 0.13–0.15 Gyr) | `[v:KSK12 dust-lane section]` 1× (Σ₀ 1×) |
| Sound-speed dependence | shocks "tend to move closer to the bar major axis as c_s increases"; lanes "at the leading side of the bar" | c_s 5–20 km/s | `[v:K12a abstract/intro]` 2× |
| Where lanes sit in orbit terms | at the transition from x₁ to x₂ flow; with c_s = 10 km/s, dx = 5 pc the transition orbit "almost coincides with the cusped orbit" | isothermal 2D hydro; position moves inward with resolution and c_s | `[v:S15a results]` 1× |
| Milky Way lanes | "precede the bar in its clockwise motion (as seen from the NGP)"; ends near l ≈ −5° and l ≈ +10°; bar angle 20° | CO l-b-v plus extinction; far lane above, near lane below the plane | `[v:M08]` 1× |
| Milky Way lane template | two straight segments, outer end on the bar's major axis, inner end on the bar's minor axis; from R ~ 3 kpc to R_CMZ = 300 pc; φ = 20° | a geometric model, not a fit | `[v:SB19 geometric model]` 2× |
| Lane width | not printed in any source read | — | — |

#### B1.2 Gas inside the bar; the nuclear ring

| Quantity | Value as printed | Definition | Key, reads |
|---|---|---|---|
| Share of area / H₂ / SFR, bars | 10.5 % / 19.8 % / 16.4 % | 74 PHANGS galaxies (barred and unbarred together), within the ALMA field, ~1″ masks | `[v:Q21 Table 2]` 2× |
| Same, centres | 0.66 % / 17.4 % / 25.2 % | as above | `[v:Q21 Table 2]` 2× |
| Same, spiral arms; interarm; disc without spirals | 10.7/18.4/16.5 %; 33.0/16.8/13.9 %; 45.0/27.4/27.7 % | as above | `[v:Q21 Table 2]` 2× |
| Median Σ_mol: centre, bar, arm, interarm, disc | 106.1, 11.51, 9.903, 4.492, 4.120 M⊙ pc⁻² | 1.5 kpc hexagonal apertures | `[v:Q21 Table 3]` 2× |
| Median τ_dep: centre, bar, arm, interarm, disc | 1.177, 2.102, 1.788, 1.677, 1.565 Gyr | as above | `[v:Q21 Table 3]` 2× |
| Arm/interarm contrast | CO 2.78, SFR 2.47 (medians) | per galaxy ratio of mean surface densities | `[v:Q21 §4.4]` 1× |
| Bars as deserts | "bars are not always deserts … they show large diversity" | — | `[v:Q21 abstract]` 2× |
| Hα radial profile, SBb/SBbc | central peak ~10 % of Hα flux; ~50 % in the outer peak's radial range; a dip between | mean normalised profiles in r/r₂₄; T = 3, 4; 313 galaxies in all | `[v:JBK09]` 1× |
| Desert line emission | [N II]/Hα 0.51–1.77 against 0.330 ± 0.013 for star formation | long-slit, 4 early-type barred spirals; "radial range swept out by the bar" | `[v:JP16]` 1× |
| Time since star formation stopped | ~1 Gyr typical, ~0.25 to > 4 Gyr; 21 galaxies | Hβ absorption in desert regions | `[v:JP18 abstract]` 1× |
| M95 bar region | ~4.2 kpc region (the bar's length) lacks H I, H₂ and star formation; none for 100–200 Myr; ring diameter ~0.7 kpc | UV, CO, H I maps | `[v:G19]` 1× |
| Four bars | 3 of 4 devoid of H I and H₂ between the centre and the bar end; NGC 2903 has H₂ along the bar | NGC 2903, 3351, 4579, 4725 | `[v:G20]` 1× |
| Molecular gas in 12 strong bars | detected along all 12; SFE "not systematically inhibited" | IRAM-30m pointings over the bar | `[v:DG21 abstract]` 1× |
| Where star formation sits | class A (centre only): S0; class B (bar ends, not along): early/intermediate spirals; class C (along the bar): late types | 433 Hα, 772 UV S⁴G bars, i < 65° | `[v:DG20 abstract]` 2× |
| FUV excess on the leading side | 21 %, 16 %, 11 % higher than trailing (early, intermediate, late spirals) | outer half of the bar ellipse, stacked GALEX | `[v:DG20 stacks]` 1× (side 2×) |
| Ring radius, upper bound | r_ring ≤ r_bar/4 (one exception, ESO 565-11) | ring = semi-major axis of the deprojected ridge; r_bar = radius of maximum ellipticity (2MASS H) | `[v:AINUR abstract, Fig. 6]` 2× |
| Ring radius vs torque | maxima ~2000 pc at Q_g = 0.1, ~500 pc at Q_g = 0.5; an envelope | Q_g = max(F_T^max/⟨F_R⟩) | `[v:AINUR §7.1]` 2× |
| Ring diameter / galaxy diameter | distribution peaks near D_r/D_o = 0.05 | — | `[v:AINUR §6.1]` 2× |
| Ring incidence | 20 ± 2 % of disc galaxies with −3 ≤ T ≤ 7 | star-forming nuclear rings | `[v:AINUR abstract]` 1× |
| Ring radius, simulations | r_ring/a = 0.062 Q_b^−0.46 (no self-gravity); 0.059 Q_b^−0.51 (self-gravity) | x₂-type rings; a = 5 kpc | `[v:KSK12 eq. 11]` 2× |
| Ring vs ILR | r_ring/r_ILR = 0.16 Q_b^−0.45; ring "not determined by the resonance" | — | `[v:KSK12]` 1× (statement 2×) |

#### B1.3 Arms against the bar

| Quantity | Value as printed | Definition | Key, reads |
|---|---|---|---|
| Arm start vs bar axis | "for all but two of the galaxies, the spirals appear to begin within 20° of the bar axis" | visual ⟨\|θ_S\|⟩, 12 barred galaxies, K_s; unsigned (no leading/trailing sign) | `[v:B04 Table 3 col. 11]` 2× |
| Stacked arms | a faint spiral overdensity "connecting to the bar ends and winding outwards" | stack of barred galaxies' stellar mass maps | `[v:N24 §4.1.1]` 1× |
| Q_b–Q_s, 17 galaxies | linear correlation above Q_b ≈ 0.3; strongest spirals only with Q_b ≥ 0.4 | maxima of F_T/⟨F_R⟩ for bar and spiral separately | `[v:B04]` 1× (threshold text garbled) |
| Q_b–Q_s, AAT 23 | r = 0.26, null rejected only at the 22.5 % level | as above | `[v:Bu09]` 2× |
| Q_b–Q_s, 177 combined | r = 0.35, r_sp = 0.31 | AAT + OSUBSGS + B04 | `[v:Bu09]` 2× |
| Q_b–Q_s, isolated | "do not show any trend or correlation"; 46 barred Sb–Sc | AMIGA | `[v:Du09]` 1× |
| Local forcing vs local A₂ | significant out to ~1.6 R_bar (r_s = 0.25, p = 0.008), 103 OSUBSGS; out to 1.4 R_bar, 23 AAT | Q_bar(r) from the bar-only density (m > 0 amplitudes zeroed beyond R_cut = R_bar) against the m = 2 amplitude A₂(r) | `[v:Sa10 abstract + text]` 3× |
| Bar vs spiral strength, S⁴G | Spearman ρ ≈ 0.42–0.62 (p < 0.01), all arm classes | 391 galaxies, i < 65° | `[v:DG19 §7.2, Fig. 14]` 1× |
| Pitch vs bar strength, S⁴G | ρ ≈ 0.18–0.2 (p < 0.01): "hardly … any dependence" | — | `[v:DG19 §7.1]` 2× |
| Pitch vs bar strength, SDSS | Pearson −0.36 (Yu & Ho 2020, as quoted by Smith et al. 2022) | not read at source | `[v:Sm22]` 1× |
| Arm vs bar contrast | Spearman ρ_F = 0.10, ρ_M = 0.29, ρ_G = 0.39 | C = 2.5 log(I_max/I_min) at 3.6 µm; 288 galaxies | `[v:Bi17]` 1× |
| Bar fraction by arm class | grand design 71 ± 5.2 %, multi-armed 59 ± 3.9 %, flocculent 77 ± 3.3 % | S⁴G, Buta et al. classes | `[v:DG19 §5.1]` 2× |
| Bar fraction by arm number | m = 2: 50 ± 1 %; each many-armed sample: 16–25 % | Galaxy Zoo 2, p_bar > 0.5; M⋆ ≥ 10¹⁰ M⊙, 0.02 ≤ z ≤ 0.055 | `[v:H17 §3.4.1]` 2× |
| Arm number shares | m = 2: 50.2 % of 3,889 spirals (m = 3: 20.7 %, 4: 9.2 %, 5+: 14.1 %, 1: 5.8 %) | same sample | `[v:H17 Table 1]` 1× |
| Arm class vs bar, by type | early types with bars "twice as likely to have symmetric spirals"; later types: same proportions | essay, no citation printed | `[v:E-essay]` 1× |
| Pattern speeds, kinematic | most bars and arms "rotate with different pattern speeds"; only 7 slow bars match their arms | 79 barred galaxies, Fabry–Pérot | `[v:Fo19]` 1× |
| ℛ = R_CR/R_bar | 1.01 ± 0.36 (T ≤ 4, 65 galaxies); 1.48 ± 0.62 (T ≥ 5, 35) | potential–density phase shift | `[v:BZ08]` 1× |
| Manifold arms | two-armed, trailing, from L₁/L₂ near the bar ends, same pattern speed as the bar; pitch grows with Q_{t,L1} | orbit theory | `[v:A09; A10 §6.4]` 1× each |

#### B1.4 The bar-driven two-armed response

| Quantity | Value as printed | Definition | Key, reads |
|---|---|---|---|
| Radial reach, observed | ~1.6 R_bar (OSUBSGS), 1.4 R_bar (AAT); bar forcing there "a few percent" | as in B1.3 | `[v:Sa10]` 3× |
| Radial reach, N-body | bar affects the arms within 1.5–2 bar radii; swing amplification explains them beyond | bar ~3 kpc, R_CR ≃ 4 kpc, Ω_b ≈ 47 km s⁻¹ kpc⁻¹ | `[v:Ba15 abstract, conclusions]` 2× |
| Radius of spiral maximum | r_s ≈ 2 r_b on average | radii of the Q_s and Q_b maxima | `[v:Bu09 Table 7 text]` 2× |
| Same, strongly barred | ⟨r(Q_b)/r(Q_s)⟩ = 0.57 ± 0.13 (7 galaxies, Q_b > 0.25) | as above | `[v:B04]` 1× |
| Bar m = 2 amplitude | A₂^max 0.23–0.41, at 0.76–0.94 r_bar | stacked S⁴G bars by mass/type bin, 3.6 µm | `[v:DG16 Table 5, Fig. 18]` 1× |
| Spiral m = 2 contrast | A₂s 0.063–1.220 (Q_s 0.031–0.497; Q_b 0.102–0.796) | maximum relative m = 2 intensity amplitude of the spiral after removing the bar; AAT 23 | `[v:Bu09]` 1× |
| Time behaviour | m = 2 arm amplitude cycles with a period ~200 Myr; grand design "only when the spirals connect with the ends of the bar" | N-body | `[v:Ba15]` 1× |
| Reconnection period | ≈ 63 Myr and ~125 Myr (model 1); ≈ 105 Myr (model 2) | bar meeting slower spiral modes | `[v:Hi20]` 1× |
| Reason for the limit | the bar's "quadrupole field decays rapidly with distance" | review | `[v:SM22 §3.1]` 1× |

### B2 Per-source notes (the full tags)

**A92** `[verified: Athanassoula 1992, MNRAS 259, 345, abstract only,
https://academic.oup.com/mnras/article/259/2/345/1057895]` Covers: the side, the x₂/x₃ condition, r_L, the sense
of curvature, the low density outside the lanes. Read: the publisher's abstract page only, once. The body (the
scanned pages with the model grid, the lane shapes, the shock strengths) was not read; ADS returned HTTP 405.
Later papers' accounts agree: C09 §I says lanes are "offset from the bar major axis" with "concavity pointing to
the bar major axis" and form "at the leading edge of the bar, roughly parallel to its major axis".

**K02** `[verified: Knapen, Pérez-Ramírez & Laine 2002, MNRAS 337, 808, arXiv:astro-ph/0207258, curvature
section, https://ar5iv.labs.arxiv.org/html/astro-ph/0207258]` Covers: the °/kpc definition, the 0–20 °/kpc range,
the ±3 °/kpc error, 9 galaxies, the first observed curvature–Q_b trend (clear with Q_b, weak with ellipticity),
"stronger bars host smaller rings" (ring diameter over D₂₅). No coefficient printed. Read 1×.

**C09** `[verified: Comerón, Martínez-Valpuesta, Knapen & Beckman 2009, ApJ 706, L256, arXiv:0910.5843, §II–VI,
Table 1, eq. 3, https://ar5iv.labs.arxiv.org/html/0910.5843 and https://arxiv.org/abs/0910.5843]` Covers: all C09
rows. Δα is the K02 tangent-angle change per unit length multiplied by r(Q_b), "thus a dimensionless quantity";
measured where curvature is constant, leaving out the innermost and outermost parts. Table 1 examples (1×): NGC
1530 Q_b 0.730, Δα 4°; NGC 613 0.401, 0°; NGC 1068 0.094, 111°; NGC 1300 0.537, 63°; NGC 1365 0.490, 64°; NGC
1097 0.279, 60°. The last three show how wide the spread is at high Q_b. Q_b uncertainty ~20 %. Simulations: 10⁵
isothermal SPH particles, pattern speeds 10–40 km s⁻¹ kpc⁻¹, a/b 1.5–4.5; sound speed not printed.

**SM15** `[verified: Sánchez-Menguiano et al. 2015, MNRAS 450, 2670, arXiv:1504.02232, abstract, method, Table 1,
https://ar5iv.labs.arxiv.org/html/1504.02232 and https://arxiv.org/abs/1504.02232]` Covers: the SM15 rows. Table
1 (1×), κ·a per lane: NGC 3504 1.35/1.54; 4123 0.77/0.77; 4303 1.40/1.14; 4314 0.20; 4457 2.37; 4548 0.46/1.29;
4579 1.70; 5921 0.12/1.22; 7552 1.16/0.34; 7723 0.77. Median of the 16 lane values = 1.15 [derived by this reader;
not printed]. "Weak bars with straight dust lanes are candidates for slow bars." The two lanes of one galaxy can
differ by a factor of ten (NGC 5921), which bounds what any one-parameter law can do.

**KSK12** `[verified: Kim, Seo & Kim 2012, ApJ 758, 14, arXiv:1208.1821, model section, eq. 9–11, dust-lane
section, https://arxiv.org/html/1208.1821 and https://ar5iv.labs.arxiv.org/html/1208.1821]` Covers: the KSK12
rows. Ω_b = 33 km s⁻¹ kpc⁻¹, R_CR = 6 kpc, a = 5 kpc (R_CR/a = 1.2 [derived]), c_s = 10 km/s, Q_b 0.02–0.67, Q_b
= 0.44 f_bar^0.87 (a/b − 1) for Ferrers n = 1 (1×). Lanes "approximately follow one of x₁-orbits and tend to be
more straight under a stronger and more elongated bar", insensitive to self-gravity. Ring radii ~0.4–1.3 kpc
(1×). Evaluating eq. 11 without self-gravity gives r_ring/a = 0.18, 0.13, 0.094, 0.078 at Q_b = 0.1, 0.2, 0.4,
0.6 [derived]. x_peak = −1 kpc on r = 1.5 kpc puts that point 42° from the bar's major axis at r = 0.3 a
[derived]. Evaluating eq. 10 at ℛ = 2.5 gives Δα ≈ 25°, 14°, 3.9° at Q_b = 0.1, 0.2, 0.4 [derived]. One read's
summary said the lanes are on the "trailing side"; no verbatim sentence supported it on re-reading (see B4).

**K12a** `[verified: Kim, Seo, Stone, Yoon & Teuben 2012, ApJ 747, 60, arXiv:1112.6055, abstract and
introduction only, https://arxiv.org/html/1112.6055]` Covers: leading side, the sound-speed trend, rings shrink
with c_s, inflow > 0.01 M⊙ yr⁻¹ at large c_s. Sections 2–3 were not delivered by the tool (three attempts).

**S15a/b/c** `[verified: Sormani, Binney & Magorrian 2015, MNRAS 449, 2421, arXiv:1502.02740,
https://ar5iv.labs.arxiv.org/html/1502.02740]`, `[verified: same authors 2015, paper II, arXiv:1504.04807,
https://arxiv.org/html/1504.04807]`, `[verified: same authors 2015, paper III, arXiv:1507.03078,
https://arxiv.org/html/1507.03078]` Cover: the orbit reading of the lanes. Paper I potential: R_ILR = 0.6 kpc,
R_CR = 3.7 kpc, Ω_p = 63 km s⁻¹ kpc⁻¹; "two thin offset shocks"; transition point and x₂ disc size "depend
strongly on both the resolution and the sound speed". Paper II: arms as librations about closed orbits, steady in
the bar frame. Paper III: stronger quadrupole shrinks the x₂ disc; Ω_p = 40 gives R_CR = 5.60 kpc; four arms
outside the shock region. No density contrast is printed in the text read (a "2–3×" in one read was the tool's
own figure-guess and is discarded). All 1×.

**F17** `[verified: Fragkoudi, Athanassoula & Bosma 2016, MNRAS 462, L41, arXiv:1606.04540,
https://arxiv.org/html/1606.04540]` Covers: nothing on lane shape. Peanut bulges cut the inflow by a factor ~2
(weak) to ~4 (strong); bar ≈ 5 kpc, c_s = 10 km/s, 50 pc grid. 1×. The brief's "2017" is this 2016 letter.

**M08** `[verified: Marshall, Fux, Robin & Reylé 2008, A&A 477, L21, arXiv:0711.2471,
https://ar5iv.arxiv.org/html/0711.2471]` Covers: the Milky Way side and longitudes. 1×; lengths, widths and
contrasts are not printed.

**SB19** `[verified: Sormani & Barnes 2019, MNRAS 484, 1213, arXiv:1901.00867, geometric model,
https://ar5iv.labs.arxiv.org/html/1901.00867]` Covers: the straight-segment template (2×), inflow 1.2 (+0.7,
−0.8) near lane and 1.5 (+0.9, −1.0) far lane, 2.7 (+1.5, −1.7) M⊙ yr⁻¹ total (1× plus search snippet). Gas
velocity in the bar frame "approximately parallel to the dust lanes".

**Q21** `[verified: Querejeta et al. 2021, A&A 656, A133, arXiv:2109.04491, Tables 2–3, §4.4,
https://ar5iv.labs.arxiv.org/html/2109.04491 and https://arxiv.org/html/2109.04491]` Covers: all Q21 rows; the
two renderings agree digit for digit. Bar mask = an ellipse from 3.6 µm; bar ends are not separated in Table 2;
the percentages include unbarred galaxies, so the bar's share within barred galaxies is larger than 19.8 % and is
not printed. Per unit area bars hold 1.9× the sample mean H₂ and interarm 0.51× [derived from Table 2].

**JBK09** `[verified: James, Bretherton & Knapen 2009, A&A 501, 207, arXiv:0904.4261,
https://ar5iv.labs.arxiv.org/html/0904.4261]` 1×. The brief names "Percival" as third author; the page says
Knapen. **JP16** `[verified: James & Percival 2016, MNRAS 457, 917, arXiv:1601.04706,
https://ar5iv.labs.arxiv.org/html/1601.04706]` 1×. **JP18** `[verified: James & Percival 2018, MNRAS 474, 3101,
arXiv:1711.10537, abstract, https://arxiv.org/abs/1711.10537]` 1× (the tool paraphrased the abstract).

**G19** `[verified: George et al. 2019, A&A 621, L4, arXiv:1812.04178,
https://ar5iv.labs.arxiv.org/html/1812.04178]` 1×. **G20** `[verified: George et al. 2020, A&A 644, A79,
arXiv:2010.04005, https://ar5iv.labs.arxiv.org/html/2010.04005]` 1×. **DG21** `[verified: Díaz-García et al.
2021, A&A 654, A135, arXiv:2106.13099, abstract, https://arxiv.org/abs/2106.13099]` 1×.

**DG20** `[verified: Díaz-García et al. 2020, A&A 644, A38, arXiv:2009.00962, abstract, Table 1, Figs. 11–13,
https://ar5iv.labs.arxiv.org/html/2009.00962 and https://arxiv.org/abs/2009.00962]` Covers: classes, side,
percentages. Class shares read off figures by the tool (1×, approximate): class C ~60–75 % in late types and
~10–20 % in S0–Sa; class A ≤ 20 % in late types. "UV emission … dominates on their leading side, as witnessed in
simulations" (abstract, 2×). Inner-ringed galaxies show the mid-bar UV/Hα deficit whether barred or not.

**AINUR** `[verified: Comerón et al. 2010, MNRAS 402, 2462, arXiv:0908.0272, abstract, §4.3, §6, §7.1, Fig. 6,
https://ar5iv.labs.arxiv.org/html/0908.0272]` Covers: all ring rows. 113 rings in 107 galaxies, 78 barred discs,
18 unbarred. "The maximum relative size of a star-forming nuclear ring is inversely proportional to … Q_g"; it is
an envelope, not a relation: small Q_g allows all sizes. No typical r_ring/r_bar is printed.

**B04** `[verified: Block et al. 2004, AJ 128, 183, arXiv:astro-ph/0405227, Table 3,
https://ar5iv.labs.arxiv.org/html/astro-ph/0405227]` Covers: θ_S, the correlation, the radius ratio. θ_S = "the
angle between the bar and the inner-limit spiral points", estimated by eye per arm; exceptions NGC 5033 and NGC
7723 (⟨|θ_S|⟩ above 40°). The authors read the correlation as bars and spirals growing together with one pattern
speed. Threshold sentences came through garbled ("Q_b ≥ 0.2", "<< 0.3"); Bu09's account gives "little correlation"
below 0.3.

**Bu09** `[verified: Buta et al. 2009, AJ 137, 4487, arXiv:0903.2008, Tables 4, 7,
https://ar5iv.labs.arxiv.org/html/0903.2008]` Covers: its rows. "Bars may drive spirals only when (a) the bar is
young and growing in strength itself, or (b) there is ample gas in the bar-spiral system." Buta et al. 2005 is
described there as "a hint of the same correlation"; not read at source.

**Du09** `[verified: Durbala et al. 2009, MNRAS 397, 1756, arXiv:0905.2340,
https://ar5iv.labs.arxiv.org/html/0905.2340]` 1×. Means (barred, N = 46): Sb Q_b 0.261 ± 0.022, Q_s 0.146 ±
0.011; Sbc 0.206 ± 0.031, 0.164 ± 0.026; Sc 0.242 ± 0.033, 0.199 ± 0.013. The m = 2 arms "appear joined to the
end regions of the bar".

**Sa10** `[verified: Salo, Laurikainen, Buta & Knapen 2010, ApJ 715, L56, arXiv:1004.5463, abstract and text,
https://arxiv.org/abs/1004.5463 and https://ar5iv.labs.arxiv.org/html/1004.5463]` Covers: the local correlation.
Q_bar(r) = max|F_T(r,φ)|/⟨|F_R(r,φ)|⟩ from the bar-only density. "The correlation is very strong just beyond the
bar, and stays statistically significant until ∼1.6 R_bar." Inside the range the spirals "are expected to share
the … pattern speed of the bar"; beyond, "independent structures … a slower pattern speed … or … short-lived
transient wave packets". No amplitude-against-radius table is printed. The brief's "about 1.5 bar lengths" is not
on the page; 1.6 and 1.4 are.

**DG19** `[verified: Díaz-García, Salo, Knapen & Herrera-Endoqui 2019, A&A 631, A94, arXiv:1908.04246, §5.1, §7,
§9.3, Table 2, https://ar5iv.labs.arxiv.org/html/1908.04246]` Covers: its rows. "We do not find observational
evidence that spiral arms are driven by stellar bars or by invariant manifolds." Pitch for 4 ≤ T < 6: barred 19.7°
± 0.6°, unbarred 19.8° ± 0.7° (1×). The bar–spiral strength link is read as a shared property of the disc.

**DG16** `[verified: Díaz-García, Salo & Laurikainen 2016, A&A 596, A84, arXiv:1607.07317, §3–4, Table 5, Fig.
18, https://arxiv.org/html/1607.07317]` 1×. 748 barred galaxies scaled to bar length and orientation and
reflected "to make the spiral arms wind clockwise"; outer structure fades in the stacks. No A₂ values at 1.5 or 2
r_bar are tabulated.

**Bi17** `[verified: Bittner et al. 2017, MNRAS 471, 1070, arXiv:1706.09904,
https://ar5iv.labs.arxiv.org/html/1706.09904]` 1×. Medians read off a figure by the tool (approximate): arm
contrast ~0.3 mag flocculent, ~0.5 mag multi-armed and grand design; bar contrast ~0.4, ~0.6, ~0.7 mag.

**H17** `[verified: Hart et al. 2017, MNRAS 468, 1850, arXiv:1703.02053, §3.4.1, Table 1,
https://arxiv.org/html/1703.02053]` Bar fractions 2× (page and search snippet agree). **SM22** `[verified:
Sellwood & Masters 2022, ARA&A 60, 73, arXiv:2110.05615, §2.2, §3.1,
https://ar5iv.labs.arxiv.org/html/2110.05615]` 1×: 62 % two arms, 20 % three, 6.5 % four in a luminosity-limited
sample the review cites; outer spirals "frequently have a different pattern speed from that of the bar"; "an
apparent connection between the spiral and bar lasts for a very large fraction of the beat period". **Sm22**
`[verified: Smith, Giroux & Struck 2022, AJ 164, 146, arXiv:2208.05995, https://arxiv.org/html/2208.05995]` 1×:
the only account of Yu & Ho 2020 read. **E-essay** `[verified: Elmegreen, NED Level 5 essay "Galaxies, Spiral,
Structure", https://ned.ipac.caltech.edu/level5/ESSAYS/Elmgreen/elmgreen.html]` 1×.

**A09, A10** `[verified: Athanassoula et al. 2009, MNRAS 400, 1706, arXiv:0910.0757, Fig. 5,
https://ar5iv.labs.arxiv.org/html/0910.0757]`, `[verified: Athanassoula et al. 2010, MNRAS 407, 1433,
arXiv:1005.2943, §4, §6, https://arxiv.org/html/1005.2943]` 1× each. Q_{t,L1} = Q_t(r = r_L). Weak forcing gives
R₁/R₁′ rings, stronger gives spirals; arm density "should decrease with increasing distance from the centre";
the manifolds wind "roughly 260°" before turning inward. No pitch values are printed in the text read; no
amplitude prediction ("unless further work concerning the trapping is made").

**SS88** `[verified: Sellwood & Sparke 1988, MNRAS 231, 25P, abstract via OSTI,
https://www.osti.gov/etdeweb/biblio/5190923]` 1×, paraphrased by the tool: arms slower than the bar; the spiral
keeps detaching from and rejoining the bar while looking like a barred spiral at all times.

**Fo19, Ba15, Hi20, BZ08, N24** `[verified: Font et al. 2019, MNRAS 482, 5362, arXiv:1901.04725,
https://ar5iv.labs.arxiv.org/html/1901.04725]`; `[verified: Baba 2015, MNRAS 454, 2954, arXiv:1509.07239,
https://ar5iv.labs.arxiv.org/html/1509.07239]`; `[verified: Hilmi et al. 2020, MNRAS 497, 933, arXiv:2003.05457,
https://ar5iv.labs.arxiv.org/html/2003.05457]`; `[verified: Buta & Zhang, arXiv:0812.2959,
https://arxiv.org/html/0812.2959]`; `[verified: Neumann et al. 2024, MNRAS 534, 2438, arXiv:2409.18180, §4.1.1,
https://arxiv.org/html/2409.18180]`. All 1× except Ba15's radial range (page and search snippet agree). Fo19:
"no galaxy … that has a strong bar with open arms". Hi20: apparent bar length swings by ~10 % (model 1) to ~100 %
(model 2) as arms connect; ℛ 1.02 and 1.75 in the two models.

### B3 What a model could adopt

**Lane template.** Two lanes, point-symmetric, on the leading side of the bar (A92, K12a, M08; DG20's FUV excess
is on the same side). Each runs from the bar's major axis near the bar's end to the nuclear ring, reaching it near
the bar's minor axis (SB19's end points; K02 and SM15 measure over the same stretch), concave towards the bar's
major axis (A92, C09). Inner radius: the ring, r_ring ≤ a/4 (AINUR), with KSK12's eq. 11 as a strength law.
- *Adopt (named L-arc):* a constant-curvature arc between those end points with dimensionless curvature κ·a drawn
  or set from SM15 (observed 0.12–2.37, median 1.15 [derived]), reduced with Q_b for fast bars. Predicts straight
  lanes at high Q_b and a spread at low Q_b. Shown wrong by a strong bar with strongly curved lanes outside the
  spread: C09's Table 1 already holds NGC 1300 and NGC 1365 (Δα 63°, 64° at Q_b ≈ 0.5), so the law must be an
  envelope with scatter, not a function.
- *Alternative L-straight:* SB19's straight segment. No curvature parameter; right for strong bars, wrong for
  weak ones by construction.
- *Alternative L-fit:* KSK12 eq. 10 (or C09 eq. 3) for Δα(Q_b, a/b). Sourced coefficients, but the two fits
  disagree in the sign of the axis-ratio term (B4), and both come from idealised isothermal gas.
- *Alternative L-orbit:* the lane as a segment of one x₁ orbit (KSK12, S15a). Needs the potential's orbits; the
  position depends on sound speed and resolution (S15a), so it is not a fixed curve.
- Not sourced and so free: the lane's width, and its compression beyond KSK12's single Σ_peak ~ 100 against 10
  M⊙ pc⁻² (1×). ℛ = 1.2 in the model is inside SM15's fast-bar range, where the strength dependence holds.

**Gas inside the bar.** Sources disagree on a number (B4). What all support: a strong central concentration
(Q21: 17.4 % of H₂ in 0.66 % of area), low gas off the lanes in early-type strong bars (A92, G19, G20, JP16), gas
along the bar in late types (DG20 class C; DG21). *Adopt:* depletion off the lanes as a parameter that grows
with bar strength and earlier type, not a constant; *alternative:* no depletion, lanes only (Q21's medians, bar
11.5 against interarm 4.5 M⊙ pc⁻² at 1.5 kpc, do not show a desert at that resolution). A map of H₂ across a
bar at sub-kpc resolution would decide it; none was read.

**Arm phases.** *Adopt (named P-tied-2):* tie only the m = 2 mode's phase to the bar's ends, with the arm
starting within about ±20° of the bar axis (B04, 10 of 12), and only inside ~1.5 R_bar; leave m ≥ 3 and all modes
beyond that radius random. Supported by B04, Du09's "joined to the end regions", N24's stack, Sa10's range, Ba15.
Predicts two-armed symmetry near the bar and bar fractions higher among two-armed spirals (H17). Shown wrong if
measured θ_S were uniform; B04 is 12 galaxies, by eye, unsigned.
- *Alternative P-manifold:* arms rigidly attached at L₁/L₂, two, trailing, bar's pattern speed, pitch rising with
  bar strength (A09, A10). DG19 and Fo19 both report the pitch prediction is not seen.
- *Alternative P-free:* phases independent of the bar (the model's present state). Consistent with SS88, Fo19,
  Hi20 on pattern speeds; but SM22 notes the apparent connection lasts most of the beat period, so a random
  instant still tends to look connected. P-free under-predicts that.

**Where a bar-driven m = 2 dominates.** *Adopt:* R ≤ ~1.5 R_bar (Sa10: 1.6 and 1.4; Ba15: 1.5–2), which is
~1.25 R_CR for R_CR = 1.2 R_bar [derived]; many-armed, locally amplified arms beyond. *Alternative:* out to 2
R_bar (Bu09's r_s ≈ 2 r_b; B04's 0.57 ratio), which for a flat rotation curve is close to the bar's outer
Lindblad resonance [recall — NOT READ: R_OLR ≈ 1.7 R_CR for a flat curve]. No source read prints the driven
amplitude as a function of radius; the amplitude should scale with local bar forcing (Sa10) and is of the order of
A₂s ~ 0.06–1.2 at maximum (Bu09). A measured A₂(r/R_bar) profile for barred two-armed spirals would test it.

### B4 Conflicts between sources

1. Axis-ratio term: C09 eq. 3 has Q_b − 0.087 (a/b) on the left; KSK12 eq. 10 has Q_b + 0.10 ℛ. At fixed Q_b
   the first makes more elongated bars more curved, the second straighter. Both were read 2× or more as printed.
2. Curvature against strength: A92 and K02 state a trend; C09 finds only an upper envelope with a spread beyond
   the errors; SM15 finds the trend only for fast bars and none for slow bars.
3. Ring radius: K02 ties it to the extent of x₂ orbits; KSK12 and K12a say the ring is set by angular momentum
   lost at the shocks, not by the ILR. Both agree stronger bars have smaller rings, as does AINUR's envelope.
4. Bars as deserts: JBK09, JP16, G19, G20 (cleared bar regions) against Q21 ("not always deserts", 19.8 % of
   H₂) and DG21 (CO in all 12 strong bars). Samples, tracers and resolutions differ; DG20's type dependence may
   reconcile them but no source says so in numbers.
5. Bar–spiral strength: B04 (correlated above Q_b ≈ 0.3), DG19 (ρ 0.42–0.62), Bi17 (ρ_G = 0.39) against Bu09
   (r = 0.26, not significant, AAT) and Du09 (none). Sa10 finds it locally, not in the maxima.
6. Pitch against bar strength: manifolds predict more open arms in stronger bars (A09); DG19 ρ ≈ 0.18–0.2; Fo19
   strong bars have only tight arms; Yu & Ho via Sm22 Pearson −0.36.
7. Pattern speeds: B04 and A10 (shared) against SS88, Fo19, Hi20, SM22 (arms slower); BZ08 shows both cases.
8. Arm class and bars: H17 (bars in 50 % of two-armed, 16–25 % of many-armed) against DG19 (flocculent the most
   barred at 77 %, multi-armed least at 59 %). Different samples, bar definitions and mass ranges.
9. ℛ: A92 1.2 ± 0.2 from lane shapes; BZ08 1.01 ± 0.36 early, 1.48 ± 0.62 late.
10. Transcription: one read of KSK12 said "trailing side"; A92, K12a, M08 and S15c's read say leading, and no
    verbatim KSK12 sentence with either word was returned. Treated as the tool's error.
11. Units: a search snippet gave C09's Δα in °/kpc; the page says dimensionless (K02's is °/kpc).

### B5 What could not be read

- Athanassoula 1992 beyond its abstract (scanned; ADS 405). Shock strengths, lane offsets, the model grid: unread.
- Kim et al. 2012a sections 2–3 (the tool returned only the abstract and introduction, three times).
- Romero-Gómez et al. 2006, 2007: not opened; known only through A09/A10.
- Yu & Ho 2020: no arXiv page found (title search returned nothing); known only through Sm22.
- Elmegreen & Elmegreen 1985, 1989, 1995: ADS 405. A search snippet of the 1995 abstract says the two inner
  symmetric arms end at twice the bar radius and inner two-arm symmetry holds inside ~0.5 R₂₅ [recall — NOT READ:
  snippet only, page not opened].
- Buta et al. 2005; Rautiainen, Salo & Laurikainen 2008 (snippet: R_CR/R_bar from 1.1 to 1.7, S0 to Sc [recall —
  NOT READ]); Sormani et al. 2018; Hunt et al.: not opened.
- Sellwood & Sparke 1988 body; James & Percival 2018 body; Díaz-García et al. 2021 body: abstracts only.
- Publisher pages for A&A (403) and all PDFs (unparsed): Marshall 2008, George 2020, Díaz-García 2019 were read
  on ar5iv instead. The failed PDF fetches left copies in the tool-results folder; they were not opened.
- Not found in anything read: a lane width; a shock compression other than KSK12's one figure; a signed
  distribution of the arm-start angle; the driven m = 2 amplitude against r/R_bar; the bar-end share of gas.
