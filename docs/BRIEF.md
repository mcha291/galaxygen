# BRIEF — for S42's close: the owner's four answers and P6, built on Opus, awaiting Fable's rulings

**The state.** S40 (D190) and S41 (D191) are merged; the second build's last planned row is closed and its "done
means" met but for the tag batch's *record*. **S42 is already built** on `session-42` (head ea06bdf, pushed,
unmerged) by Opus 5.5 on 2026-09-27, **stacked on the pre-review `session-41` (beb278f)**; `docs/HANDOFF_S42.md`
holds it: (1) the FSPS/Byler nebular grid fetched (`tools/fetch_nebular.py` → `data/nebular_lines.npz`, pinned
commit) and four `hii_*_ratio` columns, per-ring lines, Hβ both layers, `/api/render` `lines_hii` / `lines_dig`;
(2) rows 32 and 34 on Audit III's blind windows (row 34 passes, its miss removed; #100 stays; specs 12/19/5);
(3) SVO WFC3 curves (`tools/fetch_filters.py` → `instruments.json`, sets `wfc3`, `wfc3n`) and an Airy sprite per
channel; (4) the tag batch run — 39 tags s00–s20, s22–s39 on the remote (verified 2026-09-30), `s06`'s literal SHA
in MANUAL_TODO had an extra digit (the tag points at a7148384433bb…); then a POST body for queries past 4 KB and
**P6 proposed**: `/api/blackbody` (193 T, log-share interpolation ≤ 2.2e-3) and stars/clusters drawn as L × share_k(T)
/ white_k through the chosen filter set instead of the ramp's hue. The four downloads were the owner's word in chat
(D184, D186, D188); the handoff quotes it — check that before ruling.

## What to do, in order
1. `git checkout session-42; git merge main`. **Expect conflicts**: `tests/test_v4.py` (S42 moves `hii_balmer_decrement`
   and the four ratios to DRAWN; S41 added the sentence assertions, the 25 / 38 count and a measurement test — keep
   both: the count becomes 30 / 37, and `nebular.NOT_DRAWN_WHY` must lose its `hii_balmer_decrement` entry or the
   DRAWN assertion fails); `model/galaxy/stages/nebular.py` (S41 inserted `NOT_DRAWN_WHY` above `_D4`; S42 added
   columns — new drawn columns need no entry); possibly `tests/test_audit.py`'s pins and the docs S41 rewrote.
2. Read the core diff against `main`, then rule (D192): the four answers as recorded, the grid's edge clamp (26 % of
   regions at +0.2 dex — recorded, unjudged; a candidate debt), the WFC3 PSF as a display choice, the POST path, and
   **P6** — D191 already says how it sits: P6 makes the point's hue follow the filter set (RENDER_PHYSICS §2a) but
   keeps the blackbody's bolometric correction, so it does **not** close #114 (the object's own band light does);
   the exposure ranking by bolometric L is a display choice to state. Do not record P6 as closing #114.
3. **The tag batch's record** (P4, D191 deferred it here): paste `git ls-remote --tags origin` under D161, mark every
   MANUAL_TODO row **applied** (correct `s06`), tick S22 ◐ → ☑ — GALAXY_PLAN §5d's last "done means" item.
4. Board row 42 (new row; `tools/progress.py` counts it — the bar becomes /43), model **Opus 5.5** built / Fable ruled;
   debts from **#117**; register pins in `test_audit.py` (`(59, 40)` now, the carried row ends `…, 114, 115, 116 | 48 |`);
   LESSONS; RESUMING (≤ 120) and this file for the maintainer; MANUAL_TODO `s41` = S41's merge SHA, `s42` TBD;
   delete HANDOFF_S42.md. Retire nothing else: RENDER_PHYSICS §0's `halpha_surface_brightness` went at S41.
5. Gate: `uv run python -m galaxy.specs` (expect **12 / 19 / 5 of 36**), vitest (S42: 16 files / 120 tests), and
   `uv run pytest -q` **backgrounded with its own EXIT= line** (~20 min; `test_s21b_the_catalogue_is_priced_per_cell…`
   is load-flaky — re-run alone if it is the only failure). Merge `--no-ff`, subject `Merge S42 into main: … (D192)`;
   push both; `uv run python tools/verify_clone.py --ref main` on a quiet machine.

## Traps
- Never force-push; never touch :5173; a scratch check uses `.claude/launch.json` "prod" (:8018, `npx vite build`
  first), stopped after; the canvas is black ~15–20 s on first load; each reload needs six "Confirm & lock" clicks.
  `uv run` only; LF newlines; the Bash tool fails over ~8 KB; `grep -c` exits 1 on zero; `git commit -F -` fails here.
- **Do not merge or delete** the sealed branches (MANUAL_TODO §2, `claude/blissful-poitras-2cbbd3`).
- #114–#116 (D191) stand in code by design: the cluster points paint bolometric light, the dissolved clusters are
  points, the sprite has no extent. S42's `colors.ts channelShare` touches the same painting — rule, do not rebuild.
- The WFC3 render sends ≈ 20 KB of curves; the POST path exists for the Azure ingress — a browser check of `wfc3`
  through the built `dist/` is the P3-style gate for it.
