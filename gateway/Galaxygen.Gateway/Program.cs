// The galaxygen gateway (BUILD_IV §2c, Phase W3): an ASP.NET Core minimal API in front of the Python model.
//
// It serves the built frontend, proxies /api to the model, and owns the features that are about users rather than
// physics: limits, a queue for edits, share links, caching. It runs no physics, holds no colour table, reads no
// bundle (since S72 the model answers a bundled request itself), and keys every cache on the model's content hash,
// /api/version's model.hash (rules D3 and D5 as amended; BUILD_IV Appendix A).

using System.IO.Compression;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.RateLimiting;
using Azure.Data.Tables;
using Azure.Storage.Blobs;
using Galaxygen.Gateway;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.AspNetCore.ResponseCompression;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Options;
using Polly;

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

// --- Limits (BUILD_IV §7 ruling 5: 60 / minute per client; one request computing at the model at a time) ---------
builder.Services.AddRateLimiter(limiter =>
{
    limiter.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    limiter.OnRejected = (rejected, _) =>
    {
        var after = rejected.Lease.TryGetMetadata(MetadataName.RetryAfter, out var wait)
            ? wait
            : TimeSpan.FromSeconds(Math.Max(1, options.Limits.WindowSeconds / 6));
        rejected.HttpContext.Response.Headers.RetryAfter = ((int)Math.Ceiling(Math.Max(1, after.TotalSeconds))).ToString();
        return ValueTask.CompletedTask;
    };

    // A sliding window per client address over the requests that may reach the model (S74, G-8): it sits behind
    // the output cache, so a hit is free, and the page, its files and the health routes are not counted. There are
    // no accounts, so the address is the client.
    limiter.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        !ModelPipeline.Counted(context)
            ? RateLimitPartition.GetNoLimiter("free")
            : RateLimitPartition.GetSlidingWindowLimiter(
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
builder.Services.AddSingleton<ModelGate>();

// --- The model, as the gateway's own code asks it (jobs, share links, the hash) ---------------------------------
// The defaults' standard resilience retries on a timeout or a 5xx: a model route resent while the model's first
// thread still computes is two expensive computations, and a 500 computed twice. This client has no retry at all
// (S74, D-6): one attempt, its timeout the whole request's, ruling 5's 120 s. /api/version is read on its own 10 s
// (Model:VersionTimeoutSeconds, ModelClient.ReadVersionAsync), also never retried.
#pragma warning disable EXTEXP0001 // RemoveAllResilienceHandlers is marked experimental
builder.Services.AddHttpClient<ModelClient>(http =>
    {
        http.BaseAddress = new Uri(options.Model.BaseUrl);
        http.Timeout = Timeout.InfiniteTimeSpan; // the pipeline below owns the timeout
    })
    .RemoveAllResilienceHandlers()
    .AddResilienceHandler("model", pipeline => pipeline.AddTimeout(TimeSpan.FromSeconds(options.Model.TimeoutSeconds)));
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

// --- Proxying (YARP): /api/* goes to the model, through the output cache. YARP's own client takes no part in the
// defaults' resilience (it is not made by IHttpClientFactory) and never retries ------------------------------------
builder.Services.AddReverseProxy()
    .LoadFromMemory(Proxy.Routes(), Proxy.Clusters(options.Model));

builder.Services.AddOutputCache(cache =>
{
    cache.SizeLimit = options.Cache.SizeMegabytes * 1024L * 1024L;
    cache.MaximumBodySize = options.Cache.EntryMegabytes * 1024L * 1024L;
    cache.AddPolicy(ModelCachePolicy.Name, new ModelCachePolicy());
});

// --- Response compression (S76, BUILD_IV W5, D240 F4): brotli, then gzip, on the model's answers and the page's files.
// The landing is 19.4 MB of /api answers (S76's probe), most of it float arrays, which the wire carries as sent. It sits
// INSIDE the output cache (below; S76's review, G2): a body is compressed once, on the miss, and the cache stores it per
// encoding - ModelCachePolicy varies the key by the request's Accept-Encoding - so a hit is served as stored and never
// compressed again, and a client that asks for no encoding is never sent a compressed body. The window and the gate are
// unchanged. On over HTTPS as well: no answer here carries a secret or a cookie for a compression oracle to read.
builder.Services.AddResponseCompression(compression =>
{
    compression.EnableForHttps = true;
    compression.Providers.Add<BrotliCompressionProvider>();
    compression.Providers.Add<GzipCompressionProvider>();
    compression.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(
        ["application/octet-stream", "text/javascript", "image/svg+xml"]); // the model's frames (wire.py MEDIA), Vite's scripts, the icon
});
builder.Services.Configure<BrotliCompressionProviderOptions>(brotli => brotli.Level = CompressionLevel.Fastest);
builder.Services.Configure<GzipCompressionProviderOptions>(gzip => gzip.Level = CompressionLevel.Fastest);

var app = builder.Build();

if (options.Limits.TrustForwardedFor) app.UseForwardedHeaders();

// --- The model's path: label, cache, compression, window, then the gate (ModelPipeline; S74, D-5 and G-8) -------
// The output cache answers a hit before the window counts it or the gate queues it, and before the compression: a
// hit's body was compressed when it was stored (S76's review, G2). Nothing above the cache answers a request.
app.Use(ModelPipeline.Label);
app.UseOutputCache();
app.UseResponseCompression(); // the misses on their way into the cache, the files and the SPA fallback below (S76, F4/G2)

// --- Serving: the frontend's build as static files, never counted and never cached (no policy names them) -----------
// Frontend:Path is the Vite build (frontend/dist). Its /assets/ files carry their content hash in their names, so
// they are immutable for a year; index.html is not, so it is revalidated on every load (S74, G-7). Absent on a
// developer's machine, the gateway serves only its own routes and the API, and says so at /healthz. Since S76's
// review (G2) they are served below the output cache, which passes them through untouched (only the proxied /api
// routes carry its policy), so that the compression above them still covers them.
var frontend = StaticRoots.Resolve(app.Environment, options.Frontend.Path);
StaticFileOptions? files = null;
if (frontend is not null)
{
    var provider = new PhysicalFileProvider(frontend);
    files = new StaticFileOptions
    {
        FileProvider = provider,
        OnPrepareResponse = ctx => ctx.Context.Response.Headers.CacheControl = StaticRoots.CacheControl(ctx.Context.Request.Path),
    };
    app.UseDefaultFiles(new DefaultFilesOptions { FileProvider = provider });
    app.UseStaticFiles(files);
}

// The window and the gate, below the files: a file is answered before either is reached, as before.
app.UseRateLimiter();
app.Use(ModelPipeline.Bound);

// --- Routes ---------------------------------------------------------------------------------------------------
app.MapDefaultEndpoints(); // /health and /alive, development only (ServiceDefaults)

app.MapGet("/healthz", (IOptions<GatewayOptions> opts, JobQueue queue, ModelGate gate, ModelVersion version,
    IShareStore shares, IResultStore results) =>
{
    var settings = opts.Value;
    var (queued, running) = queue.Counts();
    var (inFlight, waiting) = gate.Counts();
    var mismatch = version.PinMismatch;
    var body = new
    {
        status = mismatch ? "pin_mismatch" : "ok",
        frontend = frontend is not null,
        model = settings.Model.BaseUrl,
        pinned = version.Pin is not null && !mismatch, // a pin in force: false once a mismatch dropped it
        pin_configured = version.Pin is not null,
        pin_mismatch = mismatch,
        hash = new { pin = version.Pin, live = version.Live, keyed = version.Known, error = version.Error },
        limits = new
        {
            window = new { permit = settings.Limits.PermitPerWindow, seconds = settings.Limits.WindowSeconds },
            model = new { concurrent = Math.Max(1, settings.Limits.ConcurrentModelRequests), queue = settings.Limits.ModelQueue, in_flight = inFlight, waiting },
            shares_per_hour = settings.Limits.SharesPerHour,
            query_bytes = settings.Limits.QueryBytes,
        },
        jobs = new { queued, running, concurrent = settings.Limits.ConcurrentGenerates, queue = settings.Limits.GenerateQueue },
        shares = shares.Kind,
        results = results.Kind,
    };
    // A pin the live model contradicts is a deployment to correct: the gateway still serves, keyed on the live hash.
    return Results.Json(body, statusCode: mismatch ? StatusCodes.Status503ServiceUnavailable : StatusCodes.Status200OK);
});

app.MapJobs();
app.MapShares();

// Everything else under /api is the model's (YARP), cached by path, query and the model's hash. A template's bundled
// answer comes from the model too: it answers a bundled request before any handler (S72).
app.MapReverseProxy().CacheOutput(ModelCachePolicy.Name);

// The SPA fallback: any other path without a file extension is the frontend's router, when a frontend is present.
// It never answers /assets/ or /api/: a missing asset is a 404, not index.html (S74, G-7).
if (frontend is not null)
{
    var index = files!.FileProvider!.GetFileInfo("index.html");
    app.MapFallback(async context =>
    {
        var path = ModelRoutes.Normalize(context.Request.Path);
        if (!index.Exists || path.StartsWith("/assets/", StringComparison.Ordinal) || path == "/assets" || ModelRoutes.IsApi(path))
        {
            context.Response.StatusCode = StatusCodes.Status404NotFound;
            return;
        }
        context.Response.ContentType = "text/html; charset=utf-8";
        context.Response.Headers.CacheControl = StaticRoots.Revalidate;
        await context.Response.SendFileAsync(index, context.RequestAborted);
    });
}

app.Run();

static string Client(HttpContext context) => context.Connection.RemoteIpAddress?.ToString() ?? "unknown";

// WebApplicationFactory<Program> needs the entry point to be visible to the test project.
public partial class Program;
