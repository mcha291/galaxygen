# BRIEF — after the build: what a maintainer opens with

S0–S10 are closed; S11 integrated the three S10 audits onto `main` without merging
their branches (debts #34–#45, their tests, three instrument features, the four lists'
comparison in D102); S12 made the one-line fixes (D104). Both 2026-09-07.
Open per RESUMING.md, read RULES.md in full, then this. GALAXY_INPUTS.md §11 is the
register and the only list of what is wrong (35 open). Work on a branch
`session-13` or a topic branch; the close ritual still applies; rule C2e queues tags.

## What is owed first

Nothing small. S12 made the one-line fixes (DECISIONS.md D104): G read from the
registry, the two tool labels, the midplane escape velocity, the cross-process
determinism check, the Ia factor registered. What remains is physics, below.

## The decisions a maintainer must take — physics, not fixes

1. **Sagittarius (#29).** Set its gas near zero *and* rewrite both models' row-2 miss
   entries in the same commit; a registered miss that passes fails the spec run.
2. **The step infall (#30).** Feed `merger_delivery` into `sfh` or delete the constant;
   the N_t non-monotonicity of rows 1 and 10 is the prediction that decides it.
3. **Row 3's explanations (#12, #18).** Three audits give the c_vir → c₂₀₀ conversion
   three values (242.6 / 246.9 / 248.0 km/s on row 3) and three discriminators (rows 1
   and 19; 2 and 20; 3 and 19 with z_f). Decide the conversion *and* the epoch together,
   with all of rows 1, 2, 19, 20 read, before building the extended component (D102).
4. **Row 20's target is hydrogen (#41).** Add a helium fraction or read a hydrogen
   field, then re-judge row 20 (a 47% miss) and what #18's component must supply.
5. **Rows 1, 10, 11 (#11).** A bulge stage takes ~1.5 × 10¹⁰ out of the disc and fails
   row 1 unless the budget or the concentration moves — decision 3 from the mass side.
6. **The catalogue does not migrate (#31)**, and the advanced model's row 6 rides on
   `MERGER_HEATING` (#42): judge rows 6 and 7 together when the valley (#27) opens.
7. **The statistical criterion (#38).** "Median inside the target" costs no verdict
   today and `ENSEMBLE_MIN` needs 41 for a real 95%; decide before rows 13, 14, 18 land.

## What the instruments will tell you, and what they will not

- `uv run python -m galaxy.specs`: exit 0 means every failing row is a recorded miss,
  nothing drifted across its width, and every stage was profiled. `vacuous` rows have
  nothing to converge (debt #27); "no testable target" rows have no width (#17, D100).
  Never widen a target (B5); record a miss with a prediction. No green row is an
  unconditioned prediction (AUDIT_RUN2.md §5) and no row reads inside 4 kpc (#34).
- Probing a constant: `tests/test_audit.py::with_constant`; `run(model, {...inputs},
  only=(fields,))` for an input. A verdict needs a number (rule B6).

## Traps

- **Do not merge or delete `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`**:
  they are the sealed lists D102 compares (D99). Their debt and decision numbers are
  their own; main's map is in D99.
- An audit's aim decides what it finds (D102): a repeat with the same brief finds the
  same third. Give a second run a stated aim — and reserved debt/decision numbers.
- Windows: `uv run python` only; Bash commands over ~8 KB fail obscurely; in a worktree
  set `core.hooksPath` per worktree. `tools/progress.py` counts debts by numbered item.
