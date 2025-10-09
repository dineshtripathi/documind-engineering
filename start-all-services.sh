#!/bin/bash

# DocuMind System Startup Script - All Services

echo "🚀 Starting DocuMind Complete System..."
echo "📍 This will start all services and the web UI"

# Check if running in conda environment
if [[ $CONDA_DEFAULT_ENV == "documind" ]]; then
    echo "✅ Already in documind environment"
else
    echo "🔄 Activating documind environment..."
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate documind
fi

# Change to project root
cd /home/dinesh/documind-engineering

echo "🔧 Installing web UI dependencies..."
pip install streamlit requests pandas python-dotenv

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 0
    else
        return 1
    fi
}

# Start Qdrant if not running
if ! check_port 6333; then
    echo "🔍 Starting Qdrant vector database..."
    cd scripts/workspace-infra-setup
    ./start-qdrant-vector-db.bash &
    cd /home/dinesh/documind-engineering
    sleep 3
fi

# Start Ollama if not running
if ! check_port 11434; then
    echo "🤖 Starting Ollama..."
    ollama serve &
    sleep 2
fi

# Start RAG API
if ! check_port 7001; then
    echo "🧠 Starting RAG API on port 7001..."
    cd src/python/services/rag_api
    uvicorn app:app --host 0.0.0.0 --port 7001 --reload &
    cd /home/dinesh/documind-engineering
    sleep 2
fi

# Start Vision API (if available)
if ! check_port 7002; then
    echo "👁️  Vision API would start on port 7002 (when implemented)"
fi

# Start Agents API (if available)
if ! check_port 5076; then
    echo "🤖 Agents API would start on port 5076 (when implemented)"
fi

# Start Main API (if available)
if ! check_port 5266; then
    echo "🏗️  Main API would start on port 5266 (when implemented)"
fi

# Wait a moment for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 5

# Start Web UI
echo "🌐 Starting Streamlit Web UI on port 8501..."
cd web-ui
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

echo ""
echo "🎉 DocuMind System Started Successfully!"
echo ""
echo "📍 Access Points:"
echo "   🌐 Web UI:        http://localhost:8501"
echo "   📚 RAG API Docs:  http://localhost:7001/docs"
echo "   🔍 Qdrant:        http://localhost:6333/dashboard"
echo "   🤖 Ollama:        http://localhost:11434"
echo ""
echo "🛑 To stop all services, run: pkill -f 'streamlit|uvicorn|qdrant|ollama'"
echo ""

# Keep script running to show logs
wait
