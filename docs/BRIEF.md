# BRIEF — for S55: BUILD_III's Phase R, the separation; it ends at gate G1 (an Opus lead)

**The state (2026-10-04).** S54 is merged (D213): two templates as data, `template=` on every route that takes
inputs, `/api/templates`, the viewer's switcher and a lens per template. `ngc_4414` is fitted on four free controls
(the gate's rule: a control is free only if a target measures it); **all five of its checks miss, disclosed, debts
#132–#136**. The 37 rows are unmoved: 12 / 20 / 5. Register 74 open = 11 + 63, 45 discharged. Numbers from D214,
#137, row 38, board row 55. **The owner's standing order (2026-10-03): run the sessions back to back, stop only for
a ruling that is the owner's, spawn Fable subagents at the plan's gates.**

## First
`uv run python tools/bootstrap.py`. S54's close ran the suite (`EXIT=0`) and `verify_clone` on `main`.
**Read `BUILD_III.md` §1 (all of it), "Phase R" in §5, Appendix A's A10 text and Appendix B: that is the ruling.**

## Phase R in one paragraph
A behaviour-preserving restructure: **with the layer on, every published number is bit-identical to today's.**
`synthetic` joins the provenance vocabulary; `FieldDecl` gains `stands_in_for`, `conserves`, `statistic`, required
for synthetic fields; `texture_seed` joins the seeds and binds at the layer's earliest reader;
`model/galaxy/layer/` holds the noise primitives (built and tested first: a point-evaluable lattice noise in
32-bit integer arithmetic a GLSL twin can match, octaves to a stated slope, a shear transform, a unit-mean
log-normal map per cell, committed test vectors), `compose`, and the `layer` switch through `run`, every route and
`galaxy.specs`; invariants I1–I5 as tests; Appendix B's relabels (four cloud columns and the viewer's cloud noise:
synthetic, their debts #95 and #110 still open); `basic` as the layer-off oracle, once.

## Before any builder starts: pin down what "layer off" turns off today
BUILD_III §1e says "with the layer off the composed fields are their neutral value, 1", and Phase R's gate says
rows 35 and 37 "move to their uniform-placement values" and that layer-off `azimuthal` equals `basic` field for
field. Appendix B relabels only the cloud columns. **So the switch is wider than the fields labelled synthetic
today: it neutralises the placement weights the censuses read** (the stellar and gas contrasts, `sfr_modulation`),
whose realisations (the arm phases) become synthetic only at P1. Read the code (`systems.py`, `bright.py`,
`clouds.py`, `sfh_azimuthal.py`, `gas_pattern.py`, the render) and write, as D214's first commit, exactly which
fields are composed, what each is with the layer off, and what I1's "field without a φ axis" covers. **If the
plan's sentences cannot all hold at once, that is a stop condition: put it in the G1 handoff, do not choose.**

## Agents (BUILD_III §3f), then the gate
Builder A: `layer/` primitives, their tests and vectors. Builder B: provenance, `FieldDecl`, the graph's
*placement readers* (I4), the switch through `run`, the API (`layer=off`) and the specs (I3: the acceptance table
and the template checks judged layer-off). Builder C: Appendix B's relabels. Then an Opus reviewer reads the three
diffs against I1–I5; its findings go into `docs/HANDOFF_S55.md` (150 lines at most) with the numbered questions:
do the invariants, as tested, mean what §1d says; is anything labelled synthetic that is physics, or the reverse.
**Spawn Fable on the handoff (one turn, it reads the handoff and five ranges, runs nothing); transcribe its answer
into D214; fix to it; merge only after.**

## Traps
- `tests/test_templates.py` fails when a seed is registered: give both templates their `texture_seed` (0 and 4414).
  The viewer sends the full explicit input vector, so a new seed reaches it through `/api/inputs`.
- No stream changes its seed or its value: the relabels are labels. A re-pin in this phase means something moved.
- A census row (35, 37) is read layer-off once and re-pinned once, with the reason; nothing else in the table moves.
- `basic` is frozen: where a `basic`-parametrised test would need work, narrow it to `azimuthal` and say so in D214.
- The picture test's six frames must stay byte-identical (the layer is on by default): `npm --prefix frontend run picture`.
- An Agent worktree is cut from `main`: commit the ruling first; a builder's first step is `git merge --ff-only
  session-55`, then bootstrap. Worktrees rewrite `core.hooksPath`: bootstrap before the closing suite.
- No third fit of `ngc_4414` (D213, forbidden); no unspent NGC 4414 window is read.
- Scripts go in the scratchpad, never `$TMP`; Python writes CRLF (`newline="\n"`); a Bash command over 8 KB is cut.
- Editing the register or the board while the suite runs fails `test_progress` alone: `tools/progress.py`.

## Owed to the owner (asked at S54's close; nothing waits on it)
A second fit of `ngc_4414` on the reader's own split (M_K and HI in the fit), as a probe, or fit B for the rest
of the build? Until the owner says, fit B stands and #134 stays carried.
