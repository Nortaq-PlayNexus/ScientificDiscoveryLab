"""Deterministic RNG — standalone fallback.

The lab's canonical implementation lives in
`04_SHARED_ENGINE/engine/utilities/core.py` and is imported by preference. This
module exists so the battery runs unchanged outside the lab checkout, which is
how it is published.

The contract is identical and must stay identical: **all** randomness flows
through `rng(label, seed)`, a sha256-derived `numpy.Generator`. Python's builtin
`hash()` is salted per process, so it cannot be used for reproducible streams.

Two implementations must agree bit-for-bit. `tests/test_battery.py` asserts
they do when the lab engine is importable.
"""

from __future__ import annotations

import hashlib
from typing import Any

#: Ladder of seeds used when a study needs multiple independent streams.
SEED_LADDER = (42, 7, 123, 2023, 314159, 271828)


def seed_value(label: str, seed: int = 0) -> int:
    """Deterministic integer from label+seed.

    Mirrors the lab contract exactly: the first 16 hex digits of
    sha256(f"{label}:{seed}") as an integer.
    """
    digest = hashlib.sha256(f"{label}:{seed}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def rng(label: str, seed: int = 0):
    """A numpy Generator for a named, reproducible stream."""
    import numpy as np

    return np.random.default_rng(seed_value(label, seed))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    """SHA-256 of a canonical JSON encoding (sorted keys, tight separators)."""
    import json

    return sha256_text(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
