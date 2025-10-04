using System.Net;
using System.Text.Json;

namespace DocuMind.Api.Middleware;

public sealed class ErrorHandlingMiddleware(RequestDelegate next, ILogger<ErrorHandlingMiddleware> logger)
{
    public async Task Invoke(HttpContext ctx)
    {
        try { await next(ctx); }
        catch (Exception ex)
        {
            logger.LogError(ex, "Unhandled exception");
            ctx.Response.StatusCode = (int)HttpStatusCode.InternalServerError;
            ctx.Response.ContentType = "application/json";
            var payload = new { title = "Unexpected error", status = ctx.Response.StatusCode, traceId = ctx.TraceIdentifier };
            await ctx.Response.WriteAsync(JsonSerializer.Serialize(payload));
        }
    }
}
