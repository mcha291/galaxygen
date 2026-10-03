# BRIEF — for S53: the owner's choice, after the gas's own pattern and the dust heated in its layer

**The state (2026-10-03).** S51 and S52 are merged (D210, D211). **The gas has its own arm pattern**
(`gas_pattern`: a ridge on the stellar arm's crest, FWHM 0.17 of the arm-to-arm period, `gas_arm_contrast` 2.73 derived
by `bar`, no draw; crest 3.07, trough 0.53); the render places the dust and the HII regions' light by it — a thin dark
lane along each arm's spine (`docs/design/screenshots/s51-*.jpg`) — and today's star formation and the cloud census
read it. **The dust is heated in the geometry it is drawn in** (`dust.layered_absorbed_fraction`: the stars' layer
through the gas's): L_IR 1.2006e10 L☉, the infrared share 0.2616, T_d(R₀) 18.52 K; the scattered share with it.
Register 69 open = 11 + 58, 45 discharged. Specs 12 / 20 / 5 of 37.

## First
`uv run python tools/bootstrap.py`. S52's close ran the full suite (its `EXIT=0` line) and `verify_clone` on `main`;
a session opened in a fresh context runs both again before new work.

## The owner's choice (ask; none is scheduled)
1. **The owner has not yet looked at S51's lanes or S52's cooler inner disc.** What the look may order: the
   contrast's withdrawn draw restored or re-sourced (#131 — the first draw read 10.0 from a spread over segments), the
   ridge's width from more than one galaxy (#129), the HI's lower contrast (#130), an offset to the arm's inner edge
   (D210 ruling 3's named alternative; needs a spiral pattern speed, #81), the bar's own straight lanes
   (`RESEARCH_AREAS.md` §1, direction h), spurs off the ridge (direction e, which needed d first).
2. **#128's remaining half: the heating at the dust's placement, not the ring's mean column.** Measured in the
   layered geometry at 1.0007 of the mean column's over the disc and 1.014 at R₀; applying it needs a seeded extension
   of the dust stage (every dust number then moves with `pattern_seed`). The owner's ruling.
3. **T28: a remainder-only render request** — each new threshold refetches 9 MB of which one component differs.
4. **How a planetary system is shown** now that a click does not open one (D209): the owner's design.
5. **T1, the display defaults**, and the cloud markers (true size, fainter, or the dark patches they are).
6. **T12, the image-level test**, needs a headless browser on this machine.

## Traps
- An Agent worktree is cut from `main`: commit the ruling first; the builder's first step is `git merge --ff-only`.
- A stage's restricted view answers False for an undeclared constant: `GasPattern.from_fields` then returns None and
  the layout goes flat silently — declare `GAS_ARM_WIDTH`, `GAS_ARM_MASK_WIDTH` and `gas_arm_contrast` where it is built.
- A census row (35, 37) moves with any redraw of the clouds; a pin on a census number is a pin on a realisation.
- The dust past the stellar disc's edge has no gas height: it is not heated (T_d NaN there) and not drawn.
- The render's scattered share costs two layered quadratures per ring and filter (warm render 0.2 → 0.3 s).
- Editing the register while the suite runs fails `test_progress` alone: regenerate the board (`tools/progress.py`).
- A stale :8017 from an earlier session serves old code: stop it by PID (check its command line), then `preview_start`.
- An idle Browser pane draws no frames: call `window.__galaxygenFrameSum()` before a screenshot.
- Edge-on and close in, the frame is black: the camera is inside the dust (A_V ~50 through the centre).
- Python writes CRLF here and heredoc writes have failed with Errno 22: write with `newline="\n"`, check the file.
- A long Bash command over 8 KB is cut: put scripts in the scratchpad and run them.
- RENDER_PHYSICS §8 binds: no frame-seeded noise, no detail below the cloud vector, no colour for appearance.
