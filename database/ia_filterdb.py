import logging
from struct import pack
import re
import time
import base64
import asyncio
from typing import List, Dict, Any, Optional
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError, BulkWriteError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER, MAX_LAZY_BTNS
from utils import get_settings, save_group_settings, temp
from database.multi_mongo import multi_db
from database.vps_cache import vps_cache

try:
    from fuzzywuzzy import fuzz
except ImportError:
    try:
        from thefuzz import fuzz
    except ImportError:
        fuzz = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME


class MediaItem:
    """
    Unified lightweight proxy wrapper compatible with Pyrogram templates and umongo Media
    Provides access to ._id, .file_id, .id, .file_name, .file_size, .file_type, .mime_type, .caption
    """
    def __init__(self, doc: Dict[str, Any]):
        self._id = str(doc.get('_id', ''))
        self.id = str(doc.get('_id', ''))
        self.file_id = str(doc.get('_id', ''))
        self.file_ref = doc.get('file_ref')
        self.file_name = doc.get('file_name', '')
        self.file_size = doc.get('file_size', 0)
        self.file_type = doc.get('file_type')
        self.mime_type = doc.get('mime_type')
        self.caption = doc.get('caption')

    def to_dict(self) -> Dict[str, Any]:
        return {
            '_id': self.file_id,
            'file_ref': self.file_ref,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'caption': self.caption
        }


async def save_file(media):
    """Save single file in the active writable database."""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    doc = {
        '_id': file_id,
        'file_ref': file_ref,
        'file_name': file_name,
        'file_size': media.file_size,
        'file_type': media.file_type,
        'mime_type': media.mime_type,
        'caption': media.caption.html if media.caption else None,
    }

    writable_col, db_info = await multi_db.get_writable_collection()
    try:
        await writable_col.insert_one(doc)
        logger.info(f"{getattr(media, 'file_name', 'NO_FILE')} is saved to {db_info.get('db_alias', 'DB')}")
        return True, 1
    except DuplicateKeyError:
        logger.warning(f"{getattr(media, 'file_name', 'NO_FILE')} is already saved")
        return False, 0
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return False, 2


async def save_files_batch(media_list):
    """
    ⚡ Indexing Booster with Multi-MongoDB Auto-Routing:
    Bulk save a batch of media files into the currently active writable database.
    If the database reaches >= 90% capacity, it automatically switches writes to the next available cluster!
    """
    if not media_list:
        return 0, 0, 0

    saved_count = 0
    duplicate_count = 0
    error_count = 0

    documents = []
    for media in media_list:
        try:
            file_id, file_ref = unpack_new_file_id(media.file_id)
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
            doc = {
                '_id': file_id,
                'file_ref': file_ref,
                'file_name': file_name,
                'file_size': media.file_size,
                'file_type': media.file_type,
                'mime_type': media.mime_type,
                'caption': media.caption.html if media.caption else None,
            }
            documents.append(doc)
        except Exception:
            error_count += 1

    if not documents:
        return saved_count, duplicate_count, error_count

    writable_col, db_info = await multi_db.get_writable_collection()

    try:
        result = await writable_col.insert_many(documents, ordered=False)
        saved_count = len(result.inserted_ids)
    except BulkWriteError as bwe:
        details = bwe.details
        saved_count = details.get('nInserted', 0)
        write_errors = details.get('writeErrors', [])
        for err in write_errors:
            if err.get('code') == 11000:
                duplicate_count += 1
            else:
                error_count += 1
    except Exception as exc:
        logger.error(f"Bulk insert error in {db_info.get('db_alias', 'cluster')}: {exc}")
        error_count += len(documents)

    return saved_count, duplicate_count, error_count


# Fast In-Memory RAM Cache for Sub-Millisecond Search Response
_LOCAL_SEARCH_CACHE = {}


async def get_search_results_badAss_LazyDeveloperr(chat_id, lazy_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """
    ⚡ Multi-MongoDB Parallel Search Engine with Accurate Pagination & VPS Disk Cache:
    1. Local RAM Cache (sub-millisecond)
    2. VPS High-Capacity SQLite Disk Cache (< 1ms, zero network overhead)
    3. Redis RAM Cache Check
    4. Parallel Query across ALL connected MongoDB clusters (asyncio.gather)
    5. Deduplication & Enterprise Fuzzy Relevance Scoring
    6. Accurate Total Count across all clusters for perfect 1/N page calculation
    """
    max_results = int(MAX_LAZY_BTNS) if MAX_LAZY_BTNS else 10
    query = query.strip()

    cache_key = f"{query.lower()}:{file_type}:{offset}:{max_results}"
    now = time.time()

    # ⚡ 1. Local In-Memory RAM Cache Check
    if cache_key in _LOCAL_SEARCH_CACHE:
        cached_entry = _LOCAL_SEARCH_CACHE[cache_key]
        if now - cached_entry['time'] < 300:  # 5 min TTL
            files, n_offset, total_res = cached_entry['data']
            try:
                temp.LAZY_LOCAL_FILES[f"{chat_id}-{lazy_id}"] = files
            except Exception:
                pass
            return files, n_offset, total_res

    # ⚡ 2. VPS High-Capacity SQLite Disk Cache Check (Sub-millisecond)
    try:
        cached_vps = await vps_cache.get(cache_key)
        if cached_vps:
            files_raw, n_offset, total_res = cached_vps
            files = [MediaItem(f) for f in files_raw]
            try:
                temp.LAZY_LOCAL_FILES[f"{chat_id}-{lazy_id}"] = files
            except Exception:
                pass
            _LOCAL_SEARCH_CACHE[cache_key] = {'data': (files, n_offset, total_res), 'time': now}
            return files, n_offset, total_res
    except Exception as e:
        logger.debug(f"[Search Engine] VPS cache read notice: {e}")

    # ⚡ 3. Check Redis RAM Cache
    try:
        from database.redis_db import redis_db
        cached = await redis_db.get_json_cache(f"search_res:{cache_key}")
        if cached:
            file_ids = cached.get("file_ids", [])
            next_offset = cached.get("next_offset", "")
            total_results = cached.get("total_results", 0)
            if file_ids:
                docs = await Media.find({'_id': {'$in': file_ids}}).to_list(length=len(file_ids))
                id_map = {f.id: f for f in docs}
                files = [id_map[fid] for fid in file_ids if fid in id_map]
                if files:
                    try:
                        temp.LAZY_LOCAL_FILES[f"{chat_id}-{lazy_id}"] = files
                    except Exception:
                        pass
                    _LOCAL_SEARCH_CACHE[cache_key] = {'data': (files, next_offset, total_results), 'time': now}
                    return files, next_offset, total_results
    except Exception:
        pass

    # Build Regex Query Pattern
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + re.escape(query) + r'(\b|[\.\+\-_])'
    else:
        words = query.split()
        raw_pattern = r'.*'.join([re.escape(w) for w in words])

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except Exception:
        return [], '', 0

    if USE_CAPTION_FILTER:
        db_filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        db_filter = {'file_name': regex}

    if file_type:
        db_filter['file_type'] = file_type

    # ⚡ 4. Fast Parallel Query Across ALL Connected MongoDB Clusters
    search_targets = multi_db.get_all_search_collections()
    if not search_targets:
        search_targets = [(Media.collection, {"db_alias": "Master DB"})]

    fuzzy_used = False
    fuzzy_filter = None

    async def _query_single_cluster(col, db_info):
        nonlocal fuzzy_used, fuzzy_filter
        try:
            cursor = col.find(db_filter).skip(offset).limit(max_results * 4)
            found = await cursor.to_list(length=max_results * 4)

            # Auto-fuzzy fallback if nothing matched
            if not found:
                words = [w for w in query.split() if w]
                clean_query = re.sub(r'(.)\1{2,}', r'\1', query, flags=re.IGNORECASE)
                fuzzy_patterns = [r'(\b|[\.\+\-_])' + re.escape(clean_query) + r'(\b|[\.\+\-_])']
                if words:
                    prefix_parts = [re.escape(w[:max(3, len(w)-2)]) for w in words if len(w) >= 3]
                    if prefix_parts:
                        fuzzy_patterns.append(r'.*'.join(prefix_parts))
                combined_pattern = '|'.join(fuzzy_patterns)
                fuzzy_regex = re.compile(combined_pattern, flags=re.IGNORECASE)
                fuzzy_filter = {'$or': [{'file_name': fuzzy_regex}, {'caption': fuzzy_regex}]} if USE_CAPTION_FILTER else {'file_name': fuzzy_regex}
                if file_type:
                    fuzzy_filter['file_type'] = file_type
                fuzzy_used = True
                f_cursor = col.find(fuzzy_filter).limit(max_results * 4)
                found = await f_cursor.to_list(length=max_results * 4)

            return [MediaItem(d) for d in found]
        except Exception as e:
            logger.error(f"[Parallel Search] Error on cluster {db_info.get('db_alias', 'cluster')}: {e}")
            return []

    # Run all queries concurrently
    tasks = [_query_single_cluster(col, info_dict) for col, info_dict in search_targets]
    results_nested = await asyncio.gather(*tasks, return_exceptions=True)

    # Flatten and deduplicate candidates by _id
    seen_ids = set()
    candidate_files = []
    for res in results_nested:
        if isinstance(res, list):
            for file_item in res:
                if file_item.id not in seen_ids:
                    seen_ids.add(file_item.id)
                    candidate_files.append(file_item)

    if not candidate_files:
        return [], '', 0

    # 🚀 5. Accurate Total Count across all clusters for perfect pagination
    active_count_filter = fuzzy_filter if (fuzzy_used and fuzzy_filter) else db_filter
    try:
        count_tasks = [col.count_documents(active_count_filter) for col, _ in search_targets]
        counts = await asyncio.gather(*count_tasks, return_exceptions=True)
        total_results = sum(c for c in counts if isinstance(c, int))
        if total_results == 0:
            total_results = offset + len(candidate_files)
    except Exception as e:
        logger.error(f"Error calculating total count: {e}")
        total_results = offset + len(candidate_files)

    # Next offset for pagination
    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = ''

    # 🚀 6. Enterprise Relevance Scoring & Precision Sorting
    def calculate_relevance(file_obj):
        fname = getattr(file_obj, 'file_name', '') or ''
        q_l = query.lower()
        f_l = fname.lower()
        if fuzz:
            score = (fuzz.token_set_ratio(q_l, f_l) * 0.5) + (fuzz.partial_ratio(q_l, f_l) * 0.5)
        else:
            score = 100 if q_l in f_l else 0
        tokens = [t for t in re.split(r'[\s._\-\[\(]', f_l) if t]
        if tokens and tokens[0] == q_l:
            score += 50
        elif q_l in f_l and f_l.index(q_l) < 5:
            score += 30
        elif any(t == q_l for t in tokens):
            score += 10
        return score

    candidate_files.sort(key=calculate_relevance, reverse=True)
    files = candidate_files[:max_results]

    try:
        key = f"{chat_id}-{lazy_id}"
        temp.LAZY_LOCAL_FILES[key] = candidate_files
    except Exception:
        pass

    # Save to Local RAM Cache
    _LOCAL_SEARCH_CACHE[cache_key] = {'data': (files, next_offset, total_results), 'time': now}
    if len(_LOCAL_SEARCH_CACHE) > 1000:
        oldest = min(_LOCAL_SEARCH_CACHE.keys(), key=lambda k: _LOCAL_SEARCH_CACHE[k]['time'])
        _LOCAL_SEARCH_CACHE.pop(oldest, None)

    # ⚡ 7. Save into VPS High-Capacity SQLite Disk Cache for persistent sub-millisecond retrieval
    try:
        files_dict_list = [f.to_dict() for f in files]
        await vps_cache.set(cache_key, files_dict_list, next_offset, total_results, ttl=3600)
    except Exception as e:
        logger.debug(f"[Search Engine] VPS cache write notice: {e}")

    # Save to Redis RAM Cache if available
    try:
        from database.redis_db import redis_db
        cached_payload = {
            "file_ids": [f.id for f in files],
            "next_offset": next_offset,
            "total_results": total_results
        }
        await redis_db.set_json_cache(f"search_res:{cache_key}", cached_payload, ttl=600)
    except Exception:
        pass

    return files, next_offset, total_results


async def get_search_results(query, file_type=None, max_results=10, offset=0, filter=False):
    """Fallback search"""
    return await get_search_results_badAss_LazyDeveloperr(0, 0, query, file_type, max_results, offset, filter)


async def get_file_details(query):
    """
    Search across all connected MongoDB clusters for file details.
    """
    # 1. Search in multi_mongo clusters
    search_targets = multi_db.get_all_search_collections()
    for col, db_info in search_targets:
        try:
            doc = await col.find_one({"$or": [{"_id": query}, {"file_id": query}]})
            if doc:
                return [MediaItem(doc)]
        except Exception:
            continue

    # 2. Fallback to default Media collection
    try:
        cursor = Media.find({'file_id': query})
        filedetails = await cursor.to_list(length=1)
        if filedetails:
            return filedetails
    except Exception:
        pass

    return []


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
