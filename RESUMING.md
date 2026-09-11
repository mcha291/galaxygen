# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The build is closed** (S0–S20; §5d plans S21–S22).

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
galaxy/models/  level0 (shared constants; MERGER_HEATING 88.8 derived, S20), simple (+NET_YIELD),
                advanced (yields, DTD, wind)
galaxy/stages/  cp1 halo (NFW, budget, R_d, the contraction on its own mesh; the angular-momentum
                distribution's two ends — the high-j tail S16, the spheroid S17) + disc (κ(R), the
                basis-free solver) + nucleus (M_•, seeded); cp2 assembly (delivery, σ_z by birth time,
                the radial spread); cp3 sfh (infall = exponential + tail, less the spheroid; **the first
                episode's arrival law is one function, `first_infall`, substitutable for a probe**, S20;
                Kennicutt's threshold off κ; the stars moved through the spread), chemistry — the
                migration kernel lives here: transport / transport_columns / migration_width /
                age_bin_edges, read by chemistry_dtd and by systems (A9) — / chemistry_dtd, vertical /
                vertical_alpha (publish `birth_population`); cp4 pattern; cp5 systems; cp6 planets.
galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…);  galaxy/specs/: graph, preflight,
                determinism, spec (misses D87; "no testable target" D100; median D109), convergence
                (D94, D101), performance (D95, D101)
galaxy/api/     service (routes), wire, version, http; client/ (the viewer; every published field
                previewed in both models, S19).  tools/: progress, bootstrap, verify_clone, timings,
                scaling, shot, hooks/.  AUDIT_RUN1/2.md are main's S10 lists (D97, D102)
tests/          test_audit.py is the S10 audits as tests plus S20's three probes (the first infall
                substituted by monkeypatch; the plateau spike; the kick's derivation); S14–S18's end
                in test_halo / test_sfh / test_vertical, S19's gates in test_systems
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
  (D113); a mechanism is probed by substituting one function per half from a script, the repo unchanged
  (D114; `sfh.first_infall` is the point for the infall law, `replace(Stage, compute=…)` with
  `run(..., impls=)` for a whole stage, S16/S20); a default is measured or derived by a test (D30,
  D117, D128); a derived scalar lives on the stage's own mesh, never the grid (D119). A quantity two
  stages read is published once by the stage that owns it (S18), and so is a criterion (S19).
- **A calibration's arithmetic is derived, not just its value** (S20): `MERGER_HEATING` is the thick
  disc's cited σ_W net of what the assembly stage already composes with it, at the fixed point.
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
  `tools/progress.py` counts them — add an item, never a count.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, A7) with its model, debt,
  reason and a prediction that could kill it (D33, D87); it still reports `fail`, never widen a target
  (B5), and a miss that starts *passing* fails the run (#29) — remove it and **write down why it
  passed** (S20 row 7: the constant, not the shape). `lo == hi` says "no testable target" (D100).

## What the instruments said at S20 close (2026-09-11)
- graph: acyclic, both models. preflight OK: 0 UNSET. determinism OK, reproducible across processes.
- spec: simple **10 pass, 12 fail, 2 n-y-c** (row 7 in at 962, row 3 out at 251.03 — both on the
  re-derived kick); advanced **8 pass, 15 fail, 1 n-y-c** (row 3). Every miss has its debt and a
  prediction; the advanced rows 5, 7–11 and 24 carry D128's replacement prediction.
- Numbers, to spot a regression by. Unmoved from S19: z_f 1.66, c₂₀₀ 8.24, R_d 2.605, M_star 4.75e10,
  SFR 1.755, H 8.09e9, Σ_crit(R₀) 11.5, WIND_SPEED 860.3, NET_YIELD 0.01376, feh_spread_sun 0.360,
  rows 16/17/18 42.8 / 5.70 / 1.97e7. **Moved by S20** (S19's value in brackets): MERGER_HEATING
  88.8 (120); the thick disc's σ_z 35.0 (40.4); the radial spread at R₀ **1.09** kpc (1.47), 0.22
  at 2 kpc (0.30); row 7 **962** (1279); row 3 **251.03** (250.96); row 5 1.09 (1.17); row 9 0.0455
  (0.051); row 8 0.016 (0.013); the advanced row 6 356 (373); the merger-share sweep of row 9 0.131 /
  0.083 / 0.0455 / 0.019 / 0.005 / 0.001 against row 11 unmoved.
- **The valley** (D128): `single` at N_t 1000 / 2000 / 4000; the first infall on 0.1/H(z_f) reads dip
  0.151 at all three; every `bimodal_wide` the detector has reported is the +0.45 plateau spike.
- Convergence: 0 drifts on N_R, N_t, N_z; advanced rows 5, 7–11 `vacuous` (#27). Timings and the
  profile: D129 (the catalogue is still the costliest stage, D127). Register: 32 open, 18 discharged.

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
