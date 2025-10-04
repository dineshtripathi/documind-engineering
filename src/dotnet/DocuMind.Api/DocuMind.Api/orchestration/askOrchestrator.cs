namespace DocuMind.Api.Orchestration;

using System.Diagnostics;
using DocuMind.Api.Clients;
using DocuMind.Api.Models;
using DocuMind.Api.Options;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using DocuMind.Api.Services;


public sealed class AskOrchestrator : IAskOrchestrator
{
    private readonly IRagClient _rag;
    private readonly IAzureOpenAiService _aoai;
    private readonly FeatureFlags _flags;
    private readonly ILogger<AskOrchestrator> _log;

    public AskOrchestrator(
        IRagClient rag,
        IAzureOpenAiService aoai,
        IOptions<FeatureFlags> flags,
        ILogger<AskOrchestrator> log)
    {
        _rag = rag;
        _aoai = aoai;
        _flags = flags.Value;
        _log = log;
    }

    public async Task<AskResponse> AskAsync(string userQuery, CancellationToken ct = default)
    {
        RagAskResponse? lastRag = null;
        long lastLocalMs = 0;

        // 1) Hard dependency: RAG required
        if (_flags.RagRequired)
        {
            var sw = Stopwatch.StartNew();
            var rr = await _rag.AskAsync(userQuery, ct);
            var localMs = sw.ElapsedMilliseconds;

            if (IsLocalAnswer(rr))
            {
                _log.LogInformation("Route=local localMs={Local}", localMs);
                return new AskResponse("local", rr!.Answer!, rr.ContextMap, new Timings(localMs, 0));
            }

            _log.LogInformation("RAG required but unavailable/abstained. Returning 'unavailable'.");
            return new AskResponse(
                "unavailable",
                "Local RAG is required but not available right now.",
                Array.Empty<ContextItem>(),
                new Timings(localMs, 0));
        }

        // 2) Soft dependency: try local first
        if (_flags.UseRagFirst)
        {
            var sw = Stopwatch.StartNew();
            lastRag = await _rag.AskAsync(userQuery, ct);
            lastLocalMs = sw.ElapsedMilliseconds;

            if (IsLocalAnswer(lastRag))
            {
                _log.LogInformation("Route=local localMs={Local}", lastLocalMs);
                return new AskResponse("local", lastRag!.Answer!, lastRag.ContextMap, new Timings(lastLocalMs, 0));
            }

            _log.LogInformation("Switchover → Azure OpenAI (RAG unavailable or abstained).");
        }

        // 3) Cloud fallback (always returns a body)
        try
        {
            var sw = Stopwatch.StartNew();
            var cloud = await _aoai.ChatAsync(
                system: "Answer concisely. If unsure, say 'I don't know'.",
                user: userQuery,
                ct: ct);
            var cloudMs = sw.ElapsedMilliseconds;

            _log.LogInformation("Route=cloud cloudMs={Cloud}", cloudMs);
            // Pass through any context we *did* retrieve locally (useful for UI tooltips)
            var ctx = lastRag?.ContextMap ?? Array.Empty<ContextItem>();
            return new AskResponse("cloud", cloud, ctx, new Timings(0, cloudMs));
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "AOAI fallback failed");
            return new AskResponse(
                "unavailable",
                "Sorry, the cloud model is not reachable right now. Check Azure OpenAI endpoint/deployment configuration.",
                Array.Empty<ContextItem>(),
                new Timings(0, 0));
        }
    }

    private static bool IsLocalAnswer(RagAskResponse? rr) =>
        rr is not null &&
        rr.Route.Equals("local", StringComparison.OrdinalIgnoreCase) &&
        !string.IsNullOrWhiteSpace(rr.Answer);
}
