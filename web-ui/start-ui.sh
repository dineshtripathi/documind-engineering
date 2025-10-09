#!/bin/bash

# DocuMind Web UI Startup Script

echo "🚀 Starting DocuMind Web UI..."

# Check if running in conda environment
if [[ $CONDA_DEFAULT_ENV == "documind" ]]; then
    echo "✅ Already in documind environment"
else
    echo "🔄 Activating documind environment..."
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate documind
fi

# Install Streamlit if not already installed
echo "📦 Installing Streamlit dependencies..."
pip install streamlit requests pandas python-dotenv

# Change to web-ui directory
cd "$(dirname "$0")"

echo "🌐 Starting Streamlit app..."
echo "📍 Access the web interface at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"

# Start Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
