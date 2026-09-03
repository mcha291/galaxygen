# BRIEF — Session 4: pattern (bar and arms)

Open per RESUMING.md. Read RULES.md in full, then this. Do not read
GALAXY_PLAN.md. Consult GALAXY_INPUTS.md §5 (ruling 3, `PITCH_YU`), §4b (the
seeded-draw remedy) and §11 when you reach them.

## Build

- `galaxy/stages/pattern.py`, checkpoint 4, reading `pattern_seed` — the first
  **seeded** stage, so it is also the first real exercise of `ctx.rng`, of
  provenance `seeded` in the field declarations, and of `graph.py`'s provenance
  check. Expect that check to be the thing that catches your mistakes.
- Bar: half-length (row 15), pattern speed (16), corotation radius (17). Rows
  16 and 17 are **statistical** (debt #8): they pass when the central 95% of an
  ensemble of ≥ 20 seeded runs intersects the target, so the stage must be
  runnable over seeds cheaply and `spec.run` needs an ensemble argument.
- Arms: `PITCH_YU` seeded per ruling 3; record the S-spread once. Rule B11
  warns the pitch–shear correlation may be the wrong relation even where it
  fits — say which you used and what it would take to falsify it.
- Bulge mass (row 12) and bulge/total fraction (13, statistical) if the bar
  gives them honestly; leave them not-yet-computable rather than inventing a
  bulge the pattern does not produce.

## Gate

- `PITCH_YU` seeded, S-spread recorded once.
- Rows 16 and 17 report a statistical verdict over a real ensemble, not
  not-yet-computable.
- `python -m galaxy.specs` clean; every new failure is a recorded miss naming a
  debt and a prediction.

## Traps

- **Read D51 before you trust row 9.** S3's gate passes because two errors
  cancel; a test asserts the cancellation. Do not "fix" that test.
- Seeded fields must declare `provenance="seeded"` and the graph derives the
  truth from what the stage reads — a mismatch either way is a failure, and a
  field that is seeded in one model and derived in another is the open question
  D10 left for whoever hits it first.
- Draw through `ctx.rng(seed, *path)`, never `hash()` or module-level state;
  per-region determinism means the same star gets the same draw whatever order
  regions are generated in.
- **Sweep the grid before believing a new scalar** (D46), and publish
  acceptance scalars analytically rather than off the grid (D37).
- Freeman is exact only for an exponential; use `disc.disc_circular_velocity`
  and check the residual it returns (D44).
- The bar lives inside the region where S3's thick disc is already too compact
  (debt #19). If a bar makes row 5 or 9 move, say so — those rows are held by a
  cancellation and will not survive being leaned on.
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill
  in S3's merge SHA from `git rev-list -1 --grep='^Merge S3 into main'
  origin/main`. A test fails if a ☑ session has no row there.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`.
