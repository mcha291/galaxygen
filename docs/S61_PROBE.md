# S61_PROBE — the S60 censuses measured by the clustering instrument (BUILD_III Phase L1, D220 step 2)

**A builder's measurement, for the lead's ruling; no conclusion about what the model should do is drawn here.**
Every number below was measured in this worktree on 2026-10-13. The model measured is `session-61` at
**`f73668a`** (S60's model; D220 part I's ring-first draw is not in it). The instrument is
`model/galaxy/specs/clustering.py` at `c48bceb` (with `tests/test_clustering.py`). The probe scripts and their JSON
output (every bin's 1 + omega and DD) are in the builder's scratchpad, not in the repository.

## How it was measured

- **Positions**: the published columns, face-on, `x = R cos phi`, `y = R sin phi` (pc): `cloud_radius/azimuth`,
  `cluster_radius/azimuth`, `bright_star_radius/azimuth`. Clouds and clusters are the run's published catalogues;
  the bright stars are `bright.materialise_bright(BrightGalaxy(run fields), systems_seed, all finest cells, l_min)`
  with `l_min` from `BrightGalaxy.threshold(all cells, 20 000)` - the stage's own selection rule asked for 20 000
  stars instead of 3 162 (default galaxy: log L_min = 4.22, 19 613 stars; ngc_4414: 4.04, 20 079).
- **Galaxies**: the default inputs; `templates.overrides(TEMPLATES["milky_way"])` (two pins on the defaults);
  `templates.overrides(TEMPLATES["ngc_4414"])`. Model `galaxy.models.DEFAULT`, production grid. Each run with the
  layer on and with `run(..., layer=False)`.
- **Footprint A**: an annulus over the radial range of the census's cells with a positive expectation. For clouds and
  clusters: the level-0 rings where `clouds.expected_counts(...).sum(axis=1) > 0`; for the bright stars: the finest
  rings with a positive expected count above `l_min`. **In every run both ranges are the whole grid, 0.0375-29.9625
  kpc** (the grid's own edges). Clusters are measured in their clouds' annulus.
- **Footprint B**: a square of side 6 kpc centred on (R_SUN, 0) = (8.2, 0) kpc (`solar_pointing(c["R_SUN"])`, the
  same for every galaxy).
- **Randoms**: uniform in area in the footprint, **10 times** the data inside it, seed 61; RR summed over disjoint
  slices of at most 50 000 randoms in a fixed random order (`RR_SPLIT`; the column N_r; DR uses every random).
- **Control** (footprint A only): the same census materialised from the run's fields under the four next values
  of `systems_seed` (`seed + 1 ... seed + 4`), pooled, in **the same layer setting as the data** (layer on against a
  layer-on control as the brief asks; layer off against a layer-off control, the law the layer-off census is drawn
  from). Clouds: `clouds.materialise_clouds(fields, R, s, c, texture=True)`; clusters: `clusters.materialise_clusters`
  on those clouds; bright stars: `materialise_bright(g, s, cells, l_min)` at the same `l_min`. The control is about
  four times the data (N_r column), not ten.
- **Bins**: 20 logarithmic from 30 pc to 5 kpc. **Fits**: `1 + omega = A (r/300 pc)^alpha`, least squares in log-log
  over the bins centred in [100, 2000] pc (default), [40, 800] pc (Grasha 2018's) and [100, 3000] pc (Grasha 2019's),
  bins with DD > 0 and 1 + omega > 0; "+-" is the OLS standard error of alpha; rms in dex. The broken law: two laws
  over 30-3000 pc, the break at the bin edge of least total squared error, at least three bins a side.
- **Ages**: clusters `cluster_age` (Myr) <= 10 and > 10; clouds `cloud_mass` >= 1e5 Msun; bright stars
  `bright_star_age` (Gyr x 1000) in [0, 20), [20, 40), [40, 100), [20, 100), >= 100 Myr.
- **texture_seed spread**: the default galaxy, layer on, re-run with `texture_seed` 1 and 2 (default 0).

## The instrument, held first (tests/test_clustering.py, 7 tests, about 13 s of calls)

- Pair counts equal brute force (auto and cross) on 900/700 points over many grid cells.
- Poisson points in an annulus: 1 + omega = 1 within 4 sigma in all 20 bins, slope within 4 standard errors of 0.
- **The anchor, a Thomas process** (clumps at uniform centres, density n_c = 1e-6 pc^-2; Poisson(20) members;
  Gaussian sigma = 100 pc): derived `1 + omega(r) = 1 + exp(-r^2/4 sigma^2) / (4 pi sigma^2 n_c)`, compared as the
  bin's pair-weighted mean. **It held** in every bin with signal (30 pc to about 350 pc, prediction 7.7 at the first
  bin): scratch runs on three seeds gave |z| < 2.2 in all of them once the noise included the Poisson number of
  clump-centre pairs per bin; without that term one seed's bins at 300-600 pc sat 15-30 "sigma" off - the noise
  model was incomplete, not the estimator. The formula's prefactor was not changed.
- A control drawn from the data's own law (an exponential disc) returns 1 within noise. Against uniform randoms
  the same disc reads a plateau of A int S^2 / (int S)^2 = 3.178 (quadrature) at small r, matched within noise to
  300 pc: **a smooth radial profile raises the amplitude and barely tilts the slope** (-0.03 over 100-2000 pc). My
  first draft asserted a steep slope there; the measurement showed the expectation was wrong, and it was replaced by
  the derived plateau.
- **A defect found by the probe and fixed** (`c48bceb`): RR summed over *consecutive* slices of a control in its
  catalogue's (ring) order counted pairs within radial ranges only, and every control larger than 50 000 points
  read a flat 1.05-1.16 at every scale. The slices are now drawn in a fixed random order; a test with a
  radius-sorted control in 4 000-point slices holds 1 within noise (1.83 at every scale without the fix). All the
  numbers below are from the re-run after the fix.
- **Cost** (this machine, one process alone): 20 000 points against 200 000 randoms in a 1-16 kpc annulus - RR
  7.6 s (50 000-point slices), DD + DR 7.4 s; against 100 000 randoms 4.2 s + 2.9 s. In the probe (four processes
  at once), the default galaxy's 16 749 clouds against 167 490 randoms took 5.2 s including RR; against their
  66 693-point control 12.0 s (a concentrated control has more close pairs); every footprint-B row under 1 s.

## Model costs as measured (four probe processes running at once)

| run | run() s | clouds+clusters, 4 control seeds s | bright catalogue s | 4 bright control seeds s |
|---|---|---|---|---|
| default on | 30.4 | 10.3 | 39.0 | 124.0 |
| default off | 5.3 | 1.8 | 5.0 | 19.1 |
| milky_way on | 37.4 | 10.9 | 40.3 | 126.4 |
| milky_way off | 5.0 | 1.7 | 5.1 | 18.8 |
| ngc_4414 on | 27.1 | 4.3 | 25.5 | 93.9 |
| ngc_4414 off | 5.8 | 1.4 | 6.3 | 23.2 |

## The censuses' sizes and what surprised

| run | clouds | clouds >= 1e5 | clusters | clusters <= 10 Myr | clusters in another level-0 ring than their cloud | cluster-cloud offset median / max (pc) | bright (20-40 / 40-100 / >100 Myr) |
|---|---|---|---|---|---|---|---|
| default on | 16 753 | 2 552 | 12 916 | 6 452 | 133 | 9.9 / 265 | 19 613 (13 138 / 2 109 / 4 366) |
| default off | 16 754 | 2 515 | 12 923 | 6 415 | 0 | 0 / 0 | 19 601 (13 062 / 2 189 / 4 350) |
| milky_way on | 16 716 | 2 544 | 12 853 | 6 406 | 126 | 9.9 / 265 | 19 546 (13 153 / 2 153 / 4 240) |
| milky_way off | 16 754 | 2 515 | 12 923 | 6 415 | 0 | 0 / 0 | 19 601 (13 062 / 2 189 / 4 350) |
| ngc_4414 on | 6 548 | 1 258 | 5 012 | 2 391 | 72 | 10.6 / 255 | 20 079 (11 184 / 2 186 / 6 709) |
| ngc_4414 off | 6 534 | 1 267 | 5 018 | 2 417 | 0 | 0 / 0 | 20 055 (11 209 / 2 131 / 6 715) |

- **Footprint A is the whole grid** in every run: the clouds' expectation and the bright stars' are positive out to
  the last ring (29.96 kpc). Against uniform randoms in that annulus the disc's radial profile dominates the
  amplitude: layer off, fitted A at 300 pc is 7.6-15.5 for the clouds and clusters and 3.0-6.1 for the bright stars
  (default), 24-40 and 3.9-5.3 (ngc_4414), with slopes +0.01 to -0.11 over 100-2000 pc - a plateau, as the anchor
  test's exponential disc reads.
- **Against the control every census reads 1.00 +- 0.03 at 300 pc with slopes within 0.03 of 0**, layer on and
  off, all three galaxies: the S60 censuses hold nothing beyond their own expected placement.
- No duplicate positions in any catalogue. Re-materialising the clouds and clusters from the run's fields with
  its seed gives the published columns exactly (every run).
- With the layer off the clusters sit on their clouds (offset 0: the texture columns are neutral), so none
  crosses a ring; with it on, 126-133 of about 12 900 (72 of 5 012 in ngc_4414) stand in another level-0 ring than
  their cloud.
- The bright catalogue holds **no star younger than 20 Myr** (the cluster window is the census's), so the
  "< 20 Myr" bin is empty in every run. At the 20 000-star selection the 40-100 Myr bin holds only 2 109
  (default): the catalogue's young stars are mostly 20-40 Myr.
- `milky_way` with the layer off gives the default galaxy's numbers exactly (its two pins change nothing the
  censuses read with the layer off); with the layer on its numbers differ slightly (the pins move the pattern).
- Footprint B holds 730-795 clouds, 101-116 massive clouds, 554-615 clusters, 277-304 young clusters and 93-133
  bright stars of 40-100 Myr in the default and milky_way runs; 175 clouds, 23 massive clouds and 74 young clusters
  in ngc_4414: its rows are noisy (see the alpha errors), the smallest censuses' most.

## Measured beside the reading

The reading's numbers are `READING_CLUSTERING.md` "What a model could adopt" items 1, 3, 7 and 10 (and Turner
Table 4's medians as read there); every source measures against uniform randoms in its instrument's footprint,
which is this probe's "A uniform" (a whole disc) or "B uniform" (a 6 kpc pointing); none measures against a
control except He 2026's clouds [FQ]. Each cell is alpha over [100, 2000] pc / A = the fitted 1 + omega at 300 pc;
the other two fit ranges, the measured 1 + omega at 100, 300 and 1000 pc, the errors and the broken laws are in the
row tables below.

| census | reading (READING_CLUSTERING.md) | galaxy | layer | A uniform: alpha / A300 | B uniform | A control |
|---|---|---|---|---|---|---|
| clusters age<=10 | -0.5 (PHANGS median -0.51, range -0.14 to -0.84); 1+w(300) = 3.4 (1.2-10) | default | on | -0.27 / 11.39 | -0.11 / 1.18 | +0.00 / 1.00 |
|  |  | default | off | -0.05 / 7.59 | -0.09 / 1.15 | -0.00 / 1.00 |
|  |  | milky_way | on | -0.28 / 11.63 | -0.06 / 1.08 | -0.00 / 1.00 |
|  |  | milky_way | off | -0.05 / 7.59 | -0.09 / 1.15 | -0.00 / 1.00 |
|  |  | ngc_4414 | on | -0.12 / 25.71 | -0.26 / 1.51 | +0.01 / 0.99 |
|  |  | ngc_4414 | off | -0.11 / 24.13 | -0.07 / 1.18 | +0.00 / 0.99 |
| clusters age>10 | -0.28 (-0.20 to -0.38); 2.3 (1.4-5.0) | default | on | -0.26 / 10.53 | -0.01 / 1.09 | -0.01 / 1.01 |
|  |  | default | off | -0.05 / 7.56 | -0.02 / 1.12 | -0.01 / 1.01 |
|  |  | milky_way | on | -0.27 / 10.66 | -0.03 / 1.08 | -0.01 / 1.01 |
|  |  | milky_way | off | -0.05 / 7.56 | -0.02 / 1.12 | -0.01 / 1.01 |
|  |  | ngc_4414 | on | -0.14 / 26.92 | -0.01 / 1.11 | -0.00 / 1.00 |
|  |  | ngc_4414 | off | -0.09 / 24.39 | +0.47 / 0.73 | +0.00 / 1.00 |
| clusters all | PHANGS all ages: median -0.38 [inferred, Turner T4] | default | on | -0.26 / 10.86 | -0.10 / 1.18 | +0.00 / 1.00 |
|  |  | default | off | -0.05 / 7.55 | -0.09 / 1.18 | -0.00 / 1.00 |
|  |  | milky_way | on | -0.26 / 11.03 | -0.08 / 1.13 | +0.00 / 1.00 |
|  |  | milky_way | off | -0.05 / 7.55 | -0.09 / 1.18 | -0.00 / 1.00 |
|  |  | ngc_4414 | on | -0.12 / 26.34 | -0.11 / 1.33 | +0.01 / 0.99 |
|  |  | ngc_4414 | off | -0.09 / 24.16 | -0.06 / 1.24 | +0.01 / 0.99 |
| clouds all | about -0.2 (-0.08 to -0.82); 2.2; flat below ~500 pc. Against a CO-following control: 1.3, slope ~0 [FQ] | default | on | -0.27 / 11.04 | -0.10 / 1.17 | -0.00 / 1.00 |
|  |  | default | off | -0.05 / 7.68 | -0.12 / 1.20 | -0.00 / 1.00 |
|  |  | milky_way | on | -0.26 / 11.14 | -0.08 / 1.12 | +0.00 / 1.00 |
|  |  | milky_way | off | -0.05 / 7.68 | -0.12 / 1.20 | -0.00 / 1.00 |
|  |  | ngc_4414 | on | -0.12 / 26.59 | -0.13 / 1.32 | +0.00 / 0.99 |
|  |  | ngc_4414 | off | -0.09 / 24.34 | -0.15 / 1.32 | +0.01 / 0.99 |
| clouds M>=1e5 | -0.44(3) above 1e5 Msun, NGC 7793 over 40-800 pc; 1+w not given at 300 pc | default | on | -0.33 / 25.45 | +0.27 / 1.04 | -0.01 / 1.01 |
|  |  | default | off | -0.05 / 15.51 | +0.07 / 1.24 | -0.00 / 1.00 |
|  |  | milky_way | on | -0.33 / 25.80 | +0.01 / 1.31 | -0.01 / 1.01 |
|  |  | milky_way | off | -0.05 / 15.51 | +0.07 / 1.24 | -0.00 / 1.00 |
|  |  | ngc_4414 | on | -0.11 / 41.91 | -0.59 / 3.15 | +0.00 / 0.99 |
|  |  | ngc_4414 | off | -0.08 / 40.24 | -0.63 / 3.69 | +0.03 / 0.97 |
| bright 20-40 Myr | field young stars (NGC 6503): -0.69 to 32 Myr, -0.47 to 40 Myr | default | on | -0.23 / 5.07 | -0.33 / 1.77 | +0.00 / 1.00 |
|  |  | default | off | -0.01 / 3.03 | -0.01 / 1.08 | -0.00 / 1.00 |
|  |  | milky_way | on | -0.21 / 5.33 | -0.17 / 1.52 | -0.00 / 1.00 |
|  |  | milky_way | off | -0.01 / 3.03 | -0.01 / 1.08 | -0.00 / 1.00 |
|  |  | ngc_4414 | on | -0.26 / 8.44 | -0.26 / 1.72 | +0.00 / 1.00 |
|  |  | ngc_4414 | off | +0.00 / 3.88 | -0.01 / 1.11 | +0.00 / 1.00 |
| bright 40-100 Myr | -0.32 (50), -0.29 (63), ~-0.22 (71-112 Myr) | default | on | -0.27 / 11.50 | -0.36 / 2.02 | -0.03 / 1.03 |
|  |  | default | off | -0.03 / 6.06 | -0.01 / 1.21 | +0.01 / 0.98 |
|  |  | milky_way | on | -0.25 / 13.08 | -0.25 / 1.94 | -0.02 / 1.02 |
|  |  | milky_way | off | -0.03 / 6.06 | -0.01 / 1.21 | +0.01 / 0.98 |
|  |  | ngc_4414 | on | -0.29 / 9.36 | -0.27 / 1.78 | +0.02 / 0.97 |
|  |  | ngc_4414 | off | +0.01 / 4.11 | +0.13 / 1.00 | +0.02 / 0.99 |
| bright 20-100 Myr | (the series above) | default | on | -0.24 / 5.68 | -0.33 / 1.79 | +0.00 / 1.00 |
|  |  | default | off | -0.01 / 3.30 | -0.01 / 1.10 | -0.00 / 1.00 |
|  |  | milky_way | on | -0.21 / 6.01 | -0.16 / 1.55 | -0.00 / 1.00 |
|  |  | milky_way | off | -0.01 / 3.30 | -0.01 / 1.10 | -0.00 / 1.00 |
|  |  | ngc_4414 | on | -0.27 / 8.60 | -0.27 / 1.72 | -0.00 / 1.00 |
|  |  | ngc_4414 | off | -0.00 / 3.92 | -0.01 / 1.12 | +0.00 / 1.00 |
| bright >100 Myr | ~-0.2 to 112 Myr; red (old) stars -0.05 | default | on | -0.00 / 5.23 | +0.00 / 1.12 | +0.03 / 0.97 |
|  |  | default | off | +0.01 / 5.07 | -0.01 / 1.12 | +0.02 / 0.98 |
|  |  | milky_way | on | -0.00 / 5.19 | +0.04 / 1.01 | +0.03 / 0.97 |
|  |  | milky_way | off | +0.01 / 5.07 | -0.01 / 1.12 | +0.02 / 0.98 |
|  |  | ngc_4414 | on | -0.02 / 5.44 | +0.05 / 1.29 | +0.01 / 0.99 |
|  |  | ngc_4414 | off | -0.00 / 5.25 | +0.04 / 1.25 | +0.01 / 1.00 |

## The layer-on spread: texture_seed 0, 1, 2 (default galaxy, layer on; the bright catalogue not repeated)

| census | vs | texture_seed | N | alpha [100,2000] | A300 | alpha [40,800] | alpha [100,3000] | 1+w 100 | 300 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| clouds all | A uniform | 0 | 16749 | -0.266+-0.015 | 11.04 | -0.152 | -0.272 | 13.44 | 11.28 | 8.01 |
| clouds all | A uniform | 1 | 16734 | -0.268+-0.015 | 11.06 | -0.151 | -0.275 | 13.43 | 11.28 | 8.02 |
| clouds all | A uniform | 2 | 16719 | -0.268+-0.014 | 11.16 | -0.152 | -0.274 | 13.35 | 11.35 | 8.07 |
| clouds all | B uniform | 0 | 773 | -0.096+-0.009 | 1.17 | -0.037 | -0.094 | 1.18 | 1.17 | 1.04 |
| clouds all | B uniform | 1 | 732 | -0.115+-0.011 | 1.24 | -0.010 | -0.123 | 1.41 | 1.21 | 1.08 |
| clouds all | B uniform | 2 | 730 | -0.105+-0.009 | 1.17 | -0.081 | -0.100 | 1.31 | 1.13 | 1.03 |
| clouds M>=1e5 | A uniform | 0 | 2550 | -0.329+-0.017 | 25.45 | -0.152 | -0.328 | 36.98 | 26.12 | 17.07 |
| clouds M>=1e5 | A uniform | 1 | 2545 | -0.336+-0.015 | 25.65 | -0.188 | -0.335 | 35.99 | 26.12 | 17.05 |
| clouds M>=1e5 | A uniform | 2 | 2529 | -0.341+-0.014 | 26.14 | -0.159 | -0.337 | 36.96 | 26.09 | 17.39 |
| clouds M>=1e5 | B uniform | 0 | 106 | +0.266+-0.125 | 1.04 | +0.140 | +0.162 | 1.02 | 1.28 | 1.32 |
| clouds M>=1e5 | B uniform | 1 | 101 | -0.112+-0.094 | 1.35 | +0.102 | -0.101 | 0.60 | 1.43 | 1.18 |
| clouds M>=1e5 | B uniform | 2 | 104 | +0.054+-0.055 | 1.32 | +0.028 | +0.001 | 0.98 | 1.45 | 1.36 |
| clusters all | A uniform | 0 | 12909 | -0.262+-0.016 | 10.86 | -0.139 | -0.270 | 12.66 | 11.08 | 7.91 |
| clusters all | A uniform | 1 | 12882 | -0.270+-0.015 | 10.94 | -0.145 | -0.277 | 12.54 | 11.19 | 7.91 |
| clusters all | A uniform | 2 | 12860 | -0.266+-0.016 | 11.01 | -0.142 | -0.272 | 12.89 | 11.25 | 7.98 |
| clusters all | B uniform | 0 | 601 | -0.100+-0.010 | 1.18 | -0.021 | -0.096 | 1.29 | 1.14 | 1.03 |
| clusters all | B uniform | 1 | 562 | -0.128+-0.016 | 1.27 | -0.048 | -0.134 | 1.43 | 1.19 | 1.09 |
| clusters all | B uniform | 2 | 554 | -0.115+-0.010 | 1.19 | -0.026 | -0.107 | 1.19 | 1.17 | 1.03 |
| clusters age<=10 | A uniform | 0 | 6450 | -0.272+-0.019 | 11.39 | -0.117 | -0.283 | 13.73 | 11.69 | 8.23 |
| clusters age<=10 | A uniform | 1 | 6404 | -0.279+-0.016 | 11.51 | -0.130 | -0.290 | 13.64 | 11.75 | 8.27 |
| clusters age<=10 | A uniform | 2 | 6428 | -0.273+-0.018 | 11.53 | -0.120 | -0.284 | 13.81 | 11.80 | 8.33 |
| clusters age<=10 | B uniform | 0 | 296 | -0.108+-0.020 | 1.18 | -0.142 | -0.099 | 1.46 | 1.10 | 1.03 |
| clusters age<=10 | B uniform | 1 | 277 | -0.162+-0.029 | 1.27 | -0.245 | -0.150 | 1.57 | 1.17 | 1.13 |
| clusters age<=10 | B uniform | 2 | 279 | -0.142+-0.025 | 1.19 | -0.182 | -0.119 | 1.28 | 1.13 | 1.02 |

## Every row

Columns: N inside the footprint (dropped: outside it); N_r the randoms' (or the control's) number; alpha +- its
standard error, A300 and rms (dex) over [100, 2000] pc; alpha and A over [40, 800] and [100, 3000] pc; the measured
1 + omega in the bins holding 100, 300 and 1000 pc (the bins [83.5, 107.8], [299.9, 387.3] and [834.3, 1077.5] pc); the broken law (break at a bin edge, pc; inner and outer slope) over 30-3000 pc; the instrument's seconds
(including RR the first time a footprint and random count is used, with four probe processes running at once).

### default galaxy

| run | census | vs | footprint | N (dropped) | N_r | a [100,2000] | A300 | rms | a [40,800] | A | a [100,3000] | A | 1+w 100 | 300 | 1000 | broken: break pc, inner, outer | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer on | clouds all | A uniform | annulus 0.037-29.962 kpc | 16749 (4) | 167490 | -0.266+-0.015 | 11.04 | 0.015 | -0.152 | 10.98 | -0.272 | 11.04 | 13.44 | 11.28 | 8.01 | 232, -0.06, -0.30 | 5.2 |
| layer on | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 773 (15980) | 7730 | -0.096+-0.009 | 1.17 | 0.009 | -0.037 | 1.16 | -0.094 | 1.17 | 1.18 | 1.17 | 1.04 | 65, -0.73, -0.07 | 0.6 |
| layer on | clouds all | A control | annulus 0.037-29.962 kpc | 16749 (4) | 66693 | -0.000+-0.001 | 1.00 | 0.001 | 0.004 | 1.00 | 0.000 | 1.00 | 1.01 | 1.00 | 1.00 | 65, -0.06, -0.00 | 12.0 |
| layer on | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 2550 (2) | 25500 | -0.329+-0.017 | 25.45 | 0.018 | -0.152 | 25.21 | -0.328 | 25.46 | 36.98 | 26.12 | 17.07 | 83, -0.09, -0.33 | 0.7 |
| layer on | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 106 (2446) | 1060 | 0.266+-0.125 | 1.04 | 0.132 | 0.140 | 1.18 | 0.162 | 1.04 | 1.02 | 1.28 | 1.32 | 139, -1.79, 0.01 | 0.0 |
| layer on | clouds M>=1e5 | A control | annulus 0.037-29.962 kpc | 2550 (2) | 9906 | -0.012+-0.006 | 1.01 | 0.006 | 0.028 | 1.00 | -0.008 | 1.01 | 1.12 | 1.01 | 0.99 | 83, 0.08, -0.02 | 0.8 |
| layer on | clusters all | A uniform | annulus 0.037-29.962 kpc | 12909 (7) | 129090 | -0.262+-0.016 | 10.86 | 0.017 | -0.139 | 10.80 | -0.270 | 10.85 | 12.66 | 11.08 | 7.91 | 232, -0.04, -0.31 | 3.6 |
| layer on | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 601 (12315) | 6010 | -0.100+-0.010 | 1.18 | 0.010 | -0.021 | 1.18 | -0.096 | 1.18 | 1.29 | 1.14 | 1.03 | 65, -0.98, -0.09 | 0.4 |
| layer on | clusters all | A control | annulus 0.037-29.962 kpc | 12909 (7) | 51406 | 0.003+-0.002 | 1.00 | 0.002 | 0.001 | 1.00 | 0.002 | 1.00 | 1.00 | 0.99 | 1.00 | 65, 0.04, 0.00 | 9.4 |
| layer on | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 6450 (2) | 64500 | -0.272+-0.019 | 11.39 | 0.020 | -0.117 | 11.32 | -0.283 | 11.39 | 13.73 | 11.69 | 8.23 | 232, -0.03, -0.33 | 1.6 |
| layer on | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 296 (6156) | 2960 | -0.108+-0.020 | 1.18 | 0.021 | -0.142 | 1.19 | -0.099 | 1.18 | 1.46 | 1.10 | 1.03 | 139, -0.31, -0.10 | 0.1 |
| layer on | clusters age<=10 | A control | annulus 0.037-29.962 kpc | 6450 (2) | 25694 | 0.002+-0.004 | 1.00 | 0.004 | 0.011 | 1.00 | 0.002 | 1.00 | 1.00 | 0.98 | 1.00 | 65, 0.18, 0.00 | 2.3 |
| layer on | bright 20-40 Myr | A uniform | annulus 0.037-29.962 kpc | 13138 (0) | 131380 | -0.229+-0.028 | 5.07 | 0.030 | -0.076 | 5.13 | -0.248 | 5.07 | 5.85 | 5.29 | 3.89 | 300, 0.00, -0.33 | 3.3 |
| layer on | bright 20-40 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 616 (12522) | 6160 | -0.334+-0.038 | 1.77 | 0.040 | -0.130 | 1.79 | -0.315 | 1.76 | 2.19 | 1.84 | 1.20 | 646, -0.13, -0.26 | 0.4 |
| layer on | bright 20-40 Myr | A control | annulus 0.037-29.962 kpc | 13138 (0) | 52913 | 0.001+-0.002 | 1.00 | 0.003 | 0.015 | 1.00 | 0.001 | 1.00 | 1.05 | 0.99 | 1.00 | 108, 0.10, 0.00 | 4.3 |
| layer on | bright 40-100 Myr | A uniform | annulus 0.037-29.962 kpc | 2109 (0) | 21090 | -0.273+-0.034 | 11.50 | 0.036 | -0.086 | 11.62 | -0.321 | 11.50 | 13.15 | 11.67 | 8.49 | 500, -0.05, -0.50 | 0.5 |
| layer on | bright 40-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 101 (2008) | 1010 | -0.356+-0.068 | 2.02 | 0.071 | -0.240 | 2.04 | -0.340 | 2.02 | 1.84 | 1.92 | 1.33 | 108, -1.16, -0.34 | 0.0 |
| layer on | bright 40-100 Myr | A control | annulus 0.037-29.962 kpc | 2109 (0) | 8598 | -0.026+-0.018 | 1.03 | 0.019 | 0.033 | 1.01 | -0.018 | 1.03 | 0.88 | 0.99 | 1.00 | 139, 0.16, 0.00 | 0.4 |
| layer on | bright 20-100 Myr | A uniform | annulus 0.037-29.962 kpc | 15247 (0) | 152470 | -0.236+-0.028 | 5.68 | 0.030 | -0.072 | 5.74 | -0.259 | 5.68 | 6.53 | 5.86 | 4.34 | 300, 0.03, -0.35 | 4.1 |
| layer on | bright 20-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 717 (14530) | 7170 | -0.331+-0.042 | 1.79 | 0.045 | -0.144 | 1.82 | -0.315 | 1.79 | 2.11 | 1.86 | 1.21 | 646, -0.12, -0.27 | 0.4 |
| layer on | bright 20-100 Myr | A control | annulus 0.037-29.962 kpc | 15247 (0) | 61511 | 0.002+-0.002 | 1.00 | 0.002 | 0.014 | 1.00 | 0.002 | 1.00 | 1.03 | 0.99 | 1.00 | 65, 0.19, -0.00 | 4.8 |
| layer on | bright >100 Myr | A uniform | annulus 0.037-29.962 kpc | 4366 (0) | 43660 | -0.005+-0.010 | 5.23 | 0.011 | -0.035 | 5.32 | -0.019 | 5.23 | 5.92 | 5.35 | 5.21 | 65, 0.61, -0.03 | 0.9 |
| layer on | bright >100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 221 (4145) | 2210 | 0.004+-0.049 | 1.12 | 0.051 | -0.098 | 1.17 | -0.011 | 1.12 | 1.25 | 1.27 | 1.06 | 65, -2.23, -0.06 | 0.0 |
| layer on | bright >100 Myr | A control | annulus 0.037-29.962 kpc | 4366 (0) | 17478 | 0.027+-0.010 | 0.97 | 0.010 | -0.070 | 1.00 | 0.021 | 0.97 | 1.17 | 0.99 | 1.00 | 65, 0.93, -0.01 | 0.8 |
| layer off | clouds all | A uniform | annulus 0.037-29.962 kpc | 16748 (6) | 167480 | -0.054+-0.004 | 7.68 | 0.004 | -0.026 | 7.67 | -0.070 | 7.68 | 7.93 | 7.66 | 7.27 | 646, -0.02, -0.13 | 4.3 |
| layer off | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 795 (15959) | 7950 | -0.117+-0.008 | 1.20 | 0.009 | -0.039 | 1.18 | -0.113 | 1.20 | 1.29 | 1.17 | 1.04 | 83, -0.12, -0.11 | 0.6 |
| layer off | clouds all | A control | annulus 0.037-29.962 kpc | 16748 (6) | 66847 | -0.002+-0.001 | 1.00 | 0.001 | 0.006 | 1.00 | -0.001 | 1.00 | 1.00 | 1.00 | 1.00 | 232, 0.02, 0.00 | 8.9 |
| layer off | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 2512 (3) | 25120 | -0.052+-0.011 | 15.51 | 0.012 | -0.012 | 15.44 | -0.065 | 15.51 | 15.98 | 14.92 | 14.69 | 65, 0.41, -0.06 | 0.5 |
| layer off | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 108 (2407) | 1080 | 0.066+-0.070 | 1.24 | 0.074 | 0.124 | 1.19 | 0.017 | 1.24 | 0.35 | 1.25 | 1.38 | 139, -1.41, -0.04 | 0.0 |
| layer off | clouds M>=1e5 | A control | annulus 0.037-29.962 kpc | 2512 (3) | 9975 | -0.004+-0.010 | 1.00 | 0.010 | 0.023 | 1.00 | -0.002 | 1.00 | 1.11 | 1.00 | 1.00 | 139, 0.24, 0.01 | 0.5 |
| layer off | clusters all | A uniform | annulus 0.037-29.962 kpc | 12918 (5) | 129180 | -0.049+-0.004 | 7.55 | 0.005 | -0.023 | 7.56 | -0.066 | 7.55 | 7.90 | 7.55 | 7.18 | 834, -0.03, -0.14 | 2.9 |
| layer off | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 615 (12308) | 6150 | -0.094+-0.011 | 1.18 | 0.011 | -0.031 | 1.18 | -0.097 | 1.18 | 1.35 | 1.17 | 1.04 | 65, -0.55, -0.09 | 0.3 |
| layer off | clusters all | A control | annulus 0.037-29.962 kpc | 12918 (5) | 51585 | -0.004+-0.002 | 1.00 | 0.002 | 0.008 | 1.00 | -0.003 | 1.00 | 1.01 | 0.99 | 1.00 | 65, -0.01, -0.00 | 6.9 |
| layer off | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 6414 (1) | 64140 | -0.053+-0.006 | 7.59 | 0.006 | -0.002 | 7.58 | -0.071 | 7.59 | 7.87 | 7.64 | 7.22 | 300, 0.03, -0.10 | 1.2 |
| layer off | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 301 (6114) | 3010 | -0.092+-0.044 | 1.15 | 0.047 | -0.086 | 1.16 | -0.089 | 1.15 | 1.49 | 1.15 | 1.05 | 65, 0.80, -0.11 | 0.1 |
| layer off | clusters age<=10 | A control | annulus 0.037-29.962 kpc | 6414 (1) | 25843 | -0.004+-0.004 | 1.00 | 0.004 | 0.011 | 1.00 | -0.003 | 1.00 | 1.01 | 0.99 | 1.01 | 65, 0.35, -0.00 | 1.6 |
| layer off | bright 20-40 Myr | A uniform | annulus 0.037-29.962 kpc | 13062 (0) | 130620 | -0.009+-0.004 | 3.03 | 0.004 | 0.006 | 3.02 | -0.013 | 3.03 | 3.12 | 3.00 | 3.02 | 83, -0.05, -0.01 | 2.8 |
| layer off | bright 20-40 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 672 (12390) | 6720 | -0.008+-0.011 | 1.08 | 0.012 | 0.003 | 1.09 | -0.014 | 1.08 | 1.14 | 1.12 | 1.08 | 65, -0.42, -0.03 | 0.3 |
| layer off | bright 20-40 Myr | A control | annulus 0.037-29.962 kpc | 13062 (0) | 52874 | -0.004+-0.005 | 1.00 | 0.005 | 0.009 | 1.00 | -0.003 | 1.00 | 1.04 | 0.99 | 1.00 | 108, 0.11, -0.00 | 3.3 |
| layer off | bright 40-100 Myr | A uniform | annulus 0.037-29.962 kpc | 2189 (0) | 21890 | -0.030+-0.021 | 6.06 | 0.022 | 0.062 | 6.01 | -0.039 | 6.06 | 5.70 | 6.12 | 5.97 | 83, 0.80, -0.03 | 0.4 |
| layer off | bright 40-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 102 (2087) | 1020 | -0.012+-0.086 | 1.21 | 0.091 | -0.145 | 1.22 | -0.030 | 1.21 | 2.07 | 1.07 | 1.25 | 180, 0.02, 0.09 | 0.0 |
| layer off | bright 40-100 Myr | A control | annulus 0.037-29.962 kpc | 2189 (0) | 8437 | 0.008+-0.026 | 0.98 | 0.027 | 0.058 | 0.98 | 0.010 | 0.98 | 1.06 | 1.01 | 0.99 | 180, 0.18, 0.05 | 0.3 |
| layer off | bright 20-100 Myr | A uniform | annulus 0.037-29.962 kpc | 15251 (0) | 152510 | -0.008+-0.002 | 3.30 | 0.002 | 0.013 | 3.30 | -0.013 | 3.30 | 3.39 | 3.30 | 3.29 | 83, 0.02, -0.01 | 3.5 |
| layer off | bright 20-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 774 (14477) | 7740 | -0.015+-0.013 | 1.10 | 0.013 | -0.036 | 1.11 | -0.022 | 1.10 | 1.14 | 1.12 | 1.11 | 180, -0.14, -0.04 | 0.5 |
| layer off | bright 20-100 Myr | A control | annulus 0.037-29.962 kpc | 15251 (0) | 61311 | -0.003+-0.002 | 1.00 | 0.002 | 0.011 | 1.00 | -0.002 | 1.00 | 1.04 | 1.00 | 1.00 | 83, 0.04, -0.01 | 4.2 |
| layer off | bright >100 Myr | A uniform | annulus 0.037-29.962 kpc | 4350 (0) | 43500 | 0.010+-0.012 | 5.07 | 0.013 | 0.006 | 5.13 | -0.006 | 5.07 | 4.86 | 5.16 | 5.06 | 65, 1.00, -0.00 | 0.8 |
| layer off | bright >100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 231 (4119) | 2310 | -0.011+-0.035 | 1.12 | 0.036 | -0.108 | 1.14 | -0.013 | 1.12 | 0.99 | 1.21 | 1.09 | 65, -0.56, 0.00 | 0.0 |
| layer off | bright >100 Myr | A control | annulus 0.037-29.962 kpc | 4350 (0) | 17531 | 0.018+-0.006 | 0.98 | 0.007 | -0.002 | 1.00 | 0.013 | 0.98 | 0.94 | 0.98 | 1.00 | 65, 0.73, 0.00 | 0.7 |

Note: default layer on bright <20 Myr: 0 stars

Note: default layer off bright <20 Myr: 0 stars

### milky_way

| run | census | vs | footprint | N (dropped) | N_r | a [100,2000] | A300 | rms | a [40,800] | A | a [100,3000] | A | 1+w 100 | 300 | 1000 | broken: break pc, inner, outer | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer on | clouds all | A uniform | annulus 0.037-29.962 kpc | 16712 (4) | 167120 | -0.265+-0.015 | 11.14 | 0.015 | -0.145 | 11.08 | -0.272 | 11.14 | 13.59 | 11.38 | 8.09 | 232, -0.04, -0.30 | 5.4 |
| layer on | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 793 (15923) | 7930 | -0.081+-0.010 | 1.12 | 0.011 | -0.010 | 1.10 | -0.074 | 1.12 | 1.22 | 1.09 | 1.02 | 65, -0.83, -0.07 | 0.8 |
| layer on | clouds all | A control | annulus 0.037-29.962 kpc | 16712 (4) | 66787 | 0.000+-0.001 | 1.00 | 0.001 | 0.005 | 1.00 | 0.000 | 1.00 | 1.01 | 1.00 | 1.00 | 65, -0.06, -0.00 | 12.4 |
| layer on | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 2542 (2) | 25420 | -0.333+-0.013 | 25.80 | 0.014 | -0.161 | 25.44 | -0.331 | 25.80 | 35.70 | 26.43 | 17.29 | 83, -0.08, -0.32 | 0.6 |
| layer on | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 116 (2428) | 1160 | 0.010+-0.075 | 1.31 | 0.079 | 0.069 | 1.26 | -0.023 | 1.31 | 0.74 | 1.31 | 1.30 | 646, 0.05, -0.18 | 0.0 |
| layer on | clouds M>=1e5 | A control | annulus 0.037-29.962 kpc | 2542 (2) | 9984 | -0.010+-0.006 | 1.01 | 0.006 | 0.030 | 1.00 | -0.007 | 1.01 | 1.10 | 1.00 | 0.99 | 83, 0.09, -0.02 | 0.7 |
| layer on | clusters all | A uniform | annulus 0.037-29.962 kpc | 12846 (7) | 128460 | -0.264+-0.016 | 11.03 | 0.016 | -0.140 | 10.96 | -0.272 | 11.03 | 12.92 | 11.27 | 8.00 | 232, -0.04, -0.31 | 3.4 |
| layer on | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 615 (12238) | 6150 | -0.084+-0.010 | 1.13 | 0.010 | 0.025 | 1.12 | -0.078 | 1.13 | 1.22 | 1.08 | 1.00 | 65, -1.19, -0.06 | 0.4 |
| layer on | clusters all | A control | annulus 0.037-29.962 kpc | 12846 (7) | 51492 | 0.000+-0.001 | 1.00 | 0.001 | 0.001 | 1.00 | 0.000 | 1.00 | 1.00 | 0.99 | 1.00 | 139, -0.01, -0.00 | 8.9 |
| layer on | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 6404 (2) | 64040 | -0.276+-0.017 | 11.63 | 0.017 | -0.117 | 11.52 | -0.287 | 11.62 | 13.83 | 11.87 | 8.37 | 232, -0.03, -0.33 | 1.4 |
| layer on | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 304 (6102) | 3040 | -0.056+-0.045 | 1.08 | 0.048 | 0.090 | 1.07 | -0.050 | 1.08 | 1.48 | 1.05 | 1.01 | 65, -1.37, -0.06 | 0.1 |
| layer on | clusters age<=10 | A control | annulus 0.037-29.962 kpc | 6404 (2) | 25693 | -0.000+-0.003 | 1.00 | 0.003 | 0.018 | 1.00 | -0.000 | 1.00 | 1.00 | 0.98 | 1.00 | 65, 0.11, 0.00 | 2.2 |
| layer on | bright 20-40 Myr | A uniform | annulus 0.037-29.962 kpc | 13153 (0) | 131530 | -0.213+-0.021 | 5.33 | 0.022 | -0.087 | 5.36 | -0.239 | 5.33 | 5.95 | 5.48 | 4.15 | 387, -0.05, -0.33 | 3.1 |
| layer on | bright 20-40 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 800 (12353) | 8000 | -0.168+-0.027 | 1.52 | 0.029 | -0.095 | 1.54 | -0.208 | 1.51 | 1.65 | 1.58 | 1.26 | 139, -0.38, -0.24 | 0.6 |
| layer on | bright 20-40 Myr | A control | annulus 0.037-29.962 kpc | 13153 (0) | 52757 | -0.002+-0.002 | 1.00 | 0.002 | 0.007 | 1.00 | -0.002 | 1.00 | 0.97 | 0.99 | 1.00 | 65, -0.17, 0.00 | 3.7 |
| layer on | bright 40-100 Myr | A uniform | annulus 0.037-29.962 kpc | 2153 (0) | 21530 | -0.249+-0.031 | 13.08 | 0.032 | -0.096 | 13.16 | -0.324 | 13.07 | 13.65 | 13.36 | 10.08 | 387, 0.04, -0.51 | 0.4 |
| layer on | bright 40-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 133 (2020) | 1330 | -0.249+-0.063 | 1.94 | 0.066 | -0.132 | 1.89 | -0.318 | 1.94 | 1.14 | 2.07 | 1.59 | 108, -0.56, -0.32 | 0.0 |
| layer on | bright 40-100 Myr | A control | annulus 0.037-29.962 kpc | 2153 (0) | 8707 | -0.019+-0.010 | 1.02 | 0.010 | -0.023 | 1.01 | -0.014 | 1.02 | 0.90 | 1.01 | 1.00 | 65, 0.74, 0.00 | 0.4 |
| layer on | bright 20-100 Myr | A uniform | annulus 0.037-29.962 kpc | 15306 (0) | 153060 | -0.213+-0.023 | 6.01 | 0.025 | -0.091 | 6.06 | -0.248 | 6.01 | 6.67 | 6.23 | 4.71 | 387, -0.04, -0.35 | 3.9 |
| layer on | bright 20-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 933 (14373) | 9330 | -0.163+-0.026 | 1.55 | 0.027 | -0.106 | 1.57 | -0.213 | 1.55 | 1.74 | 1.59 | 1.30 | 139, -0.33, -0.24 | 0.8 |
| layer on | bright 20-100 Myr | A control | annulus 0.037-29.962 kpc | 15306 (0) | 61464 | -0.002+-0.002 | 1.00 | 0.002 | 0.001 | 1.00 | -0.001 | 1.00 | 0.99 | 1.00 | 1.00 | 65, 0.11, 0.00 | 4.8 |
| layer on | bright >100 Myr | A uniform | annulus 0.037-29.962 kpc | 4240 (0) | 42400 | -0.004+-0.009 | 5.19 | 0.010 | -0.012 | 5.22 | -0.019 | 5.19 | 4.99 | 5.29 | 5.13 | 65, 0.52, -0.01 | 0.8 |
| layer on | bright >100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 241 (3999) | 2410 | 0.037+-0.063 | 1.01 | 0.066 | -0.125 | 1.04 | 0.023 | 1.01 | 0.82 | 1.13 | 1.01 | 65, 2.37, 0.03 | 0.0 |
| layer on | bright >100 Myr | A control | annulus 0.037-29.962 kpc | 4240 (0) | 17465 | 0.031+-0.009 | 0.97 | 0.009 | -0.038 | 0.98 | 0.024 | 0.97 | 0.96 | 0.98 | 0.99 | 83, 0.21, 0.02 | 0.7 |
| layer off | clouds all | A uniform | annulus 0.037-29.962 kpc | 16748 (6) | 167480 | -0.054+-0.004 | 7.68 | 0.004 | -0.026 | 7.67 | -0.070 | 7.68 | 7.93 | 7.66 | 7.27 | 646, -0.02, -0.13 | 4.4 |
| layer off | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 795 (15959) | 7950 | -0.117+-0.008 | 1.20 | 0.009 | -0.039 | 1.18 | -0.113 | 1.20 | 1.29 | 1.17 | 1.04 | 83, -0.12, -0.11 | 0.5 |
| layer off | clouds all | A control | annulus 0.037-29.962 kpc | 16748 (6) | 66847 | -0.002+-0.001 | 1.00 | 0.001 | 0.006 | 1.00 | -0.001 | 1.00 | 1.00 | 1.00 | 1.00 | 232, 0.02, 0.00 | 8.9 |
| layer off | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 2512 (3) | 25120 | -0.052+-0.011 | 15.51 | 0.012 | -0.012 | 15.44 | -0.065 | 15.51 | 15.98 | 14.92 | 14.69 | 65, 0.41, -0.06 | 0.4 |
| layer off | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 108 (2407) | 1080 | 0.066+-0.070 | 1.24 | 0.074 | 0.124 | 1.19 | 0.017 | 1.24 | 0.35 | 1.25 | 1.38 | 139, -1.41, -0.04 | 0.0 |
| layer off | clouds M>=1e5 | A control | annulus 0.037-29.962 kpc | 2512 (3) | 9975 | -0.004+-0.010 | 1.00 | 0.010 | 0.023 | 1.00 | -0.002 | 1.00 | 1.11 | 1.00 | 1.00 | 139, 0.24, 0.01 | 0.5 |
| layer off | clusters all | A uniform | annulus 0.037-29.962 kpc | 12918 (5) | 129180 | -0.049+-0.004 | 7.55 | 0.005 | -0.023 | 7.56 | -0.066 | 7.55 | 7.90 | 7.55 | 7.18 | 834, -0.03, -0.14 | 2.8 |
| layer off | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 615 (12308) | 6150 | -0.094+-0.011 | 1.18 | 0.011 | -0.031 | 1.18 | -0.097 | 1.18 | 1.35 | 1.17 | 1.04 | 65, -0.55, -0.09 | 0.0 |
| layer off | clusters all | A control | annulus 0.037-29.962 kpc | 12918 (5) | 51585 | -0.004+-0.002 | 1.00 | 0.002 | 0.008 | 1.00 | -0.003 | 1.00 | 1.01 | 0.99 | 1.00 | 65, -0.01, -0.00 | 6.5 |
| layer off | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 6414 (1) | 64140 | -0.053+-0.006 | 7.59 | 0.006 | -0.002 | 7.58 | -0.071 | 7.59 | 7.87 | 7.64 | 7.22 | 300, 0.03, -0.10 | 1.2 |
| layer off | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 301 (6114) | 3010 | -0.092+-0.044 | 1.15 | 0.047 | -0.086 | 1.16 | -0.089 | 1.15 | 1.49 | 1.15 | 1.05 | 65, 0.80, -0.11 | 0.1 |
| layer off | clusters age<=10 | A control | annulus 0.037-29.962 kpc | 6414 (1) | 25843 | -0.004+-0.004 | 1.00 | 0.004 | 0.011 | 1.00 | -0.003 | 1.00 | 1.01 | 0.99 | 1.01 | 65, 0.35, -0.00 | 1.7 |
| layer off | bright 20-40 Myr | A uniform | annulus 0.037-29.962 kpc | 13062 (0) | 130620 | -0.009+-0.004 | 3.03 | 0.004 | 0.006 | 3.02 | -0.013 | 3.03 | 3.12 | 3.00 | 3.02 | 83, -0.05, -0.01 | 2.8 |
| layer off | bright 20-40 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 672 (12390) | 6720 | -0.008+-0.011 | 1.08 | 0.012 | 0.003 | 1.09 | -0.014 | 1.08 | 1.14 | 1.12 | 1.08 | 65, -0.42, -0.03 | 0.4 |
| layer off | bright 20-40 Myr | A control | annulus 0.037-29.962 kpc | 13062 (0) | 52874 | -0.004+-0.005 | 1.00 | 0.005 | 0.009 | 1.00 | -0.003 | 1.00 | 1.04 | 0.99 | 1.00 | 108, 0.11, -0.00 | 3.4 |
| layer off | bright 40-100 Myr | A uniform | annulus 0.037-29.962 kpc | 2189 (0) | 21890 | -0.030+-0.021 | 6.06 | 0.022 | 0.062 | 6.01 | -0.039 | 6.06 | 5.70 | 6.12 | 5.97 | 83, 0.80, -0.03 | 0.4 |
| layer off | bright 40-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 102 (2087) | 1020 | -0.012+-0.086 | 1.21 | 0.091 | -0.145 | 1.22 | -0.030 | 1.21 | 2.07 | 1.07 | 1.25 | 180, 0.02, 0.09 | 0.0 |
| layer off | bright 40-100 Myr | A control | annulus 0.037-29.962 kpc | 2189 (0) | 8437 | 0.008+-0.026 | 0.98 | 0.027 | 0.058 | 0.98 | 0.010 | 0.98 | 1.06 | 1.01 | 0.99 | 180, 0.18, 0.05 | 0.3 |
| layer off | bright 20-100 Myr | A uniform | annulus 0.037-29.962 kpc | 15251 (0) | 152510 | -0.008+-0.002 | 3.30 | 0.002 | 0.013 | 3.30 | -0.013 | 3.30 | 3.39 | 3.30 | 3.29 | 83, 0.02, -0.01 | 3.3 |
| layer off | bright 20-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 774 (14477) | 7740 | -0.015+-0.013 | 1.10 | 0.013 | -0.036 | 1.11 | -0.022 | 1.10 | 1.14 | 1.12 | 1.11 | 180, -0.14, -0.04 | 0.4 |
| layer off | bright 20-100 Myr | A control | annulus 0.037-29.962 kpc | 15251 (0) | 61311 | -0.003+-0.002 | 1.00 | 0.002 | 0.011 | 1.00 | -0.002 | 1.00 | 1.04 | 1.00 | 1.00 | 83, 0.04, -0.01 | 3.7 |
| layer off | bright >100 Myr | A uniform | annulus 0.037-29.962 kpc | 4350 (0) | 43500 | 0.010+-0.012 | 5.07 | 0.013 | 0.006 | 5.13 | -0.006 | 5.07 | 4.86 | 5.16 | 5.06 | 65, 1.00, -0.00 | 0.8 |
| layer off | bright >100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 231 (4119) | 2310 | -0.011+-0.035 | 1.12 | 0.036 | -0.108 | 1.14 | -0.013 | 1.12 | 0.99 | 1.21 | 1.09 | 65, -0.56, 0.00 | 0.0 |
| layer off | bright >100 Myr | A control | annulus 0.037-29.962 kpc | 4350 (0) | 17531 | 0.018+-0.006 | 0.98 | 0.007 | -0.002 | 1.00 | 0.013 | 0.98 | 0.94 | 0.98 | 1.00 | 65, 0.73, 0.00 | 0.7 |

Note: milky_way layer on bright <20 Myr: 0 stars

Note: milky_way layer off bright <20 Myr: 0 stars

### ngc_4414

| run | census | vs | footprint | N (dropped) | N_r | a [100,2000] | A300 | rms | a [40,800] | A | a [100,3000] | A | 1+w 100 | 300 | 1000 | broken: break pc, inner, outer | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer on | clouds all | A uniform | annulus 0.037-29.962 kpc | 6545 (3) | 65450 | -0.123+-0.013 | 26.59 | 0.013 | -0.063 | 26.72 | -0.168 | 26.60 | 29.06 | 26.95 | 23.23 | 646, -0.05, -0.32 | 1.6 |
| layer on | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 175 (6373) | 1750 | -0.133+-0.038 | 1.32 | 0.040 | 0.052 | 1.24 | -0.134 | 1.32 | 0.51 | 1.19 | 1.16 | 108, -0.49, -0.13 | 0.0 |
| layer on | clouds all | A control | annulus 0.037-29.962 kpc | 6545 (3) | 26403 | 0.004+-0.001 | 0.99 | 0.002 | 0.000 | 1.00 | 0.004 | 0.99 | 1.01 | 1.00 | 1.00 | 83, -0.08, 0.00 | 4.7 |
| layer on | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 1257 (1) | 12570 | -0.108+-0.023 | 41.91 | 0.025 | -0.072 | 43.08 | -0.165 | 41.93 | 49.28 | 42.24 | 37.01 | 1077, -0.11, -0.46 | 0.3 |
| layer on | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 23 (1235) | 230 | -0.590+-0.205 | 3.15 | 0.217 | -0.838 | 3.29 | -0.521 | 3.15 | -0.21 | 0.94 | 0.94 | 387, -1.62, -0.42 | 0.0 |
| layer on | clouds M>=1e5 | A control | annulus 0.037-29.962 kpc | 1257 (1) | 5034 | 0.001+-0.012 | 0.99 | 0.013 | -0.013 | 1.00 | 0.003 | 0.99 | 0.98 | 0.99 | 0.98 | 139, -0.21, -0.01 | 0.3 |
| layer on | clusters all | A uniform | annulus 0.037-29.962 kpc | 5007 (5) | 50070 | -0.123+-0.012 | 26.34 | 0.013 | -0.047 | 26.45 | -0.167 | 26.35 | 29.51 | 26.36 | 22.89 | 646, -0.04, -0.31 | 1.1 |
| layer on | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 132 (4880) | 1320 | -0.111+-0.079 | 1.33 | 0.084 | -0.256 | 1.36 | -0.128 | 1.33 | 1.70 | 1.43 | 1.17 | 232, -0.81, -0.20 | 0.0 |
| layer on | clusters all | A control | annulus 0.037-29.962 kpc | 5007 (5) | 20335 | 0.007+-0.003 | 0.99 | 0.003 | -0.005 | 1.00 | 0.005 | 0.99 | 1.05 | 1.00 | 1.00 | 65, 0.02, 0.00 | 2.8 |
| layer on | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 2388 (3) | 23880 | -0.117+-0.010 | 25.71 | 0.011 | -0.072 | 25.87 | -0.162 | 25.71 | 28.36 | 25.78 | 22.48 | 834, -0.06, -0.36 | 0.5 |
| layer on | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 74 (2317) | 740 | -0.262+-0.083 | 1.51 | 0.087 | -0.290 | 1.43 | -0.219 | 1.51 | 2.46 | 1.47 | 1.05 | 139, 1.42, -0.13 | 0.0 |
| layer on | clusters age<=10 | A control | annulus 0.037-29.962 kpc | 2388 (3) | 10161 | 0.009+-0.006 | 0.99 | 0.006 | -0.019 | 0.99 | 0.008 | 0.99 | 0.99 | 0.99 | 0.99 | 65, 0.61, -0.00 | 0.8 |
| layer on | bright 20-40 Myr | A uniform | annulus 0.037-29.962 kpc | 11184 (0) | 111840 | -0.260+-0.032 | 8.44 | 0.034 | -0.095 | 8.54 | -0.313 | 8.44 | 9.66 | 8.80 | 6.35 | 500, -0.05, -0.49 | 2.7 |
| layer on | bright 20-40 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 585 (10599) | 5850 | -0.259+-0.036 | 1.72 | 0.038 | -0.109 | 1.77 | -0.245 | 1.72 | 2.42 | 1.91 | 1.28 | 65, -0.46, -0.25 | 0.3 |
| layer on | bright 20-40 Myr | A control | annulus 0.037-29.962 kpc | 11184 (0) | 44804 | 0.001+-0.003 | 1.00 | 0.003 | -0.003 | 1.00 | 0.000 | 1.00 | 1.02 | 1.00 | 1.00 | 65, -0.08, -0.00 | 4.6 |
| layer on | bright 40-100 Myr | A uniform | annulus 0.037-29.962 kpc | 2186 (0) | 21860 | -0.290+-0.033 | 9.36 | 0.035 | -0.069 | 9.45 | -0.340 | 9.36 | 11.79 | 9.93 | 6.64 | 300, 0.05, -0.47 | 0.5 |
| layer on | bright 40-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 93 (2093) | 930 | -0.267+-0.053 | 1.78 | 0.056 | -0.130 | 1.77 | -0.273 | 1.78 | 1.86 | 1.70 | 1.24 | 83, -2.50, -0.24 | 0.0 |
| layer on | bright 40-100 Myr | A control | annulus 0.037-29.962 kpc | 2186 (0) | 8728 | 0.024+-0.015 | 0.97 | 0.015 | 0.102 | 0.97 | 0.020 | 0.97 | 1.00 | 1.03 | 0.99 | 83, -0.10, 0.01 | 0.4 |
| layer on | bright 20-100 Myr | A uniform | annulus 0.037-29.962 kpc | 13370 (0) | 133700 | -0.266+-0.031 | 8.60 | 0.033 | -0.094 | 8.68 | -0.318 | 8.59 | 9.92 | 8.94 | 6.39 | 387, -0.04, -0.47 | 3.6 |
| layer on | bright 20-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 678 (12692) | 6780 | -0.265+-0.035 | 1.72 | 0.037 | -0.092 | 1.77 | -0.251 | 1.72 | 2.39 | 1.89 | 1.28 | 65, -0.83, -0.25 | 0.5 |
| layer on | bright 20-100 Myr | A control | annulus 0.037-29.962 kpc | 13370 (0) | 53532 | -0.000+-0.002 | 1.00 | 0.002 | -0.000 | 1.00 | -0.001 | 1.00 | 1.01 | 1.00 | 1.00 | 65, -0.20, -0.00 | 6.0 |
| layer on | bright >100 Myr | A uniform | annulus 0.037-29.962 kpc | 6709 (0) | 67090 | -0.019+-0.009 | 5.44 | 0.009 | -0.021 | 5.44 | -0.031 | 5.44 | 5.07 | 5.50 | 5.33 | 108, -0.25, -0.03 | 1.5 |
| layer on | bright >100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 358 (6351) | 3580 | 0.045+-0.031 | 1.29 | 0.033 | 0.080 | 1.32 | -0.016 | 1.29 | 1.08 | 1.45 | 1.37 | 65, -3.21, -0.02 | 0.1 |
| layer on | bright >100 Myr | A control | annulus 0.037-29.962 kpc | 6709 (0) | 26560 | 0.011+-0.007 | 0.99 | 0.007 | -0.021 | 1.00 | 0.008 | 0.99 | 0.94 | 1.01 | 1.00 | 83, -0.15, 0.01 | 1.8 |
| layer off | clouds all | A uniform | annulus 0.037-29.962 kpc | 6530 (4) | 65300 | -0.087+-0.011 | 24.34 | 0.011 | -0.037 | 24.43 | -0.132 | 24.34 | 25.83 | 24.41 | 22.24 | 834, -0.03, -0.33 | 1.7 |
| layer off | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 176 (6358) | 1760 | -0.149+-0.039 | 1.32 | 0.041 | 0.114 | 1.23 | -0.147 | 1.32 | 1.07 | 1.13 | 1.13 | 108, 0.02, -0.15 | 0.0 |
| layer off | clouds all | A control | annulus 0.037-29.962 kpc | 6530 (4) | 26360 | 0.008+-0.003 | 0.99 | 0.003 | 0.002 | 0.99 | 0.006 | 0.99 | 1.00 | 1.00 | 1.00 | 139, -0.01, 0.00 | 4.4 |
| layer off | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 1267 (0) | 12670 | -0.079+-0.027 | 40.24 | 0.028 | -0.095 | 41.61 | -0.133 | 40.26 | 49.93 | 41.89 | 37.36 | 180, -0.25, -0.19 | 0.3 |
| layer off | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 23 (1244) | 230 | -0.632+-0.176 | 3.69 | 0.185 | -0.633 | 4.03 | -0.595 | 3.69 | 11.35 | 1.57 | 1.04 | 387, -1.22, -0.73 | 0.0 |
| layer off | clouds M>=1e5 | A control | annulus 0.037-29.962 kpc | 1267 (0) | 5031 | 0.027+-0.025 | 0.97 | 0.026 | -0.054 | 1.00 | 0.022 | 0.97 | 1.03 | 1.02 | 0.99 | 139, -0.42, -0.01 | 0.3 |
| layer off | clusters all | A uniform | annulus 0.037-29.962 kpc | 5016 (2) | 50160 | -0.088+-0.011 | 24.16 | 0.012 | -0.047 | 24.30 | -0.132 | 24.16 | 25.63 | 24.09 | 21.96 | 834, -0.03, -0.32 | 1.2 |
| layer off | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 132 (4886) | 1320 | -0.058+-0.054 | 1.24 | 0.057 | -0.107 | 1.26 | -0.082 | 1.24 | 1.46 | 1.34 | 1.14 | 232, -0.35, -0.16 | 0.0 |
| layer off | clusters all | A control | annulus 0.037-29.962 kpc | 5016 (2) | 20332 | 0.011+-0.004 | 0.99 | 0.005 | -0.008 | 1.00 | 0.008 | 0.99 | 1.02 | 0.99 | 1.00 | 65, 0.11, 0.01 | 2.8 |
| layer off | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 2417 (0) | 24170 | -0.106+-0.008 | 24.13 | 0.009 | -0.091 | 24.19 | -0.144 | 24.14 | 27.46 | 23.25 | 21.64 | 1077, -0.07, -0.39 | 0.5 |
| layer off | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 75 (2342) | 750 | -0.067+-0.108 | 1.18 | 0.114 | -0.437 | 1.26 | -0.055 | 1.18 | 0.11 | 1.02 | 1.01 | 180, -2.08, 0.02 | 0.0 |
| layer off | clusters age<=10 | A control | annulus 0.037-29.962 kpc | 2417 (0) | 10195 | 0.001+-0.010 | 0.99 | 0.010 | -0.031 | 0.99 | 0.002 | 0.99 | 0.96 | 0.98 | 0.99 | 65, 0.59, 0.01 | 0.7 |
| layer off | bright 20-40 Myr | A uniform | annulus 0.037-29.962 kpc | 11209 (0) | 112090 | 0.001+-0.003 | 3.88 | 0.004 | 0.004 | 3.88 | -0.007 | 3.88 | 3.89 | 3.92 | 3.90 | 83, -0.23, -0.01 | 2.8 |
| layer off | bright 20-40 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 558 (10651) | 5580 | -0.010+-0.015 | 1.11 | 0.016 | -0.005 | 1.11 | -0.019 | 1.11 | 1.12 | 1.18 | 1.12 | 65, -0.39, -0.03 | 0.3 |
| layer off | bright 20-40 Myr | A control | annulus 0.037-29.962 kpc | 11209 (0) | 44584 | 0.003+-0.004 | 1.00 | 0.004 | 0.012 | 1.00 | 0.002 | 1.00 | 0.99 | 1.00 | 1.01 | 65, -0.35, 0.00 | 4.1 |
| layer off | bright 40-100 Myr | A uniform | annulus 0.037-29.962 kpc | 2131 (0) | 21310 | 0.014+-0.017 | 4.11 | 0.018 | 0.083 | 4.22 | -0.000 | 4.11 | 5.20 | 4.34 | 4.11 | 65, 1.76, -0.04 | 0.4 |
| layer off | bright 40-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 100 (2031) | 1000 | 0.127+-0.129 | 1.00 | 0.135 | -0.199 | 1.07 | 0.076 | 0.99 | 1.12 | 1.01 | 1.14 | 180, -1.63, 0.00 | 0.0 |
| layer off | bright 40-100 Myr | A control | annulus 0.037-29.962 kpc | 2131 (0) | 8694 | 0.021+-0.019 | 0.99 | 0.020 | 0.131 | 1.00 | 0.013 | 0.99 | 1.07 | 1.06 | 1.00 | 65, 0.31, -0.02 | 0.4 |
| layer off | bright 20-100 Myr | A uniform | annulus 0.037-29.962 kpc | 13340 (0) | 133400 | -0.001+-0.003 | 3.92 | 0.003 | 0.006 | 3.93 | -0.009 | 3.92 | 4.03 | 3.93 | 3.93 | 83, -0.12, -0.01 | 3.3 |
| layer off | bright 20-100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 658 (12682) | 6580 | -0.010+-0.018 | 1.12 | 0.019 | -0.021 | 1.12 | -0.023 | 1.12 | 1.04 | 1.16 | 1.14 | 65, -1.13, -0.02 | 0.4 |
| layer off | bright 20-100 Myr | A control | annulus 0.037-29.962 kpc | 13340 (0) | 53278 | 0.002+-0.002 | 1.00 | 0.002 | 0.011 | 1.00 | 0.001 | 1.00 | 1.00 | 0.99 | 1.01 | 65, -0.29, -0.00 | 5.1 |
| layer off | bright >100 Myr | A uniform | annulus 0.037-29.962 kpc | 6715 (0) | 67150 | -0.001+-0.006 | 5.25 | 0.006 | -0.017 | 5.29 | -0.012 | 5.25 | 4.98 | 5.36 | 5.23 | 139, -0.19, -0.02 | 1.4 |
| layer off | bright >100 Myr | B uniform | square 6 kpc at (8.2, 0) kpc | 342 (6373) | 3420 | 0.045+-0.028 | 1.25 | 0.029 | -0.020 | 1.30 | -0.003 | 1.25 | 1.09 | 1.26 | 1.25 | 65, -1.62, -0.04 | 0.1 |
| layer off | bright >100 Myr | A control | annulus 0.037-29.962 kpc | 6715 (0) | 26729 | 0.007+-0.005 | 1.00 | 0.005 | -0.010 | 1.01 | 0.004 | 1.00 | 1.00 | 1.03 | 1.00 | 139, -0.14, -0.00 | 1.6 |

Note: ngc_4414 layer on bright <20 Myr: 0 stars

Note: ngc_4414 layer off bright <20 Myr: 0 stars

### default galaxy, texture_seed 1 and 2 (layer on)

| run | census | vs | footprint | N (dropped) | N_r | a [100,2000] | A300 | rms | a [40,800] | A | a [100,3000] | A | 1+w 100 | 300 | 1000 | broken: break pc, inner, outer | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer on texture_seed=1 | clouds all | A uniform | annulus 0.037-29.962 kpc | 16734 (4) | 167340 | -0.268+-0.015 | 11.06 | 0.016 | -0.151 | 11.01 | -0.275 | 11.06 | 13.43 | 11.28 | 8.02 | 232, -0.05, -0.31 | 5.4 |
| layer on texture_seed=1 | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 732 (16006) | 7320 | -0.115+-0.011 | 1.24 | 0.012 | -0.010 | 1.23 | -0.123 | 1.24 | 1.41 | 1.21 | 1.08 | 83, -0.44, -0.12 | 0.6 |
| layer on texture_seed=1 | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 2545 (2) | 25450 | -0.336+-0.015 | 25.65 | 0.016 | -0.188 | 25.42 | -0.335 | 25.65 | 35.99 | 26.12 | 17.05 | 83, -0.05, -0.33 | 0.6 |
| layer on texture_seed=1 | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 101 (2446) | 1010 | -0.112+-0.094 | 1.35 | 0.099 | 0.102 | 1.21 | -0.101 | 1.35 | 0.60 | 1.43 | 1.18 | 232, 0.67, 0.05 | 0.0 |
| layer on texture_seed=1 | clusters all | A uniform | annulus 0.037-29.962 kpc | 12882 (7) | 128820 | -0.270+-0.015 | 10.94 | 0.016 | -0.145 | 10.86 | -0.277 | 10.94 | 12.54 | 11.19 | 7.91 | 232, -0.05, -0.31 | 3.4 |
| layer on texture_seed=1 | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 562 (12327) | 5620 | -0.128+-0.016 | 1.27 | 0.017 | -0.048 | 1.26 | -0.134 | 1.27 | 1.43 | 1.19 | 1.09 | 65, -1.07, -0.13 | 0.4 |
| layer on texture_seed=1 | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 6404 (2) | 64040 | -0.279+-0.016 | 11.51 | 0.017 | -0.130 | 11.41 | -0.290 | 11.51 | 13.64 | 11.75 | 8.27 | 232, -0.05, -0.33 | 1.6 |
| layer on texture_seed=1 | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 277 (6129) | 2770 | -0.162+-0.029 | 1.27 | 0.030 | -0.245 | 1.24 | -0.150 | 1.27 | 1.57 | 1.17 | 1.13 | 65, 0.29, -0.14 | 0.1 |
| layer on texture_seed=2 | clouds all | A uniform | annulus 0.037-29.962 kpc | 16719 (4) | 167190 | -0.268+-0.014 | 11.16 | 0.015 | -0.152 | 11.08 | -0.274 | 11.16 | 13.35 | 11.35 | 8.07 | 232, -0.06, -0.31 | 5.3 |
| layer on texture_seed=2 | clouds all | B uniform | square 6 kpc at (8.2, 0) kpc | 730 (15993) | 7300 | -0.105+-0.009 | 1.17 | 0.009 | -0.081 | 1.15 | -0.100 | 1.17 | 1.31 | 1.13 | 1.03 | 83, -0.27, -0.10 | 0.6 |
| layer on texture_seed=2 | clouds M>=1e5 | A uniform | annulus 0.037-29.962 kpc | 2529 (2) | 25290 | -0.341+-0.014 | 26.14 | 0.015 | -0.159 | 25.77 | -0.337 | 26.14 | 36.96 | 26.09 | 17.39 | 83, 0.11, -0.33 | 0.6 |
| layer on texture_seed=2 | clouds M>=1e5 | B uniform | square 6 kpc at (8.2, 0) kpc | 104 (2427) | 1040 | 0.054+-0.055 | 1.32 | 0.058 | 0.028 | 1.35 | 0.001 | 1.32 | 0.98 | 1.45 | 1.36 | 139, -1.00, -0.07 | 0.0 |
| layer on texture_seed=2 | clusters all | A uniform | annulus 0.037-29.962 kpc | 12860 (7) | 128600 | -0.266+-0.016 | 11.01 | 0.017 | -0.142 | 10.94 | -0.272 | 11.00 | 12.89 | 11.25 | 7.98 | 232, -0.03, -0.31 | 3.8 |
| layer on texture_seed=2 | clusters all | B uniform | square 6 kpc at (8.2, 0) kpc | 554 (12313) | 5540 | -0.115+-0.010 | 1.19 | 0.011 | -0.026 | 1.16 | -0.107 | 1.19 | 1.19 | 1.17 | 1.03 | 83, -0.68, -0.09 | 0.3 |
| layer on texture_seed=2 | clusters age<=10 | A uniform | annulus 0.037-29.962 kpc | 6428 (2) | 64280 | -0.273+-0.018 | 11.53 | 0.019 | -0.120 | 11.45 | -0.284 | 11.53 | 13.81 | 11.80 | 8.33 | 232, -0.02, -0.33 | 1.6 |
| layer on texture_seed=2 | clusters age<=10 | B uniform | square 6 kpc at (8.2, 0) kpc | 279 (6151) | 2790 | -0.142+-0.025 | 1.19 | 0.026 | -0.182 | 1.15 | -0.119 | 1.19 | 1.28 | 1.13 | 1.02 | 65, 2.70, -0.08 | 0.1 |

### clusters older than 10 Myr: default galaxy

| run | census | vs | footprint | N (dropped) | N_r | a [100,2000] | A300 | rms | a [40,800] | A | a [100,3000] | A | 1+w 100 | 300 | 1000 | broken: break pc, inner, outer | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer on | clusters age>10 | A uniform | annulus 0.037-29.962 kpc | 6459 (5) | 64590 | -0.264+-0.014 | 10.53 | 0.015 | -0.131 | 10.44 | -0.267 | 10.53 | 11.99 | 10.77 | 7.63 | 232, -0.05, -0.29 | 1.5 |
| layer on | clusters age>10 | B uniform | square 6 kpc at (8.2, 0) kpc | 305 (6159) | 3050 | -0.005+-0.046 | 1.09 | 0.049 | 0.188 | 1.12 | -0.029 | 1.09 | 0.97 | 1.22 | 1.02 | 65, -3.11, -0.05 | 0.1 |
| layer on | clusters age>10 | A control | annulus 0.037-29.962 kpc | 6459 (5) | 25712 | -0.006+-0.004 | 1.01 | 0.005 | 0.025 | 1.01 | -0.006 | 1.01 | 0.96 | 1.01 | 1.00 | 65, -0.27, 0.00 | 2.3 |
| layer off | clusters age>10 | A uniform | annulus 0.037-29.962 kpc | 6504 (4) | 65040 | -0.053+-0.005 | 7.56 | 0.005 | -0.015 | 7.53 | -0.068 | 7.56 | 7.73 | 7.52 | 7.15 | 180, 0.04, -0.07 | 1.5 |
| layer off | clusters age>10 | B uniform | square 6 kpc at (8.2, 0) kpc | 314 (6194) | 3140 | -0.022+-0.047 | 1.12 | 0.049 | 0.296 | 1.14 | -0.051 | 1.12 | 0.98 | 1.15 | 1.05 | 65, -1.26, -0.04 | 0.1 |
| layer off | clusters age>10 | A control | annulus 0.037-29.962 kpc | 6504 (4) | 25742 | -0.011+-0.005 | 1.01 | 0.005 | 0.018 | 1.00 | -0.008 | 1.01 | 0.94 | 1.01 | 1.00 | 108, -0.03, -0.01 | 2.2 |

### clusters older than 10 Myr: milky_way

| run | census | vs | footprint | N (dropped) | N_r | a [100,2000] | A300 | rms | a [40,800] | A | a [100,3000] | A | 1+w 100 | 300 | 1000 | broken: break pc, inner, outer | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer on | clusters age>10 | A uniform | annulus 0.037-29.962 kpc | 6442 (5) | 64420 | -0.266+-0.014 | 10.66 | 0.015 | -0.131 | 10.56 | -0.268 | 10.66 | 12.20 | 10.90 | 7.69 | 232, -0.05, -0.29 | 1.6 |
| layer on | clusters age>10 | B uniform | square 6 kpc at (8.2, 0) kpc | 311 (6136) | 3110 | -0.028+-0.038 | 1.08 | 0.040 | 0.101 | 1.10 | -0.040 | 1.08 | 1.14 | 1.01 | 1.02 | 65, 0.01, -0.07 | 0.1 |
| layer on | clusters age>10 | A control | annulus 0.037-29.962 kpc | 6442 (5) | 25799 | -0.007+-0.005 | 1.01 | 0.006 | 0.021 | 1.00 | -0.007 | 1.01 | 0.95 | 1.01 | 1.00 | 65, -0.34, 0.01 | 2.2 |
| layer off | clusters age>10 | A uniform | annulus 0.037-29.962 kpc | 6504 (4) | 65040 | -0.053+-0.005 | 7.56 | 0.005 | -0.015 | 7.53 | -0.068 | 7.56 | 7.73 | 7.52 | 7.15 | 180, 0.04, -0.07 | 1.6 |
| layer off | clusters age>10 | B uniform | square 6 kpc at (8.2, 0) kpc | 314 (6194) | 3140 | -0.022+-0.047 | 1.12 | 0.049 | 0.296 | 1.14 | -0.051 | 1.12 | 0.98 | 1.15 | 1.05 | 65, -1.26, -0.04 | 0.1 |
| layer off | clusters age>10 | A control | annulus 0.037-29.962 kpc | 6504 (4) | 25742 | -0.011+-0.005 | 1.01 | 0.005 | 0.018 | 1.00 | -0.008 | 1.01 | 0.94 | 1.01 | 1.00 | 108, -0.03, -0.01 | 2.4 |

### clusters older than 10 Myr: ngc_4414

| run | census | vs | footprint | N (dropped) | N_r | a [100,2000] | A300 | rms | a [40,800] | A | a [100,3000] | A | 1+w 100 | 300 | 1000 | broken: break pc, inner, outer | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer on | clusters age>10 | A uniform | annulus 0.037-29.962 kpc | 2619 (2) | 26190 | -0.135+-0.014 | 26.92 | 0.015 | -0.050 | 27.05 | -0.176 | 26.93 | 30.19 | 27.00 | 23.07 | 646, -0.06, -0.31 | 0.6 |
| layer on | clusters age>10 | B uniform | square 6 kpc at (8.2, 0) kpc | 58 (2563) | 580 | -0.013+-0.243 | 1.11 | 0.256 | -0.135 | 1.17 | -0.043 | 1.10 | 1.24 | 0.58 | 1.19 | 232, -1.53, -0.15 | 0.0 |
| layer on | clusters age>10 | A control | annulus 0.037-29.962 kpc | 2619 (2) | 10174 | -0.003+-0.005 | 1.00 | 0.005 | -0.006 | 1.00 | -0.002 | 1.00 | 1.06 | 0.98 | 1.00 | 83, -0.29, -0.01 | 0.8 |
| layer off | clusters age>10 | A uniform | annulus 0.037-29.962 kpc | 2599 (2) | 25990 | -0.092+-0.012 | 24.39 | 0.013 | -0.027 | 24.56 | -0.135 | 24.40 | 27.23 | 24.30 | 22.20 | 646, -0.01, -0.28 | 0.5 |
| layer off | clusters age>10 | B uniform | square 6 kpc at (8.2, 0) kpc | 57 (2544) | 570 | 0.474+-0.316 | 0.73 | 0.333 | -0.288 | 1.06 | 0.306 | 0.73 | 3.26 | 0.67 | 1.29 | 139, -5.20, -0.03 | 0.0 |
| layer off | clusters age>10 | A control | annulus 0.037-29.962 kpc | 2599 (2) | 10137 | 0.004+-0.010 | 1.00 | 0.010 | -0.014 | 1.00 | 0.003 | 1.00 | 1.03 | 0.98 | 1.01 | 65, 0.16, -0.00 | 0.8 |

## What was not done, and why

- Footprint A was not trimmed: the brief's rule (the radial range of cells with a positive expectation) gives the
  whole grid in every run, and that is what was measured.
- The bright catalogue's "< 20 Myr" bin is empty by construction (the cluster window), not measured.
- The bright catalogue was not repeated under the two other texture_seed values (the brief asked for clouds and
  clusters there).
- Footprint B was not given a control (the brief asks for the control in footprint A only).
- No randoms multiple above 10, no unsplit RR at the probe's sizes (the instrument's tests hold the split against
  brute force and the anchor; the cost of an unsplit RR at 167 000 randoms was not measured).
- Rows for clusters older than 10 Myr were added (the reading names them); they come from a second pass of the same
  script over the same runs (same seeds, same numbers of the shared rows).
