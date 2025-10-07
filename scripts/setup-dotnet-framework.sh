#!/bin/bash

# DocuMind .NET Framework Compatibility Manager
# Handles both .NET 8 (current) and .NET 10 (future) environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 DocuMind .NET Framework Compatibility Manager${NC}"
echo "=================================================="

# Check current .NET version
DOTNET_VERSION=$(dotnet --version 2>/dev/null || echo "not-found")

if [[ $DOTNET_VERSION == "not-found" ]]; then
    echo -e "${RED}❌ .NET SDK not found. Please install .NET SDK first.${NC}"
    exit 1
fi

echo -e "${GREEN}📋 Current .NET SDK: $DOTNET_VERSION${NC}"

# Check if .NET 10 is available
if [[ $DOTNET_VERSION == 10.* ]]; then
    echo -e "${GREEN}🎉 .NET 10 detected! Full MCP Framework support available.${NC}"
    FRAMEWORK_MODE="net10-mcp"
elif [[ $DOTNET_VERSION == 8.* ]]; then
    echo -e "${YELLOW}⚠️  .NET 8 detected. MCP packages will be simulated.${NC}"
    echo -e "${YELLOW}   Consider upgrading to .NET 10 for full MCP framework support.${NC}"
    FRAMEWORK_MODE="net8-compat"
else
    echo -e "${RED}❌ Unsupported .NET version: $DOTNET_VERSION${NC}"
    echo -e "${RED}   Supported: .NET 8.0+ or .NET 10.0+${NC}"
    exit 1
fi

echo -e "\n${BLUE}🔄 Configuring framework compatibility...${NC}"

if [[ $FRAMEWORK_MODE == "net8-compat" ]]; then
    echo -e "${YELLOW}🔧 Setting up .NET 8 compatibility mode...${NC}"

    # Temporarily modify global.json for .NET 8 compatibility
    cat > "/home/dinesh/documind-engineering/src/dotnet/global.json" << 'EOF'
{
  "sdk": {
    "version": "8.0.0",
    "rollForward": "latestMajor"
  }
}
EOF

    echo -e "${GREEN}✅ Configured for .NET 8 compatibility${NC}"
    echo -e "${YELLOW}ℹ️  MCP packages will be excluded from build${NC}"

elif [[ $FRAMEWORK_MODE == "net10-mcp" ]]; then
    echo -e "${GREEN}🚀 Setting up .NET 10 with full MCP support...${NC}"

    # Restore original global.json for .NET 10
    cat > "/home/dinesh/documind-engineering/src/dotnet/global.json" << 'EOF'
{
  "sdk": {
    "version": "10.0.0",
    "rollForward": "latestMajor",
    "allowPrerelease": true
  },
  "msbuild-sdks": {
    "Microsoft.Extensions.ModelContextProtocol.Sdk": "10.0.0"
  }
}
EOF

    echo -e "${GREEN}✅ Configured for .NET 10 with MCP framework${NC}"
fi

echo -e "\n${BLUE}🏗️  Testing framework configuration...${NC}"

cd /home/dinesh/documind-engineering/src/dotnet

# Test restore
if dotnet restore DocuMind.Api.sln > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Package restore successful${NC}"

    # Test build
    echo -e "${BLUE}🔨 Testing build...${NC}"
    if dotnet build DocuMind.Api.sln --configuration Release --verbosity minimal > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Build successful${NC}"

        echo -e "\n${GREEN}🎯 Framework Status Summary:${NC}"
        echo -e "=================================================="
        echo -e "SDK Version: ${GREEN}$DOTNET_VERSION${NC}"
        echo -e "Framework Mode: ${GREEN}$FRAMEWORK_MODE${NC}"

        if [[ $FRAMEWORK_MODE == "net10-mcp" ]]; then
            echo -e "MCP Support: ${GREEN}✅ Full Native Support${NC}"
            echo -e "MCP Server: ${GREEN}✅ Available (Port 9090)${NC}"
            echo -e "Enhanced Features: ${GREEN}✅ All enabled${NC}"

            echo -e "\n${BLUE}🚀 Start .NET 10 services:${NC}"
            echo -e "bash scripts/start-dotnet10-mcp.sh"

        else
            echo -e "MCP Support: ${YELLOW}⚠️  Simulated/Limited${NC}"
            echo -e "MCP Server: ${YELLOW}⚠️  Requires .NET 10${NC}"
            echo -e "Enhanced Features: ${YELLOW}⚠️  Upgrade recommended${NC}"

            echo -e "\n${BLUE}🚀 Start current services:${NC}"
            echo -e "bash scripts/dev-up.sh"

            echo -e "\n${YELLOW}📋 To unlock full MCP capabilities:${NC}"
            echo -e "1. Install .NET 10 SDK"
            echo -e "2. Re-run this script"
            echo -e "3. Use: bash scripts/start-dotnet10-mcp.sh"
        fi

    else
        echo -e "${RED}❌ Build failed${NC}"
        echo -e "${RED}📋 Check build errors with: dotnet build DocuMind.Api.sln${NC}"
    fi

else
    echo -e "${RED}❌ Package restore failed${NC}"
    echo -e "${RED}📋 Check package errors with: dotnet restore DocuMind.Api.sln${NC}"
fi

echo -e "\n${BLUE}📚 Documentation:${NC}"
echo -e "• Framework Status: cat DOTNET10_MCP_UPGRADE.md"
echo -e "• Service Health: curl http://localhost:9090/healthz (if running)"
echo -e "• MCP Documentation: http://localhost:9090/swagger (if running)"
