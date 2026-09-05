# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's
status board is the only record of what is done (A9); this file does not repeat it,
is rewritten in place each session, and is capped at 120 lines (C3) by a test.
**The eleven-session build is closed (S10, 2026-09-05).** BRIEF.md is for a maintainer.

## Open a session (rules C1, C2b)

```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```

Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section, when BRIEF.md
names one. Branch `session-NN`; commit and push at every sub-deliverable (rule C2b).
In a git worktree also run `git config --worktree core.hooksPath tools/hooks` (S10 run 2).

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
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…); graph, preflight,
                          determinism, spec (misses per model, D87), convergence (the
                          grid swept one axis at a time, D94), performance (D95)
galaxy/api/               service (routes), wire, version, http; client/ (the viewer)
tools/                    progress, bootstrap, verify_clone, timings, scaling, shot, hooks/
AUDIT_RUN1.md, AUDIT_RUN2.md   the two independent S10 defect lists; their diff is D97
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
  else in the one model that does (D29, D85). A field nobody reads is dead (debt #30).
- **Two implementations of one slot** publish the same names under the same contract
  (`FieldDecl.contract`; `dataclasses.replace(decl, about=…)` keeps it) and their own
  fields as `optional=True`. A model's own stage may `require` its own optional field;
  a *shared* stage reads it through `requires_optional` and `.get()` (D86).
- A stage that reads a seed publishes *seeded* fields: split one whose other half is
  determined (`population`/`systems`, `formation`/`planets`) (D78).

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
  run for that model — so a default that fixes a row changes its miss entry in the same
  commit (debt #29). The table itself is `spec.py`, never prose.

## What the instruments said at S10 close (run 2, 2026-09-05)

- graph: acyclic, both models; orders in `tests/test_graph.py::ORDER`. preflight OK:
  0 UNSET, 0 controls without a range. determinism OK, golden values pinned.
- spec, simple: **11 pass, 7 fail** (2, 3, 5, 11, 20, 22, 23), 6 not-yet-computable.
  spec, advanced: **8 pass, 11 fail, 5 not-yet-computable** — no thick disc (debt #27:
  rows 5, 7–11, 24), row 23 migration (#28), row 22 passes. Every failure recorded for
  its model; exit 0. No green row is an unconditioned prediction (AUDIT_RUN2.md §5).
- Numbers, to spot a regression by: R200 = 212.94, R_d = 2.49, M_star = 5.276e10, SFR
  = 1.969, v_tan = 256.0 (both); simple grad −0.0237, old −0.0067, thick M 1.07e10, row
  9 0.103; advanced grad −0.0566, old −0.0193, v_esc(R₀) 578, f_esc 0.753, spread 0.299.
- **Convergence** (D94): 0 drifts on N_R, N_t, N_z in either model; the default grid
  is the N_t outlier at 0.2% (a step-onset infall, debt #30); DTD_BINS and AGE_BIN
  converged by probe. **Profile** (D95, D98): simple 0.43 s, advanced 0.66 s
  (chemistry_dtd 40%); `pattern`'s warm column is a cache (9 ms cold). **Scaling**
  (D92): 0.94 / 0.78 / 2.03 naive; the tool's "whole model, cold" is warm.
- **Register**: 26 open, 7 discharged; S10 added #29–#33, amended #11, #12, #17, #18,
  #21, #24, #28. The two audits' diff is D97.

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board — surface, model **actually used**, tag, date — then `uv run python
   tools/progress.py`, then `uv run pytest` once, quiet.
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **publish the cold timings**
   (rule B2), the profile (D95) and, when a stage's cost changes, `tools/scaling.py`.
2. Rewrite this file in place (≤ 120 lines); write BRIEF.md (≤ 60 lines).
3. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into
   main: …`; push both. **Do not tag** (C2e) — add your MANUAL_TODO.md row with the last
   session's merge SHA filled in, and never force-push.
4. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps, runs
   the suite and the specs there; refuses if the working tree is dirty.

A session that stops early closes **partially** (C2d): commit, push, write what remains
into BRIEF.md, mark the row ◐, do **not** merge; the branch stays open.

**Credentials.** The helper or a repo-scoped token; the hook refuses token shapes; never push a tag (C2e).
