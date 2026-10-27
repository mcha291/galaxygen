# BRIEF — after S75: W4 prepared and verified in CI, nothing deployed (the subscription is disabled); next is the owner's deploy, then S76, Phase W5 (row 76)

**The state (2026-10-28).** S75 (D239) built the deployment and verified what a machine without Docker and a
subscription without write access could: `Dockerfile.model` (the API and its bundles, labelled with its `model.hash`)
and `gateway/Dockerfile` (the frontend and the gateway) are built, run and smoke-tested together in
`.github/workflows/image.yml` before the push (`infra/smoke.sh`: the bundles' hash the live hash, the landing's three
answers `X-Galaxy-Source: bundle` in 1 ms each, the pinned gateway's `miss` then `hit` with the model's log unchanged,
a wrong pin a 503), then pushed as `ghcr.io/mcha291/galaxygen-model:<short sha>` and `galaxygen-gateway:<short sha>`
(public; `latest` on main). `infra/main.bicep` has the two Container Apps in one Consumption environment (the gateway
external on 8080 with readiness on `/healthz`; the model internal on 8000 with readiness on `/api`, `--verbose`; both
0–1; 1 vCPU / 2 GiB and 0.5 / 1 GiB as `modelSize` / `gatewaySize`), Table `shares` + Blob `results` with a 30-day
lifecycle TTL, the gateway's env from `gateway/README.md`'s keys; `infra/deploy.ps1` reads the live subscription state,
the pin from the image's label, recreates the old environment only on `-Recreate` (or when its type cannot change),
and stops on a wrong `-ModelHash` unless `-Force`. `dotnet test` 107. Register 133 open = 11 + 122, 55 discharged;
next number **#206**, decisions from **D240**, board row 76 (W5), acceptance rows from 38. Zero-traffic cost ~$0 (D239).

## What waits on the owner (before any agent session can do W5)
- **The subscription** reads `Disabled` (a free trial at its spending limit; `az rest` on the subscription, not the
  CLI's cached `az account show`). Re-enable it in the portal (upgrade to pay-as-you-go), then from a checkout whose
  `image` run is green: `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha> -Recreate` — it deletes the
  old app `galaxygen` and `galaxygen-env` (the hostname changes), creates the environment, the storage account,
  `galaxygen-model` and `galaxygen`, and prints the URL. `-Preview` runs the same path read-only.
- **Rulings D239 asks for:** the sizes; the results TTL (30 days); the readiness probe on `/healthz` taking the one
  gateway replica out of rotation on a pin mismatch (a loud outage, against a gateway that stays up unpinned);
  **#205**'s remedy — a gateway at zero replicas starts with an empty cache, so the first visit after a quiet spell
  wakes the model for the landing (W5's eager warm, a Blob-backed output cache, or a warm gateway against ruling 9).
- The re-rulings of D238 stand (the proxied gate 1 / 64; jobs sharing the permit; a pin mismatch until restart);
  #197, #202, #203 / T20 each a session of its own.

## Build: S76 — Phase W5, smoothness measured (`BUILD_IV.md` §5 Phase W5, §7 ruling 10; row 76)
- **First, #204's three gate sentences on the deployed site** (the model's logs through
  `az containerapp logs show -n galaxygen-model -g galaxygen-rg --type console`, filtering the readiness probe's
  `GET /api` and `kube-probe`): the landing from the bundles with no model request *while the gateway is warm*; an
  edit (Generate) waking the model and returning through the proxy's gate (`X-Gateway-Cache: miss`, one at a time);
  a share link (`POST /share` by hand, since the viewer does not call it, #203) opened on another device.
- **The probe:** Playwright against the deployed URL — first paint, template switch (Milky Way ↔ NGC 4414), one zoom
  step below 4 kpc (the model wakes: ruling 15), cold (both apps at zero: wait past the idle cooldown, ~5 min) and
  warm, five runs each, a table with medians; the gateway's `/healthz` sampled for `in_flight` / `waiting`; the model's
  cold start (image pull + the bundle index's digest check, 0.27 s on this machine for 285 MB) measured on its own.
  Compare with ruling 10's bound: 1 s warm, 5 s cold.
- **Then whatever the table says is slow and the bound forbids** (§5 Phase W5): an eager warm of the gateway from the
  bundles' manifests at start (#205), a prefetch of the neighbouring level's cells, a smaller level-3 encoding, a CDN in
  front of the bundles; each measured before and after, in the decision. Nothing in `model/` moves (the pin).
- **Gate:** the table inside the bound, with the before numbers, in D240; the Python suite and `dotnet test` green.

## Read
- `BUILD_IV.md` §5 Phase W5, §7 rulings 9, 10, 15; D238, D239 (the cost table, the review's eleven findings);
  `gateway/README.md`; `infra/` (bicep, deploy.ps1, smoke.sh), `.github/workflows/image.yml`; the Azure memory file.

## Traps (S72–S75's stand; D235–D239)
- No Docker here: images build and run in CI only (`gh workflow run image.yml --ref <branch>`, `gh run watch`); the
  gateway is checked locally by `dotnet run` against `uv run python -m galaxy.api --port 8050`. Every byte under
  `model/galaxy` is in the hash: a change there is a new model image and a new pin, and the gateway's `/healthz` is
  503 until redeployed with it. `az account show` lies about a disabled subscription (read `az rest`).
- The owner's servers run in their Terminal panel on 8017 / 8018 / 5173; agents use 8050+ (the AppHost 8027).
- `tools/bootstrap.py` after the last agent worktree and before the suite (~6 h; the pricing test flakes under load,
  green alone); pytest's exit code to a file; Bash under 8 KB; agent worktrees are cut from `main` (`git merge
  --ff-only session-NN` first); the register's count pin in `tests/test_audit.py` moves with every entry; a detached
  `verify_clone`'s log is 0 bytes until it ends (block-buffered) — S75's at
  `C:\Users\Semaphore\AppData\Local\Temp\galaxygen-verify-s75\verify_s75.log`, read before the session ends.
