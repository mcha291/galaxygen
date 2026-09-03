# BRIEF — Session 3: assembly & mergers

Open per RESUMING.md. Read RULES.md in full, then this. Do not read
GALAXY_PLAN.md. Consult GALAXY_INPUTS.md §11 (rulings 5, 9, 11 and the debt
register), §14 (ruling 11 in detail) and §4b when you reach them.

## Build

- `galaxy/stages/assembly.py`, checkpoint 2: the `mergers[]` event list, each
  event carrying a mass ratio, a time and a `gas_fraction` (ruling 11). Set the
  Milky Way default history with citations — this is the last UNSET input.
  Publish the accretion history and the thick disc the mergers heat into being.
- **Debt #13 is S3's headline**, not a side quest: λ_d predicts a disc scale
  length of 2.605 kpc, the star formation history builds 3.737 kpc, and
  acceptance rows 3 and 4 both fail on it. Rule out `GAS_DISC_SCALE_RATIO`
  first (it is the least defended constant in the model), then MMW98's
  structure factors f_c and f_R, which S1 folded into λ_d unmodelled (debt #6).
  One of the two routes is wrong; do not split the difference.
- Rows 5, 6, 7, 8, 9, 10, 11 need a thick/thin split. The gas is already
  extended and the stars are not, so the vertical structure is what is missing:
  `h_z = σ_z²/πGΣ` is verdict A (arithmetic) once σ_z(age) exists (§4b).
- Debt #9 is now cheap to discharge: the model has been running merger-free all
  along, so compare α-bimodality with and without `mergers[]` and record it.
  Note the simple model has instantaneous recycling and therefore no α–Fe
  separation at all — say so rather than reporting a null result as evidence.

## Gate

- f_Σ = 12% ± 4% (row 9).
- Debt #9 answered with a merger-free run beside a merger run.
- `python -m galaxy.specs` clean; every new failure is a recorded miss naming a
  debt and a prediction. Do not widen a target (B5) or tune a constant against a
  mechanism the model lacks (B10).

## Traps

- **Sweep the grid before believing any new scalar.** S2's SFR was "passing" by
  grid alignment: it wandered 1.47–1.79 with no trend while everything else
  converged to 0.1%. A hard threshold inside an integral did it (D46).
- Freeman is exact for an exponential and nothing else. Use
  `disc.disc_circular_velocity`, which decomposes onto an exponential basis;
  check the residual it returns (D44).
- Publish an acceptance scalar analytically, never interpolated off the grid.
- `spec.MISSES` entries are predictions. Row 3's says closing debt #13 closes
  it; if you close #13 and row 3 stays out, update the entry with what happened
  rather than deleting it.
- Checkpoint 2 sits between the disc and the SFH. A stage there may require
  checkpoint-1 fields only, and `graph.py` fails on an input read earlier than
  GALAXY_PLAN.md §3 puts it.
- `migration_efficiency` is kpc, not dimensionless (D45); `NET_YIELD` is an
  *effective* yield and loses its claim the moment outflows exist (D47, #16).
- Do **not** tag (rule C2e). At close add your row to `MANUAL_TODO.md` and fill
  in S2's merge SHA from `git rev-list -1 --grep='^Merge S2 into main'
  origin/main`. A test fails if a ☑ session has no row there.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`.
