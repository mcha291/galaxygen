# READING_CLOUD_LAYER — the molecular layer's thickness: the clouds' scale height (S67, D229)

**The lead's note (2026-10-18, entered at S67 on the owner's order).** The owner: "read a source for the clouds'
scale height and fix the layer in the model before I retune." Until S67 the cloud census drew each cloud's height
from a sech²(z/2h) layer at `CLOUD_LAYER_SHARE` 0.5 of the thin disc's scale height (177.8 pc on `milky_way`, 477 pc
on `ngc_4414`), "a stated guess with no source" (debt #95); D228 measured the clouds floating to 1.95 kpc and the
viewer's whole-galaxy clouds drawing near-black. One blind Opus reader (no repository access) read the sources
below; what is below the rule is its report in substance, the quotations as the reader gave them. **What the lead
took from it** (D229 rules on it): (1) the Milky Way's molecular layer at R0 is about 120 pc FWHM, roughly
independent of R from 2 kpc to R0 (Bronfman et al. 1988, via Ferrière 2001), with 118 pc (Bronfman et al. 2000) and
136 ± 17 pc (Clemens, Sanders & Scoville 1988) beside it and Malhotra 1994's σ_z 58 pc at R0 (FWHM 137) the high
reading; (2) massive clouds sit in a layer as thin as the CO layer or thinner (Stark & Lee 2005); (3) the layer flares
outside R0 (Nakanishi & Sofue 2006, FWHM 160-186 pc at 8-11 kpc) and the sources conflict inside R0 (Marasco et al.
2017 falling with R, Malhotra and Nakanishi & Sofue rising); (4) edge-on spirals' CO widths are σ = 31-89 pc plus 1-5
pc/kpc × R (Yim et al. 2014). The layer is entered as an absolute thickness, the level-0 constant
`MOLECULAR_LAYER_FWHM` = 120 pc, `[verified: Bronfman et al. 1988 via Ferrière 2001 §II.B]` (was §II.A; *re-read at Audit V (S70)*; the passage is
in §III "Interstellar Matter", its molecular-gas subsection, III.2 as ar5iv numbers it - the print's lettering not
checked; re-read at S95, reader R, F-R-3); the clouds' scale height is the sech² h whose FWHM that is,
h = FWHM / (4 artanh(1/√2)) = FWHM / 3.5255 = 34.04 pc (D229).

---

## The reading (the reader's report, 2026-10-18)

Conversions: a Gaussian's σ = FWHM / 2.3548 = HWHM / 1.1774; a sech²(z/2h) layer's FWHM = 3.5255 h.

- **Malhotra 1994** (ApJ 433, 687; astro-ph/9404028; "rising" read in the abstract at S95, reader R - the 58 pc and
  5.5 pc/kpc not). A Gaussian σ_z rising with R: ~10 pc at 2.6 kpc, 30-52 pc over
  3.4-7.2 kpc; the fit "extrapolates to give a scale height 58 pc at R⊙" (FWHM 137 pc); the gradient 5.5 pc/kpc.
- **Clemens, Sanders & Scoville 1988** (ApJ 327, 139), read via Ferrière 2001 (RMP 73, 1031) §II.B (ar5iv §III.2; F-R-3): FWHM
  136 ± 17 pc at R0, ∝ R^0.58 (read at S95, reader R).
- **Bronfman et al. 1988** (ApJ 324, 248), read via Ferrière 2001 §II.B (ar5iv §III.2; F-R-3): "a FWHM of 120 ± 18
  pc, roughly independent of R" from 2 kpc to R0 (read at S95, reader R). **The value entered** (`MOLECULAR_LAYER_FWHM`).
- **Bronfman et al. 2000** (A&A 358, 521; astro-ph/0006104), Table 7 and §4.1: a mean half-width of 58-60 pc for
  R/R0 0.2-1.0, "118 pc (FWHM) for the layer of molecular gas traced by CO"; the OB stars' layer FWHM 73 pc, "62% the
  thickness of the molecular gas disk" (a disclosed check on the HII layer, not a pin).
- **Roman-Duval et al. 2016** (ApJ 818, 144): the inner Galaxy's FWHM ~110 pc; the diffuse molecular gas 130-200 pc;
  the outer Galaxy 110-300 pc.
- **Marasco et al. 2017** (arXiv 1707.00743): the HWHM from ~100 pc at the centre to ~50 pc at R0 (52 pc held fixed
  beyond 7 kpc) - falling with R inside R0, against Malhotra's and Nakanishi & Sofue's rise.
- **Su et al. 2021** (ApJ 910, 131): a thin component of FWHM ~85 pc and a thick one of ~280 pc.
- **Nakanishi & Sofue 2006** (PASJ; astro-ph/0610769), Table 1, the sech² FWHM: 48 pc at 0-1 kpc rising to 90 ± 30 pc
  at 7-8 kpc, 186 pc at 8-9 kpc, 160 pc at 10-11 kpc - the flaring outside R0. (The bins read in the table's printed
  layout, 9-10 kpc 182 ± 20 between them: read at S95, reader R.)
- **Stark & Lee 2005** (ApJ 619, L159): clouds below ~2 × 10⁵ M☉ have a scale height of ~35 pc, "not significantly
  different" from the CO layer's; the most massive clouds sit in a thinner layer.
- **Yim et al. 2014** (arXiv 1408.5905), Table 3, edge-on spirals' CO: σ = 89 + 5.0 R pc (NGC 4157), 33 + 1.1 R pc
  (NGC 4565), 31 + 2.7 R pc (NGC 5907), R in kpc - the bracket `ngc_4414`'s one value is disclosed against.
- **HI at R0**, for scale: FWHM 230 pc (Dickey & Lockman 1990, via Ferrière 2001).
- **Heyer & Dame 2015** (ARA&A) was not read: the fetch returned 403.

Read 2026-10-18 by a blind reader (no repository access); quotations as the reader gave them.

---

## Part S89 — what #180's closer needs that the repository does not hold (2026-11-04, no web access)

Read beside today's model at S89 (BUILD_V row 89). The layer is one constant, `MOLECULAR_LAYER_FWHM` 120 pc (h 34.04
pc), drawn at every radius for every cloud and both templates; since S89 (#168) the dust stage heats the clouds' share
of the dust in that layer too, so the layer now reaches the infrared numbers. What a radial or mass law would need:

- **The flare outside R0.** Nakanishi & Sofue 2006's Table 1 whole, every radial bin with its error: the reader above
  quoted four (48 pc at 0-1 kpc, 90 ± 30 at 7-8, 186 at 8-9, 160 at 10-11), and the two outer bins fall again, so no
  flare law can be fitted to what is held.
- **Inside R0, a ruling.** Bronfman et al. 1988 (flat, the value entered), Marasco et al. 2017 (falling from ~100 pc HWHM
  at the centre to ~50 pc at R0 — the R0 end not measured: the scale height is fixed at 52 pc beyond 7 kpc, their
  Table 2's 52 ± 40, ad hoc (re-read at Audit VI, 1B's notes)) and Malhotra 1994 / Nakanishi & Sofue (rising) conflict: by B12 they are named
  rulesets, and which one the model draws is the owner's choice, not a reader's.
- **A mass dependence.** Stark & Lee 2005's table of cloud heights by mass (the reader gave ~35 pc below ~2 × 10⁵ M☉ and
  "thinner" above, no number), or a catalogue's heights binned by mass (Miville-Deschênes et al. 2017's whole-Galaxy
  catalogue holds each cloud's latitude and distance `[recall]`).
- **NGC 4414's own layer.** An edge-on CO thickness for NGC 4414 is impossible (it is inclined ~55°); a template's own
  layer would need a population law (Yim et al. 2014's σ = a + b R over three spirals is a bracket, not a law).

---

## Part S98 — the clouds in the plane against the gas ridge: their shape, where they sit, whether they join, the weight that places them, and a step in the gas field (2026-11-12, BUILD_VI row 98; the measurer)

**The note.** S98's measurer (an Opus agent, read and run only, in two passes; its note `s98_M.md` in the session's
scratchpad, its scripts and logs `s98_M_*` beside it) read the code and S96's saved answers — the `/api/clouds` windows
`s96_P_clouds_<template>.npz` (4-9 kpc, all φ; 6530 clouds on `milky_way`, 1901 on `ngc_4414`) and the `/api/render`
grids `s96_P_render_<template>.npz` (400 × 360 cells, 75 pc × 1°, 0-30 kpc). No server was started and no new model
run made. This part is about the clouds in the plane, where the part above is about their layer's thickness. File and
line references are the measurer's reading of the code at 08ff7e9; numbers are measured unless tagged `[inferred]`.
The register (#228, #229, #230) carries the gate's ruling (D267).

### S98.1 What the code says (read, not assumed)

- **The viewer's ellipse.** `frontend/src/galaxy/cloudOpacity.ts` lines 190-198 (`cloudRaster`) draw each cloud as an
  ellipse of the SAME AREA π s² (s = `cloud_size`, its radius): semi-axes `along = s √q`, `across = s / √q`, with q =
  `cloud_axis_ratio ^ elongation` (`cloudEllipse`, line 100); the long axis is r̂ turned by `cloud_angle` towards φ̂.
  S97's area-preserving assumption is **CONFIRMED**, at the default elongation 1 (`tuning.ts` line 196, `cloudElongation:
  1`; range 0-2, a display control). A cloud whose long diameter 2a is under the smaller side of its texel is deposited
  whole in one texel (round in effect; line 199); the texel is 5 per render cell a side (`CLOUD_RASTER`, lines 33-37) =
  15 pc in R, 0.2° in φ (21 pc at 6 kpc).
- **The census's shape.** `model/galaxy/api/v6_clouds.py` lines 77-127 (`cloud_shape`): k = sense × strain[the level-0
  ring of `cloud_radius`]; q = (2 + k² + |k| √(k² + 4)) / 2; angle = atan2(q − 1, k), from r̂ towards φ̂. **The angle and
  the ratio are ONE value per level-0 ring**: every cloud in a ring has the same shape and orientation; neither reads the
  gas pattern or the arm, only the fluctuation field's shear. S97's "about 30° from the tangent at k = −1.2" is this
  formula's arithmetic (q 3.12, 119.5° from r̂ = 29.5° from φ̂). **The ellipse and the angle hold against the code.**

### S98.2 The ridge's direction (what the measurer used, and why)

The field is `dust_placement_unspurred` (`gas_density_contrast`'s cell means without the spurs — the gas pattern the
diffuse dust follows). A gradient structure tensor (σ 2 cells) read the ridge as nearly tangential (a pitch of 1-15°
at crests that visibly drift 1.6° per row, a pitch of about 18° at 8 kpc), and was REJECTED. The measurer used the
pattern's own drift instead: for each cell, the azimuthal shift (searched ±15 cells at 0.1 cell) that best correlates
row i − 2 with row i + 2 (0.3 kpc apart) in a Gaussian window of σ 6°; the ridge angle = atan2(R × shift, 0.3 kpc),
then smoothed (a correlation-weighted circular mean, σ 2 rows × 3°). The arm pieces' catalogue pitches were NOT used
(the gas answers the pieces in its own frame, and the ridge is what is drawn). On `milky_way` at 8-9 kpc the drift
ridge (a pitch of 14.5° at the clouds' median) and the crests tracked one by one (15.6° at 8 kpc) agree; on `ngc_4414`
they do not (drift 47-54° at the clouds, tracked 31-33° at 4-6 kpc, 26-54° at 8 kpc): **the flocculent pattern's
direction is poorly defined, and every NGC 4414 angle below carries that.** (The second pass corrected the first's
reason for rejecting the tensor: S98.6.)

### S98.3 The clouds' long axes against the ridge

Angles from r̂ towards φ̂; diff = the cloud's axis − the ridge's axis, folded to (−90°, 90°]. The census's own
`cloud_angle` (two values per 1-kpc band = two level-0 rings): `milky_way` 57.7-63.3° from r̂ (= 27-32° from the
tangent), q 2.5-4.0; `ngc_4414` 57.5-66.0° (24-33° from the tangent), q 2.5-5.1. The ridge and the clouds lean the SAME
way (both trailing in this frame); the clouds are the more open. "On-arm" = F above the row median and drift
correlation above 0.5.

| ring kpc | MW N | MW ridge angle median [p16, p84] | MW diff median [p16, p84] | MW on-arm diff | NGC N | NGC ridge angle | NGC diff | NGC on-arm diff |
|---|---|---|---|---|---|---|---|---|
| 4-5 | 1329 | 29.6 [−5.0, 47.4] | +28.5 [−0.4, 54.0] | 790: +28.9 [14.5, 52.8] | 583 | 39.0 [−4.1, 59.8] | +18.6 [4.8, 60.6] | 331: +18.6 [4.3, 58.7] |
| 5-6 | 1045 | 54.3 [9.7, 76.9] | −0.4 [−16.4, 45.5] | 605: +2.0 [−15.1, 40.4] | 396 | 40.6 [3.2, 62.0] | +20.8 [1.7, 58.1] | 239: +13.0 [0.6, 54.5] |
| 6-7 | 810 | 70.0 [36.4, 78.9] | −11.9 [−18.9, 16.0] | 474: −10.7 [−18.9, 10.5] | 213 | 43.0 [23.6, 71.8] | +16.1 [−10.1, 35.6] | 113: +8.2 [−10.4, 33.9] |
| 7-8 | 637 | 75.1 [28.4, 80.0] | −17.1 [−20.8, 6.9] | 402: −17.5 [−21.3, 23.4] | 140 | 36.6 [12.0, 62.5] | +20.5 [−5.1, 41.8] | 80: +13.9 [−12.0, 41.1] |
| 8-9 | 1647 | 75.5 [64.5, 78.9] | −17.8 [−21.2, −7.5] | 961: −18.2 [−21.8, −15.4] | 272 | 39.3 [12.1, 66.9] | +18.3 [−9.4, 45.4] | 153: +15.1 [−10.7, 45.6] |

On the Milky Way's arms (6-9 kpc) the clouds' long axes sit **11-18° off the gas ridge**, more open than the arm (about
30° from the tangent against the ridge's 11-20°), the 16-84 % band about 20-35° wide — all of the spread from the
ridge, none from the clouds (one angle per ring). At 4-5 kpc (inside the bar, half-length 5 kpc) the offset is **about
29°**, the bar's lanes more open still. On NGC 4414 the median offset is **16-21°** with a band 45-65° wide: the
flocculent ridge's direction is itself ill-defined. With the rejected tensor the `milky_way` medians would read −16 to
−26° — the same sign and order.

### S98.4 Where the clouds sit against the gas crest (the null: the same clouds' radii at a uniform azimuth, seed 1)

| ring kpc | MW F at cloud / row median [p16, p84] (null) | MW percentile in row (null 0.50) | MW top-quarter share (null 0.25) | MW offset / crest spacing (null) | NGC F / median (null) | NGC percentile | NGC top quarter | NGC offset / spacing (null) |
|---|---|---|---|---|---|---|---|---|
| 4-5 | 1.05 [0.90, 1.88] (1.00 [0.89, 1.28]) | 0.60 | 0.35 | 0.23 (0.26) | 1.12 (1.01) | 0.58 | 0.33 | 0.21 (0.27) |
| 5-6 | 1.06 [0.86, 1.29] (1.00) | 0.59 | 0.33 | 0.21 (0.27) | 1.13 (1.02) | 0.60 | 0.36 | 0.20 (0.23) |
| 6-7 | 1.08 [0.80, 1.44] (0.99) | 0.63 | 0.36 | 0.20 (0.26) | 1.02 (1.02) | 0.53 | 0.26 | 0.25 (0.24) |
| 7-8 | 1.07 [0.80, 1.27] (1.00) | 0.62 | 0.31 | 0.22 (0.25) | 1.05 (0.91) | 0.55 | 0.29 | 0.21 (0.28) |
| 8-9 | 1.07 [0.83, 1.33] (1.01) | 0.59 | 0.36 | 0.22 (0.24) | 1.03 (1.00) | 0.56 | 0.25 | 0.23 (0.27) |

The clouds do NOT sit on the ridge; they lean to it weakly: 5-8 % above the row median at the median cloud, a third
(against a quarter) in the top quarter of the gas, a median offset of 0.20-0.23 of the crest spacing against
0.24-0.27 at random. On NGC 4414 beyond 6 kpc the preference is nearly gone. (The offset in pc depends on the drift
ridge's angle and is not tabulated; the ratio is angle-free.)

### S98.5 Whether they join: the viewer's own ellipse

Two clouds touch when their centre distance d < r_i(u) + r_j(u), r(u) the ellipse's radius along the centre line u
(exact for contact along that line; an ellipse pair can overlap off the line slightly before this fires, so a small
under-count). "End to end along the arm" = touching with u within 30° of both clouds' ridge axes. Elongation 1 is the
viewer's default, 2 the control's maximum, 0 round; "aligned" = the counterfactual with each long axis laid on its
local ridge (the same q, the same areas). S97's upper bound (centres closer than a_i + a_j) was 0.41-0.69 on
`milky_way`.

| ring kpc | MW any touch (e1) | MW end to end along the ridge: e1 / aligned / e2 / round | MW largest along-ridge chain e1 (aligned) | NGC any touch (e1) | NGC along the ridge: e1 / aligned / e2 / round | NGC largest chain e1 (aligned) |
|---|---|---|---|---|---|---|
| 4-5 | 0.516 | 0.242 / 0.378 / 0.193 / 0.254 | 12, 0.36 kpc (34, 0.65) | 0.425 | 0.226 / 0.300 / 0.187 / 0.196 | 9, 0.58 (16, 1.01) |
| 5-6 | 0.339 | 0.199 / 0.250 / 0.188 / 0.163 | 8, 0.49 (7, 0.12) | 0.255 | 0.126 / 0.164 / 0.104 / 0.101 | 4, 0.11 (5, 0.17) |
| 6-7 | 0.343 | 0.220 / 0.243 / 0.225 / 0.163 | 9, 0.51 (8, 0.26) | 0.174 | 0.117 / 0.136 / 0.108 / 0.028 | 3, 0.03 (3, 0.03) |
| 7-8 | 0.281 | 0.157 / 0.188 / 0.176 / 0.132 | 4, 0.10 (4, 0.25) | 0.086 | 0.057 / 0.071 / 0.071 / 0.043 | 2, 0.03 (2, 0.03) |
| 8-9 | 0.401 | 0.248 / 0.263 / 0.271 / 0.208 | 13, 0.18 (14, 0.16) | 0.092 | 0.055 / 0.055 / 0.055 / 0.011 | 3, 0.06 (3, 0.06) |

The median ellipse at e1: `milky_way` 39-49 × 11-17 pc; `ngc_4414` 43-67 × 12-22 pc. The share of clouds in
along-ridge chains of 3 or more: `milky_way` 0.09-0.15 (aligned 0.10-0.28); `ngc_4414` 0.00-0.13. With the true
ellipse **a quarter or less touch a neighbour end to end along the arm** (`milky_way` 0.16-0.25, `ngc_4414` 0.06-0.23),
and the longest such chain is 4-13 clouds, 0.1-0.5 kpc. Turning every cloud onto the ridge raises that share **by at
most 0.14** (4-5 kpc), mostly by 0.01-0.05; doubling the elongation does nothing. **The orientation is not what keeps
the clouds from joining into lanes: their number density along the ridge and their weak preference for the crest
are.** (S97 ranked the size against the pixel first, the orientation second, the count last; this measures the second
as small and puts the placement beside the count.)

### S98.6 Why the clouds barely prefer the crest: the weight that places them (second pass, SP-1)

**The rule, read.** A cloud's azimuth is placed in two stages, with the layer on:
1. **Its sector** (a level-0 cell, 32 rings × 32 sectors; `stages/systems.py` lines 91-92). The ring's cumulative
   sector weights are inverted at the cloud's own `sector` uniform (`stages/clouds.py` lines 301-308, `allocate`,
   called at line 352). The weights are `stages/clouds.py` lines 257-283 (`sector_placement`): the gas pattern's exact
   sector means (`pattern.sector_means`, clipped at 0) **times the census clustering field's mean over the cell**
   (`field.sector_factors`, S90's #161), over their mean round the ring (`census_clustering.ring_unit`). So the weight
   is **linear** in the gas contrast, multiplied by the clustering field's cell mean.
2. **Its place inside the cell.** `layer/census_clustering.py` lines 183-212 (`place`): drawn jointly in R and φ on the
   cell's lattice, each point weighted by Σ_H2(R) R × the pattern's point function (read on a 16 × 24 mesh, clipped at
   0; `mesh_factor`, line 205) × the clustering field's map (line 204). Again **linear** in the gas contrast, multiplied
   by the clustering field. Called from `stages/clouds.py` line 505.
- Not a power of the gas, not the molecular fraction (Σ_H2 enters only as the radial law within the cell), not the
  star-formation modulation. With the layer off: uniform in the sector, the sector uniform too (`clouds.py` lines
  498-501). **No register entry owned the rule** (#161, struck at S90, the nearest) — now #229.

**The measurement** (the saved 4-9 kpc windows; bands R0 ± 0.5 kpc; each cloud's row quartile and decile of F =
`dust_placement_unspurred`; "prop. F" = the share a draw proportional to F would put there, from the same rows' values;
"prop. F²" likewise):

| template | R0 | N | top quartile by number / by mass | uniform | prop. F | prop. F² | top decile by number / by mass | uniform | prop. F | prop. F² | row p90 / p50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| milky_way | 5 | 1218 | 0.333 / 0.386 | 0.25 | 0.358 | 0.498 | 0.154 / 0.160 | 0.10 | 0.180 | 0.310 | 1.50 |
| milky_way | 6 | 946 | 0.332 / 0.284 | 0.25 | 0.336 | 0.426 | 0.165 / 0.128 | 0.10 | 0.144 | 0.195 | 1.37 |
| milky_way | 7 | 713 | 0.328 / 0.321 | 0.25 | 0.352 | 0.465 | 0.133 / 0.083 | 0.10 | 0.165 | 0.253 | 1.43 |
| milky_way | 8 | 647 | 0.318 / 0.329 | 0.25 | 0.328 | 0.415 | 0.153 / 0.148 | 0.10 | 0.147 | 0.207 | 1.30 |
| milky_way | 9 (8.5-9) | 2041 | 0.375 / 0.353 | 0.25 | 0.324 | 0.405 | 0.165 / 0.168 | 0.10 | 0.143 | 0.198 | 1.34 |
| ngc_4414 | 5 | 485 | 0.359 / 0.431 | 0.25 | 0.361 | 0.482 | 0.155 / 0.161 | 0.10 | 0.157 | 0.226 | 1.70 |
| ngc_4414 | 6 | 311 | 0.289 / 0.233 | 0.25 | 0.335 | 0.429 | 0.125 / 0.091 | 0.10 | 0.142 | 0.193 | 1.51 |
| ngc_4414 | 7 | 156 | 0.269 / 0.479 | 0.25 | 0.351 | 0.464 | 0.096 / 0.302 | 0.10 | 0.157 | 0.232 | 1.51 |
| ngc_4414 | 8 | 135 | 0.289 / 0.264 | 0.25 | 0.322 | 0.397 | 0.111 / 0.024 | 0.10 | 0.136 | 0.177 | 1.36 |
| ngc_4414 | 9 (8.5-9) | 317 | 0.265 / 0.270 | 0.25 | 0.293 | 0.339 | 0.095 / 0.109 | 0.10 | 0.123 | 0.150 | 1.17 |

- **The linear expectation holds on the Milky Way**: the clouds sit where a draw linear in the gas contrast puts them
  (top quartile 0.32-0.38 against 0.32-0.36 expected), so the weak preference is the rule doing what it says. **The
  square expectation**: a draw in F² would put 0.41-0.50 in the top quartile.
- **The rule is weak because the contrast is shallow**: a row's 90th percentile is only 1.3-1.5 times its median at
  5-9 kpc; a linear draw on a field that varies by ±30 % can only lean by ±30 %.
- **NGC 4414 beyond 5.5 kpc** falls BELOW the linear expectation (0.27-0.29 against 0.29-0.35; small N, 135-317) — the
  measurer's reading: the clustering field's cell means, multiplied in, outweighing a shallow contrast there. **Not
  separated** (the cell means are published as `census_clustering_cell_mean`; not fetched).
- The mass columns swing (NGC 4414 at 7 kpc: 0.479 by mass against 0.269 by number) because a few massive clouds
  dominate small bands.

### S98.7 A step in the Milky Way's gas field (second pass, SP-3)

The statistic: J = the median over azimuth of |F[i+1] − F[i]| at fixed φ; a pair is flagged where J > 3 × the median J
of its 10 neighbouring pairs and J > 0.01, over 0.5-14 kpc. The typical J at 4-10 kpc is 0.029 on `milky_way` and 0.015
on `ngc_4414`, against a row standard deviation of about 0.23-0.24.

| template | boundary R kpc | J | max abs dF | neighbours' J | J / row std | nearest level-0 edge (pc away) |
|---|---|---|---|---|---|---|
| milky_way | 2.025 | 0.043 | 0.77 | 0.009 | 0.03 | 1.9125 (112) |
| milky_way | **5.925** | **0.247** | 0.60 | 0.035 | **0.86** | 5.6625 (263) |
| milky_way | **6.075** | **0.216** | 0.59 | 0.037 | **0.70** | 5.6625 (413) |
| milky_way | 12.225, 12.375 | 0.023, 0.028 | 0.05, 0.08 | 0.007, 0.003 | 0.5, 1.7 | 12.225 (0), (150) — the pattern's outer end, row std 0.02-0.05 |
| ngc_4414 | 9.975 | 0.010 | 0.03 | 0.003 | 1.6 | the pattern's outer end (flat from 10.0 kpc) |

- **One step matters**, on `milky_way`: **a band two rows wide, R 5.9625 and 6.0375 kpc, that differs from the rows on
  either side** by 0.7-0.9 of a row's own scatter at the median azimuth, and by up to 0.6 in contrast (e.g. near φ 89°:
  1.27 at R 5.89, 1.05 at 5.96, 1.30 at 6.11). Elsewhere the field is smooth row to row; `ngc_4414` has no interior
  step.
- **Not on a level-0 ring edge** (the edges are 0.0375 + k × 0.9375 kpc, #202's text: 5.6625 and 6.6; the band is
  263-413 pc from the nearest). **Not #202's**: #202's diffuse dust share has been continuous since S89, its largest
  change between rows here 0.026 (`milky_way`, at 4.425 kpc) and 0.033 (`ngc_4414`), and it moves
  `dust_diffuse_share`, not `gas_density_contrast`. No register entry found — now #230.
- **The cause NOT traced.** The suspects, by `stages/gas_pattern.py`'s own text: the solver's per-ring profiles carried
  along the arm pieces' loci and blended linearly in R (lines 614, 1142-1204), or the bar's taper (lines 45-47, 305-314)
  near 6 kpc, about 1.2 bar half-lengths `[inferred]`. Neither was read through.
- **The first pass corrected.** The first pass blamed the row steps for the structure tensor's failure; the steps are
  confined to this band (and the pattern's outer ends), yet the tensor also read the ridge as near-tangential at 8 and
  10 kpc, where there is no step. So the steps explain its failure at 6 kpc only; at 8-10 kpc it is unexplained. The
  drift-correlation ridge and the tracked pitches stand as measured.

### S98.8 Not measured (as the measurer lists it)

- The S96 windows only (4-9 kpc, the layer on, the templates' seeds); no fresh `/api/clouds` call; no 10 kpc cloud
  ring.
- The viewer's raster depositing a cloud whose 2a is under its texel side (15 pc in R, 0.2°) whole into one texel: not
  modelled; the touching test is in the plane, not on the raster or the capture's pixel.
- The ridge's direction is a choice among three (S98.2); NGC 4414's is poorly defined.
- How #144's / #129's pinned 0.37 was measured: not read; the definitions may differ.
- The clustering field's part of NGC 4414's shortfall (S98.6): not separated.
- The step's cause (S98.7): not traced; the gas solver's radial sampling (`gas_response.CELLS` per ring) not read.
- No file in any repository changed; no server started; one python process at a time.

## Part S99 — the clouds' arm contrast against the gas's in mapped galaxies: the weight's power read (2026-11-12, BUILD_VI row 99; the reader)

**The note.** S99's reader (`s99_R.md`, item 2) fetched each paper below from arxiv.org this session, the text by
`pdftotext -layout`; Colombo et al.'s Table 2 also through ar5iv by a summarising fetch asked for the rows verbatim —
the two agree row for row. `[verified: source, place]` marks a quotation from those texts; `[inferred]` the reader's
own arithmetic (`s99_R_c14.py`, its log ending EXIT=0). The question was #229's closer: the arm to inter-arm contrast
of molecular clouds, in number or mass per area, set against the gas's in the same mask. The gate's ruling is D269
ruling 5 and the register's #229 / #231.

### S99.1 Colombo et al. 2014 — M 51's clouds by environment (READ)

- **Source.** Colombo et al. 2014, "The PdBI Arcsecond Whirlpool Survey (PAWS): Environmental Dependence of Giant
  Molecular Cloud Properties in M51", ApJ 784, 3, arXiv:1401.1505v1. Beam "(1.16 x 0.97)" arcsec, "~40 pc" at 7.6 Mpc;
  CO(1-0), CPROPS, 1507 GMCs; X_CO 2 × 10²⁰ constant (Sect. 5.2).
- **The mask.** Centre R_gal < 1.3 kpc; the "disk" 1.3 ≤ R_gal ≤ 5 kpc "divided azimuthally into spiral arm (SA) and
  inter-arm (IA) zones". App. C: the arm width is kinematic — "take the width of the signal at 95% maximum as our
  measure of the kinematic arm width", "centered on the spiral arm ridge located by eye", "assumed to be symmetric".
  **No width in pc is printed.** From Table 2's areas the arm mask is 14.6 / (14.6 + 27.8) = **0.344 of the disc's
  area** `[inferred]`.
- **Table 2, the three rows verbatim** (columns: (1) A kpc², (2) L_CO 10⁷ K km/s pc², (3) Σ_H2 M☉/pc², (4) A_work, (5)
  L_CO work, (6) L_NX, (7) L_EX, (8) %NX, (9) %EX, (10) #, (11) N_GMC kpc⁻²) `[verified: Colombo et al. 2014, Table 2]`:
  - "SA | 14.6 | 43.44 | 129.94 | 2.3 | 35.10 | 8.16 | 23.22 | 21 | 59 | 657 | 45"
  - "IA | 27.8 | 21.88 | 34.37 | 1.0 | 9.12 | 4.93 | 10.93 | 19 | 42 | 514 | 19"
  - "CR | 4.7 | 25.47 | 237.02 | 1.2 | 22.85 | 4.71 | 14.48 | 18 | 57 | 335 | 73"
  - Sect. 5.2: "The number density of clouds, NGMC, shows a similar trend as Sigma_H2, decreasing from 72 kpc-2 in the
    central region to 45 kpc-2 in the spiral arms and 19 kpc-2 in the inter-arm region."
- **The arithmetic** `[inferred: s99_R_c14.py]`, arm over inter-arm in the same mask:

| statistic | SA / IA | exponent against the gas (ln ratio / ln 3.781) |
|---|---|---|
| all CO, Σ_H2 (the gas) | **3.78** | 1 |
| GMC number per area | **2.43** | **0.67** |
| GMC CO luminosity per area, extrapolated (mass at constant X) | **4.05** | **1.05** |
| GMC CO luminosity per area, not extrapolated | 3.15 | 0.86 |
| mean GMC luminosity per cloud | 1.66 | — |

  Shares in the arm mask (34 % of the area): the gas 0.665, the cloud mass 0.680, the cloud number 0.561.
- **The table's own inconsistency.** L_CO × 4.37 / A reproduces Σ_H2 on every row (α 4.35-4.38), so the SA, IA and CR
  rows are internally consistent. **The sub-environment rows are not**: L_EX exceeds the region's whole L_CO for DWI
  (7.23 > 5.50) and MAT (5.27 > 3.50), and %EX does not equal L_EX / L_CO for SA (0.53 against 59) or IA (0.50
  against 42) — as printed in both the PDF and ar5iv. The sub-region rows are not used. (An inconsistency of the
  source's table, not a model finding.)
- **Against the model** `[inferred: the reader]`: the model's crest over the inter-arm median (1.4-1.8) is not this
  statistic — Colombo's is a ratio of means over a broad kinematic mask, a third of the area. The model's equivalent
  would be the mean gas and the mean cloud count / mass inside an arm mask holding 34 % of a ring band's area centred on
  the ridge, over the mean outside; the exponent (the clouds against the gas in the same mask) is the mask-robust
  quantity to carry, not the contrast itself.

### S99.2 Koda et al. 2009 — M 51's GMAs (READ, a letter)

ApJ 700, L132, arXiv:0907.1656v1; CARMA + NRO45, CO(1-0), "4 resolution" (arcsec as extracted; no pc read).
Qualitative only: "clearly indicating many GMCs with mass exceeding 4 x 10^5 Msun in the inter-arm regions"; "only 36%
of the inter-arm CO emission is seen in the detected discrete clouds"; "The most massive structures with 10^7-8 Msun,
referred to as GMAs, are found only in spiral arms, not in inter-arm regions" `[verified: Koda et al. 2009]`. **No
number or mass per area by environment, no areas** — the direction of S99.1 (the arm's excess carried by heavier
structures), not a number.

### S99.3 Rosolowsky et al. 2021 — PHANGS-ALMA's clouds in four discs with arms (READ: Sects. 2, 6.2.2, Table 5)

arXiv:2101.04697, "Giant Molecular Cloud Catalogues for PHANGS-ALMA"; "a common 90 pc" resolution. The arm and
inter-arm populations are for "the four galaxies with defined spiral arms" "(NGC 0628, NGC 1637, NGC 3627, NGC 5643)";
Table 5: arm N = 931, inter-arm N = 903 (clouds, no areas). Sect. 6.2.2: "the truncation mass in the Spiral Arms is a
factor of 2.5 higher than the truncation mass in the Interarm regions, showing that more massive clouds are found in
Spiral Arms"; the masks "set Spiral Arm regions to have a minimum width of 1 kpc. If we defined the Spiral Arm region
with a more restricted area around the molecular gas ridge line, the Arm-Interarm contrast would likely become
stronger" `[verified: Rosolowsky et al. 2021, Sect. 6.2.2, Table 5]`. **No per-area statistic** in what was read;
independent of Colombo on the mass-per-cloud half only.

### S99.4 Hirota et al. 2024 — M 83 (READ: Sects. 3.3, 4)

arXiv:2410.05424v1, "Whole-disk sampling of molecular clouds in M83"; "a spatial resolution of 46 pc", "5724 molecular
clouds". The mask: "each of the logarithmic spiral arm regions has a width of 40" (880 pc)"; "Out of 734 clouds with >
10^6 Msun in M83, 498 clouds reside in the arm/bar/center mask. The total mass of > 10^6 Msun clouds is 2.2 x 10^9
Msun and about 80% of the mass is included in the mask" `[verified: Hirota et al. 2024, Sect. 3.3]`. **The mask's area
share is not printed** in what was read, so no contrast.

### S99.5 What no source gives

- **No source read prints a law** (an exponent of the clouds' density on the gas's contrast). The one area-normalised
  table is Colombo et al. 2014's: **one galaxy** (M 51, grand design, interacting), 1.3-5 kpc, a broad kinematic mask.
- **No flocculent disc**: none of the four papers covers NGC 4414's kind; Rosolowsky et al. exclude galaxies without
  arms from the arm / inter-arm populations ("GMCs from galaxies without arms or bars (NGC 3521, NGC 3621, NGC 4826)
  are not included").
- **Not read**: Meidt et al. 2021 and Querejeta et al. 2021 (they compare CO against the stellar contrast — the gas's
  contrast, which the model takes from Querejeta et al. 2024, #130), Hughes et al. 2013 (CO brightness PDFs; gas, not
  clouds) — stopped on the time box.
- No scatter is printed (one galaxy); the 0.86-1.05 bracket from the catalogue's extrapolation is the only spread.

### S99.6 The reader's recommendation and the gate's ruling

- **The reader**: keep the first power, close #229 as permanent with the reason written in, plus one optional sourced
  build. By mass M 51's clouds follow the gas to the first power in the same mask (1.05; 0.86 without CPROPS's
  extrapolation) — the model's linear weight is what the one area-normalised source supports; a squared weight (S98's
  0.41-0.50 top-quarter share) has no source. By number the clouds are less concentrated than the gas (0.67): the
  arm's excess is carried by heavier clouds (mean luminosity 1.66 times in the arms; Rosolowsky et al.'s truncation mass
  2.5 times over four galaxies; Koda et al.'s GMAs "only in spiral arms"; Hirota et al.'s 498 of 734 clouds over 10⁶ M☉
  and about 80 % of their mass in M 83's mask). The optional build, in the reader's words: "number weight
  contrast^0.67 with the mass function's upper cut scaled by contrast^0.38 (so mass stays ~linear) - Colombo's one
  galaxy, or the truncation-mass factor 2.5 arm/inter-arm from Rosolowsky et al. as the cut's step". Sureness (the
  reader): the exponents' arithmetic high; Colombo's SA / IA rows high; "first power by mass" as a general law
  **low-medium** (one galaxy, one mask, a grand design, masses at constant X); the flocculent case **not covered**.
- **What it settles for a lane** (#228, #144): no sourced weight gathers the clouds onto a ridge more tightly than the
  gas; a shallow lane is the gas field's, not the clouds' weight.
- **The gate's ruling (D269 ruling 5): #229 discharged on evidence** — by mass the one area-normalised source has the
  clouds follow the molecular gas to the power 1.05, the model's first power; the citation is in the code
  (`stages/clouds.py` `sector_placement` and `layer/census_clustering.py` `place`, lane M's 6ae82ab: the cloud census
  read the same before and after, `cloud_count_total` 17263.580633491907 both). What the reading leaves is **#231**
  (carried): the model's cloud mass function does not know the arm — a sourced build the adopted list (D268) does not
  hold, the owner's to order. **A lane cannot come from the clouds' weight**; the gas law's frame is ruling 9's.
