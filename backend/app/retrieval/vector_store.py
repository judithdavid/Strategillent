"""Persistent local Qdrant vector store for Strategillent retrieval."""
from functools import lru_cache
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient, models
from app.core.config import PROJECT_ROOT, settings

COLLECTION_NAME = "strategillent_chunks"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384


@lru_cache(maxsize=1)
def get_vector_client() -> QdrantClient:
    path = Path(settings.qdrant_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(path))


def ensure_collection(client: QdrantClient | None = None) -> QdrantClient:
    client = client or get_vector_client()
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )
    return client


@lru_cache(maxsize=1)
def get_embedding_model():
    # First use downloads the model; subsequent runs use the local cache.
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=settings.embedding_model)


def embed_documents(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    return [vector.tolist() for vector in model.embed(texts)]


def embed_query(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Query cannot be empty.")
    model = get_embedding_model()
    # BGE models use a query prefix for retrieval queries.
    return next(model.query_embed("Represent this sentence for searching relevant passages: " + text)).tolist()


def upsert_chunks(chunks: list[dict[str, Any]]) -> int:
    """Embed and upsert chunks. Point IDs are deterministic UUID strings."""
    if not chunks:
        return 0

    client = ensure_collection()
    vectors = embed_documents([item["text"] for item in chunks])
    points = []
    for item, vector in zip(chunks, vectors):
        points.append(
            models.PointStruct(
                id=item["point_id"],
                vector=vector,
                payload={key: value for key, value in item.items() if key not in {"point_id", "text"}}
                | {"text": item["text"]},
            )
        )
    client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
    return len(points)
