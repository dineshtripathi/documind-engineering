# DocuMind Engineering

## Overview

DocuMind is a hybrid AI orchestration platform that combines local LLMs with cloud AI services for intelligent document processing and retrieval. The system integrates .NET 8 APIs with Python-based AI services to provide scalable, enterprise-ready AI capabilities.

## Architecture

### System Components

**Frontend Layer**
- Web UI, API Tests, REST clients
- Swagger UI for API documentation

**.NET API Layer (Port 5266)**
- `DocuMind.Api` - Main orchestration service
- `Documind.Vision` - Azure AI Vision integration
- Enhanced AskOrchestrator with intelligent query routing
- Swagger/OpenAPI documentation

**Python AI Layer (Port 7001)**
- RAG API (FastAPI) with GPU acceleration
- BAAI/bge-m3 embeddings (1024-dimensional)
- Jina v1-turbo reranking (cross-encoder)
- Local LLM processing

**Storage & AI Services**
- Qdrant Vector Database (Port 6333)
- Ollama (Phi-3.5 3.8B) for local inference
- Azure OpenAI (GPT-4o-mini) for complex queries

### Query Processing

1. **Query Analysis** - Complexity, domain, and intent classification
2. **Intelligent Routing** - Local vs cloud decision based on analysis
3. **RAG Processing** - Vector search, reranking, context assembly
4. **Response Generation** - LLM inference with confidence scoring
5. **Quality Assessment** - Citation validation and hallucination detection

## Technology Stack
## Technology Stack

### Backend Services

- **.NET 8 / ASP.NET Core**: Main API orchestrator with Swagger documentation
- **Python 3.11 / FastAPI**: RAG processing and AI model inference
- **Docker**: Containerized Qdrant vector database

### AI & ML

- **Local LLM**: Ollama Phi-3.5 3.8B (CUDA acceleration)
- **Cloud LLM**: Azure OpenAI GPT-4o-mini
- **Embeddings**: BAAI/bge-m3 (1024-dimensional)
- **Reranking**: Jina reranker v1-turbo-en
- **Vision**: Azure AI Vision for OCR and image analysis

### Database & Storage

- **Vector Database**: Qdrant (cosine similarity, persistent storage)
- **Document Storage**: Local file system with staging support

## Installation & Setup

### Prerequisites

- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows WSL2
- **Hardware**: 8GB RAM minimum, 16GB recommended
- **GPU**: NVIDIA RTX 20xx+ with 8GB+ VRAM (optional, for acceleration)
- **Disk Space**: 10GB free space minimum

### Quick Installation

```bash
# Clone repository
git clone <repository-url> documind-engineering
cd documind-engineering

# Run universal setup (installs all dependencies)
chmod +x scripts/setup.sh && ./scripts/setup.sh

# Start all services
./scripts/start.sh
```

### Manual Installation

#### 1. System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential git curl wget unzip jq \
    software-properties-common apt-transport-https ca-certificates
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git curl wget jq
```

#### 2. Docker Installation

**Linux:**
```bash
# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 3. .NET 8 SDK

```bash
# Ubuntu
wget -q https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0

# macOS
brew install --cask dotnet
```

#### 4. Python Environment

**Option A: Conda (Recommended)**
```bash
# Install Miniconda
curl -fsSLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p $HOME/miniconda3
eval "$($HOME/miniconda3/bin/conda shell.bash hook)"

# Create environment
conda env create -f src/python/environment.yml
conda activate documind
```

**Option B: Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r src/python/requirements.txt
```

#### 5. GPU Support (Optional)

For NVIDIA GPU acceleration:
```bash
# Install CUDA PyTorch
conda activate documind
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Verify GPU setup
./scripts/dev/setup-cuda.sh
```

#### 6. Ollama Installation

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download models
ollama pull phi3.5:3.8b-mini-instruct-q4_0
```

## Running the Application

### Start All Services

```bash
# Background mode (recommended)
./scripts/start.sh --background

# Foreground mode (with logs)
./scripts/start.sh
```

### Individual Services

**Start Qdrant only:**
```bash
./scripts/dev-up.sh
```

**Start Python RAG API only:**
```bash
./scripts/run-rag-api.sh
```

**Start .NET API only:**
```bash
cd src/dotnet/DocuMind.Api/DocuMind.Api
dotnet run
```

### Verify Installation

```bash
# Quick health check
./scripts/dev/quick-test.sh

# Comprehensive tests
./scripts/dev/test.sh

# Manual checks
curl http://localhost:6333/        # Qdrant
curl http://localhost:7001/healthz # Python RAG API
curl http://localhost:5266/healthz # .NET API
```

## API Documentation

### Swagger/OpenAPI

**Interactive Documentation**:
- **Swagger UI**: http://localhost:5266/swagger
- **OpenAPI JSON**: http://localhost:5266/swagger/v1/swagger.json

**Main API Endpoints**:

**DocuMind API (Port 5266)**:
- `GET /healthz` - Service health check
- `POST /ask` - Query processing with intelligent routing
- `POST /ask/complex` - Force cloud AI processing
- `POST /ingest` - Document ingestion and indexing

**Vision API (Port 5266/vision)**:
- `POST /vision/analyze` - Image analysis from URL
- `POST /vision/analyze-file` - File upload processing
- `GET /vision/healthz` - Vision service health

**Python RAG API (Port 7001)**:
- `GET /healthz` - RAG service health
- `POST /search` - Vector similarity search
- `POST /ask` - RAG query processing

### Response Format

All APIs return standardized responses:

```json
{
  "success": true,
  "data": { ... },
  "correlationId": "uuid",
  "timestamp": "2025-10-05T10:30:00Z"
}
```

**Error responses**:
```json
{
  "success": false,
  "message": "Error description",
  "correlationId": "uuid",
  "details": { ... }
}
```

## API Usage

### Service Endpoints

- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Python RAG API**: http://localhost:7001
- **.NET DocuMind API**: http://localhost:5266
- **Swagger Documentation**: http://localhost:5266/swagger

### Basic API Calls

**Simple Query:**
```bash
curl "http://localhost:5266/ask?q=What%20is%20the%20backup%20policy?"
```

**Complex Analysis:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"q": "Analyze the security implications of our DR strategy"}' \
  http://localhost:5266/ask
```

**Vision Analysis:**
```bash
curl -X POST -H "Content-Type: multipart/form-data" \
  -F "image=@/path/to/image.jpg" \
  http://localhost:5266/vision/analyze
```

### Response Format

```json
{
  "route": "local|cloud",
  "answer": "Response text with citations [1][2]",
  "contextMap": [
    {
      "index": 1,
      "doc_id": "document.pdf",
      "chunk_id": "123456789",
      "score": 0.85
    }
  ],
  "timings": {
    "localMs": 1250,
    "cloudMs": 0
  }
}
```

## Configuration

### Environment Variables

Create `.env` file in project root:
```bash
# Service URLs
QDRANT_URL=http://127.0.0.1:6333
RAG_API_URL=http://127.0.0.1:7001
DOTNET_API_URL=http://127.0.0.1:5266

# Model Configuration
OLLAMA_MODEL=phi3.5:3.8b-mini-instruct-q4_0
EMBED_MODEL=BAAI/bge-m3
RERANK_MODEL=jinaai/jina-reranker-v1-turbo-en

# Azure AI (Optional)
AZURE_AI_VISION_ENDPOINT=https://your-region.cognitiveservices.azure.com
AZURE_AI_VISION_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-key

# Feature Flags
FeatureFlags__UseRagFirst=true
FeatureFlags__RagRequired=false
```

### Query Routing Configuration

The system automatically routes queries based on complexity:

- **Simple queries** → Local RAG (faster, cost-effective)
- **Complex analysis** → Cloud AI (higher quality, more expensive)

Routing is determined by:
- Query length and complexity
- Domain-specific keywords
- Intent classification
- Confidence thresholds

## Development

### Project Structure

```
documind-engineering/
├── src/
│   ├── dotnet/                 # .NET 8 API services
│   │   ├── DocuMind.Api/      # Main orchestrator API
│   │   ├── Documind.Vision/   # Azure Vision service
│   │   └── Documind.Contracts/ # Shared contracts
│   └── python/                # Python AI services
│       └── services/rag_api/  # RAG processing API
├── scripts/                   # Automation scripts
│   ├── setup.sh              # Universal setup
│   ├── start.sh              # Service management
│   ├── stop.sh               # Clean shutdown
│   └── dev/                  # Development tools
├── docker/                   # Container configurations
├── data/                     # Document storage
└── docs/                     # Documentation
```

### Development Commands

```bash
# Reset development environment
./scripts/dev/reset.sh

# Run integration tests
./scripts/dev/test.sh

# Setup CUDA acceleration
./scripts/dev/setup-cuda.sh

# Format .NET code
cd src/dotnet && dotnet format DocuMind.Api.sln

# Python code formatting
cd src/python && python -m black .
```

### Testing

The project includes comprehensive test suites:

**Health Checks:**
```bash
./scripts/dev/quick-test.sh
```

**Integration Tests:**
```bash
./scripts/dev/test.sh --full
```

**Performance Tests:**
```bash
./scripts/dev/test.sh --performance
```

**API Testing:**
Use the provided HTTP test file:
```
src/dotnet/DocuMind.Api/DocuMind.Api.http
```

## Troubleshooting

### Common Issues

**Docker Permission Error:**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**Python Dependencies:**
```bash
# If conda fails, try pip
pip install -r src/python/requirements.txt
```

**Port Conflicts:**
```bash
# Check port usage
sudo lsof -i :6333,7001,5266

# Kill conflicting processes
sudo pkill -f "qdrant|uvicorn|dotnet"
```

**GPU Not Detected:**
```bash
# Verify CUDA installation
nvidia-smi

# Reinstall CUDA PyTorch
./scripts/dev/setup-cuda.sh
```

**Models Not Downloading:**
```bash
# Manual model download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
ollama pull phi3.5:3.8b-mini-instruct-q4_0
```

### Logs and Monitoring

**Service Logs:**
```bash
# Background service logs
tail -f .run/logs/rag.log
tail -f .run/logs/dotnet.log

# Docker logs
docker logs qdrant
```

**Health Monitoring:**
```bash
# Continuous health check
watch -n 5 ./scripts/dev/quick-test.sh
```

## Technical Details

### Enhanced Query Orchestration

**QueryAnalyzer**: Classifies queries by complexity, domain, and intent
- Simple questions → Local RAG processing
- Complex analysis → Cloud AI escalation
- Multi-dimensional analysis (technical depth, domain specificity, reasoning requirements)

**ConfidenceScorer**: Quality assessment for response validation
- Citation quality verification
- Context relevance scoring
- Hallucination detection
- Automatic escalation for low-confidence responses

### Azure AI Vision Integration

**Complete OCR Pipeline**:
- Azure Computer Vision API 2023-10-01
- Multi-format support (images, PDFs)
- Text extraction with confidence scores
- Caption generation and tag classification
- Bounding box coordinates for layout analysis

**Key Features**:
- File upload processing (25MB limit)
- URL-based image analysis
- Language detection and specification
- Structured response with correlation tracking

### Vector Database Architecture

**Qdrant Configuration**:
- 1024-dimensional embeddings (BAAI/bge-m3)
- Cosine similarity with persistent storage
- UUID-based deterministic document IDs
- Auto-collection creation with retry logic

**RAG Pipeline**:
1. Document chunking and embedding
2. Vector search with configurable topk
3. Jina reranker for relevance scoring
4. Context assembly with citation tracking

## Performance

### Benchmarks

- **Simple queries**: 800-1,700ms (local RAG)
- **Complex analysis**: 4,000-5,000ms (cloud AI)
- **Vector search**: 50-100ms typical
- **GPU acceleration**: 10-100x faster inference

### Optimization

**GPU Acceleration:**
- Requires NVIDIA RTX 20xx+ with 8GB+ VRAM
- Automatic detection and configuration
- Fallback to CPU if GPU unavailable

**Memory Usage:**
- Qdrant: ~500MB baseline
- Python services: ~2-4GB with models loaded
- .NET API: ~100-200MB

## Security

### API Security

- HTTPS support (configure in production)
- Rate limiting (implement as needed)
- Input validation and sanitization
- No sensitive data logging

### Data Privacy

- Local processing by default
- Optional cloud escalation
- Document data stays on-premises
- Configurable data retention

## Production Deployment

### Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: SSD recommended, 50GB+ available
- **Network**: Stable internet for cloud AI features

### Configuration

1. **Environment Setup:**
   ```bash
   export NODE_ENV=production
   export FeatureFlags__UseRagFirst=true
   ```

2. **SSL/TLS:**
   Configure HTTPS certificates for APIs

3. **Monitoring:**
   Implement logging and health check endpoints

4. **Backup:**
   Regular backup of Qdrant data and documents

### Scaling

- **Horizontal**: Multiple API instances behind load balancer
- **Vertical**: Increase CPU/RAM for better performance
- **GPU**: Multiple GPUs for parallel processing
- **Cloud**: Azure AI Foundry for unlimited scaling

## License

[Add your license information here]

## Support

For issues and questions:
- Create GitHub issues for bugs
- Check troubleshooting section first
- Review logs for error details
