"""utilities.core — deterministic RNG, hashing, experiment.json metadata.

Determinism rule (DECISIONS.md): ALL random numbers come from rng(label, seed),
a sha256-derived numpy Generator, independent of Python's per-process hash() salt.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


def seed_value(label: str, seed: int = 0) -> int:
    """Deterministic integer from label+seed (contract from DECISIONS.md)."""
    digest = hashlib.sha256(f"{label}:{seed}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def rng(label: str, seed: int = 0):
    """A numpy random Generator for a named, reproducible stream."""
    import numpy as np

    return np.random.default_rng(seed_value(label, seed))


SEED_LADDER = (42, 7, 123, 2023, 314159, 271828)
RESULT_HASH_SCOPE = "canonical_json_utf8_result_object"
RESULT_ARTIFACT_HASH_SCOPE = "exact_artifact_bytes"
CANONICAL_JSON_SPEC = {
    "allow_nan": False,
    "ensure_ascii": False,
    "separators": [",", ":"],
    "sort_keys": True,
}


def sha256_file(path: str, chunk: int = 1 << 20) -> str:
    """Streaming sha256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically for content hashes.

    Rejects NaN/Infinity and fixes separators, key ordering, and UTF-8 policy so
    the same JSON value has one stable SHA-256 representation.
    """
    return json.dumps(
        value,
        allow_nan=CANONICAL_JSON_SPEC["allow_nan"],
        ensure_ascii=CANONICAL_JSON_SPEC["ensure_ascii"],
        separators=tuple(CANONICAL_JSON_SPEC["separators"]),
        sort_keys=CANONICAL_JSON_SPEC["sort_keys"],
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    """Return the SHA-256 of a value's canonical JSON representation."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def version_info() -> dict:
    """Python + key library versions for experiment.json."""
    import sys

    out = {"python": sys.version.split()[0]}
    for name in ("numpy", "scipy", "matplotlib", "skimage", "sklearn", "sympy"):
        try:
            mod = __import__(name)
            out[name] = getattr(mod, "__version__", "?")
        except Exception:
            out[name] = "not-installed"
    return out


def machine_info() -> dict:
    import platform

    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def make_experiment_json(
    experiment_id: str,
    question: str,
    hypothesis: str,
    seed: int,
    parameters: dict,
    result: dict,
    out_path: str | os.PathLike | None = None,
    extra: dict | None = None,
    result_path: str | os.PathLike | None = None,
) -> dict:
    """Build (and optionally write) a machine-readable experiment record.

    ``result_hash`` is explicitly the hash of the canonical JSON result object.
    When ``result_path`` is supplied, its exact artifact bytes are hashed in a
    separate ``result_artifact`` record. Keeping these scopes separate avoids
    claiming that an in-memory hash verifies differently formatted output bytes.
    """
    from datetime import datetime, timezone

    record = {
        "experiment_id": experiment_id,
        "question": question,
        "hypothesis": hypothesis,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": seed,
        "parameters": parameters,
        "software": version_info(),
        "machine": machine_info(),
        "result": result,
        "result_hash": sha256_json(result),
        "result_hash_scope": RESULT_HASH_SCOPE,
        "canonical_json": dict(CANONICAL_JSON_SPEC),
    }
    if extra:
        record["extra"] = extra
    if result_path is not None:
        artifact = Path(result_path).expanduser().resolve()
        if not artifact.is_file():
            raise FileNotFoundError(f"Result artifact does not exist: {artifact}")
        record["result_artifact"] = {
            "path": str(artifact),
            "sha256": sha256_file(str(artifact)),
            "size_bytes": artifact.stat().st_size,
            "hash_scope": RESULT_ARTIFACT_HASH_SCOPE,
        }
    if out_path is not None:
        target = Path(out_path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as fh:
            json.dump(
                record,
                fh,
                allow_nan=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            fh.write("\n")
    return record


def verify_experiment_result_hash(
    record: dict,
    *,
    result_path: str | os.PathLike | None = None,
) -> dict[str, Any]:
    """Verify canonical result, declared hash scopes, and optional artifact.

    An absent optional artifact check is reported as not checked, never as a
    pass. Declared scope/canonicalization/size metadata must match this helper's
    documented contract.
    """
    report: dict[str, Any] = {
        "valid": False,
        "result_hash_valid": False,
        "scope_valid": False,
        "artifact_checked": False,
        "artifact_hash_valid": None,
        "artifact_size_valid": None,
        "errors": [],
    }
    if "result" not in record or "result_hash" not in record:
        report["errors"].append("missing result or result_hash")
        return report

    if record.get("result_hash_scope") != RESULT_HASH_SCOPE:
        report["errors"].append("result_hash_scope mismatch")
    if record.get("canonical_json") != CANONICAL_JSON_SPEC:
        report["errors"].append("canonical_json declaration mismatch")
    report["scope_valid"] = not report["errors"]

    try:
        actual_result_hash = sha256_json(record["result"])
    except (TypeError, ValueError) as exc:
        report["errors"].append(f"result is not canonical JSON: {exc}")
        return report
    report["result_hash_actual"] = actual_result_hash
    report["result_hash_recorded"] = record["result_hash"]
    report["result_hash_valid"] = actual_result_hash == record["result_hash"]
    if not report["result_hash_valid"]:
        report["errors"].append("canonical result SHA-256 mismatch")

    artifact_info = record.get("result_artifact")
    candidate = result_path if result_path is not None else (
        artifact_info.get("path") if isinstance(artifact_info, dict) else None
    )
    if candidate is None:
        if artifact_info is not None:
            report["errors"].append("result artifact metadata has no path")
        report["valid"] = report["scope_valid"] and report["result_hash_valid"] and not report["errors"]
        return report
    artifact = Path(candidate).expanduser().resolve()
    report["artifact_checked"] = True
    if not artifact.is_file():
        report["errors"].append(f"result artifact is missing: {artifact}")
        return report
    if not isinstance(artifact_info, dict):
        report["errors"].append("result artifact metadata is missing")
        return report
    if artifact_info.get("hash_scope") != RESULT_ARTIFACT_HASH_SCOPE:
        report["errors"].append("result_artifact.hash_scope mismatch")
    declared_path = artifact_info.get("path")
    if not isinstance(declared_path, str) or not declared_path:
        report["errors"].append("result_artifact.path is malformed")
    elif Path(declared_path).expanduser().resolve() != artifact:
        report["errors"].append("result_artifact.path does not match checked path")
    recorded_size = artifact_info.get("size_bytes")
    if type(recorded_size) is not int or recorded_size < 0:
        report["errors"].append("result_artifact.size_bytes is malformed")
        report["artifact_size_valid"] = False
    else:
        actual_size = artifact.stat().st_size
        report["artifact_size_actual"] = actual_size
        report["artifact_size_recorded"] = recorded_size
        report["artifact_size_valid"] = actual_size == recorded_size
        if not report["artifact_size_valid"]:
            report["errors"].append("result artifact byte-size mismatch")

    actual_artifact_hash = sha256_file(str(artifact))
    report["artifact_hash_actual"] = actual_artifact_hash
    report["artifact_hash_recorded"] = artifact_info.get("sha256")
    report["artifact_hash_valid"] = actual_artifact_hash == artifact_info.get("sha256")
    if not report["artifact_hash_valid"]:
        report["errors"].append("result artifact SHA-256 mismatch")
    report["valid"] = (
        report["scope_valid"]
        and report["result_hash_valid"]
        and report["artifact_hash_valid"] is True
        and report["artifact_size_valid"] is True
        and not report["errors"]
    )
    return report