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
galaxy/stages/disc.py     MMW98 scale length, Freeman rotation curve, v_c(R0)
galaxy/specs/             graph.py, preflight.py, determinism.py, spec.py; `python -m galaxy.specs`
galaxy/run.py             run(model, inputs=None, grid=None) -> Outputs(fields, decls, order)
tools/                    progress.py, bootstrap.py, verify_clone.py, hooks/pre-commit
tests/                    pytest; helpers.py builds synthetic stages/models
DECISIONS.md LESSONS.md   append-only; lessons tagged by stage type
MANUAL_TODO.md            queued session tags; add yours, fill in the last one (C2e)
BRIEF.md                  the next session's brief, written by the previous one
```

## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_inputs, reads_seeds,
  reads_constants, requires, requires_optional, publishes)`.
- Each published field is a `FieldDecl` beside its compute: name, label, unit
  (from `core/units.py`), kind, axes in `(R, t, z, phi)` order, ramp,
  meaningful_zero, provenance (`derived` or `seeded`), about.
- `compute(ctx)` sees `ctx.grid`, `ctx.inputs[...]`, `ctx.constants[...]`,
  `ctx.fields[...]` (strict) or `.get()/.has()` (optional), `ctx.rng(seed, *path)`.
  Only declared names resolve; anything else raises.
- Return exactly the declared names. The runner checks shape and value class.
- Register with `IMPLEMENTATIONS.register(...)`, import the module in
  `galaxy/stages/__init__.py`, and map the slot in **both** models.
- A new Level 0 constant goes in `models/level0.py`, not in a model — but only
  if some stage reads it, or preflight fails it as dead (D29).

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
- Inputs: 7 controls, 4 seeds, `mergers`. UNSET defaults (3 now) raise only when
  a stage reads them. Ratchet tests in `tests/test_registry.py` bound the debt
  from above (unset ≤ 3, controls without a range ≤ 3); lower them when you
  discharge one, never raise them.
- Every factual claim in every document is tagged `[verified: cite]`,
  `[recall]` or `[inferred]` (rule B14); a verified tag without a citation fails a test.
- Debts live in the register at GALAXY_INPUTS.md §11; `tools/progress.py`
  counts them onto the board. Add a numbered item; never edit the board's count.
- Any new unit, kind, axis, object class or cmap is an edit to `core/` plus a
  DECISIONS.md entry.
- An acceptance row that fails goes in `spec.MISSES` with its debt number, a
  reason and a prediction that could kill the reason (D33). It still reports
  `fail`. Never widen a target (rule B5). A recorded miss that starts passing
  fails the run, so a spent explanation cannot linger.

## What the instruments said at S1 close

- graph: acyclic for both models; order `halo -> disc`; 4 of 12 inputs bound,
  all at checkpoint 1 and none contradicting GALAXY_PLAN.md §3's hypothesis.
- preflight: OK; 3 inputs with UNSET default; 3 controls without a range.
- determinism: OK; golden values pinned under numpy 2.5.2.
- spec: 3 pass (rows 1, 4, 19), 1 fail (row 3, a recorded miss), 20
  not-yet-computable, for both models. `python -m galaxy.specs` exits 0.
- The numbers, for the next session to recognise a regression by:
  R₂₀₀ = 212.94 kpc, c₂₀₀ = 14.35, r_s = 14.84 kpc, m_d = 0.0533,
  M_baryon = 5.859 × 10¹⁰ M☉, R_d = 2.6049 kpc, Σ₀ = 1374 M☉/pc²,
  v_halo(R₀) = 159.84, v_c(R₀) = 243.85, v_tan(R₀) = 256.09 km/s.

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

Push through the machine's git credential helper or a fine-grained token scoped
to this repository (Contents: read and write). Nothing credential-shaped enters
the tree; the hook refuses token shapes. Editing `.github/workflows/` needs
workflow permission on the token. Do not attempt to push a tag: the web
environment's proxy refuses tag refs with a 403 whatever credential is used, so
tags are queued in MANUAL_TODO.md and applied by hand at the end (rule C2e).
