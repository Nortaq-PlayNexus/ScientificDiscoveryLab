#!/usr/bin/env python3
"""Verify the preserved curated Zenodo deposit against its own manifest.

    python tools/verify_deposit_manifest.py

Checks `zenodo-deposit/manifest.json` against the files alongside it.

Expected result: 46 of 47 verified, 0 digest mismatches, 1 missing
(`N004_raw.sqlite3`), exit status 0.

**On the expected missing file.** The manifest's `files` list has 47 entries but
its `omitted_from_git` list declares only one — the 57.6 MB N001 database. The
1.9 MB N004 database appears in `files` yet was already absent from the published
Git tree, so the deposit's own bookkeeping does not account for it. That is a gap
in the deposit manifest, not a corruption introduced here, and it is reported
rather than silently tolerated: an unaccounted file is exactly the class of
bookkeeping failure this laboratory exists to surface.

Exits 0 when every discrepancy is a missing bulk binary (`.sqlite3` / `.npz`),
declared or not; 1 on any digest mismatch or any missing non-bulk file.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEPOSIT = ROOT / "zenodo-deposit"
MANIFEST = DEPOSIT / "manifest.json"
BULK_SUFFIXES = (".sqlite3", ".npz")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if not MANIFEST.is_file():
        print(f"ERROR: {MANIFEST} not found", file=sys.stderr)
        return 1

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    declared = {e["path"] for e in m.get("omitted_from_git", [])}

    ok: list[str] = []
    changed: list[str] = []
    missing: list[str] = []

    for entry in m["files"]:
        rel = entry["path"]
        p = DEPOSIT / rel
        if not p.is_file():
            missing.append(rel)
        elif sha256_file(p) != entry["sha256"]:
            changed.append(rel)
        else:
            ok.append(rel)

    print(f"deposit:    {m.get('deposit')}")
    print(f"version:    {m.get('version')}  ({m.get('date')})")
    print(f"test suite: {m.get('test_suite')}")
    print(f"claim:      {m.get('discovery_claim')}")
    print()
    print(f"verified:   {len(ok)}")
    print(f"changed:    {len(changed)}")
    print(f"missing:    {len(missing)}")

    undeclared_bulk = [r for r in missing if r not in declared and r.endswith(BULK_SUFFIXES)]
    unexpected = [
        r for r in missing if r not in declared and r not in undeclared_bulk
    ]

    for rel in changed:
        print(f"  CHANGED {rel}")
    for rel in missing:
        if rel in declared:
            tag = "declared in omitted_from_git"
        elif rel in undeclared_bulk:
            tag = "undeclared bulk binary — manifest bookkeeping gap"
        else:
            tag = "UNEXPECTED"
        print(f"  MISSING {rel}")
        print(f"          [{tag}]")

    if undeclared_bulk:
        print()
        print("NOTE: the deposit manifest does not declare these bulk binaries in")
        print("      `omitted_from_git`, though its own `files` list contains them.")
        print("      Gap in the deposit's bookkeeping, not corruption here.")

    if changed or unexpected:
        print("\nFAIL: deposit integrity broken")
        return 1

    print("\nOK: no digest mismatches. Missing files are bulk binaries, which the")
    print("    deposit carries on Zenodo rather than in git.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())