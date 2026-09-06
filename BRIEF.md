# BRIEF — Session 10, after the diff: the merge is owed, and it is wider than planned

Open per RESUMING.md. Read RULES.md in full, then this. The board said **Fable, run
twice** — two blind audits, then diff the defect lists. This branch
(`session-10-gamme-run-2`) is run 2 of the pair whose run 1 is `session-10-gamma`;
both were cut from the S9 merge `635c3c8` and read nothing after it. **The diff is
done: DECISIONS.md D100.** The close stays partial (◐, rule C2d): the merge needs a
decision only the maintainer can take (below).

## What is on this branch

- `galaxy/specs/convergence.py` and `performance.py` under `python -m galaxy.specs`
  (exit 0); `Outputs.seconds`; `Quantity.testable`; `tests/test_audit.py`.
- The audit: D96's numbered list; register #17 discharged, #29–#31 opened, #12/#26/
  #27/#28 measured. D97 the zero-width remedy, D98 timings, D99 the clock and gate.
- **D100, the diff of the pair.** Both found 5 things and every shared number agrees
  to the printed digit; run 1 only 3, run 2 only 6; one substantive disagreement —
  debt #17's remedy (printed-precision half-units on gamma, `Quantity.testable`
  here) — left unaveraged (B12). Run 1's findings are ported: **#32** (`KS_NORM` ±1σ
  contains row 2), **#33** (`NET_YIELD`/`WIND_SPEED` provisional on #18, levers), and
  #26/#30/#31 amended, each cited to gamma's `tests/test_calibration.py` by branch.
  Register: 25 open, 8 discharged. Both runs were Fable 5.1: the pair measures
  run-to-run variance of one model, not the plan's model comparison.

## What remains — read D100 "Beyond this pair" and MANUAL_TODO.md §2 first

1. **`main` already has an S10.** `ff12928` "Merge S10 into main" came from
   `session-10` (its own two runs, `AUDIT_RUN1.md`/`AUDIT_RUN2.md`, diffed in its
   D97) and carries debts #29–#33 and D94–D98 of its own; `session-10-beta` holds a
   further list (D94–D105, debts #29–#35, **on Opus 5** — the plan's model
   comparison). **D101 sets all four lists side by side**: a core of five, what
   each found alone (15 / 12 / 7), six disagreements (the size of #12's
   conversion, #17's remedy 4 : 1, `MERGER_HEATING` in the advanced model, whether
   #24 is discharged, `KS_NORM`'s filing, row 20's 28% against 47%) and what a
   union register needs. Decide which S10 `main` keeps first; the row stays ◐.
2. If this branch is the one to merge: renumber #29–#33 past `main`'s (cited in
   `tests/test_audit.py::test_the_register_carries_s10s_findings`, D96, D100 and the
   register text), decide debt #17's remedy (D100, disagreement 1) and port the
   loser's numbers as prose, then `git merge --no-ff` with subject `Merge S10 into
   main: …`, push, add the `s10` row to MANUAL_TODO.md (S9's SHA is `635c3c8ff43d`),
   tick the board ☑ with the date, `uv run python tools/progress.py`, then
   `uv run python tools/verify_clone.py --ref main`.
3. If `main`'s S10 stands: port this pair's union onto `main`'s register as new
   numbers (#34 onward) with D100 as the source, and close this branch unmerged.

## Traps

- This branch's name carries a typo (`gamme`); the remote is `origin/session-10-gamme-run-2`.
- Gamma and this branch both edit `galaxy/specs/spec.py`, `convergence.py`,
  `performance.py`, `__main__.py`, GALAXY_INPUTS.md §11, DECISIONS.md and the tests;
  a textual merge of the two will not work — take one and port the other.
- `python -m galaxy.specs` takes ~15 s longer here: ten sweep runs, two fresh
  interpreters. `tests/test_audit.py` is ~30 model runs.
- Row 20 is `untestable` in the convergence report and `fail` in the spec report on
  purpose (D97); gamma's branch gives it a 10⁸ M☉ width instead. Do not blend them.
- The advanced thick-disc rows are `vacuous`, not converged (#27); debts #12 and #18
  both lower row 3 and together overshoot (242.6 before the component). Judge together.
- Windows: `uv run python` only; a Bash command over ~8 KB fails obscurely. `.claude/`
  holds other sessions' worktrees. Do **not** tag (rule C2e).
