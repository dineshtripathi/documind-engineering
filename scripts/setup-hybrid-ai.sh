#!/bin/bash
# DocuMind Engineering - Hybrid AI Infrastructure Setup
# Local Models (Ollama + llama.cpp) + Cloud Models (Azure AI Foundry)

set -euo pipefail

# Configuration
PROJECT_ROOT="/home/dinesh/documind-engineering"
MODELS_DIR="$PROJECT_ROOT/models"
CONDA_ENV="documind"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure conda environment is activated
ensure_conda_env() {
    if [[ "$CONDA_DEFAULT_ENV" != "$CONDA_ENV" ]]; then
        log_info "Activating conda environment: $CONDA_ENV"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate "$CONDA_ENV"
    fi
}

# Setup local Ollama models
setup_ollama_models() {
    log_info "Setting up Ollama local models..."
    
    # Check if Ollama server is running
    if ! pgrep -f "ollama serve" > /dev/null; then
        log_info "Starting Ollama server..."
        nohup ollama serve > "$PROJECT_ROOT/logs/ollama.log" 2>&1 &
        sleep 5
    fi
    
    # Essential models for local inference
    local models=(
        "llama3.1:8b"           # Fast general purpose
        "phi3.5:3.8b"           # Lightweight efficiency
        "deepseek-coder:6.7b"   # Coding (smaller version)
        "qwen2.5-coder:7b"      # Alternative coding
    )
    
    for model in "${models[@]}"; do
        log_info "Pulling model: $model"
        if ollama pull "$model"; then
            log_success "Successfully pulled: $model"
        else
            log_warning "Failed to pull: $model (will retry later)"
        fi
    done
    
    log_info "Testing model inference..."
    echo "What is machine learning?" | ollama run llama3.1:8b --verbose
}

# Setup llama.cpp quantized models
setup_llamacpp_models() {
    log_info "Setting up llama.cpp quantized models..."
    
    mkdir -p "$MODELS_DIR/gguf"
    cd "$MODELS_DIR/gguf"
    
    # Download high-efficiency quantized models
    local models=(
        "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf|llama-3.1-8b-q4.gguf"
        "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf|phi3-mini-q4.gguf"
        "https://huggingface.co/bartowski/deepseek-coder-6.7b-instruct-GGUF/resolve/main/deepseek-coder-6.7b-instruct-Q4_K_M.gguf|deepseek-6.7b-q4.gguf"
    )
    
    for model_info in "${models[@]}"; do
        IFS='|' read -r url filename <<< "$model_info"
        log_info "Downloading: $filename"
        
        if [[ ! -f "$filename" ]]; then
            curl -L -C - -o "$filename" "$url" || log_warning "Failed to download $filename"
        else
            log_success "Already exists: $filename"
        fi
    done
}

# Test GPU performance
test_gpu_performance() {
    log_info "Testing GPU performance..."
    
    # Test Ollama GPU usage
    echo "=== Ollama GPU Test ===" 
    echo "Simple test question" | ollama run llama3.1:8b
    
    # Test llama.cpp GPU usage
    echo "=== llama.cpp GPU Test ==="
    "$PROJECT_ROOT/scripts/llamacpp-config.sh" test "$MODELS_DIR/gguf/phi3-mini-q4.gguf"
    
    # Show GPU status
    nvidia-smi
}

# Setup Azure AI Foundry
setup_azure_ai_foundry() {
    log_info "Setting up Azure AI Foundry..."
    
    # Create Azure configuration
    cat > "$PROJECT_ROOT/infra/azure-ai-config.json" << EOF
{
    "ai_foundry": {
        "subscription_id": "your-subscription-id",
        "resource_group": "documind-ai-rg",
        "workspace_name": "documind-ai-workspace",
        "location": "eastus2",
        "models": {
            "gpt_4o": {
                "deployment_name": "gpt-4o-deployment",
                "model_name": "gpt-4o",
                "version": "2024-08-06",
                "capacity": 10
            },
            "text_embedding_3_large": {
                "deployment_name": "text-embedding-3-large",
                "model_name": "text-embedding-3-large", 
                "version": "1",
                "capacity": 10
            },
            "gpt_4o_mini": {
                "deployment_name": "gpt-4o-mini-deployment",
                "model_name": "gpt-4o-mini",
                "version": "2024-07-18",
                "capacity": 10
            }
        }
    }
}
EOF
    
    log_success "Azure AI configuration created"
    log_info "Next step: Run Azure provisioning script"
}

# Create hybrid model router configuration
setup_hybrid_routing() {
    log_info "Setting up hybrid model routing configuration..."
    
    cat > "$PROJECT_ROOT/src/python/services/hybrid_config.py" << 'EOF'
"""
DocuMind Engineering - Hybrid Model Configuration
Local GPU + Cloud AI routing configuration
"""

HYBRID_CONFIG = {
    "local_models": {
        "ollama": {
            "endpoint": "http://localhost:11434",
            "models": {
                "llama3.1:8b": {
                    "tier": "balanced",
                    "specialties": ["general", "reasoning"],
                    "max_context": 131072,
                    "memory_mb": 4900
                },
                "phi3.5:3.8b": {
                    "tier": "efficient", 
                    "specialties": ["lightweight", "quick_queries"],
                    "max_context": 131072,
                    "memory_mb": 2200
                },
                "deepseek-coder:6.7b": {
                    "tier": "balanced",
                    "specialties": ["coding", "debugging"],
                    "max_context": 16384,
                    "memory_mb": 4000
                }
            }
        },
        "llamacpp": {
            "endpoint": "http://localhost:8081",
            "models": {
                "llama-3.1-8b-q4": {
                    "tier": "efficient",
                    "specialties": ["general", "batch_processing"],
                    "max_context": 131072,
                    "memory_mb": 4600
                },
                "phi3-mini-q4": {
                    "tier": "efficient",
                    "specialties": ["lightweight", "fast_inference"],
                    "max_context": 131072,
                    "memory_mb": 2300
                }
            }
        }
    },
    "cloud_models": {
        "azure_ai_foundry": {
            "endpoint": "https://documind-ai-workspace.openai.azure.com/",
            "models": {
                "gpt-4o": {
                    "tier": "premium",
                    "specialties": ["complex_reasoning", "analysis", "real_time_info"],
                    "max_context": 128000,
                    "cost_per_1k_tokens": 0.03
                },
                "gpt-4o-mini": {
                    "tier": "balanced",
                    "specialties": ["general", "cost_effective"],
                    "max_context": 128000,
                    "cost_per_1k_tokens": 0.0015
                },
                "text-embedding-3-large": {
                    "tier": "premium",
                    "specialties": ["embeddings", "semantic_search"],
                    "dimensions": 3072,
                    "cost_per_1k_tokens": 0.00013
                }
            }
        }
    },
    "routing_strategy": {
        "real_time_info": "cloud",      # Internet access needed
        "complex_reasoning": "local_premium_or_cloud",
        "coding_tasks": "local_coding",
        "batch_processing": "local_efficient", 
        "embeddings": "cloud",
        "cost_sensitive": "local",
        "high_context": "local_or_cloud"
    },
    "fallback_chain": [
        "local_premium",
        "local_balanced", 
        "cloud_balanced",
        "local_efficient"
    ]
}
EOF
    
    log_success "Hybrid routing configuration created"
}

# Create monitoring setup
setup_monitoring() {
    log_info "Setting up monitoring and cost tracking..."
    
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/monitoring"
    
    cat > "$PROJECT_ROOT/monitoring/usage_tracker.py" << 'EOF'
"""
DocuMind Engineering - Usage and Cost Tracker
Monitor local GPU usage and cloud API costs
"""

import json
import time
from datetime import datetime
from typing import Dict, List
import psutil
import subprocess

class UsageTracker:
    def __init__(self, log_file="logs/usage.json"):
        self.log_file = log_file
        self.usage_data = []
    
    def log_inference(self, model_name: str, tier: str, tokens: int, 
                     duration: float, cost: float = 0.0):
        """Log inference usage"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "tier": tier,
            "tokens": tokens,
            "duration_sec": duration,
            "cost_usd": cost,
            "gpu_memory_mb": self.get_gpu_memory(),
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": psutil.virtual_memory().percent
        }
        
        self.usage_data.append(entry)
        self.save_data()
    
    def get_gpu_memory(self) -> int:
        """Get current GPU memory usage"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True, text=True
            )
            return int(result.stdout.strip())
        except:
            return 0
    
    def save_data(self):
        """Save usage data to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def get_daily_stats(self) -> Dict:
        """Get daily usage statistics"""
        today = datetime.now().date()
        today_data = [
            entry for entry in self.usage_data 
            if datetime.fromisoformat(entry["timestamp"]).date() == today
        ]
        
        if not today_data:
            return {"date": today.isoformat(), "total_requests": 0}
        
        return {
            "date": today.isoformat(),
            "total_requests": len(today_data),
            "total_tokens": sum(entry["tokens"] for entry in today_data),
            "total_cost": sum(entry["cost_usd"] for entry in today_data),
            "avg_duration": sum(entry["duration_sec"] for entry in today_data) / len(today_data),
            "models_used": list(set(entry["model"] for entry in today_data))
        }

# Global tracker instance
usage_tracker = UsageTracker()
EOF
    
    log_success "Monitoring setup created"
}

# Main execution
main() {
    log_info "🚀 DocuMind Engineering - Hybrid AI Infrastructure Setup"
    echo "=================================================================="
    
    ensure_conda_env
    
    case "${1:-all}" in
        "ollama")
            setup_ollama_models
            ;;
        "llamacpp")
            setup_llamacpp_models
            ;;
        "azure")
            setup_azure_ai_foundry
            ;;
        "routing")
            setup_hybrid_routing
            ;;
        "monitoring")
            setup_monitoring
            ;;
        "test")
            test_gpu_performance
            ;;
        "all")
            mkdir -p "$PROJECT_ROOT/logs"
            setup_ollama_models
            setup_llamacpp_models
            setup_azure_ai_foundry
            setup_hybrid_routing
            setup_monitoring
            log_success "🎉 Hybrid AI infrastructure setup complete!"
            log_info "Next steps:"
            log_info "1. Configure Azure credentials"
            log_info "2. Run Azure provisioning"
            log_info "3. Test hybrid routing"
            ;;
        *)
            echo "Usage: $0 [ollama|llamacpp|azure|routing|monitoring|test|all]"
            exit 1
            ;;
    esac
}

main "$@"