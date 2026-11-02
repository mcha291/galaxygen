# BRIEF — S84 (BUILD_V row 84): T17, the design system as designed — the tabs kept, the mockup's components ported

**The state (2026-11-02).** D252 took BUILD_V §6 rulings 2–6 on the owner's word ("Yes, all five"): the tabs stay as
they stand since V9 (Science / Galaxy with the edit panel), the mockup's components are ported onto them; #189 is
discharged (the reference client retired); the pin lifts per batch from S86; Audit VI at the end; the deploy whenever.
`session-84` is cut from `main` at 894e19b (S85's close) and carries D252 as its first commit. **The model's hash is
f1fbbb17eff3c1dc003abcd38117cb1f** (since S77); nothing under `model/galaxy` moves this session. Register **125 open =
33 + 92, 69 discharged**; next number **#212**, decisions from **D253**. The owner's own open rulings (#211 / T11 on
`s83-robust` aa0eec6, #210, S80's (a) and S81's Worker, the subscription) are not this session's; T11 stays held.

## What S84 builds (an Opus lead on `session-84`, Fable at the close; one Opus builder at most beside the lead)
- **The design record**: `docs/design/_ds/galaxy-design-system-…/readme.md` (the voice, the foundations), its `styles.css`
  and `tokens/` (already byte-identical to `frontend/src/styles/tokens`), `_ds_manifest.json` (the 21 components) and
  `_ds_bundle.js` (their source — the manifest's `components/…/*.jsx` paths exist only inside the bundle), the mockup
  `docs/design/Galaxygen.dc.html` with `support.js`, the brief `docs/design/uploads/DESIGN_BRIEF.md`, the screenshots.
- **The port**: the 20 unported components as React + CSS Modules under `frontend/src/ui/` beside `Button.tsx` (ported
  at S46, the pattern): Badge, Card, Dialog, IconButton, Tabs, Tag, Tooltip, DataTable, Meter, Readout, StarIcon (with
  SPRITE_URL, SPECTRAL_COLORS, CORES, MODIFIERS), StatusDot, Checkbox, Input, Select, Switch. Each one a typed
  component with the design's variants and states, the tokens' variables and no colour of its own; a vitest per
  component (render, variants, the accessible role/name, keyboard where the design has it).
- **Then the panels use them** where the built chrome has the same thing by hand: the view switch in `App.tsx`
  (Tabs), the edit panel / rail (`workflow/Workflow.tsx`: Input, Select, Switch, Checkbox, Badge, Tag, Readout, Meter,
  IconButton), the Galaxy view's tuning panel and legends (`galaxy/TuningPanel.tsx`, `FieldLegend.tsx`, `Exposure.tsx`:
  Readout, Meter, Switch, Select, Tooltip), the compare pane's chrome (`ComparePane.tsx`), the error boundary and
  confirmations (Dialog), tables in the Science tab's plots where a table is drawn (DataTable), the status line
  (StatusDot). The tab structure, the drawer / rail placement (`drawerLayout.ts`, 320 px, its test against both
  stylesheets), the landing, the Generate flow and every loader stay as they are — this is chrome, not behaviour.
- **The viewer's register items where the port touches the same chrome** (BUILD_V §2a: #111, #170, #177, #183, #185)
  and T16's four limits (the right pane's tuning at mount, its budget, the probes the last pane's, the drawer over its
  bar): take what the port reaches; leave a line in each entry for what it does not. Nothing in these moves a capture
  knowingly without the reason written.

## The gates (D245: a viewer session closes on the fast gates)
- `npm --prefix frontend run test`, `typecheck`, `typecheck:e2e`, `npm --prefix frontend run build`.
- The picture test: `GALAXYGEN_PICTURE=1 GALAXY_BUNDLES=C:\Users\Semaphore\AppData\Local\Temp\galaxygen-s78\bundles
  PYTHONIOENCODING=utf-8 uv run pytest -s -p no:cacheprovider tests/test_picture.py` — 14 passed and nine `picture:`
  verdict lines read, not `git status`. The captures are canvas reads of the Galaxy view with the drawer closed, so a
  port of chrome should leave every one "the committed picture, byte for byte" (`ngc_4414-zoom` is #210's: "not the
  committed picture's bytes" before this session already). Where a capture must change, `captures.json` says why, the
  frame is re-taken with the reason and the sums, and the close says so. No `fetch(` added (D2), no colour of the
  viewer's own, the probe quiet.
- `uv run python tools/progress.py` then `uv run pytest tests/test_docs.py tests/test_progress.py tests/test_audit.py
  tests/test_hook.py tests/test_graph.py`. `tests/test_viewer.py` pins the reference client as it is: untouched.

## The close (Fable; the lead hands back with the list below)
- D253 in `DECISIONS.md` (what was ported, what each panel took, the captures' verdicts, what the register items got);
  `VIEWER_TASKS.md` T17 struck with the facts; `LESSONS.md` tagged bullets; `RESUMING.md` ≤ 120 lines; this file
  rewritten for S86 (M1, on ruling 4: §2a's 25 items, `READING_ARM_*.md` / `READING_BAR.md`, #152 the owner's word
  first, the pin lifted for the batch, the full suite once at S88's close on the owner's run); `MANUAL_TODO.md` row 84.
- The merge `--no-ff` into `main`, the tag `s84` pushed at the close (no batches), the row's SHA in the commit after.

## Traps (S72–S85's stand)
- Never run the full suite, `verify_clone` or the pins unprompted (D246). A fresh worktree needs `npm ci --prefix
  frontend`; `uv` makes its venv on the first run. The owner's servers on 8017 / 8018 / 5173; agents 8050+; the picture
  test's 8019 one builder's at a time. No backtick in a shell string; commit messages through a file; scripts through
  the Write tool (a Bash heredoc rewrites `\\n`). One commit per item, no push from a builder, no DECISIONS from one.
- A half-applied edit blanks the owner's live canvas on 5173 — keep each file consistent per edit. The design's voice:
  sentence case, no emoji, no exclamation, numbers with units in mono; the magenta accent only on the actionable.
