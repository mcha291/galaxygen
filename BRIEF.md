# BRIEF — Session 7: the viewer (galaxy view, checkpoints, stage previews)

Open per RESUMING.md. Read RULES.md in full — **section D is the whole session**
— then this. Do not read GALAXY_PLAN.md. Consult GALAXY_INPUTS.md only if a row
needs it. **This is the largest quota risk in the build** (GALAXY_PLAN §5b):
visual work iterates blind. Plan to close partially (rule C2d) rather than to
start something you cannot finish; commit and push at every sub-deliverable.

## Build

- The viewer's files go in **`galaxy/api/client/`**, beside `transport.js`. That
  directory is what `/api/version` hashes, so a stale bundle is one glance (D3).
- **Import `transport.js`; do not write another `fetch`** (rule D2). It already
  has `version/stages/fields/inputs/arrays/region`, the `galaxy-bin/1` decoder
  and `codes()` for BigInt category columns. A test scans every `.js` in the repo.
- A **static route** to serve those files is yours to add (`service.ROUTES` plus a
  handler, **plus a row in `tools/timings.py`** — a test fails without one).
- Stage-by-stage flow over the six checkpoints from `/api/stages`; controls from
  `/api/inputs` with their defaults and ranges; **every ramp, label and unit from
  `/api/fields` and nowhere else** (rule A9). No colour table in the viewer.
- Field-as-image from `/api/arrays`; the clickable seeded sample from
  `/api/region`. `stars=` there is the galaxy-wide count and a region gets its
  share, so the LOD ladder climbs by raising it — a smaller sample is a strict
  prefix of a larger one (D60), which is what keeps a click stable while more
  materialises underneath.

## Gate

- Field-as-image **and** a clickable seeded sample, both from the endpoints.
- **Reopening a stage discards every later one; a page load lands on stage one; a
  confirmed control is disabled, not hidden; a lock means "do not re-roll", never
  "freeze against upstream"** (rule D1). Assert these, in a test.
- Still exactly one `fetch`, still no physics and nothing generated persisted (D5).
- **Cold timings published** for every route, the new static one included (B2, D67).

## Traps

- **Debt #23 will be visible for the first time.** Nothing publishes a
  non-axisymmetric density, so the galaxy is a smooth axisymmetric disc: no arms.
  GALAXY_PLAN §3 calls stage 4 "the first recognisable galaxy" and it is not.
  **Do not paint arms the model does not have** — that is rule A4's failure one
  level up (D62). Report it; the fix is a field, and a field is a stage's job.
- A star belongs to the cell that *drew* it, not to the cell its radius falls in:
  inverting a ring's CDF can place it one R-spacing outside its own ring (D69).
  Draw cell boundaries knowing that.
- `feh_history` is 6.4 MB of float64 on the default grid. That is the honest
  value and the wire is right; the viewer decides what to ask for.
- Category columns arrive as `BigInt`; `null` in a header scalar means the model
  has no number there, and is never to be drawn as zero (rule B9).
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill in
  S6's merge SHA from `git rev-list -1 --grep='^Merge S6 into main' origin/main`.
  A test fails if a ☑ session has no row there.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`.
