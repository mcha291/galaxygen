# BUILD_III — the third build: two templates, a physics model beside a randomness layer, and the pictures they are for

**Status: PROPOSED 2026-10-03, on the owner's word ("please create a plan …"), awaiting adoption.** Fourteen board
rows, S53–S66. Nothing here is a ruling until S53 records the owner's answers to §7 in `DECISIONS.md` (D212). Hand a
session this document, `RULES.md`, `BRIEF.md`, `RENDER_PHYSICS.md` and the sections of `GALAXY_INPUTS.md` its phase
names.

Everything here is `[inferred]` design unless tagged. Every source named is `[recall]` and **NEEDS SOURCING**: it is
read on a fetched page by a reading agent before a number from it enters code (RESUMING: a citation is read before
it enters code and says what fraction it covers; S51's `READING_GAS_PATTERN.md` is the form).

---

## 0. What this build is for, and what it will not reach

**The goals** are two pictures in `docs/goals/`: an artist's impression of the Milky Way face-on (a long yellow bar,
unequal kinked arms, dust lanes threaded with pink knots, blue arms on a warmer disc) and Hubble's NGC 4414 (an
inclined, unbarred, flocculent disc: a yellow core, a filamentary dust web, patchy blue-white star complexes).
**They are display targets, never acceptance rows** (C6, D113): the first is a drawing, the second is one galaxy
through one instrument.

**The owner's direction (2026-10-03):** build the physics up to what is feasible for a fast generation on consumer
cloud resources, not to perfection; where the proper physics is too expensive and an average looks wrong, a separate
layer injects randomness to stand in for it.

**Where the gap is today** (the S52 review). The model is ahead on content and behind on shape; the viewer is behind
the model.

| What the pictures need | The model today | The viewer today |
|---|---|---|
| Irregular arms; flocculence | One perfect logarithmic spiral, repeated m times | Nothing to draw |
| A bar as a body, or no bar | A faint two-fold ripple with the disc's colour; always present | The centre renders round |
| Blue arms on a warmer disc | Published: the light split by age and placed per age | One colour per ring in the field mode |
| HII knots along the arms | A census of ~12 900 regions, each about a parsec across | A smooth Hα layer at galaxy scale |
| Clumpy dust, filaments | The gas ridge (S51); ~16 800 clouds placed independently; smooth between them | The smooth lane; clouds only below 4 kpc |
| Resolved bright stars and complexes | Bright catalogue and clusters; no grouping | Points over a smooth field |

**What will remain after this build** `[inferred]`. The Milky Way picture: the same kind of picture, differing in
hand-drawn irregularity. NGC 4414: right at a glance in colour, inclination, flocculence and mottling; side by side
the dust web and star complexes will still read as procedural. That residue is the cost of not simulating
self-gravitating gas (§8), and the randomness layer is what stands in its place.

---

## 1. The separation: the physics model and the randomness layer

### 1a. The principle

**The physics model publishes laws and statistics. The randomness layer publishes realisations.** Physics says which
arm numbers a disc amplifies and how strongly, how wide and how offset the gas ridge is across an arm, how long the
bar is, how strongly clouds cluster. It does not say where each arm, kink, cloud complex or filament lies: that
takes a simulation stepped through time (`RESEARCH_AREAS.md` §1). The layer draws those placements, reproducibly,
from measured statistics. **A composed field — a density contrast over (R, φ), a census placement — is a law
applied to a realisation.**

### 1b. Four kinds of quantity (rule A10, to be amended at S53)

| Kind | Definition | Example |
|---|---|---|
| Input | A free control | `halo_mass` |
| Derived | A pure function of the inputs | `bar_half_length`, `gas_arm_contrast` |
| Seeded | Inputs and a seed: **a measured scatter between galaxies, or the sampling of a derived distribution** | the fast-bar ratio's draw; a star's mass drawn from the IMF |
| **Synthetic** (new) | Inputs and the layer's seed: **a realisation standing in for physics the model does not compute**, constrained by measured statistics | where each arm mode's phase lies; the clustering field; the gas fluctuation field |

### 1c. The layer's five rules

1. **In the model, on its own seed** (`texture_seed`, a fifth seed): rerolling it changes placements and texture and
   nothing else. Never frame-seeded, never in the viewer's own code.
2. **Conserving.** A synthetic field redistributes inside a ring or a cell; it never changes a total. Each declares
   what it conserves (`FieldDecl.conserves`).
3. **Sourced statistics.** Its spectrum, contrast or correlation is a measured one, cited; its anisotropy comes from
   the model's own shear. Each declares the statistic (`FieldDecl.statistic`).
4. **Labelled.** Each declares the physics it stands in for (`FieldDecl.stands_in_for`), so the day that physics is
   built the field is replaced, not layered over.
5. **Evaluable at a point.** No stored grid is its definition: a region, a zoom level or a shader evaluates the same
   function of position and seed (D60).

### 1d. The invariants (machine-checked from Phase R on)

- **I1.** With the layer off, the model runs, and every field without a φ axis and every scalar that is not a census
  statistic is bit-identical to the layer-on run.
- **I2.** A census's expected counts per ring are identical with the layer on or off; only placements differ.
- **I3.** The acceptance table is judged on the layer-off run. No row reads a synthetic field. (Rows 35 and 37 read
  the HII census and moved with S51's redraw; under I3 they stop moving with placement.)
- **I4.** No physics stage requires a synthetic field, except the census stages, which consume composed placement
  weights only and are declared *placement readers* in the graph.
- **I5.** The viewer and the API carry a switch: physics only, or physics with the layer.

### 1e. Where things live `[inferred]`

`model/galaxy/stages/` stays the physics. `model/galaxy/layer/` is new: the noise primitives, the realisation
stages, and `compose` (law × realisation → the (R, φ) fields and placement weights). `run(model, inputs,
layer=True)`; every route takes `layer=off`. Whether `azimuthal` collapses into `basic` plus the layer is Phase R's
recommendation and the owner's ruling (§7).

---

## 2. Templates

**A template is a named galaxy: an input set, its seeds, a camera, an instrument, and optional pins.**

- **Inputs and seeds:** the seven controls, the merger list, the five seeds.
- **Camera and instrument:** the default view and filter set (NGC 4414: the goal image's inclination and framing,
  the Hubble broadband set; the Milky Way: face-on, rgb).
- **Pins:** measured structure of *that* galaxy that overrides the layer's draw — the Milky Way's arm segments from
  the maser fits, its bar angle; NGC 4414's missing bar. A pin replaces a realisation with a measurement; it never
  touches a law. This is rule A5 extended: the defaults are measured values.
- **`milky_way` is today's defaults exactly** (gate: bit-identical). **`ngc_4414`'s inputs are fitted** to its
  measured properties by a bounded offline search, the residuals published: what the seven controls cannot reach is
  a finding to record, not a number to force (B5).
- The viewer lands on `milky_way` (rule D1, amended) and carries a switcher; "Edit galaxy" starts from the
  template's inputs.

---

## 3. How the sessions run

The protocol is `GALAXY_PLAN.md` §5's and `RESUMING.md`'s, as BUILD_II adapted it: one row, one `session-NN` branch,
one `--no-ff` merge, the suite's own `EXIT=0` line gating it, the tag at close, `verify_clone` after. Numbers are
sequential and taken when written: decisions from **D212**, debts from **#132**, acceptance rows from **38**.

### 3a. Who leads a session

- **Fable leads** where the session makes rulings on physics, changes a rule or designs an interface other sessions
  build on: Phases 0, R, P1, P2, P3, L2 and the audit. Fable writes the ruling **before** any code moves (D113),
  spawns Opus agents for the reading and the building, reviews every diff, re-pins the combined state, and writes
  the records.
- **Opus leads** where this document and the preceding session's `BRIEF.md` already hold the rulings and the work is
  a specified build: Phases T, V5, V6, P4, L1, V7, V8. An Opus lead may spawn Opus agents under the same briefs.
  **An Opus lead stops and closes partially (C2d), asking for a Fable session in `BRIEF.md`, if:** a ruling here
  cannot be followed as written; a number moves in the layer-off acceptance table; a source contradicts what this
  plan assumed; or a gate cannot be met without changing what is measured.

### 3b. The reading agent's brief (Opus, read-only, parallel, one question each)

State the question and why the model needs it. Then the rules, verbatim: a number is written only if read on a
fetched page, tagged `[verified: author year, journal or arXiv id, section or table, URL]`; each citation says what
fraction it covers; what the quantity *is* (definition, mask, resolution) is stated; anything recalled is tagged
`[recall — NOT READ]` and kept out of the summary table. Output: one Markdown note in the scratchpad with a summary
table, per-source notes, what could not be read, and a recommendation with named alternatives. The lead assembles
the notes into `docs/READING_<TOPIC>.md`.

### 3c. The building agent's brief (Opus, `isolation: worktree`)

- **First step:** `git merge --ff-only session-NN` (a worktree is cut from `main`), then `tools/bootstrap.py`.
- **It reads** the ruling in `DECISIONS.md` (committed before launch), `RESUMING.md`'s "Writing a stage", and the
  files it owns. **It owns a named, disjoint set of files**; a failure in another agent's file is reported, not
  edited.
- **It neither pushes nor writes** `DECISIONS.md`, `GALAXY_INPUTS.md`, `RESUMING.md`, `BRIEF.md`, `GALAXY_PLAN.md`.
- **Predictions are read before they are judged** and nothing is changed to make one hold (B4, B5). A re-pin
  carries `# S<NN> (D<n>): was <old>`; a failure the change does not explain is reported, not re-pinned.
- **It does not run the whole suite** while another agent or the lead does; the lead runs it once on the combined
  state. A stage's restricted view answers False for an undeclared constant: declare what is read.
- **Its report:** branch and commits (or, when the owner has ordered review before commit, no commit and a patch
  left in the scratchpad), files, every re-pinned number before and after, each prediction held or failed, the
  spec summary line, what was not done.

### 3d. Every phase

Probe before build. The instrument before the thing it certifies (B1). Cold timings when a stage's cost changes
(B2). A picture gate from Phase 0 on: the goal metrics and a capture recorded in the phase's decision.

---

## 4. Reconciled: what the repository already has (2026-10-03, after S52)

| This plan needs | The repository has | Consequence |
|---|---|---|
| A gas pattern | `gas_pattern` (S51): a von Mises ridge in one arm's phase, sourced width and contrast, no offset | P1 restates it as a response to any stellar pattern; P2 derives its profile |
| Light split by age | `bright.resolve`: young, middle, old parts per ring, used by the star-first remainder | V5 exposes them as field components; no stage changes |
| Object censuses | Clouds, clusters, HII regions, bubbles, remnants, bright stars, with per-region determinism | V6 draws them at galaxy scale; L1 correlates their placement |
| A dust layer | The gas's height per ring; the heating in that geometry (S52) | L2 modulates the diffuse part only |
| Structure synthesis | Cloud interiors synthesised in the viewer from the cloud vector, below 4 kpc; its noise index unsourced (#110) | The precedent for the layer; it moves under the layer's rules in Phase R |
| A spiral pattern speed | None (#81); the bar's only | P2 |
| Named galaxies | Defaults only; the viewer's "presets" are camera angles | Phase T |
| A picture test | None for the React viewer (T12: no headless browser on the machine) | Phase 0, on the owner's leave to install one |
| Seeded draws classified | Three kinds; some seeded draws are placements without physics, some unsourced (#95) | Phase R's audit |

---

## 5. The phases

### Phase 0 — adoption, the rules, the instruments (S53, Fable)

**Rulings recorded (D212):** §7's answers. **Rules amended on the owner's word:** A10 (four kinds), A5 and D1
(templates), `RENDER_PHYSICS.md` §8 (rewritten: every visible feature traces to a published field or to the layer;
frame-seeded noise and colour for appearance stay forbidden; "no detail below the cloud vector" becomes "no detail
the layer does not publish") and D5 (the viewer may evaluate a published seeded function; it still computes no
physics). `RESEARCH_AREAS.md` and `VIEWER_TASKS.md` point their absorbed entries here (directions a–h; T1, T5–T8,
T12, T16, T28).

**The instruments (B1).**
- `tools/goal_metrics.py`: on any image — a goal or a capture — the radial colour profile, the azimuthal Fourier
  amplitudes m = 1–8 by radius after deprojection, the arm–interarm contrast in the blue channel, the dark-lane
  covering fraction, the power-spectrum slope of the unsharp-masked image between stated scales, and the count of
  point sources above a threshold. Tested on synthetic images of known spectra. **Display targets, not rows.**
- T12: the React viewer captured at fixed cameras per template (needs a headless browser; §7). Without it, the
  lead's in-pane captures, as at S51.

**Agents:** Opus builder A (`goal_metrics` and its tests), Opus builder B (T12's harness). **Gate:** the metrics
return known values on synthetic inputs; a baseline table — both goals, both of today's renders — in D212.

### Phase T — templates (S54, Opus lead) — the owner's item 1 and list item 10

**Reading:** NGC 4414's distance, inclination, position angle, rotation speed, stellar and gas mass, star formation
rate, scale length, morphological class, bar classification, each with its coverage.

**Build.** `galaxy/templates.py` (the two templates as data, every number tagged); `tools/fit_template.py` (a
bounded search of the seven controls against the measured properties, residuals table committed);
`/api/templates` (metadata only, D4) and `template=` on every route that takes inputs; the viewer's landing on
`milky_way`, the switcher with model-made thumbnails, the template's camera and filter set, and "compare with the
goal" beside the render at a stated band and scale (T16 ii).

**Gate:** `milky_way` reproduces the defaults bit for bit; the fit's residuals are published and none is tuned
away; a timings row; vitest on the switcher; a capture of each template beside its goal.

**Agents:** one reader; builder A (model, API, fit tool); builder B (viewer).

### Phase R — the separation (S55, Fable) — the owner's item 2

**A behaviour-preserving restructure: with the layer on, every published number is bit-identical to S52.**

1. `synthetic` joins the provenance vocabulary; `FieldDecl` gains `stands_in_for`, `conserves`, `statistic`,
   required for synthetic fields; `texture_seed` joins the seeds.
2. `model/galaxy/layer/`: **the noise primitives, built and tested first** — a point-evaluable lattice noise keyed
   by an integer hash of seed, cell and octave, written in 32-bit integer arithmetic so a GLSL twin can match it
   bit for bit (V7); octave shaping to a stated spectral slope; a shear transform; a unit-mean log-normal map.
   Tests: determinism at a point, mean, measured slope, anisotropy under shear, committed test vectors.
3. `compose`, the `layer` switch through `run`, the API and `galaxy.specs`; the graph's rules I1–I5 as tests.
4. **The audit of every `ctx.rng` and `_seeds.rng` call site**, each ruled into seeded-scatter, seeded-sampling or
   synthetic, in a table in the decision. Expected to move: the cloud vector's unsourced draws (#95), the viewer's
   cloud-interior noise (#110, T8), the arm phases once P1 gives them a draw. Expected to stay: the fast-bar ratio,
   the arm number's weighted draw, the pitch's scatter, every IMF and age sampling.
5. The recommendation on `basic` and `azimuthal`.

**Gate:** bit-identical outputs with the layer on; I1–I5 green; the layer-off acceptance table read once and
recorded (rows 35 and 37 will move to their uniform-placement values and then stay).

**Agents:** builder A (primitives, tests, vectors); builder B (provenance, `FieldDecl`, graph, switch); builder C
(the moves the audit rules, and their re-pins). Fable: the audit table, the rulings, the review, the rule text.

### Phase V5 — light by age in the field (S56, Opus lead) — the owner's item 4, first part

`/api/render` returns `stars_young`, `stars_middle`, `stars_old`, each through the curves on its own and placed by
its own weight (the gas contrast, `sfr_modulation`, the stellar contrast), summing to `stars` per ring and filter
to rounding; the field mode draws the three. No stage changes.

**Gate:** the closure; the arm–interarm colour difference measured before and after (goal metric); payload and
timings. **Agents:** builder A (render route and its tests), builder B (viewer).

### Phase V6 — the censuses at whole-galaxy scale (S57, Opus lead)

- **Clouds as extinction:** the census rasterised by window and level into an opacity the march composites at the
  clouds' height; the ring's diffuse dust reduced by the clouds' share so each ring's dust mass is unchanged.
- **HII regions as knots:** each region's line light through the set as a point, sized by its bubble when
  resolved; the smooth Hα layer reduced by what the points carry.
- **Clusters with their half-mass radius** (T6, the profile ruled in `BRIEF.md`), **bright stars by tiles** to 10⁶
  (T28's windowed request), **the depth-aware composite** (T5).

**Gate:** each closure (dust mass per ring, Hα per window, points plus field equal the render); the frame-time
readout; goal metrics (dark covering fraction, point counts). **Agents:** three builders, one per bullet.

### Phase P1 — several modes at once; the gas follows any pattern (S58, Fable) — list items 1 and 2

**Reading:** Fourier amplitude spectra of spirals by arm number and radius; the swing amplifier's gain against X;
the radial extent of a transient mode between its resonances.

**Physics.** The amplitude of each arm number at each radius from the *local* swing parameter (today's named
alternative in `pattern.py` becomes the law), normalised to the sourced class contrast, its galaxy-to-galaxy
scatter seeded. **Layer.** Each mode's phase and radial window. **Gas.** The ridge restated as the gas settling
into the composed pattern's potential — g ∝ exp(β ψ), normalised round each ring — with β fixed so that one mode
returns S51's field to 1e-9 (the regression gate).

**Gate:** ring means 1; the single-mode regression; a Fourier decomposition of the composed field returns the
published amplitudes; I1–I3; the goals' azimuthal spectra beside the render's.

**Agents:** two readers; builders for the mode law, the realisation, the gas response, and the catalogue re-pins.

### Phase P2 — pattern speeds; the gas shock ring by ring (S59, Fable) — "level A"

**Reading:** the steady spiral shock (Roberts 1969; Shu, Milione & Roberts 1973); its width and offset (Gittins &
Clarke 2004; Kim & Ostriker 2002, partly read at S51); pattern speeds of transient modes.

**Build.** A pattern speed per mode (its corotation at the mode's radius), closing #81's first half; the young-star
cut replaced by the crossing time it gives. `gas_shock`: per ring, the steady one-dimensional isothermal flow
through the arm's potential in the rotating frame — a fixed-step integration with a bisection on the sonic point
and the isothermal jump (A1: the step count is known in advance) — publishing the ridge's profile across an arm.
The profile replaces the von Mises: its width, contrast and **offset** are derived.

**The instrument first:** the solver reproduces a published profile at the source's parameters before the model
uses it. **Declared in advance:** where the forcing is too weak for a shock the response is the linear one.

**Consequences:** `GAS_ARM_WIDTH`, the mask and the two contrast constants stop being inputs; PHANGS's ratio of
means becomes a check, a disclosed row (its numbers have been printed, D113). #129 and #131 are re-ruled. D210's
ruling 3 is superseded where the physics signs the offset.

**Agents:** two readers; builder A (solver and instrument); builder B (integration and re-pins).

### Phase P3 — the bar: a body, an absence, its lanes (S60, Fable) — list items 6, 9, 7

**Reading:** bar light fractions, axis ratios and profiles from the S⁴G decompositions; the bar fraction against
disc properties and a disc stability criterion; star formation inside bars; the gas lanes' offset and curvature.

**Build.** *The body:* inside the bar radius the ring's old stars are concentrated along the bar's axis by a
mean-one two-fold profile of sourced axis ratio and light share; today's star formation avoids its interior.
*The absence:* presence derived from the stability criterion with a seeded residual; an unbarred galaxy publishes
NaN for the bar's fields (D164) and rows 15–17 are not applicable to it. *The lanes:* a template curve with sourced
parameters, **synthetic**, standing in for two-dimensional gas flow in the bar's potential (§8, level B).

**Gate:** ring totals unchanged; rows 15–17 unchanged for the Milky Way; the Fourier m = 2 amplitude inside the
bar against the sourced value (`BAR_CONTRAST_MEDIAN`'s like-for-like).

**Agents:** two readers; builders for the body, the presence and its rows, the lanes.

### Phase P4 — pitch along an arm; the templates' pins (S61, Opus lead) — list item 8, first half

Segments of seeded length and pitch change from the measured distributions (Honig & Reid 2015, read at S51;
Díaz-García et al. 2019), continuous in phase: synthetic. The Milky Way's pins — arm segments and kinks from the
maser fits (Reid et al. 2019), the bar's angle — and NGC 4414's (unbarred, flocculent). **Gate:** the pinned arms
pass through the measured loci; a galaxy without pins is unchanged. **Agents:** one reader, two builders.

### Phase L1 — clustered censuses; young stars near where they formed (S62, Opus lead) — list items 3 and 5

**Reading:** two-point correlation functions of young clusters and molecular clouds, and how they flatten with
age; association sizes against age.

**Build.** The synthetic field `census_clustering`, unit mean in every level-0 cell, multiplying the clouds'
expected counts; clusters inherit it; the bright catalogue's 20–100 Myr stars follow the same field with its finest
octaves dropped as age grows (a drift of dispersion times age).

**Gate:** the census's measured correlation function returns the sourced slope over the sourced range; I2; D60's
per-region tests; the layer-off acceptance table bit-identical.

**Agents:** one reader; builders for the field and clouds, the bright stars, the re-pins.

### Phase L2 — structure between the clouds; spurs (S63, Fable) — list items 4 and 8, second half

**Reading:** column-density power spectra of atomic gas and dust in nearby discs and their break at the disc's
thickness; log-normal column widths against Mach number; feather spacing.

**Build.** `gas_fluctuation`, published as **parameters** — slope, log-normal width from the ring's Mach number,
outer scale from the gas's height, shear stretch from the disc's own shear and a sourced lifetime, the seed — with
a Python reference evaluator and **committed test vectors a GLSL twin must match**. It modulates the diffuse dust
only; the clouds stay the census's. Spurs: spacing derived from the ridge's Jeans length, phases synthetic.

**Gate:** unit mean per cell; the evaluator's measured spectrum; the vectors; I1–I3.

**Agents:** two readers; builder A (evaluator, vectors); builder B (spurs).

### Phase V7 — the layer in the viewer (S64, Opus lead)

The GLSL twin of the noise (matching the vectors to 1e-5); the diffuse dust modulated per pixel in the march; the
spurs; the bar's body and lanes; the "physics only" switch. **Gate:** the vectors; the frame-time readout; each
ring's dust on screen unchanged by the layer (`__galaxygenFrameSum` on a dust-only frame). **Agents:** two builders.

### Phase V8 — the display defaults, the instrument, the goal captures (S65, Opus lead)

T1 per template, from the owner's tuning; NGC 4414's instrument look (the sprite's scale ruled, T9; diffraction
spikes); committed captures of both templates beside their goals; the goal metrics' final table against Phase 0's
baseline. **Agents:** one builder; the owner's panel settings are the input.

### Audit V (S66, Fable)

Every citation entered since S51 read again; every synthetic field's conservation and statistic re-measured; I1–I5
re-derived, not re-run; a picture traced feature by feature to a published field or a layer field; the register
pass; the goal metrics table judged honestly against §0's "what will remain".

---

## 6. Sequence

| S | Phase | Deliverable | Blocked by | Lead |
|---|---|---|---|---|
| **53** | 0 | Adoption (D212), the rule amendments, `goal_metrics`, the picture test, the baseline table | the owner's §7 answers | Fable |
| **54** | T | Two templates, the fit and its residuals, `/api/templates`, the switcher, compare-with-goal | 53 | Opus |
| **55** | R | The fourth kind, `layer/` and its primitives, the switch, I1–I5, the audit of every draw | 53 | Fable |
| **56** | V5 | The field's light by age | nothing (can precede 55) | Opus |
| **57** | V6 | Clouds, HII knots, clusters and bright stars at whole-galaxy scale | 56 | Opus |
| **58** | P1 | Several modes; the gas follows any pattern | 55 | Fable |
| **59** | P2 | Pattern speeds; the shock per ring; #81, #129, #131 re-ruled | 58 | Fable |
| **60** | P3 | The bar's body, its absence, its lanes | 58 | Fable |
| **61** | P4 | Pitch segments; the templates' pins | 58, 60 | Opus |
| **62** | L1 | Clustered censuses; young stars near birth | 55, 57 | Opus |
| **63** | L2 | The gas fluctuation field and its twin's vectors; spurs | 55, 59 | Fable |
| **64** | V7 | The layer in the shader; the physics-only switch | 63 | Opus |
| **65** | V8 | Display defaults, instrument look, goal captures | 64, the owner's tuning | Opus |
| **66** | — | Audit V | 53–65 | Fable |

55 → 58 → {59, 60} → 61 is the hard chain on the model side. 56 and 57 need nothing new from the model and give
the first visible gain; they may run before 55 if the owner wants pictures first. 62 and 63 both stand on 55's
primitives. Seven rows are Fable's and seven Opus's.

---

## 7. Rulings needed before starting (the owner's)

1. **Adopt the plan** and its numbering, S53–S66.
2. **The fourth kind** (rule A10) and the layer's five rules (§1c).
3. **`RENDER_PHYSICS.md` §8 and rule D5 amended** as Phase 0 words them.
4. **Templates** (rules A5 and D1): the viewer lands on `milky_way`; a template may carry pins.
5. **The goal images committed** to this public repository, with their credits — both are agency images
   `[recall]`; the credit lines want checking before the push. They are untracked today.
6. **A headless browser installed** for the picture test, or captures stay manual.
7. **`basic` and `azimuthal`:** one model with the layer switch, if Phase R shows them identical.
8. **NGC 4414's checks:** a small table of blind windows for the template, or display only.
9. **Pictures first?** V5 and V6 before Phase R (§6).
10. **The dependency rule stays numpy-only** (level A needs nothing more).

---

## 8. Scope boundary — recorded as decisions

**Level B, two-dimensional gas in the rotating potential,** is not built. It would give real bar lanes and shock
ridges at 10–100 s a galaxy `[inferred]`; the bar's lanes are a synthetic template until the owner orders it, most
plausibly as a precomputed table for the bar alone.

**Level C, self-gravitating, cooling, star-forming gas,** is not built and cannot run at generation time. Flocculence
and filaments are the layer's. A shipped library of simulations stays `RESEARCH_AREAS.md` §1's last resort.

**A live stellar disc** (arms that emerge) is not built: the pattern's shape stays laws plus realisations.

**#128's placement half, the remaining viewer debts (T9–T11, T13–T15, T17–T19, T24–T27) and the pinned model debts**
are not in this build unless a phase names them.

---

## 9. What not to do

**Do not let the layer change a total.** A synthetic field that moves a ring's mass, light, dust or star formation
is a bug, whatever the picture gains.

**Do not judge an acceptance row with the layer on.**

**Do not put the layer's noise in the viewer's own code.** The viewer evaluates the published function with the
published seed and parameters, and matches the committed vectors.

**Do not tune a synthetic field to a goal image.** Its statistics are sourced; the goal metrics are read, recorded,
and never targets.

**Do not draw a residual from a spread that is not galaxy-to-galaxy** (D210's amendment), and do not relabel an
unsourced draw "synthetic" to excuse it: a synthetic field still cites its statistic.

**Do not force NGC 4414's inputs.** What the seven controls cannot reach is recorded.

**Do not make the gas shock a convergence loop.** Fixed steps, a bisection, a declared fallback (A1).

**Do not rebuild what exists:** the light by age, the censuses, the dust's layer and the gas ridge are there (§4).

**Do not reserve number blocks.**
