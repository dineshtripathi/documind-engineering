namespace DocuMind.Api.Options;
public sealed class FeatureFlags
{
    public bool UseRagFirst { get; set; } = true;  // try local first
    public bool RagRequired { get; set; } = false; // if true and RAG down -> 503
}
