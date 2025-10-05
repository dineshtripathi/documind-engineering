using DocuMind.Agents.Interfaces;
using DocuMind.Agents.Models;
using DocuMind.Agents.Options;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System.Text.Json;

namespace DocuMind.Agents.Services;

/// <summary>
/// Educational workflows for learning multi-agent orchestration patterns
/// </summary>
public class LearningWorkflows
{
    private readonly ILogger<LearningWorkflows> _logger;
    private readonly AgentOptions _options;
    private readonly IDocumentAgent _documentAgent;
    private readonly IVisionAgent _visionAgent;
    private readonly ISearchAgent _searchAgent;
    private readonly HttpClient _httpClient;

    public LearningWorkflows(
        ILogger<LearningWorkflows> logger,
        IOptions<AgentOptions> options,
        IDocumentAgent documentAgent,
        IVisionAgent visionAgent,
        ISearchAgent searchAgent,
        HttpClient httpClient)
    {
        _logger = logger;
        _options = options.Value;
        _documentAgent = documentAgent;
        _visionAgent = visionAgent;
        _searchAgent = searchAgent;
        _httpClient = httpClient;
    }

    /// <summary>
    /// LEARNING WORKFLOW 1: Basic Document Analysis Pipeline
    /// Demonstrates: Sequential agent coordination, data flow between agents
    /// </summary>
    public async Task<OrchestrationResponse> BasicDocumentAnalysisPipeline(
        string documentContent,
        string fileName,
        string sessionId,
        CancellationToken cancellationToken = default)
    {
        var response = new OrchestrationResponse
        {
            SessionId = sessionId,
            AgentType = "LearningWorkflow",
            ExecutionSteps = new List<string>()
        };

        try
        {
            _logger.LogInformation("🎓 LEARNING WORKFLOW 1: Basic Document Analysis Pipeline");

            // Step 1: Document Processing
            response.ExecutionSteps.Add("Step 1: Processing document with Document Agent");
            var docRequest = new DocumentAgentRequest
            {
                SessionId = sessionId,
                FileContent = documentContent,
                FileName = fileName,
                ProcessingType = "analysis"
            };

            var docResult = await _documentAgent.ProcessDocumentAsync(docRequest, cancellationToken);
            response.WorkflowResults["document_analysis"] = docResult;

            // Step 2: Extract key terms for search
            response.ExecutionSteps.Add("Step 2: Extracting key terms for related content search");
            var keyTerms = ExtractKeyTermsFromDocument(documentContent);

            // Step 3: Search for related content
            response.ExecutionSteps.Add("Step 3: Searching for related content using extracted terms");
            var searchRequest = new SearchAgentRequest
            {
                SessionId = sessionId,
                Query = string.Join(" ", keyTerms),
                SearchType = "semantic",
                MaxResults = 5
            };

            var searchResult = await _searchAgent.SearchAsync(searchRequest, cancellationToken);
            response.WorkflowResults["related_content_search"] = searchResult;

            // Step 4: Generate insights
            response.ExecutionSteps.Add("Step 4: Generating insights from analysis and search results");
            response.FinalAnswer = GenerateBasicInsights(docResult, searchResult, keyTerms);

            response.Metadata["workflow_type"] = "basic_document_pipeline";
            response.Metadata["learning_objective"] = "Understanding sequential agent coordination";
            response.Metadata["key_terms_extracted"] = keyTerms;

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Basic Document Analysis Pipeline");
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    /// <summary>
    /// LEARNING WORKFLOW 2: Multi-Modal Intelligence
    /// Demonstrates: Parallel agent execution, different data types, result synthesis
    /// </summary>
    public async Task<OrchestrationResponse> MultiModalIntelligenceWorkflow(
        string documentContent,
        string imageData,
        string researchQuery,
        string sessionId,
        CancellationToken cancellationToken = default)
    {
        var response = new OrchestrationResponse
        {
            SessionId = sessionId,
            AgentType = "LearningWorkflow",
            ExecutionSteps = new List<string>()
        };

        try
        {
            _logger.LogInformation("🎓 LEARNING WORKFLOW 2: Multi-Modal Intelligence");

            response.ExecutionSteps.Add("Step 1: Starting parallel processing of multiple data types");

            // Parallel execution of different agents
            var tasks = new List<Task>();
            var results = new Dictionary<string, object>();

            // Task 1: Document Analysis
            if (!string.IsNullOrEmpty(documentContent))
            {
                response.ExecutionSteps.Add("Step 2a: Analyzing document content (parallel)");
                var docTask = _documentAgent.ProcessDocumentAsync(new DocumentAgentRequest
                {
                    SessionId = sessionId,
                    FileContent = documentContent,
                    ProcessingType = "analysis"
                }, cancellationToken);

                tasks.Add(docTask.ContinueWith(t => results["document"] = t.Result, cancellationToken));
            }

            // Task 2: Image Analysis
            if (!string.IsNullOrEmpty(imageData))
            {
                response.ExecutionSteps.Add("Step 2b: Processing image content (parallel)");
                var visionTask = _visionAgent.ProcessImageAsync(new VisionAgentRequest
                {
                    SessionId = sessionId,
                    ImageData = imageData,
                    AnalysisType = "general"
                }, cancellationToken);

                tasks.Add(visionTask.ContinueWith(t => results["vision"] = t.Result, cancellationToken));
            }

            // Task 3: Research Search
            if (!string.IsNullOrEmpty(researchQuery))
            {
                response.ExecutionSteps.Add("Step 2c: Conducting research search (parallel)");
                var searchTask = _searchAgent.SearchAsync(new SearchAgentRequest
                {
                    SessionId = sessionId,
                    Query = researchQuery,
                    SearchType = "semantic",
                    MaxResults = 8
                }, cancellationToken);

                tasks.Add(searchTask.ContinueWith(t => results["research"] = t.Result, cancellationToken));
            }

            // Wait for all parallel tasks to complete
            response.ExecutionSteps.Add("Step 3: Waiting for all parallel processing to complete");
            await Task.WhenAll(tasks);

            // Copy results to workflow response
            foreach (var result in results)
            {
                response.WorkflowResults[result.Key] = (AgentResponse)result.Value;
            }

            // Step 4: Cross-modal analysis
            response.ExecutionSteps.Add("Step 4: Performing cross-modal analysis and synthesis");
            response.FinalAnswer = PerformCrossModalAnalysis(results);

            response.Metadata["workflow_type"] = "multi_modal_intelligence";
            response.Metadata["learning_objective"] = "Understanding parallel agent execution and multi-modal data processing";
            response.Metadata["modalities_processed"] = results.Keys.ToList();

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Multi-Modal Intelligence Workflow");
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    /// <summary>
    /// LEARNING WORKFLOW 3: Iterative Research Assistant
    /// Demonstrates: Agent chaining, iterative refinement, decision-making
    /// </summary>
    public async Task<OrchestrationResponse> IterativeResearchAssistant(
        string researchTopic,
        int maxIterations,
        string sessionId,
        CancellationToken cancellationToken = default)
    {
        var response = new OrchestrationResponse
        {
            SessionId = sessionId,
            AgentType = "LearningWorkflow",
            ExecutionSteps = new List<string>()
        };

        try
        {
            _logger.LogInformation("🎓 LEARNING WORKFLOW 3: Iterative Research Assistant");

            response.ExecutionSteps.Add($"Step 1: Starting iterative research on '{researchTopic}'");

            var currentQuery = researchTopic;
            var allResults = new List<SearchResult>();
            var refinementHistory = new List<string>();

            for (int iteration = 1; iteration <= maxIterations; iteration++)
            {
                response.ExecutionSteps.Add($"Step {iteration + 1}: Research iteration {iteration}");

                // Search with current query
                var searchResult = await _searchAgent.SearchAsync(new SearchAgentRequest
                {
                    SessionId = sessionId,
                    Query = currentQuery,
                    SearchType = "semantic",
                    MaxResults = 5
                }, cancellationToken);

                response.WorkflowResults[$"iteration_{iteration}"] = searchResult;
                allResults.AddRange(searchResult.Results);

                // Analyze results and refine query for next iteration
                if (iteration < maxIterations)
                {
                    var refinedQuery = RefineSearchQuery(currentQuery, searchResult.Results, iteration);
                    refinementHistory.Add($"Iteration {iteration}: '{currentQuery}' → '{refinedQuery}'");
                    currentQuery = refinedQuery;

                    response.ExecutionSteps.Add($"Step {iteration + 1}b: Refined query to '{refinedQuery}'");
                }
            }

            // Final synthesis
            response.ExecutionSteps.Add("Final Step: Synthesizing findings from all iterations");
            response.FinalAnswer = SynthesizeIterativeResearch(researchTopic, allResults, refinementHistory);

            response.Metadata["workflow_type"] = "iterative_research";
            response.Metadata["learning_objective"] = "Understanding iterative agent workflows and query refinement";
            response.Metadata["iterations_completed"] = maxIterations;
            response.Metadata["refinement_history"] = refinementHistory;
            response.Metadata["total_results_gathered"] = allResults.Count;

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Iterative Research Assistant");
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    // Helper methods for educational purposes
    private List<string> ExtractKeyTermsFromDocument(string content)
    {
        // Simple keyword extraction for demonstration
        var words = content.Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Where(w => w.Length > 4)
            .Select(w => w.Trim('.', ',', '!', '?', ';', ':'))
            .GroupBy(w => w.ToLowerInvariant())
            .OrderByDescending(g => g.Count())
            .Take(5)
            .Select(g => g.Key)
            .ToList();

        _logger.LogInformation("Extracted key terms: {Terms}", string.Join(", ", words));
        return words;
    }

    private string GenerateBasicInsights(DocumentAgentResponse docResult, SearchAgentResponse searchResult, List<string> keyTerms)
    {
        return $@"📊 BASIC DOCUMENT ANALYSIS INSIGHTS:

🔍 Key Terms Identified: {string.Join(", ", keyTerms)}

📄 Document Analysis:
- Analysis completed: {docResult.Success}
- Processing confidence: {docResult.ConfidenceScore:P1}
- Insights found: {docResult.Insights.Count}

🔎 Related Content Search:
- Related documents found: {searchResult.TotalCount}
- Average relevance score: {(searchResult.Results.Count > 0 ? searchResult.Results.Average(r => r.Score) : 0):P1}
- Search quality: {searchResult.Metadata.GetValueOrDefault("search_quality", 0.0)}

💡 Learning Notes:
- This workflow demonstrates sequential agent coordination
- Document analysis → Key term extraction → Related content search
- Each step builds on the previous step's output";
    }

    private string PerformCrossModalAnalysis(Dictionary<string, object> results)
    {
        var analysis = "🧠 CROSS-MODAL INTELLIGENCE ANALYSIS:\n\n";

        foreach (var result in results)
        {
            var agentResponse = (AgentResponse)result.Value;
            analysis += $"📊 {result.Key.ToUpperInvariant()} ANALYSIS:\n";
            analysis += $"- Status: {(agentResponse.Success ? "✅ Successful" : "❌ Failed")}\n";
            analysis += $"- Processing time: {agentResponse.ExecutionTimeMs}ms\n";
            analysis += $"- Response: {agentResponse.Response[..Math.Min(100, agentResponse.Response.Length)]}...\n\n";
        }

        analysis += "💡 Learning Notes:\n";
        analysis += "- This workflow demonstrates parallel agent execution\n";
        analysis += "- Multiple data types processed simultaneously\n";
        analysis += "- Results synthesized for comprehensive analysis";

        return analysis;
    }

    private string RefineSearchQuery(string originalQuery, List<SearchResult> results, int iteration)
    {
        // Simple query refinement logic for demonstration
        if (results.Count == 0)
        {
            return $"{originalQuery} overview basics";
        }

        // Extract terms from top result
        var topResult = results.OrderByDescending(r => r.Score).First();
        var refinementTerms = topResult.Content.Split(' ')
            .Where(w => w.Length > 4 && !originalQuery.Contains(w, StringComparison.OrdinalIgnoreCase))
            .Take(2)
            .ToList();

        if (refinementTerms.Any())
        {
            return $"{originalQuery} {string.Join(" ", refinementTerms)}";
        }

        return $"{originalQuery} detailed analysis";
    }

    private string SynthesizeIterativeResearch(string topic, List<SearchResult> allResults, List<string> refinementHistory)
    {
        return $@"🔬 ITERATIVE RESEARCH SYNTHESIS:

📋 Research Topic: {topic}

🔄 Query Evolution:
{string.Join("\n", refinementHistory)}

📊 Research Statistics:
- Total results gathered: {allResults.Count}
- Average relevance: {(allResults.Count > 0 ? allResults.Average(r => r.Score) : 0):P1}
- Unique sources: {allResults.Select(r => r.Metadata.GetValueOrDefault("doc_id", "unknown")).Distinct().Count()}

🎯 Top Findings:
{string.Join("\n", allResults.OrderByDescending(r => r.Score).Take(3).Select((r, i) => $"{i + 1}. {r.Content[..Math.Min(80, r.Content.Length)]}... (Score: {r.Score:F3})"))}

💡 Learning Notes:
- This workflow demonstrates iterative agent coordination
- Queries were refined based on previous results
- Multiple search iterations provided comprehensive coverage";
    }
}
