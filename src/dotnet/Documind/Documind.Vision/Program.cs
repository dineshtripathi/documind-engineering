using Documind.Common.Constants;
using Documind.Vision.Services;
using Documind.Vision.Options;
using Documind.Vision.Filters;

var builder = WebApplication.CreateBuilder(args);

// Configuration
builder.Services.Configure<VisionOptions>(builder.Configuration.GetSection(VisionOptions.Section));
builder.Services.Configure<AzureVisionOptions>(builder.Configuration.GetSection(AzureVisionOptions.Section));

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

    // Support for file uploads
    // c.OperationFilter<FileUploadOperationFilter>();
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
app.UseSwagger();
app.UseSwaggerUI();

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
