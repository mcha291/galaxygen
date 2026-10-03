# HANDOFF_S56 — a conditional gate: Phase P1's law cannot be followed as written at two points

**For Fable, one short turn (BUILD_III §3c; §6 lists S56's gate as "if the probe contradicts §5"). Read this file
and at most the four ranges named at the end. Run nothing, explore nothing, write nothing. Answer in at most 80
lines: the ruling on each numbered question in final wording, with what it predicts and what is forbidden.**
Written by the Opus lead of S56, 2026-10-04, from a probe with the repository unchanged (BUILD_III §3g). Nothing is
built. The owner's answers after S55 are recorded (D215): rule A10 amended to expected ring totals until L1, the
plan's order kept; `ngc_4414` keeps its fit.

## Phase P1's ruling, as the plan states it (BUILD_III §5)

- *The law.* At each radius the weight of arm number m is the existing `swing_weight` evaluated at the local swing
  parameter X_m(R) — today's named alternative in `pattern.py` becomes the law; no new constant; m = 2–6.
- *The power is conserved, not the peak.* Σ_m A_m(R)² = A², A the single-mode amplitude the model publishes today
  (`arm_contrast`). One surviving mode returns today's field exactly.
- *The realisation (synthetic):* each mode's phase, on `texture_seed`; one pitch for all modes until P4.
- *The gas:* the ridge is exp(κψ) over its ring mean, ψ = (c − 1)/A the stellar pattern at unit amplitude; with
  one mode it is S51's field to 1e-9.

## The probe (both templates, the production grid; the phases drawn by the probe, no model stream touched)

`swing_weight(m, m_lo, m_hi, …)` is 1 inside the window, falls log-linearly to 0 at `SWING_X_DEAD` (too few arms)
and `SWING_X_FLOOR` (too many). Locally: X₂(R) = κ²R / (2πGΣ·2) with the checkpoint-1 disc's `epicyclic_frequency`
and `disc_surface_density`, the shear Γ(R) = 1 − d ln v / d ln R, the window m_lo = X₂/(Γ x_high), m_hi = X₂/(Γ x_low).

**The split is what the plan hoped for.** Milky Way defaults (A = 0.401, today's drawn m = 4), power shares m = 2…6:

| R kpc | X₂(R) | Γ | m = 2 | 3 | 4 | 5 | 6 | Σ_m w_m |
|---|---|---|---|---|---|---|---|---|
| 2.0 | 1.54 | 0.63 | 0.50 | 0.35 | 0.15 | 0 | 0 | — |
| 4.0 | 2.13 | 0.82 | 0.45 | 0.36 | 0.17 | 0.02 | 0 | — |
| 6.0 | 2.83 | 0.98 | 0.38 | 0.35 | 0.20 | 0.08 | 0 | — |
| 8.0 | 3.96 | 1.10 | 0.27 | 0.27 | 0.23 | 0.14 | 0.07 | — |
| 10.0 | 6.00 | 1.17 | 0.09 | 0.24 | 0.24 | 0.24 | 0.19 | 4.19 (the maximum, at 9.9 kpc) |
| 12.0 | 9.82 | 1.19 | 0 | 0.07 | 0.30 | 0.32 | 0.32 | — |
| 14.8 | — | 1.19 | 0 | 0 | 0 | 0 | 1 | 0.015 (the last ring with a mode) |
| ≥ 14.9 | 23 → 576 | 1.2 | 0 | 0 | 0 | 0 | 0 | 0 |

Two arms inside, five and six at the solar radius and beyond; 169 of 400 rings hold three or more modes above 5 %.
`ngc_4414` is the same shape, more compact: two modes inside 5 kpc, 4–6 at 8–10 kpc, nothing past 11.5 kpc.

**Contradiction 1 — rings with no surviving mode.** X grows without bound as Σ falls: past 14.9 kpc (Milky Way;
2.2 % of the disc's mass lies outside) and 11.6 kpc (`ngc_4414`; 1.0 %) every weight for m ≤ 6 is zero — 202 and
246 of 400 rings. There "Σ_m A_m² = A²" has no solution. And just inside, the per-ring normalisation hands the full
power A² to a ring whose total weight is 0.015: the pattern is at full strength where the amplifier is at 1.5 % of
one mode, and gone at the next ring. Today's single spiral runs to the grid's edge at full amplitude.
`compute_pattern` already has a fallback for a *global* window that selects nothing: the m nearest its centre.

**Contradiction 2 — the conserved-power sum makes negative densities.** A cosine's peak is A; five modes of equal
power peak at √5 A. The worst ring's Σ_m A_m is 0.89 at the default seed (A = 0.40, still positive), 1.07 at the
grand-design mean with no scatter (A = 0.48), 1.38 at +1σ of the amplitude's scatter. Over 120 pattern seeds with
random phases, bar term included: **21 galaxies of 120 have a cell below zero** (25 for `ngc_4414`); the minimum
contrast has median +0.215 and worst −0.374; the mass-weighted share of negative cells is 0 at the median and
1.6 % at worst. A (the seeded amplitude) has median 0.46, 5–95 % 0.19–0.72. Today's single mode cannot go negative
(A < 1, and the bar's cap is 0.9 under a taper that never sums the two at full weight).

**What holds.** One fully amplified surviving mode (w = 1 for one m, 0 for the rest) returns today's field; 8–9
rings are in that state. The gas ridge's definition (exp(κψ) over its ring mean) is positive for any ψ.

## The options

**Q1, the rings the amplifier does not reach, and the normalisation.**
- **N1.** Per-ring normalisation as written; no pattern where no mode survives (contrast 1). The pattern ends at
  14.8 kpc in a step from full power to none.
- **N2.** Per-ring normalisation, and the existing fallback (the nearest m, here 6) where none survives: arms to
  the grid's edge at full power, as today, six-fold.
- **N3.** The power follows the amplifier: A_tot(R)² = A² · max_m w_m(R), split among the modes by w_m / Σw. Full
  power wherever at least one mode is vigorously amplified (every ring inside ≈ 12 kpc), fading continuously to
  zero as the best mode's weight falls; one fully amplified mode still returns today's field exactly; no new
  constant. "Power conserved" then means *the sourced power where the disc amplifies, less where it does not*.
- **N4.** One normalisation for the whole disc: A_m(R)² = A² w_m(R) / W with W the mass-weighted mean of Σ_m w_m,
  so the disc-averaged power is the sourced one. Local power then exceeds A² where several modes are in the
  window (Σw reaches 4.2), which makes contradiction 2 worse, and no ring returns today's field.

**Q2, positivity.**
- **P1.** A floor: the composed contrast is max(c, 0), each ring renormalised to mean 1. Touches only the cells
  that would be negative (none at the default seed; at most 1.6 % of the mass); the single-mode field is
  untouched; the published amplitudes are the pre-floor ones and the Fourier gate is asserted on unfloored rings,
  the floored share published.
- **P2.** A bound on the peak: on a ring where Σ_m A_m (with the bar's term) would exceed 1, the arm amplitudes
  are scaled down together to make it 1. Positive for any phases; the law stays a law (no dependence on the
  realisation); costs power on those rings — at A = 0.48, about a tenth of it at the worst ring; roughly half of
  all seeds lose some.
- **P3.** A positive map: c = exp(s) / ⟨exp(s)⟩_ring with s the sum of modes — the form the gas ridge already has.
  Always positive, ring mean 1; **the single-mode field is no longer today's cosine**, so every pin on the stellar
  contrast and the "returns today's field exactly" clause go.
- **P4.** Cap the seeded amplitude so √5 A ≤ 1 − bar: changes the amplitude's sourced distribution.

**The lead's recommendation: N3 and P1.** N3 keeps the regression clause, needs no constant and removes the step;
P1 is the smallest departure and leaves the default galaxy's law untouched. Named alternatives: N1 (the plan's
words, with the step recorded as a debt) and P2 (a law-side bound, at the price of power in half the galaxies).

## Questions

1. Q1: which of N1–N4, or another form? In final wording. If N3: is "max_m w_m" the right measure of the
   amplifier's strength, and does the amended sentence replace "Σ_m A_m(R)² = A²" in BUILD_III §5?
2. Q2: which of P1–P4, or another? If P1: is a floor a property of `compose` (the composed field) or of the law,
   and what does the Fourier gate assert?
3. The local X uses the checkpoint-1 disc's Σ (the spin's exponential, stars and gas together) because the
   pattern stage is at checkpoint 3 and star formation at 4 (D174). Acceptable, or must it say more?
4. `arm_multiplicity` (the drawn m, published and read by the gas pattern and the viewer) retires with its draw
   (Appendix B). The lead proposes: five radial fields `arm_mode_amplitude_2 … _6` (derived, the law), five
   synthetic scalars for the phases (a layer stage on `texture_seed`, the first reader of that seed), and
   `arm_multiplicity` kept as a derived scalar — the mode holding the most mass-weighted power — so what reads it
   keeps a meaning. Right, or should the scalar go?
5. With the layer off the three composed fields are 1 (S55). The mode amplitudes are radial, derived, and
   bit-identical on and off; the phases are synthetic and their neutral is not 0-phase-but-drawn: with the layer
   off no field reads them. Is a synthetic scalar with the layer off published as NaN (D164: dead is NaN), as 0,
   or unpublished?
6. Anything in the plan's P1 text this probe makes you want to change beyond Q1 and Q2 (for instance: one pitch
   for all modes means every mode's arms are parallel logarithmic spirals that only beat in azimuth).

## The ranges you may read (at most these four)

1. `docs/BUILD_III.md` lines 327–352 — Phase P1's text.
2. `model/galaxy/stages/pattern.py` lines 55–83 — `swing_window` and `swing_weight`.
3. `model/galaxy/stages/pattern.py` lines 300–345 and 390–445 — `ArmPattern` and `compute_pattern`.
4. `docs/DECISIONS.md` — D215, from the line starting `### D215.` to the end of the file.
