# BRIEF — for S33: BUILD_II Phase 11, clusters as objects (Opus subagent)

**For the orchestrating session.** Open `session-33` from `main`; hand an Opus subagent, in a worktree
(`git checkout session-33`, `git config --worktree core.hooksPath tools/hooks`), this file, `BUILD_II.md`
Phase 11 and Phase 5's "Globular clusters" paragraphs (the unification), `RULES.md`, `RESUMING.md`'s
"Writing a stage", `RENDER_PHYSICS.md` §5b, `stages/clouds.py` (S32's object-class pattern: a census
drawn per cell, `of="cloud"`, level-0 constants with citations), `stages/systems.py` (`materialise`,
the cell grid, `canonical_cell`; do not touch the hierarchy), `api/service.py` (`_clouds` as the
route template), `stages/massive_stars.py` (Q and wind per star). It neither pushes nor writes
DECISIONS.md. Debts from #96, decisions from D182; MANUAL_TODO's `s32` row takes S32's merge SHA.
**Rulings made here (D113):** (a) the cluster mass function is SOURCED — Portegies Zwart, McKee &
Gieles 2010 (ARA&A 48, 431) for dN/dM ∝ M⁻² and its range, with the truncation or Schechter mass if the
review states one — a read-only agent fetches the sentences verbatim; (b) the bound fraction and the
dissolution timescale are SOURCED (Lada & Lada 2003, ARA&A 41, 57: the fraction of embedded clusters
surviving to 10 Myr; a read-only agent fetches it) — otherwise the bound flag is not built and the
report says why; (c) the mass–radius relation is sourced or the radius is not published (e.g. Larsen
2004 / Portegies Zwart 2010's r_h ≈ constant few pc statement); (d) a cluster is **one per cloud in
the blown-open and dispersing states** unless a source gives a cloud-to-cluster efficiency (the star
formation efficiency per cloud, Lada & Lada's ~10% or Murray 2011's ε_GMC — read it); the cluster's
mass is that efficiency times the cloud's mass, capped by the function's upper end.

## What to build
- **`clusters`**: an object class beside stars and clouds (`of="cluster"`, the vocabulary widened, a
  `core/` edit named in the report), drawn per cell by the cell-and-index machinery as clouds are
  (`stages/clouds.py` is the template), a census: `cluster_radius`/`_azimuth`/`_height`, `cluster_mass`,
  `cluster_half_mass_radius`, `cluster_age` (the cloud's), `cluster_bound` (category), `cluster_metallicity`,
  `cluster_ionizing_photons` and `cluster_wind_luminosity` — **the sums over the members the IMF gives it**:
  integrate Q and the wind luminosity per unit mass formed at the cluster's age from the same isochrone
  tables `light.py` integrates (`photometry.ionizing_yield`'s pattern), not a star sample.
- Each cloud in the blown-open or dispersing state points at one cluster: a `cloud_cluster_index`
  column on the cloud census (−1 for none), the cluster's `(cell, index)` name being the cloud's.
- `/api/clusters` by window and level (filter as `/api/clouds` does); a timings row; both models.
- **The Phase 5 hook**: the same mass function integrated over the history with the bound fraction gives
  the mass in surviving old clusters; publish `bound_cluster_mass_total` (a population integral) so Phase
  5 (S34) can check Boylan-Kolchin 2018's η = M_GC/M_halo ≈ (3–4) × 10⁻⁵ against it rather than assert it.
- No new inputs; level-0 constants with citations; about lines name no constant (D5). No acceptance row
  unless a target with an uncertainty is read (D100, #17) — the Milky Way's young-cluster formation rate
  or bound mass only if a source quotes one.

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; rows 1–31 unmoved
(15 = 5.20971, 29 = −7.914, 30 = 0.0176069, 31 = 0.0065332); the cluster census's per-region determinism
(D60) asserted; the clusters' total Q equals the ionizing photons the light stage integrates for stars
younger than the oldest cluster, to a stated tolerance (or the report says why not); every cloud's
`cloud_cluster_index` resolves to a cluster in the same cell; existing pins untouched unless one moves,
then the old number in the comment; new tests on the coarse grid where the claim allows.

## Traps
- The cloud census is seeded on `systems_seed` with streams `("cloud", cell, …)`; use `("cluster", cell,
  …)` so neither reroll touches the other's numbers. Every table over every ring and sector (D60).
- The CellCache splits a response by `Catalogue.counts` in the order asked: return counts in that order.
- Machine: `uv run`; the Bash tool fails over ~8 KB (write scripts to files); cp1252 console; LF newlines;
  `grep -c` exits 1 on zero matches and kills `&&` chains; long runs backgrounded with `EXIT=$?`.
- **Do not merge or delete** the sealed audit branches listed in MANUAL_TODO §2.

## At close (orchestrator)
Core diff first, then tests. Board row 33 ☑ with the subagent's model; `progress.py`; the suite backgrounded,
merge gated on its EXIT line; D182 with rulings (a)–(d), the census's numbers and the Q check; RESUMING
(≤ 120) and this file for **S34 (Phase 5, GCs and the stellar halo, Opus)**; `MANUAL_TODO.md` row `s33`
with `s32`'s SHA; merge `--no-ff`, push, `verify_clone --ref main`.
