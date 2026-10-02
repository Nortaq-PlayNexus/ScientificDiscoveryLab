#!/usr/bin/env python3
"""Build the publishable copy of ScientificDiscoveryLab.

The laboratory is ~400 MB, of which ~327 MB is raw simulation output (.npz
lattices and sqlite3 databases). The publishable copy excludes those and records
which excluded files the test suite requires, so a reader knows exactly what is
missing and why rather than discovering it as a wall of collection errors.

Excluded by default (regenerable from the recorded seeds):
    *.npz    Monte Carlo lattice cell caches
    *.sqlite3 / *.db   raw simulation databases
    *.rar    superseded archive
    __pycache__ / .pytest_cache

Everything else ships: code, preregistrations, results JSON, reports, audit
trails, registries and governance documents.

Usage:
    python tools/build_publishable.py --dest <dir>          # stage
    python tools/build_publishable.py --dest <dir> --check  # verify
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
#: Recorded rather than hardcoded per-invocation so the published copy cannot
#: claim a test count it did not observe.
LAB_TEST_SUITE = "543 passed, 0 failed (2026-10-02, laboratory, full data present)"
#: Not produced by this script, so re-staging must not delete them.
#: ``.git`` is the destination's own repository; ``zenodo-deposit`` is the
#: curated v1.0.0 deposit extracted from the published repository, which the
#: laboratory tree does not contain and cannot regenerate.
PRESERVE = {".git", "zenodo-deposit"}
EXCLUDE_DIRS = {
    "__pycache__", ".pytest_cache", ".git", ".venv", "venv", "build", "dist",
    "node_modules", ".mypy_cache", ".ruff_cache",
}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".npz", ".sqlite3", ".db", ".rar", ".zip", ".whl"}

#: Credential files, excluded by NAME rather than by suffix or directory.
#:
#: `.gitignore` already lists these, and git honours .gitignore for tracked
#: content — but this script walks the filesystem directly and never consults
#: git, so an ignored file was still being collected. It reached the published
#: `manifest.json` as `zenodo/.zenodo_token` with its SHA-256 recorded.
#:
#: The token's contents never entered git. But publishing a manifest that
#: contains a digest of the maintainer's Zenodo credential is still wrong: it
#: discloses that a credential exists, lets anyone confirm a guessed token, and
#: produces a manifest entry that cannot verify on any checkout that lacks the
#: secret, which is every one of them.
#:
#: This is the same class of error as the CI gate that could not fail: a check
#: that appears to be working while quietly recording the wrong thing.
EXCLUDE_NAMES = {
    ".zenodo_token", ".env", "credentials.json", "id_rsa", "id_ed25519",
    ".netrc", ".npmrc", ".pypirc",
}
EXCLUDE_PATTERNS = ("*.token", "*.key", "*.pem", "*.p12", "*.pfx")


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def _excluded(src: Path, rel: Path) -> bool:
    """True if this path must never be published."""
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return True
    if src.suffix.lower() in EXCLUDE_SUFFIX:
        return True
    if src.name in EXCLUDE_NAMES:
        return True
    return any(fnmatch.fnmatch(src.name, pat) for pat in EXCLUDE_PATTERNS)


def collect() -> list[tuple[Path, Path]]:
    """Return (source, relative-destination) pairs to publish."""
    out = []
    for src in sorted(LAB.rglob("*")):
        rel = src.relative_to(LAB)
        if _excluded(src, rel):
            continue
        if not src.is_file():
            continue
        out.append((src, rel))
    return out


def excluded_inventory() -> list[tuple[str, int]]:
    rows = []
    for src in sorted(LAB.rglob("*")):
        rel = src.relative_to(LAB)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if src.suffix.lower() in EXCLUDE_SUFFIX and src.is_file():
            rows.append((str(rel).replace("\\", "/"), src.stat().st_size))
    return rows


def _clear(dest: Path, preserve: set[str]) -> None:
    """Empty `dest` except the entries named in `preserve`.

    A blunt rmtree is wrong here. The destination is the git working copy, and
    deleting `.git` on Windows also destroys the object store in a way that
    leaves the repository unusable rather than merely uninitialised. The curated
    Zenodo deposit under `zenodo-deposit/` is likewise not produced by the
    laboratory copy -- it was extracted from the published repository -- so
    re-staging must not silently delete it either.
    """
    if not dest.exists():
        dest.mkdir(parents=True)
        return
    for child in dest.iterdir():
        if child.name in preserve:
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def stage(dest: Path, preserve: set[str] | None = None) -> dict:
    dest = dest.resolve()
    preserve = preserve or set()
    _clear(dest, preserve)
    dest.mkdir(parents=True, exist_ok=True)

    files = collect()
    shipped = []
    for src, rel in files:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        shipped.append({"path": str(rel).replace("\\", "/"), "sha256": sha256_file(target)})

    excluded = excluded_inventory()
    manifest = {
        "schema": "sdl-publishable-manifest-v1",
        "name": "ScientificDiscoveryLab",
        "lab_test_suite": LAB_TEST_SUITE,
        "file_count": len(shipped),
        "total_bytes": sum((dest / f["path"]).stat().st_size for f in shipped),
        "excluded_suffixes": sorted(EXCLUDE_SUFFIX),
        "excluded_file_count": len(excluded),
        "excluded_total_bytes": sum(size for _, size in excluded),
        "excluded_note": (
            "Raw simulation output, regenerable from the seeds recorded in each "
            "preregistration. The read-only audit test suite REQUIRES some of these "
            "files; see tests_requiring_excluded_data.txt for the exact list. Those "
            "tests cannot run from this copy alone and will report a missing-"
            "historical-evidence error, which is correct fail-closed behaviour "
            "rather than a defect in this package."
        ),
        "files": shipped,
    }
    (dest / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def tests_needing_data(dest: Path) -> list[str]:
    """Which excluded files does the audit actually demand?"""
    scope = (
        dest
        / "03_INVESTIGATIONS/PHYSICS/percolation"
        / "AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/CONFIG/audit_scope.json"
    )
    needed: list[str] = []
    if not scope.is_file():
        return needed
    data = json.loads(scope.read_text(encoding="utf-8"))
    for entry in data.get("historical_evidence", []):
        candidate = dest / entry
        if not candidate.exists():
            # only report if it exists in the lab with an excluded suffix
            orig = LAB / entry
            if orig.is_file() and orig.suffix.lower() in EXCLUDE_SUFFIX:
                needed.append(entry)
    return needed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True, help="destination directory")
    ap.add_argument("--check", action="store_true", help="run the test suite in the copy")
    ap.add_argument(
        "--preserve",
        action="append",
        default=list(PRESERVE),
        metavar="NAME",
        help=(
            "top-level entry in the destination to keep (repeatable). "
            f"Defaults to: {', '.join(sorted(PRESERVE))}"
        ),
    )
    args = ap.parse_args()

    dest = Path(args.dest)
    print(f"staging {LAB} -> {dest}")
    m = stage(dest, set(args.preserve))
    print(f"  shipped   {m['file_count']} files, {m['total_bytes'] / 1e6:.1f} MB")
    print(f"  excluded  {m['excluded_file_count']} files, {m['excluded_total_bytes'] / 1e6:.1f} MB")

    # Fail loudly if a credential reached the published tree. This is a guard, not
    # a report: by the time a reader sees "all digests match" they have already
    # accepted the manifest, and a manifest listing a secret's digest is exactly
    # the kind of thing that gets waved through.
    leaks = [
        f["path"] for f in m["files"]
        if Path(f["path"]).name in EXCLUDE_NAMES
        or any(fnmatch.fnmatch(Path(f["path"]).name, pat) for pat in EXCLUDE_PATTERNS)
    ]
    if leaks:
        print("\nSECURITY: credential-shaped files reached the published tree:")
        for path in leaks:
            print(f"  {path}")
        print("Refusing to continue. Fix EXCLUDE_NAMES/EXCLUDE_PATTERNS.")
        return 1
    print("  secrets    none in the published set")

    needed = tests_needing_data(dest)
    if needed:
        listing = [
            "# Excluded data required by the test suite",
            "",
            "The following files are excluded from this publishable copy because they",
            "are raw simulation output, but the audit test suite reads them. Tests",
            "depending on them will fail CLOSED with `required historical evidence is",
            "missing` or `unable to open database file`. **That is correct",
            "behaviour, not a packaging defect.** The audit is designed to refuse to",
            "run without the exact bytes it was audited against; a copy that silently",
            "substituted regenerated data would defeat the control.",
            "",
            "Test counts in the published copy therefore differ from the laboratory:",
            f"laboratory {LAB_TEST_SUITE}; this copy expects the subset that does not",
            "read excluded data.",
            "",
            "To run the complete suite, restore these files from the laboratory, or",
            "regenerate them from the seeds in the corresponding preregistrations.",
            "",
            "| bytes | path |",
            "|---|---|",
        ]
        for entry in needed:
            listing.append(f"| {(LAB / entry).stat().st_size} | `{entry}` |")
        (dest / "tests_requiring_excluded_data.txt").write_text(
            "\n".join(listing) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"\n  {len(needed)} excluded file(s) required by the audit suite:")
        for e in needed:
            print(f"    {e}")

    if args.check:
        print("\nrunning test suite in the published copy...")
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=dest, capture_output=True, text=True, timeout=3600,
        )
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-1]
        print(f"  {tail}")
        print(f"  exit {proc.returncode}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())