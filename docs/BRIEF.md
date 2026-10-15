# BRIEF — S66: BUILD_III's Phase V7, the layer in the viewer (an Opus lead; Fable at a stop condition)

**The state (2026-10-15).** S65 is merged (D225): Phase V6b — the zoomed-in points below 4 kpc in the star-first mode
are the bright catalogue at level-k tiles (complete above the frame's threshold, the picker naming the level), the
plan's level-k sample measured and set aside (light share ≤ 9.4e-4; its luminosity function 0.14 of the catalogue's
at 10³ L☉, #171), the budget weighted by the stellar layer the frustum sees, two zoom captures; the eight old frames
byte for byte. Register 106 open = 11 + 95, 49 discharged; next number **#173**, decisions from **D226**, board row 66,
acceptance rows from 38. The owner's standing order: run the sessions back to back, stop only for a ruling that is
theirs; S61–S65 were led by Fable with Opus builders on their word — re-read their latest word on models and the
rationing rule (one heavy agent, none started past 50 % of the 5-hour window).

## Build: Phase V7 (`BUILD_III.md` §5, the V7 paragraph; D219's addition)
- **The GLSL twin of the noise**, matching `model/galaxy/layer/vectors.json` to 1e-5.
- **The diffuse dust modulated per pixel in the march** by the gas fluctuation field; **the spurs**; **the bar's body
  and lanes**; **the "physics only" switch**.
- **The young starlight of V5** (unresolved, most of what a blue-white complex is) modulated per pixel by the
  clustering field, its finest scales dropped with age as L1 rules for the bright catalogue; **unit mean per cell**
  keeps each ring's light.
- **Gate:** the vectors; the frame-time readout (the picture test's ready time per capture, D225 R5; a per-frame GPU
  time is V8's, T14); each ring's dust on screen unchanged by the layer (`__galaxygenFrameSum` on a dust-only frame).
  **Two builders.** Probe before the build, as S63–S65 did; the lead rules each finding on the measurement.

## Read
- `BUILD_III.md` V7; D221 (the gas fluctuation field, its evaluator and vectors); D220 (`census_clustering`, the
  octaves by age); D224–D225 (the clouds' slab, the knots' share, the tiles).
- `model/galaxy/layer/` (noise, vectors.json, `gas_fluctuation.evaluate`); `frontend/src/galaxy/fieldFragment.s64.glsl`
  and `FieldVolume.tsx`; `RENDER_PHYSICS.md` §0.

## Told to the owner (none awaited; if they answer, their word comes first)
- (a) V6b was built on the bright catalogue at finer tiles instead of the plan's level-k sample, on three numbers:
  the sample's light share is its sampling fraction (≤ 9.4e-4 at level 3), its bright end is 0.14 (Milky Way) / 0.09
  (`ngc_4414`) of the catalogue's at 10³ L☉ (#171), and the tiles reach 71 L☉ at a 62 pc view in ~1.4 s. Reversible
  on their word.
- (b) The zoom frames: `milky_way-zoom` (0.5 kpc on the arm crest at 8.14 kpc) reads as a star field for the first
  time — about 1 400 stars above 1 260 L☉, blue, white and orange, two bright orange giants at the right edge, over a
  grey featureless glow; `ngc_4414-zoom` a pink-beige field with a few hundred points and one bright blue-white star,
  one rare bright source dropped by the fetch rule (see D225). The field at that zoom shows the render grid's cells
  enlarged (stripes and blocks of 75 pc): V7's per-pixel layer and V8's display defaults are what it waits on.
- (c) The main checkout's `frontend/node_modules` was emptied by a worktree removal and restored with `npm ci`; their
  dev tab may need a restart.
- (d) The stray "v" at the end of `gateway/Galaxygen.AppHost/Galaxygen.AppHost.csproj`, still uncommitted, theirs.
- (e) Still theirs, carried from S63–S64: the spurs' factor (10 or 2.5), #164's mend, the default seed's cloud draw,
  #159, #142, #145, #147, the 88-minute gate test; and #172, one mode at zoom (the region regime or the tiles).

## Traps learned at S65
- **The junction trap**: a worktree holding a junction (e.g. to `node_modules`) — `rmdir` the junction before
  `git worktree remove`, or the removal empties the target.
- **A perspective cone at a short standoff**: the frustum cut by a ±3 kpc slab spans 3 kpc at a 0.6 kpc standoff; a
  budget over "the cells in view" must weight each cell by the share of its layer the frustum sees.
- **The sample's luminosity function**: measure a sampled catalogue's against the complete one before drawing it as
  points (#171: interpolation at fixed initial mass drops the short evolved phases).
- Keep every Bash command under 8 KB; per-agent scratchpad sub-folders; capture pytest's own exit code; the register
  pin and its entries change in one commit; layer off nothing may move; nothing is tuned to a goal picture.
