# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's board is the
only record of what is done (A9); this file is rewritten each session, capped at 120 lines (C3). **The
first build (S0–S22) closed; the second (S25–S41, `BUILD_II.md`, §5e) is open: S25–S39 closed by 2026-09-27; S40
(V3: Fable's rulings, Opus's build across a usage limit) closed 2026-09-30 (D190). S41 (V4) and S42 are BUILT on
Opus on `session-41` / `session-42` (stacked, unmerged; `docs/HANDOFF_S41.md`, `HANDOFF_S42.md`) and wait on
Fable's review, rulings and close, in row order.** Owner owes: the FSPS grid (D184), rows 32/34's blind windows
(D186), filter files (D188), the tag batch. S22 ◐.

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
debts from #114, decisions from D191, taken when the entry is written.

## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5e), GALAXY_INPUTS (§11 register), DECISIONS, LESSONS,
                MANUAL_TODO, BUILD_II (the phases), RENDER_PHYSICS (the contract), RENDER_PLAN (done), AUDIT_*.md
model/galaxy/core/    units (closed; grew at S28, S30, S31), special, cmaps, fielddoc (FieldDecl: optional, contract,
                provenance; OBJECTS closed: system star planet belt moon cloud cluster remnant), stage (CHECKPOINTS 1–6;
                Stage.extends / extend()), registry (INPUTS: 7 controls + 4 seeds + mergers; MODELS; IMPLEMENTATIONS), seeds, grids
model/galaxy/models/  level0 (constants), basic, azimuthal (BASIC's tuple, sfh -> sfh_azimuthal) · stages/ cp1 halo, disc, nucleus ·
                cp2 assembly · cp3 bar + pattern · cp4 sfh, sfh_azimuthal, chemistry_dtd, supernovae, vertical_alpha, ism, light
                (Σ_L, colour, Hα, eight bands, Q), dust, stellar_halo · cp5 population + systems (the star columns; the cell
                hierarchy, MAX_LEVEL 3) + clouds (S32 census; **S40: `cloud_extinction_v` 2.9696 mag, one scalar**) + clusters
                (S33) + nebular (S35: HII regions, Hα per volume, the DIG) + cluster_survival + globular_clusters (S34) + bubbles
                (S36: Weaver bubbles, the remnant census, porosity) · cp6 formation, habitable_zone, planets; massive_stars.py;
                remnants.py; photometry; spectra (S38–S39: the SED, the grain table, the filter integral)
model/galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…) · data/ parsec_isochrones.npz (396 × 137 818 rows)
model/galaxy/specs/   graph, preflight, determinism, spec (rows 1–31; MISSES one ledger), convergence, performance; api/: service (ROUTES)
frontend/       Vite + React + three.js (`npm --prefix frontend run dev` on :5173); galaxy/ FieldVolume (the field's march),
                **RegionVolume + region.ts (S40: the region regime's march, levelFor, the seeded noise)**, regimes.ts, filters.json
tests/          53 files; every `model`-parametrised test runs per registered model (two); test_audit*.py and each phase's
                file pin measurements; test_render the V1 and V2 gates; **test_region_synthesis the V3 gates (24 s)**
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
- **Two implementations of one slot.** Shared fields carry one `FieldDecl.contract` (D86); if the second reads a
  seeded field for its own field, **extend the first** (`extend(BASE, …)`, D176); `requires_optional` + `ctx.fields.get`.
- **A stage may only require fields from its own or an earlier checkpoint** (A1 as rewritten at S25, D173); the
  pattern is checkpoint 3, star formation 4. **A stage has one provenance** (D55): reading a seeded column seeds all it publishes.
  **A seed binds at the checkpoint of its earliest reader**, which `graph` requires to equal the input's `checkpoint_hypothesis` (S17).
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read (D113); a
  mechanism is probed by substituting one function (D114); a default is measured or derived (D30, D117, D175). **A calibration's
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
  `/api/clusters`, `/api/remnants` serve the censuses by window — **since S40 every row carries `cell` and `index`
  (its name, the seed of its interior) and a level filter's header counts the rows kept** (a defect since S32, D190);
  a catalogue stage's scalars ride in the header (rule D4, D148).
- The viewer computes no physics (D5): colour is the declared ramp; **since S38 the field regime's colour is the model's
  filter integral** (`/api/render`, option (a), D188); **since S39 nothing structural is invented at galaxy scale** (D189);
  **since S40 the region regime below 4 kpc marches the censuses' objects from their published vectors** — the level
  from the view's width, seeded log-normal cloud interiors with cavity and pillars, HII spheres, bubble and remnant
  shells, the field's HII fading inside the window (D190; its four stated departures #110–#113). The owner watches :5173 live.

## Conventions (names `lower_snake`, constants `UPPER_SNAKE`; every claim tagged, B14)
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill
  it (D33, D87); it still reports `fail`, never widen a target (B5); a miss that starts *passing* fails the
  run (#29) — remove it and **write down why**. `lo == hi` says "no testable target" (D100; rows 20, 21,
  25–28, 36); a row whose source does not say what it measures names no field (D177). New rows from 37.

## What the instruments said on 2026-09-30, after S40 (D174–D190 hold the before/after)
- graph acyclic for both models; preflight OK, 7 of 12 controls; determinism reproducible for both; spec **11 pass /
  20 fail / 5 not-yet-computable of 36, identical**; convergence 0 drifts; row 3 251.026 (#11); row 15 5.20971 (#80);
  row 29 −7.914; rows 30 / 31 0.0176069 / 0.0065332 yr⁻¹, the Ia pass thin (#88); rows 25–28, 36 n-y-c; rows 32–34
  misses (#98–#100); row 35 −2.008 passes.
- Regression numbers: z_f 1.66, c₂₀₀ 8.24, R_d 2.60486 (thin 2.44138), M_star 4.751e10, SFR 1.7551515, H 8.088e9,
  WIND_SPEED 860.3, MERGER_HEATING 88.8, `swing_x` 3.334; rows 16 / 17 medians 41.10 / 6.08; M_V −21.2159, B − V 0.6306,
  Υ_V 1.8468, disc_luminosity 4.8958e10, Q 1.6527e53 s⁻¹; remnant_mass_fraction 0.214686 (living + remnants 0.836104, #85),
  PN count 14 732; T_d(R₀) 19.54 K, L_IR 1.622e10 L☉, G₀(R₀) 2.64, q_PAH(R₀) 0.0908 (S31); 16 704 clouds, mass in clouds
  1.037 of the molecular mass, Mach median 6.5 (S32); 12 860 clusters, ε 0.0206, ΣQ / young Q 1.0088, bound_cluster_mass_total
  2.79e9 (S33); gc_survival 0.0250, gc mean 6.97e7 (#97), metal-poor share 0.643, halo_stellar_mass 3.03e9 (S34); 12 860 HII
  regions, R_S median 0.72 pc, n_e 194, log U −2.83, census/field 0.990, halpha_sfr_ratio 0.7095, DIG 0.30 (S35); bubbles
  median 9 pc, 12 521 of 12 860 stalled, 1 464 remnants, porosity(R₀) 0.033 (S36); zone peak 6.6 kpc, GC mean +0.34 dex from
  measured η (S38 fixes); render frame B − V 0.630641, M_V −21.216042 (S38); frame balance 0.999321, profile worst ring
  9.2e-4 (S39); **clusters' HII Hα / field 0.9801 (disc) and 0.9744 (level-1 sector); √⟨L²⟩/⟨L⟩ 6.898, sixty level-1 windows
  z mean +0.15, sd 1.16; `cloud_extinction_v` 2.9696; a census identical at levels 0–3 (S40)**.
- performance: basic ~2.8 s cold; render whole rgb 1.9 s cold, 5.2 MB; clusters whole disc 1.4 s cold, 3.5 MB (D190).
- Register: **56 open — 11 permanent, 45 carried — and 40 discharged** (#107–#108 V1; #109 V2; #110–#113 V3, D190).

## Close a session (GALAXY_PLAN.md §5, in this order)
0. Tick the board — surface, model **actually used**, tag, date — then `uv run python tools/progress.py`, then
   `uv run pytest` once, quiet, **backgrounded with its exit status appended to its log** (it outlasts the tool's
   cap), the merge gated on that line (D115, D120).
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **the cold timings as `tools/timings.py` prints them**
   when a stage's cost changes (B2); rewrite this file (≤ 120) and BRIEF.md (≤ 60) for the next row of §5e.
2. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into main: …`; push both.
   **Do not tag** (C2e): add your MANUAL_TODO.md row with the last session's merge SHA filled in; never
   force-push. Then `uv run python tools/verify_clone.py --ref main`.

A session that stops early closes **partially** (C2d): commit, push, BRIEF.md, ◐, no merge. Opus subagents work in
worktrees (main checkout on `main`), neither push nor write DECISIONS.md; two may run at once (D178); the orchestrator reads
the core diff first. **A row built on Opus across Fable's limit** (S40–S42) leaves a `docs/HANDOFF_S<NN>.md`: Fable
reviews, rules in the decision, deletes the file at close; `session-41` and `-42` are stacked — merge `main` into each before its close.
