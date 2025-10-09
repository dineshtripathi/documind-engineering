#!/bin/bash
# Production Stop Script for DocuMind
# Gracefully stops all services and cleans up

set -e

echo "🛑 Stopping DocuMind Production System..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to stop service by PID
stop_service_by_pid() {
    local service_name=$1
    local pid_file=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${BLUE}🛑 Stopping $service_name (PID: $pid)...${NC}"
            kill -TERM $pid

            # Wait for graceful shutdown
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                ((count++))
            done

            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  Force stopping $service_name...${NC}"
                kill -KILL $pid
            fi

            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name was not running${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No PID file found for $service_name${NC}"
    fi
}

# Stop Streamlit
stop_service_by_pid "Streamlit" "logs/streamlit.pid"

# Stop RAG API
stop_service_by_pid "RAG API" "logs/rag_api.pid"

# Stop any remaining Python processes
echo -e "${BLUE}🔍 Stopping remaining Python services...${NC}"
pkill -f "streamlit run app.py" 2>/dev/null || true
pkill -f "uvicorn app:app" 2>/dev/null || true

# Stop Docker services
echo -e "${BLUE}🐳 Stopping Docker services...${NC}"
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker/docker-compose.production.yml down
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose -f docker/docker-compose.production.yml down
else
    echo -e "${YELLOW}⚠️  Docker Compose not found, stopping containers manually...${NC}"
    docker stop documind-qdrant documind-ollama 2>/dev/null || true
fi

# Clean up log files (optional)
echo -e "${BLUE}📝 Log files preserved in logs/ directory${NC}"

echo "=================================="
echo -e "${GREEN}✅ DocuMind Production System Stopped${NC}"
echo ""
echo -e "${BLUE}💡 Data preserved:${NC}"
echo -e "  📊 Qdrant data: data/qdrant_storage/"
echo -e "  🦙 Ollama models: data/ollama/"
echo -e "  📋 Logs: logs/"
echo ""
echo -e "${YELLOW}To restart: ./scripts/start-production.sh${NC}"
echo "=================================="
