def parse_referrer(start_argument: str | None, user_id: int) -> int | None:
    if not start_argument or not start_argument.startswith("ref_"):
        return None
    try:
        referrer_id = int(start_argument[4:])
    except ValueError:
        return None
    return None if referrer_id == user_id else referrer_id

