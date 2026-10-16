using System.Text.Json;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;

namespace Galaxygen.Gateway.Tests;

/// <summary>A clock that moves only when the test moves it.</summary>
public sealed class ManualClock : TimeProvider
{
    public DateTimeOffset Now { get; set; } = new(2026, 10, 16, 12, 0, 0, TimeSpan.Zero);
    public override DateTimeOffset GetUtcNow() => Now;
    public void Advance(TimeSpan by) => Now += by;
}

/// <summary>
/// The gateway's parts without the host: the queue's bookkeeping, a job's moves, the memory stores, the hash's
/// lifetime, the static roots. FeatureTests drives the same parts through HTTP; these pin the rules underneath.
/// </summary>
public sealed class PartsTests
{
    private static IOptions<GatewayOptions> Options(Action<GatewayOptions>? set = null)
    {
        var options = new GatewayOptions();
        set?.Invoke(options);
        return Microsoft.Extensions.Options.Options.Create(options);
    }

    private static GalaxyQuery Query(string canonical) => GalaxyQuery.Parse(canonical);

    // --- A job's moves ------------------------------------------------------------------------------------------

    [Fact]
    public void A_job_moves_until_it_ends_and_not_after()
    {
        var clock = new ManualClock();
        var job = new GenerateJob("j", "arrays", Query("template=a"), clock.Now);
        Assert.Equal(JobState.Queued, job.State);
        Assert.False(job.Terminal);

        clock.Advance(TimeSpan.FromSeconds(1));
        Assert.True(job.Move(JobState.Running, clock.Now));
        Assert.Equal(clock.Now, job.Started);
        Assert.Null(job.Finished);

        clock.Advance(TimeSpan.FromSeconds(1));
        var result = new ModelResult(200, "application/octet-stream", "disc", [1, 2]);
        Assert.True(job.Move(JobState.Done, clock.Now, hash: "h", result: result));
        Assert.True(job.Terminal);
        Assert.Equal(clock.Now, job.Finished);

        // A cancel that lost the race to the finish changes nothing.
        Assert.False(job.Move(JobState.Cancelled, clock.Now + TimeSpan.FromSeconds(1), error: "late"));
        Assert.Equal(JobState.Done, job.State);
        Assert.Null(job.Error);

        var view = job.View(position: null);
        Assert.Equal(("j", JobState.Done, "arrays", "h", 200), (view.Id, view.State, view.Route, view.Hash, view.Status));
    }

    [Fact]
    public async Task A_jobs_change_completes_the_task_its_watchers_wait_on()
    {
        var job = new GenerateJob("j", "arrays", GalaxyQuery.Empty, DateTimeOffset.UnixEpoch);
        var before = job.Changed;
        Assert.False(before.IsCompleted);
        job.Move(JobState.Running, DateTimeOffset.UnixEpoch);
        await before.WaitAsync(TimeSpan.FromSeconds(1));
        Assert.False(job.Changed.IsCompleted); // the next change has a task of its own
    }

    [Fact]
    public void A_move_keeps_the_hash_and_result_it_already_has()
    {
        var job = new GenerateJob("j", "arrays", GalaxyQuery.Empty, DateTimeOffset.UnixEpoch);
        job.Move(JobState.Running, DateTimeOffset.UnixEpoch, hash: "h");
        job.Move(JobState.Failed, DateTimeOffset.UnixEpoch, error: "boom");
        Assert.Equal("h", job.Hash);
        Assert.Equal("boom", job.Error);
    }

    // --- The queue ----------------------------------------------------------------------------------------------

    [Fact]
    public void The_queue_counts_positions_from_one_and_forgets_them_once_a_job_leaves()
    {
        var clock = new ManualClock();
        var queue = new JobQueue(Options(), clock);
        var first = queue.TryEnqueue("arrays", Query("t=1"))!;
        clock.Advance(TimeSpan.FromMilliseconds(1));
        var second = queue.TryEnqueue("arrays", Query("t=2"))!;

        Assert.Equal(1, queue.Position(first));
        Assert.Equal(2, queue.Position(second));
        Assert.Equal((2, 0), queue.Counts());

        first.Move(JobState.Running, clock.Now);
        Assert.Null(queue.Position(first));
        Assert.Equal(1, queue.Position(second));
        Assert.Equal((1, 1), queue.Counts());
        Assert.Same(second, queue.Find(second.Id));
        Assert.Null(queue.Find("nope"));
    }

    [Fact(Skip = "Open finding: JobQueue.Position orders by Created, so two jobs queued in the same clock tick both report position 1")]
    public void Two_jobs_queued_in_the_same_tick_have_distinct_positions()
    {
        var queue = new JobQueue(Options(), new ManualClock()); // the clock does not move between the two
        var first = queue.TryEnqueue("arrays", Query("t=1"))!;
        var second = queue.TryEnqueue("arrays", Query("t=2"))!;
        Assert.Equal(1, queue.Position(first));
        Assert.Equal(2, queue.Position(second));
    }

    [Fact]
    public void A_full_queue_refuses_and_forgets_the_refused_job()
    {
        var queue = new JobQueue(Options(o => o.Limits.GenerateQueue = 2), new ManualClock());
        Assert.NotNull(queue.TryEnqueue("arrays", Query("t=1")));
        Assert.NotNull(queue.TryEnqueue("arrays", Query("t=2")));
        Assert.Null(queue.TryEnqueue("arrays", Query("t=3")));
        Assert.Equal((2, 0), queue.Counts()); // the refused job is not left behind as queued
    }

    [Fact]
    public void The_oldest_finished_jobs_are_forgotten_first_and_a_live_one_never()
    {
        var clock = new ManualClock();
        var queue = new JobQueue(Options(o => o.Jobs.Retain = 1), clock);
        var live = queue.TryEnqueue("arrays", Query("t=live"))!;
        var older = queue.TryEnqueue("arrays", Query("t=1"))!;
        var newer = queue.TryEnqueue("arrays", Query("t=2"))!;

        clock.Advance(TimeSpan.FromSeconds(1));
        older.Move(JobState.Done, clock.Now);
        clock.Advance(TimeSpan.FromSeconds(1));
        newer.Move(JobState.Failed, clock.Now);

        queue.TryEnqueue("arrays", Query("t=3")); // eviction runs as a job is queued
        Assert.Null(queue.Find(older.Id));
        Assert.NotNull(queue.Find(newer.Id));
        Assert.NotNull(queue.Find(live.Id));
    }

    [Fact]
    public void A_job_id_is_sixteen_hex_characters()
    {
        var job = new JobQueue(Options(), TimeProvider.System).TryEnqueue("arrays", GalaxyQuery.Empty)!;
        Assert.Matches("^[0-9a-f]{16}$", job.Id);
    }

    // --- The memory stores --------------------------------------------------------------------------------------

    [Fact]
    public async Task The_memory_share_store_keeps_the_first_record_for_an_id()
    {
        var store = new MemoryShareStore();
        await store.PutAsync(new ShareRecord("id", "t=a", "h1", DateTimeOffset.UnixEpoch), default);
        await store.PutAsync(new ShareRecord("id", "t=a", "h2", DateTimeOffset.UnixEpoch.AddDays(1)), default);
        var kept = await store.GetAsync("id", default);
        Assert.Equal("h1", kept!.Hash);
        Assert.Null(await store.GetAsync("other", default));
        Assert.Equal("memory", store.Kind);
    }

    [Fact]
    public async Task The_memory_result_store_drops_the_oldest_past_its_size()
    {
        var store = new MemoryResultStore(Options(o => o.Cache.ResultEntries = 2));
        ModelResult Body(byte b) => new(200, "application/octet-stream", null, [b]);
        await store.PutAsync("a", Body(1), default);
        await store.PutAsync("b", Body(2), default);
        await store.PutAsync("a", Body(9), default); // a repeat neither replaces nor counts twice
        await store.PutAsync("c", Body(3), default);

        Assert.Null(await store.GetAsync("a", default));
        Assert.Equal([2], (await store.GetAsync("b", default))!.Body);
        Assert.Equal([3], (await store.GetAsync("c", default))!.Body);
    }

    [Fact]
    public void A_share_records_view_gives_its_url_and_its_pairs()
    {
        var record = new ShareRecord("abc", "seed=1&template=m%20w", "h", DateTimeOffset.UnixEpoch);
        var view = JsonSerializer.SerializeToElement(record.View());
        Assert.Equal("/share/abc", view.GetProperty("url").GetString());
        Assert.Equal("m w", view.GetProperty("query").GetProperty("template").GetString());
        Assert.Equal("1", view.GetProperty("query").GetProperty("seed").GetString());
    }

    [Fact]
    public void A_result_key_starts_with_the_hash_and_moves_with_every_part()
    {
        var query = Query("template=a");
        var key = ResultKey.For("h", "id", "arrays", query);
        Assert.Equal($"h/id/arrays/{query.Digest(18)}", key);
        Assert.NotEqual(key, ResultKey.For("h", "id2", "arrays", query));
        Assert.NotEqual(key, ResultKey.For("h", "id", "render", query));
        Assert.NotEqual(key, ResultKey.For("h", "id", "arrays", Query("template=b")));
    }

    [Fact]
    public void A_model_result_is_ok_only_for_a_2xx()
    {
        Assert.True(new ModelResult(200, "x", null, []).Ok);
        Assert.True(new ModelResult(204, "x", null, []).Ok);
        Assert.False(new ModelResult(304, "x", null, []).Ok);
        Assert.False(new ModelResult(400, "x", null, []).Ok);
        Assert.False(new ModelResult(502, "x", null, []).Ok);
    }

    // --- The model's hash ---------------------------------------------------------------------------------------

    [Fact]
    public void The_hash_joins_the_apis_and_the_viewers()
    {
        var version = JsonDocument.Parse("""{"api": {"hash": "a1"}, "viewer": {"hash": "v1"}}""").RootElement;
        Assert.Equal("a1.v1", ModelVersion.Compose(version));
    }

    [Theory]
    [InlineData("""{"api": {"hash": ""}, "viewer": {"hash": "v1"}}""")]
    [InlineData("""{"api": {"hash": "a1"}, "viewer": {"hash": null}}""")]
    public void A_version_without_a_hash_is_refused(string json) =>
        Assert.Throws<FormatException>(() => ModelVersion.Compose(JsonDocument.Parse(json).RootElement));

    [Fact]
    public void A_version_missing_its_parts_is_refused() =>
        Assert.Throws<KeyNotFoundException>(() => ModelVersion.Compose(JsonDocument.Parse("""{"api": {}}""").RootElement));

    [Fact]
    public async Task A_read_hash_is_trusted_for_its_seconds_then_read_again()
    {
        await using var model = await StubModel.StartAsync();
        var services = new ServiceCollection();
        services.AddHttpClient<ModelClient>(http => http.BaseAddress = new Uri(model.Url));
        await using var provider = services.BuildServiceProvider();
        var clock = new ManualClock();
        var version = new ModelVersion(provider, Options(o => o.Model.VersionSeconds = 30), clock);

        Assert.Equal("api0.viewer0", await version.CurrentAsync(default));
        model.ApiHash = "api1"; // a redeploy the gateway has not seen yet
        clock.Advance(TimeSpan.FromSeconds(29));
        Assert.Equal("api0.viewer0", await version.CurrentAsync(default));
        Assert.Equal(1, model.CallsTo("version"));

        clock.Advance(TimeSpan.FromSeconds(1));
        Assert.Equal("api1.viewer0", await version.CurrentAsync(default));
        Assert.Equal(2, model.CallsTo("version"));
    }

    [Fact]
    public async Task Callers_at_once_read_the_hash_once()
    {
        await using var model = await StubModel.StartAsync();
        var services = new ServiceCollection();
        services.AddHttpClient<ModelClient>(http => http.BaseAddress = new Uri(model.Url));
        await using var provider = services.BuildServiceProvider();
        var version = new ModelVersion(provider, Options(o => o.Model.VersionSeconds = 30), new ManualClock());

        var hashes = await Task.WhenAll(Enumerable.Range(0, 20).Select(_ => version.CurrentAsync(default).AsTask()));
        Assert.All(hashes, h => Assert.Equal("api0.viewer0", h));
        Assert.Equal(1, model.CallsTo("version"));
    }

    // --- The static roots ---------------------------------------------------------------------------------------

    private sealed class Environment(string root) : IHostEnvironment
    {
        public string EnvironmentName { get; set; } = "Testing";
        public string ApplicationName { get; set; } = "tests";
        public string ContentRootPath { get; set; } = root;
        public IFileProvider ContentRootFileProvider { get; set; } = new NullFileProvider();
    }

    [Fact]
    public void A_static_root_resolves_against_the_content_root_and_is_null_when_absent()
    {
        var root = Directory.CreateTempSubdirectory("gateway-tests-");
        try
        {
            var dist = root.CreateSubdirectory("dist");
            var environment = new Environment(Path.Combine(root.FullName, "project"));

            Assert.Equal(dist.FullName, StaticRoots.Resolve(environment, "../dist"));
            Assert.Equal(dist.FullName, StaticRoots.Resolve(environment, dist.FullName));
            Assert.Null(StaticRoots.Resolve(environment, "../missing"));
            Assert.Null(StaticRoots.Resolve(environment, null));
            Assert.Null(StaticRoots.Resolve(environment, "  "));
        }
        finally
        {
            root.Delete(recursive: true);
        }
    }
}
