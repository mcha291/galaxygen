# RENDER_PHYSICS — the model/renderer contract

What the model publishes so that the viewer can draw galaxy-scale and
nebula-scale images, in broadband colour, narrowband false colour, or as a named
instrument would record them.

Companion to `RENDER_PLAN.md`, which covers the viewer's first build (M1–M4,
H1, R1–R5, all done at S23–S24) and to `BUILD_II.md`, whose Phases 8–11 build
the model side of this contract and whose sessions V1–V4 build the renderer
side. This document covers the **interface**: it is the thing both ends must
agree on, and it is written to be unambiguous because the two ends get built by
different sessions.

Everything here is `[inferred]` design unless tagged. Physics constants marked
**NEEDS SOURCING** must be read from a source before entering code (rule B9).

---

## 0. Where the repository stands against this contract (reconciled 2026-09-26)

Written when the contract entered the repository, so that no phase reads the
sections below as a description of an empty slate.

**Already published, and consistent with the contract.**

- Per star, `star_luminosity` (L☉, bolometric) and `star_temperature` (K) from
  the committed PARSEC table `[verified: model/galaxy/stages/photometry.py; DECISIONS.md D164]`.
  No RGB is published: the temperature's declared ramp is the `blackbody` cmap
  computed from Planck's law at import, which is §2's rule already honoured for
  stars.
- The disc's unresolved light as `disc_surface_brightness` (L☉/pc²) and
  `disc_light_temperature`, integrated along every isochrone once
  `[verified: model/galaxy/stages/light.py; D165]`. A **surface** quantity, as
  §4 permits at galaxy scale.
- Dust as `dust_surface_density` and `dust_extinction_v` (A_V face-on) from the
  `ism` stage `[verified: model/galaxy/stages/ism.py; D163]`. Since S31 (BUILD_II
  Phase 7) the `dust` stage adds, per radius, the scattering optical depth and
  E(B − V), the scalar asymmetry g, the absorbed starlight, the dust temperature
  from the heating balance, the infrared emission and its total, G₀ and the PAH
  fraction; the absorbed and emitted powers are the §7 energy-balance test
  `[verified: model/galaxy/stages/dust.py; tests/test_dust.py]`. Galaxy-scale
  surface quantities, face-on.
- Per-region determinism: `/api/region` materialises any (R, φ) window as the
  same stars a full sweep would give, a star named by `(cell, index)` at a
  sample size `[verified: model/galaxy/stages/systems.py; D60, D167]`. This is
  §5c's `sample_region(bounds, seed)` in all but name.

**Published, but not in the contract's form.**

- `halpha_surface_brightness` was Σ_SFR times one constant `[verified: light.py;
  D166]`, **retired at S41 (D191)**: no route, test or viewer read it once the
  nebular stage's layers existed. **Since S35 (Phase 9)** the `nebular` stage publishes §2's ionized-gas
  component: per cluster the HII region's Q, n_e, T_e, log U, clumping and O/N/S
  (§3a's shape parameters) and its Hα **per unit volume** (§4, unit `erg/s/cm3`),
  the diffuse layer, and the disc's Hα as Σ_Q redistributed; `HALPHA_PER_SFR` is
  the check (0.71 at S35) `[verified: model/galaxy/stages/nebular.py; D184]`. **Since S42
  (D192)** the collisionally excited lines are read off the photoionization grid ruled in
  (Byler et al. 2017 via FSPS, fetched on the owner's word of 2026-09-27, clamped at its
  edges): per region `hii_{oiii_5007,nii_6583,sii_6716,sii_6731}_ratio` over its own Hα,
  per ring `*_surface_brightness_hii`, and Hβ in both layers; `/api/render` carries them as
  `lines_hii` / `lines_dig` and `absent.lines` is empty. The diffuse gas has no forbidden
  line (the grid does not model its field; debt #119).
- **Since S36 (Phase 10)** the `bubbles` stage publishes the hollow: per cluster
  Weaver et al. 1977's bubble (radius, shell velocity, density, thickness, Hα per
  unit volume in the shell, interior pressure and temperature, phase, stalled),
  the supernova-remnant census as an object class (`of="remnant"`, `/api/remnants`,
  Sedov then the snowplow), the hot phase's porosity per radius, and a star's own
  bubble as a catalogue column `[verified: model/galaxy/stages/bubbles.py,
  feedback.py; D185]`. The shells' own [S II]/Hα still waits: the grid is read for the
  HII regions, not for a shocked shell.
- The region cells were galaxy-scale: 1024 cells in (R, φ), of which ~800 realise
  a star at the default sample `[verified: python -m galaxy.specs, performance]`.
  **Since S32 (Phase 8) `/api/region` and `/api/system` take `level=` 0–3**: a
  level-k cell is one of 4^k children of a level-0 cell with its own seeded stream,
  holds its parent's stars that fall inside it plus its own at the parent's density
  read at the child — 4^k the sample density — and the union, prefix and
  determinism properties are asserted at every level `[verified:
  model/galaxy/stages/systems.py; tests/test_hierarchy.py; D181]`. The molecular
  clouds of §5a exist as an object class (`of="cloud"`) served by `/api/clouds`, a
  census that a level filters `[verified: model/galaxy/stages/clouds.py; D181]`;
  since S33 the cluster object of §5b exists too (`of="cluster"`, `/api/clusters`,
  one per cloud past its embedded phase, Q and wind as IMF integrals) `[verified:
  model/galaxy/stages/clusters.py; D182]`.

**Present in the viewer, and forbidden by §8 once the cloud vector exists.**
The field regime lays each ring out within itself: 30% of the starlight as
12 000 K young light crowded into the arms, the dust led onto the arms' inner
edge, a seeded clump lattice along the arms, and Hα gathered into knots covering
~1.6% of a ring, all seeded from `world_seed` so a galaxy keeps its clumps from
view to view `[verified: frontend/src/galaxy/FieldVolume.tsx, regimes.ts;
commit f2230d5]`. The seed comes from the model, which §8 requires; the
*structure* does not trace to a published field, which §8 forbids. It was a
stated display choice made before any cloud field existed, and it is exactly
what V2 and V3 replace: the young light by the ionized-gas and stellar
components at the arms' own star formation (Phase 2), the clumps and knots by
the cloud catalogue (Phase 8) and its emissivity (Phase 9). **Since S38 (V1)
the young light is gone**: the stellar component's colour per cell is the
model's filter integral at the population's published colour temperature, and
what stays of the exception is the Hα's crowding into the arms and its seeded
knots, and the dust's lead and clumps, V2's to remove `[verified:
frontend/src/galaxy/regimes.ts, FieldVolume.tsx]`. **Since S39 (V2) the exception
is closed**: `/api/render` returns the Hα as two volumetric layers (the HII
regions' share placed by the pattern's contrast in the clouds' layer, the diffuse
gas's in its published 1.4 kpc layer) and the dust as three components — the
extinction per filter from the grain table's own curve (A_λ/A_V from C_ext/H at
the filter's reference wavelength over the V row's), the scattered light (the
slab's scattered share, a Henyey–Greenstein phase table at the published g) and
the thermal emission (Σ_IR at T_d through the curve) — each with its layer in the
header; the viewer spreads each through its layer and integrates along the ray.
The knots, the clump lattice, the dust's lead and `CHANNEL_EXTINCTION` are gone;
what the field regime keeps is display only (white point, exposure, tone curve,
bloom, the march's sampling). The frame's absorbed and emitted power are the
published fields' to 3.4 × 10⁻⁴ each and balance to 6.8 × 10⁻⁴, the TIR box's
coverage `[verified: tests/test_render.py]`. **Since S40 (V3) the region regime
draws §5's objects from their published vectors** (D190): below the stars
handover the view asks `/api/clouds`, `/api/clusters`, `/api/remnants` and
`/api/render` at the level its width needs (one level per factor four under
4 kpc) and marches per pixel each cloud's interior — the log-normal at the
published σ_s realised by a value-noise field seeded by the cloud's (cell, index)
path, the mean tilted along the published gradient, the cluster's Strömgren
sphere carved out and the clumps above e^σ_s inside it left as pillars — each
HII region as a sphere of the published emissivity per volume, each bubble and
remnant as a shell of the published thickness and emissivity (§4's limb
brightening for free), the clouds' transmission at the census's one central A_V
(`cloud_extinction_v`); the field's HII component fades inside the window as
the spheres fade in (§7: no double counting). The routes name every row by
(cell, index) — §5a's seed, realised. §7's catalogue-against-field holds for the
clusters' Hα (0.980 over the disc, 0.974 over a level-1 sector, sixty level-1
windows scattering as the census's own second moment says) and a census is
identical at levels 0–3 `[verified: tests/test_region_synthesis.py;
frontend/src/galaxy/region.test.ts]`. Stated, not hidden (#110–#113): the
noise's octaves and the pillar threshold are shapes the vector does not
constrain; a display budget of 256 objects; the composite is a screen-space
pass; the stars stay on the level-0 sample.

**Since S50 (D206) the dust has its own layer.** Until then the render put the
dust at the stars' one scale height, because the dust stage heats it as a slab
mixed with them, and an edge-on frame showed no lane (#109). The ism stage now
publishes `gas_scale_height` per ring — the gas's column over four times its
midplane density, the h of the one layer form, missing past the stellar disc's
edge — and `/api/render` returns it as the dust's (`layers.dust` names the
array `dust_height`, kpc): 21 pc at the centre, 113 pc at R₀ against the thin
disc's 356, passing the stars' height near 13 kpc `[verified:
model/galaxy/stages/ism.py; tests/test_dust_layer.py]`. The viewer reads the
height ring by ring and cuts every sub-step that crosses the layer at fixed
multiples of the dust's height, composing the pieces front to back, so the
stars in front of the dust are not dimmed by it: within 0.6 % of the two
layers' own integral from face-on to cos i = 0.1 `[verified:
frontend/src/galaxy/regimes.ts, composeStep; regimes.test.ts]`. An inclined
disc shows a dark lane inside the stellar light, and a face-on ring far thicker
than τ = 1 shows about half its light where the mixed slab showed 1/τ.
**Stated, not hidden (#128):** the energy budget is still the mixed slab's —
the dust's heating, its scattered share and the frame's balance are computed
as before — so the picture's geometry and the budget's now differ; the layered
geometry would absorb 0.77 of what the slab does.

**Since S50 (D207) the dust is placed round each ring.** `/api/render` returns
`dust_placement` (R, φ), the pattern's density contrast — the gas the dust is a
share of is taken to follow it, as the azimuthal star formation already reads
it — and the viewer multiplies the ring's depth and thermal light by it; the
scattered light is already a share of the placed stars. Every ring keeps its
dust. Because the stars follow the same factor the arms are muted and reddened
by their own dust rather than crossed by lanes: at R₀ an arm lets through 0.747
of its light and a gap 0.874, and a ring's face-on V light falls by 1.3 %
`[verified: tests/test_dust_layer.py]`. A lane needs a gas pattern distinct
from the stars', which the model does not publish (`RESEARCH_AREAS.md` §1).

**Since S50 (D208) the points are on the field's scale.** The star-first mode
draws the N brightest disc stars in view and every cluster as points of their
own published light through the filter set (`response`, over the white point),
each sprite summing to that light over the area of sky one pixel covers at the
point — the unit the march integrates — over the render's remainder
(`stars_unresolved`, at the bright header's own threshold), with one exposure
for both; the dust between a point and the camera dims it per channel from the
march's own textures. This is §7's no-double-counting made visible: the frame's
summed light with the points on equals the whole starlight's with them off to
0.9995 / 0.9997 / 1.0006 through rgb `[verified: DECISIONS.md D208, measured
on screen; frontend/src/galaxy/flux.test.ts for the scale and the dust's
segment]`. #114 (points painted as blackbodies) and #115 (the young population
drawn twice) no longer apply in this mode; they remain the field mode's.
Since S64 (V6, R8) the bright stars come by tiles: the view's footprint as
level-0 cells, one grid threshold per frame picked from `/api/bright?table=1`
(the smallest at which the tiles in view hold at most the point budget in
expectation), each tile asked at it (`cells=`, the same bytes every time), and
the remainder under that threshold as `/api/render?only=remainder`'s two
per-ring arrays placed by the render's own `stars_middle_placement` and
`stars_placement` — the full `l_min=` render's `stars_unresolved` bit for bit
`[verified: tests/test_v6_bright.py]`; the whole render is not asked again on a
threshold change (T28). The frustum cut is the GPU's clipping; the points are
every star of the tiles in view above the threshold, not the N brightest.
Since S65 (V6b, RULING_S65 R1) below the stars handover (4 kpc) the tiles are
level-k cells, k the field mode's `levelFor` (1 for 1-4 kpc, 2 for 0.25-1, 3
below): `cells=<level-k ids>&level=k`, a level-k tile's rows its finest cells'
rows — the level-0 tile's restricted to them, row for row — and the counts
`table=1&cells=<ids>&level=k`, each the sum of its finest cells' (never the
whole level-k table); a tile whose level-0 ring holds more than 5 x 10^6 stars
above the threshold is refused before any draw (#159); below 4 kpc the budget
weighs each cell by the share of the stars' layer inside the frustum's height
range (the mean over 3 x 3 points across the cell), and a cell is asked only
when its weighted count is at least one star, the skipped cells' sum stated
beside the threshold as the rule's loss `[verified:
tests/test_v6b_points.py]`. The zoomed-in point layer is the bright catalogue,
complete above the frame's threshold; the level-k star sample stays the field
mode's region regime.

**Since S63 (D223) the stars are split by age.** `/api/render` returns
`stars_young`, `stars_middle` and `stars_old` per ring and filter — the bright
catalogue's three age parts (`bright.AGE_PARTS`: younger than the cluster
window, 0.02 Gyr; to `YOUNG_STAR_AGE`, 0.1 Gyr; older), each its own spectrum's
response through the curves (`bright.part_anchors`, the decomposition `l_min=`
reads) scaled by its ring's closure factor `stars / Σ parts`, so the three sum
to the stars' ring value per ring and filter to rounding `[verified:
tests/test_render.py]`. The factor's largest departure from 1 is stated per
filter (the join is not linear: 4.9 × 10⁻⁶ through rgb, to 2.4 × 10⁻³ through
the narrowband sets). The header's `ages` names, per part, the (R, φ) array the
viewer multiplies its ring value by: the old by `stars_placement` (the stellar
contrast, as `stars` is placed), the middle by `stars_middle_placement`
(`sfr_modulation` over its ring mean), the young by `dust_placement` (the gas's
own contrast — the clusters sit in the clouds; where no dust placement is shipped the header names
`stars_young_placement`, and `stars_placement` for a model with no gas pattern: the header's name rules, S63). Each weight averages to 1 round
every ring, so the placed parts keep each ring's light; they are `stars` split,
never light beside it.

**Since S64 (T5) the region's clouds dim a star only behind them.** The region
march's transmission pass writes, beside the whole ray's T, the clouds' front:
the optical-depth-weighted entry distance −Σ τ t0 / Σ τ in its alpha (`NO_FRONT`,
1, where no cloud's optical depth is met). The star points draw after the
multiply quad and take T themselves, read once per star at the pixel holding its
centre, only where the star is farther from the camera than the front (strictly:
a star exactly at the front is drawn undimmed); the field
is still multiplied by the whole ray's T, in front of a cloud as well (the
stated approximation; the exact composite, T at K depth slabs, is not built)
`[verified: frontend/src/galaxy/regionDepth.test.ts]`. FluxPoints' own dust is
per point along its segment and was already depth-correct.

**Since S64 (BUILD_III V6) the clouds are extinction at galaxy scale.** `/api/clouds`
carries `cloud_dust_extinction_v`, each cloud's face-on mean A_V from its own dust:
`cloud_mass` x `dust_to_gas_ratio` x (`dust_extinction_v` / `dust_surface_density`),
the ring terms read at `cloud_birth_radius`, over pi `cloud_size`^2 (the radius) -
derived in the API from published fields, no stage; the clouds stage's own
`cloud_extinction_v` (S40, 2.97 mag for every cloud) is on another law (debt #167).
`/api/render` carries `dust_diffuse_share` per ring - 1 less the ring's realised
clouds' dust over its published dust, summed off the ring-first draw's streams, no
census materialised, the same layer on and off - and the header's `clouds` states the
rule "diffuse depth(R, phi) = depth(R) x dust_placement(R, phi) x dust_diffuse_share(R)"
and the closure: per level-0 ring the share times the ring's dust plus the census's
clouds' dust is the ring's dust to 1e-12 (measured under 1e-15)
`[verified: tests/test_v6_clouds.py]`. The disc's realised clouds hold 0.490 of the
Milky Way's dust and 0.633 of NGC 4414's (expected, the molecular fraction: 0.548,
0.590). The viewer rasterises the whole disc's census into a polar texture of face-on
A_V, conserving each cloud's A_V x area to float32 rounding, at the "cloud raster"
tuning value (default 5 texels a render cell a side, 2000 x 1800, the finest float32
A_V texture under 16 MiB), and beside it a half-float texture of each texel's slab: the
A_V-weighted mean `cloud_height` of its clouds and a half-thickness, the rms of their
heights in quadrature with their mean radius (28.8 MB the two). The march and the
star-first points compose each texel's clouds as a uniform slab at those heights, cut
with the dust's pieces; against brute-force integration the step misses by at most 0.51 %
of the unattenuated light, and with no clouds it is the dust-only step to the bit
`[verified: frontend/src/galaxy/cloudOpacity.test.ts, regimes.test.ts]`. Stated, not
hidden: a texel holding one cloud is that cloud at its own height and extent; one holding
several is one slab spanning them, which in the inner disc, where a texel gathers clouds
far apart in height, still draws thin vertical streaks on an inclined view (half-thickness
up to 1.1 kpc MW, 3.0 kpc NGC 4414). The clouds sit up to 3.8x (MW) higher than the gas
layer D211's heating and the scattered light were computed in (debt #168).

**Since S64 (BUILD_III V6) the HII regions are knots at galaxy scale.** `/api/clusters`
with `filters=` carries `line_response`: each region's Hα (`hii_halpha_luminosity`),
Hβ (over `hii_balmer_decrement`) and the four forbidden lines (times `hii_*_ratio`),
each through each curve at its wavelength by `spectra.line_response` - the lines of the
render's `halpha_hii` and `lines_hii`, one for one. Its header's `knots` names the light,
the size (`hii_stromgren_radius`: the line light's sphere; the bubble is the shell's
object) and the naming cell, the level-0 layout, and the rule the render's two HII abouts
repeat: in a level-0 cell c the field's HII layers are scaled by 1 - D_c / K_c, D_c the Hα
of the knots drawn in c, K_c of every knot c names; a cell naming no knot (no region
realised) by 1 - d, d the drawn share of the disc's knots' Hα - so the screen holds
the census exactly where every knot is drawn and the field where none is, never both, never
negative `[verified: tests/test_v6_knots.py]`. The census against the field (§7's check,
not a target): the knots' Hα is 0.921 of the field's (MW), 1.081 (NGC 4414), per ring
0.53-1.43 and 0.37-2.15; the field in cells naming no knot, Hα no knot realised: 1.29 % and 5.5 % of the HII
Hα. The viewer draws the knots in the field mode above the region regime, on the field's
scale at its weight, dimmed by the field's dust, and hands the march the per-cell share;
a knot is a point until 2 R_S fills a pixel, then a disc of R_S summed over its own box.
In the star-first mode a cluster whose 2 r_h fills a pixel is a Plummer sphere of
a = r_h / 1.3048, each pixel the profile's exact integral over it over the box's (the light
to 1e-12; none fills a pixel in a star-first capture) `[verified:
frontend/src/galaxy/plummer.test.ts, knots.test.ts]`. Not built: the region regime's
clusters keep their sprite (they are drawn in display colours, not on the field's scale).

**Since S66 (BUILD_III V7, the model's side) `/api/render` carries what the march needs to
draw the randomness layer once per ray as a thin screen at the midplane**, every number the model's (D226 R4-R6): the header's
`gas_fluctuation` (the field's seed, form, ring table, ladder weights and cell normalisers),
`census_clustering` (the clustering field's form, its octaves' survival ages and the 1-, 2- and
3-octave maps' means per level-0 cell on its table lattice, the 3-octave one the published
`census_clustering_cell_mean` to the bit) and `spurs` (the gas spurs' table and their ring mean
per render ring), each stating its rule, their values null with the layer off; and the arrays
`dust_placement_unspurred` (the gas pattern's cell means without the spurs, which composed
through `Spurs.compose_cells` give `dust_placement` to 1e-12; the neutral placement with the
layer off) and `stars_middle_kept3/2/1` (the middle part's light of the age windows that keep
3, 2 and 1 clustering octaves, summing with the rest to `stars_middle` to 1e-12). No array sent
before moved, on eight requests against S65's bodies. The noise the march evaluates is one GLSL
include (`frontend/src/galaxy/noise.glsl.ts`) with a float32 TypeScript twin held to the
model's vectors: the hash and the noise bit-exact to numpy's float32, the gas sum at numpy's
read positions bit-exact, the composed g within 4.9e-4 of float64; on the RTX 4070 the GLSL
itself within 5.5e-7 of float32 on the primitives and 1.7e-3 on g `[verified:
tests/test_v7_header.py, frontend/src/galaxy/noise.test.ts, frontend/e2e/noise.spec.ts]`.

**Since S66 (V7, the march's side) the field's march evaluates the layer once per ray** (D226
R3-R5 as amended): the three maps are face-on column maps read as a thin screen at the ray's
crossing of the midplane (a ray that does not cross it inside the march reads at its start
point's projection), each value multiplying every sub-step's placement, which is still read per
sub-step. The alternative was measured and set aside: a column map drawn through the layer makes
each feature a pillar of the layer's height, smeared by h tan i along the view (the streaks of
the first capture); a thin screen at the midplane displaces nothing - a declared approximation.
The gas fluctuation map multiplies the dust's
placement (its depth, thermal light and diagnostic, not its scattered light); the gas spurs are
drawn from their table, `(1 - <S>(R))` times the unspurred placement plus their sum; the field
mode's young light and the middle part's kept shares are multiplied by the 1-, 2- or 3-octave
clustering map over its level-0 cell's mean. Each is a tuning switch ("gas fluctuation", "spurs",
"young light clustered" in the march), drawn only with the layer on: under "physics only" the
frame is S65's byte for byte. Held: the dust-only frame's light with the gas map and the spurs over
both off 1.000553 (gate 3e-3; the gas map alone 1.000545, and 1.000247 when the maps were read per
sub-step); per level-0 ring on a
capture's own pixel lattice, at 16 offsets, the dust's column and every clustered part,
young and kept, within the derived one-draw bound 3 sqrt((e^v - 1) g^2 / N_r) of a log-normal map
point-sampled on the ring's pixels (worst 2.93 of it; debt #176) `[verified: tests/test_v7_layer.py,
frontend/e2e/picture.spec.ts]`. Not modulated: the star-first points' dust (the ring's placed
column, R7) and the star-first remainder's middle part (R5e) - debts.

**The ruling V1 made (S38): option (a).** The paragraph below is the question as
it stood; the answer is `/api/render` (`model/galaxy/stages/spectra.py`,
`api/service.py`): the viewer sends its curves as numbers (the sets are
`frontend/src/galaxy/filters.json`; a request naming a set without curves is
refused, since the model holds none), and the model returns the stars per
(R, φ) cell, the Hα and the dust per ring and the bulge per filter, never
composited; the viewer divides by a white point and multiplies by its exposure
`[verified: tests/test_render.py]`. The stellar spectrum is the population's
own eight-band SED (`disc_sed_*`, `bulge_sed_*`, λL_λ at the SVO reference
wavelengths), joined by power laws made band-consistent, blackbody tails beyond U
and K; the frame through the table's B and V reads B − V +8.9 × 10⁻⁵ and M_V
−1.7 × 10⁻⁴ mag from Phase 3's, tolerance 10⁻³. The first cut (one blackbody at
the colour temperature, M_V 0.71 mag bright) is kept in the test as the record.

**One ruling this contract leaves open, for V1.** §3a says the model ships the
spectrum function and the renderer calls it, and §2a says the viewer holds the
filters. In this repository the model is Python behind an HTTP API and the
viewer computes no physics (rule D5), so "the renderer calls the function" means
one of two things, and V1 must rule:

- *(a)* the viewer sends a filter set (named, or its curves) with a request and
  the model returns each component's per-channel response per cell, three or
  four floats per cell per component — the payload of today's RGB texture, the
  filter integral run once server-side;
- *(b)* the model publishes each component's spectrum *basis* (a table over its
  shape parameters on the shared wavelength grid, plus the line list) and the
  viewer integrates against the filters itself.

(a) keeps D5 and A9 intact and is recommended `[inferred]`; (b) moves an
integral into the viewer and needs D5 amended. Either way the filters are the
viewer's data and the model holds no palette.

---

## 1. The problem this contract solves

A galaxy view spans ~30 kpc at ~10 pc resolution. A nebula view spans ~10 pc
with structure to ~0.01 pc. That is six orders of magnitude in linear scale and
eighteen in volume.

**No grid spans it and no catalogue holds the stars.** So the contract is not a
list of fields at one resolution. It is two things:

1. **Field-level output** — smooth, galaxy-scale, published by the model.
2. **A region contract** — a small parameter vector per object, from which the
   renderer synthesises interior detail on demand, deterministically.

The model does not produce pillars, filaments or clumps. It produces the
**conditions that generate them**, and the statistics they must obey.

---

## 2. Emission is published as components, not colours

The model must not publish RGB, and must not publish a single "brightness"
field. It publishes **five physically distinct emitting components**, each with
its own spectrum:

| Component | Emits | Determined by |
|---|---|---|
| Stellar photospheres | continuum | L, T_eff per star (Phase 3) |
| Ionized gas | recombination + forbidden lines, free-free continuum | Q(H⁰), n_e, T_e, abundances |
| Photodissociation region | PAH features, H₂ lines | radiation field at the ionization front |
| Dust (warm and cold) | modified blackbody | heating balance, β |
| Shocked gas | [S II]-enhanced lines | shell velocity, ambient density |

Extinction applies to components 1 and 2; the energy removed is what components
3 and 4 re-emit. **That closes a loop, and the loop is a test** (§7).

### 2a. Why components rather than colours

Because every display mode the viewer offers is then the *same mechanism*:

| Display | Is just |
|---|---|
| Broadband RGB | three wide filters |
| SHO / HOO false colour | three narrow filters |
| "As JWST" | NIRCam filter set + hexagonal PSF |
| "As Hubble" | WFC3 filter set + Airy PSF |
| Single-line map | one filter |

The viewer holds the filters. The model holds no opinion about palette at all.

---

## 3. Spectra: continuum grid plus a line list

A narrow emission line on a coarse wavelength grid is lost, and narrowband false
colour is *made of* narrow lines. So a component's spectrum is **two objects**:

- **`continuum`** — on a shared log-spaced wavelength grid, 0.1–30 µm.
- **`lines`** — an explicit list of (wavelength, flux) pairs, evaluated exactly.

The line list must include at minimum: Hα 6563, Hβ 4861, [O III] 4959/5007,
[S II] 6717/6731, [N II] 6548/6583, plus the PAH features at 3.3, 6.2, 7.7, 8.6
and 11.3 µm `[recall — NEEDS SOURCING]`.

**[S II]/Hα separates shocks from photoionization for free** once both are
published. No extra field.

### 3a. Payload discipline — do not publish spectra per cell

A 128-point spectrum on a (R, φ) grid is the 288-million-cell mistake again.

Instead: **per cell the model publishes the handful of parameters that determine
each component's spectrum, and ships the spectrum function as model-side code.**
The renderer calls that function (see §0 for what "calls" means here). This
keeps the payload at a few floats per cell, and it keeps rule A9 satisfied —
there is exactly one rendering opinion and the code computing the field holds it.

The shape parameters are small:

| Component | Parameters per cell |
|---|---|
| Stars | mass-weighted T_eff mix, surface density, [Fe/H] |
| Ionized gas | Q(H⁰) surface density, n_e, ionization parameter, O/H, S/H, N/H |
| PDR | radiation field strength G₀, PAH abundance |
| Dust | Σ_dust, T_dust, β |
| Shocks | shell velocity, ambient n |

---

## 4. Emissivity is volumetric, not a surface

**This is the requirement most likely to be got wrong once and be expensive to
retrofit.**

A wind-blown bubble reads as a sphere because the line of sight passes through
more shell material tangentially than face-on — limb brightening. Every
edge-brightened filament, every bubble rim, every bright-rimmed pillar face is
this effect.

If emission is drawn as a surface texture, a bubble renders as a flat disc.

So at region scale the model publishes **emissivity per unit volume**
(erg s⁻¹ cm⁻³ per unit wavelength) and the renderer integrates along the ray.
The shell appears for free and is correct for any viewing angle.

Galaxy-scale fields may remain surface quantities, because the disc is optically
thin and integrated through by construction. **The transition point must be
stated in the field docstrings**, or the two will be silently mixed. (The
repository's galaxy-scale light is already a surface quantity with a stated
vertical profile the ray-marcher applies, D167; region-scale emissivity is new
and must be declared volumetric in its `FieldDecl` — a new unit in the closed
vocabulary, which is a `core/` edit plus a DECISIONS entry.)

---

## 5. The region contract

### 5a. Cloud vector

One record per molecular cloud. Everything the renderer needs to synthesise the
interior, and nothing else.

| Field | Why it is needed |
|---|---|
| `cloud_id` | |
| `position` (R, φ, z) | placement |
| `mass`, `radius` | mean density |
| `density_gradient` (magnitude + direction) | **bubbles sit off-centre** because they expand into a gradient; without this every shell is concentric and wrong |
| `mach_number` | sets σ_s² = ln(1 + b²ℳ²) `[recall — NEEDS SOURCING for b]`, the log-normal density PDF that **generates clump-and-filament structure** |
| `metallicity` ([Fe/H], [α/Fe]) | O/H and S/H for line ratios; dust and PAH abundance |
| `age` | which state it is in |
| `state` | embedded / blown open / dispersing / remnant |
| `cluster_id` or null | the embedded cluster, if any |
| `ionizing_source_offset` (vector) | **which way the pillars point** — they are the shadows of clumps that survived the front eating the cloud from one side |
| `seed` | deterministic regeneration |

The Mach number and the source offset are the two that do the visual work. Mean
density alone produces a fog.

In this repository a cloud is an **object class** beside `star`, declared with
`FieldDecl(kind=Kind.COLUMN, of="cloud")` columns and drawn per cell exactly as
stars are, so that a region's clouds are the same clouds a sweep would give
(D60). The `seed` is the cell-and-index path, not a stored number.

### 5b. Cluster object

Clusters are their own class, not a label on stars.

`cluster_id`, position, mass, half-mass radius, age, bound flag, metallicity,
`Q_ionizing`, `wind_luminosity`, `seed`.

**This unifies with BUILD_II Phase 5.** Globular clusters are the surviving
massive end of the same mass function, so one mechanism produces both, and the
η relation becomes a check on it rather than a separate assertion.

Since S33 (BUILD_II Phase 11) the cluster is an object class (`of="cluster"`)
served by `/api/clusters`: one per cloud past its embedded phase, named by the
cloud's cell and its `cloud_cluster_index`, placed at the cloud's embedded source
(`cloud_source_angle` read from the outward radial direction toward increasing
azimuth `[inferred]`), with `cluster_ionizing_photons` and `cluster_wind_luminosity`
the IMF integrals at its age times its mass `[verified:
model/galaxy/stages/clusters.py; tests/test_clusters.py]`. The `seed` is the
cell-and-index path, as for clouds.

### 5c. On-demand resampling

The star catalogue is a sample, not a census. Zooming to pillar scale needs stars
down to the bottom of the IMF inside a tiny volume.

**Interface requirement:** the model exposes a function
`sample_region(bounds, seed) -> stars`, deterministic in its arguments,
independent of what has been sampled before. Regions are generated and discarded,
never stored.

The repository has this at galaxy scale already (`/api/region`, D60, D167:
§0). What it lacks is depth: a cell is kiloparsecs across and the sample size
that would fill a 10 pc window with the whole IMF is ~10¹¹ stars galaxy-wide.
The interface change is a **cell hierarchy** — level-0 cells are today's; a
level-k cell is one of 4ᵏ children with its own stream, and a request names the
level it wants — with the prefix property (a smaller sample is a prefix of a
larger one) holding within a cell and the union property (a parent's stars are
its children's) holding across levels. That is the piece most likely to be
missed until the viewer needs it.

---

## 6. Clumping: one mechanism, two payoffs

Emission measure goes as n²ℓ, and ⟨n²⟩ ≠ ⟨n⟩². The mean density gets nebular
brightness wrong by a large factor.

The clumping factor comes from the **same log-normal PDF** that generates the
pillars. Build it once; it corrects the photometry and draws the structure.

---

## 7. Consistency constraints

These are tests, not guidelines, and they belong in the suite.

**Energy balance.** Ultraviolet and optical light absorbed by dust must equal the
infrared re-emitted. This catches an extinction law and a dust emission model
that disagree — exactly the class of defect that put the extinction coefficient
out by a factor of 162, which no test caught `[verified: DECISIONS.md D163]`.

**Catalogue against field.** Integrate the resolved star catalogue over a patch;
compare against the galaxy-scale surface brightness field at that patch. They
must agree within Poisson noise. If they do not, the zoom will visibly not match
the wide view.

**Modulation is a redistribution.** Any azimuthal or clumping modulation must
integrate back to the axisymmetric quantity. Assert it. (`pattern_density_
contrast` already averages to 1 around every ring `[verified: tests/test_pattern.py]`;
Phase 2's star-formation modulation must do the same, weighted by gas.)

**Region determinism.** `sample_region` called twice with the same arguments
returns the same stars. Called on overlapping bounds, it agrees on the overlap.
Across levels of the hierarchy, a parent's stars are its children's.

---

## 8. What the renderer may not do

**Every visible feature traces to a published field, or to the randomness layer: a synthetic field the model
publishes, on the model's seed.** The failure mode is unchanged — a galaxy-flavoured noise generator with a
physics model bolted to the side — and what keeps the layer from being one is that it is the model's, it
conserves every total, its statistics are sourced, it names the physics it stands in for, and it can be switched
off to show the physics alone.

Specifically forbidden:
- frame-seeded or time-seeded noise (it would shimmer, and it is not a structure)
- detail the model does not publish: structure, parameters or seeds of the viewer's own
- colour applied for appearance rather than derived from the filter integral
- a synthetic field tuned to a picture rather than to its cited statistic

*Amended 2026-10-03 on the owner's word (BUILD_III §7, ruling 3; Appendix A)* `[verified: DECISIONS.md D212]`.
**Until D212 this section read:** "Every visible feature traces to a published field or to a seeded draw from
one, and the seed comes from the model, not from the frame", with a paragraph on noise textures as rule A4 read
backwards — the renderer inventing structure the physics does not have, hard to detect after the fact because it
looks correct — and its second ban was "detail added below the scale the cloud vector constrains". The layer
itself is built from S55 (BUILD_III Phase R); until then no synthetic field exists.

The viewer's clump lattice and Hα knots (§0) were the one standing exception,
dated; V2 removed them at S39, and nothing of that kind may be added.

---

## 9. Out of scope, deliberately

Recorded so these read as decisions rather than oversights.

**Interacting and merging systems.** `mergers[]` is a history of completed
events, not a second body present in the frame. Tidal tails, bridges, a shared
non-axisymmetric potential and merger-triggered bursts are not expressible, and
the SFH is smooth by construction. The model generates one galaxy.

**Environment.** No intracluster medium, no cluster membership, no cooling-flow
filaments, no active nucleus. These are properties of *where a galaxy lives*, not
of the galaxy. The model has a dark matter halo and nothing outside it.

Background galaxies and foreground stars in a rendered field are viewer-side
decoration and are fine; they carry no physics and must not be described as if
they do.

**Named objects.** The model produces a morphology class at a given metallicity
around a cluster of a given mass. It does not produce a particular nebula, and
attempting one would be fitting with the answer known (rule B5).

---

## 10. Sourcing still owed

Everything marked `[recall — NEEDS SOURCING]` above, plus:

- ~~the turbulence forcing parameter b in σ_s² = ln(1 + b²ℳ²)~~ — read at S32 (Federrath et al. 2010, D181)
- ~~Case B Hα yield per recombination, and the Hα/Hβ ratio~~ — read at S35 from Storey & Hummer 1995's tables (D184)
- ~~dust albedo and scattering asymmetry g in V, and R_V~~ — read at S31 from Draine's table (D180); the
  table's extinction curve and albedo per wavelength read at S39 for the per-filter dust (`spectra.GRAIN_TABLE`)
- ~~modified blackbody emissivity index β~~ — read at S31 (Planck 2013 XI, D180)
- the Henyey–Greenstein phase function — read at S39 (Bosschaart & Olofsson 2026, arXiv:2604.08379 eq. 3)
- PAH feature wavelengths and their metallicity dependence
- ~~the wind bubble solution's constants (Weaver et al. 1977) and the Sedov phase~~ — read at S36 from Weaver's scan, Kim & Ostriker 2015, Chen & Slane 2001 (D185)
- the hydrogen-ionizing photon rate Q(H⁰) as a function of T_eff and L (Phase 3)
- the filter curves of every named filter set the viewer offers (V1)

None of these enter code from recall.
