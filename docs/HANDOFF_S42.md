# HANDOFF — S42: the owner's rulings of 2026-09-27, applied on Opus while Fable's limit resets

**Why this file exists.** After S40 and S41 were built on Opus (unmerged; their handoffs), the owner answered the four
questions the build had left for them, on 2026-09-27, in chat:

1. **The Byler/FSPS nebular grid (D184): download it.**
2. **Rows 32 and 34 (Audit III, A3-7, D186): follow the audit's recommendation** — both rows take the blind windows,
   their texts keeping the disclosure.
3. **The instrument filter curves (D188, #108): yes** — download them from the SVO Filter Profile Service.
4. **The tag batch: run it.**

and asked that the rulings on S40 and S41 wait for Fable. So this work sits on `session-42`, **stacked on the unmerged
`session-41`** (rows merge in order: S40, S41, then this), built on **Opus 5.5**, and it is not a board row yet: Fable adds
row 42 (or folds it) when it closes S40 and S41, writes the decision that records these rulings, and deletes this file.

## 1. Done: the tag batch (item 4)

Run from this desktop checkout on 2026-09-27; `main` equalled `origin/main` (8d8c894), so the batch's
`git reset --hard origin/main` was not needed and not run. The stale remote `s01` (an orphan pointing at the pre-rebuild
merge, D41) was deleted and re-tagged; 38 annotated tags `s01`–`s39` were created from MANUAL_TODO's commands and pushed.
**One command was wrong**: `s06`'s literal SHA read `a71483844338`, an extra `8` — no such object; the S6 merge on `main`
is `a7148384433bb3218027ea9966afdc19b41d12c3` (one match for `^Merge S6 into main`), and the tag points there.
`git ls-remote --tags origin` then listed **39 tags: s00–s20 and s22–s39** (no `s21` command exists in the batch: S21's
two audit branches were never merged, and S22's merge carries `s22`). What Fable still owes the record (MANUAL_TODO's own
"finish the record"): paste the listing under D161, mark every row applied (correcting `s06`'s SHA), and tick S22's board
row from ◐ to ☑ — GALAXY_PLAN §5d's last "done means" item is met.

## 2. Built on this branch (Opus 5.5, 2026-09-27)

**Ruling 2 — rows 32 and 34 take the blind windows (b275c1e).** `docs/AUDIT_III_BLIND.md` is the blind report, verbatim.
- **Row 32**: [2.7e7, 4.0e7] M☉, the Harris sum 1.716e7 L☉ at Baumgardt, Sollima & Hilker 2020's M/L_V ≈ 1.9 (§3.3,
  quoted in `_HARRIS_BLIND_READ`); the old window (BHG16's 1.4 ± 0.5, 1.54–3.26e7) kept in the note as the record. Still a
  recorded miss (**#98**), its reason rewritten: 7.13e7 is 0.25 dex above the new top, 0.34 above the centre (0.47 above
  the old centre); η M_halo 3.19e7 now falls *inside* the window, which sharpens #98's finding.
- **Row 34**: McKee & Williams 1997's (2.6 ± 1.3)e53 s⁻¹ → [1.3e53, 3.9e53]; the model's 1.6527e53 **passes**. Its
  recorded miss is removed with the reason written in its place (a miss that starts passing fails the run, #29);
  **debt #100 stays open** on the 0.71 Q/SFR. Both texts carry the disclosure: the builder knew the model's number and
  chose Bennett's window, the blind reader did not. `test_s22_rulings` adds row 34 to `joined_since` with its conditioning.
- Pins: specs 11/20/5 → **12/19/5 of 36** (both models); `FAILED` loses 34; `DEBTS` loses 100 (the debt, not the row);
  `test_globular_clusters` pins the new window and M/L 1.6–2.2 on the sum.

**Ruling 1 — the forbidden lines from Byler et al. 2017's grid (644750b).**
- `tools/fetch_nebular.py` → `model/galaxy/data/nebular_lines.npz` (16 KB) from FSPS `nebular/ZAU_ND_prsc.lines` at commit
  `bd187a0d07dac17b55c4dc7c60d83f63694c1b4e` (PARSEC-ionized, dust-free; MIT, attributed in the README; the Byler et al.
  reference checked on arXiv:1611.08305 — authors and DOI; units "Lsun/Q" and the file order read in FSPS's
  `sps_setup.f90`, the interpolation in `add_nebular.f90`). Axes 11 log Z (−1.98…+0.2) × 10 ages (0.5–20 Myr) × 7 log U
  (−4…−1); six lines kept (Hβ, [O III] 5007, Hα, [N II] 6583, [S II] 6716, 6731).
- The nebular stage reads it per region at log(Z/Z☉) = its [α/H] (the stage's oxygen − 8.69), the cluster's age and the
  region's own log U; trilinear in log L as FSPS does, **clamped at the edges** (FSPS extrapolates in Z and U). Publishes
  `hii_{oiii_5007,nii_6583,sii_6716,sii_6731}_ratio` (line over the grid's own Hα, so the region's Case B Hα carries the
  photon budget), per-ring `*_surface_brightness_hii` (the census's Hα-weighted ratio per ring, empty rings interpolated),
  and `hbeta_surface_brightness_{hii,dig}` by the Case B decrement. The diffuse gas gets no forbidden line (named).
- `/api/render`: components `lines_hii` (R, φ, filter; the regions' layer, placed by the contrast) and `lines_dig`
  (R, filter; Hβ), each line through each curve at its own wavelength, per-line transmissions in the header;
  `absent.lines` is now `[]`. The viewer sums them into the field's HII and diffuse layers, and colours each resolved
  region by its own lines (`region.ts regionLineColour`; the HII row's spare slots 9–11). The inventory (`test_v4`) moves
  `hii_balmer_decrement` and the four ratios to DRAWN.
- **Recorded, not judged** (`test_nebular`): 26.4% of the default regions are richer than the grid's +0.2 dex and read the
  edge; 2.6% are younger than 0.5 Myr and read the floor; every log U is inside. Hα-weighted [O III]/Hα 0.477, [N II]/Hα
  0.131, [S II] 0.053 + 0.041; per ring [O III]/Hα 0.02 at 4 kpc → 0.72 at 12, [N II]/Hα 0.19 → 0.09 — the metallicity
  gradient's direction. No acceptance row reads these; comparing them to Milky Way HII-region line ratios would need a
  sourced target (candidate row or debt for Fable). `[inferred]` in the stage's docstring: the grid's gas carries its own
  abundance pattern (N/O included) at n_H = 100 cm⁻³, not the model's published N/H, S/H or density.

**Ruling 3 — HST WFC3 as a named instrument (17c57ef).**
- `tools/fetch_filters.py` → `frontend/src/galaxy/instruments.json` (48 KB, generated, do not hand-edit): SVO's
  `HST/WFC3_UVIS2.*` system throughputs, two sets — **WFC3** (F814W, F555W, F438W) and **WFC3 SHO** (F673N, F656N, F502N)
  — each curve on 241 points, peak one; the largest resample error 1.07% of peak (F438W). SVO's acknowledgement and
  references (read on its front page) in the README. SVO does not state air or vacuum: the tool records each line's share
  both ways — the largest difference is F673N at [S II] 6716, 0.983 vs 0.958. Through the model: Hα 0.962 in F656N,
  [O III] 0.903 in F502N, [S II] 0.98/0.86 in F673N, no [N II] in F656N (`test_render`).
- **The PSF**: under either instrument set the stars are drawn with the Airy pattern of a circular aperture, per channel at
  a radius in proportion to the filter's pivot (λ/D), J1 from its integral definition (vitest checks it against the power
  series and finds the Rayleigh zero at 1.2197π). Float texture, so rings at 1% survive; sprite 25 px, the red core's first
  dark ring at 0.16 of its radius — a display choice `[inferred]` (the view has no distance to the galaxy). HST's central
  obscuration and its four spikes are not drawn. In the browser the rings are faint under the bloom at 0.48 kpc across;
  the stars read slightly larger and redder-edged than under RGB. JWST (NIRCam + hexagonal PSF) is not built.
- The render's query string carries the sampled curves (≈ 20 KB of URL per request for three 241-point curves); it
  works against the stdlib server here, a note for a proxy with a shorter URL limit (the Azure deployment).

**After the rulings, asked by the owner ("anything you can do on the render in the meantime?") — two more.**

- **A long query travels as a POST body (5872162).** The server takes a form-encoded body as the rest of the query and
  answers exactly as the GET (411 / 413 past 1 MiB / 415; nothing written); the transport sends any query past 4 KB
  that way. It exists for the deployment: WFC3's curves made a ≈ 20 KB render URL. Tested through the real JS transport
  against the server (`test_api`), and seen in the browser (WFC3 SHO's render and table went as bare-URL POSTs, 200).
- **P6 — proposed, for Fable to ratify or overturn: stars and clusters drawn through the filter set (e29868f).** Until
  now a point in "light" was its bolometric luminosity in the declared blackbody ramp's hue, whatever the filter set
  (the panel said "always in broadband colour") — so in SHO the stars were broadband over a narrowband field, against
  RENDER_PHYSICS §2a's one mechanism. New route `/api/blackbody` (runs no stage; timed): each filter's share of a
  blackbody's light on 193 temperatures (1000–100 000 K) and the white point's, read log-share linear in log T (a line
  in the share itself missed by 16% at 1000 K; this is within 2.2e-3 everywhere, `test_render`). The viewer draws a
  point's channel k as L × share_k(T) / white_k (`colors.ts channelShare`); the ramp stays until the table arrives.
  **What it changes** (RGB): a 5800 K star (1.02, 0.96, 0.85) — as before; 3000 K (0.39, 0.20, 0.07); 10 000 K (0.66,
  0.79, 1.11); 30 000 K (0.06, 0.09, 0.19). The giants and the O stars are dimmer through optical filters than their
  bolometric light, as through a camera; the exposure rule (`exposureFor`) still ranks stars by bolometric L — a
  question for the ruling. `[inferred]`: a star is a blackbody at its `star_temperature` (the ramp assumed the same;
  the stars' own isochrone magnitudes are not published per star). To overturn: pass no table (`colorsFor`'s last
  argument) and restore the panel's sentence.

## 3. The gate (2026-09-27, Opus 5.5; EXIT lines read from the logs)

- `uv run python -m galaxy.specs`: **EXIT=0**; **12 pass / 19 fail / 5 not-yet-computable of 36** in both models (row 34
  joined; all 19 failures recorded misses).
- `uv run pytest -q`: **EXIT=0**.
- vitest 16 files / 118 tests; `tsc -b` clean; the frontend build clean.
- **In a browser** (a scratch server on :8018 serving the built `dist/`, stopped; :5173 untouched): SHO and HOO field and
  region views draw with the lines (header `absent.lines` = []; `lines_hii` carries each line's transmission); WFC3 and
  WFC3 SHO draw, the region's stars under the Airy sprite; no console errors.
- `tools/timings.py`: **EXIT=0**; the render grew by the two line components, the clusters route by the four ratios:

```
endpoint                 cold s   warm s    c/w      bytes  stages
------------------------------------------------------------------
clusters: one sector*    1.0695   0.0022 487.46     70,648  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
clusters: whole disc*    1.6253   0.0138 117.38  4,128,488  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
render: whole, rgb*      2.1545   0.2401   8.97  6,940,400  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,light,vertical_alpha,ism,dust,clouds,clusters,nebular
render: one region*      2.1370   0.2210   9.67     27,032  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,light,vertical_alpha,ism,dust,clouds,clusters,nebular
```

(Cold times up ~0.3–0.5 s against S41's run on the same machine; part of that is the grid's first load, part load on the
machine — not investigated.)

**Re-run after the POST and P6 (same day):** `uv run pytest -q` **EXIT=0**; vitest 16 files / 120 tests; `tsc -b` clean;
`tools/timings.py` **EXIT=0** — the new route `blackbody: rgb` 0.0041 s cold, 17 KB, no stage; the renders 2.44 / 2.40 s
cold (unchanged by this work: nothing in the render route moved). Specs untouched by it (12/19/5).

## 4. What Fable owes for S42 (after S40 and S41 are closed and merged)

1. Merge or rebase `session-42` onto the closed `session-41` if S40's or S41's review changed anything. Conflicts to
   expect: `tests/test_v4.py` (the inventory; S42 moved five cluster columns to DRAWN), `frontend/src/galaxy/region.ts`
   (the HII row's slots 9–11), `docs/HANDOFF_*`.
2. **A decision recording the owner's rulings of 2026-09-27** (the four in the header, in the owner's words) and what S42
   built on them: D184's grid fetched and read, A3-7's windows adopted (rows 32, 34), #108's instrument half built.
3. The debt register: **#98** (row 32's reason now reads the new window), **#100** (row 34 passes, the debt stays open on
   the 0.71 Q/SFR — or re-scope it), **#108** (the instrument half done; the per-filter dust half was V2's — discharge?).
   Candidates: the line ratios have no acceptance target (a sourced Milky Way HII-region [N II]/Hα, [S II]/Hα or
   [O III]/Hβ gradient would make one); a quarter of the regions read the grid's metal-rich edge; the diffuse gas's
   forbidden lines (the grid does not model its field); JWST's set and PSF; HST's obscuration and spikes.
4. D161's tag listing (§1), MANUAL_TODO rows marked applied with `s06`'s SHA corrected, S22 ◐ → ☑.
5. **Rule on P6** (stars and clusters through the filter set, §2): ratify, overturn, or ratify with the exposure rule
   moved to the filtered light; and on the POST path (an API change a decision should name).
6. Board row 42 if Fable makes one (rulings: the owner, 2026-09-27; build Opus 5.5), LESSONS, RESUMING/BRIEF, the close
   ritual, merge `--no-ff`, push, `verify_clone`, delete this file.
