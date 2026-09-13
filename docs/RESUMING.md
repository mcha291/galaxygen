# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The build is closed and S0–S22 are spent.** What is owed is
one command that no session can run: the tag batch in MANUAL_TODO.md, from a desktop (D161).

## Open a session (rules C1, C2b)
```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```
Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section — §11's head is the debt
map and is the fastest way in. Branch `session-NN`; commit and push at every sub-deliverable
(C2b). In a worktree: `git config --worktree core.hooksPath tools/hooks`. Write files with
`newline="\n"`: CRLF breaks progress.py's line regexes.

## Layout
```
galaxy/core/    units (32 closed), cmaps (8 + stops, A9), fielddoc (FieldDecl, 6 Kinds, Ramp/Palette,
                AXES), stage (Stage, Context, CHECKPOINTS), registry (12 INPUTS, MODELS,
                IMPLEMENTATIONS), seeds, grids (**its docstring is what the default mesh is sized
                for**, S22, #36), special (I1, K0, K1, erf)
galaxy/models/  level0 (shared constants; MERGER_HEATING 88.8, with its named alternative 112.3 in
                the about line — B12, S22), simple (+NET_YIELD), advanced (yields, DTD, wind)
galaxy/stages/  cp1 halo (NFW, budget, R_d, the contraction on its own mesh; the angular-momentum
                distribution's two ends — the high-j tail S16, the spheroid S17) + disc (κ(R), the
                basis-free solver) + nucleus (M_•, seeded); cp2 assembly (delivery, σ_z by birth time,
                the radial spread); cp3 sfh (infall = exponential + tail, less the spheroid; the first
                episode's arrival law is one function, `first_infall`, substitutable for a probe;
                Kennicutt's threshold off κ; the stars moved through the spread), chemistry — the
                migration kernel lives here: transport / transport_columns / migration_width /
                age_bin_edges — / chemistry_dtd, vertical / vertical_alpha (publish `birth_population`);
                cp4 pattern; cp5 systems; cp6 planets.
galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…);  galaxy/specs/: graph, preflight,
                determinism, spec (misses D87; "no testable target" D100; median D109), convergence
                (D94, D101), performance (**two fits, per star and per cell, with their R²** — read the
                per-cell one, S21b D145)
galaxy/api/     service, wire, version, http; client/.  tools/: progress, bootstrap, verify_clone, timings
tests/          test_audit.py is S10–S20's audits plus S21b's five; test_audit_ii_a.py S21 (a)'s twelve;
                test_s22_rulings.py S22's six — #51's three diagonals, row 3 against the mesh, the
                detector against row 9, #28's crossing, #79, the green-row gate. AUDIT_RUN1/2.md are
                main's S10 lists; AUDIT_II_A.md and AUDIT_S21B.md S21's two.
```
## Writing a stage
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a `FieldDecl`
  beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero,
  provenance, about. `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or
  `.get()` / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked. Register with `IMPLEMENTATIONS.register`,
  import in `stages/__init__.py`, map the slot in the models that use it; a constant goes in `level0.py`
  if both models read it (D29, D85); a field nobody reads is dead. **Two implementations of one slot**
  publish the same names under one contract (`FieldDecl.contract`), their own as `optional=True` (D86).
- **A seed binds at the checkpoint of its earliest reader, and `graph` requires that to equal §3's
  hypothesis** (S17); a stage reading a seed publishes *seeded* fields, all of them (D55).
- A named ruleset is a constant with its alternative in the about line, chosen before the row is read (D113,
  and S22 added MERGER_HEATING's); a mechanism is probed by substituting one function, the repo unchanged
  (D114; `sfh.first_infall`, `.star_formation_rate`, `.radial_transport`, `.toomre_threshold` and
  `halo.angular_momentum_core` are S20's and S21's); a default is measured or derived by a test (D30, D117,
  D128); a derived scalar lives on the stage's own mesh, never the grid (D119).
- **A calibration's arithmetic is derived, not just its value** (S20), and **its citation is read before
  the row is trusted** (S21 a, A-14: `MERGER_HEATING`'s "cited 35 km/s" is a selection-function constant
  and the measurement behind it is 39 ± 4). **An opinion about how a field is rendered lives in its
  declaration** (A9) — a reduction over an axis (`disc_radial_spread`, #73), or "the viewer cannot show
  this, and why" (#69). **Per-region determinism is the catalogue's contract** (D60): nothing in
  `materialise` may depend on which cells a request asked for (S19).

## The API and the viewer
- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path, query)` is the same
  without a socket and is what the tests drive; `model=advanced` selects the second model on every route.
  A new route is a `Route` in `service.ROUTES` plus **a row in `tools/timings.py`**.
- Metadata answers from declarations and must not reach the runner; whatever computes goes through
  `Service.compute(...)` (D4, D63); objects are materialised per request (D82). `transport.js` holds **the
  only `fetch`** and that gate asks `git ls-files` what the repository contains (D101).
- The viewer shows every published field **it can show without materialising a galaxy to print one
  number**; four scalars are ruled invisible and say so in their own declarations (#69, S22).

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. 7 controls, 4 seeds,
  `mergers`; every input has a default and every control a range. Every factual claim in every document is
  tagged `[verified: cite]`, `[recall]` or `[inferred]` (B14). A new unit, kind, axis, object class or cmap
  is a `core/` edit plus a DECISIONS.md entry; debts live in §11 and `tools/progress.py` counts them.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, A7) with its model, debt, reason
  and a prediction that could kill it (D33, D87); it still reports `fail`, never widen a target (B5), and a
  miss that starts *passing* fails the run (#29) — remove it and **write down why it passed**. `lo == hi`
  says "no testable target" (D100).

## What the instruments said at S22 close (2026-09-12)
- graph: acyclic, both models. preflight OK: 0 UNSET. determinism OK, reproducible across processes. spec:
  simple **10 pass, 12 fail, 2 n-y-c**; advanced **8 / 15 / 1** — unmoved by S22, which changed no physics:
  it ported two lists, ruled 44 debts, and edited declarations and documents.
- Numbers, to spot a regression by, all unmoved from S20: z_f 1.66, c₂₀₀ 8.24, R_d 2.605, M_star 4.75e10,
  SFR 1.755, H 8.09e9, Σ_crit(R₀) 11.5, WIND_SPEED 860.3, NET_YIELD 0.01376, feh_spread_sun 0.360,
  MERGER_HEATING 88.8, thick σ_z 35.0, spread at R₀ 1.09, rows 3 / 5 / 7 / 9 / 16 / 17 / 18 at 251.03 /
  1.09 / 962 / 0.0455 / 42.8 / 5.70 / 1.97e7, the advanced row 6 356.
- Convergence: 0 drifts on N_R, N_t, N_z; advanced rows 5, 7–11 `vacuous` (#27). **Row 3 converges to
  251.013 at n_R = 3200**, so half its 0.027 miss is the default mesh (S22, #11).
- Register: **27 open — 15 ruled permanent, 12 carried — and 35 discharged**, none unruled; the map is
  at §11's head. Four of the twelve carried are one missing mechanism (#19, #27, #49, half of #47).
- Timings and the profile: D162. The catalogue is the costliest stage in both and is priced **per cell**
  (375 / 338 µs, R² 0.94 / 0.93); the per-star pair every record before S21b quoted is a line
  through a curve (#67).

## Close a session (GALAXY_PLAN.md §5, in this order)
0. Tick the board — surface, model **actually used**, tag, date — then `uv run python
   tools/progress.py`, then `uv run pytest` once, quiet, **backgrounded with its exit status
   appended to its log** (it outlasts the tool's cap), the merge gated on that status (D115, D120).
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **publish the cold timings exactly as
   `tools/timings.py` prints them, stage column included** (B2; #66 is what dropping it costs), the
   profile (D95) and, when a stage's cost changes, `tools/scaling.py`; then rewrite this file in place
   (≤ 120 lines) and write BRIEF.md (≤ 60 lines).
2. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into main: …`;
   push both. **Do not tag** (C2e) — add your MANUAL_TODO.md row with the last session's merge SHA
   filled in, and never force-push. Then `uv run python tools/verify_clone.py --ref main`, which
   clones fresh, bootstraps and runs the suite and the specs there; it refuses on a dirty tree.

A session that stops early closes **partially** (C2d): commit, push, write what remains into
BRIEF.md, mark the row ◐, do **not** merge. **Credentials:** the helper or a repo-scoped token;
never push a tag (C2e) — S22 tried and got the same 403 D40 recorded (D161).
