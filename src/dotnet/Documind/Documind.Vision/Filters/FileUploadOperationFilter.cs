using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;
using System.Reflection;

namespace Documind.Vision.Filters;

/// <summary>
/// Operation filter to properly handle file upload endpoints in Swagger documentation
/// </summary>
public class FileUploadOperationFilter : IOperationFilter
{
    public void Apply(OpenApiOperation operation, OperationFilterContext context)
    {
        // Check if this operation consumes multipart/form-data
        var hasFileUpload = context.ApiDescription.ActionDescriptor.EndpointMetadata
            .OfType<Microsoft.AspNetCore.Mvc.ConsumesAttribute>()
            .Any(attr => attr.ContentTypes.Contains("multipart/form-data"));

        if (!hasFileUpload) return;

        // Find parameters with IFormFile
        var fileParameters = context.MethodInfo.GetParameters()
            .Where(p =>
                p.ParameterType == typeof(IFormFile) ||
                p.ParameterType == typeof(IFormFileCollection) ||
                p.ParameterType == typeof(IEnumerable<IFormFile>) ||
                HasFormFileProperty(p.ParameterType))
            .ToArray();

        if (!fileParameters.Any()) return;

        operation.RequestBody = new OpenApiRequestBody
        {
            Content = new Dictionary<string, OpenApiMediaType>
            {
                ["multipart/form-data"] = new OpenApiMediaType
                {
                    Schema = new OpenApiSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, OpenApiSchema>()
                    }
                }
            }
        };

        var schema = operation.RequestBody.Content["multipart/form-data"].Schema;

        // Handle form models with IFormFile properties
        foreach (var param in fileParameters)
        {
            if (param.ParameterType == typeof(IFormFile))
            {
                schema.Properties[param.Name!] = new OpenApiSchema
                {
                    Type = "string",
                    Format = "binary"
                };
            }
            else if (HasFormFileProperty(param.ParameterType))
            {
                // Handle complex form models
                var properties = param.ParameterType.GetProperties();
                foreach (var prop in properties)
                {
                    if (prop.PropertyType == typeof(IFormFile))
                    {
                        schema.Properties[prop.Name] = new OpenApiSchema
                        {
                            Type = "string",
                            Format = "binary"
                        };
                    }
                    else if (prop.PropertyType == typeof(string))
                    {
                        schema.Properties[prop.Name] = new OpenApiSchema
                        {
                            Type = "string",
                            Description = $"Optional {prop.Name.ToLower()} parameter"
                        };
                    }
                }
            }
        }
    }

    private static bool HasFormFileProperty(Type type)
    {
        return type.GetProperties()
            .Any(p => p.PropertyType == typeof(IFormFile) ||
                     p.PropertyType == typeof(IFormFileCollection) ||
                     p.PropertyType == typeof(IEnumerable<IFormFile>));
    }
}
