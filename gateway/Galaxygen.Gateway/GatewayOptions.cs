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
    public PathOptions Bundles { get; set; } = new();
}

/// <summary>Where the Python model answers. Under Aspire the app host sets BaseUrl from the container's endpoint.</summary>
public sealed class ModelOptions
{
    public string BaseUrl { get; set; } = "http://localhost:8017";

    /// <summary>The longest allowed model route, seconds (BUILD_IV §7 ruling 5: 120).</summary>
    public int TimeoutSeconds { get; set; } = 120;

    /// <summary>The model's content hash, pinned by a deployment so a cached answer never wakes a model at zero
    /// replicas; empty means read /api/version (rule D3 as amended).</summary>
    public string? ContentHash { get; set; }

    /// <summary>How long a hash read from /api/version is trusted, seconds; a redeployed model is seen within it.</summary>
    public int VersionSeconds { get; set; } = 30;
}

/// <summary>BUILD_IV §7 ruling 5: 60 requests a minute per client; one generate at a time with a queue of 10.</summary>
public sealed class LimitOptions
{
    public int PermitPerWindow { get; set; } = 60;
    public int WindowSeconds { get; set; } = 60;
    public int ConcurrentGenerates { get; set; } = 1;
    public int GenerateQueue { get; set; } = 10;

    /// <summary>Share links a client may create an hour.</summary>
    public int SharesPerHour { get; set; } = 20;

    /// <summary>The largest galaxy query a job or a share link takes, bytes of its canonical form.</summary>
    public int QueryBytes { get; set; } = 16384;

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

    /// <summary>Answers kept for share links when no blob store is configured.</summary>
    public int ResultEntries { get; set; } = 200;
}

/// <summary>The edit queue: how many finished jobs are remembered for their clients to read.</summary>
public sealed class JobOptions
{
    public int Retain { get; set; } = 100;
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
