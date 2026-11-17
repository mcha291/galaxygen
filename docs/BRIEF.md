# BRIEF — after S102: batch Q's close (D272); `batch-q` and the held head `batch-q-lanes` await the owner

**What the frames show (the gate's verdict, shortened).** **Batch Q moved nothing a viewer sees against the two goal
pictures.** `batch-q` beside `main`: the field frames cannot be told apart by eye, at the defaults and in M4 / N6; the
regions grown to their size are a few faint pinkish discs at a 2.2 kpc zoom and nothing at the field scale. The
distance to the goals is S101's: the Milky Way a tan disc with a white ball (M4 a blue-white barred spiral, no pink
knot strings, no lanes); NGC 4414 a white ball over a faint tan ellipse (N6 grey-blue with dark flecks, no brown lane
network, no yellow core). **The held head (#234's (ii)): no dark lanes in any frame, continuous or dashed** - the
measured relation moves the clouds' ellipses and nothing else, and on N6 the dark fraction and the arm contrast move
away from the goal (0.0617 -> 0.0565 against 0.154; 1.46 -> 1.37). `q-231` (#231): no lanes, NGC 4414 redder, one
untraced defect. Why `[inferred]`: (ii) gathers the gas into a crest still about a kiloparsec wide; the goals' lanes are
about a hundred parsecs and continuous - a narrow ridge neither ruleset holds. Sheets: `docs/goals/batch_q_s102/`;
the yardstick `READING_PICTURES.md` Part S102.

**The state (2026-11-17).** S102 closed batch Q (BUILD_VII rows 102-103, a DRAFT run on the word of 2026-11-17):
#232 built (each HII region grown past its clump: median 0.77 -> 11.0 pc on the Milky Way, its Halpha unchanged) and
drawn at its radius; #230 mended (the forcing's pitch averaged over the layer's height); #226's edge declared. On
`batch-q-lanes` (held): #234 (ii). On `q-231` (frames only, pushed, never merged): #231. Nothing merged into `main`
(b5d421c; hash 27561e8d...). [[LEAD: both heads' shas, final runs and pytest lines; the new hash]].
**115 open = 49 + 66, 104 discharged**; next #237, D273. #230, #232 discharged; #235, #236 opened.

## The owner's choices now (recommendations are the gate's, each re-rulable)
1. **`batch-q` -> `main`**, on its green dispatched run, the owner's word (it moves the regions' physics and #230's
   step; no frame moves visibly).
2. **The held head (#234):** (i) D216's response kept, or (ii) the measured relation on `batch-q-lanes`. The
   recommendation now stands on the measurement alone; **the gate recommends NOT taking (ii) for the picture's sake**
   and leaving `batch-q-lanes` held until the lanes' width, offset and covering fraction are read (#229's line,
   BUILD_VII row 105). A defect of (ii) as built: the stars' kink at 4.450 kpc steps the molecular field by 0.029.
3. **#231: do not order it** (no lanes; invariant I2 broken by design; NGC 4414 redder; a cloud at the 150 pc cap; an
   untraced defect). `q-231` stays a branch.
4. **#184:** (i) the young and middle light in the clouds' 34 pc layer (Robin et al. 2003's youngest bin, 33 pc) -
   **recommended** - or (ii) Robin's ratio per part for every galaxy.
5. Adopt BUILD_VII (a draft) or re-order it; the display pass (sheets in `docs/goals/display_pass_s101/`).
6. Still owed from S101: #80 with #233 ((i) Table 4's bar - recommended); #223 / #233 / #224 (the nine-seed reading -
   recommended); #84 / #100 (the PARSEC download); #85; #225 ((i)); #92, #94, #138, #153; #107, #179; #203-#205;
   the looks #156, #202; #227's coarse-grid fallback; a cadence for the pinned nodes; the concurrency rule.

## What the next session does
1. The gate enters D272 from the scratchpad draft, tags `s102` on `batch-q`'s closing head (MANUAL_TODO row 102).
2. On the owner's word: the merge of `batch-q`; the held head kept, merged or dropped.
3. Then BUILD_VII row 104 (the viewer row, with #236) or row 105 (the reading row: #229's lanes, #235, #149's table,
   #226's truncation), as the owner orders.

## Rulings taken on recommendation — the owner may re-rule any
- At S97-S101's gates: as BRIEF said at S101 (no default moved; #80 kept over #233; #95 not merged; #101, #147
  permanent; #183 pulled into batch Q).
- At S102's gate: #232's sound speed c_0^2 = c_s^2 + sigma_v^2, the capped region keeping its photons, the bubbles on
  the natal density, the log U floor recorded; D219's pitch clause re-ruled (the Gaussian of the layer's height) and
  the count's taper at a turn back; #234's weak arms held, not failed, the relation on the tapered field; #231's
  invariant break declared, not amended; #136 a disclosed check for batch R; #183 to batch R.

## The rules said again, and the traps (S72-S102's stand)
- **Two-thirds**: a lead past two-thirds of its context hands back. **Commit each item when green** (`git commit -F`).
- The runner's suite once per head (`gh run view`); the `machine_pinned` nodes a change touches read by name.
- Never the full suite, `verify_clone` or the pins unprompted (D246); one single-threaded pytest at a time, `tasklist`
  first; no backtick in a shell string; any byte under `model/galaxy` moves the hash.
- pytest's collect-only under the project's `-q` prints no ids; an empty argument file runs the whole suite (S94).
- One change against the control per experiment; a display default is never moved by a session (D227).
- A lane re-pins nothing outside its own files (S99); a re-pin pass is briefed in thirds on disjoint files (S100).
- A held head is never merged on a recommendation (BUILD_VII §1); a frames-only branch is never gated or merged.
