#!/usr/bin/env bash
# Simple integration test for DocuMind services
set -e

# Colors
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

success() { echo -e "${GREEN}✅${NC} $*"; }
error() { echo -e "${RED}❌${NC} $*"; }
log() { echo -e "${BLUE}[Test]${NC} $*"; }

echo -e "${BLUE}🧪 DocuMind Quick Health Check${NC}"
echo ""

# Test 1: Qdrant
log "Testing Qdrant..."
if timeout 5 curl -s http://localhost:6333/ >/dev/null 2>&1; then
    success "Qdrant is running"
else
    error "Qdrant is not responding"
fi

# Test 2: Python RAG API
log "Testing Python RAG API..."
if timeout 5 curl -s http://localhost:7001/healthz >/dev/null 2>&1; then
    success "Python RAG API is running"
else
    error "Python RAG API is not responding"
fi

# Test 3: .NET API
log "Testing .NET DocuMind API..."
if timeout 5 curl -s http://localhost:5266/healthz >/dev/null 2>&1; then
    success ".NET API is running"
else
    error ".NET API is not responding"
fi

echo ""
log "Testing basic functionality..."

# Test 4: Simple query
if timeout 10 curl -s "http://localhost:5266/ask?q=test" >/dev/null 2>&1; then
    success "Basic query works"
else
    error "Basic query failed"
fi

echo ""
success "Quick health check complete!"
echo ""
log "For comprehensive tests run: ./scripts/dev/test.sh --full"
log "Service URLs:"
echo "  Qdrant:           http://localhost:6333/dashboard"
echo "  Python RAG API:   http://localhost:7001"
echo "  .NET API:         http://localhost:5266"
echo "  Swagger UI:       http://localhost:5266/swagger"
