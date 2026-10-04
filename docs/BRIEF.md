# BRIEF — S59: BUILD_III's Phase P4, pitch along an arm and the templates' pins (an Opus lead; no scheduled gate)

**The state (2026-10-05).** S58 is merged (D217). The bar has a presence (Fujii et al. 2018's formation time
against the disc's age, derived, no draw), **a template pin** (`bar_present`: `milky_way` barred, `ngc_4414`
unbarred as observed — an input of kind `pin`, reaching a run only through `template=`, which the viewer now
sends), a body (a Ferrers component on generalised ellipses, normalised by the drawn `bar_contrast`), gas lanes
(a synthetic template in `gas_density_contrast`; star formation follows the footprint-uniform field instead), and
the two-armed mode's phase tied to the bar. Rows are judged layer-off: 12 / 20 / 5 of 37, unmoved. Register 86
open = 11 + 75, 46 discharged. Numbers from D218, #150, row 38, board row 59. **The owner's standing order: run
the sessions back to back, stop only for a ruling that is the owner's, spawn Fable at the plan's gates and at a
stop condition** (the gate agent of S57–S58 can be resumed if it still exists; else a fresh one reads D216–D217).

## Told to the owner at S58's close (none awaited; if they answer, their word comes first)
- `ngc_4414` is shown unbarred, as observed; one template field restores the old picture. A pin holds through
  edited controls, so in the viewer the derived criterion never decides: a "derived presence" switch is theirs.
- The presence criterion bars nearly every input (#145); Erwin 2018's measured frequency as a draw is theirs to order.
- The lanes' width is an unsourced placeholder (#147): a slider if they prefer; the lanes end in a cliff at the
  bar's end and make no nuclear ring.
- **#138's re-read:** with the bar's body the disc-wide A3/A2 is 0.65 and the inner 4 kpc are two-armed, but
  outside the bar m = 5–6 still dominate from 8.7 kpc — by D215's ruling 12 a conflict of sources, put to them. (Open since S57: a floor on the drawn pitch, #142, theirs to order with a read source.)

## First
`uv run python tools/bootstrap.py`; confirm S58's `verify_clone` on `main` passed. **Read `BUILD_III.md` §1,
"Phase P4" in §5, §3d–§3g, and D217 whole** (the pin's mechanism is P4's too).

## The order (BUILD_III §5, Phase P4)
1. **Reading, one blind reader (§3e):** the distributions of arm-segment length and of the pitch's change between
   segments (Honig & Reid 2015 was read at S51: `READING_GAS_PATTERN.md`; Díaz-García et al. 2019); the Milky Way's
   arm segments and kinks from the maser fits (Reid et al. 2019: each arm's reference radius and azimuth, pitch
   inside and outside the kink, width), the bar's angle; NGC 4414's measured structure (flocculent: what can be
   pinned at all?).
2. **Probe before build:** what a segmented pitch does to the modes' common winding χ = φ − ln R cot p (today one
   pitch for all modes; the gas response, the bar's angle, the lanes' leading side and the two-armed phase all
   read it), and whether "the pinned arms pass through the measured loci" can be met by a sum of modes m = 2–6 at
   all (the Milky Way template is four-to-six-armed outside the bar, #138). **Expect a stop condition here: put it
   to a conditional gate with the numbers, as S58 did.**
3. **Build to the phase's text:** segments of seeded length and pitch change, continuous in phase, synthetic (on
   `texture_seed`, declared with what they stand in for and their statistic); the templates' pins by D217's
   mechanism (an input of kind `pin`; a galaxy without pins unchanged, bit for bit).
4. **An Opus reviewer on the diff before the merge** (it found what the builders could not at S55–S58).

## What S58 leaves (D217)
- The bar's angle is a convention, ln(a) cot p, not a field; the Milky Way's measured bar angle is P4's pin.
  `pattern.lookback_time` and the grid's `t_max` are two clocks (#148). The shocked branch has no user.
- An unbarred galaxy's arms run to the centre at full amplitude (#149); its inner gas is nearly emptied (#142).

## Traps
- **Check a probe before it reaches a gate, on the quantity the ruling will use** (S58: the lead's share was on
  the wrong surface density); one hand-derived test independent of the modules; the reviewer always.
- **When a field gains structure, list its readers** (S58: star formation rode the lanes through unchanged code).
- **Sweep seeds and the corners of the controls' ranges** (300 pattern seeds per template; three values per
  control, both pins) before the gate; count exact zeros and NaN.
- Hold every new row or check against I1–I5: a row may not read a composed or a synthetic field (I3); a layer-on
  measurement is a pinned, disclosed check in the tests. Layer-off nothing may move but what the ruling names;
  frames and thumbnails (`npm --prefix frontend run picture:update`) only after the pins are read.
- No third fit of `ngc_4414`; no unspent NGC 4414 window read; no m = 1 term; no ring-first draw (L1's); no change
  to the pitch's draw or the bar's length without the owner.
- A paused sitting can still commit: re-read the branch's log. Readers for the next session may run during the
  closing suite (notes saved to the scratchpad, not named a report); resume a builder or a gate agent with
  SendMessage; scripts in the scratchpad; LF newlines; 8 KB per Bash command; no pinned-doc edits under a suite.
