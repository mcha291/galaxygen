# HANDOFF_S56 (second turn) — the gas ridge on several modes: built as written, it does not fade and it spikes

**For Fable, one short turn (BUILD_III §3c, §3d). Read this file and at most the three ranges named at the end.
Run nothing, explore nothing, write nothing. Answer in at most 60 lines: the ruling in final wording, what it
predicts, what is forbidden.** Written by the Opus lead of S56, 2026-10-04. Your first ruling of this session (the
power follows the amplifier; the modes saturate together; phases on `texture_seed`; NaN with the layer off) is
transcribed in D215 and **built and green**: the stellar field is byte-identical to S55 with one mode; the m = 2–6
amplitudes are recovered to 4e-15 on every ring; no cell is below zero on 240 seeded galaxies (lowest +0.0026);
layer-off, 331 of 332 fields are bit-identical to S55 (the exception `arm_multiplicity`, 4 → 3; `ngc_4414` 4 → 2);
the 37 rows and the five template checks have not moved. This turn is about the gas only.

## What was ruled for the gas, and what it gives

The plan (BUILD_III §5): "with ψ = (c − 1)/A the stellar pattern scaled to unit amplitude, the ridge is
v = exp(κψ) over its ring mean, κ as S51 has it; the amplitude a(R) keeps S51's rule" — a(R) is set so that the
ratio of the gas's mean inside the arm mask to its mean outside equals the published `gas_arm_contrast` (2.73 at
the defaults; PHANGS's ratio of means). Your ruling 6: "ψ = (c − 1)/A stays as written — the gas fades with the
potential that drives it; nothing shocks on nothing."

Built exactly so (g = 1 + w_arm · a(R) · (v − 1) + the bar's term; κ = 4.98 from the measured width; the mask the
top share of the ring in ψ, the share from the power-weighted arm number). With one mode it is S51's field to
3e-15. **With several modes, on the default galaxy:**

1. **It does not fade.** The ratio-of-means rule sets 2.73 on every ring that carries any mode, so a(R) *grows* as
   the ridge flattens. At the last ring with a pattern (14.8 kpc; stellar amplitude 0.05, stars 0.95–1.05) the gas
   runs 0.34–1.90; the next ring is exactly 1. Your sentence and the rule you kept contradict each other.
2. **It spikes.** ψ is at unit *power*, so where crests meet it reaches Σ u_m = 2.19 at R₀, and e^{κψ} is a map
   calibrated on a cosine of reach 1. The crest at R₀ is **11.3** where S51's was 3.07 (trough 0.57 against 0.53);
   the field's range is 0.34–15.5 where it was 0.53–3.06; 1.0 % of cells hold 9.3 % of the gas;
   `sfr_modulation` peaks at 41.6. Downstream, layer-on only: clouds 16 822 → 16 718, clusters 12 930 → 12 863,
   the census's Q over the field's 1.038 → 0.969, the HII census over the field 1.014 → 0.945. The ratio of means
   is still 2.73 on every ring by construction: the sourced number is honoured and the picture is a few knots.

## Measured alternatives (the default galaxy, production grid; ring means 1 to 1e-15 in all)

| Form | Field's range | R = 4 kpc | R₀ = 8.2 | 12 kpc | 14 kpc | last ring 14.8 | Cells > 4 hold | ⟨g²⟩ by mass |
|---|---|---|---|---|---|---|---|---|
| S51, one mode (the regression) | 0.53–3.06 | — | 0.53–3.07 | 0.61–2.72 | — | — | 0 | — |
| **A. As built** (ψ at unit power) | 0.34–15.5 | 0.66–2.37 | 0.57–11.4 | 0.58–15.5 | 0.57–7.3 | 0.34–1.90 | 9.3 % of the gas | 1.84 |
| **B.** ψ over its peak bound, ψ = Σ A_m cos / Σ A_m ∈ [−1, 1] | 0.51–9.7 | 0.65–1.87 | 0.51–5.4 | 0.54–9.6 | 0.56–6.1 | 0.58–2.87 | 4.6 % | 1.36 |
| **C.** A with the ratio following the gain, C(R) = 1 + (C − 1)·min(1, Σw) | 0.56–15.5 | as A | as A | as A | 0.63–6.4 | 0.98–1.02 | 9.3 % | 1.84 |
| **B + C** | 0.51–9.7 | 0.65–1.87 | 0.51–5.4 | 0.54–9.6 | 0.62–5.4 | 0.99–1.05 | 4.6 % | 1.36 |

Even with ψ bounded by 1 (B) the crest is 5–10: with several modes ψ sits near 0 over most of a ring and reaches
its bound only where every crest aligns, so the ring mean of e^{κψ} is small and the aligned point towers over it.
**The exponential of a sum of modes makes knots, not ridges, whatever the scaling.**

**A form not built or measured, for your judgement — E, the ridge by rank.** On each ring the cells take S51's
ridge values in the order of ψ: v(φ) = V(q(φ)), q the fraction of the ring with ψ above ψ(φ) and V the von Mises
ridge as a function of that fraction (for one mode q = |θ|/π, so it is S51's field exactly). Every ring then has
S51's histogram — crest 3.07, trough 0.53 at R₀, the ratio of means 2.73 with the same mask by construction — and
the gas lies along the stellar crests in order of their height. It is evaluable at a point (the ring's ψ is
ranked on the fixed 360-cell quadrature the mask already uses). What it gives up: the ridge's width is the
measured one only for one mode; with several, a tall crest takes a wider ridge and a low crest none.

## Constraints you set that still bind

No new constant; the single-mode regression to 1e-9; ring means 1; the gas finite everywhere; nothing composed
from `arm_multiplicity`; the stellar side is not reopened. P2 (S57, gates G2 and G3) replaces this ridge by the
steady shock per ring: whatever is ruled here is published for one session and is the instrument P2's solver is
compared against at one mode.

## Questions

1. **The fade.** Which rule makes the gas fade with the potential: C (the ratio of means follows the disc's gain,
   the number that already scales the stellar power), the ratio following the amplitude (√gain), or another?
2. **The spike.** A as built, B, E, or another form? If E: is a rank map a law the model may publish for one
   session, and what is its named alternative?
3. Is the answer the same inside the bar's reach, where S51 keeps the taper and the bar's term outside the ridge
   (the builder kept that: it is the only reading under which one mode is S51's field)?
4. `sfr_modulation` and the censuses follow the gas. Is a bound on the gas's crest (e.g. S51's single-mode crest)
   a property the ruling should guarantee, or only report?

## The ranges you may read (at most these three)

1. `model/galaxy/stages/gas_pattern.py` lines 1–68 — the stage's docstring: the form, the ridge, the mask, the
   amplitude, as built.
2. `model/galaxy/stages/gas_pattern.py` lines 263–342 — `_ring` (the quadrature, the mask, a(R)) and `contrast`.
3. `docs/DECISIONS.md` — D215, from the line starting `**A conditional gate (BUILD_III §3d; §6 lists it for S56)`
   to the end of the file.
