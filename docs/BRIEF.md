# BRIEF — after S72: W2 is built; W3 (row 71) is the owner's and W4 (row 73) waits on it; one ruling owed

**The state (2026-10-26).** S72 is merged (D235): BUILD_IV Phase W2, the template bundles. `tools/export_template.py`
computes every galaxy-scale answer the viewer asks of a template once (198 entries, 285 MB, 101 s for both templates
and both layer settings) and `galaxy.api.bundle` serves a matching request from the file before any handler runs,
byte-identical (`--check` 198 / 198; the picture run 15 / 15 with the frames byte for byte, 234 of 253 `/api` answers
from the bundle), under the hash of every byte of `model/galaxy` (`/api/version`'s `model`; rule D3 amended). The
`Dockerfile` runs the export into `/app/bundles` — **the image is not yet built on this machine (W4's)**. Register
132 open = 11 + 121, 52 discharged; next number **#202**, decisions from **D236**, board rows 71 (W3) / 73 (W4),
acceptance rows from 38. The owner's word of 2026-10-26 ("start working on the next sessions, continuing until the
context is getting full") covered S72; **what follows needs theirs.** The rationing rule holds (two agents, one heavy;
`get_usage` before each spawn).

## What waits on the owner
- **Ruling 6, the levels and the size bound (D235's table).** The lead's recommendation: ship the whole-galaxy scope
  alone (285 MB; the landing, the template switch, the star-first mode and the physics-only switch never run the
  model); leave every zoom below 4 kpc to the model (ruling 15 as it stands, W5 measuring the step); do not ship
  levels 0–1 (6.64 GB, 4.80 h to export; level 2 +22.6 GB, level 3 +89.9 GB). The alternatives are each a ruling: the
  model kept warm; a composing reader for the tiles (they compose, the header is the reader's work — D5-adjacent); the
  ring-first draw published for the viewer. Nothing is assumed; `--levels` exists and plans single-cell tiles only.
- **W3, the gateway (row 71):** `gateway/` scaffolded; the features built by an agent on the owner's ask on branch
  `worktree-session-70-gateway` (09147c9: queue, share links, hash-keyed output cache, 17 tests), unmerged, no decision
  or board entry. The gateway should serve a bundle hit as the API does — or proxy it: the API answers a hit in 3 ms
  with `X-Galaxy-Source: bundle`, `Cache-Control: no-store` (what the gateway caches is its decision, keyed on
  `/api/version`'s `model` hash, D3). D5's Appendix A sentence enters at W3's merge. A stray uncommitted `v` sits at
  the end of `gateway/Galaxygen.AppHost/Galaxygen.AppHost.csproj` in the owner's working tree (invalid XML; not S72's).
- **W4 (row 73, `BUILD_IV.md` §2d, §5):** two container apps, `Dockerfile.model` and `gateway/Dockerfile`, both
  images in `image.yml`, Bicep, `deploy.ps1`, the suspended environment recreated. Needs W3 merged. Its first step is
  `docker build` of today's `Dockerfile` (the export step is unbuilt here; `.dockerignore` re-includes the one tool).
- **#197** (the stars' and remnants' ring draws; a session of its own), **#195**, **F-4-1**: as before.

## Sessions an agent could run meanwhile, if the owner says so (each a row to insert — their call, D219's rule)
- **#200:** a logged walk of the Science tab and each shipped set (`python -m galaxy.api --source-log`), the fixture
  `tests/fixtures/s72_viewer_requests.json` extended, the picture opt-in covering those captures.
- **#199:** the layer's tables published once per galaxy and the windowed render naming them by the hash (a wire
  change; `render: one region` 126 064 → ~300 B + the tables once); the viewer's RegionVolume reads them once.
- **#201:** the two 500s caught at the parse (a 400 with the reason), pinned in `tests/test_api.py`.

## Read
- `BUILD_IV.md` §2b–§2d, §5, §7 (ruling 6's answer paragraph and D235), Appendix A; D222, D235; `RULES.md` D2–D5;
  `model/galaxy/api/bundle.py` (the format's one definition), `service.py` (`handle`'s hit path, `_version`),
  `tools/export_template.py` (`plan()`, `--check`), `tests/test_bundle.py`, `tests/test_picture.py` (the opt-in).

## Traps learned at S72
- **Every byte under `model/galaxy` is in the bundle's hash**, the server's entry point and its comments included: a
  close that touches `model/` re-exports before it re-runs the picture opt-in (two re-exports in one session).
- **A body that records what the server did is not a function of the request**: the header's `stages` is the closure
  the answer needs; `X-Galaxy-Stages` says what ran. A new header field is asked whether two requests of one meaning
  could write it differently.
- **The viewer's spelling is JavaScript's** (`js_number`, `js_query` in `bundle.py`); the key is semantic so spelling
  only costs a miss; a body echoes the PARSED floats (the reviewer's measurement), not the raw strings.
- **The gate's instruments are tested by the gate:** the e2e runner empties `frontend/e2e/.output` after the server
  starts; the picture wrapper's "N passed" count was stale since S66; vitest's pin-lines expectation since S70 — run
  the whole file the gate runs, and run vitest at every close that touches the frontend or a template.
- Still standing: an agent worktree is cut from `main` (`git merge --ff-only session-NN` first); Bash under 8 KB;
  pytest's exit code to a file; one picture run at a time (:8019); `tools/bootstrap.py` before the suite; the register's
  two pins in `tests/test_audit.py` (the tuple and the carried row) plus the carried summary row in GALAXY_INPUTS.md
  §11; the owner's servers in their Terminal panel; a detached `verify_clone`'s log read before the session ends.
