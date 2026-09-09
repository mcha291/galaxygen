# BRIEF — for S19: the catalogue migrates, and the viewer shows the new fields (§5d; Opus)

S0–S10 are closed; S11–S18 integrated, fixed and decided (D99–D125). S18 built the merger's
radial kick, derived Kennicutt's threshold from the rotation curve, replaced the disc velocity
solver, and refitted both solar calibrations (D124). Open per RESUMING.md, read RULES.md, then
this; §11 is the register (32 open). Branch `session-19`; your decision is **D126**.

## What you build (§5d row 19; debts #31, #32)
- `systems.materialise` draws a **birth radius** around the present one with the migration
  kernel's width (`migration_efficiency` × √(age/8 Gyr), the chemistry's own rule) and looks the
  abundance up there, both models (D110); new golden values; determinism and per-region checks.
- **Gate:** the catalogue's [Fe/H] spread at R₀ equals the chemistry's `feh_spread_sun`, which
  reads **0.360** now — and note it is *narrower* than without migration (0.370): since S18 the
  migrants reaching R₀ carry narrower age–metallicity relations than the local one (D124, debt
  #28's test has the numbers). Your gate is an equality, not "wider"; assert it as measured.
- **Previews** for every field published since S15 with none: `halo_density_sun`,
  `halo_concentration_contracted` (S15); `infall_tail_surface_density`, `infall_tail_share`,
  `infall_tail_inner_radius` (S16); `bulge_stellar_mass`, `bulge_scale_radius`,
  `bulge_velocity_dispersion`, `bulge_classical_fraction`, `black_hole_mass` (S17);
  `epicyclic_frequency`, `disc_radial_spread` (R, t), `stars_formed_history` (R, t),
  `sf_threshold_surface_density` (S18). `halo_contraction` too (§5d). Ramps come from the
  declaration and nowhere else (rule A9, D1–D5); the client computes no physics.

## What is different about the model since the catalogue was last touched
1. **Where the stars are is not where they were born.** `sfh` publishes `stars_formed_history`
   — (1 − R) Ψ dt per step, moved through `disc_radial_spread`, the merger's radial kick (1.47 kpc
   rms at R₀ for stars born before 3.8 Gyr, 0.30 at 2 kpc, zero after). `stellar_surface_density`
   is its sum; the vertical stages sort it. The chemistry still reads the *birth* history
   (`sfr_surface_density_history`) and migrates abundances with its own kernel. A catalogue that
   draws present radius from `stellar_surface_density` and birth radius by the migration kernel
   is consistent with the chemistry; whether the kick should also enter the birth-radius draw
   for pre-merger stars is your call — say which, and why, in D126.
2. The threshold is Kennicutt's and diverges at the centre: 589 M☉/pc² at the first cell, so the
   innermost rings hold gas (276 M☉/pc²) and form almost no stars; the advanced centre's [Fe/H]
   peaks at 0.5 kpc (0.70) not at the first ring. Any catalogue check on the inner disc reads that.
3. `NET_YIELD` 0.01376 and `WIND_SPEED` 860.3 (refit at S18, debt #43); the disc velocity solver
   is basis-free (`disc.disc_circular_velocity`, one call per profile, 40 ms); the execution order
   puts `disc` before `assembly`. Row 3 is green at 250.96 by 0.04 — do not read it as evidence.

## Traps
- **Every pin that reads the catalogue moves with new golden values**: test_systems, test_planets,
  test_determinism, test_api's object routes. Re-pin with the old number beside (D124 lists S18's).
- **Write files with `newline="\n"`.** A Python `open(p, "w")` on this machine writes CRLF; git
  normalises on commit but `tools/progress.py`'s line regexes fail on the working copy, and
  `test_progress` with them. Normalise before running the board.
- The full suite outlasts the Bash tool's cap: run it in the background with `EXIT=$?` appended
  to its log and gate the merge on **that line**, not the tool's notice. Scratch scripts
  `s19_<what>.py`; `uv run python` only. **Do not merge or delete `session-10-beta`,
  `session-10-gamma`, `session-10-gamme-run-2`.**
- Not yours: the heating constants (#42: `MERGER_HEATING` = 60 reads rows 7 and advanced 6
  inside together — S20's first probe), the first infall's timescale (#49, S20 with the valley,
  which the derived threshold reopens at τ₀ = 1 for n = 2–3), the inner gas reservoir (#47, #21).
