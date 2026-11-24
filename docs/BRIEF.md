# BRIEF — after S111: the Milky Way's arms from the bar's tips, NGC 4414 not nearer (D282, BUILD_VIII rows 130-132)

**First, plainly: the Milky Way took its largest step in composition since S109; NGC 4414 did not come nearer.**
**The Milky Way**: arms that leave the bar's two tips and wind as four, the closed oval and the violet moat gone, the
pink thinning outward as the goal's does. **Still unlike:** just past each tip the inner arm is a thin, grain-starved
stretch with a dark lane; the tip complexes are pink blobs, not blue-white-and-pink knots; the stipple bluer than the
goal's white-turquoise; the pink pastel; the bar a flat cream-gold ellipse; at the close stand the lanes are dark grey
cords again. **NGC 4414**: lost its record grooves and sits in its frame. **Still unlike:** its light is still grain;
its bright points soft and few (13 against 97); its outer zone bluer; its inner dust rust streaks brushed along the
spiral, not a dark branching network. By the tool it is further than S110 on outer colour, colour gradient and arm
contrast. **Its close-up is a loss in its lower half** against S110's (smeared rust flakes where S110 had a fine warm
grain and winding filaments) to the documents' writer, who was the first to look at the merged head's frames; the lead
had read it, on the builder's sheet, as different and no worse. `blotReach` 3.0 or `blot` 0 restores more of S110's.
The frames: `docs/pictures/s111/`.

## TWO THINGS ONLY YOU CAN RULE (#238, #239: entered in the register on your word; nothing waits on them)
- **#238 - a defect in the PHYSICAL look.** At NGC 4414's centre the dust is so thick (optical depth about 97 / 122 /
  159 in R, V, B) that its transmission rounds to exactly 0 at float32, and the viewer reads 0 as "no dust": a blue or
  cyan core and a white ring at close or low-exposure stands. Fixing it moves the four committed NGC 4414 frames, so it
  was NOT fixed (mended under the illustrative look only). **Recommended:** treat an exact 0 as opaque in `regimes.ts`
  (the depth from a surviving channel in the published ratio), then re-capture those four frames. Say yes or no.
- **#239 - a model question.** NGC 4414's published central extinction is about 130 mag in V face-on (the Milky Way's
  about 50): a correct march hides the nucleus. The illustrative look thins it 2 dex inside 1 kpc. Re-read it or not?
- Both are carried in `GALAXY_INPUTS.md` section 11 since your "Yes, enter both" (2026-11-24); entering decided neither.

## What S111 changed, and how to see it
Pull `main`, hard-reload, open the Tuning panel's group Illustrative; or `npm --prefix frontend run look` (8 frames).
The Milky Way: sixteen default values, no code (`arms.ts`, `knots.ts`): the arms from the bar's tips, about four arcs
along a radius, the pink weighted inward. NGC 4414: dust blotches inside 3.5 kpc in place of the grooves (`floc.blot*`),
the clouds as mild soft banks (`lumpForm`), 120 soft sparks, the disc inside the frame (`framing.scale` 0.48).

## The state (2026-11-24)
S111: a lean session (the week's quota nearly spent), one builder pass a lane; a Fable lead, four Opus agents (two
builders, the reviewer, the documents' writer); the lead read the hand-backs on the builders' sheets and did not look
at the merged head's frames; the review: (the lead adds it). **No byte under `model/galaxy` moved** (hash
5a862a70...); register unchanged, 117 open = 50 + 67, 104 discharged. GitHub: S110's head (run 45383329570)
dispatched, the lead adds the result; S111's dispatched, not read. Next: #240, D283.

## Rulings taken on recommendation — yours to re-rule (`BUILD_VIII.md` section 4 is the table)
1-58 stand (some values re-ruled by later rulings). S111's: 59. the Milky Way's composition c6 as handed back. 60. NGC
4414's blotches inside 3.5 kpc though the close stand is not better. 61. its framing 0.48. 62. its sparks on though
soft. 63. its clouds at mild strength. 64. a lean session, the second reader and the reviewer the eyes on the head.
65. four plain pictures.

## Parked, waiting on your word (nothing here touched them)
`batch-r` 699629c (S104, D274: green, stacked on `batch-q`, one stage-B re-read of `test_s100_bar_length` owed; it
also needs `main` merged into it, and D274 enters before D275); the held heads `batch-q-lanes` and `q-231`; BUILD_VII's
remaining rows; your owed rulings (#226, #234, #149, #88, #97/#98, #129, #184, the clustering questions, S101's list,
in `git show batch-r:docs/BRIEF.md`); the worktrees on disk, yours to remove or allow.

## The rules said again, and the traps
- Under `physical` nothing of the layer runs; a change that moves a committed frame is a defect, never a re-capture. The
  march has NO spare sampler: a feature's map is a channel of the one shared map (`index.ts`'s header).
- A new map plane is a NAMED pure memo (`memoOn`); the main thread builds no map while a worker answers. The edge-on
  handover is per ray; anything left on screen edge-on must take it. Capture the MERGED head before trusting it.
- Merge a pass on both ranges: the close stand's own frame beside the last session's at full size. Someone must LOOK at
  the merged head's frames before the close. Time the worker on a quiet machine only. Switch terms off to find what
  draws a defect; write a guess down as a guess. Never the full suite here (D246).
