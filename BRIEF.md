# BRIEF — after the build: what a maintainer opens with

The eleven sessions are closed (S0–S10; S10 ran twice and its two defect lists
are diffed in DECISIONS.md D97). Nothing is scheduled. Open per RESUMING.md,
read RULES.md in full, then this. Do not read GALAXY_PLAN.md for anything but
the status board; GALAXY_INPUTS.md §11 is the register and the only list of
what is wrong. Work on a branch `session-11` or a topic branch; the close
ritual in RESUMING.md still applies, and rule C2e still queues tags.

## What is owed first — one-line fixes, each with a test (D97)

- `galaxy/stages/vertical.py::scale_height` hard-codes G; read the constant and
  add `G` to both vertical stages' `reads_constants` (AUDIT_RUN2.md D-9).
- `tools/scaling.py::measure` labels a warm run "whole model, cold"; measure it
  in a subprocess or relabel it (D-13). DECISIONS.md D95's sentence "cold and
  warm agree at every stage" is false for `pattern` (D-12); amend, don't delete.
- The Ia iron-peak factor `2.0` in `chemistry_dtd.py` belongs in the register,
  and the total-Z zero point wants deciding (debt #33).

## The decisions a maintainer must take — physics, not fixes

1. **Sagittarius (debt #29).** The default delivers 5.9 × 10⁹ M☉ from 3.8 Gyr.
   Set its gas fraction near zero *and* rewrite the row-2 miss entries for both
   models in the same commit: row 2 will pass (1.837), and a registered miss that
   passes fails the spec run. Then re-fit nothing — check whether `WIND_SPEED`
   still puts R₀ at solar (it should; the wind is insensitive to the SFR).
2. **The step infall (debt #30).** Feed `merger_delivery` into `sfh` in place of
   the step, or delete `MERGER_DURATION` and the field. The prediction that
   decides it: the N_t non-monotonicity of rows 1 and 10 (AUDIT_RUN2.md C2) goes.
3. **Row 3's three explanations (debt #12, #18, D-4).** Before building the
   extended accretion component, decide the c_vir → c₂₀₀ conversion: K = 3.5
   closes row 3 by itself. Rows 1 and 19 discriminate; build the instrument that
   reads them together before the mechanism.
4. **Rows 1, 10, 11 (debt #11 amended).** A bulge stage takes ~1.5 × 10¹⁰ out of
   the disc and fails row 1 unless the budget or the concentration moves. This
   is the same decision as 3, seen from the mass side.
5. **The catalogue does not migrate (debt #31).** Either the advanced model's
   `systems` draws from the migrated per-age mass, or `feh_spread_sun` says it
   describes stars the viewer will not show.

## What the instruments will tell you, and what they will not

- `uv run python -m galaxy.specs`: exit 0 means every failing row is a recorded
  miss for its model, and nothing drifted across its target width. It does not
  mean a green row is a prediction — AUDIT_RUN2.md §5 lists what each one
  actually rests on. Never widen a target (B5); record a miss with a prediction.
- The convergence sweep judges against the target width; a wide target hides a
  grid dependence. Add a converged-rate check before trusting a new stage.
- The profile is cold per model; `pattern`'s warm column is the RNG cache.
- Probing a constant: copy `with_constant` from `tests/test_chemistry_dtd.py`;
  `run(model, {...inputs}, only=(fields,))` for an input. A verdict needs a
  number (rule B6); the round-3 probe in AUDIT_RUN2.md §4 is the pattern.

## Traps

- A second audit must seal the register and the lessons, not only the list:
  run 1's amendments carried five findings into run 2 (D97).
- Windows: `uv run python` only; Bash commands over ~8 KB fail obscurely — write
  long files with a file tool. In a worktree set `core.hooksPath` per worktree.
- `tools/progress.py` counts debts by numbered item: add an item, never a count.
