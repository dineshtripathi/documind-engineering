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
/// Specialized agent for document processing and analysis
/// </summary>
public class DocumentAgent : IDocumentAgent
{
    private readonly ILogger<DocumentAgent> _logger;
    private readonly AgentOptions _options;
    private readonly Kernel _kernel;
    private readonly HttpClient _httpClient;

    public string AgentType => "DocumentAgent";

    public DocumentAgent(
        ILogger<DocumentAgent> logger,
        IOptions<AgentOptions> options,
        Kernel kernel,
        HttpClient httpClient)
    {
        _logger = logger;
        _options = options.Value;
        _kernel = kernel;
        _httpClient = httpClient;
    }

    public async Task<AgentResponse> ProcessAsync(AgentRequest request, CancellationToken cancellationToken = default)
    {
        if (request is DocumentAgentRequest docRequest)
        {
            return await ProcessDocumentAsync(docRequest, cancellationToken);
        }

        return new AgentResponse
        {
            Success = false,
            Error = "Invalid request type for DocumentAgent",
            AgentType = AgentType
        };
    }

    public async Task<DocumentAgentResponse> ProcessDocumentAsync(DocumentAgentRequest request, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            _logger.LogInformation("Processing document request: {ProcessingType}", request.ProcessingType);

            var response = new DocumentAgentResponse
            {
                SessionId = request.SessionId,
                AgentType = AgentType
            };

            switch (request.ProcessingType.ToLowerInvariant())
            {
                case "analysis":
                    response.Response = await AnalyzeDocumentAsync(request.FileContent ?? string.Empty, cancellationToken);
                    response.Insights = await ExtractInsightsAsync(request.FileContent ?? string.Empty, cancellationToken);
                    break;

                case "extraction":
                    response.ExtractedText = await ExtractTextAsync(request.FileContent ?? string.Empty, request.FileName ?? string.Empty, cancellationToken);
                    response.Response = $"Successfully extracted {response.ExtractedText?.Length ?? 0} characters from {request.FileName}";
                    break;

                case "summary":
                    response.Summary = await SummarizeAsync(request.FileContent ?? string.Empty, cancellationToken);
                    response.Response = "Document summarized successfully";
                    break;

                default:
                    response.Response = await AnalyzeDocumentAsync(request.FileContent ?? string.Empty, cancellationToken);
                    break;
            }

            response.ConfidenceScore = CalculateConfidenceScore(response);
            response.ExecutionTimeMs = stopwatch.ElapsedMilliseconds;

            _logger.LogInformation("Document processing completed in {ElapsedMs}ms", stopwatch.ElapsedMilliseconds);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing document request");

            return new DocumentAgentResponse
            {
                Success = false,
                Error = ex.Message,
                SessionId = request.SessionId,
                AgentType = AgentType,
                ExecutionTimeMs = stopwatch.ElapsedMilliseconds
            };
        }
    }

    public async Task<string> ExtractTextAsync(string fileContent, string fileName, CancellationToken cancellationToken = default)
    {
        try
        {
            // Use Semantic Kernel for intelligent text extraction
            var extractionPrompt = """
                Extract and clean the text content from the following document.
                Focus on preserving structure and readability while removing any formatting artifacts.

                Document Content:
                {{$input}}

                Please provide clean, readable text:
                """;

            var extractionFunction = _kernel.CreateFunctionFromPrompt(extractionPrompt);
            var result = await _kernel.InvokeAsync(extractionFunction, new() { ["input"] = fileContent }, cancellationToken);

            return result.ToString() ?? fileContent;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error extracting text from document");
            return fileContent; // Fallback to original content
        }
    }

    public async Task<string> SummarizeAsync(string content, CancellationToken cancellationToken = default)
    {
        try
        {
            var summaryPrompt = """
                Create a comprehensive summary of the following document.
                Include key points, main themes, and important details.
                Keep the summary concise but informative.

                Document Content:
                {{$input}}

                Summary:
                """;

            var summaryFunction = _kernel.CreateFunctionFromPrompt(summaryPrompt);
            var result = await _kernel.InvokeAsync(summaryFunction, new() { ["input"] = content }, cancellationToken);

            return result.ToString() ?? "Unable to generate summary";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error summarizing document");
            return "Error generating summary: " + ex.Message;
        }
    }

    private async Task<string> AnalyzeDocumentAsync(string content, CancellationToken cancellationToken)
    {
        try
        {
            var analysisPrompt = """
                Analyze the following document and provide insights about:
                1. Document type and purpose
                2. Key topics and themes
                3. Important entities (people, places, organizations)
                4. Sentiment and tone
                5. Notable patterns or structure

                Document Content:
                {{$input}}

                Analysis:
                """;

            var analysisFunction = _kernel.CreateFunctionFromPrompt(analysisPrompt);
            var result = await _kernel.InvokeAsync(analysisFunction, new() { ["input"] = content }, cancellationToken);

            return result.ToString() ?? "Unable to analyze document";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing document");
            return "Error analyzing document: " + ex.Message;
        }
    }

    private async Task<List<string>> ExtractInsightsAsync(string content, CancellationToken cancellationToken)
    {
        try
        {
            var insightsPrompt = """
                Extract key insights from this document as a list of important points.
                Focus on actionable insights, key findings, and significant information.

                Document Content:
                {{$input}}

                Please provide insights as a numbered list:
                """;

            var insightsFunction = _kernel.CreateFunctionFromPrompt(insightsPrompt);
            var result = await _kernel.InvokeAsync(insightsFunction, new() { ["input"] = content }, cancellationToken);

            var insightsText = result.ToString() ?? string.Empty;

            // Parse the numbered list into individual insights
            var insights = insightsText
                .Split('\n')
                .Where(line => !string.IsNullOrWhiteSpace(line))
                .Select(line => line.Trim())
                .Where(line => line.Length > 0)
                .ToList();

            return insights;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error extracting insights");
            return new List<string> { "Error extracting insights: " + ex.Message };
        }
    }

    private static double CalculateConfidenceScore(DocumentAgentResponse response)
    {
        // Simple confidence calculation based on response completeness
        var score = 0.5; // Base score

        if (!string.IsNullOrEmpty(response.Response)) score += 0.2;
        if (!string.IsNullOrEmpty(response.ExtractedText)) score += 0.1;
        if (!string.IsNullOrEmpty(response.Summary)) score += 0.1;
        if (response.Insights.Count > 0) score += 0.1;

        return Math.Min(1.0, score);
    }
}
