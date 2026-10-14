# BRIEF — S63: BUILD_III's Phase V5, light by age in the field (an Opus lead; Fable at a stop condition)

**The state (2026-10-14).** S62 is merged (D221): Phase L2 built **`gas_fluctuation`** — one noise with L1's, its
three octaves continued by three finer on the same seed path, the gain steepened by one below the disc's thickness
(an octave is "below" when four times its lattice scale lies under π × the ring's gas scale height), the log-normal
width σ = 0.501 from Burkhart & Lazarian's relation at M = 6 km/s over the cold neutral medium's 0.675 (Heiles &
Troland 2003's 70 K, read), the shear's strain −2A·min(1/A, 30 Myr) applied in polar form, unit mean per cell, an
evaluator and committed vectors; **nothing reads it until V7** — and **the spurs**: a layer census `gas_spur` walked
along each chain at ten Jeans lengths of the ridge, composed into `gas_density_contrast` by a new stage `spurs`
after the star formation history (g′ = (1 − ⟨S⟩)g + S, the ring mean exact), 48 on the Milky Way, none on a
flocculent disc. Register 99 open = 11 + 88, 48 discharged; next number **#165**, decisions from **D222**, board
row 63, acceptance rows from 38. The owner's standing order: run the sessions back to back, stop only for a ruling
that is theirs; S61–S62 were led by Fable with Opus builders on the owner's word — re-read their latest word on
models and on the usage windows (the rationing rule: no heavy agent past 50 % of the 5-hour window; stop and ask
past 80 % of a weekly one) before spawning.

## Read
- `BUILD_III.md` §5 **Phase V5**: `/api/render` returns `stars_young`, `stars_middle`, `stars_old`, each through
  the curves on its own and placed by its own weight (the gas contrast, `sfr_modulation`, the stellar contrast),
  summing to `stars` per ring and filter to rounding; the field mode draws the three; **no stage changes**. Gate:
  the closure; the arm–interarm colour difference before and after (`tools/goal_metrics.py`); payload and timings.
  Two builders: the render route and its tests; the viewer. No reading is listed: none was taken.
- D221 (S62's record) for what the render will one day read: the field's `evaluate`, the `ring` and `cell`
  tables, #163; and what the spurs did to the gas contrast the young light is placed by (#164: a spur's foot
  stands on top of the ridge, so the crest doubles at the foot — the mend S_foot = crest − g is one pass, and V5's
  young light will show it; the owner's look).
- `docs/RENDER_PHYSICS.md` (the contract), `model/galaxy/stages/light.py` and `spectra.py` (the SED, the filter
  integral), `model/galaxy/api/service.py` (`/api/render`), `frontend/src/galaxy/FieldVolume.tsx` and the field
  regime's colour (D188), `tests/test_render.py` (the V1/V2 gates), `tools/goal_metrics.py` (the arm–interarm
  colour difference is its "arm / interarm, blue" column: S62's frames read 1.410 field / 1.743 star-first for the
  Milky Way, 2.064 / 2.216 for `ngc_4414` at the instrument's default geometry).

## Told to the owner (none awaited; if they answer, their word comes first)
- (a) The spurs' spacing: the law's ten Jeans lengths of the ridge (Kim & Ostriker 2006; M51's measured 10.4) gives
  5–7 kpc at the solar circle on the Milky Way template because its gas crest is 1.1–1.55 of the ring mean (#155);
  Kim & Ostriker 2002's thin-disc 2.5 would give 1.2–1.7 kpc. Both are sourced; which is theirs.
- (b) A spur's foot doubles the ridge's crest (#164); the mend is one pass and moves every layer-on gas pin.
- (c) The gas field is built and read by nothing; its look is V7's (S65). Its normaliser table costs ~5 s a run
  (#163). The shallow slope above the thickness at the solar circle is a disclosed miss of the one-noise
  construction (the band is a fifth of a decade wide).
- (d) Still theirs: the default seed's cloud draw (the lowest of 300), the whole-disc routes' cost (#159), the
  pitch floor (#142), Erwin's bar frequency (#145), the lanes' width (#147), the 88-minute gate test (g).

## Traps learned at S62
- **A derived spacing is read on the model's own inputs before it is ruled**: the builder's probe of the law at
  three radii on the template, before any code, turned a 100–2 000 pc expectation into a 5–7 kpc fact.
- **Value noise carries an octave's power near four times its lattice scale**: a mapping of octaves to a break by
  the lattice scale alone put every octave below the thickness beyond 5 kpc; the measured mapping is π/4.
- **A field needs a sound speed for the phase it stands for**: the model had one dispersion standing for every
  phase; the new constant was fetched and read, not recalled.
- **Two builders in one session each own disjoint files; the later one rebases**, and the bookkeeping tests
  (`test_layer`, `test_graph`, `test_fielddoc`, `test_pieces`' lists) are resolved once, by the one who knows both.
- **A builder waiting on its own background test runs can cycle without reporting**: tell it never to leave a
  run in the background when it hands back, and ask for the hand-back when it stalls.
- Keep every Bash command under 8 KB; scripts in a per-agent scratchpad sub-folder; capture pytest's own exit
  code; background the suite with its EXIT line; layer off nothing may move; nothing is tuned to a goal picture.
- Look at the frames beside the goals before the close and say plainly what they show.
