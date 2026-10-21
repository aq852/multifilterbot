from datetime import datetime, timezone
from typing import Any


def file_document(*, chat_id: int, message_id: int, media_type: str, file_id: str,
                  name: str, size: int | None, caption: str | None) -> dict[str, Any]:
    from app.services.search import build_search_terms, normalize_title
    from app.services.metadata import extract_metadata

    title = name or caption or "untitled"
    metadata = extract_metadata(title)
    return {
        "chat_id": chat_id,
        "message_id": message_id,
        "media_type": media_type,
        "file_id": file_id,
        "name": name,
        "caption": caption,
        "title": title,
        "normalized_title": normalize_title(title),
        "search_terms": build_search_terms(title),
        "size": size,
        "created_at": datetime.now(timezone.utc),
        **metadata,
    }
