# BRIEF — Session 2: star formation & chemistry (simple)

Open per RESUMING.md. Read RULES.md in full, then this. Do not read
GALAXY_PLAN.md. Consult GALAXY_INPUTS.md §3 (inputs 4, 5, 7), §4b (three
verdicts, two remedies) and §7 (rows 2, 20–23) when you reach them.

## Build

- `galaxy/stages/gas.py`: the gas phase, at checkpoint 3. Two-infall accretion
  from `infall_timescale` τ₀ with τ(R) = τ₀(R/R_d)ⁿ, Kennicutt–Schmidt star
  formation, instantaneous recycling. Publish `gas_mass_30kpc` (row 20),
  `gas_h2_fraction` (21), `sfr` (2). One implementation, both models.
- `galaxy/stages/chemistry.py`: single-element [Fe/H](R, t) with a migration
  kernel from `migration_efficiency`. Publish `metallicity_gradient` (row 22)
  and operationalise row 23 — define its scalars and age bins and fill
  `field`/`lo`/`hi` in `spec.py`, which S1 left as `None`.
- **`stellar_mass_total` becomes stars only.** S1 publishes the whole baryon
  budget under that name; split it and re-examine `baryon_retention` in the
  same commit (rule B10, debt #11). `baryon_mass_total` stays the budget.
- Registry: set defaults for `inside_out_index` and `migration_efficiency` with
  citations, and lo/hi for all three checkpoint-3 controls. Lower both ratchets
  in `tests/test_registry.py` (unset ≤ 1, controls without a range ≤ 0).
- Confirm `t_max = 13.8 Gyr` and the time convention (t = 0 at the Big Bang) in
  `core/grids.py`, with a DECISIONS entry. `n_t = 2000` is untouched.

## Gate

- Gradient ≈ −0.06 dex/kpc (row 22, interval [−0.069, −0.049]); SFR ≈ 1.65 M☉/yr
  (row 2). Both pointwise.
- **Debt #11 is S2's to close or kill.** S1 predicts that giving the gas its own
  shallower profile drops v_tan(R₀) from 256.1 to ≈ 246.4 km/s, inside row 3.
  If row 3 still misses, the recorded explanation is wrong: say so, remove the
  `spec.MISSES` entry and record the real cause (rule B5). Do not tune λ_d or
  `baryon_retention` to close it.
- `python -m galaxy.specs` clean for both models; rows 2, 20, 21, 22 report
  pass or fail, not not-yet-computable, and row 3 resolves one way or the other.
- Anything fitted while a mechanism is missing goes in the debt register.

## Traps

- Row 20 and row 21 are **zero-width** targets: the sources quote no
  uncertainty, so a pointwise check fails for any float that is not exactly
  equal. Find the uncertainty in the source or record the miss in
  `spec.MISSES` with a debt (rule B5). Do not widen the interval.
- A row that fails still reports `fail`; only an entry in `spec.MISSES` keeps
  the run's exit status clean, and a recorded miss that starts passing is an
  error. Read the top of `galaxy/specs/spec.py` before touching it.
- Publish anything an acceptance row reads as an **analytic scalar**, never
  interpolated off the grid, or the S10 sweep will move it (D37).
- `disc_spin` is 0.0173, not ruling 8's 0.0144 (D30, debt #10). If a re-ruling
  has come back the other way, changing the default is one number plus
  `tests/test_registry.py::test_defaults_are_the_milky_way`.
- Checkpoint order: a stage at checkpoint 3 may require checkpoint-1 fields but
  not the reverse, and `graph.py` fails on an input read earlier than
  GALAXY_PLAN.md §3 puts it. `mergers` is S3's, not yours.
- Axes order is `(R, t, z, phi)`; chemistry fields are `(R, t)`.
- Windows: `encoding="utf-8"` everywhere; Bash heredocs over 8 KB fail.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`; the suite
  asserts the board agrees with itself.
