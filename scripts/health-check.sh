#!

# 🏥 System Health Check & Validation# 🏥 System Health Check & Validation

# Comprehensive system validation for DocuMind# Comprehensive system validation for DocuMind



set -eset -e



echo "🏥 DocuMind System Health Check"echo "🏥 DocuMind System Health Check"

echo "==============================="

echo ""echo "=========================="



# Colors for outputset -e

RED='\033[0;31m'

GREEN='\033[0;32m' services=(

YELLOW='\033[1;33m'

NC='\033[0m' # No Colorecho "🏥 DocuMind System Health Check"    "Main API:5266:http://127.0.0.1:5266/swagger"



# Test resultsecho "==============================="    "RAG API:7001:http://127.0.0.1:7001/healthz"

TESTS_PASSED=0

TESTS_FAILED=0echo ""    "Vision API:7002:http://127.0.0.1:7002/swagger"



# Helper functions    "Semantic Kernel:5076:http://127.0.0.1:5076/swagger"

pass() {

    echo -e "${GREEN}✅ $1${NC}"# Colors for output    "Agent Framework:8082:http://127.0.0.1:8082/"

    ((TESTS_PASSED++))

}RED='\033[0;31m'    "Legacy Agents:8081:http://127.0.0.1:8081/swagger"



fail() {GREEN='\033[0;32m'     "Qdrant DB:6333:http://127.0.0.1:6333/dashboard"

    echo -e "${RED}❌ $1${NC}"

    ((TESTS_FAILED++))YELLOW='\033[1;33m')

}

NC='\033[0m' # No Color

warn() {

    echo -e "${YELLOW}⚠️ $1${NC}"all_healthy=true

}

# Test results

# System Resources Check

echo "📊 System Resources:"TESTS_PASSED=0for service in "${services[@]}"; do

echo "===================="

TESTS_FAILED=0    IFS=':' read -r name port url <<< "$service"

# RAM Check

RAM_GB=$(free -g | grep Mem | awk '{print $2}')    printf "%-20s " "$name"

if [ "$RAM_GB" -ge 150 ]; then

    pass "RAM: ${RAM_GB}GB (Excellent for large models)"# Helper functions

else

    warn "RAM: ${RAM_GB}GB (May limit concurrent model loading)"pass() {    if curl -sf "$url" > /dev/null 2>&1; then

fi

    echo -e "${GREEN}✅ $1${NC}"        echo "✅ Healthy (Port $port)"

# GPU Check

if nvidia-smi &> /dev/null; then    ((TESTS_PASSED++))    else

    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)

    GPU_MEM_GB=$((GPU_MEM / 1024))}        echo "❌ Unhealthy (Port $port)"

    if [ "$GPU_MEM_GB" -ge 20 ]; then

        pass "GPU Memory: ${GPU_MEM_GB}GB (Perfect for 70B models)"        all_healthy=false

    else

        warn "GPU Memory: ${GPU_MEM_GB}GB (May need CPU fallback)"fail() {    fi

    fi

else    echo -e "${RED}❌ $1${NC}"done

    fail "GPU: NVIDIA GPU not detected"

fi    ((TESTS_FAILED++))



# CPU Check}echo "=========================="

CPU_CORES=$(nproc)

if [ "$CPU_CORES" -ge 16 ]; thenif $all_healthy; then

    pass "CPU Cores: $CPU_CORES (Excellent for parallel processing)"

elsewarn() {    echo "🎉 All services are healthy!"

    warn "CPU Cores: $CPU_CORES (Consider upgrading for better performance)"

fi    echo -e "${YELLOW}⚠️ $1${NC}"    echo ""



echo ""}    echo "🔗 Quick Access Links:"



# Storage Check    echo "  • Main API: http://127.0.0.1:5266/swagger"

echo "💾 Storage:"

echo "============"# System Resources Check    echo "  • RAG API Docs: http://127.0.0.1:7001/docs"



# H: drive checkecho "📊 System Resources:"    echo "  • Vision API: http://127.0.0.1:7002/swagger"

if [ -d "/mnt/h/ollama-models" ]; then

    H_DRIVE_SIZE=$(df -h /mnt/h | tail -1 | awk '{print $2}')echo "===================="    echo "  • Semantic Kernel: http://127.0.0.1:5076/swagger"

    H_DRIVE_USED=$(du -sh /mnt/h/ollama-models | cut -f1)

    pass "H: Drive Models: $H_DRIVE_USED / $H_DRIVE_SIZE"    echo "  • Agent Framework: http://127.0.0.1:8082/swagger"

else

    fail "H: Drive not accessible at /mnt/h/ollama-models"# RAM Check    echo "  • Legacy Agents: http://127.0.0.1:8081/swagger"

fi

RAM_GB=$(free -g | grep Mem | awk '{print $2}')    echo "  • Qdrant Dashboard: http://127.0.0.1:6333/dashboard"

# Project disk usage

PROJECT_SIZE=$(du -sh . --exclude=.venv --exclude=.git | cut -f1)if [ "$RAM_GB" -ge 150 ]; then    echo ""

pass "Project Size: $PROJECT_SIZE (YAGNI compliance)"

    pass "RAM: ${RAM_GB}GB (Excellent for large models)"    echo "🎯 Test Commands:"

echo ""

else    echo "  • RAG Query: curl -X POST 'http://127.0.0.1:7001/ask' -H 'Content-Type: application/json' -d '{\"q\":\"test\"}'"

# Services Check

echo "🚀 Services:"    warn "RAM: ${RAM_GB}GB (May limit concurrent model loading)"    echo "  • Main API Ask: curl -X POST 'http://127.0.0.1:5266/api/ask' -H 'Content-Type: application/json' -d '{\"question\":\"test\"}'"

echo "============"

fi    exit 0

# Ollama Check

if pgrep -f ollama > /dev/null; thenelse

    if curl -s http://localhost:11434/api/tags > /dev/null; then

        MODEL_COUNT=$(ollama list | grep -v NAME | wc -l)# GPU Check    echo "⚠️  Some services are unhealthy"

        pass "Ollama: Running with $MODEL_COUNT models"

    elseif nvidia-smi &> /dev/null; then    echo ""

        warn "Ollama: Process running but API not responding"

    fi    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)    echo "🔧 Troubleshooting tips:"

else

    fail "Ollama: Service not running"    GPU_MEM_GB=$((GPU_MEM / 1024))    echo "  • Check logs: docker logs qdrant"

fi

    if [ "$GPU_MEM_GB" -ge 20 ]; then    echo "  • Restart services: ./scripts/stop-all.sh && ./scripts/start-all.sh"

# Docker Check

if docker --version > /dev/null 2>&1; then        pass "GPU Memory: ${GPU_MEM_GB}GB (Perfect for 70B models)"    echo "  • Check ports: netstat -tlnp | grep -E ':(5266|7001|7002|5076|8082|8081|6333)'"

    if docker compose -f docker/compose.yml ps | grep -q "qdrant.*Up"; then

        pass "Qdrant: Vector database running"    else    exit 1

    else

        fail "Qdrant: Vector database not running"        warn "GPU Memory: ${GPU_MEM_GB}GB (May need CPU fallback)"fi

    fi

else    fi

    fail "Docker: Not installed or not accessible"else

fi    fail "GPU: NVIDIA GPU not detected"

fi

# Python Environment Check

if [ -d ".venv" ]; then# CPU Check

    if [ -f ".venv/bin/activate" ]; thenCPU_CORES=$(nproc)

        pass "Python: Virtual environment ready"if [ "$CPU_CORES" -ge 16 ]; then

    else    pass "CPU Cores: $CPU_CORES (Excellent for parallel processing)"

        fail "Python: Virtual environment corrupted"else

    fi    warn "CPU Cores: $CPU_CORES (Consider upgrading for better performance)"

elsefi

    fail "Python: No virtual environment found"

fiecho ""



echo ""# Storage Check

echo "💾 Storage:"

# Quick Functional Testsecho "============"

echo "🧪 Functional Tests:"

echo "==================="# H: drive check

if [ -d "/mnt/h/ollama-models" ]; then

# Ollama API test    H_DRIVE_SIZE=$(df -h /mnt/h | tail -1 | awk '{print $2}')

if curl -s http://localhost:11434/api/tags > /dev/null; then    H_DRIVE_USED=$(du -sh /mnt/h/ollama-models | cut -f1)

    pass "Ollama API: Responding"    pass "H: Drive Models: $H_DRIVE_USED / $H_DRIVE_SIZE"

elseelse

    fail "Ollama API: Not responding"    fail "H: Drive not accessible at /mnt/h/ollama-models"

fifi



# Qdrant API test  # Project disk usage

if curl -s http://localhost:6333/health > /dev/null; thenPROJECT_SIZE=$(du -sh . --exclude=.venv --exclude=.git | cut -f1)

    pass "Qdrant API: Responding"pass "Project Size: $PROJECT_SIZE (YAGNI compliance)"

else

    fail "Qdrant API: Not responding"echo ""

fi

# Services Check

echo ""echo "🚀 Services:"

echo "============"

# Summary

echo "📋 Health Check Summary:"# Ollama Check

echo "========================"if pgrep -f ollama > /dev/null; then

echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"    if curl -s http://localhost:11434/api/tags > /dev/null; then

echo -e "${RED}Failed: $TESTS_FAILED${NC}"        MODEL_COUNT=$(ollama list | grep -v NAME | wc -l)

        pass "Ollama: Running with $MODEL_COUNT models"

if [ "$TESTS_FAILED" -eq 0 ]; then    else

    echo ""        warn "Ollama: Process running but API not responding"

    echo -e "${GREEN}🎉 System is healthy and ready for DocuMind development!${NC}"    fi

    exit 0else

else    fail "Ollama: Service not running"

    echo ""fi

    echo -e "${YELLOW}⚠️ Some issues detected. Review failed tests above.${NC}"

    exit 1# Docker Check

fiif docker --version > /dev/null 2>&1; then
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