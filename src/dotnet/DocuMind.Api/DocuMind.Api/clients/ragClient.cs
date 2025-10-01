// Clients/RagClient.cs
using System.Net.Http.Json;
using DocuMind.Api.Models;
using Microsoft.Extensions.Logging;

namespace DocuMind.Api.Clients;

public sealed class RagClient : IRagClient
{
    private readonly HttpClient _http;
    private readonly ILogger<RagClient> _log;

    public RagClient(HttpClient http, ILogger<RagClient> log)
    {
        _http = http; _log = log;
    }

    public async Task<RagAskResponse?> AskAsync(string q, CancellationToken ct = default)
    {
        try
        {
            var url = $"/ask?q={Uri.EscapeDataString(q)}";
            using var resp = await _http.GetAsync(url, ct);
            if (!resp.IsSuccessStatusCode)
            {
                _log.LogWarning("RAG /ask non-success: {Status}", (int)resp.StatusCode);
                return null;
            }
            return await resp.Content.ReadFromJsonAsync<RagAskResponse>(cancellationToken: ct);
        }
        catch (Exception ex) when (ex is HttpRequestException || ex is TaskCanceledException)
        {
            _log.LogWarning( "RAG unreachable/timeouts at {Base}", _http.BaseAddress);
            return null; // ← key: gracefully fallback
        }
    }
}
