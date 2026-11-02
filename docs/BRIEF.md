# BRIEF — after S84: T17 done; next is S86–S88 (BUILD_V rows 86–88), M1 the arms and the bar, the pin lifted for the batch

**The state (2026-11-02).** S84 (D253) ported the design system's 20 remaining components to `frontend/src/ui/` and
drew the panels' chrome with them on the kept tabs (ruling 2, D252); every capture byte for byte (`ngc_4414-zoom` #210's,
as before). D252 took BUILD_V's rulings 2–6: the pin lifts per batch from here. **The model's hash is
f1fbbb17eff3c1dc003abcd38117cb1f** (since S77) and M1 moves it once, at S88's close. Register **125 open = 33 + 92,
69 discharged**; next number **#212**, decisions from **D254**. T11 stays held on `s83-robust` (aa0eec6, worktree
`galaxygen-s83-a`) for #211; #210, S80's (a) and S81's Worker, the subscription (D239) are the owner's, not a row's.

## What the owner is asked first (the lead asks at S86's open; builds the rest meanwhile)
- **#152 (with #138)**: a ridge per measured arm for the Milky Way template (Reid et al. 2019's loci) is a change of
  the arm law — a pinned template holds the bar's angle only today. Yes (build it in M1, the law gains a per-arm
  pin for templates that carry loci) or no (#152 stays the disclosed check, ruled permanent at S88's close).
- **#209 with #142**: a floor on the drawn pitch — the per-piece draw p(1 + 0.56 z) and the disc's draw have no
  sourced floor; the owner orders one with a read source (the lead proposes a value from `READING_ARM_*.md`'s
  scatter at the open), or rules that a near-circular arc is what the sources' scatter means. A floor moves
  layer-on fields on the seeds it touches.

## S86–S88 — M1 (an Opus lead per session, Fable at the gates; two Opus builders on disjoint stages at most)
- **The list** (BUILD_V §2a, 25): #80, #81, #129, #130, #131, #138, #139, #141–#149, #152–#157, #186, #198, #209. The
  readers: `READING_ARM_MODES.md`, `READING_ARM_PIECES.md`, `READING_ARM_SEGMENTS.md`, `READING_BAR.md`,
  `RESEARCH_AREAS.md` beside them. Order: the law's items first (#138–#139 the arm number and the phases; #141, #143,
  #144; #142 the finite-thickness reduction with #209's floor), then the bar (#145–#149, #80), then the pieces
  (#152–#157), then the wire and the cuts (#81, #186, #198) and the gas response (#129–#131, derived with the forcing
  since D216). Each item: the entry's "what closes it" built or the entry re-ruled with the reason, the register line
  written, one commit.
- **The pin lifted for the batch**: every change under `model/galaxy` allowed; the stage's subset green at every commit
  (`tests/test_arms*.py`, `test_pattern*.py`, `test_bar*.py`, `test_pieces*.py` and what the entry names); the hash
  moves once, at S88's close (D3 as amended at D235): one re-export of the bundles, one model image and pin at the next
  deploy. The acceptance table's rows the batch touches (35, 37 and the arms' rows) re-read with their misses written
  in; `galaxy.specs` to its last row; the frames regenerated with the reason, the goal pictures beside them and the
  distance said plainly (the yardstick).
- **The full suite once, the owner's run, before the merge** (D246): at S88's close the lead commits, asks, and the
  owner starts `uv run pytest` backgrounded with its EXIT line to a file; the merge waits on that line, the nightly CI
  run on the merge is read at the open after. S86 and S87 close on the subset plus the fast gates, merged into
  `session-86`'s batch branch, not `main`; only S88 merges to `main` (tags s86–s88 at each close all the same).

## The gates and the close (each session)
- The subset at every commit; `npm --prefix frontend run test` / `typecheck` / `typecheck:e2e`; the picture test only
  where a frame is regenerated knowingly (the captures move with the model: re-taken with the reason and the sums);
  `tools/progress.py` and the docs tests (`test_docs`, `test_progress`, `test_audit`, `test_hook`, `test_graph`); the
  register's count pin and its pinned rows with every entry.
- D254… in `DECISIONS.md`; `LESSONS.md` tagged; `RESUMING.md` ≤ 120 lines; this file rewritten; `MANUAL_TODO.md`'s row.

## Traps (S72–S85's stand)
- Never run the full suite, `verify_clone` or the pins unprompted (D246). A fresh worktree needs `npm ci --prefix
  frontend`; `uv` makes its venv on the first run. The owner's servers on 8017 / 8018 / 5173; agents 8050+; the
  picture test's 8019 one builder's at a time. No backtick in a shell string; commit messages through a file; scripts
  through the Write tool (a Bash heredoc rewrites `\\n`). Builders: worktrees cut from the session's branch, one commit
  per item, no push, no DECISIONS; the lead cherry-picks and re-runs the gates. Two agents at once, one heavy, none
  heavy past 50 % of the 5-hour window. Read a suite's exit from pytest's own line, never from a pipe.
- A chrome change that moves a bar's height moves every capture (S84); a model change moves every layer-on field.
