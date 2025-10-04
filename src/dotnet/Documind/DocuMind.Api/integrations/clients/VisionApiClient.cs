using Documind.Contracts;
using DocuMind.Api.Clients;
using Documind.Common.Models;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace DocuMind.Api.Clients;

/// <summary>
/// HTTP client for communicating with the Vision API service
/// </summary>
public sealed class VisionApiClient : IVisionClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<VisionApiClient> _logger;
    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNameCaseInsensitive = true };

    public VisionApiClient(HttpClient httpClient, ILogger<VisionApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<TextBlocksDto> AnalyzeUrlAsync(string url, string? language, string[]? features, CancellationToken ct = default)
    {
        _logger.LogInformation("Sending URL analysis request to Vision API: {Url}", url);

        var payload = new IngestUrlRequest(url, null, language, features);
        var json = JsonSerializer.Serialize(payload);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync("/vision/analyze-url", content, ct);
        response.EnsureSuccessStatusCode();

        var responseContent = await response.Content.ReadAsStringAsync(ct);
        var result = JsonSerializer.Deserialize<OperationResult<TextBlocksDto>>(responseContent, JsonOptions);

        if (result?.IsSuccess == true && result.Data != null)
        {
            return result.Data;
        }

        throw new InvalidOperationException($"Vision API returned error: {result?.ErrorMessage ?? "Unknown error"}");
    }

    public async Task<TextBlocksDto> AnalyzeFileAsync(Stream stream, string fileName, string? language, CancellationToken ct = default)
    {
        _logger.LogInformation("Sending file analysis request to Vision API: {FileName}", fileName);

        using var form = new MultipartFormDataContent();
        var streamContent = new StreamContent(stream);
        streamContent.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");
        form.Add(streamContent, "File", fileName);

        if (!string.IsNullOrWhiteSpace(language))
        {
            form.Add(new StringContent(language), "Language");
        }

        var response = await _httpClient.PostAsync("/vision/analyze", form, ct);
        response.EnsureSuccessStatusCode();

        var responseContent = await response.Content.ReadAsStringAsync(ct);
        var result = JsonSerializer.Deserialize<OperationResult<TextBlocksDto>>(responseContent, JsonOptions);

        if (result?.IsSuccess == true && result.Data != null)
        {
            return result.Data;
        }

        throw new InvalidOperationException($"Vision API returned error: {result?.ErrorMessage ?? "Unknown error"}");
    }
}
