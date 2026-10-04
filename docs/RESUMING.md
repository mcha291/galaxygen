# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's board is the only record
of what is done (A9); this file is rewritten each session, capped at 120 lines (C3). **Every row is ☑ through S56: S0–S22
(§5d), S25–S42 (§5e), S43–S45, S46–S47 the viewer, S48 the bright catalogue, S49 the light tables, S50 the dust's layer
and the star-first mode (D205–D209), S51 the gas's own arm pattern (D210), S52 the dust heated in its own layer (D211), S53 BUILD_III adopted and its Phase 0 (D212), S54 the templates (D213), S55 the separation (D214, gate G1), S56 several arm modes (D215, three gate turns). Rows 57–66 are the third build's (`BUILD_III.md`, GALAXY_PLAN §5f): Opus leads, Fable at four gates and at a stop condition. `BRIEF.md` is S57's: Phase P2, gates G2 and G3, once the owner answers S56's question.**

## Open a session (rules C1, C2b)
```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```
Then RULES.md in full, BRIEF.md, **BUILD_III.md (the phase's text is its ruling)**; GALAXY_INPUTS.md by section (§11's head is the debt map).
Branch `session-NN`; commit and push at every sub-deliverable (C2b); in a worktree `git config --worktree core.hooksPath
tools/hooks`; LF newlines. **Numbers are sequential**: debts from #141, decisions from D216, board rows from 57,
acceptance rows from 38, taken when the entry is written.
## Layout (since 0f78156: docs/, model/galaxy/, frontend/; the import name is still `galaxy`)
```
docs/           RULES, this file, BRIEF, GALAXY_PLAN (board, §5e), GALAXY_INPUTS (§11 register), DECISIONS, LESSONS,
                MANUAL_TODO, BUILD_II (done), **BUILD_III (the plan in force, S53–S66)**, RENDER_PHYSICS (the contract), **VIEWER_TASKS (the list, S47)**, **RESEARCH_AREAS (S50)**, **READING_GAS_PATTERN (S51)**, **READING_NGC_4414 (S54: the blind windows; six unspent)**, **READING_ARM_MODES (S56: the observed mode spectra, a check)**, AUDIT_*.md (the
                _BLIND files hold the windows rows 32, 34 and 37 cite)
model/galaxy/core/    units (closed; grew at S28, S30, S31), special, cmaps, fielddoc (FieldDecl: optional, contract,
                provenance **derived | seeded | synthetic (S55), `composed` + `neutral`**; OBJECTS closed: system star planet belt moon cloud cluster remnant), stage (CHECKPOINTS 1–6;
                Stage.extends / extend()), registry (INPUTS: 7 controls + **5 seeds (`texture_seed`: the arm phases since S56)** + mergers; MODELS; IMPLEMENTATIONS), seeds, grids
model/galaxy/models/  level0 (constants), **azimuthal (default since S46, D197)**, basic · stages/ cp1 halo, disc, nucleus ·
                cp2 assembly · cp3 bar + pattern (**S56: the local swing window's mode amplitudes, `arm_saturation`; `arm_multiplicity` a label**) + **gas_pattern (S51; S56: the ridge by rank, #140)** · cp4 sfh, sfh_azimuthal, chemistry_dtd, supernovae, vertical_alpha, ism, light
                (Σ_L, colour, eight bands, Q), dust, stellar_halo · cp5 population + systems (the star columns; the cell
                hierarchy, MAX_LEVEL 3) + clouds (S32 census; `cloud_extinction_v`, S40) + clusters (S33; S41 `cluster_luminosity`,
                `cluster_light_temperature`) + nebular (S35: HII regions, Hα per volume, the DIG; **S42: the four forbidden
                lines per region off Byler's grid, per-ring lines, Hβ in both layers; S44: the grid on its own 8.93 and
                `nii_halpha_gradient_hii`, row 37**) + cluster_survival + globular_clusters (S34) + bubbles (S36) · cp6
                formation, habitable_zone, planets; massive_stars.py; remnants.py; photometry; **bright (S48: the luminosity function, `bright_stars`)**; spectra (S38–S39: the SED, the
                grain table, the filter integral, LINE_WAVELENGTHS in air; **S44: a curve's `wavelengths` air | vacuum,
                honoured by `line_response` through `air_to_vacuum`, Morton 1991**)
model/galaxy/layer/  **(S55: noise + vectors.json, compose — the one reader of the switch — and the layer stages cloud_texture and, S56, arm_phases)** · templates.py  **(S54: `milky_way`, `ngc_4414` as data; `resolve`; the fit's free set, bounds, checks)** · run.py   run(model, inputs, grid, only=…, resume=…, impls=…, **layer=True**) · data/ parsec_isochrones.npz (396 × 137 818 rows),
                **nebular_lines.npz (S42: FSPS `ZAU_ND_prsc.lines` at bd187a0d, six lines; `tools/fetch_nebular.py`)**
model/galaxy/specs/   graph, preflight, determinism, spec (rows 1–37; MISSES one ledger), **templates (S54: the five checks, `CHECK_MISSES`, apart from the rows)**, convergence, performance; api/: service
                (ROUTES; **S42 `/api/blackbody`; S54 `/api/templates`, `template=`; S55 `layer=off`, on every route that takes inputs**), http (**S42: a form-encoded POST is the GET with its query in the body**)
frontend/       Vite + React + three.js (`npm --prefix frontend run dev` on :5173); galaxy/ FieldVolume, RegionVolume + region.ts,
                regimes.ts, filters.json (rgb, sho, hoo), instruments.json (wfc3, wfc3n from SVO via `tools/fetch_filters.py`; vacuum
                since S44), psf.ts, colors.ts, **flux.ts + FluxPoints.tsx (S50)**; interface/transport.js the one fetch (POST past 4 KB); **e2e/ (S53: the picture test — captures.json, frames/, `npm run picture`, its own server on :8019)**
tests/          64 files (S56: test_modes and the frozen s55_patterns oracle; S53: test_goal_metrics, test_picture — no browser unless `GALAXYGEN_PICTURE=1`; S54: test_templates; **S55: test_layer (I1–I5, the S54 reference, `CENSUS_STATISTICS`), test_layer_noise**); every `model`-parametrised test runs per registered model (two); test_audit*.py (iv: S43's mesh) and
                each phase's file pin measurements; test_render the V1/V2 gates, the lines, instrument, blackbody and grain
                keys; test_region_synthesis the V3 gates (24 s); test_v4 the object columns (**30 drawn / 37 not, D192**);
                test_s45_diagnosis row 37's parts (Z′, the grid's responses, the frozen probes; D196)
tools/          progress (the board), bootstrap, verify_clone, timings, scaling, fetch_parsec, fetch_nebular, fetch_filters, **goal_metrics (S53: six statistics of a picture; Pillow, dev group only)**, **fit_template (S54: the bounded search over a template's free set)**
```
## Writing a stage
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a `FieldDecl` beside its
  compute (name, label, unit, kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero, provenance, about); `compute(ctx)`
  sees `ctx.grid`, `.inputs`, `.constants`, `.fields` / `.get()` and `.rng(seed, *path)`, returns exactly the declared names.
  Register with `IMPLEMENTATIONS.register`, import in `stages/__init__.py`, map the slot in the models; a constant goes in
  `level0.py` if more than one model reads it (D29, D85); a field nobody reads is dead (S41). **An about line must not
  name a constant** (D5). A new unit is a `core/units.py` edit plus a line in the decision (D177).
- **Two implementations of one slot** share one `FieldDecl.contract` (D86); if the second reads a seeded field for its
  own, **extend the first** (`extend(BASE, …)`, D176). **A stage requires only its own or an earlier checkpoint** (A1,
  D173). **One provenance per stage** (D55). **A seed binds at its earliest reader's checkpoint** (S17).
- A named ruleset is a constant with its alternative in the about, chosen before the row is read (D113); a mechanism is
  probed by substituting one function (D114); a default is measured or derived (D30, D117, D175). **A citation is read
  before it enters code** and **says what fraction it covers** (#84). **A number read before its row is ruled cannot
  become a row** (D113; #87); a number the model has printed gets only a blind or a disclosed row (#117, D192).
  **Per-region determinism is the catalogue's contract** (D60). **Dead is the table's NaN** (D164). **Population numbers
  come from the field** (D177). **An object column is drawn or says "Not drawn by the viewer"** (`NOT_DRAWN_WHY`, D191).

## The API and the viewer
- `uv run python -m galaxy.api` serves the API and `interface/` on 127.0.0.1:8017 (`--client frontend/dist` for the
  built viewer); `Service().handle(path, query)` is what the tests drive. A new route is a `Route` in `service.ROUTES`
  **plus a `tools/timings.py` row**. Metadata never reaches the runner (D4). `/api/region` and `/api/system` take
  `level=` 0–3 (D181); the census routes serve by window, every row named by `(cell, index)`, a level filter's header
  counting the body (D190); a catalogue stage's scalars ride in the header (D4, D148). **A form-encoded POST is the GET
  with the body appended to its query** (411 / 413 past 1 MiB / 415; nothing written; D192) — the transport switches
  past 4 KB, which WFC3's ≈ 20 KB of curves need.
- The viewer computes no physics and may evaluate only what the model publishes (D5 as amended, D212): the field regime's colour is the model's filter integral (`/api/render`,
  D188); nothing structural is invented at galaxy scale (D189); the region regime below 4 kpc marches the censuses
  from their published vectors (D190); the window's clusters are points of their own light (D191); **since S42 a point
  in "light" is L × the model's blackbody share at T over the white point's, from `/api/blackbody`** (P6, D192; the
  bolometric correction is still a blackbody's, #114 open), each resolved HII region is coloured by its own lines, and
  under `wfc3` / `wfc3n` the stars wear the Airy sprite (#120). Sets: rgb, sho, hoo, wfc3, wfc3n. :5173 is the owner's.

## Conventions (names `lower_snake`, constants `UPPER_SNAKE`; every claim tagged, B14)
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction that could kill it (D33,
  D87); it still reports `fail`, never widen a target (B5) — **a disclosed row's honest successor is a blind one**
  (D186 A3-7, D192); a miss that starts *passing* fails the run (#29) — remove it and **write down why** (row 34, S42).
  `lo == hi` says "no testable target" (D100; rows 20, 21, 25–28, 36); a row whose source does not say what it
  measures names no field (D177). New rows from 37.

## What the instruments said on 2026-10-04, after S56 (D174–D215 hold the before/after; **the rows are judged layer-off: 35 −2.081, 37 −0.1030, unmoved; layer on the galaxy has several arm modes since S56 — clouds 16 660, clusters 12 814, the gas's crest 3.06 at R₀**; the pictures' tables are in D212 and D213; `ngc_4414`: peak 239.18 km/s, 1.676 kpc, 3.905e10 M☉, five disclosed misses #132–#136)
- graph acyclic for both models; preflight OK, 7 of 12 controls; determinism reproducible for both; spec **12 pass /
  20 fail / 5 not-yet-computable of 37, identical** (row 34 green since S42 on the blind window; row 37 a miss, #117); convergence
  0 drifts; row 3 251.026 (#11); row 15 5.20971 (#80); row 29 −7.892; rows 30 / 31 0.0176069 / 0.0065332 yr⁻¹ (#88);
  rows 25–28, 36 n-y-c; rows 32 / 33 misses (#98, #99: 7.13e7 against 2.7–4.0e7; 3.0e9 against 4–7e8); row 34 1.6594e53
  in 1.3–3.9e53; row 35 −1.989 passes; **row 37 −0.1055 dex kpc⁻¹ against the blind [−0.045, −0.005] (S44; S51's redraw)**.
- Regression numbers: z_f 1.66, c₂₀₀ 8.24, R_d 2.60486 (thin 2.44138), M_star 4.751e10, SFR 1.7551515, H 8.088e9,
  WIND_SPEED 860.3, MERGER_HEATING 88.8, `swing_x` 3.334; rows 16 / 17 medians 41.10 / 6.08; **M_V −21.1102, B − V 0.5694,
  Υ_V 2.0356, disc_luminosity 4.5898e10, Q 1.6594e53 s⁻¹ (S49)**; remnant_mass_fraction 0.214686 (#85), PN count 14 732; T_d(R₀)
  **18.52 K, L_IR 1.2006e10 L☉, the infrared share 0.2616 (S52, the layered geometry)**, G₀(R₀) 2.64, q_PAH(R₀) 0.0908 (S31); **16 822 clouds** (S51), Mach median 6.5 (S32); **12 930 clusters**,
  ε 0.0206, ΣQ / young Q **1.0382** (S51); gc_survival 0.0250, gc mean 6.97e7 (#97), halo_stellar_mass 3.03e9 (S34); 12 930
  HII regions, R_S median 0.72 pc, n_e 194, log U −2.83, census/field 0.990, halpha_sfr_ratio 0.7124 (#100), DIG 0.30
  (S35); bubbles median 9 pc, 1 464 remnants, porosity(R₀) 0.029 (S51); render frame B − V 0.569495, M_V −21.110365;
  balance 0.999144 (S52); clusters' HII Hα / field **1.0140 / 0.9942**, √⟨L²⟩/⟨L⟩ 6.798 (S51), `cloud_extinction_v` 2.9696
  (S40); clusters' ΣL 0.2436 of the disc's (S51); a star's blackbody painting 1.15 / 1.09 / 1.04× its filter light (S48);
  **S44 (the grid on 8.93): Hα-weighted [O III]/Hα 0.756 (S51), [N II]/Hα 0.082, [S II] 0.053 + 0.041; 3.0 % at the +0.2 dex
  edge, 2.6 % at the age floor; WFC3 SHO on vacuum curves: Hα 0.945 F656N, [O III] 0.899 F502N, [S II] 0.958 / 0.863 F673N;
  56 tags on the remote.** Performance: basic ~2.8 s cold; render rgb 2.1 s cold, 6.9 MB; clusters 1.7 s; `/api/blackbody` 5 ms.
- Register: **78 open — 11 permanent, 67 carried — and 45 discharged** (#138–#140 at S56, D215: the law against the reading, the phases, the ranked ridge; #137 at S55: expected totals only until L1; #132–#136 at S54, D213; #129–#131 at S51; #128's first half applied at S52). **The gas pattern:** `gas_arm_contrast` 2.73, crest 3.07 / trough 0.53 at R₀, young stars' mean modulation 2.63 (1.78). `bright_star_limit` 33 788 L☉,
  3.35e6 stars > 10³ L☉; light at 10³: 26.3 % young / 18.8 % bright / 54.9 % unresolved; **a stale :8017 is stopped by PID before it serves new code**.

## Close a session (GALAXY_PLAN.md §5, in this order)
0. Tick the board — surface, model **actually used**, tag, date — then `uv run python tools/progress.py`, then `uv run
   pytest` once, quiet, **backgrounded with its exit status appended to its log**; the merge is gated on that line (D115, D120).
1. Append to DECISIONS.md, new rules to LESSONS.md tagged (its `Tags:` line is the closed set), **the cold timings as
   `tools/timings.py` prints them** when a stage's cost changes (B2); rewrite this file (≤ 120) and BRIEF.md (≤ 60).
2. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into main: …`; push both. **Then tag** (C2e,
   D193): `git tag -a s<NN> <sha> -m "S<N>: …"`, `git push origin s<NN>`, `git ls-remote --tags origin` read back, your
   MANUAL_TODO.md §1 row applied with the SHA; never force-push. Then `tools/verify_clone.py --ref main`.

A session that stops early closes **partially** (C2d): commit, push, BRIEF.md, ◐, no merge, no tag. Opus builders work in
worktrees on branches cut from the session's, own disjoint files, neither push nor write DECISIONS.md (D195); a row built
across Fable's limit leaves `docs/HANDOFF_S<NN>.md` for Fable to review, rule and delete at close (D190–D192).
