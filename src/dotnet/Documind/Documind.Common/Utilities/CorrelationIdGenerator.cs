namespace Documind.Common.Utilities;

/// <summary>
/// Utility class for generating and managing correlation IDs
/// </summary>
public static class CorrelationIdGenerator
{
    /// <summary>
    /// Generates a new correlation ID
    /// </summary>
    public static string Generate()
    {
        return Guid.NewGuid().ToString("N")[..12]; // Short 12-character ID
    }

    /// <summary>
    /// Validates if a correlation ID is in the expected format
    /// </summary>
    public static bool IsValid(string? correlationId)
    {
        return !string.IsNullOrWhiteSpace(correlationId) &&
               correlationId.Length >= 8 &&
               correlationId.Length <= 36;
    }
}
