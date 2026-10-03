# BRIEF — for S56: BUILD_III's Phase P1, several arm modes at once; the gas follows any pattern (an Opus lead)

**The state (2026-10-04).** S55 is merged (D214): the physics model and the randomness layer are separate in the
code. `run(layer=)` and `layer=off` on every route; `galaxy/layer/` holds `noise.py` (the primitives and 632
committed vectors, read by nothing yet), `compose.py` (the one place that tests the switch) and the layer stage
`cloud_texture`; the 37 rows and the template checks are judged layer-off; the viewer has "physics only". Gate G1
ruled the invariants hold on **expected** totals until L1 (#137). Rows layer-off: 35 −2.081 (passes), 37 −0.1030
(a miss); 12 / 20 / 5. Register 75 open = 11 + 64, 45 discharged. Numbers from D215, #138, row 38, board row 56.
**The owner's standing order: run the sessions back to back, stop only for a ruling that is the owner's, spawn
Fable at the plan's gates.**

## First
`uv run python tools/bootstrap.py` (S55's close ran the suite and `verify_clone` on `main`). **Read `BUILD_III.md` §1 (as amended at G1), "Phase P1" in §5 and Appendix B: that text is the ruling.** P1 has no
planned gate; a conditional one opens only if the probe contradicts §5 (BUILD_III §3d).

## Phase P1 in one paragraph (the plan's ruling; build to it)
At each radius the weight of arm number m is the existing `swing_weight` at the *local* swing parameter X_m(R)
(today's named alternative in `pattern.py` becomes the law; m = 2–6; no new constant). **Power is conserved, not
the peak:** Σ_m A_m(R)² = A², A today's single-mode amplitude; one surviving mode returns today's field exactly.
The realisation, *synthetic*: each mode's phase, a **new draw on `texture_seed`** — G1 found there is no phase
draw today, only the convention ln R · cot(pitch), so nothing is "moved". The gas: with ψ = (c − 1)/A the stellar
pattern scaled to unit amplitude, the ridge is exp(κψ) over its ring mean, S51's κ and amplitude rule, the mask
the cells where ψ exceeds the level that encloses the share of the ring the 1.5 kpc mask did; **with one mode it
is S51's field to 1e-9, the regression gate.** The arm-number draw retires (Appendix B); the pitch's, the
amplitude's and the bar's scatter stay seeded.

## The order
1. **A probe, repo unchanged, before any build** (BUILD_III §3g): the split of power among m = 2–6 by radius at
   the defaults and at `ngc_4414`'s inputs, and the single-mode limit. If it contradicts the plan's text — a
   degenerate split, no single-mode limit for the field or the ridge — **stop and write the handoff.**
2. **One reader (a check, not an input):** Fourier amplitude spectra of spirals by arm number and radius, set
   beside the law's split in D215. Blind to the model's split.
3. **D215's ruling committed first**, then builders (§3f): the mode law; the realisation (the phases, a layer
   stage, the first reader of `texture_seed` — remove `graph.UNREAD_BY_RULING`'s one entry, the test that guards
   it says so); the gas response; the catalogues' re-pins. Then an Opus reviewer on the diff.

**Gate:** ring means 1; the single-mode regression (1e-9); a Fourier decomposition of the composed field returns
the published amplitudes; I1–I3 (`tests/test_layer.py`; a new composed field declares itself and its neutral);
the goals' azimuthal spectra beside the render's (`tools/goal_metrics.py`; S53's and S54's tables the baseline).

## What changes for everything downstream (say so in D215)
- **With the layer on, the default galaxy changes**: several modes replace one, the censuses are re-placed, the
  six layered frames change (regenerate with `picture:update`, and say so). Layer-off nothing may move: the 37
  rows, the template checks and every radial field are judged there and must be bit-identical to S55's.
- The phases are the first field on `texture_seed`: rerolling it changes placements and nothing else (§1c rule 1).
  `ngc_4414`'s picture changes with the modes; its fit and its checks may not (D213).

## Traps
- A composed field is a declaration (`composed`, `neutral`), not a φ axis (G1). A pattern object is built only
  through `layer/compose.py`; a source test refuses `ArmPattern(` / `GasPattern(` / `.from_fields(` elsewhere.
- `CENSUS_STATISTICS` (fourteen names) is closed: a fifteenth is a finding. Rows 35 and 37 must not move here.
- No third fit of `ngc_4414`, no unspent NGC 4414 window read (D213). No ring-first draw here: it is L1's.
- A builder's first step is `git merge --ff-only session-56`, then bootstrap (again before the closing suite).
  A subagent cannot write a report file: ask a reviewer for its findings as its final message.
- Scripts in the scratchpad, never `$TMP`; LF newlines; `tests/test_audit.py` pins the register's counts.

## The owner's answers (2026-10-04, D215)
1. `ngc_4414`: keep the current fit; no second fit.
2. Rule A10 amended to expected ring totals until L1; the sessions keep the plan's order: this phase is next.
