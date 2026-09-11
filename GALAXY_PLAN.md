# Galaxy generator — implementation plan

## Status

`███████████████████████████████████████████░░░` **21 / 23 sessions** · repo initialised: yes

| | S | Session | Surface | Model planned | Model used | Tag | Closed |
|---|---|---|---|---|---|---|---|
| ☑ | 0 | Instruments, registry, stub second model | desktop | **Fable** | **Fable** | s00 | 2026-09-03 |
| ☑ | 1 | Halo & disc | web | Opus | **Opus 5** | s01 | 2026-09-02 |
| ☑ | 2 | SFH & chemistry (simple) | web | Opus | **Opus 5** | s02 | 2026-09-03 |
| ☑ | 3 | Assembly & mergers | web | Opus | **Opus 5** | s03 | 2026-09-03 |
| ☑ | 4 | Pattern: bar, arms | web | Opus | **Opus 5** | s04 | 2026-09-03 |
| ☑ | 5 | Systems: catalogue | web | Opus | **Opus 5** | s05 | 2026-09-03 |
| ☑ | 6 | API | web | Opus | **Opus 5** | s06 | 2026-09-03 |
| ☑ | 7 | Viewer, galaxy view, stage previews | web | Opus | **Opus 5** | s07 | 2026-09-04 |
| ☑ | 8 | Planets & system view | web | Opus | **Opus 5** | s08 | 2026-09-04 |
| ☑ | 9 | Advanced model | desktop | **Fable** | **Fable 5.1** | s09 | 2026-09-04 |
| ☑ | 10 | Audit | desktop | **Fable** ×2 | **Fable 5.1** (runs 1, 2) | s10 | 2026-09-05 |
| ☑ | 11 | Integrate the S10 audits (beta, the gamma pair) | desktop | — | **Fable 5.1** | s11 | 2026-09-07 |
| ☑ | 12 | The maintainer's one-line fixes (D-9, D-13, #33, #35, #37, #40) | desktop | — | **Fable 5.1** | s12 | 2026-09-07 |
| ☑ | 13 | The physics decisions: step infall, Sagittarius, c_vir → c₂₀₀, hydrogen, the median criterion; bulge and catalogue probed | desktop | — | **Fable 5.1** | s13 | 2026-09-07 |
| ☑ | 14 | The halo contracts around the disc (#6; row 3 turns round, wants z_f 0.7–1.0); the extended component probed (#18) | desktop | — | **Fable 5.1** | s14 | 2026-09-07 |
| ☑ | 15 | Row 3's cause, derived: the epoch's default from the ΛCDM median (2.5 → 1.66, #12 discharged); the calibration ruled out as the lever (#46); row 3 at 260.1 under #11 with the bulge and the component its prediction | desktop | **Fable** | **Fable 5.1** | s15 | 2026-09-09 |
| ☑ | 16 | The extended component, derived as the high-j tail of the halo's angular momentum (#18 discharged, #47 opened); the timescale was not the decision; the derived threshold probed for S18 | desktop | **Fable** | **Fable 5.1** | s16 | 2026-09-09 |
| ☑ | 17 | The spheroid derived as the low-j end of the halo's angular momentum, and M_• (rows 10–14, 18; #17 discharged for row 14, #48 opened); the bulge is worth 1.6 km/s and not D110's 5–8, so row 3 misses by 0.3 and rows 3 and 12 have one cause | desktop | Opus | **Opus 5** | s17 | 2026-09-09 |
| ☑ | 18 | The thick disc: the merger's radial kick derived and built (worth 0.3 kpc on row 5; its prediction dead, #19), Kennicutt's threshold derived (#47: the gas rows land, row 9 leaves), the basis-free disc solver; row 3 landed on the kick; the shape is the first infall's (#49 opened) | desktop | **Fable** | **Fable 5.1** | s18 | 2026-09-10 |
| ☑ | 19 | The catalogue migrates: birth radius **and birth time** drawn together from the chemistry's backward weights (#31 discharged, #32 re-ruled, #50 opened); the thin/thick criterion published; every published field previewed, in both models | web | Opus | **Opus 5** | s19 | 2026-09-10 |
| ☑ | 20 | The valley probed six ways, the repo unchanged, and not opened: every valley the detector finds is the plateau spike, the early population a plain (#27's prediction replaced; #49's killed, #26 and the drain ruled for S22); `MERGER_HEATING` derived from the thick disc's dispersion net of the secular heating (120 → 88.8, #42: row 7 lands, row 3 leaves by 0.03) | desktop | **Fable** | **Fable 5.1** | s20 | 2026-09-11 |
| ◐ | 21 | Audit II, twice with two stated aims and reserved numbers (§5d). **Run (b) closed** on branch `claude/keen-lamport-lldlvp`, which *is* `session-21-b` (the container names the branch): the instruments and the viewer — rule D4 counted at the stages and found honest, the catalogue priced per **cell** and not per star so D115's flake is the misfit (#67, #68), the detector's blind spot in closed form (#70), four published fields the viewer cannot show (#69); debts #65–#73, decisions D144–D150, `AUDIT_S21B.md`. **Run (a) — every prediction since S13 — still open.** | desktop + web | **Fable** ×1, Opus ×1 | (b) — see MANUAL_TODO §2 | s21 | — |
| ☐ | 22 | Close-out: audit lists ported, every debt ruled, the tag batch applied (§5d) | web | Opus | — | s22 | — |

**Surface** is where the session ran — desktop, web, terminal. **Model** is which
model ran it. They are different things and neither substitutes for the other.
*Model used* is filled at close from what actually ran, which may differ from
what was planned; the S10 comparison (below) is worthless if this is recorded
from intention rather than fact.

☐ not started · ◐ in progress or split · ☑ closed and verified

**Tags are deferred to one batch at the end of the build** (rule C2e). The web
sessions run behind an egress proxy that refuses tag refs — `git push origin s01`
returns HTTP 403 while branch and `main` pushes succeed `[verified: DECISIONS.md
D40]`. Rather than have every session fight it, no session tags: each appends its
`git tag` command to `MANUAL_TODO.md`, and they are all applied in one go from the
desktop. **The Tag column therefore names the tag a session has *earned*, not one
that exists on the remote yet.** `MANUAL_TODO.md` is where the truth about which
tags exist lives, and a test asserts it carries a row for every ☑ session.

**Next:** S21. Read `BRIEF.md`, written by the session before it; `S0_PROMPT.md`
is the record of S0's own brief.

**Open debts:** 41 (`GALAXY_INPUTS.md` §11). **Discharged:** 18.

> This board is the single source of truth for what is done. `RESUMING.md` does
> not repeat it (rule A9 — one opinion, in one place). The progress bar is
> **generated** from the checkboxes by `tools/progress.py`, and a test asserts
> they agree, because a hand-maintained bar drifts from the thing it summarises.

---

Companion to `GALAXY_INPUTS.md`, which holds the model. This holds the build.

Everything here is `[inferred]` design unless tagged otherwise. The working rules
this plan invokes are stated in `RULES.md`, inside this project — nothing here
reaches outside it for justification.

---

## 1. Three architectural commitments, made before any physics

Three things that a project with one model can discover late, and this project
cannot, because two models make each of them load-bearing rather than convenient.

**Field declaration at S0** (rule A8). Every published field carries a label,
unit, kind, ramp, meaningful-zero flag and an `about` line, declared in the stage
that computes it, with `preflight` asserting nothing is undeclared and no
declaration orphaned. **Two models publish different field sets** — advanced
chemistry publishes per-element abundances the simple model does not. Without a
declared contract, a downstream stage will read a field that exists in one model
and not the other, and the failure is silent rather than loud.

**The graph audit at S0.** `graph.py` computes the earliest field each input can
affect; that is what decides which checkpoint each control belongs to. Staged
previews with per-stage rerolls are a **requirement** here, not something
discovered midway, so the audit that grounds them is a prerequisite rather than a
by-product. The stage grouping in §3 is a **hypothesis to be checked against the
audit**, not a decree.

**A stub second model at S0.** The single largest risk in this build is that
eight sessions of simple-model work rot the two-model boundary, and the advanced
model turns out not to fit. Mitigation: S0 ships a second registered model that
differs *trivially* — one constant — purely so the registry, the field
reconciliation and the model switch are exercised from the first session onward.
Build the instrument before the thing it certifies (rule B1).

---

## 2. Layering

```
galaxy/
  core/          fielddoc, registry, seeds, grids, units
  models/        model declarations: which stage impl, which constants
  stages/        stage implementations (shared where identical)
  model/         executable specs: graph, determinism, convergence,
                 performance, preflight, spec
  api/           HTTP layer. JSON metadata + binary arrays. No rendering.
viewer/          static HTML/JS. Talks only to api/. Replaceable.
```

### The model boundary

A **model** is not a pipeline. It is a declaration:

```
Model = {
  name, inputs[], constants{},
  stages: {stage_name -> implementation_id},
  publishes: derived from the chosen implementations
}
```

Stages are shared wherever the implementation is identical — `halo`, `potential`
and `disc` are the same code in both models. Only where an advanced
implementation exists does the model choose. **A third model slots in by
declaring a stage map**, not by forking a pipeline.

The contract between stages is the **field set**, never the implementation.
Downstream code that wants `[Fe/H](R,t)` gets it identically whether the simple
or the multi-element chemistry produced it. Fields present in only one model are
declared optional and any reader must handle absence — `preflight` asserts this
per model, so a stage cannot quietly assume the richer model.

### The UI boundary

The viewer receives only: stage metadata, field metadata, and arrays. It never
receives model internals and it never computes physics. Replacing it means
reimplementing against the same endpoints.

**One fetch, asserted** (rules D2, D3, D4). Exactly one `fetch` in the client
transport with CI asserting the count; a `/api/version` content hash; and no
endpoint running more of the pipeline than its answer requires.

The failure this prevents is a metadata endpoint that quietly calls into the
pipeline — cheap warm, ruinous cold, and **invisible to every check ever run
against a warm cache** `[recall]`. So: **cold timings from the first API commit,
published every session** (rule B2).

---

## 3. Stages and previews

Six stages. The grouping is a hypothesis; `model_graph.py` rules.

| # | Stage | Inputs / seeds it owns | Preview |
|---|---|---|---|
| 1 | **Halo & disc** | `halo_mass`, `spin`, `halo_assembly_z`, `baryon_retention` | Rotation curve; face-on surface density (smooth, axisymmetric) |
| 2 | **Assembly** | `mergers[]` | Accretion history; edge-on view showing the thick disc appear |
| 3 | **Star formation & chemistry** | `infall_timescale`, `inside_out_index`, `migration_efficiency` | Age–metallicity relation, radial gradient, SFH; face-on coloured by [Fe/H] |
| 4 | **Pattern** | `pattern_seed` | Bar and arms. **First recognisable galaxy** |
| 5 | **Systems** | `systems_seed` | Galaxy view — the star catalogue |
| 6 | **Planets** | `planets_seed` | System view |

Every stage renders the **same two views** — face-on and edge-on — plus a
stage-specific plot. Each preview shows only the fields that exist at that point,
so the galaxy visibly assembles: smooth disc, then thickened, then chemically
structured, then armed, then resolved into stars. That progression is honest
rather than decorative; it is what the model actually knows at each step.

### Locking

Confirming a stage locks its prefix, under rule D1: a lock means *do not re-roll
this* and never *freeze this against upstream changes*. Confirmed controls are
disabled rather than hidden, reopening a stage discards every later one, and a
page load lands on stage one.

**Reroll is a distinct action from edit.** Rerolling stage 4's `pattern_seed`
invalidates 5 and 6 but not 1–3. This is the whole point of per-stage seeds and
it falls out of the graph audit rather than being hand-wired.

---

## 4. The two views

### Galaxy view

10⁶ stars will not render as 10⁶ DOM nodes or draw calls. The rendering strategy
**mirrors the model's own field/object split**:

- **The field renders as an image.** Stellar density, integrated and coloured by
  the populations stage, drawn as a texture. This is what you see at galaxy zoom.
- **A materialised sample renders as points.** A seeded subset — order 10⁴–10⁵ —
  drawn as clickable objects, stable across sessions because it comes from
  `hash(systems_seed, star_id)`.
- **Zooming materialises more.** Below some angular scale the field is replaced
  by actual stars within the view volume, generated on demand and never stored.

The consequence to state plainly: **at full galaxy zoom you are looking at a
field, not at stars.** Clicking requires the materialised sample. Building the
sample first and the LOD ladder later is the right order.

### System view

Star, planets, belts, moons. Small N, trivial to render. Selecting a star in
galaxy view transitions here; the system is generated from
`hash(planets_seed, star_id)` at that moment and discarded on exit.

### What the viewer must not do

No physics, no persistence of generated objects, no second opinion about how a
field is rendered (rules D5, A9). **Ramps come from the field declaration, in the
stage that computes the field, and from nowhere else.** The failure mode is a
client-side colour table that silently wins over the authoritative one and
renders a field as something it is not `[recall]`.

---

## 5. Session protocol

Every session is a fresh context. The repo lives at
`https://github.com/mcha291/galaxygen.git` and every session clones it fresh
(rule C1). **Verified reachable from the sandbox** `[verified: clone succeeded,
this session]`; **push requires a token** `[verified: unauthenticated push
rejected, this session]`.

This replaces file-passing entirely, which matters most for the cross-account
Fable sessions — they clone the same URL and nothing has to be carried.

### Fixed opening and closing

**Open:** clone the remote into a fresh directory → read `RESUMING.md` (capped,
see below) → read `BRIEF.md` → start on branch `session-NN`. Nothing else is read
by default.

**Mid-session:** commit and push at every completed sub-deliverable (rule C2b).
The binding constraint is usage quota, and a session halted by it loses
everything after its last push. See **Partial close** below.

**Close, in order:**
0. **Tick this session's box in the status board** at the top of
   `GALAXY_PLAN.md`. Fill in **surface, model actually used**, tag and close
   date; set the next session's row to ◐ if it has already begun. Record the
   model from what ran, not from what the plan said. Then run
   `python tools/progress.py`, which regenerates every derived number. A session that closes
   without doing this leaves the board lying, and the board is what you look at
   to know where the build is.
1. Full suite once, quiet mode.
2. Append to `DECISIONS.md` and any new rule to `LESSONS.md`, **tagged** by stage
   type so future sessions read only what applies to them.
3. Rewrite `RESUMING.md` in place — it does not grow.
4. Write `BRIEF.md` for the next session: what to build, which files to touch,
   the gate, and known traps. This is the single highest-leverage artefact in the
   whole protocol; it is what lets the next session skip reading the plan.
5. Commit, `--no-ff` merge to `main` with the subject `Merge S<N> into main: …`,
   push branch and main. **Do not tag** (rule C2e): append this session's tag
   command to `MANUAL_TODO.md`, and fill in the *previous* session's merge SHA
   while you are there — it was unknowable until its merge existed.
   **Never force-push** (rule C2a).
6. **Verify by cloning the remote into a clean directory and running the suite
   there** (rule C2) — not by re-running in the working copy, which cannot detect
   a file that was never `git add`ed.

### Token discipline — the rules that actually move the number

The dominant recurring cost in a multi-session build is **re-reading state at
session start**, and it grows with the project unless capped. An uncapped
resuming document reaches a few hundred lines by the end of a build of this size,
and every session pays it — eleven times over. `[inferred]`

| Rule | Why |
|---|---|
| **`RESUMING.md` hard cap: 120 lines.** Enforced by a test | Otherwise it grows monotonically and every session pays |
| **`BRIEF.md` replaces reading this plan.** Written by the previous session, ~40 lines | The plan is read once, at S0 |
| **Lessons are tagged by stage type**; a session reads only its tags | 27 untagged lessons is a per-session tax on all of them |
| **The acceptance table lives in `spec.py`, never in prose read at runtime** | A session runs the spec and reads pass/fail, not 24 rows |
| **Tests run quiet; only failures print.** Affected subset mid-session, full suite once at close | A suite printing 339 passing test names is pure waste |
| **Never read a file you are about to overwrite** | Common and invisible |
| **Bundle verification is a fixed script, not an exploration** | It is the same six commands every time |

### Subagent delegation — delegate reading, not deciding

The test is the **ratio of output to input**. Delegate when a task consumes a lot
of context and returns little; keep when the output feeds further design in the
same session.

**Delegate:**
- Literature verification of acceptance values — searches are read-heavy, the
  return is a number and a citation
- Auditing a large existing spec for a short answer — one agent reads it, returns
  a list
- Writing test suites against a settled contract
- Independent stage implementations that do not interact

**Do not delegate:**
- Any ruling, or any design whose output feeds more design this session
- Anything where the subagent's return is large — it gets read back anyway
- The audit sessions. Finding a defect nobody saw requires the whole context

### Credentials

Push needs a fine-grained personal access token, and it must be supplied each
session because containers do not persist. Scope it as tightly as the work
allows: **this repository only, `Contents: read and write`, short expiry.**
Nothing else is needed — no org scope, no workflow scope.

Two shapes, pick one:

- **Push to `main` directly.** Lower friction. Safe because sessions are
  sequential and rule C2a forbids force-pushing, so a rejected push is a signal
  rather than an obstacle to overcome.
- **Push the session branch only; merge by PR.** One click per session, and the
  blast radius of any mistake is one branch. Recommended if the token's lifetime
  is long.

Rule C2c covers the rest: the token stays out of the working tree, and a
pre-commit hook refuses staged content matching `ghp_` or `github_pat_`.

### Subagents and the remote

Subagents share the main agent's checkout and **do not push**. Delegated work
returns to the session, which commits it. *Justification: a subagent pushing
independently would need its own credentials and could interleave commits in an
order nobody chose* `[inferred]`.

### Which sessions to run on Fable

**Fable draws on a separate limit**, so its marginal cost against the rest of the
build is near zero and unused quota is simply wasted. That removes the trade-off
this section originally agonised over: the question is not whether the capability
gap justifies the cost, but which sessions are longest and hardest.

Anthropic's guidance is a **procedure rather than a claim** — start on Opus 5 and
move to Fable when evals at higher effort still fall short `[recall: Claude
Platform docs, "Choosing the right model"]`. The stated strengths are long
autonomous sessions, investigating before acting, and verifying work more often
`[recall: Claude Code docs, model configuration]`.

**S10 — audit. The strongest case, and it is structural rather than a hunch.**
S1–S8 all have gates: acceptance checks pass or they do not, so a weaker model
fails *visibly*. S10's output is "here are the defects I found", and that cannot
be checked for false negatives. **Capability matters most exactly where
verification is weakest.**

**Run S10 twice, once on each model, and diff the defect lists.** It is the one
session whose output is directly comparable, it converts an impression into a
measurement, and an audit run twice is not wasted work even when the two agree.
Record the comparison in `DECISIONS.md` — it is the only controlled evidence this
project will produce about whether the model choice mattered.

**S9 — advanced model. Second.** Long-horizon, and it contains a specific trap
(the complexity-class change in the DTD) that must be verified rather than
assumed.

**S0 — ran on Fable, and the result is evidence but not a comparison.** S0 found
a real arithmetic error in this very board — the debt line claimed 9 open and 2
discharged against a register of 9 items of which 2 were struck `[verified:
DECISIONS.md D15]` — and turned the fix into a generated number that cannot drift
again. That is a data point. It is **not** a controlled result: there is no
counterfactual S0, and the session was also unusually well specified. Do not
treat it as settling the question that S10's double run is designed to answer.

**After S14 — what the double run said, and the rule it leaves.** S10 ran six
times on four lists and the model did not visibly matter; the stated aim did
`[verified: DECISIONS.md D102]`. What did separate the sessions since is the
kind of work: the sessions that overturned a register assumption by probing
first (D110, D113, D114) and the one that caught a solver defect by probing a
third ruleset (D113) were judgement sessions, where a wrong answer passes
every gate. So the rule for what remains (§5d): **Fable where verification is
weakest** — a decision about what the model derives, a mechanism that could be
tuned into passing, an audit — and **Opus where the contract is decided and the
gate is in `spec.py`**, which is how S1–S8 were built and passed.

---

## 5b. Sessions

Eleven. **All physics is headless through S5** — the viewer arrives at S7 with
everything to show at once, so the rendering harness is written once instead of
five times.

That ordering is not only cheaper, it is what rule B1 requires. It has already
paid once in this project: the benchmark written to measure the advanced model's
cost found a defect in a proposal made a turn earlier, and no picture would have
shown it `[verified: bench2.py §1]`. **Instruments before pictures.**

| S | Deliverable | Gate | Notes |
|---|---|---|---|
| **0** | Repo init, `tools/progress.py`. `core/` + registry, fielddoc, seeds, grids. `graph`, `preflight`, `determinism`. `spec.py` as **data**. **Stub second model.** No physics | Graph acyclic per model; both models preflight; determinism holds; `spec.py` lists 24 quantities and reports each not-yet-computable | **Fable.** `convergence`/`performance` deferred to S10 — they need something to measure (rule B1) |
| **1** | Halo & disc (shared impl) | λ_d = 0.0144 from a **joint** fit to stellar mass and scale length; R₂₀₀ arithmetic | Delegate: verify M₂₀₀, R_vir values |
| **2** | SFH + chemistry, simple | Gradient ≈ −0.06 dex/kpc; SFR ≈ 1.65 M☉/yr | |
| **3** | Assembly + `mergers[]` with `gas_fraction` | f_Σ = 12% ± 4%; **debt #9: run a merger-free galaxy, check whether α-bimodality appears anyway** | |
| **4** | Pattern: bar, arms | `PITCH_YU` seeded; S-spread recorded once | |
| **5** | Systems: catalogue, headless | 10⁶ stars < 10 s; per-region determinism | |
| **6** | API. Headless and fully tested | **One `fetch`**; `/api/version` hash; **cold timings published** | Testable without a browser — separated from S7 deliberately (rules D2–D4) |
| **7** | Viewer: galaxy view, checkpoints, previews for stages 1–5 | Field-as-image + clickable seeded sample; reopening a stage discards later ones | Largest quota risk — visual work iterates blind |
| **8** | Planets stage + system view | Occurrence vs [Fe/H]; belts derived from resonances; **planet scalar set declared and closed** | No external dependency — see §5c |
| **9** | Advanced: multi-element + DTD, migration, outflows, coupling | **Exponent 1.0 in N_t**, not 2.0 (`bench2.py`); coupling multiplier measured | **Fable** |
| **10** | Audit: `convergence`, `performance`, calibration debt | N_R and N_t swept **independently** | **Fable, run twice** — diff the defect lists |

### On splitting

**The binding constraint is usage quota, not wall clock.** A session can run as
long as it likes; what it cannot do is exceed its allowance and stop mid-way.
That makes the split criterion a **token-volume judgement**, which belongs with
the token discipline above rather than being read off the session table.

The signal to watch is not elapsed time but **iteration depth** — how many
test-fix cycles a session has burned. A session that cleared its gate on the
first or second attempt is nowhere near the limit; one grinding through a
rendering loop or a failing acceptance check is consuming quota fast and has
little to show per token. S7 is the likeliest, because visual work cannot be
tested headlessly and so iterates blind.

Splitting costs one session-open — a clone plus two capped documents, small under
the discipline above. It **saves** an entire iteration loop being carried in a
context that is already long.

So: split freely, with one exception. **S9 must not split.** Its two halves touch
the same stages, and splitting means reading the chemistry implementation into
context twice — the one case where the handoff costs more than it saves.

### Partial close — what a session does when it senses the limit

The close ritual assumes a session finishes. **A session that stops because it
ran out of allowance must not leave the next one to reconstruct where it got to**
— reconstruction is exactly the expensive thing this protocol exists to avoid.

So, from the start rather than as a panic measure (rule C2d):

1. **Commit at every completed sub-deliverable**, not only at close, and push the
   branch each time. A stranded session loses only what came after its last push.
2. **Keep `BRIEF.md` written-ahead.** At the point a session's plan is clear,
   write the next brief *as if stopping now*, and refine it at close. A brief
   that already exists costs nothing to update and everything to write from
   scratch after the fact.
3. **On sensing the limit, stop and close partially**: commit, push, append what
   was done and what remains to `BRIEF.md`, set this session's board row to ◐
   with a note. Do not start new work in the hope of finishing it.
4. A partial close does **not** merge to `main`. The branch stays open and the
   next session continues on it. No session tags in any case (rule C2e), so
   there is nothing extra to withhold here.

---

## 5a. What each session reads

**All three documents are committed in S0's first commit.** After that they are
in the repo and can be consulted by section rather than read whole.

| | S0 | S1–S10 |
|---|---|---|
| `RULES.md` | **In full** | **In full** — it is capped and every rule applies |
| `GALAXY_PLAN.md` | **In full** | Not read. `BRIEF.md` replaces it (rule C4) |
| `GALAXY_INPUTS.md` | §7 and §11 only | By section, when a `BRIEF` names one |
| `RESUMING.md` | Written, not read | **In full** — capped at 120 lines (rule C3) |
| `BRIEF.md` | — | **In full** — ~40 lines |

`GALAXY_INPUTS.md` is a **source document, not a session-time read.** S0's job
includes consuming the durable parts of it into code, after which they are never
read as prose again:

- **§7's 24 acceptance quantities → `spec.py` as data**, with a runner that
  reports each as pass, fail, or not-yet-computable. From S1 onward a session
  runs the spec and reads pass/fail (rule C6).
- **§11's input table → the registry.** Names, defaults, units, ranges.
- **§4b's three categories → already lifted to rule A10.**

What stays in `GALAXY_INPUTS.md` is reasoning — why a quantity is derived rather
than input, which conflicts are preserved, what each debt is. A session consults
those when its brief says to, not by default.

### The three gaps S0 must close itself

None of these is settled in any document, and the registry cannot be written
without them:

1. **The closed unit vocabulary** for field declarations — kpc, Gyr, M☉, dex,
   km/s, M☉/yr, dimensionless, and whatever else the six stages need. Closed
   means a field cannot invent one.
2. **The `kind` vocabulary** — continuous scalar field, category, per-object
   scalar, catalogue column.
3. **Grid defaults.** `N_R = 400` radial annuli, `N_t = 2000` timesteps, `N_z`
   ≈ 60 for the (R, z) potential grid. N_R is measured nearly free up to 400 —
   exponent 0.13 in N_R against 1.0+ in N_t `[verified: bench2.py §3]` — so the
   two are separate quality knobs, never one (rule A6, and `convergence.py` at
   S10).

---

## 5c. The planets handoff has no external dependency

An earlier draft made S8 block on enumerating another project's input list. **That
dependency is removed.**

The planets stage publishes a **self-defined, closed set of planet scalars** —
mass, insolation, volatile inventory, rotation, obliquity, atmosphere class —
declared under rule A8 like every other field, chosen for what the formation
model actually determines rather than for what some consumer currently accepts.
`preflight` asserts the set is closed and documented. That is the whole gate.

This is better design independently of scope. A stage shaped by a downstream
consumer's current input list inherits that consumer's arbitrary choices; a stage
that publishes what it knows lets integration adapt to it. Any future consumer
writes an adapter.

**Recorded as a note, not a blocker:** if this project is later joined to a
surface-scale world generator, the two scalar sets must be reconciled, and
whichever side is authoritative for a given quantity must be declared once. That
reconciliation is an integration task with its own session, not a prerequisite
for S8.

---

## 5d. Completing the project — S15 to S22 (written after S14, at the owner's request)

The build (S0–S10) closed on schedule; S11–S14 then diverged from §5b into
integration, fixes and physics decisions, each session taking whatever the last
one's `BRIEF.md` put first. That was the right order for the work but it is not
a plan, and a plan is what tells a maintainer when the project is *done*.

**Done means** `[inferred]`: every acceptance row either passes or is a recorded
miss whose cause is a *mechanism the model lacks*, not a constant it could tune
(rule B5); every item in the register is discharged, or ruled permanent with the
reason written in — a property of the model's scope, like the simple model's
one-abundance chemistry (#15), or of the sources, like the zero-width targets
(#17); the viewer shows every published field; the tag batch in `MANUAL_TODO.md`
has been applied from a desktop; and `verify_clone` is OK on `main`.

Eight sessions. Each opens per RESUMING.md, works on `session-NN`, and closes by
§5's ritual, tags queued (C2e). Gates are read from `python -m galaxy.specs`,
never from prose. **Probe before build** in every physics session: S13 and S14
each found, with a fifty-line probe, that the register's stated lever had the
wrong sign or the wrong magnitude (D110, D113).

| S | Deliverable | Gate | Model, and why |
|---|---|---|---|
| **15** | **Row 3's cause, derived** (#12, #46, #11). Three levers, none free: the assembly epoch (0.7–1.0 closes the row alone; the cited range is 2–3), the contraction's calibration (a mass- and epoch-dependent (A, w) is the untried form; A = 1.6 alone reads 256.8), and a less compact baryon distribution (the bulge is worth 5–8 the right way, D110). Decide which the model *derives*; sweep nothing to the answer | Row 3 inside 245–251 with its cause a derived quantity, or a miss whose prediction names a mechanism; row 19 unmoved; v_esc(R₀) inside 530–580 as the second discriminant | **Fable.** A row can be closed by tuning and no gate would see it — verification is weakest exactly here |
| **16** | **The extended component with its own timescale** (#18, #43, #45). D114 showed a share at k R_d on the disc's timescale buys row 20 with row 2; the component must arrive late or diffuse enough to stay under the threshold. Derive the timescale (the halo's angular momentum arriving late is the physical candidate), then build it in `sfh` behind `infall_profile` | Rows 2 and 20 inside with rows 4 and 22 unmoved; row 3 read with it; `NET_YIELD` and `WIND_SPEED` refitted and recorded (rule B10) | **Fable.** The timescale is a derivation decision (D114), and #45 says a wider first component is the wrong answer that passes |
| **17** | **The bulge stage and M_•** (#11, #2, #17, ruling 10). Hernquist spheroid drawn from the disc in proportion, as D110 probed; rows 10–14; M_• as derived mean plus seeded residual, row 18 statistical; row 14 needs the source's uncertainty entered first (#17) | Rows 10, 12, 13 inside; row 11 no longer passing on the cancellation; rows 14 and 18 statistical per their debts; row 3 moves −5 to −8 and is re-read | **Opus.** The contract is decided (D110, §13) and every row is in `spec.py` — a gated build, as S1–S8 were |
| **18** | **The thick disc** (#19). Radial heating with the vertical kick is the prediction: a merger that thickens the disc also spreads it, so rows 5 and 11 can be right together and row 9 comes off the cancellation | Rows 5, 7, 9 and 11 inside together in the simple model, row 9 not on a cancellation (a sweep of the merger's `gas_fraction` leaves it inside) | **Fable.** A cancellation can be tuned into passing; the gate is the sweep, and judging it is the session |
| **19** | **The catalogue migrates, and the viewer shows the new fields** (#31, #32). Birth radius drawn around the present one with the migration kernel's width, the abundance looked up there, both models (D110); new golden values; previews for `halo_contraction` and whatever S15–S18 published | The catalogue's [Fe/H] spread at R₀ equals the chemistry's `feh_spread_sun`; determinism and per-region checks OK on the new golden values; every published field has a preview | **Opus.** A specified change in `systems.materialise` with its own golden values; the viewer work is the S7 kind |
| **20** | **The advanced model's [α/Fe] valley** (#27, #42, #26). The mechanism that makes the inner disc fast without steepening the infall law everywhere — the bulge's inflow is the named candidate — then rows 5–11 and 24 in the advanced model, and rows 6 and 7 judged together with both heating constants re-examined | Row 24 `bimodal_wide` at the default grid, stated (the N_t = 8 trap); row 22 still inside; rows 6 and 7 inside together | **Fable.** The hardest open physics, and the one with a known false positive (a coarse grid manufactures the valley) |
| **21** | **Audit II, run twice with two stated aims** (D102's lesson). Aim (a): every prediction the register and `spec._MISSES` made since S13, killed or held with a number (rule B4). Aim (b): the instruments and the viewer — cold paths (D4), the flaky per-star slope (D115), the audit tests' pins. **Reserved numbers**, fixed when S21 opens (decisions are numbered sequentially and S15–S20 each append theirs): fourteen debts and fourteen decisions for (a) starting at the next free numbers, the following fourteen of each for (b), so the lists port without renumbering (D99). Written at D116 as #47–#60 / D117–D130 and #61–#75 / D131–D145, before S15 took D117 | Two lists, diffed; every prediction has a verdict; no green row unconditioned (AUDIT_RUN2 §5) | **One on Fable, one on Opus**, aims different by design — extends the only controlled evidence the project has (D102) |
| **22** | **Close-out.** Port both audit lists onto `main` (never merge the branches, D99); rule every open debt discharged, permanent or carried, with the reason; apply the tag batch from a desktop and delete the stale `s01` (MANUAL_TODO); final RESUMING/BRIEF for whoever maintains it | Tags on the remote, `git ls-remote --tags` listed in DECISIONS; register with no unruled item; `verify_clone` OK | **Opus.** Procedure with a checklist; the judgement was spent in S21 |

**What this does not promise.** Rows whose cause is the model's scope stay
misses by design: the simple model's gradients (#15) are a third of the observed
because it has one abundance and no wind, and that is what the advanced model is
for. Debts #3, #5, #10, #21–#23, #25, #33, #34, #36, #39 and #44 are the kind S22
rules on rather than closes — each is a measured limitation with its number
already in the register, and a session spent closing one would be a session
inventing a variable (rule A4). The order above is by dependency, not by
importance: S15 before S16 because the component is judged against row 3, S17
before S20 because the valley's candidate mechanism is the bulge's inflow, S19
last of the builds because it re-pins every seeded number the earlier sessions
move.

## 6. What the executable specs assert

| Spec | Addition |
|---|---|
| `graph.py` | Acyclic **per model**, and the stage→checkpoint map is derived from it |
| `preflight.py` | Field declarations reconcile **across models**; optional fields have handled absence |
| `determinism.py` | Per-region determinism: `hash(seed, star_id)` is order-independent |
| `convergence.py` | **N_R and N_t swept separately.** They are not one quality knob — measured exponent 0.13 in N_R against 1.0+ in N_t `[verified: bench2.py §3]` |
| `performance.py` | Asserts the DTD stays linear in N_t. This is the one place the advanced model can change complexity class |
| `spec.py` | The 24 acceptance quantities, with entries 13/14/16/17 **statistical rather than pointwise** (`GALAXY_INPUTS.md` §4b) |

---

## 7. Risks, ranked

1. ~~The λ circularity.~~ **Discharged by ruling 8.** Replaced as top risk by:
   **the λ_d prior.** Default and prior must be drawn from the same population —
   seeding rolls from a halo-λ log-normal would make every generated galaxy three
   times too extended, and the error would look like a plausible galaxy.
2. **The advanced model is unfalsifiable in the generator.** Its headline outputs
   can only be checked against our galaxy, not a random one
   (`GALAXY_INPUTS.md` §10). S8–S9 must ship with that stated, or they will look
   like progress they are not.
3. **Two-model boundary rot.** Mitigated by the S0 stub, and only by it.
4. **Browser rendering at 10⁶.** Mitigated by field-as-image; the LOD ladder is
   the part most likely to slip.
5. **Warm-cache self-deception.** This class of defect can survive every check
   ever run against it, because the checks run warm `[recall]`. Cold timings from
   S6, published, every session (rule B2).
6. **Acceptance table internal inconsistency.** The 24 quantities are not
   mutually consistent (`GALAXY_INPUTS.md` §7); a model fitting all of them
   exactly is fitting a contradiction.

---

## 8. Rulings needed before S0

**All settled.** The input vector is closed and S0 can declare it.

### The seven

| # | Input | MW default |
|---|---|---|
| 1 | `halo_mass` M₂₀₀ | 1.1 × 10¹² M☉ |
| 2 | `disc_spin` λ_d | 0.0144 |
| 3 | `halo_assembly_z` | z ≈ 2–3 |
| 4 | `baryon_retention` | ~0.35 |
| 5 | `infall_timescale` τ₀ | ~7 Gyr at R₀ |
| 6 | `inside_out_index` n | — |
| 7 | `migration_efficiency` | — |

Plus `world_seed`, `systems_seed`, `planets_seed`, `pattern_seed`, and
`mergers[]` — the last now carrying `gas_fraction` per ruling 11. **Ceiling 12;
five slots of headroom.**

### Rulings that changed the build

- **8** discharged debts #1 and #7. S1's gate is no longer "resolve the λ
  circularity" but "reproduce λ_d = 0.0144 from a joint fit to stellar mass and
  scale length."
- **11** cut an input and made the model falsifiable. **S4 gains a gate**: run a
  merger-free galaxy and check whether α-bimodality appears anyway (debt #9).
- **10** added a sixth seeded residual and no machinery.
