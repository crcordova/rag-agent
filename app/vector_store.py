from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from .config import COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT

def get_qdrant_client():
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def get_qdrant_collection():
    qdrant_client = get_qdrant_client()
    return qdrant_client.get_collection(COLLECTION_NAME)

def get_vector_store():
    qdrant_client = get_qdrant_client()
    # qdrant_client.get_collections()

    if not qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )

    return QdrantVectorStore(client=qdrant_client, collection_name=COLLECTION_NAME)
