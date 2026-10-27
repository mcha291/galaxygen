# gateway — the .NET service in front of the Python model (BUILD_IV Phase W3)

An ASP.NET Core minimal API on .NET 10. It serves the built frontend, proxies `/api` to the model, and owns the
features about users rather than physics: limits, an edit queue, share links, caching. It runs no physics, reads
no template bundle and keys every cache on the model's content hash (`docs/BUILD_IV.md` §2c and Appendix A; rule
D5's last sentence: a gateway serves what the model published, keyed by the model's content hash, and computes
nothing). Reviewed and fixed at S74.

```
gateway/
  Galaxygen.slnx                    the solution
  Galaxygen.Gateway/                the web project: Program.cs (the wiring), ModelPipeline.cs (the cache's label,
                                    the window's scope, the model's one permit), ModelClient.cs (the route table,
                                    the model's answers, its hash and the pin), Caching.cs, Jobs.cs, Shares.cs,
                                    GalaxyQuery.cs, Proxy.cs, StaticRoots.cs, GatewayOptions.cs
  Galaxygen.Gateway.Tests/          xunit through WebApplicationFactory against StubModel, no Python needed
  Galaxygen.AppHost/                .NET Aspire: the gateway, the model container and Azurite, one `dotnet run`
  Galaxygen.ServiceDefaults/        OpenTelemetry, health checks, service discovery, HttpClient defaults
  Dockerfile                        the gateway image (W4), built from the repository root
```

## Run

The gateway alone, against a model started by hand (`uv run python -m galaxy.api`, port 8017):

```bash
dotnet run --project gateway/Galaxygen.Gateway
```

Everything together, with the Aspire dashboard (Docker Desktop running; the model container is built from the
repository's root `Dockerfile` on first start and published on host port 8027, so it never collides with a model
run by hand on 8017):

```bash
dotnet run --project gateway/Galaxygen.AppHost
```

The tests:

```bash
dotnet build gateway/Galaxygen.slnx -c Release --nologo
dotnet test gateway/Galaxygen.slnx -c Release --no-build --nologo
```

Without a frontend build the gateway serves only its own routes and the API; `npm --prefix frontend run build`
makes one, and `/healthz` says whether it was found.

## The model's hash

Every cache key carries `/api/version`'s `model.hash`: the hash of every byte under `model/galaxy`, so a stage, a
constant or a data file that changes moves it. That string alone is the key's hash; the `api` hash (a subset of it)
and the `viewer` hash are not in any key. A `/api/version` without `model` is refused with a logged error (the
gateway requires the API of S72 or later), and until one is read nothing is looked up or stored in any cache: the
output cache passes requests to the model uncached, a share link's route answers 503, a job fails.

Without a pin the hash is read from `/api/version` (its own 10 s timeout, never retried, one read at a time) and
trusted for `Model:VersionSeconds`. Every `/api/version` the viewer asks through the gateway is read on its way
back too, unchanged.

A deployment may pin the hash (`Model:ContentHash`: `model.hash`, 32 hex characters, the value the model image's
`/api/version` publishes) so that a request answered from a cache never wakes a model scaled to zero. The pin is
verified: against every `/api/version` the viewer asks through the gateway, and once per `Model:VersionSeconds`
before a request reaches the model (a cache hit asks nothing). On a mismatch the gateway logs an error, drops the
pin and keys on the live hash from then on (an answer computed under the wrong pin is not stored), and `/healthz`
answers 503 with `pin_mismatch: true` and both hashes until the deployment is corrected and restarted. A model that
cannot be read leaves the pin standing.

## Configuration

| Key | Default | Meaning |
|---|---|---|
| `Gateway:Model:BaseUrl` | `http://localhost:8017` | where the Python model answers; Aspire sets it from the container |
| `Gateway:Model:TimeoutSeconds` | 120 | the longest allowed model route (ruling 5): YARP's activity timeout and the gateway's own client's one timeout; nothing sent to the model is retried |
| `Gateway:Model:ContentHash` | empty | the pinned `model.hash`; empty reads `/api/version` (above) |
| `Gateway:Model:VersionSeconds` | 30 | how long a hash read from `/api/version` is trusted; with a pin, how often it is checked |
| `Gateway:Model:VersionTimeoutSeconds` | 10 | a read of `/api/version`: its timeout, and the longest a request waits for another's read |
| `Gateway:Limits:PermitPerWindow` / `WindowSeconds` | 60 / 60 | the sliding window per client address (six segments), over the requests that may reach the model (below) |
| `Gateway:Limits:ConcurrentModelRequests` / `ModelQueue` | 1 / 64 | requests computing at the model at once / waiting, oldest first; past that 429 with `Retry-After: 5` |
| `Gateway:Limits:ConcurrentGenerates` / `GenerateQueue` | 1 / 10 | jobs run at once / jobs waiting; past that `POST /jobs` is 429 with `Retry-After: 5` |
| `Gateway:Limits:SharesPerHour` | 20 | share links a client may create an hour |
| `Gateway:Limits:QueryBytes` | 131072 | the largest galaxy query a job or a share link takes, bytes of its canonical form (an eighth of the API's `MAX_BODY`) |
| `Gateway:Limits:TrustForwardedFor` | false | the client is `X-Forwarded-For`'s last entry; on only behind Container Apps' ingress (W4), never when exposed directly |
| `Gateway:Cache:SizeMegabytes` / `EntryMegabytes` / `ExpirationMinutes` | 256 / 64 / 60 | the output cache: its size, its largest answer, an entry's life |
| `Gateway:Cache:ResultEntries` / `ResultMegabytes` | 200 / 64 | share links' answers kept in memory when no blob store is configured: entries and bytes, the oldest dropped first |
| `Gateway:Jobs:Retain` / `ResultMegabytes` | 100 / 64 | finished jobs remembered, and the bytes of their results; the oldest finished forgotten first, as jobs are queued and finish and each minute |
| `Gateway:Frontend:Path` | `../../frontend/dist` | the Vite build, relative to the project or absolute |
| `ConnectionStrings:shares` / `ConnectionStrings:results` | none | Azure Table / Blob Storage for share links; Aspire sets both from Azurite; without them, the gateway's memory (lost on restart) |

Environment variables use `__` for `:` (`Gateway__Model__BaseUrl`).

## The routes

| Route | Answer |
|---|---|
| `GET /`, files of the build | the frontend. `/assets/*` (Vite's hashed names) `Cache-Control: public, max-age=31536000, immutable`; `index.html` and every other file `no-cache` |
| any other path without a file extension | `index.html`, `no-cache` (the SPA fallback). Never for `/assets/*` or `/api/*`: a missing asset is 404 |
| `/api/*` | the model's, through YARP, unchanged; its headers (`X-Galaxy-Stages`, `X-Galaxy-Source`, `Cache-Control: no-store`) pass through. A GET or HEAD is cached by path, every query parameter and `model.hash`, except `/api` and `/api/version` (a trailing slash is the same path); only a 200 without a cookie is stored; a POST is never cached. `X-Gateway-Cache: hit` on a replay, with `X-Galaxy-Stages` empty (no stage ran for it), `miss` on an answer from the model. The routes that take a galaxy's inputs (`arrays`, `region`, `system`, `clouds`, `clusters`, `remnants`, `bright`, `render`, `layer`) wait for the model's one permit (below); a cache hit never waits |
| `POST /jobs` `{route?, query}` | `202` and `{id, state, position}` at once; `429` when the queue is full. `route` is any route of the API's table but `/api` and `/api/version` (`arrays` by default) |
| `GET /jobs/{id}` | the job's state: `queued` (with its position), `running`, `done`, `failed`, `cancelled`, and the `model.hash` it ran under |
| `GET /jobs/{id}/events` | the same as server-sent events, one per change, ending at the last state |
| `GET /jobs/{id}/result` | the model's status, bytes, `X-Galaxy-Stages`, `X-Galaxy-Source` and `Cache-Control`, as it sent them; `409` while the job waits or runs |
| `DELETE /jobs/{id}` | cancels a queued job (its place is free at once) or a running one |
| `POST /share` `{query}` | `201` and `{id, url, query, hash}`; the id is the query's digest (12 characters of base64url), so the same galaxy is the same link. `hash` is the one known without waiting (the pin or the last read; one bounded read only when none is), for the record only |
| `GET /share/{id}` | the record; an id of another shape is 404 |
| `GET /share/{id}/{route}` | the shared galaxy's route: the record's query with the request's own parameters beneath it (the record's keys win). Beside the record's keys the request may name only the route's own parameters from the API's table (a window's `r_min r_max phi_min phi_max`, `level`, `precision`, `filters`, `white`, `set`, `l_min`, `only`, `fields`, `t_samples`, `stars`, `brightest`, `view`, `cells`, `n`, `table`, `cell`, `index`, each where its route declares it); anything else is 400. From the store under the current `model.hash` when held (`X-Gateway-Cache: hit`, `X-Galaxy-Stages` empty), else from the model, which then fills it (`miss`); an input-taking route's miss waits for the model's permit |
| `GET /healthz` | `status`, `frontend`, `model`, `pinned` (a pin is in force: false once a mismatch dropped it), `pin_configured` (`Model:ContentHash` is set), `pin_mismatch`, `hash` (`pin`, `live`, `keyed`, `error`), `limits` (the window, the model's permit with `in_flight` and `waiting`, shares per hour, query bytes), `jobs` (counts and limits), the stores in use. 503 on a pin mismatch |
| `GET /health`, `GET /alive` | ASP.NET health checks, in Development only (ServiceDefaults) |

The model answers a template's bundled request itself (S72, `X-Galaxy-Source: bundle`); the gateway serves those
bytes as any other.

## Limits

- **The window** (ruling 5): 60 requests a minute per client address, counting only what may reach the model:
  `/api/*` past the output cache (a hit is free), `POST /jobs` and `GET /share/{id}/{route}`. The page, its
  files, the fallback, `/healthz`, `/health`, `/alive`, a job's state and a share's record are not counted;
  `POST /share` has its own hourly window. A 429 carries `Retry-After`.
- **The model's permit** (S74, the lead's ruling, for the owner to re-rule): one request computes at the model at
  a time, over the input-taking `/api` routes the viewer asks through YARP, the share links' misses and the jobs
  together; 64 wait, oldest first; past that 429 with `Retry-After: 5`. The metadata routes (`/api`, `version`,
  `stages`, `fields`, `inputs`, `templates`, `blackbody`) are not limited by it.
- **The edit queue**: one job runs, ten wait. The viewer does not use `/jobs`; a job also takes the model's permit.

## The rules at this boundary

One `fetch` stays in the client (D2; the gateway is same-origin). `/api/version` passes through unchanged and every
cache keys on its `model.hash` (D3). No physics, no colour table, no bundle read here (D5).

## Left to W4

- The Blob store's lifetime: nothing in the gateway deletes a stored answer; the `results` container's lifecycle
  rule (a TTL) is set on the storage account.
- `Limits:TrustForwardedFor` on behind Container Apps' ingress.
- Azure Monitor: ServiceDefaults exports OpenTelemetry over OTLP only when `OTEL_EXPORTER_OTLP_ENDPOINT` is set
  (Aspire's dashboard locally); the Azure Monitor exporter is not wired.
- Trimming: the Dockerfile publishes untrimmed.
- The memory stores (jobs always; shares and their answers without connection strings) are lost on a restart.
- A share link's routes are GET only: a query past Kestrel's 8 KB request line (a named instrument's sampled
  filter curves) cannot be sent through one; the viewer's own long queries go to `/api` as a POST.
