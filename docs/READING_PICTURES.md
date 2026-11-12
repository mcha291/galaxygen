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
  h = σ_z² / (2πGΣ) evaluated at `R_SUN` = 8.2 kpc on every template (`stages/vertical.py`). In `ngc_4414` that is
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
  angle, not amplitude); the light holds 0.294 without the bulge, 0.274 with it, 0.252 with the dust — the tool's
  0.12–0.14, section 3's row 3. By the same tool the goal's bar is 2.4 times that in either convention (0.58–0.68 in
  the stage's, near the 84th percentile of the source's distribution): an artist's impression, no target (C6). What a
  source could say is the Milky Way's own bar: `READING_BAR.md` holds Portail et al. 2017's bar and bulge mass, 1.88 ×
  10¹⁰ M☉, against the model's 1.21 × 10¹⁰ (0.64 of it; the analyst's arithmetic `[inferred]`). #146's, amended.
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
