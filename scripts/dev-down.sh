#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "🔻 Stopping and removing dev containers..."
docker compose -f ./docker/compose.yml down -v || true

# Extra cleanup: any stray qdrant container created outside compose
if docker ps -a --format '{{.Names}}' | grep -q '^qdrant$'; then
  echo "🧹 Found old qdrant container, stopping/removing..."
  docker stop qdrant || true
  docker rm qdrant || true
fi

echo "✅ Dev environment cleaned up!"
