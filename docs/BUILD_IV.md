# BUILD_IV — the fourth build: a galaxy at once, pregenerated templates, and a .NET gateway

**Status: ADOPTED 2026-10-14 (the owner: "adopt the plan with your recommendations except for 12, scaffold the
project for me"); recorded as D222.** Written the same day on the owner's word ("please create a plan to implement
this") and, on the owner's question whether it could keep to deployment alone, split before adoption: **this build
is W2–W5, deployment only**. **W2 built at S72 (D235, 2026-10-26): `tools/export_template.py`, the reader in
`galaxy.api.bundle` under the model's hash, the whole-galaxy scope (ruling 6's levels await the owner's ruling on the
probe's table in D235; nothing below 4 kpc is bundled); W3 remains the owner's.** The edit panel (W1) is BUILD_III's Phase V9 (S68) and the zoomed-in point layer is its
Phase V6b (S65). Every §7 recommendation was adopted except 12, where the owner's word is: an agent scaffolds the
gateway, the features are the owner's. The scaffold is in `gateway/` (D222). Board rows: **W3 S70 (in parallel
from adoption), W2 S71, W4 S72, W5 S73.** Everything here is `[inferred]` design unless tagged. Numbers quoted
from the repository are tagged where they were read.

---

## 0. What this build is for

**The owner's direction (2026-10-14), in their words.** "Move away from the staged generation … instead of going
through generation step by step with locks and stuff, I want to refactor the project so that it produces a galaxy
right away. If a user wants it they can then enable edits and change the variables, which should still be grouped
for convenience but use whatever makes sense instead of strictly enforcing a sequential process. The emphasis is
now on generating a realistic galaxy and creating good looking renders from it, including when zoomed in. This also
means having some pregenerated galaxies as templates. The web deployment should have the templates cached so that
users can switch between templates and zoom in or out reasonably smoothly. If they edit the templates it is okay for
generation to take a while." And on the gateway: a .NET service in front of the Python model, no accounts, with
limits and share links, as a project to get modern .NET experience in.

**Three deliverables, in the order they pay off** (the first is BUILD_III's since adoption; it is kept here
because the owner's direction names it, and §2a says where it went).

1. **A generate-first viewer.** The page shows a finished galaxy. Editing is opt-in, the controls are grouped for
   reading, any control can be changed at any time, and one action regenerates. No locks, no sequence, no
   invalidation of "later" stages shown to the user. **Moved to BUILD_III as Phase V9 (S68) at adoption.**
2. **Pregenerated templates.** Each template's every published answer is computed once at build time and shipped
   as files, so switching templates and zooming never runs the model. The model runs only for an edited galaxy.
3. **A .NET gateway** that serves the frontend and the template bundles, proxies edits to the model, and owns the
   features that are about users rather than physics: limits, a queue for edits, share links, caching.

**What this build does not do.** It does not change the model's physics, its stage order, its acceptance table or
its numbers. The realism of the galaxy and the look of the renders, at galaxy scale and zoomed in, remain
BUILD_III's V5–V8 (the light by age, the censuses at galaxy scale, the layer in the shader, the display defaults)
and Audit V. This build makes what those phases draw arrive at once, and makes a deployment that stays up.

---

## 1. Where the repository stands (read 2026-10-14)

**The viewer already lands on a generated galaxy.** Since S46 (D198) the React viewer confirms every checkpoint at
the template's inputs on load and shows the Galaxy view; since S54 (D213) a switcher selects `milky_way` or
`ngc_4414`. "Edit galaxy" opens the staged process `[verified: frontend/src/workflow/useWorkflow.ts, landOn;
docs/DECISIONS.md D198, D213]`. So what the direction removes is not the landing but **the semantics behind
"Edit galaxy"**: rule D1's locks, "reopening a stage discards every later one", the rail's locked / editing / next /
blocked states (`frontend/src/workflow/logic.ts statusOf`), and the state machine both clients share,
`interface/flow.js`, pinned by `tests/test_viewer.py` and `tests/js/flow.test.mjs` `[verified: those files]`.

**The model has no concept of a lock.** A run is a function of the inputs, the template, the seeds and the layer
switch; `run(..., resume=…)` reruns only the difference from a cached galaxy and the service keeps two galaxies in
memory (`Service.cache_size`) `[verified: model/galaxy/api/service.py ~804–974]`. Checkpoints exist in the
registry as the grouping of inputs by the earliest stage they reach (`graph.py`), which is exactly the grouping
"for convenience" the owner asks to keep. Nothing in `model/` changes for deliverable 1.

**Every template answer is a pure function of (template, layer, route, query).** The service's routes:
`/api/version`, `/api/stages`, `/api/fields`, `/api/inputs`, `/api/templates`, `/api/arrays`, `/api/region`,
`/api/system`, `/api/clouds`, `/api/clusters`, `/api/remnants`, `/api/bright`, `/api/blackbody`, `/api/render`
`[verified: service.py routes()]`. Per-cell censuses are cached between requests in `CellCache` and `BrightCache`;
the catalogue at a million stars takes ~25 s cold with the layer on, a whole-disc census route ~5.7 s, the field
~3 s `[verified: docs/RESUMING.md, docs/GALAXY_PLAN.md row 60]`. On a 0.5 vCPU replica these are the numbers a
user waits for today on every template switch after a cold start, and the reason the direction asks for caching.

**The deployment is one container and is down.** The Bicep runs one Container App (0.5 vCPU, 1 GiB, scale 0–1)
from a public ghcr.io image, with a capped Log Analytics workspace, in `galaxygen-rg` `[verified: infra/main.bicep]`.
On 2026-10-14 the managed environment reports itself suspended for a disabled subscription, the app's provisioning
state is Failed, the public URL does not answer, and the last rollout was image `d60f1ee` on 2026-09-25 — before
every session from S25 on `[verified: az queries of 2026-10-14, recorded in this session's transcript; not in the
repository]`. Deliverable 3's deployment phase recreates it.

**The client's transport is one file.** Rule D2: exactly one `fetch`, in `interface/transport.js`, same-origin by
default (`ORIGIN = ""`, `BASE = "/api"`) `[verified: interface/transport.js]`. A gateway on the same origin needs no
client change at all.

---

## 2. The design

### 2a. The generate-first viewer (Phase W1 — moved to BUILD_III as Phase V9 at adoption; the design below is its text)

- **Landing is unchanged**: the Galaxy view of the default template, the switcher beside it.
- **"Edit galaxy" opens a control panel, not a rail.** Inputs are shown in their registry groups, named as the
  checkpoints are today (Halo & disc; Assembly; Star formation & chemistry; Pattern; Systems; Planets) because that
  grouping is derived from the stage graph and reads well; the groups carry no order. Every control is enabled at
  all times. Seeds appear as reroll buttons inside their group. The merger list keeps its timeline editor.
- **One "Generate" action**, enabled when any value differs from the shown galaxy; a dirty marker per group says
  which groups changed. Generation runs the whole model for the new inputs (the model's own `resume` reuses what is
  unchanged, invisibly). While it runs the previous galaxy stays on screen with a progress indicator; the API's
  cost is the owner's accepted wait.
- **"Reset to template"** returns the panel to the template's inputs. A template's pins stay pins (A5): a pinned
  value is shown as read-only with its source, as today.
- **The checkpoint previews survive as a "Science" tab**: every published field previewed, as D1 always required,
  reached without reopening anything. T18 (view a locked checkpoint without reopening) is discharged by
  construction.
- **The reference client in `interface/`** is the API's own demonstration of the staged flow and is pinned by
  `tests/test_viewer.py`. Two options, ruling 2 in §7: (a) retire its workflow with D1's locks, keeping it as a
  plain demonstration of the routes; (b) keep it as a historical demonstration behind a flag. The shared
  `flow.js` becomes the React panel's state only if (a).

**Rule D1 is amended** (Appendix A). Its first sentence, "A lock means do not re-roll this", and its lock and
reopen semantics are retired; the landing clause, the switcher and "Edit galaxy" stay; a new sentence says that
every input is editable at any time and a galaxy is regenerated whole. The reason the rule exists — the viewer
must not show a galaxy that is half one input set and half another — is kept as the new wording's justification.

### 2b. Pregenerated template bundles (Phase W2)

- **An export tool, `tools/export_template.py`**, runs the model once per template and writes a bundle: every
  metadata route's JSON; every published array; `/api/render` for each shipped filter set at the default white
  point; the censuses (`clouds`, `clusters`, `remnants`, `bright` at the viewer's levels); `/api/region` for every
  cell at every level the viewer can reach; the content hash the bundle was built from. The bundle's manifest
  lists each entry with its route, query and byte size.
- **The service answers from a bundle when one matches.** A request whose template, layer switch and query equal a
  bundle entry, under the same content hash, is served from the file; anything else falls through to the model as
  today. The read is byte-identical to the computation — the gate asserts it on every entry — so nothing the
  viewer sees depends on which path answered.
- **Bundles are built in CI** as a stage of the image build, so a template's bundle can never be older than the
  model that serves it: the hash check is the guard and a mismatch is an error, not a fallback.
- **The scope and the size bound are the owner's** (ruling 6): which filter sets, which levels, whether the whole
  disc's level-3 cells ship or only to level 2 with level 3 computed on demand. The phase measures the bundle
  before the ruling is final and reports the table.
- **A shared edited galaxy is bundled on first generation** (Phase W3's share links): the gateway stores the result
  under the share id with the hash, so a shared link opens as a template does.

This phase touches `model/galaxy/api/` (the bundle reader) and `tools/`; no stage, no field, no number.

### 2c. The .NET gateway (Phase W3)

A new top-level project, `gateway/`, ASP.NET Core minimal API on .NET 10 (the current LTS), with its own tests.
The model's numpy-only rule is a rule about `model/`; the gateway is a separate toolchain beside the frontend's
Node, and the CI matrix gains a `dotnet` job.

| Feature | Design | What it teaches |
|---|---|---|
| **Serving** | The built frontend and the template bundles as static files with long cache headers keyed by the content hash; `/api/version` passed through from the model so rule D3 holds at the new boundary | Static files, response caching, ETags |
| **Proxying** | YARP forwards `/api/*` that no bundle answers to the model container; timeouts sized to the longest route (the million-star catalogue, ~25 s on 0.5 vCPU; ruling 5 may bound it) | YARP, HttpClient resilience |
| **Limits** | Built-in rate limiting: a sliding window per client IP on every route; a concurrency limiter on the generate route of one in flight, the rest queued — one model replica runs one expensive job at a time | `Microsoft.AspNetCore.RateLimiting`, partitioned limiters |
| **The edit queue** | A generate request returns a job id at once; a `BackgroundService` consumes a `Channel<Job>`, runs the model, stores the result; the client polls `/jobs/{id}` or reads a server-sent stream | Hosted services, channels, cancellation, `IAsyncEnumerable` |
| **Share links** | A galaxy is its template name, its inputs and its seeds: a few hundred bytes. A share link is a short id over that record in Azure Table Storage (free-tier friendly), with the generated bundle beside it in Blob Storage so the link opens warm. No accounts: a link is a capability, and a limit per IP on creating them | Azure.Data.Tables, Azure.Storage.Blobs, minimal-API route groups |
| **Caching** | Output caching on template routes; the edited-galaxy cache keyed by share id plus the model's content hash, so a redeploy invalidates what it should and nothing else | Output caching middleware, cache keys |
| **Around it** | .NET Aspire to run the gateway, the model container and the storage emulator together locally; OpenTelemetry to Log Analytics; a trimmed `dotnet publish` image so the replica wakes fast | Aspire, OpenTelemetry, container publishing |

**What the gateway may not do.** Run physics, hold a colour table, or cache by any key that omits the content
hash. Rules D2–D5 are restated at the boundary in Appendix A.

### 2d. The deployment (Phase W4)

- **Two container apps in one environment**: the gateway with external ingress, the model with internal ingress
  only, both scaled 0–1. The free grant is per subscription and a warm replica all month costs several times it, so
  minimum replicas stay zero (ruling 9). Table and Blob Storage for share links.
- **Two images from CI**: `Dockerfile.model` (today's, less the frontend stage) and `gateway/Dockerfile` (the
  frontend build and the gateway); both tagged with the short commit. The bundles are built into the gateway's
  image by the export tool run against the model image at build time.
- **`infra/main.bicep` and `deploy.ps1`** gain the second app, the storage and the two image parameters; the
  suspended environment is deleted and recreated by the first run.
- **Smoothness is measured on the deployed site** (Phase W5): time to switch templates, time to the next zoom
  level, cold and warm, with the numbers in the decision. The bound is the owner's (ruling 10).

---

## 3. Rules touched

| Rule | Today | After this build |
|---|---|---|
| **D1** | Locks, reopen-discards-later, the landing on the default template, the switcher, "Edit galaxy" | Landing, switcher and "Edit galaxy" kept; locks and the sequence retired; every input editable, regeneration whole (Appendix A) |
| **D2** | One `fetch` in the client transport | Unchanged; the gateway is same-origin, so `ORIGIN` stays empty |
| **D3** | The API publishes a content hash | The gateway passes it through and keys every cache on it |
| **D4** | No endpoint runs more pipeline than its answer needs | Unchanged for the model; a bundle hit runs none |
| **D5** | The viewer computes no physics | Extended: neither does the gateway |
| **A5** | Templates are named input sets with the defaults' standing | Unchanged; "pregenerated" is a property of the deployment, not of the template |
| **C-rules** | One toolchain under test: uv and Node | A third, `dotnet`, with its own test job; the close ritual runs it |
| BUILD_III §7 ruling 10 | The runtime stays numpy-only | Unchanged for `model/`; the gateway is outside it |

---

## 4. Where it sits against BUILD_III

S62 (L2) is in progress; S63–S66 are the viewer phases V5–V8 and S67 is Audit V `[verified: docs/BUILD_III.md
§6]`. The owner ruled on 2026-10-05 "don't reorder the sessions" for that build. This build's phases depend on it
unevenly:

- **W1 (the viewer flow) is independent of every remaining row**: it changes the edit panel and the reference
  client, nothing the V phases draw. It can run before or between them.
- **W2 (bundles) should run after V6 and V7**, because a bundle holds what the viewer draws and those two phases
  change what the viewer asks for at galaxy scale and in the shader. Built earlier, every bundle is rebuilt twice.
- **W3 (the gateway) is independent of the model entirely** and is the owner's own learning project: it can start
  at once, in parallel, against today's API, and gain the bundle routes when W2 lands.
- **W4 and W5 (deployment, smoothness) close the build** and need W2 and W3.

The recommended order is therefore: **W3 now, in parallel with S62–S66 on its own branch; W1 at the first gap the
owner chooses; W2, W4, W5 after S66 and before or after Audit V (ruling 1).** A deploy of today's `main` to a
recreated environment is a one-line action that does not wait for any of this (§1).

### 4b. Compatibility with BUILD_III's remaining rows, checked 2026-10-14

Read against the texts of V5–V8 and Audit V (`BUILD_III.md` §5, §6, §8, §9) `[verified: those sections]`.

- **Nothing in V5–V8 or Audit V reads the staged flow.** No phase names a checkpoint, a lock, a reopen or
  `flow.js`; V8's display defaults live in the tuning panel on the Galaxy tab, which W1 does not touch; the picture
  test captures the landing, which W1 keeps. The only text that mentions the staged process is BUILD_III's
  Appendix A, quoting D1 as amended at S53 — history after W1, and BUILD_III §2's "Edit galaxy starts from the
  template's inputs" stays true. **W1 needs no change to BUILD_III**; D212's Appendix A text is superseded by this
  build's Appendix A and says so.
- **V7 is bundle-safe by construction.** The viewer evaluates the published noise with the published seed and
  parameters and matches committed vectors (BUILD_III §9: "do not put the layer's noise in the viewer's own
  code"), so a bundle carries parameters, not pixels; the "physics only" switch is the `layer=off` bundle. No change.
- **V6 needs one constraint added so W2 can bundle it.** V6's new answers (clouds as extinction "by window and
  level", HII knots, bright stars "by tiles", T28's "windowed request") must be **keyed by cell and level on the
  wire**, as `/api/region`, `/api/clouds` and `/api/bright` already are (`cells_in(... level=)`,
  `BrightCache.fetch(... cells ...)`) `[verified: service.py ~1197–1218, ~489]`, with any window resolved to cells
  before the route and any rasterisation done in the viewer. A window-keyed route cannot be precomputed. This is one
  sentence in BUILD_III's V6 text, to be entered when ruling 1 is given; the lead of S64 reads it before the build.
- **Zoomed-in smoothness has a cost V phases do not pay and this build must measure.** The zoom regimes hand over
  by view width (`regimes.ts`) and a region below 4 kpc asks for the level-k cells its window meets, to `MAX_CHILD_
  CELLS` per request `[verified: service.py ~1209–1211; regimes.ts ~316]`. A level-k cell holds its parent's stars
  plus 4^k the density, so the whole disc at level 3 is of order sixty times the million-star catalogue and cannot
  ship as a bundle; and since L1 every census is drawn ring-first, so a single cell's draw costs its whole ring at
  that level (#159). **So a template's deepest zoom will wake the model unless the probe says otherwise.** W2's
  probe measures a level-2 and a level-3 window cold and warm, and ruling 6's recommendation is corrected to:
  levels 0–1 whole, level 2 as the probe allows, level 3 on demand — with W5's bound stated separately for a
  zoom step that crosses to level 3. The alternatives, each a ruling: keep the model replica warm (paid), or make
  the ring-first draw a published function the viewer may evaluate (D5 as amended at S53 permits it; the drawn
  objects are then the viewer's work and the API's own catalogue is the test vector). Neither is assumed.
- **A gap in "including when zoomed in".** BUILD_III's viewer phases face the galaxy-scale picture (V6: "the
  censuses at whole-galaxy scale"); the region regime below 4 kpc has V3's cloud interiors, V4's cluster points,
  L1's clustering and will get V7's per-pixel layer. What no phase schedules is **T4, the level-k stars as the
  point layer below 1 kpc** (`VIEWER_TASKS.md` §2; not in BUILD_III §8's exclusion list either) — today the
  points at the deepest zoom are the level-0 sample and the bright catalogue, which thin out as the view narrows.
  If the owner's emphasis on the zoomed-in render is to be met, T4 belongs in V6 or in a short V6b, and its cell-
  keyed route belongs in W2's bundles at the levels that ship. Ruling 13 (§7).

---

## 5. The phases

Each phase is one board row, one `session-NN` branch, one `--no-ff` merge and a tag (C2e); numbers continue from
the board's last row at the time of adoption. **Probe before build** (BUILD_II's rule) in W2 and W5, where the
numbers decide the design.

### Phase W1 — the generate-first viewer (BUILD_III Phase V9, S68, since adoption; the text below is what moved)

**Build.** The React workflow panel replaced by the grouped control panel of §2a with Generate, Reset to template
and per-group dirty markers; seeds as rerolls; pins read-only with their source; the Science tab for previews;
`useWorkflow` reduced to values, the shown galaxy's query, and the generate action; `interface/flow.js` and the
reference client per ruling 2; rule D1 amended; T18 discharged; `VIEWER_TASKS.md` updated.
**Gate.** The picture test's six captures unchanged byte for byte (the landing did not move); vitest green with
the lock and status tests replaced by generate-and-reset tests; `tests/test_viewer.py` rewritten to the new rule;
`tsc -b` and `vite build` clean; an Opus reviewer walks the panel on `prod` or a local build and reports every
control reachable without confirming anything.

### Phase W2 — the template bundles

**Probe first.** Export one template in full and report the table: entries, bytes per route, total; the time to
export; the level-3 cell count and bytes. Put the size bound to the owner (ruling 6) with that table.
**Build.** `tools/export_template.py`; the manifest format; the bundle reader in `galaxy.api` behind the hash
check; the fall-through; CI builds the bundles into the image; `tools/timings.py` gains rows for a bundle hit and a
miss, measured cold (B2).
**Gate.** Every bundle entry equals the live computation byte for byte, asserted over the whole manifest for both
templates and both layer settings; a changed hash refuses the bundle with a named error; the timings rows; the
suite green; `verify_clone`.

### Phase W3 — the gateway

**Build.** `gateway/` as §2c: the project, serving, YARP, limits, the queue, share links, caching, Aspire for
local runs, OpenTelemetry, xunit tests with `WebApplicationFactory` and a stub model; a `dotnet` job in CI; the
frontend served by the gateway in development through Aspire. Built in two sittings if needed: first serving,
proxying and limits; then the queue, share links and caching.
**Gate.** The frontend's full flow through the gateway against the real model with no client change; `/api/
version` through the gateway equals the model's; the limiter returns 429 on the second concurrent generate and the
queue serves it after; a share link round-trips its inputs and opens warm on the second load; every cache key
contains the hash (a test reads the key builder); `dotnet test` green; the Python suite untouched and green.

### Phase W4 — the deployment

**Build.** `Dockerfile.model`, `gateway/Dockerfile`, both images in `image.yml`; Bicep with the two apps, internal
ingress for the model, storage, the gateway's health probe on `/healthz` and the model's on `/api`; `deploy.ps1`
with both tags; the suspended environment recreated; `README.md` and `VIEWER_TASKS.md` T19 updated.
**Gate.** The deployed site serves the landing from a bundle with the model replica at zero (the model's logs show
no request); an edit wakes the model and returns through the queue; a share link opens on another device; the
month's projected cost at zero traffic is zero, written down from the Bicep's sizes.

### Phase W5 — smoothness, measured

**Probe.** On the deployed site, through Playwright: template switch time, zoom-level change time, first paint,
cold and warm, five runs each, in a table. Compared with the owner's bound (ruling 10).
**Build.** Whatever the table says is slow and the bound forbids: a prefetch of the neighbouring level's cells, a
smaller level-3 encoding, a CDN in front of the bundles, an eager warm of the gateway. Each measured before and
after.
**Gate.** The table inside the bound, recorded in the decision with the before numbers.

---

## 6. Costs and order

| Phase | Row | Deliverable | Depends on | Sessions | Lead |
|---|---|---|---|---|---|
| W3 | S70 | The gateway | nothing in the model; in parallel from adoption | 2 | the owner; scaffolded by an agent (ruling 12) |
| W2 | S71 | Template bundles | V6, V7 (S64, S66) | 1–2 | Opus; Fable at the byte-identity gate if it fails |
| W4 | S72 | Deployment | W2, W3 | 1 | Opus |
| W5 | S73 | Smoothness | W4 | 0.5–1 | Opus |

About five to six sessions beside the seven BUILD_III rows still to run (S63–S69; W1 is its V9). No Fable gate is required by design; a
conditional one opens if W2's byte identity cannot be met (§3d of BUILD_III applies as written).

---

## 7. Rulings needed from the owner

**Answered 2026-10-14 (D222): "adopt the plan with your recommendations except for 12, scaffold the project for
me."** Every recommendation in the last column stands as the ruling, except 12, whose ruling is the owner's words:
an agent scaffolds W3 and the features are the owner's. Rulings 2, 3 and 13 travel with the work they concern to
BUILD_III (its §7 rulings 13–15); 14's sentence is entered in BUILD_III's V6 text.

| # | Question | Options | Recommendation |
|---|---|---|---|
| 1 | Where the build sits | (a) W3 now in parallel, W1 at the next gap, W2–W5 after S66; (b) everything after Audit V; (c) BUILD_III's V phases paused for this | (a) |
| 2 | The reference client `interface/` | (a) retire its staged workflow, keep it as a route demonstration; (b) keep it whole behind a flag; (c) delete it | (a) |
| 3 | Editing granularity | (a) any input at any time, regenerate whole; (b) groups must be generated in order (the old rule in new clothes) | (a) |
| 4 | Share link form | (a) a short id over a stored record, result cached beside it; (b) a stateless link carrying the inputs, nothing stored; (c) both | (a), with (b) as the copy-the-inputs fallback |
| 5 | Limits | numbers: requests per minute per IP, concurrent generates, the longest allowed route | 60 / minute, 1 concurrent generate with a queue of 10, 120 s |
| 6 | Bundle scope | which filter sets, which levels ship, the size bound per template | all shipped sets; levels 0–1 whole, level 2 as the probe allows, 3 on demand (§4b); bound after the probe |
| 7 | The gateway's stack | .NET 10 LTS, minimal API, YARP, xunit, Aspire; the folder `gateway/` | as listed |
| 8 | Two container apps or one multi-container app | (a) two apps, the model internal; (b) one app with two containers | (a): the model wakes only on edits |
| 9 | Minimum replicas | zero on both (free), or the gateway warm (paid) | zero |
| 10 | The smoothness bound | a number: template switch and zoom step, warm, on the deployed site | 1 s warm, 5 s cold, to be checked against the probe |
| 11 | The old API's own caches | keep the in-memory galaxy cache in the model (two galaxies) beside the bundles, or drop it | keep |
| 12 | Who builds W3 | the owner alone, the owner with an agent scaffolding and writing tests, or an agent whole | the owner with an agent for tests: the point is the experience |
| 13 | The zoomed-in point layer (T4, §4b) | (a) added to V6; (b) a short V6b after S64; (c) left out | (b): V6 already has three builders |
| 14 | V6's routes cell-keyed (§4b) | one sentence entered in BUILD_III's V6 text now, or left to S64's lead | enter it now; it costs nothing and S64 reads it first |
| 15 | The deepest zoom on a template (§4b) | (a) wakes the model, W5's bound allows it; (b) the model kept warm; (c) the ring-first draw published for the viewer to evaluate | (a) until the probe's numbers say otherwise |

---

## Appendix A — rule amendments, verbatim; D1's is entered at BUILD_III's Phase V9 (S68), D3's and D5's at W3's merge

**D1 (replacing its lock clauses; the landing clauses kept).** *The viewer shows one galaxy at a time and never a
galaxy that is half one input set and half another.* It lands on the Galaxy view of the default template, every
input at the template's values; a switcher selects another template; "Edit galaxy" opens the inputs in their
registry groups, every one editable at any time, seeds as rerolls, pins read-only with their source; "Generate"
regenerates the galaxy whole from the inputs shown, and until it returns the previous galaxy stays on screen and is
marked stale; "Reset to template" returns the inputs to the template's. *Amended on the owner's word of 2026-10-14*
`[verified: DECISIONS.md D<next>]`. **Until then the rule read:** "A lock means do not re-roll this … reopening a
stage discards every later one" — the staged flow of the first three builds, whose justification (a checkpoint's
preview must agree with the inputs that made it) is kept by the first sentence above.

**D5 (one sentence added).** *A gateway in front of the API is held to the same: it serves what the model
published, keyed by the model's content hash, and computes nothing.*

**D3 (one sentence added).** *Every cache between the model and the viewer, in the API or in front of it, is keyed
on that hash.*
