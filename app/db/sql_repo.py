from __future__ import annotations
from airflow.providers.postgres.hooks.postgres import PostgresHook


DDL = """
CREATE TABLE IF NOT EXISTS ads (
  id TEXT PRIMARY KEY,
  description TEXT,
  meta_json TEXT,
  index_status TEXT NOT NULL DEFAULT 'PENDING',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ads_index_status ON ads(index_status);

CREATE TABLE IF NOT EXISTS photos (
  id TEXT PRIMARY KEY,
  ad_id TEXT NOT NULL REFERENCES ads(id) ON DELETE CASCADE,
  source_url TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_photos_ad_id ON photos(ad_id);
"""

def ensure_schema(hook: PostgresHook) -> None:
    hook.run(DDL)

def upsert_ad(hook: PostgresHook, ad_id: str, description: str, meta_json: str, index_status: str) -> None:
    hook.run(
        """
        INSERT INTO ads(id, description, meta_json, index_status, updated_at)
        VALUES (%s, %s, %s, %s, now())
        ON CONFLICT (id) DO UPDATE SET
          description = EXCLUDED.description,
          meta_json = EXCLUDED.meta_json,
          index_status = EXCLUDED.index_status,
          updated_at = now();
        """,
        parameters=(ad_id, description, meta_json, index_status),
    )

def photo_exists(hook: PostgresHook, photo_id: str) -> bool:
    r = hook.get_first("SELECT 1 FROM photos WHERE id = %s", parameters=(photo_id,))
    return r is not None

def upsert_photo(hook: PostgresHook, photo_id: str, ad_id: str, source_url: str) -> None:
    hook.run(
        """
        INSERT INTO photos(id, ad_id, source_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
          ad_id = EXCLUDED.ad_id,
          source_url = EXCLUDED.source_url
        """,
        parameters=(photo_id, ad_id, source_url),
    )
