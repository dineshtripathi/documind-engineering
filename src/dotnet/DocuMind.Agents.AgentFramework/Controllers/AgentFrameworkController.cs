using Microsoft.AspNetCore.Mvc;
using DocuMind.Agents.AgentFramework.Services;

namespace DocuMind.Agents.AgentFramework.Controllers;

/// <summary>
/// Agent Framework-based API controller for educational comparison with Semantic Kernel
/// Demonstrates different architectural patterns between Agent Framework and Semantic Kernel
/// </summary>
[ApiController]
[Route("api/agent-framework")]
[Produces("application/json")]
public class AgentFrameworkController : ControllerBase
{
    private readonly ILogger<AgentFrameworkController> _logger;
    private readonly AgentFrameworkOrchestratorCompatible _orchestrator;
    private readonly AgentFrameworkLearningWorkflowsCompatible _learningWorkflows;

    public AgentFrameworkController(
        ILogger<AgentFrameworkController> logger,
        AgentFrameworkOrchestratorCompatible orchestrator,
        AgentFrameworkLearningWorkflowsCompatible learningWorkflows)
    {
        _logger = logger;
        _orchestrator = orchestrator;
        _learningWorkflows = learningWorkflows;
    }

    /// <summary>
    /// Execute Agent Framework multi-agent orchestration for educational comparison
    /// </summary>
    [HttpPost("orchestrate")]
    public async Task<IActionResult> OrchestateAgents([FromBody] OrchestrationRequest request)
    {
        try
        {
            _logger.LogInformation("🤖 Agent Framework orchestration requested");

            var result = await _orchestrator.ProcessComplexQueryAsync(
                $"Process this multi-modal content: Document: {request.DocumentContent ?? "None"}, " +
                $"Image: {(string.IsNullOrEmpty(request.ImageData) ? "None" : "Provided")}, " +
                $"Research Query: {request.ResearchQuery ?? "None"}");

            var response = new
            {
                Framework = "Agent Framework",
                Timestamp = DateTime.UtcNow,
                Result = result,
                EducationalNote = "This uses Microsoft's Agent Framework for native multi-agent orchestration. Compare with Semantic Kernel's plugin-based approach.",
                ArchitecturalPattern = "Native Agent Collaboration",
                KeyDifferences = new[]
                {
                    "Direct agent creation and specialization",
                    "Agent-to-agent communication patterns",
                    "Built-in multi-agent coordination",
                    "Persistent agent identity and context"
                }
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Agent Framework orchestration");
            return StatusCode(500, new { error = ex.Message, framework = "Agent Framework" });
        }
    }

    /// <summary>
    /// Learning Workflow 1: Simple Agent Framework Pattern
    /// </summary>
    [HttpPost("learn/simple-pattern")]
    public async Task<IActionResult> LearningWorkflow1([FromBody] LearningRequest request)
    {
        try
        {
            _logger.LogInformation("📚 Agent Framework Learning Workflow 1 requested");

            var result = await _learningWorkflows.LearningWorkflow1_SimpleAgentPattern(
                request.Query ?? "What is AI agent orchestration?");

            return Ok(new
            {
                workflow = "Simple Agent Pattern",
                framework = "Agent Framework",
                result = result,
                timestamp = DateTime.UtcNow,
                educational_value = "Demonstrates Agent Framework's approach to simple agent coordination"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Agent Framework Learning Workflow 1");
            return StatusCode(500, new { error = ex.Message, workflow = "Simple Agent Pattern" });
        }
    }

    /// <summary>
    /// Learning Workflow 2: Multi-Agent Collaboration
    /// </summary>
    [HttpPost("learn/multi-agent-collaboration")]
    public async Task<IActionResult> LearningWorkflow2([FromBody] LearningRequest request)
    {
        try
        {
            _logger.LogInformation("📚 Agent Framework Learning Workflow 2 requested");

            var result = await _learningWorkflows.LearningWorkflow2_MultiAgentCollaboration(
                request.Query ?? "How do multiple AI agents work together?");

            return Ok(new
            {
                workflow = "Multi-Agent Collaboration",
                framework = "Agent Framework",
                result = result,
                timestamp = DateTime.UtcNow,
                educational_value = "Demonstrates Agent Framework's multi-agent coordination patterns"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Agent Framework Learning Workflow 2");
            return StatusCode(500, new { error = ex.Message, workflow = "Multi-Agent Collaboration" });
        }
    }

    /// <summary>
    /// Learning Workflow 3: RAG-Enhanced Agents
    /// </summary>
    [HttpPost("learn/rag-enhanced")]
    public async Task<IActionResult> LearningWorkflow3([FromBody] LearningRequest request)
    {
        try
        {
            _logger.LogInformation("📚 Agent Framework Learning Workflow 3 requested");

            var result = await _learningWorkflows.LearningWorkflow3_RAGEnhanced(
                request.Query ?? "What is the relationship between AI agents and knowledge retrieval?");

            return Ok(new
            {
                workflow = "RAG-Enhanced Agents",
                framework = "Agent Framework",
                result = result,
                timestamp = DateTime.UtcNow,
                educational_value = "Demonstrates Agent Framework's integration with RAG patterns"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Agent Framework Learning Workflow 3");
            return StatusCode(500, new { error = ex.Message, workflow = "RAG-Enhanced Agents" });
        }
    }

    /// <summary>
    /// Get information about Agent Framework vs Semantic Kernel
    /// </summary>
    [HttpGet("framework-info")]
    public IActionResult GetFrameworkInfo()
    {
        var info = new
        {
            framework = "Microsoft Agent Framework",
            version = "Beta",
            description = "Microsoft's new framework for building and orchestrating AI agents",
            keyFeatures = new[]
            {
                "Native multi-agent support",
                "Direct agent creation and specialization",
                "Agent-to-agent communication patterns",
                "Built-in coordination mechanisms",
                "Persistent agent identity and context"
            },
            architecturalApproach = "Agent-Centric",
            comparisonWithSemanticKernel = new
            {
                agentFramework = "Focuses on agent entities and their interactions",
                semanticKernel = "Focuses on functions and plugins with orchestration",
                agentFrameworkStrength = "Natural multi-agent workflows",
                semanticKernelStrength = "Flexible function composition and planning"
            },
            learningEndpoints = new[]
            {
                "/api/agent-framework/learn/simple-pattern",
                "/api/agent-framework/learn/multi-agent-collaboration",
                "/api/agent-framework/learn/rag-enhanced"
            },
            comparisonEndpoints = new[]
            {
                "/api/semantic-kernel/learn/simple-pattern (compare)",
                "/api/semantic-kernel/learn/multi-agent-collaboration (compare)",
                "/api/semantic-kernel/learn/rag-enhanced (compare)"
            }
        };

        return Ok(info);
    }

    /// <summary>
    /// Health check endpoint for Agent Framework service
    /// </summary>
    [HttpGet("health")]
    public IActionResult GetHealth()
    {
        return Ok(new
        {
            status = "Healthy",
            framework = "Agent Framework",
            timestamp = DateTime.UtcNow,
            message = "Agent Framework service is operational and ready for educational comparisons"
        });
    }
}

/// <summary>
/// Request model for orchestration
/// </summary>
public class OrchestrationRequest
{
    public string? DocumentContent { get; set; }
    public string? ImageData { get; set; }
    public string? ResearchQuery { get; set; }
}

/// <summary>
/// Request model for learning workflows
/// </summary>
public class LearningRequest
{
    public string? Query { get; set; }
    public bool IncludeEducational { get; set; } = true;
}
