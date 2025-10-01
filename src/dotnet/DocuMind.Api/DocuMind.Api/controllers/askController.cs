// Controllers/AskController.cs
using DocuMind.Api.Models;
using DocuMind.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace DocuMind.Api.Controllers;

[ApiController]
[Route("[controller]")]
public sealed class AskController(IAskOrchestrator orchestrator) : ControllerBase
{
    [HttpPost]
    [ProducesResponseType(typeof(AskResponse), StatusCodes.Status200OK)]
    public async Task<IActionResult> Post([FromBody] AskRequest req, CancellationToken ct)
    {
        var q = req.Q ?? req.Prompt;
        if (string.IsNullOrWhiteSpace(q)) return BadRequest("Provide 'q' or 'prompt'.");
        var resp = await orchestrator.AskAsync(q, ct);
        return Ok(resp);
    }

    [HttpGet]
    [ProducesResponseType(typeof(AskResponse), StatusCodes.Status200OK)]
    public async Task<IActionResult> Get([FromQuery] string? q, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(q)) return BadRequest("Missing 'q'.");
        var resp = await orchestrator.AskAsync(q, ct);
        return Ok(resp);
    }
}
