# READING_ARM_GAS_CONTRAST — how strongly the arms' molecular gas answers its stars: the model's chain and the measured relation (S101, D271)

**What this file is (2026-11-17, S101, BUILD_VI row 101).** The frames have no dust lanes in the arms (`READING_PICTURES.md`
sections 13, 19, 20). S101's scout L (an Opus agent, read and probe only; note `s101_L.md` in the session's
scratchpad) measured the chain from the stars' arm to the gas the clouds and the dust follow, and found the gap is the
gain; S101's reader RQ (note `s101_RQ.md`) then read the measured relation to the equation. What the gate took from
it is in `DECISIONS.md` D271 and register #234 (new), #228, #129, #131, #144.

**Tags.** READ — quoted from a page fetched at S101 (the place named); `[inferred]` / ARITH — the agent's own
arithmetic on read numbers; RECALL — not fetched; NOT READ and NOT PRINTED said plainly. Nothing here moved a
constant, a pin or a model byte.

---

## Part S101 — the chain measured, and the relation read (2026-11-17, BUILD_VI row 101; scout L, reader RQ)

### S101.1 The chain, measured on the model (scout L)

Production grid (400 rings), layer on, default seeds, the disclosed check's mask (1.5 kpc, `tests/gas_check.py`),
6-10 kpc, 53 rings; the probe reproduces the pinned check exactly (Milky Way 1.4311; NGC 4414 1.4294), so every
variant below is read on the same instrument. Milky Way first, `ngc_4414` in brackets.

| step | value | what it costs |
|---|---|---|
| the stars' arm, ratio of means in the mask | **1.458** [1.405] | not short: PHANGS's stellar median 1.28, grand designs 1.34 |
| forcing gain, razor thin, m/(X sin p) at the strongest harmonic | 1.32 median (0.58-3.0) [0.84] | X 6.1-10.7: a light disc for its κ |
| thickness factor T = 1/(1 + kh), h 357 pc | **0.66** (0.49-0.83) [0.76] | the largest single loss: without it 1.43 -> 2.03 [1.76] |
| pressure, 1/(1 + m²ε²) | 0.94 [0.96] | a few per cent |
| nonlinearity, solver against the linear response | 1.4311 against 1.4311 [1.4294 / 1.4264] | none: the steady co-rotating response is linear to four digits |
| net, rms gas over rms stars | **1.035** (0.76-2.66) | the gain is about one |
| the gas's ratio of means | **1.431** [1.429] | |
| the gas crest's FWHM across the arm | **1.28 kpc** [2.09] | the stars' 1.59 [2.41]: 0.87 [0.99] of them |

The thickness factor is sourced (Kregel et al. 2002's flattening, D219 item 5) and a razor-thin forcing blows up on
the pieces' square ends: it is not a knob. The cause is the law itself - a linear, steady pressure-and-epicycle
balance in the co-rotating frame. `gas_arm_contrast` 2.73 is a target named in a stage (D216 item 11 iv) that nothing
aims at or checks. The bar's taper (0.0015 over 6-10 kpc), #130's atomic blend (-2 %) and the ring normalisation
are each small.

### S101.2 Querejeta et al. 2024 (A&A 687, A293, arXiv:2405.05364) — READ (reader RQ, the HTML v1 and Fig. 5's image)

- **The contrast** (Sect. 2.7): "for each radial bin, we consider the mean surface density within the footprint of
  each spiral segment at that radius (arm value), and divide it by the mean surface density within the ring outside
  the spiral mask (interarm value)." A ratio of means, arm over inter-arm - the form of the model's `ratio_of_means`
  (its mask the stellar-ranked share, not a log-spiral footprint). Radial bins 500 pc; masks about 1-2 kpc wide
  (narrow masks 500-1000 pc); about 100 pc resolution; stars from Spitzer 3.6 µm (0.11 dex), gas ¹²CO(2-1) (0.14 dex).
- **The fit** (Sect. 3.3): "The trend is superlinear ... In the case of CO, the slope from a bisector fit is m=1.8";
  "The rank coefficients and linear fits refer to the mean contrasts over entire spiral segments".
- **Fig. 5's axes**: log(contrast) against log(Σ_star contrast); the fitted line crosses y = 1.5 near x 0.73
  (read by eye; ARITH 1.83 × 0.73 + 0.16 = 1.50) - **the fit is log-log**: log10 C_mol = 1.83 log10 C_star + 0.16.
- **Table 4, Σ_star - Σ_mol** (segments ρ / slope / intercept | all radial bins):
  nominal 0.73 / 1.83 ± 0.46 / 0.16 ± 0.03 | 0.46 / 2.23 ± 0.15 / 0.08 ± 0.02;
  narrow masks 0.65 / 1.83 ± 0.48 / 0.19 ± 0.03 | 0.48 / 2.19 ± 0.17 / 0.13 ± 0.02;
  1.5 kpc resolution 0.83 / 1.91 ± 0.25 / 0.05 ± 0.02 | 0.68 / 1.86 ± 0.09 / 0.05 ± 0.01;
  SFR from the MUSE subset 0.55 / 2.47 ± 2.06 / 0.19 ± 0.06 | 0.40 / 2.66 ± 0.51 / 0.12 ± 0.03.
- **Table 1's medians** (16th-84th): Σ_star 1.28 (−0.26 +0.49), Σ_mol 2.22 (−0.96 +2.19); grand design 1.34 / 2.73;
  the rest 1.23 / 1.90; at 1.5 kpc 1.15 / 1.49. The log form reproduces the medians (1.28 -> 2.27 against 2.22, ARITH).
- **The sample** (Sect. 4.1): "Only two galaxies in our sample are classified as flocculent (NGC 1385 and NGC 2283),
  as opposed to nine multi-armed and 17 grand-design." 59 segments in 27 galaxies with stars and gas, 44 in 21 with
  SFR as well; which set Fig. 5's CO fit uses is **not stated unambiguously**.
- **Caveats the authors print:** resolution first ("contrasts get strongly diluted when shifting from ~100 pc to 1.5
  kpc resolution", Sect. 4.4); scatter ("a relation that operates 'on average' ... even mean values over entire spiral
  segments, show significant scatter around this relation", Sect. 4.2); the masks ("the details of the spiral masks
  do affect individual measurements in a non-trivial way", App. E); α_CO and R21 (0.14 dex together); CO-dark gas
  (Sect. 3.5); selection (predominantly grand design); the inner radii near bars "complex". No fit by class.
- **NOT PRINTED:** the scatter about the fit (only ρ and the fit errors; per-point errors 0.11 / 0.14 dex) and the
  slope-intercept covariance. **No ridge width** of gas against stars is measured (the narrow masks raise the gas's
  contrast 10 % and the stars' 1 %, App. E; qualitative words in Sect. 2.6.1 and 4.4).

### S101.3 Meidt et al. 2021 (arXiv:2103.13247) — READ (reader RQ, ar5iv's full text)

- A different statistic: C = I / <I>_ref, the reference the mean of a radial bin's pixels below the 84th percentile,
  "irrespective of morphological environment" (Eq. 1, Sect. III.2); 150 pc, 67 galaxies.
- **Eq. 2**: "log C_CO = 1.41 log C_3.6um + 0.31, with an rms scatter of ~0.15 dex"; **Eq. 3**: "log C_CO = 1.29 log
  C_3.6um + 0.53, with ~0.3 dex scatter" (the 99th percentile) - "purely empirical references".
- **App. D.2, Eq. D1**: the physical form, v_T ~ sin i_p V_c (1 − Ω_p/Ω) (C_stars − 1) cos(θ − θ_sp), the contrast
  as M² = (v_T/σ)². In a co-rotating frame Ω_p = Ω and v_T = 0 - "large-scale gas compression ... should be absent
  at R_CR" - so **its physical form is zero in D216's frame**; only the empirical fits could sit there.

### S101.4 The simulations

Baba, Morokuma-Matsui & Saitoh 2017 (arXiv:1609.00097, READ by scout L on ar5iv): qualitative - "both stellar and
gaseous arms are formed simultaneously by 'large-scale colliding flows'", the clouds' mass segregation observable in
the dynamic model, no contrast number. Baba, Saitoh & Wada 2013: pure N-body, no gas. Wada, Baba & Saitoh 2011 and
Dobbs & Baba 2014 §3.7: no number (S98). The simulations are silent on the gain.

### S101.5 The worked values and what the gate ruled

At the model's stellar contrasts the nominal segment relation reads **2.89** (Milky Way, 1.46) and **2.69**
(`ngc_4414`, 1.405) (ARITH, reader RQ; envelope with slope and intercept both at ±1σ 2.27-3.68 / 2.15-3.37, not a
confidence interval) - against the model's 1.43 / 1.43. A power g = c_star^γ over its ring mean (scout L's probe 2)
reads 2.10 / 1.96 at γ 2 and 3.24 / 2.85 at γ 3.23, the crest narrowing to 0.79-0.88 and 0.64-0.73 of the stars'
with no width put in. The gate (D271): **#234** opened, the owner's (B12) between (i) D216's steady response kept for
the molecular gas and (ii) the arms' molecular contrast set by the measured relation inside D216's frame, one exponent
per galaxy solved to meet Table 4's nominal row - **(ii) recommended and built on a held head** (`batch-q-lanes`); a
shock (D216 re-opened) stays not recommended. A ridge under (ii) is still about 1 kpc wide: a real lane (20-150 pc)
is the clouds' (#228, #231).

### S101.6 Not read

The fit's scatter (not printed); Fig. 5's point count; the PDF against the HTML (same v1); Kim & Ostriker 2002 and
Baba et al. 2015 (cited by both papers for the slope-2 expectation); gas self-gravity's size in the response (RECALL:
Jog & Solomon 1984). No frame was rendered under any variant.
