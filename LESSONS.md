# Lessons

Tags: `all` `infra` `field` `catalogue` `api` `viewer` `advanced` `audit` `close`
— a session reads only the bullets carrying its tags (rule C5). `field` is a
grid-physics stage (S1–S4), `catalogue` an object stage (S5, S8), `advanced`
the S9 model, `audit` S10, `close` the session protocol, `infra` this
repository's tooling, `all` everyone. One bullet per lesson; tags first.

## From S0

- [all] Read and write text with `encoding="utf-8"` and reconfigure stdout
  before printing non-ASCII. Windows defaults to cp1252 and the first spec
  report crashed on a subscript character `[verified: DECISIONS.md D22]`.
- [all] Never derive randomness from Python's `hash()`; it is salted per
  process for strings. Use `galaxy.core.seeds` (BLAKE2b path hashing,
  `SeedSequence` spawn keys) `[verified: DECISIONS.md D18]`.
- [all] Any test that touches a model takes the `model` fixture and runs once
  per registered model. A test written against `simple` alone is how the
  two-model boundary rots `[verified: tests/conftest.py]`.
- [all] Tag every factual claim in every document; `tests/test_docs.py`
  rejects a verified tag that has no colon and citation after it.
- [field][catalogue][advanced] A stage may read only what it declares.
  `UndeclaredAccess` means "declare it in the Stage", never "reach around the
  context". Optional fields go in `requires_optional` and are read with
  `ctx.fields.get()` / `.has()`; subscripting them raises even when present.
- [field][catalogue][advanced] Return exactly the declared field names with the
  declared shape; axes are `(R, t, z, phi)` in that order. The runner rejects a
  transposed array, an extra key and a missing key.
- [field][catalogue][advanced] Constants are `UPPER_SNAKE`, declared per model
  with a unit and an `about`, and read via `reads_constants`. A constant no
  stage reads fails preflight; a constant one model lacks fails preflight.
- [field][catalogue][advanced] A spec row names the exact scalar field it
  reads (`galaxy/specs/spec.py` QUANTITIES). Publish under that name with that
  unit, as kind `scalar`, or the row stays not-yet-computable; a unit mismatch
  is a `fail`, not a warning.
- [field] The stub stage and `CANARY` are S1's to delete. `tests/test_models.py`
  must keep passing after the move: keep one constant the two models differ on,
  read by a real stage, or the canary guard has nothing to guard.
- [audit][all] Ratchet tests encode debt as a one-way bound (unset defaults ≤ 4,
  controls without range ≤ 7 at S0). When you discharge a debt, lower the bound
  in the same commit; a bound that stays loose is a board that lies quietly.
- [infra] GALAXY_PLAN.md §5a points at GALAXY_INPUTS.md §11 for the input
  table; the table is §3. §11 holds the rulings and the debt register, and
  `tools/progress.py` counts debts from that register.
- [infra] On Windows a Bash command longer than about 8 KB fails with a
  misleading quoting error (command-line length limit). Write long files with a
  file tool, not a heredoc.
- [close] Close in order: tick the board, run `uv run python tools/progress.py`,
  then the suite. `tests/test_progress.py` fails while the board is stale, so a
  suite run before the regeneration is wasted.
- [close] The hook is installed per clone by `uv run python tools/bootstrap.py`.
  A clone without it has no token guard; `tests/test_hook.py` fails to remind
  you rather than letting a commit through.
- [close] Editing `.github/workflows/ci.yml` needs a token with workflow
  permission; a Contents-only fine-grained token's push is rejected for that
  file `[recall: GitHub fine-grained token permissions]`. Do not touch CI in a
  session whose token lacks it.
- [close] Verify with `uv run python tools/verify_clone.py --ref main` (rule
  C2). It refuses to start while the working tree has uncommitted or untracked
  files, which is the defect it exists to catch.
