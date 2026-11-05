import logging
import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import info

logger = logging.getLogger(__name__)

# Default max storage limit for MongoDB Atlas M0 free tier in MB (512MB max, default threshold 500MB)
DEFAULT_MAX_DB_SIZE_MB = 500.0
CAPACITY_THRESHOLD_PERCENT = 90.0  # Mark as Read-Only when >= 90%

class MultiMongoManager:
    """
    ⚡ Dynamic Multi-MongoDB Cluster Manager
    - Supports N multiple MongoDB databases dynamically.
    - Automatically checks cluster-wide storage capacity via dbstats.
    - If any database cluster hits >= 90% full, automatically marks it as READ-ONLY and switches
      all new indexing/writes to the next available database with the most free space.
    - Enables high-speed parallel search across ALL connected databases simultaneously.
    - Fully controllable by Bot Admins via Telegram UI (/mongo).
    """

    def __init__(self):
        self._master_client: Optional[AsyncIOMotorClient] = None
        self._master_db = None
        self._registry_col = None
        self._clients: Dict[str, AsyncIOMotorClient] = {}
        self._collections: Dict[str, Any] = {}
        self._db_info: Dict[str, Dict[str, Any]] = {}
        self._is_initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize connection to Master DB and load all registered database clusters."""
        async with self._lock:
            if self._is_initialized:
                return

            try:
                self._master_client = AsyncIOMotorClient(info.DATABASE_URI)
                self._master_db = self._master_client[info.DATABASE_NAME]
                self._registry_col = self._master_db["file_databases"]

                # Ensure Master DB itself is registered as DB-1 (Primary)
                primary_doc = await self._registry_col.find_one({"is_primary": True})
                if not primary_doc:
                    existing = await self._registry_col.find_one({"db_uri": info.DATABASE_URI})
                    if not existing:
                        initial_db_doc = {
                            "db_alias": "DB-1 (Primary)",
                            "db_uri": info.DATABASE_URI,
                            "db_name": info.DATABASE_NAME,
                            "col_name": info.COLLECTION_NAME,
                            "is_primary": True,
                            "read_only": False,
                            "max_size_mb": DEFAULT_MAX_DB_SIZE_MB,
                            "current_size_mb": 0.0,
                            "usage_percent": 0.0,
                            "file_count": 0,
                            "status": "active",
                            "added_at": time.time(),
                        }
                        result = await self._registry_col.insert_one(initial_db_doc)
                        logger.info(f"[MultiMongo] Registered Primary DB #1 (ID: {result.inserted_id})")

                # Load all registered databases into live pool
                cursor = self._registry_col.find({})
                async for doc in cursor:
                    await self._mount_database(doc)

                # Run initial capacity stats check
                await self.update_all_stats()
                self._is_initialized = True
                logger.info(f"[MultiMongo] Successfully initialized with {len(self._clients)} database cluster(s)!")

            except Exception as e:
                logger.error(f"[MultiMongo] Initialization error: {e}", exc_info=True)

    async def _mount_database(self, doc: Dict[str, Any]) -> bool:
        """Connects and mounts a single database into live runtime pool."""
        db_id = str(doc["_id"])
        db_uri = doc["db_uri"]
        db_name = doc["db_name"]
        col_name = doc["col_name"]

        try:
            client = AsyncIOMotorClient(db_uri, serverSelectionTimeoutMS=5000)
            # Test ping
            await client.admin.command('ping')

            target_db = client[db_name]
            target_col = target_db[col_name]

            # Ensure text / wildcard search indexes on target collection
            try:
                await target_col.create_index([("file_name", "text")])
                await target_col.create_index([("file_name", 1)])
            except Exception as ie:
                logger.debug(f"[MultiMongo] Index creation notice for {doc.get('db_alias')}: {ie}")

            self._clients[db_id] = client
            self._collections[db_id] = target_col
            self._db_info[db_id] = doc
            logger.info(f"[MultiMongo] Mounted cluster: {doc.get('db_alias', db_name)}")
            return True
        except Exception as e:
            logger.error(f"[MultiMongo] Failed to mount cluster {doc.get('db_alias', db_name)}: {e}")
            self._db_info[db_id] = doc
            self._db_info[db_id]["status"] = "error"
            self._db_info[db_id]["error_msg"] = str(e)
            return False

    async def _compute_cluster_storage(self, client: AsyncIOMotorClient, default_db_name: str) -> Tuple[float, float]:
        """
        Calculates cluster-wide total storage across all non-system databases in this MongoDB cluster.
        Returns: (size_mb, storage_bytes)
        """
        total_storage_bytes = 0
        total_data_bytes = 0
        try:
            dbs_in_cluster = await client.list_database_names()
            for d_name in dbs_in_cluster:
                if d_name in ["local", "admin"]:
                    continue
                try:
                    s = await client[d_name].command("dbstats")
                    total_storage_bytes += s.get("storageSize", 0)
                    total_data_bytes += s.get("dataSize", 0)
                except Exception:
                    pass
        except Exception:
            try:
                stats = await client[default_db_name].command("dbstats")
                total_storage_bytes = stats.get("storageSize", 0)
                total_data_bytes = stats.get("dataSize", 0)
            except Exception:
                pass

        used_bytes = max(total_storage_bytes, total_data_bytes)
        size_mb = round(used_bytes / (1024 * 1024), 2)
        return size_mb, used_bytes

    async def update_all_stats(self) -> List[Dict[str, Any]]:
        """Calculates dbstats for all clusters and updates read-only status if >= 90% full."""
        summaries = []
        for db_id, client in list(self._clients.items()):
            doc = self._db_info.get(db_id, {})
            db_name = doc.get("db_name", info.DATABASE_NAME)
            col_name = doc.get("col_name", info.COLLECTION_NAME)
            max_size_mb = float(doc.get("max_size_mb", DEFAULT_MAX_DB_SIZE_MB))

            try:
                target_db = client[db_name]
                target_col = target_db[col_name]

                # ⚡ Accurate Cluster-wide Storage Calculation (matches Atlas Dashboard)
                size_mb, _ = await self._compute_cluster_storage(client, db_name)
                usage_percent = round((size_mb / max_size_mb) * 100, 1) if max_size_mb > 0 else 0.0

                try:
                    file_count = await target_col.estimated_document_count()
                except Exception:
                    file_count = 0

                # Check 90% auto-seal rule
                is_full = usage_percent >= CAPACITY_THRESHOLD_PERCENT
                read_only = doc.get("read_only", False) or is_full
                status = "full (read-only)" if is_full else ("read-only" if read_only else "active")

                # Update registry in Master DB
                update_fields = {
                    "current_size_mb": size_mb,
                    "usage_percent": usage_percent,
                    "file_count": file_count,
                    "read_only": read_only,
                    "status": status,
                    "last_checked": time.time(),
                }
                await self._registry_col.update_one({"_id": doc["_id"]}, {"$set": update_fields})

                # Update in-memory dict
                self._db_info[db_id].update(update_fields)
                summaries.append(self._db_info[db_id])

            except Exception as e:
                logger.error(f"[MultiMongo] Error updating stats for {doc.get('db_alias', db_name)}: {e}")
                self._db_info[db_id]["status"] = "error"
                self._db_info[db_id]["error_msg"] = str(e)
                summaries.append(self._db_info[db_id])

        return summaries

    async def get_writable_collection(self) -> Tuple[Any, Dict[str, Any]]:
        """
        ⚡ Smart Write Router:
        Returns the collection instance for writing new files during Indexing.
        Automatically filters out any database that is >= 90% full or marked read-only.
        Picks the database with the MOST available free space (lowest usage_percent).
        """
        if not self._is_initialized:
            await self.initialize()

        # Find eligible writable databases
        writable_candidates = []
        for db_id, doc in self._db_info.items():
            if db_id in self._collections and not doc.get("read_only", False):
                usage = doc.get("usage_percent", 0.0)
                if usage < CAPACITY_THRESHOLD_PERCENT:
                    writable_candidates.append((usage, db_id))

        if writable_candidates:
            # Sort by lowest usage percent (most free space)
            writable_candidates.sort(key=lambda x: x[0])
            best_db_id = writable_candidates[0][1]
            return self._collections[best_db_id], self._db_info[best_db_id]

        # If all databases are >= 90% full, pick the one with lowest usage and send warning
        logger.warning("[MultiMongo] ⚠️ ALL DATABASES REACHED >= 90% CAPACITY! Writing to database with least usage.")
        all_candidates = []
        for db_id, doc in self._db_info.items():
            if db_id in self._collections:
                all_candidates.append((doc.get("usage_percent", 100.0), db_id))

        if all_candidates:
            all_candidates.sort(key=lambda x: x[0])
            fallback_id = all_candidates[0][1]
            return self._collections[fallback_id], self._db_info[fallback_id]

        # Extreme fallback to Master DB
        primary_col = self._master_db[info.COLLECTION_NAME]
        return primary_col, {"db_alias": "Master DB Fallback"}

    def get_all_search_collections(self) -> List[Tuple[Any, Dict[str, Any]]]:
        """
        Returns list of (collection, db_info) across ALL active connected databases
        (both writable and read-only) for parallel search querying.
        """
        targets = []
        for db_id, col in self._collections.items():
            info_dict = self._db_info.get(db_id, {})
            targets.append((col, info_dict))
        return targets

    async def add_database(self, db_uri: str, db_name: str, col_name: str, max_size_mb: float = DEFAULT_MAX_DB_SIZE_MB) -> Tuple[bool, str]:
        """
        Admin API to validate and add a new MongoDB database cluster on the fly.
        """
        db_uri = db_uri.strip()
        db_name = db_name.strip()
        col_name = col_name.strip()

        # Verify duplicate URI / DB
        existing = await self._registry_col.find_one({
            "db_uri": db_uri,
            "db_name": db_name,
            "col_name": col_name
        })
        if existing:
            return False, f"Database with same URI, DB Name ({db_name}) and Collection ({col_name}) is already added!"

        # Test connection
        try:
            test_client = AsyncIOMotorClient(db_uri, serverSelectionTimeoutMS=7000)
            await test_client.admin.command('ping')
            size_mb, _ = await self._compute_cluster_storage(test_client, db_name)
        except ServerSelectionTimeoutError:
            return False, "❌ Connection Timed Out! Please verify your IP Whitelist (0.0.0.0/0) and credentials in MongoDB Atlas."
        except ConnectionFailure as cf:
            return False, f"❌ Connection Failed: {cf}"
        except Exception as e:
            return False, f"❌ Verification Error: {e}"

        # Count existing databases to assign alias
        total_dbs = await self._registry_col.count_documents({})
        alias = f"DB-{total_dbs + 1}"

        usage_percent = round((size_mb / max_size_mb) * 100, 1) if max_size_mb > 0 else 0.0
        is_full = usage_percent >= CAPACITY_THRESHOLD_PERCENT
        status = "full (read-only)" if is_full else "active"

        new_doc = {
            "db_alias": alias,
            "db_uri": db_uri,
            "db_name": db_name,
            "col_name": col_name,
            "is_primary": False,
            "read_only": is_full,
            "max_size_mb": max_size_mb,
            "current_size_mb": size_mb,
            "usage_percent": usage_percent,
            "file_count": 0,
            "status": status,
            "added_at": time.time(),
        }

        res = await self._registry_col.insert_one(new_doc)
        new_doc["_id"] = res.inserted_id

        # Mount live into pool
        mounted = await self._mount_database(new_doc)
        if mounted:
            return True, f"✅ Successfully connected and mounted <b>{alias} ({db_name})</b>!\nCurrent Usage: <b>{usage_percent}%</b> ({size_mb} MB / {max_size_mb} MB)"
        else:
            return False, "⚠️ Database was saved to registry but failed to mount to live pool."

    async def remove_database(self, db_id_str: str) -> Tuple[bool, str]:
        """Admin API to remove a database from the cluster registry."""
        from bson import ObjectId
        try:
            obj_id = ObjectId(db_id_str)
        except Exception:
            return False, "Invalid Database ID format."

        doc = await self._registry_col.find_one({"_id": obj_id})
        if not doc:
            return False, "Database not found in registry."

        if doc.get("is_primary"):
            return False, "❌ Cannot delete the Primary Database #1 (Master DB)!"

        # Close client connection
        client = self._clients.pop(db_id_str, None)
        if client:
            try:
                client.close()
            except Exception:
                pass

        self._collections.pop(db_id_str, None)
        self._db_info.pop(db_id_str, None)

        await self._registry_col.delete_one({"_id": obj_id})
        return True, f"✅ Successfully removed database <b>{doc.get('db_alias', 'cluster')}</b> from pool!"

    async def toggle_read_only(self, db_id_str: str) -> Tuple[bool, str]:
        """Toggle read-only flag manually for a specific database."""
        from bson import ObjectId
        try:
            obj_id = ObjectId(db_id_str)
        except Exception:
            return False, "Invalid Database ID."

        doc = await self._registry_col.find_one({"_id": obj_id})
        if not doc:
            return False, "Database not found."

        new_status = not doc.get("read_only", False)
        await self._registry_col.update_one({"_id": obj_id}, {"$set": {"read_only": new_status}})
        if db_id_str in self._db_info:
            self._db_info[db_id_str]["read_only"] = new_status

        status_label = "🔒 READ-ONLY" if new_status else "✍️ WRITABLE"
        return True, f"Updated <b>{doc.get('db_alias')}</b> status to <b>{status_label}</b>."

    async def get_databases_summary(self) -> List[Dict[str, Any]]:
        """Returns all database cluster records with up-to-date stats."""
        await self.update_all_stats()
        cursor = self._registry_col.find({}).sort("added_at", 1)
        results = []
        async for doc in cursor:
            results.append(doc)
        return results

multi_db = MultiMongoManager()
