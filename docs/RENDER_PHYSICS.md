# RENDER_PHYSICS — the model/renderer contract

What the model publishes so that the viewer can draw galaxy-scale and
nebula-scale images, in broadband colour, narrowband false colour, or as a named
instrument would record them.

Companion to `RENDER_PLAN.md`, which covers the viewer's first build (M1–M4,
H1, R1–R5, all done at S23–S24) and to `BUILD_II.md`, whose Phases 8–11 build
the model side of this contract and whose sessions V1–V4 build the renderer
side. This document covers the **interface**: it is the thing both ends must
agree on, and it is written to be unambiguous because the two ends get built by
different sessions.

Everything here is `[inferred]` design unless tagged. Physics constants marked
**NEEDS SOURCING** must be read from a source before entering code (rule B9).

---

## 0. Where the repository stands against this contract (reconciled 2026-09-26)

Written when the contract entered the repository, so that no phase reads the
sections below as a description of an empty slate.

**Already published, and consistent with the contract.**

- Per star, `star_luminosity` (L☉, bolometric) and `star_temperature` (K) from
  the committed PARSEC table `[verified: model/galaxy/stages/photometry.py; DECISIONS.md D164]`.
  No RGB is published: the temperature's declared ramp is the `blackbody` cmap
  computed from Planck's law at import, which is §2's rule already honoured for
  stars.
- The disc's unresolved light as `disc_surface_brightness` (L☉/pc²) and
  `disc_light_temperature`, integrated along every isochrone once
  `[verified: model/galaxy/stages/light.py; D165]`. A **surface** quantity, as
  §4 permits at galaxy scale.
- Dust as `dust_surface_density` and `dust_extinction_v` (A_V face-on) from the
  `ism` stage `[verified: model/galaxy/stages/ism.py; D163]`. Since S31 (BUILD_II
  Phase 7) the `dust` stage adds, per radius, the scattering optical depth and
  E(B − V), the scalar asymmetry g, the absorbed starlight, the dust temperature
  from the heating balance, the infrared emission and its total, G₀ and the PAH
  fraction; the absorbed and emitted powers are the §7 energy-balance test
  `[verified: model/galaxy/stages/dust.py; tests/test_dust.py]`. Galaxy-scale
  surface quantities, face-on.
- Per-region determinism: `/api/region` materialises any (R, φ) window as the
  same stars a full sweep would give, a star named by `(cell, index)` at a
  sample size `[verified: model/galaxy/stages/systems.py; D60, D167]`. This is
  §5c's `sample_region(bounds, seed)` in all but name.

**Published, but not in the contract's form.**

- `halpha_surface_brightness` is Σ_SFR times one constant `[verified: light.py;
  D166]`. **Since S35 (Phase 9)** the `nebular` stage publishes §2's ionized-gas
  component: per cluster the HII region's Q, n_e, T_e, log U, clumping and O/N/S
  (§3a's shape parameters) and its Hα **per unit volume** (§4, unit `erg/s/cm3`),
  the diffuse layer, and the disc's Hα as Σ_Q redistributed; `HALPHA_PER_SFR` is
  the check (0.71 at S35) `[verified: model/galaxy/stages/nebular.py; D184]`. The
  collisionally excited lines wait on the photoionization grid ruled in (Byler et
  al. 2017 via FSPS), whose fetch is the owner's call; the old field stays until V3.
- **Since S36 (Phase 10)** the `bubbles` stage publishes the hollow: per cluster
  Weaver et al. 1977's bubble (radius, shell velocity, density, thickness, Hα per
  unit volume in the shell, interior pressure and temperature, phase, stalled),
  the supernova-remnant census as an object class (`of="remnant"`, `/api/remnants`,
  Sedov then the snowplow), the hot phase's porosity per radius, and a star's own
  bubble as a catalogue column `[verified: model/galaxy/stages/bubbles.py,
  feedback.py; D185]`. Their [S II]/Hα waits on the same grid.
- The region cells were galaxy-scale: 1024 cells in (R, φ), of which ~800 realise
  a star at the default sample `[verified: python -m galaxy.specs, performance]`.
  **Since S32 (Phase 8) `/api/region` and `/api/system` take `level=` 0–3**: a
  level-k cell is one of 4^k children of a level-0 cell with its own seeded stream,
  holds its parent's stars that fall inside it plus its own at the parent's density
  read at the child — 4^k the sample density — and the union, prefix and
  determinism properties are asserted at every level `[verified:
  model/galaxy/stages/systems.py; tests/test_hierarchy.py; D181]`. The molecular
  clouds of §5a exist as an object class (`of="cloud"`) served by `/api/clouds`, a
  census that a level filters `[verified: model/galaxy/stages/clouds.py; D181]`;
  since S33 the cluster object of §5b exists too (`of="cluster"`, `/api/clusters`,
  one per cloud past its embedded phase, Q and wind as IMF integrals) `[verified:
  model/galaxy/stages/clusters.py; D182]`.

**Present in the viewer, and forbidden by §8 once the cloud vector exists.**
The field regime lays each ring out within itself: 30% of the starlight as
12 000 K young light crowded into the arms, the dust led onto the arms' inner
edge, a seeded clump lattice along the arms, and Hα gathered into knots covering
~1.6% of a ring, all seeded from `world_seed` so a galaxy keeps its clumps from
view to view `[verified: frontend/src/galaxy/FieldVolume.tsx, regimes.ts;
commit f2230d5]`. The seed comes from the model, which §8 requires; the
*structure* does not trace to a published field, which §8 forbids. It was a
stated display choice made before any cloud field existed, and it is exactly
what V2 and V3 replace: the young light by the ionized-gas and stellar
components at the arms' own star formation (Phase 2), the clumps and knots by
the cloud catalogue (Phase 8) and its emissivity (Phase 9). **Since S38 (V1)
the young light is gone**: the stellar component's colour per cell is the
model's filter integral at the population's published colour temperature, and
what stays of the exception is the Hα's crowding into the arms and its seeded
knots, and the dust's lead and clumps, V2's to remove `[verified:
frontend/src/galaxy/regimes.ts, FieldVolume.tsx]`. **Since S39 (V2) the exception
is closed**: `/api/render` returns the Hα as two volumetric layers (the HII
regions' share placed by the pattern's contrast in the clouds' layer, the diffuse
gas's in its published 1.4 kpc layer) and the dust as three components — the
extinction per filter from the grain table's own curve (A_λ/A_V from C_ext/H at
the filter's reference wavelength over the V row's), the scattered light (the
slab's scattered share, a Henyey–Greenstein phase table at the published g) and
the thermal emission (Σ_IR at T_d through the curve) — each with its layer in the
header; the viewer spreads each through its layer and integrates along the ray.
The knots, the clump lattice, the dust's lead and `CHANNEL_EXTINCTION` are gone;
what the field regime keeps is display only (white point, exposure, tone curve,
bloom, the march's sampling). The frame's absorbed and emitted power are the
published fields' to 3.4 × 10⁻⁴ each and balance to 6.8 × 10⁻⁴, the TIR box's
coverage `[verified: tests/test_render.py]`.

**The ruling V1 made (S38): option (a).** The paragraph below is the question as
it stood; the answer is `/api/render` (`model/galaxy/stages/spectra.py`,
`api/service.py`): the viewer sends its curves as numbers (the sets are
`frontend/src/galaxy/filters.json`; a request naming a set without curves is
refused, since the model holds none), and the model returns the stars per
(R, φ) cell, the Hα and the dust per ring and the bulge per filter, never
composited; the viewer divides by a white point and multiplies by its exposure
`[verified: tests/test_render.py]`. The stellar spectrum is the population's
own eight-band SED (`disc_sed_*`, `bulge_sed_*`, λL_λ at the SVO reference
wavelengths), joined by power laws made band-consistent, blackbody tails beyond U
and K; the frame through the table's B and V reads B − V +8.9 × 10⁻⁵ and M_V
−1.7 × 10⁻⁴ mag from Phase 3's, tolerance 10⁻³. The first cut (one blackbody at
the colour temperature, M_V 0.71 mag bright) is kept in the test as the record.

**One ruling this contract leaves open, for V1.** §3a says the model ships the
spectrum function and the renderer calls it, and §2a says the viewer holds the
filters. In this repository the model is Python behind an HTTP API and the
viewer computes no physics (rule D5), so "the renderer calls the function" means
one of two things, and V1 must rule:

- *(a)* the viewer sends a filter set (named, or its curves) with a request and
  the model returns each component's per-channel response per cell, three or
  four floats per cell per component — the payload of today's RGB texture, the
  filter integral run once server-side;
- *(b)* the model publishes each component's spectrum *basis* (a table over its
  shape parameters on the shared wavelength grid, plus the line list) and the
  viewer integrates against the filters itself.

(a) keeps D5 and A9 intact and is recommended `[inferred]`; (b) moves an
integral into the viewer and needs D5 amended. Either way the filters are the
viewer's data and the model holds no palette.

---

## 1. The problem this contract solves

A galaxy view spans ~30 kpc at ~10 pc resolution. A nebula view spans ~10 pc
with structure to ~0.01 pc. That is six orders of magnitude in linear scale and
eighteen in volume.

**No grid spans it and no catalogue holds the stars.** So the contract is not a
list of fields at one resolution. It is two things:

1. **Field-level output** — smooth, galaxy-scale, published by the model.
2. **A region contract** — a small parameter vector per object, from which the
   renderer synthesises interior detail on demand, deterministically.

The model does not produce pillars, filaments or clumps. It produces the
**conditions that generate them**, and the statistics they must obey.

---

## 2. Emission is published as components, not colours

The model must not publish RGB, and must not publish a single "brightness"
field. It publishes **five physically distinct emitting components**, each with
its own spectrum:

| Component | Emits | Determined by |
|---|---|---|
| Stellar photospheres | continuum | L, T_eff per star (Phase 3) |
| Ionized gas | recombination + forbidden lines, free-free continuum | Q(H⁰), n_e, T_e, abundances |
| Photodissociation region | PAH features, H₂ lines | radiation field at the ionization front |
| Dust (warm and cold) | modified blackbody | heating balance, β |
| Shocked gas | [S II]-enhanced lines | shell velocity, ambient density |

Extinction applies to components 1 and 2; the energy removed is what components
3 and 4 re-emit. **That closes a loop, and the loop is a test** (§7).

### 2a. Why components rather than colours

Because every display mode the viewer offers is then the *same mechanism*:

| Display | Is just |
|---|---|
| Broadband RGB | three wide filters |
| SHO / HOO false colour | three narrow filters |
| "As JWST" | NIRCam filter set + hexagonal PSF |
| "As Hubble" | WFC3 filter set + Airy PSF |
| Single-line map | one filter |

The viewer holds the filters. The model holds no opinion about palette at all.

---

## 3. Spectra: continuum grid plus a line list

A narrow emission line on a coarse wavelength grid is lost, and narrowband false
colour is *made of* narrow lines. So a component's spectrum is **two objects**:

- **`continuum`** — on a shared log-spaced wavelength grid, 0.1–30 µm.
- **`lines`** — an explicit list of (wavelength, flux) pairs, evaluated exactly.

The line list must include at minimum: Hα 6563, Hβ 4861, [O III] 4959/5007,
[S II] 6717/6731, [N II] 6548/6583, plus the PAH features at 3.3, 6.2, 7.7, 8.6
and 11.3 µm `[recall — NEEDS SOURCING]`.

**[S II]/Hα separates shocks from photoionization for free** once both are
published. No extra field.

### 3a. Payload discipline — do not publish spectra per cell

A 128-point spectrum on a (R, φ) grid is the 288-million-cell mistake again.

Instead: **per cell the model publishes the handful of parameters that determine
each component's spectrum, and ships the spectrum function as model-side code.**
The renderer calls that function (see §0 for what "calls" means here). This
keeps the payload at a few floats per cell, and it keeps rule A9 satisfied —
there is exactly one rendering opinion and the code computing the field holds it.

The shape parameters are small:

| Component | Parameters per cell |
|---|---|
| Stars | mass-weighted T_eff mix, surface density, [Fe/H] |
| Ionized gas | Q(H⁰) surface density, n_e, ionization parameter, O/H, S/H, N/H |
| PDR | radiation field strength G₀, PAH abundance |
| Dust | Σ_dust, T_dust, β |
| Shocks | shell velocity, ambient n |

---

## 4. Emissivity is volumetric, not a surface

**This is the requirement most likely to be got wrong once and be expensive to
retrofit.**

A wind-blown bubble reads as a sphere because the line of sight passes through
more shell material tangentially than face-on — limb brightening. Every
edge-brightened filament, every bubble rim, every bright-rimmed pillar face is
this effect.

If emission is drawn as a surface texture, a bubble renders as a flat disc.

So at region scale the model publishes **emissivity per unit volume**
(erg s⁻¹ cm⁻³ per unit wavelength) and the renderer integrates along the ray.
The shell appears for free and is correct for any viewing angle.

Galaxy-scale fields may remain surface quantities, because the disc is optically
thin and integrated through by construction. **The transition point must be
stated in the field docstrings**, or the two will be silently mixed. (The
repository's galaxy-scale light is already a surface quantity with a stated
vertical profile the ray-marcher applies, D167; region-scale emissivity is new
and must be declared volumetric in its `FieldDecl` — a new unit in the closed
vocabulary, which is a `core/` edit plus a DECISIONS entry.)

---

## 5. The region contract

### 5a. Cloud vector

One record per molecular cloud. Everything the renderer needs to synthesise the
interior, and nothing else.

| Field | Why it is needed |
|---|---|
| `cloud_id` | |
| `position` (R, φ, z) | placement |
| `mass`, `radius` | mean density |
| `density_gradient` (magnitude + direction) | **bubbles sit off-centre** because they expand into a gradient; without this every shell is concentric and wrong |
| `mach_number` | sets σ_s² = ln(1 + b²ℳ²) `[recall — NEEDS SOURCING for b]`, the log-normal density PDF that **generates clump-and-filament structure** |
| `metallicity` ([Fe/H], [α/Fe]) | O/H and S/H for line ratios; dust and PAH abundance |
| `age` | which state it is in |
| `state` | embedded / blown open / dispersing / remnant |
| `cluster_id` or null | the embedded cluster, if any |
| `ionizing_source_offset` (vector) | **which way the pillars point** — they are the shadows of clumps that survived the front eating the cloud from one side |
| `seed` | deterministic regeneration |

The Mach number and the source offset are the two that do the visual work. Mean
density alone produces a fog.

In this repository a cloud is an **object class** beside `star`, declared with
`FieldDecl(kind=Kind.COLUMN, of="cloud")` columns and drawn per cell exactly as
stars are, so that a region's clouds are the same clouds a sweep would give
(D60). The `seed` is the cell-and-index path, not a stored number.

### 5b. Cluster object

Clusters are their own class, not a label on stars.

`cluster_id`, position, mass, half-mass radius, age, bound flag, metallicity,
`Q_ionizing`, `wind_luminosity`, `seed`.

**This unifies with BUILD_II Phase 5.** Globular clusters are the surviving
massive end of the same mass function, so one mechanism produces both, and the
η relation becomes a check on it rather than a separate assertion.

Since S33 (BUILD_II Phase 11) the cluster is an object class (`of="cluster"`)
served by `/api/clusters`: one per cloud past its embedded phase, named by the
cloud's cell and its `cloud_cluster_index`, placed at the cloud's embedded source
(`cloud_source_angle` read from the outward radial direction toward increasing
azimuth `[inferred]`), with `cluster_ionizing_photons` and `cluster_wind_luminosity`
the IMF integrals at its age times its mass `[verified:
model/galaxy/stages/clusters.py; tests/test_clusters.py]`. The `seed` is the
cell-and-index path, as for clouds.

### 5c. On-demand resampling

The star catalogue is a sample, not a census. Zooming to pillar scale needs stars
down to the bottom of the IMF inside a tiny volume.

**Interface requirement:** the model exposes a function
`sample_region(bounds, seed) -> stars`, deterministic in its arguments,
independent of what has been sampled before. Regions are generated and discarded,
never stored.

The repository has this at galaxy scale already (`/api/region`, D60, D167:
§0). What it lacks is depth: a cell is kiloparsecs across and the sample size
that would fill a 10 pc window with the whole IMF is ~10¹¹ stars galaxy-wide.
The interface change is a **cell hierarchy** — level-0 cells are today's; a
level-k cell is one of 4ᵏ children with its own stream, and a request names the
level it wants — with the prefix property (a smaller sample is a prefix of a
larger one) holding within a cell and the union property (a parent's stars are
its children's) holding across levels. That is the piece most likely to be
missed until the viewer needs it.

---

## 6. Clumping: one mechanism, two payoffs

Emission measure goes as n²ℓ, and ⟨n²⟩ ≠ ⟨n⟩². The mean density gets nebular
brightness wrong by a large factor.

The clumping factor comes from the **same log-normal PDF** that generates the
pillars. Build it once; it corrects the photometry and draws the structure.

---

## 7. Consistency constraints

These are tests, not guidelines, and they belong in the suite.

**Energy balance.** Ultraviolet and optical light absorbed by dust must equal the
infrared re-emitted. This catches an extinction law and a dust emission model
that disagree — exactly the class of defect that put the extinction coefficient
out by a factor of 162, which no test caught `[verified: DECISIONS.md D163]`.

**Catalogue against field.** Integrate the resolved star catalogue over a patch;
compare against the galaxy-scale surface brightness field at that patch. They
must agree within Poisson noise. If they do not, the zoom will visibly not match
the wide view.

**Modulation is a redistribution.** Any azimuthal or clumping modulation must
integrate back to the axisymmetric quantity. Assert it. (`pattern_density_
contrast` already averages to 1 around every ring `[verified: tests/test_pattern.py]`;
Phase 2's star-formation modulation must do the same, weighted by gas.)

**Region determinism.** `sample_region` called twice with the same arguments
returns the same stars. Called on overlapping bounds, it agrees on the overlap.
Across levels of the hierarchy, a parent's stars are its children's.

---

## 8. What the renderer may not do

**Every visible feature traces to a published field or to a seeded draw from
one, and the seed comes from the model, not from the frame.**

It would be very easy to make this beautiful with noise textures that aren't from
the model. That is rule A4 read backwards — the renderer inventing structure the
physics does not have. A galaxy-flavoured noise generator with a physics model
bolted to the side is the failure mode, and it is hard to detect after the fact
because it looks correct.

Specifically forbidden:
- frame-seeded or time-seeded noise (it would shimmer, and it is not a structure)
- detail added below the scale the cloud vector constrains
- colour applied for appearance rather than derived from the filter integral

The viewer's clump lattice and Hα knots (§0) were the one standing exception,
dated; V2 removed them at S39, and nothing of that kind may be added.

---

## 9. Out of scope, deliberately

Recorded so these read as decisions rather than oversights.

**Interacting and merging systems.** `mergers[]` is a history of completed
events, not a second body present in the frame. Tidal tails, bridges, a shared
non-axisymmetric potential and merger-triggered bursts are not expressible, and
the SFH is smooth by construction. The model generates one galaxy.

**Environment.** No intracluster medium, no cluster membership, no cooling-flow
filaments, no active nucleus. These are properties of *where a galaxy lives*, not
of the galaxy. The model has a dark matter halo and nothing outside it.

Background galaxies and foreground stars in a rendered field are viewer-side
decoration and are fine; they carry no physics and must not be described as if
they do.

**Named objects.** The model produces a morphology class at a given metallicity
around a cluster of a given mass. It does not produce a particular nebula, and
attempting one would be fitting with the answer known (rule B5).

---

## 10. Sourcing still owed

Everything marked `[recall — NEEDS SOURCING]` above, plus:

- ~~the turbulence forcing parameter b in σ_s² = ln(1 + b²ℳ²)~~ — read at S32 (Federrath et al. 2010, D181)
- ~~Case B Hα yield per recombination, and the Hα/Hβ ratio~~ — read at S35 from Storey & Hummer 1995's tables (D184)
- ~~dust albedo and scattering asymmetry g in V, and R_V~~ — read at S31 from Draine's table (D180); the
  table's extinction curve and albedo per wavelength read at S39 for the per-filter dust (`spectra.GRAIN_TABLE`)
- ~~modified blackbody emissivity index β~~ — read at S31 (Planck 2013 XI, D180)
- the Henyey–Greenstein phase function — read at S39 (Bosschaart & Olofsson 2026, arXiv:2604.08379 eq. 3)
- PAH feature wavelengths and their metallicity dependence
- ~~the wind bubble solution's constants (Weaver et al. 1977) and the Sedov phase~~ — read at S36 from Weaver's scan, Kim & Ostriker 2015, Chen & Slane 2001 (D185)
- the hydrogen-ionizing photon rate Q(H⁰) as a function of T_eff and L (Phase 3)
- the filter curves of every named filter set the viewer offers (V1)

None of these enter code from recall.
