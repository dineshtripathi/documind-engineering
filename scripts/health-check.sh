#!/bin/bash#!/bin/bash

# 🏥 System Health Check & Validation

# Comprehensive system validation for DocuMindecho "🧪 DocuMind Health Check..."

echo "=========================="

set -e

services=(

echo "🏥 DocuMind System Health Check"    "Main API:5266:http://127.0.0.1:5266/swagger"

echo "==============================="    "RAG API:7001:http://127.0.0.1:7001/healthz"

echo ""    "Vision API:7002:http://127.0.0.1:7002/swagger"

    "Semantic Kernel:5076:http://127.0.0.1:5076/swagger"

# Colors for output    "Agent Framework:8082:http://127.0.0.1:8082/"

RED='\033[0;31m'    "Legacy Agents:8081:http://127.0.0.1:8081/swagger"

GREEN='\033[0;32m'     "Qdrant DB:6333:http://127.0.0.1:6333/dashboard"

YELLOW='\033[1;33m')

NC='\033[0m' # No Color

all_healthy=true

# Test results

TESTS_PASSED=0for service in "${services[@]}"; do

TESTS_FAILED=0    IFS=':' read -r name port url <<< "$service"

    printf "%-20s " "$name"

# Helper functions

pass() {    if curl -sf "$url" > /dev/null 2>&1; then

    echo -e "${GREEN}✅ $1${NC}"        echo "✅ Healthy (Port $port)"

    ((TESTS_PASSED++))    else

}        echo "❌ Unhealthy (Port $port)"

        all_healthy=false

fail() {    fi

    echo -e "${RED}❌ $1${NC}"done

    ((TESTS_FAILED++))

}echo "=========================="

if $all_healthy; then

warn() {    echo "🎉 All services are healthy!"

    echo -e "${YELLOW}⚠️ $1${NC}"    echo ""

}    echo "🔗 Quick Access Links:"

    echo "  • Main API: http://127.0.0.1:5266/swagger"

# System Resources Check    echo "  • RAG API Docs: http://127.0.0.1:7001/docs"

echo "📊 System Resources:"    echo "  • Vision API: http://127.0.0.1:7002/swagger"

echo "===================="    echo "  • Semantic Kernel: http://127.0.0.1:5076/swagger"

    echo "  • Agent Framework: http://127.0.0.1:8082/swagger"

# RAM Check    echo "  • Legacy Agents: http://127.0.0.1:8081/swagger"

RAM_GB=$(free -g | grep Mem | awk '{print $2}')    echo "  • Qdrant Dashboard: http://127.0.0.1:6333/dashboard"

if [ "$RAM_GB" -ge 150 ]; then    echo ""

    pass "RAM: ${RAM_GB}GB (Excellent for large models)"    echo "🎯 Test Commands:"

else    echo "  • RAG Query: curl -X POST 'http://127.0.0.1:7001/ask' -H 'Content-Type: application/json' -d '{\"q\":\"test\"}'"

    warn "RAM: ${RAM_GB}GB (May limit concurrent model loading)"    echo "  • Main API Ask: curl -X POST 'http://127.0.0.1:5266/api/ask' -H 'Content-Type: application/json' -d '{\"question\":\"test\"}'"

fi    exit 0

else

# GPU Check    echo "⚠️  Some services are unhealthy"

if nvidia-smi &> /dev/null; then    echo ""

    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)    echo "🔧 Troubleshooting tips:"

    GPU_MEM_GB=$((GPU_MEM / 1024))    echo "  • Check logs: docker logs qdrant"

    if [ "$GPU_MEM_GB" -ge 20 ]; then    echo "  • Restart services: ./scripts/stop-all.sh && ./scripts/start-all.sh"

        pass "GPU Memory: ${GPU_MEM_GB}GB (Perfect for 70B models)"    echo "  • Check ports: netstat -tlnp | grep -E ':(5266|7001|7002|5076|8082|8081|6333)'"

    else    exit 1

        warn "GPU Memory: ${GPU_MEM_GB}GB (May need CPU fallback)"fi

    fi
else
    fail "GPU: NVIDIA GPU not detected"
fi

# CPU Check
CPU_CORES=$(nproc)
if [ "$CPU_CORES" -ge 16 ]; then
    pass "CPU Cores: $CPU_CORES (Excellent for parallel processing)"
else
    warn "CPU Cores: $CPU_CORES (Consider upgrading for better performance)"
fi

echo ""

# Storage Check
echo "💾 Storage:"
echo "============"

# H: drive check
if [ -d "/mnt/h/ollama-models" ]; then
    H_DRIVE_SIZE=$(df -h /mnt/h | tail -1 | awk '{print $2}')
    H_DRIVE_USED=$(du -sh /mnt/h/ollama-models | cut -f1)
    pass "H: Drive Models: $H_DRIVE_USED / $H_DRIVE_SIZE"
else
    fail "H: Drive not accessible at /mnt/h/ollama-models"
fi

# Project disk usage
PROJECT_SIZE=$(du -sh . --exclude=.venv --exclude=.git | cut -f1)
pass "Project Size: $PROJECT_SIZE (YAGNI compliance)"

echo ""

# Services Check
echo "🚀 Services:"
echo "============"

# Ollama Check
if pgrep -f ollama > /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        MODEL_COUNT=$(ollama list | grep -v NAME | wc -l)
        pass "Ollama: Running with $MODEL_COUNT models"
    else
        warn "Ollama: Process running but API not responding"
    fi
else
    fail "Ollama: Service not running"
fi

# Docker Check
if docker --version > /dev/null 2>&1; then
    if docker compose -f docker/compose.yml ps | grep -q "qdrant.*Up"; then
        pass "Qdrant: Vector database running"
    else
        fail "Qdrant: Vector database not running"
    fi
else
    fail "Docker: Not installed or not accessible"
fi

# Python Environment Check
if [ -d ".venv" ]; then
    if [ -f ".venv/bin/activate" ]; then
        pass "Python: Virtual environment ready"
    else
        fail "Python: Virtual environment corrupted"
    fi
else
    fail "Python: No virtual environment found"
fi

echo ""

# Quick Functional Tests
echo "🧪 Functional Tests:"
echo "==================="

# Ollama API test
if curl -s http://localhost:11434/api/tags > /dev/null; then
    pass "Ollama API: Responding"
else
    fail "Ollama API: Not responding"
fi

# Qdrant API test  
if curl -s http://localhost:6333/health > /dev/null; then
    pass "Qdrant API: Responding"
else
    fail "Qdrant API: Not responding"
fi

# Model responsiveness test (quick)
if command -v ollama &> /dev/null; then
    SMALLEST_MODEL=$(ollama list | grep -v NAME | head -1 | awk '{print $1}')
    if [ ! -z "$SMALLEST_MODEL" ]; then
        if timeout 10s ollama run "$SMALLEST_MODEL" "Hi" > /dev/null 2>&1; then
            pass "Model Test: $SMALLEST_MODEL responsive"
        else
            warn "Model Test: $SMALLEST_MODEL slow or unresponsive"
        fi
    fi
fi

echo ""

# Summary
echo "📋 Health Check Summary:"
echo "========================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 System is healthy and ready for DocuMind development!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️ Some issues detected. Review failed tests above.${NC}"
    exit 1
fi