# BRIEF — after S80: #208's head start and shader checks in; next is the owner's deploy and the probe on the deployed site

**The state (2026-11-02).** S78 (D242) took T29: warm first paint 4.5 → 0.79 s, switch 1.7 → 0.85, cold 7.5 → 2.1–2.5,
the frames byte for byte; what it left is #208. S79 (D243, the #207 side session) read #207 on the runner's draw and
discharged it — the continuity test's hard ends by identity, its bound the taper's own rate — and opened #209 (the
per-piece pitch draw has no floor). S80 (D244) built #208's (a) and (c): the field's loads (the arrays, the whole
render, the layer's tables, the clouds' census) asked beside the star sample as soon as the shown query exists
(`fieldLoads.ts` names them once, `api.ts askAhead` hands each to the loader that asks the same key), and three's
`checkShaderErrors` off in a production build (`renderer.ts`, `SHADER_CHECKS = !import.meta.env.PROD`; 12 / 24 info-log
calls → 0 / 0). The request set and the frames are unchanged. Beside the suite the warm landing did not move (the
answers are not localhost's critical path; the compile and the mesh are) and the cold first paints ~0.6 s (quiet;
0.14–0.29 s beside the suite); (e) closed by measurement (the walk's 303 requests are the landing's own, pressed inside a settle); (b) the mesh and (d)
the switch's context carried. D245 / D246 (the owner's rulings): the close's gate is the change's; the six of 2026-11-02 accepted. **The model's hash is f1fbbb17eff3c1dc003abcd38117cb1f** (since S77): the next deploy
builds a new model image and pins the gateway to it. Register **135 open = 11 + 124, 57 discharged**; next number
**#210**, decisions from **D247**, board row 79 (none planned: the owner's choice).

## What waits on the owner
- **The subscription and the deploy** (D239 (i)–(ii)): re-enable it in the portal, then from a checkout of `main` whose
  `image` run is green (`gh workflow run image.yml --ref main`; the images carry the hash f1fbbb17…)
  `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short sha> -Recreate`; `/healthz` 200 says the pin matches.
- **Then the deployed run of the probe, the first thing after:** `uv run python tools/smoothness.py --url https://<site>`
  (the warm state; `--state replica-cold --runs 5` after the idle cooldown); #204's three gate sentences through
  `az containerapp logs show -n galaxygen-model -g galaxygen-rg --type console`; the table appended to D244 and
  #204 / #205 ruled on it. The wire now carries F4's compressed bytes, the field's loads start with the sample (S80).
- **Rulings:** S80's (a) kept on the lead's ruling, to confirm (D244); F5, the model-cold zoom (an eager warm after the
  landing, a warm replica, or the ring-first draw published — ruling 15); #208 (d), the Canvas kept across a switch
  (a fresh camera by design, D213 ruling 5); #209 with #142 (a floor on the drawn pitch); D241's two (CI's full suite
  off every branch push; per-platform pins — S78 marked two more cases, 21); T20; #197, #202, #203; whether a debt
  session takes a board row (S79 and S80 took none).

## What an agent session can do without the deploy (each the owner's word)
- **#208 (b), the mesh's build** (~0.35 s on the main thread, `planeTexture` / `clumpedLight`: a Worker or a split,
  measured with the probe quiet, the frames byte for byte); the blackbody table asked ahead with the sample (a fifth
  load, measured the same way).
- **The march's cost (T14):** `npm --prefix frontend run march` is the per-frame instrument (16–36 ms a re-march at 1024²).

## Read
- D244 (#208's a, c, e: as built, the gates, the numbers beside the suite and quiet), D245 (the close's gate), D243 (#207's reading, the sweep,
  #209), D242 (R1–R5, the profile, the tables of record, #208), D240 (the probe, F1–F6), D241 (#206's rulings);
  `BUILD_IV.md` §5 W5, §7 rulings 9, 10, 15; `fieldLoads.ts`'s and `renderer.ts`'s headers; `smooth.probe.ts`'s header;
  `tools/smoothness.py`'s docstring; `gateway/README.md`; `ci.yml`'s head.

## Traps (S72–S80's stand)
- No Docker here (images build in CI); every byte under `model/galaxy` is in the hash — a change there is a new model
  image and pin; a bundle at another hash is refused at startup (the bundles for the picture test and the probe:
  `GALAXY_BUNDLES=C:\Users\Semaphore\AppData\Local\Temp\galaxygen-s78\bundles`, 234 MB, at f1fbbb17). `az account show`
  lies, `az rest` tells. `CI=true` skips the `machine_pinned` cases (21): a green `ci` run says nothing about this
  machine's bits, which the close's own suite checks; the runner fleet is not one machine (S77's two cases, D242).
- The probe: "warm" is the browser's too (run 1 pays the program's ~0.8 s build); a number taken beside the suite is a
  different machine's — attribute it with its own instrument's medians, never run 1 (S80); the probe's own cost is
  stated beside the table (~10 % duty at 264 ms). The shader snapshot is `fieldFragment.s78.glsl`: a change to the march
  is a change to that file, made knowingly, with `npm run compile` read before and after. Rule D2's gate refuses a
  second `fetch(` in tracked JS/TS (ask through Playwright's request context).
- Two sessions open on one day claim their numbers in the shared notes at the open; the later merge renumbers on a
  fresh branch BEFORE main is merged in (S79: a `^208\. ` anchor misses the quoted test items). The owner's servers run
  in their Terminal panel on 8017 / 8018 / 5173; agents use 8050+ (the probe 8050 / 8060, the picture test 8019).
  The full suite (~3–5 h, `tools/bootstrap.py` first; the pricing test flakes under load, green alone; pytest's exit
  code to a file) only on the owner's word, asked where the model, a fixture or a pin changed; every session closes on
  the fast gates; CI's full suite nightly and on dispatch, every push the fast job (D245, D246). Bash under 8 KB; the register's count pin in `tests/test_audit.py` and its pinned carried row move with every
  entry. 74 `galaxygen-verify-*` folders (3.9 GB) and 59 agent worktrees under `.claude/worktrees` are the owner's to clear.
