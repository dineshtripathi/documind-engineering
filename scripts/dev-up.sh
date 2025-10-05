#!/usr/bin/env bash
# Simple Qdrant startup script (legacy compatibility)
# For full setup, use: ./scripts/start.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "🚀 Starting Qdrant vector database..."
docker compose -f docker/compose.yml up -d

echo "⏳ Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -sf http://127.0.0.1:6333/ >/dev/null 2>&1; then
        echo "✅ Qdrant ready at http://127.0.0.1:6333"
        curl -s http://127.0.0.1:6333/ | jq .status || true
        break
    fi
    sleep 1
    if [[ $i -eq 30 ]]; then
        echo "⚠️  Qdrant took longer than expected to start"
    fi
done

echo ""
echo "📋 Next steps:"
echo "  Start Python RAG API:    ./scripts/run-rag-api.sh"
echo "  Start all services:      ./scripts/start.sh"
echo "  Full setup guide:        cat SETUP_GUIDE.md"
