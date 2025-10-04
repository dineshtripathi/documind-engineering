using Microsoft.AspNetCore.Http;
using System.Text.Json.Serialization;
namespace Documind.Contracts;

public sealed record RagAskResponse(string Route, string Answer, IReadOnlyList<ContextItem> ContextMap);

public sealed record IngestBlobRequest(string DocId, string BlobUrl, string? ContentType = null, string? BlobName = null);
public sealed record IngestTextRequest(string DocId, string Text);
public sealed record IngestUrlRequest(string Url, string? DocId = null);

public sealed record ContextItem(
    [property: JsonPropertyName("index")] int Index,
    [property: JsonPropertyName("doc_id")] string DocId,
    [property: JsonPropertyName("chunk_id")] string ChunkId,
    [property: JsonPropertyName("score")] double Score
);

public sealed class UploadIngestForm
{
    public IFormFile File { get; set; } = default!;   // required
    public string? DocId { get; set; }                // optional
}
