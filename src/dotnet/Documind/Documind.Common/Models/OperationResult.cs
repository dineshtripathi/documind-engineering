namespace Documind.Common.Models;

/// <summary>
/// Represents the result of an operation with success/failure status
/// </summary>
public class OperationResult
{
    public bool IsSuccess { get; init; }
    public string? ErrorMessage { get; init; }
    public string? CorrelationId { get; init; }

    public static OperationResult Success(string? correlationId = null)
    {
        return new OperationResult { IsSuccess = true, CorrelationId = correlationId };
    }

    public static OperationResult Failure(string errorMessage, string? correlationId = null)
    {
        return new OperationResult
        {
            IsSuccess = false,
            ErrorMessage = errorMessage,
            CorrelationId = correlationId
        };
    }
}

/// <summary>
/// Represents the result of an operation with success/failure status and data
/// </summary>
public class OperationResult<T> : OperationResult
{
    public T? Data { get; init; }

    public static OperationResult<T> Success(T data, string? correlationId = null)
    {
        return new OperationResult<T>
        {
            IsSuccess = true,
            Data = data,
            CorrelationId = correlationId
        };
    }

    public static new OperationResult<T> Failure(string errorMessage, string? correlationId = null)
    {
        return new OperationResult<T>
        {
            IsSuccess = false,
            ErrorMessage = errorMessage,
            CorrelationId = correlationId
        };
    }
}
