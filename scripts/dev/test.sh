#!/usr/bin/env bash
# Integration test suite for DocuMind
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Service URLs
readonly QDRANT_URL="http://localhost:6333"
readonly RAG_URL="http://localhost:7001"
readonly API_URL="http://localhost:5266"

# Colors
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log() { echo -e "${BLUE}[Test]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
error() { echo -e "${RED}❌${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️${NC}  $*"; }

# Test tracking
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="${3:-0}"

    ((TESTS_RUN++))
    log "Running: $test_name"

    # Capture both output and exit status
    local output
    local status
    output=$(eval "$test_command" 2>/dev/null)
    status=$?

    if [[ $status -eq $expected_status ]]; then
        success "$test_name"
        ((TESTS_PASSED++))
        return 0
    else
        error "$test_name (exit code: $status, expected: $expected_status)"
        if [[ -n "$output" ]]; then
            echo "  Output: $output"
        fi
        ((TESTS_FAILED++))
        return 1
    fi
}

test_service_health() {
    log "Testing service health endpoints..."

    run_test "Qdrant health" "curl -sf '$QDRANT_URL/'"
    run_test "Python RAG health" "curl -sf '$RAG_URL/healthz'"
    run_test ".NET API health" "curl -sf '$API_URL/healthz'"
}

test_rag_api() {
    log "Testing Python RAG API functionality..."

    # Test basic query
    run_test "RAG basic query" "curl -sf '$RAG_URL/ask?q=test'"

    # Test POST query
    local post_data='{"q": "What is a test?"}'
    run_test "RAG POST query" "curl -sf -X POST -H 'Content-Type: application/json' -d '$post_data' '$RAG_URL/ask'"
}

test_dotnet_api() {
    log "Testing .NET DocuMind API functionality..."

    # Test basic query
    run_test "DocuMind basic query" "curl -sf '$API_URL/ask?q=test'"

    # Test enhanced orchestrator
    local complex_data='{"q": "Analyze the technical implications of our backup strategy"}'
    run_test "DocuMind complex query" "curl -sf -X POST -H 'Content-Type: application/json' -d '$complex_data' '$API_URL/ask'"

    # Test Swagger endpoint
    run_test "Swagger documentation" "curl -sf '$API_URL/swagger/v1/swagger.json'"
}

test_routing_logic() {
    log "Testing intelligent query routing..."

    # Simple query (should route locally)
    local simple_response=$(curl -sf "$API_URL/ask?q=What%20is%20the%20backup%20policy?" | jq -r '.route // "unknown"' 2>/dev/null)
    if [[ "$simple_response" == "local" ]]; then
        success "Simple query routing (local)"
        ((TESTS_PASSED++))
    else
        error "Simple query routing (got: $simple_response, expected: local)"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    # Complex query (should route to cloud)
    local complex_data='{"q": "Conduct a comprehensive risk analysis of our disaster recovery infrastructure with strategic recommendations"}'
    local complex_response=$(curl -sf -X POST -H "Content-Type: application/json" -d "$complex_data" "$API_URL/ask" | jq -r '.route // "unknown"' 2>/dev/null)
    if [[ "$complex_response" == "cloud" ]]; then
        success "Complex query routing (cloud)"
        ((TESTS_PASSED++))
    else
        error "Complex query routing (got: $complex_response, expected: cloud)"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
}

test_performance() {
    log "Testing API performance..."

    # Test response times
    local start_time=$(date +%s%N)
    curl -sf "$RAG_URL/healthz" >/dev/null 2>&1
    local end_time=$(date +%s%N)
    local duration_ms=$(( (end_time - start_time) / 1000000 ))

    if [[ $duration_ms -lt 1000 ]]; then
        success "RAG API response time: ${duration_ms}ms"
        ((TESTS_PASSED++))
    else
        warn "RAG API slow response: ${duration_ms}ms"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    # Test .NET API response time
    start_time=$(date +%s%N)
    curl -sf "$API_URL/healthz" >/dev/null 2>&1
    end_time=$(date +%s%N)
    duration_ms=$(( (end_time - start_time) / 1000000 ))

    if [[ $duration_ms -lt 2000 ]]; then
        success ".NET API response time: ${duration_ms}ms"
        ((TESTS_PASSED++))
    else
        warn ".NET API slow response: ${duration_ms}ms"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
}

test_error_handling() {
    log "Testing error handling..."

    # Test invalid endpoints
    run_test "Invalid RAG endpoint" "curl -sf '$RAG_URL/invalid'" 1
    run_test "Invalid API endpoint" "curl -sf '$API_URL/invalid'" 1

    # Test malformed requests
    run_test "Malformed JSON" "curl -sf -X POST -H 'Content-Type: application/json' -d '{invalid}' '$API_URL/ask'" 1
}

check_prerequisites() {
    log "Checking test prerequisites..."

    # Check if jq is available
    if ! command -v jq >/dev/null 2>&1; then
        warn "jq not found. Installing for JSON parsing..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v brew >/dev/null 2>&1; then
            brew install jq
        else
            error "Please install jq for JSON parsing"
            exit 1
        fi
    fi

    # Check if services are running
    if ! curl -sf "$QDRANT_URL/" >/dev/null 2>&1; then
        error "Qdrant not running. Start with: ./scripts/start.sh"
        exit 1
    fi

    if ! curl -sf "$RAG_URL/healthz" >/dev/null 2>&1; then
        error "Python RAG API not running. Start with: ./scripts/start.sh"
        exit 1
    fi

    if ! curl -sf "$API_URL/healthz" >/dev/null 2>&1; then
        error ".NET API not running. Start with: ./scripts/start.sh"
        exit 1
    fi

    success "All prerequisites met"
}

show_results() {
    echo
    echo -e "${BLUE}==================== TEST RESULTS ====================${NC}"
    echo -e "Total Tests:  $TESTS_RUN"
    echo -e "${GREEN}Passed:       $TESTS_PASSED${NC}"
    echo -e "${RED}Failed:       $TESTS_FAILED${NC}"
    echo -e "Success Rate: $((TESTS_PASSED * 100 / TESTS_RUN))%"
    echo -e "${BLUE}====================================================${NC}"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        success "All tests passed! 🎉"
        return 0
    else
        error "$TESTS_FAILED test(s) failed"
        return 1
    fi
}

show_help() {
    cat << EOF
DocuMind Integration Test Suite

Usage: $0 [OPTIONS]

Options:
    --help          Show this help message
    --health-only   Run only health checks
    --performance   Run performance tests
    --routing       Test query routing logic
    --full          Run all tests (default)

Prerequisites:
    - All services must be running (./scripts/start.sh)
    - jq must be installed for JSON parsing

Test Categories:
    - Service health checks
    - API functionality tests
    - Query routing validation
    - Performance benchmarks
    - Error handling

Examples:
    $0                  # Run all tests
    $0 --health-only    # Quick health check
    $0 --performance    # Performance benchmarks
EOF
}

main() {
    local test_mode="full"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --health-only)
                test_mode="health"
                shift
                ;;
            --performance)
                test_mode="performance"
                shift
                ;;
            --routing)
                test_mode="routing"
                shift
                ;;
            --full)
                test_mode="full"
                shift
                ;;
            *)
                warn "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo -e "${GREEN}"
    cat << 'EOF'
   🧪 DocuMind Integration Tests

EOF
    echo -e "${NC}"

    # Check prerequisites
    check_prerequisites

    # Run tests based on mode
    case "$test_mode" in
        "health")
            test_service_health
            ;;
        "performance")
            test_performance
            ;;
        "routing")
            test_routing_logic
            ;;
        "full")
            test_service_health
            test_rag_api
            test_dotnet_api
            test_routing_logic
            test_performance
            test_error_handling
            ;;
    esac

    # Show results
    show_results
}

main "$@"
