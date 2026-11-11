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
  radius MD17's clouds give 57.5 R^2.10); LD20's 78.6 R^1.98 is "for the clouds in the R+16 catalog".
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

## 2. What the batches built, re-measured (strand 2)

*(assembled when the strand's note is in)*
