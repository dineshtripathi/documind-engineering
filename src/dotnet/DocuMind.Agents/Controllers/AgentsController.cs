using DocuMind.Agents.Interfaces;
using DocuMind.Agents.Models;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;

namespace DocuMind.Agents.Controllers;

/// <summary>
/// API controller for agent orchestration and individual agent operations
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class AgentsController : ControllerBase
{
    private readonly ILogger<AgentsController> _logger;
    private readonly IAgentOrchestrator _orchestrator;
    private readonly IDocumentAgent _documentAgent;
    private readonly IVisionAgent _visionAgent;
    private readonly ISearchAgent _searchAgent;

    public AgentsController(
        ILogger<AgentsController> logger,
        IAgentOrchestrator orchestrator,
        IDocumentAgent documentAgent,
        IVisionAgent visionAgent,
        ISearchAgent searchAgent)
    {
        _logger = logger;
        _orchestrator = orchestrator;
        _documentAgent = documentAgent;
        _visionAgent = visionAgent;
        _searchAgent = searchAgent;
    }

    /// <summary>
    /// Health check endpoint
    /// </summary>
    [HttpGet("healthz")]
    public IActionResult HealthCheck()
    {
        return Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow,
            service = "DocuMind.Agents",
            version = "1.0.0"
        });
    }

    /// <summary>
    /// Execute a multi-agent workflow
    /// </summary>
    [HttpPost("orchestrate")]
    public async Task<ActionResult<OrchestrationResponse>> OrchestrateworkflowAsync(
        [FromBody, Required] OrchestrationRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Orchestration request received: {WorkflowType}", request.WorkflowType);

            var result = await _orchestrator.OrchestrateworkflowAsync(request, cancellationToken);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in orchestration");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Route a request to a specific agent
    /// </summary>
    [HttpPost("route/{agentType}")]
    public async Task<ActionResult<AgentResponse>> RouteToAgentAsync(
        [FromRoute, Required] string agentType,
        [FromBody, Required] AgentRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Routing to agent: {AgentType}", agentType);

            var result = await _orchestrator.RouteToAgentAsync(request, agentType, cancellationToken);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error routing to agent: {AgentType}", agentType);
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Process a document using the Document Agent
    /// </summary>
    [HttpPost("document/process")]
    public async Task<ActionResult<DocumentAgentResponse>> ProcessDocumentAsync(
        [FromBody, Required] DocumentAgentRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Document processing request: {ProcessingType}", request.ProcessingType);

            var result = await _documentAgent.ProcessDocumentAsync(request, cancellationToken);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing document");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Extract text from a document
    /// </summary>
    [HttpPost("document/extract-text")]
    public async Task<ActionResult<string>> ExtractTextAsync(
        [FromBody, Required] DocumentExtractionRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var result = await _documentAgent.ExtractTextAsync(
                request.FileContent,
                request.FileName,
                cancellationToken);

            return Ok(new { extracted_text = result });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error extracting text");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Summarize document content
    /// </summary>
    [HttpPost("document/summarize")]
    public async Task<ActionResult<string>> SummarizeAsync(
        [FromBody, Required] DocumentSummaryRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var result = await _documentAgent.SummarizeAsync(request.Content, cancellationToken);

            return Ok(new { summary = result });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error summarizing document");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Process an image using the Vision Agent
    /// </summary>
    [HttpPost("vision/process")]
    public async Task<ActionResult<VisionAgentResponse>> ProcessImageAsync(
        [FromBody, Required] VisionAgentRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Vision processing request: {AnalysisType}", request.AnalysisType);

            var result = await _visionAgent.ProcessImageAsync(request, cancellationToken);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing image");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Analyze an image
    /// </summary>
    [HttpPost("vision/analyze")]
    public async Task<ActionResult<string>> AnalyzeImageAsync(
        [FromBody, Required] ImageAnalysisRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var result = await _visionAgent.AnalyzeImageAsync(
                request.ImageData,
                request.AnalysisType,
                cancellationToken);

            return Ok(new { analysis = result });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing image");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Extract text from an image
    /// </summary>
    [HttpPost("vision/extract-text")]
    public async Task<ActionResult<string>> ExtractTextFromImageAsync(
        [FromBody, Required] ImageTextExtractionRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var result = await _visionAgent.ExtractTextFromImageAsync(request.ImageData, cancellationToken);

            return Ok(new { extracted_text = result });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error extracting text from image");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Perform a search using the Search Agent
    /// </summary>
    [HttpPost("search")]
    public async Task<ActionResult<SearchAgentResponse>> SearchAsync(
        [FromBody, Required] SearchAgentRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Search request: {SearchType} for '{Query}'",
                request.SearchType, request.Query);

            var result = await _searchAgent.SearchAsync(request, cancellationToken);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing search");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Perform semantic search
    /// </summary>
    [HttpGet("search/semantic")]
    public async Task<ActionResult<List<SearchResult>>> SemanticSearchAsync(
        [FromQuery, Required] string query,
        [FromQuery] int maxResults = 10,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var results = await _searchAgent.SemanticSearchAsync(query, maxResults, cancellationToken);

            return Ok(results);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing semantic search");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Execute the Document Intelligence workflow
    /// </summary>
    [HttpPost("workflows/document-intelligence")]
    public async Task<ActionResult<OrchestrationResponse>> DocumentIntelligenceWorkflowAsync(
        [FromBody, Required] DocumentIntelligenceWorkflowRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Document Intelligence workflow requested");

            var inputs = new Dictionary<string, object>();

            if (!string.IsNullOrEmpty(request.DocumentContent))
                inputs["document_content"] = request.DocumentContent;

            if (!string.IsNullOrEmpty(request.ImageData))
                inputs["image_data"] = request.ImageData;

            if (!string.IsNullOrEmpty(request.SearchQuery))
                inputs["search_query"] = request.SearchQuery;

            if (!string.IsNullOrEmpty(request.FileName))
                inputs["file_name"] = request.FileName;

            var result = await _orchestrator.ExecuteDocumentIntelligenceWorkflowAsync(
                inputs,
                request.SessionId ?? Guid.NewGuid().ToString(),
                cancellationToken);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing Document Intelligence workflow");
            return StatusCode(500, new { error = ex.Message });
        }
    }
}

// Helper request models for specific operations
public class DocumentExtractionRequest
{
    public string FileContent { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
}

public class DocumentSummaryRequest
{
    public string Content { get; set; } = string.Empty;
}

public class ImageAnalysisRequest
{
    public string ImageData { get; set; } = string.Empty;
    public string AnalysisType { get; set; } = "general";
}

public class ImageTextExtractionRequest
{
    public string ImageData { get; set; } = string.Empty;
}

public class DocumentIntelligenceWorkflowRequest
{
    public string? DocumentContent { get; set; }
    public string? ImageData { get; set; }
    public string? SearchQuery { get; set; }
    public string? FileName { get; set; }
    public string? SessionId { get; set; }
}
