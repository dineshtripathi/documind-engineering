using System.Net.Http.Headers;
using DocuMind.Api.Clients;
using DocuMind.Api.Middleware;
using DocuMind.Api.Options;
using DocuMind.Api.Orchestration;
using DocuMind.Api.Services;
using Microsoft.Extensions.Options;
using Polly;
using Polly.Extensions.Http;

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
builder.Services.AddScoped<IQueryAnalyzer, QueryAnalyzer>();
builder.Services.AddScoped<IConfidenceScorer, ConfidenceScorer>();
builder.Services.Configure<FeatureFlags>(
    builder.Configuration.GetSection("FeatureFlags"));

// Vision API client
builder.Services.AddHttpClient<IVisionClient, VisionApiClient>((sp, http) =>
{
    // TODO: Configure from appsettings
    http.BaseAddress = new Uri("http://localhost:7002");
    http.Timeout = TimeSpan.FromSeconds(30);
});

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
