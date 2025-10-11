#!/bin/bash
# 🔄 Model Management & Synchronization
# Handles local and cloud model operations

set -e

echo "🔄 DocuMind Model Management"
echo "============================"

# Configuration
OLLAMA_MODELS_DIR="/mnt/h/ollama-models"
LOCAL_MODELS=("llama3.1:70b" "llama3.1:8b" "phi3.5")

# Functions
check_model_exists() {
    local model=$1
    if ollama list | grep -q "$model"; then
        return 0
    else
        return 1
    fi
}

sync_local_models() {
    echo "🤖 Syncing local Ollama models..."
    
    for model in "${LOCAL_MODELS[@]}"; do
        if check_model_exists "$model"; then
            echo "✅ $model - Available"
        else
            echo "⚠️ $model - Missing"
            read -p "Download $model? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "📥 Downloading $model..."
                ollama pull "$model"
            fi
        fi
    done
}

check_storage_space() {
    echo "📊 Storage Analysis:"
    echo "H: drive usage: $(du -sh $OLLAMA_MODELS_DIR 2>/dev/null || echo 'Not accessible')"
    echo "Available space: $(df -h /mnt/h 2>/dev/null | tail -1 | awk '{print $4}' || echo 'Unknown')"
    echo ""
}

optimize_models() {
    echo "⚡ Model Optimization for High-End Hardware:"
    echo "- 192GB RAM: Can load all 3 models simultaneously"
    echo "- 24GB VRAM: Primary model (70B) fits in GPU memory"  
    echo "- 22 cores: Parallel processing enabled"
    echo ""
    
    # Set optimal environment
    export OLLAMA_NUM_PARALLEL=4
    export OLLAMA_MAX_LOADED_MODELS=3
    
    echo "✅ Environment optimized for concurrent model loading"
}

test_models() {
    echo "🧪 Testing model responses..."
    
    for model in "${LOCAL_MODELS[@]}"; do
        if check_model_exists "$model"; then
            echo "Testing $model..."
            response=$(ollama run "$model" "Hello, respond with just 'OK'" --timeout 10s 2>/dev/null || echo "TIMEOUT")
            if [[ "$response" == *"OK"* ]]; then
                echo "✅ $model - Responsive"
            else
                echo "⚠️ $model - Slow/Unresponsive"
            fi
        fi
    done
}

# Main execution
case "${1:-sync}" in
    "sync")
        check_storage_space
        sync_local_models
        optimize_models
        ;;
    "test")
        test_models
        ;;
    "optimize")
        optimize_models
        ;;
    "status")
        check_storage_space
        echo "📋 Local Models:"
        ollama list
        ;;
    *)
        echo "Usage: $0 {sync|test|optimize|status}"
        echo ""
        echo "Commands:"
        echo "  sync     - Sync and download missing models"
        echo "  test     - Test model responsiveness"  
        echo "  optimize - Apply high-end hardware optimizations"
        echo "  status   - Show current model status"
        exit 1
        ;;
esac

echo ""
echo "🎯 Model management complete!"