namespace DocuMind.Api.Options;
public sealed class AzureOpenAiOptions
{
    public string Endpoint { get; set; } = default!;
    public string Key { get; set; } = default!;
    public string Deployment { get; set; } = "gpt-4o-mini";
}
