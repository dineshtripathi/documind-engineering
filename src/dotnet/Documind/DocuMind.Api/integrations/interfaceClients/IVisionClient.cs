using Documind.Contracts;

namespace DocuMind.Api.Clients;

/// <summary>
/// Interface for communicating with the Vision API service
/// </summary>
public interface IVisionClient
{
    /// <summary>
    /// Analyze an image from a URL using the Vision API
    /// </summary>
    Task<TextBlocksDto> AnalyzeUrlAsync(string url, string? language, string[]? features, CancellationToken ct = default);

    /// <summary>
    /// Analyze an uploaded image file using the Vision API
    /// </summary>
    Task<TextBlocksDto> AnalyzeFileAsync(Stream stream, string fileName, string? language, CancellationToken ct = default);
}
