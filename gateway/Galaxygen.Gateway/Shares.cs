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

/// <summary>Answers in the gateway's memory, at most Cache:ResultEntries of them, the oldest dropped first.</summary>
public sealed class MemoryResultStore(IOptions<GatewayOptions> options) : IResultStore
{
    private readonly ConcurrentDictionary<string, ModelResult> _results = new(StringComparer.Ordinal);
    private readonly ConcurrentQueue<string> _order = new();
    public string Kind => "memory";
    public Task<ModelResult?> GetAsync(string key, CancellationToken cancel) => Task.FromResult(_results.GetValueOrDefault(key));

    public Task PutAsync(string key, ModelResult result, CancellationToken cancel)
    {
        if (_results.TryAdd(key, result)) _order.Enqueue(key);
        while (_results.Count > options.Value.Cache.ResultEntries && _order.TryDequeue(out var oldest)) _results.TryRemove(oldest, out _);
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

/// <summary>Answers in Azure Blob Storage, one blob per key; the status and stages ride in the blob's metadata.</summary>
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
            return new ModelResult(status, got.Details.ContentType, meta.TryGetValue("stages", out var stages) ? stages : null, got.Content.ToArray());
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
        if (result.Stages is not null) metadata["stages"] = result.Stages;
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

            string? hash = null;
            try { hash = await version.CurrentAsync(cancel); }
            catch (Exception) when (!cancel.IsCancellationRequested) { } // the record does not need the model awake

            var record = new ShareRecord(query.Digest(), query.Canonical, hash, clock.GetUtcNow());
            await store.PutAsync(record, cancel);
            var stored = await store.GetAsync(record.Id, cancel) ?? record;
            return Results.Created($"/share/{stored.Id}", stored.View());
        }).RequireRateLimiting(Policies.Share);

        share.MapGet("/{id}", async (string id, IShareStore store, CancellationToken cancel) =>
            await store.GetAsync(id, cancel) is { } record ? Results.Ok(record.View()) : Results.NotFound());

        // A shared galaxy's model route: the record's query with the request's own parameters beneath it (the
        // record's keys win, so a link cannot be edited by its URL), answered from the store when it holds this
        // exact query under the current hash, and from the model otherwise, which then fills the store.
        share.MapGet("/{id}/{route}", async (string id, string route, HttpRequest request, IShareStore store, IResultStore results,
            ModelClient model, ModelVersion version, IOptions<GatewayOptions> options, CancellationToken cancel) =>
        {
            if (!ModelRoutes.Galaxy.Contains(route)) return Results.NotFound();
            if (await store.GetAsync(id, cancel) is not { } record) return Results.NotFound();
            var extra = GalaxyQuery.FromRequest(request.Query, options.Value.Limits.QueryBytes, out var error);
            if (extra is null) return Results.Problem(error, statusCode: 400);
            var query = GalaxyQuery.Parse(record.Query).Under(extra);

            string hash;
            try { hash = await version.CurrentAsync(cancel); }
            catch (Exception) when (!cancel.IsCancellationRequested)
            {
                return Results.Problem("the model's content hash could not be read", statusCode: 503);
            }

            var key = ResultKey.For(hash, id, route, query);
            if (await results.GetAsync(key, cancel) is { } kept) return kept.ToHttp("hit");
            ModelResult fresh;
            try { fresh = await model.GetAsync(route, query, cancel); }
            catch (Exception) when (!cancel.IsCancellationRequested)
            {
                return Results.Problem("the model could not be reached", statusCode: 502);
            }
            if (fresh.Ok) await results.PutAsync(key, fresh, cancel);
            return fresh.ToHttp("miss");
        });

        return share;
    }
}
