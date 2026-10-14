namespace Galaxygen.Gateway;

/// <summary>Configuration for the gateway, bound from the "Gateway" section (appsettings, environment, Aspire).</summary>
public sealed class GatewayOptions
{
    public const string Section = "Gateway";

    public ModelOptions Model { get; set; } = new();
    public LimitOptions Limits { get; set; } = new();
    public PathOptions Frontend { get; set; } = new();
    public PathOptions Bundles { get; set; } = new();
}

/// <summary>Where the Python model answers. Under Aspire the app host sets BaseUrl from the container's endpoint.</summary>
public sealed class ModelOptions
{
    public string BaseUrl { get; set; } = "http://localhost:8017";

    /// <summary>The longest allowed model route, seconds (BUILD_IV §7 ruling 5: 120).</summary>
    public int TimeoutSeconds { get; set; } = 120;
}

/// <summary>BUILD_IV §7 ruling 5: 60 requests a minute per client; one generate at a time with a queue of 10.</summary>
public sealed class LimitOptions
{
    public int PermitPerWindow { get; set; } = 60;
    public int WindowSeconds { get; set; } = 60;
    public int ConcurrentGenerates { get; set; } = 1;
    public int GenerateQueue { get; set; } = 10;
}

/// <summary>A directory of static files, relative to the content root or absolute; empty means none.</summary>
public sealed class PathOptions
{
    public string? Path { get; set; }
}

/// <summary>Named rate-limiting policies.</summary>
public static class Policies
{
    public const string Generate = "generate";
}
