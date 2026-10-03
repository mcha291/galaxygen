# BRIEF — for S53: adopt BUILD_III (proposed), then its Phase 0

**The state (2026-10-03).** S51 and S52 are merged (D210, D211): the gas has its own arm pattern and the dust is
heated in the geometry it is drawn in. **`session-53` is open and holds one thing: `docs/BUILD_III.md`, a proposed
third build, written on the owner's word and not yet adopted.** Register 69 open = 11 + 58, 45 discharged. Specs
12 / 20 / 5 of 37.

**Why a third build.** The owner put two goal pictures in `docs/goals/` (an artist's Milky Way; Hubble's NGC 4414)
and asked for a review against them on two axes. The finding: the model is ahead on content and behind on shape,
the viewer is behind the model, and the leftovers S53 was going to choose among do not close the gap. The owner's
direction: physics up to what a fast generation affords, and **a separate randomness layer** for what the physics
cannot place. The owner's four orders: two templates in the viewer; a clean separation of the physics model from
the randomness layer; the ten model items and the per-ring gas shock; the viewer's rendering brought up to them.

## First
`uv run python tools/bootstrap.py`. S52's close ran the full suite (`EXIT=0`) and `verify_clone` on `main` (OK at
551bbbf); a session opened in a fresh context runs both again before new work.

## Then: the owner's ten rulings (BUILD_III §7), recorded as D212
1. Adopt the plan and its numbering, S53–S66. 2. The fourth kind of quantity, *synthetic*, and the layer's five
rules. 3. `RENDER_PHYSICS.md` §8 and rule D5 amended. 4. Templates (rules A5, D1), with pins. 5. **The goal images
committed to this public repository with their credits — they are untracked today, and the close's clean-tree
check will fail until they are committed or moved.** 6. A headless browser installed for the picture test, or
manual captures. 7. `basic` and `azimuthal` as one model with the layer switch. 8. NGC 4414's checks: blind
windows or display only. 9. Pictures first (V5, V6 before Phase R)? 10. The dependency rule stays numpy-only.

## Then: Phase 0 (this session, Fable leads)
The rule amendments in `RULES.md` and `RENDER_PHYSICS.md`; `RESEARCH_AREAS.md` and `VIEWER_TASKS.md` pointed at the
plan; `tools/goal_metrics.py` and the React viewer's picture test (two Opus builders in worktrees); the baseline
table — both goals, both of today's renders — in D212; board row 53; BRIEF for S54 (Phase T, an Opus-led session).

## If the owner does not adopt it
The earlier choice stands (`git show main:docs/BRIEF.md`): the owner's look at S51's lanes and S52's numbers;
#128's placement half; T28; how a planetary system is shown; T1; T12.

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
