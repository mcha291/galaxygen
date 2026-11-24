# BRIEF — after S109: both tuned frames now the goals' kind of picture (D280, BUILD_VIII rows 123-126)

**First, plainly: both full frames are now their goal's kind of picture at a glance, which they were not at S108;
neither is yet its goal at a second look.** S109 worked only on the two tuned frames. **The Milky Way** is now a spiral
of four arms on a lavender-blue disc, its first arm an oval through the ends of a cream bar at the goal's angle, pink
regions in bunches, dark-brown lanes, a soft edge, the disc at the goal's size. **Still unlike:** two of its four arms
broad and dominant (the goal's four nearer equal, narrower, more wound); the arms a uniform icy speckle, not knotted
clusters and clumps; lanes thin continuous strokes, not broken reddish filaments strung with pink; fewer, larger pink
regions; a softer, paler bar with a weak dark ground beside it; no inner arcs along the bar; a ragged outer edge; no
far arm. **NGC 4414** now overfills the frame and fades outward, a white core in a cream glow, a warm tan inner disc,
broken lanes winding in, heaps of white and blue-white clumps. **Still unlike:** its dust sparser and greyer than the
photograph's dense warm-brown network; even sand with heaps, not lumpy cauliflower clouds; the outer third grey-white
clumps on dark, not a blue-grey haze; the core's glow a little broad; 20 bright points against 97. What separates them
now is texture and balance, mostly within your sliders' reach (`docs/pictures/s109/`; `READING_PICTURES.md` S109).

## TWO THINGS ONLY YOU CAN RULE (#238, #239: entered in the register on your word; nothing waits on them)
- **#238 - a defect in the PHYSICAL look.** At NGC 4414's centre the dust is so thick (optical depth about 97 / 122 /
  159 in R, V, B) that its transmission rounds to exactly 0 at float32, and the viewer reads 0 as "no dust": a blue or
  cyan core and a white ring at close or low-exposure stands. Fixing it moves the four committed NGC 4414 frames, so it
  was NOT fixed (mended under the illustrative look only). **Recommended:** treat an exact 0 as opaque in `regimes.ts`
  (the depth from a surviving channel in the published ratio), then re-capture those four frames. Say yes or no.
- **#239 - a model question.** NGC 4414's published central extinction is about 130 mag in V face-on (the Milky Way's
  about 50): a correct march hides the nucleus. The illustrative look thins it 2 dex inside 1 kpc. Re-read it or not?
- **Entered.** On your word of 2026-11-24 ("Yes, enter both") #238 and #239 are in the register, carried, yours
  (`GALAXY_INPUTS.md` section 11; the audit test's pinned counts 115 -> 117 and its carried row moved with them). The
  two rulings above are still open: entering them decided neither.

## What S109 changed, and how to see it
Pull `main`, hard-reload, open the Tuning panel's group Illustrative; or `npm --prefix frontend run look` (8 frames).
New: NGC 4414's fall-off, dust bands, white core, cloud heaps; the Milky Way's oval round the bar, the roll 15, no
combed streaks or soft blue discs, the pitch slider's freeze mended (a skeleton slider's picture now arrives 0.8-0.9 s
late, no stall). Close up and edge-on little is better (the Milky Way's close stand frames fewer arms; NGC 4414's is
darker outside; the Milky Way edge-on still busy).

## The state (2026-11-24)
S109 on `session-109` from `main` 411426a; a Fable lead, ten Opus agents; the physical frames byte for byte; **no byte
under `model/galaxy` moved** (hash 5a862a70...); register 117 open = 50 + 67, 104 discharged. GitHub suites: S107's
(run 45241440967) and S108's (run 45277627004) green, 1860 passed each; S109's dispatched, not read. Next: #240, D281.

## Rulings taken on recommendation — yours to re-rule (`BUILD_VIII.md` section 4 is the table)
1-40 stand (16's roll and 35's cap re-ruled by 44 and 45). S109's: 41. a pass merges only if it gains at both ranges; a
lane that does not converge goes to variant sheets the lead picks from. 42. NGC 4414 overfills the frame, a fall-off of
the layer's own. 43. NGC 4414's dust and tone the lead's pick; its close-up a little darker. 44. the Milky Way's roll 15
degrees. 45. its winding, width, tone and lanes the lead's picks (`sparklecap` 10). 46. the 0.8-0.9 s worker rebuild.
47. four plain pictures in `docs/pictures/s109/`. 48. #238 / #239 entered on your word; their rulings yours.

## Parked, waiting on your word (nothing here touched them)
`batch-r` 699629c (S104, D274: green, stacked on `batch-q`, one stage-B re-read of `test_s100_bar_length` owed; it
also needs `main` merged into it, and D274 enters before D275); the held heads `batch-q-lanes` and `q-231`; BUILD_VII's
remaining rows; your owed rulings (#226, #234, #149, #88, #97/#98, #129, #184, the clustering questions, S101's list,
in `git show batch-r:docs/BRIEF.md`); the worktrees on disk, yours to remove or allow.

## The rules said again, and the traps
- Under `physical` nothing of the layer runs; a change that moves a committed frame is a defect, never a re-capture. The
  march has NO spare sampler: a feature's map is a channel of the one shared map (`index.ts`'s header).
- A new map plane is a NAMED pure memo (`memoOn`); nothing of another galaxy drawn for a frame; the main thread builds
  no map while a worker answers. The edge-on handover is per ray and bit-exact below 72 degrees. Physics only draws
  the physical look. Capture the MERGED head before trusting it. Never the full suite here (D246).
- Merge a pass on both ranges (full frame and close-up) or not at all; a lane that does not converge goes to variant
  sheets. Pick composition on small tiles, tone on full-size pairs, and read the numbers before setting a default.
