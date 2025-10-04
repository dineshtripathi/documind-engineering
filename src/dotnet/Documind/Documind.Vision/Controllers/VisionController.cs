using System.Security.Cryptography;
using System.Text;
using Documind.Contracts;
using Documind.Common.Extensions;
using Documind.Common.Models;
using Documind.Common.Utilities;
using Documind.Vision.Services;
using Documind.Vision.Models;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Http;

namespace Documind.Vision.Controllers;

/// <summary>
/// Vision processing controller for document OCR and image analysis using Azure AI Vision
/// </summary>
[ApiController]
[Route("vision")]
[Produces("application/json")]
public sealed class VisionController : ControllerBase
{
    private readonly IVisionService _visionService;
    private readonly ILogger<VisionController> _logger;

    public VisionController(IVisionService visionService, ILogger<VisionController> logger)
    {
        _visionService = visionService;
        _logger = logger;
    }

    /// <summary>
    /// Request model for URL-based image analysis
    /// </summary>
    /// <param name="Url">The public URL of the image to analyze</param>
    /// <param name="Language">Optional language code for OCR (e.g., 'en', 'es', 'fr')</param>
    /// <param name="Features">Optional array of features to extract (Read, Caption, Tags)</param>
    public sealed record AnalyzeUrlRequest(
        [Required] string Url,
        string? Language = null,
        string[]? Features = null
    );

    /// <summary>
    /// Health check endpoint for the Vision service
    /// </summary>
    /// <returns>Service health status and configuration validation</returns>
    /// <response code="200">Service is healthy and properly configured</response>
    [HttpGet("healthz")]
    [ProducesResponseType(typeof(HealthResponse), StatusCodes.Status200OK)]
    [Produces("application/json")]
    public IActionResult Healthz()
    {
        var ok = !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("AZURE_VISION_ENDPOINT"))
              && !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("AZURE_VISION_KEY"));

        var response = new HealthResponse
        {
            Status = ok ? "ok" : "warn",
            Service = "DocuMind.Vision",
            Timestamp = DateTime.UtcNow
        };

        return Ok(response);
    }
    /// <summary>
    /// Analyzes an image from a URL using Azure AI Vision for OCR and content extraction
    /// </summary>
    /// <param name="req">The analysis request containing the image URL and options</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>Extracted text blocks, captions, and metadata from the image</returns>
    /// <response code="200">Analysis completed successfully</response>
    /// <response code="400">Invalid request parameters</response>
    /// <response code="500">Internal server error during analysis</response>
    [HttpPost("analyze")]
    [Consumes("application/json")]
    [ProducesResponseType(typeof(OperationResult<TextBlocksDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(OperationResult<TextBlocksDto>), StatusCodes.Status500InternalServerError)]
    [Produces("application/json")]
    public async Task<IActionResult> Analyze([FromBody] AnalyzeUrlRequest req, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(req.Url))
        {
            return BadRequest(new ErrorResponse
            {
                Message = "url is required",
                CorrelationId = CorrelationIdGenerator.Generate()
            });
        }

        var correlationId = CorrelationIdGenerator.Generate();

        try
        {
            _logger.LogInformation("Processing URL: {Url}, Language: {Language}, CorrelationId: {CorrelationId}",
                req.Url, req.Language, correlationId);

            var result = await _visionService.AnalyzeUrlAsync(req.Url, req.Language, req.Features, ct);
            var sourceId = SourceId(req.Url);

            return Ok(OperationResult<TextBlocksDto>.Success(result, correlationId));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing URL analysis. CorrelationId: {CorrelationId}", correlationId);
            return StatusCode(500, OperationResult<TextBlocksDto>.Failure(
                "Internal server error during URL analysis", correlationId));
        }
    }

    /// <summary>
    /// Analyzes an uploaded image or PDF file using Azure AI Vision for OCR and content extraction
    /// </summary>
    /// <param name="file">The image or PDF file to analyze (max 25MB)</param>
    /// <param name="language">Optional language code for OCR (e.g., 'en', 'es', 'fr')</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>Extracted text blocks, captions, and metadata from the uploaded file</returns>
    /// <response code="200">File analysis completed successfully</response>
    /// <response code="400">Invalid file or missing file</response>
    /// <response code="500">Internal server error during file analysis</response>
    [HttpPost("analyze-file")]
    [RequestSizeLimit(25_000_000)]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(OperationResult<TextBlocksDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(OperationResult<TextBlocksDto>), StatusCodes.Status500InternalServerError)]
    [Produces("application/json")]
    public async Task<IActionResult> AnalyzeFile([FromForm] IFormFile file, [FromQuery] string? language, CancellationToken ct)
    {
        if (file is null || file.Length == 0)
        {
            return BadRequest(new ErrorResponse
            {
                Message = "file is required",
                CorrelationId = CorrelationIdGenerator.Generate()
            });
        }

        var correlationId = CorrelationIdGenerator.Generate();

        try
        {
            _logger.LogInformation("Processing file: {FileName}, Size: {Size} bytes, Type: {Type}, CorrelationId: {CorrelationId}",
                file.FileName, file.Length, GuessType(file.FileName), correlationId);

            await using var stream = file.OpenReadStream();
            var result = await _visionService.AnalyzeFileAsync(stream, file.FileName, language, ct);

            return Ok(OperationResult<TextBlocksDto>.Success(result, correlationId));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing file analysis. CorrelationId: {CorrelationId}", correlationId);
            return StatusCode(500, OperationResult<TextBlocksDto>.Failure(
                "Internal server error during file analysis", correlationId));
        }
    }
    /// <summary>
    /// Simple health check endpoint
    /// </summary>
    /// <returns>Basic service health information</returns>
    /// <response code="200">Service is running</response>
    [HttpGet("health")]
    [ProducesResponseType(typeof(HealthResponse), StatusCodes.Status200OK)]
    [Produces("application/json")]
    public IActionResult Health()
    {
        var response = new HealthResponse
        {
            Status = "healthy",
            Service = "vision",
            Timestamp = DateTime.UtcNow
        };

        return Ok(response);
    }

    static string GuessType(string name) => name.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase) ? "pdf" : "image";

    static string SourceId(string seed) =>
        "src-" + Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(seed))).ToLowerInvariant()[..12];
}
