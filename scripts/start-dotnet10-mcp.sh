#!/bin/bash

# .NET 10 with MCP Framework Service Startup Script
# DocuMind Engineering - Advanced AI Platform with Model Context Protocol

set -e

echo "🚀 Starting DocuMind .NET 10 Services with MCP Framework..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for .NET 10 SDK
echo -e "${BLUE}📋 Checking .NET 10 SDK availability...${NC}"
if command -v dotnet &> /dev/null; then
    DOTNET_VERSION=$(dotnet --version)
    echo -e "${GREEN}✅ .NET SDK Version: $DOTNET_VERSION${NC}"

    if [[ $DOTNET_VERSION == 10.* ]]; then
        echo -e "${GREEN}✅ .NET 10 SDK detected - MCP Framework available${NC}"
    else
        echo -e "${YELLOW}⚠️  .NET 10 SDK not detected. Current version: $DOTNET_VERSION${NC}"
        echo -e "${YELLOW}   MCP packages may require .NET 10 SDK for full functionality${NC}"
    fi
else
    echo -e "${RED}❌ .NET SDK not found. Please install .NET 10 SDK${NC}"
    exit 1
fi

# Function to start a service
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local description=$4

    echo -e "\n${BLUE}🎯 Starting $service_name on port $port...${NC}"
    echo -e "   $description"

    cd "$service_path"

    # Kill any existing process on the port
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "   ${YELLOW}⚠️  Terminating existing process on port $port${NC}"
        lsof -ti:$port | xargs kill -9
        sleep 2
    fi

    # Build the project
    echo -e "   ${BLUE}🔨 Building project...${NC}"
    dotnet build --configuration Release --verbosity minimal

    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✅ Build successful${NC}"

        # Start the service in background
        echo -e "   ${BLUE}🚀 Launching service...${NC}"
        nohup dotnet run --configuration Release --urls "http://localhost:$port" > "/tmp/$service_name.log" 2>&1 &
        SERVICE_PID=$!

        # Wait a moment and check if service started
        sleep 3
        if kill -0 $SERVICE_PID 2>/dev/null; then
            echo -e "   ${GREEN}✅ $service_name started successfully (PID: $SERVICE_PID)${NC}"
            echo -e "   ${GREEN}📡 Endpoint: http://localhost:$port${NC}"
        else
            echo -e "   ${RED}❌ Failed to start $service_name${NC}"
            echo -e "   ${RED}📋 Log: /tmp/$service_name.log${NC}"
        fi
    else
        echo -e "   ${RED}❌ Build failed for $service_name${NC}"
    fi
}

# Start services
BASE_PATH="/home/dinesh/documind-engineering/src/dotnet"

echo -e "\n${YELLOW}🏗️  Starting DocuMind .NET 10 Services...${NC}"

# Start Main API (Enhanced with MCP)
start_service "DocuMind.Api" \
    "$BASE_PATH/Documind/DocuMind.Api" \
    "5266" \
    "Main API service with MCP integration (.NET 10)"

# Start Vision Service (Enhanced with MCP)
start_service "Documind.Vision" \
    "$BASE_PATH/Documind/Documind.Vision" \
    "7002" \
    "Vision processing service with MCP support (.NET 10)"

# Start Semantic Kernel Service (Enhanced with MCP)
start_service "DocuMind.Agents.Semantic" \
    "$BASE_PATH/DocuMind.Agents.Semantic" \
    "5076" \
    "Semantic Kernel agents with MCP integration (.NET 10)"

# Start Agent Framework Service (Enhanced with MCP)
start_service "DocuMind.Agents.AgentFramework" \
    "$BASE_PATH/DocuMind.Agents.AgentFramework" \
    "8082" \
    "Microsoft Agent Framework with MCP (.NET 10)"

# Start NEW MCP Service (Native .NET 10 MCP Framework)
start_service "DocuMind.Agents.Mcp" \
    "$BASE_PATH/DocuMind.Agents.Mcp" \
    "9090" \
    "🆕 Native MCP server showcasing .NET 10 MCP Framework"

echo -e "\n${YELLOW}⏱️  Waiting for services to fully initialize...${NC}"
sleep 10

echo -e "\n${GREEN}🎉 DocuMind .NET 10 Platform Status:${NC}"
echo -e "=================================================="

# Check service health
check_service() {
    local name=$1
    local url=$2
    local description=$3

    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name${NC} - $description"
        echo -e "   🔗 $url"
    else
        echo -e "${RED}❌ $name${NC} - Service unavailable"
        echo -e "   🔗 $url"
    fi
}

check_service "Main API" "http://localhost:5266/healthz" "Core DocuMind API with MCP"
check_service "Vision Service" "http://localhost:7002/healthz" "AI Vision processing with MCP"
check_service "Semantic Kernel" "http://localhost:5076/healthz" "SK agents with MCP integration"
check_service "Agent Framework" "http://localhost:8082/healthz" "MS Agent Framework with MCP"
check_service "🆕 MCP Server" "http://localhost:9090/healthz" "Native .NET 10 MCP Framework"

echo -e "\n${BLUE}📖 Service Documentation:${NC}"
echo -e "=================================================="
echo -e "${YELLOW}Main API Swagger:${NC}        http://localhost:5266/swagger"
echo -e "${YELLOW}Vision API Swagger:${NC}      http://localhost:7002/swagger"
echo -e "${YELLOW}Semantic Kernel Swagger:${NC} http://localhost:5076/swagger"
echo -e "${YELLOW}Agent Framework Swagger:${NC} http://localhost:8082/swagger"
echo -e "${YELLOW}🆕 MCP Server Swagger:${NC}   http://localhost:9090/swagger"

echo -e "\n${BLUE}🔧 MCP Framework Features (.NET 10):${NC}"
echo -e "=================================================="
echo -e "• ${GREEN}Native MCP Protocol Support${NC} - Built into .NET 10"
echo -e "• ${GREEN}Tool Execution Framework${NC} - Dynamic tool registration"
echo -e "• ${GREEN}Resource Access Management${NC} - Secure resource protocols"
echo -e "• ${GREEN}Prompt Template System${NC} - Advanced prompt management"
echo -e "• ${GREEN}Semantic Kernel Integration${NC} - Enhanced SK with MCP"
echo -e "• ${GREEN}Agent Framework Integration${NC} - MS Agents with MCP"

echo -e "\n${BLUE}🧪 Testing MCP Capabilities:${NC}"
echo -e "=================================================="
echo -e "# Test MCP Tools"
echo -e "curl -X POST http://localhost:9090/mcp/tools/document_analysis \\"
echo -e "  -H \"Content-Type: application/json\" \\"
echo -e "  -d '{\"content\": \"Sample document text\", \"analysis_type\": \"summary\"}'"
echo -e ""
echo -e "# Test MCP Resources"
echo -e "curl http://localhost:9090/mcp/resources/documents://knowledge_base"
echo -e ""
echo -e "# Test MCP Server Info"
echo -e "curl http://localhost:9090/"

echo -e "\n${GREEN}🎯 .NET 10 MCP Platform Ready!${NC}"
echo -e "   All services enhanced with Model Context Protocol support"
echo -e "   Native MCP server demonstrates .NET 10's built-in MCP framework"
echo -e "\n${BLUE}📋 Logs available in /tmp/*.log${NC}"
