namespace DocuMind.Agents.AgentFramework.Options;

/// <summary>
/// Configuration options for Microsoft Agent Framework
/// </summary>
public class AgentFrameworkOptions
{
    public const string SectionName = "AgentFramework";

    /// <summary>
    /// Azure OpenAI configuration
    /// </summary>
    public AzureOpenAIOptions AzureOpenAI { get; set; } = new();

    /// <summary>
    /// Service endpoints for existing APIs
    /// </summary>
    public ServiceEndpoints ServiceEndpoints { get; set; } = new();

    /// <summary>
    /// Agent Framework specific configurations
    /// </summary>
    public AgentWorkflowConfig AgentWorkflow { get; set; } = new();
}

/// <summary>
/// Azure OpenAI configuration for Agent Framework
/// </summary>
public class AzureOpenAIOptions
{
    public string Endpoint { get; set; } = string.Empty;
    public string ApiKey { get; set; } = string.Empty;
    public string DeploymentName { get; set; } = "gpt-4o-mini";
    public string ApiVersion { get; set; } = "2024-06-01";
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
/// Agent Framework workflow configuration
/// </summary>
public class AgentWorkflowConfig
{
    public int MaxAgents { get; set; } = 10;
    public int WorkflowTimeoutSeconds { get; set; } = 120;
    public bool EnableParallelExecution { get; set; } = true;
    public bool EnableWorkflowCheckpoints { get; set; } = true;
    public string LogLevel { get; set; } = "Information";
}
