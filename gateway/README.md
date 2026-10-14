# gateway — the .NET service in front of the Python model (BUILD_IV Phase W3)

An ASP.NET Core minimal API on .NET 10. It serves the built frontend and the pregenerated template bundles,
proxies the rest of `/api` to the model, and owns the features about users rather than physics. It runs no
physics and keys every cache on the model's content hash (`docs/BUILD_IV.md` §2c and Appendix A).

**This is the scaffold.** Serving, proxying, limits, health and the tests exist; the queue, share links and the
hash-keyed cache are marked `TODO(W3)` in `Galaxygen.Gateway/Program.cs` and are the owner's to build
(ruling 12). The design for each is the table in `BUILD_IV.md` §2c.

```
gateway/
  Galaxygen.slnx                    the solution
  Galaxygen.Gateway/                the web project: Program.cs, GatewayOptions.cs, Proxy.cs, StaticRoots.cs
  Galaxygen.Gateway.Tests/          xunit through WebApplicationFactory, no model needed
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
| `Gateway:Limits:PermitPerWindow` / `WindowSeconds` | 60 / 60 | the sliding window per client address |
| `Gateway:Limits:ConcurrentGenerates` / `GenerateQueue` | 1 / 10 | the generate route's concurrency limiter |
| `Gateway:Frontend:Path` | `../../frontend/dist` | the Vite build |
| `Gateway:Bundles:Path` | `../../bundles` | W2's template export |

Environment variables use `__` for `:` (`Gateway__Model__BaseUrl`).

## What goes where (the owner's features)

| Feature | Where | The .NET it exercises |
|---|---|---|
| The edit queue | a `BackgroundService` over a `Channel<GenerateJob>`; `/jobs` returns an id, `/jobs/{id}` its state | hosted services, channels, cancellation, `IAsyncEnumerable` for progress |
| Share links | `/share`: a short id over {template, inputs, seeds} in Azure Table Storage, the generated bundle in Blob Storage beside it; a limit per client on creating them | `Azure.Data.Tables`, `Azure.Storage.Blobs`, route groups |
| Caching | output caching on the template routes; every key carries `/api/version`'s hash | output caching middleware, cache key policies |
| Bundles | when W2's export exists: a request matching a bundle entry is answered from the file before YARP | static files, endpoint ordering |

The rules at this boundary: one `fetch` stays in the client (D2; the gateway is same-origin), the hash passes
through (D3), no physics here (D5).
