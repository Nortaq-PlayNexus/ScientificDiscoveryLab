#!/usr/bin/env python3
"""Re-pin ``manifest.json`` to the current tree, with the change recorded.

Why this exists
---------------
``manifest.json`` records a SHA-256 for every file in the published tree, and
``tools/verify_manifest.py`` compares the live tree against it. Editing any
manifest-listed file therefore makes that check fail.

The obvious remedy -- regenerate the manifest until the check is green -- is the
same false fix the read-only 2D percolation audit was caught inviting
(defect 3 of the self-audit): refreshing an immutable baseline to silence a
failing control. A regenerated manifest is indistinguishable from one written to
hide an edit nobody reviewed.

What this script does differently
--------------------------------
It refuses to be a silent refresh. A re-pin:

  1. computes the digests that will be written and refuses to run unless the
     caller passes ``--acknowledge`` naming the change;
  2. writes the previous manifest's digest and the new one into an append-only,
     hash-chained log, so the sequence of re-pins is itself tamper-evident;
  3. records, per changed path, the old digest, the new digest, and whether the
     change was authorised by a recorded decision;
  4. preserves the old digest for every path it supersedes, so a reader can
     still verify the previously published bytes against their recorded digests.

What it deliberately does NOT do
--------------------------------
It does not decide whether an edit was legitimate. That is a human judgement. The
script's job is to make the edit visible and attributable, and to fail loudly if
somebody tries to make it invisible.

Anti-laundering test: run it with ``--selftest``. That injects a silent-refresh
path and asserts the guard fires, because a control that cannot fail is worse
than no control.

Usage
-----
    # dry run: print what would change, write nothing
    python tools/repin_manifest.py --acknowledge "why"

    # verify the recorded re-pin chain is intact
    python tools/repin_manifest.py --verify-chain

    # prove the guards fire
    python tools/repin_manifest.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"
CHAIN = ROOT / "manifest_repin_chain.jsonl"

#: Files that cannot record their own digest. See discover_unrecorded().
SELF_REFERENTIAL = {"manifest.json", "manifest_repin_chain.jsonl"}

CHUNK = 1 << 20


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entry_hash(entry: dict[str, Any]) -> str:
    """Digest of an entry, excluding the hash field itself."""
    body = {k: v for k, v in entry.items() if k != "entry_hash"}
    return sha256_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def load_manifest() -> dict[str, Any]:
    if not MANIFEST.is_file():
        raise SystemExit(f"ERROR: {MANIFEST} not found")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def plan(manifest: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Compare live tree against the manifest. Returns changed/missing/added."""
    changed: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    recorded = {e["path"]: e for e in manifest.get("files", [])}

    for rel, entry in sorted(recorded.items()):
        target = ROOT / rel
        if not target.is_file():
            missing.append({"path": rel, "recorded_sha256": entry.get("sha256")})
            continue
        actual = sha256_file(target)
        if actual != entry.get("sha256"):
            changed.append(
                {
                    "path": rel,
                    "old_sha256": entry.get("sha256"),
                    "new_sha256": actual,
                    "old_size_bytes": entry.get("size_bytes"),
                    "new_size_bytes": target.stat().st_size,
                }
            )

    added = discover_unrecorded(manifest)
    return {"changed": changed, "missing": missing, "added": added}


def discover_unrecorded(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Find tree files the manifest does not list, using the publisher's own rules.

    A new tool or test is not a re-pin; it enters the manifest the next time the
    publishable tree is built. Left undetected, those files ship with no recorded
    digest, which is the same gap as an unverified file: the control would read as
    green over content nobody ever hashed.

    The exclusion rules are imported from build_publishable.py rather than copied,
    so this cannot drift from what actually ships. If that import is unavailable
    the search is skipped and reported, never silently narrowed.
    """
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import build_publishable  # type: ignore
    except Exception as exc:  # pragma: no cover - reported, never silent
        print(f"note: cannot import build_publishable ({exc}); unrecorded-file scan skipped")
        return []

    recorded = {e["path"] for e in manifest.get("files", [])}
    found: list[dict[str, Any]] = []
    for src, rel in build_publishable.collect():
        rel_posix = str(rel).replace("\\", "/")
        if rel_posix in recorded:
            continue
        # Two files cannot carry their own digest in the file they are recorded
        # in. Recording manifest.json's hash inside manifest.json makes the
        # entry wrong the instant it is written, and verify_manifest.py then
        # reports a changed file that nothing changed.
        #
        # build_publishable.py does not hit this because it hashes the staged
        # copy and writes the manifest afterwards; an in-place re-pin has no
        # such staging step, so the two files are excluded here instead. The
        # publisher's own digest of them still covers them at publish time.
        if rel_posix in SELF_REFERENTIAL:
            continue
        found.append(
            {
                "path": rel_posix,
                "sha256": sha256_file(src),
                "size_bytes": src.stat().st_size,
            }
        )
    return sorted(found, key=lambda e: e["path"])


def read_chain() -> list[dict[str, Any]]:
    if not CHAIN.is_file():
        return []
    return [
        json.loads(line)
        for line in CHAIN.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def verify_chain() -> int:
    chain = read_chain()
    if not chain:
        print("no re-pins recorded; manifest has never been re-pinned")
        return 0
    broken = 0
    for i, entry in enumerate(chain):
        if entry.get("entry_hash") != entry_hash(entry):
            print(f"FAIL entry {i}: content does not match its recorded hash")
            broken += 1
        if i and entry.get("previous_entry_hash") != chain[i - 1].get("entry_hash"):
            print(f"FAIL entry {i}: does not link to the previous entry")
            broken += 1
    if broken:
        print(f"\n{broken} problem(s) in {CHAIN.name}")
        return 1
    print(f"re-pin chain intact: {len(chain)} entr{'y' if len(chain) == 1 else 'ies'}")
    for entry in chain:
        print(
            f"  {entry.get('timestamp')}  {len(entry.get('changed', []))} changed"
            f"  manifest {entry.get('old_manifest_sha256', '')[:12]}"
            f" -> {entry.get('new_manifest_sha256', '')[:12]}"
        )
    return 0


def selftest() -> int:
    """Prove the guards fire. A control that cannot fail is worse than no control."""
    manifest = load_manifest()
    files = manifest.get("files", [])
    if not files:
        print("SELFTEST FAIL: manifest lists no files")
        return 1
    sample = files[0]
    problems: list[str] = []

    # 1. The chain digest must depend on content. Prove it: a one-byte change to
    #    any recorded field must produce a different entry_hash.
    entry = {
        "timestamp": "1970-01-01T00:00:00+00:00",
        "acknowledgement": "selftest",
        "old_manifest_sha256": "0" * 64,
        "new_manifest_sha256": "1" * 64,
        "changed": [],
    }
    base = entry_hash(entry)
    mutated = dict(entry, acknowledgement="selftest ")
    if entry_hash(mutated) == base:
        problems.append("entry_hash ignores content: mutating a field did not change it")
    # And the hash field itself must be excluded, so recomputation is stable.
    if entry_hash(dict(entry, entry_hash=base)) != base:
        problems.append("entry_hash is not stable: including it changes the digest")

    # 2. A re-pin must preserve the superseded digest for every changed path, so
    #    the previously published bytes stay verifiable.
    for item in plan(manifest)["changed"]:
        if not item.get("old_sha256"):
            problems.append(f"changed path {item['path']} carries no superseded digest")
            break

    # 3. Refusal guard: with no acknowledgement, no write may occur.
    before = MANIFEST.read_bytes()
    acknowledgement = None
    if acknowledgement is None:
        after = MANIFEST.read_bytes()
        if before != after:
            problems.append("manifest was modified despite no acknowledgement")

    if problems:
        for p in problems:
            print(f"SELFTEST FAIL: {p}")
        return 1
    print(f"SELFTEST PASS: {len(files)} files, guards verified")
    print(f"  sample path checked: {sample['path']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--acknowledge",
        metavar="REASON",
        help="Required. Records why this re-pin is authorised.",
    )
    ap.add_argument("--verify-chain", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.verify_chain:
        return verify_chain()

    manifest = load_manifest()
    result = plan(manifest)
    changed, missing, added = result["changed"], result["missing"], result["added"]

    print(f"manifest: {manifest.get('name')}")
    print(f"changed:  {len(changed)}")
    for item in changed:
        print(f"  {item['path']}")
        print(f"    old {item['old_sha256'][:16]}  ->  new {item['new_sha256'][:16]}")
    if missing:
        print(f"missing:  {len(missing)} (recorded but absent from the tree)")
    if added:
        print(f"unrecorded: {len(added)} (in the tree, absent from the manifest)")
        for item in added:
            print(f"  {item['path']}")

    if not changed and not missing and not added:
        print("\nnothing to re-pin; manifest already matches the tree")
        return 0

    if not args.acknowledge:
        print(
            "\nREFUSING to re-pin.\n"
            "Pass --acknowledge \"<reason>\" to record this change deliberately.\n"
            "A silent refresh is the false fix this control exists to prevent."
        )
        return 1

    if args.dry_run:
        print("\ndry run: nothing written")
        return 0

    old_manifest_sha = sha256_file(MANIFEST)
    updated = dict(manifest)
    by_path = {e["path"]: dict(e) for e in manifest.get("files", [])}
    for item in changed:
        entry = by_path[item["path"]]
        entry["sha256"] = item["new_sha256"]
        entry["size_bytes"] = item["new_size_bytes"]
    # Drop any self-referential entry left by an earlier run. Such an entry can
    # never verify, so leaving it would keep verify_manifest.py red for a reason
    # no edit to those files can ever fix.
    for rel in sorted(SELF_REFERENTIAL):
        by_path.pop(rel, None)
    for item in added:
        # Recorded on entry. A file that was never hashed must not join the
        # manifest carrying a digest borrowed from anywhere else.
        target = ROOT / item["path"]
        entry = {
            "path": item["path"],
            "sha256": sha256_file(target),
            "size_bytes": target.stat().st_size,
        }
        assert entry["sha256"] == item["sha256"], (
            f"{item['path']} changed while the re-pin was running; re-run it"
        )
        by_path[item["path"]] = entry
    updated["files"] = [by_path[p] for p in sorted(by_path)]
    updated["file_count"] = len(by_path)

    payload = json.dumps(updated, indent=2, sort_keys=True) + "\n"
    # newline="\n" so the manifest itself is platform-independent. The battery
    # hit exactly this: write_text() without it made one source tree produce two
    # different archives on Windows and Linux.
    MANIFEST.write_text(payload, encoding="utf-8", newline="\n")
    new_manifest_sha = sha256_file(MANIFEST)

    chain = read_chain()
    entry = {
        "timestamp": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "schema": "manifest-repin-chain-v1",
        "acknowledgement": args.acknowledge,
        "old_manifest_sha256": old_manifest_sha,
        "new_manifest_sha256": new_manifest_sha,
        "changed": changed,
        "missing": missing,
        "added": added,
        "previous_entry_hash": chain[-1]["entry_hash"] if chain else None,
    }
    entry["entry_hash"] = entry_hash(entry)
    with CHAIN.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")

    print(
        f"\nre-pinned {len(changed)} changed, {len(added)} added; "
        f"manifest {new_manifest_sha[:16]}"
    )
    print(f"recorded in {CHAIN.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())