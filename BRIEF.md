# BRIEF — Session 10, continued: the close

S10 is **split** (board row ◐, rule C2d) and **not merged**. Both audit runs are
done on `session-10-beta` and their defect lists are diffed in DECISIONS.md
(D105). Open per RESUMING.md, read RULES.md in full — B3, B5, B10 and B12 are the
ones this session lives on — then this. GALAXY_INPUTS.md §11 is the register: 28
open, 7 discharged.

## What the two runs did

**Run 1 — the model and its cost.** `convergence.py` sweeps N_R, N_t and N_z one
knob at a time with a too-coarse control on each; `performance.py` profiles every
stage cold in a fresh process and answers D61. Debts #29–#32; #12 re-measured and
given a second explanation for row 3; #17 given a mechanism; #16, #24, #26, #27
updated. Decisions D94–D101.

**Run 2 — the instruments.** Debts #33–#35: a statistical row tests overlap and
not agreement and `ENSEMBLE_MIN = 20` is too small for the 95% it quotes;
`world_seed` is read by no stage and the ensemble samples a diagonal; the
determinism check compares two runs in one interpreter. Decisions D102–D105.

**No physics changed in either run.** The spec report reads exactly as it did at
S9 close, which is the correct outcome for an audit.

## What is owed

1. **Decide what to do with the other branch.** `session-10` on the remote is a
   separate audit run neither of these two read. It is unmerged. Whoever closes
   S10 decides whether it merges, is superseded, or is diffed in as a third list
   — and D105 says a third list read by someone who has seen neither of these is
   the only thing that would measure coverage rather than aim.
2. **Then close S10**: tick the board to ☑, merge, add the `s10` row to
   MANUAL_TODO.md. S9's merge SHA is already filled in (`635c3c8ff43d`).

## Traps

- **Do not fix on the way through.** `CONCENTRATION_NORM` stays at 4.1 even
  though correcting it closes row 3 (D95) — rows 2 and 20 are the discriminator
  against debt #18. The statistical criterion stays as it is (D102), and the fact
  that makes changing it cheap is recorded: both live rows would still pass under
  "the median lies in the target".
- **Merging branches that all touch DECISIONS.md, GALAXY_INPUTS.md §11 and
  LESSONS.md will conflict**, and the debt numbers will collide — this branch
  used #29–#35 and another run will have numbered its own from #29 too. Renumber
  deliberately, then `uv run python tools/progress.py`: the board's debt count is
  generated and `tests/test_progress.py` fails if it is stale.
  `tests/test_docs.py` also asserts DECISIONS.md's D-numbers are sequential.
- A **verified tag with no citation** anywhere in a session document fails a
  test, including one written inside backticks while explaining rule B14. The
  check is a plain substring, so do not type the bare form at all.
- The advanced model still has no thick disc (#27): rows 5, 7–11 and 24 read zero
  or `single` and are recorded. At N_t = 8 it reports a valley — a coarse grid
  manufactures the signal, so state the grid beside any qualitative verdict.
- Windows: `uv run python` only; a PowerShell here-string breaks on embedded
  double quotes, so commit with `git commit -F <file>`. Bash commands over ~8 KB
  fail obscurely — use a file tool.
- Do **not** tag (rule C2e). `tests/test_docs.py` only requires a MANUAL_TODO row
  for a ☑ session, so the ◐ row is consistent as it stands.
- After ticking the board run `uv run python tools/progress.py`, then
  `uv run pytest` once, quiet, then `tools/verify_clone.py --ref main`.
