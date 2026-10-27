using Microsoft.AspNetCore.OutputCaching;
using Microsoft.Extensions.Options;

namespace Galaxygen.Gateway;

/// <summary>
/// Output caching for what the model publishes under /api (BUILD_IV §2c, "Caching"). A key is the path, every
/// query parameter and the model's content hash, so the same galaxy asked twice is answered once, and a redeploy
/// that changes the model changes every key. A key without the hash is a bug this policy cannot express: when the
/// hash cannot be read, nothing is looked up and nothing is stored (rule D3 as amended).
/// </summary>
public sealed class ModelCachePolicy : IOutputCachePolicy
{
    public const string Name = "model";

    /// <summary>The vary-by value the hash travels in; a test reads it.</summary>
    public const string HashKey = "model-hash";

    /// <summary>Never cached: the hash itself (recomputed per request at the model, D3) and the route table.</summary>
    public static readonly IReadOnlySet<string> Uncached = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "/api", "/api/", "/api/version" };

    async ValueTask IOutputCachePolicy.CacheRequestAsync(OutputCacheContext context, CancellationToken cancel)
    {
        var request = context.HttpContext.Request;
        var cacheable = (HttpMethods.IsGet(request.Method) || HttpMethods.IsHead(request.Method))
            && !Uncached.Contains(request.Path.Value ?? "");

        context.EnableOutputCaching = true;
        context.AllowCacheLookup = false;
        context.AllowCacheStorage = false;
        context.AllowLocking = true;
        if (!cacheable) return;

        string hash;
        try
        {
            hash = await context.HttpContext.RequestServices.GetRequiredService<ModelVersion>().CurrentAsync(cancel);
        }
        catch (Exception) when (!cancel.IsCancellationRequested) // unreachable, timed out, circuit open, or no hash published
        {
            return; // no hash, no key: the request goes to the model uncached
        }

        Vary(context, hash);
        var options = context.HttpContext.RequestServices.GetRequiredService<IOptions<GatewayOptions>>().Value;
        context.ResponseExpirationTimeSpan = TimeSpan.FromMinutes(options.Cache.ExpirationMinutes);
        context.AllowCacheLookup = true;
        context.AllowCacheStorage = true;
    }

    /// <summary>What goes into the key: every query parameter and the hash.</summary>
    public static void Vary(OutputCacheContext context, string hash)
    {
        context.CacheVaryByRules.QueryKeys = "*";
        context.CacheVaryByRules.VaryByValues[HashKey] = hash;
        context.Tags.Add(hash);
    }

    ValueTask IOutputCachePolicy.ServeFromCacheAsync(OutputCacheContext context, CancellationToken cancel) => ValueTask.CompletedTask;

    ValueTask IOutputCachePolicy.ServeResponseAsync(OutputCacheContext context, CancellationToken cancel)
    {
        // Only a whole success is kept: an error, a partial answer or one that sets a cookie is the model's to repeat.
        var response = context.HttpContext.Response;
        if (response.StatusCode != StatusCodes.Status200OK || response.Headers.SetCookie.Count > 0)
        {
            context.AllowCacheStorage = false;
        }
        return ValueTask.CompletedTask;
    }
}

/// <summary>The key of a stored model answer (a share link's warm copy): the hash first, so a store can be listed
/// or cleared by model version, then the share id, the route and the digest of the whole query.</summary>
public static class ResultKey
{
    public static string For(string hash, string shareId, string route, GalaxyQuery query) =>
        $"{hash}/{shareId}/{route}/{query.Digest(18)}";
}
