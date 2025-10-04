using Microsoft.AspNetCore.Http;
namespace Documind.Contracts;

public sealed class UploadIngestForm
{
    public IFormFile File { get; set; } = default!;   // required
    public string? DocId { get; set; }                // optional
    public string? Language { get; set; }             // optional (used by VisionFile)
}

