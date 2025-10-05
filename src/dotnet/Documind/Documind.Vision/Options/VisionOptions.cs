namespace Documind.Vision.Options;

public sealed class VisionOptions
{
    public const string Section = "VisionSettings";
    public int MaxFileSizeMB { get; set; } = 10;
    public string[] SupportedFormats { get; set; } = new[] { "jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp" };
    public int ProcessingTimeoutSeconds { get; set; } = 30;
    public bool DemoMode { get; set; } = false;
}
