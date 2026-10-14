// The galaxygen gateway (BUILD_IV §2c, Phase W3): an ASP.NET Core minimal API in front of the Python model.
//
// It serves the built frontend and the pregenerated template bundles, proxies everything else under /api
// to the model, and owns the features that are about users rather than physics: limits, a queue for edits,
// share links, caching. It runs no physics, holds no colour table, and keys every cache on the model's
// content hash (rules D3 and D5 as amended for this build; BUILD_IV Appendix A).
//
// This file is the scaffold (the owner's ruling 12: "scaffold the project for me"). Each feature below is
// wired to the point where the owner's code goes and no further; the extension points are marked TODO(W3).

using System.Threading.RateLimiting;
using Galaxygen.Gateway;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

// OpenTelemetry, health checks, service discovery and HttpClient resilience (Galaxygen.ServiceDefaults).
builder.AddServiceDefaults();

builder.Services.Configure<GatewayOptions>(builder.Configuration.GetSection(GatewayOptions.Section));
var options = builder.Configuration.GetSection(GatewayOptions.Section).Get<GatewayOptions>() ?? new GatewayOptions();

// --- Limits (BUILD_IV §7 ruling 5: 60 / minute per client, 1 concurrent generate with a queue of 10) ---------
builder.Services.AddRateLimiter(limiter =>
{
    limiter.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

    // Every route: a sliding window per client address. There are no accounts, so the address is the client.
    limiter.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        RateLimitPartition.GetSlidingWindowLimiter(
            partitionKey: context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            factory: _ => new SlidingWindowRateLimiterOptions
            {
                PermitLimit = options.Limits.PermitPerWindow,
                Window = TimeSpan.FromSeconds(options.Limits.WindowSeconds),
                SegmentsPerWindow = 6,
                QueueLimit = 0,
            }));

    // The generate route: one model replica runs one expensive job at a time; the rest wait in a short queue.
    limiter.AddConcurrencyLimiter(Policies.Generate, policy =>
    {
        policy.PermitLimit = options.Limits.ConcurrentGenerates;
        policy.QueueLimit = options.Limits.GenerateQueue;
        policy.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
    });
});

// --- Proxying (YARP): /api/* that no bundle answers goes to the model -------------------------------------------
// The model's address comes from configuration (Model:BaseUrl); under Aspire the app host sets it from the
// model container's endpoint. Timeouts are sized to the longest route (ruling 5: 120 s).
builder.Services.AddReverseProxy()
    .LoadFromMemory(Proxy.Routes(), Proxy.Clusters(options.Model));

// --- Caching: output caching on what the model publishes; every key carries the content hash ------------------
// TODO(W3): add the hash to the cache key once /api/version is read at startup (BUILD_IV Appendix A, D3).
builder.Services.AddOutputCache();

// --- The edit queue and share links: the owner's features ---------------------------------------------------
// TODO(W3): a BackgroundService consuming a Channel<GenerateJob>; the job store; the share-link store
// (Azure.Data.Tables for the record, Azure.Storage.Blobs for the generated bundle beside it). The packages are
// referenced; nothing is registered until the code exists, so a missing connection string cannot fail startup.

var app = builder.Build();

app.UseRateLimiter();
app.UseOutputCache();

// --- Serving: the frontend and the template bundles as static files ------------------------------------------
// Frontend:Path is the Vite build (frontend/dist); Bundles:Path is W2's export (BUILD_IV §2b). Either may be
// absent on a developer's machine: the gateway then serves only the API routes and says so at /healthz.
var frontend = StaticRoots.Resolve(app.Environment, options.Frontend.Path);
var bundles = StaticRoots.Resolve(app.Environment, options.Bundles.Path);

if (bundles is not null)
{
    app.UseStaticFiles(new StaticFileOptions
    {
        FileProvider = new PhysicalFileProvider(bundles),
        RequestPath = "/bundles",
        OnPrepareResponse = ctx => ctx.Context.Response.Headers.CacheControl = "public, max-age=31536000, immutable",
    });
}

if (frontend is not null)
{
    app.UseDefaultFiles(new DefaultFilesOptions { FileProvider = new PhysicalFileProvider(frontend) });
    app.UseStaticFiles(new StaticFileOptions { FileProvider = new PhysicalFileProvider(frontend) });
}

// --- Routes ---------------------------------------------------------------------------------------------------
app.MapDefaultEndpoints(); // /health and /alive, development only (ServiceDefaults)

app.MapGet("/healthz", (IOptions<GatewayOptions> opts) => Results.Ok(new
{
    status = "ok",
    frontend = frontend is not null,
    bundles = bundles is not null,
    model = opts.Value.Model.BaseUrl,
}));

// Generation: an edit returns a job id at once; the queue runs it against the model (BUILD_IV §2c).
var jobs = app.MapGroup("/jobs").RequireRateLimiting(Policies.Generate);
jobs.MapPost("/", () => Results.StatusCode(StatusCodes.Status501NotImplemented)); // TODO(W3): enqueue, return { id }
jobs.MapGet("/{id}", (string id) => Results.StatusCode(StatusCodes.Status501NotImplemented)); // TODO(W3): status / result

// Share links: a galaxy is its template, its inputs and its seeds; a link is a short id over that record.
var share = app.MapGroup("/share");
share.MapPost("/", () => Results.StatusCode(StatusCodes.Status501NotImplemented)); // TODO(W3): store, return { id, url }
share.MapGet("/{id}", (string id) => Results.StatusCode(StatusCodes.Status501NotImplemented)); // TODO(W3): the record

// Everything else under /api is the model's (YARP). A bundle hit will be answered before this once W2 lands.
app.MapReverseProxy();

// The SPA fallback: any other path is the frontend's router, when a frontend is present.
if (frontend is not null)
{
    app.MapFallbackToFile("index.html", new StaticFileOptions { FileProvider = new PhysicalFileProvider(frontend) });
}

app.Run();

// WebApplicationFactory<Program> needs the entry point to be visible to the test project.
public partial class Program;
