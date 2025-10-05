conda activate documind
pip install sentence-transformers qdrant-client
pip install "sentence-transformers[torch]" 
pip install --upgrade torch
python - <<'PY'
from sentence_transformers import SentenceTransformer, CrossEncoder
print("✅ sentence-transformers loaded")

model = SentenceTransformer("BAAI/bge-m3")
print("Embedding dim:", model.get_sentence_embedding_dimension())

ce = CrossEncoder("jinaai/jina-reranker-v1-turbo-en")
print("CrossEncoder ok")
PY
