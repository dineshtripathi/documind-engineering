#!/bin/bash
# Production Startup Script for DocuMind
# Starts all services in production mode with comprehensive monitoring

set -e

echo "🚀 Starting DocuMind Production System..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '#' | xargs)
    echo -e "${GREEN}✅ Loaded production environment${NC}"
else
    echo -e "${YELLOW}⚠️  Using default environment settings${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating data directories...${NC}"
mkdir -p data/qdrant_storage
mkdir -p data/ollama
mkdir -p logs

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/health >/dev/null 2>&1 || \
           curl -s http://localhost:$port >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is running on port $port${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Waiting for $service_name (attempt $attempt/$max_attempts)...${NC}"
        sleep 2
        ((attempt++))
    done

    echo -e "${RED}❌ $service_name failed to start on port $port${NC}"
    return 1
}

# Start Docker services
echo -e "${BLUE}🐳 Starting Docker services...${NC}"
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker/docker-compose.production.yml up -d
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose -f docker/docker-compose.production.yml up -d
else
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Desktop.${NC}"
    exit 1
fi

# Wait for Qdrant
echo -e "${BLUE}🔍 Waiting for Qdrant...${NC}"
check_service "Qdrant" 6333

# Wait for Ollama
echo -e "${BLUE}🦙 Waiting for Ollama...${NC}"
check_service "Ollama" 11434

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
source /home/dinesh/miniconda3/etc/profile.d/conda.sh
conda activate documind

# Install additional production dependencies
pip install feedparser python-dateutil uvicorn[standard] gunicorn

# Pull required Ollama models
echo -e "${BLUE}🔽 Pulling Ollama models...${NC}"
MODELS=(
    "phi3.5:3.8b-mini-instruct-q4_0"
    "llama3.1:8b"
    "codellama:13b"
)

# Only pull llama3.1:70b if we have enough resources
if [ $(free -g | awk 'NR==2{print $2}') -gt 32 ]; then
    MODELS+=("llama3.1:70b")
    echo -e "${GREEN}✅ System has enough RAM for 70B model${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping 70B model due to RAM constraints${NC}"
    # Use mixtral as alternative
    MODELS+=("mixtral:8x7b-instruct-v0.1-q4_0")
fi

for model in "${MODELS[@]}"; do
    echo -e "${BLUE}📥 Pulling $model...${NC}"
    if ! docker exec documind-ollama ollama pull $model; then
        echo -e "${YELLOW}⚠️  Failed to pull $model, continuing...${NC}"
    fi
done

# Load production data
echo -e "${BLUE}📚 Loading production knowledge base...${NC}"
cd /home/dinesh/documind-engineering
python scripts/load_production_data.py

# Start RAG API
echo -e "${BLUE}🚀 Starting RAG API...${NC}"
cd src/python
nohup uvicorn services.rag_api.app:app --host 0.0.0.0 --port 7001 --workers 2 > ../../logs/rag_api.log 2>&1 &
RAG_PID=$!
echo $RAG_PID > ../../logs/rag_api.pid

# Wait for RAG API
check_service "RAG API" 7001

# Start Streamlit Web UI
echo -e "${BLUE}🌐 Starting Web UI...${NC}"
cd ../../web-ui
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > ../logs/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo $STREAMLIT_PID > ../logs/streamlit.pid

# Wait for Streamlit
check_service "Streamlit" 8501

# Final health check
echo -e "${BLUE}🔍 Final system health check...${NC}"
sleep 5

# Check all services
SERVICES_OK=true

if ! check_service "Qdrant" 6333; then
    SERVICES_OK=false
fi

if ! check_service "Ollama" 11434; then
    SERVICES_OK=false
fi

if ! check_service "RAG API" 7001; then
    SERVICES_OK=false
fi

if ! check_service "Streamlit" 8501; then
    SERVICES_OK=false
fi

# Show system status
echo "=================================="
if [ "$SERVICES_OK" = true ]; then
    echo -e "${GREEN}🎉 DocuMind Production System Started Successfully!${NC}"
    echo ""
    echo -e "${BLUE}📊 Service URLs:${NC}"
    echo -e "  🌐 Web Interface: ${GREEN}http://localhost:8501${NC}"
    echo -e "  🔧 API Documentation: ${GREEN}http://localhost:7001/docs${NC}"
    echo -e "  📈 Qdrant Dashboard: ${GREEN}http://localhost:6333/dashboard${NC}"
    echo -e "  🦙 Ollama API: ${GREEN}http://localhost:11434${NC}"
    echo ""
    echo -e "${YELLOW}💡 To expose via ngrok:${NC}"
    echo -e "  ngrok http 8501 --domain=your-domain.ngrok.io"
    echo ""
    echo -e "${BLUE}📋 Log files:${NC}"
    echo -e "  RAG API: logs/rag_api.log"
    echo -e "  Streamlit: logs/streamlit.log"
    echo ""
    echo -e "${GREEN}✅ System ready for production use!${NC}"
else
    echo -e "${RED}❌ Some services failed to start. Check logs for details.${NC}"
    exit 1
fi

echo "=================================="
