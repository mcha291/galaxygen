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
- [field] `CANARY` now lives in the halo stage; the stub is gone. It is S9's to
  delete, when the advanced model gets a stage map of its own. Until then
  `tests/test_models.py` is the only thing keeping the two-model boundary
  exercised, so a change that makes the two models identical must fail it
  rather than quietly pass.
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

## From S1

- [field][advanced] A relation and the constant fitted to it must use the *same*
  definitions. λ_d = 0.0144 was inferred against a top-hat virial radius and
  used with an r₂₀₀ 20% smaller; the symptom was a scale length 17% low, well
  inside the acceptance window and therefore invisible to the gate `[verified:
  DECISIONS.md D30]`. Before trusting any inherited constant, ask what radius,
  mass and overdensity it was measured against.
- [field][advanced] Ask what overdensity a quoted (M, R) pair implies rather
  than trusting its label. "Virial" names at least two conventions that differ
  by 25% in radius; the arithmetic settles it in one line `[verified:
  tests/test_disc.py::test_the_255_kpc_is_a_top_hat_radius_not_R200]`.
- [field] Publish a quantity an acceptance row reads as an analytic scalar, not
  interpolated off the grid. Otherwise the S10 convergence sweep moves an
  acceptance number, and N_R stops being a quality knob `[verified:
  DECISIONS.md D37]`.
- [field] Fit a parameter only against a mechanism the model actually has.
  `baryon_retention` could have been fitted to make two more rows pass; the
  budget it names includes gas the model does not have yet, so the fit would
  have been undone at S2 (rule B10) `[verified: DECISIONS.md D32]`.
- [field][all] A failing acceptance row is recorded in `spec.MISSES` with its
  debt, a reason and a prediction that could kill the reason. It still reports
  `fail`; only the process exit status distinguishes explained from
  unexplained, and a recorded miss that starts *passing* is itself an error
  `[verified: DECISIONS.md D33]`. Never widen a target to get green.
- [field] Two stages may not both know one fact. The halo publishes its own
  v_c(R₀) as a scalar so the disc can add to it without a second copy of the
  NFW formula (rule A9) `[verified: DECISIONS.md D36, D37]`.
- [field] Check a definition by inverting it, never by re-running the formula
  the stage used. R₂₀₀ is tested by confirming the sphere encloses 200 ρ_crit
  (rule B3) `[verified: tests/test_halo.py::test_R200_encloses_200_rho_crit_by_construction]`.
- [all] Transcribed numerical coefficients need golden values. A mistyped digit
  in a Bessel approximation shifts v_c by a fraction of a percent, which is the
  size of an acceptance error bar and looks like physics `[verified:
  DECISIONS.md D28]`.
- [close] Do not try to tag. The web environment's proxy refuses tag refs with
  HTTP 403 — the GitHub API says the *path* is not permitted, so it is a policy
  and not a token permission, and no credential fixes it. Queue the command in
  `MANUAL_TODO.md` instead (rule C2e) `[verified: DECISIONS.md D40]`.
- [close] When a ritual step cannot succeed in this environment, change the
  ritual rather than repeating the failure or quietly skipping it. A close that
  ends in a guaranteed error trains everyone to ignore the error.
- [close] Before rewriting history, check `git ls-remote` for **tags**, not just
  the branch head. A rewrite invalidates every ref pointing into the rewritten
  range, including refs someone else pushed while the session was working;
  S1 orphaned a hand-pushed `s01` exactly this way `[verified: DECISIONS.md
  D41]`.
- [infra] `tools/progress.py` counts debts straight out of GALAXY_INPUTS.md
  §11's register, so adding a numbered item is all it takes to move the board's
  debt line; do not edit the line.

## From S2

- [field][advanced] Sweep the grid before believing a scalar. S2's star formation
  rate wandered between 1.47 and 1.79 with **no trend** in either N_R or N_t
  while every other scalar converged to 0.1%; no trend is the signature of an
  artefact rather than a truncation error, and the row it fed was "passing" by
  grid alignment `[verified: DECISIONS.md D46]`.
- [field][advanced] A hard threshold inside an integral is a defect when the
  system self-regulates *to* the threshold, because then the answer depends on
  which side of it each cell lands. Smooth it; nature's thresholds are not steps
  either.
- [field] Establish what a constant does **not** affect, not only what it does.
  The gradient turned out exactly insensitive to the yield, which killed the
  obvious explanation for it being too flat and made calibrating the yield cost
  nothing `[verified: DECISIONS.md D47]`.
- [field] Check a quoted relation against the numbers quoted beside it.
  GALAXY_INPUTS.md §3 gives τ₀ "at R₀" in one row and τ₀(R/R_d)ⁿ in the next;
  they differ by a factor of three, and the source's own τ_D(R) settles it
  `[verified: DECISIONS.md D43]`.
- [field] Freeman's formula is exact for an exponential and for nothing else. A
  gas disc shaped by a star formation threshold is flat then falling, and its
  fitted "scale length" depends only on the fitting range. Decompose onto an
  exponential basis and superpose — Poisson is linear `[verified: DECISIONS.md D44]`.
- [field] When two independent routes to one quantity disagree, that is a result,
  not a tolerance to be split. λ_d and the star formation history give disc scale
  lengths 44% apart and two acceptance rows fail on it; averaging them would have
  hidden the finding and fixed nothing `[verified: DECISIONS.md D48, debt #13]`.
- [field][all] A prediction recorded by an earlier session is there to be run, not
  honoured. S1's row 3 prediction was directionally right and numerically wrong;
  the entry gets updated with what actually happened (rule B5).
- [all] A quantity an acceptance row reads must not be interpolated off the grid
  *or* be a discontinuous functional of it. Both make N_R a physics parameter.
