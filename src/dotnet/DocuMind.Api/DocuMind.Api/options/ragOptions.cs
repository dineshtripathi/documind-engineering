namespace DocuMind.Api.Options;
public sealed class RagOptions
{
    public string BaseUrl { get; set; } = "http://127.0.0.1:7001";
    public int TimeoutSeconds { get; set; } = 5;
}
