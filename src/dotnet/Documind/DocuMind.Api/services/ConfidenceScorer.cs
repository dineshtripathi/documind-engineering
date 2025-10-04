using System.Text.RegularExpressions;
using Documind.Contracts;
using Documind.Common.Extensions;

namespace DocuMind.Api.Services;

/// <summary>
/// Evaluates response quality and confidence for AI-generated answers
/// </summary>
public interface IConfidenceScorer
{
    Task<ConfidenceScore> EvaluateResponseAsync(
        string query,
        string response,
        IReadOnlyList<ContextItem> context,
        string route,
        CancellationToken ct = default);
}

/// <summary>
/// Comprehensive confidence assessment for AI responses
/// </summary>
public sealed record ConfidenceScore(
    double OverallConfidence,
    CitationQuality CitationQuality,
    ResponseQuality ResponseQuality,
    ContextRelevance ContextRelevance,
    bool ShouldEscalate,
    string Reasoning,
    Dictionary<string, double> DetailedMetrics
);

/// <summary>
/// Citation quality assessment
/// </summary>
public sealed record CitationQuality(
    double Score,
    int CitationCount,
    bool HasValidCitations,
    bool HasHallucinations,
    string Assessment
);

/// <summary>
/// Response quality assessment
/// </summary>
public sealed record ResponseQuality(
    double Score,
    bool IsCoherent,
    bool IsRelevant,
    bool IsComplete,
    bool IsAccurate,
    string Assessment
);

/// <summary>
/// Context relevance assessment
/// </summary>
public sealed record ContextRelevance(
    double Score,
    int RelevantChunks,
    double AverageRelevance,
    bool SufficientContext,
    string Assessment
);

/// <summary>
/// Implementation of response confidence scoring
/// </summary>
public sealed class ConfidenceScorer : IConfidenceScorer
{
    private readonly ILogger<ConfidenceScorer> _logger;

    // Citation patterns
    private static readonly Regex _citationPattern = new(@"\[(\d+)\]", RegexOptions.Compiled);

    // Quality indicators
    private static readonly HashSet<string> _uncertaintyPhrases = new(StringComparer.OrdinalIgnoreCase)
    {
        "i don't know", "i'm not sure", "i cannot", "i can't", "unclear",
        "uncertain", "maybe", "perhaps", "possibly", "might be",
        "could be", "not found", "no information", "insufficient"
    };

    private static readonly HashSet<string> _confidencePhrases = new(StringComparer.OrdinalIgnoreCase)
    {
        "according to", "based on", "the document states", "as shown in",
        "specifically", "clearly", "definitely", "certainly", "precisely"
    };

    private static readonly HashSet<string> _hallucinationIndicators = new(StringComparer.OrdinalIgnoreCase)
    {
        "as an ai", "i apologize", "i cannot provide", "i don't have access",
        "my training data", "as of my last update", "i'm not able to"
    };

    public ConfidenceScorer(ILogger<ConfidenceScorer> logger)
    {
        _logger = logger;
    }

    public Task<ConfidenceScore> EvaluateResponseAsync(
        string query,
        string response,
        IReadOnlyList<ContextItem> context,
        string route,
        CancellationToken ct = default)
    {
        try
        {
            var citationQuality = EvaluateCitations(response, context);
            var responseQuality = EvaluateResponseQuality(query, response);
            var contextRelevance = EvaluateContextRelevance(query, context);

            var overallConfidence = CalculateOverallConfidence(
                citationQuality, responseQuality, contextRelevance, route);

            var shouldEscalate = DetermineEscalation(
                overallConfidence, citationQuality, responseQuality, route);

            var reasoning = BuildReasoning(
                citationQuality, responseQuality, contextRelevance, overallConfidence);

            var detailedMetrics = BuildDetailedMetrics(
                citationQuality, responseQuality, contextRelevance);

            var score = new ConfidenceScore(
                OverallConfidence: overallConfidence,
                CitationQuality: citationQuality,
                ResponseQuality: responseQuality,
                ContextRelevance: contextRelevance,
                ShouldEscalate: shouldEscalate,
                Reasoning: reasoning,
                DetailedMetrics: detailedMetrics
            );

            _logger.LogDebug("Confidence evaluation: {Query} -> {Confidence:F2} ({Route})",
                query.Truncate(50), overallConfidence, route);

            return Task.FromResult(score);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error evaluating response confidence");

            // Return safe fallback
            return Task.FromResult(new ConfidenceScore(
                OverallConfidence: 0.5,
                CitationQuality: new CitationQuality(0.5, 0, false, false, "Error during evaluation"),
                ResponseQuality: new ResponseQuality(0.5, true, true, true, true, "Error during evaluation"),
                ContextRelevance: new ContextRelevance(0.5, 0, 0.5, false, "Error during evaluation"),
                ShouldEscalate: true,
                Reasoning: "Confidence evaluation failed",
                DetailedMetrics: new Dictionary<string, double>()
            ));
        }
    }

    private static CitationQuality EvaluateCitations(string response, IReadOnlyList<ContextItem> context)
    {
        var citations = _citationPattern.Matches(response);
        var citationCount = citations.Count;
        var maxContextIndex = context.Count;

        // Check if citations are valid (within context range)
        var validCitations = 0;
        var invalidCitations = 0;

        foreach (Match citation in citations)
        {
            if (int.TryParse(citation.Groups[1].Value, out var index))
            {
                if (index >= 1 && index <= maxContextIndex)
                    validCitations++;
                else
                    invalidCitations++;
            }
        }

        var hasValidCitations = validCitations > 0;
        var hasHallucinations = invalidCitations > 0 || ContainsHallucinationIndicators(response);

        // Calculate citation score
        var citationScore = 0.0;

        if (context.Count > 0) // Only evaluate if context was provided
        {
            if (hasValidCitations && !hasHallucinations)
                citationScore = Math.Min(1.0, validCitations / Math.Max(1.0, response.Split('.').Length * 0.3));
            else if (hasValidCitations && hasHallucinations)
                citationScore = 0.6; // Partial credit
            else if (hasHallucinations)
                citationScore = 0.2; // Heavy penalty
            else
                citationScore = 0.4; // No citations but no hallucinations
        }
        else
        {
            // No context provided - cloud route
            citationScore = hasHallucinations ? 0.3 : 0.7;
        }

        var assessment = BuildCitationAssessment(hasValidCitations, hasHallucinations, validCitations, invalidCitations);

        return new CitationQuality(
            Score: citationScore,
            CitationCount: validCitations,
            HasValidCitations: hasValidCitations,
            HasHallucinations: hasHallucinations,
            Assessment: assessment
        );
    }

    private static bool ContainsHallucinationIndicators(string response)
    {
        var lowerResponse = response.ToLowerInvariant();
        return _hallucinationIndicators.Any(indicator => lowerResponse.Contains(indicator));
    }

    private static string BuildCitationAssessment(bool hasValid, bool hasHallucinations, int valid, int invalid)
    {
        return (hasValid, hasHallucinations) switch
        {
            (true, false) => $"Excellent citations ({valid} valid)",
            (true, true) => $"Mixed citations ({valid} valid, {invalid} invalid)",
            (false, true) => "Hallucination detected",
            (false, false) => "No citations provided"
        };
    }

    private static ResponseQuality EvaluateResponseQuality(string query, string response)
    {
        var lowerResponse = response.ToLowerInvariant();
        var words = response.Split(' ', StringSplitOptions.RemoveEmptyEntries);

        // Coherence check
        var isCoherent = !string.IsNullOrWhiteSpace(response) &&
                        response.Length > 10 &&
                        !response.Contains("```") && // Not just code
                        words.Length > 3;

        // Relevance check (basic keyword matching)
        var queryWords = query.ToLowerInvariant()
            .Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Where(w => w.Length > 3)
            .ToHashSet();

        var responseWords = lowerResponse
            .Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Where(w => w.Length > 3)
            .ToHashSet();

        var commonWords = queryWords.Intersect(responseWords).Count();
        var isRelevant = queryWords.Count == 0 || (double)commonWords / queryWords.Count > 0.1;

        // Completeness check
        var hasUncertainty = _uncertaintyPhrases.Any(phrase => lowerResponse.Contains(phrase));
        var hasConfidence = _confidencePhrases.Any(phrase => lowerResponse.Contains(phrase));
        var isComplete = !hasUncertainty && response.Length > 50;

        // Accuracy indicators
        var isAccurate = !hasUncertainty && (hasConfidence || !ContainsHallucinationIndicators(response));

        // Calculate overall response score
        var score = (
            (isCoherent ? 0.25 : 0) +
            (isRelevant ? 0.25 : 0) +
            (isComplete ? 0.25 : 0) +
            (isAccurate ? 0.25 : 0)
        );

        var assessment = BuildResponseAssessment(isCoherent, isRelevant, isComplete, isAccurate);

        return new ResponseQuality(
            Score: score,
            IsCoherent: isCoherent,
            IsRelevant: isRelevant,
            IsComplete: isComplete,
            IsAccurate: isAccurate,
            Assessment: assessment
        );
    }

    private static string BuildResponseAssessment(bool coherent, bool relevant, bool complete, bool accurate)
    {
        var qualities = new List<string>();
        if (coherent) qualities.Add("coherent");
        if (relevant) qualities.Add("relevant");
        if (complete) qualities.Add("complete");
        if (accurate) qualities.Add("accurate");

        return qualities.Any() ? string.Join(", ", qualities) : "needs improvement";
    }

    private static ContextRelevance EvaluateContextRelevance(string query, IReadOnlyList<ContextItem> context)
    {
        if (!context.Any())
        {
            return new ContextRelevance(
                Score: 0.0,
                RelevantChunks: 0,
                AverageRelevance: 0.0,
                SufficientContext: false,
                Assessment: "No context provided"
            );
        }

        var queryWords = query.ToLowerInvariant()
            .Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Where(w => w.Length > 3)
            .ToHashSet();

        if (!queryWords.Any())
        {
            return new ContextRelevance(
                Score: 0.5,
                RelevantChunks: context.Count,
                AverageRelevance: 0.5,
                SufficientContext: context.Count >= 2,
                Assessment: "Unable to assess relevance"
            );
        }

        var relevanceScores = new List<double>();
        var relevantChunks = 0;

        foreach (var item in context)
        {
            var contextText = $"{item.DocId} {item.ChunkId}".ToLowerInvariant();
            var contextWords = contextText.Split(' ', StringSplitOptions.RemoveEmptyEntries).ToHashSet();

            var commonWords = queryWords.Intersect(contextWords).Count();
            var relevanceScore = (double)commonWords / queryWords.Count;

            relevanceScores.Add(relevanceScore);

            if (relevanceScore > 0.1) // Threshold for "relevant"
                relevantChunks++;
        }

        var averageRelevance = relevanceScores.Average();
        var sufficientContext = relevantChunks >= 2 && averageRelevance > 0.15;

        var contextScore = Math.Min(1.0, averageRelevance * 2); // Scale up moderate relevance

        var assessment = BuildContextAssessment(relevantChunks, context.Count, averageRelevance);

        return new ContextRelevance(
            Score: contextScore,
            RelevantChunks: relevantChunks,
            AverageRelevance: averageRelevance,
            SufficientContext: sufficientContext,
            Assessment: assessment
        );
    }

    private static string BuildContextAssessment(int relevant, int total, double avgRelevance)
    {
        var percentage = total > 0 ? (double)relevant / total * 100 : 0;

        return percentage switch
        {
            >= 75 => $"Highly relevant ({relevant}/{total})",
            >= 50 => $"Moderately relevant ({relevant}/{total})",
            >= 25 => $"Partially relevant ({relevant}/{total})",
            _ => $"Low relevance ({relevant}/{total})"
        };
    }

    private static double CalculateOverallConfidence(
        CitationQuality citation,
        ResponseQuality response,
        ContextRelevance context,
        string route)
    {
        // Weighted combination based on route
        var weights = route.ToLowerInvariant() switch
        {
            "local" => (citation: 0.4, response: 0.3, context: 0.3), // Citations crucial for RAG
            "cloud" => (citation: 0.2, response: 0.6, context: 0.2), // Response quality key
            _ => (citation: 0.3, response: 0.4, context: 0.3)        // Balanced
        };

        var confidence =
            citation.Score * weights.citation +
            response.Score * weights.response +
            context.Score * weights.context;

        return Math.Round(confidence, 3);
    }

    private static bool DetermineEscalation(
        double overallConfidence,
        CitationQuality citation,
        ResponseQuality response,
        string route)
    {
        // Escalate if confidence is too low
        if (overallConfidence < 0.6) return true;

        // Escalate if hallucinations detected
        if (citation.HasHallucinations) return true;

        // Escalate if response quality is poor
        if (!response.IsCoherent || !response.IsRelevant) return true;

        // Don't escalate cloud responses (nowhere to go)
        if (route.ToLowerInvariant() == "cloud") return false;

        return false;
    }

    private static string BuildReasoning(
        CitationQuality citation,
        ResponseQuality response,
        ContextRelevance context,
        double confidence)
    {
        var reasons = new List<string>();

        if (confidence >= 0.8)
            reasons.Add("High confidence response");
        else if (confidence >= 0.6)
            reasons.Add("Moderate confidence");
        else
            reasons.Add("Low confidence");

        if (citation.HasValidCitations)
            reasons.Add("well-cited");
        if (citation.HasHallucinations)
            reasons.Add("contains hallucinations");
        if (response.IsAccurate && response.IsComplete)
            reasons.Add("accurate and complete");
        if (!response.IsRelevant)
            reasons.Add("relevance concerns");
        if (context.SufficientContext)
            reasons.Add("good context");

        return string.Join(", ", reasons);
    }

    private static Dictionary<string, double> BuildDetailedMetrics(
        CitationQuality citation,
        ResponseQuality response,
        ContextRelevance context)
    {
        return new Dictionary<string, double>
        {
            ["citation_score"] = citation.Score,
            ["response_score"] = response.Score,
            ["context_score"] = context.Score,
            ["citation_count"] = citation.CitationCount,
            ["relevant_chunks"] = context.RelevantChunks,
            ["average_relevance"] = context.AverageRelevance,
            ["coherence"] = response.IsCoherent ? 1.0 : 0.0,
            ["relevance"] = response.IsRelevant ? 1.0 : 0.0,
            ["completeness"] = response.IsComplete ? 1.0 : 0.0,
            ["accuracy"] = response.IsAccurate ? 1.0 : 0.0
        };
    }
}
