using System.IO.Compression;
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
/// BUILD_IV Phase W3's gate, as far as it is the gateway's own, with S74's review fixes: /api/version passes through,
/// every cache key carries the model's hash (model.hash, and only it), a pin is checked, one input-taking request
/// computes at the model at a time, the queue serves one job at a time and refuses past its length, a share link
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
            host.UseSetting("Gateway:Frontend:Path", ""); // no frontend unless a test gives one
            foreach (var (key, value) in settings) host.UseSetting(key, value);
        });

    private static string Header(HttpResponseMessage response, string name) =>
        response.Headers.TryGetValues(name, out var values) ? string.Join(",", values) : "<absent>";

    // --- Proxying and the cache --------------------------------------------------------------------------------

    [Fact]
    public async Task Api_version_passes_through_unchanged_and_is_never_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();

        var first = await client.GetFromJsonAsync<JsonElement>("/api/version");
        Assert.Equal("model0", first.GetProperty("model").GetProperty("hash").GetString());
        Assert.Equal("api0", first.GetProperty("api").GetProperty("hash").GetString());

        _model.ModelHash = "model1";
        var second = await client.GetFromJsonAsync<JsonElement>("/api/version");
        Assert.Equal("model1", second.GetProperty("model").GetProperty("hash").GetString());
    }

    [Fact]
    public async Task Api_version_with_a_trailing_slash_is_never_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();

        var first = await client.GetFromJsonAsync<JsonElement>("/api/version/");
        _model.ModelHash = "model1";
        var second = await client.GetFromJsonAsync<JsonElement>("/api/version/");
        Assert.Equal("model0", first.GetProperty("model").GetProperty("hash").GetString());
        Assert.Equal("model1", second.GetProperty("model").GetProperty("hash").GetString());
        Assert.Equal(2, _model.CallsTo("version"));
        Assert.Contains("/api/version", ModelCachePolicy.Uncached);
    }

    [Fact]
    public async Task A_model_route_is_answered_once_per_query_and_model_hash()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();

        Assert.Equal("GLXY arrays?template=milky_way&fields=sigma", await StubModel.Text(client, "/api/arrays?template=milky_way&fields=sigma"));
        await StubModel.Text(client, "/api/arrays?template=milky_way&fields=sigma");
        Assert.Equal(1, _model.CallsTo("arrays")); // the second came from the cache

        await StubModel.Text(client, "/api/arrays?template=milky_way&fields=gas");
        Assert.Equal(2, _model.CallsTo("arrays")); // another query is another key

        _model.ApiHash = "api1"; // the API's files and the viewer's moved, the model's bytes did not:
        _model.ViewerHash = "viewer1";
        await StubModel.Text(client, "/api/arrays?template=milky_way&fields=sigma");
        Assert.Equal(2, _model.CallsTo("arrays")); // the same key

        _model.ModelHash = "model1"; // a stage, a constant, a data file changed: a redeploy
        await StubModel.Text(client, "/api/arrays?template=milky_way&fields=sigma");
        Assert.Equal(3, _model.CallsTo("arrays")); // the old answer is not served under the new hash
    }

    [Fact]
    public async Task A_proxied_answer_carries_the_models_headers_and_a_replay_says_it_ran_nothing()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();

        using var miss = await client.GetAsync("/api/clouds?template=a");
        Assert.Equal("miss", Header(miss, "X-Gateway-Cache"));
        Assert.Equal("disc,stars", Header(miss, "X-Galaxy-Stages"));
        Assert.Equal("model", Header(miss, "X-Galaxy-Source"));
        Assert.True(miss.Headers.CacheControl?.NoStore);

        using var hit = await client.GetAsync("/api/clouds?template=a");
        Assert.Equal("hit", Header(hit, "X-Gateway-Cache"));
        Assert.Equal("", Header(hit, "X-Galaxy-Stages")); // nothing ran for this request (D4)
        Assert.Equal("model", Header(hit, "X-Galaxy-Source"));
        Assert.True(hit.Headers.CacheControl?.NoStore);
        Assert.Equal(await miss.Content.ReadAsByteArrayAsync(), await hit.Content.ReadAsByteArrayAsync());
        Assert.Equal(1, _model.CallsTo("clouds"));
    }

    [Fact]
    public async Task A_model_error_is_not_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync("/api/fail?x=1")).StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync("/api/fail?x=1")).StatusCode);
    }

    // S76 (BUILD_IV W5, D240 F4; the review's G2): the compression runs inside the output cache, so a body is compressed
    // once, on its miss, and stored per encoding (the key varies by Accept-Encoding); a hit is served as stored. Each
    // encoding asked in turn - a miss then a hit - is one model call each: three in all, and a request asking for no
    // encoding is never sent a compressed body, before or after the compressed ones are stored.
    [Fact]
    public async Task A_body_is_compressed_once_on_its_miss_and_stored_per_encoding()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var expected = (byte[])[.. StubModel.Prefix, .. System.Text.Encoding.ASCII.GetBytes("GLXY render?template=a")];
        static async Task<byte[]> Decoded(HttpResponseMessage response, string encoding)
        {
            await using var body = await response.Content.ReadAsStreamAsync();
            await using Stream decoder = encoding switch
            {
                "br" => new BrotliStream(body, CompressionMode.Decompress),
                "gzip" => new GZipStream(body, CompressionMode.Decompress),
                _ => body,
            };
            using var bytes = new MemoryStream();
            await decoder.CopyToAsync(bytes);
            return bytes.ToArray();
        }
        HttpRequestMessage Asked(string encoding)
        {
            var request = new HttpRequestMessage(HttpMethod.Get, "/api/render?template=a");
            if (encoding != "identity") request.Headers.AcceptEncoding.ParseAdd(encoding);
            return request;
        }

        var calls = 0;
        foreach (var encoding in new[] { "br", "gzip", "identity" })
        {
            foreach (var expectCache in new[] { "miss", "hit" })
            {
                using var answer = await client.SendAsync(Asked(encoding));
                Assert.Equal(HttpStatusCode.OK, answer.StatusCode);
                Assert.Equal(expectCache, Header(answer, "X-Gateway-Cache"));
                if (encoding == "identity") Assert.Empty(answer.Content.Headers.ContentEncoding);
                else Assert.Equal([encoding], answer.Content.Headers.ContentEncoding);
                Assert.Contains("Accept-Encoding", answer.Headers.Vary);
                Assert.Equal(expected, await Decoded(answer, encoding));
            }
            calls += 1;
            Assert.Equal(calls, _model.CallsTo("render")); // one model call per distinct encoding: its miss
        }
        Assert.Equal(3, _model.CallsTo("render"));

        // And a client asking for no encoding, once every encoding is stored, is still sent the identity body.
        using var plain = await client.SendAsync(Asked("identity"));
        Assert.Equal("hit", Header(plain, "X-Gateway-Cache"));
        Assert.Empty(plain.Content.Headers.ContentEncoding);
        Assert.Equal(expected, await plain.Content.ReadAsByteArrayAsync());
        Assert.Equal(3, _model.CallsTo("render"));
    }

    [Fact]
    public async Task The_page_files_are_compressed_below_the_cache()
    {
        var root = Directory.CreateTempSubdirectory("galaxygen-files-");
        try
        {
            Directory.CreateDirectory(Path.Combine(root.FullName, "assets"));
            var script = string.Concat(Enumerable.Repeat("console.log('galaxygen');\n", 200));
            await File.WriteAllTextAsync(Path.Combine(root.FullName, "assets", "app-0000.js"), script);
            await File.WriteAllTextAsync(Path.Combine(root.FullName, "index.html"), "<!doctype html><title>g</title>" + new string(' ', 2000));
            await using var gateway = Gateway(("Gateway:Frontend:Path", root.FullName));
            using var client = gateway.CreateClient();
            foreach (var path in new[] { "/assets/app-0000.js", "/", "/some/route" })
            {
                using var request = new HttpRequestMessage(HttpMethod.Get, path);
                request.Headers.AcceptEncoding.ParseAdd("gzip");
                using var answer = await client.SendAsync(request);
                Assert.Equal(HttpStatusCode.OK, answer.StatusCode);
                Assert.Equal(["gzip"], answer.Content.Headers.ContentEncoding);
                Assert.Equal("<absent>", Header(answer, "X-Gateway-Cache"));
            }
        }
        finally
        {
            root.Delete(recursive: true);
        }
    }

    [Fact]
    public void Every_key_carries_the_model_hash_and_only_it()
    {
        // The key builder, read (D3 as amended): /api/version's model.hash is the key's hash; api and viewer are not in it.
        static JsonElement Version(string model, string api, string viewer) => JsonSerializer.SerializeToElement(
            new { viewer = new { hash = viewer }, api = new { hash = api }, model = new { hash = model } });

        var base0 = ModelVersion.Compose(Version("m0", "a0", "v0"));
        Assert.Equal("m0", base0);
        Assert.Equal(base0, ModelVersion.Compose(Version("m0", "a1", "v0")));
        Assert.Equal(base0, ModelVersion.Compose(Version("m0", "a0", "v1")));
        Assert.NotEqual(base0, ModelVersion.Compose(Version("m1", "a0", "v0")));

        // The output cache's key: every query parameter and the hash in the vary-by values.
        var context = new OutputCacheContext { HttpContext = new DefaultHttpContext() };
        ModelCachePolicy.Vary(context, base0);
        Assert.Equal("m0", context.CacheVaryByRules.VaryByValues[ModelCachePolicy.HashKey]);
        Assert.Equal("*", context.CacheVaryByRules.QueryKeys.ToString());
        Assert.Equal("Accept-Encoding", context.CacheVaryByRules.HeaderNames.ToString()); // G2: stored per encoding

        // A share link's stored answer, keyed under the hash first, and moved by it.
        var query = GalaxyQuery.Parse("template=milky_way");
        Assert.StartsWith("m0/", ResultKey.For(base0, "id", "arrays", query));
        Assert.NotEqual(ResultKey.For("m0", "id", "arrays", query), ResultKey.For("m1", "id", "arrays", query));
    }

    [Fact]
    public async Task A_jobs_record_carries_the_model_hash()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = await Post(client, new { template = "a" });
        Assert.Equal("model0", (await Until(client, id, "done")).GetProperty("hash").GetString());
    }

    [Fact]
    public async Task A_post_to_the_model_is_not_cached()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var form = () => new FormUrlEncodedContent([new("template", "milky_way")]);
        Assert.Equal("GLXY arrays?template=milky_way", await StubModel.Text(await client.PostAsync("/api/arrays", form())));
        await client.PostAsync("/api/arrays", form());
        Assert.Equal(2, _model.CallsTo("arrays"));
    }

    [Fact]
    public async Task A_long_render_body_is_forwarded_unchanged()
    {
        // The viewer's sampled filter curves: a form body of about 20 KB, as a POST (S42).
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var filters = string.Join(",", Enumerable.Range(0, 2400).Select(i => (i * 0.37).ToString("F3")));
        using var form = new FormUrlEncodedContent([new("template", "milky_way"), new("filters", filters)]);
        var sent = (await form.ReadAsStringAsync()).Length;
        Assert.True(sent > 20_000, $"the body is {sent} bytes");

        using var response = await client.PostAsync("/api/render", form);
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal(sent.ToString(), Header(response, "X-Stub-Body-Length"));
        Assert.Equal($"GLXY render?filters={filters}&template=milky_way", await StubModel.Text(response));
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

        Assert.Equal("GLXY arrays?template=a", await StubModel.Text(client, "/api/arrays?template=a"));
        Assert.Equal("GLXY arrays?template=a", await StubModel.Text(client, "/api/arrays?template=a"));
        Assert.Equal(2, _model.CallsTo("arrays"));
    }

    [Fact]
    public async Task A_version_without_the_model_hash_is_refused_and_keys_nothing()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        _model.OmitModelHash = true; // an API before S72: api and viewer only

        await StubModel.Text(client, "/api/arrays?template=a");
        await StubModel.Text(client, "/api/arrays?template=a");
        Assert.Equal(2, _model.CallsTo("arrays")); // no cache serves anything until a model hash is read

        var health = await client.GetFromJsonAsync<JsonElement>("/healthz");
        Assert.Contains("S72", health.GetProperty("hash").GetProperty("error").GetString());
        Assert.Equal(JsonValueKind.Null, health.GetProperty("hash").GetProperty("keyed").ValueKind);

        _model.OmitModelHash = false;
        await StubModel.Text(client, "/api/arrays?template=a");
        await StubModel.Text(client, "/api/arrays?template=a");
        Assert.Equal(3, _model.CallsTo("arrays")); // read once, kept once
    }

    // --- The pin -----------------------------------------------------------------------------------------------

    [Fact]
    public async Task A_pinned_hash_keys_the_cache_and_a_hit_never_asks_the_model()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "model0"));
        using var client = gateway.CreateClient();
        await StubModel.Text(client, "/api/arrays?template=a"); // a miss: the pin is checked on the way
        await StubModel.Text(client, "/api/arrays?template=a"); // a hit: nothing asked
        await StubModel.Text(client, "/api/arrays?template=a");
        Assert.Equal(1, _model.CallsTo("arrays"));
        Assert.Equal(1, _model.CallsTo("version"));

        var health = await client.GetAsync("/healthz");
        Assert.Equal(HttpStatusCode.OK, health.StatusCode);
        Assert.False((await health.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("pin_mismatch").GetBoolean());
    }

    [Fact]
    public async Task A_pinned_hash_is_used_without_asking_the_model()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "pinned"));
        var version = gateway.Services.GetRequiredService<ModelVersion>();
        Assert.Equal("pinned", await version.CurrentAsync(CancellationToken.None));
        Assert.Equal(0, _model.CallsTo("version"));
    }

    [Fact]
    public async Task Healthz_tells_a_configured_pin_from_one_in_force()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "pinned"));
        using var client = gateway.CreateClient();

        var before = await client.GetFromJsonAsync<JsonElement>("/healthz");
        Assert.True(before.GetProperty("pinned").GetBoolean());
        Assert.True(before.GetProperty("pin_configured").GetBoolean());

        await StubModel.Text(client, "/api/arrays?template=a"); // the check on the way drops the pin
        var health = await client.GetAsync("/healthz");
        Assert.Equal(HttpStatusCode.ServiceUnavailable, health.StatusCode);
        var body = await health.Content.ReadFromJsonAsync<JsonElement>();
        Assert.False(body.GetProperty("pinned").GetBoolean()); // no pin in force
        Assert.True(body.GetProperty("pin_configured").GetBoolean()); // though the configuration names one
        Assert.True(body.GetProperty("pin_mismatch").GetBoolean());
    }

    [Fact]
    public async Task A_pin_the_live_model_contradicts_is_dropped_and_healthz_answers_503()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "pinned"));
        using var client = gateway.CreateClient();

        await StubModel.Text(client, "/api/arrays?template=a"); // keyed under the pin, which the check on the way refutes
        var health = await client.GetAsync("/healthz");
        Assert.Equal(HttpStatusCode.ServiceUnavailable, health.StatusCode);
        var body = await health.Content.ReadFromJsonAsync<JsonElement>();
        Assert.True(body.GetProperty("pin_mismatch").GetBoolean());
        Assert.Equal("pinned", body.GetProperty("hash").GetProperty("pin").GetString());
        Assert.Equal("model0", body.GetProperty("hash").GetProperty("live").GetString());
        Assert.Equal("model0", body.GetProperty("hash").GetProperty("keyed").GetString());

        // The answer made under the wrong pin was not kept; from now on the live hash keys.
        await StubModel.Text(client, "/api/arrays?template=a");
        await StubModel.Text(client, "/api/arrays?template=a");
        Assert.Equal(2, _model.CallsTo("arrays"));
        Assert.Equal("model0", await gateway.Services.GetRequiredService<ModelVersion>().CurrentAsync(default));
    }

    [Fact]
    public async Task The_viewers_own_version_read_checks_the_pin()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "pinned"));
        using var client = gateway.CreateClient();

        var version = await client.GetFromJsonAsync<JsonElement>("/api/version");
        Assert.Equal("model0", version.GetProperty("model").GetProperty("hash").GetString()); // passed through as it was
        Assert.Equal(1, _model.CallsTo("version")); // read once, by the viewer; the gateway looked on the way
        Assert.Equal(HttpStatusCode.ServiceUnavailable, (await client.GetAsync("/healthz")).StatusCode);
    }

    // --- One request at the model at a time (D-5) ---------------------------------------------------------------

    [Fact]
    public async Task Two_concurrent_proxied_renders_run_one_after_the_other()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        _model.Hold();

        var first = client.GetAsync("/api/render?template=a");
        await Eventually(() => _model.CallsTo("render") == 1);
        var second = client.GetAsync("/api/render?template=b");
        await Eventually(async () =>
            (await client.GetFromJsonAsync<JsonElement>("/healthz")).GetProperty("limits").GetProperty("model").GetProperty("waiting").GetInt32() == 1);
        Assert.False(second.IsCompleted);
        Assert.Equal(1, _model.CallsTo("render")); // the second waits at the gateway, not at the model

        // A metadata route is not queued behind it.
        var stages = client.GetAsync("/api/stages");
        await Eventually(() => _model.CallsTo("stages") == 1);

        _model.Release();
        Assert.Equal(HttpStatusCode.OK, (await first).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await second).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await stages).StatusCode);
        Assert.Equal(2, _model.CallsTo("render"));
    }

    [Fact]
    public async Task Past_the_model_queue_a_request_is_429_with_retry_after()
    {
        await using var gateway = Gateway(("Gateway:Limits:ModelQueue", "1"));
        using var client = gateway.CreateClient();
        _model.Hold();

        var running = client.GetAsync("/api/region?template=a");
        await Eventually(() => _model.CallsTo("region") == 1);
        var waiting = client.GetAsync("/api/region?template=b");
        await Eventually(async () =>
            (await client.GetFromJsonAsync<JsonElement>("/healthz")).GetProperty("limits").GetProperty("model").GetProperty("waiting").GetInt32() == 1);

        using var refused = await client.GetAsync("/api/region?template=c");
        Assert.Equal(HttpStatusCode.TooManyRequests, refused.StatusCode);
        Assert.Equal(TimeSpan.FromSeconds(ModelGate.RetryAfterSeconds), refused.Headers.RetryAfter?.Delta);

        _model.Release();
        Assert.Equal(HttpStatusCode.OK, (await running).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await waiting).StatusCode);
    }

    [Fact]
    public async Task A_cache_hit_never_waits_for_the_model()
    {
        await using var gateway = Gateway(("Gateway:Limits:ModelQueue", "0"));
        using var client = gateway.CreateClient();
        await StubModel.Text(client, "/api/render?template=warm");
        _model.Hold();

        var running = client.GetAsync("/api/render?template=a");
        await Eventually(() => _model.CallsTo("render") == 2);
        using var hit = await client.GetAsync("/api/render?template=warm").WaitAsync(TimeSpan.FromSeconds(5));
        Assert.Equal(HttpStatusCode.OK, hit.StatusCode);
        Assert.Equal("hit", Header(hit, "X-Gateway-Cache"));
        Assert.Equal(HttpStatusCode.TooManyRequests, (await client.GetAsync("/api/render?template=cold")).StatusCode);

        _model.Release();
        Assert.Equal(HttpStatusCode.OK, (await running).StatusCode);
    }

    [Fact]
    public async Task A_share_links_miss_waits_for_the_same_permit()
    {
        await using var gateway = Gateway(("Gateway:Limits:ModelQueue", "0"));
        using var client = gateway.CreateClient();
        var id = await Share(client, new { template = "milky_way" });
        _model.Hold();

        var running = client.GetAsync("/api/render?template=a");
        await Eventually(() => _model.CallsTo("render") == 1);
        Assert.Equal(HttpStatusCode.TooManyRequests, (await client.GetAsync($"/share/{id}/render")).StatusCode);

        _model.Release();
        await running;
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync($"/share/{id}/render")).StatusCode);
    }

    // --- The window (G-8) ----------------------------------------------------------------------------------------

    [Fact]
    public async Task The_window_counts_only_what_may_reach_the_model_and_says_when_to_retry()
    {
        await using var gateway = Gateway(("Gateway:Limits:PermitPerWindow", "2"));
        using var client = gateway.CreateClient();

        await StubModel.Text(client, "/api/arrays?template=a"); // counted: 1
        for (var i = 0; i < 5; i++) await StubModel.Text(client, "/api/arrays?template=a"); // hits: free
        for (var i = 0; i < 5; i++) Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/healthz")).StatusCode); // free
        await StubModel.Text(client, "/api/arrays?template=b"); // counted: 2

        using var refused = await client.GetAsync("/api/arrays?template=c");
        Assert.Equal(HttpStatusCode.TooManyRequests, refused.StatusCode);
        Assert.True(refused.Headers.RetryAfter?.Delta > TimeSpan.Zero);
        Assert.Equal(2, _model.CallsTo("arrays"));
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
        Assert.Equal("model0", done.GetProperty("hash").GetString());

        var result = await client.GetAsync($"/jobs/{id}/result");
        Assert.Equal(HttpStatusCode.OK, result.StatusCode);
        Assert.Equal("disc,stars", Header(result, "X-Galaxy-Stages"));
        Assert.Equal("model", Header(result, "X-Galaxy-Source"));
        Assert.True(result.Headers.CacheControl?.NoStore);
        Assert.Equal("GLXY arrays?fields=sigma%2Cgas&seed_disc=7&template=milky_way", await StubModel.Text(result));
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
        Assert.NotNull(refused.Headers.RetryAfter);
        Assert.Equal(1, _model.CallsTo("arrays")); // one generate in flight, not two

        Assert.Equal(HttpStatusCode.Conflict, (await client.GetAsync($"/jobs/{waiting}/result")).StatusCode);
        _model.Release();
        await Until(client, running, "done");
        await Until(client, waiting, "done");
        Assert.Equal("GLXY arrays?template=b", await StubModel.Text(client, $"/jobs/{waiting}/result"));
    }

    [Fact]
    public async Task A_cancelled_queued_job_frees_its_place_at_once()
    {
        await using var gateway = Gateway(("Gateway:Limits:GenerateQueue", "1"));
        using var client = gateway.CreateClient();
        _model.Hold();
        var running = await Post(client, new { template = "a" });
        await Until(client, running, "running");
        var waiting = await Post(client, new { template = "b" });
        Assert.Equal(HttpStatusCode.TooManyRequests, (await client.PostAsJsonAsync("/jobs/", new { query = new { template = "c" } })).StatusCode);

        Assert.Equal(HttpStatusCode.Accepted, (await client.DeleteAsync($"/jobs/{waiting}")).StatusCode);
        var again = await Post(client, new { template = "d" }); // the cancelled job's place, while the first still runs
        _model.Release();
        await Until(client, again, "done");
        Assert.Equal("cancelled", (await client.GetFromJsonAsync<JsonElement>($"/jobs/{waiting}")).GetProperty("state").GetString());
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
        Assert.Equal(HttpStatusCode.BadRequest, (await client.PostAsJsonAsync("/jobs/", new { route = "version", query = new { } })).StatusCode);

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
        Assert.Equal($"GLXY arrays?template={template}", await StubModel.Text(client, $"/jobs/{id}/result"));

        var shortId = await Post(client, new { template = "a" });
        await Until(client, shortId, "done");
        Assert.Equal("GET", _model.LastMethod);
    }

    [Fact]
    public async Task A_job_takes_a_query_the_size_of_the_viewers_filter_curves()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var filters = string.Join(",", Enumerable.Range(0, 3000).Select(i => (i * 0.37).ToString("F3")));
        Assert.True(filters.Length > 20_000);
        var posted = await client.PostAsJsonAsync("/jobs/", new { route = "render", query = new { template = "a", filters } });
        Assert.Equal(HttpStatusCode.Accepted, posted.StatusCode); // under G-4's 131072 bytes, over the old 16384
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
        Assert.Equal("GLXY render?template=a", await StubModel.Text(client, $"/jobs/{id}/result"));
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
        await Eventually(async () => (await client.GetAsync($"/jobs/{first}")).StatusCode == HttpStatusCode.NotFound
            && (await client.GetAsync($"/jobs/{second}")).StatusCode == HttpStatusCode.OK); // evicted as the second finished
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
        Assert.Equal("miss", Header(cold, "X-Gateway-Cache"));
        Assert.Equal("disc,stars", Header(cold, "X-Galaxy-Stages"));
        var warm = await client.GetAsync($"/share/{id}/arrays?fields=sigma");
        Assert.Equal("hit", Header(warm, "X-Gateway-Cache"));
        Assert.Equal(await cold.Content.ReadAsByteArrayAsync(), await warm.Content.ReadAsByteArrayAsync());
        Assert.Equal("", Header(warm, "X-Galaxy-Stages")); // nothing ran for the hit (D4)
        Assert.Equal("model", Header(warm, "X-Galaxy-Source")); // as the model sent it
        Assert.True(warm.Headers.CacheControl?.NoStore);
        Assert.Equal(1, _model.CallsTo("arrays"));

        _model.ApiHash = "api1"; // not a redeploy of the model's bytes: still warm
        Assert.Equal("hit", Header(await client.GetAsync($"/share/{id}/arrays?fields=sigma"), "X-Gateway-Cache"));
        _model.ModelHash = "model1"; // a redeploy: the link computes again
        Assert.Equal("miss", Header(await client.GetAsync($"/share/{id}/arrays?fields=sigma"), "X-Gateway-Cache"));
    }

    [Fact]
    public async Task A_share_links_own_query_cannot_be_overridden_by_its_url()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = await Share(client, new { template = "milky_way" });

        Assert.Equal("GLXY arrays?fields=sigma&template=milky_way", await StubModel.Text(client, $"/share/{id}/arrays?template=ngc_4414&fields=sigma"));
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync($"/share/{id}/version")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/share/nope")).StatusCode);
    }

    [Fact]
    public async Task A_share_link_takes_only_its_routes_own_parameters()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = await Share(client, new { template = "milky_way" });

        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync($"/share/{id}/arrays?bar_strength=0.9")).StatusCode); // an input the record lacks
        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync($"/share/{id}/arrays?r_min=1")).StatusCode); // region's, not arrays'
        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync($"/share/{id}/layer?level=1")).StatusCode);
        Assert.Equal(0, _model.CallsTo("arrays") + _model.CallsTo("layer"));

        Assert.Equal("GLXY region?r_max=4&r_min=1&template=milky_way", await StubModel.Text(client, $"/share/{id}/region?r_min=1&r_max=4"));
        Assert.Equal("GLXY render?filters=u%2Cg&level=2&template=milky_way", await StubModel.Text(client, $"/share/{id}/render?filters=u,g&level=2"));
        Assert.Equal("GLXY layer?template=milky_way", await StubModel.Text(client, $"/share/{id}/layer"));
    }

    [Fact]
    public async Task A_share_id_of_the_wrong_shape_is_not_found()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        foreach (var id in new[] { "nope", "abc%27def%21ghi", "ABCDEFGHIJK%2F", "ABCDEFGHIJKLM", "ABCDEFGHIJKL" })
        {
            Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync($"/share/{id}")).StatusCode);
            Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync($"/share/{id}/arrays")).StatusCode);
        }
    }

    [Fact]
    public async Task Creating_share_links_is_limited_per_client()
    {
        await using var gateway = Gateway(("Gateway:Limits:SharesPerHour", "1"));
        using var client = gateway.CreateClient();
        Assert.Equal(HttpStatusCode.Created, (await client.PostAsJsonAsync("/share/", new { query = new { template = "a" } })).StatusCode);
        using var refused = await client.PostAsJsonAsync("/share/", new { query = new { template = "b" } });
        Assert.Equal(HttpStatusCode.TooManyRequests, refused.StatusCode);
        Assert.NotNull(refused.Headers.RetryAfter);
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
    public async Task A_share_takes_the_known_hash_without_asking_the_model()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "model0"));
        using var client = gateway.CreateClient();
        var created = await client.PostAsJsonAsync("/share/", new { query = new { template = "milky_way" } });
        Assert.Equal("model0", (await created.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("hash").GetString());
        Assert.Equal(0, _model.CallsTo("version"));
    }

    [Fact]
    public async Task A_shared_galaxys_error_is_passed_on_and_not_kept()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = await Share(client, new { template = "milky_way" });

        _model.GalaxyStatus = 500;
        var first = await client.GetAsync($"/share/{id}/arrays");
        Assert.Equal(HttpStatusCode.InternalServerError, first.StatusCode);
        Assert.Equal("miss", Header(first, "X-Gateway-Cache"));
        Assert.Equal(1, _model.CallsTo("arrays")); // not retried (D-6)

        _model.GalaxyStatus = 200;
        var second = await client.GetAsync($"/share/{id}/arrays");
        Assert.Equal(HttpStatusCode.OK, second.StatusCode);
        Assert.Equal("miss", Header(second, "X-Gateway-Cache")); // the error was not stored
    }

    [Fact]
    public async Task A_shared_galaxys_routes_key_each_extra_parameter_apart()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = await Share(client, new { template = "milky_way" });

        Assert.Equal("miss", Header(await client.GetAsync($"/share/{id}/arrays?fields=sigma"), "X-Gateway-Cache"));
        Assert.Equal("miss", Header(await client.GetAsync($"/share/{id}/arrays?fields=gas"), "X-Gateway-Cache"));
        Assert.Equal("miss", Header(await client.GetAsync($"/share/{id}/render?filters=u"), "X-Gateway-Cache"));
        Assert.Equal(3, _model.CallsTo("arrays") + _model.CallsTo("render"));
    }

    [Fact]
    public async Task A_shared_galaxys_route_refuses_a_bad_parameter_and_an_unknown_link()
    {
        await using var gateway = Gateway();
        using var client = gateway.CreateClient();
        var id = await Share(client, new { template = "milky_way" });

        Assert.Equal(HttpStatusCode.BadRequest, (await client.GetAsync($"/share/{id}/arrays?bad%20key=1")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/share/nope/arrays")).StatusCode);
        Assert.Equal(0, _model.CallsTo("arrays"));
    }

    // --- The frontend (G-7) -------------------------------------------------------------------------------------

    [Fact]
    public async Task The_frontend_is_served_with_its_cache_headers_and_the_fallback_never_answers_assets()
    {
        var dist = Directory.CreateTempSubdirectory("gateway-dist-");
        try
        {
            await File.WriteAllTextAsync(Path.Combine(dist.FullName, "index.html"), "<!doctype html><title>galaxygen</title>");
            dist.CreateSubdirectory("assets");
            await File.WriteAllTextAsync(Path.Combine(dist.FullName, "assets", "index-AbC123.js"), "console.log(1)");
            await using var gateway = Gateway(("Gateway:Frontend:Path", dist.FullName));
            using var client = gateway.CreateClient();

            foreach (var page in new[] { "/", "/index.html", "/galaxy/edit" })
            {
                using var response = await client.GetAsync(page);
                Assert.Equal(HttpStatusCode.OK, response.StatusCode);
                Assert.Contains("galaxygen", await response.Content.ReadAsStringAsync());
                Assert.True(response.Headers.CacheControl?.NoCache, page);
            }

            using var asset = await client.GetAsync("/assets/index-AbC123.js");
            Assert.Equal(HttpStatusCode.OK, asset.StatusCode);
            Assert.Equal("public, max-age=31536000, immutable", asset.Headers.CacheControl?.ToString());

            Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/assets/index-gone.js")).StatusCode);
            Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/assets/gone")).StatusCode);
            Assert.Equal("GLXY arrays?template=a", await StubModel.Text(client, "/api/arrays?template=a")); // /api stays the model's

            var health = await client.GetFromJsonAsync<JsonElement>("/healthz");
            Assert.True(health.GetProperty("frontend").GetBoolean());
        }
        finally
        {
            dist.Delete(recursive: true);
        }
    }

    // --- Health and the client's address ------------------------------------------------------------------------

    [Fact]
    public async Task Healthz_names_the_stores_the_pin_the_limits_and_the_queue()
    {
        await using var gateway = Gateway(("Gateway:Model:ContentHash", "model0"));
        using var client = gateway.CreateClient();
        var health = await client.GetFromJsonAsync<JsonElement>("/healthz");
        Assert.Equal(_model.Url, health.GetProperty("model").GetString());
        Assert.True(health.GetProperty("pinned").GetBoolean());
        Assert.False(health.GetProperty("pin_mismatch").GetBoolean());
        Assert.False(health.GetProperty("frontend").GetBoolean());
        Assert.False(health.TryGetProperty("bundles", out _)); // the gateway reads no bundle (D-3)
        Assert.Equal("memory", health.GetProperty("shares").GetString());
        Assert.Equal("memory", health.GetProperty("results").GetString());
        var limits = health.GetProperty("limits");
        Assert.Equal(10000, limits.GetProperty("window").GetProperty("permit").GetInt32());
        Assert.Equal(60, limits.GetProperty("window").GetProperty("seconds").GetInt32());
        Assert.Equal(1, limits.GetProperty("model").GetProperty("concurrent").GetInt32());
        Assert.Equal(64, limits.GetProperty("model").GetProperty("queue").GetInt32());
        Assert.Equal(131072, limits.GetProperty("query_bytes").GetInt32());
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
            using var request = new HttpRequestMessage(HttpMethod.Get, "/api/version");
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
        using var first = new HttpRequestMessage(HttpMethod.Get, "/api/version") { Headers = { { "X-Forwarded-For", "203.0.113.1" } } };
        using var second = new HttpRequestMessage(HttpMethod.Get, "/api/version") { Headers = { { "X-Forwarded-For", "203.0.113.2" } } };
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

    private static async Task<string> Share(HttpClient client, object query)
    {
        var created = await client.PostAsJsonAsync("/share/", new { query });
        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
        return (await created.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetString()!;
    }

    private static Task Eventually(Func<bool> condition) => Eventually(() => Task.FromResult(condition()));

    private static async Task Eventually(Func<Task<bool>> condition)
    {
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(10);
        while (!await condition())
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
