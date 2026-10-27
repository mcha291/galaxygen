using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.OutputCaching;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;

namespace Galaxygen.Gateway.Tests;

/// <summary>
/// BUILD_IV Phase W3's gate, as far as it is the gateway's own: /api/version passes through, every cache key
/// carries the model's hash, the queue serves one job at a time and refuses past its length, a share link
/// round-trips its query and opens warm on its second load. Each test runs the gateway against a stub model.
/// </summary>
public sealed class FeatureTests : IAsyncLifetime
{
    private StubModel _model = null!;

    public async Task InitializeAsync() => _model = await StubModel.StartAsync();

    public async Task DisposeAsync() => await _model.DisposeAsync();

    private WebApplicationFactory<Program> Gateway(params (string Key, string Value)[] settings) =>
        new WebApplicationFactory<Program>().WithWebHostBuilder(host =>
        {
            host.UseSetting("Gateway:Model:BaseUrl", _model.Url);
            host.UseSetting("Gateway:Model:VersionSeconds", "0"); // read the hash on every request: a changed hash is seen at once
            host.UseSetting("Gateway:Limits:PermitPerWindow", "10000");
            foreach (var (key, value) in settings) host.UseSetting(key, value);
        });

    // --- Proxying and the cache --------------------------------------------------------------------------------

    [Fact]
    public async Task Api_version_passes_through_unchanged_and_is_never_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();

        var first = await client.GetFromJsonAsync<JsonElement>("/api/version");
        Assert.Equal("api0", first.GetProperty("api").GetProperty("hash").GetString());

        _model.ApiHash = "api1";
        var second = await client.GetFromJsonAsync<JsonElement>("/api/version");
        Assert.Equal("api1", second.GetProperty("api").GetProperty("hash").GetString());
    }

    [Fact]
    public async Task A_model_route_is_answered_once_per_query_and_hash()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();

        var body = await client.GetStringAsync("/api/arrays?template=milky_way&fields=sigma");
        Assert.Equal("GLXY arrays?template=milky_way&fields=sigma", body);
        await client.GetStringAsync("/api/arrays?template=milky_way&fields=sigma");
        Assert.Equal(1, _model.CallsTo("arrays")); // the second came from the cache

        await client.GetStringAsync("/api/arrays?template=milky_way&fields=gas");
        Assert.Equal(2, _model.CallsTo("arrays")); // another query is another key

        _model.ApiHash = "api1"; // a redeploy
        await client.GetStringAsync("/api/arrays?template=milky_way&fields=sigma");
        Assert.Equal(3, _model.CallsTo("arrays")); // the old answer is not served under the new hash
    }

    [Fact]
    public async Task A_model_error_is_not_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync("/api/fail?x=1")).StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync("/api/fail?x=1")).StatusCode);
    }

    [Fact]
    public async Task The_cache_key_carries_the_hash()
    {
        // The key builder, read: the policy puts the hash in the vary-by values and every query key in the key.
        var context = new OutputCacheContext { HttpContext = new DefaultHttpContext() };
        ModelCachePolicy.Vary(context, "abc.def");
        Assert.Equal("abc.def", context.CacheVaryByRules.VaryByValues[ModelCachePolicy.HashKey]);
        Assert.Equal("*", context.CacheVaryByRules.QueryKeys.ToString());

        // And a share link's stored answer, keyed under the hash first.
        var query = GalaxyQuery.Parse("template=milky_way");
        Assert.StartsWith("abc.def/", ResultKey.For("abc.def", "id", "arrays", query));
        Assert.NotEqual(ResultKey.For("abc.def", "id", "arrays", query), ResultKey.For("abc.xyz", "id", "arrays", query));
        await Task.CompletedTask;
    }

    [Fact]
    public async Task A_post_to_the_model_is_not_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var form = () => new FormUrlEncodedContent([new("template", "milky_way")]);
        Assert.Equal("GLXY arrays?template=milky_way", await (await client.PostAsync("/api/arrays", form())).Content.ReadAsStringAsync());
        await client.PostAsync("/api/arrays", form());
        Assert.Equal(2, _model.CallsTo("arrays"));
    }

    [Fact]
    public async Task An_answer_that_sets_a_cookie_is_not_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        await client.GetStringAsync("/api/cookie");
        await client.GetStringAsync("/api/cookie");
        Assert.Equal(2, _model.CallsTo("cookie"));
    }

    [Fact]
    public async Task Without_a_hash_nothing_is_cached_and_the_request_still_reaches_the_model()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        _model.VersionStatus = 500; // the model publishes no hash: no key can be made (D3)

        Assert.Equal("GLXY arrays?template=a", await client.GetStringAsync("/api/arrays?template=a"));
        Assert.Equal("GLXY arrays?template=a", await client.GetStringAsync("/api/arrays?template=a"));
        Assert.Equal(2, _model.CallsTo("arrays"));
    }

    [Fact]
    public async Task A_pinned_hash_keys_the_cache_without_reading_the_version()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "pinned"));
        using var client = gateway.CreateClient();
        await client.GetStringAsync("/api/arrays?template=a");
        await client.GetStringAsync("/api/arrays?template=a");
        Assert.Equal(1, _model.CallsTo("arrays"));
        Assert.Equal(0, _model.CallsTo("version"));
    }

    [Fact]
    public async Task A_pinned_hash_is_used_without_asking_the_model()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "pinned"));
        var version = gateway.Services.GetRequiredService<ModelVersion>();
        Assert.Equal("pinned", await version.CurrentAsync(CancellationToken.None));
        Assert.Equal(0, _model.CallsTo("version"));
    }

    // --- The edit queue ----------------------------------------------------------------------------------------

    [Fact]
    public async Task A_job_returns_an_id_at_once_and_its_result_when_done()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();

        var posted = await client.PostAsJsonAsync("/jobs/", new { query = new { template = "milky_way", seed_disc = 7, fields = new[] { "sigma", "gas" } } });
        Assert.Equal(HttpStatusCode.Accepted, posted.StatusCode);
        var id = (await posted.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetString()!;
        Assert.Equal($"/jobs/{id}", posted.Headers.Location!.ToString());

        var done = await Until(client, id, "done");
        Assert.StartsWith("api0.", done.GetProperty("hash").GetString());

        var result = await client.GetAsync($"/jobs/{id}/result");
        Assert.Equal(HttpStatusCode.OK, result.StatusCode);
        Assert.Equal("disc,stars", result.Headers.GetValues("x-galaxy-stages").Single());
        Assert.Equal("GLXY arrays?fields=sigma%2Cgas&seed_disc=7&template=milky_way", await result.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task The_queue_runs_one_at_a_time_refuses_past_its_length_and_serves_the_waiting_job_after()
    {
        await using var gateway = Gateway(("Gateway:Limits:ConcurrentGenerates", "1"), ("Gateway:Limits:GenerateQueue", "1"));
        using var client = gateway.CreateClient();
        _model.Hold();

        var running = await Post(client, new { template = "a" });
        await Until(client, running, "running");
        await Eventually(() => _model.CallsTo("arrays") == 1); // the job is marked running just before its request lands
        var waiting = await Post(client, new { template = "b" });
        var waitingView = await client.GetFromJsonAsync<JsonElement>($"/jobs/{waiting}");
        Assert.Equal("queued", waitingView.GetProperty("state").GetString());
        Assert.Equal(1, waitingView.GetProperty("position").GetInt32());

        var refused = await client.PostAsJsonAsync("/jobs/", new { query = new { template = "c" } });
        Assert.Equal(HttpStatusCode.TooManyRequests, refused.StatusCode);
        Assert.Equal(1, _model.CallsTo("arrays")); // one generate in flight, not two

        Assert.Equal(HttpStatusCode.Conflict, (await client.GetAsync($"/jobs/{waiting}/result")).StatusCode);
        _model.Release();
        await Until(client, running, "done");
        await Until(client, waiting, "done");
        Assert.Equal("GLXY arrays?template=b", await client.GetStringAsync($"/jobs/{waiting}/result"));
    }

    [Fact]
    public async Task A_jobs_events_stream_ends_with_its_last_state()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        _model.Hold();
        var id = await Post(client, new { template = "milky_way" });
        await Until(client, id, "running");

        // Read event by event, as a browser's EventSource does, and let the model answer once the stream is open.
        using var response = await client.GetAsync($"/jobs/{id}/events", HttpCompletionOption.ResponseHeadersRead);
        Assert.Equal("text/event-stream", response.Content.Headers.ContentType?.MediaType);
        using var reader = new StreamReader(await response.Content.ReadAsStreamAsync());
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        var events = new List<string>();
        while (await reader.ReadLineAsync(timeout.Token) is { } line)
        {
            if (!line.StartsWith("event: ")) continue;
            events.Add(line["event: ".Length..]);
            if (events.Count == 1) _model.Release();
            if (line == "event: done") break;
        }
        Assert.Equal(["running", "done"], events); // each change once, the last state last
    }

    [Fact]
    public async Task A_queued_job_can_be_cancelled()
    {
        await using var gateway = Gateway(("Gateway:Limits:GenerateQueue", "2"));
        using var client = gateway.CreateClient();
        _model.Hold();
        var running = await Post(client, new { template = "a" });
        await Until(client, running, "running");
        var waiting = await Post(client, new { template = "b" });

        Assert.Equal(HttpStatusCode.Accepted, (await client.DeleteAsync($"/jobs/{waiting}")).StatusCode);
        Assert.Equal(HttpStatusCode.Accepted, (await client.DeleteAsync($"/jobs/{running}")).StatusCode);
        await Until(client, waiting, "cancelled");
        await Until(client, running, "cancelled");
        _model.Release();
        Assert.Equal(HttpStatusCode.BadGateway, (await client.GetAsync($"/jobs/{waiting}/result")).StatusCode);
    }

    [Fact]
    public async Task A_job_needs_a_known_route_and_a_valid_query()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var posted = await client.PostAsJsonAsync("/jobs/", new { route = "nonsense", query = new { } });
        Assert.Equal(HttpStatusCode.BadRequest, posted.StatusCode); // not a route a job runs

        Assert.Equal(HttpStatusCode.BadRequest, (await client.PostAsJsonAsync("/jobs/", new { query = new Dictionary<string, string> { ["bad key"] = "1" } })).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/jobs/nope")).StatusCode);
    }

    [Fact]
    public async Task A_model_error_fails_the_job_and_its_result_is_the_models_answer()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        _model.GalaxyStatus = 422;
        var id = await Post(client, new { template = "milky_way" });

        var failed = await Until(client, id, "failed");
        Assert.Equal(422, failed.GetProperty("status").GetInt32());
        Assert.Equal("the model answered 422", failed.GetProperty("error").GetString());

        var result = await client.GetAsync($"/jobs/{id}/result");
        Assert.Equal((HttpStatusCode)422, result.StatusCode); // the model's own status and body, not a gateway 502
        Assert.Contains("arrays refused", await result.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task A_job_fails_when_the_models_hash_cannot_be_read()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        _model.VersionStatus = 503;
        var id = await Post(client, new { template = "milky_way" });

        var failed = await Until(client, id, "failed");
        Assert.Equal("the model could not be reached", failed.GetProperty("error").GetString());
        Assert.Equal(HttpStatusCode.BadGateway, (await client.GetAsync($"/jobs/{id}/result")).StatusCode);
        Assert.Equal(0, _model.CallsTo("arrays")); // a job never runs without the hash it would be recorded under
    }

    [Fact]
    public async Task A_query_past_the_url_limit_travels_to_the_model_as_a_post()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var template = new string('x', ModelClient.MaxUrl);
        var id = await Post(client, new { template });
        await Until(client, id, "done");
        Assert.Equal("POST", _model.LastMethod);
        Assert.Equal($"GLXY arrays?template={template}", await client.GetStringAsync($"/jobs/{id}/result"));

        var shortId = await Post(client, new { template = "a" });
        await Until(client, shortId, "done");
        Assert.Equal("GET", _model.LastMethod);
    }

    [Fact]
    public async Task A_job_runs_the_route_it_names()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var posted = await client.PostAsJsonAsync("/jobs/", new { route = "render", query = new { template = "a" } });
        var view = await posted.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("render", view.GetProperty("route").GetString());
        var id = view.GetProperty("id").GetString()!;
        await Until(client, id, "done");
        Assert.Equal("GLXY render?template=a", await client.GetStringAsync($"/jobs/{id}/result"));
    }

    [Fact]
    public async Task An_unknown_job_is_not_found_on_every_route()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/jobs/nope/result")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/jobs/nope/events")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.DeleteAsync("/jobs/nope")).StatusCode);
    }

    [Fact]
    public async Task A_finished_job_is_forgotten_past_the_retained_count()
    {
        await using var gateway = Gateway(("Gateway:Jobs:Retain", "1"));
        using var client = gateway.CreateClient();
        var first = await Post(client, new { template = "a" });
        await Until(client, first, "done");
        var second = await Post(client, new { template = "b" });
        await Until(client, second, "done");
        var third = await Post(client, new { template = "c" }); // queueing it evicts down to one finished
        await Until(client, third, "done");

        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync($"/jobs/{first}")).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync($"/jobs/{second}")).StatusCode);
    }

    // --- Share links --------------------------------------------------------------------------------------------

    [Fact]
    public async Task A_share_link_round_trips_its_query_and_opens_warm_on_the_second_load()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var query = new { template = "milky_way", seed_disc = 42, bar_strength = 0.3 };

        var created = await client.PostAsJsonAsync("/share/", new { query });
        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
        var record = await created.Content.ReadFromJsonAsync<JsonElement>();
        var id = record.GetProperty("id").GetString()!;
        Assert.Equal(12, id.Length);

        var again = await (await client.PostAsJsonAsync("/share/", new { query = new { bar_strength = 0.3, seed_disc = 42, template = "milky_way" } }))
            .Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal(id, again.GetProperty("id").GetString()); // the same galaxy, in any order, is the same link

        var read = await client.GetFromJsonAsync<JsonElement>($"/share/{id}");
        var pairs = read.GetProperty("query");
        Assert.Equal("milky_way", pairs.GetProperty("template").GetString());
        Assert.Equal("42", pairs.GetProperty("seed_disc").GetString());
        Assert.Equal("0.3", pairs.GetProperty("bar_strength").GetString());

        var cold = await client.GetAsync($"/share/{id}/arrays?fields=sigma");
        Assert.Equal("miss", cold.Headers.GetValues("x-gateway-cache").Single());
        var warm = await client.GetAsync($"/share/{id}/arrays?fields=sigma");
        Assert.Equal("hit", warm.Headers.GetValues("x-gateway-cache").Single());
        Assert.Equal(await cold.Content.ReadAsStringAsync(), await warm.Content.ReadAsStringAsync());
        Assert.Equal("disc,stars", warm.Headers.GetValues("x-galaxy-stages").Single());
        Assert.Equal(1, _model.CallsTo("arrays"));

        _model.ApiHash = "api1"; // a redeploy: the link computes again
        Assert.Equal("miss", (await client.GetAsync($"/share/{id}/arrays?fields=sigma")).Headers.GetValues("x-gateway-cache").Single());
    }

    [Fact]
    public async Task A_share_links_own_query_cannot_be_overridden_by_its_url()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = (await (await client.PostAsJsonAsync("/share/", new { query = new { template = "milky_way" } }))
            .Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetString();

        var body = await client.GetStringAsync($"/share/{id}/arrays?template=ngc_4414&fields=sigma");
        Assert.Equal("GLXY arrays?fields=sigma&template=milky_way", body);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync($"/share/{id}/version")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/share/nope")).StatusCode);
    }

    [Fact]
    public async Task Creating_share_links_is_limited_per_client()
    {
        await using var gateway = Gateway(("Gateway:Limits:SharesPerHour", "1"));
        using var client = gateway.CreateClient();
        Assert.Equal(HttpStatusCode.Created, (await client.PostAsJsonAsync("/share/", new { query = new { template = "a" } })).StatusCode);
        Assert.Equal(HttpStatusCode.TooManyRequests, (await client.PostAsJsonAsync("/share/", new { query = new { template = "b" } })).StatusCode);
    }

    [Fact]
    public async Task A_share_needs_a_query_within_bounds()
    {
        await using var gateway = Gateway(("Gateway:Limits:QueryBytes", "64"));
        using var client = gateway.CreateClient();
        Assert.Equal(HttpStatusCode.BadRequest, (await client.PostAsJsonAsync("/share/", new { query = new { } })).StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, (await client.PostAsJsonAsync("/share/", new { query = new { template = new string('x', 100) } })).StatusCode);
    }

    [Fact]
    public async Task A_share_is_made_without_the_model_awake_and_its_routes_wait_for_the_hash()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        _model.VersionStatus = 503;

        var created = await client.PostAsJsonAsync("/share/", new { query = new { template = "milky_way" } });
        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
        var record = await created.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal(JsonValueKind.Null, record.GetProperty("hash").ValueKind);
        var id = record.GetProperty("id").GetString();
        Assert.Equal($"/share/{id}", created.Headers.Location!.ToString());

        // No hash, no key: the route refuses rather than serve or store an answer it cannot key.
        Assert.Equal(HttpStatusCode.ServiceUnavailable, (await client.GetAsync($"/share/{id}/arrays")).StatusCode);
        Assert.Equal(0, _model.CallsTo("arrays"));
    }

    [Fact]
    public async Task A_shared_galaxys_error_is_passed_on_and_not_kept()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = (await (await client.PostAsJsonAsync("/share/", new { query = new { template = "milky_way" } }))
            .Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetString();

        _model.GalaxyStatus = 500;
        var first = await client.GetAsync($"/share/{id}/arrays");
        Assert.Equal(HttpStatusCode.InternalServerError, first.StatusCode);
        Assert.Equal("miss", first.Headers.GetValues("x-gateway-cache").Single());

        _model.GalaxyStatus = 200;
        var second = await client.GetAsync($"/share/{id}/arrays");
        Assert.Equal(HttpStatusCode.OK, second.StatusCode);
        Assert.Equal("miss", second.Headers.GetValues("x-gateway-cache").Single()); // the error was not stored
    }

    [Fact]
    public async Task A_shared_galaxys_routes_key_each_extra_parameter_apart()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = (await (await client.PostAsJsonAsync("/share/", new { query = new { template = "milky_way" } }))
            .Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetString();

        Assert.Equal("miss", (await client.GetAsync($"/share/{id}/arrays?fields=sigma")).Headers.GetValues("x-gateway-cache").Single());
        Assert.Equal("miss", (await client.GetAsync($"/share/{id}/arrays?fields=gas")).Headers.GetValues("x-gateway-cache").Single());
        Assert.Equal("miss", (await client.GetAsync($"/share/{id}/render?fields=sigma")).Headers.GetValues("x-gateway-cache").Single());
        Assert.Equal(3, _model.CallsTo("arrays") + _model.CallsTo("render"));
    }

    [Fact]
    public async Task A_shared_galaxys_route_refuses_a_bad_parameter_and_an_unknown_link()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = (await (await client.PostAsJsonAsync("/share/", new { query = new { template = "milky_way" } }))
            .Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetString();

        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync($"/share/{id}/arrays?bad%20key=1")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/share/nope/arrays")).StatusCode);
        Assert.Equal(0, _model.CallsTo("arrays"));
    }

    // --- Health and the client's address ------------------------------------------------------------------------

    [Fact]
    public async Task Healthz_names_the_stores_the_pin_and_the_queue()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "pinned"));
        using var client = gateway.CreateClient();
        var health = await client.GetFromJsonAsync<JsonElement>("/healthz");
        Assert.Equal(_model.Url, health.GetProperty("model").GetString());
        Assert.True(health.GetProperty("pinned").GetBoolean());
        Assert.Equal("memory", health.GetProperty("shares").GetString());
        Assert.Equal("memory", health.GetProperty("results").GetString());
        Assert.Equal(0, health.GetProperty("jobs").GetProperty("queued").GetInt32());
        Assert.Equal(0, health.GetProperty("jobs").GetProperty("running").GetInt32());

        _model.Hold();
        var id = await Post(client, new { template = "a" });
        await Until(client, id, "running");
        health = await client.GetFromJsonAsync<JsonElement>("/healthz");
        Assert.Equal(1, health.GetProperty("jobs").GetProperty("running").GetInt32());
        _model.Release();
    }

    [Fact]
    public async Task Behind_the_ingress_each_forwarded_address_is_its_own_client()
    {
        await using var gateway = Gateway(("Gateway:Limits:TrustForwardedFor", "true"), ("Gateway:Limits:PermitPerWindow", "1"));
        using var client = gateway.CreateClient();

        async Task<HttpStatusCode> From(string address)
        {
            using var request = new HttpRequestMessage(HttpMethod.Get, "/healthz");
            request.Headers.Add("X-Forwarded-For", address);
            return (await client.SendAsync(request)).StatusCode;
        }

        Assert.Equal(HttpStatusCode.OK, await From("203.0.113.1"));
        Assert.Equal(HttpStatusCode.TooManyRequests, await From("203.0.113.1"));
        Assert.Equal(HttpStatusCode.OK, await From("203.0.113.2"));

        // Only the last entry, the ingress's own, is believed: a forged first entry does not make a new client.
        Assert.Equal(HttpStatusCode.TooManyRequests, await From("198.51.100.9, 203.0.113.2"));
    }

    [Fact]
    public async Task Without_trusting_the_ingress_a_forwarded_address_is_ignored()
    {
        await using var gateway = Gateway(("Gateway:Limits:PermitPerWindow", "1"));
        using var client = gateway.CreateClient();
        using var first = new HttpRequestMessage(HttpMethod.Get, "/healthz") { Headers = { { "X-Forwarded-For", "203.0.113.1" } } };
        using var second = new HttpRequestMessage(HttpMethod.Get, "/healthz") { Headers = { { "X-Forwarded-For", "203.0.113.2" } } };
        Assert.Equal(HttpStatusCode.OK, (await client.SendAsync(first)).StatusCode);
        Assert.Equal(HttpStatusCode.TooManyRequests, (await client.SendAsync(second)).StatusCode);
    }

    // --- Helpers ------------------------------------------------------------------------------------------------

    private static async Task<string> Post(HttpClient client, object query)
    {
        var posted = await client.PostAsJsonAsync("/jobs/", new { query });
        Assert.Equal(HttpStatusCode.Accepted, posted.StatusCode);
        return (await posted.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetString()!;
    }

    private static async Task Eventually(Func<bool> condition)
    {
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(10);
        while (!condition())
        {
            if (DateTime.UtcNow > deadline) throw new TimeoutException("the condition never held");
            await Task.Delay(10);
        }
    }

    private static async Task<JsonElement> Until(HttpClient client, string id, string state)
    {
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(10);
        while (true)
        {
            var view = await client.GetFromJsonAsync<JsonElement>($"/jobs/{id}");
            if (view.GetProperty("state").GetString() == state) return view;
            if (DateTime.UtcNow > deadline) throw new TimeoutException($"job {id} is {view.GetProperty("state")}, not {state}");
            await Task.Delay(20);
        }
    }
}
