# BRIEF — for S52: the dust heated in the geometry it is drawn in (#128), on the owner's word

**The state (2026-10-03).** S51 is merged (D210). **The gas has its own arm pattern**: `gas_pattern` (checkpoint 3)
publishes `gas_density_contrast`, a von Mises ridge in the stellar arm's phase, on its crest (no offset), FWHM 0.17 of
the arm-to-arm period, its amplitude from PHANGS's ratio of means over the source's 1.5 kpc mask; `gas_arm_contrast`
is the `bar` stage's, derived (2.73 at the defaults: crest 3.07, trough 0.53), no draw. The render places the dust and
the HII regions' light by it — a thin dark lane along each arm's spine (`docs/design/screenshots/s51-*.jpg`) — and
`sfh_azimuthal` and the cloud census read it (16 822 clouds, 12 930 clusters, young stars' mean modulation 2.63).
The reading is `docs/READING_GAS_PATTERN.md`. Register 69 open = 11 + 58, 45 discharged (#129–#131 new). Specs 12 /
20 / 5 of 37; rows 35 and 37 read the census and moved (−1.989, −0.1055), statuses unchanged.

## First
`uv run python tools/bootstrap.py`. S51's close ran the full suite (its `EXIT=0` line) and `verify_clone` on `main`;
a session opened later in a fresh context runs both again before new work.

## The task: #128's first half (the owner, 2026-10-03, during S51)
"when you finish, proceed to Option 2 (dust heating). Delegating it to an Opus agent, and review its work yourself
afterwards before comiting." **So: the ruling (D211) first, an Opus agent builds in a worktree and commits nothing,
the lead reads the whole diff and only then commits.**
- **What changes:** `dust.py`'s absorbed fraction becomes the layered geometry's — stars in sech²(z/2h★),
  `thin_disc_scale_height`; dust in sech²(z/2h_g), the ring's `gas_scale_height`; isotropic emitters, absorption depth
  (1 − ω)τ; the escape ∫₀¹ ½[E₂(τA) + E₂(τ(1 − A))] ds as a **fixed** quadrature with a stated error bound (A1) — and
  `spectra.scattered_share` with it, so the frame's balance still closes to 1e-9. `tests/test_dust_layer.py`'s
  `layered_escape` is the independent reference (B3: keep it independent).
- **What does not:** G₀ keeps the mixed slab (its sources are young stars inside the gas layer); **the placement
  round the ring is measured in the new geometry and pinned, not applied** — applying it makes every dust number
  seeded (D55) for under 1 % of the disc's absorbed light. #128 stays open for that half, reworded; the remedy is a
  seeded extension of the dust stage. The flare's pressure clause is another row.
- **The predictions (B4), from S50's quadrature:** L_IR 1.5675e10 → 1.20e10 L☉ (0.766); the infrared share 0.3415 →
  0.2616; absorbed over the slab's 0.590 at 0.5 kpc, 0.913 at R₀, 0.995 at 12 kpc; T_d(R₀) 18.82 → 18.52 K; G₀,
  q_PAH, every stellar and radial field unchanged; the ratio-1 limit returns the slab's closed form.
- **Pins that move:** `tests/test_dust.py`, `test_dust_layer.py`, `test_render.py` (thermal, scattered, the face-on
  record), `test_audit_iii.py`, `test_audit_iv.py`. A spec row that reads T_d or L_IR is reported, not accepted.

## After it, the owner's choice (none scheduled)
1. **What the gas pattern left open:** the owner has not yet looked at the lanes; the contrast's withdrawn draw
   (#131), the width from one galaxy (#129), the HI's lower contrast (#130), an offset to the arm's inner edge
   (D210 ruling 3's named alternative, needs #81), the bar's own lanes (`RESEARCH_AREAS.md` §1, direction h).
2. **T28: a remainder-only render request** — each new threshold refetches 9 MB of which one component differs.
3. **How a planetary system is shown** now that a click does not open one (D209): the owner's design.
4. **T1, the display defaults**, and the cloud markers (true size, fainter, or the dark patches they are).
5. **T12, the image-level test**, needs a headless browser on this machine.

## Traps
- An Agent worktree is cut from `main`: commit the ruling first; the builder's first step is `git merge --ff-only`.
- A stage's restricted view answers False for an undeclared constant: `GasPattern.from_fields` then returns None and
  the layout goes flat silently — declare `GAS_ARM_WIDTH`, `GAS_ARM_MASK_WIDTH` and `gas_arm_contrast` where it is built.
- A census row (35, 37) moves with any redraw of the clouds; a pin on a census number is a pin on a realisation.
- Editing the register while the suite runs fails `test_progress` alone: regenerate the board (`tools/progress.py`).
- A stale :8017 from an earlier session serves old code: stop it by PID (check its command line), then `preview_start`.
- An idle Browser pane draws no frames: call `window.__galaxygenFrameSum()` before a screenshot.
- Edge-on and close in, the frame is black: the camera is inside the dust (A_V ~50 through the centre).
- Python heredoc writes have failed with Errno 22 here, and Python writes CRLF: write with `newline="\n"`.
- A long Bash command over 8 KB is cut: put scripts in the scratchpad and run them.
- RENDER_PHYSICS §8 binds: no frame-seeded noise, no detail below the cloud vector, no colour for appearance.
