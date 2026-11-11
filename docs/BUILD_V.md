# BUILD_V — the fifth build: everything that remains, batched so the work runs ahead of the suites

**Status: ADOPTED 2026-11-02 at S82 (D248; the owner's word "adopt the plan"), as drafted at S81's open on the owner's
word ("redesign the plan for the remaining work to try to get as much done as possible"; "there's ample usage remaining
for the next two days").** Its §6 ruling 1 is taken by the adoption and **rulings 2–6 by the owner's word of 2026-11-02
("Yes, all five", D252), each as recommended**; S84 runs on ruling 2, S86 on ruling 4. S81 (the viewer batch of D246) was its first row, closed on D247. **S86 closed 2026-11-03 into `batch-m1` (D254: #139, #142, #198 struck, #154's table rebuilt, #186 on the wire, four permanent at the gate; the hash moves at S88).** **S87 closed 2026-11-03 into `batch-m1` (D255: the owner's four rulings taken — #209 discharged, #80's law and pin, #145 a check, #152 kept; #148 one clock, #212 opened; six bounds ruled at the gate; rows 15–17's referent and #212 the owner's for S88).** **S88 closed 2026-11-03 into `batch-m1` (D256: the six bounds applied, both answers built — the defaults judged, `MERGER_HEATING` 90.6 — #154's table reproducible, the hash 244c8bda… once, the frames regenerated with no frame nearer the goal pictures, the S55 reference's rewrite tried and reverted, #212 discharged, #152 permanent, #213 and #214 opened to M2; `batch-m1` → `main` on the owner's full suite).** **`batch-m1` merged into `main` 2026-11-04 (7aed48b, tag s88) on the full suite run here on the owner's word: 1723 passed, EXIT=1 on #67's pricing flake alone, green alone.** **S89 closed 2026-11-04 into `batch-m2` (D257: #167 retired and #168 built — discharged; #202 continuous in R, read at S90's frames; #128 a rule's change put to the owner; #169 measured for the look; nine entries read; #91 to M3; the hash 85649e31… in fact, the pin until S90).** **S90 closed 2026-11-09 into `batch-m2` (D258: #213, #161, #197 built and discharged; #214 re-based onto M2's final layer-off run in `tests/layer_reference_s90.json`, S55's kept as `test_modes`' oracle, discharged; #215 opened to M3; the hash moved once to 5a2c097e…, the bundles and the nine frames regenerated, no frame nearer the goal pictures; #158 / #160 / #164 / #165 rulings put to the owner; `batch-m2` → `main` on the owner's full suite).** **S90a, a side session beside S90 (D259), read the nightly's fourteen CI-only failures on `main` (red every night since M1's merge, unrecorded until then) and marked them `machine_pinned`: thirteen records of this machine's arm census, whose births rounding decides (#216), and one identity of two power paths (#217).** **`batch-m2` merged into `main` 2026-11-09 (66687e0) on the GitHub runner's full suite, the owner's word (run 42558372671 on `session-90a`: 1713 passed, 41 skipped, specs OK — the first green full run since M1's merge; no local suite, D246); M2 done, `batch-m3` cuts from `main`.** **S91 closed 2026-11-10 into `batch-m3` (D260: the owner's twelve rulings of 2026-11-10 taken — #82, #128, #158, #180, #182 permanent, #210 discharged, #109 the viewer's, #159 / #163's bound 25 s cold; built #216 (the census's births bit-independent, the thirteen marks read on the runner), T2 / #114 (discharged, its closure test green), #160; left for S92: T3 / #115, #113, #171, #184, #174–#176, #164 / #165, #166, #91, #211, #217; the hash in fact, the pin at S92).** **S92 closed PARTIAL 2026-11-11 on `session-92` (D261: #164 / #165 built as ruled, #217 one grid threshold, #211 the tails on their own grid; #218's cause named — a BLAS product's bits follow the thread count — its ordered sum S93's first item; #164, #165, #211, #216, #219 discharged, #220 and #221 opened; the hash in fact moved, not pinned). Row 92 is carried by S92 and S93: S93 takes #218's ordered sum, T3, the ionized gas and the batch's close.** **S93 closed row 92 and M3 2026-11-11 into `batch-m3` (D262: five parallel Opus lanes each reviewed, the Fable gate integrating — #218's ordered sums on every draw path, T3 / #115 in part, #113 / #171 the EEP-style lookup, T10 / #119, #118 (b), #174, #175 with `kept=1`, #166 by the gate's ruling, `s83-robust` merged; #113, #119, #166, #171, #174, #175, #217 discharged, #222 opened; the layer-off reference re-based, the hash pinned once, the bundles and frames regenerated at the batch's close; several rulings taken on recommendation under the owner's word of 2026-11-11, each re-rulable).** **`batch-m3` merged into `main` 2026-11-11 (e115d7c) on the GitHub runner's full suite, the owner's word (run 42952574634 on `batch-m3`: 1752 passed, 27 skipped, specs OK; no local suite, D246); M3 done. Next: row 93, Audit VI.** **S94 ran row 93, Audit VI, 2026-11-12 (D263, `docs/AUDIT_VI.md`): the three batches read again blind - no cited number that reaches a field differs, no judged bound moved in number without a decision, 50 findings none a wrong number, the fixes S95's; section 7's "done" is not reachable on the rows as written (65 carried entries and five viewer rows have no row to take them) - what follows is the owner's word.** **S95 made Audit VI's fixes 2026-11-12 (D264): the missing tests, the walker and a walked fixture, one viewer defect mended, the readings corrected, #160 / #173 struck and #223 / #224 opened — 108 open, 99 discharged; no model byte moved.**
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
| 84 | S84 | V-4 | **T17, the design system as designed** — the tabs kept as they stand since V9, the mockup's components ported onto them (ruling 2, D252) | Opus lead, Fable at the close | fast gates; the picture test re-captured knowingly |
| 85 | S85 | R | **The register pass**: the 124 carried items each ruled permanent (with the reason written in, B5) or assigned to batch M1 / M2 / M3 below; the viewer's remaining items confirmed done or carried; `RESEARCH_AREAS.md` read beside the arms' items | Fable alone (judgement) | docs and register tests; the count pin moved once |
| 86–88 | S86–S88 | M1 | **The arms and the bar** (the pin lifted for the batch): #142 the finite-thickness reduction of the forcing with #209's floor by it; #138–#139 the arm-number law and the phases; #141, #143, #144; the bar's #145–#149; the pieces' #152–#157; `READING_ARM_*.md` the readers | Opus lead per session, Fable at the gates; two Opus builders on disjoint stages | subset mid-session; **the full suite once at S88's close, the owner's run**; the frames regenerated with the reason; the goal pictures beside |
| 89–90 | S89–S90 | M2 | **The clouds, the dust and the gas**: #128 the heating's placement applied; #167–#169, #180–#182 the clouds' law, layer and slab; #202 the diffuse share's step; #197 the stars' and remnants' ring draws; #158–#165 the censuses' and spurs' debts | Opus lead, Fable at the gates; two Opus builders | subset mid-session; **one full suite at S90's close**; frames regenerated |
| 91–92 | S91–S92 | M3 | **The populations and the ionized gas**: T2 / #114 points through the filter set, T3 / #115 the young population once, #113, #171, #184, #174–#176; #100–#101, #117–#119 and T10's forbidden lines (the FSPS grid download accepted 2026-11-02); T15; T8 | Opus lead, Fable at the gates; two Opus builders | subset mid-session; **one full suite at S92's close**; the acceptance table's rows re-read |
| 93 | S93 | A | **Audit VI**: the three batches read blind against their sources and the register, as Audit V read BUILD_III | Fable | docs tests; no number moved without a decision |
| — | the owner | D | **T19 the deploy** (the subscription when its cost suits), **then the deployed probe** (#204, #205, F5, S80's (a)); then **T20** share links and the queue (#203) as a session of its own | the owner; then Opus | the deployed table appended to D244 |

Thirteen sessions, three full suites, the deploy whenever the owner takes it. Rows 86–92's membership is the register
pass's to settle (S85): a batch takes what S85 rules a defect, in the order above; an item ruled permanent leaves it.

## 2a. The register pass's assignment (S85, D251)

Every carried item ruled, none unruled. **Permanent** (22 more, 33 in all): #3, #11, #19, #26, #27, #28, #33, #39, #42, #43, #47, #49, #52, #70, #87, #90, #93, #99, #132, #133, #134, #195 — the frozen
history's (the owner's ruling 7), the fit the owner kept (D215), a row no ruling owes, an instrument no row reads, a scope.
**Discharged on evidence** (5): #191, #192, #193, #194, #196 — entered at S70 and never struck. **Discharged by ruling** (1): #189 — ruling 3 taken, D252. **M1, the arms and the bar** (25):
#80, #81, #129, #130, #131, #138, #139, #141, #142, #143, #144, #145, #146, #147, #148, #149, #152, #153, #154, #155, #156, #157, #186, #198, #209. **M2, the clouds, the dust and the gas** (26 since S89, #91 to M3): #82, #92, #94, #95, #109, #110, #128, #136, #158, #159, #160, #161, #162, #163, #164, #165, #167, #168, #169, #180, #181, #182, #197, #202, #213, #214 (opened at S88's close, D256); at S90's close (D258) #161, #197, #213, #214 discharged and #215 opened to M3. **M3, the populations and the ionized gas**
(31 since S90, D258): #83, #84, #85, #86, #88, #89, #91 (from M2: the eight-band heating, beside T2 / #114), #96, #97, #98, #100, #101, #102, #103, #113, #114, #115, #117, #118, #119, #124, #125, #127, #135, #166, #171, #174, #175, #176, #184, #215 (from M2's close: the clouds' L1 slope). **Since S91, on the owner's twelve rulings of 2026-11-10 ("accept all recommendations")**: to M3 #216 (built first, S91), #160 (built, S91), #164 / #165 (the spur's height the excess over the ring's trough, `crest_width`'s floor the width), #211 (the response grid's tails to 4.4 µm), #217 (opened at S90a, a batch's); #159 / #163 carried for the cost pass after M3 (the whole-disc bound 25 s cold); #109 to the viewer's list; #82, #128, #158 (its window half), #180, #182 permanent; #210 discharged by ruling (the gate moves the counts, D260). **At S91's close (the gate, D260)**: #114 discharged (T2 built); #215 out, discharged on its own kill clause (the clouds' slope inside the window on #216's re-lay, not a mend); #218 (the layer-off reference off on `main`, S92's first bisection) and #219 (the L1 gate's two slopes at the window's edge, both populations) in. **At S92 (D261; row 92 carried by S92 and S93)**: #164, #165, #211, #216 (the runner's eleven read here alike, the marks lifted), #219 (the gate's ruling) out; #217 built, open until the runner reads its mark lifted; #218 to S93 (the arrival law's ordered sum and the BLAS sweep first); #220 (the walk's crest read over its bound) and #221 (a spur's crest on a bar lane) in. **At S93 (D262; M3's close)**: #113, #171 (the star sample along equivalent evolutionary points, on their closure tests), #119 (T10), #166 (the gate's ruling), #174, #175, #217 (green on the runner) out; #222 (the remainder the viewer asks over its 32 kB gate through WFC3) in; carried past M3 with their readings written: #115 (in part), #118 (on (c)), #100, #101, #117, #124, #184, #176, #91, #220, #221, and the fifteen read once (#83–#86, #88–#89, #96–#98, #102–#103, #124–#125, #127, #135); #218 discharged at the close (the close builder, D262): the layer-off reference re-based onto M3's final run in `tests/layer_reference_s93.json`, written single-threaded, its two nodes green at one thread and unrestricted (S90's file kept as history). **The viewer's** (5, a viewer pass with S84 or on the owner's word; #109 the sixth since S91 — the infrared white point by eye with the sliders): #111, #170, #177, #183, #185.
**The owner's word** (5): #107, #179, #203, #204, #205 (#189 was the eighth until ruling 3, D252; #210 discharged at S91 by the owner's ruling, D260, and #211 at S92, built, D261 - out of the list at S95, Audit VI F-5-9). **Audit VI** (1): #173.

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
- The layer-off reference (#214's procedure, D258): each batch that moves the model re-bases `tests/layer_reference_s90.json`'s successor at its close by decision (`tests/layer_reference.py write` to a new file), the two reference tests holding every later run to it with an empty named list.
- The register's count pin (`tests/test_audit.py`) and its carried-row literal move with every entry, as before.

## 6. Rulings from the owner — all six taken (1 at the adoption, D248; 2–6 on 2026-11-02, D252, each as recommended)

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
nightly runs green on the three batch merges (green apart from the `machine_pinned` cases since S90a, D259: M1's merge
was red every night on records of this machine's census, #216; a seed names one galaxy per machine until #216 closes).
