#!/bin/bash

echo "🧪 DocuMind Health Check..."
echo "=========================="

services=(
    "Main API:5266:http://127.0.0.1:5266/swagger"
    "RAG API:7001:http://127.0.0.1:7001/healthz"  
    "Vision API:7002:http://127.0.0.1:7002/swagger"
    "Semantic Kernel:5076:http://127.0.0.1:5076/swagger"
    "Agent Framework:8082:http://127.0.0.1:8082/"
    "Legacy Agents:8081:http://127.0.0.1:8081/swagger"
    "Qdrant DB:6333:http://127.0.0.1:6333/dashboard"
)

all_healthy=true

for service in "${services[@]}"; do
    IFS=':' read -r name port url <<< "$service"
    printf "%-20s " "$name"
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo "✅ Healthy (Port $port)"
    else
        echo "❌ Unhealthy (Port $port)"
        all_healthy=false
    fi
done

echo "=========================="
if $all_healthy; then
    echo "🎉 All services are healthy!"
    echo ""
    echo "🔗 Quick Access Links:"
    echo "  • Main API: http://127.0.0.1:5266/swagger"
    echo "  • RAG API Docs: http://127.0.0.1:7001/docs" 
    echo "  • Vision API: http://127.0.0.1:7002/swagger"
    echo "  • Semantic Kernel: http://127.0.0.1:5076/swagger"
    echo "  • Agent Framework: http://127.0.0.1:8082/swagger"
    echo "  • Legacy Agents: http://127.0.0.1:8081/swagger"
    echo "  • Qdrant Dashboard: http://127.0.0.1:6333/dashboard"
    echo ""
    echo "🎯 Test Commands:"
    echo "  • RAG Query: curl -X POST 'http://127.0.0.1:7001/ask' -H 'Content-Type: application/json' -d '{\"q\":\"test\"}'"
    echo "  • Main API Ask: curl -X POST 'http://127.0.0.1:5266/api/ask' -H 'Content-Type: application/json' -d '{\"question\":\"test\"}'"
    exit 0
else
    echo "⚠️  Some services are unhealthy"
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "  • Check logs: docker logs qdrant"
    echo "  • Restart services: ./scripts/stop-all.sh && ./scripts/start-all.sh"
    echo "  • Check ports: netstat -tlnp | grep -E ':(5266|7001|7002|5076|8082|8081|6333)'"
    exit 1
fi