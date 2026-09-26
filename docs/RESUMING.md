# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's board is the
only record of what is done (A9); this file is rewritten each session, capped at 120 lines (C3). **The
first build (S0–S22) closed; the second (S25–S41, `BUILD_II.md`, §5e) is open: S25–S28 closed on
2026-09-26; S29 (Phase 4, remnants, Opus subagent) is next.** The tag batch (MANUAL_TODO.md §1) is owed; S22 stays ◐.

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
debts from #85, decisions from D178, taken when the entry is written.

## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5d, §5e), GALAXY_INPUTS (§11 register),
                DECISIONS, LESSONS, MANUAL_TODO, BUILD_II (the phases), RENDER_PHYSICS (the contract),
                RENDER_PLAN (the viewer's first build, done), the four AUDIT_*.md, future_ideas
model/galaxy/core/    units (closed; Msun/Lsun, 1/s, 1/s/kpc2 since S28), cmaps, fielddoc (FieldDecl:
                optional, contract, provenance), stage (CHECKPOINTS 1 Halo & disc, 2 Assembly, 3 Pattern,
                4 Star formation & chemistry, 5 Systems, 6 Planets; Stage.extends / extend()), registry
                (INPUTS: 7 controls + 4 seeds + mergers; MODELS; IMPLEMENTATIONS), seeds, grids
model/galaxy/models/  level0 (shared constants), basic, azimuthal (BASIC's tuple, sfh -> sfh_azimuthal)
model/galaxy/stages/  cp1 halo, disc, nucleus · cp2 assembly · cp3 bar + pattern · cp4 sfh, sfh_azimuthal
                (extends sfh; sfr_modulation), chemistry_dtd, vertical_alpha, ism, light (Σ_L, colour, Hα,
                **eight-band magnitudes, B − V, Υ_V, Σ_V, V scale length, Q(H⁰)** S28) · cp5 population +
                systems (catalogue columns looked up inside materialise: L, T_eff, [α/Fe], **M_V, Q, wind
                luminosity, Wolf–Rayet flag**) · cp6 formation + planets; massive_stars.py (Q tables, blackbody, wind, WR)
model/galaxy/data/    parsec_isochrones.npz (396 × 137 818 rows; U B V R I J H K, M_bol, present mass since S28; fetch_parsec.py)
model/galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…)
model/galaxy/specs/   graph, preflight, determinism, spec (rows 1–29; modes pointwise / statistical /
                qualitative / **sweep**; MISSES one ledger), convergence, performance; api/: service (ROUTES)
frontend/       Vite + React + three.js (`npm --prefix frontend run dev` on :5173); rail and model toggle
                data-driven from /api/stages
interface/      the earlier plain-JS viewer, still served by the API when frontend/dist is absent
tests/          40 files; every `model`-parametrised test runs per registered model (two); test_audit*.py,
                test_s22/s25/s26_rulings.py, test_sfh_azimuthal.py, test_massive_stars.py pin measurements
tools/          progress (the board), bootstrap, verify_clone, timings, scaling, fetch_parsec
```
## Writing a stage
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a `FieldDecl`
  beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero,
  provenance, about. `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or
  `.get()` / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked. Register with `IMPLEMENTATIONS.register`,
  import in `stages/__init__.py`, map the slot in the models that use it; a constant goes in `level0.py`
  if more than one model reads it (D29, D85); a field nobody reads is dead. **An about line must not
  name a constant** (D5, `test_the_api_publishes_no_model_internals`). A new unit is a `core/units.py`
  edit plus a line in the decision (D177).
- **Two implementations of one slot.** Shared fields carry one `FieldDecl.contract` (provenance
  included), the second's own as `optional=True` (D86); if the second reads a seeded field for its own
  field, **extend the first** (`extend(BASE, id=…, own=…, requires=…, publishes=…)`, D176) so the shared
  fields keep the base's provenance. Optional fields: `requires_optional` + `ctx.fields.get`.
- **A stage may only require fields from its own or an earlier checkpoint** (graph; A1 as rewritten
  at S25, D173). The pattern is checkpoint 3 and star formation 4; rerolling `pattern_seed` discards 4–6.
- **A seed binds at the checkpoint of its earliest reader, and `graph` requires that to equal the
  input's `checkpoint_hypothesis`** (S17); a stage reading a seed publishes *seeded* fields, all (D55).
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read
  (D113; S28: the Q table over the blackbody, and what light a row judges); a mechanism is probed by
  substituting one function, the repo unchanged (D114); a default is measured or derived by a test (D30,
  D117, D175); a derived scalar lives on the stage's own mesh (D119). **A calibration's citation is read
  before it enters code** — a table's rows fetched, counted, its arithmetic checked (D175, D177) — and
  **say what fraction of a quantity it covers** (#84). **Per-region determinism is the catalogue's
  contract** (D60): columns looked up inside `materialise`; a second model must not rename a star.
- **Population numbers come from the field, not the sample**: light, magnitudes and Q are history
  integrals along the isochrones, each step averaged over the ages its stars span (D177).

## The API and the viewer
- `uv run python -m galaxy.api` serves the API and `interface/` on 127.0.0.1:8017 (`--client
  frontend/dist` for the built viewer); `Service().handle(path, query)` is what the tests drive. A new route
  is a `Route` in `service.ROUTES` **plus a `tools/timings.py` row**. Metadata never reaches the runner (D4).
- The viewer computes no physics (D5): colour is the declared ramp, light the published Σ_L times the
  pattern's contrast, dust the published A_V per line of sight. **What it invents today** — young light
  in the arms, a seeded clump lattice, Hα knots — is RENDER_PHYSICS.md §0's dated exception, removed by
  V1–V3 (`sfr_modulation` and the band magnitudes are the fields that replace it). The brightest-N mode
  still ranks by bolometric L; ranking by `star_magnitude_v` is owed to V1 (D177). The owner watches :5173
  live: keep every frontend file consistent within one edit; `npm --prefix frontend run typecheck`.

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. Every input has a
  default and every control a range. Every factual claim in every document is tagged `[verified: cite]`,
  `[recall]` or `[inferred]` (B14); a verified tag cites something in this repo or a named source.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill
  it (D33, D87); it still reports `fail`, never widen a target (B5); a miss that starts *passing* fails the
  run (#29) — remove it and **write down why**. `lo == hi` says "no testable target" (D100; rows 20, 21,
  25–28); a row whose source does not say what it measures names no field (D177). New rows from 30.

## What the instruments said on 2026-09-26, after S28 (D174–D177 hold the before/after)
- graph acyclic for both models; preflight OK, controls 7 of 12; determinism reproducible across
  processes for both; spec **8 pass / 17 fail / 4 not-yet-computable of 29, identical in both models**,
  every failure recorded; convergence 0 drifts; row 3 251.026 (#11); row 15 5.20971 (#80); row 21 0.2001
  (#17); **row 29 (Tully–Fisher slope) −7.914 in [−8.56, −7.14]**; rows 25–28 not-yet-computable (#82).
- Regression numbers: z_f 1.66, c₂₀₀ 8.24, R_d 2.60486 (thin 2.44138), M_star 4.751e10, SFR 1.7551515,
  H 8.088e9, WIND_SPEED 860.3, MERGER_HEATING 88.8, `swing_x` 3.334, window 1.722–3.444; rows 16 / 17
  medians 41.10 / 6.08; **M_B −20.5853, M_V −21.2159, B − V 0.6306, Υ_V 1.8468, BC_V −0.83843,
  disc_luminosity 4.8958e10 (5.31e10 until S28's step averaging), V scale length 4.403, Q 1.6527e53 s⁻¹**.
- performance: basic 1.29 s cold (light 0.40 cold / 0.06 warm after S28's table integrals; systems,
  chemistry_dtd ~25% each); az: one star 0.476 cold. The catalogue ~370 µs per cell realised.
- Register: **30 open — 11 permanent, 19 carried — and 37 discharged** (#82–#84 opened at S28: the
  photometric rows' dust question, the wind's Γ_e, the ionizing budget's reach).

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
