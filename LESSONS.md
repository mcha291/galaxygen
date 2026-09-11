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

## From S10 (run 1)

- [audit][all] Sweep each grid axis alone and judge the drift against the row's
  own error bar, never a fixed percentage: a scalar is converged when the grid
  cannot move it across the width it is judged by, and a zero-width target
  makes a row untestable rather than failed `[verified: DECISIONS.md D94]`.
- [audit][all] A profile whose warm column matches its cold one is a profile; one
  that does not is a reading of a cache. Publish both columns so the reader can
  tell `[verified: DECISIONS.md D95]`.
- [audit][field] A row that passes because a constant was chosen inside its cited
  range is not evidence for the mechanism. Ask of every green row which constant
  could have been set to make it green, and whether it was (row 15, debt #21).
- [audit][all] Re-examine the *consumers* of a changed field, not only the stage
  that changed it: the advanced model's iron-rich centre moved giant occurrence
  by 7× at 2 kpc without the planets stage changing a line (D96).
- [audit][close] Two independent runs of one session means the first closes
  partially and the second continues the branch (rule C2d) — the instruments are
  shared, the findings are sealed in a file the second run must not open.

## From S10 (run 2)

- [audit][all] Move every constant across its own cited range and read the rows
  before writing "holds": three of run 1's verdicts written from the about lines
  alone were wrong (`SECULAR_HEATING`, `SF_THRESHOLD`, `GAS_DISC_SCALE_RATIO`)
  `[verified: DECISIONS.md D97]`.
- [audit][all] Trace every published field to a reader. A field nobody reads is
  a constant nobody tests: `merger_delivery` and `MERGER_DURATION` were dead for
  seven sessions under an about line describing a mechanism that never ran
  `[verified: AUDIT_RUN2.md D-1]`.
- [audit][all] Re-read the miss register's prose against the current numbers at
  every audit. A reason written at S2 was false from S3 and still quoted at S9
  `[verified: AUDIT_RUN2.md D-2]`.
- [audit][field] An input default is a constant too: ask what it delivers in
  mass. A gas fraction of 0.2 on a 1:50 satellite was 5.9 × 10⁹ M☉
  `[verified: AUDIT_RUN2.md D-7]`.
- [audit][all] Check a profile's warm column against its cold one per stage, not
  per total: the first seeded stage carries the process's first Generator and
  reads 46× warm `[verified: AUDIT_RUN2.md P1]`.
- [audit][close] Two independent runs need the register and the lessons sealed
  as well as the list. Run 1's amendments to three debts and one lesson carried
  every overlapping finding across, so the overlap measured the leak, not the
  agreement `[verified: DECISIONS.md D97]`.

## From S11

- [audit][close] Integrate audits by porting findings and tests, never by merging
  their branches: four implementations of two instruments on three branches
  conflict on fifteen files, while every test that pins a model measurement runs
  unchanged on the base because no audit changed physics — 137 did
  `[verified: DECISIONS.md D99]`.
- [audit][all] Rule B10 reaches the instruments' constants too. The default grid
  (debt #36) and `ENSEMBLE_MIN` (debt #38) were each chosen once and never
  re-derived, and each does something other than its name says. Audit the measuring
  apparatus with the same rule as the thing measured (session-10-beta).
- [audit][all] Ask which direction a check's errors point: "the ensemble's interval
  intersects the target" makes a noisier model easier to pass (debt #38). A
  criterion that cannot be failed by getting worse is not a criterion.
- [audit][all] Ask what the acceptance table cannot see. Every row is a summary
  quantity or an integral, so nothing reads the inner disc and the model's worst
  number sits where no row looks (debt #34). Coverage is a property of the table.
- [audit][all] A target's accounting is part of the target: row 20's 8.0 × 10⁹ M☉
  is hydrogen and the model's gas is every retained baryon, so the miss is 47%, not
  28% (debt #41). Check what a quoted mass counts before checking the number.
- [audit][field] A constant shared by two models can calibrate different rows in
  each (`MERGER_HEATING`, debt #42), and a constant that is a no-op at its default
  can still carry a row (`GAS_DISC_SCALE_RATIO` at 1.0, debt #45).
- [audit][field] Run the register's prediction with every knob it names before
  writing that it failed: debt #27's fast inner disc does nothing with the default
  merger list and opens the valley with one event delivering a fifth of the budget.
- [audit][infra] A two-point difference is not a decomposition — differencing the
  whole-galaxy and nine-cell catalogues returned a negative cost per star. Fit a
  slope over a range wide enough to condition it (`performance.SAMPLES`, D101).
- [audit][infra] A per-stage cold profile bills the interpreter's one-offs to
  whichever stage trips them first (10 ms of bit-generator setup on `pattern`).
  Measure the one-off separately and publish it beside the table; paying it before
  the loop tidies the table and destroys the evidence (debt #37).
- [audit][advanced] A coarse grid can manufacture the signal you are hunting: at
  N_t = 8 the advanced model reports the [α/Fe] valley debt #27 exists to find.
  State the grid beside any qualitative verdict.
- [audit][close] An audit's aim decides what it finds more than a repeat does: six
  S10 runs with three aims gave three nearly disjoint lists that agree to the digit
  where they meet, and the model — Fable 5.1 against Opus 5 — did not visibly
  matter. Run a session twice with two stated aims, not the same brief blind
  `[verified: DECISIONS.md D102]`.
- [close][infra] A paired run needs a reserved range of debt and decision numbers
  before it starts: every S10 branch opened #29 and D94 with different contents,
  and the integration had to map numbers before it could compare findings.

## From S12

- [infra] A label on a measurement is a claim the instrument makes about itself.
  "Whole model, cold" was the seventeenth run of its process for three sessions;
  when a number cannot be measured cold where it is printed, measure it in a
  subprocess or say what it is (rule B2) `[verified: DECISIONS.md D104]`.
- [field] Declare where a value is evaluated, not only what it is. "Midplane escape
  velocity" read the first cell centre for three sessions and moved with a grid
  knob nobody connected to it; a field that names a location should publish that
  location's value, computed there (debt #35).
- [infra] When a check can only be made stronger from outside the process — a
  reproducibility comparison, a cold timing — put the subprocess in the instrument
  the sessions read, not only in the suite: `python -m galaxy.specs` is the report
  a session actually looks at (debt #40).

## From S13

- [field] An input default is a constant and can be an unphysical one: Sagittarius'
  gas share delivered more gas than its progenitor weighed for ten sessions, and
  fixing the mechanism that hid it (the step infall) was what made the default's
  error visible — do the mechanism and the default together (D106).
- [field] Probe before you predict. The bulge was about to be written into row 3's
  miss as the fix, in three places; a fifty-line probe showed it lowers the row by
  5–8 km/s, because a disc rotates faster than a sphere of the same mass (D110).
- [field] When a units error in a mechanism is fixed, refit the constant that was
  fitted against it and record old → new in its about line (rule B10): WIND_SPEED
  1010 → 987 once the concentration was converted (D107).
- [field] A row that misses after a fix can miss the *other way*; rewrite the miss,
  its debt and its prediction rather than keeping the old explanation with a new
  number — row 3's old cause now has the wrong sign (D107).
- [infra] Normalise a discrete kernel on the grid it runs on, not in the continuum:
  a left-rectangle rule over-accreted by dt/2τ and put the baryon budget 0.08% over
  a test that closes it to 1e-4 (D111).
- [infra] A tolerance on a seeded sample is a binomial width, not a round number: 5%
  on 200 giants was inside the 7% noise by luck and broke the moment the physics
  moved (D111).
- [close] Re-pin a measurement to the new number with the old one beside it, never
  to the target (rule B5); a suite of pinned measurements is what tells a physics
  change from a regression, and it costs a pass of re-pinning every time (D111).

## From S14

- [field] A recalled magnitude is not a measurement. "Several km/s" for the halo's
  contraction sat in the register for a session as row 3's lever and was an order of
  magnitude short; the mechanism belongs in a register, the number belongs in a
  probe, and the probe costs fifty lines (D113).
- [field][infra] Probe a third ruleset before trusting two. The default and a probed
  (A, w) reading the same number to the digit was the only sign that A had cancelled
  out of the solver; the Blumenthal number was right throughout and would never have
  shown it (D113).
- [field] Decide the ruleset before reading the row and write the decision into the
  constant's about line first (rule B5). When the row then misses by eight
  half-widths, the record shows the number did not choose the physics (D113).
- [advanced][close] A mechanism that deepens the potential moves the wind's
  calibration: `WIND_SPEED` has now been refitted three times, once per mechanism
  upstream of v_esc, and its about line carries all three numbers (rule B10, D113).
- [field] A component's premise is itself a prediction. "Gas the threshold protects"
  was inferred from one exponential swept wider (debt #45) and fails for a second one
  on the disc's timescale — row 2 rises with row 20. Probe the premise before the
  mechanism, and probe with the repo unchanged: one substituted function per half (D114).
- [close][infra] A shell chain that pipes the suite into `tail` tests `tail`'s exit
  status, not the suite's: S14's close merged and pushed main with RESUMING.md three
  lines over its cap and the docs test red. Capture the suite's status before the pipe
  and gate the merge on it; the cost of not doing so is a second merge on the record (D115).

## From S15

- [field] A mechanism added upstream re-opens every *validation* an input's default
  rests on, not only the fitted constants rule B10 names. The epoch's 2.5 was justified
  by c₂₀₀ = 14.4 "inside the measured 10–18"; the measurements are fits to the halo
  after it contracted, and once the model contracted its halo the same fit read 18.5.
  Publish the quantity the measurement measures and compare like with like (D117).
- [field] Probe the discriminant before trusting it. The local dark-matter density was
  expected to double under the contraction and to judge it independently of row 3; it
  rose 16% and reads inside the measured span at every epoch. Fifty lines, and the
  register would otherwise have carried a discriminant that discriminates nothing (D117).
- [field][infra] A recalled formula is a claim about a paper, and the paper can refuse it.
  The "mass- and epoch-dependent (A, w)" the register named as the next thing to try does
  not exist in Gnedin et al. 2011, which says the response cannot be reduced to a
  prescription. A read-only agent with the arXiv text costs two minutes; tag `[recall]`
  until it has run, and let it overturn the plan's wording when it does (D117).
- [field] A default derived from a population relation is not a sweep to the answer when
  the row still misses. B5 forbids choosing an input against a known answer; it does not
  forbid replacing an unmeasured midpoint with a measured median that leaves the row
  outside and names what closes it (D117).
- [close][infra] Decisions are numbered sequentially by a test, so a plan cannot reserve
  D-numbers for a future session while earlier sessions still append; reserve *counts* and
  fix the numbers when the session opens (GALAXY_PLAN.md §5d, amended at S15).
- [infra] A scratch script named like a standard-library module (`numbers.py`) shadows it
  and numpy fails to import with a circular-import error that names nothing useful. Name
  probes `s<NN>_<what>.py`.

## From S16

- [field] The register named a timescale; the physics was a radius. Three arrival laws
  for the extended component read identically on every row, because the inside-out law
  already accretes over 10–20 Gyr where the component lives; D114's form failed on row 2
  only because its inner part overlapped the disc's own gas. Before deriving a timescale,
  check whether the rows can see one (D119).
- [field] Derive the profile from the distribution that exists, not from the observable
  the row wants. The halo's angular-momentum distribution gives the extended gas a share
  and a radius with one cited constant; a component "sized to the observed HI disc"
  would pass row 20 by construction and is the wrong answer that passes (debt #47).
- [field][infra] A derived field that feeds a scalar must live on the stage's own mesh,
  not the grid: the tail computed on the grid moved v_halo(R₀) with N_R and the
  grid-independence test caught it in the first run. The mesh is what the halo owns (D119).
- [field] A stage object holds its own `compute`; patching the module's name does nothing.
  A probe that substitutes a stage's compute sets it on the Stage (`object.__setattr__`),
  and reads the substituted number back before trusting the row (the "late" rows of the
  first probe were the unsubstituted model, and only the mass budget said so).
- [field] Probe the constant the rows point at even when it is not the session's: the
  threshold closed row 20 and cost row 9, which put it in S18's judgement rather than in
  this session's build — the probe cost fifty lines and saved a mechanism built for the
  wrong session (D119).
- [close][infra] A full suite that takes longer than the tool's timeout is killed with a
  misleading exit status; run it in the background with the status appended to its log.

## From S17

- [field] A probe's number is only as good as the model it was run on. D110 measured the
  bulge at −5 to −8 km/s on the uncontracted S13 halo, drawing it from the stellar disc in
  proportion; four sessions later, derived and taken out of the accreting budget, it is
  worth −1.6. A probe result carries the halo it was read against, and BRIEF.md was right
  to say "re-probe first" — the re-probe is the session's first hour, not a formality (D121).
- [field] When one construction has two ends, build both from it rather than from two.
  S16's high-j tail and S17's spheroid are the same mapped distribution read outside and
  inside its two crossings; factoring the shared half out (`angular_momentum_excess`) was
  the difference between two components that must agree and two that happen to (rule A9).
- [field] Ask where a derived component's *mass* comes from before deciding where its code
  goes. The spheroid could not be a stage: row 3 is computed in `sfh`, the halo contracts
  around the total baryons, and the derivation needs the halo's own mesh. Three constraints
  that each look like a preference close on one answer, and the design trap BRIEF.md named
  was the whole of the difficulty (D121).
- [field][close] A recorded miss that starts passing must be removed, and the reason it
  passed is what matters. Row 2 landed because the spheroid took 13% of the budget out of
  the disc, not because debt #47's threshold was built — so the debt is unaltered and the
  row is no longer evidence for it. Write that where the next session will read it, in the
  debt and in the removed miss's place, or the register quietly gains a discharge it did
  not earn (D121).
- [field] Two rows that want the same fix in opposite directions are worth more than either
  alone. Row 12 wants 7 × 10⁹ more mass in the spheroid; row 14's dispersion is already
  0.16 km/s high and that mass would take it to 123. The session that builds bar buckling
  reads which, and neither row could have said so on its own (rule B4).
- [field] A number that is nearly right can be right for a reason that is not the model's.
  Row 14 reads 116 against 113 while row 12 is 45% low, because σ inside the half-mass
  radius is set by the whole enclosed mass and not by the spheroid: on self-gravity alone
  it would read 71. Check what a passing quantity is actually sensitive to before crediting
  it to the mechanism under test (rule B3's cousin).
- [close] A missing calibration is not a licence to invent one. Ruling 10 asked for the
  M_• residual's width to be interpolated towards the pseudobulge end; the sources decline
  to fit pseudobulges at all, so the width stays the classical one, the model is recorded
  as understating the spread, and it becomes a debt (#48) rather than a number (rule B9).
- [infra][close] A note that names a stage in a literal goes stale the session a stage
  moves. The profile's "billed to the first stage that draws (pattern)" was wrong the
  moment a seeded stage landed at checkpoint 1; it derives the name from the widest
  cold/warm ratio now (rule B13).

## From S18

- [field] Derive the mechanism the plan named, measure it, and let the number kill the
  prediction before deciding what to build next. The merger's radial kick is real physics
  with no new constant, and it is worth 0.3 kpc on a row that needs 0.8; the probe that
  showed that also showed where the row is decided (the first infall's arrival law), which
  the plan's mechanism would have hidden if it had been built and tuned (rules B1, B4; D124).
- [field] A kernel's boundary is a physics statement. A Gaussian in R reflected at R = 0
  piles mass into a central cusp (Σ at the first cell ×6 for a 0.5 kpc kernel), and the
  velocity solver then read a rise in v(R₀) that was the fit failing (residual 0.001 → 0.30),
  not the disc. Check the instrument's residual on the new profile before reading a row off
  it — the old profiles were smooth and the solver had never been asked a hard question.
- [field] A representation-based solver cannot be densified past its conditioning.
  Twelve exponentials fit the profile; sixteen return zero or thousands of km/s. When a fit
  is the instrument, the honest replacement is a method with no basis at all, validated on
  a case with an analytic answer that looks nothing like the basis (Kuzmin), and the
  correction it makes to every earlier reading measured and written down (−0.09 km/s here).
- [field] A pre-committed reading is worth more than a post-hoc one. Debt #47 wrote, a
  session early, "if row 9 cannot be restored with the threshold derived, the thick disc is
  what is wrong, not the threshold". That sentence is why the derived threshold went in
  with row 9 red, and why the row is a mechanism-shaped miss rather than a constant kept at
  the bottom of its range to hold a gate (rule B5).
- [field] A derived quantity can be right where it was calibrated and wrong where the
  calibration never reached. Kennicutt's threshold lands the gas at R₀ and diverges with κ
  at the centre, where the argument does not apply and the bar does the work; it put 1.1e9
  of hydrogen inside 4 kpc and row 20 at its target partly for that reason. Read a landed
  row's *distribution*, not its total, before crediting it (rule B3's cousin, D124).
- [field] When a regulator takes over, a calibration stops mattering and the record must say
  so in both directions. With the threshold derived the disc is threshold-regulated and
  `KS_NORM` no longer reaches row 2 at all (1.764 / 1.755 / 1.755 across ±1σ, from 1.97 /
  1.82 / 1.73); debt #44's claim flipped from "the row cannot see past the constant" to "the
  row cannot see the constant", and both are findings about what a green row 2 is worth.
- [field] Two rows one constant lands together is a probe, not a decision, when the plan
  gives that constant to another session. `MERGER_HEATING` = 60 reads row 7 at 751 and the
  advanced row 6 at 346, both inside, for the first time; it is written into #42 and BRIEF
  for S20, which owns both heating constants, and left where it is (rule B10 cuts both ways).
- [close] A miss that lands by less than the instrument's correction is a pass to record
  with its decomposition. Row 3 read 250.96, inside by 0.04: the solver −0.09, the kick −0.2,
  the threshold 0.00; none of them is the bar its entry predicted. The entry went (debt #29)
  and its replacement says which mechanism paid, so the bar's prediction stays testable.
- [infra] A stage that reads a field from an earlier checkpoint can change the execution
  order without changing the graph. Assembly now reads the disc's curve; Kahn's tie-break
  put the disc first and a test that pinned the order caught it, which is what the pin is
  for — re-pin with the reason, do not loosen it.

## From S19

- [catalogue][field] A kernel normalised over its destination is not a distribution over its
  source. `transport` sums to one along each *row*, so reading a column as "where did the
  stars here come from" is wrong by the mass each ring had to send: the backward weight is
  `born[i] · K[i, j]`, which both chemistries already computed and the catalogue had to be
  told. The symmetric reading is not a small error — it places stars where nothing was born,
  and reads an abundance off gas that made no stars (D126).
- [catalogue][field] When a quantity is transported, so is every marginal of it. The
  catalogue drew a star's abundance at the ring it sits in and its birth time from the birth
  rate *there* — the answer for a disc whose stars never moved. Fixing the radius alone
  moved the spread the wrong way (0.284 → 0.273 against a target of 0.360); fixing the time
  with it landed the gate. Ask which of a rule's marginals the mechanism touches before
  deciding you have implemented half of it and got half the effect.
- [field][catalogue] A criterion two stages apply is a field one stage publishes. `systems`
  rebuilt the thin/thick mask from the same ingredients `vertical` used, and in the advanced
  model the two disagreed — the stage's α-criterion selects nothing without a valley, the
  catalogue's fallback was the merger time. It never showed because the surface density it
  was drawn against was zero: **a duplicate can be wrong for sessions while a zero masks
  it** (rule A9, D126).
- [catalogue][infra] Arithmetic that depends on what was asked for cannot coexist with
  per-region determinism. Narrowing a matrix product to the rings a region touches changed
  the last bit of a star's age, because BLAS sums a one-column product in a different order
  than a thirty-two-column one. Make the work query-independent and make it cheap instead —
  here by reading the kernel column-wise rather than building it square (D126).
- [catalogue] A per-star cost hides inside a per-cell design until the profile is read. The
  first draw gave every star its own 400-cell cumulative sum; the catalogue still passed
  every correctness test and its cost structure had quietly inverted. The kernel is a
  bin-level object, so the draw is too — and the accuracy cost was nil (rule B6, D24).
- [all] State a numerical claim at the precision you checked it at. "The same numbers" became
  "the same to 6 × 10⁻¹³ relative, and here is why" once the bound was measured — a running
  total over 2n − 1 terms against a pairwise sum over n. The weaker claim is the one that
  says the two must not be mixed inside one answer, which is the part that matters.
- [field] A dispersion is a poor discriminator between hypotheses that shift a mixture's
  components. Debt #32 spent three sessions on whether migration widens the local [Fe/H]
  spread; the answer was "barely, and lately it narrows it" — while migration was moving the
  mean age at R₀ by 1.4 Gyr and bringing 84% of the Sun's neighbours from inside it. Pick
  the moment the mechanism moves, not the one the source sentence happened to name (D126).


## From S20

- [field] Decompose the distribution before choosing the lever. The valley's absence had been
  argued for four sessions in terms of infall timescales; one instrument — the [α/Fe] mass at R₀
  by birth epoch, radius and time — showed the early population is a *plain*, not a mode, because
  dN/dx = Ψ/|dx/dt| and the rate was already falling while x fell. Every timescale probe then
  read the same for a reason that was visible in the first table (D128).
- [field] Check what a detector's "yes" is made of before crediting it. Every `bimodal_wide` the
  model has ever reported was a spike of the stars formed before the first type Ia — +0.45
  exactly, five percent of the mass — with the split above the α-rich sequence itself. A verdict
  is a summary; read the histogram it summarises (rule B3's cousin; debt #27).
- [field] A mechanism that opens the row at the cost of the budget is a measurement, not a
  candidate. The mass-loaded wind and the bar-driven drain both open a valley and both gut rows 2,
  3 and 10; the number that matters is the one that says the retained budget would have to be an
  output. Write it into the debt it belongs to and stop (rule A1, A4; #26, #21).
- [field] Derive a calibration's arithmetic, not just its value. `MERGER_HEATING` was "scaled so
  the merger leaves the disc at 30 km/s" and the thick disc read 40, because the stage composes
  the kick with 27 km/s the model already gives those stars. Net of that the cited 35 gives 88.8,
  row 7 lands, and the constant now has a citation instead of a sentence (rule B10; #42).
- [field] A row landed on a constant leaves when the constant is derived. Row 3 was inside by 0.04
  on the kick at S18; the kick re-derived is worth +0.07 and the row is out by 0.03. Neither
  reading is a defect — the record says which mechanism paid each time, so the bar's prediction
  is still the one that is testable (rule B5; #11).
- [field][infra] Factor the substitution point when a probe is worth repeating. `sfh.first_infall`
  is one function so that a test can monkeypatch the law and re-run S20's three probes; the
  session's findings are pins rather than prose, which is what S21's aim (a) needs.
- [close] A pre-committed reading is the ruling when the prediction fails. Debt #49 wrote "if rows 5
  and 11 still trade, the star formation law at high redshift is what is wrong" before the probe
  ran; the probe ran, they traded, and that sentence is the decision — nothing was re-argued.
