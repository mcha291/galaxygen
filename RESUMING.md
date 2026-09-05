# Resuming

How to open a session, where things are, what the instruments say. GALAXY_PLAN.md's
status board is the only record of what is done (A9); this file does not repeat it,
is rewritten in place each session, and is capped at 120 lines (C3) by a test.

## Open a session (rules C1, C2b)

```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```

Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section, when BRIEF.md
names one. Branch `session-NN`; commit and push at every sub-deliverable (rule C2b).

## Layout

```
galaxy/core/              units (32 closed), cmaps (8 + stops, A9), fielddoc (FieldDecl,
                          6 Kinds, Ramp/Palette, AXES), stage (Stage, Context, CHECKPOINTS),
                          registry (12 INPUTS, MODELS, IMPLEMENTATIONS), seeds (pure
                          child/rng), grids, special (I1, K0, K1, erf)
galaxy/models/            level0 (shared constants), simple (+NET_YIELD), advanced (its
                          own yields, DTD and wind constants; remaps two slots)
galaxy/stages/            cp1 halo + disc; cp2 assembly; cp3 sfh, chemistry (simple) /
                          chemistry_dtd (advanced), vertical (merger split) /
                          vertical_alpha (chemical split); cp4 pattern; cp5 systems; cp6
                          planets. Shared where identical, mapped per model.
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…); six specs — graph,
                          preflight, determinism, spec (the table; misses are per model,
                          D87), convergence (S10), performance (S10)
galaxy/api/               service (routes), wire, version, http; client/ (the viewer)
tools/                    progress, bootstrap, verify_clone, timings, scaling, shot, hooks/
```

## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field
  a `FieldDecl` beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)`
  order, ramp, meaningful_zero, provenance, about.
- `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or `.get()`
  / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it
  returns exactly the declared names, shape and value class checked.
- `IMPLEMENTATIONS.register(...)`, import in `stages/__init__.py`, map the slot in the
  models that use it. A constant goes in `level0.py` if both models read it, else in
  the one that does (D29, D85).
- **Two implementations of one slot** publish the same names under the same contract
  (`FieldDecl.contract`; `dataclasses.replace(decl, about=…)` keeps it) and their own
  fields as `optional=True`. A model's own stage may `require` its own optional field; a
  *shared* one reads it through `requires_optional` and `.get()` (D86).
- A stage that reads a seed publishes *seeded* fields: split one whose other half is
  determined (`population`/`systems`, `formation`/`planets`), or the declaration is
  false and gets enforced as true (D78).

## The API and the viewer

- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path,
  query)` is the same without a socket and is what the tests drive. `model=advanced`
  selects the second model on every route. A new route is a `Route` in `service.ROUTES`
  with a handler `_<name>`, **plus a row in `tools/timings.py`** — a test fails if a
  route has no cold timing.
- Metadata answers from declarations and must not reach the runner; whatever computes
  goes through `Service.compute(...)`, the closure above the fields asked for (D4, D63);
  objects are per request (D82). `transport.js` holds **the only `fetch`**; the gate
  asserting that asks `git ls-files`, not the filesystem (D99).

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
  7 controls, 4 seeds, `mergers`; every input has a default and every control a range.
- Every factual claim in every document is tagged `[verified: cite]`, `[recall]` or
  `[inferred]` (B14); an uncited verified tag fails a test. A new unit, kind, axis,
  object class or cmap is a `core/` edit plus a DECISIONS.md entry. Debts live in
  GALAXY_INPUTS §11; `progress.py` counts them — add an item, never a count.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, rule A7) with
  its model, debt, reason and a prediction that could kill it (D33, D87); it still
  reports `fail`, never widen a target (B5), and a miss that starts *passing* fails the
  run for that model. A grid drift registers the same way in `convergence._RECORDED`.

## What the instruments said at S10 close

- graph: acyclic, both models; orders differ (`tests/test_graph.py::ORDER`). preflight OK
  (0 UNSET, 0 controls without a range). determinism OK, golden values pinned.
- spec, simple: **11 pass, 7 fail** (2, 3, 5, 11, 20, 22, 23), 6 not-yet-computable;
  advanced **8 pass, 11 fail** (2, 3, 5, 7–11, 20, 23, 24), 5 nyc. Each recorded for its
  model, exit 0; **unchanged since S8/S9 — S10 changed no physics** (D101). Rows 20 and
  21 are now named as having no testable target (debt #17, D98).
- Numbers, to spot a regression by: R200 = 212.94, R_d = 2.49, M_star = 5.276e10, M_gas
  = 5.80e9, SFR = 1.969, v_tan = 256.0 (both); simple grad = −0.0237, thick M = 1.07e10;
  advanced grad = −0.0566, old = −0.0193, v_esc(R₀) = 578, [Fe/H] max +1.5.
- **convergence** (D94): one knob at a time. Nothing drifts; **worst margin 0.056 of a
  target width**. Controls fire at N_R = 8 and N_t = 8, **never for N_z even at 1**.
- **performance** (D96, D97): simple 0.43 s cold over 12 stages, advanced 0.65 s;
  `chemistry_dtd` is 40% of the advanced model, the catalogue 27% of the simple one.
  Catalogue 113 ms, **90% of it independent of the sample size**; 14.9 ms lays out all
  1024 cells whether or not anything asks. The first seeded draw costs 8.9 ms once a
  process and the table bills it to `pattern` (debt #32).
- **Cold timings** (B2, D100): ~10–15% slower than D93, shape unchanged — the machine,
  not the code. `tools/scaling.py` not re-run: no stage's `compute` was touched (B7).

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
into BRIEF.md, mark the row ◐, do **not** merge; the branch stays open.

**Credentials.** Push through the helper or a repo-scoped token; nothing credential-shaped
enters the tree (the hook refuses token shapes). Never push a tag (C2e, D40).
