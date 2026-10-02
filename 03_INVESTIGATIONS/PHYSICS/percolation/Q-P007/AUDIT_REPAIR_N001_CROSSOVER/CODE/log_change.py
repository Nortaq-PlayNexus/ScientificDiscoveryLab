"""Append a hash-chained entry to a preregistration change log.

The chain is: ``entry_hash = sha256(canonical_json(entry_without_entry_hash))``
and ``previous_entry_hash`` links to the prior entry's hash, so any edit to an
earlier entry is detectable.  Refuses to overwrite or reorder an existing log.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


def canonical(entry: dict[str, Any]) -> str:
    return json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def append(log_path: Path, entry: dict[str, Any]) -> dict[str, Any]:
    if not log_path.exists():
        raise SystemExit(f"refusing to create a new change log: {log_path}")
    lines = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise SystemExit(f"refusing to append to an empty change log: {log_path}")
    previous = json.loads(lines[-1])["entry_hash"]
    if entry.get("previous_entry_hash") not in (None, previous):
        raise SystemExit(
            f"chain break: log head is {previous}, entry claims {entry['previous_entry_hash']}"
        )
    body = {k: v for k, v in entry.items() if k != "entry_hash"}
    body["previous_entry_hash"] = previous
    body["entry_hash"] = hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(body) + "\n")
    return body


def genesis(log_path: Path, entry: dict[str, Any]) -> dict[str, Any]:
    """Write the first entry of a NEW chain. Refuses if the log already has one."""
    if log_path.exists():
        lines = [
            line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        if lines:
            raise SystemExit(
                f"refusing to write a genesis entry into a non-empty log: {log_path}"
            )
    body = {k: v for k, v in entry.items() if k != "entry_hash"}
    body["previous_entry_hash"] = None
    body["entry_hash"] = hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(body) + "\n")
    return body


if __name__ == "__main__":
    log = Path(sys.argv[1])
    payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    as_genesis = "--genesis" in sys.argv
    written = genesis(log, payload) if as_genesis else append(log, payload)
    print(json.dumps(written, indent=2, sort_keys=True, ensure_ascii=False))
