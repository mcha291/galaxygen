# BRIEF — for S53: BUILD_III is adopted; its Phase 0, Opus-led

**The state (2026-10-03).** S51 and S52 are merged (D210, D211): the gas has its own arm pattern and the dust is
heated in the geometry it is drawn in. **`session-53` is open and holds `docs/BUILD_III.md`, the third build, adopted by
the owner on 2026-10-03, all ten of its rulings answered (BUILD_III §7).** Register 69 open = 11 + 58, 45 discharged. Specs
12 / 20 / 5 of 37.

**Why a third build.** The owner put two goal pictures in `docs/goals/` (an artist's Milky Way; Hubble's NGC 4414)
and asked for a review against them on two axes. The finding: the model is ahead on content and behind on shape,
the viewer is behind the model, and the leftovers S53 was going to choose among do not close the gap. The owner's
direction: physics up to what a fast generation affords, and **a separate randomness layer** for what the physics
cannot place. The owner's four orders: two templates in the viewer; a clean separation of the physics model from
the randomness layer; the ten model items and the per-ring gas shock; the viewer's rendering brought up to them. **Fable's usage is
limited (the owner): every row of the plan is Opus-led, and Fable is called at four short gates only (BUILD_III §3).**

## First
`uv run python tools/bootstrap.py`. S52's close ran the full suite (`EXIT=0`) and `verify_clone` on `main` (OK at
551bbbf); a session opened in a fresh context runs both again before new work.

## The owner's rulings (BUILD_III §7 holds the table and the owner's words; record it as D212)
1 adopted. 2 the fourth kind, *synthetic*: yes. 3 and 4 approved. 5 the goal pictures are not committed
(`docs/goals/` is git-ignored). 6 a headless browser: yes. 7 `basic` is ignored from now on, not merged. 8 five
checks for NGC 4414, fitted apart. 9 the model's phases before the viewer's. 10 numpy-only at runtime; Pillow and
Playwright as development-only tools.

## Then: Phase 0 (this session, an Opus lead; no Fable gate)
The rule amendments in `RULES.md` and `RENDER_PHYSICS.md`, **verbatim from BUILD_III's Appendix A**; `RESEARCH_AREAS.md` and `VIEWER_TASKS.md` pointed at the
plan; `tools/goal_metrics.py` and the React viewer's picture test (two Opus builders in worktrees); the baseline
table — both goals, both of today's renders — in D212; board row 53; BRIEF for S54 (Phase T). **An Opus lead does not
improvise a physics ruling: on a stop condition (BUILD_III §3d) it closes partially and writes `docs/HANDOFF_S<NN>.md`.**

## Traps
- An Agent worktree is cut from `main`: commit the ruling first; the builder's first step is `git merge --ff-only`.
- A stage's restricted view answers False for an undeclared constant: declare `GAS_ARM_WIDTH`, `GAS_ARM_MASK_WIDTH`
  and `gas_arm_contrast` wherever a `GasPattern` is built, or the layout goes flat silently.
- A census row (35, 37) moves with any redraw of the clouds, until BUILD_III's Phase R judges rows with the layer off.
- The dust past the stellar disc's edge has no gas height: it is not heated (T_d NaN there) and not drawn.
- Editing the register while the suite runs fails `test_progress` alone: regenerate the board (`tools/progress.py`).
- A stale :8017 from an earlier session serves old code: stop it by PID (check its command line), then `preview_start`.
- An idle Browser pane draws no frames: call `window.__galaxygenFrameSum()` before a screenshot.
- Python writes CRLF here and heredoc writes have failed with Errno 22: write with `newline="\n"`, check the file.
- A long Bash command over 8 KB is cut: put scripts in the scratchpad and run them.
- BUILD_III §9: the layer never changes a total; no row is judged with it on; no synthetic field is tuned to a goal.
