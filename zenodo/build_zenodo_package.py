#!/usr/bin/env python3
"""Build the Zenodo archive for ScientificDiscoveryLab.

Byte-reproducible: running this twice on an unchanged tree produces an archive
with an identical SHA-256. That matters more than it usually would, because
Zenodo files are immutable after publication -- if the wrong archive is uploaded
the only remedy is a new version, and there is no way to check afterwards whether
what you uploaded is what you meant to upload. The digest printed here is the
value to compare against the file Zenodo reports.

Determinism requires:

  fixed mtimes      every entry is stamped with a constant, never the source
                    file's mtime, which would change on every copy
  sorted entries    a fixed traversal order, not filesystem order
  fixed compression level and no platform-dependent flags

Usage:
    python build_zenodo_package.py --tree <dir> --out <zip>
    python build_zenodo_package.py --tree <dir> --out <zip> --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

#: Fixed timestamp for every archive entry: 1980-01-01, the earliest a zip can
#: represent. Any constant works; using the real mtime would make the archive
#: unreproducible across copies.
FIXED_DATE = (1980, 1, 1, 0, 0, 0)

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".rar"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def collect(tree: Path) -> list[Path]:
    """Return every file to archive, in a deterministic order."""
    found: list[Path] = []
    for path in tree.rglob("*"):
        rel = path.relative_to(tree)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIX:
            continue
        if not path.is_file():
            continue
        found.append(path)
    # Sort on the POSIX form so Windows and Linux builds agree.
    return sorted(found, key=lambda p: p.relative_to(tree).as_posix())


def build(tree: Path, out: Path) -> tuple[int, int]:
    files = collect(tree)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(tree).as_posix()
            info = zipfile.ZipInfo(filename=rel, date_time=FIXED_DATE)
            # 0o644: read-only for everyone. The external_attr would otherwise
            # inherit the Windows filesystem and vary by machine.
            info.external_attr = (0o644 & 0xFFFF) << 16
            info.create_system = 3  # Unix, so the attr above is honoured
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())
    return len(files), out.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True, help="directory to archive")
    ap.add_argument("--out", required=True, help="output .zip path")
    ap.add_argument("--verify", action="store_true", help="build twice and compare digests")
    args = ap.parse_args()

    tree = Path(args.tree).resolve()
    out = Path(args.out).resolve()
    if not tree.is_dir():
        print(f"ERROR: {tree} is not a directory")
        return 1

    count, size = build(tree, out)
    digest = sha256_file(out)
    print(f"files   : {count}")
    print(f"bytes   : {size:,}")
    print(f"sha256  : {digest}")
    print(f"output  : {out}")

    if args.verify:
        second = out.with_suffix(".verify.zip")
        build(tree, second)
        second_digest = sha256_file(second)
        second.unlink()
        if second_digest == digest:
            print("\nARCHIVE VERIFIED: two independent builds are byte-identical")
            return 0
        print(f"\nARCHIVE NOT REPRODUCIBLE: {digest} != {second_digest}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
