# BRIEF — for S21: Audit II, run twice with two stated aims (§5d; one on Fable, one on Opus)

S0–S10 are closed; S11–S20 integrated, fixed and decided (D99–D129). S20 changed one constant
(`MERGER_HEATING` 120 → 88.8, derived) and one function boundary (`sfh.first_infall`), and wrote
the valley's record. Open per RESUMING.md, read RULES.md, then this; §11 is the register (32
open, 18 discharged). Two branches, `session-21-a` and `session-21-b`, **never merged into each
other** — S22 ports both lists onto main (D99). Your decisions are **D130** onward.

## Reserved numbers, fixed now (§5d row 21; D116 wrote them before S15 took D117)
- Aim (a): debts **#51–#64**, decisions **D130–D143**. Aim (b): debts **#65–#78**, decisions
  **D144–D157**. Open your first number at the start of your range whatever the other run did.
- Give each run its aim in its first line and its model in the board row (the S10 comparison is
  worthless if the model used is recorded from intention, GALAXY_PLAN.md §5).

## Aim (a): every prediction since S13, killed or held with a number (rule B4)
- The predictions live in `spec._MISSES` / `_MISSES_ADVANCED` (every entry has one) and in §11's
  entries from S13 on. Run each one that can be run with the repo unchanged; S20 left the
  substitution point for the infall law (`sfh.first_infall`, monkeypatched in
  `tests/test_audit.py`'s three S20 tests) and `with_constant` for the rest.
- Not yet read by anyone: **#50** (S19: the model transports stars twice, kick in `sfh` and churn
  in `chemistry`; its prediction is that moving the stars through both lands row 9 between 0.0455
  and 0.221) — S19 wrote it for you to *read* and S22 to rule. The bar's prediction (D121: 7e9
  buckled into the spheroid reads row 3 at 249.4, row 12 inside, row 14 at 123) has never run.
- S20's own claims to test: every `bimodal_wide` the detector reports is the plateau spike (D128,
  a test pins one case — try the single-merger ones); the valley needs a *rising* first phase cut
  within a gigayear (nothing in the repo can make one, so this is a claim to attack, not confirm).

## Aim (b): the instruments and the viewer
- Cold paths (D4): every route in `tools/timings.py`, the metadata routes touching no stage.
- `tests/test_performance.py::test_the_catalogue_is_priced_per_cell` is flaky under load (D115).
- The audit tests' pins: `tests/test_audit.py` carries S10–S20's measurements at loose tolerances;
  ask which ones would not notice a regression of the size that matters (S19's lesson: state the
  precision you checked at). The `bimodality` detector's `MODE_MIN_SHARE` = 0.1 within ±0.05 dex
  cannot see a thick mode holding 12% of the mass unless it is under 0.1 dex wide (D128) — an
  instrument finding for you to state, not a threshold for you to move (rule B5).
- The viewer previews every published field in both models (S19); check the two S20 numbers
  reach it (`disc_radial_spread` 1.09 at R₀; the thick disc's σ_z 35.0).

## Traps
- **Write files with `newline="\n"`**; the full suite outlasts the Bash tool's cap — background
  it with `EXIT=$?` appended to its log and gate the merge on **that line**. Scratch scripts
  `s21_<what>.py`, deleted before the close asserts `git ls-files --others` is empty.
- Row 3 reads 251.03, out by 0.03, on the miss list under #11 since S20; row 7 (simple) passes at
  962 since S20. The advanced model reads 8 / 15 / 1. A recorded miss that starts passing fails
  the run (#29): remove the entry and write why.
- The `judged` fixture runs both models' 41-seed ensembles once per session; `tests/test_spec.py`
  pins the pass/fail sets and the debt sets per model.
- **Do not merge or delete `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`.**
