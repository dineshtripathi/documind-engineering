namespace Documind.Common.Constants;

/// <summary>
/// Application-wide constants
/// </summary>
public static class AppConstants
{
    public const string ApplicationName = "DocuMind";
    public const string ApiVersion = "v1";

    public static class Routes
    {
        public const string HealthCheck = "/healthz";
        public const string Ask = "/ask";
        public const string Ingest = "/ingest";
        public const string Search = "/search";
    }

    public static class Headers
    {
        public const string CorrelationId = "X-Correlation-ID";
        public const string RequestId = "X-Request-ID";
        public const string UserAgent = "User-Agent";
    }

    public static class ContentTypes
    {
        public const string Json = "application/json";
        public const string FormData = "multipart/form-data";
        public const string PlainText = "text/plain";
    }
}
