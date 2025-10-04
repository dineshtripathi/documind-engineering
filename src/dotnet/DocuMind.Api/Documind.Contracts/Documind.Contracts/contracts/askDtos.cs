namespace Documind.Contracts;

public sealed record AskRequest(string? Q, string? Prompt);
public sealed record AskResponse(string Route, string Answer, IReadOnlyList<ContextItem> ContextMap, Timings Timings);

//public sealed record ContextItem(int Index, string DocId, string ChunkId, double Score);
public sealed record Timings(long LocalMs, long CloudMs);
