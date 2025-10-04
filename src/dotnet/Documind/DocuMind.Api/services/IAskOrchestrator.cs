using Documind.Contracts;

namespace DocuMind.Api.Services;

public interface IAskOrchestrator
{
    Task<AskResponse> AskAsync(string userQuery, CancellationToken ct = default);
}
