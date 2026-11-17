# BRIEF — after S103: the reading row (D273); `batch-q` and the held head `batch-q-lanes` await the owner

**First, plainly: the reading found no source for a lane's share of the gas, its offset from the stars' crest or its
continuity, so the largest thing a viewer misses - the dark lanes - cannot be built by the project's own rule (D1).**
A lane's width is measured (20-150 pc, a handful of grand designs) and its darkness (V transmission about 0.5); the
rest is not, and no closed form gives a thin lane (`READING_LANES.md`). Whether to draw one anyway is the owner's (1).

**What the frames show (S102's verdict, unchanged; S103 moved no frame).** Batch Q moved nothing a viewer sees against
the goal pictures: the Milky Way a tan disc with a white ball, no pink knot strings, no lanes; NGC 4414 a white ball
over a faint tan ellipse, dark flecks, no brown lane network. The held head (#234's (ii)): no dark lanes in any frame.

**The state (2026-11-17).** S103 = BUILD_VII row 105, the reading row, documents only, on `session-103` from
`batch-q`'s closing head fccecee (tag s102). Three files new (`READING_LANES.md`, `READING_DISC_EDGE.md`,
`READING_ROW_105.md`), `READING_HII_SIZES.md` Part S103. Sourced for batch R: #235 (the region grown at today's ionizing
rate, a defect - grow it at the rate's history), #226 (the cliff is the gas's own: the infall tail's hard end; Wang et
al.'s outer HI profile, a lane that measures first), #86 (Spera et al. 2015), #83 (σ_e 0.34), #96, #135 (M/L_K a 2.1x
miss), #162, #103's check. #131 permanent; #118 (c) closed by the reading. **The masers' question (D272's item (b)) is
answered**: the match improved (0.18 -> 0.13 σ gas, 0.19 -> 0.15 young stars); the null widened because the field has
fewer crests - nothing is owed before `batch-q` -> `main` is asked for. Nothing merged into `main` (b5d421c; hash
27561e8d...); `batch-q`'s run 44108837489 green (1860 passed). **115 open = 50 + 65, 104 discharged**; next #237, D274.

## The owner's choices now (recommendations are the gate's, each re-rulable)
1. **#234, the lanes:** (i) no lane - the model keeps what is measured, the goals' lanes declared outside it -
   **recommended**; or (ii) a disclosed lane (width 20-150 pc, a share with no source, zero offset: picture-driven).
2. **`batch-q` -> `main`** on its green run. **The held head (#234):** the gate recommends NOT taking (ii) for the
   picture's sake; with (1)'s (i) it stays held or is dropped.
3. **#149:** pin NGC 4414's arms' inner radius to Herrera-Endoqui et al.'s innermost segment, 1.66 kpc - **recommended**.
4. **#88:** (i) WAF17's own pair (row 31 reads 0.594 against 0.6 until #89) - **recommended**; (ii) Maoz & Graur's.
5. **#97 with #98:** (i) Baumgardt & Makino for clusters older than ~9 Gyr, Lamers et al.'s time for the disc -
   **recommended** (chosen after S34's measurement, disclosed); (ii) the model as it is.
6. **#129:** (i) permanent - **recommended**; (ii) measure it from the PHANGS-ALMA maps (a download).
7. **#95** joins the clustering questions (#80, #233, #223): the window is the clusters', the clouds' target borrowed.
8. **#231: do not order it.** **#184:** (i) the clouds' 34 pc layer - recommended. Adopt BUILD_VII or re-order it.
9. Still owed from S101: #80 with #233 ((i) Table 4's bar); #223 / #233 / #224 (nine seeds); #84 / #100 (PARSEC);
   #85; #225 ((i)); #92, #94, #138, #153; #107, #179; #203-#205; the looks #156, #202; #227's fallback; the cadences.

## What the next session does
1. The gate enters D273 from the scratchpad draft, tags `s103` on `session-103`'s closing head (MANUAL_TODO row 103).
2. On the owner's word: the merge of `batch-q`; the held head kept, merged or dropped; the rulings above.
3. Then batch R = S104 (BUILD_VII rows 106-107): #235, #226 (measure first), #86, #83, #96, #135, #162, #103's check -
   every coefficient re-checked against the PDF before it is built (every S103 number came through an extracting fetch).

## Rulings taken on recommendation — the owner may re-rule any
- At S97-S102's gates: as BRIEF said at S102 (no default moved; #80 over #233; #95 not merged; #101, #147 permanent;
  #232's c_0, the cap, the natal density; D219's pitch clause; #234's weak arms held; #136, #183 to batch R).
- At S103's gate: #131 permanent; #118 (c) closed on Byler's thin-shell sentence; #103's lifetime clause permanent,
  its Sedov clause closed; #95's compact-cluster row not chosen (B5); #226's first ruling corrected on a second reading.

## The rules said again, and the traps (S72-S103's stand)
- **Two-thirds**: a lead past two-thirds of its context hands back. **Commit each item when green** (`git commit -F`).
- The runner's suite once per head (`gh run view`); the `machine_pinned` nodes a change touches read by name.
- Never the full suite, `verify_clone` or the pins unprompted (D246); one single-threaded pytest at a time, `tasklist`
  first; no backtick in a shell string; any byte under `model/galaxy` moves the hash.
- `--collect-only -q` prints no ids, an empty id file runs all (S94); one change per experiment; defaults fixed (D227).
- A lane re-pins nothing outside its own files (S99); a re-pin pass is briefed in thirds on disjoint files (S100).
- A held head is never merged on a recommendation (BUILD_VII §1); a frames-only branch is never gated or merged.
- A number from an extracting fetch is checked against the PDF before a build (S103).
