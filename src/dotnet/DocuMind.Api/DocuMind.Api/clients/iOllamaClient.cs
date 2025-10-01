namespace DocuMind.Api.Clients;
public interface IOllamaClient
{
    Task<string> GenerateAsync(string prompt, string? modelOverride = null, double? temperature = null, CancellationToken ct = default);
    Task<string> ChatAsync(string user, string? system = null, string? modelOverride = null, double? temperature = null, CancellationToken ct = default);
}
