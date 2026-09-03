# Resuming

How to open a session, where things are, what the instruments say. GALAXY_PLAN.md's
status board is the only record of what is done (A9); this file does not repeat it,
is rewritten in place each session, and is capped at 120 lines (C3) by a test.

## Open a session (rules C1, C2b)

```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
git checkout -b session-NN
```

Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section, when BRIEF.md
names one. Commit and push at every completed sub-deliverable (rule C2b).

## Layout

```
galaxy/core/units.py      closed unit vocabulary (31 ASCII symbols, display forms)
galaxy/core/fielddoc.py   FieldDecl, Kind (6), Ramp/Palette, AXES, OBJECTS, CMAPS
galaxy/core/stage.py      Stage declaration, Context (restricted views), CHECKPOINTS
galaxy/core/registry.py   INPUTS (12), Input/Constant/Model, MODELS, IMPLEMENTATIONS;
                          models/: level0 (shared constants), simple, advanced (stub)
galaxy/core/seeds.py      child/rng(seed, *path), pure and order-independent. grids.py:
                          GridSpec(400, 2000, 60, 360). special.py: I1, K0, K1 (A&S 9.8)
galaxy/stages/halo.py     NFW halo, R200, c200, M200 -> dark + baryons (cp 1). disc.py:
                          MMW98 scale length, Freeman + a general razor-thin solver
galaxy/stages/assembly.py mergers[]: gas delivery, vertical heating (cp 2). sfh.py:
                          two-infall, Kennicutt-Schmidt, the gas/star split (cp 3)
galaxy/stages/chemistry.py  Z(R,t), [Fe/H], gradient, migration. vertical.py: the
                          thin/thick split, scale heights, rows 5-11
galaxy/stages/pattern.py  bar + pattern (seeded), cp 4. systems.py: the catalogue and
                          the (R, phi) cell grid, cp 5
galaxy/run.py             run(model, inputs, grid, only=…, resume=…) -> Outputs
galaxy/specs/             graph, preflight, determinism, spec (the acceptance table)
galaxy/api/               service.py (routes), wire, version, http, client/transport.js
tools/                    progress, bootstrap, verify_clone, timings, hooks/pre-commit
DECISIONS.md LESSONS.md   append-only; lessons tagged by stage type. MANUAL_TODO.md:
                          queued session tags — add yours, fill in the last one (C2e)
```

## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each
  published field a `FieldDecl` beside its compute: name, label, unit, kind, axes in
  `(R, t, z, phi)` order, ramp, meaningful_zero, provenance, about.
- `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or
  `.get()/.has()` (optional), `.rng(seed, *path)`; only declared names resolve, and it
  returns exactly the declared names, shape and value class checked.
- `IMPLEMENTATIONS.register(...)`, import in `stages/__init__.py`, map the slot in
  **both** models; a Level 0 constant goes in `models/level0.py` only if read (D29).

## Using or extending the API

- `uv run python -m galaxy.api` serves on 127.0.0.1:8017; `Service().handle(path, query)`
  is the same without a socket and is what the tests drive. A new route is a `Route` in
  `service.ROUTES` with a handler `_<name>`, **plus a row in `tools/timings.py`** — a
  test fails if a route has no cold timing.
- Metadata answers from declarations and must not reach the runner; whatever computes
  goes through `Service.compute(...)`, which runs the closure above the fields asked for
  and resumes what the galaxy has (D4, D63). `galaxy-bin/1` (D65) is decoded by
  `client/transport.js`, which holds **the only `fetch`** (D2).

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
  7 controls, 4 seeds, `mergers`. Every input has a default and every control a range;
  the `tests/test_registry.py` ratchets are at zero.
- Every factual claim in every document is tagged `[verified: cite]`, `[recall]` or
  `[inferred]` (B14); a bare verified tag fails a test. A new unit, kind, axis, object
  class or cmap is a `core/` edit plus a DECISIONS.md entry.
- Debts live in GALAXY_INPUTS.md §11, counted onto the board by `tools/progress.py` —
  add a numbered item, never edit the count.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a prediction
  that could kill it (D33); it still reports `fail`, never widen a target (B5), and a
  miss that starts *passing* fails the run. The table itself is `spec.py`, never prose.

## What the instruments said at S6 close

- graph: acyclic; order `halo -> assembly -> disc -> sfh -> chemistry -> vertical ->
  bar -> population -> pattern -> systems`. preflight OK: 0 UNSET, 0 controls without
  a range. determinism OK, golden values pinned.
- spec: **11 pass** (1, 4, 6-10, 15-17, 19), **7 fail** (2, 3, 5, 11, 20, 22, 23, every
  one a recorded miss), 6 not-yet-computable, exit 0. S6 moved no number; **read D51
  before trusting row 9**, which passes on two errors cancelling.
- Numbers, to spot a regression by: R200 = 212.94, R_d = 2.49, M_star = 5.276e10,
  M_gas = 5.80e9, SFR = 1.969, v_tan = 256.0, grad = -0.0237, thick M = 1.07e10, row 9
  = 0.103, bar a = 4.98, N_stars = 9.0e10. **Cold timings, published every session from
  here on** (B2, D67): metadata 0.1-1.0 ms and **zero stages**; a nine-cell region
  0.28 s cold, 8.4 ms warm, against 0.72 / 0.37 for all 1024 cells; a run 0.48 s (D59).
- **Three causes hold seven failing rows**: #18 (no extended accretion) has 2, 3, 20;
  #15 (gradients a third of observed) 22, 23; #19 (the thick disc) 5, 11. #23 (no arm
  pattern) costs no row and is why the galaxy does not look like one; #24 is
  **discharged** (D63).

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board — surface, model **actually used**, tag, date — then
   `uv run python tools/progress.py`, then `uv run pytest` once, quiet.
1. Append to DECISIONS.md; new rules into LESSONS.md, tagged. Publish the cold
   timings (rule B2) — every session from S6 on.
2. Rewrite this file in place (≤ 120 lines); write BRIEF.md (≤ 60 lines).
3. Commit; `git checkout main && git merge --no-ff session-NN`, subject
   `Merge S<N> into main: …`; push branch and main. **Do not tag** (C2e) — add your row
   to MANUAL_TODO.md and fill in the previous session's merge SHA. Never force-push.
4. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps, runs
   the suite and the specs there; refuses if the working tree is dirty.

A session that stops early closes **partially** (C2d): commit, push, write what remains
into BRIEF.md, mark the board row ◐, do **not** merge. The branch stays open.

## Credentials

Push through the credential helper or a fine-grained token scoped to this repo
(Contents: read and write). Nothing credential-shaped enters the tree; the hook refuses
token shapes. `.github/workflows/` needs workflow permission. Never push a tag: the
proxy refuses tag refs with a 403 whatever the credential (C2e, D40).
