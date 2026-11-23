# BRIEF — after S107: the sliders are free and both close-ups read as their goal's (D278, BUILD_VIII rows 115-118)

**First, plainly: S106 made both frames their goal's composition; S107 makes both close-ups read as their goal's
close-ups, and no slider freezes the view any more.** Under the **illustrative look** (the default) the Milky Way is a
balanced spiral opening outward from the bar's ends, patchy pale blue-white arms on a periwinkle disc, ragged red-pink
regions in bunches and complexes on braided brown lanes, a pale cream bar. NGC 4414 is a flocculent disc of many narrow
broken dust lanes round a bright nucleus in a golden inner disc, star clouds at the rim, no brushing. **Still far:**
the Milky Way's inner arms do not hug the bar's ends (an empty lavender zone), its bar too orange, its lanes browner
and broader than the goal's threads, soft round blue blobs between the arms close up (the arm grain's soft sprite,
traced, not mended); NGC 4414's lanes lighter and less prominent than the photograph's, fingerprint stripes near the
nucleus, the outer disc grey-white to the rim where the photograph's dims and turns blue (a second reader's). Frames:
`docs/pictures/s107/`; words and numbers: `READING_PICTURES.md` Part S107. The physical look is unchanged.

## TWO THINGS ONLY YOU CAN RULE, AND THE OK TO ENTER THEM (#238, #239; nothing waits on them)
- **#238 - a defect in the PHYSICAL look.** At NGC 4414's centre the dust is so thick (optical depth about 97 / 122 /
  159 in R, V, B) that its transmission rounds to exactly 0 at float32, and the viewer reads 0 as "no dust": a blue or
  cyan core and a white ring at close or low-exposure stands. Fixing it moves the four committed NGC 4414 frames, so it
  was NOT fixed (mended under the illustrative look only). **Recommended:** treat an exact 0 as opaque in `regimes.ts`
  (the depth from a surviving channel in the published ratio), then re-capture those four frames. Say yes or no.
- **#239 - a model question.** NGC 4414's published central extinction is about 130 mag in V face-on (the Milky Way's
  about 50): a correct march hides the nucleus. The illustrative look thins it 2 dex inside 1 kpc. Re-read it or not?
- **The OK to enter them.** #238 and #239 are two findings of S106, STILL NOT ENTERED in the register: the numbers are
  reserved for them; entering them needs a two-line change to tests/test_audit.py (the pinned counts 115 -> 117 and
  the carried row), which waits for your word.

## How to see it and tune it
- Pull `main`, run the API and `npm --prefix frontend run dev`, hard-reload (Ctrl+Shift+R); **illustrative** sits
  beside **physics only**. Tuning panel, group **Illustrative**: the sliders by feature with a filter box; an
  `arms.skel*` slider moves the Milky Way's glow, grain, lanes and regions together; the copy box carries every value.
  Frames: `npm --prefix frontend run look` against an API on :8031 with the bundles, then `tools/goal_sheet.py`.

## The state (2026-11-23)
S107 on `session-107` from `main` 510ee63 (tag `s106`); a Fable lead, ten Opus agents. The nine physical frames byte
for byte on the merged head. S106's GitHub suite (run 45182703859): green, 1860 passed; S107's dispatched, **not read
yet**. **No byte under `model/galaxy` moved** (hash 5a862a70...). Register as it was: 115 open = 50 + 65, 104
discharged. Next: #240 (#238, #239 reserved), D279 (#237 and D274 are `batch-r`'s).

## Rulings taken on recommendation — yours to re-rule (`BUILD_VIII.md` section 4 is the table)
S105's 1-11 and S106's 12-20 stand (20: #238 and #239 not entered). S107's: 21. nothing of another galaxy drawn for a
frame after a switch. 22. the framing keyed on the drawn template, a one-line fix in `GalaxyTab.tsx`. 23. NGC 4414's
dust the mesh on narrow lanes, the threads off (S106's pick reversed). 24. `arms.flat` kept at 0. 25. the Milky Way's
lesser arms at 0.7 of the majors. 26. the regions' veil. 27. S107's frames plain pictures. 28. #238 / #239 still yours.

## Known defects and what the next session does (`BUILD_VIII.md` section 6)
- **MENDED at S107:** the slider stalls (longest frame gap 17-50 ms against `main`'s 277-379; the map built in a
  worker; memory as `main`'s after the reviewer's fix) and the `glGetProgramiv` warnings (a second canvas per landing;
  0 lines against `main`'s 12). Left: the picture completes 0.35-3 s after a move. NGC 4414's brushing was the layer's
  own threads and grain (the lead had guessed the model). Next: your tuning, your rulings; then "Still far" above.

## Parked, waiting on your word (nothing here touched them)
`batch-r` 699629c (S104, D274: green, stacked on `batch-q`, one stage-B re-read of `test_s100_bar_length` owed; it
also needs `main` merged into it, and D274 enters before D275); the held heads `batch-q-lanes` and `q-231`; BUILD_VII's
remaining rows; your owed rulings (#226, #234, #149, #88, #97/#98, #129, #184, the clustering questions, S101's list,
in `git show batch-r:docs/BRIEF.md`); the worktrees on disk, yours to remove or allow.

## The rules said again, and the traps
- Under `physical` nothing of the layer runs; a change that moves a committed frame is a defect, never a re-capture. The
  march has NO spare sampler: a feature's map is a channel of the one shared map (`index.ts`'s header).
- A new map plane must be a NAMED pure memo (`memoOn(build, name)`): the worker builds it by name. Nothing of another
  galaxy may be drawn for a frame. Capture the MERGED head before trusting it. Never the full suite here (D246).
