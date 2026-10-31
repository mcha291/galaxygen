# BRIEF — after S78: the landing inside ruling 10's bound where the client owns it; next is the owner's deploy and the probe on the deployed site

**The state (2026-10-31).** S78 (D242) took T29. The viewer's warm landing read 4.5 s against ruling 10's 1 s and a
first visit 7.3–7.7 s against 5; an Opus profile attributed it (the march program's 6.8 s link — Direct3D unrolling the
96-step loop; a clouds' raster built twice, the first at the wrong shape, its long task holding the render's body
unread; the raster's trig recomputed per texel; three loaders in a chain each waiting a 350 ms settle on mount; the
mesh summing age parts it then overwrote) and five frame-safe fixes followed, each measured: the step loop's bound and
its reciprocal uniforms (`fieldFragment.s78.glsl`; one program for every step count; the compile 6.8 → 0.8 s, the GPU
time per re-march unchanged), the raster gated on a census, a grid and a render of one run (`api.ts sameRun`), the trig
hoisted (bit-identical, the old loop kept in the test as the reference), a loader's first key asked at once (not the
view-keyed ones: the picture walk's request log found two drag-frame keys otherwise), the parts' sum skipped under the
clustered fill, and the raster in a Worker. **The tables of record are in D242**: warm first paint 4.53 → 0.79 s
(run 1 in a fresh browser 7.28 → 1.85), switch → NGC 4414 1.69 → 0.85, switch back 0.59, star-first 0.63,
zoom 0.52; model-cold first paint 7.49 → 2.13, gateway-cold 7.66 → 2.54; the model-cold zoom 24 s is F5, the
owner's. F6 (`precision=f4`) is closed by measurement: the render and the clouds already ask `f4`. Nothing drawn
changed (the picture test's 15 captures byte for byte); nothing under `model/galaxy` (the hash f1fbbb17… stands).
Register **135 open = 11 + 124, 56 discharged**; next number **#209**, decisions from **D243**, board row 79; the #207
session's branch `session-78-207` (its own D243 / #209 at its merge) awaits the owner.

## What waits on the owner
- **The subscription and the deploy** (D239 (i)–(ii)): re-enable it in the portal, then from a checkout of `main` whose
  `image` run is green (`gh workflow run image.yml --ref main`; the images carry the hash f1fbbb17…)
  `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha> -Recreate`; `/healthz` 200 says the pin matches.
- **Then the deployed run of the probe, the first thing after:** `uv run python tools/smoothness.py --url https://<site>`
  (the warm state; `--state replica-cold --runs 5` after the idle cooldown); #204's three gate sentences through
  `az containerapp logs show -n galaxygen-model -g galaxygen-rg --type console`; the table appended to D240 / D242 and
  #204 / #205 ruled on it. The deployed wire now carries F4's compressed bytes and the client's work is ~1 s.
- **Rulings:** F5, the model-cold zoom (24 s: an eager warm after the landing, a warm replica, or the ring-first draw
  published — ruling 15); #208 (D242: the landing's last tenths — the field's loads asked beside the sample, the switch's context kept, three's shader checks off in production, R3's extra requests on the walk); the #207 session's merge
  (`session-78-207`, its full `ci` run and the 400-seed sweep read first); D241's two (CI's full suite off every branch
  push; per-platform pins); T20; #197, #202, #203.

## What an agent session can do without the deploy (each the owner's word)
- **#208's remedies** (D242 names them with their estimated gains): the field's loads asked beside the star sample
  (`App.tsx` / `GalaxyTab.tsx`: ~0.3 s of the landing's chain), the Canvas kept across a template switch (`GalaxyView`'s
  `key` carries `epoch`: a new WebGL context, ~0.15 s — the camera is fresh by design, D213 ruling 5, so the frames may
  move: the owner's), three's `checkShaderErrors` off in production (~20 ms).
- **The march's cost (T14):** `npm --prefix frontend run march` is the per-frame instrument now (16–36 ms a re-march at 1024²).

## Read
- D242 (R1–R5, the profile, the compile table, the fixes' before / after, the tables of record, #208), D240 (the probe,
  F1–F6), D241 (#206's rulings); `BUILD_IV.md` §5 W5, §7 rulings 9, 10, 15; `frontend/e2e/compile/*.probe.ts`'s
  headers; `smooth.probe.ts`'s header; `tools/smoothness.py`'s docstring; `gateway/README.md`; `ci.yml`'s head.

## Traps (S72–S78's stand)
- No Docker here (images build in CI); every byte under `model/galaxy` is in the hash — a change there is a new model
  image and pin; a bundle at another hash is refused at startup (S78 re-exported: 150 s, 234 MB). `az account show`
  lies, `az rest` tells. `CI=true` skips the `machine_pinned` cases: a green `ci` run says nothing about this machine's
  bits, which the close's own suite checks.
- The probe: "warm" is the browser's too (run 1 pays the program's build — ~0.8 s now, not 6 s); a number taken beside
  the suite is a different machine's (S78: within 0.1 s on every step but the model-cold zoom); the probe's own cost is
  stated beside the table (~10 % duty at 264 ms; the ready instant a bracket of up to 0.26 s). The picture test's
  bundle variable is `GALAXY_BUNDLES` (not `GALAXYGEN_…`). The shader snapshot is `fieldFragment.s78.glsl`: a change to
  the march is a change to that file, made knowingly, with `npm run compile` read before and after.
- A single `gpu_ms` after a pause reads the GPU's clock state (5 vs 50 ms on one thumbnail); the march probe keeps the
  GPU busy. Rule D2's gate refuses a second `fetch(` in tracked JS/TS (ask through Playwright's request context).
- The owner's servers run in their Terminal panel on 8017 / 8018 / 5173; agents use 8050+ (the probe 8050 / 8060, the
  picture test 8019). `tools/bootstrap.py` before the suite (~3–5 h; the pricing test flakes under load, green alone);
  pytest's exit code to a file; Bash under 8 KB; the register's count pin in `tests/test_audit.py` and its pinned
  carried row move with every entry. Two sessions open on one day claim their numbers in the shared notes at the open.
