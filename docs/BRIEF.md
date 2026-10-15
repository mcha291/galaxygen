# BRIEF — S65: BUILD_III's Phase V6b, the zoomed-in point layer (an Opus lead; Fable at a stop condition)

**The state (2026-10-15).** S64 is merged (D224): Phase V6 — the clouds are extinction in their own slabs (each
cloud at its height, closure (i) under 1e-15), the HII regions are knots that scale the field per level-0 cell by
the undrawn share (closure (ii) exact at both ends), the bright stars come by level-0 tiles with an expected-count
table and a remainder-only render (bit for bit), the composite is depth-aware (T5), and clusters are Plummer
profiles where 2 r_h fills a pixel (T6). **The Milky Way frame's arm over interarm in blue 1.623 → 1.634 (the goal
1.83), its dark fraction 0 → 0.0188.** Register 104 open = 11 + 93, 49 discharged; next number **#171**, decisions
from **D225**, board row 65, acceptance rows from 38. The owner's standing order: run the sessions back to back, stop
only for a ruling that is theirs; S61–S64 were led by Fable with Opus builders on their word — re-read their latest
word on models and the rationing rule (one heavy agent, none started past 50 % of the 5-hour window).

## Build: Phase V6b (`BUILD_III.md` §5, the V6b paragraph; D222 ruling 13)
- **T4** (`VIEWER_TASKS.md` §2, #113): below 1 kpc the points are the level-0 sample and the bright catalogue, which
  thin out as the view narrows. Draw **the level-k stars as the point layer** at the levels the view reaches, each
  through the filter set as the bright catalogue's are (T2's response), the picker reading `level`, `cell`, `index`.
- **Single counting** (T3's rule): the sample and the bright catalogue withdrawn where the level-k points carry them.
- **Cell-keyed on the wire** (D222 ruling 14): every new answer keyed by cell and level, any rasterisation by window
  the viewer's — build on S64's tile form (`/api/bright?cells=`, the 0.05 dex grid, `table=1`, the point budget).
- **Gate:** T2's closure at each level (points plus field equal the render's total within the window); the
  frame-time readout; a census identical at every level (S40's assertion kept). One builder, one reviewer.
- Probe before the build, as S63 and S64 did: measure the gate's closures on the model and list where the code or
  the numbers contradict the plan's text; the lead rules each on the measurement, the owner none unless it is theirs.

## Read
- `BUILD_III.md` V6b and `BUILD_IV.md`'s ruling 13 with its §4b (D222); D224 — the tile form and the point budget V6b builds
  on, the knots' rule (a share, never a difference), the clouds' slab and its limit (#169).
- `/api/region`'s `level=` contract (D181, D190: the census routes by window, every row named by `(cell, index)`, a
  level filter's header counting the body); S48's identity (D200–D203: unresolved + young + bright = `stars`).
- `frontend/src/galaxy/brightTiles.ts` and `FluxPoints.tsx` as they stand; `RENDER_PHYSICS.md` §0.

## Told to the owner (none awaited; if they answer, their word comes first)
- (a) The pictures: the Milky Way field frame now has the clouds as a dark speckle over the disc, opaque discs in
  the inner few kpc and a dark lane along the bar, and the HII regions as faint dots (322 in the disc's mask, 551
  outside it — the outer disc's real regions at one pixel each); it gains the dust's grain and the regions' dots
  but not the lanes along the arms' inner edges. `ngc_4414` shows separate dark blobs over the outer disc, some
  blocky, thin streaks round the bulge (#169) and green knots through WFC3; it is still a smooth disc with a bulge,
  now dusted and dotted. Nothing was tuned to the goals.
- (b) The star-first mode's threshold now comes from the expected-count table against the point budget (35 481 L☉,
  2 820 points drawn, where `n` = 3 162 had given 33 500); its frames moved by at most 1e-4 per channel.
- (c) A stray "v" sits uncommitted at the end of `gateway/Galaxygen.AppHost/Galaxygen.AppHost.csproj` in the main
  checkout — not the session's; left for the owner.
- (d) Still theirs, carried from S63: the spurs' factor (10 or 2.5), #164's mend, the default seed's cloud draw,
  #159, #142, #145, #147, the 88-minute gate test.
- (e) For BUILD_IV W2's probe: a template's bright tiles at the 10⁶ depth are ~90 MB (92.6 B a star).

## Traps learned at S64
- **Look at the inclined frame**: a face-on raster of a 3-D census streaked the inclined `ngc_4414` view until the
  height and thickness went in per texel.
- **A per-cell difference goes negative, a share does not**: scale an expectation by the undrawn share (in [0, 1],
  exact at both ends), never subtract a realisation from it.
- **Two builders' paragraphs in one doc section conflict on cherry-pick**: merge by hand, keep both.
- **The register pin test reads the register**: the pin and the entries change in one commit.
- The rationing rule (one heavy agent, none past 50 % of the window) held and cost no death. Keep every Bash command
  under 8 KB; per-agent scratchpad sub-folders; capture pytest's own exit code; never leave a run in the background
  at a hand-back; layer off nothing may move; nothing is tuned to a goal picture.
