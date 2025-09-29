using DocuMind.Api.Services;
using Polly;
using Polly.Extensions.Http;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddSingleton<AzureOpenAiService>();

builder.Services.AddHttpClient<OllamaClient>(client =>
{
    var baseUrl = builder.Configuration["Ollama:BaseUrl"] ?? "http://127.0.0.1:11434";
    client.BaseAddress = new Uri(baseUrl);
})
.AddPolicyHandler(HttpPolicyExtensions
    .HandleTransientHttpError()
    .WaitAndRetryAsync(new[] { TimeSpan.FromMilliseconds(200), TimeSpan.FromMilliseconds(500), TimeSpan.FromSeconds(1) }));

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapGet("/healthz", () => Results.Ok(new { ok = true, ts = DateTimeOffset.UtcNow }));

// Minimal /ask: local-first, fallback to AOAI if "not found"
app.MapPost("/ask", async (
    AzureOpenAiService aoai,
    OllamaClient ollama,
    IConfiguration cfg,
    AskRequest req) =>
{
    string system = "You are DocuMind. Be concise.";
    // Prompt is already built by Python RAG or we can pass plain q for now
    var localModel = cfg["Ollama:Model"] ?? "phi3.5:3.8b-mini-instruct-q4_0";

    var local = await ollama.GenerateAsync(localModel, req.Prompt ?? req.Q ?? "");
    if (!string.IsNullOrWhiteSpace(local) && !local.Trim().Equals("not found", StringComparison.OrdinalIgnoreCase))
        return Results.Ok(new { route = "local", answer = local });

    // Fallback to AOAI
    var deployment = cfg["AzureOpenAI:Deployment"] ?? "gpt-4o-mini";
    var cloud = await aoai.ChatAsync(deployment, system, req.Q ?? req.Prompt ?? "");
    return Results.Ok(new { route = "aoai", answer = cloud });
});

app.Run();

public sealed record AskRequest(string? Q, string? Prompt);
