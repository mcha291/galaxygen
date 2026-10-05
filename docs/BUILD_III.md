# BUILD_III — the third build: two templates, a physics model beside a randomness layer, and the pictures they are for

**Status: ADOPTED 2026-10-03 (the owner: "adopt the plan"); all ten rulings of §7 are answered.** Written
that day on the owner's word ("please create a plan …") and revised the same
day on the owner's word — "Fable usage is limited … make sure only work that really benefits from using Fable uses
that, and push the rest to Opus": every row is now Opus-led, and Fable is called at four named gates (§3).**
Fourteen board rows, S53–S66, **and a fifteenth since 2026-10-05: Phase P5, the arms as a census of pieces, inserted at S60 on the owner's ruling (D219, §7 rulings 11–12); every later phase runs one session on, to S67.** S53 records the owner's answers (§7) in `DECISIONS.md` as D212. Hand a session this document, `RULES.md`, `BRIEF.md`, `RENDER_PHYSICS.md` and the sections
of `GALAXY_INPUTS.md` its phase names.

Everything here is `[inferred]` design unless tagged. Every source named is `[recall]` and **NEEDS SOURCING**: it is
read on a fetched page by a reading agent before a number from it enters code (RESUMING: a citation is read before
it enters code and says what fraction it covers; S51's `READING_GAS_PATTERN.md` is the form).

---

## 0. What this build is for, and what it will not reach

**The goals** are two pictures the owner keeps locally in `docs/goals/` (ignored by git, on the owner's word; a
clone does not have them): an artist's impression of the Milky Way face-on (a long yellow bar,
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

### 1b. Four kinds of quantity (rule A10; the amended text is Appendix A)

| Kind | Definition | Example |
|---|---|---|
| Input | A free control | `halo_mass` |
| Derived | A pure function of the inputs | `bar_half_length`, `gas_arm_contrast` |
| Seeded | Inputs and a seed: **a measured scatter between galaxies, or the sampling of a derived distribution** | the fast-bar ratio's draw; a star's mass drawn from the IMF |
| **Synthetic** (new) | Inputs and the layer's seed: **a realisation standing in for physics the model does not compute**, constrained by measured statistics | where each arm mode's phase lies; the clustering field; the gas fluctuation field |

### 1c. The layer's five rules

1. **In the model, on its own seed** (`texture_seed`, a fifth seed): rerolling it changes placements and texture and
   nothing else. Never frame-seeded, never in the viewer's own code.
2. **Conserving.** A synthetic field redistributes inside a ring or a cell. It changes no ring total of a field it
   multiplies, and no expected count or expected total of a census it places; from L1, no realised ring total
   either. Each declares what it conserves (`FieldDecl.conserves`), and a declaration states what it does not
   keep, with the measured number. *(Amended at gate G1, D214: until then it read "it never changes a total".)*
3. **Sourced statistics.** Its spectrum, contrast or correlation is a measured one, cited; its anisotropy comes from
   the model's own shear. Each declares the statistic (`FieldDecl.statistic`).
4. **Labelled.** Each declares the physics it stands in for (`FieldDecl.stands_in_for`), so the day that physics is
   built the field is replaced, not layered over.
5. **Evaluable at a point.** No stored grid is its definition: a region, a zoom level or a shader evaluates the same
   function of position and seed (D60).

### 1d. The invariants (machine-checked from Phase R on)

- **I1.** With the layer off, the model runs, and every field not declared composed — every scalar, every history,
  every radial field, every φ-axis field tabulated in a pattern's own frame — is bit-identical to the layer-on
  run, except the census statistics named in `tests/test_layer.py::CENSUS_STATISTICS`, a closed list each entry of
  which names the census it is computed from. Every composed field is its declared neutral value. After L1 the
  list is empty. An *expected* total that is a sum of placement weights is equal within four units in the
  last place — the rounding of sums over the cells of weights that average to 1 to 1e-13; exact sums are not
  required *(amended at gate G2, S57, D216, as "one unit"; re-worded at S58 when the measured difference became
  two, D217; rulings by Fable)*.
- **I2.** A census's expected counts per ring — the numbers the draws are given, summed round the ring — are
  identical with the layer on or off to 1e-12. Until L1 the realised counts, and every total summed over realised
  objects, differ between the two runs by re-draw noise (measured S55: cloud mass −1.9 % galaxy-wide, up to 19 %
  in a cell ring; cluster mass −5.8 %; HII Hα −8.1 %, up to 43 % in a ring; over six seeds −1.0 ± 1.7 %,
  −2.2 ± 2.9 %, −2.1 ± 6.0 % — noise, not bias). From L1 a ring's objects are drawn on the ring's stream before
  the layer places them, and the realised totals are identical too.
- **I3.** The acceptance table is judged on the layer-off run. No row reads a synthetic field. (Rows 35 and 37 read
  the HII census and moved with S51's redraw; under I3 they stop moving with placement.)
- **I4.** No physics stage requires a synthetic or composed field; the census stages consume composed placement
  weights only and are declared placement readers. Placement also reaches physics through the realised
  catalogues: the stages that bin realised objects (`nebular`, `bubbles`, by `cluster_radius`) are a closed list
  in the test, and from L1 what they bin per ring does not depend on placement.
- **I5.** The viewer and the API carry a switch: physics only, or physics with the layer.

*I1, I2 and I4 were amended at gate G1 (S55, D214; ruling by Fable). As adopted they read: "every field without a φ
axis and every scalar that is not a census statistic is bit-identical"; "expected counts per ring are identical
with the layer on or off; only placements differ"; "no physics stage requires a synthetic field, except the census
stages". The first two promised a conservation of realised totals that a census drawn cell by cell at a weighted
expectation does not deliver; the ring-first draw that delivers it is L1's (S61).*

### 1e. Where things live

`model/galaxy/stages/` stays the physics. `model/galaxy/layer/` is new: the noise primitives, the realisation
stages, and `compose` — the gate, law × realisation — lives in `layer/`; a law stays with its stage; a stage that
publishes a composed field is a *composing stage*, declared so in the graph, and lives in `stages/` *(amended at
G1, D214)*. `run(model, inputs,
layer=True)`; every route takes `layer=off`. With the layer off the composed fields are their neutral value, 1.
**Existing draw streams keep their seeds and their values** (Phase R is behaviour-preserving); `texture_seed` feeds
only fields this build adds. **`basic` is frozen** (§7, ruling 7): it stays registered and is not merged; no phase
is required to keep it working beyond Phase R, which uses it once as the oracle for I1 (the layer-off `azimuthal`
against `basic`, field for field). Where a later phase would need work to keep a `basic`-parametrised test green,
the test is narrowed to `azimuthal` and the decision says so.

---

## 2. Templates

**A template is a named galaxy: an input set, its seeds, a camera, an instrument, and optional pins.**

- **Inputs and seeds:** the seven controls, the merger list, the five seeds.
- **Camera and instrument:** the default view, filter set, distance and pixel scale (NGC 4414: the goal image's
  inclination and framing, the Hubble broadband set; the Milky Way: face-on, rgb).
- **Pins:** measured structure of *that* galaxy that overrides the layer's draw — the Milky Way's arm segments from
  the maser fits, its bar angle; NGC 4414's missing bar. A pin replaces a realisation with a measurement; it never
  touches a law.
- **`milky_way` is today's defaults exactly** (gate: bit-identical). **`ngc_4414`'s inputs are fitted** to its
  measured properties by a bounded offline search, the residuals published: what the seven controls cannot reach is
  a finding to record, not a number to force (B5).
- The viewer lands on `milky_way` and carries a switcher; "Edit galaxy" starts from the template's inputs.

---

## 3. How the sessions run: Opus leads every row, Fable is called at four gates

The protocol is `GALAXY_PLAN.md` §5's and `RESUMING.md`'s: one row, one `session-NN` branch, one `--no-ff` merge,
the suite's own `EXIT=0` line gating it, the tag at close, `verify_clone` after. Numbers are sequential and taken
when written: decisions from **D212**, debts from **#132**, acceptance rows from **38**.

### 3a. Why Fable is not the lead anywhere

Reading, building, re-pinning, running suites and writing records were most of what a Fable lead spent at S51–S52,
and none of it needs Fable. What did need it was small: choosing the form of a ruling where the physics is subtle,
and judging whether a build means what its ruling says. **So the judgment that can be made now is made in this
document** — the amended rule texts (Appendix A), the classification of every existing draw (Appendix B), and each
phase's ruling written out in §5 — **and what cannot be made until something is read or built is a gate.**

### 3b. The four Fable gates

| Gate | When | What Fable is asked | Why it needs Fable |
|---|---|---|---|
| **G1** | End of Phase R, before its merge | Do the invariants I1–I5, as tested, mean what §1d says? Is anything labelled synthetic that is physics, or the reverse? | Every later phase stands on this interface; a wrong invariant is silent |
| **G2** | Phase P2, after the reading, before the build | The equations of the steady shock to integrate, the treatment of the sonic point, the fallback where no shock forms, which pattern speed a ring uses when modes differ | The one place the build derives new physics from papers |
| **G3** | Phase P2, after the build, before its merge | Does the solver reproduce the published profile for the right reason? Are the retired constants' checks honest? | A solver can match one curve and be wrong |
| **G4** | The audit (S67) | The verdict on the findings list an Opus audit assembles | An audit by the builder's own model is rule B3's "check that takes your own path" |

**A conditional gate** opens only when an Opus lead hits a stop condition (§3d).

### 3c. How a gate is run, and its budget

- The Opus lead writes `docs/HANDOFF_S<NN>.md`, **150 lines at most**: what was read or built (a table), the draft
  ruling or the review findings (an Opus reviewer agent's, for G1 and G3), the numbered questions, and at most five
  file ranges Fable may need. The convention is the existing one (D190–D192).
- The owner runs the gate as one short Fable turn on the same branch. **Fable reads the handoff and the named
  ranges only**: no exploring, no suite, no agents, no records. It appends "Fable's answer", **80 lines at most**:
  the ruling in final wording with its predictions, or the verdict with the changes required.
- The Opus lead transcribes the answer into `DECISIONS.md`, attributed, builds or fixes to it, and deletes the
  handoff at close.

### 3d. The Opus lead's stop conditions

An Opus lead **stops, closes partially (C2d) and writes a handoff** if: a ruling here cannot be followed as written;
a number moves in the layer-off acceptance table; a source contradicts what this plan assumed; a gate cannot be met
without changing what is measured; or a probe contradicts a prediction this document states. It does not improvise
a ruling on physics.

### 3e. The reading agent's brief (Opus, read-only, parallel, one question each)

State the question and why the model needs it. Then the rules, verbatim: a number is written only if read on a
fetched page, tagged `[verified: author year, journal or arXiv id, section or table, URL]`; each citation says what
fraction it covers; what the quantity *is* (definition, mask, resolution) is stated; anything recalled is tagged
`[recall — NOT READ]` and kept out of the summary table. Output: one Markdown note in the scratchpad with a summary
table, per-source notes, what could not be read, and a recommendation with named alternatives. The lead assembles
the notes into `docs/READING_<TOPIC>.md`.

### 3f. The building agent's brief (Opus, `isolation: worktree`)

- **First step:** `git merge --ff-only session-NN` (a worktree is cut from `main`), then `tools/bootstrap.py`.
- **It reads** the ruling (this document's phase text, or `DECISIONS.md` where a gate wrote one, committed before
  launch), `RESUMING.md`'s "Writing a stage", and the files it owns. **It owns a named, disjoint set of files**; a
  failure in another agent's file is reported, not edited.
- **It neither pushes nor writes** `DECISIONS.md`, `GALAXY_INPUTS.md`, `RESUMING.md`, `BRIEF.md`, `GALAXY_PLAN.md`.
- **Predictions are read before they are judged** and nothing is changed to make one hold (B4, B5). A re-pin
  carries `# S<NN> (D<n>): was <old>`; a failure the change does not explain is reported, not re-pinned.
- **It does not run the whole suite** while another agent or the lead does; the lead runs it once on the combined
  state. A stage's restricted view answers False for an undeclared constant: declare what is read.
- **Its report:** branch and commits, files, every re-pinned number before and after, each prediction held or
  failed, the spec summary line, what was not done.

### 3g. Every phase

Probe before build. The instrument before the thing it certifies (B1). Cold timings when a stage's cost changes
(B2). A picture gate from Phase 0 on: the goal metrics and a capture recorded in the phase's decision. An Opus
reviewer agent reads each builder's diff against the phase's gate before the lead merges it.

---

## 4. Reconciled: what the repository already has (2026-10-03, after S52)

| This plan needs | The repository has | Consequence |
|---|---|---|
| A gas pattern | `gas_pattern` (S51): a von Mises ridge in one arm's phase, sourced width and contrast, no offset | P1 restates it as a response to any stellar pattern; P2 derives its profile |
| Light split by age | `bright.resolve`: young, middle, old parts per ring, used by the star-first remainder | V5 exposes them as field components; no stage changes |
| Object censuses | Clouds, clusters, HII regions, bubbles, remnants, bright stars, with per-region determinism | V6 draws them at galaxy scale; L1 correlates their placement |
| A dust layer | The gas's height per ring; the heating in that geometry (S52) | L2 modulates the diffuse part only |
| Structure synthesis | Cloud interiors synthesised in the viewer from the cloud vector, below 4 kpc; its noise index unsourced (#110) | The precedent for the layer; relabelled under the layer's rules in Phase R |
| A spiral pattern speed | None (#81); the bar's only | P2 |
| The amplifier's window by arm number | `swing_weight` and the local form of X, the named alternative in `pattern.py` | P1's law needs no new source: it is that function at each radius |
| Named galaxies | Defaults only; the viewer's "presets" are camera angles | Phase T |
| A picture test | None for the React viewer (T12: no headless browser on the machine) | Phase 0, on the owner's leave to install one |
| Draws classified | Three kinds; seventeen draw sites, of which four cloud columns and the viewer's cloud noise are placements without a source (#95, #110) | Appendix B rules each; Phase R applies it |

---

## 5. The phases

Each phase states its ruling here, so its Opus lead builds to this text. "Agents" are Opus.

### Phase 0 — adoption, the rules, the instruments (S53)

**Recorded (D212):** the owner's answers to §7. **Rules amended** to Appendix A's wording, verbatim. The absorbed
entries of `RESEARCH_AREAS.md` (directions a–h) and `VIEWER_TASKS.md` (T1, T5–T8, T12, T16, T28) point here.

**The instruments (B1).**
- `tools/goal_metrics.py`: on any image — a goal or a capture — the radial colour profile, the azimuthal Fourier
  amplitudes m = 1–8 by radius after deprojection, the arm–interarm contrast in the blue channel, the dark-lane
  covering fraction, the power-spectrum slope of the unsharp-masked image between stated scales, and the count of
  point sources above a threshold. Tested on synthetic images of known spectra. **Display targets, not rows.**
- T12: the React viewer captured at fixed cameras per template, on a headless browser the owner has allowed
  (§7, ruling 6). The goal pictures are read from `docs/goals/` where present; the baseline table records their
  numbers, never the pictures.

**Development-only tools (§7, ruling 10):** Pillow in the Python dev group, Playwright in the frontend's dev
dependencies; neither is imported by `model/galaxy/`.

**Agents:** builder A (`goal_metrics` and its tests), builder B (T12's harness). **Gate:** the metrics return known
values on synthetic inputs; a baseline table — both goals, both of today's renders — in D212.

### Phase T — templates (S54) — the owner's item 1 and list item 10

**Reading:** NGC 4414's distance, inclination, position angle, rotation speed, stellar and gas mass, star formation
rate, scale length, morphological class, bar classification, each with its coverage.

**Build.** `galaxy/templates.py` (the two templates as data, every number tagged); `tools/fit_template.py` (a
bounded search of the seven controls against the measured properties, residuals table committed);
`/api/templates` (metadata only, D4) and `template=` on every route that takes inputs; the viewer's landing on
`milky_way`, the switcher with model-made thumbnails, the template's camera and filter set, and "compare with a
picture" beside the render at a stated band and scale (T16 ii) — **the picture is a file the user picks from disk;
none is bundled or committed** (§7, ruling 5).

**NGC 4414's five checks (§7, ruling 8).** The reader fixes a window for each of about eight measured properties
**before any model output for the template exists** (blind, D113). The fit uses some — rotation speed, scale
length, stellar mass — and **five the fit never sees** are the checks — by default gas mass, star formation rate,
integrated colour, absolute magnitude and the rotation curve's shape, the lead choosing from what the reading
supports. They are reported in their own table beside the 37 rows, never among them, judged with the layer off; a
failure is a recorded miss with its debt (B5), not a reason to refit.

**Gate:** `milky_way` reproduces the defaults bit for bit; the fit's residuals are published and none is tuned
away; the five checks read and recorded, pass or miss; a timings row; vitest on the switcher; a capture of each template beside its goal.

**Agents:** one reader; builder A (model, API, fit tool); builder B (viewer).

### Phase R — the separation (S55) — the owner's item 2 — **gate G1**

**A behaviour-preserving restructure: with the layer on, every published number is bit-identical to S52.**

1. `synthetic` joins the provenance vocabulary; `FieldDecl` gains `stands_in_for`, `conserves`, `statistic`,
   required for synthetic fields; `texture_seed` joins the seeds and binds at the layer's earliest reader.
2. `model/galaxy/layer/`: **the noise primitives, built and tested first** — a point-evaluable lattice noise keyed
   by an integer hash of seed, cell and octave, written in 32-bit integer arithmetic so a GLSL twin can match it
   (V7); octave shaping to a stated spectral slope; a shear transform; a unit-mean log-normal map normalised per
   cell. Tests: determinism at a point, mean, measured slope, anisotropy under shear, committed test vectors.
3. `compose`, the `layer` switch through `run`, the API and `galaxy.specs`; the rules I1–I5 as tests.
4. **Appendix B applied**: the four cloud columns and the viewer's cloud noise relabelled synthetic with their
   three declarations (the statistic "none read" is a debt, not an excuse: #95 and #110 stay open); every other
   site keeps its kind. **No stream changes its seed or its value.**
5. `basic` as the oracle, once: the layer-off run of `azimuthal` equals `basic` field for field (I1's independent
   check). `basic` is then frozen and not merged (§7's ruling 7); if the two differ, that is a finding for G1.

**Gate:** bit-identical outputs with the layer on; I1–I5 green; the layer-off acceptance table read once and
recorded (rows 35 and 37 move to their uniform-placement values and then stay). **Then G1.**

**Agents:** builder A (primitives, tests, vectors); builder B (provenance, `FieldDecl`, graph, switch); builder C
(Appendix B's relabels); a reviewer whose findings go into the handoff.

### Phase V5 — light by age in the field (S63) — the owner's item 4, first part

`/api/render` returns `stars_young`, `stars_middle`, `stars_old`, each through the curves on its own and placed by
its own weight (the gas contrast, `sfr_modulation`, the stellar contrast), summing to `stars` per ring and filter
to rounding; the field mode draws the three. No stage changes.

**Gate:** the closure; the arm–interarm colour difference measured before and after (goal metric); payload and
timings. **Agents:** builder A (render route and its tests), builder B (viewer).

### Phase V6 — the censuses at whole-galaxy scale (S64)

- **Clouds as extinction:** the census rasterised by window and level into an opacity the march composites at the
  clouds' height; the ring's diffuse dust reduced by the clouds' share so each ring's dust mass is unchanged.
- **HII regions as knots:** each region's line light through the set as a point, sized by its bubble when
  resolved; the smooth Hα layer reduced by what the points carry.
- **Clusters with their half-mass radius** (T6). *Ruled here:* a Plummer profile, whose scale is the published
  half-mass radius over 1.305 (the sphere's own geometry) `[inferred]`; a King profile needs a concentration the
  model does not publish and is the named alternative.
- **Bright stars by tiles** to 10⁶ (T28's windowed request); **the depth-aware composite** (T5).

**Gate:** each closure (dust mass per ring, Hα per window, points plus field equal the render); the frame-time
readout; goal metrics (dark covering fraction, point counts). **Agents:** three builders, one per group.

### Phase P1 — several modes at once; the gas follows any pattern (S56) — list items 1 and 2

**Ruled here (a conditional gate opens only if the probe contradicts it).**
- **The law.** At each radius the weight of arm number m is the existing `swing_weight` evaluated at the *local*
  swing parameter X_m(R) — today's named alternative in `pattern.py` becomes the law; no new constant. m runs over
  the closed set 2–6.
- **The power is the sourced power where the disc amplifies, less where it does not; the peak is not conserved.**
  At each radius the modes' power is the sourced power times the disc's gain, the gain capped at one:
  A_m(R)² = A² · w_m(R) / max(1, Σ_k w_k(R)), A the published `arm_contrast`. Where Σ_k w_k ≥ 1 the ring carries A²
  whole, split by the weights; below 1 the ring carries Σw · A², falling continuously to zero where the amplifier
  is dead; no ring is normalised up. One fully amplified mode returns today's field exactly. **The modes saturate
  together** where their peak would reach the mean: s(R) = min(1, (1 − b(R)) / Σ_m Ã_m(R)), a law of the pattern
  stage, published as `arm_saturation`; no floor, no renormalisation after composition. *(Amended at S56's gate,
  D215, ruling by Fable: it read "The amplitudes satisfy Σ_m A_m(R)² = A² … how it is split", which has no solution
  on the rings no mode reaches and makes negative densities in a sixth of galaxies.)* With one pitch the field
  is 1 + Σ_m A_m(R) cos(mχ − θ_m) + bar, χ = φ − ln R · cot i: one rigid winding whose azimuthal profile changes
  with radius, never two pitches, until P4.
- **The realisation (synthetic):** each mode's phase, on `texture_seed`; one pitch for all modes until P4. *(G1, D214: today there is no
  phase draw at all — a fixed convention, ln R · cot(pitch); this is a new draw, and the convention is retired.)*
- **The gas.** With ψ = (c − 1)/A the stellar pattern scaled to unit amplitude, the ridge is v = exp(κ ψ) over its
  ring mean (a fixed quadrature on the ring's cells), κ as S51 has it; the amplitude a(R) keeps S51's rule, the
  mask being the cells where ψ exceeds the level that encloses the same share of the ring the 1.5 kpc mask did.
  **With one mode this is S51's field to 1e-9: the regression gate.**
- **The arm number's draw retires** (it becomes the split of power); the pitch's, the amplitude's and the bar's
  scatter stay seeded.

**Reading (a check, not an input):** Fourier amplitude spectra of spirals by arm number and radius, to set beside
the law's split in the decision.

**Gate:** ring means 1 to 1e-12 on every ring; the single-mode regression; the m = 2–6 cosine amplitudes recovered
from the composed field equal the published ones (the bar's m = 2 term added at its taper) to 1e-9 on every
ring, no exclusions; the minimum over cells ≥ 0 on every seed the suite draws; I1–I3; the goals' azimuthal
spectra beside the render's *(the amplitude and positivity items are the gate's, D215)*.

**Agents:** one reader; builders for the mode law, the realisation, the gas response, and the catalogue re-pins.

### Phase P2 — pattern speeds; the gas shock ring by ring (S57) — "level A" — **gates G2 and G3**

**Reading:** the steady spiral shock (Roberts 1969; Shu, Milione & Roberts 1973); its width and offset (Gittins &
Clarke 2004; Kim & Ostriker 2002, partly read at S51); pattern speeds of transient modes. **Then G2.**

**The frame G2 rules inside.** A pattern speed per mode (its corotation at the mode's radius), closing #81's first
half; the young-star cut replaced by the crossing time it gives. `gas_shock`: per ring, the steady one-dimensional
isothermal flow through the composed potential in the rotating frame — a fixed-step integration with a bisection on
the sonic point and the isothermal jump (A1: the step count is known in advance) — publishing the ridge's profile
across an arm. The profile replaces the von Mises: its width, contrast and **offset** are derived.

**The instrument first:** the solver reproduces a published profile at the source's parameters before the model
uses it. **Declared in advance:** where the forcing is too weak for a shock the response is the linear one.

**Consequences:** `GAS_ARM_WIDTH`, the mask and the two contrast constants stop being inputs; PHANGS's ratio of
means becomes a check, a disclosed row (its numbers have been printed, D113). #129 and #131 are re-ruled. D210's
ruling 3 is superseded where the physics signs the offset. **Then G3.**

**Agents:** two readers; builder A (solver and instrument); builder B (integration and re-pins); a reviewer.

*(Ruled at gate G2, S57, D216; ruling by Fable. The frame is Ω_p(R) = Ω(R) for every arm mode — the plan's
"corotation at the mode's radius" with amplitudes set ring by ring — so no gas flows through an arm and **no arm
shocks**: no sonic point, no jump, no bisection, no fallback. `gas_shock` is the steady corotating response under
uniform potential vorticity, ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(mχ − θ_m), the ν → 0 member of the shock's own
equations; its offset is zero, so D210's ruling 3 stands, derived; the young-star cut is the arm's lifetime, not a
crossing time. The instrument is the smooth-branch solver for general (ν, x, f), certified on Sormani et al.
2017's no-shock threshold and the linear limit; the shocked branch is P3's.)*

### Phase P3 — the bar: a body, an absence, its lanes (S58) — list items 6, 9, 7

**Reading:** bar light fractions, axis ratios and profiles from the S⁴G decompositions; the bar fraction against
disc properties and a disc stability criterion; the gas lanes' offset and curvature.

**Ruled here.**
- *The body:* inside the bar radius the ring's **old** stars are concentrated along the bar's axis by a mean-one
  two-fold ridge whose axis ratio and light share are the sourced medians; the young stars and the gas follow the
  gas response (P1), which now feels the bar's potential too. No ring total changes.
- *The absence:* presence is derived from the sourced stability criterion. **A seeded residual is drawn only if a
  galaxy-to-galaxy scatter is read (D210's amendment); otherwise none, and a debt.** An unbarred galaxy publishes
  NaN for the bar's fields (D164); rows 15–17 are not applicable to it and are unchanged for the Milky Way, whose
  template pins it barred.
- *The lanes:* a template curve with sourced parameters, **synthetic**, standing in for two-dimensional gas flow in
  the bar's potential (§8, level B).
- *The shocked branch (deferred here from P2 at gate G2, D216):* the bar has a real pattern speed, so gas flows
  through its potential and the steady flow can shock. If P3 uses the one-dimensional shocked solution — the
  sonic point in Gittins & Clarke's regularised variables, the isothermal jump, a bisection on the sonic point's
  phase alone — **it is certified before the model calls it** on Kim, Kim & Kim 2014's Table 1 under both
  x = 0.1450 and 0.1458, and on Shu, Milione & Roberts 1973's rows B–D (`READING_GAS_SHOCK.md` Part A, A3).
  *(Amended at S58's conditional gate, D217; ruling by Fable: the one-dimensional steady shocked branch assumes a
  tightly wound forcing; a bar is the opposite limit — k R = 2, a two-dimensional x₁/x₂ flow — so it is not the
  bar's instrument either. It stays deferred with no user. In this phase "the gas response feels the bar's
  potential" is the synthetic lanes, blended as D216's item 8 blends the bar; presence is Fujii et al. 2018's
  formation time against the disc's age, with a template pin `bar_present` for a measured class.)*

**Gate:** ring totals unchanged; rows 15–17 unchanged for the Milky Way; the m = 2 Fourier amplitude inside the
bar against the sourced value. **Agents:** two readers; builders for the body, the presence and its rows, the lanes.

### Phase P4 — pitch along an arm; the templates' pins (S59) — list item 8, first half

Segments of seeded length and pitch change from the measured distributions (Honig & Reid 2015, read at S51;
Díaz-García et al. 2019), continuous in phase: synthetic. The Milky Way's pins — arm segments and kinks from the
maser fits (Reid et al. 2019), the bar's angle — and NGC 4414's (unbarred, flocculent). **Gate:** the pinned arms
pass through the measured loci; a galaxy without pins is unchanged. **Agents:** one reader, two builders.

### Phase P5 — the arms as a census of pieces (S60) — the owner's ruling of 2026-10-05 (D219)

*Inserted after S59.* The frames set beside the goals showed what #138 and #152 had recorded as conflicts: a sum
of cosine modes on one winding makes many broad, equal, faint arms, holds no arm that could be pinned, and with
S59's kinks on common rings reads as ripples. The owner was given three ways out — fewer and stronger modes; a
ridge per arm; arm pieces as a census — and ruled: **"Take C, don't reorder the sessions."**

**Ordered here (the owner).** The stellar arm pattern is built from **arm pieces**: each a ridge along its own
logarithmic locus, with a start, an extent, a pitch, a width across it and an amplitude along it. A few long
chains of connected pieces make a grand design; many short ones make a flocculent disc. **The arm-number law keeps
its place as the budget**: how much arm power a ring carries is P1's law; where on the ring it lies is the
pieces'. The pieces are the layer's (synthetic on `texture_seed`, each statistic sourced: S59's reading for length
and pitch, as the sources measure them — per arm; this phase's reading for width, number and class). A template
may pin its pieces and its arm class: the Milky Way's from the maser fits where they are measured, NGC 4414
flocculent.

**Ruled at S60's conditional gate (D219; ruling by Fable — the decision holds it whole, this is its outline).**
- *A piece:* a ridge on its own logarithmic locus (start, pitch, azimuthal extent), a Gaussian across it of
  FWHM(R) = 0.53 h (0.27 + 0.73 R/(2h)), h the checkpoint-1 scale length; flat along it and tapered over one
  width at each end (a declared placeholder). *A chain:* pieces joined end to start on S59's draws, per arm; its
  length normal, 273° ± 143° or 244° ± 131°, never under 90°.
- *Class, derived, no draw:* barred, two chains from the bar's ends and more wherever the law's power-weighted arm
  number n(R) exceeds the chains crossing a ring; unbarred, chains by n(R) alone; **flocculent by pin only**
  (`arm_class`): single pieces of 37°–105°, n(R) of them crossing each ring.
- *The budget, in expectation:* one amplitude B(R) for the pieces crossing a ring, set so that the expected ring
  variance equals ½ Σ A_m(R)², analytically, from the census's statistics; never a division by a realised power;
  positivity by P1's saturation. The split by arm number is a disclosed check of the composed field.
- *The forcing:* piece by piece and Fourier term by term, × |m|/(X (|sin p_j| + |m| h_z/R)): each piece's own pitch
  and the exponential layer's exact thickness factor, h_z the checkpoint-1 scale length over 7.3. ε keeps the
  disc's pitch.
- *The gas between rings:* a ring's profile carried to a point along the pieces' loci, its error against a direct
  solve measured and pinned; over 1 % on a star-forming gap, the ring step is halved there.
- *Retired:* the modes' phases and `arm_phases`, the common winding and `arm_segment`. *Kept:* the amplitudes (the
  budget), the pitch, the bar. A table `arm_piece`. Layer off bit for bit.
- *The Milky Way's pins:* Reid et al. 2019's four major arms and the Local arm as chains over their measured
  ranges, continued by drawn pieces; no pinned chain tied to the bar.

**Gate (as ruled):** ring means 1 to 1e-12; the expected ring power equal to the budget to 1e-10 and the realised
power published, its scatter pinned; the minimum ≥ 0 on every suite seed by the saturation only; layer off
bit-identical; I1–I5; the gas converges under D216's criterion or raises; the gas map's mid-gap error pinned; the
pinned loci within 0.1 width by construction, **and the gas's and young stars' crest against the maser loci
within the masers' σ as a disclosed check with its null**; the thickness factor's hand test; the m-split check;
the goal metrics read beside the render's.

**Agents:** two readers; a model builder; re-pin builders of their own once the model is final; a viewer builder;
a reviewer.

### Phase L1 — clustered censuses; young stars near where they formed (S61) — list items 3 and 5

**Reading:** two-point correlation functions of young clusters and molecular clouds, and how they flatten with
age; association sizes against age.

**Ruled here.** The synthetic field `census_clustering` has unit mean in every level-0 cell (so D60 and I2 hold)
and multiplies the clouds' expected counts; clusters inherit it through their clouds; the bright catalogue's
20–100 Myr stars follow the same field with its finest octaves dropped as age grows. Its slope and amplitude are
the sourced correlation function's; where the reading gives a range, the median, the range in the about.

**Ordered here at gate G1 (S55, D214).** *The ring-first draw:* a ring's objects — its count and every per-object
draw — are drawn on a ring stream before the layer places them; the layer assigns the cell and the azimuth. After
it `tests/test_layer.py::CENSUS_STATISTICS` is empty and the realised ring totals are identical with the layer on
or off (I2's second half). `cloud_texture` moves to `texture_seed`; the cloud's offset is bounded to its cell or
the cluster is binned by its cloud's ring; whether `cloud_height` is a placement or a sample of the vertical
profile is ruled. D60 (per-region determinism) must survive it: a cell's objects from the ring's draw and a
fixed allocation, without materialising the ring's other cells' objects.

**Gate:** the census's measured correlation function returns the sourced slope over the sourced range; I2; D60's
per-region tests; the layer-off acceptance table bit-identical. After the ring-first draw: the realised ring totals identical on and off.

**Added 2026-10-05 (D219; the reading is `READING_CLUSTERING.md`, taken at S59's close).** Put to L1's gate: whether
`census_clustering` is a field of its own or the coarse scales of L2's `gas_fluctuation` — one field, so that
clouds stand where the gas is dense and young stars are displaced from it by their age (clusters leave their
clouds in 2–6 Myr and about 200 pc as read), and the dust and the star complexes of a flocculent disc alternate
instead of ignoring each other. The census's correlation is measured as the sources measure it — uniform randoms
in a footprint — on the finished census, arms included: no source measures it against an arm-modulated disc.

**Agents:** one reader; builders for the field and clouds, the bright stars, the re-pins.

### Phase L2 — structure between the clouds; spurs (S62) — list items 4 and 8, second half

**Reading:** column-density power spectra of atomic gas and dust in nearby discs and their break at the disc's
thickness; log-normal column widths against Mach number; feather spacing.

**Ruled here.** `gas_fluctuation` is published as **parameters**, each from the model or a source and none chosen
for the picture: the spectral slope (sourced), the log-normal width (the sourced relation at the ring's published
Mach number), the outer scale (the gas's published height), the shear stretch (the disc's own shear and a sourced
lifetime), the seed. It has unit mean per cell and modulates the **diffuse** dust only; the clouds stay the
census's. A Python reference evaluator and **committed test vectors a GLSL twin must match**. Spurs: spacing
derived from the ridge's Jeans length, phases synthetic.

**Gate:** unit mean per cell; the evaluator's measured spectrum; the vectors; I1–I3.

**Added 2026-10-05 (D219).** Put to L2's gate: whether the fluctuation may take a ridged, filamentary form beyond
its sourced spectrum and shear — a choice of look with no measured statistic, declared as one if it goes in.
The spurs attach to P5's pieces.

**Agents:** two readers; builder A (evaluator, vectors); builder B (spurs).

### Phase V7 — the layer in the viewer (S65)

The GLSL twin of the noise (matching the vectors to 1e-5); the diffuse dust modulated per pixel in the march; the
spurs; the bar's body and lanes; the "physics only" switch. **Added 2026-10-05 (D219):** the young starlight of
V5 — unresolved, and most of what a blue-white complex is — modulated per pixel by the clustering field, its
finest scales dropped with age as L1 rules for the bright catalogue; unit mean per cell keeps each ring's light. **Gate:** the vectors; the frame-time readout; each
ring's dust on screen unchanged by the layer (`__galaxygenFrameSum` on a dust-only frame). **Agents:** two builders.

### Phase V8 — the display defaults, the instrument, the goal captures (S66)

T1 per template, from the owner's tuning. *Ruled here (T9):* a point's sprite is scaled by the template's distance
and the instrument's pixel scale, both carried by the template. NGC 4414's instrument look; committed captures of
both templates beside their goals; the goal metrics' final table against Phase 0's baseline. **Agents:** one builder.

### Audit V (S67) — **gate G4**

Opus agents, blind to the builders' reports: every citation entered since S51 read again; every synthetic field's
conservation and statistic re-measured; I1–I5 re-derived, not re-run; a picture traced feature by feature to a
published field or a layer field; the register pass; the goal metrics table set against §0's "what will remain".
The lead assembles the findings. **Then G4:** Fable's verdict on each, and the fixes ordered.

---

## 6. Sequence

| S | Phase | Deliverable | Blocked by | Lead | Fable |
|---|---|---|---|---|---|
| **53** | 0 | Adoption (D212), the rule amendments, `goal_metrics`, the picture test, the baseline table | — | Opus | — |
| **54** | T | Two templates, the fit and its residuals, `/api/templates`, the switcher, compare-with-goal | 53 | Opus | — |
| **55** | R | The fourth kind, `layer/` and its primitives, the switch, I1–I5, Appendix B applied | 53 | Opus | **G1** |
| **56** | P1 | Several modes; the gas follows any pattern | 55 | Opus | if the probe contradicts §5 |
| **57** | P2 | Pattern speeds; the shock per ring; #81, #129, #131 re-ruled | 56 | Opus | **G2, G3** |
| **58** | P3 | The bar's body, its absence, its lanes | 56 | Opus | — |
| **59** | P4 | Pitch segments; the templates' pins | 56, 58 | Opus | — |
| **60** | P5 | The arms as a census of pieces; the forcing corrected for the disc's thickness (inserted 2026-10-05, D219) | 59 | Opus | a conditional gate |
| **61** | L1 | Clustered censuses; young stars near birth | 55, 60 | Opus | — |
| **62** | L2 | The gas fluctuation field and its twin's vectors; spurs | 55, 57, 60 | Opus | — |
| **63** | V5 | The field's light by age | the model phases (the owner's order) | Opus | — |
| **64** | V6 | Clouds, HII knots, clusters and bright stars at whole-galaxy scale | 63 | Opus | — |
| **65** | V7 | The layer in the shader; the physics-only switch; the young light by the clustering field | 62, 64 | Opus | — |
| **66** | V8 | Display defaults, instrument look, goal captures | 65, the owner's tuning | Opus | — |
| **67** | — | Audit V | 53–66 | Opus | **G4** |

55 → 56 → {57, 58} → 59 → 60 is the hard chain on the model side; 61 and 62 stand on 55's primitives and on 60's arms. **The model's
phases come first and the viewer's follow, on the owner's word (§7, ruling 9)**; §5 keeps the phases in the order
they were written, and this table is the order they run. **Fable's whole share is four short turns** (G1–G4), plus
any conditional gate a stop condition opens.

## 7. The owner's rulings (2026-10-03; S53 records them as D212)

| # | Question | The owner's answer |
|---|---|---|
| 1 | Adopt the plan and its numbering, Opus leading every row, Fable at the four gates | **"adopt the plan"** |
| 2 | The fourth kind, *synthetic*, and the layer's five rules, in Appendix A's wording | **"yes"**, after asking what the quantity is: a label for randomness that places structure the physics cannot, apart from measured scatter and from sampling |
| 3 | `RENDER_PHYSICS.md` §8 and rule D5 amended, in Appendix A's wording | **"approved"** |
| 4 | Templates (rules A5 and D1): the viewer lands on `milky_way`; a template may carry pins | **"approved"** |
| 5 | The goal images committed to this public repository | **"don't commit"**: `docs/goals/` is ignored by git; the pictures are the owner's local files |
| 6 | A headless browser installed for the picture test | **"yes"** |
| 7 | `basic` and `azimuthal` as one model with the layer switch | **Not merged: "seems better to just ignore basic from now on, not worth spending effort on merging it unless there's something it does better than azimuth".** `basic` is frozen: no new work targets it (§1e) |
| 8 | NGC 4414's checks: a small table of blind windows, or display only | **"yes, do 5"**: five checks, fitted apart (Phase T) |
| 9 | Pictures first (V5, V6 before Phase R)? | **"no, lets finish model part first"**: §6 reordered |
| 10 | The dependency rule stays numpy-only | **"ok"**: the runtime stays numpy-only; two development-only tools are allowed — Pillow, to read pictures in `goal_metrics`, and Playwright, for the picture test |
| 11 | *(2026-10-05, after S59; D219)* The arms: fewer and stronger modes (A), a ridge per arm (B), or arm pieces as a census with the arm-number law as each ring's budget (C) | **"Take C"**: Phase P5, inserted at S60 |
| 12 | *(2026-10-05; D219)* The picture-facing phases ahead of L1 and L2? | **"don't reorder the sessions"**: the order stands; P5 goes in ahead of L1 (the lead's reading of the two rulings together, told to the owner) and every later phase runs one session on |

---

## 8. Scope boundary — recorded as decisions

**Level B, two-dimensional gas in the rotating potential,** is not built. It would give real bar lanes and shock
ridges at 10–100 s a galaxy `[inferred]`; the bar's lanes are a synthetic template until the owner orders it, most
plausibly as a precomputed table for the bar alone.

**Level C, self-gravitating, cooling, star-forming gas,** is not built and cannot run at generation time. Flocculence
and filaments are the layer's. A shipped library of simulations stays `RESEARCH_AREAS.md` §1's last resort.

**A live stellar disc** (arms that emerge) is not built: the pattern's shape stays laws plus realisations.

**#128's placement half, the remaining viewer debts (T9's ruling aside: T10, T11, T13–T15, T17–T19, T24–T27) and
the pinned model debts** are not in this build unless a phase names them.

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
unsourced draw "synthetic" to excuse it: a synthetic field still cites its statistic, or carries a debt.

**Do not force NGC 4414's inputs.** What the seven controls cannot reach is recorded.

**Do not make the gas shock a convergence loop.** Fixed steps, a bisection, a declared fallback (A1).

**Do not rebuild what exists:** the light by age, the censuses, the dust's layer and the gas ridge are there (§4).

**Do not spend a Fable turn on reading, building, re-pinning, a suite or a record**, and do not improvise a physics
ruling in an Opus session: stop and write the handoff (§3d).

**Do not reserve number blocks.**

---

## Appendix A — the amended rule texts (entered verbatim at S53 if the owner adopts §7's rulings 2–4)

**RULES.md A10, the table gains a row and the rule a paragraph:**

> | **Synthetic** | Function of inputs **and the layer's seed**, standing in for physics the model does not compute | No | **Yes** |
>
> **A seeded quantity is a measured scatter between galaxies or the sampling of a derived distribution. A synthetic
> quantity is a realisation the physics cannot place** — where an arm's phase, a cloud complex or a filament lies —
> drawn from measured statistics on the randomness layer's own seed. It conserves the total it redistributes, cites
> its statistic, names the physics it stands in for, and is evaluable at a point. No acceptance row reads one, and
> switching the layer off changes no ring total. *Added 2026-10-03 on the owner's word* `[verified: DECISIONS.md D212]`.

**RULES.md A5, appended:**

> **A template is a named input set with the same standing**: its inputs are fitted to that galaxy's measured
> properties and the misfit is published; its pins are measurements of that galaxy which replace the randomness
> layer's draw and never a law. The default template is the Milky Way, whose inputs are the defaults.

**RULES.md D1, the landing clause becomes:**

> the viewer lands on the Galaxy view of **the default template**, every checkpoint confirmed at its inputs; **a
> switcher selects another template**; and "Edit galaxy" opens the staged process from the template's inputs with
> the confirmations kept.

**RULES.md D5 becomes:**

> **D5. The viewer computes no physics and persists no generated object.** It may evaluate a function the model
> publishes — its form, its parameters, its seed and its committed test vectors — as it evaluates the cloud
> vector's interior; it adds no structure, no parameter and no seed of its own. Replacing the viewer means
> reimplementing against the same endpoints and the same vectors.

**RENDER_PHYSICS.md §8 becomes:**

> **Every visible feature traces to a published field, or to the randomness layer: a synthetic field the model
> publishes, on the model's seed.** The failure mode is unchanged — a galaxy-flavoured noise generator with a
> physics model bolted to the side — and what keeps the layer from being one is that it is the model's, it
> conserves every total, its statistics are sourced, it names the physics it stands in for, and it can be switched
> off to show the physics alone.
>
> Specifically forbidden:
> - frame-seeded or time-seeded noise (it would shimmer, and it is not a structure)
> - detail the model does not publish: structure, parameters or seeds of the viewer's own
> - colour applied for appearance rather than derived from the filter integral
> - a synthetic field tuned to a picture rather than to its cited statistic

---

## Appendix B — every draw in the model, classified (ruled 2026-10-03; Phase R applies it)

Read from the repository at S52's merge: every `ctx.rng` and `_seeds.rng` call site under `model/galaxy/stages/`.
**Scatter** is a measured scatter between galaxies; **sampling** is the sampling of a distribution the model
derives or a source gives; **synthetic** is a placement with no physics behind it. Phase R changes labels and
declarations only: no stream changes its seed or its value.

| Site | The draw | Kind | Note |
|---|---|---|---|
| `nucleus.py` `black_hole` | The black hole mass's residual about its relation | scatter | stays seeded |
| `globular_clusters.py` `residual` | The cluster system's mass residual | scatter | stays seeded |
| `pattern.py` `fast_bar` | The fast-bar ratio | scatter | stays seeded; rows 16–17 statistical |
| `pattern.py` `pitch` | The pitch about the shear trend | scatter | stays seeded |
| `pattern.py` `arms` | The arm number, weighted by the swing window | scatter | **retires at P1**: the window becomes the split of power among modes |
| `pattern.py` `arm_contrast` | The arm amplitude's class scatter | scatter | stays seeded |
| `pattern.py` `bar_contrast` | The bar amplitude's scatter | scatter | stays seeded |
| `systems.py` `count`, `radius`, `age`, `birth_radius`, `height`, `mass`, the level streams | A star from the derived distributions | sampling | stays seeded |
| `systems.py` `azimuth` | A star's azimuth from the composed weight in its cell | sampling | the draw is sampling; the weight it samples is composed (I4's placement reader) |
| `bright.py` `gamma`, `population`, `age`, `segment`, `luminosity`, `radius`, `height` | A bright star from the luminosity function and the profiles | sampling | stays seeded |
| `bright.py` `azimuth` | As `systems.py`'s | sampling | placement reader |
| `clouds.py` `count`, `radius`, `mass`, `age`, `height` | A cloud from the molecular column and the sourced mass function | sampling | stays seeded |
| `clouds.py` `azimuth` | As above | sampling | placement reader |
| `clouds.py` `source_offset`, `source_angle`, `gradient`, `gradient_angle` | Where a cloud's source sits and how its density leans | **synthetic** | unsourced (#95): relabelled, the debt stays open |
| `clusters.py` `bound` | Whether a cluster is bound, at the sourced fraction | sampling | stays seeded |
| `bubbles.py` `count` and the remnant columns | A remnant from the supernova rate and its lifetime | sampling | stays seeded |
| `planets.py` the cell streams | A system's planets from the occurrence laws | sampling | stays seeded |
| The viewer's cloud-interior noise | The log-normal interior synthesised from the cloud vector | **synthetic** | its spectral index unsourced (#110, T8): relabelled, the debt stays open |

**New in this build, all synthetic, all on `texture_seed`:** the modes' phases (P1), the pitch segments (P4), the
bar's lanes (P3, a template: no draw), `census_clustering` (L1), `gas_fluctuation` and the spurs' phases (L2).
