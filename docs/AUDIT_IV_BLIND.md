<!-- Audit IV (S43, D194): the blind reading of the forbidden-line target (#117) and the diffuse gas's line ratios (#119), by a read-only agent forbidden the repository, copied verbatim from the S43 scratchpad so a row can cite it. The row itself is the next session's to enter (B3); AUDIT_IV.md section 4 says what the session verified at the sources (Zhao et al. 2026 Eqs. 5, 8, 9.1, 9.2 read on 2026-09-30) and what it did not. -->

# Audit IV (S43) — blind reader's report: Targets A and B

## Header — what was not opened

Nothing under `D:\Users\Semaphore\Documents\Projects\` was opened, listed, searched, grepped or run; no git command, no test, no project file, no model output, no earlier session document. I have not seen any model number for [N II]/Hα, [S II]/Hα, [O III]/Hα, per region or per ring, nor the model's WIM temperature. Tools used: WebSearch, WebFetch only.

Two mechanical limits the auditor should know:
1. PDF page rendering was unavailable in this environment (no poppler), and the fetch tool's summariser refused verbatim table dumps twice on copyright grounds. All "READ" labels below therefore mean *read through a text rendering of the primary paper (ar5iv / arXiv-HTML / IOP full text / jina text-extraction of the arXiv PDF), with the sentence or number returned to me by the fetch tool*. Where I obtained the same number from two or more independent renderings of the same paper I say so; where renderings disagreed I say so and do not use the number.
2. Madsen, Reynolds & Haffner (2006) Table 2 was rendered four times (ar5iv ×2, jina ×2); the row-level values differed between renderings (e.g. S264 [N II]/Hα came back as 0.20, 0.25, 0.30), the fourth attempt admitted the rows were "not fully legible". Only the paper's own summary sentences (averages 0.27 and 0.11), which came back identically every time, are used as READ. The row scatter is given as approximate and flagged.

Label key, as in Audit III: **READ** = read in the primary this session (URL + location); **READ second-hand** = read quoted elsewhere; **NOT READ** = memory/inference, context only.

---

# Target A — the row: a Milky-Way HII-region line-ratio statistic against galactocentric radius

## Adopted target (stated first)

**Ratio:** [N II] λ6583 / Hα (intrinsic; for the comparison the correction is immaterial — the lines are 20 Å apart and every Galactic source below leaves this ratio uncorrected).

**Form:** 1 (a gradient), with a value-at-R₀ as a stated secondary check (form 3 if the session wants both; only the gradient is proposed as the row).

**Row statistic:** the slope of an unweighted straight line in log₁₀([N II]6583/Hα) against R (kpc) through the model's per-ring Hα-luminosity-weighted means, **using only rings whose centres lie between 8.2 and 15.4 kpc** (the source's radial coverage; do not extend to 3 kpc).

**Central value:** d log([N II]/Hα)/dR = **−0.025 dex kpc⁻¹**.
**1σ (propagated formal) window:** ±0.009 → **[−0.034, −0.016] dex kpc⁻¹**.
**Recommended acceptance window (stated, ~2σ):** **[−0.045, −0.005] dex kpc⁻¹**. Reason for widening: the source fits binned medians weighted by the bin scatter, so its formal error understates the population's own scatter; its two-zone alternative fit gives −0.028 ± 0.009 outside 9.65 kpc and −0.077 ± 0.018 inside; and the model's rings will not coincide with the source's bins.

**Source:** Zhao, Y., Zhang, W., Ma, L., Wen, S., et al. 2026, *AJ* 172, 168, "Galactic HII regions in LAMOST Medium-Resolution Spectroscopic Survey of Nebulae", arXiv:2607.27662 (submitted 30 July 2026). https://arxiv.org/html/2607.27662 and https://arxiv.org/abs/2607.27662 .

**How the number is obtained (the arithmetic is exact, not a model conversion):**
- READ, Eq. 5 (§IV.4.3): "12+log(O/H) = 8.90 + 0.57 × log([N II]/Hα)", stated valid for −2.5 < log([N II]/Hα) < −0.3 (this is the Pettini & Pagel 2004 N2 calibration — the rendering garbled the citation as "Pettini & Pagano"; the coefficients and the validity range are PP04's). Because the paper's "oxygen abundance" is a *linear* function of log([N II]/Hα) and nothing else, every O/H-vs-R fit in the paper is an [N II]/Hα-vs-R fit divided by 0.57.
- READ, Eq. 8 (§V, global weighted fit, all regions with distances, 8.16–15.36 kpc): "12+log(O/H) = 8.763(±0.046) − 0.014(±0.005) × R_gal". → d log([N II]/Hα)/dR = −0.014/0.57 = **−0.0246 ± 0.0088 dex kpc⁻¹**.
- READ, Eq. 9.1 (inner, R_gal ≤ 9.65 kpc): "9.025(±0.087) − 0.044(±0.010) × R_gal" → −0.077 ± 0.018 dex kpc⁻¹.
- READ, Eq. 9.2 (outer, R_gal > 9.65 kpc): "8.792(±0.054) − 0.016(±0.005) × R_gal" → −0.028 ± 0.009 dex kpc⁻¹.
- READ, §V.1: "[N II]/Hα and [S II]/Hα show negative radial gradients with increasing Rgal." and "The fitting slope of [S II]/[N II] is positive, but it is very shallow and the associated error is relatively large."
- READ, Fig. 9 caption: "Black squares represent the median values of binned H II regions with scatter shown as error bars. Black lines correspond to linear fits to the median values, using errors as weights."

**The sample (READ unless marked):**
- 280 WISE-catalogue HII regions and candidates in the outer Galaxy observed by LAMOST MRS-N; 255 confirmed as HII regions on a [N II]/Hα–[S II]/Hα diagnostic diagram (§III.3, Fig. 4; 90 previously "Known", 165 newly classified).
- Distances (§IV.4.4): "In total, distances have been estimated for 243 H II regions in our sample, including 6 dmaser,wise, 145 dOB and 92 dkin,lamost" — i.e. 6 maser parallaxes, 145 Gaia EDR3 OB-star parallaxes, 92 kinematic. R_gal 8.16–15.36 kpc. (One rendering said 246 regions have O/H; the discrepancy 243/246 is the rendering's, not resolved.)
- R₀: "adopting a Galactocentric distance of the sun of R⊙ = 8.15 kpc" (§IV.4.4). **Restated at R₀ = 8.2 kpc:** every R_gal shifts by ≤ +0.05 kpc; the slope is unchanged to first order, and a value read off the fit at R₀ moves by 0.05 kpc × 0.025 dex kpc⁻¹ = 0.001 dex — negligible.
- Per-region spectrum (§III.2): spectra resampled to 3′×3′ bins keeping the highest-S/N spectrum per bin, then "For each source, stack resampled spectra within its radius and apply Gaussian fitting to stacked spectra" — the radius being the WISE catalogue radius. So the ratio is a **flux-summed spectrum over the whole projected region**, not a slit through one knot; it is the closest Galactic analogue to the model's per-region luminosity ratio.
- Line definitions (§III.2): "we define F(Hα), F([N II]), and F([S II]) as the integrated fluxes of Hα, [N II]λ6584, and [S II]λλ6717,6731 emission lines." — [S II] is the doublet sum.
- Extinction: no absolute flux calibration; relative calibration against the OH λ6554 sky line (§III.1, Eq. 1); no reddening correction; the N2 method is chosen partly for "minimizing the effects of extinction correction" (§IV.3). For 6563/6583 the differential reddening is < 1 % at any plausible A_V (NOT READ, arithmetic on any standard law).
- Medians of the confirmed sample (Fig. 5, red dashed lines; also §V.5/Fig. 13): [N II]/Hα ≈ 0.31, [S II]/Hα ≈ 0.15 (the uncertainties are printed in the figure panels, not in text; not recovered).
- Other fits in the paper, for context: Eq. 6, T_e = 5015(±856) + 344.6(±78.1) × R_gal K (227 regions; T_e from the Hα–[N II] line-width difference, a crude method); Eq. 7, log n_e = 3.485(±0.432) − 0.143(±0.041) R_gal.

**Value at R₀ (secondary check, not the row):** [N II]6583/Hα at R = 8.2 kpc, central **0.27**, window **0.20–0.40** (log: −0.57, +0.17/−0.13 dex). Source: Madsen, Reynolds & Haffner 2006, ApJ 652, 401 (arXiv astro-ph/0609558; https://ar5iv.labs.arxiv.org/html/astro-ph/0609558), §4/Table 2, READ in four renderings identically: "For [N II]/Hα, we find that the average value for the O-star H II regions is 0.27" and "For [S II]/Hα, we find an average value of 0.11 for the O-star H II regions" ([S II] = λ6716 alone; WHAM 1° beam, so whole regions; 12–13 O-star regions, all within ~2–3 kpc of the Sun, so R_G ≈ 8.2–9.7 kpc — distances NOT READ, from memory of the regions' names: λ Ori/S264, Barnard's Loop/S276, NGC 1499/S220, ξ Per, α Cam, σ Ori, CMa OB1/S292 at ≲1 kpc; W4 and S132 at ~2–3.5 kpc, l ≈ 103°–135°, giving R_G ≈ 9.6–9.7 kpc). The window 0.20–0.40 is the row-level spread every rendering returned (minimum 0.20–0.23, maximum 0.40 for Sivan 4; per-row errors ±0.04–0.06) — **flagged: rendering-uncertain, to be re-read from the PDF if the session wants a tighter window**. The window also contains the LAMOST whole-sample median 0.31 and, at its upper edge, the LAMOST global fit evaluated at 8.2 kpc: 10^[(8.763 − 0.014×8.2 − 8.90)/0.57] = 10^(−0.442) = 0.36 (intercept ±0.046 dex in O/H → ±0.081 dex → 0.30–0.44).

## What each candidate says (sentences and locations)

1. **Zhao et al. 2026 (LAMOST MRS-N HII regions)** — above. The only Galactic source found that (a) fits line ratios of a *population* of whole HII regions against R, (b) publishes slopes with errors, (c) spans > 7 kpc of radius.
2. **Madsen, Reynolds & Haffner 2006** — READ: averages 0.27 ([N II]/Hα), 0.11 ([S II]λ6716/Hα), 0.18 ([O III]/Hα), 0.018 (He I/Hα) for O-star HII regions (Table 2 summary; the 0.18 and 0.018 came back in two renderings). READ, §VI.2.1: "The [N II]/Hα data suggest that most of the emission from the H II regions is relatively cool (6000 K < T < 7000 K)". READ, extinction: "The corrections to the line ratios (Table 2) are not very sensitive to moderate values of A(V)" (§IV; A(V) from Hα/Hβ where measured). No galactocentric distances tabulated; no gradient.
3. **Haffner, Reynolds & Tufte 1999, ApJ 523, 223** (https://iopscience.iop.org/article/10.1086/307734/fulltext/40172.text.html; arXiv astro-ph/9904143) — READ, §3.3: toward NGC 7000 (I_Hα = 800 R) "[S II]/Hα = 0.06 and [N II]/Hα = 0.20"; NGC 1499 (six pointings, I_Hα > 50 R): [S II]/Hα = 0.14, [N II]/Hα = 0.39. Two bright regions only; no radial information.
4. **Haffner et al. 2009, RvMP 81, 969** (https://ned.ipac.caltech.edu/level5/Sept09/Haffner/Haffner2.html) — READ, §2.3: "bright classical H II regions all cluster near the lower left corner of the plot, [S II]/Hα ≈ 0.1", "[N II]/Hα ≈ 0.25, where T_e = 6000–7000 K and S⁺/S ≈ 0.25". A review; maps to Madsen 2006 / Haffner 1999.
5. **Wen et al. 2024/25, "Diffuse Ionized Gas in the Anti-center of the Milky Way"** (LAMOST MRS-N DIG; https://arxiv.org/html/2412.05692v1) — READ: 17 821 DIG spectra, |z| < 0.3 kpc, R₀ = 8.34 kpc; DIG peaks [N II]/Hα 0.33, [S II]/Hα 0.38; comparison HII values 0.31 and 0.20; "[N II]/Hα and [S II]/Hα do not exhibit a consistent, monotonic decrease with increasing Galactocentric distance" (peak at ≈ 9.1 kpc, interarm). DIG, not HII regions — no row.
6. **Abundance-gradient papers (no line ratios published; used for direction and for a derived check):**
   - Méndez-Delgado et al. 2022, MNRAS 510, 4436 (https://ar5iv.labs.arxiv.org/html/2112.12600) — READ: 42 regions, R_G ≈ 6.5–17 kpc, "We adopt a solar Galactocentric distance of R₀ = 8.2 ± 0.1 kpc"; Table 2 (t² = 0 / t² > 0): O/H −0.044 ± 0.009 (int. 8.86 ± 0.09) / −0.059 ± 0.012; N/H −0.063 ± 0.009 (int. 8.20 ± 0.09) / −0.078 ± 0.013; S/H −0.035 ± 0.011 / −0.049 ± 0.012; Ar/H −0.029 ± 0.008 / −0.042 ± 0.011 dex kpc⁻¹; log(N/O) −0.018 ± 0.015 (t² > 0). Line intensities are not tabulated in the paper (they sit in the cited data papers).
   - Arellano-Córdova et al. 2020, MNRAS 496, 1051 (https://ar5iv.labs.arxiv.org/html/2005.11372) — READ: 33 regions, 6.15–17.0 kpc, Gaia-revised distances; Table 1 gives per-region R_G and T_e, e.g. M8 R_G 7.04 ± 0.20 kpc T_e([N II]) 8400 ± 100 K; M17 6.46 kpc, 8900 ± 200 K; Sh 2-83 15.3 kpc, 11 900 ± 600 K. The gradient section was truncated in the rendering; slopes NOT READ from this paper.
   - Arellano-Córdova et al. 2021, MNRAS 502, 225 (https://ar5iv.labs.arxiv.org/html/2012.06643) — READ: 42 regions, 4–17 kpc, R₀ = 8.2 kpc; O/H −0.042 ± 0.009 (int. 8.84 ± 0.09, σ 0.07 dex); N/H −0.057 ± 0.011 (int. 8.18 ± 0.11, σ 0.11); log(N/O) −0.015 ± 0.007 (int. −0.65 ± 0.07, σ 0.10); "The shape of the radial gradients of O/H and N/H is linear and constant, discarding any substantial change of the slope".
   - Fernández-Martín et al. 2017, A&A 597, A84 (https://ar5iv.labs.arxiv.org/html/1610.01194) — READ: 23 regions, 11–18 kpc, kinematic distances on Brand & Blitz 1993 with R₀ = 8.5 kpc, θ₀ = 220 km s⁻¹; slopes O/H −0.053 ± 0.009, N/H −0.080 ± 0.019, S/H −0.106 ± 0.006, Ar/H −0.074 ± 0.006, N/O −0.041 ± 0.006 dex kpc⁻¹; Cardelli et al. 1989 R_V = 3.1; 1D spectra extracted from zones chosen for auroral-line S/N (slit, brightest zones). Dereddened intensities exist for the 9 WHT regions (Table 3) but the rendering could not return them.
   - Esteban et al. 2017 (https://ar5iv.labs.arxiv.org/html/1706.07727) — READ: 21 regions, 5.1–17 kpc, R₀ = 8.0 kpc; O/H −0.040 ± 0.005 dex kpc⁻¹ (inner −0.029 ± 0.009, outer −0.046 ± 0.017); T_e([O III]) rises at 320 ± 40 K kpc⁻¹; extraction apertures "targeted the brightest nebular regions"; two example rows returned (Sh 2-100, R_G 9.4, I(6583) = 19.5 on Hβ = 100 with I(Hα) = 100.1 → [N II]/Hα = 0.19 (the low Hα is odd — treat as rendering-suspect); Sh 2-298, R_G 11.9, I(6583) = 150.7, I(Hα) = 280 → 0.54).
   - Wenger et al. 2019, ApJ 887, 114 (https://ar5iv.labs.arxiv.org/html/1910.14605) — READ: 167 nebulae, 4–16 kpc, R₀ = 8.34 kpc; "Te/K = 4493(+156/−188) + 359(+22/−18) R/kpc"; Shaver et al. 1983 conversion "12 + log(O/H) = (9.82 ± 0.02) − (1.49 ± 0.11) T_e/10⁴ K"; O/H −0.052 ± 0.004 dex kpc⁻¹; intrinsic scatter ~1000 K / 0.25 dex.
   - Shaver et al. 1983, MNRAS 204, 53 (https://academic.oup.com/mnras/article/204/1/53/967131, abstract only) — READ: 67 regions (33 optical), 3.5 < R_G < 13.7 kpc, T_e gradient 433 ± 40 K kpc⁻¹, O/H −0.07 ± 0.015, N/H −0.09 ± 0.015 dex kpc⁻¹ (R₀ in the abstract not shown; NOT READ: 10 kpc).
   - Deharveng et al. 2000, MNRAS 311, 329 — not reachable (no arXiv version found; OUP page not fetched; VizieR returned "Table or Catalog not found"). Context only, NOT READ: 34 regions, 6.6–17.7 kpc (that sentence READ second-hand from the OUP search listing).
7. **External-galaxy relations (MaNGA/CALIFA/PHANGS)** — not read this session; not used.

## Why this one

- It is the only Galactic measurement found of a line ratio of *whole* HII regions fitted against galactocentric radius for a population (243–246 regions with distances), with a stated slope and error, over 8.2–15.4 kpc — most of the model's range. Criteria (a)–(d) of the brief all hold: Galactic; flux-stacked over each region's WISE radius (integrated, not a slit); [N II]/Hα is reddening-free at the 1 % level; error stated.
- The conversion from the paper's "O/H" slope to the [N II]/Hα slope is a division by a published constant (0.57), not a modelling step; no photoionization assumption enters the target.
- The deep-spectra compilations (Méndez-Delgado, Arellano-Córdova, Esteban, Fernández-Martín) are better *abundance* sources, but they publish abundances, not ratios; their apertures are slits through the brightest zones (they say so); and the ratio would have to be reconstructed region by region from data tables the renderings could not return. They serve as the direction check below.
- Madsen 2006 is the best Galactic *value* at the solar circle (whole regions, WHAM beam), but has no radial lever arm; hence the secondary check.
- [N II]/Hα rather than [S II]/Hα: [S II] carries the extra S⁺/S ionization-structure dependence and the density dependence of the doublet; the sources also disagree on the HII-region [S II]/Hα level (see below). [O III]/Hα: no Galactic radial measurement found this session.

## Windows the other candidates would give

| Candidate | Statistic | Value / window | Label |
|---|---|---|---|
| Zhao 2026 Eq. 8 (adopted) | d log([N II]/Hα)/dR, 8.2–15.4 kpc | −0.025 ± 0.009 dex kpc⁻¹ | READ |
| Zhao 2026 Eq. 9.2 | same, > 9.65 kpc | −0.028 ± 0.009 | READ |
| Zhao 2026 Eq. 9.1 | same, 8.16–9.65 kpc | −0.077 ± 0.018 | READ |
| Derived: MD22 N/H (t²=0) −0.063 + T_e term (+0.059, Wenger 359 K kpc⁻¹ through Madsen Eq. 2 at T ≈ 7700 K) | predicted slope | ≈ −0.004 (± ~0.02) | derived from READ inputs |
| Derived: MD22 N/H (t²>0) −0.078 + 0.059 | predicted slope | ≈ −0.019 | derived |
| Derived: Arellano-Córdova 2021 N/H −0.057 + 0.059 | predicted slope | ≈ +0.002 | derived |
| Derived: Shaver 1983 N/H −0.09 + T term at 433 K kpc⁻¹ (+0.071) | predicted slope | ≈ −0.02 | derived |
| Derived: Fernández-Martín 2017 (11–18 kpc) N/H −0.080 + T term at T ≈ 10⁴ K (+0.039) | predicted slope | ≈ −0.04 | derived |
| Wen 2024 DIG | [N II]/Hα vs R | non-monotonic, not fitted | READ (not applicable) |
| Madsen 2006 | [N II]/Hα at R ≈ 8.2–9.7 kpc | 0.27, rows ≈ 0.20–0.40 | READ (rows flagged) |
| Zhao 2026 fit at 8.2 kpc | [N II]/Hα | 0.36 (0.30–0.44) | READ + arithmetic |
| Zhao 2026 median, whole sample | [N II]/Hα | 0.31 | READ |
| Haffner 1999 | NGC 7000 / NGC 1499 | 0.20 / 0.39 | READ |
| Haffner 2009 | "bright classical" | ≈ 0.25 | READ (review) |
| [S II] doublet/Hα at R₀ | Zhao median 0.15; Wen "HII" 0.20; Madsen λ6716 0.11 → doublet ≈ 0.19 at low density (6731/6716 ≈ 0.7, NOT READ) | 0.15–0.20 | mixed |
| [O III]/Hα at R₀ | Madsen O-star average | 0.18 | READ (two renderings) |

## What moves the window

- **Source:** Madsen's 0.27 versus the LAMOST fit's 0.36 at R₀ is 0.13 dex; the LAMOST WISE radii include the regions' faint outskirts (where [N II]/Hα is higher — the LAMOST spatially-resolved paper on 10 isolated regions reports that "[N II]/Hα and [S II]/Hα ratios increase with distance from the center of the H II regions", READ second-hand from its abstract in the search listing), while the WHAM beam includes the same outskirts plus foreground/background WIM. Neither is a slit. For the gradient there is one source; the choice is between its global and two-zone fits (−0.025 vs −0.028/−0.077).
- **R₀:** negligible for both statistics (≤ 0.001 dex).
- **Scatter versus formal error:** the LAMOST slope error (±0.009) is the error of a fit to binned medians; the population scatter in log([N II]/Hα) at fixed R is of order the width of the Fig. 5 histogram (not recovered numerically; from Madsen's rows it is ≈ ±0.1 dex). A model ring is an Hα-weighted mean, not a median, so it will sit above the median if the ratio is anti-correlated with luminosity within the ring — an effect of a few hundredths of a dex; hence the ~2σ acceptance window.
- **Integrated versus slit:** slit spectra through the brightest knots (Esteban/Fernández-Martín/Méndez-Delgado data) under-sample the low-ionization outer zone and give lower [N II]/Hα and [S II]/Hα than whole-region measurements — do not mix them with Madsen/LAMOST.
- **Radiation-bounded model regions versus a leaky sample — my view, the session's to rule:** real Galactic regions leak (the WIM's existence requires it; Haffner 2009 §5 discusses escape fractions "in excess of 20 %" for bubbles in turbulent clouds, READ), and a leaky region truncates exactly the outer N⁺/S⁺ zone. A radiation-bounded model with the same stars and abundances should therefore sit at or **above the sample median** in [N II]/Hα and [S II]/Hα and **below** it in [O III]/Hα. For the *gradient* row this bias is roughly radius-independent and cancels; for the value-at-R₀ check I would compare to the median but read a result in the upper half of 0.20–0.40 as expected, not as a warning, and only a result above 0.40 as a miss. I would not compare to the upper envelope: the envelope is set by the oldest/most evolved regions and by WIM contamination in the beam, not by ionization bounding.
- **N/O of the grid:** at R₀ the deep-spectra intercepts give log(N/O) ≈ −0.77 (Arellano-Córdova 2021: −0.65 − 0.015×8.2) to ≈ −0.82 (Méndez-Delgado 2022 t²=0, from the N/H and O/H intercepts); a grid at log(N/O) = −0.6 or −1.0 moves the value-at-R₀ by ±0.2 dex but leaves the slope alone unless N/O itself is given a gradient (measured: −0.015 ± 0.007 to −0.018 ± 0.015 dex kpc⁻¹, i.e. flat).

## Direction note (what the row will most likely pass or kill on)

For a disc whose O/H falls outward at −0.044 to −0.059 dex kpc⁻¹ (READ, Méndez-Delgado 2022), N/H at −0.063 to −0.078 (READ, same) and S/H at −0.035 to −0.049 (READ, same), while T_e rises at +359 (+22/−18) K kpc⁻¹ (READ, Wenger 2019) or +345 ± 78 K kpc⁻¹ (READ, Zhao 2026 Eq. 6), the collisionally excited ratios do **not** follow the abundances. Through Madsen 2006 Eq. 2 (READ; [N II]/Hα ∝ T₄^0.4 e^(−2.18/T₄)), a +0.0359 in T₄ per kpc at T₄ ≈ 0.77–0.80 adds +0.055 to +0.06 dex kpc⁻¹ to log([N II]/Hα), nearly cancelling the N/H fall; the measured Galactic slope is indeed shallow and negative, −0.025 ± 0.009 dex kpc⁻¹ (READ, Zhao 2026), with "[N II]/Hα and [S II]/Hα show negative radial gradients with increasing Rgal" and [S II]/[N II] "nearly flat" (READ, Zhao §V.1). So: **[N II]/Hα falls outward, slowly (about −0.02 to −0.03 dex kpc⁻¹, roughly a third of the N/H gradient); [S II]/Hα falls outward about as slowly or less (S/H gradient shallower, [S II] excitation 2.14/T₄ similar; Zhao: "gradually decrease", slope not published); [O III]/Hα is expected to *rise* outward** — the 2.88/T₄ Boltzmann term alone gives +0.07 dex kpc⁻¹ against O/H's −0.05, and O⁺⁺/O rises as the ionizing spectrum hardens at lower Z — but this last direction is **NOT READ** for the Galaxy (no Galactic HII-region [O III]/Hα-vs-R measurement was found; the supporting Galactic fact READ is T_e([O III]) rising at +320 ± 40 K kpc⁻¹, Esteban 2017). A model that lets [N II]/Hα track N/H (slope ≈ −0.06 to −0.08) or that keeps T_e fixed with radius will fail the row; a model whose grid raises T_e as O/H falls should land near −0.02.

---

# Target B — a reading, not a row: the Milky Way WIM/DIG's [N II]/Hα and [S II]/Hα

## Adopted reading (two constants a later session could enter)

- **[N II] λ6583/Hα (WIM, WHAM, |z| ≳ 0.5 kpc and I_Hα ≲ few R): characteristic ≈ 0.5, range ≈ 0.3–1.0, exceeding 1.0 on the faintest sightlines.** READ, Madsen et al. 2006 §I/§IV (three renderings): "A typical value of [N II]/Hα is ≈ 0.5, but in some cases exceeds 1.0"; READ, Haffner et al. 1999 abstract: "the [S II]/Hα and [N II]/Hα ratios increase as absolute Hα intensities decrease", §3.3/Fig. 6: from ≈ 0.2 at I_Hα > 50 R to ≈ 0.8–1.0 at 0.5 R.
- **[S II] λ6716/Hα (single line; WHAM does not observe λ6731): characteristic ≈ 0.3–0.5 in the diffuse gas, range 0.06 (bright HII) to > 0.5 (faintest).** READ, Haffner 1999 §3.3: NGC 7000 0.06, NGC 1499 0.14, faint WIM 0.3–0.5; READ, Madsen 2006: WIM "[S II]/Hα is significantly higher than the H II regions (≈ 0.1)"; Sivan 2 decomposition (one rendering only, flagged): WIM component [N II]/Hα 0.83, [S II]/Hα 0.38 against HII component 0.23, 0.12. For the doublet sum multiply by ≈ 1.7 at n_e ≪ 100 cm⁻³ (NOT READ).
- **In-plane DIG (|z| < 0.3 kpc, anticentre, LAMOST):** peaks [N II]/Hα = 0.33 and [S II](6717+6731)/Hα = 0.38 (READ, Wen et al. §II/Fig. 5), i.e. the in-plane DIG's [N II]/Hα is barely above HII regions while its [S II]/Hα is ≈ ×1.9; Wen: DIG shows "higher [N II]/Hα and [S II]/Hα ratios, coupled with lower [O III]/Hα ratios"; Zhao §V.1 from the HII side: "The values of [N II]/Hα are slightly higher than those in the DIG, while the values of [S II]/Hα and [S II]/[N II] are significantly lower across all Rgal."

**Enhancement relative to classical HII regions (READ):** HII-region references are [N II]/Hα 0.27 and [S II]6716/Hα 0.11 (Madsen 2006) or "[S II]/Hα ≈ 0.1", "[N II]/Hα ≈ 0.25" (Haffner 2009 §2.3). Hence the WIM proper is enhanced by **≈ ×2 (up to ×4) in [N II]/Hα and ≈ ×3–4 in [S II]/Hα**; the in-plane DIG by ≈ ×1.1 and ≈ ×1.9. [O III]/Hα in the WIM is "typically less (~10 %) those seen in H II regions" and He I/Hα about half: "(He I/Hα)_WIM ~ 0.5 × (He I/Hα)_HII", "He⁺/He ≲ 60 %" (READ, Haffner 2009 §2.2). S⁺/S: 0.3–0.7 in the WIM versus ≈ 0.25 in HII regions (READ, Haffner 2009 §2.3; Haffner 1999 §4: local diffuse 0.6–0.65, Perseus ≈ 0.5, full range 0.25–0.8).

**Dependence on Hα intensity / height / temperature (READ):**
- Intensity: ratios rise as I_Hα falls (Haffner 1999 abstract, §3.3; Madsen 2006 §VI: "[N II]/Hα and [S II]/Hα increase with decreasing Hα intensity").
- Height: Haffner 1999 §4: "the temperature in the halo rises from about 7000 K at |z| = 0.75 kpc to over 10,000 K at |z| = 1.75 kpc"; Wen et al. abstract: "[N II]/Hα, [S II]/Hα, and [S II]/[N II] increase with increasing Galactic disk height (|z|) in both southern and northern disks" (their Table 2 vertical slopes for [S II]/[N II]: 1.21 ± 0.71 kpc⁻¹ south, 1.07 ± 0.60 north; [N II]/Hα and [S II]/Hα slopes not returned).
- Temperature: WIM 6000–9000 K (Haffner 1999 abstract; one rendering said 10 000 — the abstract fetched directly says 9000), 7000–10 000 K (Haffner 2009 §2.3); "WIM is about 2000 K warmer than the denser, classical H II regions" from [N II]λ5755/λ6583 (READ, Haffner 2009 §2.3.2, citing Madsen 2006); HII regions 6000–7000 K (Madsen 2006 §VI.2.1).

**The temperature relation (READ, Madsen 2006 Eqs. 2–5; Haffner 1999 Eq. 11 agrees):**
- [N II]6583/Hα = 1.62×10⁵ T₄^0.4 e^(−2.18/T₄) (N⁺/N)(N/H)(H⁺/H)⁻¹, with N/H = 7.5×10⁻⁵, N⁺/N ≈ 0.8, H⁺/H ≈ 1 assumed. (Haffner 1999 Eq. 11: 1.63×10⁵ T₄^0.426 e^(−2.18/T₄), same abundances.)
- [S II]6716/[N II]6583 = 4.62 e^(0.04/T₄) (S⁺/S)(S/H) / [(N⁺/N)(N/H)], S/H = 1.86×10⁻⁵ — nearly temperature-independent ("From T₄ = 0.5 to 1.0 ... decreases only about 11 %", READ Haffner 2009 §2.3.1), so [S II]/[N II] measures S⁺/S.
- [N II]5755/6584 = 0.192 e^(−2.5/T₄) (Eq. 4); [O III]5007/Hα = 1.74×10⁵ T₄^0.4 e^(−2.88/T₄)(O⁺⁺/O)(O/H)(H⁺/H)⁻¹, O/H = 3.19×10⁻⁴ (Eq. 5); He I/Hα ≃ 0.47 T₄^−0.14 (He⁺/He)(He/H), He/H = 0.1 (Eq. 6).
- Evaluated (my arithmetic, N⁺/N = 0.8, N/H = 7.5×10⁻⁵): [N II]/Hα = 0.21 (6000 K), 0.29 (6500), 0.37 (7000), 0.58 (8000), 0.83 (9000), 1.10 (10 000). The HII average 0.27 ↔ ≈ 6400 K; the WIM's 0.5 ↔ ≈ 7700 K; 1.0 ↔ ≈ 9600 K — consistent with the papers' own temperature statements. [S II]6716/Hα = [N II]/Hα × 1.43 e^(0.04/T₄) (S⁺/S): with S⁺/S = 0.25 at 6500 K → 0.11 (matches Madsen's HII average); with S⁺/S = 0.5 at 8000 K → 0.44 (WIM).
- Caution: the model's layer, if judged by these formulae, needs its N/H at the layer's radius (the 7.5×10⁻⁵ is a solar-neighbourhood gas-phase value the WHAM papers assume, READ), an N⁺/N (0.8 assumed), and an S⁺/S (0.3–0.7 measured); the enhancement of the WIM over HII regions is *partly temperature (+2000 K) and partly ionization state (S⁺/S ×2)*, not abundance.

**Unresolved in this reading (flagged):** two renderings of Haffner 1999 reported its [S II]/[N II] values as "1.0–1.5"; that contradicts the same paper's quoted HII/WIM pairs (0.06/0.20 = 0.30, 0.14/0.39 = 0.36) and Madsen's Eq. 3 (which gives 0.4–1.0 for S⁺/S = 0.25–0.7). I treat the 1.0–1.5 as a misread axis and do not use it; the auditor may check Haffner 1999 Fig. 9 directly.

---

# Summary for the auditor

**Target A (row):** d log([N II]6583/Hα)/dR of the model's Hα-weighted ring means over 8.2–15.4 kpc only = **−0.025 dex kpc⁻¹, 1σ ±0.009, acceptance window [−0.045, −0.005]**, from Zhao et al. 2026 (LAMOST MRS-N, 243–246 Galactic HII regions, whole-region stacked spectra, R₀ 8.15 → 8.2 kpc immaterial): their Eq. 8 O/H slope −0.014 ± 0.005 divided by the 0.57 of their Eq. 5 (PP04 N2).
Secondary check, not the row: [N II]/Hα at R₀ = **0.27, window 0.20–0.40** (Madsen 2006 O-star HII average, whole regions at R_G ≈ 8.2–9.7 kpc; LAMOST median 0.31 and LAMOST fit 0.36 at 8.2 kpc inside/at the edge of the window). Killing direction: a model whose [N II]/Hα follows N/H (≈ −0.06 to −0.08 dex kpc⁻¹) fails; the rising T_e (+345–359 K kpc⁻¹) must cancel most of the abundance fall.

**Target B (reading, two constants):** WIM [N II]6583/Hα ≈ **0.5 (0.3–1.0)** and [S II]6716/Hα ≈ **0.3–0.5** (doublet ≈ ×1.7), rising as I_Hα falls and as |z| rises, i.e. **≈ ×2 and ≈ ×3–4 above classical HII regions (0.27, 0.11)**; in the plane (|z| < 0.3 kpc) the DIG is only ×1.1 and ×1.9 above HII regions (0.33, 0.38 doublet). Temperature: WIM 6000–10 000 K, ≈ 2000 K hotter than HII regions (6000–7000 K); [N II]/Hα(T) = 1.62×10⁵ T₄^0.4 e^(−2.18/T₄)(N⁺/N)(N/H) (Madsen 2006 Eq. 2), giving 0.37 at 7000 K, 0.58 at 8000 K, 0.83 at 9000 K for N⁺/N = 0.8, N/H = 7.5×10⁻⁵; [S II]/[N II] is set by S⁺/S (0.3–0.7 WIM vs 0.25 HII), not by T.

Primary URLs used: https://arxiv.org/html/2607.27662 ; https://arxiv.org/abs/2607.27662 ; https://ar5iv.labs.arxiv.org/html/astro-ph/0609558 ; https://r.jina.ai/https://arxiv.org/pdf/astro-ph/0609558 ; https://iopscience.iop.org/article/10.1086/307734/fulltext/40172.text.html ; https://arxiv.org/abs/astro-ph/9904143 ; https://ned.ipac.caltech.edu/level5/Sept09/Haffner/Haffner2.html ; https://arxiv.org/html/2412.05692v1 ; https://ar5iv.labs.arxiv.org/html/2112.12600 ; https://ar5iv.labs.arxiv.org/html/2005.11372 ; https://ar5iv.labs.arxiv.org/html/2012.06643 ; https://ar5iv.labs.arxiv.org/html/1610.01194 ; https://ar5iv.labs.arxiv.org/html/1706.07727 ; https://ar5iv.labs.arxiv.org/html/1910.14605 ; https://academic.oup.com/mnras/article/204/1/53/967131 .
