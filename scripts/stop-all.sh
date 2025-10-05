#!/bin/bash

echo "🛑 Stopping DocuMind Engineering Platform..."

# Kill services by PIDs if available
if [ -f .service_pids ]; then
    echo "📋 Stopping services using stored PIDs..."
    read -r pids < .service_pids
    for pid in $pids; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔻 Stopping PID $pid"
            kill "$pid"
        fi
    done
    rm .service_pids
fi

# Kill by port/process name as backup
echo "🔍 Cleaning up remaining processes..."
pkill -f "uvicorn.*rag_api" || true
pkill -f "dotnet.*DocuMind" || true

# Stop Docker services
echo "🐳 Stopping Docker services..."
./scripts/dev-down.sh

echo "✅ All services stopped"
echo ""
echo "🔄 To restart everything: ./scripts/start-all.sh"
