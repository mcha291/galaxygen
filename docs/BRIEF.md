# BRIEF — after S106: both pictures read as their goal at a glance (D277, BUILD_VIII rows 111-114)

**First, plainly: S105 made both frames the right kind of picture; S106 makes both read as their goal at a glance.**
Under the **illustrative look** (the default) the Milky Way is a luminous lavender disc filling the frame to a soft
fade, pale cyan-white arms of fine grain winding from the bar's ends to the edge, thin red-brown lanes on their inner
edges, small pink-red regions with white cores in bunches, a crisp cream bar at the goal's angle in a darker zone.
NGC 4414 lies at the photograph's tilt: a cream nucleus in a golden inner disc, dark brown dust in many thin spiral
arcs with a tangle between, blue-white star clouds at the rim, field stars on a navy sky. **Still far, at close range
only:** the Milky Way's arms are smooth bands with points where the goal's are patchy light, its regions salmon rather
than crimson and never a large complex, its lanes unbranched, a stray blue blob right of the bar; NGC 4414's threads
are more even than the photograph's lanes, the light between them soft, the rim's dust grey, the nucleus a soft blob.
Frames: `docs/pictures/s106/`; words and numbers: `READING_PICTURES.md` Part S106. The **physical look** is unchanged.

## TWO THINGS ONLY YOU CAN RULE (register #238 and #239; nothing waits on them, nothing fixes them without you)
- **#238 - a defect in the PHYSICAL look.** At NGC 4414's centre the dust is so thick (optical depth about 97 / 122 /
  159 in R, V, B) that its transmission rounds to exactly 0 at float32, and the viewer reads 0 as "no dust": a blue or
  cyan core and a white ring at close or low-exposure stands. Fixing it moves the four committed NGC 4414 frames, so it
  was NOT fixed (mended under the illustrative look only). **Recommended:** treat an exact 0 as opaque in `regimes.ts`
  (the depth from a surviving channel in the published ratio), then re-capture those four frames. Say yes or no.
- **#239 - a model question.** NGC 4414's published central extinction is about 130 mag in V face-on (the Milky Way's
  about 50): a correct march hides the nucleus. The illustrative look thins it 2 dex inside 1 kpc. Re-read it or not?

## How to see it and tune it
- Pull `main`, run the API and `npm --prefix frontend run dev`, hard-reload (Ctrl+Shift+R); **illustrative** sits
  beside **physics only**. Tuning panel, group **Illustrative**: about 300 sliders by feature with a filter box; an
  `arms.skel*` slider moves the Milky Way's glow, grain, lanes and regions together; the copy box carries every value.
- Frames beside the goals: `uv run python -m galaxy.api --port 8031 --client frontend/dist --bundles <dir>`, the build,
  `GALAXYGEN_E2E_PORT=8031 npm --prefix frontend run look`, `uv run python tools/goal_sheet.py --frames docs/goals/look --out docs/goals/look`.

## The state (2026-11-23)
S106 on `session-106` from `main` d40c43a (tag `s105`). A Fable lead, eleven Opus builders and investigators, an Opus
reviewer; the two Fable builders were cut by HTTP 529 and replaced by Opus. The picture test's nine physical frames
byte for byte at every hand-back and on the merged head; the full suite dispatched on GitHub, **not read yet** (S105's
run 45130693940: green, 1860 passed). **No byte under `model/galaxy` moved** (hash 5a862a70...). Register: 117 open =
50 + 67, 104 discharged. Next numbers: #240, D278 (#237 and D274 are `batch-r`'s).

## Rulings taken on recommendation — yours to re-rule (`BUILD_VIII.md` section 4 is the table)
S105's 1-11 stand (D5 amended for the layer alone; viewer sessions merge at close; the default look illustrative; lanes
a drawing; the register frozen but for physical defects; the frames unpinned). S106's: 12. the layer may draw
structure the model lacks where a goal has it (the arm skeleton; NGC 4414's threads, mesh, star clouds, sky). 13. the
look-switch fix in the shared loader `useLoad.ts`. 14. #238 mended in the layer only. 15. NGC 4414's core dust thinned
2 dex, the Milky Way's dust placement 0.1. 16. NGC 4414 tilted 6 degrees, the Milky Way rolled 25. 17. three builders
at once. 18. S106's frames plain pictures. 19. NGC 4414's near-side and star-cloud azimuths follow no other camera.

## Known defects and what the next session does (`BUILD_VIII.md` section 6)
- S105's blanking look switch is MENDED. The `glGetProgramiv` warnings on a remount: not reproduced, cause unknown.
  NGC 4414's map rebuild with the threads on: not re-measured. Three 5-second vitest tests time out on a loaded machine.
- Next: your tuning pass or list; your rulings on #238 and #239; then each picture at close range (the list above).

## Parked, waiting on your word (nothing here touched them)
`batch-r` 699629c (S104, D274: green, stacked on `batch-q`, one stage-B re-read of `test_s100_bar_length` owed before
its merge; it now also needs `main` merged into it, and D274 enters before D275); the held heads `batch-q-lanes` and
`q-231`; BUILD_VII's remaining rows; your owed rulings (#226, #234, #149, #88, #97/#98, #129, #184, the clustering
questions, S101's list): `git show batch-r:docs/BRIEF.md`. Worktrees on disk: yours to remove or allow.

## The rules said again, and the traps
- Under `physical` nothing of the layer runs; a change that moves a committed frame is a defect, never a re-capture.
- The march has NO spare sampler: a feature's map is a channel of the one shared map (`index.ts`'s header).
- Capture the MERGED head before trusting it; a builder commits early (an API error loses uncommitted work).
- Never the full suite here (D246): `gh workflow run ci.yml --ref <branch>`. Each agent its own scratch directory.
