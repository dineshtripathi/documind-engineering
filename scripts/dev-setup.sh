#!/bin/bash
# 🚀 DocuMind Development Environment Setup
# Optimized for 192GB RAM, 24GB VRAM, 22 cores

set -e

echo "🏗️ DocuMind YAGNI Development Setup"
echo "===================================="
echo ""

# Check system resources
echo "📊 System Resources:"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null || echo 'No NVIDIA GPU detected')"
echo "CPU Cores: $(nproc)"
echo ""

# Environment variables
echo "🔧 Setting up environment variables..."
export OLLAMA_MODELS="/mnt/h/ollama-models"
export OLLAMA_HOST="http://127.0.0.1:11434"
export CUDA_VISIBLE_DEVICES=0

# Add to bashrc if not already there
if ! grep -q "OLLAMA_MODELS" ~/.bashrc; then
    echo 'export OLLAMA_MODELS="/mnt/h/ollama-models"' >> ~/.bashrc
    echo 'export OLLAMA_HOST="http://127.0.0.1:11434"' >> ~/.bashrc
    echo 'export CUDA_VISIBLE_DEVICES=0' >> ~/.bashrc
    echo "✅ Environment variables added to ~/.bashrc"
fi

# Check Ollama installation
echo "🤖 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found: $(ollama --version)"
    
    # Test Ollama connection
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama service running"
        echo "📋 Available models:"
        ollama list
    else
        echo "⚠️ Starting Ollama service..."
        ollama serve &
        sleep 3
    fi
else
    echo "❌ Ollama not found. Please install Ollama first."
    exit 1
fi

# Check Python environment
echo ""
echo "🐍 Checking Python environment..."
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    source .venv/bin/activate
    echo "✅ Activated virtual environment"
    echo "Python version: $(python --version)"
else
    echo "❌ No .venv found. Creating virtual environment..."
    python -m venv .venv
    source .venv/bin/activate
    echo "✅ Created and activated virtual environment"
fi

# Check Docker
echo ""
echo "🐳 Checking Docker services..."
if docker compose -f docker/compose.yml ps | grep -q "qdrant"; then
    echo "✅ Qdrant vector database running"
else
    echo "🚀 Starting Qdrant..."
    cd docker && docker compose up -d
    cd ..
    echo "✅ Qdrant started"
fi

echo ""
echo "🎉 Development environment ready!"
echo "================================="
echo "🤖 Local Models: 3 models (49GB) on H: drive"
echo "🐳 Vector DB: Qdrant running in Docker"
echo "🐍 Python: Virtual environment activated"
echo "⚡ System: Optimized for high-end hardware"
echo ""
echo "Next: Run './scripts/health-check.sh' to validate setup"