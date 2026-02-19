from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct


def make_qdrant(url: str) -> QdrantClient:
    return QdrantClient(url=url)


def ensure_collections(q: QdrantClient, text_collection: str, image_collection: str, text_dim: int, image_dim: int):
    existing = {c.name for c in q.get_collections().collections}

    if text_collection not in existing:
        q.create_collection(
            collection_name=text_collection,
            vectors_config=VectorParams(size=text_dim, distance=Distance.COSINE),
        )

    if image_collection not in existing:
        q.create_collection(
            collection_name=image_collection,
            vectors_config=VectorParams(size=image_dim, distance=Distance.COSINE),
        )
        

def upsert_point(q: QdrantClient, collection: str, point_id: str, vector: list[float], payload: dict):
    q.upsert(
        collection_name=collection,
        points=[PointStruct(id=point_id, vector=vector, payload=payload)],
    )
