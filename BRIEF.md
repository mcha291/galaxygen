# BRIEF — Session 6: the API (headless, fully tested)

Open per RESUMING.md. Read RULES.md in full — **section D matters most this
session** — then this. Do not read GALAXY_PLAN.md. Consult GALAXY_INPUTS.md only
if a row needs it.

## Build

- `galaxy/api/`: HTTP, JSON metadata plus binary arrays, **no rendering**. It
  publishes stage metadata, field metadata and arrays, and nothing about model
  internals (rule D5).
- Endpoints for: the stage list and their checkpoints; the field declarations
  (label, unit, kind, ramp, meaningful zero, about — the viewer's *only* source
  of rendering opinion, rule A9); arrays by field name; the input registry with
  defaults and ranges; a region query returning a materialised star catalogue.
- `/api/version` publishing a **content hash of the viewer's own bytes** (D3),
  so "am I running the new code" is a glance and not an investigation.
- **Cold timings published, every session from here on** (rule B2, GALAXY_PLAN
  §5b). S5's numbers are in D59; add the API's and keep the format.

## Gate

- **Exactly one `fetch` in the client transport, asserted in CI** (rule D2). The
  viewer does not exist yet, so assert it against whatever transport module you
  ship for S7 to import.
- `/api/version` returns a content hash that changes when the bytes change.
- **No endpoint runs more of the pipeline than its answer requires** (D4). This
  is the session's real work, not a checkbox: metadata must not touch a stage,
  and a region query must not rebuild the galaxy. Debt #24 is the same defect
  already present in the spec ensemble — fixing it here likely fixes it there.
- Cold timings published for every endpoint.

## Traps

- **D4 is the one that hides.** A metadata endpoint that quietly calls `run()`
  is cheap warm and ruinous cold, and invisible to every check made against a
  warm cache (rule B2, GALAXY_PLAN §7 risk 5). Measure cold, from a fresh
  process, and publish the number rather than the verdict.
- The catalogue is already regional and deterministic: `systems.materialise(...)`
  takes a cell list and per-region determinism is tested (D60). Use it rather
  than re-deriving; a region endpoint that regenerates the galaxy is exactly D4.
- Ramps come from the field declaration and nowhere else (rule A9). The API
  serves them; it does not invent them, and neither may the viewer.
- **Read D51 before trusting row 9.** It passes on two errors cancelling.
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill
  in S5's merge SHA from `git rev-list -1 --grep='^Merge S5 into main'
  origin/main`. A test fails if a ☑ session has no row there.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`.
