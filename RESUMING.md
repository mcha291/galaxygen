# Resuming

How to open the repository, where things are, what the instruments say. GALAXY_PLAN.md's status
board is the only record of what is done (A9); this file does not repeat it, is rewritten each
session, capped at 120 lines (C3). **The build is closed** (S0–S20; §5d plans S21–S22). **You are
on `claude/keen-lamport-lldlvp` = S21's aim (b) branch (`session-21-b`), which merges into neither
aim (a)'s nor `main` — S22 ports both lists (D99). No physics changed here.**

## Open a session (rules C1, C2b)
```
git clone https://github.com/mcha291/galaxygen.git && cd galaxygen
uv run python tools/bootstrap.py       # installs the pre-commit hook path, checks imports
uv run pytest && uv run python -m galaxy.specs    # the suite, then the spec reports
```
Then RULES.md in full and BRIEF.md; GALAXY_INPUTS.md only by section. Branch `session-NN`; commit
and push at every sub-deliverable (C2b). In a worktree, `git config --worktree core.hooksPath
tools/hooks`; write files with `newline="\n"` (CRLF breaks progress.py's regexes).

## Layout
```
galaxy/core/    units (32 closed), cmaps (8 + stops, A9), fielddoc (FieldDecl, 6 Kinds, Ramp/
                Palette, AXES), stage, registry (12 INPUTS, MODELS, IMPLEMENTATIONS), seeds, grids,
                special (I1, K0, K1, erf)
galaxy/models/  level0 (shared; MERGER_HEATING 88.8 derived, S20), simple (+NET_YIELD), advanced
galaxy/stages/  cp1 halo (NFW, budget, R_d, the contraction on its own mesh; the high-j tail S16,
                the spheroid S17) + disc (κ(R)) + nucleus (M_•, seeded); cp2 assembly (delivery,
                σ_z by birth time, the radial spread); cp3 sfh (infall = exponential + tail less
                the spheroid; `first_infall` is one substitutable function, S20; Kennicutt's
                threshold off κ — which is why `disc` is in every route's closure, #66), chemistry
                (the migration kernel, read by chemistry_dtd and by systems, A9) / chemistry_dtd,
                vertical / vertical_alpha (`birth_population`); cp4 pattern; cp5 systems; cp6
                planets.
galaxy/run.py   run(model, inputs, grid, only=…, resume=…, impls=…);  galaxy/specs/: graph,
                preflight, determinism, spec (D87, D100, D109), convergence (D94), performance
                (D95; both catalogue fits since S21b, D145)
galaxy/api/     service, wire, version, http; client/ (four scalars reach no surface of it, #69).
                tools/: progress, bootstrap, verify_clone, timings, scaling, shot, hooks/.
                AUDIT_RUN1/2.md are main's S10 lists, AUDIT_S21B.md this branch's
tests/          test_audit.py is the S10 audits as tests, S20's three probes and S21b's five;
                S14–S18's end in test_halo / test_sfh / test_vertical, S19's in test_systems
```
## Writing a stage (S22 writes none — the short form; the long one is on `main`)
- `Stage(id, slot, checkpoint, about, compute, reads_*, requires*, publishes)`, each field a
  `FieldDecl` beside its compute; `compute(ctx)` sees only what it declares and returns exactly the
  declared names, shape and value class checked. Register, import in `stages/__init__.py`, map the
  slot; a constant both models read lives in `level0.py` (D29, D85); a field nobody reads is dead
  (#30); two implementations of one slot share a `FieldDecl.contract` (D86); a seed binds at its
  earliest reader's checkpoint and publishes *seeded* fields, all of them (S17, D55). A named
  ruleset is a constant with its alternative in the about line (D113); a mechanism is probed by
  substituting one function with the repo unchanged (D114); a default is measured or derived by a
  test (D30, D117, D128); a calibration's *arithmetic* is derived, not just its value (S20).
  **Per-region determinism is the catalogue's contract** (D60).

## The API and the viewer
- `uv run python -m galaxy.api` serves both on 127.0.0.1:8017; `Service().handle(path, query)` is
  the same without a socket and is what the tests drive; `model=advanced` selects the second model.
  A new route is a `Route` in `service.ROUTES` plus **a row in `tools/timings.py`**.
- Metadata answers from declarations and must not reach the runner; whatever computes goes through
  `Service.compute(...)` (D4, D63) and objects are materialised per request (D82) — outside it,
  which is why `Response.stages` cannot see that cost (#65). `transport.js` holds **the only
  `fetch`**; the gate asks `git ls-files` what the repository contains (D101).

## Conventions
- Names: fields, inputs, seeds, stages, models `lower_snake`; constants `UPPER_SNAKE`. 7 controls,
  4 seeds, `mergers`; every input has a default and every control a range. Every factual claim in
  every document is tagged (B14), and a verified tag cites something *inside* this repo — which is
  why a finding worth citing is pinned as a test the same session (S21b). A new unit, kind, axis,
  object class or cmap is a `core/` edit plus a DECISIONS.md entry. Debts live in GALAXY_INPUTS
  §11; `tools/progress.py` counts them — add an item, never a count.
- A failing acceptance row goes in `spec._MISSES` (or `_MISSES_ADVANCED`, A7) with its model, debt,
  reason and a prediction that could kill it (D33, D87); it still reports `fail`, never widen a
  target (B5), and a miss that starts *passing* fails the run (#29). `lo == hi` = no testable
  target (D100).

## What run (b) did — the record is AUDIT_S21B.md and D144–D150 (debts #65–#73)
- Rule D4 counted **at the stages**, not off `Response.stages` (B3): honest on all 17 endpoints,
  metadata routes run zero computes. Two things no record held — `materialise` / `one_system` run
  outside the runner so no `stages` tuple sees them (#65), and `disc` is back in every physics route
  since S18 where D115 records it gone, so the stage column is published again (#66).
- **The catalogue is priced per cell, not per star** (#67): the cells that realise a star saturate
  (349 of 1024 at 500 stars, 829 at 80,000), so seconds is a line in cells (R² 0.97) and a curve in
  stars (R² 0.67), and **there is no fixed cost** — it is the price of the cells the sample lights
  up. Both fits are published with their R²; D115's flake is that misfit, not the machine (#68).
- **The detector's mode test is a density test** — a mode of share s and width σ is kept iff
  `s·erf(0.05/(σ√2)) ≥ 0.1` — so at row 9's share and the observed α-width the Milky Way's own thick
  disc reads `single`, 0.0929 against 0.1000 (#70). Stated, not moved (B5).
- **Four published fields reach no surface of the viewer**, both models (#69); S20's two numbers do
  reach it, the radial spread only as an image (#73). No pin in `test_audit.py` can flip its row; the
  wind's is 2.5× looser than the refit it watches (#71).

## What the instruments said at S21b close (2026-09-11, a web container)
- pytest exit 0, 4 skips. specs OK: graph acyclic, preflight 0 UNSET, determinism reproducible within
  and across processes; convergence 0 drifts, advanced rows 5, 7–11 `vacuous` (#27). spec unmoved from
  S20 — simple **10 / 12 / 2** (row 7 in at 962, row 3 out at 251.03, both on the re-derived kick),
  advanced **8 / 15 / 1** (row 3) — and no miss has started passing (#29). **Nothing physical moved.**
- Numbers to spot a regression by, all unmoved: z_f 1.66, c₂₀₀ 8.24, R_d 2.605, M_star 4.75e10, SFR
  1.755, H 8.09e9, Σ_crit(R₀) 11.5, WIND_SPEED 860.3, NET_YIELD 0.01376, feh_spread_sun 0.360, rows
  16/17/18 42.8 / 5.70 / 1.97e7, MERGER_HEATING 88.8, σ_z 35.0, the radial spread 1.09 at R₀ and 0.22
  at 2 kpc, rows 5 / 8 / 9 1.09 / 0.016 / 0.0455, advanced row 6 356; the valley `single` at N_t 1000
  / 2000 / 4000, dip 0.151 on 0.1/H(z_f) (D128).
- Profile — a web container, so shares carry and seconds do not: simple 0.861 s cold (systems 40.3%,
  sfh 21.8%, planets 17.0%), advanced 1.047 s (systems 33.0%, chemistry_dtd 31.4%); catalogue **423
  / 445 µs per cell** (D145). Timings: D150. Register **41 open, 18 discharged** (32 / 18 before).

## Close a session (GALAXY_PLAN.md §5, in this order)
0. Tick the board — surface, model **actually used**, tag, date — then `tools/progress.py`, then
   `uv run pytest` once, quiet, **backgrounded with its exit status appended to its log** (it
   outlasts the tool's cap); the close is gated on that line (D115, D120).
1. Append to DECISIONS.md, new rules to LESSONS.md tagged, **publish the cold timings** (B2), the
   profile (D95) and, when a stage's cost changes, `tools/scaling.py`; rewrite this file (≤ 120) and
   BRIEF.md (≤ 60).
2. Commit; `git checkout main && git merge --no-ff session-NN`, subject `Merge S<N> into main: …`;
   push both, **do not tag** (C2e), add your MANUAL_TODO.md row with the last session's merge SHA
   filled in, then `uv run python tools/verify_clone.py --ref main`: it clones fresh, bootstraps,
   runs the suite and the specs there, and refuses on a dirty tree. **On this branch step 2 is
   different by design — an S21 audit branch never merges** (D99) — so the close ends at the push
   and `verify_clone --ref <this branch>`; S22 does the porting.

A session that stops early closes **partially** (C2d): commit, push, write what remains into
BRIEF.md, mark the row ◐, do **not** merge. Never push a tag (C2e), never force-push (C2a).
