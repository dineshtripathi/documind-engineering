#!/usr/bin/env bash
# DocuMind Service Manager - Start all services
set -euo pipefail

# --- Configuration ---
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly CONDA_ENV="documind"
readonly RAG_HOST="127.0.0.1"
readonly RAG_PORT="7001"
readonly DOTNET_PORT="5266"
readonly QDRANT_PORT="6333"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# --- Helper Functions ---
log() { echo -e "${BLUE}[DocuMind]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️${NC}  $*"; }

show_help() {
    cat << EOF
DocuMind Service Manager

Usage: $0 [OPTIONS]

Options:
    --help              Show this help message
    --python-only       Start only Python RAG API
    --dotnet-only       Start only .NET API
    --no-models         Skip model download check
    --background        Run services in background

Examples:
    $0                  # Start all services (hybrid mode)
    $0 --python-only    # Start only RAG API
    $0 --background     # Run in background with logs

Services:
    Qdrant:             http://localhost:$QDRANT_PORT/dashboard
    Python RAG API:     http://localhost:$RAG_PORT/healthz
    .NET DocuMind API:  http://localhost:$DOTNET_PORT/swagger
EOF
}

check_dependencies() {
    log "Checking dependencies..."

    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        warn "Docker not found. Run: ./scripts/setup.sh"
        return 1
    fi

    # Check .NET
    if ! command -v dotnet >/dev/null 2>&1; then
        warn ".NET SDK not found. Run: ./scripts/setup.sh"
        return 1
    fi

    # Check Python environment
    local python_ready=false
    if command -v conda >/dev/null 2>&1 && conda env list | grep -q "^${CONDA_ENV} "; then
        python_ready=true
    elif [[ -d "$ROOT_DIR/.venv" ]]; then
        python_ready=true
    elif command -v python3 >/dev/null 2>&1; then
        python_ready=true
    fi

    if [[ "$python_ready" != "true" ]]; then
        warn "Python environment not found. Run: ./scripts/setup.sh"
        return 1
    fi

    success "Dependencies check passed"
}

setup_python_env() {
    # Activate Python environment
    if command -v conda >/dev/null 2>&1 && conda env list | grep -q "^${CONDA_ENV} "; then
        log "Activating conda environment: $CONDA_ENV"
        eval "$(conda shell.bash hook)"
        conda activate "$CONDA_ENV"
    elif [[ -d "$ROOT_DIR/.venv" ]]; then
        log "Activating virtual environment"
        source "$ROOT_DIR/.venv/bin/activate"
    fi

    export PYTHONPATH="$ROOT_DIR"
    export QDRANT_URL="http://${RAG_HOST}:${QDRANT_PORT}"
}

start_qdrant() {
    log "Starting Qdrant vector database..."

    cd "$ROOT_DIR"

    # Check if already running
    if curl -sf "http://${RAG_HOST}:${QDRANT_PORT}/" >/dev/null 2>&1; then
        success "Qdrant already running"
        return
    fi

    # Start via Docker Compose
    docker compose -f docker/compose.yml up -d

    # Wait for Qdrant to be ready
    log "Waiting for Qdrant to be ready..."
    for i in {1..30}; do
        if curl -sf "http://${RAG_HOST}:${QDRANT_PORT}/" >/dev/null 2>&1; then
            success "Qdrant ready at http://${RAG_HOST}:${QDRANT_PORT}"
            return
        fi
        sleep 1
    done

    warn "Qdrant took longer than expected to start"
}

check_models() {
    local skip_models="$1"

    if [[ "$skip_models" == "true" ]]; then
        return
    fi

    log "Checking AI models..."

    # Check embedding model
    python3 -c "
from sentence_transformers import SentenceTransformer
try:
    SentenceTransformer('BAAI/bge-m3')
    print('✅ Embedding model ready')
except:
    print('⚠️  Embedding model not found, downloading...')
    SentenceTransformer('BAAI/bge-m3')
" 2>/dev/null || warn "Embedding model check failed"

    # Check Ollama model
    if command -v ollama >/dev/null 2>&1; then
        if ! ollama list 2>/dev/null | grep -q "phi3.5:3.8b-mini-instruct-q4_0"; then
            log "Downloading Ollama model..."
            ollama pull phi3.5:3.8b-mini-instruct-q4_0 || warn "Ollama model download failed"
        else
            success "Ollama model ready"
        fi
    fi
}

start_python_rag() {
    local background="$1"

    log "Starting Python RAG API..."

    # Check if already running
    if curl -sf "http://${RAG_HOST}:${RAG_PORT}/healthz" >/dev/null 2>&1; then
        success "Python RAG API already running"
        return
    fi

    cd "$ROOT_DIR"
    setup_python_env

    if [[ "$background" == "true" ]]; then
        mkdir -p .run/{logs,pids}
        log "Starting RAG API in background..."
        (uvicorn src.python.services.rag_api.app:app \
            --host "$RAG_HOST" \
            --port "$RAG_PORT" \
            --reload > .run/logs/rag.log 2>&1) &
        echo $! > .run/pids/rag.pid

        # Wait for startup
        for i in {1..20}; do
            if curl -sf "http://${RAG_HOST}:${RAG_PORT}/healthz" >/dev/null 2>&1; then
                success "Python RAG API ready at http://${RAG_HOST}:${RAG_PORT}"
                return
            fi
            sleep 1
        done
        warn "Python RAG API took longer than expected to start"
    else
        log "Starting RAG API (foreground)..."
        log "API will be available at: http://${RAG_HOST}:${RAG_PORT}"
        log "Press Ctrl+C to stop"
        uvicorn src.python.services.rag_api.app:app \
            --host "$RAG_HOST" \
            --port "$RAG_PORT" \
            --reload
    fi
}

start_dotnet_api() {
    local background="$1"

    log "Starting .NET DocuMind API..."

    # Check if already running
    if curl -sf "http://${RAG_HOST}:${DOTNET_PORT}/healthz" >/dev/null 2>&1; then
        success ".NET API already running"
        return
    fi

    cd "$ROOT_DIR/src/dotnet/DocuMind.Api/DocuMind.Api"

    # Set environment variables
    export Rag__BaseUrl="http://${RAG_HOST}:${RAG_PORT}"
    export FeatureFlags__UseRagFirst=true
    export FeatureFlags__RagRequired=false

    if [[ "$background" == "true" ]]; then
        mkdir -p "$ROOT_DIR/.run"/{logs,pids}
        log "Starting .NET API in background..."
        (dotnet run > "$ROOT_DIR/.run/logs/dotnet.log" 2>&1) &
        echo $! > "$ROOT_DIR/.run/pids/dotnet.pid"

        # Wait for startup
        for i in {1..30}; do
            if curl -sf "http://${RAG_HOST}:${DOTNET_PORT}/healthz" >/dev/null 2>&1; then
                success ".NET API ready at http://${RAG_HOST}:${DOTNET_PORT}"
                return
            fi
            sleep 1
        done
        warn ".NET API took longer than expected to start"
    else
        log "Starting .NET API (foreground)..."
        log "API will be available at: http://${RAG_HOST}:${DOTNET_PORT}"
        log "Swagger UI: http://${RAG_HOST}:${DOTNET_PORT}/swagger"
        log "Press Ctrl+C to stop"
        dotnet run
    fi
}

show_status() {
    echo -e "${GREEN}"
    cat << 'EOF'
   🚀 DocuMind Services Status

EOF
    echo -e "${NC}"

    # Check Qdrant
    if curl -sf "http://${RAG_HOST}:${QDRANT_PORT}/" >/dev/null 2>&1; then
        success "Qdrant:            http://localhost:$QDRANT_PORT/dashboard"
    else
        warn "Qdrant:            Not running"
    fi

    # Check Python RAG API
    if curl -sf "http://${RAG_HOST}:${RAG_PORT}/healthz" >/dev/null 2>&1; then
        success "Python RAG API:    http://localhost:$RAG_PORT"
    else
        warn "Python RAG API:    Not running"
    fi

    # Check .NET API
    if curl -sf "http://${RAG_HOST}:${DOTNET_PORT}/healthz" >/dev/null 2>&1; then
        success ".NET DocuMind API: http://localhost:$DOTNET_PORT"
        success "Swagger UI:        http://localhost:$DOTNET_PORT/swagger"
    else
        warn ".NET DocuMind API: Not running"
    fi

    echo
    log "Quick test commands:"
    echo "  curl http://localhost:$RAG_PORT/healthz"
    echo "  curl http://localhost:$DOTNET_PORT/healthz"
    echo '  curl "http://localhost:5266/ask?q=What%20is%20the%20backup%20policy?"'
}

cleanup() {
    if [[ -f "$ROOT_DIR/.run/pids/rag.pid" ]]; then
        kill $(cat "$ROOT_DIR/.run/pids/rag.pid") 2>/dev/null || true
        rm -f "$ROOT_DIR/.run/pids/rag.pid"
    fi
    if [[ -f "$ROOT_DIR/.run/pids/dotnet.pid" ]]; then
        kill $(cat "$ROOT_DIR/.run/pids/dotnet.pid") 2>/dev/null || true
        rm -f "$ROOT_DIR/.run/pids/dotnet.pid"
    fi
}

# --- Main Function ---
main() {
    local python_only=false
    local dotnet_only=false
    local skip_models=false
    local background=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --python-only)
                python_only=true
                shift
                ;;
            --dotnet-only)
                dotnet_only=true
                shift
                ;;
            --no-models)
                skip_models=true
                shift
                ;;
            --background)
                background=true
                shift
                ;;
            *)
                warn "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi

    # Setup cleanup on exit
    trap cleanup EXIT

    # Start services
    start_qdrant
    check_models "$skip_models"

    if [[ "$dotnet_only" != "true" ]]; then
        if [[ "$background" == "true" ]]; then
            start_python_rag "$background"
        elif [[ "$python_only" == "true" ]]; then
            start_python_rag "false"
            exit 0
        else
            start_python_rag "$background"
        fi
    fi

    if [[ "$python_only" != "true" ]]; then
        start_dotnet_api "$background"
    fi

    # Show final status
    if [[ "$background" == "true" ]]; then
        sleep 2
        show_status
        echo
        success "All services running in background"
        log "View logs: tail -f .run/logs/*.log"
        log "Stop services: ./scripts/stop.sh"
    fi
}

# Run main function
main "$@"
