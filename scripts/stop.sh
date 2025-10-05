#!/usr/bin/env bash
# DocuMind Service Manager - Stop all services
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log() { echo -e "${BLUE}[DocuMind]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️${NC}  $*"; }

show_help() {
    cat << EOF
DocuMind Service Stopper

Usage: $0 [OPTIONS]

Options:
    --help          Show this help message
    --hard          Force kill all processes
    --clean         Remove all containers and volumes

Examples:
    $0              # Stop all services gracefully
    $0 --hard       # Force kill all processes
    $0 --clean      # Stop and remove all data
EOF
}

stop_background_services() {
    log "Stopping background services..."

    local pids_dir="$ROOT_DIR/.run/pids"

    # Stop Python RAG API
    if [[ -f "$pids_dir/rag.pid" ]]; then
        local rag_pid=$(cat "$pids_dir/rag.pid")
        if ps -p "$rag_pid" >/dev/null 2>&1; then
            log "Stopping Python RAG API (PID: $rag_pid)"
            kill "$rag_pid" 2>/dev/null || kill -9 "$rag_pid" 2>/dev/null || true
        fi
        rm -f "$pids_dir/rag.pid"
    fi

    # Stop .NET API
    if [[ -f "$pids_dir/dotnet.pid" ]]; then
        local dotnet_pid=$(cat "$pids_dir/dotnet.pid")
        if ps -p "$dotnet_pid" >/dev/null 2>&1; then
            log "Stopping .NET API (PID: $dotnet_pid)"
            kill "$dotnet_pid" 2>/dev/null || kill -9 "$dotnet_pid" 2>/dev/null || true
        fi
        rm -f "$pids_dir/dotnet.pid"
    fi
}

stop_all_processes() {
    local force="$1"

    log "Stopping all DocuMind processes..."

    # Stop uvicorn processes (Python RAG API)
    local uvicorn_pids=$(pgrep -f "uvicorn.*rag_api" 2>/dev/null || true)
    if [[ -n "$uvicorn_pids" ]]; then
        log "Stopping uvicorn RAG API processes..."
        if [[ "$force" == "true" ]]; then
            pkill -9 -f "uvicorn.*rag_api" 2>/dev/null || true
        else
            pkill -TERM -f "uvicorn.*rag_api" 2>/dev/null || true
            sleep 2
            pkill -9 -f "uvicorn.*rag_api" 2>/dev/null || true
        fi
    fi

    # Stop .NET processes
    local dotnet_pids=$(pgrep -f "dotnet.*DocuMind.Api" 2>/dev/null || true)
    if [[ -n "$dotnet_pids" ]]; then
        log "Stopping .NET DocuMind API processes..."
        if [[ "$force" == "true" ]]; then
            pkill -9 -f "dotnet.*DocuMind.Api" 2>/dev/null || true
        else
            pkill -TERM -f "dotnet.*DocuMind.Api" 2>/dev/null || true
            sleep 2
            pkill -9 -f "dotnet.*DocuMind.Api" 2>/dev/null || true
        fi
    fi

    # Stop any remaining processes on our ports
    for port in 7001 5266; do
        local port_pid=$(lsof -ti:$port 2>/dev/null || true)
        if [[ -n "$port_pid" ]]; then
            log "Stopping process on port $port (PID: $port_pid)"
            if [[ "$force" == "true" ]]; then
                kill -9 "$port_pid" 2>/dev/null || true
            else
                kill "$port_pid" 2>/dev/null || true
                sleep 1
                kill -9 "$port_pid" 2>/dev/null || true
            fi
        fi
    done
}

stop_docker_services() {
    local clean="$1"

    log "Stopping Docker services..."

    cd "$ROOT_DIR"

    if [[ "$clean" == "true" ]]; then
        log "Removing containers and volumes..."
        docker compose -f docker/compose.yml down -v --remove-orphans 2>/dev/null || true

        # Clean up any orphaned qdrant containers
        docker ps -a --format "{{.Names}}" | grep -E "^qdrant" | xargs -r docker rm -f 2>/dev/null || true

        # Remove Qdrant data volume if it exists
        docker volume ls -q | grep -E "(qdrant|documind)" | xargs -r docker volume rm 2>/dev/null || true

        success "Docker cleanup complete"
    else
        docker compose -f docker/compose.yml down 2>/dev/null || true
        success "Docker services stopped"
    fi
}

check_services() {
    log "Checking remaining services..."

    local any_running=false

    # Check ports
    for port in 6333 7001 5266; do
        if lsof -i:$port >/dev/null 2>&1; then
            warn "Port $port still in use"
            any_running=true
        fi
    done

    # Check processes
    if pgrep -f "uvicorn.*rag_api" >/dev/null 2>&1; then
        warn "Python RAG API still running"
        any_running=true
    fi

    if pgrep -f "dotnet.*DocuMind.Api" >/dev/null 2>&1; then
        warn ".NET API still running"
        any_running=true
    fi

    if [[ "$any_running" == "false" ]]; then
        success "All services stopped successfully"
    else
        warn "Some services may still be running. Use --hard to force stop."
    fi
}

cleanup_temp_files() {
    log "Cleaning up temporary files..."

    # Remove PID files
    rm -rf "$ROOT_DIR/.run/pids" 2>/dev/null || true

    # Clean up logs (optional)
    if [[ -d "$ROOT_DIR/.run/logs" ]]; then
        log "Log files preserved in .run/logs/"
    fi

    # Remove any Python cache
    find "$ROOT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$ROOT_DIR" -name "*.pyc" -delete 2>/dev/null || true
}

main() {
    local force=false
    local clean=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --hard)
                force=true
                shift
                ;;
            --clean)
                clean=true
                shift
                ;;
            *)
                warn "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo -e "${BLUE}"
    log "Stopping DocuMind services..."
    echo -e "${NC}"

    # Stop services in order
    stop_background_services
    stop_all_processes "$force"
    stop_docker_services "$clean"
    cleanup_temp_files

    # Wait a moment for processes to fully stop
    sleep 1

    # Check final status
    check_services

    echo -e "${GREEN}"
    success "DocuMind shutdown complete"
    echo -e "${NC}"

    if [[ "$clean" == "true" ]]; then
        log "All data has been removed. Run ./scripts/setup.sh to reinitialize."
    else
        log "To restart services: ./scripts/start.sh"
    fi
}

main "$@"
