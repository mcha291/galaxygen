# BRIEF — for S49: the owner's word on #126, then the star-first viewer mode

**The state (2026-10-01).** S48 is merged (D200–D203). The model now serves what a star-first picture needs: **the
bright-end-complete catalogue** (`stages/bright.py`, stage `bright_stars`, `/api/bright` with `n` or `l_min`: every disc
star older than 20 Myr above a luminosity, per region, an ordered Poisson process per level-3 cell; the 3 162 brightest
are everything above 33 960 L☉; 3.35 × 10⁶ stars above 10³ L☉), **the per-object filter response**
(`spectra.object_response`, the field's machinery factorised, within 2 × 10⁻⁵ mag of the exact integral; `filters=` on
`/api/bright` and `/api/clusters` returns `response`, L☉ through each filter), and **the field's unresolved remainder**
(`/api/render?l_min=` returns `stars_unresolved`; unresolved + young + bright ≡ the total to 10⁻¹³; the clusters carry
0.985 / 0.990 / 1.000 of the young light through rgb). At 10³ L☉ the disc's light is 24.6 % young, 18.4 % bright,
57.0 % unresolved. Specs 12 / 20 / 5 of 37 both models, unchanged. Register 65 open = 11 + 54, 44 discharged. The owner's
servers run on :8017 and :5173; never stop them. T1 (the display defaults) waits on the owner's slider combination.

## The decision asked of the owner (pending at S48's close)
**#126: fix the field's light tables now, or leave them registered.** `photometry.population_light` integrates each
isochrone on a fixed mass grid that puts one or two points on the giant branch; against the integral along the
isochrone's points the disc's light is 6.7 % high bolometric (V 5.4 %, I 11 %, H 12.4 %, K 10.9 %). The fix is to
integrate along the points (`bright.luminosity_function`'s quadrature exists) — and it moves every photometric number
the model publishes (M_V, B − V, Υ_V, `disc_luminosity`, the eight bands, the dust's absorbed starlight and so L_IR and
T_d, row 29). The session's recommendation: fix it before the viewer mode, since the mode's light accounting rests on
it (today the realised bright stars hold less light than the field subtracts for them: 1.26× in the 7–9 kpc window
above 10³ L☉). **If the owner says fix:** one builder, `population_light` on the isochrone's points, the
renormalisation factors then ≈ 1 (assert it and remove the `_own` split), every moved pin re-read with its reason and
B10 applied (constants calibrated against the old tables: the dust's heating balance first), V1's gate re-pinned,
specs re-read. **If not:** the viewer mode proceeds on the field's budget and the header's two budgets stay.

## Then the viewer (VIEWER_TASKS.md §4; numbers from #127, D204, row 38)
1. **The star-first mode** (replacing "brightest"): `/api/bright?view=…&n=…&filters=…` for the stars, `/api/clusters`
   with `filters=` for the young population, `/api/render?l_min=<the bright body's threshold>` for the field under them
   (`stars_unresolved`, the bulge, the gas and dust layers as now). **Points on the field's own scale**: a point's
   channel is its `response` over the white, divided by the area of sky its pixel covers (pc²), times the field's gain —
   so a star emerges from the glow as the view closes in, instead of through a separate point gain. The tuning panel's
   point gain and sprite size stay as display controls. The filter-set chips shown in the mode (T22).
2. **Picking**: a bright star is named (level-3 cell, rank); it has no planetary system yet — the pick shows its
   columns. Clusters pickable (T23).
3. **Dust in front of each point** (T20): the march's optical depth to the point's position, per channel.
4. **The image-level test** (T12) before or with 1: no row can otherwise prove the picture.

## Gate
vitest, `tsc -b`, `vite build` clean; `tests/test_bright.py`, `test_render`, `test_api`, `test_clusters` green; a `prod`
check (:8018 after the build, the branch's bundle built into the scratch directory before merging) with frames under
`docs/design/screenshots/s49/`; `bootstrap.py` before the full suite; the suite's own `EXIT=` line; merge, push, tag
`s49`, `ls-remote`, the MANUAL_TODO row, `verify_clone --ref main`.

## Traps
- A bright star's prefix property is exact at the grid's thresholds (0.05 dex) and by interval inside one (D203); ask
  `/api/bright` with `n` and read the header's `threshold.l_min` for the render's `l_min`.
- The remainder's colour temperature is the ring's (`[inferred]`; within 7.5 × 10⁻⁵ through rgb, 1.5 % through the
  narrowband sets). The response of parts adds to the whole to 6 × 10⁻⁶ through rgb, 2 × 10⁻³ through WFC3.
- 32 dust-shrouded TP-AGB points miss their own U by up to 2.65 mag in the SED machinery (#125): a bright star's U or B
  response can be too bright where its U is a millionth of its K. Do not tune the viewer around it.
- :5173 and :8017 are the owner's. Scripts and commit-message files go in a builder's own scratchpad folder. Builders
  in parallel own disjoint files; a builder that finds a defect in merged work reports it with a strict xfail.
