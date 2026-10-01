# BRIEF — for S50: the star-first viewer mode, on a light accounting that adds up

**The state (2026-10-01).** S49 is merged (D204): the field's light tables are integrated along each isochrone's own
points (#126 discharged) — `disc_luminosity` 4.5898 × 10¹⁰ L☉, M_V −21.110, B − V 0.569, Υ_V 2.04, the radial profile
smooth — and the bright catalogue shares the quadrature, so there is one budget. From S48 (D200–D203): `/api/bright`
(every disc star older than 20 Myr above a luminosity, per region; the 3 162 brightest are everything above 33 960 L☉;
3.35 × 10⁶ above 10³ L☉), `filters=` on `/api/bright` and `/api/clusters` (each object's `response`, L☉ through each
filter, the field's own machinery), and `/api/render?l_min=` (`stars_unresolved`: unresolved + young + bright ≡ the
total to 10⁻¹³). At 10³ L☉ the light is 26.3 % young (the clusters'), 18.8 % bright, 54.9 % unresolved. Specs 12 / 20 /
5 of 37 both models. Register 65 open = 11 + 54, 45 discharged. **The owner's API server on :8017 predates S48: it must
be restarted (the owner's, or on the owner's word) before the viewer can call the new routes.** T1 (the display
defaults) waits on the owner's slider combination.

## What S50 builds (VIEWER_TASKS.md §4; numbers from #128, D205, row 38)
1. **The star-first mode, replacing "brightest".** For the view's frustum: `/api/bright?view=…&n=N&filters=<set>` for
   the stars; `/api/clusters` with `filters=` at the view's level for the young population; `/api/render?l_min=<the
   bright header's threshold.l_min>` for the field under them — `stars_unresolved`, the bulge, the gas and dust layers
   as now. The N slider stays (10²–10⁵). **Rule the scale first (D205):** a point's channel is its `response` over the
   white, divided by the area of sky one pixel covers at the point's depth (pc²), times the field's own gain — the
   point then sits on the field's surface-brightness scale and emerges from the glow as the view closes in. The tuning
   panel's point gain and sprite size remain display multipliers on top (D199). The auto-exposure of the old mode goes
   (one exposure rule for field and points) unless the owner wants it kept as a toggle.
2. **The filter sets in the mode** (T22): the chips shown; the instrument sprite as in field mode.
3. **Picking** (T23): a bright star is named (level-3 cell, rank) and has no planetary system — the pick opens a
   summary of its columns (luminosity, temperature, phase, age, the eight magnitudes); clusters pickable to theirs.
4. **Dust in front of each point** (T20): the march's optical depth from the camera to the point, per channel — the
   same `dust_extinction` texture the field uses, read along the segment to the star.
5. **The image-level test** (T12) with or before 1: `tools/shot.py`'s sibling serving `frontend/dist`, fixed cameras,
   frames compared at a tolerance; skipped without a browser.

## Gate
vitest, `tsc -b`, `vite build` clean; **the closure on screen**: at one fixed camera, the frame's summed light in the
star-first mode (field remainder + cluster points + bright points, before tone mapping) against field mode's frame
(the total) — equal within the bright catalogue's own noise and the stated response departure (6 × 10⁻⁶ rgb); a `prod`
check (:8018 after the build, the branch's bundle built into the scratch directory before merging) with frames under
`docs/design/screenshots/s50/`; `bootstrap.py` before the full suite; the suite's own `EXIT=` line; merge, push, tag
`s50`, `ls-remote`, the MANUAL_TODO row, `verify_clone --ref main`.

## Traps
- The prefix by luminosity is exact at the grid's thresholds (0.05 dex) and by interval inside one (D203): take the
  render's `l_min` from the bright header, never from the viewer's own arithmetic (D5).
- The remainder's colour temperature is the ring's (`[inferred]`; 7.5 × 10⁻⁵ through rgb, 1.5 % narrowband). 32
  dust-shrouded TP-AGB points miss their own U by up to 2.65 mag in the SED machinery (#125): do not tune around it.
- #127: the light tables carry a thousandth on the upper main sequence (the segments' uniform spread). Not S50's.
- :5173 and :8017 are the owner's; a scratch check uses `prod` (:8018). Scripts and commit-message files go in a
  builder's own scratchpad folder. Put `tests/test_sfh_azimuthal.py` in every builder's list when a stage's output can
  depend on the model. Builders in parallel own disjoint files; the shell (`App.tsx`, `GalaxyTab.tsx`) is sequenced.
- RENDER_PHYSICS §8 binds: no frame-seeded noise, no detail below the cloud vector, no colour for appearance.
