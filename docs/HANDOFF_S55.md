# HANDOFF_S55 — gate G1: do the invariants I1–I5, as tested, mean what BUILD_III §1d says?

**For Fable, one short turn (BUILD_III §3b, §3c). Read this file and at most the five ranges named at the end. Run
nothing, explore nothing, write nothing. Answer in at most 80 lines: the verdict on each numbered question in final
wording, the changes required before the merge, and what goes to a later phase as a debt.** Written by the Opus lead
of S55 (Phase R, the separation), 2026-10-04, from three builders' reports and an independent Opus reviewer's
findings (the reviewer read the whole diff, re-derived the S54 reference from the `s54` tag, and measured).

## What was built (all on `session-55`, not merged)

| Piece | State |
|---|---|
| D214, the lead's ruling, committed first | Layer off = the three φ-axis fields are 1 and the censuses get no pattern; every scalar of `bar`, `pattern`, `gas_pattern` unchanged |
| `layer/noise.py` (builder A) | lowbias32 hash in 32-bit integers; value noise divided by its pointwise standard deviation (unit variance everywhere); octaves to a slope; shear; a log-normal map with unit quadrature mean per cell; 632 committed vectors. Nothing reads it yet |
| The model side (builder B) | `synthetic` provenance with `stands_in_for`, `conserves`, `statistic`; `texture_seed` (no reader; one named graph exception); `layer/compose.py`, the only place that tests the switch (an AST test and a grep hold it); `run(layer=)`, `layer=off` on eight routes, every cache keyed by it; the specs judged layer-off; layer stage `cloud_texture` publishing the four cloud columns (same seed, same streams, same values) and three scalars for the viewer's cloud noise; `tests/test_layer.py`, 52 tests |
| The viewer (builder D) | A "physics only" switch adding `layer=off` in one place, the header's echo checked on every route; the cloud interior evaluated with the published octave count, lacunarity and gain; one layer-off capture |

**Behaviour-preserving: confirmed independently.** With the layer on, all 332 / 331 fields of the two models and the
routes' arrays are bit-identical to the `s54` tag (the reviewer recomputed the digests from a `git archive` of the
tag). The six S54 frames are byte-identical. Layer-off, `azimuthal` equals `basic` on all 334 shared fields.
Rows layer-off: 35 −1.989 → −2.081 (passes); 37 −0.1055 → −0.1030 (a miss still); no other row moves by a bit.

## The findings (reviewer's ids; "measured" = on the production grid at the defaults)

**F1 — the invariants hold in expectation only (the one finding that needs a ruling).** Every census draws each
cell's count on the cell's own stream at an expectation that already carries the composed weight. So the switch
re-draws *which objects exist*, not only where they are. Measured, layer off against on: realised cloud mass −1.9 %
galaxy-wide and up to 19 % in a cell ring (26 of 32 rings differ); cluster mass −5.8 %; the census's HII Hα −8.1 %,
up to 43 % in a ring. Over six seeds the shifts are re-draw noise, not bias (cloud mass −1.0 ± 1.7 %, cluster mass
−2.2 ± 2.9 %, ionizing −2.1 ± 6.0 %). **Expected** counts per ring are identical to 1e-12 for stars, bright stars,
clouds and remnants (I2's first clause, tested on the number handed to the draw). No analytic radial field of mass,
light, dust or star formation changes. But: fourteen published quantities move — nine scalars (`catalogue_size`,
three planet-sample statistics, `bright_star_limit`, `cloud_mass_total`, rows 35 and 37's two, and
`dig_halpha_fraction` by 2 ulp) **and five radial fields** (the four forbidden-line Σ(R) from the HII census —
[N II] median 6.6 %, maximum 54 % per ring — and `hot_phase_porosity`, median 12 %). §1d's I1 exempts "every scalar
that is not a census statistic"; it has no exemption for a radial field. §1c rule 2 and A10 say the layer "never
changes a total" and "changes no ring total". The render draws `lines_hii` from those four fields.
It cannot be repaired inside Phase R: a draw that fixes a ring's objects first and lets the layer assign only
azimuth needs new streams, and Phase R keeps every stream.

**F2 — a synthetic column's `conserves` is false.** `cloud_source_offset` reaches 249 pc against a 75 pc radial
step: it puts 1 610 of 12 930 clusters (12.5 %, 43.8 % of the cluster mass) in another radial ring than their
cloud, 157 in another cell ring. Its declaration says no ring's cluster mass changes. (S33's behaviour, unchanged;
the declaration is new.)

**F7 — D214 mis-described the code.** It says "the arm and bar phases stay seeded on `pattern_seed`". There is no
phase draw: the arm phase is ln R · cot(pitch), the bar's angle ln(a_bar) · cot(pitch) — a fixed convention.
Appendix B lists none. What the switch removes today is a law evaluated at a convention, labelled seeded only
because its stage reads a seed (D55). P1's "each mode's phase, on `texture_seed`" is a new draw, not a moved one.

**F8 — label and switch disagree in both directions.** Switched but labelled seeded, with no synthetic
declarations: the three φ fields and every census placement. Labelled synthetic but neither switched nor drawn:
the three `cloud_interior_*` scalars — constants (4, 2, 0.5), the same with the layer on and off (I1 requires a
non-census scalar to be bit-identical; "smooth when off" is done in the viewer). And the four cloud columns are a
function of `systems_seed`, where A10's amended text says "the layer's seed".

**F9 — I4 as coded is narrower than its words.** The graph refuses a non-reader stage that *requires* a composed
or synthetic field. It is not transitive: `nebular` and `bubbles` (physics, not readers) bin by `cluster_radius`,
which carries the synthetic offset — that is how F1's five radial fields acquire the layer. A pattern built by the
constructor rather than `from_fields` would bypass `compose` (no stage does it wrongly today). `sfh_azimuthal` is a
third category, a *composing stage* in `stages/`; §1e puts composition in `layer/`, and in the code the laws are
applied in `stages/` with `compose.py` only the gate.

**F12 — "composed = has a φ axis" will not survive P2 and P3.** The builder identified a composed field by its
axes, with neutral value 1 hard-coded. A law tabulated against azimuth in the pattern's own frame (P2's shock
profile, P3's bar body) would be forced to 1 by I1's test; an additive or phase-like field has neutral 0. The
lead's brief had offered "a flag or the axes"; the builder took the axes.

**F5, F6 — tests and records (the lead will fix these before the merge unless you rule otherwise).** I1's test
exempts every object column wholesale, so nothing asserts a cloud's mass or a star's age is unchanged. "Each ring
keeps its light" sums the `stars` component only. Row 37's miss still quotes the layer-on number;
`test_s45_diagnosis` still diagnoses the layer-on census (its conclusion holds either way: the metallicity path is
−0.0957 on and off). The three composed fields' about lines and the render header do not say what they are with
the layer off. `run.py`, the `/api` route text and `texture_seed`'s about claim "every ring total … unchanged".

**From the viewer's builder.** (i) The viewer still holds parameters of the interior's function that the model does
not publish: per-octave lattice offsets (17.3, 31.7, 47.1) and a seed stride (1013), its own hash constants, the
smoothstep, the measured normaliser 0.2088 (kept with an assertion that it belongs to the published set; another
set draws smooth clouds), the tilt's clamps, the packing of (cell, index) into a seed, four samples per chord, the
pillar rule. Amended D5 forbids the viewer a parameter or seed of its own. (ii) The interior does not conserve a
ray's column in expectation: over 4000 seeds a diameter along the lattice reads 1.20–1.78 × the smooth column and
an off-axis chord 0.94–0.63 (value noise on a lattice centred on the cloud); the volume mean is 1.016 / 0.993 /
0.888 at σ_s 0.8 / 1.4 / 2.0. Both predate S55. (iii) Physics-only against layered, whole frame: 1.0026 / 1.0012 /
0.9994 in R, G, B; starlight alone with the whole disc in frame 1.00003.

## The lead's proposals (for your verdict, not yet done)

- **P-A (F1).** Phase R states what is true: I1, I2, §1c rule 2 and A10 read "expected totals"; the fourteen
  realised statistics are a closed, named list in the test (nine scalars, five radial fields), each with where it
  is computed; a debt is opened; **the ring-first draw is ordered for L1 (S60)**, the phase that re-draws the
  censuses anyway — a ring's object count drawn on a ring stream, the layer assigning cells — after which the list
  must be empty of everything but placement-dependent fits. Until then no acceptance row or check is affected
  (I3: all judged layer-off, where the censuses are the uniform ones).
- **P-B (F2).** The offset's `conserves` is rewritten to what holds (the cloud's mass and the cluster's mass; not
  the ring it is binned in), with the numbers above, under #95; clamping the offset would move a stream's value.
- **P-C (F7, F8).** D214's sentence corrected in place; the record says the label lags the switch until P1, and
  that the three interior scalars are *parameters of a synthetic function*, not synthetic quantities — or they
  are published another way, if you rule the label wrong.
- **P-D (F12).** `composed` becomes an explicit declaration on the field with its neutral value, not a reading of
  the axes; I1's test walks the declaration.
- **P-E (F9).** I4's test gains the transitive case as a *named, closed list* of physics stages that bin realised
  objects (`nebular`, `bubbles`), tied to P-A's debt; no code moves.
- **P-F (the viewer's literals).** A debt beside #110: the interior's function is the viewer's own until V7
  replaces it with the layer's noise and its vectors; nothing more is published for a function about to be retired.

## Questions

1. **F1:** is P-A the right ruling — the invariants restated on expectations with a closed list and the ring-first
   draw ordered for L1 — or must Phase R not merge until realised ring totals are conserved? If P-A: the exact
   amended wording for §1d I1 and I2, §1c rule 2 and A10's last sentence. (Amending A10 again touches a rule the
   owner approved in Appendix A's wording: is that the owner's to approve, and what should the owner be asked?)
2. **F7, F8, Q "anything labelled synthetic that is physics, or the reverse":** your verdict on (a) the three φ
   fields and the census placements switched while labelled seeded; (b) the three interior scalars labelled
   synthetic; (c) `cloud_texture` on `systems_seed` under A10's "the layer's seed"; (d) `cloud_height`, as
   unsourced as the four columns (#95) and left seeded by Appendix B.
3. **F12:** P-D, or keep the axes?
4. **F9:** is a *composing stage* in `stages/` acceptable, or must composition move into `layer/` now? P-E?
5. **F2 and the viewer's findings:** P-B and P-F, or something stricter?
6. Anything in the list the lead proposes to fix (F5, F6) that should instead stand, or anything missing.

## The ranges you may read (at most these five)

1. `docs/BUILD_III.md` lines 48–101 — §1, the separation, with I1–I5.
2. `docs/DECISIONS.md` — D214, from the line starting `### D214.` to the end of the file (about 75 lines).
3. `tests/test_layer.py` lines 60–210 — the closed list and I1's test.
4. `model/galaxy/layer/compose.py` — whole (the switch's one reader).
5. `model/galaxy/layer/cloud_texture.py` lines 40–130 — the synthetic declarations.
