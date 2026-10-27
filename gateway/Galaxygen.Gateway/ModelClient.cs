using System.Text;
using System.Text.Json;

namespace Galaxygen.Gateway;

/// <summary>
/// The model's routes the gateway itself calls (for a job or a share link) rather than proxies. A name not here is
/// not one the gateway will run on a client's behalf: an allowlist cannot be widened by accident.
/// </summary>
public static class ModelRoutes
{
    public static readonly IReadOnlySet<string> Galaxy = new HashSet<string>(StringComparer.Ordinal)
    {
        "arrays", "render", "region", "system", "clouds", "clusters", "remnants", "bright", "stages", "fields", "inputs",
    };

    /// <summary>The header the model names the stages it ran in (rule D4); passed through wherever bytes are.</summary>
    public const string StagesHeader = "x-galaxy-stages";
}

/// <summary>One answer from the model, held whole: what a job stores and a share link caches.</summary>
public sealed record ModelResult(int Status, string ContentType, string? Stages, byte[] Body)
{
    public bool Ok => Status is >= 200 and < 300;

    /// <summary>Written back exactly as the model sent it; <paramref name="cache"/> says where it came from.</summary>
    public IResult ToHttp(string? cache = null) => new Written(this, cache);

    private sealed class Written(ModelResult result, string? cache) : IResult
    {
        public async Task ExecuteAsync(HttpContext context)
        {
            context.Response.StatusCode = result.Status;
            context.Response.ContentType = result.ContentType;
            context.Response.ContentLength = result.Body.Length;
            if (result.Stages is not null) context.Response.Headers[ModelRoutes.StagesHeader] = result.Stages;
            if (cache is not null) context.Response.Headers[CacheHeader] = cache;
            await context.Response.Body.WriteAsync(result.Body, context.RequestAborted);
        }
    }

    /// <summary>"hit" or "miss" on a response the gateway answered from its own store or filled it with.</summary>
    public const string CacheHeader = "x-gateway-cache";
}

/// <summary>The model's address and the one way the gateway's own code asks it something.</summary>
public sealed class ModelClient(HttpClient http)
{
    /// <summary>As the client transport (interface/transport.js, MAX_URL): past it the query travels as a POST body.</summary>
    public const int MaxUrl = 4096;

    public async Task<ModelResult> GetAsync(string route, GalaxyQuery query, CancellationToken cancel)
    {
        var path = $"/api/{route}";
        var canonical = query.Canonical;
        using var request = canonical.Length == 0
            ? new HttpRequestMessage(HttpMethod.Get, path)
            : path.Length + 1 + canonical.Length <= MaxUrl
                ? new HttpRequestMessage(HttpMethod.Get, $"{path}?{canonical}")
                : new HttpRequestMessage(HttpMethod.Post, path)
                {
                    Content = new StringContent(canonical, Encoding.UTF8, "application/x-www-form-urlencoded"),
                };
        using var response = await http.SendAsync(request, HttpCompletionOption.ResponseContentRead, cancel);
        var body = await response.Content.ReadAsByteArrayAsync(cancel);
        var stages = response.Headers.TryGetValues(ModelRoutes.StagesHeader, out var values) ? string.Join(",", values) : null;
        var type = response.Content.Headers.ContentType?.ToString() ?? "application/octet-stream";
        return new ModelResult((int)response.StatusCode, type, stages, body);
    }

    /// <summary>/api/version's body, parsed for the two hashes it publishes (rule D3).</summary>
    public async Task<string> ContentHashAsync(CancellationToken cancel)
    {
        using var response = await http.GetAsync("/api/version", cancel);
        response.EnsureSuccessStatusCode();
        await using var stream = await response.Content.ReadAsStreamAsync(cancel);
        using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: cancel);
        return ModelVersion.Compose(doc.RootElement);
    }
}

/// <summary>
/// The model's content hash, which every cache key in the gateway carries (rule D3 as amended by BUILD_IV
/// Appendix A). A deployment pins it (Model:ContentHash, the hash the model image was built with) so that a
/// request answered from a cache never wakes a model scaled to zero; without a pin it is read from /api/version
/// and kept for Model:VersionSeconds, so a redeploy of the model is seen within that time.
/// </summary>
public sealed class ModelVersion(IServiceProvider services, Microsoft.Extensions.Options.IOptions<GatewayOptions> options, TimeProvider clock)
{
    private readonly SemaphoreSlim _gate = new(1, 1);
    private string? _hash;
    private DateTimeOffset _read = DateTimeOffset.MinValue;

    /// <summary>The key part from /api/version's body: the API's hash and the viewer's, joined.</summary>
    public static string Compose(JsonElement version)
    {
        var api = version.GetProperty("api").GetProperty("hash").GetString();
        var viewer = version.GetProperty("viewer").GetProperty("hash").GetString();
        if (string.IsNullOrEmpty(api) || string.IsNullOrEmpty(viewer)) throw new FormatException("/api/version published no hash");
        return $"{api}.{viewer}";
    }

    public async ValueTask<string> CurrentAsync(CancellationToken cancel)
    {
        var settings = options.Value.Model;
        if (!string.IsNullOrWhiteSpace(settings.ContentHash)) return settings.ContentHash;

        var ttl = TimeSpan.FromSeconds(settings.VersionSeconds);
        if (_hash is { } fresh && clock.GetUtcNow() - _read < ttl) return fresh;

        await _gate.WaitAsync(cancel);
        try
        {
            if (_hash is { } again && clock.GetUtcNow() - _read < ttl) return again;
            _hash = await services.GetRequiredService<ModelClient>().ContentHashAsync(cancel);
            _read = clock.GetUtcNow();
            return _hash;
        }
        finally
        {
            _gate.Release();
        }
    }
}
