namespace Documind.Contracts;

//public sealed record ContextItem(int Index, string DocId, string ChunkId, double Score);
public sealed record Timings(long LocalMs, long CloudMs);
