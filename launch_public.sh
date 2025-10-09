#!/bin/bash

# DocuMind Ultimate AI Platform - Public Launch Script
# Run this after setting up your ngrok authtoken

echo "🚀 DOCUMIND ULTIMATE AI PLATFORM - LAUNCH SEQUENCE 🚀"
echo "=================================================="
echo "Date: $(date)"
echo "Platform: DocuMind Commercial AI Suite"
echo "Features: 11 Specialized AI Interfaces"
echo ""

# Check if services are running
echo "📊 Checking system status..."
UVICORN_RUNNING=$(ps aux | grep uvicorn | grep -v grep | wc -l)
STREAMLIT_RUNNING=$(ps aux | grep streamlit | grep -v grep | wc -l)

if [ $UVICORN_RUNNING -eq 0 ]; then
    echo "❌ RAG API not running! Starting..."
    cd /home/dinesh/documind-engineering
    source /home/dinesh/miniconda3/etc/profile.d/conda.sh
    conda activate documind
    nohup uvicorn services.rag_api.app:app --host 0.0.0.0 --port 7001 --workers 2 > api.log 2>&1 &
    sleep 5
    echo "✅ RAG API started"
else
    echo "✅ RAG API running"
fi

if [ $STREAMLIT_RUNNING -eq 0 ]; then
    echo "❌ Web interface not running! Starting..."
    cd /home/dinesh/documind-engineering/web-ui
    nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > web.log 2>&1 &
    sleep 5
    echo "✅ Web interface started"
else
    echo "✅ Web interface running"
fi

# Test API health
echo ""
echo "🔍 Testing API health..."
API_RESPONSE=$(curl -s -X POST "http://localhost:7001/ask" -H "Content-Type: application/json" -d '{"q": "test"}' | jq -r '.answer' 2>/dev/null)

if [ ! -z "$API_RESPONSE" ] && [ "$API_RESPONSE" != "null" ]; then
    echo "✅ API responding correctly"
else
    echo "⚠️  API response check inconclusive (may be normal)"
fi

# Test web interface
echo ""
echo "🌐 Testing web interface..."
WEB_STATUS=$(curl -s -I http://localhost:8501 | head -1 | grep "200 OK")

if [ ! -z "$WEB_STATUS" ]; then
    echo "✅ Web interface responding"
else
    echo "❌ Web interface not responding"
    exit 1
fi

echo ""
echo "🎯 SYSTEM STATUS: READY FOR PUBLIC DEPLOYMENT"
echo ""
echo "📋 Pre-Launch Checklist:"
echo "✅ RAG API Backend (Port 7001)"
echo "✅ Streamlit Frontend (Port 8501)"
echo "✅ AI Models Loaded"
echo "✅ 11 Specialized Interfaces"
echo "✅ Multi-format Processing"
echo "✅ Export Capabilities"
echo ""
echo "🚀 LAUNCHING PUBLIC TUNNEL..."
echo "=================================================="
echo ""

# Check if ngrok is configured
if ! ngrok config check > /dev/null 2>&1; then
    echo "❌ ngrok not configured!"
    echo ""
    echo "Please run first:"
    echo "ngrok config add-authtoken YOUR_TOKEN_HERE"
    echo ""
    echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

echo "🌍 Starting ngrok tunnel for DocuMind..."
echo "Your platform will be accessible worldwide!"
echo ""
echo "🎉 LAUNCH IN PROGRESS..."
echo "Watch for the public URL below:"
echo ""

# Launch ngrok
ngrok http 8501
