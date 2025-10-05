cat > ~/setup_hybrid_ai.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
PY_VER="3.11"
CONDA_HOME="$HOME/miniconda3"
CONDA_ENV="documind"
WORKDIR="$HOME/documind-engineering"

# --- Apt essentials ---
echo "[1/8] Apt update + essentials..."
sudo apt-get update -y
sudo apt-get install -y build-essential git curl wget unzip jq pkg-config ca-certificates \
  libssl-dev software-properties-common

# --- .NET SDK (if not already) ---
if ! command -v dotnet >/dev/null 2>&1; then
  echo "[2/8] Installing .NET SDK 8..."
  wget -q https://packages.microsoft.com/config/ubuntu/$(
    . /etc/os-release; echo $VERSION_ID
  )/packages-microsoft-prod.deb -O /tmp/msprod.deb
  sudo dpkg -i /tmp/msprod.deb
  sudo apt-get update -y
  sudo apt-get install -y dotnet-sdk-8.0
else
  echo "[2/8] .NET already present: $(dotnet --version)"
fi

# --- Miniconda ---
if [ ! -d "$CONDA_HOME" ]; then
  echo "[3/8] Installing Miniconda..."
  cd /tmp
  curl -fsSLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash miniconda.sh -b -p "$CONDA_HOME"
fi
eval "$("$CONDA_HOME/bin/conda" shell.bash hook)"
conda init bash >/dev/null || true

# --- Create Python env ---
if ! conda env list | grep -q "^${CONDA_ENV} "; then
  echo "[4/8] Creating env ${CONDA_ENV} (Python ${PY_VER})..."
  conda create -y -n "${CONDA_ENV}" python="${PY_VER}"
fi
conda activate "${CONDA_ENV}"

# --- PyTorch (CUDA via conda) + core libs ---
echo "[5/8] Installing PyTorch (CUDA 12.1) + AI libs..."
conda install -y -c pytorch -c nvidia pytorch pytorch-cuda=12.1
pip install --upgrade pip
pip install "transformers>=4.43" "accelerate>=0.30" \
            "sentence-transformers>=3.0" \
            "qdrant-client>=1.9" \
            "fastapi>=0.111" "uvicorn[standard]>=0.30" \
            "httpx>=0.27" "pydantic>=2.8" \
            "numpy" "pandas" "scikit-learn" "tiktoken" "python-dotenv"

# --- Hugging Face CLI (login optional) ---
pip install "huggingface_hub>=0.24" "hf-transfer>=0.1"  # faster downloads
if ! grep -q "HF_HUB_ENABLE_HF_TRANSFER" ~/.bashrc ; then
  echo 'export HF_HUB_ENABLE_HF_TRANSFER=1' >> ~/.bashrc
fi

# --- Workspace layout ---
echo "[6/8] Creating workspace..."
mkdir -p "${WORKDIR}"/{src,infra,logs,models,data,notebooks,scripts}
if ! grep -q "DOCUMIND_HOME" ~/.bashrc ; then
  echo "export DOCUMIND_HOME=${WORKDIR}" >> ~/.bashrc
fi

# --- Ollama ---
if ! command -v ollama >/dev/null 2>&1; then
  echo "[7/8] Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "[7/8] Ollama already installed: $(ollama --version)"
fi

# --- Qdrant via Docker Compose ---
echo "[8/8] Creating Qdrant compose..."
mkdir -p "${WORKDIR}/infra"
cat > "${WORKDIR}/infra/compose.dev.yaml" <<'YAML'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    restart: unless-stopped
    ports: ["6333:6333","6334:6334"]
    volumes:
      - qdrant_data:/qdrant/storage
volumes:
  qdrant_data:
YAML

echo "✅ Base setup complete."
echo "Next:"
echo "  1) conda activate ${CONDA_ENV}"
echo "  2) docker compose -f ${WORKDIR}/infra/compose.dev.yaml up -d"
echo "  3) Pull models: ollama pull phi3.5:3.8b-mini-instruct-q8_0 ; ollama pull llama3.1:8b-instruct-q4_K_M"
echo "  4) (Optional) huggingface-cli login"
echo "  5) Run embedding/reranker services (I'll give files next)"
SH

chmod +x ~/setup_hybrid_ai.sh
./setup_hybrid_ai.sh


# ---Install Miniconda (if not already) ---

cd /tmp
curl -fsSLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p "$HOME/miniconda3"

# --- Accept conda TOS + create env (if not already) ---

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda create -y -n documind python=3.11

