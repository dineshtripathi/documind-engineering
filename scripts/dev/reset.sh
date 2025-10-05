#!/usr/bin/env bash
# Development environment reset script
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log() { echo -e "${BLUE}[Dev Reset]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️${NC}  $*"; }

show_help() {
    cat << EOF
Development Environment Reset

Usage: $0 [OPTIONS]

Options:
    --help          Show this help message
    --full          Full reset including models and data
    --soft          Soft reset (keep models and data)

This script will:
1. Stop all running services
2. Clean containers and volumes
3. Rebuild .NET solution
4. Reset development data (optional)
5. Restart services

Examples:
    $0              # Standard reset
    $0 --full       # Full reset including models
    $0 --soft       # Keep everything, just restart
EOF
}

main() {
    local reset_type="standard"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --full)
                reset_type="full"
                shift
                ;;
            --soft)
                reset_type="soft"
                shift
                ;;
            *)
                warn "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    cd "$ROOT_DIR"

    log "Starting development environment reset ($reset_type mode)..."

    # 1. Stop all services
    log "Stopping services..."
    if [[ "$reset_type" == "full" ]]; then
        ./scripts/stop.sh --clean
    else
        ./scripts/stop.sh
    fi

    # 2. Clean build artifacts
    if [[ "$reset_type" != "soft" ]]; then
        log "Cleaning build artifacts..."

        # .NET clean
        if [[ -f "src/dotnet/DocuMind.Api.sln" ]]; then
            cd src/dotnet
            dotnet clean DocuMind.Api.sln
            cd "$ROOT_DIR"
        fi

        # Python cache clean
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true

        # Remove logs
        rm -rf .run/logs/* 2>/dev/null || true
    fi

    # 3. Full reset specific actions
    if [[ "$reset_type" == "full" ]]; then
        log "Performing full reset..."

        # Remove model cache (they'll be re-downloaded)
        rm -rf ~/.cache/huggingface 2>/dev/null || true

        # Reset data directories
        rm -rf data/docs/* data/staging/* 2>/dev/null || true

        warn "Model cache cleared - models will be re-downloaded on next start"
    fi

    # 4. Rebuild solution
    if [[ "$reset_type" != "soft" ]]; then
        log "Rebuilding .NET solution..."
        cd src/dotnet
        dotnet restore DocuMind.Api.sln
        dotnet build DocuMind.Api.sln --configuration Release
        cd "$ROOT_DIR"
    fi

    # 5. Restart services
    log "Restarting services..."
    sleep 2

    if [[ "$reset_type" == "full" ]]; then
        ./scripts/start.sh --background
    else
        ./scripts/start.sh --background --no-models
    fi

    # 6. Wait and check status
    log "Waiting for services to start..."
    sleep 5

    # Test services
    local all_good=true

    if ! curl -sf http://localhost:6333/ >/dev/null 2>&1; then
        warn "Qdrant not responding"
        all_good=false
    fi

    if ! curl -sf http://localhost:7001/healthz >/dev/null 2>&1; then
        warn "Python RAG API not responding"
        all_good=false
    fi

    if ! curl -sf http://localhost:5266/healthz >/dev/null 2>&1; then
        warn ".NET API not responding"
        all_good=false
    fi

    if [[ "$all_good" == "true" ]]; then
        success "Development environment reset complete!"
        success "All services are running"
        echo
        log "Quick test: curl \"http://localhost:5266/ask?q=test\""
        log "Logs: tail -f .run/logs/*.log"
    else
        warn "Some services may not be ready yet"
        log "Check logs: tail -f .run/logs/*.log"
        log "Manual start: ./scripts/start.sh"
    fi
}

main "$@"
