// The local orchestration (BUILD_IV §2c, "around it"): the gateway, the Python model as a container built from
// the repository's own Dockerfile, and later the storage emulator for share links. `dotnet run` in this project
// opens the Aspire dashboard with every service's logs, traces and endpoints.
//
// Docker Desktop must be running for the model container. Without it, run the model by hand
// (`uv run python -m galaxy.api`, port 8017) and start the gateway project alone: its default Model:BaseUrl
// points there.

var builder = DistributedApplication.CreateBuilder(args);

// The Python model: the repository root's Dockerfile, which also builds the frontend into the image.
// The API listens on PORT (8000 in the image) and /api is its route table (a metadata-only readiness check).
var model = builder.AddDockerfile("model", "../..", "Dockerfile")
    .WithHttpEndpoint(port: 8017, targetPort: 8000, name: "http")
    .WithHttpHealthCheck("/api");

// TODO(W3): the storage emulator for share links (Azurite), via the Aspire.Hosting.Azure.Storage package:
//   var storage = builder.AddAzureStorage("storage").RunAsEmulator();
//   var tables = storage.AddTables("share"); var blobs = storage.AddBlobs("bundles");

builder.AddProject<Projects.Galaxygen_Gateway>("gateway")
    .WithEnvironment("Gateway__Model__BaseUrl", model.GetEndpoint("http"))
    .WaitFor(model)
    .WithExternalHttpEndpoints();

builder.Build().Run();
