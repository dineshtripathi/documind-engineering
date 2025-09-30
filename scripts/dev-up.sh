#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

docker compose -f docker/compose.yml up -d
echo "[Qdrant] http://127.0.0.1:6333"
curl -s http://127.0.0.1:6333/ | jq .status || true

echo "To start RAG API:"
echo "  ./scripts/run-rag-api.sh"
