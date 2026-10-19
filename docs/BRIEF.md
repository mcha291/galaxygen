# BRIEF — S68: BUILD_III's Phase V9, the generate-first edit panel (an Opus lead)

**The state (2026-10-19).** S67 is merged (D227–D231): Phase V8 — the owner's display defaults per template
(`TEMPLATE_TUNING`; the Milky Way at 96 steps, NGC 4414 at 48 with its own set, opening on RGB); T9 physical (the
obscured Airy through the template's distance and the instrument's pixel; the spikes a switch); the surface-brightness
gates and the GPU light check at the plain display defaults; `gpu_ms`; the clouds re-read and re-drawn on the owner's
questions (D228–D231); the goal metrics' final table in D227's close. Register 117 open = 11 + 106, 51 discharged;
next number **#186**, decisions from **D232**, board row 68, acceptance rows from 38. **The owner's standing order:**
run the sessions back to back, stop only for a ruling that is theirs; re-read their latest word on models and the
rationing rule (at most two agents, one heavy, none started past 50 % of the 5-hour window).

## Build: Phase V9 (`BUILD_III.md` §5, the V9 paragraph; BUILD_IV's W1, moved here at adoption, D222)
- **The owner's direction (2026-10-14):** a galaxy at once; edits on demand, the variables grouped for convenience,
  no enforced sequence. The landing is already a generated galaxy (D198, D213); what goes is the lock-and-sequence
  machinery behind "Edit galaxy".
- **The panel:** the inputs in their registry groups (the checkpoint names, derived from the stage graph, kept as
  group names with no order), every control enabled at all times, seeds as rerolls, pins read-only with their
  source; one **Generate**, enabled when any value differs from the shown galaxy, a dirty marker per group; **Reset
  to template**; the previous galaxy on screen, marked stale, until the new one returns; the checkpoint previews a
  Science tab reached without reopening anything (T18 discharged by construction).
- **The code:** `frontend/src/workflow/` (`Workflow.tsx`, `useWorkflow.ts` reduced to the values, the shown query and
  the generate action, `logic.ts`); `interface/` keeps its routes and loses the staged workflow (BUILD_IV §7 ruling 2
  (a)), `interface/flow.js` reduced to what the panel needs; **rule D1 amended** to BUILD_IV Appendix A's text, the
  old text kept as history. **No model change**: a run is a function of the inputs, `resume=` reuses what is unchanged.
- **Gate:** the picture test's captures byte for byte (the landing did not move); vitest green with the lock and status
  tests replaced by generate-and-reset tests; `tests/test_viewer.py` and `tests/js/flow.test.mjs` rewritten to the new
  rule; `tsc -b` and `vite build` clean; a reviewer walks the panel and reports every control reachable without
  confirming anything. **Agents:** one builder, one reviewer.

## Read
- `BUILD_III.md` V9; `BUILD_IV.md` §7 ruling 2 and Appendix A (D1's new text); RULES.md D1; D198, D213, D222.
- `VIEWER_TASKS.md` T18; `frontend/src/workflow/`; `interface/flow.js`; `tests/test_viewer.py`; `tests/js/flow.test.mjs`.

## Told to the owner (none awaited; if they answer, their word comes first)
- (a) The frames beside the goals (D227's close): the Milky Way the same kind of picture as the artist's impression,
  its arms less distinct and less irregular (m = 2 0.054 against 0.194), no lanes by default, the outer disc grainy;
  NGC 4414 an inclined disc with sheared dust streaks round the bulge, the bulge too bright and compact, the outer
  disc without the flocculent segments and blue complexes, the dust web (dark fraction 0.030 against 0.157) inner only.
- (b) At their defaults the star-first captures draw bloomed points over the cell outlines' grid; their metrics read
  the display, not the disc.
- (c) Carried, theirs: #172 (one mode at zoom), #176 (the speckle; its sampling half open), #164, #159, #142, #145,
  #147, the 88-minute gate test, the stray "v" in `gateway/Galaxygen.AppHost/Galaxygen.AppHost.csproj` (uncommitted),
  #183 (the knots pure green under WFC3, now hidden by RGB), #184 (one stellar height), #185 (sampled stars undimmed).

## Traps learned at S67
- **StrictMode builds a memo twice**: never keep a ref filled inside `useMemo` (the bloom sliders moved a dead pass).
- **The e2e imports app modules** only through `import ... with { type: "json" }` in what they import.
- **Preview servers stop after about an hour**: run the owner's :8017 / :5173 in their Terminal panel.
- **Display defaults move display pins**: gates that test the drawing run at the plain display defaults
  (`addInitScript`); a new default re-pins the physics-only ratio and regenerates captures - say so with the frames.
- **The march is not converged at 48 steps**, even face-on (+4 %): measure both counts before cutting steps.
- **Measure the model before the renderer**: the black blobs were an unsourced height and a fixed Σ, twice.
- Still standing: one picture-test run at a time (port 8019); `rmdir` a worktree's `node_modules` junction before
  `git worktree remove`; Bash under 8 KB; pytest's own exit code to a file; the register pin and its entries in one
  commit; layer off nothing may move; nothing is tuned to a goal picture.
