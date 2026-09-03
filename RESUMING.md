# Resuming

How to open a session, where things are, what the instruments say. The status
board at the top of GALAXY_PLAN.md is the only record of what is done (rule A9);
this file does not repeat it. Hard cap 120 lines (rule C3), enforced by
`tests/test_docs.py`. Rewritten in place every session; it never grows.

## Open a session (rules C1, C2b)

```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest                          # quiet; only failures print
uv run python -m galaxy.specs          # graph, preflight, determinism, spec reports
git checkout -b session-NN
```

Then read RULES.md in full and BRIEF.md. Read GALAXY_INPUTS.md only by section,
when BRIEF.md names one. Commit and push at every completed sub-deliverable.

## Layout

```
galaxy/core/units.py      closed unit vocabulary (31 ASCII symbols, display forms)
galaxy/core/fielddoc.py   FieldDecl, Kind (6), Ramp/Palette, AXES, OBJECTS, CMAPS
galaxy/core/stage.py      Stage declaration, Context (restricted views), CHECKPOINTS
galaxy/core/registry.py   INPUTS (12), Input/Constant/Model, MODELS, IMPLEMENTATIONS, production()
galaxy/core/seeds.py      child(seed, *path), rng(seed, *path): pure, order-independent
galaxy/core/grids.py      GridSpec(n_R=400, n_t=2000, n_z=60, n_phi=360) -> Grid
galaxy/core/special.py    I1, K0, K1 (Abramowitz & Stegun 9.8); numpy has only i0
galaxy/models/level0.py   the physical constants every model shares
galaxy/models/            simple.py, advanced.py (stub until S9; differs by CANARY)
galaxy/stages/halo.py     NFW halo, R200, c200, the M200 -> dark + baryons split
galaxy/stages/disc.py     MMW98 scale length; Freeman + a general razor-thin solver
galaxy/stages/assembly.py   mergers[]: gas delivery and vertical heating (cp 2)
galaxy/stages/sfh.py      two-infall accretion, Kennicutt-Schmidt, gas/star split
galaxy/stages/chemistry.py  Z(R,t), [Fe/H], the gradient, radial migration
galaxy/stages/vertical.py   thin/thick split, scale heights, rows 5-11
galaxy/specs/             graph.py, preflight.py, determinism.py, spec.py; `python -m galaxy.specs`
galaxy/run.py             run(model, inputs=None, grid=None) -> Outputs(fields, decls, order)
tools/                    progress.py, bootstrap.py, verify_clone.py, hooks/pre-commit
tests/                    pytest; helpers.py builds synthetic stages/models
DECISIONS.md LESSONS.md   append-only; lessons tagged by stage type
MANUAL_TODO.md            queued session tags; add yours, fill in the last one (C2e)
BRIEF.md                  the next session's brief, written by the previous one
```

## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`.
- Each published field is a `FieldDecl` beside its compute: name, label, unit,
  kind, axes in `(R, t, z, phi)` order, ramp, meaningful_zero, provenance, about.
- `compute(ctx)` sees `ctx.grid`, `ctx.inputs`, `ctx.constants`, `ctx.fields`
  (strict) or `.get()/.has()` (optional), `ctx.rng(seed, *path)`. Only declared
  names resolve.
- Return exactly the declared names. The runner checks shape and value class.
- Register with `IMPLEMENTATIONS.register(...)`, import it in
  `galaxy/stages/__init__.py`, map the slot in **both** models. A new Level 0
  constant goes in `models/level0.py`, and only if a stage reads it (D29).

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants
  `UPPER_SNAKE`. 7 controls, 4 seeds, `mergers`. **Every input now has a default
  and every control a range**; the `tests/test_registry.py` ratchets are at zero
  and must stay there.
- Every factual claim in every document is tagged `[verified: cite]`, `[recall]`
  or `[inferred]` (rule B14); a bare verified tag fails a test.
- Debts live in GALAXY_INPUTS.md §11; `tools/progress.py` counts them onto the
  board — add a numbered item, never edit the count. A new unit, kind, axis,
  object class or cmap is a `core/` edit plus a DECISIONS.md entry.
- A failing acceptance row goes in `spec.MISSES` with its debt, reason and a
  prediction that could kill it (D33); it still reports `fail`, never widen a
  target (B5), and a recorded miss that starts *passing* fails the run.

## What the instruments said at S3 close

- graph: acyclic for both models; order `halo -> assembly -> disc -> sfh ->
  chemistry -> vertical`; all 8 non-seed inputs bound, none contradicting §3.
- preflight: OK; 0 inputs UNSET; 0 controls without a range.
- determinism: OK; golden values pinned under numpy 2.5.2.
- spec: **8 pass** (1, 4, 6, 7, 8, 9, 10, 19), **7 fail** (2, 3, 5, 11, 20, 22,
  23 — every one a recorded miss), 9 not-yet-computable. Exit 0.
- **Read D51 before trusting row 9.** It is the gate and it passes on two errors
  cancelling; a test asserts the cancellation.
- Numbers, to recognise a regression by: R₂₀₀ = 212.94 kpc, c₂₀₀ = 14.35,
  R_d(λ_d) = 2.605, R_d(fitted) = 2.49 kpc, M_star = 5.276e10, M_gas = 5.80e9,
  SFR = 1.969, v_tan = 256.0 km/s, [Fe/H](R₀) ≈ 0, gradient = −0.0237,
  thick M = 1.07e10, thick R_d = 1.17 kpc, h_thin = 253 pc, h_thick = 1039 pc,
  σ_z thin/thick = 20.1/40.7 km/s, row 9 = 0.103.
- **Three causes hold seven failing rows**: #18 (no extended accretion) has 2, 3,
  20; #15 (every gradient a third of observed) has 22, 23; #19 (the thick disc's
  shape, and the gate's compensation) has 5, 11.

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board — surface, model **actually used**, tag, date;
   `uv run python tools/progress.py`.
1. `uv run pytest` — full suite once, quiet.
2. Append to DECISIONS.md; new rules into LESSONS.md, tagged.
3. Rewrite this file in place (≤ 120 lines).
4. Write BRIEF.md for the next session (≤ 60 lines).
5. Commit; `git checkout main && git merge --no-ff session-NN` with the subject
   `Merge S<N> into main: …`; push branch and main. **Do not tag** (rule C2e) —
   add your row to MANUAL_TODO.md and fill in the previous session's merge SHA.
   Never force-push (rule C2a).
6. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps,
   runs the suite and the specs there; refuses if the working tree is dirty.

A session that stops early closes **partially** instead (rule C2d): commit,
push, write what remains into BRIEF.md, mark the board row ◐ — and do **not**
merge. The branch stays open and the next session continues on it.

## Credentials

Push through the git credential helper or a fine-grained token scoped to this
repository (Contents: read and write). Nothing credential-shaped enters the tree;
the hook refuses token shapes. `.github/workflows/` needs workflow permission.
Do not attempt to push a tag: the proxy refuses tag refs with a 403 whatever
credential is used, so tags are queued in MANUAL_TODO.md (rule C2e).
