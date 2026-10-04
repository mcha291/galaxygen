# HANDOFF_S57 (gate G3) — the gas's steady response is built: does the solver certify what the model uses, and what must change before the merge

**For Fable, one short turn (BUILD_III §3b–§3c). Read this file and at most the five ranges named at the end. Run
nothing, explore nothing, write nothing. Answer in at most 80 lines: the verdict, each required change in final
wording, what is forbidden, and whether any part is the owner's.** Written by the Opus lead of S57, 2026-10-04.
Your G2 ruling and its two follow-ups are D216 in `docs/DECISIONS.md`; this handoff replaces G2's.

## What was built (branch `session-57`, pushed, unmerged; two Opus builders, one independent Opus reviewer)

| Piece | As built | Read against D216 |
|---|---|---|
| `stages/gas_response.py` (builder A) | d/dχ[(ε² − μ²/s²) d ln s/dχ] = s − 1 − g on 1440 periodic cells, conservative, Newton in ln s with halving, 120 steps / 30 halvings at most, batched cyclic tridiagonal solve, raise on non-convergence | Sormani's threshold 0.7202298 (published 0.7202; Richardson 0.7202228); hand-derived linear limits at four (ν, x); mean 1 to 8.5e-14 with no division; an extra base-subsonic check, SMR's cusp at 14 kpc, 3.65 % against 3.7 % |
| `stages/gas_pattern.py` (builder B) | the law of item 5 per grid ring, untapered forcing, g = (1 − taper)s + taper(1 + B cos 2(φ − φ_bar)), point evaluation linear in χ and R (item 9), no division, no fallback, one solve per run (a content-keyed cache, bit-identical with and without); the ranked ridge deleted; `arm_pattern_speed` published by `bar` | layer off, all 343 earlier fields bit-identical, specs 12 / 20 / 5 of 37, template checks 0 / 5; `cloud_count_total` one ulp apart on and off |
| Predictions (Milky Way) | 7.99 kpc 2.797 / 0.0171 / 2.571; 10.0 2.090 / 0.182 / 2.037; 11.0 1.765 / 0.385 / 1.886; 12.0 1.198 / 0.811 / 1.281 | held outside the bar's reach. Inside it not held, as foreseen (the probe used tapered amplitudes): 4.0 kpc s 4.17 / 4.5e-7 / 3.81, g 2.01 / 0.50; 6.0 kpc s 3.48 / 2.5e-4 / 3.21, g 3.01 / 0.13 |
| Disclosed check (layer on, default seeds, 53 rings over 6–10 kpc) | ratio of means: Milky Way median 2.571 (2.05–3.19, 53 of 53 inside 1.37–5.79); `ngc_4414` 1.881 (1.08–2.83, 46 of 53 inside). Width: 0.311 (0.211–0.481) and 0.422 (0.262–0.508) against 0.17 | a hit, disclosed; a miss on every ring, as predicted (one ring under the predicted 0.23) |
| Cost, cold | the stage 0.38 → 0.27 s; clouds whole disc 3.67 → 1.14 s; clusters 4.94 → 2.53 s; render 5.32 → 3.07 s | #140's cost is repaid |
| Layer on, default galaxy | clouds 16 660 → 16 667, clusters 12 814 → 12 829; the census's Q over the field's 0.987 → 0.970; a ring's light at R₀ through the dust −0.89 % → −1.82 % | re-pinned with reasons; rows 35 and 37 layer-on −2.070, −0.1039 |

## The reviewer's verdict (its own arithmetic: 60-digit referee, a Fourier-collocation solver, planted errors)

"The law as coded is the law as ruled, and the solver is sound. One blocker." Verified: ε, f_m, X re-derived on
paper and on three rings from the published fields (X(7.9875) = 7.92860), units checked, the taper applied once, the
sign right; the model's rings against its own spectral solver to 1.3e-4, 2.6e-5, 1.2e-5 (the h² error); the Jacobian
against differences (4e-10); the cyclic solve (7e-16); no division, clip, fallback or caught error anywhere in the
solve; batch independence; the cache's key complete; layer-off 343 fields bit-identical; the disclosed check
re-measured to 2e-15; nothing tuned.

**On the instrument:** every small error planted in a scratch copy moved Sormani's threshold far outside the test's
window (μ² coefficient × 1.01 → 0.7000; ε² × 1.001 → 0.71875; source s − 1.001 → 0.72356; h's 2π → 6.28 → 0.72072),
"so the test cannot pass with a wrong equation in any term the two members share. The member the model uses is the
same state with the μ² term absent, the same cyclic solve and the same convergence measure." What is μ ≠ 0 only: the
Newton step is applied to H = ε²φ + μ²e^{−2φ}/2 and φ read back (in φ the solver could not approach the threshold);
at μ = 0 that is identically the plain step. The limit: the threshold is blind to the forcing's sign and phase,
which the linear-limit tests and the hand rings certify.

### BLOCKER B1 — the convergence criterion sits inside the rounding of doubles on tightly wound galaxies
The gate says "discrete residual under 1e-10 on every cell", and `gas_response` holds max|r| < 1e-10 absolutely. A
galaxy whose drawn pitch is under about 2.7° has ε = 0.7–2.6 and Σf = 60–79 on its inner rings (f and ε both go as
1/sin p), and there the residual's rounding floor, **|r_k| ≤ (ε²/h²)(½ulp(φ_{k−1}) + ulp(φ_k) + ½ulp(φ_{k+1}))**,
h = 2π/1440, exceeds 1e-10. The referee shows Newton converges quadratically (40, 13, 3.4, 0.40, 7.9e-3, 3.3e-6,
1.6e-10) and then sits at 1.43e-10 for 113 steps; that iterate is within 0.66 ulp of the exact discrete solution,
whose own correctly rounded residual is 1.30–1.42e-10. So the ring is solved and still raises. **5 of 300 Milky Way
pattern seeds and 15 of 300 for `ngc_4414` raise** (every one at pitch ≤ 2.7°; 5–6 of 300 sit on the pitch's 1°
clip; `ngc_4414` seed 216 fails 45 rings out to 3.3 kpc, arm weight 0.56); which fail is chance (seed 1 raises at
one texture seed and passes at two others, 9.7e-11 against 1.25e-10); 400–480 converged rings per template sit
above 5e-11; the residual recomputed from the returned s passes 1e-10 on 7 passing galaxies (to 4.4e-10). The ring
mean is unaffected (the rounding telescopes: |Σr| ≤ 7e-14). `tests/test_s22_rulings.py`'s three-diagonal test
fails on seed 122 (pitch 1.0°); builder B added no fallback and pinned the failures as failures. Remedies the
reviewer names, none changing a solution's bits:
(a) accept when max|r_k| < max(1e-10, the per-cell bound above) and the sum criterion holds — "a theorem about the
rounded exact solution, not a loosened number"; (b) a backward-error criterion, |r_k| ≤ τ(|s_k| + 1 + |g_k| +
|Φ_{k+½}| + |Φ_{k−½}|), measured 5e-13–1.2e-12 on the failing rings; (c) a forward criterion: Newton's step in
ln s under a few ulp, plus the sum; (d) physics: the pitch draw's lower clip. Whichever: detect the fixed point
instead of spending the remaining steps, and assert the recomputed residual under the same criterion.
*The lead's note on the physics behind it:* on those rings the troughs reach s = 2e-44 and crests 14 over the 238
galaxies that build — the razor-thin forcing, f ∝ 1/sin p, grows without bound as the winding tightens (item 5's
declared approximation, at its worst).

### SHOULD FIX
- **S1. The width's "strongest mode" rests on a tie-break.** 52 of 53 Milky Way rings tie at the top amplitude and
  the lower m is taken (the probe's reading): 0.211–0.481, median 0.311. The higher tied m: 0.352–0.481, median
  0.466; the mode of largest forcing m·A_m: 0.423–0.481, median 0.466 (`ngc_4414`: 0.422 / 0.506 / 0.512). A miss
  on every ring either way; as built it is the kindest reading (1.24–2.83× against 2.1–2.8×).
- **S2. The saturation is inside the "untapered" amplitude, unruled.** The forcing takes published/(1 − taper) =
  A·√gain·s_sat, and s_sat = min(1, (1 − B·taper)/ΣÃ) is computed from the *tapered* sum and the bar. It is 1 on
  every ring at both templates' seeds, under 1 on 26 of 60 Milky Way pattern seeds (down to 0.62, up to 96 rings);
  no hand test sees it.
- **S3. Ring totals hold only on φ grids that divide 1440.** The sampled ring mean is off 1 by 7e-14 at 360 and 720
  cells, 2.4e-11 at 180, 2.0e-7 at 500, 1.8e-6 at 108, 2.0e-3 at 36; three small-grid tests were re-pinned from
  1e-12 to those, and the render's `halpha_hii` and `dust_placement` ring totals leave their layer-off values by
  1.26e-3 on the 36-cell grid. "A remedy with no division exists in the module already: publish cell averages
  through `sector_means` instead of centre samples" — measured 8e-15 off 1 on every one of those grids, minimum
  still positive. It changes items 9 and 11 (i)'s wording.
- **S4.** Stale counts in a test docstring (7 rings, 15 seeds).

### Notes
χ-interpolation on the model's own rings: 3.5e-4 on s beyond 6 kpc, 1.2e-3 on the worst ring (inside the bar, arm
weight 1 %), 2.96e-4 on the published field — above the 2.0e-4 pinned on the instrument's rings; R-interpolation
5.7e-4 / 7.9e-4 of the field at worst. "Offset 0" holds exactly for one mode; with several the gas crest and the
crest of the stellar modes' sum are one solver cell (0.25°) apart, one grid cell at R₀. A no-op clamp of the pitch
to [1°, 89°] mirrors `bar_terms`; the end rings are held beyond the grid. The stage declares the two retired ridge
constants only so that preflight's "every constant has a reader" passes. With the layer off the render header
still says "a narrow ridge" (frozen by the S55 reference digest). The field's ramp tops at 4; seeds reach 6.78.

## Questions

1. **G3's own question:** does the solver reproduce the published threshold for the right reason, and does that
   certify the μ = 0 member the model uses, the μ ≠ 0 step in H included? Is anything further owed to the instrument?
2. **B1: which convergence criterion**, in final wording — (a), (b), (c), or another — and how the gate's
   "residual under 1e-10 on every cell" now reads. Is (d), or any change to how low a pitch may be drawn, wanted
   as well, and is that yours or the owner's? Is the low-pitch regime (troughs of 1e-44) a finding recorded under
   the razor-thin debt, or something the build must not publish?
3. **S2:** is the forcing's amplitude the saturated one (as built), or the unsaturated A√gain? Either way, what
   hand test is owed on a saturated seed?
4. **S3:** centre samples (as ruled; ring totals exact only on grids dividing 1440) or cell averages on the model's
   φ cells (exact on every grid, no division)? If cell averages: is the published field then "the law's mean over
   each cell", and do `contrast_at` and the censuses keep the point function?
5. **The interpolation pins:** the model's own rings read 3.0e-4 on the field (1.2e-3 on s where the arm weight is
   1 %). 1440 with those pinned, or 2880?
6. **S1:** the width's definition, fixed now that the numbers are read: which mode's period, and how the recorded
   miss is worded (both readings, or one).
7. **The record's honesty:** are the disclosed check and the width, as measured, worded right ("a hit, disclosed";
   `ngc_4414`'s seven outer rings below 1.37; "a miss on every ring")? Is "offset zero" to be reworded for several
   modes? Is the stage's declaration of two constants it never computes with acceptable, or do they leave the
   registry for the tests?
8. **The verdict:** may S57 merge once your required changes are applied and the suite is green, on the lead's and
   a reviewer's check, or is another turn owed? What, if anything, is the owner's before the merge?

## The ranges you may read (at most these five)

1. `model/galaxy/stages/gas_response.py` lines 36–60 and 120–132 — the stated convergence criterion and its constants.
2. `model/galaxy/stages/gas_response.py` lines 369–461 — `_measure` and `_newton` (the halving, the μ ≠ 0 step).
3. `model/galaxy/stages/gas_pattern.py` lines 1–60 and 255–310 — the module's statement of the law; the untapered
   amplitude with the saturation in it; ε and f.
4. `model/galaxy/stages/gas_pattern.py` lines 342–405 and 497–530 — point evaluation, sector means, the grid field.
5. `tests/test_gas_pattern.py` lines 218–338 — the gate's tests as built (the two failing galaxies pinned).
