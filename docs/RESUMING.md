# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The first build (S0–S22) closed; the second (S25–S41,
`BUILD_II.md`, GALAXY_PLAN.md §5e) is open.** The tag batch in MANUAL_TODO.md §1 is still owed
from a desktop (D161), and S22 stays ◐ for it.

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
debts from #80, decisions from D173, taken when the entry is written.

## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5d, §5e), GALAXY_INPUTS (§11 register),
                DECISIONS, LESSONS, MANUAL_TODO, BUILD_II (the phases), RENDER_PHYSICS (the contract),
                RENDER_PLAN (the viewer's first build, done), the four AUDIT_*.md, future_ideas
model/galaxy/core/    units (closed), cmaps (incl. `blackbody`, computed), fielddoc (FieldDecl, Kinds,
                Ramp/Palette, AXES), stage, registry (INPUTS: 7 controls + 2 experimental amplitudes
                (D171) + 4 seeds + mergers; MODELS; IMPLEMENTATIONS), seeds, grids, special
model/galaxy/models/  level0 (shared constants), basic (the one model since D170: chemistry_dtd +
                vertical_alpha + its yields, DTD, wind); a new model is a new file, discovered
model/galaxy/stages/  cp1 halo, disc, nucleus · cp2 assembly · cp3 sfh, chemistry_dtd, vertical_alpha,
                ism (P, f_H₂, dust, A_V; D163), light (Σ_L, colour temperature, Hα, bulge light; D165–166)
                · cp4 bar + pattern (pattern.py: `pattern_density_contrast`, ARM_MULTIPLICITIES (2, 4))
                · cp5 population + systems (the catalogue; photometry.py's PARSEC lookup inside
                materialise: star_luminosity, star_temperature, star_alpha) · cp6 formation + planets
model/galaxy/data/    parsec_isochrones.npz (396 isochrones, 4 columns; tools/fetch_parsec.py)
model/galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…)
model/galaxy/specs/   graph, preflight, determinism, spec (QUANTITIES rows 1–24, MISSES), convergence,
                performance;  model/galaxy/api/: service (ROUTES incl. /api/region with brightest= and
                view=, /api/system), wire, version, http
frontend/       the viewer (Vite + React + three.js; `npm --prefix frontend run dev` on :5173):
                galaxy/ (FieldVolume ray-marcher, regimes, frustum, psf), preview/, system/
interface/      the earlier plain-JS viewer, still served by the API when frontend/dist is absent
tests/          405 tests; test_audit*.py and test_s22_rulings.py pin the audits' measurements
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
- **A seed binds at the checkpoint of its earliest reader, and `graph` requires that to equal the
  input's `checkpoint_hypothesis`** (S17); a stage reading a seed publishes *seeded* fields, all (D55).
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read
  (D113); a mechanism is probed by substituting one function, the repo unchanged (D114; `sfh.first_infall`,
  `.star_formation_rate`, `.radial_transport`, `.toomre_threshold`, `halo.angular_momentum_core`); a
  default is measured or derived by a test (D30, D117, D128); a derived scalar lives on the stage's own
  mesh, never the grid (D119). **A calibration's arithmetic is derived, not just its value** (S20), and
  **its citation is read before the row is trusted** (S21 a, A-14). **Per-region determinism is the
  catalogue's contract** (D60): nothing in `materialise` may depend on which cells a request asked for.
- Object columns are `FieldDecl(kind=Kind.COLUMN, of="star")`; a second object class (clouds, clusters:
  BUILD_II Phases 8 and 11) is a `core/` edit plus a DECISIONS entry, as a new unit or kind is.

## The API and the viewer
- `uv run python -m galaxy.api` serves the API and `interface/` on 127.0.0.1:8017 (`--client
  frontend/dist` for the built React viewer); `Service().handle(path, query)` is the same without a
  socket and is what the tests drive. A new route is a `Route` in `service.ROUTES` **plus a row in
  `tools/timings.py`**. Metadata answers from declarations and must not reach the runner (D4, D63);
  objects are materialised per request (D82) and cached per cell (`CellCache`, D168).
- The viewer computes no physics (D5): colour is the declared ramp (the blackbody cmap on
  `star_temperature`), light is the published Σ_L times the pattern's contrast, dust is the published
  A_V per line of sight. **What it invents today** — young light crowded into the arms, a seeded clump
  lattice, Hα knots (f2230d5) — is recorded in RENDER_PHYSICS.md §0 as the dated exception V2/V3 remove.

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. Every input has a
  default and every control a range. Every factual claim in every document is tagged `[verified: cite]`,
  `[recall]` or `[inferred]` (B14); a verified tag cites something in this repo or a named source — A1's
  `bench2.py` never existed here, and Phase 0 is the correction.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill
  it (D33, D87); it still reports `fail`, never widen a target (B5), and a miss that starts *passing*
  fails the run (#29) — remove it and **write down why it passed**. `lo == hi` says "no testable
  target" (D100). New rows (BUILD_II Phases 3, 5, 6, 9) take the next numbers from 25 and cite their
  source in `QUANTITIES`; the habitable zone gets none, on purpose.

## What the instruments said on 2026-09-26 (no physics changed since S20)
- graph acyclic; preflight OK, 0 UNSET; determinism reproducible across processes; spec **basic
  8 pass / 16 fail / 0 n-y-c**; convergence 0 drifts; row 3 251.026 (out by 0.027, half of it the
  mesh, D160); row 15 4.88277 in [4.8, 5.2] — **the one green row Phase 1 can move**; row 21 0.2001
  against a zero-width 0.11 (#17).
- Numbers to spot a regression by: z_f 1.66, c₂₀₀ 8.24, R_d 2.605 (thin 2.44), M_star 4.75e10, SFR 1.755,
  H 8.09e9, WIND_SPEED 860.3, MERGER_HEATING 88.8, rows 16 / 17 / 18 at 47.46 / 5.14 / 1.35e7 (seeded).
- performance: basic 1.44 s cold; systems 25%, light 24%, chemistry_dtd 24%; the catalogue priced per
  cell, 389 µs per cell realised (R² 0.92).
- Register: **26 open — 14 permanent, 12 carried — and 36 discharged**; the map at §11's head still
  counts #79 as permanent in its prose (D163 discharged it) — Phase 0 rewrites the map anyway.

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

A session that stops early closes **partially** (C2d): commit, push, what remains into BRIEF.md, ◐,
no merge. Opus subagents work in a worktree on the session branch and neither push nor write
DECISIONS.md; the orchestrating session reviews against the gate and closes (§5e).
