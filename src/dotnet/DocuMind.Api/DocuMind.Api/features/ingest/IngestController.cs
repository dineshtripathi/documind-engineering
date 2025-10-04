using Documind.Contracts;
using DocuMind.Api.Clients;     // <-- DTOs & IRagClient live here per our earlier code
using Microsoft.AspNetCore.Mvc;


namespace DocuMind.Api.Controllers;

[ApiController]
[Route("ingest")]
public sealed class IngestController : ControllerBase
{
    private readonly IRagClient _rag;
    private readonly ILogger<IngestController> _log;
    private readonly IVisionClient _vision;

    public IngestController(IRagClient rag, IVisionClient vision, ILogger<IngestController> log)
    {
        _rag = rag;
        _log = log;
        _vision = vision;
    }

    [HttpPost("text")]
    public async Task<IActionResult> Text([FromBody] IngestTextRequest req, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(req.DocId) || string.IsNullOrWhiteSpace(req.Text))
            return BadRequest("docId and text are required");

        var ok = await _rag.IngestTextAsync(req, ct);
        return Ok(new { ok, req.DocId });
    }

    [HttpPost("url")]
    public async Task<IActionResult> IngestUrl([FromBody] IngestUrlRequest req, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(req.Url))
            return BadRequest("url is required");

        var ok = await _rag.IngestUrlAsync(req, ct);
        return Ok(new { ok, req.Url, req.DocId });
    }

    [HttpPost("blob")]
    public async Task<IActionResult> Blob([FromBody] IngestBlobRequest req, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(req.DocId) || string.IsNullOrWhiteSpace(req.BlobUrl))
            return BadRequest("docId and blobUrl are required");
        if (req.BlobUrl.Contains("sr=c") && string.IsNullOrWhiteSpace(req.BlobName))
            return BadRequest("blobName is required when using a container SAS (sr=c)");

        var ok = await _rag.IngestBlobAsync(req, ct);
        return Ok(new { ok, req.DocId, req.BlobUrl, req.BlobName });
    }

    // ✅ FIXED: use a single [FromForm] DTO and mark the action as multipart
    [HttpPost("upload")]
    [Consumes("multipart/form-data")]
    [RequestSizeLimit(100_000_000)]
    public async Task<IActionResult> Upload([FromForm] UploadIngestForm form, CancellationToken ct)
    {
        if (form.File is null || form.File.Length == 0)
            return BadRequest("file is required");

        var ok = await _rag.UploadAsync(form.File, form.DocId, ct);
        return Ok(new { ok, docId = form.DocId ?? form.File.FileName });
    }

    [HttpPost("vision-url")]
    public async Task<IActionResult> VisionUrl([FromBody] IngestUrlRequest req, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(req.Url))
            return BadRequest("url is required");

        // 1) Vision OCR / analyze
        TextBlocksDto dto = await _vision.AnalyzeUrlAsync(req.Url, req.Language ?? "en", req.Features, ct);

        // 2) Index to RAG
        var batchId = await _rag.IndexBlocksAsync(dto, ct);
        return Ok(new { ok = true, batchId, items = dto.Blocks.Count, req.Url });
    }

    [HttpPost("vision-file")]
    [Consumes("multipart/form-data")]
    [RequestSizeLimit(100_000_000)]
    public async Task<IActionResult> VisionFile([FromForm] UploadIngestForm form, CancellationToken ct)
    {
        if (form.File is null || form.File.Length == 0)
            return BadRequest("file is required");

        await using var s = form.File.OpenReadStream();

        // 1) Vision OCR / analyze
        TextBlocksDto dto = await _vision.AnalyzeFileAsync(s, form.File.FileName, form.Language ?? "en", ct);

        // 2) Index to RAG
        var batchId = await _rag.IndexBlocksAsync(dto, ct);
        return Ok(new { ok = true, batchId, items = dto.Blocks.Count, docId = form.DocId ?? form.File.FileName });
    }
}

