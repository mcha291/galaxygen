# BRIEF — after the build: what a maintainer opens with

S0–S10 are closed; S11 integrated the three S10 audits onto `main` without merging
their branches (debts #34–#45, their tests, three instrument features, the four lists'
comparison in D102); S12 made the one-line fixes (D104); S13 the physics decisions
(D106–D112). All 2026-09-07.
Open per RESUMING.md, read RULES.md in full, then this. GALAXY_INPUTS.md §11 is the
register and the only list of what is wrong (31 open). Work on a branch
`session-14` or a topic branch; the close ritual still applies; rule C2e queues tags.

## What S13 did, and what is still physics

Done (D106–D110): the merger's gas accretes from its own delivery windows and
Sagittarius delivers a physical share (#29, #30 discharged; row 2 reads 1.89, so the
rest is #18's timescale); the halo converts c_vir to c₂₀₀ (#12 half: row 3 reads 242.7,
**low**, z_f stays 2.5; WIND_SPEED refit 987); row 20 reads hydrogen (#41: 4.17e9, a 48%
miss); a statistical row passes on its median at n = 41 (#38). The bulge was probed and
**lowers row 3 by 5–8 km/s**; it is for rows 10, 12, 13, not for row 3.

## The decisions a maintainer must take next — physics

1. **Row 3 (#6, #11, #12).** Adiabatic contraction of the halo is the lever now; a
   bulge is not. Model contraction with z_f at 2.5 and read rows 3 and 19; if the row
   still misses, z_f 2.7–3.1 is what the table wants and the cited range is wrong low.
2. **The extended component (#18).** Rows 2 (1.89 against 1.84) and 20 (3.8e9 of
   hydrogen short) are its evidence alone now; row 3 is not, and moves the wrong way.
   Rows 3 and 4 are the check that it is high enough in angular momentum.
3. **The bulge stage (#11).** For rows 10, 12, 13 and the cancellation on row 11; row 14
   needs the source's uncertainty first (#17). It must not be built for row 3 (D110).
4. **The catalogue migrates (#31).** A systems-stage change with its own golden values;
   then rows 6 and 7 in the advanced model are judged together when #27's valley opens.
5. **The thick disc (#19).** Rows 5 and 11 fail and row 9 passes at 0.152 on the
   cancellation, worse since S13; radial heating with the vertical kick is the prediction.
6. **Row 6, advanced (#42).** A recorded miss at 358 since S13; SECULAR_HEATING and
   MERGER_HEATING are the simple model's fits. Do not tune it back; wait for the valley.

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
