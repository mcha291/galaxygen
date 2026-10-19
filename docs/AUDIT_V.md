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
