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
- [close] `git tag -d` is local only; a remote tag needs
  `git push origin :refs/tags/<name>`. Confirm with `git ls-remote` rather than
  on report — S2 wrote "deleted" into a tracked file on the strength of a
  message and the tag was still there.
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

## From S3

- [field][advanced] A passing check can be two errors cancelling. Row 9 passes
  because the thick disc is both too massive and too compact; fixing either one
  alone breaks it. Before believing a green row, move the thing it depends on
  and see whether it moves for the right reason `[verified: DECISIONS.md D51]`.
- [field][advanced] When one knob has to satisfy several criteria, sweep it and
  see whether *any* value satisfies them. `GAS_DISC_SCALE_RATIO` cannot: the
  structure rows want ≤ 1.25 and the gas rows ≥ 1.35. That turns "the model is
  miscalibrated" into "the model is missing a component" (debt #18).
- [field] Set a constant from the end of the relation it is defined at.
  `SECULAR_HEATING` is the dispersion at 10 Gyr and had been given the 5 Gyr
  value, which halved the thin disc's thickness `[verified: DECISIONS.md D54]`.
- [field][advanced] A control run is worthless if the thing it varies is what
  defines the measurement. The merger-free galaxy has no thick disc because the
  split is *defined* as "born before the last major merger" — a circularity, not
  a result (debt #20) `[verified: DECISIONS.md D53]`.
- [field][advanced] Before reporting a null result, check the instrument can see
  the signal. The simple model has one abundance, so it has no α–Fe plane and
  cannot find bimodality in it whatever the mergers do (rule B3).
- [field] Deliver an accretion episode over its own decay, not as a burst. A
  merger delivering its gas over a crossing time made the SFR a function of the
  timestep — the same defect class as the hard star formation threshold (D46).
- [all] Check a formula's constant factor against a worked case. The brief wrote
  h_z = σ_z²/πGΣ, missing the isothermal sheet's 2, which would have made every
  scale height twice too large and still looked plausible.

## From S4

- [field][catalogue][advanced] Provenance is derived **per stage**: a stage that
  reads a seed publishes seeded fields, all of them. If one field of a stage is
  genuinely reproducible and another is drawn, split the stage rather than
  mislabel either (rule A10) `[verified: DECISIONS.md D55]`.
- [field][advanced] Measure what a relation actually contributes before trusting
  it. The pitch–shear trend holds 0.3% of the pitch variance because the model's
  rotation curves are near-flat whatever the inputs, so a wrong slope would look
  exactly like the right one (rule B11) `[verified: DECISIONS.md D57]`.
- [field] A statistical acceptance row needs something to build the ensemble, not
  just a rule for judging one. Rows 16 and 17 reported not-yet-computable for four
  sessions because the criterion existed and the 20 draws did not (D58).
- [field][advanced] Derive what you can and draw only the residual. The pattern
  speed is v_c(R_CR)/R_CR exactly — a definition — so its scatter is all inherited
  from the one quantity that is genuinely drawn, and there is one place to look
  when it moves.
- [all] When two project documents disagree, prefer the one the machinery depends
  on. §5 puts the pitch draw on `world_seed`; the registry and the plan put it on
  `pattern_seed`, and only the latter keeps rerolling the arms from invalidating
  checkpoint 1 (D56).

## From S5

- [catalogue] Give each *property* its own seeded stream, not each object. Then a
  small sample is a strict prefix of a large one and a region is identical alone
  or inside a sweep — both for free, from identity rather than from care
  `[verified: DECISIONS.md D60]`.
- [catalogue] Anything a per-cell draw is keyed on must come from the *field*,
  not from the stars the cell realised. Keying the age CDF on the realised mean
  radius made a cell's ages depend on how many stars were asked for, and it was
  invisible until the prefix property was asserted.
- [catalogue] Invert the CDF, never reject-sample: the density is already
  published, so the draw is exact and its cost does not depend on how peaked the
  galaxy is (rule B8). The mean of a known distribution is computed, not sampled.
- [catalogue][api] Check a sample against the *field* it was drawn from, never
  against its own histogram (rule B3) — a sample tracing the wrong density is
  still internally consistent.
- [infra] A suite that builds an ensemble per test runs for minutes. Build it once
  per session; twenty pipeline runs is the cost of one statistical row.
- [catalogue][advanced] Cost that is paid per cell is paid whether or not anyone
  asks for that cell. numpy's `Generator` construction is ~22 µs and dominated the
  whole model run before the cell grid was sized against it (D61).

## From S6

- [api][viewer][all] Publish what a response *did*, not how long it took. Every
  response carries the stages it ran, and the rule-D4 assertions read that: a
  timing says only which rows a cache serves, and an endpoint that ran the whole
  pipeline sits in the same range as one that ran nothing `[verified:
  DECISIONS.md D67]`.
- [api][viewer] "This endpoint runs no stage" is checked by taking the runner out
  of its path and calling it again. Observing that it did not run one is a check
  on the run; observing that it *could not have* is a check on the route.
- [api][all] A partial run is only safe if it cannot be resumed from a different
  galaxy. Refuse a resume whose model, grid or inputs differ — mixing two input
  vectors publishes a self-consistent galaxy that no input vector generates, and
  nothing downstream can detect it (D63).
- [api][catalogue] A star belongs to the cell that drew it, not to the cell its
  radius falls in: inverting a ring's CDF can place it up to one R-spacing
  outside its own ring (D69). Anything that maps positions back to cells is
  fuzzy by that much, by construction.
- [api][viewer] JSON has no NaN. A non-finite scalar goes out as `null`, and a
  browser will refuse to parse the alternative (rule B9).
- [api][viewer] Pad a binary payload to eight bytes. `new Float64Array(buffer,
  offset, n)` throws on a misaligned offset, and an int64 column arrives as
  `BigInt` — convert once, where the conversion can be seen.
- [api][viewer] Write the one-`fetch` gate over the file *tree*, not over the
  file you just wrote. The viewer S7 adds is then covered without anyone
  remembering to extend it (rule B13).
- [api][infra] node is installed here and on the CI runner, so a JS decoder is
  run rather than mirrored in Python. A twin gets alignment, endianness and
  BigInt right by construction and tells you nothing (rule B3). Skip where the
  runtime is absent — a skip is visible, a silent pass is not.
- [infra][all] A tool that must be run every session needs a test that fails when
  it is not extended. `tests/test_api.py` asserts every route appears in
  `tools/timings.py`, so a new endpoint cannot go unmeasured.

## From S7

- [viewer][api][all] Put every rule-bearing decision in a pure module and leave
  the DOM a shell. Rule D1 is four claims about *state*, and state can be
  asserted; on a screen it would be checked by looking, which is the one access
  path immune to the defect (rule B3, D70).
- [viewer][all] `Number(null)` is 0 in JavaScript, and `null` is exactly how this
  API publishes a number the model does not have. A missing value would be drawn
  the colour of zero and read as a measurement — rule B9's failure arriving
  through a language feature. Coerce in one place, and make it return NaN (D72).
- [viewer][api] Rule D4 can be broken from the client side: asking for a scalar
  runs the stage that publishes it, and one of them materialises a 20 000-star
  catalogue. Decide what to request from the declarations — a scalar whose stage
  also publishes object columns is never worth a stage (D73).
- [viewer][api] Publish the colours behind a cmap name, do not let the client
  hold them. Then the A9 gate can be written as an absence — no colour literal
  and no cmap name in the client's JavaScript — and an absence cannot drift.
- [viewer] Say what the picture does not have, and derive the sentence. The disc
  is axisymmetric because no field has a phi axis, so the viewer asks that
  question rather than carrying a note somebody typed: when a stage publishes one,
  the sentence goes away by itself (D75).
- [viewer][all] Uniform beats memorable in a client API. A mixture of
  `f(model, options)` and `f(options)` produced `model=[object Object]` the first
  time the transport was called from outside the file that wrote it.
- [viewer][catalogue] Render it and look. Three defects — a checkpoint opening on
  a non-physics probe field, a constant drawn on the floor where it reads as zero,
  a legend overflowing its column — were invisible to every assertion worth
  writing and obvious in one screenshot (`tools/shot.py`, D77).
- [viewer][infra] Node's test runner needs the files named: `node --test <dir>`
  loads the directory as a module and fails. Glob them in the wrapper, and assert
  the glob is non-empty so an empty run cannot look like a passing one.

## From S8

- [catalogue][api][all] Identity is not a field. It has no unit, no meaningful
  zero and nothing to draw, and forcing it into a declaration means inventing all
  three. Let it travel in the *shape* of the answer — the runs a catalogue was
  built from — and the contract stays honest (D81).
- [catalogue][advanced] The isolation mass is an embryo's, not a planet's: ~0.02
  M⊕ at 1 AU. A model that assigns it directly builds systems of gravel. Partition
  the disc and let the stability criterion filter, which is what §12 sanctions it
  for (D83).
- [catalogue] A merge changes the thing it merged into. Filtering pairs of
  neighbouring *slots* left crowded pairs behind, because the survivor got heavier
  after the pair before it was checked; sweep and carry the survivor forward.
- [field][all] Do not write down the relation the literature quotes if the
  mechanism can produce it. Deriving occurrence made β a measurement, and the
  measurement showed that two numbers cited in the same paragraph of our own
  inputs document cannot both be true (debt #25, D79).
- [field][all] When two cited claims conflict, the model's job is to say which one
  its mechanism agrees with — not to average them (rule B12) and not to fit both.
  Fit one constant, publish the rest as predictions, and record the disagreement.
- [all] A quantity that scales the same way everywhere can be lifted out of a
  per-cell computation. Occurrence over an 800 000-cell history built an
  800 000 × 8 intermediate until the part that depends only on the star was
  separated — 1.5 s of a 2.5 s run, from arithmetic that was already correct.
- [close][infra] Never `git checkout <file>` to undo a temporary edit to a file
  that has uncommitted work in it: it reverts to HEAD, not to your edit's start,
  and takes the day's work with it. Copy the file aside, or commit first. This
  cost the viewer's system view once, in this session.
- [viewer] Three decades on a linear axis draws every inner planet on top of the
  star. A system view is logarithmic, and because that is a decision about how the
  picture is read, it belongs in a module where it can be asserted.

## From S9

- [advanced][field] Run the prediction the register made, then write down what
  happened either way. Debt #15's "outflows steepen the gradient" held for row
  22 and S2's "then migration is wrong too" fired for row 23 — one session,
  one mechanism, both a confirmation and a kill `[verified: DECISIONS.md D90]`.
- [advanced][field] Make the criterion a *result* and accept what it finds. The
  chemical thin/thick split found no thick disc at all, which is seven red
  rows and the honest answer; a fixed [α/Fe] threshold would have produced one
  and taught nothing `[verified: DECISIONS.md D88, D91]`.
- [advanced][field] Check a detector on a signal you know is there before
  believing its null. The bimodality reader counted a bump on a tail as a mode
  until it was tried on a distribution that *is* bimodal; then it needed a
  mode to hold real mass.
- [advanced][audit] A miss belongs to a model. The moment two models judge one
  table, "recorded" and "stale" can both be true of a row, and the register has
  to say whose explanation it is (rule A7) `[verified: DECISIONS.md D87]`.
- [advanced][audit] Publish the exponent and the control together. The binned
  kernel's 0.77 means nothing on its own; beside the naive form's 2.04 on the
  same histories it is a measurement of the algorithm `[verified: DECISIONS.md D92]`.
- [advanced][field] A model's own stage may require its own optional field;
  only a *shared* stage must handle absence. A rule written when both models
  published identical fields fired the first time they did not (D86).
- [infra] `node --test` prints the spec reporter under node 24 even when
  captured; name the reporter (`--test-reporter=tap`) or a TAP assertion fails
  on the machine and passes in CI.
- [close] Kahn's algorithm here runs in rounds, so remapping one slot can move
  stages that did not change: the advanced vertical stage lands three places
  later than the simple one's because it waits on the chemistry. Orders are per
  model; assert them per model.

## From S10

- [audit][all] A sweep in which nothing drifts and an instrument that cannot
  fire look identical from the sweep alone. Give every convergence knob a
  deliberately too-coarse control point and record what it did, so the
  demonstration is part of the measurement rather than an argument beside it
  (rule B3) `[verified: DECISIONS.md D94]`.
- [audit][all] Judging a drift against the width of its own acceptance target
  is the right *criterion* and a very loose one: the worst margin here is 0.056
  of a width, so the check passes with a factor of 18 to spare and would keep
  passing through a real regression. Publish the margin next to the verdict —
  a row at 0.001 widths and a row at 0.9 widths are not the same finding.
- [audit][field] Sweep the axis nobody asked you to sweep. N_z was outside the
  brief, and it is the one that turned out to buy nothing: one field on the
  axis, one consumer, and it reads column 0 `[verified: GALAXY_INPUTS.md §11
  debt #30]`.
- [audit][all] Ask what the acceptance table *cannot* see. Every row here is a
  summary quantity or an integral, so nothing reads the inner disc, and the
  model's worst number — a full dex above what real bulges reach — sits where no
  row looks. Coverage is a property of the table, and only an audit checks it.
- [audit][all] A two-point difference is not a decomposition. Differencing the
  whole-galaxy and nine-cell catalogues to split fixed cost from per-star cost
  returns a *negative* cost per star, because both points sit at the same
  stars-per-cell ratio. Fit a slope over a range wide enough to condition it —
  the same reason rule B7 prefers an exponent to a stopwatch `[verified:
  DECISIONS.md D96]`.
- [audit][infra] A per-stage cold profile bills the interpreter's one-off costs
  to whichever stage trips them first. 8.9 ms of numpy bit-generator setup made
  `pattern` read at 30× cold-over-warm. Measure the one-off separately and
  publish it beside the table rather than paying it before the loop: paying it
  first tidies the table and destroys the evidence that the effect exists.
- [audit][all] When a re-examined constant turns out to close a failing row, the
  finding is the *discriminator*, not the fix. Two explanations for one miss are
  worth more than one, provided you also record the measurement that tells them
  apart — here rows 2 and 20, which one explanation moves and the other does not
  `[verified: DECISIONS.md D95]`.
- [audit][all] Re-measure a debt's own stated magnitude, not just its claim.
  Debt #12 said 10 km/s and three error bars; two sessions of unrelated work
  later it was 15.3 km/s and five. The claim was still true and the number that
  made it actionable had gone stale.
- [close][infra] A gate that walks the filesystem behind a denylist of directory
  names widens silently. A sibling git worktree checked out under `.claude/`
  made the one-fetch gate read files this repository never wrote. Ask git what
  the repository contains (rule B13) `[verified: DECISIONS.md D99]`.
- [audit][advanced] A coarse grid can manufacture the signal you are hunting: at
  N_t = 8 the advanced model reports the [α/Fe] valley debt #27 exists to find.
  State the grid beside any qualitative verdict.
