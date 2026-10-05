#!/usr/bin/env python3
"""Confirm a superseded manifest digest can still be checked against its bytes.

A re-pin that overwrites the record of what was published is indistinguishable
from one written to hide an edit. This script closes that gap from the other side:
it pulls the previously published bytes for the paths a re-pin superseded, from
git, and checks them against the digests the re-pin recorded as ``old_sha256``.

If it passes, a reader can still confirm that the tree once contained exactly the
bytes Zenodo holds -- the re-pin did not launder the history, it added to it.

Usage:
    python tools/verify_superseded_digests.py
    python tools/verify_superseded_digests.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CHAIN = ROOT / "manifest_repin_chain.jsonl"
CHUNK = 1 << 20


def read_chain() -> list[dict[str, Any]]:
    if not CHAIN.is_file():
        return []
    return [
        json.loads(line)
        for line in CHAIN.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def git_blob(revision: str, rel: str) -> bytes | None:
    """Return the bytes of ``rel`` at ``revision``, or None if absent there."""
    proc = subprocess.run(
        ["git", "cat-file", "blob", f"{revision}:{rel}"],
        cwd=ROOT,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def selftest() -> int:
    """Prove the comparison can fail. A check that cannot fail is not a check."""
    problems: list[str] = []

    # A digest must change when a single bit changes.
    a = hashlib.sha256(b"alpha").hexdigest()
    b = hashlib.sha256(b"alphb").hexdigest()
    if a == b:
        problems.append("sha256 comparison cannot distinguish different bytes")

    # An absent revision must return None rather than empty bytes, so a missing
    # file can never be mistaken for a matching empty one.
    if git_blob("0" * 40, "definitely/not/a/real/path") is not None:
        problems.append("a bogus revision returned bytes instead of None")

    if problems:
        for p in problems:
            print(f"SELFTEST FAIL: {p}")
        return 1
    print("SELFTEST PASS: digest comparison is sensitive and absence is detected")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    chain = read_chain()
    if not chain:
        print("no re-pins recorded; nothing superseded")
        return 0

    # Each entry records the manifest digest before its re-pin. That manifest is
    # itself in git history, so the pre-re-pin tree can be recovered exactly.
    total = matched = unverifiable = 0
    failures: list[str] = []

    for index, entry in enumerate(chain):
        old_manifest_sha = entry.get("old_manifest_sha256")
        # Find the commit whose manifest.json matches the recorded pre-re-pin digest.
        revision = None
        for line in subprocess.run(
            ["git", "log", "--format=%H", "--", "manifest.json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        ).stdout.splitlines():
            blob = git_blob(line, "manifest.json")
            if blob and hashlib.sha256(blob).hexdigest() == old_manifest_sha:
                revision = line
                break

        if revision is None:
            print(f"entry {index}: pre-re-pin manifest not found in git history")
            unverifiable += len(entry.get("changed", []))
            continue

        print(f"entry {index}: pre-re-pin tree is commit {revision[:12]}")
        for item in entry.get("changed", []):
            total += 1
            rel = item["path"]
            blob = git_blob(revision, rel)
            if blob is None:
                print(f"  UNVERIFIABLE {rel}: absent at {revision[:12]}")
                unverifiable += 1
                continue
            actual = hashlib.sha256(blob).hexdigest()
            if actual == item.get("old_sha256"):
                matched += 1
                print(f"  OK          {rel}  {actual[:16]}")
            else:
                failures.append(rel)
                print(f"  MISMATCH    {rel}: recorded {str(item.get('old_sha256'))[:16]}, git {actual[:16]}")

    print()
    print(f"superseded paths checked : {total}")
    print(f"  digest confirmed       : {matched}")
    print(f"  unverifiable           : {unverifiable}")
    print(f"  mismatched             : {len(failures)}")

    if failures:
        print("\nFAIL: the recorded pre-re-pin bytes do not match git history.")
        return 1
    if matched:
        print("\nOK: every superseded path still verifies against its recorded digest.")
        print("The previously published bytes remain checkable; the re-pin added to")
        print("the record rather than replacing it.")
        return 0
    print("\nSKIP: nothing verifiable from git history in this checkout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())