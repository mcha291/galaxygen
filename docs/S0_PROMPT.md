Session 0 of an eleven-session build: a procedural galaxy generator, Python core
plus a web viewer, physically-grounded, defaulting to the Milky Way.

**Repo:** https://github.com/mcha291/galaxygen.git — currently empty. You are
initialising it.

**Attached:** `RULES.md`, `GALAXY_PLAN.md`, `GALAXY_INPUTS.md`.

Read `RULES.md` and `GALAXY_PLAN.md` in full before writing anything. From
`GALAXY_INPUTS.md` read only §7 (the 24 acceptance quantities) and §11 (the
input table and the debt register) — the rest is reasoning you can consult later
if something surprises you, not startup reading. Commit all three unchanged as
the first commit.

**Tag every factual claim** as `[verified]`, `[recall]` or `[inferred]`.
`[verified]` requires a citation in the same message, to something in the repo or
a cited external source — a bare `[verified]` is a false label. Never state or
imply you have read a document, run a search or checked a source unless the
corresponding tool call appears in that turn. This is rule B14 and it applies to
your messages, not just the docs.

---

## Deliverable

Infrastructure only. **No physics in this session** — not a single stage
implementation beyond what the stub model needs to exist.

- `core/` — model registry, field declaration (`fielddoc`), seeds, grids, units
- `model/` — `graph.py`, `preflight.py`, `determinism.py`, `spec.py`
- `spec.py` holds the 24 acceptance quantities **as data**, with a runner that
  reports each as pass / fail / not-yet-computable. Everything reports
  not-yet-computable this session. This is the point: build the instrument before
  the thing it certifies (rule B1).
- **A stub second model** that differs from the first by one constant. This is
  the most important deliverable in the session. It exists so the registry, the
  model switch and cross-model field reconciliation are exercised from now on
  rather than discovered broken at S9.
- `.gitignore`, and a pre-commit hook refusing staged content matching `ghp_` or
  `github_pat_` (rule C2c)
- `tools/progress.py` — regenerates the progress bar in `GALAXY_PLAN.md`'s status
  board from its checkboxes, plus a test asserting the two agree. Small, but it
  is the thing that stops the board from quietly lying about where the build is

Deferred to S10, deliberately: `convergence.py`, `performance.py`. They need
something to measure.

## Gate

1. `graph` is acyclic **per model**
2. Both models pass `preflight` — no undeclared field, no orphaned declaration,
   optional fields have handled absence
3. `determinism` holds, including per-region: `hash(seed, object_id)` is
   order-independent
4. `spec` runs and lists 24 quantities
5. `tools/progress.py` regenerates the bar and its test passes
6. A test asserts `RESUMING.md` is ≤ 120 lines

## Three gaps no document settles — decide them and record why

1. **The closed unit vocabulary** for field declarations. Closed means a field
   cannot invent one.
2. **The `kind` vocabulary** — continuous scalar field, category, per-object
   scalar, catalogue column, or whatever set you can justify.
3. **Grid defaults.** `GALAXY_PLAN.md` §5a proposes N_R = 400, N_t = 2000,
   N_z ≈ 60, and gives the measured reason N_R and N_t must stay separate quality
   knobs. Take them or argue.

If anything else in the plan is wrong, say so rather than building it. The design
documents have been through several audit passes but S0 is the first time
anything gets implemented, and the implementation is entitled to push back.

## Close, in this order

0. Tick S0's box in `GALAXY_PLAN.md`'s status board, fill in the tag and date,
   update the debt counts, run `tools/progress.py`
1. Full suite once, quiet mode
2. `DECISIONS.md` — every non-obvious decision, with what settled it. New rules
   into `LESSONS.md`, **tagged by stage type**
3. `RESUMING.md` — ≤ 120 lines, and it never grows past that
4. `BRIEF.md` for S1 — about 40 lines: what to build, which files to touch, the
   gate, known traps. This replaces reading `GALAXY_PLAN.md` from now on, so it
   has to stand alone
5. Commit, `--no-ff` merge to `main`, tag `s00`, push branch, main and tags.
   **Never force-push** — sessions are sequential, so a rejected non-fast-forward
   push is a signal to stop, not an obstacle
6. **Verify by cloning the remote into a clean directory and running the suite
   there** — not by re-running in your working copy, which cannot detect a file
   you wrote but never `git add`ed. Also assert `git status --porcelain` and
   `git ls-files --others --exclude-standard` are both empty

Work on branch `session-00` and push it at least once mid-session, so a session
that runs out of time doesn't lose its work.
