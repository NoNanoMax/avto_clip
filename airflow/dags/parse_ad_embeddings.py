from __future__ import annotations

import json
import hashlib
from datetime import datetime
import logging
import uuid

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from app.config import (
    ADS_API_BASE_URL,
    QDRANT_URL,
    NEW_LINK,
    QDRANT_TEXT_COLLECTION, QDRANT_IMAGE_COLLECTION,
)
from app.client.ads_api import AdsApiClient
from app.db.qdrant import make_qdrant, ensure_collections, upsert_point
from app.db.sql_repo import ensure_schema, upsert_ad, upsert_photo, photo_exists
from app.embeddings.clip_hf import ClipHFEmbedder

MODEL_NAME = "openai/clip-vit-base-patch32"

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def photo_id_for(ad_id: str, source_url: str) -> str:
    return sha1(f"{ad_id}||{source_url}")

logging.basicConfig(filename="dags.log", level=logging.INFO)
_LOG = logging.getLogger()
_LOG.addHandler(logging.StreamHandler())

@dag(
    dag_id="parse_ads_photos_text_embeddings",
    start_date=datetime(2026, 1, 1),
    schedule="*/30 * * * *",
    catchup=False,
    max_active_runs=10,
)
def pipeline_dag():

    @task
    def init_infra():
        hook = PostgresHook(postgres_conn_id="app_db")
        ensure_schema(hook)

        q = make_qdrant(QDRANT_URL)
        clip = ClipHFEmbedder(model_name=MODEL_NAME)
        ensure_collections(
            q,
            text_collection=QDRANT_TEXT_COLLECTION,
            image_collection=QDRANT_IMAGE_COLLECTION,
            text_dim=clip.dim,
            image_dim=clip.dim,
        )
        return True

    @task
    def get_ids() -> list[str]:
        api = AdsApiClient(ADS_API_BASE_URL)
        res = api.list_ad_ids(query=NEW_LINK)[:5]
        print(res)
        return res

    @task
    def process_one(ad_ids: str):

        print(ad_ids)

        api = AdsApiClient(ADS_API_BASE_URL)
        qdrant = make_qdrant(QDRANT_URL)
        clip = ClipHFEmbedder(model_name=MODEL_NAME)

        hook = PostgresHook(postgres_conn_id="app_db")

        for ad_id in ad_ids:

            data = api.get_ad(ad_id)
            print(data)
            description = data.get("description") or ""
            meta = data.get("meta") or {}
            photos = data.get("photos") or []

            upsert_ad(hook, ad_id, description, json.dumps(meta, ensure_ascii=False), "PENDING")

            if description.strip():
                vec = clip.embed_text(description)
                upsert_point(
                    qdrant,
                    collection=QDRANT_TEXT_COLLECTION,
                    point_id=str(uuid.uuid4()),
                    vector=vec,
                    payload={"ad_id": ad_id, "type": "ad_text"},
                )

            for p in photos:

                src_url = p
                if not src_url:
                    continue

                pid = photo_id_for(ad_id, src_url)

                if photo_exists(hook, pid):
                    continue

                img_bytes = api.download_photo_bytes(src_url)

                upsert_photo(hook, pid, ad_id, src_url)

                img_vec = clip.embed_image_bytes(img_bytes)

                upsert_point(
                    qdrant,
                    collection=QDRANT_IMAGE_COLLECTION,
                    point_id=str(uuid.uuid4()),
                    vector=img_vec,
                    payload={"ad_id": ad_id, "photo_id": src_url, "type": "ad_photo", "pid": pid},
                )

            upsert_ad(hook, ad_id, description, json.dumps(meta, ensure_ascii=False), "READY")


    ok = init_infra()
    ids = get_ids()
    ok >> process_one(ad_ids=ids)
    # ok >> ids

pipeline_dag()
