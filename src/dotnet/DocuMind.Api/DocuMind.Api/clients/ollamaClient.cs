using System.Net.Http.Json;
using System.Text.Json;
using DocuMind.Api.Options;
using DocuMind.Api.Models;
using Microsoft.Extensions.Options;

namespace DocuMind.Api.Clients;

public sealed class OllamaClient : IOllamaClient
{
    private static readonly JsonSerializerOptions JsonOpts = new(JsonSerializerDefaults.Web) { PropertyNameCaseInsensitive = true };
    private readonly HttpClient _http;
    private readonly OllamaOptions _opt;

    public OllamaClient(HttpClient http, IOptions<OllamaOptions> options)
    {
        _http = http;
        _opt = options.Value;
        _http.Timeout = TimeSpan.FromSeconds(_opt.TimeoutSeconds);
    }

    public async Task<string> GenerateAsync(string prompt, string? modelOverride = null, double? temperature = null, CancellationToken ct = default)
    {
        var payload = new
        {
            model = modelOverride ?? _opt.Model, prompt, stream = false,
            options = new { temperature = temperature ?? _opt.Temperature }
        };

        using var resp = await _http.PostAsJsonAsync("/api/generate", payload, ct);
        if (resp.IsSuccessStatusCode)
        {
            var gen = await resp.Content.ReadFromJsonAsync<OllamaGenerateResponse>(JsonOpts, ct);
            if (!string.IsNullOrWhiteSpace(gen?.Response)) return gen!.Response!;
        }
        return await ChatAsync(prompt, null, modelOverride, temperature, ct);
    }

    public async Task<string> ChatAsync(string user, string? system = null, string? modelOverride = null, double? temperature = null, CancellationToken ct = default)
    {
        var messages = new List<object>();
        if (!string.IsNullOrWhiteSpace(system)) messages.Add(new { role = "system", content = system });
        messages.Add(new { role = "user", content = user });

        var payload = new
        {
            model = modelOverride ?? _opt.Model, stream = false, messages,
            options = new { temperature = temperature ?? _opt.Temperature }
        };

        using var resp = await _http.PostAsJsonAsync("/api/chat", payload, ct);
        resp.EnsureSuccessStatusCode();
        var chat = await resp.Content.ReadFromJsonAsync<OllamaChatResponse>(JsonOpts, ct);
        return chat?.Message?.Content ?? string.Empty;
    }
}
