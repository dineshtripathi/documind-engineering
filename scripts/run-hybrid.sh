#!/usr/bin/env bash
set -euo pipefail

# --- Config (tweak as you like) ---
DOTNET_DIR="src/dotnet/DocuMind.Api/DocuMind.Api"
PY_RAG_APP="src.python.services.rag_api.app:app"
RAG_HOST="127.0.0.1"
RAG_PORT="7001"
RAG_BASE="http://${RAG_HOST}:${RAG_PORT}"
CONDA_ENV="documind"        # change if your env is named differently
TIMEOUT_SECS=30             # uvicorn/dotnet bring-up wait

# --- Paths ---
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
LOG_DIR="${RUN_DIR}/logs"
PID_DIR="${RUN_DIR}/pids"
mkdir -p "$LOG_DIR" "$PID_DIR"

echo "[hybrid] root: $ROOT_DIR"
cd "$ROOT_DIR"

# --- Start Qdrant (docker) ---
if [[ -x "./scripts/dev-up.sh" ]]; then
  echo "[hybrid] starting Qdrant via scripts/dev-up.sh ..."
  ./scripts/dev-up.sh
else
  echo "[hybrid] WARNING: ./scripts/dev-up.sh not found; ensure Qdrant is up on 6333."
fi

# --- Activate conda (best effort) ---
if command -v conda >/dev/null 2>&1; then
  echo "[hybrid] activating conda env: ${CONDA_ENV}"
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate "${CONDA_ENV}" || echo "[hybrid] WARNING: conda env '${CONDA_ENV}' not found; ensure deps are installed."
else
  echo "[hybrid] WARNING: conda not found; assuming Python deps already available."
fi

# --- Start FastAPI RAG (background) ---
export PYTHONPATH="${ROOT_DIR}"
echo "[hybrid] starting RAG: uvicorn ${PY_RAG_APP} on ${RAG_BASE}"
( uvicorn "${PY_RAG_APP}" --host "${RAG_HOST}" --port "${RAG_PORT}" --reload \
  > "${LOG_DIR}/rag.out" 2>&1 ) & echo $! > "${PID_DIR}/rag.pid"

# --- Wait for RAG health ---
echo -n "[hybrid] waiting for RAG health"
for i in $(seq 1 $TIMEOUT_SECS); do
  if curl -fsS "${RAG_BASE}/healthz" >/dev/null 2>&1; then
    echo " ... up"
    break
  fi
  echo -n "."
  sleep 1
  if [[ $i -eq $TIMEOUT_SECS ]]; then
    echo
    echo "[hybrid] ERROR: RAG did not become healthy in ${TIMEOUT_SECS}s (still continuing; AOAI fallback will work)."
  fi
done

# --- Run .NET orchestrator (foreground) ---
echo "[hybrid] starting .NET orchestrator on http://localhost:5266 (CTRL+C to stop)"
cd "${ROOT_DIR}/${DOTNET_DIR}"

# Ensure RAG is used first; not strictly required (soft dependency still falls back)
export Rag__BaseUrl="${RAG_BASE}"
export FeatureFlags__UseRagFirst=true
export FeatureFlags__RagRequired=false

dotnet run
