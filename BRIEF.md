# BRIEF — for S20: the advanced model's [α/Fe] valley, and rows 6–7 (§5d; Fable)

S0–S10 are closed; S11–S19 integrated, fixed and decided (D99–D127). S19 made the catalogue
migrate and left the physics untouched: **no acceptance row moved**, and none reads the
catalogue. Open per RESUMING.md, read RULES.md, then this; §11 is the register (32 open).
Branch `session-20`; your decision is **D128**.

## What you build (§5d row 20; debts #27, #42, #26, and #49 which S18 handed you)
- **The mechanism that makes the inner disc fast without steepening the infall law
  everywhere.** The bulge's inflow is §5d's named candidate; #49's is the first infall on its
  own short timescale (τ₀ ≈ 0.8–1 Gyr, radius-independent, the halo/thick-disc phase), which
  S18 probed and which the derived threshold reopens. They are not the same lever — decide
  which the model *derives* and say why in D128.
- Then rows 5–11 and 24 in the advanced model, and **rows 6 and 7 judged together with both
  heating constants re-examined** (#42: `MERGER_HEATING` = 60 reads row 7 at 751 and advanced
  row 6 at 346, both inside, for the first time — S18 left it alone because the plan gives it
  to you, rule B10 cutting both ways).
- **Gate:** row 24 `bimodal_wide` at the default grid, *stated* (the N_t = 8 trap — a coarse
  grid manufactures the valley, which is why this row has a known false positive); row 22
  still inside; rows 6 and 7 inside together.

## What is different since the valley was last looked at
1. **The advanced model has no thick disc at all**, and since S19 that fact is visible rather
   than masked. `alpha_split` is NaN, so `vertical_alpha`'s mask selects nothing and
   `birth_population` — the criterion, now published by the stage that owns it — is all-thin.
   The catalogue reads it instead of rebuilding it, so when your valley opens, the thick disc
   appears in the viewer, in `star_population`, and in the planets, with no further work. Six
   thick-disc rows plus row 24 have this one cause (#27).
2. **The threshold is Kennicutt's and diverges at the centre** (S18, #47): 589 M☉/pc² at the
   first cell, so the innermost rings hold gas and form almost no stars, and the advanced
   centre's [Fe/H] peaks at 0.5 kpc (0.70) not at the first ring. The same reservoir halves
   the centre's iron (#26) and is what reopened the valley at a fast inner disc.
3. **The chemistry owns the migration kernel now** (S19, A9): `transport`,
   `transport_columns`, `migration_width` and `age_bin_edges` live in `chemistry.py` and are
   read by `chemistry_dtd` *and* by `systems`. Change the kernel and the catalogue follows;
   change the age binning and it follows too. That is deliberate — do not fork it.

## Traps
- **The catalogue is the costliest stage** (0.68 s of a 1.4 s run) and its cost is fixed per
  cell, not per star (D24, D127). If you touch `materialise` or `Churn`, read the profile
  after: a per-star cost hides inside a per-cell design and every correctness test still passes.
- **Nothing in `materialise` may depend on which cells were asked for.** Narrowing the churn
  to a region's own rings changed the last bit of a star's age, because BLAS sums a 1-column
  product differently than a 32-column one. Per-region determinism is the contract (D60, D126).
- **Write files with `newline="\n"`.** A Python `open(p, "w")` on this machine writes CRLF;
  git normalises on commit but `tools/progress.py`'s line regexes fail on the working copy.
  The full suite outlasts the Bash tool's cap: background it with `EXIT=$?` appended to its
  log and gate the merge on **that line**. Scratch scripts `s20_<what>.py`, deleted before the
  close asserts `git ls-files --others` is empty. **Do not merge or delete `session-10-beta`,
  `session-10-gamma`, `session-10-gamme-run-2`.**
- Not yours: **#50**, opened by S19 — the model transports stars twice, the merger's kick in
  `sfh` and the churn in `chemistry`, and nothing reconciles them, so the catalogue's thick
  fraction at R₀ (0.221) is not `thick_thin_surface_density_ratio` (0.051) and the two bracket
  row 9's observed 0.08–0.16 from either side. It moves five acceptance rows and is explicitly
  **for S21 to read and S22 to rule**. Also not yours: the inner gas reservoir's cause, which
  is the bar (#47, #21).
