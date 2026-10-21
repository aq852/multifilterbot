import re


_PART_PATTERNS = (
    re.compile(r"^(?P<base>.+?)(?:[._-])(?P<number>\d{3})$", re.IGNORECASE),
    re.compile(r"^(?P<base>.+?)[._-]part(?P<number>\d+)$", re.IGNORECASE),
)


def split_part_info(name: str | None) -> tuple[str, int] | None:
    value = (name or "").strip()
    for pattern in _PART_PATTERNS:
        match = pattern.match(value)
        if match:
            return match.group("base"), int(match.group("number"))
    return None
