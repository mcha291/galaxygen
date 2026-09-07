# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's
status board is the only record of what is done (A9); this file does not repeat it,
is rewritten in place each session, and is capped at 120 lines (C3) by a test.
**The build is closed** (S0–S10; S11 integrated the audits, S12 the one-line fixes, S13 the physics decisions).

## Open a session (rules C1, C2b)

```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```

Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section. Branch `session-NN`;
commit and push at every sub-deliverable (C2b). In a worktree: `git config --worktree core.hooksPath tools/hooks`.

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
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…); graph, preflight, determinism,
                          spec (misses per model D87; "no testable target" D100; median D109), convergence (one axis
                          at a time D94; vacuous D101), performance (D95; fixed/per-star fit, one-off D101)
galaxy/api/               service (routes), wire, version, http; client/ (the viewer)
tools/                    progress, bootstrap, verify_clone, timings, scaling, shot, hooks/
tests/test_audit.py       the S10 audits' measurements as tests (#12, #17, #21, #26–#28, #41–#45);
                          beta's are in test_halo, test_chemistry_dtd, test_determinism, test_spec
AUDIT_RUN1.md, AUDIT_RUN2.md   main's two S10 lists (diff D97); all four lists: D102
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
  objects are materialised per request (D82). `transport.js` holds **the only `fetch`**;
  the gate asks `git ls-files` what the repository contains (D101).

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
  run for that model (debt #29). A pointwise row with `lo == hi` says "no testable target" (D100).

## What the instruments said at S13 close (2026-09-07)

- graph: acyclic, both models. preflight OK: 0 UNSET, 0 controls without a range.
  determinism OK, golden values pinned, and reproducible across processes (two hash seeds, S12).
- spec: simple **11 pass, 7 fail** (2, 3, 5, 11, 20, 22, 23; row 3 low since S13), 6 n-y-c;
  advanced **7 pass, 12 fail, 5 n-y-c** (row 6 joined at S13, debt #42). Every failure
  recorded for its model. No green row is an unconditioned prediction (AUDIT_RUN2 §5).
- Numbers, to spot a regression by (S13): R200 212.94, c_vir 14.35, c200 10.91, R_d 2.49,
  M_star 5.287e10, SFR 1.891, gas 5.714e9, H 4.171e9, v_tan 242.7 (both); simple grad −0.0236,
  old −0.0064, thick M 1.42e10, row 9 0.152; advanced grad −0.0561, v_esc(R₀) 561.5, f_esc 0.757.
- **Convergence** (D94, D101): 0 drifts on N_R, N_t, N_z in either model; the worst is
  row 3 under N_t at 0.055 of its width; advanced rows 5, 7–11 are `vacuous` (debt #27).
  **Profile** (D101, D103): 0.51 s simple, 0.81 s advanced (chemistry_dtd 41%); the
  catalogue is 90–95% fixed cost (134 / 123 ms, 0.3–0.7 µs per star); the first seeded
  draw costs ~10 ms, lands on `pattern`, and `tools/timings.py` stars the routes that pay it.
- **Register**: 31 open, 14 discharged; S13 discharged #29, #30, #38, #41 and half of #12
  (D106–D109), probed the bulge (D110: it lowers row 3). The three audit branches stay unmerged.

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
