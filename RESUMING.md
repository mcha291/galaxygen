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
when BRIEF.md names one. Push the session branch at least once mid-session.

## Layout

```
galaxy/core/units.py      closed unit vocabulary (ASCII symbols, display forms)
galaxy/core/fielddoc.py   FieldDecl, Kind (6), Ramp/Palette, AXES, OBJECTS, CMAPS
galaxy/core/stage.py      Stage declaration, Context (restricted views), CHECKPOINTS
galaxy/core/registry.py   INPUTS (12), Input/Constant/Model, MODELS, IMPLEMENTATIONS, production()
galaxy/core/seeds.py      child(seed, *path), rng(seed, *path): pure, order-independent
galaxy/core/grids.py      GridSpec(n_R=400, n_t=2000, n_z=60, n_phi=360) -> Grid
galaxy/stages/            one module per implementation; registers itself; stub.py at S0
galaxy/models/            simple.py, advanced.py (stub until S9; differs by CANARY)
galaxy/specs/             graph.py, preflight.py, determinism.py, spec.py; `python -m galaxy.specs`
galaxy/run.py             run(model, inputs=None, grid=None) -> Outputs(fields, decls, order)
tools/                    progress.py, bootstrap.py, verify_clone.py, hooks/pre-commit
tests/                    pytest; helpers.py builds synthetic stages/models
DECISIONS.md LESSONS.md   append-only; lessons tagged by stage type
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

## Conventions

- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`.
- Inputs: 7 controls, 4 seeds, `mergers`. UNSET defaults (4 at S0) raise only
  when a stage reads them. Ratchet tests in `tests/test_registry.py` bound the
  debt from above; lower them when you discharge it.
- Every factual claim in every document is tagged `[verified: cite]`,
  `[recall]` or `[inferred]` (rule B14); a verified tag without a citation fails a test.
- Debts live in the register at GALAXY_INPUTS.md §11; `tools/progress.py`
  counts them onto the board.
- Any new unit, kind, axis, object class or cmap is an edit to `core/` plus a
  DECISIONS.md entry.

## What the instruments said at S0 close

- graph: acyclic for both models; 12 of 12 inputs unbound (no stage reads one yet).
- preflight: OK; 4 inputs with UNSET default; 7 controls without a range.
- determinism: OK; golden values pinned under numpy 2.5.2.
- spec: 24 of 24 not-yet-computable for both models; 0 fail.

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board, fill tag and date; `uv run python tools/progress.py`.
1. `uv run pytest` — full suite once, quiet.
2. Append to DECISIONS.md; new rules into LESSONS.md, tagged.
3. Rewrite this file in place (≤ 120 lines).
4. Write BRIEF.md for the next session (≤ 60 lines).
5. Commit; `git checkout main && git merge --no-ff session-NN && git tag sNN`;
   push branch, main and tags. Never force-push (rule C2a).
6. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps,
   runs the suite and the specs there; refuses if the working tree is dirty.

## Credentials

Push through the machine's git credential helper or a fine-grained token scoped
to this repository (Contents: read and write). Nothing credential-shaped enters
the tree; the hook refuses token shapes. Editing `.github/workflows/` needs
workflow permission on the token.
