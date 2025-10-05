using DocuMind.Agents.Models;
using DocuMind.Agents.Services;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;

namespace DocuMind.Agents.Controllers;

/// <summary>
/// Learning-focused workflows for understanding multi-agent orchestration
/// </summary>
[ApiController]
[Route("api/learning")]
[Produces("application/json")]
public class LearningController : ControllerBase
{
    private readonly ILogger<LearningController> _logger;
    private readonly LearningWorkflows _learningWorkflows;

    public LearningController(
        ILogger<LearningController> logger,
        LearningWorkflows learningWorkflows)
    {
        _logger = logger;
        _learningWorkflows = learningWorkflows;
    }

    /// <summary>
    /// Get available learning workflows with descriptions
    /// </summary>
    [HttpGet("workflows")]
    public IActionResult GetLearningWorkflows()
    {
        var workflows = new
        {
            available_workflows = new[]
            {
                new
                {
                    id = "basic-document-pipeline",
                    name = "Basic Document Analysis Pipeline",
                    description = "Learn sequential agent coordination through document processing → key term extraction → related content search",
                    learning_objectives = new[] { "Sequential workflow", "Data flow between agents", "Simple orchestration" },
                    endpoint = "/api/learning/basic-document-pipeline",
                    difficulty = "Beginner"
                },
                new
                {
                    id = "multi-modal-intelligence",
                    name = "Multi-Modal Intelligence Workflow",
                    description = "Process document, image, and research data simultaneously using parallel agent execution",
                    learning_objectives = new[] { "Parallel execution", "Multi-modal processing", "Result synthesis" },
                    endpoint = "/api/learning/multi-modal-intelligence",
                    difficulty = "Intermediate"
                },
                new
                {
                    id = "iterative-research",
                    name = "Iterative Research Assistant",
                    description = "Perform multiple search iterations with query refinement based on previous results",
                    learning_objectives = new[] { "Agent chaining", "Iterative refinement", "Decision-making loops" },
                    endpoint = "/api/learning/iterative-research",
                    difficulty = "Advanced"
                }
            },
            getting_started = new
            {
                recommendation = "Start with 'basic-document-pipeline' to understand sequential workflows",
                sample_data = new
                {
                    document = "Sample business document with quarterly performance data",
                    image = "Base64 encoded image data",
                    research_query = "artificial intelligence trends 2025"
                }
            }
        };

        return Ok(workflows);
    }

    /// <summary>
    /// LEARNING WORKFLOW 1: Basic Document Analysis Pipeline
    /// Demonstrates sequential agent coordination and data flow
    /// </summary>
    [HttpPost("basic-document-pipeline")]
    public async Task<ActionResult<OrchestrationResponse>> BasicDocumentPipeline(
        [FromBody, Required] BasicDocumentPipelineRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("🎓 Starting Basic Document Analysis Pipeline learning workflow");

            var result = await _learningWorkflows.BasicDocumentAnalysisPipeline(
                request.DocumentContent,
                request.FileName ?? "learning_document.txt",
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
            _logger.LogError(ex, "Error in Basic Document Pipeline learning workflow");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// LEARNING WORKFLOW 2: Multi-Modal Intelligence
    /// Demonstrates parallel agent execution and multi-modal data processing
    /// </summary>
    [HttpPost("multi-modal-intelligence")]
    public async Task<ActionResult<OrchestrationResponse>> MultiModalIntelligence(
        [FromBody, Required] MultiModalIntelligenceRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("🎓 Starting Multi-Modal Intelligence learning workflow");

            var result = await _learningWorkflows.MultiModalIntelligenceWorkflow(
                request.DocumentContent ?? string.Empty,
                request.ImageData ?? string.Empty,
                request.ResearchQuery ?? string.Empty,
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
            _logger.LogError(ex, "Error in Multi-Modal Intelligence learning workflow");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// LEARNING WORKFLOW 3: Iterative Research Assistant
    /// Demonstrates agent chaining and iterative refinement
    /// </summary>
    [HttpPost("iterative-research")]
    public async Task<ActionResult<OrchestrationResponse>> IterativeResearch(
        [FromBody, Required] IterativeResearchRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("🎓 Starting Iterative Research Assistant learning workflow");

            var result = await _learningWorkflows.IterativeResearchAssistant(
                request.ResearchTopic,
                Math.Min(request.MaxIterations ?? 3, 5), // Limit to 5 iterations for safety
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
            _logger.LogError(ex, "Error in Iterative Research learning workflow");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    /// <summary>
    /// Get a sample business document for testing workflows
    /// </summary>
    [HttpGet("sample-data/document")]
    public IActionResult GetSampleDocument()
    {
        var sampleDocument = @"QUARTERLY BUSINESS REPORT - Q3 2025

EXECUTIVE SUMMARY
This quarter has been marked by significant growth and strategic expansion. Our revenue increased by 28% compared to Q2 2025, reaching $3.2 million. Key achievements include successful market penetration in the European region and the launch of our AI-powered product suite.

KEY PERFORMANCE INDICATORS
- Revenue: $3.2M (↑28% from Q2)
- Customer Acquisition: 450 new customers (↑35%)
- Customer Satisfaction: 4.3/5.0 (↑0.2 points)
- Employee Satisfaction: 4.1/5.0
- Market Share: 12% in target segments

STRATEGIC INITIATIVES
1. European Market Expansion
   - Opened offices in London and Berlin
   - Localized product offerings for EU compliance
   - Hired 25 new team members across sales and support

2. AI Product Suite Launch
   - Launched DocuMind AI Platform
   - Integrated machine learning capabilities
   - Achieved 85% customer adoption rate

3. Operational Excellence
   - Reduced processing time by 40%
   - Implemented automated quality controls
   - Enhanced cybersecurity measures

CHALLENGES AND OPPORTUNITIES
Challenges:
- Supply chain disruptions affecting delivery times
- Increased competition from tech giants
- Talent acquisition in specialized AI roles

Opportunities:
- Growing demand for AI-powered solutions
- Potential partnerships with Fortune 500 companies
- Government contracts in digital transformation

FINANCIAL OUTLOOK
Based on current trends, we project Q4 2025 revenue of $3.8M, representing sustained growth. Investment in R&D will increase to 18% of revenue to maintain competitive advantage.

CONCLUSION
Q3 2025 demonstrates our company's resilience and growth trajectory. Strategic investments in AI and international expansion are yielding positive results.";

        return Ok(new
        {
            title = "Sample Quarterly Business Report",
            content = sampleDocument,
            suggested_workflows = new[]
            {
                "basic-document-pipeline - Extract key terms and find related content",
                "multi-modal-intelligence - Combine with image analysis and research",
                "iterative-research - Deep dive into specific business metrics"
            }
        });
    }

    /// <summary>
    /// Generate sample research queries for learning
    /// </summary>
    [HttpGet("sample-data/research-queries")]
    public IActionResult GetSampleResearchQueries()
    {
        var queries = new
        {
            beginner_queries = new[]
            {
                "business performance metrics",
                "artificial intelligence trends",
                "customer satisfaction improvement",
                "revenue growth strategies"
            },
            intermediate_queries = new[]
            {
                "machine learning implementation best practices",
                "digital transformation enterprise solutions",
                "supply chain optimization AI",
                "customer experience personalization"
            },
            advanced_queries = new[]
            {
                "multi-agent systems orchestration patterns",
                "semantic search relevance optimization",
                "document intelligence processing workflows",
                "cross-modal AI analysis techniques"
            }
        };

        return Ok(queries);
    }
}

// Request models for learning workflows
public class BasicDocumentPipelineRequest
{
    [Required]
    public string DocumentContent { get; set; } = string.Empty;
    public string? FileName { get; set; }
    public string? SessionId { get; set; }
}

public class MultiModalIntelligenceRequest
{
    public string? DocumentContent { get; set; }
    public string? ImageData { get; set; }
    public string? ResearchQuery { get; set; }
    public string? SessionId { get; set; }
}

public class IterativeResearchRequest
{
    [Required]
    public string ResearchTopic { get; set; } = string.Empty;
    public int? MaxIterations { get; set; } = 3;
    public string? SessionId { get; set; }
}
