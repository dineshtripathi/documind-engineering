using System.Net.Http.Json;
using System.Text.Json;

namespace DocuMind.Api.Services;

public sealed class OllamaClient
{
    private readonly HttpClient _http;
    public OllamaClient(HttpClient http) => _http = http;

    public async Task<string> GenerateAsync(string model, string prompt, float temperature = 0.1f)
    {
        var payload = new
        {
            model,
            prompt,
            stream = false,
            options = new { temperature }
        };

        using var r = await _http.PostAsJsonAsync("/api/generate", payload);
        if (r.IsSuccessStatusCode)
        {
            using var doc = JsonDocument.Parse(await r.Content.ReadAsStringAsync());
            if (doc.RootElement.TryGetProperty("response", out var resp))
                return resp.GetString() ?? "";
        }

        // fallback to /api/chat
        var chat = new
        {
            model,
            stream = false,
            messages = new[] { new { role = "user", content = prompt } },
            options = new { temperature }
        };
        using var rc = await _http.PostAsJsonAsync("/api/chat", chat);
        rc.EnsureSuccessStatusCode();
        var s = await rc.Content.ReadAsStringAsync();
        using var d2 = JsonDocument.Parse(s);
        if (d2.RootElement.TryGetProperty("message", out var msg) &&
            msg.TryGetProperty("content", out var content))
            return content.GetString() ?? "";
        return "";
    }
}
