import hashlib
from datetime import datetime
from typing import Optional


def generate_stable_id(prefix: str, counter: int = 1) -> str:
    return f"{prefix}-{counter:06d}"


def generate_id_from_string(input_string: str) -> str:
    hash_bytes = hashlib.sha256(input_string.encode()).digest()[:6]
    hex_str = hash_bytes.hex()
    return f"ID-{hex_str.upper()}"


def timestamp_now() -> str:
    return datetime.utcnow().isoformat()


def deduplicate_smiles(smiles_list: list) -> list:
    seen = set()
    unique = []
    from src.utils.validator import canonicalize
    for s in smiles_list:
        canonical = canonicalize(s) if s else s
        if canonical not in seen:
            seen.add(canonical)
            unique.append(s)
    return unique


__all__ = [
    "generate_stable_id",
    "generate_id_from_string",
    "timestamp_now",
    "deduplicate_smiles",
]
