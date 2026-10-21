import re
from typing import Any

from app.database import get_database
from app.services.metadata import extract_metadata
from app.services.search import build_search_terms, normalize_title
from app.services.search import parse_media_filter, parse_search_filters, search_pattern
from app.services.split_parts import split_part_info


async def save_file(document: dict[str, Any]) -> bool:
    result = await get_database().files.update_one(
        {"chat_id": document["chat_id"], "message_id": document["message_id"]},
        {"$set": document}, upsert=True
    )
    return result.upserted_id is not None or result.modified_count > 0


async def search_files(query: str, limit: int = 5, skip: int = 0, media_type: str | None = None) -> list[dict[str, Any]]:
    query, detected_type = parse_media_filter(query)
    query, metadata_filters = parse_search_filters(query)
    media_type = media_type or detected_type
    pattern = search_pattern(query)
    filters: dict[str, Any] = {"$or": [{"normalized_title": {"$regex": pattern}},
                                        {"search_terms": {"$regex": pattern}}]}
    if media_type:
        filters["media_type"] = media_type
    filters.update(metadata_filters)
    normalized_query = normalize_title(query)
    pipeline = [
        {"$match": filters},
        {"$addFields": {
            "_match_rank": {
                "$cond": [
                    {"$eq": ["$normalized_title", normalized_query]},
                    0,
                    {"$cond": [
                        {"$regexMatch": {"input": {"$ifNull": ["$normalized_title", ""]}, "regex": f"^{pattern}"}},
                        1,
                        2,
                    ]},
                ]
            },
            "_popularity": {"$ifNull": ["$downloads", 0]},
        }},
        {"$sort": {"_match_rank": 1, "_popularity": -1, "title": 1}},
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {
            "name": 1, "title": 1, "chat_id": 1, "message_id": 1,
            "media_type": 1, "size": 1, "downloads": 1,
        }},
    ]
    return await get_database().files.aggregate(pipeline).to_list(length=limit)


async def count_search_files(query: str) -> int:
    query, media_type = parse_media_filter(query)
    query, metadata_filters = parse_search_filters(query)
    pattern = search_pattern(query)
    filters: dict[str, Any] = {"$or": [{"normalized_title": {"$regex": pattern}},
                                        {"search_terms": {"$regex": pattern}}]}
    if media_type:
        filters["media_type"] = media_type
    filters.update(metadata_filters)
    return await get_database().files.count_documents(filters)


async def get_file(chat_id: int, message_id: int) -> dict[str, Any] | None:
    return await get_database().files.find_one({"chat_id": chat_id, "message_id": message_id})


async def delete_file(chat_id: int, message_id: int) -> bool:
    result = await get_database().files.delete_one({"chat_id": chat_id, "message_id": message_id})
    if result.deleted_count:
        await get_database().saved_files.delete_many({"chat_id": chat_id, "message_id": message_id})
    return result.deleted_count > 0


async def find_files_by_name(query: str, limit: int = 10) -> list[dict[str, Any]]:
    pattern = re.escape(query.strip())
    if not pattern:
        return []
    cursor = get_database().files.find(
        {"$or": [
            {"name": {"$regex": pattern, "$options": "i"}},
            {"title": {"$regex": pattern, "$options": "i"}},
        ]},
        {"name": 1, "title": 1, "chat_id": 1, "message_id": 1},
    ).sort("title", 1).limit(limit)
    return await cursor.to_list(length=limit)


async def rename_file(chat_id: int, message_id: int, title: str) -> bool:
    clean_title = title.strip()
    if not clean_title:
        return False
    metadata = extract_metadata(clean_title)
    result = await get_database().files.update_one(
        {"chat_id": chat_id, "message_id": message_id},
        {"$set": {
            "title": clean_title,
            "normalized_title": normalize_title(clean_title),
            "search_terms": build_search_terms(clean_title),
            **metadata,
        }},
    )
    return result.matched_count > 0


async def related_files(chat_id: int, message_id: int, limit: int = 10) -> list[dict[str, Any]]:
    source = await get_database().files.find_one(
        {"chat_id": chat_id, "message_id": message_id}, {"search_terms": 1}
    )
    terms = [term for term in (source or {}).get("search_terms", []) if len(term) >= 3][:5]
    if not terms:
        return []
    cursor = get_database().files.find(
        {"$nor": [{"chat_id": chat_id, "message_id": message_id}], "search_terms": {"$in": terms}},
        {"name": 1, "title": 1, "chat_id": 1, "message_id": 1, "media_type": 1},
    ).sort("title", 1).limit(limit)
    return await cursor.to_list(length=limit)


async def find_split_parts(file: dict[str, Any], limit: int = 100) -> list[dict[str, Any]]:
    source_name = file.get("name") or file.get("title") or ""
    parsed = split_part_info(source_name)
    if parsed is None:
        return []
    base, _ = parsed
    pattern = rf"^{re.escape(base)}(?:[._-](?:\d{{3}}|part\d+))$"
    candidates = await get_database().files.find(
        {"$or": [
            {"name": {"$regex": pattern, "$options": "i"}},
            {"title": {"$regex": pattern, "$options": "i"}},
        ]},
        {"name": 1, "title": 1, "chat_id": 1, "message_id": 1, "size": 1},
    ).limit(limit).to_list(length=limit)
    parts = []
    for candidate in candidates:
        candidate_name = candidate.get("name") or candidate.get("title") or ""
        candidate_part = split_part_info(candidate_name)
        if candidate_part and candidate_part[0].lower() == base.lower():
            candidate["part_number"] = candidate_part[1]
            parts.append(candidate)
    return sorted(parts, key=lambda item: item["part_number"])
