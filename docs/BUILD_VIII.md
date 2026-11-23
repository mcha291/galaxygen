# BUILD_VIII — the pictures first: the illustrative look

**Status: ADOPTED on the owner's word of 2026-11-23 (D275); rows 105 to 110 run at S105 the same day (D276); rows 111
to 114 run at S106 the same day (D277): both pictures now read as their goal at a glance.** The
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
| 13 | A fix outside the layer for the look-switch defect | taken, in the shared loader `useLoad.ts`: the defect was the layer's and the nine physical frames stayed byte for byte; reviewed independently (D277) |
| 14 | #238, the dust transmission's float32 underflow | **not fixed in the physical path**: its fix re-captures committed NGC 4414 frames, the owner's ruling; mended under the illustrative look only (`base.mend`) (D277) |
| 15 | NGC 4414's central dust and the Milky Way's dust placement | thinned by 2 dex inside 1 kpc on NGC 4414; the Milky Way's diffuse dust placement at 0.1; under the illustrative look, display choices, each a slider (D277) |
| 16 | The view | NGC 4414 tilted 6 degrees past the template's inclination, the Milky Way rolled 25 degrees, under the illustrative look only: view choices, each a slider (D277) |
| 17 | The concurrency at S106 | three builders at once most of the session (ruling 7 says two), on a fresh window; none died of the quota; the two Fable builders died of HTTP 529 and were replaced by Opus (D277) |
| 18 | S106's frames | committed as plain pictures in `docs/pictures/s106/`; still not pinned (D277) |
| 19 | `floc.nearAz`, `floc.cloudAz` | NGC 4414's near-side dust bias and rich star-cloud sectors are galactocentric azimuths tuned to the template's stand: they do not follow another camera (D277) |

## 5. What done means

Each template's illustrative frame set beside its goal reads as the same kind of picture to the owner's eye: the
Milky Way a blue-white barred spiral with a warm bar, narrow arms carrying brown lanes and strings of pink regions; NGC
4414 a warm-cored flocculent disc under a brown filament network with blue-white clumps outside. The physical look
unchanged byte for byte. The distance still left is stated at the close, per picture. **S105's gate: both read as the
same kind of picture; the owner's eye has not yet ruled** (`READING_PICTURES.md` Part S105). **S106's gate: both
read as their goal at a glance; what remains is texture and finish at close range, not composition; the owner's eye
has still not ruled** (Part S106).

## 6. What is left, in the order of what a viewer would gain

1. **The owner's own tuning pass** on the live sliders (now about 300; the Tuning panel's Illustrative group, by
   feature, with a filter).
2. **The owner's ruling on #238** (the dust transmission's float32 underflow: the physical fix and the re-capture of
   the four NGC 4414 committed frames) **and on #239** (the model's central extinction on NGC 4414).
3. **The Milky Way at close range**: the arms' patchy cyan light (ours are smooth bands with points on them); large
   ragged region complexes; branching lanes; the first arm leaving the bar's ends clearly; the stray blue blob right of
   the bar (the model's young clumps on the inner rings) and the lone region at a faded outer arm end.
4. **NGC 4414 at close range**: lanes of many widths; crisp star fields between the dust; the rim's dust brown; a
   sharper nucleus; the cloud discs (tauC) that the core's thinning does not reach read as dark blots at close face-on
   stands.
5. **The cost**: the map's rebuild with NGC 4414's threads on (measure it; a worker needs an asynchronous map
   contract); three 5-second vitest tests (`hstPsf`, `sphere`, `floc`) time out when the machine is loaded (they pass
   alone and with `--maxWorkers=4`).
6. **The `glGetProgramiv` warnings** on a canvas remount: not reproduced at S106, cause unknown.
7. **A third template** would want its own preset (a skeleton or a plane-style network).
