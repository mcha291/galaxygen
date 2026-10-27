# BRIEF — after S71's close: the next agent session is S74, the gateway's review (row 74); then W4 (75), W5 (76)

**The state (2026-10-27).** The owner answered S73's five open items (D237): ruling 6 is entered (the bundles hold the
whole-galaxy scope alone, 202 entries, ~285 MB; nothing below 4 kpc; W5 measures the zoom step); **W3, the gateway,
is merged as built** from branch `worktree-session-70-gateway` (`gateway/`: `Caching.cs`, `GalaxyQuery.cs`, `Jobs.cs`,
`ModelClient.cs`, `Shares.cs`, `Program.cs`, 70 xunit tests against a stub model; `dotnet build -c Release` clean and
`dotnet test` 69 passed / 1 skipped before the merge; never run against the live model, never read against the plan);
the Milky Way now draws its clouds as extinction (F-4-1's display half; every Milky Way frame regenerated, D237's
table); the stray csproj edit is gone. Register 130 open = 11 + 119, 55 discharged; next number **#203**, decisions
from **D238**, board rows 74 / 75 / 76, acceptance rows from 38. The owner's word covers S74 ("schedule a review
session") and W4 after it ("do this afterwards"); the rationing rule holds (two agents, one heavy; `get_usage`
before each spawn).

## Build: S74 — the gateway's review (row 74; `BUILD_IV.md` §2c's table, §5 Phase W3's gate, Appendix A's D3 and D5)
- **Read it against the plan first** (an Opus reviewer blind to the builder's README, then the lead): the gateway
  runs no physics and holds no colour table; every cache key contains the model's hash (a test reads the key builder
  — `Caching.cs`; `ModelClient.cs` reads `/api/version`'s `model` hash or the pinned `Gateway:Model:ContentHash`:
  the key must use `model`, the hash of every byte of `model/galaxy` since S72, not `api` or `viewer`); the limiter's
  429 on the second concurrent generate and the queue serving it after; a share link round-trips its inputs (the
  query bound 16 KB — the viewer's full input vector with the merger prose is ~1.4 KB, a WFC3 render's filters ~20 KB:
  does a share carry filters? it should not); `/api/version` through the gateway equals the model's; a bundle hit
  passed through with its `X-Galaxy-Source: bundle` (the API answers it in 3 ms; `Cache-Control: no-store` from the
  API, the gateway's output cache keyed on the hash is its own decision, D3); D5's Appendix A sentence entered on the
  review's merge ("a gateway in front of the API is held to the same: it serves what the model published, keyed by
  the model's content hash, and computes nothing").
- **Then run it**: `dotnet run --project gateway/Galaxygen.Gateway` against `uv run python -m galaxy.api --port 8017
  --bundles <dir> --client frontend/dist` (export the bundles first: `uv run python tools/export_template.py --out
  <dir>`, ~100 s); the frontend's full flow through the gateway with no client change (`interface/transport.js`'s
  `ORIGIN` stays empty); the picture test cannot drive the gateway (it starts its own server on :8019) — a Playwright
  walk through the gateway's port, as S73's walker did (its spec and `logserve.py` are described in D236), with the
  gateway's logs showing the cache's hits and misses.
- **Fix what the review finds** in the same session (Opus builder), `dotnet test` and the Python suite green;
  `.github/workflows/dotnet.yml` runs on changes under `gateway/`. The Aspire app host needs Docker Desktop (the
  model container from the root `Dockerfile`, whose export step is unbuilt here) — W4's; say so if not run.
- **Gate:** every line of §5 Phase W3's gate measured or named as not met; D5's sentence in `RULES.md`; D238.

## What waits on the owner
- **#197** (the stars' and remnants' ring draws; a session of its own — explained in D237 §4) and **#202** (the
  diffuse dust share one number per level-0 ring: the circle at 4.72 kpc in every Milky Way frame; what closes it is
  the share continuous in R — a model-side change, no number, the frames regenerated). Their word on when; both
  before W4 if the deployed frames are to be the fixed ones.
- The Milky Way's frames moved (D237's table): the stars frame's colour reached the goal's, the dark fraction rose
  to 0.031 against the goal's 0.007 — the flecks are darker and more numerous than the goal's two lanes. The owner's
  look at the tuning panel decides whether the extinction strength slider (D228) comes down.

## Read
- `BUILD_IV.md` §2c, §5 (W3's gate), §7 (rulings 4, 5, 6, 12), Appendix A; D222, D235–D237; `gateway/README.md`
  (the configuration table); `RULES.md` D2–D5; `model/galaxy/api/http.py` (the headers), `bundle.py`.

## Traps (S72–S73's stand; see D235–D236)
- Every byte under `model/galaxy` is in the bundle's hash: a close that touches `model/` re-exports before the
  picture opt-in (`GALAXYGEN_PICTURE=1 GALAXY_BUNDLES=<dir> uv run pytest tests/test_picture.py`; :8019, one at a time).
- `tools/bootstrap.py` before the suite (~5 h with the pieces' gate; the pricing test flakes under load, green alone);
  pytest's exit code to a file; Bash under 8 KB; an agent worktree is cut from `main` (`git merge --ff-only
  session-NN` first); the register's two pins in `tests/test_audit.py` plus the carried and discharged rows in
  GALAXY_INPUTS.md §11; vitest and the picture test at every close that touches the frontend or a template; the
  owner's servers in their Terminal panel; a detached `verify_clone`'s log read before the session ends (S73's was
  green: 1 722 passed; S71's close's at `C:\Users\Semaphore\AppData\Local\Temp\galaxygen-verify-s71\verify_s71.log`).
