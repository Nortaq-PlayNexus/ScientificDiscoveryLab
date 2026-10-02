"""Validate the EXP-0003 audit hash manifest without rewriting the bad source.

The historical manifest ends with the literal characters ``\\n`` after its JSON
object. This script preserves that file, salvages only the prefix through the
last closing brace, verifies every listed byte count/SHA-256, and writes a valid
JSON sidecar plus a machine-readable validation report.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "RESULTS" / "artifact_hashes.json"
REPAIRED = ROOT / "RESULTS" / "artifact_hashes_repaired.json"
REPORT = ROOT / "RESULTS" / "artifact_hashes_validation.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_source() -> tuple[dict, dict]:
    raw = SOURCE.read_bytes()
    source_info = {
        "path": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "valid_json_directly": True,
        "direct_parse_error": None,
        "salvaged_through_last_closing_brace": False,
        "trailing_bytes_hex_after_salvage": "",
    }
    try:
        return json.loads(raw), source_info
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        source_info["valid_json_directly"] = False
        source_info["direct_parse_error"] = str(exc)

    last_brace = raw.rfind(b"}")
    if last_brace < 0:
        raise ValueError("Source manifest has no closing JSON brace")
    source_info["salvaged_through_last_closing_brace"] = True
    source_info["trailing_bytes_hex_after_salvage"] = raw[last_brace + 1:].hex()
    return json.loads(raw[: last_brace + 1]), source_info


def main() -> int:
    manifest, source_info = load_source()
    checks = []
    for entry in manifest.get("files", []):
        relative = Path(entry["path"])
        candidate = (ROOT / relative).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
            in_scope = True
        except ValueError:
            in_scope = False
        exists = in_scope and candidate.is_file()
        actual_bytes = candidate.stat().st_size if exists else None
        actual_sha256 = sha256_bytes(candidate.read_bytes()) if exists else None
        checks.append(
            {
                "path": relative.as_posix(),
                "exists": exists,
                "inside_audit_root": in_scope,
                "bytes_recorded": entry.get("bytes"),
                "bytes_actual": actual_bytes,
                "sha256_recorded": entry.get("sha256"),
                "sha256_actual": actual_sha256,
                "valid": bool(
                    exists
                    and actual_bytes == entry.get("bytes")
                    and actual_sha256 == entry.get("sha256")
                ),
            }
        )

    all_valid = bool(checks) and all(row["valid"] for row in checks)
    repaired_bytes = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    REPAIRED.write_bytes(repaired_bytes)
    report = {
        "schema": "exp0003-broadband/hash-manifest-validation/v1",
        "source": source_info,
        "entries_checked": len(checks),
        "all_entries_valid": all_valid,
        "checks": checks,
        "repaired_sidecar": {
            "path": str(REPAIRED.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(repaired_bytes),
            "sha256": sha256_bytes(repaired_bytes),
            "note": "Valid JSON serialization of the salvaged source object; source file preserved unchanged.",
        },
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"source_valid={source_info['valid_json_directly']} "
        f"entries={len(checks)} all_valid={all_valid}"
    )
    return 0 if all_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
