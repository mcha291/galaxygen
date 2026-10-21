# AUDIT_V — Session 69: the third build's audit (S53–S68: BUILD_III's phases 0, T, R, P1–P5, L1–L2, V5–V9) — gate G4

Once, after the build, as the project does (S10's two runs, S21's aim (a), S37's Audit III, S43's Audit IV);
commissioned by BUILD_III §5 ("Audit V (S69) — gate G4") on the owner's adoption of 2026-10-03 (D212) and placed
at S69 by D222. **Nothing here changes a number in the model or the viewer** (B3): a finding that would is a debt
or a ruling for the owner, with the sentence that decides it. The findings, the method and the counts are the
audit's decision; the fixes are the next session's.

## 0. The aim, stated before any audited file was opened (D113), and how it is to read

Drafted at S68 by the Fable lead from BUILD_III's text (§1d, §5 "Audit V", §0 "what will remain"), the readings'
citation counts and the layer tests' names alone, while S68's builder worked; committed on `session-69` as its
first commit, before any file this audit judges was opened in that session. Where it names a file range it names
it from `RESUMING.md`'s layout, not from a reading.

**The five strands BUILD_III names, each one question, each with its own reader:**

1. **Every citation entered since S51 re-read against the sentence it cites.** The readings
   `docs/READING_GAS_PATTERN.md` (S51; 116 tags), `READING_ARM_MODES` (S56; 34), `READING_GAS_SHOCK` (S57; 58),
   `READING_BAR` (S58; 79), `READING_ARM_SEGMENTS` (S59; 3), `READING_ARM_PIECES` (S60; 92), `READING_CLUSTERING`
   (S61; no tags — every number there is to be labelled), `READING_GAS_SPECTRA` and `READING_SPURS` (S62; 24, 29),
   `READING_NGC_4414` (S54; 27), `READING_HST_OPTICS`, `READING_CLOUD_LAYER`, `READING_CLOUD_SIZES` (S67; 0, 1, 2),
   and every constant, pin and table that entered `model/galaxy/models/level0.py`, `models/stages/`, `layer/` and
   `templates.py` between tag `s50` and the S68 merge (`git diff s50..main`), each labelled **MATCH / DIFFERS /
   ADOPTED-NOT-MEASURED / MISATTRIBUTED / UNREACHABLE** as Audit III's and IV's re-readers did (D186, D194): a
   number is checked only on a fetched page; equation numbers counted from the source; nothing from recall (a
   recalled value is `[recall — NOT READ]` and out of the table); each citation's stated coverage fraction checked
   against what the source measures. A DIFFERS is a finding; an adopted or inferred value presented as measured is
   A-14's class; a display choice is labelled and not judged. The readers are **blind to the builders' reports**:
   they receive file ranges, the readings and the sources, never `DECISIONS.md`'s build paragraphs.
2. **Every synthetic field's conservation and statistic re-measured**, in `tests/test_audit_v.py` (the one test
   file the audit adds), at a mesh the build did not use and on a `texture_seed` the build did not pin: the five
   layer stages — `cloud_texture` (the four cloud columns + three scalars; neutral layer-off), `arm_pieces` (the
   `arm_piece` table; the ring mean's exactness, the power budget), `census_clustering` (the `cell` table and the
   three-octave map; σ 1.75 and the statistic (r/190 pc)^−0.64 re-fitted by the audit's own estimator, not the
   build's Landy–Szalay code), `gas_fluctuation` (the field's periodogram against the declared broken law; the
   per-ring break, Mach, σ, strain, twist, normaliser), `gas_spurs` (the `gas_spur` table; feathers at ten Jeans
   lengths off chains only). For each: what it declares it conserves (`FieldDecl.conserves`) measured on and off;
   what it says it stands in for (`stands_in_for`) read against the physics it names; the statistic
   (`statistic`) re-derived from the realisation. A declared conservation that holds only in expectation, or a
   statistic the realisation does not reproduce within its own noise, is a finding.
3. **I1–I5 re-derived, not re-run.** For each invariant of BUILD_III §1d, the reader states what the tests in
   `tests/test_layer.py` (the `test_i1_*` … `test_i5_*` families) *actually assert* — the named exceptions
   (`RING_FIRST_STATISTICS`, the four-ulp allowance, the "but the named list" clause), the meshes, the seeds, the
   templates — beside what §1d promises, and whether a layer-on change the invariant forbids could pass the test
   as written. Where the test asserts less than the text, a finding with the gap in one sentence; where the text
   was amended at a gate (G1, G2, S58), the amendment's wording checked against the test that cites it.
4. **A picture traced feature by feature to a published field or a layer field.** For each of the seven committed
   frames (`frontend/e2e/frames/`): every feature a viewer sees — the arms and their pieces, the bar's body and
   lanes, the dust web and its spurs, the clouds, the HII knots, the young light's speckle, the bulge and its PSF,
   the bright points — traced to the array or header entry the viewer read (`/api/render`'s header, the census
   routes, the `v6_*`/`v7_*` modules) and to the model field or layer field behind it, with the display choice that
   scaled it named (`TEMPLATE_TUNING`, the sliders' defaults). Anything the viewer draws that no published
   quantity stands behind (D5 as amended, D189, D212) is a finding; a display choice is labelled. The trace is a
   table: feature → array → field → provenance (derived | seeded | synthetic | display).
5. **The register pass and the pictures' residue.** Every open item (#3 … #185 at S67; S68's additions) re-stated
   in one line with its verdict re-ruled against the repository as it stands — discharged by a later session that
   did not say so, permanent, carried with its closer named — and the counts (open = permanent + carried;
   discharged) re-derived against `tools/progress.py`. Then the goal metrics' final table (D227) set against §0's
   "what will remain" and against D212's baseline, one plain sentence per picture saying what a viewer sees
   beside the goal and what BUILD_III promised would remain — never a target, never a tuning (C6, D113).

**Method (Audit III's and IV's shape, D186, D194).** Read-only Opus reader agents, one strand or one slice each,
run two at a time at most (the rationing rule: one heavy, none started past 50 % of the 5-hour window, none while a
weekly window is past 80 %); each writes one Markdown note in the scratchpad with a summary table, per-source
notes, what could not be read and the labels; the lead assembles them into this file's §1–§5 and writes the
findings list numbered F1 …, each with its class (DIFFERS, gap, invention, mis-ruled debt, display), the file and
line, and the sentence that would settle it. **Then G4**: Fable's verdict on each finding — upheld, dismissed with
the reason, or a ruling for the owner — in at most 80 lines, transcribed to the decision; the fixes ordered by
class into the next session's BRIEF. B3 holds throughout: the audit checks, the next session fixes, no model
number moves, no frame is regenerated.

**What this audit does not do.** It does not re-run the build's gates (they ran); it does not re-fit `ngc_4414`
(D215: fit B stands, no third fit without the owner); it does not open `basic` (frozen, ruling 7); it does not
read the owner's goal pictures except through `tools/goal_metrics.py`'s numbers already in D227; it does not touch
the deployment (BUILD_IV). A reader that meets a stop condition of BUILD_III §3d (a source contradicting what the
plan assumed) writes it as a finding and continues.

## 1. The citations since S51, re-read (strands 1A and 1B; two Opus readers, about 175 fetches; nothing from recall)

The readers' notes (every tag with its label, the per-source notes, the constants-to-reading trace) are the audit's
working papers in the lead's scratchpad; this section keeps the counts and the findings. Where an arXiv PDF would not
parse, the reader ran `pdftotext` on the tool's saved copy; VizieR rows were read as raw TSV; a reader's arithmetic
(a median of a table, a ratio) was re-run under `uv run` and matched.

| reading | tags counted | MATCH | DIFFERS | ADOPTED | MISATTRIBUTED | UNREACHABLE |
|---|---|---|---|---|---|---|
| GAS_PATTERN (S51) | 119 | 89 | 0 | 0 | 0 | 30 |
| ARM_MODES (S56) | 37 | 28 | 1 | 0 | 0 | 8 |
| GAS_SHOCK (S57) | 69 | 30 | 1 | 1 | 0 | 37 |
| BAR (S58) | 78 source keys | 25 | 3 | 0 | 1 | 49 |
| ARM_PIECES (S60) | 157 | 49 | 1 | 0 | 0 | 107 |
| ARM_SEGMENTS (S59) | 27 source keys | 10 | 1 | 0 | 0 | 16 |
| CLUSTERING (S61; its own `[V:]` labels) | 85 | 8 | 0 | 0 | 0 | 77 |
| GAS_SPECTRA (S62) | 23 | 6 | 0 | 0 | 0 | 17 |
| SPURS (S62) | 28 | 17 | 0 | 0 | 0 | 11 |
| NGC_4414 (S54) | 27 source keys | 10 | 0 | 0 | 0 | 17 |
| HST_OPTICS (S67; "read" items) | 12 | 5 | 0 | 0 | 0 | 7 |
| CLOUD_LAYER, CLOUD_SIZES (S67) | 3 | 2 | 1 | 0 | 0 | 0 |
| **total** | **665** | **279** | **8** | **1** | **1** | **376** |
| level0 constants and pins traced to code | 18 + 43 + 23 | 59 | 3 | 10 (6 declared adopted or inferred) | 4 | 0 |

The UNREACHABLE column is mostly budget: context-only sources the readers did not fetch (about 55 in 1A, nearly all of
1B's 252), listed by name in the notes. **Every tag that feeds a constant, a pin or a fit target in code was reached**
except one ADS scan (Shu, Milione & Roberts 1973, whose restatements in Kim, Kim & Kim 2014 Table 1 and Sormani 2017
MATCH) and the five items of F-1B-7. **No constant's number differs from its source.** Reid 2019's Table 2 (seven rows,
every digit, R₀ 8.15), the NGC 4414 pins (the five Herrera-Endoqui segments; Díaz-García 2019's 28.88° ± 5.97°, sd
13.35°; Buta 2015's class F; Thornley's "most flocculent"; Vallejo's and Wong's "no bar"), the Milky Way's 30° bar
angle inside Wegg 2015's and Bland-Hawthorn & Gerhard 2016's 28–33°, the fit targets (P16 237 ± 10 km/s, S4G 19.22″,
z0MGS 10.65 ± 0.10), the HST numbers (0.04″/px, 2.4 m, f/24, the TinyTim pupil 0.330 / 0.022 and the three pads), Fujii
2018's 0.146 and 1.38, Gadotti's ε ≈ 0.6 and c = 3, Kruk's 0.31 ± 0.12, Kim, Seo & Kim's eq. 11, Querejeta 2024's 2.73
and 1.90, Sellwood & Masters' 1/f_d ≲ m ≲ 2/f_d, Block 2004's 20° — all MATCH the fetched page.

**Findings (class in capitals; the sentence that settles each is in the note).**
- **F-1A-1** `level0.py:362-371` `BAR_GAS_RATIO` 2.6 — ADOPTED-NOT-MEASURED: defined and used as a ratio of means, but 2.56 is Querejeta 2021 Table 3's ratio of *medians* (11.51 / 4.492); the means give 3.17. Redefine as medians or enter 3.17.
- **F-1A-2** `level0.py:282, 299` (Fujii T₀ and S), `READING_BAR.md:105` — MISATTRIBUTED (equation number): the fit is unnumbered, §3.3 and the Fig. 9 caption; eq. (11) defines f_d.
- **F-1A-3** `level0.py:320` `BAR_BOXINESS` — MISATTRIBUTED in part: "always above 2" is Kim et al. 2015, not Gadotti 2011 ("peaks at c = 3").
- **F-1A-4** `level0.py:328-331` `BAR_PROFILE_INDEX` — MISATTRIBUTED (provenance): the Ferrers profile is called "the fitting function of the S4G decompositions the bar statistics come from", but the shape statistics are Gadotti's SDSS Sérsic-bar fits; Salo 2015 prints no bar statistics. The body mixes a shape from Sérsic fits with a profile from Ferrers fits.
- **F-1A-5** `stages/systems.py:124-126` `YOUNG_STAR_AGE` 0.1 Gyr, `READING_GAS_SHOCK.md:38` — ADOPTED-NOT-MEASURED tagged verified: Baba, Saitoh & Wada 2013 prints no "0.3–0.5 rotation periods" or "100–160 Myr"; only Grand 2012a's "about 120 Myr" is printed.
- **F-1A-6** `READING_GAS_SHOCK.md:36` — DIFFERS (context): Grand 2012a prints no Ω_p(R) values; "~10 at 8 kpc" contradicts its "almost equal to the rotation curve" (~26).
- **F-1A-7** `READING_BAR.md:318` — DIFFERS (context): Q_b runs 0.09–0.57, not 0.09–0.63.
- **F-1A-8** `READING_BAR.md:316, 411` — DIFFERS (context): Comerón 2009's runs are FTM with 10⁵ isothermal particles, not SPH; 238 is the number of simulations (88 with lanes), not "238 simulated bars".
- **F-1A-9** `level0.py:1032-1033` — wording: "17 of 27 PHANGS spirals" should read 17 grand designs of the 28 spirals.
- **F-1A-10** `READING_BAR.md:507-508` — DIFFERS (context): Salo 2010's Conclusions do say "r ∼ 1.5 R_bar".
- **F-1A-11** `READING_BAR.md:43` — DIFFERS: Kim et al. 2015 says Bar/T "can change up to 25 %", no direction; Kim et al. 2014 (the primary) not fetched.
- **F-1A-12** `READING_ARM_MODES.md:40` — DIFFERS (definition): Zaritsky & Rix 1997 average ⟨A₁⟩ between 1.5 and 2.5 scale lengths, not over R > 1.5 R_exp; the numbers MATCH.
- **F-1A-13** `READING_ARM_MODES.md:75` — MISATTRIBUTED (context): the linear rise is NGC 2841's (Kendall 2011 §3.1.4), not NGC 2403's.
- **F-1A-14** `READING_BAR.md` — a key collision: "DG16" is arXiv:1509.06743 in Part A and 1607.07317 in Part B (Part A's DG16b).
- **F-1B-1** `level0.py:1088-1091` `ARM_SEGMENT_PITCH_RELATIVE_SCATTER`, `layer/arm_pieces.py:504`, `READING_ARM_SEGMENTS.md:45, 151-154` — DIFFERS (coverage): 0.56 ± 0.25 covers Savchenko 2020's 67 stage-2 galaxies, not "155 galaxies" (§3.3, §4.2); the value stands.
- **F-1B-2** `level0.py:461, 474` `GMC_SURFACE_DENSITY_INNER/_OUTER`, `stages/clouds.py:23, 163-167` — DIFFERS (the regimes): the model uses 82 at every radius inside R_SUN and 35 outside; Lada & Dame 2020 give 82 ± 10 for the molecular ring (4–7 kpc) alone, "likely an upper limit", and 35 as the Galaxy-wide value elsewhere — inside 4 kpc and between the ring and the Sun included. `ngc_4414` inherits the Milky Way's R_SUN as its boundary and nothing says so.
- **F-1B-3** `level0.py:874-880` `CENSUS_CLUSTERING_WIDTH` (and `_SPECTRAL_SLOPE` 857-861) — ADOPTED-NOT-MEASURED presented as verified: 2.43 at 47.5 pc needs Grasha's two branches to meet at Menon's 190 pc; they meet at 112 pc (Grasha 2017a Table 4, age ≤ 40 Myr, classes 1–3), which gives 1.73. `layer/census_clustering.py:435-438` discloses "the lead's choice"; the level0 note does not.
- **F-1B-4** `level0.py:1892`, `READING_SPURS.md:41` — place: Kim & Ostriker 2006 has no §6; the sentence is §5.1 item 1. The value matches.
- **F-1B-5** `level0.py:492, 495` `MOLECULAR_LAYER_FWHM`, READING_CLOUD_LAYER — place: Ferrière 2001 §II.B, not §II.A. The value matches.
- **F-1B-6** `READING_ARM_PIECES.md:299` — DIFFERS (context; no constant reads it): Honig & Reid's innermost HII segments lie at 1.09–2.63 kpc per galaxy, not "1.1–3.3".
- **F-1B-7** UNREACHABLE where an about-line names the number (named alternatives and disclosed checks only): Shetty & Ostriker 2006's "~5 λ_J" (`level0.py:1898`); Corder 2008's 155 / 420 / 475 pc (`:1919`); Bronfman 2000's 118 pc (`:493`); HyperLeda's kt 6.98 and bvtc 0.77 (`templates.py:914, 930`); whether Helfer 2003 has single-dish data for NGC 4414.
- **F-1B-8** minor wording, no value moves: (a) `level0.py:917` drops Elmegreen & Scalo's condition "if there are no velocity fluctuations"; (b) `layer/gas_fluctuation.py:435` tags the THINGS median −1.6 as verified where it is derived arithmetic (the page prints the 50 % range −1.9 to −1.5 and a mean −1.3); (c) `level0.py:839` "four more galaxies give only limits" — Menon's Table 3 has four lower, two upper, one none; (d) `GMC_RADIUS_MAX` takes Miville-Deschênes's (R_max R_min²)^{1/3} radius as a cap on the equal-area radius; (e) the gas fluctuation's Mach 8.9 is 1 % past Burkhart & Lazarian's simulated 0.4–8.8.
- Ten place-only slips (the value right, the section off) are listed in 1A's note §3 and are not counted.

## 2. The synthetic fields re-measured (strand 2) — *[pending the builder's report; `tests/test_audit_v.py`]*

## 3. I1–I5 re-derived, not re-run (strand 3; one Opus reader, read-only, `tests/test_layer.py` 70 tests collected)

| invariant / rule | the text promises | the tests assert | gap |
|---|---|---|---|
| I1 | layer off, every non-composed field bit-identical to layer on but an empty `CENSUS_STATISTICS`; composed fields at their neutral; ring-first statistics 1e-12; expected totals within four ulp | a walk over every declared field, both models, the production grid, `milky_way` at default seeds only; composed fields a closed set; synthetic NaN-off fields and the two layer tables set apart; **placed objects' columns skipped**; 14 ring-first statistics at 1e-12; expected totals at 2 ulp | F-3-1, 2, 3, 10, 11 |
| I2 | expected counts per ring identical to 1e-12; from L1 the realised totals identical | ring expectations from the stages' own functions — **the stars' from the test's own reconstruction**; realised totals: cloud count / mass, cluster count / mass, HII Hα, bubble volume, stars, planets, giants, sub-rings at levels 1 and 3; `ngc_4414` on expectations only, SMALL | F-3-1, 2, 4 |
| I3 | judged layer-off; no row reads a synthetic field | every judging entry point `layer=False`, `layer=True` refused; each row's field and abscissa neither composed nor synthetic; template checks layer-off; rows 35 / 37 pinned | F-3-5 |
| I4 | no physics stage requires a synthetic or composed field; censuses consume placement weights "only"; the binners a closed list "by `cluster_radius`" | graph refusal + `compose` refusal at run time; the sets of readers, layer stages, composing stages and binners pinned; the binners read `cluster_birth_radius` | F-3-6, 7, 8 |
| I5 | the viewer and the API carry a switch | the API half only (routes, absent == on, 400, header echo, separate cache entries, the layer-off contract, the render arrays classified); the guard that only `compose` reads the switch | F-3-9 |
| rule 1 | a `texture_seed` reroll moves placements and texture, nothing else | DEFAULT_MODEL, SMALL, two seeds: no law moves, expectations 1e-12, tables and objects move | F-3-1, 12 |
| rules 2–5 | conserving with "does not keep" and the number; a measured, cited statistic; stands-in-for; evaluable at a point, no stored grid | `conserves` non-empty; "does not keep" asserted for two fields; `statistic` non-empty or "none read" beside a debt; nothing for rule 5 | F-3-13, 14, 15 |

- **F-3-1** `tests/test_layer.py:584-594` (also 32-34, 877-882, 921-924, 2037-2041) — gap: **the I1 walk compares no column of a placed catalogue**, and I2 sums only count and mass (plus Hα, volume, age). A layer-on change to `cloud_velocity_dispersion`, `cloud_alpha` or a star's metallicity passes I1, I2, I4 and rule 1. G1's reason ("the objects do not correspond") stopped holding at L1. Settle: a per-object test, on/off and under a texture reroll, matching each census's objects by (drawn ring, index) and holding every column outside a declared placement set bit for bit.
- **F-3-2** `:260-264, 963-969` — gap: the walk and the realised totals run only at `milky_way`, default seeds; `ngc_4414` (unbarred, flocculent) only in expectations on SMALL; the saturation cut never fires. Settle: parametrise over a SMALL `ngc_4414` run and one non-default seed pair.
- **F-3-3** `BUILD_III.md:86-92` vs `:584-615` — gap: I1's text excepts only census statistics and expected totals; the test also exempts placed columns, the two layer tables and the NaN-off synthetic fields (read literally the text would hold `cloud_azimuth` bit-identical). Settle: amend I1 to "… not synthetic, and not a placed catalogue's placement column".
- **F-3-4** `:804-805` — gap: the stars' expectation is the test's own arithmetic from the stellar-pattern weights, while the stage also places its young stars by `sfr_modulation` (`systems.py:120, 626`). Settle: read the expectation from the stage's own input to `ring_star_count`.
- **F-3-5** `:1007` — gap: I3's check does not read `q.only_if` (`spec.py:128`), the field that decides whether a row is judged. Settle: add `q.only_if[0]` to `named`.
- **F-3-6** `core/stage.py:310-315`, `specs/graph.py:184-188`, `:1124-1125` — gap: publishing one composed field gives a stage `may_place` for everything it requires; its non-composed outputs (`gas_pattern`'s scalars) can carry the layer to any physics stage, and `binning_stages` does not trace them; only I1's single-run walk stands behind this. Settle: test those outputs on/off at a second template and seed, or propagate "layer-dependent" through composing stages in the graph.
- **F-3-7** `BUILD_III.md:104-105` vs `:1281-1286, 1155` — gap: I4 says "composed placement weights only"; `clouds` requires 21 synthetic fields and `clusters` `cloud_source_offset`. Settle: amend I4 to "… and the layer's synthetic fields, for placement only", made checkable by F-3-1's test.
- **F-3-8** `BUILD_III.md:106` — stale: "by `cluster_radius`"; the binners use `cluster_birth_radius` (`:1157-1161`). Amend the text; extend line 1161 to every placement column.
- **F-3-9** `:2164-2193` — gap: the guard that only `compose` branches on the layer looks for the identifier `layer` in a test expression; an alias, `compose.setting(...) == "on"` or a branch on `compose.words(...)` slips through. Settle: flag any `.layer` read outside `compose` and any `setting` / `words` call outside the API's echo sites.
- **F-3-10** `:13-14, 29-34, 586-589` — stale: the docstring presents I2's pre-L1 half and G1's "no per-object assertion" as current.
- **F-3-11** `:193-194, 215, 670-671` vs `BUILD_III.md:92-95` — three gaps: comments cite G2's "one unit" as held, the text says four; `EXPECTED_TOTAL_UNITS = 2` is labelled measured where the measured count is 1 (`:709`); the text's "average to 1 to 1e-13" is asserted nowhere (nearest 1e-12 on SMALL, `:2069`).
- **F-3-12** `:2011` — gap: under a texture reroll the expected totals are held at 1e-12 relative (~4 600 ulp at 16 693), not I1's four ulp. Settle: `same_expected_total` there.
- **F-3-13** `:1489, 1498, 1779` vs `BUILD_III.md:75-76` — gap: no "does not keep, with the number" clause asserted for the `arm_piece` and `gas_spur` columns or the two gradient columns; `fielddoc.py:215` checks only non-empty.
- **F-3-14** `core/fielddoc.py:221-224`, `:1513` vs `BUILD_III.md:77-78` — gap: rule 3 requires a measured, cited statistic; the check admits "none read (#95)", which the four cloud-texture columns use.
- **F-3-15** `BUILD_III.md:81-82` vs `:171-182`, `compose.py:234-238` — gap: rule 5 says no stored grid defines a field; the clustering and gas fields are evaluated with stored per-cell normalisers, and no rule-5 test exists. Settle: recompute a cell's normaliser from (seed, cell) at a point and match the published value, or amend rule 5.
- Notes: the bright catalogue's realised ring totals are asserted in `tests/test_bright.py:428`; I5's viewer half lives in `frontend/src/galaxy/layer.test.ts` (nine cases, not audited — after S68's panel, confirm every loader sends `layer=off`); `GAS_RING_FIELDS` are commented "physics read per ring" but declared synthetic and NaN off (a labelling question).

## 4. The pictures traced (strand 4; one Opus reader; the seven committed frames, its own API on :8031)

All seven captures are on the rgb set (no instrument PSF; every point the display sprite) under each template's
`TEMPLATE_TUNING`: point gain 4, cell outlines on, starlight 0.55 with gas and dust at 1, extinction strength 1.25,
bloom 2.25 / 2, ACES; the clouds as extinction off for the Milky Way and on for NGC 4414. **Every feature traces to a
published array, header entry or layer field: no invention in D5's sense.** Features by the label that decides where
or whether they are drawn (synthetic over seeded over derived; display only where the feature exists by a display choice):

| frame | derived | seeded | synthetic | display |
|---|---|---|---|---|
| milky_way-field | 4 | 3 | 6 | 2 |
| milky_way-physics-only | 2 | 4 | 0 | 1 |
| milky_way-stars | 2 | 3 | 0 | 2 |
| milky_way-zoom | 1 | 2 | 0 | 1 |
| ngc_4414-field | 3 | 3 | 2 | 1 |
| ngc_4414-stars | 1 | 2 | 0 | 1 |
| ngc_4414-zoom | 1 | 2 | 1 | 1 |

- **F-4-1** display — `tuning.ts:445` (`cloudsExtinction: false` for the Milky Way) with `fieldFragment.s66.glsl:505`: the physics-only frame has a sharp circle at R = 4.72 kpc (−7 % between 4.61 and 4.77 kpc, fainter circles at other level-0 edges) because `dust_diffuse_share` is constant per level-0 ring and jumps 0.478 → 0.692 there; with the clouds' own dust off, 30–73 % of each inner ring's dust and 0.49 of the disc's is missing from every Milky Way frame. Settle: capture with clouds as extinction on; if the circle goes, it is the display default's.
- **F-4-2** gap — `components.ts:244-252` vs `systems.py:272-279`: the cell outlines are drawn at `lo + (hi − lo) i / 32` on 0–30 kpc, but the model's level-0 edges are `linspace(R[0], R[-1], 33)` = 0.0375 … 29.9625 kpc, published as `gas_fluctuation.edges`; the grid in the four star-first frames is off the model's cells by up to 37.5 pc (~33 px in the Milky Way zoom, ~67 px in NGC 4414's). Settle: draw from the published edges.
- **F-4-3** gap — `cloudOpacity.ts:89-101, 196`: the elongated clouds' axis ratio λ₊ and angle are a formula the viewer applies to the published strain; no route publishes a cloud's shape (the model's own λ₊ in `layer/noise.py:520-532` describes the gas field's spectrum). Settle: a per-cloud axis ratio and angle in `/api/clouds`, or the formula declared as the model's.
- **F-4-4** display, against RENDER_PHYSICS §8 — `tuning.ts:441` (`starsIntensity: 0.55`) and `:444` (`extinctionStrength: 1.25`, D228's exception): in every committed frame the starlight is drawn at 0.55 of its filter integral while gas and dust stay at 1, and every optical depth is 1.25× the model's, so the frames' colour is not the filter integral of the model's emission. For the verdict: does a per-component intensity other than 1 in a template's committed defaults count as §8's "colour applied for appearance"?
- **F-4-5** display — `fieldFragment.s66.glsl:435`: the march's dither is a hash of `gl_FragCoord`, the viewer's one seed of its own, declared as sampling; it shows as fine grain. Settle: capture with dither off and check the frames differ only below the march's step.
- **F-4-6** display — `GalaxyTab.tsx:571` (the sample at `weights.sampled` 0.185 / 0.42) with point gain 4: the large coloured dots in both field frames are single sample stars (K giants and A stars of 30–340 L☉, several at 16–23 kpc; the 20 brightest hold 38 % of the sample's light) reading as cluster-sized objects. Published and seeded: a label, not an invention.
- Also seen: neither star-first frame shows arms (the points dominate at point gain 4); the Milky Way star-first frame has a grey-blue haze to its corners (RGB 18, 21, 27 at R ≈ 28 kpc; bloom, unverified); the bar's gas lanes have a width the model declares a placeholder (`gas_pattern.py:510, 639`).

## 5. The register pass and the pictures' residue (strand 5; one Opus reader)

**The counts agree:** `debt_counts` gives (122, 51) over 173 numbered items; the verdict table's 11 + 111 and its
discharged rows sum to the same; the permanent and carried lists are exactly the un-struck items. Items 53–64 and
74–78 are absent: 74–78 reserved for S21b and unused, 53–64 unexplained in the register (F-5-15; the counts unaffected).
Of the 122 open items about 95 stand as written; the rest:

- **F-5-1** discharged in fact — #137 (`GALAXY_INPUTS.md:3710-3729`): it closes when `CENSUS_STATISTICS` is empty after L1's ring-first draw; `test_layer.py:115-118` has `CENSUS_STATISTICS = {}` since S61. Strike it, or narrow it to the one-ulp expected totals.
- **F-5-2** trigger fired — #39 (`:1985-1990`) says the ensemble's diagonal is harmless until a published quantity depends on two seeds: `systems` now places its young stars by `sfr_modulation` (`systems.py:45, 120, 626`), drawn on `pattern_seed` (`pattern.py:1102-1130`), beside its own `systems_seed`, while `spec.ensemble` still sets every seed to k (`spec.py:1199-1202`). No statistical row reads a two-seed quantity yet.
- **F-5-3** half closed — #114 (`:3337-3338`): `/api/clusters` and `/api/bright` take `filters=` and return `response` (`service.py:262, 289`) and the star-first points draw from it (`GalaxyTab.tsx:435, 442`); only the field mode's region-regime cluster colours still use the blackbody share (`:336`). Narrow the entry.
- **F-5-4** half closed — #115: the "drawn twice" half is closed in the star-first mode by the age partition (`bright.py:58-60, 70-76`); the field mode's sample and "a dissolved cluster is a point" remain.
- **F-5-5** retired model — #15 (`:1114`) is "PERMANENT for the simple model"; no simple model since D170 (`basic.py:3-8`). What remains is row 22's tilt, #47's.
- **F-5-6** scope understated — #128(b) (`:3604`): the mixed-slab `face_on` moved at S54 to `specs/templates.py:83-91`, read by `face_on_colour` (`:98-101`), which is `ngc_4414`'s template check `colour_b_v_face_on` (`templates.py:922-936`): the check reads a geometry neither the dust stage (layered since S52) nor the viewer uses; #136's 0.636 is read through it.
- **F-5-7** stale text — #21 (`:1341`) "published and unread" and #80 (`:2851`) "unused" of `disc_dominance`: read by `swing_window` (`pattern.py:178`) and `bar_formation_time` (`:353`); #21's verdict stands (`bar_half_length = BAR_LENGTH_RATIO × R_d`, `:801`), its reason is overtaken.
- **F-5-8, F-5-9** stale row labels — #87 (`:2955`) "row 30 is owed" (row 30 is now the core-collapse rate, `spec.py:221`); #93 (`:3012`) "row 32 is owed" (now the globular-cluster mass, `:239`), and its T_d 19.54 K / L_IR 1.62e10 superseded by S52's 18.52 K / 1.2006e10.
- **F-5-10, F-5-11** stale constant and path — #43 (`:2124`) names `NET_YIELD`, retired at D170 (`basic.py:137`; the test renamed, `test_audit.py:482`); #33 (`:1812`) puts `IA_METAL_TO_IRON` in the deleted `advanced.py` (it is `basic.py:153`).
- **F-5-12** deleted test citations — #11, #19, #26 (`tests/test_models.py`), #39, #42, #47; most serious **#154** (`:3938`): "pinned in `tests/test_segments.py`", deleted at S60 (7be85c8); no surviving test pins its 0.59 % / 1.20.
- **F-5-13** the named closer has passed — #110 (`:3264`, "V7 (S64) discharges this": the value noise is still drawn, `region.ts:41, 113, 167`, GLSL `:731-757`, `RegionVolume.tsx`); #159 (`:4024`, "V7 (S65)" — S65 was V6b); #160 (`:4040`, V5/V6: still two rules, `bright.py:344-356` vs `systems.py:793, 875`); #161 (L2/V6); #162 (`:4067`, V5); #166 (V7 or V8).
- **F-5-14** the closer names this audit — #171 (`:4153`) and #173 (`:4170`, "one pass, Audit V's"): §0 does not take them; #173's randomised-order run of the migration test is a measurement, safe under B3.
- **F-5-15** the numbering gap above.
- **F-5-16** the frames show less than §0 promised — the Milky Way template pins a bar (`templates.py:590-596`) but `milky_way-field.png` shows no long bar (A₂ 0.054 against A₁ 0.057: the dominant mode is m = 1) and no dark lanes (dark fraction 0.018); `ngc_4414-field.png` has an outer disc redder than its inner (Δ(B−R) +0.19) and no blue-white complexes.
- **F-5-17** the four `-stars` and `-zoom` frames do not show the whole disc (a 494–642 px against a 512 px half-width) and the `-stars` frames carry a line grid; their metric rows cannot be set beside a goal's.
- Parked though written "carried": #141 (its closer outside BUILD_III), #134 (the owner declined the only closer), and #3, #19, #26, #27, #28, #42, #49 (blocked by ruling 7, `basic` frozen).

**The goal metrics on the committed frames** (`tools/goal_metrics.py --table`; the goal rows are D227's, which the reader was blind to):

| frame | Δ(B−R) | A₂ | dominant m | arm / interarm B | dark fraction |
|---|---|---|---|---|---|
| milky_way-field | −0.334 | 0.054 | 1 | 1.63 | 0.018 |
| milky_way-physics-only | −0.338 | 0.012 | 1 | 1.07 | 0.000 |
| ngc_4414-field | +0.187 | 0.198 | 2 | 2.85 | 0.030 |

**The residue, in the reader's words.** *Milky Way:* a round white-yellow core under a warm disc, a grainy, tightly
wound two-armed inner pattern opening into a grey-blue outer band that reads mostly as a ring; a handful of pink
knots, no dark lanes and no long yellow bar — not yet "the same kind of picture": the residue is in the bar, the lanes
and the knots, not only in hand-drawn irregularity, though the outer disc is bluer as promised. *NGC 4414:* the
inclination and the dominant yellow core are right and the fine streaky dust reads as mottling, but the disc is small
and faint, ringed by a dozen isolated green-white and pink point knots (#183), with no blue-white complexes and an outer
disc redder than the inner — right at a glance in inclination and the core, partly in mottling, not yet in colour or
in the complexes §0 expected to read merely as procedural.
