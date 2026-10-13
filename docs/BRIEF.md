# BRIEF — S62: BUILD_III's Phase L2, the gas fluctuation field and the spurs (an Opus lead; Fable at a stop condition)

**The state (2026-10-13).** S61 is merged (D220): Phase L1 built **the ring-first draw** for every placed census —
a ring's count and every per-object draw on a ring stream, the layer assigning only the sector and the place
within it, so the realised ring totals are identical with the layer on or off, `CENSUS_STATISTICS` is empty and
rows 35 / 37 moved by the redraw alone (−2.05555, −0.097717) — and **`census_clustering`**, a synthetic field on
`texture_seed` placing the clouds (and so the clusters) jointly in radius and azimuth on each level-0 cell's lattice
and the 20–40.7 Myr bright stars with their finest octaves dropped by age. Its gate is judged **against a control**
(the census's own law with the field's width 0): clouds −0.636 / clusters −0.670 on the default galaxy against the
sourced −0.64 ± 0.15; the uniform-random numbers are a disclosed check, not a target. Register 97 open = 11 + 86,
46 discharged; next number **#163**, decisions from **D221**, board row 62, acceptance rows from 38. **The owner's
standing order: run the sessions back to back, stop only for a ruling that is theirs.** S61 was led by Fable with
Opus builders on the owner's word for that session; re-read their latest word on models before spawning.

## Read
- `BUILD_III.md` §5 **Phase L2** with its two added paragraphs: D219's (a ridged, filamentary form is a declared
  choice of look) and **D220's "one noise"** — `gas_fluctuation` is the same lattice noise on the same seed path as
  `census_clustering`, its octaves continuing finer than 47.5 pc with the slope and width L2 sources; **L2 may not
  change the clouds' map** (ℓ = 190 pc, three octaves, σ = 1.75; `tests/test_clustering_gate.py` stays green).
- `model/galaxy/layer/census_clustering.py` (the field, its constants in `level0.py`, the cell lattice and the
  `cell` table), `noise.py` (`fractal`, `fractal_coarsest`, `lognormal_map`, `cell_quadrature`'s pair form).
- D220 part II (the gate re-read: a control, not uniform randoms; why) and the register's **#161** — the per-cell
  conservation cuts the hierarchy's power at the cell scale; rule 2 allows a ring as the unit, and the field's cell
  means entering the clouds' sector weights is the named mend, which L2's drawing beside the finer octaves may be
  the place for. **#159** (the lattice placement's cost: `clouds: whole disc` ~10 s cold) wants a shared per-cell
  lattice when the shader reads the same noise (V7).
- `docs/S61_PROBE.md` is deleted at S61's close; its tables are in D220. The instrument is
  `model/galaxy/specs/clustering.py` (Landy–Szalay, footprints, a control, the fits).

## Told to the owner (none awaited; if they answer, their word comes first)
- (a) The default seed's cloud draw is the lowest of 300 (0.904 of the molecular gas): 6.6 % less cluster light
  than S60; a reroll of the default seed is theirs.
- (b) The whole-disc census routes cost 2.5× cold (#159); their bound on the viewer's calls is still theirs.
- (c) What the field adds is seen only in the region regime below 4 kpc until V6 draws the censuses at galaxy scale.
- (d) The young stars' clustering fades in one step at 40.7 Myr, not the sources' decline (#162).
- (e) The 88-minute gate test in `tests/test_pieces.py` (g) and the closing suite's length, theirs to cut or keep.
- (f) Still theirs from before: the pitch floor (#142), Erwin's bar frequency (#145), the lanes' width (#147).

## Traps learned at S61
- **A placement rule bounds the correlation it can carry**: azimuth-only placement read −0.18 of a −0.64 field,
  a ±190 pc window −0.41, the whole cell −0.63 — probe the placement variants before the ruling names one.
- **The census's own law realised again is the only honest control**; the literal "other seeds, field kept"
  reads 1 because data and control share the clumps.
- **A declared bound is measured over the whole disc, not a sample**: "0.06 dex" was the 90th percentile; the
  maximum was 1.26 dex at the disc's edge. The reviewer found it; declare distributions, not a number.
- **Rebase builders onto the branch, never merge**; cherry-pick only when the branch has not moved under them.
- **Two agents at once, one heavy, none past 50 % of the 5-hour window; read the meter before every spawn.**
- Keep every Bash command under 8 KB; scripts in the scratchpad (sub-folders per agent: builders collided on a
  shared `cost.py`); capture pytest's own exit code, never a pipe's; background the suite with its EXIT line.
- Layer off nothing may move; nothing is tuned to a goal picture; a prediction is read before it is judged and a
  failed one is recorded with its mechanism (D220 records four).
- Look at the frames beside the goals before the close and say plainly what they show.
