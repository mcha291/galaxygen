# BRIEF — for S40: V3, region synthesis from the cloud vector (Fable's own row)

**For the session.** Open `session-40` from `main`; read this file, `BUILD_II.md` "V3" (lines 779–786),
`RENDER_PHYSICS.md` §§4, 5 (5a the cloud vector, 5b the cluster object, 5c on-demand resampling — the hierarchy
exists since S32), 6 (clumping: one mechanism, two payoffs), 7 (catalogue against field; region determinism),
8; `stages/clouds.py` (the census's columns: mass, size, Mach, `cloud_density_pdf_width` σ_s, `cloud_source_offset`
and `_angle`, `cloud_density_gradient` and `_gradient_angle`, state), `stages/nebular.py` (per region: R_S,
n_e, T_e, `hii_halpha_emissivity` per volume, the Balmer decrement), `stages/bubbles.py` (per cluster: the
bubble's radius, shell thickness, density, `bubble_shell_emissivity`; per remnant the same), `api/service.py`
(`/api/region` with `level=`, `/api/clouds`, `/api/clusters` — the bubble and HII columns ride on it — `/api/
remnants`, `/api/render` with `level=`), `frontend/src/galaxy/regimes.ts` (`REGIME_KPC` field 25 / stars 4,
`regimeWeights`, `regionAround`), `GalaxyView.tsx` (the star layers), `api.ts` (`loadRegion`, `loadBrightest`,
`loadRender`), `FieldVolume.tsx` (V2's march: the pattern V3 follows for a region volume). Debts from #110,
decisions from D190; MANUAL_TODO's `s39` row takes S39's merge SHA. **Rulings to make before a number is printed
(D113), each recorded in D190:** (1) **the level the view asks for** — a function of the view's width in kpc:
level 0 above the stars handover (4 kpc), 1 below 1 kpc, 2 below 0.25, 3 below 0.06 `[inferred: 4^k the
density]`, or the level at which a cell is at most N pixels wide — state which and why; (2) **the cloud
interior** is synthesised in the shader from the log-normal at the published σ_s: a 3-D noise field whose
one-point PDF is log-normal with that width (a sum of octaves exponentiated), seeded by the cloud's cell-and-
index path so the same cloud is the same at every approach, with the density gradient tilting it and the
Strömgren radius carving the HII cavity around the source offset — the pillars are the shadows of clumps the
front did not eat, drawn by marching from the source; (3) **shells** from the bubble and remnant columns as
thin spheres of the published shell thickness and emissivity (limb-brightened by the march, §4); (4) **the
region's light** is the region's own: `/api/render` at the level for the stars (already volumetric per cell),
the region's clusters' Hα from `hii_halpha_emissivity` inside R_S, the DIG from the field; the census stars
drawn as points as today at the level's sample.

## What to build
- The viewer's **region regime** below 4 kpc: `regionAround` picks the level; the loads become `/api/region?level=k`
  (stars), `/api/clusters` (clusters with HII and bubble columns), `/api/clouds`, `/api/remnants` for the window;
  a `RegionVolume` component marches cloud volumes (log-normal interiors, cavities, shells) and adds the star points.
- The model side only if a column is missing (name it; every existing field bit-identical). The seed for a
  cloud's noise is its `(cell, index)` — publish nothing new for it (§5a: "the seed is the cell-and-index path").
- **Gate** (BUILD_II V3): RENDER_PHYSICS §7's catalogue-against-field — the region's light integrated over a
  patch (the stars at the level plus the clusters' Hα) equals the field's at that patch (the render at level 0
  over the same window) within the census's Poisson noise, asserted by a Python test that drives the routes and
  integrates without a browser; and **determinism across zoom levels** — a nebula the same at every approach:
  the same cloud's parameters and seed at levels 1, 2, 3 (a test on the routes) and a vitest that the noise
  field for a given seed is bit-identical across two constructions.

## Traps
- No downloads. The owner watches :5173 live: one consistent edit per file; a scratch port for checks.
- Machine: `uv run`; `npm --prefix frontend run test -- --run`, `run build`; the Bash tool fails over ~8 KB;
  cp1252 console; LF newlines; `grep -c` exits 1 on zero matches; `git commit -F -` fails, use a file.
- **Do not merge or delete** the sealed audit branches (MANUAL_TODO §2) or `claude/blissful-poitras-2cbbd3`.

## At close
Board row 40 ☑ (Fable 5.1); `progress.py`; the suite backgrounded, merge gated on its EXIT line; D190; RESUMING
(≤ 120) and this file for **S41 (V4, clusters as objects, instruments, close-out, Opus)**; `MANUAL_TODO.md` row
`s40` with `s39`'s SHA; merge `--no-ff`, push, `verify_clone --ref main` on a quiet machine.
