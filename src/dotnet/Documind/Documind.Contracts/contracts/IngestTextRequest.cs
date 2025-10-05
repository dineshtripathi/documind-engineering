using System.Text.Json.Serialization;

namespace Documind.Contracts;

public sealed record IngestTextRequest(
    [property: JsonPropertyName("doc_id")] string DocId,
    [property: JsonPropertyName("text")] string Text
);
