# BRIEF — Session 9: the advanced model

Open per RESUMING.md. Read RULES.md in full — **A1, A6, A7, B7 and B10 are the
ones this session lives on** — then this. Do not read GALAXY_PLAN.md. Read
GALAXY_INPUTS.md **§8** (the advanced axes) and **§10** (the measured cost
model); consult §11 only for the debts named below.

The board says **Fable** runs this one.

## Build

The advanced model has mapped the same stages as `simple` since S0, differing by
one constant. S9 gives it implementations of its own where it genuinely differs,
and leaves the rest shared — that is what the two-model discipline was built for
and this is the session it finally exercises.

- **Multi-element chemistry with a delay-time distribution.** Iron from SNIa
  arrives late, α from core collapse arrives promptly, and the simple model's
  instantaneous recycling collapses the two into one. This is what makes an
  α/Fe plane exist at all, and **acceptance row 24 becomes computable**: give it
  a `category_scalar` and an `expect` in `spec.py` (rule C6).
- **Outflows**, which debt #15 predicts will fix the gradients — rows 22 and 23
  come out a third of the observed slope with no mechanism to remove metal
  preferentially from the outer disc.
- **Radial migration** as a mechanism rather than the simple model's kernel.
- **Delete `CANARY`** and the canary field: they exist only while the advanced
  model is a stub, and this session ends that. `tests/test_models.py` asserts the
  two models differ — make it assert something real instead.

## Gate

- **The N_t scaling exponent is 1.0, not 2.0** (rule B7). The naive DTD is a
  convolution at every timestep and is quadratic in time resolution; measure the
  exponent across at least three N_t and publish it, do not time one grid.
- **The coupling multiplier is measured**, and rule A1 still holds: no fixed-point
  solver on the grid. Bounded, cheap iteration only — the coupled fixed point is
  an 8× multiplier no implementation recovers.
- `preflight` reconciles both models: a field name that both publish must carry
  the **same contract**. If multi-element chemistry changes what `feh_history`
  means, it needs a new name, not a new declaration.
- Cold timings published, both models (B2, D84).

## Traps

- **Rule B10 first.** `NET_YIELD` = 0.011 is an effective yield calibrated
  against a model with no outflows (debt #16). The moment outflows exist it has
  no claim on its value and must be re-derived — before anything is judged.
- **Debt #20 blocks debt #9.** The thin/thick split is *defined* as "born before
  the last major merger", so a merger-free run cannot be evidence about mergers.
  A criterion grounded in kinematics or chemistry has to come first; then the
  merger-free α-bimodality test means something.
- Rule A7: advanced-model findings are stored separately from the simple pass.
- Every test takes the `model` fixture, so tests that quietly assume the two
  models agree will start failing. That is the S0 stub paying off, not a problem.
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill in
  S8's merge SHA from `git rev-list -1 --grep='^Merge S8 into main' origin/main`.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`.
