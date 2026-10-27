using System.Collections.Concurrent;
using System.Text.Json;
using Azure;
using Azure.Data.Tables;
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Microsoft.Extensions.Options;

namespace Galaxygen.Gateway;

// Share links (BUILD_IV §2c, ruling 4 (a)): a galaxy is its template, its inputs and its seeds, a few hundred bytes
// of query. A link is a short id over that record; there are no accounts, so a link is a capability, and creating
// one is limited per client. The id is the query's own digest, so sharing the same galaxy twice gives the same link.
// The model's answers for a shared galaxy are kept beside the record under the content hash, so a link opens warm
// on its second load and a redeploy of the model makes it compute again rather than serve the old physics.

public sealed record ShareRequest(Dictionary<string, JsonElement>? Query);

/// <summary>A stored share: the canonical query, and the model hash it was shared under (for the record only).</summary>
public sealed record ShareRecord(string Id, string Query, string? Hash, DateTimeOffset Created)
{
    public object View() => new { id = Id, url = $"/share/{Id}", query = GalaxyQuery.Parse(Query).Pairs, hash = Hash, created = Created };
}

public interface IShareStore
{
    string Kind { get; }
    Task<ShareRecord?> GetAsync(string id, CancellationToken cancel);
    Task PutAsync(ShareRecord record, CancellationToken cancel);
}

public interface IResultStore
{
    string Kind { get; }
    Task<ModelResult?> GetAsync(string key, CancellationToken cancel);
    Task PutAsync(string key, ModelResult result, CancellationToken cancel);
}

/// <summary>Shares in the gateway's memory: a developer's machine, the tests. Lost on restart.</summary>
public sealed class MemoryShareStore : IShareStore
{
    private readonly ConcurrentDictionary<string, ShareRecord> _records = new(StringComparer.Ordinal);
    public string Kind => "memory";
    public Task<ShareRecord?> GetAsync(string id, CancellationToken cancel) => Task.FromResult(_records.GetValueOrDefault(id));

    public Task PutAsync(ShareRecord record, CancellationToken cancel)
    {
        _records.TryAdd(record.Id, record); // the first sharing's record stands; the same id is the same query
        return Task.CompletedTask;
    }
}

/// <summary>Answers in the gateway's memory, at most Cache:ResultEntries of them and Cache:ResultMegabytes of bytes
/// (S74, G-1), the oldest dropped first; an answer larger than the whole bound is not kept.</summary>
public sealed class MemoryResultStore(IOptions<GatewayOptions> options) : IResultStore
{
    private readonly Dictionary<string, ModelResult> _results = new(StringComparer.Ordinal);
    private readonly Queue<string> _order = new();
    private readonly Lock _lock = new();
    private long _bytes;
    public string Kind => "memory";

    /// <summary>Bytes of answers held now.</summary>
    public long Bytes { get { lock (_lock) return _bytes; } }

    public Task<ModelResult?> GetAsync(string key, CancellationToken cancel)
    {
        lock (_lock) return Task.FromResult(_results.GetValueOrDefault(key));
    }

    public Task PutAsync(string key, ModelResult result, CancellationToken cancel)
    {
        var cache = options.Value.Cache;
        var limit = cache.ResultMegabytes * 1024L * 1024L;
        if (result.Body.Length > limit) return Task.CompletedTask;
        lock (_lock)
        {
            if (!_results.TryAdd(key, result)) return Task.CompletedTask; // a repeat neither replaces nor counts twice
            _order.Enqueue(key);
            _bytes += result.Body.Length;
            while ((_results.Count > cache.ResultEntries || _bytes > limit) && _order.TryDequeue(out var oldest))
            {
                if (_results.Remove(oldest, out var dropped)) _bytes -= dropped.Body.Length;
            }
        }
        return Task.CompletedTask;
    }
}

/// <summary>Shares in Azure Table Storage: one table, one partition, the id as the row key.</summary>
public sealed class TableShareStore(TableServiceClient service) : IShareStore
{
    public const string Table = "shares";
    private const string Partition = "share";
    private readonly Lazy<Task<TableClient>> _table = new(async () =>
    {
        var table = service.GetTableClient(Table);
        await table.CreateIfNotExistsAsync();
        return table;
    });

    public string Kind => "azure-table";

    public async Task<ShareRecord?> GetAsync(string id, CancellationToken cancel)
    {
        var table = await _table.Value;
        var got = await table.GetEntityIfExistsAsync<TableEntity>(Partition, id, cancellationToken: cancel);
        if (!got.HasValue || got.Value is not { } entity) return null;
        return new ShareRecord(id, entity.GetString("Query") ?? "", entity.GetString("Hash"),
            entity.GetDateTimeOffset("Created") ?? DateTimeOffset.MinValue);
    }

    public async Task PutAsync(ShareRecord record, CancellationToken cancel)
    {
        var table = await _table.Value;
        var entity = new TableEntity(Partition, record.Id)
        {
            ["Query"] = record.Query,
            ["Hash"] = record.Hash,
            ["Created"] = record.Created,
        };
        try
        {
            await table.AddEntityAsync(entity, cancel);
        }
        catch (RequestFailedException e) when (e.Status == 409)
        {
            // Shared before: the same id is the same query, and the first record stands.
        }
    }
}

/// <summary>Answers in Azure Blob Storage, one blob per key; the status and the model's headers ride in the blob's
/// metadata. Nothing here deletes a blob: the container's lifecycle rule (a TTL) is W4's, set on the storage account.</summary>
public sealed class BlobResultStore(BlobServiceClient service) : IResultStore
{
    public const string Container = "results";
    private readonly Lazy<Task<BlobContainerClient>> _container = new(async () =>
    {
        var container = service.GetBlobContainerClient(Container);
        await container.CreateIfNotExistsAsync();
        return container;
    });

    public string Kind => "azure-blob";

    public async Task<ModelResult?> GetAsync(string key, CancellationToken cancel)
    {
        var container = await _container.Value;
        try
        {
            var got = (await container.GetBlobClient(key).DownloadContentAsync(cancel)).Value;
            var meta = got.Details.Metadata;
            var status = meta.TryGetValue("status", out var s) && int.TryParse(s, out var n) ? n : 200;
            string? Meta(string name) => meta.TryGetValue(name, out var value) ? value : null;
            return new ModelResult(status, got.Details.ContentType, Meta("stages"), got.Content.ToArray(), Meta("source"), Meta("cachecontrol"));
        }
        catch (RequestFailedException e) when (e.Status == 404)
        {
            return null;
        }
    }

    public async Task PutAsync(string key, ModelResult result, CancellationToken cancel)
    {
        var container = await _container.Value;
        var metadata = new Dictionary<string, string> { ["status"] = result.Status.ToString() };
        if (!string.IsNullOrEmpty(result.Stages)) metadata["stages"] = result.Stages;
        if (!string.IsNullOrEmpty(result.Source)) metadata["source"] = result.Source;
        if (!string.IsNullOrEmpty(result.CacheControl)) metadata["cachecontrol"] = result.CacheControl;
        await container.GetBlobClient(key).UploadAsync(BinaryData.FromBytes(result.Body), new BlobUploadOptions
        {
            HttpHeaders = new BlobHttpHeaders { ContentType = result.ContentType },
            Metadata = metadata,
        }, cancel);
    }
}

public static class ShareEndpoints
{
    public static RouteGroupBuilder MapShares(this IEndpointRouteBuilder app)
    {
        var share = app.MapGroup("/share");

        share.MapPost("/", async (ShareRequest? body, IShareStore store, ModelVersion version, IOptions<GatewayOptions> options,
            TimeProvider clock, CancellationToken cancel) =>
        {
            var query = GalaxyQuery.FromJson(body?.Query, options.Value.Limits.QueryBytes, out var error);
            if (query is null) return Results.Problem(error, statusCode: 400);
            if (query.Pairs.Count == 0) return Results.Problem("a share needs a query: at least the template", statusCode: 400);

            // The record's hash is for the record only; the last one read, or the pin, is taken without waiting on
            // the model (S74, G-10), and only when none is known yet is the model asked, on its short timeout.
            var hash = version.Known;
            if (hash is null)
            {
                try { hash = await version.CurrentAsync(cancel); }
                catch (Exception) when (!cancel.IsCancellationRequested) { } // the record does not need the model awake
            }

            var record = new ShareRecord(query.Digest(), query.Canonical, hash, clock.GetUtcNow());
            await store.PutAsync(record, cancel);
            var stored = await store.GetAsync(record.Id, cancel) ?? record;
            return Results.Created($"/share/{stored.Id}", stored.View());
        }).RequireRateLimiting(Policies.Share);

        share.MapGet("/{id}", async (string id, IShareStore store, CancellationToken cancel) =>
            ShareIds.Valid(id) && await store.GetAsync(id, cancel) is { } record ? Results.Ok(record.View()) : Results.NotFound());

        // A shared galaxy's model route: the record's query with the request's own parameters beneath it (the
        // record's keys win, so a link cannot be edited by its URL; any other key must be one the route itself
        // declares), answered from the store when it holds this exact query under the current hash, and from the
        // model otherwise, which then fills the store.
        share.MapGet("/{id}/{route}", async (string id, string route, HttpRequest request, IShareStore store, IResultStore results,
            ModelClient model, ModelVersion version, ModelGate gate, IOptions<GatewayOptions> options, CancellationToken cancel) =>
        {
            if (!ShareIds.Valid(id) || !ModelRoutes.Parameters.TryGetValue(route, out var own)) return Results.NotFound();
            if (await store.GetAsync(id, cancel) is not { } record) return Results.NotFound();
            var extra = GalaxyQuery.FromRequest(request.Query, options.Value.Limits.QueryBytes, out var error);
            if (extra is null) return Results.Problem(error, statusCode: 400);
            var shared = GalaxyQuery.Parse(record.Query);
            if (extra.Pairs.Keys.FirstOrDefault(k => !own.Contains(k) && !shared.Pairs.ContainsKey(k)) is { } stray)
            {
                return Results.Problem($"'{stray}' is not a parameter of /api/{route}: a shared galaxy's inputs are its record's " +
                    $"(this route takes {(own.Count == 0 ? "none" : string.Join(", ", own.Order(StringComparer.Ordinal)))})", statusCode: 400);
            }
            var query = shared.Under(extra);

            string hash;
            try { hash = await version.CurrentAsync(cancel); }
            catch (Exception) when (!cancel.IsCancellationRequested)
            {
                return Results.Problem("the model's content hash could not be read", statusCode: 503);
            }

            var key = ResultKey.For(hash, id, route, query);
            if (await results.GetAsync(key, cancel) is { } kept) return kept.ToHttp(ModelResult.Hit);

            // A miss reaches the model: an input-taking route waits for its one permit, as the viewer's own requests do.
            using var lease = ModelRoutes.Generating.Contains(route) ? await gate.AcquireAsync(cancel) : null;
            if (lease is { IsAcquired: false }) return ModelGate.Refusal();
            await version.VerifyAsync(cancel);
            try { hash = await version.CurrentAsync(cancel); }
            catch (Exception) when (!cancel.IsCancellationRequested)
            {
                return Results.Problem("the model's content hash could not be read", statusCode: 503);
            }
            key = ResultKey.For(hash, id, route, query); // a pin found wrong on the way moves the key to the live hash

            ModelResult fresh;
            try { fresh = await model.GetAsync(route, query, cancel); }
            catch (Exception) when (!cancel.IsCancellationRequested)
            {
                return Results.Problem("the model could not be reached", statusCode: 502);
            }
            if (fresh.Ok && version.Known == hash) await results.PutAsync(key, fresh, cancel);
            return fresh.ToHttp(ModelResult.Miss);
        });

        return share;
    }
}

/// <summary>A share id is the query's digest: 12 characters of base64url. Anything else is not a link, and is
/// answered 404 before any store is asked (S74, N-1: never a 500 from the Table SDK on a key it refuses).</summary>
public static partial class ShareIds
{
    [System.Text.RegularExpressions.GeneratedRegex("^[A-Za-z0-9_-]{12}$")]
    private static partial System.Text.RegularExpressions.Regex Pattern();

    public static bool Valid(string id) => Pattern().IsMatch(id);
}
