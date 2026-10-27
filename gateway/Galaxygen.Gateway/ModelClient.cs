using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Options;

namespace Galaxygen.Gateway;

/// <summary>
/// The model's routes as the gateway knows them, from the API's own table (model/galaxy/api/service.py, ROUTES).
/// A name not here is not one the gateway will run on a client's behalf: an allowlist cannot be widened by accident.
/// </summary>
public static class ModelRoutes
{
    private static readonly string[] Window = ["r_min", "r_max", "phi_min", "phi_max"];

    /// <summary>
    /// Every route of the API's table but /api and /api/version, each with the parameters it declares beside the
    /// galaxy's own (<c>model</c>, <c>template</c>, <c>layer</c> and the inputs, which a share link's record holds).
    /// The routes a job or a share link runs, and the parameters a share link's URL may add (S74, G-1, G-5).
    /// </summary>
    public static readonly IReadOnlyDictionary<string, IReadOnlySet<string>> Parameters = new Dictionary<string, IReadOnlySet<string>>(StringComparer.Ordinal)
    {
        ["stages"] = Set(),
        ["fields"] = Set(),
        ["inputs"] = Set(),
        ["templates"] = Set(),
        ["arrays"] = Set("fields", "t_samples", "precision"),
        ["region"] = Set([.. Window, "stars", "brightest", "view", "level"]),
        ["system"] = Set("cell", "index", "stars", "level"),
        ["clouds"] = Set([.. Window, "level", "precision"]),
        ["clusters"] = Set([.. Window, "level", "filters", "white"]),
        ["remnants"] = Set([.. Window, "level"]),
        ["bright"] = Set([.. Window, "view", "n", "l_min", "precision", "filters", "white", "cells", "table", "level"]),
        ["blackbody"] = Set("filters", "white"),
        ["render"] = Set([.. Window, "filters", "set", "white", "level", "precision", "l_min", "only"]),
        ["layer"] = Set(),
    };

    /// <summary>The route names a job or a share link runs: the keys of <see cref="Parameters"/>.</summary>
    public static readonly IReadOnlySet<string> Galaxy = new HashSet<string>(Parameters.Keys, StringComparer.Ordinal);

    /// <summary>The routes that take a galaxy's inputs and compute: one at a time at the model (S74, D-5). The metadata
    /// routes (/api, version, stages, fields, inputs, templates, blackbody) are not among them.</summary>
    public static readonly IReadOnlySet<string> Generating = new HashSet<string>(StringComparer.Ordinal)
    {
        "arrays", "region", "system", "clouds", "clusters", "remnants", "bright", "render", "layer",
    };

    /// <summary>The headers the model sends with every answer (model/galaxy/api/http.py), passed on wherever its bytes
    /// are: the stages it ran (rule D4), where the answer came from (bundle or model, S72), and no-store.</summary>
    public const string StagesHeader = "X-Galaxy-Stages";
    public const string SourceHeader = "X-Galaxy-Source";

    /// <summary>A request path as the model reads it: no trailing slash, and the root as "/" (S74, D-4). Every route
    /// comparison in the gateway is made on this form.</summary>
    public static string Normalize(PathString path)
    {
        var value = (path.Value ?? "").TrimEnd('/');
        return value.Length == 0 ? "/" : value;
    }

    /// <summary>The route name of an /api/{name} path (normalised), or null for anything else, /api itself included.</summary>
    public static string? ApiRoute(string normalized) =>
        normalized.StartsWith("/api/", StringComparison.Ordinal) && normalized.IndexOf('/', 5) < 0 ? normalized[5..] : null;

    /// <summary>Whether a normalised path is under the model's /api.</summary>
    public static bool IsApi(string normalized) =>
        normalized == "/api" || normalized.StartsWith("/api/", StringComparison.Ordinal);

    private static HashSet<string> Set(params string[] names) => new(names, StringComparer.Ordinal);
}

/// <summary>One answer from the model, held whole: what a job stores and a share link caches, with the model's
/// headers as it sent them.</summary>
public sealed record ModelResult(int Status, string ContentType, string? Stages, byte[] Body, string? Source = null, string? CacheControl = null)
{
    public bool Ok => Status is >= 200 and < 300;

    /// <summary>Written back as the model sent it. <paramref name="cache"/> says where it came from: on "hit" no stage
    /// ran for this request, so X-Galaxy-Stages is empty (rule D4: the header is the transport's truth).</summary>
    public IResult ToHttp(string? cache = null) => new Written(this, cache);

    private sealed class Written(ModelResult result, string? cache) : IResult
    {
        public async Task ExecuteAsync(HttpContext context)
        {
            var response = context.Response;
            response.StatusCode = result.Status;
            response.ContentType = result.ContentType;
            response.ContentLength = result.Body.Length;
            if (cache == Hit) response.Headers[ModelRoutes.StagesHeader] = "";
            else if (result.Stages is not null) response.Headers[ModelRoutes.StagesHeader] = result.Stages;
            if (result.Source is not null) response.Headers[ModelRoutes.SourceHeader] = result.Source;
            if (result.CacheControl is not null) response.Headers.CacheControl = result.CacheControl;
            if (cache is not null) response.Headers[CacheHeader] = cache;
            await response.Body.WriteAsync(result.Body, context.RequestAborted);
        }
    }

    /// <summary>"hit" or "miss" on a response the gateway answered from a store of its own or filled one with.</summary>
    public const string CacheHeader = "X-Gateway-Cache";
    public const string Hit = "hit";
    public const string Miss = "miss";
}

/// <summary>The model's address and the one way the gateway's own code asks it something.</summary>
public sealed class ModelClient(HttpClient http, IOptions<GatewayOptions> options)
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
        var type = response.Content.Headers.ContentType?.ToString() ?? "application/octet-stream";
        return new ModelResult((int)response.StatusCode, type, Header(response, ModelRoutes.StagesHeader), body,
            Header(response, ModelRoutes.SourceHeader), response.Headers.CacheControl?.ToString());
    }

    /// <summary>/api/version's body, on its own short timeout (Model:VersionTimeoutSeconds) and never retried.</summary>
    public async Task<JsonElement> ReadVersionAsync(CancellationToken cancel)
    {
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancel);
        timeout.CancelAfter(TimeSpan.FromSeconds(options.Value.Model.VersionTimeoutSeconds));
        using var response = await http.GetAsync("/api/version", timeout.Token);
        response.EnsureSuccessStatusCode();
        await using var stream = await response.Content.ReadAsStreamAsync(timeout.Token);
        using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: timeout.Token);
        return doc.RootElement.Clone();
    }

    private static string? Header(HttpResponseMessage response, string name) =>
        response.Headers.TryGetValues(name, out var values) ? string.Join(",", values) : null;
}

/// <summary>
/// The model's content hash, which every cache key in the gateway carries (rule D3 as amended by BUILD_IV
/// Appendix A; D5's last sentence): /api/version's <c>model.hash</c>, the hash of every byte under model/galaxy, so a
/// stage, a constant or a data file that changes moves it (the <c>api</c> hash is a subset, the <c>viewer</c>'s another
/// thing). A version without it is refused: the gateway requires the S72+ API, and keys nothing until it reads one.
///
/// A deployment may pin the hash (Model:ContentHash) so that a request answered from a cache never wakes a model
/// scaled to zero. The pin is checked against every /api/version the gateway reads: the viewer's own reads passing
/// through, and one read before a request reaches the model, at most once per Model:VersionSeconds. On a mismatch the
/// gateway logs an error, drops the pin and keys on the live hash from then on; /healthz answers 503 (S74, D-2).
/// Without a pin the hash is read from /api/version and kept for Model:VersionSeconds.
/// </summary>
public sealed class ModelVersion(IServiceProvider services, IOptions<GatewayOptions> options, TimeProvider clock, ILogger<ModelVersion> log)
{
    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly Lock _lock = new();
    private string? _live;
    private DateTimeOffset _read = DateTimeOffset.MinValue;
    private DateTimeOffset _checked = DateTimeOffset.MinValue;
    private bool _mismatch;
    private string? _error;

    /// <summary>The key from /api/version's body: <c>model.hash</c>, alone.</summary>
    public static string Compose(JsonElement version)
    {
        if (version.ValueKind == JsonValueKind.Object
            && version.TryGetProperty("model", out var model) && model.ValueKind == JsonValueKind.Object
            && model.TryGetProperty("hash", out var hash) && hash.ValueKind == JsonValueKind.String
            && hash.GetString() is { Length: > 0 } value)
        {
            return value;
        }
        throw new FormatException("/api/version published no model.hash: the gateway requires the S72+ API, whose model hash keys every cache");
    }

    /// <summary>The configured pin, or null.</summary>
    public string? Pin => string.IsNullOrWhiteSpace(options.Value.Model.ContentHash) ? null : options.Value.Model.ContentHash.Trim();

    /// <summary>The pin was found to differ from the model's live hash, and is no longer used.</summary>
    public bool PinMismatch { get { lock (_lock) return _mismatch; } }

    /// <summary>The model's hash as last read from /api/version, or null.</summary>
    public string? Live { get { lock (_lock) return _live; } }

    /// <summary>Why the last read of /api/version was refused, or null after a good one.</summary>
    public string? Error { get { lock (_lock) return _error; } }

    /// <summary>The hash the gateway keys on now, known without asking the model: the pin while it holds, else the
    /// last hash read (however old), else null.</summary>
    public string? Known
    {
        get
        {
            var pin = Pin;
            lock (_lock) return pin is not null && !_mismatch ? pin : _live;
        }
    }

    private bool PinHolds(out string pin)
    {
        var configured = Pin;
        pin = configured ?? "";
        lock (_lock) return configured is not null && !_mismatch;
    }

    private string? Fresh()
    {
        var ttl = TimeSpan.FromSeconds(options.Value.Model.VersionSeconds);
        lock (_lock) return _live is { } live && clock.GetUtcNow() - _read < ttl ? live : null;
    }

    /// <summary>The hash every key is made with now: the pin while it holds, else the live hash, read when the last
    /// read is older than Model:VersionSeconds. Throws when it cannot be read: then nothing may be cached.</summary>
    public async ValueTask<string> CurrentAsync(CancellationToken cancel)
    {
        if (PinHolds(out var pin)) return pin;
        if (Fresh() is { } fresh) return fresh;
        return await ReadAsync(() => PinHolds(out var p) ? p : Fresh(), cancel);
    }

    /// <summary>With a pin, compares it with the live hash when the last comparison is older than
    /// Model:VersionSeconds; called where a request is about to reach the model anyway. Never throws: a model that
    /// cannot be read is the request's own failure to find, and the pin stands until a read contradicts it.</summary>
    public async Task VerifyAsync(CancellationToken cancel)
    {
        if (!PinHolds(out _)) return;
        var period = TimeSpan.FromSeconds(options.Value.Model.VersionSeconds);
        lock (_lock) if (_checked != DateTimeOffset.MinValue && clock.GetUtcNow() - _checked < period) return;
        try
        {
            await ReadAsync(() =>
            {
                if (!PinHolds(out _)) return "";
                lock (_lock) return _checked != DateTimeOffset.MinValue && clock.GetUtcNow() - _checked < period ? "" : null;
            }, cancel);
        }
        catch (Exception e) when (!cancel.IsCancellationRequested)
        {
            log.LogWarning("the pinned model hash could not be checked: {Error}", e.Message);
        }
    }

    /// <summary>One read of /api/version at a time, the wait and the read each bounded by
    /// Model:VersionTimeoutSeconds; <paramref name="settled"/> returns a hash when another caller's read made this one
    /// unnecessary.</summary>
    private async Task<string> ReadAsync(Func<string?> settled, CancellationToken cancel)
    {
        var wait = TimeSpan.FromSeconds(options.Value.Model.VersionTimeoutSeconds);
        if (!await _gate.WaitAsync(wait, cancel)) throw new TimeoutException("a read of /api/version already under way did not finish in time");
        try
        {
            if (settled() is { } done) return done;
            var json = await services.GetRequiredService<ModelClient>().ReadVersionAsync(cancel);
            return Observe(json);
        }
        finally
        {
            _gate.Release();
        }
    }

    /// <summary>Takes in an /api/version body the gateway saw (its own read, or the viewer's passing through): the live
    /// hash, and the pin's comparison. A body without <c>model.hash</c> is refused with a logged error and changes
    /// nothing. Returns the hash the gateway keys on after it.</summary>
    public string Observe(JsonElement version)
    {
        string hash;
        try
        {
            hash = Compose(version);
        }
        catch (FormatException e)
        {
            lock (_lock) _error = e.Message;
            log.LogError("{Error}", e.Message);
            throw;
        }

        var pin = Pin;
        lock (_lock)
        {
            _live = hash;
            _read = clock.GetUtcNow();
            _error = null;
            if (pin is null || _mismatch) return hash;
            if (pin == hash)
            {
                _checked = _read;
                return pin;
            }
            _mismatch = true;
        }
        log.LogError("the pinned model hash {Pin} is not the live model's {Live}: the pin is dropped and every key is made " +
            "with the live hash from now on; /healthz answers 503 until the deployment is corrected", pin, hash);
        return hash;
    }

    /// <summary><see cref="Observe(JsonElement)"/> on raw bytes, for the viewer's reads passing through; never throws.</summary>
    public void TryObserve(ReadOnlySpan<byte> body)
    {
        try
        {
            var reader = new Utf8JsonReader(body);
            using var doc = JsonDocument.ParseValue(ref reader);
            Observe(doc.RootElement);
        }
        catch (Exception e) when (e is JsonException or FormatException)
        {
            if (e is JsonException) log.LogWarning("an /api/version passing through was not JSON: {Error}", e.Message);
        }
    }
}
