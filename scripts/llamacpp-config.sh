#!/bin/bash
# llama.cpp Configuration Script for DocuMind Engineering
# Hardware-optimized for RTX 5090 + 24-core CPU + 94GB RAM

set -euo pipefail

# Configuration
MODELS_DIR="/home/dinesh/documind-engineering/models/gguf"
LLAMA_SERVER_PORT=8081
CPU_THREADS=24
GPU_LAYERS=50  # Adjust based on model size and VRAM
CONTEXT_SIZE=8192
BATCH_SIZE=2048

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if llama.cpp is installed
check_llamacpp() {
    if ! command -v llama-cli &> /dev/null; then
        log_error "llama.cpp not found. Please install first."
        exit 1
    fi
    
    log_success "llama.cpp found: $(llama-cli --version | head -1)"
}

# List available models
list_models() {
    log_info "Available GGUF models:"
    if [ -d "$MODELS_DIR" ] && [ "$(ls -A $MODELS_DIR 2>/dev/null)" ]; then
        ls -lh "$MODELS_DIR"/*.gguf 2>/dev/null || log_warning "No .gguf files found"
    else
        log_warning "No models directory or no models found"
        log_info "Creating models directory: $MODELS_DIR"
        mkdir -p "$MODELS_DIR"
    fi
}

# Test model inference
test_model() {
    local model_file="$1"
    
    if [ ! -f "$model_file" ]; then
        log_error "Model file not found: $model_file"
        return 1
    fi
    
    log_info "Testing model: $(basename "$model_file")"
    log_info "Using $CPU_THREADS CPU threads, $GPU_LAYERS GPU layers"
    
    # Test with a simple prompt
    echo -e "\n${YELLOW}Testing with prompt: 'What is artificial intelligence?'${NC}\n"
    
    llama-cli \
        --model "$model_file" \
        --threads "$CPU_THREADS" \
        --n-gpu-layers "$GPU_LAYERS" \
        --ctx-size "$CONTEXT_SIZE" \
        --batch-size "$BATCH_SIZE" \
        --prompt "What is artificial intelligence? Give a brief explanation." \
        --n-predict 200 \
        --temp 0.7 \
        --seed 42
}

# Start llama.cpp server
start_server() {
    local model_file="$1"
    
    if [ ! -f "$model_file" ]; then
        log_error "Model file not found: $model_file"
        return 1
    fi
    
    log_info "Starting llama.cpp server on port $LLAMA_SERVER_PORT"
    log_info "Model: $(basename "$model_file")"
    log_info "Threads: $CPU_THREADS, GPU layers: $GPU_LAYERS"
    
    llama-server \
        --model "$model_file" \
        --host 0.0.0.0 \
        --port "$LLAMA_SERVER_PORT" \
        --threads "$CPU_THREADS" \
        --n-gpu-layers "$GPU_LAYERS" \
        --ctx-size "$CONTEXT_SIZE" \
        --batch-size "$BATCH_SIZE" \
        --log-disable \
        &
    
    local server_pid=$!
    log_success "Server started with PID: $server_pid"
    log_info "Server accessible at: http://localhost:$LLAMA_SERVER_PORT"
    log_info "To stop server: kill $server_pid"
    
    return 0
}

# Benchmark model performance
benchmark_model() {
    local model_file="$1"
    
    if [ ! -f "$model_file" ]; then
        log_error "Model file not found: $model_file"
        return 1
    fi
    
    log_info "Benchmarking model: $(basename "$model_file")"
    
    llama-bench \
        --model "$model_file" \
        --threads "$CPU_THREADS" \
        --n-gpu-layers "$GPU_LAYERS" \
        --ctx-size "$CONTEXT_SIZE" \
        --batch-size "$BATCH_SIZE"
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [MODEL_FILE]"
    echo ""
    echo "Commands:"
    echo "  check          - Check llama.cpp installation"
    echo "  list           - List available models"
    echo "  test MODEL     - Test model inference"
    echo "  server MODEL   - Start llama.cpp server"
    echo "  bench MODEL    - Benchmark model performance"
    echo "  help           - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 check"
    echo "  $0 list"
    echo "  $0 test $MODELS_DIR/llama-3.1-8b-instruct-q4_k_m.gguf"
    echo "  $0 server $MODELS_DIR/llama-3.1-8b-instruct-q4_k_m.gguf"
    echo "  $0 bench $MODELS_DIR/llama-3.1-8b-instruct-q4_k_m.gguf"
}

# Main execution
main() {
    case "${1:-help}" in
        "check")
            check_llamacpp
            ;;
        "list")
            check_llamacpp
            list_models
            ;;
        "test")
            if [ $# -lt 2 ]; then
                log_error "Model file required for test command"
                show_usage
                exit 1
            fi
            check_llamacpp
            test_model "$2"
            ;;
        "server")
            if [ $# -lt 2 ]; then
                log_error "Model file required for server command"
                show_usage
                exit 1
            fi
            check_llamacpp
            start_server "$2"
            ;;
        "bench")
            if [ $# -lt 2 ]; then
                log_error "Model file required for bench command"
                show_usage
                exit 1
            fi
            check_llamacpp
            benchmark_model "$2"
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

main "$@"