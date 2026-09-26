# HANDOFF — S40 (BUILD_II V3) built on Opus while Fable's limit is reset

**Why this file exists.** S40 is a Fable row (board row 40). Fable made its design rulings (below, §1) and
began the build on `session-40`; its usage limit ran out mid-session on 2026-09-27. At the owner's request the
build continues on **Opus 5.5** to Fable's rulings, committed and pushed to `session-40`, **not merged**. What
remains for Fable is the part only the orchestrator does: review the build against the gate, write **D190**,
tick board row 40 (model actually used: Fable 5.1 for the rulings, Opus 5.5 for the build), register any debts
from **#110**, rewrite RESUMING and BRIEF for S41, run the close ritual and merge. This file is deleted at that
close; nothing in it is a decision until D190 records it.

## 1. Fable's rulings (written before any number, D113; from the S40 scratchpad design)

- **R1. The level the view asks for.** Level 0 while the view is ≥ 4 kpc across (the stars handover,
  `REGIME_KPC.stars`); then one level per factor four of width: 1 below 4 kpc, 2 below 1, 3 below 0.25
  (`LEVEL_KPC = [4, 1, 0.25, 0.0625]`, `levelFor` in `frontend/src/galaxy/region.ts`) `[inferred: a level-k
  cell is 2^k finer per side than a level-0 cell (~1.6 kpc × 0.2 rad at R₀), so it stays under about half the
  view]`.
- **R2. Where the region regime's light comes from** (RENDER_PHYSICS §7: the region integrates back to the
  field). Stars: `/api/region?level=k` as points (a child holds its parent's stars plus its own at 4^k the
  density, D181 — the cloud of points densifies on approach and no star moves). Clusters' HII regions: spheres
  of radius R_S carrying `hii_halpha_emissivity` per volume, marched so they limb-brighten (§4); the line's
  per-filter weights are `/api/render`'s `components.halpha_hii.transmission` (the viewer holds no physics,
  D5). Bubbles and remnants: thin shells at the published radius, thickness and shell emissivity (they occlude
  nothing — the model gives no shell opacity). Clouds: extinction at the published mean column, made
  log-normal by the noise (R3). **No double counting**: inside the region's window the field's HII component
  fades as the resolved spheres fade in (the `stars` regime weight), as the field's starlight already does.
- **R3. The cloud interior** is a log-normal noise field seeded by the cloud's (cell, index) path (§5a: the
  seed is the path, nothing stored): four octaves of value noise, normalised to unit variance by measurement,
  ρ/ρ̄ = exp(σ_s g − σ_s²/2) at the census's published width, the mean tilted linearly along the published
  gradient `[inferred]`; the HII cavity is the Strömgren sphere around the published source offset; pillars
  are the clumps inside it that survive as extinction, drawn by the march itself.
- **R4. The gate** (BUILD_II V3): catalogue against field — the window's clusters' HII Hα against the field's
  HII Hα from `/api/render?level=k` over the same window, within the census's Poisson noise — and determinism
  across levels: a cloud's and a cluster's columns identical at every level that holds it; the noise field
  bit-identical for a seed.

## 2. Built so far (commits on `session-40`)

- **Model**: one census scalar, `cloud_extinction_v` = 2.9696 mag — the V extinction through a cloud's centre,
  1.4 m_H per hydrogen and Draine's V cross-section per H (`spectra.GRAIN_V_EXTINCTION`, D189). **A finding for
  Fable**: it is one number for every cloud, because the census fixes one surface density (Heyer et al. 2009's
  42 M☉ pc⁻², D181) and a uniform sphere's central column is 3/2 of the mean — mass and radius cancel. It was
  first built as a per-cloud column and changed to a scalar when every value came out equal. Carried in the
  `/api/clouds` header under `scalars`; rule D4 (the audit's lost-scalar count 16 → 17). All earlier fields
  bit-identical is to be confirmed by the gate run below.
- **Transport and loaders**: `clouds`, `clusters`, `remnants` in `interface/transport.js`; `loadClouds`,
  `loadClusters`, `loadRemnants` in `frontend/src/api.ts`.
- **Noise**: `frontend/src/galaxy/region.ts` with `region.test.ts`. Measured on 64 000 points: one octave's
  spread 0.1794; the summed field's 0.2088, 1% over the independent-octave 0.2067 because the octaves share
  lattice corners; normalised by the measurement. The realised log-density spread equals σ_s to 0.1 at 0.8,
  1.4 and 2.0; the mean density ratio sits in 0.8–1.25.

## 3. Still to build (this section is updated as the Opus build proceeds)

- `RegionVolume.tsx` (the march of clouds, cavities, shells) and its wiring in `GalaxyTab.tsx`.
- `tests/test_region_synthesis.py` (R4's two gates).
- The gate run: specs, the full suite, vitest and the build, all EXIT lines recorded here.
