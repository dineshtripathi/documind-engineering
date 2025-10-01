using DocuMind.Api.Models;
namespace DocuMind.Api.Clients;
public interface IRagClient { Task<RagAskResponse?> AskAsync(string q, CancellationToken ct = default); }
