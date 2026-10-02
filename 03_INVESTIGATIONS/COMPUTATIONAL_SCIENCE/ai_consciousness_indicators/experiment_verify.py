"""Verify the SHA-256 record in a RESULTS/experiment*.json.

Published alongside the results so a reader can confirm the numbers were not
edited after the run. The upstream framework separates two hash scopes, and this
module preserves that separation rather than conflating them:

  result_hash            canonical JSON of the `result` object
                         (allow_nan=False, sorted keys, tight separators)
  result_artifact.sha256 SHA-256 of exact file bytes

A hash of pretty-printed JSON is not the same value, so claiming one verifies
the other would be a false claim. An absent artifact check is reported as
"not checked", never as a pass.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

RESULT_HASH_SCOPE = "canonical_json_utf8_result_object"
RESULT_ARTIFACT_HASH_SCOPE = "exact_artifact_bytes"
CANONICAL_JSON_SPEC = {
    "allow_nan": False,
    "ensure_ascii": False,
    "separators": [",", ":"],
    "sort_keys": True,
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=CANONICAL_JSON_SPEC["allow_nan"],
        ensure_ascii=CANONICAL_JSON_SPEC["ensure_ascii"],
        separators=tuple(CANONICAL_JSON_SPEC["separators"]),
        sort_keys=CANONICAL_JSON_SPEC["sort_keys"],
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def verify_experiment_result_hash(
    record: dict,
    *,
    result_path: str | Path | None = None,
) -> dict[str, Any]:
    """Verify a result record's declared hashes and scopes."""
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
        actual = sha256_json(record["result"])
    except (TypeError, ValueError) as exc:
        report["errors"].append(f"result is not canonical JSON: {exc}")
        return report

    report["result_hash_actual"] = actual
    report["result_hash_recorded"] = record["result_hash"]
    report["result_hash_valid"] = actual == record["result_hash"]
    if not report["result_hash_valid"]:
        report["errors"].append("canonical result SHA-256 mismatch")

    artifact_info = record.get("result_artifact")
    candidate = result_path or (
        artifact_info.get("path") if isinstance(artifact_info, dict) else None
    )
    if candidate is None:
        if artifact_info is not None:
            report["errors"].append("result artifact metadata has no path")
        report["valid"] = (
            report["scope_valid"] and report["result_hash_valid"] and not report["errors"]
        )
        return report

    artifact = Path(candidate).expanduser().resolve()
    report["artifact_checked"] = True
    if not artifact.is_file():
        report["errors"].append(f"result artifact is missing: {artifact}")
        return report
    if not isinstance(artifact_info, dict):
        report["errors"].append("result_artifact metadata is missing")
        return report
    if artifact_info.get("hash_scope") != RESULT_ARTIFACT_HASH_SCOPE:
        report["errors"].append("result_artifact.hash_scope mismatch")

    declared_size = artifact_info.get("size_bytes")
    if type(declared_size) is not int or declared_size < 0:
        report["errors"].append("result_artifact.size_bytes is malformed")
        report["artifact_size_valid"] = False
    else:
        report["artifact_size_actual"] = artifact.stat().st_size
        report["artifact_size_valid"] = artifact.stat().st_size == declared_size
        if not report["artifact_size_valid"]:
            report["errors"].append("result artifact byte-size mismatch")

    actual_file = sha256_file(artifact)
    report["artifact_hash_actual"] = actual_file
    report["artifact_hash_recorded"] = artifact_info.get("sha256")
    report["artifact_hash_valid"] = actual_file == artifact_info.get("sha256")
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


def verify_file(path: str | Path) -> dict[str, Any]:
    """Convenience: load a RESULTS/experiment*.json and verify it."""
    p = Path(path).expanduser().resolve()
    with p.open(encoding="utf-8") as fh:
        record = json.load(fh)
    report = verify_experiment_result_hash(record)
    report["file"] = str(p)
    return report


if __name__ == "__main__":
    import sys

    for arg in sys.argv[1:] or ["RESULTS/experiment.json"]:
        rep = verify_file(arg)
        status = "VALID" if rep["valid"] else "INVALID"
        print(f"{status}  {rep.get('file', arg)}")
        if rep["errors"]:
            for err in rep["errors"]:
                print(f"    - {err}")
        else:
            print(f"    result_hash {rep['result_hash_actual'][:16]}…")
