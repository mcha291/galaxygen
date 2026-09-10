# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The build is closed** (S0–S19; §5d plans S20–S22).

## Open a session (rules C1, C2b)
```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```
Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section. Branch `session-NN`; commit
and push at every sub-deliverable (C2b). In a worktree: `git config --worktree core.hooksPath
tools/hooks`. Write files with `newline="\n"`: CRLF breaks progress.py's line regexes.

## Layout
```
galaxy/core/    units (32 closed), cmaps (8 + stops, A9), fielddoc (FieldDecl, 6 Kinds, Ramp/Palette,
                AXES), stage (Stage, Context, CHECKPOINTS), registry (12 INPUTS, MODELS,
                IMPLEMENTATIONS), seeds, grids, special (I1, K0, K1, erf)
galaxy/models/  level0 (shared constants), simple (+NET_YIELD), advanced (yields, DTD, wind)
galaxy/stages/  cp1 halo (NFW, budget, R_d, the contraction on its own mesh; ρ_DM and the contracted
                fit; the angular-momentum distribution's two ends — the high-j tail S16, the spheroid
                S17) + disc (κ(R), the basis-free solver) + nucleus (M_•, seeded); cp2 assembly
                (delivery, σ_z by birth time, the radial spread); cp3 sfh (infall = exponential + tail,
                less the spheroid; Kennicutt's threshold off κ; the stars moved through the spread),
                chemistry — **the migration kernel lives here**: transport / transport_columns /
                migration_width / age_bin_edges, read by chemistry_dtd and by systems (A9) — /
                chemistry_dtd, vertical / vertical_alpha (publish `birth_population`, the criterion
                itself, S19); cp4 pattern; cp5 systems (`Churn` draws birth radius *and* time from
                the backward weights, S19); cp6 planets.
galaxy/run.py   run(model, inputs, grid, only=…, resume=…);  galaxy/specs/: graph, preflight,
                determinism, spec (misses D87; "no testable target" D100; median D109), convergence
                (D94, D101), performance (D95, D101)
galaxy/api/     service (routes), wire, version, http; client/ (the viewer; `paintOf` picks ramp or
                palette from the declaration, S19).  tools/: progress, bootstrap, verify_clone,
                timings, scaling, shot, hooks/.  AUDIT_RUN1/2.md are main's S10 lists (D97, D102)
tests/          test_audit.py is the S10 audits as tests (#12, #17, #21, #26–#28, #41–#45), S14–S18's
                end in test_halo / test_sfh / test_vertical, S19's gates in test_systems
```
## Writing a stage
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a `FieldDecl`
  beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero,
  provenance, about. `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or
  `.get()` / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked. Register with
  `IMPLEMENTATIONS.register(...)`, import in `stages/__init__.py`, map the slot in the models that use
  it; a constant goes in `level0.py` if both models read it (D29, D85); a field nobody reads is dead
  (#30). **Two implementations of one slot** publish the same names under the same contract
  (`FieldDecl.contract`) and their own as `optional=True`, read via `requires_optional` (D86).
- **A seed binds at the checkpoint of its earliest reader and `graph` requires that to equal §3's
  hypothesis** (S17). A stage reading a seed publishes *seeded* fields, all of them: split the derived
  half into its own stage rather than mislabel it (D55, `bar`/`pattern`, `halo`/`nucleus`).
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read
  (D113); a mechanism is probed by substituting one function per half from a script, the repo unchanged
  (D114) — or a stage's whole compute, set on the Stage, not the module (S16); a default is measured or
  derived by a test (D30, D117); a derived scalar lives on the stage's own mesh, never the grid (D119).
  A quantity two stages read is published once by the stage that owns it (`epicyclic_frequency`,
  `stars_formed_history`, S18) — and so is a **criterion** two stages apply (`birth_population`, S19:
  the catalogue's copy silently disagreed in the advanced model).
- **Per-region determinism is the catalogue's contract** (D60): nothing in `materialise` may depend on
  which cells were asked for. Narrowing the churn to a region's own rings moved the last bit of a star's
  age — BLAS sums a 1-column product differently — so it is done for every ring (S19).

## The API and the viewer
- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path, query)` is the
  same without a socket and is what the tests drive; `model=advanced` selects the second model on every
  route. A new route is a `Route` in `service.ROUTES` plus **a row in `tools/timings.py`**.
- Metadata answers from declarations and must not reach the runner; whatever computes goes through
  `Service.compute(...)`, the closure above the fields asked for (D4, D63); objects are materialised per
  request (D82). `transport.js` holds **the only `fetch`**; the gate asks `git ls-files` what the
  repository contains (D101). No about line names a constant (D5).
- Every published field reaches the viewer, in both models, asserted in `tests/js/render.test.mjs` (S19)
  — bar a catalogue stage's own scalars, which the region census reports instead (D4).

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. 7 controls, 4
  seeds, `mergers`; every input has a default and every control a range. Every factual claim in every
  document is tagged `[verified: cite]`, `[recall]` or `[inferred]` (B14); a bare verified tag fails a
  test. A new unit, kind, axis, object class or cmap is a `core/` edit plus a DECISIONS.md entry. Debts
  live in GALAXY_INPUTS §11; `tools/progress.py` counts them — add an item, never a count.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, A7) with its model, debt,
  reason and a prediction that could kill it (D33, D87); it still reports `fail`, never widen a target
  (B5), and a miss that starts *passing* fails the run (#29) — remove it and **write down why it
  passed** (S17 row 2; S18 row 3, on the kick and the solver, not the bar). `lo == hi` says "no testable
  target" (D100); off that list is a citation with an uncertainty (D122).

## What the instruments said at S19 close (2026-09-10)
- graph: acyclic, both models; the disc runs before assembly (it reads the curve). preflight
  OK: 0 UNSET. determinism OK, reproducible across processes (two hash seeds). No input unbound.
- spec: simple **10 pass, 12 fail, 2 n-y-c**; advanced **9 pass, 14 fail, 1 n-y-c** — unchanged
  from S18 in every row. **No acceptance row reads the catalogue**, which is why S19 moved none.
- Numbers, to spot a regression by. **Every number upstream of the catalogue is D124's, unmoved**:
  z_f 1.66, c₂₀₀ 8.24, R_d 2.605, M_star 4.75e10, SFR 1.755, H 8.09e9, Σ_crit(R₀) 11.5, v_tan 250.96,
  WIND_SPEED 860.3, NET_YIELD 0.01376, rows 16/17/18 42.8 / 5.70 / 1.97e7, feh_spread_sun **0.360**.
- **Moved by S19, all inside the catalogue**, S18's value in brackets: the [Fe/H] spread at R₀
  **0.361** advanced (0.299) and 0.277 simple (0.333); R₀ mean age **7.31** Gyr (5.72 / 6.01); R₀
  [Fe/H] mean −0.249 / −0.180 (−0.330 / −0.272); R₀ thick fraction **0.221** simple (0.049), the
  whole-catalogue fraction unmoved at 0.254; mean birth radius at R₀ **5.4 kpc**, 84% born inside;
  metal-rich share 0.0031 (0.005); giant_fraction_sample 0.0169 / 0.0136 (0.0192 / 0.0122).
- **Convergence**: 0 drifts on N_R, N_t, N_z; advanced rows 5, 7–11 `vacuous` (#27). **Profile**
  (D127): the catalogue is the costliest stage, its cost fixed per cell not per star (D24).
  **Register**: 32 open, 18 discharged. Audit branches stay unmerged.

## Close a session (GALAXY_PLAN.md §5, in this order)
0. Tick the board — surface, model **actually used**, tag, date — then `uv run python
   tools/progress.py`, then `uv run pytest` once, quiet, **backgrounded with its exit status
   appended to its log** (it outlasts the tool's cap), the merge gated on that status (D115, D120).
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **publish the cold timings** (B2), the
   profile (D95) and, when a stage's cost changes, `tools/scaling.py`; then rewrite this file in
   place (≤ 120 lines) and write BRIEF.md (≤ 60 lines).
2. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into main: …`;
   push both. **Do not tag** (C2e) — add your MANUAL_TODO.md row with the last session's merge SHA
   filled in, and never force-push. Then `uv run python tools/verify_clone.py --ref main`, which
   clones fresh, bootstraps and runs the suite and the specs there; it refuses on a dirty tree.

A session that stops early closes **partially** (C2d): commit, push, write what remains into
BRIEF.md, mark the row ◐, do **not** merge. **Credentials:** the helper or a repo-scoped token;
never push a tag (C2e).
