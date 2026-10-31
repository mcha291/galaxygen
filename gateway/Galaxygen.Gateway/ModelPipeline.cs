using System.Threading.RateLimiting;
using Microsoft.Extensions.Options;

namespace Galaxygen.Gateway;

/// <summary>
/// One expensive request at the model at a time (S74, D-5; BUILD_IV §2c "Limits"): the proxied /api routes that take
/// a galaxy's inputs, the share links' misses and the jobs all hold a permit of this one limiter while the model
/// computes. Limits:ConcurrentModelRequests in flight (1), Limits:ModelQueue waiting oldest first (64), and past
/// that a 429 with Retry-After.
/// </summary>
public sealed class ModelGate : IDisposable
{
    /// <summary>What a refused request is told to wait, seconds.</summary>
    public const int RetryAfterSeconds = 5;

    private readonly ConcurrencyLimiter _limiter;
    private readonly int _permits;

    public ModelGate(IOptions<GatewayOptions> options)
    {
        var limits = options.Value.Limits;
        _permits = Math.Max(1, limits.ConcurrentModelRequests);
        _limiter = new ConcurrencyLimiter(new ConcurrencyLimiterOptions
        {
            PermitLimit = _permits,
            QueueLimit = Math.Max(0, limits.ModelQueue),
            QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
        });
    }

    public ValueTask<RateLimitLease> AcquireAsync(CancellationToken cancel) => _limiter.AcquireAsync(1, cancel);

    /// <summary>Requests computing at the model now, and requests waiting for it.</summary>
    public (long InFlight, long Queued) Counts()
    {
        var statistics = _limiter.GetStatistics();
        return statistics is null ? (0, 0) : (_permits - statistics.CurrentAvailablePermits, statistics.CurrentQueuedCount);
    }

    /// <summary>The 429 a request past the queue gets.</summary>
    public static IResult Refusal() => new Refused();

    private sealed class Refused : IResult
    {
        public Task ExecuteAsync(HttpContext context)
        {
            context.Response.Headers.RetryAfter = RetryAfterSeconds.ToString();
            return Results.Problem("the model is busy and its queue is full; try again shortly",
                statusCode: StatusCodes.Status429TooManyRequests).ExecuteAsync(context);
        }
    }

    public void Dispose() => _limiter.Dispose();
}

/// <summary>
/// The middleware around the proxied /api routes, in the order Program.cs places them:
/// <see cref="Label"/> before the output cache, so a replay is told apart from an answer the model computed;
/// the output cache, which answers a hit before anything below runs (a hit is never counted, never queued);
/// the sliding window (<see cref="Counted"/>); then <see cref="Bound"/>, which reads the viewer's /api/version as
/// it passes, checks a pin before a request reaches the model, and queues the input-taking routes at the
/// <see cref="ModelGate"/>.
/// </summary>
public static class ModelPipeline
{
    /// <summary>Set on a request that went past the output cache, toward the model.</summary>
    private const string Reached = "galaxygen.reached-model";

    /// <summary>X-Gateway-Cache on /api: "hit" on the output cache's replay, with X-Galaxy-Stages emptied (no stage
    /// ran for it, rule D4), "miss" on an answer from the model. The cache stores the headers before this runs, and a
    /// replay carries the Age header the cache adds; the model never sends one.</summary>
    public static async Task Label(HttpContext context, RequestDelegate next)
    {
        if (ModelRoutes.IsApi(ModelRoutes.Normalize(context.Request.Path)))
        {
            context.Response.OnStarting(() =>
            {
                var headers = context.Response.Headers;
                if (context.Items.ContainsKey(Reached))
                {
                    headers[ModelResult.CacheHeader] = ModelResult.Miss;
                }
                else if (headers.Age.Count > 0)
                {
                    headers[ModelResult.CacheHeader] = ModelResult.Hit;
                    headers[ModelRoutes.StagesHeader] = "";
                }
                // Every /api answer varies by the accepted encoding (S76's review, G2: the cache stores one body per
                // encoding), the identity one too - the compression says so only on the bodies it compresses.
                if (!headers.Vary.Any(v => v is not null && v.Contains(ModelCachePolicy.EncodingHeader, StringComparison.OrdinalIgnoreCase)))
                {
                    headers.Append(Microsoft.Net.Http.Headers.HeaderNames.Vary, ModelCachePolicy.EncodingHeader);
                }
                return Task.CompletedTask;
            });
        }
        await next(context);
    }

    /// <summary>Whether a request counts against the sliding window: only one that may reach the model (S74, G-8) -
    /// /api past the output cache, POST /jobs, and a share link's route. The page, its files, the SPA fallback, the
    /// health routes, a job's state and a share's record are free; creating a share has its own hourly window.</summary>
    public static bool Counted(HttpContext context)
    {
        var path = ModelRoutes.Normalize(context.Request.Path);
        if (ModelRoutes.IsApi(path)) return true;
        if (path == "/jobs") return HttpMethods.IsPost(context.Request.Method);
        return path.StartsWith("/share/", StringComparison.Ordinal) && path.Count(c => c == '/') == 3;
    }

    /// <summary>Behind the output cache and the window, for /api: what reaches the model.</summary>
    public static async Task Bound(HttpContext context, RequestDelegate next)
    {
        var path = ModelRoutes.Normalize(context.Request.Path);
        if (!ModelRoutes.IsApi(path))
        {
            await next(context);
            return;
        }
        context.Items[Reached] = true;
        var version = context.RequestServices.GetRequiredService<ModelVersion>();

        if (path == "/api/version" && HttpMethods.IsGet(context.Request.Method))
        {
            await Observe(context, next, version);
            return;
        }

        await version.VerifyAsync(context.RequestAborted);
        if (ModelRoutes.ApiRoute(path) is { } route && ModelRoutes.Generating.Contains(route))
        {
            var gate = context.RequestServices.GetRequiredService<ModelGate>();
            using var lease = await gate.AcquireAsync(context.RequestAborted);
            if (!lease.IsAcquired)
            {
                await ModelGate.Refusal().ExecuteAsync(context);
                return;
            }
            await next(context);
            return;
        }
        await next(context);
    }

    /// <summary>The viewer's /api/version passes through unchanged (rule D3 at this boundary) and the gateway reads it
    /// on the way: the live hash, and the pin's comparison (S74, D-2).</summary>
    private static async Task Observe(HttpContext context, RequestDelegate next, ModelVersion version)
    {
        var original = context.Response.Body;
        using var buffer = new MemoryStream();
        context.Response.Body = buffer;
        try
        {
            await next(context);
        }
        finally
        {
            context.Response.Body = original;
        }
        if (context.Response.StatusCode == StatusCodes.Status200OK)
        {
            version.TryObserve(buffer.GetBuffer().AsSpan(0, (int)buffer.Length));
        }
        buffer.Position = 0;
        await buffer.CopyToAsync(original, context.RequestAborted);
    }
}
