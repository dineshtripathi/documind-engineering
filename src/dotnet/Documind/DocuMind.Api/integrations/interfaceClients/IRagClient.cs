using Documind.Contracts;
namespace DocuMind.Api.Clients;

public interface IRagClient
{
    Task<RagAskResponse?> AskAsync(string q, CancellationToken ct = default);

    Task<bool> IngestTextAsync(IngestTextRequest req, CancellationToken ct = default);
    Task<bool> IngestUrlAsync(IngestUrlRequest req, CancellationToken ct = default);
    Task<bool> IngestBlobAsync(IngestBlobRequest req, CancellationToken ct = default);
    Task<bool> UploadAsync(IFormFile file, string? docId, CancellationToken ct = default);
    Task<string> IndexBlocksAsync(TextBlocksDto dto, CancellationToken ct = default);
}
