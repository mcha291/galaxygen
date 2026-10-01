# RENDER_PLAN II — finishing the viewer (S46 onward)

**The owner's word, 2026-10-01:** "put a pin in the model work for now … finish building out the viewer … if the
azimuth model is feature complete, make that the default and work on the galaxy renderer", and, asked which parts count
as finished: "not sure yet, let's review this" — the plan document first. So this document is the review: §1 is where
the viewer stands, read from the code on 2026-10-01 (a read-only agent's survey, the session's own walk of the built
viewer on `prod`, and the design record); §2 is every candidate the record names, costed; §3 is a proposed sequence
with the choices left open for the owner. Everything here is `[inferred]` design unless tagged. Rows run under
BUILD_II's protocol (one row, one branch, one `--no-ff` merge, the tag at close); Fable rules and reviews, Opus builds.
The render contract `RENDER_PHYSICS.md` still binds, §8 above all: **every visible feature traces to a published field
or a seeded draw from one; no frame-seeded noise, no detail below what the cloud vector constrains, no colour applied
for appearance rather than derived from the filter integral.** The model is pinned: a candidate that needs a new
published field says so, and is the owner's to allow.

---

## 1. Where the viewer stands (reconciled 2026-10-01)

### 1a. What is built

| Part | As built `[verified: the files named, read 2026-10-01]` |
|---|---|
| **Regimes** | Three, handed over by the view's width (`regimes.ts`): the **field** (≥ 25 kpc across; a ray-marched volume of `/api/render`'s components), the **sampled** points (a 20 000-star whole-galaxy sample, 50 → 15 kpc), the **stars** (below 4 kpc: a region materialised by `/api/region` at 60 000–1 000 000 stars, the level's clusters as points, and the region volume of clouds, HII spheres and shells). The field never fades to zero (0.03 stays, to keep the bulge from washing the view). Jump buttons at 45 / 12 / 2.5 kpc. |
| **Modes** | *field* (the three regimes) and *brightest* (the N most luminous stars in the frustum, 10²–10⁵, auto-exposed to the hundredth brightest; no field, no region). |
| **The field's render** | `/api/render` at f4 over the whole grid through the chosen set's curves at a 6500 K white: `stars`, `halpha_hii + lines_hii` (one layer), `halpha_dig + lines_dig`, `dust_scattered × phase + dust_thermal`, `dust_extinction` as τ per channel; the bulge as a Hernquist profile from the header. 96 geometric steps, exact tanh columns per layer, front-to-back with each layer's own dust, fixed screen-space jitter, a 400 000-pixel budget into a half-float target, re-marched only on change. AgX tone mapping, restrained bloom (0.35 / 0.45 / threshold 1). Gain 1/400 per L☉ pc⁻² × 2^stops is "a display balance, not a physical constant". |
| **The region's march** | Clouds as seeded log-normal spheres (four octaves, measured σ, a linear tilt `[inferred]`, pillars inside the cavity), HII spheres of uniform emissivity coloured by Hα, Hβ and the four forbidden lines, bubbles and remnant shells; **a display budget of 256 objects per pixel (128 / 64 / 64)**; composited as two screen-space quads — transmission multiplies the whole frame behind it, stars in front included (#112). |
| **Points** | A star's channel is L × the blackbody share at T over the white (`/api/blackbody`), × 2^stops / 100; clusters the same from `cluster_luminosity` and `cluster_light_temperature` (#114: about twice the filter light). A 9 px Gaussian + Moffat sprite; the WFC3 sets a 25 px Airy sprite per channel at the pivot, its scale a display choice (#120). **Only the level-0 prefix-scaled sample is ever used**; `/api/region?level=k` is served and never sent (#113). Picking a star within 8 px opens its system; clusters cannot be picked. |
| **Filter sets** | rgb (Gaussians `[inferred]`), sho, hoo (30 Å boxes), wfc3, wfc3n (SVO's curves, vacuum since S44). The `ir` set exists and is not offered. |
| **Previews** | Checkpoint 1 the Σ disc with isophotes and orbit tracers; 2 the mergers' heated envelope and history tower; 3 Σ × the pattern; **4 the history scrubber** (every (R, t) field but `stars_formed_history`, which is at today's radii); 5–6 the field volume alone. |
| **System** | An overlay, not a tab: the star's summary, a migration strip, an orbit rail (log or schematic; belts dashed as inferred), a planet table; the star's disc colour is a display choice. |
| **Tests** | 16 vitest files, 121 cases, all on the logic (colours, curves, frustum, noise, packing, zoom); **no image-level test** — `tools/shot.py` and `test_viewer.py` capture the reference viewer in `interface/`, not the React app. |
| **Performance** (D192, D194) | render whole rgb 2.1 s cold / 0.22 warm, 6.9 MB; one region 2.0 / 0.21; clusters whole disc 1.6 s, 4.1 MB; `/api/blackbody` 5 ms; a WFC3 request is a POST past 4 KB. |

### 1b. What the walk of the built viewer showed (`prod`, :8018, main at 13fea07; frames in `docs/design/screenshots/s46/`)

- **The field at 57 kpc oblique and 112 kpc face-on** (`field-oblique-57kpc-rgb.jpg`, `field-faceon-112kpc-rgb.jpg`):
  a soft, low-contrast spiral — the arms and the bulge read, the dust lanes do not, nothing resolves. This is the
  physics as published through the display's defaults (the 1/400 gain, 0 stops, AgX), not a bug; whether it is what
  the owner wants the first frame to be is §2 B4's question. The design mockup of 2026-09-13 (`screenshots/01-final.png`)
  shows the same regime with a brighter bar and tighter arms under a "natural" base image.
- **Brightest mode** (`brightest-3162-stars.jpg`): works as designed; the pool and the auto-exposure behave.
- **The stars regime drew nothing** at 0.3 and 0.07 kpc across in either set (`stars-regime-0.3kpc-black.jpg`), while
  every request behind it returned 200 (`/api/region` at 1 000 000 stars for r 2.5–3.5, φ 3.44–3.83; `/api/clusters`,
  `/api/clouds`, `/api/remnants` and `/api/render` at level 3). **The console logged `THREE.WebGLRenderer: Context
  Lost` five times.** In the desktop app's small browser pane that is the likeliest cause — the region's two offscreen
  targets, the half-float march target and the composer's passes together exceed what the pane's GPU context gives —
  but the session could not separate a lost context from an empty window at that position, and **the owner's live tab
  on :5173 is the check**: if the stars regime draws there, the finding is the pane's; if not, it is the viewer's and
  B5 below moves to the front. Either way a renderer that loses its context silently and shows black is a defect
  (`[inferred]`: no handler restores it; three.js logs and stops).
- **A reload lands on checkpoint one** (rule D1), so the Galaxy tab is reached only after six confirmations; the walk's
  earlier frames came from a persisted session.

### 1c. The design record against the build

The mockup (`docs/design/Galaxygen.dc.html`, the `_ds` design system with 21 components, the brief in `uploads/`) and
the build diverge in ways nobody has ruled on: **one of the 21 components was ported** (`Button`, plus an error boundary);
the tabs are Preview / Science / Galaxy with the system as an overlay against the design's Workflow / Galaxy / System /
Science; the design's "base image natural / inferno" and "field painting the disc" became filter sets and "field
painting the stars"; the handover is 25 kpc where the design said 22. The token CSS files are byte-identical. Three
records are stale: `App.tsx`'s "since D170 there is one model", `basic.py`'s "the one registered model", and
`RENDER_PLAN.md`'s status table ("H1 … done at checkpoint 3"; it is checkpoint 4 since S25).

### 1d. The azimuthal model is feature complete relative to `basic`

`azimuthal` is `BASIC`'s tuple with the `sfh` slot swapped for `sfh_azimuthal` and `BASIC`'s constants: every stage
`basic` gains it gains, it publishes everything `basic` does plus `sfr_modulation`, and the catalogue places its young
stars by it `[verified: model/galaxy/models/azimuthal.py]`. Every acceptance row reads identically in both (12 / 20 / 5 of
37). Its one open debt, #81 (the 0.1 Gyr young-star cut, unsourced), does not block a default. **The default lives in
three places**: the registry's order (`DEFAULT = "basic"` first; the API takes `names()[0]`), the viewer's
`useWorkflow(initialModel = "basic")`, and the tests' `default` fixtures — and the owner ruled all three.

---

## 2. The candidates, costed

Each: what exists, what the row builds, its gate (something checkable, per RENDER_PLAN Part 3: "looks right" is not a
row), who builds it, the cost in sessions. **Model** marks a candidate that needs a new published field.

### A. The default switch (ruled by the owner: API, viewer and tests) — S46's first row
*Exists:* two registered models, `basic` first. *Builds:* `azimuthal` registered first (the API's default), the viewer
starting on it, the test fixtures' `default` run and the specs' first report on it; `basic` stays registered and
selectable; the three stale comments corrected; the preset thumbnails, if any are kept, re-made. *Moves:* every pin
on the default run's catalogue that the young stars' azimuths touch (`test_region_synthesis`, `test_v4`, V3's windows,
the S45 diagnosis's region selection — radial statistics are unchanged by construction; the per-window ones are not).
*Gate:* the suite green with every moved pin's reason; `/api/version` or `/api/stages` says which model is first;
specs 12 / 20 / 5 of 37 both models. *Who:* Opus builds, Fable rules on each moved pin. *Cost:* one session, most of it
pins.

### B. The picture's correctness
- **B1 — points painted through the filter set (#114).** *Exists:* a point's colour is its bolometric L through a
  blackbody share, ≈ 2× the optical light (the census summed reads 1.89 / 2.12 / 2.43× the render's R / G / B). *Builds:*
  per cluster the eight band points × mass through the set, per star the isochrone's magnitudes the table holds;
  `/api/region` and `/api/clusters` gain per-filter responses, or the viewer asks `/api/render`'s machinery per object.
  *Gate:* the census summed through the set equals the render's `stars` over the same cells within the sample's noise
  (V4's measurement made a test). *Who:* Fable rules the API form (server-side per object, or band points on the
  wire), Opus builds. *Cost:* one session. **Model**: a per-object band response is a derived column.
- **B2 — the young population once (#115).** *Exists:* clusters are the whole young population and the sample draws
  the same stars; nothing accounts between them. *Builds:* a membership the model publishes (`star_cluster_index`, or
  the young stars a cell's clusters account for) so the sample excludes what the points carry; dissolved clusters' light
  handed back to the sample. *Gate:* sample + points = the render's `stars` over the cells (the same test as B1).
  *Cost:* one session, after B1. **Model.**
- **B3 — depth-aware composite (#112).** *Exists:* the region's transmission quad multiplies everything behind the
  camera's whole frame, a star in front of a cloud included. *Builds:* the star layer's depth written and read by the
  transmission pass, or the region marched inside the field's own volume. *Gate:* a star placed in front of an opaque
  cloud keeps its light (a unit test on the pass with a synthetic depth). *Who:* Opus. *Cost:* half a session.
- **B4 — the first frame's balance.** *Exists:* the 1/400 gain, 0 stops, AgX, the field floor at 0.03: the first
  frame is soft (§1b). *Builds:* a ruled default exposure and a ruled tone curve, each named a display choice in the
  set's declaration, and nothing that is not (§8: no contrast "for appearance"). *Gate:* the surface-brightness profile
  of the rendered face-on frame against the exponential disc the model publishes (RENDER_PLAN Part 3's second check,
  never built) — a measurement, not an opinion. *Who:* Fable rules, Opus builds the profile test. *Cost:* half a session.
- **B5 — the renderer survives its context.** *Exists:* a lost WebGL context is logged and the canvas stays black
  (§1b). *Builds:* a `webglcontextlost` / `restored` handler that re-creates the targets, a pixel and target budget that
  scales to the context's limits, and the region's two targets merged with the march's where they can be. *Gate:* a
  simulated context loss (`WEBGL_lose_context`) followed by a frame that draws; the pane at 800 × 590 draws the stars
  regime. *Who:* Opus. *Cost:* half a session; **first if the owner's tab shows the same black.**

### C. Resolved objects on approach
- **C1 — clusters with their published radius (#116).** *Exists:* every cluster a point sprite at every level;
  `cluster_half_mass_radius` on the wire, tens of pixels at level 3. *Builds:* a light profile (Plummer or King, ruled)
  drawn at the levels that resolve it, the point kept where it does not. *Gate:* the profile integrates to the cluster's
  light; the switch is at a stated pixel size. *Cost:* half a session.
- **C2 — the level-k stars as the point layer (#113).** *Exists:* `/api/region?level=k` served, never sent; the viewer
  densifies the level-0 sample. *Builds:* the level's region as the point layer below 1 kpc with the picker reading
  `level`, `cell`, `index`. *Gate:* B1's closure test at each level. *Cost:* one session, with B2.
- **C3 — the display budget (#111).** *Exists:* 256 objects per pixel, the rest drawn by nothing. *Builds:* the kept
  share returned by `packObjects` and the field's HII faded by weight × share, or the unbudgeted regions as points.
  *Gate:* the window's Hα on screen equals the census's within the share. *Cost:* half a session.
- **C4 — the sprite's scale (#120's sprite half).** *Builds:* the Airy radius tied to a stated pixel scale and distance
  (the view has none: a declared distance is a display choice and says so), or ruled display as it is. *Cost:* a quarter.
- **C5 — the cloud noise's spectral index (#110).** *Builds:* one sourced constant (Larson / Heyer's σ–ℓ) and the octave
  weights derived from it; the pillar rule as a column condition. *Gate:* the realised mean 1 and σ as measured. *Cost:*
  half a session; a reading first.

### D. Time and comparison
- **D1 — the stellar disc building up.** *Exists:* the checkpoint-4 scrubber sweeps every (R, t) field but the stars
  formed, which is at today's radii. *Builds:* `stars_formed_history` at birth radius (**Model**: a new field of the
  chemistry stage, cheap — the migration kernel is already there), the scrubber showing it. *Gate:* the birth-radius
  history integrates to today's stellar mass at every epoch. *Cost:* half a session.
- **D2 — a comparison view.** Two forms: (i) real imagery beside the render — a download of a published image (DSS,
  or an HST mosaic of a Milky-Way analogue) on the owner's word, with the frame set to its pixel scale and band; (ii)
  no download — two seeds, two models or two sets side by side from the same camera. *Gate:* (ii) is a layout; (i)'s
  gate is the band and scale written on the frame. *Cost:* (ii) half a session; (i) one, after the word.
- **D3 — "As JWST".** NIRCam's curves from SVO (a download on the owner's word) and a hexagonal PSF (§2a's named row).
  *Gate:* as S42's WFC3. *Cost:* half a session after the word.

### E. Reach and polish
- **E1 — the design system as designed.** 20 of 21 components unported; the tab structure differs from the mockup.
  *Builds:* the owner rules which structure stands (the built one, or the design's Workflow / Galaxy / System / Science
  with the system a tab), then the components that structure needs. *Gate:* vitest on the panels; the build. *Cost:*
  one to two sessions, by the ruling.
- **E2 — an image-level test for the React app.** *Exists:* none; `shot.py` serves `interface/`. *Builds:* `shot.py`
  (or a sibling) serving `frontend/dist` and capturing the Galaxy tab at the three regimes and the five sets, checked
  against committed frames at a tolerance, skipped without a browser as now. *Gate:* the captures exist and a changed
  gain fails it. *Cost:* half a session. **The one thing that lets every later row prove it did not break the picture.**
- **E3 — the stale records** (App's comment, `basic.py`'s docstring, RENDER_PLAN's table, the `ir` set's status): part
  of A.
- **E4 — performance.** *Exists:* 2 s / 6.9 MB a whole-galaxy render; the region march's 256 budget. *Builds:* the
  render by window (the field's regime needs the whole grid; the stars regime asks for one level's cells and gets the
  whole grid at f4), a cached whole-grid frame on the server. *Gate:* `tools/timings.py` cold / warm with the table
  appended (B2, B6). *Cost:* one session.
- **E5 — deploy.** The command is ready (`./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha>`); CI builds
  the image on every push. The owner's action, after any row that changes the viewer.

---

## 3. A proposed sequence (the owner chooses; nothing starts without the word)

| Row | What | Why in this place | Cost |
|---|---|---|---|
| S46 | **A** the default switch + **E3** the stale records + **E2** the image test | A is ruled; E2 first so every later row has a picture-level gate (B1: the instrument before the thing it certifies) | 1 |
| S47 | **B5** the context (first if the live tab shows black) + **B3** the depth-aware composite | Correctness the eye sees at once; both are viewer-only | 1 |
| S48 | **B1** photometric points → **B2** the young population once → **C2** the level-k stars | One closure test gates all three; the largest correctness gain; needs the owner's leave for the two Model items | 2 |
| S49 | **B4** the first frame's balance, with the surface-brightness-profile gate | After B1, so the points and the field are on one scale | 0.5 |
| S50 | **C1** cluster profiles + **C3** the budget share + **C4** the sprite scale | Resolved objects, all viewer-only | 1 |
| later | **D1–D3**, **C5**, **E1**, **E4**, each on its own word (two downloads among them) | | |

What this leaves out on purpose: anything §8 forbids (a noise texture for the arms, a "natural" colour pass not derived
from the filter integral); any acceptance-row work (pinned); JWST and real-imagery comparison until the owner's word for
the downloads.

---

## 4. How to tell whether it worked

- **The closure test** (B1, B2, C2): the sample's light plus the points' through the set, over a window's cells, equals
  the render's `stars` over the same cells within the sample's noise — at level 0 and at each level the viewer sends.
- **The profile test** (B4): the rendered face-on frame's azimuthally averaged surface brightness against the model's
  published `disc_surface_brightness` through the same set, over 2–20 kpc, to a stated tolerance.
- **The image test** (E2): committed frames of the three regimes and five sets at a tolerance; every row re-runs it.
- **The context test** (B5): a forced loss, then a drawn frame.
- Everything else — the sprite's radius, the tone curve, the budget's cut — is a display choice judged by eye, and is
  labelled so in the set's or the layer's declaration (rule A9: one opinion, held where it is computed).

## 5. Traps
- :5173 is the owner's live tab: a half-applied edit blanks the Galaxy canvas until a hard reload; keep each file
  consistent per edit; never start or stop that server. Checks use `prod` (:8018) after `npx vite build`, stopped after.
- The viewer computes no physics and persists nothing (D5); a page load lands on stage one (D1). A per-object band
  response is the model's to publish, not the viewer's to integrate.
- Downloads (D2(i), D3, C5's paper is read not fetched) need the owner's word; SVO's fetch tool exists for D3.
- A row that touches the catalogue's default run moves window-level pins; brief the builder to grep the inventories.
