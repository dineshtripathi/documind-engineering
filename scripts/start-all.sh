#!/bin/bash
set -e

echo "🚀 Starting DocuMind Engineering Platform..."

# Start infrastructure
echo "📦 Starting Docker services..."
./scripts/dev-up.sh

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
until curl -sf http://localhost:6333/health > /dev/null 2>&1; do
    sleep 2
    echo "  Still waiting for Qdrant..."
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
sleep 15

echo "🧪 Running health checks..."
./scripts/health-check.sh

echo "✅ All services started successfully!"
echo ""
echo "📚 Service Access Points:"
echo "  • Main API & Swagger UI: http://localhost:5266/swagger"
echo "  • Python RAG API: http://localhost:7001/docs"
echo "  • Vision API: http://localhost:7002/swagger"
echo "  • Semantic Kernel Educational: http://localhost:5076/swagger"
echo "  • Agent Framework Educational: http://localhost:8082/swagger"
echo "  • Qdrant Admin UI: http://localhost:6333/dashboard"
echo ""
echo "🔧 Management Commands:"
echo "  • Health Check: ./scripts/health-check.sh"
echo "  • Stop All: ./scripts/stop-all.sh"

# Store PIDs for cleanup
echo "$RAG_PID $MAIN_PID $VISION_PID $SK_PID $AF_PID" > .service_pids
