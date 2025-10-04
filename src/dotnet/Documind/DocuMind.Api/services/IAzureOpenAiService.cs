namespace DocuMind.Api.Services;
public interface IAzureOpenAiService
{
    Task<string> ChatAsync(string system, string user, CancellationToken ct = default, string? deployment = null);
}
