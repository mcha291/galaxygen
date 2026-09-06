# BRIEF — Session 10, closing: diff the two runs and merge

Open per RESUMING.md. Read RULES.md in full, then this. The board said **Fable, run
twice** — two independent audits, then diff the defect lists. This branch
(`session-10-gamme-run-2`) is run 2: it started at the S9 merge and read nothing of
run 1 (`session-10-gamma`), by instruction. Its close is **partial** (◐, rule C2d):
everything below "What run 2 delivered" is done, committed and pushed; what remains
needs both runs in one place.

## What run 2 delivered

- `galaxy/specs/convergence.py` and `performance.py`, run by `python -m galaxy.specs`
  beside the four existing specs (exit 0); `Outputs.seconds`; `Quantity.testable`.
- The calibration audit as `tests/test_audit.py`, its findings on the register
  (GALAXY_INPUTS.md §11: #17 discharged, #29–#31 opened, #12/#26/#27/#28 measured)
  and as a numbered defect list in DECISIONS.md D96 — written to be diffed.
- Cold timings (D98), the profile (D95), the sweep (D94); LESSONS.md `[audit]`.

## What remains (the gate's last item, then the close)

1. **Diff the two defect lists.** Run 1's findings are on `session-10-gamma`; run 2's
   are D96's numbered list. Put the diff in DECISIONS.md — what both found, what only
   one found, and where they disagree on a number or a debt. Register anything only
   run 1 found that run 2 missed, and vice versa; never average a disagreement (B12).
2. Reconcile the register: two runs may have opened debts with the same number.
   Renumber run 2's #29–#31 if run 1 used them (they are cited by number in
   `tests/test_audit.py::test_the_register_carries_s10s_findings` and D96).
3. Merge `--no-ff` into `main` with subject `Merge S10 into main: …`, push, add the
   `s10` row to MANUAL_TODO.md (S9's SHA is filled in: `635c3c8ff43d`), tick the
   board ☑ with the date, `uv run python tools/progress.py`, then
   `uv run python tools/verify_clone.py --ref main`.

## Traps

- Run 2's branch name carries a typo (`gamme`); rename before merging if it matters,
  the remote branch is `origin/session-10-gamme-run-2`.
- `python -m galaxy.specs` now takes ~15 s longer: the sweep is ten runs and the
  profile is two fresh interpreters. `tests/test_convergence.py` sweeps once per
  session (module fixture); `tests/test_audit.py` is ~30 model runs.
- Row 20 is `untestable` in the convergence report and still `fail` in the spec
  report, on purpose (D97): the drift has no width to be judged against, the miss
  is real on any reading. Do not make one of them agree with the other.
- The advanced model's thick-disc rows are `vacuous`, not converged: a valley
  opening (debt #27) turns them into rows that can drift, and the sweep will then
  judge them for the first time.
- Debt #12's conversion and debt #18's extended component both lower row 3; applied
  together they overshoot (242.6 before the component). Judge them together.
- Windows: `uv run python` only; a Bash command over ~8 KB fails obscurely — write
  a patch script to a file and run it. `.claude/` holds other sessions' worktrees.
- Do **not** tag (rule C2e).
