# BRIEF — for S26: BUILD_II Phase 1b, the amplitudes and the arm number (Fable)

Read `RULES.md` in full (A1 is new since S25), `RESUMING.md`, `BUILD_II.md` Phase 1b and the
design paragraph at the head of Phase 2 (what will read the contrast), `GALAXY_INPUTS.md` §4b (the
three verdicts and the two remedies) and §11 items 21, 22, 23 and 80, then `DECISIONS.md` D174.
Branch `session-26`; commit and push at every sub-deliverable (C2b); numbers sequential from
debt #81 and decision D175. S27 (Phase 2) is the first Opus row: write its BRIEF as a subagent
prompt — Phase 2's text, the gate, RULES — and note the worktree rule (no push, no DECISIONS).

## What to build
`arm_amplitude` and `bar_amplitude` are two **inputs** (D171), read by `pattern` and published
back as `arm_contrast` / `bar_contrast`, then `ArmPattern(arm, bar, m, pitch, a_bar)` builds
`pattern_density_contrast`. Phase 2's modulation reads that field, so built on two sliders it would
be a modulation of an input (A2; RENDER_PLAN M1: "it does not become a control"). Remove both.
- **Derive the arm amplitude's mean** from what `bar` already publishes off the checkpoint-1 curve
  — `shear_rate` 0.9680 and `disc_dominance` 0.5999 at 2.2 R_d = 5.73 kpc (D174) — through swing
  amplification's gain; the bar's from its length relative to the disc (`bar_half_length`/R_d = 2.0,
  a constant today). A derivation that closes is §4b's verdict B; one that leaves real scatter is C,
  and the remedy is **derive the mean, seed the residual on `pattern_seed`**, as `pitch_angle` is
  (`PITCH_SHEAR_*`, `PITCH_SCATTER`). Write the verdict down before the number is read (D113).
- **The arm number**: `arm_multiplicity` is `ARM_MULTIPLICITIES[rng("pattern_seed","arms")]`, a
  2-or-4 coin toss (D174). Derive the preferred m from Toomre's X = κ²R/(2πGΣm) — κ is the disc
  stage's `epicyclic_frequency`, Σ its `disc_surface_density`, both checkpoint 1 — with the
  residual seeded, and a **flocculent** state where the gain is weak; or keep a draw widened to
  {2, 3, 4} with the odds stated. **NEEDS SOURCING before it enters code** (B9): Toomre 1981;
  Sellwood & Carlberg 1984 — delegate the reading to a read-only agent with web access, take the
  number and the citation, decide yourself.
- **Re-rule #23** ("the arms are parameters, not a pattern", permanent because no stage published a
  non-axisymmetric density — one does since 5f79cfc): discharge it, or restate what it now names.

## Gate
Rows 15–17 unmoved: **row 15 stays 5.20971, the recorded miss under #80** (the amplitudes do not
enter it; if it moves, something else did). The contrast still averages to 1 around every ring
(`tests/test_pattern.py`). Determinism and convergence re-run and re-pinned. `/api/inputs` reads
**7 controls, 4 seeds, 1 event list** — `tools/timings.py` line 52 already says so and has been
wrong since M1; make it true. `tests/test_graph.py`'s `bound` dict loses the two amplitudes.

## Traps
- Provenance is per stage (D55): a *derived* amplitude published from `pattern` would be labelled
  seeded. If the verdict is B, publish it from `bar`; if C, the mean can live in `bar` and the
  drawn value in `pattern`, or both in `pattern` — say which and why.
- The frontend's bottom bar holds the two sliders (`frontend/src/workflow/useWorkflow.ts`); the owner
  watches :5173 live, so remove the controls and their uses in one consistent edit per file, run
  `npm --prefix frontend run typecheck` and `run test`, and say "hard-reload".
- Write files with `newline="\n"`; the full suite outlasts the tool's cap — background it with
  `EXIT=$?` on its log and gate the merge on that line (S14's and S17's trap).
- A recorded miss that starts passing fails the run (#29); a new one needs a debt, a reason and a
  prediction in `spec._MISSES` (row 15's entry is the template).
- `progress.py` names S22 as "Next" while its tag batch is owed; that is by design. Leave S22's ◐.
- **Do not merge or delete** `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`,
  `session-21-a` or `claude/keen-lamport-lldlvp` (MANUAL_TODO §2).

## At close
Board row 26 ☑ with the model actually used; `uv run python tools/progress.py`; the suite; D175
with the verdict, the derivation and its citation, and rows 15–17 before/after; a lesson if one was
learnt; RESUMING (≤ 120) and this file rewritten for **S27 (Phase 2, Opus subagent)**;
`MANUAL_TODO.md` row `s26` with `s25`'s merge SHA filled in; merge `--no-ff`, push,
`uv run python tools/verify_clone.py --ref main`.
