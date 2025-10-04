# Documind.Common Project

A shared library containing common utilities, constants, and models used across the DocuMind solution.

## 📁 Structure

```
Documind.Common/
├── Constants/
│   └── AppConstants.cs          # Application-wide constants
├── Extensions/
│   └── StringExtensions.cs      # String utility extensions
├── Models/
│   └── OperationResult.cs       # Result wrapper classes
└── Utilities/
    ├── CorrelationIdGenerator.cs # Correlation ID management
    └── JsonHelper.cs            # JSON serialization helpers
```

## 🚀 Features

### Constants
- **AppConstants**: Application name, API version, routes, headers, content types

### Extensions
- **StringExtensions**:
  - `IsNullOrWhiteSpace()` - Enhanced null/empty checking
  - `HasValue()` - Checks for actual content
  - `OrDefault()` - Provides fallback values
  - `Truncate()` - Safe string truncation

### Models
- **OperationResult**: Generic result wrapper for operations
- **OperationResult<T>**: Typed result wrapper with data

### Utilities
- **CorrelationIdGenerator**: Generate and validate correlation IDs
- **JsonHelper**: Simplified JSON serialization with consistent options

## 🔗 Usage

### In DocuMind.Api
```csharp
using Documind.Common.Constants;
using Documind.Common.Extensions;
using Documind.Common.Models;
using Documind.Common.Utilities;

// Use constants
var route = AppConstants.Routes.Ask;

// Use extensions
if (query.HasValue())
{
    // Process query
}

// Use operation results
return OperationResult<string>.Success(result, correlationId);

// Generate correlation IDs
var correlationId = CorrelationIdGenerator.Generate();
```

### In Documind.Contracts
```csharp
using Documind.Common.Extensions;

public record AskRequest(string? Q, string? Prompt)
{
    public string GetQuery() => Q.OrDefault(Prompt.OrDefault());
}
```

## 📦 Project References

- **Referenced by**: DocuMind.Api, Documind.Contracts
- **Dependencies**: None (only .NET 8 base libraries)

## 🛠️ Development

```bash
# Build the common library
dotnet build Documind/Documind.Common/Documind.Common.csproj

# Add reference to another project
dotnet add YourProject.csproj reference ../Documind.Common/Documind.Common.csproj
```

---
*This project provides a foundation for shared functionality across the DocuMind solution.*
