using DocuMind.Api.Models;

namespace DocuMind.Api.Services;

public interface IAskOrchestrator
{
    Task<AskResponse> AskAsync(string userQuery, CancellationToken ct = default);
}
