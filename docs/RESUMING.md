# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's board is the
only record of what is done (A9); this file is rewritten each session, capped at 120 lines (C3). **The
first build (S0–S22) closed; the second (S25–S41, `BUILD_II.md`, §5e) is open: S25–S31 closed on 2026-09-26
(S29 and S30 in parallel), S32–S34 the same day; S35 (Phase 9, nebular emission, **Fable**) is next.** Tag batch owed; S22 ◐.

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
debts from #100, decisions from D184, taken when the entry is written.

## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5e), GALAXY_INPUTS (§11 register), DECISIONS, LESSONS,
                MANUAL_TODO, BUILD_II (the phases), RENDER_PHYSICS (the contract), RENDER_PLAN (done), AUDIT_*.md
model/galaxy/core/    units (closed; grew at S28, S30, S31), special (i0 k0 erf expn), cmaps, fielddoc (FieldDecl:
                optional, contract, provenance; OBJECTS closed: system star planet belt moon **cloud**), stage (CHECKPOINTS 1 Halo & disc, 2 Assembly, 3 Pattern,
                4 Star formation & chemistry, 5 Systems, 6 Planets; Stage.extends / extend()), registry
                (INPUTS: 7 controls + 4 seeds + mergers; MODELS; IMPLEMENTATIONS), seeds, grids
model/galaxy/models/  level0 (constants), basic, azimuthal (BASIC's tuple, sfh -> sfh_azimuthal) · stages/ cp1 halo, disc, nucleus · cp2 assembly · cp3 bar + pattern · cp4 sfh, sfh_azimuthal
                (extends sfh), chemistry_dtd, supernovae (SN rates), vertical_alpha, ism (P, f_H₂, Σ_dust, A_V), light
                (Σ_L, colour, Hα, eight bands, Q(H⁰)), dust (τ_sca, E(B−V), g, Σ_abs, T_d, Σ_IR, G₀, q_PAH),
                **stellar_halo** (S34: debris over mergers[], BHG16 profile) ·
                cp5 population (IMF integrals, remnants, PN count) + systems (materialise: the star columns; **the
                cell hierarchy, MAX_LEVEL 3, canonical_cell**) + clouds (S32: the molecular census, of="cloud") +
                clusters (S33: one per cloud past embedded, of="cluster", ε derived) + **cluster_survival +
                globular_clusters** (S34: Lamers dissolution, gc_system_mass seeded on world_seed) · cp6 formation,
                habitable_zone, planets; massive_stars.py; remnants.py; photometry (population_light/_wind)
model/galaxy/data/    parsec_isochrones.npz (396 × 137 818 rows; U B V R I J H K, M_bol, present mass; fetch_parsec.py)
model/galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…)
model/galaxy/specs/   graph, preflight, determinism, spec (rows 1–31; modes pointwise / statistical /
                qualitative / sweep; MISSES one ledger), convergence, performance; api/: service (ROUTES)
frontend/       Vite + React + three.js (`npm --prefix frontend run dev` on :5173); rail and toggle from /api/stages
tests/          48 files; every `model`-parametrised test runs per registered model (two); test_audit*.py,
                test_s22/s25/s26_rulings and each phase's file (…, clouds, hierarchy, clusters, **globular_clusters**) pin measurements
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
- **Population numbers come from the field, not the sample** (`photometry.steps_over`, `remnants.budget`; D177, D178).

## The API and the viewer
- `uv run python -m galaxy.api` serves the API and `interface/` on 127.0.0.1:8017 (`--client
  frontend/dist` for the built viewer); `Service().handle(path, query)` is what the tests drive. A new route
  is a `Route` in `service.ROUTES` **plus a `tools/timings.py` row**. Metadata never reaches the runner (D4).
  `/api/region` and `/api/system` take `level=` 0–3 (a child holds its parent's stars plus its own, D181); `/api/clouds`,
  `/api/clusters` serve the censuses by window; a catalogue stage's scalars ride in the header (rule D4, D148).
- The viewer computes no physics (D5): colour is the declared ramp, light Σ_L × the pattern's contrast, dust A_V per
  line of sight. **What it invents today** (young light in the arms, a clump lattice, Hα knots) is RENDER_PHYSICS.md
  §0's dated exception, removed by V1–V3 (brightest-N by `star_magnitude_v` owed to V1, D177). The owner watches :5173 live.

## Conventions
- Names `lower_snake`, constants `UPPER_SNAKE`; every input a default, every control a range. Every factual claim
  in every document is tagged `[verified: cite]`, `[recall]` or `[inferred]` (B14), a verified tag citing a source.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill
  it (D33, D87); it still reports `fail`, never widen a target (B5); a miss that starts *passing* fails the
  run (#29) — remove it and **write down why**. `lo == hi` says "no testable target" (D100; rows 20, 21,
  25–28); a row whose source does not say what it measures names no field (D177). New rows from 34.

## What the instruments said on 2026-09-26, after S34 (D174–D183 hold the before/after)
- graph acyclic for both models (order: … sfh, chemistry_dtd, stellar_halo, supernovae, light, vertical_alpha,
  cluster_survival, population, ism, globular_clusters, systems, …, clouds, planets, clusters); preflight OK, 7 of 12
  controls; determinism reproducible for both; spec **10 pass / 19 fail / 4 not-yet-computable of 33, identical in both**;
  convergence 0 drifts; row 3 251.026 (#11); row 15 5.20971 (#80); row 29 −7.914; **rows 30 / 31 (SN rates)
  0.0176069 / 0.0065332 yr⁻¹, the Ia pass thin (#88)**; rows 25–28 n-y-c (#82); **rows 32 / 33 misses (#98, #99)**.
- Regression numbers: z_f 1.66, c₂₀₀ 8.24, R_d 2.60486 (thin 2.44138), M_star 4.751e10, SFR 1.7551515, H 8.088e9,
  WIND_SPEED 860.3, MERGER_HEATING 88.8, `swing_x` 3.334; rows 16 / 17 medians 41.10 / 6.08;
  M_V −21.2159, B − V 0.6306, Υ_V 1.8468, disc_luminosity 4.8958e10, Q 1.6527e53 s⁻¹;
  remnant_mass_fraction 0.214686 (living + remnants 0.836104 of the locked mass, #85), PN count 14 732; **T_d(R₀)
  19.54 K, L_IR 1.622e10 L☉, G₀(R₀) 2.64, q_PAH(R₀) 0.0908 (S31); **16 704 clouds, mass in clouds 1.037 of the
  molecular mass (noise 0.035), Mach median 6.5 (S32); 12 860 clusters, ε 0.0206, ΣQ / young Q 1.0088,
  bound_cluster_mass_total 2.79e9 (S33); gc_survival 0.0250, gc mean 6.97e7 = +0.26 dex from η M_halo but 53% under
  1 Gyr (#97), metal-poor share 0.643, halo_stellar_mass 3.03e9 (S34)**; the level-0 catalogue bit-identical.
- performance: basic ~1.7 s cold (light 0.55, systems 0.37, clouds 0.27, population 0.20, clusters 0.13); region
  one sector 0.6 s cold, clouds whole disc 0.82 s, clusters one sector 1.06 s (the wind table's build); timings at S33 (D182).
- Register: **45 open — 11 permanent, 34 carried — and 37 discharged** (#94–#95 S32, #96–#97 S33, #98–#99 S34).

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

A session that stops early closes **partially** (C2d): commit, push, BRIEF.md, ◐, no merge. Opus subagents work in
worktrees (main checkout on `main`), neither push nor write DECISIONS.md; two may run at once (D178); the orchestrator reads the core diff first.
