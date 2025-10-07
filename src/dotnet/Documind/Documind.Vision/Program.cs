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
// builder.Services.AddEndpointsApiExplorer(); // Temporarily disabled for .NET 10 compatibility
// builder.Services.AddSwaggerGen(); // Temporarily disabled for .NET 10 compatibility

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
// app.UseSwagger(); // Temporarily disabled for .NET 10 compatibility
// app.UseSwaggerUI(); // Temporarily disabled for .NET 10 compatibility

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
