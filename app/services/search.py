import re

STOP_WORDS = {"a", "an", "and", "in", "of", "on", "the", "to"}


def normalize_title(value: str) -> str:
    value = value.casefold().replace("_", " ").replace(".", " ")
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def build_search_terms(value: str) -> list[str]:
    return sorted({term for term in normalize_title(value).split()
                   if len(term) >= 2 and term not in STOP_WORDS})


def search_pattern(query: str) -> str:
    return re.escape(normalize_title(query))
