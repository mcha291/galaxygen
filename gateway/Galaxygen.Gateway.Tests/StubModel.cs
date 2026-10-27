using System.Collections.Concurrent;
using System.Text;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Hosting.Server;
using Microsoft.AspNetCore.Hosting.Server.Features;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace Galaxygen.Gateway.Tests;

/// <summary>
/// A stand-in for the Python model on a real loopback port (YARP and the gateway's HttpClient both need one):
/// /api/version publishes a hash the test can change, every other /api route answers "GLXY" and the query it was
/// asked, and counts its calls. <see cref="Hold"/> keeps the galaxy routes waiting until the test releases them.
/// </summary>
public sealed class StubModel : IAsyncDisposable
{
    private readonly WebApplication _app;
    private TaskCompletionSource _gate = Released();

    public string ApiHash { get; set; } = "api0";
    public string ViewerHash { get; set; } = "viewer0";

    /// <summary>What /api/version answers with: anything but 200 is a model that publishes no hash.</summary>
    public int VersionStatus { get; set; } = 200;

    /// <summary>What a galaxy route answers with: anything but 200 is an error body, as the model's own.</summary>
    public int GalaxyStatus { get; set; } = 200;

    /// <summary>The HTTP method of the last galaxy-route request.</summary>
    public string? LastMethod { get; private set; }

    public ConcurrentDictionary<string, int> Calls { get; } = new();
    public string Url { get; private set; } = "";

    private StubModel()
    {
        var builder = WebApplication.CreateSlimBuilder();
        builder.Logging.ClearProviders();
        builder.WebHost.UseUrls("http://127.0.0.1:0");
        _app = builder.Build();

        _app.MapGet("/api/version", () =>
        {
            Calls.AddOrUpdate("version", 1, (_, n) => n + 1);
            if (VersionStatus != 200) return Results.StatusCode(VersionStatus);
            return Results.Json(new
            {
                viewer = new { hash = ViewerHash, count = 1, bytes = 1 },
                api = new { hash = ApiHash, count = 1, bytes = 1 },
                wire = "galaxy-bin/1",
                models = new[] { "basic" },
            });
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
            var query = request.QueryString.Value ?? "";
            if (HttpMethods.IsPost(request.Method) && request.HasFormContentType)
            {
                var form = await request.ReadFormAsync();
                query = "?" + string.Join("&", form.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => $"{p.Key}={p.Value}"));
            }
            Calls.AddOrUpdate(route, 1, (_, n) => n + 1);
            await _gate.Task;
            if (GalaxyStatus != 200) return Results.Json(new { error = $"{route} refused" }, statusCode: GalaxyStatus);
            request.HttpContext.Response.Headers["x-galaxy-stages"] = "disc,stars";
            return Results.Bytes(Encoding.UTF8.GetBytes($"GLXY {route}{query}"), "application/octet-stream");
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

    /// <summary>From now on a galaxy route waits until <see cref="Release"/>.</summary>
    public void Hold() => _gate = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);

    public void Release() => _gate.TrySetResult();

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
