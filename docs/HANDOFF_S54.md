# HANDOFF_S54 — a conditional gate: NGC 4414's fit ran three unmeasured controls to their bounds

**For Fable, one short turn (BUILD_III §3c). Read this file and at most the five ranges named at the end. Run
nothing, explore nothing, write nothing. Answer in at most 80 lines: the ruling in final wording, with what is
predicted and what is forbidden afterwards.** Written by the Opus lead of S54 (Phase T, the templates), 2026-10-04.
The owner's standing order (2026-10-03): run the sessions back to back, stop only for a ruling that is the
owner's, "spawn fable subagents when you need to and in accordance with the plan". If your answer is that this is
the owner's to rule, say so and say what to ask.

## Why the gate opened (BUILD_III §3d)

D213 ruling 3 cannot be followed as written and mean what it says. It gave the fit an objective — squared
residuals of three targets in half-windows, plus 10⁻³ × squared departures of the seven controls from the defaults
in units of their ranges — and said of the second term: "The tie-break keeps a control nothing measures at the
Milky Way's value." **Run as written, it does not.** And four of D213's five predictions failed.

## What was read and built

| Step | State |
|---|---|
| The reading (`READING_NGC_4414.md`) | Blind: a reader forbidden the repository; 17 properties, a window each, fixed before any model output for the galaxy |
| D213 | Committed before the fit: three fit targets, the objective, five checks on the reader's windows, predictions |
| Builder A | `galaxy/templates.py`, `template=`, `/api/templates`, `tools/fit_template.py`, the checks' report in `galaxy.specs`; merged into `session-54`. `milky_way` is bit-identical to the defaults. The 37 rows unchanged |
| Builder B | The viewer's landing, switcher, lens per template, compare-with-a-picture; not merged yet; the NGC 4414 frames wait on the fit |

## The fit as D213's objective gives it (fit A; 433 evaluations, deterministic, four of five starts agree)

| Target | Window | Measured | Model | Residual (half-windows) |
|---|---|---|---|---|
| Peak of the curve inside 20.6 kpc | [222, 247] km/s | 237 | 238.85 | +0.148 |
| Stellar disc scale length | [1.5, 1.9] kpc | 1.649 | 1.673 | +0.122 |
| Stellar mass | [3.4, 5.9] × 10¹⁰ M☉ | 4.467 | 3.973 | −0.395 |

| Control | Default (Milky Way) | Fitted | Range | |
|---|---|---|---|---|
| `halo_mass` | 1.1e12 | 5.89e11 | 1e11–1e13 | |
| `disc_spin` | 0.0173 | 0.01409 | 0.005–0.05 | |
| `halo_assembly_z` | 1.66 | **0.5** | 0.5–5 | at its bound |
| `baryon_retention` | 0.35 | **0.5** | 0.05–0.5 | at its bound |
| `infall_timescale` | 7 Gyr | **1 Gyr** | 1–14 | at its bound |
| `inside_out_index` | 1 | 0.45 | 0–3 | |
| `migration_efficiency` | 3.6 | 3.6 | 0–8 | no target sees it |

Objective 0.1931 = 0.1927 (targets) + 0.0004 (tie-break). The targets are in tension: a disc this compact and
massive wants a higher peak than 237 km/s, so the search lowers the halo's concentration (late assembly) and trades
stellar mass. **The infall time goes from 7 Gyr to the 1 Gyr bound for a gain of about 0.05 half-windows in one
target**: gas that falls in early is all turned to stars, which lifts the stellar mass a little at fixed baryons.

## The five checks, read once on fit A (blindness spent for fit A only)

| Check | Window | Model (fit A) | Verdict | D213 predicted |
|---|---|---|---|---|
| Curve shape S (outer / peak) | [0.71, 0.86] | 0.648 | miss, low | miss high — failed |
| Star formation rate | [1.8, 4.7] M☉/yr | 0.125 | miss, 14× low | near the lower edge — failed |
| Hydrogen (HI + H₂) | [7.4, 14.7] × 10⁹ M☉ | 3.72 | miss, low | pass — failed |
| M_K | [−24.62, −24.12] | −22.98 | miss, 1.14 mag faint | not predicted |
| B − V face-on through dust | [0.72, 0.82] | 0.819 | pass, by 0.001 | miss blue — failed |

Fit A is a quenched disc: old, red, gas-poor. NGC 4414 is a star-forming Sc (2.9 M☉/yr, 10¹⁰ M☉ of hydrogen).

## What the builder measured on the fit side only (no check was read for these)

| Fit | Free controls | Objective | Peak | Scale length | Stellar mass | Bounds hit |
|---|---|---|---|---|---|---|
| A (as D213) | all seven | 0.193 | +0.148 | +0.122 | −0.395 | assembly, retention, infall |
| B | five: `infall_timescale` and `inside_out_index` held at the defaults | 0.251 | +0.175 | +0.135 | −0.450 | assembly 0.5 (retention 0.492, inside) |
| C | four: `halo_assembly_z` held too | 0.610 | — | — | −0.717 | not reported |

All three targets are inside their windows in A, B and C. Also found: the three target fields are **stepped** in
`halo_mass` and `disc_spin` (a jump of 0.014 half-windows across 2.5e-4 of the spin's range — quantities snapped to
the radial grid, cause not traced), which is why the search differences widely. A debt, whatever is ruled.

## The lead's reading of what went wrong

1. **The defect is in D213's ruling 3, and it is visible from the fit alone.** Three numbers cannot identify seven
   controls. The tie-break at 10⁻³ is 0.2 % of the objective; it breaks exact ties and nothing else. A fitted
   value at the bound of its range is not a fit of that control: it says the targets push without limit in a
   direction no measurement constrains. The two history controls were moved by structure targets that do not
   measure a history.
2. **But the checks have been read**, and BUILD_III's Phase T says of a failed check: "a failure is a recorded miss
   with its debt (B5), not a reason to refit." A refit chosen after four misses is a forking path, whatever its
   fit-side justification. The lead will not make that call alone.
3. **The reading keeps unspent blind windows**: HI and H₂ separately, the outer flat speed, the face-on M_B, the
   infrared luminosity, the bulge. No model number has been printed against them for any fit.
4. **The reader's own recommended split** (READING §6, written blind, named in D213 as the alternative before the
   fit): fit = peak speed, scale length, M_K, HI mass; checks = S, star formation rate, H₂, B − V, stellar mass.
   It puts a gas measurement and an age-sensitive magnitude in the fit, which is what constrains the history.

## The options

- **O1. Adopt fit A as it stands.** Four recorded misses with debts; the plan's text followed to the letter. Cost:
  the second template of the build is a quenched disc for every later phase (P1–V8 draw it; the goal picture is a
  blue flocculent spiral), and the published "fit" has three controls that are bounds, not fits.
- **O2. Fit B — free only what the targets can identify.** Rule stated on the fit side: a control enters the
  search only if a target measures what it controls; the three targets are structure, so the two history controls
  and migration stay at the defaults. Then the five checks are read **once more, declared disclosed, not blind**
  (D192's language), with A's verdicts kept in the record beside them; no further refit whatever they read.
- **O3. Fit C** — as O2 with the assembly epoch held too (four free controls; a mass residual of −0.72).
- **O4. The reader's split** (item 4): four fit targets, five checks of which two are new and unspent (H₂, and the
  stellar mass as a check); S, the star formation rate and B − V have been read on fit A and would be disclosed.
- **O5. A constrained form**: among all input vectors whose targets lie inside their windows, the one nearest the
  defaults in range units. No weight to choose; the fit sits on the windows' edges.

**The lead's recommendation: O2**, with (a) D213 amended in place to say the tie-break failed its stated purpose
and why, fit A's two tables and five verdicts kept in the decision as the first reading; (b) the five checks on
fit B recorded as disclosed, their misses entered with debts; (c) the unspent windows named as the blind
successors and left unread until a later session rules which to spend; (d) the assembly epoch at its bound
published as the fit's finding (the model cannot lower its peak enough inside the range); (e) no third fit in this
build. O4 is the named alternative: it measures the history rather than freezing it, at the price of changing the
check set after results were seen.

## Questions

1. Which option, or what other form? In final wording, as it should be transcribed into D213.
2. On the chosen fit, what standing do the five checks have (blind, disclosed), and may any of the unspent windows
   be spent now as blind checks on it — which, and how many?
3. Is a control fitted to the bound of its range acceptable in a published template, or must it be held and the
   residual published instead? (Fit B leaves `halo_assembly_z` at 0.5.)
4. The stepped targets: a debt to open as it stands, or does it change what a fit on this model can claim?
5. Is any of this the owner's to rule rather than yours (the owner's ruling 8 was "yes, do 5": five checks fitted
   apart, windows fixed blind)? If so, what exactly should the owner be asked?

## The ranges you may read (at most these five)

1. `docs/DECISIONS.md` lines 8500–8575 — D213 as committed before the fit.
2. `docs/BUILD_III.md` lines 237–259 — Phase T's text; and lines 158–163, the stop conditions.
3. `docs/READING_NGC_4414.md` lines 80–110 — the windows with their arithmetic.
4. `docs/READING_NGC_4414.md` lines 141–163 — the reader's recommended split and the structural mismatches.
5. `model/galaxy/templates.py` lines 340–430 — the template as committed with fit A.
