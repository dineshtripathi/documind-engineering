using System.Text.Json.Serialization;

namespace DocuMind.Agents.Models;

/// <summary>
/// Base request for agent operations
/// </summary>
public class AgentRequest
{
    [JsonPropertyName("user_message")]
    public string UserMessage { get; set; } = string.Empty;

    [JsonPropertyName("session_id")]
    public string SessionId { get; set; } = Guid.NewGuid().ToString();

    [JsonPropertyName("context")]
    public Dictionary<string, object> Context { get; set; } = new();
}

/// <summary>
/// Request for document processing agents
/// </summary>
public class DocumentAgentRequest : AgentRequest
{
    [JsonPropertyName("file_content")]
    public string? FileContent { get; set; }

    [JsonPropertyName("file_name")]
    public string? FileName { get; set; }

    [JsonPropertyName("processing_type")]
    public string ProcessingType { get; set; } = "analysis"; // analysis, extraction, summary
}

/// <summary>
/// Request for vision processing agents
/// </summary>
public class VisionAgentRequest : AgentRequest
{
    [JsonPropertyName("image_data")]
    public string? ImageData { get; set; } // Base64 encoded image

    [JsonPropertyName("analysis_type")]
    public string AnalysisType { get; set; } = "general"; // general, text_extraction, object_detection
}

/// <summary>
/// Request for search operations
/// </summary>
public class SearchAgentRequest : AgentRequest
{
    [JsonPropertyName("query")]
    public string Query { get; set; } = string.Empty;

    [JsonPropertyName("search_type")]
    public string SearchType { get; set; } = "semantic"; // semantic, exact, hybrid

    [JsonPropertyName("max_results")]
    public int MaxResults { get; set; } = 10;
}

/// <summary>
/// Multi-agent orchestration request
/// </summary>
public class OrchestrationRequest : AgentRequest
{
    [JsonPropertyName("workflow_type")]
    public string WorkflowType { get; set; } = "document_intelligence"; // document_intelligence, research, analysis

    [JsonPropertyName("inputs")]
    public Dictionary<string, object> Inputs { get; set; } = new();
}
