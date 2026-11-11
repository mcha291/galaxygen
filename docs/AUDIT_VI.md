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
