namespace DocuMind.Api.Options;
public sealed class OllamaOptions
{
    public string BaseUrl { get; set; } = "http://127.0.0.1:11434";
    public string Model { get; set; } = "phi3.5:3.8b-mini-instruct-q4_0";
    public double Temperature { get; set; } = 0.1;
    public int TimeoutSeconds { get; set; } = 30;
}
