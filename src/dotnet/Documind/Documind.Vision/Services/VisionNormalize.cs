using System.Text.Json;
using Documind.Contracts;

namespace Documind.Vision.Services;

public static class VisionNormalize
{

    public static TextBlocksDto ToTextBlocksDto(string providerJson, string sourceId, string sourceUri, string sourceType, string language)
    {
        using var doc = JsonDocument.Parse(providerJson);
        var root = doc.RootElement;

        var blocks = new List<TextBlock>();
        var captions = new List<Caption>();
        var tags = new List<string>();

        // captions
        if (Try(root, "captionResult", out var cap)) AddCap(cap);
        else if (Try(root, "caption", out var cap2)) AddCap(cap2);

        void AddCap(JsonElement e)
        {
            var txt = GetString(e, "text");
            var conf = GetFloat(e, "confidence");
            if (!string.IsNullOrWhiteSpace(txt))
                captions.Add(new Caption(
                    Page: 1,
                    Text: txt!,
                    Confidence: conf ?? 0.0f
                ));
        }

        // tags
        if (Try(root, "tagsResult", out var tr) && tr.TryGetProperty("values", out var vals) && vals.ValueKind == JsonValueKind.Array)
            foreach (var v in vals.EnumerateArray())
                if (GetString(v, "name") is { } n) tags.Add(n);
                else if (Try(root, "tags", out var ta) && ta.ValueKind == JsonValueKind.Array)
                    foreach (var tagElem in ta.EnumerateArray())
                        if (GetString(tagElem, "name") is { } tagName) tags.Add(tagName);

        // lines
        var order = 0;
        foreach (var prop in EnumerateAll(root))
        {
            if (!prop.NameEquals("lines") || prop.Value.ValueKind != JsonValueKind.Array) continue;
            foreach (var line in prop.Value.EnumerateArray())
            {
                var text = GetString(line, "content") ?? GetString(line, "text");
                if (string.IsNullOrWhiteSpace(text)) continue;

                float[]? bbox = null;
                if (line.TryGetProperty("boundingPolygon", out var poly) && poly.ValueKind == JsonValueKind.Array)
                {
                    var xs = new List<float>(); var ys = new List<float>();
                    foreach (var pt in poly.EnumerateArray())
                    {
                        if (pt.TryGetProperty("x", out var x) && pt.TryGetProperty("y", out var y)
                            && x.TryGetDouble(out var xd) && y.TryGetDouble(out var yd))
                        { xs.Add((float)xd); ys.Add((float)yd); }
                    }
                    if (xs.Count > 0 && ys.Count > 0) bbox = new[] { xs.Min(), ys.Min(), xs.Max(), ys.Max() };
                }

                blocks.Add(new TextBlock(
                    Page: 1,
                    Text: text!,
                    Confidence: GetFloat(line, "confidence") ?? 0.0f,
                    Bbox: bbox,
                    Order: order++
                ));
            }
        }

        return new TextBlocksDto(
            SourceId: sourceId,
            SourceUri: sourceUri,
            SourceType: sourceType,
            Language: language,
            Blocks: blocks,
            Captions: captions,
            Tags: tags.Distinct().ToList(),
            IngestedAt: DateTimeOffset.UtcNow
        );

        // helpers
        static bool Try(JsonElement e, string name, out JsonElement found)
        {
            if (e.ValueKind == JsonValueKind.Object && e.TryGetProperty(name, out found)) return true;
            foreach (var p in EnumerateAll(e)) if (p.NameEquals(name)) { found = p.Value; return true; }
            found = default; return false;
        }

        static IEnumerable<JsonProperty> EnumerateAll(JsonElement e)
        {
            var st = new Stack<JsonElement>(); st.Push(e);
            while (st.Count > 0)
            {
                var cur = st.Pop();
                if (cur.ValueKind == JsonValueKind.Object)
                    foreach (var p in cur.EnumerateObject()) { yield return p; st.Push(p.Value); }
                else if (cur.ValueKind == JsonValueKind.Array)
                    foreach (var a in cur.EnumerateArray()) st.Push(a);
            }
        }

        static string? GetString(JsonElement e, string n) =>
            e.ValueKind == JsonValueKind.Object && e.TryGetProperty(n, out var v) ? v.GetString() : null;

        static float? GetFloat(JsonElement e, string n)
        {
            if (e.ValueKind != JsonValueKind.Object || !e.TryGetProperty(n, out var v)) return null;
            return v.ValueKind == JsonValueKind.Number && v.TryGetDouble(out var d) ? (float)d
                 : v.ValueKind == JsonValueKind.String && float.TryParse(v.GetString(), out var f) ? f : null;
        }
    }
}
