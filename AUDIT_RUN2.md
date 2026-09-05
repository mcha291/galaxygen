# AUDIT_RUN2 — Session 10, run 2: the second independent audit

The second of two independent audits of the finished model (D96's protocol, by
its heading). This file was written and committed **before** `AUDIT_RUN1.md` or
DECISIONS.md D96 were opened; the diff between the two lists is D97. Every
number below was produced in this run, on `session-10` at `d57f274`, on the
machine named in RESUMING.md, 2026-09-05. Instrument output is quoted from the
runs in §1; probes are the scripts described beside their numbers.

## 0. What this run knew before it started (independence, stated)

Rule B3: a second list is only a second list if it was not steered by the first.
What leaked, so the diff in D97 can discount it:

- The register (GALAXY_INPUTS.md §11), which run 1 amended: debt #17's paragraph
  says the sweep reports row 20 as untestable; debt #21's says run 1 found row 15
  passes on `BAR_LENGTH_RATIO`; debt #24's says run 1 measured the per-cell
  catalogue cost `[verified: GALAXY_INPUTS.md §11, debts 17, 21, 24]`.
- LESSONS.md's five S10 (run 1) lessons, one of which names D96's finding that the
  advanced model's iron-rich centre moved giant occurrence 7× at 2 kpc
  `[verified: LESSONS.md "From S10 (run 1)"]`.
- D96's *heading* ("one defect, four flags, and the protocol for run 2"), seen in
  a grep of DECISIONS.md headings while locating D94 and D95. Its body was not read.
- D94 and D95 in full, which BRIEF.md permits.

Everything in §2–§7 that overlaps those items is marked **(known)**. Everything
else was reached from the code, the register, the instruments and the probes.

## 1. The instruments, run here

### 1.1 `uv run python -m galaxy.specs` (full sweep), exit 0

graph: both models acyclic, orders as `tests/test_graph.py::ORDER`. preflight OK
(0 UNSET, 0 controls without a range). determinism OK. spec: **simple 11 pass, 7
fail, 6 not-yet-computable; advanced 8 pass, 11 fail, 5 not-yet-computable**;
every failure a recorded miss for its model `[verified: the run's spec section]`.
Values, to spot a regression by: M★ 5.27619e10, SFR 1.96876, v_tan 256.004, R_d
2.49018, simple thick R 1.17317 / h 1039.32 / M 1.073e10 / row 9 0.10299 / row
8 0.0250762, row 15 4.98037, row 20 5.79503e9, simple gradient −0.0236683 and
old −0.00668545; advanced row 6 326.166, gradient −0.0565751, old −0.0192657,
row 24 `single`. Rows 16/17 (n=20): Ω central 95% [32.8, 51.9], R_CR [4.50, 7.45].

### 1.2 convergence (same run)

simple: 45 ok, 0 drift, 3 untestable, 6 statistical; advanced: 48 ok, 0 drift, 3
untestable, 6 statistical. Largest movements, as (drift / target width):

| axis | row | values at the three grids | drift / width |
|---|---|---|---|
| n_R 200/400/800 | 3 v_tan | 256.068, 256.004, 255.959 | 0.065 / 6 |
| n_R | 6 h_thin (adv) | 327.06, 326.17, 326.76 | 0.89 / 100 |
| n_R | 22 gradient (adv) | −0.05629, −0.05658, −0.05648 | 0.00029 / 0.02 |
| n_t 1000/2000/4000 | 1 M★ | 5.2876e10, **5.27619e10**, 5.28174e10 | 1.14e8 / 2e10 |
| n_t | 3 v_tan | 256.338, 256.004, 256.173 | 0.33 / 6 |
| n_t | 7 h_thick (simple) | 1038.61, 1039.32, 1039.01 | 0.71 / 360 |
| n_t | 9 Σ ratio (simple) | 0.102465, 0.10299, 0.102774 | 0.0005 / 0.08 |
| n_z 30/60/120 | 22 gradient (adv) | −0.0565748, −0.0565751, −0.0565752 | 3e-7 / 0.02 |
| n_z | everything else | identical to the last digit | 0 |

`[verified: the run's convergence section]`. Row 20 untestable on every axis
(zero-width target, debt #17, **known**); rows 16, 17 statistical, no verdict.

### 1.3 performance (same run; a fresh interpreter per model)

    simple   0.433 s cold, 0.408 s warm; import + registry 0.006 s
      halo 0.0006  assembly 0.0002  disc 0.0003  sfh 0.0714 (16.5%)  chemistry 0.0402 (9.3%)
      vertical 0.0072  bar 0.0002  population 0.0000  pattern 0.0093 cold / 0.0002 warm
      systems 0.1153 (26.6%)  formation 0.0693 cold / 0.0587 warm  planets 0.1192 (27.5%)
    advanced 0.660 s cold, 0.640 s warm; import + registry 0.006 s
      sfh 0.0781 (11.8%)  chemistry_dtd 0.2662 (40.3%)  vertical_alpha 0.0089
      pattern 0.0094 cold / 0.0002 warm  formation 0.0623  systems 0.1175 (17.8%)  planets 0.1165 (17.6%)
    catalogue at 20,000 stars: layout 0.0142 s; one cell 0.0012 s (23 stars);
      nine 0.0027 s (206); every cell 0.1120 s (19,998)   [advanced: 0.0147 / 0.0012 / 0.0027 / 0.1145]

`[verified: the run's performance section]`.

### 1.4 `uv run python tools/timings.py` (cold, one interpreter per route)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0002   1.39        940
    viewer: a module         0.0003   0.0002   1.39     21,599
    index                    0.0000   0.0000   1.67      1,237
    version                  0.0016   0.0014   1.18      1,132
    stages                   0.0002   0.0001   1.53      8,645
    fields                   0.0006   0.0004   1.44     57,008
    inputs                   0.0001   0.0001   1.52      9,091
    arrays: one profile      0.0733   0.0002 328.69      4,672  halo,assembly,disc,sfh
    arrays: history          0.1197   0.0023  52.86  6,401,472  halo,assembly,disc,sfh,chemistry
    arrays: scalar           0.0729   0.0003 284.29      1,416  halo,assembly,disc,sfh
    region: one sector       0.1359   0.0032  42.52     18,720  …,chemistry,vertical
    region: whole disc       0.2425   0.1078   2.25  1,126,208  …,chemistry,vertical
    system: one star         0.1350   0.0020  67.80      2,816  …,chemistry,vertical
    adv: history             0.3334   0.0026 129.13  6,401,480  …,chemistry_dtd
    adv: alpha plane         0.3394   0.0027 126.40  6,401,528  …,chemistry_dtd
    adv: one sector          0.3459   0.0032 107.81     18,736  …,chemistry_dtd,vertical_alpha
    adv: one star            0.3545   0.0021 168.35      2,824  …,chemistry_dtd,vertical_alpha
    import + registry: 0.078-0.087 s, paid once per process and excluded from the cold column

`[verified: tools/timings.py, this run]`. Metadata routes run no stages.

### 1.5 `uv run python tools/scaling.py`

    chemistry stage      N_t=500   N_t=1000   N_t=2000   N_t=4000   N_t=8000  exponent
    simple                0.0115     0.0208     0.0390     0.0784     0.1530      0.94
    advanced              0.1055     0.1515     0.2579     0.4630     0.9103      0.78
    naive DTD (tool)     N_t=250    N_t=500    N_t=1000   N_t=2000              exponent
                          0.0052     0.0216     0.0909     0.3551                  2.03
    advanced chemistry / simple chemistry at N_t = 2000: 6.51x
    whole model, "cold": simple 0.418 s, advanced 0.631 s (1.51x)

`[verified: tools/scaling.py, this run]`. The quotation marks on "cold" are this
audit's; see P2.

## 2. Convergence findings

- **C1. Nothing drifts across its target width, on any axis, in either model**
  `[verified: §1.2]`. The biggest movement is 5.5% of a target (v_tan under N_t).
  This reproduces D94's count (54 and 57 row×axis pairs) **(known)**.
- **C2. The default grid is the outlier under N_t, not the midpoint.** Rows 1, 3,
  7, 9 and 10 move *non-monotonically*: 1000 and 4000 agree with each other
  better than either agrees with 2000 (M★ 5.2876, 5.2762, 5.2817 ×10¹⁰)
  `[verified: §1.2]`. The amplitude is 0.2% and inside every bar, so it is an
  observation, not a drift. The cause is [inferred]: the merger-delivered second
  infall starts as a step at `last_major_merger_time` in `sfh.episode`
  (`galaxy/stages/sfh.py`, `elapsed >= 0.0`), and where 3.8 Gyr falls relative to
  a cell edge changes with N_t. See D-1: the constant that was supposed to
  smooth this is dead.
- **C3. The sweep judges drift against the target width, so a wide target hides a
  real grid dependence.** Row 1's width is 2 × 10¹⁰; a scalar could move 40%
  and pass. `[inferred from convergence._judge]`. A converged-rate criterion
  (does 400→800 move less than 200→400?) would catch what a bar cannot; C2 is
  exactly the case a bar misses.
- **C4. What is not swept.** `n_phi`, `R_max`, `t_max`, `z_max`; the advanced
  chemistry's own resolution constants `DTD_BINS = 32` and `AGE_BIN = 0.5`; the
  catalogue sample (20 000) and the ensemble size (20) `[verified:
  galaxy/specs/convergence.py SWEEPS; galaxy/stages/chemistry_dtd.py]`. Probed
  here for the two chemistry constants: DTD_BINS 16/32/64 moves the advanced
  gradient −0.05670/−0.05658/−0.05660 and [Fe/H](R₀) by 0.0004; AGE_BIN
  0.25/0.5/1.0 moves the old gradient by 4 × 10⁻⁵ and the local spread not at all
  `[verified: probe P12, this run]`. Converged; recorded so the next sweep can
  include them rather than take this on report.
- **C5. The N_z sweep tests one consumer.** Only the advanced chemistry reads the
  z-axis (`halo_potential[:, 0]`); the simple model is bit-identical across N_z
  because nothing reads z `[verified: §1.2, n_z rows]`. The sech² heights are
  analytic. So "N_z converged" means "N_z unused", which is a true statement
  with less content than it looks.

## 3. Performance findings

- **P1. D95's claim that cold and warm agree at every stage is false for the
  first seeded stage.** `pattern` costs 9.3 ms cold and 0.2 ms warm in both
  models (46×); `formation` 69 ms cold against 59 warm `[verified: §1.3]`. The
  pattern number is the first `numpy.random.Generator` construction of the
  process landing on whichever seeded stage runs first [inferred:
  `galaxy/core/seeds.py::rng`]. Nine milliseconds is 2% of the run and matters
  to nothing, but the profile's warm column *is* a reading of a cache there,
  which is the thing D95 says it is not.
- **P2. `tools/scaling.py` labels a warm number "cold".** `measure()` runs the
  stage sweeps, the naive convolution and the multiplier, and *then*
  `time_model()` in the same interpreter; its "whole model, cold" is the
  seventeenth model run of that process `[verified: tools/scaling.py measure]`.
  The true cold numbers are the profile's: 0.433 and 0.660 s against the tool's
  0.418 and 0.631 `[verified: §1.3, §1.5]`. Rule B2: a label that says cold on
  a warm measurement. Small (3–4%), but the tool's docstring promises otherwise.
- **P3. The advanced chemistry's exponent 0.78 is sublinear because it is measured
  where fixed costs dominate.** The stage runs 28 transport kernels of 400 × 400
  and the wind, none of which scale with N_t; the per-timestep loop is the only
  N_t term `[verified: galaxy/stages/chemistry_dtd.py compute; §1.5]`. Between
  N_t = 4000 and 8000 the local exponent is 0.98. "Linear, with a large constant"
  is the honest reading; 0.78 published alone would suggest better than linear.
- **P4. The API's warm column measures the service cache, not the model** (c/w up
  to 329) `[verified: §1.4]`, which the tool says of itself. Nothing new; recorded
  because the cold numbers moved: `adv: one star` 0.3545 s here.
- **P5. Where a session would go.** chemistry_dtd at 40% (0.27 s) is the only
  stage worth a session **(known)**; `systems` + `planets` are 54% of the simple
  model and 35% of the advanced, and the per-cell table says a region query pays
  for its own stars only **(known)**.

## 4. The calibration audit, constant by constant

Verdicts: **holds** (cited, mechanism unchanged, no acceptance row depends on
its exact value); **fitted** (set against an observable or a row — then that row
is a check that the fit took, not evidence); **chosen** (picked inside a cited
range with a row's verdict in view); **load-bearing** (a cited uncertainty on
it is wider than a row's target); **stale-risk** (rule B10: fitted while a
mechanism now changed was live); **dead** (no field reads it to any effect).
"Probe" numbers are this run's; scripts P1–P14, Q1–Q14 and the round-3 sweep
are summarised in the cells that quote them.

### 4.1 `galaxy/models/level0.py`

| constant | value | set against | since then | verdict, with the number |
|---|---|---|---|---|
| G | 4.3009e-6 | IAU GM☉ / kpc / (km/s)² | — | **holds** `[verified: tests/test_special.py::test_G_is_the_IAU_nominal_solar_mass_parameter]`. Duplicated by hand in `galaxy/stages/vertical.py::scale_height` (D-9). |
| H0 | 0.07 | BHG16 h = 0.7 | — | **holds**; ±8% ladder/CMB unmodelled, says so `[verified: level0 about]`. |
| F_BARYON | 0.152 | Planck Ω_b h² with h = 0.7, Ω_M = 0.3 | — | **holds**; 3% below Planck's own, says so. |
| CONCENTRATION_NORM | 4.1 | c_vir normalisation (Wechsler+02) applied to c₂₀₀ without conversion (debt #12) | halo unchanged since S1 | **load-bearing**. Probe Q5: K = 3.5 gives c₂₀₀ 12.25 and v_tan **247.97, inside row 3's 245–251**; K = 3.3 gives 245.20 `[verified: probe Q5]`. The c_vir→c₂₀₀ conversion debt #12 names is [recall] of order 0.8, i.e. K ≈ 3.3–3.5. So the conversion alone closes row 3. See D-4. |
| R_SUN | 8.2 | BHG16 | — | **holds**. |
| RETURN_FRACTION | 0.30 | Kroupa/Chabrier [recall] | S9's DTD replaced instantaneous recycling for *metals*; the *mass* return in `sfh` is still instantaneous, shared by both models | **holds** for the shared sfh. `chemistry_dtd` omits the (1 − R) factor in its `formed` mass — a common factor in every ratio it publishes, so harmless `[verified: chemistry_dtd.py compute, `formed = …`]`. |
| KS_NORM | 2.5e-4 | Kennicutt 98, (2.5 ± 0.7) × 10⁻⁴, deliberately not fitted | — | **holds, load-bearing**: at 3.2e-4 (inside the bar) row 2 reads 1.847, 0.007 above its bound; row 20 5.25e9 `[verified: round-3 probe]`. |
| KS_INDEX | 1.4 | Kennicutt 98, ±0.15 | — | **holds, load-bearing**: 1.55 gives row 2 = 1.777 (pass), row 20 5.14e9 `[verified: round-3 probe]`. |
| SF_THRESHOLD | 5.0 | [recall] 5–10 M☉/pc²; the *low* end taken | — | **chosen, and it is the other end of its own range that the failing rows want.** At 10: row 2 = 1.709 (pass), row 20 = 7.52e9 (6% low instead of 28%), row 22 = −0.0456 (from −0.0237), row 1 = 5.10e10 (pass), row 3 unchanged `[verified: round-3 probe]`. See D-3. |
| GAS_DISC_SCALE_RATIO | 1.0 | Two arguments (MMW98; running the observed ratio back) — D49 | — | **holds as argued, but far from "does nothing".** 0.8 → 1.2 moves row 3 261.1 → 248.7 (pass at 1.2), row 4 2.00 → 2.97, row 20 4.32e9 → 7.25e9, row 22 −0.047 → −0.018, row 2 1.54 → 2.33 `[verified: probe P5]`. The about's "at 1.0 it does nothing" means it is the identity factor; every failing row is steep in it. See D-3, D-6. |
| MERGER_DURATION | 0.5 | [recall] crossing time; "not cosmetic" | S3 | **dead.** Its only product, `merger_delivery`, is read by no stage `[verified: grep of galaxy/ for merger_delivery: only assembly.py]`; `sfh` rebuilds the second episode as a step at the last major merger from `second_infall_share`, which is the window's integral and is 0.6 whatever the width. Probe Q1: 0.1 and 2.0 Gyr change every acceptance scalar by ≤ 3.4 × 10⁻¹⁵ `[verified: probe Q1]`. D-1. |
| BIRTH_DISPERSION | 8 | [recall] 6–10 km/s | — | **holds**: 6/8/10 gives row 6 235/253/276, all inside `[verified: probe P10]`. |
| SECULAR_HEATING | 25 | the 10 Gyr end of the AVR, re-chosen after the 5 Gyr end left the thin disc half as thick (about says so) | — | **fitted to row 6.** 20 → 176 (fail), 25 → 253 (pass by 3 pc), 30 → 347 (pass); row 7 883/1039/1231 (fail at 30) `[verified: probe P10]`. The pair (25, 120) is the corner where rows 6 and 7 both pass. |
| SECULAR_HEATING_INDEX | 0.5 | random-walk value, top of 0.3–0.5 | — | **holds**: 0.3 gives row 6 = 301, row 7 = 1021, both inside `[verified: probe P10]`. |
| MERGER_HEATING | 120 | "scaled so the 1:4 merger leaves ~30 km/s, which is what makes it thick" | — | **fitted to row 7.** 100 → 867, 120 → 1039, 140 → 1243 (fail) `[verified: probe P10]`. |
| BAR_LENGTH_RATIO | 2.0 | [recall] 1.5–2.5 | — | **chosen** **(known: debt #21)**. 1.5 → row 15 = 3.74 (fail), Ω 9/20 and R_CR 8/20 in target; 2.5 → 6.23 (fail), Ω 11/20, R_CR 9/20 — and rows 16, 17 still *pass* at 2.5 by the intersects criterion `[verified: probe P9]`. Rows 16 and 17 are downstream of 15. |
| FAST_BAR_RATIO / SCATTER | 1.2 / 0.2 | BHG16 §4.4 | — | **holds**. 17/20 draws inside both targets at default `[verified: probe P14]`. |
| PITCH_SHEAR_INTERCEPT / SLOPE / SCATTER | 13 / −8 / 6 | [recall]; ruling 3 | — | **holds, unfalsifiable here** (debt #22). No row reads them. |
| SOLAR_METALLICITY | 0.0142 | Asplund+09 | — | **holds** as [Fe/H]'s zero point in the simple model. In the advanced model `metallicity_history` at R₀ reads Z = 1.24 Z☉ where [Fe/H] = 0.00 `[verified: probe P1]`: the core-collapse metals are taken in solar proportion to oxygen (which already contains the Sun's *whole* iron), then the Ia iron-peak is added on top with a factor 2.0 that lives in the code, not the register (D-10). Nothing downstream reads Z `[verified: grep of galaxy/ for metallicity_history readers: none]`. |
| DISC_MASS_FRACTION | 0.01 | Class II surveys [recall] | — | **holds**; degenerate with PLANETESIMAL_EFFICIENCY, says so. |
| DISC_MASS_SCATTER | 0.3 | §12 | — | **holds**; sets β = 2.99 (debt #25). |
| PLANETESIMAL_EFFICIENCY | 0.171 | fitted: 5% giant occurrence at [Fe/H] = 0, M = 1 M☉ | the fit reads `giant_probability(0.0, 1.0)`, not any field, so S9 could not move it | **fitted, and the fit stands**: `giant_occurrence_sun` = 0.0499 in both models `[verified: probe P1]`. What S9 changed is the *consumer*: advanced `giant_occurrence` at 2 kpc = 0.189 against the simple model's 0.026 (7.3×), because `feh_stars_young(2 kpc)` is +0.49 against +0.17 `[verified: probe P1]` **(known: LESSONS S10 run 1, D96)**. |
| CORE_CRITICAL_MASS, ICE_LINE_TEMPERATURE, ICE_BOOST, HILL_SEPARATION, DISC_INNER/OUTER_EDGE | 10, 170, 2, 10, 0.05, 30 | [recall], each documented | — | **holds**; the ice line lands at 2.67 AU `[verified: tests/test_planets.py::test_the_ice_line_is_where_the_solar_system_puts_it]`. |
| V_SUN_PECULIAR | 12.24 | Schönrich+10 | — | **holds**. |

### 4.2 `galaxy/models/simple.py`

| constant | value | set against | since then | verdict |
|---|---|---|---|---|
| NET_YIELD | 0.011 | [Fe/H](R₀) = 0 at S2 (D47) | S3 added the merger-delivered second infall and shrank the disc | **fitted, drifted −0.025 dex, harmless**: [Fe/H]_gas(R₀) now reads −0.0248 `[verified: probe P1]`; the test tolerates 0.1 `[verified: tests/test_chemistry.py::test_the_solar_neighbourhood_comes_out_solar]`; no row depends on it (D47). |

### 4.3 `galaxy/models/advanced.py`

| constant | value | set against | verdict |
|---|---|---|---|
| SOLAR_IRON, SOLAR_OXYGEN | 1.29e-3, 5.73e-3 | Asplund+09 | **holds**. |
| Y_O_CC, Y_FE_CC, Y_FE_IA | 0.015, 1.2e-3, 1.7e-3 | WAF17 [recall] | **holds**; plateau +0.45 `[verified: tests/test_chemistry_dtd.py::test_the_plateau_is_the_core_collapse_yield_ratio]`. |
| DTD_INDEX, DTD_MIN_DELAY | 1.1, 0.15 Gyr | Maoz+; WAF17 | **holds**; binned at 32 delays, converged (C4). |
| WIND_INDEX | 2.0 | "energy-driven; chosen, not fitted" (D89) | **chosen, and row 22's pass is conditional on the choice.** At 1 (momentum-driven, the other cited option) the gradient is −0.0482, outside −0.069…−0.049; at 3, −0.0664 `[verified: probe P7]`. The tilt is a prediction *given* 2; the pass is not evidence that 2 is right. D89 records the choice as made before the row was read [recall of D89's wording; the order is not verifiable from here]. |
| WIND_SPEED | 1010 km/s | [Fe/H]_gas(R₀) = 0 against the present-day potential | **fitted; the fit holds** ([Fe/H](R₀) = +0.0018 `[verified: probe P1]`) **and is stale-risk twice over.** (i) The potential it was fitted against carries row 3's 8 km/s excess (debts #12/#18): every fix to row 3 lowers v_esc(R₀) and moves the fitted point. Sensitivity: ±5% in v_esc/WIND_SPEED is ∓0.03 dex at R₀; the gradient moves 0.0004 `[verified: probe P7]` — row 22 is robust, the level is not. (ii) The escape fraction is evaluated on the *present-day* potential and applied at every time: with the baryonic potential scaled to the mass in place, v_esc(R₀) was ~530–540 km/s at t = 2–4 Gyr and f_esc ~0.78 against the 0.753 used; 30% of R₀'s star formation predates t = 6 Gyr `[verified: probe Q14]`. A 3% error on the early metal loss; small, and unmodelled rather than wrong. |

### 4.4 Input defaults, `galaxy/core/registry.py`

| input | default | set against | verdict |
|---|---|---|---|
| halo_mass | 1.1e12 | McMillan / Karukes+19 | **holds**; row 19 *is* this input (the halo stage says so). |
| disc_spin | 0.0173 | re-derived at S1 to reproduce R_d = 2.6 kpc (D30) | **fitted**: row 4 (2.49) is the echo. |
| halo_assembly_z | 2.5 | midpoint of "z ≈ 2–3", [inferred] | **load-bearing** (debt #12 says 10 km/s across 2–3). Probe P8: z_f = 2.0 → v_tan **248.17 (row 3 passes)**, 2.5 → 256.00, 3.0 → 263.46 `[verified: probe P8]`. D-4. |
| baryon_retention | 0.35 | chosen to reconcile rows 1 and 20 (about says so) | **fitted to row 1, and load-bearing on row 3**: 0.30 → row 1 4.49e10, row 2 1.686, row 3 **246.3** — rows 1, 2, 3 all pass — row 20 5.34e9; 0.40 → row 3 265 `[verified: round-3 probe]`. D-4, D-5. |
| infall_timescale, inside_out_index | 7.0 Gyr, 1.0 | Chiappini+01 τ_D(R), one relation | **holds**. n = 3 gives −0.0666 (debt #15's "needs n near 3" confirmed) at the cost of row 2 = 1.29 `[verified: round-3 probe]`. |
| migration_efficiency | 3.6 kpc | Frankel+18 [recall] | **holds as a citation; the record around it is wrong** (D-2). Young/old ratio 3.18 in the simple model, 3.09 in the advanced; 1.75 is reached near 2.9 kpc (simple: 3.0 → 1.93, 2.5 → 1.17) and between 2.5 and 3.6 (advanced: 1.59 at 2.5) `[verified: probes Q2, Q3]`. |
| mergers: Gaia-Enceladus (3.8 Gyr, 1:4, gas 0.5) | Helmi+18, Belokurov+18 | **holds** for time and ratio; the gas share is ruling 11's and untested. |
| mergers: Sagittarius (8.8 Gyr, 1:50, gas 0.2) | Ibata+94 for the event | **defect** (D-7): delivers 0.2 × (1 − 0.5) = 10% of the whole baryon budget, 5.9 × 10⁹ M☉ `[verified: probe P1, second_infall_share 0.6 = 0.5 + 0.1]`, from a satellite whose entire progenitor is ~10⁸–10⁹ M☉ [recall]; and `sfh` starts that gas at the *last major merger*, 3.8 Gyr, five Gyr before the event, because it reads only the total share and the major onset `[verified: sfh.py compute: `merger_share`, `onset`]`. Sagittarius's `time` reaches nothing that survives. |
| seeds | 0 | — | holds. |

### 4.5 Constants outside the register

Preflight checks that every registered constant is read; it cannot see a number
that never registered. Found: `y_z_ia = 2.0 × Y_FE_IA` and the bimodality
detector's five thresholds (`DIP_DEPTH 0.5`, `PEAK_SEPARATION 0.1`,
`MODE_MIN_SHARE 0.1`, `WIDE_SPAN 0.5`, histogram 0.02 dex) in
`chemistry_dtd.py`; `THRESHOLD_WIDTH 0.25` in `sfh.py`; `GRADIENT_FIT_RANGE`,
`YOUNG_MAX_AGE`, `OLD_MIN_AGE` in `chemistry.py`; `SCALE_LENGTH_FIT` in
`vertical.py`; some twenty in `planets.py` (278 K at 1 AU, L ∝ M^3.5, escape
parameter 10 [inferred], mass–radius indices, locking radius, planet minimum
0.05 M⊕) `[verified: those modules' top-level assignments]`. Most are numerical
or rendering choices and say so. Two carry a verdict: `DIP_DEPTH = 0.5` decides
row 24 for the best input vector S9 found (dip 0.384 reads `single` at 0.5 and
0.4, `bimodal_wide` at 0.3 `[verified: probe P12]`; at the default the dip is
0.0 and no threshold matters), and `OLD_MIN_AGE = 10 Gyr` makes row 23's "old"
population exactly the simple model's thick disc (born before 3.8 Gyr).

## 5. The green rows: which constant could have made each green, and was it

| row | model(s) | what makes it green | verdict |
|---|---|---|---|
| 1 M★ | both | `baryon_retention` chosen against it; and the target 5 ± 1 × 10¹⁰ *includes the bulge* (rows 10 + 11 + 12 = 3.5 + 0.6 + 1.5), which the model has not got — the disc alone should read ~4.1 × 10¹⁰ `[verified: GALAXY_INPUTS.md §7 rows 1, 10–13; spec.py]` | green by a chosen input, for the wrong reason (D-5) |
| 4 R_d | both | `disc_spin` derived to reproduce 2.6 kpc | calibration echo (4% low of the fit, inside) |
| 6 h_thin | both | `SECULAR_HEATING` re-chosen after a fail; 253 vs a bound at 250 (simple) | fitted; fragile |
| 7 h_thick | simple | `MERGER_HEATING` scaled to make the disc thick | fitted |
| 8 ρ ratio | simple | rows 9 and 7 (not independent, the stage says so) | derived from two constructed numbers |
| 9 Σ ratio | simple | cancellation of rows 5 and 11 (debt #19) | known cancellation |
| 10 M_thin | simple | = row 1 − row 11; passes at 4.20e10 **because row 11 fails high**: a thick disc at its target 6 × 10⁹ would put the thin disc at 4.7 × 10¹⁰, outside 2.5–4.5 `[verified: probe P3, "GES only": thick 1.38e10 → thin 3.91e10]` | second cancellation (D-5) |
| 15 a_bar | both | `BAR_LENGTH_RATIO = 2.0` | chosen **(known)** |
| 16, 17 | both | downstream of 15 with a cited 1.2 ± 0.2; the intersects criterion passes with as few as 9/20 draws inside | chosen upstream; weak criterion |
| 19 M₂₀₀ | both | it is the input | not a check |
| 22 gradient | advanced | `WIND_SPEED` sets the level (no effect on the slope), `WIND_INDEX = 2` sets the tilt; at 1 it fails | the one green row that is a prediction, conditional on one binary choice |

No green row is an unconditioned prediction. Row 22 (advanced) is the nearest.

## 6. Defects

Numbered D-n so D97 can cite them; "record" means the code does what the
document says it does not, or the reverse; "physics" means the mechanism.

- **D-1 (record + mechanism). `MERGER_DURATION` is dead and its about line
  describes a mechanism that does not run.** `assembly` spreads each event's gas
  over a Gaussian window and publishes `merger_delivery`; nothing reads it;
  `sfh` delivers the whole merger share as an exponential starting at a step at
  the last major merger. Probe Q1: ≤ 3.4 × 10⁻¹⁵ relative change in every
  acceptance scalar over 0.1–2.0 Gyr `[verified: probe Q1; grep in §4.1]`. The
  about says "delivering the gas instantaneously makes the star formation rate
  depend on the timestep, which is the same class of defect the star formation
  threshold had (D46)" — and that is what the code does (C2's non-monotone N_t
  drift, 0.2%). Prediction (B4): feeding `merger_delivery` into `sfh` in place
  of the step removes the non-monotone N_t movement of rows 1 and 10.
- **D-2 (record). The simple model's row 23 miss is recorded with a stale
  reason.** `spec._MISSES[row 23].reason` says "Migration itself is close to
  right — the young/old ratio is near the observed 1.75" `[verified:
  galaxy/specs/spec.py]`; the ratio is 3.18 `[verified: probe P1]` and has been
  3.2 since S3, whose own test pins it `[verified:
  tests/test_chemistry.py::test_migration_over_flattens_the_old_population]`.
  Consequence for debt #28: "migration is too strong *once the tilt is right*"
  is the wrong framing — it is too strong in the simple model with the tilt
  wrong, by the same factor (3.18 against 3.09). The register's two live
  explanations (the citation's width is not this kernel's; the old gas gradient
  is too steep) both survive; the first is now the likelier, since the same
  kernel over-flattens two different old-gas gradients by the same ratio
  [inferred]. Also stale in the same entry: "−0.027 dex/kpc" for row 22 (it is
  −0.0237 `[verified: §1.1]`).
- **D-3 (physics, register). Rows 2, 20 and 22 in the simple model have a cited
  constant that closes or nearly closes them, and the register attributes them
  to a missing mechanism.** `SF_THRESHOLD = 10` (the top of its own cited 5–10)
  gives row 2 = 1.709 (pass), row 20 = 7.52 × 10⁹ (6% low), row 22 = −0.0456;
  row 1 stays green `[verified: round-3 probe]`. Debt #18 explains rows 2 and
  20 by a missing high-angular-momentum accretion component; debt #15 explains
  row 22 by outflows and "an inside-out index near 3". Both may still be right
  — a higher threshold holds more gas unconsumed, which is the same *effect* as
  extended gas arriving where the threshold protects it — but the register
  should carry the cheap explanation beside the expensive one. Prediction: the
  extended component debt #18 asks for closes row 20 at threshold 5 with row 3
  and row 4 unmoved; the threshold does not (row 3 is unchanged at 256.0 by it).
  That difference is the test between them.
- **D-4 (register). Row 3's miss has three live explanations and the register
  names one.** v_tan = 256.0 against 248 ± 3 is attributed to "all the baryons
  in the compact disc" (debt #18). Also sufficient on its own: (i) the
  c_vir→c₂₀₀ conversion debt #12 records as unmodelled (K = 3.5 → 247.97); (ii)
  z_f = 2.0 inside the cited 2–3 (248.17); (iii) `baryon_retention = 0.30`
  inside "~0.35" (246.3) `[verified: probes Q5, P8, round-3]`. The recorded
  prediction ("splitting the baryons … lowers v_c there") cannot fail in a way
  that discriminates, because each of the three moves the number the same way.
  Prediction that can: the extended component leaves c₂₀₀ and the stellar mass
  where they are; (i) changes `halo_concentration` to ~12; (iii) changes row 1
  to 4.5 × 10¹⁰. Rows 1 and 19 are the discriminants.
- **D-5 (record). Rows 1 and 10 pass by two cancellations the register does not
  list.** Row 1's target includes the bulge; the model's disc carries it (debt
  #11 says the *gas* was the excess and S2 removed it; the bulge's 1.4–1.7 × 10¹⁰
  is still in the disc). Row 10 passes only because row 11 fails high (§5).
  Prediction: a bulge stage that takes 1.5 × 10¹⁰ out of the disc fails row 1
  (3.8 × 10¹⁰) unless `baryon_retention` rises, which then fails row 3 by 9 km/s
  more (round-3 probe: 0.40 → 265). The three cannot be green together without
  the extended component or a lower concentration — D-4 again.
- **D-6 (register). `GAS_DISC_SCALE_RATIO` is presented as inert and is the
  steepest lever on the failing rows.** The about line: "at 1.0 it does
  nothing." Probe P5: ±0.2 moves row 3 by 12 km/s, row 20 by 3 × 10⁹, row 22 by
  0.03 dex/kpc, row 4 by 1 kpc `[verified: probe P5]`. Debt #18's "second
  accretion channel at high angular momentum" is, to first order, this constant
  above 1 on part of the infall. Not a defect in the value — D49's two arguments
  stand — but in the sentence, and in the register not naming it under #18.
- **D-7 (physics, input default). The Sagittarius event delivers 5.9 × 10⁹ M☉ of
  gas, from the wrong time.** §4.4. Removing its gas (or the event) puts row 2 at
  **1.837, inside 1.46–1.84**, row 8 at 0.037, row 9 at 0.150 (both inside), row
  20 at 5.66 × 10⁹, row 11 at 1.38 × 10¹⁰, row 5 at 1.31 `[verified: probe P3]`.
  So the recorded row 2 miss (debt #18, "the second episode decays on the same
  7 Gyr timescale") is at least half an unphysical input default; and a
  registered miss that starts passing fails the spec run for that model
  (`spec.stale`), so the default cannot be corrected without re-recording rows 2
  (both models) in the same commit. Left in place (this audit fixes no physics),
  recorded here and in the register as a new debt. Prediction: with Sagittarius
  carrying ≤ 1% of the budget, row 2 passes in both models and rows 5, 9, 11 of
  the simple model move as above; if row 2 does *not* pass, debt #18's
  timescale explanation is the whole story after all.
- **D-8 (record + mechanism). "Without migration the local metallicity
  distribution comes out far too narrow" is refuted by the model that was built
  to show it.** GALAXY_INPUTS.md §8 (line "…comes out far too narrow `[recall]`")
  and `FEH_SPREAD_SUN`'s about line say so; `feh_spread_sun` is 0.294 dex with
  `migration_efficiency = 0` and 0.299 at 3.6 `[verified: probe Q2]`. The spread
  is the local age–metallicity relation (old stars at R₀ read −0.55, the gas
  0.00 `[verified: probe P1]`), and migration adds 2% to it. The test
  `test_the_solar_neighbourhood_has_a_spread_and_migration_makes_it` passes on
  0.299 > 0.294 and asserts a mechanism the model does not exhibit.
- **D-9 (code, rule A9). `vertical.scale_height` hard-codes G = 4.300917270e-6**
  instead of reading the constant `[verified: galaxy/stages/vertical.py]`. The
  stage's `reads_constants` omits G; a change to level0's G would leave every
  scale height on the old value. The duplicate rule A9 forbids, in the file
  that quotes the rule.
- **D-10 (register, rule A8). The advanced chemistry's total metallicity has its
  own zero-point error and an unregistered constant.** Z(R₀)/Z☉ = 1.236 where
  [Fe/H] = 0 `[verified: probe P1]`; the `2.0` in `y_z_ia = 2.0 * y_fe_ia` is in
  the code with a [recall] comment `[verified: chemistry_dtd.py compute]`.
  Consequence today: none, no stage reads Z in the advanced model (§4.1). It
  would matter to the first consumer of `metallicity_history`.
- **D-11 (mechanism, advanced). The catalogue does not migrate, so the
  advanced model's migrants never reach the viewer or the planets.** `systems`
  draws a star's radius from the present `stellar_surface_density` (the sfh
  stage's, unmigrated) and looks its abundance up at *that* radius and its birth
  time `[verified: galaxy/stages/systems.py materialise]`. At R₀ the catalogue's
  [Fe/H] spread is 0.192 (advanced) against the chemistry's own 0.299, and its
  mean −0.263 `[verified: probe P1]`; the planets stage reads the catalogue. The
  simple model is consistent with itself (a kernel on a mean is not a population
  either). Not a bug in either stage; a boundary S9 did not cross, and the field
  `feh_spread_sun` now describes stars the catalogue does not contain.
- **D-12 (record, D95).** P1: the profile's cold and warm columns do not agree
  for `pattern` (46×); the sentence "Cold and warm agree at every stage, so there
  is no cache in the reading" is false at one stage. **D-13 (record, tool).**
  P2: `tools/scaling.py` publishes a warm number as "whole model, cold".
- **D-14 (record, D89/about). `WIND_INDEX`'s about says "the tilt it gives the
  gradient is a prediction"; the pass of row 22 is conditional on the choice
  of 2 over the equally cited 1** (§4.3). Not a defect in the choice; in the
  row being read as evidence for the wind model rather than for the
  energy-driven variant of it.

## 7. Not found

What the instruments and probes looked for and did not find:

- **Grid dependence** in any acceptance scalar across N_R, N_t, N_z, DTD_BINS or
  AGE_BIN (C1, C4): none beyond 0.2%.
- **A stale calibration.** `NET_YIELD` (−0.025 dex), `WIND_SPEED` (+0.002 dex),
  `PLANETESIMAL_EFFICIENCY` (0.0499) all still sit on the observable they were
  fitted to `[verified: probe P1]`; S9 changed the consumers of two of them, not
  the fits.
- **A cache in the cold profile** other than P1's 9 ms first-RNG cost; cold and
  warm agree elsewhere to a few percent (§1.3). **An endpoint running stages it
  does not need** (§1.4, the stages column): none.
- **Superlinear cost** in N_t for either chemistry (0.94, 0.78; the naive form
  2.03 on the same histories, so the instrument sees what it exists to see).
- **A dependence of any row on `MERGER_DURATION`, `PITCH_*`, `FAST_BAR_SCATTER`
  beyond the ensemble, `SECULAR_HEATING_INDEX` across its range, or
  `BIRTH_DISPERSION` across its range** — none that changes a verdict (§4.1).
- **A second thick disc** in the advanced model: none (dip 0.0 at default, 0.384
  at best; debt #27 stands, **known**). **A valley opened by the detector's own
  thresholds** at the default: none (the dip is 0.0, so DIP_DEPTH is not what
  says `single` there).
- **A wind calibration that breaks the gradient**: WIND_SPEED ± 10% moves row 22
  by ± 0.0006 (§4.3). **Row 22's advanced pass by any single constant other than
  `WIND_INDEX`**: none found; the tilt survives the wind speed, DTD_BINS,
  AGE_BIN and the grid.
- **Double-counting of the disc in the rotation curve, a wrong overdensity in
  R₂₀₀, a misplaced R₀ cell, a sign error in the sech² inversion, a
  non-conserving transport kernel**: each has a test and each passes
  `[verified: uv run pytest, 2026-09-05: 1 failure, tests/test_hook.py::test_hooks_path_is_configured_in_this_checkout, a worktree artefact fixed by setting the worktree's hooksPath]`.
- **Anything in the advanced model's shared stages that differs from the
  simple model's**: bit-identical upstream of chemistry `[verified:
  tests/test_models.py::test_the_models_agree_upstream_of_chemistry_and_differ_below]`.

## 8. Not done, and why

No physics was changed (the brief). The Sagittarius default (D-7), the dead
constant (D-1) and the stale miss text (D-2) are each a one-line fix; each is
left as a registered debt because fixing D-7 makes a recorded miss pass, which
is a spec failure until the register is rewritten in the same commit, and that
is a session's decision, not an audit's. The wind's time-independence (§4.3
ii) was estimated, not modelled: a 3% effect on early metal loss, recorded as a
number rather than a debt.
