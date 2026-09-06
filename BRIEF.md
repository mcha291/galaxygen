# BRIEF — after S10 run 3: what is owed, and this run's defect list

Open per RESUMING.md. Read RULES.md in full, then this. Do not read GALAXY_PLAN.md.
This run (`session-10-gamma`) was cut from S9's merge `635c3c8` and told to read
nothing after it, so it is **unmerged** and has not seen runs 1 and 2. The board is ◐.

## Owed (MANUAL_TODO.md §2, needs someone who may read all three branches)

- **Diff the defect lists** of `session-10`, `session-10-beta` and this run, and put
  the diff in DECISIONS.md — the board's gate. This run's list is the section below.
- **Decide the merge.** Three runs touched the same files (`galaxy/specs/convergence.py`,
  `performance.py`, `__main__.py`, `spec.py`, GALAXY_INPUTS.md §11, DECISIONS.md,
  tests). Merge one, or merge one and port the others' findings as register entries.
- Fill S10's merge SHA into MANUAL_TODO.md §1 once merged; the tag batch stays queued.

## This run's defect list (D94–D102)

- **Instruments built:** `convergence` (n_R 100/200/800, n_t 500/1000/4000, one at a
  time; every reachable row passes; largest drift row 20 at 7 % of width) and
  `performance` (per-stage cold profile per model in a fresh process; D61 measured:
  276 µs/cell, 41–53 % of it Generator construction). Both under `python -m galaxy.specs`.
- **Discharged:** debt #17 — rows 14, 20, 21 carry the source's printed precision (D95).
- **Measured, recorded, not fixed:** #12 the missing c_vir→c₂₀₀ conversion is worth
  13 km/s on row 3, the other way (D97); #18 `GAS_DISC_SCALE_RATIO` swept — a wider single
  infall trades rows 3/20 against 2/22 (D98); #26 the +1.5 dex centre makes giant
  occurrence 0.43 inside 1 kpc and a 60 % difference in the sample's giant fraction (D100).
- **New debts:** #29 row 2 sits inside `KS_NORM`'s own ±1σ; #30 `NET_YIELD` and
  `WIND_SPEED` are fitted on the row-2/row-20 SFH, levers published; #31 `SECULAR_HEATING`
  is a different fit under the chemical split, row 6 passes by 24 pc (D99).
- **Ratchets:** UNSET defaults 1 → 0. `tests/test_api.py` skips `.claude/` worktrees.
- **Not done:** the runs' diff, the merge, `tools/scaling.py` (no stage changed).

## If an S11 is added — the register's order of attack

1. **Rows 3 and 19 together:** set the overdensity conversion and z_f jointly (#12); on
   its own either fix overshoots row 3. Then the extended component (#18) on top, judged
   with the bulge (rows 12–14, #26's inflow). Re-fit `NET_YIELD`/`WIND_SPEED` after (#30).
2. **The valley** (#27): the register predicts a fast inner disc; the sweep already said
   the accretion history alone will not open it. Row 6 changes with it (#31).
3. **Migration** (#28): a gradient measured at 10 Gyr decides 3.6 kpc against 2.5.

## Traps

- Misses and drifts are per model (`spec.misses`, `convergence.recorded`); a recorded
  entry that starts passing fails the run — remove it with a DECISIONS entry.
- `performance.py` spawns one interpreter per model via `sys.executable -m`; under
  `uv run` that is the venv's python. `python -m galaxy.specs` now takes ~10 s longer.
- To vary a constant, build a probe `Model` (`tests/test_calibration.py::with_constants`);
  never edit `level0.py` to measure.
- `tests/test_progress.py` fails if the board is edited without `tools/progress.py`.
- Windows: `uv run python` only; Bash commands over ~8 KB fail obscurely; `node --test`
  needs `--test-reporter=tap`. Do **not** tag (rule C2e).
