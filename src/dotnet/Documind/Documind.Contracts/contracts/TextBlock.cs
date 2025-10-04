using System.Text.Json.Serialization;

namespace Documind.Contracts
{
    public record TextBlock(
        [property: JsonPropertyName("page")] int Page,
        [property: JsonPropertyName("text")] string Text,
        [property: JsonPropertyName("confidence")] float? Confidence,
        [property: JsonPropertyName("bbox")] float[]? Bbox,
        [property: JsonPropertyName("order")] int Order);
}
