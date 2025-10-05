#!/usr/bin/env bash
# DocuMind Universal Setup Script
# Works on: Linux (Ubuntu/Debian/RHEL), macOS, Windows WSL2

set -euo pipefail

# --- Configuration ---
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly CONDA_ENV="documind"
readonly PYTHON_VERSION="3.11"
readonly DOTNET_VERSION="8.0"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# --- Helper Functions ---
log() { echo -e "${BLUE}[DocuMind]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️${NC}  $*"; }
error() { echo -e "${RED}❌${NC} $*" >&2; exit 1; }

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            echo "ubuntu"
        elif command -v yum >/dev/null 2>&1; then
            echo "rhel"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        warn "Unknown OS: $OSTYPE, assuming Linux"
        echo "linux"
    fi
}

check_requirements() {
    log "Checking system requirements..."

    # Check available memory (minimum 4GB, recommended 8GB)
    if command -v free >/dev/null 2>&1; then
        local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
        if [[ $mem_gb -lt 4 ]]; then
            warn "Low memory detected (${mem_gb}GB). Minimum 4GB recommended."
        fi
    fi

    # Check disk space (minimum 10GB)
    local available_gb=$(df "$ROOT_DIR" | awk 'NR==2 {print int($4/1024/1024)}')
    if [[ $available_gb -lt 10 ]]; then
        error "Insufficient disk space. Need 10GB, available: ${available_gb}GB"
    fi

    success "System requirements check passed"
}

install_system_deps() {
    local os="$1"
    log "Installing system dependencies for $os..."

    case "$os" in
        "ubuntu")
            sudo apt-get update -y
            sudo apt-get install -y \
                build-essential git curl wget unzip jq \
                software-properties-common apt-transport-https \
                ca-certificates gnupg lsb-release
            ;;
        "rhel")
            sudo yum update -y
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y git curl wget unzip jq
            ;;
        "macos")
            if ! command -v brew >/dev/null 2>&1; then
                log "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install git curl wget jq
            ;;
        *)
            warn "Manual installation may be required for $os"
            ;;
    esac

    success "System dependencies installed"
}

install_docker() {
    if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
        success "Docker already installed: $(docker --version)"
        return
    fi

    log "Installing Docker..."
    local os="$1"

    case "$os" in
        "ubuntu")
            # Add Docker's official GPG key
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

            # Add repository
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

            # Install Docker
            sudo apt-get update -y
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        "macos")
            warn "Please install Docker Desktop from: https://docs.docker.com/desktop/install/mac/"
            warn "Press Enter when Docker is installed..."
            read -r
            ;;
        *)
            warn "Please install Docker manually for $os"
            warn "Visit: https://docs.docker.com/engine/install/"
            ;;
    esac

    # Configure Docker for current user
    if [[ "$os" != "macos" ]]; then
        sudo usermod -aG docker "$USER" || warn "Could not add user to docker group"
        warn "You may need to log out and back in for Docker permissions"
    fi

    success "Docker installed"
}

install_dotnet() {
    if command -v dotnet >/dev/null 2>&1; then
        local version=$(dotnet --version | cut -d. -f1)
        if [[ $version -ge 8 ]]; then
            success ".NET already installed: $(dotnet --version)"
            return
        fi
    fi

    log "Installing .NET SDK $DOTNET_VERSION..."
    local os="$1"

    case "$os" in
        "ubuntu")
            # Get Ubuntu version
            local ubuntu_version=$(lsb_release -rs)

            # Add Microsoft package repository
            wget -q "https://packages.microsoft.com/config/ubuntu/${ubuntu_version}/packages-microsoft-prod.deb" -O /tmp/packages-microsoft-prod.deb
            sudo dpkg -i /tmp/packages-microsoft-prod.deb
            sudo apt-get update -y
            sudo apt-get install -y dotnet-sdk-${DOTNET_VERSION}
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew install --cask dotnet
            else
                warn "Please install .NET SDK manually from: https://dotnet.microsoft.com/download"
            fi
            ;;
        *)
            warn "Please install .NET SDK manually from: https://dotnet.microsoft.com/download"
            ;;
    esac

    success ".NET SDK installed"
}

install_python() {
    log "Setting up Python environment..."

    # Check if conda is available
    if command -v conda >/dev/null 2>&1; then
        log "Using conda for Python environment..."

        # Create/update conda environment
        if conda env list | grep -q "^${CONDA_ENV} "; then
            log "Updating existing conda environment..."
            conda env update -n "$CONDA_ENV" -f "$ROOT_DIR/src/python/environment.yml"
        else
            log "Creating new conda environment..."
            conda env create -f "$ROOT_DIR/src/python/environment.yml"
        fi

        # Install CUDA PyTorch specifically (based on cuda-pytorch-121.bash)
        log "Installing PyTorch with CUDA 12.8 support..."
        eval "$(conda shell.bash hook)"
        conda activate "$CONDA_ENV"
        pip uninstall -y torch torchvision torchaudio 2>/dev/null || true
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

        success "Conda environment '$CONDA_ENV' ready with CUDA PyTorch"

    elif command -v python3 >/dev/null 2>&1; then
        log "Using system Python with virtual environment..."

        # Check Python version
        local py_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [[ $(echo "$py_version >= 3.9" | bc) -eq 0 ]]; then
            error "Python 3.9+ required, found: $py_version"
        fi

        # Create virtual environment
        local venv_dir="$ROOT_DIR/.venv"
        if [[ ! -d "$venv_dir" ]]; then
            python3 -m venv "$venv_dir"
        fi

        # Install dependencies with CUDA PyTorch
        source "$venv_dir/bin/activate"
        pip install --upgrade pip

        # Install CUDA PyTorch first (based on cuda-pytorch-121.bash)
        log "Installing PyTorch with CUDA 12.8 support..."
        pip uninstall -y torch torchvision torchaudio 2>/dev/null || true
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

        # Install remaining dependencies
        pip install -r "$ROOT_DIR/src/python/requirements.txt"

        success "Python virtual environment ready with CUDA PyTorch"
    else
        error "Python 3.9+ required but not found. Please install Python or Conda."
    fi
}install_ollama() {
    if command -v ollama >/dev/null 2>&1; then
        success "Ollama already installed: $(ollama --version 2>/dev/null || echo 'version unknown')"
        return
    fi

    log "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh

    # Start Ollama service (Linux)
    if command -v systemctl >/dev/null 2>&1; then
        sudo systemctl enable ollama || warn "Could not enable ollama service"
        sudo systemctl start ollama || warn "Could not start ollama service"
    fi

    success "Ollama installed"
}

download_models() {
    log "Downloading AI models..."

    # Activate Python environment first
    if command -v conda >/dev/null 2>&1 && conda env list | grep -q "^${CONDA_ENV} "; then
        # Use conda environment
        eval "$(conda shell.bash hook)"
        conda activate "$CONDA_ENV"
    elif [[ -d "$ROOT_DIR/.venv" ]]; then
        # Use virtual environment
        source "$ROOT_DIR/.venv/bin/activate"
    fi

    # Download sentence transformer model
    log "Downloading embedding model (BAAI/bge-m3)..."
    python3 -c "
from sentence_transformers import SentenceTransformer
import sys
try:
    model = SentenceTransformer('BAAI/bge-m3')
    print('✅ Embedding model downloaded successfully')
except Exception as e:
    print(f'❌ Failed to download embedding model: {e}', file=sys.stderr)
    sys.exit(1)
" || warn "Failed to download embedding model"

    # Download Ollama models
    if command -v ollama >/dev/null 2>&1; then
        log "Downloading Ollama models..."

        # Wait for ollama service to be ready
        for i in {1..30}; do
            if ollama list >/dev/null 2>&1; then
                break
            fi
            if [[ $i -eq 30 ]]; then
                warn "Ollama service not ready, skipping model download"
                return
            fi
            sleep 1
        done

        # Download Phi-3.5 model (efficient 4-bit quantized version)
        ollama pull phi3.5:3.8b-mini-instruct-q4_0 || warn "Failed to download Phi-3.5 model"

        success "Ollama models downloaded"
    fi
}

setup_project() {
    log "Setting up project structure..."

    cd "$ROOT_DIR"

    # Create necessary directories
    mkdir -p data/{docs,staging} logs models .run/{logs,pids}

    # Build .NET solution
    if [[ -f "src/dotnet/DocuMind.Api.sln" ]]; then
        log "Building .NET solution..."
        cd src/dotnet
        dotnet restore DocuMind.Api.sln
        dotnet build DocuMind.Api.sln --configuration Release
        cd "$ROOT_DIR"
        success ".NET solution built"
    fi

    # Set up environment file
    if [[ ! -f ".env" ]]; then
        cat > .env <<EOF
# DocuMind Configuration
QDRANT_URL=http://127.0.0.1:6333
RAG_API_URL=http://127.0.0.1:7001
DOTNET_API_URL=http://127.0.0.1:5266

# Model Configuration
OLLAMA_MODEL=phi3.5:3.8b-mini-instruct-q4_0
EMBED_MODEL=BAAI/bge-m3
RERANK_MODEL=jinaai/jina-reranker-v1-turbo-en

# Azure AI (Optional - add your credentials)
# AZURE_AI_VISION_ENDPOINT=https://your-region.cognitiveservices.azure.com
# AZURE_AI_VISION_KEY=your-key

# Feature Flags
FeatureFlags__UseRagFirst=true
FeatureFlags__RagRequired=false
EOF
        success "Environment file created (.env)"
    fi

    success "Project setup complete"
}

# --- Main Setup Process ---
main() {
    echo -e "${GREEN}"
    cat << 'EOF'
    ____                   __  __ _           _
   |  _ \  ___   ___ _   _|  \/  (_)_ __   __| |
   | | | |/ _ \ / __| | | | |\/| | | '_ \ / _` |
   | |_| | (_) | (__| |_| | |  | | | | | | (_| |
   |____/ \___/ \___|\__,_|_|  |_|_|_| |_|\__,_|

   🚀 Universal Setup Script

EOF
    echo -e "${NC}"

    log "Starting DocuMind setup..."
    log "Root directory: $ROOT_DIR"

    local os=$(detect_os)
    log "Detected OS: $os"

    # Check system requirements
    check_requirements

    # Install dependencies
    install_system_deps "$os"
    install_docker "$os"
    install_dotnet "$os"
    install_python
    install_ollama

    # Download models
    download_models

    # Setup project
    setup_project

    # Final success message
    echo -e "${GREEN}"
    cat << 'EOF'

   ✅ DocuMind Setup Complete!

   Next steps:
   1. Start services:    ./scripts/start.sh
   2. Test APIs:         curl http://localhost:7001/healthz
   3. Open dashboard:    http://localhost:6333/dashboard

   For help: ./scripts/start.sh --help

EOF
    echo -e "${NC}"

    # Show environment activation command
    if command -v conda >/dev/null 2>&1 && conda env list | grep -q "^${CONDA_ENV} "; then
        warn "To activate Python environment manually: conda activate $CONDA_ENV"
    elif [[ -d "$ROOT_DIR/.venv" ]]; then
        warn "To activate Python environment manually: source .venv/bin/activate"
    fi
}

# Run main function
main "$@"
