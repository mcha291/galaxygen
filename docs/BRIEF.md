# BRIEF — S58: BUILD_III's Phase P3, the bar: a body, an absence, its lanes (an Opus lead; no scheduled gate)

**The state (2026-10-04).** S57 is merged (D216). Gate G2 ruled the plan's mechanism away: for arms whose power is
set ring by ring the frame is the ring's own rotation, so **no arm shocks**, and the gas's arm pattern is its
steady corotating response under uniform potential vorticity, solved ring by ring (`stages/gas_response.py` the
solver, certified on Sormani et al. 2017's threshold; `stages/gas_pattern.py` the law). The ranked ridge is gone
(#140 discharged). Rows are judged layer-off: 12 / 20 / 5 of 37, unmoved. Register 81 open = 11 + 70, 46
discharged. Numbers from D217, #145, row 38, board row 58. **The owner's standing order: run the sessions back to
back, stop only for a ruling that is the owner's, spawn Fable at the plan's gates and at a stop condition.**

## Told to the owner at S57's close (nothing here waits on an answer)
- Their item 3's "steady 1-D gas shock per ring" became the steady corotating response; the shocked branch is P3's.
- The derived gas ridge is as wide as the stellar arm, 2.5–3.1 times the one measured width (#129): a recorded miss.
- A galaxy that draws a pitch under about 2.7° is forced enormously (#142); **a floor on the drawn pitch is the
  owner's to order, with a read source** — do not add one.
- `ngc_4414`'s seven outer rings read under PHANGS's band in the disclosed check.

## First
`uv run python tools/bootstrap.py`; confirm S57's `verify_clone` on `main` passed (the close ran it; RESUMING has
the instruments). **Read `BUILD_III.md` §1, "Phase P3" in §5 (it now carries the shocked branch's certification),
§3b–§3g, and D216 whole: its items 8 and 10 are P3's inheritance.**

## The order (BUILD_III §5, Phase P3)
1. **Reading, two blind readers (§3e):** bar light fractions, axis ratios and profiles from the S⁴G decompositions;
   the bar fraction against disc properties and a disc stability criterion, with any galaxy-to-galaxy scatter; the
   gas lanes' offset and curvature; **and, for #139, the phase of spiral arms against the bar's ends**.
2. **Probe before build** (§3g): what the existing `bar` fields give against the reading; rows 15–17 as they stand.
3. **Build to the phase's text:** the body (the ring's *old* stars along the bar's axis, a mean-one two-fold ridge,
   sourced axis ratio and light share; young stars and gas follow the gas response, which now feels the bar); the
   absence (presence derived from the sourced criterion; a seeded residual only if a galaxy-to-galaxy scatter is
   read; an unbarred galaxy publishes NaN); the lanes (a synthetic template curve with sourced parameters).
4. **An Opus reviewer on the diff before the merge** (it found a blocker at S55, S56 and S57).
5. **At the close: re-read debt #138 once** (the arm-number law against `READING_ARM_MODES.md`, same statements,
   same table), with the bar's m = 2 built; if statement 8 still fails it goes to the owner as a conflict of sources.

## What S57 leaves P3 (D216)
- **The bar inside the gas's forcing.** Today the gas is g = (1 − taper)·s + taper·(1 + B cos 2(φ − φ_bar)): the
  response to the *arms*, blended with the stellar bar's own cosine. The bar turns at Ω_b, not with the ring, so
  gas flows through it: "P3 may replace the blend inside the bar's reach" (item 8). **How the bar's potential
  enters — a second frame on the same ring — is a physics ruling: a conditional gate, not the lead's.**
- **The shocked branch** (sonic point in Gittins & Clarke's regularised variables, the isothermal jump, a bisection
  on the sonic point's phase) is unbuilt. If P3 uses it, it is certified first on Kim, Kim & Kim 2014's Table 1
  under both x = 0.1450 and 0.1458 and on Shu, Milione & Roberts's rows B–D (`READING_GAS_SHOCK.md` A3). The
  smooth branch at flow ≠ 0 exists in `gas_response.solve(flow=…)` and is certified only base-subsonic.
- `arm_pattern_speed` is a statement of the arms' frame; nothing computes from it, and Ω_b is a separate field.

## Traps
- **Check a probe before it reaches a gate**; one hand-derived test independent of the modules; the reviewer always.
- **Sweep a law's inputs to their tails before the gate** (S57: twenty of 600 seeds sat on the pitch's clip and
  raised): 300 pattern seeds per template in the builder's brief.
- A convergence criterion is stated with its rounding floor (`gas_response._floor`); never loosen its numbers.
- Hold every new row or check against I1–I5 before briefing a builder: a row may not read a composed or a
  synthetic field (I3); a layer-on measurement is a pinned, disclosed check in the tests.
- Layer-off nothing may move: the rows, the template checks, every radial field outside `CENSUS_STATISTICS`.
  Regenerate the frames (`npm --prefix frontend run picture:update`) only after the pins are read.
- No third fit of `ngc_4414`; no unspent NGC 4414 window read; no m = 1 term; no ring-first draw (L1's); no
  change to the pitch's draw.
- A paused sitting can still commit: fetch and read the branch's log again before repeating owed work.
- A subagent cannot write report files; resume a builder or a gate agent with SendMessage; scripts in the
  scratchpad, never `$TMP`; LF newlines; a Bash command over 8 KB is cut; never edit pinned docs while the suite runs.
