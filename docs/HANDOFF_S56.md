# HANDOFF_S56 (third turn) — the window was probed and built on X_m/2: the lead's error, and what the law is

**For Fable, one short turn (BUILD_III §3c, §3d). Read this file and at most the three ranges named at the end.
Run nothing, explore nothing, write nothing. Answer in at most 60 lines: the ruling in final wording, what it
predicts, what is forbidden, and whether any part is the owner's.** Written by the Opus lead of S56, 2026-10-04.

## What went wrong, and whose error it is

Your first ruling of this session was given a probe's numbers, and **the probe was wrong by a factor of two in the
swing parameter. The error is the lead's**: the probe, the handoff and the builder's brief all wrote
"X₂(R) = κ²R/(2πGΣ·2), m_lo = X₂/(Γ x_high), m_hi = X₂/(Γ x_low)". The window formula (S26's `swing_window`)
takes the variable x = 2/f_d, which is **m·X_m**, not X₂ (the function's own docstring says X_m = 2/(m f_d), and
its name `x2` and the field `swing_x`'s about call 2/f_d "X at m = 2", which is where the slip came from). So the
probe and the build apply the source's ranges — vigorous for 1 < X/Γ < 2, dead at 3 and at 0.5 — to **X_m/2**.
An independent Opus reviewer found it by re-deriving three rings from the published fields (the module's weights
equal "the window on X_m/2" to 9e-16 on all 400 rings; on X_m they differ by up to 1.0). No test could have: the
tests recompute with the module's formula, and every prediction you made was read off the same probe.

**What is unaffected.** Your formulas — the gain capped at one, the saturation, the phases on `texture_seed`, NaN
with the layer off, the ridge by rank, the fade on the forcing amplitude — are formulas on w_m and stand whatever
the window. They are built and green: the stellar field is byte-identical to S55 with one mode, the Fourier gate
holds to 4e-15, no cell is negative on 240 seeds, the ranked ridge agrees with a polynomial-root oracle to 3e-9
and with S51 at one mode to 1.4e-12, per-region determinism holds, layer-off 331 of 332 fields are S55's and the
rows have not moved. The reviewer also settled the census-against-field worry: over 44 `systems_seed`s the
census's Q over the light stage's is 0.999 ± 0.009 with the layer on and 1.001 ± 0.009 off — the default seed's
0.966 is half a standard deviation of one draw, not a loss.

## The law under four windows (both templates, production grid; gain = w / max(1, Σw); power shares m = 2…6)

| Window | Milky Way: mass-weighted power m = 2…6 | at 2 kpc | at 6 kpc | at 8 kpc | at 10 kpc | whole power to | last ring | `ngc_4414`: power m = 2…6 |
|---|---|---|---|---|---|---|---|---|
| **As built** (ranges on X_m/2: the error) | 0.40 / 0.32 / 0.17 / 0.07 / 0.04 | .50 .35 .15 0 0 | .38 .35 .20 .08 0 | .27 .27 .23 .14 .07 | .09 .24 .24 .24 .19 | 13.8 kpc | 14.8 | 0.59 / 0.30 / 0.07 / 0.02 / 0.02 |
| **W1. Ruling 3's words** (ranges on X_m, Σ the exponential disc's) | 0.08 / 0.21 / 0.24 / 0.25 / 0.22 | .12 .24 .24 .23 .17 | .03 .25 .25 .25 .23 | 0 .15 .28 .28 .28 | 0 0 .16 .40 .43 | 11.1 kpc | 12.3 | 0.19 / 0.24 / 0.24 / 0.19 / 0.14 |
| **W2. S26's Mestel form at each ring**, x = 2/f_d(R), f_d(R) = 1 − (v_halo/v)² | 0.20 / 0.25 / 0.24 / 0.19 / 0.14 | .02 .25 .25 .25 .24 | .29 .29 .23 .13 .05 | .32 .32 .22 .12 .03 | .31 .31 .22 .12 .04 | the grid's edge | none dies | 0.33 / 0.30 / 0.19 / 0.11 / 0.07 |
| **W3. S26's global window on every ring** (today's `swing_arm_min/max`) | 0.29 / 0.29 / 0.23 / 0.13 / 0.06 | the same on every ring | | | | the grid's edge | none dies | 0.43 / 0.36 / 0.18 / 0.04 / 0 |

Under W1 the Milky Way is a four-to-six-armed disc with almost no m = 2 (8 % of the power), its pattern whole to
11.1 kpc and gone at 12.3; the worst ring's Σ Ã_m + b is 0.795 at the default seed (saturation still 1). Under W2
the inner 2–3 kpc are many-armed (under the bar's taper, which hides most of it: the bar's half-length is 5.2 kpc)
and the disc beyond 4 kpc is m = 2 and 3 in equal parts; no ring loses its pattern. W3 has no radial change at all:
five parallel windings of fixed proportions.

## The blind reading, which was to be a check and not an input (`READING_ARM_MODES.md`, read before this was found)

Observed, in starlight, by Fourier decomposition: A3/A2 = 0.33 ± 0.19 (grand design), 0.48 ± 0.24 (multiple-arm),
0.58 ± 0.11 (flocculent); A4/A2 "about half in all cases" (46 S4G galaxies); A6 about 0.1 or less for nearly all;
83 % of multiple-arm galaxies have **two** inner arms inside 0.5 R25 and 2 % four; where a second mode appears it
is outside the two-armed part and it is m = 3 or m = 1 (m = 4 joining in one galaxy); **no source read shows m = 5
or 6 dominant at any radius in stellar light**; fitted arms end at 0.5–0.7 R25 by one definition and are detectable
to 1.5 R25 by another. The reader's own line on the theory: "D'Onghia predicts 5–6 arms at the solar radius; the
observed outer takeover modes are m = 1 and m = 3."

Set beside the windows (amplitude ratio = √ of the power ratio): W1 gives A3/A2 ≈ 1.6 and m = 5–6 dominant from
8 kpc — it fails the reading's statements on the inner two arms, on A3/A2, and on m = 5–6. W2 and W3 give
A3/A2 = 1.0 beyond 4 kpc (1.1 and 1.0 mass-weighted) and A4/A2 ≈ 0.85–0.9 there — m = 2 among the largest, the
spectrum still flatter than observed, no m = 5–6 dominance outside the bar. The error as built sits nearest the reading (A3/A2 = 0.89, A4/A2 = 0.65 mass-weighted;
two arms inside), by accident.

## What the lead thinks the choice is (for your judgement)

- **W1 is the plan's law correctly implemented** (BUILD_III §5: "the local swing parameter X_m(R) … today's named
  alternative becomes the law"; your ruling 3: "this is the definition, not an approximation"). The reading
  contradicts what the plan assumed of it — a stop condition in its own right (§3d: "a source contradicts what this
  plan assumed"). Swing amplification of a light exponential disc does predict many arms at the solar radius; two
  strong inner arms in real discs are commonly a driven pattern (a bar, a companion), which this model's P3 (the
  bar) has not built. W1 now and a bar-driven m = 2 at P3 is one coherent course; its price is a Milky Way template
  that reads four-to-six-armed for two sessions, and a recorded debt against the reading.
- **W3 is the law S26 sourced and ruled** (Sellwood & Masters' "1/f_d ≲ m ≲ 2/f_d", a statement about the disc as
  a whole): several modes at once (the owner's item), no radial branching (direction b of `RESEARCH_AREAS.md` goes
  unbuilt, with the reading as the reason), arms to the grid's edge (your first ruling's fade never triggers).
- **W2** uses S26's formula with the local disc fraction: no new constant, radial change, m = 2–3 outside the bar;
  but X_m = 2/(m f_d) is the Mestel disc's identity, applied ring by ring to a disc that is not one.
- **The window as built is not a law**: the source's ranges on half the source's variable. Keeping it would be
  choosing a number by the picture.

Whatever is ruled, the mislabel is corrected (the function's `x2`, `swing_x`'s about: 2/f_d is m·X_m, i.e. X at
m = 1), a test re-derives the weights independently of the module, and every layer-on pin is re-read once more.
The layer-off rows cannot move (the amplitudes are derived fields; no row reads them).

## Questions

1. Which window is the law — W1, W2, W3, or another form — in final wording, with what it predicts for the two
   templates (use the table's numbers) and what is forbidden?
2. Is the blind reading now an input to this choice, or still only a check? If the ruled law fails statements of
   the reading, which are recorded as the debt and what closes it (P3's bar-driven m = 2? an m = 1 term?)
3. Does your first ruling's predictions list stand as "read on a wrong probe, re-read on the right one", and does
   anything else in rulings 1–10 change with the window (the fade radius, the saturation's reach, the ridge)?
4. Is the choice between a many-armed Milky Way template (W1) and a two-to-three-armed one (W2, W3) the owner's
   to make rather than yours? If so, what exactly is the owner asked, and does the build wait?

## The ranges you may read (at most these three)

1. `docs/READING_ARM_MODES.md` lines 95–150 — "What a model should reproduce" and the conflicts between sources.
2. `model/galaxy/stages/pattern.py` lines 104–135 and 160–200 — `swing_window`, `swing_weight`, and the local
   window as built.
3. `docs/DECISIONS.md` lines 5157–5166 — D175's two readings of the window's form (S26), where the global form was
   chosen and the local one named.
