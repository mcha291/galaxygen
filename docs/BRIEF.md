# BRIEF — after S87: M1's second session closed into `batch-m1` (D255); next is S88 (BUILD_V row 88), the batch's close

**The state (2026-11-03).** S87 (D255) took the owner's four rulings of 2026-11-03 — **#209** the 1.0° floor on a drawn
piece's pitch (`ARM_SEGMENT_PITCH_FLOOR`, discharged); **#80** Erwin 2019's law for the bar's half-length (2.27 kpc on the
default disc) with the Milky Way's measured 5.0 kpc pinned (`bar_half_length`), rows 15–17 recorded misses under #80 on
the default inputs; **#145** Erwin 2018's frequency a disclosed check, not a draw (the criterion bars 0.91–1.00 above
10^10.5 against 0.48–0.06); **#152** the arm law kept, permanent at S88 — and built **#148**: one clock, the grid's `t_max`
the model's own flat-ΛCDM age 13.467 Gyr (`core/cosmology.py`); row 2 out by 0.020 as predicted and recorded, row 6 in
(345.09 pc, on σ_z), **#212** opened (`MERGER_HEATING` derives 90.62 on this clock against 88.8). #154's render half
re-ruled a viewer pass's; #130 not built (no source gives the atomic dispersion); seven readings each in its
`READING_*.md`. **The hash pin moved at S88 (M1's final model): 4522ff0b17784e14edf852a8ebbac688** (f1fbbb17… pinned until S88; a6a389b9… in fact at S87's close).
Register **121 open = 37 + 84, 74 discharged**; next number **#213**, decisions from **D256**. Branches: `batch-m1` holds
S86 and S87 (tags s86, s87); S88 cuts `session-88` from it, merges back into it, then **merges `batch-m1` into `main`**.

## What the owner is asked (put at S87's close, D255; take each answer as it comes, build nothing on either before it)
- **(a) Rows 15–17**: the acceptance table judges the default inputs (as now; the gate's recommendation — the three rows
  stay recorded misses under #80) or the Milky Way template with its 5.0 kpc pin (a change to `spec.run` and rule A5).
- **(b) #212**: re-derive `MERGER_HEATING` at its fixed point on the model's clock, 88.8 → 90.62, row 3's miss (251.017,
  out by 0.017) written in (the gate's recommendation, B10) — or keep 88.8 declared as the old clock's with the gap beside it.

## S88 — the batch's close (an Opus lead, Fable at the gate; the owner's full suite before the merge to `main`)
- **The six bounds, as ruled at the gate (D255, applied with the strict run)**: (1) `tests/test_bar.py` `RING_MEAN_OVER`
  → the tolerance 2e-13 with the measurement; (2) Audit V's power-budget share 0.934 and (3) its pair-correlation
  slope −0.458 → one probe, the Milky Way's pin on and off on the same seeds, names the cause; the share's declaration
  re-measured with it, the slope's law kept and a composition defect mended or the reading held with the cause; (4) the
  spurs' walk 0.570 → `WALK_READ_DIFFERENCE_COARSE` re-measured over the same feet on the final model, the 0.27
  production bound checked beside it; (5) the drawn `ngc_4414` leg's first-crossing step at 29.42 kpc → mend the count's
  floor if the first-crossing rule misses a redrawn piece at the grid's edge, else hold with the cause; (6) the price per
  cell → re-declared at the measurement with the census's size (54 pieces / 13 chains), non-strict.
- **#152 to the permanent row** (the register's summary rows, the count pin, RESUMING's line) — Fable moves it at the close.
- **The owner's two answers** built as they come (a) `spec.run` unchanged or judging the template; (b) the constant
  re-derived with row 3's miss in `spec._MISSES`, or the gap declared beside 88.8.
- **The hash moves once** (D3 as amended at D235; done at S88: 4522ff0b17784e14edf852a8ebbac688): the docs' pin f1fbbb17… → the final `content_hash(MODEL)` in BRIEF,
  DECISIONS, GALAXY_INPUTS, GALAXY_PLAN, RESUMING; one re-export of the bundles (`tools/export_template.py`); the frames
  regenerated with the reason and **the goal pictures beside them — say how far they are**; the owner's look rules
  #156 (and #157's reopen condition). The acceptance rows the batch touched (2, 6, 15, 16, 17, 35, 37, the arms') re-read
  with their misses written in; `galaxy.specs` to its last row.
- **The tests the batch left unrun**: the layer, API and frames files, test_gas_response strict — in S88's own subset
  before the owner's suite. Then: the lead commits, asks; **the owner backgrounds `uv run pytest` with its EXIT line to a
  file** (D246); the merge of `batch-m1` into `main` waits on that line; tag s88; CI's nightly run read at S89's open.
- Builders: worktrees cut from `session-88`, one commit per item, no push, no DECISIONS; `machine_pinned` tests
  re-pinned with the reason, never loosened; the subset's files as parallel processes with their own EXIT lines
  (test_pieces and test_gas_pattern split six ways: the pieces' gate test alone 1 h 29).

## The gates and the close (each session)
- `npm --prefix frontend run test` / `typecheck` / `typecheck:e2e`; the picture test where a frame is regenerated
  knowingly (S88: yes, with `GALAXY_BUNDLES` at the new export); `tools/progress.py` and the docs tests (`test_docs`,
  `test_progress`, `test_audit`, `test_hook`, `test_graph`); the register's count pin and its pinned rows with every
  entry. D256… in `DECISIONS.md`; `LESSONS.md` tagged; `RESUMING.md` ≤ 120 lines; this file rewritten; `MANUAL_TODO.md`'s
  row (the SHA of the merge into `batch-m1`, then `main`'s).

## Traps (S72–S87's stand)
- Never run the full suite, `verify_clone` or the pins unprompted (D246). A fresh worktree needs `npm ci --prefix
  frontend`. The owner's servers on 8017 / 8018 / 5173; agents 8050+; the picture test's 8019 one builder's at a time.
  No backtick in a shell string; commit messages through a file with `s88_`-prefixed names (a refused Write is a stale
  name); scripts through the Write tool. Two agents at once, one heavy, none past 50 % of the 5-hour window. Read a
  suite's exit from pytest's own line. Stage a hunk on HEAD's text, never `--unidiff-zero`.
- A model change moves every layer-on field; an item-by-item commit that leaves heavy files red names them, and the
  joint re-pin on the final model runs before anything is reported green. Before a whole-model change, list every
  constant whose derivation reads the model's own output (not only those fitted to a row): #212 is the one S86 missed.
