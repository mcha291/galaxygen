# BRIEF — after S110: the Milky Way much nearer, NGC 4414 nearer in zones (D281, BUILD_VIII rows 127-129)

**First, plainly: the Milky Way is now plainly its goal's picture in substance and tone, short of it in arm count and
in the colour and richness of its details; NGC 4414 has its photograph's zones and nucleus but not its cloud texture.**
**The Milky Way**: a glowing lavender disc with a smooth edge, three windings and an outer arm, a compact bar, the arms
continuous bands of fine pale stipple with faint thin lanes and pink clusters, faint stars over the disc. **Still
unlike:** three windings with wide gaps (the rim nearly a ring) against the goal's four arms; the stipple sky-blue, not
white-turquoise; the pink pastel, not saturated red, densest on the outermost arm; a violet moat round a larger bar,
still a little gold; the first arm an oval detached from the bar. **NGC 4414**: a tan inner disc, a blue-white outer
zone on a faint haze, a compact white nucleus, a brown broken dust network, its light fine grain with soft cloud banks.
**Still unlike:** no knotty cauliflower clouds (S110 built lumps, but they drew flakes and a crackle close up and are
now only soft banks); the inner dust in regular grooves, not a broken network; the outer third bluer and as bright as
the middle; 13 bright points against 97. By the tool NGC 4414 is nearer S109 on its colours and further on the colour
step and the bright points. Tone is within your sliders; the textures are new drawing (`docs/pictures/s110/`).

## TWO THINGS ONLY YOU CAN RULE (#238, #239: entered in the register on your word; nothing waits on them)
- **#238 - a defect in the PHYSICAL look.** At NGC 4414's centre the dust is so thick (optical depth about 97 / 122 /
  159 in R, V, B) that its transmission rounds to exactly 0 at float32, and the viewer reads 0 as "no dust": a blue or
  cyan core and a white ring at close or low-exposure stands. Fixing it moves the four committed NGC 4414 frames, so it
  was NOT fixed (mended under the illustrative look only). **Recommended:** treat an exact 0 as opaque in `regimes.ts`
  (the depth from a surviving channel in the published ratio), then re-capture those four frames. Say yes or no.
- **#239 - a model question.** NGC 4414's published central extinction is about 130 mag in V face-on (the Milky Way's
  about 50): a correct march hides the nucleus. The illustrative look thins it 2 dex inside 1 kpc. Re-read it or not?
- Both are carried in `GALAXY_INPUTS.md` section 11 since your "Yes, enter both" (2026-11-24); entering decided neither.

## What S110 changed, and how to see it
Pull `main`, hard-reload, open the Tuning panel's group Illustrative; or `npm --prefix frontend run look` (8 frames).
NGC 4414: a compact nucleus (the broad ball was the bloom), a yellower inner disc, the blue-white outer zone and haze,
lumps built and drawn as soft banks, **edge-on mended** (it tapers again); its close-up S109's warm grain again (the
second reader caught a loss the lead had passed on its brightness). The Milky Way: stipple bands, field stars, a grainy
bar, faint broken lanes, pink that fades edge-on, three windings in a larger glow; its close stand its best frame.

## The state (2026-11-24)
S110: a Fable lead, six Opus agents (four builders, the reviewer, the documents' writer); the review no blocker, 49 of
49 physical frames identical; **no byte under `model/galaxy` moved** (hash 5a862a70...); register unchanged, 117 open =
50 + 67, 104 discharged. GitHub: S109's head green, 1860 passed; S110's dispatched, not read. Next: #240, D282.

## Rulings taken on recommendation — yours to re-rule (`BUILD_VIII.md` section 4 is the table)
1-48 stand (16 and 35 re-ruled by 44 and 45; some of 43's and 45's values by 49-58). S110's: 49. the Milky Way's tone
and winding the lead's picks. 50. its lanes faint and broken, the grain at 250000 points. 51. NGC 4414's dust the
lead's picks. 52. its lumps built, drawn only as soft banks; the outer zone less blue. 53. its core `coreGain` 3. 54.
three shared files changed for the edge-on handover. 55. four plain pictures. 56. the sparkle job's cost as measured.
57. NGC 4414's close-up mended (mesh half as deep, grain back). 58. the Milky Way's bar paler, pink less far out.

## Parked, waiting on your word (nothing here touched them)
`batch-r` 699629c (S104, D274: green, stacked on `batch-q`, one stage-B re-read of `test_s100_bar_length` owed; it
also needs `main` merged into it, and D274 enters before D275); the held heads `batch-q-lanes` and `q-231`; BUILD_VII's
remaining rows; your owed rulings (#226, #234, #149, #88, #97/#98, #129, #184, the clustering questions, S101's list,
in `git show batch-r:docs/BRIEF.md`); the worktrees on disk, yours to remove or allow.

## The rules said again, and the traps
- Under `physical` nothing of the layer runs; a change that moves a committed frame is a defect, never a re-capture. The
  march has NO spare sampler: a feature's map is a channel of the one shared map (`index.ts`'s header).
- A new map plane is a NAMED pure memo (`memoOn`); nothing of another galaxy drawn for a frame; the main thread builds
  no map while a worker answers. The edge-on handover is per ray and bit-exact below 72 degrees; a veil hook, the
  halo and the points fade under it, so anything left edge-on must take it too. Capture the MERGED head before trusting
  it. Never the full suite here (D246).
- Merge a pass on both ranges: the close stand's own frame beside the last session's at full size, never a mean or a
  crop. Tone from variant sheets; check a pick against its control's range (a capture clamps it silently); switch
  terms off to find what draws a defect; a number guards the eye, not a target.
