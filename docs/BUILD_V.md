# BUILD_V — the fifth build: everything that remains, batched so the work runs ahead of the suites

**Status: ADOPTED 2026-11-02 at S82 (D248; the owner's word "adopt the plan"), as drafted at S81's open on the owner's
word ("redesign the plan for the remaining work to try to get as much done as possible"; "there's ample usage remaining
for the next two days").** Its §6 ruling 1 is taken by the adoption; rulings 2–6 stand as recommendations until the
owner takes them (S84 needs ruling 2, S86 ruling 4). S81 (the viewer batch of D246) was its first row, closed on D247.
Everything here is `[inferred]` design unless tagged; the register's items are named by their numbers in
`GALAXY_INPUTS.md`, the viewer tasks by `VIEWER_TASKS.md`'s rows.

---

## 0. What this build is for

Four builds are done and every board row is ticked (S0–S80). What remains lives in three lists: the register's 124
carried items (111 of them the model's), the viewer task list's open rows (T2, T3, T8, T10, T11, T13–T17, T19, T20),
and BUILD_IV's deployed half (T19, #204, #205). This build takes all of it, in an order chosen for one thing: **the
tests gate a batch, not an item.** Rule C7 as re-amended (D245, D246): every session closes on the fast gates (~15 min);
the local full suite runs on the owner's word, asked once per model batch; CI's full suite runs nightly.

## 1. The three rules of the order

1. **Viewer first.** Viewer sessions change nothing under `model/galaxy`, so they close on the fast gates alone. They
   run back to back while the owner decides nothing (D212's auto-continue: stop only for a ruling that is theirs).
2. **The register pass before any model batch.** One docs-only session rules each of the 111 model items *permanent*
   (a property of the model's scope or of its sources) or *a defect in a batch*, so each batch builds what is actually
   wrong. The owner accepted this on 2026-11-02.
3. **Model work in batches by stage group**, each batch two or three sessions on one branch, the affected subset
   mid-session (C7), **one full suite at the batch's close, run by the owner** (asked by the lead), the merge waiting on
   its EXIT line. Three batches, three suites, in place of one suite per debt.

## 2. The rows

| Row | Session | Phase | What | Lead / builders | Gate |
|---|---|---|---|---|---|
| 81 | S81 | V-1 | **The landing's last tenths**: #208 (b) the mesh off the main thread; the blackbody table a fifth head-start load; T14's sub-sample cut while the camera moves, the counts as tuning sliders | Fable; one Opus builder | fast gates; the probe quiet; frames byte for byte |
| 82 | S82 | V-2 | **S68's viewer debts and the zoom's seams**: #186 the merger ranges on the wire, #187 the swap's dependent loaders, #188 the landing keeps the old field, #190 the drawer and the caption, #172 the zoomed view as one picture, #178 the clamped instrument box; #189 the reference client's generate (or its retirement, ruling 2 of BUILD_IV) | Fable; two Opus builders on disjoint files (the loaders / the view) | fast gates; the walk's request set; frames byte for byte except where #172 and #178 change them knowingly, regenerated with the reason |
| 83 | S83 | V-3 | **Robustness and comparison**: T13 the renderer survives a lost WebGL context; T16 (i) two seeds / sets side by side and (ii) a picture file beside the frame at a stated band and scale; T11 "as JWST" (NIRCam's curves, a hexagonal PSF; the download accepted 2026-11-02) | Fable; two Opus builders | fast gates; frames byte for byte |
| 84 | S84 | V-4 | **T17, the design system as designed** — on the structure ruled in §6 | Opus lead, Fable at the close | fast gates; the picture test re-captured knowingly |
| 85 | S85 | R | **The register pass**: the 124 carried items each ruled permanent (with the reason written in, B5) or assigned to batch M1 / M2 / M3 below; the viewer's remaining items confirmed done or carried; `RESEARCH_AREAS.md` read beside the arms' items | Fable alone (judgement) | docs and register tests; the count pin moved once |
| 86–88 | S86–S88 | M1 | **The arms and the bar** (the pin lifted for the batch): #142 the finite-thickness reduction of the forcing with #209's floor by it; #138–#139 the arm-number law and the phases; #141, #143, #144; the bar's #145–#149; the pieces' #152–#157; `READING_ARM_*.md` the readers | Opus lead per session, Fable at the gates; two Opus builders on disjoint stages | subset mid-session; **the full suite once at S88's close, the owner's run**; the frames regenerated with the reason; the goal pictures beside |
| 89–90 | S89–S90 | M2 | **The clouds, the dust and the gas**: #128 the heating's placement applied; #167–#169, #180–#182 the clouds' law, layer and slab; #202 the diffuse share's step; #197 the stars' and remnants' ring draws; #158–#165 the censuses' and spurs' debts | Opus lead, Fable at the gates; two Opus builders | subset mid-session; **one full suite at S90's close**; frames regenerated |
| 91–92 | S91–S92 | M3 | **The populations and the ionized gas**: T2 / #114 points through the filter set, T3 / #115 the young population once, #113, #171, #184, #174–#176; #100–#101, #117–#119 and T10's forbidden lines (the FSPS grid download accepted 2026-11-02); T15; T8 | Opus lead, Fable at the gates; two Opus builders | subset mid-session; **one full suite at S92's close**; the acceptance table's rows re-read |
| 93 | S93 | A | **Audit VI**: the three batches read blind against their sources and the register, as Audit V read BUILD_III | Fable | docs tests; no number moved without a decision |
| — | the owner | D | **T19 the deploy** (the subscription when its cost suits), **then the deployed probe** (#204, #205, F5, S80's (a)); then **T20** share links and the queue (#203) as a session of its own | the owner; then Opus | the deployed table appended to D244 |

Thirteen sessions, three full suites, the deploy whenever the owner takes it. Rows 86–92's membership is the register
pass's to settle (S85): a batch takes what S85 rules a defect, in the order above; an item ruled permanent leaves it.

## 3. Parallelism and pacing

- **Two agents at once, one heavy** (the owner's rationing): a session's two builders own disjoint files; the lead
  cherry-picks. Two *sessions* never run at once on one day (S78/S79's renumbering is the lesson).
- **Fable where judgement is the work**: the viewer rows' reviews, the register pass, the gates of the model batches,
  Audit VI. **Opus leads the model batches' building sessions** on a brief from the gate before, as BUILD_III ran.
  The Fable weekly limit is the binding one (48 % used at S81's open): when it passes ~85 % the remaining viewer rows
  run with Opus leads too, Fable only at the closes.
- **Each batch's suite is the owner's overnight run**: at the batch's last session the lead commits, asks, and the
  owner starts `uv run pytest` backgrounded with its EXIT line to a file; the next morning the merge. The nightly CI
  run on the merge is read at the open after.
- **Auto-continue** (D212's standing word): sessions run back to back; the lead stops only for a ruling that is the
  owner's, and asks for it in the close that reaches it.

## 4. What each session reads

`BRIEF.md` (written by the close before), this plan's row, the register items it names, the readers' files its row
names, and — for a model row — the stage's tests. Nothing else by default (GALAXY_PLAN §5a).

## 5. The gates, verbatim where they are new

- A viewer row: vitest, `typecheck`, `typecheck:e2e`, the picture test's captures byte for byte (`GALAXYGEN_PICTURE=1`,
  the bundles), the docs and register tests; the probe quiet where a row names it; no `fetch(` added (D2).
- A model batch: the stage's subset green at every commit; `galaxy.specs` to its last row; the acceptance table's rows
  that the batch touches re-read and their misses written in; the frames regenerated with the reason and the goal
  pictures beside them (the yardstick); the full suite once, the owner's run, before the batch's merge; the hash moves
  once per batch — one model image and pin at the next deploy.
- The register's count pin (`tests/test_audit.py`) and its carried-row literal move with every entry, as before.

## 6. Rulings needed from the owner

| # | Question | Recommendation |
|---|---|---|
| 1 | Adopt the plan and its order | adopt; S81 already runs row 81 |
| 2 | T17's structure: keep the tabs as they stand since V9 (Science / Galaxy with the edit panel) and port the mockup's components to them, or restructure to the mockup's tabs | keep the tabs; port the components |
| 3 | #189: finish the reference client's generate, or retire it to a route demonstration (BUILD_IV ruling 2 (a)) | retire it |
| 4 | The pin lifted for M1, M2 and M3 as batches (not per item) | yes, per batch, the hash moving once per batch |
| 5 | Audit VI at the end, or none | at the end: one session that reads what three batches did |
| 6 | Where the deploy falls | whenever the owner takes it; nothing in rows 82–93 waits on it |

## 7. What done means

Every register item discharged or permanent with its reason; the viewer task list empty but for the owner's own rows
(T19, T20 if not yet taken); the frames at their closest to the goal pictures with the distance stated; the model's hash
pinned in a deployed gateway, or, if the deploy is not taken, the images for it green in CI at the final hash; three
nightly runs green on the three batch merges.
