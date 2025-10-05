from qdrant_client import QdrantClient

# Connect to your running Qdrant
client = QdrantClient("localhost", port=6333)

# List collections (should be empty initially)
print("Collections:", client.get_collections())

# Test creating a collection
client.recreate_collection(
    collection_name="test_collection",
    vectors_config={"size": 768, "distance": "Cosine"}
)

print("✅ Qdrant is working!")