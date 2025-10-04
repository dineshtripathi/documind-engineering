using System.ComponentModel.DataAnnotations;

namespace Documind.Vision.Models;

/// <summary>
/// Health check response model
/// </summary>
public class HealthResponse
{
    /// <summary>
    /// Service health status (ok, warn, error)
    /// </summary>
    /// <example>ok</example>
    public required string Status { get; set; }

    /// <summary>
    /// Service name
    /// </summary>
    /// <example>DocuMind.Vision</example>
    public required string Service { get; set; }

    /// <summary>
    /// Response timestamp
    /// </summary>
    /// <example>2025-10-04T10:30:00Z</example>
    public DateTime? Timestamp { get; set; }
}

/// <summary>
/// Error response model
/// </summary>
public class ErrorResponse
{
    /// <summary>
    /// Error message
    /// </summary>
    /// <example>url is required</example>
    public required string Message { get; set; }

    /// <summary>
    /// Optional correlation ID for tracking
    /// </summary>
    /// <example>12345678-1234-1234-1234-123456789abc</example>
    public string? CorrelationId { get; set; }
}
