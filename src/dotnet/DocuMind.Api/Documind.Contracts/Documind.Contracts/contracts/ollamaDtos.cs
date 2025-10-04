using System.Text.Json.Serialization;

namespace Documind.Contracts;

public sealed class OllamaGenerateResponse
{
    [JsonPropertyName("response")] public string? Response { get; set; }
    [JsonPropertyName("model")] public string? Model { get; set; }
    [JsonPropertyName("created_at")] public string? CreatedAt { get; set; }
}
public sealed class OllamaChatMessage
{
    [JsonPropertyName("role")] public string? Role { get; set; }
    [JsonPropertyName("content")] public string? Content { get; set; }
}
public sealed class OllamaChatResponse
{
    [JsonPropertyName("message")] public OllamaChatMessage? Message { get; set; }
    [JsonPropertyName("model")] public string? Model { get; set; }
    [JsonPropertyName("created_at")] public string? CreatedAt { get; set; }
}
