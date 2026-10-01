# VIEWER_TASKS — everything that remains for the viewer, in one list

Consolidated 2026-10-01 (S47) on the owner's word, from four places that each held part of it: the render contract's
open debts (`GALAXY_INPUTS.md` §11, #110–#116, #119, #120), `RENDER_PLAN_II.md` §2–§3 (S46's review and costing),
`future_ideas.md`, and what S46–S47 found or deferred. **This file is the task list; `RENDER_PLAN_II.md` keeps the
review (§1), the gates (§4) and the traps (§5), and its §2–§3 are superseded by this list.** `RENDER_PHYSICS.md` is
the contract every row is held to (§8: no frame-seeded noise, no detail below the cloud vector, no colour for
appearance). The model is pinned (the owner, 2026-10-01): a task marked **Model** needs a new published field and the
owner's leave. **The owner lifted the pin for T2, T3 and T21 on 2026-10-01 ("lift the pin for those two and implement
them first"): they are S48's, designed in D200, with `BRIEF.md` the working plan.** Costs are in sessions.

## 0. Done (for orientation)

| Session | What |
|---|---|
| S38–S42 | The contract's viewer side: the filter integral through `/api/render`, dust as three layered components, the region march (clouds, HII spheres, shells), clusters as points, the named instrument sets (D188–D192) |
| S46 | `azimuthal` the default everywhere; the field march's terracing fixed (jittered sub-samples, the box at 16 h); the viewer lands on the Galaxy view of the default galaxy, "Edit galaxy" opens the staged process (D197, D198) |
| S47 | The tuning panel: the field's display choices as sliders, today's values as defaults (D199) |
| S48 | **The model side of T2, T3 and T21**: the bright-end-complete catalogue (`/api/bright`), the per-object filter response (`filters=` on `/api/bright` and `/api/clusters`), the field's unresolved remainder (`/api/render?l_min=`), single counting by age (the clusters carry the first 20 Myr) with the closure identity to 10⁻¹³ (D200–D203). **What remains of them is the viewer's**: the star-first mode that draws these (§4), and resolving a cluster into its own stars at close zoom (the second half of T3) |

## 1. In progress

| # | Task | Waiting on | Cost |
|---|---|---|---|
| T1 | **The display defaults.** The owner finds a combination in the tuning panel (resolution cap, pixel budget, steps, sub-samples, dither, filtering, field gain and floor, white point, bloom, tone mapping, sprite size, point gain) and pastes the copy box; the session makes it the default, declares each a display choice where it is computed (A9), and adds the surface-brightness-profile gate (the rendered face-on profile against `disc_surface_brightness`) | The owner's combination | 0.5 |

## 2. The contract's open debts (RENDER_PHYSICS)

| # | Debt | Task | Needs | Gate | Cost |
|---|---|---|---|---|---|
| T2 | #114 | **Points painted through the filter set**, not a bolometric blackbody (about 2× too bright in the optical): per cluster the eight band points × mass, per star the isochrone's magnitudes | **Model** (a per-object band response) | The census summed through the set equals the render's `stars` over the same cells | 1 |
| T3 | #115 | **The young population drawn once**: a membership so the sample excludes what the cluster points carry; dissolved clusters' light handed back to the sample | **Model** (`star_cluster_index` or equivalent); after T2 | T2's closure test: sample + points = the render's `stars` | 1 (with T2 and T4: 2 for the three) |
| T4 | #113 | **The level-k stars as the point layer** below 1 kpc; the picker reads `level`, `cell`, `index` | — | T2's closure test at each level | with T3 |
| T5 | #112 | **Depth-aware composite**: the region's transmission must not darken a star in front of a cloud | — | A synthetic depth test on the pass | 0.5 |
| T6 | #116 | **Clusters with their published half-mass radius** (Plummer or King, ruled) at the levels that resolve it | A ruling on the profile | The profile integrates to the cluster's light | 0.5 |
| T7 | #111 | **The region's display budget**: the kept share returned and the field's HII faded by it, or the unbudgeted regions as points | — | The window's Hα on screen equals the census's within the share | 0.5 |
| T8 | #110 | **The cloud noise's spectral index**: one sourced constant, the octave weights derived; the pillar rule as a column condition | A reading (Larson / Heyer) | The realised mean 1 and σ as measured | 0.5 |
| T9 | #120 | **The instrument sprite's scale** tied to a stated pixel scale and distance, or ruled display | A ruling | — | 0.25 |
| T10 | #119 | **The diffuse gas's forbidden lines** as two sourced scalars drawn beside its Hβ | **Model** (pinned) | The ratios as read at S43 | 0.3 |
| T11 | §2a | **"As JWST"**: NIRCam's curves and a hexagonal PSF | A download (the owner's word) | As S42's WFC3 | 0.5 |

Debts in full: about 5 to 6.

## 3. What the review added (RENDER_PLAN_II)

| # | Task | Needs | Gate | Cost |
|---|---|---|---|---|
| T12 | **An image-level test for the React app** (`shot.py` serves the old reference client): fixed cameras, three regimes, five sets, compared to committed frames. One load reaches the generated galaxy since D198 | A headless browser on the machine | The captures exist; a changed gain fails it | 0.5 — **first, so every later task has a picture gate** |
| T13 | **The renderer survives a lost WebGL context** (five losses and a black stars regime in the app's pane; the owner's tab is the check) | The owner's observation | A forced loss, then a drawn frame | 0.5 |
| T14 | **The march's cost after S46** (96 × 8 × 6 reads per pixel at worst; ≈ 100 ms per re-march at the budget on an RTX 4070): fewer sub-samples while the camera moves, the full count at rest; the render by window | The owner's frame time (the tuning panel's readout) | `tools/timings.py` and the readout | 0.5–1 |
| T15 | **The stellar disc building up in the scrubber**: `stars_formed_history` at birth radius | **Model** (a new field) | It integrates to today's stellar mass at every epoch | 0.5 |
| T16 | **A comparison view**: (i) two seeds / models / sets side by side, or (ii) real imagery at a stated band and scale | (ii) a download | (ii) the band and scale on the frame | 0.5 / 1 |
| T17 | **The design system as designed**: 20 of 21 components unported; the tabs differ from the mockup (Preview / Science / Galaxy + overlay against Workflow / Galaxy / System / Science) | The owner's ruling on the structure | vitest on the panels; the build | 1–2 |
| T18 | **View a locked checkpoint without reopening it** (S46: `flow.goTo` treats going back as reopening; "Edit galaxy" lands on checkpoint 6's scene) | A change to the shared `interface/flow.js` | `tests/test_viewer.py`'s flow tests | 0.25 |
| T19 | **Deploy**: `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha>`; CI builds the image on every push | The owner's action | — | minutes |

Additions in full: about 4.5 to 6. Everything in §2 and §3: about 10 to 12.

## 4. A direction under review: build up from the "brightest" view (the owner, 2026-10-01)

The brightest mode draws the N most luminous stars inside the frustum (10²–10⁵; default ≈ 3 200) from a pool sized to
the footprint (200 000 target, 2 000 000 at most), exposed to its hundredth-brightest star, and nothing else.
**Measured at S47** (`/api/region`, the whole galaxy): the pool is a number-drawn sample of the galaxy's stars, about
one in 10⁵–10⁶ of them, so "brightest" is the brightest *of the sample* (`service._brightest` says so). The top 3 162
carry 86 % of a 160 000-star pool's light and 94 % of a 1 000 000-star pool's, whose single brightest star (514 000 L☉)
is 41 % of it: the pool's light is not converged at the bright end, and the pool's total is 10⁻⁵–10⁻⁶ of the galaxy's
4.9 × 10¹⁰ L☉.

| Feature | Field mode today | Brightest mode today | The finished plan |
|---|---|---|---|
| Unresolved starlight (the 4.9 × 10¹⁰ L☉ the points do not carry) | The field volume: the filter integral per cell, in its layers | **None** | The field **minus what the points carry** (T3's accounting) |
| The bulge | A Hernquist profile in the march | **None** | As field |
| Dust on the field | Extinction, scattered and thermal light, per channel, in the march | n/a | As field |
| Dust on the points | Region clouds only, and wrongly in front (T5); **never the galaxy-scale dust** | **None** | Each point dimmed by the dust in front of it (not yet a task: **T20**) |
| Ionized gas (Hα, Hβ, forbidden lines; HII regions, diffuse layer) | Field layers; resolved HII spheres in the stars regime | **None** | As field, plus the budget (T7) and the DIG's lines (T10) |
| Clouds, bubbles, remnant shells | The region march, below 4 kpc | **None** | As field, noise sourced (T8) |
| Clusters | Points below 4 kpc, bolometric | **None** | Photometric (T2), with extent (T6), counted once (T3) |
| Which stars | 20 000 sampled (whole galaxy); 60 000–1 000 000 per region | The pool's top N in the frustum, any zoom | The level's own stars (T4) |
| **Completeness at the bright end** | Not claimed (the field carries the light) | **The sample's brightest, not the galaxy's**: a real magnitude-limited view has every star above a luminosity; the pool has a random 10⁻⁵ of them | Not in the plan (**T21**, Model: count the stars above a luminosity per cell and materialise those — rule B8, do not sample what you can count) |
| Point colour | Blackbody share at T through the set (T2's 2× error) | The same; the filter-set chips are hidden in this mode, so the last set chosen applies | The object's band light through the set (T2) |
| Filter sets and instrument sprite | Five sets; Airy sprite on WFC3 | Inherited silently from field mode | As field, chosen in either mode (**T22**) |
| Exposure | Manual stops over a fixed gain | Automatic, to the hundredth-brightest star, plus stops | One rule for both (a ruling) |
| Handover by zoom | Three regimes at 25 and 4 kpc | None needed: the frustum selects | The frustum selection for points, the field under it |
| Picking a star | Yes | Yes | Yes; clusters too (**T23**) |

**What building from brightest would take** (new tasks this direction adds): **T20** the dust in front of each point
(the march's own optical depth to the star's position: a per-point attenuation, viewer-side integration of a published
field); **T21** a bright-end-complete star selection (**Model**); **T22** the filter sets and the instrument sprite as
first-class controls in the mode; **T23** clusters and their HII regions as pickable points in the mode; and the
field's light drawn *under* the selection with the selection's own light subtracted (T3's closure, which then needs T2).
Its natural order: T22 (a quarter) → the field under the points with a ruled accounting (one) → T20 (half) → T2/T3
(two, Model) → T21 (one, Model).

### 4a. What the owner was told after S49, and the choice left open (2026-10-01, recorded at handoff)

**How the light divides among the brightest N disc stars** (exact, from `bright.luminosity_function` over all ages;
89 billion living disc stars, 4.59 × 10¹⁰ L☉; the bulge not included): the brightest 100 carry 0.35 %, 1 000 2.2 %,
3 162 5.1 %, 10⁴ 10 % (each above 2.4 × 10⁵ L☉), 10⁵ 22 %, 10⁶ 35 % (above 2 900 L☉), 10⁷ 53 % (above 390 L☉), 10⁸ 72 %,
10⁹ 88 % (above 2.5 L☉), 10¹⁰ 98 %. So no small number of stars "is" the galaxy: half the light takes about seven
million stars, the star-first mode needs the unresolved field under its points, and the very top is young (the
clusters').

**What the model does not yet provide for a star-first picture** (none blocks S50's mode): **T24** a cluster resolved
into its own stars at close zoom (stars under 20 Myr exist only as cluster points; the same ordered process with
Λ = M_cluster × the luminosity function at the cluster's age); **T25** bulge stars (the bulge stays as glow; the same
process on its Hernquist profile); **T26** the faint end below 0.1 L☉ with finer cells so a close view stays
affordable; **T27** one star list — the number-sampled catalogue (which carries the planetary systems and is about one
star in 10⁵–10⁷ of the galaxy: 20 000 by default, at most 5 × 10⁶) re-keyed onto the complete list's identities, so
any drawn star can be picked and its system opened; today a bright star is named (level-3 cell, rank) and has no
system. T24–T26 are about two sessions together, T27 two to three; all four are model work beyond the two pieces the
pin was lifted for and need the owner's word. **The owner's open choice at handoff:** the star-first viewer mode first
on what exists (the session's recommendation), or T24–T26 first. The owner has ideas of their own for the viewer to
give the next session.

## 5. Not viewer work (pinned)

The model's open debts — #117 and #124 (row 37 and the gas gradient; the blind direct-method reading), #107, Audit V —
are in `GALAXY_INPUTS.md` §11 and wait for the owner's word.
