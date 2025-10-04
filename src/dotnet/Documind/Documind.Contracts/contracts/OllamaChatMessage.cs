using System.Text.Json.Serialization;

namespace Documind.Contracts;

public sealed class OllamaChatMessage
{
    [JsonPropertyName("role")] public string? Role { get; set; }
    [JsonPropertyName("content")] public string? Content { get; set; }
}
