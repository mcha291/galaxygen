# BRIEF — after S97: the pictures, first part (D266) — the display pass is the owner's; BUILD_VI waits on its adoption

**The state (2026-11-12).** S94–S96 (Audit VI, its fixes, the reading session; D263–D265) are in `main`. Asked what
follows, the owner said **"The pictures"**: `docs/BUILD_VI.md` is drafted on that word, not adopted. **S97 ran its row
97 (D266):** two display controls built - `knotsIntensity` (the field mode's knots' drawn light; 1 keeps the closure)
and the Tuning panel's "load a combination" (a copy box pasted back); the diagnosis's experiments finished - the bloom,
not the tone curve, reverses NGC 4414's colour and makes the burnt core, the 6500 K white makes the tan; sixteen
combinations measured for the owner to load (`READING_PICTURES.md` §11); the three model gaps traced to their laws (§13).
No display default, no frame, no model byte moved. **112 open = 46 + 66, 99 discharged**; next #229, D267. The nightly on `main` green (run 43117828717).

## The two headlines
- **The display pass is ready, and it is the owner's** (BUILD_VI row P-2): paste a box from `READING_PICTURES.md` §11 into the Tuning panel's
  "load a combination", press Apply, tune live, paste the copy box back. The two display choices that carry most: the bloom's strength and threshold
  (the white ball, NGC 4414's reversed colour, half the bar's ring) and the white point (the tan). With the bloom off or at 0.35 and a white point
  near 4500 K the Milky Way reads as a blue-white barred spiral and NGC 4414's colour step takes the goal's sign.
- **What the model lacks is now named by law:** #227 a defect (the stellar height read at the Milky Way's `R_SUN` on every template: 926 pc on
  NGC 4414, where the same law's mass-weighted mean is 222); #181 the knots as regions; #144 / #147 the lanes (no shock in a co-rotating arm;
  the bar lanes' placeholder width); #146 the bar's amplitude a seeded draw, not a loss. The frames: byte for byte yesterday's, as far from their goals.

## What S97 left (and what S95–S96 still carry)
- The viewer: the paste box's Apply click has no committed test (the runner's end-to-end bytes are the evidence); `gasIntensity` does not reach the knots; #226, the field's circle at 23.6 kpc under a cool white point, cause unknown.
- Noted, not pursued: neither template publishes a thick disc (`thick_disc_stellar_mass` 0) - S98 checks an entry owns it.
  S98 (row 98) reads: Kregel et al. 2002 (#227); Díaz-García et al. 2016's A₂ and the Milky Way's own bar (#146); Kim
  & Ostriker 2002, Wada et al. 2011 (#144); a bar lane's width (#147); the clouds' angles against the arms (#228).
- From S95: the catalogue's price a record with no bound (#154); the kept windows' check one-sided; the exemption in
  `tests/test_one_threshold.py`; the sliver test's 1e-20. Queued for batch P: F-1A-1, F-1A-6, F-1B-4, the isochrone
  labels' caveat, F-2-3's comment; #220's, #224's, #225's mends; S96's builds (#130, #95, #136, #181), #146's citation.

## Rulings taken on recommendation — the owner may re-rule any
- #218's second part: three more draw-path products ordered (sfh, bright, chemistry_dtd); #166 discharged by the gate's ruling. #173 discharged at S95 as not reproducible (D263).
- #175's `kept=1` opt-in (the builder's); its WFC3 size clause held strict on #222, the 32 kB bound unmoved. #115 met in part: membership by class, not a per-star `star_cluster_index`.
- #118 (a) the +0.2 dex edge the grid's limit; (b) met on Sanders et al. 2016's atomic data. #117 carried on #124's ruling; #124 carried past M3 as a build item of its own.
- `s83-robust` merged (T11, T13), the one conflict resolved keeping S84's status dot. The request fixture respelled by hand; `jwst_nircam` held to `wfc3`'s; the three-legs record re-pinned, not re-run.
- #219 discharged at S92 on the gate's ruling (D261; F-5-4); the layer-off reference re-based, #218 discharged on it (D262 item 11). The guard in place of a subprocess pair at two thread counts; the solve and the einsums left unordered and named (D262).
- At S94's gate: `PRICE_RECORD` a record, `WING_BLOCK` a sampling bound, #146's two named rows, the readings ordered.
- At S95's gate: 0.27 not relaxed (#220 a population finding); #224 opened, no bound moved; F-W-1 mended in the viewer; the fixture re-recorded from the walk.
- At S97's gate: no default moved; `knotsIntensity` a display balance; #144 kept permanent pending S98's reading; #226-#228 opened.

## The owner's, still owed (none blocking)
1. Adopt BUILD_VI (drafted on your word; its section 6 holds six rulings, each with a recommendation).
2. The display pass: load, tune, paste (BUILD_VI row P-2) - and with it the order of features for the model batch
   (recommended: #227, the knots as regions, the bar's amplitude if S98 finds the Milky Way's, the arms' lanes last).
3. The L1 gate's judged statistic (F-3B-4, #223): one default census, or the nine-seed mean (recommended).
4. A cadence for the pinned nodes (F-3B-3): the three read by name at every model batch's close (recommended).
5. Any re-ruling of the rulings above: D262's eleven and the four Audit VI adds.
6. The looks: the regenerated frames, #156, #157, #169, #202, NGC 4414's reversed colour gradient (F-4-6).
7. The standing owner's-word items: #107, #179 (downloads), #203–#205 and T19 (the deploy).
8. The concurrency S94–S96 used (three agents at once, two heavy during S95): to refuse or keep.
9. The readings' five rulings (D265), each two named rulesets: #80 the bar's length law (Table 3, or Table 4 with a stellar mass at checkpoint 3 — rule A1),
   #153 the pitch's dependence on shear (as it stands, or none with the S4G type mean — recommended), #92 the PAH fraction's law (metallicity or sSFR),
   #94 the diffuse molecular share (none — recommended — or Roman-Duval's 25 %), #138 the arm-number law (as before).
10. Whether the ionized gas intensity should reach the knots (today it scales the field's HII remainder only).

## The rules said again, and the traps (S72–S97's stand)
- **Two-thirds**: a lead past two-thirds of its context hands back. **Commit each item when green** (`git commit -F`).
- The runner's suite once, on the final head (`gh run view`); the `machine_pinned` nodes a change touches read by name.
- Never the full suite, `verify_clone` or the pins unprompted (D246); one single-threaded pytest at a time, `tasklist`
  first; no backtick in a shell string; any byte under `model/galaxy` moves the hash.
- pytest's collect-only under the project's `-q` prints no ids, and an empty argument file runs the whole suite: count the ids first (S94).
- One change against the control per experiment; a display default is never moved by a session (D227).
