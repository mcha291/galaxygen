# BRIEF — for S41's close: V4, built on Opus, awaiting Fable's review (rows merge in order)

**The state.** S40 (V3) is merged (D190, 2026-09-30). **S41 is already built** on `session-41` by Opus 5.5 during
Fable's usage limit, **branched from the pre-review `session-40` and merged with its tip 3700cfc**; `session-42` is
stacked on `session-41` the same way. `docs/HANDOFF_S41.md` on `session-41` holds five rulings Opus *proposed and
wrote down before the build* (P1 clusters as points of light from two new columns `cluster_luminosity` and
`cluster_light_temperature`; P2 no named-instrument PSFs without the owner's download; P3 the model toggle's gate
is that both models draw both regimes; P4 the tag batch is the owner's; P5 the #69 gate extended to the object
classes: every `of="cloud" | "cluster" | "remnant"` column drawn or carrying the D4 sentence — 25 drawn, 39 not),
its commits, its gate run and what Fable owes. Nothing in it is a decision until D191 ratifies or overturns it.

## What to do, in order
1. `git checkout session-41`; read HANDOFF_S41.md, then the core diff **against `main`** (`clusters.py`'s two
   columns, `colors.lightColors`, `GalaxyTab.tsx`'s shared cluster load, `RegionVolume.tsx`'s 7 lines,
   `tests/test_v4.py`). `git merge main` into `session-41` first — S40's close commits (docs, `test_audit.py`'s
   register pins, `test_region_synthesis.py`'s sixty-window test, the deleted HANDOFF_S40) are not on it; the
   code will not conflict (S41 touched no doc S40 closed), `test_graph.py` may (S41 adds a line, S40 added one).
2. Rule on P1–P5 (D113: they were written before the numbers, by Opus; the ratification is yours). Review against
   BUILD_II's V4 gate: every published field of both models shown or ruled invisible (#69), both models draw,
   `verify_clone` OK. P1 is a real question: a cluster's light as a blackbody ramp of one temperature is what V1
   removed for the field (D188) — say why it is acceptable for a point, or send it to `/api/render`.
3. **D191**; debts from **#114** (the 39 undrawn object columns are one candidate; the register's carried row and
   `test_audit.py`'s pins move with them: now `(56, 40)` and `…, 110, 111, 112, 113 | 45 |`); board row 41
   (**Opus 5.5** built, Fable ruled); LESSONS; RESUMING (≤ 120) and this file for S42 — also built, on
   `session-42` (`HANDOFF_S42.md`: the FSPS nebular grid fetched? `tools/fetch_nebular.py`, `nebular_lines.npz`,
   `fetch_filters.py`, spec rows — **downloads were the owner's word (D184, D188): check the handoff says so**).
4. MANUAL_TODO: row `s40` takes S40's merge SHA (`git rev-list -1 --grep='^Merge S40 into main' main`), add `s41`
   TBD; the commands block likewise. Delete HANDOFF_S41.md in the close commit.
5. Gate: `uv run python -m galaxy.specs` (expect 11 / 20 / 5 of 36) and `uv run pytest -q` **backgrounded with
   its own EXIT= line** (~20 min; `test_s21b_the_catalogue_is_priced_per_cell_not_per_star` is flaky under load —
   re-run alone if it is the only failure). Merge `--no-ff` with subject `Merge S41 into main: … (D191)`; push both;
   `uv run python tools/verify_clone.py --ref main` on a quiet machine.

## Traps
- Never force-push; never touch :5173 (the owner watches it); a scratch check uses `.claude/launch.json` "prod"
  (:8018, `npx vite build` in frontend/ first) and is stopped after. `uv run` only; LF newlines; the Bash tool fails
  over ~8 KB; `grep -c` exits 1 on zero matches; `git commit -F -` fails here — use `-m` or a file.
- **Do not merge or delete** the sealed branches (MANUAL_TODO §2, `claude/blissful-poitras-2cbbd3`).
- S40's four stated departures (#110 the noise's shapes, #111 the display budget's dropped light, #112 the
  screen-space composite, #113 stars on the level-0 sample) were left in code because S41 was stacked; S41's
  cluster points at the census's Hα are #111's named closer — say in D191 whether V4 closes it.
- RENDER_PHYSICS §0 says `halpha_surface_brightness` (light's Σ_SFR × constant) is the close-out's to retire.
