using Yarp.ReverseProxy.Configuration;

namespace Galaxygen.Gateway;

/// <summary>
/// The YARP configuration, in code so that the model's address is one option and one test can read it.
/// One route: everything under /api goes to the model unchanged. The model's own content hash at /api/version
/// passes through with it, so rule D3 holds at this boundary.
/// </summary>
public static class Proxy
{
    public const string ClusterId = "model";
    public const string RouteId = "api";

    public static IReadOnlyList<RouteConfig> Routes() =>
    [
        new RouteConfig
        {
            RouteId = RouteId,
            ClusterId = ClusterId,
            Match = new RouteMatch { Path = "/api/{**rest}" },
        },
    ];

    public static IReadOnlyList<ClusterConfig> Clusters(ModelOptions model) =>
    [
        new ClusterConfig
        {
            ClusterId = ClusterId,
            Destinations = new Dictionary<string, DestinationConfig>
            {
                ["model"] = new DestinationConfig { Address = model.BaseUrl },
            },
            HttpRequest = new Yarp.ReverseProxy.Forwarder.ForwarderRequestConfig
            {
                ActivityTimeout = TimeSpan.FromSeconds(model.TimeoutSeconds),
            },
        },
    ];
}
