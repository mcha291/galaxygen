// The galaxygen gateway (BUILD_IV §2c, Phase W3): an ASP.NET Core minimal API in front of the Python model.
//
// It serves the built frontend and the pregenerated template bundles, proxies everything else under /api
// to the model, and owns the features that are about users rather than physics: limits, a queue for edits,
// share links, caching. It runs no physics, holds no colour table, and keys every cache on the model's
// content hash (rules D3 and D5 as amended for this build; BUILD_IV Appendix A).

using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.RateLimiting;
using Azure.Data.Tables;
using Azure.Storage.Blobs;
using Galaxygen.Gateway;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

// OpenTelemetry, health checks, service discovery and HttpClient resilience (Galaxygen.ServiceDefaults).
builder.AddServiceDefaults();

builder.Services.Configure<GatewayOptions>(builder.Configuration.GetSection(GatewayOptions.Section));
var options = builder.Configuration.GetSection(GatewayOptions.Section).Get<GatewayOptions>() ?? new GatewayOptions();

builder.Services.AddSingleton(TimeProvider.System);
builder.Services.ConfigureHttpJsonOptions(json =>
    json.SerializerOptions.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.CamelCase)));

// --- The client's address: behind Container Apps' ingress it is X-Forwarded-For's last entry ---------------------
if (options.Limits.TrustForwardedFor)
{
    builder.Services.Configure<ForwardedHeadersOptions>(forwarded =>
    {
        forwarded.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
        forwarded.ForwardLimit = 1; // the ingress's own entry; anything a client wrote before it is not believed
        forwarded.KnownIPNetworks.Clear();
        forwarded.KnownProxies.Clear();
    });
}

// --- Limits (BUILD_IV §7 ruling 5: 60 / minute per client; the generate queue is the jobs' own, below) ---------
builder.Services.AddRateLimiter(limiter =>
{
    limiter.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

    // Every route but the static files: a sliding window per client address. There are no accounts, so the
    // address is the client.
    limiter.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        RateLimitPartition.GetSlidingWindowLimiter(
            partitionKey: Client(context),
            factory: _ => new SlidingWindowRateLimiterOptions
            {
                PermitLimit = options.Limits.PermitPerWindow,
                Window = TimeSpan.FromSeconds(options.Limits.WindowSeconds),
                SegmentsPerWindow = 6,
                QueueLimit = 0,
            }));

    // Creating a share link: a link is a capability and a stored record, so a client makes a few an hour.
    limiter.AddPolicy(Policies.Share, context =>
        RateLimitPartition.GetSlidingWindowLimiter(
            partitionKey: Client(context),
            factory: _ => new SlidingWindowRateLimiterOptions
            {
                PermitLimit = options.Limits.SharesPerHour,
                Window = TimeSpan.FromHours(1),
                SegmentsPerWindow = 6,
                QueueLimit = 0,
            }));
});

// --- The model, as the gateway's own code asks it (jobs, share links, the hash) ---------------------------------
// The defaults' resilience gives every client a 30 s total; a model route may take the whole of ruling 5's 120 s,
// so this client's pipeline is replaced by one sized to it: one retry, for a replica still waking from zero.
var attempt = TimeSpan.FromSeconds(options.Model.TimeoutSeconds);
#pragma warning disable EXTEXP0001 // RemoveAllResilienceHandlers is marked experimental
builder.Services.AddHttpClient<ModelClient>(http =>
    {
        http.BaseAddress = new Uri(options.Model.BaseUrl);
        http.Timeout = Timeout.InfiniteTimeSpan; // the pipeline below owns the timeouts
    })
    .RemoveAllResilienceHandlers()
    .AddStandardResilienceHandler(resilience =>
    {
        resilience.AttemptTimeout.Timeout = attempt;
        resilience.Retry.MaxRetryAttempts = 1;
        resilience.TotalRequestTimeout.Timeout = attempt * 2 + TimeSpan.FromSeconds(10);
        resilience.CircuitBreaker.SamplingDuration = attempt * 2;
    });
#pragma warning restore EXTEXP0001
builder.Services.AddSingleton<ModelVersion>();

// --- The edit queue -----------------------------------------------------------------------------------------------
builder.Services.AddSingleton<JobQueue>();
builder.Services.AddHostedService<JobWorker>();

// --- Share links: Azure Table and Blob Storage when connection strings are given (Aspire's emulator locally, the
// storage account when deployed), the gateway's memory otherwise, so a developer's machine needs neither ----------
if (!string.IsNullOrWhiteSpace(builder.Configuration.GetConnectionString(TableShareStore.Table)))
{
    builder.AddAzureTableServiceClient(TableShareStore.Table);
    builder.Services.AddSingleton<IShareStore>(sp => new TableShareStore(sp.GetRequiredService<TableServiceClient>()));
}
else
{
    builder.Services.AddSingleton<IShareStore, MemoryShareStore>();
}

if (!string.IsNullOrWhiteSpace(builder.Configuration.GetConnectionString(BlobResultStore.Container)))
{
    builder.AddAzureBlobServiceClient(BlobResultStore.Container);
    builder.Services.AddSingleton<IResultStore>(sp => new BlobResultStore(sp.GetRequiredService<BlobServiceClient>()));
}
else
{
    builder.Services.AddSingleton<IResultStore, MemoryResultStore>();
}

// --- Proxying (YARP): /api/* goes to the model, through the output cache ------------------------------------------
builder.Services.AddReverseProxy()
    .LoadFromMemory(Proxy.Routes(), Proxy.Clusters(options.Model));

builder.Services.AddOutputCache(cache =>
{
    cache.SizeLimit = options.Cache.SizeMegabytes * 1024L * 1024L;
    cache.MaximumBodySize = options.Cache.EntryMegabytes * 1024L * 1024L;
    cache.AddPolicy(ModelCachePolicy.Name, new ModelCachePolicy());
});

var app = builder.Build();

if (options.Limits.TrustForwardedFor) app.UseForwardedHeaders();

// --- Serving: the frontend and the template bundles as static files ------------------------------------------
// Ahead of the limiter: a page load is a dozen files, cheap and cacheable, and a client limited on its own
// scripts would see a broken page rather than a 429. Frontend:Path is the Vite build (frontend/dist); Bundles:Path
// is W2's export (BUILD_IV §2b). Either may be absent on a developer's machine: the gateway then serves only the
// API routes and says so at /healthz.
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

app.UseRateLimiter();
app.UseOutputCache();

// --- Routes ---------------------------------------------------------------------------------------------------
app.MapDefaultEndpoints(); // /health and /alive, development only (ServiceDefaults)

app.MapGet("/healthz", (IOptions<GatewayOptions> opts, JobQueue queue, IShareStore shares, IResultStore results) =>
{
    var (queued, running) = queue.Counts();
    return Results.Ok(new
    {
        status = "ok",
        frontend = frontend is not null,
        bundles = bundles is not null,
        model = opts.Value.Model.BaseUrl,
        pinned = !string.IsNullOrWhiteSpace(opts.Value.Model.ContentHash),
        jobs = new { queued, running },
        shares = shares.Kind,
        results = results.Kind,
    });
});

app.MapJobs();
app.MapShares();

// Everything else under /api is the model's (YARP), cached by path, query and content hash. A bundle hit will be
// answered before this once W2 lands.
app.MapReverseProxy().CacheOutput(ModelCachePolicy.Name);

// The SPA fallback: any other path is the frontend's router, when a frontend is present.
if (frontend is not null)
{
    app.MapFallbackToFile("index.html", new StaticFileOptions { FileProvider = new PhysicalFileProvider(frontend) });
}

app.Run();

static string Client(HttpContext context) => context.Connection.RemoteIpAddress?.ToString() ?? "unknown";

// WebApplicationFactory<Program> needs the entry point to be visible to the test project.
public partial class Program;
