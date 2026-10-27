using System.Net;
using Galaxygen.Gateway;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;

namespace Galaxygen.Gateway.Tests;

/// <summary>
/// The gateway through the test host, with no model behind it: what the scaffold promises, asserted.
/// The features (the queue, share links, the cache) are FeatureTests', against a stub model.
/// </summary>
public sealed class GatewayTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public GatewayTests(WebApplicationFactory<Program> factory) => _factory = factory;

    [Fact]
    public async Task Healthz_reports_what_is_served()
    {
        using var client = _factory.CreateClient();
        var response = await client.GetAsync("/healthz");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadAsStringAsync();
        Assert.Contains("\"status\":\"ok\"", body);
        Assert.Contains("\"model\":", body);
    }

    [Fact]
    public async Task The_sliding_window_returns_429_past_its_permit()
    {
        // Two requests a window, then the third is refused (BUILD_IV §7 ruling 5's shape at a small number).
        using var factory = _factory.WithWebHostBuilder(host =>
            host.UseSetting("Gateway:Limits:PermitPerWindow", "2")
                .UseSetting("Gateway:Limits:WindowSeconds", "60"));
        using var client = factory.CreateClient();

        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/healthz")).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/healthz")).StatusCode);
        Assert.Equal(HttpStatusCode.TooManyRequests, (await client.GetAsync("/healthz")).StatusCode);
    }

    [Fact]
    public void The_proxy_sends_the_api_to_the_configured_model()
    {
        var model = new ModelOptions { BaseUrl = "http://model.internal:8000", TimeoutSeconds = 7 };
        var cluster = Assert.Single(Proxy.Clusters(model));
        Assert.Equal("http://model.internal:8000", cluster.Destinations!["model"].Address);
        Assert.Equal(TimeSpan.FromSeconds(7), cluster.HttpRequest!.ActivityTimeout);

        var route = Assert.Single(Proxy.Routes());
        Assert.Equal("/api/{**rest}", route.Match.Path);
        Assert.Equal(cluster.ClusterId, route.ClusterId);
    }
}
