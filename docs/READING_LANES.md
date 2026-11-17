# READING_LANES — a spiral arm's dust lane: its width, offset, continuity and contrast, and the shock theory (S103, D273)

**What this file is (2026-11-17, S103, BUILD_VII row 105, the reading row).** The frames have no dust lanes
(`READING_PICTURES.md` sections 13, 19, 20, 25); #234's measured relation, built held in batch Q, gathers the gas into
a crest of order a kiloparsec, and the goal pictures' lanes are of order a hundred parsecs (#234's S102 paragraph,
#229's S102 line). S103's reader RL (an Opus agent, read-only; its note `s103_RL.md` in the session's scratchpad) read
what is measured of a lane and what the theory gives. What the gate took from it is item 1 of `DECISIONS.md` D273 and
register #229 and #234.

**Tags.** READ (this session) — the page fetched at S103 and the sentence or row quoted (a summarising fetch, asked
each time for exact sentences; long sentences came back as fragments, said where); READ (repo, Sxx) — read by an
earlier session's reader and recorded with its quote in the named docs file, not re-fetched at S103; RECALL — memory,
not usable for a law; NOT READ — the fetch failed or was not attempted; `[inferred]` — the reader's own arithmetic or
connection of a paper to the model. Nothing here moved a constant, a pin or a model byte.

---

## Part S103 — the reading (reader RL)

### S103.0 The answer in five lines

1. **Width.** Measured optical dust lanes are 20-81 pc (M51's inner arms, HST V; Schinnerer et al. 2010) and about
   150 pc (five S4G grand designs, at the resolution limit; Elmegreen et al. 2014). NGC 628's dust-filament network is
   detected from a 25 pc floor up (Thilker et al. 2023) — a method's scale, not a measured width. The CO arm is wider:
   M51's inner gas arm FWHM 0.17 of the arm spacing, half the stellar arm's (Egusa et al. 2017).
2. **Offset.** In M51 the CO ridge lies on the concave (inner, upstream) side of the 15 micron arm by about 100 pc, up
   to 600 pc, inside corotation, with no change of side across it (Patrikeev et al. 2006) — warm dust, not the old
   stars' crest. Against the stellar-mass arm one M51 arm moves from about −45 deg to 0 with radius, the other has no
   trend (Egusa 2017). Across 24 PHANGS galaxies only 4 show a single-density-wave trend (Querejeta et al. 2025). **No
   measured offset of the lane from the OLD stellar crest in pc, over a sample, was found.**
3. **Continuity and contrast.** No covering fraction of lanes along arms is printed anywhere read. Proxies: M51's gas
   arm "fairly smooth" with brightness variations of a factor 2-3 (Schinnerer et al. 2017); in NGC 628 filaments take
   50-55 % of sight lines at 25-100 pc and are clearer in arms (Thilker 2023). Halving the PHANGS arm mask's area raises
   the molecular contrast only from 2.22 to 2.53 (Querejeta et al. 2024 Table 1). Darkness against the adjacent arm:
   V transmission about 0.44-0.58 (M51, Rix & Rieke 1993, repo S98).
4. **Theory.** A steady galactic shock exists only with a pattern speed (flow through the arm). It has no closed form:
   a 1-D ODE per ring with a sonic point and a jump (Kim, Kim & Kim 2014 = KKK14; Gittins & Clarke 2004; repo S57),
   tabulated for one parameter set. Its time-averaged multiphase version is broad: TIGRESS arms (feedback, F = 0.2)
   match an isothermal shock with c_s = 20 km/s and fill about 0.9 kpc of a π kpc spacing (Kim, Kim & Ostriker 2020).
   The co-rotating (dynamic) arm the model uses (D216) has no shock profile in any source read.
5. So the lane's **width and darkness** are measured well enough for disclosed checks (few galaxies); its **offset and
   continuity** are not measured as laws; **no closed form** gives a 20-150 pc lane from forcing, sound speed and pitch.

### S103.1 Width (FWHM or stated width)

| source | id | what is measured | number | coverage | label |
|---|---|---|---|---|---|
| Schinnerer, Weiss, Aalto & Scoville 2010 | arXiv:1007.0692 | HST V dust lanes, M51 inner arms | "range from about 0.5'' to 2''" = 20-81 pc `[inferred at 40.7 pc/arcsec]`; extinction "across the full width of the gas spiral arms of ~ 7''" (~285 pc) | HST, M51 only | READ (repo, S98; `READING_GAS_SHOCK.md` S98.4) |
| Elmegreen et al. 2014 | arXiv:1310.7146 | S4G dust lanes (opacity vs 3.6 µm) | "A typical dust lane width is ~4 pixels ... W ~ 150 pc at a distance of 10 Mpc"; "W/piR ~ 1%" at R = 4 kpc | 1.7 arcsec, at the resolution limit; NGC 4321, 5055, 5194, 5248, 5457 | READ (repo, S51; `READING_GAS_PATTERN.md` sect. 9) |
| Thilker et al. 2023 | arXiv:2301.00881 | dust-filament network of NGC 628 (MIRI emission + HST B attenuation) | "at multiple scales between 25-400 pc"; "With our highest resolution DFN maps (25 pc filament width)"; Sect. III.1: "The minimum scale of 25 pc corresponds to approximately twice the PSF FWHM of MIRI F770W" | one galaxy; 25 pc is the extraction floor | READ (this session) |
| Meidt et al. 2023 | arXiv:2212.06434 | ISM filaments, four PHANGS-JWST galaxies | Sect. III.1.1: "Extracted features are selected to have widths not below 50 pc (roughly 3 resolution elements at the distance of NGC 628)"; no width distribution printed (asked) | a selection floor | READ (this session) |
| Schinnerer et al. 2017 (PAWS) | arXiv:1701.02184 | an M51 arm segment with nine spurs | Sect. III.1.1: "The (deprojected) spurs have typical widths of 1-2'' (40-80 pc) in their thin structures"; no numeric width for the arm itself (asked) | one arm segment | READ (this session; characters 0-100 000 of 127 636) |
| Egusa et al. 2017 | arXiv:1610.06642 | M51 gas (HI+CO) and stellar-mass arms, azimuthal FWHM | gas "~30 degree (FWHM) for inner arms and ~5 degree for outer arms"; stars "~60 degree ... ~30 degree" -> gas FWHM / spacing 0.17 inner `[inferred, m = 2]` | 6 arcsec (~240 pc); one galaxy | READ (repo, S51/S57) |
| Querejeta et al. 2024 | arXiv:2405.05364 | PHANGS narrow arm masks | App. E: "typical widths between 500 and 1000 pc"; Sect. 2.6.1: "Locally, the distribution of molecular gas or star formation in the arms often looks thinner, but the presence of kinks and irregularities requires this width in order to warrant full coverage along the entire arm" | 28 galaxies; top-hat mask widths | READ (repo S51 for App. E; this session for 2.6.1) |
| Reid et al. 2014 / 2019 | arXiv:1401.5377, 1910.03357 | Milky Way arms, masers' scatter about the arm | 0.17-0.63 kpc (Table 2); w(R) = 336 + 36 (R − 8.15) pc (1σ) | star-forming regions, not dust | READ (repo, S57) |
| Patrikeev et al. 2006 | astro-ph/0609787 | M51 wavelet arms | Sect. 4.1: "the approximate width of the spiral arms of 1 kpc" (the noise cut, not a measurement) | — | READ (this session) |

Width in theory (rigid pattern, Ω_p = Ω/2, R0 = 10 kpc): Kim & Ostriker 2002 (KO02) Table 1 W/L_x 0.05-0.16 = 155-500
pc at L_x 3.1 kpc (READ, repo S98.1). KKK14's sonic-point-to-shock distance 0.056-0.139 L for F = 3-20 % (repo C1.3,
`[inferred]` there from the READ table). Dobbs & Baba 2014 report Shu et al. 1972's two-phase shock "a width of the
shocked region of 50 pc" (secondary, repo S98.3).

### S103.2 Offset of the gas or dust ridge from the stellar arm

| source | id | quantity | number / sentence | coverage | label |
|---|---|---|---|---|---|
| Patrikeev et al. 2006 | astro-ph/0609787 | CO ridge vs ISO 15 µm ridge, M51 | Sect. 4.2: "the CO spiral arms are consistently situated on the concave side of the ISO 15um arms"; "The shift between the two ridges is typically ~100 pc, increasing to around 600 pc in the northern part of arm 2"; Sect. 5: "The typical offset is 100 pc corresponding to a typical time delay of ~10^7 yr for gas well inside the co-rotation radius"; "We do not see a shift in the relative positions of the ISO and CO arms, i.e. the CO arm does not move from the concave to the convex side of the ISO arm" | M51; 15 µm is warm dust + PAH, NOT the old stars | READ (this session) |
| Egusa et al. 2017 | arXiv:1610.06642 | az(gas) − az(stellar mass) | inner arm 2 from about −45 deg to ~0 with radius (a shock with R_CR = 168 arcsec); inner arm 1 no trend; outer arms scatter about zero | M51, two arms, 240 pc | READ (repo S57, B5) |
| Schinnerer et al. 2013 (PAWS I) | arXiv:1304.1801 | CO vs dust lanes, M51 | CO "very well follows these dust lanes" (Sect. 4.3.3) | 40 pc | READ (repo S51) |
| Vallée 2019 (compilation) | arXiv:1911.06798 | dust lane to the star-forming tracer | "24 of them have a positive offset"; "we find offsets with a median value near 326 pc and a mean near 370 pc" | 40 galaxies, mixed tracers and resolutions | READ (this session, abstract only) |
| Querejeta et al. 2025 | arXiv:2509.01668 | CO -> Hα | mean 230 pc, median 220 pc, range −400 to +740 pc; 4/24 with a declining trend, 10/24 positive without trend, 10/24 not positive | 24 PHANGS galaxies, ~100 pc | READ (repo S57 B6) |
| Tamburro 2008; Foyle 2011; Egusa 2009; Louie 2013 | 0810.2391; 1105.5141; 0904.3121; 1301.2601 | HI/CO vs 24 µm / Hα | Tamburro "a few degrees", positive inside CR; Foyle "no systematic angular offsets", < 5 deg; Egusa 2009 clear in 5 of 13 | 12-14 galaxies | READ (repo S57 B1-B4) |
| Baba, Morokuma-Matsui & Egusa 2015 | arXiv:1505.02881 | simulations | dynamic spirals: "no systematic radial dependence of the arm-gas offsets"; steady: a radial trend | sims | READ (repo S96/S57 B19) |
| Dobbs & Baba 2014 sect. 3.7 | arXiv:1407.5062 | dynamic arms | "gas effectively falls in to the minimum of the potential, from both sides of the spiral arm"; "a systematic offset is not expected" | review | READ (repo S98.3) |
| Kim, Kim & Ostriker 2020 (TIGRESS) | arXiv:2006.05614 | rigid pattern with feedback | Sect. III.1: "the high-density ridge slightly to the right (downstream) from the potential minimum"; "the density peak located at x~0.3-0.5 kpc" (fragment) | one local model, R0 = 8 kpc | READ (this session) |
| Chandar et al. 2017 (M51 clusters) | — | clusters vs gas | only as cited by others | — | NOT READ (not used) |

Sign in theory: inside corotation a steady shock sits upstream of (on the concave side of) the potential minimum —
Dobbs & Baba quote Roberts 1969, "for warm gas and moderate forcing, a narrow shock is expected ahead of the minimum of
the potential" (repo S98.3); KKK14's x_sh/L 0.40-0.56 against the minimum at 0.5 (repo C1.3, READ); KO02 at x/L_x
~ −0.02 to −0.05 (repo B20). Gittins & Clarke 2004: near corotation ("base-subsonic") "a broad density peak at eta =
0", the shock weak or absent (repo C1.3/C1.4, READ). With feedback the dense ridge sits downstream (TIGRESS).

### S103.3 Continuity and contrast

| source | quantity | number / sentence | label |
|---|---|---|---|
| Schinnerer et al. 2017, Sect. V.2 | brightness along the gas arm | "the gas spiral arm appears fairly smooth (with variations within a factor of 2-3 in brightness)" | READ (this session) |
| Schinnerer et al. 2017, Sects. III.1.1-2 | arm vs spur | arm-to-spur gas surface density "compared to two times for the gas surface density" (fragment); peak T_CO "generally about 20-25% higher in the spiral arm"; spur bases 4-11 arcsec apart, "The average spacing is ~7.5''" (~300 pc `[inferred]`) | READ (this session; fragments) |
| Thilker et al. 2023, Sect. IV.1 | sight lines in filaments, NGC 628 | "approximately 50-55% of sight lines are attributed to dust filaments for scales 25-100 pc"; emission filaments "can be seen in spiral arms (markedly less so in interarm regions)"; the attenuation mask "recovers continuous spiral structure more effectively than the F770W emission mask"; emission and attenuation "co-spatial in 40% of sight lines"; no A_V or τ of filaments printed (Sect. V: future work) | READ (this session) |
| Meidt et al. 2023, Sect. IV | filament spacing | "the filament spacings fall very near the Jeans length"; "filaments tend to modestly increase in separation moving outwards"; no contrast printed (asked) | READ (this session) |
| Querejeta et al. 2024, Table 1 | arm / inter-arm Σ_mol, nominal vs narrow mask (~50 % of the area) | Σ_mol 2.22 (−0.96/+2.19) nominal vs 2.53 (−1.02/+2.83) narrow; Σ_star 1.28 vs 1.28; no CO flux fraction in the narrow mask printed (asked) | READ (this session; cell by cell not re-checked) |
| Querejeta et al. 2021, Table 2 | area of the arm masks | spiral 10.7 %, inter-arm 33.0 % | READ (repo S51) |
| Rix & Rieke 1993, Table 1 | lane centre vs surrounding arm, M51 | V − K 0.79 / 0.58 mag -> V transmission about 0.44-0.58 `[inferred, repo]`; τ_V 3.5-9 in lanes | READ (repo S98.4) |
| Keel & White 2001, Sect. V | non-backlit lanes, NGC 3314A, I | "non-backlit dust lanes have no values below 0.75" of a 5 arcsec running median | READ (repo S98.4) |
| Schinnerer et al. 2010 | column through M51's lanes | "AV~12-18" from CO (the full column, not the dimming seen) | READ (repo S98.4) |
| Kim, Kim & Kim 2014, abstract | the shock's continuity | spiral shocks are "unstable to wiggle instability (WI)"; at 5 % forcing "the wavelength of the most unstable mode is about 0.07 times the arm-to-arm spacing"; "The wavelength and growth time of the WI depend on the arm strength quite sensitively" | READ (this session, arXiv:1405.5874 abstract) |

**Grand design against flocculent.** NGC 4414 is flocculent (Elmegreen class 3, Buta class F; `READING_NGC_4414.md`
row 16). Elmegreen, Elmegreen & Leitner 2003 (astro-ph/0305049, READ this session): Table 1 lists NGC 4414 as F, 9.7
Mpc, 4.7 pc pixels; optical structure power spectra "approximately flat between 20 pc and 100 pc"; "The typical
length scale in the flat part of our power spectra is 100 pc"; "dust and bright stars dominate the high spatial
frequencies". It says nothing on whether flocculent dust is lanes or a network (asked). Thornley & Mundy 1997 (ApJ
490, 682): NOT READ (ADS returned HTTP 405). `[inferred]` For NGC 4414 the literature read supports a dust network with
a ~100 pc scale, not continuous lanes; no measured statement of it as a network was read.

### S103.4 Theory: what a model could evaluate per ring

- **Equations.** The steady isothermal spiral shock in a rigid pattern: one 1-D ODE per ring across the arm, a
  regularity condition at the sonic point and the isothermal jump u₊ u₋ = c_s² (KKK14 eqs. 8-22; Gittins & Clarke 2004
  App. A). All READ in repo (`READING_GAS_SHOCK.md` C1.1-C1.2, S57). Inputs: F, c_s/(RΩ), sin i, Ω_p/Ω, κ/Ω, m.
- **Closed form: none.** KKK14's abstract (READ this session) has no fitted formula for the jump, width or place
  against F, c_s or pitch (asked). Tabulations at one parameter set only: KKK14 Table 1 (q = 1, m = 2, sin i = 0.1,
  Ω_p/Ω = 0.5, c_s/(RΩ) = 0.027): F = 0.03, 0.05, 0.10, 0.20 -> μ = Σ₊/Σ₋ = 5.67, 11.6, 34.5, 97.3; x_sh/L 0.402, 0.431,
  0.495, 0.560 (READ repo C1.3). KO02 Table 1: F 1-3 % -> Σ_max/Σ_0 2.1-6.5, W/L_x 0.05-0.16 (READ repo S98.1).
- **Threshold.** KKK14 report SMR73's "even a very weak spiral forcing (F > 0.9%) for their model parameters results in
  shocks" (secondary within a READ page); Dobbs & Baba: "For c_s = 8 km/s, the forcing required to produce a shock is
  around a few %"; Sormani et al. 2017 an exact Φ_c = 0.07297 for one dimensionless set (READ repo C1.2). At small F
  "the solutions reach the first-order response, which is sinusoidal" (Gittins & Clarke, READ repo) — the regime of the
  model's linear solve.
- **Round corotation, or with no flow through the arm (the model's D216 frame):** no shock; "a broad density peak at
  eta = 0" (GC04) or gas falling in from both sides (Dobbs & Baba); no profile, contrast or width printed in any source
  read (repo S98.2-S98.3).
- **A realistic ISM.** Kim, Kim & Ostriker 2020 (TIGRESS, arXiv:2006.05614, READ this session): sin i = 0.125, m = 2,
  Ω_p = Ω₀/2, L_x = π kpc, R0 = 8 kpc, F = 0.2 in model F20B10. "In terms of the peak density and its location, the
  spiral-arm profiles in model F20B10 are similar" "to those in the isothermal counterpart with cs=20 km s-1" (two
  fragments); the shocks' oscillations "smear out the averaged profiles considerably"; "In model F20B10, the arm region
  is at -0.1 kpc<x<0.8 kpc, varying slightly with time"; the shock fronts "consist of numerous small-scale curved
  shocks"; "making the density profile broader than the isothermal counterpart". No arm / inter-arm surface-density
  number printed. `[inferred]` The time-averaged arm is ~0.9/π = 0.29 of the spacing even at F = 0.2: a realistic
  galactic shock does not make a 20-150 pc lane in the mean; the narrow dark features are instantaneous small-scale
  shocks and clouds.

### S103.5 What a model could carry

**Measured well enough for a disclosed check (never a target, C6):**
- The lane's width, a bracket: 20-81 pc (M51, one galaxy) to ~150 pc (five S4G grand designs at their resolution
  limit); filament floors 25-50 pc in NGC 628 and three more PHANGS-JWST galaxies. About seven galaxies, all grand
  design or multi-arm. Not a law: no width against radius, forcing or type is fitted anywhere read.
- The lane's darkness against its own arm: V transmission 0.44-0.58 (M51), I ≥ 0.75 (NGC 3314A). Two galaxies.
- The gas ridge's width against the stellar arm: 0.5 (M51 inner, one galaxy); the narrow PHANGS masks 500-1000 pc.
- The molecular contrast's weak dependence on the mask's width: 2.22 -> 2.53 for half the area (28 galaxies, ~100 pc)
  — the kiloparsec arm is not dominated by a thin ridge at 100 pc resolution `[inferred]`.

**Not measured well enough:**
- The lane's offset from the old stellar crest in pc, over a sample. The dynamic-arm reading (the model's frame)
  predicts no systematic offset; most galaxies' measurements are consistent with that.
- Continuity: no covering fraction along arms printed anywhere read (proxies only).
- The share of an arm's molecular gas in the narrow ridge: not printed (Querejeta 2024 asked: area only).
- Flocculent dust (NGC 4414): no lane or network statistic; only a ~100 pc structure scale.
- A closed form for a lane: the steady shock is a per-ring ODE needing a pattern speed, tabulated at one parameter
  set, and its realistic time average is broad (~0.3 of the spacing).

**Candidate rulesets (the reader's; candidates only):**

- **R1 — a thin lane laid on the existing gas crest, D216 kept** `[inferred throughout]`. Per ring, on each crest of the
  placed molecular field, a narrow Gaussian in the dust column centred on the crest (offset 0: Dobbs & Baba 3.7 and
  Baba et al. 2015 for dynamic arms), following the crest's pitch. Uses the placed field's crests and pitch, f_mol, the
  dust-to-gas ratio and the layer's height (Schinnerer 2010's "can not have a larger vertical extent than a dust lane is
  wide"; Rix & Rieke's 0.25-0.6 of the stars' height). New constants: (1) the lane's FWHM, a bracket 20-150 pc — a
  disclosed choice inside a measured bracket, not a fitted law, the same kind of placeholder #147 regrets; (2) the share
  of the crest's gas moved into the lane — **no source**, at best bounded small by Querejeta 2024's 2.22 -> 2.53.
  Continuity: continuous along every crest (not measured), or broken at the spur spacing (~300 pc in M51) or the
  Jeans-length filament spacing — each a further choice. Weakness: constant (2) has no source; the lane would be
  drawn, not derived.
- **R2 — the steady shock per ring where an arm has a pattern speed (D216 re-opened).** KKK14/GC04's ODE per ring with a
  sourced Ω_p (the Milky Way's: Gerhard 2011 25 ± 2, Dias 2019 28.2, Castro-Ginard 2021 per arm; repo B1). Inputs: the
  stellar forcing from the pieces, κ, Ω, the pitch, the gas dispersion as c_s. The crux is the effective c_s: at 7 km/s
  the shocked arm is 155-500 pc (KO02); with the multiphase average it behaves as c_s = 20 km/s and fills ~0.3 of the
  spacing (TIGRESS) — even R2 gives a ridge of hundreds of parsecs in the mean, and a 20-80 pc lane would still need
  R1's thin component or the clouds (#231). NGC 4414 (flocculent, no pattern speed) cannot take R2: two laws in one
  model. Checks: KKK14 Table 1 and Sormani et al. 2017's threshold.

**The gate's ruling (D273 item 1).** A lane cannot enter the model by D1: its share of the gas, its offset from the
stellar crest and its continuity have no source. The owner's question, put as (i) **no lane** — the model keeps what
is measured (the kiloparsec contrast, the clouds), the frames keep dark flecks, and the goal pictures' lanes are
declared outside what the model holds; or (ii) **a disclosed lane** — R1, width a declared bracket 20-150 pc, share a
declared number with no source, zero offset: a picture-driven term, which C6 and D1 forbid a session to take and only
the owner can order. The gate recommends (i), and says what it costs: the lanes are the largest thing a viewer
misses. R2 is recorded and not recommended: it reopens D216, needs a pattern speed NGC 4414 does not have, and still
gives hundreds of parsecs.

### S103.6 Not read

- Roberts 1969, Shu, Milione & Roberts 1973, Elmegreen 1980, Lynds 1970: not on arXiv; secondary quotes only (repo).
- Thornley & Mundy 1997 (NGC 4414): ADS HTTP 405. NOT READ.
- Chandar et al. 2017 (M51 cluster offsets): secondary only. NOT READ.
- Williams et al. 2022: not identified. Schinnerer et al. 2013 beyond the repo's quotes; Kreckel et al. 2018
  (arXiv:1807.11506) found by search, not fetched: NOT READ.
- Querejeta et al. 2024's Table 4 fit form: still not stated in the HTML's first 100 000 characters (asked again).
- Kim & Ostriker 2006, Wada 2008, Shetty & Ostriker 2006, Kim, Kim & Ostriker 2008/2010: not attempted.
- TIGRESS (2006.05614) characters 100 000-187 827 read only for Sect. V and the summary; Fig. 11's profile values not
  read.
