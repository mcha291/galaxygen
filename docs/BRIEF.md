# BRIEF — after S105: the illustrative look (D275, D276; BUILD_VIII rows 105-110); in `main`; the owner's eye is next

**First, plainly: the viewer can now draw both goal pictures' kind of picture.** Under the new **illustrative look**
(the default since this close) the Milky Way is a blue barred spiral on black - a cream bar with two thin lanes, pale
blue arm bands from the bar's ends, broken red-brown lanes along the arms, pink regions strung on them, a soft edge -
and NGC 4414 is an inclined warm disc lying as the photograph's does: a pale nucleus, cream and tan inside, a brown
dust network in short spiral pieces, a grey-white outer disc with white flecks. **Still far:** the Milky Way's disc
fills about 70 % of the frame against the goal's 90 %, its arms are the model's (fewer, broader), the goal's fine pale
grain is not reached; NGC 4414's network is coarser and more brushed than the photograph's, its white clumps read as
dashes and its outer left lacks star clouds; a streaky brushed texture lies under both (the model's own light). The
two frames: `docs/pictures/s105/`. Words and numbers: `READING_PICTURES.md` Part S105. The **physical look** is the
viewer as it was, byte for byte (the nine committed frames; seven more states compared against `main`'s own build).

## How to see it and tune it
- Pull `main`, run the API and `npm --prefix frontend run dev`, hard-reload (Ctrl+Shift+R). The **illustrative** button
  sits beside **physics only**; a browser that never chose lands on illustrative.
- Tuning panel, group **Illustrative**: the sliders by feature (grade, edge, speckle, framing, regions, lanes, arms,
  flocculent network), each block collapsible, a filter box above ("bar", "pink", "lane"). A slider that rebuilds a map
  shows "rebuilding" and settles 250 ms after the last move (the network's takes about a second). The copy box and
  "load a combination" carry the look and every value; settings are kept per template per look.
- Frames beside the goals: start `uv run python -m galaxy.api --port 8031 --client frontend/dist --bundles <dir>`, then
  `npm --prefix frontend run build`, `GALAXYGEN_E2E_PORT=8031 npm --prefix frontend run look`,
  `uv run python tools/goal_sheet.py --frames docs/goals/look --out docs/goals/look` (list: `frontend/e2e/look.json`).

## The state (2026-11-23)
S105 on `session-105` from `main` c6d7b15, merged into `main` at its close (tag `s105`; MANUAL_TODO row 105). Twelve
agents (ten Opus, two Fable for the lanes and NGC 4414), a Fable lead. Gates on the closing head: vitest 775 passed,
both typechecks, the build, the picture test (the nine frames byte for byte), the docs tests; the full suite
dispatched on GitHub, not run here. **No byte under `model/galaxy` moved** (hash 5a862a70...). The register is as it
was on `main` (115 open = 50 + 65, 104 discharged). Next numbers: #238, D277 (#237 and D274 are `batch-r`'s).

## Rulings taken on recommendation — yours to re-rule (`BUILD_VIII.md` section 4 is the table)
1. Rule D5 and `RENDER_PHYSICS.md` section 8 are amended for the illustrative layer alone (your word, D275).
2. Cut from `main`; `batch-r` (S104) left unmerged and untouched. 3. Viewer-only sessions merge into `main` at close.
4. **The default look is illustrative** (`DEFAULT_LOOK` in `frontend/src/galaxy/tuning.ts`, one line).
5. The model's cloud flecks are off under the illustrative look; lanes and the network are drawn in their place.
6. Brown lanes are a drawing over the picture (the `veil`), not dust in the model's layer. 7. The register frozen.
8. The illustrative frames are not pinned by the picture test. 9. One session for six rows. 10. BUILD_VII parked.

## Known defects of the new layer (none in the physical look)
- A look switch while a generation is pending blanks the field until it ends (the canvas remounts on the stand).
- An intermittent burst of `glGetProgramiv` warnings round a canvas remount; warnings only, frames unchanged; untraced.
- The network's map rebuilds on the main thread in 0.7-1.0 s per shaping change (once per drag since the debounce).

## What the next session does (`BUILD_VIII.md` section 6, in order of what a viewer gains)
1. Your own tuning pass, or your list of what looks wrong: every value is a slider and a per-template default.
2. The streaky texture under both pictures: a smoothing or a switch for the model's synthetic maps under this look.
3. The Milky Way: fill the frame; the arms' fine grain; the regions' confetti. NGC 4414: a finer, feathered network;
   star clouds in place of dashes; the inclination. Then the two defects above and the map in a worker.

## Parked, waiting on your word (nothing here touched them)
`batch-r` 699629c (S104, D274: green, stacked on `batch-q`, one stage-B re-read of `test_s100_bar_length` owed before
its merge; it now also needs `main` merged into it, and D274 enters before D275); the held heads `batch-q-lanes` and
`q-231`; BUILD_VII's remaining rows; your owed rulings (#226, #234, #149, #88, #97/#98, #129, #184, the clustering
questions, S101's list): `git show batch-r:docs/BRIEF.md` is the list. Nine worktrees are on disk
(`galaxygen-s105`, `-s105-b`, `-s105-c` and the older ones): the app denies their removal; yours to remove or allow.

## The rules said again, and the traps
- Under `physical` nothing of the layer runs; a change that moves a committed frame is a defect, never a re-capture.
- The march has NO spare sampler: a feature's map is a channel of the one shared map (`index.ts`'s header).
- Capture the MERGED head before trusting it; every lane's gates were green while the field was black.
- Never the full suite here (D246): `gh workflow run ci.yml --ref <branch>`. No backtick in a shell string.
- Each agent a scratch directory of its own; commit messages through a file; commit at each working step.
