#!/usr/bin/env bash
set -euo pipefail

DOTNET_DIR="src/dotnet/DocuMind.Api/DocuMind.Api"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[cloud] root: $ROOT_DIR"
cd "$ROOT_DIR/${DOTNET_DIR}"

# Force cloud path: don’t even try local RAG
export FeatureFlags__UseRagFirst=false
export FeatureFlags__RagRequired=false

# Optionally make sure any proxy doesn’t interfere
export Rag__BaseUrl="http://127.0.0.1:7001"

echo "[cloud] starting .NET orchestrator on http://localhost:5266 (CTRL+C to stop)"
dotnet run
