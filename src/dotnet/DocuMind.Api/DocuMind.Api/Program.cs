using DocuMind.Api.Clients;
using DocuMind.Api.Middleware;
using DocuMind.Api.Options;
using DocuMind.Api.Services;
using Polly;
using Polly.Extensions.Http;
using System.Net.Http.Headers;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

// Options binding
builder.Services.Configure<RagOptions>(builder.Configuration.GetSection("Rag"));
builder.Services.Configure<AzureOpenAiOptions>(builder.Configuration.GetSection("AzureOpenAI"));
builder.Services.Configure<OllamaOptions>(builder.Configuration.GetSection("Ollama"));

// Controllers + Swagger
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SupportNonNullableReferenceTypes();
});

static IAsyncPolicy<HttpResponseMessage> QuietRetryPolicy()
{
    var delays = new[] { TimeSpan.FromMilliseconds(100), TimeSpan.FromMilliseconds(300) };
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .OrResult(r => (int)r.StatusCode == 429)
        .WaitAndRetryAsync(new[]
    {
        TimeSpan.FromMilliseconds(200),
        TimeSpan.FromMilliseconds(500),
        TimeSpan.FromSeconds(10)
    }); // no logging, totally quiet
}
// Polly retry for HTTP
var retryPolicy = HttpPolicyExtensions
    .HandleTransientHttpError()
    .OrResult(r => (int)r.StatusCode == 429)
    .WaitAndRetryAsync(new[]
    {
        TimeSpan.FromMilliseconds(200),
        TimeSpan.FromMilliseconds(500),
        TimeSpan.FromSeconds(1)
    });

// HttpClients
builder.Services.Configure<RagOptions>(builder.Configuration.GetSection(RagOptions.Section));
builder.Services.AddHttpClient<IRagClient, RagClient>((sp, http) =>
{
    var o = sp.GetRequiredService<IOptions<RagOptions>>().Value;
    http.BaseAddress = new Uri(o.BaseUrl.TrimEnd('/'));
    http.Timeout = TimeSpan.FromSeconds(o.TimeoutSeconds);
})
.AddPolicyHandler(HttpPolicyExtensions
    .HandleTransientHttpError()
    .WaitAndRetryAsync(new[]
    {
        TimeSpan.FromMilliseconds(200),
        TimeSpan.FromMilliseconds(500),
        TimeSpan.FromSeconds(1)
    }));

builder.Services.AddHttpClient<IOllamaClient, OllamaClient>((sp, http) =>
{
    var opt = sp.GetRequiredService<Microsoft.Extensions.Options.IOptions<OllamaOptions>>().Value;
    http.BaseAddress = new Uri(opt.BaseUrl);
    http.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
}).AddPolicyHandler(retryPolicy);

// Services
builder.Services.AddSingleton<IAzureOpenAiService, AzureOpenAiService>();
builder.Services.AddScoped<IAskOrchestrator, AskOrchestrator>();
builder.Services.Configure<FeatureFlags>(
    builder.Configuration.GetSection("FeatureFlags"));

var app = builder.Build();

app.UseMiddleware<ErrorHandlingMiddleware>();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapControllers();
app.MapGet("/healthz", () => Results.Ok(new { ok = true, ts = DateTimeOffset.UtcNow }));

app.Run();




// using DocuMind.Api.Services;
// using Polly;
// using Polly.Extensions.Http;

// var builder = WebApplication.CreateBuilder(args);

// builder.Services.AddEndpointsApiExplorer();
// builder.Services.AddSwaggerGen();

// builder.Services.AddSingleton<AzureOpenAiService>();

// builder.Services.AddHttpClient<OllamaClient>(client =>
// {
//     var baseUrl = builder.Configuration["Ollama:BaseUrl"] ?? "http://127.0.0.1:11434";
//     client.BaseAddress = new Uri(baseUrl);
// })
// .AddPolicyHandler(HttpPolicyExtensions
//     .HandleTransientHttpError()
//     .WaitAndRetryAsync(new[] { TimeSpan.FromMilliseconds(200), TimeSpan.FromMilliseconds(500), TimeSpan.FromSeconds(1) }));

// var app = builder.Build();

// if (app.Environment.IsDevelopment())
// {
//     app.UseSwagger();
//     app.UseSwaggerUI();
// }

// app.MapGet("/healthz", () => Results.Ok(new { ok = true, ts = DateTimeOffset.UtcNow }));

// // Minimal /ask: local-first, fallback to AOAI if "not found"
// app.MapPost("/ask", async (
//     AskRequest req,
//     AzureOpenAiService aoai,
//     RagClient rag, // your HTTP client to python sidecar
//     ILoggerFactory lf) =>
// {
//     var logger = lf.CreateLogger("Ask");
//     string userQ = req.Q ?? req.Prompt ?? "";
//     if (string.IsNullOrWhiteSpace(userQ)) return Results.BadRequest("Missing q/prompt");

//     // 1) RAG call
//     var ragResp = await rag.SearchAsync(userQ); // returns ranked chunks + prompt
//     // 2) Build final prompt
//     var prompt = PromptBuilder.FromRag(userQ, ragResp);
//     // 3) Azure OpenAI call
//     var answer = await aoai.ChatAsync(
//         deployment: Environment.GetEnvironmentVariable("AOAI_DEPLOYMENT")!,
//         system: "Answer strictly from context; cite sources.",
//         user: prompt);
//     return Results.Ok(new { answer });
// })
// .Accepts<AskRequest>("application/json")
// .Produces(StatusCodes.Status200OK)
// .Produces(StatusCodes.Status400BadRequest);

// app.MapGet("/ask", async (string q, AzureOpenAiService aoai, RagClient rag) => { /* same */ });

// app.Run();

// public sealed record AskRequest(string? Q, string? Prompt);
