# BRIEF — Session 5: systems (the star catalogue, headless)

Open per RESUMING.md. Read RULES.md in full, then this. Do not read
GALAXY_PLAN.md. Consult GALAXY_INPUTS.md §9 (depth of materialisation) and §12
when you reach them.

## Build

- `galaxy/stages/systems.py`, checkpoint 5, reading `systems_seed`. Seeded like
  S4's `pattern` — read D55 first: provenance is per *stage*, so anything
  reproducible-without-a-seed belongs in a separate derived stage.
- A star catalogue drawn from the fields the model already publishes: positions
  from the stellar surface density and the scale heights, ages and [Fe/H] from
  the histories, kinematics from `disc_heating`. **Do not sample what you can
  count** (rule B8) — the density field is known, so draw positions from it
  rather than rejection-sampling a guess.
- **Per-region determinism is the gate, and it is a property of the seed
  derivation rather than of the loop.** `hash(systems_seed, star_id)` must give
  the same star whatever order regions are generated in and whatever else has
  been generated; `galaxy/specs/determinism.py::check_region` already tests the
  primitive, so build on `ctx.rng(seed, *path)` and never on iteration state.
- 10⁶ stars in under 10 s. Measure it cold (rule B2) and publish the number.

## Gate

- 10⁶ stars < 10 s, measured and published.
- Per-region determinism: the same region generated twice, and generated after
  different neighbours, is identical.
- `python -m galaxy.specs` clean; new failures are recorded misses with a debt
  and a prediction.

## Traps

- **Read D51 before trusting row 9.** It passes because two errors cancel.
- A catalogue is `column` kind with `of="star"`, not `field`; every column of one
  object class must share a length, and the runner checks it.
- Seeded fields declare `provenance="seeded"`; `graph.py` derives the truth and
  fails on a mismatch either way.
- **Sweep the grid before believing a new scalar** (D46); publish acceptance
  scalars analytically (D37). A catalogue statistic is not exempt: if it moves
  with N_R it is measuring the grid.
- The materialised sample is drawn per region and never stored (GALAXY_PLAN.md
  §4). Do not accumulate a global list you then index into — that is the
  order-dependence the gate exists to catch.
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill
  in S4's merge SHA from `git rev-list -1 --grep='^Merge S4 into main'
  origin/main`. A test fails if a ☑ session has no row there.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`.
