#!/usr/bin/env python3
"""Verify every published file against the recorded manifest.

Run from the repository root:

    python tools/verify_manifest.py

Exits 0 if every digest matches, 1 otherwise. Used by CI, and runnable by a
reader who wants to confirm the tree has not drifted from what was published.

Note: the manifest is itself an artifact, not self-verifying. It establishes
internal consistency of the tree against the recorded record. To establish that
the record itself is the audited one, use ``zenodo/verify_historical_integrity.py``,
which checks against digests frozen at audit time.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"
CHUNK = 1 << 20


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if not MANIFEST.is_file():
        print(f"ERROR: {MANIFEST} not found", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    if not files:
        print("ERROR: manifest lists no files", file=sys.stderr)
        return 1

    missing: list[str] = []
    changed: list[str] = []

    for entry in files:
        rel = entry["path"]
        target = ROOT / rel
        if not target.is_file():
            missing.append(rel)
            continue
        if sha256_file(target) != entry["sha256"]:
            changed.append(rel)

    print(f"manifest: {manifest.get('name')}")
    print(f"test suite at build time: {manifest.get('lab_test_suite', '?')}")
    print(f"files recorded: {len(files)}")
    print(f"verified:       {len(files) - len(missing) - len(changed)}")

    if missing:
        print(f"\nMISSING ({len(missing)}):")
        for rel in missing[:25]:
            print(f"  {rel}")
    if changed:
        print(f"\nCHANGED ({len(changed)}):")
        for rel in changed[:25]:
            print(f"  {rel}")

    if missing or changed:
        print("\nFAIL")
        return 1

    print("\nall digests match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())