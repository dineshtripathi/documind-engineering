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

    public IngestController(IRagClient rag, ILogger<IngestController> log)
    {
        _rag = rag;
        _log = log;
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
}

