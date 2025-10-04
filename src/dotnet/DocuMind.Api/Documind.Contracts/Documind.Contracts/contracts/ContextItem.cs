using System.Text.Json.Serialization;
namespace Documind.Contracts;

public sealed record ContextItem(
    [property: JsonPropertyName("index")] int Index,
    [property: JsonPropertyName("doc_id")] string DocId,
    [property: JsonPropertyName("chunk_id")] string ChunkId,
    [property: JsonPropertyName("score")] double Score
);
