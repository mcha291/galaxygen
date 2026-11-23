# BUILD_VIII — the pictures first: the illustrative look

**Status: ADOPTED on the owner's word of 2026-11-23 (D275); rows 105 to 110 run at S105 the same day (D276).** The
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

## 3. Parallelism and pacing

Fable leads and gates; a builder is Opus unless the work is designing a picture, where Fable builds (rows 107 and 109).
`get_usage` before every spawn; builders in their own worktrees on disjoint files, the lead merges and captures the
merged head. A builder commits at each working step and hands back by two thirds of its context. Long suites go to the
runner. Every brief names a scratch directory of the agent's own.

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

## 5. What done means

Each template's illustrative frame set beside its goal reads as the same kind of picture to the owner's eye: the
Milky Way a blue-white barred spiral with a warm bar, narrow arms carrying brown lanes and strings of pink regions; NGC
4414 a warm-cored flocculent disc under a brown filament network with blue-white clumps outside. The physical look
unchanged byte for byte. The distance still left is stated at the close, per picture. **S105's gate: both read as the
same kind of picture; the owner's eye has not yet ruled** (`READING_PICTURES.md` Part S105).

## 6. What is left, in the order of what a viewer would gain

1. **The owner's own tuning pass** on the live sliders (the Tuning panel's Illustrative group, by feature, with a filter).
2. **The streaky, brushed texture under everything** on both templates: it is the model's own light (the synthetic
   layer's maps in the march), no illustrative slider reaches it; a smoothing or a switch for it under this look.
3. **The Milky Way**: the disc fills about 70 % of the frame against the goal's 90 %; fewer and broader arms than the
   goal's (ours are the model's own); the arms' fine pale grain; the regions a little like confetti on one outer arm.
4. **NGC 4414**: the network is coarser and more brushed than the photograph's feathered one; the white clumps read as
   dashes, and the outer left lacks the photograph's star clouds; the disc is rounder (the template's inclination).
5. **The cost**: the network's map takes about a second to rebuild per shaping change on the main thread (debounced
   since S105, still a stall); a worker needs an asynchronous map contract.
6. **A third template** would want its own preset; nothing here is per-galaxy beyond the per-template defaults.
