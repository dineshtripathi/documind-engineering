namespace Documind.Contracts;

public sealed record AskResponse(string Route, string Answer, IReadOnlyList<ContextItem> ContextMap, Timings Timings);
