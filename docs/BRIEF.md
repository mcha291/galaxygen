# BRIEF — after S108: the look holds away from its two stands (D279, BUILD_VIII rows 119-122)

**First, plainly: both pictures are still plainly unlike their goals, and S108 did not bring either nearer.** It was
not its subject: S108 made the illustrative look survive the camera, the controls and a reroll. At the tuned stands
NGC 4414 is S107's frame byte for byte and the Milky Way S107's with a finer grain and fewer soft blue blobs close up
(fainter ones remain: reduced, not mended). **Still far, the Milky Way:** its first arm at about twice the bar's
half-length with an empty dark lavender moat, where the goal's arms hug the bar as an oval ring with bright complexes
at its ends; a saturated yellow-orange bar with a white rim against the goal's pale grainy cream; two dominant open arms
against four near-equal arms filling the disc; a smooth glow with sparse points of one white against a dense mottled
cloud; a less muted disc. **NGC 4414:** a sharp-edged oval of even brightness at three quarters of the frame against a
disc that overfills it and dims to blue-grey; a small peach nucleus against a large soft cream bulge; grey-black dashes
scattered evenly against two or three broad warm brown bands of fine filaments; star clouds at the rim only against
lumpy clouds all through. **S109 works on these lists.** Frames `docs/pictures/s108/`; `READING_PICTURES.md` S108.

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

## What S108 changed, and how to try it (Tuning panel, group Illustrative; `npm --prefix frontend run look`, 8 frames)
- **Tilt edge-on:** from 72 to 88 degrees the layer hands over, ray by ray, to the model's own volume: NGC 4414 a
  classic edge-on spiral; the Milky Way recognisable but busy (regions and sparkle dotted along the lane, bluish disc).
- **Physics only** draws the physical look, the button "illustrative (suspended)" (it was a pale fog). **Orbit**: the
  roll holds. **Star-first**: points end at the disc's edge. **Reroll** (`pattern_seed` / `texture_seed`; `world_seed`
  alone changes nothing on screen): each galaxy its own lanes and clouds; a rerolled Milky Way can still show crescents.
- The Milky Way's view now settles and draws one full-quality frame (up to about 280 ms) after a move; it never settled
  before (2 of 8 samples on every frame). A lower ceiling is yours to ask for (ruling 40).

## The state (2026-11-24)
S108 on `session-108` from `main` 69ffb40 (tag `s107`); a Fable lead, six Opus agents; the physical frames byte for
byte; **no byte under `model/galaxy` moved** (hash 5a862a70...); register 117 open = 50 + 67, 104 discharged (#238, #239 entered
after the close). S107's GitHub suite (run 45241440967) in progress, **not read at this close**; S108's dispatched, not
read. Next: #240, D280. S109's two builders run on `s109-mw` and `s109-ngc`, cut from S108's head.

## Rulings taken on recommendation — yours to re-rule (`BUILD_VIII.md` section 4 is the table)
1-28 stand. S108's: 29. physics only draws the physical look, shown suspended. 30. the edge-on handover, 72-88 degrees
per ray, `grazeDust` 4. 31. the roll after the orbit in `GalaxyView.tsx` (it moved the Milky Way's frames slightly). 32.
`points.edge` star-first only. 33. seeds follow a reroll; a 10-degree pitch floor. 34. near clouds off under the look.
35. `arms.sparklecap` 30. 36. rerolled crescents go with the inner zone. 37. four plain pictures. 38. #238 / #239
yours. 39. NGC 4414's close stand turned 1.6 degrees. 40. the settling view's one full-quality march.

## Parked, waiting on your word (nothing here touched them)
`batch-r` 699629c (S104, D274: green, stacked on `batch-q`, one stage-B re-read of `test_s100_bar_length` owed; it
also needs `main` merged into it, and D274 enters before D275); the held heads `batch-q-lanes` and `q-231`; BUILD_VII's
remaining rows; your owed rulings (#226, #234, #149, #88, #97/#98, #129, #184, the clustering questions, S101's list,
in `git show batch-r:docs/BRIEF.md`); the worktrees on disk, yours to remove or allow.

## The rules said again, and the traps
- Under `physical` nothing of the layer runs; a change that moves a committed frame is a defect, never a re-capture. The
  march has NO spare sampler: a feature's map is a channel of the one shared map (`index.ts`'s header).
- A new map plane is a NAMED pure memo (`memoOn`); nothing of another galaxy drawn for a frame. The edge-on handover
  is per ray and bit-exact below its start (72 degrees; the tuned stands' widest ray 64.5). Physics only draws the
  physical look. Capture the MERGED head before trusting it. Never the full suite here (D246).
