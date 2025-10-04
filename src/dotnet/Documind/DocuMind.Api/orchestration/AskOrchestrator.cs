namespace DocuMind.Api.Orchestration;

using System.Diagnostics;
using Documind.Contracts;
using DocuMind.Api.Clients;
using DocuMind.Api.Options;
using DocuMind.Api.Services;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;


public sealed class AskOrchestrator : IAskOrchestrator
{
    private readonly IRagClient _rag;
    private readonly IAzureOpenAiService _aoai;
    private readonly IQueryAnalyzer _queryAnalyzer;
    private readonly IConfidenceScorer _confidenceScorer;
    private readonly FeatureFlags _flags;
    private readonly ILogger<AskOrchestrator> _log;

    public AskOrchestrator(
        IRagClient rag,
        IAzureOpenAiService aoai,
        IQueryAnalyzer queryAnalyzer,
        IConfidenceScorer confidenceScorer,
        IOptions<FeatureFlags> flags,
        ILogger<AskOrchestrator> log)
    {
        _rag = rag;
        _aoai = aoai;
        _queryAnalyzer = queryAnalyzer;
        _confidenceScorer = confidenceScorer;
        _flags = flags.Value;
        _log = log;
    }

    public async Task<AskResponse> AskAsync(string userQuery, CancellationToken ct = default)
    {
        // 1) Analyze query complexity for intelligent routing
        var queryAnalysis = await _queryAnalyzer.AnalyzeAsync(userQuery, ct);

        _log.LogInformation("Query analysis: {Complexity} {Domain} {Intent} -> {Route}",
            queryAnalysis.Complexity, queryAnalysis.Domain, queryAnalysis.Intent, queryAnalysis.RecommendedRoute);

        RagAskResponse? lastRag = null;
        long lastLocalMs = 0;
        string actualRoute;
        string response;
        IReadOnlyList<ContextItem> context = Array.Empty<ContextItem>();
        Timings timings;

        // 2) Hard dependency: RAG required (overrides intelligence)
        if (_flags.RagRequired)
        {
            var (ragResult, localMs) = await TryLocalRagAsync(userQuery, ct);

            if (IsLocalAnswer(ragResult))
            {
                actualRoute = "local";
                response = ragResult!.Answer!;
                context = ragResult.ContextMap;
                timings = new Timings(localMs, 0);
            }
            else
            {
                _log.LogInformation("RAG required but unavailable/abstained. Returning 'unavailable'.");
                actualRoute = "unavailable";
                response = "Local RAG is required but not available right now.";
                timings = new Timings(localMs, 0);
            }
        }
        // 3) Intelligent routing based on complexity analysis
        else if (ShouldUseLocalFirst(queryAnalysis))
        {
            var (ragResult, localMs) = await TryLocalRagAsync(userQuery, ct);
            lastRag = ragResult;
            lastLocalMs = localMs;

            if (IsLocalAnswer(ragResult))
            {
                actualRoute = "local";
                response = ragResult!.Answer!;
                context = ragResult.ContextMap;
                timings = new Timings(localMs, 0);
            }
            else
            {
                _log.LogInformation("Local RAG failed, escalating to cloud (complexity: {Complexity})",
                    queryAnalysis.Complexity);

                var (cloudResult, cloudMs) = await TryCloudAsync(userQuery, ct);
                actualRoute = "cloud";
                response = cloudResult;
                context = ragResult?.ContextMap ?? Array.Empty<ContextItem>();
                timings = new Timings(localMs, cloudMs);
            }
        }
        // 4) Direct to cloud for complex queries
        else
        {
            _log.LogInformation("Routing directly to cloud based on complexity: {Complexity}",
                queryAnalysis.Complexity);

            var (cloudResult, cloudMs) = await TryCloudAsync(userQuery, ct);
            actualRoute = "cloud";
            response = cloudResult;
            timings = new Timings(0, cloudMs);
        }

        // 5) Evaluate response confidence
        var confidenceScore = await _confidenceScorer.EvaluateResponseAsync(
            userQuery, response, context, actualRoute, ct);

        _log.LogInformation("Response confidence: {Confidence:F2} ({Reasoning}) Escalate: {ShouldEscalate}",
            confidenceScore.OverallConfidence, confidenceScore.Reasoning, confidenceScore.ShouldEscalate);

        // 6) Confidence-based escalation
        if (confidenceScore.ShouldEscalate && actualRoute == "local" && !_flags.RagRequired)
        {
            _log.LogInformation("Low confidence response, escalating to cloud");

            var (cloudResult, cloudMs) = await TryCloudAsync(userQuery, ct);

            // Re-evaluate cloud response
            var cloudConfidence = await _confidenceScorer.EvaluateResponseAsync(
                userQuery, cloudResult, context, "cloud", ct);

            if (cloudConfidence.OverallConfidence > confidenceScore.OverallConfidence)
            {
                _log.LogInformation("Cloud escalation improved confidence: {OldConf:F2} -> {NewConf:F2}",
                    confidenceScore.OverallConfidence, cloudConfidence.OverallConfidence);

                return new AskResponse("cloud", cloudResult, context,
                    new Timings(lastLocalMs, cloudMs));
            }
            else
            {
                _log.LogInformation("Cloud escalation did not improve confidence, keeping local response");
            }
        }

        _log.LogInformation("Route={Route} localMs={Local} cloudMs={Cloud} confidence={Confidence:F2}",
            actualRoute, timings.LocalMs, timings.CloudMs, confidenceScore.OverallConfidence);

        return new AskResponse(actualRoute, response, context, timings);
    }

    private async Task<(RagAskResponse? ragResult, long elapsedMs)> TryLocalRagAsync(string userQuery, CancellationToken ct)
    {
        try
        {
            var sw = Stopwatch.StartNew();
            var result = await _rag.AskAsync(userQuery, ct);
            return (result, sw.ElapsedMilliseconds);
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Local RAG failed");
            return (null, 0);
        }
    }

    private async Task<(string response, long elapsedMs)> TryCloudAsync(string userQuery, CancellationToken ct)
    {
        try
        {
            var sw = Stopwatch.StartNew();
            var result = await _aoai.ChatAsync(
                system: "Answer concisely and accurately. If unsure, say 'I don't know'. Provide citations when possible.",
                user: userQuery,
                ct: ct);
            return (result, sw.ElapsedMilliseconds);
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Cloud AI failed");
            return ("Sorry, the cloud model is not reachable right now. Check Azure OpenAI endpoint/deployment configuration.", 0);
        }
    }

    private bool ShouldUseLocalFirst(QueryAnalysis analysis)
    {
        // Use legacy flag if enabled
        if (_flags.UseRagFirst) return true;

        // Intelligent routing logic
        return analysis.RecommendedRoute switch
        {
            "local" => true,
            "cloud" => false,
            "hybrid" => true, // Try local first for hybrid
            _ => true // Default to local first
        };
    }

    private static bool IsLocalAnswer(RagAskResponse? rr) =>
        rr is not null &&
        rr.Route.Equals("local", StringComparison.OrdinalIgnoreCase) &&
        !string.IsNullOrWhiteSpace(rr.Answer);
}
