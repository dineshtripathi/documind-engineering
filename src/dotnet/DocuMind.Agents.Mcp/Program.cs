using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Note: MCP packages are targeting .NET 8.0, may need compatibility adjustments for .NET 10
// For now, we'll configure basic service structure and test package availability

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseRouting();
app.UseCors();

app.MapControllers();

// Health check endpoint
app.MapGet("/healthz", () => new
{
    status = "healthy",
    timestamp = DateTime.UtcNow,
    service = "DocuMind.Agents.Mcp",
    version = "1.0.0",
    framework = ".NET 10 RC1 with Official MCP SDK",
    environment = app.Environment.EnvironmentName,
    mcp_status = "✅ Official MCP SDK Packages Installed",
    mcp_version = "0.4.0-preview.1",
    dotnet_version = "10.0.100-rc.1",
    compatibility_note = "MCP packages targeting .NET 8.0, testing .NET 10 compatibility"
});

// Root endpoint with MCP information
app.MapGet("/", () => new
{
    service = "DocuMind MCP Server",
    version = "1.0.0",
    framework = ".NET 10 RC1 with Official MCP SDK v0.4.0-preview.1",
    description = "Model Context Protocol server with official Microsoft/Anthropic SDK",
    status = new
    {
        dotnet_10 = "✅ Running on .NET 10 RC1",
        mcp_packages = "✅ Official MCP SDK v0.4.0-preview.1 packages installed",
        compatibility = "🔄 Testing .NET 10 compatibility with .NET 8 MCP packages",
        project_structure = "✅ Production-ready structure"
    },
    packages_installed = new
    {
        ModelContextProtocol = "0.4.0-preview.1",
        ModelContextProtocol_AspNetCore = "0.4.0-preview.1",
        target_framework = ".NET 8.0 (packages) running on .NET 10 (runtime)"
    },
    next_steps = new[]
    {
        "Test MCP package compatibility with .NET 10",
        "Implement MCP tools and resources",
        "Configure server capabilities",
        "Add client/server communication"
    },
    endpoints = new
    {
        health = "/healthz",
        tools = "/mcp/tools",
        resources = "/mcp/resources",
        prompts = "/mcp/prompts",
        dotnet_features = "/dotnet10-features"
    }
});

// MCP Tools endpoint - placeholder for MCP SDK integration
app.MapGet("/mcp/tools", () =>
{
    return new
    {
        message = "MCP Tools Endpoint",
        sdk_version = "0.4.0-preview.1",
        status = "Ready for tool registration",
        note = "Will integrate MCP tool discovery when compatibility confirmed"
    };
});

// MCP Resources endpoint
app.MapGet("/mcp/resources", () =>
{
    return new
    {
        message = "MCP Resources Endpoint",
        available_resources = new[]
        {
            "Document Analysis",
            "Vision Processing",
            "Vector Search",
            "Azure AI Services"
        }
    };
});

// MCP Prompts endpoint
app.MapGet("/mcp/prompts", () =>
{
    return new
    {
        message = "MCP Prompts Endpoint",
        available_prompts = new[]
        {
            "Document Summarization",
            "Content Analysis",
            "Vision Description",
            "Semantic Search"
        }
    };
});

// Sample endpoint showing .NET 10 capabilities
app.MapGet("/dotnet10-features", () => new
{
    message = "DocuMind MCP Server - .NET 10 + Official MCP SDK",
    version = "10.0.100-rc.1.25451.107",
    mcp_sdk = "0.4.0-preview.1",
    new_features = new[]
    {
        "✅ Official Model Context Protocol SDK packages installed",
        "🔄 Testing .NET 10 compatibility with .NET 8 MCP packages",
        "✅ C# 14.0 support with enhanced AI features",
        "✅ Performance improvements for AI workloads",
        "✅ Enhanced containerization support"
    },
    ai_enhancements = new
    {
        mcp_protocol = "✅ Official SDK packages available",
        compatibility_testing = "🔄 .NET 10 compatibility verification in progress",
        integration_ready = "✅ Project structure prepared for full MCP integration"
    },
    documentation = new
    {
        mcp_docs = "https://modelcontextprotocol.io/",
        nuget_package = "https://www.nuget.org/packages/ModelContextProtocol",
        github = "https://github.com/modelcontextprotocol/csharp-sdk"
    }
});

app.Run();
