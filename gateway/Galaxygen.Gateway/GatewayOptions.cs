namespace Galaxygen.Gateway;

/// <summary>Configuration for the gateway, bound from the "Gateway" section (appsettings, environment, Aspire).</summary>
public sealed class GatewayOptions
{
    public const string Section = "Gateway";

    public ModelOptions Model { get; set; } = new();
    public LimitOptions Limits { get; set; } = new();
    public CacheOptions Cache { get; set; } = new();
    public JobOptions Jobs { get; set; } = new();
    public PathOptions Frontend { get; set; } = new();
}

/// <summary>Where the Python model answers. Under Aspire the app host sets BaseUrl from the container's endpoint.</summary>
public sealed class ModelOptions
{
    public string BaseUrl { get; set; } = "http://localhost:8017";

    /// <summary>The longest allowed model route, seconds (BUILD_IV §7 ruling 5: 120). It is the attempt's timeout and
    /// the whole request's: nothing sent to the model is retried (S74, D-6), so a slow route is computed once.</summary>
    public int TimeoutSeconds { get; set; } = 120;

    /// <summary>The model's content hash, /api/version's <c>model.hash</c> (32 hex characters), pinned by a deployment
    /// so a cached answer never wakes a model at zero replicas; empty means read /api/version (rule D3 as amended). A
    /// pin is checked against every /api/version the gateway reads; on a mismatch it is dropped (S74, D-2).</summary>
    public string? ContentHash { get; set; }

    /// <summary>How long a hash read from /api/version is trusted, seconds; a redeployed model is seen within it. With a
    /// pin, how often a request that reaches the model checks the pin against the live hash.</summary>
    public int VersionSeconds { get; set; } = 30;

    /// <summary>The one timeout of a read of /api/version, seconds, waiting included; never retried (S74, D-6, G-10).</summary>
    public int VersionTimeoutSeconds { get; set; } = 10;
}

/// <summary>BUILD_IV §7 ruling 5: 60 requests a minute per client; one generate at a time.</summary>
public sealed class LimitOptions
{
    /// <summary>The sliding window per client. It counts only requests that may reach the model (S74, G-8).</summary>
    public int PermitPerWindow { get; set; } = 60;
    public int WindowSeconds { get; set; } = 60;

    /// <summary>Requests computing at the model at once, over the proxied input-taking /api routes, the share links'
    /// misses and the jobs together (S74, D-5): one model replica runs one expensive request at a time.</summary>
    public int ConcurrentModelRequests { get; set; } = 1;

    /// <summary>Requests waiting for the model, oldest first; past it a request is 429 with Retry-After (S74, D-5).</summary>
    public int ModelQueue { get; set; } = 64;

    /// <summary>The edit queue (/jobs): jobs run at once, jobs waiting; past that POST /jobs is 429.</summary>
    public int ConcurrentGenerates { get; set; } = 1;
    public int GenerateQueue { get; set; } = 10;

    /// <summary>Share links a client may create an hour.</summary>
    public int SharesPerHour { get; set; } = 20;

    /// <summary>The largest galaxy query a job or a share link takes, bytes of its canonical form: an eighth of the API's
    /// MAX_BODY, room for the viewer's sampled filter curves (S74, G-4).</summary>
    public int QueryBytes { get; set; } = 131072;

    /// <summary>Take the client's address from X-Forwarded-For (the last hop's entry). On only behind an ingress that
    /// sets it, as Container Apps' does: otherwise every client shares the ingress's address, or can forge its own.</summary>
    public bool TrustForwardedFor { get; set; }
}

/// <summary>Output caching of the model's answers and the share links' warm copies.</summary>
public sealed class CacheOptions
{
    public int SizeMegabytes { get; set; } = 256;
    public int EntryMegabytes { get; set; } = 64;
    public int ExpirationMinutes { get; set; } = 60;

    /// <summary>Answers kept for share links when no blob store is configured: at most this many...</summary>
    public int ResultEntries { get; set; } = 200;

    /// <summary>...and at most this many megabytes of them (S74, G-1).</summary>
    public int ResultMegabytes { get; set; } = 64;
}

/// <summary>The edit queue: what finished jobs are remembered for their clients to read.</summary>
public sealed class JobOptions
{
    /// <summary>Finished jobs remembered, the oldest finished forgotten first.</summary>
    public int Retain { get; set; } = 100;

    /// <summary>Megabytes of finished jobs' results held; past it the oldest finished are forgotten (S74, G-2).</summary>
    public int ResultMegabytes { get; set; } = 64;
}

/// <summary>A directory of static files, relative to the content root or absolute; empty means none.</summary>
public sealed class PathOptions
{
    public string? Path { get; set; }
}

/// <summary>Named rate-limiting policies.</summary>
public static class Policies
{
    public const string Share = "share";
}
