# READING_ROW_105 — the reading row's register entries: #149, #83, #86, #88, #95, #96, #97 with #98, #103, #118 (c), #129, #131, #135, #162 (S103, D273)

**What this file is (2026-11-17, S103, BUILD_VII row 105, the reading row).** One section per register entry the row
read, beside the three that have files of their own (`READING_LANES.md` for #229 and #234, `READING_HII_SIZES.md`
Part S103 for #235, `READING_DISC_EDGE.md` for #226). Three Opus readers, read-only, wrote the notes this file
carries: RB (`s103_RB.md`, section C: #149), R1 (`s103_R1.md`: #83, #86, #88, #95, #96, #97/#98), R2 (`s103_R2.md`:
#103, #118 (c), #129, #131, #135, #162), all in the session's scratchpad. Each section ends with the gate's ruling
(`DECISIONS.md` D273 items 4-6); the register carries one dated S103 line per entry.

**Tags.** READ — the page fetched at S103 and the sentence, row or equation seen (a summarising fetch, asked for
exact text; quotes are short excerpts as returned); RECALL — memory, founds nothing; NOT READ — the fetch failed or was
not attempted; `[inferred]` — the reader's own arithmetic or connection of a paper to the model. **Every number below
came through an extracting fetch: a builder checks coefficients against the PDF before any build** (D273 item 6).
Nothing here moved a constant, a pin or a model byte.

---

## #149 — NGC 4414's arms' inner radius (reader RB)

- The paper's arXiv id is **1509.05328** (Herrera-Endoqui, Díaz-García, Laurikainen & Salo 2015, A&A 582, A86); RB
  first fetched 1509.06743 by mistake, which is Díaz-García et al. 2016a on bars. cdsarc.cds.unistra.fr refused the
  connection; the CfA VizieR mirror worked.
- READ — VizieR J/A+A/582/A86/table3 ("Properties of spiral arms in the S4G, corrected version sent by the author",
  1 854 rows), `https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=J/A%2BA/582/A86/table3&Name=NGC4414&-out.all`,
  rows as returned (Name, Class, Type, Segment, Pitchang deg, ri arcsec, ro arcsec, Qual):

      NGC4414  SA(r_s)b_c/E3  F  sp1  -30.5  28.7  63.6  2.0
      NGC4414  SA(r_s)b_c/E3  F  sp2  -34.2  19.4  57.3  2.0
      NGC4414  SA(r_s)b_c/E3  F  sp3  -28.1  32.7  87.4  2.0
      NGC4414  SA(r_s)b_c/E3  F  sp4  -44.0  29.2  54.4  2.0
      NGC4414  SA(r_s)b_c/E3  F  sp5   -7.6  57.9  66.3  2.0

- READ (the paper, ar5iv): "G, F, and M for grand design, flocculent, and multiple types"; quality "1.0 = good, 2.0 =
  acceptable"; the radii are the "inner and outer radius at which the different arms where measured", fitted per
  segment on the deprojected image in log-polar coordinates (so deprojected radii `[inferred]`).
- At the template's 17.7 Mpc (`templates.py` `distance_mpc=17.7`, 85.81 pc/arcsec) and h_r = 19.22 arcsec = 1.649 kpc
  `[inferred arithmetic]`: inner radii 2.46, **1.66**, 2.81, 2.51, 4.97 kpc (1.49, **1.01**, 1.70, 1.52, 3.01 h_r);
  the innermost traced arm 19.4 arcsec = **1.66 kpc**, the median inner radius 29.2 arcsec = 2.51 kpc. No segment is
  traced inside 1.66 kpc. Caveat `[inferred]`: an inner radius is where a log-spiral segment was measurable on an S4G
  3.6 µm unsharp mask — an upper bound on where arm structure starts, not a measured amplitude cut-off; NGC 4414's
  SA(r_s) class carries an inner pseudo-ring.
- **The gate (D273 item 4): the owner's** — (i) pin the template's arms' inner radius to the catalogue's innermost
  segment, 1.66 kpc — **recommended**, a measured row replacing an unsourced default — or (ii) permanent.

## #83 — the stellar wind's escape velocity has no Eddington factor (reader R1)

- Vink, de Koter & Lamers 2001, astro-ph/0101509 — READ, sect. 4 item 3, eq. 11: "Gamma_e = L sigma_e / (4 pi c G M) =
  7.66e-5 sigma_e (L/Lsun)(M/Msun)^-1"; σ_e "is the electron scattering cross-section per unit mass", its dependence on
  Teff and composition "described in Lamers & Leitherer 1993". No numeric σ_e printed.
- Vink, de Koter & Lamers 2000, astro-ph/0008183 — READ, sect. 3 item 3: σ_e's "value is taken as determined in Lamers
  & Leitherer 1993"; no number.
- Lamers & Leitherer 1993 (ApJ 412, 771): **NOT READ** (ADS HTTP 405, no arXiv version, no quoting paper found; A&A
  384, 987 PDF HTTP 403; Puls's lecture PDF not extractable).
- The closed form σ_e = σ_T n_e / ρ = 0.2 (1 + X) cm²/g for fully ionized H and He: **RECALL** — it cannot found the
  law under D1 until a page printing it is read.
- **The gate (D273 item 6): NOT DONE.** Stays carried, a reading: LL93, or Kudritzki & Puls 2000 (ARA&A 38, 613).

## #86 — the black hole's mass and the remnant boundaries do not depend on metallicity (reader R1)

- Spera, Mapelli & Bressan 2015, arXiv:1505.05201 — READ (ar5iv, main text and App. C). The fit is SEVN's outputs with
  the delayed supernova model, deviating "by <~10 %" (App. C); the CO-core fit holds for M_ZAMS >~ 7 M☉ (sect. 3).
- **The CO core is a function of M_ZAMS and Z** (eqs. 32-36), so the model's missing CO core is no obstacle: eq. 32
  M_CO = −2.0 + [B1(Z) + 2.0][g(Z, M_ZAMS; K1, δ1) + g(Z, M_ZAMS; K2, δ2)], eq. 33 g = 0.5 / (1 + 10^((K − M_ZAMS) δ)),
  with coefficients in three Z ranges (eq. 34 Z > 4e-3; eq. 35 1e-3 ≤ Z ≤ 4e-3; eq. 36 Z < 1e-3).
- M_rem(M_CO, Z): eqs. 22-31 (p = −2.333 + 0.1559 M_CO + 0.2700 M_CO² below Z = 5e-4; h = A1 + (A2 − A1)/(1 +
  10^((L − M_CO) η)) above, with A1, A2, L, η fitted in Z; f = m(Z) M_CO + q(Z)). The reader's full coefficient list
  is in `s103_R1.md` (#86 item 2); it came through an extracting fetch of an HTML rendering of LaTeX.
- Anchors (main text, READ): "At Z=2.0e-3 (Z=2.0e-4), the maximum BH mass is ~60 Msun (~130 Msun)" (sect. 3.4); the
  maximum "at Z=2.0e-2 ... is ~25" (sect. 3.5); Z☉ = 0.01524 (sect. 2.1). Fryer et al. 2012: not fetched.
- 7.8 M☉ (Özel et al. 2010) is a measured mass; Spera's is a population-synthesis fit (its solar maximum ~25 M☉).
- **The gate (D273 item 6): SOURCED, destination batch R** — Spera et al. 2015 App. C eqs. 22-36, coefficients checked
  against the PDF first. Özel's measured 7.8 M☉ becomes the DISCLOSED CHECK on the fit's mean, and the gate rules on
  the builder's measurement. The 8.5 M☉ white-dwarf / neutron-star boundary is not in the fit and stays as it is.

## #88 — row 31 passes on an unsourced Ia yield (reader R1)

- Weinberg, Andrews & Freudenburg 2017 (WAF17), arXiv:1604.07435 — READ, sect. II.2 eq. 2 and Table 1: "the
  time-integrated yield is m_Fe^Ia = 0.0017"; Table 1 "IMF-integrated SNIa iron yield" 0.0017. Its derivation (same
  paragraph, as extracted): K_Fe^Ia = 0.77 M☉ "based on the W70 model of Iwamoto et al. 1999", R0 = 2.2e-3 per M☉
  "based on Maoz & Mannucci 2012" — 0.77 x 2.2e-3 = 0.0017.
- Maoz & Graur 2017 (MG17), arXiv:1703.04540 — READ, sect. II: volumetric rates "N/M* = 1.3 +- 0.1 SNe per 1000" M☉;
  field galaxies, all DTD measurements combined, "N/M* = 1.6 +- 0.3 SNe per 1000"; clusters (5.4 ± 2.3)e-3. Sect. III
  eq. 2: mean Ia iron 0.7 M☉. **MG17 print two field values (1.3 and 1.6); the register carries both.**
- **The split source.** The model divides WAF17's 0.0017 by MG17's 0.7: 2.43e-3 events per M☉ — **a number neither
  paper states**.
- Row 31 under each reading `[inferred: the rate linear in Y_FE_IA / IA_IRON_MASS, base 0.65332 /century]`: WAF17
  whole 0.594 /century (under the 0.6 floor by 0.006); MG17 field DTD 0.430; MG17 volumetric 0.350; as now 0.653.
- **The gate (D273 item 6): the owner's** — (i) WAF17's own pair (0.0017 = 0.77 M☉ of iron per Ia x 2.2e-3 events per
  M☉) — **recommended**: the one pair printed together, it misses row 31's floor by 0.006 (0.594 against 0.6 per
  century) and #89 is the named mend — or (ii) MG17's 1.3e-3 or 1.6e-3 (0.350, 0.430).

## #95 — is the clusters' slope window the clusters'? (reader R1)

- The window (repo, READ): `tests/test_clustering_gate.py` TARGET_SLOPE = −0.64, "Grasha et al. 2017a Table 4's two
  branches' ratio (D220 II item 2)", SLOPE_WINDOW 0.15; asserted on clouds and clusters alike.
- Grasha et al. 2017a, arXiv:1704.06321 — READ, Table 4 "Power-Law Parameters for Weighted Average", age ≤ 40 Myr:
  classes 1, 2, 3: α1 −0.85(3), break 112 pc, α2 −0.21(2); classes 1, 2: α1 −0.60(3), break 186 pc, α2 −0.139(19).
  The paper measures star clusters and associations only — no molecular clouds.
- Clouds' own measured slopes about −0.2 (NGC 7793 −0.18(2); M51 PAWS −0.09(3); PHANGS median −0.26) — READ at
  S61/S96 (`READING_CLUSTERING.md` sect. 3.1), not re-fetched.
- The model's clusters are 0 to ~20 Myr `[inferred]`, inside Table 4's ≤ 40 Myr cut.
- **The gate (D273 item 6):** the −0.64 is Grasha et al. 2017a Table 4, clusters only, ≤ 40 Myr, classes 1-3: **the
  window IS the clusters'**. S100's built-not-merged offset stays unmerged, and the borrowed target is the clouds'
  (clouds measure about −0.2). The compact-cluster row (−0.60 − (−0.139) = −0.461) is disclosed and **NOT chosen**:
  picking a target with the answer known is B5's breach. Stays carried; it joins the owner's clustering questions
  (#80, #233, #223).

## #96 — the cluster census inherits the clouds' mass function (reader R1)

- Krumholz, McKee & Bland-Hawthorn 2019, arXiv:1812.01615 — READ (first 100 000 characters), sect. 2.2: disc clusters
  "with values of alpha_M = -2 +- 0.2", measured over ~1e3 to 1e5 M☉; "The lower limit on this range is entirely a
  function of observational limitations"; M31 "Mc ~ 8.5e3". Sect. 2.4: Γ "~0.01-0.1". Sect. 4 (cloud-to-cluster
  mapping): NOT READ (past the fetched part).
- Lada & Lada 2003, astro-ph/0301540 — READ, sect. II.1: a cluster is "a group of 35 or more physically related stars
  whose stellar mass density exceeds 1.0" M☉ pc⁻³; sect. II.4 a characteristic cluster mass of 50 M☉; abstract: "Less
  than 4-7% of embedded clusters survive emergence".
- **The gate (D273 item 6):** a definition (Lada & Lada 2003 sect. II.1) and a DISCLOSED CHECK for batch R (Krumholz et
  al. 2019 sect. 2.2: slope −2 ± 0.2 over 1e3-1e5 M☉; the census's −1.6 inner sits outside by 0.2 `[inferred]`, the
  outer −2.2 inside); the cloud-to-cluster mass relation was not found and that clause is declared permanent within
  the entry. Stays carried to batch R.

## #97 with #98 — the bound mass before survival; row 32 against the Harris catalogue (reader R1)

- Lamers et al. 2005, astro-ph/0505558 — READ: t0 = 3.3 (+1.5/−1.0) Myr (sect. 6.3, the solar neighbourhood); γ =
  0.62; "a factor 5 shorter than derived from N-body simulations"; the cause offered: "encounters with giant molecular
  clouds may also shorten the lifetime of open clusters" (sect. 7). No halo orbits discussed.
- Baumgardt & Makino 2003, astro-ph/0211471 — READ: eq. 7 T_diss[Myr] = β (N / ln(0.02 N))^x R_G[kpc] (V_G / 220
  km/s)^−1; W0 = 5: x = 0.75, β = 1.91; W0 = 7: x = 0.82, β = 1.03; eq. 8 eccentric orbits x (1 − ε), R_G apogalactic.
  Logarithmic potential, no GMCs `[inferred from the setup]`.
- VandenBerg et al. 2013, arXiv:1308.2257 — READ: 55 GCs, the oldest ~13.0 Gyr; Pal 12 "an unusually young system,
  with an age near 9 Gyr". Table 2 (the ages): NOT READ (three fetches).
- **The disclosure the reader asked for:** S34 already measured the old survivors at both dissolution times (−1.87 dex
  at 3.3 Myr, +0.09 dex at the N-body t0), so any choice now is made after the measurement.
- **The gate (D273 item 6): the owner's** — (i) Baumgardt & Makino 2003 eqs. 7-8 for clusters older than about 9 Gyr
  (halo orbits, no molecular clouds), Lamers et al. 2005's five-times-shorter time for the disc — **recommended**, on
  the physical ground only (the two papers name the cause of the difference) — or (ii) the model as it is.

## #103 — the remnant count from a visible lifetime; the shell physics (reader R2)

- Green 2019, arXiv:1907.02638 — READ, sect. 4.2: a surface-brightness completeness limit Σ ≈ 10⁻²⁰ W m⁻² Hz⁻¹ sr⁻¹ at
  1 GHz, "the current catalogue contains 67 remnants with a surface brightness above" it; asked for an age distribution
  or a total, the fetch found none. Green's statistics are selection statistics; no age distribution, no census.
- Ranasinghe & Leahy 2023, arXiv:2302.06593 — READ, sect. III.3: "Most of the literature ages (>95%) are <65 kyr";
  "The sample is likely nearly complete for the SNR ages <2 kyr, but the incompleteness is a factor of ∼2 for SNR ages
  <14 kyr"; old remnants "are not bright enough to have an easily measured X-ray spectrum"; Conclusions item 4: "A
  birthrate of 1 SN in 58 yr fits the SNR age distribution for t<2 kyr". No visibility lifetime stated.
- Ball et al. 2023, arXiv:2307.01948 — READ, sect. 1: "1000 to 2700 radio supernova remnants should be detectable in
  our Galaxy"; "So far we have only discovered somewhere in the range of 300 to 400" — a prediction (rate x
  Sedov-Taylor lifetime), not a census.
- Leahy & Williams 2017, arXiv:1701.05942 — READ, sect. III.1.4: "Here the shock is assumed to be a strong shock with
  compression ratio of 4".
- The radiative shell's ionization state: **NOT READ** (no source fetched).
- **The gate (D273 item 5):** the count's lifetime clause is PERMANENT within the entry (no survey prints a complete
  age distribution: Green 2019 sect. 4.2, Ranasinghe & Leahy 2023 sect. III.3), with one disclosed check for batch R
  (the model's 1 464 inside Ball et al. 2023's predicted 1 000-2 700 detectable remnants — a prediction, said so); the
  Sedov jump clause CLOSES on Leahy & Williams 2017's stated compression ratio of 4; the shell's ionization-state clause
  was NOT READ. The entry stays carried, restated to that one clause.

## #118 (c) — which ionization parameter the grid is read at (reader R2)

- Byler et al. 2017, arXiv:1611.08305 — READ, sect. II.1.1: a spherical shell, R_inner fixed at 10¹⁹ cm, n_H = 100
  cm⁻³; sect. II.1.4, eq. 1: U ≡ Q_H / (4π R² n_H c), U0 at the inner radius; Cloudy computes U at the Strömgren
  radius, and **"The distinction does not matter for a thin spherical shell, the geometry assumed in this work."**;
  "any combination of Q_H, R_inner, and n_H that produces the same value of U₀ will produce the same nebular spectrum".
  No recipe for mapping a filled sphere's or a volume-averaged U onto U0.
- Gutkin, Charlot & Bruzual 2016, arXiv:1607.06086 — READ, sect. 2.2, eqs. 5-8: U_S at the Strömgren radius; eq. 8
  "U_S(t′) ≈ <U>(t′)/3", "valid for r_in ≪ R_S"; models parametrized by the zero-age U_S.
- The reader proposed the owner's ((i) keep the read point, recommended; (ii) the volume mean).
- **The gate (D273 item 5): CLOSED by the reading, the gate's** — Byler et al. 2017 sect. II.1.4 says the inner face
  against the Strömgren radius "does not matter for a thin spherical shell"; the model keeps its read point and nothing
  moves. The volume-mean alternative (Gutkin et al. 2016 eq. 8, U_S about <U>/3) is named in the entry. #118's other
  clauses are untouched.

## #129 — the gas ridge's width is one galaxy's number (reader R2)

- Querejeta et al. 2024, arXiv:2405.05364 — READ (both halves): no table prints per-galaxy or per-segment widths or
  contrasts (Tables 3, 4 captions read).
- Colombo et al. 2022 (SEDIGISM), arXiv:2110.06071 — READ, sect. 5.3: Milky Way molecular arms "a global median of ∼580
  pc, but with a broad inter-quartile range IQR∼830 pc" (twice the clouds' offset to the arm); no arm-separation
  comparison. Already in the register.
- A web search found single galaxies only (M31's CO arms 1-2 kpc, snippet — NOT READ).
- **The gate (D273 item 5): the owner's** — (i) permanent — **recommended** — or (ii) measured from the PHANGS-ALMA maps,
  a download, which is the owner's to order.

## #131 — the gas contrast's galaxy-to-galaxy scatter (reader R2)

- Querejeta et al. 2024 — READ: Fig. 3's caption ("Range of contrasts for each spiral segment per galaxy");
  sect. 3.1: contrasts "from just a few percent up to ∼10 in the most extreme cases" (over radial bins); sect. 4.2:
  "even mean values over entire spiral segments, show significant scatter around this relation" — **no number for the
  scatter is printed**; no table of per-galaxy or per-segment contrasts. Fig. 3 itself is an image: NOT READ (a
  digitised figure is not a READ number, D1).
- **The gate (D273 item 5): PERMANENT, the gate's** — no scatter number and no per-galaxy table is printed; the model's
  spread stays the stellar draws', no residual drawn.

## #135 — the model's K light per unit stellar mass (reader R2)

- Just et al. 2015, arXiv:1504.05808 — READ, sect. 3.3: "The local mass density implies a mass-to-light ratio of the
  stellar component in the local volume of M/L_K = 0.31 ± 0.02 M⊙/L_K⊙"; sect. 3.4: "It implies a K band mass-to-light
  ratio of M/L_K = 0.34 M⊙/L_K⊙" (the solar cylinder, white and brown dwarfs counted, masses empirical: no IMF, no
  population synthesis); sect. 3.5: total M_K = −24.2; **sect. 3.2: M_K☉ = 3.27 mag** (citing Casagrande et al. 2012).
- Search snippets only, not usable: arXiv:2311.17202, Martinsson et al. 2013, Drimmel & Spergel 2001.
- **The gate (D273 item 5):** a SOURCED disclosed check for batch R — M/L_K 0.31 ± 0.02 locally, 0.34 for the solar
  cylinder, against the model's about 0.73: **a miss of 2.1x**, recorded as measured, its cause named by the builder
  (which populations carry the K light) before anything is mended. The entry's recalled M_K,☉ 3.27 is now READ (sect.
  3.2). Stays carried.

## #162 — the young stars' clustering fades in one step (reader R2)

- Turner et al. 2022, arXiv:2209.02872 — READ, Table 4: "Best-Fitting Power Law Slopes and Amplitudes at 300 pc", the
  amplitudes 1 + ω(θ), angles converted "in units of parsecs" — **the unit is printed: 1 + ω at 300 pc**. The rows
  re-read match `READING_CLUSTERING.md` 1.4's transcription. The fit range is "constrained to the distance ranges marked
  by the thick grey lines in Figure 10" — no range in pc. "each galaxy shows a steeper power-law slope for the younger
  clusters than for the older clusters" (except NGC 4571).
- Medians over the eleven rows `[inferred]`: 1 + ω(300 pc) all 2.86, ≤ 10 Myr 3.43, > 10 Myr 2.26, GMCs 2.19 (the
  slip at `READING_CLUSTERING.md` line 139 mended at S103). Under a log-normal field σ²(>10)/σ²(≤10) = ln 2.26 / ln
  3.43 = 0.66 `[inferred]`. Grasha 2019's M51 series read in pc at 300 pc (2.35 / 1.87 / 1.36 / 1.41) sits in Turner's
  order, where an arcsec reading would not — supports, does not prove, S96's pc inference.
- **The gate (D273 item 5):** a SOURCED disclosed check for batch R (Turner et al. 2022 Table 4: 1 + ω at 300 pc,
  medians 3.43 at ≤ 10 Myr and 2.26 above `[inferred]`); the four-bin width law still rests on Grasha et al. 2019 and
  stays `[inferred]`. Stays carried.

## Not read, by entry

- #83: Lamers & Leitherer 1993 (ADS 405), Kudritzki & Puls 2000 (not fetched); the Thomson closed form RECALL only.
- #86: Fryer et al. 2012 (not fetched); Spera's coefficients through an extracting fetch, unchecked against the PDF.
- #96: Krumholz et al. 2019 sect. 4. #97/#98: VandenBerg et al. 2013 Table 2.
- #95: He et al. 2026 (clouds against a CO-following control). The other #95 clauses (offset shape, density gradient,
  remnant state) not searched.
- #103: the radiative shell's ionization state. #118: Byler's page past 100 000 characters.
- #129: no sample-wide ridge width exists in what was read. #131: Querejeta 2024 Fig. 3's values (image); CANFAR's
  listing not retried. #135: arXiv:2311.17202, Martinsson 2013, Drimmel & Spergel 2001 (snippets).
- #149: cdsarc (ECONNREFUSED); the ReadMe's notes (taken from the paper).
