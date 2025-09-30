#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

export PYTHONPATH=.
export QDRANT_URL=http://127.0.0.1:6333

echo "🚀 Starting RAG API on http://127.0.0.1:7001/ask"
uvicorn src.python.services.rag_api.app:app \
  --host 127.0.0.1 \
  --port 7001 \
  --reload
