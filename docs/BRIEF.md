# BRIEF — after S86: M1's first session closed into `batch-m1` (D254); next is S87 (BUILD_V row 87), M1's second session

**The state (2026-11-03).** S86 (D254) re-read M1's 23 items on today's model: #139, #142, #198 discharged (the first
two met at S60 and never struck), #154's table rebuilt as the young stars' point reader's cell means (the one model change:
`sfh_azimuthal.modulation_cells`, 2.7e-4 in a cell against 0.62), #186's ranges on the wire (`registry.EVENT_FIELDS`,
`/api/inputs` `fields`), #146's bar body read at checkpoint 4 (Bar/T mass 0.093 a hit, light 0.047 half the stacks', the
m = 2 peak 0.41 a against 0.76–0.94 — the bulge killed as the suspect), #141 / #143 / #155 / #157 permanent at the gate.
**The model's bytes moved: `content_hash` prints 4be843b416a77d713f848a48303ac7c2; the docs' pin stays f1fbbb17… until
S88's close**, when the bundles are re-exported, the frames regenerated and the owner runs the full suite before the merge
to `main`. Register **122 open = 37 + 85, 72 discharged**; next number **#212**, decisions from **D255**. Branches:
`batch-m1` holds S86 (merge of `session-86`, tag s86); S87 cuts `session-87` from it and merges back into it.

## What the owner is asked (put at S86's close; build the rest meanwhile, take each answer as it comes)
- **#152 with #138**: a ridge per measured arm for the Milky Way template (a change of the arm law) — or the law kept
  and #152 permanent at S88. **#209**: the lead's floor, 1.0° on each drawn piece's pitch (redraw while p(1 + 0.56 z)
  < 1°; Reid 2019 Table 2's Sgr–Car outer segment 1.0 ± 2.1°, Honig & Reid 2015's M51 arm B +1.2°; the disc draw's 1°
  clip) — or the ruling that a near-circular arc is what the scatter means. **#80**: keep 2.0 declared a Milky Way fit,
  or Erwin 2019's law with a pinned 5.0 kpc Milky Way bar (row 15 misses by 2.73 under the law alone). **#145**: Erwin
  2018's bar frequency as a draw, or not.

## S87 — M1's second session (an Opus lead, Fable at the gates; two Opus builders on disjoint stages at most)
- **Builds**: #148 the grid's t_max from the model's own cosmology (13.467 Gyr; SFR 1.7552 → 1.8599, **row 2 leaves its
  window 1.46–1.84 by 0.020 — write the miss in first**, S88's suite judges; nothing tuned back, B5 / B10); #154's render
  half (the render's wound read of the table; the azimuth from 25 samples); #130 a second gas response at the atomic
  dispersion once that dispersion is read from a source, weighted downstream by the molecular fraction (the design is in
  #130's S86 line); the owner's answers where they arrive (#209's floor touches the pieces' draw and every layer-on field
  on the seeds it moves; #152 the arm law; #80 the bar's half-length and row 15; #145 `bar_present`).
- **Readings, each to its `READING_*.md` with the entry's line**: #146 the stacks' bars' b/a and profile (DG16b) and a b/a
  distribution; #129 / #131 PHANGS ridge widths and per-galaxy contrasts; #153 Yu & Ho 2019's pitch with shear; #149
  Chugunov et al. 2024's inner arm ends (an inner taper) and a driven A2(r/a) from Salo et al. 2010; #81 the age at
  which a population's arm–interarm contrast decays; #147 a bar lane width; #144 dynamic-arm gas widths.
- **#186's viewer half** (`flow.setValue`, the event editor reading `fields`) is a viewer pass, not M1's.
- Each item: the entry's closer built or the entry re-ruled with the reason, the register line, one commit; the subset's
  files as parallel processes with their own EXIT lines (hours; test_pieces holds the 88-minute test), the targeted
  tests plus test_audit's register tests at every commit; `machine_pinned` tests re-pinned with the reason, never loosened.

## S88 — the batch's close
- The hash moves once (D3 as amended at D235): the docs' pin, one re-export of the bundles (`tools/export_template.py`),
  the frames regenerated with the reason and the goal pictures beside them (the yardstick), the acceptance rows the batch
  touched (2, 15, 35, 37, the arms') re-read with their misses written in, `galaxy.specs` to its last row; the owner's
  look at the frames rules #156 (and #157's reopen condition). The full suite once, the owner's run (D246): the lead
  commits, asks, the owner backgrounds `uv run pytest` with its EXIT line to a file; the merge of `batch-m1` into `main`
  waits on that line; CI's nightly run read at S89's open. Tags s86–s88 at each close all the same.

## The gates and the close (each session)
- `npm --prefix frontend run test` / `typecheck` / `typecheck:e2e`; the picture test only where a frame is regenerated
  knowingly; `tools/progress.py` and the docs tests (`test_docs`, `test_progress`, `test_audit`, `test_hook`,
  `test_graph`); the register's count pin and its pinned rows with every entry. D255… in `DECISIONS.md`; `LESSONS.md`
  tagged; `RESUMING.md` ≤ 120 lines; this file rewritten; `MANUAL_TODO.md`'s row (the SHA of the merge into `batch-m1`).

## Traps (S72–S86's stand)
- Never run the full suite, `verify_clone` or the pins unprompted (D246). A fresh worktree needs `npm ci --prefix
  frontend`; `uv` makes its venv on the first run. The owner's servers on 8017 / 8018 / 5173; agents 8050+; the picture
  test's 8019 one builder's at a time. No backtick in a shell string; commit messages through a file; scripts through
  the Write tool. Builders: worktrees cut from the session's branch, one commit per item, no push, no DECISIONS. Two
  agents at once, one heavy, none heavy past 50 % of the 5-hour window. Read a suite's exit from pytest's own line.
- Stage a hunk on HEAD's text, never `--unidiff-zero`; read an Edit's result before the commit that depends on it; a
  model change moves every layer-on field, and the s78 bundles no longer match a batch run (the service computes).
