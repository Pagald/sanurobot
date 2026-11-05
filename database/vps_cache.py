import os
import sqlite3
import json
import time
import logging
import asyncio
from typing import Optional, Tuple, List, Dict, Any

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vps_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "search_cache.db")

class VPSDiskCache:
    """
    ⚡ High-Performance Local VPS Disk Cache (SQLite WAL Engine)
    Stores frequently searched queries and file results locally on VPS disk.
    Sub-millisecond query response time (< 1ms) with ZERO MongoDB network overhead.
    """
    def __init__(self, db_path: str = CACHE_FILE):
        self.db_path = db_path
        self._ensure_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high concurrency reading/writing
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _ensure_db(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS query_cache (
                        query_key TEXT PRIMARY KEY,
                        files_json TEXT NOT NULL,
                        next_offset TEXT,
                        total_results INTEGER,
                        created_at REAL,
                        ttl INTEGER,
                        hit_count INTEGER DEFAULT 1
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_created ON query_cache (created_at);")
                conn.commit()
        except Exception as e:
            logger.error(f"[VPS Cache] Init error: {e}")

    def _sync_get(self, query_key: str) -> Optional[Tuple[List[Dict[str, Any]], str, int]]:
        try:
            now = time.time()
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT files_json, next_offset, total_results, created_at, ttl FROM query_cache WHERE query_key = ?",
                    (query_key,)
                )
                row = cursor.fetchone()
                if not row:
                    return None

                created_at = row["created_at"]
                ttl = row["ttl"]

                if now - created_at > ttl:
                    # Expired
                    conn.execute("DELETE FROM query_cache WHERE query_key = ?", (query_key,))
                    conn.commit()
                    return None

                # Increment hit counter
                conn.execute(
                    "UPDATE query_cache SET hit_count = hit_count + 1 WHERE query_key = ?",
                    (query_key,)
                )
                conn.commit()

                files = json.loads(row["files_json"])
                return files, row["next_offset"], row["total_results"]
        except Exception as e:
            logger.debug(f"[VPS Cache] Get error: {e}")
            return None

    def _sync_set(self, query_key: str, files_data: List[Dict[str, Any]], next_offset: str, total_results: int, ttl: int = 3600):
        try:
            now = time.time()
            files_json = json.dumps(files_data)
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO query_cache (query_key, files_json, next_offset, total_results, created_at, ttl, hit_count)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(query_key) DO UPDATE SET
                        files_json = excluded.files_json,
                        next_offset = excluded.next_offset,
                        total_results = excluded.total_results,
                        created_at = excluded.created_at,
                        ttl = excluded.ttl;
                """, (query_key, files_json, next_offset, total_results, now, ttl))
                conn.commit()
        except Exception as e:
            logger.debug(f"[VPS Cache] Set error: {e}")

    def _sync_clear(self) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM query_cache;")
                deleted = cursor.rowcount
                conn.execute("VACUUM;")
                conn.commit()
                return deleted
        except Exception as e:
            logger.error(f"[VPS Cache] Clear error: {e}")
            return 0

    def _sync_get_stats(self) -> Dict[str, Any]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*), SUM(hit_count) FROM query_cache;")
                count, total_hits = cursor.fetchone()
                count = count or 0
                total_hits = total_hits or 0

            file_size_bytes = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            size_mb = round(file_size_bytes / (1024 * 1024), 2)

            return {
                "total_cached_queries": count,
                "total_hits": total_hits,
                "disk_size_mb": size_mb,
                "db_path": self.db_path
            }
        except Exception as e:
            return {
                "total_cached_queries": 0,
                "total_hits": 0,
                "disk_size_mb": 0.0,
                "error": str(e)
            }

    # Async wrappers using asyncio.to_thread for seamless non-blocking async Pyrogram compatibility
    async def get(self, query_key: str) -> Optional[Tuple[List[Dict[str, Any]], str, int]]:
        return await asyncio.to_thread(self._sync_get, query_key)

    async def set(self, query_key: str, files_data: List[Dict[str, Any]], next_offset: str, total_results: int, ttl: int = 3600):
        await asyncio.to_thread(self._sync_set, query_key, files_data, next_offset, total_results, ttl)

    async def clear(self) -> int:
        return await asyncio.to_thread(self._sync_clear)

    async def get_stats(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync_get_stats)

vps_cache = VPSDiskCache()
