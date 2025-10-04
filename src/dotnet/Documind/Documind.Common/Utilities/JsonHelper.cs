using System.Text.Json;

namespace Documind.Common.Utilities;

/// <summary>
/// Utility class for JSON serialization and deserialization
/// </summary>
public static class JsonHelper
{
    private static readonly JsonSerializerOptions DefaultOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false,
        PropertyNameCaseInsensitive = true
    };

    private static readonly JsonSerializerOptions PrettyOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true,
        PropertyNameCaseInsensitive = true
    };

    /// <summary>
    /// Serializes an object to JSON string
    /// </summary>
    public static string Serialize<T>(T obj, bool pretty = false)
    {
        var options = pretty ? PrettyOptions : DefaultOptions;
        return JsonSerializer.Serialize(obj, options);
    }

    /// <summary>
    /// Deserializes a JSON string to an object
    /// </summary>
    public static T? Deserialize<T>(string json)
    {
        return JsonSerializer.Deserialize<T>(json, DefaultOptions);
    }

    /// <summary>
    /// Tries to deserialize a JSON string to an object
    /// </summary>
    public static bool TryDeserialize<T>(string json, out T? result)
    {
        try
        {
            result = Deserialize<T>(json);
            return result != null;
        }
        catch
        {
            result = default;
            return false;
        }
    }
}
