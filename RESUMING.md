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
galaxy/core/units.py      31 closed units; cmaps.py: 8 cmaps and their stops (A9, D71)
galaxy/core/fielddoc.py   FieldDecl, Kind (6), Ramp/Palette, AXES, OBJECTS, SCALES;
                          stage.py: Stage, Context (restricted views), CHECKPOINTS
galaxy/core/registry.py   INPUTS (12), Input/Constant/Model, MODELS, IMPLEMENTATIONS;
                          models/: level0 (constants), simple, advanced (stub)
galaxy/core/seeds.py      child/rng(seed,*path), pure; grids.py GridSpec(400,2000,60,360)
galaxy/stages/halo.py     NFW halo, R200, c200, M200 -> dark + baryons (cp 1). disc.py:
                          MMW98 scale length, Freeman + a general razor-thin solver
galaxy/stages/assembly.py mergers[]: gas delivery, vertical heating (cp 2). sfh.py:
                          two-infall, Kennicutt-Schmidt, the gas/star split (cp 3)
galaxy/stages/chemistry.py  Z(R,t), [Fe/H], gradient, migration. vertical.py: the
                          thin/thick split, scale heights, rows 5-11 (cp 3)
galaxy/stages/pattern.py  bar + pattern (cp 4). systems.py: the catalogue and its
                          (R, phi) cell grid (cp 5)
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…) -> Outputs;
                          graph, preflight, determinism, spec (the acceptance table)
galaxy/api/               service.py (routes), wire, version, http; client/: the page,
                          transport.js (the one fetch), flow.js (D1), ramp.js (A9),
                          field.js, stars.js, view.js, app.js (the only DOM)
tools/                    progress, bootstrap, verify_clone, timings, shot, hooks/
DECISIONS.md LESSONS.md   append-only; lessons tagged by stage type. MANUAL_TODO.md:
                          the queued session tags (C2e)
```

## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each
  published field a `FieldDecl` beside its compute: name, label, unit, kind, axes in
  `(R, t, z, phi)` order, ramp, meaningful_zero, provenance, about.
- `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or `.get()
  /.has()` (optional), `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked.
- `IMPLEMENTATIONS.register(...)`, import in `stages/__init__.py`, map the slot in
  **both** models; a Level 0 constant goes in `models/level0.py` only if read (D29).

## The API and the viewer

- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path,
  query)` is the same without a socket, and is what the tests drive.
- A new route is a `Route` in `service.ROUTES` with a handler `_<name>`, **plus a row
  in `tools/timings.py`** — a test fails if a route has no cold timing.
- Metadata answers from declarations and must not reach the runner; whatever computes
  goes through `Service.compute(...)`, the closure above the fields asked for, resuming
  what the galaxy has (D4, D63). Ask for nothing more: a scalar whose stage publishes
  object columns costs a whole catalogue (D73).
- The client is pure modules plus `app.js`; rules live in the modules so node tests in
  `tests/js/` can assert them rather than look (D70). It holds no colour, no cmap name
  and no storage API, and `transport.js` holds **the only `fetch`** — four absences.
  `uv run python tools/shot.py --path /` renders the page to a PNG (D77).

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
  7 controls, 4 seeds, `mergers`. Every input has a default and every control a range;
  the `tests/test_registry.py` ratchets are at zero.
- Every factual claim in every document is tagged `[verified: cite]`, `[recall]` or
  `[inferred]` (B14); a bare verified tag fails a test. A new unit, kind, axis, object
  class or cmap is a `core/` edit plus a DECISIONS.md entry. Debts live in GALAXY_INPUTS
  §11 and `tools/progress.py` counts them onto the board — add an item, never a count.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction
  that could kill it (D33); it still reports `fail`, never widen a target (B5), and a
  miss that starts *passing* fails the run. The table itself is `spec.py`, never prose.

## What the instruments said at S7 close

- graph: acyclic; order `halo -> assembly -> disc -> sfh -> chemistry -> vertical ->
  bar -> population -> pattern -> systems`. preflight OK: 0 UNSET, 0 controls without
  a range. determinism OK, golden values pinned.
- spec: **11 pass** (1, 4, 6-10, 15-17, 19), **7 fail** (2, 3, 5, 11, 20, 22, 23, every
  one a recorded miss), 6 not-yet-computable, exit 0. S7 moved no number; **read D51
  before trusting row 9**, which passes on two errors cancelling.
- Numbers, to spot a regression by: R200 = 212.94, R_d = 2.49, M_star = 5.276e10,
  M_gas = 5.80e9, SFR = 1.969, v_tan = 256.0, grad = -0.0237, thick M = 1.07e10, row 9
  = 0.103, bar a = 4.98, N_stars = 9.0e10. **Cold timings** (B2, D76): a file 0.1 ms and
  no stages; one profile 0.22 s; a nine-cell region 0.30 s cold and 6.4 ms warm against
  0.49 / 0.27 for all 1024 cells.
- **Three causes hold seven failing rows**: #18 (no extended accretion) has 2, 3, 20;
  #15 (gradients) 22, 23; #19 (the thick disc) 5, 11. **#23 is now visible**: the
  viewer draws a smooth axisymmetric disc and says why (D75).

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board — surface, model **actually used**, tag, date — then
   `uv run python tools/progress.py`, then `uv run pytest` once, quiet.
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, and **publish the cold
   timings** (rule B2) — every session from S6 on.
2. Rewrite this file in place (≤ 120 lines); write BRIEF.md (≤ 60 lines).
3. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into
   main: …`; push branch and main. **Do not tag** (C2e) — add your MANUAL_TODO.md row,
   fill in the last session's merge SHA, never force-push.
4. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps, runs
   the suite and the specs there; refuses if the working tree is dirty.

A session that stops early closes **partially** (C2d): commit, push, write what remains
into BRIEF.md, mark the board row ◐, do **not** merge. The branch stays open.

**Credentials.** Push through the helper or a token scoped to this repo (Contents: read
and write). Nothing credential-shaped enters the tree; the hook refuses token shapes.
`.github/workflows/` needs workflow permission. Never push a tag: the proxy refuses tag
refs with a 403 whatever the credential (C2e, D40).
