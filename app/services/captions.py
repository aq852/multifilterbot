from typing import Any


def render_caption(template: str, file: dict[str, Any]) -> str:
    values = {
        "title": file.get("title") or file.get("name") or "untitled",
        "name": file.get("name") or "untitled",
        "type": file.get("media_type") or "file",
        "size": format_size(file.get("size")),
    }
    try:
        return template.format_map(values)
    except (KeyError, ValueError):
        return values["title"]


def format_size(size: int | None) -> str:
    if not size:
        return "unknown size"
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return "unknown size"

