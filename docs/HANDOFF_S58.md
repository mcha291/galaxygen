# HANDOFF_S58 — a conditional gate before Phase P3's build: the bar's presence, its body, its gas, and the arms next to it

**For Fable, one short turn (BUILD_III §3c, §3d: "a source contradicts what this plan assumed" and "a ruling here
cannot be followed as written"). Read this file and at most the five ranges named at the end. Run nothing, explore
nothing, write nothing. Answer in at most 80 lines: the ruling in final wording, what it predicts (B4), the gate
the build must meet, what is forbidden, and what part, if any, is the owner's.** Written by the Opus lead of S58,
2026-10-04. Nothing is built; the repository holds only the reading (`docs/READING_BAR.md`, two blind readers).

## The plan's text for P3 (BUILD_III §5), and where it cannot be followed as written
*The body:* inside the bar radius the ring's **old** stars are concentrated along the bar's axis by a mean-one
two-fold ridge whose axis ratio and light share are the sourced medians; the young stars and the gas follow the gas
response, "which now feels the bar's potential too"; no ring total changes. *The absence:* presence derived from
the sourced stability criterion; a seeded residual only if a galaxy-to-galaxy scatter is read, otherwise none and a
debt; an unbarred galaxy publishes NaN for the bar's fields; rows 15–17 unchanged for the Milky Way, "whose template
pins it barred". *The lanes:* a template curve with sourced parameters, synthetic. *Gate:* ring totals unchanged;
rows 15–17 unchanged for the Milky Way; the m = 2 Fourier amplitude inside the bar against the sourced value.
Three places it stops: (i) it names no criterion, and the reading gives three with no scatter and none that
separates the two templates; (ii) "the gas response feels the bar's potential" meets D216 item 8 — the bar turns at
Ω_b, a second frame on the ring, "P3's"; (iii) D215's ruling 12 names "P3's bar-driven m = 2" as #138's closer, and
the phase's text builds no driven arm.

## What was read (`docs/READING_BAR.md`)

| Topic | As read |
|---|---|
| Light share | Bar/T ≈ 0.10 of the **whole galaxy's** light at M⋆ > 10¹⁰ M☉ (Gadotti 2011, peak; 0.14 for strong bars, Kruk 2018; range 0.03–0.47, Weinzirl 2009). No 3.6 µm statistic found. |
| Shape | 2-D component ε ≈ 0.6, i.e. b/a ≈ 0.4 (Gadotti; ellipse fits read 20 % lower: ε ≈ 0.5); b/a = 0.31 ± 0.12 for strong bars (Kruk); boxiness c ≈ 3, always > 2. |
| Profile along the bar | Sérsic n_bar ≈ 0.3 (flat) where B/T > 0.2, ≈ 0.85 (exponential) with no bulge, changing near 10^10.2 M☉ (Kim 2015); the S⁴G fitting function is a Ferrers form with exponent 2. |
| m = 2 amplitude | stacked S⁴G bars: A₂ maximum 0.23–0.41 by mass bin, **at 0.76–0.94 of the bar radius** (Díaz-García 2016b). The model's `bar_contrast` is S⁴G's A₂^max median 0.374, drawn log-normally (S26). |
| Size | bar length 1.3–1.5 h in S0–Sab, 0.6 h in Sc–Sd (Erwin 2005); log a = 0.04 + 0.76 log h (Erwin 2019); nothing beyond 3 h. |
| Presence | **No source gives a barred fraction as a function of a criterion's value, nor a galaxy-to-galaxy scatter about a threshold.** ELN (ε = V_max/(G M_d/R_d)^½ ≤ 1.1): right for 72–75 % of bars and 75–81 % of unbarred discs in TNG and SPARC, wrong for 55 % of 91 galaxies in another test, rejected by two papers. Fujii 2018: t_b = (0.146 ± 0.079) exp[(1.38 ± 0.17)/f_d] Gyr, f_d the disc's share of V² at 2.2 R_d; threshold f_d ≈ 0.30–0.35; a second parameter (Q) moves t_b from 0.27 to 8.8 Gyr at one f_d. Erwin 2018: the measured frequency, a logistic in stellar mass peaking at 0.70 at 10^9.7 M☉, flat in gas and colour. |
| Lanes | on the **leading** side, from the bar's end on its major axis to a nuclear ring (r_ring ≤ a/4; simulations r_ring/a = 0.062 Q_b^−0.46) near the minor axis, concave to the major axis; curvature against bar strength is an upper envelope with a wide spread (κ·a 0.12–2.37 in ten galaxies; two fitted laws disagree in the sign of the axis-ratio term); **no width and no compression are printed** but one simulation's Σ_peak ~ 10 × the initial. |
| Gas in the bar | disputed in numbers: "bars are not always deserts" (PHANGS: bars hold 19.8 % of H₂ in 10.5 % of area) against cleared bar regions in early-type strong bars; star formation along the bar in late types, at its ends and centre in early types. |
| Arms against the bar | arms begin within 20° of the bar axis in 10 of 12 galaxies (by eye, unsigned); bar forcing correlates with the local m = 2 amplitude out to 1.4–1.6 bar radii (Salo 2010), 1.5–2 in N-body; bar–spiral strength correlated in some samples, not in others; most bars and arms have different pattern speeds; bar fraction 50 % among two-armed spirals, 16–25 % among many-armed. No driven amplitude against radius is printed. |

## What the model's discs read (probes, repository unchanged; published fields, hand arithmetic)

| | R_d kpc | V_max | ELN ε | f_d at 2.2 R_d | Fujii t_b Gyr | a_bar = 2.0 R_d | drawn B | observed |
|---|---|---|---|---|---|---|---|---|
| `milky_way` | 2.605 | 250.1 | 0.804 | 0.600 | 1.46 | 5.21 | 0.289 | barred |
| `ngc_4414` | 1.755 | 239.2 | 0.715 | 0.756 | 0.91 | 3.51 | 0.321 | **no bar** (RC3 SA, S⁴G fits none) |

- **Every criterion bars both templates, and nearly every input.** ε and f_d do not depend on the halo's mass at
  all (checkpoint 1 is scale-free: 0.804 and 0.600 from 10¹¹ to 10¹³ M☉). Over the controls' ranges, one at a
  time: `disc_spin` 0.005 → 0.05 gives ε 0.68 → 1.12 and f_d 0.84 → 0.32 (unbarred only at the last value, by ELN
  alone); `baryon_retention` 0.05 → 0.5 gives ε 1.46 → 0.77 (unbarred only at 0.05, f_d 0.27); `halo_assembly_z`
  0.5 → 5 gives ε 0.76 → 0.92. So a derived presence is "barred" on almost the whole input space, has no mass
  dependence to set beside Erwin's curve, and is wrong for the one unbarred galaxy the build holds.
- **The bar's length** is 2.0 R_d against the reading's 1.25–1.5 h (early types) and Erwin 2019's 2.27 kpc at
  h = 2.6 (row 15 passes at 5.21 on #80's terms; not this phase's to move unless you say so).
- **A body as a two-dimensional component** — Σ_bar(m), m = ((|x|/a)^c + (|y|/(q a))^c)^{1/c}, its mass taken ring
  by ring from the ring's own stars, so the contrast is 1 − β(R) + Σ_bar(R, φ)/Σ⋆(R), β the bar's share of the
  ring, mean 1, no ring total moved — on the Milky Way template (`ngc_4414` within 5 %), share of the stellar disc:

| Body (q, c, profile) | share | β max | A₂ max, at | A₂ at 0.85 a | min contrast |
|---|---|---|---|---|---|
| today's cosine, B exp(−(R/a)⁴) | 0.052 (positive lobes) | — | 0.289 at 0 | 0.171 | 0.71 |
| 0.4, 3, Ferrers exponent 2 | 0.10 | 0.35 | 0.262 at 0.42 a | 0.042 | 0.79 |
| 0.4, 3, Ferrers exponent 1 | 0.10 | 0.26 | 0.237 at 0.53 a | 0.114 | 0.80 |
| 0.4, 3, Sérsic 0.3, r_e = a/2 | 0.10 | 0.30 | 0.248 at 0.47 a | 0.081 | 0.80 |
| 0.4, 3, Sérsic 0.85, r_e = a/2 | 0.10 | 0.53 | 0.197 at 0.44 a | 0.091 | 0.82 |
| 0.31, 3, Ferrers exponent 2 | 0.14 | 0.60 | 0.448 at 0.34 a | 0.056 | 0.65 |

  A share of 0.10 at b/a 0.4 gives A₂^max 0.20–0.27, under the 0.374 the model draws and at the bottom of the
  stacks' 0.23–0.41, and **it peaks at 0.4–0.5 a where the stacks peak at 0.76–0.94 a**: two sourced numbers (the
  light share, the A₂ maximum) describe one thing and do not agree through these profiles. r_e/a is not sourced.
  Checkpoint 3 has no stellar surface density (it is checkpoint 4's); the cp1 total disc is what a pattern stage
  may read, as the arm law does.

## The lead's draft (for your judgement; nothing here is ruled)
1. **Presence: derived, no draw, with a debt; the templates pin their measured structure.** Fujii's time against the
   disc's age (f_d is already published as `disc_dominance`; coefficients sourced), ELN the named alternative. It
   bars both templates, so `ngc_4414` is pinned unbarred and `milky_way` barred (the plan's own word), the
   criterion's miss on NGC 4414 recorded as a finding. Erwin's logistic as a probability is refused: a measured
   frequency in stellar mass is not a residual about a derived criterion, and checkpoint 3 has no stellar mass.
2. **Body:** the two-dimensional component above with q = 0.4, c = 3, in `pattern_density_contrast` in place of the
   cosine; **the drawn `bar_contrast` stays the amplitude** (a measured galaxy-to-galaxy scatter of A₂^max) and
   fixes the body's normalisation so that its A₂ maximum equals it; the light share becomes the disclosed check
   against 0.10. Profile: one, chosen now (flat or exponential by the bulge needs checkpoint 4).
3. **Gas inside the bar's reach:** keep D216's blend with the body in the bar's place for this phase, the lanes a
   synthetic template that redistributes the ring's gas (conserving, on `texture_seed` only if something is
   drawn); the steady shocked branch in the bar's frame is not built unless you rule it.
4. **Arms:** the m = 2 mode's phase tied to the bar's end inside 1.5 a (the reading's P-tied-2) only if you rule
   it; no driven arm amplitude is invented (none is sourced); #138 is re-read at the close on what is built.

## Questions
1. **Presence:** which criterion, in final wording, given no scatter is read? Is "barred almost everywhere, no mass
   dependence, wrong for NGC 4414" a finding to record with the templates pinned, or a reason to rule differently
   (Erwin's frequency as a draw; a two-parameter form; nothing derived and the bar pinned or always present)?
   What exactly is a pin here (a template field that overrides a derived presence), and what does an unbarred
   galaxy publish — NaN for which fields — and what do rows 15–17 and the arm law's saturation do then?
2. **Body:** the form (the 2-D component with the ring's share taken out, or another); q, c and the profile; which
   of the light share and the A₂ maximum is the input and which the check, and what the gate's "m = 2 amplitude
   against the sourced value" then asserts; what Σ the share is of at checkpoint 3; "old stars" as built today
   (the stellar pattern field places stars older than the young-star cut; the young follow `sfr_modulation`).
3. **The saturation and the taper** (D215: s(R) = min(1, (1 − b(R))/Σ Ã_m), b = B·taper; the arms' weight
   1 − taper): what b(R) and the arm weight become when the bar is a body with its own radial run.
4. **Gas and the bar** (D216 item 8): the blend kept with the body; the lanes as the only gas structure inside the
   bar with the rest depleted (by what sourced amount, given B4's dispute); or the certified shocked branch in the
   bar's frame. What does "the gas response feels the bar's potential" become?
5. **Lanes:** the template's curve, extent, side and strength dependence in final wording (reader B's L-arc,
   L-straight, L-fit, L-orbit), what is drawn and from which statistic, and what stays unsourced as a debt (width,
   compression). Is the lane a property of the gas field, the dust placement, or both?
6. **Arms next to the bar:** is the m = 2 phase tied to the bar's ends (and #139 re-ruled), and is any bar-driven
   two-armed amplitude built in P3? If not, what does #138's re-read at the close stand on?
7. **The bar's length** against the reading: left to #80, or re-read here?
8. **What is the owner's?** `ngc_4414` losing its bar changes that template's picture and its five disclosed
   checks' inputs (no third fit is allowed); the default galaxy stays barred.

## The ranges you may read (at most these five)
1. `docs/READING_BAR.md` lines 224–288 — Part A's "what a model could adopt" and its conflicts.
2. `docs/READING_BAR.md` lines 554–625 — Part B's "what a model could adopt" and its conflicts.
3. `docs/BUILD_III.md` lines 393–416 — Phase P3's text.
4. `model/galaxy/stages/pattern.py` lines 207–250 and 556–640 — the bar's taper and angle, the mode law's
   saturation, and the stellar pattern as composed today.
5. `model/galaxy/stages/gas_pattern.py` lines 1–60 and 191–200 — the gas's law and its blend with the bar.
