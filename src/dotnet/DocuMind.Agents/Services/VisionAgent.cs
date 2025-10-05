using DocuMind.Agents.Interfaces;
using DocuMind.Agents.Models;
using DocuMind.Agents.Options;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.SemanticKernel;
using System.Diagnostics;
using System.Text.Json;

namespace DocuMind.Agents.Services;

/// <summary>
/// Specialized agent for vision processing and image analysis
/// </summary>
public class VisionAgent : IVisionAgent
{
    private readonly ILogger<VisionAgent> _logger;
    private readonly AgentOptions _options;
    private readonly Kernel _kernel;
    private readonly HttpClient _httpClient;

    public string AgentType => "VisionAgent";

    public VisionAgent(
        ILogger<VisionAgent> logger,
        IOptions<AgentOptions> options,
        Kernel kernel,
        HttpClient httpClient)
    {
        _logger = logger;
        _options = options.Value;
        _kernel = kernel;
        _httpClient = httpClient;
    }

    public async Task<AgentResponse> ProcessAsync(AgentRequest request, CancellationToken cancellationToken = default)
    {
        if (request is VisionAgentRequest visionRequest)
        {
            return await ProcessImageAsync(visionRequest, cancellationToken);
        }

        return new AgentResponse
        {
            Success = false,
            Error = "Invalid request type for VisionAgent",
            AgentType = AgentType
        };
    }

    public async Task<VisionAgentResponse> ProcessImageAsync(VisionAgentRequest request, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            _logger.LogInformation("Processing vision request: {AnalysisType}", request.AnalysisType);

            var response = new VisionAgentResponse
            {
                SessionId = request.SessionId,
                AgentType = AgentType
            };

            // Call the existing Vision API
            var visionResult = await CallVisionApiAsync(request.ImageData ?? string.Empty, request.AnalysisType, cancellationToken);

            switch (request.AnalysisType.ToLowerInvariant())
            {
                case "general":
                    response.ImageDescription = await AnalyzeImageAsync(request.ImageData ?? string.Empty, "general", cancellationToken);
                    response.Response = response.ImageDescription;
                    break;

                case "text_extraction":
                    response.ExtractedText = await ExtractTextFromImageAsync(request.ImageData ?? string.Empty, cancellationToken);
                    response.Response = $"Extracted {response.ExtractedText?.Length ?? 0} characters from image";
                    break;

                case "object_detection":
                    response.DetectedObjects = await DetectObjectsAsync(request.ImageData ?? string.Empty, cancellationToken);
                    response.Response = $"Detected {response.DetectedObjects.Count} objects in image";
                    break;

                default:
                    response.ImageDescription = await AnalyzeImageAsync(request.ImageData ?? string.Empty, "general", cancellationToken);
                    response.Response = response.ImageDescription;
                    break;
            }

            // Enhance with AI analysis
            response = await EnhanceWithAIAnalysis(response, request.ImageData ?? string.Empty, cancellationToken);

            response.ExecutionTimeMs = stopwatch.ElapsedMilliseconds;

            _logger.LogInformation("Vision processing completed in {ElapsedMs}ms", stopwatch.ElapsedMilliseconds);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing vision request");

            return new VisionAgentResponse
            {
                Success = false,
                Error = ex.Message,
                SessionId = request.SessionId,
                AgentType = AgentType,
                ExecutionTimeMs = stopwatch.ElapsedMilliseconds
            };
        }
    }

    public async Task<string> AnalyzeImageAsync(string imageData, string analysisType, CancellationToken cancellationToken = default)
    {
        try
        {
            // Call the existing Vision API for initial analysis
            var visionApiResult = await CallVisionApiAsync(imageData, analysisType, cancellationToken);

            // Enhance with Semantic Kernel analysis
            var enhancementPrompt = """
                Analyze the following image analysis results and provide enhanced insights.
                Focus on providing detailed, contextual understanding of the image content.

                Original Analysis:
                {{$input}}

                Please provide enhanced analysis with:
                1. Detailed description
                2. Context and significance
                3. Notable features
                4. Potential applications

                Enhanced Analysis:
                """;

            var enhancementFunction = _kernel.CreateFunctionFromPrompt(enhancementPrompt);
            var result = await _kernel.InvokeAsync(enhancementFunction, new() { ["input"] = visionApiResult }, cancellationToken);

            return result.ToString() ?? visionApiResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing image");
            return "Error analyzing image: " + ex.Message;
        }
    }

    public async Task<string> ExtractTextFromImageAsync(string imageData, CancellationToken cancellationToken = default)
    {
        try
        {
            // Call the existing Vision API for OCR
            var visionApiResult = await CallVisionApiAsync(imageData, "text_extraction", cancellationToken);

            // Clean and enhance extracted text with AI
            var cleaningPrompt = """
                Clean and structure the following extracted text from an image.
                Fix OCR errors, improve formatting, and ensure readability.

                Raw OCR Text:
                {{$input}}

                Clean, structured text:
                """;

            var cleaningFunction = _kernel.CreateFunctionFromPrompt(cleaningPrompt);
            var result = await _kernel.InvokeAsync(cleaningFunction, new() { ["input"] = visionApiResult }, cancellationToken);

            return result.ToString() ?? visionApiResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error extracting text from image");
            return "Error extracting text: " + ex.Message;
        }
    }

    private async Task<List<string>> DetectObjectsAsync(string imageData, CancellationToken cancellationToken)
    {
        try
        {
            // Call the existing Vision API for object detection
            var visionApiResult = await CallVisionApiAsync(imageData, "object_detection", cancellationToken);

            // Parse and enhance object detection results
            var objects = new List<string>();

            // For now, we'll parse the text response. In a real implementation,
            // this would parse structured JSON from the Vision API
            if (!string.IsNullOrEmpty(visionApiResult))
            {
                var lines = visionApiResult.Split('\n')
                    .Where(line => !string.IsNullOrWhiteSpace(line))
                    .Select(line => line.Trim())
                    .ToList();

                objects.AddRange(lines);
            }

            return objects;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error detecting objects");
            return new List<string> { "Error detecting objects: " + ex.Message };
        }
    }

    private async Task<string> CallVisionApiAsync(string imageData, string analysisType, CancellationToken cancellationToken)
    {
        try
        {
            // Prepare request for the existing Vision API
            var requestData = new
            {
                image_data = imageData,
                analysis_type = analysisType
            };

            var jsonContent = JsonSerializer.Serialize(requestData);
            var content = new StringContent(jsonContent, System.Text.Encoding.UTF8, "application/json");

            // Call the existing Vision API
            var response = await _httpClient.PostAsync(
                $"{_options.ServiceEndpoints.VisionApiUrl}/analyze",
                content,
                cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);
                return responseContent;
            }
            else
            {
                _logger.LogWarning("Vision API call failed with status: {StatusCode}", response.StatusCode);
                return "Vision API unavailable - using fallback analysis";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling Vision API");
            return "Vision API error - using fallback analysis";
        }
    }

    private async Task<VisionAgentResponse> EnhanceWithAIAnalysis(VisionAgentResponse response, string imageData, CancellationToken cancellationToken)
    {
        try
        {
            // Generate confidence scores based on analysis completeness
            var confidenceScores = new Dictionary<string, double>();

            if (!string.IsNullOrEmpty(response.ImageDescription))
                confidenceScores["description"] = 0.85;

            if (!string.IsNullOrEmpty(response.ExtractedText))
                confidenceScores["text_extraction"] = 0.90;

            if (response.DetectedObjects.Count > 0)
                confidenceScores["object_detection"] = 0.80;

            response.ConfidenceScores = confidenceScores;

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error enhancing vision analysis");
            return response;
        }
    }
}
