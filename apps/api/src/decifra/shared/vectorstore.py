from functools import lru_cache

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from decifra.config import get_settings
from decifra.shared.llm import get_embeddings

EMBEDDING_DIMENSIONS = 1536


@lru_cache
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=get_settings().qdrant_url)


def ensure_collection() -> None:
    settings = get_settings()
    client = get_qdrant_client()
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=EMBEDDING_DIMENSIONS, distance=Distance.COSINE),
        )


def get_vector_store() -> QdrantVectorStore:
    ensure_collection()
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=get_settings().qdrant_collection,
        embedding=get_embeddings(),
    )
