# BRIEF — after S76: W5 measured and fixed locally, the deployed run owed; next is the owner's deploy and the probe on the deployed site

**The state (2026-10-31).** S76 (D240) built W5's probe and ran it here because the subscription still reads
`Disabled` (`az rest`, not `az account show`): `frontend/e2e/smooth/smooth.probe.ts` on its own config
(`npm --prefix frontend run smooth`, `GALAXYGEN_URL`, `GALAXYGEN_RUNS`, `GALAXYGEN_STATE`, `GALAXYGEN_OUT`,
`GALAXYGEN_MODEL_URL`) and `tools/smoothness.py` (`--bundles DIR` stands the model with its bundles on :8050 and the
gateway pinned on :8060 and runs the states model-cold / gateway-cold / warm, five runs each; `--url <site>` runs the
warm state against a deployed site). The ready instant is the first still probe; every step records its split (the
`/api` wait against the client's own work), the longest request, `/healthz`, the main thread's long tasks. Fixes F1–F4
(D240) brought the switch back, star-first and zoom inside ruling 10's 1 s warm; the cold first paint (6.9 s: the
march program's ~5.8 s compile, a pinned GLSL), the warm first paint (4.25 s: the 9.3 MB render's parse, the first
clouds' raster) and the model-cold zoom (23 s: the galaxy computed in a fresh process, F5) are still over — T29 in
`VIEWER_TASKS.md`. The picture test's 15 captures byte for byte; vitest 457; `dotnet test` 109; the model's hash
4f0c8401… unchanged. Register 134 open = 11 + 123, 55 discharged; next number **#207**, decisions from **D241**, board
row 77 (none planned), acceptance rows from 38. **#206**: the `ci` workflow has failed on every push since 2026-10-03
(18 machine-bound pins, the deep-JSON 400's wording the stack size's, two numeric cases to read) and the specs have not
run on the runner since — a session of its own, the owner's call.

## What waits on the owner
- **The subscription and the deploy** (D239 (i)–(ii), unchanged): re-enable it in the portal, then from a checkout
  whose `image` run is green `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha> -Recreate`.
- **Then the deployed run of the probe, the first thing after:** `uv run python tools/smoothness.py --url https://<site>`
  (or `GALAXYGEN_URL=https://<site> npm --prefix frontend run smooth`) — the warm state; a cold run by hand after the
  idle cooldown (~5 min with both apps at zero), noting the replica's wake and the image pull; #204's three gate
  sentences through `az containerapp logs show -n galaxygen-model -g galaxygen-rg --type console` (filter the
  readiness probe's `GET /api` and `kube-probe`); the table appended to D240 and #204 / #205 ruled on it.
- **Rulings:** F5, the model-cold zoom — an eager warm of the model after the landing (wakes the replica on every
  visit, a cost under ruling 9), a warm replica (ruling 15 b, paid), or the ring-first draw published to the viewer
  (15 c); #205's remedy with it; D239's sizes, the 30-day TTL and the `/healthz` readiness probe on a pin mismatch;
  the re-rulings of D238 stand. #206's session; T29's order (the shader program first); T20; #197, #202, #203.

## What an agent session can do without the deploy (each the owner's word)
- **#206, CI green:** a `machine_pinned` marker skipped under `CI` for the eighteen (bit-exact by design, no tolerance);
  a depth cap at the parse so both platforms answer the same 400 (`model/galaxy/api`: a new hash and pin);
  `.python-version` to a patch; `test_gas_fluctuation`'s 2.3e-3 and `test_pieces`' midpoint step read; the four-hour
  suite off every push with a fast subset per push. The reader's logs: `C:\Users\SEMAPH~1\AppData\Local\Temp\claude\ci_reader\`.
- **T29, the landing inside the bound:** the march program smaller or shared (re-baselining `fieldFragment.s66.glsl`'s
  snapshot with the reason; the picture test byte for byte is the gate), the first raster in a Worker, F6's `precision=f4`
  render (the bundle plan's meanings and the frames to re-check). Measure each with `npm run smooth` before and after.

## Read
- D240 (the rulings R1–R5, the two tables, F1–F6, the CI finding); `BUILD_IV.md` §5 Phase W5, §7 rulings 9, 10, 15;
  `gateway/README.md`; `frontend/e2e/smooth/smooth.probe.ts`'s header; `tools/smoothness.py`'s docstring.

## Traps (S72–S76's stand)
- No Docker here (images build and run in CI: `gh workflow run image.yml --ref <branch>`); every byte under
  `model/galaxy` is in the hash — a change there is a new model image and pin; `az account show` lies.
- The probe: "warm" is the browser's too (Chromium keeps compiled programs across contexts of one browser — a cold
  number needs a fresh browser per run, which `tools/smoothness.py` gives); the instrument's own quiet wait is not the
  user's; rule D2's gate refuses a second `fetch(` in any tracked JS/TS, e2e included (ask through Playwright's
  request context); the model's stdout is block-buffered when piped (`PYTHONUNBUFFERED`); the gateway's dll runs from
  its publish directory (the content root is the cwd); `/api/version` lines inside a step are the gateway's pin check.
- The owner's servers run in their Terminal panel on 8017 / 8018 / 5173; agents use 8050+ (the probe 8050 / 8060,
  8051 / 8061 when taken; the picture test 8019; the AppHost 8027). `tools/bootstrap.py` before the suite (~3–6 h; the
  pricing test flakes under load, green alone); pytest's exit code to a file; Bash under 8 KB; the register's count pin
  in `tests/test_audit.py` and its pinned carried row move with every entry (S75's #204–#205 had missed the row).
