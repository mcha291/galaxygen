# BRIEF — for S45: the owner's choice after Audit IV's fixes

**The state (2026-10-01).** S44 is merged (D195): Audit IV's four fixes are applied and row 37 is entered. The grid's
axis is read on its own total oxygen (8.93; 3.0 % of regions clamp, the Hα-weighted [O III]/Hα 0.752, [N II]/Hα
0.082); the WFC3 sets declare `wavelengths: "vacuum"` and `line_response` converts the model's air lines by Morton
1991 (F656N at Hα 0.945, F502N at [O III] 0.899); the grain row is the file's, its keys pinned; the record's nine
sentences are set right (FSPS clamps; D192's sentence corrected in D195; one solar mass 1.98841e33). **Row 37 is a
recorded miss under #117: `nii_halpha_gradient_hii` −0.1035 dex kpc⁻¹ against the blind [−0.045, −0.005], 6.5σ**,
steeper than S43's −0.0815 (the offset moved it out, not in). Register: **62 open = 11 permanent + 51 carried, 44
discharged.** Specs 12 / 20 / 5 of 37 in both models; vitest 121. Nothing is owed from S44 except #119 (optional, left).

## What S45 could do — the owner chooses; none is started without the word (numbers from #124, D196, row 38)
1. **Row 37's diagnosis, by the miss's own prediction** (`spec.MISSES[37]`, D195 (5)). Read the grid first: at a
   fixed age and log U, d log([N II]/Hα)/d log Z along the grid's Z axis (`nebular.grid_line_ratios` on the loaded
   `_line_grid()`), times the model's d log Z/dR over 8.2–15.4 kpc (`hii_oxygen_abundance` against `cluster_radius`),
   is the slope the grid alone imposes. If it is within 0.01 dex/kpc of −0.1035 the grid's temperature run is the
   cause; if it is inside the window, the chemistry's N/H gradient (Nicholls' secondary term on the model's O/H
   gradient) is. A slope inside the window after either one change alone kills the other. What may follow: the
   blind reader's direction note says the Galactic T_e rises +345–359 K kpc⁻¹ and nearly cancels the abundance
   fall — a grid read at the region's own T_e is not available (the grid's T_e is its own), so a diagnosis that
   lands on the grid becomes a debt with a stated closer, not a fix. Also the secondary reading: 0.137 at 8.2 kpc
   against 0.20–0.40 (it was 0.205 as built); a fix that lifts the slope must not sink this further.
2. **#119 — the diffuse gas's two ratios** as sourced scalars once the layer is ruled the WIM proper: [N II]/Hα 0.5
   (0.3–1.0) and [S II] 6716/Hα 0.3–0.5 (doublet ≈ ×1.7), Madsen 2006 / Haffner 1999 as read in `AUDIT_IV_BLIND.md`
   Target B; published by the nebular stage beside the layer's Hβ, drawn by the render route's `lines_dig`.
3. **#107 — the SED's anchors**: CMD's U B V are Maíz Apellániz 2006's and YBC's Vega is `alpha_lyr_stis_008`; what
   closes it is a download (the owner's word), then a reading and a re-pin of V1's 8.9 × 10⁻⁵.
4. **A redeploy** (`galaxygen-azure-deploy`: `deploy.ps1 -Tag <sha>`): the live viewer predates S42–S44 — the WFC3
   sets, the vacuum key, row 37's scalar in `/api/fields`. A deploy is the owner's action; a session can build and
   check `prod` (:8018) first.
5. **Audit V** in Audit III/IV's shape, of S44 itself: a re-reader for the four constants that entered (8.93, Morton's
   coefficients, the grain row, 1.98841e33) and a blind reader for row 37's diagnosis window if item 1 is chosen.

## Gate for whichever is chosen
`test_nebular`, `test_render`, `test_spec`, `test_audit_iv` green with any moved pin's reason in its comment; specs
reported for both models; vitest and `npx vite build` clean if the sets change; the full suite backgrounded with its
own `EXIT=` line; merge, push, **tag `s45` on the merge and push it**, `ls-remote` read back, the MANUAL_TODO row,
`verify_clone --ref main`.

## Traps
- Never force-push; never touch :5173; a scratch check uses `.claude/launch.json` "prod" (:8018, `npx vite build` first),
  stopped after. `uv run` only; LF newlines; the Bash tool fails over ~8 KB; `grep -c` exits 1 on zero; `git commit -F -`
  fails; bare `python` is not on the path. Do not merge or delete the sealed branches (MANUAL_TODO §2). Download nothing
  without the owner's word (items 3 and 5's sources; a fresh SVO fetch for the instrument sets).
- The full suite is ~15–20 min; `test_s21b_the_catalogue_is_priced_per_cell…` is load-flaky — re-run it alone if it is
  the only failure, and say so. Gate the merge on the log's own `EXIT=` line.
- Builders in parallel worktrees must own disjoint files; a record pass that touches every file runs last. Brief them
  to grep the inventories (`test_graph`, `test_audit`'s `lost`, `test_sfh_azimuthal`'s row range, `test_nebular`'s
  scalar loop) by a neighbouring name, not only to edit the files named (S44's lesson).
- A number the model has printed gets only a blind or a disclosed row (#117, D192, D195): row 37's diagnosis prints
  the grid's slope, so a row on it needs a blind window set first (item 5).
- The grid's `_line_grid()` is cached; `nebular.py`'s read point is the one `grid_line_ratios` call. `OXYGEN_ABUNDANCE_
  SOLAR` (8.69) is the T_e and PAH relations' scale and must not move with the grid's 8.93.
