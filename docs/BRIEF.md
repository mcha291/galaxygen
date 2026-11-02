# BRIEF — after S83: robustness and comparison in; next is S84, BUILD_V row 84 (T17, the design system) on ruling 2

**The state (2026-11-02).** S83 (D250) built T16 (the comparison view: two galaxies side by side under one camera —
`cameraLink.ts`, `ComparePane.tsx`, `workflow/comparison.ts`; a picture file beside the frame at a stated band and scale
— `PictureBeside.tsx PictureFrame`; a session switch, off in every capture), T13 (the renderer survives a lost WebGL context: `contextLoss.ts`, the frame loop paused and a status line while lost, the march's and the region's targets re-marched on the restore's generation, the rest three.js's own re-upload; `e2e/context.spec.ts` proves the frame after equals the frame before — the black field without the re-march was the owner's black stars regime), and T11 built on `s83-robust` (aa0eec6) and **held, not merged**: the `jwst_nircam` set (NIRCam F444W / F200W / F090W fetched by the tool, the 18-segment primary as a pupil) fails two of `tests/test_render.py`'s model-table tests and needs a pin in a third — #211, the owner's word under D246. The frames: every capture as before, eight byte for byte and the zoom capture #210's. **The
model's hash is f1fbbb17eff3c1dc003abcd38117cb1f** (since S77). Register **131 open = 11 + 120, 63 discharged**; next number **#212**, decisions
from **D251**. BUILD_V (D248): rulings 2–6 of its §6 stand as recommendations until the owner takes them; **S84 needs
ruling 2** (T17's structure) and S86 ruling 4 (the pin per batch). #210 (the zoom capture's bytes): the picture gate reads
the verdict lines at every close (`pytest -s`, the `picture:` lines).

## S84 — BUILD_V row 84: T17, the design system as designed (an Opus lead, Fable at the close)
- **Waits on ruling 2.** The recommendation: keep the tabs as they stand since V9 (Science / Galaxy with the edit panel)
  and port the mockup's components to them. If the owner takes it, S84 is: the 20 unported components (of 21) ported
  onto the existing tabs — read `VIEWER_TASKS.md` row T17 and the mockup it names first, then the panels' tests; the
  picture test's captures CHANGE knowingly where a panel's chrome is in the frame (they are canvas reads: check which,
  if any, before promising), re-captured with the reason and the before / after sums; every other capture byte for byte.
  If the owner rules the mockup's tabs instead (Workflow / Galaxy / System / Science), the session starts with the
  tabs' restructure and the port follows; write the plan before the first edit and show it to the owner.
- **The comparison view's limits from S83, as the owner may want them:** the right pane's tuning read at mount; its point
  budget the default; `GalaxyView`'s probes the last pane's; the drawer over the right pane's bar — each a small item
  for S84's lead to take with T17's panels where the port touches the same chrome, or to leave with a line.
- Read: T17; D250; D232 (V9, the tabs since); `App.tsx`, `GalaxyTab.tsx` (the panel, the drawer), `ComparePane.tsx`.

## What waits on the owner
- **BUILD_V §6 rulings 2–6** (T17's structure; #189 retire the reference client; the pin per batch; Audit VI at the end;
  the deploy whenever). **Confirm** S80's (a) and S81's Worker. **#210**: name the session by re-taking the capture on
  each tag, or rule that a within-tolerance byte change needs no name. **#211 / T11**: say whether to pin the JWST set's numbers in `tests/test_render.py` (the `full` fixture run once, on your word), to move the red band inside the grid (F356W), or to leave the set for the M3 model batch that extends the response grid's tails; the commit waits on `s83-robust` in `galaxygen-s83-a`.
- **The subscription and the deploy** (D239 (i)–(ii)), then the deployed probe. Housekeeping deferred: delete nothing.

## Traps (S72–S83's stand)
- Never run the full suite, `verify_clone` or the pins unprompted (D246): ask the owner where the model, a fixture or a
  pin changed. The fast gates: `npm --prefix frontend run test` / `typecheck` / `typecheck:e2e`, then
  `GALAXYGEN_PICTURE=1 GALAXY_BUNDLES=C:\Users\Semaphore\AppData\Local\Temp\galaxygen-s78\bundles uv run pytest -s
  tests/test_picture.py` (14 passed; the nine `picture:` verdict lines, every capture named), then `tools/progress.py`
  and the docs tests. A fresh worktree needs `npm ci --prefix frontend` first.
- The picture test's port 8019 is one builder's at a time (`reuseExistingServer` takes a sibling's server): say who runs
  when. Two builders sharing a file's line conflict at the cherry-pick: resolve by hand before the gates. A builder's
  frame-time measurement while the other builder is on the GPU is a bound, not a number (S83).
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
