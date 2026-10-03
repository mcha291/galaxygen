# RESEARCH_AREAS — open problems that need reading or a new mechanism before they can be built

Opened 2026-10-02 (S50) on the owner's word: "create a document called Research_Areas and document the problem with
spiral shape in it." **What belongs here:** a known shortfall of the model whose remedy is not yet a task — the
mechanism is not chosen, or its numbers have not been read. A task with a gate goes in `VIEWER_TASKS.md`; a debt with
a ruling goes in `GALAXY_INPUTS.md` §11; a passing thought goes in `future_ideas.md`. An entry here says what the model
does, what is wrong with it, why it is that way, what it costs, and which directions are worth reading — and **every
source named below is `[recall]` until a session reads it** (RESUMING: a citation is read before it enters code).

## 1. The spiral's shape is a template, not a result

### What the model does
The bar and the arms are one formula on the (R, φ) grid, `pattern_density_contrast` `[verified:
model/galaxy/stages/pattern.py, ArmPattern.contrast]`:

    Σ(R, φ) / Σ(R) = 1 + A · w_arm(R) · cos m(φ − ln R / tan p) + B · w_bar(R) · cos 2(φ − φ_bar)

- **Derived from the halo and the disc** (the `bar` stage, no draw): the bar's half-length, the disc's share of the
  rotation and its shear, the range of arm numbers the disc amplifies (`swing_arm_min` to `swing_arm_max`), and the
  mean arm amplitude `[verified: pattern.py, compute_bar]`.
- **Drawn on `pattern_seed`** (the `pattern` stage): the arm number m (2 to 6, weighted by that range), the pitch
  angle p (the shear trend is weak, so the draw dominates), the arm amplitude's residual, the bar's amplitude and
  its pattern speed `[verified: pattern.py, compute_pattern]`.
- **Fixed for every galaxy:** the functional form above. The starting conditions and the seed choose five numbers
  (m, p, A, B, the bar's length); nothing chooses the shape.

### What is wrong with it
1. **Every arm is a perfect logarithmic spiral**: one pitch angle from the bar's end to the disc's edge.
2. **The arms are identical and evenly spaced**: one m, one amplitude, phases 2π/m apart.
3. **An arm's cross-section is a cosine**: as wide as the gap between arms, with no sharp edge. At the Sun's radius
   the default seed's contrast runs 0.60 to 1.40 `[verified: a probe at S50, the repo unchanged]`.
4. **Nothing is irregular**: no spurs, feathers, branches or forks, no arm that fades and restarts, no flocculent
   patches. A five- or six-armed draw is a tidy five- or six-fold rosette, not a flocculent disc.
5. **There is always a bar**: its amplitude is drawn about the barred sample's median, so no galaxy is unbarred
   `[verified: pattern.py, BAR_CONTRAST's about]`.
6. **The gas has no pattern of its own.** Everything placed "on the arms" — the stars, today's star formation
   (`sfr_modulation`), the HII regions' light — reads this one stellar contrast `[verified: sfh_azimuthal.py;
   api/service.py, _render]`. A real disc's gas shocks at the arm's inner edge into a lane far narrower than the
   stellar arm `[recall]`.
7. **The arms have no pattern speed**, so nothing downstream of an arm (the age gradient across it, the offset
   between dust, HII regions and young stars) can be placed `[verified: GALAXY_INPUTS.md §11, #81]`.

### Why it is that way
Arms emerge from the self-gravity of a shearing disc, and the only calculation that makes a particular arm appear is
a simulation stepped through time; the model is closed-form by design (rule A1: iteration lives inside a stage and
terminates in advance), which is what lets a changed input give a new galaxy in seconds. Swing amplification does
give closed-form predictions — which m a disc amplifies, how strongly, the trend of pitch with shear — and the model
uses those `[verified: pattern.py, swing_window; GALAXY_INPUTS.md, "They are not rival relations"]`. It gives no closed form for *where each arm
goes*, so the predicted statistics are drawn onto the simplest shape that carries them. The seed is honest:
simulations started from the same disc with different noise grow different arms, with scatter comparable to observed
galaxies `[verified: GALAXY_INPUTS.md, the same section, citing Grand et al. 2013]`. **The shortfall is not that the pattern is
drawn; it is that what is drawn is too regular.**

### What it costs today
- **The dust follows the stars' arms, so it mutes them instead of drawing lanes.** Since D207 the dust is placed by
  this contrast: 2.3 times heavier on an arm than between arms at the Sun's radius (A_V 0.72 against 0.31). But the
  stars sit on the same arms, so an arm loses a little more of its own light (0.747 let through against a gap's
  0.874) and stays far brighter than the gap; a ring's face-on V light falls 1.3 % there `[verified:
  tests/test_dust_layer.py]`. A dark lane needs the dust where the stars are not: direction d below.
- **The picture reads as a diagram.** The owner's reference (a face-on Milky Way concept image, S50) differs from the
  render first in irregularity: uneven arms, spurs, dark lanes on the arms' inner edges.
- **RENDER_PHYSICS §8 forbids the viewer from repairing it**: no structure the model does not publish. Any
  irregularity has to be the model's, seeded and sourced.

### Directions worth reading (none chosen)
| # | Direction | What it would add | What must be read or ruled first |
|---|---|---|---|
| a | **Several modes at once**: the contrast as a sum over m, each with its own amplitude and phase | Uneven arms, forks where modes beat, flocculence at high m | A sourced amplitude spectrum over m (the S4G Fourier decompositions the bar's amplitude already cites); whether phases are drawn or locked to the bar |
| b | **The arm number changing with radius**: the local swing parameter rises outward | Two arms inside branching to four or more outside | The local form of X is already in `pattern.py` as the named alternative (D'Onghia 2015: two arms at 4.5 kpc, five or six at R₀); how one mode hands over to the next |
| c | **Pitch varying along an arm**: arms as joined segments of different pitch | Kinks and arcs instead of one curve | The measured distribution of segment lengths and pitch changes (Honig & Reid 2015; Díaz-García et al. 2019) |
| d | **A gas response distinct from the stars'**: a narrow ridge offset to the arm's inner edge inside corotation | Real dust lanes; the dust → HII → young-star sequence across an arm | A spiral pattern speed (#81); the shock's width and offset as closed forms (Roberts 1969; Gittins & Clarke 2004) |
| e | **Spurs and feathers** off the gas ridge | The fine structure of a grand-design arm | Their spacing as a Jeans length of the arm's gas (Kim & Ostriker 2002; La Vigne et al. 2006); needs (d) first |
| f | **A bar that can be absent**: the bar's presence as a draw | Unbarred and weakly barred galaxies | The bar fraction against disc dominance or mass; what the bar-derived rows (15–17) mean without one |
| g | **A pattern library**: arms read from precomputed simulations, indexed by disc dominance and shear | Genuinely emergent shapes | The owner's word on a data download; a library is a lookup, not a derivation (A3) — the last resort |

### What any remedy must keep
- **Every ring's mean stays 1**, so no radial profile and no acceptance row moves (`tests/test_pattern.py`'s
  ring-mean gate).
- **Reproducible from `pattern_seed` alone**, and evaluated at a point without the whole grid: the catalogue draws
  each star's azimuth from the contrast inside its own cell (D60, per-region determinism).
- **Closed form and priced**: no integrator (A1), a cost row in `tools/timings.py`.
- **Sourced amplitudes**: a new degree of irregularity enters as a measured distribution with its residual seeded
  (§4b's verdict C), never as a display constant.
- **One pattern for everything that follows it**, or a stated reason a component has its own (direction d).

*Status: recorded, not scheduled. The model is pinned (the owner, 2026-10-01); any direction above needs the owner's
word and a reading session before a build.*
