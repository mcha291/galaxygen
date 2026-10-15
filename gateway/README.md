# gateway — the .NET service in front of the Python model (BUILD_IV Phase W3)

An ASP.NET Core minimal API on .NET 10. It serves the built frontend and the pregenerated template bundles,
proxies the rest of `/api` to the model, and owns the features about users rather than physics. It runs no
physics and keys every cache on the model's content hash (`docs/BUILD_IV.md` §2c and Appendix A).

Serving, proxying, limits, the edit queue, share links and the hash-keyed cache are built (W3); the bundle routes
wait for W2's export. The design for each is the table in `BUILD_IV.md` §2c; the routes are below.

```
gateway/
  Galaxygen.slnx                    the solution
  Galaxygen.Gateway/                the web project: Program.cs (the wiring), Jobs.cs, Shares.cs, Caching.cs,
                                    ModelClient.cs (the model's answers and its hash), GalaxyQuery.cs, Proxy.cs
  Galaxygen.Gateway.Tests/          xunit through WebApplicationFactory against StubModel, no Python needed
  Galaxygen.AppHost/                .NET Aspire: the gateway + the model container, one `dotnet run`
  Galaxygen.ServiceDefaults/        OpenTelemetry, health checks, service discovery, HttpClient resilience
  Dockerfile                        the gateway image (W4), built from the repository root
```

## Run

The gateway alone, against a model started by hand (`uv run python -m galaxy.api`, port 8017):

```bash
dotnet run --project gateway/Galaxygen.Gateway
```

Everything together, with the Aspire dashboard (Docker Desktop running; the model container is built from the
repository's root `Dockerfile` on first start):

```bash
dotnet run --project gateway/Galaxygen.AppHost
```

The tests:

```bash
dotnet test gateway/Galaxygen.slnx
```

`/healthz` says whether a frontend build and a bundles directory were found (`Gateway:Frontend:Path`,
`Gateway:Bundles:Path` in `appsettings.json`, relative to the project). Without a frontend build the gateway serves
only the API routes; `npm --prefix frontend run build` makes one.

## Configuration

| Key | Default | Meaning |
|---|---|---|
| `Gateway:Model:BaseUrl` | `http://localhost:8017` | where the Python model answers; Aspire sets it from the container |
| `Gateway:Model:TimeoutSeconds` | 120 | the longest allowed model route (ruling 5) |
| `Gateway:Model:ContentHash` | empty | the model's hash, pinned by a deployment so a cache hit never wakes the model; empty reads `/api/version` |
| `Gateway:Model:VersionSeconds` | 30 | how long a hash read from `/api/version` is trusted |
| `Gateway:Limits:PermitPerWindow` / `WindowSeconds` | 60 / 60 | the sliding window per client address (static files are not counted) |
| `Gateway:Limits:ConcurrentGenerates` / `GenerateQueue` | 1 / 10 | jobs run at once / jobs waiting; past that `POST /jobs` is 429 |
| `Gateway:Limits:SharesPerHour` | 20 | share links a client may create an hour |
| `Gateway:Limits:QueryBytes` | 16384 | the largest galaxy query a job or a share takes |
| `Gateway:Limits:TrustForwardedFor` | false | the client is `X-Forwarded-For`'s last entry; turn on behind Container Apps' ingress (W4), never when exposed directly |
| `Gateway:Cache:SizeMegabytes` / `EntryMegabytes` / `ExpirationMinutes` | 256 / 64 / 60 | the output cache |
| `Gateway:Cache:ResultEntries` | 200 | share-link answers kept in memory when no blob store is configured |
| `Gateway:Jobs:Retain` | 100 | finished jobs remembered for their clients |
| `ConnectionStrings:shares` / `ConnectionStrings:results` | none | Azure Table / Blob Storage for share links; Aspire sets both from Azurite; without them, memory |
| `Gateway:Frontend:Path` | `../../frontend/dist` | the Vite build |
| `Gateway:Bundles:Path` | `../../bundles` | W2's template export |

Environment variables use `__` for `:` (`Gateway__Model__BaseUrl`).

## The routes

| Route | Answer |
|---|---|
| `GET /api/*` | the model's, through YARP; cached by path, every query parameter and the content hash (`Caching.cs`). `/api` and `/api/version` are never cached; a long query the client sends as a POST is not cached either |
| `POST /jobs` `{route?, query}` | `202` and `{id, state, position}` at once; `429` when the queue is full. `route` is one of the galaxy routes (`arrays` by default) |
| `GET /jobs/{id}` | the job's state: `queued` (with its position), `running`, `done`, `failed`, `cancelled`, and the hash it ran under |
| `GET /jobs/{id}/events` | the same as server-sent events, one per change, ending at the last state |
| `GET /jobs/{id}/result` | the model's bytes and `x-galaxy-stages`, exactly as it sent them; `409` while the job runs |
| `DELETE /jobs/{id}` | cancels a queued or running job |
| `POST /share` `{query}` | `201` and `{id, url, query, hash}`; the id is the query's digest, so the same galaxy is the same link |
| `GET /share/{id}` | the record |
| `GET /share/{id}/{route}` | the shared galaxy's route: the record's query (its keys win) with the request's own parameters, from the store under the current hash when held (`x-gateway-cache: hit`), else from the model, which then fills it (`miss`) |
| `GET /healthz` | what is served, the queue's counts, which stores are in use |

When W2's export exists, a request matching a bundle entry is to be answered from the file before YARP.

The rules at this boundary: one `fetch` stays in the client (D2; the gateway is same-origin), the hash passes
through (D3), no physics here (D5).
