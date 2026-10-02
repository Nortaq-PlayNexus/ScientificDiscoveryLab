"""Immutable preregistration and hash-changed experiment logs.

A preregistration is created exactly once with exclusive filesystem semantics.
Its canonical SHA-256 is embedded in the document, so later edits are detected.
Post-freeze changes must be appended to a separate hash-chained change log.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PREREG_SCHEMA = "scientific-discovery-lab/prereg/v1"
CHANGE_SCHEMA = "scientific-discovery-lab/prereg-change/v1"


class PreregistrationExistsError(FileExistsError):
    """Raised when a caller attempts to freeze over an existing protocol."""


class PreregistrationIntegrityError(ValueError):
    """Raised when a frozen protocol or change-log chain is not intact."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PreregistrationIntegrityError(
                f"duplicate JSON key is forbidden: {key}"
            )
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise PreregistrationIntegrityError(
        f"non-finite JSON number is forbidden: {value}"
    )


def _canonical_json_bytes(value: Any) -> bytes:
    """Return stable UTF-8 JSON bytes for hashing and fail on non-finite data."""
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _verified_digest(document: dict[str, Any], field: str, path: Path) -> None:
    recorded = document.get(field)
    if not isinstance(recorded, str) or len(recorded) != 64:
        raise PreregistrationIntegrityError(
            f"{path}: missing or malformed {field}"
        )
    payload = dict(document)
    payload.pop(field, None)
    actual = _json_sha256(payload)
    if not hmac.compare_digest(recorded, actual):
        raise PreregistrationIntegrityError(
            f"{path}: {field} mismatch; the frozen document was modified"
        )


def freeze_config(
    *,
    experiment_id,
    hypothesis_id,
    question_id,
    seed,
    alpha=0.01,
    controls=(),
    analyses=(),
    params,
    out_path,
    note="",
):
    """Create a content-addressed preregistration without overwriting.

    The destination is opened with ``O_EXCL``. Calling this function again for
    an existing experiment fails closed; an amendment must use ``log_change()``
    or a new experiment identifier and preregistration path.
    """
    target = Path(out_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema": PREREG_SCHEMA,
        "experiment_id": experiment_id,
        "hypothesis_id": hypothesis_id,
        "question_id": question_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": seed,
        "alpha": alpha,
        "preregistered_controls": list(controls),
        "preregistered_analyses": list(analyses),
        "parameters": params,
        "note": note,
    }
    # Serialize before creating the file so NaN/invalid values cannot leave a
    # partial protocol behind.
    config = {**payload, "config_sha256": _json_sha256(payload)}
    serialized = (
        json.dumps(
            config,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    try:
        descriptor = os.open(
            target,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
    except FileExistsError as exc:
        raise PreregistrationExistsError(
            f"Refusing to overwrite frozen preregistration: {target}"
        ) from exc

    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            target.unlink()
        except FileNotFoundError:
            pass
        raise
    return config


def verify_frozen_config(out_path, *, expected=None) -> dict[str, Any]:
    """Load a preregistration, verify its hash, and optionally its payload.

    ``expected`` is a mapping of top-level fields that must exactly match the
    frozen document (for example ``experiment_id`` and ``parameters``).
    """
    target = Path(out_path).expanduser().resolve()
    try:
        document = json.loads(
            target.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except FileNotFoundError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError, PreregistrationIntegrityError) as exc:
        raise PreregistrationIntegrityError(
            f"{target}: preregistration is not strict UTF-8 JSON: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise PreregistrationIntegrityError(
            f"{target}: preregistration root must be an object"
        )
    if document.get("schema") != PREREG_SCHEMA:
        raise PreregistrationIntegrityError(
            f"{target}: unsupported preregistration schema"
        )
    _verified_digest(document, "config_sha256", target)
    if expected is not None:
        mismatches = {
            key: {"expected": value, "actual": document.get(key)}
            for key, value in expected.items()
            if document.get(key) != value
        }
        if mismatches:
            raise PreregistrationIntegrityError(
                f"{target}: frozen payload mismatch: {mismatches}"
            )
    return document


def verify_change_log(changelog_path) -> list[dict[str, Any]]:
    """Verify and return a complete append-only, SHA-256 hash chain."""
    target = Path(changelog_path).expanduser().resolve()
    if not target.exists():
        return []
    raw = target.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise PreregistrationIntegrityError(
            f"{target}: change log must end with a newline before append"
        )
    entries: list[dict[str, Any]] = []
    previous_hash: str | None = None
    with target.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise PreregistrationIntegrityError(
                    f"{target}:{line_number}: blank line in change log"
                )
            try:
                entry = json.loads(
                    line,
                    object_pairs_hook=_reject_duplicate_keys,
                    parse_constant=_reject_nonfinite,
                )
            except (json.JSONDecodeError, PreregistrationIntegrityError) as exc:
                raise PreregistrationIntegrityError(
                    f"{target}:{line_number}: invalid strict JSON change entry: {exc}"
                ) from exc
            if not isinstance(entry, dict) or entry.get("schema") != CHANGE_SCHEMA:
                raise PreregistrationIntegrityError(
                    f"{target}:{line_number}: unsupported change entry"
                )
            if entry.get("previous_entry_hash") != previous_hash:
                raise PreregistrationIntegrityError(
                    f"{target}:{line_number}: broken previous-entry hash"
                )
            _verified_digest(entry, "entry_hash", target)
            entries.append(entry)
            previous_hash = entry["entry_hash"]
    return entries


def log_change(
    *,
    experiment_id,
    what_changed,
    reason,
    changelog_path,
):
    """Append a verified hash-chain entry after the experiment started."""
    target = Path(changelog_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = verify_change_log(target)
    previous_hash = existing[-1]["entry_hash"] if existing else None
    payload = {
        "schema": CHANGE_SCHEMA,
        "experiment_id": experiment_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "change": what_changed,
        "reason": reason,
        "previous_entry_hash": previous_hash,
    }
    entry = {**payload, "entry_hash": _json_sha256(payload)}
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return entry