using DocuMind.Agents.Interfaces;
using DocuMind.Agents.Models;
using DocuMind.Agents.Options;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.SemanticKernel;
using System.Diagnostics;
using System.Text.Json;

namespace DocuMind.Agents.Services;

/// <summary>
/// Main orchestrator for coordinating multiple agents and workflows
/// </summary>
public class AgentOrchestrator : IAgentOrchestrator
{
    private readonly ILogger<AgentOrchestrator> _logger;
    private readonly AgentOptions _options;
    private readonly Kernel _kernel;
    private readonly IDocumentAgent _documentAgent;
    private readonly IVisionAgent _visionAgent;
    private readonly ISearchAgent _searchAgent;

    public AgentOrchestrator(
        ILogger<AgentOrchestrator> logger,
        IOptions<AgentOptions> options,
        Kernel kernel,
        IDocumentAgent documentAgent,
        IVisionAgent visionAgent,
        ISearchAgent searchAgent)
    {
        _logger = logger;
        _options = options.Value;
        _kernel = kernel;
        _documentAgent = documentAgent;
        _visionAgent = visionAgent;
        _searchAgent = searchAgent;
    }

    public async Task<OrchestrationResponse> OrchestrateworkflowAsync(OrchestrationRequest request, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            _logger.LogInformation("Starting workflow orchestration: {WorkflowType}", request.WorkflowType);

            var response = new OrchestrationResponse
            {
                SessionId = request.SessionId,
                AgentType = "Orchestrator"
            };

            switch (request.WorkflowType.ToLowerInvariant())
            {
                case "document_intelligence":
                    response = await ExecuteDocumentIntelligenceWorkflowAsync(request.Inputs, request.SessionId, cancellationToken);
                    break;

                case "research":
                    response = await ExecuteResearchWorkflowAsync(request.Inputs, request.SessionId, cancellationToken);
                    break;

                case "analysis":
                    response = await ExecuteAnalysisWorkflowAsync(request.Inputs, request.SessionId, cancellationToken);
                    break;

                default:
                    response = await ExecuteDocumentIntelligenceWorkflowAsync(request.Inputs, request.SessionId, cancellationToken);
                    break;
            }

            response.ExecutionTimeMs = stopwatch.ElapsedMilliseconds;
            response.Response = $"Workflow '{request.WorkflowType}' completed successfully";

            _logger.LogInformation("Workflow orchestration completed in {ElapsedMs}ms", stopwatch.ElapsedMilliseconds);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in workflow orchestration");

            return new OrchestrationResponse
            {
                Success = false,
                Error = ex.Message,
                SessionId = request.SessionId,
                AgentType = "Orchestrator",
                ExecutionTimeMs = stopwatch.ElapsedMilliseconds
            };
        }
    }

    public async Task<AgentResponse> RouteToAgentAsync(AgentRequest request, string agentType, CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Routing request to agent: {AgentType}", agentType);

            return agentType.ToLowerInvariant() switch
            {
                "document" or "documentagent" => await _documentAgent.ProcessAsync(request, cancellationToken),
                "vision" or "visionagent" => await _visionAgent.ProcessAsync(request, cancellationToken),
                "search" or "searchagent" => await _searchAgent.ProcessAsync(request, cancellationToken),
                _ => new AgentResponse
                {
                    Success = false,
                    Error = $"Unknown agent type: {agentType}",
                    AgentType = "Router"
                }
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error routing to agent: {AgentType}", agentType);

            return new AgentResponse
            {
                Success = false,
                Error = ex.Message,
                AgentType = "Router"
            };
        }
    }

    public async Task<OrchestrationResponse> ExecuteDocumentIntelligenceWorkflowAsync(Dictionary<string, object> inputs, string sessionId, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();
        var response = new OrchestrationResponse
        {
            SessionId = sessionId,
            AgentType = "Orchestrator"
        };

        try
        {
            _logger.LogInformation("Executing Document Intelligence workflow");

            var executionSteps = new List<string>();
            var workflowResults = new Dictionary<string, AgentResponse>();

            // Step 1: Analyze input and plan workflow
            executionSteps.Add("Planning workflow execution");
            var workflowPlan = await PlanWorkflowAsync(inputs, "document_intelligence", cancellationToken);

            // Step 2: Document processing (if document content provided)
            if (inputs.ContainsKey("document_content") || inputs.ContainsKey("file_content"))
            {
                executionSteps.Add("Processing document content");

                var docRequest = new DocumentAgentRequest
                {
                    SessionId = sessionId,
                    FileContent = inputs.GetValueOrDefault("document_content")?.ToString() ??
                                 inputs.GetValueOrDefault("file_content")?.ToString(),
                    FileName = inputs.GetValueOrDefault("file_name")?.ToString(),
                    ProcessingType = "analysis"
                };

                var docResult = await _documentAgent.ProcessDocumentAsync(docRequest, cancellationToken);
                workflowResults["document_analysis"] = docResult;
            }

            // Step 3: Vision processing (if image data provided)
            if (inputs.ContainsKey("image_data"))
            {
                executionSteps.Add("Processing image content");

                var visionRequest = new VisionAgentRequest
                {
                    SessionId = sessionId,
                    ImageData = inputs.GetValueOrDefault("image_data")?.ToString(),
                    AnalysisType = "general"
                };

                var visionResult = await _visionAgent.ProcessImageAsync(visionRequest, cancellationToken);
                workflowResults["vision_analysis"] = visionResult;
            }

            // Step 4: Semantic search (if query provided)
            if (inputs.ContainsKey("search_query") || inputs.ContainsKey("query"))
            {
                executionSteps.Add("Performing semantic search");

                var searchRequest = new SearchAgentRequest
                {
                    SessionId = sessionId,
                    Query = inputs.GetValueOrDefault("search_query")?.ToString() ??
                           inputs.GetValueOrDefault("query")?.ToString() ?? string.Empty,
                    SearchType = "semantic",
                    MaxResults = 10
                };

                var searchResult = await _searchAgent.SearchAsync(searchRequest, cancellationToken);
                workflowResults["search_results"] = searchResult;
            }

            // Step 5: Generate final analysis and answer
            executionSteps.Add("Generating comprehensive analysis");

            var finalAnswer = await GenerateFinalAnswerAsync(workflowResults, inputs, cancellationToken);

            response.WorkflowResults = workflowResults;
            response.FinalAnswer = finalAnswer;
            response.ExecutionSteps = executionSteps;
            response.ExecutionTimeMs = stopwatch.ElapsedMilliseconds;

            // Add workflow metadata
            response.Metadata["workflow_type"] = "document_intelligence";
            response.Metadata["steps_completed"] = executionSteps.Count;
            response.Metadata["agents_used"] = workflowResults.Keys.ToArray();

            _logger.LogInformation("Document Intelligence workflow completed with {StepCount} steps", executionSteps.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing Document Intelligence workflow");

            response.Success = false;
            response.Error = ex.Message;
            response.ExecutionTimeMs = stopwatch.ElapsedMilliseconds;

            return response;
        }
    }

    private async Task<OrchestrationResponse> ExecuteResearchWorkflowAsync(Dictionary<string, object> inputs, string sessionId, CancellationToken cancellationToken)
    {
        // Research workflow: Search → Analyze → Synthesize
        var response = new OrchestrationResponse
        {
            SessionId = sessionId,
            AgentType = "Orchestrator"
        };

        try
        {
            var executionSteps = new List<string> { "Executing research workflow" };
            var workflowResults = new Dictionary<string, AgentResponse>();

            // Implement research-specific workflow logic here
            // This could involve multiple search iterations, analysis, and synthesis

            response.ExecutionSteps = executionSteps;
            response.WorkflowResults = workflowResults;
            response.FinalAnswer = "Research workflow completed";

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing research workflow");
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    private async Task<OrchestrationResponse> ExecuteAnalysisWorkflowAsync(Dictionary<string, object> inputs, string sessionId, CancellationToken cancellationToken)
    {
        // Analysis workflow: Process → Compare → Insights
        var response = new OrchestrationResponse
        {
            SessionId = sessionId,
            AgentType = "Orchestrator"
        };

        try
        {
            var executionSteps = new List<string> { "Executing analysis workflow" };
            var workflowResults = new Dictionary<string, AgentResponse>();

            // Implement analysis-specific workflow logic here

            response.ExecutionSteps = executionSteps;
            response.WorkflowResults = workflowResults;
            response.FinalAnswer = "Analysis workflow completed";

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing analysis workflow");
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    private async Task<string> PlanWorkflowAsync(Dictionary<string, object> inputs, string workflowType, CancellationToken cancellationToken)
    {
        try
        {
            var planningPrompt = """
                Analyze the provided inputs and create an execution plan for a {{$workflowType}} workflow.

                Available Inputs:
                {{$inputs}}

                Create a step-by-step execution plan:
                """;

            var inputsJson = JsonSerializer.Serialize(inputs);

            var planningFunction = _kernel.CreateFunctionFromPrompt(planningPrompt);
            var result = await _kernel.InvokeAsync(planningFunction, new()
            {
                ["workflowType"] = workflowType,
                ["inputs"] = inputsJson
            }, cancellationToken);

            return result.ToString() ?? "Basic workflow plan created";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error planning workflow");
            return "Default workflow plan";
        }
    }

    private async Task<string> GenerateFinalAnswerAsync(Dictionary<string, AgentResponse> workflowResults, Dictionary<string, object> inputs, CancellationToken cancellationToken)
    {
        try
        {
            var synthesisPrompt = """
                Synthesize the results from multiple AI agents into a comprehensive final answer.

                Agent Results:
                {{$results}}

                Original Inputs:
                {{$inputs}}

                Provide a comprehensive analysis and final answer:
                """;

            var resultsJson = JsonSerializer.Serialize(workflowResults);
            var inputsJson = JsonSerializer.Serialize(inputs);

            var synthesisFunction = _kernel.CreateFunctionFromPrompt(synthesisPrompt);
            var result = await _kernel.InvokeAsync(synthesisFunction, new()
            {
                ["results"] = resultsJson,
                ["inputs"] = inputsJson
            }, cancellationToken);

            return result.ToString() ?? "Workflow completed successfully";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating final answer");
            return "Workflow completed with partial results";
        }
    }
}
