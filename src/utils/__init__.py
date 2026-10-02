import hashlib
import time
from typing import Optional


def generate_stable_id(prefix: str, counter: int = 1) -> str:
    """Generate a stable ID like PLANT-000001."""
    return f"{prefix}-{counter:06d}"


def generate_id_from_string(input_string: str) -> str:
    """Generate a deterministic ID from any string."""
    hash_bytes = hashlib.sha256(input_string.encode()).digest()[:6]
    hex_str = hash_bytes.hex()
    return f"ID-{hex_str.upper()}"


def timestamp_now() -> str:
    """Get current UTC timestamp as ISO string."""
    from datetime import datetime
    return datetime.utcnow().isoformat()


def deduplicate_smiles(smiles_list: list) -> list:
    """Remove duplicate SMILES, keeping first occurrence."""
    seen = set()
    unique = []
    for s in smiles_list:
        canonical = canonicalize(s) if s else s
        if canonical not in seen:
            seen.add(canonical)
            unique.append(s)
    return unique


def canonicalize(smiles: str) -> Optional[str]:
    """Canonicalize a SMILES string."""
    try:
        from rdkit import Chem
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        pass
    return smiles


__all__ = [
    "generate_stable_id",
    "generate_id_from_string",
    "timestamp_now",
    "deduplicate_smiles",
]
