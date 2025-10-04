using System.Text.RegularExpressions;
using Documind.Common.Extensions;

namespace DocuMind.Api.Services;

/// <summary>
/// Analyzes query complexity for intelligent AI model routing
/// </summary>
public interface IQueryAnalyzer
{
    Task<QueryAnalysis> AnalyzeAsync(string query, CancellationToken ct = default);
}

/// <summary>
/// Query complexity levels for routing decisions
/// </summary>
public enum QueryComplexity
{
    Simple,      // Basic factual questions, short answers
    Moderate,    // Multi-step reasoning, context needed
    Complex,     // Advanced reasoning, synthesis required
    Specialized  // Domain expertise, technical analysis
}

/// <summary>
/// Query domain classification
/// </summary>
public enum QueryDomain
{
    General,     // General knowledge, conversational
    Technical,   // Programming, engineering, IT
    Legal,       // Legal documents, compliance
    Medical,     // Healthcare, pharmaceutical
    Financial,   // Banking, accounting, finance
    Code,        // Code analysis, debugging
    Creative,    // Writing, content generation
    Research     // Academic, scientific analysis
}

/// <summary>
/// Query intent classification
/// </summary>
public enum QueryIntent
{
    Question,     // Direct question seeking answer
    Explanation,  // Request for detailed explanation
    Summary,      // Document summarization
    Analysis,     // Data/content analysis
    Generation,   // Content creation
    Translation,  // Language translation
    Extraction    // Information extraction
}

/// <summary>
/// Complete query analysis result
/// </summary>
public sealed record QueryAnalysis(
    QueryComplexity Complexity,
    QueryDomain Domain,
    QueryIntent Intent,
    double ConfidenceThreshold,
    string RecommendedRoute,
    double EstimatedCost,
    TimeSpan EstimatedLatency,
    string Reasoning
);

/// <summary>
/// Internal routing recommendation
/// </summary>
internal sealed record RoutingRecommendation(
    string Route,
    double ConfidenceThreshold,
    string Reasoning
);

/// <summary>
/// Implementation of query complexity analyzer
/// </summary>
public sealed class QueryAnalyzer : IQueryAnalyzer
{
    private readonly ILogger<QueryAnalyzer> _logger;

    // Complexity indicators
    private static readonly HashSet<string> _simpleIndicators = new(StringComparer.OrdinalIgnoreCase)
    {
        "what", "who", "when", "where", "is", "are", "can", "does", "do", "will", "how many"
    };

    private static readonly HashSet<string> _complexIndicators = new(StringComparer.OrdinalIgnoreCase)
    {
        "analyze", "compare", "evaluate", "synthesize", "explain why", "what if", "how does",
        "relationship between", "impact of", "strategy", "optimize", "recommend"
    };

    private static readonly HashSet<string> _specializedIndicators = new(StringComparer.OrdinalIgnoreCase)
    {
        "algorithm", "implementation", "architecture", "compliance", "regulation", "legal",
        "diagnosis", "treatment", "financial model", "statistical", "research", "methodology"
    };

    // Domain keywords
    private static readonly Dictionary<QueryDomain, HashSet<string>> _domainKeywords = new()
    {
        [QueryDomain.Technical] = new(StringComparer.OrdinalIgnoreCase)
        {
            "api", "database", "server", "network", "cloud", "aws", "azure", "docker", "kubernetes",
            "software", "hardware", "programming", "development", "engineering", "tech", "IT"
        },
        [QueryDomain.Legal] = new(StringComparer.OrdinalIgnoreCase)
        {
            "contract", "agreement", "legal", "law", "court", "regulation", "compliance",
            "policy", "terms", "clause", "liability", "jurisdiction", "statute"
        },
        [QueryDomain.Medical] = new(StringComparer.OrdinalIgnoreCase)
        {
            "patient", "treatment", "diagnosis", "medical", "health", "clinical", "drug",
            "pharmaceutical", "therapy", "symptom", "disease", "healthcare"
        },
        [QueryDomain.Financial] = new(StringComparer.OrdinalIgnoreCase)
        {
            "financial", "investment", "revenue", "profit", "cost", "budget", "accounting",
            "tax", "banking", "finance", "money", "economics", "market"
        },
        [QueryDomain.Code] = new(StringComparer.OrdinalIgnoreCase)
        {
            "function", "method", "class", "variable", "code", "debug", "error", "bug",
            "syntax", "compile", "programming", "script", "algorithm", "data structure"
        },
        [QueryDomain.Creative] = new(StringComparer.OrdinalIgnoreCase)
        {
            "write", "create", "generate", "story", "article", "content", "creative",
            "marketing", "copy", "blog", "social media", "design"
        },
        [QueryDomain.Research] = new(StringComparer.OrdinalIgnoreCase)
        {
            "research", "study", "analysis", "academic", "scientific", "paper", "journal",
            "methodology", "hypothesis", "experiment", "data", "statistics"
        }
    };

    public QueryAnalyzer(ILogger<QueryAnalyzer> logger)
    {
        _logger = logger;
    }

    public Task<QueryAnalysis> AnalyzeAsync(string query, CancellationToken ct = default)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                return Task.FromResult(new QueryAnalysis(
                    Complexity: QueryComplexity.Simple,
                    Domain: QueryDomain.General,
                    Intent: QueryIntent.Question,
                    ConfidenceThreshold: 0.8,
                    RecommendedRoute: "local",
                    EstimatedCost: 0.0001,
                    EstimatedLatency: TimeSpan.FromMilliseconds(100),
                    Reasoning: "Empty or null query"
                ));
            }

            var words = TokenizeQuery(query);
            var complexity = AnalyzeComplexity(query, words);
            var domain = AnalyzeDomain(words);
            var intent = AnalyzeIntent(query, words);

            var routing = DetermineRouting(complexity, domain, intent);
            var cost = EstimateCost(complexity, routing.Route);
            var latency = EstimateLatency(complexity, routing.Route);

            var analysis = new QueryAnalysis(
                Complexity: complexity,
                Domain: domain,
                Intent: intent,
                ConfidenceThreshold: routing.ConfidenceThreshold,
                RecommendedRoute: routing.Route,
                EstimatedCost: cost,
                EstimatedLatency: latency,
                Reasoning: routing.Reasoning
            );

            _logger.LogDebug("Query analysis: {Query} -> {Complexity}/{Domain}/{Intent} -> {Route}",
                query.Truncate(100), complexity, domain, intent, routing.Route);

            return Task.FromResult(analysis);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing query: {Query}", query.Truncate(100));

            // Fallback to safe defaults
            return Task.FromResult(new QueryAnalysis(
                Complexity: QueryComplexity.Moderate,
                Domain: QueryDomain.General,
                Intent: QueryIntent.Question,
                ConfidenceThreshold: 0.7,
                RecommendedRoute: "local",
                EstimatedCost: 0.001,
                EstimatedLatency: TimeSpan.FromMilliseconds(500),
                Reasoning: "Fallback due to analysis error"
            ));
        }
    }

    private static string[] TokenizeQuery(string query)
    {
        return query.ToLowerInvariant()
            .Split(new[] { ' ', '\t', '\n', '\r', ',', '.', '?', '!', ';', ':' },
                   StringSplitOptions.RemoveEmptyEntries);
    }

    private static QueryComplexity AnalyzeComplexity(string query, string[] words)
    {
        var length = words.Length;
        var lowerQuery = query.ToLowerInvariant();

        // Check for specialized indicators first
        if (_specializedIndicators.Any(indicator => lowerQuery.Contains(indicator)))
            return QueryComplexity.Specialized;

        // Check for complex indicators
        if (_complexIndicators.Any(indicator => lowerQuery.Contains(indicator)))
            return QueryComplexity.Complex;

        // Check for simple patterns
        if (_simpleIndicators.Any(indicator => lowerQuery.StartsWith(indicator)))
            return QueryComplexity.Simple;

        // Length-based heuristics
        return length switch
        {
            <= 5 => QueryComplexity.Simple,
            <= 15 => QueryComplexity.Moderate,
            <= 30 => QueryComplexity.Complex,
            _ => QueryComplexity.Specialized
        };
    }

    private static QueryDomain AnalyzeDomain(string[] words)
    {
        var domainScores = new Dictionary<QueryDomain, int>();

        foreach (var (domain, keywords) in _domainKeywords)
        {
            var score = words.Count(word => keywords.Contains(word));
            if (score > 0)
                domainScores[domain] = score;
        }

        // Return domain with highest score, or General if no matches
        return domainScores.Any()
            ? domainScores.OrderByDescending(kvp => kvp.Value).First().Key
            : QueryDomain.General;
    }

    private static QueryIntent AnalyzeIntent(string query, string[] words)
    {
        var lowerQuery = query.ToLowerInvariant();

        // Pattern matching for intent
        if (Regex.IsMatch(lowerQuery, @"\b(what|who|where|when|which|how many)\b"))
            return QueryIntent.Question;

        if (Regex.IsMatch(lowerQuery, @"\b(explain|describe|tell me about|how does|why)\b"))
            return QueryIntent.Explanation;

        if (Regex.IsMatch(lowerQuery, @"\b(summarize|summary|overview|brief)\b"))
            return QueryIntent.Summary;

        if (Regex.IsMatch(lowerQuery, @"\b(analyze|analysis|examine|evaluate|assess)\b"))
            return QueryIntent.Analysis;

        if (Regex.IsMatch(lowerQuery, @"\b(create|generate|write|make|build)\b"))
            return QueryIntent.Generation;

        if (Regex.IsMatch(lowerQuery, @"\b(translate|convert|transform)\b"))
            return QueryIntent.Translation;

        if (Regex.IsMatch(lowerQuery, @"\b(extract|find|get|retrieve|list)\b"))
            return QueryIntent.Extraction;

        // Default to question
        return QueryIntent.Question;
    }

    private static RoutingRecommendation DetermineRouting(
        QueryComplexity complexity,
        QueryDomain domain,
        QueryIntent intent)
    {
        // Route to cloud for complex reasoning or specialized domains
        if (complexity == QueryComplexity.Specialized)
        {
            return new RoutingRecommendation(
                Route: "cloud",
                ConfidenceThreshold: 0.8,
                Reasoning: "Specialized domain requires advanced reasoning"
            );
        }

        if (complexity == QueryComplexity.Complex &&
            (domain == QueryDomain.Legal || domain == QueryDomain.Medical))
        {
            return new RoutingRecommendation(
                Route: "cloud",
                ConfidenceThreshold: 0.85,
                Reasoning: "Complex query in sensitive domain"
            );
        }

        // Route to local for document retrieval and simple questions
        if (intent == QueryIntent.Extraction || intent == QueryIntent.Summary)
        {
            return new RoutingRecommendation(
                Route: "local",
                ConfidenceThreshold: 0.7,
                Reasoning: "Document retrieval favors local RAG"
            );
        }

        if (complexity == QueryComplexity.Simple)
        {
            return new RoutingRecommendation(
                Route: "local",
                ConfidenceThreshold: 0.6,
                Reasoning: "Simple query suitable for local processing"
            );
        }

        // Hybrid approach for moderate complexity
        return new RoutingRecommendation(
            Route: "hybrid",
            ConfidenceThreshold: 0.75,
            Reasoning: "Moderate complexity benefits from hybrid approach"
        );
    }

    private static double EstimateCost(QueryComplexity complexity, string route)
    {
        var baseCost = route.ToLowerInvariant() switch
        {
            "local" => 0.0001,   // Very low cost for local processing
            "cloud" => 0.002,    // Standard cloud API cost
            "hybrid" => 0.001,   // Mixed cost
            _ => 0.001
        };

        var complexityMultiplier = complexity switch
        {
            QueryComplexity.Simple => 0.5,
            QueryComplexity.Moderate => 1.0,
            QueryComplexity.Complex => 2.0,
            QueryComplexity.Specialized => 3.0,
            _ => 1.0
        };

        return baseCost * complexityMultiplier;
    }

    private static TimeSpan EstimateLatency(QueryComplexity complexity, string route)
    {
        var baseLatency = route.ToLowerInvariant() switch
        {
            "local" => TimeSpan.FromMilliseconds(200),   // Fast local processing
            "cloud" => TimeSpan.FromMilliseconds(1500),  // Network + processing
            "hybrid" => TimeSpan.FromMilliseconds(800),  // Mixed latency
            _ => TimeSpan.FromMilliseconds(1000)
        };

        var complexityMultiplier = complexity switch
        {
            QueryComplexity.Simple => 0.5,
            QueryComplexity.Moderate => 1.0,
            QueryComplexity.Complex => 1.5,
            QueryComplexity.Specialized => 2.5,
            _ => 1.0
        };

        return TimeSpan.FromMilliseconds(baseLatency.TotalMilliseconds * complexityMultiplier);
    }
}
