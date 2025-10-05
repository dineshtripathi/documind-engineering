#!/usr/bin/env bash
# Python RAG API startup script (legacy compatibility)
# For full setup, use: ./scripts/start.sh --python-only
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# Setup Python environment
if command -v conda >/dev/null 2>&1 && conda env list | grep -q "^documind "; then
    echo "🐍 Activating conda environment: documind"
    eval "$(conda shell.bash hook)"
    conda activate documind
elif [[ -d ".venv" ]]; then
    echo "🐍 Activating virtual environment"
    source .venv/bin/activate
else
    echo "⚠️  No Python environment found. Run: ./scripts/setup.sh"
fi

export PYTHONPATH="$(pwd)"
export QDRANT_URL="http://127.0.0.1:6333"

echo "🚀 Starting Python RAG API..."
echo "📍 API URL: http://127.0.0.1:7001"
echo "🔍 Health: http://127.0.0.1:7001/healthz"
echo "📖 Docs: http://127.0.0.1:7001/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn src.python.services.rag_api.app:app \
  --host 127.0.0.1 \
  --port 7001 \
  --reload
