using System.Text.Json.Serialization;

namespace Documind.Contracts;

public sealed class OllamaChatResponse
{
    [JsonPropertyName("message")] public OllamaChatMessage? Message { get; set; }
    [JsonPropertyName("model")] public string? Model { get; set; }
    [JsonPropertyName("created_at")] public string? CreatedAt { get; set; }
}
