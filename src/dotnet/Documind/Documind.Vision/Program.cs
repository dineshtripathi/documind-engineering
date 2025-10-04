using Documind.Common.Constants;
using Documind.Vision.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new()
    {
        Title = "Documind Vision API",
        Version = AppConstants.ApiVersion,
        Description = "Document vision processing and OCR services using Azure AI Vision",
        Contact = new()
        {
            Name = "Documind Team",
            Email = "support@documind.ai"
        },
        License = new()
        {
            Name = "MIT License",
            Url = new Uri("https://opensource.org/licenses/MIT")
        }
    });

    // Include XML comments if available
    var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath))
    {
        c.IncludeXmlComments(xmlPath);
    }

    // Add schema filter for examples
    c.SchemaFilter<ExampleSchemaFilter>();
});

// Register vision services
builder.Services.AddHttpClient<AzureVisionClient>();
builder.Services.AddScoped<IVisionService, VisionService>();

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Documind Vision API v1");
        c.RoutePrefix = string.Empty; // Serve Swagger UI at root
    });
}

app.UseHttpsRedirection();
app.UseCors();
app.UseAuthorization();
app.MapControllers();

// Health check endpoint
app.MapGet("/healthz", () => new
{
    status = "healthy",
    service = "documind-vision",
    version = AppConstants.ApiVersion,
    timestamp = DateTime.UtcNow
});

app.Run();
