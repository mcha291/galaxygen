# BRIEF — Session 10, run 2: the second audit

Open per RESUMING.md, **on the open branch `session-10`** (rule C2d: run 1 closed
partially, nothing is merged). Read RULES.md in full — **B2, B6, B7, B10, B3** —
then this. Do not read GALAXY_PLAN.md. Read GALAXY_INPUTS.md **§10** and **§11**.

**Do not open `AUDIT_RUN1.md`, or DECISIONS.md D96, until your own list is
written.** The point of two runs is two independent defect lists; the diff is the
deliverable (D96). Everything else run 1 left — the instruments, D94, D95, the
lessons — is yours to use.

## Build

- Run the instruments and read them yourself: `uv run python -m galaxy.specs`
  (convergence at full size, the cold profile), `tools/timings.py`,
  `tools/scaling.py`. Rule B3: a check that takes run 1's path is a check on run 1.
- **The calibration audit** (rule B10), independently: every constant in
  `models/level0.py`, `simple.py`, `advanced.py` and every input default in
  `core/registry.py` — what was it fitted or chosen against, has that mechanism
  changed since, what does it hold up now? Read the `about` lines and the register;
  probe where a verdict needs a number.
- Write **`AUDIT_RUN2.md`** in the same shape as a defect list with a "not found"
  section, add it to `tests/test_docs.py::SESSION_DOCS`, **then** open
  `AUDIT_RUN1.md` and write the diff into DECISIONS.md (D97): what both found,
  what only one found, and why the other missed it.
- Register anything new as a debt (§11; `tools/progress.py` counts it) or
  discharge it; lower a ratchet where a debt is gone.

## Gate

- `python -m galaxy.specs` exit 0, both models, every miss recorded for its model.
- `AUDIT_RUN2.md` exists and was finished before `AUDIT_RUN1.md` was read; the
  diff is in DECISIONS.md.
- The board row goes ☑ (run 2 closes S10): merge `session-10` into `main` with
  subject `Merge S10 into main: …`, queue `s10` in MANUAL_TODO.md and fill in S9's
  merge SHA from `git rev-list -1 --grep='^Merge S9 into main' origin/main`.

## Traps

- Row 20's target is zero-width (debt #17): the sweep reports it *untestable*
  and the table still fails it; do not widen it (rule B5).
- The advanced model has no thick disc (debt #27) and its rows 5, 7–11, 24 are
  recorded; a sweep sees them converged at zero. Do not tune the valley open.
- Statistical rows (16, 17) are seeded draws; the sweep reports them without a
  verdict. Judge them by their ensembles, not by one seed.
- Kahn's rounds pin per-model orders in `tests/test_graph.py::ORDER`.
- Windows: `uv run python` only; Bash commands over ~8 KB fail obscurely — use a
  file tool; `$TMP` is the system temp, not the scratchpad.
- After ticking the board run `uv run python tools/progress.py`; then the suite
  once, quiet; then `tools/verify_clone.py --ref main` after the merge.
