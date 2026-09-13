# Design brief — galaxygen

Design a UI for a scientific procedural galaxy generator. A working Python model
and a plain reference viewer already exist; this is a design pass over a real
API, not a concept for something imaginary. Repo:
`https://github.com/mcha291/galaxygen` — run `uv run python -m galaxy.api` for a
live server on `127.0.0.1:8017`.

**Audience: two, in this order.** An astronomer or astronomy-literate enthusiast
who wants to see what a galaxy's parameters imply, and a game or worldbuilding
designer who wants a galaxy full of star systems. Design for the first; the
second is served by the same screens.

**Tone.** Instrument, not toy. Dark, high contrast, data-forward. Every number
carries a unit and, where the model knows it, an uncertainty. Nothing decorative
that could be mistaken for data. Closer to a telescope control room or a
professional DAW than to a space game's menu.

---

## 1. The core structure: a six-stage workflow

Generation runs in **six checkpoints, in order**. Each has its own controls and
its own preview. Confirming a checkpoint **locks it**; reopening one **discards
every later one**. Locked controls are **disabled and still visible, never
hidden** — the user must be able to see what a locked stage was set to.

Each checkpoint has a **reroll** action separate from editing: reroll changes
that stage's seed only, which invalidates later stages but not earlier ones.
Make reroll and edit visibly different affordances — they have different
consequences.

| # | Checkpoint | What appears in the preview |
|---|---|---|
| 1 | Halo & disc | Rotation curve; smooth axisymmetric disc |
| 2 | Assembly | Merger history; the thick disc appears edge-on |
| 3 | Star formation & chemistry | Gradients and histories; disc colours by [Fe/H] |
| 4 | Pattern | Bar and spiral arms — **first recognisable galaxy** |
| 5 | Systems | Resolves into individual stars |
| 6 | Planets | Systems become openable |

Design the rail/stepper that carries this. It must show: which stage you are on,
which are locked, which are invalidated, and what rerolling would cost.

---

## 2. Controls — the exact set

**Seven scalar controls, a hard ceiling of twelve, and both models take the same
seven.** The two models differ in *stages*, not inputs. Do not invent controls;
the shortness of this list is a deliberate design property of the project and the
UI should make it feel like precision rather than poverty.

### Checkpoint 1 — Halo & disc

| Control | Default (Milky Way) | Range | Unit |
|---|---|---|---|
| `halo_mass` — Halo mass M₂₀₀ | 1.1 × 10¹² | 10¹¹ – 10¹³ | M☉ (log slider) |
| `disc_spin` — Disc spin parameter λ_d | 0.0173 | 0.005 – 0.05 | dimensionless |
| `halo_assembly_z` — Halo assembly redshift | 1.66 | 0.5 – 5.0 | dimensionless |
| `baryon_retention` — Baryon retention fraction | 0.35 | 0.05 – 0.5 | dimensionless |
| `world_seed` | 0 | any integer | seed |

### Checkpoint 2 — Assembly

| Control | Notes |
|---|---|
| `mergers[]` — merger events | **An editable list, not a slider.** Each event: `time` (Gyr), `mass_ratio`, `gas_fraction`. Exempt from the input ceiling, so the list can be any length. Milky Way default is two events: Gaia-Enceladus (t=3.8, ratio 0.25, gas 0.5) and Sagittarius (t=8.8, ratio 0.02, gas 0.01). Design an event editor — a timeline is the natural metaphor, since `time` is the primary axis and mass ratio reads well as height |

### Checkpoint 3 — Star formation & chemistry

| Control | Default | Range | Unit |
|---|---|---|---|
| `infall_timescale` — Infall timescale τ₀ at R₀ | 7.0 | 1.0 – 14.0 | Gyr |
| `inside_out_index` — Inside-out index n | 1.0 | 0.0 – 3.0 | dimensionless |
| `migration_efficiency` — Radial migration efficiency | 3.6 | 0.0 – 8.0 | kpc |

### Checkpoints 4, 5, 6 — seeds only

`pattern_seed`, `systems_seed`, `planets_seed`. Each defaults to 0. **These
stages have no scalar controls at all** — their output is derived from earlier
stages plus a seed. The UI must make that legible rather than looking broken: a
stage whose only control is a reroll is a real and intentional state.

### Model switch

A global **simple / advanced** toggle. Advanced replaces two stages — chemistry
becomes multi-element with a supernova delay-time distribution, and the vertical
structure becomes alpha-resolved — and publishes ten extra fields: `alpha_fe_gas`,
`alpha_fe_stars`, `alpha_fe_history`, `alpha_sequence`, `alpha_split`,
`alpha_dip_depth`, `high_alpha_feh_span`, `feh_spread_sun`, `escape_velocity`,
`metal_escape_fraction`. Show clearly which views gain content in advanced, and
grey nothing without saying why.

---

## 3. The two views

### Galaxy view — the default

Shows the stars. **Critical technical constraint that shapes the design:** the
model can produce ~10⁶ stars, which cannot render as individual objects at
galaxy zoom. The renderer shows a **density field as an image**, with a
**materialised, clickable sample** of ~20,000 stars drawn as points on top.
Zooming past a threshold materialises real stars in the view volume.

So design for **three zoom regimes** and the transitions between them:
smooth field → sampled points → actual stars. The user should understand which
they are looking at without being told twice.

Needs: face-on and edge-on, a field selector (which quantity paints the disc),
a colour legend with units, and a scale bar in kpc. Colour ramps come from the
API's field declarations — **the UI must never hold its own table of colours**.

Star columns available for colouring and filtering: `star_radius`,
`star_azimuth`, `star_height`, `star_age`, `star_birth_radius`,
`star_metallicity`, `star_mass`, `star_population` (thin/thick).

**A design note worth honouring:** a correct galaxy is *overwhelmingly red* —
about 73% of stars are M dwarfs. Blue stars are rare and confined to the arms,
because they live only a few million years. Resist making it prettier than it is.

### System view

Entered by selecting a star. Opens in 0.02 s because it materialises one cell
rather than the galaxy. Shows the star and its planets and belts.

Star: mass, age, metallicity, birth radius vs current radius (migration is
visible per star and is worth showing).

Planets, per body: `planet_semi_major_axis`, `planet_mass`, `planet_radius`,
`planet_insolation`, `planet_orbital_period`, `planet_rotation_period`,
`planet_obliquity`, `planet_volatile_fraction`, `planet_atmosphere`. Plus belts,
which are derived from giant-planet resonances and may be absent.

**Orbital span runs 0.05 to 30 AU — nearly three decades.** A linear orbit plot
is useless. Solve this: log-radial, or a schematic rail, or both with a toggle.
Also design the **return transition** to the galaxy, keeping the user's place.

---

## 4. Presets — real galaxies

A preset gallery on entry, each a card with a real image, a one-line
description, and the parameter story. Selecting one loads its seven values.

**Scope limit, state it in the UI:** this model generates **disc galaxies**.
Below 10¹¹ M☉ the rotating-disc assumption fails; above 10¹³ the object is not a
disc galaxy. **Ellipticals like M87 are out of range** — design an honest
"outside this model's regime" state rather than pretending otherwise. That
honesty is in keeping with the project.

Seven presets:

| Preset | The idea | Parameters that carry it |
|---|---|---|
| **Milky Way** | The default. Every control at its measured value | All defaults; two merger events |
| **Andromeda (M31)** | Bigger, more violently assembled, larger disc | Higher `halo_mass` (~1.5×10¹²), higher `disc_spin`, a major merger in the event list |
| **Triangulum (M33)** | Small, low shear, loosely wound, still forming stars | Low `halo_mass` (~5×10¹¹), longer `infall_timescale`, no major mergers |
| **Whirlpool (M51)** | Grand-design arms driven by an interaction | A recent, high-mass-ratio merger event |
| **NGC 1300** | A strongly barred spiral — the bar is the whole point | High `disc_dominance` via high `baryon_retention` |
| **Pinwheel (M101)** | Large, extended, low surface brightness, multi-armed | High `disc_spin`, moderate mass |
| **Large Magellanic Cloud** | At the low-mass edge of what the model can do | `halo_mass` near 10¹¹ — show the regime warning honestly |

Also design a **"compare to Milky Way"** affordance — presets are most useful
against a reference.

---

## 5. Scientific views

These are what an astronomer opens the tool for, and they should be
first-class screens rather than a debug panel. Every one maps to a field the
model already publishes.

**Dynamics.** Rotation curve `circular_velocity` decomposed into halo, disc and
bulge contributions — the classic plot. Plus `epicyclic_frequency`,
`shear_rate`, `halo_enclosed_mass`, `halo_contraction`.

**Chemical evolution.** The radial `[Fe/H]` gradient with `feh_stars_young` and
`feh_stars_old` shown separately, since the gradient *evolves*. The
age–metallicity relation. The metallicity distribution function at the solar
radius. `feh_history` and `metallicity_history` are on an (R, t) grid — design a
**2D heatmap with a time scrubber**, since these are the model's richest output
and the current viewer cannot show them at all.

**The alpha plane — advanced model only.** `[α/Fe]` against `[Fe/H]`, the single
most diagnostic plot in galactic archaeology. The thin and thick discs separate
into two sequences here. `alpha_sequence`, `alpha_split`, `alpha_dip_depth`,
`high_alpha_feh_span`.

**Star formation.** `sfr_surface_density` and its history, `gas_surface_density`,
`sf_threshold_surface_density`, `infall_rate_history`, `stars_formed_history`.

**Structure.** `stellar_surface_density`, `disc_heating`, `disc_radial_spread`,
`bar_half_length`, `bar_pattern_speed`, `bar_corotation_radius`, `pitch_angle`,
`arm_multiplicity`, `disc_dominance`.

**Stellar populations.** Mass function, age distribution, thin/thick split by
`star_population`, and a **birth radius vs present radius** plot — radial
migration made visible, which is the model's most distinctive result.

**Planet occurrence.** `giant_occurrence` against radius and against metallicity,
`ice_line_sun`, `mean_planets_per_star`. Giant-planet occurrence scales roughly
as the square of iron abundance, so this view is where the galaxy's chemistry
visibly becomes a statement about where planets can exist.

**An acceptance/validation screen.** The model is scored against 24 measured
Milky Way quantities, each pass, fail, or not-computable, some judged
statistically rather than pointwise. Design this: it is unusual, it is the
project's central discipline, and no consumer tool has anything like it. Show
the model's value, the observed value with its uncertainty, and the verdict.

---

## 6. Screens to produce

1. **Entry / preset gallery**
2. **Generation workflow** — the six-checkpoint rail with controls and previews,
   including the locked, invalidated and seed-only states
3. **Galaxy view** — all three zoom regimes
4. **System view** — including the log-scale orbit problem
5. **Scientific views** — enough of the set above to establish the pattern,
   including the (R, t) heatmap with its scrubber and the alpha plane
6. **Acceptance screen**
7. **Comparison view** — two galaxies, or one against the Milky Way
8. Responsive behaviour, and the empty, loading, out-of-regime and error states

**Two things to get right above all.** The workflow's lock-and-invalidate
behaviour is the interaction that makes this tool what it is — it must feel
predictable and never lose someone's work by surprise. And the science views
must look like they were made by someone who has read a paper, not by someone
who has seen a screenshot of one.
