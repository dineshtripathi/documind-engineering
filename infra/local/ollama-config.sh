#!/bin/bash
# 🚀 Native Ollama Configuration Script
# Optimized for high-end hardware setup

set -e

echo "🤖 Ollama Native Configuration"
echo "=============================="
echo ""

# System info
echo "📊 Target System:"
echo "- RAM: 192GB"
echo "- VRAM: 24GB"
echo "- CPU: 22 cores"
echo "- Storage: H: drive (/mnt/h/ollama-models)"
echo ""

# Environment configuration
echo "🔧 Setting up Ollama environment..."

# Create model directory if it doesn't exist
if [ ! -d "/mnt/h/ollama-models" ]; then
    echo "📁 Creating model directory on H: drive..."
    sudo mkdir -p /mnt/h/ollama-models
    sudo chown $USER:$USER /mnt/h/ollama-models
fi

# Set environment variables for current session
export OLLAMA_MODELS="/mnt/h/ollama-models"
export OLLAMA_HOST="http://127.0.0.1:11434"
export OLLAMA_MAX_LOADED_MODELS=3
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_QUEUE=100
export CUDA_VISIBLE_DEVICES=0

# Memory optimization for 192GB RAM
export OLLAMA_HOST_MEMORY=150  # 150GB for models, leave 42GB for system

echo "✅ Environment variables set for current session"

# Persistent configuration
OLLAMA_CONFIG="# Ollama Configuration for DocuMind
export OLLAMA_MODELS=\"/mnt/h/ollama-models\"
export OLLAMA_HOST=\"http://127.0.0.1:11434\"
export OLLAMA_MAX_LOADED_MODELS=3
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_QUEUE=100
export OLLAMA_HOST_MEMORY=150
export CUDA_VISIBLE_DEVICES=0"

# Add to bashrc if not already there
if ! grep -q "OLLAMA_MODELS" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "$OLLAMA_CONFIG" >> ~/.bashrc
    echo "✅ Configuration added to ~/.bashrc"
else
    echo "✅ Configuration already in ~/.bashrc"
fi

# Create systemd service for auto-start (optional)
echo ""
read -p "🚀 Create systemd service for auto-start? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/ollama.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Ollama Server
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=$USER
Group=$USER
Restart=always
RestartSec=3
Environment="OLLAMA_MODELS=/mnt/h/ollama-models"
Environment="OLLAMA_HOST=http://127.0.0.1:11434"
Environment="OLLAMA_MAX_LOADED_MODELS=3"
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_QUEUE=100"
Environment="OLLAMA_HOST_MEMORY=150"
Environment="CUDA_VISIBLE_DEVICES=0"

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ollama
    echo "✅ Systemd service created and enabled"
fi

# Test configuration
echo ""
echo "🧪 Testing configuration..."

# Check if ollama is running
if pgrep -f ollama > /dev/null; then
    echo "✅ Ollama already running"
else
    echo "🚀 Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Test API
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama API responding"
    echo ""
    echo "📋 Current models:"
    ollama list
else
    echo "⚠️ Ollama API not responding yet (may need more time to start)"
fi

echo ""
echo "🎯 Ollama native configuration complete!"
echo "========================================"
echo "✅ Models stored on H: drive for performance"
echo "✅ Memory optimized for 192GB RAM"
echo "✅ GPU acceleration configured"
echo "✅ Parallel processing enabled (4 concurrent)"
echo "✅ Multi-model loading (up to 3 simultaneously)"
echo ""
echo "Next steps:"
echo "1. Run 'source ~/.bashrc' or restart terminal"
echo "2. Run '../scripts/model-sync.sh' to verify models"
echo "3. Run '../scripts/health-check.sh' for full validation"