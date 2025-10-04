using System.Security.Cryptography;
using System.Text;
using Documind.Contracts;
using Documind.Common.Utilities;
using Documind.Common.Extensions;

namespace Documind.Vision.Services;

/// <summary>
/// Vision processing service implementation using Azure AI Vision
/// </summary>
public class VisionService : IVisionService
{
    private readonly AzureVisionClient _azureClient;
    private readonly ILogger<VisionService> _logger;

    public VisionService(AzureVisionClient azureClient, ILogger<VisionService> logger)
    {
        _azureClient = azureClient;
        _logger = logger;
    }

    public async Task<TextBlocksDto> AnalyzeUrlAsync(string url, string? language, string[]? features, CancellationToken ct = default)
    {
        var correlationId = CorrelationIdGenerator.Generate();

        _logger.LogInformation("Starting URL analysis: {Url}, Language: {Language}, CorrelationId: {CorrelationId}",
            url, language, correlationId);

        try
        {
            var endpoint = GetRequiredEnvVar("AZURE_VISION_ENDPOINT");
            var key = GetRequiredEnvVar("AZURE_VISION_KEY");

            var json = await _azureClient.AnalyzeUrlAsync(endpoint, key, url, features, language, ct);
            var sourceId = GenerateSourceId(url);
            var sourceType = GuessType(url);

            var result = VisionNormalize.ToTextBlocksDto(json, sourceId, url, sourceType, language ?? "en");

            _logger.LogInformation("URL analysis completed successfully. CorrelationId: {CorrelationId}, Blocks: {BlockCount}",
                correlationId, result.Blocks.Count);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during URL analysis. CorrelationId: {CorrelationId}", correlationId);
            throw;
        }
    }

    public async Task<TextBlocksDto> AnalyzeFileAsync(Stream stream, string fileName, string? language, CancellationToken ct = default)
    {
        var correlationId = CorrelationIdGenerator.Generate();

        _logger.LogInformation("Starting file analysis: {FileName}, Language: {Language}, Size: {Size} bytes, CorrelationId: {CorrelationId}",
            fileName, language, stream.Length, correlationId);

        try
        {
            var endpoint = GetRequiredEnvVar("AZURE_VISION_ENDPOINT");
            var key = GetRequiredEnvVar("AZURE_VISION_KEY");

            var json = await _azureClient.AnalyzeBytesAsync(endpoint, key, stream, null, language, ct);
            var sourceId = GenerateSourceId(fileName);
            var sourceType = GuessType(fileName);

            var result = VisionNormalize.ToTextBlocksDto(json, sourceId, fileName, sourceType, language ?? "en");

            _logger.LogInformation("File analysis completed successfully. CorrelationId: {CorrelationId}, Blocks: {BlockCount}",
                correlationId, result.Blocks.Count);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during file analysis. CorrelationId: {CorrelationId}", correlationId);
            throw;
        }
    }

    public async Task<string> AnalyzeBytesAsync(
        string endpoint, string key, Stream bytes,
        string[]? features, string? language, CancellationToken ct)
    {
        return await _azureClient.AnalyzeBytesAsync(endpoint, key, bytes, features, language, ct);
    }

    private static string GetRequiredEnvVar(string name)
    {
        return Environment.GetEnvironmentVariable(name)
            ?? throw new InvalidOperationException($"Environment variable {name} is not set");
    }

    private static string GuessType(string name) =>
        name.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase) ? "pdf" : "image";

    private static string GenerateSourceId(string seed) =>
        "src-" + Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(seed))).ToLowerInvariant()[..12];
}
