namespace Galaxygen.Gateway;

/// <summary>Resolves a configured static-file directory; null when unset or absent, so a developer's machine
/// without a frontend build still starts the gateway for the API routes. And the frontend's cache headers.</summary>
public static class StaticRoots
{
    /// <summary>Vite's /assets/ files: their names carry their content hash, so a changed file is a new URL.</summary>
    public const string Immutable = "public, max-age=31536000, immutable";

    /// <summary>Everything else (index.html above all, which names the current assets): revalidated on every load.</summary>
    public const string Revalidate = "no-cache";

    public static string CacheControl(PathString path) =>
        ModelRoutes.Normalize(path).StartsWith("/assets/", StringComparison.Ordinal) ? Immutable : Revalidate;

    public static string? Resolve(IHostEnvironment environment, string? configured)
    {
        if (string.IsNullOrWhiteSpace(configured)) return null;
        var path = Path.IsPathRooted(configured) ? configured : Path.GetFullPath(configured, environment.ContentRootPath);
        return Directory.Exists(path) ? path : null;
    }
}
