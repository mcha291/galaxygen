# BRIEF — after S77 (and S79's #207): CI green again, the model's hash moved; next is the owner's deploy (a new image and pin) and the probe on the deployed site

**The state (2026-10-31).** S76 (D240) built W5's probe and ran it here (the subscription still `Disabled` by `az rest`):
`frontend/e2e/smooth/smooth.probe.ts` on its own config (`npm --prefix frontend run smooth`; `GALAXYGEN_URL`, `_RUNS`,
`_STATE`, `_OUT`, `_MODEL_URL`) and `tools/smoothness.py` (`--bundles DIR` stands the model with its bundles on :8050 and
the gateway pinned on :8060 and runs model-cold / gateway-cold / warm, five runs each, run 1 on its own row; `--url <site>`
runs one state against a deployed site). F1–F4 and the review's second pass (D240) brought the switch back, star-first and
zoom inside ruling 10's 1 s warm; the first paint (cold ≈ 7 s: the march program's compile; warm ≈ 4 s: the 9 MB render's
parse and the first raster), the switch to NGC 4414 warm (≈ 1.8 s) and the model-cold zoom (≈ 24 s: the galaxy computed
in a fresh process, F5) are over — T29. S77 (D241) made the `ci` workflow green (#206 discharged): the machine pins marked
`machine_pinned` and skipped under `CI`, `JSON_DEPTH_CAP` 64 at every parse, Python 3.14.4, the full suite on `main` /
nightly / dispatch with a fast job elsewhere. **The model's hash is f1fbbb17eff3c1dc003abcd38117cb1f** (was 4f0c8401…):
the next deploy builds a new model image and pins the gateway to it. S79 (D242, a side session, no row) read #207 on the
runner's draw and discharged it — the continuity test's hard ends by identity, its bound the taper's own rate — and opened
#208 (the per-piece pitch draw has no floor). Register 134 open = 11 + 123, 57 discharged; next
number **#209**, decisions from **D243**, board row 78 (none planned), acceptance rows from 38.

## What waits on the owner
- **The subscription and the deploy** (D239 (i)–(ii)): re-enable it in the portal, then from a checkout of `main` whose
  `image` run is green (`gh workflow run image.yml --ref main`; the images carry the new hash)
  `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha> -Recreate`; `/healthz` 200 says the pin matches.
- **Then the deployed run of the probe, the first thing after:** `uv run python tools/smoothness.py --url https://<site>`
  (the warm state; `--state replica-cold --runs 5` after the idle cooldown, ~5 min with both apps at zero, run 1 holding
  the replica's wake and the image pull); #204's three gate sentences through `az containerapp logs show -n galaxygen-model
  -g galaxygen-rg --type console` (filter the readiness probe's `GET /api` and `kube-probe`); the table appended to D240
  and #204 / #205 ruled on it.
- **Rulings:** F5, the model-cold zoom — an eager warm after the landing (wakes the replica on every visit, ruling 9), a
  warm replica (15 b, paid), or the ring-first draw published to the viewer (15 c); #205's remedy with it; D239's sizes,
  TTL and readiness probe; D241's two — CI's full suite off every branch push (D24 amended), and whether the pins get a
  per-platform capture; T29's order (the shader program first); T20; #197, #202, #203; #208 with #142 (a floor on the pitch).

## What an agent session can do without the deploy (each the owner's word)
- **T29, the landing inside the bound:** the march program smaller or shared (re-baselining `fieldFragment.s66.glsl`'s
  snapshot with the reason; the picture test byte for byte is the gate), the first raster in a Worker, F6's `precision=f4`
  render (the bundle plan's meanings and the frames to re-check). Measure with `tools/smoothness.py --bundles` before
  and after, the machine quiet (a run beside the suite is not comparable: S76's second pass).

## Read
- D240 (R1–R5, the tables, F1–F6, the review and its second pass), D241 (#206's rulings R1–R6); `BUILD_IV.md` §5 W5,
  §7 rulings 9, 10, 15; `gateway/README.md`; `smooth.probe.ts`'s header; `tools/smoothness.py`'s docstring; `ci.yml`'s head.

## Traps (S72–S77's stand)
- No Docker here (images build in CI); every byte under `model/galaxy` is in the hash — a change there is a new model
  image and pin; `az account show` lies, `az rest` tells. `CI=true` skips the `machine_pinned` cases: a green `ci` run
  says nothing about this machine's bits, which the close's own suite checks.
- The probe: "warm" is the browser's too (a cold number needs a fresh browser per run); the instrument's cost is stated
  beside the table (7 % duty cycle at 264 ms); rule D2's gate refuses a second `fetch(` in tracked JS/TS (ask through
  Playwright's request context); the model's stdout is block-buffered when piped (`PYTHONUNBUFFERED`); the gateway's dll
  runs from its publish directory; `/api/version` lines inside a step are the gateway's pin check.
- The owner's servers run in their Terminal panel on 8017 / 8018 / 5173; agents use 8050+ (the probe 8050 / 8060, 8051 /
  8061 when taken; the picture test 8019; the AppHost 8027). `tools/bootstrap.py` before the suite (~3–5 h; the pricing
  test flakes under load, green alone); pytest's exit code to a file; Bash under 8 KB; the register's count pin in
  `tests/test_audit.py` and its pinned carried row move with every entry.
