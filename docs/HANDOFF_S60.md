# HANDOFF_S60 — a conditional gate before Phase P5's build: the arms as a census of pieces

**For Fable, one short turn (BUILD_III §3c, §3d). Read this file and at most the five ranges named at the end. Run
nothing, explore nothing, write nothing. Answer in at most 80 lines: the ruling in final wording, what it predicts
(B4), the gate the build must meet, what is forbidden, and what part, if any, is the owner's.** Written by the Opus
lead of S60, 2026-10-05. Nothing is built; the repository holds the owner's ruling (D219), the amended plan and two
blind readings (`docs/READING_ARM_PIECES.md`). S59 is merged (D218, as you ruled it).

## What the owner ruled, and why (D219)
The frames were set beside the two goal pictures: far from both. The Milky Way template is a dim disc with thin
nearly circular ripples (S59's segments on common rings, on an outlier seed) where the goal has a few bright
unequal arms; `ngc_4414` has two or three smooth sweeps where the goal is flocculent. Offered fewer and stronger
modes (A), a ridge per arm (B), or arm pieces as a census with the arm-number law as each ring's budget (C), the
owner said: **"Take C, don't reorder the sessions."** Phase P5 is inserted at S60; its text (your range 1) orders
the direction and leaves the rest to this gate.

## What the model's arms are today (D215–D218)
Stars: 1 + (1 − taper)·Σ_m A_m(R) cos(mχ − θ_m) + the bar's body, m = 2…6, χ = φ − Φ(R), Φ the common winding in
seeded segments (S59), θ_m drawn on `texture_seed` (θ₂ = 0 when barred). A_m(R) is physics (P1's law: the local
swing window's split of A², capped and saturated), published layer on and off. **With the layer off no arm is
placed at all** (composed fields at their neutral value). Gas: per ring, ε² d²ln s/dχ² = s − 1 − F(χ), F = Σ_m f_m
cos(mχ − θ_m), f_m = m A_m/(X sin p), ε = a/(κ R sin p); the solver takes F on 1440 cells (any periodic function).
A point between rings reads each ring's profile at its own χ (the common winding carries it); the young stars'
reader, the clouds and the dust all read the gas pattern that way.

## What was read (`docs/READING_ARM_PIECES.md`; the lead's summary is its first 25 lines)

| Topic | As read |
|---|---|
| Width, old stars | FWHM 0.53 ± 0.04 scale lengths = 0.12 r25 at mid-arm (3.6 µm, 29 galaxies, 0.24–1.18 per galaxy); grows linearly with radius, zero point 19–34 % of the mid-arm width; radial FWHM 0.19 r or 0.30 r by the disc subtraction; 20°–40° in azimuth in K. These disagree by up to two. Profile near-Gaussian (Sérsic 0.6–0.7); asymmetry small, its sign disputed. |
| Width, young tracers | Milky Way masers σ = 0.34 kpc at 8.15 kpc, +36 pc/kpc; HII σ 0.055 R median; FUV radial FWHM 0.14 r — half the stellar width or less. |
| Amplitude | Arm over interarm at 3.6 µm, disc average: 1.14 ± 0.44 mag (grand design), 0.81 ± 0.28 (multi-armed), 0.75 ± 0.35 (flocculent; 0.44 at one radius). Light in arms 0.21 (0.08–0.46). The arms' share is zero at the centre and peaks at 1–2 scale lengths; ends are tapered, not sharp; dips in 24 % of arms; the outer end usually at 0.5–0.7 r25. |
| Number and length | Arms of ≥ 90°: 2.8 (grand design), 3.5 (multi-armed), plus 1.4 shorter features; whole-arm length 273° ± 143° and 244° ± 131°; pieces 5–8 kpc between kinks; bends in 35 % of arms. **Flocculent: no number and no length distribution of pieces is measured**; a weak two-armed K′ pattern in about 15 %; NGC 4414's five segments span 37°–105° each (pitches 30.5°, 34.2°, 28.1°, 44.0°, 7.6°). |
| Classes | 50 / 32 / 18 % flocculent / multi-armed / grand design (S⁴G); 42 / 18 / 32 % + 8 % smooth (PHANGS CO); 75 % of grand designs barred; flocculent goes with low mass and late type. No deterministic predictor. |
| Inequality | Between a galaxy's arms: pitch 16–27 % of the mean, width 10–37 %; no distribution of amplitude or length ratios. **Not measured:** branch radii or frequency, the share of arms starting at a bar's end, a taper length. |
| Thickness | Midplane force of a wave of wavenumber k from an exponential stellar layer of scale height h: **× 1/(1 + k h), exact** (Kim & Ostriker 2007 eq. 4), and it is the factor the gas feels from the stars (their eq. 8). sech²(z/z0): exact form printed (Wang et al. 2010 eq. 35); Cox & Gómez's fit (1 + 0.3 k z0)/(1 + k z0 + 0.3 (k z0)²) is within 1.4 % of it. Which profile a fitted scale height stands for moves the factor 0.39–0.57 at k h = 1. h_R/h_z = 7.3 ± 2.2 (Kregel et al. 2002). |
| Not established | No source converts a stellar arm's amplitude to a forcing with thickness; none gives the gas's response to a narrow arm, or a contrast law for arms that corotate (gas converges from both sides, no shock). |

## The probe (the lead's; the model's own rings and solver, nothing changed in the repository)
Ridges put in place of the five modes at each ring's budget (variance = ½ Σ A_m², rms 0.284 on the Milky Way
template, 0.251 on `ngc_4414`), 2 or 4 equal Gaussian ridges, perpendicular FWHM 0.4 / 0.8 / 1.5 kpc; forcing by
the model's own rule per Fourier term, F̂_m = |m| ĉ_m /(X sin p), without and with × 1/(1 + m h/(R sin p)).
- **The solver takes ridges as it is**: every case converged in 4–8 Newton steps, both templates, 0.5–12 kpc.
- **The budget is spendable**: at FWHM 1.5 kpc (≈ 0.53 scale lengths on the Milky Way) two ridges of amplitude
  0.80–0.87 leave the stellar minimum at 0.67–0.81 (5–10 kpc): crest over trough about 2.1, 0.8 mag, against the
  grand designs' 1.14 ± 0.44 and the multi-armed 0.81 ± 0.28.
- **Thickness**, today's modes × 1/(1 + k h) with the model's own `thin_disc_scale_height`: Milky Way (356 pc) Σf at
  8 kpc 1.98 → 1.04, the gas minimum 0.017 → 0.32, top tenth over lower half 4.1 → 2.2; `ngc_4414` (954 pc) the
  inner minimum 1e-14 → 0.83 and the ratio 3.5–8 → 1.2–1.4.
- With two ridges of 1.5 kpc and the factor: gas maximum 1.5–1.6, minimum 0.56–0.81, top tenth over lower half
  1.8–2.1 at 3–8 kpc (Milky Way); without the factor 1.9–2.0, 0.15–0.69 and 2.5–4.6.
- **Two findings.** `thin_disc_scale_height` is checkpoint 4's and the gas pattern is checkpoint 3's (A1). And
  **`ngc_4414`'s is 954 pc on a scale length of 1.68 kpc — a ratio of 1.8 against the measured 7.3 ± 2.2** (the
  Milky Way template: 2.44 / 0.356 = 6.9).
- **A factor's side effect:** F̂_m × T = |m| ĉ_m /(X (sin p + |m| h/R)) is regular through sin p = 0 — the local-pitch
  form #151 asked for.

## The lead's draft (for your judgement; nothing here is ruled)
1. **A piece** is a ridge on its own logarithmic locus: start (R₀, φ₀), pitch p_j, azimuthal extent Δβ_j, so it ends
   at R₀ exp(Δβ_j |tan p_j|). Across it a Gaussian in the perpendicular distance (the named alternative: Sérsic
   0.65), FWHM 0.53 scale lengths at the galaxy's two-scale-length radius, linear in R with a zero point of 27 %.
   Along it flat, tapered to zero at each end over one width (a declared placeholder: no taper length is measured).
2. **An arm is a chain of pieces** joined end to start, each piece's extent and pitch S59's draws (median 60°,
   σ_ln 0.35; pitch p (1 + 0.56 z)), now per arm as the sources measure them. Chain length: 273° ± 143° or
   244° ± 131°. Kinks are then each arm's own (#150 discharged).
3. **Class, derived where not pinned, no draw:** barred → two chains from the bar's ends (#149's missing
   bar-driven arms, as geometry; amplitude from the budget), plus chains born further out while the arm-number
   law's mean number n(R) = Σ m w_m / Σ w_m exceeds the chains crossing the ring; unbarred → chains by n(R)
   alone. **Flocculent by pin only** (`arm_class` on `ngc_4414`): short single pieces (its measured 37°–105°),
   their number set so that n(R) of them cross each ring — the local swing law is the physics of a flocculent
   disc, and no source gives the count.
4. **The budget:** the pieces' common amplitude B(R) is set so that the *expected* variance of a ring's contrast
   over the census's draws equals the law's ½ Σ A_m(R)² (taper and saturation in); the realised power scatters
   and is measured. Exactly per ring is the alternative, and it undoes any taper (a piece's end is renormalised
   up) and spikes where one piece alone crosses a ring. Each ring keeps its mean exactly; where the trough would
   pass zero the ring's amplitude is cut to the bound, as P1's saturation does.
5. **The gas:** per ring, F from the ring's own stellar pieces, Fourier term by term, each piece with its own
   |sin p_j| and the thickness factor 1/(1 + k h) (exponential: the exact case; the sech² fit the alternative),
   **h = the checkpoint-1 scale length / 7.3** (Kregel's ratio, so A1 holds and `ngc_4414`'s anomalous height
   does not enter; the anomaly a debt). ε keeps the disc's pitch. #142 and #151 are then re-read.
6. **At a point:** the stars are the pieces' sum, exact anywhere. The gas is solved on rings; a ring's profile is
   carried to a point between rings **along the pieces' own loci** (a periodic piecewise-linear map of azimuth
   anchored where each crossing piece stands on the ring and at the point's radius), its error measured against a
   direct solve at mid-gap radii and pinned, as S59's 0.29 % was.
7. **Retired:** the modes' drawn phases; the common winding and its `arm_segment` table (a table `arm_piece`
   takes its place: chain, order, start, pitch, extent, pinned or drawn). **Kept:** `arm_mode_amplitude_m` as the
   budget (physics, published on and off); the bar's body, lanes and angle; layer off bit for bit.
8. **The Milky Way's pins:** Reid et al. 2019's four major arms and the Local arm as chains of their fitted
   pieces over the measured β ranges, each continued beyond its range by drawn pieces (flagged); equal weights
   (no amplitude ratio is measured); the 3 kpc arm left out (inside the bar's taper). `sun_bar_angle` gives the frame.

## Questions
1. **A piece and a chain** (draft 1–2): the profile, the width's law among the three that disagree, the taper,
   whether S59's per-segment draws may serve per arm unchanged, the chain's length and where it starts.
2. **The class of an unpinned galaxy, and a flocculent disc's count** (draft 3): derived from the bar and n(R), a
   draw on the measured frequencies, or pin only? Is "n(R) pieces cross each ring" a fair use of the law?
3. **The budget** (draft 4): in expectation or exact per ring; the saturation; whether the split by m survives as
   a published check of the composed field.
4. **The forcing** (draft 5): the factor's form; which thickness (the ratio on checkpoint 1, or the model's own
   height moved or awaited); each piece's pitch in F and the disc's in ε; what becomes of #142's "floor" question.
5. **The gas between rings** (draft 6): the carried profile and its measured error, or something else.
6. **What retires and what the layer-off galaxy is** (draft 7); the readers that must follow (young stars,
   clouds, dust, the viewer's grid fields).
7. **The Milky Way's pins** (draft 8): which rows, the continuation, the weights; and what P4's gate sentence
   becomes when the pinned pieces lie on the loci by construction.
8. **Scope:** one session, or the model this session and the readers' and viewer's side the next (the plan would
   move one more on — the owner's)?

## The ranges you may read (at most these five)
1. `docs/BUILD_III.md` — "Phase P5" (search the heading; about 40 lines) and §1c, the layer's five rules (lines 68–82).
2. `docs/READING_ARM_PIECES.md` lines 365–412 — Part A's "what a model could adopt".
3. `docs/READING_ARM_PIECES.md` lines 707–742 — Part B's.
4. `model/galaxy/stages/gas_pattern.py` lines 552–604 — the forcing, ε and the solved rings.
5. `docs/DECISIONS.md` — D219 (the last 60 lines of the file).
