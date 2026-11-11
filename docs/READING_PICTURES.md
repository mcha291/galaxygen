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
frame (a = 0.29 of the frame's half-side against the goal's 0.72); the goal's kpc scale (~15 kpc for a) is the
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
| 8 | "a small tan disc" (Milky Way) | display / metric | a = 0.29 of the half-side (goal 0.72); the colour level +1.0–1.1 mag at 6500 K; ~4000 K moves B−R by −1.10 `[inferred: hand computed, not rendered]` | not run (capture `radius_kpc` 20 → 14–15; white point → ~4000 K) | — | not run |

## 4. What the model does not hold

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
