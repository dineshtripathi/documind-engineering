namespace DocuMind.Api.Options;

public sealed class AzureVisionOptions
{
    public const string Section = "AzureVision";
    public string Endpoint { get; set; } = string.Empty;
    public string Key { get; set; } = string.Empty;
}
