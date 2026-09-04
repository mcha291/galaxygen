# BRIEF — Session 10: the audit

Open per RESUMING.md. Read RULES.md in full — **B2, B6, B7, B10 and A10 are the
ones this session lives on** — then this. Do not read GALAXY_PLAN.md. Read
GALAXY_INPUTS.md **§10** (the measured cost model) and **§11** (rulings and the
whole debt register: 21 open, 7 discharged — this session's raw material).

The board says **Fable, run twice** — two independent audits, then diff the
defect lists. Each run is its own session branch; the second must not read the
first's findings before making its own.

## Build

- **`galaxy/specs/convergence.py`**: sweep N_R and N_t **independently** (never
  one knob) for every acceptance scalar in both models, publish the drift of each
  against the default grid, and fail a row whose drift exceeds its target's width.
  `tests/test_sfh.py::test_scalars_do_not_move_with_grid_resolution` and
  `test_chemistry.py::test_the_gradient_converges` are the seeds of it.
- **`galaxy/specs/performance.py`**: the profile per stage, both models, cold in a
  fresh process (`tools/timings.py` and `tools/scaling.py` are the pattern), and
  the per-cell catalogue cost D61 left open. Publish the numbers, not verdicts.
- **The calibration audit** (rule B10): every constant fitted while a mechanism was
  missing, re-examined now that the advanced model has the mechanism. The list is
  §11; start with #12 (c₂₀₀–z), #17 (zero-width targets: read the sources'
  uncertainties or give the table "no testable target"), #26–#28 (S9's).
- Register findings as debts or discharge them; lower the ratchets in
  `tests/test_registry.py` where a debt is gone. Do not fix physics — record.

## Gate

- Every acceptance row's drift across the sweep is published for both models, and
  the sweep runs N_R and N_t separately (GALAXY_INPUTS.md §10: exponent 0.13 in
  N_R against ~1 in N_t — they are not one knob).
- `python -m galaxy.specs` runs convergence and performance beside the four
  existing specs; exit 0 with every miss recorded for its model.
- The two audit runs' defect lists are diffed and the diff is in DECISIONS.md.
- Cold timings published (B2); `tools/scaling.py` re-run if any stage changed.

## Traps

- **The advanced model has no thick disc** (debt #27): rows 5, 7–11 and 24 read
  zero or `single` and are recorded. Do not tune the valley into existence; the
  register's prediction names what to try (a fast inner disc) if you must.
- Misses are per model (`spec.misses(name)`, D87): a row can be stale for one
  model and recorded for the other, and the runner judges each against its own.
- The advanced model's centre reaches [Fe/H] = +1.5 (debt #26) — a convergence
  sweep will see the inner rings move; that is the massless wind, not the grid.
- `tests/test_graph.py::ORDER` pins each model's execution order; Kahn's rounds
  move stages you did not touch when a dependency changes.
- Windows: `uv run python` only; Bash commands over ~8 KB fail obscurely — use a
  file tool. `node --test` needs `--test-reporter=tap` named.
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill in
  S9's merge SHA from `git rev-list -1 --grep='^Merge S9 into main' origin/main`.
- After ticking the board run `uv run python tools/progress.py`.
