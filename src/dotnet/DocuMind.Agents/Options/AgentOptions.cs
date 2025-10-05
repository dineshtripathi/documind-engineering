namespace DocuMind.Agents.Options;

/// <summary>
/// Configuration options for Semantic Kernel and Azure AI services
/// </summary>
public class AgentOptions
{
    public const string SectionName = "Agents";

    /// <summary>
    /// Azure OpenAI configuration
    /// </summary>
    public AzureOpenAIOptions AzureOpenAI { get; set; } = new();

    /// <summary>
    /// Service endpoints for existing APIs
    /// </summary>
    public ServiceEndpoints ServiceEndpoints { get; set; } = new();

    /// <summary>
    /// Agent-specific configurations
    /// </summary>
    public AgentConfigurations AgentConfig { get; set; } = new();
}

/// <summary>
/// Azure OpenAI configuration for Semantic Kernel
/// </summary>
public class AzureOpenAIOptions
{
    public string Endpoint { get; set; } = string.Empty;
    public string ApiKey { get; set; } = string.Empty;
    public string DeploymentName { get; set; } = "gpt-4"; // Default deployment
    public string ApiVersion { get; set; } = "2024-02-01";
}

/// <summary>
/// Service endpoints for integration with existing APIs
/// </summary>
public class ServiceEndpoints
{
    public string DocumentApiUrl { get; set; } = "http://localhost:5266";
    public string VisionApiUrl { get; set; } = "http://localhost:7002";
    public string RagApiUrl { get; set; } = "http://localhost:7001";
    public string QdrantUrl { get; set; } = "http://localhost:6333";
}

/// <summary>
/// Agent-specific configuration settings
/// </summary>
public class AgentConfigurations
{
    public DocumentAgentConfig DocumentAgent { get; set; } = new();
    public VisionAgentConfig VisionAgent { get; set; } = new();
    public SearchAgentConfig SearchAgent { get; set; } = new();
    public OrchestratorConfig Orchestrator { get; set; } = new();
}

public class DocumentAgentConfig
{
    public int MaxTokens { get; set; } = 4000;
    public double Temperature { get; set; } = 0.7;
    public int TimeoutSeconds { get; set; } = 30;
}

public class VisionAgentConfig
{
    public int MaxTokens { get; set; } = 2000;
    public double Temperature { get; set; } = 0.5;
    public int TimeoutSeconds { get; set; } = 45;
}

public class SearchAgentConfig
{
    public int DefaultMaxResults { get; set; } = 10;
    public double MinRelevanceScore { get; set; } = 0.7;
    public int TimeoutSeconds { get; set; } = 15;
}

public class OrchestratorConfig
{
    public int MaxWorkflowSteps { get; set; } = 10;
    public int WorkflowTimeoutSeconds { get; set; } = 120;
    public bool EnableParallelExecution { get; set; } = true;
}
