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
/// Specialized agent for search operations and information retrieval
/// </summary>
public class SearchAgent : ISearchAgent
{
    private readonly ILogger<SearchAgent> _logger;
    private readonly AgentOptions _options;
    private readonly Kernel _kernel;
    private readonly HttpClient _httpClient;

    public string AgentType => "SearchAgent";

    public SearchAgent(
        ILogger<SearchAgent> logger,
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
        if (request is SearchAgentRequest searchRequest)
        {
            return await SearchAsync(searchRequest, cancellationToken);
        }

        return new AgentResponse
        {
            Success = false,
            Error = "Invalid request type for SearchAgent",
            AgentType = AgentType
        };
    }

    public async Task<SearchAgentResponse> SearchAsync(SearchAgentRequest request, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            _logger.LogInformation("Processing search request: {SearchType} for query: {Query}",
                request.SearchType, request.Query);

            var response = new SearchAgentResponse
            {
                SessionId = request.SessionId,
                AgentType = AgentType
            };

            List<SearchResult> results;

            switch (request.SearchType.ToLowerInvariant())
            {
                case "semantic":
                    results = await SemanticSearchAsync(request.Query, request.MaxResults, cancellationToken);
                    break;

                case "exact":
                    results = await ExactSearchAsync(request.Query, request.MaxResults, cancellationToken);
                    break;

                case "hybrid":
                    results = await HybridSearchAsync(request.Query, request.MaxResults, cancellationToken);
                    break;

                default:
                    results = await SemanticSearchAsync(request.Query, request.MaxResults, cancellationToken);
                    break;
            }

            response.Results = results;
            response.TotalCount = results.Count;
            response.SearchTimeMs = stopwatch.ElapsedMilliseconds;
            response.Response = $"Found {results.Count} results for query: {request.Query}";

            // Enhance results with AI analysis
            response = await EnhanceSearchResults(response, request.Query, cancellationToken);

            response.ExecutionTimeMs = stopwatch.ElapsedMilliseconds;

            _logger.LogInformation("Search completed in {ElapsedMs}ms with {ResultCount} results",
                stopwatch.ElapsedMilliseconds, results.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing search request");

            return new SearchAgentResponse
            {
                Success = false,
                Error = ex.Message,
                SessionId = request.SessionId,
                AgentType = AgentType,
                ExecutionTimeMs = stopwatch.ElapsedMilliseconds
            };
        }
    }

    public async Task<List<SearchResult>> SemanticSearchAsync(string query, int maxResults, CancellationToken cancellationToken = default)
    {
        try
        {
            // Call the existing RAG API for semantic search using GET with query parameters
            var encodedQuery = Uri.EscapeDataString(query);
            var url = $"{_options.ServiceEndpoints.RagApiUrl}/rag/search?q={encodedQuery}&top_k={maxResults}";

            var response = await _httpClient.GetAsync(url, cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);
                return ParseRagSearchResults(responseContent);
            }
            else
            {
                _logger.LogWarning("RAG API search failed with status: {StatusCode}", response.StatusCode);
                return await FallbackSearch(query, maxResults, cancellationToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing semantic search");
            return await FallbackSearch(query, maxResults, cancellationToken);
        }
    }

    public async Task<List<SearchResult>> HybridSearchAsync(string query, int maxResults, CancellationToken cancellationToken = default)
    {
        try
        {
            // Combine semantic and exact search results
            var semanticResults = await SemanticSearchAsync(query, maxResults / 2, cancellationToken);
            var exactResults = await ExactSearchAsync(query, maxResults / 2, cancellationToken);

            // Merge and deduplicate results
            var allResults = new List<SearchResult>();
            allResults.AddRange(semanticResults);
            allResults.AddRange(exactResults);

            // Remove duplicates based on content similarity
            var uniqueResults = await DeduplicateResults(allResults, cancellationToken);

            // Sort by score and take top results
            return uniqueResults
                .OrderByDescending(r => r.Score)
                .Take(maxResults)
                .ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing hybrid search");
            return await SemanticSearchAsync(query, maxResults, cancellationToken);
        }
    }

    private async Task<List<SearchResult>> ExactSearchAsync(string query, int maxResults, CancellationToken cancellationToken)
    {
        try
        {
            // For exact search, we'll use a different endpoint or search strategy
            // This could involve exact text matching in Qdrant or a different search API

            // For now, we'll enhance semantic search with exact matching requirements
            var enhancedQuery = $"exact match: {query}";
            return await SemanticSearchAsync(enhancedQuery, maxResults, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing exact search");
            return new List<SearchResult>();
        }
    }

    private Task<List<SearchResult>> FallbackSearch(string query, int maxResults, CancellationToken cancellationToken)
    {
        try
        {
            // Simple fallback without Semantic Kernel dependency
            _logger.LogInformation("Using fallback search for query: {Query}", query);

            var fallbackResults = new List<SearchResult>
            {
                new()
                {
                    Content = $"Fallback search result for '{query}'. This is a demo result showing the search agent is working. In a full implementation, this would use AI to generate relevant content based on the query.",
                    Score = 0.8,
                    Source = "Fallback Search",
                    Metadata = new Dictionary<string, object>
                    {
                        ["generated"] = true,
                        ["query"] = query,
                        ["timestamp"] = DateTime.UtcNow
                    }
                }
            };

            return Task.FromResult(fallbackResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in fallback search");
            return Task.FromResult(new List<SearchResult>());
        }
    }

    private List<SearchResult> ParseSearchResults(string jsonResponse, string searchType)
    {
        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };

            // Parse the JSON response from the RAG API
            using var doc = JsonDocument.Parse(jsonResponse);
            var results = new List<SearchResult>();

            if (doc.RootElement.TryGetProperty("results", out var resultsElement))
            {
                foreach (var item in resultsElement.EnumerateArray())
                {
                    var result = new SearchResult();

                    if (item.TryGetProperty("content", out var contentElement))
                        result.Content = contentElement.GetString() ?? string.Empty;

                    if (item.TryGetProperty("score", out var scoreElement))
                        result.Score = scoreElement.GetDouble();

                    if (item.TryGetProperty("metadata", out var metadataElement))
                    {
                        var metadata = JsonSerializer.Deserialize<Dictionary<string, object>>(
                            metadataElement.GetRawText(), options) ?? new();
                        result.Metadata = metadata;
                    }

                    result.Source = searchType;
                    results.Add(result);
                }
            }

            return results;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error parsing search results");
            return new List<SearchResult>();
        }
    }

    private List<SearchResult> ParseRagSearchResults(string jsonResponse)
    {
        try
        {
            // Parse the RAG API response format
            using var doc = JsonDocument.Parse(jsonResponse);
            var results = new List<SearchResult>();

            if (doc.RootElement.TryGetProperty("top", out var topElement))
            {
                foreach (var item in topElement.EnumerateArray())
                {
                    var result = new SearchResult();

                    if (item.TryGetProperty("preview", out var previewElement))
                        result.Content = previewElement.GetString() ?? string.Empty;

                    if (item.TryGetProperty("score", out var scoreElement))
                        result.Score = scoreElement.GetDouble();

                    // Add metadata from the RAG response
                    result.Metadata = new Dictionary<string, object>();
                    if (item.TryGetProperty("doc_id", out var docIdElement))
                        result.Metadata["doc_id"] = docIdElement.GetString() ?? string.Empty;

                    if (item.TryGetProperty("chunk", out var chunkElement))
                        result.Metadata["chunk"] = chunkElement.GetString() ?? string.Empty;

                    result.Source = "RAG API";
                    results.Add(result);
                }
            }

            return results;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error parsing RAG search results");
            return new List<SearchResult>();
        }
    }

    private Task<List<SearchResult>> DeduplicateResults(List<SearchResult> results, CancellationToken cancellationToken)
    {
        try
        {
            var uniqueResults = new List<SearchResult>();
            var seenContent = new HashSet<string>();

            foreach (var result in results)
            {
                // Simple deduplication based on content hash
                var contentHash = result.Content.GetHashCode().ToString();

                if (!seenContent.Contains(contentHash))
                {
                    seenContent.Add(contentHash);
                    uniqueResults.Add(result);
                }
            }

            return Task.FromResult(uniqueResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deduplicating results");
            return Task.FromResult(results); // Return original if deduplication fails
        }
    }

    private Task<SearchAgentResponse> EnhanceSearchResults(SearchAgentResponse response, string query, CancellationToken cancellationToken)
    {
        try
        {
            // Simple enhancement without AI for now
            var searchQuality = CalculateSearchQuality(response.Results);

            // Add analysis to metadata
            response.Metadata["search_quality"] = searchQuality;
            response.Metadata["query_analysis"] = $"Processed query: '{query}' with {response.Results.Count} results";
            response.Metadata["avg_score"] = response.Results.Count > 0 ? response.Results.Average(r => r.Score) : 0.0;

            return Task.FromResult(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error enhancing search results");
            return Task.FromResult(response);
        }
    }

    private static double CalculateSearchQuality(List<SearchResult> results)
    {
        if (results.Count == 0) return 0.0;

        var avgScore = results.Average(r => r.Score);
        var scoreVariance = results.Count > 1
            ? results.Select(r => Math.Pow(r.Score - avgScore, 2)).Average()
            : 0.0;

        // Quality is higher when average score is high and variance is low
        var quality = avgScore * (1.0 - Math.Min(scoreVariance, 0.5));

        return Math.Max(0.0, Math.Min(1.0, quality));
    }
}
