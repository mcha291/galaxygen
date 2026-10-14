# BRIEF — S64: BUILD_III's Phase V6, the censuses at whole-galaxy scale (an Opus lead; Fable at a stop condition)

**The state (2026-10-14).** S63 is merged (D223): Phase V5 — `/api/render` returns the starlight young (0–0.02 Gyr),
middle (0.02–0.1) and old, each its own spectrum's response scaled by the ring's closure factor so the three sum to
`stars` to 1e-14, each placed by its own weight (the gas contrast's placement, `sfr_modulation`, the stellar
contrast), shipped per ring with the weights named in the header (+1.17 MB); the field mode draws the three as
layers with switches. **The Milky Way frame's arm over interarm in blue rose 1.410 → 1.623 (the goal 1.83);
`ngc_4414` 2.064 → 2.119.** The owner's D222 (BUILD_IV) reshaped the board: V6 is row 64, V6b (the zoomed-in point
layer) row 65, V7 66, V8 67, V9 68, Audit V 69, BUILD_IV's W3, W2, W4, W5 rows 70–73 — read `BUILD_III.md` and
`BUILD_IV.md` as the owner left them. Register 100 open = 11 + 89, 48 discharged; next number **#166**, decisions
from **D224**, acceptance rows from 38. The owner's standing order: run the sessions back to back, stop only for a
ruling that is theirs; S61–S63 were led by Fable with Opus builders on their word — re-read their latest word on
models and the rationing rule (no heavy agent past 50 % of the 5-hour window; stop and ask past 80 % of a weekly).

## Read
- `BUILD_III.md` §5 **Phase V6** (clouds, HII knots, clusters and bright stars at whole-galaxy scale: what the
  plan rules, its gate) and the owner's **V6b** paragraph (D222); `docs/RENDER_PHYSICS.md`; D223 (the route's
  `ages` header: the pattern for naming a placing weight; the warm render 0.39 → 0.90 s, the anchors cache not
  added); D220 (the ring-first censuses and `census_clustering`: what the censuses' placements are at galaxy scale
  — the clouds and clusters placed jointly on each cell's lattice, the young bright stars by age); D221 (the gas
  field no route serves yet, V7's); the viewer's census routes (`/api/clouds`, `/api/clusters`, `/api/bright`) and
  the region regime below 4 kpc (D190).
- `tools/goal_metrics.py`: the frames at S63 read `milky_way` field 1.623 / star-first 1.743, `ngc_4414` field
  2.119 / star-first 2.216 at the instrument's default geometry (q = cos 55° for `ngc_4414`).

## Told to the owner (none awaited; if they answer, their word comes first)
- (a) The young light now follows the gas arms in the field mode: the arms carry a bluish tint; 2.9 % of the light
  moved. The closure factors (≤ 2.4e-3 in the narrow bands) are the spectrum join's non-linearity, recorded.
- (b) The warm render request doubled (0.39 → 0.90 s); a cache of the parts' anchors per galaxy would save 0.13 s.
- (c) Still theirs: the spurs' spacing factor (10 or 2.5), #164's mend, the default seed's cloud draw, the
  whole-disc routes' cost (#159), the pitch floor (#142), Erwin's bar frequency (#145), the lanes' width (#147),
  the 88-minute gate test.

## Traps learned at S63
- **"Each through the curves on its own" and "summing to the total to rounding" cannot both hold** when the
  spectrum join is non-linear: probe the closure on the model before the route is built, and record the factor.
- **A viewer builder can build against a fixed wire contract before the route lands**: state the contract (names,
  shapes, the placing weights) in the ruling and both builders run in parallel.
- Keep every Bash command under 8 KB; per-agent scratchpad sub-folders; capture pytest's own exit code; background
  the suite with its EXIT line; never leave a run in the background at a hand-back; layer off nothing may move;
  nothing is tuned to a goal picture; look at the frames beside the goals before the close and say what they show.
