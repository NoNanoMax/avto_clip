from __future__ import annotations

import json
import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from sqlalchemy import create_engine, text
from qdrant_client import QdrantClient

from app.embeddings.clip_hf import ClipHFEmbedder


APP_DB_DSN = os.environ["APP_DB_DSN"]
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
TEXT_COLLECTION = os.getenv("QDRANT_TEXT_COLLECTION", "ads_text")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/clip-vit-base-patch32")


engine = create_engine(APP_DB_DSN, pool_pre_ping=True, pool_size=5, max_overflow=10)
qdrant = QdrantClient(url=QDRANT_URL)
clip = ClipHFEmbedder(model_name=MODEL_NAME)


app = FastAPI(title="Ads Search API")


class SearchRequest(BaseModel):
    query: str
    limit: int


class PhotoOut(BaseModel):
    id: str
    source_url: str
    s3_url: str


class AdOut(BaseModel):
    ad_id: str
    score: float
    description: str | None = None
    meta: Any | None = None
    photos: list[PhotoOut] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search", response_model=dict)
def search(req: SearchRequest):
    qvec = clip.embed_text(req.query)
    hits = qdrant.search(
        collection_name=TEXT_COLLECTION,
        query_vector=qvec,
        limit=req.limit,
        with_payload=True,
    )
    scored_ids: list[tuple[str, float]] = []
    for h in hits:
        if not h.payload:
            continue
        ad_id = h.payload.get("ad_id")
        if not ad_id:
            continue
        scored_ids.append((ad_id, float(h.score)))

    if not scored_ids:
        return {"items": []}

    ad_ids = [ad_id for ad_id, _ in scored_ids]
    score_by_id = {ad_id: score for ad_id, score in scored_ids}

    ads_sql = text("""
      SELECT id, description, meta_json
      FROM ads
      WHERE id = ANY(:ids)
        AND index_status = 'READY'
    """)

    with engine.begin() as conn:
        ad_rows = conn.execute(ads_sql, {"ids": ad_ids}).mappings().all()

    ads_by_id = {r["id"]: dict(r) for r in ad_rows}
    ready_ids = list(ads_by_id.keys())

    if not ready_ids:
        return {"items": []}

    photos_sql = text("""
      SELECT id, ad_id, source_url, s3_url
      FROM photos
      WHERE ad_id = ANY(:ids)
    """)

    with engine.begin() as conn:
        ph_rows = conn.execute(photos_sql, {"ids": ready_ids}).mappings().all()

    photos_by_ad: dict[str, list[dict]] = {}
    for r in ph_rows:
        photos_by_ad.setdefault(r["ad_id"], []).append(dict(r))

    items: list[AdOut] = []
    for ad_id, _score in scored_ids:
        a = ads_by_id.get(ad_id)
        if not a:
            continue

        meta_raw = a.get("meta_json")
        meta = None
        if meta_raw:
            try:
                meta = json.loads(meta_raw)
            except Exception:
                meta = meta_raw 

        photos = [
            PhotoOut(
                id=p["id"],
                source_url=p["source_url"],
                s3_url=p["s3_url"],
            )
            for p in photos_by_ad.get(ad_id, [])
        ]

        items.append(AdOut(
            ad_id=ad_id,
            score=score_by_id.get(ad_id, 0.0),
            description=a.get("description"),
            meta=meta,
            photos=photos,
        ))

    return {"items": [i.model_dump() for i in items]}
