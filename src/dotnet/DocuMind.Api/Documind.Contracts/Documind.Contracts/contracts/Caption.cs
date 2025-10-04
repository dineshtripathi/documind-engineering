using System.Text.Json.Serialization;

namespace Documind.Contracts
{

    public record Caption(
        [property: JsonPropertyName("page")] int Page,
        [property: JsonPropertyName("text")] string Text,
        [property: JsonPropertyName("confidence")] float? Confidence);
}
