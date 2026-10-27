using System.Collections.Concurrent;
using System.Net.ServerSentEvents;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Threading.Channels;
using Microsoft.Extensions.Options;

namespace Galaxygen.Gateway;

// The edit queue (BUILD_IV §2c): a generate request returns a job id at once; a BackgroundService consumes a
// bounded Channel<GenerateJob> and runs each against the model; the client polls /jobs/{id} or reads its events.
// One model replica runs one expensive job at a time (Limits:ConcurrentGenerates), the rest wait in a queue of
// Limits:GenerateQueue, and a job past that is refused with 429 rather than left to time out.

public enum JobState { Queued, Running, Done, Failed, Cancelled }

/// <summary>The request body: the model route to run (arrays by default) and the galaxy's query.</summary>
public sealed record JobRequest(string? Route, Dictionary<string, JsonElement>? Query);

/// <summary>What /jobs/{id} and its events say about a job.</summary>
public sealed record JobView(
    string Id, JobState State, string Route, int? Position, string? Hash, int? Status, string? Error,
    DateTimeOffset Created, DateTimeOffset? Started, DateTimeOffset? Finished);

public sealed class GenerateJob
{
    private readonly object _lock = new();
    private TaskCompletionSource _changed = new(TaskCreationOptions.RunContinuationsAsynchronously);

    public GenerateJob(string id, string route, GalaxyQuery query, DateTimeOffset created)
    {
        Id = id;
        Route = route;
        Query = query;
        Created = created;
    }

    public string Id { get; }
    public string Route { get; }
    public GalaxyQuery Query { get; }
    public DateTimeOffset Created { get; }
    public CancellationTokenSource Cancel { get; } = new();

    public JobState State { get; private set; } = JobState.Queued;
    public DateTimeOffset? Started { get; private set; }
    public DateTimeOffset? Finished { get; private set; }
    public string? Hash { get; private set; }
    public ModelResult? Result { get; private set; }
    public string? Error { get; private set; }

    public bool Terminal => State is JobState.Done or JobState.Failed or JobState.Cancelled;

    /// <summary>Completes at the job's next change; the events stream waits on it.</summary>
    public Task Changed { get { lock (_lock) return _changed.Task; } }

    /// <summary>Moves the job on, unless it already ended (a cancel that lost the race to a finish, or after it).</summary>
    public bool Move(JobState state, DateTimeOffset at, string? hash = null, ModelResult? result = null, string? error = null)
    {
        TaskCompletionSource fire;
        lock (_lock)
        {
            if (Terminal) return false;
            State = state;
            if (state == JobState.Running) Started = at; else Finished = at;
            Hash = hash ?? Hash;
            Result = result ?? Result;
            Error = error ?? Error;
            fire = _changed;
            _changed = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        }
        fire.TrySetResult();
        return true;
    }

    public JobView View(int? position) =>
        new(Id, State, Route, position, Hash, Result?.Status, Error, Created, Started, Finished);
}

/// <summary>The jobs the gateway knows: the queue's channel, and every job by id until it is evicted.</summary>
public sealed class JobQueue
{
    private readonly ConcurrentDictionary<string, GenerateJob> _jobs = new(StringComparer.Ordinal);
    private readonly Channel<GenerateJob> _channel;
    private readonly int _retain;
    private readonly TimeProvider _clock;

    public JobQueue(IOptions<GatewayOptions> options, TimeProvider clock)
    {
        var limits = options.Value.Limits;
        _channel = Channel.CreateBounded<GenerateJob>(new BoundedChannelOptions(Math.Max(1, limits.GenerateQueue))
        {
            FullMode = BoundedChannelFullMode.Wait, // TryWrite refuses when full; nothing is dropped silently
            SingleReader = limits.ConcurrentGenerates == 1,
        });
        _retain = options.Value.Jobs.Retain;
        _clock = clock;
    }

    public ChannelReader<GenerateJob> Reader => _channel.Reader;

    /// <summary>Queues a job; null when the queue is full.</summary>
    public GenerateJob? TryEnqueue(string route, GalaxyQuery query)
    {
        var job = new GenerateJob(Guid.NewGuid().ToString("N")[..16], route, query, _clock.GetUtcNow());
        _jobs[job.Id] = job;
        if (!_channel.Writer.TryWrite(job))
        {
            _jobs.TryRemove(job.Id, out _);
            return null;
        }
        Evict();
        return job;
    }

    public GenerateJob? Find(string id) => _jobs.TryGetValue(id, out var job) ? job : null;

    /// <summary>How many queued jobs are ahead of this one, counting from one; null once it has left the queue.</summary>
    public int? Position(GenerateJob job) => job.State != JobState.Queued
        ? null
        : 1 + _jobs.Values.Count(other => other.State == JobState.Queued && other.Created < job.Created);

    public (int Queued, int Running) Counts() =>
        (_jobs.Values.Count(j => j.State == JobState.Queued), _jobs.Values.Count(j => j.State == JobState.Running));

    /// <summary>Keeps at most Jobs:Retain finished jobs, the oldest finished forgotten first; a live job is never evicted.</summary>
    private void Evict()
    {
        var finished = _jobs.Values.Where(j => j.Terminal).OrderBy(j => j.Finished).ToList();
        foreach (var job in finished.Take(Math.Max(0, finished.Count - _retain))) _jobs.TryRemove(job.Id, out _);
    }

    /// <summary>The job's views, from now until it ends, each one that differs from the last: what
    /// /jobs/{id}/events streams.</summary>
    public async IAsyncEnumerable<JobView> Watch(GenerateJob job, [EnumeratorCancellation] CancellationToken cancel)
    {
        JobView? last = null;
        while (true)
        {
            var changed = job.Changed;
            var view = job.View(Position(job));
            if (view != last) yield return last = view;
            if (job.Terminal) yield break;
            // A queued job's position moves when one ahead of it starts, which is not its own change: look each second.
            await Task.WhenAny(changed, Task.Delay(TimeSpan.FromSeconds(1), _clock, cancel));
            cancel.ThrowIfCancellationRequested();
        }
    }
}

/// <summary>Runs the queue: Limits:ConcurrentGenerates readers, each one job at a time against the model.</summary>
public sealed class JobWorker(
    JobQueue queue, IServiceProvider services, ModelVersion version, IOptions<GatewayOptions> options,
    TimeProvider clock, ILogger<JobWorker> log) : BackgroundService
{
    protected override Task ExecuteAsync(CancellationToken stopping) =>
        Task.WhenAll(Enumerable.Range(0, Math.Max(1, options.Value.Limits.ConcurrentGenerates)).Select(_ => Read(stopping)));

    private async Task Read(CancellationToken stopping)
    {
        await foreach (var job in queue.Reader.ReadAllAsync(stopping))
        {
            if (job.Terminal) continue; // cancelled while it waited
            await Run(job, stopping);
        }
    }

    private async Task Run(GenerateJob job, CancellationToken stopping)
    {
        using var linked = CancellationTokenSource.CreateLinkedTokenSource(stopping, job.Cancel.Token);
        if (!job.Move(JobState.Running, clock.GetUtcNow())) return;
        try
        {
            var hash = await version.CurrentAsync(linked.Token);
            var result = await services.GetRequiredService<ModelClient>().GetAsync(job.Route, job.Query, linked.Token);
            job.Move(result.Ok ? JobState.Done : JobState.Failed, clock.GetUtcNow(), hash, result,
                result.Ok ? null : $"the model answered {result.Status}");
        }
        catch (OperationCanceledException) when (job.Cancel.IsCancellationRequested)
        {
            job.Move(JobState.Cancelled, clock.GetUtcNow());
        }
        catch (OperationCanceledException) when (stopping.IsCancellationRequested)
        {
            job.Move(JobState.Cancelled, clock.GetUtcNow(), error: "the gateway stopped");
        }
        catch (Exception e)
        {
            log.LogWarning(e, "job {Id} on /api/{Route} failed", job.Id, job.Route);
            job.Move(JobState.Failed, clock.GetUtcNow(), error: e is TimeoutException or OperationCanceledException or Polly.Timeout.TimeoutRejectedException
                ? "the model did not answer in time"
                : "the model could not be reached");
        }
    }
}

public static class JobEndpoints
{
    public static RouteGroupBuilder MapJobs(this IEndpointRouteBuilder app)
    {
        var jobs = app.MapGroup("/jobs");

        jobs.MapPost("/", (JobRequest? body, JobQueue queue, IOptions<GatewayOptions> options) =>
        {
            var route = body?.Route ?? "arrays";
            if (!ModelRoutes.Galaxy.Contains(route)) return Results.Problem($"'{route}' is not a route a job runs", statusCode: 400);
            var query = GalaxyQuery.FromJson(body?.Query, options.Value.Limits.QueryBytes, out var error);
            if (query is null) return Results.Problem(error, statusCode: 400);

            var job = queue.TryEnqueue(route, query);
            if (job is null)
            {
                return Results.Problem("the generate queue is full; try again shortly", statusCode: StatusCodes.Status429TooManyRequests,
                    extensions: new Dictionary<string, object?> { ["retryAfterSeconds"] = 5 });
            }
            return Results.Accepted($"/jobs/{job.Id}", job.View(queue.Position(job)));
        });

        jobs.MapGet("/{id}", (string id, JobQueue queue) =>
            queue.Find(id) is { } job ? Results.Ok(job.View(queue.Position(job))) : Results.NotFound());

        // The answer, exactly as the model gave it; a job not finished yet is a conflict, with its state.
        jobs.MapGet("/{id}/result", (string id, JobQueue queue) => queue.Find(id) switch
        {
            null => Results.NotFound(),
            { Result: { } result } => result.ToHttp(),
            { State: JobState.Failed or JobState.Cancelled } job => Results.Problem(job.Error, statusCode: 502),
            var job => Results.Conflict(job.View(queue.Position(job))),
        });

        jobs.MapGet("/{id}/events", (string id, JobQueue queue, CancellationToken cancel) =>
            queue.Find(id) is { } job
                ? TypedResults.ServerSentEvents(Events(queue.Watch(job, cancel), cancel))
                : Results.NotFound());

        jobs.MapDelete("/{id}", (string id, JobQueue queue, TimeProvider clock) =>
        {
            if (queue.Find(id) is not { } job) return Results.NotFound();
            if (job.State == JobState.Queued) job.Move(JobState.Cancelled, clock.GetUtcNow());
            job.Cancel.Cancel(); // a running job's model request is abandoned; the worker records the cancel
            return Results.Accepted($"/jobs/{job.Id}", job.View(null));
        });

        return jobs;
    }

    private static async IAsyncEnumerable<SseItem<JobView>> Events(IAsyncEnumerable<JobView> views, [EnumeratorCancellation] CancellationToken cancel)
    {
        await foreach (var view in views.WithCancellation(cancel))
        {
            yield return new SseItem<JobView>(view, view.State.ToString().ToLowerInvariant());
        }
    }
}
