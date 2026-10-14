namespace Galaxygen.Gateway;

/// <summary>Resolves a configured static-file directory; null when unset or absent, so a developer's machine
/// without a frontend build still starts the gateway for the API routes.</summary>
public static class StaticRoots
{
    public static string? Resolve(IHostEnvironment environment, string? configured)
    {
        if (string.IsNullOrWhiteSpace(configured)) return null;
        var path = Path.IsPathRooted(configured) ? configured : Path.GetFullPath(configured, environment.ContentRootPath);
        return Directory.Exists(path) ? path : null;
    }
}
