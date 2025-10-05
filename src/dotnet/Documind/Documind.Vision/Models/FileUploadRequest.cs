namespace Documind.Vision.Models;

/// <summary>
/// Model for file upload requests
/// </summary>
public class FileUploadRequest
{
    /// <summary>
    /// The file to analyze
    /// </summary>
    public IFormFile File { get; set; } = null!;

    /// <summary>
    /// Optional language hint for OCR processing
    /// </summary>
    public string? Language { get; set; }
}
