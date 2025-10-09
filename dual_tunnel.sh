#!/bin/bash

# DocuMind Dual Tunnel Manager
# Manages both Web UI and API ngrok tunnels

echo "🚀 DOCUMIND DUAL TUNNEL SETUP 🚀"
echo "=================================="
echo ""

# Check if ngrok is configured
if ! ngrok config check > /dev/null 2>&1; then
    echo "❌ ngrok not configured!"
    echo "Please run: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

# Kill any existing ngrok processes
echo "🧹 Cleaning up existing tunnels..."
pkill -f ngrok 2>/dev/null || true
sleep 2

# Check if services are running
echo "📊 Checking DocuMind services..."
if ! curl -s http://localhost:8501 > /dev/null; then
    echo "❌ Web UI not running on port 8501"
    echo "Please start Streamlit first"
    exit 1
fi

if ! curl -s http://localhost:7001/ask > /dev/null; then
    echo "❌ API not running on port 7001"
    echo "Please start the RAG API first"
    exit 1
fi

echo "✅ Both services are running"
echo ""

# Start Web UI tunnel
echo "🌐 Starting Web UI tunnel..."
ngrok http 8501 --log=stdout > web_tunnel.log 2>&1 &
WEB_PID=$!

# Wait a moment and start API tunnel
echo "🔧 Starting API tunnel..."
sleep 3
ngrok http 7001 --log=stdout > api_tunnel.log 2>&1 &
API_PID=$!

# Wait for tunnels to establish
echo "⏳ Waiting for tunnels to establish..."
sleep 8

# Extract URLs
echo ""
echo "🎯 TUNNEL STATUS:"
echo "=================="

# Get Web UI URL
WEB_URL=$(grep -o 'https://[^.]*\.ngrok-free\.app' web_tunnel.log | head -1)
if [ ! -z "$WEB_URL" ]; then
    echo "✅ Web UI: $WEB_URL"
else
    echo "❌ Web UI tunnel failed"
fi

# Get API URL
API_URL=$(grep -o 'https://[^.]*\.ngrok-free\.app' api_tunnel.log | head -1)
if [ ! -z "$API_URL" ]; then
    echo "✅ API: $API_URL"
else
    echo "❌ API tunnel failed"
fi

echo ""
echo "🎉 DOCUMIND IS NOW PUBLIC!"
echo "=========================="
echo ""
echo "📋 SHARE THESE URLS:"
echo "• Main Platform: $WEB_URL"
echo "• API Endpoint: $API_URL"
echo "• API Docs: $API_URL/docs"
echo ""
echo "🔧 TUNNEL MANAGEMENT:"
echo "• Web UI PID: $WEB_PID"
echo "• API PID: $API_PID"
echo "• Logs: web_tunnel.log, api_tunnel.log"
echo ""
echo "Press Ctrl+C to stop all tunnels"
echo ""

# Monitor tunnels
trap 'echo "Stopping tunnels..."; kill $WEB_PID $API_PID 2>/dev/null; exit' INT

# Keep script running
while true; do
    sleep 10
    # Check if processes are still running
    if ! kill -0 $WEB_PID 2>/dev/null; then
        echo "⚠️ Web tunnel died, restarting..."
        ngrok http 8501 --log=stdout >> web_tunnel.log 2>&1 &
        WEB_PID=$!
    fi

    if ! kill -0 $API_PID 2>/dev/null; then
        echo "⚠️ API tunnel died, restarting..."
        ngrok http 7001 --log=stdout >> api_tunnel.log 2>&1 &
        API_PID=$!
    fi
done
