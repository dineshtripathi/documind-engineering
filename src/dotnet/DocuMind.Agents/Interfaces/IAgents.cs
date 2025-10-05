using DocuMind.Agents.Models;

namespace DocuMind.Agents.Interfaces;

/// <summary>
/// Base interface for all agents
/// </summary>
public interface IAgent
{
    string AgentType { get; }
    Task<AgentResponse> ProcessAsync(AgentRequest request, CancellationToken cancellationToken = default);
}

/// <summary>
/// Specialized agent for document processing
/// </summary>
public interface IDocumentAgent : IAgent
{
    Task<DocumentAgentResponse> ProcessDocumentAsync(DocumentAgentRequest request, CancellationToken cancellationToken = default);
    Task<string> ExtractTextAsync(string fileContent, string fileName, CancellationToken cancellationToken = default);
    Task<string> SummarizeAsync(string content, CancellationToken cancellationToken = default);
}

/// <summary>
/// Specialized agent for vision processing
/// </summary>
public interface IVisionAgent : IAgent
{
    Task<VisionAgentResponse> ProcessImageAsync(VisionAgentRequest request, CancellationToken cancellationToken = default);
    Task<string> AnalyzeImageAsync(string imageData, string analysisType, CancellationToken cancellationToken = default);
    Task<string> ExtractTextFromImageAsync(string imageData, CancellationToken cancellationToken = default);
}

/// <summary>
/// Specialized agent for search operations
/// </summary>
public interface ISearchAgent : IAgent
{
    Task<SearchAgentResponse> SearchAsync(SearchAgentRequest request, CancellationToken cancellationToken = default);
    Task<List<SearchResult>> SemanticSearchAsync(string query, int maxResults, CancellationToken cancellationToken = default);
    Task<List<SearchResult>> HybridSearchAsync(string query, int maxResults, CancellationToken cancellationToken = default);
}

/// <summary>
/// Orchestrator for managing multiple agents
/// </summary>
public interface IAgentOrchestrator
{
    Task<OrchestrationResponse> OrchestrateworkflowAsync(OrchestrationRequest request, CancellationToken cancellationToken = default);
    Task<AgentResponse> RouteToAgentAsync(AgentRequest request, string agentType, CancellationToken cancellationToken = default);
    Task<OrchestrationResponse> ExecuteDocumentIntelligenceWorkflowAsync(Dictionary<string, object> inputs, string sessionId, CancellationToken cancellationToken = default);
}
