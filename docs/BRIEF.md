# BRIEF — after S73: the bundles and their debts are done; W3 (row 71) is the owner's, W4 (row 74) waits on it; one ruling owed

**The state (2026-10-26).** S72 (D235) built BUILD_IV Phase W2, the template bundles: `tools/export_template.py`
computes every galaxy-scale answer the viewer asks of a template once and `galaxy.api.bundle` serves a matching
request from the file before any handler, byte-identical, under the hash of every byte of `model/galaxy`
(`/api/version`'s `model`; D3 amended). S73 (D236) closed its three debts on the owner's word: `/api/layer` publishes
the randomness layer's galaxy-wide tables once per galaxy and every render's header names it (the whole rgb header
124 → 27 KB, a windowed render 126 → 27 KB; the render no longer runs `gas_fluctuation`); a logged walk of the whole
viewer (171 request meanings) found the bundle plan right string for string, and `tests/test_bundle.py` now holds
both directions (every logged request planned; every planned entry logged but the four whole-disc remnants); every
request shape of #201's class answers 400 at the parse. The `Dockerfile` runs the export — **the image is not yet
built on this machine (W4's)**. Register 129 open = 11 + 118, 55 discharged; next number **#202**, decisions from
**D237**, board rows 71 (W3) / 74 (W4) / 75 (W5), acceptance rows from 38. **What follows needs the owner.** The
rationing rule holds (two agents, one heavy; `get_usage` before each spawn).

## What waits on the owner
- **Ruling 6, the levels and the size bound (D235's table).** The lead's recommendation: ship the whole-galaxy scope
  alone (202 entries, ~285 MB, ~100 s in the image build; the landing, the template switch, the star-first mode and
  the physics-only switch never run the model); leave every zoom below 4 kpc to the model (ruling 15 as it stands,
  W5 measuring the step); do not ship levels 0–1 (6.64 GB, 4.80 h to export; level 2 +22.6 GB, level 3 +89.9 GB).
  The alternatives are each a ruling: the model kept warm; a composing reader for the tiles (they compose; the
  header is the reader's work — D5-adjacent); the ring-first draw published for the viewer. `--levels` exists and
  plans single-cell tiles only; nothing is assumed.
- **W3, the gateway (row 71):** `gateway/` scaffolded; the features built by an agent on the owner's ask on branch
  `worktree-session-70-gateway` (09147c9: queue, share links, hash-keyed output cache, 17 tests), unmerged, no decision
  or board entry. The gateway should serve a bundle hit as the API does — or proxy it: the API answers a hit in 3 ms
  with `X-Galaxy-Source: bundle`, `Cache-Control: no-store` (what the gateway caches is its decision, keyed on
  `/api/version`'s `model` hash, D3). D5's Appendix A sentence enters at W3's merge. A stray uncommitted `v` sits at
  the end of `gateway/Galaxygen.AppHost/Galaxygen.AppHost.csproj` in the owner's working tree (invalid XML; not ours).
- **W4 (row 74, `BUILD_IV.md` §2d, §5):** two container apps, `Dockerfile.model` and `gateway/Dockerfile`, both
  images in `image.yml`, Bicep, `deploy.ps1`, the suspended environment recreated. Needs W3 merged. Its first step is
  `docker build` of today's `Dockerfile` (the export step is unbuilt here; `.dockerignore` re-includes the one tool).
- **#197** (the stars' and remnants' ring draws; a session of its own), **#195**, **F-4-1**: as before. Noted, not
  opened (D236): the windowed render's remaining 26 KB header (`components`, `clouds`' per-ring table, `ages`); the
  lax 200s (`set=junk`, `r_min > r_max`, `about: [1]`); `stages/spectra.py`'s `_finite` catching no `OverflowError`.

## Read
- `BUILD_IV.md` §2b–§2d, §5, §7 (ruling 6's answer paragraph and D235), Appendix A; D222, D235, D236; `RULES.md`
  D2–D5; `model/galaxy/api/bundle.py` (the format's one definition), `service.py` (`handle`'s hit path, `_version`,
  `_layer_tables`), `v7_layer.py`, `tools/export_template.py` (`plan()`, `--check`), `tests/test_bundle.py` (the
  fixture test in both directions), `tests/test_picture.py` (the `GALAXY_BUNDLES` opt-in).

## Traps learned at S72–S73
- **Every byte under `model/galaxy` is in the bundle's hash**, the server's entry point and its comments included: a
  close that touches `model/` re-exports before it re-runs the picture opt-in (`GALAXYGEN_PICTURE=1 GALAXY_BUNDLES=<dir>
  uv run pytest tests/test_picture.py`; one run at a time on :8019; the export ~100 s, `--check` ~100 s, the run ~4 min).
- **A body that records what the server did is not a function of the request**: the header's `stages` is the closure
  the answer needs; `X-Galaxy-Stages` says what ran. A new header field is asked whether two requests of one meaning
  could write it differently; a galaxy-wide table goes on a route of its own, never on a per-window answer.
- **Two loaders for one picture need a pairing rule** (`drawnPair`, `sameGalaxy` on model, template, layer, inputs):
  the first `/api/layer` build blanked the field between its answers; pins are not inputs.
- **A 500's fix is reviewed as the class** (negative seeds, booleans, a HEAD's body); a guard's test goes through the
  socket. **The gate's instruments are tested by the gate** (the e2e runner empties `frontend/e2e/.output` after the
  server starts; the picture wrapper counts the spec's tests from its output; vitest at every close that touches the
  frontend or a template). **An agent worktree is cut from `main`** (`git merge --ff-only session-NN` first; a second
  builder on the same files merges). Bash under 8 KB; pytest's exit code to a file; `tools/bootstrap.py` before the
  suite (the suite ~5 h with the pieces' gate test); the register's two pins in `tests/test_audit.py` plus the carried
  and discharged rows in GALAXY_INPUTS.md §11; the owner's servers in their Terminal panel; a detached
  `verify_clone`'s log read before the session ends (S72's at
  `C:\Users\Semaphore\AppData\Local\Temp\galaxygen-verify-s72\verify_s72.log`, S73's beside it as `-s73`).
