# Rules

The rules this project is held to. Stated here so that no document has to reach
outside the project to justify itself.

**Provenance.** Several of these were derived from recorded measurements in an
earlier, separate project. Where a rule's justification stands on its own — a
fact about git, an arithmetic argument, a measurement in this repo — it is tagged
accordingly. Where the rule rests on empirical evidence gathered elsewhere and
not reproducible here, it is tagged `[recall]` and says so. **No rule is tagged
`[verified]` on the strength of a document outside this repo.**

---

## A. Model rules

**A1. No fixed-point solvers on the grid.** Every field is computable in one
pass, in a fixed order. Iteration only where bounded and cheap. *Justification:
measured — the coupled fixed point is an 8× multiplier and it is the one
advanced-model cost that no implementation recovers* `[verified: bench2.py §4]`.

**A2. Controls are global scalars only.** Nothing per-cell, per-annulus or
per-system is ever an input. Regional metallicity, disc structure and system
architecture are *results*. *Justification: per-object inputs make the input
count unbounded and the model unauditable* `[inferred]`.

**A3. If it can be derived, derive it — and "derived" means determined, not
correlated.** A relation with real galaxy-to-galaxy scatter, shipped as if exact,
claims a precision the model does not have. See `GALAXY_INPUTS.md` §4b for the
three verdicts and the two remedies.

**A4. Never invent a variable to justify a stage.** Judged individually: would
this input exist if no stage needed filling?

**A5. Defaults are real measured values**, so launching with nothing touched
generates the Milky Way.

**A6. Dependent stages come after their dependencies**, and the graph is
machine-checked acyclic in CI — **per model**.

**A7. Advanced-model findings are stored separately** from the simple first pass.

**A8. A field is described where it is computed**, with a label, a unit from a
closed vocabulary, a kind, its ramp, whether it has a meaningful zero, and an
`about` line recording its surprise. *Justification: two models publish different
field sets; without a declared contract a stage will read a field that exists in
one model and not the other, silently* `[inferred]`.

**A10. Every quantity is exactly one of three kinds, and the model says which.**

| | Definition | Counts against the ceiling? | Reproducible? |
|---|---|---|---|
| **Input** | A free control someone sets | **Yes** | Yes |
| **Derived** | Pure function of inputs. Same inputs → same output | No | Yes |
| **Seeded** | Function of inputs **and a seed** | No | **Yes** |

**"Deterministic" is ambiguous and is never used unqualified in this project.**
Two distinct properties claim the word: *reproducible given all arguments*, which
seeded quantities have because the seed is an argument, and *determined by the
physical inputs alone*, which only derived quantities have. A seeded quantity is
fully reproducible and not at all determined. Say which is meant, every time.

**A9. One opinion about how a field is rendered, held by the code that computes
it.** Ramps come from the field declaration and from nowhere else — not a client
table, not a scale list, not a workflow step. *Justification: a duplicate that
loses is dead code; a duplicate that wins is a bug wearing the right name*
`[recall]`.

---

## B. Working method

**B1. Build the instrument before the thing it certifies.** *Evidence is
empirical and from outside this repo* `[recall]` — but it has already held once
here: the DTD benchmark found a defect in a proposal made one turn earlier
`[verified: bench2.py §1]`.

**B2. Measure cold.** A cache turns a measurement into a reading of the cache.
*Justification: intrinsic* `[inferred]`.

**B3. A check that takes your own path is a check on you.** Verification that
uses the one access path immune to the defect will pass every time.

**B4. State the hypothesis as a prediction that could fail**, and let a symptom
that misses by one kill it.

**B5. Record failed acceptance checks rather than relaxing them**, along with the
explanations tested and found wrong.

**B6. Profile before optimising and publish the profile.** Publish the number,
not the verdict — the planets benchmark's occurrence rate is 30× low and says so
`[verified: bench_planets.py]`.

**B7. A scaling exponent finds what a stopwatch cannot.** *Justification:
measured — the naive DTD is fast enough at low time resolution and quadratic
above it* `[verified: bench2.py §1]`.

**B8. Do not sample what you can count.**

**B9. A missing number must not be shown as a measured one.** `None` and zero are
different answers.

**B10. A constant fitted against a broken mechanism has no claim on its value.**
When a bug is fixed, re-examine every constant calibrated while it was live.

**B11. A relation that fits the validation table can still be the wrong
relation.** *Instance in this project: the pitch–shear correlation* (`GALAXY_
INPUTS.md` §5).

**B12. Conflicts are preserved as named rulesets, never averaged.**

**B13. When correctness depends on remembering, move it where it cannot be
forgotten.** The point is not that the current state is more correct, but that a
class of future states becomes unreachable.

**B14. Every factual claim is tagged** `[verified]`, `[recall]` or `[inferred]`.
`[verified]` requires a citation in the same document, to something inside this
repo or to a cited external source.

---

## C. Repository and session

**C1. Resume by cloning the remote into a fresh directory.** Never update an old
checkout, never reuse a container's leftover working tree. *Justification: a
stale checkout that silently fails to update looks identical to one that
succeeded* `[recall]`.

**C2. Verify a session's work by cloning the remote into a clean directory and
running the suite there — never by testing the working copy you pushed from.**
*Justification: this is B3 applied to the specific defect that a remote
introduces. A file that was written but never `git add`ed passes every test in
the working copy, because the file is on disk; it is absent for the next session.
The working copy is exactly the path immune to the defect.* `[inferred]`

At close, additionally assert both are empty:

    git status --porcelain
    git ls-files --others --exclude-standard

**C2a. Never force-push. Ever.** Sessions are sequential and nobody else commits,
so a push to `main` should always fast-forward. **A rejected non-fast-forward
push is a signal that something is wrong — stop and investigate, do not force.**
`[inferred]`

**C2b. Commit and push at every completed sub-deliverable**, on the session
branch — not once at close. *Justification: the binding constraint on a session
is usage quota, which stops it mid-work without warning and without regard to how
much was accomplished. Everything after the last push is lost. Wall-clock length
is not the risk; iteration depth is.* `[inferred]`

**C2d. A session that stops early closes partially.** Commit, push, write what
remains into `BRIEF.md`, mark the board row ◐. **Do not merge to `main` and do
not tag** — the branch stays open and the next session continues on it. Never
start new work in the hope of finishing before the limit. *Justification: leaving
the next session to reconstruct where the last one got to is the single most
expensive failure this protocol exists to prevent.* `[inferred]`

**C2e. Sessions do not tag; they queue the command.** A session's close appends
its `git tag -a s<NN> <merge sha> -m …` line to `MANUAL_TODO.md` and fills in the
*previous* session's merge SHA, which was unknowable while that merge was being
written. The tags are applied in one batch, by hand, at the end of the build.
*Justification: the environment the web sessions run in refuses tag refs — a tag
push returns HTTP 403 where a branch push to `main` succeeds, so a close ritual
that ends in a tag ends in a failure every time* `[verified: DECISIONS.md D40]`.
*A step that cannot succeed is not a step; queueing it keeps the record honest and
the ritual completable.* `[inferred]`

**C2c. Credentials never enter the repository.** The token lives in the container
environment or a credential file outside the working tree, never in a tracked
file, never in `.git/config` that gets committed. A pre-commit hook greps staged
content for `ghp_` and `github_pat_` and refuses. *Justification: the one
irreversible mistake available in this workflow* `[inferred]`.

**C3. `RESUMING.md` has a hard cap of 120 lines, enforced by a test.**
*Justification: session-open cost is paid once per session and grows
monotonically otherwise* `[inferred]`.

**C4. `BRIEF.md` is written by the previous session and replaces reading the
plan.** ~40 lines: what to build, which files, the gate, known traps.

**C5. Lessons are tagged by stage type.** A session reads only its tags.

**C6. The acceptance table lives in `spec.py`, never in prose read at runtime.**
A session runs it and reads pass/fail.

**C7. Tests run quiet.** Affected subset mid-session, full suite once at close.

**C8. Never read a file you are about to overwrite.**

---

## D. Viewer

**D1. A lock means "do not re-roll this."** It can never mean "freeze this
against upstream changes." Confirmed controls are **disabled rather than
hidden**; reopening a stage discards every later one; a page load lands on stage
one.

**D2. Exactly one `fetch` in the client transport, asserted in CI.**
*Justification: instrumentation that must be remembered in N places will be
forgotten in one of them* (see B13) `[inferred]`.

**D3. The API publishes a content hash of the viewer's own bytes**, so "am I
running the new code" is a glance rather than an investigation.

**D4. No endpoint runs more of the pipeline than its answer requires.** Metadata
endpoints must not touch stages. *Justification: this class of defect is
invisible to any check run against a warm cache* (see B2) `[recall]`.

**D5. The viewer computes no physics and persists no generated object.**
Replacing the viewer means reimplementing against the same endpoints.
