// using DocuMind.Contracts; // Add the correct namespace for TextBlocksDto
using Documind.Contracts; // Replace with the actual namespace containing TextBlocksDto

public interface IVisionClient
{
    Task<TextBlocksDto> AnalyzeUrlAsync(string url, string? language, string[]? features, CancellationToken ct = default);
    Task<TextBlocksDto> AnalyzeFileAsync(Stream stream, string fileName, string? language, CancellationToken ct = default);
}
