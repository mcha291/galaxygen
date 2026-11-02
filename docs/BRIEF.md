# BRIEF — after S82: S68's viewer debts and the zoom's seams in, BUILD_V adopted; next is S83, BUILD_V row 83 (robustness and comparison)

**The state (2026-11-02).** BUILD_V is adopted (D248; `docs/BUILD_V.md`, the board's §5h): rulings 2–6 of its §6 stand
as recommendations until the owner takes them (S84 needs ruling 2 on T17's structure, S86 ruling 4 on the pin per
batch). S82 (D249) built #187 (`useLoad`'s `role`: the swap's dependent loaders ask inside the swap, the camera's never
hold), #188 (a landing holds the old picture under its own line until the new template's answers are in, drawn with
its own display tuning — `drawnTuning` / `LOAD_TUNING_KEYS`), #190 (the caption left of the open drawer), #178 (the
light past the instrument's clamped box drawn where it falls by a coarse second pass, nothing returned; the PSF table
in a Worker, the pupil image freed) and #172 on the owner's ruling (A: the field mode's region regime draws the
catalogue's light-scaled tiles, the sampled reading kept behind the per-template switch 'region stars' (catalogue / sampled) for comparison).
The captures unmoved (the zoom captures are the star-first mode's). #186 moved out of the viewer rows (an API change under the model's hash: the first model batch). **The model's
hash is f1fbbb17eff3c1dc003abcd38117cb1f** (since S77). Register **130 open = 11 + 119, 63 discharged**; next number **#211**, decisions from
**D250**. #210 opened: `ngc_4414-zoom` has not been the committed bytes since some session after S70 — read the picture
test's verdict lines at every close (S82's lesson), never `git status` alone.

## S83 — BUILD_V row 83: robustness and comparison (a Fable lead, two Opus builders)
- **T13, the renderer survives a lost WebGL context** (`VIEWER_TASKS.md` row T13; the owner saw five losses and a
  black stars regime in the app's pane): the context-lost / restored events handled in `GalaxyView` and the field
  volumes (the march's targets, the raster and PSF Workers' textures, the mesh's textures rebuilt), a forced loss
  (`WEBGL_lose_context`) then a drawn frame as the test; the picture test byte for byte.
- **T16, a comparison view**: (i) two seeds / sets side by side (the same camera, the existing tabs' state, no second
  model call where a bundle answers); (ii) a picture file the user picks drawn beside the frame at a stated band and
  scale (the scale bar, the band's name; none bundled). Display choices as sliders where they are choices.
- **T11, "as JWST"**: NIRCam's curves (the download accepted by the owner 2026-11-02: `tools/fetch_filters.py` as
  WFC3's, SVO) and a hexagonal pupil for the PSF (`hstPsf.ts pupilImage` takes the optics: add the segmented aperture,
  the table built by the same job in the Worker). A new filter set, no template carries it by default: the frames stay
  byte for byte; the set's about text and the instrument's in `instruments.json` by the tool, not by hand.
- Read: T13 / T16 / T11 in `VIEWER_TASKS.md`; D227 (R1–R3, the PSF), D249 (the wings' pass, `psfTableJob.ts`), D232
  (the tabs since V9); `GalaxyView.tsx`, `FieldVolume.tsx`, `rasterClient.ts`, `meshTexelsClient.ts`, `psfTableClient.ts`.

## What waits on the owner
- **BUILD_V §6 rulings 2–6** (T17's structure; #189 retire the reference client; the pin per batch; Audit VI at the end;
  the deploy whenever). **Confirm** S80's (a) and S81's Worker. **#210**: name the session by re-taking the capture on
  each tag, or rule that a within-tolerance byte change needs no name.
- **The subscription and the deploy** (D239 (i)–(ii)), then the deployed probe. Housekeeping deferred: delete nothing.

## Traps (S72–S82's stand)
- Never run the full suite, `verify_clone` or the pins unprompted (D246): ask the owner where the model, a fixture or a
  pin changed. The fast gates: `npm --prefix frontend run test` / `typecheck` / `typecheck:e2e`, then
  `GALAXYGEN_PICTURE=1 GALAXY_BUNDLES=C:\Users\Semaphore\AppData\Local\Temp\galaxygen-s78\bundles uv run pytest -s
  tests/test_picture.py` (14 passed; grep the log for "byte for byte" / "not the committed": every capture named),
  then `tools/progress.py` and the docs tests. A fresh worktree needs `npm ci --prefix frontend` first.
- The picture test's port 8019 is one builder's at a time (`reuseExistingServer` takes a sibling's server): say who runs
  when. Two builders sharing a file's line conflict at the cherry-pick: resolve by hand before the gates (S82).
- The shader snapshot `fieldFragment.s78.glsl`: a change to the march is a change to that file, made knowingly. Rule D2
  refuses a second `fetch(`. The register's count pin in `tests/test_audit.py` and its pinned items move with every
  entry. Every byte under `model/galaxy` is in the hash: a change there is a model session, a new image and pin.
- Builders: worktrees cut from the session's branch, one commit per item, no push, no DECISIONS; the lead cherry-picks
  and runs the gates again on the session's tree; a builder's next item starts from a worktree reset onto the session
  branch (`git checkout -B`). Two agents at once, one heavy. The owner's servers on 8017 / 8018 / 5173; agents 8050+
  (the probe 8050 / 8060, the picture test 8019). No backtick in a shell string; messages and scripts via files (the
  Bash heredoc rewrites a doubled backslash: the Write tool for scripts).
- CI: every push the fast job; the nightly run is the suite of record, read at the open after a model merge. A side
  session on the same day claims its numbers in the shared notes; renumber on a fresh branch before merging `main` in.
