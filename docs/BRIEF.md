# BRIEF — for S25: BUILD_II Phases 0 and 1

The second build starts here. Read `RULES.md` in full, then `RESUMING.md`, then
`BUILD_II.md` from its head through Phase 1 (its "Reconciled" table first — the plan was
written against a repository that no longer exists in three places), then `GALAXY_INPUTS.md`
§11's head and items 3, 23 and 26. `RENDER_PHYSICS.md` is not this session's. Branch
`session-25`; commit and push at every sub-deliverable (C2b); numbers sequential from
debt #80 and decision D173 — no reserved blocks.

## Phase 0 — rewrite A1, one commit, first
Replace A1 in `RULES.md` with the text in `BUILD_II.md` Phase 0 (the stage graph acyclic;
iteration inside a stage when termination is guaranteed in advance). Its present
`[verified: bench2.py §4]` cites a file the repository has never held — checked with
`git log --all -- '**/bench2.py'` — and the 8× is "8 iterations" assumed (GALAXY_INPUTS.md
§10's cost table). Then **re-rule debts #26 and #3**, both permanent on the clause that goes:
the question becomes whether the retained budget can be a root of a monotone function of
itself inside checkpoint 1, as the contraction is (`halo.py`, `contracted_halo`). Re-rule,
or record as re-opened; update the three-way map at §11's head. Gate: suite green,
`graph.py` untouched, `tests/test_docs.py` green.

## Phase 1 — the pattern ahead of sfh
`bar` and `pattern` (both in `pattern.py`) require `circular_velocity_resolved`, published by
`sfh` at checkpoint 3; swap both to `circular_velocity` (published by `disc`, checkpoint 1)
and `graph.py` reorders on its own. `chemistry_dtd` also reads the resolved curve and stays.
**Measure rows 15, 16, 17 before touching anything** (`uv run python -m galaxy.specs`; row 15
reads 4.88277 in [4.8, 5.2] today) and again after; both numbers into D-next. If row 15
leaves its window that is a recorded miss under B5 with `disc_dominance` named as the cause,
not a retune. Re-run determinism and convergence: the pattern's checkpoint moves, and
`pattern_seed`'s `checkpoint_hypothesis` (4) must still equal where `graph` binds it (S17's
rule), or it is the hypothesis that changes and the decision says why. Re-pin what moves.

Then **record the arm-number finding without acting on it**: `arm_multiplicity` is a seeded
draw of 2 or 4 with equal odds (`ARM_MULTIPLICITIES`, `rng("pattern_seed", "arms")`) — no 3,
no flocculent state, no dependence on `shear_rate` or `disc_dominance`, both of which the
stage reads. S26 decides it with the amplitudes (Phase 1b).

## Traps
- `arm_amplitude` and `bar_amplitude` are inputs (D171). Leave them this session; S26 removes them.
- Write files with `newline="\n"`; the full suite outlasts the tool's cap — background it with
  `EXIT=$?` on its log and gate the merge on that line (S17's and S14's trap).
- A recorded miss that starts passing fails the run (#29): remove the entry and write why.
- `progress.py` names S22 as "Next" while its tag batch is owed; that is by design. Tick your
  own row, run the tool, and leave S22's ◐ alone unless you ran the batch from this desktop.
- **Do not merge or delete** `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`,
  `session-21-a` or `claude/keen-lamport-lldlvp` (MANUAL_TODO §2).

## At close
Board row 25 ☑ with the model actually used; `uv run python tools/progress.py`; the suite;
D173 (Phase 0) and D174 (Phase 1) with the before/after rows; a `[close]`/`[field]` lesson if
one was learnt; RESUMING (≤ 120) and this file rewritten for **S26 (Phase 1b, Fable)**;
`MANUAL_TODO.md` row `s25` with `s24`'s SHA already filled; merge `--no-ff`, push,
`uv run python tools/verify_clone.py --ref main`.
