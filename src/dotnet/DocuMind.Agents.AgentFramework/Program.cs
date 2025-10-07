using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.SemanticKernel;
// using Microsoft.OpenApi.Models;
using DocuMind.Agents.AgentFramework.Services;
using DocuMind.Agents.AgentFramework.Options;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Configure Swagger - Simplified for .NET 10 compatibility
builder.Services.AddSwaggerGen();

// Configure Agent Framework options
builder.Services.Configure<AgentFrameworkOptions>(
    builder.Configuration.GetSection(AgentFrameworkOptions.SectionName));

// Configure HTTP clients
builder.Services.AddHttpClient();

// Add Semantic Kernel for agent creation
builder.Services.AddKernel();

// Configure Azure OpenAI for Agent Framework with Semantic Kernel
var agentFrameworkConfig = builder.Configuration.GetSection(AgentFrameworkOptions.SectionName).Get<AgentFrameworkOptions>() ?? new AgentFrameworkOptions();
var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT") ?? agentFrameworkConfig.AzureOpenAI.Endpoint;
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? agentFrameworkConfig.AzureOpenAI.DeploymentName;
var apiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY") ?? agentFrameworkConfig.AzureOpenAI.ApiKey;

if (!string.IsNullOrEmpty(endpoint) && !string.IsNullOrEmpty(apiKey) && !string.IsNullOrEmpty(deploymentName))
{
    // Add Azure OpenAI Chat Completion to Semantic Kernel
    builder.Services.AddAzureOpenAIChatCompletion(
        deploymentName: deploymentName,
        endpoint: endpoint,
        apiKey: apiKey);
}
else if (!string.IsNullOrEmpty(endpoint) && !string.IsNullOrEmpty(deploymentName))
{
    // Use Azure CLI credential for authentication
    builder.Services.AddAzureOpenAIChatCompletion(
        deploymentName: deploymentName,
        endpoint: endpoint,
        credentials: new AzureCliCredential());
}
else
{
    throw new InvalidOperationException("Azure OpenAI endpoint and deployment name must be configured for Agent Framework");
}

// Register Agent Framework services
builder.Services.AddScoped<AgentFrameworkOrchestratorCompatible>();
builder.Services.AddScoped<AgentFrameworkLearningWorkflowsCompatible>();

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

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "DocuMind Agents API - Agent Framework v1.0");
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
    service = "DocuMind.Agents.AgentFramework",
    version = "1.0.0",
    framework = "Microsoft Agent Framework",
    environment = app.Environment.EnvironmentName
});

// Root endpoint with API information
app.MapGet("/", () => new
{
    service = "DocuMind Agents API - Agent Framework",
    version = "1.0.0",
    framework = "Microsoft Agent Framework (Beta)",
    description = "Educational comparison: Native multi-agent system using Microsoft's latest Agent Framework",
    documentation = "/swagger",
    health = "/healthz",
    comparison = new
    {
        semantic_kernel_version = "Available at DocuMind.Agents.Semantic",
        agent_framework_version = "This API - Native multi-agent workflows",
        learning_objective = "Compare approaches for multi-agent orchestration"
    },
    endpoints = new
    {
        learning_workflows = "/api/agent-learning/workflows",
        agent_comparison = "/api/agent-learning/comparison"
    }
});

app.Run();
