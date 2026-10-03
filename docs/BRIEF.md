# BRIEF — for S54: BUILD_III's Phase T, the templates (an Opus lead; no Fable gate)

**The state (2026-10-03).** S53 is merged (D212): BUILD_III is adopted, its ten rulings recorded, the rules amended
(A10's fourth kind, A5, D1, D5, `RENDER_PHYSICS.md` §8), and Phase 0's two instruments built. No model code moved:
specs 12 / 20 / 5 of 37; register 69 open = 11 + 58, 45 discharged. Numbers from D213, #132, row 38, board row 54.
**Read `BUILD_III.md` §2, §3 and "Phase T" in §5: that text is the ruling you build to.**

## First
`uv run python tools/bootstrap.py`. S53's close ran the suite (`EXIT=0`) and `verify_clone` on `main`; a fresh
context can open with `uv run python tools/verify_clone.py --ref main --skip-worktree-checks`, backgrounded, while it reads.

## The order (BUILD_III §5, Phase T; §3e and §3f are the agents' briefs)
1. **One reader, before any model output for NGC 4414 exists** (blind, D113): its distance, inclination, position
   angle, rotation speed, stellar and gas mass, star formation rate, scale length, class and bar classification,
   each read on a fetched page with its coverage, **and a window for each of about eight properties**. Commit
   `docs/READING_NGC_4414.md` before anything is fitted. The lead then names which the fit sees and which five are checks.
2. **Builder A (model, API, fit):** `galaxy/templates.py` (two templates as data, every number tagged),
   `tools/fit_template.py` (a bounded search of the seven controls; the residuals table committed, none tuned away),
   `/api/templates` (metadata only, D4) and `template=` on every route that takes inputs, a `tools/timings.py` row.
3. **Builder B (viewer):** the landing on `milky_way`, the switcher with model-made thumbnails, the template's camera
   and filter set, "compare with a picture" (a file the user picks; none bundled, ruling 5); vitest on the switcher.
4. **The five checks** read on the layer-off model (today's model: no layer exists yet), in their own table beside
   the 37 rows, pass or miss with a debt (B5), never a refit. A capture of each template beside its goal.

**Gate:** `milky_way` reproduces today's defaults **bit for bit**; the fit's residuals published; the five checks
recorded; the timings row; vitest; the captures.

## What S53 left you
- `uv run python tools/goal_metrics.py IMAGE [--axis-ratio Q] --table` — six statistics of a picture at one standard
  scale; `--table-header` for the header. **Give `--axis-ratio 1` for a face-on picture.** Baseline table: D212.
- `npm --prefix frontend run picture` (compare) / `picture:update` (rewrite frames + `e2e/frames.json`): four
  captures of the default galaxy in `frontend/e2e/captures.json`, on its own server at **:8019**. Each entry has a
  `template` key, null today: **the spec refuses any other value until you teach it to choose a template.**
- **The inclined camera is a placeholder**: 59.2° is the goal picture's outline read as a thin disc, azimuth 0.
  Replace both with the template's sourced camera and regenerate.
- **The camera's projection is yours to settle with the template** (BUILD_III §2: distance and pixel scale): the
  viewer's 45° perspective puts an m = 1 of 0.09–0.11 into an inclined capture and cuts the near side. Hubble's
  view is parallel. A long lens or an orthographic camera is a display choice; say which and why in D213.

## Traps
- A template's seeds are the four that exist; `texture_seed` is Phase R's (S55). Pins are data a template *may*
  carry and no pin is built before P3/P4 (S58–S59): NGC 4414 will show a bar until then — record it, do not hide it.
- **Do not force NGC 4414's inputs** (BUILD_III §9): what seven controls cannot reach is a finding. A check that
  fails is a recorded miss; a window is fixed before the model's number exists and is never widened (B5).
- A stop condition (BUILD_III §3d) means a partial close and `docs/HANDOFF_S54.md`, not an improvised ruling.
- An Agent worktree is cut from `main`: commit the ruling first; the builder's first step is `git merge --ff-only
  session-54`. Worktrees rewrite `core.hooksPath`: run `tools/bootstrap.py` before the closing suite.
- `frontend/node_modules` in a worktree: `npm --prefix frontend ci`. In the main checkout use `npm install`, never
  `ci`, while the owner's dev server may be running. Never bind or stop :8017, :8018 or :5173.
- The committed frames belong to this machine's renderer (`frames.json`); a changed viewer default fails the
  picture test by design — regenerate with `picture:update` and say so in the decision.
- Scripts go in the scratchpad, never `$TMP` (a stray `numbers.py` there shadows the standard library).
- Editing the register or the board while the suite runs fails `test_progress` alone: regenerate with `tools/progress.py`.
- Python writes CRLF here: write with `newline="\n"`; a Bash command over 8 KB is cut.
