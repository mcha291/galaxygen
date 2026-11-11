# AUDIT_VI — Session 94: the fifth build's audit (S86–S93: BUILD_V's batches M1, M2, M3) — BUILD_V row 93

Once, after the build, as the project does (S10's two runs, S21's aim (a), S37's Audit III, S43's Audit IV, S69's
Audit V); commissioned by BUILD_V §2 row 93 and §6 ruling 5 ("at the end: one session that reads what three batches
did"; the owner's word of 2026-11-02, D252) and started on the owner's word of 2026-11-12 ("read the docs and continue
with the project"). **Nothing here changes a number in the model or the viewer** (B3): a finding that would is a debt
or a ruling for the owner, with the sentence that decides it. The findings, the method and the counts are the audit's
decision (D263); the fixes are the next session's.

## 0. The aim, stated before any audited file was opened (D113), and how it is to read

Written by the Fable lead on `session-94` (cut from `main` at dd003ee) from `BUILD_V.md`'s rows 86–93 and §2a,
`BRIEF.md` as S93 left it, the headings of D254–D262 and the file names of `git diff --stat s85..main` alone; committed
as the session's first commit, before any file this audit judges was opened in the session. Where it names a file it
names it from that listing, not from a reading. The range audited is **tag `s85` to `main`** — the register pass's
close to M3's merge: 32 files under `model/galaxy` (1 711 lines added), 56 under `tests/` (13 817 added), eight
readings, the register's entries and nine decisions.

**What sets this audit apart from Audit V.** BUILD_III was built one phase a session with the full suite at every
close. BUILD_V's batches were built ahead of the suites (C7 as re-amended, D245 / D246): the runner's suite read once a
batch, this machine's pins skipped on the runner, re-pin passes written from failed logs, M3's close in five parallel
lanes and several rulings taken on recommendation in the owner's place. So the audit's weight is on what that method
could have let through: **a pin moved to green that was a judged bound, a test that asserts less than its decision
says, a mark that hides a red, a number that entered with a batch and was never read against its page.**

**The five strands, each one question, each with its own reader:**

1. **Every citation entered since `s85` re-read against the sentence it cites.** The lines the batches added to
   `docs/READING_ARM_PIECES.md`, `READING_ARM_SEGMENTS`, `READING_BAR`, `READING_GAS_PATTERN`, `READING_GAS_SHOCK`
   (M1), `READING_DUST` (new), `READING_CLOUD_LAYER`, `READING_CLOUD_SIZES` (M2), and every constant, pin, table and
   about-line that entered or changed in `model/galaxy/models/level0.py`, `stages/`, `layer/`, `core/cosmology.py`,
   `specs/` and `templates.py` in the range, each labelled **MATCH / DIFFERS / ADOPTED-NOT-MEASURED / MISATTRIBUTED /
   UNREACHABLE** as Audits III–V's re-readers did (D186, D194, D233): a number is checked only on a fetched page;
   equation and table numbers counted from the source; nothing from recall (a recalled value is `[recall — NOT READ]`
   and out of the table); a citation's stated coverage checked against what the source measures. Two readers: **1A**
   the arms and the bar (M1), **1B** the clouds, the dust, the gas, the populations and the ionized gas (M2, M3). The
   readers are **blind to the builders' reports**: they receive the diff, the readings and the sources, never
   `DECISIONS.md`'s build paragraphs.
2. **What the batches built, re-measured** in `tests/test_audit_vi.py` (the one test file the audit adds), on seeds
   and a mesh the builds did not pin, each by an estimator the audit writes and not the build's own helper (B3): the
   arm census's births under a one-ulp perturbation (#216); the draw paths' bits at two thread counts (#218); one
   placement rule for the old stars of both catalogues (#160); the spur's height as the excess over the ring's trough
   and the walk's end at the arms' budget (#164, #165, #213); the ring as the unit of the clouds' sector weights and
   the stars' and remnants' ring draws (#161, #197); the cluster points' closure through a filter set (T2 / #114); the
   sample's luminosity function along equivalent evolutionary points (#113, #171); the remainder's kept windows
   summing to the whole (#175); the diffuse gas's line ratios against the constants they cite (T10 / #119). And
   **#173**, the register's item for this audit since S85: the migration test run alone and in a shuffled order under
   a fixed hash seed, to tell state left by an earlier test from a hash-order dependence. A closure that holds only on
   the seed its build pinned, or a statistic the realisation does not reproduce within its own noise, is a finding.
   Short named nodes only, one process at a time (D246); nothing here runs the suite.
3. **The re-pins and the gates re-derived, not re-run.** For every literal, bound, mark and list that changed under
   `tests/` in the range (and in `specs/spec.py`'s `MISSES` and `specs/templates.py`'s `CHECK_MISSES`): is it an
   as-measured record or a judged bound; if a bound, which decision moved it and does that decision say so; every
   `machine_pinned`, `xfail` and `skip` added or lifted, with what it now hides; every "no judged bound moved" in
   D256, D258 and D260–D262 held against the diff. Then, for each closure test a discharge rests on (#114, #148,
   #160, #161, #166, #174, #175, #197, #213, #216, #217, #218 and the re-based layer-off reference), what the test
   *actually asserts* beside what the register's closer promises, and whether the change the closer forbids could pass
   the test as written. Two readers: **3A** `s85..s90a` (M1, M2), **3B** `s90a..main` (M3).
4. **The viewer and the pictures.** The viewer's changes in BUILD_V (`s80..main` under `frontend/` and
   `interface/`: the four viewer rows 81–84, the batches' viewer halves, `s83-robust`) read against D5 as amended
   (nothing drawn that no published quantity stands behind; no structure, parameter or seed of the viewer's own), D2
   (one `fetch`) and D1; each feature the nine committed frames gained or lost since Audit V's trace traced to the
   array and the field behind it; the request fixture held against a walk of the built viewer on M3's model if a walk
   fits a bounded run (S93 respelled it by hand and held `jwst_nircam`'s requests to `wfc3`'s), else recorded as owed;
   and `tools/goal_metrics.py`'s numbers on the committed frames set beside the goal pictures' and D227's table, one
   plain sentence per picture saying how far it stands from its goal — never a target, never a tuning (C6, D113).
5. **The register pass and what "done" still wants.** Every open item (108 at the open: 43 permanent, 65 carried)
   re-stated in one line with its verdict re-ruled against the repository as it stands — discharged in fact by a
   session that did not say so, permanent without its reason written in (B5), carried with a closer whose session has
   passed, a discharge whose closer was not met — and the counts re-derived against `tools/progress.py` and the pin
   in `tests/test_audit.py`. Then the rulings taken on recommendation (D262's list, `BRIEF.md`'s) held against the
   decisions and commits for one taken and not listed; `VIEWER_TASKS.md`'s rows against what is built; and BUILD_V
   §7's "what done means" read clause by clause, saying what each still wants.

**Method (Audits III–V's shape; D186, D194, D233).** Read-only reader agents on Opus, one strand or one slice each,
the builder of strand 2 in a worktree of its own on a branch cut from `session-94`; at most three running at once
while the 5-hour window is under 40 %, one of them heavy at most (the lead's reading of the rationing rule on fresh
windows, 3 % at the open — said here so the owner can refuse it). Each writes one Markdown note in the scratchpad with
a summary table, per-source notes, what could not be read and the labels; the lead assembles them into §1–§5 and
numbers the findings F-<strand>-<n>, each with its class (DIFFERS, moved bound, weak test, hidden red, invention,
mis-ruled debt, display), the file and line, and the sentence that would settle it. **Then the gate**: Fable's verdict
on each finding — upheld, dismissed with the reason, or a ruling for the owner — transcribed to D263; the fixes ordered
by class into the next session's `BRIEF.md`. B3 holds throughout: the audit checks, the next session fixes, no model
number moves, no frame is regenerated, no pin is re-pinned.

**What this audit does not do.** It does not run the full suite, `verify_clone` or this machine's pins (D246); it
does not re-fit a template or open `basic` (frozen, ruling 7); it does not re-rule the owner's rulings of 2026-11-03
and 2026-11-10, and it lists — without judging — the rulings taken on recommendation, which are the owner's to
re-rule; it does not touch the deployment (row D). A reader that finds a source contradicting what a batch assumed
writes it as a finding and continues.

## 1. The citations since s85, re-read (strands 1A and 1B; two Opus readers; nothing from recall)

Two read-only Opus readers on `git diff s85..main`, blind to DECISIONS, LESSONS, BRIEF, RESUMING, BUILD_V and
GALAXY_INPUTS §11 (none opened): **1A** the arms and the bar (M1, 17 slice files), **1B** the clouds, the dust, the gas,
the populations and the ionized gas (M2, M3). Every label rests on a page fetched in the session (WebFetch on arXiv
abs, ar5iv and arxiv html, SVO, JDox, the CMD FAQ; arXiv PDFs read through `pdftotext`); 1A redid three derivations by
hand, 1B its arithmetic in two scratch scripts; no pytest ran and nothing in the repository changed. **84 rows:** 1A 49
(15 code, 34 reading) — MATCH 38, DIFFERS 3, ADOPTED-NOT-MEASURED 1, MISATTRIBUTED 0, UNREACHABLE 2, unread 4, n/a 1;
1B 36 (35 labelled) — MATCH 31, DIFFERS 2, MISATTRIBUTED 2, ADOPTED-NOT-MEASURED 0, UNREACHABLE 0. **The answer, in
the readers' terms: no wrong number reaching a computed field or a pin was found** — "every code constant and pin in
the slice matched its page" (1A); "every number that reaches a field in my slice ... matched its page" (1B). The ten
findings are wording, provenance and coverage.

| source group (strand) | rows | MATCH | DIFFERS | ADOPTED | MISATTR. | UNREACH. | unread / n/a |
|---|---|---|---|---|---|---|---|
| `level0.py`, `core/cosmology.py`, `templates.py`'s bar pin (1A) | 13 | 12 | 0 | 0 | 0 | 1 | 0 |
| `layer/arm_pieces.py` (1A) | 2 | 1 | 1 | 0 | 0 | 0 | 0 |
| READING_ARM_PIECES, READING_BAR (1A; one row shared) | 19 | 15 | 2 | 0 | 0 | 0 | 2 |
| READING_ARM_SEGMENTS (1A) | 7 | 4 | 0 | 1 | 0 | 1 | 1 n/a |
| READING_GAS_PATTERN, READING_GAS_SHOCK (1A) | 8 | 6 | 0 | 0 | 0 | 0 | 2 |
| `level0.py` DIG_*, `nebular.py`, `spec.py` row 2, `photometry.py` (1B) | 14 | 14 | 0 | 0 | 0 | 0 | 0 |
| `tools/fetch_filters.py` / `instruments.json`, JWST (1B) | 9 | 6 | 1 | 0 | 1 | 0 | 1 unlabelled |
| READING_CLOUD_SIZES, READING_CLOUD_LAYER, READING_DUST (1B) | 12 | 11 | 1 | 0 | 0 | 0 | 0 |
| `stages/systems.py:819, 832` (1B) | 1 | 0 | 0 | 0 | 1 | 0 | 0 |

Not a plain MATCH beyond the findings: Erwin 2019's MNRAS volume / page (only the DOI printed) and Herrera-Endoqui
2015's NGC 4414 pitch 28.9 ± 6.0 (VizieR table3 "HTTP 404") UNREACHABLE; PITCH_SHEAR's intercept self-declared
[recall] (n/a); MJ07's "0.25-0.80" where the page prints "0.35-0.80" (DIFFERS, low, not numbered). MATCHes with a
note: Erwin's "367 ... (Spearman 0.61)" (Table 3 prints neither), Chugunov 2024's "Fig. 17" unconfirmed, DG16b's
"a hint of" dropped, Chugunov 2025's zones azimuthal; LD20's 78.6 R^1.98 fitted to Rice et al. 2016's catalogue,
Marasco 2017's R0 end fixed at 52 pc, V02's A_B - A_V derived, the CMD FAQ's "have not been carefully checked".

- **F-1A-1** `layer/arm_pieces.py:25, 315, 566, 628`, `level0.py:1159` — DIFFERS (rule vs its own cited table);
  wording / rule, not a number. "the sources measure the pitch's variation along an arm, not a reversal of its sense";
  HR15 Table 5, M51 arm B: "-200->-250 | 7.11+-0.05 | -10.3+-1.4 | 0.43+-0.04". Settle: "Is a measured reversed
  segment (HR15 Table 5, M51 arm B, -10.3 +- 1.4 deg at 7.1 kpc) outside what the model draws by ruling (M51
  interacting), and does the about-line say so instead of 'the sources measure ... not a reversal'?"
- **F-1A-2** `READING_BAR.md:666`, `READING_ARM_PIECES.md:769` — DIFFERS (a quoted range narrower than the table);
  medium. "at 0.76-0.94 a (DG16b Table 5)"; the table also prints T 5-8 0.66, SB all T 0.68, SB T>=5 0.62. Settle:
  "Which DG16b Table 5 row is the Milky Way template's comparator (SB, T<5: 0.78 +- 0.19; or the mass bin 10.5-11:
  0.90 +- 0.20), and is #146's miss stated against that row's value and dispersion?"
- **F-1A-3** `READING_ARM_SEGMENTS.md:323` — stale arithmetic referent; low. "(28.9 - 19.0)/6.95 = 1.4 sigma from H17's
  mean"; H17 s3.1: "Our mean pitch angle is 18.0 deg"; on it 1.57 sigma; the conclusion is unchanged. Settle: "Use
  H17's 18.0 (s3.1) beside its percentiles, or say the 19.0 is the arm-number means' midpoint."
- **F-1A-4** `READING_ARM_SEGMENTS.md:330` — a directed reading the source cannot answer; low-medium. YH19 s IV.3.5
  prints only rho = -0.49, "much weaker than previously claimed"; no slope, intercept or scatter for the law's -8 deg
  and 6 deg. Settle: "Re-point #153's reading at a source that prints a pitch-shear fit (or at YH19's data to fit),
  and record that YH19 prints rho = -0.49 only."
- **F-1A-5** `READING_ARM_SEGMENTS.md:329` — ADOPTED-NOT-MEASURED (provenance); low. "15.0 deg pooled, four galaxies";
  HR15 prints no pooled mean, "Most pitch angles ... between about 10 and 30 deg". Settle: "Mark 15.0 as [inferred:
  pooled from HR15 Tables 2-5 by <reader>, weighting ...] or drop it."
- **F-1A-6** `level0.py:274` BAR_LENGTH_LOG_NORM — coverage; low. Erwin 2019's Table 3 fit is to barred spirals of
  log M* 9-11; the about-line names the h referent but not the mass range. Settle: "Add the fit's mass range (log M*
  9-11) to the about-line, or record what the model does outside it."
- **F-1B-1** `tools/fetch_filters.py:113`, so `instruments.json`'s jwst_nircam optics.about — MISATTRIBUTED (author),
  provenance only. "Feinberg et al. 2023, arXiv:2301.01779": first author McElwain, Feinberg second; the numbers match.
  Settle: "arXiv:2301.01779's first author is McElwain; the citation reads McElwain et al. 2023 (PASP 135, 058001)".
- **F-1B-2** `tools/fetch_filters.py:116` — DIFFERS (a derived comparison's wording), small. "which the two numbers
  here give to 0.5 %"; re-derived 6.628 m across the flats (+0.81 % over 6.575) and 6.6717 m circumscribed (+0.48 %
  over 6.64). Settle: "the comment says 0.8 % (flat-to-flat) and 0.5 % (circumscribed)", or a reason the outer
  segments' flats differ from 4p + f.
- **F-1B-3** `READING_CLOUD_SIZES.md:69-70` — DIFFERS (a source's definition), prose feeding the owner's ruling #182.
  "the catalogues' R is an equal-area radius" holds for LD20, not MD17 (inertia-matrix radius, eqs. 18, 22; on LD20's
  radius MD17's clouds give 57.5 R^2.10); LD20's 78.6 R^1.98 is "for the clouds in the R+16 catalog"; on it a 1e7
  Msun cloud is 378-379 pc (the note gives both), right on the relation as quoted.
  Settle: the MD17 relation "restated on LD20's equal-area radius ... or labelled as MD17's inertia-matrix radius; and
  78.6 R^1.98 is labelled Rice et al. 2016's clouds as fitted by LD20".
- **F-1B-4** `stages/systems.py:819, 832` (S93 docstrings) — MISATTRIBUTED (a modelling choice attributed to a source),
  wording. "bound is drawn independent of mass and age (Lada & Lada 2003)"; the page: "only the most massive clusters
  in our catalog are candidates for long term survival". Settle: "the docstrings say the fraction is Lada & Lada's
  and the independence of mass and age is the model's choice (their sec. 2.5 names a mass cut)".

**Not read / not reached.** *1A:* not fetched Elmegreen & Elmegreen 1995, Salo 2015's fitting form, Egusa 2017,
Wada, Baba & Saitoh 2011, Shabani 2018, Martinez-Garcia 2009, Grasha 2017 and 2019, Dobbs & Baba 2014 §3.7, Corbelli
2018, Querejeta 2024's 7.5" dilation, Chugunov 2024's figure numbers; MERGER_HEATING's unchanged 35 km/s target and the
model outputs (26.68 km/s, 0.507, 0.40, the spur bounds) not re-run. *1B:* not fetched Bronfman 1988, Malhotra 1994,
Remy-Ruyer 2015 eq. 5, Licquia, Newman & Brinchmann 2015, JDox's NIRCam filters page; NS06's Table 1 read through
`pdftotext` with its rows offset; [recall]-labelled sources and READING_DUST's model measurements are not rows; the
changed lines of `stages/dust.py`, `clouds.py`, `clusters.py`, `bubbles.py`, `chemistry_dtd.py`, `bright.py`,
`spectra.py`, two `layer/` and three `api/` modules carry no cited claim; #168's two-layer derivation not re-derived.

## 2. What the batches built, re-measured (strand 2; one Opus builder in a worktree; `tests/test_audit_vi.py`, the one file the audit adds)

One Opus builder in its own worktree on `s94-measure` (cut from `session-94` at 766b431), merged at 83c85d8; no byte
outside `tests/test_audit_vi.py` changed. The mesh is `AUDIT_VI_GRID` (96, 320, 6, 72), which no build pinned; the
texture seeds are 5151, 6060 and 31337 (pattern 4141 for #218), and each estimator is the audit's own, written in the
test rather than taken from the build's helpers. Only #164's trough calls the model's point function. The file's 10
nodes ran in 7 min 42 s (461.96 s) single-threaded with EXIT=0. The file has no strict xfail. **Items examined 10:
7 hold** (#216, #218, #175, T2 / #114 to its bounds, #197, #164 / #165 / #213, T10 / #119). **#173: neither candidate
reproduced.** **Not reached:** #160 and #113 / #171; #161 was not measured separately. No measured claim failed. The
three findings are about evidence and wording, not numbers.

| item | claim | what the build pinned | what was measured (seed, grid, estimator, number) | verdict |
|---|---|---|---|---|
| #173 | migration node: hash order or left state | 0.8845979 vs 0.9284296 once, at 16ab0c3 | four numbers bit-identical under hash seeds 0, 1, 2, 12345, 28504 (old -0.2801196316960978 / -0.005541389266041417); test_chemistry.py whole in file order 20 passed (1341 s); three shuffled subsets (9401 / 9402 / 9403) 4 passed each | neither reproduced; F-2-1 |
| #216 | arm census births bit-independent | records, the oracle the model's `ap.counted` | `ap.census` re-run on the published inputs (8 fields, 6 of 6 cases bit for bit); censuses MW (51, 13), (47, 11), (41, 10), ngc_4414 (21, 21), (18, 18), (24, 24); design counts nudged one ulp both ways, every crossing azimuth one ulp both ways; near-integer rings 3 per MW case, 1 per ngc case; gap ties MW 5151 1 of 7, ngc 2/20, 3/17, 3/23 | holds; see F-3B-2 |
| #218 | draw bits independent of BLAS threads | AST guard, no two-thread run | 7 answers (/api/region levels 0 and 2, clouds, clusters, remnants, bright at l_min 3000, layer), sha256 at 1 thread vs the machine count: all equal; grep finds no unguarded BLAS product | holds |
| #175 | the remainder's kept windows sum to the middle | the sum to 1e-12 (part tautological) | ngc_4414, 31337, RGB, l_min 2000, against the answer without kept=: shared arrays within 1e-12, windows >= 0, sum <= middle, spans contiguous | holds; F-2-2 |
| T2 / #114 | clusters' response through a filter set | rgb ratios 0.93-0.94 | `sho` set, MW 5151: census response against the render's young light, each filter in 0.80-1.20, max/min < 1.03; ratios not printed | holds at the stated bounds |
| #160 | one placement rule | test_bright one-rule test | draft refused (l_min 100: 4 423 669 expected stars > 200 000) | not reached |
| #197 (#161 not separate) | ring draws in their own ring | one parent cell, seed 0 | both templates, 5151 and 6060: region, remnants, clouds' birth radius against ring edges (1e-9 kpc): 0 outside (e.g. 1559 remnants, 17 050 clouds) | holds |
| #164 / #165 / #213 | spur height over the trough; walk ends at the budget | 1440 cell centres | MW, three seeds, the gas_spur table: no foot past the last ring with amplitude > 0; height = crest - trough on 8192 azimuths, within 2e-3 (the builder's bound) | holds; ngc_4414 draws no spur |
| #113 / #171 | sample along equivalent points | - | - | not reached |
| T10 / #119 | diffuse gas line ratios | hand formula to 1e-12 | relation from the register's transcription: [N II]/Ha 0.58270, [S II]6716/Ha 0.43868; per-ring equal to 1e-12, both templates x three seeds; 6716/6731 = 1.44818 vs R_max 1.4484 | holds; F-2-3 |

- **F-2-1** mis-ruled debt / stale text. Place: `docs/GALAXY_INPUTS.md` #173. Evidence: the entry records old_lots
  0.8845979 against old_none 0.9284296. Today's model gives -0.005541389266041417 against -0.2801196316960978,
  bit-identical under five hash seeds, and the file order and three shuffles are green. "Tell the two apart" cannot
  be met. Settle: "#173 is closed as not reproducible on the current model: no hash-order dependence (5 seeds,
  bit-identical) and no order dependence (file order and 3 shuffles), held by test_audit_vi::test_173_."
- **F-2-2** weak test. Place: `tests/test_v7_header.py:256-259`. Evidence: `rest = middle - sum(parts)` is defined,
  then `sum(parts) + rest` is checked against `middle` to 1e-12, which is true by construction. The test's other
  assertions carry content. Settle: "The sum line in test_the_remainder_s_middle_part_s_kept_windows_sum_to_it is
  dropped or replaced by a check against the answer without kept=."
- **F-2-3** stale text, minor. Place: `nebular.py` dig_line_ratios. Evidence: it takes the doublet clamped to 1 cm^-3
  (1.44818). The fit's n_e -> 0 limit is 1.4498, and the cited R_max is 1.4484. No number moves; 1B's note records
  the same 1.44818 as a non-finding. Settle: "The comment and #119 say 'the doublet at 1 cm^-3, the fit's lower edge
  (1.4482)' in place of 'the low-density limit'."

**The builder's incident, as the note records it.** Argument files generated with `--collect-only -q` on top of the
project's `-q` came out empty, so `pytest @empty` started the full suite at about 01:53. It was seen within about a
minute from "collected 0", the processes were stopped, and no result was taken from the run. Separately, a small
`uv run python` ran for a few seconds beside a pytest run, against the one-process rule. The note records this too.

**Not reached / not measured.** #160 and #113 / #171 were not reached. #161's own claim (the clouds' sector weights
per ring) has no separate estimator. #164 / #165 were not measured on ngc_4414, which draws no spur. T2's ratios were
asserted to bounds, not printed. The 20-id shuffles of the whole test_chemistry.py were written but not run (22 min
each). Whether a module-level cache inside the model could hold left state was not examined.

## 3. The re-pins and the gates re-derived, not re-run (strands 3A and 3B; two Opus readers, read-only)

Two read-only Opus readers on `tests/` and `model/galaxy/specs/`; nothing was run or re-measured. **3A** `s85..s90a`
(M1, M2): 50 files, 49 read (the s90 reference json not), the diff 4 898 lines without it; about 275 records re-pinned
with a cause, 6 judged bounds changed each with a decision, 1 loosened identity with none found, 3 invariants changed
by design with decisions, about 10 strengthened, 0 tests deleted. **3B** `s90a..main` (M3): 30 files (6875+ / 238-;
`specs/` unchanged in M3); about 130 records plus 22 fixture strings, 6 judged clauses changed in form (all named by
a decision), 0 judged bounds moved in number, 4 strict-xfail sites / 6 cases added (all registered), 14
machine_pinned and 1 strict xfail lifted, 0 skips or non-strict xfails added, 0 tests removed. **The answers.** 3A:
no judged bound moved without a decision "among the bounds I read", but four were "reset to the very reading that
failed, plus a small margin", and one identity was loosened with no decision found (F-3A-8); one mark hides a red no
register entry carries, `BRIGHT_GATE_READ_OVER` (F-3A-5). 3B: no tolerance widened, no window re-centred, no bound
number changed, but the walk's bounds now judge a re-defined statistic and no decision says so (F-3B-1); no mark hides
an unregistered red, with two reservations (no `raises=` on #220 / #221; closures guarded by nodes the runner skips).

| change | where | decision | reader's verdict |
|---|---|---|---|
| gas ring mean `< 1e-13` -> `< 2e-13` (worst read 1.0036e-13) | test_bar, test_gas_pattern x2 | D255 r. 1 | F-3A-4 |
| power-budget share 0.4-0.9 -> 0.39-0.98 (read 0.934) | test_audit_v | D255 r. 2 | F-3A-2 |
| WALK_READ_DIFFERENCE_COARSE 0.49 -> 0.58 (read 0.5700) | test_audit_v | D255 r. 4 | F-3A-2; F-3B-1 |
| "reach boundary" class admitted in `unexpected` steps | test_pieces | D255 r. 5 | decided, reason a mechanism |
| price `< 3000` -> `< 3500` us, non-strict xfail kept (2839-3026 us in 3A's answer; 2924-3208 us at S87 in F-3A-1) | test_audit | D255 r. 6 | F-3A-1 |
| per-cell -> per-ring cloud equality (#161); continuous share (#202); empty named set (#214) | test_audit_v, test_v6_clouds, test_layer | D258, D257, D258 | by design |
| `top[here]` exact -> `approx(abs=1e-4)` | test_sfh_azimuthal | none found | F-3A-8 |
| #154 "worst cell and worst ring are one ring" removed; input window 0-1.0 -> 0-1.5 rad (1000-star guard) | test_audit; test_bright | D260 | named |
| `count >= counted(design)`, `earlier < births`, ties by identity (#216) | test_pieces | D260 | ruled rule; oracle the model's own |
| spurs' peak identity re-defined (1e-9 / 1e-12 unchanged) | test_audit_v, test_spurs | D261 C3 | definition change |
| walk read statistic re-defined, 0.27 / 0.58 carried | test_audit_v, test_spurs | not said | F-3B-1 |
| #217 oracle -> `v6_tiles.grid_threshold` + 5e-16 | test_v6_bright | D261 | F-3B-5 |
| upper clauses split into strict xfails (#220, #221) | test_spurs, test_bar, test_gas_pattern | D261 C1 | bound unmoved |

| mark | where | carried by | reader |
|---|---|---|---|
| `PRICE_RECORD`, non-strict xfail (S87 / S88) | test_audit | #154 | F-3A-1, F-3B-10 |
| `BRIGHT_GATE_READ_OVER`, strict (S88), still in main | test_clustering_gate | none (#161 struck) | F-3A-5 |
| `L1_GATE_READ_OVER_S90`, clouds leg, strict (S88); lifted S91 on XPASS | test_clustering_gate | #215 | 3A; F-3B-4 |
| `L1_GATE_READ_OVER_S91`, clusters, strict, added S91, lifted S92 | test_clustering_gate | #219 | F-3B-4 |
| `DUST_COLUMN_OVER`, MW leg, strict (S88) | test_v7_layer | #176 | 3A: OK |
| `HIERARCHY_197`, `OUTER_SPURS`, L1 clusters (S88): added and lifted inside M1 / M2 | test_hierarchy, test_modes, gate | - | F-3A-7 |
| 14 `machine_pinned` (S90a): 7 pure records (test_bar x2, test_modes, test_gas_pattern cell-mean and crests MW, test_pieces crest and masers); 6 also skip judged clauses; 1 test_v6b level-3 MW | 6 files | #216 / #217 | F-3A-3; lifted in M3 (3B: 13 for #216, 1 for #217) |
| `WALK_READ_OVER_S92` (seed 4242); `GAS_LANES_READ_OVER_S92`, `GATE_MAX_G_READ_OVER_S92` (MW only); strict, no `raises=` | test_spurs; test_bar, test_gas_pattern | #220; #221 | 3B reservation (a) |
| #222 size gate on kept=1, wfc3 x 3, strict, `raises=AssertionError` | test_v6_bright | #222 | 3B: bound unmoved |
| three-legs gate and two layer-off reference nodes, `machine_pinned` since S77 | test_pieces, test_layer | - | F-3B-3 |

| closure | what the test asserts | could the defect return unseen? |
|---|---|---|
| #148, #212, #161, #168, #198, #213 | one clock to 1e-12; `== 90.6`; per-ring counts equal, not all cells; an independent midpoint path; a 15-ring saturation case; `radius <= edge` | No (3A) |
| #209 | `pitch >= 1.0` on the audit's seeds; the constant == 1.0 | adequate, only on the audit's seeds (3A) |
| #154 (table) | `array_equal(table, reader cell means)`; statistic rel 0.05 | No; docstring stale (F-3A-9) |
| #167 | the scalar gone, counts down by one | removal held; per-cloud Z not reached (3A) |
| #197 | one parent cell, default galaxy, seed 0 | **Yes** (F-3A-6) |
| #139, #142 | no test written at S86 | not reached (3A) |
| #166 | bit equality, cached vs cold | **Yes**: removing the cache stays green (F-3B-6) |
| #216, #218 and the reference, #215 / #219, #217, #160, #114 / #174 | as F-3B-2, 3, 4, 5, 8, 9 state | 3B (below) |

- **F-3A-1** mark / weak test; low, method — `tests/test_audit.py` price test, `xfail(strict=False,
  reason=PRICE_RECORD)` around `< 3500.0` (PRICE_OVER at S87: 2924-3208 us vs 3000; 3A's answer gives 2839-3026 us):
  "a non-strict xfail around a bound can fail nowhere"; the runner's XPASS.
  Settle: "Make it a record (print, no assert; or machine_pinned with the bound) or a gate (strict, under a bound
  measured on the runner); a non-strict xfail with a bound is neither." See F-3B-10.
- **F-3A-2** moved bound, decided, reason = the failing reading — power share and `WALK_READ_DIFFERENCE_COARSE`, each
  the failing reading + 0.05 / + 0.01 (D256). Settle: "Re-declare each from seeds disjoint from the ones the test
  checks, so the bound is not fitted to the draw it judges." See F-3B-1 on the same 0.58.
- **F-3A-3** mark hides judged clauses from CI (disclosed, mostly) — six S90a `machine_pinned` marks also skip the MW
  pair-slope law (met by 0.013), the walk bound 0.58, "every chain long enough carries spurs", the hand census's
  clauses, the whole-ring MW bound and the gas gate-predictions verdicts, which D259 does not list. Settle: "Split each
  marked test so the record carries the mark and the judged clause runs in CI." 3B counts the fourteen lifted in M3.
- **F-3A-4** moved bound; the stated reason does not reach the size; medium — D255 r. 1 "each exact to its own
  rounding": 360 roundings give about 1e-16, the reading is 1.0036e-13. Settle: "math.fsum each component's cell means
  (response, lanes, pieces) over the ring alone; whichever is off 1 by ~1e-13 owns the tolerance, named there."
- **F-3A-5** hidden red / mis-ruled debt; high — `tests/test_clustering_gate.py` `BRIGHT_GATE_READ_OVER`: youngest
  slope -0.4750 (0.165 over 0.15), 40.71-100 Myr 0.8457; held under #161 (D256 (ii)), #161 discharged (D258), #215
  names the clouds only. Settle: "Open an entry (or widen #162) naming the young bright stars' L1 hold, its two
  readings, and what closes it." 3B's "no" covers the marks M3 added or lifted; this one M3 neither added nor lifted.
- **F-3A-6** weak test (#197); high — one parent cell (300), default galaxy, seed 0; the 0-below reading a probe
  script; the remnants untested. Settle: "A test that every level-0 star's and every remnant's radius lies in its own
  ring's [lo, hi) over both templates' whole catalogues."
- **F-3A-7** method — `HIERARCHY_197` hid `parent.size` 9 -> 16 for a batch; `BRIGHT_GATE_READ_OVER` and the L1 clouds
  leg have the same shape. Settle: "For each strict hold, a measurement run that records every assert after the first
  failure, written into the hold's comment."
- **F-3A-8** loosened identity, no decision found; low — test_sfh_azimuthal exact -> `abs=1e-4`; `built[past]` moved to
  `cell_law[past]` plus a record 0.00228. Settle: "D254's #154 paragraph names the identities that became records."
- **F-3A-9** stale text; low — test_audit #154 "2.6e-4 in a cell at worst" (pin 2.439e-3); test_bar #146 0.093 / 0.047
  / 0.684 (pins 0.0883 / 0.0437 / 0.667); test_gas_pattern's "feet out to 26.6 kpc" (none past 12.34 since #213);
  D259's list. No settling sentence in the note.
- **F-3A-10** weak scope; low — test_bar's body sliver: at 5.0 kpc no ring in the reach (`sliver.sum() == 0`). No
  settling sentence in the note.
- **F-3B-1** moved bound (in substance) / stale text; medium — the walk read was
  `|contrast / unspurred_contrast_at(foot) - 1|`, from S92 `|peak/column / point_crest - 1|`; 0.27 and 0.58 measured
  on the old one; D261 "no tolerance widened, no bound moved". Settle: "WALK_READ_DIFFERENCE and its coarse twin are
  re-derived on the crest statistic, or the decision states that the S70/S88 numbers are carried onto it by ruling."
  See F-3A-2.
- **F-3B-2** weak test; medium — #216's one-ulp probe only in scratch scripts; no test pins `BIRTH_COUNT_TOLERANCE` /
  `GAP_TOLERANCE`. Settle: "a test perturbs a plateau design count and a tied gap by one ulp and asserts the census
  unchanged." Strand 2 builds this probe.
- **F-3B-3** weak test / unverified record; low-medium — EXPECTED_LEAST's MW leg (0.1208, 0.1252, 6.696) -> (0.1208,
  0.1245, 8.214) "not re-run" (D262), the node and #218's two reference nodes `machine_pinned`. Settle: "the three-legs
  node and the two reference nodes are read by name on main's final model, and a cadence for them is ruled."
- **F-3B-4** fragile gate (not moved); low-medium — clouds -0.5035, clusters -0.4970 against the -0.49 edge, sd
  0.1030 / 0.1064. Settle: "the owner rules whether L1's judged clause reads the default census or a seed mean."
- **F-3B-5** weak test (machine-dependent guard); low — #217: here `10.0 ** LOG_L_GRID` equals math.pow bit for bit.
  Settle: "a source-level check (as test_ordered_products does) that both thresholds call grid_threshold."
- **F-3B-6** weak test; low-medium — #166: bit equality only. Settle: "the test asserts the second request does not
  call part_anchors (spy or counter)."
- **F-3B-7** stale record; low (wording) — the fixture's 20 respelled `kept=1` records keep the S73 walk's `bytes`
  (14 680 ... 27 944), kept=1 answers are 30 792-43 824; `tools/smoothness.py` sums them. Settle: "the walk on S93's
  model re-records the bytes." See F-4-1.
- **F-3B-8** mis-ruled debt / stale text; low — #160 met and held, still open, no decision says why (3B's brief listed
  it discharged; the register does not). Settle: "the gate discharges #160 on that test or states what it waits for."
- **F-3B-9** weak tests at the viewer edge; low — no test asserts GalaxyTab.tsx's `responseColors` call (line 432);
  #174 discharged with "no GPU has compiled the new vertex shader". No settling sentence in the note.
- **F-3B-10** note for 3A — the runner's "1 xpassed (test_audit's non-strict cost record)"; not read by 3B. See F-3A-1.

**Not read / not reached.** *3A:* the S60 tests behind #139 / #142; #167's per-cloud A_V against metallicity; the s90
reference json and its tests; D254 / D257 in full; test_nebular, test_remnants, test_s26 and test_s45 read only as
changed-assert lines. *3B:* `layer_reference_s93.json` beyond its role, its digests not re-checked; the frontend tests'
bodies; #113 / #171's LF bright end (0.438 -> 0.948) not pinned and not judged; #211's bound; #119 / #118's source
values (strand 1's); regimes.test.ts for #175; the #218 guard misses alias imports and np.fft and "does not show
bits"; no pytest node run; about 30 records sampled against their comments' arithmetic; re-pins matched to D260-D262's
paragraphs in a sample, not line by line.

## 4. The viewer and the pictures (strand 4; one Opus reader, read-only)

One read-only Opus reader at 766b431 on `s80..main` under `frontend/src` and `interface` (115 files, +9176 / -602, 48
of them `ui/` components): 11 files or groups read in the diff, the rest screened by a grep of added lines;
`tools/goal_metrics.py --table` run one process at a time. **Counts:** Part A 13 rows (11 files / groups, D2, D1) — 9
OK, 3 display, 1 OK with a note; D2 holds (`fetch(` once, `interface/transport.js:71`), D1 by reading; the 2 new
workers compute nothing new beyond JWST's segments-only image. Part B 8 features — 7 traced to a published array and
its model field, 1 display overlay on published edges, 0 untraceable; 12 metric rows, D262's frame numbers reproduced
to the last digit. Part C 22 records hand-edited since s85, jwst_nircam never walked. Findings 5 standing, 1
withdrawn. **The answer:** "Nothing in a committed frame was found untraceable to a published array or a declared
display choice"; none is a wrong model number, none an invention under D5.

| file (session, item) | what the diff adds | verdict |
|---|---|---|
| FluxPoints.tsx (S93 #174) | points' diffuse dust x the gas map, read once at the midplane crossing, from the march's uniforms | OK under D5; D226's approximation |
| FluxPoints.tsx, hstPsf.ts (S82 #178) | a clamped point's light past its 60-px box spread over 8-px blocks | conserves the table's light; F-4-3 |
| hstPsf.ts, psfTableJob.ts, instruments.json (S83 T11) | JWST's pupil: 18 segments, 7 mm gaps, struts at 90 / 240 / 300 deg, 0.039 radii wide | sourced and tagged; F-4-2 |
| psf.ts viewOptics (S83), colors.ts responseColors (S91 T2), regionStars.ts dropRows (S93 T3), ages.js remainderParts (S93 #175) | JWST at the template's distance; colour from `response` over `white.response`; member rows zeroed; remainder by named weights | OK (dropRows only at "sampled") |
| FieldVolume.tsx (S81, S82, S93), tuning.ts | texels in a worker, moving-camera cap, remainder clustered; subMoving, settleMs, regionStars, drawnTuning | display; a still frame unchanged |
| meshTexelsJob, psfTableJob and their workers | the same functions imported, not copied | nothing new but JWST's segments-only image |
| RegionVolume.tsx, contextLoss.ts; comparison, ComparePane, compare, cameraLink (S83 T16) | re-march on a restored context; a second pane | OK; D1 per pane holds by reading |

| feature (range) | frames | model field behind it | provenance |
|---|---|---|---|
| cluster points through the filter set (S91 T2 #114); young population once (S93 T3 #115) | stars, zoom; field knots | `_object_response_header`; `systems.py:811`, `bright.py:316, 558` | derived; dropRows in no frame |
| points' dust x gas map (S93 #174); the clouds' layer | every frame with points | `api/v6_clouds.py`, v7_layer gas_fluctuation | derived + seeded |
| spurs' heights (S92 #164 / #165); diffuse share continuous in R | field frames | v7_layer spurs; `api/v6_clouds.py`, service.py | model side; derived (session not traced) |
| remainder's kept windows (S93 #175) | stars frames | `api/service.py:357-361, 2399` | derived |
| polar cell grid | stars, ngc_4414-zoom | `systems.cell_edges` | published edges; display overlay |
| JWST optics, the wings (#178), T14's cap | none confirmed | - | zoom stands' wings not checked |

| image | Δ(B-R) | A1 | A2 | A3 | arm/interarm | dark frac | PS slope | points in / out |
|---|---|---|---|---|---|---|---|---|
| **GOAL milky_way** | -0.354 | 0.0515 | 0.1943 | 0.0594 | 1.829 | 0.0066 | -1.99 | 518 / 139 |
| milky_way-field | -0.322 | 0.0564 | 0.0531 | 0.0528 | 1.604 | 0.0315 | -1.26 | 708 / 3072 |
| milky_way-physics-only | -0.337 | 0.0055 | 0.0041 | 0.0044 | 1.042 | 0.0213 | -1.28 | 546 / 873 |
| milky_way-stars | -0.304 | 0.0418 | 0.0916 | 0.0555 | 1.968 | 0.1342 | -3.59 | 177 / 87 |
| milky_way-zoom | +0.146 | 0.1745 | 0.2282 | 0.1465 | 6.370 | 0.2130 | -0.20 | 162 / 42 |
| milky_way thumbnail | -0.276 | 0.0525 | 0.0551 | 0.0504 | 1.654 | 0.0621 | - | 44 / 383 |
| **GOAL ngc_4414 (q 0.5736)** | -0.329 | 0.1013 | 0.0739 | 0.0556 | 2.669 | 0.1543 | -2.10 | 119 / 294 |
| GOAL ngc_4414 (q 0.512) | -0.274 | 0.0993 | 0.0683 | 0.0550 | 2.720 | 0.1572 | -2.09 | 97 / 311 |
| ngc_4414-field | +0.185 | 0.0911 | 0.1848 | 0.0423 | 2.568 | 0.0309 | -2.12 | 241 / 2215 |
| ngc_4414-stars | -0.272 | 0.0619 | 0.0886 | 0.0517 | 2.014 | 0.0172 | -3.59 | 104 / 128 |
| ngc_4414-zoom | +0.114 | 0.2303 | 0.1538 | 0.1462 | 8.160 | 0.1449 | -3.69 | 74 / 65 |
| ngc_4414 thumbnail | +0.132 | 0.0674 | 0.2076 | 0.0345 | 2.461 | 0.0523 | - | 30 / 258 |

Milky Way frames at q 1, NGC 4414's at q 0.5736 (D227's convention); the zoom frames are 0.5 kpc views with no
counterpart in either goal. Nearest: milky_way-field's colour step and A1, ngc_4414-field's slope and A1. Farthest:
milky_way-field's A2 (a quarter) and dark fraction (4.8 times); ngc_4414-field's dark fraction (a fifth), A2 (2.5
times) and colour step of the opposite sign. One sentence per frame, the reader's: *milky_way-field*, a small tan disc
with a burnt-out white core and broad faint tightly wound arms, where the goal is a large blue-white disc with a long
yellow bar, distinct arms on thin dark lanes and pink HII knots, and about twenty large dots outside the disc;
*milky_way-physics-only*, a smooth round tan glow peppered with dark spots and no arms; *milky_way-stars*, evenly
spread blue-white blobs under a polar cell grid, no spiral, bar or lanes; *milky_way-zoom*, overlapping white and amber
discs on a beige wash, a star field at a scale no goal shows; *ngc_4414-field*, an overexposed bulge glow over a faint
swirled tan disc, where the goal is a bright flocculent disc threaded by a dense brown lane network, bluer outward
(the frame gets redder outward); *ngc_4414-stars*, blue-white blobs in an inclined ellipse under the cell grid, no
spiral and no lanes; *ngc_4414-zoom*, stars on a beige wash with faint streaks and two grid lines, no goal counterpart;
the two thumbnails measured, not looked at.

- **F-4-1** weak test / owed walk — `tests/fixtures/s72_viewer_requests.json`, `tests/test_bundle.py:378-385`: 22
  records "respelled by hand", jwst_nircam held to wfc3's by substitution ("one is owed"). Settle: "A walk of the built
  viewer on main, including jwst_nircam, logs the same distinct meanings as the fixture, the 22 respelled records
  string for string." See F-3B-7.
- **F-4-2** ADOPTED-NOT-MEASURED (display of the instrument); low — `instruments.json:3080`: struts "[inferred from the
  eight spikes of JWST's images ...]", width "[derived ...]". Settle: "A drawing of JWST's secondary support (e.g.
  JDox's OTE page) gives the struts' directions in the V2/V3 frame and their width; the inferred values agree or are
  replaced."
- **F-4-3** display; low — `hstPsf.ts` WING_BLOCK = 8 decides where 4-6 % of a close point's red light lands. Settle:
  "The lead labels WING_BLOCK display or sampling bound, and VIEWER_TASKS / the Tuning text says it is not offered as a
  slider and why."
- **F-4-4** withdrawn — D1 under a landing's hold: `useLoad.ts`'s swap holds every new answer (read, not run).
- **F-4-5** stale text / method — D262's NGC 4414 goal brackets are the goal at the estimated q 0.512 beside frames at
  q 0.5736 (A2 8 %, the rest under 3 %). Settle: "The goal row and the frame rows are read at one stated axis ratio,
  and D262's brackets are re-quoted at it."
- **F-4-6** display, unreported in D262 — ngc_4414-field Δ(B-R) +0.185 (redder outward) against the goal's -0.329;
  D227 had +0.187 (S67) / +0.177 (S70); never a target (C6). Settle: "The owner's look names whether the outward
  reddening of ngc_4414-field is the model's light or the capture's exposure/bulge glow, and D263 records the sign
  beside D227's."

**Not read / not reached.** App.tsx, api.ts, GalaxyView.tsx, useLoad.ts beyond lines 1-60, fieldLoads.ts,
cameraLink.ts, contextLoss.ts, drawerLayout.ts, Workflow.tsx, PictureBeside.tsx and the 48 ui/ components screened by
grep only; GalaxyTab.tsx read at 410-440 and 712-731; RENDER_PHYSICS.md and VIEWER_TASKS.md not opened; no vitest,
Playwright or worker test; the zoom stands' wings; the diffuse share's session; the walk (its S73 walker not committed).

## 5. The register pass and what "done" still wants (strand 5; one Opus reader, read-only)

One read-only Opus reader at 766b431 with scratch parsers on progress.py's rule (`s94_5_parse.py`, `s94_5_stale.py`,
`s94_5_rulings.py`); no test run, no source fetched. **The counts agree in six places:** `tools/progress.py --check`,
`tests/test_audit.py:395`'s pin `(108, 97)`, its map rows (43 / 65), BRIEF.md:12-13, RESUMING.md:104 and D262's
closing count all read 108 open = 43 permanent + 65 carried, 97 discharged, next #223 / D263, as the parser does;
every open item in one map row, no duplicates, #223 and D263 unused (at s85: 126 open = 33 + 93, 68 discharged).
**29 discharges** of the range examined (21 carried -> struck, 8 new -> struck), each saying what met it, every named
file, test or function grepped existing; **43 permanent**, each with its reason. Of the 108: stands 95 (2 with stale
wording), stale 10, discharged in fact 1, permanent without reason 0, mis-ruled 0 found. Eleven findings, bookkeeping
and wording; no wrong number found.

| # | what | stated status | verdict |
|---|---|---|---|
| 26, 33 | permanent, frozen history | "The advanced model's ..." | stands, stale text (F-5-11) |
| 80 | BAR_LENGTH_RATIO's scale length; rows 15-17 misses | M1; "still carried, with its closer as written" (S88) | stale; cites `S55_REFERENCE_MOVED`, gone since #214 |
| 156 | a chain's excess jumps at a kink | M1; "Carried to S88's look" | stale; the look never recorded |
| 92, 94, 95, 136, 181 | PAH per radius; gas all in clouds; cloud draws; bluer face-on; HII complexes | M2; S89 read, "What would close it" | stale; no destination after S89 |
| 162 | young stars' clustering fades in one step | M2; "no ruling needed once the unit is read" | stale; no session named |
| 159, 163 | lattice cost; normaliser table cost | "the cost pass runs after M3 - at S92's close or Audit VI" | stale; §0's strands hold no cost pass |
| 160 | two old-star placement rules | M2 -> M3; built S91, test_bright.py:470 | discharged in fact (F-5-1) |

**Discharges by ruling.** Owner: #189 ("Yes, all five", D252), #209 (2026-11-03), #210 (2026-11-10), #212 ("Yes,
both"). Gate: #166 (cache built, skip reverted), #214 ("re-based, not retired"), #219 (against its kill clause as
written); #164 / #165 "on the gate's ruling" of an owner-ruled build. Also by the gate: #167 / #168 (D257 (1)), #161 /
#197 / #213 on build, #215 on its kill clause, #216 a gate read, #218 on the gate's re-base; #175's kept=1 the builder's.
The owner's own words in the range: D252, D255 (2026-11-03's four), D256 ("Yes, both"), D259 ("Yes, fix them"), D260
(2026-11-10's twelve, "accept all recommendations"), dd003ee ("Merge if green"); the delegation is dated 2026-11-11.

| # | ruling (gate / lead / builder) | who | entry | in BRIEF? | in D262? |
|---|---|---|---|---|---|
| 1 | four proposals ruled permanent | gate S86 | 141 143 155 157 | n/a | n/a |
| 2 | six declared bounds ruled on the lead's measurements (D255 r. 1-6) | gate S87 | - | n/a | n/a |
| 3 | five readings held; "a spur does not belong where no ridge stands" (D256) | gate S88 | 197, 213 etc | n/a | n/a |
| 4 | #167, #168 discharged; #169 carried for the owner's look (D257) | gate S89 | 167 168 169 | n/a | n/a |
| 5 | #214 re-based, not retired (D258) | gate S90 | 214 | n/a | n/a |
| 6 | the marks: cherry-pick, #217's mark lifted (D261 (1)) | gate S92 | 216 217 | no | no |
| 7 | **#219 discharged on the gate's ruling, against its kill clause as written** (D261 (b)) | gate S92 | 219 | **no** | **no** |
| 8 | #218's remedy = #216's ruling carried to its second cause | gate S92 / lane S93 | 218 | yes | yes (1) |
| 9 | #164 / #165 discharged on the ruled build; #220, #221 opened (D261 (4)) | gate S92 | 164 165 | n/a | no |
| 10 | C1-C3 mends (#221's over-clauses split; a docstring; peak identity) | gate S92 | 221 | no | no |
| 11 | #166 discharged by the gate's ruling | gate S93 | 166 | yes | yes (2) |
| 12 | `kept=1` opt-in; #222 for the WFC3 size clause | builder S93 | 175 222 | yes | yes (3) |
| 13 | #115 membership by class | builder S93 | 115 | yes | yes (4) |
| 14 | #118 (a) the +0.2 dex edge the grid's limit (builder); (b) met on Sanders 2016 (gate) | builder + gate | 118 | yes | yes (5) |
| 15 | #117 carried on #124's ruling; #124 a build item; #117's blind window -0.043 +- 0.008 | gate S93 | 117 124 | yes | yes (6) |
| 16 | s83-robust merged, keeping S84's dot | gate S93 | T11 T13 | yes | yes (7) |
| 17 | #184 a source ruling needed (Robin et al. 2003 proposed), not taken | gate S93 | 184 | "Carried past M3" only | yes (8) |
| 18 | fixture respelled by hand; jwst_nircam's 17 requests held to wfc3's | gate S93 | T11 | yes | yes (9) |
| 19 | the three-legs record re-pinned as read, not re-run | gate S93 | - | yes | yes (10) |
| 20 | the layer-off reference re-based, #218 discharged on it | gate S93 | 218 | **no** | yes (11) |
| 21 | **"the guard in place of a subprocess pair at two thread counts; the solve and the einsums left unordered and named"** | gate S93 | 218 | **no** | **no** |

**Still owed by the owner (4c):** the look at S93's frames (f9b04ed2; "none materially nearer", BRIEF:38); #107, #179
(downloads), #203 (T20), #204 (Azure), #205 (ruling 9 says zero), T19; re-ruling any of rows 7-21; #169's look at the
streaks (only in its entry; F-5-6). #110's "standing" in D258 is stale and harmless; Audit VI's start is answered.
**Viewer rows not struck (5a):** T2 stale (built S91, #114 struck; F-5-3); T3 in part; T7 in part; T8 a stale
"waiting on" (the reading is done, the `region.ts` rewrite waits); T11 merged at S93, its head sentence contradicted by
its tail; T12 stale (built S53, pre-range); T15 not started; T19, T20 the owner's.

**BUILD_V §7, clause by clause (5b).** (1) "Every register item discharged or permanent with its reason": not met, 65
carried - 5 the owner's word, 6 the viewer's plus three viewer halves, 1 Audit VI's (#173), 26 "carried past M3", 15
M1 leftovers (11 on "the owner's reading", #80 and #156 stale, #154 / #186 viewer), 11 M2 leftovers and #160; no BUILD_V
row after 93 takes the carried-past-M3, M1 or M2 leftovers. (2) "the viewer task list empty but for the owner's own
rows": not met, T3, T7, T8, T11, T15 open (T2, T12 on paper only). (3) "the frames at their closest ... with the
distance stated": "none materially nearer"; no stated distance read; the look owed. (4) the hash "green in CI at the
final hash": holds - image run 42976759684 on main at dd003ee prints `model.hash f9b04ed20a06c0a68420f1cc8e13714e`;
not deployed (#204). (5) "three nightly runs green on the three batch merges": M1's head (1c58051) five nightlies
11-04..11-08 all failure; M2's (4f06cc9) 11-10 00:28 and 22:00 success; M3's (dd003ee) none listed yet. Dispatched:
batch-m3 at e2e571f (42952574634) and main at dd003ee (42976759706) success.

- **F-5-1** mis-ruled debt / stale text; high — #160 discharged in fact (995a007, `tests/test_bright.py:470`), still
  carried, no decision says why; striking it gives 107 / 64 / 98. Settle: "the gate strikes #160 on 995a007 +
  test_bright.py:470 with a decision, or writes which clause of the closer is still unmet." See F-3B-8.
- **F-5-2** hidden red / mis-ruled debt; high — `BRIGHT_GATE_READ_OVER` (test_clustering_gate.py:145, :348) named only
  inside struck #161; #215 struck; #162 does not mention it; D261's "every xfail strict with a register entry" not true
  of it. Settle: "an open entry (#162, or a new #223) named in the reason string and carrying the hold in its text, or
  the gate rules the clause." See F-3A-5.
- **F-5-3** stale text; high — VIEWER_TASKS.md:52 T2 open, built and struck at S91; BRIEF:35 omits it. Settle: "T2
  struck, 'Done at S91 (D260)'."
- **F-5-4** ruling taken, not listed; high — D261: "#219's discharge rests on the gate's ruling, not on the entry's
  kill clause as written"; in neither BRIEF.md:21-29 nor D262's eleven; the "S93 re-reads" its struck text promises
  is not in D262. Settle: "#219 added to BRIEF's list; S93's read recorded (the runner's node, or a named-node read)."
- **F-5-5** stale text; high — (a) D262 item 11 not among BRIEF's eight; (b) DECISIONS.md:17341-17342's guard ruling
  in neither list. Settle: "both added to BRIEF's 'Rulings taken on recommendation' (and (b) to D262's list)."
- **F-5-6** stale text; medium — #169's and #202's looks, put to the owner in D258, not ruled in D260 nor named in
  BRIEF:38; #156 and #157 hang on a look never recorded. Settle: "BRIEF's owed list names #156 / #157 / #169 / #202 and
  what to look for."
- **F-5-7** stale; high on the text — ten carried entries (#80, #156; #92, #94, #95, #136, #181, #162, #159, #163) name
  no destination after their batch. Settle: "each entry given a destination (a row, the viewer's pass, the owner's),
  or BUILD_V gains the row."
- **F-5-8** owner-facing gap; medium — #81, #129-#131, #138, #144-#147, #149, #153 wait on "the owner's reading"; BRIEF
  lists only #107, #179, #203-#205 and T19. Settle: "BRIEF lists them, or the entries go to a reading session."
- **F-5-9** stale text; high — BUILD_V.md:55 "The owner's word (7)" includes #210 and #211, both discharged; #167 /
  #168's bodies still end "Proposed **discharged**". No settling sentence in the note.
- **F-5-10** plan; high — §7's "done" not reachable on the plan as written (65 carried, no row after 93; five viewer
  rows open; M1's nightlies red, M3's unread). Settle: "the owner's word on what follows Audit VI (a next build, or §7
  restated)."
- **F-5-11** stale text; low, pre-range — permanent #26 and #33 name `tests/test_models.py`, `bench2.py`,
  `galaxy/models/advanced.py`, none existing, and "The advanced model's". No settling sentence in the note.

**Not read / not reached.** Each open entry read by its title and last 420 characters, not every middle paragraph
("mis-ruled 0" means none found that way); #80's closer not re-read in full; the code behind #142 and #148, #119's
and #211's test names, #189's test_viewer pin and #212's derivation test not grepped; struck viewer rows not re-checked
beyond the greps; the frames' stated distance not looked for beyond "none materially nearer"; why no scheduled run is
listed after 2026-11-10 22:00 not investigated; no test run, no source fetched.
