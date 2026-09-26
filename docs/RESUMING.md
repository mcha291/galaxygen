# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's board is the
only record of what is done (A9); this file is rewritten each session, capped at 120 lines (C3). **The
first build (S0–S22) closed; the second (S25–S41, `BUILD_II.md`, §5e) is open: S25–S30 closed on 2026-09-26
(S29 and S30 ran in parallel, merged in row order); S31 (Phase 7, dust that radiates, Opus) is next.** Tag batch owed; S22 ◐.

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
debts from #91, decisions from D180, taken when the entry is written.

## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5d, §5e), GALAXY_INPUTS (§11 register),
                DECISIONS, LESSONS, MANUAL_TODO, BUILD_II (the phases), RENDER_PHYSICS (the contract),
                RENDER_PLAN (the viewer's first build, done), the four AUDIT_*.md, future_ideas
model/galaxy/core/    units (closed; Msun/Lsun, 1/s, 1/s/kpc2 S28; 1/yr, 1/yr/kpc2, 1/Msun S30), cmaps, fielddoc (FieldDecl:
                optional, contract, provenance), stage (CHECKPOINTS 1 Halo & disc, 2 Assembly, 3 Pattern,
                4 Star formation & chemistry, 5 Systems, 6 Planets; Stage.extends / extend()), registry
                (INPUTS: 7 controls + 4 seeds + mergers; MODELS; IMPLEMENTATIONS), seeds, grids
model/galaxy/models/  level0 (shared constants), basic, azimuthal (BASIC's tuple, sfh -> sfh_azimuthal)
model/galaxy/stages/  cp1 halo, disc, nucleus · cp2 assembly · cp3 bar + pattern · cp4 sfh, sfh_azimuthal
                (extends sfh), chemistry_dtd, **supernovae** (S30: core collapse = SFR × IMF, Ia = the chemistry's
                DTD convolution counted), vertical_alpha, ism, light (Σ_L, colour, Hα, eight bands, Q(H⁰)) · cp5
                population (IMF integrals, remnant_mass_fraction, planetary_nebula_count) + systems (columns inside
                materialise: L, T_eff, [α/Fe], M_V, Q, wind, WR, star_remnant + mass) · cp6 formation, **habitable_zone**
                (S30, unjudged), planets; massive_stars.py (Q tables, wind, WR); remnants.py (IFMR, budget)
model/galaxy/data/    parsec_isochrones.npz (396 × 137 818 rows; U B V R I J H K, M_bol, present mass; fetch_parsec.py)
model/galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…)
model/galaxy/specs/   graph, preflight, determinism, spec (rows 1–31; modes pointwise / statistical /
                qualitative / sweep; MISSES one ledger), convergence, performance; api/: service (ROUTES)
frontend/       Vite + React + three.js (`npm --prefix frontend run dev` on :5173); rail and model toggle
                data-driven from /api/stages
interface/      the earlier plain-JS viewer, still served by the API when frontend/dist is absent
tests/          43 files; every `model`-parametrised test runs per registered model (two); test_audit*.py,
                test_s22/s25/s26_rulings, test_sfh_azimuthal, test_massive_stars, test_remnants, test_supernovae pin measurements
tools/          progress (the board), bootstrap, verify_clone, timings, scaling, fetch_parsec
```
## Writing a stage
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a `FieldDecl`
  beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero,
  provenance, about. `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or
  `.get()` / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked. Register with `IMPLEMENTATIONS.register`,
  import in `stages/__init__.py`, map the slot in the models that use it; a constant goes in `level0.py`
  if more than one model reads it (D29, D85) — and at module level only where `materialise` must read
  it (S28, S29); a field nobody reads is dead. **An about line must not name a constant** (D5). A new
  unit is a `core/units.py` edit plus a line in the decision (D177).
- **Two implementations of one slot.** Shared fields carry one `FieldDecl.contract` (provenance included),
  the second's own as `optional=True` (D86); if the second reads a seeded field for its own field, **extend
  the first** (`extend(BASE, …)`, D176) so the shared fields keep the base's provenance; `requires_optional` + `ctx.fields.get`.
- **A stage may only require fields from its own or an earlier checkpoint** (graph; A1 as rewritten
  at S25, D173). The pattern is checkpoint 3 and star formation 4; rerolling `pattern_seed` discards 4–6.
- **A seed binds at the checkpoint of its earliest reader, and `graph` requires that to equal the
  input's `checkpoint_hypothesis`** (S17); a stage reading a seed publishes *seeded* fields, all (D55).
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read
  (D113); a mechanism is probed by substituting one function (D114); a default is measured or derived by
  a test (D30, D117, D175); a derived scalar lives on the stage's own mesh (D119). **A calibration's
  citation is read before it enters code** — rows fetched, counted, arithmetic checked (D175–D178) — and
  **say what fraction of a quantity it covers** (#84). **A number read before its row is ruled cannot
  become a row** (D113; #87). **Per-region determinism is the catalogue's contract** (D60); a second
  model must not rename a star. **Dead is the table's NaN** (D164, D178): nothing re-derives a lifetime.
- **Population numbers come from the field, not the sample**: light, magnitudes, Q, remnants and nebulae
  are history integrals along the isochrones (`photometry.steps_over`, `remnants.budget`; D177, D178).

## The API and the viewer
- `uv run python -m galaxy.api` serves the API and `interface/` on 127.0.0.1:8017 (`--client
  frontend/dist` for the built viewer); `Service().handle(path, query)` is what the tests drive. A new route
  is a `Route` in `service.ROUTES` **plus a `tools/timings.py` row**. Metadata never reaches the runner (D4).
- The viewer computes no physics (D5): colour is the declared ramp, light the published Σ_L times the
  pattern's contrast, dust the published A_V per line of sight. **What it invents today** (young light in
  the arms, a clump lattice, Hα knots) is RENDER_PHYSICS.md §0's dated exception, removed by V1–V3; ranking
  brightest-N by `star_magnitude_v` is owed to V1 (D177). The owner watches :5173 live: one consistent edit per file.

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. Every input has a
  default and every control a range. Every factual claim in every document is tagged `[verified: cite]`,
  `[recall]` or `[inferred]` (B14); a verified tag cites something in this repo or a named source.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill
  it (D33, D87); it still reports `fail`, never widen a target (B5); a miss that starts *passing* fails the
  run (#29) — remove it and **write down why**. `lo == hi` says "no testable target" (D100; rows 20, 21,
  25–28); a row whose source does not say what it measures names no field (D177). New rows from 32.

## What the instruments said on 2026-09-26, after S30 (D174–D179 hold the before/after)
- graph acyclic for both models (order: … sfh, chemistry_dtd, supernovae, light, vertical_alpha, population,
  ism, systems, formation, habitable_zone, planets); preflight OK, 7 of 12 controls; determinism reproducible
  across processes for both; spec **10 pass / 17 fail / 4 not-yet-computable of 31, identical in both models**;
  convergence 0 drifts; row 3 251.026 (#11); row 15 5.20971 (#80); row 29 −7.914; **rows 30 / 31 (SN rates)
  0.0176069 / 0.0065332 yr⁻¹, the Ia pass thin (#88)**; rows 25–28 n-y-c (#82).
- Regression numbers: z_f 1.66, c₂₀₀ 8.24, R_d 2.60486 (thin 2.44138), M_star 4.751e10, SFR 1.7551515,
  H 8.088e9, WIND_SPEED 860.3, MERGER_HEATING 88.8, `swing_x` 3.334; rows 16 / 17 medians 41.10 / 6.08;
  M_V −21.2159, B − V 0.6306, Υ_V 1.8468, disc_luminosity 4.8958e10, Q 1.6527e53 s⁻¹;
  **remnant_mass_fraction 0.214686, planetary_nebula_count 14 732, living + remnants = 0.836104 of the
  locked mass (#85)**; default catalogue 18 269 living / 1 589 WD / 113 NS / 19 BH.
- performance: basic ~1.5 s cold (light 0.40, population 0.17, systems 0.29, supernovae 0.07, habitable_zone
  0.06); region one sector ~0.49 s cold; timings re-published at S28 and S29 (D177, D178).
- Register: **36 open — 11 permanent, 25 carried — and 37 discharged** (#85–#87 at S29, #88–#90 at S30).

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
work in worktrees (main checkout on `main`), neither push nor write DECISIONS.md; two may run at once from one
`main`, merged in row order (D178); the orchestrator reads the core diff first, then closes.
