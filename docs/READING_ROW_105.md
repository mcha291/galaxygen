# READING_ROW_105 — the reading row's register entries: #149, #83, #86, #88, #95, #96, #97 with #98, #103, #118 (c), #129, #131, #135, #162 (S103, D273; batch R's measurements, Part S104, D274)

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
- The gate's first ruling (D273 item 6) was NOT DONE; **item 9 replaces it** on the second reading below.

**The second reading (reader RT, `s104_RT.md` section B).**
- The code: `stages/massive_stars.py` applies **no Γ_e at all** — the comment: σ_e "taken as determined in Lamers &
  Leitherer 1993", a value S28 could not read, "So Gamma_e is not applied: v_esc here is the Newtonian sqrt(2GM/R)";
  `VINK_JUMP = (61.2, 2.59, -14.94, 0.85)` is eq. 23 without its 3.2 Γ_e term. No σ_e constant anywhere under
  `model/galaxy`.
- Vink, de Koter & Lamers 2000, astro-ph/0008183 — READ (transcribed): Table 1, twelve series (log L, M, Γ_e, M_eff),
  each over Teff 12.5-50 kK with one Γ_e: 4.5/15/0.055; 4.5/20/0.041; 5.0/20/0.130; 5.0/30/0.087; 5.0/40/0.068;
  5.5/30/0.274; 5.5/40/0.206; 5.5/50/0.165; 5.75/45/0.325; 6.0/60/0.434; 6.0/80/0.326; 6.25/120/0.386.
- σ_e = Γ_e M / (7.66e-5 L) from those rows `[inferred, arithmetic on a READ table]`: eleven of twelve give **0.340 ±
  0.002 cm²/g** (the rounding of Γ_e); series 5 gives 0.355 (its M_eff matches its own 0.068: an outlier not
  explained). Vink et al. 1999 (astro-ph/9908196) sect. 5 — READ: Γ_e = 0.130 for L = 1e5 L☉, 20 M☉ -> 0.339. So the
  recipe's own grid used one σ_e, 0.34, independent of Teff over 12.5-50 kK `[inferred]`. That 0.34 = 0.2 (1 + X) at
  X = 0.70 is the Thomson form — RECALL. Lamers & Leitherer 1993: still NOT READ; Kudritzki & Puls 2000: NOT FETCHED.
- What it would move `[inferred, from massive_stars.py's own formula]`: Γ_e 0.041-0.434 over Vink's grid, v_inf
  overstated by (1 − Γ_e)^−1/2 = 1.02-1.33x, the wind power by 1.04-1.77x, the jump 0.3-3.6 kK too cool.
- **The gate (D273 item 9, replacing item 6's "NOT DONE"):** #83 stays carried, its closer restated: the recipe's
  effective escape speed (1 − Γ_e) applied with σ_e 0.34, destination **batch R**, the builder's measurement of what it
  moves first.

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

- #83: Lamers & Leitherer 1993 (ADS 405, scan only), Kudritzki & Puls 2000 (not fetched); the Thomson closed form
  RECALL only; σ_e 0.34 is back-solved from Vink et al. 2000's Table 1, not printed.
- #86: Fryer et al. 2012 (not fetched); Spera's coefficients through an extracting fetch, unchecked against the PDF.
- #96: Krumholz et al. 2019 sect. 4. #97/#98: VandenBerg et al. 2013 Table 2.
- #95: He et al. 2026 (clouds against a CO-following control). The other #95 clauses (offset shape, density gradient,
  remnant state) not searched.
- #103: the radiative shell's ionization state. #118: Byler's page past 100 000 characters.
- #129: no sample-wide ridge width exists in what was read. #131: Querejeta 2024 Fig. 3's values (image); CANFAR's
  listing not retried. #135: arXiv:2311.17202, Martinsson 2013, Drimmel & Spergel 2001 (snippets).
- #149: cdsarc (ECONNREFUSED); the ReadMe's notes (taken from the paper).

---

## Part S104 — batch R's measurements of the entries this row sourced (D274)

**What this part is (2026-11-17, S104, batch R).** D273 sent five of this file's entries to batch R with a disclosed
check or a build. Two builders measured them: RS (`s104_RS.md`: #86, #83 - measured, NOT built, `r-remnants` holds no
commit) and RC (`s104_RC.md`: #135, #136, #162, #96, #103 - six records "DISCLOSED, as measured" in
`tests/test_disclosed_s104.py`, integrated into `batch-r`). The gate's rulings are `DECISIONS.md` D274 items 3, 4 and 6.
Same tags as above; this time **the sources were re-read from the PDF** where a coefficient was to enter code.

### #86 — the remnant masses by Spera, Mapelli & Bressan 2015: read from the PDF, measured, not built

- **D1 met for the reading.** arXiv:1505.05201 fetched as a PDF and its text extracted (App. C, "GENERAL FITTING
  FORMULA FOR Mrem", PDF pp. 19-20). The arXiv PDF numbers the equations C1-C15; the journal (and ar5iv) 22-36. Every
  coefficient agrees with the S103 reader's list; no digit differs. Preamble READ: "obtained by fitting the outputs of
  SEVN with the delayed SN model and the PARSEC stellar evolution isochrones ... deviate from the outputs of SEVN by
  <~ 10 %". Validity M_ZAMS 7-150 M☉, Z 1e-4 - 2e-2; Z☉ = 0.01524 (sect. 2.1); NS below 3.0 M☉, BH above (sect. 2.3);
  App. B eq. B4 M_grav = 0.9 M_bar for BHs.
- **Cross-checks against the paper's own tables** (SEVN, delayed): the NS / BH transition M_ZAMS 18.8 / 18.2 / 18.2 at
  Z = 2e-2 / 2e-3 / 2e-4 -> the fit 18.67 / 15.46 / 16.35; the largest BH 25 / 58 / 130 -> the fit 25.6 / 61.5 / 125.0.
  Eq. 6 × 0.9 against the fit at Z = 1e-4 within 2 % (30 M☉ 18.97 / 18.64 ... 150 M☉ 129.8 / 128.8). Monotonic in
  M_ZAMS at each Z tested; continuous at M_CO = 5 and 10.
- **The seam (the unphysical finding).** At Z = 5.0e-4 (C1 -> C4, [Fe/H] ~ −1.48) the remnant mass **jumps by up to
  5.89 M☉** (at M_ZAMS 64), by more than 10 % over M_ZAMS 10.7-70; at 20 M☉ 5.69 -> 9.07 (+59 %). At Z = 1e-3 up to 0.28
  M☉; at 2e-3 and 4e-3 continuous to rounding. On the model's isochrone nodes the seam falls between [M/H] −1.70 and
  −1.45, so **M_rem is not monotonic in Z** for 12-30 and 60 M☉ (20 M☉: 5.69, 9.10 at −1.45, 7.41, 6.23, 4.07 ...); the
  NS / BH cut in M_ZAMS by node 16.35 ... 12.93 (−1.45) ... 18.67 (+0.30). Two sides of a 59 % jump cannot both be
  within the paper's "<~10 %" of a continuous SEVN curve `[inferred]`.
- **What it would move** (a monkeypatch, the production grid; `default` = `milky_way`):

| | before (`milky_way`; `ngc_4414`) | after, `milky_way` | after, `ngc_4414` |
|---|---|---|---|
| BH mean (integral, number-weighted) | 7.80 M☉ | 15.00 | 16.07 |
| BH sample mean / median / p5 / p95 / max | 7.8 flat | 14.72 / 12.87 / 3.35 / 36.26 / 89.3 | 15.43 / 12.91 / 3.34 / 39.62 / 78.0 |
| NS mean (integral); sample range | 1.331; 1.33 | 1.634; 1.27-2.99 | 1.620; 1.27-3.00 |
| NS / BH boundary (solar) | 25 M☉, a 1.33 -> 7.8 jump | 18.6 M☉, continuous at 3.0 | same |
| `remnant_mass_fraction` | 0.2127; 0.2382 | 0.2589 | 0.2894 |
| effective return | 0.4137; 0.4253 | 0.3772 | 0.3838 |

  The register's prediction ("the remnant fraction moves by under 1 %") is wrong: +22 %, because the fit's BHs are
  about twice Özel's even at solar Z. The BH mean by [M/H] −2.19 .. +0.30 at 12.6 Gyr: 25.1 ... 11.8 (before 7.8 flat).
  The model's top Z 0.030 lies outside the fit's 2e-2 (clamped in the measurement). Downstream only `star_remnant`,
  `star_remnant_mass` and `remnant_mass_fraction` read the remnant masses.
- **The disclosed check:** Özel et al. 2010 (arXiv:1006.2834, abstract READ) "a narrow mass distribution at 7.8 ± 1.2
  Msolar" from sixteen transient low-mass X-ray-binary black holes (a selected sample). The fit's mean 15.0 (16.1),
  median 12.9: about twice; Özel's 7.8 sits near the fit's 30th-40th percentile `[inferred]`.
- **The gate (D274 item 3):** D273's "sourced, destination batch R" WITHDRAWN on the measurement; #86 stays carried,
  its closer restated - a remnant-mass law continuous in metallicity (Fryer et al. 2012's delayed prescription on the
  isochrones' own core masses if the tracks carry them, or Spera's fit with its seam's cause read - a reading first),
  Özel's mean and the gravitational-wave black holes' masses the two disclosed checks.

### #83 — Γ_e with σ_e 0.34: measured, not built

- Vink, de Koter & Lamers 2001 READ from the arXiv PDF: eq. 11 "Gamma_e = L sigma_e / 4 pi c G M = 7.66 10^-5 sigma_e
  (L/Lsun)(M/Msun)^-1" (σ_e's Teff and composition dependence "described in Lamers & Leitherer 1993"); eq. 23
  "log<rho> = -14.94 (+-0.54) + 0.85 (+-0.10) log(Z/Zsun) + 3.2 (+-2.2) Gamma_e"; eq. 15 T_jump = 61.2 + 2.59 log<ρ>.
  Eqs. 24-25 use fixed ratios 2.6 / 1.3, so the mass loss moves only through the jump; v_∞ through M_eff = M(1 − Γ_e).
  σ_e = 0.34 `[inferred, S103's back-solve]`.
- The grid: every isochrone node with M_now ≥ 8 M☉ inside 12.5-50 kK (157 668 nodes). min / p5 / median / p95 / max:
  Γ_e 0.009 / 0.020 / 0.120 / 0.526 / 1.111 - **133 nodes at Γ_e ≥ 1** (v_esc imaginary; Vink's grid tops at 0.434);
  the mass loss after / before 1 / 1 / 1 / 19.3 / 126.7 - **8 995 nodes (5.7 %) flip to the cool side** (the jump
  hotter by 8.3 Γ_e kK); the v_∞ ratio 0.006 / 0.46 / 0.937 / 0.990 / 0.995; the wind power ratio 0.0012 / 0.50 /
  0.889 / 2.54 / 29.4. Per mass formed (the clusters' and bubbles' wind) by log age at solar: 0.78, 0.76, 0.95, 1.06,
  1.13 (6.6-7.0), then 0.97-1.0; integrated over age **0.80-0.86 at every metallicity** (−14 to −20 %). The catalogues
  hold one / no star with a wind. Final masses and the returned mass do not move (PARSEC's).
- The Γ_e ≥ 1 nodes would turn NaN and then zero in `population_wind` silently; a hydrogen-poor star's σ_e is under
  0.34, and the Thomson form in X is RECALL.
- **The gate (D274 item 4):** D273 item 9 amended - #83 stays carried, not built; what kills it: σ_e as a function of
  the surface hydrogen READ (Lamers & Leitherer 1993 or the Thomson form in a fetched source) and the recipe's stated
  range in Γ_e READ, then the build with the nodes outside the range declared.

### The disclosed checks (lane RC; `tests/test_disclosed_s104.py`, six records "DISCLOSED, as measured", not judged)

The default galaxy (= `milky_way`'s inputs), the production grid (n_R 400, n_t 2000), at 8fed299; `ngc_4414` read and
not pinned.

- **#135, M/L_K at the solar column.** Definition: the ring nearest R_SUN 8.2 (R = 8.2125 kpc); the K light = the sum
  over formation steps of the mass formed (`stars_formed_history` / (1 − 0.30)) × the population's K flux (the light
  stage's own sum), with M_K☉ 3.27 (READ at S103); the mass as counted = `stellar_surface_density`; the mass by kind
  from `remnants`; K by phase from each isochrone segment's PARSEC label (MS 0-1, SGB + RGB 2-3, core He burning 4-6,
  AGB 7-8; closes to 6e-16). Σ_K 66.89 L_K☉/pc²; the locked mass 36.04 M☉/pc²; **M/L_K 0.539** against Just et al.
  2015's 0.34 (the solar cylinder; 0.31 ± 0.02 locally): **a miss of 1.6x**. The galaxy's own stellar mass / L_K 0.703
  (M_K −23.802) - the entry's "0.73" / 2.1x was that, set against a local column. By kind: living 24.84, white dwarfs
  4.49, neutron stars 0.53, black holes 0.92 = 30.78 physical (5.26 returned by the isochrones beyond 0.30 but counted
  locked); the physical M/L_K 0.460 (1.35x). Just et al. (sects. 3.2-3.4, an extracting fetch): Σ_K 98.7 (giants 82.5,
  dwarfs 16.2), 33.3 M☉/pc² with white and brown dwarfs. K by phase: MS 12.31, SGB + RGB 23.27, CHeB 10.30, AGB 21.01
  (the giants 54.6 = 0.66x Just's; the MS 0.76x). K by age: < 0.1 Gyr 0.105, 0.1-1 0.157, 1-3 0.225, 3-6 0.259, 6-9
  0.215, 9-11 0.037, 11-14 0.002. **The cause: too little K light, not too much mass**; a quarter of the miss is the
  locked mass's bookkeeping. The gate (item 6): carried, the closer a reading of the giants' K light.
- **#136, the face-on disc's attenuation.** Definition: the `/api/render` frame, layer off (as the colour check is
  judged), B and V through `band_curve`, face-on through the layered transmission (the clouds' share in their layer);
  A = mag(through the dust) − mag(the stars alone), the disc summed over the frame (the bulge excluded unless said).
  `milky_way`: extinction alone A_B 0.377, A_V 0.383; with the scattered light **A_B 0.326**, A_V 0.329, **E(B−V)
  −0.003**; with the undimmed bulge A_B 0.308; the check's B − V 0.5664; light-weighted τ_B 3.14; A_B by R 0.958 (0-2
  kpc), 0.863, 0.675, 0.381, 0.114, 0.011 (13-30). `ngc_4414`: 0.404 / 0.436; **0.359** / 0.388, **E(B−V) −0.029**; the
  check 0.6441 (S99's, the anchor); τ_B 8.95. Against Driver et al. 2007's 0.20 ± 0.04 a miss (1.6-1.8x over); against
  Tuffs et al. 2004's 0.067-0.088 `[inferred from READ tables]` a miss **of the wrong sign**. Sources as S101's reader
  R3 read them, not re-fetched. The gate (item 6): carried with #47; the record stays in the test file.
- **#162, the young clusters' clustering.** The census 13 124 clusters, 0-20 Myr (6 580 ≤ 10, 6 544 above).
  Instrument: `specs.clustering.against_uniform` (Landy-Szalay, randoms 10x, seed 61), the power law fitted over
  100-2000 pc, A = 1 + ω at 300 pc from the fit. `milky_way`, the 6 kpc square at R_SUN: ≤ 10 Myr n 281, **A 1.3755**
  (the gate's square anchor holds); 10-20 Myr n 259, **A 1.1970**; the 300 pc bin itself 1.066 / 1.093. The annulus
  (the whole disc) 10.335 / 10.777, the radial profile's. `ngc_4414`: square 1.342 / 1.273, annulus 18.03 / 18.07.
  Against Turner et al. 2022's medians 3.43 / 2.26 `[inferred]`: a miss, and not like for like (one face-on galaxy,
  every cluster against detected ones, another footprint and fit range; the model's "above 10 Myr" ends at 20;
  Turner's upper age NOT READ). The gate (item 6): carried, with the owner's clustering questions.
- **#96, the clusters' mass function.** `cluster_mass` in [1e3, 1e5] M☉, every cluster 0-20 Myr: n 5 420, the
  maximum-likelihood index (a truncated power law, Fisher error) **−1.870 ± 0.014**, least squares on ten logarithmic
  bins −1.947; ≤ 10 Myr −1.889 ± 0.020 / −1.969; the masses 10 - 2.3e5, 21 above 1e5. `ngc_4414` −1.912 ± 0.022 /
  −1.996 (n 2 310). Against Krumholz et al. 2019's −2 ± 0.2 (a review's summary across studies; its estimator per
  study NOT READ): **a hit** on both estimators. The gate (item 6): **#96 permanent.**
- **#103, the remnant count.** `remnant_count_total` **1 529.63** (the entry's 1 464 is S36's: corrected); drawn
  1 549 (Sedov 652, radiative 897); `REMNANT_VISIBLE_LIFETIME` 60 000 yr; `ngc_4414` 626.7. Against Ball et al. 2023's
  predicted 1 000-2 700: a hit against **a prediction**. The Sedov jump: `bubbles.py:349` `4.0 * n0`, every Sedov
  shell exactly four times its ambient - Leahy & Williams 2017's ratio; the comment re-tagged by the integrator
  (e7be575). The gate (item 6): the Sedov clause CLOSED; carried on the shell's ionization state, NOT READ.
- **The clusters' offset declaration** (D272 (e); not a register entry): measured with `test_layer`'s own
  construction, layer on: 13 124 clusters, **1 678 in another radial ring** (12.8 %; the mass share 35.5 %), 138 in
  another cell ring, the largest radial move 140.38 pc, the largest offset 148.36 pc. `layer/cloud_texture.py`'s text
  mended from S70's "1 591 of 12 710 (12.5 %, 34.3 %) ... 132" to these numbers (it moves the hash, no number in the
  model).

### Not read, S104

- #86: Fryer et al. 2012 (not fetched); why the fit has a seam at Z = 5e-4 (the paper's text on its two branches not
  searched); the gravitational-wave black holes' masses (named by the gate as a check, not read).
- #83: Lamers & Leitherer 1993 still NOT READ; the recipe's stated range in Γ_e; the Thomson form RECALL.
- #135: the isochrones' K photometry against an independent source; the AGB's share in Just et al.
- #136: Driver et al. 2007 and Tuffs et al. 2004 not re-fetched (S101's R3 read used).
- #162: Turner et al.'s upper age above 10 Myr; their fit ranges in pc. #96: Krumholz et al.'s estimator per study.
