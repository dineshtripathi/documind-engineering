using OpenAI;
using OpenAI.Chat;
using System.ClientModel;

namespace DocuMind.Api.Services;

public sealed class AzureOpenAiService
{
    private readonly ChatClient _chat;

    public AzureOpenAiService(IConfiguration cfg)
    {
        var endpoint = cfg["AzureOpenAI:Endpoint"]!;   // must be .../openai/v1/
        var apiKey = cfg["AzureOpenAI:Key"]!;
        var deployment = cfg["AzureOpenAI:Deployment"] ?? "gpt-4o-mini";

        _chat = new ChatClient(
            credential: new ApiKeyCredential(apiKey),
            model: deployment,
            options: new OpenAIClientOptions
            {
                Endpoint = new Uri(endpoint)
            });
    }

    public async Task<string> ChatAsync(string deployment, string system, string prompt)
    {
        ChatCompletion completion = await _chat.CompleteChatAsync(
            new ChatMessage[]
            {
            new SystemChatMessage(system ?? "You are DocuMind, a helpful assistant."),
            new UserChatMessage(prompt)
            });

        return string.Concat(completion.Content.Select(p => p.Text));
    }

}