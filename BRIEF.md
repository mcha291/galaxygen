# BRIEF — Session 1: Halo & disc (shared implementation)

Open per RESUMING.md. Read RULES.md in full, then this. Do not read
GALAXY_PLAN.md. Consult GALAXY_INPUTS.md §2 (Level 0 constants), §4b (three
verdicts, two remedies) and §6 (λ_d, ruling 8) when you reach them.

## Build

- `galaxy/stages/halo.py`: NFW halo from `halo_mass` (M₂₀₀) and
  `halo_assembly_z` (which also derives c₂₀₀, ruling 5): R₂₀₀, circular
  velocity v_c(R), potential on (R, z). One implementation, mapped in both models.
- `galaxy/stages/disc.py`: exponential disc from `disc_spin` λ_d and
  `baryon_retention`: scale length R_d, Σ(R), disc mass. Shared likewise.
- Delete `galaxy/stages/stub.py`. Keep one constant the two models differ on,
  read by a real stage (a legitimate second-model choice such as the c₂₀₀–z
  normalisation, or simply carry `CANARY`). `tests/test_models.py` must pass unchanged.
- Level 0 constants (H₀, Ω_m, f_b, G, R₀ …) are `Constant`s with units in both
  models, never inputs (rule A4). Cite each value in its `about`.
- Registry: set `halo_assembly_z` default with a citation; set lo/hi ranges for
  the four checkpoint-1 controls. Lower the ratchets in `tests/test_registry.py`.
- Publish scalars under the spec names as far as a one-disc model honestly can:
  `halo_virial_mass` (row 19), `v_tangential_sun` (3), `stellar_mass_total` (1),
  `thin_disc_scale_length` (4). Leave the rest not-yet-computable.
- Fields: units from `core/units.py` only; a new unit is a DECISIONS entry.

## Gate

- λ_d = 0.0144 reproduces stellar mass **and** scale length from a joint fit —
  both observables together, not either alone.
- R₂₀₀ arithmetic agrees with a cited value; delegate the literature check for
  M₂₀₀ and R_vir (a subagent returns a number and a citation).
- `python -m galaxy.specs` is clean for both models; spec rows 1, 3, 4, 19
  report pass or fail, not not-yet-computable.
- Anything fitted while a mechanism is missing goes into the debt register
  (rule B10), and `progress.py` picks the count up.

## Traps

- λ_d is the disc's spin, not the halo's; a halo-λ prior makes every galaxy
  three times too extended (GALAXY_PLAN.md §7 risk 1, ruling 8).
- The context exposes only declared names. `UndeclaredAccess` means declare
  it; optional fields via `requires_optional` and `.get()`.
- Axes order is `(R, t, z, phi)`; the potential grid is `(R, z)` with z ≥ 0.
  Grid extents (`R_max`, `z_max`) are provisional — confirm or change them in
  `core/grids.py` with a DECISIONS entry.
- Stage checkpoint is 1 for both stages; `graph.py` fails if a stage at
  checkpoint 1 reads an input the plan assigns elsewhere.
- Windows: `encoding="utf-8"` everywhere; Bash heredocs over 8 KB fail.
- Do not edit `.github/workflows/` without workflow scope on the token.
- After ticking the board run `uv run python tools/progress.py`; the suite
  asserts the board agrees with itself.
