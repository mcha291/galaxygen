# BRIEF — for S27: BUILD_II Phase 2, `sfh_azimuthal` and the `azimuthal` model (Opus subagent)

**For the orchestrating session.** S27 is the first Opus row (GALAXY_PLAN.md §5e). Open `session-27`,
then hand an Opus subagent — in a worktree on that branch, `git config --worktree core.hooksPath
tools/hooks` — this file, `BUILD_II.md` Phase 2 (its design decision is made: read it verbatim),
`RULES.md`, and `RESUMING.md`'s "Writing a stage". The subagent **neither pushes nor writes
DECISIONS.md**; it commits on the branch, reports the diff and the measurements, and the orchestrator
reviews against the gate, runs the suite, writes D176, and closes by RESUMING.md's ritual. Numbers
sequential from debt #81 and decision D176; MANUAL_TODO's `s26` row takes S26's merge SHA.

## What to build (BUILD_II.md Phase 2, reconciled)
- **`sfh_azimuthal`**, a second implementation of the `sfh` slot at checkpoint 4, publishing everything
  `sfh` publishes under the same contract plus **one (R, φ) field**: the present-day star-formation
  modulation, `pattern_density_contrast` raised to `KS_INDEX` with the threshold's `tanh` switch applied
  per cell, renormalised so its gas-weighted mean around every ring is 1. **No φ axis on any history**
  (the design paragraph at Phase 2's head says why: 288 million cells, and azimuthal mixing is faster
  than enrichment). Build it from `sfh`'s functions, not a copy: import and reuse.
- **The `azimuthal` model**, `model/galaxy/models/azimuthal.py`, built **from `BASIC`'s tuple** with the
  `sfh` slot swapped (the snippet in Phase 2), constants shared. A test asserts the two models differ in
  exactly one slot. Since S25 the pattern is checkpoint 3, so a checkpoint-4 stage may require
  `pattern_density_contrast` — that reorder was made for this.
- **The two-implementation machinery**: `FieldDecl.contract` and `optional=True` (D86), reverted by
  D170 when the models collapsed to one; restore it from D169/D170's tests and `git show 4a20490`.
- **The catalogue's young stars** follow the modulation in `azimuthal` and the density contrast alone
  in `basic` (the arm-crossing timescale, ~100 Myr, is the age cut — say where the number comes from).
- **The viewer's model toggle** returns when the registry holds two models (hidden at one, D170).

## Gate (assert, do not eyeball)
Both models pass graph, preflight and determinism (per model: `graph.py`'s ORDER and `bound` tables,
`tests/test_graph.py`, are per model name). **The modulation integrates to the axisymmetric SFR over
φ at every radius** — a redistribution, not a new source (RENDER_PHYSICS §7). **Every acceptance row
reads the same in both models at the defaults**: `tests/test_spec.py`'s SUMMARY / FAILED / DEBTS are
per model, so the `azimuthal` entries are the `basic` ones; record any row that differs and why.
Rows 15–17 unmoved (5.20971 recorded miss #80 / 41.1036 / 6.08381). `python -m galaxy.specs` exits 0.

## Traps
- The `judged` fixture and every `model`-parametrised test run per registered model: expect the suite
  to roughly double where it builds galaxies; keep new tests on `COARSE` grids where the claim allows.
- `tools/timings.py` has a row per route and `tests/test_timings.py` pins the route list; a second model
  needs no new route, but the `model=` query is exercised — check `test_api`'s model-switch tests.
- Two implementations of one slot **must publish the same names** or the graph's producer map breaks
  per model; the (R, φ) field is the only `optional=True` one.
- The pattern's fields are seeded, so `sfh_azimuthal`'s modulation is seeded too and provenance follows
  per stage (D55): every field `sfh_azimuthal` publishes becomes *seeded* in `azimuthal`, including the
  histories `basic` publishes as derived. Say so in the decision; do not fight the labelling.
- Write files with `newline="\n"`; the full suite outlasts the tool's cap — background it with `EXIT=$?`
  on its log and gate the merge on that line. A recorded miss that starts passing fails the run (#29).
- The owner watches :5173 live: one consistent edit per frontend file; `npm --prefix frontend run
  typecheck` and `run test`; say "hard-reload". `progress.py` names S22 as "Next" by design; leave it.
- **Do not merge or delete** `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`,
  `session-21-a` or `claude/keen-lamport-lldlvp` (MANUAL_TODO §2).

## At close (orchestrator)
Board row 27 ☑ with the model actually used (the subagent's); `uv run python tools/progress.py`; the
suite; D176 with the redistribution check's numbers and the per-model rows; RESUMING (≤ 120) and this
file rewritten for **S28 (Phase 3, Opus)**; `MANUAL_TODO.md` row `s27` with `s26`'s merge SHA filled
in; merge `--no-ff`, push, `uv run python tools/verify_clone.py --ref main`.
