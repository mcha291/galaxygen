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
                          6 Kinds, Ramp/Palette, AXES), stage (Stage, Context,
                          CHECKPOINTS), registry (12 INPUTS, MODELS, IMPLEMENTATIONS),
                          seeds (pure child/rng), grids, special (I1, K0, K1, erf)
galaxy/models/            level0 (shared constants), simple, advanced (a stub)
galaxy/stages/            cp1 halo (NFW, R200, c200, dark/baryon split) + disc (MMW98,
                          Freeman, a razor-thin solver); cp2 assembly (mergers[]);
                          cp3 sfh (two-infall, KS) + chemistry (Z, [Fe/H], gradient,
                          migration) + vertical (thin/thick, heights); cp4 pattern;
                          cp5 systems (catalogue, cells); cp6 planets (formation + planets)
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…); graph, preflight,
                          determinism, spec (the acceptance table)
galaxy/api/               service (routes), wire, version, http; client/: the page,
                          transport.js (the one fetch), flow (D1), ramp (A9), field,
                          stars, system, view, app.js (the only DOM)
tools/                    progress, bootstrap, verify_clone, timings, shot, hooks/
```

## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field
  a `FieldDecl` beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)`
  order, ramp, meaningful_zero, provenance, about.
- `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or `.get()`
  / `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it
  returns exactly the declared names, shape and value class checked.
- `IMPLEMENTATIONS.register(...)`, import in `stages/__init__.py`, map the slot in
  **both** models; a Level 0 constant goes in `models/level0.py` only if read (D29).
- A stage that reads a seed publishes *seeded* fields: split one whose other half is
  determined (`population`/`systems`, `formation`/`planets`), or the declaration is false
  and gets enforced as true (D78).

## The API and the viewer

- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path,
  query)` is the same without a socket and is what the tests drive. A new route is a
  `Route` in `service.ROUTES` with a handler `_<name>`, **plus a row in
  `tools/timings.py`** — a test fails if a route has no cold timing.
- Metadata answers from declarations and must not reach the runner; whatever computes
  goes through `Service.compute(...)`, the closure above the fields asked for (D4, D63).
  Ask for nothing more: a scalar whose stage publishes object columns costs a whole
  catalogue (D73). Objects are materialised per request — a region builds the cells it
  was asked for, `/api/system` builds one cell and one star (D82).
- The client is pure modules plus `app.js`, so node tests in `tests/js/` assert the rules
  rather than look at them (D70). It holds no colour, no cmap name and no storage API,
  and `transport.js` holds **the only `fetch`** — four absences. `tools/shot.py` renders
  a page to a PNG (D77).

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
  7 controls, 4 seeds, `mergers`; every input has a default and every control a range.
- Every factual claim in every document is tagged `[verified: cite]`, `[recall]` or
  `[inferred]` (B14); a bare verified tag fails a test. A new unit, kind, axis, object
  class or cmap is a `core/` edit plus a DECISIONS.md entry. Debts live in GALAXY_INPUTS
  §11 and `tools/progress.py` counts them: add an item, never a count.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction
  that could kill it (D33); it still reports `fail`, never widen a target (B5), and a
  miss that starts *passing* fails the run. The table itself is `spec.py`, never prose.

## What the instruments said at S8 close

- graph: acyclic; order `halo -> assembly -> disc -> sfh -> chemistry -> vertical -> bar
  -> population -> pattern -> systems -> formation -> planets`. preflight OK: 0 UNSET, 0
  controls without a range. determinism OK, golden values pinned.
- spec: **11 pass** (1, 4, 6-10, 15-17, 19), **7 fail** (2, 3, 5, 11, 20, 22, 23, every one
  a recorded miss), 6 not-yet-computable, exit 0. S8 moved no galactic number; **read D51
  before trusting row 9**, which passes on two errors cancelling.
- Numbers, to spot a regression by: R200 = 212.94, R_d = 2.49, M_star = 5.276e10,
  M_gas = 5.80e9, SFR = 1.969, v_tan = 256.0, grad = -0.0237, thick M = 1.07e10, row 9 =
  0.103, bar a = 4.98, N_stars = 9.0e10; occurrence 0.0499 at solar [Fe/H] = 0, β = 2.99,
  ice line 2.674 AU, 5.3 planets per sampled star.
- **Cold timings** (B2, D84) moved with the machine, not the code — compare within a
  run: metadata sub-millisecond, no stages; one profile 0.13 s; a nine-cell region
  0.18 s; **one system 0.16 s cold, 2.8 ms warm** against 0.32 s for a whole disc. A
  full model run is 0.60 s.
- **Three causes hold seven failing rows**: #18 (no extended accretion) has 2, 3, 20;
  #15 (gradients a third too shallow) 22, 23; #19 (the thick disc) 5, 11. #23 (no arms)
  and #25 (S8's occurrence slope) cost no row.

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board — surface, model **actually used**, tag, date — then `uv run python
   tools/progress.py`, then `uv run pytest` once, quiet.
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **publish the cold timings**
   (rule B2) — every session from S6 on.
2. Rewrite this file in place (≤ 120 lines); write BRIEF.md (≤ 60 lines).
3. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into
   main: …`; push both. **Do not tag** (C2e) — add your MANUAL_TODO.md row with the last
   session's merge SHA filled in, and never force-push.
4. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps, runs
   the suite and the specs there; refuses if the working tree is dirty.

A session that stops early closes **partially** (C2d): commit, push, write what remains
into BRIEF.md, mark the row ◐, do **not** merge; the branch stays open.

**Credentials.** Push through the helper or a token scoped to this repo (Contents: read
and write). Nothing credential-shaped enters the tree; the hook refuses token shapes.
`.github/workflows/` needs workflow permission. Never push a tag: the proxy refuses tag
refs with a 403 whatever the credential (C2e, D40).
