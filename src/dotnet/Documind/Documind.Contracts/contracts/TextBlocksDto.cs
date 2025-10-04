using System.Text.Json.Serialization;

namespace Documind.Contracts
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
}
