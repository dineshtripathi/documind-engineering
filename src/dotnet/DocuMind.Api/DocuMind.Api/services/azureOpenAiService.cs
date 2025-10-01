using OpenAI;
using OpenAI.Chat;
using System.ClientModel;
using DocuMind.Api.Options;
using Microsoft.Extensions.Options;

namespace DocuMind.Api.Services;

public sealed class AzureOpenAiService : IAzureOpenAiService
{
    private readonly ChatClient _chat;
    private readonly string _endpoint;
    private readonly string _deployment;

    public AzureOpenAiService(IOptions<AzureOpenAiOptions> options, ILogger<AzureOpenAiService> log)
    {
        var o = options.Value;

        if (string.IsNullOrWhiteSpace(o.Endpoint))   throw new ArgumentNullException(nameof(o.Endpoint));
        if (string.IsNullOrWhiteSpace(o.Key))        throw new ArgumentNullException(nameof(o.Key));
        if (string.IsNullOrWhiteSpace(o.Deployment)) throw new ArgumentNullException(nameof(o.Deployment));

        // IMPORTANT: mimic your working code – ensure /openai/v1/ suffix
        _endpoint   = EnsureV1Suffix(o.Endpoint);
        _deployment = o.Deployment;

        log.LogInformation("AOAI init: endpoint={Endpoint} deployment={Deployment}", _endpoint, _deployment);

        // EXACTLY like your smoke test:
        _chat = new ChatClient(
            credential: new ApiKeyCredential(o.Key),
            model: _deployment,                  // deployment name e.g. "gpt-4o-mini"
            options: new OpenAIClientOptions
            {
                Endpoint = new Uri(_endpoint)    // e.g. https://.../openai/v1/
            });
    }

    public async Task<string> ChatAsync(string system, string user, CancellationToken ct = default, string? deployment = null)
    {
        var sys = string.IsNullOrWhiteSpace(system) ? "You are DocuMind, a helpful assistant." : system;

        ChatCompletion completion = await _chat.CompleteChatAsync(
            new ChatMessage[]
            {
                new SystemChatMessage(sys),
                new UserChatMessage(user)
            },
            cancellationToken: ct);

        return string.Concat(completion.Content.Select(p => p.Text));
    }

    private static string EnsureV1Suffix(string endpoint)
    {
        var e = endpoint.TrimEnd('/');
        // if already ends with /openai/v1, keep; else append
        if (e.EndsWith("/openai/v1", StringComparison.OrdinalIgnoreCase)) return e + "/";
        return e + "/openai/v1/";
    }
}
