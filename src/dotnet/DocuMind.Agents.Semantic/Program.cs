using DocuMind.Agents.Interfaces;
using DocuMind.Agents.Options;
using DocuMind.Agents.Services;
using Microsoft.SemanticKernel;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Configure Swagger
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "DocuMind Agents API",
        Version = "v1.0",
        Description = "AI Agent Orchestration API for DocuMind - Multi-agent system for document intelligence, vision processing, and search operations",
        Contact = new OpenApiContact
        {
            Name = "DocuMind Engineering",
            Email = "engineering@documind.com"
        }
    });

    // Include XML comments for better API documentation
    var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath))
    {
        options.IncludeXmlComments(xmlPath);
    }

    // Add security definition for future API key authentication
    options.AddSecurityDefinition("ApiKey", new OpenApiSecurityScheme
    {
        Description = "API Key needed to access the endpoints",
        In = ParameterLocation.Header,
        Name = "X-API-Key",
        Type = SecuritySchemeType.ApiKey
    });
});

// Configure Agent options
builder.Services.Configure<AgentOptions>(
    builder.Configuration.GetSection(AgentOptions.SectionName));

// Configure HTTP clients
builder.Services.AddHttpClient();

// Configure Semantic Kernel
builder.Services.AddSingleton<Kernel>(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var agentOptions = configuration.GetSection(AgentOptions.SectionName).Get<AgentOptions>() ?? new AgentOptions();

    var kernelBuilder = Kernel.CreateBuilder();

    // Add Azure OpenAI chat completion service
    if (!string.IsNullOrEmpty(agentOptions.AzureOpenAI.Endpoint) &&
        !string.IsNullOrEmpty(agentOptions.AzureOpenAI.ApiKey))
    {
        kernelBuilder.AddAzureOpenAIChatCompletion(
            deploymentName: agentOptions.AzureOpenAI.DeploymentName,
            endpoint: agentOptions.AzureOpenAI.Endpoint,
            apiKey: agentOptions.AzureOpenAI.ApiKey);
    }
    else
    {
        // Fallback configuration - use environment variables
        var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT") ?? "https://your-resource.openai.azure.com/";
        var apiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY") ?? "your-api-key";
        var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? "gpt-4";

        if (apiKey != "your-api-key" && endpoint != "https://your-resource.openai.azure.com/")
        {
            kernelBuilder.AddAzureOpenAIChatCompletion(
                deploymentName: deploymentName,
                endpoint: endpoint,
                apiKey: apiKey);
        }
    }

    return kernelBuilder.Build();
});

// Register agent services
builder.Services.AddScoped<IDocumentAgent, DocumentAgent>();
builder.Services.AddScoped<IVisionAgent, VisionAgent>();
builder.Services.AddScoped<ISearchAgent, SearchAgent>();
builder.Services.AddScoped<IAgentOrchestrator, AgentOrchestrator>();

// Register learning workflows service
builder.Services.AddScoped<LearningWorkflows>();

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Add logging
builder.Services.AddLogging(logging =>
{
    logging.AddConsole();
    logging.AddDebug();
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "DocuMind Agents API v1.0");
        options.RoutePrefix = "swagger";
        options.DisplayRequestDuration();
        options.EnableTryItOutByDefault();
        options.DocExpansion(Swashbuckle.AspNetCore.SwaggerUI.DocExpansion.None);
    });
}

app.UseRouting();
app.UseCors();

app.MapControllers();

// Health check endpoint
app.MapGet("/healthz", () => new
{
    status = "healthy",
    timestamp = DateTime.UtcNow,
    service = "DocuMind.Agents",
    version = "1.0.0",
    environment = app.Environment.EnvironmentName
});

// Root endpoint with API information
app.MapGet("/", () => new
{
    service = "DocuMind Agents API",
    version = "1.0.0",
    description = "AI Agent Orchestration System for Document Intelligence",
    documentation = "/swagger",
    health = "/healthz",
    endpoints = new
    {
        orchestration = "/api/agents/orchestrate",
        document_processing = "/api/agents/document/process",
        vision_processing = "/api/agents/vision/process",
        search = "/api/agents/search",
        workflows = "/api/agents/workflows/document-intelligence"
    }
});

app.Run();
