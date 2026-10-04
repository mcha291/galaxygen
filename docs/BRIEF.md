# BRIEF — for S57: BUILD_III's Phase P2, pattern speeds and the gas shock ring by ring (an Opus lead; gates G2, G3)

**The state (2026-10-04).** S56 is merged (D215): the stellar pattern is several arm modes at once — the local swing
window splits the power among m = 2–6 ring by ring, the modes saturate together, their phases are a draw on
`texture_seed` — and the gas ridge follows any pattern, **placed by rank along each ring, a one-session instrument
(#140) that this phase retires**. The Milky Way template is four-to-six-armed outside the bar (#138, re-read at
P3's close). Rows are judged layer-off: 12 / 20 / 5, unmoved. Register 78 open = 11 + 67, 45 discharged. Numbers
from D216, #141, row 38, board row 57. **The owner's standing order: run the sessions back to back, stop only for
a ruling that is the owner's, spawn Fable at the plan's gates.**

## Before anything: the owner's answer to S56's question (D215, the end)
(a) keep the local arm-number law and carry #138 to P3 — **the default if unanswered**; or (b) S26's global window
on every ring. **If (b): S57 opens with that swap** — `mode_law`'s weights from `swing_window` on the global f_d
and Γ, constant in R; the hand-derived test re-pointed; every layer-on pin re-read; no gate turn (D215 ruling 11).

## First
`uv run python tools/bootstrap.py` (S56's close ran the suite and `verify_clone` on `main`). **Read `BUILD_III.md`
§1, "Phase P2" in §5, §3b–§3d, and D215's rulings 7–13: that text is the ruling so far.** The closing suite now
takes about 45 minutes (the ranked ridge).

## The order (BUILD_III §5, Phase P2)
1. **Two readers, blind to the model, in parallel**: the steady spiral shock (Roberts 1969; Shu, Milione & Roberts
   1973) — its equations, the sonic point, the isothermal jump, a published profile with the parameters it was
   computed at; and its width and offset (Gittins & Clarke 2004; Kim & Ostriker 2002) with pattern speeds of
   transient modes. Assemble `docs/READING_GAS_SHOCK.md`.
2. **Gate G2 (Fable, one turn on `docs/HANDOFF_S57.md`), after the reading and before any build**: the equations
   to integrate, the treatment of the sonic point, the fallback where no shock forms (the plan declares the linear
   response), which pattern speed a ring uses when its modes differ. **Carried to G2 from S56**: the ranked
   ridge's published field passes its exact bound by 2.5e-3 (the ring-mean division; the law is inside); two
   expected totals differ by one ulp layer on and off (I1 says bit for bit); the fade's exponent (ruling 8 took 1,
   P2's solver measures it); and what replaces the ratio-of-means amplitude when the shock derives its own.
3. **The instrument first (B1)**: the solver reproduces a published profile at the source's parameters before the
   model uses it. Builder A (solver and instrument), builder B (integration, the pattern speeds, the re-pins).
4. **An Opus reviewer on the diff, then gate G3**: does the solver reproduce the profile for the right reason; are
   the retired constants' checks honest (`GAS_ARM_WIDTH`, the mask, the two contrast constants become checks, a
   disclosed row for PHANGS's ratio of means — its numbers have been printed, D113).

**Consequences the plan names:** a pattern speed per mode (#81's first half; the young-star cut becomes a crossing
time); #129, #131 and #140 re-ruled; D210's ruling 3 (no offset) superseded where the physics signs the offset.

## Traps
- **Check a probe before it reaches a gate** (S56's lesson, the lead's own error): confirm what every reused
  function's argument *is* from its docstring and call site, test the probe against one published anchor, and
  have a builder write one test that re-derives the central quantity by hand, independent of the module.
- **Always run the independent reviewer before a merge**: it found a blocker at S55 and at S56.
- A fixed-step integration, a bisection, a declared fallback: no convergence loop (A1, BUILD_III §9).
- The pattern stage's fields are the law (five `arm_mode_amplitude_m`, `arm_saturation`); `arm_multiplicity` is a
  label nothing may compose from; a pattern object is built only through `layer/compose.py`.
- Layer-off nothing may move: the rows, the template checks, every radial field outside `CENSUS_STATISTICS`.
  Layer-on the galaxy changes again; regenerate the frames (`npm --prefix frontend run picture:update`) only
  after the pins are read, and say so.
- No third fit of `ngc_4414`; no unspent NGC 4414 window read; no bar work and no m = 1 term (they are P3's and
  the owner's); no ring-first draw (L1's).
- A subagent cannot write report files: take findings from its final message. Resume a builder with SendMessage
  for a second pass; hold a branch's merge until both halves of a contract change are ready.
- Scripts in the scratchpad, never `$TMP`; LF newlines; a Bash command over 8 KB is cut (use the Write tool);
  `tests/test_audit.py` pins the register's counts and its carried row.
