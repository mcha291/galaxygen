# BRIEF — branch `claude/keen-lamport-lldlvp` (S21 aim b). For S22, porting list (b)

**This is aim (b)'s brief, not S21's.** `main` still carries the S21 brief that aim (a)
opens from, untouched — this branch never merges (D99), so nothing here reaches run (a).
Run (b) is closed: `AUDIT_S21B.md` is the list, D144–D150 the decisions, #65–#73 the
register entries, five findings pinned as tests in `tests/test_audit.py`. Nothing
physical moved; the acceptance table reads 10/12/2 and 8/15/1, as it did at S20.

## What to port, and in what order
1. **`AUDIT_S21B.md`** onto `main` beside `AUDIT_RUN1/2.md`, then diff it against aim
   (a)'s list and write the comparison into DECISIONS.md, as D102 did for S10's four.
   The two aims were different by design, so the interesting diff is *what each aim
   could not have found*, not the overlap.
2. **The register entries #65–#73** and **D144–D150**, which are already numbered for a
   clean port (D116): run (a)'s are #51–#64 and D130–D143, so the two lists interleave
   without renumbering. `tests/test_docs.py::test_decisions_are_numbered_sequentially`
   admits a gap only inside D130–D157; once both lists are on `main` the gap closes and
   that window can go back to a plain range.
3. **Two instrument changes**, both in `galaxy/specs/performance.py` with their tests:
   `catalogue_cost` fits and publishes a per-cell price beside the per-star one with the
   R² of each, and `SAMPLES` reaches down to 500 stars. `test_the_catalogue_is_priced_per_cell`
   reads the conditioned fit instead of asserting the sign of a slope the instrument
   cannot establish.

## What S22 has to rule on (each is a choice, not a repair — which is why none was made)
- **#69, the viewer.** Three planets-stage aggregates — `giant_fraction_sample`,
  `mean_planets_per_star`, `planet_count_sample` — are published and reach no surface,
  excluded by rule D4 along with `catalogue_size`, whose count the region census already
  carries. Either a cheap aggregate endpoint answering from the sample the region already
  built, or three declarations ruled viewer-invisible with the reason written in. §5d's
  "done" says the viewer shows every published field, so this one has to be settled.
- **#70, the detector.** `MODE_MIN_SHARE` is a density test wearing a share test's name,
  and at row 9's share with the observed α-width the Milky Way's own thick disc reads
  `single`. Replacing it means choosing an instrument, against the same evidence D128
  read. **Do not just lower the number** (rule B5).
- **#71, the wind pin.** −0.060 ± 0.01 against an S18 refit worth 0.004. Tighten to
  ±0.004 if it reproduces on a second machine, or write the machine spread into the
  comment. One machine measured it here.
- **#72**, `AUDIT_RUN1.md` §2's discharge of debt #24's remainder: the verdict holds, the
  reason was wrong, re-read it with the per-cell price in it. **#73**, `disc_radial_spread`
  reaches the viewer as an image and the number S20 recorded is a reduction over t that
  nothing publishes — a rendering opinion, so A9 makes it a `core/` edit.
- **#65** is left open with a prediction rather than repaired: putting `materialise` into
  the `stages` tuple would make the tuple mean two things at once.

## Traps
- **Write files with `newline="\n"`.** The full suite outlasts the Bash tool's cap —
  background it with `EXIT=$?` appended to its log and gate on that line.
- **`RESUMING.md` is at exactly 120 lines.** Anything added needs something removed.
- The board row 21 is **◐**, not ☑: run (a) has not run. Its "Model used" cell reads
  "(b) **Opus 5**"; aim (a) adds its own half when it closes.
- **Do not merge or delete** `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`,
  this branch, or aim (a)'s.
