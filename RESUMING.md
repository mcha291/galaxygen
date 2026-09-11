# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The build is closed** (S0–S20; §5d plans S21–S22). **This copy
is `session-21-a`'s** — Audit II, aim (a), a sealed branch S22 ports (D99, D130); `main`'s RESUMING
is S20's and says the same about the model, because this branch changed no physics.

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
galaxy/models/  level0 (shared constants; MERGER_HEATING 88.8 derived, S20 — its citation read at
                S21 (a): an adopted 35, the measurement 39 ± 4, A-14), simple (+NET_YIELD),
                advanced (yields, DTD, wind)
galaxy/stages/  cp1 halo (NFW, budget, R_d, the contraction on its own mesh; the angular-momentum
                distribution's two ends — the high-j tail S16, the spheroid S17; `angular_momentum_core`
                is the substitution point for a buckled bulge, S21) + disc (κ(R), the basis-free solver)
                + nucleus (M_•, seeded); cp2 assembly (delivery, σ_z by birth time, the radial spread);
                cp3 sfh (infall = exponential + tail, less the spheroid; `first_infall`, `star_formation_rate`,
                `toomre_threshold` and `radial_transport` are each one function a probe substitutes,
                S20/S21; the stars moved through the spread), chemistry — the migration kernel lives
                here: transport / transport_columns / migration_width / age_bin_edges, read by
                chemistry_dtd and by systems (A9) — / chemistry_dtd, vertical / vertical_alpha (publish
                `birth_population`); cp4 pattern; cp5 systems; cp6 planets.
galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…);  galaxy/specs/: graph, preflight,
                determinism, spec (misses D87; "no testable target" D100; median D109), convergence
                (D94, D101), performance (D95, D101)
galaxy/api/     service (routes), wire, version, http; client/ (the viewer; every published field
                previewed in both models, S19).  tools/: progress, bootstrap, verify_clone, timings,
                scaling, shot, hooks/.  AUDIT_RUN1/2.md are S10's lists; AUDIT_II_A.md is S21 (a)'s
tests/          test_audit.py is the S10 audits as tests plus S20's three probes; **test_audit_ii_a.py
                is S21 (a)** — twelve probes, each a substituted function, each pinning AUDIT_II_A.md's
                number; S14–S18's end in test_halo / test_sfh / test_vertical, S19's gates in test_systems
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
  hypothesis** (S17). A stage reading a seed publishes *seeded* fields, all of them (D55).
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read
  (D113); a mechanism is probed by substituting one function from a script or a test, the repo
  unchanged (D114, D128, D130); a default is measured or derived by a test (D30, D117, D128); a derived
  scalar lives on the stage's own mesh, never the grid (D119). A quantity two stages read is published
  once by the stage that owns it (S18), and so is a criterion (S19).
- **A prediction is run as written, with the knob it names, and its pre-committed reading is the
  ruling when it fails** (S20, S21): the register's entries since S13 each carry a verdict and a
  number now (AUDIT_II_A.md §1); a killed prediction's replacement sits beside the old one in `spec.py`.
- **Per-region determinism is the catalogue's contract** (D60): nothing in `materialise` may depend on
  which cells were asked for (S19).

## The API and the viewer
- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path, query)` is the
  same without a socket and is what the tests drive; `model=advanced` selects the second model on every
  route. A new route is a `Route` in `service.ROUTES` plus **a row in `tools/timings.py`**.
- Metadata answers from declarations and must not reach the runner; whatever computes goes through
  `Service.compute(...)` (D4, D63); objects are materialised per request (D82). `transport.js` holds
  **the only `fetch`**; the gate asks `git ls-files` what the repository contains (D101).

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. 7 controls, 4
  seeds, `mergers`; every input has a default and every control a range. Every factual claim in every
  document is tagged `[verified: cite]`, `[recall]` or `[inferred]` (B14). A new unit, kind, axis,
  object class or cmap is a `core/` edit plus a DECISIONS.md entry. Debts live in GALAXY_INPUTS §11;
  `tools/progress.py` counts them — add an item, never a count. Paired runs use reserved numbers.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, A7) with its model, debt,
  reason and a prediction that could kill it (D33, D87); it still reports `fail`, never widen a target
  (B5), and a miss that starts *passing* fails the run (#29) — remove it and **write down why it
  passed**. `lo == hi` says "no testable target" (D100).

## What the instruments said at S21 (a) close (2026-09-11) — the model as S20 left it
- graph: acyclic, both models. preflight OK: 0 UNSET. determinism OK, reproducible across processes.
- spec: simple **10 pass, 12 fail, 2 n-y-c**; advanced **8 pass, 15 fail, 1 n-y-c**. Every miss has its
  debt and a prediction, and every prediction since S13 has now been run (D130).
- Numbers, to spot a regression by: z_f 1.66, c₂₀₀ 8.24, R_d 2.441 (fitted; spin 2.605), M_star 4.75e10,
  SFR 1.755, H 8.09e9, Σ_crit(R₀) 11.5, WIND_SPEED 860.3, NET_YIELD 0.01376, feh_spread_sun 0.360,
  MERGER_HEATING 88.8, the radial spread at R₀ 1.09 kpc, row 3 251.03, row 7 962, row 5 1.09, row 9
  0.0455, the advanced row 6 356, rows 16/17/18 42.8 / 5.70 / 1.97e7 (on seeds 0–40; 41.1 / 5.94 /
  2.68e7 on 41–81, debt #51).
- **What the audit read** (AUDIT_II_A.md): both kernels on the mass — row 9 0.266, row 4 3.49, row 3
  244.9; the bar's 7e9 — row 3 249.6, row 14 144; the burst inside the α-fall — a mode at +0.35 holding
  0.10; the cut-only law — rows 8–11 together, row 5 1.61; the diagonal's median residual −0.577σ;
  the advanced row 22 blind to the inner 4 kpc (−0.0699); σ_W = 39 reads row 7 at 1193.
- Convergence: 0 drifts on N_R, N_t, N_z; advanced rows 5, 7–11 `vacuous` (#27). Timings and the
  profile: D131 (0.69 / 1.00 s cold; the catalogue and `chemistry_dtd` the costliest, as at S20).
  Register: 34 open, 18 discharged.

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
   **An audit branch (S21 a/b) skips step 2's merge**: push the branch, S22 ports it (D99).

A session that stops early closes **partially** (C2d): commit, push, write what remains into
BRIEF.md, mark the row ◐, do **not** merge. Credentials: the helper or a repo-scoped token; no tags (C2e).
