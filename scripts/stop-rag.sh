#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="${ROOT_DIR}/.run/pids"

if [[ -f "${PID_DIR}/rag.pid" ]]; then
  PID="$(cat "${PID_DIR}/rag.pid")"
  if ps -p "$PID" >/dev/null 2>&1; then
    echo "[stop] killing RAG pid ${PID}"
    kill "$PID" || true
  fi
  rm -f "${PID_DIR}/rag.pid"
else
  echo "[stop] no rag.pid found"
fi
