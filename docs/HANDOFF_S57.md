# HANDOFF_S57 — gate G2: is a steady shock the gas's response to arms set ring by ring, in which frame, and what is integrated

**For Fable, one short turn (BUILD_III §3b–§3c). Read this file and at most the five ranges named at the end. Run
nothing, explore nothing, write nothing. Answer in at most 80 lines: the ruling in final wording, what it predicts
(B4), what is forbidden, the gate the build must meet, and what part, if any, is the owner's.** Written by the Opus
lead of S57, 2026-10-04. Nothing is built; the repository is unchanged but for the reading.

## What was read (`docs/READING_GAS_SHOCK.md`; three readers, all blind to the repository)

| Part | Finding the ruling stands on |
|---|---|
| A, C (two independent readers) | **One system, three parameters per mode.** With w the gas's speed normal to the arm in units of κR sin i/m, s = Σ/Σ₀, η the phase (0 at the potential minimum): `(w − x/w) dw/dη = v − f sin η`, `dv/dη = s − 1`, `s w = −ν`; ν = m(Ω_p − Ω)/κ, x = (m a/(κ R sin i))², f = (Ω/κ)² m F/sin i. Shu, Milione & Roberts 1973 (read as page images), Gittins & Clarke 2004, Kim, Kim & Kim 2014 and Lee & Shu 2012 print the same system; `dv/dη = s − 1` is uniform potential vorticity. |
| A, C | **Sonic point** w = √x, regular only if v = f sin η there; isothermal **jump** w₁w₂ = x, v continuous; closed by a search on the sonic point's phase alone. **Checks:** Kim, Kim & Kim 2014 Table 1 (ν = −0.7071, x = 0.1450 or 0.1458, f = 0.3, 0.5, 1, 2: sonic point, shock front and jump to three figures) read identically by both readers; Sormani 2017's no-shock threshold (four digits); SMR's figures at 10, 11 and 14 kpc (labels exact, curves to ±5 %). |
| A | **Base-subsonic rings** (R sin i |Ω − Ω_p| < a, a band round corotation): smooth below a cusp forcing (3.7 % at SMR's 14 kpc), the cusp at the potential *maximum*, the peak broad and at the minimum, "not unlike the linear theory"; the search window for a shocked solution can be under π/1000. |
| A, C | **Exactly at corotation no source gives a nonlinear solution**; both readers reconstruct the linear limit σ₁/σ₀ = f cos η/(1 − ν² + x), which is the textbook WKB gas response. Reader C: at ν = 0 the steady state is not unique without a closure — (a) uniform potential vorticity, the ν → 0 member of the same family, `x d²ln s/dη² = s − 1 − f cos η`; (b) hydrostatic, s ∝ exp((f/x) cos η), larger by (1 + x)/x. |
| A, C | **No source integrates a sum of modes.** A steady one-dimensional problem exists only if every mode shares one pattern speed and one pitch. |
| B | For swing-amplified arms, simulations find **Ω_p(R) ≈ Ω(R)** (Grand 2012, Baba 2013, Wada 2011: "every single position in the arm can be regarded as the co-rotation point"): no flow through the arm, no galactic shock, gas entering the minimum from both sides, no offset trend. Mode decompositions of the same discs find a few rigid modes each peaking at its own corotation. PHANGS (24 galaxies): 17 % show the single-wave offset trend, 42 % offsets without a trend, 42 % none. |

Not read: Roberts 1969's and SMR's remaining pages, Binney & Tremaine, Shu 2016. No source gives F from a stellar
contrast (both readers compose it from the WKB Poisson relation Φ₁ = −2πGΣ₁/|k|), a finite-thickness correction,
or a measured gas contrast in co-rotating arms.

## What a ring of the model is, in those variables (probe, repository unchanged; Milky Way template, default seeds)

All modes share the pitch p, so the composed potential is a function of χ = φ − ln R cot p alone and mode m's
phase is η = mχ − θ_m. With the published fields: **f_m = m A_m(R)/(X(R) sin p)**, X = κ²R/(2πGΣ) the arm-number
law's own variable (checkpoint 1's total disc Σ), A_m the published mode amplitudes (taper and saturation in them);
x_m = m²ε², **ε = a/(κ R sin p)**, a = `GAS_DISPERSION` = 6 km/s. *Anchors:* X(7.99 kpc) = 7.93 and Γ = 1.10, D215's
hand values; f's form derived by the lead and, independently, by reader C (F = 2πGΣ₁/(RΩ²)); the corotating
equation derived by the lead and by reader C before either saw the other's.

| R kpc | Ω, κ km/s/kpc | X | ε | f_m, m = 2…6 | Σ_m f_m/(1+x_m) | M⊥ at Ω_p = 45.5 (the bar's) / 26 | **ν = 0, closure (a):** crest / trough / ratio of means in S56's mask | S56's ridge |
|---|---|---|---|---|---|---|---|---|
| 4.01 | 59.9, 91.9 | 4.26 | 0.069 | .07 .18 .23 .29 .31 | 0.98 | +2.3 / +5.3 | 1.91 / 0.37 / 1.57 | 1.70 / 0.66 |
| 5.96 | 41.9, 59.8 | 5.66 | 0.072 | .08 .37 .49 .62 .72 | 2.04 | −0.8 / +3.7 | 3.02 / 0.007 / 2.69 | 2.67 / 0.57 |
| 7.99 | 30.9, 41.4 | 7.93 | 0.077 | 0 .25 .46 .57 .69 | 1.72 | −4.5 / +1.5 | 2.79 / 0.018 / 2.56 | 3.06 / 0.53 |
| 10.01 | 23.9, 30.9 | 12.0 | 0.083 | 0 0 .23 .45 .56 | 1.05 | −8.4 / −0.8 | 2.09 / 0.18 / 2.04 | 3.07 / 0.53 |
| 10.99 | 21.4, 27.4 | 15.1 | 0.085 | 0 0 0 .32 .56 | 0.72 | −10.3 / −2.0 | 1.77 / 0.38 / 1.89 | 3.07 / 0.53 |
| 12.04 | 19.2, 24.4 | 19.6 | 0.087 | 0 0 0 0 .25 | 0.19 | −12.3 / −3.2 | 1.20 / 0.81 / 1.28 | 2.29 / 0.71 |

M⊥ = R(Ω − Ω_p) sin p / a, the base flow's Mach number normal to the arm. The last column but one solves
`ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(mχ − θ_m)` on 1440 periodic cells by Newton (5–8 steps here; 34 at worst, on
`ngc_4414` at 4 kpc where Σf = 2.1 and the trough is 0.001); the ring mean is 1 to 1e-15 with no division.

- **The response is linear in the forcing** up to the ring's full amplitude: crest − 1 = 0.084, 0.168, 0.428, 0.873,
  1.79 at 0.05, 0.1, 0.25, 0.5 and 1 times the R₀ forcing. Ruling 8's exponent 1 is what the physics gives.
- **The ratio of means comes out near the measured one without being put in**: 2.56 at R₀ and 2.0–2.8 over
  6–10 kpc, against PHANGS's 2.73 (16th–84th percentiles 1.37–5.79); it fades to 1 with the forcing by itself.
- **The gas between the arms is nearly emptied where Σf > 1** (trough 0.007–0.02 at 6–8 kpc; `ngc_4414` 0.001 at
  4–5 kpc). The razor-thin WKB potential overstates high m; with an illustrative factor 1/(1 + kh), h = 0.3 kpc
  (no source, `[recall — NOT READ]`), R₀ reads 2.00 / 0.28 / 1.68; with a = 10 km/s, 2.55 / 0.13 / 2.10.
- **The ridge is as wide as the stellar arm**: one mode's response has FWHM 0.46–0.50 of its period (several
  modes: 0.23–0.48 of the dominant one's), against the measured 0.17 (`GAS_ARM_WIDTH`, #129). No offset, by symmetry.
- **One rigid frame cannot hold the model's modes.** A mode lies between its Lindblad resonances only where
  |Ω − Ω_p| < κ/m: for m = 6 on a flat curve, within ±24 % of corotation; the model's m = 4–6 span 3–12 kpc. At
  Ω_p = 26 the band |M⊥| < 1 is 8.4–10.2 kpc, and inside 6 kpc ν₆ < −1.6 (outside the inner Lindblad resonance,
  where the linear response changes sign). The model publishes no spiral pattern speed; the bar's is P3's.

## The lead's draft (for your judgement; nothing here is ruled)

1. **Frame: Ω_p(R) = Ω(R) for every arm mode.** The plan's "corotation at the mode's radius", for amplitudes set
   ring by ring, is this; it is what simulations of swing-amplified arms find; and it is the only frame in which a
   ring's several modes are steady together. So ν = 0 on every ring: no flow through the arm, **no sonic point, no
   jump — the arms' gas does not shock**, and the plan's "steady shock" is replaced by the same equations' ν → 0
   member under closure (a). Closure (b) is refused: it drops the Coriolis term the family carries.
2. **The law:** `ε²(R) d²ln s/dχ² = s − 1 − Σ_m f_m(R) cos(mχ − θ_m)`, periodic in χ, with f_m and ε as above; it is
   the Euler–Lagrange equation of a strictly convex functional, so the solution exists, is unique and positive,
   and Newton on fixed cells with a fixed step count reaches it (A1); its ring mean is 1 identically. The linear
   limit f_m/(1 + m²ε²) is the textbook response at corotation. No constant is added.
3. **The instrument (B1) is the family's solver, not only the member the model uses:** builder A writes the
   general (ν, x, f) solver — smooth branch as a boundary-value problem, shocked branch by the regularised
   variables and a bisection on the sonic point's phase — and it reproduces Kim, Kim & Kim's Table 1 and Sormani's
   threshold before the model calls its ν = 0 member; a hand-derived test (the linear limit, and uniform potential
   vorticity checked from the solution) is independent of the module. The shocked branch then waits, certified,
   for P3's bar, which has a real pattern speed.
4. **Consequences:** the offset is zero and D210's ruling 3 stands, now derived; `GAS_ARM_WIDTH`,
   `GAS_ARM_MASK_WIDTH` and the two contrast constants stop being inputs — the mask and PHANGS's ratio become a
   disclosed check (row 38), the width a recorded miss; #140 discharged; #129, #131 re-ruled as checks; #81's first
   half closed by "the arms' pattern speed is Ω(R)", its cut (0.1 Gyr) becoming the arm's lifetime (Part B: 100–160
   Myr in Grand 2012 and Baba 2013), not a crossing time.

## Questions

1. **Is a steady shock the right gas response at all** for ring-by-ring swing-amplified arms, and **in which
   frame**? Draft 1, or: per-mode rigid speeds (no steady solution exists for several modes on a ring); one global
   speed (which? none is sourced for this model; the Lindblad bullet above); or a small non-zero ν.
2. **At ν = 0, which closure** — (a) uniform potential vorticity, (b) hydrostatic, or another — and is a *steady*
   state admissible for arms that live ~100 Myr (1/κ is 24 Myr at R₀; the sound crossing of an arm is longer)?
3. **The equations in final wording**: the potential from which Σ (checkpoint 1's total, as X uses, or another —
   checkpoint 3 has no stellar/gas split and no scale height); razor-thin as a declared approximation with a debt,
   or a thickness factor (from what source and what height); a = `GAS_DISPERSION` (6 km/s) or another published
   number. The near-empty interarm at 6–8 kpc: a finding to record, or a sign the forcing is overstated?
4. **The sonic point and the fallback**: under draft 1 there is neither. If you rule a frame with flow: the
   treatment (regularised variables, the search), the fallback where no shock forms (the plan declares the linear
   response; the smooth branch is exact and available), and what a ring does when its search fails (A1).
5. **The instrument**: is draft 3 right — build and certify the shocked branch in S57 although no arm uses it —
   or is it deferred to P3 and S57's instrument only the smooth solver (checked how, with no published profile at
   ν = 0)? Is certifying on Kim, Kim & Kim's restatement enough, SMR's own figures being read to ±5 %?
6. **The bar's reach**: today g = 1 + w_arm a (v − 1) + B·taper·cos 2(φ − φ_bar). With s in place of the ridge,
   s + b cos 2(…) is negative where the trough is under b (5 kpc: trough 0.08, b = 0.125). Additive with what
   guarantee, multiplicative over its ring mean, or the bar's term inside the forcing (it rotates at Ω_b: P3's)?
7. **Evaluable at a point** (layer rule 5) and the cost (#140: three times the census's time): solved on the grid's
   rings on fixed cells and interpolated — linear in R between rings keeps the mean and the sign — or re-solved at
   each object's radius? What the gate holds: ring means to 1e-12 on the cells, min ≥ 0, expected totals.
8. **Carried from S56.** (i) The ranked ridge's published field passes its exact bound by 2.5e-3 through the
   sampled-mean division: does it retire with the ridge, and may the new field be divided by a sampled mean at
   all? (ii) `cloud_count_total` and `bright_star_count_1e3` differ by one unit in the last place layer on and off
   (sums of placement weights that average to 1 only to rounding); I1 says bit-identical: amend I1's wording, or
   require the sums made exact? (iii) The fade's exponent: is "1, measured" (above) its close? (iv) What replaces
   the ratio-of-means amplitude: nothing (s is the field), with `gas_arm_contrast` kept as the check's target?
9. **The checks' honesty (for G3)**: how row 38 is defined before its number is read (the probe has printed 2.56 at
   R₀ in S56's mask: disclosed, D113); what the width's miss is recorded against; what must not be tuned.
10. **What is the owner's?** Their item 3 ordered "level A, the steady 1-D gas shock per ring". If the arms do not
    shock, is that a plan change they must approve before the build, or a finding told at the close?

## The ranges you may read (at most these five)

1. `docs/READING_GAS_SHOCK.md` lines 226–303 — Part A: constructing the solution, the checkable cases, scalings
   (the base-subsonic band and exact corotation), several modes.
2. `docs/READING_GAS_SHOCK.md` lines 470–603 — Part C: the corotating case in the sources, and the two closures.
3. `docs/READING_GAS_SHOCK.md` lines 116–146 — Part B: the five frames a model could adopt, with their evidence.
4. `model/galaxy/stages/gas_pattern.py` lines 1–112 — what the gas pattern is today (the form, the bar's term,
   the sampled-mean division).
5. `docs/BUILD_III.md` lines 363–381 and `docs/DECISIONS.md` lines 9302–9312 — Phase P2's text; what S56 carried.
