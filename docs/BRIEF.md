# BRIEF — for S51: the owner's choice, after the star-first mode and the dust's own layer

**The state (2026-10-03).** S50 is merged (D205–D209), in two parts. *Sidetrack session 1* (branch
`sidetrack-session-1`): component layers in the old brightest mode; `docs/RESEARCH_AREAS.md`; **the dust in its own
layer** (`gas_scale_height` per ring, `/api/render`'s `dust_height`, the march composing light and dust in order) and
**placed round each ring** by the pattern's contrast (`dust_placement`). *S50 proper*: **the star-first mode** replaces
brightest — the N brightest disc stars in view and every cluster as points of their own light on the field's scale,
over the render's remainder at the bright header's `l_min`; one exposure; the dust in front of each point; a click
opens the object's published columns. The closure on screen 0.9995 / 0.9997 / 1.0006 through rgb. **D209: clicking a
star no longer opens its planetary system**; `/api/system` and the planets stage stay. Register 66 open = 11 + 55,
45 discharged (#128 new). Specs 12 / 20 / 5 of 37 (unchanged).

## First, before anything else
`uv run python tools/bootstrap.py`, then the full suite backgrounded with its exit status appended to its log —
**S50 closed without it on the owner's word** (the last `EXIT=0` was on D207's code; S50 proper changed no Python).
Then `uv run python tools/verify_clone.py --ref main`. A failure there is S50's to fix before new work.

## The owner's choice (ask; none is scheduled)
1. **The gas's own arm pattern** (`RESEARCH_AREAS.md` §1, direction d; the owner's stated next): a narrower gas ridge
   than the stars' cosine, so the dust can make lanes. A reading session first — measured gas arm-to-interarm
   contrasts and ridge widths, and the evidence on offsets; the model's swing-amplified arms imply no offset (#81).
   Project rules bar numbers from memory. Then dust on it (render-only), then star formation on it (catalogue pins).
2. **#128: the dust's heating in the drawn geometry** — the layered slab absorbs 0.766 of the mixed one and the
   placed one 1.013 of it; applying it moves T_d, L_IR and every pin on them. The owner's ruling.
3. **T28: a remainder-only render request** — each new threshold refetches 9 MB of which one component differs.
4. **How a planetary system is shown** now that a click does not open one (D209): the owner's design.
5. **T1, the display defaults**, and the cloud markers (drawn at a 2-pixel floor and full strength: true size,
   fainter, or as the dark patches they are — the owner asked why they are so visible).
6. **T12, the image-level test**, needs a headless browser on this machine.

## Traps
- An idle Browser pane draws no frames: a screenshot or `window.__galaxygenFrameSum()` right after a change can read
  a stale frame (the probe now advances one itself).
- Edge-on and close in, the star-first frame is black: the camera is inside the dust (A_V ~50 through the centre).
- The dust's "where it is" diagnostic saturates edge-on at 0 stops (log levels × long paths); −6 stops shows it.
- :5173 and :8017 are started by the session for the owner and stopped by the app after a few hours.
- Python heredoc writes to the repo have failed with Errno 22 here: check the file and retry with the Edit tool.
- A long Bash command over 8 KB is cut: put scripts in the scratchpad and run them.
- RENDER_PHYSICS §8 binds: no frame-seeded noise, no detail below the cloud vector, no colour for appearance.
