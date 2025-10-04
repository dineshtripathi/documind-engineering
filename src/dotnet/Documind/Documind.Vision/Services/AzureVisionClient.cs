using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Documind.Contracts;

namespace Documind.Vision.Services;

/// <summary>
/// Azure AI Vision client for computer vision and OCR operations
/// </summary>
public class AzureVisionClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AzureVisionClient> _logger;

    public AzureVisionClient(HttpClient httpClient, ILogger<AzureVisionClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    /// <summary>
    /// Analyzes an image from a URL using Azure Computer Vision API
    /// </summary>
    public async Task<string> AnalyzeUrlAsync(
        string endpoint,
        string key,
        string imageUrl,
        string[]? features = null,
        string? language = null,
        CancellationToken ct = default)
    {
        var feat = (features?.Length > 0) ? string.Join(',', features) : "Read,Caption,Tags";
        var apiUrl = $"{endpoint.TrimEnd('/')}/computervision/imageanalysis:analyze?api-version=2023-10-01&features={feat}";

        if (!string.IsNullOrWhiteSpace(language))
            apiUrl += $"&language={Uri.EscapeDataString(language)}";

        var requestBody = JsonSerializer.Serialize(new { url = imageUrl });

        using var request = new HttpRequestMessage(HttpMethod.Post, apiUrl);
        request.Headers.Add("Ocp-Apim-Subscription-Key", key);
        request.Content = new StringContent(requestBody, Encoding.UTF8, "application/json");

        _logger.LogInformation("Calling Azure Vision API: {Url}", apiUrl);

        var response = await _httpClient.SendAsync(request, ct);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadAsStringAsync(ct);
        _logger.LogDebug("Azure Vision API response: {Response}", result);

        return result;
    }

    /// <summary>
    /// Analyzes an image from bytes using Azure Computer Vision API
    /// </summary>
    public async Task<string> AnalyzeBytesAsync(
        string endpoint,
        string key,
        Stream imageStream,
        string[]? features = null,
        string? language = null,
        CancellationToken ct = default)
    {
        var feat = (features?.Length > 0) ? string.Join(',', features) : "Read,Caption,Tags";
        var apiUrl = $"{endpoint.TrimEnd('/')}/computervision/imageanalysis:analyze?api-version=2023-10-01&features={feat}";

        if (!string.IsNullOrWhiteSpace(language))
            apiUrl += $"&language={Uri.EscapeDataString(language)}";

        using var request = new HttpRequestMessage(HttpMethod.Post, apiUrl);
        request.Headers.Add("Ocp-Apim-Subscription-Key", key);
        request.Content = new StreamContent(imageStream);
        request.Content.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");

        _logger.LogInformation("Calling Azure Vision API with binary data: {Url}", apiUrl);

        var response = await _httpClient.SendAsync(request, ct);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadAsStringAsync(ct);
        _logger.LogDebug("Azure Vision API response: {Response}", result);

        return result;
    }
}
