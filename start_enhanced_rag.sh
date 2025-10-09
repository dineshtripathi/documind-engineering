#!/bin/bash
# Enhanced RAG API Startup Script with Domain Detection

cd /home/dinesh/documind-engineering

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate documind

# Set environment variables
export PYTHONPATH=.
export QDRANT_URL=http://127.0.0.1:6333
export ENABLE_DOMAIN_DETECTION=true
export MIN_CONFIDENCE=0.7

echo "🔧 Environment Setup:"
echo "   • Python: $(python --version)"
echo "   • Conda Environment: $CONDA_DEFAULT_ENV"
echo "   • PYTHONPATH: $PYTHONPATH"
echo "   • Qdrant URL: $QDRANT_URL"
echo "   • Domain Detection: $ENABLE_DOMAIN_DETECTION"
echo ""

echo "🐍 Starting Enhanced DocuMind RAG API with Domain Detection..."
echo "   • API Version: 0.5.0"
echo "   • Port: 7001"
echo "   • Features: Domain-aware retrieval, specialized accuracy"
echo ""

# Start the enhanced RAG API
uvicorn src.python.services.rag_api.app:app --host 127.0.0.1 --port 7001 --reload
