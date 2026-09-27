# HANDOFF — S41 (BUILD_II V4) built on Opus ahead of Fable's rulings

**Why this file exists.** S41 is an Opus row (board row 41), normally opened by the orchestrator (Fable) with a
BRIEF whose rulings are made before any number (D113). Fable's usage limit ran out during S40; the owner asked
Opus to do every task it can. So this row was built on **Opus 5.5** on `session-41`, **branched from the unmerged
`session-40`** (rows merge in order), **to rulings Opus proposed and wrote down first (§1)**. Fable ratifies or
overturns them in D191; nothing here is a decision until then. If S40 changes at its review, `session-41` is
rebased or merged onto the reviewed `session-40` before it is closed. Delete this file at S41's close.

## 1. Proposed rulings (written before the build; for Fable's ratification)

- **P1. Clusters as objects (BUILD_II V4: "cluster objects drawn as objects").** A cluster is drawn as a point of
  light at its position, as a star is, with its own light: two new columns on the `clusters` stage,
  `cluster_luminosity` (L☉, bolometric) = mass × the light per mass formed at the cluster's age and [Fe/H], and
  `cluster_light_temperature` (K) = the correlated colour temperature of the same population's colour — both from
  the tables the light stage integrates (`photometry.population_at`, `correlated_temperature`), never a star sample
  (B8). The alternative, a cluster's light through the filter set by `/api/render`, is V1's machinery at a finer
  grain and is left for later: a point's colour is the declared ramp of its temperature, as for stars (A9, D5).
  Its HII sphere and bubble shell are S40's region volume.
- **P2. Named-instrument PSFs are not built**: the filter curves are files (SVO), a download the owner has not
  approved (#108); the named-instrument mode waits on that word. Recorded, not guessed.
- **P3. The model toggle** (`azimuthal` against `basic`): exists since S27; V4's gate is that both models draw the
  field and the region regimes without error — checked in a browser on a scratch server.
- **P4. The tag batch** is the owner's (C2e: sessions do not tag); MANUAL_TODO carries every queued command.
- **P5. The #69 gate — every published field shown or ruled invisible** — extended from scalars to the object
  classes: a test lists every `of="cloud" | "cluster" | "remnant"` column and asserts each is either read by the
  viewer (the region volume's object table or the cluster points) or says in its about why it is not drawn
  (the D4 sentence's object-class twin). Columns the viewer does not read yet get that sentence, not a drawing
  invented to use them.

## 2. Built (commits on `session-41`, Opus 5.5)

| commit | what |
|---|---|
| 2f3bf9b | this file, the proposals written before the build |
| 0bc8fe9 | **P1 model**: `cluster_luminosity` (L☉) = mass × `photometry.population_at` light per mass at the cluster's age and [Fe/H]; `cluster_light_temperature` (K) = `correlated_temperature` of the same colour, the blackbody ramp as `star_temperature` has. Default grid: L 857 – 2.1 × 10⁸ L☉, median 1.7 × 10⁵; L/M median 185 L☉/M☉; T 10 200 – 30 600 K, median 13 900; the youngest (< 4 Myr) median 27 800 K, the oldest (> 15 Myr) 11 100 K |
| 58eaab9 | `session-40` merged in (its remnant-shell fix, found while planning this row) |
| 2f67b74 | **P1 viewer**: `colors.lightColors` generalises `photometricColors` to any object with a luminosity and a blackbody temperature; the galaxy tab loads the window's clusters once at the view's level, shares them with S40's region volume, and draws them as a point layer (photometric painting, the stars regime's weight); **P5**: `tests/test_v4.py` — the cluster light's identity with the tables (P1), and the object-column inventory: 25 columns drawn, 39 not drawn yet (8 cloud, 24 cluster, 7 remnant) |

## 3. The gate (2026-09-27, Opus 5.5; EXIT lines read from the logs)

- `uv run python -m galaxy.specs`: **EXIT=0**; 11 pass / 20 fail / 5 not-yet-computable of 36 in both models, unchanged.
- `uv run pytest -q`: **EXIT=0**, the three known skips.
- vitest 16 files / 111 tests; the frontend build clean.
- **P3 in a browser** (a scratch server on :8018 serving the built `dist/`, stopped; :5173 untouched): `basic` at 1.38 kpc
  across (level 1) draws the region's stars and the cluster points over the bulge's glow; `azimuthal` (switching model
  reopens checkpoint 4, the app's existing behaviour) draws the field and, at 0.88 kpc, stars, cluster points and an
  HII region in its shell; no console errors; one `/api/clusters` request per window (shared with the region volume).
- **P5**: the scalar half of #69's gate is `test_audit.py::test_s21b…` (17 ruled invisible under rule D4); the object half
  is the inventory above, which fails if a new object column is left unplaced.
- `tools/timings.py`: **EXIT=0**; the clusters route grew by the two light columns:

```
endpoint                 cold s   warm s    c/w      bytes  stages
------------------------------------------------------------------
clusters: one sector*    0.8061   0.0014 574.60     63,744  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
clusters: whole disc*    1.2350   0.0097 127.74  3,716,480  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,vertical_alpha,ism
render: whole, rgb*      1.6158   0.1705   9.48  5,205,784  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,light,vertical_alpha,ism,dust,clouds,clusters,nebular
render: one region*      1.5351   0.1655   9.28     20,912  halo,disc,assembly,bar,pattern,sfh,chemistry_dtd,light,vertical_alpha,ism,dust,clouds,clusters,nebular
```

## 4. What Fable owes for S41 (after S40 is closed and merged)

1. Rebase or merge `session-41` onto the closed `session-40` if S40's review changed anything.
2. Ratify or overturn P1–P5 in **D191**; for P5, rule on the 39 not-drawn columns — draw, or give each declaration the
   object-class twin of rule D4's sentence (a candidate debt if deferred).
3. Board row 41 (**rulings: Opus 5.5, proposed; ratified by Fable 5.1** — or as Fable records it; build Opus 5.5);
   MANUAL_TODO `s41` row with `s40`'s SHA; LESSONS; RESUMING and BRIEF for the maintainer (BUILD_II's end: V4 is the last
   row); the suite's EXIT line; merge `--no-ff`; push; `verify_clone`; delete this file.
4. Not built, by P2 and P4: the named-instrument PSFs (a filter-file download, the owner's word, #108) and the tag batch
   (the owner's, C2e). The merge commit 58eaab9 carries git's default message without the co-author line; it is pushed,
   so it was left as is (C2a).
