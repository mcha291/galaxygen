# BRIEF — after the build: what a maintainer opens with

S0–S10 are closed; S11 integrated the three S10 audits (D99–D103), S12 the one-line
fixes (D104), S13 the physics decisions (D106–D112), S14 the halo's contraction and a
probe of the extended component (D113–D115). All 2026-09-07.
Open per RESUMING.md, read RULES.md in full, then this. GALAXY_INPUTS.md §11 is the
register and the only list of what is wrong (31 open). Work on a branch
`session-15` or a topic branch; the close ritual still applies; rule C2e queues tags.

## What S14 found, and why it changes the next decision

The halo now contracts around the disc (debt #6 discharged; D113): Gnedin et al. 2004's
invariant by default, Blumenthal's as the named alternative, both Level 0 constants
(`CONTRACTION_A`, `CONTRACTION_W`), the disc's scale length computed by the halo stage.
The register had it at "several km/s". **It is 43 km/s on the halo's share at R₀ and 28
on row 3, which reads 270.8 — high by 20 — against 242.7 before.** The epoch row 3 wants
is now **0.7–1.0**, below the cited 2–3, where at S13 it wanted 2.7–3.1 above it. The
advanced model's escape velocity at R₀ rose 562 → 585 (over the observed 530–580) and
`WIND_SPEED` was refitted 987 → 1028 against that potential (debt #43, provisional).
Debt #46 holds the calibration question: every published invariant overshoots.

## The decisions a maintainer must take next — physics

1. **Row 3 (#12, #46, #11, #18).** Three levers, none free: the assembly epoch (0.7–1.0
   closes it alone; the cited range is 2–3), the contraction's calibration (A = 1.6 at
   w = 0.8 reads 256.8, still out; Gnedin et al. 2011's mass- and epoch-dependent form is
   not adopted), and a less compact baryon distribution (the bulge is worth 5–8 the right
   way now, D110; the component below). Decide which the model derives; do not sweep to
   the answer (B5). `halo_contraction` at R₀ (1.42) and v_esc(R₀) are the discriminants.
2. **The extended component (#18), probed at D114.** A share s at k R_d on the disc's own
   timescale lowers row 3 (4–13 km/s) and lifts row 20 toward 8e9 — and lifts row 2 with
   it (1.98–2.45 against ≤ 1.84), because the gas arrives above the threshold. The
   component needs a timescale of its own; that is the decision, before any constant.
   Substitute `sfh.infall_profile` and `halo.disc_enclosed_mass` from a script to probe.
3. **The bulge stage (#11).** For rows 10, 12, 13 and the cancellation on row 11; row 14
   needs the source's uncertainty first (#17). It lowers row 3 by 5–8 (D110).
4. **The catalogue migrates (#31).** A systems-stage change with its own golden values;
   rows 6 and 7 in the advanced model judged together when #27's valley opens.
5. **The thick disc (#19).** Rows 5 and 11 fail, row 9 passes at 0.152 on the
   cancellation; radial heating with the vertical kick is the prediction.
6. **Row 6, advanced (#42).** A recorded miss at 358; do not tune it back; wait for the valley.

## What the instruments will tell you, and what they will not

- `uv run python -m galaxy.specs`: exit 0 means every failing row is a recorded miss,
  nothing drifted across its width, and every stage was profiled. Never widen a target
  (B5); record a miss with a prediction. A miss that starts passing fails the run.
- Probing a constant: `tests/test_audit.py::with_constant`; a ruleset: `tests/test_halo.py::
  _with_contraction`; an input: `run(model, {...}, only=(fields,))`. A verdict needs a number.

## Traps

- **A solver that attaches the contracted mass to the orbit-averaged radius makes A cancel**
  — three rulesets read one number (D113). Keep `test_a_third_ruleset_reads_a_third_number`.
- The disc stage is off the acceptance path since S14 (the halo owns R_d); `timings.py`'s
  stage column shows `halo,assembly,sfh`. Its fields are stage one's preview only (D42).
- **Do not merge or delete `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`**:
  the sealed lists D102 compares (D99). Give any paired run a stated aim and reserved numbers.
- Windows: `uv run python` only; Bash commands over ~8 KB fail obscurely; in a worktree
  set `core.hooksPath` per worktree. `tools/progress.py` counts debts by numbered item.
