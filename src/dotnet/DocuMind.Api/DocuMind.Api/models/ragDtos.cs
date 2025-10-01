namespace DocuMind.Api.Models;
public sealed record RagAskResponse(string Route, string? Answer, IReadOnlyList<ContextItem> ContextMap, Timings Timings);
