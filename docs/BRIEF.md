# BRIEF — for S47: the renderer, by RENDER_PLAN_II's sequence (the model work is pinned)

**The state (2026-10-01).** S46 is merged (D197, D198). The viewer is reviewed in `RENDER_PLAN_II.md` (where it
stands, every candidate costed, a sequence proposed). Built at S46: **`azimuthal` is the default model** across the
registry (`put_first`), the API, the specs' order, the viewer and the tests' default run — no measured pin moved, the
two models sharing every field but the star columns; **the field march reads each step's layers at jittered
sub-samples** (the terraces at a grazing view were the steps; the box at 16 h) — verified on `prod` before and after
(`docs/design/screenshots/s46/field-grazing-*.jpg`); **the viewer lands on the Galaxy view of the default galaxy and
"Edit galaxy" opens the staged process** (rule D1 amended on the owner's word, D198; the reference client keeps stage
one). Specs azimuthal first, 12 / 20 / 5 of 37 both models. The owner's live servers: the API on :8017 and Vite on
:5173, started on the owner's word at S46 — **never stop or restart them**.

## What S47 could do — RENDER_PLAN_II §3's next rows; the owner chooses (numbers from #125, D199, row 38)
1. **E2 — an image-level test for the React app.** `tools/shot.py` serves `interface/`, not the React app, so no row can
   prove it left the picture intact. Build a sibling that serves `frontend/dist` (after `npx vite build`), lands on the
   generated default galaxy (D198 makes this one load), captures the three regimes and the five filter sets at fixed
   cameras, and compares against committed frames at a tolerance; skipped without a browser as `test_viewer` is now.
   Gate: the captures exist and a changed gain fails it. Half a session. **First, so every later row has a gate.**
2. **B5 — the renderer survives its context.** The app's pane logged five WebGL context losses and the stars regime
   drew black (`RENDER_PLAN_II.md` §1b); the owner's live tab is the check of whether it is the pane's or the viewer's.
   A `webglcontextlost` / `restored` handler that re-creates the targets, a target budget that scales to the context's
   limits. Gate: a forced loss (`WEBGL_lose_context`) then a drawn frame. Half a session.
3. **B3 — the depth-aware composite (#112).** The region's transmission quad darkens stars in front of clouds. The star
   layer's depth written and read by the pass. Gate: a synthetic depth test. Half a session.
4. **B1 → B2 → C2 — points through the filter set, the young population once, the level-k stars** (#114, #115, #113):
   one closure test gates all three; two need a new published field (the owner's leave: the model is pinned). Two
   sessions.
5. **E4 — the march's cost after S46**: 96 × 8 × 6 reads per pixel at worst, ≈ 100 ms per re-march at the pixel budget
   on an RTX 4070 (the harness's number; the Intel GPU untested). A settle-then-refine scheme (fewer sub-samples while
   the camera moves, the full count once it rests) if the owner's machine shows it. Gate: `tools/timings.py`'s table
   and a frame-time print. A quarter.
6. The rest of RENDER_PLAN_II §2 (B4 the first frame's balance with the profile gate; C1/C3/C4/C5; D1–D3; E1 the design
   system; E5 the deploy, whose command is `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha>` — CI builds
   the image on every push).

## Gate for whichever is chosen
vitest, `npx tsc -b` and `npx vite build` clean; the named pytest files green; a `prod` check (:8018, after the build,
stopped after) with a frame saved under `docs/design/screenshots/s47/` when the picture changes; **`uv run python
tools/bootstrap.py` before the full suite** (agent worktrees rewrite the hooks path); the suite backgrounded with its
own `EXIT=` line; merge, push, **tag `s47`**, `ls-remote` read back, the MANUAL_TODO row, `verify_clone --ref main`.

## Traps
- :5173 and :8017 are the owner's. A scratch check uses `prod` (:8018) after `npx vite build`; a reload there lands on
  the generated default galaxy since D198 (six confirmations no longer needed; before D198 the walk cost six round
  trips, `find` before each click, refs stable only within a load). The pane's GPU context is small: a black canvas
  there may be the pane's, not the viewer's — check the owner's tab before ruling.
- RENDER_PHYSICS §8 binds every renderer row: no frame-seeded noise, no detail below the cloud vector, no colour for
  appearance. A dither is fixed by the pixel. A display choice is declared where it is computed (A9).
- Builders in parallel worktrees own disjoint files; `useWorkflow.ts` and `App.tsx` are the shell, touched by most
  viewer rows — sequence those. `uv run` only; LF; the Bash tool fails over ~8 KB; `grep -c` exits 1 on zero; downloads
  (JWST's curves, real imagery) need the owner's word.
- The model is pinned (the owner, 2026-10-01): a renderer row that needs a new published field says so in its ruling
  and waits for the word; the register's model debts (#117, #124 …) are not S47's.
