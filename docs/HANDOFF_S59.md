# HANDOFF_S59 — a conditional gate before Phase P4's build: pitch along an arm, and what a template may pin

**For Fable, one short turn (BUILD_III §3c, §3d: "a source contradicts what this plan assumed"). Read this file and
at most the five ranges named at the end. Run nothing, explore nothing, write nothing. Answer in at most 80 lines:
the ruling in final wording, what it predicts (B4), the gate the build must meet, what is forbidden, and what
part, if any, is the owner's.** Written by the Opus lead of S59, 2026-10-05. Nothing is built; the repository holds
only the reading (`docs/READING_ARM_SEGMENTS.md`, one blind reader). S58 is merged (D217, as you ruled it).

## The plan's text for P4 (BUILD_III §5), whole
"Segments of seeded length and pitch change from the measured distributions (Honig & Reid 2015; Díaz-García et al.
2019), continuous in phase: synthetic. The Milky Way's pins — arm segments and kinks from the maser fits (Reid et
al. 2019), the bar's angle — and NGC 4414's (unbarred, flocculent). **Gate:** the pinned arms pass through the
measured loci; a galaxy without pins is unchanged."

## What the model's arms are today (D215–D217)
The stellar field is body + Σ_m A_m(R) cos(mχ − θ_m), m = 2…6, **χ = φ − ln R · cot p with one pitch p for the whole
disc** (`pitch_angle`: a law's mean from the shear plus a draw of 6° on `pattern_seed`; 13.54° and 14.33° on the
two templates). The amplitudes are the local swing window's (the Milky Way template is four-to-six-armed outside
the bar: 0.007 / 0.147 / 0.230 / 0.286 / 0.330 of the power in m = 2…6, #138, with the owner); θ₃…θ₆ are uniform
draws on `texture_seed`, θ₂ = 0 when barred. What reads the pitch: the winding χ; the bar's angle ln(a)·cot p; the
lanes' leading side; **the gas law's two numbers, ε = a/(κR sin p) and f_m = m A_m/(X sin p)** (so a lower pitch
forces harder: ×2.7 at 5°, ×5.0 at 2.7°, the regime of #142).

## What was read (`docs/READING_ARM_SEGMENTS.md`)

| Topic | As read |
|---|---|
| Segments | Honig & Reid 2015 fit **each arm on its own** as log-spiral segments joined at kinks: 38 segments in 4 galaxies. The reader's arithmetic on the 38 printed rows (the paper prints "∼5 kpc"): azimuthal extent median 60° (quartiles 50°–80°, range 20°–180°); arc length median 5.9 kpc; segment pitch mean 15.0°, sd 9.9° pooled, **3 of 38 reversed**; change at a join signed mean −0.5°, rms 14.4°, median \|Δψ\| 9.7°; 12 of 15 successive changes reverse sign (independent draws about a mean predict 2/3, a random walk 1/2). "No systematic trend with galactocentric distance". Positions at joins not imposed continuous (they meet to about an arm's width). |
| Within a galaxy | S⁴G (391 galaxies): sd of \|pitch\| among a galaxy's segments 9.5° ± 0.3°; 3–4 segments per galaxy typical. Along the two main arms the pitch varies by > 20 % in 2/3 of 50 galaxies; falls outward in 64 % (against "no trend" above). |
| Arm to arm | whole-arm fits differ by 0.6°, 1.1°, 5.1° in three two-armed galaxies; 2.6° median for the longest arcs (14.5° for all arcs); one hierarchical fit gives σ = 11.0° ± 0.9° between a galaxy's arms (absorbs along-arm variation). **No source says kinks of different arms share a radius**; M 51's two arms corotate at different radii. |
| Milky Way | Reid et al. 2019 Table 2 (read twice, digit for digit): seven separately fitted segments, ln(R/R_kink) = −(β − β_kink) tan ψ, β from the Sun in the direction of rotation, R₀ = 8.15 kpc: Norma (β 5→54°, kink 18°, 4.46 kpc, ψ −1.0° / 19.5°), Sct-Cen (0→104, 23, 4.91, 14.1 / 12.1), Sgr-Car (2→97, 24, 6.04, 17.1 / 1.0), Local (−8→34, 9, 8.26, 11.4), Perseus (−23→115, 40, 8.87, 10.3 / 8.7), Outer (−16→71, 18, 12.24, 3.0 / 9.4), 3-kpc (15→18, 3.52, −4.2); widths 0.14–0.65 kpc. Four major arms (Norma–Outer, Sct-Cen, Sgr-Car, Perseus), the Local arm "an isolated segment", the data covering about a third of the disc. **Disputed since:** Perseus 0.2–0.4 kpc further out (2026); two inner arms that bifurcate, with irregular outer segments (Xu et al. 2023). The long bar 28°–33° from the Sun–centre line, half-length 5.0 ± 0.2 kpc. |
| NGC 4414 | unbarred, arm class F; **no locus is tabulated anywhere**: five 3.6 µm segments with a pitch and a radial range each (30.5°, 34.2°, 28.1°, 44.0°, 7.6° over 19″–87″; mean 28.9° ± 6.0°, one winding sense), a K′ ring at 20″ and two outer pieces "to north and south". |

## The probe (hand arithmetic on the table above; the repository unchanged)
- **The measured arms are not one winding.** At one azimuth the four major arms' radii (β = 24°: 4.89, 6.04, 9.33,
  12.03 kpc) need a common four-armed winding of pitch 7.6°, 15.5°, 9.2° between neighbours, where the arms' own
  pitches there are 12.1°, 17.1°, 10.3°, 9.4° (at β = 40°: 9.6°, 13.9°, 9.3° against 12.1°, 1.0°, 10.3°, 9.4°).
  Arms that overlap in radius are not 90° apart: Norma and Sct-Cen 34°–42° at 4.0–4.3 kpc; Local and Perseus
  57°–60° at 8.0–8.3 kpc; Perseus and Outer 84° at 10.6 kpc.
- **A sum of modes with drawn phases has no "arms" to pass through loci.** Outside the bar the template's crests
  are those of m = 3…6 together; a pin could set the common winding and each mode's phase and nothing else.
- **Segments in the model's variables:** a 60° segment at 13.5° spans d ln R = 0.25 (a factor 1.29 in radius), so
  five or six segments between 3 and 12 kpc — but as kinks of a common winding they would sit on common rings for
  every arm, which no source describes.
- **A segment's pitch drawn about the mean with the measured sd of 10°** is reversed 9 % of the time and under
  2.7° another 9 % (mean 13.5°); above 30° 5 %. If the local pitch entered the gas law, a tenth of the segments
  would sit in #142's regime and the reversed ones would cross sin p = 0.

## The lead's draft (for your judgement; nothing here is ruled)
1. **Segments are a property of the common winding, geometry only.** Φ(R) = ∫ cot p(R′) dR′/R′ with p piecewise
   constant on radial segments; each segment's extent d ln R = Δβ · tan p with Δβ drawn (median 60°, the reader's
   log-normal), its pitch the galaxy's `pitch_angle` plus an independent residual; continuous in phase by
   construction; synthetic on `texture_seed`, standing in for per-arm kinks, its statistic the reader's arithmetic
   on Honig & Reid's rows (a declared derivation, with S⁴G's 9.5° beside it). **The gas law's ε and f keep the
   galaxy's `pitch_angle`** (a law reads a law; the layer redistributes and changes no forcing), and so do the
   bar's angle and the lanes. Layer off: one pitch, as today, bit for bit.
2. **The residual's width and its tails** need your word: 10° about a mean of 13.5° reverses a segment in eleven;
   the sources do show reversed and near-zero segments (3 of 38; the Milky Way's Norma −1.0°, Sagittarius 1.0°).
3. **Pins, the Milky Way:** what a common winding can hold — the bar's angle to the Sun–centre line (which first
   needs the Sun's azimuth as a published number), and nothing of the arms' loci. The seven segments become a
   **disclosed check**: the distance of each measured locus from the nearest crest of the composed field, read and
   recorded (predicted: a miss, by the arithmetic above), under #138's conflict. A representation that could carry
   them — ridges per arm, replacing the mode sum in a pinned template — is not this phase's and is the owner's.
4. **Pins, NGC 4414:** unbarred (done, D217); its mean segment pitch, 28.9°, as a pinned `pitch_angle` replacing
   the draw (a measured fact, not a fit — but it moves layer-off fields of that template: the gas law's forcing
   halves), or left as a disclosed check against the drawn 14.3°.

## Questions
1. **What is a "segment" in a model whose arms share one winding?** Draft 1 (a piecewise pitch of the common
   winding, kinks on common rings); or per-mode windings (each m its own Φ_m(R): then modes shear against each
   other and the composed crests are not continuous arms); or nothing built (the sources describe per-arm
   structure the representation cannot hold: a debt). The extent's and the residual's distributions in final
   wording, and what "continuous in phase" asserts.
2. **Does a segment's pitch enter the physics** (ε, f, the bar's angle, the lanes' side), or the geometry only?
   If the physics: the tails (reversed, near zero) and #142. If geometry only: is a law (the gas response) then
   forced by a winding that is not the one drawn on the sky, and is that acceptable?
3. **The tails:** truncate (where, on what source), reflect, or draw as measured?
4. **The Milky Way's pins:** which of the seven segments, the four-arm reading, the bar's angle and the Sun's
   azimuth enter as pins; what "the pinned arms pass through the measured loci" becomes when the arms are a sum of
   modes (a check with what statistic and tolerance; or the pin deferred); and whether pinning Reid et al. 2019
   is right at all given the later disputes.
5. **NGC 4414's pins:** the pitch (28.9° against the drawn 14.3°) as a pin or a check; anything else.
6. **A galaxy without pins is unchanged** — bit for bit layer off, and layer on only by the segments' draw?
7. **What is the owner's?** The Milky Way template cannot show its measured arms in this representation; #138 is
   already with them. Does the build wait, proceed on the segments alone, or stop here with a finding?

## The ranges you may read (at most these five)
1. `docs/READING_ARM_SEGMENTS.md` lines 217–269 — "what a model could adopt".
2. `docs/READING_ARM_SEGMENTS.md` lines 61–96 — the Milky Way's table, its form and conventions, the disputes.
3. `docs/BUILD_III.md` lines 423–429 and 48–82 — Phase P4's text; the layer's principle and its five rules.
4. `model/galaxy/stages/pattern.py` lines 257–273 and 910–930 — the winding and the bar's angle; the composed field.
5. `model/galaxy/layer/arm_phases.py` lines 1–60 — the layer stage that realises the modes' phases.
