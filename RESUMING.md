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
S10 ran three times (`session-10`, `-beta`, `-gamma`; the last cut from S9's merge and
unmerged): MANUAL_TODO.md §2 says what is owed.

## Layout

```
galaxy/core/              units (32 closed), cmaps (8 + stops, A9), fielddoc (FieldDecl,
                          6 Kinds, Ramp/Palette, AXES), stage (Stage, Context,
                          CHECKPOINTS), registry (12 INPUTS, MODELS, IMPLEMENTATIONS),
                          seeds (pure child/rng), grids (GridSpec: the knobs), special
galaxy/models/            level0 (shared constants), simple (+NET_YIELD), advanced (its
                          own yields, DTD and wind constants; remaps two slots)
galaxy/stages/            cp1 halo + disc; cp2 assembly; cp3 sfh, chemistry (simple) /
                          chemistry_dtd (advanced), vertical (merger split) /
                          vertical_alpha (chemical split); cp4 pattern; cp5 systems;
                          cp6 planets. Shared where identical, mapped per model.
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…); graph, preflight,
                          determinism, spec (the table; misses per model, D87),
                          convergence (n_R, n_t swept separately; drifts recorded per
                          model, D94), performance (per-stage cold profile in a fresh
                          process per model, the catalogue's per-cell cost, D96)
galaxy/api/               service (routes), wire, version, http; client/ (the viewer)
tools/                    progress, bootstrap, verify_clone, timings, scaling, shot, hooks/
tests/test_calibration.py the audit (rule B10): each debt's measurement pinned, D97–D100
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
  (`FieldDecl.contract`) and their own fields as `optional=True`. A model's own stage may
  `require` its own optional field; a *shared* stage reads it through `.get()` (D86).

## The API and the viewer

- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path,
  query)` is the same without a socket and is what the tests drive. `model=advanced`
  selects the second model on every route. A new route is a `Route` in
  `service.ROUTES` with a handler `_<name>`, **plus a row in `tools/timings.py`**.
- Metadata answers from declarations and must not reach the runner; whatever computes
  goes through `Service.compute(...)`, the closure above the fields asked for (D4, D63).
  A region query materialises its cells, never the catalogue stage: one cell 1.2 ms, the
  whole 140 ms (D96). `transport.js` holds **the only `fetch`** (the test skips `.claude/`).

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
  7 controls, 4 seeds, `mergers`; every input has a default (ratchet at 0) and a range.
- Every factual claim in every document is tagged `[verified: cite]`, `[recall]` or
  `[inferred]` (B14). Debts live in GALAXY_INPUTS §11 and `tools/progress.py` counts
  them: add an item, never a count. No target has zero width (D95).
- A failing acceptance row goes in `spec._MISSES` / `_MISSES_ADVANCED` with its model,
  debt, reason and a prediction that could kill it (D33, D87); a drift beyond a row's
  width goes in `convergence._RECORDED` the same way. Neither widens a target (B5), and
  a recorded entry that starts passing fails the run. The tables are code, never prose.

## What the instruments said at S10 close

- graph, preflight, determinism: unchanged from S9 — acyclic both models, 0 UNSET,
  0 controls without a range, golden values pinned.
- spec: simple **11 pass, 7 fail** (2, 3, 5, 11, 20, 22, 23), 6 not-yet-computable;
  advanced **8 pass, 11 fail** (2, 3, 5, 7–11, 20, 23, 24), 5 not-yet-computable. Every
  failure recorded for its model; exit 0. Unchanged since S9 — the audit fixed no physics.
- convergence: simple **18 pass, 0 fail**, advanced **19 pass, 0 fail**; the largest drift
  is row 20 at 6.8 % of its width (n_R) and row 3 at 5.7 % (n_t, 0.34 km/s). Nothing
  recorded. Row 24 is `single` on every grid; the advanced thick-disc rows are zero on all.
- performance: full run **0.54 s simple, 0.82 s advanced**, cold; `chemistry_dtd` is 42 %
  of the advanced model, the three object stages 70 % of the simple one; the catalogue
  is 276 µs per realised cell, 41–53 % of it eight `Generator` constructions (D61 closed).
- Numbers, to spot a regression by: R200 = 212.94, R_d = 2.49, M_star = 5.276e10,
  M_gas = 5.80e9, SFR = 1.969, v_tan = 256.0 (both models); simple grad = −0.0237, thick
  M = 1.07e10, row 9 = 0.103; advanced grad = −0.0566, old = −0.0193, f_esc(R₀) = 0.753,
  [Fe/H] max +1.5 at the centre. The audit's: c₂₀₀ converted 10.9 → v_tan 242.6; KS ±1σ
  → SFR 1.85–2.16; ratio 1.2 → v_tan 248.7; advanced row 6 = 326 (274 without merger
  heating); giant occurrence inside 1 kpc 0.43 advanced against 0.07 simple.
- **Scaling** (D92) not re-run: no stage changed. **Cold timings** (B2, D101): 20–30 %
  slower than D93 on the same desktop — the machine, not the code.

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

A session that stops early, or may not merge, closes **partially** (C2d): commit, push,
write what remains into BRIEF.md, mark the row ◐, do **not** merge; the branch stays open.

**Credentials.** Push through the helper or a repo-scoped token; nothing credential-shaped
enters the tree (the hook refuses token shapes). Never push a tag (C2e, D40).
