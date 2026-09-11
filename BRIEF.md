# BRIEF — for S22 (close-out), from `session-21-a` (Audit II, aim (a), Fable 5.1)

This branch is **sealed**: never merge it into `main` or into `session-21-b`; port it (D99). It changed
no physics, constant or default — the table reads 10 / 12 / 2 and 8 / 15 / 1 as S20 left it — and it
used debts **#51, #52** and decisions **D130, D131** of its reserved #51–#64 / D130–D143. Aim (b)
(`session-21-b`, Opus) has its own #65–#78 / D144–D157 and its own BRIEF; read both before porting.

## What to port from here (AUDIT_II_A.md §5)
- `tests/test_audit_ii_a.py` verbatim (twelve tests, ~1 min; it imports helpers from `test_audit`).
- `AUDIT_II_A.md`, and `tests/test_docs.py`'s `SESSION_DOCS` entry for it.
- GALAXY_INPUTS.md §11: **#51** (the ensemble is one fixed sample, median residual −0.58σ) and **#52**
  (row 14 is −46 and +28 cancelling); amendments to #11, #19, #27, #28, #42, #46, #47, #48, #49, #50.
  `tests/test_audit.py::test_the_register_carries_the_s10_findings` now asserts 34 / 18 and the two
  new headings.
- `galaxy/specs/spec.py`: the predictions of rows 3, 5, 9, 11, 12, 14, 20, the advanced 6, 22, 23 and
  `_NO_VALLEY_PREDICTION` each carry an appended "S21 (a)" reading; the row 7 removal note carries
  the citation finding. The old text is kept above each — port the entries whole.
- DECISIONS.md D130 (the verdicts) and D131 (timings); LESSONS.md "From S21 (a)"; MANUAL_TODO.md's
  S20 row now carries `7e96422190ab` and its literal tag command. The board row 21 is ◐ with the
  model used; S22 ticks it ☑ once both lists are on `main`.

## What this run hands S22 to rule (each with its number in AUDIT_II_A.md)
- **#19 / #49 — the split criterion.** Star formation off 1.0–3.8 Gyr on the fast first infall lands
  rows 8, 9, 10, 11 together with row 5 at 1.61 (A-5). By #19's own sentence the criterion "born before
  the last major merger" is what is wrong. Rule it; nothing in the repo makes that law.
- **#50 — one of the two widths is wrong.** The chemistry's kernel applied to the mass reads row 4 at
  3.49 and row 3 at 244.9 (A-2); the transports do not compose. The bracket was a fraction read as a
  ratio (A-1). Rule with #28: a narrower kernel lands the advanced row 23 with young/old at 1.22 (A-10).
- **#42 — `MERGER_HEATING`'s citation** is Bensby+03's adopted 35 with no error bar; the measurement
  behind it is 39 ± 4, at which row 7 reads 1193 (out) and row 3 250.97 (in) (A-14). Row 7's green
  is the round number. Decide whether the constant is re-set to the measurement (then row 7 leaves and
  row 3 returns) or the round number stays with this written beside it.
- **#11 / #52 — the bar and row 14.** 7e9 buckled in reads row 3 at 249.6 (held) and row 14 at 144
  (not 123); no concentration lands rows 12 and 14 together; the isotropic dispersion is the suspect.
- **#27 — the valley opens on a burst inside the α-fall** (1–2 Gyr on the fast infall, cut 2–3 Gyr):
  a real mode at +0.35, a tenth of the mass, the advanced row 6 at 353 (A-4). D128's clock was wrong.
  Not a build; a statement of what the mechanism has to be.
- **#47 — the advanced row 22 does not see the inner reservoir** (fit window 4–12 kpc); by its own
  reading the wind's tilt (#26) is what is wrong (A-7). **#46**'s sweep cannot judge (A-8).
- **#51** is aim (b)'s kind of finding (an instrument): the diagonal 0–40 is one draw; rows 16/17
  hold on 41–81, row 18's number moves 0.3 dex with the width.

## Traps
- The audit tests substitute `sfh.star_formation_rate` with a call-counting object: one instance per
  `run`, never reused. `Window(...)` assumes the default grid (2000 steps, 13.8 Gyr).
- Write files with `newline="\n"`; the full suite outlasts the tool's cap — background it with
  `EXIT=$?` appended and gate on that line. The three S10 audit branches stay unmerged.
- `test_the_catalogue_is_priced_per_cell` is still flaky under load (D115) — aim (b)'s.
