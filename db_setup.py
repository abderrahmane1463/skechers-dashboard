"""
db_setup.py — Create Supabase tables for Footland dashboard cache.
Run once: python db_setup.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ["SUPABASE_DB_URL"]

SQL = """
CREATE TABLE IF NOT EXISTS metric_cache (
    id          BIGSERIAL PRIMARY KEY,
    metric_key  TEXT        NOT NULL,
    period_start DATE       NOT NULL,
    period_end   DATE       NOT NULL,
    data        JSONB       NOT NULL,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_metric_cache_unique
    ON metric_cache (metric_key, period_start, period_end);

CREATE INDEX IF NOT EXISTS idx_metric_cache_fetched
    ON metric_cache (metric_key, fetched_at DESC);
"""

def setup():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(SQL)
    cur.close()
    conn.close()
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    setup()
