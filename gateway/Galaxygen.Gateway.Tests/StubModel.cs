using System.Collections.Concurrent;
using System.Text;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Hosting.Server;
using Microsoft.AspNetCore.Hosting.Server.Features;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.WebUtilities;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace Galaxygen.Gateway.Tests;

/// <summary>
/// A stand-in for the Python model on a real loopback port (YARP and the gateway's HttpClient both need one).
/// /api/version publishes the three hashes the model does (S72+): <c>viewer</c>, <c>api</c> and <c>model</c>, the one
/// every cache keys on, each changeable by the test. Every other /api route answers as the model's http.py does:
/// <c>Cache-Control: no-store</c>, <c>X-Galaxy-Stages</c>, <c>X-Galaxy-Source</c>, and a binary-looking body - four
/// bytes that are not UTF-8, then "GLXY", the route and the query it was asked - and counts its calls, and echoes
/// the length of a POST body it read in <c>X-Stub-Body-Length</c>. <see cref="Hold"/> keeps the routes waiting.
/// </summary>
public sealed class StubModel : IAsyncDisposable
{
    /// <summary>The bytes every galaxy answer starts with: not text, so a gateway that decodes and re-encodes shows.</summary>
    public static readonly byte[] Prefix = [0x00, 0xFF, 0xFE, 0x80];

    private readonly WebApplication _app;
    private TaskCompletionSource _gate = Released();

    public string ModelHash { get; set; } = "model0";
    public string ApiHash { get; set; } = "api0";
    public string ViewerHash { get; set; } = "viewer0";

    /// <summary>Publish /api/version without its <c>model</c> key, as an API before S72 did.</summary>
    public bool OmitModelHash { get; set; }

    /// <summary>What /api/version answers with: anything but 200 is a model that publishes no hash.</summary>
    public int VersionStatus { get; set; } = 200;

    /// <summary>What a galaxy route answers with: anything but 200 is an error body, as the model's own.</summary>
    public int GalaxyStatus { get; set; } = 200;

    /// <summary>What X-Galaxy-Source says: "model" when computed, "bundle" when a template bundle answered.</summary>
    public string Source { get; set; } = "model";

    /// <summary>The HTTP method of the last galaxy-route request.</summary>
    public string? LastMethod { get; private set; }

    public ConcurrentDictionary<string, int> Calls { get; } = new();

    /// <summary>Galaxy-route requests computing now, and the most there ever were at once.</summary>
    public int InFlight => _inFlight;
    public int MostInFlight => _most;
    private int _inFlight;
    private int _most;

    public string Url { get; private set; } = "";

    private StubModel()
    {
        var builder = WebApplication.CreateSlimBuilder();
        builder.Logging.ClearProviders();
        builder.WebHost.UseUrls("http://127.0.0.1:0");
        _app = builder.Build();

        _app.MapGet("/api/version", (HttpResponse response) =>
        {
            Calls.AddOrUpdate("version", 1, (_, n) => n + 1);
            response.Headers.CacheControl = "no-store";
            if (VersionStatus != 200) return Results.StatusCode(VersionStatus);
            var hashes = new Dictionary<string, object>
            {
                ["viewer"] = new { hash = ViewerHash, count = 1, bytes = 1 },
                ["api"] = new { hash = ApiHash, count = 1, bytes = 1 },
                ["wire"] = "galaxy-bin/1",
                ["models"] = new[] { "basic" },
            };
            if (!OmitModelHash) hashes["model"] = new { hash = ModelHash, count = 1, bytes = 1 };
            return Results.Json(hashes);
        });

        _app.Map("/api/fail", () => Results.Json(new { error = "no such input" }, statusCode: 400));

        _app.MapGet("/api/cookie", (HttpResponse response) =>
        {
            Calls.AddOrUpdate("cookie", 1, (_, n) => n + 1);
            response.Headers.SetCookie = "session=1";
            return Results.Text("with a cookie");
        });

        _app.Map("/api/{route}", async (string route, HttpRequest request) =>
        {
            LastMethod = request.Method;
            var response = request.HttpContext.Response;
            var query = request.QueryString.Value ?? "";
            if (HttpMethods.IsPost(request.Method))
            {
                using var reader = new StreamReader(request.Body, Encoding.ASCII);
                var raw = await reader.ReadToEndAsync();
                response.Headers["X-Stub-Body-Length"] = raw.Length.ToString();
                var form = QueryHelpers.ParseQuery(raw);
                query = "?" + string.Join("&", form.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => $"{p.Key}={p.Value}"));
            }
            Calls.AddOrUpdate(route, 1, (_, n) => n + 1);
            var now = Interlocked.Increment(ref _inFlight);
            InterlockedMax(ref _most, now);
            try
            {
                await _gate.Task;
            }
            finally
            {
                Interlocked.Decrement(ref _inFlight);
            }
            response.Headers.CacheControl = "no-store";
            response.Headers["X-Galaxy-Source"] = Source;
            response.Headers["X-Galaxy-Stages"] = Source == "bundle" ? "" : "disc,stars";
            if (GalaxyStatus != 200) return Results.Json(new { error = $"{route} refused" }, statusCode: GalaxyStatus);
            return Results.Bytes([.. Prefix, .. Encoding.ASCII.GetBytes($"GLXY {route}{query}")], "application/octet-stream");
        });
    }

    public static async Task<StubModel> StartAsync()
    {
        var stub = new StubModel();
        await stub._app.StartAsync();
        stub.Url = stub._app.Services.GetRequiredService<IServer>().Features.Get<IServerAddressesFeature>()!.Addresses.First();
        return stub;
    }

    public int CallsTo(string route) => Calls.GetValueOrDefault(route);

    /// <summary>A galaxy answer's text after its binary prefix, which must be there byte for byte.</summary>
    public static string Text(byte[] body)
    {
        Assert.True(body.Length >= Prefix.Length && body.AsSpan(0, Prefix.Length).SequenceEqual(Prefix), "the binary prefix was changed on the way");
        return Encoding.ASCII.GetString(body, Prefix.Length, body.Length - Prefix.Length);
    }

    public static async Task<string> Text(HttpResponseMessage response) => Text(await response.Content.ReadAsByteArrayAsync());

    public static async Task<string> Text(HttpClient client, string url)
    {
        using var response = await client.GetAsync(url);
        Assert.True(response.IsSuccessStatusCode, $"{url} answered {(int)response.StatusCode}");
        return await Text(response);
    }

    /// <summary>From now on a galaxy route waits until <see cref="Release"/>.</summary>
    public void Hold() => _gate = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);

    public void Release() => _gate.TrySetResult();

    private static void InterlockedMax(ref int target, int value)
    {
        int seen;
        while ((seen = Volatile.Read(ref target)) < value && Interlocked.CompareExchange(ref target, value, seen) != seen) { }
    }

    private static TaskCompletionSource Released()
    {
        var done = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        done.SetResult();
        return done;
    }

    public async ValueTask DisposeAsync()
    {
        Release();
        await _app.StopAsync();
        await _app.DisposeAsync();
    }
}
