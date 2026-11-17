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
(b5d421c; hash 27561e8d...). **`batch-q`**: the re-pin pass (RA, RB, RC; the lead's spill 1826 -> 1821, the three
legs' `EXPECTED_LEAST` as read), run 44072430053 on 0433cd1 **green** (1860 passed, 35 skipped, 10 xfailed, 2:33:21);
D1: hash **5a862a70d3760c426ca51c2cffa2b0c2**, `tests/layer_reference_s102.json`, `bundles_q`, the frames = the live
captures byte for byte. Final run 44108837489 on 7ecd0e4 GREEN (1860 passed, 35 skipped, 10 xfailed, 2:40:55); the closing head is its one-line docs successor (this line).
**The held head**: re-pinned under (ii) by LA, LB; four judged clauses held strict (`GATE_MAX_G_OVER_STEADY_S102`,
`SUBSAMPLE_READ_OVER_S102`, `MANY_WINDOWS_READ_OVER_S102`, `DUST_COLUMN_OVER_S102`); #233's flatness hold lifted under
(ii) (0.0468 / 0.0387); its run to come. **115 open = 49 + 66, 104 discharged**; next #237, D273. #230, #232
discharged; #235, #236 opened.

## The owner's choices now (recommendations are the gate's, each re-rulable)
1. **`batch-q` -> `main`** on its green dispatched run (the regions' physics, #230's step; no frame moves visibly).
2. **The held head (#234):** (i) D216's response kept, or (ii) the measured relation on `batch-q-lanes`. The
   recommendation now stands on the measurement alone; **the gate recommends NOT taking (ii) for the picture's sake**
   and leaving `batch-q-lanes` held until the lanes' width, offset and covering fraction are read (#229's line,
   BUILD_VII row 105). A defect of (ii) as built: the stars' kink at 4.450 kpc steps the molecular field by 0.029.
3. **#231: do not order it** (no lanes; I2 broken by design; NGC 4414 redder; a cloud at the 150 pc cap; a defect).
4. **#184:** (i) the young and middle light in the clouds' 34 pc layer (Robin et al. 2003's youngest bin, 33 pc) -
   **recommended** - or (ii) Robin's ratio per part for every galaxy.
5. Adopt BUILD_VII (a draft) or re-order it; the display pass (sheets in `docs/goals/display_pass_s101/`).
6. Still owed from S101: #80 with #233 ((i) Table 4's bar - recommended); #223 / #233 / #224 (the nine-seed reading -
   recommended); #84 / #100 (the PARSEC download); #85; #225 ((i)); #92, #94, #138, #153; #107, #179; #203-#205;
   the looks #156, #202; #227's coarse-grid fallback; a cadence for the pinned nodes; the concurrency rule.

## What the next session does
1. The gate enters D272 from the scratchpad draft, tags `s102` on `batch-q`'s closing head (MANUAL_TODO row 102).
2. On the owner's word: the merge of `batch-q`; the held head kept, merged or dropped.
3. Then BUILD_VII row 104 (the viewer, #236) or 105 (the reading: #229's lanes, #235, #149, #226), as the owner orders.

## Rulings taken on recommendation — the owner may re-rule any
- At S97-S101's gates: as BRIEF said at S101 (no default moved; #80 over #233; #95 not merged; #101, #147 permanent).
- At S102's gate: #232's c_0^2 = c_s^2 + sigma_v^2, the capped region keeping its photons, the bubbles on the natal
  density, the log U floor recorded; D219's pitch clause re-ruled (a Gaussian of the layer's height), the count's taper
  at a turn back; #234's weak arms held, not failed; #231's I2 break declared, not amended; #136, #183 to batch R.

## The rules said again, and the traps (S72-S102's stand)
- **Two-thirds**: a lead past two-thirds of its context hands back. **Commit each item when green** (`git commit -F`).
- The runner's suite once per head (`gh run view`); the `machine_pinned` nodes a change touches read by name.
- Never the full suite, `verify_clone` or the pins unprompted (D246); one single-threaded pytest at a time, `tasklist`
  first; no backtick in a shell string; any byte under `model/galaxy` moves the hash.
- `--collect-only -q` prints no ids, an empty id file runs all (S94); one change per experiment; defaults fixed (D227).
- A lane re-pins nothing outside its own files (S99); a re-pin pass is briefed in thirds on disjoint files (S100).
- A held head is never merged on a recommendation (BUILD_VII §1); a frames-only branch is never gated or merged.
