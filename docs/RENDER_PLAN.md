# Realistic galaxy rendering — plan

Basis: `origin/frontend`, which draws the materialised sample as three.js
`<Points>` with vertex colours from the field ramp, normal blending, sprite size
`reach/150`, through react-three-fiber `[verified: frontend/src/galaxy/
GalaxyView.tsx]`.

**Most of this work is in the model, not the renderer.** Three things light needs
are not published, and the catalogue records the first as a deliberate refusal
rather than an oversight `[verified: model/galaxy/stages/systems.py]`:

> *It is axisymmetric. S4 published a pitch angle and an arm multiplicity but no
> non-axisymmetric density, so there is nothing here to wind stars into arms —
> recorded as debt #23 rather than faked.*

No dust field and no line emission are published either. Those three absences,
not the shader, are why the current view reads as a scatter plot.

---

## 0. The architectural question, settled first

Rule A9: one opinion about how a field is rendered, held by the code that
computes it. Rule D5: the viewer computes no physics.

A photometric render is **not a field painted with a ramp** — it is radiance. So
the honest resolution is that per-star colour becomes a *derived published
quantity*, not something the client invents from mass and age. Both rules stay
intact and the client stays a compositor.

This is the difference between the two modes and it is worth stating in one line:

- **Scientific mode** — a field, painted by its declared ramp. What exists today.
- **Photometric mode** — published radiance, composited. What this plan adds.

**Photometric mode never replaces scientific mode.** A viridis ramp on [Fe/H] is
*correct* for reading the model and *wrong* for looking at a galaxy; the reverse
also holds. Two modes, one toggle, neither a default that hides the other.

---

## Part 1 — what the model must publish

### M1 — Non-axisymmetric density (debt #23). **Blocking.**

Nothing downstream matters without this. An axisymmetric point cloud cannot be
made to look like a galaxy by any amount of shading.

The `pattern` stage already publishes `pitch_angle`, `arm_multiplicity`,
`bar_half_length`, `bar_corotation_radius` and `bar_pattern_speed`. It publishes
no density. Add one: a logarithmic-spiral perturbation over (R, φ),

    Σ(R, φ) = Σ(R) · [ 1 + A · cos( m·(φ − ln(R)/tan p) ) ]

analytic, one pass, no fixed point — rule A1 holds. The bar follows from
`bar_half_length` as a separate m = 2 term inside corotation.

**The one new quantity is the arm amplitude A.** Under A4 it is not an input:
arm strength is set by disc self-gravity and shear, both already computed, so
derive it from `disc_dominance` and `shear_rate`. If that derivation will not
close, A becomes a **seeded** draw on `pattern_seed`, exactly as `pitch_angle`
already is under `PITCH_YU`. It does not become a control.

Then `systems` samples azimuth from the perturbed density instead of uniformly.

**Consequences to check, not assume.** Star positions change, so determinism,
convergence and the per-region hash all need re-running. Acceptance rows are
mostly radial and vertical and should be untouched — **verify rather than expect**.

### M2 — Per-star photometry

Colour must come from effective temperature, not from a data ramp. The catalogue
already carries `star_mass`, `star_age` and `star_metallicity`; what is missing
is the mapping to luminosity and T_eff.

**This needs an isochrone grid** — a Level 0 constant set, (mass, age, [Fe/H]) →
(L, T_eff, evolutionary phase). It is a real external dependency that no document
in the project has yet named, and the choice between a tabulated grid (MIST,
PARSEC) and an analytic approximation should be made explicitly and recorded.

Publish per star: `star_luminosity`, `star_temperature`, and `star_rgb` derived
from T_eff. Cost is a vectorised interpolation, linear in star count.

**This also settles a realism trap.** About 73% of stars are M dwarfs, so a
correct galaxy is overwhelmingly red, with blue points rare and confined to the
arms because O and B stars live only a few million years. Photometry gets that
for free; a hand-picked palette will not.

### M3 — Dust surface density and extinction

Cheap once M1 lands. Dust-to-gas tracks metallicity, and `gas_surface_density`
and the metallicity field both exist, so dust is a derivation rather than a
model. Publish an optical-depth field; the arm structure comes free from M1, and
lanes sit on the inner edge of the arms.

### M4 — Line emission

`sfr_surface_density` is published. HII emissivity scales with it. One derived
field, and it too inherits arm structure from M1.

---

## Part 1b — the formation-history view

A separate axis from the workflow, and it needs saying why.

**The six checkpoints are a dependency order, not a historical one.** `graph.py`
derives them from which field each input can affect. The Milky Way's default
mergers land at **3.8 and 8.8 Gyr**, straddling the chemistry integration that
runs the whole 13.6 Gyr — so checkpoint 2 happens both before and after
checkpoint 3. Checkpoints 5 and 6 have no history at all; `systems` and
`planets` sample the present day.

So: **the workflow answers *what do I control*. This view answers *what
happened*.** Conflating them would make the workflow lie about causality.

### The history is already computed and has never been looked at

Eight fields sit on an (R, t) grid at **n_t = 2000, one step every 6.9 Myr**
`[verified: model/galaxy/core/grids.py GridSpec]`: `feh_history`,
`metallicity_history`, `gas_surface_density_history`,
`sfr_surface_density_history`, `infall_rate_history`, `stars_formed_history`,
`giant_occurrence_history`, and `alpha_fe_history` in the chemical model.

`GridSpec`'s own docstring records that n_t = 2000 is sized for exactly this —
*what a screen-sized picture of each needs* — while the acceptance table would be
satisfied by a mesh **80× coarser in time** `[verified: GridSpec docstring,
debt #36 ruled at S22]`. **The time resolution was chosen for a view nobody
built.** This is a scrubber over data that exists, not a new computation.

### What can honestly be shown at a past epoch

| Quantity | Status |
|---|---|
| Gas surface density | **Real** — stored per timestep |
| Star formation rate | **Real** |
| Metallicity, [Fe/H] | **Real** |
| [α/Fe] | **Real** (chemical model) |
| Infall rate | **Real** |
| Stellar surface density | **Real** — integrate `stars_formed_history` |
| Merger arrivals | **Real** — timestamps in the event list |
| Disc thickness | **Derivable** — heating grows scale height with age |
| Individual stars | **Not stored.** Present-day catalogue only |
| Bar and arms | **No time evolution.** Pattern speed is one scalar |

### The trap, named so nobody walks into it

It is tempting to reconstruct past stars from `star_age` and `star_birth_radius`
— a star of age 10 Gyr existed at t = 3.6 Gyr, at its birth radius. **That is
right at the instant of birth and wrong ever after**, because migration is
applied as a present-day dispersion kernel, not a trajectory. Every intermediate
position would be invented.

Rendering them as model output is precisely the *rather than faked* line that
debt #23 was opened to hold. The honest version shows the stellar component at
past epochs as a **surface density from `stars_formed_history`**, never as points.

### H1 — the scrubber

Make it **checkpoint 3's preview**, since chemistry *is* the history and every
field above is published there. A time slider over 0–13.6 Gyr, the (R, φ) disc
re-rendered at the selected epoch, merger arrivals marked on the slider.

Needs nothing from Part 1 to be useful, and improves with all of it: M1 gives the
arms to wind, M3 gives dust that thickens as metallicity rises, M4 gives emission
that blazes during the early starburst and fades.

**Cost.** Eight fields × 400 × 2000 × 8 bytes ≈ 51 MB if fetched whole. Fetch a
radial slice per epoch, or a decimated (R, t) tile with full resolution on
demand. This is the one place in the plan where payload size needs designing
rather than assuming.

### H2 — what the sequence then reads as

Build the halo → place the mergers → **watch the galaxy form** → see its
structure → resolve it into stars → open a system.

The formation history sits at the checkpoint that computes it, instead of being
smeared across a dependency graph or bolted on as a separate mode.

---

## Part 2 — the renderer

Each of these is small; none is possible before Part 1.

### R1 — Additive blending, HDR, tone mapping

The current code chooses normal blending deliberately, because overlapping stars
summing to white looked wrong `[verified: GalaxyView.tsx]`. **The diagnosis was
right and the remedy was the wrong one.** Light is additive; overlapping stars
genuinely do add. What was missing is the rest of the chain: render to an HDR
target and tone-map on output (`ACESFilmicToneMapping`), so a dense core
saturates gracefully instead of clipping to white.

Keep `srgbToLinear` and the linear-space discipline already in `colors.ts` — that
part is right and the comment explaining it should survive the rewrite.

### R2 — A point spread function instead of squares

Stars are not 1.5px squares. A sprite texture with a bright core and faint wings
is the single largest visual return per line in this plan.

### R3 — The far field

The smooth unresolved component, rendered as surface brightness under the points.
This is the half of the LOD design that was specified and never built — the
current view is *sample only*, as its own comment says. Real galaxy images are
mostly unresolved light, so this layer is most of what makes the result read as a
photograph rather than a plot.

### R4 — Dust as subtraction

M3's optical depth as a multiplicative layer in front of the stars behind it.
**Dust is not a colour, it is occlusion** — getting this wrong by adding brown
instead of subtracting light is the most common way this looks fake.

### R5 — Bloom

A postprocessing pass. Cheap, and it is what sells the bright core. Do it last
and keep it restrained — bloom is also the fastest way to make an instrument look
like a screensaver.

---

## Part 3 — how to tell whether it worked

"Looks right" is not an acceptance row, and the project does not accept claims it
cannot check. Three things here *are* checkable:

1. **Integrated colour and absolute magnitude.** Once M2 publishes per-star
   luminosity and temperature, the galaxy's total B−V and M_B follow by
   summation, and both are measured for real galaxies. **These are genuine new
   acceptance-row candidates** and they are the first rows this project could add
   that test the photometry rather than the dynamics.
2. **Surface brightness profile.** An exponential disc has a known profile; the
   rendered image should reproduce it.
3. **Arm contrast amplitude.** Measurable in real galaxies, and it is the direct
   check on M1's A.

H1 adds a fourth, and it is free: the scrubber is a **visual convergence check on
the time axis**. A history that flickers or steps between adjacent epochs is
under-resolved in t, and n_t is the axis the measured exponent says is expensive
`[verified: bench2.py §3]`. Eight fields at 2000 steps have never been looked at;
the first thing a scrubber may reveal is whether they are smooth.

Everything beyond those three is judged by eye, and should be labelled as such
rather than dressed up.

---

## Sequence

| | Step | Blocked by |
|---|---|---|
| **M1** | Non-axisymmetric density (debt #23) | nothing — **start here** |
| **M2** | Isochrone grid; per-star L, T_eff, RGB | nothing; parallel to M1 |
| **M3** | Dust optical depth | M1 |
| **M4** | Line emission | M1 |
| **H1** | Formation-history scrubber at checkpoint 3 | nothing — **the data exists** |
| **R1** | Additive + HDR + tone mapping | M2 |
| **R2** | PSF sprite | nothing |
| **R3** | Far field layer | M1, M2 |
| **R4** | Dust subtraction | M3, R1 |
| **R5** | Bloom | R1 |
| **P3** | Photometric acceptance rows | M2 |

M1 and M2 are the work. **R2 and H1 can both be done today** — R2 improves the
current view with no model change, and H1 renders eight fields that have never
been displayed in twenty-three sessions. Everything else is compositing.

**One caution.** M1 discharges a debt the project deliberately left open, with
the phrase *rather than faked*. The perturbation must therefore be derived and
declared like any other field, with its amplitude either derived or seeded and
never made a control — otherwise this plan closes a debt by doing the exact thing
the debt was opened to avoid.
