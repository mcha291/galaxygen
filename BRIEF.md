# BRIEF — Session 8: the planets stage and the system view

Open per RESUMING.md. Read RULES.md in full, then this. Do not read GALAXY_PLAN.md.
Read **GALAXY_INPUTS.md §12** — the planets stage — and §7 rows 13-14 only if a
row needs it. There is no external dependency here: everything the stage needs is
already published.

## Build

- `galaxy/stages/planets.py`, checkpoint 6, seeded by `planets_seed` — the last
  empty checkpoint on the board, and the viewer already says so on that screen.
- **First, close a gap S7 walked into.** A star's identity is `(cell, index)`
  (D60) and *neither is published*: the catalogue's columns are all physical, so
  nothing can name a star to open its system. Publish the identity as columns
  from `systems.materialise`, and the system view becomes addressable without the
  viewer inventing a key.
- A route for one system — `/api/system?cell=…&index=…` — that materialises **one
  cell** and takes the star out of it. It must not rebuild the galaxy: the
  closure it needs is what the catalogue stage reads, and `materialise(cells=[c])`
  gives exactly the stars that cell has in a full sweep (D60). A row in
  `tools/timings.py` or a test fails.
- The viewer already selects a star on click (`stars.js`, `app.js`) and shows its
  columns. The system view is that panel, grown: the planets, their orbits, the
  belts. Nothing new is needed in the transport.
- **The planet scalar set is declared and closed** in this session: every
  published planet quantity gets a `FieldDecl` with a unit from the closed
  vocabulary (`Mearth`, `Rearth`, `AU`, `K`, `Searth`, `day` are all in it).

## Gate

- Occurrence rises with `[Fe/H]` — read the star's own published metallicity, do
  not re-derive it (rule A3, and the column is right there).
- Belts are **derived from resonances**, not drawn from a distribution.
- The planet scalar set is closed: `preflight` reconciles it across both models.
- Cold timings published, the system route included (B2, D76).
- The four client gates still hold: one `fetch`, no colour literal, no cmap name,
  no storage API — they are tests, and any new module inherits them.

## Traps

- **No new inputs** (A2, A4). Planets are derived from the star and seeded from
  `planets_seed`; a knob for occurrence would be an input invented to justify a
  stage. §12 has the argument already.
- **Count, do not sample** (B8). The number of planets a star has is drawn; their
  properties are inverted from distributions the stage publishes. Rejection
  sampling is what this project refuses.
- A `Generator` costs ~22 µs to construct (D61), so a system opened per click is
  cheap and a system opened per *star in the catalogue* is not. Open on demand.
- A star belongs to the cell that drew it, not the cell its radius falls in (D69).
- Rule D1 does not bend for the system view: **a page load lands on stage one**,
  so the system is a panel inside checkpoint 6, never a URL that reopens it.
- `uv run python tools/shot.py --path /` renders the page to a PNG. Look at it
  before believing it (D77) — three defects at S7 were invisible to every test.
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill in
  S7's merge SHA from `git rev-list -1 --grep='^Merge S7 into main' origin/main`.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`.
