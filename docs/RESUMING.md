# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's board is the
only record of what is done (A9); this file is rewritten each session, capped at 120 lines (C3). **The
first build (S0–S22) closed; the second (S25–S41, `BUILD_II.md`, §5e) is open: S25–S27 closed on
2026-09-26; S28 (Phase 3, Opus subagent) is next.** The tag batch (MANUAL_TODO.md §1) is owed; S22 stays ◐.

## Open a session (rules C1, C2b)
```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```
Then RULES.md in full, BRIEF.md, and the BUILD_II.md phase BRIEF names; GALAXY_INPUTS.md only by
section — §11's head is the debt map. Branch `session-NN`; commit and push at every
sub-deliverable (C2b). In a worktree: `git config --worktree core.hooksPath tools/hooks`. Write
files with `newline="\n"`: CRLF breaks progress.py's line regexes. **Numbers are sequential**:
debts from #82, decisions from D177, taken when the entry is written.

## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5d, §5e), GALAXY_INPUTS (§11 register),
                DECISIONS, LESSONS, MANUAL_TODO, BUILD_II (the phases), RENDER_PHYSICS (the contract),
                RENDER_PLAN (the viewer's first build, done), the four AUDIT_*.md, future_ideas
model/galaxy/core/    units (closed), cmaps, fielddoc (FieldDecl: optional, contract, provenance), stage
                (CHECKPOINTS 1 Halo & disc, 2 Assembly, 3 Pattern, 4 Star formation & chemistry, 5 Systems,
                6 Planets; **Stage.extends / extend() / Extension**, S27), registry (INPUTS: 7 controls +
                4 seeds + mergers; MODELS; IMPLEMENTATIONS), seeds, grids
model/galaxy/models/  level0 (shared constants), basic, **azimuthal** (BASIC's tuple, sfh slot ->
                sfh_azimuthal, D176); `uv run python -m galaxy.models` prints the slots side by side
model/galaxy/stages/  cp1 halo, disc, nucleus · cp2 assembly · cp3 bar (the swing window, arm_contrast_mean,
                derived) + pattern (arm_multiplicity ∈ {2…6}, the contrasts, pattern_density_contrast (R, φ),
                seeded) · cp4 sfh, **sfh_azimuthal** (extends sfh; adds sfr_modulation (R, φ), optional, seeded),
                chemistry_dtd, vertical_alpha, ism, light · cp5 population + systems (young stars < 0.1 Gyr
                follow sfr_modulation where published; cell counts and names are the contrast's) · cp6 formation + planets
model/galaxy/data/    parsec_isochrones.npz (396 isochrones, 4 columns; tools/fetch_parsec.py)
model/galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…)
model/galaxy/specs/   graph (provenance per stage, extensions at the base's), preflight, determinism, spec (rows
                1–24, MISSES one ledger), convergence, performance; api/: service (ROUTES; model= on every route)
frontend/       Vite + React + three.js (`npm --prefix frontend run dev` on :5173); the rail is data-driven
                from /api/stages and the model toggle shows when the API lists two models
interface/      the earlier plain-JS viewer, still served by the API when frontend/dist is absent
tests/          39 files; every `model`-parametrised test runs per registered model (two since S27);
                test_audit*.py, test_s22/s25/s26_rulings.py, test_sfh_azimuthal.py pin measurements
tools/          progress (the board), bootstrap, verify_clone, timings (rows per route, az: rows), scaling
```
## Writing a stage
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a `FieldDecl`
  beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero,
  provenance, about. `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or
  `.get()` / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked. Register with `IMPLEMENTATIONS.register`,
  import in `stages/__init__.py`, map the slot in the models that use it; a constant goes in `level0.py`
  if more than one model reads it (D29, D85); a field nobody reads is dead. **An about line must not
  name a constant** (D5, `test_the_api_publishes_no_model_internals`).
- **Two implementations of one slot.** Shared fields carry one `FieldDecl.contract` (provenance
  included), the second's own as `optional=True` (D86). If the second reads a seeded field for its own
  field, **extend the first** (`extend(BASE, id=…, own=…, requires=…, publishes=…)`, D176): the shared
  fields are computed by the base in its own view and keep its provenance. Readers of an optional field
  use `requires_optional` and `ctx.fields.get`. A model built from another's tuple cannot drift.
- **A stage may only require fields from its own or an earlier checkpoint** (graph; A1 as rewritten
  at S25, D173). The pattern is checkpoint 3 and star formation 4; rerolling `pattern_seed` discards 4–6
  and, in `azimuthal`, recomputes bit-identical histories (the extension working).
- **A seed binds at the checkpoint of its earliest reader, and `graph` requires that to equal the
  input's `checkpoint_hypothesis`** (S17); a stage reading a seed publishes *seeded* fields, all (D55),
  which is why the derived window lives in `bar` and the draws in `pattern`.
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read
  (D113); a mechanism is probed by substituting one function, the repo unchanged (D114); a default is
  measured or derived by a test (D30, D117, D175); a derived scalar lives on the stage's own mesh, never
  the grid (D119). **A calibration's arithmetic is derived, not just its value**, and **its citation is
  read before the row is trusted** — a table's rows fetched and counted (D175). **Per-region determinism
  is the catalogue's contract** (D60): every table over every ring and sector, and a second model must
  not rename a star (D176). Object columns are `FieldDecl(kind=Kind.COLUMN, of="star")`.

## The API and the viewer
- `uv run python -m galaxy.api` serves the API and `interface/` on 127.0.0.1:8017 (`--client
  frontend/dist` for the built viewer); `Service().handle(path, query)` is what the tests drive. A new route
  is a `Route` in `service.ROUTES` **plus a `tools/timings.py` row**. Metadata never reaches the runner (D4).
- The viewer computes no physics (D5): colour is the declared ramp, light the published Σ_L times the
  pattern's contrast, dust the published A_V per line of sight. **What it invents today** — young light
  in the arms, a seeded clump lattice, Hα knots (f2230d5) — is RENDER_PHYSICS.md §0's dated exception,
  removed by V1–V3 (`sfr_modulation` is the field that replaces the young-light rule). The owner watches
  :5173 live: keep every frontend file consistent within one edit; `npm --prefix frontend run typecheck`.

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. Every input has a
  default and every control a range. Every factual claim in every document is tagged `[verified: cite]`,
  `[recall]` or `[inferred]` (B14); a verified tag cites something in this repo or a named source.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill
  it (D33, D87); it still reports `fail`, never widen a target (B5); a miss that starts *passing* fails
  the run (#29) — remove it and **write down why**. `lo == hi` says "no testable target" (D100). New rows
  (Phase 3: 25–28) cite their source in `QUANTITIES`; a miss with `model=None` binds every model.

## What the instruments said on 2026-09-26, after S27 (D174–D176 hold the before/after)
- graph acyclic for both models (order halo, disc, nucleus, assembly, bar, pattern, sfh | sfh_azimuthal,
  …); preflight OK, controls 7 of 12; determinism reproducible across processes for both; spec **7 pass /
  17 fail / 0 in both models, row for row identical**; convergence 0 drifts in both; row 3 251.026 (#11);
  row 15 5.20971 (#80); row 21 0.2001 against a zero-width 0.11 (#17).
- Regression numbers: z_f 1.66, c₂₀₀ 8.24, R_d 2.60486 (thin 2.44138), M_star 4.751e10, SFR 1.7551515,
  H 8.088e9, WIND_SPEED 860.3, MERGER_HEATING 88.8, `disc_dominance` 0.5999, `swing_x` 3.334, window
  1.722–3.444, `arm_contrast_mean` 0.4815; default seed m = 4, arm 0.401, bar 0.289; rows 16 / 17 medians
  41.10 / 6.08; `sfr_modulation` at R₀ 0.0243–2.511; young stars 0.26% of the catalogue (D176).
- performance: basic 1.23 s cold, azimuthal 1.23 s (sfh_azimuthal 0.131 s against sfh's 0.128 s); no
  stage's cost moved at S25–S27. timings' `az:` rows: modulation 0.146, history 0.406, one sector 0.451.
- Register: **27 open — 11 permanent, 16 carried — and 37 discharged** (#81 opened at S27: the 0.1 Gyr
  young-star cut; #23 discharged at S26; #3 and #26 carried since D173; #80 is row 15's).

## Close a session (GALAXY_PLAN.md §5, in this order)
0. Tick the board — surface, model **actually used**, tag, date — then `uv run python
   tools/progress.py`, then `uv run pytest` once, quiet, **backgrounded with its exit status
   appended to its log** (it outlasts the tool's cap), the merge gated on that line (D115, D120).
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **the cold timings as `tools/timings.py`
   prints them** when a stage's cost changes (B2); rewrite this file (≤ 120) and BRIEF.md (≤ 60) for
   the next row of §5e.
2. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into main: …`;
   push both. **Do not tag** (C2e): add your MANUAL_TODO.md row with the last session's merge SHA
   filled in; never force-push. Then `uv run python tools/verify_clone.py --ref main`.

A session that stops early closes **partially** (C2d): commit, push, BRIEF.md, ◐, no merge. Opus subagents
work in a worktree on the branch (main checkout on `main`), neither push nor write DECISIONS.md; the orchestrator closes.
