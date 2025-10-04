namespace Documind.Contracts;

public sealed record IngestBlobRequest(string DocId, string BlobUrl, string? ContentType = null, string? BlobName = null);
