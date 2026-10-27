// The local orchestration (BUILD_IV §2c, "around it"): the gateway, the Python model as a container built from
// the repository's own Dockerfile, and the storage emulator for share links. `dotnet run` in this project
// opens the Aspire dashboard with every service's logs, traces and endpoints.
//
// Docker Desktop must be running for the model container. Without it, run the model by hand
// (`uv run python -m galaxy.api`, port 8017) and start the gateway project alone: its default Model:BaseUrl
// points there.

var builder = DistributedApplication.CreateBuilder(args);

// The Python model: the repository root's Dockerfile, which also builds the frontend into the image.
// The API listens on PORT (8000 in the image) and /api is its route table (a metadata-only readiness check).
// Host port 8027, not 8017: 8017 is the owner's own model server, run by hand (S74, G-15).
var model = builder.AddDockerfile("model", "../..", "Dockerfile")
    .WithHttpEndpoint(port: 8027, targetPort: 8000, name: "http")
    .WithHttpHealthCheck("/api");

// Share links' storage: Azurite locally (a container, so Docker again), the storage account when deployed. The
// gateway finds the connection strings by these names and falls back to its own memory without them.
var storage = builder.AddAzureStorage("storage").RunAsEmulator();
var shares = storage.AddTables("shares");
var results = storage.AddBlobs("results");

builder.AddProject<Projects.Galaxygen_Gateway>("gateway")
    .WithEnvironment("Gateway__Model__BaseUrl", model.GetEndpoint("http"))
    .WithReference(shares)
    .WithReference(results)
    .WaitFor(model)
    .WaitFor(storage)
    .WithExternalHttpEndpoints();

builder.Build().Run();
