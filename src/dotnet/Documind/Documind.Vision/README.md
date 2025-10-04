# Documind.Vision WebAPI

A specialized WebAPI service for document vision processing, OCR, and image analysis within the DocuMind solution.

## 🚀 Features

### Vision Controller (`/vision`)
- **POST /vision/analyze** - Process images and extract text using OCR
- **GET /vision/health** - Health check endpoint

### Core Capabilities
- ✅ Image upload and validation
- ✅ OCR text extraction (placeholder implementation)
- ✅ Support for multiple image formats
- ✅ Correlation ID tracking
- ✅ Structured response with confidence scores

## 📁 Project Structure

```
Documind.Vision/
├── Controllers/
│   └── VisionController.cs         # Main vision processing endpoints
├── Properties/
│   └── launchSettings.json        # Launch configuration (port 7002)
├── Documind.Vision.csproj         # Project file
├── Documind.Vision.http           # HTTP test file
├── Program.cs                     # Application startup
├── appsettings.json               # Configuration
└── appsettings.Development.json   # Development settings
```

## 🔗 Dependencies

- **Documind.Common** - Shared utilities and constants
- **Documind.Contracts** - Shared DTOs and models
- **.NET 8 WebAPI** - Base framework

## 📡 API Endpoints

### POST /vision/analyze
Process an image file and extract text content.

**Request:**
```
Content-Type: multipart/form-data

- File: Image file (jpg, png, etc.)
- DocId: Optional document identifier
- Language: Optional language code (default: "en")
```

**Response:**
```json
{
  "isSuccess": true,
  "data": {
    "sourceId": "doc123",
    "sourceUri": "image.jpg",
    "sourceType": "image",
    "language": "en",
    "blocks": [
      {
        "page": 1,
        "text": "Extracted text content",
        "confidence": 0.95,
        "bbox": [0, 0, 100, 50],
        "order": 1
      }
    ],
    "captions": [],
    "tags": ["sample", "vision"],
    "ingestedAt": "2025-10-04T19:45:00Z"
  },
  "correlationId": "abc123def456"
}
```

### GET /vision/health
Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "vision",
  "timestamp": "2025-10-04T19:45:00Z"
}
```

### GET /healthz
Application health check (global endpoint).

## ⚙️ Configuration

### appsettings.json
```json
{
  "VisionSettings": {
    "MaxFileSizeMB": 10,
    "SupportedFormats": ["jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"],
    "ProcessingTimeoutSeconds": 30
  }
}
```

## 🛠️ Development

### Running the Service
```bash
# Build and run
cd /home/dinesh/documind-engineering/src/dotnet
dotnet run --project Documind/Documind.Vision/Documind.Vision.csproj

# Or use VS Code launch configuration
# F5 → Select ".NET Core Launch (Vision API)"
```

### Service URLs
- **Development**: http://localhost:7002
- **Swagger UI**: http://localhost:7002 (root path)
- **Health Check**: http://localhost:7002/healthz

### Testing
```bash
# Test health endpoint
curl http://localhost:7002/healthz

# Test vision analysis (with file upload)
curl -X POST http://localhost:7002/vision/analyze \
  -F "File=@path/to/image.jpg" \
  -F "DocId=test123" \
  -F "Language=en"
```

## 🔧 TODO / Future Enhancements

- [ ] Integrate actual OCR engine (Azure Computer Vision, Tesseract, etc.)
- [ ] Add support for PDF documents
- [ ] Implement batch processing
- [ ] Add image preprocessing (rotation, scaling, etc.)
- [ ] Add confidence threshold configuration
- [ ] Implement caching for processed documents
- [ ] Add metrics and monitoring
- [ ] Add authentication/authorization

## 🏗️ Architecture

The Vision API is designed as a microservice that can be deployed independently or alongside the main DocuMind.Api. It follows the same patterns and uses shared contracts for consistency.

**Service Communication:**
```
DocuMind.Api ←→ Documind.Vision
     ↓              ↓
Documind.Contracts (shared DTOs)
     ↓              ↓
Documind.Common (shared utilities)
```

---
*This service handles all document vision processing and OCR capabilities for the DocuMind solution.*
