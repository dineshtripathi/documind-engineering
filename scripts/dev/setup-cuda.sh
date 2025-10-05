#!/usr/bin/env bash
# CUDA PyTorch Installation and Validation Script
# Based on the working cuda-pytorch-121.bash script

set -euo pipefail

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log() { echo -e "${BLUE}[CUDA Setup]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️${NC}  $*"; }

install_cuda_pytorch() {
    log "Installing PyTorch with CUDA 12.8 support..."

    # Activate environment if conda is available
    if command -v conda >/dev/null 2>&1 && conda env list | grep -q "^documind "; then
        eval "$(conda shell.bash hook)"
        conda activate documind
    elif [[ -d ".venv" ]]; then
        source .venv/bin/activate
    fi

    # Uninstall existing PyTorch to avoid conflicts
    log "Removing any existing PyTorch installation..."
    pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

    # Install PyTorch with CUDA 12.8
    log "Installing PyTorch with CUDA 12.8..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

    success "PyTorch with CUDA 12.8 installed"
}

validate_cuda_setup() {
    log "Validating CUDA setup..."

    python3 << 'PY'
import torch
print("🔧 PyTorch:", torch.__version__)
print("🔧 CUDA Version:", torch.version.cuda)
print("🔧 CUDA Available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("🎮 GPU:", torch.cuda.get_device_name(0))
    print("🎮 Capability:", torch.cuda.get_device_capability(0))
    print("🎮 VRAM GB:", round(torch.cuda.get_device_properties(0).total_memory/1024**3, 2))
    print("✅ CUDA setup is working correctly!")
else:
    print("⚠️  CUDA not available - running in CPU mode")
    print("   This is normal if you don't have an NVIDIA GPU")
PY
}

main() {
    echo -e "${GREEN}"
    echo "🚀 CUDA PyTorch Setup (Based on cuda-pytorch-121.bash)"
    echo -e "${NC}"

    install_cuda_pytorch
    validate_cuda_setup

    success "CUDA PyTorch setup complete!"
    echo ""
    log "To use CUDA features, ensure you have:"
    echo "  - NVIDIA GPU (RTX 20xx+ recommended)"
    echo "  - CUDA 12.8+ drivers installed"
    echo "  - Sufficient VRAM (8GB+ recommended)"
}

main "$@"
