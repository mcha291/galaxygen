# BRIEF — for S44: Audit IV's fixes and the blind row (B3: S43 checked, S44 fixes)

**The state (2026-09-30).** S43 is merged (D194): the owner chose "run the tags and do them with each session from now
on, then proceed to do Audit IV" — the tags are on the remote and C2e is amended (D193; the close now ends with `git tag
-a`, `git push origin s<NN>`, `git ls-remote --tags origin` read back, the MANUAL_TODO row applied). Audit IV read the
renderer S38–S42 at its sources (12 match / 4 differ / 4 adopted), re-derived every gate at a fourth mesh (all hold,
`tests/test_audit_iv.py`), conditioned the greens and set the forbidden-line row blind. **Nothing moved (B3).** Register:
**65 open = 11 permanent + 54 carried, 41 discharged.** Specs 12 / 19 / 5 of 36 unchanged.

## What S44 does, in this order (each a commit; numbers from #124, D195, row 37)
1. **#121 — the grid's solar scale.** Rule which oxygen the FSPS/Byler axis is entered on: the total 8.93 (Anders &
   Grevesse, the model's oxygen is a total abundance) or the gas-phase 8.71 (after Dopita's depletion). Add the constant
   beside `OXYGEN_ABUNDANCE_SOLAR` with Byler §2.1.2's sentence; move the read point in `nebular.py` (line ~275);
   re-pin `test_nebular`'s clamp share (26.4 % → ~3.0 % on the total scale) and the Hα-weighted ratios ([O III]/Hα 0.48 →
   0.75, [N II]/Hα 0.131 → 0.082, [S II] unchanged); rewrite #118's clamp sentence. `audit4_offset.py`'s numbers are in
   AUDIT_IV §6 for the check.
2. **Row 37, blind-with-disclosure (#117).** The statistic: an unweighted straight-line slope of log₁₀([N II]/Hα) of the
   Hα-weighted ring means against R over rings whose centres lie in **8.2–15.4 kpc** (`nii_6583_surface_brightness_hii`
   over `halpha_surface_brightness_hii`). Target **−0.025 dex kpc⁻¹, window [−0.045, −0.005]** (Zhao et al. 2026, AJ 172,
   168, arXiv:2607.27662, Eq. 8 over Eq. 5's 0.57; `AUDIT_IV_BLIND.md`; verified at the source at S43). The model reads
   **−0.0815** as built and ≈ −0.07 on the corrected scale: enter it as a **recorded miss** with the disclosure that the
   audit computed the statistic after the window was set, prediction "the gradient is the chemistry's or the grid's T_e
   run" — read the grid's T_e against the Galactic +345–359 K kpc⁻¹ before blaming the chemistry. The secondary check
   ([N II]/Hα at R₀ 0.27, 0.20–0.40; the model 0.205) goes in the row text, not as a second row. Specs → 12 / 20 / 5 of 37.
3. **#123 — the grain row.** Replace `(398.107, 0.0000, -0.0001, 3.493e-26, 2.498e00)` with the file's `3.184e-26,
   2.277e00` (albedo 0, ⟨cos⟩ −0.0000) and add a test pinning every kept row's λ against Draine's wavelength list.
4. **#120's convention.** Either a `wavelengths: "vacuum"` flag on `wfc3` / `wfc3n` that `spectra.line_response` honours,
   or `fetch_filters.py` shifting the curves to air by 1/1.000277 and the sets regenerated; move `test_render`'s 0.962 /
   0.903 pins (→ 0.945 / 0.899). The sprite half stays.
5. **#122 — the record pass** (nine sentences, no number): `nebular.py` and `grid_line_ratios` docstrings ("FSPS
   clamps"), the `prsc` citation ("Byler's method as FSPS ships it"), `fetch_nebular.py`'s vacuum-offset note,
   `LINE_WAVELENGTHS` and `K_OVER_MH` recall → READ, one solar mass in level-0, `filters.json`'s TIR label and citation,
   `transport.js`'s "Envoy's 60 KiB", #118's U convention; a D195 paragraph that D192's "FSPS extrapolates" was wrong.
6. Optional if time: **#119** — the DIG's two ratios as sourced scalars once the layer is ruled the WIM proper (0.5 and
   0.3–0.5 × 1.7, Madsen 2006 / Haffner 1999 as read in `AUDIT_IV_BLIND.md` Target B), drawn beside the layer's Hβ.

**Gate.** `test_nebular`, `test_render`, `test_audit_iv`, `test_spec` green with their pins moved and the reason in each
pin's comment; specs 12 / 20 / 5 of 37 in both models; vitest and the frontend build clean if the sets change; the full
suite backgrounded with its own `EXIT=` line; merge, push, **tag `s44` on the merge and push it**, `ls-remote` read back,
the MANUAL_TODO row, `verify_clone --ref main`.

## Traps
- Never force-push; never touch :5173; a scratch check uses `.claude/launch.json` "prod" (:8018, `npx vite build` first),
  stopped after. `uv run` only; LF newlines; the Bash tool fails over ~8 KB; `grep -c` exits 1 on zero; `git commit -F -`
  fails; bare `python` is not on the path. Do not merge or delete the sealed branches (MANUAL_TODO §2). Download nothing
  without the owner's word (a Maíz Apellániz 2006 curve for #107 would be one).
- The full suite is ~15–20 min; `test_s21b_the_catalogue_is_priced_per_cell…` is load-flaky — re-run it alone if it is
  the only failure, and say so. Gate the merge on the log's own `EXIT=` line.
- A window compared across levels must be exactly cells (AUDIT_IV §2); a frame-against-published-total tolerance is a
  400-ring number (§2). A blind window, once a model number is measured against it, stays blind only if the order is
  written down — row 37's text must say S43 measured after.
