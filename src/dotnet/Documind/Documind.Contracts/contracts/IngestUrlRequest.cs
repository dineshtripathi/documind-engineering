namespace Documind.Contracts;

public sealed record IngestUrlRequest(
    string Url,
    string? DocId = null,
    string? Language = null,
    string[]? Features = null
);

