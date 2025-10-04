// Clients/RagClient.cs
using System.Net.Http.Json;
using System.Text.Json;
using System.Text;
using Documind.Contracts;
using DocuMind.Api.Options;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
namespace DocuMind.Api.Clients;

public sealed class RagClient : IRagClient
{
    private readonly HttpClient _http;
    private readonly ILogger<RagClient> _log;

    public RagClient(HttpClient http, IOptions<RagOptions> options, ILogger<RagClient> log)
    {
        _http = http; _log = log;
    }

    public async Task<string> IndexBlocksAsync(TextBlocksDto dto, CancellationToken ct = default)
    {
        using var res = await _http.PostAsync("/index/blocks",
            new StringContent(JsonSerializer.Serialize(dto), Encoding.UTF8, "application/json"), ct);

        res.EnsureSuccessStatusCode();
        using var doc = JsonDocument.Parse(await res.Content.ReadAsStringAsync(ct));
        return doc.RootElement.TryGetProperty("batchId", out var b) ? (b.GetString() ?? "unknown") : "unknown";
    }

    // helper
    private async Task<bool> PostOkAsync<T>(string route, T body, CancellationToken ct)
    {
        using var res = await _http.PostAsJsonAsync(route, body, ct);
        return res.IsSuccessStatusCode;
    }

    public async Task<RagAskResponse?> AskAsync(string q, CancellationToken ct = default)
    {
        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Get, $"/ask?q={Uri.EscapeDataString(q)}");
            var r = await _http.SendAsync(req, ct);
            if (!r.IsSuccessStatusCode) return null;

            var opts = new JsonSerializerOptions(JsonSerializerDefaults.Web); // camelCase
            var resp = await r.Content.ReadFromJsonAsync<RagAskResponse>(opts, ct);
            return resp;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "RAG unreachable/timeouts at {Base}", _http.BaseAddress);
            return null;
        }


    }
    public async Task<bool> IngestTextAsync(IngestTextRequest req, CancellationToken ct = default)
    {
        try
        {
            var r = await _http.PostAsJsonAsync("/ingest/text", req, ct);
            return r.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "IngestText failed");
            return false;
        }
    }

    public async Task<bool> IngestUrlAsync(IngestUrlRequest req, CancellationToken ct = default)
    {
        try
        {
            var r = await _http.PostAsJsonAsync("/ingest/url", req, ct);
            return r.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "IngestUrl failed");
            return false;
        }
    }

    public async Task<bool> IngestBlobAsync(IngestBlobRequest req, CancellationToken ct = default)
    {
        try
        {
            var r = await _http.PostAsJsonAsync("/ingest/blob", req, ct);
            return r.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "IngestBlob failed");
            return false;
        }
    }

    public async Task<bool> UploadAsync(IFormFile file, string? docId, CancellationToken ct = default)
    {
        try
        {
            using var content = new MultipartFormDataContent();

            if (!string.IsNullOrWhiteSpace(docId))
                content.Add(new StringContent(docId), "doc_id");

            var stream = file.OpenReadStream();
            var sc = new StreamContent(stream);
            sc.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(file.ContentType ?? "application/octet-stream");
            content.Add(sc, "file", file.FileName);

            var r = await _http.PostAsync("/ingest/upload", content, ct);
            return r.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Upload ingest failed");
            return false;
        }
    }
}
