# Resuming

How to open a session, where things are, what the instruments say. GALAXY_PLAN.md's
status board is the only record of what is done (A9); this file does not repeat it,
is rewritten in place each session, and is capped at 120 lines (C3) by a test.

## Open a session (rules C1, C2b)

```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the six spec reports
```

Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section, when BRIEF.md
names one. Branch `session-NN`; commit and push at every sub-deliverable (rule C2b).

## Layout

```
galaxy/core/              units (32 closed), cmaps (8 + stops, A9), fielddoc (FieldDecl,
                          6 Kinds, Ramp/Palette, AXES), stage (Stage, Context,
                          CHECKPOINTS), registry (12 INPUTS, MODELS, IMPLEMENTATIONS),
                          seeds (pure child/rng), grids, special (I1, K0, K1, erf)
galaxy/models/            level0 (shared constants), simple (+NET_YIELD), advanced (its
                          own yields, DTD and wind constants; remaps two slots)
galaxy/stages/            cp1 halo + disc; cp2 assembly; cp3 sfh, chemistry (simple) /
                          chemistry_dtd (advanced), vertical (merger split) /
                          vertical_alpha (chemical split); cp4 pattern; cp5 systems;
                          cp6 planets. Shared where identical, mapped per model.
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…) -> Outputs (+seconds
                          per stage); graph, preflight, determinism, spec (misses per
                          model, D87), convergence (D94), performance (D95)
galaxy/api/               service (routes), wire, version, http; client/ (the viewer)
tools/                    progress, bootstrap, verify_clone, timings, scaling, shot, hooks/
tests/test_audit.py       the S10 calibration audit as tests: what each constant does
```

## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field
  a `FieldDecl` beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)`
  order, ramp, meaningful_zero, provenance, about.
- `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or `.get()`
  / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it
  returns exactly the declared names, shape and value class checked.
- `IMPLEMENTATIONS.register(...)`, import in `stages/__init__.py`, map the slot in the
  models that use it. A constant goes in `level0.py` if both models' stages read it,
  else in the one model that does (D29, D85).
- **Two implementations of one slot** publish the same names under the same contract
  (`FieldDecl.contract`; `dataclasses.replace(decl, about=…)` keeps it) and their own
  fields as `optional=True`. A model's own stage may `require` its own optional field;
  a *shared* stage reads it through `requires_optional` and `.get()` (D86).
- A stage that reads a seed publishes *seeded* fields: split one whose other half is
  determined (`population`/`systems`, `formation`/`planets`), or the declaration is false
  and gets enforced as true (D78).
- An acceptance scalar is analytic or a smooth functional of the grid (D37); convergence
  sweeps N_R and N_t alone and fails a row that moves past its width (`_UNCONVERGED`).

## The API and the viewer

- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path,
  query)` is the same without a socket and is what the tests drive. `model=advanced`
  selects the second model on every route. A new route is a `Route` in
  `service.ROUTES` with a handler `_<name>`, **plus a row in `tools/timings.py`** — a
  test fails if a route has no cold timing.
- Metadata answers from declarations and must not reach the runner; whatever computes
  goes through `Service.compute(...)`, the closure above the fields asked for (D4, D63);
  objects are materialised per request (D82). `transport.js` holds **the only `fetch`**.

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
  7 controls, 4 seeds, `mergers`; every input has a default and every control a range.
- Every factual claim in every document is tagged `[verified: cite]`, `[recall]` or
  `[inferred]` (B14); a bare verified tag fails a test. A new unit, kind, axis, object
  class or cmap is a `core/` edit plus a DECISIONS.md entry. Debts live in GALAXY_INPUTS
  §11 and `tools/progress.py` counts them: add an item, never a count.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, rule A7) with
  its model, debt, reason and a prediction that could kill it (D33, D87); it still
  reports `fail`, never widen a target (B5), and a miss that starts *passing* fails the
  run for that model. A row whose source quotes no uncertainty has `lo == hi` and
  `Quantity.testable` False: "no testable target", published and not widened (D97).

## What the instruments said at S10 close (run 2)

- graph, preflight, determinism: as at S9. spec: **simple 11 pass, 7 fail, 6 n-y-c;
  advanced 8 pass, 11 fail, 5 n-y-c**, every failure recorded, exit 0 — unchanged.
- **convergence** (D94): every computable row converges in both models; the widest
  drift is row 3's 0.33 km/s (5.6% of its width, from N_t), and N_R never moves a row
  more than N_t does. Row 20 untestable; the advanced thick-disc rows vacuous (#27).
- **performance** (D95): cold 0.54 s simple, 0.81 s advanced; the catalogue pays ~100 µs
  per cell against ~2 µs per star (75% of the systems stage is per-cell setup, D61
  answered); chemistry_dtd is 42% of the advanced run.
- **The audit** (D96): #17 discharged; #29 (row 20 counts hydrogen, the model helium:
  47% low), #30 (row 6 at the edge in both models, opposite ends), #31 (`GAS_DISC_SCALE_
  RATIO` carries the advanced row 22) opened; #12 measured (the c₂₀₀ conversion alone
  takes row 3 to 242.6); #27's prediction held in part (n = 3 plus one small merger).
- Numbers to spot a regression by: R200 = 212.94, R_d = 2.49, M_star = 5.276e10, M_gas
  = 5.80e9, SFR = 1.969, v_tan = 256.0 (both); simple grad −0.0237, thick M 1.07e10, row 9
  0.103; advanced grad −0.0566, old −0.0193, mode +0.21, [Fe/H] max +1.53, > +0.5 to 2.7 kpc.

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board — surface, model **actually used**, tag, date — then `uv run python
   tools/progress.py`, then `uv run pytest` once, quiet.
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **publish the cold timings**
   (rule B2) and, when a stage's cost changes, `tools/scaling.py` (rule B7).
2. Rewrite this file in place (≤ 120 lines); write BRIEF.md (≤ 60 lines).
3. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into
   main: …`; push both. **Do not tag** (C2e) — add your MANUAL_TODO.md row with the last
   session's merge SHA filled in, and never force-push.
4. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps, runs
   the suite and the specs there; refuses if the working tree is dirty.

A session that stops early closes **partially** (C2d): commit, push, write what remains
into BRIEF.md, mark the row ◐, do **not** merge; the branch stays open (S10 is one, twice).

**Credentials.** Push through the helper or a repo-scoped token; nothing credential-shaped
enters the tree (the hook refuses token shapes). Never push a tag (C2e, D40).
