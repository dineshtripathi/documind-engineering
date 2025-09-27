docker rm -f qdrant 2>/dev/null || true
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest

curl -s http://localhost:6333/ | jq .status   # expect "ok"
