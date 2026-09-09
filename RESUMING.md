# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The build is closed** (S0–S18; §5d plans S19–S22).

## Open a session (rules C1, C2b)
```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```
Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section. Branch `session-NN`;
commit and push at every sub-deliverable (C2b). In a worktree: `git config --worktree core.hooksPath tools/hooks`.
Write files with `newline="\n"`: a CRLF working copy breaks progress.py's line regexes.

## Layout
```
galaxy/core/              units (32 closed), cmaps (8 + stops, A9), fielddoc (FieldDecl, 6 Kinds,
                          Ramp/Palette, AXES), stage (Stage, Context, CHECKPOINTS), registry
                          (12 INPUTS, MODELS, IMPLEMENTATIONS), seeds, grids, special (I1, K0, K1, erf)
galaxy/models/            level0 (shared constants), simple (+NET_YIELD), advanced (yields, DTD, wind)
galaxy/stages/            cp1 halo (NFW, budget, R_d, the contraction on its own mesh; ρ_DM and the
                          contracted fit S15; both ends of the angular-momentum distribution — the
                          high-j tail S16, the spheroid S17) + disc (the cp1 preview, κ(R) S18, the
                          basis-free razor-thin solver S18) + nucleus (M_•, seeded, S17); cp2 assembly
                          (delivery, σ_z by birth time, the radial spread S18); cp3 sfh (infall =
                          exponential + tail, less the spheroid; Kennicutt's threshold off κ S18; the
                          stars moved through the spread S18), chemistry / chemistry_dtd, vertical /
                          vertical_alpha (sort stars_formed_history); cp4 pattern; cp5 systems; cp6 planets.
galaxy/run.py, specs/     run(model, inputs, grid, only=…, resume=…); graph, preflight, determinism, spec (misses
                          D87; "no testable target" D100; median D109), convergence (D94, D101), performance (D95, D101)
galaxy/api/               service (routes), wire, version, http; client/ (the viewer)
tools/                    progress, bootstrap, verify_clone, timings, scaling, shot, hooks/
tests/test_audit.py       the S10 audits' measurements as tests (#12, #17, #21, #26–#28, #41–#45); S14–S18's
                          end test_halo / test_sfh / test_vertical. AUDIT_RUN1/2.md: main's S10 lists (D97, D102)
```
## Writing a stage

- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a
  `FieldDecl` beside its compute: name, label, unit, kind, axes in `(R, t, z, phi)` order,
  ramp, meaningful_zero, provenance, about.
- `compute(ctx)` sees `ctx.grid`, `.inputs`, `.constants`, `.fields` (strict) or `.get()` /
  `.has()` (optional) and `.rng(seed, *path)`; only declared names resolve, and it returns
  exactly the declared names, shape and value class checked.
- `IMPLEMENTATIONS.register(...)`, import in `stages/__init__.py`, map the slot in the models
  that use it. A constant goes in `level0.py` if both models' stages read it, else in the one
  model that does (D29, D85). A field nobody reads is dead (debt #30).
- **A seed binds at the checkpoint of its earliest reader and `graph` requires that to equal
  §3's hypothesis**, so a stage that draws sits where its seed says (S17). A stage reading a
  seed publishes *seeded* fields, all of them: split the derived half off into its own stage
  rather than mislabel it (D55, `bar`/`pattern`, `halo`/`nucleus`).
- **Two implementations of one slot** publish the same names under the same contract
  (`FieldDecl.contract`; `dataclasses.replace(decl, about=…)` keeps it) and their own fields as
  `optional=True`, read through `requires_optional` and `.get()` (D86).
- A named ruleset is a constant with its alternative in the about line, chosen before the row
  is read (D113); a mechanism is probed by substituting one function per half from a script, the
  repo unchanged (D114) — or a stage's whole compute, set on the Stage, not the module (S16); a
  default is measured or derived by a test (D30, D117); a derived scalar lives on the stage's own
  mesh, never the grid (D119). A quantity two stages read is published once by the stage that
  owns it, not computed twice (`epicyclic_frequency`, `stars_formed_history`, S18; rule A9).

## The API and the viewer
- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path, query)`
  is the same without a socket and is what the tests drive. `model=advanced` selects the second
  model on every route. A new route is a `Route` in `service.ROUTES` with a handler `_<name>`,
  **plus a row in `tools/timings.py`** — a test fails without one.
- Metadata answers from declarations and must not reach the runner; whatever computes goes
  through `Service.compute(...)`, the closure above the fields asked for (D4, D63); objects are
  materialised per request (D82). `transport.js` holds **the only `fetch`**; the gate asks
  `git ls-files` what the repository contains (D101). No about line names a constant (D5).

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. 7
  controls, 4 seeds, `mergers`; every input has a default and every control a range. Every
  factual claim in every document is tagged `[verified: cite]`, `[recall]` or `[inferred]`
  (B14); a bare verified tag fails a test. A new unit, kind, axis, object class or cmap is a
  `core/` edit plus a DECISIONS.md entry. Debts live in GALAXY_INPUTS §11 and
  `tools/progress.py` counts them: add an item, never a count. Decisions are sequential.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, rule A7) with its
  model, debt, reason and a prediction that could kill it (D33, D87); it still reports `fail`,
  never widen a target (B5), and a miss that starts *passing* fails the run for that model (debt
  #29) — remove it and **write down why it passed**, which may not be the mechanism its debt
  named (S17 row 2; S18 row 3, on the kick and the solver, not the bar). A pointwise row with
  `lo == hi` says "no testable target" (D100); off that list is a citation with an uncertainty (D122).

## What the instruments said at S18 close (2026-09-10)

- graph: acyclic, both models; the disc now runs before assembly (it reads the curve). preflight
  OK: 0 UNSET. determinism OK, reproducible across processes (two hash seeds). No input unbound.
- spec: simple **10 pass, 12 fail, 2 n-y-c** (fails 5, 7, 8, 9, 11, 12, 13, 14, 18, 20, 22, 23);
  advanced **9 pass, 14 fail, 1 n-y-c** (adds 6, 24; drops 8, 9 → 5–9, 11 under #27; 22 under #47).
  Every failure recorded for its model. Row 3 came off the miss list at S18 by passing (D124).
- Numbers, to spot a regression by (S18): z_f 1.66, c₂₀₀ 8.24, contracted fit 15.0, R_d 2.605
  (fitted **2.441**); tail share 0.0756; spheroid 7.71e9, a 0.365; M_star **4.75e10**, SFR **1.755**,
  gas **1.11e10**, H **8.09e9** (1.1e9 of it inside 4 kpc, D124); κ(R₀) 40.1, **Σ_crit(R₀) 11.5**,
  gas at R₀ **10.8**; the kick's spread at R₀ **1.47 kpc**; v_tan **250.96** (251.3 until S18; 251.17
  on this solver); halo at R₀ 163.2; simple grad −0.0337, old −0.0069, thick M 9.6e9, row 5 1.17,
  row 9 **0.051**, row 6 327, row 7 1279; advanced grad **−0.0698**, f_esc **0.699**, WIND_SPEED
  **860.3**, NET_YIELD **0.01376**, row 6 **373**; rows 16/17 medians 42.8 / 5.70; row 18 median
  1.97e7; centre [Fe/H] 0.70 (advanced) / 0.25. **Convergence**: 0 drifts on N_R, N_t, N_z in
  either model; advanced rows 5, 7–11 `vacuous` (debt #27). **Profile** (D125): sfh is the costliest
  physics stage now. **Register**: 32 open, 17 discharged; #49 opened at S18. Audit branches stay unmerged.

## Close a session (GALAXY_PLAN.md §5, in this order)

0. Tick the board — surface, model **actually used**, tag, date — then `uv run python
   tools/progress.py`, then `uv run pytest` once, quiet, **backgrounded with its exit status
   appended to its log** (it outlasts the tool's cap), the merge gated on that status (D115, D120).
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **publish the cold timings** (rule
   B2), the profile (D95) and, when a stage's cost changes, `tools/scaling.py`. Then rewrite
   this file in place (≤ 120 lines) and write BRIEF.md (≤ 60 lines).
2. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into
   main: …`; push both. **Do not tag** (C2e) — add your MANUAL_TODO.md row with the last
   session's merge SHA filled in, and never force-push.
3. `uv run python tools/verify_clone.py --ref main` — clones fresh, bootstraps, runs the
   suite and the specs there; refuses if the working tree is dirty.

A session that stops early closes **partially** (C2d): commit, push, write what remains into
BRIEF.md, mark the row ◐, do **not** merge. **Credentials:** the helper or a repo-scoped token; never push a tag (C2e).
