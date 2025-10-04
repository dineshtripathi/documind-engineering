namespace Documind.Contracts;

public sealed record RagAskResponse(string Route, string Answer, IReadOnlyList<ContextItem> ContextMap);
