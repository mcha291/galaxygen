# HANDOFF — S42: the owner's rulings of 2026-09-27, applied on Opus while Fable's limit resets

**Why this file exists.** After S40 and S41 were built on Opus (unmerged; their handoffs), the owner answered the four
questions the build had left for them, on 2026-09-27, in chat:

1. **The Byler/FSPS nebular grid (D184): download it.**
2. **Rows 32 and 34 (Audit III, A3-7, D186): follow the audit's recommendation** — both rows take the blind windows,
   their texts keeping the disclosure.
3. **The instrument filter curves (D188, #108): yes** — download them from the SVO Filter Profile Service.
4. **The tag batch: run it.**

and asked that the rulings on S40 and S41 wait for Fable. So this work sits on `session-42`, **stacked on the unmerged
`session-41`** (rows merge in order: S40, S41, then this), built on **Opus 5.5**, and it is not a board row yet: Fable adds
row 42 (or folds it) when it closes S40 and S41, writes the decision that records these rulings, and deletes this file.

## 1. Done: the tag batch (item 4)

Run from this desktop checkout on 2026-09-27; `main` equalled `origin/main` (8d8c894), so the batch's
`git reset --hard origin/main` was not needed and not run. The stale remote `s01` (an orphan pointing at the pre-rebuild
merge, D41) was deleted and re-tagged; 38 annotated tags `s01`–`s39` were created from MANUAL_TODO's commands and pushed.
**One command was wrong**: `s06`'s literal SHA read `a71483844338`, an extra `8` — no such object; the S6 merge on `main`
is `a7148384433bb3218027ea9966afdc19b41d12c3` (one match for `^Merge S6 into main`), and the tag points there.
`git ls-remote --tags origin` then listed **39 tags: s00–s20 and s22–s39** (no `s21` command exists in the batch: S21's
two audit branches were never merged, and S22's merge carries `s22`). What Fable still owes the record (MANUAL_TODO's own
"finish the record"): paste the listing under D161, mark every row applied (correcting `s06`'s SHA), and tick S22's board
row from ◐ to ☑ — GALAXY_PLAN §5d's last "done means" item is met.

## 2. Built on this branch (filled in as the work proceeds)
