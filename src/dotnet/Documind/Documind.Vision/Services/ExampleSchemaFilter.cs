using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;
using System.ComponentModel;

namespace Documind.Vision.Services;

/// <summary>
/// Schema filter to add examples to Swagger documentation
/// </summary>
public class ExampleSchemaFilter : ISchemaFilter
{
    public void Apply(OpenApiSchema schema, SchemaFilterContext context)
    {
        if (context.Type == typeof(string) && context.MemberInfo?.Name == "Url")
        {
            schema.Example = new Microsoft.OpenApi.Any.OpenApiString("https://example.com/image.jpg");
        }
        else if (context.Type == typeof(string) && context.MemberInfo?.Name == "Language")
        {
            schema.Example = new Microsoft.OpenApi.Any.OpenApiString("en");
        }
        else if (context.Type == typeof(string[]) && context.MemberInfo?.Name == "Features")
        {
            schema.Example = new Microsoft.OpenApi.Any.OpenApiArray
            {
                new Microsoft.OpenApi.Any.OpenApiString("Read"),
                new Microsoft.OpenApi.Any.OpenApiString("Caption"),
                new Microsoft.OpenApi.Any.OpenApiString("Tags")
            };
        }
    }
}
