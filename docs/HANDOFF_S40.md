# HANDOFF — S40 (BUILD_II V3) built on Opus while Fable's limit is reset

**Why this file exists.** S40 is a Fable row (board row 40). Fable made its design rulings (§1) and began the
build on `session-40`; its usage limit ran out mid-session on 2026-09-27. At the owner's request the build
continued on **Opus 5.5** to Fable's rulings, committed and pushed to `session-40`, **not merged**. What remains
is what only the orchestrator does (§5). This file is deleted at that close; nothing in it is a decision until
D190 records it.

## 1. Fable's rulings (written before any number, D113; from the S40 scratchpad design)

- **R1. The level the view asks for.** Level 0 while the view is ≥ 4 kpc across (the stars handover,
  `REGIME_KPC.stars`); then one level per factor four of width: 1 below 4 kpc, 2 below 1, 3 below 0.25
  (`LEVEL_KPC = [4, 1, 0.25, 0.0625]`, `levelFor` in `frontend/src/galaxy/region.ts`) `[inferred: a level-k
  cell is 2^k finer per side than a level-0 cell (~1.6 kpc × 0.2 rad at R₀), so it stays under about half the
  view]`.
- **R2. Where the region regime's light comes from** (RENDER_PHYSICS §7: the region integrates back to the
  field). Stars: `/api/region?level=k` as points. Clusters' HII regions: spheres of radius R_S carrying
  `hii_halpha_emissivity` per volume, marched so they limb-brighten (§4); the line's per-filter weights are
  `/api/render`'s `components.halpha_hii.transmission` (the viewer holds no physics, D5). Bubbles and remnants:
  thin shells at the published radius, thickness and shell emissivity. Clouds: extinction at the published mean
  column, made log-normal by the noise (R3). **No double counting**: inside the region's window the field's HII
  component fades as the resolved spheres fade in.
- **R3. The cloud interior** is a log-normal noise field seeded by the cloud's (cell, index) path (§5a):
  ρ/ρ̄ = exp(σ_s g − σ_s²/2) at the census's published width, the mean tilted linearly along the published
  gradient `[inferred]`; the HII cavity is the cluster's Strömgren sphere; pillars are the clumps inside it that
  survive as extinction.
- **R4. The gate** (BUILD_II V3): catalogue against field — the window's clusters' HII Hα against the field's
  HII Hα from `/api/render?level=k` over the same cells, within the census's noise — and determinism across
  levels: a cloud's and a cluster's columns identical at every level that holds it; the noise bit-identical.

## 2. What was built (commits on `session-40`, Opus 5.5)

| commit | what |
|---|---|
| 37b9784 | `cloud_extinction_v` census scalar; the census routes in `interface/transport.js` and `frontend/src/api.ts`; `region.ts` noise with vitest; this file |
| d909717 | `tests/test_region_synthesis.py`: R4's two gates |
| ae9644f | the census routes name every row by (cell, index); a level filter recomputes the header's counts |
| d4b23c5 | `RegionVolume.tsx`, the field's HII fade inside the window, `GalaxyTab` wiring, the object table |
| (this) | R2's **remnant shells**, missing from d4b23c5 (found while planning S41): remnants join the shell list; a Sedov-phase remnant's NaN emissivity draws nothing (D185) |

- **Model: one scalar, no new column.** `cloud_extinction_v` = 2.9696 mag, the V extinction through a cloud's
  centre: 1.4 m_H per hydrogen and Draine's V cross-section per H (`spectra.GRAIN_V_EXTINCTION`, D189). It is one
  number for every cloud, because the census fixes one surface density (Heyer et al. 2009's 42 M☉ pc⁻², D181) and
  a uniform sphere's central column is 3/2 of the mean, so mass and radius cancel. First built as a per-cloud
  column and changed to a scalar when every value came out equal. Carried in the `/api/clouds` header under
  `scalars`; rule D4 (test_audit's lost-scalar count 16 → 17).
- **A defect found and fixed (since S32).** At a level above 0 the census routes kept the level-0 cells' counts
  in their header after filtering the rows: the clouds of r 7–9, φ 0–0.4 at level 2 returned 155 rows under
  counts summing to 257, so no client could name a row. `service._named` now adds int64 `cell` and `index` columns
  to `/api/clouds`, `/api/clusters` and `/api/remnants` (taken before any filter, so a kept row keeps its name),
  and `_in_children` recomputes the counts from the rows it keeps. Tested in `test_region_synthesis.py`.
- **The noise** (`region.ts`): four octaves of value noise, a 32-bit integer hash (`Math.imul`, so the shader's
  `uint` arithmetic draws the same field; a float64 product of a large seed had lost its low bits). Measured on
  64 000 points: one octave's spread 0.1794; the summed field's 0.2088, 1% over the independent-octave 0.2067
  because the octaves share lattice corners; the field is divided by the measured value. Realised log-density
  spread equals σ_s to 0.1 at σ_s = 0.8, 1.4, 2.0; mean density ratio 1.06–1.12 (a sum of smoothed uniforms has
  lighter tails than a Gaussian; bounds 0.8–1.25 asserted).
- **The viewer.** `RegionVolume` marches, per pixel and front to back (objects sorted by distance from the eye on
  the CPU each time the camera moves), the window's clouds (seeded log-normal interiors, the cavity carved by the
  cloud's cluster, pillars where the density exceeds e^σ_s inside it), HII spheres (uniform emissivity over the
  chord, limb-brightened) and bubble shells (the chord less the hollow's). A display budget of 256 objects (128
  heaviest clouds, 64 brightest regions, 64 brightest shells), stated. Emission adds to the frame; the clouds'
  transmission multiplies what is behind them in a second pass. The field's HII fades by the stars weight inside
  the window. The level follows the view (`levelFor`). Checked on a scratch server (:8018, the built `dist/`, now
  stopped; :5173 untouched): at 0.88 kpc across, level 2, two HII regions draw as bright spheres inside
  limb-brightened shells; no console errors. One bug found there and fixed: the transmission target was cleared
  to black, so the multiply pass blacked out everything outside the objects' box; it clears to white now.

## 3. The gate's numbers

- **Catalogue against field** (`test_region_synthesis.py`): the clusters' HII Hα over the field's —
  **0.9801** for the disc at level 0 (12 597 clusters, census noise 0.061) and **0.9744** for r 4–12, φ 0–2 at level
  1 (2 499 clusters, noise 0.138), both inside 3 × noise + 0.02 (D184's galaxy-wide 1%).
- **Recorded, not gated — a finding for Fable:** small windows read low: **0.6745** (r 6–10, φ 0–1.2, level 1, 832
  clusters, noise 0.227) and **0.5107** (r 7–9, φ 0–0.8, level 2, 246 clusters, noise 0.246). The HII luminosities
  are heavy-tailed (a few bright regions carry the sum), so a window of a few hundred clusters usually reads low and
  occasionally far high, and the realised √ΣL²/ΣL understates that spread. Fable rules whether R4's gate is met at
  the windows that matter to a view, or whether it wants a different statistic (e.g. the median over many windows).
- **Determinism across levels:** over cell 300 the 58 clouds and 42 clusters `/api/clouds` and `/api/clusters`
  return are identical, column for column, at levels 0, 1, 2 and 3.
- **The full run** — specs, the full suite, cold timings — is below (§4), EXIT lines read from their logs.

## 4. Gate run (2026-09-27, `session-40` at d4b23c5, Opus 5.5; EXIT lines read from the logs)

- `uv run python -m galaxy.specs`: **EXIT=0**, "specs: OK"; **11 pass / 20 fail / 5 not-yet-computable of 36 in both
  models**, unchanged from S39; graph, preflight, determinism and convergence OK.
- `uv run pytest -q`: **EXIT=0**, the three known skips (test_systems ×2, debt #27; test_viewer, no chromium).
- vitest 16 files / 110 tests green; `npm --prefix frontend run build` clean (the chunk-size warning only).
- `uv run python tools/timings.py`: **EXIT=0**. The census routes grew by the two name columns (clusters whole disc
  3.51 MB; clouds 2.55 MB); no new route, so no new row. As printed:

```
endpoint                 cold s   warm s    c/w      bytes  stages
------------------------------------------------------------------
region: one sector*      0.4663   0.0008 605.29     44,096  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
system: one star*        0.4618   0.0160  28.84      3,608  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
clouds: one sector*      0.4069   0.0015 268.85     42,816  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
clouds: whole disc*      0.6459   0.0077  84.13  2,549,688  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
clusters: one sector*    0.7982   0.0013 604.19     60,280  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
clusters: whole disc*    1.0832   0.0100 108.74  3,510,456  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
remnants: one sector*    0.4549   0.0009 499.36      6,648  halo,disc,assembly,sfh,chemistry_dtd,supernovae,vertical_alpha,ism
remnants: whole disc*    0.5261   0.0031 171.14    171,680  halo,disc,assembly,sfh,chemistry_dtd,supernovae,vertical_alpha,ism
render: whole, rgb*      1.4881   0.2531   5.88  5,205,784  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,light,vertical_alpha,ism,dust,clouds,clusters,nebular
render: one region*      1.5298   0.1660   9.21     20,912  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,light,vertical_alpha,ism,dust,clouds,clusters,nebular
```

## 5. What Fable still owes for S40

1. Review the build against R1–R4 and the gate (§3), core diff first (`service.py` `_named`/`_in_children`,
   `clouds.py` `central_extinction_v`, `RegionVolume.tsx`, `region.ts`).
2. Rule on the small-window finding (§3) and on two departures from R2, both stated here:
   - **Stars stay on the prefix-scaled level-0 sample**, not `/api/region?level=k`: picking a star opens its system
     by (cell, index) read from the header, and level-k rows are named by `level`, `cell`, `index` columns the picker
     does not read yet. The prefix-scaled sample already densifies on approach with no star moving (D167); switching
     is one call plus the picker's naming, not built.
   - **The clouds' transmission multiplies the whole frame behind them**, stars in front of a cloud included, because
     the region composites as a screen-space pass (an approximation of one volume; a single march of field and region
     together is the exact form).
3. Write **D190**; register debts from **#110** — candidates: the noise synthesis and the pillar rule are stated
   shapes (`[inferred]`), the display budget, the two R2 departures, the composite approximation, the small-window
   statistic; tick board row 40 (**rulings Fable 5.1, build Opus 5.5**); LESSONS (the S32 header-count defect lived
   seven sessions because no test compared header to body); RESUMING and BRIEF for **S41**; MANUAL_TODO `s40` row with
   `s39`'s SHA `8d8c89475086421c77c13dace70cd9149c2f7564`; progress.py; the suite's EXIT line; merge `--no-ff`; push;
   `verify_clone` on a quiet machine; delete this file in the close commit.

## 6. S41 (V4, Opus) — not started, and why

S41 depends on S40 being reviewed and merged (rows merge in order), and its brief carries rulings that are the
orchestrator's to write. BUILD_II's V4: cluster objects drawn as objects (Phase 11) — **partly done by S40**, whose
region volume draws each cluster's HII sphere and bubble shell; the named-instrument PSFs (their filter curves are a
download: the owner's word, #108); the model toggle for `azimuthal` against `basic` (the header's toggle exists since
S27; V4's gate is that both models draw); the tag batch attempted again from the desktop (the owner's: 15 queued tags
in MANUAL_TODO); the maintainer's RESUMING/BRIEF. Its gate — every published field of both models shown or ruled
invisible (#69's rule) — is already asserted for scalars by `test_audit.py::test_s21b…` (17 ruled invisible); the
object classes cloud, cluster and remnant now reach the viewer only partly through the region volume, which S41
should state column by column.

## 7. Still owed by the owner (unchanged)

The Byler/FSPS nebular grid download (D184), rows 32 and 34's blind windows (D186), the instrument filter files
(D188), and the tag batch.
