# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The first build (S0–S22) closed; the second (S25–S41,
`BUILD_II.md`, GALAXY_PLAN.md §5e) is open: S25 (Phases 0 + 1) closed on 2026-09-26, S26 (Phase 1b,
Fable) is next.** The tag batch (MANUAL_TODO.md §1) is still owed from a desktop; S22 stays ◐ for it.

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
debts from #81, decisions from D175, taken when the entry is written.

## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5d, §5e), GALAXY_INPUTS (§11 register),
                DECISIONS, LESSONS, MANUAL_TODO, BUILD_II (the phases), RENDER_PHYSICS (the contract),
                RENDER_PLAN (the viewer's first build, done), the four AUDIT_*.md, future_ideas
model/galaxy/core/    units (closed), cmaps (incl. `blackbody`, computed), fielddoc (FieldDecl, Kinds,
                Ramp/Palette, AXES), stage (CHECKPOINTS: 1 Halo & disc, 2 Assembly, **3 Pattern, 4 Star
                formation & chemistry** since S25, 5 Systems, 6 Planets), registry (INPUTS: 7 controls
                + 2 experimental amplitudes (D171) + 4 seeds + mergers; MODELS; IMPLEMENTATIONS), seeds, grids
model/galaxy/models/  level0 (shared constants), basic (the one model since D170: chemistry_dtd +
                vertical_alpha + its yields, DTD, wind); a new model is a new file, discovered
model/galaxy/stages/  cp1 halo, disc, nucleus · cp2 assembly · **cp3 bar + pattern** (pattern.py, off the
                checkpoint-1 curve and the λ_d scale length since S25, D174; ARM_MULTIPLICITIES (2, 4))
                · cp4 sfh, chemistry_dtd, vertical_alpha, ism (P, f_H₂, dust, A_V; D163), light (Σ_L,
                colour temperature, Hα, bulge light; D165–166) · cp5 population + systems (the catalogue;
                photometry.py's PARSEC lookup inside materialise) · cp6 formation + planets
model/galaxy/data/    parsec_isochrones.npz (396 isochrones, 4 columns; tools/fetch_parsec.py)
model/galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…)
model/galaxy/specs/   graph, preflight, determinism, spec (QUANTITIES rows 1–24, MISSES), convergence,
                performance;  model/galaxy/api/: service (ROUTES incl. /api/region with brightest= and
                view=, /api/system), wire, version, http
frontend/       the viewer (Vite + React + three.js; `npm --prefix frontend run dev` on :5173): the rail is
                data-driven from /api/stages; preview/CheckpointScene.tsx maps checkpoint -> scene, Workflow.tsx captions
interface/      the earlier plain-JS viewer, still served by the API when frontend/dist is absent
tests/          37 files; test_audit*.py, test_s22_rulings.py and test_s25_rulings.py pin measurements
tools/          progress (the board), bootstrap, verify_clone, timings, scaling, fetch_parsec
```
## Writing a stage
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a `FieldDecl`
  beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero,
  provenance, about. `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or
  `.get()` / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked. Register with `IMPLEMENTATIONS.register`,
  import in `stages/__init__.py`, map the slot in the models that use it; a constant goes in `level0.py`
  if more than one model reads it (D29, D85); a field nobody reads is dead. **Two implementations of one
  slot** publish the same names under one contract (`FieldDecl.contract`), their own as `optional=True`
  (D86) — the machinery D170 reverted and Phase 2 restores.
- **A stage may only require fields from its own or an earlier checkpoint** (graph's checkpoint-order
  check; A1 as rewritten at S25, D173: acyclic graph, iteration inside a stage when its termination is
  guaranteed in advance, as `contracted_halo`'s bisection is). Since S25 the pattern is checkpoint 3 and
  star formation 4: a star-formation stage may read the pattern; rerolling `pattern_seed` discards 4–6.
- **A seed binds at the checkpoint of its earliest reader, and `graph` requires that to equal the
  input's `checkpoint_hypothesis`** (S17); a stage reading a seed publishes *seeded* fields, all (D55) —
  so a *derived* amplitude belongs in `bar` (the derived half), a seeded residual in `pattern`.
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read
  (D113); a mechanism is probed by substituting one function, the repo unchanged (D114; `sfh.first_infall`,
  `.toomre_threshold`, `halo.angular_momentum_core`); a default is measured or derived by a test (D30,
  D117, D128); a derived scalar lives on the stage's own mesh, never the grid (D119). **A calibration's
  arithmetic is derived, not just its value** (S20), and **its citation is read before the row is
  trusted** (S21 a; S25: A1's own cited a file never in the repository, D173). **Per-region determinism
  is the catalogue's contract** (D60). Object columns are
  `FieldDecl(kind=Kind.COLUMN, of="star")`; a second object class is a `core/` edit plus a decision.

## The API and the viewer
- `uv run python -m galaxy.api` serves the API and `interface/` on 127.0.0.1:8017 (`--client
  frontend/dist` for the built viewer); `Service().handle(path, query)` is what the tests drive. A new
  route is a `Route` in `service.ROUTES` **plus a row in `tools/timings.py`**. Metadata answers from
  declarations, never the runner (D4, D63); objects are materialised per request, cached per cell (D168).
- The viewer computes no physics (D5): colour is the declared ramp, light the published Σ_L times the
  pattern's contrast, dust the published A_V per line of sight. **What it invents today** — young light
  in the arms, a seeded clump lattice, Hα knots (f2230d5) — is RENDER_PHYSICS.md §0's dated exception,
  removed by V2/V3. The owner watches :5173 live: keep every frontend file consistent within one edit.

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. Every input has a
  default and every control a range. Every factual claim in every document is tagged `[verified: cite]`,
  `[recall]` or `[inferred]` (B14); a verified tag cites something in this repo or a named source.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill
  it (D33, D87); it still reports `fail`, never widen a target (B5); a miss that starts *passing* fails
  the run (#29) — remove it and **write down why**. `lo == hi` says "no testable target" (D100). New
  rows (BUILD_II Phases 3, 5, 6, 9) take the next numbers from 25 and cite their source in `QUANTITIES`.

## What the instruments said on 2026-09-26, after S25 (D174's table has the before/after)
- graph acyclic, order halo, disc, nucleus, assembly, **bar, pattern, sfh**, …; preflight OK, 0 UNSET;
  determinism reproducible across processes; spec **basic 7 pass / 17 fail / 0 n-y-c**, every failure
  recorded; convergence 0 drifts; row 3 251.026 (out by 0.027, half of it the mesh, D160); **row 15
  5.20971 against 4.8–5.2, out by 0.010, recorded under #80** (4.88277 on the thin disc's fitted
  length until the pattern moved ahead of `sfh`); row 21 0.2001 against a zero-width 0.11 (#17).
- Regression numbers: z_f 1.66, c₂₀₀ 8.24, R_d 2.60486 (thin 2.44138), M_star 4.751e10, SFR 1.755,
  H 8.088e9, WIND_SPEED 860.3, MERGER_HEATING 88.8, `disc_dominance` 0.5999 and `shear_rate` 0.9680 at
  5.73 kpc, rows 16 / 17 medians 41.10 / 6.08 (default seed 45.4636 / 5.48371), row 18 median 1.97e7.
- performance: basic 1.18 s cold; light 25%, systems 25%, chemistry_dtd 22%, planets 11%, sfh 10%;
  the catalogue priced per cell, 368 µs per cell realised. No stage's cost moved at S25.
- Register: **27 open — 12 permanent, 15 carried — and 36 discharged**; the map at §11's head agrees
  with its table again. #3 and #26 carried since D173 (the retained budget as a root inside checkpoint
  1: probe f* 0.338 against the input's 0.35); #80 is row 15's.

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
work in a worktree on the session branch, neither push nor write DECISIONS.md; the orchestrator closes (§5e).
