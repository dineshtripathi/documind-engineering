using System.Text.Json.Serialization;

namespace DocuMind.Agents.Models;

/// <summary>
/// Base response from agent operations
/// </summary>
public class AgentResponse
{
    [JsonPropertyName("success")]
    public bool Success { get; set; } = true;

    [JsonPropertyName("response")]
    public string Response { get; set; } = string.Empty;

    [JsonPropertyName("session_id")]
    public string SessionId { get; set; } = string.Empty;

    [JsonPropertyName("agent_type")]
    public string AgentType { get; set; } = string.Empty;

    [JsonPropertyName("execution_time_ms")]
    public long ExecutionTimeMs { get; set; }

    [JsonPropertyName("metadata")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [JsonPropertyName("error")]
    public string? Error { get; set; }
}

/// <summary>
/// Response from document processing agents
/// </summary>
public class DocumentAgentResponse : AgentResponse
{
    [JsonPropertyName("extracted_text")]
    public string? ExtractedText { get; set; }

    [JsonPropertyName("summary")]
    public string? Summary { get; set; }

    [JsonPropertyName("insights")]
    public List<string> Insights { get; set; } = new();

    [JsonPropertyName("confidence_score")]
    public double ConfidenceScore { get; set; }
}

/// <summary>
/// Response from vision processing agents
/// </summary>
public class VisionAgentResponse : AgentResponse
{
    [JsonPropertyName("detected_objects")]
    public List<string> DetectedObjects { get; set; } = new();

    [JsonPropertyName("extracted_text")]
    public string? ExtractedText { get; set; }

    [JsonPropertyName("image_description")]
    public string? ImageDescription { get; set; }

    [JsonPropertyName("confidence_scores")]
    public Dictionary<string, double> ConfidenceScores { get; set; } = new();
}

/// <summary>
/// Response from search agents
/// </summary>
public class SearchAgentResponse : AgentResponse
{
    [JsonPropertyName("results")]
    public List<SearchResult> Results { get; set; } = new();

    [JsonPropertyName("total_count")]
    public int TotalCount { get; set; }

    [JsonPropertyName("search_time_ms")]
    public long SearchTimeMs { get; set; }
}

/// <summary>
/// Individual search result
/// </summary>
public class SearchResult
{
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    [JsonPropertyName("score")]
    public double Score { get; set; }

    [JsonPropertyName("metadata")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [JsonPropertyName("source")]
    public string? Source { get; set; }
}

/// <summary>
/// Multi-agent orchestration response
/// </summary>
public class OrchestrationResponse : AgentResponse
{
    [JsonPropertyName("workflow_results")]
    public Dictionary<string, AgentResponse> WorkflowResults { get; set; } = new();

    [JsonPropertyName("final_answer")]
    public string FinalAnswer { get; set; } = string.Empty;

    [JsonPropertyName("execution_steps")]
    public List<string> ExecutionSteps { get; set; } = new();
}
