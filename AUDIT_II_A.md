# Audit II, aim (a) — every prediction since S13, killed or held with a number

S21, branch `session-21-a`, **Fable 5.1**, desktop, 2026-09-11. The paired run (aim (b), Opus,
`session-21-b`) is not read here and this branch is never merged into it; S22 ports both lists
onto `main` (D99, GALAXY_PLAN.md §5d). Reserved numbers: debts **#51–#64**, decisions **D130–D143**;
this run opens #51 and #52 and writes D130 and D131. Every probe substitutes one function with
the repo unchanged (D114); `tests/test_audit_ii_a.py` pins every number below and says the
precision it checked at. Finding numbers A-n are cited by D130 and by the register.

## 0. What this run knew, and how it read

All of `main` at 7e96422 (S20's merge): the register, `spec._MISSES` / `_MISSES_ADVANCED`,
D113–D129, S20's three probe tests. The rule applied to each prediction (B4): the knob it names
is moved to the value it names, the row it names is read, and the verdict is the row's own
window. Where a prediction carried a pre-committed reading for its failure, that reading is
quoted and applied, not re-argued (LESSONS, S20). A prediction that could not be run with the
repo unchanged is listed in §4 with the reason.

## 1. The verdicts

| # | Prediction (where) | Run as | Read | Verdict |
|---|---|---|---|---|
| 1 | **#50** (S19, D126): stars moved through both kernels land row 9 between 0.0455 and 0.221; rows 5, 8, 11 move with it | `sfh.radial_transport` = the built kick, then the chemistry's own kernel per age bin (`transport(R, migration_width(age))`), mass-conserving | row 9 **0.2655**, row 5 2.73, row 8 0.092, row 11 unmoved, **row 4 3.49, row 3 244.9**; the churn alone reads the same to 0.002 | **killed** — above the bracket, and the bracket was a fraction read as a ratio (A-1); the churn on the mass fails rows 3 and 4 (A-2) |
| 2 | **D121** (S17; row 3 and row 12 entries): 7e9 buckled into the spheroid at the derived scale radius reads row 3 at 249.4, row 12 inside, row 14 at 123 | `halo.angular_momentum_core` returns the derived mass + 7e9 at the derived half-mass radius; the halo contracts around it, σ recomputed, `sfh` takes the share | row 3 **249.64** (in), row 12 1.47e10 (in), row 13 0.31 (in), **row 14 144.4** | row 3 **held** to 0.2 km/s; row 14 **killed** by 21 km/s (A-3) |
| 3 | row 12's conditional: a bar-built component less concentrated keeps row 14 inside | 1.4e10 total at 1.5 / 2 / 3 / 4 × the half-mass radius | row 14 129.0 / 123.8 / 121.2 / 121.5; row 3 249.1 / 248.4 / 247.1 / 245.9 | **killed**: no concentration lands rows 12 and 14 together; row 14's floor is ~121 (A-3) |
| 4 | row 14's isotropy branch: subtracting the rotation the model computes takes the row below 113 | v_rot = ⟨j⟩/r_half = 0.829 × v_c(0.88 kpc) = 160 km/s | √(σ² − v_rot²/3) = **70**; √(σ² − v_rot²) = 0 | **held**, by 43 km/s, not by a few (A-12) |
| 5 | **D128 claim 1**: every `bimodal_wide` is the +0.45 plateau spike | the single-merger cases of #27 (n = 3 at τ₀ = 7 with GE alone at 0.2; n = 3 at τ₀ = 1 with GE alone at 0.5 and with the default list), the R₀ histogram decomposed as `chemistry_dtd` builds it | above +0.40: 0.109–0.112, of which +0.42–0.46 holds 0.086–0.088; no bin in +0.24–0.40 above 0.05; splits 0.39–0.41 | **held** (A-4) |
| 6 | **D128 claim 2**: no accretion law under a constant-efficiency Kennicutt law makes a thick mode | the first infall at 0.1 and 0.3 Gyr everywhere | `bimodal_wide` at dip 0.78 / 0.52, split 0.21; the +0.42–0.46 spike 0.114 / 0.074, the plain's largest bin 0.026 / 0.029 | **held**: the strongest accretion law reads the spike valley (A-4) |
| 7 | **D128 claim 2, the mechanism named**: a rising first phase cut within ~1 Gyr opens the valley | `sfh.star_formation_rate` × 5 in a window then zero after it, on the fast first infall (0.55 Gyr) | burst **1.0–2.0 Gyr, cut 2.0–3.0**: `bimodal_wide`, split 0.21, dip 0.93, **a mode at +0.35 holding 0.103 of the mass in one 0.02 dex bin**, the spike 0.051, the advanced row 6 353 (in); burst 0–0.8, cut to 1.5: the stars form at the plateau (spike 0.123, plain's largest bin 0.024) | **held, with the timing corrected**: the burst must sit after the first Ia iron (1–2 Gyr), not in the first gigayear (A-4) |
| 8 | rows 5 / 9 / 11 (S18, #19, #49): they land together only when most of the early gas is still gas at the merger — a burst and a cut | star formation off from 1.0 to 3.8 Gyr on the fast first infall | rows **8, 9, 10, 11 inside together** (0.040, 0.115, 3.36e10, 6.72e9), row 5 **1.61**, row 7 1095, row 2 1.27 | **half held**: the cancellation is broken, row 5 is 0.2 short; #19's own reading applies — the split criterion (A-5) |
| 9 | **#49** (S18): the first infall on its own timescale lands row 5 at any share with rows 9 and 11 moving together | S20's test, re-run in the suite | 1.95 / 0.56 / 1.67e10 at the default share; 1.26 / 0.04 / 4.8e9 at 0.8 | **killed at S20**, confirmed |
| 10 | **#48** (S17): whatever the residual's width, row 18's median does not move | `BLACK_HOLE_SCATTER` 0.28 / 0.5 / 0.8, the spec's own 41-seed ensemble | median 1.97e7 / 1.47e7 / **9.9e6**; the 41 standardised residuals' median **−0.577σ** (2.9 standard errors of a 41-sample median); seeds 41–81: −0.10σ | verdict **held**, the claim it rested on **killed**: the median is not the mean relation; the pre-committed reading (n too small) applies (A-6, **#51**) |
| 11 | advanced row 22 (S18, #47): the inner gas is the prediction; cleared, if the row still reads below −0.069 the wind's tilt is what is wrong | `sfh.toomre_threshold` capped at 5 M☉/pc² inside 4 kpc (gas there 1.53e9 → 4.0e8) | row 22 **−0.0699**, unmoved; capped at the R₀ value everywhere inside: **−0.0794**; the constant 5 everywhere: −0.0633 | **killed** on its mechanism: the row is fitted over 4–12 kpc and the reservoir is inside 4; its pre-committed reading applies (A-7) |
| 12 | **#46** (S15, revised): if row 3 does not close with the bulge and the tail, sweep w at A = 1.6 against rows 3, 19 and v_esc together | `CONTRACTION_A` 1.6, `CONTRACTION_W` 0.6 / 0.8 / 1.0 / 1.3 | row 3 230.3 / 237.8 / 249.3 / 267.8; v_esc(R₀) 544 / 550 / 559 / 577; row 19 1.1e12 at every w | the test **cannot discriminate** (A-8): row 19 is the input, v_esc stays inside 530–580; A = 1.6 at w = 0.8 reads 237.8 now, not S15's 245.6 |
| 13 | row 12's entry: across μ = 1.06–1.40 the spheroid runs 1.46e10 down to 5.6e9 | `ANGULAR_MOMENTUM_MU` 1.06 / 1.15 / 1.25 / 1.4 | 1.46e10 / 1.02e10 / 7.71e9 / 5.6e9; at 1.06 row 3 249.4, row 13 0.317, **row 2 1.14, row 14 145.6**, row 20 7.53e9 | **held**; μ lands rows 3, 12, 13 and loses 2, 14, 20 (A-9) |
| 14 | row 20's entry: μ across its range is worth ±1e9; if the row lands at the median with the reservoir still there, the reservoir is being counted as the outer HI | the same sweep, hydrogen outside 4 kpc read beside the total | 7.53 / 8.80 / 8.09 / 7.06e9; outside 4 kpc 6.42 / 7.69 / 6.97 / 5.94e9 | **held** (+0.7 / −1.0e9, non-monotone); the reservoir is 1.1e9 of the 8.09e9 at every μ, so the entry's own reading stands (A-13) |
| 15 | advanced row 23 (#28): a kernel width of 2.5 kpc at 8 Gyr reads −0.039 with young/old 1.6 | `migration_efficiency` 2.5 and 2.0 | 2.5: **−0.048** (inside), young/old **1.22**; 2.0: −0.073, 0.81; row 22 unmoved at −0.0698 | verdict **held**, the ratio moved to the wrong side of 1.75 (A-10) |
| 16 | advanced row 6 (#42, S20): `MERGER_HEATING` would have to fall below 78 to land it alone | 78 / 75 / 70 | 351.4 / 350.3 / 348.7 | direction held, the number is **74** (A-11) |
| 17 | **#44** (S18): row 2 cannot see `KS_NORM` | ±1σ | 1.764 / 1.755 / 1.755 | **held** |
| 18 | row 15 = `BAR_LENGTH_RATIO` × R_d (#21) | the baseline | 2.0 × 2.441 = 4.883, 0.08 above the floor | **held**; a 2% fall in R_d fails it |
| 19 | D121: 1.4e10 in the spheroid is worth 3.7 km/s on row 3 | +6.3e9 at the derived radius | 249.78, i.e. −1.25 | direction held; the number is a third of D121's on the S18–S20 potential |
| 20 | **#45** (S16): the tail is not the ratio's second value; row 22 holds or moves toward −0.047 | pinned at S16–S18 | −0.059 → −0.0698; no setting of the ratio reads the row | held at S16, superseded at S18; not re-run |
| 21 | the statistical rows are the sample's (from A-6) | rows 16 and 17 on seeds 41–81 | 41.1 / 5.94 against 42.8 / 5.70 | verdicts hold on the second diagonal |
| 22 | D128 / #42: `MERGER_HEATING` 88.8 is the cited σ_W = 35 net of 27.06 | the source read (a read-only agent, the publisher's PDF via Lund University's repository), then the constant at the measured value | Bensby+03 Table 1's 35 is an adopted characteristic value with no uncertainty; the measurement it quotes is Soubiran+03's **39 ± 4**; at 39 the constant is 112.3 and row 7 reads **1193** (out), row 3 **250.97** (in); the window's edge is σ_W = 37.1 | row 7's green is the choice of the round number (A-14) |

## 2. The findings, numbered for D130 and the register

- **A-1 (record).** Debt #50's bracket compared a fraction with a ratio. "The catalogue's thick
  fraction at R₀ is 0.221 where `thick_thin_surface_density_ratio` says 0.051" reads a share of
  the catalogue against a thick/thin ratio; 0.221 as a ratio is 0.284, and the double transport
  reads 0.2655 on the grid — inside the bracket as it should have been written, above it as
  written, and outside row 9's window either way.
- **A-2 (physics).** The two transports cannot be reconciled by composing them. The chemistry's
  kernel applied to the mass carries the disc's stars outward until the thin disc's scale
  length reads 3.49 kpc (row 4, out of 2.1–3.1) and the Sun's tangential velocity 244.9 (row 3,
  out low): the width `chemistry_dtd` and the catalogue use is ruled out by the disc's structure
  the moment the mass follows it, which is debt #28 ("migration is too strong") read off rows 3
  and 4 instead of row 23. The kick is nothing beside it (0.002 on row 9). At half the width
  rows 3, 4, 8 and 9 are inside together (250.4, 2.86, 0.043, 0.128) and rows 5 and 11 are not;
  at the full width and a merger share of 0.7, rows 9 and 11 are inside together for the first
  time in the project (0.113, 4.9e9) with row 5 at 2.56 — the cancellation debt #19 recorded, run
  the other way. The register's pre-committed reading ("if row 9 still cannot be reached from
  inside that interval, the split criterion is what is wrong") does not fire: row 9 is reachable;
  what is not reachable is rows 3 and 4 with it.
- **A-3 (physics).** The bar's prediction held on row 3 and died on row 14. 7e9 at the derived
  scale radius reads row 3 at 249.64 against D121's 249.4 and rows 12 and 13 inside — and row
  14 at 144.4, not 123. D121's 123 was read on S17's potential; the derived probe contracts the
  halo around the added mass and recomputes the Jeans dispersion in that potential. Less
  concentrated does not help: at four times the derived half-mass radius (a = 1.46 kpc) row 14
  reads 121.5 and row 3 245.9, so **no concentration lands rows 12 and 14 together**, and the
  conditional the row 12 entry pre-committed to ("built at a scale radius that keeps row 14
  inside and row 12 still misses") cannot be reached from either side. The advanced model pays
  twice more: its row 6 356 → 400 and its row 22 −0.0698 → −0.081, neither in D121's list.
- **A-4 (physics).** D128's two claims held, and the mechanism it named works at a time it did
  not name. Every valley the detector reports is the plateau spike — the single-merger cases,
  and the strongest accretion law (all the early gas in 0.1 Gyr: dip 0.78, split 0.21, the spike
  0.114 of the mass, the plain's largest bin 0.026). A burst of star formation (× 5) placed
  **inside the α-fall, 1–2 Gyr**, on the fast first infall and cut 2–3 Gyr, makes an α-rich mode
  at +0.35 holding a tenth of the mass in one 0.02 dex bin — twice the spike, the first mode
  short of the plateau the model has ever produced — with the advanced row 6 at 353, inside.
  The same burst in the first 0.8 Gyr forms its stars before any Ia iron and makes nothing
  (spike 0.123, plain's largest bin 0.024). So D128's "rising first phase cut within a gigayear"
  is right about the shape and wrong about the clock: the burst has to run after the first Ia
  iron has arrived and while the gas is still rich, which on this DTD (minimum delay 0.15 Gyr)
  is 1–2 Gyr after the infall begins. Nothing in the repo makes one; the cost in the simple
  model is #49's trade unchanged (row 5 2.01, row 9 0.60, row 11 1.7e10, row 2 1.27).
- **A-5 (physics).** Rows 5, 9 and 11's prediction, run: with the early gas left as gas at the
  merger (star formation off 1.0–3.8 Gyr on the fast first infall) rows 8, 9, 10 and 11 are
  inside together for the first time (0.040, 0.115, 3.36e10, 6.72e9) and row 5 reads 1.61, 0.2
  short of its window; row 7 1095, row 2 1.27. The pre-merger disc is extended enough only where
  the first gigayear's stars formed, which is inside the threshold's reach on a 0.55 Gyr infall.
  Debt #19's sentence — "if they still cannot be satisfied together at the right scale length
  once the early infall is fast, the split criterion is what is wrong" — is now the reading, by
  0.2 kpc, and S22 rules on it.
- **A-6 (instrument).** The spec judges every statistical row on one fixed sample — seeds 0–40,
  every seed name equal — and that sample's standardised residual for `world_seed`'s
  black-hole draw has median −0.577σ, 2.9 standard errors of a 41-sample median from zero
  (mean −0.33, sd 1.29). Row 18's median therefore reads 0.16 dex below the mean relation at
  the classical width and 0.46 dex below at 0.8 dex, and moves with the width (1.97e7 → 9.9e6)
  while its verdict does not; the next diagonal (41–81) reads −0.10σ and 2.68e7. Debt #48's
  claim that "the median is the mean relation at any width" is false by exactly the mechanism
  its own pre-committed reading named. Rows 16 and 17 hold on the second diagonal (41.1 / 5.94).
  Opened as **debt #51**: `ENSEMBLE_MIN` = 41 was derived for the interval's coverage (D109), not
  for the median's precision (0.2σ at n = 41), and the diagonal is one draw, not a sample.
- **A-7 (record + physics).** The advanced row 22 miss names the gas inside 4 kpc and the row
  does not see it: the gradient is fitted over 4–12 kpc (`GRADIENT_FIT_RANGE`), and emptying the
  reservoir to 4.0e8 leaves the row at −0.0699. What the derived threshold did to the row is
  the gas it holds in the fit window itself — 22.8 M☉/pc² at 4 kpc and 6.1 at 12 against the
  constant threshold's 10.2 and 4.7 — with `WIND_SPEED` refitted to keep R₀ solar: the outer
  window is more dilute and the gradient steeper. Capping the threshold at its R₀ value inside
  R₀ steepens it further (−0.0794). By the entry's own reading the wind's tilt (#26) is what is
  wrong, and the bar (#21) is not the lever for this row.
- **A-8 (record).** Debt #46's pre-committed test has two judges that cannot judge: row 19 is
  `halo_mass`, the input, and moves under nothing; v_esc(R₀) runs 544–577 across w = 0.6–1.3 at
  A = 1.6, inside 530–580 throughout. Only row 3 is left, and it crosses its window between
  w = 0.8 (237.8) and 1.0 (249.3): a one-row sweep is a fit (rule B5). S15's "A = 1.6 at w = 0.8
  reads 245.6" is stale by 8 km/s — the tail and the spheroid have arrived since.
- **A-9 (record).** The spheroid's constant does what its entry says: μ = 1.06 lands rows 3
  (249.4), 12 (1.46e10) and 13 (0.317) and loses rows 2 (1.14), 14 (145.6) and 20 (7.53e9). It is
  not a lever — it is the profile's cited median — but a session that moved it would land three
  rows, and the entry now carries what it costs.
- **A-10 (physics).** The kernel width that lands the advanced row 23 (2.5 kpc: −0.048) puts the
  young/old ratio at 1.22, under the observed 1.75, and 2.0 kpc inverts it (0.81). The row can be
  landed; the ratio cannot be landed with it. Debt #28's second explanation — the old stars'
  starting gradient is too steep — is the one this convicts, because a narrower kernel flattens
  less and the old population is then steeper than the young one wants.
- **A-11 (record).** The advanced row 6 lands at `MERGER_HEATING` ≈ 74 (350.3 at 75, 348.7 at 70),
  not "below 78".
- **A-12 (physics).** Row 14's near-miss is two large errors of opposite sign. The model's own
  V/σ says the spheroid is 83% rotation-supported (v_rot = ⟨j⟩/r_half = 160 km/s at 0.88 kpc); the
  isotropic Jeans reading counts that as dispersion, and subtracting it leaves 70 km/s. The
  missing bar mass adds 28 at the derived concentration and 5 at four times the radius. 116.2
  against 113 is therefore not evidence that the spheroid's kinematics are right, and rows 12
  and 14 cannot be landed together by mass alone (A-3). Opened as **debt #52** with the
  prediction that the buckled 7e9 and a V/σ-aware dispersion together read near 113.
- **A-13 (record).** Row 20's entry already concedes its number is partly the reservoir; the μ
  sweep shows the hydrogen outside 4 kpc never reaches the target's ~7.7e9 (7.69e9 at μ = 1.15
  is the most), so the concession holds at every μ.
- **A-14 (record + calibration, rule B10).** `MERGER_HEATING`'s citation was read. Bensby,
  Feltzing & Lundström 2003 give σ_W = 35 km/s for the thick disc in their Table 1 as one of the
  "characteristic velocity dispersions … used in Eq. (1)" — an adopted round value for their
  kinematic selection function, with no uncertainty — and in their Sect. 1 quote the measurement
  it stands in for: Soubiran, Bienaymé & Siebert 2003, (σ_U, σ_V, σ_W) = (63 ± 6, 39 ± 4, 39 ± 4)
  `[verified: Bensby et al. 2003, A&A 410, 527, Table 1 and Sect. 1, and Soubiran et al. 2003,
  A&A 398, 141, abstract — both read in full at S21 (a) by a read-only agent from the
  publisher-identical PDFs; the Bensby paper has no arXiv copy]`. Net of the model's 27.06 km/s
  the measured 39 gives a constant of 112.3, which reads row 7 at 1193 (out) and row 3 at
  250.97 (in); the window's top edge is σ_W = 37.1 (101.5). So row 7 is green on the choice of
  the round number at the −1σ edge of the measurement, and rows 3 and 7 trade across the
  source's own error bar. Not a re-fit — S20's derivation is the right shape — but the record
  said "a citation instead of a sentence" and the citation is a selection-function constant;
  written into debt #42 and the row 7 note in `spec.py` for S22.

## 3. The green rows: what each is green on (AUDIT_RUN2 §5, re-read at S21)

| row | model | green on | verdict |
|---|---|---|---|
| 1 | both | 4.75e10 = disc + spheroid, with row 11 3.6e9 high and row 12 6.3e9 low; at their targets it reads ~4.5e10, still inside | conditioned on two misses of opposite sign, but would survive their repair |
| 2 | both | the infall and the derived threshold; blind to `KS_NORM` (A-14); μ moves it 1.14–1.82 across its 90% range, the merger share 1.27–2.15 | conditioned on μ = 1.25 and the default share |
| 4 | both | `disc_spin` derived to 2.6; 2.44 read; the chemistry's kernel on the mass would read 3.49 (A-2) | green because the mass does not follow the churn |
| 6 | simple | `SECULAR_HEATING` 25, bracketed by 20 (228) and 30 (451), both out; 328 in 250–350 | the constant, inside a window narrower than its own step |
| 7 | simple | `MERGER_HEATING` 88.8 derived from a cited 35 km/s net of 27.06; Σ(R₀) unmoved at 47.3 while rows 5, 9, 11 miss; the 35 is an adopted round value and the measurement behind it is 39 ± 4, at which the row reads 1193 (A-14) | the constant's derivation from the round number; out on the measured one |
| 10 | simple | row 1 − row 11 − row 12 at 3.02e10; at rows 11 and 12's targets 2.65e10, 0.15e10 above the floor | inside either way, by a margin of a tenth |
| 10 | advanced | thin = every star (3.98e10) on #27 | the cancellation |
| 15 | both | `BAR_LENGTH_RATIO` 2.0 × 2.441 = 4.88, 0.08 above the floor | chosen; a 2% fall in R_d fails it |
| 16, 17 | both | downstream of 15, judged on the median of one fixed 41-seed sample (A-6); the second diagonal reads 41.1 / 5.94 | chosen upstream; the sample does not decide these two |
| 19 | both | the input | not a check |

No green row is an unconditioned prediction; row 2 is the nearest and it is a prediction of two
constants' defaults.

## 4. Not run, and why

- Row 18's M_•–M_bulge on the classical share (5.2e6): no such relation is in the repo, and
  entering one to read it is the tuning the entry exists to catch (rule B5).
- #26's mass-loaded wind and #21's drain: S20 ran them and ruled them for S22; nothing here adds
  to their numbers.
- #42's "when the valley opens, the advanced row 6 falls toward the simple model's": the one
  probe that opens a real mode (A-4) reads it at 353, inside — recorded in the row's entry,
  not a verdict on a mechanism the model does not have.
- The catalogue under the double transport: no acceptance row reads the catalogue (D126), and
  the grid's ratio (0.2655) against the catalogue's (0.284) is the same number to 7%.

## 5. What S22 ports from this branch

`tests/test_audit_ii_a.py` verbatim; this file; the register's #51 and #52 and its amendments to
#11, #19, #27, #28, #42, #46, #47, #48, #49, #50; the replaced predictions in `spec._MISSES` and
`_MISSES_ADVANCED` (rows 3, 5, 9, 11, 12, 14, 20; the advanced 6, 22, 23 and `_NO_VALLEY_PREDICTION`);
D130 and D131; the S21 (a) lessons. The scratch scripts were deleted (the tests are the probes).
