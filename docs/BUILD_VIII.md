# BUILD_VIII — the pictures first: the illustrative look

**Status: ADOPTED on the owner's word of 2026-11-23 (D275); rows 105 to 110 run at S105 the same day (D276); rows 111
to 114 run at S106 the same day (D277): both pictures now read as their goal at a glance; rows 115 to 118 run at S107
the same day (D278): the sliders no longer freeze the view and both close-ups read as their goal's close-ups; rows
119 to 122 run at S108 on 2026-11-23/24 (D279): the look holds away from the tuned stands (edge-on, orbited, under
physics only and star-first, rerolled), and neither tuned frame moved nearer its goal; rows 123 to 126 run at S109 on
2026-11-23/24 (D280): both tuned full frames are now their goal's kind of picture at a glance, neither yet its goal at a
second look; #238 and #239 entered in the register on the owner's word.** The
owner, after the status review of that day: "i want to prioritise being able to produce images akin to the goal. the
physics is secondary and can be incrementally improved later", and then, on the lead's list of what the display lacks
and its recommendation: "i accept your recommendations, please begin working on it ... do your best to do as much as
you can in the next 48 hours ... if i'm not around to make rulings, use your best judgement and recommend one, and
document it for me to review later". BUILD_VII stays a DRAFT and is parked where it stands (`batch-r` unmerged, the
register's rows waiting); nothing here touches it. **What is left of this build is section 6.**

## 0. What this build is for

The two goal pictures (`docs/goals/`) are now what the viewer is built toward. Three model batches (P, Q, R) moved
nothing a viewer sees, and the two sourced laws built for the pictures (#234 (ii) on the held head, #232) drew neither
lanes nor strings of pink regions (`READING_PICTURES.md` sections 21 to 25). What stands between the frames and the
goals is drawn here by the viewer, as a declared layer of its own, and the model is left as it is.

## 1. The rules of the order

1. **The illustrative layer.** The viewer has two looks. **Physical** is the viewer as it stood at S104: every visible
   feature a published field or the model's synthetic layer, and the nine committed frames reproduced byte for byte.
   **Illustrative** adds display-only structure, colour and parameters of the viewer's own, tuned to the goal pictures.
   Rule D5 and `RENDER_PHYSICS.md` section 8 are amended for this layer alone (D275); BUILD_VI's "a goal picture is
   never a target" holds for the model and the physical look and is lifted for the illustrative look.
2. **One switch, and it is honest.** `look: "physical"` draws nothing of the layer: the picture test's nine frames are
   captured under it and must stay the committed bytes. Everything the layer draws is named in the panel as illustrative.
3. **No byte under `model/galaxy` moves.** The model hash is asserted unchanged at every close. A step that seems to
   need a model change is put to the owner in `BRIEF.md` and built display-side meanwhile.
4. **Every value a slider** with a copy box (the owner's direction of 2026-10-01); a tuned preset per template ships
   as the illustrative defaults, the owner's to re-tune.
5. **A viewer-only session merges into `main` at its close on the fast gates** (rule C7; as S97 and S98 did). The full
   suite is dispatched to GitHub (`gh workflow run ci.yml --ref <branch>`), never run here (D246).
6. **Every close reads the frames beside the goals** and says in plain words what a viewer sees nearer and what not.
7. **A feature is one file** under `frontend/src/galaxy/illustrative/` (the contract is `index.ts`'s header): its
   sliders, its GLSL for the march's hooks, its channel of the ONE shared map (the march has no spare sampler), a layer
   of its own. A merged head is captured before it is trusted (S105's lesson).

## 2. The rows

| Row | Session | What | Built by | Done |
|---|---|---|---|---|
| 105 | S105 | **the look's switch and the grade**: the look, per-look tuning and copy box, the feature registry and the march's hooks (patches by anchor on the pinned fragment), an asinh curve with a shoulder that keeps hue, saturation, split tone, the point speckle hidden, the field's edge softened, framing and roll; the capture tool (`npm --prefix frontend run look`, `tools/goal_sheet.py`) | Opus (A, then G's fix pass) | S105 |
| 106 | S105 | **the pink regions**: the model's own HII regions drawn at a visible size in pink with a white-blue core, weighted to the arms by the gas's contrast in its own ring (`knots.ts`) | Opus (B) | S105 |
| 107 | S105 | **the lanes**: braided, broken, wiggling brown lanes with feathers along the arm pieces' ridges and two in the bar, a polar map from published geometry; the `veil` hook (`lanes.ts`) | Fable (C) | S105 |
| 108 | S105 | **the arms**: ridge lines of a set width from the stars' contrast, the inter-arm disc dimmed, the bar's cream ellipse, a sparkle of points in groups; the `light` hook (`arms.ts`) | Opus (D; the bar by tuner M) | S105 |
| 109 | S105 | **NGC 4414**: a lace of dust threads with blotches and drawn filaments, patches and young clumps, an inner warmth (`floc.ts`) | Fable (E) | S105 |
| 110 | S105 | **the tuning pass and the close**: one shared map for the layer (the march's seventeenth sampler, the lead's capture of the merged head); each template's sliders tuned together against its goal; an independent review against `main`'s own build and its fixes; the default look | Opus (F, tuners M and N, the reviewer, R); the Fable gate | S105 |
| 111 | S106 | **the base, the tilt, the switch**: the streaks traced to the gas fluctuation map's shear and smoothed (`base.ts`, hook kinds `gas` and later `depth`); `framing.tilt`; the look switch inside a pending generation mended in the shared loader `useLoad.ts` (ruling 13) | Opus (A) | S106 |
| 112 | S106 | **the Milky Way**: one drawn arm skeleton that glow, grain, lanes and regions all read (`skeleton.ts`, `armsSkeleton.ts`; ruling 12); a feature reads another's live parameters (`IllContext.paramsOf`); the pink regions placed on it (`knotsPlace.ts`, `knotsLayer.ts`); the lavender haze, the dark zone round the bar, the slim bar, lumpy grain, a soft fade; five passes | Opus (B, B3, B4, K, B5) | S106 |
| 113 | S106 | **NGC 4414**: the dust in the disc's plane as threads and a branching mesh (`flocNet.ts`, the veil's GLSL), star clouds (`flocClouds.ts`, `CloudsLayer.tsx`), the sky (`sky.ts`, `SkyLayer.tsx`); the blue nucleus traced to #238 and mended in the layer (`base.mend`), the core thinned (`base.core`; #239) | Opus (C, C3, C4, D, N, E) | S106 |
| 114 | S106 | **the gate and the close**: every builder's frames read beside the goals, each lane sent back with its defect list; the merged head captured four times; an independent review against `main`'s own build | Opus (the reviewer); the Fable lead | S106 |
| 115 | S107 | **the sliders freed**: the layer's map planes and the sparkle built in one module worker through the registry's named memos (`illMap.worker.ts`, `illMapJob.ts`, `illMapClient.ts`, `sparkleJob.ts`), the answers seeded into the main thread's cache; nothing of another galaxy drawn for a frame (`illFieldDrawn`; ruling 21); probe `frontend/e2e/ill/sliders.probe.ts` | Opus (W, MW2's one-frame fix) | S107 |
| 116 | S107 | **the `glGetProgramiv` warnings**: traced to a second canvas per landing (the framing keyed on the live template) and removed by keying it on the drawn one in `GalaxyTab.tsx` (ruling 22); probe `frontend/e2e/switch/glprogram.probe.ts` | Opus (GL) | S107 |
| 117 | S107 | **the Milky Way at close range**: the pitch opening outward, the lesser arms spaced evenly, patchy arm light, bunched ragged regions with a dozen complexes and a veil (ruling 26), split lanes, the sparkle placed directly, the colour matched patch by patch | Opus (MW, MW2, MW3); the lead's picks | S107 |
| 118 | S107 | **NGC 4414 at close range**: the brushing traced to the layer's own threads and grain (the map's threads off, ruling 23; `arms.flat` kept at 0, ruling 24), the dust a field of many narrow broken lanes with a pale mesh, dark cores, a veil and wisps (`floc.laneForm`), the rim and a white patch cleared | Opus (NGC, NGC2, NGC3); the lead's picks | S107 |
| 119 | S108 | **the tour**: 222 settled captures and motion frames of both templates under both looks away from the tuned stands (inclination 0-180, azimuth, zoom, rerolls, physics only, star-first, exposure, canvas sizes, an orbit), ranked worst first; nothing committed | Opus (T) | S108 |
| 120 | S108 | **the edge-on handover**: per ray, from 72 to 88 degrees off the axis (`illGraze`, `base.grazeFrom` / `grazeTo`), the layer's thin-screen marks fade and its ink goes into the model's own dust layer (`base.grazeDust` 4); the point layers lifted off the midplane (`pointsPlace.ts`, `base.pointHeight`); bit-exact below the start; two edge-on look captures | Opus (G) | S108 |
| 121 | S108 | **the controls**: physics only draws the physical look, the look shown as suspended (`tuning.ts drawnLook`); the roll held through any orbit (`framing.ts rollAfterLookAt`, `GalaxyView.tsx`), the stand now settling at full quality; star-first points fade at the edge (`points.ts`); the layer's seeds follow a reroll (`illSeeded`), the skeleton's pitch floor; probe `frontend/e2e/s108/controls.probe.ts` | Opus (H; the reviewer's fix) | S108 |
| 122 | S108 | **the leftovers**: the near region clouds off under the look (`base.nearClouds` 0), the Milky Way's arm grain capped before the bloom (`arms.sparklecap` 30: the soft blue discs reduced, not mended), the pitch floor a slider, the prefetch following the drawn look; a rerolled Milky Way's crescents and bar-end gap diagnosed, not mended | Opus (J) | S108 |
| 123 | S109 | **NGC 4414 at full frame**: the disc overfilling the frame and dissolving at its edge (`framing.scale` 0.45, `edge.radius` 16 / `width` 14), a radial fall-off of the drawn light with a blue outer disc (`floc.fall`, `illFlocPts`), brown ink and four log-spiral dust bands (`floc.dustArm*`), a soft cream glow with a white-hot core (`glowShape`, `coreHot`), a multi-scale star-cloud field in the veil (`floc.sc*`), the cloud points capped before the bloom (`cloudCap`); a declared-before-use test for floc's uniforms | Opus (B, B2, B3, B4); the lead's pick | S109 |
| 124 | S109 | **the Milky Way at full frame**: four arms hugging the bar, the skeleton squashed into an oval through the bar's ends (`skelopen`, `skeloval*`, `skelcorebar`), a cream bar held to its ellipse (`barhold`, `sparklebar*`), the roll 15 degrees, the disc at the goal's size; the band read at the arm's nearest point with a 2-D mottle (`skelfoot`, `skelmottle`, `skelbreaks` 0) and a test on its step; the soft blue discs gone (`sparklecap` 10); the pitch slider's freeze mended (`illMapClient.ts`, `illMapJob.ts`) | Opus (A, A2, A3, A4's variant sheets); the lead's picks | S109 |
| 125 | S109 | **the register entry**: #238 and #239 entered in `GALAXY_INPUTS.md` section 11 on the owner's word ("Yes, enter both", 2026-11-24), carried, the owner's; 117 open = 50 + 67; `tests/test_audit.py`'s two pins (e591fd0) | the Fable lead | S109 |
| 126 | S109 | **the gate and the close**: each pass read on pair sheets, merged on both ranges; the lead's picks from variant sheets; the merged head captured; an independent review against `main`'s own build (the lead adds its line) | Opus (the reviewer); the Fable lead | S109 |

## 3. Parallelism and pacing

Fable leads and gates; a builder is Opus unless the work is designing a picture, where Fable builds (rows 107 and 109).
`get_usage` before every spawn; builders in their own worktrees on disjoint files, the lead merges and captures the
merged head. A builder commits at each working step and hands back by two thirds of its context. Long suites go to the
runner. Every brief names a scratch directory of the agent's own.

**At S106** every picture row was built by Opus on the lead's own defect lists: the two Fable builders (the Milky Way's
and NGC 4414's first passes) were cut twice by HTTP 529 (the API overloaded) within fifteen minutes with nothing
committed and were replaced by Opus builders. A brief now says "commit early"; a builder cut by an API error is
restarted on another model rather than resumed into the same overload (D277).

## 4. Rulings taken on recommendation — the owner may re-rule any

| # | Question | Taken |
|---|---|---|
| 1 | Where the build is cut from | `main` c6d7b15. `batch-r` (S104, D274) stays unmerged and untouched; D274 is reserved for it in the decisions' numbering test (D275) |
| 2 | Whether viewer-only sessions merge into `main` unasked | yes, at each close on the fast gates, as the protocol has it for viewer rows; no model byte moves (D275) |
| 3 | The default look | **`illustrative` since S105's gate** (D276): both templates' illustrative frames are nearer their goals than the physical ones. One constant, `DEFAULT_LOOK`; a stored choice is kept; the picture test pins `physical` |
| 4 | What the layer may do | display-only structure placed by published fields (the arm pieces, the contrast fields, the bar's scalars, the regions' places); a field tuned to a picture; colour for appearance; seeds of its own, fixed. It may not change a published number, a readout, a tracer or a Science-tab preview (D275) |
| 5 | The register | frozen for this build: a defect of the physical path found on the way gets a number; the layer's own to-dos are section 6 (D275) |
| 6 | BUILD_VII's rows and the owner's owed rulings | parked, none taken here (D275) |
| 7 | The concurrency | two heavy builders at once on disjoint files (D275). **S105 ran three at once twice, on a fresh window; none died** (D276) |
| 8 | Six sessions or one | rows 105 to 110 ran as ONE session, S105: one merge, one tag (D276) |
| 9 | The model's cloud flecks under the illustrative look | switched off on both templates: the lanes and the network are drawn in their place (D276) |
| 10 | A lane inked over the picture (the `veil` hook) | allowed in this layer: dust in the model's thin layer reads blue-black with half the stars in front of it, so brown lanes are drawn over the ray's whole light. It is a drawing, and said so (D276) |
| 11 | Whether the illustrative frames join the picture test's committed set | no: a pinned frame would fail at the owner's first re-tuning. The two frames of S105's close are committed as plain pictures in `docs/pictures/s105/` (D276) |
| 12 | Whether the layer may draw structure the model does not have | yes, where a goal picture has it: the Milky Way's arms continued to the edge, lesser arms and spurs, the regions placed on the skeleton; NGC 4414's threads, mesh, star clouds, sky stars - display-only, said so in each file's header (D277) |
| 13 | A fix outside the layer for the look-switch defect | taken, in the shared loader `useLoad.ts`: the defect was the layer's and the nine physical frames stayed byte for byte; reviewed independently. **It changes one behaviour of the physical look too:** a mode switched while a generation is pending no longer blanks the field (`main` dropped it to 1.6 % of its light for the whole wait); no frame at rest differs (D277) |
| 14 | #238, the dust transmission's float32 underflow | **not fixed in the physical path**: its fix re-captures committed NGC 4414 frames, the owner's ruling; mended under the illustrative look only (`base.mend`) (D277) |
| 15 | NGC 4414's central dust and the Milky Way's dust placement | thinned by 2 dex inside 1 kpc on NGC 4414; the Milky Way's diffuse dust placement at 0.1; under the illustrative look, display choices, each a slider (D277) |
| 16 | The view | NGC 4414 tilted 6 degrees past the template's inclination, the Milky Way rolled 25 degrees, under the illustrative look only: view choices, each a slider (D277) |
| 17 | The concurrency at S106 | three builders at once most of the session (ruling 7 says two), on a fresh window; none died of the quota; the two Fable builders died of HTTP 529 and were replaced by Opus (D277) |
| 18 | S106's frames | committed as plain pictures in `docs/pictures/s106/`; still not pinned (D277) |
| 19 | `floc.nearAz`, `floc.cloudAz` | NGC 4414's near-side dust bias and rich star-cloud sectors are galactocentric azimuths tuned to the template's stand: they do not follow another camera (D277) |
| 20 | Whether #238 and #239 enter the register | #238 and #239 are two findings of S106, NOT YET ENTERED in the register: the numbers #238 and #239 are reserved for them; entering them needs a two-line change to tests/test_audit.py (the pinned counts 115 -> 117 and the carried row), which waits for the owner's word (D277) |
| 21 | What the layer draws after a switch of galaxy | nothing of the previous galaxy, not for one frame: the empty map until the new galaxy's own planes arrive; the first frame after a landing or a look switch may lack the map's features (D278) |
| 22 | A fix outside the layer for the `glGetProgramiv` warnings | taken, in `GalaxyTab.tsx`: the framing keyed on the drawn template, one canvas per landing; the wasted canvas was the layer's doing (the framing is the layer's) and the physical frames stayed byte for byte; reviewed independently (D278) |
| 23 | NGC 4414's dust | the march's GLSL mesh on a field of narrow lanes, the map's threads off (`floc.netDepth` 0): the threads combed. S106's pick of threads and mesh together is reversed (D278) |
| 24 | `arms.flat` (the model's star contrast divided out without the skeleton) | kept as a slider at 0 on both templates: built on the lead's wrong guess about the brushing, harmless, possibly useful to the owner (D278) |
| 25 | The Milky Way's lesser arms | at 0.7 of the majors (A₂ 0.163): plainer lessers cost the two-armed measure; the owner's `arms.skellevel` (D278) |
| 26 | The regions' veil | premultiplied blending under `knots.place` 1, so the pink stays red over bright arms: a drawing choice; 0 is the plain additive light (D278) |
| 27 | S107's frames | the illustrative frames remain unpinned; S107's two are committed as plain pictures in `docs/pictures/s107/` (D278) |
| 28 | #238 and #239 | still wait for the owner's word; nothing entered in the register (D278) |
| 29 | "Physics only" under the illustrative look | draws the physical look, the illustrative look shown as suspended: with the physics' layers off the layer has no published structure to draw on. Greying the control out, or giving the Milky Way a structure of its own, not taken (D279) |
| 30 | The edge-on handover | from 72 to 88 degrees off the axis, per ray, the layer's thin-screen marks fade and the model's volume is drawn in the layer's colours; `base.grazeDust` 4 stands in for the clouds' extinction ruling 9 switched off (the clouds are not loaded back edge-on); the point lift scales with the handover (none face-on, so the tuned frames stay as they were) (D279) |
| 31 | A fix outside the layer for the roll | taken, in `GalaxyView.tsx`: the roll applied after the orbit (both looks pass through it; under the physical look the roll is 0); the swing was the layer's doing and the nine physical frames stayed byte for byte; reviewed independently. Its side effect (the Milky Way's stand settles and marches at full quality) moved the Milky Way's illustrative frames slightly: accepted (D279) |
| 32 | `points.edge` | applies to the star-first mode's stars and clusters only, not the field mode's regions (D279) |
| 33 | The layer's seeds | follow the generated galaxy's `pattern_seed` and `texture_seed`; the template's own seeds draw the tuned picture; a rerolled skeleton's pitch has a floor, 10 degrees, a slider (`arms.skelpitchmin`) (D279) |
| 34 | The near regime's region clouds under the look | not drawn as extinction (`base.nearClouds` 0) on both templates: a change in what `GalaxyTab.tsx` passes to `RegionVolume`; the physical look unchanged (D279) |
| 35 | The Milky Way's arm grain | capped before the bloom (`arms.sparklecap` 30): it moves the Milky Way's frames; the lead compared the close-up before and after beside the goal's crop and took it (D279) |
| 36 | A rerolled Milky Way's crescents and bar-end gap | not mended behind a reroll-only gate: they are the default Milky Way's inner zone, mended with it next session, which may move the default frames (D279) |
| 37 | S108's frames | committed as plain pictures in `docs/pictures/s108/` (the two stands and the two edge-on captures); still not pinned (D279) |
| 38 | #238 and #239 | still wait for the owner's word; nothing entered in the register (D279) |
| 39 | NGC 4414's close stand turned 1.6 degrees | accepted: the roll about the true line of sight is the right one, and the close-up is the same picture (D279) |
| 40 | The Milky Way's view settling | accepted: one full-quality march (up to about 280 ms) after each move, the quality the look was meant to have, where `main`'s never-settling view marched at 2 of 8 sub-samples on every frame; a lower sub-sample ceiling under the look is the owner's to ask for (D279) |
| 41 | How a pass is merged | only if it is a gain at both ranges (full frame and close-up); a lane that does not converge under judged passes is switched to variant sheets on named axes, the goal the first tile, picked by the lead (D280) |
| 42 | NGC 4414's framing | the disc overfills the frame (`framing.scale` 0.45) as the photograph's does; the layer draws a radial fall-off of its own (display only) (D280) |
| 43 | NGC 4414's dust and tone | the lead's pick between the third and fourth passes (`dustArmClear` 0.82, depth 3.7, `inkOpaque` 0.5, `inkBrown` 0.8, `coreHot` 1.5, `grade.gain` 0, `grade.split` 0.1); the close-up accepted a little darker in its outer half than S107's (the fall-off is real there too) (D280) |
| 44 | The Milky Way's roll | 15 degrees, the bar at the goal's angle (ruling 16's 25 re-ruled) (D280) |
| 45 | The Milky Way's winding, width, tone and lanes | the lead's picks: from the variant sheets `arms.skelpitch` 0.9, `sparklecap` 10 (ruling 35's 30 replaced), knots `sizeMin` 20 / `sizeMax` 80, lanes `width` 65, `barglow` 1.5, `skelwidthgrow` 0.3; from the lead's fourteen 600-px variants `arms.floor` 0.4, `lavender` 0.35, `skelcore` 0.35, `skelcoreout` 1.2, `cap` 1.2, `sparklegain` 250000, `skelwidth` 0.75, `lanes.redness` 3.5, `lanes.depth` 2.0, `grade.gain` -2.5, `grade.saturation` 1.15 (the sheets' first defaults were near-black between the arms at full size) (D280) |
| 46 | The arms map's worker rebuild | about 0.8 to 0.9 s accepted for now: no stall, the picture arrives later after a skeleton slider settles (D280) |
| 47 | S109's frames | committed as plain pictures in `docs/pictures/s109/` (the two stands and the two edge-on captures; the close-ups not committed); still not pinned (D280) |
| 48 | #238 and #239 | **now ENTERED in the register on the owner's word** ("Yes, enter both", 2026-11-24): carried, the owner's, 117 open = 50 + 67. Rulings 20, 28 and 38 stand as the record of the wait. Their rulings (#238's physical fix with its re-capture, #239's central column) stay the owner's (D280) |

## 5. What done means

Each template's illustrative frame set beside its goal reads as the same kind of picture to the owner's eye: the
Milky Way a blue-white barred spiral with a warm bar, narrow arms carrying brown lanes and strings of pink regions; NGC
4414 a warm-cored flocculent disc under a brown filament network with blue-white clumps outside. The physical look
unchanged byte for byte. The distance still left is stated at the close, per picture. **S105's gate: both read as the
same kind of picture; the owner's eye has not yet ruled** (`READING_PICTURES.md` Part S105). **S106's gate: both
read as their goal at a glance; what remains is texture and finish at close range, not composition; the owner's eye
has still not ruled** (Part S106). **S107's gate: both close-ups read as their goal's close-ups; what remains is
strength and balance, most of it within the owner's sliders, and a few forms; the owner's eye has still not ruled**
(Part S107). **S108's gate: the look holds away from the tuned stands (edge-on, orbited, under physics only and
star-first, rerolled); at the tuned stands neither frame moved nearer its goal, and both full frames are still plainly
unlike their goals in the ways section 6 lists** (Part S108). **S109's gate: both tuned full frames are now their
goal's kind of picture at a glance; neither is yet its goal at a second look: what separates them is texture and
balance (the Milky Way's speckle against clumps, its arm weights and lanes; NGC 4414's dust density and colour, its
cloud texture), most of it within the owner's sliders' reach, some of it new drawing; the owner's eye has still not
ruled** (Part S109).

## 6. What is left, in the order of what a viewer would gain

1. **The owner's own tuning pass** on the live sliders (the Tuning panel's Illustrative group, by feature, with a
   filter; no slider freezes the view) **and the owner's rulings**: #238 (the dust transmission's float32 underflow:
   the physical fix and the re-capture of the four NGC 4414 committed frames) and #239 (the model's central extinction
   on NGC 4414). Both are now entered in the register on the owner's word (ruling 48); the rulings are still open.
2. **The Milky Way**: the arm grain as knotted clusters and cumulus-like clumps with a turquoise tint, not a uniform
   fine speckle; four nearer-equal, narrower arms with more wraps (ours two broad and dominant), without bringing back
   the target of rings; the lanes as broken reddish-brown filaments strung with small pink regions (ours thin
   continuous dark strokes, the pink regions fewer and larger); a brighter grainy bar with a definite edge and the dark
   ground beside its long sides; the tight inner arcs along the bar's flanks; a smooth outer glow (ours ragged grain on
   a dim haze) and the faint far arm at the right.
3. **NGC 4414**: a denser, warmer-brown dust network covering about a third of the inner and middle disc, strongest on
   the near side (ours sparser and greyer); lumpy cauliflower clouds in place of the even sand with heaps; a blue-grey
   outer haze (ours grey-white clumps on dark); a slightly tighter glow round the core; about a hundred bright points
   in the disc (the photograph's 97; ours 20 by the tool).
4. **Away from the tuned stands**: the Milky Way edge-on (busy with regions and grain along the lane, hardly a bulge);
   the close stands, which no longer frame what they were chosen for (the Milky Way's spiral moved under its close
   stand; NGC 4414's close stand is darker in its outer half than S107's, ruling 43); exposure +3 washes the look out;
   NGC 4414's faint brushing between 78 and 82 degrees.
5. **Cost and the rest**: the arms map's worker rebuild of about 0.8 to 0.9 s (the picture arrives late after a
   skeleton slider settles, ruling 46); `FluxPoints`' instrument wing pass reads the unlifted position inside the
   handover (at most about 0.6 kpc, the instrument only; S108's low item); a third template would want its own preset.
