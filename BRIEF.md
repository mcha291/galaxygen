# BRIEF — Session 10, continued: the diff and the close

S10 is **split** (board row ◐, rule C2d). The board asked for two independent
audits and a diff of their defect lists; this is the second run, on
`session-10-beta`, made without reading the first. **Neither run is merged.**
Open per RESUMING.md, read RULES.md in full — B5, B6, B10 and B12 are the ones
this session lives on — then this. GALAXY_INPUTS.md §11 is the register: 25
open, 7 discharged.

## What this run did

Two new specs, both wired into `python -m galaxy.specs` (exit 0, ~15 s):
`convergence.py` sweeps N_R, N_t and N_z **one knob at a time** with a
too-coarse control on each; `performance.py` profiles every stage cold in a
fresh process and answers D61. The calibration audit (B10) re-measured debts
#12, #16, #17, #24, #26, #27 and added #29–#32. **No physics changed** — the
spec report reads exactly as it did at S9 close, which is the correct outcome
for an audit. Decisions D94–D101.

## What is owed

1. **The diff of the two runs' defect lists**, in DECISIONS.md. It is the one
   gate neither run could meet alone. Both branches are on the remote:
   `session-10` and `session-10-beta`. Compare what each *found*, not what each
   wrote — a defect one run recorded as a debt and the other as a test is the
   same defect, and a defect only one run found is the interesting row.
2. **Then close S10 properly**: tick the board to ☑ with both runs' models,
   merge both branches to `main`, and add the `s10` row to MANUAL_TODO.md.
   S9's merge SHA is already filled in (`635c3c8ff43d`).

## Traps

- **Do not fix the physics on the way through.** `CONCENTRATION_NORM` stays at
  4.1 even though correcting it closes row 3 (D95); the fix is cheap and the
  reason to hold it is that it is a candidate answer to an open question. Rows
  2 and 20 are the discriminator against debt #18 — whoever closes row 3 checks
  them.
- **Merging two branches that both touch DECISIONS.md, GALAXY_INPUTS.md §11 and
  LESSONS.md will conflict**, and the debt numbers will collide: this run added
  #29–#32 and the other will have numbered its own findings from 29 too.
  Renumber deliberately, then `uv run python tools/progress.py` — the board's
  debt count is generated, and `tests/test_progress.py` fails if it is stale.
  `tests/test_docs.py` asserts DECISIONS.md's D-numbers are sequential with no
  gaps, so the same is true of them.
- A **verified tag with no citation** anywhere in a session document fails a
  test — including one written inside backticks while explaining rule B14. The
  check is a plain substring, so do not type the bare form at all.
- The advanced model still has no thick disc (debt #27): rows 5, 7–11 and 24
  read zero or `single` and are recorded. At N_t = 8 it reports a valley — a
  coarse grid manufactures the signal, so state the grid beside any verdict.
- Windows: `uv run python` only; a PowerShell here-string breaks on embedded
  double quotes, so commit with `git commit -F <file>`. Bash commands over
  ~8 KB fail obscurely — use a file tool.
- Do **not** tag (rule C2e). `tests/test_docs.py` only requires a MANUAL_TODO
  row for a ☑ session, so the ◐ row is consistent as it stands.
- After ticking the board run `uv run python tools/progress.py`, then
  `uv run pytest` once, quiet, then `tools/verify_clone.py --ref main`.
