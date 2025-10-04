using System.Text.Json.Serialization;

namespace DocuMind.Contracts.Contracts.visionDtos
{
    public record TextBlocksDto(
        [property: JsonPropertyName("sourceId")] string SourceId,
        [property: JsonPropertyName("sourceUri")] string SourceUri,
        [property: JsonPropertyName("sourceType")] string SourceType,   // "image" | "pdf"
        [property: JsonPropertyName("language")] string Language,
        [property: JsonPropertyName("blocks")] List<TextBlock> Blocks,
        [property: JsonPropertyName("captions")] List<Caption> Captions,
        [property: JsonPropertyName("tags")] List<string> Tags,
        [property: JsonPropertyName("ingestedAt")] DateTimeOffset IngestedAt);

    public record TextBlock(
        [property: JsonPropertyName("page")] int Page,
        [property: JsonPropertyName("text")] string Text,
        [property: JsonPropertyName("confidence")] float? Confidence,
        [property: JsonPropertyName("bbox")] float[]? Bbox,
        [property: JsonPropertyName("order")] int Order);

    public record Caption(
        [property: JsonPropertyName("page")] int Page,
        [property: JsonPropertyName("text")] string Text,
        [property: JsonPropertyName("confidence")] float? Confidence);
}
