using System.Text.Json;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.WebUtilities;

namespace Galaxygen.Gateway.Tests;

/// <summary>
/// The canonical query, alone: every id and every key is made from it, so the same galaxy must always give the same
/// string, a different galaxy a different one, and a stored record must read back as it was written.
/// </summary>
public sealed class GalaxyQueryTests
{
    private static GalaxyQuery Json(string json, int maxBytes = 16384)
    {
        var parsed = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json)!;
        return GalaxyQuery.FromJson(parsed, maxBytes, out var error) ?? throw new Xunit.Sdk.XunitException(error);
    }

    private static string? Refused(string json, int maxBytes = 16384)
    {
        var parsed = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json)!;
        Assert.Null(GalaxyQuery.FromJson(parsed, maxBytes, out var error));
        return error;
    }

    [Fact]
    public void Json_values_become_the_strings_the_model_reads()
    {
        var query = Json("""
            {"template": "milky_way", "seed": 7, "bar": 0.30, "on": true, "off": false,
             "fields": ["sigma", "gas", 3], "skip": null, "obj": {"a": 1}}
            """);
        Assert.Equal("milky_way", query.Pairs["template"]);
        Assert.Equal("7", query.Pairs["seed"]);
        Assert.Equal("0.30", query.Pairs["bar"]); // numbers as written, not reformatted
        Assert.Equal("true", query.Pairs["on"]);
        Assert.Equal("false", query.Pairs["off"]);
        Assert.Equal("sigma,gas,3", query.Pairs["fields"]); // as the client transport joins an array
        Assert.False(query.Pairs.ContainsKey("skip")); // a null is not sent
        Assert.Equal("""{"a": 1}""", query.Pairs["obj"]);
    }

    [Fact]
    public void The_canonical_form_is_ordinal_and_escaped()
    {
        var query = Json("""{"b": "x y", "a": "1&2", "B": "="}""");
        Assert.Equal("B=%3D&a=1%262&b=x%20y", query.Canonical); // ordinal: upper case first
        Assert.Equal(query.Canonical, query.ToString());
    }

    [Fact]
    public void The_same_galaxy_in_any_order_has_one_digest_and_another_galaxy_another()
    {
        var one = Json("""{"template": "milky_way", "seed": 1}""");
        var same = Json("""{"seed": 1, "template": "milky_way"}""");
        var other = Json("""{"template": "milky_way", "seed": 2}""");
        Assert.Equal(one.Digest(), same.Digest());
        Assert.NotEqual(one.Digest(), other.Digest());
    }

    [Fact]
    public void A_number_written_differently_is_a_different_galaxy()
    {
        // The gateway knows no physics (D5): 0.3 and 0.30 are two strings, and so two keys.
        Assert.NotEqual(Json("""{"bar": 0.3}""").Digest(), Json("""{"bar": 0.30}""").Digest());
    }

    [Fact]
    public void The_digest_is_url_safe_and_sized_by_its_bytes()
    {
        // Enough queries that a '+' or a '/' would turn up in a plain base64 digest.
        for (var i = 0; i < 200; i++)
        {
            var query = Json($$"""{"seed": {{i}}}""");
            var digest = query.Digest();
            Assert.Equal(12, digest.Length); // 9 bytes, 72 bits
            Assert.Matches("^[A-Za-z0-9_-]+$", digest);
            Assert.Equal(24, query.Digest(18).Length);
        }
    }

    [Fact]
    public void A_stored_record_parses_back_to_the_same_query()
    {
        var query = Json("""{"template": "m w", "odd": "a+b&c=d%é", "empty": ""}""");
        var back = GalaxyQuery.Parse(query.Canonical);
        Assert.Equal(query.Pairs, back.Pairs);
        Assert.Equal(query.Canonical, back.Canonical);
        Assert.Equal(query.Digest(), back.Digest());
    }

    [Fact]
    public void An_empty_query_is_empty()
    {
        Assert.Equal("", GalaxyQuery.Empty.Canonical);
        Assert.Empty(GalaxyQuery.Parse("").Pairs);
        Assert.Empty(GalaxyQuery.FromJson(null, 100, out _)!.Pairs);
    }

    [Fact]
    public void A_request_query_keeps_a_repeated_keys_last_value()
    {
        var request = new QueryCollection(QueryHelpers.ParseQuery("seed=1&template=a&seed=2"));
        var query = GalaxyQuery.FromRequest(request, 1000, out var error);
        Assert.Null(error);
        Assert.Equal("seed=2&template=a", query!.Canonical);
    }

    [Fact]
    public void Under_lets_this_querys_keys_win()
    {
        var record = GalaxyQuery.Parse("template=milky_way&seed=1");
        var request = GalaxyQuery.Parse("template=ngc_4414&fields=sigma");
        var merged = record.Under(request);
        Assert.Equal("fields=sigma&seed=1&template=milky_way", merged.Canonical);
        Assert.Equal("seed=1&template=milky_way", record.Canonical); // the inputs are untouched
        Assert.Equal("fields=sigma&template=ngc_4414", request.Canonical);
    }

    [Theory]
    [InlineData("a b")]
    [InlineData("a&b")]
    [InlineData("é")]
    [InlineData("")]
    public void A_name_outside_the_pattern_is_refused(string name)
    {
        var error = Refused(JsonSerializer.Serialize(new Dictionary<string, string> { [name] = "1" }));
        Assert.Contains("is not a parameter name", error);
    }

    [Fact]
    public void A_name_is_at_most_64_characters_and_a_long_one_is_clipped_in_the_error()
    {
        Json(JsonSerializer.Serialize(new Dictionary<string, string> { [new string('k', 64)] = "1" }));
        var error = Refused(JsonSerializer.Serialize(new Dictionary<string, string> { [new string('k', 65)] = "1" }));
        Assert.Contains(new string('k', 40) + "...", error);
        Assert.DoesNotContain(new string('k', 41), error);
    }

    [Fact]
    public void At_most_256_parameters()
    {
        var keys = Enumerable.Range(0, GalaxyQuery.MaxKeys).ToDictionary(i => $"k{i}", i => "1");
        Json(JsonSerializer.Serialize(keys));
        keys["one_more"] = "1";
        Assert.Contains("at most 256", Refused(JsonSerializer.Serialize(keys)));
    }

    [Fact]
    public void The_byte_limit_is_on_the_canonical_form()
    {
        // "t=" and 62 characters is 64 bytes: at the limit. One more is over it.
        Json($$"""{"t": "{{new string('x', 62)}}"}""", maxBytes: 64);
        Assert.Contains("over 64 bytes", Refused($$"""{"t": "{{new string('x', 63)}}"}""", maxBytes: 64));

        // Escaping counts: a space is three bytes once canonical.
        Assert.NotNull(Refused($$"""{"t": "{{new string(' ', 21)}}"}""", maxBytes: 64));
    }
}
