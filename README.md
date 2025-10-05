# DocuMind Engineering

🚀 **Comprehensive AI Orchestration Platform** combining local LLMs, cloud AI services, and advanced agent frameworks for intelligent document processing and multi-modal AI workflows.

## 🏗️ Architecture Overview

### 🎯 Core Services

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  Web UI  │  REST Clients  │  Swagger/OpenAPI Documentation │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    .NET Services                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │DocuMind.Api │ │Vision:7002  │ │Semantic:5076│ │Agent:8082│ │
│ │    :5266    │ │             │ │    Kernel   │ │Framework │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                 Python AI Services                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ RAG API     │ │ Embeddings  │ │ Reranking   │          │
│  │   :7001     │ │   BAAI/bge  │ │    Jina     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Storage & AI Infrastructure                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │ Qdrant:6333 │ │ Ollama LLM  │ │Azure OpenAI │ │Azure    │ │
│ │Vector Store │ │ Phi-3.5 3.8B│ │ GPT-4o-mini │ │Vision   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 🚀 Service Portfolio

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **DocuMind.Api** | 5266 | Main orchestration service | ✅ Operational |
| **Documind.Vision** | 7002 | Azure AI Vision integration | ✅ Operational |
| **Semantic Kernel** | 5076 | Educational AI workflows | ✅ Ready |
| **Agent Framework** | 8082 | Next-gen agent orchestration | ✅ Operational |
| **Legacy Agents** | 8081 | Original agent service | ✅ Running |
| **Python RAG API** | 7001 | AI processing engine | ✅ CUDA Enabled |
| **Qdrant Vector DB** | 6333 | Vector storage | ✅ Memory Mode |

## Technology Stack
## 🛠️ Technology Stack

### 🔧 Backend Services
- **.NET 8 / ASP.NET Core**: Main orchestration with Swagger documentation
- **Python 3.11 / FastAPI**: RAG processing and AI model inference
- **Docker**: Containerized services and vector database

### 🤖 AI & ML Stack
- **Local LLM**: Ollama Phi-3.5 3.8B (CUDA acceleration)
- **Cloud LLM**: Azure OpenAI GPT-4o-mini
- **Embeddings**: BAAI/bge-m3 (1024-dimensional vectors)
- **Reranking**: Jina reranker v1-turbo-en (cross-encoder)
- **Vision**: Azure AI Vision for OCR and image analysis
- **Frameworks**: Microsoft Semantic Kernel + Agent Framework

### 📊 Database & Storage
- **Vector Database**: Qdrant (cosine similarity, persistent storage)
- **Document Storage**: Local file system with staging support
- **Configuration**: JSON-based with environment overrides

## 🚀 Quick Start Guide

### 📋 Prerequisites

**System Requirements:**
- Ubuntu 20.04+ / Windows 11 with WSL2
- NVIDIA GPU with CUDA 12.1+ (for local AI)
- Docker & Docker Compose
- .NET 8 SDK
- Python 3.10+

**Verify CUDA Support:**
```bash
nvidia-smi  # Should show GPU details
nvcc --version  # CUDA compiler version
```

### ⚡ One-Line Setup

```bash
# Complete environment setup (automated)
bash scripts/provision/workspace-infra-setup/setup-workspace.bash
```

### 🛠️ Manual Setup (Development)

**1. Clone & Navigate**
```bash
git clone <repository-url>
cd documind-engineering
```

**2. Infrastructure Setup**
```bash
# Start all Docker services
./scripts/dev-up.sh

# Verify Qdrant vector database
curl http://localhost:6333/health
```

**3. Python Environment**
```bash
# Create conda environment
conda env create -f src/python/environment.yml
conda activate documind

# Install additional packages
pip install -r src/python/requirements.txt
```

**4. .NET Dependencies**
```bash
cd src/dotnet/DocuMind.Api
dotnet restore
```

### 🎯 Service Startup

**Start All Services (Production Mode):**
```bash
# Start infrastructure
./scripts/dev-up.sh

# Start Python RAG API with CUDA
cd src/python
uvicorn services.rag_api.app:app --host 0.0.0.0 --port 7001

# Start .NET main API
cd src/dotnet/DocuMind.Api/DocuMind.Api
dotnet run --urls "http://localhost:5266"

# Start Vision API
cd src/dotnet/DocuMind.Api/Documind.Vision
dotnet run --urls "http://localhost:7002"
```

**Educational Workflows:**
```bash
# Start Semantic Kernel service
cd src/dotnet/DocuMind.Api/DocuMind.Agents.SemanticKernel
dotnet run --urls "http://localhost:5076"

# Start Agent Framework service
cd src/dotnet/DocuMind.Api/DocuMind.Agents.AgentFramework
dotnet run --urls "http://localhost:8082"
```

### 🧪 Health Verification

**Service Health Check:**
```bash
# Check all services
curl http://localhost:5266/health  # Main API
curl http://localhost:7001/health  # Python RAG
curl http://localhost:7002/health  # Vision API
curl http://localhost:5076/health  # Semantic Kernel
curl http://localhost:8082/health  # Agent Framework
curl http://localhost:6333/health  # Qdrant Vector DB
```

**Quick AI Test:**
```bash
# Test RAG processing
curl -X POST "http://localhost:5266/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is artificial intelligence?"}'

# Test agent frameworks comparison
curl "http://localhost:5076/semantickernel/workflows/list"
curl "http://localhost:8082/agentframework/workflows/list"
```
## 📚 Educational Framework Comparison

### 🎓 Agent Framework Learning

This project includes **educational implementations** comparing Microsoft's Semantic Kernel and Agent Framework approaches:

**Semantic Kernel (Port 5076):**
- Traditional function composition
- Direct kernel service integration
- Compatible with production packages
- Proven stability for enterprise use

**Agent Framework (Port 8082):**
- Next-generation agent orchestration
- Multi-agent collaboration patterns
- Educational compatibility layer
- Future-ready architecture concepts

### 🔬 Learning Endpoints

```bash
# List available workflows
curl "http://localhost:5076/semantickernel/workflows/list"
curl "http://localhost:8082/agentframework/workflows/list"

# Execute educational workflows
curl -X POST "http://localhost:5076/semantickernel/execute/simple" \
  -H "Content-Type: application/json" \
  -d '{"input": "learning example"}'

curl -X POST "http://localhost:8082/agentframework/execute/collaborative" \
  -H "Content-Type: application/json" \
  -d '{"query": "multi-agent example"}'
```

**📖 Key Learning Concepts:**
- Function composition vs agent orchestration
- Sequential vs parallel processing
- State management approaches
- Error handling strategies
- Performance optimization patterns

## 🔧 Configuration Management

### 🌍 Environment Variables

Create `.env` file in project root:
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://documind-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini

# Azure Vision Configuration
AZURE_VISION_ENDPOINT=https://your-vision-resource.cognitiveservices.azure.com/
AZURE_VISION_API_KEY=your_vision_key_here

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=documents

# Local LLM Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3.5:3.8b
```

### ⚙️ Service Configuration

**appsettings.json locations:**
```
src/dotnet/DocuMind.Api/DocuMind.Api/appsettings.json               # Main API
src/dotnet/DocuMind.Api/Documind.Vision/appsettings.json           # Vision Service
src/dotnet/DocuMind.Api/DocuMind.Agents.SemanticKernel/appsettings.json    # Semantic Kernel
src/dotnet/DocuMind.Api/DocuMind.Agents.AgentFramework/appsettings.json    # Agent Framework
```

## 📡 API Documentation

### 🎯 Main Orchestration API (Port 5266)

**Core Endpoints:**
```bash
GET    /health                           # Service health check
POST   /api/ask                          # Intelligent Q&A processing
GET    /api/documents                    # List processed documents
POST   /api/documents/upload             # Upload new documents
DELETE /api/documents/{id}               # Remove documents
```

**Swagger UI:** `http://localhost:5266/swagger`

### 🖼️ Vision API (Port 7002)

**Vision Endpoints:**
```bash
GET    /health                           # Vision service health
POST   /api/vision/analyze               # Image analysis
POST   /api/vision/ocr                   # Text extraction from images
POST   /api/vision/describe              # Image description
```

### 🧠 Python RAG API (Port 7001)

**RAG Processing:**
```bash
GET    /health                           # RAG service health
POST   /query                            # Direct RAG query processing
GET    /models/status                    # Model loading status
POST   /embeddings                       # Generate embeddings
POST   /rerank                           # Rerank search results
```

## 🗂️ Project Structure Deep Dive

### 📁 Directory Organization

```
documind-engineering/
├── 🐳 docker/                           # Docker Compose configurations
│   └── compose.yml                      # Qdrant vector database setup
├── 🏗️ infra/                           # Kubernetes & Infrastructure
│   └── k8s/                            # K8s deployment manifests
├── 📊 IaC/                             # Infrastructure as Code
│   ├── main.bicep                      # Azure Bicep templates
│   └── parameters.json                 # Deployment parameters
├── 📚 data/                            # Data storage
│   ├── docs/                           # Document ingestion
│   └── staging/                        # Processing workspace
├── 🧪 notebooks/                       # Jupyter analysis notebooks
├── 📦 models/                          # Local model storage
├── 📜 scripts/                         # Automation scripts
│   ├── dev-up.sh                       # Start development environment
│   ├── dev-down.sh                     # Stop services
│   ├── dev-reset.sh                    # Reset environment
│   └── provision/                      # Setup automation
├── 🐍 src/python/                      # Python AI services
│   ├── environment.yml                 # Conda environment
│   ├── requirements.txt                # Pip dependencies
│   ├── services/rag_api/               # FastAPI RAG service
│   └── tests/                          # Python test suite
└── 🔷 src/dotnet/                      # .NET service collection
    └── DocuMind.Api.sln                # Main solution file
        ├── DocuMind.Api/               # Main orchestration API
        ├── Documind.Vision/            # Vision processing service
        ├── DocuMind.Agents.SemanticKernel/     # Educational SK workflows
        └── DocuMind.Agents.AgentFramework/     # Educational AF workflows
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

## 🚨 Troubleshooting Guide

### 🔍 Common Issues & Solutions

**❌ Service Port Conflicts**
```bash
# Check port usage
netstat -tlnp | grep -E ":(5266|7001|7002|5076|8082|6333)"

# Kill processes using ports
sudo lsof -ti:5266 | xargs sudo kill -9
```

**❌ CUDA/GPU Issues**
```bash
# Verify GPU availability
nvidia-smi
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Reset CUDA context
sudo nvidia-smi --gpu-reset
```

**❌ Docker Permission Denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker  # Refresh group membership
```

**❌ Qdrant Connection Issues**
```bash
# Check Qdrant status
docker ps | grep qdrant
curl http://localhost:6333/health

# Restart Qdrant
docker restart qdrant
```

**❌ .NET Build Failures**
```bash
# Clear NuGet cache
dotnet nuget locals all --clear

# Restore packages
cd src/dotnet/DocuMind.Api
dotnet clean && dotnet restore
```

**❌ Python Environment Issues**
```bash
# Recreate conda environment
conda env remove -n documind
conda env create -f src/python/environment.yml
conda activate documind
```

### 📋 Health Check Commands

**Comprehensive System Check:**
```bash
# Check all services
./scripts/health-check.sh

# Manual verification
ps aux | grep -E "(dotnet|python|qdrant)" | grep -v grep
netstat -tlnp | grep -E ":(5266|7001|7002|5076|8082|6333)"
```

**Service-Specific Health:**
```bash
# Main API health
curl -f http://localhost:5266/health || echo "Main API down"

# RAG API health
curl -f http://localhost:7001/health || echo "RAG API down"

# Vision API health
curl -f http://localhost:7002/health || echo "Vision API down"

# Educational services
curl -f http://localhost:5076/health || echo "Semantic Kernel down"
curl -f http://localhost:8082/health || echo "Agent Framework down"

# Vector database
curl -f http://localhost:6333/health || echo "Qdrant down"
```

## 📋 Automated Setup Scripts

### 🎛️ Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `dev-up.sh` | Start Docker infrastructure | `./scripts/dev-up.sh` |
| `dev-down.sh` | Stop all services | `./scripts/dev-down.sh` |
| `dev-reset.sh` | Reset environment completely | `./scripts/dev-reset.sh` |
| `run-rag-api.sh` | Start Python RAG API | `./scripts/run-rag-api.sh` |
| `setup-workspace.bash` | Complete environment setup | `./scripts/provision/workspace-infra-setup/setup-workspace.bash` |

### 🔧 Create Enhanced Setup Scripts

Let's create some additional automation scripts for easier management:

```bash
# Create start-all.sh
cat > scripts/start-all.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting DocuMind Engineering Platform..."

# Start infrastructure
echo "📦 Starting Docker services..."
./scripts/dev-up.sh

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
until curl -sf http://localhost:6333/health > /dev/null; do
    sleep 2
done
echo "✅ Qdrant is ready"

# Start Python RAG API in background
echo "🐍 Starting Python RAG API..."
cd src/python
uvicorn services.rag_api.app:app --host 0.0.0.0 --port 7001 &
RAG_PID=$!
cd ../..

# Start .NET services
echo "🔷 Starting .NET services..."

# Main API
cd src/dotnet/DocuMind.Api/DocuMind.Api
dotnet run --urls "http://localhost:5266" &
MAIN_PID=$!
cd ../../../..

# Vision API
cd src/dotnet/DocuMind.Api/Documind.Vision
dotnet run --urls "http://localhost:7002" &
VISION_PID=$!
cd ../../../..

# Educational services
cd src/dotnet/DocuMind.Api/DocuMind.Agents.SemanticKernel
dotnet run --urls "http://localhost:5076" &
SK_PID=$!
cd ../../../..

cd src/dotnet/DocuMind.Api/DocuMind.Agents.AgentFramework
dotnet run --urls "http://localhost:8082" &
AF_PID=$!
cd ../../../..

echo "⏳ Waiting for services to start..."
sleep 10

echo "🧪 Running health checks..."
./scripts/health-check.sh

echo "✅ All services started successfully!"
echo "📚 Access Swagger UI: http://localhost:5266/swagger"
echo "🔧 Educational endpoints available on ports 5076 and 8082"

# Store PIDs for cleanup
echo "$RAG_PID $MAIN_PID $VISION_PID $SK_PID $AF_PID" > .service_pids
EOF

chmod +x scripts/start-all.sh
```

```bash
# Create health-check.sh
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash

echo "🧪 DocuMind Health Check..."
echo "=========================="

services=(
    "Main API:5266:http://localhost:5266/health"
    "RAG API:7001:http://localhost:7001/health"
    "Vision API:7002:http://localhost:7002/health"
    "Semantic Kernel:5076:http://localhost:5076/health"
    "Agent Framework:8082:http://localhost:8082/health"
    "Qdrant DB:6333:http://localhost:6333/health"
)

all_healthy=true

for service in "${services[@]}"; do
    IFS=':' read -r name port url <<< "$service"
    printf "%-20s " "$name"

    if curl -sf "$url" > /dev/null 2>&1; then
        echo "✅ Healthy (Port $port)"
    else
        echo "❌ Unhealthy (Port $port)"
        all_healthy=false
    fi
done

echo "=========================="
if $all_healthy; then
    echo "🎉 All services are healthy!"
    exit 0
else
    echo "⚠️  Some services are unhealthy"
    exit 1
fi
EOF

chmod +x scripts/health-check.sh
```

```bash
# Create stop-all.sh
cat > scripts/stop-all.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping DocuMind Engineering Platform..."

# Kill services by PIDs if available
if [ -f .service_pids ]; then
    echo "📋 Stopping services using stored PIDs..."
    read -r pids < .service_pids
    for pid in $pids; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔻 Stopping PID $pid"
            kill "$pid"
        fi
    done
    rm .service_pids
fi

# Kill by port/process name as backup
echo "🔍 Cleaning up remaining processes..."
pkill -f "uvicorn.*rag_api" || true
pkill -f "dotnet.*DocuMind" || true

# Stop Docker services
echo "🐳 Stopping Docker services..."
./scripts/dev-down.sh

echo "✅ All services stopped"
EOF

chmod +x scripts/stop-all.sh
```

## 🎯 Usage Examples & Workflows

### 🤖 AI Query Processing

**Basic RAG Query:**
```bash
curl -X POST "http://localhost:5266/api/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key benefits of vector databases?",
    "useLocalModel": false,
    "includeContext": true
  }'
```

**Complex Multi-Modal Query:**
```bash
# Upload and analyze document
curl -X POST "http://localhost:5266/api/documents/upload" \
  -F "file=@document.pdf" \
  -F "description=Technical specification"

# Query with vision analysis
curl -X POST "http://localhost:7002/api/vision/analyze" \
  -F "image=@diagram.png"
```

### 🎓 Educational Framework Learning

**Semantic Kernel Workflows:**
```bash
# List available workflows
curl "http://localhost:5076/semantickernel/workflows/list"

# Execute simple workflow
curl -X POST "http://localhost:5076/semantickernel/execute/simple" \
  -H "Content-Type: application/json" \
  -d '{"input": "Explain neural networks"}'
```

**Agent Framework Patterns:**
```bash
# List agent framework capabilities
curl "http://localhost:8082/agentframework/workflows/list"

# Execute collaborative workflow
curl -X POST "http://localhost:8082/agentframework/execute/collaborative" \
  -H "Content-Type: application/json" \
  -d '{"query": "Research and summarize machine learning trends"}'
```

## 🔧 Development & Customization

### 🎨 Adding New Features

**1. Extend RAG Processing:**
```python
# In src/python/services/rag_api/rag_core.py
def custom_preprocessing(query: str) -> str:
    # Add your custom query preprocessing
    return enhanced_query
```

**2. Add New .NET Controllers:**
```csharp
// In src/dotnet/DocuMind.Api/DocuMind.Api/Controllers/
[ApiController]
[Route("api/[controller]")]
public class CustomController : ControllerBase
{
    // Your custom endpoints
}
```

**3. Educational Workflow Extensions:**
```csharp
// In DocuMind.Agents.SemanticKernel or AgentFramework
public async Task<string> CustomLearningWorkflow(string input)
{
    // Implement your educational pattern
}
```

### 📚 Model Customization

**Local Model Updates:**
```bash
# Change Ollama model
ollama pull llama3.1:8b
# Update configuration in appsettings.json
```

**Azure OpenAI Configuration:**
```json
{
  "AzureOpenAI": {
    "Endpoint": "https://your-resource.openai.azure.com/",
    "ApiKey": "your-api-key",
    "DeploymentName": "gpt-4"
  }
}
```

## 🚀 Production Deployment

### 🐳 Docker Production Setup

**Create production Docker Compose:**
```yaml
# docker/production.yml
version: '3.8'
services:
  documind-api:
    build: ./src/dotnet
    ports:
      - "80:5266"
    environment:
      - ASPNETCORE_ENVIRONMENT=Production

  rag-api:
    build: ./src/python
    ports:
      - "8000:7001"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### ☁️ Azure Deployment

**Infrastructure as Code (Bicep):**
```bash
# Deploy using Azure Bicep
az deployment group create \
  --resource-group documind-rg \
  --template-file IaC/main.bicep \
  --parameters @IaC/parameters.json
```

**Kubernetes Deployment:**
```bash
# Apply K8s manifests
kubectl apply -f infra/k8s/
```

## 📊 Monitoring & Observability

### 📈 Performance Metrics

**Service Monitoring:**
```bash
# Check resource usage
docker stats

# Monitor GPU usage
nvidia-smi -l 1

# Check service logs
docker logs qdrant
tail -f logs/rag_api.log
```

**Health Monitoring Script:**
```bash
# Continuous health monitoring
watch -n 30 './scripts/health-check.sh'
```

### 🐛 Debugging

**Enable Debug Logging:**
```json
// In appsettings.Development.json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.SemanticKernel": "Trace"
    }
  }
}
```

**Python Debug Mode:**
```bash
# Start RAG API with debug logging
cd src/python
uvicorn services.rag_api.app:app --host 0.0.0.0 --port 7001 --log-level debug
```

## 🤝 Contributing

### 📝 Development Guidelines

**1. Code Structure:**
- Follow .NET naming conventions for C# code
- Use Python PEP 8 for Python code
- Add comprehensive XML documentation for public APIs
- Include unit tests for new features

**2. Testing:**
```bash
# Run .NET tests
cd src/dotnet/DocuMind.Api
dotnet test

# Run Python tests
cd src/python
pytest tests/
```

**3. Pull Request Process:**
- Fork the repository
- Create feature branch: `git checkout -b feature/amazing-feature`
- Commit changes: `git commit -m 'Add amazing feature'`
- Push to branch: `git push origin feature/amazing-feature`
- Open Pull Request

### 🔧 Development Setup

**VS Code Extensions (Recommended):**
- C# Dev Kit
- Python Extension Pack
- Docker Extension
- REST Client
- GitLens

## 📞 Support & Resources

### 🆘 Getting Help

**Common Solutions:**
1. **Port conflicts**: Use `./scripts/stop-all.sh` then restart
2. **GPU issues**: Check CUDA installation with `nvidia-smi`
3. **Docker issues**: Restart Docker daemon: `sudo systemctl restart docker`
4. **Package conflicts**: Recreate conda environment

**Documentation Links:**
- [Microsoft Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Qdrant Vector Database](https://qdrant.tech/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### 📧 Contact & Community

**Reporting Issues:**
- Create GitHub issue with reproduction steps
- Include system information and logs
- Use appropriate issue templates

**Feature Requests:**
- Describe the use case clearly
- Provide examples and mockups
- Consider contributing the implementation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

**Technologies & Frameworks:**
- Microsoft Semantic Kernel & Agent Framework teams
- FastAPI and Pydantic communities
- Qdrant vector database developers
- NVIDIA CUDA and PyTorch teams
- Azure AI Services team

**Special Thanks:**
- Open source AI/ML community
- Contributors and testers
- Documentation reviewers

---

**📊 Project Status:** ✅ **Fully Operational** - All 6 services running with educational framework comparison

**🚀 Quick Start:** `./scripts/start-all.sh` → `./scripts/health-check.sh` → Open `http://localhost:5266/swagger`
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
