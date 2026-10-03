# READING_GAS_PATTERN — the S51 reading session behind the gas's own arm pattern (D210)

Three Opus readers, 2026-10-03, each on one question; every number below was read on a fetched page and carries its
[verified] tag with the section or table it came from, or is marked [recall — NOT READ] and kept out of the summary
tables. Arithmetic on read numbers is marked as the reader's. The constants in `model/galaxy/models/level0.py` cite
this file; the ruling is DECISIONS.md D210. Nothing here is a model number until a ruling takes it (D113).

---

# Reading A — gas arm/interarm contrasts (S51, 2026-10-03)

Reading agent's note. Literature only; no repository file touched. Every number below was read on a fetched page unless tagged [recall — NOT READ]. "Ratio of means" = mean Σ in an arm mask / mean Σ in an interarm mask. "Peak-type" = a high percentile or a narrow-mask value against a floor. "Fourier" = m-component amplitude. Arithmetic marked (my arithmetic) is mine, done on the read numbers, not a literature value.

## Summary table

| Source | Tracer | Quantity | Value and spread | Coverage (galaxies, radii, mask) | Where read |
|---|---|---|---|---|---|
| Querejeta et al. 2024, A&A 687, A293 | CO(2-1) → Σmol | ratio of means, per 500 pc radial bin and spiral segment | **2.22** (16–84th pct: 1.26–4.41) | 27 PHANGS spirals, 59 segments, ~100 pc maps; NIR log-spiral masks ~1–2 kpc wide; whole disc in 500 pc bins | arXiv:2405.05364 HTML, Table 1 "Nominal contrasts" |
| same | CO → Σmol | same, grand-design only | **2.73** (1.37–5.79) | 17 grand-design spirals of the 28 | same, Table 1 "Nominal – Grand design spirals" |
| same | CO → Σmol | same, rest of spirals | **1.90** (1.12–2.94) | the non-grand-design spirals | same, Table 1 |
| same | CO → Σmol | same, narrow masks (~50 % of mask area, cut round CO/Hα ridge) | **2.53** (1.51–5.36) | as nominal | same, Table 1 "Narrow masks" |
| same | CO → Σmol | same at 1.5 kpc resolution | **1.49** (1.00–2.84) | as nominal | same, Table 1 "Low resolution (1.5 kpc)" |
| same | HI → Σatom | ratio of means | **1.22** (1.01–1.79) | 15 spirals with HI resolution < 2.5 kpc; CO matched to each HI beam | same, Table 2 "H I" |
| same | HI+H2 | ratio of means | **1.26** (0.99–2.14) | same 15 | same, Table 2 "H I+H2" |
| same | CO → Σmol, HI-matched beam | ratio of means | **1.31** (0.96–2.62); same galaxies at high res **2.43** (1.35–5.67) | same 15 | same, Table 2 |
| same | 3.6 µm → Σ* | ratio of means | **1.28** (1.02–1.77); GD 1.34 | 28 spirals | same, Table 1 |
| Querejeta et al. 2021, A&A 656, A133 | CO(2-1) → Σmol | ratio of pooled medians, 1.5 kpc hexagons | 9.903 / 4.492 M⊙ pc⁻² = **2.20** (my arithmetic); means 14.97 / 6.589 = 2.27 (my arithmetic) | all PHANGS-ALMA spirals with masks (of 74), 1.5 kpc apertures; masks ~1–2 kpc wide | arXiv:2109.04491 HTML, Table 3; Sect. 4.2 "roughly a factor of two" |
| Meidt et al. 2021, ApJ 913, 113 | CO(2-1) | peak-type: percentile / mean of pixels below 84th pct, per 150 pc annulus | log C_CO: 84th **0.50** (+0.18/−0.17) dex; 99th **0.98** (+0.34/−0.62) dex; GD 84th 0.53, 99th 1.1 | 67 PHANGS galaxies, 1527 radial bins, 150 pc maps; no arm mask (percentile-based) | arXiv:2103.13247 HTML, Table 1, Eq. 2 |
| same | 3.6 µm | same | log C_3.6: 84th **0.11** (+0.08/−0.05); 99th 0.23 dex | same | same |
| same | CO vs 3.6 µm | fit | log C_CO = **1.41** log C_3.6 + 0.31 (84th pct), scatter ~0.15 dex | same | same, Eq. 2 |
| Vlahakis et al. 2013, MNRAS 433, 1837 | CO(1-0) | ratio of means in 0.5 kpc bins, averaged | **1.7 ± 0.5** | M51 only, 1.7 to ~6 kpc (to ~10 kpc), 15″ (~600 pc); mask from CO(3-2), arms ~1 kpc wide | arXiv:1304.7408 (ar5iv), Table 5, Sect. 6.3 |
| same | CO(2-1) / CO(3-2) | same | **2.1 ± 0.5** / **2.4 ± 1.1** (3-2 falls ~4 at 2 kpc to ~1 at 6.5 kpc) | same | same |
| same | HI | same | **1.6 ± 0.3**, little radial variation over ~10 kpc | same | same |
| Hitschfeld et al. 2009, A&A 495, 795 | HI+H2 (total gas) | ratio of area means; arms = Σgas > 20 M⊙ pc⁻² | inner **2.9**, outer **2.0** | M51 only, 11″ (~450 pc); inner arms vs outer arms (~120–170″) | arXiv:0901.1601 HTML, Table 1 |
| Colombo et al. 2014, ApJ 784, 3 | CO(1-0) → ΣH2 | area-mean ΣH2 per environment | arms 129.94, interarm 34.37 M⊙ pc⁻² → **3.78** (my arithmetic) | M51 only, PAWS FoV, 1.3–5 kpc disc, ~40 pc; masks from stellar potential | arXiv:1401.1505 (ar5iv), Table 2 |
| Ferrière 2001, RMP 73, 1031 (review; primaries not read) | CO → H2, MW inner (Q1) | space-averaged density, arms/interarm | **~3.6** | MW first quadrant, inside solar circle (Clemens et al. 1988) | arXiv:astro-ph/0106359 PDF, Sect. II.B |
| same | CO → H2, MW outer | surface density ratio arm:interarm | **~13:1** | MW outer Galaxy, l = 270–300° (Grabelsky et al. 1987) and l = 102–142° (Heyer 1999) | same |
| same | HI, MW outer | surface density arm/interarm | **~4** | MW outside solar circle, three major arms (Kulkarni et al. 1982) | same, Sect. III.C |
| Colombo et al. 2022, A&A 658, A54 (SEDIGISM) | ¹³CO(2-1), MW inner | molecular mass arm/interarm (said similar to the Σ ratio) | **~1.5** | MW −60° ≤ l ≤ 18°, \|b\| ≤ 0.5°; arms = l-v within 10 km/s of Taylor & Cordes 1993 loci | arXiv:2110.06071 abstract + ar5iv Sect. 5.3 |
| Koda, Scoville & Heyer 2016, ApJ 823, 76 | f_mol = H2/(HI+H2), MW | azimuthal (arm-interarm) variation of f_mol | ~20 % inner (R ≲ 6 kpc), ~40–50 % outer | MW inside solar circle, l 0–90° and 270–360° | arXiv:1604.01053 abstract |
| Reid et al. 2019, ApJ 885, 131 | masers (young high-mass stars), MW | arm width, Gaussian 1σ | w(R) = **336 + 36 (R/kpc − 8.15) pc** | MW, ~200 parallaxes | arXiv:1910.03357 (ar5iv), text |

## Per-source notes

### 1. Querejeta et al. 2024, A&A 687, A293, "Do spiral arms enhance star formation efficiency?" (arXiv:2405.05364)
Fetched: https://arxiv.org/abs/2405.05364 (abstract), https://arxiv.org/html/2405.05364 (full text, three passes). A&A full-text page returned 403; PDF did not parse.
- Abstract: stellar contrast "very modest, typically a few tens of percent"; Σmol and ΣSFR contrasts "typically reach a factor of ∼2−3". [verified: Querejeta 2024, arXiv:2405.05364, abstract, https://arxiv.org/abs/2405.05364]
- Definition, quoted: "we consider the mean surface density within the footprint of each spiral segment at that radius (arm value), and divide it by the mean surface density within the ring outside the spiral mask". So a **ratio of means** per 500 pc radial bin, per spiral segment. Maps not clipped: "we should not be biased by non-detections". Errors are the 16th–84th percentile range over segments/bins. [verified: same, Sect. 2, https://arxiv.org/html/2405.05364]
- Mask: "perfectly smooth, dilated log-spiral segments, with a typical width of ∼1−2 kpc", spirals traced on NIR images (masks from Querejeta 2021). Narrow-mask test: "The narrow mask typically covers ∼50% of the area of the original mask", built round CO or Hα peaks along perpendicular cuts, dilated with a 7.5″ Gaussian. [verified: same, Sect. 2.6.1 and Table 1]
- Table 1 values (median, subscript/superscript = 16–84th): Σ* 1.28 −0.26 +0.49; Σmol 2.22 −0.96 +2.19; ΣSFR 2.56 −1.61 +4.59; SFE 1.16. Grand-design: Σmol 2.73 −1.36 +3.06, ΣSFR 3.12. Rest: Σmol 1.90 −0.78 +1.04. Narrow masks: Σmol 2.53 −1.02 +2.83, ΣSFR 3.11. 1.5 kpc resolution: Σmol 1.49 −0.49 +1.35. 250 pc bins: 2.25; 1000 pc bins: 2.14; perpendicular bins along arms 2.31; perpendicular with adjacent interarm 2.19. High M*: 2.70; low M*: 1.80. [verified: same, Table 1]
- Table 2 (atomic gas, 15 galaxies with HI beam < 2.5 kpc, CO degraded to each HI beam): HI 1.22 −0.21 +0.57; HI+H2 1.26 −0.27 +0.88; H2 at the HI beam 1.31 −0.35 +1.31; H2 at high resolution in the same galaxies 2.43 −1.08 +3.24; Σmol/Σatom 1.13 −0.27 +0.55. Text: "The H I contrast is typically ∼10% lower than the H2 contrast" (at matched ~kpc resolution). [verified: same, Table 2]
- Radial behaviour: "The molecular gas contrast shows a more stable behaviour with radius, with running medians fluctuating around a factor 2-2.5"; stellar contrast rises from ~5 % innermost to ~38 % at 0.5 R25. [verified: same, Sect. 3.6]
- Sample: 28 spirals with explicit spiral masks, 9.5 ≲ log M* ≲ 11.1; Σmol for 27 galaxies / 59 segments; ΣSFR for 21 / 44. 17 grand-design. [verified: same, Sect. 2.1 and Table 1 notes]
- Caveats: ~100 pc maps; resolution matters a lot (2.22 at ~100 pc vs 1.49 at 1.5 kpc); the 1–2 kpc mask width is much wider than a dust lane, so it is a ratio of means, not peak-to-trough. The HI number is at ≤ 2.5 kpc resolution only, and is therefore a lower limit on what HI would show at arm-width resolution (the matched H2 drops from 2.43 to 1.31 at that resolution).
- Coverage: 28 of 74 PHANGS galaxies (the ones with clear spiral masks); nearby, moderately inclined, massive star-forming discs.

### 2. Querejeta et al. 2021, A&A 656, A133 (arXiv:2109.04491)
Fetched: https://arxiv.org/abs/2109.04491, https://arxiv.org/html/2109.04491 (three passes).
- Sect. 4.2: centroids "displaced vertically by 0.3−0.4 dex, which results in median surface densities that are roughly a factor of two higher in spiral arms than in the interarm environment"; Fig. 6 at a common 1.5 kpc resolution. [verified: Querejeta 2021, Sect. 4.2, https://arxiv.org/html/2109.04491]
- Table 3 (1.5 kpc hexagons, pooled over all galaxies): Σmol median spiral 9.903, interarm 4.492 M⊙ pc⁻²; means 14.97 and 6.589; CO-weighted 29.82 and 14.66. Ratios (my arithmetic): medians 2.20, means 2.27, weighted 2.03. [verified: same, Table 3]
- Table 2 census: spiral arms hold 18.4 % of H2 mass on 10.7 % of area; interarm 16.8 % on 33.0 %. (my arithmetic: mass per area ratio 1.72/0.509 = 3.4, but this is pooled over all galaxies, including those without arms in the denominator only where interarm is defined — treat as indicative.) [verified: same, Table 2, Sect. 4.1]
- Mask: log-spiral fits to bright 3.6 µm arms; width grown in 0.5 kpc steps until the CO flux gain fell below 1.25× per step, "typically ~1−2 kpc wide". [verified: same, Sect. 3.2]
- Coverage: subset of 74 PHANGS galaxies that received spiral masks (count not stated in what I read; "62% of the galaxies where we implemented spiral arms were defined as 'grand design'").

### 3. Meidt et al. 2021, ApJ 913, 113 (arXiv:2103.13247)
Fetched: https://arxiv.org/abs/2103.13247, https://arxiv.org/html/2103.13247 (two passes).
- Definition: contrast = a fixed high percentile of the CO (or 3.6 µm) distribution in a radial annulus / reference level = "the mean of all pixels below the 84th percentile". Annuli 150 pc wide; native 150 pc maps; non-detections set to zero. This is **peak-type**, not arm/interarm by mask. [verified: Meidt 2021, Sect. III.2, https://arxiv.org/html/2103.13247]
- Abstract: "the logarithms of CO contrasts on 150 pc scales are 3-4 times larger than, and positively correlated with, the logarithms of 3.6 µm contrasts". [verified: same, abstract]
- Table 1 (log, dex): CO all 84th 0.50 (+0.18/−0.17), 93rd 0.69, 97th 0.84, 99th 0.98 (+0.34/−0.62); grand-design 0.53 / 0.73 / 0.91 / 1.1; flocculent 0.47 / 0.63 / 0.76 / 0.88. 3.6 µm all: 0.11 / 0.15 / 0.19 / 0.23. Fit: log C_CO = 1.41 log C_3.6 + 0.31 (84th), ~0.15 dex scatter. [verified: same, Table 1, Eq. 2]
- Coverage: 67 PHANGS-ALMA galaxies, 1527 radial bins with > 50 % CO detection. Includes bars, so not arms only.
- Caveat for the project: the 3.6 µm contrasts here (0.11–0.23 dex, i.e. factor 1.3–1.7) are far below Elmegreen et al. 2011's 1.14 mag (0.456 dex) peak-to-trough; the fit is not tested at stellar contrasts that large, so do not extrapolate it to 0.456 dex without saying so.

### 4. Vlahakis et al. 2013, MNRAS 433, 1837 (arXiv:1304.7408), M51
Fetched: https://ar5iv.labs.arxiv.org/html/1304.7408 (two passes); arXiv PDF too large.
- Contrast = "the ratio of the mean spiral arm velocity-integrated intensity versus the mean inter-arm integrated intensity in bins of 0.5 kpc", averaged over bins (Table 5 "Average arm-interarm contrast"): CO(3-2) 2.4 ± 1.1, CO(2-1) 2.1 ± 0.5, CO(1-0) 1.7 ± 0.5, HI 1.6 ± 0.3. [verified: Vlahakis 2013, Sect. 6.3, Table 5]
- CO(3-2) contrast "decreases from a contrast of ∼4 at 2 kpc to ∼1 at ∼6.5 kpc"; "for H i and CO J=1-0 emission there is little variation in the arm-interarm contrast with radius over ∼10 kpc". [verified: same, Sect. 6.3, Fig. 10]
- Mask from the CO(3-2) image; arm "width ... is ∼1 kpc (∼20″–30″), when corrected for the telescope beam"; all maps at 15″ (~600 pc). Compares CO(2-1) 2.1 with Hitschfeld et al. 2009's 2.9. [verified: same, Sect. 6.1, 2.3]
- ± not defined in the text read (likely spread over radial bins). Coverage: M51 only, ~1.7–6 kpc reliably.

### 5. Hitschfeld et al. 2009, A&A 495, 795 (arXiv:0901.1601), M51
Fetched: https://arxiv.org/html/0901.1601 (two passes).
- Table 1: Σgas (HI+H2) inner arms 26.8, outer arms 18.8, interarm 9.4 M⊙ pc⁻²; "inner arm/interarm" 2.9, "outer arm/interarm" 2.0; ΣH2/ΣHI arm/interarm 3.2 (inner), 0.3 (outer). Quote: "The averaged inner arm/interarm contrast in the total gas surface density is 2.9". [verified: Hitschfeld 2009, Table 1, Sect. 3.1]
- Arms defined as "All regions above a threshold surface density of Σgas=20 M⊙ pc⁻²" — a threshold mask, biased toward a high contrast. 11″ resolution. M51 only.

### 6. Colombo et al. 2014, ApJ 784, 3 (arXiv:1401.1505), M51 PAWS
Fetched: https://ar5iv.labs.arxiv.org/html/1401.1505.
- Table 2 (as read): spiral arms area 14.6 kpc², L_CO 43.44 ×10⁷ K km s⁻¹ pc², ΣH2 129.94 M⊙ pc⁻²; interarm 27.8 kpc², 21.88, 34.37. My check: L_CO/area gives 29.8 and 7.9 K km s⁻¹ (×4.35 ≈ the ΣH2 column), so ΣH2 is an area mean. Arm/interarm ratio of area means = 3.78 (my arithmetic). [verified: Colombo 2014, Table 2]
- Masks from the stellar potential / torque map, seven environments; disc 1.3–5 kpc; ~40 pc resolution. Mask widths are in its Appendix C, not read. M51 only, inner 9 kpc FoV.

### 7. Schinnerer et al. 2013, ApJ 779, 42 (arXiv:1304.1801), M51 PAWS overview
Fetched: https://ar5iv.labs.arxiv.org/html/1304.1801.
- Only a qualitative-numeric statement: "The factor 2× enhancement in the smooth component of the 24 µm emission in the arm compared to the inter-arm region is similar to the average arm/inter-arm difference in CO brightness." [verified: Schinnerer 2013, Sect. IV.2.3] No tabulated CO contrast. Kept out of the table.

### 8. Foyle et al. 2010, ApJ 725, 534 (arXiv:1010.0678)
Fetched PDF, extracted text locally. Arms = the brightest X % (10–50 %, fiducial 45 %) of pixels per 7.5″ annulus in an m = 6 / m = 0 Fourier-filtered 3.6 µm image; 13″ common resolution; to 0.3–0.4 r25; NGC 628, 5194, 6946. Results are flux fractions (Fig. 2), not contrasts: "the H2 (CO emission) is more concentrated to the spiral arms than the HI. The HI is the least concentrated to the arms." No numerical arm/interarm Σ ratio in the text. Ordering only (CO > HI) is usable. [verified: Foyle 2010, Sect. 2.2 and 3, arXiv PDF]

### 9. Knapen 1997, MNRAS (arXiv:astro-ph/9612137), NGC 3631 HI
Fetched PDF, extracted text locally. Introduction, general statement: "the H i emission from the interarm is generally a factor 3–5 lower than that from the arms", in the context of ~15″ resolution needed at ~15 Mpc. A general peak-type statement, uncited in the sentence; not a measurement for a sample. [verified: Knapen 1997, Sect. 1]

### 10. Ferrière 2001, Rev. Mod. Phys. 73, 1031 (arXiv:astro-ph/0106359) — Milky Way, secondary
Fetched PDF, extracted text locally. Primary papers NOT read (Clemens et al. 1988; Grabelsky et al. 1987; Heyer 1999; Kulkarni et al. 1982).
- Inner MW, first quadrant: interarm H2 space-averaged density "on average over the first quadrant, only a factor ∼ 3.6 lower than in the arms" (Clemens et al. 1988). [verified: Ferrière 2001, Sect. II.B, citing Clemens 1988]
- Outer MW: "the molecular surface density contrast ratios between spiral arms and interarm regions are much greater than in the inner Galaxy, with a mean value ∼ 13 : 1", l 270–300° (Grabelsky 1987) and l 102–142° (Heyer 1999). [verified: same]
- HI, outer MW: arms "have a roughly constant H i surface density, which is about four times greater than in the inter arm regions" (Kulkarni et al. 1982). [verified: same, Sect. III.C]
- Caveat: kinematic distances; the outer-Galaxy CO numbers cover limited longitude windows only; these are review statements from 1980s–90s data.

### 11. Colombo et al. 2022, A&A 658, A54, SEDIGISM (arXiv:2110.06071) — Milky Way
Fetched: https://arxiv.org/abs/2110.06071, https://ar5iv.labs.arxiv.org/html/2110.06071. A&A page 403; PDF too large.
- Abstract: "the molecular mass in the spiral arms is a factor of 1.5 higher than that of the inter-arm medium". Sect. 5.3: "the contrast between spiral arms and the inter-arm regions in terms of mass is about 1.5, which is similar to the mass surface-density ratio". Concludes the MW would classify as flocculent. [verified: Colombo 2022, abstract and Sect. 5.3]
- Arms: l-v regions within ΔV < 10 km/s of the Taylor & Cordes (1993) arm loci; −60° ≤ l ≤ 18°, |b| ≤ 0.5°; ¹³CO(2-1), 28″. Caveat: this is a cloud-mass ratio, and the arm model and the ±10 km/s window set what "arm" means.

### 12. Koda, Scoville & Heyer 2016, ApJ 823, 76 (arXiv:1604.01053) — Milky Way
Fetched abstract and ar5iv text. f_mol "remaining ~>50% ... to R~6kpc, and decreasing to ~10-20% ... at R=8.5 kpc"; "Azimuthal, arm-interarm variations are secondary: only ~20%, in the globally molecule-dominated inner MW, but becoming larger, ~40-50%, in the atom-dominated outskirts." No arm mask (scatter along rings). Columbia/CfA CO and LAB HI at 0.6°; inner MW, l 0–90° and 270–360°. Bears on phase change, not directly on Σ contrast. [verified: Koda 2016, abstract]
- Nakanishi & Sofue 2016 (arXiv:1511.08877) fetched: only "fmol varies by 0.1 – 0.2 between an arm and an inter-arm" (Sect. 4.6); no Σ contrast. [verified: Sofue & Nakanishi 2016, Sect. 4.6, https://arxiv.org/html/1511.08877]

### 13. Reid et al. 2019, ApJ 885, 131 (arXiv:1910.03357) — Milky Way arm width (not contrast)
Fetched abstract and ar5iv. Arm widths of maser-traced (young high-mass star) arms: "w(R) = 336 + 36(R(kpc) − 8.15) pc" in plane (Gaussian 1σ intrinsic width); vertical σz = 20 pc inside 7 kpc. Table 2 per-arm values not visible on the page read. [verified: Reid 2019, text, ar5iv]

### 14. Dobbs & Baba 2014, PASA 31, e035 (arXiv:1407.5062)
Fetched NED level5 pages Dobbs3.html, Dobbs4.html. No observed gas arm/interarm contrast numbers; only theory (Shu et al. 1972 two-phase shock density enhancements "of around 10 and 40"; Parker instabilities "factors of several"). Not usable as an observed default.

## What could not be read

- A&A full-text pages for Querejeta 2024 and Colombo 2022: HTTP 403 (arXiv versions read instead).
- Koda et al. 2009, ApJL 700, L132 (arXiv:0907.1656): abstract read, no contrast numbers in it; full text not fetched. The search engine's summary claimed CO line-ratio increase of 2-3 in arms — [recall — NOT READ], not used.
- Pety et al. 2013 (ApJ 779, 43), Schinnerer et al. 2017 (arXiv:1701.02184, fetched: arm vs spurs only, no interarm contrast), Hughes et al. 2013 (arXiv:1304.1219, fetched: qualitative — "less than 5% of the emission in the interarm is brighter than 4 K"; no ratio).
- Williams et al. 2022 (PHANGS spiral arms): not located.
- Hou & Han 2014, Reid et al. 2014, Englmaier & Gerhard 1999, Bissantz et al. 2003, Miville-Deschênes et al. 2017, Sellwood & Masters 2022: not fetched (time spent on the contrast sources first).
- Primary MW papers behind Ferrière's review (Clemens 1988, Grabelsky 1987, Heyer & Terebey 1998/Heyer 1999, Kulkarni 1982): not read; their numbers are carried at second hand.
- Levine, Blitz & Heiles 2006 (Science; astro-ph/0605728): abstract read; no contrast number in the abstract ("The ratio of the surface density to the local median surface density is relatively constant along an arm").
- [recall — NOT READ] none used.

## Recommendation to the lead (no numbers from memory)

Key point first: the model's stellar number (Elmegreen et al. 2011, 1.14 mag = factor 2.9) is a **peak-to-trough** of a narrow profile. The best gas numbers are **ratios of means** over 1–2 kpc wide masks, which dilute any peak. They are not the same quantity. A gas ratio of means of 2.2–2.7 is not "larger" than a stellar peak-to-trough of 2.9; the same papers give a stellar ratio of means of only 1.28 (1.34 grand-design). In like-for-like terms the gas contrast is much larger than the stellar one: about 3–4× in log (Meidt 2021 abstract; Querejeta 2024's 2.22 vs 1.28 gives log ratio ≈ 3.2, my arithmetic).

1. **Molecular gas (CO/H2), nearby discs.** Default: Querejeta et al. 2024, Table 1, Σmol ratio of means **2.22**, 16–84th pct 1.26–4.41 (27 PHANGS spirals, ~100 pc, 1–2 kpc masks); for a grand-design model use **2.73** (1.37–5.79). For a seeded residual this is roughly ±0.3 dex in log about the median (my arithmetic: 0.35 −0.25/+0.30 dex for all; 0.44 −0.30/+0.33 dex for GD). If the model needs a ratio relative to the stellar ratio of means, carry it as log C_gas ≈ 3.2 × log C_* (same table, my arithmetic) and keep the Meidt 2021 fit (log C_CO = 1.41 log C_3.6 + 0.31, 0.15 dex scatter, 150 pc, peak-type) as the named alternative. For a peak / narrow-lane figure, the sourced options are the narrow-mask ratio of means **2.53** (Querejeta 2024) and Meidt's 99th-percentile contrast **0.98 dex** (factor ~9.5, my arithmetic; GD 1.1 dex) over the faint floor. Record M51 as the single-galaxy cross-check: 1.7 (CO 1-0, 600 pc, Vlahakis 2013) to 3.78 (area means, 40 pc, Colombo 2014): the spread is mostly resolution and mask.

2. **Atomic gas (HI).** Default: Querejeta et al. 2024, Table 2, **1.22** (1.01–1.79), 15 spirals at ≤ 2.5 kpc resolution, said to be ~10 % below the H2 contrast at matched resolution. It is a resolution-limited lower bound. Named alternative: Vlahakis et al. 2013, M51 HI **1.6 ± 0.3** at ~600 pc, flat with radius. Knapen 1997's "factor 3–5" is a general, uncited peak-type remark at ~15″; do not adopt it as a default. Ordering that is safe to encode: HI contrast < H2 contrast (Foyle 2010; Querejeta 2024), and HI keeps its contrast to larger radius (Vlahakis 2013).

3. **Milky Way.** No modern full-disc Σ contrast was found. Best-sourced: SEDIGISM (Colombo et al. 2022) **~1.5** arm/interarm molecular mass, said to match the Σ ratio, inner Galaxy −60° ≤ l ≤ 18°, with the authors' conclusion that the MW looks flocculent. Named alternatives, both second-hand through Ferrière 2001: inner Galaxy (Q1) H2 **~3.6** (Clemens 1988), outer Galaxy CO **~13:1** (two longitude windows), outer-Galaxy HI **~4** (Kulkarni 1982). The MW figures need kinematic distances and arm-model choices, so carry them as alternatives, not as the default. For arm width (narrowness), Reid et al. 2019's maser-arm 1σ width **336 pc at R0, +36 pc/kpc** is the sourced MW figure; it traces young stars, not the gas Σ profile.

---

# Reading B — gas ridge widths (S51, 2026-10-03)

Reading agent's note. Literature only; nothing in the repository was touched.
Every number below carries a tag. `[verified: ...]` means the number was read in the fetched full text (arXiv PDF, read through `pdftotext`) at the place named. `[derived: ...]` means **the reader's own arithmetic** on verified inputs. No source states it, and it must not be cited as a literature value. `[recall — NOT READ]` means a remembered number that was not checked. None of those appear in the summary table.

(Journal volume/page numbers are given only where read; otherwise the arXiv id identifies the paper.)

Conversion used in the `[derived]` entries: the perpendicular spacing between adjacent arms of an m-armed log spiral with pitch ψ at radius R is L⊥ = 2πR sinψ / m. This is the form Kim & Ostriker 2002 §2.1 and Kim et al. 2020 (TIGRESS) §2 state as "the arm-to-arm separation". In the PDF text extraction the π glyph is lost, but their worked value (R0 = 10 kpc, sin i = 0.1, m = 2 → Lx = 3.1 kpc) requires it. An azimuthal width Δφ is a fraction Δφ·m/360° of the spacing, independent of R and ψ. For reference, the project's pure-cosine arm (1 + cos mφ) has a FWHM equal to half the arm period, i.e. FWHM / spacing = 0.50. That is a property of the cosine, not a literature value.

## Summary table

Only [verified] rows. "Spacing" gives what the source states. The derived fraction, where computable, is in the last column and marked [derived].

| Source | Tracer | Width definition | Value, spread, radial trend | Spacing / arm number / radius | Coverage | Where read | Fraction of spacing [derived] |
|---|---|---|---|---|---|---|---|
| Egusa et al. 2017, MNRAS (arXiv 1610.06642) | **Gas** (CO(1–0) + HI, total H gas surface density) **and stellar mass** (SED-fit map), same paper | Gaussian fit to azimuthal profiles (in 4″ radial bins). The text says "FWHM" (§3.1, §3.2), but the Fig. 4 caption calls the plotted bar "width (σ)" | Gas: FWHM ≈ 30° (inner arms), ≈ 5° (outer arms). Stars: ≈ 60° (inner), ≈ 30° (outer). Gas arms are "generally smaller" than stellar arms | M51, 2 arms; inner r = 30–150″, outer r = 151–220″ (D = 8.4 Mpc) | M51 only, both arms, ≈1.2–9 kpc | §2.1, §2.4 Table 2 header, §3.1, §3.2 | Gas FWHM/spacing ≈ 0.17 inner, ≈ 0.03 outer. Stars ≈ 0.33 inner, ≈ 0.17 outer. Gas/star ≈ 0.5 inner. (If the bars are σ, multiply by 2.355.) |
| Querejeta et al. 2024, A&A 687, A293 (arXiv 2405.05364) | CO + Hα ridge ("narrow masks") | Ridge of peak CO or Hα on cuts perpendicular to the log-spiral, then dilated (Gaussian kernel FWHM 7.5″, threshold 0.01). Full mask width | "typical widths between 500 and 1000 pc", "about half the width of the original masks". The narrow mask covers ≈50 % of the original mask's area | Masks follow 3.6 µm log-spirals (no spacing given) | 28 PHANGS spiral galaxies (grand-design and multi-armed), ALMA field of view | §2.6.1–2.6.2, Appendix E | ≳ 0.12 (half of the broad-mask lower bound below) |
| Querejeta et al. 2021, A&A 656, A133 (arXiv 2109.04491) | CO(2–1) flux (ALMA 7m+TP at 7″) around 3.6 µm log-spirals | Full mask width: dilation in 500 pc steps until the CO flux gain is < 25 % | "typically 1-2 kpc wide". The median width across PHANGS is 1.5 kpc (the default where ALMA coverage is poor) | Area: spiral 1495 kpc², interarm 4620 kpc² (Table 2) | PHANGS-ALMA, 74 galaxies (spiral masks in a subset; 28 per Querejeta 2024) | §3.2, Table 2, §5 | Spiral-mask area / (spiral + interarm) = 0.24. This is a **lower bound**, because "interarm" also includes the interbar and outer disc (Table 1) |
| Colombo et al. 2014, ApJ (PAWS; arXiv 1401.1505) | CO(1–0) kinematics (spiral streaming) | Width at 95 % of maximum of the azimuthal auto-correlation of streaming velocity; symmetric about the CO ridge | Areas: spiral-arm zone (SA) 14.6 kpc², inter-arm (IA) 27.8 kpc² | M51, 2 arms, disc 1.3 ≲ R ≲ 5 kpc | M51, PAWS field (≈ central 9 kpc), 1″ ≈ 40 pc | §5.1, Appendix (arm-width definition), Table 2 | SA/(SA+IA) = 0.34 (an envelope of the CO arm, not the ridge) |
| Colombo et al. 2022, A&A (SEDIGISM; arXiv 2110.06071) | ¹³CO(2–1) molecular clouds (Milky Way) | Median (and IQR) of **2 × |offset|** of clouds from the arm ridge line (Taylor & Cordes 1993 arm model); kinematic distances | All arms: 579 pc (IQR 832). Norma-Outer 463 (666), Scutum-Centaurus 531 (810), Sagittarius-Carina 951 (952), Perseus 682 (885). Authors: "more than a factor of two larger" than Reid 2019 | MW inner Galaxy | 3491 clouds in arms, −60° < l < 18° | §5.3 text, Table 2 (CxyA, full arm extent) | For a Gaussian, the median of 2|x| is 1.35σ, so σ ≈ 430 pc globally |
| Reid et al. 2019, ApJ 885, 131 (arXiv 1910.03357) | Masers in high-mass star-forming regions (young stars; **not gas**) | Intrinsic Gaussian 1σ scatter perpendicular to the arm, fitted as a parameter with parallax errors | w(R) = 336 + 36 (R[kpc] − 8.15) pc. Per arm at R_kink: 3-kpc(N) 0.18, Norma 0.14, Sct-Cen 0.23, Sgr-Car 0.27, Local 0.31, Perseus 0.35, Outer 0.65 kpc | MW "four-arm spiral". R_kink 3.52–12.24 kpc. Pitch 3°–19.5° | ≈200 parallaxes; 165 assigned to 7 arms | §3 text, Fig. 4 caption, Table 2 | With m = 4 and ψ = 12°: σ/L⊥ ≈ 0.13 (FWHM/L⊥ ≈ 0.30) at R = 5, 8.15 and 12 kpc, i.e. ~constant. Per arm, σ/L⊥ = 0.06–0.21 |
| Reid et al. 2014, ApJ 783, 130 (arXiv 1401.5377) | Masers (young stars) | Intrinsic 1σ arm width ("astrophysical noise" needed for χ²_ν ≈ 1) | Scutum 0.17, Sagittarius 0.26, Local 0.33, Perseus 0.38, Outer 0.63 kpc. Widths grow at 42 pc kpc⁻¹ over 5–13 kpc | R_ref 5.0, 6.6, 8.4, 9.9, 13.0 kpc | ≈100 parallaxes; 90 used in 5 arm fits | §3 text, Table 2, Fig. 2 caption | — |
| Honig & Reid 2015, ApJ 800, 53 (arXiv 1412.1012) | HII regions (Hα / blue images; young stars, **not gas**) | Gaussian 1σ of perpendicular (minimum) distances from a fitted log-spiral segment | M51 0.07–0.46 kpc. NGC 628 0.14–0.87. NGC 1232 0.10–0.65. NGC 3184 0.07–0.47. Width grows with R; the last segment of some arms narrows | 2-armed galaxies (NGC 1232 multi-armed). Per-segment R and pitch given | 4 face-on galaxies (i ≲ 30°), segments of 5–10 kpc length; M51 283 + 527 HII regions | §3, Tables 2–5, §5.2 | Examples: M51 seg A3 / B3 / B4 σ/L⊥ = 0.034 / 0.050 / 0.118. NGC 628 A2 / B2 / B3 = 0.118 / 0.071 / 0.140 |
| Elmegreen et al. 2014, ApJ (S4G dust lanes; arXiv 1310.7146) | **Dust lanes** (optical opacity vs 3.6 µm) | Typical full width of the lane, by eye (pixel count) | "typical dust lane width is ~4 pixels" = W ≈ 150 pc at 10 Mpc. W/(πR) ≈ 1 % at R = 4 kpc (two-arm spacing πR) | 2-arm spacing πR at R = 4 kpc | 5 galaxies (NGC 4321, 5055, 5194, 5248, 5457); S4G 1.7″ resolution (2.26 pixels), so near the resolution limit | §2, Table 1, §5.1 | ≈ 0.01 (stated by the source) |
| Vallée 2020, ApJ (arXiv 1911.06798) | Offset dust lane → other tracers (24 galaxies) | Separation between tracers across the arm (a half-width proxy in Vallée's interpretation, not a profile width) | Median 326 pc, mean ≈ 370 pc | Median galactic radius ≈ 4 kpc | 24 of 40 galaxies with a measured offset | Abstract, §3 | — |
| Vallée 2020, ApJ (arXiv 2006.01281) | MW masers vs diffuse CO(1–0) (8′ beams) | Separation maser → diffuse CO peak, and dust → diffuse CO | Maser–CO 250 ± 50 pc, rising at 25 ± 5 pc per kpc. Dust–CO 315 pc (rms 64, s.d.m. 26) | MW 4-arm model, pitch −13.1° | MW inner arms | Abstract, §1, §6, §7 | — |
| Savchenko et al. 2020, MNRAS (arXiv 2001.09110) | Optical gri light (**stellar** arms) | Asymmetric Gaussian I0·exp(−(r−r_peak)²/w²) on cuts ⊥ to the arm. Full width w = w1 + w2 (each w = √2 σ, so w1 + w2 ≈ 1.2 × FWHM) | Mean w = (0.14 ± 0.05) r25. Grand design 3.3 ± 1.2 kpc, multi-armed 2.5 ± 0.9, flocculent 2.1 ± 1.4. 85.8 % of galaxies show width rising with R. Outer half-width w2 ≈ 16 % > inner w1 | Grand design 2.0, multi-armed 2.9 ± 0.9, flocculent 3.7 ± 1.2 arms (Fig. 3) | 155 face-on SDSS galaxies | Abstract, §3.2 eq. 1, §4.3, Fig. 3 | — |
| Marchuk et al. 2024, MNRAS (arXiv 2402.08531) | M51 in 17 bands, FUV→FIR (stellar, PAH, dust) | FWHM of the radial slice of a 2D arm model; images convolved to 18″ (SPIRE 250 µm) | Arm 1 / Arm 2 width (″): FUV 40.5 / 44.0; 3.6 µm 42.5 / 41.0; 8.0 µm 36.2 / 41.1; 24 µm 24.3 / 33.9; 70 µm 27.6 / 38.4; 250 µm 18.8 / 38.8. ≈ 1.5–2 kpc. No widening with R found | M51, 2 arms, D = 8.9 Mpc | M51 only; 18″ ≈ 0.8 kpc resolution (coarse) | Table 4, §6.3.4 | — |
| Kim & Ostriker 2002, ApJ (arXiv astro-ph/0111398) — theory | 2D isothermal gas, spiral shock | Arm width W at Σ = (Σmax + Σmin)/2 | W/Lx = 0.05–0.16 across 10 models (forcing F = 1–3 %) | Lx = 2πR sin i/m. Standard: R0 = 10 kpc, sin i = 0.1, m = 2 → 3.1 kpc | Local shearing-box models | §2.1, §4, Table 1 col. 7 | 0.05–0.16 (stated, as W/Lx) |
| Kim, Kim & Ostriker 2008, ApJ (arXiv 0804.0139) — theory | 1D multiphase gas (TI), spiral shock | Fraction of the spatial domain in the dense-arm stage | Dense arm 1 %, transition 16 %, interarm 83 % of arm-to-arm distance (time: 14 / 22 / 64 %) | Standard model SU2, n0 = 2 cm⁻³ | 1D models | Abstract, §4 | 0.01 (stated) |
| Kim, Kim & Ostriker 2010, ApJ (arXiv 1006.4691) — theory | 3D stratified multiphase gas | Fractional widths of the flow zones | Arm 10 %, post-shock expansion 20 %, interarm 70 % of arm-to-arm distance (time 15 / 30 / 55 %). The 3D arm is wider than the 1D 1 % because of shock flapping | Lx = 2R0 sin i/m = 2.5 kpc (m = 2, sin i = 0.1) | Solar-neighbourhood conditions | Abstract, §2, §6 summary | 0.10 (stated) |

## Per-source notes

### 1. Egusa, Mentuch Cooper, Koda & Baba 2017, MNRAS — M51 gas and stellar arms (the only same-paper gas-vs-stellar width found)
- Fetched: https://arxiv.org/pdf/1610.06642 (full text).
- Gas map: HI from Walter et al. 2008 (5.8″ × 5.6″) plus CO(1–0) from Koda et al. 2009 (3.7″ × 2.8″, X_CO = 2×10²⁰). Both are convolved to **6″ (≈ 240 pc)**, 2″ pixels, D = 8.4 Mpc [verified: §2.1]. Stellar mass map: SED fit (Mentuch Cooper et al. 2012) at 4″, smoothed to match [verified: §2.2].
- Method: azimuthal profiles in 4″ radial bins, two-Gaussian fits following Dobbs et al. 2010 [verified: §2.5.2]. Inner arms: r = 30–150″. Outer arms: r = 151–220″ [verified: Table 2 header].
- Quotes: stars, "Typical arm widths in azimuthal angle are ~60 degree (FWHM) for inner arms and ~30 degree for outer arms" [verified: §3.1]. Gas, "~30 degree (FWHM) for inner arms and ~5 degree for outer arms" [verified: §3.2]. Gas arms "are generally smaller than those of stellar spiral arms" [verified: §3.2].
- Caveat 1, definition: the results text says FWHM. The Fig. 4 caption and §2.5.3 say the plotted bars are the "width (±1σ)". I take the text's explicit "FWHM" but flag the ambiguity. If σ were meant, every fraction below is ×2.355, and the inner stellar arm (0.78 of spacing) would then be wider than a cosine. That makes the FWHM reading the more plausible one.
- Caveat 2, outer gas width: [derived] 5° at R ≈ 7.5 kpc with ψ ≈ 28° is ≈ 0.3 kpc perpendicular, close to the 240 pc beam. The outer value is therefore near the resolution limit, and M51's outer disc is perturbed by NGC 5195 (the authors stress the companion).
- Fractions [derived; m = 2 so the spacing is 180°]: gas FWHM/spacing ≈ 0.17 inner, ≈ 0.03 outer. Stars ≈ 0.33 inner, ≈ 0.17 outer. Gas/star width ≈ 0.5 (inner).
- Coverage: one galaxy, two arms, r ≈ 1.2–6.1 kpc (inner) and 6.1–9 kpc (outer) [derived from 30–220″ at 8.4 Mpc].

### 2. Querejeta et al. 2024, A&A 687, A293 — "Do spiral arms enhance star formation efficiency?" (PHANGS)
- Fetched: https://arxiv.org/pdf/2405.05364 (full text).
- Sample: "28 spiral galaxies from PHANGS–ALMA" [verified: §2.1, abstract], studied at ~100 pc resolution.
- Narrow masks: along the backbone log-spiral, they "identify the position of the maximum CO or Hα intensity along this perpendicular line". The ridge pixels are then smoothed with a "Gaussian kernel of FWHM = 7.5″" and thresholded at 0.01. The CO and Hα masks are united [verified: §2.6.2, Fig. 2 caption]. "The narrow mask typically covers 50% of the area of the original mask" [verified: §2.6.2].
- Width: "These masks have typical widths between 500 and 1000 pc, so about half the width of the original masks" [verified: Appendix E]. Also: "Locally, the distribution of molecular gas or star formation in the arms often looks thinner" than the 1–2 kpc masks [verified: §2.6.1].
- Caveat: these are mask (top-hat) full widths, not fitted profile widths, and the dilation kernel sets a floor. It is a CO **and** Hα union. No radial trend is given.

### 3. Querejeta et al. 2021, A&A 656, A133 — PHANGS environmental masks
- Fetched: https://arxiv.org/pdf/2109.04491v2 (full text).
- Method: 3.6 µm unsharp-masked log-spiral fits (mostly from S4G, Herrera-Endoqui et al. 2015). The width is grown "in multiples of half a kpc (500 pc, 1000 pc, 1500 pc, 2000 pc, etc.)" until the CO flux ratio between successive steps "falls below an empirical threshold of 1.25" (ALMA 7m+TP, 7″) [verified: §3.2]. Result: "spiral masks which are typically 1-2 kpc wide". The default when coverage is poor is "the median (1.5 kpc) width across the whole PHANGS sample" [verified: §3.2].
- Authors' own caveat: "a more restrictive definition of the spiral arm width, following the high surface density ridge of molecular gas, would naturally result in a higher arm/interarm ratio" [verified: §5].
- Area census: spiral 1495 kpc² (10.7 %) and interarm 4620 kpc² (33.0 %) out of 13972 kpc² (all 74 galaxies, inside the ALMA field of view) [verified: Table 2]. [derived] 1495/(1495+4620) = 0.24, a lower bound on the arm-mask share of the arm+interarm area, since "interarm" = labels 4+7+8 includes the interbar and outer disc [verified: Table 1].
- Caveat: an envelope of 3.6 µm + CO + Hα built to "accommodate local irregularities ... such as spurs". It is not the gas ridge.

### 4. Colombo et al. 2014, ApJ — PAWS GMC environments in M51
- Fetched: https://arxiv.org/pdf/1401.1505 (full text).
- Definition: "We determine the zone of enhanced spiral streaming centered around the arm by measuring the (rotational) auto-correlation of azimuthal streaming velocities". The width is taken "at 95% maximum". The 95%-max width of the CO-brightness auto-correlation "corresponds well with the width estimated by eye" [verified: Appendix].
- Areas: SA 14.6 kpc², IA 27.8 kpc² (disc 1.3–5 kpc; DWI 4.2, DWO 5.3, MAT 3.9 kpc²) [verified: Table 2, §5.1]. [derived] arm share 0.34.
- Caveat: the PAWS field is not a full annulus, and an auto-correlation width is broader than the intrinsic profile.
- Related, PAWS I (Schinnerer et al. 2013, ApJ 779, 42; https://arxiv.org/pdf/1304.1801). Qualitative only: "the width of the arms as seen in the (young) stellar clusters appears significantly wider than the CO arms" [verified: §4.3.3]. CO "very well follows these dust lanes" [verified: §4.3.3]. Its Appendix B defines a convolved arm width w ≈ 0.64σ from the cross-correlation 2nd moment, but gives no numerical width in text (only figure error bars) [verified: Appendix B].
- Schinnerer et al. 2017 (PAWS spiral-arm segment; https://arxiv.org/pdf/1701.02184): no arm width. Only spur widths, "typical widths of 1-2″ (40-80 pc)" in their thin parts [verified: §3].

### 5. Colombo et al. 2022, A&A — SEDIGISM: spiral arms and the inner Milky Way molecular gas
- Fetched: https://arxiv.org/pdf/2110.06071 (full text). (The aanda.org HTML returned 403.)
- Definition: arm "width" is "the median of two times the distribution of cloud offset to the closest (and associated) arm" [verified: §5.3]. Clouds come from ¹³CO(2–1), with kinematic distances. Survey −60° < l < 18° [verified: §2].
- Quote: "spiral arms are relatively wide, with a global median of ~580 pc, but with a broad inter-quartile range IQR~830 pc" [verified: §5.3]. Table 2 (CxyA, full arm extent): Nor-Out 463 (666), Scu-Cen 531 (810), Sag-Car 951 (952), Perseus 682 (885), all 579 (832) pc. N_cloud = 943 / 1742 / 543 / 263 / 3491 [verified: Table 2].
- Authors compare: "more than a factor of two larger than the spiral arm widths estimated by Reid et al. (2019)" [verified: §5.3].
- Caveat: offsets include kinematic-distance errors and arm-model mismatch, which broaden the widths. Measured against the Taylor & Cordes 1993 arm model. [derived] For a Gaussian, median 2|x| = 1.35σ, so σ ≈ 430 pc globally (an upper-biased gas width).

### 6. Reid et al. 2019, ApJ 885, 131 — MW maser parallaxes
- Fetched: https://arxiv.org/abs/1910.03357 and the PDF (full text).
- Definition: "(Gaussian 1σ) intrinsic width of a spiral arm, w(R) = w(R_kink) + (dw/dR)(R − R_kink)", with dw/dR = 42 pc kpc⁻¹ adopted from Reid 2014 in the fit [verified: §3]. Then: "spiral arms widen with Galactocentric radius as w(R) = 336 + 36(R(kpc) − 8.15) pc" [verified: §3, Fig. 4 caption].
- Table 2 (width at R_kink, kpc): 3-kpc(N) 0.18 ± 0.05 (R_kink 3.52), Norma 0.14 ± 0.10 (4.46), Sct-Cen 0.23 ± 0.05 (4.91), Sgr-Car 0.27 ± 0.04 (6.04), Local 0.31 ± 0.05 (8.26), Perseus 0.35 ± 0.06 (8.87), Outer 0.65 ± 0.16 (12.24). N = 3, 11, 36, 35, 28, 41, 11 [verified: Table 2, raw-text extraction].
- Arm number: "the Milky Way is a four-arm spiral" [verified: abstract]. The Fig. 10 grey arms "have widths of 1.65σ, which would enclose 80% of sources" [verified: §8].
- Out-of-plane: z-width 20 + 36(R − 7.0) pc for R > 7 kpc [verified: §3.1] (not needed here).
- Caveat: the tracer is young massive stars, **not gas**. It is the scatter of sources, not an emission profile.
- [derived] Pitches from Table 2 (my choices where a kink gives two values): Norma 19.5°, Sct-Cen 13.1°, Sgr-Car 17.1°, Local 11.4°, Perseus 9.5°, Outer 9.4°. With m = 4, σ/L⊥ = 0.060, 0.132, 0.097, 0.121, 0.152, 0.207 (FWHM/L⊥ 0.14–0.49). With the global fit and ψ = 12°: σ/L⊥ = 0.136 (R = 5), 0.126 (8.15), 0.121 (12). The fraction is roughly constant because both width and spacing grow ~linearly with R. Caveat: the Local arm is arguably a spur, so the m = 4 spacing is uncertain.

### 7. Reid et al. 2014, ApJ 783, 130
- Fetched: https://arxiv.org/abs/1401.5377 and the PDF.
- "The widths of spiral arms increase with distance from the Galactic center" [verified: abstract]. "increase nearly linearly with Galactocentric radius at a rate of 42 pc kpc⁻¹ between radii of 5 to 13 kpc" [verified: §3].
- Table 2 (width, kpc): Scutum 0.17 ± 0.02 (R_ref 5.0, N = 17), Sagittarius 0.26 ± 0.02 (6.6, 18), Local 0.33 ± 0.01 (8.4, 25), Perseus 0.38 ± 0.01 (9.9, 24), Outer 0.63 ± 0.18 (13.0, 6) [verified]. Fig. 1 plots "1σ widths" [verified: Fig. 1 caption]. Superseded by Reid 2019.

### 8. Honig & Reid 2015, ApJ 800, 53 — HII-region arm widths in four galaxies
- Fetched: https://arxiv.org/pdf/1412.1012.
- Definition: "we adopt a Gaussian (1σ) approximation to the distribution of the minimum distances of H II regions from the model arm segment" [verified: §3]. Galaxies are within ~30° of face-on and were not deprojected [verified: §2]. Segments are 5–10 kpc long.
- Tables 2–5 (σ in kpc, mean R). M51 A: 0.07 (1.90), 0.18 (3.29), 0.26 (5.40), 0.31 (6.45), 0.23 (6.08). M51 B: 0.14 (2.50), 0.20 (3.42), 0.28 (5.39), 0.37 (6.70), 0.43 (7.11), 0.46 (7.05), 0.22 (9.72). NGC 628 A: 0.14, 0.34, 0.42. NGC 628 B: 0.27, 0.46, 0.87, 0.59 (R 5.75–12.02). NGC 3184: 0.07–0.47 (R 1.09–3.95). NGC 1232: 0.10–0.65 [verified].
- "spiral arms increase in width with distance from the center of their galaxy". Some outer tips narrow [verified: §5.2]. They also cite Lynds (1970) for the same trend in "primary dust lanes" (not read).
- Caveat: HII regions, not gas. Segment pitch angles are noisy, so the derived fractions scatter.

### 9. Elmegreen et al. 2014, ApJ — Embedded star formation in S4G dust lanes
- Fetched: https://arxiv.org/pdf/1310.7146.
- Quote: "A typical dust lane width is ~4 pixels ... which is W ~ 150 pc at a distance of 10 Mpc" [verified: §5.1]. Then: "the relative dust lane thickness is W/πR ~ 1%" for R = 4 kpc, with arm-to-arm distance πR for two arms [verified: §5.1. The π is lost in the text extraction, but 150/(π·4000) = 1.2 % confirms it].
- Galaxies: NGC 4321 (20.9 Mpc), 5055 (7.54), 5194 (7.54), 5248 (15.4), 5457 (4.94) [verified: Table 1]. Image resolution 1.7″ = 2.26 pixels [verified: Table 1 note].
- Caveat: a by-eye width at near-resolution scale (4 pixels vs 2.26-pixel resolution), so the true lane may be narrower. One typical value, no distribution, no radial trend.

### 10. Vallée 2020 (two papers) — tracer offsets across the arm
- arXiv 1911.06798 (24 galaxies, https://arxiv.org/pdf/1911.06798). "we find offsets with a median value near 326 pc and a mean near 370 pc", measured "Starting in the dust lane and going across the spiral arm" [verified: abstract]. The median galactic radius is ~4 kpc [verified: §3].
- arXiv 2006.01281 (MW, https://arxiv.org/pdf/2006.01281). Maser-to-diffuse-CO separation "250 ± 50 pc", "increase ... of about 25 ± 5 pc per kpc" [verified: abstract]. Dust-to-diffuse-CO "315 pc with an r.m.s. of 64 pc" [verified: §6].
- Caveat: Vallée calls these "arm widths", but they are **offsets between tracer peaks** (dust lane → potential minimum), i.e. a half-arm separation. They are not the width of the gas or dust ridge. Useful for **placing** the dust lane relative to the stellar arm centre.

### 11. Savchenko et al. 2020, MNRAS — 155 SDSS face-on spirals (stellar/optical arm widths)
- Fetched: https://arxiv.org/pdf/2001.09110. Companion: Mosenkov, Savchenko & Marchuk 2020, RAA (https://arxiv.org/pdf/2003.13994), same sample, same result (14 % show constant or narrowing width).
- Profile: I(r) = I0·exp(−(r − r_peak)²/w1²) inside, w2 outside, on cuts ⊥ to the arm [verified: eq. 1]. Full width w = w1 + w2 [verified: §4.3].
- "The mean value of the width for the sample is (0.14±0.05) r25". In kpc: grand design 3.3 ± 1.2, multi-armed 2.5 ± 0.9, flocculent 2.1 ± 1.4 [verified: §4.3]. 85.8 % have a positive width–radius slope [verified: §4.3]. The w2 (outer) half-width is ≈16 % larger than w1 [verified: §4.3]. Arm numbers: G 2.0, M 2.9 ± 0.9, F 3.7 ± 1.2 [verified: Fig. 3].
- Caveat: optical bands, a mix of young and old stars, with dust lanes depressing the inner side. Seeing-limited, with the arm width 2.7× the PSF on average.

### 12. Marchuk et al. 2024, MNRAS — M51 decomposition in 17 bands
- Fetched: https://arxiv.org/pdf/2402.08531.
- Width = "FWHM of radial slice of the spiral arm model". Values are "around 1.5–2 kpc" [verified: §6.3.4]. Table 4 values are listed above. The widest arms are in optical/NIR, with a drop at 8–24 µm and a second peak in the FIR [verified: §6.3.4, Conclusions (v)]. "We do not note a noticeable arm width increase ... toward the galaxy edge" [verified: §6.3.4]. They quote Savchenko et al. 2020 grand-design widths as "(0.16±0.04)·r25" in one band [verified: §6.3.4].
- Caveat: all images were convolved to 18″ (≈ 0.8 kpc), so these widths are resolution-inflated. Useful only for the ordering (stellar > PAH/hot dust).

### 13. Kim & Ostriker 2002, ApJ — theory (isothermal 2D spiral shocks)
- Fetched: https://arxiv.org/pdf/astro-ph/0111398.
- Table 1 column 7: W/Lx = 0.16, 0.06, 0.05 (hydro H1–H3), 0.11, 0.07, 0.06 (MS1–3), 0.16 ×4 (ME1–4) [verified]. W is the "arm width determined at Σ = (Σmax+Σmin)/2" [verified: §4]. They cite Elmegreen & Elmegreen 1983 for HII-complex spacing along arms, "roughly 3 times (~1-4 kpc) the full arm thickness" [verified: §1] (secondary; not read at source).

### 14. Kim, Kim & Ostriker 2008 (1D) and 2010 (3D) — theory (multiphase spiral shocks)
- 2008: https://arxiv.org/pdf/0804.0139. "These regions occupy 1%, 16%, and 83% of the arm-to-arm distance" (dense arm, transition, interarm) [verified: abstract]. These are one-dimensional simulations [verified: abstract].
- 2010: https://arxiv.org/pdf/1006.4691. "arm, postshock expansion zone, and interarm regions that occupy typically 10%, 20%, and 70% of the arm-to-arm distance" [verified: abstract]. The 3D arm is wider than "one-dimensional spiral shocks where the arm takes up only 1%" [verified: §6]. Setup: Lx = 2R0 sin i/m = 2.5 kpc, m = 2, sin i = 0.1 [verified: §2].
- TIGRESS spiral (Kim, Kim & Ostriker 2020, https://arxiv.org/pdf/2006.05614): confirms Lx = 2πR0 sin i/m as "the arm-to-arm distance" [verified: §2]. No ridge-width number found in the text.

### 15. Dobbs & Baba 2014, PASA (Dawes Review 4) — review
- Fetched: https://arxiv.org/pdf/1407.5062.
- "Although spiral shocks may account for the very narrow dust lanes in galaxies, the width of the shocked region ... is very narrow compared to the width of CO arms in nearby galaxies" [verified: §3.3]. They report that simulations without feedback give HI arms "too narrow ... compared to the Milky Way" (Douglas et al. 2010) [verified: §3.3]. Roberts (1969) is summarised as: "for warm gas and moderate forcing, a narrow shock is expected ahead of the minimum of the potential". For cold gas, a very narrow shock lies "after the minimum" [verified: §3.5]. No numerical width.

### 16. Other fetched items with no usable width number
- Hou & Han 2014, A&A 569, A125 (https://arxiv.org/pdf/1407.7331): no arm width is measured. The only width is a smoothing kernel, "σ = 0.2 is adopted as the Gaussian width" for a tracer density map, and "Different values of σ ... (e.g., 0.05-0.4) yield a similar result" [verified: §3]. This is not an arm property.
- Gittins & Clarke 2004, MNRAS 349, 909 (https://arxiv.org/pdf/astro-ph/0312562): about P-arm/D-arm **offsets** for constraining corotation. Mentions "narrow density peaks" reproduced by codes, but gives no closed-form or tabulated ridge width.
- Kendall, Kennicutt & Clarke 2011 / 2015 (https://arxiv.org/pdf/1101.5764, https://arxiv.org/pdf/1411.5792): no arm-width measurements found in the text.
- Silva-Villa & Cano Gómez 2022 (https://arxiv.org/pdf/2205.00010; NGC 5236, young upper-main-sequence stars): mean 1σ width 0.59 kpc (0.60 kpc by stellar-density method) for the two main arms. Slopes 0.04 ± 0.02 and 0.05 ± 0.02 over R = 2.5–3.5 kpc [verified: §3]. Young stars (≲50 Myr), not gas. One galaxy.
- Wienen et al. 2022, MNRAS 509, 68 (journal page): the Perseus arm "width" is 7.8 km s⁻¹ (a velocity FWHM in ¹²CO), not a spatial width. Not usable.

## What could not be read
- Roberts 1969 (ApJ 158, 123), Shu, Milione & Roberts 1973, Elmegreen 1980, Lynds 1970, Kennicutt & Hodge 1982: not on arXiv, not fetched. Only secondary statements are given above (Dobbs & Baba on Roberts. Marchuk et al. quote Kennicutt & Hodge 1982 as an M51 HII-region perpendicular width of 17″, which is secondary and unverified at source).
- Meidt et al. 2021/2023 and Williams et al. 2022 (PHANGS): not fetched. No arm-ridge width was located for them in this pass.
- Milky Way HI arm widths (e.g. Levine, Blitz & Heiles 2006; Douglas et al. 2010): not fetched. No verified HI ridge width.
- Vallée 2017 arm width "~600 pc" is cited by Colombo et al. 2022 [secondary; the Vallée 2017 source itself was not read].
- Search-engine summaries offered further numbers (e.g. a dust-lane width as "0.5 R50 (0.6 kpc)" in optical-depth maps, and a shock-to-sonic-point arm width "≤10 % of 2.25 kpc"). Neither source was identified or fetched [recall — NOT READ]. Do not use.

## Recommendation to the lead (no numbers from memory)

1. **Default gas-ridge width as a fraction of the perpendicular arm spacing.** Take Gaussian **FWHM ≈ 0.17 × spacing**, i.e. σ ≈ 0.07 × spacing.
   - Basis: Egusa et al. 2017 measures gas and stellar mass arms in the same galaxy, the same way, in azimuth (which converts to a spacing fraction directly). In the inner M51 arms, gas FWHM is ≈ 30° of a 180° spacing and stars ≈ 60°.
   - Two independent supports bracket it. The PHANGS CO/Hα ridge masks (28 galaxies) are 0.5–1 kpc wide, about half the 1–2 kpc broad masks, whose area share is ≥ 0.24; that puts the ridge at ≳ 0.12. The 3D stratified shock simulations of Kim, Kim & Ostriker 2010 put the arm at 0.10 of the spacing, plus a 0.20 post-shock zone.
   - This also fixes the **gas-to-stellar width ratio ≈ 0.5**. Egusa's inner stellar arm (FWHM/spacing ≈ 0.33) is itself narrower than the project's pure cosine (0.50), so the ratio is the more transferable quantity.
2. **Spread for a seeded residual.** Draw the ridge FWHM/spacing over ≈ 0.03–0.30.
   - The low end is Egusa's outer M51 gas (≈ 0.03, resolution-limited and tidally perturbed) and the 1D thin-shock limit (0.01–0.05; Kim & Ostriker 2002, KKO 2008).
   - The high end is the inner-Milky-Way ¹³CO clouds (SEDIGISM, median full width 580 pc, IQR 830 pc) and the maser σ.
   - Per-arm HII-region σ/spacing in Honig & Reid spans ≈ 0.03–0.14 [derived].
3. **Radial trend.** The absolute width grows outward in every observational source that tests it:
   - MW masers: σ = 336 + 36 (R − 8.15) pc.
   - Reid 2014: 42 pc kpc⁻¹.
   - Honig & Reid: 4 galaxies.
   - Savchenko: 86 % of 155 galaxies.

   Because the spacing also grows ∝ R, the width **as a fraction of spacing** is roughly constant in the Milky Way maser data (σ/L⊥ ≈ 0.12–0.14 from R = 5 to 12 kpc with m = 4, ψ = 12° [derived]). Recommended: keep the fraction constant with R, and do not add an extra absolute slope. Egusa's M51 gas ridge narrows in fraction outward (0.17 → 0.03), but that is one tidally perturbed galaxy near its beam limit. Record it as a caveat, not a law.
4. **Dust lanes.** Draw them much narrower than the gas ridge.
   - Width: FWHM ≈ 150 pc, ≈ 1 % of the two-arm spacing at R = 4 kpc (Elmegreen et al. 2014, 5 S4G galaxies, near the resolution limit, so an upper bound).
   - Placement: on the inner/upstream edge, offset from the stellar arm centre by the measured dust-to-old-star separation, median 326 pc over 24 galaxies (Vallée 2020). In the MW, dust → diffuse CO is 315 pc and maser → CO is 250 pc, growing 25 pc kpc⁻¹.

   As a spacing fraction, the dust lane matches the 1D thin-shock dense arm (KKO 2008: 1 %).
5. **Milky Way-specific values.**
   - Young-star arm σ(R) = 336 + 36 (R − 8.15) pc (Reid 2019, masers; four-arm spiral).
   - Molecular-cloud full width (2|offset| median) 580 pc, IQR 830 pc, inner Galaxy −60° < l < 18° (SEDIGISM). This is larger than the maser width by more than ×2 per the authors, partly through kinematic-distance error.
   - No verified MW HI ridge width was found.
6. **Named alternative to record.** The theoretical shock-zone partition of Kim, Kim & Ostriker 2010: arm 10 %, post-shock expansion 20 %, interarm 70 % of the arm-to-arm distance, under Solar-neighbourhood conditions. Its thin 1D limit is the dense arm at 1 % (KKO 2008). The latter is the natural closed-form-free candidate for the dust-lane width, if the lead prefers a theory-anchored ridge over the Egusa empirical one.

---

# Reading C — offsets between the gas ridge, the stellar arm and the young stars (S51, 2026-10-03)

Scope: is the gas/dust ridge offset from (i) the old stellar arm, (ii) the young stars / HII regions, and what does (iii) theory predict for density-wave arms vs swing-amplified/dynamic arms. Lead's working position under test: "swing-amplified arms imply no offset: the gas ridge sits on the stellar arm's crest".

Method: every arXiv source below was fetched as the full PDF from `https://arxiv.org/pdf/<id>`, converted to text, and read at the lines cited. Tags give author/year, journal, arXiv id, section/figure, URL. Quotes are kept under 25 words. Sign conventions differ between papers. Each row gives the paper's own convention.

## Summary table

| Source | Galaxies / coverage | Offset measured (which pair) | Magnitude and sign | Systematic or scatter? | Where read |
|---|---|---|---|---|---|
| Wada, Baba & Saitoh 2011 (ApJ 735, 1) | N-body/SPH, one isolated unbarred multi-arm live disc (m≈4 at 8.6 kpc). Swing-amplified arms | gas vs stellar arm; young stars (<30 Myr) vs gas arm | Gas falls in from both sides and condenses "near the bottom of the potential well". Gas speed relative to the arms ≲15 km/s. No clear young-star offset | No systematic offset | arXiv:1104.1287, abstract, §3 l.130, summary items 3, 6 |
| Baba, Morokuma-Matsui & Egusa 2015 (PASJ 67, L4) | Sims: 4 steady-potential models, plus 2 dynamic (live) snapshots, unbarred t=1.12 Gyr and barred t=2.55 Gyr | dense gas (dust lane) vs stellar potential minimum | Steady model: downstream in the inner disc, upstream in the outer (−45° to +45° over 1–9 kpc for R_CR=10 kpc, as read by Egusa 2017). Dynamic: dust lanes lie along the stellar arms | Steady: systematic radial trend. Dynamic: "no systematic radial dependence" | arXiv:1505.02881, abstract, §3.1–3.2, §4, Fig. 2 |
| Dobbs & Pringle 2010 (MNRAS 409, 396) | Sims: 4 mechanisms (fixed spiral, bar, flocculent/self-gravity, tidal M51) | cluster ages (2–130 Myr) across arms | Fixed spiral and bar: older clusters downstream. Flocculent: arms are "co-spatial both in the stars and in the gas", with no age trend across arms | Systematic only for fixed potential and bar | arXiv:1007.1399, abstract, §5, §6, Fig. 2 |
| Foyle et al. 2011 (ApJ 735, 101) | 12 THINGS/SINGS galaxies (HI–24 µm). 8 with HERACLES CO (H2–24 µm). 3 (NGC 628, 5194, 6946) with H2–FUV and H2–3.6 µm. Plus 4 DP10 sims | HI–24 µm; H2–24 µm; H2–FUV; H2–3.6 µm (gas vs old stars) | Mostly near zero and below resolution. Example: 2.7° for M51 at 80″. Sims without a fixed potential: "less than a few degrees" | "do not show any smooth trend… considerable scatter"; "In none… systematic angular offsets" | arXiv:1105.5141, abstract, §3, §4.1–4.2, §5, §6, Fig. 9 |
| Tamburro et al. 2008 (AJ 136, 2872) | 14 THINGS/SINGS galaxies, HI–24 µm; CO–24 µm for 3 (NGC 628, 5194, 3627) | HI → 24 µm (gas → embedded SF) | "typically a few degrees". t(HI→24µm) = 1–4 Myr. R_cor ≈ 2.7 R_s | Radial trend consistent with R69 (scatter larger than the errors). **Not reproduced by Foyle 2011** | arXiv:0810.2391, abstract, §5.1, Fig. 4, Table 2 |
| Egusa et al. 2009 (ApJ 697, 1870) | 13 galaxies (BIMA SONG / NMA CO + Hα). 12 analysed | CO → Hα (gas → young stars) | 5 "C" galaxies with clear offsets: t_SF ≈ 5–30 Myr. 2 "N" (NGC 4321, 5248, both barred) offsets "almost zero" in the arms. 5 "A" ambiguous | Systematic in 5/12. Zero in 2/12. Ambiguous in 5/12 | arXiv:0904.3121, abstract, §4.1, §5, §6 |
| Louie, Koda & Egusa 2013 (ApJ 763, 94) | M51 only, both arms | CO–Hα; HI–SF tracers | CO–Hα "mostly positive offsets with substantial scatter", up to 25–30° in Arm 1. HI peaks sit almost always downstream of CO and close to the SF peaks | Mostly positive, "not ordered as predicted" by the standard theory | arXiv:1301.2601, abstract, §4, §6 |
| Egusa et al. 2017 (MNRAS 465, 460) | M51, 2 arms, inner (r≤150″) / outer, 6″ ≈ 240 pc | **gas (H2+HI) vs stellar-mass (SED) arm, which is pair (i)** | Values up to ±50°. Inner arm 2 consistent with the galactic-shock trend. Inner arm 1 not. Outer arms near zero, inconclusive | Arm-dependent. Of 4 segments, 1 robustly shock-like | arXiv:1610.06642, abstract, §3.2, §3.3, §5 |
| Kendall, Clarke & Kennicutt 2015 (MNRAS 446, 4155), recapping Paper I 2011 | 13 SINGS 2-arm galaxies | **8 µm (gas shock) vs 3.6 µm stellar m=2, which is pair (i)** | 4 flocculent (no measurable shock). 5 "Regular": 8 µm upstream of the stellar arm inside corotation, with offset growing with radius. 4 "Complex", including M51 | 5/13 systematic; 4/13 scatter with no trend; 4/13 not measurable | arXiv:1411.5792, §4.1.1 |
| Querejeta et al. 2025 (A&A, PHANGS) | 24 galaxies (23 PHANGS-ALMA plus M51). Grand-design biased. 19/24 barred. ~100 pc bins, mostly to ~0.5 R25 | CO–Hα (ii); CO–stellar mass, ICA/NIR (i) | CO–Hα per-galaxy mean: mean 230 pc, median 220 pc, range −400 to +740 pc. Inner half averages 370 pc, outer half 100 pc. Scatter of individual offsets: median standard deviation 1 kpc. CO–NIR mostly positive: mean 433 pc (ICA) / 291 pc (NIRCam F200W) where JWST exists | 4/24 (17%) positive with a declining radial trend. 10/24 (42%) positive with no trend. 10/24 (42%) "no significantly positive offsets" | arXiv:2509.01668, abstract, §2, §4.1–4.3, §5.2, §6 |
| Schinnerer et al. 2017 (ApJ 836, 62) | M51, one northern arm segment (PAWS) with 9 spurs | SF tracers (24 µm, HII, clusters <10 Myr) vs gas arm | Wide spread. HII offsets correspond to times "up to 8 Myr". No single separation time | Scatter, no trend | arXiv:1701.02184, §5.1, §6, Fig. 9 |
| Shabani et al. 2018 (MNRAS 478, 3590) | LEGUS clusters in NGC 1566, M51a, NGC 628 | cluster age (<10, 10–50, 50–200 Myr) vs arm | NGC 1566: significant age gradient. M51a: none (all ages peak about 6° from the arm). NGC 628: no offset | Systematic in 1 of 3 | arXiv:1805.05643, abstract, §7, §8 |
| Pettitt, Tasker & Wadsley 2016 (MNRAS 458, 3990) | Sims of tidally driven spirals | gas arm vs stellar arm | "small yet noticeable", with gas upstream in the mid/outer disc. Size "of the order of 1-2" (unit symbol lost in the text extraction; the context implies degrees) | Small and systematic in the mid-disc | arXiv:1603.07801, abstract, §3 (Fig. 6), §6 |
| Hou & Han 2015 (MNRAS 454, 626) | Milky Way, arm tangencies: Scutum-Centaurus, Near 3 kpc (N), maybe Sagittarius | gas tracers among themselves (RRL, HII, masers, CO, dense gas, HI); gas vs old stars (2MASS/GLIMPSE) | Gas tracers: "no obvious offset". Old-star arm vs gas arm: 1.3°–5.8° in longitude, 120–530 pc, stellar arm exterior to the gas arm (Scutum, N 3 kpc, Sgr) | Same sense at 3 tangencies; Centaurus complex | arXiv:1508.04263, abstract, §3, §4 |
| Vallée 2016 (ApJ 821, 53) / 2014 (ApJS) / 2020 | Milky Way tangents, 88 entries from 18 tracers (2016). Plus a 24-galaxy literature compilation (2020) | ordering of tracers across an arm | MW: mid-arm CO and HI, about 100 pc synchrotron/RRL, about 200 pc masers and cold dust, inner edge hot dust. Half-width CO→hot dust about 340 pc. External compilation: median 326 pc, mean 370 pc | Claimed systematic and mirrored across l=0. 24 of 40 compiled galaxies "positive" | arXiv:1603.08871 abstract; 1409.4801 abstract; 1911.06798 abstract, §5 |

## The theory, as read

**Density-wave / steady-potential prediction (gas shock on the inner edge inside corotation, sign change at corotation).**
- Roberts 1969, as quoted by Gittins & Clarke: "the shock lies just on the inner side of the background [i.e. potential] spiral arm". [verified: Gittins & Clarke 2004, MNRAS 349, 909, arXiv:astro-ph/0312562, §4, https://arxiv.org/pdf/astro-ph/0312562. Roberts 1969 itself was not read]
- Gittins & Clarke 2004 define three arms: P-arm (potential, old stars), D-arm (shock, dust) and SF-arm. They say the offset "should, therefore, vary systematically with radius in a galaxy". If the D–P offset range across radii exceeds about π/4, corotation can be located to about 25 %. [verified: same, abstract and §4]
- The standard offset law, Δφ = (Ω(r) − Ω_p)·t. Tamburro: "Where Ω(R_cor) = Ω_p … we expect the sign of Δφ to change." [verified: Tamburro et al. 2008, AJ 136, 2872, arXiv:0810.2391, §2 Eq. 1, https://arxiv.org/pdf/0810.2391]
- Baba et al. 2015, steady models: dust lanes "are located downstream of the stellar spiral in the inner regions and shift upstream of the spiral in the outer regions". [verified: arXiv:1505.02881, §4, https://arxiv.org/pdf/1505.02881]
- Querejeta et al. 2025 note that even under density-wave theory the CO-vs-potential-minimum offset is less certain than CO–Hα. It "depends on the sound speed of the gas". [verified: arXiv:2509.01668, §2, https://arxiv.org/pdf/2509.01668]

**Dynamic / swing-amplified / transient arms (no systematic offset; gas and stars co-rotate with the arm).**
- Wada, Baba & Saitoh 2011 make the explicit swing-amplification link. If arms are "developed by the swing amplification… both the gas and stellar arms follow the local galactic rotational velocity". [verified: arXiv:1104.1287, §3.2 l.130, https://arxiv.org/pdf/1104.1287]
- Wada et al. 2011, abstract: "without a clear spatial offset between gas spiral arms and distribution of young stars". [verified: same, abstract]
- Dobbs & Baba 2014 review: "For dynamic arms, a systematic offset is not expected between the density peak of the gas, and the stellar minimum". [verified: PASA 31, e035, arXiv:1407.5062, §4 gas-response section, https://arxiv.org/pdf/1407.5062]
- Baba et al. 2015, dynamic models: they "show no systematic radial dependence of the arm-gas offsets". [verified: arXiv:1505.02881, abstract]
- Kendall et al. 2015, on live-potential (Sellwood–Carlberg N-body) gas sims by Clarke & Gittins 2006 and Dobbs & Bonnell 2008: the shocks "tended to trace the regions of instantaneous maximum stellar density". [verified: arXiv:1411.5792, §4.1.1, https://arxiv.org/pdf/1411.5792. The two underlying papers were not read]

**Caveats that cut against "swing-amplified ⇒ no offset".**
- Swing amplification is also the amplifier in the quasi-stationary picture: "The quasi-stationarity of spiral arms requires wave amplification mechanisms such as WASER … or swing amplification". [verified: Dobbs & Baba 2014, §2.1.3]
- Sellwood & Masters 2022: "even swing amplified disturbances that shear at close to the material rate for a while, develop wave-like properties" later on, "when gas and stars stream through the arms". [verified: ARA&A 60, 73, arXiv:2110.05615, §5.3, https://arxiv.org/pdf/2110.05615]
- Sellwood & Masters 2022 describe the transient modes in simulations as "each having a constant pattern speed over a broad radial range", each lasting "several rotations at the corresponding corotation radius". [verified: same, §5.1]
- Querejeta et al. 2025 describe modern simulated spirals as "short-lived rigidly rotating 'groove' modes of the disc shaped by both swing amplification" and changes to the disc. [verified: arXiv:2509.01668, §1]

## Per-source notes

**Wada, Baba & Saitoh 2011** — https://arxiv.org/pdf/1104.1287 (full text).
- Live N-body/SPH disc, 3×10⁶ stars, isolated, unbarred.
- The arms' rotation "mostly follow[s] the galactic rotation Ω(R) at any radii". There is no single pattern speed (§3.1, Fig. 3).
- Gas converges "to form dense gas clouds/filaments near the bottom of the stellar spirals". Each arm's local density changes on about 100 Myr.
- Young stars (<30 Myr) are "roughly associated with the background stellar arms without a clear spatial offset".
- Gas Mach number relative to the arms has a median of about 2 (live) vs 10–40 (rigid).
- No numerical offset is quoted. The claim is qualitative, from Fig. 4 and Fig. 9.
- Coverage: one simulated galaxy, m≈4–7 multi-arm. The authors exclude tidally excited and bar-driven arms from the claim.

**Baba, Morokuma-Matsui & Egusa 2015** — https://arxiv.org/pdf/1505.02881.
- Steady runs: m=2, Ω_p ≈ 23 km/s/kpc, R_CR = 10 kpc, isothermal and multiphase ISM.
- In the steady runs, the shock is upstream except at R<2 kpc and moves further upstream near corotation. The radial trend does not depend on spiral strength, pitch or ISM model.
- Dynamic runs: the angular phase speeds of the arms "follow the galactic rotation at almost all radii or radially decrease".
- Dynamic runs: "the dust lanes are along with stellar spiral arms". The gas "does not flow through the spiral arm".
- No dispersion value is given for the dynamic offsets (Fig. 2 E–F only).
- The authors caution: "the steady and dynamic models are not the only options" (tidal case).

**Dobbs & Pringle 2010** — https://arxiv.org/pdf/1007.1399.
- Four mechanisms. In the flocculent (self-gravitating, transient) model: "short spiral arms which are co-spatial both in the stars and in the gas".
- Arm segments host clusters "of roughly the same age along the arm". There is "no obvious or systematic change in cluster ages across spiral arms".
- Tidal M51 model: "no clear pattern at all".
- Fixed spiral and bar: older clusters downstream.

**Foyle et al. 2011** — https://arxiv.org/pdf/1105.5141 (full text read).
- Method: cross-correlation in annuli, peak search within ±30°, cc > 0.3. Resolution 6″ (HI–24 µm) or 13″ (CO, UV, 3.6 µm).
- Observed: radial profiles show "considerable scatter" and "do not correspond in any way to the model predictions".
- H2–3.6 µm and H2–FUV were done for 3 galaxies only. Only NGC 628 shows any R69-like trend, and "many of these offsets are well below the resolution".
- In DP10 sims without a fixed potential, offsets were "very small (less than a few degrees)".
- The authors' own caveats: interarm SF (at least 30 %), multiple pattern speeds, and elliptical orbits could hide offsets. "there is still room for the possibility that systematic offsets… exists".
- They could not reproduce T08 for NGC 628: T08's offsets were below the 6″ resolution (11° at 30″) and sensitive to the fitting range.

**Tamburro et al. 2008** — https://arxiv.org/pdf/0810.2391.
- 14 galaxies. Offsets "small, typically a few degrees".
- R69-like radial trend fitted: t(HI→24µm) = 1–4 Myr, R_cor/R_s ≈ 2.7 ± 0.2.
- The scatter of the points is "significantly larger than their error bars".
- CO–24 µm offsets (3 galaxies) all "lie closer to zero" than HI–24 µm.
- Superseded in part: Foyle 2011 and Louie 2013 both question HI as the tracer.

**Egusa et al. 2009** — https://arxiv.org/pdf/0904.3121.
- 13 galaxies, CO resolution about 250–500 pc. 5 C / 2 N / 5 A, with 1 excluded.
- C galaxies: t_SF "about 5–30 Myr".
- M51: its two arms differ. Arm 2 (connected to the companion) shows negative dependence and is treated as possibly material.
- N galaxies (NGC 4321, 5248) give offsets "almost zero" in the arm region. Listed causes: material arms, corotation, or elliptical orbits. Both are barred.
- The authors note that a bar "could account for this feature".

**Louie, Koda & Egusa 2013** — https://arxiv.org/pdf/1301.2601.
- M51. HI is contaminated by photodissociated gas: "The HI gas and star forming regions coincide spatially and tend to show small offsets."
- CO–Hα: "mostly positive offsets with substantial scatter", i.e. gas flows through the arm, "though the spiral pattern may not necessarily be stationary".
- Arm wiggles about 200 pc in amplitude add scatter but do not bias the result.
- Implication: which gas tracer is used decides the answer. CO is the right tracer for the ridge.

**Egusa et al. 2017** — https://arxiv.org/pdf/1610.06642.
- This is the direct test of pair (i) in M51: gas mass (CO+HI) vs SED stellar mass, at 6″ ≈ 240 pc.
- Adopted density-wave law (their scaling of Baba 2015): offset(gas−star) = −90/0.8·(r/R_CR − 0.5) degrees, for r = 0.1–0.9 R_CR.
- Inner arm 2 is consistent with that law. Inner arm 1 is not.
- Outer arms: offsets "closer to zero", with too few points to decide.
- They cite Schinnerer et al. 2013: CO-vs-stars offsets "fall within ±10° and no radial dependence" at r ≈ 10–110″. Egusa's own values reach ±50°.
- They attribute the arm-to-arm difference to the companion.

**Kendall, Clarke & Kennicutt 2015** — https://arxiv.org/pdf/1411.5792.
- 13 SINGS galaxies; pair (i) with 8 µm as the shock tracer.
- 9 non-flocculent galaxies show "a general tendency for the 8 µm spiral to be located on the trailing (concave) side of the stellar (3.6 µm) spiral".
- 5 Regular: NGC 3031 plus 3184, 3198, 3938, 4579. 4 Complex, including NGC 5194. 4 Flocculent (no shock), all isolated.
- Their conclusion: "many of the isolated galaxies exhibit the kind of gas response seen in simulations based on live galactic potentials".
- The Regular group is "suggestive of a more long lived spiral pattern".
- Magnitudes are in Paper I figures only (arXiv:1101.5764 Figs 18–45). Not transcribed here.

**Querejeta et al. 2025 (PHANGS)** — https://arxiv.org/pdf/2509.01668. This is the largest and most recent sample.
- Expectation they adopt for dynamical or material spirals: "offsets should randomly scatter around zero… resulting in a zero mean offset". Swing-amplified spirals are listed among "temporary material patterns that rotate with the disc".
- CO–Hα result: 58 % positive, of which 4 galaxies (NGC 1385, 1566, 2283, 4303) have a declining radial trend. Only NGC 1566 turns negative beyond corotation. 42 % show no significant positive offset.
- Pattern speeds fitted for the 4 trend galaxies: about 25–35 km/s/kpc, agreeing with Tremaine–Weinberg.
- CO vs stellar mass (pair i): "predominantly positive, in agreement with the classical picture". Individual CO–Hα and CO–NIR offsets correlate (ρ = 0.43).
- Caveats:
  - Sample biased to grand design; 19/24 barred.
  - The field of view mostly stops at about 0.5 R25.
  - Hα extinction.
  - Circular bins assumed.
  - The 1 kpc scatter partly reflects ~100 pc resolution and interarm SF.

**Schinnerer et al. 2017 (PAWS)** — https://arxiv.org/pdf/1701.02184.
- Studies one M51 arm segment that "belongs to a spiral density wave".
- SF sits in spurs and its offsets scatter. The offset "cannot be explained by simple rotation of the spiral arm pattern".
- The authors speculate the offset depends more on potential strength than on pattern speed.

**Shabani et al. 2018** — https://arxiv.org/pdf/1805.05643.
- NGC 1566 (strong bar, bisymmetric) has an age gradient. M51a and NGC 628 do not.
- It also summarises Chandar et al. 2017 for M51: gas and dust on the inner edge, old stars (3.6 µm) and young clusters on the outer. There is an offset in the inner arm zone (2.0–2.5 kpc) but none at 5.0–5.5 kpc. [verified as Shabani's summary only; Chandar 2017 itself not read]

**Pettitt, Tasker & Wadsley 2016** — https://arxiv.org/pdf/1603.07801.
- Tidal arms are a "middle-ground": "not quite standing density waves… and not quite material arms (with Ω_p = Ω(R) and coincident gas-star arms)".
- The gas–star offset is small, with gas upstream. It is "significantly smaller (of the order of 1-2…)" than in density-wave sims.

**Gittins & Clarke 2004** — https://arxiv.org/pdf/astro-ph/0312562.
- Covered in the theory section. Egusa 2017 summarises their predicted D–P offsets as "range from −30 to 0 degree and monotonically decrease with radius". [verified: arXiv:1610.06642, §3.2.1]

**Dobbs & Baba 2014** — https://arxiv.org/pdf/1407.5062.
- Multiphase fixed-potential gas (Wada 2008) shows "no clear continuous shock". The density peak usually lies "after (on the trailing side of) the potential minimum".
- In dynamic arms gas falls into the minimum "from both sides".

**Sellwood & Masters 2022** — https://arxiv.org/pdf/2110.05615.
- Covered in the caveats above.
- They also judge that offset/age-gradient studies have not settled the matter: "none of these careful studies was able to establish a fixed pattern speed over the entire radial extent". [§5.3]

**Peterken et al. 2019** (Nature Astronomy 3, 178) — https://arxiv.org/pdf/1809.08048.
- One isolated grand-design galaxy, UGC 3825 (MaNGA). Pair: Hα vs stars <60 Myr.
- The offset is consistent with "a pattern speed that varies little with radius". Corotation is about 6 kpc (0.6 R_E).

**Hou & Han 2015** — https://arxiv.org/pdf/1508.04263. Covered in the Milky Way section below.

**Vallée 2014/2016/2020/2021/2022** — the abstracts plus Vallée 2020 §5 were read: https://arxiv.org/pdf/1409.4801, /1603.08871, /1911.06798, /2106.15761, /2203.05542.
- The 2020 compilation counts 46 negative and 45 positive-or-potential results in its Table 1.
- Vallée 2022 claims a MW age gradient of 12.9 ± 1.1 Myr/kpc, "not consistent with… the dynamic transient recurrent waves".

**Reid et al. 2019** — https://arxiv.org/pdf/1910.03357.
- Masers are fitted to log-spirals. It does not discuss masers vs dust lanes.
- Useful scale: arm width w(R) = 336 + 36(R − 8.15 kpc) pc (Gaussian intrinsic width, §3, Fig. 4).

**Also read (abstracts only):**
- Martínez-García et al. 2009 (arXiv:0812.3647): in 13 A/AB galaxies, 10 "present regions that match the theoretical predictions" for azimuthal colour gradients.
- Abdeen et al. 2022 (arXiv:2010.14540): pitch angle falls with SFH age in 12 galaxies, read as favouring the stationary density wave.
- Sakhibov et al. 2025 (arXiv:2504.08283): M51's northern arm profile is consistent with a stationary density wave; the southern arm is not.
- Stuber/Greve et al. 2026 (A&A, arXiv:2605.05302): spine distances measured from 3.6 µm-based masks.
  - NGC 4321 southern arm: CO, HCN and SFR "peak towards the centre… (d ≈ 0 pc)". The northern arm's SFR rises inside-out.
  - M51 southern arm: SFR peaks at about the spine. M51 northern arm: SFR peaks "far behind the spine".

## What could not be read

- **Roberts 1969** (ApJ 158, 123): not fetched; ADS has only scans. Its content above is quoted second-hand from Gittins & Clarke 2004 and Tamburro 2008.
- **Chandar et al. 2017** (ApJ 845, 78): no arXiv id found. Known only through Shabani 2018 §1 and Vallée 2020 §5. Vallée attributes to it 50 pc (dust lane to 3.6 µm), 220 pc (dust lane to massive-star clusters) and 140 pc (dust lane to old-star IR) in M51. [secondary — Chandar not read]
- **Not read; seen only through other papers:**
  - Dobbs & Bonnell 2008, Clarke & Gittins 2006 (via Kendall 2015, Dobbs & Baba 2014).
  - Schinnerer et al. 2013 (via Egusa 2017).
  - Egusa et al. 2004 (via Tamburro: t_CO→Hα ≈ 4.8 Myr for NGC 4254).
- **Not read at all:** Grand, Kawata & Cropper 2012 gas follow-ups; Pettitt, Ragan & Smith 2020 (MNRAS 491, MW young stars); Abdeen 2020 corotation paper; Meidt & van der Wel 2024.
- Grand et al. 2012 itself (arXiv:1112.0019) was read: stellar-only N-body, with the arm pattern speed "almost equal to the rotation curve". It has no gas, so there is no offset measurement.
- [recall — NOT READ] Dobbs & Bonnell 2008 is commonly cited as showing gas "falling into" transient Sellwood–Carlberg arms with no offset. Only Kendall's and Dobbs & Baba's paraphrases were read.

## What the evidence supports for THIS model (no numbers from memory)

**(1) Is "gas ridge on the stellar crest, no offset" supported?** Yes as a model-internal choice, but only conditionally.

- **Theory for co-rotating swing-amplified arms supports it directly:**
  - Wada et al. 2011 tie swing amplification to arms that co-rotate with gas and stars. Gas condenses "near the bottom of the potential well", and young stars show no clear offset.
  - Baba et al. 2015 (dynamic), Dobbs & Pringle 2010 (flocculent), Foyle 2011's DP10 sims ("less than a few degrees") and Kendall 2015's account of live-potential sims agree.
- **Observations allow it for a large minority, not a majority:**
  - Foyle 2011: no systematic offsets in 12/12.
  - Querejeta 2025: 10/24 (42 %) show no significant positive CO–Hα offset.
  - Kendall 2015: 4/13 complex and 4/13 flocculent (no shock).
  - Egusa 2009: 2/12 zero and 5/12 ambiguous.
  - Shabani 2018: 2/3 with no age gradient.
- **Against the implication "swing-amplified ⇒ no offset":**
  - Swing amplification also sustains quasi-stationary waves (Dobbs & Baba §2.1.3).
  - Swing-amplified features turn wave-like later, with gas and stars streaming through (Sellwood & Masters 2022).
  - Modern transient spirals are short-lived modes each with its own constant pattern speed and corotation (Sellwood & Masters §5.1; Querejeta §1).
  - In grand-design, mostly barred samples, the majority show positive offsets: CO–Hα in 14/24 and CO–NIR "predominantly positive" in Querejeta 2025; a systematic upstream 8 µm shock in 5/13 in Kendall 2015.
- **Recommended wording for the ruling:** "zero mean offset, as for co-rotating (dynamic) arms (Wada 2011; Baba 2015; Dobbs & Baba 2014). Observed galaxies split, roughly 40/60, between this and gas crossing the arm (Querejeta 2025)."

**(2) The Milky Way's own tracers.**

| | Vallée (2014/2016/2020) | Hou & Han 2015 |
|---|---|---|
| Ordering across the arm | Fixed, mirrored across l = 0 | No obvious offset among the gas tracers (RRL, HII, masers, CO, dense gas, HI) |
| Positions | CO and HI at mid-arm (called the potential minimum; old stars within error of it). Masers and cold dust about 200 pc inward. Hot NIR/MIR dust at the inner edge, about 340 pc | Old-star arm lies exterior to the gas arm by 120–530 pc at the Scutum, northern Near 3 kpc and possibly Sagittarius tangencies (gas on the Galactic-centre side) |
| Method | Tangent longitudes compiled from the literature | Bump fitting in survey longitude plots |

- The two disagree on where CO sits relative to the masers, and on whether old stars coincide with CO.
- Reid et al. 2019 do not address dust-lane vs maser placement. Their arm 1σ width, about 336 pc at R0, is the same size as both claimed offsets.
- So the MW evidence is contested. Both offset claims are about one arm width. Neither directly tests a co-rotating vs density-wave origin.
- Hou & Han read their result as consistent with a quasi-stationary density wave. Vallée 2022 claims it is inconsistent with dynamic transient arms.

**(3) Best-sourced size of a residual offset a seeded draw could carry.** The evidence supports zero mean plus scatter, not a signed offset.

- **For pair (i), gas ridge vs stellar crest:**
  - Theory for dynamic arms gives less than a few degrees (Foyle 2011, DP10 sims).
  - Tidal sims give "of the order of 1–2" (Pettitt 2016; unit symbol lost in the text extraction, likely degrees).
  - The best-resolved single-galaxy statement is ±10° with no radial dependence in M51 (Schinnerer 2013 as reported by Egusa 2017).
- **For pair (ii), gas vs Hα:**
  - The only large-sample scatter is the PHANGS median standard deviation of 1 kpc, around per-galaxy means of −400 to +740 pc (Querejeta 2025).
  - That scatter includes interarm SF, spurs and stochastic sampling at 100 pc. It is an upper bound on arm-related jitter, not an arm offset.
- **A defensible seeded draw:** zero mean; an azimuthal jitter of a few degrees for the gas ridge vs the stellar crest; a separate spur/feather scatter for young stars and HII regions.
- Any seeded mean offset would need a pattern speed, which the model does not publish.

**(4) The named alternative to record: the density-wave offset law.**
- Δφ(r) = (Ω(r) − Ω_p)·t_SF. Positive (gas → young stars downstream) inside corotation, zero at corotation, negative outside. [Tamburro 2008 Eq. 1; Egusa 2009; Querejeta 2025 §2]
- For gas vs potential, the Egusa 2017 scaling of Baba 2015 applies: offset(gas−star) ≈ −(90/0.8)·(r/R_CR − 0.5) degrees, for 0.1–0.9 R_CR. The shock is on the inner (concave) edge inside corotation (Roberts 1969 via Gittins & Clarke 2004).
- Measured t_SF: 1–4 Myr (HI→24 µm, Tamburro); about 5–30 Myr (CO→Hα, Egusa 2009); 2–12 Myr (CO→Hα, Querejeta 2025).
- The law needs Ω_p. The model publishes Ω_p only for the bar, and Querejeta 2025 (NGC 4303) found the spiral corotation (5.9 kpc) well outside the bar's (3.4 ± 0.2 kpc). So this law cannot be borrowed from the bar. It should stay a recorded, unadopted alternative.
