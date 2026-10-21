import re


def normalize_code(value: str) -> str:
    return re.sub(r"[^A-Z0-9_-]", "", value.upper())


def redeem_charge_id(code: str, user_id: int) -> str:
    return f"redeem:{normalize_code(code)}:{user_id}"

