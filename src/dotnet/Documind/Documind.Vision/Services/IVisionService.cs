using Documind.Contracts;

namespace Documind.Vision.Services;

/// <summary>
/// Interface for vision processing services
/// </summary>
public interface IVisionService
{
    /// <summary>
    /// Analyze an image from a URL and extract text
    /// </summary>
    Task<TextBlocksDto> AnalyzeUrlAsync(string url, string? language, string[]? features, CancellationToken ct = default);

    /// <summary>
    /// Analyze an uploaded image file and extract text
    /// </summary>
    Task<TextBlocksDto> AnalyzeFileAsync(Stream stream, string fileName, string? language, CancellationToken ct = default);
}
