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
    AskRequest req,
    AzureOpenAiService aoai,
    RagClient rag, // your HTTP client to python sidecar
    ILoggerFactory lf) =>
{
    var logger = lf.CreateLogger("Ask");
    string userQ = req.Q ?? req.Prompt ?? "";
    if (string.IsNullOrWhiteSpace(userQ)) return Results.BadRequest("Missing q/prompt");

    // 1) RAG call
    var ragResp = await rag.SearchAsync(userQ); // returns ranked chunks + prompt
    // 2) Build final prompt
    var prompt = PromptBuilder.FromRag(userQ, ragResp);
    // 3) Azure OpenAI call
    var answer = await aoai.ChatAsync(
        deployment: Environment.GetEnvironmentVariable("AOAI_DEPLOYMENT")!,
        system: "Answer strictly from context; cite sources.",
        user: prompt);
    return Results.Ok(new { answer });
})
.Accepts<AskRequest>("application/json")
.Produces(StatusCodes.Status200OK)
.Produces(StatusCodes.Status400BadRequest);

app.MapGet("/ask", async (string q, AzureOpenAiService aoai, RagClient rag) => { /* same */ });

app.Run();

public sealed record AskRequest(string? Q, string? Prompt);
