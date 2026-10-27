# BRIEF — after S74: the gateway is reviewed and fixed; the next agent session is S75, Phase W4, the deployment (row 75)

**The state (2026-10-27).** S74 (D238) read W3 against the plan and ran it against the live model: every cache was
keyed on `api` + `viewer` instead of `model.hash` and served stale physics after a model-only change; fixed with the
pin verified (`/healthz` 503 on a mismatch), the dead `/bundles` mount gone, `/api/version/` never cached, a
concurrency gate of 1 in flight / 64 queued on the proxied input-taking routes (hits never queue), no retries, share
parameters allowlisted and ids by shape, byte-bounded stores, `X-Gateway-Cache` on hits with `X-Galaxy-Stages`
empty, immutable `/assets`, a no-cache fallback, the 60/min window after the cache counting only model-bound
requests; 106 gateway tests; `gateway/README.md` rewritten to the code (read it: it is the gateway's own account).
D5's gateway sentence is in `RULES.md`. Register 131 open = 11 + 120, 55 discharged; next number **#204**, decisions
from **D239**, board rows 75 (W4) / 76 (W5), acceptance rows from 38. The owner's word of 2026-10-27 covers W4 ("do
this afterwards"); the rationing rule holds (two agents, one heavy; `get_usage` before each spawn).

## Build: S75 — Phase W4, the deployment (`BUILD_IV.md` §2d, §5 Phase W4, §7 rulings 8, 9; row 75)
- **Two images from CI:** `Dockerfile.model` (today's root `Dockerfile` less the frontend stage; it already runs
  `tools/export_template.py` into `/app/bundles` with `GALAXY_BUNDLES` set — **unbuilt on this machine so far: build it
  first, `docker build -f Dockerfile.model .`, and confirm `/api/version`'s `model` hash inside equals the bundles'
  and the landing is served from them**) and `gateway/Dockerfile` (the frontend build and the gateway; publish
  untrimmed as it is, trimming is a later step); both tagged with the short commit in `.github/workflows/image.yml`.
- **Bicep and `deploy.ps1`:** two Container Apps in one environment — the gateway with external ingress, the model
  with internal ingress only, both scale 0–1 (ruling 9: minimum replicas zero); Table and Blob Storage for the share
  links (the Blob container's lifecycle TTL — W4's, D238); the gateway's health probe on `/healthz` (it answers 503 on
  a pin mismatch — a probe reads it) and the model's on `/api`; `Gateway:Model:BaseUrl` the model app's internal
  FQDN; `Gateway:Model:ContentHash` pinned to the image's `model.hash` so a cache hit never wakes the model (the
  gateway verifies it at the first model contact); `Gateway:Limits:TrustForwardedFor` on behind the ingress; the
  suspended environment deleted and recreated by the first run (`infra/main.bicep`, the owner's `galaxygen-rg`).
- **Costs:** the month's projected cost at zero traffic written down from the Bicep's sizes (the free grant per
  subscription; a warm replica all month costs several times it).
- **Gate:** the deployed site serves the landing from the bundles with the model replica at zero (the model's logs
  show no request); an edit wakes the model and returns through the proxy's gate (the viewer does not use `/jobs`:
  #203); a share link opens on another device; `README.md` and `VIEWER_TASKS.md` T19 updated; `dotnet test` and the
  Python suite green. The owner runs `deploy.ps1` (their subscription, their credentials): an agent prepares and
  verifies locally, the owner deploys — say so in the decision.

## What waits on the owner
- **Re-rulings from D238** (standing unless they say otherwise): the proxied path's gate of 1 in flight / 64 queued
  (ruling 5's numbers were the jobs'); jobs sharing the model's permit; a pin mismatch lasting until restart.
- **#197** (the stars' and remnants' ring draws), **#202** (the diffuse share's per-ring step), **#203 / T20** (share
  links and the queue in the viewer): each a session of its own; #197 and #202 before W4 if the deployed frames are to
  be the fixed ones.

## Read
- `BUILD_IV.md` §2d, §5 Phase W4, §7 rulings 8–10; D222, D235, D238; `gateway/README.md`; `infra/main.bicep`,
  `infra/deploy.ps1`, `Dockerfile`, `gateway/Dockerfile`, `.github/workflows/image.yml` and `dotnet.yml`; the memory
  file on the Azure deploy (ghcr.io images, `galaxygen-rg`, the environment suspended since 2026-10-14).

## Traps (S72–S74's stand; D235–D238)
- Every byte under `model/galaxy` is in the bundle's and the gateway's hash: a close that touches `model/`
  re-exports before the picture opt-in; the gateway must be pointed at an API that publishes `model` (S72+).
- The owner's servers run in their Terminal panel on 8017 / 8018 / 5173; agents use 8050+ (the AppHost now 8027).
- `tools/bootstrap.py` before the suite (~6 h; the pricing test flakes under load, green alone); pytest's exit code
  to a file; Bash under 8 KB; an agent worktree is cut from `main` (`git merge --ff-only session-NN` first); the
  register's two pins in `tests/test_audit.py` plus the carried and discharged rows; vitest and the picture test at
  every close that touches the frontend or a template; a detached `verify_clone`'s log read before the session ends
  (S71's and S74's at `C:\Users\Semaphore\AppData\Local\Temp\galaxygen-verify-s7N\verify_s7N.log`).
