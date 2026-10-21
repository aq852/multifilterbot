def build_file_payload(chat_id: int, message_id: int) -> str:
    return f"file_{chat_id}_{message_id}"


def parse_file_payload(payload: str | None) -> tuple[int, int] | None:
    if not payload or not payload.startswith("file_"):
        return None
    parts = payload.split("_")
    if len(parts) != 3:
        return None
    try:
        return int(parts[1]), int(parts[2])
    except ValueError:
        return None
