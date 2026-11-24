# READING_PICTURES — why the two field frames are far from their goal pictures (S96, D265)

**What this is (2026-11-12, the reading session's second part).** A diagnosis, not a change. A Fable analyst built the
model's own face-on maps from the published `/api/render` arrays (no exposure, no tone curve, no bloom, no points) and
ran `tools/goal_metrics.py`'s statistics on them, ranking the gaps between each committed field frame and its goal
picture as **model**, **display** or **metric**, with a predicted number for an experiment that would confirm each. An
Opus runner then re-took the two committed field captures through the project's own Playwright path, one display
setting changed at a time, and marked each prediction HELD, KILLED or PARTLY. Nothing was tuned, committed or changed;
no byte under `model/galaxy` moved. **Rule C6: a goal picture is never a target.** Every display value below is a
setting the owner may try live, not a default the project adopted (the display defaults are the owner's, D227). Tags:
`[verified: s96 analyst's maps]`, `[verified: s96 experiment, capture re-taken]`, `[inferred]` where a note marks a guess.
Not committed (in the session's scratchpad): the notes `s96_P.md`, `s96_X.md`; the PNGs `s96_P_model_*.png`, `s96_X_*.png`.

## 1. The yardstick at this date

The statistics are the tool's: D(B−R) the colour step outer minus inner band; A₂ the m = 2 amplitude over 0.2–0.8 a;
B the blue arm / interarm ratio; dark the share of pixels under 0.75 × the local median; slope the power spectrum's
between 10 and 50 cycles per a `[verified: s96 analyst's maps]`.

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm/interarm B | dark | slope (rms) |
|---|---|---|---|---|---|---|---|
| GOAL milky_way | −0.354 (−0.46 / −0.81) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 (0.232) |
| FRAME milky_way-field | −0.322 (+0.64 / +0.32) | 0.056 | 0.053 | 0.053 | 1.60 | 0.0315 | −1.26 (0.373) |
| GOAL ngc_4414 (q 0.5736) | −0.329 (+0.51 / +0.18) | 0.101 | 0.074 | 0.056 | 2.67 | 0.154 | −2.10 (0.390) |
| FRAME ngc_4414-field | +0.185 (+0.31 / +0.50) | 0.091 | 0.185 | 0.042 | 2.57 | 0.031 | −2.12 (0.242) |

The Milky Way pair is not read over the same radial range: a spans 1.7 scale lengths in the goal and 3.85 in the
frame (a = 0.59 of the frame's half-side against the goal's 0.72 — corrected at S97: the 0.29 first written here was a
over the picture's width, 300 of 1024 px, beside the goal's a over its half-side); the goal's kpc scale (~15 kpc for a) is the
analyst's inference from its bar taken as 5 kpc `[inferred]`. NGC 4414's pair spans like ranges (2.9 against 3.1).

## 2. How each half was done, and what it could not do

- **The analyst's maps.** `/api/render` (rgb set, white 6500 K, the s93 bundles), the tool's functions imported, sky 0,
  geometry given. Not measured: `/api/layer`'s fields (gas fluctuation, clustering maps, spurs' heights) and the clouds'
  own columns are NOT in the maps, so "dark 0.0000" and "slope −4.7" are the smooth arrays', not all the model
  publishes; bloom not emulated, ACES approximated (Narkowicz's fit), so every "by subtraction" rests on that; the
  thick-disc reading a 1-D smear, not a march; the white-point shift hand computed; `/api/bright` not probed; the units
  of `hii_stromgren_radius` and `cloud_size` taken from the values; no experiment run by the analyst.
- **The runner's captures.** `npm run build`, the API on its own port, a temporary spec on `picture.spec.ts`'s path
  (tuning via `localStorage["galaxygen.tuning.<template>"]`, the Exposure slider, `__galaxygenCapture.place`), each
  gain read back. **Both controls byte-identical to the committed PNGs** (sha256 ccb214cd… / c8a235fc…)
  `[verified: s96 experiment, capture re-taken]`. Metrics at the committed frame's own geometry (the tool's estimate in
  brackets). Not run: "bloom 0 at 55°" (row 5's second half); E1's and E3's two settings not separated; no goal picture
  re-measured (the goal numbers are the analyst's).

## 3. The gaps, ranked (the analyst's order; the runner's results)

| # | gap | verdict | the analyst's number | experiment (exact setting) | before → after | result |
|---|---|---|---|---|---|---|
| 1 | NGC 4414's colour step of the wrong sign | display | model's own map −0.28 (dust) / −0.38 (none); the same map through exposure + ACES +0.005 `[inferred: ACES approximated]` | E1: tuning `toneMapping: "linear"`, `bloomStrength: 0` | D(B−R) +0.185 → **−0.258** (in +0.651 / out +0.392) | **HELD** |
| 2 | dark lanes: Milky Way 4.8× the goal's as dashes, NGC 4414 a fifth | model (lanes absent) + display (dashes) | smooth maps with all dust: dark 0.0000 in both; NGC 4414's A_V 3.8–88 mag inside 3 kpc, placement ≤ 2.4× the ring mean under a 0.93 kpc stellar layer | E2: tuning `cloudsExtinction: false` | MW 0.0315 → **0.0180**; NGC 0.0309 → **0.0187** (goal 0.154) | **KILLED** — predicted under 0.01; the clouds' extinction is about half the dark fraction (−43 % / −40 %), the rest unattributed (grain and other features) |
| 3 | the Milky Way's bar / A₂ 0.053 (goal 0.194) | model mostly, display second | bar in the model's light A₂ 0.137 peak at 2.5 kpc against the goal's 0.29–0.34 (2.4×); arms outside the bar 0.02–0.05 against 0.13–0.30; the frame 0.060 at r/a 0.21 | E3: tuning `bloomStrength: 0`, Exposure slider −1.5 | A₂ 0.053 → **0.083** [0.088]; r/a 0.21 0.060 → **0.159** | **PARTLY** — the headline stops short of 0.10, but the bar rings overshoot the analyst's smooth map (0.123): the display takes more than half the bar |
| 4 | no pink knots, twenty large dots (one cause) | display + model | the dots = HII knots: 13 of the 20 brightest beyond 10 kpc; Strömgren radii ≤ 26 pc (< 1 px); analyst's "7.3× the field by pointGain 4 / starsIntensity 0.55" | E4: tuning `pointGain: 0.55`; E4b: tuning `knots: false` | E4: every metric unchanged; E4b: the dots gone, slope −1.26 → −0.90 | E4 **KILLED**, E4b **PARTLY** — the knots do not follow the point gain (`knotsGain` = … × `fieldGain` × 2^exposure × `weights.field`): the dots are HII knots at the field's gain |
| 5 | NGC 4414's A₂ 0.185 at one phase (the minor axis), a burnt core | metric (inclination) + model + display | thin disc 0.035; the stars' h 0.926 kpc smeared 0.089–0.099 `[inferred: 1-D smear]`; frame's own outline q 0.774 | E5: camera `inclination_deg: 0` via `place()`, `--axis-ratio 1` | A₂ 0.185 → **0.032** | **HELD** — the m = 2 is the inclination / geometry, not a bar |
| 6 | the Milky Way's slope −1.26 (goal −1.99) | display (the number) | −2.24 under a 3×3 median; the smooth map −4.7, rms 0.085 against the goal's 0.232 | E4 / E4b above | E4 −1.26 → −1.26; E4b → −0.90 | **KILLED** as worded — the slope is the points' uniform 3 px speckle, not the knots |
| 7 | burnt-out core (both) | display on a model cusp | 3.4 / 3.8 stops over at the peak pixel; the disc at 4 kpc 6.4 stops under it; the goal's range ~2 stops | not run alone (E3 shrinks the core to a small clipped spot) | — | not run |
| 8 | "a small tan disc" (Milky Way) | display / metric | a = 0.59 of the half-side (goal 0.72; S97 corrects the 0.29 first written, a share of the width); the colour level +1.0–1.1 mag at 6500 K; ~4000 K moves B−R by −1.10 `[inferred: hand computed, not rendered]` | not run (capture `radius_kpc` 20 → 14–15; white point → ~4000 K) | — | not run |

## 4. What the model does not hold

*(S97 traced each of these to its law: section 13 re-words the bar's row — nothing is lost inside the model, the
"2.4×" is the goal's bar against a seeded draw — and finds NGC 4414's layer to be a radius the height is read at.
Section 8 re-words two rows of section 3: row 1's sign is turned by the bloom alone, and row 6's speckle is the young
light's clustering in the march, not the points.)*

- **Connected dust lanes** (row 2): the smooth maps read dark 0.0000 with all the dust composed; the dashes are isolated
  clouds (axis ratio ≥ 2.5, A_V 4–15) `[verified: s96 analyst's maps]`. No entry (the analyst knew none).
- **The bar's contrast in light** (row 3): A₂ 0.12–0.14 at 2.5 kpc against the goal's 0.29–0.34 — 2.4× under; and no
  two-armed mode outside it (A₁, A₄ larger than A₂). The notes name #80 (the bar) and the arms' m = 2 share as the
  pinned table's, the owner's ruling (#138).
- **The knots as regions, and where the brightest are** (row 4): every Strömgren radius under one pixel; 31 % of the
  Milky Way's knots beyond 10 kpc, 301 beyond 20 kpc. The notes name #183 (the knots' colour); #181 (one Strömgren
  sphere each, never a complex) is the register's entry for the size.
- **NGC 4414's thick stellar layer** (row 5): h 0.926 kpc, 2.7× the Milky Way's (0.40 of the light's scale length),
  rounding the inclined picture and smearing any lane. No entry.
- **The cusp under the core** (row 7): the notes name #177.

## 5. What the display hides — the owner's to choose (D227)

- `toneMapping: "linear"` with `bloomStrength: 0` on `ngc_4414` turned its colour step from +0.185 to −0.258, the
  model's own sign; the picture loses its bloom ball and haloed knots and its disc reads dimmer and browner.
- `bloomStrength: 0` with Exposure −1.5 on `milky_way` raised the bar's ring A₂ at 0.21 a from 0.060 to 0.159 and made
  the S-shaped inner spiral plainly visible; the outer disc nearly fades and the darker frame inflates the dark fraction
  (0.059) and flattens the slope (8-bit quantisation).
- `knots: false` removed the twenty-odd large dots; `pointGain` does nothing to them.
- `cloudsExtinction: false` removed the dark dashes and about half the dark fraction.
- Not tried: the capture's field of view (`radius_kpc`) and the white point (row 8).

## 6. What the metric compares unlike

- **NGC 4414's A₂**: the frame's 0.185 sits at one phase on every ring because the picture is rounder than the q 0.5736
  the tool deprojects by (the frame's outline q 0.774); face-on it reads 0.032 (E5). Half or more of it is the
  inclination, not the galaxy.
- **E1's geometry**: the tool's own estimate of a moves with the display (286 → 470 px), and at that geometry E1's
  step reads −0.567 against −0.258 at the frame's; the runner measured every picture again at the committed frame's
  centre, PA and a for that reason.
- **The Milky Way's radial range**: the goal's bands at 1.7 scale lengths per a, the frame's at 3.85 (section 1).

## 7. The analyst's three things first (the analyst's judgement)

1. A display pass the owner does live, before any model work: NGC 4414's tone curve and bloom, the Milky Way capture's
   field of view and white point, the point gain (E4: it does not reach the knots; `knots: false` does) — it takes
   four of the eight gaps off the model's account.
2. Dust as connected narrow lanes: the one feature both goals share that the published fields do not hold.
3. The bar's contrast in light and NGC 4414's stellar thickness: single numbers of the model to question.

The lead's reading: D265.

---

# Part S97 — the experiments finished, and combinations for the owner to load (D266)

**What this part is (2026-11-12, S97, BUILD_VI row 97).** The same runner, the same path (the project's own Playwright
capture, one setting changed against the control, every setting read back, each picture measured at the committed
frame's own geometry `[verified: s97 experiment, capture re-taken]`): 36 captures for what S96 left unrun, then 24 on
the session's build for combinations the owner can load into the Tuning panel's new box. Both controls byte for byte
the committed frames, on both builds. **Nothing here is a default or a recommendation: the display defaults are the
owner's (D227), and no value was chosen to match a goal (C6).** Not committed (the session's scratchpad): the notes
`s97_X.md`, `s97_X2_boxes.md`; the contact sheets `s97_X_sheet_*.png`, `s97_X2_sheet_*.png`.

## 8. What S96's two-setting experiments were, separated

| # | the question | the setting, alone | before → after | what it says |
|---|---|---|---|---|
| 1 | NGC 4414's colour step: the tone curve or the bloom? | `toneMapping: "linear"` alone / `bloomStrength: 0` alone | D(B−R) +0.185 → −0.036 / → **−0.142** | **The bloom turns the sign, not the curve.** With the bloom off every curve keeps the model's sign (Reinhard −0.177, ACES −0.142, AgX −0.085, linear −0.258); linear alone clips a core of 2259 px. The viewer's plain bloom (0.35, threshold 1) under ACES keeps it too (−0.062) |
| 3 | the Milky Way's bar: the bloom or the exposure? | `bloomStrength: 0` alone / Exposure −1.5 alone | ring A₂ at 0.21 a 0.060 → **0.120** / → 0.125; together 0.159, flat from −1.5 on | Either alone doubles the bar's ring; the headline A₂ (0.2–0.8 a) never passes 0.083 at any display (goal 0.194): the rest is the model's (section 4) |
| 7 | the burnt core (never run) | Exposure 0, −1, −2, −3, with the bloom and without | near-white core r_eq 9.6 px (Milky Way) / 13.3 px (NGC 4414) at the defaults; with `bloomStrength: 0` 0.8 / 1.6 px at Exposure 0 | **The burnt ball is the bloom's**, not the exposure's: almost no pixel is clipped (3 and 61 at 255); with the bloom kept it goes only at −2 / −3 stops, when the outer disc is black (level 3 / 2 of 255 at r/a 1) |
| 8 | "a small tan disc" (never run) | camera `radius_kpc` 20 → 15, 14 / `whiteKelvin` 6500 → 5000, 4000 | a 0.59 → 0.78, 0.84 of the half-side, no colour or structure statistic moved / B−R (in / out) +0.64 / +0.32 → +0.13 / −0.35 → **−0.14 / −0.85** (goal −0.46 / −0.81) | The camera only enlarges the disc. **The white point moves the colour level about 0.5 mag per 1000 K**: the tan is the 6500 K white, and near 4000–4500 K the outer band stands beside the goal's |
| 2 | the dark dashes' other half (E2 left it unattributed) | with `cloudsExtinction: false` held: `gasInMarch: false` / `clumpsInMarch: false` / `spursInMarch: false` / `knots: false` | dark 0.0180 → **0.0005** / → 0.0097 / unchanged / unchanged; `extinctionStrength: 0` alone → 0.0000 | The clouds' extinction carries about half the dark pixels and **the gas fluctuation in the march the rest**; all of it is dust, none of it a lane |
| 6 | the Milky Way's flat slope: the points' speckle? | `spriteSize: 9` alone / `pointGain: 1` alone | slope −1.26 → −1.07 / unchanged | Neither. The one switch that steepened it was `clumpsInMarch: false` (−1.49 → **−1.99**, the goal's): **the speckle is the young light's clustering in the march**, on the disc and on the sky around it |

Row 5's bloom at 55° is row 1's run: NGC 4414's A₂ 0.185 → 0.137 with the bloom off, the inclination's share still in it (E5).

## 9. The knots: the dots are their bloom, and no display keeps the knots without it

`knotsIntensity` (S97, `tuning.ts`; 1 by default, the closure) at 0.3 and 0.1 under the owner's bloom: the Milky Way's ten
large dots outside the disc → 1 and 0; NGC 4414's fifteen → 6 and 4; the disc, the core and every other statistic the
control's. **The pink knots inside the disc fade with them**: a knot is a point under one pixel (every Strömgren radius
< 1 px, section 4) and is seen only as its bloom. A display has dots and knots, or neither; the goal's pink regions are
complexes tens of pixels across, which the model does not hold (#181).

## 10. A defect the white point shows: the field ends at a circle

At `whiteKelvin` 4000–4500 the sky inside 604 px of the centre (23.6 kpc on the Milky Way capture) is a pale blue
disc with black corners outside it; the diffuse glow and the fine speckle both stop there, with the bloom off as with it
on, and with the star-first mode's points switch off (the same bytes). At 6500 K the edge is there and too faint to
see. Its cause is not established `[inferred: the march's own extent, or the render grid's outer radius]`; entered as
#226.

## 11. Combinations measured for the owner to load

Each line of `s97_X2_boxes.md` is a copy box: paste it into the Tuning panel's "load a combination" box on its
template and press Apply (pasted through the panel, three of them gave the same bytes as the stored route). Places to
start a live pass from, with what each measured; the owner's eye decides.

| box (what differs from the template's defaults) | D(B−R) (in / out) | ring A₂ 0.21 a / A₂ | dark | core r_eq px | dots | what a viewer sees |
|---|---|---|---|---|---|---|
| GOAL milky_way | −0.354 (−0.46 / −0.81) | — / 0.194 | 0.0066 | — | — | |
| the committed frame | −0.322 (+0.64 / +0.32) | 0.060 / 0.053 | 0.0315 | 9.6 | 10 | a small tan disc, a white ball, twenty haloed dots |
| M1 `bloomStrength` 0.35, `bloomThreshold` 1 | −0.471 (+0.70 / +0.23) | 0.113 / 0.069 | 0.0503 | 0.8 | 1 | the ball and the halos gone, the bar's S plain, still tan |
| M3 `whiteKelvin` 4500, `bloomStrength` 0 | −0.662 (−0.12 / −0.78) | 0.102 / 0.064 | 0.0487 | 2.5 | 0 | a blue-white spiral, the bar plain, a blue sky |
| M4 `whiteKelvin` 4500, bloom 0.35 at 1 | −0.659 (−0.11 / −0.77) | 0.093 / 0.062 | 0.0460 | 4.3 | 3 | M3 with a soft core glow |
| M5 `whiteKelvin` 4000, `bloomStrength` 0 | −0.779 (−0.34 / −1.12) | 0.086 / 0.057 | 0.0427 | 3.1 | 0 | bluer than the goal outside; the sky's circle plain (section 10) |
| M8 M4 with `knotsIntensity` 0.3, Exposure −0.5 | −0.693 (−0.13 / −0.83) | 0.116 / 0.071 | 0.0520 | 2.5 | 0 | M4 half a stop darker, no dots |
| M9 M3 under `toneMapping` "reinhard" | −0.415 (−0.07 / −0.49) | 0.079 / 0.044 | 0.0145 | 0 | 0 | flatter and greyer, no white core, the outer arms brighter |
| GOAL ngc_4414 | −0.329 (+0.51 / +0.18) | — / 0.074 | 0.154 | — | — | |
| the committed frame | +0.185 (+0.31 / +0.50) | — / 0.185 | 0.0309 | 13.3 | 15 | a bloom ball over a faint tan swirl, fifteen dots |
| N1 `whiteKelvin` 5000, `bloomStrength` 0 | −0.285 (+0.14 / −0.14) | — / 0.129 | 0.0668 | 1.7 | 1 | a grey-white dusty disc, a small nucleus under a glow along the minor axis |
| N2 `whiteKelvin` 4500, `bloomStrength` 0 | −0.374 (−0.08 / −0.46) | — / 0.120 | 0.0647 | 0.6 | — | N1 bluer |
| N6 N2 at Exposure +0.5 | −0.347 (−0.07 / −0.41) | — / 0.099 | 0.0578 | 1.0 | — | N2 at the committed frame's brightness (level 174 at r/a 0.25) |
| N7 N6 under "reinhard" | −0.237 (−0.07 / −0.30) | — / 0.074 | 0.0234 | 0.8 | — | flatter, the outer disc brightest of all (70 at r/a 1) |

M2, M6, M7, N3, N4, N5 are in the note. In every bloom-off tile of NGC 4414 the nucleus sits under a glow drawn out
along the picture's minor axis: the model's thick stellar layer seen at 55° (section 4; S97's trace, D266).

## 12. Where this leaves the eight gaps (the lead's reading)

- **The display's, and within the owner's reach today** (rows 1, 7, 8 and the bar's half of row 3): the bloom at
  strength 2–2.25 over a threshold of 0.45 makes the white ball, reverses NGC 4414's colour and hides half the bar; the
  6500 K white makes the tan. With the bloom off or at the viewer's plain 0.35, and a white point near 4500 K, the
  Milky Way frame reads as a blue-white barred spiral and NGC 4414's colour step takes the goal's sign and size.
- **Not the display's, on these runs**: the headline A₂ (0.083 at best against 0.194), the lanes (no setting makes
  one: dark is dashes from the clouds and from the gas fluctuation), the knots as regions (section 9), NGC 4414's
  glow along the minor axis and its dark fraction (0.067 at best against 0.154), the speckle (the clustering in the
  march at the capture's scale — a viewer or a model question, not yet parted).
- **The metric's**: NGC 4414's A₂ (its inclination, E5), and the geometry the tool estimates, which moves with the
  display (a 286 → 390–480 px under AgX or Reinhard): a picture is compared at the committed frame's geometry.

## 13. The three things the model lacks, traced to the laws that set them

An analyst (Fable; read and run only, the published fields from the s93 bundles, no paper fetched) followed each of
section 4's model gaps from the field back to its constant `[verified: s97 analyst's maps]`; the chains with file and
line, the tables and the scripts are the note `s97_R.md` (the session's scratchpad). What it found re-words section 4.

- **NGC 4414's 0.926 kpc stellar layer is a radius, not a galaxy.** `thin_disc_scale_height` is one scalar per galaxy,
  h = σ_z² / (2πGΣ) evaluated at `R_SUN` = 8.2 kpc on every template (`stages/vertical.py`) (S99: built as h_R / 7.3, the law kept as `thin_disc_scale_height_dynamical`, D269). In `ngc_4414` that is
  4.90 mass scale lengths out (3.36 in the Milky Way), where Σ is 17.19 M☉/pc² against 47.13 at the same σ_z (20.74 /
  20.99 km/s): 926 against 346 pc, reproduced to five digits. No template input sets it. Read ring by ring the same
  law flares 32-fold between 1 and 8.2 kpc on `ngc_4414`, and its stellar-mass-weighted mean is 222 pc (215 on the
  Milky Way): by the model's own law the two discs are equally thin where their stars are. The pattern stage already
  holds a sourced height for any disc (`ARM_LAYER_FLATTENING` 7.3, Kregel et al. 2002): 229 pc on this template, 334
  on the Milky Way's (346 published). Seven call sites in six files read the scalar (the dust's and the clouds' layer ratio, the gas's
  midplane, the catalogues' heights, the render). Entered as #227.
- **The bar's light is the bar the law drew: nothing is lost inside the model.** `tools/goal_metrics.py`'s A_m is half
  a cosine's amplitude (its own docstring); the bar stage's `bar_contrast` is the amplitude, as its source's is. The
  template's amplitude is a seeded draw, 0.2893 (the S4G median 0.374, −0.49σ; the template pins presence, length and
  angle, not amplitude) (S99: pinned, D269); the light holds 0.294 without the bulge, 0.274 with it, 0.252 with the dust — the tool's
  0.12–0.14, section 3's row 3. By the same tool the goal's bar is 2.4 times that (S99: pinned, D269) in either convention (0.58–0.68 in
  the stage's, near the 84th percentile of the source's distribution): an artist's impression, no target (C6). What a
  source could say is the Milky Way's own bar: `READING_BAR.md` holds Portail et al. 2017's bar and bulge mass, 1.88 ×
  10¹⁰ M☉, against the model's 1.21 × 10¹⁰ (0.64 of it; the analyst's arithmetic `[inferred]` — withdrawn at S98, F-98A-1: unlike components; section 15 has
the like-for-like reading). #146's, amended.
  Outside the bar the m = 2 share of the arms' power is 0.077, as the pinned census gives (#138, the owner's).
- **No lane, for three different reasons by place.** *The arms (Milky Way 6–10 kpc, NGC 4414 beyond 4 kpc):* the gas
  answers its arms with no shock (D216's co-rotating frame; #144): its crest stands 1.5–2.0 times the ring's median
  over 3–9 kpc of arc, so the stars' transmission at the crest is 0.82–0.95 of the median's; the tool's threshold
  (0.75) needs 2.6–4.5 times the median depth inside a band under about 0.5 kpc. *The Milky Way's bar (2–5 kpc):* the
  lanes exist and are deep (transmission 0.60–0.73 of the median) but 0.5–0.9 kpc wide — `BAR_LANE_WIDTH`, "an
  unsourced placeholder" (#147) — so they fill the statistic's window and read 0.0000. *NGC 4414 inside 3 kpc:* the
  dust layer is 0.044–0.068 of the stellar layer's height, so no depth dims the stars by a quarter (the floor 0.82–
  0.86 of the median): the row above's number, not the dust's. Not binding: the render grid's cell, the diffuse /
  cloud split. The gas fluctuation composed adds dark 0.001–0.017, as specks.
- **The clouds make dashes because of their size at the pixel.** On the Milky Way the census is not sparse (a cloud's
  nearest neighbour 0.6–1.3 of its length away) but the median length is 40–50 pc, one 39 pc capture pixel; 708 of
  6530 in the 4–9 kpc windows are three pixels long. They are stretched along the fluctuation field's shear, about
  30° from the ring's tangent by the header's rule `[inferred: the analyst's arithmetic, the census's angles not
  compared with the arms' pitch]`, so neighbours lie en echelon rather than end to end. Entered as #228.

The questions these leave for a reader (BUILD_VI row 98): Kregel, van der Kruit & de Grijs 2002 — at what radius h_z
is fitted and whether it is constant with radius; Díaz-García et al. 2016's definition of A₂ (the bulge in its I₀?)
and a measured amplitude or mass for the Milky Way's own bar (Portail et al. 2017; Wegg, Gerhard & Portail 2015);
Kim & Ostriker 2002's Table 1 (the width's and the peak's definitions) and any profile of the gas across a dynamic
arm (Wada, Baba & Saitoh 2011; Dobbs & Baba 2014); a measured dust-lane width in a bar; how dark a lane is in a
face-on spiral's optical image. Not done: no re-render at another height, amplitude or gas law (none is a request
parameter and no model byte may move in this session).

---

# Part S98 — what the sources say about the three things the model lacks (D267)

**What this part is (2026-11-12, S98, BUILD_VI row 98).** Two Opus readers fetched the sources section 13's questions
named; a measurer read the model beside them. The readings themselves are in `READING_DISC_HEIGHT.md`,
`READING_BAR.md`, `READING_GAS_SHOCK.md` and `READING_CLOUD_LAYER.md` (each a part S98); this is what they do to the
pictures' gaps. Tags as those files carry them. No model byte moved; nothing is built here.

## 14. The stellar layer (#227): the sources hold one height per galaxy, constant with radius

Kregel, van der Kruit & de Grijs 2002 fit one exponential height per galaxy over the whole disc (34 edge-on spirals,
I band), assume it constant with radius on de Grijs & Peletier 1997's measurement, and print h_R / h_z = 7.3 ± 2.2
(volume-corrected) — the number the pattern stage already holds. De Grijs & Peletier: constant to first order, rising
by at most a factor 1.5 per scale length in early types and by about nothing in the latest; Ranaivoharimina et al.
2024 (46 S4G edge-ons): a factor 1.3–2.4 from the centre to R₂₅ by type. No source shows the 7.5- to 32-fold flare
the model's law gives inside the disc, and none defines "the" height at a radius. NGC 4414's own thickness: not found.
**So the mend is sourced** — the flattening the model already holds, 229 pc on NGC 4414's mass scale length (320 pc on
its photometric one; which length stands for Kregel's I-band h_R is a ruling) against the 926 pc published.

## 15. The bar (#146): the amplitude's definition matches; the Galaxy's own bar is stronger than the template's

Díaz-García et al. 2016's A₂ is the cosine's amplitude over the ring's mean of the whole 3.6 µm image (eq. 7): the
model's convention, on a denominator that holds the bulge (0.260 against the model's 0.289). Neither Portail et al.
2017 nor Wegg, Gerhard & Portail 2015 prints an m = 2 amplitude for the Milky Way. Portail et al. do print two
things the template can be read against, and it falls short of both `[verified: s98 measurer; the like-for-like cut
"outside the bulge" taken at 2 kpc, the measurer's reading]`:

| Portail et al. 2017, Sect. 9.1 | the Galaxy | the Milky Way template |
|---|---|---|
| surface density along the bar's major axis over the minor axis, at 2 kpc | "a factor of about 4" | 1.60 with the bulge (1.69 the disc alone) |
| where the two profiles cross | 6.3 kpc | 6.94 kpc |
| the non-axisymmetric long-bar mass inside 5.3 kpc, outside the bulge | 0.46 ± 0.03 × 10¹⁰ M☉ | 0.23 × 10¹⁰ outside 2 kpc (0.35 with no cut) |

This is a miss against the Galaxy's own measured bar, not against a picture: the seeded draw (0.2893, below the
population's median) gives a bar about half the mass of the one the sources fit. S97's "0.64 of Portail's mass" set
unlike components side by side (F-98A-1: their 1.88 × 10¹⁰ is a box/peanut bulge plus the long bar) and is withdrawn.

## 16. The lanes: real ones are thin, and nothing read gives the model's gas one

- **How thin and how dark.** M 51's lanes are 0.5–2″ wide in HST's V image, 20–81 pc (Schinnerer et al. 2010); at a
  lane's centre the colour against the surrounding arm changes by V−K 0.58–0.79 mag (Rix & Rieke 1993, Table 1), a V
  transmission of about 0.44–0.58 of the surroundings `[inferred: the reader's arithmetic]`; lanes lit only by their
  own galaxy dim I to no less than 0.75 of a 0.86 kpc running median (Keel & White 2001, one Sc). Rix & Rieke put the
  lanes' dust at 0.25–0.6 of the stars' height (the model: 0.09–0.50 on the Milky Way, 0.044–0.068 on NGC 4414 —
  #227 again).
- **The model's ridge** `[verified: s98 measurer]`: FWHM across the arm 1.2–2.3 kpc on the Milky Way at 6–10 kpc
  (0.35–0.47 of the spacing), 1.1–2.0 kpc on NGC 4414; crest over the inter-arm median 1.43–1.61 and 1.60–1.82.
  Twenty to a hundred times a real lane's width at a third of its depth.
- **No source gives a profile for a co-rotating arm's gas** (Wada, Baba & Saitoh 2011: no number, one figure of
  cloud spikes on an undefined, clipped ordinate; Dobbs & Baba 2014 §3.7: qualitative; Baba et al. 2015 at S96:
  offsets). **A profile exists only for a shock in an arm with a pattern speed** (Kim & Ostriker 2002, Table 1: the
  width at half way between peak and trough 0.05–0.16 of the arm spacing, peak over mean 2.1–6.5, for forcings of
  1–3 %), which D216 removed. Even that arm (155–500 pc) is wider than M 51's lanes: a lane is the dense gas at the
  ridge — the clouds — not the ridge.
- **The clouds follow the gas linearly, and the gas is shallow** `[verified: s98 measurer]`: a cloud's sector and its
  place in the cell are both weighted by the gas contrast to the first power (`stages/clouds.py`,
  `layer/census_clustering.py`); a row's 90th percentile of that contrast is 1.3–1.5 times its median, so a third of
  the clouds sit in the top quarter where a quarter would at random; 16–25 % touch a neighbour end to end along the
  ridge, the longest chains under 0.6 kpc. Their orientation is not what stops a lane (laid along the ridge the share
  rises by at most 0.14; they lean 11–18° more open than it). No source was read for the weight's power (#229).
- **A step in the gas field**: a band two rows wide at 5.96–6.04 kpc on the Milky Way, jumps of 0.7–0.9 of the row's
  scatter, on no ring edge; cause not traced `[inferred: 1.2 bar half-lengths, where the bar's gas template may
  end]` (#230).

## 17. Where this leaves the model's half (the lead's reading)

In order of what a source now supports: **the layer** (#227) has a sourced mend the model already holds; **the bar**
(#146) has a sourced miss and a choice — keep the draw with the two checks failing on record, or pin the template to
the Galaxy's own bar; **the knots as regions** (#181) were sourced at S96; **the lanes** have no sourced law in the
model's frame — a shock needs a pattern speed (the owner's, D216), and before that the clouds' weight wants a reading
(the arm to inter-arm contrast of molecular clouds in a mapped galaxy) since the clouds are what a lane is.

---

# Part S99 — the mid-batch look (D269)

## 18. What batch P's first builds do to the frames, uncommitted

**What this is (2026-11-12, S99, BUILD_VI row 99).** An Opus runner (`s99_X.md`; worktree detached at `session-99`'s
merged head 0123c7f — NGC 4414's stellar layer 926 → 229 pc, the Milky Way's bar pinned at `bar_contrast` 0.6862)
re-took the field and stars captures through the project's own Playwright path, the API on a spare port **without**
bundles (every answer computed live), at the **committed display defaults**, plus the two boxes M4 and N6 of section
11. The "before" pictures are the committed frames; the boxes' old pictures are S97's saved PNGs (`s97_X2_M4.png`,
`s97_X2_N6.png`, on 6cdef57 with the s93 bundles; no frontend change since, so the boxes differ only in the model).
The statistics are `tools/goal_metrics.py`'s at the committed field frame's geometry, the tool's own estimate in
[brackets] where it differs. **Nothing is re-committed**: no frame, no bundle, no display default — the batch's close
(S100) regenerates the frames once. **Rule C6: no number here is a target.** The first NGC 4414 field take failed the
harness's 30 s stand under live answers and was retaken with a 900 s stand; no picture is from a timed-out run.

**The Milky Way** (frame geometry: centre 519.805, 515.349, q 1, PA 25.52, a 300.3 px):

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm B | dark | slope | ring A₂ at r/a 0.21 | A₂ profile max (r/a) |
|---|---|---|---|---|---|---|---|---|---|
| GOAL (section 1) | −0.354 (−0.46 / −0.81) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 | — | — |
| committed `milky_way-field` | −0.322 (+0.639 / +0.318) | 0.056 | 0.053 | 0.053 | 1.60 | 0.0315 | −1.26 | 0.060 | 0.130 (0.89) |
| **new field, defaults** | −0.304 (+0.630 / +0.326) [−0.300] | 0.055 | **0.078** | 0.060 | **2.08** [2.07] | 0.0317 [0.0320] | −1.27 [−1.28] | **0.160** | **0.168 (0.24)** |
| committed `milky_way-stars` | −0.354 (+0.236 / −0.118) [−0.304] | 0.051 | 0.042 [0.092] | 0.042 | 1.90 [1.97] | 0.0056 [0.134] | −3.62 | 0.048 | 0.143 (0.84) |
| new stars, defaults | −0.358 (+0.241 / −0.117) [−0.328] | 0.061 | 0.054 [0.090] | 0.049 | 1.96 [1.94] | 0.0062 [0.132] | −3.57 | 0.106 | 0.137 (0.84) |
| old model, box M4 | −0.659 (−0.109 / −0.768) | 0.051 | 0.062 | 0.063 | 1.56 | 0.0460 | −0.79 | 0.093 | 0.110 (0.19) |
| **new model, box M4** | −0.660 (−0.108 / −0.768) | 0.050 | **0.091** | 0.070 | **2.01** [1.98] | 0.0471 | −0.79 | **0.253** | **0.269 (0.19)** |

In the runner's words: the pinned bar is the one visible change. At the defaults the committed frame's faint, round
inner lens becomes a short tilted bar of tan light through the white core ball; the A₂ profile's peak moves from the
outer arms (0.130 at r/a 0.89) to the bar (0.168 at r/a 0.24). Colour, levels, dark fraction and slope do not move
beyond noise. Under M4 the bar is plain and long; in the stars frame it is barely seen under the points.

**NGC 4414** (frame geometry: centre 519.388, 499.717, q 0.5736, PA 175.22, a 286.5 px; the inner disc r/a < 0.25):

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm B | dark | slope | inner disc: level, B−R |
|---|---|---|---|---|---|---|---|---|
| GOAL (section 1) | −0.329 (+0.51 / +0.18) | 0.101 | 0.074 | 0.056 | 2.67 | 0.154 | −2.10 | — |
| committed `ngc_4414-field` | +0.185 (+0.311 / +0.496) | 0.091 | 0.185 | 0.042 | 2.57 | 0.0309 | −2.12 | 207.6, +0.157 |
| **new field, defaults** | +0.166 (+0.299 / +0.464) [+0.175] | **0.059** [0.032] | **0.128** [0.129] | 0.038 [0.021] | **1.99** [2.01] | 0.0278 [0.0289] | **−1.59** [−1.62] | **220.7, +0.144** |
| committed `ngc_4414-stars` | −0.256 (+0.127 / −0.129) [−0.272] | 0.052 | 0.084 [0.089] | 0.037 | 1.57 [2.01] | 0.0000 [0.017] | −3.63 | 219.7, +0.085 |
| new stars, defaults | −0.208 (+0.131 / −0.077) [−0.305] | 0.034 | 0.074 [0.078] | 0.034 | 1.71 [1.81] | 0.0010 [0.041] | −3.58 | 229.6, +0.081 |
| old model, box N6 | −0.347 (−0.066 / −0.414) [−0.533] | 0.152 | 0.099 | 0.033 | 2.02 | 0.0578 | −1.19 | 196.3, −0.057 |
| **new model, box N6** | **−0.459** (−0.022 / −0.481) [−0.804] | **0.063** | **0.034** [0.052] | 0.035 | **1.45** [1.62] | 0.0623 [0.0363] | −1.19 [−0.62] | **205.9, −0.028** |

The inner B−R is −2.5 log₁₀(ΣB / ΣR) on sRGB-decoded pixels — not the tool's band colour, computed the same way on old
and new. In the runner's words: the visible change is the shape. The old thick layer drew a tall, vertical,
bulge-like glow above the disc, with dust shown only on the near side; the new frame is a flat, inclined ellipse, the
disc's arms and dark dust flecks on both sides of the core, and under N6 the sky glow and the speckle form a flat
ellipse instead of a near circle. At the defaults the white core ball and its halo are unchanged in kind. **The inner
disc did not go dark or red behind its dust column: it brightened** (207.6 → 220.7 of 255 at the defaults, 196.3 →
205.9 under N6) and its colour moved by 0.013-0.03 mag; the outer disc dims a little (r/a 1.0: 46 → 43, 64 → 57). The
runner's reason — the thinner layer puts more of the inner light into the midplane and less into the wide vertical
glow — is `[inferred, not traced]`. The stars frames and the default fields also differ in the random draw of knots
and points (the model's inputs changed); single-point changes there are not attributed.

**The yardstick (D269), the lead's verdicts.** `milky_way-field`: the bar shows, short and tilted — the ring's A₂ at
0.21 a 0.060 → 0.160 (0.093 → 0.253 under M4), the headline A₂ 0.053 → 0.078 against the goal's 0.194, the arm
contrast 1.60 → 2.08 (past the goal's 1.83); colour and dark fraction unmoved. **Nearer.** `ngc_4414-field`: a flat
inclined disc with arms and dust flecks where a tall glow stood — A₂ 0.185 → 0.128 (goal 0.074), but A₁ 0.091 →
0.059 (0.101), the arm contrast 2.57 → 1.99 (2.67) and the slope −2.12 → −1.59 (−2.10) move away; the colour step is
still reversed at the defaults (+0.185 → +0.166 against −0.329; under N6 −0.347 → −0.459). **Nearer by eye, mixed by
the numbers.** **Neither is near**: no lanes (ruling 9's: the gas law's frame is not touched, and no sourced weight
gathers the clouds onto a ridge — #229, #144, #228), no pink regions (#232: the regions' sizes are set in their clouds'
clumped gas), and at the owner's display defaults the white ball and the tan still stand (the display pass, the
owner's). Not captured: the thumbnails, the physics-only frame, the zoom frames; no goal picture re-measured (the goal
rows are section 1's).

---

# Part S100 — batch P's committed frames (D270)

## 19. The frames regenerated at the batch's close

**What this is (2026-11-12, S100, BUILD_VI row 100).** The close builder (`s100_C.md`) regenerated the nine frames on
batch P's final model (hash 27561e8d381b992b4ead3bccc0615aa7) from its exported bundles, at the **committed display
defaults** the owner has not yet tuned (no display default touched; `frontend/src` as on `main`): the seven captures,
both thumbnails and `frames.json`. `DUSTY_LAYER_RATIO` was re-pinned as measured (0.96977 / 0.97354 / 0.97990, was
0.96835 / 0.97233 / 0.97909); every judged check of the picture test — the dust's column, the surface-brightness gates
A and B, the GPU light check — passed unmoved, and the picture test reads all nine "the committed picture, byte for
byte" (again after the re-pin pass's two model mends, on the final bundles). "Before" is `main`'s committed frame
(S93's model with S97's display defaults). The statistics are `tools/goal_metrics.py`'s at the **old** field frame's
geometry, the tool's own estimate in [brackets] where it differs; the stars frames at their field frame's geometry.
**Rule C6: no number here is a target.**

| picture | D(B−R) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope |
|---|---|---|---|---|---|---|---|
| GOAL `milky_way` (section 1) | −0.354 | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 |
| before, `milky_way-field` | −0.322 | 0.0564 | 0.0531 | 0.0528 | 1.604 | 0.0315 | −1.26 |
| **S100, `milky_way-field`** | −0.304 [−0.301] | 0.0546 | **0.0778** [0.0783] | 0.0600 | **2.091** [2.083] | 0.0320 [0.0324] | −1.27 [−1.28] |
| before, `milky_way-stars` | −0.354 | 0.0512 | 0.0416 | 0.0424 | 1.901 | 0.0056 | −3.62 |
| S100, `milky_way-stars` | −0.358 | 0.0605 | 0.0543 | 0.0490 | 1.965 | 0.0063 | −3.57 |
| GOAL `ngc_4414` (q 0.5736) | −0.329 | 0.101 | 0.074 | 0.056 | 2.67 | 0.154 | −2.10 |
| before, `ngc_4414-field` | +0.185 | 0.0911 | 0.1848 | 0.0423 | 2.568 | 0.0309 | −2.12 |
| **S100, `ngc_4414-field`** | +0.166 [+0.175] | **0.0593** [0.0320] | **0.1281** [0.1291] | 0.0379 [0.0214] | **1.992** [2.015] | 0.0277 [0.0288] | **−1.59** [−1.62] |
| before, `ngc_4414-stars` | −0.256 | 0.0521 | 0.0837 | 0.0372 | 1.573 | 0.0000 | −3.63 |
| S100, `ngc_4414-stars` | −0.208 | 0.0341 | 0.0736 | 0.0341 | 1.707 | 0.0009 | −3.58 |

At the frame's geometry: the Milky Way field's ring A₂ at r/a 0.21 0.060 → 0.160, its A₂ profile's peak 0.130 at r/a
~0.89 (the outer arms) → 0.168 at r/a ~0.24 (the bar); NGC 4414's inner disc (r/a < 0.25) level 207.6 → 220.7, B−R
+0.157 → +0.144.

**In the close builder's words.** *`milky_way`*: one visible change, and it is the bar — the committed frame's round
inner lens becomes a short tilted tan bar through the white core ball, the two main arms leaving from its ends. Nearer
the goal: A₂ 0.053 → 0.078 (still 40 % of the goal's 0.194), A₃ and A₁ a hair. No nearer: the dark fraction (five
times the goal's), the slope, the levels and the disc's colour (the same tan-grey, no blue outer disc, no pink HII
knots). Worse: the colour step −0.322 → −0.304 (goal −0.354), and the arm contrast 1.60 → 2.09 overshoots the goal's
1.83 by more than it fell short before. *`ngc_4414`*: the visible change is the shape — the tall round glow round the
bulge (the thick 926 pc layer) is gone, and the disc is a flat inclined ellipse with dark flecks on both sides of the
core and a faint flat elliptical sky halo, by eye nearer HST's tilted disc. The metrics are mixed: A₂ 0.185 → 0.128
(goal 0.074, nearer), D(B−R) +0.185 → +0.166 (a hair nearer, still the wrong sign); further: A₁ 0.091 → 0.059 (0.101),
the arm contrast 2.57 → 1.99 (2.67), the slope −2.12 → −1.59 (−2.10), the dark fraction 0.031 → 0.028 (0.154). The
centre is brighter and the white core ball larger; none of the goal's brown lane network, flocculent fragments or
blue-white outer disc. *The stars frames*: blobs under the cell grid, as before; no spiral in either; the Milky Way's
bar barely shows (ring A₂ 0.048 → 0.106).

**The yardstick (D270), the lead's verdicts.** **The Milky Way frame is nearer in one thing**: a short, tilted, tan
bar now crosses the white core and the arms leave from its ends; the goal's bar is three times as strong, long and
yellow in a blue disc with pink knots, and the frame is a tan disc with none of them. **The NGC 4414 frame is nearer in
silhouette**: the tall round glow is gone and a flat inclined ellipse with dark flecks stands in its place; three of
its six statistics moved away from the goal, the colour step is still the wrong sign, and there is none of the Hubble
picture's brown lane network or blue outer disc. **Neither is near.** What stands between: no lanes (D268 ruling 9;
#144), no large pink regions (#232), and the white ball and the tan, which are the display pass's — the owner's.

**Against S99's mid-batch look (section 18).** The field frames' numbers match section 18's to the third figure — on
NGC 4414 every column; on the Milky Way all but the arm contrast (2.08 there, 2.091 here) and the dark fraction
(0.0317, 0.0320) — so batch P's later builds change neither frame visibly: #80's law moves the default galaxy only
(the templates' bars are pinned), and #130's blend moves the dust's crest by a few per cent. The frames' bytes differ.

---

# Part S101 — the yardstick read again on batch P's model (D271)

## 20. The boxes of section 11, re-measured

**What this is (2026-11-17, S101, BUILD_VI row 101).** S101's runner V (an Opus agent; its note `s101_V.md` in the
session's scratchpad) re-took the boxes of section 11 on batch P's model (hash 27561e8d381b992b4ead3bccc0615aa7, the
exported bundles), at the committed display defaults plus each box's tuning; nothing tuned, committed or changed. The
harness's capture at the committed defaults is the committed frame byte for byte (sha256 `e7843e66...` on
`milky_way-field`, `621f2ce7...` on `ngc_4414-field`); M8 and N6 were also pasted through the panel's "A combination to
load" box and gave the stored route's bytes. The statistics are `tools/goal_metrics.py`'s at the committed field
frame's geometry (section 18); the goal rows are section 1's, quoted, not re-measured. **Rule C6: no number here is a
target.** The sheets and tiles are local, in `docs/goals/display_pass_s101/` (never committed), one copy box per tile.

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope | ring A₂ at r/a 0.21 |
|---|---|---|---|---|---|---|---|---|
| GOAL `milky_way` (section 1) | −0.354 (−0.46 / −0.81) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 | — |
| the committed frame | −0.304 (+0.630 / +0.326) | 0.0546 | 0.0778 | 0.0600 | 2.091 | 0.0319 | −1.27 | 0.160 |
| M1 | −0.445 (+0.676 / +0.231) | 0.0534 | 0.1036 | 0.0768 | 2.264 | 0.0522 | −0.71 | 0.300 |
| M3 | −0.663 (−0.115 / −0.779) | 0.0504 | 0.0946 | 0.0723 | 2.043 | 0.0511 | −0.77 | 0.275 |
| M4 | −0.660 (−0.108 / −0.768) | 0.0499 | 0.0908 | 0.0700 | 2.009 | 0.0478 | −0.79 | 0.253 |
| M5 | −0.783 (−0.332 / −1.115) | 0.0463 | 0.0830 | 0.0661 | 1.798 | 0.0449 | −0.82 | 0.236 |
| M8 | −0.694 (−0.132 / −0.826) | 0.0541 | 0.1057 | 0.0777 | 2.159 | 0.0541 | −0.86 | 0.308 |
| M9 | −0.415 (−0.074 / −0.489) | 0.0339 | 0.0674 | 0.0487 | 1.635 | 0.0151 | −0.89 | 0.213 |
| GOAL `ngc_4414` (section 1) | −0.329 (+0.51 / +0.18) | 0.101 | 0.074 | 0.056 | 2.67 | 0.154 | −2.10 | — |
| the committed frame | +0.166 (+0.299 / +0.464) | 0.0593 | 0.1281 | 0.0379 | 1.992 | 0.0278 | −1.59 | 0.077 |
| N1 | −0.400 (+0.188 / −0.212) | 0.0747 | 0.0409 | 0.0440 | 1.644 | 0.0769 | −1.07 | 0.023 |
| N2 | −0.500 (−0.027 / −0.527) | 0.0712 | 0.0386 | 0.0415 | 1.566 | 0.0735 | −1.11 | 0.020 |
| N6 | −0.459 (−0.022 / −0.481) | 0.0631 | 0.0335 | 0.0352 | 1.456 | 0.0619 | −1.19 | 0.015 |
| N7 | −0.326 (−0.023 / −0.349) | 0.0455 | 0.0261 | 0.0277 | 1.349 | 0.0267 | −1.33 | 0.016 |

The committed frames' rows equal section 19's (dark 0.0319 here, 0.0320 there: one byte stream, a rounding).

**What a viewer sees, in the runner's words.** The Milky Way's defaults: a tan disc, a white core ball, a short tilted
bar, a dozen haloed dots on a black sky. M1: still tan; the ball shrinks to a small core, the bar plain, the dots almost
all gone. M3: a blue-white barred spiral, the bar plain, a faint blue sky disc behind it. M4: M3 with a soft core glow
and two or three faint dots. M5: bluer than the goal outside; the sky's circle plain at the corners (#226). M8: M4 half
a stop darker, no dots. M9: flatter and greyer, the outer arms brighter, no white core, the sky circle plainest.
NGC 4414's defaults: a white bloom ball over a faint tan flat ellipse, ten haloed dots. N1: a grey-blue flat inclined
disc with dark flecks, a small nucleus, the sky glow ending at an ellipse. N2: N1 bluer; N6: N2 half a stop brighter;
N7: flatter, the outer disc brightest, the sky ellipse plainest.

**Against section 11.** The Milky Way's boxes keep their colours and gain the bar: the ring A₂ at r/a 0.21 reads
0.09-0.12 (0.079 under Reinhard) on S93's model and 0.24-0.31 (0.213) on batch P's. NGC 4414's boxes lose their A₂,
0.07-0.13 to 0.03-0.04 (0.026 under Reinhard), now under the goal's 0.074, and keep their dark fraction (0.027-0.077
against the goal's 0.154).

**The gate's verdict (D271).** **No tile on either template shows the goal's lanes or its pink regions: the display
pass can take the white ball and the tan away, and nothing else of what stands between the frames and the goals is the
display's.** The display pass stays the owner's (D227); its tools and sheets are ready.

## 21. The eight gaps of section 3 after batch P

| # | gap (section 3) | where it stands at S101 |
|---|---|---|
| 1 | NGC 4414's colour step of the wrong sign | **the display's** (the owner's pass, tools and sheets ready): the committed frame +0.166; N1-N7 −0.33 to −0.50 against the goal's −0.329 |
| 2 | dark lanes | **the model's**: #234 (the arms' molecular gas at a gain of one; (ii) built held in batch Q, BUILD_VII rows 102-103), #228, #231 on the held head; no box shows a lane (dark 0.015-0.054 / 0.027-0.077 against 0.0066 / 0.154, dashes) |
| 3 | the Milky Way's bar / A₂ | **closed in part by the model** (#80's bar, pinned; the ring A₂ 0.24-0.31 in the boxes), **the display's** half (the bloom); the headline A₂ 0.067-0.106 against 0.194; what is left of the bar's shape is #146's axis ratio, batch R (BUILD_VII rows 106-107) |
| 4 | no pink knots, the large dots | the dots **the display's** (gone in M3-M9); the regions **the model's**: #232 (batch Q lane H) and a region drawn at its published radius with #183 (batch Q lane V); the complexes #181 (permanent) |
| 5 | NGC 4414's A₂ at one phase | **the metric's** (the inclination, E5); the boxes now read 0.03-0.04 under the goal's 0.074 - why not re-read at S101 |
| 6 | the Milky Way's slope | not re-read at S101 (the committed frame −1.27, the boxes −0.71 to −0.89, against −1.99) |
| 7 | the burnt-out core | **the display's** (the bloom: the ball shrinks to a small core or goes in M1-M9 and N1-N7) |
| 8 | "a small tan disc" | **the display's** (the white point: M3-M5 read blue-white) |

Beside the eight: the sky's circle at a cool white point is **the model's** stellar disc edge (#226, section 20's
runner; a declaration in batch Q lane G).

## 22. The two things the model lacks, and where they are read

**The lanes** (`READING_ARM_GAS_CONTRAST.md` Part S101). S101's scout measured the chain from the stars' arm to the gas
the clouds and the dust follow, on the pinned check's instrument: the stars' ratio of means 1.458 / 1.405 (Milky Way /
NGC 4414), the gas's 1.431 / 1.429 - the steady co-rotating response linear to four digits, its net gain 1.035, the
thickness factor (0.66, sourced) the largest single loss. Querejeta et al. 2024 measure the molecular contrast
amplifying the stellar one, log10 C_mol = 1.83 log10 C_star + 0.16 per spiral segment, which reads 2.89 / 2.69 at the
model's stellar contrasts. The gap is the gain, not the stars. A ridge set by that relation is still about 1 kpc wide;
a lane is the clouds'. The owner's ruling is #234, with (ii) - the measured relation inside D216's frame - recommended
and built on a held head beside batch Q, frames for both.

**The regions** (lane H's `READING_HII_SIZES.md`, batch Q; register #232). A region is a Strömgren sphere in its
cloud's clumped gas, so none is large. S101's reader read the law that takes a region past its clump: the D-type
expansion to the cluster's age (Bisbas et al. 2015, eq. 13) stopped at the stagnation radius (eq. 17) with the cloud's
turbulent sound speed (Tremblin et al. 2014, eq. 8). Barnes et al. 2025's HST sizes (10 pc) put the model's median right
and its bright end about 2 times too small. Under the law the Milky Way's census reads 17.1 / 42.3 / 71.4 pc (median /
p99 / max) and 4 752 regions over half a pixel against 7 - numbers printed before the build, so every check after it is
disclosed. The goal pictures' largest pink regions are complexes and envelopes, #181's (permanent).

---

# Part S102 — batch Q's frames and the held heads beside them (D272)

## 23. `batch-q`'s frames against `main`'s

**What this is (2026-11-17, S102, BUILD_VII rows 102-103).** The close's runner X (an Opus agent; its note `s102_X.md`
in the session's scratchpad) captured, with S101's harness, the field frames at the committed display defaults and at
the owner's boxes M4 and N6, plus the two 2.2 kpc zoom stands lane V used (4.4 kpc across, about 4.3 pc per pixel),
for three models served live from their worktrees without bundles - `batch-q` (e455a20, model hash 6becb77e...),
`batch-q-lanes` (6b8fe33, 6e06b54c...) and `q-231` (0e8f096, fa647806...) - through one viewer build (the frontend is
the same in all three; lane V's drawing is in it). `main` is the committed frames and S101's tiles (section 20), and,
on the gate's order (V4), `main` (b5d421c, model hash 27561e8d..., main's own frontend build) captured at the three
zoom stands. Nothing tuned, committed or changed; no display default touched. The statistics are
`tools/goal_metrics.py`'s at S101's committed field geometry (the Milky Way centre 519.805, 515.349, q 1, PA 25.52, a
300.3; NGC 4414 centre 519.388, 499.717, q 0.5736, PA 175.22, a 286.5); the zoom stands have no goal geometry and no
row. The goal rows are section 1's, quoted. **Rule C6: no number here is a target.** The sheets, crops and ratio maps
are local, in `docs/goals/batch_q_s102/` (never committed): `s102_X_sheet_milky_way.png`, `s102_X_sheet_ngc_4414.png`
(rows the defaults, M4 or N6, the zoom; columns the goal, `main`, `batch-q`, `batch-q-lanes`, `q-231`),
`s102_X_crops_milky_way.png`, `s102_X_crops_ngc_4414.png` (2x crops of one arm box on every model),
`s102_X_pair_M4.png`, `s102_X_pair_N6.png`, `s102_X_pair_M4z.png`, `s102_X_pair_N6z.png`, `s102_X_pair_N6z_left.png`,
`s102_X_main_MWz.png`, `s102_X_main_M4z.png`, `s102_X_main_N6z.png`, `s102_X_main_N6z_left.png`, the log2 luminance
ratio maps `s102_X_ratio_<box>.png` (`batch-q-lanes` over `batch-q`), and the table `s102_X_metrics.md`.

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope |
|---|---|---|---|---|---|---|---|
| GOAL `milky_way` (section 1) | −0.354 (−0.46 / −0.81) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 |
| `main`, the committed frame | −0.304 (+0.630 / +0.326) | 0.0546 | 0.0778 | 0.0600 | 2.091 | 0.0319 | −1.27 |
| **`batch-q`, defaults (live)** | −0.313 (+0.630 / +0.316) | 0.0535 | 0.0764 | 0.0598 | 2.113 | 0.0325 | −1.15 |
| `main`, M4 (section 20) | −0.660 (−0.108 / −0.768) | 0.0499 | 0.0908 | 0.0700 | 2.009 | 0.0478 | −0.79 |
| **`batch-q`, M4** | −0.657 (−0.108 / −0.765) | 0.0502 | 0.0914 | 0.0706 | 2.014 | 0.0480 | −0.81 |
| GOAL `ngc_4414` (section 1) | −0.329 (+0.51 / +0.18) | 0.101 | 0.074 | 0.056 | 2.67 | 0.154 | −2.10 |
| `main`, the committed frame | +0.166 (+0.299 / +0.464) | 0.0593 | 0.1281 | 0.0379 | 1.992 | 0.0278 | −1.59 |
| **`batch-q`, defaults (live)** | +0.165 (+0.299 / +0.464) | 0.0599 | 0.1268 | 0.0390 | 1.984 | 0.0276 | −1.52 |
| `main`, N6 (section 20) | −0.459 (−0.022 / −0.481) | 0.0631 | 0.0335 | 0.0352 | 1.456 | 0.0619 | −1.19 |
| **`batch-q`, N6** | −0.458 (−0.022 / −0.480) | 0.0630 | 0.0335 | 0.0352 | 1.456 | 0.0617 | −1.14 |

**The committed frames after D1.** `batch-q`'s nine frames regenerated from its bundles
(`C:\Users\Semaphore\AppData\Local\Temp\galaxygen-s102\bundles_q`, model 5a862a70...) at the committed display
defaults (D1's commit 0d0b28d; the picture test's real run then 1 passed twice, all nine the committed picture byte for
byte). **The regenerated field frames equal runner X's live `batch-q` captures byte for byte** (sha256 9de9b23b... the
Milky Way, bca52b22... NGC 4414), so their rows are the live rows above. `goal_metrics` at section 19's geometry:

| picture | D(B−R) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope |
|---|---|---|---|---|---|---|---|
| `main` `milky_way`-field | −0.304 | 0.0546 | 0.0778 | 0.0600 | 2.091 | 0.0319 | −1.27 |
| **S102 `milky_way`-field** | −0.313 | 0.0535 | 0.0764 | 0.0598 | 2.113 | 0.0325 | −1.15 |
| `main` `milky_way`-stars | −0.358 | 0.0605 | 0.0543 | 0.0490 | 1.964 | 0.0062 | −3.57 |
| **S102 `milky_way`-stars** | −0.362 | 0.0583 | 0.0565 | 0.0477 | 1.864 | 0.0072 | −3.50 |
| `main` `ngc_4414`-field | +0.166 | 0.0593 | 0.1281 | 0.0379 | 1.992 | 0.0278 | −1.59 |
| **S102 `ngc_4414`-field** | +0.165 | 0.0599 | 0.1268 | 0.0390 | 1.984 | 0.0276 | −1.52 |
| `main` `ngc_4414`-stars | −0.208 | 0.0341 | 0.0736 | 0.0341 | 1.707 | 0.0010 | −3.58 |
| **S102 `ngc_4414`-stars** | −0.208 | 0.0341 | 0.0736 | 0.0341 | 1.707 | 0.0010 | −3.58 |

The Milky Way's stars frame moves in the second or third figure (lane G's taper at chain 0's turn back moves the Milky Way's stars and no other galaxy's `[inferred]`);
NGC 4414's not at all. `DUSTY_LAYER_RATIO` re-pinned as measured, [0.96977, 0.97354, 0.97990] -> [0.96993, 0.97367,
0.97993]; every judged check of the picture test passed unmoved (the dust's column 0.999786; the surface-brightness
gates A and B; the GPU light at most 5.73e-6).

`batch-q`'s rows equal lane V's "after" rows (q-viewer on q-nebular) to the third figure; `main`'s equal S101's. The
numbers move in the third figure but for the power slope (the Milky Way's defaults −1.27 → −1.15, NGC 4414's −1.59 →
−1.52), which is lane V's knots spreading their light over the sphere of `hii_radius` (section 25).

## 24. The held head and `q-231` against `batch-q`

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope |
|---|---|---|---|---|---|---|---|
| `batch-q`, `milky_way` defaults | −0.313 (+0.630 / +0.316) | 0.0535 | 0.0764 | 0.0598 | 2.113 | 0.0325 | −1.15 |
| `batch-q-lanes`, `milky_way` defaults | −0.318 (+0.629 / +0.311) | 0.0528 | 0.0793 | 0.0662 | 2.079 | 0.0309 | −1.21 |
| `q-231`, `milky_way` defaults | −0.312 (+0.629 / +0.318) | 0.0574 | 0.0795 | 0.0674 | 2.106 | 0.0307 | −1.18 |
| `batch-q`, M4 | −0.657 (−0.108 / −0.765) | 0.0502 | 0.0914 | 0.0706 | 2.014 | 0.0480 | −0.81 |
| `batch-q-lanes`, M4 | −0.653 (−0.108 / −0.762) | 0.0539 | 0.0924 | 0.0727 | 2.005 | 0.0455 | −0.87 |
| `q-231`, M4 | −0.654 (−0.108 / −0.763) | 0.0548 | 0.0920 | 0.0732 | 2.008 | 0.0455 | −0.83 |
| `batch-q`, `ngc_4414` defaults | +0.165 (+0.299 / +0.464) | 0.0599 | 0.1268 | 0.0390 | 1.984 | 0.0276 | −1.52 |
| `batch-q-lanes`, `ngc_4414` defaults | +0.166 (+0.332 / +0.499) | 0.0684 | 0.1234 | 0.0313 | 1.947 | 0.0264 | −1.52 |
| `q-231`, `ngc_4414` defaults | +0.255 (+0.339 / +0.594) | 0.0865 | 0.1379 | 0.0369 | 2.095 | 0.0214 | −1.53 |
| `batch-q`, N6 | −0.458 (−0.022 / −0.480) | 0.0630 | 0.0335 | 0.0352 | 1.456 | 0.0617 | −1.14 |
| `batch-q-lanes`, N6 | −0.457 (−0.022 / −0.479) | 0.0610 | 0.0322 | 0.0275 | 1.367 | 0.0565 | −1.14 |
| `q-231`, N6 | −0.452 (−0.028 / −0.481) | 0.0603 | 0.0339 | 0.0287 | 1.374 | 0.0577 | −1.17 |

The ratio maps (`batch-q-lanes` over `batch-q`): the median log2 ratio over lit pixels 0.000 on every box but
NGC 4414's defaults (−0.037); pixels under 0.8x 1.0-2.0 % in the field frames and about 4.7 % at the zoom stands,
balanced by as many over 1.25x; the map a scatter of black and white ellipses - the dust clouds moved, and a few
knots - with no smooth band along any arm. The held head's frames are live captures only; its committed frames are
not regenerated at this close: the held head keeps `batch-q`'s committed frames, and its own close is to regenerate its
nine on a branch cut from it (`batch-q-lanes-frames`), recorded there.

## 25. What the sheets show, and the gate's verdict

**In the runner's words** (X, having looked at the sheets, crops and ratio maps). *`batch-q` against `main`*: the
field frames cannot be told apart by eye, at the defaults and in M4 / N6. At the 2.2 kpc stands `main`'s point-like
knots become small reddish discs, few and isolated (lane V's sphere). *`batch-q-lanes`*: no dark lanes, in any frame,
neither continuous nor dashed, neither on the arms' inner edge nor elsewhere; the ruleset shows only as the dust
clouds' ellipses re-placed; in the 2x crops as many dark flecks as `batch-q` on the Milky Way, slightly fewer on
NGC 4414; nothing black between the arms, no star formation switched off between arms, no new speckle. *`q-231`*: no
lanes; its frames are the lanes head's (a few dark ellipses a little larger on the Milky Way); NGC 4414's outer disc
redder at the defaults; at the N6 zoom fewer dark clouds and, on the nucleus side, hard-edged near-white saturated
patches where `batch-q` and the lanes head show a faint blue-white young patch - new with `q-231`, not traced.
*Against the goals*: unchanged from S101. *At the N6 zoom on every model, `main` included*: the dust clouds draw as
blocky, stair-stepped patches and the nucleus side carries pixel-level white / blue speckle - the same patches in the
same places on `main` (`s102_X_main_N6z_left.png`): older than batch Q (#236).

**The gate's verdict (D272), as the gate wrote it.**

*V1. Against the two goal pictures: batch Q moved nothing a viewer sees.* `batch-q` beside `main`: the field frames
cannot be told apart by eye, at the defaults and in the owner's boxes M4 and N6. The regions drawn at their grown size
are a few faint pinkish discs at the 2.2 kpc stand and nothing at the field scale. The distance to the goals is
S101's, unchanged: `milky_way` at the defaults a tan disc with a white ball; M4 a blue-white barred spiral without the
goal's strings of pink knots and without dark lanes; `ngc_4414` at the defaults a white ball over a faint tan ellipse;
N6 a grey-blue inclined disc with dark flecks, no brown lane network, no yellow core. `batch-q-lanes` (the owner's
#234, ruleset (ii)): **no dark lanes, in any frame, continuous or dashed.** The measured relation moves the clouds'
ellipses and nothing else (median brightness ratio against `batch-q` 1.000; about 2 % of lit pixels darker than 0.8x
and as many brighter than 1.25x). On N6 the two picture measures move AWAY from the goal's (dark 0.0617 → 0.0565
against 0.154; arm 1.46 → 1.37). `q-231` (#231): no lanes; its frames are the lanes head's; `ngc_4414`'s outer disc
redder at the defaults (D(B−R) +0.166 → +0.255 against the goal's −0.329) and one untraced defect.

*V2. What this says about #234 and #229* (the gate's reading, `[inferred]`). The relation (ii) is a measurement at
1.5 kpc of mask width and the model meets it; it gathers the molecular gas into a crest 0.67-0.77 of the stars' width,
still of order a kiloparsec. The goal pictures' lanes are of order a hundred parsecs wide and continuous. So a
kiloparsec-scale contrast, however right, cannot draw them: what is missing is the NARROW ridge (the gas's compression
at the arm's shock, or the clouds strung along one line with a covering fraction near one along it), and neither
ruleset holds it. **The gate's recommendation on #234 stands on the measurement alone ((ii) is what Querejeta et al.
measured; (i) is the model's own solve) and no longer on the picture: the frames give no reason to prefer either. The
gate now recommends the owner NOT take (ii) for the picture's sake, and leave `batch-q-lanes` held until the reading
is in** (#229's S102 line: the lanes' measured width, offset from the stellar crest and covering fraction).

*V3. #231.* D220 item 1 / invariant I2 is broken on the mask's rings by the brief's own design: a declared break on a
frames-only branch, the invariant not amended; "arm" as a molecular-mass share per cell and factor 1 the same
distribution (not the same bits) accepted as declared. **The gate's recommendation to the owner: do not order it** -
the frames gain nothing, an invariant breaks, `ngc_4414` reddens away from the goal, the largest cloud sits at the
150 pc cap at 219 M☉/pc², and there is a defect. `q-231` is pushed as a branch, never merged, no CI.

*V4. The N6 2.2 kpc stand.* (a) the dust drawn as blocky, stair-stepped patches and (b) the pixel-level speckle on the
nucleus side were told apart from batch Q before the close: `main` captured at the three zoom stands shows both -
older, **#236** opened (carried, the viewer row, BUILD_VII row 104; what kills it: the cause named). `q-231`'s white
patches are recorded in #231 as untraced, not chased.

**Where the eight gaps of section 21 stand after batch Q:** unmoved. Gap 4's regions are grown (#232 discharged) and
drawn at their size, and still not the goal's pink regions (#181's complexes, #235's flat relation, the display's
`knotsIntensity`); gap 2's lanes are not drawn by either ruleset of #234 (#229's reading row). C6 said again: nothing
here was tuned to a goal picture.

---

# Part S105 — the illustrative look beside the goals (D275, D276)

## 26. What changed in what this file is for

Until S104 this file measured how far the frames were from the goal pictures without ever aiming at them (C6). On the
owner's word of 2026-11-23 (D275) the goals are the target of the viewer's **illustrative look** (BUILD_VIII); the
**physical look** is the viewer of sections 1 to 25, unchanged byte for byte, and everything above still describes it.
This part reads the illustrative frames of S105's close (model hash 5a862a70..., `main`'s; no model byte moved).

## 27. The yardstick on the illustrative frames

`tools/goal_metrics.py` on S105's two illustrative captures (1024 px, the look's default stands) and, for like with
like, on the two goal pictures **at the tool's own estimate of each picture's geometry** (the Milky Way pair with
`--axis-ratio 1`). The physical rows are section 23's committed frames at the committed field geometry, quoted. The
goal's Milky Way row reproduces section 1's; NGC 4414's goal differs a little from section 1's row because the
geometry here is the tool's estimate (q 0.512, not 0.5736). A number here is a target only for the illustrative look.

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope |
|---|---|---|---|---|---|---|---|
| GOAL `milky_way` | −0.354 (−0.459 / −0.813) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 |
| physical (section 23) | −0.313 (+0.630 / +0.316) | 0.054 | 0.076 | 0.060 | 2.11 | 0.0325 | −1.15 |
| **illustrative, S105** | −0.477 (−0.504 / −0.981) | 0.087 | 0.143 | 0.091 | 2.11 | 0.0423 | −1.58 |
| GOAL `ngc_4414` (the tool's geometry) | −0.274 (+0.508 / +0.234) | 0.099 | 0.068 | 0.055 | 2.72 | 0.157 | −2.09 |
| physical (section 23) | +0.165 (+0.299 / +0.464) | 0.060 | 0.127 | 0.039 | 1.98 | 0.0276 | −1.52 |
| **illustrative, S105** | −0.496 (+0.751 / +0.255) | 0.063 | 0.045 | 0.051 | 2.10 | 0.190 | −1.89 |

Nearer on both: the colours' levels and the sign of the step (the Milky Way's bands are now blue as the goal's are;
NGC 4414 is redder inside than outside, as the photograph is), the power slope, and NGC 4414's dark fraction (0.028 to
0.190 against 0.157). The Milky Way's A₂ doubled (0.076 to 0.143 against 0.194). Not nearer: the Milky Way's dark
fraction (0.042 against 0.0066: our lanes are darker and crisper than the goal's translucent ones), its A₁ and A₃
(up, past the goal's), the arm to inter-arm ratio on both.

## 28. What a viewer sees, in the lead's words (the lead looked at every sheet)

**The Milky Way.** Physical: a small tan disc under a white ball with haloed dots. Illustrative: a blue barred spiral
on black - a cream bar ellipse with two thin lanes curling into the nucleus, pale blue arm bands springing from the
bar's ends, thin broken red-brown lanes along every arm, small pink regions strung on the arms as accents, a soft
fade at the edge. It is the goal's kind of picture. Still far: the disc fills about 70 % of the frame where the goal's
fills 90 %; our arms are fewer and broader (they are the model's arms, where the model puts them); the goal's arms
carry a fine pale grain ours lack; the inter-arm disc shows a streaky brushed texture; the pink regions read a little
like confetti on the lower right arm; a dark slate ring round the bar is a little strong.

**NGC 4414.** Physical: a white ball over a faint tan ellipse. Illustrative: an inclined warm disc lying as the
photograph's does - a small pale nucleus, cream and tan inside, a brown dust network in short spiral pieces over the
inner two thirds, a grey-white outer disc with white flecks, a soft edge. It is the photograph's kind of picture.
Still far: the network is coarser and more brushed where the photograph's is fine and feathered; the white clumps read
as dashes, and the photograph's outer left is full of white-blue star clouds ours lacks; the disc is rounder than the
photograph's (the template's inclination); the nucleus is a little cold.

**The streaky texture** under both is the model's own light in the march (the synthetic layer's maps); it stays with
every illustrative feature switched off (tuner N's test) and is BUILD_VIII section 6's second item.

The frames: `docs/pictures/s105/` (committed). The sheets beside the goals, the tuners' rounds and the reviewer's
captures are local, under `docs/goals/` in the session's worktrees (never committed: the goal pictures are not ours).

---

# Part S106 — the close-range pass: one arm skeleton, NGC 4414's threads and mesh (D277)

## 29. What S106 changed in the frames

BUILD_VIII rows 111 to 114 (D277), viewer-only (model hash 5a862a70..., no model byte moved; the physical look byte for
byte). The streaky texture under both discs (section 28's last paragraph) was traced by capture to the gas fluctuation
map's log-spiral shear multiplying the dust's placement, and is smoothed under the illustrative look (`base.ts`). The
Milky Way is drawn on one arm skeleton that its glow, grain, lanes and pink regions all read; NGC 4414's dust is drawn
in the disc's plane as thin threads and a branching mesh, with star clouds, a sky of field stars and a 6-degree tilt;
its blue nucleus was traced to a float32 underflow in the physical path (#238) and mended in the layer only.

## 30. The yardstick on S106's frames

`tools/goal_metrics.py` on the two committed frames of the close (`docs/pictures/s106/`, 1024 px, the merged head's
capture at the look's default stands), measured as section 27 measured: the Milky Way's pictures with
`--axis-ratio 1`, NGC 4414's at the tool's own estimate of each picture's geometry. The goal and S105 rows are
re-measured the same way and reproduce section 27's.

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope | q |
|---|---|---|---|---|---|---|---|---|
| GOAL `milky_way` | −0.354 (−0.459 / −0.813) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 | 1 (set) |
| illustrative, S105 | −0.477 (−0.504 / −0.981) | 0.087 | 0.143 | 0.091 | 2.11 | 0.0423 | −1.58 | 1 (set) |
| **illustrative, S106** | −0.259 (−0.429 / −0.688) | 0.076 | 0.125 | 0.133 | 2.14 | 0.0081 | −2.38 | 1 (set) |
| GOAL `ngc_4414` (the tool's geometry) | −0.274 (+0.508 / +0.234) | 0.099 | 0.068 | 0.055 | 2.72 | 0.157 | −2.09 | 0.512 |
| illustrative, S105 | −0.496 (+0.751 / +0.255) | 0.063 | 0.045 | 0.051 | 2.10 | 0.190 | −1.89 | 0.611 |
| **illustrative, S106** | −0.491 (+0.629 / +0.138) | 0.083 | 0.069 | 0.043 | 1.95 | 0.229 | −1.83 | 0.506 |

Nearer: the Milky Way's dark fraction (0.042 to 0.0081 against 0.0066: the lanes now thin threads, not dark bands)
and the size of its colour step (−0.26 against −0.35, from −0.48); NGC 4414's A₂ (0.069 against 0.068), its A₁, its
axis ratio (0.506 against 0.512: the tilt) and its inner colour (+0.63 against +0.51, from +0.75). Not nearer: the
Milky Way's A₂ (0.125, below S105's 0.143; B5's frame read 0.145 before the lead's last framing change) and its A₃
(0.133, the strongest of its first three harmonics where the goal's is m = 2); its arm contrast (2.14 against 1.83); its
slope (now as far past the goal's as S105's was short of it); NGC 4414's dark fraction (0.229 against 0.157: more dust
than the photograph, threads and mesh together; C4's mesh alone read 0.162), its arm contrast (1.95 against 2.72) and
its outer colour (+0.14 against +0.23). The table is the committed frames'; the builders' own readings were taken
before the lead's last framing change and pick, and are not repeated here.

## 31. What a viewer sees, in the lead's words (the lead looked at the final frames beside both goals)

**The Milky Way.** Now the goal's picture in kind and in composition: a luminous lavender disc filling the frame to a
soft fade on black; several continuous pale cyan-white arms of fine grain winding from the bar's ends to the edge; thin
red-brown lanes on the arms' inner edges; small pink-red regions with white cores in uneven bunches on the arms; a
crisp cream-yellow bar at the goal's angle with a fine lane, in a darker slate-lavender zone. Still unlike the goal:
the arms are smooth glowing bands with points on them where the goal's are patchy cyan-teal light; the first arm runs
nearly round the bar instead of leaving its ends clearly; the regions read salmon-pink rather than crimson and none is
a large ragged complex; the lanes are single fine threads without the goal's branching; a stray pale-blue blob sits
right of the bar and one lone region at a faded outer arm end; spurs hardly read as separate branches.

**NGC 4414.** At full frame much like the photograph: an inclined disc at the goal's tilt, a cream nucleus in a golden
inner disc, dark brown dust in many thin flocculent spiral arcs with a tangle between, a blue-grey outer disc with
blue-white star-cloud patches at the rim (richest left and bottom), field stars on a navy-black sky. Still unlike the
goal: close up the threads are more parallel and even than the photograph's tangled lanes of many widths; the light
between the dust is soft heaps rather than crisp grainy star fields; the outer rim's dust reads grey-black rather than
brown; the nucleus is a soft peach-cream blob rather than a sharp near-white point; the star clouds' points scatter a
little past the rim.

**The distance, plainly.** S105 made both frames the right kind of picture; S106 makes both read as their goal at a
glance. What remains is texture and finish at close range, not composition (`BUILD_VIII.md` section 6).

The frames: `docs/pictures/s106/` (committed; sha256 94e84028... and 936c3977..., in D277). The builders' sheets and
captures are local, under `docs/goals/` in the session's worktrees (never committed).

## 32. A second reader (the documents' writer, who built none of it)

The writer of S106's close documents looked at the two committed frames beside the two goal pictures and measured them
(section 30). What the lead's words in section 31 do not say:

- **The Milky Way's outer arms read almost as concentric rings**, more tightly wound than the goal's. The yardstick
  agrees: A₂ 0.125, below S105's 0.143, with A₃ 0.133 above it, where the goal is m = 2 (A₂ 0.194, A₃ 0.059).
- **The bar is a saturated yellow**, brighter than the goal's pale cream, and its lane is one straight line along its
  axis.
- **The pink regions sit at near-regular intervals along the arms**, like beads on a string.
- **NGC 4414's dust reads as short curled brush-strokes**, more uniform across the disc than the photograph's lanes.
  Its dark fraction is 0.229, further from the goal's 0.157 than S105's 0.190 was.
- **A grainy fringe of noise sits outside NGC 4414's rim at the upper left**; it is more visible than "the star
  clouds' points scatter a little past the rim" suggests.

---

# Part S107 — the close-up pass: the sliders freed, an opening Milky Way, NGC 4414's narrow lanes (D278)

## 33. What S107 changed in the frames

BUILD_VIII rows 115 to 118 (D278), viewer-only (model hash 5a862a70..., no model byte moved; the physical look byte for
byte). Two rows change nothing in a frame at rest: the layer's map and the sparkle are built in a worker (the four
illustrative frames byte-identical through the change), and the framing is keyed on the drawn template so a landing
makes one canvas, not two (the six look frames byte-identical). The two picture rows change both frames. The Milky
Way's skeleton opens outward with its lesser arms spaced evenly between the majors, its arm light is patchy, its
regions are bunched into ragged complexes under a veil, its lanes split and rejoin, and its colour was matched to the
goal patch by patch. NGC 4414's dust is a field of many narrow broken lanes drawn by the march's mesh, the map's threads
off; the brushing S106's second reader saw (section 32) was traced to the layer's own threads and grain, not to the
model's star contrast as the lead had guessed; the rim's fringe and a white patch right of the nucleus are gone. After
a first reading of the frames by the documents' writer (section 36), the lead changed two values and re-captured:
the Milky Way's `framing.scale` 0.9 to 0.84 (the disc across about 88 % of the frame again, the corners black) and
NGC 4414's `grade.saturation` 1 to 1.15 (1.25 was tried and measured a colour step further from the goal's). The
frames committed and measured below are the re-captured ones.

## 34. The yardstick on S107's frames

`tools/goal_metrics.py` on the two committed frames of the close (`docs/pictures/s107/`, 1024 px, the merged head's
capture at the look's default stands), measured as sections 27 and 30 measured: the Milky Way's pictures with
`--axis-ratio 1`, NGC 4414's at the tool's own estimate of each picture's geometry. The goal and S106 rows are
re-measured the same way and reproduce section 30's. The last column is the tool's own estimate of the disc's outer
radius, in each picture's own pixels (the goals are larger pictures than the 1024-px frames).

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope | q | a (px) |
|---|---|---|---|---|---|---|---|---|---|
| GOAL `milky_way` | −0.354 (−0.459 / −0.813) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 | 1 (set) | 2006 |
| illustrative, S106 | −0.259 (−0.429 / −0.688) | 0.076 | 0.125 | 0.133 | 2.14 | 0.0081 | −2.38 | 1 (set) | 415 |
| **illustrative, S107** | −0.067 (−0.637 / −0.704) | 0.052 | 0.164 | 0.039 | 2.11 | 0.0060 | −1.75 | 1 (set) | 411 |
| GOAL `ngc_4414` (the tool's geometry) | −0.274 (+0.508 / +0.234) | 0.099 | 0.068 | 0.055 | 2.72 | 0.157 | −2.09 | 0.512 | 664 |
| illustrative, S106 | −0.491 (+0.629 / +0.138) | 0.083 | 0.069 | 0.043 | 1.95 | 0.229 | −1.83 | 0.506 | 427 |
| **illustrative, S107** | −0.425 (+0.722 / +0.297) | 0.079 | 0.042 | 0.037 | 1.64 | 0.185 | −2.25 | 0.504 | 399 |

Nearer: the Milky Way's A₂ (0.125 to 0.164 against 0.194) and A₃ (0.133 to 0.039 against 0.059: m = 2 is again its
strongest harmonic, as the goal's is), its A₁, its dark fraction (0.0060 against 0.0066) and its slope (−1.75 against
−1.99, now a little short of the goal's where S106's was past it); NGC 4414's dark fraction (0.229 to 0.185 against
0.157), its colour step (−0.491 to −0.425 against −0.274) and its outer colour (+0.297 against +0.234, from +0.138).
Further: **the Milky Way's colour step** (−0.067 against −0.354, from −0.259): its inner annulus is now bluer than the
goal's (−0.637 against −0.459) while its outer is redder (−0.704 against −0.813), although MW3's patch-by-patch table
matched the goal's hues; **not understood** (BUILD_VIII section 6 item 2: find what the tool's annuli see). The first
capture of the close, with the disc smaller in the frame, gave the tool a radius of 386 px and the same step, −0.067;
the re-capture brings the radius back to 411 px (S106's 415) and the step is still −0.067, so the smaller disc was not
the reason. NGC 4414's inner colour (+0.722 against +0.508) is further from the goal's than S106's (+0.629): the
higher saturation warms the centre more than the rim (the first capture at saturation 1 read −0.371, +0.631 / +0.260).
NGC 4414's A₂ (0.069 to 0.042 against 0.068) and its arm contrast (1.95 to 1.64 against 2.72) fell: the broad bands
carried them, and the narrow lanes are lighter and less prominent than the photograph's. The Milky Way's arm contrast
did not move (2.11 against 1.83).

## 35. What a viewer sees, in the lead's words (the lead looked at the final frames and close-ups beside both goals)

**The Milky Way.** A balanced spiral: two major arms leaving the bar's ends and opening outward, with fainter lesser
arms between; the arms a patchy pale blue-white grain on a periwinkle disc that is darker between them; ragged red-pink
regions with white cores in bunches and a dozen larger complexes on braided brown lanes; a pale cream bar. The close
view now looks like the goal's close view. Still unlike the goal: an empty lavender zone round the bar where the goal's
inner arms hug the bar's ends; the lesser arms fainter and thinner than the goal's four near-equal arms; the bar-end
white-pink clusters weak; the bar still more saturated and orange than the goal's (hue 36 against 46) with too bright a
glow at its edge; the lanes browner (hue 30 against 11) and broader than the goal's fine reddish threads; the bar's
lanes nearly invisible at full frame; the disc a little washed against the goal's contrast.

**NGC 4414.** At both ranges now much like the photograph: at full frame a flocculent disc of many narrow broken dust
lanes round a small bright nucleus in a golden inner disc, blue-white star clouds at the rim, field stars; close up,
dark filaments with knots and wisps across a crisp grainy star field, no brushing. Still unlike it: the lanes are
lighter and less prominent than the photograph's at full frame; near the nucleus they read a little like parallel
fingerprint stripes; no broad pale tan veils inside the lanes; the near-side rim still shows a faint dark smeared
texture close up; the dark fraction 0.185 against 0.157.

**The distance, plainly.** S106 made both frames their goal's composition; S107 makes both close-ups read as their
goal's close-ups. What remains is strength and balance (the owner's sliders can reach most of it) and a few forms
(`BUILD_VIII.md` section 6).

The frames: `docs/pictures/s107/` (committed; sha256 803204f7... and 9f8b2f3f..., in D278). The close-ups and the
builders' sheets are local, under `docs/goals/` in the session's worktrees (never committed).

## 36. A second reader (the documents' writer, who built none of it)

The writer of S107's close documents looked at the two committed frames and the two close-ups beside the two goal
pictures and beside S106's frames (`docs/pictures/s106/`), and measured them (section 34). Where this agrees with the
lead's words: the Milky Way's arms now leave the bar's ends and open outward instead of closing into rings; its regions
are bunched clumps and ragged complexes, no longer beads on a string; its lanes braid; the bar is warmer and more
orange than the goal's cream; the zone round the bar is an empty lavender; NGC 4414's brushing is gone, its lanes
narrow, broken and lighter than the photograph's, and near the nucleus they run as concentric fingerprint stripes; its
near-side rim close up is a dark smear. What the lead's words do not say, first read on the close's first capture and
read again on the re-captured frames committed here:

- **The Milky Way's disc sat smaller in the frame than S106's** (about 80 % of the frame's width against nearly 90 %;
  the tool's radius 386 px against 415). **Acted on and met:** the lead set `framing.scale` 0.84; in the committed
  frame the disc spans about 88 % of the width again with black corners, and the tool reads 411 px.
- **The Milky Way's close view carries many soft round blue blobs** between the arms, like out-of-focus lights; the
  goal has nothing of the kind, and they read as the frame's most artificial mark at that range. **Traced by the lead
  by capture and not mended:** they vanish with `arms.sparkle` 0 and stay with `arms.sparklebig` 0, `knots.sparkle` 0,
  the regions off, the clustered young light off (`clumpsInMarch` false) and `arms.sparklerange` cut from 60 to 10:
  they are the arm grain's own points, whose sprite is soft and reads as a disc at close range. The close-up beside
  the re-captured frames still shows them unchanged; left for the next session (a sharper sprite, or a size that does
  not grow at close range).
- **The Milky Way's lanes close up zigzag** in sharp short kinks, darker and more opaque than the goal's soft threads.
  Not acted on; unchanged.
- **NGC 4414's disc reads greyer than the photograph**: an even grey-white from the golden centre to the rim, where the
  photograph's outer disc dims and turns blue-grey with darker dust between the clouds, so ours reads paler and
  flatter, with a more abrupt edge. **Acted on in part:** `grade.saturation` 1.15. In the re-captured frame the middle of
  the disc is a warmer tan and the close view's grain carries some cream, so it reads less grey; **not met**: the outer
  disc is still a bright grey-white to an abrupt edge rather than dimming and turning blue, and the extra saturation
  went mostly into the centre (inner B−R +0.631 to +0.722, further from the goal's +0.508; the step −0.371 to −0.425,
  further from −0.274).
- **NGC 4414's close view is a uniform sand-like grain**, with a few pale round blotches in it: the light between the
  lanes is evenly grained, neither the photograph's crisp clumps nor its broad smooth veils. Warmer now, still uniform.
- **Worse than S106**, besides the measures in section 34: NGC 4414's dust no longer carries the strong brown warmth
  across the middle of the disc that S106's (combed) threads gave.

---

# Part S108 — the look away from its two stands: edge-on, orbited, suspended, rerolled (D279)

## 37. What S108 changed in the frames

BUILD_VIII rows 119 to 122 (D279), viewer-only (model hash 5a862a70..., no model byte moved; the physical look byte for
byte, checked by the reviewer against `main`'s own build at many stands, inclinations, orbits and swaps). S108's subject
was not the two tuned frames but everything else a viewer can do: a tour of 222 captures found the look broke edge-on,
under physics only, in star-first mode, through an orbit and on a reroll, and the builders mended those. At the tuned
stands: **NGC 4414's full frame is S107's byte for byte** (sha256 9f8b2f3f..., the same file); its close stand is S107's
picture turned 1.6 degrees (the roll now about the true line of sight; ruling 39). **The Milky Way's two frames moved
twice, by small amounts**: once because its stand now settles and marches at 8 of 8 sub-samples where it had always
been drawn at the "moving" quality of 2 (full frame mean 0.17 of 255, grain only; rulings 31 and 40), and once by the
arm grain's cap before the bloom (`arms.sparklecap` 30: the full frame 337,492 pixels differ, at most by 46; the close
stand 1,006,915, at most 87): the brightest soft blue discs between the arms close up are gone, fainter ones remain.
New: two edge-on captures at 88 degrees, drawn through the handover (the layer's thin-screen marks fading per ray from
72 to 88 degrees off the axis, its ink put into the model's own dust layer). The four frames are committed as plain
pictures in `docs/pictures/s108/` (ruling 37).

## 38. The yardstick on S108's frames

`tools/goal_metrics.py` re-measured by the documents' writer on the two committed full frames of the close
(`docs/pictures/s108/`, 1024 px), measured as section 34 measured: the Milky Way with `--axis-ratio 1`, NGC 4414 at the
tool's own geometry. **The goal and S107 rows are taken from section 34**; S107's Milky Way frame was re-measured with
the same command and reproduces its row (−0.067, A₂ 0.1635, A₃ 0.0388, 2.109, 0.0060, −1.75). There is no goal for the
edge-on frames and the tool does not measure them.

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope | q | a (px) |
|---|---|---|---|---|---|---|---|---|---|
| GOAL `milky_way` | −0.354 (−0.459 / −0.813) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 | 1 (set) | 2006 |
| illustrative, S107 | −0.067 (−0.637 / −0.704) | 0.052 | 0.164 | 0.039 | 2.11 | 0.0060 | −1.75 | 1 (set) | 411 |
| **illustrative, S108** | −0.068 (−0.634 / −0.702) | 0.051 | 0.164 | 0.038 | 2.11 | 0.0060 | −1.74 | 1 (set) | 411 |
| GOAL `ngc_4414` (the tool's geometry) | −0.274 (+0.508 / +0.234) | 0.099 | 0.068 | 0.055 | 2.72 | 0.157 | −2.09 | 0.512 | 664 |
| illustrative, S107 | −0.425 (+0.722 / +0.297) | 0.079 | 0.042 | 0.037 | 1.64 | 0.185 | −2.25 | 0.504 | 399 |
| **illustrative, S108** | −0.425 (+0.722 / +0.297) | 0.079 | 0.042 | 0.037 | 1.64 | 0.185 | −2.25 | 0.504 | 399 |

NGC 4414's numbers are S107's to the last digit the tool prints, as they must be: the frame is S107's byte for byte.
The Milky Way moved by the grain only (A₁ 0.0517 to 0.0509, A₃ 0.0388 to 0.0384, the slope −1.75 to −1.74, the colour
step −0.067 to −0.068, the tool's point counts 869 / 487 to 876 / 483); nothing moved nearer or further from the goal
by more than that. Every distance of section 34 stands: the Milky Way's colour step (−0.068 against −0.354), NGC 4414's
inner colour, A₂, arm contrast and dark fraction.

## 39. What a viewer sees, in the lead's words (the lead looked at the merged head's frames beside both goals)

**The Milky Way, full frame:** S107's picture (two major arms opening from the bar's ends, patchy blue-white grain,
pink regions on brown lanes, a cream-orange bar). Beside the goal, whole and inner zone side by side, the lead's list:
(1) the goal's arms spring from the bar's ends and hug the bar as an oval ring at 1.2 to 1.4 bar half-lengths, with the
picture's brightest pink-white complexes at the bar's ends and a short inner arc along each long side of the bar; ours
has its first arm at about twice the bar's half-length and an empty dark lavender moat between; (2) the goal's bar is
pale cream, grainy, fading softly, with fine curling lanes inside; ours saturated yellow-orange, smooth, with a white
halo rim; (3) the goal has four near-equal arms at about 12 degrees wrapping more than a turn and filling the disc;
ours two dominant wide-open arms whose outer turns sweep past where the goal's disc has faded; (4) the goal's arms are
a dense mottled cloud texture; ours a smooth glow with sparse points all of one white; (5) the goal is more muted, its
inter-arm disc a medium blue-grey with grain. **Close stand:** the brightest soft discs are gone (the cap), but fainter
soft round blue dots 8 to 12 px across are still scattered between and beside the arms: reduced, not mended.
**Edge-on (88 degrees):** a thin disc with a warm bulge above and below and a dark lane, but the pink regions and
blue-white sparkle make a busy dotted band all along the lane and in front of it; the disc is bluish-white. It reads as
a galaxy seen edge-on, not yet as a good picture of one.

**NGC 4414, full frame:** S107's, unchanged. Beside the photograph, the lead's list: (1) the photograph's disc
overfills the frame and dims strongly outward into a blue-grey haze with star clouds; ours is a sharp-edged oval of
even brightness with a bright grainy rim, about three quarters of the frame's width; (2) the photograph has a large
soft cream bulge glow in a gold-tan inner disc; ours a small nucleus in peach-orange; (3) the photograph's dust is warm
brown in two or three broad spiral bands of fine filaments with clean bright zones between; ours grey-black short
dashes scattered evenly (fingerprint strokes); (4) the photograph has lumpy white and blue-white star clouds all
through the middle disc; ours an even speckle with clouds near the rim only. **Close stand:** S107's picture turned
1.6 degrees: dark filaments and knots across a crisp grain, star clouds at the rim. Good. **Edge-on:** a classic
edge-on spiral: a thin disc, a dark dust lane with the star clouds speckling it, a large soft cream bulge. Good; the
bulge's glow is boxy at its top edge. Between 78 and 82 degrees a faint brushed texture remains (the half-faded veil and
mottle).

**Away from the stands:** orbiting, the picture keeps its roll; physics only shows the physical look; rerolled
galaxies differ from one another, and a rerolled Milky Way can still show crescents round the bar (the inner zone's
work, ruling 36).

**The distance, plainly.** S108 moved neither tuned frame nearer its goal; it made the look survive the camera, the
controls and a reroll. Both full frames are still plainly unlike their goals in the ways listed above, and those lists
are what S109 works on (`BUILD_VIII.md` section 6, items 2 and 4).

The frames: `docs/pictures/s108/` (committed; sha256 in D279). The close-ups, the physical frames, the sheets and the
lead's goal-beside-ours pair sheets are local (never committed).

## 40. A second reader (the documents' writer, who built none of it)

The writer of S108's close documents looked at both goal pictures, the four committed frames, the two close-ups, the
close's two sheets (which carry the physical frames beside them), the lead's four pair sheets (goal left, ours right:
whole and inner zone of each) and the reviewer's inclination sheet of the Milky Way (0 to 180 degrees), and cropped
three regions at twice their size to check what is said here. Where this agrees with the lead: the empty dark lavender
moat round the Milky Way's bar and its first arm far out; the saturated yellow-orange bar with a pale rim; two
dominant open arms against the goal's four; the remaining soft blue dots close up; NGC 4414's even, sharp-edged oval,
small peach nucleus, evenly scattered dashes and fingerprint stripes; NGC 4414 edge-on the best frame of the four. What
the lead's words do not say, or where this reader disagrees:

- **The soft blobs are not only close up.** In the Milky Way's full frame at least one soft round blue disc sits on the
  inter-arm disc right of and below the bar (about x 795, y 755 of 1024), the same mark the cap was meant to remove. And
  **NGC 4414 has its own soft blobs**: pale round-to-oval patches 15 to 40 px across, cream in the middle of the disc
  and blue-white near the rim (in the full frame about x 590 y 620, x 780 y 450, x 240 y 390; in the inner pair sheet
  three peach ovals round the nucleus). They read as out-of-focus discs, not as the photograph's lumpy star clouds, and
  they sit in the middle disc as well as at the rim, so "clouds near the rim only" understates them: there are clouds
  in the middle, but as soft blurs.
- **The Milky Way's bar has two hairline dark lanes along its long sides that run straight past the bar's ends** into
  the lavender moat, and a pale streak leaves the bar's upper-right end; the goal's bar lanes are fine curling threads
  inside the bar. The lead's list says the goal's bar has curling lanes; it does not say ours now has straight ones
  that overshoot.
- **The Milky Way's pink regions are large pale pink flower-like clumps** on the outer side of the arms, far more
  conspicuous than the goal's small red-magenta knots strung along the lanes, and the lanes close up still zigzag in
  sharp opaque brown kinks with forks (S107's second reader's point, unchanged). The close stand's inter-arm disc is a
  flat slate grey, darker and greyer than the goal's blue-grey.
- **The Milky Way edge-on: this reader sees less of a bulge than the lead does.** There is a warm brightening where the lane
  crosses the centre, but no round bulge standing above and below the disc; the disc is a long thin blade inside a
  broad soft bluish halo, the lane is a grey band filled with regions and sparkle rather than a dark one, the pink
  regions crowd most at the two tips, and the lower-left tip ends in a bright point with a small flare. A real edge-on
  spiral (the kind the eye knows from NGC 891 or NGC 4565) shows a dark, continuous lane splitting the disc lengthwise,
  the bulge rising above and below it, the disc fading toward the tips, and its star-forming regions mostly hidden
  behind the lane; this frame has the blade and the halo, and little of the rest. The reviewer's inclination sheet
  shows the busy band already from 84 degrees.
- **NGC 4414 edge-on is good, but its lane reads as a translucent grey strip, not dust.** Cropped at twice the size the
  lane has hard straight edges with a thin orange rim on each side, a nearly constant width to both tips, and an even
  speckle of gold-white points across its whole width; real lanes are darkest and widest at the centre and thin toward
  the tips, with few stars in front. The bulge's glow above the lane ends in a sharp straight edge along it and flares
  outward in a bow-tie with straight sides, which is what "boxy at its top edge" describes; at a glance it reads a little
  like a lens flare more than a round bulge.
- **NGC 4414's close stand still shows the dark smeared texture along the far rim** (the top of the frame) that S107's
  second reader saw at the near-side rim, and its grain is still the uniform sand of section 36 with a pale peach blob
  in the lower left. The lead calls the close stand good; it is S107's picture, with S107's faults.
- **NGC 4414's full frame has a ragged sparkly fringe on its left end**, with a bright knot at the tip (about x 65, y
  410), and a dark fibrous mesh along its upper-left rim: the photograph's edge is a soft haze with no such fringe.

---

# Part S109 — the two tuned full frames against their goals (D280)

## 41. What S109 changed in the frames

BUILD_VIII rows 123 to 126 (D280), viewer-only (model hash 5a862a70..., no model byte moved; the picture test's nine
physical frames byte for byte at every hand-back and on the merged head). S109's subject was the two tuned full frames,
which S108 had listed as plainly unlike their goals. **NGC 4414** (four passes and the lead's pick): the disc now
overfills the frame (`framing.scale` 0.62 -> 0.45) and dissolves at its edge (`edge.radius` 16, `width` 14) under a
radial fall-off of the layer's own with a blue outer disc; brown ink in four log-spiral dust bands; a soft cream glow
with a white-hot core; a multi-scale star-cloud field (heaps between the bands). **The Milky Way** (three judged passes,
then two rounds of variant sheets and the lead's own fourteen variants): four arms, the first an oval through the bar's
ends; a cream bar held to its ellipse; the roll 25 -> 15 degrees (the bar at the goal's angle); `framing.scale` 0.84 ->
0.77 (the bright disc about 0.40 of the frame's width, the goal's 0.38); the arm map read at the arm's nearest point
(the combed streaks and wedges gone); the soft blue discs gone (`arms.sparklecap` 10). Every illustrative frame moved;
the four of the merged head are committed as plain pictures in `docs/pictures/s109/` (ruling 47).

## 42. The yardstick on S109's frames

`tools/goal_metrics.py` re-measured by the documents' writer on the two committed full frames of the close
(`docs/pictures/s109/`, 1024 px), as section 38 measured: the Milky Way with `--axis-ratio 1`, NGC 4414 at the tool's
own geometry. **The goal and S108 rows are taken from section 38** (the writer re-ran the tool on S108's Milky Way frame,
NGC 4414 frame and both goals, and each reproduces its row). There is no goal for the edge-on frames and the tool does
not measure them.

| picture | D(B−R) (in / out) | A₁ | A₂ | A₃ | arm / inter-arm | dark | slope | q | a (px) |
|---|---|---|---|---|---|---|---|---|---|
| GOAL `milky_way` | −0.354 (−0.459 / −0.813) | 0.052 | 0.194 | 0.059 | 1.83 | 0.0066 | −1.99 | 1 (set) | 2006 |
| illustrative, S108 | −0.068 (−0.634 / −0.702) | 0.051 | 0.164 | 0.038 | 2.11 | 0.0060 | −1.74 | 1 (set) | 411 |
| **illustrative, S109** | −0.268 (−0.409 / −0.677) | 0.019 | 0.110 | 0.024 | 1.84 | 0.0192 | −1.58 | 1 (set) | 356 |
| GOAL `ngc_4414` (the tool's geometry) | −0.274 (+0.508 / +0.234) | 0.099 | 0.068 | 0.055 | 2.72 | 0.157 | −2.09 | 0.512 | 664 |
| illustrative, S108 | −0.425 (+0.722 / +0.297) | 0.079 | 0.042 | 0.037 | 1.64 | 0.185 | −2.25 | 0.504 | 399 |
| **illustrative, S109** | −0.314 (+0.690 / +0.376) | 0.084 | 0.062 | 0.060 | 1.96 | 0.215 | −2.13 | 0.542 | 475 |

**The Milky Way.** Nearer: the colour step (−0.268 against −0.354; S108's −0.068 was nearly flat) and the arm
contrast, now the goal's (1.84 against 1.83). Further: A₂ (0.110 against 0.194; it was 0.164) and A₃ (0.024 against
0.059), the dark fraction (0.0192, three times the goal's 0.0066 where S108's 0.0060 was at it) and the slope (−1.58
against −1.99). The tool's dominant m is still 2, with A₄ 0.096 (the goal's 0.107). The lead's note that A4's 0da396f
frame measured A₂ 0.212 is for a frame that is not this one: the lead's last pick (calmer arms, the disc light back
between them) took the two-armed measure down to 0.110 and the dark fraction from 0.119 to 0.0192. The point counts
are 526 inside and 449 outside (S108's 876 / 483, the goal's 518 / 139).

**NGC 4414.** Nearer on the colour step (−0.314 against −0.274), A₂ (0.062 against 0.068), A₃ (0.060 against 0.055),
the arm contrast (1.96 against 2.72; it was 1.64), the slope (−2.13 against −2.09) and the bright points inside the
disc (**20** against the photograph's 97; S108's 8; the lead's "about 28" is B4's frame, not the picked one). Further:
the dark fraction (0.215 against 0.157; S108's 0.185 was already over) and the outer colour, redder than S108's (+0.376
against the goal's +0.234; S108 +0.297); the inner colour is still much redder than the photograph's (+0.690 against
+0.508). **What is comparable.** The framing changed: the tool's outline (the brightest pixels holding 90 % of the
light) grew from a = 399 to 475 px of the frame's 512 half-width, with q 0.542 and the angle 27.2 degrees; the frame's
border, from which the sky is taken, is still dark (the sky subtracted 0.0004 to 0.0012 in linear light), and all 24
rings of the 0.2 to 0.8 a band lie inside the frame, as at S108 and on the goal. So every number is computed the same
way, but on a larger ellipse that the frame and the new fall-off set as much as the disc does: the rings at a given r/a
sit at a larger radius on the disc than S108's, and the "outside" point counts (236 here, S108's 229) are over a smaller
area of sky. Read the S108 / S109 pairs for NGC 4414 as change of kind, not ring for ring; the comparison with the
goal, whose outline (664 px of a 1730 x 1428 picture) is fitted the same way, is the one that holds. Nothing here was
counted that the tool does not measure (the bright-zone texture, the dust's colour, the arm count by eye).

## 43. What a viewer sees, in the lead's words (the lead looked at the merged head's frames beside both goals)

**The Milky Way, full frame:** for the first time the goal's KIND of picture: a spiral of four arms on a lavender-blue
disc, the first arm an oval through the ends of a cream bar set at the goal's angle, pink regions in bunches and
dark-brown lanes along the arms, a soft fade at the edge, the disc at the goal's size. Still unlike the goal: two of
the four arms are broad and dominant where the goal's four are nearer equal and narrower, with more wraps; the arms
are an icy pale blue made of a UNIFORM fine speckle (salt), where the goal's are knotted clusters and cumulus-like
clumps with a turquoise tint; the lanes are thin continuous dark strokes where the goal's are broken reddish-brown
filaments strung with pink; the pink regions are fewer and larger than the goal's many small ones; the bar is softer
and paler than the goal's bright grainy cream with its distinct edge, and the dark ground beside the bar's long sides
is weak; no tight inner arcs along the bar's flanks; the outer edge is ragged grain on a dim haze where the goal's is a
smooth glow; no faint far arm at the right. **Close stand:** one or two broad pale-blue arms cross the frame with crisp
dark-brown braided lanes and pink bunches, fine bright grain, no soft discs, a calm blue-grey ground. Fewer arms cross
the fixed stand than at S108 (the spiral changed under it); each arm's glow ends in a soft band with a fairly straight
lower edge. **Edge-on:** a thin disc in a pale haze with a dark lane, crowded with pink regions and grain along its
whole length; the bulge is a faint warm glow, hardly a bulge. Not better than S108's; still busy.

**NGC 4414, full frame:** the photograph's kind of picture: a flocculent disc that overfills the frame and dissolves
at its edge, a white core in a cream glow, a warm tan inner disc, broken dark lanes winding in, heaps of white and
blue-white clumps, a dimmer blue-grey outer disc. Still unlike the photograph: the dust is sparser and greyer than the
photograph's dense warm-brown network (which covers about a third of the inner and middle disc, strongest on the near
side); the bright zones are an even sand with heaps rather than the photograph's lumpy cauliflower clouds; the outer
third is grey-white clumps on dark rather than a blue-grey haze; the glow round the core is a little broad; about 28
bright points in the disc against the photograph's 97 (the tool counts 20 on the picked frame, section 42). **Close stand:** a bright grainy star field with dark filaments and
knots and a white-cream glow at the bottom; blue-white heaps toward the rim. Against S107's close-up: the upper
(outer) half is darker and its texture a little smeared, the filaments in the lower half fewer and softer. Accepted
(ruling 43). **Edge-on:** a thin disc with a dark speckled lane and a bright cream bulge glow; the disc now runs to the
frame's edges (the larger edge radius); the bulge's glow is broad and slightly boxy.

**The distance, plainly.** Both full frames are now their goal's kind of picture at a glance, which they were not at
S108; neither is yet its goal at a second look. What separates them now is texture and balance (the Milky Way's
speckle against clumps, arm weights, lanes; NGC 4414's dust density and colour, cloud texture), most of it within the
owner's sliders' reach, some of it new drawing (`BUILD_VIII.md` section 6, items 2 and 3).

The frames: `docs/pictures/s109/` (committed; sha256 in D280). The close-ups, the physical frames, the sheets and the
lead's goal-beside-ours pair sheets are local (never committed).

## 44. A second reader (the documents' writer, who built none of it)

The writer of S109's close documents looked at both goal pictures, the four committed frames, the two close-ups, the
close's two sheets (with the physical frames), the lead's four pair sheets (goal left, ours right: whole and central
45 % of each), and S108's four committed frames and its merged head's two close-ups for the change. Places are given
in pixels of the 1024-px frames unless a sheet is named. Where this agrees with the lead: the Milky Way is now a
four-armed barred spiral with the first arm round the bar, the goal's kind of picture, and the arms are a uniform salt;
NGC 4414 is now a flocculent disc with a white core and broken lanes, and the dust is sparser than the photograph's.
What the lead's words do not say, or where this reader disagrees:

- **The Milky Way's arms have straight stretches.** The lane along the right-hand arm runs almost straight down from
  about (800, 280) to (800, 560); the inner arm below the bar runs almost straight across from about (430, 620) to
  (770, 600); a short isolated arm piece in the upper right (about x 620 to 700, y 250 to 430) points nearly radially.
  The goal's arms curve all the way round. Together they give the disc a squarish right side.
- **The speckle is not only on the arms, and the disc is greyer than "lavender-blue".** In the central pair sheet the
  white grain lies just as thickly on the ground inside the oval and between the arms; the goal's ground there is
  smooth. Beside the goal the whole disc reads grey-lavender, paler and less blue. The bar is itself a field of
  separate cream dots with a bright round nucleus and a faint ring round it, where the goal's bar is a smooth glow.
- **The Milky Way's close stand is no better than S108's, taken whole.** Better: S108's soft blue dots are gone
  entirely and the pink regions are smaller and more scattered. Worse: about half the frame (y 250 to 550) is empty
  grey ground and the lower quarter (below about y 760) falls to near-black, so the stand now looks at the disc's edge;
  and the lanes are heavier, darker and more continuous than S108's thin broken ones, further from the goal's.
- **NGC 4414's colour moved the wrong way in the outer disc.** The lead sees a dimmer blue-grey outer disc; this reader
  sees the whole disc warm tan to the rim, grey-white only in the outermost clumps, and the tool agrees: the outer
  ring is redder than S108's (+0.376 against +0.297; the photograph's +0.234), the inner still far redder than the
  photograph's. The near-side rim (the lower left, from about (60, 560) to (600, 880)) is a dark sooty skirt of brown-black
  mottle between the bright disc and the sky, where the photograph's near rim is blue-white clumps fading into haze.
- **NGC 4414's inner third has no white clumps.** In the central pair sheet the photograph's white cauliflower clumps
  reach right up to the bulge; ours is a smooth peach sand there with dark strokes, and in its right half the strokes
  still run parallel along the spiral (a fainter fingerprint). Left of the nucleus a cluster of black branching knots
  stands out darker than anything in the photograph. The tool counts 20 bright points inside the disc, not 28.
- **NGC 4414's close stand: better dust, worse light.** Against S108's (S107's picture turned): the dust is now a
  branching mesh of filaments and knots (lower left about (100 to 200, 860 to 920) a dense black branching knot)
  rather than S108's parallel strokes, nearer the photograph's network, so this reader does not find the lower half's
  filaments fewer; but the upper half is dark, its clouds broken into dim grey smudges, and the frame as a whole is
  browner and dimmer.
- **NGC 4414 edge-on is worse than S108's.** The lane now stops short with blunt, speckled ends at about x 110 and x
  870, and the faint grey disc goes on past them as a thin straight band to the frame's corners (about (0, 260) and
  (1024, 760)), which reads like a beam of light; S108's lane tapered to its tips inside the haze. The Milky Way
  edge-on is S108's picture smaller and less tilted, the pink regions now along the lane's whole length, a thin tail
  of grain beyond the halo at the left tip (about x 120 to 200, y 600 to 620).
