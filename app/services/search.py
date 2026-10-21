import re

STOP_WORDS = {"a", "an", "and", "in", "of", "on", "the", "to"}
MEDIA_TYPES = {"video", "document", "audio", "photo"}


def normalize_title(value: str) -> str:
    value = value.casefold().replace("_", " ").replace(".", " ")
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def build_search_terms(value: str) -> list[str]:
    return sorted({term for term in normalize_title(value).split()
                   if len(term) >= 2 and term not in STOP_WORDS})


def search_pattern(query: str) -> str:
    return re.escape(normalize_title(query))


def parse_media_filter(query: str) -> tuple[str, str | None]:
    prefix, separator, remainder = query.partition(":")
    if separator and prefix.casefold() in MEDIA_TYPES and remainder.strip():
        return remainder.strip(), prefix.casefold()
    return query.strip(), None
