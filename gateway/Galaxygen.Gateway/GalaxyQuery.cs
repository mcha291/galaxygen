using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Galaxygen.Gateway;

/// <summary>
/// A galaxy as the model's query string sees it: template, model, layer, every input and seed, by name. The
/// gateway does not know which names are inputs and which are a route's own parameters (rule D5: no physics here);
/// it only keeps the pairs in one canonical order, so the same galaxy always has the same id and the same key.
/// </summary>
public sealed partial class GalaxyQuery
{
    public const int MaxKeys = 256;

    private readonly SortedDictionary<string, string> _pairs;

    private GalaxyQuery(SortedDictionary<string, string> pairs) => _pairs = pairs;

    public IReadOnlyDictionary<string, string> Pairs => _pairs;

    public static GalaxyQuery Empty { get; } = new(new SortedDictionary<string, string>(StringComparer.Ordinal));

    [GeneratedRegex("^[A-Za-z0-9_.-]{1,64}$")]
    private static partial Regex KeyPattern();

    /// <summary>
    /// From a JSON object of name to value, as a client sends it. Strings pass as they are, numbers as written,
    /// booleans lower-case, arrays joined with commas (as the client transport joins them), objects as their JSON
    /// text; nulls are not sent. Returns null and an error when the object is not a query the gateway will store.
    /// </summary>
    public static GalaxyQuery? FromJson(IReadOnlyDictionary<string, JsonElement>? json, int maxBytes, out string? error)
    {
        var pairs = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (var (key, value) in json ?? new Dictionary<string, JsonElement>())
        {
            var text = value.ValueKind switch
            {
                JsonValueKind.Null or JsonValueKind.Undefined => null,
                JsonValueKind.String => value.GetString(),
                JsonValueKind.True => "true",
                JsonValueKind.False => "false",
                JsonValueKind.Number => value.GetRawText(),
                JsonValueKind.Array => string.Join(",", value.EnumerateArray()
                    .Select(item => item.ValueKind == JsonValueKind.String ? item.GetString() : item.GetRawText())),
                _ => value.GetRawText(),
            };
            if (text is not null) pairs[key] = text;
        }
        return Validate(pairs, maxBytes, out error);
    }

    /// <summary>From a request's query string; a repeated key keeps its last value, as the model reads it.</summary>
    public static GalaxyQuery? FromRequest(IQueryCollection query, int maxBytes, out string? error)
    {
        var pairs = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (var (key, values) in query)
        {
            if (values.Count > 0 && values[^1] is { } last) pairs[key] = last;
        }
        return Validate(pairs, maxBytes, out error);
    }

    /// <summary>From a stored record: the canonical query string this type wrote.</summary>
    public static GalaxyQuery Parse(string canonical)
    {
        var pairs = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (var (key, values) in Microsoft.AspNetCore.WebUtilities.QueryHelpers.ParseQuery(canonical))
        {
            pairs[key] = values[^1] ?? "";
        }
        return new GalaxyQuery(pairs);
    }

    private static GalaxyQuery? Validate(SortedDictionary<string, string> pairs, int maxBytes, out string? error)
    {
        error = null;
        if (pairs.Count > MaxKeys) error = $"at most {MaxKeys} parameters";
        else if (pairs.Keys.FirstOrDefault(k => !KeyPattern().IsMatch(k)) is { } bad) error = $"'{Clip(bad)}' is not a parameter name";
        else
        {
            var query = new GalaxyQuery(pairs);
            if (Encoding.UTF8.GetByteCount(query.Canonical) > maxBytes) error = $"the query is over {maxBytes} bytes";
            else return query;
        }
        return null;
    }

    private static string Clip(string s) => s.Length <= 40 ? s : s[..40] + "...";

    /// <summary>This query with <paramref name="over"/>'s pairs laid on it: where both name a key, this one's wins.</summary>
    public GalaxyQuery Under(GalaxyQuery over)
    {
        var pairs = new SortedDictionary<string, string>(over._pairs, StringComparer.Ordinal);
        foreach (var (key, value) in _pairs) pairs[key] = value;
        return new GalaxyQuery(pairs);
    }

    /// <summary>The query string, keys in ordinal order, each pair URL-encoded: the form every key is made from.</summary>
    public string Canonical => string.Join("&", _pairs.Select(p => $"{Uri.EscapeDataString(p.Key)}={Uri.EscapeDataString(p.Value)}"));

    /// <summary>A short, URL-safe digest of the canonical form: 12 characters, 72 bits.</summary>
    public string Digest(int bytes = 9)
    {
        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(Canonical));
        return Convert.ToBase64String(hash, 0, bytes).Replace('+', '-').Replace('/', '_').TrimEnd('=');
    }

    public override string ToString() => Canonical;
}
