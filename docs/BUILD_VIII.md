# BUILD_VIII — the pictures first: the illustrative look

**Status: ADOPTED on the owner's word of 2026-11-23 (D275).** The owner, after the status review of that day: "i want
to prioritise being able to produce images akin to the goal. the physics is secondary and can be incrementally improved
later", and then, on the lead's list of what the display lacks and its recommendation: "i accept your recommendations,
please begin working on it ... do your best to do as much as you can in the next 48 hours ... if i'm not around to make
rulings, use your best judgement and recommend one, and document it for me to review later". BUILD_VII stays a DRAFT and
is parked where it stands (`batch-r` unmerged, the register's rows waiting); nothing here touches it.

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

## 2. The rows

| Row | Session | What | Builders | Gate |
|---|---|---|---|---|
| 105 | S105 | **the look's switch and the grade**: `look`, the illustrative parameters' table, an asinh stretch that keeps hue, saturation, the point speckle hidden at galaxy scale, the field's hard edge softened, the framing; a committed capture tool that sets a frame beside its goal | Opus | fast gates; the nine frames byte for byte under `physical`; the lead's eye on the sheets |
| 106 | S106 | **the pink regions**: HII regions drawn at a visible size in H-alpha's colour with a white-blue core, gathered to the arms by the published contrast | Opus | as 105 |
| 107 | S107 | **the lanes**: continuous, narrow, translucent, reddening dust lanes along the arms' ridges and the bar's leading edges, with feathers | Fable or Opus | as 105 |
| 108 | S108 | **the arms**: the young light sharpened onto the ridges, and its sparkle | Opus | as 105 |
| 109 | S109 | **NGC 4414**: the filament network and the patchy young clumps of a flocculent disc | Fable or Opus | as 105 |
| 110 | S110 | **the tuning pass and the close**: the presets tuned against the goals, the illustrative frames committed, the defects found on the way (#236 among them), the documents | Fable gate, Opus | as 105; the dispatched suite read |

Rows 106 to 109 may run two at a time where their files are disjoint (section 3); the order is by what a viewer gains.

## 3. Parallelism and pacing

Fable leads and gates; a builder is Opus unless the work is judging or designing a picture, where Fable builds.
`get_usage` before every spawn; at most two heavy builders at once, on disjoint files in their own worktrees, with one
light runner beside them; the lead merges. A builder commits at each working step and hands back by two thirds of its
context. Long suites go to the runner.

## 4. Rulings taken on recommendation — the owner may re-rule any

| # | Question | Taken (D275) |
|---|---|---|
| 1 | Where the build is cut from | `main` c6d7b15. `batch-r` (S104, D274) stays unmerged and untouched; D274 is reserved for it in the decisions' numbering test |
| 2 | Whether viewer-only sessions merge into `main` unasked | yes, at each close on the fast gates, as the protocol has it for viewer rows; no model byte moves |
| 3 | The default look on the templates | `physical` until the lead's gate finds the illustrative frames nearer their goals on both templates, then `illustrative`; the picture test's nine frames stay `physical` either way |
| 4 | What the layer may do | display-only structure placed by published fields (the arm contrast, the bar, the regions' places); a field tuned to a picture; colour for appearance. It may not change a published number, a readout, a tracer or a Science-tab preview |
| 5 | The register | frozen for this build: a defect of the physical path found on the way gets a number; the layer's own to-dos live in this file |
| 6 | BUILD_VII's rows and the owner's owed rulings | parked, none taken here |
| 7 | The concurrency | two heavy builders at once on disjoint files (the owner's "as much as you can in the next 48 hours") |

## 5. What done means

Each template's illustrative frame set beside its goal reads as the same kind of picture to the owner's eye: the
Milky Way a blue-white barred spiral with a warm bar, narrow arms carrying brown lanes and strings of pink regions; NGC
4414 a warm-cored flocculent disc under a brown filament network with blue-white clumps outside. The physical look
unchanged byte for byte. The distance still left is stated at the close, per picture.
